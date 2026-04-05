# Google 5-Pattern Lens → SkillX Mapping Note

- **Project:** `projects/skillX`
- **Date:** 2026-03-30
- **Role:** mapping note translating the Google / ADK 5-pattern skill-design lens into the current SkillX vocabulary
- **Status:** working analytic bridge note

---

## 1. Why this note exists

After the deep-read of the Google-amplified ADK skill-pattern article, the immediate next question is not:

> should SkillX replace its own ontology with Google’s five labels?

That would be too hasty.

The better question is:

> **Can the Google 5-pattern lens serve as a useful descriptive vocabulary for parts of SkillX without collapsing the current outer-loop design?**

This note answers that question.

The short answer is:

> **yes, but only as a descriptive mid-layer, not as the main outer-loop object.**

---

## 2. Main stance

The current SkillX line should **not** be rewritten as:
- Tool Wrapper system,
- Generator system,
- Reviewer system,
- Inversion system,
- Pipeline system.

That would lose too much.

Why?
Because the Google article and SkillX are operating at different levels.

### Google 5-pattern lens
Primarily answers:

> **what kind of internal content structure does this skill use?**

### SkillX / MetaEvolver line
Primarily answers:

> **what reusable guidance object should the outer loop learn for a class of tasks?**

So the mapping should be:
- Google 5-patterns = **skill-content morphology layer**
- SkillX task classes / topology / risk / verifier = **outer-loop learning layer**

That distinction must remain explicit.

---

## 3. Two-level representation

The cleanest way to combine the two systems is a two-level representation.

### Level A — Outer-loop task-class representation (already in SkillX)
This includes fields like:
- `task_class`
- `skill_topology`
- `primary_pattern`
- `secondary_patterns`
- `risk_profile`
- `verifier_mode`

### Level B — Internal skill-content structure lens (Google 5-patterns)
This asks:
- is this skill mostly a Tool Wrapper?
- is it mostly a Generator?
- does it contain Reviewer logic?
- does it begin with Inversion?
- does it enforce Pipeline steps?

This means the five patterns should be treated as:

> **content-organization primitives that can sit inside a task-class-aware template family.**

That is the right integration point.

---

## 4. Mapping overview

The strongest overall mapping is:

- **Task class** tells us what kind of problem family we are in.
- **Skill topology** tells us how many skills and how they interact.
- **Google pattern labels** tell us what kind of internal structure dominates the skill or template.
- **Risk profile** tells us what can go wrong if the structure is wrong.
- **Verifier mode** tells us how correctness will be judged.

So the five-pattern lens is most useful when treated as one subspace within the larger SkillX profile.

---

## 5. Class-by-class mapping

Below is the strongest first mapping from current SkillX classes into the Google 5-pattern lens.

### 5.1 Class A — Artifact Generator

**Current SkillX meaning**
- tasks where the agent transforms input into a structured output artifact with a clear contract.
- example: `offer-letter-generator`

**Best Google-pattern fit**
- **Primary:** `Generator`
- **Secondary:** lightweight `Reviewer`
- Sometimes weak `Inversion` if missing fields must be gathered first

**Why this fit makes sense**
Artifact-generator tasks are exactly where template shape and contract preservation matter most.
The generator pattern directly encodes:
- target structure,
- fill-in discipline,
- no-invention rules,
- placeholder handling.

A lightweight reviewer layer may also appear as:
- final checklist,
- structure validation,
- missing-section checks.

**What this clarifies for SkillX**
For this class, the outer loop should probably ask less about “better prompt phrasing” and more about:
- artifact contract sharpness,
- missing-input discipline,
- boundary control,
- how much reviewer logic should be bundled vs kept external.

**Important caution**
Do not reduce Artifact Generator to “just Generator.”
Its outer-loop object still includes:
- risk tolerance,
- verifier mode,
- scaffold budget.

The Google label captures only the dominant internal structure.

---

