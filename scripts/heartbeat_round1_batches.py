#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MATERIALIZED_ROOT = (
    REPO_ROOT
    / "experiments/skillx-skillsbench-001/results/outer-loop-round0/"
    / "sonnet45-task-list-first20-v0.1/"
    / "outer-loop-round1-first20-fullmatrix-2026-05-01-1932-candidates"
)
PLAN_DIR = (
    REPO_ROOT
    / "experiments/skillx-skillsbench-001/results/outer-loop-round0/"
    / "sonnet45-task-list-first20-v0.1/reports/"
    / "outer-loop-round1-first20-fullmatrix-2026-05-01-1932-batches"
)
PRIMARY_CLAUDE_OAUTH_FILE = Path(
    os.environ.get(
        "SKILLX_ROUND1_PRIMARY_CLAUDE_OAUTH_FILE",
        str(Path.home() / ".claude-skillx-fallback/claude-code-oauth-token"),
    )
).expanduser()
FALLBACK_CLAUDE_OAUTH_FILE = Path(
    os.environ.get(
        "SKILLX_ROUND1_FALLBACK_CLAUDE_OAUTH_FILE",
        str(Path.home() / ".claude/claude-code-oauth-token"),
    )
).expanduser()


@dataclass(frozen=True)
class Batch:
    batch_id: str
    run_label: str
    session: str
    port: int
    pair_count: int
    pair_manifest: Path


BATCHES = [
    Batch(
        batch_id="b01",
        run_label="run-round1-first20-fullmatrix-fallback-2026-05-01-b01",
        session="skillx-round1-first20-b01",
        port=8772,
        pair_count=49,
        pair_manifest=PLAN_DIR / "batch-01_pair_manifest.json",
    ),
    Batch(
        batch_id="b02",
        run_label="run-round1-first20-fullmatrix-fallback-2026-05-01-b02",
        session="skillx-round1-first20-b02",
        port=8773,
        pair_count=49,
        pair_manifest=PLAN_DIR / "batch-02_pair_manifest.json",
    ),
    Batch(
        batch_id="b03",
        run_label="run-round1-first20-fullmatrix-fallback-2026-05-01-b03",
        session="skillx-round1-first20-b03",
        port=8774,
        pair_count=42,
        pair_manifest=PLAN_DIR / "batch-03_pair_manifest.json",
    ),
]


