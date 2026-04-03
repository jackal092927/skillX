# SkillX 5-Patterns-Aware Variant v0.1

- **Project:** `projects/multi-agent-protocol-design`
- **Date:** 2026-03-23
- **Role:** parallel variant proposal for adding lightweight pattern-awareness to SkillX
- **Status:** exploratory side-version, not baseline

---

## 1. Why this document exists

The current SkillX baseline already has a coherent main line:
- lightweight authoring,
- progressive escalation,
- evaluator backing,
- multi-round refine,
- and eventual first-class skill-object direction.

Separately, the Google Cloud Tech reference suggested a useful additional lens:
- many skills appear to fall into recurring **content patterns**:
  - Tool Wrapper
  - Generator
  - Reviewer
  - Inversion
  - Pipeline

Xin explicitly does **not** want this insight to silently overwrite the existing SkillX baseline.

So this document exists as a **parallel variant** only.

Its purpose is to answer a narrower question:

> **Would SkillX become more useful if it had an optional, lightweight notion of pattern family and pattern composition?**

This is an experiment design question, not a settled baseline decision.

---

## 2. Status relative to the baseline

### 2.1 What this document does NOT do
This document does **not**:
- replace `skillx-minimal-authoring-format-v0.1.md`
- replace `skillx-design-principles-v0.1.md`
- replace `skillx-evaluator-policy-v0.1.md`
- or redefine the canonical `C0/C1/C2/C3/C4` experiment line

### 2.2 What it does do
It proposes a **side-by-side variant** that can later be tested against the baseline.

The comparison question is:

> **Does adding a lightweight pattern overlay improve authoring, evaluation, refinement, or transfer enough to justify the extra complexity?**

If the answer is no, this variant should be discarded without harming the main line.

---

## 3. Core design stance

This variant is built around one rule:

> **Pattern-awareness should be an overlay, not a new required core schema.**

That means:
- pattern labels are optional,
- pattern composition is lightweight,
- uncertain cases may remain unlabeled,
- and the baseline SkillX object stays valid without them.

This avoids violating the existing design commitment to low-friction authoring.

---

## 4. What problem this variant is trying to solve

The baseline SkillX line already improves:
- declarative structure,
- scope control,
- evaluator linkage,
- and refine/evolution readiness.

But it still mostly treats skills as one broad family.

The pattern memo suggested that this may be too coarse.

A **Generator**, **Reviewer**, and **Inversion** skill may need different treatment in:
- authoring guidance,
- evaluation criteria,
- refine strategies,
- and transfer expectations.

So the problem this variant is testing is:

> **Would SkillX become more accurate and useful if it recognized the behavioral pattern of a skill, not just its domain and prose content?**

---

## 5. The five pattern families

This variant uses the same practical set derived from the Google Cloud Tech reference.

### 5.1 Tool Wrapper
A skill that gives the agent specialized knowledge about a library, framework, API, or domain convention.

### 5.2 Generator
A skill that produces structured output from a template, scaffold, or reusable output pattern.

### 5.3 Reviewer
A skill that evaluates existing input against a checklist, rubric, or criteria set.

### 5.4 Inversion
A skill that asks structured questions first and blocks action until enough context is collected.

### 5.5 Pipeline
A skill that enforces an ordered multi-step workflow with explicit stages/checkpoints.

---

## 6. Design principle of this variant

### 6.1 Pattern ≠ domain
Pattern labels are about **behavioral structure**, not topic.

Examples:
- a FastAPI skill may be a **Tool Wrapper**
- a project planner may be **Inversion**
- a doc-generation workflow may be **Generator + Pipeline**

### 6.2 Patterns may compose
This variant explicitly supports composition.

Examples:
- `Generator + Inversion`
- `Pipeline + Reviewer`
- `Tool Wrapper + Reviewer`

### 6.3 Composition should remain bounded
To keep the variant lightweight:
- every skill should have at most **one primary pattern**
- and usually **0–2 secondary patterns**

Do not let the label system become a giant ontology.

---

## 7. Minimal overlay design

This variant proposes a **pattern overlay block**, rather than changing the baseline required fields.

### 7.1 Proposed inline overlay

```markdown
---
skillx:
  name: report-generator
  purpose: Generate structured technical reports from a reusable template.
  scope_in:
    - user asks for a report, summary, or structured memo

skillx_pattern_overlay:
  primary: generator
  secondary:
    - inversion
  rationale: The skill mainly fills a template, but may first ask for missing inputs before generation.
  confidence: medium
---
```

### 7.2 Why an overlay block instead of changing `skillx:` directly
Because this is a variant, not the baseline.

An overlay block makes the experimental nature obvious:
- it can be added or removed without damaging the baseline design,
- it is easy to compare with a no-pattern version,
- and it avoids silently redefining the canonical minimal format.

---

## 8. Field proposal for the overlay

### 8.1 `primary`
Required if the overlay block exists.

Allowed values:
- `tool-wrapper`
- `generator`
- `reviewer`
- `inversion`
- `pipeline`

