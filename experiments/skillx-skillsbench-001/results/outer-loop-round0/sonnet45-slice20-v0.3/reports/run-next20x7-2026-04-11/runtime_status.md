# SkillX Round0 Runtime Status: `run-next20x7-2026-04-11`

| Pair | Launcher | Return | Run | Failure | Timeout | Early Stop | Started | Finished | Duration (s) |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | ---: |
| citation-check__artifact-generation | succeeded | 0 | completed | - | no | no | 2026-04-11T09:38:28.775149+00:00 | 2026-04-11T10:21:37.969402+00:00 | 2589.2 |
| citation-check__analytic-pipeline | succeeded | 0 | completed | - | no | no | 2026-04-11T10:21:37.975851+00:00 | 2026-04-11T11:03:27.355742+00:00 | 2509.4 |
| citation-check__engineering-composition | succeeded | 0 | completed | - | no | no | 2026-04-11T11:03:27.359001+00:00 | 2026-04-11T11:43:20.925055+00:00 | 2393.6 |
| citation-check__retrieval-heavy-synthesis | succeeded | 0 | completed | - | no | no | 2026-04-11T11:43:20.927858+00:00 | 2026-04-11T12:29:15.716277+00:00 | 2754.8 |
| citation-check__environment-control | succeeded | 0 | completed | - | no | no | 2026-04-11T12:29:15.718551+00:00 | 2026-04-11T13:14:01.724150+00:00 | 2686.0 |
| citation-check__methodology-guardrail | succeeded | 0 | completed | - | no | no | 2026-04-11T13:14:01.732670+00:00 | 2026-04-11T13:57:20.466503+00:00 | 2598.7 |
| citation-check__orchestration-delegation | succeeded | 0 | completed | - | no | no | 2026-04-11T13:57:20.472805+00:00 | 2026-04-11T14:42:51.053294+00:00 | 2730.6 |
| powerlifting-coef-calc__artifact-generation | succeeded | 0 | completed | - | no | no | 2026-04-11T14:42:51.055114+00:00 | 2026-04-11T15:21:36.592350+00:00 | 2325.5 |
| powerlifting-coef-calc__analytic-pipeline | succeeded | 0 | completed | - | no | no | 2026-04-11T15:21:36.599182+00:00 | 2026-04-11T15:57:45.770407+00:00 | 2169.2 |
| powerlifting-coef-calc__engineering-composition | succeeded | 0 | completed | - | no | no | 2026-04-11T15:57:45.776818+00:00 | 2026-04-11T16:39:51.258810+00:00 | 2525.5 |
| powerlifting-coef-calc__retrieval-heavy-synthesis | succeeded | 0 | completed | - | no | no | 2026-04-11T16:39:51.265380+00:00 | 2026-04-11T17:39:22.727781+00:00 | 3571.5 |
| powerlifting-coef-calc__environment-control | succeeded | 0 | completed | - | no | no | 2026-04-11T17:39:22.734829+00:00 | 2026-04-11T18:17:08.193686+00:00 | 2265.5 |
| powerlifting-coef-calc__methodology-guardrail | succeeded | 0 | completed | - | no | no | 2026-04-11T18:17:08.201023+00:00 | 2026-04-11T18:55:00.856501+00:00 | 2272.7 |
| powerlifting-coef-calc__orchestration-delegation | succeeded | 0 | completed | - | no | no | 2026-04-11T18:55:00.864864+00:00 | 2026-04-11T19:31:31.610353+00:00 | 2190.7 |
| spring-boot-jakarta-migration__artifact-generation | succeeded | 0 | completed | - | no | no | 2026-04-11T19:31:31.617091+00:00 | 2026-04-11T20:34:06.793025+00:00 | 3755.2 |
| spring-boot-jakarta-migration__analytic-pipeline | succeeded | 0 | completed | - | no | no | 2026-04-11T20:34:06.798090+00:00 | 2026-04-11T21:28:44.631245+00:00 | 3277.8 |
| spring-boot-jakarta-migration__engineering-composition | succeeded | 0 | completed | - | no | no | 2026-04-11T21:28:44.634195+00:00 | 2026-04-11T22:26:36.637772+00:00 | 3472.0 |
| spring-boot-jakarta-migration__retrieval-heavy-synthesis | succeeded | 0 | completed | RuntimeError=['c4-spring-boot-jakarta-migration__EX3ui3T'] | no | no | 2026-04-11T22:26:36.646165+00:00 | 2026-04-11T22:59:50.631996+00:00 | 1994.0 |
| spring-boot-jakarta-migration__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T22:59:50.635329+00:00 | 2026-04-11T22:59:56.967704+00:00 | 6.3 |
| spring-boot-jakarta-migration__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T22:59:56.968233+00:00 | 2026-04-11T23:00:03.190504+00:00 | 6.2 |
| spring-boot-jakarta-migration__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:00:03.192321+00:00 | 2026-04-11T23:00:09.424123+00:00 | 6.2 |
| trend-anomaly-causal-inference__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:00:09.425395+00:00 | 2026-04-11T23:00:15.653863+00:00 | 6.2 |
| trend-anomaly-causal-inference__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:00:15.655922+00:00 | 2026-04-11T23:00:21.874408+00:00 | 6.2 |
| trend-anomaly-causal-inference__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:00:21.876625+00:00 | 2026-04-11T23:00:28.124306+00:00 | 6.2 |
| trend-anomaly-causal-inference__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:00:28.125282+00:00 | 2026-04-11T23:00:34.351110+00:00 | 6.2 |
| trend-anomaly-causal-inference__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:00:34.352952+00:00 | 2026-04-11T23:00:40.580104+00:00 | 6.2 |
| trend-anomaly-causal-inference__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:00:40.581325+00:00 | 2026-04-11T23:00:46.806757+00:00 | 6.2 |
| trend-anomaly-causal-inference__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:00:46.807330+00:00 | 2026-04-11T23:00:53.016714+00:00 | 6.2 |
| sec-financial-report__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:00:53.017647+00:00 | 2026-04-11T23:00:59.265050+00:00 | 6.2 |
| sec-financial-report__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:00:59.266136+00:00 | 2026-04-11T23:01:05.488565+00:00 | 6.2 |
| sec-financial-report__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:01:05.489234+00:00 | 2026-04-11T23:01:11.722838+00:00 | 6.2 |
| sec-financial-report__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:01:11.723443+00:00 | 2026-04-11T23:01:17.738294+00:00 | 6.0 |
| sec-financial-report__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:01:17.738924+00:00 | 2026-04-11T23:01:23.941914+00:00 | 6.2 |
| sec-financial-report__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:01:23.942519+00:00 | 2026-04-11T23:01:30.151928+00:00 | 6.2 |
| sec-financial-report__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:01:30.152693+00:00 | 2026-04-11T23:01:36.374192+00:00 | 6.2 |
| virtualhome-agent-planning__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:01:36.374924+00:00 | 2026-04-11T23:01:42.607503+00:00 | 6.2 |
| virtualhome-agent-planning__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:01:42.608138+00:00 | 2026-04-11T23:01:48.830187+00:00 | 6.2 |
| virtualhome-agent-planning__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:01:48.830811+00:00 | 2026-04-11T23:01:55.058425+00:00 | 6.2 |
| virtualhome-agent-planning__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:01:55.059112+00:00 | 2026-04-11T23:02:01.270816+00:00 | 6.2 |
| virtualhome-agent-planning__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:02:01.271779+00:00 | 2026-04-11T23:02:07.285888+00:00 | 6.0 |
| virtualhome-agent-planning__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:02:07.286540+00:00 | 2026-04-11T23:02:13.507717+00:00 | 6.2 |
| virtualhome-agent-planning__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:02:13.508468+00:00 | 2026-04-11T23:02:19.725763+00:00 | 6.2 |
| 3d-scan-calc__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:02:19.726420+00:00 | 2026-04-11T23:02:25.938323+00:00 | 6.2 |
| 3d-scan-calc__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:02:25.939018+00:00 | 2026-04-11T23:02:32.144863+00:00 | 6.2 |
| 3d-scan-calc__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:02:32.145555+00:00 | 2026-04-11T23:02:38.356716+00:00 | 6.2 |
| 3d-scan-calc__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:02:38.357375+00:00 | 2026-04-11T23:02:44.596747+00:00 | 6.2 |
| 3d-scan-calc__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:02:44.597448+00:00 | 2026-04-11T23:02:50.801218+00:00 | 6.2 |
| 3d-scan-calc__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:02:50.802229+00:00 | 2026-04-11T23:02:57.013434+00:00 | 6.2 |
| 3d-scan-calc__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:02:57.014560+00:00 | 2026-04-11T23:03:03.249364+00:00 | 6.2 |
| data-to-d3__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:03:03.250144+00:00 | 2026-04-11T23:03:09.458220+00:00 | 6.2 |
| data-to-d3__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:03:09.459939+00:00 | 2026-04-11T23:03:15.692926+00:00 | 6.2 |
| data-to-d3__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:03:15.693988+00:00 | 2026-04-11T23:03:21.909460+00:00 | 6.2 |
| data-to-d3__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:03:21.912889+00:00 | 2026-04-11T23:03:28.148413+00:00 | 6.2 |
| data-to-d3__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:03:28.149213+00:00 | 2026-04-11T23:03:34.388054+00:00 | 6.2 |
| data-to-d3__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:03:34.388793+00:00 | 2026-04-11T23:03:40.599842+00:00 | 6.2 |
| data-to-d3__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:03:40.600578+00:00 | 2026-04-11T23:03:46.611807+00:00 | 6.0 |
| fix-druid-loophole-cve__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:03:46.612570+00:00 | 2026-04-11T23:03:52.818529+00:00 | 6.2 |
| fix-druid-loophole-cve__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:03:52.819314+00:00 | 2026-04-11T23:03:59.053209+00:00 | 6.2 |
| fix-druid-loophole-cve__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:03:59.053998+00:00 | 2026-04-11T23:04:05.289728+00:00 | 6.2 |
| fix-druid-loophole-cve__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:04:05.290572+00:00 | 2026-04-11T23:04:11.537120+00:00 | 6.2 |
| fix-druid-loophole-cve__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:04:11.537941+00:00 | 2026-04-11T23:04:17.740256+00:00 | 6.2 |
| fix-druid-loophole-cve__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:04:17.741095+00:00 | 2026-04-11T23:04:23.951532+00:00 | 6.2 |
| fix-druid-loophole-cve__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:04:23.952350+00:00 | 2026-04-11T23:04:30.163853+00:00 | 6.2 |
| reserves-at-risk-calc__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:04:30.164691+00:00 | 2026-04-11T23:04:36.392253+00:00 | 6.2 |
| reserves-at-risk-calc__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:04:36.393454+00:00 | 2026-04-11T23:04:42.615614+00:00 | 6.2 |
| reserves-at-risk-calc__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:04:42.616473+00:00 | 2026-04-11T23:04:48.862040+00:00 | 6.2 |
| reserves-at-risk-calc__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:04:48.863035+00:00 | 2026-04-11T23:04:55.082185+00:00 | 6.2 |
| reserves-at-risk-calc__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:04:55.083283+00:00 | 2026-04-11T23:05:01.333182+00:00 | 6.2 |
| reserves-at-risk-calc__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:05:01.334035+00:00 | 2026-04-11T23:05:07.542948+00:00 | 6.2 |
| reserves-at-risk-calc__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:05:07.543854+00:00 | 2026-04-11T23:05:13.766415+00:00 | 6.2 |
| mars-clouds-clustering__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:05:13.767267+00:00 | 2026-04-11T23:05:19.982605+00:00 | 6.2 |
| mars-clouds-clustering__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:05:19.983464+00:00 | 2026-04-11T23:05:26.191908+00:00 | 6.2 |
| mars-clouds-clustering__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:05:26.193062+00:00 | 2026-04-11T23:05:32.416156+00:00 | 6.2 |
| mars-clouds-clustering__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:05:32.417075+00:00 | 2026-04-11T23:05:38.626699+00:00 | 6.2 |
| mars-clouds-clustering__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:05:38.627593+00:00 | 2026-04-11T23:05:44.845084+00:00 | 6.2 |
| mars-clouds-clustering__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:05:44.847371+00:00 | 2026-04-11T23:05:50.854033+00:00 | 6.0 |
| mars-clouds-clustering__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:05:50.855452+00:00 | 2026-04-11T23:05:56.878825+00:00 | 6.0 |
| exceltable-in-ppt__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:05:56.879786+00:00 | 2026-04-11T23:06:03.104969+00:00 | 6.2 |
| exceltable-in-ppt__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:06:03.105867+00:00 | 2026-04-11T23:06:09.319832+00:00 | 6.2 |
| exceltable-in-ppt__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:06:09.320771+00:00 | 2026-04-11T23:06:15.542996+00:00 | 6.2 |
| exceltable-in-ppt__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:06:15.543943+00:00 | 2026-04-11T23:06:21.761237+00:00 | 6.2 |
| exceltable-in-ppt__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:06:21.762138+00:00 | 2026-04-11T23:06:27.979268+00:00 | 6.2 |
| exceltable-in-ppt__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:06:27.980231+00:00 | 2026-04-11T23:06:34.209597+00:00 | 6.2 |
| exceltable-in-ppt__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:06:34.210730+00:00 | 2026-04-11T23:06:40.328538+00:00 | 6.1 |
| simpo-code-reproduction__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:06:40.329593+00:00 | 2026-04-11T23:06:46.342626+00:00 | 6.0 |
| simpo-code-reproduction__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:06:46.343561+00:00 | 2026-04-11T23:06:52.364549+00:00 | 6.0 |
| simpo-code-reproduction__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:06:52.365492+00:00 | 2026-04-11T23:06:58.377289+00:00 | 6.0 |
| simpo-code-reproduction__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:06:58.378240+00:00 | 2026-04-11T23:07:04.396605+00:00 | 6.0 |
| simpo-code-reproduction__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:07:04.397804+00:00 | 2026-04-11T23:07:10.422367+00:00 | 6.0 |
| simpo-code-reproduction__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:07:10.424418+00:00 | 2026-04-11T23:07:16.438993+00:00 | 6.0 |
| simpo-code-reproduction__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:07:16.440002+00:00 | 2026-04-11T23:07:22.453854+00:00 | 6.0 |
| shock-analysis-demand__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:07:22.454892+00:00 | 2026-04-11T23:07:28.475285+00:00 | 6.0 |
| shock-analysis-demand__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:07:28.477004+00:00 | 2026-04-11T23:07:34.490533+00:00 | 6.0 |
| shock-analysis-demand__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:07:34.491531+00:00 | 2026-04-11T23:07:40.508307+00:00 | 6.0 |
| shock-analysis-demand__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:07:40.509330+00:00 | 2026-04-11T23:07:46.518196+00:00 | 6.0 |
| shock-analysis-demand__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:07:46.519246+00:00 | 2026-04-11T23:07:52.547848+00:00 | 6.0 |
| shock-analysis-demand__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:07:52.549552+00:00 | 2026-04-11T23:07:58.561069+00:00 | 6.0 |
| shock-analysis-demand__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:07:58.562174+00:00 | 2026-04-11T23:08:04.577583+00:00 | 6.0 |
| multilingual-video-dubbing__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:08:04.578644+00:00 | 2026-04-11T23:08:10.590547+00:00 | 6.0 |
| multilingual-video-dubbing__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:08:10.591624+00:00 | 2026-04-11T23:08:16.596649+00:00 | 6.0 |
| multilingual-video-dubbing__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:08:16.597702+00:00 | 2026-04-11T23:08:22.609408+00:00 | 6.0 |
| multilingual-video-dubbing__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:08:22.610492+00:00 | 2026-04-11T23:08:28.620145+00:00 | 6.0 |
| multilingual-video-dubbing__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:08:28.621263+00:00 | 2026-04-11T23:08:34.638029+00:00 | 6.0 |
| multilingual-video-dubbing__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:08:34.639195+00:00 | 2026-04-11T23:08:40.658429+00:00 | 6.0 |
| multilingual-video-dubbing__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:08:40.659950+00:00 | 2026-04-11T23:08:46.928770+00:00 | 6.3 |
| offer-letter-generator__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:08:46.930818+00:00 | 2026-04-11T23:08:52.932124+00:00 | 6.0 |
| offer-letter-generator__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:08:52.933263+00:00 | 2026-04-11T23:08:59.173576+00:00 | 6.2 |
| offer-letter-generator__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:08:59.174901+00:00 | 2026-04-11T23:09:05.174746+00:00 | 6.0 |
| offer-letter-generator__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:09:05.176290+00:00 | 2026-04-11T23:09:11.419812+00:00 | 6.2 |
| offer-letter-generator__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:09:11.420955+00:00 | 2026-04-11T23:09:17.430625+00:00 | 6.0 |
| offer-letter-generator__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:09:17.431783+00:00 | 2026-04-11T23:09:23.679648+00:00 | 6.2 |
| offer-letter-generator__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:09:23.680926+00:00 | 2026-04-11T23:09:30.008163+00:00 | 6.3 |
| fix-build-agentops__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:09:30.009512+00:00 | 2026-04-11T23:09:36.245775+00:00 | 6.2 |
| fix-build-agentops__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:09:36.247098+00:00 | 2026-04-11T23:09:42.510138+00:00 | 6.3 |
| fix-build-agentops__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:09:42.511402+00:00 | 2026-04-11T23:09:48.786199+00:00 | 6.3 |
| fix-build-agentops__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:09:48.787824+00:00 | 2026-04-11T23:09:55.034256+00:00 | 6.2 |
| fix-build-agentops__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:09:55.035458+00:00 | 2026-04-11T23:10:01.052647+00:00 | 6.0 |
| fix-build-agentops__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:10:01.053912+00:00 | 2026-04-11T23:10:07.287092+00:00 | 6.2 |
| fix-build-agentops__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:10:07.288349+00:00 | 2026-04-11T23:10:13.524248+00:00 | 6.2 |
| shock-analysis-supply__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:10:13.525633+00:00 | 2026-04-11T23:10:19.790394+00:00 | 6.3 |
| shock-analysis-supply__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:10:19.791678+00:00 | 2026-04-11T23:10:25.789334+00:00 | 6.0 |
| shock-analysis-supply__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:10:25.790739+00:00 | 2026-04-11T23:10:32.052932+00:00 | 6.3 |
| shock-analysis-supply__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:10:32.054242+00:00 | 2026-04-11T23:10:38.057027+00:00 | 6.0 |
| shock-analysis-supply__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:10:38.059201+00:00 | 2026-04-11T23:10:44.286260+00:00 | 6.2 |
| shock-analysis-supply__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:10:44.288355+00:00 | 2026-04-11T23:10:50.311942+00:00 | 6.0 |
| shock-analysis-supply__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:10:50.313274+00:00 | 2026-04-11T23:10:56.553961+00:00 | 6.2 |
| lab-unit-harmonization__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:10:56.555232+00:00 | 2026-04-11T23:11:02.565825+00:00 | 6.0 |
| lab-unit-harmonization__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:11:02.567095+00:00 | 2026-04-11T23:11:08.806812+00:00 | 6.2 |
| lab-unit-harmonization__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:11:08.808183+00:00 | 2026-04-11T23:11:15.039492+00:00 | 6.2 |
| lab-unit-harmonization__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:11:15.040795+00:00 | 2026-04-11T23:11:21.281188+00:00 | 6.2 |
| lab-unit-harmonization__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:11:21.282514+00:00 | 2026-04-11T23:11:27.547533+00:00 | 6.3 |
| lab-unit-harmonization__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:11:27.549072+00:00 | 2026-04-11T23:11:33.802551+00:00 | 6.3 |
| lab-unit-harmonization__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:11:33.804817+00:00 | 2026-04-11T23:11:40.058245+00:00 | 6.3 |
| protein-expression-analysis__artifact-generation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:11:40.060394+00:00 | 2026-04-11T23:11:46.070309+00:00 | 6.0 |
| protein-expression-analysis__analytic-pipeline | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:11:46.071586+00:00 | 2026-04-11T23:11:52.311819+00:00 | 6.2 |
| protein-expression-analysis__engineering-composition | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:11:52.313161+00:00 | 2026-04-11T23:11:58.568245+00:00 | 6.3 |
| protein-expression-analysis__retrieval-heavy-synthesis | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:11:58.569563+00:00 | 2026-04-11T23:12:04.864761+00:00 | 6.3 |
| protein-expression-analysis__environment-control | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:12:04.866629+00:00 | 2026-04-11T23:12:10.897347+00:00 | 6.0 |
| protein-expression-analysis__methodology-guardrail | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:12:10.898902+00:00 | 2026-04-11T23:12:17.143232+00:00 | 6.2 |
| protein-expression-analysis__orchestration-delegation | failed | 1 | failed | RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes | no | no | 2026-04-11T23:12:17.144677+00:00 | 2026-04-11T23:12:23.384207+00:00 | 6.2 |

