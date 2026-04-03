# Checkpoint — 2026-03-29 Parallel TF-IDF Full Loop

## Scope

This checkpoint records the fresh `C4AR` full-loop validation run on `parallel-tfidf-search`.

Repo root:

- `<INCUBATOR_REPO_ROOT>`

Run bundle:

- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/parallel-tfidf-full-loop-001`

Task run:

- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/parallel-tfidf-full-loop-001/task_runs/parallel-tfidf-search-c4ar-001`

## Why This Run Happened

The open concern after the first negative-transfer batch closeout was no longer "does `trend` prove one clean full-chain run exists?" because that had already been established.

The open concern was narrower:

- can the current repaired `C4AR` pipeline complete another real `R0 -> R3` loop on a different task
- can it do so on a task that was not part of the earlier four-task batch

`parallel-tfidf-search` was selected because:

- it had not yet been run through this `C4AR` line
- official SkillsBench reporting shows negative skill transfer for `Claude Code (Sonnet 4.5)` on this task
- the project already had materialized SkillX assets for direct injection

## Current State

- no live experiment processes remain for this run
- task run status: `completed`
- orchestrator status: clean end-of-budget stop at `R3`

Validation outcome:

- the full `C4AR` mechanical loop executed through `R0`, `R1`, `R2`, and `R3`
- no manual resume was needed
- no old run directory was overwritten

## Main Progress

- the repaired `run_skillx_refine_benchmark.py` path has now been validated on another fresh real task run beyond the earlier frozen batch
- a second end-to-end `C4AR` full-loop execution now exists in the project record
- the project no longer depends on `trend` alone as the only proof that the repaired loop can traverse the full round budget in a real SkillsBench task

## Final Round Readout

- `R0 = 0.0` with `AgentTimeoutError`
- `R1 = 0.0`
- `R2 = 1.0`
- `R3 = 0.0`

Best observed reward:

- `1.0` at `R2`

Important caveat:

- this should not be described as stable improvement
- `R2` and `R3` used the same submitted `solve.sh`, so the `1.0 -> 0.0` swing is evidence of unstable performance-gate behavior rather than a clean algorithmic gain followed by a clean algorithmic regression

## Interpretation

What this run proves:

- the current end-to-end `C4AR` pipeline does run to completion in a fresh non-batch task
- the repaired runtime path is operational for another real benchmark task besides the already-known `trend` line

What this run does not prove:

- that `parallel-tfidf-search` is a stable positive-transfer case
- that later-round refinement produced a robustly better artifact

More accurate readout:

- pipeline success: `yes`
- task-level scientific success: `unstable / not yet claimable`

## Recommended Project-Level Readout

Use this run to support the statement:

> the repaired `C4AR` full loop is now runtime-validated on more than one real SkillsBench task, including a fresh `parallel-tfidf-search` run that completed cleanly through `R3`

Do not use this run to support the statement:

> `parallel-tfidf-search` is now a stable positive-transfer success case

## Read Next

- [`CHECKPOINT_2026-03-29_PARALLEL_TFIDF_C4AR_RUN_SUMMARY.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/parallel-tfidf-full-loop-001/task_runs/parallel-tfidf-search-c4ar-001/CHECKPOINT_2026-03-29_PARALLEL_TFIDF_C4AR_RUN_SUMMARY.md)
- [`RUN_BRIEF.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/parallel-tfidf-full-loop-001/RUN_BRIEF.md)
- [`CHECKPOINT_2026-03-28_C4AR_BATCH_CLOSEOUT.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/CHECKPOINT_2026-03-28_C4AR_BATCH_CLOSEOUT.md)
