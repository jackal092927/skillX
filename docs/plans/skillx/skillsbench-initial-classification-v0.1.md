# SkillsBench Initial Classification v0.1

Date: 2026-03-31
Project: `projects/skillX`
Status: first-pass classification built from the completed cheap-field annotation layer
Upstream source: `docs/plans/skillx/skillsbench-task-profile-annotations-v0.1.md`

---

## 1. Purpose

This memo turns the completed first-pass SkillsBench annotation sheet into an **interpretable initial classification**.

The goal here is **not** to claim a final outer-loop ontology.
The goal is to identify:
- which class boundaries already look stable,
- which dimensions are actually discriminative,
- where split/merge pressure appears,
- and what object the future MetaSkill / UltraLoop outer loop should probably optimize.

The canonical surface for this pass is the **repo-wide SkillsBench task-directory inventory**.
Current annotated task count: **89 / 89**.

---

## 2. High-level quantitative picture

### 2.1 Task-object counts

- `analytic-pipeline`: **37**
- `artifact-generation`: **17**
- `engineering-composition`: **15**
- `retrieval-heavy-synthesis`: **10**
- `environment-control`: **6**
- `methodology-guardrail`: **2**
- `orchestration-delegation`: **2**

### 2.2 Workflow-topology counts

- `staged-multi-step`: **76**
- `single-step-with-review`: **11**
- `multi-skill-composition`: **1**
- `branching-abstention-aware`: **1**

### 2.3 Verifier-mode counts

- `deterministic-output-contract`: **52**
- `deterministic-artifact-plus-stage-check`: **19**
- `benchmark-threshold`: **17**
- `abstention-and-fit-check`: **1**

### 2.4 Tool-surface counts

- `tool-medium`: **34**
- `tool-heavy-script-recommended`: **32**
- `tool-heavy-script-optional`: **18**
- `tool-light`: **5**

### 2.5 Primary-pattern counts

- `pipeline`: **71**
- `generator`: **9**
- `reviewer`: **7**
- `inversion`: **1**
- `tool-wrapper`: **1**

### 2.6 Confidence counts

- `high`: **88**
- `medium`: **1**

---

## 3. Main classification conclusions

### Conclusion A — `task_object` is the strongest top-level axis

`task_object` produces the cleanest first-pass separation.
It tracks **what kind of reusable outer-loop object** a task seems to want:
- structured artifact production,
- analysis pipeline execution,
- engineering/codebase modification,
- retrieval-grounded synthesis,
- simulator/control interaction,
- guardrail/fit-check behavior,
- or orchestration across external actions.

This is much more discriminative than the Google 5-pattern lens by itself.

### Conclusion B — `primary_pattern` is useful, but not sufficient as the ontology

`pipeline` dominates **71 / 89** tasks.
That is too collapsed to serve as the main SkillX ontology.

This strongly supports the earlier design stance:
- Google 5 patterns are best used as a **morphology / internal structure layer**,
- not as the main outer-loop learning object.

### Conclusion C — `workflow_topology` is informative but mostly secondary

`staged-multi-step` dominates **76 / 89** tasks.
So topology matters, but by itself it does not separate task families well enough.

Topology is still valuable as a **second axis**:
- especially for distinguishing `single-step-with-review` artifact tasks,
- `multi-skill-composition` engineering bundles,
- and `branching-abstention-aware` guardrail tasks.

### Conclusion D — `verifier_mode` is the best secondary discriminator after `task_object`

`verifier_mode` separates several otherwise-similar task families:
- `benchmark-threshold` isolates many engineering and control tasks,
- `deterministic-artifact-plus-stage-check` marks artifact/pipeline tasks with intermediate-stage coupling,
- `deterministic-output-contract` captures many strict-schema production tasks,
- `abstention-and-fit-check` cleanly marks the rare guardrail-style edge.

So the practical ranking from this pass is:

1. `task_object`
2. `verifier_mode`
3. `tool_surface_regime`
4. `workflow_topology`
5. `primary_pattern` / `secondary_patterns`

---

## 4. Provisional classes

## Class 1 — Analytic Pipeline Bundle

**Count:** 37