## Pair Details

### citation-check__artifact-generation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T09:42:17.278964+00:00 | 2026-04-11T09:42:17.279444+00:00 | 2026-04-11T09:45:41.161670+00:00 | 2026-04-11T09:51:56.788496+00:00 | continue |
| 1 | 2026-04-11T09:54:59.828191+00:00 | 2026-04-11T09:54:59.828457+00:00 | 2026-04-11T09:59:12.078310+00:00 | 2026-04-11T10:05:44.576153+00:00 | continue |
| 2 | 2026-04-11T10:09:00.196229+00:00 | 2026-04-11T10:09:00.196624+00:00 | 2026-04-11T10:12:10.620570+00:00 | 2026-04-11T10:17:50.101549+00:00 | continue |
| 3 | 2026-04-11T10:21:37.909142+00:00 | 2026-04-11T10:21:37.909147+00:00 | - | - | - |

### citation-check__analytic-pipeline

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T10:26:14.988902+00:00 | 2026-04-11T10:26:14.989188+00:00 | 2026-04-11T10:29:08.884507+00:00 | 2026-04-11T10:34:28.210412+00:00 | continue |
| 1 | 2026-04-11T10:39:00.188601+00:00 | 2026-04-11T10:39:00.188856+00:00 | 2026-04-11T10:42:09.913076+00:00 | 2026-04-11T10:48:24.853774+00:00 | continue |
| 2 | 2026-04-11T10:51:51.422580+00:00 | 2026-04-11T10:51:51.422992+00:00 | 2026-04-11T10:54:38.710452+00:00 | 2026-04-11T11:00:33.473166+00:00 | continue |
| 3 | 2026-04-11T11:03:27.306564+00:00 | 2026-04-11T11:03:27.306569+00:00 | - | - | - |

