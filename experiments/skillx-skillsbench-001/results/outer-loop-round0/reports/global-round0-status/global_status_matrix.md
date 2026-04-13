# SkillX Round0 Global Status

- generated_at: `2026-04-13T05:56:12.213215+00:00`
- skillsbench_root: `/Users/Jackal/iWorld/projects/skillsbench-src`
- task_count_detected: `87`
- schema_count_detected: `7`
- total_pairs_expected: `609`
- completed_pairs: `55`
- docker_incident_pairs: `217`
- other_failed_pairs: `8`
- unrun_pairs: `329`

Legend: `C# = completed`, `D# = latest failure was Docker incident`, `F# = latest failure was other error`, `-0 = never run`.

## Source Runs

| run_label | total | succeeded | failed | finished_at | report_path |
| --- | ---: | ---: | ---: | --- | --- |
| earthquake-20260411-rerun | 7 | 7 | 0 | 2026-04-11T10:39:48.398399+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/earthquake-20260411-rerun/run_report.json` |
| run-3x7-2026-04-10 | 21 | 13 | 8 | 2026-04-11T06:33:04.887956+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/run-3x7-2026-04-10/run_report.json` |
| run-remaining-17x7-2026-04-11-v2 | 119 | 17 | 102 | 2026-04-11T23:16:30.468030+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/run-remaining-17x7-2026-04-11-v2/run_report.json` |
| run-next20x7-2026-04-11 | 140 | 18 | 122 | 2026-04-11T23:12:23.384207+00:00 | `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.3/reports/run-next20x7-2026-04-11/run_report.json` |

## Task x Schema Matrix

| task | artifact-generation | analytic-pipeline | engineering-composition | retrieval-heavy-synthesis | environment-control | methodology-guardrail | orchestration-delegation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3d-scan-calc | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| adaptive-cruise-control | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| azure-bgp-oscillation-route-leak | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| citation-check | C1 | C1 | C1 | C1 | C1 | C1 | C1 |
| civ6-adjacency-optimizer | C1 | C1 | C1 | C1 | C1 | C1 | C1 |
| court-form-filling | C1 | C1 | C1 | C1 | C1 | C1 | C1 |
| crystallographic-wyckoff-position-analysis | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| dapt-intrusion-detection | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| data-to-d3 | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| dialogue-parser | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| dynamic-object-aware-egomotion | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| earthquake-phase-association | C2 | C2 | C2 | C2 | C2 | C2 | C2 |
| earthquake-plate-calculation | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| econ-detrending-correlation | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| energy-ac-optimal-power-flow | F1 | C1 | C1 | C1 | C1 | C1 | C1 |
| energy-market-pricing | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| enterprise-information-search | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| exceltable-in-ppt | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| exoplanet-detection-period | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| financial-modeling-qa | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| find-topk-similiar-chemicals | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| fix-build-agentops | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| fix-build-google-auto | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| fix-druid-loophole-cve | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| fix-erlang-ssh-cve | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| fix-visual-stability | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| flink-query | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| flood-risk-analysis | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| gh-repo-analytics | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| glm-lake-mendota | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| gravitational-wave-detection | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| grid-dispatch-operator | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| hvac-control | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| invoice-fraud-detection | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| jax-computing-basics | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| jpg-ocr-stat | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| lab-unit-harmonization | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| lake-warming-attribution | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| latex-formula-extraction | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| lean4-proof | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| manufacturing-codebook-normalization | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| manufacturing-equipment-maintenance | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| manufacturing-fjsp-optimization | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| mario-coin-counting | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| mars-clouds-clustering | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| mhc-layer-impl | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| multilingual-video-dubbing | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| offer-letter-generator | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| organize-messy-files | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| paper-anonymizer | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| parallel-tfidf-search | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| pddl-tpp-planning | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| pdf-excel-diff | C1 | C1 | C1 | C1 | C1 | C1 | C1 |
| pedestrian-traffic-counting | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| pg-essay-to-audiobook | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| powerlifting-coef-calc | C1 | C1 | C1 | C1 | C1 | C1 | C1 |
| pptx-reference-formatting | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| protein-expression-analysis | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| python-scala-translation | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| quantum-numerical-simulation | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| r2r-mpc-control | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| react-performance-debugging | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| reserves-at-risk-calc | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| sales-pivot-analysis | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| scheduling-email-assistant | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| sec-financial-report | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| seismic-phase-picking | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| setup-fuzzing-py | F1 | F1 | F1 | F1 | F1 | F1 | F1 |
| shock-analysis-demand | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| shock-analysis-supply | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| simpo-code-reproduction | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| software-dependency-audit | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| speaker-diarization-subtitles | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| spring-boot-jakarta-migration | C1 | C1 | C1 | C1 | D1 | D1 | D1 |
| suricata-custom-exfil | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| syzkaller-ppdev-syzlang | C1 | C1 | C1 | D1 | D1 | D1 | D1 |
| taxonomy-tree-merge | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| threejs-structure-parser | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| threejs-to-obj | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| travel-planning | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| trend-anomaly-causal-inference | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| video-filler-word-remover | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| video-silence-remover | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| video-tutorial-indexer | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| virtualhome-agent-planning | D1 | D1 | D1 | D1 | D1 | D1 | D1 |
| weighted-gdp-calc | -0 | -0 | -0 | -0 | -0 | -0 | -0 |
| xlsx-recover-data | -0 | -0 | -0 | -0 | -0 | -0 | -0 |

## Pairs Needing Rerun: Docker Incident

- `3d-scan-calc__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `3d-scan-calc__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `3d-scan-calc__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `3d-scan-calc__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `3d-scan-calc__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `3d-scan-calc__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `3d-scan-calc__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `adaptive-cruise-control__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `adaptive-cruise-control__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `adaptive-cruise-control__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `adaptive-cruise-control__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `adaptive-cruise-control__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `adaptive-cruise-control__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `adaptive-cruise-control__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `data-to-d3__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `data-to-d3__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `data-to-d3__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `data-to-d3__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `data-to-d3__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `data-to-d3__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `data-to-d3__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `exceltable-in-ppt__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `exceltable-in-ppt__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `exceltable-in-ppt__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `exceltable-in-ppt__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `exceltable-in-ppt__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `exceltable-in-ppt__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `exceltable-in-ppt__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `find-topk-similiar-chemicals__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `find-topk-similiar-chemicals__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `find-topk-similiar-chemicals__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `find-topk-similiar-chemicals__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `find-topk-similiar-chemicals__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `find-topk-similiar-chemicals__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `find-topk-similiar-chemicals__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-build-agentops__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-build-agentops__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-build-agentops__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-build-agentops__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-build-agentops__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-build-agentops__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-build-agentops__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-druid-loophole-cve__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-druid-loophole-cve__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-druid-loophole-cve__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-druid-loophole-cve__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-druid-loophole-cve__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-druid-loophole-cve__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-druid-loophole-cve__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-erlang-ssh-cve__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-erlang-ssh-cve__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-erlang-ssh-cve__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-erlang-ssh-cve__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-erlang-ssh-cve__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-erlang-ssh-cve__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `fix-erlang-ssh-cve__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `gh-repo-analytics__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `gh-repo-analytics__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `gh-repo-analytics__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `gh-repo-analytics__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `gh-repo-analytics__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `gh-repo-analytics__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `gh-repo-analytics__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `glm-lake-mendota__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `glm-lake-mendota__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `glm-lake-mendota__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `glm-lake-mendota__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `glm-lake-mendota__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `glm-lake-mendota__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `glm-lake-mendota__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `lab-unit-harmonization__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `lab-unit-harmonization__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `lab-unit-harmonization__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `lab-unit-harmonization__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `lab-unit-harmonization__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `lab-unit-harmonization__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `lab-unit-harmonization__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `latex-formula-extraction__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `latex-formula-extraction__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `latex-formula-extraction__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `latex-formula-extraction__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `latex-formula-extraction__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `latex-formula-extraction__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `latex-formula-extraction__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `mars-clouds-clustering__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `mars-clouds-clustering__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `mars-clouds-clustering__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `mars-clouds-clustering__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `mars-clouds-clustering__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `mars-clouds-clustering__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `mars-clouds-clustering__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `multilingual-video-dubbing__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `multilingual-video-dubbing__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `multilingual-video-dubbing__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `multilingual-video-dubbing__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `multilingual-video-dubbing__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `multilingual-video-dubbing__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `multilingual-video-dubbing__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `offer-letter-generator__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `offer-letter-generator__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `offer-letter-generator__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `offer-letter-generator__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `offer-letter-generator__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `offer-letter-generator__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `offer-letter-generator__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `organize-messy-files__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `organize-messy-files__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `organize-messy-files__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `organize-messy-files__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `organize-messy-files__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `organize-messy-files__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `organize-messy-files__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `parallel-tfidf-search__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `parallel-tfidf-search__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `parallel-tfidf-search__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `parallel-tfidf-search__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `parallel-tfidf-search__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `parallel-tfidf-search__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `parallel-tfidf-search__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `pddl-tpp-planning__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `pddl-tpp-planning__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `pddl-tpp-planning__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `pddl-tpp-planning__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `pddl-tpp-planning__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `pddl-tpp-planning__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `pddl-tpp-planning__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `pg-essay-to-audiobook__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `pg-essay-to-audiobook__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `pg-essay-to-audiobook__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `pg-essay-to-audiobook__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `pg-essay-to-audiobook__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `pg-essay-to-audiobook__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `pg-essay-to-audiobook__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `protein-expression-analysis__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `protein-expression-analysis__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `protein-expression-analysis__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `protein-expression-analysis__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `protein-expression-analysis__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `protein-expression-analysis__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `protein-expression-analysis__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `reserves-at-risk-calc__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `reserves-at-risk-calc__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `reserves-at-risk-calc__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `reserves-at-risk-calc__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `reserves-at-risk-calc__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `reserves-at-risk-calc__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `reserves-at-risk-calc__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `sec-financial-report__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `sec-financial-report__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `sec-financial-report__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `sec-financial-report__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `sec-financial-report__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `sec-financial-report__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `sec-financial-report__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `shock-analysis-demand__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `shock-analysis-demand__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `shock-analysis-demand__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `shock-analysis-demand__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `shock-analysis-demand__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `shock-analysis-demand__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `shock-analysis-demand__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `shock-analysis-supply__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `shock-analysis-supply__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `shock-analysis-supply__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `shock-analysis-supply__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `shock-analysis-supply__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `shock-analysis-supply__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `shock-analysis-supply__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `simpo-code-reproduction__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `simpo-code-reproduction__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `simpo-code-reproduction__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `simpo-code-reproduction__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `simpo-code-reproduction__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `simpo-code-reproduction__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `simpo-code-reproduction__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `spring-boot-jakarta-migration__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `spring-boot-jakarta-migration__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `spring-boot-jakarta-migration__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `syzkaller-ppdev-syzlang__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `syzkaller-ppdev-syzlang__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `syzkaller-ppdev-syzlang__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `syzkaller-ppdev-syzlang__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `taxonomy-tree-merge__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `taxonomy-tree-merge__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `taxonomy-tree-merge__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `taxonomy-tree-merge__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `taxonomy-tree-merge__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `taxonomy-tree-merge__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `taxonomy-tree-merge__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `threejs-to-obj__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `threejs-to-obj__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `threejs-to-obj__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `threejs-to-obj__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `threejs-to-obj__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `threejs-to-obj__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `threejs-to-obj__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `travel-planning__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `travel-planning__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `travel-planning__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `travel-planning__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `travel-planning__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `travel-planning__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `travel-planning__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `trend-anomaly-causal-inference__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `trend-anomaly-causal-inference__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `trend-anomaly-causal-inference__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `trend-anomaly-causal-inference__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `trend-anomaly-causal-inference__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `trend-anomaly-causal-inference__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `trend-anomaly-causal-inference__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `virtualhome-agent-planning__artifact-generation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `virtualhome-agent-planning__analytic-pipeline`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `virtualhome-agent-planning__engineering-composition`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `virtualhome-agent-planning__retrieval-heavy-synthesis`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `virtualhome-agent-planning__environment-control`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `virtualhome-agent-planning__methodology-guardrail`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- `virtualhome-agent-planning__orchestration-delegation`: status=`docker_incident`, attempts=`1`, latest_run=`run-next20x7-2026-04-11`, reason=`docker_incident`
  latest_failure: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

