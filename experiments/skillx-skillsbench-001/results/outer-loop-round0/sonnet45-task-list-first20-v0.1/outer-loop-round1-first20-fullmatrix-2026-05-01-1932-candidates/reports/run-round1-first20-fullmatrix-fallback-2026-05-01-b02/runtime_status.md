# SkillX Round0 Runtime Status: `run-round1-first20-fullmatrix-fallback-2026-05-01-b02`

| Pair | Launcher | Return | Run | Evidence | Failure | Timeout | Early Stop | Started | Finished | Duration (s) |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | ---: |
| adaptive-cruise-control__artifact-generation | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:16.824010+00:00 | 2026-05-04T13:13:16.824230+00:00 | 0.0 |
| adaptive-cruise-control__analytic-pipeline | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:16.824583+00:00 | 2026-05-04T13:13:16.824767+00:00 | 0.0 |
| adaptive-cruise-control__engineering-composition | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:16.825115+00:00 | 2026-05-04T13:13:16.825297+00:00 | 0.0 |
| adaptive-cruise-control__retrieval-heavy-synthesis | failed | 1 | failed | runtime-blocked | RuntimeError: expected exactly one trial dir under <repo-root>/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round1-first20-fullmatrix-2026-05-01-1932-candidates/pairs/adaptive-cruise-control__retrieval-heavy-synthesis/refine_run_run-round1-first20-fullmatrix-fallback-2026-05-01-b02/refine/adaptive-cruise-control/rounds/round-0/tune_check/adaptive-cruise-control-round-0-c4-tune, found 0 | no | no | 2026-05-04T13:13:16.825740+00:00 | 2026-05-04T13:13:17.277957+00:00 | 0.5 |
| adaptive-cruise-control__environment-control | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.278536+00:00 | 2026-05-04T13:13:17.278922+00:00 | 0.0 |
| adaptive-cruise-control__methodology-guardrail | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.279524+00:00 | 2026-05-04T13:13:17.279748+00:00 | 0.0 |
| adaptive-cruise-control__orchestration-delegation | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.280327+00:00 | 2026-05-04T13:13:17.280558+00:00 | 0.0 |
| civ6-adjacency-optimizer__artifact-generation | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.281116+00:00 | 2026-05-04T13:13:17.281385+00:00 | 0.0 |
| civ6-adjacency-optimizer__analytic-pipeline | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.281946+00:00 | 2026-05-04T13:13:17.282276+00:00 | 0.0 |
| civ6-adjacency-optimizer__engineering-composition | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.282869+00:00 | 2026-05-04T13:13:17.283084+00:00 | 0.0 |
| civ6-adjacency-optimizer__retrieval-heavy-synthesis | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.283578+00:00 | 2026-05-04T13:13:17.283794+00:00 | 0.0 |
| civ6-adjacency-optimizer__environment-control | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.284300+00:00 | 2026-05-04T13:13:17.284525+00:00 | 0.0 |
| civ6-adjacency-optimizer__methodology-guardrail | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.285014+00:00 | 2026-05-04T13:13:17.285246+00:00 | 0.0 |
| civ6-adjacency-optimizer__orchestration-delegation | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.285705+00:00 | 2026-05-04T13:13:17.285904+00:00 | 0.0 |
| data-to-d3__artifact-generation | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.286359+00:00 | 2026-05-04T13:13:17.286559+00:00 | 0.0 |
| data-to-d3__analytic-pipeline | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.287005+00:00 | 2026-05-04T13:13:17.287240+00:00 | 0.0 |
| data-to-d3__engineering-composition | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.287780+00:00 | 2026-05-04T13:13:17.288027+00:00 | 0.0 |
| data-to-d3__retrieval-heavy-synthesis | succeeded | 0 | completed_with_runtime_failures | ambiguous | RuntimeError=['c4-data-to-d3-round-2__rQFGypY'] | no | no | 2026-05-04T13:13:17.288598+00:00 | 2026-05-04T13:13:17.288948+00:00 | 0.0 |
| data-to-d3__environment-control | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.289542+00:00 | 2026-05-04T13:13:17.289761+00:00 | 0.0 |
| data-to-d3__methodology-guardrail | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.290462+00:00 | 2026-05-04T13:13:17.290702+00:00 | 0.0 |
| data-to-d3__orchestration-delegation | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.291193+00:00 | 2026-05-04T13:13:17.291386+00:00 | 0.0 |
| econ-detrending-correlation__artifact-generation | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.291863+00:00 | 2026-05-04T13:13:17.292070+00:00 | 0.0 |
| econ-detrending-correlation__analytic-pipeline | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.292579+00:00 | 2026-05-04T13:13:17.292772+00:00 | 0.0 |
| econ-detrending-correlation__engineering-composition | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.293286+00:00 | 2026-05-04T13:13:17.293604+00:00 | 0.0 |
| econ-detrending-correlation__retrieval-heavy-synthesis | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.294162+00:00 | 2026-05-04T13:13:17.294382+00:00 | 0.0 |
| econ-detrending-correlation__environment-control | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.294952+00:00 | 2026-05-04T13:13:17.295155+00:00 | 0.0 |
| econ-detrending-correlation__methodology-guardrail | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.295728+00:00 | 2026-05-04T13:13:17.295927+00:00 | 0.0 |
| econ-detrending-correlation__orchestration-delegation | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.296453+00:00 | 2026-05-04T13:13:17.296648+00:00 | 0.0 |
| exceltable-in-ppt__artifact-generation | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.297170+00:00 | 2026-05-04T13:13:17.297644+00:00 | 0.0 |
| exceltable-in-ppt__analytic-pipeline | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.298451+00:00 | 2026-05-04T13:13:17.298675+00:00 | 0.0 |
| exceltable-in-ppt__engineering-composition | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.299335+00:00 | 2026-05-04T13:13:17.299562+00:00 | 0.0 |
| exceltable-in-ppt__retrieval-heavy-synthesis | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.300135+00:00 | 2026-05-04T13:13:17.300467+00:00 | 0.0 |
| exceltable-in-ppt__environment-control | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.301158+00:00 | 2026-05-04T13:13:17.301388+00:00 | 0.0 |
| exceltable-in-ppt__methodology-guardrail | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.301974+00:00 | 2026-05-04T13:13:17.302178+00:00 | 0.0 |
| exceltable-in-ppt__orchestration-delegation | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.302754+00:00 | 2026-05-04T13:13:17.302962+00:00 | 0.0 |
| find-topk-similiar-chemicals__artifact-generation | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.303550+00:00 | 2026-05-04T13:13:17.303737+00:00 | 0.0 |
| find-topk-similiar-chemicals__analytic-pipeline | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.304285+00:00 | 2026-05-04T13:13:17.304474+00:00 | 0.0 |
| find-topk-similiar-chemicals__engineering-composition | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.305054+00:00 | 2026-05-04T13:13:17.305245+00:00 | 0.0 |
| find-topk-similiar-chemicals__retrieval-heavy-synthesis | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.305863+00:00 | 2026-05-04T13:13:17.306056+00:00 | 0.0 |
| find-topk-similiar-chemicals__environment-control | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.306645+00:00 | 2026-05-04T13:13:17.306850+00:00 | 0.0 |
| find-topk-similiar-chemicals__methodology-guardrail | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.307429+00:00 | 2026-05-04T13:13:17.307620+00:00 | 0.0 |
| find-topk-similiar-chemicals__orchestration-delegation | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.308524+00:00 | 2026-05-04T13:13:17.308789+00:00 | 0.0 |
| fix-druid-loophole-cve__artifact-generation | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.309407+00:00 | 2026-05-04T13:13:17.309615+00:00 | 0.0 |
| fix-druid-loophole-cve__analytic-pipeline | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.310349+00:00 | 2026-05-04T13:13:17.310584+00:00 | 0.0 |
| fix-druid-loophole-cve__engineering-composition | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.311251+00:00 | 2026-05-04T13:13:17.311503+00:00 | 0.0 |
| fix-druid-loophole-cve__retrieval-heavy-synthesis | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.312222+00:00 | 2026-05-04T13:13:17.312430+00:00 | 0.0 |
| fix-druid-loophole-cve__environment-control | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.313062+00:00 | 2026-05-04T13:13:17.313265+00:00 | 0.0 |
| fix-druid-loophole-cve__methodology-guardrail | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.313888+00:00 | 2026-05-04T13:13:17.314069+00:00 | 0.0 |
| fix-druid-loophole-cve__orchestration-delegation | succeeded | 0 | completed | measured | - | no | no | 2026-05-04T13:13:17.314758+00:00 | 2026-05-04T13:13:17.314962+00:00 | 0.0 |

