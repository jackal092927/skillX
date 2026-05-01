#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run_skillx_first20_outer_step.sh [completed-inner-run-label] [outer-label] [next-materialized-root]

Example:
  scripts/run_skillx_first20_outer_step.sh run-first20x7-round0-2026-04-24 outer-loop-round1-first20-2026-04-24

Environment overrides:
  SKILLX_EXP_WORKTREE                Experiment worktree. Default: current checkout.
  SKILLX_PREVIOUS_MATERIALIZED_ROOT  Completed inner-loop materialized root.
  SKILLX_NEXT_MATERIALIZED_ROOT      Next-round candidate materialized root.
  SKILLX_TASK_SLICE                  First20 task slice. Defaults to sonnet45-task-list-first20-v0.1.json.
  SKILLX_REWRITE_MODE                llm or deterministic. Default: llm.
  SKILLX_LLM_MODEL                   Outer-loop rewriter model. Default: anthropic/claude-sonnet-4-5.
  SKILLX_NEXT_PAIR_PLAN_MODE         Default: full_matrix.
  SKILLX_MAX_UPDATE_SCHEMAS          Default inherited from Python wrapper; unset means rewrite all eligible schemas.
  SKILLX_MIN_SUPPORT_SIZE            Default inherited from Python wrapper.
  SKILLX_PYTHON                      Python runtime used by uv. Default: 3.11.

Behavior:
  - exports the completed inner-loop run report
  - rebuilds global status
  - runs the outer-loop assignment + schema rewrite step
  - materializes next-round task x rewritten-schema pairs
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXP_WORKTREE="${SKILLX_EXP_WORKTREE:-$WORKTREE_ROOT}"

DEFAULT_PREVIOUS_ROOT="experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1"
DEFAULT_TASK_SLICE="experiments/skillx-skillsbench-001/results/official-task-results/sonnet45-task-list-first20-v0.1.json"
PREVIOUS_MATERIALIZED_ROOT="${SKILLX_PREVIOUS_MATERIALIZED_ROOT:-$DEFAULT_PREVIOUS_ROOT}"
TASK_SLICE="${SKILLX_TASK_SLICE:-$DEFAULT_TASK_SLICE}"
OUTER_LABEL="${2:-${SKILLX_OUTER_LABEL:-outer-loop-round1-first20-$(date +%Y-%m-%d-%H%M)}}"
DEFAULT_NEXT_ROOT="experiments/skillx-skillsbench-001/results/outer-loop-round0/$OUTER_LABEL-candidates"
NEXT_MATERIALIZED_ROOT="${3:-${SKILLX_NEXT_MATERIALIZED_ROOT:-$DEFAULT_NEXT_ROOT}}"

if [[ $# -lt 1 ]]; then
  echo "completed-inner-run-label is required" >&2
  usage >&2
  exit 1
fi
if [[ $# -gt 3 ]]; then
  echo "Unexpected extra arguments: ${*:4}" >&2
  usage >&2
  exit 1
fi

cd "$EXP_WORKTREE"

SUMMARY_PATH="$EXP_WORKTREE/$PREVIOUS_MATERIALIZED_ROOT/launcher_logs/$1/summary.json"
if [[ "$PREVIOUS_MATERIALIZED_ROOT" = /* ]]; then
  SUMMARY_PATH="$PREVIOUS_MATERIALIZED_ROOT/launcher_logs/$1/summary.json"
fi
if [[ ! -f "$SUMMARY_PATH" ]]; then
  echo "Missing completed first20 inner-loop summary: $SUMMARY_PATH" >&2
  echo "Run the inner loop first, then rerun this outer step." >&2
  echo >&2
  echo "Expected first command:" >&2
  echo "  cd $EXP_WORKTREE" >&2
  echo "  scripts/run_skillx_first20_round0_tmux.sh \\" >&2
  echo "    $1 \\" >&2
  echo "    skillx-round0-first20x7 \\" >&2
  echo "    8767" >&2
  exit 1
fi

SKILLX_EXP_WORKTREE="$EXP_WORKTREE" \
SKILLX_PREVIOUS_MATERIALIZED_ROOT="$PREVIOUS_MATERIALIZED_ROOT" \
SKILLX_TASK_SLICE="$TASK_SLICE" \
SKILLX_NEXT_PAIR_PLAN_MODE="${SKILLX_NEXT_PAIR_PLAN_MODE:-full_matrix}" \
SKILLX_REWRITE_MODE="${SKILLX_REWRITE_MODE:-llm}" \
SKILLX_LLM_MODEL="${SKILLX_LLM_MODEL:-anthropic/claude-sonnet-4-5}" \
SKILLX_PYTHON="${SKILLX_PYTHON:-3.11}" \
scripts/run_skillx_outer_loop_step.sh "$1" "$OUTER_LABEL" "$NEXT_MATERIALIZED_ROOT"
