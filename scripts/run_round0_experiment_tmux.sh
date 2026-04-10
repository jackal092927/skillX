#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run_round0_experiment_tmux.sh [target] [run-label] [session-name]

Defaults:
  target: 3
  run-label: run-3x7-2026-04-10
  session-name: skillx-round0

Environment overrides:
  SKILLX_EXP_WORKTREE   Absolute path to the experiment worktree
  SKILLX_TARGET         Default launcher target when arg 1 is omitted
  SKILLX_RUN_LABEL      Default run label when arg 2 is omitted
  SKILLX_TMUX_SESSION   Default tmux session name when arg 3 is omitted

Behavior:
  - starts the round0 launcher inside tmux
  - wraps the launcher with caffeinate
  - tees stdout into launcher_logs/<run-label>/launcher.stdout.log
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GIT_COMMON_DIR="$(git -C "$WORKTREE_ROOT" rev-parse --git-common-dir)"
SHARED_REPO_ROOT="$(cd "$GIT_COMMON_DIR/.." && pwd)"

EXP_WORKTREE="${SKILLX_EXP_WORKTREE:-$SHARED_REPO_ROOT/.worktrees/exp/2026-04-10-round0-3x7}"
TARGET="${1:-${SKILLX_TARGET:-3}}"
RUN_LABEL="${2:-${SKILLX_RUN_LABEL:-run-3x7-2026-04-10}}"
SESSION_NAME="${3:-${SKILLX_TMUX_SESSION:-skillx-round0}}"

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

COMMAND="cd $EXP_WORKTREE && caffeinate -dimsu uv run python -u scripts/launch_skillx_round0.py $TARGET --output-suffix $RUN_LABEL 2>&1 | tee $STDOUT_LOG_PATH"

tmux new-session -d -s "$SESSION_NAME"
tmux send-keys -t "$SESSION_NAME" "$COMMAND" C-m

echo "Started round0 launcher in tmux"
echo "  session: $SESSION_NAME"
echo "  target: $TARGET"
echo "  run-label: $RUN_LABEL"
echo "  worktree: $EXP_WORKTREE"
echo "  stdout-log: $STDOUT_LOG_PATH"
echo
echo "Attach:"
echo "  tmux attach -t $SESSION_NAME"
