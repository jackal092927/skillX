# SkillX Round0 Outer-Loop Control Plane: `outer-loop-round0`

- generated_at: `2026-04-20T00:01:16.615692+00:00`
- output_dir: `experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/outer-loop-control-plane`
- schemas: `artifact-generation, analytic-pipeline, engineering-composition, retrieval-heavy-synthesis, environment-control, methodology-guardrail, orchestration-delegation`
- tasks_total: `87`
- tasks_with_scores: `9`
- full_coverage_tasks: `6`
- assigned_tasks: `6`
- occupied_cluster_count: `1`
- mean_assignment_margin_pp: `0.0`
- low_margin_task_fraction: `1.0`

## Cluster Occupancy

| schema_id | assigned_count | mean_assigned_score | observed_task_count | update_floor_k | below_floor |
| --- | ---: | ---: | ---: | ---: | --- |
| artifact-generation | 0 | - | 8 | 2 | yes |
| analytic-pipeline | 6 | 76.67 | 9 | 2 | no |
| engineering-composition | 0 | - | 9 | 2 | yes |
| retrieval-heavy-synthesis | 0 | - | 8 | 2 | yes |
| environment-control | 0 | - | 7 | 2 | yes |
| methodology-guardrail | 0 | - | 7 | 2 | yes |
| orchestration-delegation | 0 | - | 7 | 2 | yes |

## Assigned Tasks

| task | assigned | best | second | margin_pp | confidence | tie_break |
| --- | --- | ---: | ---: | ---: | --- | --- |
| citation-check | analytic-pipeline | 100.00 | 100.00 | 0.00 | low | deterministic_fallback |
| civ6-adjacency-optimizer | analytic-pipeline | 60.00 | 60.00 | 0.00 | low | deterministic_fallback |
| court-form-filling | analytic-pipeline | 100.00 | 100.00 | 0.00 | low | deterministic_fallback |
| earthquake-phase-association | analytic-pipeline | 0.00 | 0.00 | 0.00 | low | deterministic_fallback |
| pdf-excel-diff | analytic-pipeline | 100.00 | 100.00 | 0.00 | low | deterministic_fallback |
| powerlifting-coef-calc | analytic-pipeline | 100.00 | 100.00 | 0.00 | low | deterministic_fallback |

## Unassigned Tasks

- `3d-scan-calc`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `adaptive-cruise-control`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `azure-bgp-oscillation-route-leak`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `crystallographic-wyckoff-position-analysis`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `dapt-intrusion-detection`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `data-to-d3`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `dialogue-parser`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `dynamic-object-aware-egomotion`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `earthquake-plate-calculation`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `econ-detrending-correlation`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `energy-ac-optimal-power-flow`: status=`unassigned_incomplete_row`, observed=`6`, missing=`artifact-generation`
- `energy-market-pricing`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `enterprise-information-search`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `exceltable-in-ppt`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `exoplanet-detection-period`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `financial-modeling-qa`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `find-topk-similiar-chemicals`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `fix-build-agentops`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `fix-build-google-auto`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `fix-druid-loophole-cve`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `fix-erlang-ssh-cve`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `fix-visual-stability`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `flink-query`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `flood-risk-analysis`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `gh-repo-analytics`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `glm-lake-mendota`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `gravitational-wave-detection`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `grid-dispatch-operator`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `hvac-control`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `invoice-fraud-detection`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `jax-computing-basics`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `jpg-ocr-stat`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `lab-unit-harmonization`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `lake-warming-attribution`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `latex-formula-extraction`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `lean4-proof`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `manufacturing-codebook-normalization`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `manufacturing-equipment-maintenance`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `manufacturing-fjsp-optimization`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `mario-coin-counting`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `mars-clouds-clustering`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `mhc-layer-impl`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `multilingual-video-dubbing`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `offer-letter-generator`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `organize-messy-files`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `paper-anonymizer`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `parallel-tfidf-search`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `pddl-tpp-planning`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `pedestrian-traffic-counting`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `pg-essay-to-audiobook`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `pptx-reference-formatting`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `protein-expression-analysis`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `python-scala-translation`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `quantum-numerical-simulation`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `r2r-mpc-control`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `react-performance-debugging`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `reserves-at-risk-calc`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `sales-pivot-analysis`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `scheduling-email-assistant`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `sec-financial-report`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `seismic-phase-picking`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `setup-fuzzing-py`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `shock-analysis-demand`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `shock-analysis-supply`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `simpo-code-reproduction`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `software-dependency-audit`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `speaker-diarization-subtitles`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `spring-boot-jakarta-migration`: status=`unassigned_incomplete_row`, observed=`4`, missing=`environment-control;methodology-guardrail;orchestration-delegation`
- `suricata-custom-exfil`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `syzkaller-ppdev-syzlang`: status=`unassigned_incomplete_row`, observed=`3`, missing=`retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `taxonomy-tree-merge`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `threejs-structure-parser`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `threejs-to-obj`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `travel-planning`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `trend-anomaly-causal-inference`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `video-filler-word-remover`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `video-silence-remover`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `video-tutorial-indexer`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `virtualhome-agent-planning`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `weighted-gdp-calc`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`
- `xlsx-recover-data`: status=`unassigned_no_scores`, observed=`0`, missing=`artifact-generation;analytic-pipeline;engineering-composition;retrieval-heavy-synthesis;environment-control;methodology-guardrail;orchestration-delegation`

## Collapse Warnings

- `low_occupied_cluster_count`: Only 1 schemas are occupied by primary assignment.
- `dominant_schema`: Largest cluster share is 1.00.
- `high_low_margin_fraction`: Low-margin fraction is 1.00.

## Low-Margin Tasks

- `citation-check`: assigned=`analytic-pipeline`, margin_pp=`0.0`, tie_break=`deterministic_fallback`
- `civ6-adjacency-optimizer`: assigned=`analytic-pipeline`, margin_pp=`0.0`, tie_break=`deterministic_fallback`
- `court-form-filling`: assigned=`analytic-pipeline`, margin_pp=`0.0`, tie_break=`deterministic_fallback`
- `earthquake-phase-association`: assigned=`analytic-pipeline`, margin_pp=`0.0`, tie_break=`deterministic_fallback`
- `pdf-excel-diff`: assigned=`analytic-pipeline`, margin_pp=`0.0`, tie_break=`deterministic_fallback`
- `powerlifting-coef-calc`: assigned=`analytic-pipeline`, margin_pp=`0.0`, tie_break=`deterministic_fallback`

## Top-3 Near Ties

- `citation-check`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `civ6-adjacency-optimizer`: top3_spread_pp=`0.0`, best=`artifact-generation`
- `court-form-filling`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `earthquake-phase-association`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `energy-ac-optimal-power-flow`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `pdf-excel-diff`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `powerlifting-coef-calc`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `spring-boot-jakarta-migration`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
- `syzkaller-ppdev-syzlang`: top3_spread_pp=`0.0`, best=`analytic-pipeline`
