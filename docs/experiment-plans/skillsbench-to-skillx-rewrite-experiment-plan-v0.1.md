# SkillsBench → SkillX Rewrite Experiment Plan v0.1

- **Project:** `projects/multi-agent-protocol-design`
- **Date:** 2026-03-22
- **Role:** first concrete experiment plan for testing whether SkillX-style rewriting improves skill usefulness relative to current loose skill formats
- **Status:** planning document, not yet executed

---

## 1. Purpose

This document defines the first serious experiment for the SkillX line.

The goal is not to prove the entire SkillX framework at once.
The goal is to answer a narrower, high-value question:

> **If we rewrite existing SkillsBench skills into a lightweight SkillX format, and optionally let an agent derive stronger contract/evaluator structure, do we get measurable gains over the original skill format?**

This is the cleanest first experiment because:
- SkillsBench already directly measures skill usefulness,
- it already shows that skills can help, hurt, or do nothing,
- and it is the benchmark most aligned with our real question: **transferable external skill/context quality**.

---

## 2. Core research question

Can a lightweight, declarative, agent-assisted SkillX layer improve on existing free-form skills without imposing too much authoring burden?

More concretely:

1. Does a **SkillX minimal rewrite** outperform the original skill format?
2. Does **agent-derived contract expansion** help further?
3. Does SkillX reduce **negative transfer** on tasks where original skills are too vague or overbroad?
4. Can we design an evaluation protocol that is resistant to evaluator gaming and benchmark shortcuts?

---

## 3. Main hypotheses

### H1 — Minimal declarative rewriting helps on a nontrivial subset of tasks
Adding lightweight fields like `purpose`, `scope_in`, `scope_out`, `requires`, `preferred_tools`, and `risks` will improve skill usability compared to free-form skill prose alone.

### H2 — Agent-derived contract expansion helps more than metadata alone
Once an agent derives candidate preconditions, evaluator hooks, and failure modes from the minimal SkillX layer, performance and/or reliability should improve further.

### H3 — SkillX’s main gain is not uniform average lift, but better control of conditional utility
The strongest effect may not be a giant mean gain. It may instead be:
- fewer harmful uses,
- fewer out-of-scope activations,
- better handling of prerequisites,
- lower negative transfer.

### H4 — Anti-cheat evaluation changes the measured story
If we add stronger evaluation discipline—fresh-context replay, protected-task probes, independent review lanes—the apparent gains from some variants may shrink. That is a feature, not a bug.

### H5 — Lightweight SkillX can be useful before full formalization
We do not need a heavy DSL or full contract language to get the first measurable effect.

---

## 4. Experimental philosophy

This experiment should isolate **format effect** before claiming **framework effect**.

That means v0.1 should keep several things intentionally simple:
- no new runtime support,
- no custom parser requirement,
- no new tool API,
- no mandatory heavy schema,
- no full auto-evolve loop in the first pilot.

Instead, v0.1 should test whether **authoring-layer improvements alone** already matter.

In other words:

> **SkillX v0.1 should begin as an authoring intervention, not a platform rewrite.**

---

## 5. Experimental object

The experimental object is:

> an existing **SkillsBench skill**, rewritten into a SkillX-style artifact while preserving task intent as much as possible.

The first experiment does **not** try to invent entirely new skills from scratch.
It uses existing benchmark skills as the starting point, because that gives:
- a meaningful baseline,
- tighter comparison,
- and less ambiguity about what changed.

---

## 6. Experimental conditions

The recommended first condition set is:

### C0 — No Skill
- baseline benchmark condition
- the agent has access to the task but no skill package

### C1 — Original Skill
- the task’s original SkillsBench skill as provided
- this is the benchmark-native treatment baseline

### C2 — SkillX Minimal Rewrite
- original skill rewritten into the **SkillX minimal authoring format**
- should preserve the original body guidance as much as possible
- should add lightweight declarative fields only