### citation-check__engineering-composition

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T11:07:35.545789+00:00 | 2026-04-11T11:07:35.546137+00:00 | 2026-04-11T11:11:20.223567+00:00 | 2026-04-11T11:16:03.296023+00:00 | continue |
| 1 | 2026-04-11T11:19:05.456237+00:00 | 2026-04-11T11:19:05.456631+00:00 | 2026-04-11T11:22:08.794036+00:00 | 2026-04-11T11:27:35.435238+00:00 | continue |
| 2 | 2026-04-11T11:30:47.216250+00:00 | 2026-04-11T11:30:47.216587+00:00 | 2026-04-11T11:34:13.241955+00:00 | 2026-04-11T11:39:52.381832+00:00 | continue |
| 3 | 2026-04-11T11:43:20.894328+00:00 | 2026-04-11T11:43:20.894334+00:00 | - | - | - |

### citation-check__retrieval-heavy-synthesis

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T11:47:06.781316+00:00 | 2026-04-11T11:47:06.781705+00:00 | 2026-04-11T11:51:33.621736+00:00 | 2026-04-11T11:57:58.728520+00:00 | continue |
| 1 | 2026-04-11T12:01:29.992537+00:00 | 2026-04-11T12:01:29.992773+00:00 | 2026-04-11T12:04:17.246612+00:00 | 2026-04-11T12:10:46.714472+00:00 | continue |
| 2 | 2026-04-11T12:15:01.477173+00:00 | 2026-04-11T12:15:01.477527+00:00 | 2026-04-11T12:17:52.014955+00:00 | 2026-04-11T12:24:41.175053+00:00 | continue |
| 3 | 2026-04-11T12:29:15.689782+00:00 | 2026-04-11T12:29:15.689786+00:00 | - | - | - |

