#!/usr/bin/env python3
"""Convenience launcher for SkillX round-0 task x schema runs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import shlex
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from skillx.docker_health import attempt_docker_recovery, probe_docker_health
from skillx.model_routing import resolve_benchmark_agent_name
from skillx.run_failure_utils import build_run_failure_payload

DEFAULT_TASK_SLICE = (
    ROOT
    / "experiments"
    / "skillx-skillsbench-001"
    / "results"
    / "official-task-results"
    / "sonnet45-round0-candidate-slice-v0.2.json"
)
DEFAULT_MATERIALIZED_ROOT = (
    ROOT
    / "experiments"
    / "skillx-skillsbench-001"
    / "results"
    / "outer-loop-round0"
    / "sonnet45-slice20-v0.2"
)
DEFAULT_OAUTH_FILE = Path.home() / ".claude" / "claude-code-oauth-token"
DEFAULT_REFINE_PROTOCOL_PATH = ROOT / "docs" / "protocols" / "skillx-refine-protocol-v0.1.md"
DEFAULT_BUNDLE_CONTRACT_PATH = ROOT / "docs" / "protocols" / "skillx-refine-bundle-contract-v0.1.md"
DEFAULT_AGENT = "claude-code"
DEFAULT_MODEL = "anthropic/claude-sonnet-4-5"
MIN_DOCKER_MEMORY_BYTES = 16_000_000_000


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_task_names(task_slice_path: Path) -> list[str]:
    payload = read_json(task_slice_path)
    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError(f"task slice missing tasks list: {task_slice_path}")
    task_names: list[str] = []
    for item in tasks:
        if not isinstance(item, dict) or not isinstance(item.get("task_name"), str):
            raise ValueError(f"invalid task slice entry in {task_slice_path}: {item!r}")
        task_names.append(item["task_name"])
    return task_names


def load_materialized_pairs(materialized_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_path = materialized_root / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing materialized manifest: {manifest_path}")
    manifest = read_json(manifest_path)

    pair_specs_jsonl = materialized_root / "pair_specs.jsonl"
    pair_specs: list[dict[str, Any]] = []
    if pair_specs_jsonl.exists():
        for raw_line in pair_specs_jsonl.read_text().splitlines():
            line = raw_line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"invalid pair spec line in {pair_specs_jsonl}: {raw_line!r}")
            pair_specs.append(payload)
    else:
        for pair_spec_path in sorted((materialized_root / "pairs").glob("*/pair_spec.json")):
            payload = read_json(pair_spec_path)
            if not isinstance(payload, dict):
                raise ValueError(f"invalid pair spec at {pair_spec_path}")
            pair_specs.append(payload)

    return manifest, pair_specs


def resolve_materialized_path(raw_path: str, *, materialized_root: Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path.resolve()
    return (materialized_root / path).resolve()


def validate_selected_pair_inputs(
    pair_specs: list[dict[str, Any]],
    *,
    materialized_root: Path,
) -> None:
    missing_by_pair: list[tuple[str, list[str]]] = []
    for pair_spec in pair_specs:
        pair_id = str(pair_spec.get("pair_id", "unknown-pair"))
        task_dir = resolve_materialized_path(str(pair_spec["skillsbench_task_dir"]), materialized_root=materialized_root)
        skillpack_dir = resolve_materialized_path(
            str(pair_spec["starting_skillpack_dir"]),
            materialized_root=materialized_root,
        )
        missing = [path for path in (task_dir, skillpack_dir) if not path.exists()]
        if missing:
            missing_by_pair.append((pair_id, [str(path) for path in missing]))

    if not missing_by_pair:
        return

    preview_lines = []
    for pair_id, missing in missing_by_pair[:3]:
        preview_lines.append(f"{pair_id}: {missing}")
    if len(missing_by_pair) > 3:
        preview_lines.append(f"... and {len(missing_by_pair) - 3} more pair(s)")
    raise FileNotFoundError(
        "materialized pair specs reference missing task inputs. "
        "Re-run scripts/rematerialize_round0_root.sh before launching.\n"
        + "\n".join(preview_lines)
    )


def select_pair_specs(
    pair_specs: list[dict[str, Any]],
    *,
    task_names: list[str],
    schema_ids: list[str],
    first_n: int | None,
    explicit_tasks: list[str] | None,
) -> list[dict[str, Any]]:
    if first_n is not None and explicit_tasks:
        raise ValueError("cannot combine first_n with explicit task selection")
    if first_n is not None:
        if first_n <= 0:
            raise ValueError("first_n must be positive")
        selected_task_names = task_names[:first_n]
    elif explicit_tasks:
        unknown = [task for task in explicit_tasks if task not in task_names]
        if unknown:
            raise KeyError(f"unknown task(s): {', '.join(unknown)}")
        explicit_set = set(explicit_tasks)
        selected_task_names = [task for task in task_names if task in explicit_set]
    else:
        selected_task_names = list(task_names)

    pair_index: dict[tuple[str, str], dict[str, Any]] = {}
    for pair_spec in pair_specs:
        task_name = pair_spec.get("task_name")
        schema_id = pair_spec.get("schema_id")
        if not isinstance(task_name, str) or not isinstance(schema_id, str):
            raise ValueError(f"invalid pair spec: {pair_spec!r}")
        pair_index[(task_name, schema_id)] = pair_spec

    selected: list[dict[str, Any]] = []
    for task_name in selected_task_names:
        for schema_id in schema_ids:
            key = (task_name, schema_id)
            if key not in pair_index:
                raise KeyError(f"missing pair spec for {task_name} x {schema_id}")
            selected.append(pair_index[key])
    return selected


def select_pair_specs_by_pair_ids(
    pair_specs: list[dict[str, Any]],
    *,
    pair_ids: list[str],
) -> list[dict[str, Any]]:
    pair_index: dict[str, dict[str, Any]] = {}
    for pair_spec in pair_specs:
        pair_id = pair_spec.get("pair_id")
        if isinstance(pair_id, str):
            pair_index[pair_id] = pair_spec

    missing = [pair_id for pair_id in pair_ids if pair_id not in pair_index]
    if missing:
        preview = ", ".join(missing[:5])
        if len(missing) > 5:
            preview += f", ... ({len(missing)} missing total)"
        raise KeyError(f"missing pair spec(s): {preview}")
    return [pair_index[pair_id] for pair_id in pair_ids]


def normalize_output_suffix(output_suffix: str | None) -> str | None:
    if output_suffix is None:
        return None
    normalized = output_suffix.strip().replace("/", "_")
    return normalized or None


def load_pair_ids_from_manifest(path: Path) -> list[str]:
    payload = read_json(path)
    pair_ids = payload.get("selected_pair_ids")
    if not isinstance(pair_ids, list) or not pair_ids:
        raise ValueError(f"pair manifest missing selected_pair_ids: {path}")
    if not all(isinstance(item, str) and item for item in pair_ids):
        raise ValueError(f"pair manifest contains invalid pair ids: {path}")
    return list(pair_ids)


def resolve_pair_dir(
    pair_spec: dict[str, Any],
    *,
    materialized_root: Path,
) -> Path:
    local_pair_dir = materialized_root / "pairs" / str(pair_spec["pair_id"])
    pair_dir = resolve_materialized_path(str(pair_spec["pair_dir"]), materialized_root=materialized_root)
    if local_pair_dir.exists():
        return local_pair_dir.resolve()
    return pair_dir


def resolve_pair_run_id_and_output_dir(
    pair_spec: dict[str, Any],
    *,
    materialized_root: Path,
    output_suffix: str | None,
) -> tuple[str, Path]:
    pair_dir = resolve_pair_dir(pair_spec, materialized_root=materialized_root)
    pair_id = str(pair_spec["pair_id"])
    normalized_suffix = normalize_output_suffix(output_suffix)
    if normalized_suffix is None:
        return pair_id, pair_dir / "refine_run"
    return f"{pair_id}__{normalized_suffix}", pair_dir / f"refine_run_{normalized_suffix}"


def build_launcher_log_dir(materialized_root: Path, *, output_suffix: str | None) -> Path:
    normalized_suffix = normalize_output_suffix(output_suffix)
    if normalized_suffix is None:
        normalized_suffix = datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%S%fZ")
    log_dir = materialized_root / "launcher_logs" / normalized_suffix
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def append_ndjson(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def write_launcher_failed_run_status(
    run_dir: Path,
    *,
    run_id: str | None,
    task_name: str,
    round_budget: int,
) -> None:
    body = "\n".join(
        [
            "- status: `failed`",
            f"- run_id: `{run_id or 'unknown-run'}`",
            f"- task: `{task_name}`",
            "- source_run_dir: `launcher-synthesized`",
            f"- round_budget: `{round_budget}`",
            "- orchestration_mode: `c4ar`",
            f"- updated_at: `{datetime.now(timezone.utc).isoformat()}`",
        ]
    )
    (run_dir / "RUN_STATUS.md").write_text(body + "\n")


def ensure_launcher_failure_artifacts(
    *,
    output_dir: str | None,
    run_id: str | None,
    task_name: str,
    schema_id: str,
    pair_id: str,
    round_budget: int,
    stage: str,
    error: str,
    traceback_text: str | None = None,
    returncode: int | None = None,
    command: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    if output_dir is None:
        return
    run_dir = Path(output_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    failure_path = run_dir / "run_failure.json"
    if not failure_path.exists():
        payload = build_run_failure_payload(
            error_type="LauncherPairFailure",
            error_message=error,
            traceback_text=traceback_text,
            failed_stage=stage,
            manual_intervention=bool(returncode is not None and returncode < 0),
            returncode=returncode,
            command=command,
            extra={
                "pair_id": pair_id,
                "task_name": task_name,
                "schema_id": schema_id,
                "run_id": run_id,
                "launcher_stage": stage,
                **(extra or {}),
            },
        )
        write_json(failure_path, payload)
    write_launcher_failed_run_status(
        run_dir,
        run_id=run_id,
        task_name=task_name,
        round_budget=round_budget,
    )


def build_launcher_summary(
    *,
    task_slice_path: Path,
    materialized_root: Path,
    selected_task_names: list[str],
    selected_pair_count: int,
    results: list[dict[str, Any]],
    aborted: bool = False,
    abort_reason: str | None = None,
) -> dict[str, Any]:
    succeeded_pairs = sum(1 for item in results if item.get("status") == "succeeded")
    failed_pairs = sum(1 for item in results if item.get("status") == "failed")
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task_slice_path": str(task_slice_path.resolve()),
        "materialized_root": str(materialized_root.resolve()),
        "selected_task_names": selected_task_names,
        "total_pairs": selected_pair_count,
        "completed_pairs": len(results),
        "succeeded_pairs": succeeded_pairs,
        "failed_pairs": failed_pairs,
        "aborted": aborted,
        "abort_reason": abort_reason,
        "results": results,
    }


def resolve_skillsbench_root(
    pair_spec: dict[str, Any],
    *,
    materialized_root: Path,
) -> Path:
    task_dir = resolve_materialized_path(str(pair_spec["skillsbench_task_dir"]), materialized_root=materialized_root)
    return task_dir.parents[1]


def write_docker_health_artifacts(
    output_dir: str | None,
    *,
    health_report: dict[str, Any],
    recovery_report: dict[str, Any] | None = None,
) -> None:
    if output_dir is None:
        return
    run_dir = Path(output_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "docker_health.json", health_report)
    if recovery_report is not None:
        write_json(run_dir / "docker_recovery.json", recovery_report)


def ensure_launcher_docker_health(
    *,
    pair_spec: dict[str, Any],
    materialized_root: Path,
    output_dir: str | None,
    run_id: str | None,
    round_budget: int,
    auto_recover: bool,
    events_path: Path,
    index: int,
    total_pairs: int,
) -> tuple[bool, dict[str, Any], dict[str, Any] | None]:
    pair_id = str(pair_spec.get("pair_id", f"pair-{index}"))
    task_name = str(pair_spec.get("task_name", "unknown-task"))
    schema_id = str(pair_spec.get("schema_id", "unknown-schema"))
    health_report = probe_docker_health(min_memory_bytes=MIN_DOCKER_MEMORY_BYTES)
    append_ndjson(
        events_path,
        {
            "event": "docker_health_probe",
            "index": index,
            "pair_id": pair_id,
            "task_name": task_name,
            "schema_id": schema_id,
            "healthy": health_report["healthy"],
            "category": health_report["category"],
            "message": health_report["message"],
            "observed_at": health_report["observed_at"],
        },
    )
    if health_report["healthy"]:
        return True, health_report, None

    recovery_report: dict[str, Any] | None = None
    if auto_recover:
        recovery_report = attempt_docker_recovery(
            skillsbench_root=resolve_skillsbench_root(pair_spec, materialized_root=materialized_root)
        )
        append_ndjson(
            events_path,
            {
                "event": "docker_recovery_attempted",
                "index": index,
                "pair_id": pair_id,
                "task_name": task_name,
                "schema_id": schema_id,
                "successful": recovery_report["successful"],
                "observed_at": recovery_report["observed_at"],
            },
        )
        health_report = probe_docker_health(min_memory_bytes=MIN_DOCKER_MEMORY_BYTES)
        append_ndjson(
            events_path,
            {
                "event": "docker_health_reprobe",
                "index": index,
                "pair_id": pair_id,
                "task_name": task_name,
                "schema_id": schema_id,
                "healthy": health_report["healthy"],
                "category": health_report["category"],
                "message": health_report["message"],
                "observed_at": health_report["observed_at"],
            },
        )
        if health_report["healthy"]:
            write_docker_health_artifacts(
                output_dir,
                health_report=health_report,
                recovery_report=recovery_report,
            )
            return True, health_report, recovery_report

    write_docker_health_artifacts(
        output_dir,
        health_report=health_report,
        recovery_report=recovery_report,
    )
    ensure_launcher_failure_artifacts(
        output_dir=output_dir,
        run_id=run_id,
        task_name=task_name,
        schema_id=schema_id,
        pair_id=pair_id,
        round_budget=round_budget,
        stage="docker_health_gate",
        error=health_report["message"],
        extra={
            "docker_health_category": health_report["category"],
            "docker_health_observed_at": health_report["observed_at"],
            "docker_auto_recover_attempted": auto_recover,
        },
    )
    return False, health_report, recovery_report


def build_refine_command(
    pair_spec: dict[str, Any],
    *,
    materialized_root: Path,
    oauth_file: Path | None,
    round_budget: int,
    agent: str | None,
    model: str,
    refine_protocol_path: Path,
    bundle_contract_path: Path,
    output_suffix: str | None,
    override_memory_mb: int | None = None,
    override_storage_mb: int | None = None,
) -> list[str]:
    pair_dir = resolve_pair_dir(pair_spec, materialized_root=materialized_root)
    task_name = str(pair_spec["task_name"])
    skillsbench_root = resolve_skillsbench_root(pair_spec, materialized_root=materialized_root)
    source_stub = pair_dir / "source_stub"
    source_stub.mkdir(parents=True, exist_ok=True)

    run_id, output_dir = resolve_pair_run_id_and_output_dir(
        pair_spec,
        materialized_root=materialized_root,
        output_suffix=output_suffix,
    )
    resolved_agent = resolve_benchmark_agent_name(agent, model)
    command = [
        "uv",
        "run",
        "python",
        str(ROOT / "scripts" / "run_skillx_refine_benchmark.py"),
        "--skillsbench-root",
        str(skillsbench_root),
        "--task",
        task_name,
        "--run-id",
        run_id,
        "--output-dir",
        str(output_dir),
        "--source-run-dir",
        str(source_stub),
        "--starting-skillpack-dir",
        str(resolve_materialized_path(str(pair_spec["starting_skillpack_dir"]), materialized_root=materialized_root)),
        "--starting-label",
        str(pair_spec.get("starting_label", "C1")),
        "--round-budget",
        str(round_budget),
        "--agent",
        resolved_agent,
        "--model",
        model,
        "--orchestration-mode",
        "c4ar",
        "--refine-protocol-path",
        str(refine_protocol_path.resolve()),
        "--bundle-contract-path",
        str(bundle_contract_path.resolve()),
    ]
    if override_memory_mb is not None:
        command.extend(["--override-memory-mb", str(override_memory_mb)])
    if override_storage_mb is not None:
        command.extend(["--override-storage-mb", str(override_storage_mb)])
    if resolved_agent == "claude-code":
        if oauth_file is None:
            raise ValueError("oauth_file is required for claude-code launches")
        command[command.index("--source-run-dir"):command.index("--source-run-dir")] = [
            "--oauth-file",
            str(oauth_file.resolve()),
        ]
    return command


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Launch selected SkillX round-0 task x schema refine runs."
    )
    parser.add_argument(
        "target",
        nargs="?",
        help="Integer N = run first N tasks from the fixed slice; otherwise treat as a task id.",
    )
    parser.add_argument("--task", action="append", help="Specific task id to run. Repeatable.")
    parser.add_argument(
        "--task-index",
        action="append",
        type=int,
        help="1-based task index from --list-tasks. Repeatable.",
    )
    parser.add_argument("--pair-id", action="append", help="Specific pair id to run. Repeatable.")
    parser.add_argument(
        "--pair-manifest",
        type=Path,
        help="JSON file containing selected_pair_ids for a frozen rerun batch.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print selected commands without executing them.")
    parser.add_argument("--list-tasks", action="store_true", help="Print the ordered task list and exit.")
    parser.add_argument("--task-slice", type=Path, default=DEFAULT_TASK_SLICE)
    parser.add_argument("--materialized-root", type=Path, default=DEFAULT_MATERIALIZED_ROOT)
    parser.add_argument("--oauth-file", type=Path, default=DEFAULT_OAUTH_FILE)
    parser.add_argument("--refine-protocol-path", type=Path, default=DEFAULT_REFINE_PROTOCOL_PATH)
    parser.add_argument("--bundle-contract-path", type=Path, default=DEFAULT_BUNDLE_CONTRACT_PATH)
    parser.add_argument("--round-budget", type=int, default=3)
    parser.add_argument("--agent")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--override-memory-mb", type=int)
    parser.add_argument("--override-storage-mb", type=int)
    parser.add_argument(
        "--no-docker-health-check",
        action="store_true",
        help="Disable Docker health probes before each pair launch.",
    )
    parser.add_argument(
        "--docker-auto-recover",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Attempt Docker recovery before aborting an unhealthy batch.",
    )
    parser.add_argument(
        "--output-suffix",
        help="Optional suffix for run-id/output-dir, e.g. smoke3 -> refine_run_smoke3.",
    )
    return parser


def _resolve_selection_args(
    args: argparse.Namespace,
    *,
    task_names: list[str],
) -> tuple[int | None, list[str] | None, list[str] | None]:
    explicit_tasks = list(args.task or [])
    explicit_pair_ids = list(args.pair_id or [])
    if args.pair_manifest is not None:
        if explicit_tasks or args.target or args.task_index:
            raise ValueError("cannot combine --pair-manifest with task-based selection")
        explicit_pair_ids.extend(load_pair_ids_from_manifest(args.pair_manifest))
    for index in args.task_index or []:
        if index <= 0 or index > len(task_names):
            raise IndexError(f"task index out of range: {index}")
        explicit_tasks.append(task_names[index - 1])
    first_n: int | None = None
    if args.target:
        if explicit_pair_ids:
            raise ValueError("cannot combine positional target with pair-based selection")
        if args.target.isdigit():
            if explicit_tasks:
                raise ValueError("cannot combine numeric target with explicit task selection")
            first_n = int(args.target)
        else:
            explicit_tasks.append(args.target)
    if explicit_pair_ids and (first_n is not None or explicit_tasks):
        raise ValueError("cannot combine pair-based selection with task-based selection")
    return first_n, explicit_tasks or None, explicit_pair_ids or None


def _print_task_list(task_names: list[str]) -> None:
    for index, task_name in enumerate(task_names, start=1):
        print(f"{index:>2}. {task_name}")


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    task_names = load_task_names(args.task_slice)
    if args.list_tasks:
        _print_task_list(task_names)
        return 0

    manifest, pair_specs = load_materialized_pairs(args.materialized_root)
    schema_ids = manifest.get("schema_ids")
    if not isinstance(schema_ids, list) or not all(isinstance(item, str) for item in schema_ids):
        raise ValueError(f"materialized manifest missing schema_ids: {args.materialized_root / 'manifest.json'}")

    first_n, explicit_tasks, explicit_pair_ids = _resolve_selection_args(args, task_names=task_names)
    if explicit_pair_ids:
        selected_pairs = select_pair_specs_by_pair_ids(pair_specs, pair_ids=explicit_pair_ids)
        selected_task_names = list(dict.fromkeys(str(pair["task_name"]) for pair in selected_pairs))
    else:
        selected_pairs = select_pair_specs(
            pair_specs,
            task_names=task_names,
            schema_ids=schema_ids,
            first_n=first_n,
            explicit_tasks=explicit_tasks,
        )
        selected_task_names = sorted({pair["task_name"] for pair in selected_pairs}, key=task_names.index)
    validate_selected_pair_inputs(
        selected_pairs,
        materialized_root=args.materialized_root,
    )

    print(f"Selected {len(selected_task_names)} task(s) -> {len(selected_pairs)} pair(s)")
    print("Tasks: " + ", ".join(selected_task_names))

    if args.dry_run:
        for pair_spec in selected_pairs:
            pair_id = str(pair_spec["pair_id"])
            command = build_refine_command(
                pair_spec,
                materialized_root=args.materialized_root,
                oauth_file=args.oauth_file,
                round_budget=args.round_budget,
                agent=args.agent,
                model=args.model,
                refine_protocol_path=args.refine_protocol_path,
                bundle_contract_path=args.bundle_contract_path,
                output_suffix=args.output_suffix,
                override_memory_mb=args.override_memory_mb,
                override_storage_mb=args.override_storage_mb,
            )
            print(f"\n# {pair_id}")
            print(shlex.join(command))
        return 0

    launcher_log_dir = build_launcher_log_dir(
        args.materialized_root,
        output_suffix=args.output_suffix,
    )
    summary_path = launcher_log_dir / "summary.json"
    events_path = launcher_log_dir / "events.ndjson"
    print(f"Launcher logs: {launcher_log_dir}")

    results: list[dict[str, Any]] = []
    aborted = False
    abort_reason: str | None = None

    for index, pair_spec in enumerate(selected_pairs, start=1):
        pair_id = str(pair_spec.get("pair_id", f"pair-{index}"))
        task_name = str(pair_spec.get("task_name", "unknown-task"))
        schema_id = str(pair_spec.get("schema_id", "unknown-schema"))
        run_id: str | None = None
        output_dir: str | None = None
        print(f"[{index}/{len(selected_pairs)}] {pair_id}")
        append_ndjson(
            events_path,
            {
                "event": "pair_started",
                "index": index,
                "pair_id": pair_id,
                "task_name": task_name,
                "schema_id": schema_id,
                "observed_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        try:
            run_id, resolved_output_dir = resolve_pair_run_id_and_output_dir(
                pair_spec,
                materialized_root=args.materialized_root,
                output_suffix=args.output_suffix,
            )
            output_dir = str(resolved_output_dir)
            command = build_refine_command(
                pair_spec,
                materialized_root=args.materialized_root,
                oauth_file=args.oauth_file,
                round_budget=args.round_budget,
                agent=args.agent,
                model=args.model,
                refine_protocol_path=args.refine_protocol_path,
                bundle_contract_path=args.bundle_contract_path,
                output_suffix=args.output_suffix,
                override_memory_mb=args.override_memory_mb,
                override_storage_mb=args.override_storage_mb,
            )
        except Exception as exc:
            ensure_launcher_failure_artifacts(
                output_dir=output_dir,
                run_id=run_id,
                task_name=task_name,
                schema_id=schema_id,
                pair_id=pair_id,
                round_budget=args.round_budget,
                stage="build_command",
                error=str(exc),
                traceback_text=traceback.format_exc(),
            )
            result = {
                "pair_id": pair_id,
                "task_name": task_name,
                "schema_id": schema_id,
                "status": "failed",
                "stage": "build_command",
                "run_id": run_id,
                "output_dir": output_dir,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
            results.append(result)
            append_ndjson(
                events_path,
                {
                    "event": "pair_failed",
                    "index": index,
                    "pair_id": pair_id,
                    "task_name": task_name,
                    "schema_id": schema_id,
                    "stage": "build_command",
                    "error": str(exc),
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            write_json(
                summary_path,
                build_launcher_summary(
                    task_slice_path=args.task_slice,
                    materialized_root=args.materialized_root,
                    selected_task_names=selected_task_names,
                    selected_pair_count=len(selected_pairs),
                    results=results,
                    aborted=aborted,
                    abort_reason=abort_reason,
                ),
            )
            print(f"  FAILED during command build: {exc}")
            continue

        if not args.no_docker_health_check:
            healthy, health_report, recovery_report = ensure_launcher_docker_health(
                pair_spec=pair_spec,
                materialized_root=args.materialized_root,
                output_dir=output_dir,
                run_id=run_id,
                round_budget=args.round_budget,
                auto_recover=args.docker_auto_recover,
                events_path=events_path,
                index=index,
                total_pairs=len(selected_pairs),
            )
            if not healthy:
                abort_reason = health_report["message"]
                aborted = True
                result = {
                    "pair_id": pair_id,
                    "task_name": task_name,
                    "schema_id": schema_id,
                    "status": "failed",
                    "stage": "docker_health_gate",
                    "run_id": run_id,
                    "output_dir": output_dir,
                    "error": health_report["message"],
                    "docker_health_category": health_report["category"],
                    "docker_recovery_attempted": bool(recovery_report),
                }
                results.append(result)
                append_ndjson(
                    events_path,
                    {
                        "event": "pair_failed",
                        "index": index,
                        "pair_id": pair_id,
                        "task_name": task_name,
                        "schema_id": schema_id,
                        "stage": "docker_health_gate",
                        "error": health_report["message"],
                        "observed_at": datetime.now(timezone.utc).isoformat(),
                    },
                )
                write_json(
                    summary_path,
                    build_launcher_summary(
                        task_slice_path=args.task_slice,
                        materialized_root=args.materialized_root,
                        selected_task_names=selected_task_names,
                        selected_pair_count=len(selected_pairs),
                        results=results,
                        aborted=aborted,
                        abort_reason=abort_reason,
                    ),
                )
                print(f"  ABORTING: Docker unhealthy before launch: {health_report['message']}")
                break
            if recovery_report is not None:
                print("  Docker recovered after cleanup")

        try:
            completed = subprocess.run(command, cwd=str(ROOT), check=False)
            returncode = int(completed.returncode)
            if returncode == 0:
                result = {
                    "pair_id": pair_id,
                    "task_name": task_name,
                    "schema_id": schema_id,
                    "status": "succeeded",
                    "stage": "run",
                    "run_id": run_id,
                    "output_dir": output_dir,
                    "returncode": returncode,
                    "command": command,
                }
                results.append(result)
                append_ndjson(
                    events_path,
                    {
                        "event": "pair_succeeded",
                        "index": index,
                        "pair_id": pair_id,
                        "task_name": task_name,
                        "schema_id": schema_id,
                        "returncode": returncode,
                        "observed_at": datetime.now(timezone.utc).isoformat(),
                    },
                )
                print("  OK")
            else:
                ensure_launcher_failure_artifacts(
                    output_dir=output_dir,
                    run_id=run_id,
                    task_name=task_name,
                    schema_id=schema_id,
                    pair_id=pair_id,
                    round_budget=args.round_budget,
                    stage="run",
                    error=f"subprocess exited with code {returncode}",
                    returncode=returncode,
                    command=command,
                )
                result = {
                    "pair_id": pair_id,
                    "task_name": task_name,
                    "schema_id": schema_id,
                    "status": "failed",
                    "stage": "run",
                    "run_id": run_id,
                    "output_dir": output_dir,
                    "returncode": returncode,
                    "command": command,
                    "error": f"subprocess exited with code {returncode}",
                }
                results.append(result)
                append_ndjson(
                    events_path,
                    {
                        "event": "pair_failed",
                        "index": index,
                        "pair_id": pair_id,
                        "task_name": task_name,
                        "schema_id": schema_id,
                        "stage": "run",
                        "returncode": returncode,
                        "observed_at": datetime.now(timezone.utc).isoformat(),
                    },
                )
                print(f"  FAILED with exit code {returncode}")
        except subprocess.CalledProcessError as exc:
            ensure_launcher_failure_artifacts(
                output_dir=output_dir,
                run_id=run_id,
                task_name=task_name,
                schema_id=schema_id,
                pair_id=pair_id,
                round_budget=args.round_budget,
                stage="run",
                error=str(exc),
                traceback_text=traceback.format_exc(),
                returncode=int(exc.returncode),
                command=command,
            )
            result = {
                "pair_id": pair_id,
                "task_name": task_name,
                "schema_id": schema_id,
                "status": "failed",
                "stage": "run",
                "run_id": run_id,
                "output_dir": output_dir,
                "command": command,
                "returncode": int(exc.returncode),
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
            results.append(result)
            append_ndjson(
                events_path,
                {
                    "event": "pair_failed",
                    "index": index,
                    "pair_id": pair_id,
                    "task_name": task_name,
                    "schema_id": schema_id,
                    "stage": "run",
                    "returncode": int(exc.returncode),
                    "error": str(exc),
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            print(f"  FAILED with exit code {exc.returncode}")
        except Exception as exc:
            ensure_launcher_failure_artifacts(
                output_dir=output_dir,
                run_id=run_id,
                task_name=task_name,
                schema_id=schema_id,
                pair_id=pair_id,
                round_budget=args.round_budget,
                stage="run_exception",
                error=str(exc),
                traceback_text=traceback.format_exc(),
                command=command,
            )
            result = {
                "pair_id": pair_id,
                "task_name": task_name,
                "schema_id": schema_id,
                "status": "failed",
                "stage": "run_exception",
                "run_id": run_id,
                "output_dir": output_dir,
                "command": command,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
            results.append(result)
            append_ndjson(
                events_path,
                {
                    "event": "pair_failed",
                    "index": index,
                    "pair_id": pair_id,
                    "task_name": task_name,
                    "schema_id": schema_id,
                    "stage": "run_exception",
                    "error": str(exc),
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            print(f"  FAILED with launcher exception: {exc}")

        write_json(
            summary_path,
            build_launcher_summary(
                task_slice_path=args.task_slice,
                materialized_root=args.materialized_root,
                selected_task_names=selected_task_names,
                selected_pair_count=len(selected_pairs),
                results=results,
                aborted=aborted,
                abort_reason=abort_reason,
            ),
        )

    failed_pairs = sum(1 for item in results if item.get("status") == "failed")
    succeeded_pairs = sum(1 for item in results if item.get("status") == "succeeded")
    print(
        "Finished round0 launch:"
        f" succeeded={succeeded_pairs}"
        f" failed={failed_pairs}"
        f" summary={summary_path}"
    )
    return 1 if failed_pairs else 0


if __name__ == "__main__":
    raise SystemExit(main())