### C3 — SkillX Minimal Rewrite + Agent-Derived Expansion
- same SkillX minimal rewrite as C2
- plus an agent-derived secondary layer with:
  - candidate preconditions
  - candidate forbidden operations / risks
  - candidate evaluator hooks
  - candidate failure modes
- still no full auto-refine yet

### Optional C4 — SkillX Refined Variant
- only after the earlier conditions are working
- a **bounded multi-round refine loop** starting from `C3`
- runs under a **frozen refine protocol** (the protocol does not mutate during the benchmark run)
- uses tune-split evidence across rounds
- selects a final `C4` candidate after the bounded loop ends
- evaluates only the final `C4` candidate on held-out tasks

This staged design keeps the core question interpretable.

---

## 7. Why these conditions matter

The comparison structure isolates several questions:

- **C1 vs C0** → does the benchmark’s original skill help at all?
- **C2 vs C1** → does lightweight declarative restructuring help?
- **C3 vs C2** → does agent-assisted expansion add value beyond metadata?
- **C4 vs C3** → does bounded **multi-round** auto-refinement add value without simply overfitting?

This is much stronger than only comparing “old skill vs new skill.”

---

## 8. Benchmark scope

### 8.1 Primary benchmark
- **SkillsBench**

### 8.2 Initial task pool
Use the self-contained task pool only for v0.1.
Exclude tasks requiring extra external APIs or fragile external dependencies.

### 8.3 Why SkillsBench is the right first substrate
- directly measures skill usefulness,
- already includes no-skill / curated-skill / self-generated comparisons,
- spans multiple domains,
- has deterministic verifiers,
- aligns tightly with the SkillX problem.

---

## 9. Task selection strategy

Do **not** start by rewriting all tasks.
The first step should be a stratified pilot.

### Recommended pilot slice
Start with **12 tasks** across a diversity of domains and expected skill-response profiles.

Target properties:
- at least 4 domains,
- at least one domain where skills reportedly help a lot,
- at least one domain where gains are small/mixed,
- at least one domain where original skill use appears fragile,
- at least some tasks with plausible negative-transfer risk.

### Why 12 tasks first
- cheap enough to iterate,
- large enough to expose heterogeneity,
- small enough to manually inspect failures,
- enough to support a first paired-delta story.

### Recommended next expansion
If the 12-task pilot is promising:
- expand to **24 tasks** with a tune/eval split,
- and only then consider larger benchmark coverage.

---

## 10. Tune/eval split for refinement safety

The experiment should not let skill rewriting and refinement overfit all selected tasks.

### Pilot A (cheap, no refine)
- 12 tasks
- run C0 / C1 / C2 / C3
- use for first signal only

### Pilot B (controlled refine)
- 24 tasks
- split into:
  - **12 tune tasks**
  - **12 held-out eval tasks**
- use tune tasks for a bounded **multi-round `C4` refine loop** under a frozen refine protocol
- preserve per-round memory / ledger artifacts during tune-side refinement
- report only the final selected `C4` candidate on held-out eval tasks

This is the minimum structure needed to keep the auto-refine story honest.

---

## 11. Rewrite policy

### 11.1 Rules for the SkillX minimal rewrite (C2)
The rewrite should:
- preserve original task intent,
- preserve original guidance content whenever possible,
- add only minimal declarative structure,
- avoid sneaking in major new strategies unless clearly marked.

### 11.2 Rules for agent-derived expansion (C3)
The derived layer may add:
- candidate preconditions,
- candidate postconditions,
- candidate failure modes,
- candidate evaluator hooks,
- candidate scope clarifications,
- candidate tool preferences.

But it should not:
- silently change the fundamental task strategy,
- claim guarantees unsupported by evidence,
- or encode benchmark-specific hacks.

### 11.3 Rewrite invariants
Each rewritten skill should preserve:
- original task category,
- original intended use case,
- approximate authoring spirit,
- compatibility with the benchmark environment.

---

