# SkillX Rate-Limit Rerun 115-Pair Handoff

## Purpose

Run the 115 first20 task-schema pairs that were affected by hard quota / HTTP 429 signals.

The rerun is split into 5 task-disjoint batches. Each batch runs pairs serially, and the 5 batches run in parallel as separate tmux sessions.

## Source Branch

Use this branch as the base:

```bash
feat/2026-04-26-resilient-batch-launcher
```

If creating a fresh experiment worktree:

```bash
PROJECT_ROOT="${PROJECT_ROOT:-$PROJECTS/skillX}"
WT="$PROJECT_ROOT/.worktrees/exp/2026-04-26-first20-rate-limit-rerun-115"

git -C "$PROJECT_ROOT" worktree add \
  -b exp/2026-04-26-first20-rate-limit-rerun-115 \
  "$WT" \
  feat/2026-04-26-resilient-batch-launcher

cd "$WT"
```

If the experiment branch already exists, omit `-b ...` and use the existing branch name.

## Relevant Files

- Batch summary: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/rate-limit-rerun-batches-first20-round0-2026-04-26/summary.md`
- Batch plan JSON: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/rate-limit-rerun-batches-first20-round0-2026-04-26/batch_plan.json`
- Batch launch script: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/rate-limit-rerun-batches-first20-round0-2026-04-26/launch_rate_limit_rerun_batches.sh`
- Pair manifests: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/rate-limit-rerun-batches-first20-round0-2026-04-26/batch-*_pair_manifest.json`

Batch pair counts are `26, 25, 22, 21, 21`. Exact 23-per-batch is impossible under the no-task-overlap constraint because most affected tasks contribute 7 pairs.

## Preflight

Run these checks before launching:

```bash
git branch --show-current
git status --short --branch
tmux ls 2>/dev/null || true
docker info >/dev/null
docker system df
test -f "$HOME/.claude/claude-code-oauth-token"
test -f "$HOME/.claude-skillx-fallback/claude-code-oauth-token"
```

Expected branch is the experiment branch created from `feat/2026-04-26-resilient-batch-launcher`.

## Prepare Materialized Root

The tracked repo intentionally does not include `manifest.json`, `pair_specs.jsonl`, or raw `pairs/` outputs under the materialized root. Prepare them in the new worktree before launching:

```bash
SKILLX_PREPARE_ONLY=1 \
scripts/run_skillx_first20_round0_tmux.sh \
  prepare-first20-rate-limit-rerun \
  materialize-only
```

This should create:

```text
experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/manifest.json
experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/pair_specs.jsonl
experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/pairs/
```

Validate:

```bash
test -f experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/manifest.json
test -f experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/pair_specs.jsonl

python3 - <<'PY'
import json
from pathlib import Path

root = Path("experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1")
manifest = json.loads((root / "manifest.json").read_text())
pairs = [line for line in (root / "pair_specs.jsonl").read_text().splitlines() if line.strip()]
assert manifest["task_count"] == 20, manifest["task_count"]
assert manifest["schema_count"] == 7, manifest["schema_count"]
assert len(pairs) == 140, len(pairs)
print("materialized root OK")
PY
```

## Validate Batch Plan

```bash
python3 - <<'PY'
import json
from pathlib import Path

plan_dir = Path("experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/rate-limit-rerun-batches-first20-round0-2026-04-26")
plan = json.loads((plan_dir / "batch_plan.json").read_text())
all_pairs = []
all_tasks = []
for batch in plan["batches"]:
    manifest = json.loads((plan_dir / f"{batch['batch_id']}_pair_manifest.json").read_text())
    assert len(manifest["selected_pair_ids"]) == batch["pair_count"]
    all_pairs.extend(manifest["selected_pair_ids"])
    all_tasks.extend(manifest["task_names"])
assert len(all_pairs) == 115, len(all_pairs)
assert len(set(all_pairs)) == 115, "duplicate pair"
assert len(all_tasks) == len(set(all_tasks)) == 18, "task overlap across batches"
print("batch plan OK")
PY
```

## Launch

Choose a dashboard base port that is free. The script will use five consecutive ports.

```bash
BASE_PORT=8767

bash experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/rate-limit-rerun-batches-first20-round0-2026-04-26/launch_rate_limit_rerun_batches.sh \
  run-first20-rate-limit-rerun-2026-04-26 \
  skillx-first20-rate-limit-rerun \
  "$BASE_PORT"
```

Expected tmux sessions:

```text
skillx-first20-rate-limit-rerun-b01
skillx-first20-rate-limit-rerun-b02
skillx-first20-rate-limit-rerun-b03
skillx-first20-rate-limit-rerun-b04
skillx-first20-rate-limit-rerun-b05
```

Expected dashboards:

```text
http://127.0.0.1:8767/
http://127.0.0.1:8768/
http://127.0.0.1:8769/
http://127.0.0.1:8770/
http://127.0.0.1:8771/
```

Each batch runs with `SKILLX_MAX_CONCURRENT_PAIRS=1`. Parallelism comes from running 5 independent task-disjoint tmux sessions.

## Monitoring

```bash
tmux ls
tmux attach -t skillx-first20-rate-limit-rerun-b01
```

Launcher logs:

```bash
ROOT=experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1
find "$ROOT/launcher_logs" -maxdepth 2 -name launcher.stdout.log -print
tail -n 80 "$ROOT/launcher_logs/run-first20-rate-limit-rerun-2026-04-26-b01/launcher.stdout.log"
```

Summary files appear at:

```text
experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/launcher_logs/run-first20-rate-limit-rerun-2026-04-26-b*/summary.json
```

## Failure Handling

- If a dashboard port is busy, rerun with a different `BASE_PORT`.
- If a tmux session already exists, either attach to it or choose a new session prefix.
- If a pair hits Claude quota, the launcher should try the configured fallback chain: primary Claude Code, fallback Claude Code OAuth token, then Codex fallback.
- If all fallbacks are exhausted, the launcher should stop starting new pairs and write structured failure artifacts.
- Do not delete BuildKit cache before rerun. The previous cleanup removed dangling images only; BuildKit cache was kept intentionally for faster rebuilds.

## Completion Criteria

After all 5 tmux sessions finish:

```bash
ROOT=experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1
for f in "$ROOT"/launcher_logs/run-first20-rate-limit-rerun-2026-04-26-b*/summary.json; do
  echo "== $f"
  jq '{completed_pairs,succeeded_pairs,failed_pairs,aborted,abort_reason}' "$f"
done
```

Then export or checkpoint the rerun results before running the next outer-loop step.
