#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run_skillx_inner_loop_task_batches_tmux.sh [run-prefix] [session-prefix] [monitor-port-base]

Example:
  # Split the selected materialized root into batches of 5 tasks and start one
  # serial inner-loop tmux session per batch.
  SKILLX_MATERIALIZED_ROOT=experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1 \
  SKILLX_TASK_BATCH_SIZE=5 \
    scripts/run_skillx_inner_loop_task_batches_tmux.sh run-first20x7-batched skillx-first20x7 8767

Environment overrides:
  SKILLX_EXP_WORKTREE       Absolute path to the experiment worktree. Default: current checkout.
  SKILLX_MATERIALIZED_ROOT  Materialized root containing manifest.json and pair_specs.jsonl.
                            Default: experiments/.../outer-loop-round0/sonnet45-slice20-v0.2
  SKILLX_TASK_INDEX_START   First 1-based task index to include. Default: 1.
  SKILLX_TASK_INDEX_END     Last 1-based task index to include. Default: manifest task_count.
  SKILLX_TASK_BATCH_SIZE    Tasks per tmux batch. Default: 5. Ignored if SKILLX_TASK_BATCH_COUNT is set.
  SKILLX_TASK_BATCH_COUNT   Optional number of batches. Splits the selected index span evenly.
  SKILLX_MAX_CONCURRENT_PAIRS
                            Per-batch pair concurrency. Default: 1.
  SKILLX_PYTHON             Python runtime used by uv. Default: 3.11.
  SKILLX_BATCH_PREVIEW      1 prints the batch plan without starting tmux. Default: 0.

Behavior:
  - starts one tmux session per task batch
  - each tmux session has two windows: inner-loop, dashboard
  - each batch passes explicit --task-index values to scripts/launch_skillx_round0.py
  - batches are task-disjoint, while each batch is serial by default
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXP_WORKTREE="${SKILLX_EXP_WORKTREE:-$WORKTREE_ROOT}"

RUN_PREFIX="${SKILLX_RUN_PREFIX:-run-skillx-inner-batch-$(date +%Y-%m-%d-%H%M)}"
SESSION_PREFIX="${SKILLX_TMUX_SESSION_PREFIX:-skillx-inner-batch}"
MONITOR_PORT_BASE="${SKILLX_MONITOR_PORT_BASE:-8767}"

