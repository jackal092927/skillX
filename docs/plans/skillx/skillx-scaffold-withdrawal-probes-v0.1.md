# SkillX Scaffold Withdrawal Probes v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-07
- **Role:** lightweight experiment design for approximating scaffold withdrawal without building a full RL training pipeline
- **Status:** exploratory protocol

---

## 1. Purpose

This document defines a first set of lightweight probes for the new SkillX
internalization track.

It operationalizes the question:

> **Can a SkillX artifact behave like a teaching scaffold rather than only a runtime crutch?**

These probes are intentionally cheaper and simpler than true post-training or
RL-based scaffold-withdrawal experiments.

Their purpose is to provide early empirical signal before we decide whether the
internalization track deserves heavier infrastructure.

---

## 2. Design constraints

The probes must:

1. reuse current SkillX artifacts where possible
2. fit the existing SkillsBench-oriented evaluation workflow
3. avoid blocking the current augmentation MVP
4. produce artifact-level evidence that can feed the internalization utility
   scorecard
5. distinguish at least three broad cases:
   - runtime crutch
   - mixed / ambiguous scaffold
   - plausible teaching scaffold

---

## 3. What counts as "withdrawal" here

Since we are not doing actual policy training in v0.1, withdrawal is approximated by reducing available scaffold support across controlled conditions.

In this document, withdrawal means one of:

- removing sections from a scaffold
- shrinking the scaffold budget
- reducing scaffold support across staged task sequences
- probing whether prior scaffold exposure helps performance under weaker later support

This is not true internalization.
It is an early proxy protocol.

---

## 4. Probe family overview

Use four probe families.

### Probe A — Section-drop ablation

Goal:
- identify whether the artifact has a robust behavioral core or depends on the full surface form

### Probe B — Budget-shrink probe

Goal:
- test whether the artifact's value survives compression

### Probe C — Staged prompt retirement probe

Goal:
- test whether strong scaffold exposure on earlier same-class tasks helps under reduced support later

### Probe D — Cross-task persistence probe

Goal:
- test whether scaffold exposure appears to create reusable class-level bias rather than only one-task reliance

---

## 5. Recommended initial task slice

Use a small representative slice from the current SkillX benchmark universe.
Prefer tasks already central to the planning line.

Suggested starter set:

### Class 1 — Artifact generation
- `offer-letter-generator`

### Class 2 — Analytic pipeline
- `trend-anomaly-causal-inference`
- `parallel-tfidf-search`

### Class 3 — Engineering composition
- `taxonomy-tree-merge`

Optional expansion set:
- `exoplanet-detection-period`
- `energy-ac-optimal-power-flow`

Reason:
- these tasks are already part of the SkillX representative reasoning set
- they cover multiple structural families
- they provide a good first stress test for class-sensitive conclusions

---

## 6. Artifact selection rule

For each selected task class, choose one artifact to probe.
Initial candidates may include:

- the current category-level prompt-bank entry
- a rendered runtime prompt family instance
- one alternative or challenger if available

Do not begin with too many artifacts.
For the first pass, prefer:

- 1 artifact per class
- 3 classes
- 1-2 tasks per class

This keeps the probe set interpretable.

---

## 7. Probe A — Section-drop ablation

## Question

If we remove one major section of the scaffold, does behavior degrade gracefully or collapse?

## Setup

For a chosen artifact, define explicit sections such as:

- task framing
- workflow decomposition
- verifier / success contract
- risk / anti-goal section
- tool-use strategy section

Create these variants:

1. **full scaffold**
2. **minus decomposition section**
3. **minus verifier / contract section**
4. **minus risk / anti-goal section**
5. **minus tool-strategy section** (if present)

## Signals to record

- task score change per variant
- failure mode change
- whether the model falls back to generic behavior
- whether specific missing sections produce predictable deficits

## What it tells us

- clean, interpretable degradation suggests decomposable teaching structure
- chaotic collapse suggests entangled runtime dependence

---

## 8. Probe B — Budget-shrink probe

## Question

Does the scaffold preserve its behavioral core when compressed?

## Setup

Create budget-controlled versions:

1. **100%** original scaffold
2. **75%** budget version
3. **50%** budget version
4. **25%** budget version

Compression should preserve intent, not just truncate randomly.
Use a manual or rule-guided shortening process.

## Signals to record

- score by budget level
- failure onset point
- which concepts survive across compression levels
- whether shorter versions preserve class identity

## What it tells us

- high compression tolerance suggests compact internalizable bias
- collapse under modest compression suggests overdependence on long-form phrasing

---

## 9. Probe C — Staged prompt retirement

## Question

If a model first works with strong support on one task, can it perform a later related task with reduced support?

## Setup

For a same-class pair of tasks:

