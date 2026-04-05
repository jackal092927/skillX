# SkillX Task Clustering and Taxonomy v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-03-31
- **Role:** design memo for the first interpretable-to-data-corrected clustering scheme in the SkillX / UltraLoop line
- **Status:** working design proposal

---

## 1. Why this document exists

The project already has a strong two-loop framing:

- **Inner Loop / Skill Optimizer** = optimize a concrete skill on a concrete task
- **Outer Loop / MetaSkill / UltraLoop** = aggregate evidence across many inner-loop runs and learn reusable guidance for a class of tasks

That framing immediately creates a scientific design question:

> **How should tasks be clustered so the outer loop learns the right reusable object?**

A purely domain-based taxonomy is too weak.
A raw trajectory-based clustering scheme is also risky, because tool-calling behavior is highly model-dependent.

This memo proposes a first answer:

> **Start from a manually defined, human-interpretable task taxonomy, then refine it using trajectory-derived but model-robust middle-layer signals.**

This is intended as the first concrete clustering design for the SkillX / UltraLoop line.

---

## 2. Main stance

### 2.1 Start with an interpretable taxonomy

The first taxonomy should be understandable by a human researcher without embeddings, latent clusters, or opaque representations.

Why?
Because the first role of the taxonomy is not only compression. It is also:
- experiment design,
- outer-loop object definition,
- failure analysis,
- transfer evaluation,
- and template-family naming.

So the initial taxonomy should be:
- small (for the MVP, target **no more than ~10 manual labels**),
- explicit,
- auditable,
- easy to relabel,
- easy to split/merge later.

### 2.2 Do **not** cluster raw trajectories directly

Trace2Skill suggests that execution traces contain valuable information.
That is correct.
But raw trajectories are also highly contaminated by:
- model family,
- model version,
- runtime wrapper,
- sampling style,
- exploration habit,
- tool-ordering preference,
- verbosity,
- and local prompt wording.

Therefore:

> **UltraLoop should not treat raw tool-call sequences as the primary clustering object.**

Instead, it should extract more stable signals from runs and cluster those.

### 2.3 UltraLoop is an aggregation loop, not a single-run reaction loop

The intended outer loop is not:
- run one task,
- see one outcome,
- immediately rewrite the class template.

Instead, the intended behavior is:
- gather many inner-loop runs from plausibly similar skills/tasks,
- aggregate evidence,
- summarize stable patterns,
- then update the class-level object.

This means the clustering system should be designed for:
- aggregation,
- robustness,
- cross-run comparison,
- and delayed update.

### 2.4 MVP simplification rule

For the MVP, the clustering architecture should stay **flat and lightweight**.

Concretely:
- use a **single-layer clustering surface**,
- keep the number of manual clustering labels **below ~10**,
- minimize manually imposed inductive bias,
- and push as much future refinement as possible into **extracted semantic/topology signals plus run-derived response signals** rather than hand-authored hierarchy.

This means that, in the MVP:
- `task_object` is the main **manual seed label** space,
- `verifier_mode`, `workflow_topology`, and `tool_surface_regime` are allowed to participate in the flat clustering input as structured features,
- while fields like `primary_pattern`, `secondary_patterns`, `risk_profile`, and `rewrite_response_hypothesis` should remain **auxiliary tags / hypotheses**,
- not extra clustering levels,
- and not separate runtime optimization objects.

Subclusters may still be recorded during analysis, but only as:
- future split candidates,
- hypothesis-tracking structure,
- or experiment-slice aids.

They should **not** be operationalized as a second clustering layer in the MVP.

---

## 3. Source map: what prior materials contribute

The current design should not be derived from one source only. Different sources contribute different layers.

### 3.1 Anthropic / advanced tool use line

Relevant local notes:
- `knowledge/harness-engineering/notes/2-anthropic-advanced-tool-use.md`
- `workspace-christina/knowledge-base/interview-agentic-ai/12_harness-engineering-and-advanced-tool-use.md`

