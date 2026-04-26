#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run_skillx_inner_loop_tmux.sh [run-label] [session-name] [monitor-port] [-- launcher-selection-args...]

Examples:
  # Run the first 10 tasks from the default materialized root.
  scripts/run_skillx_inner_loop_tmux.sh run-round0-10x7 skillx-round0-10x7 8767 -- 10

  # Run all pairs in an outer-loop generated materialized root.
  SKILLX_MATERIALIZED_ROOT=experiments/skillx-skillsbench-001/results/outer-loop-round0/outer-loop-round1-candidate-rerun \
    scripts/run_skillx_inner_loop_tmux.sh run-round1-candidates skillx-round1-candidates 8768

  # Run one explicit pair.
  scripts/run_skillx_inner_loop_tmux.sh smoke-pair skillx-smoke 8769 -- --pair-id citation-check__methodology-guardrail

Environment overrides:
  SKILLX_EXP_WORKTREE       Absolute path to the experiment worktree. Default: current checkout.
  SKILLX_MATERIALIZED_ROOT  Materialized root containing manifest.json and pair_specs.jsonl.
                            Default: experiments/.../outer-loop-round0/sonnet45-slice20-v0.2
  SKILLX_TASK_SLICE         Optional task slice passed to launch_skillx_round0.py.
  SKILLX_REMATERIALIZE_CMD  Optional command run before the launcher, for legacy round0 roots.
  SKILLX_RUN_LABEL          Default run label.
  SKILLX_TMUX_SESSION       Default tmux session name.
  SKILLX_MONITOR_HOST       Dashboard bind host. Default: 127.0.0.1
  SKILLX_MONITOR_PORT       Explicit dashboard port.
  SKILLX_MONITOR_PORT_BASE  Starting port for auto-selection if no port is provided. Default: 8767
  SKILLX_PYTHON             Python runtime used by uv. Default: 3.11
  SKILLX_MAX_CONCURRENT_PAIRS  Max task-schema pairs run at once. Default: 1
  SKILLX_ROUND_BUDGET       Inner-loop round budget. Default: 3
  SKILLX_AGENT              Executor agent. Default: claude-code
  SKILLX_MODEL              Executor model. Default: anthropic/claude-sonnet-4-5
  SKILLX_FALLBACK_CLAUDE_OAUTH_FILE  Optional fallback Claude OAuth token file.
  SKILLX_FALLBACK_CODEX_MODEL        Codex fallback model. Default: gpt-5.4
  SKILLX_DISABLE_CODEX_FALLBACK      1 disables Codex fallback. Default: 0
  SKILLX_DISABLE_RATE_LIMIT_FALLBACK 1 disables all rate-limit fallback. Default: 0
  SKILLX_OVERRIDE_MEMORY_MB   Synthetic task memory override. Default: 8192
  SKILLX_OVERRIDE_STORAGE_MB  Synthetic task storage override. Default: 20480
  SKILLX_DOCKER_AUTO_RECOVER  1 enables --docker-auto-recover. Default: 1
  SKILLX_LAUNCHER_DRY_RUN     1 passes --dry-run to launch_skillx_round0.py. Default: 0

Behavior:
  - creates a tmux session with two windows: inner-loop, dashboard
  - runs scripts/launch_skillx_round0.py inside the inner-loop window
  - wraps the launcher with caffeinate
  - tees stdout into launcher_logs/<run-label>/launcher.stdout.log
  - serves scripts/serve_round0_monitor.py in the dashboard window
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXP_WORKTREE="${SKILLX_EXP_WORKTREE:-$WORKTREE_ROOT}"

RUN_LABEL="${SKILLX_RUN_LABEL:-run-skillx-inner-$(date +%Y-%m-%d-%H%M)}"
SESSION_NAME="${SKILLX_TMUX_SESSION:-skillx-inner-loop}"
REQUESTED_MONITOR_PORT="${SKILLX_MONITOR_PORT:-}"