## Pair Details

### adaptive-cruise-control__artifact-generation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T00:12:53.535071+00:00 | 2026-05-02T00:12:53.535577+00:00 | 2026-05-02T00:15:30.063550+00:00 | 2026-05-02T00:23:47.655158+00:00 | continue |
| 1 | 2026-05-02T00:24:16.998983+00:00 | 2026-05-02T00:24:16.999404+00:00 | 2026-05-02T00:27:18.415585+00:00 | 2026-05-02T00:35:36.660580+00:00 | continue |
| 2 | 2026-05-02T00:46:09.384182+00:00 | 2026-05-02T00:46:09.384969+00:00 | 2026-05-02T00:51:22.046757+00:00 | 2026-05-02T00:57:31.593557+00:00 | continue |
| 3 | 2026-05-02T01:07:25.429181+00:00 | 2026-05-02T01:07:25.429451+00:00 | - | - | - |

### adaptive-cruise-control__analytic-pipeline

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T01:21:50.946779+00:00 | 2026-05-02T01:21:50.950847+00:00 | 2026-05-02T01:27:19.271482+00:00 | 2026-05-02T01:35:31.786686+00:00 | continue |
| 1 | 2026-05-02T01:55:17.480885+00:00 | 2026-05-02T01:55:17.482376+00:00 | 2026-05-02T01:58:39.460495+00:00 | 2026-05-02T02:05:00.260236+00:00 | continue |
| 2 | 2026-05-02T02:20:49.997286+00:00 | 2026-05-02T02:20:49.998292+00:00 | 2026-05-02T02:25:10.115100+00:00 | 2026-05-02T02:35:18.768579+00:00 | continue |
| 3 | 2026-05-02T02:44:47.133099+00:00 | 2026-05-02T02:44:47.133103+00:00 | - | - | - |

### adaptive-cruise-control__engineering-composition

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T02:55:31.965434+00:00 | 2026-05-02T02:55:31.965912+00:00 | 2026-05-02T02:59:23.975735+00:00 | 2026-05-02T03:06:55.735005+00:00 | continue |
| 1 | 2026-05-02T03:39:27.291841+00:00 | 2026-05-02T03:39:27.292173+00:00 | 2026-05-02T03:44:03.173550+00:00 | 2026-05-02T03:49:41.270367+00:00 | continue |
| 2 | 2026-05-02T04:21:28.129738+00:00 | 2026-05-02T04:21:28.129958+00:00 | 2026-05-02T04:21:28.130195+00:00 | 2026-05-02T04:28:28.553854+00:00 | continue |
| 3 | 2026-05-02T04:46:01.054369+00:00 | 2026-05-02T04:46:01.054373+00:00 | - | - | - |

### adaptive-cruise-control__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `runtime-blocked`
- diagnosis_note: `Run failed before clean verifier evidence was produced.`
- failure_type: `RuntimeError`
- failure_stage: `r0_perfect_guard`
- failure_round: `None`
- failure_summary: `RuntimeError: expected exactly one trial dir under <repo-root>/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round1-first20-fullmatrix-2026-05-01-1932-candidates/pairs/adaptive-cruise-control__retrieval-heavy-synthesis/refine_run_run-round1-first20-fullmatrix-fallback-2026-05-01-b02/refine/adaptive-cruise-control/rounds/round-0/tune_check/adaptive-cruise-control-round-0-c4-tune, found 0`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | - | - | - | - | - |

### adaptive-cruise-control__environment-control

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T05:56:26.502478+00:00 | 2026-05-02T05:56:26.502732+00:00 | 2026-05-02T06:00:03.113943+00:00 | 2026-05-02T06:08:00.305967+00:00 | continue |
| 1 | 2026-05-02T06:14:49.656470+00:00 | 2026-05-02T06:14:49.656809+00:00 | 2026-05-02T06:18:50.625721+00:00 | 2026-05-02T06:26:44.743038+00:00 | continue |
| 2 | 2026-05-02T06:41:58.173115+00:00 | 2026-05-02T06:41:58.173450+00:00 | 2026-05-02T06:46:09.696975+00:00 | 2026-05-02T06:53:46.736962+00:00 | continue |
| 3 | 2026-05-02T07:03:53.904777+00:00 | 2026-05-02T07:03:53.904780+00:00 | - | - | - |