## Pairs Needing Attention: Other Failure

- `energy-ac-optimal-power-flow__artifact-generation`: status=`failed_other`, attempts=`1`, latest_run=`run-3x7-2026-04-10`, reason=`other_failure`
  latest_failure: `ManualRoleAStallTermination: terminated stalled role_a codex exec after prolonged inactivity so the launcher could continue`
- `setup-fuzzing-py__artifact-generation`: status=`failed_other`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`missing_task_inputs`
  latest_failure: `FileNotFoundError: missing task inputs for setup-fuzzing-py: ['~/iWorld/projects/skillsbench-src/tasks/setup-fuzzing-py/tests/test_outputs.py']`
- `setup-fuzzing-py__analytic-pipeline`: status=`failed_other`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`missing_task_inputs`
  latest_failure: `FileNotFoundError: missing task inputs for setup-fuzzing-py: ['~/iWorld/projects/skillsbench-src/tasks/setup-fuzzing-py/tests/test_outputs.py']`
- `setup-fuzzing-py__engineering-composition`: status=`failed_other`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`missing_task_inputs`
  latest_failure: `FileNotFoundError: missing task inputs for setup-fuzzing-py: ['~/iWorld/projects/skillsbench-src/tasks/setup-fuzzing-py/tests/test_outputs.py']`
