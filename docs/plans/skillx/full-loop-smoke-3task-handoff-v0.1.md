# SkillX Full-Loop Smoke Test: 3 Tasks v0.1

This handoff sets up a short local smoke test for the complete SkillX loop:

1. Use existing round0 inner-loop results as feedback.
2. Run one outer-loop optimization to rewrite candidate meta schemas.
3. Run the next inner-loop candidate pairs.
4. Run one more outer-loop optimization from the new feedback.
5. Stop after producing the final round2 schema artifacts.

## Branch And Worktree

- Branch: `codex/2026-04-24-full-loop-smoke-3tasks`
- Worktree: `.worktrees/codex/2026-04-24-full-loop-smoke-3tasks`

This branch is based on local `main` and includes the outer-loop optimization tooling from `feat/2026-04-19-outer-loop-optimization`.

## Selected Tasks

The smoke task list is stored at:

- `experiments/skillx-skillsbench-001/results/official-task-results/sonnet45-full-loop-smoke-3task-v0.1.json`

Selected tasks:

- `citation-check`: clean 7/7 historical pair completion; fast/simple methodology-guardrail task.
- `pdf-excel-diff`: clean 7/7 historical pair completion; fast/simple analytic artifact comparison task.
- `court-form-filling`: clean 7/7 historical pair completion; non-saturated scores provide useful outer-loop signal.

`powerlifting-coef-calc` was not selected even though it was fast, because all observed schema pairs scored 100 and therefore provide little schema-learning signal.

## Run Sequence

Start from the smoke worktree:

```bash
cd .worktrees/codex/2026-04-24-full-loop-smoke-3tasks
```

Step 1: run outer-loop optimization from existing round0 evidence.

```bash
scripts/run_skillx_full_loop_smoke3_outer_step.sh round0
```

This writes:

- `experiments/skillx-skillsbench-001/results/full-loop-smoke-3task-v0.1/reports/round0-global-status/global_pair_status.json`
- `experiments/skillx-skillsbench-001/results/full-loop-smoke-3task-v0.1/reports/outer-loop-round1-smoke/schema-updates/`
- `experiments/skillx-skillsbench-001/results/full-loop-smoke-3task-v0.1/outer-loop-round1-smoke-candidates/`

Step 2: run the round1 inner loop in tmux.

```bash
scripts/run_skillx_full_loop_smoke3_inner_tmux.sh run-full-loop-smoke3-r1 skillx-full-loop-smoke3-r1 8769
```

The tmux session has two windows:

- `inner-loop`: launcher process
- `dashboard`: monitor dashboard

Step 3: after the round1 inner loop finishes, run the second outer-loop step.

```bash
scripts/run_skillx_full_loop_smoke3_outer_step.sh round1 run-full-loop-smoke3-r1
```

This writes final stop-point artifacts under:

- `experiments/skillx-skillsbench-001/results/full-loop-smoke-3task-v0.1/reports/outer-loop-round2-smoke/schema-updates/`
- `experiments/skillx-skillsbench-001/results/full-loop-smoke-3task-v0.1/outer-loop-round2-smoke-candidates/`

For this smoke test, do not run the round2 candidate inner loop unless explicitly extending the experiment.

## Key Defaults

- Executor agent: `claude-code`
- Executor model: `anthropic/claude-sonnet-4-5`
- Outer-loop rewrite mode: `llm`
- Outer-loop rewriter model: `anthropic/claude-sonnet-4-5`
- Inner-loop round budget: `3`
- Max eval tasks per schema in the next-round candidate plan: `3`

For a cheap syntax/plumbing dry run of the outer step only, set:

```bash
SKILLX_REWRITE_MODE=deterministic scripts/run_skillx_full_loop_smoke3_outer_step.sh round0
```

Use a fresh `SKILLX_SMOKE_ROOT` if re-running, because the scripts intentionally refuse to overwrite non-empty materialized roots.