### adaptive-cruise-control__methodology-guardrail

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T07:12:49.241467+00:00 | 2026-05-02T07:12:49.241963+00:00 | 2026-05-02T07:17:48.167672+00:00 | 2026-05-02T07:27:13.660375+00:00 | continue |
| 1 | 2026-05-02T07:35:52.037909+00:00 | 2026-05-02T07:35:52.038237+00:00 | 2026-05-02T07:40:01.066538+00:00 | 2026-05-02T07:46:29.461639+00:00 | continue |
| 2 | 2026-05-02T07:57:48.551155+00:00 | 2026-05-02T07:57:48.551637+00:00 | 2026-05-02T08:02:43.602755+00:00 | 2026-05-02T08:08:48.728450+00:00 | continue |
| 3 | 2026-05-02T08:18:23.047237+00:00 | 2026-05-02T08:18:23.047241+00:00 | - | - | - |

### adaptive-cruise-control__orchestration-delegation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T08:28:15.496038+00:00 | 2026-05-02T08:28:15.497846+00:00 | 2026-05-02T08:33:02.607154+00:00 | 2026-05-02T08:39:02.457293+00:00 | continue |
| 1 | 2026-05-02T08:54:25.344192+00:00 | 2026-05-02T08:54:25.344553+00:00 | 2026-05-02T08:58:05.857680+00:00 | 2026-05-02T09:04:56.298619+00:00 | continue |
| 2 | 2026-05-02T09:31:52.198266+00:00 | 2026-05-02T09:31:52.198629+00:00 | 2026-05-02T09:35:16.152757+00:00 | 2026-05-02T09:41:52.377772+00:00 | continue |
| 3 | 2026-05-02T09:50:56.243984+00:00 | 2026-05-02T09:50:56.243992+00:00 | - | - | - |

### civ6-adjacency-optimizer__artifact-generation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T09:56:34.309370+00:00 | 2026-05-02T09:56:34.309840+00:00 | 2026-05-02T10:01:09.962119+00:00 | 2026-05-02T10:08:18.954606+00:00 | continue |
| 1 | 2026-05-02T10:50:54.338485+00:00 | 2026-05-02T10:50:54.339025+00:00 | 2026-05-02T10:55:26.007664+00:00 | 2026-05-02T11:02:44.387751+00:00 | continue |
| 2 | 2026-05-02T11:08:47.967947+00:00 | 2026-05-02T11:08:47.968290+00:00 | 2026-05-02T11:12:31.018422+00:00 | 2026-05-02T11:18:17.504911+00:00 | continue |
| 3 | 2026-05-02T11:25:30.454320+00:00 | 2026-05-02T11:25:30.454329+00:00 | - | - | - |

### civ6-adjacency-optimizer__analytic-pipeline

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T11:34:25.642843+00:00 | 2026-05-02T11:34:25.644147+00:00 | 2026-05-02T11:39:31.409805+00:00 | 2026-05-02T11:44:30.284565+00:00 | continue |
| 1 | 2026-05-02T11:48:45.473576+00:00 | 2026-05-02T11:48:45.473963+00:00 | 2026-05-02T11:54:30.279079+00:00 | 2026-05-02T12:00:10.804372+00:00 | continue |
| 2 | 2026-05-02T12:09:03.050444+00:00 | 2026-05-02T12:09:03.050799+00:00 | 2026-05-02T12:14:37.195732+00:00 | 2026-05-02T12:21:45.873875+00:00 | continue |
| 3 | 2026-05-02T12:24:32.016555+00:00 | 2026-05-02T12:24:32.016558+00:00 | - | - | - |

### civ6-adjacency-optimizer__engineering-composition

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T12:32:54.912555+00:00 | 2026-05-02T12:32:54.912941+00:00 | 2026-05-02T12:36:48.830654+00:00 | 2026-05-02T12:42:43.536808+00:00 | continue |
| 1 | 2026-05-02T12:44:34.428668+00:00 | 2026-05-02T12:44:34.429072+00:00 | 2026-05-02T12:48:39.887482+00:00 | 2026-05-02T12:56:55.729572+00:00 | continue |
| 2 | 2026-05-02T13:05:46.791118+00:00 | 2026-05-02T13:05:46.792020+00:00 | 2026-05-02T13:11:36.918797+00:00 | 2026-05-02T13:18:41.267932+00:00 | continue |
| 3 | 2026-05-02T13:25:04.906526+00:00 | 2026-05-02T13:25:04.906534+00:00 | - | - | - |

### civ6-adjacency-optimizer__retrieval-heavy-synthesis

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T13:31:49.718898+00:00 | 2026-05-02T13:31:49.720199+00:00 | 2026-05-02T13:38:28.616826+00:00 | 2026-05-02T13:46:03.036129+00:00 | continue |
| 1 | 2026-05-02T13:53:32.294946+00:00 | 2026-05-02T13:53:32.295298+00:00 | 2026-05-02T13:57:39.689905+00:00 | 2026-05-02T14:02:49.966985+00:00 | continue |
| 2 | 2026-05-02T14:10:53.104925+00:00 | 2026-05-02T14:10:53.106715+00:00 | 2026-05-02T14:15:55.319465+00:00 | 2026-05-02T14:23:30.286414+00:00 | continue |
| 3 | 2026-05-02T14:34:08.785255+00:00 | 2026-05-02T14:34:08.785258+00:00 | - | - | - |

### civ6-adjacency-optimizer__environment-control

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T14:41:04.867506+00:00 | 2026-05-02T14:41:04.867961+00:00 | 2026-05-02T14:44:33.934274+00:00 | 2026-05-02T14:52:42.048934+00:00 | continue |
| 1 | 2026-05-02T14:58:14.072520+00:00 | 2026-05-02T14:58:14.072875+00:00 | 2026-05-02T15:03:02.683183+00:00 | 2026-05-02T15:08:40.395111+00:00 | continue |
| 2 | 2026-05-02T15:14:31.982119+00:00 | 2026-05-02T15:14:31.982473+00:00 | 2026-05-02T15:17:52.657857+00:00 | 2026-05-02T15:26:26.790634+00:00 | continue |
| 3 | 2026-05-02T15:42:01.334838+00:00 | 2026-05-02T15:42:01.334841+00:00 | - | - | - |

### civ6-adjacency-optimizer__methodology-guardrail

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T15:46:53.053581+00:00 | 2026-05-02T15:46:53.055124+00:00 | 2026-05-02T15:51:30.904606+00:00 | 2026-05-02T15:57:28.558834+00:00 | continue |
| 1 | 2026-05-02T16:03:45.478250+00:00 | 2026-05-02T16:03:45.478859+00:00 | 2026-05-02T16:07:19.733006+00:00 | 2026-05-02T16:13:33.334859+00:00 | continue |
| 2 | 2026-05-02T16:20:09.650735+00:00 | 2026-05-02T16:20:09.651240+00:00 | 2026-05-02T16:23:03.420181+00:00 | 2026-05-02T16:30:07.101407+00:00 | continue |
| 3 | 2026-05-02T16:35:20.240504+00:00 | 2026-05-02T16:35:20.240512+00:00 | - | - | - |