**Core shape:**
A task that is mainly about running an ordered analysis workflow over data, media, signals, geometry, spreadsheets, or scientific artifacts, then emitting a constrained output.

**Typical signature:**
- `task_object = analytic-pipeline`
- `workflow_topology = staged-multi-step`
- primary pattern almost always `pipeline`
- verifier is usually either:
  - `deterministic-output-contract`, or
  - `deterministic-artifact-plus-stage-check`, or
  - `benchmark-threshold`

**Representative members:**
- `trend-anomaly-causal-inference`
- `earthquake-phase-association`
- `seismic-phase-picking`
- `video-tutorial-indexer`
- `jpg-ocr-stat`
- `sales-pivot-analysis`
- `dapt-intrusion-detection`
- `pdf-excel-diff`

**Current members:**
`3d-scan-calc`, `PDF-Crosspage-Table-Normalization-to-Excel`, `azure-bgp-oscillation-route-leak`, `civ6-adjacency-optimizer`, `dapt-intrusion-detection`, `dynamic-object-aware-egomotion`, `earthquake-phase-association`, `earthquake-plate-calculation`, `econ-detrending-correlation`, `energy-ac-optimal-power-flow`, `energy-market-pricing`, `exoplanet-detection-period`, `financial-modeling-qa`, `flood-risk-analysis`, `gravitational-wave-detection`, `grid-dispatch-operator`, `invoice-fraud-detection`, `jpg-ocr-stat`, `lab-unit-harmonization`, `lake-warming-attribution`, `manufacturing-fjsp-optimization`, `mario-coin-counting`, `mars-clouds-clustering`, `multilingual-video-dubbing`, `pdf-excel-diff`, `pedestrian-traffic-counting`, `quantum-numerical-simulation`, `sales-pivot-analysis`, `seismic-phase-picking`, `software-dependency-audit`, `speaker-diarization-subtitles`, `threejs-structure-parser`, `trend-anomaly-causal-inference`, `video-filler-word-remover`, `video-silence-remover`, `video-tutorial-indexer`, `xlsx-recover-data`.

**Why this class is real:**
These tasks are not just “data tasks.” They share the same outer-loop need:
**better stage structure, intermediate artifact discipline, and analysis-to-output handoff quality.**

**Split pressure:**
This class is probably too broad and is the first candidate for future subdivision.
Likely future sub-clusters include:
- scientific / simulation analysis,
- spreadsheet / document extraction-analysis,
- video / audio perception-indexing,
- optimization / solver-based analytic workflows.

---

## Class 2 — Artifact Generator

**Count:** 17

**Core shape:**
A task dominated by producing a structured artifact with a tight output contract, often with a light review pass but without a deep multi-stage engineering loop.

**Typical signature:**
- `task_object = artifact-generation`
- often `single-step-with-review` or light `staged-multi-step`
- primary pattern often `generator`
- verifier is typically `deterministic-output-contract` or `deterministic-artifact-plus-stage-check`

**Representative members:**
- `offer-letter-generator`
- `court-form-filling`
- `dialogue-parser`
- `edit-pdf`
- `paper-anonymizer`
- `latex-formula-extraction`

**Current members:**
`court-form-filling`, `data-to-d3`, `dialogue-parser`, `edit-pdf`, `exceltable-in-ppt`, `latex-formula-extraction`, `lean4-proof`, `offer-letter-generator`, `paper-anonymizer`, `powerlifting-coef-calc`, `pptx-reference-formatting`, `protein-expression-analysis`, `python-scala-translation`, `suricata-custom-exfil`, `syzkaller-ppdev-syzlang`, `threejs-to-obj`, `weighted-gdp-calc`.

**Why this class is real:**
The reusable outer-loop object here is not “how to reason about a domain,” but rather:
**how to stabilize artifact contracts, no-invention discipline, schema fidelity, and formatting correctness.**

**Boundary note:**
Some members here are artifact-heavy but still pipeline-shaped (`data-to-d3`, `exceltable-in-ppt`, `pptx-reference-formatting`).
They remain here because the end-product contract dominates the task more than open-ended analysis or codebase evolution.

---

## Class 3 — Engineering Composition Bundle

**Count:** 15

