#!/usr/bin/env bash
set -euo pipefail

WORKTREE_ROOT=/Users/Jackal/iWorld/projects/skillX
MATERIALIZED_ROOT=/Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10
PAIR_MANIFEST=/Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/reports/run-round2-guarded-patch-2026-05-10-b04/inner_loop_audit/all_flagged_pair_manifest.json
BASE_RUN_LABEL=run-round2-guarded-patch-2026-05-10-b04

RERUN_LABEL="${1:-${BASE_RUN_LABEL}-audit-rerun-all-flagged-$(date +%Y-%m-%d-%H%M)}"
SESSION_NAME="${2:-skillx-${RERUN_LABEL}}"
MONITOR_PORT="${3:-}"

export SKILLX_MATERIALIZED_ROOT="$MATERIALIZED_ROOT"
export SKILLX_MAX_CONCURRENT_PAIRS="${SKILLX_MAX_CONCURRENT_PAIRS:-1}"
export SKILLX_DOCKER_AUTO_RECOVER="${SKILLX_DOCKER_AUTO_RECOVER:-1}"

cd "$WORKTREE_ROOT"
if [[ -n "$MONITOR_PORT" ]]; then
  scripts/run_skillx_inner_loop_tmux.sh "$RERUN_LABEL" "$SESSION_NAME" "$MONITOR_PORT" -- --pair-manifest "$PAIR_MANIFEST"
else
  scripts/run_skillx_inner_loop_tmux.sh "$RERUN_LABEL" "$SESSION_NAME" -- --pair-manifest "$PAIR_MANIFEST"
fi