### citation-check__environment-control

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T12:33:34.968412+00:00 | 2026-04-11T12:33:34.968871+00:00 | 2026-04-11T12:37:14.787082+00:00 | 2026-04-11T12:46:25.211873+00:00 | continue |
| 1 | 2026-04-11T12:49:25.334836+00:00 | 2026-04-11T12:49:25.335746+00:00 | 2026-04-11T12:53:29.059356+00:00 | 2026-04-11T12:59:12.504781+00:00 | continue |
| 2 | 2026-04-11T13:01:38.771853+00:00 | 2026-04-11T13:01:38.772139+00:00 | 2026-04-11T13:05:17.482039+00:00 | 2026-04-11T13:11:27.616818+00:00 | continue |
| 3 | 2026-04-11T13:14:01.683021+00:00 | 2026-04-11T13:14:01.683025+00:00 | - | - | - |

### citation-check__methodology-guardrail

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T13:17:07.875990+00:00 | 2026-04-11T13:17:07.876430+00:00 | 2026-04-11T13:21:07.016636+00:00 | 2026-04-11T13:29:11.436816+00:00 | continue |
| 1 | 2026-04-11T13:32:25.613185+00:00 | 2026-04-11T13:32:25.613556+00:00 | 2026-04-11T13:35:18.600134+00:00 | 2026-04-11T13:40:35.657912+00:00 | continue |
| 2 | 2026-04-11T13:43:53.817617+00:00 | 2026-04-11T13:43:53.818648+00:00 | 2026-04-11T13:47:25.862885+00:00 | 2026-04-11T13:54:16.448017+00:00 | continue |
| 3 | 2026-04-11T13:57:20.430353+00:00 | 2026-04-11T13:57:20.430360+00:00 | - | - | - |

