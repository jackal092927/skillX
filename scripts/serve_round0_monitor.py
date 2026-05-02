#!/usr/bin/env python3
"""Serve a lightweight local dashboard for a round0 launcher run."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
from pathlib import Path
import shlex
import subprocess
from typing import Any


SELECTED_LINE_PATTERN = re.compile(r"Selected\s+(\d+)\s+task\(s\)\s+->\s+(\d+)\s+pair\(s\)")
MAX_CONCURRENT_PATTERN = re.compile(r"Running pairs with max_concurrent_pairs=(\d+)")
RUN_STATUS_PATTERN = re.compile(r"^- ([a-z_]+): `?(.*?)`?$")
OUTPUT_DIR_PATTERN = re.compile(r"--output-dir\s+(\S+)")
ROUND_NAME_PATTERN = re.compile(r"^round-(\d+)$")
ROUND_STAGE_ORDER = ("executor", "role_a", "role_b")
EARLY_TERMINAL_DECISIONS = {"stop", "keep_current", "select_final"}
COMPLETED_ISSUE_STATUS_LABELS = {
    "completed_with_runtime_failures": "runtime exceptions",
    "completed_with_contract_failures": "contract issues",
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _isoformat(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _coerce_datetime(value: str | datetime | None) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized).astimezone(timezone.utc)
    return _utc_now()


def _safe_read_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def _resolve_materialized_reference(raw_path: Any, *, materialized_root: Path) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path:
        return None
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path.resolve()
    repo_root = Path(__file__).resolve().parents[1]
    repo_relative = (repo_root / path).resolve()
    if repo_relative.exists():
        return repo_relative
    return (materialized_root / path).resolve()


def _read_ndjson(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _round_index_from_name(name: str) -> int | None:
    match = ROUND_NAME_PATTERN.match(name)
    if match is None:
        return None
    return int(match.group(1))


def _parse_stdout_metadata(stdout_log_path: Path) -> tuple[int | None, list[str], int | None]:
    if not stdout_log_path.exists():
        return None, [], None

    total_pairs: int | None = None
    max_concurrent_pairs: int | None = None
    selected_task_names: list[str] = []
    for raw_line in stdout_log_path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = SELECTED_LINE_PATTERN.search(line)
        if match:
            total_pairs = int(match.group(2))
            continue
        max_concurrent_match = MAX_CONCURRENT_PATTERN.search(line)
        if max_concurrent_match:
            max_concurrent_pairs = int(max_concurrent_match.group(1))
            continue
        if line.startswith("Tasks:"):
            selected_task_names = [
                part.strip()
                for part in line.removeprefix("Tasks:").split(",")
                if part.strip()
            ]
    return total_pairs, selected_task_names, max_concurrent_pairs


def _latest_mtime(path: Path) -> float | None:
    if not path.exists():
        return None
    latest = path.stat().st_mtime
    for child in path.rglob("*"):
        try:
            child_mtime = child.stat().st_mtime
        except FileNotFoundError:
            continue
        latest = max(latest, child_mtime)
    return latest


def _parse_run_status(path: Path) -> dict[str, str]:
    payload: dict[str, str] = {}
    if not path.exists():
        return payload
    for raw_line in path.read_text().splitlines():
        match = RUN_STATUS_PATTERN.match(raw_line)
        if match:
            payload[match.group(1)] = match.group(2)
    return payload


def _status_value_from_sources(
    *,
    launcher_result: dict[str, Any] | None,
    run_status: dict[str, str],
) -> str | None:
    launcher_status = launcher_result.get("status") if isinstance(launcher_result, dict) else None
    if isinstance(launcher_status, str) and launcher_status:
        normalized = launcher_status.strip().lower()
        if normalized in {"failed", "failure", "error", "running", "in_progress", "started", "active"}:
            return launcher_status

    run_status_value = run_status.get("status")
    if isinstance(run_status_value, str) and run_status_value:
        return run_status_value
    if isinstance(launcher_status, str) and launcher_status:
        return launcher_status
    return None


def _find_early_terminal_decision(
    run_dir: Path,
    round_budget: int | None,
) -> tuple[str, int] | None:
    if round_budget is None:
        return None
    task_root = _find_refine_task_root(run_dir)
    rounds_root = task_root / "rounds" if isinstance(task_root, Path) else None
    if not isinstance(rounds_root, Path) or not rounds_root.exists():
        return None

    for round_dir in sorted(path for path in rounds_root.iterdir() if path.is_dir()):
        round_index = _round_index_from_name(round_dir.name)
        if round_index is None:
            continue
        events = _read_ndjson(round_dir / "orchestrator_log.ndjson")
        for event in events:
            if str(event.get("event_type") or "") != "round_decision_loaded":
                continue
            decision = str(event.get("status") or "")
            if decision in EARLY_TERMINAL_DECISIONS and round_index < round_budget:
                return decision, round_index
    return None


def _completed_status_label(
    *,
    normalized_status: str,
    run_status: dict[str, str],
    run_dir: Path,
) -> str:
    round_budget_raw = run_status.get("round_budget")
    try:
        round_budget = int(round_budget_raw) if round_budget_raw else None
    except ValueError:
        round_budget = None

    detail_parts: list[str] = []
    issue_label = COMPLETED_ISSUE_STATUS_LABELS.get(normalized_status)
    if issue_label:
        detail_parts.append(issue_label)

    terminal_decision = _find_early_terminal_decision(run_dir, round_budget)
    if terminal_decision is not None:
        decision, round_index = terminal_decision
        detail_parts.append(f"{decision}@R{round_index}")

    if detail_parts:
        return f"completed ({', '.join(detail_parts)})"
    return "completed"


def _pair_has_issues_from_sources(
    *,
    launcher_result: dict[str, Any] | None,
    run_status: dict[str, str],
) -> bool:
    status_value = _status_value_from_sources(
        launcher_result=launcher_result,
        run_status=run_status,
    )
    if not isinstance(status_value, str):
        return False
    return status_value.strip().lower() in COMPLETED_ISSUE_STATUS_LABELS


def _resolve_active_run_dir(launcher_log_dir: Path, pair_id: str | None) -> Path | None:
    if not pair_id:
        return None
    materialized_root = launcher_log_dir.parent.parent
    pair_dir = materialized_root / "pairs" / pair_id
    suffixed_run_dir = pair_dir / f"refine_run_{launcher_log_dir.name}"
    if suffixed_run_dir.exists():
        return suffixed_run_dir
    plain_run_dir = pair_dir / "refine_run"
    if plain_run_dir.exists():
        return plain_run_dir
    return None


def _scan_active_process_commands(pair_id: str | None, run_label: str) -> list[str]:
    if not pair_id:
        return []
    proc = subprocess.run(
        ["ps", "-axo", "command"],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return []

    run_id_token = f"{pair_id}__{run_label}"
    matches: list[str] = []
    for raw_line in proc.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "serve_round0_monitor.py" in line:
            continue
        if run_id_token in line or (
            "run_skillx_refine_benchmark.py" in line
            and pair_id in line
            and run_label in line
        ):
            matches.append(line)
    return matches


def _scan_launcher_process_commands(run_label: str) -> list[str]:
    proc = subprocess.run(
        ["ps", "-axo", "command"],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return []

    matches: list[str] = []
    for raw_line in proc.stdout.splitlines():
        line = raw_line.strip()
        if not line or "serve_round0_monitor.py" in line:
            continue
        if "launch_skillx_round0.py" not in line:
            continue
        if run_label not in line:
            continue
        matches.append(line)
    return matches


def _extract_cli_args(command: str, flag: str) -> list[str]:
    try:
        parts = shlex.split(command)
    except ValueError:
        return []

    values: list[str] = []
    for index, part in enumerate(parts):
        if part == flag and index + 1 < len(parts):
            values.append(parts[index + 1])
            continue
        prefix = f"{flag}="
        if part.startswith(prefix):
            values.append(part[len(prefix) :])
    return values


def _resolve_cli_path(raw_path: str, *, base_dir: Path) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (base_dir / path).resolve()


def _load_selection_from_pair_manifest(path: Path) -> tuple[int | None, list[str], list[str]]:
    payload = _safe_read_json(path)
    if not isinstance(payload, dict):
        return None, [], []

    selected_pair_ids = [
        str(item)
        for item in (payload.get("selected_pair_ids") or [])
        if isinstance(item, str) and item
    ]
    selected_task_names = [
        str(item)
        for item in (payload.get("selected_task_names") or payload.get("task_names") or [])
        if isinstance(item, str) and item
    ]
    pair_count_total = payload.get("pair_count_total")
    pair_count = payload.get("pair_count")
    if isinstance(pair_count_total, int):
        total_pairs = pair_count_total
    elif isinstance(pair_count, int):
        total_pairs = pair_count
    else:
        total_pairs = None
    return total_pairs, selected_task_names, selected_pair_ids


def _load_selection_from_command(
    command: str,
    *,
    base_dir: Path,
    pair_to_task_name: dict[str, str],
) -> tuple[int | None, list[str], list[str] | None]:
    pair_manifest_values = _extract_cli_args(command, "--pair-manifest")
    if pair_manifest_values:
        total_pairs, selected_task_names, selected_pair_ids = _load_selection_from_pair_manifest(
            _resolve_cli_path(pair_manifest_values[-1], base_dir=base_dir)
        )
        if selected_pair_ids:
            return total_pairs, selected_task_names, selected_pair_ids

    explicit_pair_ids = _extract_cli_args(command, "--pair-id")
    if explicit_pair_ids:
        selected_task_names: list[str] = []
        seen_tasks: set[str] = set()
        for pair_id in explicit_pair_ids:
            task_name = pair_to_task_name.get(pair_id)
            if task_name and task_name not in seen_tasks:
                selected_task_names.append(task_name)
                seen_tasks.add(task_name)
        return len(explicit_pair_ids), selected_task_names, explicit_pair_ids

    return None, [], None


def _read_inner_loop_script_workdir(script_path: Path) -> Path | None:
    if not script_path.exists():
        return None
    for raw_line in script_path.read_text().splitlines():
        line = raw_line.strip()
        if not line.startswith("cd "):
            continue
        try:
            parts = shlex.split(line)
        except ValueError:
            continue
        if len(parts) == 2 and parts[0] == "cd":
            return Path(parts[1]).expanduser().resolve()
    return None


def _load_selection_from_launcher_artifacts(
    launcher_log_dir: Path,
) -> tuple[int | None, list[str], list[str] | None]:
    materialized_root = launcher_log_dir.parent.parent
    pair_to_task_name = {
        str(pair_spec.get("pair_id")): str(pair_spec.get("task_name"))
        for pair_spec in _read_pair_specs(materialized_root)
        if isinstance(pair_spec.get("pair_id"), str) and isinstance(pair_spec.get("task_name"), str)
    }
    inner_loop_script = launcher_log_dir / "run_inner_loop.sh"
    if not inner_loop_script.exists():
        return None, [], None

    base_dir = _read_inner_loop_script_workdir(inner_loop_script) or Path.cwd()
    for raw_line in inner_loop_script.read_text().splitlines():
        line = raw_line.strip()
        if "launch_skillx_round0.py" not in line:
            continue
        total_pairs, selected_task_names, selected_pair_ids = _load_selection_from_command(
            line,
            base_dir=base_dir,
            pair_to_task_name=pair_to_task_name,
        )
        if selected_pair_ids:
            return total_pairs, selected_task_names, selected_pair_ids

    return None, [], None


def _load_selection_from_summary(
    summary: dict[str, Any] | None,
) -> tuple[int | None, list[str], list[str] | None]:
    if not isinstance(summary, dict):
        return None, [], None
    total_pairs = summary.get("total_pairs")
    selected_task_names = [
        str(item)
        for item in (summary.get("selected_task_names") or [])
        if isinstance(item, str) and item
    ]
    selected_pair_ids = [
        str(item)
        for item in (summary.get("selected_pair_ids") or [])
        if isinstance(item, str) and item
    ]
    return (
        int(total_pairs) if isinstance(total_pairs, int) else None,
        selected_task_names,
        selected_pair_ids or None,
    )


def _load_selection_from_launcher_processes(
    launcher_log_dir: Path,
) -> tuple[int | None, list[str], list[str] | None]:
    commands = _scan_launcher_process_commands(launcher_log_dir.name)
    if not commands:
        return None, [], None

    materialized_root = launcher_log_dir.parent.parent
    pair_specs = _read_pair_specs(materialized_root)
    pair_to_task_name = {
        str(pair_spec.get("pair_id")): str(pair_spec.get("task_name"))
        for pair_spec in pair_specs
        if isinstance(pair_spec.get("pair_id"), str) and isinstance(pair_spec.get("task_name"), str)
    }

    for command in commands:
        total_pairs, selected_task_names, selected_pair_ids = _load_selection_from_command(
            command,
            base_dir=Path.cwd(),
            pair_to_task_name=pair_to_task_name,
        )
        if selected_pair_ids:
            return total_pairs, selected_task_names, selected_pair_ids

    return None, [], None


def _resolve_active_run_dir_from_processes(process_commands: list[str]) -> Path | None:
    for command in process_commands:
        match = OUTPUT_DIR_PATTERN.search(command)
        if match:
            return Path(match.group(1)).resolve()
    return None


def _last_failure_from_summary(summary: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(summary, dict):
        return None
    results = summary.get("results")
    if not isinstance(results, list):
        return None
    for item in reversed(results):
        if isinstance(item, dict) and item.get("status") == "failed":
            return item
    return None


def _last_failure_from_events(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    for event in reversed(events):
        if event.get("event") == "pair_failed":
            return event
    return None


def _find_refine_task_root(active_run_dir: Path) -> Path | None:
    refine_root = active_run_dir / "refine"
    if not refine_root.exists():
        return None
    task_roots = sorted(path for path in refine_root.iterdir() if path.is_dir())
    if len(task_roots) != 1:
        return None
    return task_roots[0]


def _read_pair_specs(materialized_root: Path) -> list[dict[str, Any]]:
    pair_specs_jsonl = materialized_root / "pair_specs.jsonl"
    rows: list[dict[str, Any]] = []
    if pair_specs_jsonl.exists():
        for raw_line in pair_specs_jsonl.read_text().splitlines():
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


def _read_materialized_manifest(materialized_root: Path) -> dict[str, Any] | None:
    payload = _safe_read_json(materialized_root / "manifest.json")
    return payload if isinstance(payload, dict) else None


def _read_preflight_risk_audit(launcher_log_dir: Path) -> dict[str, Any] | None:
    payload = _safe_read_json(launcher_log_dir / "preflight_docker_risk_audit.json")
    return payload if isinstance(payload, dict) else None


def _resolve_materialized_path(raw_path: str, *, materialized_root: Path) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (materialized_root / path).resolve()


def _resolve_pair_run_dir_for_label(
    pair_spec: dict[str, Any],
    *,
    materialized_root: Path,
    run_label: str,
) -> Path:
    pair_dir = _resolve_materialized_path(
        str(pair_spec.get("pair_dir") or ""),
        materialized_root=materialized_root,
    )
    return pair_dir / f"refine_run_{run_label}"


def _stage_states_from_round_events(events: list[dict[str, Any]]) -> tuple[dict[str, str], str | None]:
    stage_states = {stage: "pending" for stage in ROUND_STAGE_ORDER}
    latest_event_type = None
    if not events:
        return stage_states, None

    event_types = [str(event.get("event_type") or "") for event in events]
    latest_event_type = event_types[-1] or None
    if "executor_completed" in event_types:
        stage_states["executor"] = "completed"
    if "role_a_completed" in event_types:
        stage_states["role_a"] = "completed"
    if "role_b_completed" in event_types:
        stage_states["role_b"] = "completed"

    if "round_started" in event_types and "executor_completed" not in event_types:
        stage_states["executor"] = "running"
    elif "executor_completed" in event_types and "role_a_completed" not in event_types:
        stage_states["role_a"] = "running"
    elif "role_a_completed" in event_types and "role_b_completed" not in event_types:
        stage_states["role_b"] = "running"

    return stage_states, latest_event_type


def _collect_pair_detail(active_run_dir: Path) -> dict[str, Any] | None:
    task_root = _find_refine_task_root(active_run_dir)
    if task_root is None:
        return None

    rounds_root = task_root / "rounds"
    round_rows: list[dict[str, Any]] = []
    if rounds_root.exists():
        round_dirs = sorted(
            (
                path
                for path in rounds_root.iterdir()
                if path.is_dir() and _round_index_from_name(path.name) is not None
            ),
            key=lambda path: int(_round_index_from_name(path.name) or -1),
        )
        for round_dir in round_dirs:
            round_index = int(_round_index_from_name(round_dir.name) or 0)
            events = _read_ndjson(round_dir / "orchestrator_log.ndjson")
            stage_states, latest_event_type = _stage_states_from_round_events(events)
            latest_event = events[-1] if events else None
            round_rows.append(
                {
                    "round_index": round_index,
                    "round_dir": str(round_dir),
                    "latest_event_type": latest_event_type,
                    "latest_event_status": latest_event.get("status") if isinstance(latest_event, dict) else None,
                    "latest_event_timestamp": latest_event.get("timestamp") if isinstance(latest_event, dict) else None,
                    "stage_states": stage_states,
                }
            )

    current_round = round_rows[-1] if round_rows else None
    current_stage = None
    if current_round is not None:
        for stage in ROUND_STAGE_ORDER:
            if current_round["stage_states"].get(stage) == "running":
                current_stage = stage
                break

    last_completed_stage = None
    for row in reversed(round_rows):
        for stage in reversed(ROUND_STAGE_ORDER):
            if row["stage_states"].get(stage) == "completed":
                last_completed_stage = stage
                break
        if last_completed_stage is not None:
            break

    return {
        "task_id": task_root.name,
        "current_round_index": current_round.get("round_index") if isinstance(current_round, dict) else None,
        "current_stage": current_stage,
        "last_completed_stage": last_completed_stage,
        "round_rows": round_rows,
    }


def _collect_active_pair_details(
    launcher_log_dir: Path,
    active_pairs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for active_pair in active_pairs:
        pair_id = active_pair.get("pair_id")
        if not isinstance(pair_id, str) or not pair_id:
            continue
        process_commands = _scan_active_process_commands(pair_id, launcher_log_dir.name)
        active_run_dir = _resolve_active_run_dir(launcher_log_dir, pair_id)
        if active_run_dir is None:
            active_run_dir = _resolve_active_run_dir_from_processes(process_commands)
        active_run_status = (
            _parse_run_status(active_run_dir / "RUN_STATUS.md")
            if isinstance(active_run_dir, Path)
            else {}
        )
        pair_detail = _collect_pair_detail(active_run_dir) if isinstance(active_run_dir, Path) else None
        retry_archives = _collect_retry_archives(active_run_dir) if isinstance(active_run_dir, Path) else []
        active_run_mtime = _latest_mtime(active_run_dir) if isinstance(active_run_dir, Path) else None
        latest_activity_at = (
            _isoformat(datetime.fromtimestamp(active_run_mtime, tz=timezone.utc))
            if active_run_mtime is not None
            else None
        )
        details.append(
            {
                "pair_id": pair_id,
                "index": active_pair.get("index"),
                "task_name": active_pair.get("task_name") or active_run_status.get("task"),
                "schema_id": active_pair.get("schema_id"),
                "active_run_dir": str(active_run_dir) if isinstance(active_run_dir, Path) else None,
                "active_run_status": active_run_status,
                "active_processes": process_commands,
                "pair_detail": pair_detail,
                "retry_archives": retry_archives,
                "latest_activity_at": latest_activity_at,
            }
        )
    return details


def _synthesize_active_run_event(
    *,
    active_pair: dict[str, Any] | None,
    active_run_status: dict[str, str],
    pair_detail: dict[str, Any] | None,
    observed_at: datetime | None,
) -> dict[str, Any] | None:
    if observed_at is None:
        return None
    if not isinstance(active_pair, dict):
        return None

    current_stage = pair_detail.get("current_stage") if isinstance(pair_detail, dict) else None
    current_round_index = pair_detail.get("current_round_index") if isinstance(pair_detail, dict) else None
    task_name = active_run_status.get("task") or active_pair.get("task_name")
    status_value = active_run_status.get("status") or "running"

    note_parts = [f"status={status_value}"]
    if isinstance(current_round_index, int):
        note_parts.append(f"round=R{current_round_index}")
    if isinstance(current_stage, str) and current_stage:
        note_parts.append(f"stage={current_stage}")
    elif isinstance(pair_detail, dict) and pair_detail.get("round_rows"):
        note_parts.append("stage=bootstrap")

    return {
        "event": "active_run_heartbeat",
        "observed_at": _isoformat(observed_at),
        "pair_id": active_pair.get("pair_id"),
        "schema_id": active_pair.get("schema_id"),
        "task_name": task_name,
        "status": status_value,
        "note": ", ".join(note_parts),
    }


def _read_round_score_map(run_dir: Path) -> dict[int, float | None]:
    task_root = _find_refine_task_root(run_dir)
    if task_root is None:
        return {}
    round_scores: dict[int, float | None] = {}
    rounds_root = task_root / "rounds"
    if not rounds_root.exists():
        return round_scores
    for round_dir in sorted(path for path in rounds_root.iterdir() if path.is_dir()):
        round_index = _round_index_from_name(round_dir.name)
        if round_index is None:
            continue
        tune_result = _safe_read_json(round_dir / "tune_check" / "result.json")
        reward = tune_result.get("reward") if isinstance(tune_result, dict) else None
        round_scores[round_index] = float(reward) if isinstance(reward, (int, float)) else None
    return round_scores


def _read_baseline_perfect_rerun_report(run_dir: Path) -> dict[str, Any] | None:
    task_root = _find_refine_task_root(run_dir)
    if task_root is None:
        return None
    payload = _safe_read_json(task_root / "baseline_perfect_rerun.json")
    return payload if isinstance(payload, dict) else None


def _last_r0_attempt_reward(report: dict[str, Any] | None) -> float | None:
    if not isinstance(report, dict):
        return None
    attempts = report.get("attempts")
    last_attempt = attempts[-1] if isinstance(attempts, list) and attempts else {}
    reward = (
        last_attempt.get("reward")
        if isinstance(last_attempt, dict) and "reward" in last_attempt
        else report.get("final_reward")
    )
    return float(reward) if isinstance(reward, (int, float)) else None


def _rewards_match(left: float | None, right: float | None) -> bool:
    if left is None or right is None:
        return left is None and right is None
    return abs(left - right) <= 1e-9


def _effective_r0_reward(
    *,
    active_r0_reward: float | None,
    baseline_perfect_rerun: dict[str, Any] | None,
) -> dict[str, Any]:
    report_reward = _last_r0_attempt_reward(baseline_perfect_rerun)
    rerun_count = (
        baseline_perfect_rerun.get("rerun_count")
        if isinstance(baseline_perfect_rerun, dict)
        else None
    )
    if not isinstance(rerun_count, int):
        rerun_count = 0
    has_report = isinstance(baseline_perfect_rerun, dict) and baseline_perfect_rerun.get("enabled")
    is_stale = bool(
        has_report
        and active_r0_reward is not None
        and report_reward is not None
        and not _rewards_match(active_r0_reward, report_reward)
    )
    if is_stale:
        effective_reward = active_r0_reward
    elif report_reward is not None:
        effective_reward = report_reward
    else:
        effective_reward = active_r0_reward
    return {
        "reward": effective_reward,
        "score": _reward_to_percent(effective_reward),
        "rerun_count": rerun_count,
        "rerun_status": "stale" if is_stale else str(rerun_count),
        "report_stale": is_stale,
    }


def _read_refine_summary(run_dir: Path) -> dict[str, Any] | None:
    task_root = _find_refine_task_root(run_dir)
    if task_root is None:
        return None
    payload = _safe_read_json(task_root / "refine_summary.json")
    return payload if isinstance(payload, dict) else None


def _archive_timestamp_from_name(name: str) -> str | None:
    prefix = "rate-limit-fallback-"
    if not name.startswith(prefix):
        return None
    stamp = name.removeprefix(prefix)
    try:
        parsed = datetime.strptime(stamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return _isoformat(parsed)


def _archive_round_indices(archive_dir: Path) -> list[int]:
    rounds_root = archive_dir / "rounds"
    if not rounds_root.exists():
        return []
    round_indices: list[int] = []
    for round_dir in rounds_root.iterdir():
        if not round_dir.is_dir():
            continue
        round_index = _round_index_from_name(round_dir.name)
        if round_index is not None:
            round_indices.append(round_index)
    return sorted(round_indices)


def _collect_retry_archives(run_dir: Path) -> list[dict[str, Any]]:
    archives_root = run_dir / "archives"
    if not archives_root.exists():
        return []

    archives: list[dict[str, Any]] = []
    for archive_dir in sorted(path for path in archives_root.iterdir() if path.is_dir()):
        if not archive_dir.name.startswith("rate-limit-fallback-"):
            continue
        run_status = _parse_run_status(archive_dir / "RUN_STATUS.md")
        signal = _safe_read_json(archive_dir / "rate_limit_signal.json")
        signal = signal if isinstance(signal, dict) else {}
        refine_summary = _safe_read_json(archive_dir / "refine_summary.json")
        refine_summary = refine_summary if isinstance(refine_summary, dict) else {}
        selected = refine_summary.get("selected") if isinstance(refine_summary.get("selected"), dict) else {}
        round_indices = _archive_round_indices(archive_dir)
        archived_at = _archive_timestamp_from_name(archive_dir.name)
        if archived_at is None:
            archive_mtime = _latest_mtime(archive_dir)
            archived_at = (
                _isoformat(datetime.fromtimestamp(archive_mtime, tz=timezone.utc))
                if archive_mtime is not None
                else None
            )
        archives.append(
            {
                "archive_name": archive_dir.name,
                "archive_dir": str(archive_dir),
                "archived_at": archived_at,
                "status": run_status.get("status"),
                "signal_level": signal.get("signal_level"),
                "hard_terms": signal.get("hard_terms") if isinstance(signal.get("hard_terms"), list) else [],
                "rounds": round_indices,
                "first_round": round_indices[0] if round_indices else None,
                "last_round": round_indices[-1] if round_indices else None,
                "selected_round": selected.get("round_index") if isinstance(selected.get("round_index"), int) else None,
                "selected_score": (
                    _reward_to_percent(selected.get("reward"))
                    if isinstance(selected.get("reward"), (int, float))
                    else None
                ),
            }
        )
    return archives


def _pair_status_from_sources(
    *,
    launcher_result: dict[str, Any] | None,
    run_status: dict[str, str],
    run_dir: Path,
    pair_is_active: bool = False,
) -> str:
    status_value = _status_value_from_sources(
        launcher_result=launcher_result,
        run_status=run_status,
    )

    if isinstance(status_value, str) and status_value:
        normalized = status_value.strip().lower()
        if normalized in {"succeeded", "success", "completed", "done", "ok"} or normalized in COMPLETED_ISSUE_STATUS_LABELS:
            return _completed_status_label(
                normalized_status=normalized,
                run_status=run_status,
                run_dir=run_dir,
            )
        if normalized == "skipped_baseline_perfect":
            reruns = run_status.get("baseline_perfect_reruns")
            suffix = f", reruns={reruns}" if reruns else ""
            return f"skipped (R0 100%{suffix})"
        if normalized in {"failed", "failure", "error"}:
            return "failed"
        if normalized in {"running", "in_progress", "started", "active"}:
            return "running"
        return status_value
    if pair_is_active:
        return "running"
    return "pending"


def _task_schema_role(
    *,
    role: str,
    label: str,
    source: str,
    detail: str,
    score: float | None = None,
) -> dict[str, Any]:
    return {
        "role": role,
        "label": label,
        "source": source,
        "detail": detail,
        "score": score,
    }


def _score_value(row: dict[str, Any]) -> float:
    for key in ("assignment_score_pct", "best_score", "best_reported_score"):
        value = row.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return float("-inf")


def _score_rows_by_task(score_matrix: dict[str, Any] | None) -> dict[str, list[dict[str, Any]]]:
    rows = score_matrix.get("long_rows") if isinstance(score_matrix, dict) else None
    by_task: dict[str, list[dict[str, Any]]] = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        task_name = row.get("task_name")
        schema_id = row.get("schema_id")
        if not isinstance(task_name, str) or not isinstance(schema_id, str):
            continue
        by_task.setdefault(task_name, []).append(row)
    for task_rows in by_task.values():
        task_rows.sort(
            key=lambda row: (
                _score_value(row),
                float(row.get("delta_vs_r0_post_best_pp") or 0.0)
                if isinstance(row.get("delta_vs_r0_post_best_pp"), (int, float))
                else 0.0,
                str(row.get("schema_id") or ""),
            ),
            reverse=True,
        )
    return by_task


def _schema_from_score_rows(
    score_rows: list[dict[str, Any]],
    *,
    exclude: set[str],
) -> str | None:
    for row in score_rows:
        schema_id = row.get("schema_id")
        if isinstance(schema_id, str) and schema_id not in exclude:
            return schema_id
    return None


def _score_for_schema(score_rows: list[dict[str, Any]], schema_id: str | None) -> float | None:
    if not schema_id:
        return None
    for row in score_rows:
        if row.get("schema_id") == schema_id:
            value = row.get("assignment_score_pct")
            if isinstance(value, (int, float)):
                return float(value)
            value = row.get("best_score")
            if isinstance(value, (int, float)):
                return float(value)
    return None


def _candidate_control_plane_dirs(
    *,
    materialized_root: Path,
    manifest: dict[str, Any],
) -> list[Path]:
    candidates: list[Path] = []
    package_path = _resolve_materialized_reference(
        manifest.get("schema_update_package_path"),
        materialized_root=materialized_root,
    )
    if package_path is not None:
        candidates.append(package_path.parent.parent / "control-plane")

    run_id = manifest.get("run_id")
    if isinstance(run_id, str) and run_id:
        candidates.append(materialized_root.parent / "reports" / run_id / "control-plane")

    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(resolved)
    return unique


def _load_previous_round_schema_roles(
    *,
    materialized_root: Path,
    manifest: dict[str, Any],
) -> tuple[dict[str, dict[str, dict[str, Any]]], dict[str, Any] | None]:
    for control_plane_dir in _candidate_control_plane_dirs(
        materialized_root=materialized_root,
        manifest=manifest,
    ):
        assignments = _safe_read_json(control_plane_dir / "assignments.json")
        if not isinstance(assignments, dict):
            continue
        assignment_rows = assignments.get("assignments")
        if not isinstance(assignment_rows, list):
            continue

        score_rows_by_task = _score_rows_by_task(
            _safe_read_json(control_plane_dir / "score_matrix.json")
        )
        roles: dict[str, dict[str, dict[str, Any]]] = {}
        for row in assignment_rows:
            if not isinstance(row, dict):
                continue
            task_name = row.get("task_name")
            if not isinstance(task_name, str):
                continue
            task_score_rows = score_rows_by_task.get(task_name, [])
            assignment_status = str(row.get("assignment_status") or "")
            assigned_category = row.get("assigned_category")
            best_observed_category = row.get("best_observed_category")

            primary_schema = (
                assigned_category
                if isinstance(assigned_category, str) and assigned_category
                else best_observed_category
                if isinstance(best_observed_category, str) and best_observed_category
                else _schema_from_score_rows(task_score_rows, exclude=set())
            )
            if not isinstance(primary_schema, str) or not primary_schema:
                continue

            primary_label = "Primary" if assigned_category else "Best"
            roles.setdefault(task_name, {})[primary_schema] = _task_schema_role(
                role="primary",
                label=primary_label,
                source="previous_round_assignment",
                detail=(
                    f"{assignment_status or 'previous round'}; "
                    f"score={_format_metric(_score_for_schema(task_score_rows, primary_schema))}"
                ),
                score=_score_for_schema(task_score_rows, primary_schema),
            )

            second_schema = row.get("second_best_category")
            if not isinstance(second_schema, str) or not second_schema or second_schema == primary_schema:
                second_schema = _schema_from_score_rows(task_score_rows, exclude={primary_schema})
            if isinstance(second_schema, str) and second_schema and second_schema != primary_schema:
                roles.setdefault(task_name, {})[second_schema] = _task_schema_role(
                    role="secondary",
                    label="2nd",
                    source="previous_round_assignment",
                    detail=(
                        "previous round second; "
                        f"score={_format_metric(_score_for_schema(task_score_rows, second_schema))}"
                    ),
                    score=_score_for_schema(task_score_rows, second_schema),
                )

        if roles:
            return roles, {
                "mode": "previous_round_assignment",
                "control_plane_dir": str(control_plane_dir),
                "legend": "Primary/Best and 2nd are derived from the previous round control-plane assignment artifacts.",
            }
    return {}, None


def _load_seed_schema_roles(
    *,
    materialized_root: Path,
    manifest: dict[str, Any],
) -> tuple[dict[str, dict[str, dict[str, Any]]], dict[str, Any] | None]:
    inventory_path = _resolve_materialized_reference(
        manifest.get("inventory_path"),
        materialized_root=materialized_root,
    )
    if inventory_path is None or not inventory_path.exists():
        return {}, None

    roles: dict[str, dict[str, dict[str, Any]]] = {}
    for raw_line in inventory_path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        task_name = row.get("task_name")
        cluster_inputs = row.get("cluster_inputs")
        semantic_contract = (
            cluster_inputs.get("semantic_contract")
            if isinstance(cluster_inputs, dict)
            else None
        )
        seed_schema = (
            semantic_contract.get("task_object_seed")
            if isinstance(semantic_contract, dict)
            else None
        )
        if isinstance(task_name, str) and isinstance(seed_schema, str) and seed_schema:
            roles.setdefault(task_name, {})[seed_schema] = _task_schema_role(
                role="seed",
                label="Seed",
                source="task_inventory_seed",
                detail="task_object_seed from the task cluster inventory",
            )

    if roles:
        return roles, {
            "mode": "seed_schema",
            "inventory_path": str(inventory_path),
            "legend": "Seed highlights use task_object_seed because no previous-round assignment artifacts were found.",
        }
    return {}, None


def _load_schema_highlight_roles(
    *,
    materialized_root: Path,
    manifest: dict[str, Any],
) -> tuple[dict[str, dict[str, dict[str, Any]]], dict[str, Any]]:
    previous_roles, metadata = _load_previous_round_schema_roles(
        materialized_root=materialized_root,
        manifest=manifest,
    )
    if metadata is not None:
        return previous_roles, metadata

    seed_roles, seed_metadata = _load_seed_schema_roles(
        materialized_root=materialized_root,
        manifest=manifest,
    )
    if seed_metadata is not None:
        return seed_roles, seed_metadata

    return {}, {
        "mode": "none",
        "legend": "No schema highlight source was found for this materialized root.",
    }


def _collect_pair_rows(
    *,
    launcher_log_dir: Path,
    selected_task_names: list[str],
    selected_pair_ids: list[str] | None,
    summary: dict[str, Any] | None,
    current_pair_id: str | None,
    active_pair_ids: set[str] | None,
    active_run_dir: Path | None,
) -> list[dict[str, Any]]:
    materialized_root = launcher_log_dir.parent.parent
    manifest = _read_materialized_manifest(materialized_root) or {}
    schema_highlight_roles, _schema_highlight_metadata = _load_schema_highlight_roles(
        materialized_root=materialized_root,
        manifest=manifest,
    )
    schema_ids = [
        item for item in (manifest.get("schema_ids") or []) if isinstance(item, str)
    ]
    pair_specs = _read_pair_specs(materialized_root)
    task_order = {task_name: index for index, task_name in enumerate(selected_task_names)}
    pair_order = (
        {pair_id: index for index, pair_id in enumerate(selected_pair_ids)}
        if selected_pair_ids is not None
        else {}
    )
    schema_order = {schema_id: index for index, schema_id in enumerate(schema_ids)}
    summary_results = summary.get("results") if isinstance(summary, dict) else None
    summary_by_pair_id = {
        item.get("pair_id"): item
        for item in summary_results or []
        if isinstance(item, dict) and isinstance(item.get("pair_id"), str)
    }

    rows: list[dict[str, Any]] = []
    for pair_spec in pair_specs:
        task_name = pair_spec.get("task_name")
        schema_id = pair_spec.get("schema_id")
        pair_id = pair_spec.get("pair_id")
        if not isinstance(task_name, str) or not isinstance(schema_id, str) or not isinstance(pair_id, str):
            continue
        if selected_pair_ids is not None:
            if pair_id not in pair_order:
                continue
        elif selected_task_names and task_name not in task_order:
            continue

        pair_is_active = active_pair_ids is not None and pair_id in active_pair_ids
        launcher_result = summary_by_pair_id.get(pair_id)
        launcher_output_dir = (
            Path(str(launcher_result.get("output_dir"))).resolve()
            if isinstance(launcher_result, dict) and isinstance(launcher_result.get("output_dir"), str)
            else None
        )
        if pair_id == current_pair_id and isinstance(active_run_dir, Path):
            run_dir = active_run_dir
        elif isinstance(launcher_output_dir, Path):
            run_dir = launcher_output_dir
        else:
            run_dir = _resolve_pair_run_dir_for_label(
                pair_spec,
                materialized_root=materialized_root,
                run_label=launcher_log_dir.name,
            )
        run_status = _parse_run_status(run_dir / "RUN_STATUS.md")
        retry_archives = _collect_retry_archives(run_dir)
        round_scores_raw = _read_round_score_map(run_dir)
        baseline_perfect_rerun = _read_baseline_perfect_rerun_report(run_dir)
        effective_r0 = _effective_r0_reward(
            active_r0_reward=round_scores_raw.get(0),
            baseline_perfect_rerun=baseline_perfect_rerun,
        )
        if effective_r0.get("reward") is not None:
            round_scores_raw[0] = effective_r0["reward"]
        round_scores = {
            f"R{round_index}": _reward_to_percent(round_scores_raw.get(round_index))
            for round_index in range(0, 4)
        }
        refine_summary = _read_refine_summary(run_dir)
        selected = refine_summary.get("selected") if isinstance(refine_summary, dict) else None
        selected_round_index = selected.get("round_index") if isinstance(selected, dict) else None
        selected_score_raw = selected.get("reward") if isinstance(selected, dict) else None
        selected_score_raw = float(selected_score_raw) if isinstance(selected_score_raw, (int, float)) else None
        selected_score = _reward_to_percent(selected_score_raw)
        official_scores = pair_spec.get("official_scores") or {}
        official_c0 = official_scores.get("no_skills") if isinstance(official_scores, dict) else None
        official_c1 = official_scores.get("with_skills") if isinstance(official_scores, dict) else None
        official_c0 = float(official_c0) if isinstance(official_c0, (int, float)) else None
        official_c1 = float(official_c1) if isinstance(official_c1, (int, float)) else None
        r0_score = round_scores.get("R0")
        schema_role = schema_highlight_roles.get(task_name, {}).get(schema_id)

        rows.append(
            {
                "pair_id": pair_id,
                "task_name": task_name,
                "schema_id": schema_id,
                "schema_highlight_role": (
                    schema_role.get("role") if isinstance(schema_role, dict) else None
                ),
                "schema_highlight_label": (
                    schema_role.get("label") if isinstance(schema_role, dict) else None
                ),
                "schema_highlight_source": (
                    schema_role.get("source") if isinstance(schema_role, dict) else None
                ),
                "schema_highlight_detail": (
                    schema_role.get("detail") if isinstance(schema_role, dict) else None
                ),
                "schema_highlight_score": (
                    schema_role.get("score") if isinstance(schema_role, dict) else None
                ),
                "official_c0": official_c0,
                "official_c1": official_c1,
                "round_rewards_raw": {
                    f"R{round_index}": round_scores_raw.get(round_index)
                    for round_index in range(0, 4)
                },
                "round_scores": round_scores,
                "baseline_perfect_rerun": baseline_perfect_rerun,
                "effective_r0_reward_raw": effective_r0.get("reward"),
                "effective_r0_score": effective_r0.get("score"),
                "r0_rerun_count": effective_r0.get("rerun_count"),
                "r0_rerun_status": effective_r0.get("rerun_status"),
                "r0_rerun_report_stale": effective_r0.get("report_stale"),
                "selected_round": (
                    f"R{selected_round_index}" if isinstance(selected_round_index, int) else None
                ),
                "selected_score_raw": selected_score_raw,
                "selected_score": selected_score,
                "delta_vs_c0": (
                    selected_score - official_c0
                    if selected_score is not None and official_c0 is not None
                    else None
                ),
                "delta_vs_c1": (
                    selected_score - official_c1
                    if selected_score is not None and official_c1 is not None
                    else None
                ),
                "delta_vs_r0": (
                    selected_score - r0_score
                    if selected_score is not None and isinstance(r0_score, (int, float))
                    else None
                ),
                "pair_status": _pair_status_from_sources(
                    launcher_result=launcher_result,
                    run_status=run_status,
                    run_dir=run_dir,
                    pair_is_active=pair_is_active,
                ),
                "pair_has_issues": _pair_has_issues_from_sources(
                    launcher_result=launcher_result,
                    run_status=run_status,
                ),
                "archive_count": len(retry_archives),
                "latest_archive_status": retry_archives[-1].get("status") if retry_archives else None,
                "latest_archive_rounds": retry_archives[-1].get("rounds") if retry_archives else [],
                "retry_archives": retry_archives,
            }
        )

    rows.sort(
        key=lambda row: (
            pair_order.get(str(row.get("pair_id")), 10**6)
            if selected_pair_ids is not None
            else task_order.get(str(row.get("task_name")), 10**6),
            schema_order.get(str(row.get("schema_id")), 10**6),
            str(row.get("pair_id")),
        )
    )
    return rows


def _active_pairs_from_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    active_by_index: dict[Any, dict[str, Any]] = {}
    for event in events:
        event_type = event.get("event")
        index = event.get("index")
        if event_type == "pair_started":
            active_by_index[index] = event
            continue
        if event_type in {"pair_succeeded", "pair_failed"}:
            active_by_index.pop(index, None)
    return sorted(
        active_by_index.values(),
        key=lambda item: (
            int(item.get("index")) if isinstance(item.get("index"), int) else 10**9,
            str(item.get("pair_id") or ""),
        ),
    )


def _active_pair_from_events(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    active_pairs = _active_pairs_from_events(events)
    return active_pairs[0] if active_pairs else None


def collect_launcher_status(
    launcher_log_dir: Path,
    *,
    now: str | datetime | None = None,
    stale_seconds: int = 900,
) -> dict[str, Any]:
    launcher_log_dir = launcher_log_dir.resolve()
    now_dt = _coerce_datetime(now)
    summary_path = launcher_log_dir / "summary.json"
    events_path = launcher_log_dir / "events.ndjson"
    stdout_log_path = launcher_log_dir / "launcher.stdout.log"
    materialized_root = launcher_log_dir.parent.parent
    manifest = _read_materialized_manifest(materialized_root) or {}
    _schema_highlight_roles, schema_highlight_metadata = _load_schema_highlight_roles(
        materialized_root=materialized_root,
        manifest=manifest,
    )

    summary = _safe_read_json(summary_path)
    events = _read_ndjson(events_path)
    parsed_total_pairs, parsed_task_names, parsed_max_concurrent_pairs = _parse_stdout_metadata(stdout_log_path)
    summary_total_pairs, summary_task_names, summary_pair_ids = _load_selection_from_summary(
        summary if isinstance(summary, dict) else None
    )
    artifact_total_pairs, artifact_task_names, artifact_pair_ids = _load_selection_from_launcher_artifacts(
        launcher_log_dir
    )
    fallback_total_pairs, fallback_task_names, fallback_pair_ids = _load_selection_from_launcher_processes(
        launcher_log_dir
    )
    selected_pair_ids = summary_pair_ids or artifact_pair_ids or fallback_pair_ids
    active_pairs = _active_pairs_from_events(events)
    active_pair = active_pairs[0] if active_pairs else None
    active_pair_details = _collect_active_pair_details(launcher_log_dir, active_pairs)
    primary_active_detail = active_pair_details[0] if active_pair_details else {}
    process_commands = (
        primary_active_detail.get("active_processes")
        if isinstance(primary_active_detail.get("active_processes"), list)
        else []
    )
    active_run_dir_raw = primary_active_detail.get("active_run_dir")
    active_run_dir = Path(active_run_dir_raw).resolve() if isinstance(active_run_dir_raw, str) else None
    active_run_status = (
        primary_active_detail.get("active_run_status")
        if isinstance(primary_active_detail.get("active_run_status"), dict)
        else {}
    )
    pair_detail = (
        primary_active_detail.get("pair_detail")
        if isinstance(primary_active_detail.get("pair_detail"), dict)
        else None
    )
    active_run_activity_dt: datetime | None = None
    for detail in active_pair_details:
        latest_activity_raw = detail.get("latest_activity_at")
        if not isinstance(latest_activity_raw, str):
            continue
        latest_activity_for_pair = _coerce_datetime(latest_activity_raw)
        if active_run_activity_dt is None or latest_activity_for_pair > active_run_activity_dt:
            active_run_activity_dt = latest_activity_for_pair
    latest_event = events[-1] if events else None
    latest_event_at_raw = latest_event.get("observed_at") if isinstance(latest_event, dict) else None
    latest_event_at_dt = None
    if isinstance(latest_event_at_raw, str):
        latest_event_at_dt = _coerce_datetime(latest_event_at_raw)

    if isinstance(summary, dict):
        completed_pairs = int(summary.get("completed_pairs", 0))
        succeeded_pairs = int(summary.get("succeeded_pairs", 0))
        failed_pairs = int(summary.get("failed_pairs", 0))
        selected_task_names = (
            summary_task_names
            or parsed_task_names
            or artifact_task_names
            or fallback_task_names
        )
        max_concurrent_pairs = summary.get("max_concurrent_pairs") or parsed_max_concurrent_pairs
        total_pairs = max(
            summary_total_pairs or 0,
            parsed_total_pairs or 0,
            artifact_total_pairs or 0,
            fallback_total_pairs or 0,
            completed_pairs,
        )
    else:
        succeeded_pairs = sum(1 for event in events if event.get("event") == "pair_succeeded")
        failed_pairs = sum(1 for event in events if event.get("event") == "pair_failed")
        completed_pairs = succeeded_pairs + failed_pairs
        total_pairs = parsed_total_pairs or artifact_total_pairs or fallback_total_pairs or completed_pairs
        selected_task_names = parsed_task_names or artifact_task_names or fallback_task_names
        max_concurrent_pairs = parsed_max_concurrent_pairs
    pair_rows = _collect_pair_rows(
        launcher_log_dir=launcher_log_dir,
        selected_task_names=selected_task_names,
        selected_pair_ids=selected_pair_ids,
        summary=summary if isinstance(summary, dict) else None,
        current_pair_id=active_pair.get("pair_id") if isinstance(active_pair, dict) else None,
        active_pair_ids={
            str(item.get("pair_id"))
            for item in active_pairs
            if isinstance(item.get("pair_id"), str)
        },
        active_run_dir=active_run_dir if isinstance(active_run_dir, Path) else None,
    )
    preflight_risk_audit = _read_preflight_risk_audit(launcher_log_dir)
    event_indices = [
        int(event.get("index"))
        for event in events
        if isinstance(event.get("index"), int)
        and event.get("event") in {"pair_started", "pair_succeeded", "pair_failed"}
    ]
    observed_total_floor = max(
        completed_pairs + len(active_pairs),
        max(event_indices, default=0),
    )
    total_pairs = max(total_pairs, observed_total_floor)
    if selected_pair_ids is not None or not total_pairs:
        total_pairs = max(total_pairs, len(pair_rows))

    issue_pairs = sum(1 for row in pair_rows if row.get("pair_has_issues"))
    archived_retry_count = sum(int(row.get("archive_count") or 0) for row in pair_rows)

    if total_pairs > 0:
        progress_percent = 100.0 * completed_pairs / total_pairs
    else:
        progress_percent = 0.0

    latest_activity_dt = latest_event_at_dt
    if active_run_activity_dt is not None and (
        latest_activity_dt is None or active_run_activity_dt > latest_activity_dt
    ):
        latest_activity_dt = active_run_activity_dt
        synthetic_event = _synthesize_active_run_event(
            active_pair=active_pair if isinstance(active_pair, dict) else None,
            active_run_status=active_run_status,
            pair_detail=pair_detail,
            observed_at=active_run_activity_dt,
        )
        if synthetic_event is not None:
            latest_event = synthetic_event
            latest_event_at_dt = active_run_activity_dt

    if total_pairs > 0 and completed_pairs >= total_pairs:
        if failed_pairs:
            health = "completed_with_failures"
        elif issue_pairs:
            health = "completed_with_issues"
        else:
            health = "completed"
    elif latest_activity_dt is None:
        health = "waiting"
    elif (now_dt - latest_activity_dt).total_seconds() > stale_seconds:
        health = "stalled"
    else:
        health = "running"

    status = {
        "observed_at": _isoformat(now_dt),
        "launcher_log_dir": str(launcher_log_dir),
        "run_label": launcher_log_dir.name,
        "summary_exists": isinstance(summary, dict),
        "health": health,
        "total_pairs": total_pairs,
        "completed_pairs": completed_pairs,
        "succeeded_pairs": succeeded_pairs,
        "failed_pairs": failed_pairs,
        "issue_pairs": issue_pairs,
        "archived_retry_count": archived_retry_count,
        "progress_percent": progress_percent,
        "selected_task_names": selected_task_names,
        "schema_highlight_metadata": schema_highlight_metadata,
        "pair_rows": pair_rows,
        "preflight_risk_audit": preflight_risk_audit,
        "current_pair_id": active_pair.get("pair_id") if isinstance(active_pair, dict) else None,
        "current_pair_index": active_pair.get("index") if isinstance(active_pair, dict) else None,
        "active_pair_count": len(active_pairs),
        "active_pairs": active_pairs,
        "active_pair_details": active_pair_details,
        "max_concurrent_pairs": max_concurrent_pairs,
        "active_run_dir": str(active_run_dir) if isinstance(active_run_dir, Path) else None,
        "active_run_status": active_run_status,
        "active_processes": process_commands,
        "pair_detail": pair_detail,
        "latest_event": latest_event,
        "latest_event_at": _isoformat(latest_event_at_dt) if latest_event_at_dt else None,
        "latest_activity_at": _isoformat(latest_activity_dt) if latest_activity_dt else None,
        "recent_events": events[-10:],
        "last_failure": _last_failure_from_summary(summary) or _last_failure_from_events(events),
    }
    return status


def _health_color(health: str) -> str:
    return {
        "completed": "#22c55e",
        "completed_with_failures": "#c084fc",
        "completed_with_issues": "#f59e0b",
        "running": "#3b82f6",
        "stalled": "#ef4444",
        "waiting": "#a78bfa",
    }.get(health, "#64748b")


def _metric_card(label: str, value: str) -> str:
    return (
        '<div class="metric-card">'
        f'<div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value">{html.escape(value)}</div>'
        "</div>"
    )


def _schema_role_class(role: Any) -> str:
    value = str(role or "").strip().lower()
    if value in {"primary", "secondary", "seed"}:
        return f"schema-{value}"
    return "schema-none"


def _schema_role_badge(row: dict[str, Any]) -> str:
    label = row.get("schema_highlight_label")
    if not label:
        return ""
    role_class = _schema_role_class(row.get("schema_highlight_role"))
    title = row.get("schema_highlight_detail") or row.get("schema_highlight_source") or ""
    return (
        f'<span class="schema-role {role_class}" title="{html.escape(str(title))}">'
        f"{html.escape(str(label))}</span>"
    )


def _format_metric(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.2f}"
    if isinstance(value, int):
        return str(value)
    return str(value)


def _delta_class(value: Any) -> str:
    """Classify a delta value for color coding. Threshold 0.5 avoids noise."""
    if value is None:
        return "num"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "num"
    if numeric > 0.5:
        return "num delta-pos"
    if numeric < -0.5:
        return "num delta-neg"
    return "num delta-zero"


def _heat_class(value: Any) -> str:
    """Bucket a 0-100 score for heatmap background shading."""
    if value is None:
        return "num"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "num"
    if numeric >= 80:
        return "num heat-5"
    if numeric >= 60:
        return "num heat-4"
    if numeric >= 40:
        return "num heat-3"
    if numeric >= 20:
        return "num heat-2"
    return "num heat-1"


def _status_pill_class(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    if text.startswith("completed") and any(
        marker in text for marker in ("runtime exception", "contract issue", "issues")
    ):
        return "pill pill-warn"
    if text in {"succeeded", "success", "completed", "done", "ok"} or text.startswith("completed"):
        return "pill pill-ok"
    if text.startswith("skipped"):
        return "pill pill-other"
    if text in {"failed", "failure", "error"} or text.startswith("failed"):
        return "pill pill-fail"
    if text in {"running", "in_progress", "started", "active"} or text.startswith("running"):
        return "pill pill-run"
    return "pill pill-other"


def _reward_to_percent(value: float | None) -> float | None:
    if value is None:
        return None
    return value * 100.0


def render_dashboard_html(status: dict[str, Any], *, refresh_seconds: int) -> str:
    health = str(status.get("health") or "unknown")
    current_pair = status.get("current_pair_id") or "none"
    active_pairs = status.get("active_pairs") or []
    latest_event = status.get("latest_event") or {}
    last_failure = status.get("last_failure") or {}
    recent_events = status.get("recent_events") or []
    selected_task_names = status.get("selected_task_names") or []
    active_pair_details = status.get("active_pair_details") or []
    pair_detail = status.get("pair_detail") or {}
    pair_rows = status.get("pair_rows") or []
    schema_highlight_metadata = status.get("schema_highlight_metadata") or {}
    preflight_risk_audit = status.get("preflight_risk_audit") or {}
    observed_at = str(status.get("observed_at") or "")
    latest_event_type = latest_event.get("event") or "none"
    latest_event_at = status.get("latest_event_at") or "none"
    latest_activity_at = status.get("latest_activity_at") or "none"
    health_color = _health_color(health)
    active_pair_list = ", ".join(
        str(pair.get("pair_id"))
        for pair in active_pairs
        if isinstance(pair, dict) and pair.get("pair_id")
    ) or "none"

    recent_events_rows = "\n".join(
        (
            "<tr>"
            f'<td class="num">{html.escape(str(event.get("index", "")))}</td>'
            f'<td><span class="{_status_pill_class(event.get("event"))}">{html.escape(str(event.get("event", "")))}</span></td>'
            f"<td>{html.escape(str(event.get('pair_id', '')))}</td>"
            f'<td class="num">{html.escape(str(event.get("observed_at", "")))}</td>'
            "</tr>"
        )
        for event in reversed(recent_events)
    ) or '<tr><td colspan="4">No events yet.</td></tr>'

    failure_block = ""
    if last_failure:
        failure_block = (
            '<section class="panel">'
            "<h2>Last Failure</h2>"
            "<dl>"
            f"<dt>pair_id</dt><dd>{html.escape(str(last_failure.get('pair_id', '')))}</dd>"
            f"<dt>stage</dt><dd>{html.escape(str(last_failure.get('stage', '')))}</dd>"
            f"<dt>returncode</dt><dd>{html.escape(str(last_failure.get('returncode', '')))}</dd>"
            f"<dt>error</dt><dd>{html.escape(str(last_failure.get('error', '')))}</dd>"
            "</dl>"
            "</section>"
        )

    preflight_block = ""
    if isinstance(preflight_risk_audit, dict) and preflight_risk_audit:
        audit_pairs = preflight_risk_audit.get("pairs") or []
        affected_pairs = int(preflight_risk_audit.get("affected_pairs") or 0)
        if affected_pairs:
            rows = []
            for pair in audit_pairs:
                if not isinstance(pair, dict) or not pair.get("risk_count"):
                    continue
                summaries = "; ".join(
                    html.escape(str(item.get("summary", "")))
                    for item in (pair.get("risks") or [])
                    if isinstance(item, dict)
                )
                rows.append(
                    "<tr>"
                    f"<td>{html.escape(str(pair.get('pair_id', '')))}</td>"
                    f"<td><span class=\"{_status_pill_class(str(pair.get('risk_level', '')))}\">{html.escape(str(pair.get('risk_level', '')))}</span></td>"
                    f"<td class=\"num\">{html.escape(str(pair.get('risk_count', '')))}</td>"
                    f"<td>{summaries}</td>"
                    "</tr>"
                )
            rows_html = "\n".join(rows) or '<tr><td colspan="4">No preflight risks detected.</td></tr>'
            preflight_block = (
                '<section class="panel">'
                "<h2>Preflight Risks</h2>"
                "<dl>"
                f"<dt>Docker server</dt><dd>{html.escape(str(preflight_risk_audit.get('docker_server_os') or 'unknown'))}/{html.escape(str(preflight_risk_audit.get('docker_server_arch') or 'unknown'))}</dd>"
                f"<dt>Affected pairs</dt><dd>{html.escape(str(preflight_risk_audit.get('affected_pairs') or 0))}</dd>"
                f"<dt>High / Medium / Low</dt><dd>{html.escape(str(preflight_risk_audit.get('high_risk_pairs') or 0))} / {html.escape(str(preflight_risk_audit.get('medium_risk_pairs') or 0))} / {html.escape(str(preflight_risk_audit.get('low_risk_pairs') or 0))}</dd>"
                "</dl>"
                '<div class="table-wrap"><table>'
                '<thead><tr><th>Pair</th><th>Level</th><th class="num">Count</th><th>Notes</th></tr></thead>'
                f"<tbody>{rows_html}</tbody>"
                "</table></div>"
                "</section>"
            )

    pair_detail_block = ""
    def _stage_cell(state: Any) -> str:
        text = str(state or "")
        pill_class = _status_pill_class(text)
        if pill_class:
            return f'<td><span class="{pill_class}">{html.escape(text)}</span></td>'
        return f"<td>{html.escape(text)}</td>"

    def _render_pair_detail_card(active_detail: dict[str, Any], fallback_index: int) -> str:
        detail = active_detail.get("pair_detail") if isinstance(active_detail.get("pair_detail"), dict) else {}
        round_rows = detail.get("round_rows") or []
        round_rows_html = "\n".join(
            (
                "<tr>"
                f"<td class=\"num num-strong\">R{html.escape(str(row.get('round_index', '')))}</td>"
                f"{_stage_cell(row.get('stage_states', {}).get('executor', ''))}"
                f"{_stage_cell(row.get('stage_states', {}).get('role_a', ''))}"
                f"{_stage_cell(row.get('stage_states', {}).get('role_b', ''))}"
                f"<td>{html.escape(str(row.get('latest_event_type', '')))}</td>"
                f"<td class=\"num\">{html.escape(str(row.get('latest_event_timestamp', '')))}</td>"
                "</tr>"
            )
            for row in round_rows
        ) or '<tr><td colspan="6">No round data yet.</td></tr>'

        pair_id = active_detail.get("pair_id") or "unknown"
        index = active_detail.get("index")
        index_text = str(index) if index not in (None, "") else str(fallback_index)
        run_status = active_detail.get("active_run_status")
        run_status_value = (
            run_status.get("status")
            if isinstance(run_status, dict)
            else None
        ) or "running"
        status_pill_class = _status_pill_class(run_status_value)
        status_pill = (
            f'<span class="{status_pill_class}">{html.escape(str(run_status_value))}</span>'
            if status_pill_class
            else html.escape(str(run_status_value))
        )
        retry_archives = (
            active_detail.get("retry_archives")
            if isinstance(active_detail.get("retry_archives"), list)
            else []
        )
        archive_row_items = []
        for archive in retry_archives:
            if not isinstance(archive, dict):
                continue
            archive_rounds = ", ".join(f"R{round_index}" for round_index in (archive.get("rounds") or []))
            archive_terms = ", ".join(str(term) for term in (archive.get("hard_terms") or []))
            archive_row_items.append(
                "<tr>"
                f"<td>{html.escape(str(archive.get('archive_name') or ''))}</td>"
                f"<td>{html.escape(str(archive.get('status') or 'unknown'))}</td>"
                f"<td>{html.escape(archive_rounds)}</td>"
                f"<td>{html.escape(archive_terms)}</td>"
                f"<td class=\"num\">{html.escape(_format_metric(archive.get('selected_score')))}</td>"
                "</tr>"
            )
        archive_rows_html = "\n".join(archive_row_items)
        archive_block = ""
        if archive_rows_html:
            archive_block = (
                '<div class="table-wrap">'
                "<table>"
                '<thead><tr><th>Archived Retry</th><th>Status</th><th>Rounds</th><th>Hard Terms</th><th class="num">Best Score</th></tr></thead>'
                f"<tbody>{archive_rows_html}</tbody>"
                "</table>"
                "</div>"
            )
        return (
            '<div class="pair-detail-card">'
            f"<h3>#{html.escape(index_text)} {html.escape(str(pair_id))} {status_pill}</h3>"
            "<dl>"
            f"<dt>Task</dt><dd>{html.escape(str(active_detail.get('task_name') or 'unknown'))}</dd>"
            f"<dt>Schema</dt><dd>{html.escape(str(active_detail.get('schema_id') or 'unknown'))}</dd>"
            f"<dt>Current round</dt><dd>{html.escape(str(detail.get('current_round_index')))}</dd>"
            f"<dt>Current stage</dt><dd>{html.escape(str(detail.get('current_stage') or 'none'))}</dd>"
            f"<dt>Last completed stage</dt><dd>{html.escape(str(detail.get('last_completed_stage') or 'none'))}</dd>"
            f"<dt>Archived retries</dt><dd>{html.escape(str(len(retry_archives)))}</dd>"
            f"<dt>Latest activity</dt><dd>{html.escape(str(active_detail.get('latest_activity_at') or 'none'))}</dd>"
            f"<dt>Run dir</dt><dd>{html.escape(str(active_detail.get('active_run_dir') or 'none'))}</dd>"
            "</dl>"
            f"{archive_block}"
            '<div class="table-wrap"><table>'
            '<thead><tr><th class="num">Round</th><th>Executor</th><th>Role A</th><th>Role B</th><th>Latest Event</th><th class="num">Event Time</th></tr></thead>'
            f"<tbody>{round_rows_html}</tbody>"
            "</table></div>"
            "</div>"
        )

    if active_pair_details:
        pair_detail_cards = "\n".join(
            _render_pair_detail_card(active_detail, fallback_index=index)
            for index, active_detail in enumerate(active_pair_details, start=1)
            if isinstance(active_detail, dict)
        )
        pair_detail_block = (
            '<section class="panel">'
            "<h2>Current Pair Details</h2>"
            f"{pair_detail_cards}"
            "</section>"
        )
    elif pair_detail:
        pair_detail_block = (
            '<section class="panel">'
            "<h2>Current Pair Details</h2>"
            f"{_render_pair_detail_card({'pair_id': status.get('current_pair_id'), 'index': status.get('current_pair_index'), 'active_run_dir': status.get('active_run_dir'), 'active_run_status': status.get('active_run_status'), 'pair_detail': pair_detail}, 1)}"
            "</section>"
        )

    pair_row_items: list[str] = []
    previous_task: str | None = None
    group_toggle = False
    for row in pair_rows:
        task_name = str(row.get("task_name", ""))
        if task_name != previous_task:
            group_toggle = not group_toggle
            previous_task = task_name
        group_class = "group-a" if group_toggle else "group-b"
        round_scores = row.get("round_scores") or {}
        r0 = round_scores.get("R0")
        r1 = round_scores.get("R1")
        r2 = round_scores.get("R2")
        r3 = round_scores.get("R3")
        r0_rerun_status = row.get("r0_rerun_status")
        d0 = row.get("delta_vs_c0")
        d1 = row.get("delta_vs_c1")
        dr0 = row.get("delta_vs_r0")
        archive_count = int(row.get("archive_count") or 0)
        role_class = _schema_role_class(row.get("schema_highlight_role"))
        role_badge = _schema_role_badge(row)
        status_value = row.get("pair_status") or ""
        status_pill_class = _status_pill_class(status_value)
        status_cell = (
            f'<span class="{status_pill_class}">{html.escape(str(status_value))}</span>'
            if status_pill_class
            else html.escape(str(status_value))
        )
        pair_row_items.append(
            f'<tr class="{group_class} {role_class}">'
            f'<td class="col-task">{html.escape(task_name)}</td>'
            f'<td class="col-schema {role_class}">{html.escape(str(row.get("schema_id", "")))}</td>'
            f'<td class="col-role">{role_badge}</td>'
            f'<td class="num">{html.escape(_format_metric(row.get("official_c0")))}</td>'
            f'<td class="num">{html.escape(_format_metric(row.get("official_c1")))}</td>'
            f'<td class="{_heat_class(r0)}">{html.escape(_format_metric(r0))}</td>'
            f'<td class="{_heat_class(r1)}">{html.escape(_format_metric(r1))}</td>'
            f'<td class="{_heat_class(r2)}">{html.escape(_format_metric(r2))}</td>'
            f'<td class="{_heat_class(r3)}">{html.escape(_format_metric(r3))}</td>'
            f'<td class="num">{html.escape(str(r0_rerun_status or "0"))}</td>'
            f'<td class="num">{html.escape(str(row.get("selected_round") or ""))}</td>'
            f'<td class="num num-strong">{html.escape(_format_metric(row.get("selected_score")))}</td>'
            f'<td class="{_delta_class(dr0)}">{html.escape(_format_metric(dr0))}</td>'
            f'<td class="{_delta_class(d0)}">{html.escape(_format_metric(d0))}</td>'
            f'<td class="{_delta_class(d1)}">{html.escape(_format_metric(d1))}</td>'
            f'<td class="col-status">{status_cell}</td>'
            f'<td class="num">{html.escape(str(archive_count))}</td>'
            "</tr>"
        )
    pair_rows_html = (
        "\n".join(pair_row_items)
        or '<tr><td colspan="17">No pair rows available.</td></tr>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="{refresh_seconds}">
  <title>SkillX Round0 Monitor</title>
  <style>
    :root {{
      --bg: #000000;
      --panel: #0f0f11;
      --panel-alt: #17171a;
      --panel-hover: #1e1e22;
      --ink: #fafafa;
      --ink-soft: #d4d4d8;
      --muted: #a1a1aa;
      --muted-dim: #71717a;
      --border: #2a2a2e;
      --border-strong: #3f3f46;
      --accent: {health_color};
      --pos: #4ade80;
      --pos-bg: rgba(74, 222, 128, 0.14);
      --pos-border: rgba(74, 222, 128, 0.35);
      --neg: #f87171;
      --neg-bg: rgba(248, 113, 113, 0.14);
      --neg-border: rgba(248, 113, 113, 0.35);
      --run: #60a5fa;
      --run-bg: rgba(96, 165, 250, 0.14);
      --run-border: rgba(96, 165, 250, 0.35);
      --warn: #f59e0b;
      --warn-bg: rgba(245, 158, 11, 0.14);
      --warn-border: rgba(245, 158, 11, 0.35);
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ height: 100%; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
        "Inter", system-ui, sans-serif;
      color: var(--ink);
      background: var(--bg);
      font-size: 14px;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
      color-scheme: dark;
    }}
    main {{
      max-width: 1480px;
      margin: 0 auto;
      padding: 24px 24px 48px;
    }}

    /* Hero */
    .hero {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 20px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }}
    .hero-main {{
      display: flex;
      flex-direction: column;
      gap: 6px;
      min-width: 0;
    }}
    .eyebrow {{
      font-size: 11px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--muted);
      font-weight: 600;
    }}
    h1 {{
      margin: 0;
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.01em;
      font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
      word-break: break-word;
      color: var(--ink);
    }}
    .subhead {{
      color: var(--muted);
      font-size: 13px;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 14px;
      border-radius: 999px;
      background: var(--accent);
      color: #0a0a0b;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      white-space: nowrap;
      border: 1px solid var(--accent);
      box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.4),
        0 0 20px rgba(255, 255, 255, 0.05);
    }}
    .badge::before {{
      content: "";
      width: 8px;
      height: 8px;
      background: #0a0a0b;
      border-radius: 50%;
    }}

    /* Metric cards */
    .metrics {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 12px;
      margin: 0 0 16px;
    }}
    .metric-card, .panel {{
      background: var(--panel);
      border: 1px solid var(--border-strong);
      border-radius: 10px;
      padding: 14px 18px;
      box-shadow: 0 1px 0 rgba(255, 255, 255, 0.02) inset,
        0 4px 12px rgba(0, 0, 0, 0.4);
    }}
    .metric-label {{
      color: var(--muted);
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 6px;
    }}
    .metric-value {{
      font-size: 24px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
      color: var(--ink);
    }}
    .metric-bar {{
      margin-top: 10px;
      height: 6px;
      background: var(--border);
      border-radius: 999px;
      overflow: hidden;
      border: 1px solid var(--border-strong);
    }}
    .metric-bar-fill {{
      height: 100%;
      background: var(--accent);
      border-radius: 999px;
      transition: width 0.3s ease;
      box-shadow: 0 0 8px var(--accent);
    }}
    .metric-card.metric-ok .metric-value {{ color: var(--pos); }}
    .metric-card.metric-bad .metric-value {{ color: var(--neg); }}
    .metric-card.metric-warn .metric-value {{ color: var(--warn); }}

    /* Grid layout for snapshot / tasks */
    .grid {{
      display: grid;
      gap: 16px;
      grid-template-columns: 1.4fr 1fr;
      align-items: start;
      margin-bottom: 16px;
    }}
    .panel h2 {{
      margin: 0 0 14px;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}
    .panel > .subhead {{
      margin: -6px 0 12px;
    }}
    .pair-detail-card {{
      margin: 12px 0 18px;
      padding: 14px;
      border: 1px solid var(--border);
      border-radius: 10px;
      background: var(--panel-alt);
    }}
    .pair-detail-card + .pair-detail-card {{
      margin-top: 16px;
    }}
    .pair-detail-card h3 {{
      margin: 0 0 12px;
      font-size: 13px;
      color: var(--ink);
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
    }}

    dl {{
      display: grid;
      grid-template-columns: max-content 1fr;
      gap: 8px 18px;
      margin: 0;
      font-size: 13px;
    }}
    dt {{
      color: var(--muted);
      font-weight: 500;
    }}
    dd {{
      margin: 0;
      word-break: break-word;
      font-variant-numeric: tabular-nums;
      color: var(--ink-soft);
    }}

    /* Tasks as chips */
    .tasks {{
      margin: 0;
      padding: 0;
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}
    .tasks li {{
      font-size: 12px;
      padding: 4px 10px;
      border-radius: 999px;
      background: var(--panel-alt);
      border: 1px solid var(--border-strong);
      color: var(--ink-soft);
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }}

    /* Tables */
    .table-wrap {{
      overflow-x: auto;
      border-radius: 8px;
      border: 1px solid var(--border-strong);
      max-height: 70vh;
      background: var(--panel);
    }}
    .events-wrap {{
      max-height: 320px;
      overflow-y: auto;
      border-radius: 8px;
      border: 1px solid var(--border-strong);
      background: var(--panel);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
    }}
    th, td {{
      text-align: left;
      padding: 8px 12px;
      border-bottom: 1px solid var(--border);
      font-size: 13px;
      vertical-align: middle;
      white-space: nowrap;
      color: var(--ink-soft);
    }}
    thead th {{
      position: sticky;
      top: 0;
      background: var(--panel-alt);
      color: var(--muted);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      font-size: 11px;
      border-bottom: 2px solid var(--border-strong);
      z-index: 1;
    }}
    tbody tr:last-child td {{ border-bottom: none; }}
    tbody tr.group-a td {{ background: var(--panel); }}
    tbody tr.group-b td {{ background: var(--panel-alt); }}
    tbody tr:hover td {{ background: var(--panel-hover); }}

    td.num, th.num {{
      text-align: right;
      font-variant-numeric: tabular-nums;
      font-family: "SF Mono", Menlo, "Cascadia Code",
        "Roboto Mono", Consolas, monospace;
      font-size: 12px;
    }}
    td.num-strong {{ font-weight: 700; color: var(--ink); }}
    td.col-task {{
      font-weight: 600;
      max-width: 210px;
      overflow: hidden;
      text-overflow: ellipsis;
      color: var(--ink);
    }}
    td.col-schema {{
      color: var(--muted);
      font-size: 12px;
    }}
    td.col-role {{
      min-width: 78px;
    }}
    td.col-status {{ text-align: center; }}

    tbody tr.schema-primary td.col-schema,
    tbody tr.schema-secondary td.col-schema,
    tbody tr.schema-seed td.col-schema {{
      color: var(--ink);
      font-weight: 700;
    }}
    tbody tr.schema-primary td:first-child {{
      box-shadow: inset 4px 0 0 #22c55e;
    }}
    tbody tr.schema-secondary td:first-child {{
      box-shadow: inset 4px 0 0 #38bdf8;
    }}
    tbody tr.schema-seed td:first-child {{
      box-shadow: inset 4px 0 0 #f59e0b;
    }}
    .schema-role {{
      display: inline-block;
      min-width: 42px;
      padding: 3px 8px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 800;
      text-align: center;
      border: 1px solid transparent;
    }}
    .schema-role.schema-primary {{
      background: rgba(34, 197, 94, 0.16);
      color: #86efac;
      border-color: rgba(34, 197, 94, 0.34);
    }}
    .schema-role.schema-secondary {{
      background: rgba(56, 189, 248, 0.16);
      color: #7dd3fc;
      border-color: rgba(56, 189, 248, 0.34);
    }}
    .schema-role.schema-seed {{
      background: rgba(245, 158, 11, 0.16);
      color: #fcd34d;
      border-color: rgba(245, 158, 11, 0.36);
    }}

    /* Delta cells: sign-coded */
    .delta-pos {{
      color: var(--pos) !important;
      background: var(--pos-bg) !important;
      font-weight: 700;
      box-shadow: inset 0 0 0 1px var(--pos-border);
    }}
    .delta-neg {{
      color: var(--neg) !important;
      background: var(--neg-bg) !important;
      font-weight: 700;
      box-shadow: inset 0 0 0 1px var(--neg-border);
    }}
    .delta-zero {{
      color: var(--muted) !important;
    }}

    /* Heatmap for round score cells (dark variants) */
    .heat-1 {{
      background: rgba(248, 113, 113, 0.10) !important;
      color: #fca5a5 !important;
    }}
    .heat-2 {{
      background: rgba(251, 146, 60, 0.10) !important;
      color: #fdba74 !important;
    }}
    .heat-3 {{
      background: rgba(234, 179, 8, 0.10) !important;
      color: #fde047 !important;
    }}
    .heat-4 {{
      background: rgba(132, 204, 22, 0.12) !important;
      color: #bef264 !important;
    }}
    .heat-5 {{
      background: rgba(74, 222, 128, 0.14) !important;
      color: #86efac !important;
    }}

    /* Status pills */
    .pill {{
      display: inline-block;
      padding: 3px 10px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      border: 1px solid transparent;
    }}
    .pill-ok {{
      background: var(--pos-bg);
      color: var(--pos);
      border-color: var(--pos-border);
    }}
    .pill-fail {{
      background: var(--neg-bg);
      color: var(--neg);
      border-color: var(--neg-border);
    }}
    .pill-run {{
      background: var(--run-bg);
      color: var(--run);
      border-color: var(--run-border);
    }}
    .pill-warn {{
      background: var(--warn-bg);
      color: var(--warn);
      border-color: var(--warn-border);
    }}
    .pill-other {{
      background: var(--panel-alt);
      color: var(--muted);
      border-color: var(--border-strong);
    }}

    .footer {{
      margin-top: 24px;
      color: var(--muted-dim);
      font-size: 12px;
      text-align: center;
    }}
    .footer code {{
      background: var(--panel);
      color: var(--ink-soft);
      padding: 2px 8px;
      border-radius: 4px;
      border: 1px solid var(--border-strong);
    }}
    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: var(--panel); }}
    ::-webkit-scrollbar-thumb {{
      background: var(--border-strong);
      border-radius: 6px;
      border: 2px solid var(--panel);
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--muted-dim); }}

    @media (max-width: 1080px) {{
      .metrics {{ grid-template-columns: repeat(2, 1fr); }}
      .grid {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 640px) {{
      main {{ padding: 16px 12px 32px; }}
      .metrics {{ grid-template-columns: 1fr 1fr; }}
      dl {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 22px; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="hero-main">
        <div class="eyebrow">SkillX Round0 Launcher Monitor</div>
        <h1>{html.escape(str(status.get("run_label") or ""))}</h1>
        <div class="subhead">Observed at {html.escape(observed_at)} · Auto-refreshes every {refresh_seconds}s</div>
      </div>
      <span class="badge">{html.escape(health)}</span>
    </section>

    <section class="metrics">
      {_metric_card("Completed", f"{status.get('completed_pairs', 0)} / {status.get('total_pairs', 0)}")}
      <div class="metric-card metric-ok">
        <div class="metric-label">Succeeded</div>
        <div class="metric-value">{html.escape(str(status.get("succeeded_pairs", 0)))}</div>
      </div>
      <div class="metric-card{' metric-warn' if int(status.get('issue_pairs', 0) or 0) > 0 else ''}">
        <div class="metric-label">Issues</div>
        <div class="metric-value">{html.escape(str(status.get("issue_pairs", 0)))}</div>
      </div>
      <div class="metric-card{' metric-bad' if int(status.get('failed_pairs', 0) or 0) > 0 else ''}">
        <div class="metric-label">Failed</div>
        <div class="metric-value">{html.escape(str(status.get("failed_pairs", 0)))}</div>
      </div>
      <div class="metric-card{' metric-warn' if int(status.get('archived_retry_count', 0) or 0) > 0 else ''}">
        <div class="metric-label">Archived Retries</div>
        <div class="metric-value">{html.escape(str(status.get("archived_retry_count", 0)))}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Progress</div>
        <div class="metric-value">{float(status.get('progress_percent', 0.0)):.1f}%</div>
        <div class="metric-bar"><div class="metric-bar-fill" style="width: {max(0.0, min(100.0, float(status.get('progress_percent', 0.0)))):.1f}%"></div></div>
      </div>
    </section>

    <section class="grid">
      <section class="panel">
        <h2>Run Snapshot</h2>
        <dl>
          <dt>Current pair</dt><dd>{html.escape(str(current_pair))}</dd>
          <dt>Current index</dt><dd>{html.escape(str(status.get("current_pair_index") or "none"))}</dd>
          <dt>Max concurrency</dt><dd>{html.escape(str(status.get("max_concurrent_pairs") or "unknown"))}</dd>
          <dt>Active pairs</dt><dd>{html.escape(str(status.get("active_pair_count") or 0))}</dd>
          <dt>Active pair list</dt><dd>{html.escape(active_pair_list)}</dd>
          <dt>Latest event</dt><dd>{html.escape(str(latest_event_type))}</dd>
          <dt>Latest event at</dt><dd>{html.escape(str(latest_event_at))}</dd>
          <dt>Latest activity at</dt><dd>{html.escape(str(latest_activity_at))}</dd>
          <dt>Active run dir</dt><dd>{html.escape(str(status.get("active_run_dir") or "none"))}</dd>
          <dt>Summary file</dt><dd>{html.escape("present" if status.get("summary_exists") else "waiting for first completed pair")}</dd>
          <dt>Launcher log dir</dt><dd>{html.escape(str(status.get("launcher_log_dir") or ""))}</dd>
        </dl>
      </section>

      <section class="panel">
        <h2>Tasks</h2>
        <ul class="tasks">
          {''.join(f'<li>{html.escape(str(task_name))}</li>' for task_name in selected_task_names) or '<li>unknown</li>'}
        </ul>
      </section>
    </section>

        {failure_block}
        {preflight_block}
        {pair_detail_block}

    <section class="panel">
      <h2>Task / Pair Results</h2>
      <div class="subhead">Official C0/C1 scores are native 0-100 values. Local R0-R3 rewards are normalized 0-1 internally and shown here on a 0-100 scale; R0 uses the final baseline-rerun attempt when present.</div>
      <div class="subhead">Schema highlights: {html.escape(str(schema_highlight_metadata.get("legend") or "none"))}</div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Task</th>
              <th>Schema</th>
              <th>Role</th>
              <th class="num">C0</th>
              <th class="num">C1</th>
              <th class="num">R0</th>
              <th class="num">R1</th>
              <th class="num">R2</th>
              <th class="num">R3</th>
              <th class="num">R0 reruns</th>
              <th class="num">Best Round</th>
              <th class="num">Best Score</th>
              <th class="num">Δ vs R0</th>
              <th class="num">Δ vs C0</th>
              <th class="num">Δ vs C1</th>
              <th>Status</th>
              <th class="num">Retries</th>
            </tr>
          </thead>
          <tbody>
            {pair_rows_html}
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <h2>Recent Events</h2>
      <div class="events-wrap">
        <table>
          <thead>
            <tr>
              <th class="num">Index</th>
              <th>Event</th>
              <th>Pair</th>
              <th>Observed At</th>
            </tr>
          </thead>
          <tbody>
            {recent_events_rows}
          </tbody>
        </table>
      </div>
    </section>

    <div class="footer">JSON API: <code>/api/status</code></div>
  </main>
</body>
</html>
"""


