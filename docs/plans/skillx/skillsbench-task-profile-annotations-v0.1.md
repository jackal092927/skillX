# SkillsBench Task Profile Annotations v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-03-31
- **Purpose:** first-pass human-interpretable annotation sheet for assigning all SkillsBench tasks into the current SkillX / UltraLoop schema before deriving an initial provisional classification
- **Status:** scaffold created; task-by-task annotation in progress

---

## 1. Annotation policy

This sheet is the raw annotation layer.
It is intentionally separate from the later classification memo.

### First-pass rule
For the first pass, prioritize fields that are relatively observable from the task + skill artifact:
- `task_object`
- `workflow_topology`
- `tool_surface_regime`
- `verifier_mode`
- `primary_pattern`
- `secondary_patterns`
- `confidence`
- `evidence_note`

### Second-pass rule
Delay more inferential fields until after broader task coverage and evidence review:
- `risk_profile`
- `dominant_failure_mode`
- `rewrite_response_hypothesis`

### Confidence levels
- `high` = clearly supported by task structure / verifier contract
- `medium` = strong guess but some ambiguity remains
- `low` = provisional placement; revisit after broader comparison

---

## 2. Field vocabulary

### `task_object`
- `artifact-generation`
- `analytic-pipeline`
- `engineering-composition`
- `methodology-guardrail`
- `retrieval-heavy-synthesis`
- `environment-control`
- `orchestration-delegation`
- `other`

### `workflow_topology`
- `single-step`
- `single-step-with-review`
- `staged-multi-step`
- `multi-skill-composition`
- `branching-abstention-aware`
- `orchestration-heavy`
- `other`

### `tool_surface_regime`
- `tool-light`
- `tool-medium`
- `tool-heavy-script-optional`
- `tool-heavy-script-recommended`
- `runtime-bootstrap-sensitive`
- `other`

### `verifier_mode`
- `deterministic-output-contract`
- `deterministic-artifact-plus-stage-check`
- `benchmark-threshold`
- `human-judgment-heavy`
- `abstention-and-fit-check`
- `other`

### `primary_pattern` / `secondary_patterns`
- `tool-wrapper`
- `generator`
- `reviewer`
- `inversion`
- `pipeline`

---

## 3. Annotation table

### Canonical inventory note
For this first-pass annotation sheet, the canonical surface is the **repo-wide SkillsBench task directory list** rather than the narrower paper table.
That means this sheet currently tracks the full repo task surface (`89` task directories by current count), even though the paper/eval subset uses a slightly narrower and partially truncated naming surface.