### citation-check__orchestration-delegation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T14:00:29.906385+00:00 | 2026-04-11T14:00:29.906661+00:00 | 2026-04-11T14:04:18.718221+00:00 | 2026-04-11T14:14:46.410474+00:00 | continue |
| 1 | 2026-04-11T14:18:23.304473+00:00 | 2026-04-11T14:18:23.304739+00:00 | 2026-04-11T14:21:30.822277+00:00 | 2026-04-11T14:26:31.592477+00:00 | continue |
| 2 | 2026-04-11T14:30:12.125020+00:00 | 2026-04-11T14:30:12.125333+00:00 | 2026-04-11T14:33:56.877928+00:00 | 2026-04-11T14:40:01.958750+00:00 | continue |
| 3 | 2026-04-11T14:42:51.022003+00:00 | 2026-04-11T14:42:51.022009+00:00 | - | - | - |

### powerlifting-coef-calc__artifact-generation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T14:48:13.777445+00:00 | 2026-04-11T14:48:13.777967+00:00 | 2026-04-11T14:51:49.420874+00:00 | 2026-04-11T14:58:11.704592+00:00 | continue |
| 1 | 2026-04-11T15:00:13.043384+00:00 | 2026-04-11T15:00:13.043693+00:00 | 2026-04-11T15:03:07.846174+00:00 | 2026-04-11T15:07:47.267000+00:00 | continue |
| 2 | 2026-04-11T15:10:15.632591+00:00 | 2026-04-11T15:10:15.632901+00:00 | 2026-04-11T15:14:30.852127+00:00 | 2026-04-11T15:19:39.295161+00:00 | continue |
| 3 | 2026-04-11T15:21:36.529618+00:00 | 2026-04-11T15:21:36.529625+00:00 | - | - | - |

