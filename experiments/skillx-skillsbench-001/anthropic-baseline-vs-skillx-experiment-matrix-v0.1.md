# Anthropic Baseline vs SkillX — Experiment Matrix v0.1

- **Project:** `projects/skillX`
- **Experiment line:** `experiments/skillx-skillsbench-001`
- **Date:** 2026-03-28
- **Role:** experiment matrix for comparing Anthropic-style local skill refinement baseline against the current and near-term SkillX / REP V2 line
- **Status:** planning memo / execution matrix

---

## 1. Why this document exists

We have already decided to treat Anthropic's latest skill-creator loop as an explicit external baseline.

That framing is useful, but still too abstract for execution.
We therefore need a more operational question:

> **What exactly should be compared, on which tasks, with what metrics, and what outcomes would support or weaken the SkillX / REP V2 story?**

This memo answers that question.

---

## 2. Core experimental goal

The point of this matrix is **not** to prove that our system beats Anthropic's baseline on every metric.
That would be the wrong standard.

The real goal is to test three progressively stronger claims:

### Claim A — class-aware structure helps
A class-aware starting point (`C2A`) is a better prior than generic minimal rewriting (`C2`) on at least some task families.

### Claim B — REP-style post-run experience extraction adds value beyond plain eval-driven iteration
A revision process informed by structured extracted experience can produce better next-step decisions than a loop driven only by benchmark outputs and qualitative review.

### Claim C — the right object of learning is not just the single skill, but the task-class template family
Across multiple tasks in the same family, gains should show signs of **reusability**, not just one-off local tuning.

---

## 3. Baseline / condition definitions

For this matrix, use the following condition names.

### `A0` — Anthropic-style local baseline
A practical local-skill refinement condition modeled after Baseline A:
- single skill artifact as the main object;
- with-skill vs no-skill / old-skill comparison;
- explicit benchmark and qualitative review;
- skill-body refinement based on eval outcomes and reviewer feedback;
- no REP-style explicit experience extraction;
- no class-aware template-family prior unless already present in the original skill.

This is not meant to reimplement Anthropic's whole tooling stack exactly.
It is meant to capture the **same loop logic**.

### `C0` — No skill
The raw no-skill control.

### `C1` — Original skill
The task's original skill artifact.

### `C2` — Generic SkillX minimal rewrite
The current generic minimal rewrite condition.

### `C2A` — Class-aware SkillX minimal rewrite
The class-template-instantiated lightweight rewrite.

### `R1` — SkillX + REP-informed local refine
A local refine pass that uses:
- benchmark and output review,
- plus REP-style extracted experience from the completed run/session,
- but still targets the local task artifact.

This is the first condition that actually tests whether REP adds decision value.

### `T1` — Class-aware + REP-informed template-guided refine
A stronger experimental condition where:
- the starting point is class-aware (`C2A`),
- post-run revision uses REP-style extracted experience,
- and revision decisions are interpreted through the task-class template family.

This is the first real proxy for the intended SkillX / MARC direction.

---

## 4. Recommended phase structure

Do **not** run every condition immediately.
The cleanest plan is phased.

### Phase 1 — frozen structure comparison
Compare:
- `C0`
- `C1`
- `C2`
- `C2A`

Purpose:
- isolate whether class-aware structure helps **before** refine logic is added.

This phase is already aligned with the current class-aware C2 protocol.

### Phase 2 — local refine logic comparison
On a smaller subset of tasks, compare:
- `A0`
- `C2`
- `C2A`
- `R1`

Purpose:
- test whether REP-informed local revision adds anything beyond a clean Anthropic-style local loop.

### Phase 3 — outer-loop object comparison
On the most promising task family, compare:
- `A0`
- `R1`
- `T1`

Purpose:
- test whether template-family-aware revision produces more transferable gains than single-skill local refinement.

---

## 5. Frozen task set

Use the same representative task set already chosen for the first class-aware comparison pilot:

1. `offer-letter-generator`
2. `parallel-tfidf-search`
3. `trend-anomaly-causal-inference`
4. `taxonomy-tree-merge`

