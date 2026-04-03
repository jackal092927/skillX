# SkillX Task-Class Taxonomy and MetaEvolver Design v0.1

- **Project:** `projects/multi-agent-protocol-design`
- **Date:** 2026-03-25
- **Role:** proposal for adding task-class-aware outer-loop structure to the current SkillX line
- **Status:** design memo after MARC two-loop reframing

---

## 1. Why this document exists

The project has now been reframed around a clearer two-loop story:

- **Inner Loop** = refine a concrete skill on a concrete task using traces, verifier outputs, and performance deltas
- **Outer Loop / MetaEvolver** = learn reusable guidance about what a skill should look like for a **class of tasks**

This immediately creates a design question:

> **How should we classify SkillsBench tasks so that the outer loop has a meaningful object to optimize?**

A generic answer like “all skills” is too coarse.
A purely domain-only answer like “NLP vs document vs science” is also too weak.

The proposal in this memo is:

> **SkillsBench tasks should be classified primarily by task shape and skill-usage topology, not just by topical domain.**

That task-class label then determines the first candidate **skill template family** for outer-loop learning.

---

## 2. Main design stance

### 2.1 Do not replace the current SkillX baseline
This memo does **not** replace the current baseline:
- `C0` / `C1` / `C2` / `C3` / `C4`
- minimal rewrite
- derived expansion
- bounded refine

Instead, it proposes a new overlay:

> **task-class-aware template guidance**

The current baseline remains the control line.
The new layer becomes the first concrete object for the outer loop.

### 2.2 Classify by behavior, not just topic
A task should not be classified only as “document”, “NLP”, or “science”.
Those domain labels are still useful metadata, but they are not enough to drive template design.

Instead, each task should be classified by:
1. **task shape** — what kind of process the agent must execute
2. **skill topology** — single skill, bundle, staged pipeline, etc.
3. **risk profile** — likely positive-skill, likely negative-transfer, over-guidance-sensitive, etc.

---

## 3. Proposed classification scheme

Each SkillsBench task should receive a small structured profile.

### 3.1 Required task-class fields

```yaml
task_class_profile:
  task_class: analytic-pipeline
  skill_topology: multi-skill-staged-bundle
  primary_pattern: pipeline
  secondary_patterns:
    - tool-wrapper
    - reviewer
  risk_profile:
    - negative-transfer-sensitive
    - scaffold-sensitive
  verifier_mode: deterministic-artifact-plus-stage-check
  scaffold_budget: medium
  script_policy: recommended
```

### 3.2 Field meanings

#### `task_class`
The main family of task behavior.

#### `skill_topology`
How many skills are involved and how they interact:
- `single-skill`
- `single-skill-with-helper-resources`
- `multi-skill-flat-bundle`
- `multi-skill-staged-bundle`
- `guardrail-heavy-single-skill`

#### `primary_pattern` / `secondary_patterns`
Reuse the lightweight pattern-awareness lens:
- `tool-wrapper`
- `generator`
- `reviewer`
- `inversion`
- `pipeline`

#### `risk_profile`
One or more risk labels such as:
- `likely-positive-skill`
- `negative-transfer-sensitive`
- `over-guidance-sensitive`
- `scope-drift-sensitive`
- `composition-confusion-sensitive`
- `model-sensitivity-high`

#### `verifier_mode`
The main acceptance shape for the task.

#### `scaffold_budget`
A first hypothesis about how much guidance this task family can tolerate:
- `low`
- `medium`
- `high`

#### `script_policy`
Whether scripts are:
- `discouraged`
- `optional`
- `recommended`
- `required`

---

## 4. Initial candidate task classes

The following classes are designed to be useful **now**, based on the current SkillsBench slice we have already touched.

### Class A — Artifact Generator

#### Definition
Tasks where the agent mainly transforms input into a structured output artifact with a clear contract.

#### Typical examples
- `offer-letter-generator`

#### Typical pattern mix
- primary: `generator`
- secondary: `reviewer` or lightweight `tool-wrapper`

#### Main failure modes
- losing template structure
- inventing content
- placeholder misuse
- formatting drift

#### Candidate template shape
A good template for this class should emphasize:
- output contract
- required inputs / placeholders
- preserve-structure rules
- forbidden invention rules
- compact acceptance checklist
- style/template reference files when necessary

#### Scaffold budget
- usually **low to medium**
- stronger models likely need less prose, not more

#### Script policy
- usually `optional`
- use scripts only if deterministic document inspection helps

#### Design note
This is a good class for testing whether lighter templates beat verbose guidance.

---

### Class B — Engineering Composition Bundle

#### Definition
Tasks where multiple skills contribute overlapping but distinct operational advice for one engineering goal.

#### Typical examples
- `parallel-tfidf-search`

