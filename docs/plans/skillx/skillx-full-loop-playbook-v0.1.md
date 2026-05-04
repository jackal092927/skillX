# SkillX Full Inner-Outer Loop Playbook v0.1

- **Purpose:** run one complete SkillX optimization cycle and repeat it across outer-loop rounds.
- **Audience:** Coding Agent, experiment operator, collaborator.
- **Status:** executable playbook with human checkpoints.

## 1. Loop Contract

The full loop is:

```text
materialized schema-task pairs
  -> inner loop rerun in tmux
  -> run report export
  -> post-inner-loop audit and targeted rerun plan
  -> global pair status rebuild
  -> outer loop assignment and schema rewrite
  -> next materialized schema-task pairs
  -> repeat
```

The inner loop evaluates task-schema pairs. The outer loop consumes the completed pair results, rewrites schema candidates, verifies the rewrite, and materializes the next batch for another inner loop.

## 2. Standard Scripts

- `scripts/run_skillx_inner_loop_tmux.sh`
  - starts one inner-loop launcher in tmux
  - creates two windows: `inner-loop` and `dashboard`
  - serves the monitor dashboard with `scripts/serve_round0_monitor.py`
- `scripts/run_skillx_outer_loop_step.sh`
  - exports the completed inner-loop run report
  - runs `scripts/audit_skillx_inner_loop_results.py`
  - blocks by default if any pair requires rerun before outer-loop consumption
  - rebuilds `global_pair_status.json`
  - runs `scripts/run_outer_loop_optimization.py`
  - writes `rewrite_verification.json`
  - materializes the next round's candidate pairs

Older round-0 specific helpers still work, but new full-loop runs should prefer the two generic scripts above.

## 3. Default Configuration

Dataset:

- Default benchmark family: SkillsBench.
- Default task inventory: `docs/plans/skillx/skillsbench-task-cluster-inputs-v0.1.jsonl`.
- Default official scores: `experiments/skillx-skillsbench-001/results/official-task-results/official_task_results.jsonl`.
- Default schema bank: `docs/plans/skillx/skillx-prompt-bank-v0.1.json`.

Inner loop:

- Executor agent: `claude-code`.
- Executor model: `anthropic/claude-sonnet-4-5`.
- Executor auth: local Claude Code authentication, not an API key.
- C4AR Role A model: `codex-5.3`.
- C4AR Role B model: `gpt-5.4`.
- Round budget: `3` unless overridden.
- Launcher runs up to `3` pairs concurrently by default. Set `SKILLX_MAX_CONCURRENT_PAIRS=1` for serial execution. One failed pair should be recorded and should not stop later pairs.

Outer loop:

- Rewriter mode: `llm`.
- Rewriter model: `anthropic/claude-sonnet-4-5`.
- Rewriter auth: local CLI authentication, not an API key.
- Default rewrite policy: rewrite all schemas unless constrained.
- Default `min_support_size`: `0`.
- Default `max_update_schemas`: `0`.
- Default `max_eval_tasks_per_schema`: `6`.
- Default next-pair plan mode: `full_matrix`, meaning every selected task is materialized against every rewritten candidate schema for the next inner loop.
- Optional next-pair plan mode: `challenger_eval`, which materializes only the smaller schema-specific challenger subset.
- Verification: `rewrite_verification.json` must pass before next-round materialization is trusted.

Batch size:

- Smoke test: one explicit `--pair-id`.
- Small batch: first `3`, `10`, or `20` tasks.
- Full benchmark: run all pairs in the materialized root by omitting launcher selection args.
- For a new outer-loop algorithm, prefer `10 × 7` or `20 × 7` before full SkillsBench.

## 4. Human-Operated Cycle

Use this mode when you want a human to inspect each stage before the next long run starts.

### Step A: Prepare The Worktree

Use a dedicated experiment branch/worktree for any long run.

```bash
git status --short
```

If the run is independent, create or switch to an experiment worktree using the parallel development playbook:

```text
docs/plans/skillx/skillx-parallel-development-playbook-v0.1.md
```

### Step B: Start Inner Loop And Dashboard

Run the first `10 × 7` batch from the default round-0 materialized root:

```bash
scripts/run_skillx_inner_loop_tmux.sh run-round0-10x7 skillx-round0-10x7 8767 -- 10
```

Run all pairs from an outer-loop generated materialized root:

```bash
SKILLX_MATERIALIZED_ROOT=experiments/skillx-skillsbench-001/results/outer-loop-round0/outer-loop-round1-candidate-rerun \
  scripts/run_skillx_inner_loop_tmux.sh run-round1-candidates skillx-round1-candidates 8768
```