### powerlifting-coef-calc__analytic-pipeline

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T15:23:52.258376+00:00 | 2026-04-11T15:23:52.258804+00:00 | 2026-04-11T15:27:38.188800+00:00 | 2026-04-11T15:34:32.309461+00:00 | continue |
| 1 | 2026-04-11T15:36:22.938152+00:00 | 2026-04-11T15:36:22.938453+00:00 | 2026-04-11T15:39:10.448892+00:00 | 2026-04-11T15:45:13.978102+00:00 | continue |
| 2 | 2026-04-11T15:47:04.138316+00:00 | 2026-04-11T15:47:04.138653+00:00 | 2026-04-11T15:50:10.716365+00:00 | 2026-04-11T15:55:54.892011+00:00 | continue |
| 3 | 2026-04-11T15:57:45.720286+00:00 | 2026-04-11T15:57:45.720291+00:00 | - | - | - |

### powerlifting-coef-calc__engineering-composition

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T16:00:29.335741+00:00 | 2026-04-11T16:00:29.336134+00:00 | 2026-04-11T16:03:57.055982+00:00 | 2026-04-11T16:09:55.275358+00:00 | continue |
| 1 | 2026-04-11T16:11:56.848538+00:00 | 2026-04-11T16:11:56.848829+00:00 | 2026-04-11T16:15:08.263042+00:00 | 2026-04-11T16:23:30.751830+00:00 | continue |
| 2 | 2026-04-11T16:26:16.552563+00:00 | 2026-04-11T16:26:16.552984+00:00 | 2026-04-11T16:30:56.675099+00:00 | 2026-04-11T16:37:37.491078+00:00 | continue |
| 3 | 2026-04-11T16:39:51.213054+00:00 | 2026-04-11T16:39:51.213062+00:00 | - | - | - |

### powerlifting-coef-calc__retrieval-heavy-synthesis

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T16:42:37.590051+00:00 | 2026-04-11T16:42:37.590453+00:00 | 2026-04-11T16:46:36.627234+00:00 | 2026-04-11T16:54:24.862540+00:00 | continue |
| 1 | 2026-04-11T16:56:44.892035+00:00 | 2026-04-11T16:56:44.892368+00:00 | 2026-04-11T16:59:57.371856+00:00 | 2026-04-11T17:06:08.563128+00:00 | continue |
| 2 | 2026-04-11T17:08:48.427748+00:00 | 2026-04-11T17:08:48.428142+00:00 | 2026-04-11T17:12:22.325563+00:00 | 2026-04-11T17:37:23.228075+00:00 | continue |
| 3 | 2026-04-11T17:39:22.676101+00:00 | 2026-04-11T17:39:22.676110+00:00 | - | - | - |

### powerlifting-coef-calc__environment-control

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T17:41:41.983266+00:00 | 2026-04-11T17:41:41.983690+00:00 | 2026-04-11T17:45:04.354639+00:00 | 2026-04-11T17:50:48.695086+00:00 | continue |
| 1 | 2026-04-11T17:52:57.489818+00:00 | 2026-04-11T17:52:57.490108+00:00 | 2026-04-11T17:56:25.155218+00:00 | 2026-04-11T18:06:12.016168+00:00 | continue |
| 2 | 2026-04-11T18:08:00.812270+00:00 | 2026-04-11T18:08:00.812556+00:00 | 2026-04-11T18:11:01.237881+00:00 | 2026-04-11T18:15:21.604547+00:00 | continue |
| 3 | 2026-04-11T18:17:08.147072+00:00 | 2026-04-11T18:17:08.147078+00:00 | - | - | - |

