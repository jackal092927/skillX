# SkillX Internalization Utility Scorecard v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-07
- **Role:** defines how to judge whether a SkillX artifact is promising as a scaffold that can later be reduced or removed
- **Status:** working exploratory scorecard

---

## 1. Purpose

This document makes the idea of **internalization utility** operational.

It answers a question introduced in:

- `skillx-internalization-track-roadmap-v0.1.md`
- `../../research/deep-dives/2026-04-05-skill0-icrl-implications-for-skillx.md`

namely:

> **When a prompt family, meta-prompt, render template, or structured scaffold helps now, how do we judge whether it is also a good candidate for scaffold withdrawal later?**

This scorecard is intentionally separate from ordinary augmentation evaluation.
Its purpose is not to replace current benchmark scoring.
Its purpose is to add a second lens.

---

## 2. Core definition

### Internalization utility

Internalization utility measures how suitable a SkillX artifact is as a
**teaching scaffold** whose support can later be reduced or removed while task
competence remains stable or degrades gracefully.

This is different from immediate benchmark utility.

A scaffold may score well on live tasks yet score poorly on internalization
utility if it is:

- too verbose
- too entangled
- too brittle to wording changes
- too monolithic to ablate cleanly
- too dependent on persistent runtime injection

---

## 3. What this scorecard applies to

This scorecard can be applied to any SkillX artifact that functions as runtime
support, including:

- category-level prompt bank entries
- rendered task-facing meta-prompts
- rewrite/refine scaffolds
- task-class-specific template families
- meta-schema variants
- guardrail-heavy protocol fragments

It should **not** be used as the sole decision rule for artifacts whose purpose
is primarily safety, auditability, or user control.
Those may need to remain external by design.

---

## 4. Main judgment question

For any artifact under review, ask:

> If a learner benefits from this artifact now, is the artifact helping the
> learner become less dependent on it, or is it only serving as permanent
> runtime crutch?

The scorecard exists to make that distinction explicit.

---

## 5. Required evidence bundle

Before assigning a serious internalization-utility judgment, collect at least:

```yaml
artifact_id: string
artifact_type: prompt_bank_entry | render_template | meta_schema | protocol | other
artifact_version: string
task_class: string | null
intended_role: augmentation_only | dual_use | internalization_candidate | unknown
support_size: int
full_support_results:
  - task_name: string
    score: float
partial_support_results:
  - ablation_name: string
    task_name: string
    score: float
compressed_support_results:
  - budget_level: full | 75pct | 50pct | 25pct
    task_name: string
    score: float
cross_task_results:
  - task_name: string
    relatedness_bucket: same_class | adjacent_class | out_of_class
    score: float
artifact_structure_summary:
  sections:
    - name: string
      role: string
      removable: true | false
  known_risky_sections:
    - string
notes:
  - string
```

If this bundle is unavailable, the artifact can still receive a provisional
judgment, but it should be marked low-confidence.

---

## 6. Scorecard dimensions

Use six primary dimensions.
Each should be judged qualitatively first.
Numeric overlays are optional.

---

## 6.1 Dimension A — Scaffold dependence profile

Question:

> How sharply does performance collapse when the scaffold is reduced?

Signals:

- full-support vs partial-support gap
- whether degradation is graceful or cliff-like
- whether the artifact seems to carry the task alone

Judgment bands:

- **A+** graceful degradation; strong signs the scaffold is teaching rather than merely carrying
- **A** moderate degradation but still robust
- **B** mixed / uncertain
- **C** heavy dependence on full scaffold
- **D** cliff-like collapse under even small reduction

Interpretation:
- High scores suggest the scaffold may be internalization-friendly.
- Low scores suggest runtime dependence.

---

## 6.2 Dimension B — Component isolatability

Question:

> Can the artifact be decomposed into parts whose contributions can be studied independently?

Signals:

- explicit sections / slots / sub-policies
- ability to remove one part without destroying the whole artifact format
- semantic clarity of each component's role

Judgment bands:

- **A+** highly modular and ablation-friendly
- **A** mostly decomposable
- **B** partially decomposable
- **C** weak structure; hard to isolate components
- **D** monolithic / entangled

Why it matters:
- If an artifact cannot be decomposed, helpfulness-driven retirement becomes
  hard to study.

---

## 6.3 Dimension C — Compression friendliness

Question:

> Can the artifact be shortened substantially without losing its behavioral core?

Signals:

- 75/50/25% budget shrink behavior
- whether shorter versions preserve the same policy bias
- whether the artifact contains redundant wording vs essential structure

Judgment bands:

- **A+** compact core survives strong compression
- **A** moderate compression works
- **B** somewhat compressible
- **C** performance depends on long verbose form
- **D** heavy collapse under compression

Why it matters:
- Internalizable scaffolds should ideally express a compact, transferable bias.

---

## 6.4 Dimension D — Cross-task reuse stability

Question:

> Does the artifact help across a coherent task region rather than only on a single narrow case?

Signals:

- same-class task consistency
- adjacent-class behavior
- variance across representative tasks

Judgment bands:

- **A+** stable benefit across coherent class slice
- **A** strong same-class reuse
- **B** mixed but plausible
- **C** narrow / unstable
- **D** one-off or overfit-like

