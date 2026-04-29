# Checkpoint - 2026-04-29 - SkillX First20 Round-0 Final

Project: `projects/skillX`
Date: 2026-04-29
Status: completed final `20 x 7` Setting A round-0 matrix

## 1. What changed at this checkpoint

The first `20 tasks x 7 schemas` Setting A inner-loop matrix is now finalized
with all three rate-limit rerun batches exported and folded into the official
round-0 checkpoint.

Final effective state:

- tasks: `20`
- schemas: `7`
- effective pairs: `140`
- launcher-succeeded pairs: `140`
- launcher-failed pairs: `0`
- every task has all `7` schema pairs completed

This supersedes the 2026-04-26 checkpoint. The earlier checkpoint established
an executable `20 x 7` matrix; this checkpoint replaces the saturated or
rate-limit-affected rows with the completed rerun-batch results.

## 2. Run labels

Base run:

- `run-first20x7-round0-2026-04-24`

Rerun overlays:

- `run-first20x7-rerun-failed5-2026-04-25-v2`
- `run-first20-rate-limit-rerun-2026-04-27-3batch-b01`
- `run-first20-rate-limit-rerun-2026-04-27-3batch-b02`
- `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`

Final batch status:

- B01: `40 / 40` completed
- B02: `36 / 36` completed
- B03: `39 / 39` completed

## 3. Result summary

Execution status:

- global first20 pair status: `140 completed`, `0 failed`, `0 unrun`
- checkpoint effective pair count: `140`
- rerun replacements applied: `120`

Outcome classification:

- `clean_success`: `79`
- `scientific_failure`: `60`
- `runtime_failure`: `1`

The single `runtime_failure` is retained as measured completed evidence at the
launcher level, but it remains marked separately for downstream diagnostics.

## 4. Assignment summary

The assignment control plane now uses R0-relative trajectory scoring. R0 is
treated only as the baseline, not as positive performance credit.

Current assignment score:

```text
0.40 * mean(max(R1..R3 - R0, 0))
+ 0.25 * post_r0_monotonicity
+ 0.20 * fraction(R1..R3 > R0)
+ 0.15 * max(last_post_round - R0, 0)
```

Assignment outcome:

- primary assigned tasks: `15`
- unassigned tasks with no positive R0-relative signal: `5`
- multi-assignments for outer-loop training evidence: `27`
- occupied schemas: `7 / 7`

Primary assignment counts:

- `analytic-pipeline`: `3`
- `environment-control`: `3`
- `engineering-composition`: `2`
- `methodology-guardrail`: `2`
- `orchestration-delegation`: `2`
- `retrieval-heavy-synthesis`: `2`
- `artifact-generation`: `1`

Unassigned no-positive-signal tasks:

- `3d-scan-calc`
- `citation-check`
- `fix-build-agentops`
- `fix-build-google-auto`
- `fix-druid-loophole-cve`

## 5. Canonical artifacts

Final global status:

- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/global-round0-status-first20-final-2026-04-29/global_pair_status.json`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/global-round0-status-first20-final-2026-04-29/global_pair_status.csv`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/global-round0-status-first20-final-2026-04-29/global_status_matrix.md`

Final merged checkpoint:

- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-first20-round0-rate-limit-rerun-3batch-final-2026-04-29/checkpoint.md`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-first20-round0-rate-limit-rerun-3batch-final-2026-04-29/checkpoint_summary.json`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-first20-round0-rate-limit-rerun-3batch-final-2026-04-29/final_pair_results.csv`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-first20-round0-rate-limit-rerun-3batch-final-2026-04-29/score_matrix_wide.csv`

Final outer-loop control plane:

- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-control-plane-first20-final-2026-04-29/control_plane_bundle.json`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-control-plane-first20-final-2026-04-29/assignments.csv`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-control-plane-first20-final-2026-04-29/multi_assignments.csv`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-control-plane-first20-final-2026-04-29/schema_training_assignments.csv`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-control-plane-first20-final-2026-04-29/summary.md`

Batch reports:

- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/run-first20-rate-limit-rerun-2026-04-27-3batch-b01/`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/run-first20-rate-limit-rerun-2026-04-27-3batch-b02/`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/run-first20-rate-limit-rerun-2026-04-27-3batch-b03/`

## 6. Code included

This checkpoint includes the runner, monitor, export, and control-plane fixes
needed to make the final evidence reproducible:

- precise rate-limit detection and fallback handling
- R0 baseline-perfect rerun guard and stale-report handling
- effective R0 dashboard semantics
- Docker image retention support for task/schema inner-loop reuse
- final R0-relative assignment scoring and multi-assignment evidence export

## 7. Next step

Use the final outer-loop control-plane bundle as the input for issue `#8`:

> Package first-round schema updates.

The primary input is:

- `control_plane_bundle.json`

The schema-update step should consume the `27` multi-assignment evidence links,
not only the `15` primary assignments.
