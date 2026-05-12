# Round2 Guarded-Patch Final 140 Results Table

| batch_id | batch_index | task_name | schema_id | final_run_status | selected_round | selected_reward | r0_reward | r1_reward | r2_reward | r3_reward | final_issue_codes | archive_count | pair_rerun_or_exception_history |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b01 | 1 | adaptive-cruise-control | artifact-generation | completed | R1 | 1 | 0 | 1 | 0 | 0 | complete_without_exceptions | 0 |  |
| b01 | 2 | adaptive-cruise-control | analytic-pipeline | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b01 | 3 | adaptive-cruise-control | engineering-composition | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b01 | 4 | adaptive-cruise-control | retrieval-heavy-synthesis | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b01 | 5 | adaptive-cruise-control | environment-control | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b01 | 6 | adaptive-cruise-control | methodology-guardrail | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b01 | 7 | adaptive-cruise-control | orchestration-delegation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b01 | 8 | earthquake-phase-association | artifact-generation | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b01 | 9 | earthquake-phase-association | analytic-pipeline | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b01 | 10 | earthquake-phase-association | engineering-composition | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b01 | 11 | earthquake-phase-association | retrieval-heavy-synthesis | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b01 | 12 | earthquake-phase-association | environment-control | completed | R1 | 1 | 0 | 1 | 1 | 1 | complete_without_exceptions | 0 |  |
| b01 | 13 | earthquake-phase-association | methodology-guardrail | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b01 | 14 | earthquake-phase-association | orchestration-delegation | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 | 2026-05-11T06:50:36.679806+00:00: archived launcher pair_failed stage=run returncode=2 message= \| 2026-05-11T07:02:58.017667+00:00: archived launcher docker_health_probe_failed stage=docker_health_gate returncode=None message=docker_info returned exit code 1 \| 2026-05-11T07:03:51.178434+00:00: docker auto recovery successful=True |
| b01 | 15 | energy-ac-optimal-power-flow | artifact-generation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 | 2026-05-11T06:50:37.155975+00:00: archived launcher docker_health_probe_failed stage=docker_health_gate returncode=None message=docker_info returned exit code 1 \| 2026-05-11T06:53:50.069141+00:00: archived launcher pair_failed stage=docker_health_gate returncode=None message=docker_info returned exit code 1 \| 2026-05-11T06:53:49.227700+00:00: docker auto recovery successful=True |
| b01 | 16 | energy-ac-optimal-power-flow | analytic-pipeline | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b01 | 17 | energy-ac-optimal-power-flow | engineering-composition | completed | R3 | 1 | 0 | 0 | 0 | 1 | complete_without_exceptions | 0 |  |
| b01 | 18 | energy-ac-optimal-power-flow | retrieval-heavy-synthesis | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b01 | 19 | energy-ac-optimal-power-flow | environment-control | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 1 | 2026-05-12T00:18:59.399012+00:00: archived b01 runtime-failure pair and launcher log before same-label rerun (dashboard completed_with_issues; RUN_STATUS showed completed_with_runtime_failures at R0) |
| b01 | 20 | energy-ac-optimal-power-flow | methodology-guardrail | completed | R2 | 1 | 0 | 0 | 1 | 0 | complete_without_exceptions | 0 |  |
| b01 | 21 | energy-ac-optimal-power-flow | orchestration-delegation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b01 | 22 | data-to-d3 | artifact-generation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b01 | 23 | data-to-d3 | analytic-pipeline | completed | R1 | 1 | 0 | 1 | 0 | 0 | complete_without_exceptions | 0 |  |
| b01 | 24 | data-to-d3 | engineering-composition | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b01 | 25 | data-to-d3 | retrieval-heavy-synthesis | completed | R3 | 1 | 0 | 0 | 0 | 1 | complete_without_exceptions | 0 |  |
| b01 | 26 | data-to-d3 | environment-control | completed | R2 | 1 | 0 | 0 | 1 | 0 | complete_without_exceptions | 0 |  |
| b01 | 27 | data-to-d3 | methodology-guardrail | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b01 | 28 | data-to-d3 | orchestration-delegation | completed | R2 | 1 | 0 | 0 | 1 | 0 | complete_without_exceptions | 0 |  |
| b02 | 1 | citation-check | artifact-generation | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 1 | 2026-05-11T10:19:11.202744+00:00: archived b02 runtime-failure pairs and launcher log before same-label rerun (dashboard completed_with_issues; RUN_STATUS showed completed_with_runtime_failures) |
| b02 | 2 | citation-check | analytic-pipeline | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b02 | 3 | citation-check | engineering-composition | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b02 | 4 | citation-check | retrieval-heavy-synthesis | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b02 | 5 | citation-check | environment-control | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b02 | 6 | citation-check | methodology-guardrail | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 1 | 2026-05-11T10:19:11.202744+00:00: archived b02 runtime-failure pairs and launcher log before same-label rerun (dashboard completed_with_issues; RUN_STATUS showed completed_with_runtime_failures) |
| b02 | 7 | citation-check | orchestration-delegation | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b02 | 8 | energy-market-pricing | artifact-generation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b02 | 9 | energy-market-pricing | analytic-pipeline | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b02 | 10 | energy-market-pricing | engineering-composition | completed | R1 | 1 | 0 | 1 | 0 | 1 | complete_without_exceptions | 0 |  |
| b02 | 11 | energy-market-pricing | retrieval-heavy-synthesis | completed | R1 | 1 | 0 | 1 | 1 | 0 | complete_without_exceptions | 0 |  |
| b02 | 12 | energy-market-pricing | environment-control | completed | R2 | 1 | 0 | 0 | 1 | 1 | complete_without_exceptions | 0 |  |
| b02 | 13 | energy-market-pricing | methodology-guardrail | completed | R2 | 1 | 0 | 0 | 1 | 0 | complete_without_exceptions | 0 |  |
| b02 | 14 | energy-market-pricing | orchestration-delegation | completed | R1 | 1 | 0 | 1 | 1 | 0 | complete_without_exceptions | 0 |  |
| b02 | 15 | exceltable-in-ppt | artifact-generation | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b02 | 16 | exceltable-in-ppt | analytic-pipeline | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b02 | 17 | exceltable-in-ppt | engineering-composition | completed | R1 | 1 | 0 | 1 | 1 | 1 | complete_without_exceptions | 0 |  |
| b02 | 18 | exceltable-in-ppt | retrieval-heavy-synthesis | completed | R1 | 1 | 0 | 1 | 1 | 1 | complete_without_exceptions | 0 |  |
| b02 | 19 | exceltable-in-ppt | environment-control | completed | R1 | 1 | 0 | 1 | 1 | 1 | complete_without_exceptions | 0 |  |
| b02 | 20 | exceltable-in-ppt | methodology-guardrail | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b02 | 21 | exceltable-in-ppt | orchestration-delegation | completed | R1 | 1 | 0 | 1 | 1 | 1 | complete_without_exceptions | 0 |  |
| b02 | 22 | fix-build-google-auto | artifact-generation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b02 | 23 | fix-build-google-auto | analytic-pipeline | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b02 | 24 | fix-build-google-auto | engineering-composition | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b02 | 25 | fix-build-google-auto | retrieval-heavy-synthesis | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b02 | 26 | fix-build-google-auto | environment-control | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 | 2026-05-11T06:50:36.508864+00:00: archived launcher pair_failed stage=run returncode=2 message= \| 2026-05-11T07:02:58.017420+00:00: archived launcher docker_health_probe_failed stage=docker_health_gate returncode=None message=docker_info returned exit code 1 \| 2026-05-11T07:04:08.491189+00:00: docker auto recovery successful=True |
| b02 | 27 | fix-build-google-auto | methodology-guardrail | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 | 2026-05-11T06:50:37.005092+00:00: archived launcher docker_health_probe_failed stage=docker_health_gate returncode=None message=docker_info returned exit code 1 \| 2026-05-11T06:53:50.070447+00:00: archived launcher pair_failed stage=docker_health_gate returncode=None message=docker_info returned exit code 1 \| 2026-05-11T06:53:49.247992+00:00: docker auto recovery successful=True |
| b02 | 28 | fix-build-google-auto | orchestration-delegation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 1 | civ6-adjacency-optimizer | artifact-generation | completed | R0 | 0.6 | 0.6 | 0.5 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 2 | civ6-adjacency-optimizer | analytic-pipeline | completed | R3 | 0.6 | 0.55 | 0 | 0.5 | 0.6 | complete_without_exceptions | 0 |  |
| b03 | 3 | civ6-adjacency-optimizer | engineering-composition | completed | R0 | 0.55 | 0.55 | 0 | 0 | 0.55 | complete_without_exceptions | 0 |  |
| b03 | 4 | civ6-adjacency-optimizer | retrieval-heavy-synthesis | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 5 | civ6-adjacency-optimizer | environment-control | completed | R0 | 0.6 | 0.6 | 0 | 0.6 | 0.6 | complete_without_exceptions | 0 |  |
| b03 | 6 | civ6-adjacency-optimizer | methodology-guardrail | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 7 | civ6-adjacency-optimizer | orchestration-delegation | completed | R1 | 0.5 | 0 | 0.5 | 0.45 | 0.5 | complete_without_exceptions | 0 |  |
| b03 | 8 | exoplanet-detection-period | artifact-generation | completed | R2 | 1 | 0 | 0 | 1 | 0 | complete_without_exceptions | 0 |  |
| b03 | 9 | exoplanet-detection-period | analytic-pipeline | completed | R1 | 1 | 0 | 1 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 10 | exoplanet-detection-period | engineering-composition | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 11 | exoplanet-detection-period | retrieval-heavy-synthesis | completed | R3 | 1 | 0 | 0 | 0 | 1 | complete_without_exceptions | 0 |  |
| b03 | 12 | exoplanet-detection-period | environment-control | completed | R1 | 1 | 0 | 1 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 13 | exoplanet-detection-period | methodology-guardrail | completed | R1 | 1 | 0 | 1 | 1 | 0 | complete_without_exceptions | 0 |  |
| b03 | 14 | exoplanet-detection-period | orchestration-delegation | completed | R3 | 1 | 0 | 0 | 0 | 1 | complete_without_exceptions | 0 |  |
| b03 | 15 | fix-druid-loophole-cve | artifact-generation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 16 | fix-druid-loophole-cve | analytic-pipeline | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 17 | fix-druid-loophole-cve | engineering-composition | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 18 | fix-druid-loophole-cve | retrieval-heavy-synthesis | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 | 2026-05-11T06:50:36.642476+00:00: archived launcher pair_failed stage=run returncode=2 message= \| 2026-05-11T07:02:58.017452+00:00: active launcher docker_health_probe_failed stage=docker_health_gate returncode=None message=docker_info returned exit code 1 \| 2026-05-11T07:03:51.511036+00:00: docker auto recovery successful=True |
| b03 | 19 | fix-druid-loophole-cve | environment-control | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 | 2026-05-11T06:50:37.123553+00:00: archived launcher docker_health_probe_failed stage=docker_health_gate returncode=None message=docker_info returned exit code 1 \| 2026-05-11T06:53:50.070845+00:00: archived launcher pair_failed stage=docker_health_gate returncode=None message=docker_info returned exit code 1 \| 2026-05-11T06:53:49.214410+00:00: docker auto recovery successful=True |
| b03 | 20 | fix-druid-loophole-cve | methodology-guardrail | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 21 | fix-druid-loophole-cve | orchestration-delegation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 22 | azure-bgp-oscillation-route-leak | artifact-generation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 23 | azure-bgp-oscillation-route-leak | analytic-pipeline | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 24 | azure-bgp-oscillation-route-leak | engineering-composition | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 25 | azure-bgp-oscillation-route-leak | retrieval-heavy-synthesis | completed | R2 | 1 | 0 | 0 | 1 | 0 | complete_without_exceptions | 0 |  |
| b03 | 26 | azure-bgp-oscillation-route-leak | environment-control | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 27 | azure-bgp-oscillation-route-leak | methodology-guardrail | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b03 | 28 | azure-bgp-oscillation-route-leak | orchestration-delegation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b04 | 1 | court-form-filling | artifact-generation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b04 | 2 | court-form-filling | analytic-pipeline | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b04 | 3 | court-form-filling | engineering-composition | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 1 | 2026-05-10T21:21:34.822824+00:00: archived b04 launcher log and court-form-filling__engineering-composition runtime-failure run before same-label rerun (completed_with_runtime_failures at R2; audit marked rerun required) |
| b04 | 4 | court-form-filling | retrieval-heavy-synthesis | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b04 | 5 | court-form-filling | environment-control | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b04 | 6 | court-form-filling | methodology-guardrail | completed | R2 | 1 | 0 | 0 | 1 | 0 | complete_without_exceptions | 0 |  |
| b04 | 7 | court-form-filling | orchestration-delegation | completed | R3 | 1 | 0 | 0 | 0 | 1 | complete_without_exceptions | 0 |  |
| b04 | 8 | earthquake-plate-calculation | artifact-generation | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b04 | 9 | earthquake-plate-calculation | analytic-pipeline | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b04 | 10 | earthquake-plate-calculation | engineering-composition | completed | R2 | 1 | 0 | 0 | 1 | 1 | complete_without_exceptions | 0 |  |
| b04 | 11 | earthquake-plate-calculation | retrieval-heavy-synthesis | completed | R1 | 1 | 0 | 1 | 1 | 1 | complete_without_exceptions | 0 |  |
| b04 | 12 | earthquake-plate-calculation | environment-control | completed | R2 | 1 | 0 | 0 | 1 | 0 | complete_without_exceptions | 0 |  |
| b04 | 13 | earthquake-plate-calculation | methodology-guardrail | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b04 | 14 | earthquake-plate-calculation | orchestration-delegation | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b04 | 15 | financial-modeling-qa | artifact-generation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b04 | 16 | financial-modeling-qa | analytic-pipeline | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b04 | 17 | financial-modeling-qa | engineering-composition | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b04 | 18 | financial-modeling-qa | retrieval-heavy-synthesis | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b04 | 19 | financial-modeling-qa | environment-control | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b04 | 20 | financial-modeling-qa | methodology-guardrail | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b04 | 21 | financial-modeling-qa | orchestration-delegation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b04 | 22 | 3d-scan-calc | artifact-generation | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b04 | 23 | 3d-scan-calc | analytic-pipeline | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b04 | 24 | 3d-scan-calc | engineering-composition | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b04 | 25 | 3d-scan-calc | retrieval-heavy-synthesis | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b04 | 26 | 3d-scan-calc | environment-control | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b04 | 27 | 3d-scan-calc | methodology-guardrail | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b04 | 28 | 3d-scan-calc | orchestration-delegation | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b05 | 1 | dapt-intrusion-detection | artifact-generation | completed | R3 | 1 | 0 | 0 | 0 | 1 | complete_without_exceptions | 0 |  |
| b05 | 2 | dapt-intrusion-detection | analytic-pipeline | completed | R2 | 1 | 0 | 0 | 1 | 0 | complete_without_exceptions | 0 |  |
| b05 | 3 | dapt-intrusion-detection | engineering-composition | completed | R1 | 1 | 0 | 1 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 4 | dapt-intrusion-detection | retrieval-heavy-synthesis | completed | R1 | 1 | 0 | 1 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 5 | dapt-intrusion-detection | environment-control | completed | R1 | 1 | 0 | 1 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 6 | dapt-intrusion-detection | methodology-guardrail | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b05 | 7 | dapt-intrusion-detection | orchestration-delegation | completed | R3 | 1 | 0 | 0 | 0 | 1 | complete_without_exceptions | 0 |  |
| b05 | 8 | econ-detrending-correlation | artifact-generation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 9 | econ-detrending-correlation | analytic-pipeline | completed | R1 | 1 | 0 | 1 | 1 | 1 | complete_without_exceptions | 0 |  |
| b05 | 10 | econ-detrending-correlation | engineering-composition | skipped_baseline_perfect | R0 | 1 | 1 |  |  |  | baseline_perfect_skip | 0 |  |
| b05 | 11 | econ-detrending-correlation | retrieval-heavy-synthesis | completed | R1 | 1 | 0 | 1 | 1 | 0 | complete_without_exceptions | 0 |  |
| b05 | 12 | econ-detrending-correlation | environment-control | completed | R1 | 1 | 0 | 1 | 1 | 0 | complete_without_exceptions | 0 |  |
| b05 | 13 | econ-detrending-correlation | methodology-guardrail | completed | R1 | 1 | 0 | 1 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 14 | econ-detrending-correlation | orchestration-delegation | completed | R1 | 1 | 0 | 1 | 1 | 1 | complete_without_exceptions | 0 |  |
| b05 | 15 | find-topk-similiar-chemicals | artifact-generation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 16 | find-topk-similiar-chemicals | analytic-pipeline | completed | R1 | 0.5 | 0 | 0.5 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 17 | find-topk-similiar-chemicals | engineering-composition | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 18 | find-topk-similiar-chemicals | retrieval-heavy-synthesis | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 19 | find-topk-similiar-chemicals | environment-control | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 20 | find-topk-similiar-chemicals | methodology-guardrail | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 21 | find-topk-similiar-chemicals | orchestration-delegation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 22 | fix-build-agentops | artifact-generation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 23 | fix-build-agentops | analytic-pipeline | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 24 | fix-build-agentops | engineering-composition | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 25 | fix-build-agentops | retrieval-heavy-synthesis | completed | R0 | 0 | 0 | 0 | 0 |  | complete_without_exceptions | 0 |  |
| b05 | 26 | fix-build-agentops | environment-control | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 27 | fix-build-agentops | methodology-guardrail | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 |  |
| b05 | 28 | fix-build-agentops | orchestration-delegation | completed | R0 | 0 | 0 | 0 | 0 | 0 | complete_without_exceptions | 0 | 2026-05-11T06:53:55.723466+00:00: archived launcher pair_failed stage=run returncode=2 message= \| 2026-05-11T07:02:58.017419+00:00: active launcher docker_health_probe_failed stage=docker_health_gate returncode=None message=docker_info returned exit code 1 \| 2026-05-11T07:03:51.250636+00:00: docker auto recovery successful=True |
