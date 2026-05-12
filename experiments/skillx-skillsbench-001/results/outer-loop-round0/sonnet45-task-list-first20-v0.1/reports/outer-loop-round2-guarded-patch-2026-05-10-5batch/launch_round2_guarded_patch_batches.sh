#!/usr/bin/env bash
set -euo pipefail

RUN_PREFIX="${1:-run-round2-guarded-patch-2026-05-10}"
SESSION_PREFIX="${2:-skillx-round2-guarded-patch}"
PORT_BASE="${3:-8782}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../../.." && pwd)"
MATERIALIZED_ROOT="$REPO_ROOT/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10"
PLAN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

export SKILLX_MAX_CONCURRENT_PAIRS="${SKILLX_MAX_CONCURRENT_PAIRS:-1}"
export SKILLX_ROUND_BUDGET="${SKILLX_ROUND_BUDGET:-3}"
export SKILLX_MATERIALIZED_ROOT="$MATERIALIZED_ROOT"
export SKILLX_AGENT="${SKILLX_AGENT:-claude-code}"
export SKILLX_MODEL="${SKILLX_MODEL:-anthropic/claude-sonnet-4-5}"
export SKILLX_DOCKER_AUTO_RECOVER="${SKILLX_DOCKER_AUTO_RECOVER:-1}"
ROUND2_PRIMARY_CLAUDE_OAUTH_FILE="${SKILLX_ROUND2_PRIMARY_CLAUDE_OAUTH_FILE:-$HOME/.claude/claude-code-oauth-token}"
ROUND2_FALLBACK_CLAUDE_OAUTH_FILE="${SKILLX_ROUND2_FALLBACK_CLAUDE_OAUTH_FILE:-$HOME/.claude-skillx-fallback/claude-code-oauth-token}"

if [[ ! -f "$MATERIALIZED_ROOT/manifest.json" || ! -f "$MATERIALIZED_ROOT/pair_specs.jsonl" ]]; then
  echo "Missing local materialized root files under: $MATERIALIZED_ROOT" >&2
  echo "Regenerate the outer-loop materialization or restore the local git-ignored files before launching." >&2
  exit 1
fi
if [[ ! -f "$ROUND2_PRIMARY_CLAUDE_OAUTH_FILE" ]]; then
  echo "Missing primary Claude OAuth token: $ROUND2_PRIMARY_CLAUDE_OAUTH_FILE" >&2
  exit 1
fi
if [[ ! -f "$ROUND2_FALLBACK_CLAUDE_OAUTH_FILE" ]]; then
  echo "Missing fallback Claude OAuth token: $ROUND2_FALLBACK_CLAUDE_OAUTH_FILE" >&2
  exit 1
fi

for batch in 01 02 03 04 05; do
  port=$((PORT_BASE + 10#$batch - 1))
  run_label="$RUN_PREFIX-b$batch"
  session_name="$SESSION_PREFIX-b$batch"
  pair_manifest="$PLAN_DIR/batch-$batch"_pair_manifest.json
  echo "Starting batch-$batch on port $port: $run_label / $session_name"
  scripts/run_skillx_inner_loop_tmux.sh "$run_label" "$session_name" "$port" -- \
    --pair-manifest "$pair_manifest" \
    --skip-existing-succeeded \
    --oauth-file "$ROUND2_PRIMARY_CLAUDE_OAUTH_FILE" \
    --fallback-oauth-file "$ROUND2_FALLBACK_CLAUDE_OAUTH_FILE"
done
