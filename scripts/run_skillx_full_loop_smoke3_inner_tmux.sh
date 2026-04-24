#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run_skillx_full_loop_smoke3_inner_tmux.sh [run-label] [session-name] [monitor-port]

Starts the round1 inner-loop smoke run in tmux using the candidate pairs produced by:

  scripts/run_skillx_full_loop_smoke3_outer_step.sh round0

Environment overrides:
  SKILLX_SMOKE_ROOT    Default: experiments/.../full-loop-smoke-3task-v0.1
  SKILLX_ROUND_BUDGET  Default: 3
  SKILLX_AGENT         Default: claude-code
  SKILLX_MODEL         Default: anthropic/claude-sonnet-4-5
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

SMOKE_ROOT="${SKILLX_SMOKE_ROOT:-experiments/skillx-skillsbench-001/results/full-loop-smoke-3task-v0.1}"
MATERIALIZED_ROOT="$SMOKE_ROOT/outer-loop-round1-smoke-candidates"

RUN_LABEL="${1:-run-full-loop-smoke3-round1-inner-$(date +%Y-%m-%d-%H%M)}"
SESSION_NAME="${2:-skillx-full-loop-smoke3-r1}"
MONITOR_PORT="${3:-}"

if [[ ! -f "$MATERIALIZED_ROOT/manifest.json" ]]; then
  echo "Missing materialized root. Run outer step first:" >&2
  echo "  scripts/run_skillx_full_loop_smoke3_outer_step.sh round0" >&2
  exit 1
fi

args=("$RUN_LABEL" "$SESSION_NAME")
if [[ -n "$MONITOR_PORT" ]]; then
  args+=("$MONITOR_PORT")
fi

SKILLX_MATERIALIZED_ROOT="$MATERIALIZED_ROOT" \
  scripts/run_skillx_inner_loop_tmux.sh "${args[@]}"