## 12. Authoring burden measurement

Because adoption is a central project concern, the experiment should track not only task performance, but also **rewrite burden**.

Recommended metadata to record per rewritten skill:
- original skill length,
- SkillX rewrite length,
- number of new declarative fields added,
- time to rewrite,
- time for agent-derived expansion,
- number of manual edits after agent derivation.

This matters because a small performance gain may not justify a huge authoring cost.

---

## 13. Evaluation policy

This experiment should explicitly adopt the SkillX evaluator-policy stance.

### 13.1 Primary lane
Use the benchmark’s deterministic verifier as the main outcome lane.
This remains the core pass/fail signal.

### 13.2 Secondary lane
For a smaller manually audited subset, add a fresh-context or independent review lane that inspects:
- task trajectory,
- suspicious shortcuts,
- obvious scope violations,
- evidence of skill misuse.

### 13.3 Protected-task negative-transfer lane
Define a small protected subset where any regression is treated seriously.
This is especially important if a rewritten skill appears to help average score while harming safer or cleaner cases.

### 13.4 Anti-cheat rule
A rewrite variant should not be treated as superior only because it appears to fit the benchmark better while violating broader task intent.

---

## 14. Independence policy

The experiment should preserve some separation between:
- **skill builder** (rewriter / derivation agent),
- **skill executor** (benchmark agent),
- **skill evaluator** (benchmark verifier + optional independent audit lane).

At minimum:
- the agent that rewrites the skill should not be the same context that judges its final quality,
- held-out evaluation tasks should remain unseen during refinement,
- any manual audit should happen after execution, not during prompt construction.

---

## 15. Core metrics

### 15.1 Performance metrics
- overall pass rate
- paired delta vs no-skill
- paired delta vs original skill
- per-domain pass rate
- per-task delta

### 15.2 Harm metrics
- negative transfer count
- negative transfer rate
- protected-task regression count

### 15.3 Reliability metrics
- multi-run stability on a subset
- disagreement between lanes (deterministic vs review lane)
- suspicious-success count (passes that look exploitative or misaligned)

### 15.4 Cost metrics
- token/cost overhead
- runtime overhead
- authoring overhead
- cost per successful gain

### 15.5 Structure metrics
- did the agent appear to discover/use the skill?
- did the agent satisfy key derived preconditions?
- did scope clarifications seem to reduce misuse?

Not all of these must be automated in v0.1, but they should be tracked where feasible.

---

## 16. Decision criteria

A promising early SkillX result does **not** require universal improvement.
A promising early result would be any of the following:

1. **C2 > C1** on average with modest overhead
2. **C3 > C2** on a meaningful subset of tasks
3. negative transfer reduced even if average gain is modest
4. gains are strongest on tasks where original skills were under-specified
5. authoring burden remains low enough to preserve adoption plausibility

A weak result would look like:
- no measurable improvement,
- improvement only from hidden extra strategy injection,
- higher average pass but much worse negative transfer,
- or heavy authoring burden for tiny gain.

---

## 17. Failure modes to watch

### 17.1 Rewrite overfitting
The rewritten skill may accidentally encode benchmark-specific hints or stronger strategies unrelated to the format change.

### 17.2 False declarativity
The skill may gain YAML fields but not actually become more useful.

### 17.3 Evaluation leakage
The rewrite/derivation process may leak task-specific cues into later evaluation.

### 17.4 Overclaiming from tiny pilots
A 12-task result should be treated as directional, not definitive.

### 17.5 Cost blindness
A slightly better skill that takes much longer to author or maintain may still be a poor practical design.

### 17.6 Agent-derived hallucinated contract
The derived layer may invent constraints or claims not grounded in the original skill/task.

---

## 18. Concrete pilot structure

### Pilot A — Rewrite-only pilot
**Goal:** determine whether minimal SkillX structure is worth taking seriously.

#### Inputs
- 12 selected SkillsBench tasks
- original skills for those tasks

