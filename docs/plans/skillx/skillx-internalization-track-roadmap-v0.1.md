# SkillX Internalization Track Roadmap v0.1

_Date: 2026-04-07_

## Status

This document turns the external memo
`../../research/deep-dives/2026-04-05-skill0-icrl-implications-for-skillx.md`
into a concrete SkillX planning artifact.

It is intentionally framed as a **parallel but linked track**.
It should not disrupt the current SkillX MVP line around:

- prompt bank distinctness
- assignment matrix quality
- render template stability
- meta-schema search and acceptance

Instead, it defines how SkillX can later support a second objective:

> using SkillX artifacts not only as inference-time scaffolds, but also as
> candidates for training-time scaffold withdrawal and possible policy
> internalization.

## Core stance

SkillX should maintain two explicit tracks:

### Track A — Augmentation Track

Current main line.
The goal is to improve task performance by supplying external structured support
at runtime.

Typical objects:

- prompt bank entries
- class-aware meta-prompts
- render templates
- rewrite/refine artifacts
- meta-schema search candidates

Typical questions:

- which external scaffold works best for this task or class?
- how should tasks be assigned to prompt families?
- how should prompt families be updated over time?

### Track B — Internalization Track

New exploratory line.
The goal is to determine which SkillX artifacts are good candidates for
scaffold withdrawal and eventual policy-level absorption.

Typical questions:

- which SkillX artifacts remain useful only while present in context?
- which artifacts help a learner become less dependent on them over time?
- what artifact properties correlate with successful scaffold retirement?

## Why we should open this track now

Recent papers such as SKILL0 and ICRL suggest that external skill artifacts may
serve two roles:

1. **runtime support**
2. **training-time teaching interface**

This matters for SkillX because our current work is already building precisely
those kinds of structured external artifacts.

If SkillX never accounts for internalization-readiness, it may overfit to
artifacts that are useful only as permanent context injections.

## Strategic design principle

Do **not** collapse augmentation and internalization into one score.

The correct move is:

- keep augmentation as the current optimization target
- add internalization-readiness as a second evaluation lens
- let the two tracks share artifact formats and evidence logs where possible

## Non-goals for v0.1

This roadmap does **not** propose that SkillX should immediately become an RL
training framework.

This roadmap also does **not** propose that all skills should be internalized.
Some artifacts will likely remain better as external, inspectable, editable,
and user-steerable support.

## Working hypothesis

The strongest SkillX artifacts will eventually have one of three destinations:

1. **external-only**
   - best used as persistent inference-time support
2. **dual-use**
   - good external support and also promising as an internalization scaffold
3. **internalization-oriented**
   - designed primarily as training scaffolds that should later disappear

A useful long-term SkillX system should be able to tell these categories apart.

## Research questions

## RQ1 — Internalization utility

Can we define a practical score for whether a SkillX artifact is a good
candidate for scaffold withdrawal?

Candidate dimensions:

- usefulness while present
- usefulness under partial removal
- usefulness after repeated exposure
- abstraction compactness
- decomposition clarity
- verifier compatibility

## RQ2 — Retirement dynamics

What withdrawal schedule works best for different task classes?

Examples:

- abrupt removal
- fixed decay
- helpfulness-driven retirement
- component-wise retirement
- class-level budget decay

## RQ3 — Artifact granularity

What is the right unit for internalization-oriented SkillX artifacts?

Possible units:

- full prompt family
- prompt sections / slots
- sub-protocols
- decision heuristics
- verifier-facing guardrails

## RQ4 — Task-class dependence

Do different SkillX classes need different scaffold-retirement logic?

Likely yes.
Examples:

- analytic-pipeline tasks may benefit from structured stage plans longer
- artifact-generation tasks may internalize formatting and decomposition faster
- methodology-guardrail tasks may need persistent external boundary checks

## RQ5 — Acceptance policy across tracks

How should SkillX decide whether a candidate artifact should:

- replace the current augmentation artifact
- branch as an internalization-oriented variant
- remain an analysis-only hypothesis

## Proposed new concept: internalization utility

We should introduce a new evaluation lens called **internalization utility**.

### Definition (v0.1)

Internalization utility measures how suitable a SkillX artifact is as a
scaffold that can later be reduced or removed while preserving or improving task
competence in the learner.

### Why it is distinct from ordinary benchmark utility

An artifact can improve immediate task performance while still being poor for
internalization if it is:

- too verbose
- too entangled
- too brittle
- too tied to exact wording
- too monolithic to ablate cleanly

### Candidate observable proxies

Version 0.1 should treat this as a proxy-based construct.
Possible observable proxies:

1. **ablation resilience**
   - performance under partial artifact removal
2. **compression friendliness**
   - whether the artifact can be shortened without collapse
3. **component isolatability**
   - whether parts can be removed independently
4. **cross-task reuse stability**
   - whether the same artifact helps across a coherent class
5. **post-exposure persistence**
   - whether performance remains improved after scaffold reduction in a repeated
     interaction or staged prompting regime

