#!/usr/bin/env python3
"""Build frozen task/pair selection artifacts for round0 rerun recovery."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GLOBAL_STATUS_PATH = (
    ROOT
    / "experiments"
    / "skillx-skillsbench-001"
    / "results"
    / "outer-loop-round0"
    / "reports"
    / "global-round0-status"
    / "global_pair_status.json"
)
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "experiments"
    / "skillx-skillsbench-001"
    / "results"
    / "outer-loop-round0"
    / "reports"
    / "rerun-recovery"
)
DEFAULT_TASK_SLICE_OUT = DEFAULT_OUTPUT_DIR / "round0-rerun-recovery-v0.1.task-slice.json"
DEFAULT_PAIR_MANIFEST_OUT = DEFAULT_OUTPUT_DIR / "round0-rerun-recovery-v0.1.pair-manifest.json"
DEFAULT_SUMMARY_OUT = DEFAULT_OUTPUT_DIR / "round0-rerun-recovery-v0.1.md"
DEFAULT_EXCLUDED_PAIR_IDS = ["energy-ac-optimal-power-flow__artifact-generation"]
SETUP_FUZZING_TASK = "setup-fuzzing-py"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_global_pair_rows(path: Path) -> list[dict[str, Any]]:
    payload = read_json(path)
    rows = payload.get("pairs")
    if not isinstance(rows, list):
        raise ValueError(f"global status missing pairs list: {path}")
    valid_rows: list[dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("pair_id"), str):
            valid_rows.append(row)
    return valid_rows


def select_default_rerun_rows(
    rows: list[dict[str, Any]],
    *,
    excluded_pair_ids: set[str],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for row in rows:
        pair_id = str(row["pair_id"])
        if pair_id in excluded_pair_ids:
            continue
        latest_status = str(row.get("latest_status") or "")
        task_name = str(row.get("task_name") or "")
        rerun_reason = str(row.get("rerun_reason") or "")

        if latest_status == "docker_incident":
            selected.append(row)
            continue

        if task_name == SETUP_FUZZING_TASK and rerun_reason in {"missing_task_inputs", "other_failure"}:
            selected.append(row)

    return selected


def build_task_slice(selected_rows: list[dict[str, Any]]) -> dict[str, Any]:
    seen: set[str] = set()
    tasks: list[dict[str, Any]] = []
    for row in selected_rows:
        task_name = str(row["task_name"])
        if task_name in seen:
            continue
        seen.add(task_name)
        tasks.append({"task_name": task_name})
    return {"tasks": tasks}


def build_pair_manifest(
    *,
    global_status_path: Path,
    task_slice_out: Path,
    selected_rows: list[dict[str, Any]],
    excluded_pair_ids: set[str],
) -> dict[str, Any]:
    selected_pair_ids = [str(row["pair_id"]) for row in selected_rows]
    selected_task_names = [task["task_name"] for task in build_task_slice(selected_rows)["tasks"]]
    reason_counts = Counter(str(row.get("rerun_reason") or "unknown") for row in selected_rows)
    status_counts = Counter(str(row.get("latest_status") or "unknown") for row in selected_rows)
    return {
        "generated_at": _utc_now(),
        "name": "round0-rerun-recovery-v0.1",
        "selection_mode": "pair_manifest",
        "source_status_report": display_path(global_status_path),
        "task_slice_path": display_path(task_slice_out),
        "selected_pair_ids": selected_pair_ids,
        "selected_task_names": selected_task_names,
        "pair_count_total": len(selected_pair_ids),
        "task_count_total": len(selected_task_names),
        "counts_by_latest_status": dict(status_counts),
        "counts_by_rerun_reason": dict(reason_counts),
        "excluded_pair_ids": sorted(excluded_pair_ids),
        "notes": [
            "Includes all latest docker_incident pairs.",
            "Includes all setup-fuzzing-py schemas blocked by the old verifier contract assumption.",
            "Excludes energy-ac-optimal-power-flow__artifact-generation by default.",
        ],
    }


def build_summary_markdown(
    *,
    global_status_path: Path,
    selected_rows: list[dict[str, Any]],
    excluded_pair_ids: set[str],
    task_slice_out: Path,
    pair_manifest_out: Path,
) -> str:
    reason_counts = Counter(str(row.get("rerun_reason") or "unknown") for row in selected_rows)
    selected_pair_ids = [str(row["pair_id"]) for row in selected_rows]
    selected_tasks = [task["task_name"] for task in build_task_slice(selected_rows)["tasks"]]
    lines = [
        "# Round0 Rerun Recovery Manifest",
        "",
        f"- generated_at: `{_utc_now()}`",
        f"- source_status_report: `{display_path(global_status_path)}`",
        f"- task_slice_path: `{display_path(task_slice_out)}`",
        f"- pair_manifest_path: `{display_path(pair_manifest_out)}`",
        f"- selected_task_count: `{len(selected_tasks)}`",
        f"- selected_pair_count: `{len(selected_pair_ids)}`",
        f"- excluded_pair_ids: `{', '.join(sorted(excluded_pair_ids))}`",
        "",
        "## Counts By Rerun Reason",
        "",
    ]
    for reason, count in sorted(reason_counts.items()):
        lines.append(f"- `{reason}`: `{count}`")
    lines.extend(
        [
            "",
            "## Selected Tasks",
            "",
        ]
    )
    lines.extend(f"- `{task_name}`" for task_name in selected_tasks)
    lines.extend(
        [
            "",
            "## First 20 Selected Pairs",
            "",
        ]
    )
    lines.extend(f"- `{pair_id}`" for pair_id in selected_pair_ids[:20])
    if len(selected_pair_ids) > 20:
        lines.append(f"- ... and `{len(selected_pair_ids) - 20}` more")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build frozen round0 rerun recovery artifacts.")
    parser.add_argument("--global-status", type=Path, default=DEFAULT_GLOBAL_STATUS_PATH)
    parser.add_argument("--task-slice-out", type=Path, default=DEFAULT_TASK_SLICE_OUT)
    parser.add_argument("--pair-manifest-out", type=Path, default=DEFAULT_PAIR_MANIFEST_OUT)
    parser.add_argument("--summary-out", type=Path, default=DEFAULT_SUMMARY_OUT)
    parser.add_argument(
        "--exclude-pair-id",
        action="append",
        default=[],
        help="Pair id to exclude from the default rerun selection. Repeatable.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    excluded_pair_ids = set(DEFAULT_EXCLUDED_PAIR_IDS)
    excluded_pair_ids.update(str(item) for item in (args.exclude_pair_id or []))

    rows = load_global_pair_rows(args.global_status)
    selected_rows = select_default_rerun_rows(rows, excluded_pair_ids=excluded_pair_ids)
    task_slice = build_task_slice(selected_rows)
    pair_manifest = build_pair_manifest(
        global_status_path=args.global_status,
        task_slice_out=args.task_slice_out,
        selected_rows=selected_rows,
        excluded_pair_ids=excluded_pair_ids,
    )

    write_json(args.task_slice_out, task_slice)
    write_json(args.pair_manifest_out, pair_manifest)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(
        build_summary_markdown(
            global_status_path=args.global_status,
            selected_rows=selected_rows,
            excluded_pair_ids=excluded_pair_ids,
            task_slice_out=args.task_slice_out,
            pair_manifest_out=args.pair_manifest_out,
        )
    )

    print(f"Selected {pair_manifest['task_count_total']} task(s) -> {pair_manifest['pair_count_total']} pair(s)")
    print(f"Task slice: {args.task_slice_out}")
    print(f"Pair manifest: {args.pair_manifest_out}")
    print(f"Summary: {args.summary_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
