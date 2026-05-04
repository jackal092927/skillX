# SkillX Round0 Outer-Loop Control Plane: `outer-loop-round1-first20-fullmatrix-effective-2026-05-04`

- generated_at: `2026-05-04T17:58:48.471210+00:00`
- output_dir: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-control-plane-round1-fullmatrix-effective-2026-05-04`
- schemas: `artifact-generation, analytic-pipeline, engineering-composition, retrieval-heavy-synthesis, environment-control, methodology-guardrail, orchestration-delegation`
- assignment_score_mode: `trajectory`
- assignment_score_formula: `0.4*mean(max(R1..R3 - R0, 0)) + 0.25*post_r0_monotonicity + 0.2*fraction(R1..R3 > R0) + 0.15*max(last_post_round - R0, 0)`
- tie_break_policy: `semantic_prior -> balance_when_score_range_leq_threshold -> stable_random`
- tasks_total: `20`
- tasks_with_scores: `20`
- full_coverage_tasks: `20`
- assigned_tasks: `14`
- multi_assignments: `23`
- occupied_cluster_count: `7`
- mean_assignment_margin_pp: `32.55`
- low_margin_task_fraction: `0.0`

## Cluster Occupancy

| schema_id | primary_assigned | multi_assigned | training_evidence | mean_assigned_score | observed_task_count | floor_k | below_training_floor |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| artifact-generation | 2 | 3 | 3 | 80.00 | 20 | 2 | no |
| analytic-pipeline | 3 | 3 | 3 | 86.67 | 20 | 2 | no |
| engineering-composition | 2 | 3 | 3 | 100.00 | 20 | 2 | no |
| retrieval-heavy-synthesis | 2 | 4 | 4 | 66.25 | 20 | 2 | no |
| environment-control | 2 | 3 | 3 | 55.62 | 20 | 2 | no |
| methodology-guardrail | 1 | 4 | 4 | 80.00 | 20 | 2 | no |
| orchestration-delegation | 2 | 3 | 3 | 69.96 | 20 | 2 | no |

## Schema Training Assignments

| schema_id | task | role | reasons | score | dR0 | trajectory | rank | primary_assigned |
| --- | --- | --- | --- | ---: | ---: | --- | ---: | --- |
| artifact-generation | exceltable-in-ppt | primary_assignment | primary;near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | artifact-generation |
| artifact-generation | earthquake-plate-calculation | primary_assignment | primary;near_best;stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 1 | artifact-generation |
| artifact-generation | earthquake-phase-association | stable_gain_support | high_score;stable_gain | 80.00 | 100.00 | stable_non_decreasing_gain | 2 | analytic-pipeline |
| analytic-pipeline | dapt-intrusion-detection | primary_assignment | primary;near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | analytic-pipeline |
| analytic-pipeline | earthquake-phase-association | primary_assignment | primary;near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | analytic-pipeline |
| analytic-pipeline | court-form-filling | primary_assignment | primary;near_best;stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 1 | analytic-pipeline |
| engineering-composition | adaptive-cruise-control | primary_assignment | primary;near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | engineering-composition |
| engineering-composition | energy-ac-optimal-power-flow | primary_assignment | primary;near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | engineering-composition |
| engineering-composition | data-to-d3 | stable_gain_support | high_score;stable_gain | 80.00 | 100.00 | stable_non_decreasing_gain | 2 | orchestration-delegation |
| retrieval-heavy-synthesis | energy-market-pricing | primary_assignment | primary;near_best | 72.50 | 100.00 | stable_no_loss_gain | 1 | retrieval-heavy-synthesis |
| retrieval-heavy-synthesis | financial-modeling-qa | primary_assignment | primary;near_best;stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 1 | retrieval-heavy-synthesis |
| retrieval-heavy-synthesis | earthquake-phase-association | stable_gain_support | stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 3 | analytic-pipeline |
| retrieval-heavy-synthesis | energy-ac-optimal-power-flow | stable_gain_support | stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 3 | engineering-composition |
| environment-control | econ-detrending-correlation | primary_assignment | primary;near_best;high_score;stable_gain | 80.00 | 100.00 | stable_non_decreasing_gain | 1 | environment-control |
| environment-control | find-topk-similiar-chemicals | primary_assignment | primary;near_best | 31.25 | 100.00 | partial_gain_then_regression | 1 | environment-control |
| environment-control | energy-market-pricing | stable_gain_support | stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 2 | retrieval-heavy-synthesis |
| methodology-guardrail | exoplanet-detection-period | primary_assignment | primary;near_best;high_score;stable_gain | 80.00 | 100.00 | stable_non_decreasing_gain | 1 | methodology-guardrail |
| methodology-guardrail | dapt-intrusion-detection | stable_gain_support | stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 3 | analytic-pipeline |
| methodology-guardrail | data-to-d3 | stable_gain_support | stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 3 | orchestration-delegation |
| methodology-guardrail | energy-ac-optimal-power-flow | stable_gain_support | stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 3 | engineering-composition |
| orchestration-delegation | data-to-d3 | primary_assignment | primary;near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | orchestration-delegation |
| orchestration-delegation | civ6-adjacency-optimizer | primary_assignment | primary;near_best | 39.92 | 60.00 | partial_gain_then_regression | 1 | orchestration-delegation |
| orchestration-delegation | econ-detrending-correlation | stable_gain_support | stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 3 | environment-control |

## Assigned Tasks

| task | assigned | best | second | margin_pp | confidence | tie_break |
| --- | --- | ---: | ---: | ---: | --- | --- |
| adaptive-cruise-control | engineering-composition | 100.00 | 31.25 | 68.75 | high | no |
| civ6-adjacency-optimizer | orchestration-delegation | 39.92 | 14.25 | 25.67 | high | no |
| court-form-filling | analytic-pipeline | 60.00 | 51.25 | 8.75 | medium | no |
| dapt-intrusion-detection | analytic-pipeline | 100.00 | 72.50 | 27.50 | high | no |
| data-to-d3 | orchestration-delegation | 100.00 | 80.00 | 20.00 | high | no |
| earthquake-phase-association | analytic-pipeline | 100.00 | 80.00 | 20.00 | high | no |
| earthquake-plate-calculation | artifact-generation | 60.00 | 31.25 | 28.75 | high | no |
| econ-detrending-correlation | environment-control | 80.00 | 72.50 | 7.50 | medium | no |
| energy-ac-optimal-power-flow | engineering-composition | 100.00 | 72.50 | 27.50 | high | no |
| energy-market-pricing | retrieval-heavy-synthesis | 72.50 | 60.00 | 12.50 | high | no |
| exceltable-in-ppt | artifact-generation | 100.00 | 31.25 | 68.75 | high | no |
| exoplanet-detection-period | methodology-guardrail | 80.00 | 0.00 | 80.00 | high | no |
| financial-modeling-qa | retrieval-heavy-synthesis | 60.00 | 31.25 | 28.75 | high | no |
| find-topk-similiar-chemicals | environment-control | 31.25 | 0.00 | 31.25 | high | no |

## Unassigned Tasks

- `3d-scan-calc`: status=`unassigned_no_positive_signal`, observed=`7`, missing=``
- `azure-bgp-oscillation-route-leak`: status=`unassigned_no_positive_signal`, observed=`7`, missing=``
- `citation-check`: status=`unassigned_no_positive_signal`, observed=`7`, missing=``
- `fix-build-agentops`: status=`unassigned_no_positive_signal`, observed=`7`, missing=``
- `fix-build-google-auto`: status=`unassigned_no_positive_signal`, observed=`7`, missing=``
- `fix-druid-loophole-cve`: status=`unassigned_no_positive_signal`, observed=`7`, missing=``

## Top-3 Near Ties

- `3d-scan-calc`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `azure-bgp-oscillation-route-leak`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `citation-check`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `fix-build-agentops`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `fix-build-google-auto`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `fix-druid-loophole-cve`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
