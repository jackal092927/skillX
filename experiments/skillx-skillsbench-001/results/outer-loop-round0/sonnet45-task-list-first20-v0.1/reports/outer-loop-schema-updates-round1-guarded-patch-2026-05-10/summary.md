# SkillX Outer-Loop Schema Update Package: `outer-loop-round1`

- generated_at: `2026-05-10T07:36:14.764817+00:00`
- output_dir: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-schema-updates-round1-guarded-patch-2026-05-10`
- next_round_id: `outer-loop-round2-guarded-patch`
- rewrite_mode: `llm`
- outer_loop_update_mode: `guarded_patch`
- llm_model: `anthropic/claude-sonnet-4-5`
- min_support_size: `0`
- max_update_schemas: `0`
- rewrite_verification: `passed` (7/7)

## Round Update Plan

| schema_id | action | update_mode | reason | support | reliable | priority | challenger |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| analytic-pipeline | update | guarded_patch | selected_by_guarded_patch_positive_transfer | 3 | 3 | 6.00 | conservative |
| artifact-generation | update | guarded_patch | selected_by_guarded_patch_positive_transfer | 3 | 3 | 6.00 | conservative |
| engineering-composition | update | guarded_patch | selected_by_guarded_patch_positive_transfer | 3 | 3 | 7.00 | conservative |
| environment-control | update | guarded_patch | selected_by_guarded_patch_positive_transfer | 3 | 3 | 6.00 | conservative |
| methodology-guardrail | update | guarded_patch | selected_by_guarded_patch_positive_transfer | 4 | 4 | 7.00 | conservative |
| orchestration-delegation | update | guarded_patch | selected_by_guarded_patch_positive_transfer | 3 | 3 | 6.00 | conservative |
| retrieval-heavy-synthesis | update | guarded_patch | selected_by_guarded_patch_positive_transfer | 4 | 4 | 7.00 | conservative |

## Evidence Summary

- `artifact-generation`: support=`3`, reliable=`3`, mean_score=`80.0`, competitors=`analytic-pipeline (6)`
- `analytic-pipeline`: support=`3`, reliable=`3`, mean_score=`86.6667`, competitors=`artifact-generation (6)`
- `engineering-composition`: support=`3`, reliable=`3`, mean_score=`93.3333`, competitors=`analytic-pipeline (7), environment-control (1)`
- `retrieval-heavy-synthesis`: support=`4`, reliable=`4`, mean_score=`63.125`, competitors=`analytic-pipeline (6)`
- `environment-control`: support=`3`, reliable=`3`, mean_score=`57.0833`, competitors=`analytic-pipeline (6)`
- `methodology-guardrail`: support=`4`, reliable=`4`, mean_score=`65.0`, competitors=`analytic-pipeline (6)`
- `orchestration-delegation`: support=`3`, reliable=`3`, mean_score=`66.6389`, competitors=`analytic-pipeline (6)`

## Challenger Eval Plan

- `analytic-pipeline` / `conservative`: 6 task(s): `dapt-intrusion-detection, energy-ac-optimal-power-flow, earthquake-phase-association, court-form-filling, 3d-scan-calc, azure-bgp-oscillation-route-leak`
- `artifact-generation` / `conservative`: 6 task(s): `data-to-d3, earthquake-phase-association, earthquake-plate-calculation, econ-detrending-correlation, exceltable-in-ppt, financial-modeling-qa`
- `engineering-composition` / `conservative`: 6 task(s): `adaptive-cruise-control, court-form-filling, data-to-d3, econ-detrending-correlation, energy-ac-optimal-power-flow, energy-market-pricing`
- `environment-control` / `conservative`: 6 task(s): `data-to-d3, econ-detrending-correlation, find-topk-similiar-chemicals, energy-market-pricing, 3d-scan-calc, azure-bgp-oscillation-route-leak`
- `methodology-guardrail` / `conservative`: 6 task(s): `data-to-d3, earthquake-phase-association, earthquake-plate-calculation, econ-detrending-correlation, energy-ac-optimal-power-flow, exoplanet-detection-period`
- `orchestration-delegation` / `conservative`: 6 task(s): `civ6-adjacency-optimizer, data-to-d3, econ-detrending-correlation, 3d-scan-calc, azure-bgp-oscillation-route-leak, citation-check`
- `retrieval-heavy-synthesis` / `conservative`: 6 task(s): `data-to-d3, earthquake-phase-association, econ-detrending-correlation, energy-ac-optimal-power-flow, financial-modeling-qa, energy-market-pricing`