What this line contributes:
- a **control decomposition** for agent work:
  - discovery / routing,
  - execution / orchestration,
  - invocation fidelity.
- a practical way to think about where a task or skill fails:
  - selecting the right capability,
  - structuring the workflow around tools,
  - or calling tools correctly.

This does **not** provide a full task taxonomy by itself.
But it gives an important lens for classifying workflow shape.

### 3.2 Skill survey / SoK line

Relevant local notes:
- `knowledge/evolution/deep-reads/agent-skills-survey-2602.12430-cycle21a.md`
- `knowledge/evolution/deep-reads/sok-agentic-skills-2602.20867-cycle13b.md`

What this line contributes:
- a formal skill object:
  - applicability condition,
  - policy,
  - termination,
  - reusable interface.
- a skill lifecycle:
  - discovery,
  - practice,
  - distillation,
  - storage,
  - composition,
  - evaluation,
  - update.
- a system-level vocabulary for talking about skill packaging and composition.

This is useful for defining what kind of reusable object the outer loop should eventually learn.

### 3.3 Harness / framework / industrial-system line

Relevant local note:
- `workspace-christina/knowledge-base/system-design-openclaw/harness-framework-agent-framework-survey-2026-03-29.md`

What this line contributes:
- a realistic industrial layering of agent systems:
  - framework / SDK,
  - managed runtime / deployment,
  - coding-agent runtime,
  - orchestration harness.

This matters because many task differences are not merely topical.
They are also differences in:
- execution surface,
- workflow topology,
- orchestration burden,
- and runtime assumptions.

### 3.4 Google 5-pattern lens

Relevant local note:
- `docs/research/deep-dives/2026-03-30-google-5-patterns-to-skillx-mapping.md`

What this line contributes:
- a useful **internal skill morphology layer**:
  - Tool Wrapper,
  - Generator,
  - Reviewer,
  - Inversion,
  - Pipeline.

This should remain a descriptive mid-layer, not the main outer-loop ontology.

---

## 4. The central design claim

The clustering system should combine three things:

1. **task objective / work object**
2. **workflow topology / control regime**
3. **skill morphology / internal structure**

In short:

> **Task class says what kind of reusable outer-loop object we want.**
> **Workflow topology says how the task is operationally solved.**
> **Pattern labels say what internal structure dominates the skill content.**

That three-layer representation is more useful than:
- pure topic labels,
- pure raw-trajectory similarity,
- or pure Google-pattern labels.

---

## 5. Proposed clustering representation

Each task should receive a compact structured profile.

### 5.1 Proposed profile schema

```yaml
task_profile:
  task_object: analytic-pipeline
  workflow_topology: staged-multi-step
  tool_surface_regime: tool-heavy-script-recommended
  verifier_mode: deterministic-artifact-plus-stage-check
  primary_pattern: pipeline
  secondary_patterns:
    - tool-wrapper
    - reviewer
  risk_profile:
    - scaffold-sensitive
    - negative-transfer-sensitive
  dominant_failure_mode: stage-handoff-break
  rewrite_response_hypothesis:
    - stronger_stage_contracts_help
    - reviewer_logic_helps
    - extra_generic_scaffolding_hurts
```

### 5.2 Required fields

#### `task_object`
The main work object the agent is producing or resolving.
Examples:
- `artifact-generation`
- `analytic-pipeline`
- `engineering-composition`
- `methodology-guardrail`

#### `workflow_topology`
The shape of the process needed to complete the task.
Examples:
- `single-step`
- `single-step-with-review`
- `staged-multi-step`
- `multi-skill-composition`
- `branching-abstention-aware`
- `orchestration-heavy`

#### `tool_surface_regime`
How much the task depends on tools, scripts, environment structure, and orchestration.
Examples:
- `tool-light`
- `tool-medium`
- `tool-heavy-script-optional`
- `tool-heavy-script-recommended`
- `runtime-bootstrap-sensitive`

#### `verifier_mode`
How correctness is primarily judged.
Examples:
- `deterministic-output-contract`
- `deterministic-artifact-plus-stage-check`
- `benchmark-threshold`
- `human-judgment-heavy`
- `abstention-and-fit-check`

