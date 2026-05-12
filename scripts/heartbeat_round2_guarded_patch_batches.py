#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def ensure_restart_safe_path() -> None:
    """Make automation PATH robust after macOS app or machine restarts."""
    extra_dirs = [
        "/opt/homebrew/bin",
        "/usr/local/bin",
        "/Applications/Docker.app/Contents/Resources/bin",
    ]
    current = os.environ.get("PATH", "")
    parts = [part for part in current.split(os.pathsep) if part]
    for path in reversed(extra_dirs):
        if path not in parts and Path(path).exists():
            parts.insert(0, path)
    os.environ["PATH"] = os.pathsep.join(parts)


ensure_restart_safe_path()


REPO_ROOT = Path(__file__).resolve().parents[1]
ROUND1_HEARTBEAT = REPO_ROOT / "scripts/heartbeat_round1_batches.py"
MATERIALIZED_ROOT = (
    REPO_ROOT
    / "experiments/skillx-skillsbench-001/results/outer-loop-round0/"
    / "sonnet45-task-list-first20-v0.1/"
    / "outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10"
)
PLAN_DIR = (
    REPO_ROOT
    / "experiments/skillx-skillsbench-001/results/outer-loop-round0/"
    / "sonnet45-task-list-first20-v0.1/reports/"
    / "outer-loop-round2-guarded-patch-2026-05-10-5batch"
)
PRIMARY_CLAUDE_OAUTH_FILE = Path(
    os.environ.get(
        "SKILLX_ROUND2_PRIMARY_CLAUDE_OAUTH_FILE",
        str(Path.home() / ".claude/claude-code-oauth-token"),
    )
).expanduser()
FALLBACK_CLAUDE_OAUTH_FILE = Path(
    os.environ.get(
        "SKILLX_ROUND2_FALLBACK_CLAUDE_OAUTH_FILE",
        str(Path.home() / ".claude-skillx-fallback/claude-code-oauth-token"),
    )
).expanduser()
HEARTBEAT_LOG = MATERIALIZED_ROOT / "reports/round2_guarded_patch_heartbeat.jsonl"
ISSUE_LOG = MATERIALIZED_ROOT / "reports/round2_guarded_patch_heartbeat_issues.jsonl"


def load_round1_module() -> Any:
    spec = importlib.util.spec_from_file_location("skillx_round1_heartbeat", ROUND1_HEARTBEAT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import heartbeat helper from {ROUND1_HEARTBEAT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


heartbeat = load_round1_module()
heartbeat.MATERIALIZED_ROOT = MATERIALIZED_ROOT
heartbeat.PLAN_DIR = PLAN_DIR
heartbeat.PRIMARY_CLAUDE_OAUTH_FILE = PRIMARY_CLAUDE_OAUTH_FILE
heartbeat.FALLBACK_CLAUDE_OAUTH_FILE = FALLBACK_CLAUDE_OAUTH_FILE
heartbeat.BATCHES = [
    heartbeat.Batch(
        batch_id="b01",
        run_label="run-round2-guarded-patch-2026-05-10-b01",
        session="skillx-round2-guarded-patch-b01",
        port=8782,
        pair_count=28,
        pair_manifest=PLAN_DIR / "batch-01_pair_manifest.json",
    ),
    heartbeat.Batch(
        batch_id="b02",
        run_label="run-round2-guarded-patch-2026-05-10-b02",
        session="skillx-round2-guarded-patch-b02",
        port=8783,
        pair_count=28,
        pair_manifest=PLAN_DIR / "batch-02_pair_manifest.json",
    ),
    heartbeat.Batch(
        batch_id="b03",
        run_label="run-round2-guarded-patch-2026-05-10-b03",
        session="skillx-round2-guarded-patch-b03",
        port=8784,
        pair_count=28,
        pair_manifest=PLAN_DIR / "batch-03_pair_manifest.json",
    ),
    heartbeat.Batch(
        batch_id="b04",
        run_label="run-round2-guarded-patch-2026-05-10-b04",
        session="skillx-round2-guarded-patch-b04",
        port=8785,
        pair_count=28,
        pair_manifest=PLAN_DIR / "batch-04_pair_manifest.json",
    ),
    heartbeat.Batch(
        batch_id="b05",
        run_label="run-round2-guarded-patch-2026-05-10-b05",
        session="skillx-round2-guarded-patch-b05",
        port=8786,
        pair_count=28,
        pair_manifest=PLAN_DIR / "batch-05_pair_manifest.json",
    ),
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Heartbeat monitor for SkillX round2 guarded-patch batches."
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-repair", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--stale-minutes", type=int, default=180)
    args = parser.parse_args()

    dry_run = bool(args.dry_run or args.no_repair)
    results = [
        heartbeat.assess_batch(
            batch,
            dry_run=dry_run,
            stale_minutes=args.stale_minutes,
        )
        for batch in heartbeat.BATCHES
    ]
    payload = {
        "observed_at": now(),
        "automation_id": "skillx-round2-guarded-patch-heartbeat",
        "materialized_root": str(MATERIALIZED_ROOT),
        "plan_dir": str(PLAN_DIR),
        "primary_claude_oauth_file": str(PRIMARY_CLAUDE_OAUTH_FILE),
        "fallback_claude_oauth_file": str(FALLBACK_CLAUDE_OAUTH_FILE),
        "heartbeat_log": str(HEARTBEAT_LOG),
        "issue_log": str(ISSUE_LOG),
        "dry_run": dry_run,
        "results": results,
    }

    append_jsonl(HEARTBEAT_LOG, payload)
    issue_results = [
        result
        for result in results
        if result.get("issues") or result.get("actions") or result.get("status") != "ok"
    ]
    if issue_results:
        append_jsonl(
            ISSUE_LOG,
            {
                "observed_at": payload["observed_at"],
                "results": issue_results,
            },
        )

    if args.json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"SkillX round2 guarded-patch heartbeat at {payload['observed_at']}")
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
