# SkillX Outer-Loop Effectiveness Scorecard: Round1 vs Round0

- previous_result: `first20-round0-rate-limit-rerun-3batch-final-2026-04-29`
- current_result: `outer-loop-round1-first20-fullmatrix-effective-2026-05-04`
- scope: same first20 x 7 full matrix, 140 task-schema pairs
- note: this is an offline analysis of existing artifacts; no new experiments were run

## Executive Read

- Full-matrix absolute performance declined: mean reported score went from 54.14 to 45.18, with 26 previously-100 pairs dropping to 0.
- Assignment-aware trajectory score was nearly flat/slightly positive: mean assignment score went from 17.67 to 18.05 across all 140 pairs.
- On the exact previous primary assignments, the result is negative: mean assignment score fell from 77.48 to 31.67, and mean reported score fell from 97.33 to 57.33.
- On the broader previous multi-assignment/training evidence sets, the result is also negative on average, though there are strong isolated wins.
- Assignment confidence improved mechanically: low-confidence assigned tasks dropped from 8 to 0, but this is not enough to claim outer-loop success because the target performance regressed.

## Scorecard Summary

| set | n | mean_prev_score | mean_cur_score | mean_delta_score | improved_score_count | worse_score_count | mean_prev_reported_score | mean_cur_reported_score | mean_delta_reported_score | reported_100_to_0 | mean_delta_trajectory_signal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_140_pairs | 140 | 17.67 | 18.05 | 0.38 | 29 | 34 | 54.14 | 45.18 | -8.96 | 26 | 0.93 |
| previous_primary_assignment | 15 | 77.48 | 31.67 | -45.81 | 1 | 13 | 97.33 | 57.33 | -40.0 | 6 | -43.0 |
| previous_multi_assignment | 27 | 77.5 | 25.34 | -52.15 | 1 | 25 | 94.63 | 58.89 | -35.74 | 10 | -57.78 |
| previous_schema_training_assignment | 28 | 75.85 | 25.55 | -50.29 | 1 | 25 | 94.82 | 60.36 | -34.46 | 10 | -55.71 |

## Assignment Confidence

| metric | previous | current | delta |
| --- | --- | --- | --- |
| assigned_tasks | 15 | 14 | -1.0 |
| unassigned_tasks | 5 | 6 | 1.0 |
| multi_assignment_count_total | 27 | 23 | -4.0 |
| low_confidence_assigned | 8 | 0 | -8.0 |
| medium_confidence_assigned | 0 | 2 | 2.0 |
| high_confidence_assigned | 7 | 12 | 5.0 |
| low_confidence_fraction_assigned | 53.33 | 0.0 | -53.33 |
| mean_margin_pp_assigned | 27.33 | 32.55 | 5.22 |
| median_margin_pp_assigned | 0.0 | 27.5 | 27.5 |

## Biggest Task-Level Winners By Assignment Score

| task_name | mean_prev_score | mean_cur_score | mean_delta_score | improved_score_count | worse_score_count | reported_100_to_0 |
| --- | --- | --- | --- | --- | --- | --- |
| data-to-d3 | 4.46 | 53.39 | 48.93 | 6 | 0 | 0 |
| econ-detrending-correlation | 14.29 | 46.61 | 32.32 | 5 | 1 | 1 |
| energy-ac-optimal-power-flow | 14.29 | 41.79 | 27.5 | 4 | 1 | 3 |
| adaptive-cruise-control | 8.93 | 18.75 | 9.82 | 1 | 1 | 1 |
| dapt-intrusion-detection | 28.57 | 33.21 | 4.64 | 1 | 2 | 4 |
| energy-market-pricing | 22.86 | 23.39 | 0.54 | 1 | 2 | 1 |

## Biggest Task-Level Regressions By Assignment Score

| task_name | mean_prev_score | mean_cur_score | mean_delta_score | improved_score_count | worse_score_count | reported_100_to_0 |
| --- | --- | --- | --- | --- | --- | --- |
| azure-bgp-oscillation-route-leak | 21.61 | 0.0 | -21.61 | 0 | 3 | 3 |
| exceltable-in-ppt | 42.86 | 23.21 | -19.64 | 1 | 3 | 3 |
| civ6-adjacency-optimizer | 26.64 | 7.74 | -18.9 | 1 | 5 | 0 |
| court-form-filling | 43.21 | 24.82 | -18.39 | 1 | 4 | 2 |
| earthquake-phase-association | 53.21 | 41.61 | -11.61 | 2 | 3 | 0 |
| exoplanet-detection-period | 21.61 | 11.43 | -10.18 | 1 | 3 | 3 |

## Schema-Level Delta By Assignment Score