#### `primary_pattern` / `secondary_patterns`
Internal skill morphology labels, reused from the Google 5-pattern lens.
These are not the outer-loop object. They are descriptive structure labels.

#### `risk_profile`
One or more likely failure-sensitivity labels.
Examples:
- `negative-transfer-sensitive`
- `scaffold-sensitive`
- `timeout-sensitive`
- `composition-confusion-sensitive`
- `model-sensitivity-high`
- `threshold-fragile`

#### `dominant_failure_mode`
The most likely dominant failure class.
Examples:
- `placeholder-invention`
- `stage-handoff-break`
- `precedence-conflict`
- `premature-commitment`
- `same-artifact-score-instability`

#### `rewrite_response_hypothesis`
A first hypothesis about which kinds of rewrite operations are likely to help or hurt.
Examples:
- `stronger_stage_contracts_help`
- `bundle_manifest_clarity_helps`
- `reviewer_logic_helps`
- `inversion_helps`
- `extra_generic_scaffolding_hurts`

This field is especially important because it links clustering to the outer-loop update target.

---

## 6. Initial interpretable task classes

The initial taxonomy should remain small.
The current strongest four-class seed remains reasonable.

### Class A — Artifact Generator

#### Definition
Tasks whose main job is to transform inputs into a structured output artifact with a clear contract.

#### Typical properties
- `task_object`: `artifact-generation`
- `workflow_topology`: `single-step-with-review`
- `tool_surface_regime`: `tool-light`
- `verifier_mode`: `deterministic-output-contract`
- `primary_pattern`: `generator`
- `secondary_patterns`: `reviewer`

#### Typical failure modes
- content invention,
- placeholder misuse,
- contract drift,
- formatting mismatch.

#### Likely rewrite-response profile
- stronger output contracts help,
- lightweight reviewer logic helps,
- verbose generic guidance often hurts.

---

### Class B — Engineering Composition Bundle

#### Definition
Tasks where multiple skills or guidance sources must be coordinated for one engineering goal.

#### Typical properties
- `task_object`: `engineering-composition`
- `workflow_topology`: `multi-skill-composition`
- `tool_surface_regime`: `tool-medium` to `tool-heavy-script-recommended`
- `verifier_mode`: `benchmark-threshold` or integration-style correctness
- `primary_pattern`: `pipeline` or `tool-wrapper`
- `secondary_patterns`: `reviewer`

#### Typical failure modes
- skill precedence conflict,
- over-optimization for one objective,
- unclear role partition,
- bundle-level drift.

#### Likely rewrite-response profile
- clearer bundle manifest helps,
- precedence rules help,
- reviewer/checking logic helps,
- excess redundant guidance can cause composition confusion.

---

### Class C — Analytic Pipeline Bundle

#### Definition
Tasks requiring ordered intermediate stages, explicit handoff contracts, and stage-sensitive correctness.

#### Typical properties
- `task_object`: `analytic-pipeline`
- `workflow_topology`: `staged-multi-step`
- `tool_surface_regime`: `tool-heavy-script-recommended`
- `verifier_mode`: `deterministic-artifact-plus-stage-check`
- `primary_pattern`: `pipeline`
- `secondary_patterns`: `tool-wrapper`, `reviewer`

#### Typical failure modes
- stage confusion,
- malformed intermediate artifacts,
- handoff break,
- locally plausible but evaluator-incompatible outputs.

#### Likely rewrite-response profile
- stronger stage contracts help,
- explicit handoff artifact definitions help,
- reviewer logic helps,
- monolithic generic scaffolding hurts.

This remains the strongest first class for outer-loop learning.

---

### Class D — Methodology-Heavy Guardrail Task

#### Definition
Tasks where the main difficulty is choosing the right methodological stance, checking fit, abstaining when necessary, and avoiding premature commitment.

