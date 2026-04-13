#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/finalize_round0_rerun_recovery.sh [run-label] [results-root]

Defaults:
  run-label: run-round0-rerun-recovery-2026-04-13
  results-root: experiments/skillx-skillsbench-001/results/outer-loop-round0/round0-rerun-recovery-v0.1

Behavior:
  - exports the round0 run report for the given rerun label
  - rebuilds the global round0 status summary
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_LABEL="${1:-${SKILLX_RUN_LABEL:-run-round0-rerun-recovery-2026-04-13}}"
DEFAULT_RESULTS_ROOT="$WORKTREE_ROOT/experiments/skillx-skillsbench-001/results/outer-loop-round0/round0-rerun-recovery-v0.1"
RESULTS_ROOT="${2:-${SKILLX_RESULTS_ROOT:-$DEFAULT_RESULTS_ROOT}}"

cd "$WORKTREE_ROOT"

uv run python scripts/export_round0_run_report.py \
  --materialized-root "$RESULTS_ROOT" \
  --run-label "$RUN_LABEL"

uv run python scripts/build_round0_global_status.py

echo "Finalized round0 rerun recovery"
echo "  run-label: $RUN_LABEL"
echo "  report-dir: $RESULTS_ROOT/reports/$RUN_LABEL"
echo "  global-status-dir: $WORKTREE_ROOT/experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/global-round0-status"
