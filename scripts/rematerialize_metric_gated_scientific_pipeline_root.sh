#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/rematerialize_metric_gated_scientific_pipeline_root.sh

Environment overrides:
  SKILLX_EXP_WORKTREE        Absolute path to the experiment worktree
  SKILLX_SKILLSBENCH_ROOT    Absolute path to the shared skillsbench-src checkout
  SKILLX_OUTPUT_DIR          Materialized output directory
  SKILLX_ROUND0_RUN_ID       Materialization run id
  SKILLX_TASK_SLICE          Sidecar task slice JSON
  SKILLX_PROMPT_BANK         Sidecar prompt-bank JSON
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
OUTPUT_DIR="${SKILLX_OUTPUT_DIR:-$EXP_WORKTREE/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-metric-gated-scientific-pipeline-4task-v0.1}"
RUN_ID="${SKILLX_ROUND0_RUN_ID:-sonnet45-metric-gated-scientific-pipeline-4task-v0.1}"
TASK_SLICE="${SKILLX_TASK_SLICE:-experiments/skillx-skillsbench-001/results/official-task-results/metric-gated-scientific-pipeline-strong-candidates-v0.1.json}"
PROMPT_BANK="${SKILLX_PROMPT_BANK:-docs/plans/skillx/skillx-metric-gated-scientific-pipeline-prompt-bank-v0.1.json}"
ROUND_BUDGET="${SKILLX_ROUND_BUDGET:-3}"
AGENT="${SKILLX_AGENT:-claude-code}"
MODEL="${SKILLX_MODEL:-anthropic/claude-sonnet-4-5}"
OAUTH_FILE="${SKILLX_OAUTH_FILE:-$HOME/.claude/claude-code-oauth-token}"
UV_BIN="$(command -v uv)"

if [[ ! -d "$EXP_WORKTREE" ]]; then
  echo "Missing experiment worktree: $EXP_WORKTREE" >&2
  exit 1
fi

if [[ ! -d "$SKILLSBENCH_ROOT" ]]; then
  echo "Missing skillsbench root: $SKILLSBENCH_ROOT" >&2
  exit 1
fi

if [[ ! -f "$EXP_WORKTREE/$TASK_SLICE" ]]; then
  echo "Missing task slice: $EXP_WORKTREE/$TASK_SLICE" >&2
  exit 1
fi

if [[ ! -f "$EXP_WORKTREE/$PROMPT_BANK" ]]; then
  echo "Missing prompt bank: $EXP_WORKTREE/$PROMPT_BANK" >&2
  exit 1
fi

if [[ ! -f "$OAUTH_FILE" ]]; then
  echo "Missing oauth file: $OAUTH_FILE" >&2
  exit 1
fi

if [[ -z "$UV_BIN" ]]; then
  echo "Missing uv in PATH." >&2
  exit 1
fi

cd "$EXP_WORKTREE"

exec "$UV_BIN" run python scripts/materialize_skillx_round0_runner.py \
  --skillsbench-root "$SKILLSBENCH_ROOT" \
  --task-slice "$TASK_SLICE" \
  --prompt-bank "$PROMPT_BANK" \
  --inventory docs/plans/skillx/skillsbench-task-cluster-inputs-v0.1.jsonl \
  --official-results experiments/skillx-skillsbench-001/results/official-task-results/official_task_results.jsonl \
  --render-template docs/plans/skillx/skillx-render-template-frozen-v0.1.md \
  --output-dir "$OUTPUT_DIR" \
  --run-id "$RUN_ID" \
  --oauth-file "$OAUTH_FILE" \
  --round-budget "$ROUND_BUDGET" \
  --agent "$AGENT" \
  --model "$MODEL"
