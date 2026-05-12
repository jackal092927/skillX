# SkillX Round2 Guarded-Patch 5-Batch Plan

- created_at: `2026-05-10T07:51:54.640579+00:00`
- materialized_root: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10`
- source candidate: `outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10`
- batch_count: `5`
- total_tasks: `20`
- total_pairs: `140`
- schemas_per_task: `7`
- pair_count_per_batch: `28`

| batch | dashboard port | pairs | tasks | task names | pair manifest |
| --- | ---: | ---: | ---: | --- | --- |
| `batch-01` | `8782` | `28` | `4` | `adaptive-cruise-control, earthquake-phase-association, energy-ac-optimal-power-flow, data-to-d3` | `batch-01_pair_manifest.json` |
| `batch-02` | `8783` | `28` | `4` | `citation-check, energy-market-pricing, exceltable-in-ppt, fix-build-google-auto` | `batch-02_pair_manifest.json` |
| `batch-03` | `8784` | `28` | `4` | `civ6-adjacency-optimizer, exoplanet-detection-period, fix-druid-loophole-cve, azure-bgp-oscillation-route-leak` | `batch-03_pair_manifest.json` |
| `batch-04` | `8785` | `28` | `4` | `court-form-filling, earthquake-plate-calculation, financial-modeling-qa, 3d-scan-calc` | `batch-04_pair_manifest.json` |
| `batch-05` | `8786` | `28` | `4` | `dapt-intrusion-detection, econ-detrending-correlation, find-topk-similiar-chemicals, fix-build-agentops` | `batch-05_pair_manifest.json` |

## Launch

```bash
bash experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-round2-guarded-patch-2026-05-10-5batch/launch_round2_guarded_patch_batches.sh
```

This starts five tmux sessions. Each batch runs serially inside its own tmux session with `SKILLX_MAX_CONCURRENT_PAIRS=1`, for five total parallel launcher threads.