### civ6-adjacency-optimizer__orchestration-delegation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T16:37:56.050502+00:00 | 2026-05-02T16:37:56.051079+00:00 | 2026-05-02T16:43:05.395619+00:00 | 2026-05-02T16:51:54.318388+00:00 | continue |
| 1 | 2026-05-02T16:59:05.920566+00:00 | 2026-05-02T16:59:05.921410+00:00 | 2026-05-02T17:04:33.087818+00:00 | 2026-05-02T17:10:50.540906+00:00 | continue |
| 2 | 2026-05-02T17:19:37.060243+00:00 | 2026-05-02T17:19:37.060590+00:00 | 2026-05-02T17:24:12.753579+00:00 | 2026-05-02T17:29:17.715805+00:00 | continue |
| 3 | 2026-05-02T17:36:01.275571+00:00 | 2026-05-02T17:36:01.275575+00:00 | - | - | - |

### data-to-d3__artifact-generation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T17:41:21.630603+00:00 | 2026-05-02T17:41:21.631321+00:00 | 2026-05-02T17:45:12.512932+00:00 | 2026-05-02T17:49:52.457752+00:00 | continue |
| 1 | 2026-05-02T17:53:00.276787+00:00 | 2026-05-02T17:53:00.277161+00:00 | 2026-05-02T17:57:54.316860+00:00 | 2026-05-02T18:02:53.156409+00:00 | continue |
| 2 | 2026-05-02T18:06:07.917804+00:00 | 2026-05-02T18:06:07.918260+00:00 | 2026-05-02T18:09:51.271293+00:00 | 2026-05-02T18:14:27.929627+00:00 | continue |
| 3 | 2026-05-02T18:17:17.784338+00:00 | 2026-05-02T18:17:17.784341+00:00 | - | - | - |

### data-to-d3__analytic-pipeline

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T18:28:05.146780+00:00 | 2026-05-02T18:28:05.149935+00:00 | 2026-05-02T18:33:12.781646+00:00 | 2026-05-02T18:38:18.579887+00:00 | continue |
| 1 | 2026-05-02T18:42:58.286588+00:00 | 2026-05-02T18:42:58.289383+00:00 | 2026-05-02T18:47:54.484483+00:00 | 2026-05-02T18:53:29.574508+00:00 | continue |
| 2 | 2026-05-02T18:56:13.778991+00:00 | 2026-05-02T18:56:13.780047+00:00 | 2026-05-02T18:59:41.320607+00:00 | 2026-05-02T19:05:43.067072+00:00 | continue |
| 3 | 2026-05-02T19:10:58.629451+00:00 | 2026-05-02T19:10:58.629455+00:00 | - | - | - |

### data-to-d3__engineering-composition

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T19:16:26.193721+00:00 | 2026-05-02T19:16:26.194112+00:00 | 2026-05-02T19:20:44.266183+00:00 | 2026-05-02T19:27:10.625762+00:00 | continue |
| 1 | 2026-05-02T19:30:48.180242+00:00 | 2026-05-02T19:30:48.180593+00:00 | 2026-05-02T19:36:50.037712+00:00 | 2026-05-02T19:41:33.072793+00:00 | continue |
| 2 | 2026-05-02T19:44:04.734797+00:00 | 2026-05-02T19:44:04.735503+00:00 | 2026-05-02T19:48:29.927330+00:00 | 2026-05-02T19:54:38.884464+00:00 | continue |
| 3 | 2026-05-02T19:57:23.006804+00:00 | 2026-05-02T19:57:23.006821+00:00 | - | - | - |

### data-to-d3__retrieval-heavy-synthesis

- launcher_status: `succeeded`
- run_status: `completed_with_runtime_failures`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `ambiguous`
- diagnosis_note: `A score exists, but runtime exceptions or failures make it hard to treat as clean evidence.`
- failure_type: `TuneExceptionStats`
- failure_stage: `continue`
- failure_round: `2`
- failure_summary: `RuntimeError=['c4-data-to-d3-round-2__rQFGypY']`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-02T20:03:43.643755+00:00 | 2026-05-02T20:03:43.644147+00:00 | 2026-05-02T20:07:31.541757+00:00 | 2026-05-02T20:11:44.550200+00:00 | continue |
| 1 | 2026-05-02T20:14:23.078200+00:00 | 2026-05-02T20:14:23.078530+00:00 | 2026-05-02T20:20:20.664549+00:00 | 2026-05-02T20:24:47.520208+00:00 | continue |
| 2 | 2026-05-02T20:24:53.724363+00:00 | 2026-05-02T20:24:53.724599+00:00 | 2026-05-02T20:27:37.727484+00:00 | 2026-05-02T20:32:17.752861+00:00 | continue |
| 3 | 2026-05-03T00:33:34.242931+00:00 | 2026-05-03T00:33:34.242965+00:00 | - | - | - |

### data-to-d3__environment-control

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T00:39:53.501773+00:00 | 2026-05-03T00:39:53.502082+00:00 | 2026-05-03T00:45:00.746238+00:00 | 2026-05-03T00:50:32.789184+00:00 | continue |
| 1 | 2026-05-03T00:53:20.820471+00:00 | 2026-05-03T00:53:20.820811+00:00 | 2026-05-03T00:58:40.410533+00:00 | 2026-05-03T01:03:47.445272+00:00 | continue |
| 2 | 2026-05-03T01:06:12.671111+00:00 | 2026-05-03T01:06:12.671343+00:00 | 2026-05-03T01:09:52.443192+00:00 | 2026-05-03T01:14:06.119927+00:00 | continue |
| 3 | 2026-05-03T01:16:46.128468+00:00 | 2026-05-03T01:16:46.128478+00:00 | - | - | - |

### data-to-d3__methodology-guardrail

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T01:19:35.675425+00:00 | 2026-05-03T01:19:35.675713+00:00 | 2026-05-03T01:24:56.122440+00:00 | 2026-05-03T01:30:37.950286+00:00 | continue |
| 1 | 2026-05-03T01:34:23.227114+00:00 | 2026-05-03T01:34:23.227544+00:00 | 2026-05-03T01:38:08.807786+00:00 | 2026-05-03T01:43:18.054033+00:00 | continue |
| 2 | 2026-05-03T01:45:34.622198+00:00 | 2026-05-03T01:45:34.627970+00:00 | 2026-05-03T01:48:22.069073+00:00 | 2026-05-03T01:54:33.803129+00:00 | continue |
| 3 | 2026-05-03T01:57:44.511355+00:00 | 2026-05-03T01:57:44.511363+00:00 | - | - | - |