- Stage 1: run Task A with full scaffold
- Stage 2: run Task B with reduced scaffold

Possible reduced scaffold conditions:
- 50% budget
- key sections removed
- only class header + compact contract retained

This is not policy training.
But it probes whether the scaffold is acting more like temporary instruction than permanent one-shot crutch.

## Signals to record

- Stage 2 performance vs direct reduced-support baseline
- whether prior full-support exposure stabilizes later reduced-support behavior
- whether effects are class-specific

## What it tells us

- if prior exposure helps later reduced-support performance, the artifact may be transmitting reusable policy bias

---

## 10. Probe D — Cross-task persistence probe

## Question

Does scaffold exposure appear to create reusable support across multiple same-class tasks?

## Setup

For a class with 3 tasks:

- Task 1: full scaffold
- Task 2: partial scaffold
- Task 3: minimal scaffold

Compare against a control ordering such as:
- Task 1: minimal scaffold
- Task 2: partial scaffold
- Task 3: minimal scaffold

## Signals to record

- relative stability across stages
- whether later tasks degrade less than expected
- whether the scaffold seems to induce class-consistent action structure

## What it tells us

- whether the artifact supports persistent task-class bias rather than isolated one-shot prompting

---

## 11. Minimal result schema

Each probe run should emit something like:

```yaml
probe_id: string
artifact_id: string
artifact_version: string
task_class: string
probe_type: section_drop | budget_shrink | staged_retirement | cross_task_persistence
conditions:
  - name: string
    task_name: string
    scaffold_level: full | partial | minimal
    variant: string
    score: float
    outcome: success | partial | fail
    main_failure_mode: string
summary:
  degradation_profile: graceful | mixed | cliff_like
  likely_internalization_signal: high | medium | low
notes:
  - string
```

---

## 12. Probe interpretation guide

## Case A — Runtime crutch

Typical pattern:
- strong full-support score
- severe drop under section removal
- severe drop under moderate compression
- little or no benefit from staged exposure

Interpretation:
- strong augmentation artifact
- weak internalization candidate
- probably `external_only`

## Case B — Mixed scaffold

Typical pattern:
- some sections appear essential
- others can be removed with small loss
- moderate compression works
- staged exposure helps in some same-class cases

Interpretation:
- plausible `dual_use`
- needs further decomposition work

## Case C — Plausible teaching scaffold

Typical pattern:
- graceful degradation under removal
- robust compressed core
- same-class persistence signal
- predictable, interpretable failure modes

Interpretation:
- strong `internalization_candidate`
- worth preserving even if not always the top immediate augmentation winner

---

## 13. Experimental cautions

### 13.1 Not true internalization

These probes do not prove weight-level skill internalization.
They only estimate whether an artifact has the structure one would want for later scaffold-withdrawal study.

### 13.2 Ordering effects

Staged probes can be sensitive to order.
Record ordering explicitly and avoid overclaiming from tiny samples.

### 13.3 Task contamination risk

Use related but non-identical tasks for staged exposure.
Otherwise the probe may collapse into repetition effects rather than reusable class bias.

### 13.4 Model variance

Use repeated runs when feasible.
A single run should be treated as weak evidence.

---

## 14. Recommended first pilot

### Scope

Run one small internalization pilot with:

- 3 classes
- 1 artifact per class
- 2 tasks per class
- Probe A + Probe B first
- Probe C only on the most promising class

### Why this shape

This gives enough diversity to see whether the lens is meaningful, without creating a second large benchmark program.

### Suggested class order

1. analytic-pipeline
2. artifact-generation
3. engineering-composition

Reason:
- likely different degradation profiles
- good contrast for the first pilot

---

## 15. Relationship to the scorecard

This probe protocol is the evidence source for:

- `skillx-internalization-utility-scorecard-v0.1.md`

Use the scorecard to convert probe outcomes into artifact classifications:

- `external_only`
- `dual_use`
- `internalization_candidate`
- `boundary_external`

---

## 16. Relationship to current augmentation work

This protocol should be used in a way that does **not** block the current SkillX
MVP.

Recommended priority rule:

1. keep the main augmentation benchmarks moving
2. run withdrawal probes only on a small handpicked artifact slice
3. use probe results mainly to preserve promising branches and shape future
   artifact contracts

---

## 17. Immediate next implementation steps

1. choose the first 3 artifacts to probe
2. define explicit section boundaries for each
3. write compressed variants at 75/50/25%
4. create a minimal result table template
5. run Probe A and Probe B first
6. score artifacts with the internalization utility scorecard

---

## 18. Final practical rule

If a scaffold only works while fully present, it is still useful — but it is not yet evidence of internalization readiness.

The purpose of these probes is to find artifacts whose value survives controlled withdrawal, because those are the artifacts most worth preserving for the SkillX internalization track.