### 8.2 `secondary`
Optional list of 0–2 pattern labels.

Purpose:
- capture the most important composition relation without creating a huge dependency graph.

### 8.3 `rationale`
Short natural-language explanation of why this pattern labeling was chosen.

Purpose:
- improve interpretability,
- support later audits,
- reduce meaningless label dumping.

### 8.4 `confidence`
Optional light confidence field:
- `low`
- `medium`
- `high`

Purpose:
- acknowledge that some skill pattern assignments are ambiguous.

### 8.5 What is intentionally NOT included
This variant does **not** add:
- full decision-tree traces,
- elaborate composition graphs,
- mandatory pattern taxonomy proofs,
- or formal type hierarchies.

The goal is a light overlay only.

---

## 9. How labels should be assigned

### 9.1 Assignment rule
Use the **dominant behavioral shape** of the skill as `primary`.

### 9.2 Composition rule
Use `secondary` only when an additional pattern clearly affects:
- how the skill executes,
- how it should be evaluated,
- or how it should be refined.

### 9.3 Abstention rule
If classification is unclear, it is acceptable to:
- omit the pattern overlay entirely,
- or mark confidence as `low`.

The overlay must remain optional and non-coercive.

---

## 10. Why this might help

This variant is worth testing because pattern-awareness could improve several downstream tasks.

### 10.1 Better evaluation hints
Different patterns naturally suggest different failure modes.

#### Tool Wrapper
Look for:
- correct rule retrieval
- fidelity to conventions
- misuse of references

#### Generator
Look for:
- template completeness
- variable coverage
- structural fidelity

#### Reviewer
Look for:
- rubric coverage
- severity calibration
- explanatory quality

#### Inversion
Look for:
- question quality
- requirement coverage
- anti-premature-execution behavior

#### Pipeline
Look for:
- step adherence
- gate integrity
- checkpoint compliance

This could make evaluator design more specific without requiring a heavy universal schema.

### 10.2 Better refine hints
A multi-round refiner could use pattern type as a diagnosis prior.

Examples:
- for a **Generator**, refine might focus on template completeness and missing variables
- for a **Reviewer**, refine might focus on checklist completeness and severity logic
- for an **Inversion** skill, refine might focus on question order and missing-requirement capture

### 10.3 Better transfer expectations
Pattern family may affect portability.

For example:
- Tool Wrappers may transfer more via references and conventions
- Pipelines may be more fragile across environments
- Reviewers may depend more on rubric portability than on tool portability

---

## 11. Why this might NOT be worth it

This variant also has real risks.

### 11.1 Added authoring burden
Even one more metadata block can create friction.

### 11.2 Pattern labels may be too subjective
Different annotators may disagree on the same skill.

### 11.3 Pattern labels may not help enough in practice
It is possible that the baseline fields already capture enough signal.
If so, this overlay would be complexity without meaningful benefit.

### 11.4 False clarity risk
The label may create the illusion of understanding without actually improving execution or evaluation.

This is why this design should remain a side variant until tested.

---

## 12. How to test this variant

This variant should be evaluated as an experiment, not adopted by taste alone.

### 12.1 Authoring-cost test
Question:
- does the overlay impose noticeable extra burden on authors?

### 12.2 Agreement test
Question:
- do different readers assign similar pattern labels to the same skill?

### 12.3 Evaluator-value test
Question:
- does pattern-aware evaluation actually produce clearer or more accurate diagnoses?

### 12.4 Refine-value test
Question:
- does pattern-aware refine outperform baseline refine on at least some tasks or task families?

### 12.5 Transfer-value test
Question:
- do pattern labels help predict where a skill will or won’t transfer?

If these tests are weak, the variant should not graduate into the baseline.

---

## 13. Interaction with the current SkillX baseline

### 13.1 With minimal authoring format
This variant leaves the minimal format intact.
It adds an optional overlay only.

### 13.2 With evaluator policy
This variant does not replace the evaluator policy.
It only proposes that pattern family may become an additional evaluator hint.

### 13.3 With multi-round refine
This variant does not change the `C4` protocol.
It only suggests that pattern family might later become an optional input to the refine bundle.

### 13.4 With MARC
This variant is also relevant to future community indexing:
- pattern labels could become a useful discovery/filtering mechanism,
- but only if they prove reliable and low-cost enough.

---

## 14. Recommended next-step posture

This variant should be treated as:
- **documented**,
- **preserved**,
- but **not yet promoted**.

Recommended posture:
1. keep baseline SkillX unchanged,
2. keep this as a side version,
3. later test it on a small subset of skills,
4. compare whether pattern-aware evaluation/refine actually helps.

---

## 15. Bottom line

This document proposes a cautious experiment:

> **SkillX may benefit from a lightweight pattern overlay, but that claim is not yet strong enough to fold into the main baseline.**

So the right move is not to merge it now.
The right move is to:
- preserve it as a parallel variant,
- test it later,
- and let evidence decide whether it deserves promotion.
