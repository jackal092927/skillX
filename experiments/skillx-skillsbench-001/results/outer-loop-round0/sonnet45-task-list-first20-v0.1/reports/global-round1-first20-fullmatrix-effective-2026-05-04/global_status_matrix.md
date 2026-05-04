# SkillX Round0 Global Status

- generated_at: `2026-05-04T17:58:28.475295+00:00`
- skillsbench_root: `/Users/Jackal/iWorld/projects/skillsbench-src`
- task_count_detected: `20`
- schema_count_detected: `7`
- total_pairs_expected: `140`
- completed_pairs: `140`
- docker_incident_pairs: `0`
- other_failed_pairs: `0`
- unrun_pairs: `0`

Legend: `C# = completed`, `D# = latest failure was Docker incident`, `F# = latest failure was other error`, `-0 = never run`.

## Source Runs

| run_label | total | succeeded | failed | finished_at | report_path |
| --- | ---: | ---: | ---: | --- | --- |
| run-round1-first20-fullmatrix-adaptive-rhs-rerun-2026-05-04 | 1 | 1 | 0 | 2026-05-04T15:23:11.090284+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round1-first20-fullmatrix-2026-05-01-1932-candidates/reports/run-round1-first20-fullmatrix-adaptive-rhs-rerun-2026-05-04/run_report.json` |
| run-round1-first20-fullmatrix-fallback-2026-05-01-b01 | 49 | 49 | 0 | 2026-05-03T16:12:22.535452+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round1-first20-fullmatrix-2026-05-01-1932-candidates/reports/run-round1-first20-fullmatrix-fallback-2026-05-01-b01/run_report.json` |
| run-round1-first20-fullmatrix-fallback-2026-05-01-b02 | 49 | 48 | 1 | 2026-05-04T13:13:17.314962+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round1-first20-fullmatrix-2026-05-01-1932-candidates/reports/run-round1-first20-fullmatrix-fallback-2026-05-01-b02/run_report.json` |
| run-round1-first20-fullmatrix-fallback-2026-05-01-b03 | 42 | 42 | 0 | 2026-05-04T03:27:12.189678+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round1-first20-fullmatrix-2026-05-01-1932-candidates/reports/run-round1-first20-fullmatrix-fallback-2026-05-01-b03/run_report.json` |
| run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03 | 140 | 139 | 1 | 2026-05-04T13:13:17.314962+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round1-first20-fullmatrix-2026-05-01-1932-candidates/reports/run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03/run_report.json` |
| run-round1-first20-fullmatrix-infra-rerun-2026-05-04 | 2 | 2 | 0 | 2026-05-04T14:27:12.304886+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round1-first20-fullmatrix-2026-05-01-1932-candidates/reports/run-round1-first20-fullmatrix-infra-rerun-2026-05-04/run_report.json` |

## Task x Schema Matrix

| task | artifact-generation | analytic-pipeline | engineering-composition | retrieval-heavy-synthesis | environment-control | methodology-guardrail | orchestration-delegation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3d-scan-calc | C3 | C2 | C2 | C2 | C2 | C2 | C2 |
| adaptive-cruise-control | C2 | C2 | C2 | C3 | C2 | C2 | C2 |
| azure-bgp-oscillation-route-leak | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| citation-check | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| civ6-adjacency-optimizer | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| court-form-filling | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| dapt-intrusion-detection | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| data-to-d3 | C2 | C2 | C2 | C3 | C2 | C2 | C2 |
| earthquake-phase-association | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| earthquake-plate-calculation | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| econ-detrending-correlation | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| energy-ac-optimal-power-flow | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| energy-market-pricing | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| exceltable-in-ppt | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| exoplanet-detection-period | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| financial-modeling-qa | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| find-topk-similiar-chemicals | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| fix-build-agentops | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| fix-build-google-auto | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| fix-druid-loophole-cve | C2 | C2 | C2 | C2 | C2 | C2 | C2 |

## Pairs Needing Rerun: Docker Incident

- none

## Pairs Needing Attention: Other Failure

- none

## Pairs Not Yet Run

- none