Run one explicit smoke pair:

```bash
SKILLX_MATERIALIZED_ROOT=experiments/skillx-skillsbench-001/results/outer-loop-round0/outer-loop-round1-candidate-rerun \
  scripts/run_skillx_inner_loop_tmux.sh smoke-r1-pair skillx-smoke-r1 8769 -- \
  --pair-id citation-check__methodology-guardrail
```

Inner-loop pair concurrency defaults to `3`. Override it with `SKILLX_MAX_CONCURRENT_PAIRS`; use `1` to force the old serial behavior:

```bash
SKILLX_MAX_CONCURRENT_PAIRS=1 \
  scripts/run_skillx_inner_loop_tmux.sh run-serial skillx-serial 8767 -- 10
```

Attach to the tmux session only when needed:

```bash
tmux attach -t skillx-round0-10x7
```

The dashboard is available at:

```text
http://127.0.0.1:<port>/
```

### Step C: Watch Completion

Use the dashboard first. Only inspect raw logs when needed.

Important files:

```text
<materialized-root>/launcher_logs/<run-label>/launcher.stdout.log
<materialized-root>/launcher_logs/<run-label>/events.ndjson
<materialized-root>/launcher_logs/<run-label>/summary.json
```

Do not start the outer loop until `summary.json` exists and the run is no longer active.

### Step D: Run Outer Loop

After the inner loop finishes:

```bash
SKILLX_PREVIOUS_MATERIALIZED_ROOT=experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2 \
  scripts/run_skillx_outer_loop_step.sh \
  run-round0-10x7 \
  outer-loop-round1-10x7 \
  experiments/skillx-skillsbench-001/results/outer-loop-round0/outer-loop-round1-candidate-rerun-10x7
```

Before the outer-loop optimizer runs, the wrapper now audits the completed inner-loop run. It writes:

```text
<materialized-root>/reports/<run-label>/inner_loop_audit/inner_loop_audit.json
<materialized-root>/reports/<run-label>/inner_loop_audit/inner_loop_audit.md
<materialized-root>/reports/<run-label>/inner_loop_audit/*_pair_manifest.json
<materialized-root>/reports/<run-label>/inner_loop_audit/run_*_rerun.sh
```

The audit classifies failed pairs, runtime failures, rate-limit fallback, basic-model fallback, timeout signals, stale artifacts, incomplete launcher output, and intentional `skipped_baseline_perfect` rows. If `rerun_required > 0`, the wrapper stops before rebuilding global status so invalid evidence is not fed into the outer loop.

To inspect without blocking:

```bash
SKILLX_INNER_AUDIT_FAIL_ON_RERUN_REQUIRED=0 \
SKILLX_PREVIOUS_MATERIALIZED_ROOT=experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2 \
  scripts/run_skillx_outer_loop_step.sh run-round0-10x7 outer-loop-round1-10x7
```

To rerun required pairs:

```bash
bash <materialized-root>/reports/<run-label>/inner_loop_audit/run_required_rerun.sh
```

This writes:

```text
<round-root>/reports/<outer-label>/control-plane/
<round-root>/reports/<outer-label>/schema-updates/
<next-materialized-root>/
```

Required verification:

```bash
jq '{status, expected_rewrite_schema_count, completed_rewrite_schema_count, failures}' \
  <round-root>/reports/<outer-label>/schema-updates/rewrite_verification.json
```

The `status` must be `passed`.

### Step E: Repeat

Use the `next-materialized-root` from Step D as the next `SKILLX_MATERIALIZED_ROOT`.

```bash
SKILLX_MATERIALIZED_ROOT=experiments/skillx-skillsbench-001/results/outer-loop-round0/outer-loop-round1-candidate-rerun-10x7 \
  scripts/run_skillx_inner_loop_tmux.sh run-round1-10x7 skillx-round1-10x7 8770
```

Then run another outer-loop step with updated labels:

```bash
SKILLX_PREVIOUS_MATERIALIZED_ROOT=experiments/skillx-skillsbench-001/results/outer-loop-round0/outer-loop-round1-candidate-rerun-10x7 \
SKILLX_ROUND_ID=outer-loop-round1 \
SKILLX_NEXT_ROUND_ID=outer-loop-round2 \
  scripts/run_skillx_outer_loop_step.sh \
  run-round1-10x7 \
  outer-loop-round2-10x7 \
  experiments/skillx-skillsbench-001/results/outer-loop-round0/outer-loop-round2-candidate-rerun-10x7
```

