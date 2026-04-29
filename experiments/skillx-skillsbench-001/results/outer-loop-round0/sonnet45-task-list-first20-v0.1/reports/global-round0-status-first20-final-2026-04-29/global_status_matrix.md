# SkillX Round0 Global Status

- generated_at: `2026-04-29T05:08:07.497354+00:00`
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
| run-first20-rate-limit-rerun-2026-04-27-3batch-b01 | 40 | 40 | 0 | 2026-04-28T19:17:42.661479+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/run-first20-rate-limit-rerun-2026-04-27-3batch-b01/run_report.json` |
| run-first20-rate-limit-rerun-2026-04-27-3batch-b02 | 36 | 36 | 0 | 2026-04-28T14:58:51.951910+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/run-first20-rate-limit-rerun-2026-04-27-3batch-b02/run_report.json` |
| run-first20-rate-limit-rerun-2026-04-27-3batch-b03 | 39 | 39 | 0 | 2026-04-29T04:13:19.052462+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/run-first20-rate-limit-rerun-2026-04-27-3batch-b03/run_report.json` |
| run-first20x7-rerun-failed5-2026-04-25-v2 | 5 | 5 | 0 | 2026-04-26T04:21:25.623273+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/run-first20x7-rerun-failed5-2026-04-25-v2/run_report.json` |
| run-first20x7-round0-2026-04-24 | 140 | 135 | 5 | 2026-04-26T00:10:17.352136+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/run-first20x7-round0-2026-04-24/run_report.json` |

## Task x Schema Matrix

| task | artifact-generation | analytic-pipeline | engineering-composition | retrieval-heavy-synthesis | environment-control | methodology-guardrail | orchestration-delegation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3d-scan-calc | C1 | C1 | C1 | C1 | C1 | C1 | C1 |
| adaptive-cruise-control | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| azure-bgp-oscillation-route-leak | C2 | C2 | C2 | C2 | C1 | C1 | C1 |
| citation-check | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| civ6-adjacency-optimizer | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| court-form-filling | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| dapt-intrusion-detection | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| data-to-d3 | C2 | C2 | C2 | C2 | C3 | C2 | C1 |
| earthquake-phase-association | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| earthquake-plate-calculation | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| econ-detrending-correlation | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| energy-ac-optimal-power-flow | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| energy-market-pricing | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| exceltable-in-ppt | C2 | C2 | C2 | C2 | C2 | C1 | C2 |
| exoplanet-detection-period | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| financial-modeling-qa | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| find-topk-similiar-chemicals | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| fix-build-agentops | C1 | C1 | C1 | C1 | C1 | C1 | C1 |
| fix-build-google-auto | C1 | C1 | C2 | C2 | C2 | C2 | C2 |
| fix-druid-loophole-cve | C2 | C2 | C2 | C2 | C2 | C2 | C2 |

## Pairs Needing Rerun: Docker Incident

- none

## Pairs Needing Attention: Other Failure

- none

## Pairs Not Yet Run

- none