- `setup-fuzzing-py__retrieval-heavy-synthesis`: status=`failed_other`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`missing_task_inputs`
  latest_failure: `FileNotFoundError: missing task inputs for setup-fuzzing-py: ['~/iWorld/projects/skillsbench-src/tasks/setup-fuzzing-py/tests/test_outputs.py']`
- `setup-fuzzing-py__environment-control`: status=`failed_other`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`missing_task_inputs`
  latest_failure: `FileNotFoundError: missing task inputs for setup-fuzzing-py: ['~/iWorld/projects/skillsbench-src/tasks/setup-fuzzing-py/tests/test_outputs.py']`
- `setup-fuzzing-py__methodology-guardrail`: status=`failed_other`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`missing_task_inputs`
  latest_failure: `FileNotFoundError: missing task inputs for setup-fuzzing-py: ['~/iWorld/projects/skillsbench-src/tasks/setup-fuzzing-py/tests/test_outputs.py']`
- `setup-fuzzing-py__orchestration-delegation`: status=`failed_other`, attempts=`1`, latest_run=`run-remaining-17x7-2026-04-11-v2`, reason=`missing_task_inputs`
  latest_failure: `FileNotFoundError: missing task inputs for setup-fuzzing-py: ['~/iWorld/projects/skillsbench-src/tasks/setup-fuzzing-py/tests/test_outputs.py']`

