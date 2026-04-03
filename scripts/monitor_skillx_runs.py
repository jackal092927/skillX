#!/usr/bin/env python3
"""Lightweight watcher for long-running SkillX C4 runs."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

import sys

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from skillx.io_utils import ensure_dir, read_json, write_json


RUN_STATUS_PATTERN = re.compile(r"^- ([a-z_]+): `?(.*?)`?$")


@dataclass(frozen=True)
class MonitorPaths:
    output_dir: Path
    summary_json: Path
    summary_md: Path
    state_json: Path
    log_path: Path


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_read_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return read_json(path)
    except json.JSONDecodeError:
        return None


def _parse_run_status(path: Path) -> dict[str, str]:
    payload: dict[str, str] = {}
    if not path.exists():
        return payload
    for line in path.read_text().splitlines():
        match = RUN_STATUS_PATTERN.match(line)
        if match:
            payload[match.group(1)] = match.group(2)
    return payload


def _parse_job_result(job_dir: Path) -> dict[str, Any] | None:
    result_path = job_dir / "result.json"
    payload = _safe_read_json(result_path)
    if not isinstance(payload, dict):
        return None
    evals = payload.get("stats", {}).get("evals", {})
    reward_mean = None
    exception_stats: dict[str, Any] = {}
    if evals:
        _, eval_payload = next(iter(evals.items()))
        metrics = eval_payload.get("metrics") or []
        if metrics:
            reward_mean = metrics[0].get("mean")
        exception_stats = eval_payload.get("exception_stats") or {}
    return {
        "result_path": str(result_path),
        "reward": reward_mean,
        "exception_stats": exception_stats,
    }


def _existing_nested_tune_result(round_dir_path: Path) -> dict[str, Any] | None:
    tune_root = round_dir_path / "tune_check"
    top_level_result = _safe_read_json(tune_root / "result.json")
    if isinstance(top_level_result, dict):
        return top_level_result
    config_payload = _safe_read_json(tune_root / "config.json")
    if not isinstance(config_payload, dict):
        return None
    job_name = config_payload.get("job_name")
    if not isinstance(job_name, str):
        return None
    return _parse_job_result(tune_root / job_name)


def _find_task_root(run_dir: Path) -> Path | None:
    refine_root = run_dir / "refine"
    if not refine_root.exists():
        return None
    task_roots = sorted(path for path in refine_root.iterdir() if path.is_dir())
    if len(task_roots) != 1:
        return None
    return task_roots[0]


def _collect_round_rows(task_root: Path) -> list[dict[str, Any]]:
    rounds_root = task_root / "rounds"
    if not rounds_root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for round_path in sorted(path for path in rounds_root.iterdir() if path.is_dir()):
        try:
            round_index = int(round_path.name.split("-", 1)[1])
        except (IndexError, ValueError):
            continue
        tune_result_path = round_path / "tune_check" / "result.json"
        tune_result = _existing_nested_tune_result(round_path)
        rows.append(
            {
                "round_index": round_index,
                "round_dir": str(round_path),
                "has_skill_artifact": (round_path / f"round_{round_index}_skill.md").exists(),
                "tune_result_path": (
                    tune_result.get("result_path")
                    if isinstance(tune_result, dict)
                    else (str(tune_result_path) if tune_result_path.exists() else None)
                ),
                "tune_reward": tune_result.get("reward") if isinstance(tune_result, dict) else None,
                "tune_exceptions": (tune_result or {}).get("exception_stats", {}) if isinstance(tune_result, dict) else {},
            }
        )
        if rows[-1]["tune_result_path"] is None and isinstance(tune_result, dict):
            rows[-1]["tune_result_path"] = str(tune_result_path)
    return rows


def _collect_refine_job_rows(task_root: Path) -> list[dict[str, Any]]:
    jobs_root = task_root / "harbor_jobs"
    if not jobs_root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for job_dir in sorted(path for path in jobs_root.iterdir() if path.is_dir()):
        top_result_path = job_dir / "result.json"
        top_payload = _safe_read_json(top_result_path)
        trial_rows: list[dict[str, Any]] = []
        for trial_dir in sorted(path for path in job_dir.iterdir() if path.is_dir()):
            trial_result = _safe_read_json(trial_dir / "result.json")
            if not isinstance(trial_result, dict):
                continue
            trial_rows.append(
                {
                    "trial_dir": str(trial_dir),
                    "exception_info": trial_result.get("exception_info"),
                }
            )
        rows.append(
            {
                "job_dir": str(job_dir),
                "job_name": job_dir.name,
                "has_job_result": top_result_path.exists(),
                "job_errors": (
                    top_payload.get("stats", {}).get("n_errors")
                    if isinstance(top_payload, dict)
                    else None
                ),
                "trial_rows": trial_rows,
            }
        )
    return rows


def _scan_active_harbor_processes(run_dir: Path) -> list[str]:
    proc = subprocess.run(
        ["ps", "-axo", "command"],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    needle = str(run_dir)
    return [
        line.strip()
        for line in proc.stdout.splitlines()
        if line.strip().startswith("uv run harbor run -c ") and needle in line
    ]


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


def summarize_c4_run(run_dir: Path, *, previous_state: dict[str, Any] | None = None) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    run_status = _parse_run_status(run_dir / "RUN_STATUS.md")
    task_root = _find_task_root(run_dir)
    if task_root is None:
        return {
            "run_dir": str(run_dir),
            "run_id": run_dir.name,
            "state": "invalid",
            "reason": "missing_or_ambiguous_refine_task_root",
            "observed_at": _timestamp(),
        }

    round_rows = _collect_round_rows(task_root)
    refine_jobs = _collect_refine_job_rows(task_root)
    refine_summary = _safe_read_json(task_root / "refine_summary.json")
    manifest = _safe_read_json(task_root / "bundle_manifest.json")
    active_processes = _scan_active_harbor_processes(run_dir)
    latest_mtime = _latest_mtime(run_dir)

    latest_round_materialized = max((row["round_index"] for row in round_rows), default=None)
    latest_tune_completed = max(
        (row["round_index"] for row in round_rows if row["tune_result_path"]),
        default=None,
    )
    latest_reward = None
    if latest_tune_completed is not None:
        latest_row = max(
            (row for row in round_rows if row["tune_result_path"]),
            key=lambda row: row["round_index"],
        )
        latest_reward = latest_row["tune_reward"]

    tune_exception_rounds = [
        row["round_index"] for row in round_rows if row["tune_exceptions"]
    ]
    refine_exception_jobs = [
        row["job_name"]
        for row in refine_jobs
        if any(trial.get("exception_info") for trial in row["trial_rows"])
    ]
    incomplete_refine_jobs = [
        row["job_name"] for row in refine_jobs if not row["has_job_result"]
    ]

    if run_status.get("status") == "completed":
        phase = "completed"
    elif tune_exception_rounds or refine_exception_jobs:
        phase = "blocked"
    elif incomplete_refine_jobs or active_processes:
        phase = "running"
    elif latest_round_materialized is not None and latest_tune_completed != latest_round_materialized:
        phase = "awaiting_tune_check"
    else:
        phase = "idle"

    progress_signature = {
        "latest_round_materialized": latest_round_materialized,
        "latest_tune_completed": latest_tune_completed,
        "latest_reward": latest_reward,
        "n_rounds": len(round_rows),
        "n_refine_jobs": len(refine_jobs),
        "latest_mtime": latest_mtime,
        "phase": phase,
    }
    previous_signature = (previous_state or {}).get("progress_signature")
    progress_state = "new_progress" if progress_signature != previous_signature else "unchanged"

    observed = {
        "run_dir": str(run_dir),
        "run_id": run_dir.name,
        "task_id": task_root.name,
        "status": run_status.get("status", "unknown"),
        "phase": phase,
        "round_budget": (manifest or {}).get("round_budget"),
        "latest_round_materialized": latest_round_materialized,
        "latest_tune_completed": latest_tune_completed,
        "latest_reward": latest_reward,
        "tune_exception_rounds": tune_exception_rounds,
        "refine_exception_jobs": refine_exception_jobs,
        "incomplete_refine_jobs": incomplete_refine_jobs,
        "active_harbor_processes": active_processes,
        "selected_round": (refine_summary or {}).get("selected", {}).get("round_index")
        if isinstance(refine_summary, dict)
        else None,
        "selected_reward": (refine_summary or {}).get("selected", {}).get("reward")
        if isinstance(refine_summary, dict)
        else None,
        "latest_change_at": (
            datetime.fromtimestamp(latest_mtime, tz=timezone.utc).isoformat()
            if latest_mtime is not None
            else None
        ),
        "progress_state": progress_state,
        "progress_signature": progress_signature,
        "round_rows": round_rows,
        "observed_at": _timestamp(),
    }
    return observed


def build_summary_markdown(summary_rows: list[dict[str, Any]], generated_at: str) -> str:
    lines = [
        "# SkillX C4 Watcher Summary",
        "",
        f"- generated_at: `{generated_at}`",
        "",
        "| run | task | status | phase | latest round | latest tune | latest reward | progress | exceptions |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in summary_rows:
        exceptions: list[str] = []
        if row.get("tune_exception_rounds"):
            exceptions.append("tune")
        if row.get("refine_exception_jobs"):
            exceptions.append("refine")
        lines.append(
            "| {run_id} | {task_id} | {status} | {phase} | {latest_round} | {latest_tune} | {latest_reward} | {progress} | {exceptions} |".format(
                run_id=row.get("run_id", "-"),
                task_id=row.get("task_id", "-"),
                status=row.get("status", "-"),
                phase=row.get("phase", "-"),
                latest_round=row.get("latest_round_materialized", "-"),
                latest_tune=row.get("latest_tune_completed", "-"),
                latest_reward=row.get("latest_reward", "-"),
                progress=row.get("progress_state", "-"),
                exceptions=",".join(exceptions) if exceptions else "-",
            )
        )
    lines.extend(["", "## Details", ""])
    for row in summary_rows:
        lines.extend(
            [
                f"### {row.get('run_id', '-')}",
                f"- task_id: `{row.get('task_id', '-')}`",
                f"- run_dir: `{row.get('run_dir', '-')}`",
                f"- status: `{row.get('status', '-')}`",
                f"- phase: `{row.get('phase', '-')}`",
                f"- latest_round_materialized: `{row.get('latest_round_materialized')}`",
                f"- latest_tune_completed: `{row.get('latest_tune_completed')}`",
                f"- latest_reward: `{row.get('latest_reward')}`",
                f"- selected_round: `{row.get('selected_round')}`",
                f"- selected_reward: `{row.get('selected_reward')}`",
                f"- latest_change_at: `{row.get('latest_change_at')}`",
                f"- active_harbor_processes: `{len(row.get('active_harbor_processes', []))}`",
                f"- incomplete_refine_jobs: `{', '.join(row.get('incomplete_refine_jobs', [])) or '-'}`",
                f"- tune_exception_rounds: `{', '.join(str(x) for x in row.get('tune_exception_rounds', [])) or '-'}`",
                f"- refine_exception_jobs: `{', '.join(row.get('refine_exception_jobs', [])) or '-'}`",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def ensure_monitor_paths(output_dir: Path) -> MonitorPaths:
    output_dir = ensure_dir(output_dir)
    return MonitorPaths(
        output_dir=output_dir,
        summary_json=output_dir / "watch_summary.json",
        summary_md=output_dir / "watch_summary.md",
        state_json=output_dir / "watch_state.json",
        log_path=output_dir / "watch_log.ndjson",
    )


def write_iteration(paths: MonitorPaths, summary_rows: list[dict[str, Any]], generated_at: str) -> None:
    payload = {"generated_at": generated_at, "runs": summary_rows}
    write_json(paths.summary_json, payload)
    paths.summary_md.write_text(build_summary_markdown(summary_rows, generated_at))
    state_payload = {
        "generated_at": generated_at,
        "runs": {
            row["run_dir"]: {"progress_signature": row["progress_signature"]}
            for row in summary_rows
        },
    }
    write_json(paths.state_json, state_payload)
    with paths.log_path.open("a") as handle:
        handle.write(json.dumps(payload) + "\n")


def monitor_once(run_dirs: list[Path], paths: MonitorPaths) -> list[dict[str, Any]]:
    prior = _safe_read_json(paths.state_json) or {}
    prior_runs = prior.get("runs", {}) if isinstance(prior, dict) else {}
    rows = [
        summarize_c4_run(run_dir, previous_state=prior_runs.get(str(run_dir.resolve())))
        for run_dir in run_dirs
    ]
    generated_at = _timestamp()
    write_iteration(paths, rows, generated_at)
    return rows


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--interval-sec", type=int, default=300)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--continuous", action="store_true")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    run_dirs = [path.resolve() for path in args.run_dir]
    paths = ensure_monitor_paths(args.output_dir.resolve())
    iteration = 0
    while True:
        monitor_once(run_dirs, paths)
        iteration += 1
        if not args.continuous and iteration >= args.iterations:
            break
        time.sleep(args.interval_sec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