### 5.2 Class B — Engineering Composition Bundle

**Current SkillX meaning**
- tasks where multiple skills contribute overlapping but distinct operational advice for one engineering goal.
- example: `parallel-tfidf-search`

**Best Google-pattern fit**
- **Primary:** mixed `Pipeline` + `Tool Wrapper`
- **Secondary:** `Reviewer`

**Why this fit makes sense**
This class is not merely about one tool or one artifact.
It is about coordinating multiple sources of guidance and keeping precedence clear.

`Tool Wrapper` appears because:
- some skills contribute domain or implementation discipline,
- some encode best practices for a specific subsystem.

`Pipeline` appears because:
- the bundle often needs ordered execution logic,
- correctness-before-performance sequencing matters,
- handoffs and precedence become critical.

`Reviewer` appears because:
- bundle coordination often fails silently without explicit checking.

**What this clarifies for SkillX**
This class may be one of the best examples of why Google’s five labels are not enough by themselves.
A plain “Pipeline” label would miss:
- multi-skill precedence,
- bundle manifest logic,
- role partitioning,
- conflict resolution.

So for SkillX, this class shows the need for:
- task class above pattern,
- topology above local skill internals.

---

### 5.3 Class C — Analytic Pipeline Bundle

**Current SkillX meaning**
- tasks requiring ordered analytic stages, intermediate artifacts, and explicit handoff contracts.
- examples: `trend-anomaly-causal-inference`, `exoplanet-detection-period`, `energy-ac-optimal-power-flow`

**Best Google-pattern fit**
- **Primary:** `Pipeline`
- **Secondary:** `Tool Wrapper`
- Optional `Reviewer`

**Why this fit makes sense**
This is the clearest class-level match to Google’s Pipeline pattern.
The core design pressure is:
- stage order,
- stage-local artifacts,
- failure conditions,
- handoff semantics,
- bundle completion gates.

`Tool Wrapper` enters because analytic stages often need domain-specific conventions or method constraints.
`Reviewer` enters because each stage or the final artifact may require explicit validation.

**What this clarifies for SkillX**
This class is the strongest candidate where Google’s pattern lens and SkillX’s task-class lens reinforce each other.
It suggests:
- `Pipeline` should remain a first-class pattern marker,
- but the outer loop should still optimize the broader object: a reusable **analytic-pipeline template family**.

This class likely remains the best first testbed for outer-loop learning.

---

### 5.4 Class D — Methodology-Heavy Guardrail Task

**Current SkillX meaning**
- tasks where the main difficulty is not generating content but choosing the right methodological posture, checking fit, avoiding overcommitment, and abstaining or branching when needed.
- example: `taxonomy-tree-merge`

**Best Google-pattern fit**
- **Primary:** `Inversion` + `Reviewer`
- **Secondary:** sometimes `Pipeline`

**Why this fit makes sense**
This class is where the Google article becomes especially helpful.

`Inversion` fits because:
- the agent should often clarify assumptions before acting,
- premature task instantiation is dangerous,
- question-first behavior may be better than output-first behavior.

`Reviewer` fits because:
- the system needs explicit checks for fit, anti-patterns, and acceptance boundaries.

A weak `Pipeline` component may appear where methodological decisions must proceed in ordered gates.

**What this clarifies for SkillX**
This class demonstrates that some high-value skills are not primarily “generators” at all.
They are really:
- fit-check systems,
- branch-selection systems,
- abstention-aware systems.

That is extremely important for the project because it reinforces the view that the strongest skill content often lives in:
- question structure,
- evaluation structure,
- decision gates.

---

## 6. What the mapping gives us immediately

### 6.1 Better descriptive vocabulary for current drafts
The five-pattern lens gives us a way to describe current C2 / C2A outputs more precisely.
Instead of saying only:
- “more structured,”
- “more disciplined,”
- “more class-aware,”