#### Typical properties
- `task_object`: `methodology-guardrail`
- `workflow_topology`: `branching-abstention-aware`
- `tool_surface_regime`: `tool-light` to `tool-medium`
- `verifier_mode`: `abstention-and-fit-check`
- `primary_pattern`: `inversion`
- `secondary_patterns`: `reviewer`, sometimes `pipeline`

#### Typical failure modes
- wrong-fit commitment,
- assumption leakage,
- false certainty,
- premature tree expansion.

#### Likely rewrite-response profile
- inversion helps,
- fit-checks help,
- abstention-aware reviewer logic helps,
- generator-style forward execution often hurts.

---

## 7. What UltraLoop should cluster

### 7.1 Cluster trajectory-derived middle-layer signals

The best clustering signals are not raw action sequences.
They are extracted signals that are more likely to survive model changes.

#### A. Topology signals
- single-step vs multi-step
- stage count
- need for intermediate artifacts
- branching / abstention structure
- multi-skill composition burden

#### B. Tool-surface signals
- tool-light vs tool-heavy
- script dependency
- environment bootstrap sensitivity
- need for programmatic orchestration
- need for explicit wrappers / adapters

#### C. Verifier signals
- deterministic checker presence
- threshold-based evaluation
- stage-level verifiability
- contract vs benchmark vs human-judgment emphasis

#### D. Failure-mode signals
- timeout sensitivity
- threshold fragility
- stage-handoff fragility
- composition confusion
- premature commitment
- same-artifact score instability

#### E. Rewrite-response signals
- reviewer strengthening helps?
- pipeline strengthening helps?
- tool-wrapper strengthening helps?
- inversion helps?
- guidance deletion/simplification helps?

This last category is the most directly useful for outer-loop learning.

### 7.2 Why rewrite-response signals matter most

The outer loop is not trying only to say:
- “these tasks look similar.”

It is trying to say:
- “these tasks respond similarly to the same kinds of meta-level skill updates.”

That is a much more useful clustering target.

So the strongest long-term clustering criterion is:

> **Tasks belong together if they reliably benefit from similar classes of meta-level rewrite operations under similar verifier and failure conditions.**

---

## 8. Guardrails against model-dependent noise

The clustering algorithm should explicitly protect itself against model-dependent trajectory noise.

### 8.1 Never use raw tool-call order as the primary clustering object

Tool order is too entangled with:
- model behavior,
- prompt wording,
- and runtime wrapper idiosyncrasy.

It may still be a secondary diagnostic signal, but not the main basis of class formation.

### 8.2 Log model/runtime metadata for every run bundle

At minimum, each run bundle used by UltraLoop should record:
- model family,
- model version,
- runtime wrapper,
- tool registry version,
- prompt/skill baseline version,
- verifier version.

Without this, clustering noise cannot be normalized.

### 8.3 Prefer artifact- and verifier-grounded signals over reasoning-style signals

Signals tied to:
- artifacts,
- scores,
- failures,
- verifier outcomes,
- rewrite diffs,
- and rerun stability

are more trustworthy than signals tied to:
- rhetorical style,
- verbosity,
- chain length,
- or tool-call narration.

### 8.4 Require repeated evidence before class update

A single run should almost never trigger a class split or merge.

A class update should require evidence across:
- multiple tasks,
- multiple runs,
- ideally multiple model/runtime settings,
- or at least multiple independent restarts.

This matches the intended UltraLoop behavior.

---

## 9. Proposed UltraLoop clustering pipeline

### Stage 0 — seed manual labels
Annotate tasks with the initial interpretable taxonomy.
This is the bootstrap ontology.

### Stage 1 — collect inner-loop evidence bundles
For each task, gather:
- run traces,
- verifier outputs,
- scores,
- rewrite diffs,
- failure summaries,
- rerun stability information,
- and current skill/template metadata.

### Stage 2 — derive stable middle-layer signals
Transform raw evidence into:
- topology features,
- verifier features,
- failure features,
- rewrite-response features.

### Stage 3 — aggregate within tentative class
For each tentative class, summarize:
- common failure patterns,
- common rewrite-response patterns,
- common verifier shapes,
- common tool-surface regimes.