### powerlifting-coef-calc__methodology-guardrail

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T18:19:51.113040+00:00 | 2026-04-11T18:19:51.113465+00:00 | 2026-04-11T18:24:28.253832+00:00 | 2026-04-11T18:29:02.298994+00:00 | continue |
| 1 | 2026-04-11T18:31:12.727034+00:00 | 2026-04-11T18:31:12.727484+00:00 | 2026-04-11T18:35:13.114196+00:00 | 2026-04-11T18:42:42.571667+00:00 | continue |
| 2 | 2026-04-11T18:44:31.094519+00:00 | 2026-04-11T18:44:31.094865+00:00 | 2026-04-11T18:47:41.704065+00:00 | 2026-04-11T18:53:14.979933+00:00 | continue |
| 3 | 2026-04-11T18:55:00.811803+00:00 | 2026-04-11T18:55:00.811808+00:00 | - | - | - |

### powerlifting-coef-calc__orchestration-delegation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T18:57:57.498107+00:00 | 2026-04-11T18:57:57.498510+00:00 | 2026-04-11T19:00:57.160673+00:00 | 2026-04-11T19:07:00.596148+00:00 | continue |
| 1 | 2026-04-11T19:09:26.977818+00:00 | 2026-04-11T19:09:26.978291+00:00 | 2026-04-11T19:12:34.243505+00:00 | 2026-04-11T19:17:56.479961+00:00 | continue |
| 2 | 2026-04-11T19:20:13.713714+00:00 | 2026-04-11T19:20:13.714038+00:00 | 2026-04-11T19:23:07.326650+00:00 | 2026-04-11T19:29:43.203005+00:00 | continue |
| 3 | 2026-04-11T19:31:31.566309+00:00 | 2026-04-11T19:31:31.566314+00:00 | - | - | - |

### spring-boot-jakarta-migration__artifact-generation

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T19:41:21.176598+00:00 | 2026-04-11T19:41:21.177016+00:00 | 2026-04-11T19:46:42.882723+00:00 | 2026-04-11T19:53:49.757875+00:00 | continue |
| 1 | 2026-04-11T20:02:17.013357+00:00 | 2026-04-11T20:02:17.013652+00:00 | 2026-04-11T20:06:49.953646+00:00 | 2026-04-11T20:12:51.704722+00:00 | continue |
| 2 | 2026-04-11T20:18:22.412478+00:00 | 2026-04-11T20:18:22.412779+00:00 | 2026-04-11T20:21:51.427572+00:00 | 2026-04-11T20:28:01.858709+00:00 | continue |
| 3 | 2026-04-11T20:34:06.753570+00:00 | 2026-04-11T20:34:06.753575+00:00 | - | - | - |

### spring-boot-jakarta-migration__analytic-pipeline

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T20:40:16.871057+00:00 | 2026-04-11T20:40:16.871463+00:00 | 2026-04-11T20:44:53.673893+00:00 | 2026-04-11T20:53:02.902347+00:00 | continue |
| 1 | 2026-04-11T20:58:33.395744+00:00 | 2026-04-11T20:58:33.396062+00:00 | 2026-04-11T21:03:39.899111+00:00 | 2026-04-11T21:09:35.148828+00:00 | continue |
| 2 | 2026-04-11T21:15:57.953644+00:00 | 2026-04-11T21:15:57.954137+00:00 | 2026-04-11T21:19:58.018202+00:00 | 2026-04-11T21:26:45.141849+00:00 | continue |
| 3 | 2026-04-11T21:28:44.604230+00:00 | 2026-04-11T21:28:44.604238+00:00 | - | - | - |

### spring-boot-jakarta-migration__engineering-composition

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T21:33:06.010878+00:00 | 2026-04-11T21:33:06.011327+00:00 | 2026-04-11T21:37:19.291393+00:00 | 2026-04-11T21:43:29.568455+00:00 | continue |
| 1 | 2026-04-11T21:51:26.783944+00:00 | 2026-04-11T21:51:26.784282+00:00 | 2026-04-11T21:55:17.367989+00:00 | 2026-04-11T22:00:38.805110+00:00 | continue |
| 2 | 2026-04-11T22:08:07.441681+00:00 | 2026-04-11T22:08:07.442025+00:00 | 2026-04-11T22:13:43.777876+00:00 | 2026-04-11T22:19:39.668434+00:00 | continue |
| 3 | 2026-04-11T22:26:36.593775+00:00 | 2026-04-11T22:26:36.593786+00:00 | - | - | - |

### spring-boot-jakarta-migration__retrieval-heavy-synthesis

