#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run_round0_rerun_recovery_tmux.sh [run-label] [session-name] [monitor-port]

Defaults:
  run-label: run-round0-rerun-recovery-2026-04-13
  session-name: skillx-round0-rerun-recovery
  monitor-port: first free port starting from 8771

Behavior:
  - rematerializes the rerun-recovery root
  - launches the full frozen rerun batch via pair manifest
  - creates tmux windows: run, dashboard
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXP_WORKTREE="${SKILLX_EXP_WORKTREE:-$WORKTREE_ROOT}"
RUN_LABEL="${1:-${SKILLX_RUN_LABEL:-run-round0-rerun-recovery-2026-04-13}}"
SESSION_NAME="${2:-${SKILLX_TMUX_SESSION:-skillx-round0-rerun-recovery}}"
REQUESTED_MONITOR_PORT="${3:-${SKILLX_MONITOR_PORT:-}}"
MONITOR_PORT_BASE="${SKILLX_MONITOR_PORT_BASE:-8771}"
OVERRIDE_MEMORY_MB="${SKILLX_OVERRIDE_MEMORY_MB:-8192}"
OVERRIDE_STORAGE_MB="${SKILLX_OVERRIDE_STORAGE_MB:-20480}"
RESULTS_ROOT="${SKILLX_RESULTS_ROOT:-$EXP_WORKTREE/experiments/skillx-skillsbench-001/results/outer-loop-round0/round0-rerun-recovery-v0.1}"
PAIR_MANIFEST_PATH="${SKILLX_PAIR_MANIFEST_PATH:-$EXP_WORKTREE/experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/rerun-recovery/round0-rerun-recovery-v0.1.pair-manifest.json}"
TASK_SLICE_PATH="${SKILLX_TASK_SLICE_PATH:-$EXP_WORKTREE/experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/rerun-recovery/round0-rerun-recovery-v0.1.task-slice.json}"
LAUNCHER_LOG_DIR="$RESULTS_ROOT/launcher_logs/$RUN_LABEL"
STDOUT_LOG_PATH="$LAUNCHER_LOG_DIR/launcher.stdout.log"

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

if [[ -d "$LAUNCHER_LOG_DIR" ]] && find "$LAUNCHER_LOG_DIR" -mindepth 1 -print -quit | grep -q .; then
  echo "Launcher log dir already exists and is non-empty: $LAUNCHER_LOG_DIR" >&2
  exit 1
fi

mkdir -p "$LAUNCHER_LOG_DIR"

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "tmux session already exists: $SESSION_NAME" >&2
  exit 1
fi

MONITOR_PORT="$(resolve_monitor_port "$REQUESTED_MONITOR_PORT" "$MONITOR_PORT_BASE")"

launcher_cmd=(
  uv run python -u scripts/launch_skillx_round0.py
  --task-slice "$TASK_SLICE_PATH"
  --materialized-root "$RESULTS_ROOT"
  --pair-manifest "$PAIR_MANIFEST_PATH"
  --output-suffix "$RUN_LABEL"
  --override-memory-mb "$OVERRIDE_MEMORY_MB"
  --override-storage-mb "$OVERRIDE_STORAGE_MB"
  --docker-auto-recover
)

printf -v launcher_cmd_quoted '%q ' "${launcher_cmd[@]}"
printf -v run_command 'cd %q && scripts/rematerialize_round0_rerun_recovery_root.sh && caffeinate -dimsu %s2>&1 | tee %q' \
  "$EXP_WORKTREE" \
  "$launcher_cmd_quoted" \
  "$STDOUT_LOG_PATH"
printf -v dashboard_command 'cd %q && SKILLX_RESULTS_ROOT=%q scripts/run_round0_monitor.sh %q %q %q' \
  "$EXP_WORKTREE" \
  "$RESULTS_ROOT" \
  "$RUN_LABEL" \
  "$MONITOR_PORT" \
  "$RESULTS_ROOT"

tmux new-session -d -s "$SESSION_NAME" -n run
tmux send-keys -t "$SESSION_NAME":run "$run_command" C-m
tmux new-window -t "$SESSION_NAME" -n dashboard
tmux send-keys -t "$SESSION_NAME":dashboard "$dashboard_command" C-m
tmux select-window -t "$SESSION_NAME":run

echo "Started round0 rerun recovery in tmux"
echo "  session: $SESSION_NAME"
echo "  windows: run, dashboard"
echo "  run-label: $RUN_LABEL"
echo "  results-root: $RESULTS_ROOT"
echo "  pair-manifest: $PAIR_MANIFEST_PATH"
echo "  stdout-log: $STDOUT_LOG_PATH"
echo "  dashboard: http://127.0.0.1:$MONITOR_PORT/"
echo
echo "Attach:"
echo "  tmux attach -t $SESSION_NAME"