**Core shape:**
A task centered on modifying, extending, debugging, migrating, or composing nontrivial code artifacts where correctness is governed by build/test/runtime/security behavior.

**Typical signature:**
- `task_object = engineering-composition`
- `workflow_topology = staged-multi-step`
- primary pattern almost always `pipeline`
- verifier often `benchmark-threshold` or strong behavior-based correctness checks
- tool surface frequently `tool-heavy-script-recommended`

**Representative members:**
- `parallel-tfidf-search`
- `fix-build-agentops`
- `fix-build-google-auto`
- `spring-boot-jakarta-migration`
- `react-performance-debugging`
- `fix-druid-loophole-cve`

**Current members:**
`crystallographic-wyckoff-position-analysis`, `find-topk-similiar-chemicals`, `fix-build-agentops`, `fix-build-google-auto`, `fix-druid-loophole-cve`, `fix-erlang-ssh-cve`, `fix-visual-stability`, `flink-query`, `jax-computing-basics`, `mhc-layer-impl`, `parallel-tfidf-search`, `react-performance-debugging`, `setup-fuzzing-py`, `simpo-code-reproduction`, `spring-boot-jakarta-migration`.

**Why this class is real:**
These tasks share an outer-loop object closer to:
**how to rewrite or compose multi-part technical systems under build/runtime/security constraints.**
This is the class most aligned with the current SkillX inner-loop rewrite story.

**Boundary note:**
A few tasks here are “build a reusable technical function/module” rather than classic debugging (`crystallographic-wyckoff-position-analysis`, `find-topk-similiar-chemicals`).
They still fit because they require engineering-style composition, reusable implementation choices, and correctness under downstream execution.

---

## Class 4 — Retrieval-Heavy Synthesis

**Count:** 10

**Core shape:**
A task where the main challenge is gathering grounded external information or workbook-backed evidence, then synthesizing it into a constrained answer/report/plan.

**Typical signature:**
- `task_object = retrieval-heavy-synthesis`
- `workflow_topology = staged-multi-step`
- primary pattern usually `pipeline`
- verifier usually `deterministic-output-contract` or `deterministic-artifact-plus-stage-check`

**Representative members:**
- `enterprise-information-search`
- `gh-repo-analytics`
- `sec-financial-report`
- `travel-planning`

**Current members:**
`enterprise-information-search`, `gh-repo-analytics`, `manufacturing-codebook-normalization`, `manufacturing-equipment-maintenance`, `organize-messy-files`, `reserves-at-risk-calc`, `sec-financial-report`, `shock-analysis-demand`, `shock-analysis-supply`, `travel-planning`.

**Why this class is real:**
These tasks want an outer-loop object like:
**how to retrieve the right evidence, preserve grounding, and compress it into a correct structured synthesis.**

**Split pressure:**
This class probably contains at least three subfamilies:
1. **search / answer / plan** tasks (`enterprise-information-search`, `gh-repo-analytics`, `sec-financial-report`, `travel-planning`)
2. **retrieve-into-workbook-model** tasks (`reserves-at-risk-calc`, `shock-analysis-demand`, `shock-analysis-supply`)
3. **reference-grounded normalization / compliance** tasks (`manufacturing-codebook-normalization`, `manufacturing-equipment-maintenance`)

`organize-messy-files` remains a mild edge case because it behaves like classification/review on top of content retrieval.

---

## Class 5 — Environment-Control / Planning

**Count:** 6

**Core shape:**
A task where the agent interacts with a simulator, formal planner, or dynamic environment whose behavior matters as much as the final artifact.

**Typical signature:**
- `task_object = environment-control`
- `workflow_topology = staged-multi-step`
- primary pattern `pipeline`
- verifier often `benchmark-threshold` or formal validity constraints

**Current members:**
`adaptive-cruise-control`, `glm-lake-mendota`, `hvac-control`, `pddl-tpp-planning`, `r2r-mpc-control`, `virtualhome-agent-planning`.

**Why this class is real:**
The reusable outer-loop object is not just “generate an output,” but:
**how to work against an executable environment, planner, or simulator with explicit dynamics / validity / control targets.**