### Stage 4 — propose split / merge / relabel operations
These proposals should be explicit and reviewable.
For example:
- split one class into two,
- merge two near-identical classes,
- relabel a class because its current name hides the dominant structure.

### Stage 5 — validate by transfer, not only fit
A class update is good if it improves:
- same-class transfer,
- stability,
- rewrite efficiency,
- or negative-transfer rate.

It is **not** enough that it merely explains past traces more neatly.

---

## 10. Split / merge criteria

### 10.1 Split a class when
A class should be split if tasks inside it show persistent divergence in:
- dominant failure mode,
- verifier regime,
- rewrite-response profile,
- or topology shape.

Example:
if one nominal class contains both:
- threshold-fragile benchmark tasks,
- and abstention-heavy guardrail tasks,

then it is probably too coarse.

### 10.2 Merge classes when
Two classes should be merged if they repeatedly show similar:
- rewrite-response patterns,
- verifier assumptions,
- failure signatures,
- and template needs,

and if the distinction is mostly topical rather than operational.

### 10.3 Do not split or merge using topic alone
A difference in subject matter is not enough.
The question is whether the outer loop should learn a different reusable object.

---

## 11. Relation to the MetaSkill object

The purpose of clustering is not taxonomy for its own sake.
It is to define the object learned by the outer loop.

That object should eventually become a class-level **MetaSkill harness** rather than only a free-form meta prompt.

A future class-level object may look like:

```yaml
meta_skill_harness:
  class_name: analytic-pipeline
  bootstrap:
    include:
      - latest_verifier_signature
      - prior_round_diff_summary
      - unresolved_failure_points
  rewrite_prior:
    emphasize:
      - stage_contracts
      - handoff_artifacts
      - reviewer_before_finalize
    avoid:
      - generic_verbose_scaffolding
  evaluator_focus:
    - stage_correctness
    - handoff_integrity
    - rerun_stability
  stopping_policy:
    stop_if:
      - two_rounds_no_structural_gain
      - instability_persists_after_simplification
```

This is the deeper reason the clustering must be operationally meaningful.

---

## 12. Immediate next steps

### 12.1 Annotate the current core task slice
Start with at least:
- `offer-letter-generator`
- `parallel-tfidf-search`
- `trend-anomaly-causal-inference`
- `taxonomy-tree-merge`

using the new profile fields.

### 12.2 Define a minimal run-signal extraction schema
This has now been concretized in:
- `docs/plans/skillx/skillx-mvp-automatic-clustering-input-schema-v0.1.md`

That schema now tightens the MVP direction to:
- **flat clustering only**,
- **< 10 manual labels**,
- **task-level aggregate records** as the clustering unit,
- **semantic / contract + tool-topology** as the primary clustering input,
- **optimization-response signals** as secondary correction / validation input,
- and lightweight tags as auxiliary audit features only.

### 12.3 Use the schema in one UltraLoop-style aggregation pass
Next, materialize one task-level aggregate artifact (e.g. JSONL) from the schema and run one automatic clustering pass over a small task slice.

The immediate question is no longer “do subclusters look interesting?”
It is:
- can a flat hybrid clustering pass run end-to-end,
- does it produce stable, interpretable groups,
- and is it useful enough to support the next auto-loop optimization step?

### 12.4 Keep the taxonomy revisable
The first taxonomy is a scaffold, not a truth.
Its value lies in helping the outer loop become measurable and correctable.

---

## 13. Bottom line

The best first clustering strategy for SkillX / UltraLoop is:

> **small flat seed taxonomy**
> + **semantic / contract + tool-topology primary inputs**
> + **optimization-response signals for correction and validation**
> + **class updates driven by transfer and optimization evidence**

This preserves interpretability, avoids raw-trajectory overfitting, avoids collapsing everything into outcome-only similarity, respects the MVP constraint against overcomplicated hierarchy, and keeps the clustering system aligned with the actual outer-loop goal: learning reusable class-level MetaSkill guidance.