These map onto four distinct task families:
- Artifact Generator
- Engineering Composition Bundle
- Analytic Pipeline Bundle
- Methodology-Heavy Guardrail

This is a good first matrix because it covers the structural families we currently care about without exploding the scope.

---

## 6. Main comparison questions by task family

### 6.1 Artifact Generator — `offer-letter-generator`
Main question:

> does class-aware structure improve output contract preservation, missing-input discipline, and no-invention behavior?

Why it matters:
- this is a class where lighter but sharper structure may outperform verbose guidance.
- it is also a good place to test whether REP extraction adds much, or whether straightforward eval-driven revision is already enough.

Expected signal:
- `C2A` should outperform `C2` mainly on boundary control and contract discipline.
- `R1` may help, but expected incremental gain may be smaller than on more structurally complex tasks.

### 6.2 Engineering Composition Bundle — `parallel-tfidf-search`
Main question:

> does class-aware structure improve multi-skill coordination, precedence resolution, and correctness-before-speed behavior?

Why it matters:
- this class is where generic minimal rewrites may leave too much role ambiguity.
- it is also where local benchmark-only refinement may overlook deeper coordination failure patterns.

Expected signal:
- `C2A` should beat `C2` on role partitioning clarity.
- `R1` has a stronger chance to add value by extracting reusable coordination failures.

### 6.3 Analytic Pipeline Bundle — `trend-anomaly-causal-inference`
Main question:

> do class-aware templates and REP-style post-run experience help maintain stage-local artifact contracts and handoff correctness?

Why it matters:
- this currently looks like the strongest candidate class for true outer-loop learning.
- the task structure naturally exposes stage confusion, malformed handoffs, and local-vs-global success mismatches.

Expected signal:
- `C2A` should noticeably outperform `C2` as a starting point.
- `R1` should outperform plain `A0` if REP extraction is genuinely useful.
- `T1` has the strongest chance to show early outer-loop value.

### 6.4 Methodology-Heavy Guardrail — `taxonomy-tree-merge`
Main question:

> does class-aware structure improve fit checks, abstention logic, and anti-pattern resistance more than local benchmark optimization alone?

Why it matters:
- this class is important because the right move may often be restraint, deletion, or branch selection rather than adding more execution instructions.

Expected signal:
- `C2A` should beat `C2` mainly on methodological discipline.
- `A0` may struggle if local benchmark feedback under-specifies the value of fit checks.
- `R1` or `T1` may help if extracted experience captures repeated misfit patterns.

---

## 7. Metric families

The comparison should not collapse to one scalar score.
Use a small metric family.

### 7.1 Task-success metrics
These are task-specific pass/fail or graded success outcomes.
Examples:
- artifact meets contract;
- output accepted by deterministic checker;
- pipeline stages complete with valid intermediate artifacts;
- merge result satisfies methodology constraints.

### 7.2 Boundary / risk-control metrics
These are especially important for SkillX.
Examples:
- invention / hallucination rate;
- missing-input handling quality;
- wrong-branch or wrong-fit invocation;
- stage leakage;
- conflict-resolution failures;
- abstention correctness.

### 7.3 Resource metrics
Anthropic correctly foregrounds these.
Track:
- duration;
- total tokens;
- tool calls where possible.

### 7.4 Revision-efficiency metrics
These become important in Phase 2+.
Examples:
- number of iterations to reach acceptable quality;
- delta in pass rate from revision 0 to revision 1;
- whether the revision introduced regressions elsewhere.

### 7.5 Transfer / reuse metrics
These are what matter for the outer-loop story.
Examples:
- whether a template-family update helps another task in the same class;
- whether a lesson extracted on one task is reused correctly on another;
- whether improvements remain local or begin to generalize.

---

## 8. Evidence bundle requirements

Each condition run should preserve a minimal evidence bundle.

### Required artifacts
- skill or template artifact used for the run;
- task prompt / input bundle;
- final outputs;
- deterministic grading results where available;
- benchmark summary;
- timing/tokens summary;
- short reviewer note.