#### Conditions
- C0 / C1 / C2 / C3

#### Outputs
- per-task comparison table
- domain-level summary
- negative-transfer table
- rewrite burden summary
- shortlist of tasks where SkillX clearly helps / hurts / is neutral

### Pilot B — Controlled refine pilot
**Goal:** test whether bounded auto-refine adds value beyond declarative rewriting.

#### Inputs
- 24 tasks
- 12 tune / 12 eval split
- C3 as starting point

#### Conditions
- C0 / C1 / C3 / C4

#### Outputs
- held-out evaluation report
- refinement delta report
- overfitting / harm audit
- final recommendation on whether auto-refine is worth pursuing further

---

## 19. Suggested file/artifact layout

Recommended new artifact cluster:

```text
experiments/skillx-skillsbench-001/
  README.md
  task_selection.yaml
  conditions.md
  rewrite_registry/
    <task-id>/
      original_skill_snapshot.md
      skillx_minimal.md
      skillx_derived.md
      rewrite_notes.md
  runs/
    pilot-a/
    pilot-b/
  results/
    pilot-a-summary.json
    pilot-a-summary.md
    pilot-b-summary.json
    pilot-b-summary.md
  audits/
    suspicious-successes.md
    negative-transfer-ledger.md
```

This keeps the experiment reproducible and reviewable.

---

## 20. Execution phases

### Phase 0 — Benchmark setup validation
Reuse the existing SkillsBench integration playbook.
No new design claims yet.

### Phase 1 — Task selection
Select and freeze the 12-task pilot slice.

### Phase 2 — Skill rewriting
Rewrite original skills into C2 format.
Generate C3 expansions.

### Phase 3 — Pilot A execution
Run C0 / C1 / C2 / C3.
Collect raw benchmark outcomes.

### Phase 4 — Audit and synthesis
Inspect failures, suspicious wins, negative-transfer cases, and authoring burden.

### Phase 5 — Decide whether Pilot B is justified
Only proceed if Pilot A yields a meaningful signal.

### Phase 6 — Controlled refinement
Run bounded refine on tune split only.

### Phase 7 — Held-out evaluation
Evaluate refined variants on held-out split.

### Phase 8 — Publish recommendation
Decide whether SkillX should move deeper into:
- transfer/localization policy,
- full contract language,
- or auto-evolve loops.

---

## 21. Relationship to the rest of the SkillX line

This plan is the bridge from **theory/docs** to **first real experiment**.

It directly operationalizes the previous documents:
- `references/skillx-skills-extension-literature-review-and-work-map-2026-03-22.md`
- `drafts/skillx-framework-synthesis-v0.1.md`
- `drafts/skillx-design-principles-v0.1.md`
- `drafts/skillx-minimal-authoring-format-v0.1.md`
- `drafts/skillx-evaluator-policy-v0.1.md`

In practical terms:
- the literature review justified the problem,
- the principles memo constrained the design,
- the minimal format defined the entry layer,
- the evaluator policy defined how not to fool ourselves,
- this experiment plan tells us how to actually test it.

---

## 22. Recommended immediate next moves

If continuing execution immediately, the most natural order is:

1. instantiate the experiment folder
2. freeze Pilot A task selection criteria
3. select the first 12 tasks
4. rewrite the first 3 tasks as a mini dry run
5. inspect authoring burden before scaling to all 12

This helps catch format mistakes cheaply before full pilot execution.

---

## 23. Bottom line

The first SkillX experiment should not try to prove everything.
It should try to prove one thing clearly:

> **Whether lightweight declarative restructuring + agent-assisted expansion can improve skill usefulness on a benchmark built specifically to measure skill usefulness.**

If this experiment works, SkillX has earned the right to become more ambitious.
If it does not, we learn that stronger semantics alone are not enough—or that the framework needs a different layer to matter.
t enough—or that the framework needs a different layer to matter.
amework needs a different layer to matter.
