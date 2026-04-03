# C4AR New Session Entrypoint

**Audience:** a fresh coding session that should continue the project immediately  
**Priority:** continue the real multi-task `C4AR` batch after the completed `trend` run

## Read These First

Read in this order:

1. [`CHECKPOINT_2026-03-26_C4AR_PROGRESS.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/CHECKPOINT_2026-03-26_C4AR_PROGRESS.md)
2. [`CHECKPOINT_2026-03-26_TREND_C4AR_RUN_SUMMARY.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/task_runs/trend-c4ar-001/CHECKPOINT_2026-03-26_TREND_C4AR_RUN_SUMMARY.md)
3. [`C4AR_POST_TREND_BATCH_HANDOFF.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/agent_handoff/C4AR_POST_TREND_BATCH_HANDOFF.md)

Do not start by re-reading the whole repo.
These files contain the current state, the accepted `trend` result, and the next batch action.

## Current Project State

What is already true:

- historical `C0/C1/C2/C3/C4` reference line exists
- negative-transfer PoC direction is frozen
- `trend` has a verified historical `R0 = C2AR = 0.8444`
- the first real end-to-end `trend` `C4AR` loop has been completed
- accepted `trend-c4ar-001` best score is `0.95`
- `R1` and `R2` tied, and `R1` is the frozen preferred candidate
- `C4AR` 3-agent architecture is coded and now runtime-validated
- `Role A` and `Role B` are playbook-driven external agents
- `Role C` remains the real Harbor/Docker benchmark executor

What is not yet true:

- the other three frozen negative-transfer tasks have not yet been run through the same real `C4AR` loop

So the next session is not a design session.
It is a batch-continuation execution session.

## Immediate Next Step

Run exactly one new real experiment on one remaining task:

1. `taxonomy-tree-merge`
2. `exoplanet-detection-period`
3. `energy-ac-optimal-power-flow`

Start from:

- the class-aware `C2AR` starting point for that task
- the same `C4AR` orchestration pattern validated on `trend`

Use:

- [`C4AR_POST_TREND_BATCH_HANDOFF.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/agent_handoff/C4AR_POST_TREND_BATCH_HANDOFF.md)

Do not:

- rerun `trend` unless there is a specific reason
- redesign the architecture first
- broaden the benchmark set beyond the frozen four tasks

## What The Next Session Should Decide

Once the next real task run finishes, the next session should make exactly one of these decisions:

1. **Expand**
   - if the run is runtime-valid and gives a credible result

2. **Fix and rerun**
   - if the run is runtime-invalid
   - or runtime-valid but clearly broken in handoff quality

3. **Stop and reassess**
   - if the run is runtime-valid but suggests that the current `C4AR` recipe does not transfer well beyond `trend`

## Headline Metrics

Record everything in the matrix, but only emphasize:

1. `Delta(C4AR-best, C2AR)`
2. `Delta(C4AR-best, C1)`
3. whether the frozen `trend` result generalizes at all to the remaining negative-transfer tasks

## Expansion Order

Continue in this order:

1. `taxonomy-tree-merge`
2. `exoplanet-detection-period`
3. `energy-ac-optimal-power-flow`

## Bottom Line

The first real `trend C4AR` loop is no longer the open question.

The most valuable next fact is:

> does the repaired, runtime-validated `C4AR` loop help on the remaining three frozen tasks, and if so, where does it generalize and where does it fail?

That is the first thing the next session should answer.
