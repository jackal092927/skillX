# SkillX First20 Round0 Checkpoint: `first20-round0-rate-limit-rerun-3batch-final-2026-04-29`

## Scope

- base_run_label: `run-first20x7-round0-2026-04-24`
- rerun_labels: `run-first20x7-rerun-failed5-2026-04-25-v2, run-first20-rate-limit-rerun-2026-04-27-3batch-b01, run-first20-rate-limit-rerun-2026-04-27-3batch-b02, run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- tasks: `20`
- schemas: `7`
- effective_pairs: `140`
- launcher_succeeded_pairs: `140`
- launcher_failed_pairs: `0`
- all_tasks_have_7_succeeded_pairs: `True`
- generated_at: `2026-04-29T05:00:02.401175+00:00`

## Rerun Overlay

- base_failed_pairs: `5`
- rerun_replaced_pairs: `120`
- final_failed_pairs: `0`

## Classification Summary

| Classification | Count |
| --- | ---: |
| clean_success | 79 |
| runtime_failure | 1 |
| scientific_failure | 60 |

## Schema Summary

| Schema | Pairs | Mean Score | Clean Success | Scientific Failure | Runtime Failure | Contract Failure |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| analytic-pipeline | 20 | 47.75 | 10 | 10 | 0 | 0 |
| artifact-generation | 20 | 48 | 10 | 10 | 0 | 0 |
| engineering-composition | 20 | 47 | 10 | 10 | 0 | 0 |
| environment-control | 20 | 53 | 11 | 8 | 1 | 0 |
| methodology-guardrail | 20 | 58 | 12 | 8 | 0 | 0 |
| orchestration-delegation | 20 | 68 | 14 | 6 | 0 | 0 |
| retrieval-heavy-synthesis | 20 | 57.25 | 12 | 8 | 0 | 0 |

## Task Summary

| Task | Pairs | C0 | C1 | Best Score | Best Schemas | dC0 | dC1 |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 3d-scan-calc | 7/7 | 80 | 80 | 100 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 20 | 20 |
| adaptive-cruise-control | 7/7 | 0 | 0 | 100 | orchestration-delegation, retrieval-heavy-synthesis | 100 | 100 |
| azure-bgp-oscillation-route-leak | 7/7 | 0 | 0 | 100 | analytic-pipeline, methodology-guardrail, orchestration-delegation | 100 | 100 |
| citation-check | 7/7 | 100 | 100 | 100 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | 0 |
| civ6-adjacency-optimizer | 7/7 | 0 | 14.7 | 60 | artifact-generation, environment-control, methodology-guardrail, orchestration-delegation | 60 | 45.3 |
| court-form-filling | 7/7 | 20 | 20 | 100 | analytic-pipeline, artifact-generation, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 80 | 80 |
| dapt-intrusion-detection | 7/7 | 0 | 80 | 100 | artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 100 | 20 |
| data-to-d3 | 7/7 | 60 | 80 | 100 | methodology-guardrail, orchestration-delegation | 40 | 20 |
| earthquake-phase-association | 7/7 | 20 | 20 | 100 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 80 | 80 |
| earthquake-plate-calculation | 7/7 | 0 | 60 | 100 | artifact-generation, orchestration-delegation | 100 | 40 |
| econ-detrending-correlation | 7/7 | 40 | 60 | 100 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 60 | 40 |
| energy-ac-optimal-power-flow | 7/7 | 20 | 20 | 100 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 80 | 80 |
| energy-market-pricing | 7/7 | 0 | 0 | 100 | environment-control, methodology-guardrail, retrieval-heavy-synthesis | 100 | 100 |
| exceltable-in-ppt | 7/7 | 60 | 80 | 100 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, orchestration-delegation, retrieval-heavy-synthesis | 40 | 20 |
| exoplanet-detection-period | 7/7 | 0 | 0 | 100 | engineering-composition, environment-control, retrieval-heavy-synthesis | 100 | 100 |
| financial-modeling-qa | 7/7 | 0 | 0 | 100 | environment-control, methodology-guardrail | 100 | 100 |
| find-topk-similiar-chemicals | 7/7 | 20 | 10 | 100 | analytic-pipeline, engineering-composition, orchestration-delegation | 80 | 90 |
| fix-build-agentops | 7/7 | 0 | 0 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | 0 |
| fix-build-google-auto | 7/7 | 0 | 0 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | 0 |
| fix-druid-loophole-cve | 7/7 | 20 | 80 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | -20 | -80 |

## Scientific Failures

- `adaptive-cruise-control__analytic-pipeline`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b01`
- `adaptive-cruise-control__artifact-generation`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b01`
- `adaptive-cruise-control__engineering-composition`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b01`
- `adaptive-cruise-control__environment-control`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b01`
- `adaptive-cruise-control__methodology-guardrail`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b01`
- `azure-bgp-oscillation-route-leak__artifact-generation`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b02`
- `azure-bgp-oscillation-route-leak__engineering-composition`: selected `R0` score `0` from `run-first20x7-rerun-failed5-2026-04-25-v2`
- `azure-bgp-oscillation-route-leak__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `azure-bgp-oscillation-route-leak__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-rerun-failed5-2026-04-25-v2`
- `court-form-filling__engineering-composition`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b01`
- `court-form-filling__environment-control`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b01`
- `dapt-intrusion-detection__analytic-pipeline`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b01`
- `data-to-d3__analytic-pipeline`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b01`
- `data-to-d3__artifact-generation`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b01`
- `data-to-d3__engineering-composition`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b01`
- `data-to-d3__environment-control`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b01`
- `data-to-d3__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b01`
- `earthquake-plate-calculation__analytic-pipeline`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b02`
- `earthquake-plate-calculation__engineering-composition`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b02`
- `earthquake-plate-calculation__environment-control`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b02`
- `earthquake-plate-calculation__methodology-guardrail`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b02`
- `earthquake-plate-calculation__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b02`
- `energy-market-pricing__analytic-pipeline`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b02`
- `energy-market-pricing__artifact-generation`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b02`
- `energy-market-pricing__engineering-composition`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b02`
- `energy-market-pricing__orchestration-delegation`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b02`
- `exceltable-in-ppt__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `exoplanet-detection-period__analytic-pipeline`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `exoplanet-detection-period__artifact-generation`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `exoplanet-detection-period__methodology-guardrail`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `exoplanet-detection-period__orchestration-delegation`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `financial-modeling-qa__analytic-pipeline`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `financial-modeling-qa__artifact-generation`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `financial-modeling-qa__engineering-composition`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `financial-modeling-qa__orchestration-delegation`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `financial-modeling-qa__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `find-topk-similiar-chemicals__artifact-generation`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `find-topk-similiar-chemicals__environment-control`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `find-topk-similiar-chemicals__methodology-guardrail`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `find-topk-similiar-chemicals__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `fix-build-agentops__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-agentops__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-agentops__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-agentops__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-agentops__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-agentops__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-agentops__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-google-auto__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-google-auto__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-google-auto__engineering-composition`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `fix-build-google-auto__methodology-guardrail`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `fix-build-google-auto__orchestration-delegation`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `fix-build-google-auto__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `fix-druid-loophole-cve__analytic-pipeline`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `fix-druid-loophole-cve__artifact-generation`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `fix-druid-loophole-cve__engineering-composition`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `fix-druid-loophole-cve__environment-control`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `fix-druid-loophole-cve__methodology-guardrail`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `fix-druid-loophole-cve__orchestration-delegation`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`
- `fix-druid-loophole-cve__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20-rate-limit-rerun-2026-04-27-3batch-b03`

## Next Step

- Use `final_pair_results.csv` / `score_matrix_wide.csv` as the effective round-0 input for assignment, diagnostics, and outer-loop schema update.
- Treat `scientific_failure` rows as measured low-score evidence, not infrastructure failures.