### data-to-d3__orchestration-delegation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T02:00:49.750542+00:00 | 2026-05-03T02:00:49.750847+00:00 | 2026-05-03T02:05:56.856157+00:00 | 2026-05-03T02:12:27.134262+00:00 | continue |
| 1 | 2026-05-03T02:15:24.732271+00:00 | 2026-05-03T02:15:24.732638+00:00 | 2026-05-03T02:19:30.216102+00:00 | 2026-05-03T02:23:35.664946+00:00 | continue |
| 2 | 2026-05-03T02:26:39.927642+00:00 | 2026-05-03T02:26:39.931124+00:00 | 2026-05-03T02:30:17.234550+00:00 | 2026-05-03T02:34:17.077893+00:00 | continue |
| 3 | 2026-05-03T02:36:58.223329+00:00 | 2026-05-03T02:36:58.223334+00:00 | - | - | - |

### econ-detrending-correlation__artifact-generation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T02:39:34.321957+00:00 | 2026-05-03T02:39:34.322342+00:00 | 2026-05-03T02:43:12.882799+00:00 | 2026-05-03T02:48:22.061652+00:00 | continue |
| 1 | 2026-05-03T02:50:36.223131+00:00 | 2026-05-03T02:50:36.223427+00:00 | 2026-05-03T02:54:44.558607+00:00 | 2026-05-03T03:01:38.368519+00:00 | continue |
| 2 | 2026-05-03T03:03:10.026579+00:00 | 2026-05-03T03:03:10.026876+00:00 | 2026-05-03T03:08:05.349432+00:00 | 2026-05-03T03:15:08.699531+00:00 | continue |
| 3 | 2026-05-03T03:17:52.234413+00:00 | 2026-05-03T03:17:52.234416+00:00 | - | - | - |

### econ-detrending-correlation__analytic-pipeline

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T03:27:26.064807+00:00 | 2026-05-03T03:27:26.065188+00:00 | 2026-05-03T03:31:47.957355+00:00 | 2026-05-03T03:36:52.645012+00:00 | continue |
| 1 | 2026-05-03T03:39:13.828486+00:00 | 2026-05-03T03:39:13.828762+00:00 | 2026-05-03T03:42:18.664658+00:00 | 2026-05-03T03:46:32.714011+00:00 | continue |
| 2 | 2026-05-03T03:48:19.827279+00:00 | 2026-05-03T03:48:19.827544+00:00 | 2026-05-03T03:52:31.544888+00:00 | 2026-05-03T03:56:53.589881+00:00 | continue |
| 3 | 2026-05-03T03:58:18.508189+00:00 | 2026-05-03T03:58:18.508195+00:00 | - | - | - |

### econ-detrending-correlation__engineering-composition

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T04:05:28.163579+00:00 | 2026-05-03T04:05:28.163899+00:00 | 2026-05-03T04:08:27.919282+00:00 | 2026-05-03T04:13:01.602633+00:00 | continue |
| 1 | 2026-05-03T04:15:03.534006+00:00 | 2026-05-03T04:15:03.534236+00:00 | 2026-05-03T04:18:21.242983+00:00 | 2026-05-03T04:25:11.628286+00:00 | continue |
| 2 | 2026-05-03T04:27:21.902674+00:00 | 2026-05-03T04:27:21.902981+00:00 | 2026-05-03T04:31:08.497830+00:00 | 2026-05-03T04:36:24.385022+00:00 | continue |
| 3 | 2026-05-03T04:41:47.726929+00:00 | 2026-05-03T04:41:47.726932+00:00 | - | - | - |

### econ-detrending-correlation__retrieval-heavy-synthesis

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T04:43:32.607100+00:00 | 2026-05-03T04:43:32.607413+00:00 | 2026-05-03T04:46:32.030785+00:00 | 2026-05-03T04:53:06.895314+00:00 | continue |
| 1 | 2026-05-03T04:55:31.629293+00:00 | 2026-05-03T04:55:31.629570+00:00 | 2026-05-03T05:00:20.593658+00:00 | 2026-05-03T05:05:34.918314+00:00 | continue |
| 2 | 2026-05-03T05:07:24.950823+00:00 | 2026-05-03T05:07:24.951103+00:00 | 2026-05-03T05:11:09.929812+00:00 | 2026-05-03T05:15:45.297319+00:00 | continue |
| 3 | 2026-05-03T05:18:57.020894+00:00 | 2026-05-03T05:18:57.020898+00:00 | - | - | - |

### econ-detrending-correlation__environment-control

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T05:21:31.166861+00:00 | 2026-05-03T05:21:31.167201+00:00 | 2026-05-03T05:25:41.564912+00:00 | 2026-05-03T05:32:39.654730+00:00 | continue |
| 1 | 2026-05-03T05:51:53.608546+00:00 | 2026-05-03T05:51:53.608827+00:00 | 2026-05-03T05:57:44.214181+00:00 | 2026-05-03T06:06:02.412515+00:00 | continue |
| 2 | 2026-05-03T06:08:03.468228+00:00 | 2026-05-03T06:08:03.468523+00:00 | 2026-05-03T06:11:36.293815+00:00 | 2026-05-03T06:17:07.413076+00:00 | continue |
| 3 | 2026-05-03T06:19:05.470092+00:00 | 2026-05-03T06:19:05.470095+00:00 | - | - | - |

### econ-detrending-correlation__methodology-guardrail

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T06:25:41.662062+00:00 | 2026-05-03T06:25:41.662371+00:00 | 2026-05-03T06:30:11.470459+00:00 | 2026-05-03T06:36:49.459384+00:00 | continue |
| 1 | 2026-05-03T06:38:56.378682+00:00 | 2026-05-03T06:38:56.378912+00:00 | 2026-05-03T06:42:16.140900+00:00 | 2026-05-03T06:47:14.452019+00:00 | continue |
| 2 | 2026-05-03T06:50:56.060098+00:00 | 2026-05-03T06:50:56.060329+00:00 | 2026-05-03T06:54:32.109402+00:00 | 2026-05-03T07:00:50.707487+00:00 | continue |
| 3 | 2026-05-03T07:04:29.395467+00:00 | 2026-05-03T07:04:29.395471+00:00 | - | - | - |

