#!/usr/bin/env bash
set -euo pipefail

RUN_PREFIX="${1:-run-first20-rate-limit-rerun-3batch-$(date +%Y-%m-%d-%H%M)}"
SESSION_PREFIX="${2:-skillx-first20-rate-limit-rerun-3b}"
PORT_BASE="${3:-8767}"

MATERIALIZED_ROOT="experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1"
PLAN_DIR="experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/rate-limit-rerun-batches-first20-round0-2026-04-27-3batch"

if [[ ! -f "$MATERIALIZED_ROOT/manifest.json" || ! -f "$MATERIALIZED_ROOT/pair_specs.jsonl" ]]; then
  cat >&2 <<EOF
Missing materialized first20 root: $MATERIALIZED_ROOT

Prepare it first in this worktree, for example:
  SKILLX_PREPARE_ONLY=1 scripts/run_skillx_first20_round0_tmux.sh prepare-first20-rerun noop
EOF
  exit 1
fi

for batch in 01 02 03; do
  port=$((PORT_BASE + 10#$batch - 1))
  run_label="$RUN_PREFIX-b$batch"
  session_name="$SESSION_PREFIX-b$batch"
  pair_manifest="$PLAN_DIR/batch-$batch"_pair_manifest.json
  SKILLX_MAX_CONCURRENT_PAIRS="${SKILLX_MAX_CONCURRENT_PAIRS:-1}"   SKILLX_MATERIALIZED_ROOT="$MATERIALIZED_ROOT"     scripts/run_skillx_inner_loop_tmux.sh "$run_label" "$session_name" "$port" -- --pair-manifest "$pair_manifest"
done
