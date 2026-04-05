# Anthropic Skill Creator as a Baseline for SkillX / REP V2 / MARC

- **Project:** `projects/skillX`
- **Date:** 2026-03-28
- **Role:** external baseline memo for comparing Anthropic's latest skill-creator loop against the current SkillX / REP V2 / MARC line
- **Status:** baseline framing note

---

## 1. Why this memo exists

Anthropic's recent writeup on **improving skill-creator** is close enough to our current direction that it should not be treated only as inspiration.

It should be treated as a **reference baseline**.

That means:
- we should explicitly compare our current and proposed loops against it;
- we should reuse its stronger practical ideas where appropriate;
- and we should be precise about where our design target goes beyond it.

The goal of this memo is therefore not to criticize Anthropic's approach.
The goal is to define a clean baseline object that our own line can be compared against.

---

## 2. Baseline A — what exactly we mean

For the rest of this project, define:

> **Baseline A = Anthropic Skill Creator loop**

At the highest level, Baseline A looks like:

1. draft or edit a skill;
2. create a small set of test prompts;
3. run **with-skill** and **baseline** executions;
4. add assertions / grading;
5. aggregate benchmark results;
6. show outputs and metrics to a human reviewer;
7. rewrite the skill;
8. rerun into a new iteration;
9. repeat until satisfied.

In addition, Anthropic's latest skill-creator also includes a **description optimization loop** for improving skill triggering.
That sub-loop is more explicitly automated than the main skill-body revision loop.

So Baseline A is best described as:

> **an eval-driven, human-in-the-loop skill refinement workflow with optional blind comparison and automated description-trigger optimization**.

---

## 3. What Baseline A gets importantly right

Anthropic's loop is worth taking seriously because it gets several core engineering choices right.

### 3.1 It treats skills as testable objects
The key move is not merely "skills are useful." The key move is:

> **a skill should be tied to evals, measured outcomes, and repeated revision.**

This is the minimum step required to make skills evolvable rather than static prompt assets.

### 3.2 It compares against a real baseline
For new skills, the baseline is **without skill**.
For improving an existing skill, the baseline may be the **old skill snapshot**.

This is an important discipline.
Without a baseline, "improvement" is mostly storytelling.

### 3.3 It separates qualitative review from quantitative benchmarking
The workflow does not rely only on user vibes, and it does not rely only on benchmark numbers.
It keeps both:
- human review of outputs,
- quantitative assertions / pass rates / timing / token usage.

That is the correct shape for practical skill iteration.

### 3.4 It uses isolated runs to reduce contamination
Anthropic's design explicitly emphasizes clean-context comparison across runs.
This is especially relevant to skill evaluation because context bleed can invalidate comparisons.

### 3.5 It takes triggering seriously
A skill that produces better outputs but fails to trigger reliably is still weak in practice.
The dedicated description optimization loop addresses a real deployment bottleneck.

---

## 4. The two refine loops inside Baseline A

One important clarification is that Anthropic's current public design actually contains **two different refinement loops**.

### 4.1 Skill-body refine loop
This is the main loop:
- write / edit skill;
- run evals;
- benchmark;
- review outputs;
- revise skill body;
- rerun.

This loop is **iterative but not fixed-round**.
The current public framing is essentially:
- keep going until the user is satisfied,
- or feedback goes empty,
- or meaningful progress stops.

So the main refine loop is best understood as:

> **structured human-guided iterative refinement**

rather than a fixed-k autonomous optimization routine.

### 4.2 Description-trigger refine loop
This second loop is more automated.
The public skill-creator documentation describes a `run_loop` process that:
- builds trigger eval queries;
- splits train vs held-out test;
- runs each query multiple times to estimate trigger rate;
- proposes improved descriptions;
- reevaluates;
- selects the best description by held-out test score.

This loop appears to use an explicit `--max-iterations 5` cap.

So this sub-loop is best understood as:

> **bounded automated optimization of the trigger description**

rather than open-ended human-guided refinement.

---

## 5. Why this baseline matters for SkillX

Baseline A matters because it validates the practical importance of our current SkillX line.

The overlap is strongest in the following areas.

### 5.1 Skills become interesting when tied to explicit eval loops
This strongly supports the current SkillX move from static skill variants toward:
- comparison protocols,
- bounded refine,
- and evidence-backed variant selection.

### 5.2 A/B or skill-vs-baseline comparison is not optional
This resonates directly with the current SkillX comparison direction around:
- `C0`
- `C1`
- `C2`
- `C2A`

If we do not compare structured alternatives against a control, we are not really learning.

### 5.3 Triggering is part of the system, not an afterthought
Anthropic's description optimization is the strongest practical reminder that a skill system has two separate success questions:
1. does the skill improve execution when used?
2. does the system use the skill when it should?

SkillX should keep both questions visible.

---

## 6. Where our line is still different

The main reason this should be a baseline rather than a destination is that our current project is aiming at a different object level.

### 6.1 Baseline A primarily optimizes a single skill artifact
Anthropic's main unit of refinement is:
- a specific skill,
- plus its trigger description.

Even when comparing iterations, the target of improvement remains fundamentally local.

### 6.2 SkillX is moving toward class-aware template families
Our current design has already shifted toward a different outer-loop object:

> **the task-class template family**

rather than one universal skill rule and rather than only one local skill artifact.

This matters because many useful guidance patterns are not universal across all tasks, but they are also not purely one-off local hacks.
They live at an intermediate level.