| task_name | task_object | workflow_topology | tool_surface_regime | verifier_mode | primary_pattern | secondary_patterns | confidence | evidence_note |
|---|---|---|---|---|---|---|---|---|
| 3d-scan-calc | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | binary STL parsing, connected-component filtering, material lookup, and mass computation form an ordered geometry-analysis workflow into JSON |
| PDF-Crosspage-Table-Normalization-to-Excel | analytic-pipeline | staged-multi-step | tool-medium | deterministic-output-contract | pipeline | tool-wrapper, reviewer | medium | GitHub task page exists but current instruction.md is empty (0 bytes), so this remains a title-driven classification: cross-page PDF table extraction and normalization into Excel |
| adaptive-cruise-control | environment-control | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | pipeline | tool-wrapper, reviewer | high | controller design, simulation, tuning, and metric targets form an ordered control-system workflow |
| azure-bgp-oscillation-route-leak | analytic-pipeline | staged-multi-step | tool-medium | deterministic-output-contract | pipeline | reviewer, tool-wrapper | high | load topology files, detect oscillation/leak violations, evaluate solution candidates, and emit structured JSON report |
| citation-check | methodology-guardrail | single-step-with-review | tool-medium | deterministic-output-contract | reviewer | inversion | high | evidence-based fake-citation screening with cleaned sorted JSON titles is dominated by validation and false-positive control |
| civ6-adjacency-optimizer | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | benchmark-threshold | pipeline | tool-wrapper, reviewer | high | parse .Civ6Map, compute adjacency bonuses for district placements, and maximize total score against an optimal benchmark |
| court-form-filling | artifact-generation | single-step-with-review | tool-medium | deterministic-output-contract | generator | reviewer | high | field-constrained PDF artifact; required vs omitted form sections and no-extra-fill discipline dominate |
| crystallographic-wyckoff-position-analysis | engineering-composition | staged-multi-step | tool-heavy-script-recommended | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | build a reusable Python function that parses CIF files, computes Wyckoff multiplicities, and returns coordinate dicts; no hardcoding allowed |
| dapt-intrusion-detection | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | deterministic-output-contract | pipeline | reviewer, tool-wrapper | high | pcap analysis requires computing ~30 network metrics plus boolean analysis flags and filling a structured CSV template |
| data-to-d3 | artifact-generation | staged-multi-step | tool-medium | deterministic-artifact-plus-stage-check | pipeline | generator, reviewer | high | task requires a coupled multi-file web artifact with precise D3 chart behavior, layout constraints, and linked interactions |
| dialogue-parser | artifact-generation | single-step-with-review | tool-light | deterministic-output-contract | generator | reviewer | high | validated JSON graph plus DOT output create a sharp structured artifact contract |
| dynamic-object-aware-egomotion | analytic-pipeline | staged-multi-step | tool-heavy-script-recommended | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | instruction explicitly requires sampled-frame camera-motion labeling plus sparse dynamic-object masks, so this is a constrained video-analysis pipeline rather than a loose multimodal task |
| earthquake-phase-association | analytic-pipeline | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | pipeline | tool-wrapper, reviewer | high | load waveforms, run DL phase picking via SeisBench, associate picks into events, and pass F1 ≥ 0.6 gate |
| earthquake-plate-calculation | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | geospatial analysis using GeoPandas: filter earthquakes inside Pacific plate, compute max boundary distance, emit JSON |
| econ-detrending-correlation | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | extract nominal series, deflate with CPI, HP-filter log-real series, compute Pearson correlation, output single number |
| edit-pdf | artifact-generation | single-step-with-review | tool-medium | deterministic-output-contract | generator | reviewer | high | instruction-following PDF edit with update/redaction and placement constraints dominates |
| energy-ac-optimal-power-flow | analytic-pipeline | staged-multi-step | tool-heavy-script-recommended | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | solve AC-OPF from math model, produce structured JSON report with generators, buses, branches, and feasibility checks |
| energy-market-pricing | analytic-pipeline | staged-multi-step | tool-heavy-script-recommended | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | run DC-OPF with reserve co-optimization for base and counterfactual scenarios; produce comparative JSON report |
| enterprise-information-search | retrieval-heavy-synthesis | staged-multi-step | tool-medium | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | instruction explicitly frames multi-question retrieval over enterprise data into a fixed answer.json schema with per-question token accounting |
| exceltable-in-ppt | artifact-generation | staged-multi-step | tool-medium | deterministic-artifact-plus-stage-check | pipeline | tool-wrapper, reviewer | high | embedded Excel extraction, targeted update, and PPTX preservation require ordered artifact manipulation |
| exoplanet-detection-period | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | filter TESS lightcurve, remove stellar-activity variability, and output one rounded orbital period value; strong ordered analysis but single-value contract |
| financial-modeling-qa | analytic-pipeline | staged-multi-step | tool-medium | deterministic-output-contract | pipeline | reviewer, tool-wrapper | high | instruction is a concrete workbook-plus-background analysis task that reduces to one numeric answer.txt output rather than an open-ended finance QA surface |
| find-topk-similiar-chemicals | engineering-composition | staged-multi-step | tool-heavy-script-recommended | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | build a reusable Python function using PubChem/RDKit for Morgan fingerprint Tanimoto similarity; no hardcoded SMILES |
| fix-build-agentops | engineering-composition | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | pipeline | reviewer, tool-wrapper | high | diagnose build break, stage patch diffs, apply fixes, and satisfy build success gate |
| fix-build-google-auto | engineering-composition | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | pipeline | reviewer, tool-wrapper | high | diagnose build break, stage patch diffs, apply fixes, and satisfy build success gate |
| fix-druid-loophole-cve | engineering-composition | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | pipeline | reviewer, tool-wrapper | high | identify CVE root cause, write patches, rebuild with Maven, and pass exploit-blocked + legitimate-request tests |
| fix-erlang-ssh-cve | engineering-composition | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | reviewer | pipeline, tool-wrapper | high | investigate SSH protocol message vulnerability, patch Erlang source to block unauthorized execution while preserving normal SSH |
| fix-visual-stability | engineering-composition | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | pipeline | reviewer, tool-wrapper | high | instruction explicitly targets root-cause diagnosis and repair of visual instability in a Next.js app under no-regression selector constraints |
| flink-query | engineering-composition | staged-multi-step | tool-heavy-script-recommended | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | implement Flink job skeleton with custom data types, session-window logic, compile and run on Flink; output compared line-by-line |
| flood-risk-analysis | analytic-pipeline | staged-multi-step | tool-medium | deterministic-output-contract | pipeline | reviewer, tool-wrapper | high | instruction is a clean hydrology analysis task: identify stations with flood days in a fixed date window and emit a two-column CSV |
| gh-repo-analytics | retrieval-heavy-synthesis | staged-multi-step | tool-medium | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | monthly GitHub PR/issue metrics require API-style retrieval, aggregation, and structured JSON reporting |
| glm-lake-mendota | environment-control | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | pipeline | tool-wrapper, reviewer | high | configure and run GLM lake model, tune parameters until RMSE < 2°C against field observations |
| gravitational-wave-detection | analytic-pipeline | staged-multi-step | tool-heavy-script-recommended | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | condition detector data, perform matched filtering over mass grid across three approximants, report peak SNR per approximant in CSV |
| grid-dispatch-operator | analytic-pipeline | staged-multi-step | tool-heavy-script-recommended | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | solve economic dispatch with reserve coupling from MATPOWER snapshot, produce structured JSON report |
| hvac-control | environment-control | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | pipeline | tool-wrapper, reviewer | high | calibration, parameter estimation, gain tuning, and closed-loop control are tied to explicit control metrics |
| invoice-fraud-detection | analytic-pipeline | staged-multi-step | tool-medium | deterministic-output-contract | reviewer | pipeline, tool-wrapper | high | invoice extraction is coupled with ordered fraud-screening criteria, fuzzy vendor matching, and first-match reason selection into JSON |
| jax-computing-basics | engineering-composition | staged-multi-step | tool-heavy-script-recommended | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | local instruction confirms a batch programming task driven by problem.json specs: load inputs, implement JAX computations, and save per-task outputs |
| jpg-ocr-stat | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | batch OCR plus field extraction with explicit fallback rules into a strict Excel schema |
| lab-unit-harmonization | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | deterministic-output-contract | pipeline | reviewer, tool-wrapper | high | cleaning malformed numeric formats, dropping incomplete rows, detecting mixed units, and converting into harmonized physiological ranges is a stage-sensitive tabular pipeline |
| lake-warming-attribution | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | trend analysis on water temp plus driver attribution (Heat/Flow/Wind/Human) into two constrained CSVs |
| latex-formula-extraction | artifact-generation | single-step-with-review | tool-medium | deterministic-output-contract | generator | reviewer | high | extract display formulas into exact markdown/latex lines with a light syntax-fix review pass |
| lean4-proof | artifact-generation | single-step-with-review | tool-light | deterministic-output-contract | generator | reviewer | high | complete a Lean4 proof from a fixed template; must type-check with no warnings; pure formal-math generation task |
| manufacturing-codebook-normalization | retrieval-heavy-synthesis | staged-multi-step | tool-medium | deterministic-output-contract | reviewer | pipeline, tool-wrapper | high | instruction explicitly requires mapping noisy multilingual defect text to product-specific codebooks with calibrated confidence, rationales, and UNKNOWN abstention |
| manufacturing-equipment-maintenance | retrieval-heavy-synthesis | staged-multi-step | tool-medium | deterministic-output-contract | pipeline | reviewer, tool-wrapper | high | handbook-grounded maintenance QA over MES logs, thermocouples, and defect data makes this a grounded retrieval-plus-calculation synthesis workflow |
| manufacturing-fjsp-optimization | analytic-pipeline | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | pipeline | tool-wrapper, reviewer | high | instruction explicitly asks for a feasible flexible job-shop schedule that improves makespan without worsening policy budgets, with synchronized JSON/CSV outputs |
| mario-coin-counting | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | extract keyframes, convert to grayscale, template-match coins/enemies/turtles, and produce a strict CSV with counts per frame |
| mars-clouds-clustering | analytic-pipeline | staged-multi-step | tool-heavy-script-recommended | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | grid-search DBSCAN hyperparameters with custom distance metric, compute F1/delta per image, identify Pareto frontier, output CSV |
| mhc-layer-impl | engineering-composition | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | pipeline | tool-wrapper, reviewer | high | implement mHC layer from paper, train baseline and mHC nanoGPT models on A100, compare loss/gradient stats in JSON |
| multilingual-video-dubbing | analytic-pipeline | staged-multi-step | tool-heavy-script-recommended | deterministic-artifact-plus-stage-check | pipeline | tool-wrapper, reviewer | high | translation-aligned TTS, segment timing control, loudness constraints, and muxed dubbed-video output form a tightly staged AV pipeline |
| offer-letter-generator | artifact-generation | single-step-with-review | tool-light | deterministic-output-contract | generator | reviewer | high | clear structured artifact contract; missing-input and no-invention discipline dominate |
| organize-messy-files | retrieval-heavy-synthesis | staged-multi-step | tool-medium | deterministic-artifact-plus-stage-check | reviewer | pipeline, inversion | high | local instruction confirms a content-based document classification task with exclusive assignment into five folders and no leftover files |
| paper-anonymizer | artifact-generation | single-step-with-review | tool-medium | deterministic-output-contract | reviewer | generator | high | redaction task is dominated by leak detection/removal while preserving a usable anonymized PDF artifact |
| parallel-tfidf-search | engineering-composition | multi-skill-composition | tool-heavy-script-recommended | benchmark-threshold | pipeline | tool-wrapper, reviewer | high | coordination across bundle logic, ordered execution, and benchmark-style performance gate |
| pddl-tpp-planning | environment-control | staged-multi-step | tool-medium | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | formal planning task is dominated by loading domain/problem files and producing valid executable plan artifacts |
| pdf-excel-diff | analytic-pipeline | staged-multi-step | tool-medium | deterministic-artifact-plus-stage-check | pipeline | reviewer, tool-wrapper | high | extract legacy table, compare against current workbook, and emit a structured diff report |
| pedestrian-traffic-counting | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | each video requires object counting with cross-frame deduplication and strict Excel reporting per filename |
| pg-essay-to-audiobook | orchestration-delegation | staged-multi-step | tool-heavy-script-optional | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | instruction is a clean two-system workflow: retrieve specified Paul Graham essays online and turn them into one audiobook via remote or local TTS |
| powerlifting-coef-calc | artifact-generation | staged-multi-step | tool-medium | deterministic-artifact-plus-stage-check | pipeline | generator, reviewer | high | existing workbook must be extended in-place with selected columns and Excel formulas for TotalKg and Dots coefficients |
| pptx-reference-formatting | artifact-generation | staged-multi-step | tool-medium | deterministic-output-contract | pipeline | reviewer, generator | high | slide-wide title detection, formatting normalization, and reference-slide synthesis produce a tightly constrained PPTX artifact |
| protein-expression-analysis | artifact-generation | staged-multi-step | tool-medium | deterministic-artifact-plus-stage-check | pipeline | generator, reviewer | high | populate workbook cells via lookup formulas, compute group statistics and fold changes; no macros, formulas only |
| python-scala-translation | artifact-generation | single-step-with-review | tool-light | deterministic-output-contract | generator | reviewer | high | primary job is source-to-source code translation under explicit symbol-preservation and Scala-idiom constraints |
| quantum-numerical-simulation | analytic-pipeline | staged-multi-step | tool-heavy-script-recommended | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | local instruction specifies a four-case steady-state simulation workflow with cavity-state tracing and 1000x1000 Wigner grids saved as CSVs |
| r2r-mpc-control | environment-control | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | pipeline | tool-wrapper, reviewer | high | state-space derivation, MPC design, simulator execution, and control metrics define an ordered control loop |
| react-performance-debugging | engineering-composition | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | pipeline | reviewer, tool-wrapper | high | root-cause performance debugging plus functional guardrails requires ordered engineering changes and verification |
| reserves-at-risk-calc | retrieval-heavy-synthesis | staged-multi-step | tool-medium | deterministic-artifact-plus-stage-check | pipeline | tool-wrapper, reviewer | high | download IMF gold price data, populate workbook, compute volatility/exposure/RaR across steps; Excel formulas only |
| sales-pivot-analysis | analytic-pipeline | staged-multi-step | tool-medium | deterministic-artifact-plus-stage-check | pipeline | tool-wrapper, reviewer | high | multi-source tabular merge plus specific pivot-table/report sheet contract dominates |
| scheduling-email-assistant | orchestration-delegation | staged-multi-step | tool-heavy-script-optional | deterministic-artifact-plus-stage-check | pipeline | tool-wrapper, reviewer | high | extract constraints, consult calendar, send reply email, and log message IDs as part of one workflow |
| sec-financial-report | retrieval-heavy-synthesis | staged-multi-step | tool-medium | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | multi-question SEC filing analysis requires repeated search, accession resolution, holdings comparison, and JSON answer synthesis |
| seismic-phase-picking | analytic-pipeline | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | pipeline | tool-wrapper, reviewer | high | load 100 npz traces, pick P/S wave indices, output CSV; graded on F1 ≥ 0.7 (P) and ≥ 0.6 (S) |
| setup-fuzzing-py | engineering-composition | staged-multi-step | tool-heavy-script-recommended | deterministic-artifact-plus-stage-check | pipeline | tool-wrapper, reviewer | high | discover libraries, analyze functions, write fuzz drivers, set up venvs, run 10s fuzzing validation; 5-step ordered workflow |
| shock-analysis-demand | retrieval-heavy-synthesis | staged-multi-step | tool-medium | deterministic-artifact-plus-stage-check | pipeline | tool-wrapper, reviewer | high | collect IMF WEO + geostat data, populate workbook, model demand-side shock across 3 scenarios; Excel formulas only |
| shock-analysis-supply | retrieval-heavy-synthesis | staged-multi-step | tool-medium | deterministic-artifact-plus-stage-check | pipeline | tool-wrapper, reviewer | high | collect PWT/WEO/ECB data, HP-filter in Excel via Solver, build Cobb-Douglas production function across projection; Excel only |
| simpo-code-reproduction | engineering-composition | staged-multi-step | tool-heavy-script-recommended | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | implement SimPO loss from paper PDF, set up environment, run unit test, save loss matrix to npz |
| software-dependency-audit | analytic-pipeline | staged-multi-step | tool-medium | deterministic-output-contract | reviewer | tool-wrapper, pipeline | high | dependency audit is dominated by vulnerability-screening criteria and a strict CSV evidence schema |
| speaker-diarization-subtitles | analytic-pipeline | staged-multi-step | tool-heavy-script-recommended | deterministic-artifact-plus-stage-check | pipeline | tool-wrapper, reviewer | high | audio extraction, diarization, subtitle generation, and process reporting are explicit ordered stages with multiple artifact contracts |
| spring-boot-jakarta-migration | engineering-composition | staged-multi-step | tool-heavy-script-recommended | benchmark-threshold | pipeline | tool-wrapper, reviewer | high | framework migration with dependency, namespace, and test/compile gates is an ordered engineering bundle |
| suricata-custom-exfil | artifact-generation | single-step-with-review | tool-medium | deterministic-output-contract | generator | reviewer | high | write a single Suricata signature matching 5 conjunctive conditions; verifier checks alert on exfil pcaps and no false positives |
| syzkaller-ppdev-syzlang | artifact-generation | single-step-with-review | tool-medium | deterministic-output-contract | generator | reviewer | high | create syzlang description files for ppdev ioctls; verified by make descriptions + make all compilation |
| taxonomy-tree-merge | methodology-guardrail | branching-abstention-aware | tool-light | abstention-and-fit-check | inversion | reviewer, pipeline | high | fit checks, assumption control, and premature-commitment avoidance dominate |
| threejs-structure-parser | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | deterministic-artifact-plus-stage-check | pipeline | tool-wrapper, reviewer | high | parse createScene(), recover part/group structure, and export grouped mesh/link OBJ artifacts in a specified directory layout |
| threejs-to-obj | artifact-generation | staged-multi-step | tool-heavy-script-optional | deterministic-output-contract | tool-wrapper | pipeline, reviewer | high | task is centered on writing/export tooling that converts a Three.js-defined object into a Blender-ready OBJ with coordinate-frame adjustment |
| travel-planning | retrieval-heavy-synthesis | staged-multi-step | tool-medium | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | grounded multi-constraint itinerary synthesis with mandatory search-skill usage and strict 7-day JSON output |
| trend-anomaly-causal-inference | analytic-pipeline | staged-multi-step | tool-heavy-script-recommended | deterministic-artifact-plus-stage-check | pipeline | tool-wrapper, reviewer | high | ordered analytic stages, intermediate artifacts, and handoff contracts dominate |
| video-filler-word-remover | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | deterministic-artifact-plus-stage-check | pipeline | tool-wrapper, reviewer | high | transcribe video, detect filler words with timestamps, save JSON annotations, stitch filler clips into output video |
| video-silence-remover | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | deterministic-artifact-plus-stage-check | pipeline | tool-wrapper, reviewer | high | detect silent/non-teaching segments, remove them, produce compressed video and JSON compression report with consistent math |
| video-tutorial-indexer | analytic-pipeline | staged-multi-step | tool-heavy-script-optional | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | long-video topic segmentation into exact ordered chapter titles and monotonic timestamps is an ordered multimodal indexing workflow |
| virtualhome-agent-planning | environment-control | staged-multi-step | tool-medium | deterministic-output-contract | pipeline | tool-wrapper, reviewer | high | local instruction confirms a formal planning workflow over domain/problem pairs in problem.json with validity and syntax constraints on each generated plan |
| weighted-gdp-calc | artifact-generation | staged-multi-step | tool-medium | deterministic-artifact-plus-stage-check | pipeline | generator, reviewer | high | workbook task requires staged lookup formulas, derived statistics, and weighted-mean calculation while preserving sheet formatting |
| xlsx-recover-data | analytic-pipeline | staged-multi-step | tool-medium | deterministic-output-contract | pipeline | reviewer | high | recover missing spreadsheet values through cross-sheet relational analysis into an updated workbook |

