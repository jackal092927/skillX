#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run_skillx_full_loop_smoke3_outer_step.sh round0
  scripts/run_skillx_full_loop_smoke3_outer_step.sh round1 <inner-run-label>

Purpose:
  Runs one outer-loop optimization step for the three-task full-loop smoke test.

Flow:
  round0: use existing historical round0 inner-loop reports for the selected tasks,
          then materialize round1 candidate pairs.
  round1: export the completed round1 inner-loop report, use it as feedback,
          then produce the final round2 schema/candidate artifacts and stop.

Environment overrides:
  SKILLX_SMOKE_ROOT                 Default: experiments/.../full-loop-smoke-3task-v0.1
  SKILLX_REWRITE_MODE               llm or deterministic. Default: llm
  SKILLX_LLM_MODEL                  Default: anthropic/claude-sonnet-4-5
  SKILLX_MAX_EVAL_TASKS_PER_SCHEMA  Default: 3
  SKILLX_ROUND_BUDGET               Default: 3
  SKILLX_AGENT                      Default: claude-code
  SKILLX_MODEL                      Default: anthropic/claude-sonnet-4-5
  SKILLX_SKILLSBENCH_ROOT           Optional SkillsBench source checkout.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || $# -lt 1 ]]; then
  usage
  exit 0
fi

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WORKTREE_ROOT"

STEP="$1"
INNER_RUN_LABEL="${2:-}"

TASKS=(
  citation-check
  pdf-excel-diff
  court-form-filling
)

SCHEMA_IDS=(
  artifact-generation
  analytic-pipeline
  engineering-composition
  retrieval-heavy-synthesis
  environment-control
  methodology-guardrail
  orchestration-delegation
)

SMOKE_ROOT="${SKILLX_SMOKE_ROOT:-experiments/skillx-skillsbench-001/results/full-loop-smoke-3task-v0.1}"
REWRITE_MODE="${SKILLX_REWRITE_MODE:-llm}"
LLM_MODEL="${SKILLX_LLM_MODEL:-anthropic/claude-sonnet-4-5}"
MAX_EVAL_TASKS_PER_SCHEMA="${SKILLX_MAX_EVAL_TASKS_PER_SCHEMA:-3}"
ROUND_BUDGET="${SKILLX_ROUND_BUDGET:-3}"
AGENT="${SKILLX_AGENT:-claude-code}"
MODEL="${SKILLX_MODEL:-anthropic/claude-sonnet-4-5}"

task_args=()
for task in "${TASKS[@]}"; do
  task_args+=(--task "$task")
done
schema_args=()
for schema_id in "${SCHEMA_IDS[@]}"; do
  schema_args+=(--schema-id "$schema_id")
done

skillsbench_args=()
if [[ -n "${SKILLX_SKILLSBENCH_ROOT:-}" ]]; then
  skillsbench_args+=(--skillsbench-root "$SKILLX_SKILLSBENCH_ROOT")
fi

case "$STEP" in
  round0)
    ROUND_ROOT="experiments/skillx-skillsbench-001/results/outer-loop-round0"
    OUTER_LABEL="outer-loop-round1-smoke"
    ROUND_ID="outer-loop-round0-smoke"
    NEXT_ROUND_ID="outer-loop-round1-smoke"
    NEXT_ROOT="$SMOKE_ROOT/outer-loop-round1-smoke-candidates"
    GLOBAL_STATUS_DIR="$SMOKE_ROOT/reports/round0-global-status"
    ;;
  round1)
    if [[ -z "$INNER_RUN_LABEL" ]]; then
      echo "round1 requires the completed round1 inner-loop run label." >&2
      exit 1
    fi
    ROUND_ROOT="$SMOKE_ROOT"
    PREVIOUS_MATERIALIZED_ROOT="$SMOKE_ROOT/outer-loop-round1-smoke-candidates"
    if [[ ! -f "$PREVIOUS_MATERIALIZED_ROOT/manifest.json" ]]; then
      echo "Missing round1 materialized root: $PREVIOUS_MATERIALIZED_ROOT" >&2
      exit 1
    fi
    uv run python scripts/export_round0_run_report.py \
      --materialized-root "$PREVIOUS_MATERIALIZED_ROOT" \
      --run-label "$INNER_RUN_LABEL"
    OUTER_LABEL="outer-loop-round2-smoke"
    ROUND_ID="outer-loop-round1-smoke"
    NEXT_ROUND_ID="outer-loop-round2-smoke"
    NEXT_ROOT="$SMOKE_ROOT/outer-loop-round2-smoke-candidates"
    GLOBAL_STATUS_DIR="$SMOKE_ROOT/reports/round1-global-status"
    ;;
  *)
    echo "Unknown step: $STEP" >&2
    usage >&2
    exit 1
    ;;
esac

if [[ -d "$NEXT_ROOT" ]] && find "$NEXT_ROOT" -mindepth 1 -print -quit | grep -q .; then
  echo "Next materialized root already exists and is non-empty: $NEXT_ROOT" >&2
  exit 1
fi

uv run python scripts/build_round0_global_status.py \
  --round0-root "$ROUND_ROOT" \
  --output-dir "$GLOBAL_STATUS_DIR" \
  ${skillsbench_args[@]+"${skillsbench_args[@]}"} \
  "${task_args[@]}" \
  "${schema_args[@]}"

uv run python scripts/run_outer_loop_optimization.py \
  --round0-root "$ROUND_ROOT" \
  --global-pair-status-path "$GLOBAL_STATUS_DIR/global_pair_status.json" \
  --control-plane-output-dir "$SMOKE_ROOT/reports/$OUTER_LABEL/control-plane" \
  --schema-update-output-dir "$SMOKE_ROOT/reports/$OUTER_LABEL/schema-updates" \
  --next-materialized-root "$NEXT_ROOT" \
  --round-id "$ROUND_ID" \
  --next-round-id "$NEXT_ROUND_ID" \
  --next-run-id "$NEXT_ROUND_ID-candidates" \
  --round-budget "$ROUND_BUDGET" \
  --agent "$AGENT" \
  --model "$MODEL" \
  --rewrite-mode "$REWRITE_MODE" \
  --llm-model "$LLM_MODEL" \
  --max-eval-tasks-per-schema "$MAX_EVAL_TASKS_PER_SCHEMA" \
  --allow-partial-assignment \
  ${skillsbench_args[@]+"${skillsbench_args[@]}"}

echo "Completed full-loop smoke outer step"
echo "  step: $STEP"
echo "  tasks: ${TASKS[*]}"
echo "  schema-ids: ${SCHEMA_IDS[*]}"
echo "  global-status: $GLOBAL_STATUS_DIR/global_pair_status.json"
echo "  schema-updates: $SMOKE_ROOT/reports/$OUTER_LABEL/schema-updates"
echo "  next-materialized-root: $NEXT_ROOT"
