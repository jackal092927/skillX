#!/usr/bin/env python3
"""Build a global SkillX round-0 pair status summary across all exported run reports."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROUND0_ROOT = (
    ROOT
    / "experiments"
    / "skillx-skillsbench-001"
    / "results"
    / "outer-loop-round0"
)
DEFAULT_OUTPUT_DIR = DEFAULT_ROUND0_ROOT / "reports" / "global-round0-status"
DEFAULT_SCHEMA_IDS = [
    "artifact-generation",
    "analytic-pipeline",
    "engineering-composition",
    "retrieval-heavy-synthesis",
    "environment-control",
    "methodology-guardrail",
    "orchestration-delegation",
]
STATUS_CODE = {
    "completed": "C",
    "docker_incident": "D",
    "failed_other": "F",
    "unrun": "-",
}
COMPLETED_RUN_STATUSES = {
    "completed",
    "completed_with_runtime_failures",
    "skipped_baseline_perfect",
}


def discover_default_skillsbench_root() -> Path:
    candidates = [ROOT.parent / "skillsbench-src"]
    candidates.extend(parent / "skillsbench-src" for parent in ROOT.parents)
    for candidate in candidates:
        if (candidate / "tasks").exists():
            return candidate
    return ROOT.parent / "skillsbench-src"


DEFAULT_SKILLSBENCH_ROOT = discover_default_skillsbench_root()


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def discover_task_ids(skillsbench_root: Path) -> list[str]:
    tasks_root = skillsbench_root / "tasks"
    if not tasks_root.exists():
        raise FileNotFoundError(f"missing tasks root: {tasks_root}")
    return sorted(path.name for path in tasks_root.iterdir() if path.is_dir())


def discover_schema_ids(round0_root: Path) -> list[str]:
    discovered: list[str] = []
    for manifest_path in sorted(round0_root.glob("*/manifest.json")):
        payload = read_json(manifest_path)
        schema_ids = payload.get("schema_ids")
        if not isinstance(schema_ids, list):
            continue
        for schema_id in schema_ids:
            if isinstance(schema_id, str) and schema_id not in discovered:
                discovered.append(schema_id)
    if discovered:
        return [schema_id for schema_id in DEFAULT_SCHEMA_IDS if schema_id in discovered] + [
            schema_id for schema_id in discovered if schema_id not in DEFAULT_SCHEMA_IDS
        ]
    return list(DEFAULT_SCHEMA_IDS)


def discover_run_report_paths(round0_root: Path) -> list[Path]:
    return sorted(round0_root.glob("**/reports/*/run_report.json"))


def classify_attempt_status(row: dict[str, Any]) -> str:
    launcher = row.get("launcher") or {}
    run = row.get("run") or {}
    failure = row.get("failure") or {}
    summary = str(failure.get("summary") or failure.get("error_message") or "")
    selected = row.get("selected") or {}
    best_observed = row.get("best_observed") or {}
    has_score = isinstance(selected.get("score_pct"), (int, float)) or isinstance(
        best_observed.get("score_pct"),
        (int, float),
    )
    if launcher.get("status") == "succeeded" and (
        run.get("status") in COMPLETED_RUN_STATUSES or has_score
    ):
        return "completed"
    if "Docker memory too low: 0 bytes" in summary:
        return "docker_incident"
    return "failed_other"


def classify_rerun_reason(status: str, latest_attempt: dict[str, Any] | None) -> str:
    if status == "completed":
        return ""
    if status == "unrun":
        return "unrun"
    if latest_attempt is None:
        return "unknown"
    summary = str(latest_attempt.get("failure_summary") or "")
    if status == "docker_incident":
        return "docker_incident"
    if "missing task inputs" in summary:
        return "missing_task_inputs"
    return "other_failure"


def summarize_attempt(row: dict[str, Any], *, run_label: str, report_path: Path) -> dict[str, Any]:
    launcher = row.get("launcher") or {}
    run = row.get("run") or {}
    failure = row.get("failure") or {}
    selected = row.get("selected") or {}
    best_observed = row.get("best_observed") or {}
    status = classify_attempt_status(row)
    finished_at = str(launcher.get("finished_at") or run.get("updated_at") or "")
    started_at = str(launcher.get("started_at") or "")
    return {
        "pair_id": str(row["pair_id"]),
        "task_name": str(row["task_name"]),
        "schema_id": str(row["schema_id"]),
        "run_label": run_label,
        "report_path": display_path(report_path),
        "finished_at": finished_at,
        "started_at": started_at,
        "status": status,
        "launcher_status": launcher.get("status"),
        "launcher_stage": launcher.get("stage"),
        "launcher_returncode": launcher.get("returncode"),
        "run_status": run.get("status"),
        "failure_stage": failure.get("failed_stage"),
        "failure_type": failure.get("error_type"),
        "failure_summary": failure.get("summary") or failure.get("error_message") or "",
        "selected_round_index": selected.get("round_index"),
        "selected_score_pct": selected.get("score_pct"),
        "best_observed_round_index": best_observed.get("round_index"),
        "best_observed_score_pct": best_observed.get("score_pct"),
        "early_stop": bool(row.get("early_stop")),
        "timeout_detected": bool(row.get("timeout_detected")),
        "has_intermediate_exceptions": bool(row.get("has_intermediate_exceptions")),
        "output_dir": run.get("output_dir"),
    }


def sort_attempt_key(attempt: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(attempt.get("finished_at") or ""),
        str(attempt.get("started_at") or ""),
        str(attempt.get("run_label") or ""),
    )


def build_pair_rows(
    *,
    task_ids: list[str],
    schema_ids: list[str],
    attempts_by_pair: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task_id in task_ids:
        for schema_id in schema_ids:
            pair_id = f"{task_id}__{schema_id}"
            attempts = sorted(attempts_by_pair.get(pair_id, []), key=sort_attempt_key)
            latest = attempts[-1] if attempts else None
            latest_status = latest["status"] if latest is not None else "unrun"
            rerun_reason = classify_rerun_reason(latest_status, latest)
            row = {
                "pair_id": pair_id,
                "task_name": task_id,
                "schema_id": schema_id,
                "latest_status": latest_status,
                "latest_status_code": STATUS_CODE[latest_status],
                "attempt_count": len(attempts),
                "successful_attempt_count": sum(1 for attempt in attempts if attempt["status"] == "completed"),
                "docker_incident_attempt_count": sum(
                    1 for attempt in attempts if attempt["status"] == "docker_incident"
                ),
                "other_failure_attempt_count": sum(
                    1 for attempt in attempts if attempt["status"] == "failed_other"
                ),
                "needs_rerun": latest_status != "completed",
                "rerun_reason": rerun_reason,
                "latest_run_label": latest["run_label"] if latest else "",
                "latest_started_at": latest["started_at"] if latest else "",
                "latest_finished_at": latest["finished_at"] if latest else "",
                "latest_launcher_status": latest["launcher_status"] if latest else "",
                "latest_launcher_stage": latest["launcher_stage"] if latest else "",
                "latest_launcher_returncode": latest["launcher_returncode"] if latest else "",
                "latest_run_status": latest["run_status"] if latest else "",
                "latest_failure_stage": latest["failure_stage"] if latest else "",
                "latest_failure_type": latest["failure_type"] if latest else "",
                "latest_failure_summary": latest["failure_summary"] if latest else "",
                "latest_selected_round_index": latest["selected_round_index"] if latest else "",
                "latest_selected_score_pct": latest["selected_score_pct"] if latest else "",
                "latest_best_observed_round_index": latest["best_observed_round_index"] if latest else "",
                "latest_best_observed_score_pct": latest["best_observed_score_pct"] if latest else "",
                "latest_early_stop": latest["early_stop"] if latest else False,
                "latest_timeout_detected": latest["timeout_detected"] if latest else False,
                "latest_has_intermediate_exceptions": (
                    latest["has_intermediate_exceptions"] if latest else False
                ),
                "latest_output_dir": latest["output_dir"] if latest else "",
                "attempt_run_labels": ";".join(attempt["run_label"] for attempt in attempts),
            }
            rows.append(row)
    return rows


def summarize_reports(report_paths: list[Path]) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    report_rows: list[dict[str, Any]] = []
    attempts_by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for report_path in report_paths:
        payload = read_json(report_path)
        report_rows.append(
            {
                "run_label": payload["run_label"],
                "report_path": display_path(report_path),
                "materialized_root": payload.get("materialized_root"),
                "pair_count_total": payload.get("pair_count_total"),
                "pair_count_completed": payload.get("pair_count_completed"),
                "pair_count_succeeded": payload.get("pair_count_succeeded"),
                "pair_count_failed": payload.get("pair_count_failed"),
                "started_at": payload.get("started_at"),
                "finished_at": payload.get("finished_at"),
                "duration_sec": payload.get("duration_sec"),
            }
        )
        for pair_row in payload.get("pair_results", []):
            if not isinstance(pair_row, dict):
                continue
            attempt = summarize_attempt(
                pair_row,
                run_label=str(payload["run_label"]),
                report_path=report_path,
            )
            attempts_by_pair[attempt["pair_id"]].append(attempt)
    return report_rows, attempts_by_pair


def build_status_counts(pair_rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(row["latest_status"] for row in pair_rows)
    return {
        "completed": counts["completed"],
        "docker_incident": counts["docker_incident"],
        "failed_other": counts["failed_other"],
        "unrun": counts["unrun"],
    }


def build_task_status_rows(pair_rows: list[dict[str, Any]], schema_ids: list[str]) -> list[dict[str, Any]]:
    rows_by_task: dict[str, dict[str, Any]] = {}
    for pair_row in pair_rows:
        task_row = rows_by_task.setdefault(
            pair_row["task_name"],
            {
                "task_name": pair_row["task_name"],
            },
        )
        code = pair_row["latest_status_code"]
        attempts = pair_row["attempt_count"]
        task_row[pair_row["schema_id"]] = f"{code}{attempts}"
    for task_row in rows_by_task.values():
        for schema_id in schema_ids:
            task_row.setdefault(schema_id, "-0")
    return [rows_by_task[task_name] for task_name in sorted(rows_by_task)]


def render_markdown(
    *,
    generated_at: str,
    skillsbench_root: Path,
    report_rows: list[dict[str, Any]],
    pair_rows: list[dict[str, Any]],
    schema_ids: list[str],
) -> str:
    status_counts = build_status_counts(pair_rows)
    task_count = len({row["task_name"] for row in pair_rows})
    total_pairs = len(pair_rows)
    matrix_rows = build_task_status_rows(pair_rows, schema_ids)
    docker_rows = [row for row in pair_rows if row["rerun_reason"] == "docker_incident"]
    other_rows = [row for row in pair_rows if row["latest_status"] == "failed_other"]
    unrun_rows = [row for row in pair_rows if row["latest_status"] == "unrun"]

    lines = [
        "# SkillX Round0 Global Status",
        "",
        f"- generated_at: `{generated_at}`",
        f"- skillsbench_root: `{skillsbench_root}`",
        f"- task_count_detected: `{task_count}`",
        f"- schema_count_detected: `{len(schema_ids)}`",
        f"- total_pairs_expected: `{total_pairs}`",
        f"- completed_pairs: `{status_counts['completed']}`",
        f"- docker_incident_pairs: `{status_counts['docker_incident']}`",
        f"- other_failed_pairs: `{status_counts['failed_other']}`",
        f"- unrun_pairs: `{status_counts['unrun']}`",
        "",
        "Legend: `C# = completed`, `D# = latest failure was Docker incident`, `F# = latest failure was other error`, `-0 = never run`.",
        "",
        "## Source Runs",
        "",
        "| run_label | total | succeeded | failed | finished_at | report_path |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for report in report_rows:
        lines.append(
            "| {run_label} | {pair_count_total} | {pair_count_succeeded} | {pair_count_failed} | {finished_at} | `{report_path}` |".format(
                **report
            )
        )

    lines.extend(
        [
            "",
            "## Task x Schema Matrix",
            "",
            "| task | "
            + " | ".join(schema_ids)
            + " |",
            "| --- | "
            + " | ".join("---" for _ in schema_ids)
            + " |",
        ]
    )
    for row in matrix_rows:
        lines.append(
            "| {task_name} | ".format(**row)
            + " | ".join(str(row[schema_id]) for schema_id in schema_ids)
            + " |"
        )

    def _render_pair_section(title: str, rows: list[dict[str, Any]]) -> None:
        lines.extend(["", f"## {title}", ""])
        if not rows:
            lines.append("- none")
            return
        for row in rows:
            lines.append(
                "- `{pair_id}`: status=`{latest_status}`, attempts=`{attempt_count}`, latest_run=`{latest_run_label}`, reason=`{rerun_reason}`".format(
                    **row
                )
            )
            if row["latest_failure_summary"]:
                lines.append(f"  latest_failure: `{row['latest_failure_summary']}`")

    _render_pair_section("Pairs Needing Rerun: Docker Incident", docker_rows)
    _render_pair_section("Pairs Needing Attention: Other Failure", other_rows)
    _render_pair_section("Pairs Not Yet Run", unrun_rows)

    return "\n".join(lines) + "\n"


def build_global_status(
    *,
    skillsbench_root: Path,
    round0_root: Path,
    task_filter: list[str] | None = None,
    schema_filter: list[str] | None = None,
) -> dict[str, Any]:
    task_ids = discover_task_ids(skillsbench_root)
    if task_filter:
        known_task_ids = set(task_ids)
        unknown = [task_id for task_id in task_filter if task_id not in known_task_ids]
        if unknown:
            raise KeyError(f"unknown task(s): {', '.join(unknown)}")
        task_filter_set = set(task_filter)
        task_ids = [task_id for task_id in task_ids if task_id in task_filter_set]
    schema_ids = discover_schema_ids(round0_root)
    if schema_filter:
        known_schema_ids = set(schema_ids)
        unknown = [schema_id for schema_id in schema_filter if schema_id not in known_schema_ids]
        if unknown:
            raise KeyError(f"unknown schema id(s): {', '.join(unknown)}")
        schema_filter_set = set(schema_filter)
        schema_ids = [schema_id for schema_id in schema_ids if schema_id in schema_filter_set]
    report_paths = discover_run_report_paths(round0_root)
    report_rows, attempts_by_pair = summarize_reports(report_paths)
    pair_rows = build_pair_rows(
        task_ids=task_ids,
        schema_ids=schema_ids,
        attempts_by_pair=attempts_by_pair,
    )
    status_counts = build_status_counts(pair_rows)
    return {
        "generated_at": _timestamp(),
        "skillsbench_root": str(skillsbench_root),
        "round0_root": str(round0_root),
        "task_count_detected": len(task_ids),
        "schema_ids": schema_ids,
        "pair_count_expected": len(pair_rows),
        "pair_count_attempted": sum(1 for row in pair_rows if row["attempt_count"] > 0),
        "pair_count_completed": status_counts["completed"],
        "pair_count_docker_incident": status_counts["docker_incident"],
        "pair_count_other_failed": status_counts["failed_other"],
        "pair_count_unrun": status_counts["unrun"],
        "reports": report_rows,
        "pairs": pair_rows,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skillsbench-root", type=Path, default=DEFAULT_SKILLSBENCH_ROOT)
    parser.add_argument("--round0-root", type=Path, default=DEFAULT_ROUND0_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--task",
        action="append",
        default=None,
        help="Optional task id to include. Repeatable. Defaults to all detected tasks.",
    )
    parser.add_argument(
        "--schema-id",
        action="append",
        default=None,
        help="Optional schema id to include. Repeatable. Defaults to all detected schemas.",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    payload = build_global_status(
        skillsbench_root=args.skillsbench_root.resolve(),
        round0_root=args.round0_root.resolve(),
        task_filter=args.task,
        schema_filter=args.schema_id,
    )
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    pair_rows = list(payload["pairs"])
    markdown = render_markdown(
        generated_at=payload["generated_at"],
        skillsbench_root=args.skillsbench_root.resolve(),
        report_rows=list(payload["reports"]),
        pair_rows=pair_rows,
        schema_ids=list(payload["schema_ids"]),
    )

    write_json(output_dir / "global_pair_status.json", payload)
    write_csv(
        output_dir / "global_pair_status.csv",
        pair_rows,
        fieldnames=[
            "pair_id",
            "task_name",
            "schema_id",
            "latest_status",
            "latest_status_code",
            "attempt_count",
            "successful_attempt_count",
            "docker_incident_attempt_count",
            "other_failure_attempt_count",
            "needs_rerun",
            "rerun_reason",
            "latest_run_label",
            "latest_started_at",
            "latest_finished_at",
            "latest_launcher_status",
            "latest_launcher_stage",
            "latest_launcher_returncode",
            "latest_run_status",
            "latest_failure_stage",
            "latest_failure_type",
            "latest_failure_summary",
            "latest_selected_round_index",
            "latest_selected_score_pct",
            "latest_best_observed_round_index",
            "latest_best_observed_score_pct",
            "latest_early_stop",
            "latest_timeout_detected",
            "latest_has_intermediate_exceptions",
            "latest_output_dir",
            "attempt_run_labels",
        ],
    )
    (output_dir / "global_status_matrix.md").write_text(markdown)
    print(f"Wrote global round0 status to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
