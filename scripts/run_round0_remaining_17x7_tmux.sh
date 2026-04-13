#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run_round0_remaining_17x7_tmux.sh [run-label] [session-name] [monitor-port]

Defaults:
  run-label: run-remaining-17x7-2026-04-11
  session-name: skillx-round0-remaining-17x7
  monitor-port: first free port starting from 8767
  experiment worktree: current checkout

Environment overrides:
  SKILLX_EXP_WORKTREE   Absolute path to the experiment worktree
  SKILLX_RUN_LABEL      Default run label when arg 1 is omitted
  SKILLX_TMUX_SESSION   Default tmux session name when arg 2 is omitted
  SKILLX_MONITOR_PORT   Explicit dashboard port
  SKILLX_MONITOR_PORT_BASE  Starting port for auto-selection, default 8767
  SKILLX_OVERRIDE_MEMORY_MB   Synthetic task memory override, default 8192
  SKILLX_OVERRIDE_STORAGE_MB  Synthetic task storage override, default 20480

Behavior:
  - rematerializes the round0 pair specs before launch
  - runs task indices 4 through 20 from the fixed round0 slice
  - creates a tmux session with two windows: run, dashboard
  - wraps the launcher with caffeinate inside tmux
  - tees stdout into launcher_logs/<run-label>/launcher.stdout.log
  - serves the dashboard via scripts/run_round0_monitor.sh
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
REQUESTED_MONITOR_PORT="${3:-${SKILLX_MONITOR_PORT:-}}"
MONITOR_PORT_BASE="${SKILLX_MONITOR_PORT_BASE:-8767}"
OVERRIDE_MEMORY_MB="${SKILLX_OVERRIDE_MEMORY_MB:-8192}"
OVERRIDE_STORAGE_MB="${SKILLX_OVERRIDE_STORAGE_MB:-20480}"

RESULTS_ROOT="$EXP_WORKTREE/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2"
LAUNCHER_LOG_DIR="$RESULTS_ROOT/launcher_logs/$RUN_LABEL"
STDOUT_LOG_PATH="$LAUNCHER_LOG_DIR/launcher.stdout.log"

if [[ ! -d "$EXP_WORKTREE" ]]; then
  echo "Missing experiment worktree: $EXP_WORKTREE" >&2
  exit 1
fi

if [[ -d "$LAUNCHER_LOG_DIR" ]] && find "$LAUNCHER_LOG_DIR" -mindepth 1 -print -quit | grep -q .; then
  echo "Launcher log dir already exists and is non-empty: $LAUNCHER_LOG_DIR" >&2
  echo "Choose a new run label or remove the existing log dir first." >&2
  exit 1
fi

mkdir -p "$LAUNCHER_LOG_DIR"

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "tmux session already exists: $SESSION_NAME" >&2
  echo "Attach with: tmux attach -t $SESSION_NAME" >&2
  exit 1
fi

is_port_busy() {
  local port="$1"
  if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

resolve_monitor_port() {
  local requested_port="$1"
  local base_port="$2"
  local port
  if [[ -n "$requested_port" ]]; then
    if is_port_busy "$requested_port"; then
      echo "Requested monitor port is already in use: $requested_port" >&2
      exit 1
    fi
    printf '%s\n' "$requested_port"
    return 0
  fi

  for ((port = base_port; port < base_port + 100; port++)); do
    if ! is_port_busy "$port"; then
      printf '%s\n' "$port"
      return 0
    fi
  done

  echo "Could not find a free monitor port starting from $base_port" >&2
  exit 1
}

MONITOR_PORT="$(resolve_monitor_port "$REQUESTED_MONITOR_PORT" "$MONITOR_PORT_BASE")"

launcher_cmd=(
  uv run python -u scripts/launch_skillx_round0.py
)
for index in {4..20}; do
  launcher_cmd+=(--task-index "$index")
done
launcher_cmd+=(
  --output-suffix "$RUN_LABEL"
  --override-memory-mb "$OVERRIDE_MEMORY_MB"
  --override-storage-mb "$OVERRIDE_STORAGE_MB"
  --docker-auto-recover
)

printf -v launcher_cmd_quoted '%q ' "${launcher_cmd[@]}"
printf -v run_command 'cd %q && scripts/rematerialize_round0_root.sh && caffeinate -dimsu %s2>&1 | tee %q' \
  "$EXP_WORKTREE" \
  "$launcher_cmd_quoted" \
  "$STDOUT_LOG_PATH"
printf -v dashboard_command 'cd %q && scripts/run_round0_monitor.sh %q %q' \
  "$EXP_WORKTREE" \
  "$RUN_LABEL" \
  "$MONITOR_PORT"

tmux new-session -d -s "$SESSION_NAME" -n run
tmux send-keys -t "$SESSION_NAME":run "$run_command" C-m
tmux new-window -t "$SESSION_NAME" -n dashboard
tmux send-keys -t "$SESSION_NAME":dashboard "$dashboard_command" C-m
tmux select-window -t "$SESSION_NAME":run

echo "Started remaining round0 launcher in tmux"
echo "  session: $SESSION_NAME"
echo "  windows: run, dashboard"
echo "  task-indices: 4-20"
echo "  run-label: $RUN_LABEL"
echo "  override-memory-mb: $OVERRIDE_MEMORY_MB"
echo "  override-storage-mb: $OVERRIDE_STORAGE_MB"
echo "  worktree: $EXP_WORKTREE"
echo "  stdout-log: $STDOUT_LOG_PATH"
echo "  dashboard: http://127.0.0.1:$MONITOR_PORT/"
echo
echo "Attach:"
echo "  tmux attach -t $SESSION_NAME"
