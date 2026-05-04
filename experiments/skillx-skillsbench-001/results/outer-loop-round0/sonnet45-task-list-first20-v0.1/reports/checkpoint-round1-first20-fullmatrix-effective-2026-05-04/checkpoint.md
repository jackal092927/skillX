# SkillX First20 Round0 Checkpoint: `checkpoint-round1-first20-fullmatrix-effective-2026-05-04`

## Scope

- base_run_label: `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- rerun_labels: `run-round1-first20-fullmatrix-infra-rerun-2026-05-04, run-round1-first20-fullmatrix-adaptive-rhs-rerun-2026-05-04`
- tasks: `20`
- schemas: `7`
- effective_pairs: `140`
- launcher_succeeded_pairs: `140`
- launcher_failed_pairs: `0`
- all_tasks_have_7_succeeded_pairs: `True`
- generated_at: `2026-05-04T17:57:41.434143+00:00`

## Rerun Overlay

- base_failed_pairs: `1`
- rerun_replaced_pairs: `3`
- final_failed_pairs: `0`

## Classification Summary

| Classification | Count |
| --- | ---: |
| clean_success | 66 |
| scientific_failure | 74 |

## Schema Summary

| Schema | Pairs | Mean Score | Clean Success | Scientific Failure | Runtime Failure | Contract Failure |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| analytic-pipeline | 20 | 33.5 | 7 | 13 | 0 | 0 |
| artifact-generation | 20 | 48 | 10 | 10 | 0 | 0 |
| engineering-composition | 20 | 48 | 10 | 10 | 0 | 0 |
| environment-control | 20 | 48 | 10 | 10 | 0 | 0 |
| methodology-guardrail | 20 | 53 | 11 | 9 | 0 | 0 |
| orchestration-delegation | 20 | 38 | 8 | 12 | 0 | 0 |
| retrieval-heavy-synthesis | 20 | 47.75 | 10 | 10 | 0 | 0 |

## Task Summary

| Task | Pairs | C0 | C1 | Best Score | Best Schemas | dC0 | dC1 |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 3d-scan-calc | 7/7 | 80 | 80 | 100 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 20 | 20 |
| adaptive-cruise-control | 7/7 | 0 | 0 | 100 | engineering-composition, orchestration-delegation | 100 | 100 |
| azure-bgp-oscillation-route-leak | 7/7 | 0 | 0 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | 0 |
| citation-check | 7/7 | 100 | 100 | 100 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | 0 |
| civ6-adjacency-optimizer | 7/7 | 0 | 14.7 | 70 | analytic-pipeline | 70 | 55.3 |
| court-form-filling | 7/7 | 20 | 20 | 100 | analytic-pipeline, artifact-generation, engineering-composition, methodology-guardrail | 80 | 80 |
| dapt-intrusion-detection | 7/7 | 0 | 80 | 100 | analytic-pipeline, methodology-guardrail, retrieval-heavy-synthesis | 100 | 20 |
| data-to-d3 | 7/7 | 60 | 80 | 100 | artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 40 | 20 |
| earthquake-phase-association | 7/7 | 20 | 20 | 100 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 80 | 80 |
| earthquake-plate-calculation | 7/7 | 0 | 60 | 100 | artifact-generation, methodology-guardrail | 100 | 40 |
| econ-detrending-correlation | 7/7 | 40 | 60 | 100 | artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 60 | 40 |
| energy-ac-optimal-power-flow | 7/7 | 20 | 20 | 100 | analytic-pipeline, engineering-composition, methodology-guardrail, retrieval-heavy-synthesis | 80 | 80 |
| energy-market-pricing | 7/7 | 0 | 0 | 100 | engineering-composition, environment-control, retrieval-heavy-synthesis | 100 | 100 |
| exceltable-in-ppt | 7/7 | 60 | 80 | 100 | artifact-generation, environment-control, orchestration-delegation | 40 | 20 |
| exoplanet-detection-period | 7/7 | 0 | 0 | 100 | methodology-guardrail | 100 | 100 |
| financial-modeling-qa | 7/7 | 0 | 0 | 100 | artifact-generation, environment-control, retrieval-heavy-synthesis | 100 | 100 |
| find-topk-similiar-chemicals | 7/7 | 20 | 10 | 100 | environment-control | 80 | 90 |
| fix-build-agentops | 7/7 | 0 | 0 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | 0 |
| fix-build-google-auto | 7/7 | 0 | 0 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | 0 |
| fix-druid-loophole-cve | 7/7 | 20 | 80 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | -20 | -80 |

## Scientific Failures

- `adaptive-cruise-control__analytic-pipeline`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `adaptive-cruise-control__artifact-generation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `adaptive-cruise-control__environment-control`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `adaptive-cruise-control__methodology-guardrail`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `adaptive-cruise-control__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-round1-first20-fullmatrix-adaptive-rhs-rerun-2026-05-04`
- `azure-bgp-oscillation-route-leak__analytic-pipeline`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `azure-bgp-oscillation-route-leak__artifact-generation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `azure-bgp-oscillation-route-leak__engineering-composition`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `azure-bgp-oscillation-route-leak__environment-control`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `azure-bgp-oscillation-route-leak__methodology-guardrail`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `azure-bgp-oscillation-route-leak__orchestration-delegation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `azure-bgp-oscillation-route-leak__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `court-form-filling__environment-control`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `court-form-filling__orchestration-delegation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `court-form-filling__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `dapt-intrusion-detection__artifact-generation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `dapt-intrusion-detection__engineering-composition`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `dapt-intrusion-detection__environment-control`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `dapt-intrusion-detection__orchestration-delegation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `data-to-d3__analytic-pipeline`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `earthquake-plate-calculation__analytic-pipeline`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `earthquake-plate-calculation__engineering-composition`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `earthquake-plate-calculation__environment-control`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `earthquake-plate-calculation__orchestration-delegation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `earthquake-plate-calculation__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `econ-detrending-correlation__analytic-pipeline`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `energy-ac-optimal-power-flow__artifact-generation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `energy-ac-optimal-power-flow__environment-control`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `energy-ac-optimal-power-flow__orchestration-delegation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `energy-market-pricing__analytic-pipeline`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `energy-market-pricing__artifact-generation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `energy-market-pricing__methodology-guardrail`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `energy-market-pricing__orchestration-delegation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `exceltable-in-ppt__analytic-pipeline`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `exceltable-in-ppt__engineering-composition`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `exceltable-in-ppt__methodology-guardrail`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `exceltable-in-ppt__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `exoplanet-detection-period__analytic-pipeline`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `exoplanet-detection-period__artifact-generation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `exoplanet-detection-period__engineering-composition`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `exoplanet-detection-period__environment-control`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `exoplanet-detection-period__orchestration-delegation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `exoplanet-detection-period__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `financial-modeling-qa__analytic-pipeline`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `financial-modeling-qa__engineering-composition`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `financial-modeling-qa__methodology-guardrail`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `financial-modeling-qa__orchestration-delegation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `find-topk-similiar-chemicals__analytic-pipeline`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `find-topk-similiar-chemicals__artifact-generation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `find-topk-similiar-chemicals__engineering-composition`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `find-topk-similiar-chemicals__methodology-guardrail`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `find-topk-similiar-chemicals__orchestration-delegation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `find-topk-similiar-chemicals__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-build-agentops__analytic-pipeline`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-build-agentops__artifact-generation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-build-agentops__engineering-composition`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-build-agentops__environment-control`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-build-agentops__methodology-guardrail`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-build-agentops__orchestration-delegation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-build-agentops__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-build-google-auto__analytic-pipeline`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-build-google-auto__artifact-generation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-build-google-auto__engineering-composition`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-build-google-auto__environment-control`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-build-google-auto__methodology-guardrail`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-build-google-auto__orchestration-delegation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-build-google-auto__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-druid-loophole-cve__analytic-pipeline`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-druid-loophole-cve__artifact-generation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-druid-loophole-cve__engineering-composition`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-druid-loophole-cve__environment-control`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-druid-loophole-cve__methodology-guardrail`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-druid-loophole-cve__orchestration-delegation`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`
- `fix-druid-loophole-cve__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-round1-first20-fullmatrix-fallback-2026-05-01-combined-b01-b03`

## Next Step

- Use `final_pair_results.csv` / `score_matrix_wide.csv` as the effective round-0 input for assignment, diagnostics, and outer-loop schema update.
- Treat `scientific_failure` rows as measured low-score evidence, not infrastructure failures.
