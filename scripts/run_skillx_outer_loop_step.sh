#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run_skillx_outer_loop_step.sh [inner-run-label] [outer-label] [next-materialized-root]

Example:
  scripts/run_skillx_outer_loop_step.sh run-round0-10x7 outer-loop-round1-10x7 \
    experiments/skillx-skillsbench-001/results/outer-loop-round0/outer-loop-round1-candidate-rerun-10x7

Environment overrides:
  SKILLX_EXP_WORKTREE       Absolute path to the experiment worktree. Default: current checkout.
  SKILLX_PREVIOUS_MATERIALIZED_ROOT
                            Materialized root containing the completed inner-loop run.
                            Default: experiments/.../outer-loop-round0/sonnet45-slice20-v0.2
  SKILLX_ROUND_ROOT         Parent round root used for global status and reports.
                            Default: parent directory of SKILLX_PREVIOUS_MATERIALIZED_ROOT.
  SKILLX_INNER_RUN_LABEL    Completed inner-loop run label if arg 1 is omitted.
  SKILLX_OUTER_LABEL        Label used for outer-loop report directories if arg 2 is omitted.
  SKILLX_NEXT_MATERIALIZED_ROOT
                            Next-round materialized root if arg 3 is omitted.
  SKILLX_EXPORT_REPORT      1 exports the completed inner-loop run report first. Default: 1
  SKILLX_BUILD_GLOBAL_STATUS
                            1 rebuilds reports/global-round0-status. Default: 1
  SKILLX_ROUND_ID           Source outer-loop round id. Default: outer-loop-round0
  SKILLX_NEXT_ROUND_ID      Next outer-loop round id. Default: outer-loop-round1
  SKILLX_NEXT_RUN_ID        Run id embedded into next-round pair specs.
  SKILLX_REWRITE_MODE       llm or deterministic. Default: llm
  SKILLX_LLM_MODEL          Outer-loop rewriter model. Default: anthropic/claude-sonnet-4-5
  SKILLX_PYTHON             Python runtime used by uv. Default: 3.11
  SKILLX_NEXT_PAIR_PLAN_MODE
                            full_matrix or challenger_eval. Default: full_matrix
  SKILLX_MIN_SUPPORT_SIZE   Rewrite support floor. Default comes from Python wrapper, currently 0.
  SKILLX_MAX_UPDATE_SCHEMAS Max rewritten schemas. Default comes from Python wrapper, currently 0.
  SKILLX_MAX_EVAL_TASKS_PER_SCHEMA
                            Max next-round eval tasks per schema. Default: 6
  SKILLX_ROUND_BUDGET       Inner-loop round budget for next pair specs. Default: 3
  SKILLX_AGENT              Next inner-loop executor agent. Default: claude-code
  SKILLX_MODEL              Next inner-loop executor model. Default: anthropic/claude-sonnet-4-5
  SKILLX_SKILLSBENCH_ROOT   Optional SkillsBench source checkout.
  SKILLX_ALLOW_PARTIAL_ASSIGNMENT
                            1 passes --allow-partial-assignment. Default: 0

Behavior:
  - exports a run_report.json for the completed inner-loop run
  - rebuilds global_pair_status.json
  - runs scripts/run_outer_loop_optimization.py
  - verifies schema rewrite completion through rewrite_verification.json
  - materializes the next round's candidate schema-task pairs
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXP_WORKTREE="${SKILLX_EXP_WORKTREE:-$WORKTREE_ROOT}"