### econ-detrending-correlation__orchestration-delegation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T07:09:08.655400+00:00 | 2026-05-03T07:09:08.655784+00:00 | 2026-05-03T07:12:31.747546+00:00 | 2026-05-03T07:18:15.212670+00:00 | continue |
| 1 | 2026-05-03T07:20:06.873238+00:00 | 2026-05-03T07:20:06.873474+00:00 | 2026-05-03T07:43:29.356658+00:00 | 2026-05-03T07:49:27.372272+00:00 | continue |
| 2 | 2026-05-03T07:50:55.396974+00:00 | 2026-05-03T07:50:55.397255+00:00 | 2026-05-03T07:54:09.166684+00:00 | 2026-05-03T08:01:16.388286+00:00 | continue |
| 3 | 2026-05-03T08:02:42.564204+00:00 | 2026-05-03T08:02:42.564206+00:00 | - | - | - |

### exceltable-in-ppt__artifact-generation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T08:10:49.443415+00:00 | 2026-05-03T08:10:49.443846+00:00 | 2026-05-03T08:14:33.521710+00:00 | 2026-05-03T08:21:31.188734+00:00 | continue |
| 1 | 2026-05-03T08:43:43.596896+00:00 | 2026-05-03T08:43:43.597113+00:00 | 2026-05-03T08:48:30.723711+00:00 | 2026-05-03T08:53:25.490952+00:00 | continue |
| 2 | 2026-05-03T08:55:50.192610+00:00 | 2026-05-03T08:55:50.192868+00:00 | 2026-05-03T09:01:08.626990+00:00 | 2026-05-03T09:06:59.191886+00:00 | continue |
| 3 | 2026-05-03T09:09:39.210557+00:00 | 2026-05-03T09:09:39.210562+00:00 | - | - | - |

### exceltable-in-ppt__analytic-pipeline

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T09:14:07.303210+00:00 | 2026-05-03T09:14:07.303571+00:00 | 2026-05-03T09:19:00.260740+00:00 | 2026-05-03T09:27:00.534567+00:00 | continue |
| 1 | 2026-05-03T09:29:04.407037+00:00 | 2026-05-03T09:29:04.407389+00:00 | 2026-05-03T09:34:18.025246+00:00 | 2026-05-03T09:42:06.322214+00:00 | continue |
| 2 | 2026-05-03T09:43:54.031969+00:00 | 2026-05-03T09:43:54.032214+00:00 | 2026-05-03T09:46:49.165768+00:00 | 2026-05-03T09:52:10.711349+00:00 | continue |
| 3 | 2026-05-03T09:54:01.452307+00:00 | 2026-05-03T09:54:01.452316+00:00 | - | - | - |

### exceltable-in-ppt__engineering-composition

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T09:59:20.736251+00:00 | 2026-05-03T09:59:20.736584+00:00 | 2026-05-03T10:03:26.465993+00:00 | 2026-05-03T10:12:05.450770+00:00 | continue |
| 1 | 2026-05-03T10:14:12.390915+00:00 | 2026-05-03T10:14:12.391188+00:00 | 2026-05-03T10:18:40.159775+00:00 | 2026-05-03T10:24:37.815291+00:00 | continue |
| 2 | 2026-05-03T10:27:22.057232+00:00 | 2026-05-03T10:27:22.057484+00:00 | 2026-05-03T10:30:34.157198+00:00 | 2026-05-03T10:35:32.287021+00:00 | continue |
| 3 | 2026-05-03T10:38:08.875506+00:00 | 2026-05-03T10:38:08.875509+00:00 | - | - | - |

### exceltable-in-ppt__retrieval-heavy-synthesis

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T10:45:26.098457+00:00 | 2026-05-03T10:45:26.098847+00:00 | 2026-05-03T10:50:52.096337+00:00 | 2026-05-03T10:57:30.491792+00:00 | continue |
| 1 | 2026-05-03T10:59:50.898657+00:00 | 2026-05-03T10:59:50.898904+00:00 | 2026-05-03T11:04:19.340569+00:00 | 2026-05-03T11:11:25.011187+00:00 | continue |
| 2 | 2026-05-03T11:13:30.480744+00:00 | 2026-05-03T11:13:30.481061+00:00 | 2026-05-03T11:16:38.469663+00:00 | 2026-05-03T11:21:41.931116+00:00 | continue |
| 3 | 2026-05-03T11:23:43.308780+00:00 | 2026-05-03T11:23:43.308786+00:00 | - | - | - |

### exceltable-in-ppt__environment-control

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T11:25:47.500853+00:00 | 2026-05-03T11:25:47.501174+00:00 | 2026-05-03T11:30:25.788335+00:00 | 2026-05-03T11:37:02.990619+00:00 | continue |
| 1 | 2026-05-03T11:39:23.068564+00:00 | 2026-05-03T11:39:23.068805+00:00 | 2026-05-03T11:42:40.875346+00:00 | 2026-05-03T11:52:32.511550+00:00 | continue |
| 2 | 2026-05-03T11:54:54.458752+00:00 | 2026-05-03T11:54:54.459115+00:00 | 2026-05-03T11:59:30.923131+00:00 | 2026-05-03T12:04:39.466931+00:00 | continue |
| 3 | 2026-05-03T12:06:34.906618+00:00 | 2026-05-03T12:06:34.906624+00:00 | - | - | - |

### exceltable-in-ppt__methodology-guardrail

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T12:13:08.543178+00:00 | 2026-05-03T12:13:08.543740+00:00 | 2026-05-03T12:16:10.158331+00:00 | 2026-05-03T12:23:09.007116+00:00 | continue |
| 1 | 2026-05-03T12:25:22.282952+00:00 | 2026-05-03T12:25:22.283211+00:00 | 2026-05-03T12:30:05.959865+00:00 | 2026-05-03T12:37:01.791338+00:00 | continue |
| 2 | 2026-05-03T12:39:11.176811+00:00 | 2026-05-03T12:39:11.177072+00:00 | 2026-05-03T12:42:37.758588+00:00 | 2026-05-03T12:47:56.745592+00:00 | continue |
| 3 | 2026-05-03T12:50:03.166355+00:00 | 2026-05-03T12:50:03.166359+00:00 | - | - | - |

