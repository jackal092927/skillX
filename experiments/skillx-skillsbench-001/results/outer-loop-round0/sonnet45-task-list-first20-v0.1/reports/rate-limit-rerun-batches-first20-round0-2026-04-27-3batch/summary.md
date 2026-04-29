# SkillX Rate-Limit Rerun 3-Batch Plan

- created_at: `2026-04-27T02:02:03.165798+00:00`
- materialized_root: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1`
- source_plan_dir: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/rate-limit-rerun-batches-first20-round0-2026-04-26`
- total_pairs: `115`
- total_tasks: `18`
- pair_counts: `40, 36, 39`
- balance_max_minus_min: `4`

| batch | pairs | tasks | task names |
| --- | ---: | ---: | --- |
| batch-01 | 40 | 6 | adaptive-cruise-control, citation-check, civ6-adjacency-optimizer, court-form-filling, dapt-intrusion-detection, data-to-d3 |
| batch-02 | 36 | 6 | earthquake-phase-association, earthquake-plate-calculation, econ-detrending-correlation, energy-ac-optimal-power-flow, energy-market-pricing, azure-bgp-oscillation-route-leak |
| batch-03 | 39 | 6 | exoplanet-detection-period, financial-modeling-qa, find-topk-similiar-chemicals, fix-druid-loophole-cve, exceltable-in-ppt, fix-build-google-auto |

## Launch

```bash
BASE_PORT=8767
bash experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/rate-limit-rerun-batches-first20-round0-2026-04-27-3batch/launch_rate_limit_rerun_batches.sh run-first20-rate-limit-rerun-2026-04-27-3batch skillx-first20-rate-limit-rerun-3b "$BASE_PORT"
```