- launcher_status: `succeeded`
- run_status: `completed`
- returncode: `0`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `TuneExceptionStats`
- failure_stage: `continue`
- failure_round: `0`
- failure_summary: `RuntimeError=['c4-spring-boot-jakarta-migration__EX3ui3T']`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
| 0 | 2026-04-11T22:33:05.061150+00:00 | 2026-04-11T22:33:05.061744+00:00 | 2026-04-11T22:36:05.278009+00:00 | 2026-04-11T22:42:55.050282+00:00 | continue |
| 1 | 2026-04-11T22:43:09.760054+00:00 | 2026-04-11T22:43:09.760272+00:00 | 2026-04-11T22:46:00.362639+00:00 | 2026-04-11T22:51:45.099911+00:00 | continue |
| 2 | 2026-04-11T22:51:59.666347+00:00 | 2026-04-11T22:51:59.666569+00:00 | 2026-04-11T22:54:34.066206+00:00 | 2026-04-11T22:59:35.825164+00:00 | continue |
| 3 | 2026-04-11T22:59:50.607899+00:00 | 2026-04-11T22:59:50.607902+00:00 | - | - | - |

### spring-boot-jakarta-migration__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### spring-boot-jakarta-migration__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### spring-boot-jakarta-migration__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### trend-anomaly-causal-inference__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### trend-anomaly-causal-inference__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### trend-anomaly-causal-inference__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### trend-anomaly-causal-inference__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### trend-anomaly-causal-inference__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### trend-anomaly-causal-inference__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### trend-anomaly-causal-inference__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### sec-financial-report__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### sec-financial-report__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### sec-financial-report__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### sec-financial-report__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### sec-financial-report__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### sec-financial-report__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### sec-financial-report__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### virtualhome-agent-planning__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### virtualhome-agent-planning__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### virtualhome-agent-planning__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### virtualhome-agent-planning__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### virtualhome-agent-planning__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### virtualhome-agent-planning__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### virtualhome-agent-planning__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### 3d-scan-calc__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### 3d-scan-calc__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### 3d-scan-calc__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### 3d-scan-calc__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### 3d-scan-calc__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### 3d-scan-calc__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### 3d-scan-calc__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### data-to-d3__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### data-to-d3__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### data-to-d3__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### data-to-d3__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### data-to-d3__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### data-to-d3__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### data-to-d3__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### fix-druid-loophole-cve__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### fix-druid-loophole-cve__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### fix-druid-loophole-cve__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### fix-druid-loophole-cve__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### fix-druid-loophole-cve__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### fix-druid-loophole-cve__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### fix-druid-loophole-cve__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### reserves-at-risk-calc__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### reserves-at-risk-calc__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### reserves-at-risk-calc__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### reserves-at-risk-calc__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### reserves-at-risk-calc__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### reserves-at-risk-calc__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### reserves-at-risk-calc__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### mars-clouds-clustering__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### mars-clouds-clustering__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### mars-clouds-clustering__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### mars-clouds-clustering__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### mars-clouds-clustering__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### mars-clouds-clustering__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### mars-clouds-clustering__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### exceltable-in-ppt__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### exceltable-in-ppt__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### exceltable-in-ppt__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### exceltable-in-ppt__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### exceltable-in-ppt__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### exceltable-in-ppt__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### exceltable-in-ppt__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### simpo-code-reproduction__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### simpo-code-reproduction__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### simpo-code-reproduction__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### simpo-code-reproduction__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### simpo-code-reproduction__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### simpo-code-reproduction__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### simpo-code-reproduction__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### shock-analysis-demand__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### shock-analysis-demand__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### shock-analysis-demand__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### shock-analysis-demand__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### shock-analysis-demand__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### shock-analysis-demand__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### shock-analysis-demand__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### multilingual-video-dubbing__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### multilingual-video-dubbing__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### multilingual-video-dubbing__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### multilingual-video-dubbing__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### multilingual-video-dubbing__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### multilingual-video-dubbing__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### multilingual-video-dubbing__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### offer-letter-generator__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### offer-letter-generator__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### offer-letter-generator__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### offer-letter-generator__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### offer-letter-generator__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### offer-letter-generator__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### offer-letter-generator__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### fix-build-agentops__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### fix-build-agentops__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### fix-build-agentops__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### fix-build-agentops__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### fix-build-agentops__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### fix-build-agentops__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### fix-build-agentops__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### shock-analysis-supply__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### shock-analysis-supply__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### shock-analysis-supply__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### shock-analysis-supply__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### shock-analysis-supply__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### shock-analysis-supply__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### shock-analysis-supply__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### lab-unit-harmonization__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### lab-unit-harmonization__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### lab-unit-harmonization__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### lab-unit-harmonization__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### lab-unit-harmonization__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### lab-unit-harmonization__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### lab-unit-harmonization__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### protein-expression-analysis__artifact-generation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### protein-expression-analysis__analytic-pipeline

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### protein-expression-analysis__engineering-composition

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### protein-expression-analysis__retrieval-heavy-synthesis

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### protein-expression-analysis__environment-control

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### protein-expression-analysis__methodology-guardrail

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |

### protein-expression-analysis__orchestration-delegation

- launcher_status: `failed`
- run_status: `failed`
- returncode: `1`
- stale_run_status: `False`
- timeout_detected: `False`
- early_stop: `False`
- failure_type: `RuntimeError`
- failure_stage: `environment_check`
- failure_round: `None`
- failure_summary: `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

| Round | round_started | executor_completed | role_a_completed | role_b_completed | decision |
| ---: | --- | --- | --- | --- | --- |