## 5. Useful Configuration Knobs

Inner loop knobs:

```bash
export SKILLX_ROUND_BUDGET=3
export SKILLX_AGENT=claude-code
export SKILLX_MODEL=anthropic/claude-sonnet-4-5
export SKILLX_OVERRIDE_MEMORY_MB=8192
export SKILLX_OVERRIDE_STORAGE_MB=20480
```

Outer loop knobs:

```bash
export SKILLX_REWRITE_MODE=llm
export SKILLX_LLM_MODEL=anthropic/claude-sonnet-4-5
export SKILLX_MIN_SUPPORT_SIZE=0
export SKILLX_MAX_UPDATE_SCHEMAS=0
export SKILLX_MAX_EVAL_TASKS_PER_SCHEMA=6
export SKILLX_NEXT_PAIR_PLAN_MODE=full_matrix
export SKILLX_INNER_AUDIT=1
export SKILLX_INNER_AUDIT_FAIL_ON_RERUN_REQUIRED=1
```

Task scope knobs:

```bash
# First N tasks from the task slice.
scripts/run_skillx_inner_loop_tmux.sh run-10x7 skillx-10x7 8767 -- 10

# One task.
scripts/run_skillx_inner_loop_tmux.sh run-one-task skillx-one-task 8768 -- --task citation-check

# One pair.
scripts/run_skillx_inner_loop_tmux.sh run-one-pair skillx-one-pair 8769 -- --pair-id citation-check__methodology-guardrail

# Frozen custom pair manifest.
scripts/run_skillx_inner_loop_tmux.sh run-custom skillx-custom 8770 -- --pair-manifest path/to/selected_pairs.json
```

## 6. Agent Procedure

When a Coding Agent is asked to run the full loop:

1. Check the current worktree and branch.
2. Confirm whether the user wants smoke, small batch, or full benchmark.
3. Confirm the materialized root and run label.
4. Start `scripts/run_skillx_inner_loop_tmux.sh`.
5. Report the tmux session name and dashboard URL.
6. Wait for human confirmation or monitor completion.
7. Run `scripts/run_skillx_outer_loop_step.sh`; inspect `inner_loop_audit.md` if it blocks.
8. If reruns are required, launch the generated rerun script and fold the clean rerun output into the effective run before continuing.
9. Inspect `rewrite_verification.json`.
10. Report the next materialized root and suggested next inner-loop command.
11. Keep code commits separate from large raw experiment outputs unless explicitly asked.

## 7. Optional Main-Agent Automation

A main agent can automate the cycle, but it should still keep hard checkpoints:

```text
for each outer-loop round:
  prepare branch/worktree
  start inner-loop tmux + dashboard
  monitor launcher summary until completed
  export run report
  run post-inner-loop audit
  if rerun_required > 0:
    launch or hand off generated targeted rerun plan before outer-loop consumption
  rebuild global status
  run outer-loop optimizer
  require rewrite_verification.status == passed
  smoke-test one generated pair if this is a new algorithm version
  hand off next materialized root
```

The main agent should not silently launch a full benchmark after a schema rewrite unless the user already approved that batch size.

## 8. Acceptance Criteria

One complete cycle is valid when:

- inner-loop `summary.json` exists
- every failed pair has structured failure artifacts
- `run_report.json` was exported
- `inner_loop_audit.json` exists
- `inner_loop_audit.json.counts.rerun_required = 0`, or required reruns were executed and folded into the effective results
- `global_pair_status.json` was rebuilt
- outer-loop `outer_loop_optimization_summary.json` exists
- `rewrite_verification.json` has `status = passed`
- the next materialized root has `manifest.json`, `pair_specs.jsonl`, and `next_round_pair_plan.json`

The candidate prompt bank is not accepted as incumbent until the next inner loop validates it.

## 9. Related Documents

- `docs/plans/skillx/skillx-round0-mxn-runbook-v0.1.md`
- `docs/plans/skillx/skillx-outer-loop-agent-playbook-v0.1.md`
- `docs/plans/skillx/skillx-assignment-matrix-protocol-v0.1.md`
- `docs/plans/skillx/skillx-outer-loop-update-protocol-v0.1.md`
- `docs/plans/skillx/skillx-parallel-development-playbook-v0.1.md`
- `docs/plans/skillx/full-loop-post-inner-audit-reference-v0.1.md`
- `skills/skillx-full-loop-audit/SKILL.md`
