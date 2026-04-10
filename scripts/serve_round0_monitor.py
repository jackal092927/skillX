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
import subprocess
from typing import Any


SELECTED_LINE_PATTERN = re.compile(r"Selected\s+(\d+)\s+task\(s\)\s+->\s+(\d+)\s+pair\(s\)")
RUN_STATUS_PATTERN = re.compile(r"^- ([a-z_]+): `?(.*?)`?$")
OUTPUT_DIR_PATTERN = re.compile(r"--output-dir\s+(\S+)")
ROUND_NAME_PATTERN = re.compile(r"^round-(\d+)$")
ROUND_STAGE_ORDER = ("executor", "role_a", "role_b")


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


def _parse_stdout_metadata(stdout_log_path: Path) -> tuple[int | None, list[str]]:
    if not stdout_log_path.exists():
        return None, []

    total_pairs: int | None = None
    selected_task_names: list[str] = []
    for raw_line in stdout_log_path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = SELECTED_LINE_PATTERN.search(line)
        if match:
            total_pairs = int(match.group(2))
            continue
        if line.startswith("Tasks:"):
            selected_task_names = [
                part.strip()
                for part in line.removeprefix("Tasks:").split(",")
                if part.strip()
            ]
    return total_pairs, selected_task_names


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


def _resolve_pair_run_dir_for_label(pair_spec: dict[str, Any], run_label: str) -> Path:
    pair_dir = Path(str(pair_spec.get("pair_dir") or "")).resolve()
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


def _read_refine_summary(run_dir: Path) -> dict[str, Any] | None:
    task_root = _find_refine_task_root(run_dir)
    if task_root is None:
        return None
    payload = _safe_read_json(task_root / "refine_summary.json")
    return payload if isinstance(payload, dict) else None


def _pair_status_from_sources(
    *,
    launcher_result: dict[str, Any] | None,
    run_status: dict[str, str],
    run_dir: Path,
) -> str:
    if isinstance(launcher_result, dict) and isinstance(launcher_result.get("status"), str):
        return str(launcher_result["status"])
    run_status_value = run_status.get("status")
    if isinstance(run_status_value, str) and run_status_value:
        return run_status_value
    if run_dir.exists():
        return "running"
    return "pending"


def _collect_pair_rows(
    *,
    launcher_log_dir: Path,
    selected_task_names: list[str],
    summary: dict[str, Any] | None,
    current_pair_id: str | None,
    active_run_dir: Path | None,
) -> list[dict[str, Any]]:
    materialized_root = launcher_log_dir.parent.parent
    manifest = _read_materialized_manifest(materialized_root) or {}
    schema_ids = [
        item for item in (manifest.get("schema_ids") or []) if isinstance(item, str)
    ]
    pair_specs = _read_pair_specs(materialized_root)
    task_order = {task_name: index for index, task_name in enumerate(selected_task_names)}
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
        if task_name not in task_order:
            continue

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
            run_dir = _resolve_pair_run_dir_for_label(pair_spec, launcher_log_dir.name)
        run_status = _parse_run_status(run_dir / "RUN_STATUS.md")
        round_scores_raw = _read_round_score_map(run_dir)
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

        rows.append(
            {
                "pair_id": pair_id,
                "task_name": task_name,
                "schema_id": schema_id,
                "official_c0": official_c0,
                "official_c1": official_c1,
                "round_rewards_raw": {
                    f"R{round_index}": round_scores_raw.get(round_index)
                    for round_index in range(0, 4)
                },
                "round_scores": round_scores,
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
                "pair_status": _pair_status_from_sources(
                    launcher_result=launcher_result,
                    run_status=run_status,
                    run_dir=run_dir,
                ),
            }
        )

    rows.sort(
        key=lambda row: (
            task_order.get(str(row.get("task_name")), 10**6),
            schema_order.get(str(row.get("schema_id")), 10**6),
            str(row.get("pair_id")),
        )
    )
    return rows


