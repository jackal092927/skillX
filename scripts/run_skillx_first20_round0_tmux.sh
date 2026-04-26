#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/run_skillx_first20_round0_tmux.sh [run-label] [session-name] [monitor-port]

Example:
  scripts/run_skillx_first20_round0_tmux.sh run-first20x7-round0-2026-04-24 skillx-round0-first20x7 8769

Environment overrides:
  SKILLX_EXP_WORKTREE           Experiment worktree. Default: current checkout.
  SKILLX_SKILLSBENCH_ROOT       SkillsBench source checkout. Auto-detected by searching parent dirs.
  SKILLX_FIRST20_TASK_SLICE     First-20 task slice JSON.
  SKILLX_FIRST20_MATERIALIZED_ROOT
                                Materialized root for the first-20 20x7 round0 run.
  SKILLX_RUN_LABEL              Default run label.
  SKILLX_TMUX_SESSION           Default tmux session name.
  SKILLX_MONITOR_PORT           Dashboard port. If omitted, run_skillx_inner_loop_tmux.sh auto-selects.
  SKILLX_MAX_CONCURRENT_PAIRS   Max concurrent task-schema pairs. Default: 1.
  SKILLX_ROUND_BUDGET           Inner-loop budget after R0. Default: 3, yielding R0-R3.
  SKILLX_AGENT                  Executor agent. Default: claude-code.
  SKILLX_MODEL                  Executor model. Default: anthropic/claude-sonnet-4-5.
  SKILLX_FALLBACK_CLAUDE_OAUTH_FILE  Optional fallback Claude OAuth token file.
  SKILLX_FALLBACK_CODEX_MODEL        Codex fallback model. Default: gpt-5.4.
  SKILLX_DISABLE_CODEX_FALLBACK      1 disables Codex fallback. Default: 0.
  SKILLX_DISABLE_RATE_LIMIT_FALLBACK 1 disables all rate-limit fallback. Default: 0.
  SKILLX_LLM_MODEL              Later outer-loop rewriter model. Default documented here only.
  SKILLX_PYTHON                 Python runtime used by uv. Default: 3.11.
  SKILLX_PREPARE_ONLY           1 materializes and validates without starting tmux.

Behavior:
  - materializes the task-list first 20 tasks against all 7 schemas if needed
  - starts a tmux session with inner-loop and dashboard windows
  - defaults to one pair job per tmux session; use task-batch tmux launchers for parallelism
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

WORKTREE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXP_WORKTREE="${SKILLX_EXP_WORKTREE:-$WORKTREE_ROOT}"

