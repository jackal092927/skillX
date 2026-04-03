#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TERMINAL_EVENT_TYPES = {"role_b_completed", "round_decision_loaded"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def latest_round_dir(rounds_dir: Path) -> Path | None:
    if not rounds_dir.exists():
        return None
    round_dirs = [path for path in rounds_dir.iterdir() if path.is_dir() and path.name.startswith("round-")]
    if not round_dirs:
        return None
    return sorted(round_dirs, key=lambda path: int(path.name.split("-")[-1]))[-1]


def read_latest_event(round_dir: Path) -> dict[str, Any] | None:
    log_path = round_dir / "orchestrator_log.ndjson"
    if not log_path.exists():
        return None
    lines = [line for line in log_path.read_text().splitlines() if line.strip()]
    if not lines:
        return None
    return json.loads(lines[-1])


def read_latest_reward(round_dir: Path) -> float | None:
    verifier_path = round_dir / "executor" / "verifier_summary.json"
    if not verifier_path.exists():
        return None
    payload = read_json(verifier_path)
    reward = payload.get("reward")
    return float(reward) if isinstance(reward, (int, float)) else None


def list_live_processes(run_id: str) -> list[str]:
    pattern = (
        rf"run_skillx_refine_benchmark\.py.*{run_id}"
        r"|codex exec --model gpt-5\.3-codex"
        r"|codex exec --model gpt-5\.4"
        r"|codex exec --model gpt-5-codex"
    )
    proc = subprocess.run(["pgrep", "-af", pattern], capture_output=True, text=True, check=False)
    return [line for line in proc.stdout.splitlines() if line.strip()]


def notify(title: str, message: str) -> None:
    subprocess.run(
        [
            "/usr/bin/osascript",
            "-e",
            f'display notification "{message}" with title "{title}"',
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def run_codex_diagnosis(repo_root: Path, run_dir: Path, task_id: str, latest_round: str, latest_event: dict[str, Any] | None) -> None:
    codex_path = shutil.which("codex")
    if codex_path is None:
        return
    monitor_dir = run_dir / "monitor"
    diagnosis_path = monitor_dir / "agent_alert.md"
    prompt = "\n".join(
        [
            "Inspect this SkillX C4AR run and summarize the current issue.",
            f"Run directory: {run_dir}",
            f"Task id: {task_id}",
            f"Latest round: {latest_round}",
            f"Latest orchestrator event: {json.dumps(latest_event or {}, ensure_ascii=True)}",
            f"Write a concise Markdown diagnosis to: {diagnosis_path}",
            "Focus on whether the run is stuck, crashed, or waiting on a child process. Include the next action.",
        ]
    )
    subprocess.run(
        [
            codex_path,
            "exec",
            "--dangerously-bypass-approvals-and-sandbox",
            "--skip-git-repo-check",
            "--cd",
            str(repo_root),
            "--output-last-message",
            str(monitor_dir / "agent_alert_last_message.json"),
            prompt,
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def build_status(run_dir: Path, task_id: str) -> dict[str, Any]:
    rounds_dir = run_dir / "refine" / task_id / "rounds"
    current_round_dir = latest_round_dir(rounds_dir)
    current_round = None if current_round_dir is None else current_round_dir.name
    latest_event = None if current_round_dir is None else read_latest_event(current_round_dir)
    latest_reward = None if current_round_dir is None else read_latest_reward(current_round_dir)
    live_processes = list_live_processes(run_dir.name)
    latest_event_type = None if latest_event is None else latest_event.get("event_type")
    alert = bool(latest_event_type and not live_processes and latest_event_type not in TERMINAL_EVENT_TYPES)
    alert_reason = None if not alert else f"no_live_process_after_{latest_event_type}"
    return {
        "ts": utc_now(),
        "run_id": run_dir.name,
        "task_id": task_id,
        "latest_round": current_round,
        "latest_event_type": latest_event_type,
        "latest_event_status": None if latest_event is None else latest_event.get("status"),
        "latest_reward": latest_reward,
        "live_processes": live_processes,
        "alert": alert,
        "alert_reason": alert_reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Periodic monitor for a SkillX run.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--codex-on-alert", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    run_dir = Path(args.run_dir).resolve()
    monitor_dir = run_dir / "monitor"
    status_log = monitor_dir / "monitor_status.ndjson"
    latest_status_path = monitor_dir / "latest_status.json"
    latest_status_md = monitor_dir / "latest_status.md"
    state_path = monitor_dir / "monitor_state.json"

    status = build_status(run_dir, args.task_id)
    append_jsonl(status_log, status)
    write_json(latest_status_path, status)
    latest_status_md.write_text(
        "\n".join(
            [
                "# Monitor Status",
                "",
                f"- ts: `{status['ts']}`",
                f"- run_id: `{status['run_id']}`",
                f"- latest_round: `{status['latest_round']}`",
                f"- latest_event_type: `{status['latest_event_type']}`",
                f"- latest_event_status: `{status['latest_event_status']}`",
                f"- latest_reward: `{status['latest_reward']}`",
                f"- live_processes: `{', '.join(status['live_processes']) or 'none'}`",
                f"- alert: `{status['alert']}`",
                f"- alert_reason: `{status['alert_reason']}`",
            ]
        )
        + "\n"
    )

    previous_state = read_json(state_path) if state_path.exists() else {}
    previous_key = (
        previous_state.get("latest_round"),
        previous_state.get("latest_event_type"),
        previous_state.get("alert"),
        previous_state.get("alert_reason"),
    )
    current_key = (
        status.get("latest_round"),
        status.get("latest_event_type"),
        status.get("alert"),
        status.get("alert_reason"),
    )
    write_json(state_path, status)

    if current_key == previous_key:
        return 0

    if status["alert"]:
        notify(
            "SkillX Monitor Alert",
            f"{status['run_id']} {status['latest_round']} stalled after {status['latest_event_type']}",
        )
        if args.codex_on_alert:
            round_name = status["latest_round"] or "unknown-round"
            latest_round = latest_round_dir(run_dir / "refine" / args.task_id / "rounds")
            latest_event = None if latest_round is None else read_latest_event(latest_round)
            run_codex_diagnosis(repo_root, run_dir, args.task_id, round_name, latest_event)
    elif status["latest_event_type"] in {"round_decision_loaded", "role_b_completed"}:
        notify(
            "SkillX Monitor Update",
            f"{status['run_id']} reached {status['latest_event_type']} in {status['latest_round']}",
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