---

## 4. Notes for later second pass

For each task, later append or derive:
- `risk_profile`
- `dominant_failure_mode`
- `rewrite_response_hypothesis`

Those fields should be filled after:
1. wider task coverage,
2. cross-task comparison,
3. and where possible, run/verifier evidence.

---

## 5. Follow-on artifact

This first-pass sheet has now been lifted into:
- `docs/plans/skillx/skillsbench-initial-classification-v0.1.md`

That memo summarizes:
- provisional classes,
- clear members,
- edge cases,
- split/merge pressure,
- and which schema dimensions seem most discriminative.

---

## 6. Second-pass seed overlay (representative tasks)

This is **not** yet the full second-pass layer.
It is a seeded overlay for representative tasks so the deferred fields become concrete enough to use in later experiment design.

For the MVP, these seeded fields should be treated as **lightweight tags / hypotheses**, not as extra clustering labels or a second clustering layer.

| task_name | risk_profile | dominant_failure_mode | rewrite_response_hypothesis | seed_rationale |
|---|---|---|---|---|
| offer-letter-generator | negative-transfer-sensitive | placeholder-invention | inversion_helps | missing-input discipline and anti-invention behavior matter more than adding generic scaffolding |
| court-form-filling | negative-transfer-sensitive | placeholder-invention | reviewer_logic_helps | field omission / overfill errors are likely best reduced by explicit review checks against form constraints |
| data-to-d3 | scaffold-sensitive | stage-handoff-break | stronger_stage_contracts_help | multi-file chart artifact generation is highly sensitive to stage boundaries between data prep, rendering, and linked interaction wiring |
| pptx-reference-formatting | scaffold-sensitive | stage-handoff-break | stronger_stage_contracts_help | slide-level normalization plus final reference-slide synthesis is an ordered artifact pipeline where stage leakage is costly |
| parallel-tfidf-search | composition-confusion-sensitive | precedence-conflict | bundle_manifest_clarity_helps | this is the clearest bundle-style task where role/order/interface confusion is a primary failure source |
| fix-build-agentops | threshold-fragile | precedence-conflict | stronger_stage_contracts_help | build-fix tasks usually benefit from cleaner diagnose→patch→verify staging instead of generic expansion |
| fix-druid-loophole-cve | threshold-fragile | precedence-conflict | reviewer_logic_helps | exploit-preserving security fixes are likely helped most by stronger patch-side review logic against both malicious and benign flows |
| spring-boot-jakarta-migration | composition-confusion-sensitive | precedence-conflict | stronger_stage_contracts_help | namespace, dependency, and compile/test migration work benefits from sharper ordered subcontracts rather than broad generic advice |
| trend-anomaly-causal-inference | scaffold-sensitive | stage-handoff-break | stronger_stage_contracts_help | ordered analytic stages and intermediate artifact handoffs are already visible in the task contract |
| flood-risk-analysis | negative-transfer-sensitive | stage-handoff-break | extra_generic_scaffolding_hurts | this is a relatively clean windowed analysis task where over-scaffolding is more likely to add noise than value |
| speaker-diarization-subtitles | scaffold-sensitive | stage-handoff-break | stronger_stage_contracts_help | diarization, subtitle generation, and reporting create obvious multi-artifact handoff risks |
| enterprise-information-search | scaffold-sensitive | stage-handoff-break | reviewer_logic_helps | retrieval-to-answer compression risks dropping evidence; stronger answer-side checking is likely high leverage |
| gh-repo-analytics | scaffold-sensitive | stage-handoff-break | reviewer_logic_helps | metric aggregation over repo events benefits from a stronger check layer between retrieval and final JSON synthesis |
| manufacturing-codebook-normalization | model-sensitivity-high | premature-commitment | reviewer_logic_helps | noisy multilingual text-to-codebook mapping needs calibrated matching and UNKNOWN abstention more than extra workflow length |
| adaptive-cruise-control | threshold-fragile | stage-handoff-break | stronger_stage_contracts_help | controller design / simulation / tuning failures are often exposed at metric gates after earlier-stage slippage |
| pddl-tpp-planning | threshold-fragile | precedence-conflict | stronger_stage_contracts_help | valid plan generation over formal domain/problem pairs is highly sensitive to ordered grounding and validity checks |
| citation-check | negative-transfer-sensitive | premature-commitment | reviewer_logic_helps | fake-citation detection needs careful evidence checking to avoid both hallucinated positives and missed bad entries |
| taxonomy-tree-merge | negative-transfer-sensitive | premature-commitment | inversion_helps | fit-check and abstention discipline are the main protective levers, not more verbose synthesis |
| scheduling-email-assistant | negative-transfer-sensitive | precedence-conflict | stronger_stage_contracts_help | extract constraints → consult calendar → send reply is an order-sensitive action workflow with easy step-order breakage |
| pg-essay-to-audiobook | scaffold-sensitive | precedence-conflict | stronger_stage_contracts_help | retrieve essays → normalize text → TTS → merge output is a fragile orchestration chain where ordering mistakes dominate |
| dialogue-parser | negative-transfer-sensitive | placeholder-invention | reviewer_logic_helps | strict JSON-plus-DOT structure means small invented links or malformed graph elements are disproportionately costly |
| lean4-proof | threshold-fragile | placeholder-invention | extra_generic_scaffolding_hurts | formal proof generation fails hard on non-type-checking filler, so concise proof-directed rewrites are likely better than generic expansion |
| threejs-to-obj | composition-confusion-sensitive | precedence-conflict | stronger_stage_contracts_help | object extraction, coordinate normalization, and OBJ emission form an order-sensitive export toolchain |
| react-performance-debugging | threshold-fragile | precedence-conflict | reviewer_logic_helps | performance fixes must preserve product behavior and test hooks, so post-patch review logic is especially valuable |
| setup-fuzzing-py | composition-confusion-sensitive | precedence-conflict | stronger_stage_contracts_help | discovery → target selection → driver authoring → env setup → validation is a multi-interface engineering chain |
| seismic-phase-picking | threshold-fragile | stage-handoff-break | stronger_stage_contracts_help | waveform loading, pick generation, CSV emission, and metric gates make this a classic stage-fragile benchmarked pipeline |
| sales-pivot-analysis | scaffold-sensitive | stage-handoff-break | stronger_stage_contracts_help | multi-source merge and downstream workbook/pivot construction create obvious intermediate handoff risks |
| software-dependency-audit | negative-transfer-sensitive | premature-commitment | reviewer_logic_helps | high/critical-only filtering with exact CSV evidence makes premature inclusion/exclusion mistakes costly |
| sec-financial-report | scaffold-sensitive | stage-handoff-break | reviewer_logic_helps | filing retrieval, accession resolution, and holdings-comparison synthesis benefit from stronger answer-side evidence checks |
| travel-planning | negative-transfer-sensitive | premature-commitment | reviewer_logic_helps | early itinerary commitments can easily violate budget, date, pet, and transportation constraints unless aggressively checked |
| manufacturing-equipment-maintenance | model-sensitivity-high | premature-commitment | reviewer_logic_helps | handbook-grounded compliance QA over multiple plant data sources needs conservative evidence-backed synthesis |
| shock-analysis-demand | scaffold-sensitive | stage-handoff-break | stronger_stage_contracts_help | retrieval → Excel population → scenario modeling is a serial workbook-analysis workflow with clear stage interfaces |
| glm-lake-mendota | threshold-fragile | stage-handoff-break | stronger_stage_contracts_help | model configuration, run, tuning, and RMSE evaluation create a gated scientific control loop |
| r2r-mpc-control | threshold-fragile | stage-handoff-break | stronger_stage_contracts_help | derivation, controller synthesis, simulation, and metric evaluation are tightly ordered and gate-fragile |
| virtualhome-agent-planning | threshold-fragile | precedence-conflict | stronger_stage_contracts_help | formal plan generation is sensitive to ordered grounding/validity logic, so weak sequencing is likely the dominant failure source |

These rows are best understood as **working hypotheses** for the next experimental phase, not as settled truths.
