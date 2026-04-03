# Checkpoint — 2026-03-28 C4AR Batch Closeout

## Scope

This checkpoint records the terminal state of the first class-aware negative-transfer `C4AR` batch.

Repo root:

- `<INCUBATOR_REPO_ROOT>`

Run bundle:

- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001`

## Current State

- no live experiment processes remain
- batch status: `closed out`
- code status:
  - resume and timeout hardening landed
  - regression suite passes

Validation:

- `./.venv-swebench/bin/python -m unittest tests.test_run_skillx_refine_benchmark`
- `36 tests` passed

## Final Task Readout

- `trend`
  - clean uninterrupted full-chain run
  - best observed reward `0.95`
  - freeze `R1`
- `taxonomy`
  - best retained reward `0.7712`
  - not a single uninterrupted chain
- `energy`
  - clean `R0 = 1.0`
  - intentionally early-stopped
- `exoplanet`
  - completed through `R3`
  - clean `0.0` through `R2`
  - `R3` timeout

## Important Caveat

Only `trend` should be described as a clean uninterrupted `R0 -> R3` run.

## If Work Continues Later

Use fresh non-overwriting run ids. Do not resume old task-run directories in place unless the new backup-before-resume logic is explicitly intended for that workflow.

Most likely next actions, if any:

- repeatability checks for `energy` `R0 = 1.0`
- a fresh isolated follow-up if `taxonomy` needs cleaner artifact continuity
- a fresh exoplanet rerun only if the goal is specifically to probe timeout sensitivity at the last round

## Read Next

- [`MILESTONE_REPORT_2026-03-28_C4AR_BATCH_CLOSEOUT.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/MILESTONE_REPORT_2026-03-28_C4AR_BATCH_CLOSEOUT.md)
- [`SUMMARY_2026-03-28_C4AR_BATCH_CLOSEOUT.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/SUMMARY_2026-03-28_C4AR_BATCH_CLOSEOUT.md)
- [`C4AR_BATCH_CLOSEOUT_HANDOFF_2026-03-28.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/agent_handoff/C4AR_BATCH_CLOSEOUT_HANDOFF_2026-03-28.md)