#### Typical pattern mix
- primary: `pipeline` or `tool-wrapper`
- secondary: `reviewer`

#### Main failure modes
- overlapping skill triggers
- unclear precedence among skills
- overemphasis on one objective (e.g. speed) at the expense of correctness
- local optimization harming system-level outcome

#### Candidate template shape
A good template for this class should emphasize:
- bundle manifest
- role of each skill in the bundle
- precedence / conflict-resolution policy
- primary objective vs secondary objectives
- correctness-before-performance rule
- explicit interaction note
- optional profiling / verification scripts

#### Scaffold budget
- usually **medium**
- enough structure to coordinate bundle roles, but not so much that each skill becomes bloated

#### Script policy
- `recommended`
- especially for performance or equivalence verification

#### Design note
This class is the natural stress test for multi-skill story credibility.

---

### Class C — Analytic Pipeline Bundle

#### Definition
Tasks that require ordered transformation through several intermediate analytic stages, where each stage has a distinct artifact and failure mode.

#### Typical examples
- `trend-anomaly-causal-inference`
- `exoplanet-detection-period`
- `energy-ac-optimal-power-flow`

#### Typical pattern mix
- primary: `pipeline`
- secondary: `tool-wrapper`, sometimes `reviewer`

#### Main failure modes
- stage confusion
- malformed intermediate artifacts
- leakage across stages
- incorrect handoff semantics
- evaluator-incompatible outputs despite locally plausible reasoning

#### Candidate template shape
A good template for this class should emphasize:
- stage graph / stage ordering
- one skill per stage where possible
- handoff contract between stages
- data invariants and type constraints
- failure conditions per stage
- stage-level acceptance checks
- bundle-level end-to-end acceptance criteria
- scripts for deterministic validation where feasible

#### Scaffold budget
- usually **medium to high**, but **localized by stage**
- guidance should be distributed across stages, not accumulated in one monolithic derived layer

#### Script policy
- `recommended` to `required`
- especially when stage outputs can be checked automatically

#### Design note
This is likely the most important first class for outer-loop learning, because it is where structure genuinely matters and where C3/C4 already produced signal.

---

### Class D — Methodology-Heavy Guardrail Task

#### Definition
Tasks where the original skill is highly prescriptive, methodology-heavy, or brittle, and the main question is how to reduce harmful overcommitment.

#### Typical examples
- `taxonomy-tree-merge`
- also potentially some hard scientific / reasoning tasks with over-strong process priors

#### Typical pattern mix
- primary: `inversion` or `reviewer`
- secondary: `pipeline` or `tool-wrapper`

#### Main failure modes
- premature commitment to one method
- false precision
- brittle assumptions
- unnecessary methodological overreach
- negative transfer from a skill that is too strong for the actual task instance

#### Candidate template shape
A good template for this class should emphasize:
- when-to-use / when-not-to-use boundaries
- assumption checklist
- clarifying-question block
- abstention / branch conditions
- compact caution list
- negative examples / anti-patterns
- lightweight acceptance criteria focused on avoiding harmful overcommitment

#### Scaffold budget
- usually **low to medium**
- this class is especially sensitive to over-guidance

#### Script policy
- usually `optional`
- scripts help less than good boundaries and good abstention rules

#### Design note
For this class, **deletion** is likely a first-class refine operator, not just simplification.

---

### Class E — Knowledge Transfer / Knowledge-Base Construction

#### Definition
Tasks where the main job is not solving a one-shot problem but extracting, organizing, merging, or updating reusable knowledge.

#### Typical examples
- not yet central in the current dry run, but likely important for the outer-loop vision and future task families

#### Typical pattern mix
- primary: `generator` or `reviewer`
- secondary: `pipeline`, sometimes `inversion`

#### Main failure modes
- weak provenance
- poor deduplication
- incoherent schema
- shallow synthesis
- accumulation of unverifiable statements

#### Candidate template shape
A good template for this class should emphasize:
- source/provenance policy
- extraction schema
- merge / dedup rules
- update policy
- evidence traceability
- verification against source coverage

#### Scaffold budget
- usually **medium**

#### Script policy
- `optional` to `recommended`
- especially for schema validation and dedup support

#### Design note
This class may become important once MARC shifts from single benchmark loops to community knowledge accumulation.

---

### Class F — Workflow Automation

#### Definition
Tasks centered on reliably executing a fixed operational process across tools or states.

#### Typical examples
- not central in the current dry run, but likely important for future broader benchmark coverage

#### Typical pattern mix
- primary: `pipeline`
- secondary: `reviewer` or `tool-wrapper`

#### Main failure modes
- skipped steps
- bad checkpointing
- missing rollback conditions
- fragile state assumptions

#### Candidate template shape
A good template for this class should emphasize:
- ordered stages
- checkpoints / gates
- state assumptions
- rollback rules
- logging behavior
- executable helper scripts/drivers