SHELL_COMMANDS = {"zsh", "bash", "sh", "fish"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(
    args: list[str],
    *,
    check: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=check,
        env=env,
    )


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def has_children(path: Path) -> bool:
    try:
        next(path.iterdir())
    except (FileNotFoundError, StopIteration):
        return False
    return True


def tmux_has_session(session: str) -> bool:
    return run(["tmux", "has-session", "-t", session]).returncode == 0


def tmux_window_exists(session: str, window: str) -> bool:
    result = run(["tmux", "list-windows", "-t", session, "-F", "#{window_name}"])
    if result.returncode != 0:
        return False
    return window in result.stdout.splitlines()


def tmux_pane_command(session: str, window: str) -> str | None:
    result = run(
        ["tmux", "list-panes", "-t", f"{session}:{window}", "-F", "#{pane_current_command}"]
    )
    if result.returncode != 0:
        return None
    commands = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return commands[0] if commands else None


def tmux_send(session: str, window: str, *keys: str) -> None:
    run(["tmux", "send-keys", "-t", f"{session}:{window}", *keys])


def port_listening(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def fetch_status(port: int) -> dict[str, Any] | None:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status", timeout=5) as response:
            payload = json.load(response)
            return payload if isinstance(payload, dict) else None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def launcher_log_dir(batch: Batch) -> Path:
    return MATERIALIZED_ROOT / "launcher_logs" / batch.run_label


def archive_launcher_log(batch: Batch, actions: list[str], *, dry_run: bool) -> None:
    log_dir = launcher_log_dir(batch)
    if not has_children(log_dir):
        return

    archive_root = MATERIALIZED_ROOT / "launcher_logs" / "_heartbeat_archives"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = archive_root / f"{batch.run_label}-{stamp}"
    suffix = 1
    while dest.exists():
        suffix += 1
        dest = archive_root / f"{batch.run_label}-{stamp}-{suffix}"

    actions.append(f"archive launcher log {log_dir} -> {dest}")
    if dry_run:
        return
    archive_root.mkdir(parents=True, exist_ok=True)
    shutil.move(str(log_dir), str(dest))


def read_summary(batch: Batch) -> dict[str, Any] | None:
    return read_json(launcher_log_dir(batch) / "summary.json")


def summary_completed(summary: dict[str, Any] | None, expected_total: int) -> bool:
    if not isinstance(summary, dict):
        return False
    completed = summary.get("completed_pairs")
    failed = summary.get("failed_pairs")
    return completed == expected_total and failed == 0 and not summary.get("aborted")


def active_processes_use_primary(status: dict[str, Any] | None) -> bool:
    if not isinstance(status, dict):
        return True
    processes = status.get("active_processes") or []
    if not processes:
        return True
    expected = f"--oauth-file {PRIMARY_CLAUDE_OAUTH_FILE}"
    runner_processes = [str(process) for process in processes if "--oauth-file" in str(process)]
    return all(expected in process for process in runner_processes)


def latest_runtime_profile_uses_known_oauth(status: dict[str, Any] | None) -> bool:
    if not isinstance(status, dict):
        return True
    allowed_oauth_files = {
        str(PRIMARY_CLAUDE_OAUTH_FILE),
        str(FALLBACK_CLAUDE_OAUTH_FILE),
    }
    for event in reversed(status.get("recent_events") or []):
        profile = event.get("runtime_profile") if isinstance(event, dict) else None
        if isinstance(profile, dict) and profile.get("agent") == "claude-code":
            return profile.get("oauth_file") in allowed_oauth_files
    return True


def launch_batch(batch: Batch, actions: list[str], *, dry_run: bool) -> None:
    cmd = [
        str(REPO_ROOT / "scripts/run_skillx_inner_loop_tmux.sh"),
        batch.run_label,
        batch.session,
        str(batch.port),
        "--",
        "--pair-manifest",
        str(batch.pair_manifest),
        "--skip-existing-succeeded",
        "--oauth-file",
        str(PRIMARY_CLAUDE_OAUTH_FILE),
        "--fallback-oauth-file",
        str(FALLBACK_CLAUDE_OAUTH_FILE),
    ]
    env = os.environ.copy()
    env.update(
        {
            "SKILLX_MAX_CONCURRENT_PAIRS": env.get("SKILLX_MAX_CONCURRENT_PAIRS", "1"),
            "SKILLX_ROUND_BUDGET": env.get("SKILLX_ROUND_BUDGET", "3"),
            "SKILLX_MATERIALIZED_ROOT": str(MATERIALIZED_ROOT),
            "SKILLX_AGENT": env.get("SKILLX_AGENT", "claude-code"),
            "SKILLX_MODEL": env.get("SKILLX_MODEL", "anthropic/claude-sonnet-4-5"),
        }
    )
    actions.append(f"launch {batch.session} on port {batch.port}")
    if dry_run:
        return
    result = run(cmd, env=env)
    if result.returncode != 0:
        raise RuntimeError(
            f"failed to launch {batch.session}: {result.stderr.strip() or result.stdout.strip()}"
        )


def restart_batch(batch: Batch, actions: list[str], *, dry_run: bool) -> None:
    if tmux_has_session(batch.session):
        actions.append(f"kill tmux session {batch.session}")
        if not dry_run:
            run(["tmux", "kill-session", "-t", batch.session])
            time.sleep(1)
    archive_launcher_log(batch, actions, dry_run=dry_run)
    launch_batch(batch, actions, dry_run=dry_run)


def ensure_dashboard(batch: Batch, actions: list[str], *, dry_run: bool) -> bool:
    script = launcher_log_dir(batch) / "run_dashboard.sh"
    if not script.exists() or not tmux_has_session(batch.session):
        return False

    if not tmux_window_exists(batch.session, "dashboard"):
        actions.append(f"create dashboard window for {batch.session}")
        if not dry_run:
            result = run(["tmux", "new-window", "-t", batch.session, "-n", "dashboard"])
            if result.returncode != 0:
                return False

    actions.append(f"restart dashboard for {batch.session}")
    if dry_run:
        return True
    tmux_send(batch.session, "dashboard", "C-c")
    tmux_send(batch.session, "dashboard", f"bash {script}", "C-m")
    time.sleep(2)
    return port_listening(batch.port)


def assess_batch(batch: Batch, *, dry_run: bool, stale_minutes: int) -> dict[str, Any]:
    actions: list[str] = []
    issues: list[str] = []
    repaired = False
    status = fetch_status(batch.port)
    summary = read_summary(batch)
    session_exists = tmux_has_session(batch.session)
    inner_command = tmux_pane_command(batch.session, "inner-loop") if session_exists else None
    dashboard_listening = port_listening(batch.port)

    completed = (
        bool(status and status.get("health") == "completed")
        or summary_completed(summary, batch.pair_count)
    )

    if not PRIMARY_CLAUDE_OAUTH_FILE.exists():
        issues.append(f"missing primary token {PRIMARY_CLAUDE_OAUTH_FILE}")
    if not FALLBACK_CLAUDE_OAUTH_FILE.exists():
        issues.append(f"missing fallback token {FALLBACK_CLAUDE_OAUTH_FILE}")

    if status and status.get("run_label") not in {None, batch.run_label}:
        issues.append(f"dashboard run_label mismatch: {status.get('run_label')}")
    if status and status.get("total_pairs") not in {None, batch.pair_count}:
        issues.append(f"dashboard total_pairs mismatch: {status.get('total_pairs')}")
    if not active_processes_use_primary(status):
        issues.append("active runtime is not using fallback Claude token as primary")
    if not latest_runtime_profile_uses_known_oauth(status):
        issues.append("latest runtime profile is using an unexpected Claude token")

    if not session_exists and not completed:
        issues.append("tmux session missing")
    has_active_process = bool(status and (status.get("active_processes") or []))
    if session_exists and inner_command in SHELL_COMMANDS and not completed and not has_active_process:
        issues.append(f"inner-loop inactive: pane command is {inner_command}")
    if not dashboard_listening and not completed:
        issues.append("dashboard port not listening")
    if not status and dashboard_listening:
        issues.append("dashboard API not responding")
    if status and status.get("health") not in {None, "running", "completed"}:
        issues.append(f"dashboard health is {status.get('health')}")
    if status and (status.get("failed_pairs") or 0) > 0 and not (status.get("active_pair_count") or 0):
        issues.append(f"failed_pairs={status.get('failed_pairs')} and no active pair")

    latest_activity = status.get("latest_activity_at") if status else None
    if (
        status
        and status.get("health") == "running"
        and not (status.get("active_processes") or [])
        and latest_activity
    ):
        try:
            latest = datetime.fromisoformat(str(latest_activity).replace("Z", "+00:00"))
            stale_seconds = (datetime.now(timezone.utc) - latest).total_seconds()
            if stale_seconds > stale_minutes * 60:
                issues.append(f"no active process and latest activity is older than {stale_minutes}m")
        except ValueError:
            issues.append(f"could not parse latest_activity_at={latest_activity}")

    repairable = [
        issue
        for issue in issues
        if not issue.startswith("missing primary token") and not issue.startswith("missing fallback token")
    ]
    dashboard_only = repairable == ["dashboard port not listening"] or repairable == [
        "dashboard API not responding"
    ]

    if repairable and not completed:
        if dashboard_only and ensure_dashboard(batch, actions, dry_run=dry_run):
            repaired = True
        else:
            restart_batch(batch, actions, dry_run=dry_run)
            repaired = True

    post_status = fetch_status(batch.port) if repaired and not dry_run else status
    return {
        "batch_id": batch.batch_id,
        "session": batch.session,
        "port": batch.port,
        "run_label": batch.run_label,
        "status": "ok" if not issues else "repaired" if repaired else "issue",
        "issues": issues,
        "actions": actions,
        "health": (post_status or status or {}).get("health"),
        "completed_pairs": (post_status or status or {}).get("completed_pairs"),
        "failed_pairs": (post_status or status or {}).get("failed_pairs"),
        "active_pair_count": (post_status or status or {}).get("active_pair_count"),
        "completed": completed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Heartbeat monitor for SkillX round1 batches.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-repair", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--stale-minutes", type=int, default=180)
    args = parser.parse_args()

    results = [
        assess_batch(
            batch,
            dry_run=args.dry_run or args.no_repair,
            stale_minutes=args.stale_minutes,
        )
        for batch in BATCHES
    ]
    payload = {
        "observed_at": now(),
        "materialized_root": str(MATERIALIZED_ROOT),
        "primary_claude_oauth_file": str(PRIMARY_CLAUDE_OAUTH_FILE),
        "fallback_claude_oauth_file": str(FALLBACK_CLAUDE_OAUTH_FILE),
        "dry_run": bool(args.dry_run or args.no_repair),
        "results": results,
    }

    if args.json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"SkillX round1 heartbeat at {payload['observed_at']}")
        for result in results:
            print(
                f"- {result['batch_id']} {result['status']}: "
                f"health={result['health']} completed={result['completed_pairs']} "
                f"failed={result['failed_pairs']} active={result['active_pair_count']}"
            )
            for issue in result["issues"]:
                print(f"  issue: {issue}")
            for action in result["actions"]:
                print(f"  action: {action}")

    has_unrepaired_issue = any(result["status"] == "issue" for result in results)
    return 2 if has_unrepaired_issue else 0


if __name__ == "__main__":
    sys.exit(main())
