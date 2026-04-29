# SkillX Round0 Outer-Loop Control Plane: `first20-round0-rate-limit-rerun-3batch-final-2026-04-29`

- generated_at: `2026-04-29T05:08:56.313435+00:00`
- output_dir: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-control-plane-first20-final-2026-04-29`
- schemas: `artifact-generation, analytic-pipeline, engineering-composition, retrieval-heavy-synthesis, environment-control, methodology-guardrail, orchestration-delegation`
- assignment_score_mode: `trajectory`
- assignment_score_formula: `0.4*mean(max(R1..R3 - R0, 0)) + 0.25*post_r0_monotonicity + 0.2*fraction(R1..R3 > R0) + 0.15*max(last_post_round - R0, 0)`
- tie_break_policy: `semantic_prior -> balance_when_score_range_leq_threshold -> stable_random`
- tasks_total: `20`
- tasks_with_scores: `20`
- full_coverage_tasks: `20`
- assigned_tasks: `15`
- multi_assignments: `27`
- occupied_cluster_count: `7`
- mean_assignment_margin_pp: `27.33`
- low_margin_task_fraction: `0.5333`

## Cluster Occupancy

| schema_id | primary_assigned | multi_assigned | training_evidence | mean_assigned_score | observed_task_count | floor_k | below_training_floor |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| artifact-generation | 1 | 1 | 2 | 68.42 | 20 | 2 | no |
| analytic-pipeline | 3 | 5 | 5 | 86.67 | 20 | 2 | no |
| engineering-composition | 2 | 4 | 4 | 45.62 | 20 | 2 | no |
| retrieval-heavy-synthesis | 2 | 4 | 4 | 55.62 | 20 | 2 | no |
| environment-control | 3 | 5 | 5 | 100.00 | 20 | 2 | no |
| methodology-guardrail | 2 | 4 | 4 | 65.62 | 20 | 2 | no |
| orchestration-delegation | 2 | 4 | 4 | 100.00 | 20 | 2 | no |

## Schema Training Assignments

| schema_id | task | role | reasons | score | dR0 | trajectory | rank | primary_assigned |
| --- | --- | --- | --- | ---: | ---: | --- | ---: | --- |
| artifact-generation | civ6-adjacency-optimizer | primary_assignment | primary;near_best | 68.42 | 60.00 | stable_no_loss_gain | 1 | artifact-generation |
| artifact-generation | court-form-filling | floor_top_score | - | 31.25 | - | - | 4 | analytic-pipeline |
| analytic-pipeline | court-form-filling | primary_assignment | primary;near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | analytic-pipeline |
| analytic-pipeline | earthquake-phase-association | primary_assignment | primary;near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | analytic-pipeline |
| analytic-pipeline | azure-bgp-oscillation-route-leak | primary_assignment | primary;near_best;stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 1 | analytic-pipeline |
| analytic-pipeline | exceltable-in-ppt | stable_gain_support | near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | environment-control |
| analytic-pipeline | civ6-adjacency-optimizer | stable_gain_support | stable_gain | 47.25 | 55.00 | stable_non_decreasing_gain | 2 | artifact-generation |
| engineering-composition | exoplanet-detection-period | primary_assignment | primary;near_best;stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 1 | engineering-composition |
| engineering-composition | find-topk-similiar-chemicals | primary_assignment | primary;near_best | 31.25 | 100.00 | partial_gain_then_regression | 1 | engineering-composition |
| engineering-composition | earthquake-phase-association | stable_gain_support | near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | analytic-pipeline |
| engineering-composition | civ6-adjacency-optimizer | stable_gain_support | stable_gain | 43.00 | 40.00 | stable_non_decreasing_gain | 3 | artifact-generation |
| retrieval-heavy-synthesis | energy-market-pricing | primary_assignment | primary;near_best;high_score;stable_gain | 80.00 | 100.00 | stable_non_decreasing_gain | 1 | retrieval-heavy-synthesis |
| retrieval-heavy-synthesis | adaptive-cruise-control | primary_assignment | primary;near_best | 31.25 | 100.00 | partial_gain_then_regression | 1 | retrieval-heavy-synthesis |
| retrieval-heavy-synthesis | dapt-intrusion-detection | stable_gain_support | near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | methodology-guardrail |
| retrieval-heavy-synthesis | court-form-filling | stable_gain_support | stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 3 | analytic-pipeline |
| environment-control | energy-ac-optimal-power-flow | primary_assignment | primary;near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | environment-control |
| environment-control | exceltable-in-ppt | primary_assignment | primary;near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | environment-control |
| environment-control | financial-modeling-qa | primary_assignment | primary;near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | environment-control |
| environment-control | energy-market-pricing | stable_gain_support | near_best;high_score;stable_gain | 80.00 | 100.00 | stable_non_decreasing_gain | 1 | retrieval-heavy-synthesis |
| environment-control | exoplanet-detection-period | stable_gain_support | near_best;stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 1 | engineering-composition |
| methodology-guardrail | dapt-intrusion-detection | primary_assignment | primary;near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | methodology-guardrail |
| methodology-guardrail | data-to-d3 | primary_assignment | primary;near_best | 31.25 | 100.00 | partial_gain_then_regression | 1 | methodology-guardrail |
| methodology-guardrail | court-form-filling | stable_gain_support | high_score;stable_gain | 80.00 | 100.00 | stable_non_decreasing_gain | 2 | analytic-pipeline |
| methodology-guardrail | azure-bgp-oscillation-route-leak | stable_gain_support | near_best;stable_gain | 60.00 | 100.00 | stable_non_decreasing_gain | 1 | analytic-pipeline |
| orchestration-delegation | earthquake-plate-calculation | primary_assignment | primary;near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | orchestration-delegation |
| orchestration-delegation | econ-detrending-correlation | primary_assignment | primary;near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | orchestration-delegation |
| orchestration-delegation | earthquake-phase-association | stable_gain_support | near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | analytic-pipeline |
| orchestration-delegation | exceltable-in-ppt | stable_gain_support | near_best;high_score;stable_gain;ideal_zero_to_full | 100.00 | 100.00 | ideal_zero_to_full_stable | 1 | environment-control |

## Assigned Tasks

| task | assigned | best | second | margin_pp | confidence | tie_break |
| --- | --- | ---: | ---: | ---: | --- | --- |
| adaptive-cruise-control | retrieval-heavy-synthesis | 31.25 | 31.25 | 0.00 | low | stable_random |
| azure-bgp-oscillation-route-leak | analytic-pipeline | 60.00 | 60.00 | 0.00 | low | semantic_prior |
| civ6-adjacency-optimizer | artifact-generation | 68.42 | 47.25 | 21.17 | high | no |
| court-form-filling | analytic-pipeline | 100.00 | 80.00 | 20.00 | high | no |
| dapt-intrusion-detection | methodology-guardrail | 100.00 | 100.00 | 0.00 | low | balance |
| data-to-d3 | methodology-guardrail | 31.25 | 0.00 | 31.25 | high | no |
| earthquake-phase-association | analytic-pipeline | 100.00 | 100.00 | 0.00 | low | semantic_prior |
| earthquake-plate-calculation | orchestration-delegation | 100.00 | 31.25 | 68.75 | high | no |
| econ-detrending-correlation | orchestration-delegation | 100.00 | 0.00 | 100.00 | high | no |
| energy-ac-optimal-power-flow | environment-control | 100.00 | 0.00 | 100.00 | high | no |
| energy-market-pricing | retrieval-heavy-synthesis | 80.00 | 80.00 | 0.00 | low | stable_random |
| exceltable-in-ppt | environment-control | 100.00 | 100.00 | 0.00 | low | balance |
| exoplanet-detection-period | engineering-composition | 60.00 | 60.00 | 0.00 | low | balance |
| financial-modeling-qa | environment-control | 100.00 | 31.25 | 68.75 | high | no |
| find-topk-similiar-chemicals | engineering-composition | 31.25 | 31.25 | 0.00 | low | semantic_prior |

## Unassigned Tasks

- `3d-scan-calc`: status=`unassigned_no_positive_signal`, observed=`7`, missing=``
- `citation-check`: status=`unassigned_no_positive_signal`, observed=`7`, missing=``
- `fix-build-agentops`: status=`unassigned_no_positive_signal`, observed=`7`, missing=``
- `fix-build-google-auto`: status=`unassigned_no_positive_signal`, observed=`7`, missing=``
- `fix-druid-loophole-cve`: status=`unassigned_no_positive_signal`, observed=`7`, missing=``

## Collapse Warnings

- `high_low_margin_fraction`: Low-margin fraction is 0.53.

## Low-Margin Tasks

- `adaptive-cruise-control`: assigned=`retrieval-heavy-synthesis`, margin_pp=`0.0`, tie_break=`stable_random`
- `azure-bgp-oscillation-route-leak`: assigned=`analytic-pipeline`, margin_pp=`0.0`, tie_break=`semantic_prior`
- `dapt-intrusion-detection`: assigned=`methodology-guardrail`, margin_pp=`0.0`, tie_break=`balance`
- `earthquake-phase-association`: assigned=`analytic-pipeline`, margin_pp=`0.0`, tie_break=`semantic_prior`
- `energy-market-pricing`: assigned=`retrieval-heavy-synthesis`, margin_pp=`0.0`, tie_break=`stable_random`
- `exceltable-in-ppt`: assigned=`environment-control`, margin_pp=`0.0`, tie_break=`balance`
- `exoplanet-detection-period`: assigned=`engineering-composition`, margin_pp=`0.0`, tie_break=`balance`
- `find-topk-similiar-chemicals`: assigned=`engineering-composition`, margin_pp=`0.0`, tie_break=`semantic_prior`

## Top-3 Near Ties

- `3d-scan-calc`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `citation-check`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `earthquake-phase-association`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `exceltable-in-ppt`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `find-topk-similiar-chemicals`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `fix-build-agentops`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `fix-build-google-auto`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `fix-druid-loophole-cve`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
