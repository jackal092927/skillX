# SkillX Round1 First20 Full-Matrix Effective Archive (2026-05-04)

## Status

- effective_pairs: `140/140`
- tasks: `20`
- schemas: `7`
- launcher_failed_pairs: `0`
- rerun_replaced_pairs: `3`
- classification_counts: `{'clean_success': 66, 'scientific_failure': 74}`
- outer_loop_ready: `True`

## Effective Result Inputs

- checkpoint: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-round1-first20-fullmatrix-effective-2026-05-04/checkpoint.md`
- final pair table: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-round1-first20-fullmatrix-effective-2026-05-04/final_pair_results.csv`
- score matrix: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-round1-first20-fullmatrix-effective-2026-05-04/score_matrix_wide.csv`
- global status: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/global-round1-first20-fullmatrix-effective-2026-05-04/global_pair_status.json`
- control plane bundle: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-control-plane-round1-fullmatrix-effective-2026-05-04/control_plane_bundle.json`
- assignment summary: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-control-plane-round1-fullmatrix-effective-2026-05-04/summary.md`

## Rerun Overlay

- `3d-scan-calc__artifact-generation`: base=`succeeded`, rerun=`succeeded`, source=`run-round1-first20-fullmatrix-infra-rerun-2026-05-04`
- `data-to-d3__retrieval-heavy-synthesis`: base=`succeeded`, rerun=`succeeded`, source=`run-round1-first20-fullmatrix-infra-rerun-2026-05-04`
- `adaptive-cruise-control__retrieval-heavy-synthesis`: base=`failed`, rerun=`succeeded`, source=`run-round1-first20-fullmatrix-adaptive-rhs-rerun-2026-05-04`

## Assignment Snapshot

- assignment_score_mode: `trajectory`
- assigned_tasks: `14`
- unassigned_tasks: `6` (`3d-scan-calc`, `azure-bgp-oscillation-route-leak`, `citation-check`, `fix-build-agentops`, `fix-build-google-auto`, `fix-druid-loophole-cve`)
- multi_assignments: `23`
- update_floor_k: `2`
- primary assignment counts:
  - `analytic-pipeline`: `3`
  - `artifact-generation`: `2`
  - `engineering-composition`: `2`
  - `environment-control`: `2`
  - `methodology-guardrail`: `1`
  - `orchestration-delegation`: `2`
  - `retrieval-heavy-synthesis`: `2`

- schema training evidence counts:
  - `analytic-pipeline`: `3`
  - `artifact-generation`: `3`
  - `engineering-composition`: `3`
  - `environment-control`: `3`
  - `methodology-guardrail`: `4`
  - `orchestration-delegation`: `3`
  - `retrieval-heavy-synthesis`: `4`

## Next Outer-Loop Step

Use the global status and control-plane artifacts above as the effective input. The next schema rewrite should use the original primary Claude plan as default and `~/.claude-skillx-fallback` as first fallback.

Recommended inputs:

- `--global-pair-status-path experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/global-round1-first20-fullmatrix-effective-2026-05-04/global_pair_status.json`
- control-plane seed: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-control-plane-round1-fullmatrix-effective-2026-05-04/control_plane_bundle.json`
- effective score table: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-round1-first20-fullmatrix-effective-2026-05-04/final_pair_results.csv`

