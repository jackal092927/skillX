# Checkpoint — 2026-04-26 — SkillX First20 Round-0 Completion

Project: `projects/skillX`
Date: 2026-04-26
Status: completed effective `20 x 7` Setting A round-0 matrix

## 1. What changed at this checkpoint

The first `20 tasks x 7 schemas` Setting A inner-loop matrix is now complete
with auditable end states.

The original run completed all `140` pair attempts, but `5` pairs failed at the
launcher/runtime level. Those `5` failed pairs were rerun under a separate rerun
label after fixing the Python virtualenv entrypoint issue. The effective merged
checkpoint now has:

- effective pairs: `140`
- tasks: `20`
- schemas: `7`
- launcher-succeeded pairs: `140`
- launcher-failed pairs: `0`
- every task has all `7` schemas successfully executed

This closes the execution requirement for issue `#2` and makes issue `#3`
the next active step: build the score matrix, assignments, and diagnostics.

## 2. Run labels

Base run:

- `run-first20x7-round0-2026-04-24`

Successful rerun overlay:

- `run-first20x7-rerun-failed5-2026-04-25-v2`

The intermediate failed rerun label
`run-first20x7-rerun-failed5-2026-04-25` is intentionally not used as effective
evidence; it is retained only as a debugging record for the missing-virtualenv
dependency issue.

## 3. Rerun overlay

The following base-run failed pairs were replaced by successful rerun-v2 outputs:

- `azure-bgp-oscillation-route-leak__analytic-pipeline`
- `azure-bgp-oscillation-route-leak__engineering-composition`
- `azure-bgp-oscillation-route-leak__retrieval-heavy-synthesis`
- `data-to-d3__environment-control`
- `data-to-d3__methodology-guardrail`

Final effective state:

- original failed pairs: `5`
- rerun replacements: `5`
- final failed pairs: `0`

## 4. Result interpretation

The effective checkpoint distinguishes execution success from scientific
success.

Execution status:

- all `140` pairs executed successfully at launcher level
- Docker is no longer the blocker for this batch
- the rerun repaired infrastructure-level missing dependency failures

Outcome classification:

- `clean_success`: `20`
- `scientific_failure`: `120`

`scientific_failure` means the pair ran cleanly but selected reward was `0` or
negative. It should be treated as valid low-score evidence for assignment and
outer-loop optimization, not as an infrastructure failure.

## 5. Key report artifacts

Canonical merged checkpoint:

- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-first20-round0-2026-04-26/checkpoint.md`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-first20-round0-2026-04-26/checkpoint_summary.json`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-first20-round0-2026-04-26/final_pair_results.csv`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-first20-round0-2026-04-26/score_matrix_wide.csv`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-first20-round0-2026-04-26/schema_summary.csv`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-first20-round0-2026-04-26/task_summary.csv`

Run-level reports:

- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/run-first20x7-round0-2026-04-24/`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/run-first20x7-rerun-failed5-2026-04-25-v2/`

Exporter:

- `scripts/build_round0_checkpoint_report.py`

## 6. Next step

The next step is issue `#3`:

> Build round-0 score matrix, assignments, and diagnostics.

Use these merged checkpoint artifacts as the effective round-0 input:

- `final_pair_results.csv`
- `score_matrix_wide.csv`
- `checkpoint_summary.json`

The outer-loop should treat the `120` scientific failures as measured evidence
about schema-task mismatch or no-gain behavior, not as missing data.