we can say:
- this rewrite strengthened Generator structure,
- this variant moved Reviewer logic earlier,
- this draft added Inversion before generation,
- this template shifted toward Pipeline discipline.

That makes cross-task comparison more interpretable.

### 6.2 A useful middle layer for REP extraction
REP V2 may benefit from a lightweight field that says:
- what internal pattern(s) dominated the run,
- or what pattern deficiency caused failure.

For example:
- failure due to missing Reviewer logic;
- failure due to absent Inversion under ambiguity;
- failure due to overgrown Pipeline monolith;
- failure due to weak Tool Wrapper discipline.

This is interesting because it could make extracted experience more reusable than pure task-local wording.

### 6.3 A way to describe failure in structural terms
A large class of failures may be more meaningfully described as:
- missing pattern,
- wrong dominant pattern,
- incorrect pattern mix,
- over-applied pattern.

This is more useful than generic comments like “skill weak” or “guidance unclear.”

---

## 7. What the mapping does *not* give us

This is just as important.

### 7.1 It does not replace task class
Task class still captures broader process shape than the five pattern labels.
For example, both an analytic pipeline bundle and an engineering composition bundle may contain `Pipeline`, but they are not the same outer-loop object.

### 7.2 It does not replace topology
Multi-skill flat bundle vs staged bundle is still a distinct axis.
Google’s five labels do not adequately represent bundle interaction topology.

### 7.3 It does not replace risk profile
Some tasks are fragile not because they lack a named pattern, but because they are:
- over-guidance-sensitive,
- composition-confusion-sensitive,
- negative-transfer-sensitive.

Those are SkillX-critical dimensions that must remain visible.

### 7.4 It does not by itself solve evolution
The five-pattern lens helps name structure.
It does not tell us:
- when to switch patterns,
- how to revise a pattern mix,
- how to aggregate experience across tasks,
- or how to update a class-aware template family.

That remains our problem.

---

## 8. Proposed integration into SkillX artifacts

A low-risk way to integrate this lens is **annotation, not replacement**.

### Option A — keep current profile, tighten interpretation
Continue using the current profile:

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
```

This is already close to the right shape.
The change would mainly be interpretive: use the Google 5-pattern vocabulary more consciously when assigning `primary_pattern` and `secondary_patterns`.

### Option B — add pattern-role annotation to experiments
For each tested skill variant, add a compact note such as:
- dominant pattern role;
- added pattern role;
- missing pattern role.

Example:

```yaml
pattern_observation:
  dominant: pipeline
  strengthened:
    - reviewer
  still_missing:
    - inversion
```

This could be very helpful in cross-task analysis.

### Option C — extend REP V2 schema later, but only after evidence
Do **not** immediately redesign REP around these five labels.
But if repeated extraction runs show they are useful explanatory handles, then add them as optional abstraction tags.

---

## 9. Best current hypothesis

The strongest current hypothesis is:

> **Google’s 5-pattern system is most useful as an internal structure lens for understanding what kind of content a class-aware SkillX template should contain, but it is too low-level to become the outer-loop learning object on its own.**

That means the right relation is:

- **outer loop learns task-class template families**;
- **template families are internally composed from pattern-like structural primitives**.

This is a clean synthesis.

---

## 10. Implications for the next comparison memo

This mapping now sets up the next step naturally.
A three-way comparison can distinguish:

- **Anthropic** → refine infrastructure
- **Google** → skill-structure taxonomy
- **SkillX** → experience-informed class-aware outer-loop evolution

That comparison will be much sharper now because the Google side has been grounded into the SkillX vocabulary instead of left as a floating inspiration source.

---

## 11. Bottom line

The correct use of Google’s 5-pattern article is not to replace SkillX’s ontology.
It is to give SkillX a better language for describing the **internal morphology** of skills and templates.

In practical terms:

> **task class tells us what kind of outer-loop object we are optimizing; Google’s five patterns help tell us what internal structural ingredients that object is made of.**

That is the right bridge between the two systems.
