# SkillX Round2 Guarded-Patch Overall Comparison

Generated: 2026-05-12T02:49:19.474394+00:00

## Executive Summary

Round2 guarded-patch is directionally better than the previous effective inner-loop checkpoint, but the signal is mixed rather than uniformly positive.

- Valid final results: 140 / 140 pairs.
- Average selected score: 45.2% -> 51.0% (+5.8 pp).
- Clean-success pairs: 66 -> 74 (+8).
- Pair movement: 25 improved, 20 regressed, 95 unchanged.
- Final exception audit: 0 final rate-limit signals; runtime profile observed was primary:claude-code only; all rerun-required items were repaired before final aggregation.

## Best Task Deltas

| Task | Delta pp | Improved | Regressed | Unchanged |
|---|---:|---:|---:|---:|
| earthquake-plate-calculation | +71.4 | 5 | 0 | 2 |
| exoplanet-detection-period | +71.4 | 5 | 0 | 2 |
| dapt-intrusion-detection | +57.1 | 4 | 0 | 3 |
| exceltable-in-ppt | +42.9 | 3 | 0 | 4 |
| energy-market-pricing | +28.6 | 2 | 0 | 5 |

## Worst Task Deltas

| Task | Delta pp | Improved | Regressed | Unchanged |
|---|---:|---:|---:|---:|
| financial-modeling-qa | -42.9 | 0 | 3 | 4 |
| court-form-filling | -28.6 | 1 | 3 | 3 |
| data-to-d3 | -28.6 | 1 | 3 | 3 |
| energy-ac-optimal-power-flow | -28.6 | 0 | 2 | 5 |
| civ6-adjacency-optimizer | -20.0 | 0 | 5 | 2 |

## Schema Deltas

| Schema | Delta pp | Improved | Regressed | Unchanged |
|---|---:|---:|---:|---:|
| orchestration-delegation | +19.5 | 5 | 2 | 13 |
| analytic-pipeline | +17.0 | 6 | 3 | 11 |
| retrieval-heavy-synthesis | +7.2 | 4 | 3 | 13 |
| environment-control | +5.0 | 3 | 2 | 15 |
| engineering-composition | -0.2 | 3 | 4 | 13 |
| methodology-guardrail | -3.0 | 1 | 2 | 17 |
| artifact-generation | -5.0 | 3 | 4 | 13 |

## Recorded Reruns And Repairs

- 2026-05-10T21:17:14.055225+00:00: b04 issue; issues: dashboard health is completed_with_issues; actions: recorded only
- 2026-05-10T21:21:34.822824+00:00: court-form-filling__engineering-composition: completed_with_runtime_failures at R2; audit marked rerun required; action: archived b04 launcher log and court-form-filling__engineering-composition runtime-failure run before same-label rerun
- 2026-05-11T03:17:15.598274+00:00: b01 repaired; issues: dashboard health is stalled; actions: kill tmux session skillx-round2-guarded-patch-b01; archive launcher log /Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/launcher_logs/run-round2-guarded-patch-2026-05-10-b01 -> /Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/launcher_logs/_heartbeat_archives/run-round2-guarded-patch-2026-05-10-b01-20260511T031713Z; launch skillx-round2-guarded-patch-b01 on port 8782
- 2026-05-11T07:02:54.276626+00:00: b01 repaired; issues: tmux session missing, dashboard port not listening; actions: archive launcher log /Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/launcher_logs/run-round2-guarded-patch-2026-05-10-b01 -> /Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/launcher_logs/_heartbeat_archives/run-round2-guarded-patch-2026-05-10-b01-20260511T070253Z; launch skillx-round2-guarded-patch-b01 on port 8782
- 2026-05-11T07:02:54.276626+00:00: b02 repaired; issues: tmux session missing, dashboard port not listening; actions: archive launcher log /Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/launcher_logs/run-round2-guarded-patch-2026-05-10-b02 -> /Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/launcher_logs/_heartbeat_archives/run-round2-guarded-patch-2026-05-10-b02-20260511T070253Z; launch skillx-round2-guarded-patch-b02 on port 8783
- 2026-05-11T07:02:54.276626+00:00: b03 repaired; issues: tmux session missing, dashboard port not listening; actions: archive launcher log /Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/launcher_logs/run-round2-guarded-patch-2026-05-10-b03 -> /Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/launcher_logs/_heartbeat_archives/run-round2-guarded-patch-2026-05-10-b03-20260511T070253Z; launch skillx-round2-guarded-patch-b03 on port 8784
- 2026-05-11T07:02:54.276626+00:00: b05 repaired; issues: tmux session missing, dashboard port not listening; actions: archive launcher log /Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/launcher_logs/run-round2-guarded-patch-2026-05-10-b05 -> /Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/launcher_logs/_heartbeat_archives/run-round2-guarded-patch-2026-05-10-b05-20260511T070254Z; launch skillx-round2-guarded-patch-b05 on port 8786
- 2026-05-11T10:17:40.282254+00:00: b02 issue; issues: dashboard health is completed_with_issues; actions: recorded only
- 2026-05-11T10:19:11.202744+00:00: citation-check__artifact-generation, citation-check__methodology-guardrail: dashboard completed_with_issues; RUN_STATUS showed completed_with_runtime_failures; action: archived b02 runtime-failure pairs and launcher log before same-label rerun
- 2026-05-11T10:19:20.215426+00:00: b02 repaired; issues: tmux session missing, dashboard port not listening; actions: launch skillx-round2-guarded-patch-b02 on port 8783
- 2026-05-11T19:47:08Z: b01: user reported Docker error while only b01 remained active; docker info initially failed, then recovered after open -a Docker; action: started Docker Desktop after docker API was unavailable
- 2026-05-12T00:18:18.993282+00:00: b01 issue; issues: dashboard health is completed_with_issues; actions: recorded only
- 2026-05-12T00:18:59.399012+00:00: energy-ac-optimal-power-flow__environment-control: dashboard completed_with_issues; RUN_STATUS showed completed_with_runtime_failures at R0; action: archived b01 runtime-failure pair and launcher log before same-label rerun
- 2026-05-12T00:19:05.477556+00:00: b01 repaired; issues: tmux session missing, dashboard port not listening; actions: launch skillx-round2-guarded-patch-b01 on port 8782

## Files

- Visual overall page: `/Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/reports/round2_guarded_patch_overall_comparison_2026-05-12/overall.html`
- Pair comparison CSV: `/Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/reports/round2_guarded_patch_overall_comparison_2026-05-12/pair_comparison.csv`
- Metrics JSON: `/Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/reports/round2_guarded_patch_overall_comparison_2026-05-12/summary_metrics.json`
- Current final 140-result CSV: `/Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/reports/round2_guarded_patch_final_summary_2026-05-12/round2_guarded_patch_final_140_results.csv`
- Previous effective checkpoint CSV: `/Users/Jackal/iWorld/projects/skillX/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/checkpoint-round1-first20-fullmatrix-effective-2026-05-04/final_pair_results.csv`