**Split pressure:**
This class likely wants a future split into:
- **closed-loop control** (`adaptive-cruise-control`, `hvac-control`, `r2r-mpc-control`, `glm-lake-mendota`)
- **formal planning** (`pddl-tpp-planning`, `virtualhome-agent-planning`)

So this is probably a stable umbrella but not a final leaf taxonomy.

---

## Class 6 — Methodology-Heavy Guardrail

**Count:** 2

**Current members:**
`citation-check`, `taxonomy-tree-merge`

**Core shape:**
Tasks dominated by:
- fit checks,
- false-positive / premature-commitment control,
- abstention / merge discipline,
- and review-first reasoning over structure.

**Why this class matters despite its size:**
This class is behaviorally distinct.
Its outer-loop object is closer to:
**how to improve fit-checks, decision discipline, and anti-hallucination/anti-overcommit behavior**, not just generation quality.

**Interpretation:**
This class is small in SkillsBench, but strategically important for SkillX because it may correspond to high-value “meta” skills.
So low count should **not** automatically imply merge-away.

---

## Class 7 — Orchestration / Delegation

**Count:** 2

**Current members:**
`pg-essay-to-audiobook`, `scheduling-email-assistant`

**Core shape:**
Tasks that coordinate multiple external systems or action surfaces in one end-to-end workflow.

**Interpretation:**
This class is currently too small to promote with high confidence as a stable top-level ontology node.
It may end up being better represented as a **workflow/control overlay** on top of other classes.

For now it stays as a provisional class because it is visibly different from plain retrieval or artifact generation.

---

## 5. What seems most discriminative

## 5.1 Stable discriminators

### A. `task_object`
Best first-pass separator.

### B. `verifier_mode`
Best second separator.
Useful for distinguishing:
- benchmark-driven engineering/control tasks,
- strict schema artifact tasks,
- stage-sensitive pipeline tasks,
- abstention/fit-check tasks.

### C. `tool_surface_regime`
Helpful for separating:
- light artifact tasks,
- medium retrieval/document tasks,
- heavy script/simulator/codebase tasks.

## 5.2 Weak discriminators when used alone

### A. `primary_pattern`
Too collapsed (`pipeline = 71 / 89`).
Supports keeping Google 5 patterns as morphology only.

### B. `workflow_topology`
Also too collapsed (`staged-multi-step = 76 / 89`).
Useful only after `task_object` and `verifier_mode` are already known.

---

## 6. Edge cases and split/merge pressure

## 6.1 Biggest split pressure: Analytic Pipeline Bundle

This class is by far the largest (`37 / 89`).
It is almost certainly a temporary umbrella rather than a final leaf class.

Most likely future splits:
- scientific / signal / physics analysis
- spreadsheet / document extraction + analysis
- perception / multimodal media analysis
- optimization / solver-driven analytics

## 6.2 Environment-Control is probably two classes wearing one jacket

The control tasks and the PDDL planning tasks share “environment interaction,” but differ a lot in actual failure structure.
So this should probably split later.

## 6.3 Retrieval-Heavy Synthesis likely needs workbook vs open retrieval split

Workbook-grounded economics/finance tasks behave differently from API/search/report tasks.
This is a clear future split candidate.

## 6.4 Orchestration-Delegation may become an overlay, not a class

With only 2 members, it may be better modeled later as:
- a topology / control overlay,
- or an action-surface regime,
- not a full task-object class.

## 6.5 Methodology-Guardrail is small but should not be collapsed too early

This is exactly the kind of small-but-high-value class that might matter disproportionately for MetaSkill outer-loop research.

---

## 7. Medium-confidence audit bucket

After the local `tmp/skillsbench` audit pass, only one row remains `medium` in the current annotation layer:

- `PDF-Crosspage-Table-Normalization-to-Excel`

Reason:
- the GitHub task page exists, but the current `instruction.md` is empty (`0 bytes`), so this one still rests on a title-driven classification rather than a task-local instruction read.

This does not block the current v0.1 memo, but it is still the first audit target if that task later appears in a fuller local checkout or upstream fix.

---

## 8. Outer-loop takeaway for SkillX / UltraLoop

The strongest practical takeaway from this pass is:

> the outer loop should probably optimize **class-aware guidance objects keyed primarily by task object**, then refined by verifier shape and tool/control regime — not by Google pattern labels alone.