if [[ $# -gt 0 ]]; then
  RUN_PREFIX="$1"
  shift
fi
if [[ $# -gt 0 ]]; then
  SESSION_PREFIX="$1"
  shift
fi
if [[ $# -gt 0 ]]; then
  MONITOR_PORT_BASE="$1"
  shift
fi
if [[ $# -gt 0 ]]; then
  echo "Unexpected extra arguments: $*" >&2
  usage >&2
  exit 1
fi

resolve_path() {
  local raw_path="$1"
  if [[ "$raw_path" = /* ]]; then
    printf '%s\n' "$raw_path"
  else
    printf '%s\n' "$EXP_WORKTREE/$raw_path"
  fi
}

is_positive_int() {
  [[ "${1:-}" =~ ^[1-9][0-9]*$ ]]
}

is_port_busy() {
  local port="$1"
  lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
}

DEFAULT_MATERIALIZED_ROOT="experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2"
MATERIALIZED_ROOT="$(resolve_path "${SKILLX_MATERIALIZED_ROOT:-$DEFAULT_MATERIALIZED_ROOT}")"
PYTHON_RUNTIME="${SKILLX_PYTHON:-3.11}"
TASK_INDEX_START="${SKILLX_TASK_INDEX_START:-1}"
TASK_INDEX_END="${SKILLX_TASK_INDEX_END:-}"
TASK_BATCH_SIZE="${SKILLX_TASK_BATCH_SIZE:-5}"
TASK_BATCH_COUNT="${SKILLX_TASK_BATCH_COUNT:-}"
MAX_CONCURRENT_PAIRS="${SKILLX_MAX_CONCURRENT_PAIRS:-1}"
BATCH_PREVIEW="${SKILLX_BATCH_PREVIEW:-0}"
INNER_LOOP_TMUX_SCRIPT="$EXP_WORKTREE/scripts/run_skillx_inner_loop_tmux.sh"

if [[ ! -d "$EXP_WORKTREE" ]]; then
  echo "Missing experiment worktree: $EXP_WORKTREE" >&2
  exit 1
fi
if [[ ! -x "$INNER_LOOP_TMUX_SCRIPT" ]]; then
  echo "Missing executable inner-loop tmux script: $INNER_LOOP_TMUX_SCRIPT" >&2
  exit 1
fi
if [[ ! -f "$MATERIALIZED_ROOT/manifest.json" || ! -f "$MATERIALIZED_ROOT/pair_specs.jsonl" ]]; then
  echo "Missing materialized root manifest or pair specs: $MATERIALIZED_ROOT" >&2
  exit 1
fi
if ! is_positive_int "$MONITOR_PORT_BASE"; then
  echo "monitor-port-base must be a positive integer: $MONITOR_PORT_BASE" >&2
  exit 1
fi
if ! is_positive_int "$TASK_INDEX_START"; then
  echo "SKILLX_TASK_INDEX_START must be a positive integer: $TASK_INDEX_START" >&2
  exit 1
fi
if ! is_positive_int "$TASK_BATCH_SIZE"; then
  echo "SKILLX_TASK_BATCH_SIZE must be a positive integer: $TASK_BATCH_SIZE" >&2
  exit 1
fi
if [[ -n "$TASK_BATCH_COUNT" ]] && ! is_positive_int "$TASK_BATCH_COUNT"; then
  echo "SKILLX_TASK_BATCH_COUNT must be a positive integer: $TASK_BATCH_COUNT" >&2
  exit 1
fi
if ! is_positive_int "$MAX_CONCURRENT_PAIRS"; then
  echo "SKILLX_MAX_CONCURRENT_PAIRS must be a positive integer: $MAX_CONCURRENT_PAIRS" >&2
  exit 1
fi

TASK_COUNT="$(uv run --python "$PYTHON_RUNTIME" python - "$MATERIALIZED_ROOT/manifest.json" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text())
task_count = manifest.get("task_count")
if not isinstance(task_count, int) or task_count <= 0:
    raise SystemExit(f"manifest has invalid task_count: {task_count!r}")
print(task_count)
PY
)"

if [[ -z "$TASK_INDEX_END" ]]; then
  TASK_INDEX_END="$TASK_COUNT"
elif ! is_positive_int "$TASK_INDEX_END"; then
  echo "SKILLX_TASK_INDEX_END must be a positive integer: $TASK_INDEX_END" >&2
  exit 1
fi
if (( TASK_INDEX_START > TASK_INDEX_END )); then
  echo "SKILLX_TASK_INDEX_START must be <= SKILLX_TASK_INDEX_END" >&2
  exit 1
fi
if (( TASK_INDEX_END > TASK_COUNT )); then
  echo "SKILLX_TASK_INDEX_END=$TASK_INDEX_END exceeds manifest task_count=$TASK_COUNT" >&2
  exit 1
fi

batch_starts=()
batch_ends=()
total_selected=$((TASK_INDEX_END - TASK_INDEX_START + 1))
if [[ -n "$TASK_BATCH_COUNT" ]]; then
  if (( TASK_BATCH_COUNT > total_selected )); then
    echo "SKILLX_TASK_BATCH_COUNT=$TASK_BATCH_COUNT exceeds selected task count=$total_selected" >&2
    exit 1
  fi
  base_size=$((total_selected / TASK_BATCH_COUNT))
  remainder=$((total_selected % TASK_BATCH_COUNT))
  cursor="$TASK_INDEX_START"
  for ((batch = 1; batch <= TASK_BATCH_COUNT; batch++)); do
    size="$base_size"
    if (( batch <= remainder )); then
      size=$((size + 1))
    fi
    batch_start="$cursor"
    batch_end=$((cursor + size - 1))
    batch_starts+=("$batch_start")
    batch_ends+=("$batch_end")
    cursor=$((batch_end + 1))
  done
else
  cursor="$TASK_INDEX_START"
  while (( cursor <= TASK_INDEX_END )); do
    batch_start="$cursor"
    batch_end=$((cursor + TASK_BATCH_SIZE - 1))
    if (( batch_end > TASK_INDEX_END )); then
      batch_end="$TASK_INDEX_END"
    fi
    batch_starts+=("$batch_start")
    batch_ends+=("$batch_end")
    cursor=$((batch_end + 1))
  done
fi

if [[ "$BATCH_PREVIEW" != "1" && "$BATCH_PREVIEW" != "true" ]]; then
  if ! command -v tmux >/dev/null 2>&1; then
    echo "tmux is required but was not found" >&2
    exit 1
  fi
fi

echo "SkillX task-batch tmux plan"
echo "  worktree: $EXP_WORKTREE"
echo "  materialized-root: $MATERIALIZED_ROOT"
echo "  task-index-span: $TASK_INDEX_START-$TASK_INDEX_END"
echo "  batches: ${#batch_starts[@]}"
echo "  per-batch max-concurrent-pairs: $MAX_CONCURRENT_PAIRS"
echo "  monitor-port-base: $MONITOR_PORT_BASE"

for idx in "${!batch_starts[@]}"; do
  batch_number=$((idx + 1))
  batch_label="$(printf 'b%02d' "$batch_number")"
  run_label="${RUN_PREFIX}-${batch_label}"
  session_name="${SESSION_PREFIX}-${batch_label}"
  monitor_port=$((MONITOR_PORT_BASE + idx))
  log_dir="$MATERIALIZED_ROOT/launcher_logs/$run_label"
  start="${batch_starts[$idx]}"
  end="${batch_ends[$idx]}"

  echo "  $batch_label: tasks $start-$end -> session=$session_name port=$monitor_port run=$run_label"

  if [[ "$BATCH_PREVIEW" == "1" || "$BATCH_PREVIEW" == "true" ]]; then
    continue
  fi
  if tmux has-session -t "$session_name" 2>/dev/null; then
    echo "tmux session already exists: $session_name" >&2
    exit 1
  fi
  if is_port_busy "$monitor_port"; then
    echo "monitor port is already in use: $monitor_port" >&2
    exit 1
  fi
  if [[ -d "$log_dir" ]] && find "$log_dir" -mindepth 1 -print -quit | grep -q .; then
    echo "Launcher log dir already exists and is non-empty: $log_dir" >&2
    exit 1
  fi
done

if [[ "$BATCH_PREVIEW" == "1" || "$BATCH_PREVIEW" == "true" ]]; then
  echo "Preview mode; tmux launch skipped."
  exit 0
fi

for idx in "${!batch_starts[@]}"; do
  batch_number=$((idx + 1))
  batch_label="$(printf 'b%02d' "$batch_number")"
  run_label="${RUN_PREFIX}-${batch_label}"
  session_name="${SESSION_PREFIX}-${batch_label}"
  monitor_port=$((MONITOR_PORT_BASE + idx))
  start="${batch_starts[$idx]}"
  end="${batch_ends[$idx]}"

  selection_args=()
  for ((task_index = start; task_index <= end; task_index++)); do
    selection_args+=(--task-index "$task_index")
  done

  SKILLX_EXP_WORKTREE="$EXP_WORKTREE" \
  SKILLX_MATERIALIZED_ROOT="$MATERIALIZED_ROOT" \
  SKILLX_MAX_CONCURRENT_PAIRS="$MAX_CONCURRENT_PAIRS" \
    "$INNER_LOOP_TMUX_SCRIPT" "$run_label" "$session_name" "$monitor_port" -- "${selection_args[@]}"
done

echo
echo "Started ${#batch_starts[@]} SkillX task-batch tmux session(s)."
echo "Attach examples:"
for idx in "${!batch_starts[@]}"; do
  batch_number=$((idx + 1))
  batch_label="$(printf 'b%02d' "$batch_number")"
  session_name="${SESSION_PREFIX}-${batch_label}"
  echo "  tmux attach -t $session_name"
done