### exceltable-in-ppt__orchestration-delegation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T12:57:02.269118+00:00 | 2026-05-03T12:57:02.269469+00:00 | 2026-05-03T13:01:54.429210+00:00 | 2026-05-03T13:08:19.458980+00:00 | continue |
| 1 | 2026-05-03T13:10:58.703282+00:00 | 2026-05-03T13:10:58.703556+00:00 | 2026-05-03T13:15:25.106437+00:00 | 2026-05-03T13:21:18.871928+00:00 | continue |
| 2 | 2026-05-03T13:23:28.468097+00:00 | 2026-05-03T13:23:28.468361+00:00 | 2026-05-03T13:28:16.977596+00:00 | 2026-05-03T13:34:49.987461+00:00 | continue |
| 3 | 2026-05-03T13:36:36.344037+00:00 | 2026-05-03T13:36:36.344045+00:00 | - | - | - |

### find-topk-similiar-chemicals__artifact-generation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T13:44:40.156026+00:00 | 2026-05-03T13:44:40.156414+00:00 | 2026-05-03T13:48:00.954420+00:00 | 2026-05-03T13:53:17.902207+00:00 | continue |
| 1 | 2026-05-03T13:58:29.244634+00:00 | 2026-05-03T13:58:29.245003+00:00 | 2026-05-03T14:02:12.715901+00:00 | 2026-05-03T14:08:51.416435+00:00 | continue |
| 2 | 2026-05-03T14:13:53.719580+00:00 | 2026-05-03T14:13:53.719912+00:00 | 2026-05-03T14:17:37.871163+00:00 | 2026-05-03T14:23:09.949479+00:00 | continue |
| 3 | 2026-05-03T14:24:32.274730+00:00 | 2026-05-03T14:24:32.274733+00:00 | - | - | - |

### find-topk-similiar-chemicals__analytic-pipeline

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T14:41:38.359184+00:00 | 2026-05-03T14:41:38.359586+00:00 | 2026-05-03T14:45:41.455986+00:00 | 2026-05-03T14:51:48.017438+00:00 | continue |
| 1 | 2026-05-03T15:00:29.798682+00:00 | 2026-05-03T15:00:29.798989+00:00 | 2026-05-03T15:05:17.616161+00:00 | 2026-05-03T15:12:16.886875+00:00 | continue |
| 2 | 2026-05-03T15:13:32.297435+00:00 | 2026-05-03T15:13:32.297705+00:00 | 2026-05-03T15:17:03.520059+00:00 | 2026-05-03T15:22:31.146878+00:00 | continue |
| 3 | 2026-05-03T15:26:54.046174+00:00 | 2026-05-03T15:26:54.046177+00:00 | - | - | - |

### find-topk-similiar-chemicals__engineering-composition

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T15:35:56.054706+00:00 | 2026-05-03T15:35:56.055074+00:00 | 2026-05-03T15:39:44.656236+00:00 | 2026-05-03T15:50:42.846906+00:00 | continue |
| 1 | 2026-05-03T15:54:23.364728+00:00 | 2026-05-03T15:54:23.365076+00:00 | 2026-05-03T15:58:36.922477+00:00 | 2026-05-03T16:04:48.091480+00:00 | continue |
| 2 | 2026-05-03T16:10:25.589894+00:00 | 2026-05-03T16:10:25.590235+00:00 | 2026-05-03T16:13:49.284489+00:00 | 2026-05-03T16:19:14.110350+00:00 | continue |
| 3 | 2026-05-03T16:25:04.321167+00:00 | 2026-05-03T16:25:04.321170+00:00 | - | - | - |

### find-topk-similiar-chemicals__retrieval-heavy-synthesis

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T16:31:14.675116+00:00 | 2026-05-03T16:31:14.675397+00:00 | 2026-05-03T16:35:28.759258+00:00 | 2026-05-03T16:41:07.026543+00:00 | continue |
| 1 | 2026-05-03T16:57:07.824436+00:00 | 2026-05-03T16:57:07.824895+00:00 | 2026-05-03T17:01:23.384637+00:00 | 2026-05-03T17:08:35.003210+00:00 | continue |
| 2 | 2026-05-03T17:13:19.430837+00:00 | 2026-05-03T17:13:19.431116+00:00 | 2026-05-03T17:16:03.172079+00:00 | 2026-05-03T17:20:52.024761+00:00 | continue |
| 3 | 2026-05-03T17:26:10.039699+00:00 | 2026-05-03T17:26:10.039703+00:00 | - | - | - |

### find-topk-similiar-chemicals__environment-control

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T17:30:54.987469+00:00 | 2026-05-03T17:30:54.987791+00:00 | 2026-05-03T17:34:11.616396+00:00 | 2026-05-03T17:40:49.954070+00:00 | continue |
| 1 | 2026-05-03T17:46:31.442337+00:00 | 2026-05-03T17:46:31.442687+00:00 | 2026-05-03T17:50:05.853932+00:00 | 2026-05-03T17:56:27.974075+00:00 | continue |
| 2 | 2026-05-03T18:02:10.075300+00:00 | 2026-05-03T18:02:10.075654+00:00 | 2026-05-03T18:05:45.901132+00:00 | 2026-05-03T18:12:04.294254+00:00 | continue |
| 3 | 2026-05-03T18:16:13.523296+00:00 | 2026-05-03T18:16:13.523304+00:00 | - | - | - |

### find-topk-similiar-chemicals__methodology-guardrail

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T18:20:28.296753+00:00 | 2026-05-03T18:20:28.297078+00:00 | 2026-05-03T18:24:09.941536+00:00 | 2026-05-03T18:31:14.730828+00:00 | continue |
| 1 | 2026-05-03T18:39:57.166078+00:00 | 2026-05-03T18:39:57.166341+00:00 | 2026-05-03T18:45:03.290543+00:00 | 2026-05-03T18:50:31.046598+00:00 | continue |
| 2 | 2026-05-03T18:57:22.801498+00:00 | 2026-05-03T18:57:22.801796+00:00 | 2026-05-03T19:01:35.582669+00:00 | 2026-05-03T19:07:36.999091+00:00 | continue |
| 3 | 2026-05-03T19:12:22.408471+00:00 | 2026-05-03T19:12:22.408475+00:00 | - | - | - |

### find-topk-similiar-chemicals__orchestration-delegation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T19:17:17.502312+00:00 | 2026-05-03T19:17:17.502779+00:00 | 2026-05-03T19:21:48.926784+00:00 | 2026-05-03T19:29:42.868381+00:00 | continue |
| 1 | 2026-05-03T19:34:06.689630+00:00 | 2026-05-03T19:34:06.689864+00:00 | 2026-05-03T19:37:08.187499+00:00 | 2026-05-03T19:45:25.847677+00:00 | continue |
| 2 | 2026-05-03T19:51:30.994123+00:00 | 2026-05-03T19:51:30.994387+00:00 | 2026-05-03T19:54:53.041165+00:00 | 2026-05-03T20:02:33.662585+00:00 | continue |
| 3 | 2026-05-03T20:07:13.611062+00:00 | 2026-05-03T20:07:13.611065+00:00 | - | - | - |

