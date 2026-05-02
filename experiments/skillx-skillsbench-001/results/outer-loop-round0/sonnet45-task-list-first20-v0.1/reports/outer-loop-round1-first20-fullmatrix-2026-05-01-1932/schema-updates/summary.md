# SkillX Outer-Loop Schema Update Package: `outer-loop-round0`

- generated_at: `2026-05-01T23:43:45.632563+00:00`
- output_dir: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-round1-first20-fullmatrix-2026-05-01-1932/schema-updates`
- next_round_id: `outer-loop-round1`
- rewrite_mode: `llm`
- llm_model: `anthropic/claude-sonnet-4-5`
- min_support_size: `0`
- max_update_schemas: `0`
- rewrite_verification: `passed` (7/7)

## Round Update Plan

| schema_id | action | reason | support | reliable | priority | challenger |
| --- | --- | --- | ---: | ---: | ---: | --- |
| analytic-pipeline | update | selected_by_priority | 5 | 5 | 9.50 | differentiating |
| artifact-generation | update | selected_by_priority | 2 | 2 | 4.50 | differentiating |
| engineering-composition | update | selected_by_priority | 4 | 4 | 8.00 | differentiating |
| environment-control | update | selected_by_priority | 5 | 5 | 9.00 | differentiating |
| methodology-guardrail | update | selected_by_priority | 4 | 4 | 7.50 | differentiating |
| orchestration-delegation | update | selected_by_priority | 4 | 4 | 8.50 | differentiating |
| retrieval-heavy-synthesis | update | selected_by_priority | 4 | 4 | 8.00 | differentiating |

## Evidence Summary

- `artifact-generation`: support=`2`, reliable=`2`, mean_score=`49.8334`, competitors=`analytic-pipeline (5)`
- `analytic-pipeline`: support=`5`, reliable=`5`, mean_score=`81.45`, competitors=`artifact-generation (5), engineering-composition (2), methodology-guardrail (1)`
- `engineering-composition`: support=`4`, reliable=`4`, mean_score=`58.5625`, competitors=`analytic-pipeline (7), environment-control (1)`
- `retrieval-heavy-synthesis`: support=`4`, reliable=`4`, mean_score=`67.8125`, competitors=`analytic-pipeline (5), orchestration-delegation (1), methodology-guardrail (1)`
- `environment-control`: support=`5`, reliable=`5`, mean_score=`88.0`, competitors=`analytic-pipeline (6), retrieval-heavy-synthesis (1), engineering-composition (1)`
- `methodology-guardrail`: support=`4`, reliable=`4`, mean_score=`67.8125`, competitors=`analytic-pipeline (6), retrieval-heavy-synthesis (1)`
- `orchestration-delegation`: support=`4`, reliable=`4`, mean_score=`100.0`, competitors=`analytic-pipeline (8), retrieval-heavy-synthesis (1)`

## Challenger Eval Plan

- `analytic-pipeline` / `differentiating`: 6 task(s): `court-form-filling, earthquake-phase-association, azure-bgp-oscillation-route-leak, exceltable-in-ppt, civ6-adjacency-optimizer, 3d-scan-calc`
- `artifact-generation` / `differentiating`: 6 task(s): `civ6-adjacency-optimizer, court-form-filling, 3d-scan-calc, citation-check, fix-build-agentops, fix-build-google-auto`
- `engineering-composition` / `differentiating`: 6 task(s): `exoplanet-detection-period, find-topk-similiar-chemicals, earthquake-phase-association, civ6-adjacency-optimizer, 3d-scan-calc, citation-check`
- `environment-control` / `differentiating`: 6 task(s): `energy-ac-optimal-power-flow, exceltable-in-ppt, financial-modeling-qa, energy-market-pricing, exoplanet-detection-period, 3d-scan-calc`
- `methodology-guardrail` / `differentiating`: 6 task(s): `dapt-intrusion-detection, data-to-d3, court-form-filling, azure-bgp-oscillation-route-leak, 3d-scan-calc, citation-check`
- `orchestration-delegation` / `differentiating`: 6 task(s): `earthquake-plate-calculation, econ-detrending-correlation, earthquake-phase-association, exceltable-in-ppt, 3d-scan-calc, adaptive-cruise-control`
- `retrieval-heavy-synthesis` / `differentiating`: 6 task(s): `energy-market-pricing, adaptive-cruise-control, dapt-intrusion-detection, court-form-filling, 3d-scan-calc, citation-check`