#### Scaffold budget
- usually **medium**

#### Script policy
- often `recommended` or `required`

---

## 5. Mapping the current known SkillsBench tasks

This is the first concrete mapping for tasks we have already touched.

| Task | Proposed Class | Skill Topology | Risk Prior | Template Direction |
|---|---|---|---|---|
| `offer-letter-generator` | Artifact Generator | single-skill | positive-skill / low-scaffold | compact generator template |
| `parallel-tfidf-search` | Engineering Composition Bundle | multi-skill-flat-bundle | composition-confusion | bundle manifest + precedence template |
| `trend-anomaly-causal-inference` | Analytic Pipeline Bundle | multi-skill-staged-bundle | negative-transfer + stage-confusion | stage graph + handoff contracts |
| `exoplanet-detection-period` | Analytic Pipeline Bundle | multi-skill-staged-bundle | stage-confusion + contract-completion risk | stage-local structure + required outputs |
| `energy-ac-optimal-power-flow` | Analytic Pipeline Bundle | multi-skill-staged-bundle | stage-confusion + contract-completion risk | stage-local structure + deterministic checks |
| `taxonomy-tree-merge` | Methodology-Heavy Guardrail Task | guardrail-heavy-single-skill | over-guidance-sensitive | lean boundary / assumption / abstention template |

---

## 6. How this should modify the current project design

### 6.1 Add a new outer-loop object
Right now the main experimental object is the rewritten skill.
We should add a second explicit object:

> **task-class template family**

This becomes the first concrete object for MetaEvolver.

### 6.2 Keep the current C0–C4 baseline, but add task-class annotation
Do **not** replace the current experimental ladder.
Instead, annotate each task in `rewrite_registry/` with:
- task class
- skill topology
- pattern family
- risk profile
- scaffold budget prior
- script policy prior

This gives us a structured substrate for later outer-loop analysis without breaking current comparability.

### 6.3 Change the meaning of C2 and C3 in later variants
Not immediately for the baseline, but for the next design iteration:

- **Current C2** = generic SkillX minimal rewrite
- **Future class-aware C2** = template-instantiated minimal rewrite
- **Current C3** = generic agent-derived expansion
- **Future class-aware C3** = template-guided derived expansion

This gives a natural comparison:
- generic SkillX vs class-aware SkillX

### 6.4 Make C4 class-aware before making it fully outer-loop adaptive
The first safe outer-loop modification is not to let the protocol mutate freely.
It is to let the frozen `C4` protocol consume a **task-class prior**.

For example:
- for Artifact Generator tasks, C4 should bias toward compression and preserve output contract
- for Analytic Pipeline tasks, C4 should bias toward handoff clarity and stage verification
- for Guardrail tasks, C4 should bias toward deletion, abstention, and anti-overcommitment

This is a clean intermediate step between:
- current frozen generic C4
- future evolving MetaEvolver

### 6.5 Redesign the 12-task pilot matrix
The future 12-task pilot should not be sampled only by broad diversity + positive/negative cases.
It should also ensure **task-class coverage**.

Recommended target:
- at least 2 tasks from Artifact Generator / simple structured output
- at least 2 tasks from Engineering Composition Bundle
- at least 3–4 tasks from Analytic Pipeline Bundle
- at least 2 tasks from Methodology-Heavy / Guardrail-sensitive cases
- remaining slots for Knowledge Transfer / Workflow Automation if available in the benchmark

This makes the pilot interpretable from the outer-loop perspective.

---

## 7. First concrete implementation proposal

A tractable next step is:

### Step 1 — Annotate all currently touched tasks
Add `task_class_profile.yaml` for the current 6 tasks.

### Step 2 — Write 3–4 template-family skeletons
Do not attempt full universal coverage yet.
Start with:
- Artifact Generator
- Engineering Composition Bundle
- Analytic Pipeline Bundle
- Methodology-Heavy Guardrail

### Step 3 — Use those templates as optional priors, not mandatory replacements
Let them guide:
- what sections to include
- how much reference depth to include
- when scripts are encouraged
- how verification should be framed
- what is safe to delete

### Step 4 — Run a small comparison
Compare:
- generic SkillX rewrite
- class-aware SkillX rewrite
for a small subset, preferably one task per class.

---

## 8. Working conclusion

The outer loop should not try to discover one universal skill law.
Its first realistic objective is:

> **to learn task-class-specific template guidance that is more portable than a single task skill, but more concrete than a universal prompt rule.**

That gives the project a much clearer research object.

The design shift is therefore:
- from “rewrite every task skill the same way,”
- toward “learn which template family each task belongs to, then optimize within that family.”

That is likely the right bridge between the current SkillX experiments and the longer-term MARC MetaEvolver vision.
