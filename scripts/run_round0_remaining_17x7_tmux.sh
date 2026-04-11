#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run_round0_remaining_17x7_tmux.sh [run-label] [session-name]

Defaults:
  run-label: run-remaining-17x7-2026-04-11
  session-name: skillx-round0-remaining-17x7
  experiment worktree: current checkout

Environment overrides:
  SKILLX_EXP_WORKTREE   Absolute path to the experiment worktree
  SKILLX_RUN_LABEL      Default run label when arg 1 is omitted
  SKILLX_TMUX_SESSION   Default tmux session name when arg 2 is omitted

Behavior:
  - runs task indices 4 through 20 from the fixed round0 slice
  - wraps the launcher with caffeinate inside tmux
  - tees stdout into launcher_logs/<run-label>/launcher.stdout.log
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXP_WORKTREE="${SKILLX_EXP_WORKTREE:-$WORKTREE_ROOT}"
RUN_LABEL="${1:-${SKILLX_RUN_LABEL:-run-remaining-17x7-2026-04-11}}"
SESSION_NAME="${2:-${SKILLX_TMUX_SESSION:-skillx-round0-remaining-17x7}}"

RESULTS_ROOT="$EXP_WORKTREE/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2"
LAUNCHER_LOG_DIR="$RESULTS_ROOT/launcher_logs/$RUN_LABEL"
STDOUT_LOG_PATH="$LAUNCHER_LOG_DIR/launcher.stdout.log"

if [[ ! -d "$EXP_WORKTREE" ]]; then
  echo "Missing experiment worktree: $EXP_WORKTREE" >&2
  exit 1
fi

mkdir -p "$LAUNCHER_LOG_DIR"

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "tmux session already exists: $SESSION_NAME" >&2
  echo "Attach with: tmux attach -t $SESSION_NAME" >&2
  exit 1
fi

launcher_cmd=(
  uv run python -u scripts/launch_skillx_round0.py
)
for index in {4..20}; do
  launcher_cmd+=(--task-index "$index")
done
launcher_cmd+=(--output-suffix "$RUN_LABEL")

printf -v launcher_cmd_quoted '%q ' "${launcher_cmd[@]}"
printf -v command 'cd %q && caffeinate -dimsu %s2>&1 | tee %q' \
  "$EXP_WORKTREE" \
  "$launcher_cmd_quoted" \
  "$STDOUT_LOG_PATH"

tmux new-session -d -s "$SESSION_NAME"
tmux send-keys -t "$SESSION_NAME" "$command" C-m

echo "Started remaining round0 launcher in tmux"
echo "  session: $SESSION_NAME"
echo "  task-indices: 4-20"
echo "  run-label: $RUN_LABEL"
echo "  worktree: $EXP_WORKTREE"
echo "  stdout-log: $STDOUT_LOG_PATH"
echo
echo "Attach:"
echo "  tmux attach -t $SESSION_NAME"