In other words:
- `task_object` says **what family of work this is**,
- `verifier_mode` says **how correctness is enforced**,
- `tool_surface_regime` says **what operating surface the optimizer must respect**,
- Google patterns say **what internal skill morphology is dominant inside the class**.

That is a much better starting point for MetaSkill design than trying to cluster on pattern labels directly.

---

## 9. Immediate next step

The most useful next artifact is **not** another generic taxonomy note.
It is a more operational follow-on:

1. pick the largest unstable umbrella (`analytic-pipeline`),
2. propose 2–4 candidate subclusters,
3. test whether those subclusters line up with:
   - verifier mode,
   - tool surface,
   - rewrite response,
   - and future inner-loop transfer behavior.

That would turn this v0.1 classification from a descriptive taxonomy into a genuine outer-loop hypothesis.

---

## 10. Candidate class-internal subcluster hypotheses (post-seed expansion)

After widening the second-pass seed overlay across representative tasks, the class picture is already more structured than the original v0.1 pass implied.

These are still **working hypotheses**.
For the MVP, they should be treated as:
- analysis-only structure,
- future split candidates,
- and experiment-slice aids,

not as:
- new clustering labels,
- a second runtime clustering layer,
- or separate optimization objects.

So the operative MVP stance remains:
- keep a **flat top-level class taxonomy**,
- keep the manual label count **below ~10**,
- and treat the subcluster view as a backlog for later evidence-based refinement.

### 10.1 Analytic Pipeline Bundle → likely 4 subclusters

#### A. Scientific / signal / simulation inference
Representative tasks:
- `earthquake-phase-association`
- `exoplanet-detection-period`
- `gravitational-wave-detection`
- `quantum-numerical-simulation`
- `seismic-phase-picking`

Common pattern:
- stage-sensitive scientific inference
- benchmark or correctness gates
- high sensitivity to intermediate processing quality

Likely outer-loop emphasis:
- `stronger_stage_contracts_help`
- sometimes `threshold-fragile`

#### B. Spreadsheet / document reconciliation pipelines
Representative tasks:
- `pdf-excel-diff`
- `sales-pivot-analysis`
- `xlsx-recover-data`
- `lab-unit-harmonization`

Common pattern:
- extraction / normalization / merge / workbook emission
- deterministic artifact contracts with fragile intermediate handoffs

Likely outer-loop emphasis:
- `stronger_stage_contracts_help`
- `stage-handoff-break`

#### C. Multimodal perception / indexing pipelines
Representative tasks:
- `dynamic-object-aware-egomotion`
- `speaker-diarization-subtitles`
- `video-tutorial-indexer`
- `video-filler-word-remover`
- `video-silence-remover`
- `pedestrian-traffic-counting`

Common pattern:
- multiple media-processing stages
- temporal alignment / segmentation / mask or subtitle artifacts
- many opportunities for silent intermediate degradation

Likely outer-loop emphasis:
- `stronger_stage_contracts_help`
- `stage-handoff-break`

#### D. Optimization / solver / report analytics
Representative tasks:
- `energy-ac-optimal-power-flow`
- `grid-dispatch-operator`
- `manufacturing-fjsp-optimization`
- `civ6-adjacency-optimizer`
- `mars-clouds-clustering`

Common pattern:
- structured optimization or search process
- score/feasibility driven outputs
- more gate-fragile than ordinary data-cleaning tasks

Likely outer-loop emphasis:
- `threshold-fragile`
- `stronger_stage_contracts_help`

### 10.2 Retrieval-Heavy Synthesis → likely 3 subclusters

#### A. Search / answer / planning synthesis
Representative tasks:
- `enterprise-information-search`
- `gh-repo-analytics`
- `sec-financial-report`
- `travel-planning`

Common pattern:
- retrieve relevant evidence
- compress it into structured answers or plans
- failure often comes from premature synthesis rather than missing pipeline stages alone

Likely outer-loop emphasis:
- `reviewer_logic_helps`
- `premature-commitment` or `stage-handoff-break`

#### B. Workbook-backed macro / finance synthesis
Representative tasks:
- `reserves-at-risk-calc`
- `shock-analysis-demand`
- `shock-analysis-supply`