| schema_id | mean_prev_score | mean_cur_score | mean_delta_score | improved_score_count | worse_score_count | reported_100_to_0 |
| --- | --- | --- | --- | --- | --- | --- |
| orchestration-delegation | 26.25 | 13.12 | -13.13 | 2 | 7 | 6 |
| environment-control | 22.71 | 14.25 | -8.46 | 3 | 6 | 3 |
| analytic-pipeline | 21.93 | 17.34 | -4.59 | 2 | 5 | 4 |
| retrieval-heavy-synthesis | 18.75 | 21.38 | 2.62 | 4 | 6 | 4 |
| methodology-guardrail | 15.8 | 20.25 | 4.45 | 6 | 5 | 3 |
| engineering-composition | 11.71 | 21.75 | 10.04 | 6 | 4 | 4 |
| artifact-generation | 6.55 | 18.25 | 11.7 | 6 | 1 | 2 |

## Protected Regression Examples

| pair_id | prev_score | cur_score | delta_score | prev_reported_score | cur_reported_score | delta_reported_score | prev_trajectory_quality | cur_trajectory_quality |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| earthquake-plate-calculation__orchestration-delegation | 100.0 | 0.0 | -100.0 | 100.0 | 0.0 | -100.0 | ideal_zero_to_full_stable | stable_no_loss |
| energy-ac-optimal-power-flow__environment-control | 100.0 | 0.0 | -100.0 | 100.0 | 0.0 | -100.0 | ideal_zero_to_full_stable | stable_no_loss |
| exceltable-in-ppt__analytic-pipeline | 100.0 | 0.0 | -100.0 | 100.0 | 0.0 | -100.0 | ideal_zero_to_full_stable | stable_no_loss |
| azure-bgp-oscillation-route-leak__analytic-pipeline | 60.0 | 0.0 | -60.0 | 100.0 | 0.0 | -100.0 | stable_non_decreasing_gain | stable_no_loss |
| azure-bgp-oscillation-route-leak__methodology-guardrail | 60.0 | 0.0 | -60.0 | 100.0 | 0.0 | -100.0 | stable_non_decreasing_gain | stable_no_loss |
| court-form-filling__retrieval-heavy-synthesis | 60.0 | 0.0 | -60.0 | 100.0 | 0.0 | -100.0 | stable_non_decreasing_gain | stable_no_loss |
| exoplanet-detection-period__engineering-composition | 60.0 | 0.0 | -60.0 | 100.0 | 0.0 | -100.0 | stable_non_decreasing_gain | stable_no_loss |
| exoplanet-detection-period__environment-control | 60.0 | 0.0 | -60.0 | 100.0 | 0.0 | -100.0 | stable_non_decreasing_gain | stable_no_loss |
| adaptive-cruise-control__retrieval-heavy-synthesis | 31.25 | 0.0 | -31.25 | 100.0 | 0.0 | -100.0 | partial_gain_then_regression | stable_no_loss |
| azure-bgp-oscillation-route-leak__orchestration-delegation | 31.25 | 0.0 | -31.25 | 100.0 | 0.0 | -100.0 | partial_gain_then_regression | stable_no_loss |
| court-form-filling__orchestration-delegation | 31.25 | 0.0 | -31.25 | 100.0 | 0.0 | -100.0 | partial_gain_then_regression | stable_no_loss |
| exoplanet-detection-period__retrieval-heavy-synthesis | 31.25 | 0.0 | -31.25 | 100.0 | 0.0 | -100.0 | partial_gain_then_regression | stable_no_loss |
| financial-modeling-qa__methodology-guardrail | 31.25 | 0.0 | -31.25 | 100.0 | 0.0 | -100.0 | partial_gain_then_regression | stable_no_loss |
| find-topk-similiar-chemicals__analytic-pipeline | 31.25 | 0.0 | -31.25 | 100.0 | 0.0 | -100.0 | partial_gain_then_regression | stable_no_loss |
| find-topk-similiar-chemicals__engineering-composition | 31.25 | 0.0 | -31.25 | 100.0 | 0.0 | -100.0 | partial_gain_then_regression | stable_no_loss |
| find-topk-similiar-chemicals__orchestration-delegation | 31.25 | 0.0 | -31.25 | 100.0 | 0.0 | -100.0 | partial_gain_then_regression | stable_no_loss |
| dapt-intrusion-detection__artifact-generation | 0.0 | 0.0 | 0.0 | 100.0 | 0.0 | -100.0 | baseline_only | stable_no_loss |
| dapt-intrusion-detection__engineering-composition | 0.0 | 0.0 | 0.0 | 100.0 | 0.0 | -100.0 | baseline_only | stable_no_loss |
| dapt-intrusion-detection__environment-control | 0.0 | 0.0 | 0.0 | 100.0 | 0.0 | -100.0 | baseline_only | stable_no_loss |
| dapt-intrusion-detection__orchestration-delegation | 0.0 | 0.0 | 0.0 | 100.0 | 0.0 | -100.0 | baseline_only | stable_no_loss |

## Strong Improvement Examples