def _active_pair_from_events(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    active_pair: dict[str, Any] | None = None
    for event in events:
        event_type = event.get("event")
        if event_type == "pair_started":
            active_pair = event
            continue
        if event_type in {"pair_succeeded", "pair_failed"} and active_pair is not None:
            if active_pair.get("index") == event.get("index"):
                active_pair = None
    return active_pair


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

    summary = _safe_read_json(summary_path)
    events = _read_ndjson(events_path)
    parsed_total_pairs, parsed_task_names = _parse_stdout_metadata(stdout_log_path)
    active_pair = _active_pair_from_events(events)
    process_commands = _scan_active_process_commands(
        active_pair.get("pair_id") if isinstance(active_pair, dict) else None,
        launcher_log_dir.name,
    )
    active_run_dir = _resolve_active_run_dir(
        launcher_log_dir,
        active_pair.get("pair_id") if isinstance(active_pair, dict) else None,
    )
    if active_run_dir is None:
        active_run_dir = _resolve_active_run_dir_from_processes(process_commands)
    active_run_status = (
        _parse_run_status(active_run_dir / "RUN_STATUS.md")
        if isinstance(active_run_dir, Path)
        else {}
    )
    pair_detail = _collect_pair_detail(active_run_dir) if isinstance(active_run_dir, Path) else None
    active_run_mtime = _latest_mtime(active_run_dir) if isinstance(active_run_dir, Path) else None
    active_run_activity_dt = (
        datetime.fromtimestamp(active_run_mtime, tz=timezone.utc)
        if active_run_mtime is not None
        else None
    )
    latest_event = events[-1] if events else None
    latest_event_at_raw = latest_event.get("observed_at") if isinstance(latest_event, dict) else None
    latest_event_at_dt = None
    if isinstance(latest_event_at_raw, str):
        latest_event_at_dt = _coerce_datetime(latest_event_at_raw)

    if isinstance(summary, dict):
        summary_total_pairs = int(summary.get("total_pairs", 0))
        completed_pairs = int(summary.get("completed_pairs", 0))
        succeeded_pairs = int(summary.get("succeeded_pairs", 0))
        failed_pairs = int(summary.get("failed_pairs", 0))
        selected_task_names = summary.get("selected_task_names") or parsed_task_names
        total_pairs = max(summary_total_pairs, parsed_total_pairs or 0, completed_pairs)
    else:
        succeeded_pairs = sum(1 for event in events if event.get("event") == "pair_succeeded")
        failed_pairs = sum(1 for event in events if event.get("event") == "pair_failed")
        completed_pairs = succeeded_pairs + failed_pairs
        total_pairs = parsed_total_pairs or completed_pairs
        selected_task_names = parsed_task_names
    pair_rows = _collect_pair_rows(
        launcher_log_dir=launcher_log_dir,
        selected_task_names=selected_task_names,
        summary=summary if isinstance(summary, dict) else None,
        current_pair_id=active_pair.get("pair_id") if isinstance(active_pair, dict) else None,
        active_run_dir=active_run_dir if isinstance(active_run_dir, Path) else None,
    )

    if total_pairs > 0:
        progress_percent = 100.0 * completed_pairs / total_pairs
    else:
        progress_percent = 0.0

    latest_activity_dt = latest_event_at_dt
    if active_run_activity_dt is not None and (
        latest_activity_dt is None or active_run_activity_dt > latest_activity_dt
    ):
        latest_activity_dt = active_run_activity_dt

    if total_pairs > 0 and completed_pairs >= total_pairs:
        health = "completed_with_failures" if failed_pairs else "completed"
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
        "progress_percent": progress_percent,
        "selected_task_names": selected_task_names,
        "pair_rows": pair_rows,
        "current_pair_id": active_pair.get("pair_id") if isinstance(active_pair, dict) else None,
        "current_pair_index": active_pair.get("index") if isinstance(active_pair, dict) else None,
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
        "completed": "#1b5e20",
        "completed_with_failures": "#8e24aa",
        "running": "#1565c0",
        "stalled": "#b71c1c",
        "waiting": "#6d4c41",
    }.get(health, "#37474f")


def _metric_card(label: str, value: str) -> str:
    return (
        '<div class="metric-card">'
        f'<div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value">{html.escape(value)}</div>'
        "</div>"
    )


def _format_metric(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.2f}"
    if isinstance(value, int):
        return str(value)
    return str(value)


def _reward_to_percent(value: float | None) -> float | None:
    if value is None:
        return None
    return value * 100.0


