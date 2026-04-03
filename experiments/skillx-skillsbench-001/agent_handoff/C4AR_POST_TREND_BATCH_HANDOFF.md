# C4AR Post-Trend Batch Handoff

**Audience:** a fresh coding session continuing the negative-transfer PoC batch after `trend-c4ar-001`  
**Status:** `trend` complete, three remaining tasks pending

## What Already Happened

The first real end-to-end `C4AR` run has already been completed on:

- `trend-anomaly-causal-inference`

Accepted result:

- task run: `trend-c4ar-001`
- best observed reward: `0.95`
- best rounds: `R1`, `R2`
- freeze decision: `R1`
- `R3` regressed to `0.8944`

Key references:

1. [`CHECKPOINT_2026-03-26_TREND_C4AR_RUN_SUMMARY.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/task_runs/trend-c4ar-001/CHECKPOINT_2026-03-26_TREND_C4AR_RUN_SUMMARY.md)
2. [`RESULT_SUMMARY.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/RESULT_SUMMARY.md)
3. [`RUN_STATUS.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/RUN_STATUS.md)

## What The Next Session Should Do

Do not rerun `trend` by default.

Run exactly one next task from the remaining frozen batch:

1. `taxonomy-tree-merge`
2. `exoplanet-detection-period`
3. `energy-ac-optimal-power-flow`

Recommended order:

1. `taxonomy-tree-merge`
2. `exoplanet-detection-period`
3. `energy-ac-optimal-power-flow`

## Execution Pattern

Use the same overall recipe that was validated on `trend`:

- starting point:
  - class-aware `C2AR` skillpack for the selected task
- orchestration:
  - `c4ar`
- roles:
  - `Role C` real Harbor/Docker benchmark execution
  - `Role A` session distill
  - `Role B` bounded refine brain

Do not treat the next session as an architecture-redesign session unless a real blocker appears.

## Preconditions Before Running The Next Task

Confirm:

- repo root path
- SkillsBench path
- Docker
- `uv`
- `codex exec`
- Claude oauth-only path still works

The `trend` run exposed real failures in:

- `Role B` artifact normalization
- recovery-point handling
- Claude oauth-only runtime auth

Those were repaired during the `trend` session, but preflight should still verify them before the next task run.

## What To Record

For the selected next task, leave behind:

1. a real `task_runs/<task>-c4ar-001` directory
2. updated source-run:
   - `RUN_STATUS.md`
   - `EXECUTION_LOG.md`
   - `RESULT_SUMMARY.md`
3. a task-run checkpoint note similar to the `trend` summary
4. an explicit freeze decision if multiple rounds tie

## Scientific Framing

At this point the open scientific question is no longer:

- does `C4AR` run at all?

It is now:

- does the repaired `C4AR` loop transfer beyond `trend` to the other three frozen negative-transfer tasks?

That question should be answered one task at a time, with runtime-valid evidence.
