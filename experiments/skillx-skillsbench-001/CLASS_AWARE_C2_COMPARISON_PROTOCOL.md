# Class-Aware C2 Comparison Protocol v0.1

- **Project:** `projects/multi-agent-protocol-design`
- **Experiment:** `experiments/skillx-skillsbench-001`
- **Date:** 2026-03-25
- **Role:** protocol for the first direct comparison between generic `C2` and class-aware `C2`
- **Status:** execution-ready comparison addendum

---

## 1. Why this document exists

The current SkillX baseline already defines:
- `C0` — no skill
- `C1` — original skill
- `C2` — generic SkillX minimal rewrite
- `C3` — generic SkillX derived expansion
- optional `C4` — bounded multi-round refine

After the MARC two-loop reframing, we added a new outer-loop object:
- **task-class-aware template families**

This creates a new narrow experiment:

> **Does a class-aware C2 starting point improve on generic C2 before any C3 or C4 logic is added?**

This document freezes that comparison.

---

## 2. Comparison object

This protocol introduces one new comparison condition:

### `C2A` — Class-Aware SkillX Minimal Rewrite
A C2-level rewrite that:
- remains lightweight,
- does not add C3-style derived layers,
- but is shaped by a task-class template family prior.

Examples of task-class priors:
- artifact-generator
- engineering-composition-bundle
- analytic-pipeline-bundle
- methodology-heavy-guardrail-task

`C2A` is best understood as:

> a **template-instantiated R0 starting point** for the inner-loop skill evolver.

---

## 3. Comparison conditions

### Recommended direct comparison matrix
For the first class-aware comparison pilot, use:
- `C0` — no skill
- `C1` — original skill
- `C2` — generic SkillX minimal rewrite
- `C2A` — class-aware SkillX minimal rewrite

### Why this matrix
- `C1 vs C0` → does the original skill help at all?
- `C2 vs C1` → does generic SkillX minimal rewriting help?
- `C2A vs C2` → does task-class-aware template structure help beyond generic C2?

Do **not** add `C3` or `C4` into this first class-aware comparison.
That would confound template effect with derived/refine effect.

---

## 4. Frozen scope for the first pilot

Use one representative task from each currently defined family:

1. `offer-letter-generator`
2. `parallel-tfidf-search`
3. `trend-anomaly-causal-inference`
4. `taxonomy-tree-merge`

This gives coverage over:
- Artifact Generator
- Engineering Composition Bundle
- Analytic Pipeline Bundle
- Methodology-Heavy Guardrail

Do not widen beyond these four tasks in the first comparison pilot.

---

## 5. Allowed inputs for generating C2A

A class-aware C2 rewrite worker may see only:
- the relevant template-family file
- the task's `task_class_profile.yaml`
- the task's rewrite notes
- the original skill file(s)
- the current generic `C2` skill file(s)

The worker must not see:
- benchmark scores for the same task
- C3 or C4 outputs for the same task
- other tasks' class-aware rewrites
- reference answers
- benchmark-specific hints outside the frozen protocol

---

## 6. Constraints on C2A

`C2A` must still behave like **C2**, not C3.

It may:
- sharpen scope and boundary logic
- sharpen task-shape-specific structure
- emphasize role partitioning, stage contracts, output contracts, or fit/abstention rules depending on task class
- add lightweight acceptance language if that is naturally part of the class prior

It must not:
- add `Derived Execution Layer`
- add explicit heavy evaluator-hook blocks
- add benchmark-targeted hacks
- add unsupported strategy not grounded in the original skill and task notes
- collapse into a monolithic checklist or C3-style execution contract

---

## 7. Evaluation question

The first class-aware comparison does **not** ask whether template families solve SkillX.
It asks a narrower and cleaner question:

> **Before any derived expansion or bounded refine, does class-aware structure produce a better starting point than generic C2?**

This is the outer-loop equivalent of testing whether the template family is a useful prior.

---

## 8. Success criteria for the first comparison pilot

A successful pilot does not require that `C2A` wins every task.
It requires that:
- the comparison is cleanly executable,
- condition packaging is unambiguous,
- `C2A` induces interpretable structural differences from `C2`,
- and the results are informative enough to decide whether class-aware C3/C4 is worth pursuing.

---

## 9. Recommended next step if this pilot is clean

If the comparison artifacts are trustworthy, the next step should be:
- keep `C2A` as the outer-loop-instantiated starting point,
- then test **class-aware C3** as template-guided derived expansion,
- and only later test **class-aware C4** as class-conditioned refine bias.