RUN_LABEL="${SKILLX_RUN_LABEL:-run-first20x7-round0-$(date +%Y-%m-%d-%H%M)}"
SESSION_NAME="${SKILLX_TMUX_SESSION:-skillx-round0-first20x7}"
MONITOR_PORT="${SKILLX_MONITOR_PORT:-}"
if [[ $# -gt 0 ]]; then
  RUN_LABEL="$1"
  shift
fi
if [[ $# -gt 0 ]]; then
  SESSION_NAME="$1"
  shift
fi
if [[ $# -gt 0 ]]; then
  MONITOR_PORT="$1"
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

auto_detect_skillsbench_root() {
  local dir="$EXP_WORKTREE"
  while [[ "$dir" != "/" ]]; do
    if [[ -d "$dir/skillsbench-src/tasks" ]]; then
      printf '%s\n' "$dir/skillsbench-src"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  return 1
}

DEFAULT_TASK_SLICE="experiments/skillx-skillsbench-001/results/official-task-results/sonnet45-task-list-first20-v0.1.json"
DEFAULT_MATERIALIZED_ROOT="experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1"
TASK_SLICE="$(resolve_path "${SKILLX_FIRST20_TASK_SLICE:-$DEFAULT_TASK_SLICE}")"
MATERIALIZED_ROOT="$(resolve_path "${SKILLX_FIRST20_MATERIALIZED_ROOT:-$DEFAULT_MATERIALIZED_ROOT}")"
PROMPT_BANK="$(resolve_path "${SKILLX_PROMPT_BANK:-docs/plans/skillx/skillx-prompt-bank-v0.1.json}")"
INVENTORY="$(resolve_path "${SKILLX_INVENTORY:-docs/plans/skillx/skillsbench-task-cluster-inputs-v0.1.jsonl}")"
OFFICIAL_RESULTS="$(resolve_path "${SKILLX_OFFICIAL_RESULTS:-experiments/skillx-skillsbench-001/results/official-task-results/official_task_results.jsonl}")"
RENDER_TEMPLATE="$(resolve_path "${SKILLX_RENDER_TEMPLATE:-docs/plans/skillx/skillx-render-template-frozen-v0.1.md}")"
PYTHON_RUNTIME="${SKILLX_PYTHON:-3.11}"
ROUND_BUDGET="${SKILLX_ROUND_BUDGET:-3}"
AGENT="${SKILLX_AGENT:-claude-code}"
MODEL="${SKILLX_MODEL:-anthropic/claude-sonnet-4-5}"
FALLBACK_CLAUDE_OAUTH_FILE="${SKILLX_FALLBACK_CLAUDE_OAUTH_FILE:-}"
FALLBACK_CODEX_MODEL="${SKILLX_FALLBACK_CODEX_MODEL:-gpt-5.4}"
DISABLE_CODEX_FALLBACK="${SKILLX_DISABLE_CODEX_FALLBACK:-0}"
DISABLE_RATE_LIMIT_FALLBACK="${SKILLX_DISABLE_RATE_LIMIT_FALLBACK:-0}"
MAX_CONCURRENT_PAIRS="${SKILLX_MAX_CONCURRENT_PAIRS:-1}"
OAUTH_FILE="${SKILLX_OAUTH_FILE:-$HOME/.claude/claude-code-oauth-token}"
PREPARE_ONLY="${SKILLX_PREPARE_ONLY:-0}"

if [[ -n "${SKILLX_SKILLSBENCH_ROOT:-}" ]]; then
  SKILLSBENCH_ROOT="$(resolve_path "$SKILLX_SKILLSBENCH_ROOT")"
else
  if ! SKILLSBENCH_ROOT="$(auto_detect_skillsbench_root)"; then
    echo "Could not auto-detect skillsbench-src. Set SKILLX_SKILLSBENCH_ROOT." >&2
    exit 1
  fi
fi

for required_path in "$TASK_SLICE" "$PROMPT_BANK" "$INVENTORY" "$OFFICIAL_RESULTS" "$RENDER_TEMPLATE" "$OAUTH_FILE"; do
  if [[ ! -e "$required_path" ]]; then
    echo "Missing required path: $required_path" >&2
    exit 1
  fi
done
if [[ ! -d "$SKILLSBENCH_ROOT/tasks" ]]; then
  echo "Invalid SkillsBench root: $SKILLSBENCH_ROOT" >&2
  exit 1
fi

cd "$EXP_WORKTREE"

if [[ ! -f "$MATERIALIZED_ROOT/manifest.json" || ! -f "$MATERIALIZED_ROOT/pair_specs.jsonl" ]]; then
  if [[ -d "$MATERIALIZED_ROOT" ]] && find "$MATERIALIZED_ROOT" -mindepth 1 -print -quit | grep -q .; then
    echo "Materialized root exists but is incomplete/non-empty: $MATERIALIZED_ROOT" >&2
    exit 1
  fi
  uv run --python "$PYTHON_RUNTIME" python scripts/materialize_skillx_round0_runner.py \
    --skillsbench-root "$SKILLSBENCH_ROOT" \
    --task-slice "$TASK_SLICE" \
    --prompt-bank "$PROMPT_BANK" \
    --inventory "$INVENTORY" \
    --official-results "$OFFICIAL_RESULTS" \
    --render-template "$RENDER_TEMPLATE" \
    --output-dir "$MATERIALIZED_ROOT" \
    --run-id "first20-round0-v0.1" \
    --oauth-file "$OAUTH_FILE" \
    --round-budget "$ROUND_BUDGET" \
    --agent "$AGENT" \
    --model "$MODEL"
fi

uv run --python "$PYTHON_RUNTIME" python - <<PY
import json
from pathlib import Path
root = Path("$MATERIALIZED_ROOT")
manifest = json.loads((root / "manifest.json").read_text())
pairs = [line for line in (root / "pair_specs.jsonl").read_text().splitlines() if line.strip()]
if manifest.get("task_count") != 20:
    raise SystemExit(f"expected 20 tasks, got {manifest.get('task_count')}")
if manifest.get("schema_count") != 7:
    raise SystemExit(f"expected 7 schemas, got {manifest.get('schema_count')}")
if len(pairs) != 140:
    raise SystemExit(f"expected 140 pairs, got {len(pairs)}")
print(f"Prepared first20 materialized root: {root}")
print("  tasks: 20")
print("  schemas: 7")
print("  pairs: 140")
PY

if [[ "$PREPARE_ONLY" == "1" || "$PREPARE_ONLY" == "true" ]]; then
  echo "Prepare-only mode; tmux launch skipped."
  exit 0
fi

inner_args=("$RUN_LABEL" "$SESSION_NAME")
if [[ -n "$MONITOR_PORT" ]]; then
  inner_args+=("$MONITOR_PORT")
fi

SKILLX_EXP_WORKTREE="$EXP_WORKTREE" \
SKILLX_MATERIALIZED_ROOT="$MATERIALIZED_ROOT" \
SKILLX_TASK_SLICE="$TASK_SLICE" \
SKILLX_PYTHON="$PYTHON_RUNTIME" \
SKILLX_ROUND_BUDGET="$ROUND_BUDGET" \
SKILLX_AGENT="$AGENT" \
SKILLX_MODEL="$MODEL" \
SKILLX_FALLBACK_CLAUDE_OAUTH_FILE="$FALLBACK_CLAUDE_OAUTH_FILE" \
SKILLX_FALLBACK_CODEX_MODEL="$FALLBACK_CODEX_MODEL" \
SKILLX_DISABLE_CODEX_FALLBACK="$DISABLE_CODEX_FALLBACK" \
SKILLX_DISABLE_RATE_LIMIT_FALLBACK="$DISABLE_RATE_LIMIT_FALLBACK" \
SKILLX_MAX_CONCURRENT_PAIRS="$MAX_CONCURRENT_PAIRS" \
scripts/run_skillx_inner_loop_tmux.sh "${inner_args[@]}"