Why it matters:
- A scaffold that only works for one exact phrasing is a weak internalization candidate.

---

## 6.5 Dimension E — Verifier-aligned abstraction quality

Question:

> Does the artifact encode a reusable behavioral abstraction that aligns with task contracts and verifier logic?

Signals:

- clear relationship to task success criteria
- explicit stage / contract / boundary logic
- whether the artifact teaches a stable way of acting, not just a verbose answer style

Judgment bands:

- **A+** strong contract-aligned behavioral abstraction
- **A** clearly structured and verifier-compatible
- **B** adequate but somewhat fuzzy
- **C** shallow stylistic assistance dominates
- **D** mostly phrasing / formatting sugar with weak behavioral abstraction

Why it matters:
- Internalization should target behaviorally meaningful structure, not accidental wording hacks.

---

## 6.6 Dimension F — External-boundary necessity

Question:

> Even if the artifact is useful, should it remain external for safety, audit, or user-control reasons?

Signals:

- safety guardrails that must stay inspectable
- user-specific constraints
- policy or compliance instructions
- artifacts whose value is primarily explicit external control

Judgment bands:

- **A+** no strong reason it must remain external
- **A** probably can be dual-use
- **B** mixed
- **C** likely better kept external
- **D** should remain external by design

Important note:
- A low score here does **not** mean the artifact is bad.
- It means the artifact may belong in `boundary_external` rather than
  `internalization_candidate`.

---

## 7. Classification rule

After scoring A–F, classify the artifact into one of four practical tags.

### 7.1 `external_only`

Use when:
- immediate utility exists,
- but scaffold dependence is high,
- or decomposition/compression are weak,
- or there is no clear sign of transfer beyond runtime support.

### 7.2 `dual_use`

Use when:
- immediate utility is solid,
- dependence is moderate rather than cliff-like,
- the artifact is reasonably decomposable,
- and some evidence suggests it could survive scaffold withdrawal studies.

### 7.3 `internalization_candidate`

Use when:
- graceful degradation under ablation is visible,
- the artifact is compactable and decomposable,
- same-class reuse is stable,
- and there is no strong need for permanent externalization.

### 7.4 `boundary_external`

Use when:
- the artifact may be effective,
- but its main value is explicit external oversight, safety, auditability, or
  user-steerability.

---

## 8. Practical decision rule

### Strong internalization candidate

Treat an artifact as a strong internalization candidate only if all are true:

1. Scaffold dependence profile >= **A**
2. Component isolatability >= **B**
3. Compression friendliness >= **B**
4. Cross-task reuse stability >= **A**
5. Verifier-aligned abstraction quality >= **A**
6. External-boundary necessity >= **B**

### Dual-use candidate

Treat as dual-use if:
- immediate utility is strong,
- internalization signals are promising but incomplete,
- and there is no strong argument that the artifact must remain external.

### Keep external

Prefer external-only or boundary-external if:
- performance collapses immediately under scaffold reduction,
- the artifact is too monolithic,
- or its main value is explicit boundary control.

---

## 9. Recommended review prompts

When scoring an artifact, answer these questions explicitly:

1. What behavior is this scaffold actually teaching?
2. If one major section is removed, what degrades first?
3. Does the scaffold encode compact policy bias or just lots of local wording?
4. Does it generalize across same-class tasks?
5. Which parts look internalizable and which parts look boundary-external?
6. If we had to shrink this scaffold by half, what would we keep?

---

## 10. Acceptance artifact

Every serious review should emit:

```yaml
artifact_id: string
artifact_version: string
task_class: string | null
review_confidence: high | medium | low
scores:
  scaffold_dependence_profile: A+|A|B|C|D
  component_isolatability: A+|A|B|C|D
  compression_friendliness: A+|A|B|C|D
  cross_task_reuse_stability: A+|A|B|C|D
  verifier_aligned_abstraction_quality: A+|A|B|C|D
  external_boundary_necessity: A+|A|B|C|D
classification: external_only | dual_use | internalization_candidate | boundary_external
reasons:
  - string
suggested_next_probe:
  - string
notes:
  - string
```

---

## 11. How this should interact with the current MVP

This scorecard should be treated as:

- a **secondary lens** for artifact review
- a way to preserve promising branches
- a way to notice artifacts that are structurally valuable beyond immediate
  benchmark wins

It should **not** override the current augmentation-first evaluation stack.

---

## 12. Recommended first use

Use this scorecard first on a small set of representative current artifacts:

- one prompt-bank entry from `analytic-pipeline`
- one prompt-bank entry from `artifact-generation`
- one guardrail-heavier or methodology-flavored artifact
- one meta-schema challenger if available

This is enough to test whether the lens produces meaningful distinctions.

---

## 13. Final practical rule

If there is uncertainty, interpret the dimensions in this order:

1. Does the scaffold create cliff-like dependence or graceful dependence?
2. Is there a compact, decomposable behavioral core?
3. Does that core generalize across a coherent class?
4. Does the artifact teach verifier-aligned behavior?
5. Is there any reason it should remain external on purpose?

That order gives the right bias:
- first distinguish crutch vs teaching scaffold,
- then ask whether the taught structure is reusable,
- and finally respect cases where explicit externalization is the correct design.