### Additional artifacts for `R1` / `T1`
- extracted experience unit(s);
- revision rationale linked to those extracted units;
- note on whether the revision was local-only or interpreted through a template-family prior.

Without these artifacts, later comparison claims will be weak.

---

## 9. Recommended primary analyses

### Analysis 1 — structure prior value
Compare `C2` vs `C2A` across all four tasks.

Question:
> is class-aware structure already a better R0 than generic minimal rewriting?

This is the cleanest first analysis.

### Analysis 2 — REP value over local eval-only iteration
Compare `A0` vs `R1` on 2 tasks:
- `parallel-tfidf-search`
- `trend-anomaly-causal-inference`

Question:
> when benchmark outputs are not enough to explain failures cleanly, does REP-style extracted experience produce better next-step revision decisions?

These two tasks are recommended because they are more structurally rich than pure artifact generation.

### Analysis 3 — outer-loop object test
Compare `R1` vs `T1` within the analytic-pipeline class.
Use at least:
- `trend-anomaly-causal-inference`
- and one second analytic-pipeline task from the larger set if feasible

Question:
> is there any sign that class-aware template-family-guided revision transfers better than purely local REP-informed revision?

This is the first direct test of the intended outer-loop story.

---

## 10. Expected result patterns

We should define in advance what kinds of results would support or weaken the project thesis.

### Pattern P1 — strong support for class-aware priors
Observed if:
- `C2A` beats `C2` on at least 2 of 4 tasks;
- especially on boundary-control or coordination metrics;
- without obvious resource blow-up.

Interpretation:
- class-aware template families are a plausible outer-loop object.

### Pattern P2 — weak support for class-aware priors
Observed if:
- `C2A` is mostly indistinguishable from `C2`,
- or wins only cosmetically.

Interpretation:
- either the family templates are too weak,
- or the chosen task-class abstraction is not yet the right one.

### Pattern P3 — strong support for REP-informed revise
Observed if:
- `R1` reaches a better next iteration than `A0` on structurally complex tasks,
- especially by fixing failure patterns that plain benchmark review did not surface clearly.

Interpretation:
- REP is contributing genuinely useful post-run evidence, not just duplicate commentary.

### Pattern P4 — weak support for REP-informed revise
Observed if:
- `R1` behaves like a verbose restatement of benchmark findings,
- with no meaningful revision advantage over `A0`.

Interpretation:
- REP extraction either lacks the right semantic granularity,
- or is not yet connected to revision decisions in a meaningful way.

### Pattern P5 — early support for outer-loop learning
Observed if:
- `T1` improves more consistently across two tasks in the same class than `R1`,
- or a template-family update derived from one task helps another in the same class.

Interpretation:
- the task-class template family may indeed be a useful object of abstraction.

### Pattern P6 — no outer-loop signal yet
Observed if:
- `T1` reduces to task-local tweaking,
- or template-level updates do not transfer.

Interpretation:
- the outer-loop object may still be too early, too vague, or too coarsely defined.

---

## 11. Practical recommendation

The immediate next step should remain modest.
Do **not** try to execute the full matrix at once.

Recommended order:

1. finish / freeze the `C0-C1-C2-C2A` comparison on the four representative tasks;
2. choose **two structurally rich tasks** for `A0 vs R1`;
3. only if `R1` shows nontrivial value, proceed to `R1 vs T1`.

This order keeps the project disciplined:
- first test the structure prior,
- then test REP as an added evidence source,
- then test the outer-loop abstraction object.

---

## 12. Bottom line

The purpose of Anthropic Baseline A is not to become the enemy or the target to beat on every axis.
It is to give us a clean reference point for what a serious **local skill refinement loop** already looks like.

The central experiment question is therefore:

> **Can SkillX / REP V2 / MARC produce evidence that the right object of learning is richer than a single locally refined skill — first through class-aware priors, then through extracted experience, and eventually through transferable task-class template evolution?**

This matrix is the first concrete path to answering that question.