Common pattern:
- retrieval plus workbook population and formula-based scenario modeling
- serial flow with constrained downstream spreadsheets

Likely outer-loop emphasis:
- `stronger_stage_contracts_help`
- `stage-handoff-break`

#### C. Reference-grounded normalization / compliance synthesis
Representative tasks:
- `manufacturing-codebook-normalization`
- `manufacturing-equipment-maintenance`
- `organize-messy-files`

Common pattern:
- compare messy inputs against a reference taxonomy, handbook, or target folder ontology
- abstention / conservative mapping behavior matters more than elaborate generation

Likely outer-loop emphasis:
- `reviewer_logic_helps`
- `premature-commitment`
- sometimes `model-sensitivity-high`

### 10.3 Environment-Control / Planning → likely 2 subclusters

#### A. Closed-loop control / calibration
Representative tasks:
- `adaptive-cruise-control`
- `glm-lake-mendota`
- `hvac-control`
- `r2r-mpc-control`

Common pattern:
- configure model/controller
- run simulation or calibration loop
- satisfy explicit metric thresholds

Likely outer-loop emphasis:
- `threshold-fragile`
- `stronger_stage_contracts_help`

#### B. Formal planning
Representative tasks:
- `pddl-tpp-planning`
- `virtualhome-agent-planning`

Common pattern:
- parse formal domain/problem definitions
- generate valid plans under syntax and semantics constraints

Likely outer-loop emphasis:
- `precedence-conflict`
- `stronger_stage_contracts_help`

### 10.4 Artifact Generation → likely 3 subclusters

#### A. Strict schema / document artifact generation
Representative tasks:
- `offer-letter-generator`
- `court-form-filling`
- `dialogue-parser`
- `edit-pdf`
- `paper-anonymizer`
- `latex-formula-extraction`

Likely outer-loop emphasis:
- `placeholder-invention`
- `reviewer_logic_helps` or `inversion_helps`

#### B. Presentation / workbook transformation artifacts
Representative tasks:
- `exceltable-in-ppt`
- `pptx-reference-formatting`
- `powerlifting-coef-calc`
- `protein-expression-analysis`
- `weighted-gdp-calc`

Likely outer-loop emphasis:
- `stage-handoff-break`
- `stronger_stage_contracts_help`

#### C. Formal / code-like artifact emission
Representative tasks:
- `lean4-proof`
- `python-scala-translation`
- `syzkaller-ppdev-syzlang`
- `threejs-to-obj`

Likely outer-loop emphasis:
- `threshold-fragile` or `placeholder-invention`
- often `extra_generic_scaffolding_hurts`

### 10.5 Engineering Composition → likely 3 subclusters

#### A. Build / migration / product debugging
Representative tasks:
- `fix-build-agentops`
- `fix-build-google-auto`
- `spring-boot-jakarta-migration`
- `react-performance-debugging`
- `fix-visual-stability`

#### B. Security / robustness patching
Representative tasks:
- `fix-druid-loophole-cve`
- `fix-erlang-ssh-cve`
- `setup-fuzzing-py`

#### C. Module / algorithm implementation bundles
Representative tasks:
- `crystallographic-wyckoff-position-analysis`
- `find-topk-similiar-chemicals`
- `flink-query`
- `jax-computing-basics`
- `mhc-layer-impl`
- `simpo-code-reproduction`
- `parallel-tfidf-search`

This class still looks unified enough to keep as one top-level object, but these subclusters likely matter for future rewrite-response transfer.

### 10.6 Why this matters for the outer loop

The subcluster view is useful because it shows where the current flat classes may later want to split.
But for the MVP, the correct readout is **not** “adopt a two-level hierarchy now.”

The correct MVP readout is:
- keep the outer-loop clustering object **flat** at the top-level class layer,
- keep manual class count **below ~10**,
- use lightweight tags / quantitative signals to support later automatic clustering,
- and only promote a subcluster into a real cluster if later evidence shows that:
  1. sample size is sufficient,
  2. the subcluster has stable quantitative separation,
  3. and the split improves optimization / transfer behavior.

So for now, the subcluster material should be interpreted as **analysis backlog**, not as the MVP architecture.