def build_server(
    *,
    launcher_log_dir: Path,
    host: str,
    port: int,
    refresh_seconds: int,
    stale_seconds: int,
) -> ThreadingHTTPServer:
    launcher_log_dir = launcher_log_dir.resolve()

    class MonitorHandler(BaseHTTPRequestHandler):
        def _write_json(self, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _write_html(self, body_text: str) -> None:
            body = body_text.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/api/status":
                self._write_json(
                    collect_launcher_status(
                        launcher_log_dir,
                        stale_seconds=stale_seconds,
                    )
                )
                return
            if self.path in {"/", "/index.html"}:
                status = collect_launcher_status(
                    launcher_log_dir,
                    stale_seconds=stale_seconds,
                )
                self._write_html(
                    render_dashboard_html(
                        status,
                        refresh_seconds=refresh_seconds,
                    )
                )
                return
            self.send_error(404, "Not Found")

        def log_message(self, format: str, *args: object) -> None:
            return

    return ThreadingHTTPServer((host, port), MonitorHandler)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Serve a local HTML dashboard for a SkillX round0 launcher run."
    )
    parser.add_argument("--launcher-log-dir", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--refresh-seconds", type=int, default=15)
    parser.add_argument("--stale-seconds", type=int, default=900)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    server = build_server(
        launcher_log_dir=args.launcher_log_dir,
        host=args.host,
        port=args.port,
        refresh_seconds=args.refresh_seconds,
        stale_seconds=args.stale_seconds,
    )
    url = f"http://{args.host}:{args.port}/"
    print(f"Serving round0 monitor for {args.launcher_log_dir.resolve()}")
    print(f"Open: {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down monitor.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
