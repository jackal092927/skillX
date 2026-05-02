#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../../.." && pwd)"
MATERIALIZED_ROOT="$REPO_ROOT/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round1-first20-fullmatrix-2026-05-01-1932-candidates"
PLAN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

export SKILLX_MAX_CONCURRENT_PAIRS="${SKILLX_MAX_CONCURRENT_PAIRS:-1}"
export SKILLX_ROUND_BUDGET="${SKILLX_ROUND_BUDGET:-3}"
export SKILLX_MATERIALIZED_ROOT="$MATERIALIZED_ROOT"
export SKILLX_AGENT="${SKILLX_AGENT:-claude-code}"
export SKILLX_MODEL="${SKILLX_MODEL:-anthropic/claude-sonnet-4-5}"

echo "Starting batch-01: 7 tasks / 49 pairs"
scripts/run_skillx_inner_loop_tmux.sh 'run-round1-first20-fullmatrix-2026-05-01-b01' 'skillx-round1-first20-b01' 8772 -- --pair-manifest "$PLAN_DIR/batch-01_pair_manifest.json" --skip-existing-succeeded

echo "Starting batch-02: 7 tasks / 49 pairs"
scripts/run_skillx_inner_loop_tmux.sh 'run-round1-first20-fullmatrix-2026-05-01-b02' 'skillx-round1-first20-b02' 8773 -- --pair-manifest "$PLAN_DIR/batch-02_pair_manifest.json" --skip-existing-succeeded

echo "Starting batch-03: 6 tasks / 42 pairs"
scripts/run_skillx_inner_loop_tmux.sh 'run-round1-first20-fullmatrix-2026-05-01-b03' 'skillx-round1-first20-b03' 8774 -- --pair-manifest "$PLAN_DIR/batch-03_pair_manifest.json" --skip-existing-succeeded