## Required artifact properties for this track

To support internalization-oriented study later, SkillX artifacts should trend
toward being:

- typed
- class-aware
- decomposable
- versioned
- measurable under ablation
- explicitly connected to verifier outcomes
- auditable at the section / slot / component level

This does not require a full redesign now, but it should influence future
artifact contracts.

## Roadmap structure

## Phase 0 — Protect the current MVP

**Goal:** avoid derailment.

The current SkillX MVP remains centered on:

- prompt-bank distinctness
- assignment quality
- render-template freezing
- meta-schema search and acceptance

### Deliverable

Keep all current MVP evaluation and checkpointing unchanged.
The internalization track should begin as documentation + metric scaffolding,
not a competing execution line.

## Phase 1 — Add the evaluation lens without changing the runner

**Goal:** make internalization-readiness discussable and recordable.

### Deliverables

1. `skillx-internalization-utility-scorecard-v0.1.md`
   - define proxy metrics and review questions
2. `skillx-internalization-artifact-contract-v0.1.md`
   - specify what decomposition metadata an artifact should expose
3. add optional fields to planning/checkpoint docs for:
   - ablation-friendly structure
   - expected retirement behavior
   - external-only vs dual-use vs internalization-oriented designation

### Success condition

A reviewer can look at any new SkillX artifact and say:

- useful for augmentation?
- plausible for internalization?
- if yes, why?
- if no, which property blocks it?

## Phase 2 — Run lightweight scaffold-withdrawal probes

**Goal:** test the idea without full RL infrastructure.

This phase uses lightweight approximations rather than actual policy training.

### Candidate probe designs

1. **Section-drop ablation**
   - remove parts of a meta-prompt and observe robustness
2. **Budget shrink probes**
   - shorten the artifact by 25/50/75% and compare performance
3. **Staged prompt retirement**
   - full scaffold on task A, reduced scaffold on similar task B
4. **Cross-task persistence probes**
   - expose scaffold on earlier tasks, then test reduced-support performance on
     same-class tasks

### Deliverables

1. `skillx-scaffold-withdrawal-probes-v0.1.md`
2. a small pilot task slice using existing SkillsBench representatives
3. result template for recording degradation curves and class differences

### Success condition

We can empirically distinguish at least three cases:

- high utility / low internalization readiness
- high utility / medium internalization readiness
- high utility / high internalization readiness

## Phase 3 — Connect to outer-loop logic

**Goal:** let the outer loop reason about more than immediate score.

### Possible extensions

1. add an `internalization_readiness` field to challenger review
2. allow `accept_branch` when a challenger is weak for augmentation but strong as
   an internalization-oriented scaffold
3. track whether a prompt family is:
   - best for direct use
   - best as a teaching scaffold
   - best kept external for boundary reasons

### Deliverables

1. `skillx-meta-schema-acceptance-scorecard-v0.2.md` or addendum
2. `skillx-outer-loop-update-protocol-v0.2.md` or addendum
3. branch policy for dual-track artifact evolution

### Success condition

The outer loop can preserve artifacts that are not immediate winners on the
current benchmark, but are promising because they occupy a distinct role in the
augmentation/internalization landscape.

## Phase 4 — Optional downstream training integration

**Goal:** only later, if justified, connect SkillX artifacts to actual
internalization pipelines.

This phase is explicitly downstream of the current repository scope.
Potential future integrations could include:

- scaffold-withdrawal training experiments
- continual-learning setups
- post-training loops inspired by ICRL / SKILL0

### Important guardrail

Do not assume this phase is necessary for SkillX to be valuable.
SkillX can already succeed as an external skill-structure and outer-loop system.

## Immediate next actions

These are the next actions that fit the current project state.

### Action 1

Write `skillx-internalization-utility-scorecard-v0.1.md`.

Purpose:

- define the first practical review rubric
- make the concept operational without adding infrastructure

### Action 2

Write `skillx-scaffold-withdrawal-probes-v0.1.md`.

Purpose:

- design lightweight experiments that approximate scaffold retirement
- reuse current representative tasks and prompt-bank artifacts

### Action 3

Add a small addendum to the meta-schema acceptance logic.

Purpose:

- allow a challenger to be preserved as a branch when it is promising for the
  internalization track even if it is not the top augmentation winner

## Suggested classification tags

To support this track, future artifacts may carry one of these tags:

- `external_only`
- `dual_use`
- `internalization_candidate`
- `boundary_external` — useful but should remain external for audit / safety /
  user-control reasons

## Decision rule for now

Until evidence says otherwise:

1. continue optimizing SkillX primarily as an augmentation system
2. record internalization-readiness as a secondary lens
3. preserve candidate artifacts that look structurally promising for scaffold
   withdrawal studies
4. do not let the internalization track block current MVP execution

## Bottom line

SkillX should not pivot away from its current MVP.
But it should start preserving the properties needed for a future where some
SkillX artifacts are evaluated not only by how much they help while present,
but by whether they help the learner eventually stop needing them.
