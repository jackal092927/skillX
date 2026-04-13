#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/rematerialize_round0_rerun_recovery_root.sh

Environment overrides:
  SKILLX_EXP_WORKTREE        Absolute path to the experiment worktree
  SKILLX_SKILLSBENCH_ROOT    Absolute path to the shared skillsbench-src checkout
  SKILLX_OUTPUT_DIR          Materialized rerun recovery root
  SKILLX_REPORT_DIR          Rerun-recovery report directory
  SKILLX_TASK_SLICE_OUT      Generated task slice path
  SKILLX_PAIR_MANIFEST_OUT   Generated pair manifest path
  SKILLX_SUMMARY_OUT         Generated rerun summary markdown path
  SKILLX_ROUND0_RUN_ID       Materialization run id
  SKILLX_ROUND_BUDGET        Round budget, default 3
  SKILLX_AGENT               Benchmark agent, default claude-code
  SKILLX_MODEL               Benchmark model, default anthropic/claude-sonnet-4-5
  SKILLX_OAUTH_FILE          Claude auth token path
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GIT_COMMON_DIR="$(git -C "$WORKTREE_ROOT" rev-parse --git-common-dir)"
SHARED_REPO_ROOT="$(cd "$GIT_COMMON_DIR/.." && pwd)"
PROJECTS_ROOT="$(cd "$SHARED_REPO_ROOT/.." && pwd)"

EXP_WORKTREE="${SKILLX_EXP_WORKTREE:-$WORKTREE_ROOT}"
SKILLSBENCH_ROOT="${SKILLX_SKILLSBENCH_ROOT:-$PROJECTS_ROOT/skillsbench-src}"
ROUND0_ROOT="$EXP_WORKTREE/experiments/skillx-skillsbench-001/results/outer-loop-round0"
REPORT_DIR="${SKILLX_REPORT_DIR:-$ROUND0_ROOT/reports/rerun-recovery}"
TASK_SLICE_OUT="${SKILLX_TASK_SLICE_OUT:-$REPORT_DIR/round0-rerun-recovery-v0.1.task-slice.json}"
PAIR_MANIFEST_OUT="${SKILLX_PAIR_MANIFEST_OUT:-$REPORT_DIR/round0-rerun-recovery-v0.1.pair-manifest.json}"
SUMMARY_OUT="${SKILLX_SUMMARY_OUT:-$REPORT_DIR/round0-rerun-recovery-v0.1.md}"
OUTPUT_DIR="${SKILLX_OUTPUT_DIR:-$ROUND0_ROOT/round0-rerun-recovery-v0.1}"
RUN_ID="${SKILLX_ROUND0_RUN_ID:-round0-rerun-recovery-v0.1}"
ROUND_BUDGET="${SKILLX_ROUND_BUDGET:-3}"
AGENT="${SKILLX_AGENT:-claude-code}"
MODEL="${SKILLX_MODEL:-anthropic/claude-sonnet-4-5}"
OAUTH_FILE="${SKILLX_OAUTH_FILE:-$HOME/.claude/claude-code-oauth-token}"

if [[ ! -d "$EXP_WORKTREE" ]]; then
  echo "Missing experiment worktree: $EXP_WORKTREE" >&2
  exit 1
fi

if [[ ! -d "$SKILLSBENCH_ROOT" ]]; then
  echo "Missing skillsbench root: $SKILLSBENCH_ROOT" >&2
  exit 1
fi

if [[ ! -f "$OAUTH_FILE" ]]; then
  echo "Missing oauth file: $OAUTH_FILE" >&2
  exit 1
fi

mkdir -p "$REPORT_DIR"

cd "$EXP_WORKTREE"

uv run python scripts/build_round0_rerun_recovery.py \
  --global-status "$ROUND0_ROOT/reports/global-round0-status/global_pair_status.json" \
  --task-slice-out "$TASK_SLICE_OUT" \
  --pair-manifest-out "$PAIR_MANIFEST_OUT" \
  --summary-out "$SUMMARY_OUT"

rm -rf "$OUTPUT_DIR/pairs"
rm -f "$OUTPUT_DIR/manifest.json" "$OUTPUT_DIR/pair_specs.jsonl" "$OUTPUT_DIR/launch_round0.sh"

exec uv run python scripts/materialize_skillx_round0_runner.py \
  --skillsbench-root "$SKILLSBENCH_ROOT" \
  --task-slice "$TASK_SLICE_OUT" \
  --prompt-bank docs/plans/skillx/skillx-prompt-bank-v0.1.json \
  --inventory docs/plans/skillx/skillsbench-task-cluster-inputs-v0.1.jsonl \
  --official-results experiments/skillx-skillsbench-001/results/official-task-results/official_task_results.jsonl \
  --render-template docs/plans/skillx/skillx-render-template-frozen-v0.1.md \
  --output-dir "$OUTPUT_DIR" \
  --run-id "$RUN_ID" \
  --oauth-file "$OAUTH_FILE" \
  --round-budget "$ROUND_BUDGET" \
  --agent "$AGENT" \
  --model "$MODEL"
