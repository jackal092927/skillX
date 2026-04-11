#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run_round0_next20_monitor.sh [run-label] [port]

Defaults:
  run-label: run-next20x7-2026-04-11
  port: 8769
  experiment worktree: current checkout

Environment overrides:
  SKILLX_EXP_WORKTREE   Absolute path to the experiment worktree
  SKILLX_RUN_LABEL      Default run label when arg 1 is omitted
  SKILLX_MONITOR_HOST   Bind host, default 127.0.0.1
  SKILLX_MONITOR_PORT   Default port when arg 2 is omitted
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXP_WORKTREE="${SKILLX_EXP_WORKTREE:-$WORKTREE_ROOT}"
RUN_LABEL="${1:-${SKILLX_RUN_LABEL:-run-next20x7-2026-04-11}}"
HOST="${SKILLX_MONITOR_HOST:-127.0.0.1}"
PORT="${2:-${SKILLX_MONITOR_PORT:-8769}}"

RESULTS_ROOT="$EXP_WORKTREE/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.3"
LAUNCHER_LOG_DIR="$RESULTS_ROOT/launcher_logs/$RUN_LABEL"

if [[ ! -d "$EXP_WORKTREE" ]]; then
  echo "Missing experiment worktree: $EXP_WORKTREE" >&2
  exit 1
fi

if [[ ! -d "$LAUNCHER_LOG_DIR" ]]; then
  echo "Missing launcher log dir: $LAUNCHER_LOG_DIR" >&2
  if [[ -d "$RESULTS_ROOT/launcher_logs" ]]; then
    echo "Available run labels:" >&2
    find "$RESULTS_ROOT/launcher_logs" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort >&2
  fi
  exit 1
fi

cd "$WORKTREE_ROOT"
echo "Serving round0 next20 monitor"
echo "  launcher_log_dir: $LAUNCHER_LOG_DIR"
echo "  open: http://$HOST:$PORT/"

exec uv run python scripts/serve_round0_monitor.py \
  --launcher-log-dir "$LAUNCHER_LOG_DIR" \
  --host "$HOST" \
  --port "$PORT"