resolve_path() {
  local raw_path="$1"
  if [[ "$raw_path" = /* ]]; then
    printf '%s\n' "$raw_path"
  else
    printf '%s\n' "$EXP_WORKTREE/$raw_path"
  fi
}

DEFAULT_PREVIOUS_ROOT="experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2"
PREVIOUS_MATERIALIZED_ROOT="$(resolve_path "${SKILLX_PREVIOUS_MATERIALIZED_ROOT:-$DEFAULT_PREVIOUS_ROOT}")"
ROUND_ROOT="${SKILLX_ROUND_ROOT:-$(dirname "$PREVIOUS_MATERIALIZED_ROOT")}"
ROUND_ROOT="$(resolve_path "$ROUND_ROOT")"

INNER_RUN_LABEL="${1:-${SKILLX_INNER_RUN_LABEL:-}}"
OUTER_LABEL="${2:-${SKILLX_OUTER_LABEL:-outer-loop-step-$(date +%Y-%m-%d-%H%M)}}"
ROUND_ID="${SKILLX_ROUND_ID:-outer-loop-round0}"
NEXT_ROUND_ID="${SKILLX_NEXT_ROUND_ID:-outer-loop-round1}"
DEFAULT_NEXT_MATERIALIZED_ROOT="$ROUND_ROOT/${NEXT_ROUND_ID}-candidate-rerun-$OUTER_LABEL"
NEXT_MATERIALIZED_ROOT="$(resolve_path "${3:-${SKILLX_NEXT_MATERIALIZED_ROOT:-$DEFAULT_NEXT_MATERIALIZED_ROOT}}")"

EXPORT_REPORT="${SKILLX_EXPORT_REPORT:-1}"
BUILD_GLOBAL_STATUS="${SKILLX_BUILD_GLOBAL_STATUS:-1}"
CONTROL_PLANE_OUTPUT_DIR="$ROUND_ROOT/reports/$OUTER_LABEL/control-plane"
SCHEMA_UPDATE_OUTPUT_DIR="$ROUND_ROOT/reports/$OUTER_LABEL/schema-updates"
GLOBAL_STATUS_PATH="$ROUND_ROOT/reports/global-round0-status/global_pair_status.json"
NEXT_RUN_ID="${SKILLX_NEXT_RUN_ID:-$NEXT_ROUND_ID-candidates-$OUTER_LABEL}"
REWRITE_MODE="${SKILLX_REWRITE_MODE:-llm}"
LLM_MODEL="${SKILLX_LLM_MODEL:-anthropic/claude-sonnet-4-5}"
PYTHON_RUNTIME="${SKILLX_PYTHON:-3.11}"
NEXT_PAIR_PLAN_MODE="${SKILLX_NEXT_PAIR_PLAN_MODE:-full_matrix}"
MAX_EVAL_TASKS_PER_SCHEMA="${SKILLX_MAX_EVAL_TASKS_PER_SCHEMA:-6}"
ROUND_BUDGET="${SKILLX_ROUND_BUDGET:-3}"
AGENT="${SKILLX_AGENT:-claude-code}"
MODEL="${SKILLX_MODEL:-anthropic/claude-sonnet-4-5}"
ALLOW_PARTIAL_ASSIGNMENT="${SKILLX_ALLOW_PARTIAL_ASSIGNMENT:-0}"

if [[ ! -d "$EXP_WORKTREE" ]]; then
  echo "Missing experiment worktree: $EXP_WORKTREE" >&2
  exit 1
fi
if [[ ! -f "$PREVIOUS_MATERIALIZED_ROOT/manifest.json" ]]; then
  echo "Missing previous materialized root manifest: $PREVIOUS_MATERIALIZED_ROOT/manifest.json" >&2
  exit 1
fi
if [[ "$EXPORT_REPORT" == "1" && -z "$INNER_RUN_LABEL" ]]; then
  echo "inner-run-label is required when SKILLX_EXPORT_REPORT=1" >&2
  exit 1
fi
if [[ -d "$NEXT_MATERIALIZED_ROOT" ]] && find "$NEXT_MATERIALIZED_ROOT" -mindepth 1 -print -quit | grep -q .; then
  echo "Next materialized root already exists and is non-empty: $NEXT_MATERIALIZED_ROOT" >&2
  echo "Choose a new outer label or remove the existing root first." >&2
  exit 1
fi

cd "$EXP_WORKTREE"

if [[ "$EXPORT_REPORT" == "1" ]]; then
  uv run --python "$PYTHON_RUNTIME" python scripts/export_round0_run_report.py \
    --materialized-root "$PREVIOUS_MATERIALIZED_ROOT" \
    --run-label "$INNER_RUN_LABEL"
fi

if [[ "$BUILD_GLOBAL_STATUS" == "1" ]]; then
  global_status_cmd=(
    uv
    run
    --python
    "$PYTHON_RUNTIME"
    python
    scripts/build_round0_global_status.py
    --round0-root
    "$ROUND_ROOT"
  )
  if [[ -n "${SKILLX_SKILLSBENCH_ROOT:-}" ]]; then
    global_status_cmd+=(--skillsbench-root "$(resolve_path "$SKILLX_SKILLSBENCH_ROOT")")
  fi
  "${global_status_cmd[@]}"
fi

outer_cmd=(
  uv
  run
  --python
  "$PYTHON_RUNTIME"
  python
  scripts/run_outer_loop_optimization.py
  --round0-root
  "$ROUND_ROOT"
  --global-pair-status-path
  "$GLOBAL_STATUS_PATH"
  --control-plane-output-dir
  "$CONTROL_PLANE_OUTPUT_DIR"
  --schema-update-output-dir
  "$SCHEMA_UPDATE_OUTPUT_DIR"
  --next-materialized-root
  "$NEXT_MATERIALIZED_ROOT"
  --round-id
  "$ROUND_ID"
  --next-round-id
  "$NEXT_ROUND_ID"
  --next-run-id
  "$NEXT_RUN_ID"
  --round-budget
  "$ROUND_BUDGET"
  --agent
  "$AGENT"
  --model
  "$MODEL"
  --rewrite-mode
  "$REWRITE_MODE"
  --llm-model
  "$LLM_MODEL"
  --next-pair-plan-mode
  "$NEXT_PAIR_PLAN_MODE"
  --max-eval-tasks-per-schema
  "$MAX_EVAL_TASKS_PER_SCHEMA"
)
if [[ -n "${SKILLX_MIN_SUPPORT_SIZE:-}" ]]; then
  outer_cmd+=(--min-support-size "$SKILLX_MIN_SUPPORT_SIZE")
fi
if [[ -n "${SKILLX_MAX_UPDATE_SCHEMAS:-}" ]]; then
  outer_cmd+=(--max-update-schemas "$SKILLX_MAX_UPDATE_SCHEMAS")
fi
if [[ -n "${SKILLX_SKILLSBENCH_ROOT:-}" ]]; then
  outer_cmd+=(--skillsbench-root "$(resolve_path "$SKILLX_SKILLSBENCH_ROOT")")
fi
if [[ "$ALLOW_PARTIAL_ASSIGNMENT" == "1" || "$ALLOW_PARTIAL_ASSIGNMENT" == "true" ]]; then
  outer_cmd+=(--allow-partial-assignment)
fi

"${outer_cmd[@]}"

echo "Completed SkillX outer-loop step"
echo "  previous-materialized-root: $PREVIOUS_MATERIALIZED_ROOT"
echo "  inner-run-label: ${INNER_RUN_LABEL:-skipped}"
echo "  round-root: $ROUND_ROOT"
echo "  outer-label: $OUTER_LABEL"
echo "  python: $PYTHON_RUNTIME"
echo "  next-pair-plan-mode: $NEXT_PAIR_PLAN_MODE"
echo "  control-plane: $CONTROL_PLANE_OUTPUT_DIR"
echo "  schema-updates: $SCHEMA_UPDATE_OUTPUT_DIR"
echo "  rewrite-verification: $SCHEMA_UPDATE_OUTPUT_DIR/rewrite_verification.json"
echo "  next-materialized-root: $NEXT_MATERIALIZED_ROOT"
