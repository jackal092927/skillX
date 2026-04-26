# SkillX First20 Rate-Limit Rerun Batches

## Scope

- source_audit: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/quota-429-audit-first20-round0-2026-04-26/effective_pair_quota_flags.csv`
- affected_pair_count: `115`
- affected_task_count: `18`
- batch_count: `5`

## Batch Plan

| batch | pairs | tasks | task_names | pair_manifest |
|---|---:|---:|---|---|
| `batch-01` | 26 | 4 | `adaptive-cruise-control, earthquake-phase-association, energy-ac-optimal-power-flow, data-to-d3` | `batch-01_pair_manifest.json` |
| `batch-02` | 25 | 4 | `citation-check, energy-market-pricing, exceltable-in-ppt, fix-build-google-auto` | `batch-02_pair_manifest.json` |
| `batch-03` | 22 | 4 | `civ6-adjacency-optimizer, exoplanet-detection-period, fix-druid-loophole-cve, azure-bgp-oscillation-route-leak` | `batch-03_pair_manifest.json` |
| `batch-04` | 21 | 3 | `court-form-filling, earthquake-plate-calculation, financial-modeling-qa` | `batch-04_pair_manifest.json` |
| `batch-05` | 21 | 3 | `dapt-intrusion-detection, econ-detrending-correlation, find-topk-similiar-chemicals` | `batch-05_pair_manifest.json` |

## Validation

- No task appears in more than one batch.
- Total selected pairs across all manifests is 115.
- Pair counts are 26, 25, 22, 21, 21; exact 23-per-batch is impossible while keeping every task in only one batch because most affected tasks contribute 7 pairs.

## Run

From a worktree that has the first20 materialized root (`manifest.json` and `pair_specs.jsonl`) available:

```bash
bash experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/rate-limit-rerun-batches-first20-round0-2026-04-26/launch_rate_limit_rerun_batches.sh \
  run-first20-rate-limit-rerun-2026-04-26 \
  skillx-first20-rate-limit-rerun \
  8767
```

Each tmux session runs serially (`SKILLX_MAX_CONCURRENT_PAIRS=1`) and uses a unique dashboard port.