def render_dashboard_html(status: dict[str, Any], *, refresh_seconds: int) -> str:
    health = str(status.get("health") or "unknown")
    current_pair = status.get("current_pair_id") or "none"
    latest_event = status.get("latest_event") or {}
    last_failure = status.get("last_failure") or {}
    recent_events = status.get("recent_events") or []
    selected_task_names = status.get("selected_task_names") or []
    pair_detail = status.get("pair_detail") or {}
    round_rows = pair_detail.get("round_rows") or []
    pair_rows = status.get("pair_rows") or []
    observed_at = str(status.get("observed_at") or "")
    latest_event_type = latest_event.get("event") or "none"
    latest_event_at = status.get("latest_event_at") or "none"
    latest_activity_at = status.get("latest_activity_at") or "none"
    health_color = _health_color(health)

    recent_events_rows = "\n".join(
        (
            "<tr>"
            f"<td>{html.escape(str(event.get('index', '')))}</td>"
            f"<td>{html.escape(str(event.get('event', '')))}</td>"
            f"<td>{html.escape(str(event.get('pair_id', '')))}</td>"
            f"<td>{html.escape(str(event.get('observed_at', '')))}</td>"
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

    pair_detail_block = ""
    if pair_detail:
        round_rows_html = "\n".join(
            (
                "<tr>"
                f"<td>R{html.escape(str(row.get('round_index', '')))}</td>"
                f"<td>{html.escape(str(row.get('stage_states', {}).get('executor', '')))}</td>"
                f"<td>{html.escape(str(row.get('stage_states', {}).get('role_a', '')))}</td>"
                f"<td>{html.escape(str(row.get('stage_states', {}).get('role_b', '')))}</td>"
                f"<td>{html.escape(str(row.get('latest_event_type', '')))}</td>"
                f"<td>{html.escape(str(row.get('latest_event_timestamp', '')))}</td>"
                "</tr>"
            )
            for row in round_rows
        ) or '<tr><td colspan="6">No round data yet.</td></tr>'
        pair_detail_block = (
            '<section class="panel">'
            "<h2>Current Pair Detail</h2>"
            "<dl>"
            f"<dt>Current round</dt><dd>{html.escape(str(pair_detail.get('current_round_index')))}</dd>"
            f"<dt>Current stage</dt><dd>{html.escape(str(pair_detail.get('current_stage') or 'none'))}</dd>"
            f"<dt>Last completed stage</dt><dd>{html.escape(str(pair_detail.get('last_completed_stage') or 'none'))}</dd>"
            "</dl>"
            '<div class="table-wrap"><table>'
            "<thead><tr><th>Round</th><th>Executor</th><th>Role A</th><th>Role B</th><th>Latest Event</th><th>Event Time</th></tr></thead>"
            f"<tbody>{round_rows_html}</tbody>"
            "</table></div>"
            "</section>"
        )

    pair_rows_html = "\n".join(
        (
            "<tr>"
            f"<td>{html.escape(str(row.get('task_name', '')))}</td>"
            f"<td>{html.escape(str(row.get('schema_id', '')))}</td>"
            f"<td>{html.escape(_format_metric(row.get('official_c0')))}</td>"
            f"<td>{html.escape(_format_metric(row.get('official_c1')))}</td>"
            f"<td>{html.escape(_format_metric((row.get('round_scores') or {}).get('R0')))}</td>"
            f"<td>{html.escape(_format_metric((row.get('round_scores') or {}).get('R1')))}</td>"
            f"<td>{html.escape(_format_metric((row.get('round_scores') or {}).get('R2')))}</td>"
            f"<td>{html.escape(_format_metric((row.get('round_scores') or {}).get('R3')))}</td>"
            f"<td>{html.escape(str(row.get('selected_round') or ''))}</td>"
            f"<td>{html.escape(_format_metric(row.get('selected_score')))}</td>"
            f"<td>{html.escape(_format_metric(row.get('delta_vs_c0')))}</td>"
            f"<td>{html.escape(_format_metric(row.get('delta_vs_c1')))}</td>"
            f"<td>{html.escape(str(row.get('pair_status') or ''))}</td>"
            "</tr>"
        )
        for row in pair_rows
    ) or '<tr><td colspan="13">No pair rows available.</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="{refresh_seconds}">
  <title>SkillX Round0 Monitor</title>
  <style>
    :root {{
      --bg: #f7f4ea;
      --panel: #fffdf8;
      --ink: #16202a;
      --muted: #57646f;
      --border: #d8d0c2;
      --accent: {health_color};
      --accent-soft: #e8f0ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, #fff5d6 0, transparent 28%),
        linear-gradient(180deg, #f4efe3 0%, var(--bg) 100%);
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 28px 20px 40px;
    }}
    .hero {{
      display: grid;
      gap: 12px;
      margin-bottom: 20px;
    }}
    .eyebrow {{
      font-size: 12px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    h1 {{
      margin: 0;
      font-size: 40px;
      line-height: 1.05;
    }}
    .subhead {{
      color: var(--muted);
      font-size: 16px;
    }}
    .badge {{
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      background: var(--accent);
      color: white;
      font-size: 13px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 12px;
      margin: 18px 0 22px;
    }}
    .metric-card, .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 16px 18px;
      box-shadow: 0 10px 30px rgba(22, 32, 42, 0.06);
    }}
    .metric-label {{
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}
    .metric-value {{
      font-size: 28px;
      font-weight: 700;
    }}
    .grid {{
      display: grid;
      gap: 16px;
      grid-template-columns: 1.25fr 1fr;
      align-items: start;
    }}
    .panel h2 {{
      margin: 0 0 12px;
      font-size: 22px;
    }}
    dl {{
      display: grid;
      grid-template-columns: 150px 1fr;
      gap: 8px 12px;
      margin: 0;
    }}
    dt {{
      color: var(--muted);
      font-size: 14px;
    }}
    dd {{
      margin: 0;
      word-break: break-word;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      text-align: left;
      padding: 10px 8px;
      border-bottom: 1px solid var(--border);
      font-size: 14px;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-size: 12px;
    }}
    .tasks {{
      margin: 0;
      padding-left: 20px;
    }}
    .table-wrap {{
      overflow-x: auto;
    }}
    .footer {{
      margin-top: 16px;
      color: var(--muted);
      font-size: 13px;
    }}
    @media (max-width: 860px) {{
      .grid {{
        grid-template-columns: 1fr;
      }}
      dl {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="eyebrow">SkillX Round0 Launcher Monitor</div>
      <h1>{html.escape(str(status.get("run_label") or ""))}</h1>
      <div><span class="badge">{html.escape(health)}</span></div>
      <div class="subhead">Observed at {html.escape(observed_at)}. This page refreshes every {refresh_seconds} seconds.</div>
    </section>

    <section class="metrics">
      {_metric_card("Completed", f"{status.get('completed_pairs', 0)} / {status.get('total_pairs', 0)}")}
      {_metric_card("Succeeded", str(status.get("succeeded_pairs", 0)))}
      {_metric_card("Failed", str(status.get("failed_pairs", 0)))}
      {_metric_card("Progress", f"{float(status.get('progress_percent', 0.0)):.1f}%")}
    </section>

    <section class="grid">
      <section class="panel">
        <h2>Run Snapshot</h2>
        <dl>
          <dt>Current pair</dt><dd>{html.escape(str(current_pair))}</dd>
          <dt>Current index</dt><dd>{html.escape(str(status.get("current_pair_index") or "none"))}</dd>
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
    {pair_detail_block}

    <section class="panel">
      <h2>Task / Pair Results</h2>
      <div class="subhead">Official C0/C1 scores are native 0-100 values. Local R0-R3 rewards are normalized 0-1 internally and shown here on a 0-100 scale; deltas are percentage-point differences.</div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Task</th>
              <th>Schema</th>
              <th>C0</th>
              <th>C1</th>
              <th>R0</th>
              <th>R1</th>
              <th>R2</th>
              <th>R3</th>
              <th>Best Round</th>
              <th>Best Score</th>
              <th>Δ vs C0</th>
              <th>Δ vs C1</th>
              <th>Status</th>
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
      <table>
        <thead>
          <tr>
            <th>Index</th>
            <th>Event</th>
            <th>Pair</th>
            <th>Observed At</th>
          </tr>
        </thead>
        <tbody>
          {recent_events_rows}
        </tbody>
      </table>
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