## Pairs Not Yet Run

- `azure-bgp-oscillation-route-leak__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `azure-bgp-oscillation-route-leak__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `azure-bgp-oscillation-route-leak__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `azure-bgp-oscillation-route-leak__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `azure-bgp-oscillation-route-leak__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `azure-bgp-oscillation-route-leak__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `azure-bgp-oscillation-route-leak__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `crystallographic-wyckoff-position-analysis__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `crystallographic-wyckoff-position-analysis__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `crystallographic-wyckoff-position-analysis__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `crystallographic-wyckoff-position-analysis__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `crystallographic-wyckoff-position-analysis__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `crystallographic-wyckoff-position-analysis__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `crystallographic-wyckoff-position-analysis__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dapt-intrusion-detection__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dapt-intrusion-detection__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dapt-intrusion-detection__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dapt-intrusion-detection__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dapt-intrusion-detection__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dapt-intrusion-detection__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dapt-intrusion-detection__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dialogue-parser__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dialogue-parser__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dialogue-parser__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dialogue-parser__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dialogue-parser__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dialogue-parser__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dialogue-parser__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dynamic-object-aware-egomotion__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dynamic-object-aware-egomotion__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dynamic-object-aware-egomotion__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dynamic-object-aware-egomotion__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dynamic-object-aware-egomotion__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dynamic-object-aware-egomotion__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `dynamic-object-aware-egomotion__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `earthquake-plate-calculation__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `earthquake-plate-calculation__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `earthquake-plate-calculation__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `earthquake-plate-calculation__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `earthquake-plate-calculation__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `earthquake-plate-calculation__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `earthquake-plate-calculation__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `econ-detrending-correlation__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `econ-detrending-correlation__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `econ-detrending-correlation__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `econ-detrending-correlation__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `econ-detrending-correlation__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `econ-detrending-correlation__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `econ-detrending-correlation__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `energy-market-pricing__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `energy-market-pricing__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `energy-market-pricing__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `energy-market-pricing__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `energy-market-pricing__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `energy-market-pricing__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `energy-market-pricing__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `enterprise-information-search__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `enterprise-information-search__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `enterprise-information-search__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `enterprise-information-search__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `enterprise-information-search__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `enterprise-information-search__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `enterprise-information-search__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `exoplanet-detection-period__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `exoplanet-detection-period__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `exoplanet-detection-period__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `exoplanet-detection-period__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `exoplanet-detection-period__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `exoplanet-detection-period__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `exoplanet-detection-period__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `financial-modeling-qa__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `financial-modeling-qa__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `financial-modeling-qa__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `financial-modeling-qa__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `financial-modeling-qa__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `financial-modeling-qa__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `financial-modeling-qa__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `fix-build-google-auto__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `fix-build-google-auto__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `fix-build-google-auto__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `fix-build-google-auto__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `fix-build-google-auto__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `fix-build-google-auto__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `fix-build-google-auto__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `fix-visual-stability__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `fix-visual-stability__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `fix-visual-stability__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `fix-visual-stability__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `fix-visual-stability__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `fix-visual-stability__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `fix-visual-stability__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `flink-query__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `flink-query__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `flink-query__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `flink-query__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `flink-query__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `flink-query__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `flink-query__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `flood-risk-analysis__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `flood-risk-analysis__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `flood-risk-analysis__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `flood-risk-analysis__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `flood-risk-analysis__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `flood-risk-analysis__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `flood-risk-analysis__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `gravitational-wave-detection__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `gravitational-wave-detection__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `gravitational-wave-detection__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `gravitational-wave-detection__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `gravitational-wave-detection__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `gravitational-wave-detection__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `gravitational-wave-detection__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `grid-dispatch-operator__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `grid-dispatch-operator__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `grid-dispatch-operator__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `grid-dispatch-operator__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `grid-dispatch-operator__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `grid-dispatch-operator__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `grid-dispatch-operator__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `hvac-control__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `hvac-control__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `hvac-control__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `hvac-control__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `hvac-control__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `hvac-control__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `hvac-control__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `invoice-fraud-detection__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `invoice-fraud-detection__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `invoice-fraud-detection__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `invoice-fraud-detection__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `invoice-fraud-detection__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `invoice-fraud-detection__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `invoice-fraud-detection__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `jax-computing-basics__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `jax-computing-basics__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `jax-computing-basics__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `jax-computing-basics__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `jax-computing-basics__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `jax-computing-basics__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `jax-computing-basics__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `jpg-ocr-stat__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `jpg-ocr-stat__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `jpg-ocr-stat__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `jpg-ocr-stat__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `jpg-ocr-stat__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `jpg-ocr-stat__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `jpg-ocr-stat__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `lake-warming-attribution__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `lake-warming-attribution__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `lake-warming-attribution__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `lake-warming-attribution__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `lake-warming-attribution__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `lake-warming-attribution__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `lake-warming-attribution__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `lean4-proof__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `lean4-proof__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `lean4-proof__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `lean4-proof__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `lean4-proof__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `lean4-proof__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `lean4-proof__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-codebook-normalization__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-codebook-normalization__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-codebook-normalization__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-codebook-normalization__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-codebook-normalization__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-codebook-normalization__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-codebook-normalization__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-equipment-maintenance__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-equipment-maintenance__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-equipment-maintenance__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-equipment-maintenance__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-equipment-maintenance__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-equipment-maintenance__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-equipment-maintenance__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-fjsp-optimization__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-fjsp-optimization__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-fjsp-optimization__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-fjsp-optimization__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-fjsp-optimization__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-fjsp-optimization__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `manufacturing-fjsp-optimization__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `mario-coin-counting__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `mario-coin-counting__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `mario-coin-counting__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `mario-coin-counting__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `mario-coin-counting__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `mario-coin-counting__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `mario-coin-counting__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `mhc-layer-impl__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `mhc-layer-impl__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `mhc-layer-impl__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `mhc-layer-impl__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `mhc-layer-impl__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `mhc-layer-impl__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `mhc-layer-impl__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `paper-anonymizer__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `paper-anonymizer__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `paper-anonymizer__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `paper-anonymizer__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `paper-anonymizer__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `paper-anonymizer__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `paper-anonymizer__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `pedestrian-traffic-counting__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `pedestrian-traffic-counting__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `pedestrian-traffic-counting__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `pedestrian-traffic-counting__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `pedestrian-traffic-counting__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `pedestrian-traffic-counting__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `pedestrian-traffic-counting__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `pptx-reference-formatting__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `pptx-reference-formatting__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `pptx-reference-formatting__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `pptx-reference-formatting__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `pptx-reference-formatting__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `pptx-reference-formatting__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `pptx-reference-formatting__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `python-scala-translation__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `python-scala-translation__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `python-scala-translation__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `python-scala-translation__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `python-scala-translation__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `python-scala-translation__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `python-scala-translation__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `quantum-numerical-simulation__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `quantum-numerical-simulation__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `quantum-numerical-simulation__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `quantum-numerical-simulation__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `quantum-numerical-simulation__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `quantum-numerical-simulation__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `quantum-numerical-simulation__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `r2r-mpc-control__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `r2r-mpc-control__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `r2r-mpc-control__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `r2r-mpc-control__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `r2r-mpc-control__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `r2r-mpc-control__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `r2r-mpc-control__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `react-performance-debugging__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `react-performance-debugging__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `react-performance-debugging__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `react-performance-debugging__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `react-performance-debugging__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `react-performance-debugging__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `react-performance-debugging__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `sales-pivot-analysis__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `sales-pivot-analysis__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `sales-pivot-analysis__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `sales-pivot-analysis__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `sales-pivot-analysis__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `sales-pivot-analysis__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `sales-pivot-analysis__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `scheduling-email-assistant__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `scheduling-email-assistant__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `scheduling-email-assistant__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `scheduling-email-assistant__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `scheduling-email-assistant__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `scheduling-email-assistant__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `scheduling-email-assistant__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `seismic-phase-picking__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `seismic-phase-picking__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `seismic-phase-picking__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `seismic-phase-picking__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `seismic-phase-picking__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `seismic-phase-picking__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `seismic-phase-picking__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `software-dependency-audit__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `software-dependency-audit__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `software-dependency-audit__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `software-dependency-audit__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `software-dependency-audit__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `software-dependency-audit__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `software-dependency-audit__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `speaker-diarization-subtitles__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `speaker-diarization-subtitles__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `speaker-diarization-subtitles__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `speaker-diarization-subtitles__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `speaker-diarization-subtitles__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `speaker-diarization-subtitles__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `speaker-diarization-subtitles__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `suricata-custom-exfil__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `suricata-custom-exfil__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `suricata-custom-exfil__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `suricata-custom-exfil__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `suricata-custom-exfil__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `suricata-custom-exfil__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `suricata-custom-exfil__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `threejs-structure-parser__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `threejs-structure-parser__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `threejs-structure-parser__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `threejs-structure-parser__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `threejs-structure-parser__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `threejs-structure-parser__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `threejs-structure-parser__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-filler-word-remover__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-filler-word-remover__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-filler-word-remover__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-filler-word-remover__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-filler-word-remover__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-filler-word-remover__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-filler-word-remover__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-silence-remover__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-silence-remover__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-silence-remover__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-silence-remover__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-silence-remover__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-silence-remover__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-silence-remover__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-tutorial-indexer__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-tutorial-indexer__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-tutorial-indexer__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-tutorial-indexer__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-tutorial-indexer__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-tutorial-indexer__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `video-tutorial-indexer__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `weighted-gdp-calc__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `weighted-gdp-calc__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `weighted-gdp-calc__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `weighted-gdp-calc__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `weighted-gdp-calc__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `weighted-gdp-calc__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `weighted-gdp-calc__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `xlsx-recover-data__artifact-generation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `xlsx-recover-data__analytic-pipeline`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `xlsx-recover-data__engineering-composition`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `xlsx-recover-data__retrieval-heavy-synthesis`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `xlsx-recover-data__environment-control`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `xlsx-recover-data__methodology-guardrail`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
- `xlsx-recover-data__orchestration-delegation`: status=`unrun`, attempts=`0`, latest_run=``, reason=`unrun`
