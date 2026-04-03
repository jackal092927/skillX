from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--process-pattern", required=True)
    parser.add_argument("--interval-sec", type=int, default=300)
    parser.add_argument("--log-path", type=Path)
    parser.add_argument("--state-path", type=Path)
    return parser.parse_args()


def timestamp_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def round_index_from_name(name: str) -> int:
    return int(name.split("-", 1)[1])


def active_processes(pattern: str) -> list[str]:
    proc = subprocess.run(
        ["pgrep", "-af", pattern],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode not in (0, 1):
        return [f"pgrep_error: {proc.stderr.strip()}"]
    return [line for line in proc.stdout.splitlines() if line.strip()]


def latest_orchestrator_event(round_dir: Path) -> dict[str, Any] | None:
    event_log = round_dir / "orchestrator_log.ndjson"
    if not event_log.exists():
        return None
    lines = [line for line in event_log.read_text().splitlines() if line.strip()]
    if not lines:
        return None
    return json.loads(lines[-1])


def round_snapshot(round_dir: Path) -> dict[str, Any]:
    result_payload = read_json(round_dir / "tune_check" / "result.json")
    event = latest_orchestrator_event(round_dir)
    snapshot: dict[str, Any] = {
        "round_index": round_index_from_name(round_dir.name),
        "event_type": event.get("event_type") if event else None,
        "event_status": event.get("status") if event else None,
        "event_timestamp": event.get("timestamp") if event else None,
        "reward": result_payload.get("reward") if result_payload else None,
        "exception_stats": result_payload.get("exception_stats") if result_payload else None,
    }
    return snapshot


def collect_sample(run_dir: Path, task_id: str, process_pattern: str) -> dict[str, Any]:
    rounds_dir = run_dir / "refine" / task_id / "rounds"
    round_dirs = []
    if rounds_dir.exists():
        round_dirs = sorted(
            [path for path in rounds_dir.iterdir() if path.is_dir() and path.name.startswith("round-")],
            key=lambda path: round_index_from_name(path.name),
        )
    rounds = [round_snapshot(round_dir) for round_dir in round_dirs]
    rewards = [row["reward"] for row in rounds if isinstance(row.get("reward"), (int, float))]
    latest_round = rounds[-1] if rounds else None
    return {
        "timestamp_utc": timestamp_utc(),
        "run_dir": str(run_dir),
        "task_id": task_id,
        "active_processes": active_processes(process_pattern),
        "latest_round": latest_round,
        "best_reward_so_far": max(rewards) if rewards else None,
        "rounds": rounds,
    }


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.resolve()
    log_path = (args.log_path or (run_dir / "HEARTBEAT.ndjson")).resolve()
    state_path = (args.state_path or (run_dir / "HEARTBEAT_STATUS.json")).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.parent.mkdir(parents=True, exist_ok=True)

    while True:
        sample = collect_sample(run_dir, args.task_id, args.process_pattern)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(sample, sort_keys=True) + "\n")
        state_path.write_text(json.dumps(sample, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        time.sleep(args.interval_sec)


if __name__ == "__main__":
    raise SystemExit(main())