if [[ $# -gt 0 && "${1:-}" != "--" ]]; then
  RUN_LABEL="$1"
  shift
fi
if [[ $# -gt 0 && "${1:-}" != "--" ]]; then
  SESSION_NAME="$1"
  shift
fi
if [[ $# -gt 0 && "${1:-}" != "--" ]]; then
  REQUESTED_MONITOR_PORT="$1"
  shift
fi
if [[ $# -gt 0 && "${1:-}" == "--" ]]; then
  shift
fi
LAUNCHER_SELECTION_ARGS=()
if [[ $# -gt 0 ]]; then
  LAUNCHER_SELECTION_ARGS=("$@")
fi

resolve_path() {
  local raw_path="$1"
  if [[ "$raw_path" = /* ]]; then
    printf '%s\n' "$raw_path"
  else
    printf '%s\n' "$EXP_WORKTREE/$raw_path"
  fi
}

DEFAULT_MATERIALIZED_ROOT="experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2"
MATERIALIZED_ROOT="$(resolve_path "${SKILLX_MATERIALIZED_ROOT:-$DEFAULT_MATERIALIZED_ROOT}")"
TASK_SLICE="${SKILLX_TASK_SLICE:-}"
if [[ -n "$TASK_SLICE" ]]; then
  TASK_SLICE="$(resolve_path "$TASK_SLICE")"
fi
REMATERIALIZE_CMD="${SKILLX_REMATERIALIZE_CMD:-}"
HOST="${SKILLX_MONITOR_HOST:-127.0.0.1}"
MONITOR_PORT_BASE="${SKILLX_MONITOR_PORT_BASE:-8767}"
PYTHON_RUNTIME="${SKILLX_PYTHON:-3.11}"
MAX_CONCURRENT_PAIRS="${SKILLX_MAX_CONCURRENT_PAIRS:-1}"
ROUND_BUDGET="${SKILLX_ROUND_BUDGET:-3}"
AGENT="${SKILLX_AGENT:-claude-code}"
MODEL="${SKILLX_MODEL:-anthropic/claude-sonnet-4-5}"
FALLBACK_CLAUDE_OAUTH_FILE="${SKILLX_FALLBACK_CLAUDE_OAUTH_FILE:-}"
FALLBACK_CODEX_MODEL="${SKILLX_FALLBACK_CODEX_MODEL:-gpt-5.4}"
DISABLE_CODEX_FALLBACK="${SKILLX_DISABLE_CODEX_FALLBACK:-0}"
DISABLE_RATE_LIMIT_FALLBACK="${SKILLX_DISABLE_RATE_LIMIT_FALLBACK:-0}"
OVERRIDE_MEMORY_MB="${SKILLX_OVERRIDE_MEMORY_MB:-8192}"
OVERRIDE_STORAGE_MB="${SKILLX_OVERRIDE_STORAGE_MB:-20480}"
DOCKER_AUTO_RECOVER="${SKILLX_DOCKER_AUTO_RECOVER:-1}"
LAUNCHER_DRY_RUN="${SKILLX_LAUNCHER_DRY_RUN:-0}"

LAUNCHER_LOG_DIR="$MATERIALIZED_ROOT/launcher_logs/$RUN_LABEL"
STDOUT_LOG_PATH="$LAUNCHER_LOG_DIR/launcher.stdout.log"
INNER_LOOP_SCRIPT="$LAUNCHER_LOG_DIR/run_inner_loop.sh"
DASHBOARD_SCRIPT="$LAUNCHER_LOG_DIR/run_dashboard.sh"

if [[ ! -d "$EXP_WORKTREE" ]]; then
  echo "Missing experiment worktree: $EXP_WORKTREE" >&2
  exit 1
fi
if [[ ! -f "$MATERIALIZED_ROOT/manifest.json" || ! -f "$MATERIALIZED_ROOT/pair_specs.jsonl" ]]; then
  echo "Missing materialized root manifest or pair specs: $MATERIALIZED_ROOT" >&2
  exit 1
fi
if [[ -d "$LAUNCHER_LOG_DIR" ]] && find "$LAUNCHER_LOG_DIR" -mindepth 1 -print -quit | grep -q .; then
  echo "Launcher log dir already exists and is non-empty: $LAUNCHER_LOG_DIR" >&2
  echo "Choose a new run label or remove the existing log dir first." >&2
  exit 1
fi
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "tmux session already exists: $SESSION_NAME" >&2
  echo "Attach with: tmux attach -t $SESSION_NAME" >&2
  exit 1
fi

is_port_busy() {
  local port="$1"
  lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
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

assert_python_entrypoint_not_recursive_wrapper() {
  local candidate="$EXP_WORKTREE/.venv/bin/python"
  if [[ ! -e "$candidate" ]]; then
    return 0
  fi
  if head -c 512 "$candidate" 2>/dev/null | grep -q '\.venv/bin/python'; then
    cat >&2 <<EOF
Detected a recursive Python wrapper at: $candidate

This can make uv interpreter probing hang before a pair creates RUN_STATUS.md.
Repair the uv-managed runtime first:
  uv --no-config --directory /tmp python install $PYTHON_RUNTIME --reinstall --force

Then recreate the project virtualenv if the entrypoint is still a wrapper.
EOF
    exit 1
  fi
}

MONITOR_PORT="$(resolve_monitor_port "$REQUESTED_MONITOR_PORT" "$MONITOR_PORT_BASE")"
assert_python_entrypoint_not_recursive_wrapper
mkdir -p "$LAUNCHER_LOG_DIR"

launcher_cmd=(
  uv
  run
  --python
  "$PYTHON_RUNTIME"
  python
  -u
  scripts/launch_skillx_round0.py
)
if [[ ${#LAUNCHER_SELECTION_ARGS[@]} -gt 0 ]]; then
  launcher_cmd+=("${LAUNCHER_SELECTION_ARGS[@]}")
fi
launcher_cmd+=(
  --materialized-root
  "$MATERIALIZED_ROOT"
  --output-suffix
  "$RUN_LABEL"
  --round-budget
  "$ROUND_BUDGET"
  --max-concurrent-pairs
  "$MAX_CONCURRENT_PAIRS"
  --python-runtime
  "$PYTHON_RUNTIME"
  --agent
  "$AGENT"
  --model
  "$MODEL"
  --fallback-codex-model
  "$FALLBACK_CODEX_MODEL"
  --override-memory-mb
  "$OVERRIDE_MEMORY_MB"
  --override-storage-mb
  "$OVERRIDE_STORAGE_MB"
)
if [[ -n "$TASK_SLICE" ]]; then
  launcher_cmd+=(--task-slice "$TASK_SLICE")
fi
if [[ -n "$FALLBACK_CLAUDE_OAUTH_FILE" ]]; then
  launcher_cmd+=(--fallback-oauth-file "$FALLBACK_CLAUDE_OAUTH_FILE")
fi
if [[ "$DISABLE_CODEX_FALLBACK" == "1" || "$DISABLE_CODEX_FALLBACK" == "true" ]]; then
  launcher_cmd+=(--no-codex-fallback)
fi
if [[ "$DISABLE_RATE_LIMIT_FALLBACK" == "1" || "$DISABLE_RATE_LIMIT_FALLBACK" == "true" ]]; then
  launcher_cmd+=(--disable-rate-limit-fallback)
fi
if [[ "$DOCKER_AUTO_RECOVER" == "1" || "$DOCKER_AUTO_RECOVER" == "true" ]]; then
  launcher_cmd+=(--docker-auto-recover)
else
  launcher_cmd+=(--no-docker-auto-recover)
fi
if [[ "$LAUNCHER_DRY_RUN" == "1" || "$LAUNCHER_DRY_RUN" == "true" ]]; then
  launcher_cmd+=(--dry-run)
fi

{
  printf '#!/usr/bin/env bash\n'
  printf 'set -euo pipefail\n'
  printf 'cd %q\n' "$EXP_WORKTREE"
  if [[ -n "$REMATERIALIZE_CMD" ]]; then
    printf '%s\n' "$REMATERIALIZE_CMD"
  fi
  printf 'caffeinate -dimsu '
  printf '%q ' "${launcher_cmd[@]}"
  printf '2>&1 | tee %q\n' "$STDOUT_LOG_PATH"
} > "$INNER_LOOP_SCRIPT"
chmod +x "$INNER_LOOP_SCRIPT"

{
  printf '#!/usr/bin/env bash\n'
  printf 'set -euo pipefail\n'
  printf 'cd %q\n' "$EXP_WORKTREE"
  printf 'uv run --python %q python scripts/serve_round0_monitor.py --launcher-log-dir %q --host %q --port %q\n' \
    "$PYTHON_RUNTIME" \
    "$LAUNCHER_LOG_DIR" \
    "$HOST" \
    "$MONITOR_PORT"
} > "$DASHBOARD_SCRIPT"
chmod +x "$DASHBOARD_SCRIPT"

printf -v run_command 'bash %q' "$INNER_LOOP_SCRIPT"
printf -v dashboard_command 'bash %q' "$DASHBOARD_SCRIPT"

tmux new-session -d -s "$SESSION_NAME" -n inner-loop
tmux send-keys -t "$SESSION_NAME":inner-loop "$run_command" C-m
tmux new-window -t "$SESSION_NAME" -n dashboard
tmux send-keys -t "$SESSION_NAME":dashboard "$dashboard_command" C-m
tmux select-window -t "$SESSION_NAME":inner-loop

echo "Started SkillX inner loop in tmux"
echo "  session: $SESSION_NAME"
echo "  windows: inner-loop, dashboard"
echo "  run-label: $RUN_LABEL"
echo "  materialized-root: $MATERIALIZED_ROOT"
echo "  python: $PYTHON_RUNTIME"
echo "  max-concurrent-pairs: $MAX_CONCURRENT_PAIRS"
echo "  round-budget: $ROUND_BUDGET"
echo "  agent/model: $AGENT / $MODEL"
echo "  fallback-claude-oauth-file: ${FALLBACK_CLAUDE_OAUTH_FILE:-auto-detect-if-present}"
echo "  fallback-codex-model: $FALLBACK_CODEX_MODEL"
echo "  stdout-log: $STDOUT_LOG_PATH"
echo "  inner-loop-script: $INNER_LOOP_SCRIPT"
echo "  dashboard-script: $DASHBOARD_SCRIPT"
echo "  dashboard: http://$HOST:$MONITOR_PORT/"
echo
echo "Attach:"
echo "  tmux attach -t $SESSION_NAME"