### 6.3 REP V2 introduces an additional evidence source
Baseline A is driven mainly by:
- eval outputs,
- assertions,
- benchmarks,
- human feedback.

Our current architecture introduces a second important source:

> **single-run experience extraction**

In current framing, REP V2 is not the whole inner loop.
It is a **single-run extraction submodule** that analyzes a completed run and emits reusable experience.

That gives us a possible evidence stream that is richer than final benchmark deltas alone.

### 6.4 MARC is community-scale rather than purely local-skill-scale
Anthropic's public framing is still mostly about making one skill better and keeping it working as models evolve.

MARC is aiming at a larger question:

> can many local optimization episodes be aggregated into reusable task-class-level guidance for a community?

That is a different research claim from "iteratively improve a skill with evals."

---

## 7. A clean comparison frame

For project discussions, the most useful comparison frame is probably this one.

### Baseline A — Anthropic Skill Creator
**Loop topology**
- draft → eval → review → improve → rerun

**Refine object**
- single skill artifact
- plus skill description

**Primary evidence**
- eval outputs
- assertions
- benchmark metrics
- human feedback
- optional blind comparison

**Generalization target**
- stronger local skill
- more reliable triggering

**Automation level**
- main skill refine = human-in-the-loop
- description refine = bounded automated loop

---

### Ours-1 — SkillX current comparison line
**Loop topology**
- compare structured variants (`C0/C1/C2/C2A/...`) on representative tasks

**Refine object**
- skill variants / rewrite styles / bounded refine variants

**Primary evidence**
- cross-task comparison results
- verifier outcomes
- failure observations

**Generalization target**
- identify which kinds of skill structuring help or hurt under different task shapes

**Automation level**
- still partly manual / experimental

---

### Ours-2 — SkillX + REP V2
**Loop topology**
- run → extract reusable experience → revise skill/template candidate → reevaluate

**Refine object**
- not only the visible skill text, but also the reusable experience layer informing revisions

**Primary evidence**
- benchmark/eval evidence
- plus REP-extracted experience units

**Generalization target**
- better local revisions with richer post-run evidence

**Automation level**
- hybrid; extraction remains script-first / workflow-driven / agent-assisted

---

### Ours-3 — MARC / MetaEvolver target
**Loop topology**
- aggregate many local refinement episodes into outer-loop abstraction

**Refine object**
- task-class template family

**Primary evidence**
- many inner-loop runs
- extracted experience bundles
- transfer and cross-task comparison signals

**Generalization target**
- community-valid reusable meta-guidance for a task class

**Automation level**
- still a research target, not yet a finished system

---

## 8. What we should directly borrow from Baseline A

Even if our target is broader, there are several concrete mechanisms we should consider borrowing almost directly.

### 8.1 Always keep an explicit baseline arm
At minimum:
- no-skill baseline,
- old-version baseline,
- or simpler-template baseline.

### 8.2 Keep qualitative and quantitative evaluation separate but linked
A good loop should preserve both:
- benchmark summaries,
- and human inspection of actual outputs.

### 8.3 Preserve per-iteration artifact structure
Anthropic's iteration workspace pattern is simple but useful.
A SkillX / MARC loop should also preserve:
- iteration lineage,
- run artifacts,
- grading outputs,
- benchmark summaries,
- user or evaluator feedback.

### 8.4 Treat triggering/routing as a first-class evaluation target
For us this may not be only "description optimization."
In a broader SkillX framing, this becomes:
- routing precision,
- task-class classification quality,
- and template-family selection correctness.

### 8.5 Use isolated execution when comparing variants
If two variants are compared under contaminated or asymmetric runtime conditions, the result is weak.
This should remain a hard discipline.

---

## 9. What we should *not* collapse into Baseline A

It is equally important not to compress our project back down into the baseline.

### 9.1 Do not reduce the outer loop to single-skill revision
If our only output is "a better prompt-like skill," then the task-class MetaEvolver story disappears.

### 9.2 Do not let REP V2 get redefined as just another benchmark helper
REP V2 should remain conceptually distinct as an experience extraction submodule.
It is not only a grader, not only a dashboard, and not only a benchmark wrapper.

### 9.3 Do not assume that better local benchmark performance is the whole objective
A community-scale project also cares about:
- transfer,
- portability,
- negative-transfer detection,
- template simplification,
- and cross-task reuse.

---

## 10. Recommended project usage

For the near term, Anthropic's skill-creator should be used in this project as:

> **Baseline A: the strongest publicly visible practical loop for eval-driven skill refinement**

In concrete terms, we should use it for:
- discussion framing,
- experiment motivation,
- baseline-comparison language,
- and scoping our novelty claims.

A good disciplined statement is:

> Anthropic's latest skill-creator gives us a credible baseline for local skill refinement. Our question is whether the same engineering discipline can be lifted from single-skill iteration to class-aware template evolution and community-scale meta-guidance.

---

## 11. Bottom line

Anthropic's latest skill-creator is close enough to our direction that it should be treated as a baseline, not just a nearby idea.

The strongest summary is:

> **Baseline A solves the local skill-refinement problem in a practical eval-driven way. SkillX / REP V2 / MARC asks whether we can lift that logic into richer evidence extraction, task-class-aware template evolution, and eventually community-scale reusable guidance.**

That is the right relationship:
- not dismissal,
- not imitation,
- but **baseline-relative advancement**.
