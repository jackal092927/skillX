#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run_metric_gated_scientific_pipeline_tmux.sh [target] [run-label] [session-name] [monitor-port]

Defaults:
  target: 4
  run-label: run-metric-gated-scientific-pipeline-v0.1
  session-name: skillx-metric-gated-sci
  monitor-port: first free port starting from 8771
  experiment worktree: current checkout

Environment overrides:
  SKILLX_EXP_WORKTREE       Absolute path to the experiment worktree
  SKILLX_TARGET             Default launcher target when arg 1 is omitted
  SKILLX_RUN_LABEL          Default run label when arg 2 is omitted
  SKILLX_TMUX_SESSION       Default tmux session name when arg 3 is omitted
  SKILLX_MONITOR_PORT       Explicit dashboard port
  SKILLX_MONITOR_PORT_BASE  Starting port for auto-selection, default 8771

Behavior:
  - rematerializes the sidecar 4-task / 1-schema pair specs before launch
  - creates a tmux session with two windows: run, dashboard
  - wraps the launcher with caffeinate inside tmux
  - tees stdout into launcher_logs/<run-label>/launcher.stdout.log
  - serves the dashboard via scripts/run_metric_gated_scientific_pipeline_monitor.sh
  - exports a round-0 report after the launcher finishes
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXP_WORKTREE="${SKILLX_EXP_WORKTREE:-$WORKTREE_ROOT}"
TARGET="${1:-${SKILLX_TARGET:-4}}"
RUN_LABEL="${2:-${SKILLX_RUN_LABEL:-run-metric-gated-scientific-pipeline-v0.1}}"
SESSION_NAME="${3:-${SKILLX_TMUX_SESSION:-skillx-metric-gated-sci}}"
REQUESTED_MONITOR_PORT="${4:-${SKILLX_MONITOR_PORT:-}}"
MONITOR_PORT_BASE="${SKILLX_MONITOR_PORT_BASE:-8771}"
TMUX_BIN="$(command -v tmux)"
UV_BIN="$(command -v uv)"
CAFFEINATE_BIN="$(command -v caffeinate)"

TASK_SLICE="experiments/skillx-skillsbench-001/results/official-task-results/metric-gated-scientific-pipeline-strong-candidates-v0.1.json"
RESULTS_ROOT="$EXP_WORKTREE/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-metric-gated-scientific-pipeline-4task-v0.1"
LAUNCHER_LOG_DIR="$RESULTS_ROOT/launcher_logs/$RUN_LABEL"
STDOUT_LOG_PATH="$LAUNCHER_LOG_DIR/launcher.stdout.log"
REPORT_DIR="$RESULTS_ROOT/reports/$RUN_LABEL"

if [[ ! -d "$EXP_WORKTREE" ]]; then
  echo "Missing experiment worktree: $EXP_WORKTREE" >&2
  exit 1
fi

if [[ -z "$TMUX_BIN" || -z "$UV_BIN" || -z "$CAFFEINATE_BIN" ]]; then
  echo "Missing required binary (tmux, uv, or caffeinate) in PATH." >&2
  exit 1
fi

if [[ -d "$LAUNCHER_LOG_DIR" ]] && find "$LAUNCHER_LOG_DIR" -mindepth 1 -print -quit | grep -q .; then
  echo "Launcher log dir already exists and is non-empty: $LAUNCHER_LOG_DIR" >&2
  echo "Choose a new run label or remove the existing log dir first." >&2
  exit 1
fi

mkdir -p "$LAUNCHER_LOG_DIR"

if "$TMUX_BIN" has-session -t "$SESSION_NAME" 2>/dev/null; then
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
  "$UV_BIN"
  run
  python
  -u
  scripts/launch_skillx_round0.py
  "$TARGET"
  --task-slice
  "$TASK_SLICE"
  --materialized-root
  "$RESULTS_ROOT"
  --output-suffix
  "$RUN_LABEL"
)
report_cmd=(
  "$UV_BIN"
  run
  python
  scripts/export_round0_run_report.py
  --materialized-root
  "$RESULTS_ROOT"
  --run-label
  "$RUN_LABEL"
  --report-dir
  "$REPORT_DIR"
)

printf -v launcher_cmd_quoted '%q ' "${launcher_cmd[@]}"
printf -v report_cmd_quoted '%q ' "${report_cmd[@]}"
printf -v run_command 'cd %q && scripts/rematerialize_metric_gated_scientific_pipeline_root.sh && %q -dimsu %s2>&1 | tee %q && %s' \
  "$EXP_WORKTREE" \
  "$CAFFEINATE_BIN" \
  "$launcher_cmd_quoted" \
  "$STDOUT_LOG_PATH" \
  "$report_cmd_quoted"
printf -v dashboard_command 'cd %q && scripts/run_metric_gated_scientific_pipeline_monitor.sh %q %q' \
  "$EXP_WORKTREE" \
  "$RUN_LABEL" \
  "$MONITOR_PORT"

"$TMUX_BIN" new-session -d -s "$SESSION_NAME" -n run
"$TMUX_BIN" send-keys -t "$SESSION_NAME":run "$run_command" C-m
"$TMUX_BIN" new-window -t "$SESSION_NAME" -n dashboard
"$TMUX_BIN" send-keys -t "$SESSION_NAME":dashboard "$dashboard_command" C-m
"$TMUX_BIN" select-window -t "$SESSION_NAME":run

echo "Started metric-gated scientific pipeline launcher in tmux"
echo "  session: $SESSION_NAME"
echo "  windows: run, dashboard"
echo "  target: $TARGET"
echo "  run-label: $RUN_LABEL"
echo "  worktree: $EXP_WORKTREE"
echo "  materialized-root: $RESULTS_ROOT"
echo "  stdout-log: $STDOUT_LOG_PATH"
echo "  dashboard: http://127.0.0.1:$MONITOR_PORT/"
echo
echo "Attach:"
echo "  tmux attach -t $SESSION_NAME"
