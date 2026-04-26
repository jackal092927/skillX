# SkillX First20 Round0 Checkpoint: `first20-round0-effective-2026-04-26`

## Scope

- base_run_label: `run-first20x7-round0-2026-04-24`
- rerun_labels: `run-first20x7-rerun-failed5-2026-04-25-v2`
- tasks: `20`
- schemas: `7`
- effective_pairs: `140`
- launcher_succeeded_pairs: `140`
- launcher_failed_pairs: `0`
- all_tasks_have_7_succeeded_pairs: `True`
- generated_at: `2026-04-26T04:41:27.108920+00:00`

## Rerun Overlay

- base_failed_pairs: `5`
- rerun_replaced_pairs: `5`
- final_failed_pairs: `0`

## Classification Summary

| Classification | Count |
| --- | ---: |
| clean_success | 20 |
| scientific_failure | 120 |

## Schema Summary

| Schema | Pairs | Mean Score | Clean Success | Scientific Failure | Runtime Failure | Contract Failure |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| analytic-pipeline | 20 | 15 | 3 | 17 | 0 | 0 |
| artifact-generation | 20 | 20 | 4 | 16 | 0 | 0 |
| engineering-composition | 20 | 15 | 3 | 17 | 0 | 0 |
| environment-control | 20 | 10 | 2 | 18 | 0 | 0 |
| methodology-guardrail | 20 | 15 | 3 | 17 | 0 | 0 |
| orchestration-delegation | 20 | 15 | 3 | 17 | 0 | 0 |
| retrieval-heavy-synthesis | 20 | 10 | 2 | 18 | 0 | 0 |

## Task Summary

| Task | Pairs | C0 | C1 | Best Score | Best Schemas | dC0 | dC1 |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 3d-scan-calc | 7/7 | 80 | 80 | 100 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 20 | 20 |
| adaptive-cruise-control | 7/7 | 0 | 0 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | 0 |
| azure-bgp-oscillation-route-leak | 7/7 | 0 | 0 | 100 | analytic-pipeline, methodology-guardrail, orchestration-delegation | 100 | 100 |
| citation-check | 7/7 | 100 | 100 | 100 | analytic-pipeline, artifact-generation, engineering-composition | 0 | 0 |
| civ6-adjacency-optimizer | 7/7 | 0 | 14.7 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | -14.7 |
| court-form-filling | 7/7 | 20 | 20 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | -20 | -20 |
| dapt-intrusion-detection | 7/7 | 0 | 80 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | -80 |
| data-to-d3 | 7/7 | 60 | 80 | 100 | engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 40 | 20 |
| earthquake-phase-association | 7/7 | 20 | 20 | 100 | artifact-generation | 80 | 80 |
| earthquake-plate-calculation | 7/7 | 0 | 60 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | -60 |
| econ-detrending-correlation | 7/7 | 40 | 60 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | -40 | -60 |
| energy-ac-optimal-power-flow | 7/7 | 20 | 20 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | -20 | -20 |
| energy-market-pricing | 7/7 | 0 | 0 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | 0 |
| exceltable-in-ppt | 7/7 | 60 | 80 | 100 | artifact-generation | 40 | 20 |
| exoplanet-detection-period | 7/7 | 0 | 0 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | 0 |
| financial-modeling-qa | 7/7 | 0 | 0 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | 0 |
| find-topk-similiar-chemicals | 7/7 | 20 | 10 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | -20 | -10 |
| fix-build-agentops | 7/7 | 0 | 0 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | 0 |
| fix-build-google-auto | 7/7 | 0 | 0 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | 0 | 0 |
| fix-druid-loophole-cve | 7/7 | 20 | 80 | 0 | analytic-pipeline, artifact-generation, engineering-composition, environment-control, methodology-guardrail, orchestration-delegation, retrieval-heavy-synthesis | -20 | -80 |

## Scientific Failures

