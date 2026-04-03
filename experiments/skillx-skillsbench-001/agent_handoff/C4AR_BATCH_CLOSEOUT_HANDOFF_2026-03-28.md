# C4AR Batch Closeout Handoff — 2026-03-28

## Read Order

1. [`CHECKPOINT_2026-03-28_C4AR_BATCH_CLOSEOUT.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/CHECKPOINT_2026-03-28_C4AR_BATCH_CLOSEOUT.md)
2. [`MILESTONE_REPORT_2026-03-28_C4AR_BATCH_CLOSEOUT.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/MILESTONE_REPORT_2026-03-28_C4AR_BATCH_CLOSEOUT.md)
3. [`RESULT_SUMMARY.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/RESULT_SUMMARY.md)
4. [`EXECUTION_LOG.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/EXECUTION_LOG.md)

## Batch Status

- run bundle: `class-aware-c2-negative-transfer-poc-001`
- branch: `main`
- live experiment processes: none
- batch state: closed out

## Final Per-Task State

- `trend`
  - authoritative task run: `trend-c4ar-001`
  - final interpretation:
    - clean uninterrupted `R0 -> R3`
    - best observed reward `0.95`
    - freeze `R1`
- `taxonomy`
  - authoritative evidence is split:
    - `taxonomy-tree-merge-c4ar-002-defaulttimeout`
    - `taxonomy-tree-merge-c4ar-004-r2resume-timeoutx2`
  - final interpretation:
    - best retained score `0.7712`
    - usable, but not a single uninterrupted chain
- `energy`
  - authoritative task run: `energy-ac-optimal-power-flow-c4ar-003-timeoutx2`
  - final interpretation:
    - clean `R0 = 1.0`
    - intentionally stopped after `R0`
- `exoplanet`
  - authoritative task run: `exoplanet-detection-period-c4ar-002-defaulttimeout`
  - final interpretation:
    - `R0`, `R1`, `R2` clean `0.0`
    - `R3` timeout
    - no positive transfer evidence

## Code Status

The orchestrator fixes that landed during this batch are in:

- [`run_skillx_refine_benchmark.py`](<INCUBATOR_REPO_ROOT>/mac_autoresearch_support/scripts/run_skillx_refine_benchmark.py)
- [`test_run_skillx_refine_benchmark.py`](<INCUBATOR_REPO_ROOT>/tests/test_run_skillx_refine_benchmark.py)

The important fixes are:

- backup before risky resume
- partial-round resume from cached executor results
- non-destructive handling of already-materialized earlier rounds
- branch resume from the correct round
- timeout growth with a `30` minute cap
- timeout multiplier carry-over across resumed invocations
- preserved earlier completed rounds in resumed final outputs
- fixed next-round materialization bug that had blocked `exoplanet` after `R0`

Validation:

- `./.venv-swebench/bin/python -m unittest tests.test_run_skillx_refine_benchmark`
- `36 tests` passed

## If A New Session Continues Work

Do:

- start from fresh non-overwriting run ids
- treat existing task-run directories as frozen evidence
- use the closeout summary and per-task checkpoints rather than reconstructing the story from scratch

Do not:

- claim that all four tasks were uninterrupted `R0 -> R3` chains
- resume a damaged run in place unless that is explicitly the goal and the auto-backup path is acceptable

## Highest-Value Follow-Ups

- `energy`
  - repeatability checks for `R0 = 1.0`
- `taxonomy`
  - a fresh isolated rerun only if cleaner artifact continuity is needed
- `exoplanet`
  - a fresh rerun only if specifically probing last-round timeout sensitivity