| pair_id | prev_score | cur_score | delta_score | prev_reported_score | cur_reported_score | delta_reported_score | prev_trajectory_quality | cur_trajectory_quality |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| adaptive-cruise-control__engineering-composition | 0.0 | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 | stable_no_loss | ideal_zero_to_full_stable |
| dapt-intrusion-detection__analytic-pipeline | 0.0 | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 | stable_no_loss | ideal_zero_to_full_stable |
| data-to-d3__orchestration-delegation | 0.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 | regression_or_mixed | ideal_zero_to_full_stable |
| energy-ac-optimal-power-flow__engineering-composition | 0.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 | baseline_only | ideal_zero_to_full_stable |
| exceltable-in-ppt__artifact-generation | 0.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 | baseline_only | ideal_zero_to_full_stable |
| data-to-d3__engineering-composition | 0.0 | 80.0 | 80.0 | 0.0 | 100.0 | 100.0 | stable_no_loss | stable_non_decreasing_gain |
| exoplanet-detection-period__methodology-guardrail | 0.0 | 80.0 | 80.0 | 0.0 | 100.0 | 100.0 | stable_no_loss | stable_non_decreasing_gain |
| earthquake-phase-association__artifact-generation | 0.0 | 80.0 | 80.0 | 100.0 | 100.0 | 0.0 | stable_no_loss | stable_non_decreasing_gain |
| econ-detrending-correlation__environment-control | 0.0 | 80.0 | 80.0 | 100.0 | 100.0 | 0.0 | baseline_only | stable_non_decreasing_gain |
| econ-detrending-correlation__engineering-composition | 0.0 | 72.5 | 72.5 | 100.0 | 100.0 | 0.0 | baseline_only | stable_no_loss_gain |
| energy-ac-optimal-power-flow__analytic-pipeline | 0.0 | 72.5 | 72.5 | 100.0 | 100.0 | 0.0 | baseline_only | stable_no_loss_gain |
| financial-modeling-qa__retrieval-heavy-synthesis | 0.0 | 60.0 | 60.0 | 0.0 | 100.0 | 100.0 | stable_no_loss | stable_non_decreasing_gain |
| energy-ac-optimal-power-flow__methodology-guardrail | 0.0 | 60.0 | 60.0 | 100.0 | 100.0 | 0.0 | baseline_only | stable_non_decreasing_gain |
| energy-ac-optimal-power-flow__retrieval-heavy-synthesis | 0.0 | 60.0 | 60.0 | 100.0 | 100.0 | 0.0 | baseline_only | stable_non_decreasing_gain |
| court-form-filling__engineering-composition | 0.0 | 51.25 | 51.25 | 0.0 | 100.0 | 100.0 | stable_no_loss | partial_gain_then_regression |
| data-to-d3__environment-control | 0.0 | 51.25 | 51.25 | 0.0 | 100.0 | 100.0 | stable_no_loss | partial_gain_then_regression |
| data-to-d3__retrieval-heavy-synthesis | 0.0 | 51.25 | 51.25 | 0.0 | 100.0 | 100.0 | stable_no_loss | partial_gain_then_regression |
| earthquake-phase-association__methodology-guardrail | 0.0 | 51.25 | 51.25 | 100.0 | 100.0 | 0.0 | baseline_only | partial_gain_then_regression |
| econ-detrending-correlation__retrieval-heavy-synthesis | 0.0 | 51.25 | 51.25 | 100.0 | 100.0 | 0.0 | baseline_only | partial_gain_then_regression |
| civ6-adjacency-optimizer__orchestration-delegation | 0.0 | 39.9167 | 39.9167 | 60.0 | 60.0 | 0.0 | regression_or_mixed | partial_gain_then_regression |

## Interpretation

1. The current outer-loop rewrite should not be reported as an overall win. It produced a small aggregate gain in the trajectory-weighted assignment score, but it regressed the previous target assignments and reduced clean-success coverage.
2. The promising signal is concentrated rather than global. `data-to-d3`, `energy-ac-optimal-power-flow`, and `econ-detrending-correlation` gained meaningful trajectory score; several prior winners regressed sharply.
3. The next outer-loop scoring/reporting should treat previously successful target pairs as protected positives. A schema rewrite that creates new lift but turns many previous 100s into 0s should be penalized heavily.
4. Assignment confidence improved, but this is only useful if targeted lift also improves. Here confidence rose while previous target performance dropped, so confidence alone is not a success metric.

## Suggested Metric For The Paper/Discussion

Use a four-part scorecard rather than full-matrix mean alone:

```text
outer_loop_effectiveness =
  targeted_lift_on_previous_training_assignments
+ new_signal_gain_on_full_matrix
+ assignment_confidence_gain
- protected_regression_penalty
```

For this run, `new_signal_gain` is mildly positive, but `targeted_lift` and `protected_regression_penalty` are negative enough that the overall verdict is mixed-to-negative.