### fix-druid-loophole-cve__artifact-generation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T20:25:17.250191+00:00 | 2026-05-03T20:25:17.250626+00:00 | 2026-05-03T20:29:16.978219+00:00 | 2026-05-03T20:38:00.952393+00:00 | continue |
| 1 | 2026-05-03T20:50:11.750134+00:00 | 2026-05-03T20:50:11.750491+00:00 | 2026-05-03T20:53:53.865663+00:00 | 2026-05-03T20:59:56.799366+00:00 | continue |
| 2 | 2026-05-03T21:10:54.214890+00:00 | 2026-05-03T21:10:54.215317+00:00 | 2026-05-03T21:14:06.126224+00:00 | 2026-05-03T21:19:41.617204+00:00 | continue |
| 3 | 2026-05-03T21:33:06.590504+00:00 | 2026-05-03T21:33:06.590507+00:00 | - | - | - |

### fix-druid-loophole-cve__analytic-pipeline

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T21:45:04.386802+00:00 | 2026-05-03T21:45:04.387272+00:00 | 2026-05-03T21:50:02.674242+00:00 | 2026-05-03T21:55:09.278452+00:00 | continue |
| 1 | 2026-05-03T22:07:36.168433+00:00 | 2026-05-03T22:07:36.168821+00:00 | 2026-05-03T22:10:31.692302+00:00 | 2026-05-03T22:16:08.382234+00:00 | continue |
| 2 | 2026-05-03T22:31:13.460816+00:00 | 2026-05-03T22:31:13.461161+00:00 | 2026-05-03T22:34:28.913215+00:00 | 2026-05-03T22:40:04.324647+00:00 | continue |
| 3 | 2026-05-03T22:55:53.526784+00:00 | 2026-05-03T22:55:53.526787+00:00 | - | - | - |

### fix-druid-loophole-cve__engineering-composition

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-03T23:11:21.994902+00:00 | 2026-05-03T23:11:21.995421+00:00 | 2026-05-03T23:17:00.347678+00:00 | 2026-05-03T23:25:59.955781+00:00 | continue |
| 1 | 2026-05-03T23:38:00.277292+00:00 | 2026-05-03T23:38:00.277671+00:00 | 2026-05-03T23:41:34.643469+00:00 | 2026-05-03T23:48:39.073978+00:00 | continue |
| 2 | 2026-05-04T00:00:25.640307+00:00 | 2026-05-04T00:00:25.640704+00:00 | 2026-05-04T00:04:53.137738+00:00 | 2026-05-04T00:10:18.875027+00:00 | continue |
| 3 | 2026-05-04T00:21:51.837541+00:00 | 2026-05-04T00:21:51.837550+00:00 | - | - | - |

### fix-druid-loophole-cve__retrieval-heavy-synthesis

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-04T00:40:26.028550+00:00 | 2026-05-04T00:40:26.029055+00:00 | 2026-05-04T00:44:54.410963+00:00 | 2026-05-04T00:51:29.304061+00:00 | continue |
| 1 | 2026-05-04T01:02:43.845667+00:00 | 2026-05-04T01:02:43.845954+00:00 | 2026-05-04T01:07:45.251800+00:00 | 2026-05-04T01:15:02.918627+00:00 | continue |
| 2 | 2026-05-04T01:26:43.601066+00:00 | 2026-05-04T01:26:43.601454+00:00 | 2026-05-04T01:31:14.198848+00:00 | 2026-05-04T01:39:14.840075+00:00 | continue |
| 3 | 2026-05-04T01:50:18.923134+00:00 | 2026-05-04T01:50:18.923137+00:00 | - | - | - |

### fix-druid-loophole-cve__environment-control

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-04T02:06:00.945510+00:00 | 2026-05-04T02:06:00.945923+00:00 | 2026-05-04T02:12:13.138471+00:00 | 2026-05-04T02:20:37.891117+00:00 | continue |
| 1 | 2026-05-04T02:32:17.180093+00:00 | 2026-05-04T02:32:17.180474+00:00 | 2026-05-04T02:36:22.842666+00:00 | 2026-05-04T02:42:40.270641+00:00 | continue |
| 2 | 2026-05-04T02:55:12.724179+00:00 | 2026-05-04T02:55:12.724533+00:00 | 2026-05-04T02:59:03.208221+00:00 | 2026-05-04T03:04:12.581551+00:00 | continue |
| 3 | 2026-05-04T03:18:15.995177+00:00 | 2026-05-04T03:18:15.995181+00:00 | - | - | - |

### fix-druid-loophole-cve__methodology-guardrail

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-04T03:31:46.160130+00:00 | 2026-05-04T03:31:46.160590+00:00 | 2026-05-04T03:37:24.760146+00:00 | 2026-05-04T03:44:33.282634+00:00 | continue |
| 1 | 2026-05-04T03:57:51.793767+00:00 | 2026-05-04T03:57:51.794135+00:00 | 2026-05-04T04:01:53.810404+00:00 | 2026-05-04T04:07:59.382688+00:00 | continue |
| 2 | 2026-05-04T04:22:08.446589+00:00 | 2026-05-04T04:22:08.447084+00:00 | 2026-05-04T04:25:30.391567+00:00 | 2026-05-04T04:29:45.500751+00:00 | continue |
| 3 | 2026-05-04T04:41:45.836892+00:00 | 2026-05-04T04:41:45.836895+00:00 | - | - | - |

### fix-druid-loophole-cve__orchestration-delegation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- evidence_class: `measured`
- diagnosis_note: `Clean verifier-facing score available for comparison against C0/C1.`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-05-04T04:53:26.649250+00:00 | 2026-05-04T04:53:26.649665+00:00 | 2026-05-04T04:57:51.067051+00:00 | 2026-05-04T05:04:53.080737+00:00 | continue |
| 1 | 2026-05-04T05:19:50.454321+00:00 | 2026-05-04T05:19:50.454643+00:00 | 2026-05-04T05:22:53.553726+00:00 | 2026-05-04T05:28:29.710460+00:00 | continue |
| 2 | 2026-05-04T05:41:52.483622+00:00 | 2026-05-04T05:41:52.483979+00:00 | 2026-05-04T05:44:59.934773+00:00 | 2026-05-04T05:50:14.295938+00:00 | continue |
| 3 | 2026-05-04T06:02:31.765352+00:00 | 2026-05-04T06:02:31.765355+00:00 | - | - | - |