- `adaptive-cruise-control__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `adaptive-cruise-control__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `adaptive-cruise-control__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `adaptive-cruise-control__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `adaptive-cruise-control__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `adaptive-cruise-control__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `adaptive-cruise-control__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `azure-bgp-oscillation-route-leak__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `azure-bgp-oscillation-route-leak__engineering-composition`: selected `R0` score `0` from `run-first20x7-rerun-failed5-2026-04-25-v2`
- `azure-bgp-oscillation-route-leak__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `azure-bgp-oscillation-route-leak__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-rerun-failed5-2026-04-25-v2`
- `citation-check__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `citation-check__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `citation-check__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `citation-check__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `civ6-adjacency-optimizer__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `civ6-adjacency-optimizer__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `civ6-adjacency-optimizer__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `civ6-adjacency-optimizer__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `civ6-adjacency-optimizer__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `civ6-adjacency-optimizer__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `civ6-adjacency-optimizer__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `court-form-filling__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `court-form-filling__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `court-form-filling__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `court-form-filling__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `court-form-filling__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `court-form-filling__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `court-form-filling__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `dapt-intrusion-detection__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `dapt-intrusion-detection__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `dapt-intrusion-detection__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `dapt-intrusion-detection__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `dapt-intrusion-detection__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `dapt-intrusion-detection__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `dapt-intrusion-detection__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `data-to-d3__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `data-to-d3__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `earthquake-phase-association__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `earthquake-phase-association__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `earthquake-phase-association__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `earthquake-phase-association__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `earthquake-phase-association__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `earthquake-phase-association__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `earthquake-plate-calculation__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `earthquake-plate-calculation__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `earthquake-plate-calculation__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `earthquake-plate-calculation__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `earthquake-plate-calculation__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `earthquake-plate-calculation__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `earthquake-plate-calculation__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `econ-detrending-correlation__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `econ-detrending-correlation__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `econ-detrending-correlation__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `econ-detrending-correlation__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `econ-detrending-correlation__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `econ-detrending-correlation__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `econ-detrending-correlation__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `energy-ac-optimal-power-flow__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `energy-ac-optimal-power-flow__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `energy-ac-optimal-power-flow__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `energy-ac-optimal-power-flow__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `energy-ac-optimal-power-flow__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `energy-ac-optimal-power-flow__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `energy-ac-optimal-power-flow__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `energy-market-pricing__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `energy-market-pricing__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `energy-market-pricing__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `energy-market-pricing__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `energy-market-pricing__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `energy-market-pricing__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `energy-market-pricing__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `exceltable-in-ppt__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `exceltable-in-ppt__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `exceltable-in-ppt__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `exceltable-in-ppt__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `exceltable-in-ppt__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `exceltable-in-ppt__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `exoplanet-detection-period__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `exoplanet-detection-period__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `exoplanet-detection-period__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `exoplanet-detection-period__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `exoplanet-detection-period__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `exoplanet-detection-period__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `exoplanet-detection-period__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `financial-modeling-qa__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `financial-modeling-qa__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `financial-modeling-qa__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `financial-modeling-qa__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `financial-modeling-qa__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `financial-modeling-qa__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `financial-modeling-qa__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `find-topk-similiar-chemicals__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `find-topk-similiar-chemicals__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `find-topk-similiar-chemicals__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `find-topk-similiar-chemicals__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `find-topk-similiar-chemicals__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `find-topk-similiar-chemicals__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `find-topk-similiar-chemicals__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-agentops__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-agentops__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-agentops__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-agentops__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-agentops__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-agentops__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-agentops__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-google-auto__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-google-auto__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-google-auto__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-google-auto__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-google-auto__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-google-auto__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-build-google-auto__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-druid-loophole-cve__analytic-pipeline`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-druid-loophole-cve__artifact-generation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-druid-loophole-cve__engineering-composition`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-druid-loophole-cve__environment-control`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-druid-loophole-cve__methodology-guardrail`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-druid-loophole-cve__orchestration-delegation`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`
- `fix-druid-loophole-cve__retrieval-heavy-synthesis`: selected `R0` score `0` from `run-first20x7-round0-2026-04-24`

## Next Step

- Use `final_pair_results.csv` / `score_matrix_wide.csv` as the effective round-0 input for assignment, diagnostics, and outer-loop schema update.
- Treat `scientific_failure` rows as measured low-score evidence, not infrastructure failures.
