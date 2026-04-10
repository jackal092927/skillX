# EvoSkills vs SkillX: Method Structure, Verification Signal, and Baseline Relevance

- **Project:** `projects/skillX`
- **Date:** 2026-04-10
- **Role:** external baseline memo clarifying how EvoSkills relates to the current SkillX line
- **Status:** comparison note

---

## 1. Why this memo exists

EvoSkills is currently the strongest nearby external baseline for SkillX.

The overlap is real enough that we should be precise about:
- where the two pipelines are genuinely similar,
- where they differ structurally,
- what signal EvoSkills actually optimizes,
- and why EvoSkills should be treated as a main comparison target rather than only background reading.

This memo is also meant to answer a practical project question:

> Is EvoSkills basically doing something close to SkillX already, or is it solving a meaningfully different problem?

Short answer:

> **EvoSkills is close in high-level spirit, but not identical in optimization object or verification pathway.**

At a coarse level, both are iterative skill optimization systems with a two-part feedback structure.
At a finer level, EvoSkills is a **per-task co-evolutionary skill-generation system with a surrogate verifier**, whereas current SkillX is an **evaluator-in-the-loop, schema-specialized skill optimization system**.

---

## 2. What EvoSkills is, in one paragraph

EvoSkills proposes a self-evolving framework for autonomously generating multi-file agent skill packages. It uses two co-evolving components:

1. a **Skill Generator** that drafts and revises the skill bundle, and
2. a **Surrogate Verifier** that generates deterministic proxy tests and structured diagnostics.

When the surrogate tests pass, the current skill is re-executed under a fresh hidden oracle evaluation. The oracle does **not** reveal ground-truth test content, only a success or failure signal. If oracle failure exposes a gap between the surrogate tests and the hidden evaluator, the verifier escalates its tests and the loop continues.

So the core idea is not just iterative rewrite.
It is:

> **co-evolution of the skill and the verifier that critiques it.**

---

## 3. Is the high-level pipeline similar to SkillX?

## 3.1 Yes, at a coarse level

At the highest level, EvoSkills and SkillX do look similar.

Both have the following broad shape:

1. start from a task-conditioned skill object,
2. run an execution,
3. get task-linked feedback,
4. revise the skill,
5. keep improving under a bounded iterative loop,
6. keep track of the best candidate.

This is why EvoSkills feels immediately familiar from a SkillX perspective.

## 3.2 But the loop boundary is different

The most important structural difference is **what the second loop is actually doing**.

### EvoSkills
The second loop is mainly:
- verifier evolution,
- test-suite escalation,
- and skill revision under verifier pressure.

That is, its “outer” feedback structure is still mostly **within one task**.

### SkillX
The current SkillX second loop is mainly:
- schema-conditioned specialization,
- task-to-schema assignment,
- and schema bank update across many tasks.

That means SkillX’s outer loop is not mainly a verifier-improvement loop.
It is a **cross-task specialization loop**.

So the cleanest framing is:

> **EvoSkills has a two-part co-evolution loop inside a task.**  
> **SkillX has an inner optimization loop plus an outer schema-specialization loop across tasks.**

Because of that, the two systems are analogous, but not architecturally identical.

---

## 4. What signal does EvoSkills optimize?

This is the most important difference.

## 4.1 EvoSkills defines a hidden oracle reward

EvoSkills formalizes the task with a hidden ground-truth reward `R(x_T)` over the final execution state.

On SkillsBench, this corresponds to the task verifier and final pass/fail outcome.
The paper treats the main metric as task pass rate, that is, whether the final reward is `1.0` or `0.0`.

But crucially, the agent does **not** get full access to the oracle test content.

## 4.2 Dense feedback comes from a surrogate verifier, not the oracle itself

The paper introduces a surrogate reward:

> `R_tilde(x, V)` = average pass rate over a verifier-generated set of deterministic assertions.

The surrogate verifier:
- sees the task instruction,
- sees the current output artifacts,
- generates deterministic assertions / tests,
- and returns structured failure diagnostics.

So the dense optimization signal comes from the **surrogate verifier’s tests**, not directly from the hidden oracle tests.

## 4.3 The oracle is still used, but only as a hidden pass/fail signal

When the current skill passes the surrogate tests, EvoSkills re-runs it in a fresh environment under the hidden oracle evaluator.

The oracle then returns only:
- success/failure,
- or equivalently a binary reward signal,
- without exposing test content.

If the surrogate says “pass” but the oracle says “fail”, that mismatch triggers **test escalation** in the verifier.

So the operational split is:

- **surrogate verifier** = dense feedback and critique,
- **oracle evaluator** = hidden final gate and best-snapshot signal.

## 4.4 Comparison to current SkillX

Current SkillX is simpler.

The present main line is closer to:
- direct benchmark evaluator access,
- evaluator-in-the-loop selection,
- fixed round budget,
- best-so-far incumbent under that budget.

So the current contrast is:

- **EvoSkills**: surrogate verifier for dense feedback, hidden oracle for final correction
- **SkillX**: direct benchmark evaluator in loop, without a separately evolving verifier yet

This means Xin’s instinct is right:

> SkillX already uses task-linked test signal, but its inner loop is currently simpler than EvoSkills because it does not yet evolve verifier candidates or verifier-generated test suites.

---

## 5. How close is EvoSkills to current SkillX?

## 5.1 Similarities

The most important similarities are:

### A. Both optimize skills, not just prompts
Both systems target a richer skill object than a one-line instruction.

### B. Both are iterative rather than one-shot
Neither system claims that one-pass generation is enough.

### C. Both are evaluator-linked
Both are fundamentally anchored to task success signals rather than purely stylistic preference.

### D. Both maintain a best candidate under bounded search
EvoSkills explicitly tracks the best oracle score so far and returns the best skill snapshot.
Current SkillX also centers best-so-far selection under a fixed budget.

## 5.2 Differences

### A. EvoSkills is per-task evolution; SkillX is moving toward cross-task specialization
EvoSkills evolves a skill for a single task instance/task environment.
SkillX’s main research object is increasingly:
- schema bank,
- assignment,
- specialization,
- and task-class-aware transfer.

### B. EvoSkills uses verifier co-evolution; SkillX currently does not
EvoSkills improves both the skill and the proxy verifier.
SkillX currently improves the skill under evaluator signal, but does not yet run a full verifier-escalation loop.

### C. EvoSkills does not center schema-bank assignment as its outer loop
Its second loop is not about finding the best reusable schema family across tasks.
That remains more specific to SkillX.

### D. EvoSkills is more autonomous in the inner loop than current SkillX
Its inner loop already includes:
- proxy test generation,
- failure diagnosis,
- and test escalation.

Current SkillX is intentionally simpler at this stage.

---

## 6. What exactly is the Anthropic Skill Creator relation?

The paper makes two Anthropic-related uses explicit.

## 6.1 Meta-skill initialization
In Algorithm 1, EvoSkills initializes from a domain-agnostic meta-skill:

> `S_meta` = `skill-creator`

So Anthropic’s skill-creator idea is part of EvoSkills’ initialization setup.

## 6.2 Skill-Creator is also one of the baselines
The paper also evaluates a **Skill-Creator** baseline.
It says this baseline adopts Anthropic’s official skill-creator, but replaces human-interactive steps with autonomous equivalents:
- one session drafts / tests / refines the skill for at least three iterations,
- another session solves the task using the resulting skills.

This is important for SkillX because it means the paper is not only “inspired by Anthropic skills” in the abstract.
It explicitly uses Anthropic’s official skill-creator line both as a reference artifact and as a comparison condition.

---

## 7. What baselines and numbers does EvoSkills report on SkillsBench?

The paper reports the core comparison on **Claude Opus 4.6 + Claude-Code**.

From the main comparison section:

- **EvoSkills**: `71.1%`
- **No-skill baseline**: `30.6%`
- **Human-curated skills**: `53.5%`
- **Skill-Creator baseline**: `34.1%`
- **Simpler single-session variant**: `32.4%`
- **SkillsBench self-generated skills baseline**: `32.0% ± 3.1`
- **CoT-guided self-generation**: `30.7% ± 5.2`

The paper also reports an ablation result that removing the surrogate verifier drops pass rate from:

- `71.1%` → `41.1%`

and reports that using background context alone yields:

- `48.6%`

One important nuance:
- the main comparison reports `71.1%`,
- while the evolution-dynamics section says the curve converges to about `75%` by round 5.

So when citing numbers, the safest public number for the headline comparison is:

> **71.1% pass rate on SkillsBench in the main benchmark comparison.**

---

## 8. Why EvoSkills should be treated as a main baseline for SkillX

EvoSkills is a main baseline not because it is identical to SkillX, but because it is the strongest nearby system on the same broad object.

### 8.1 Same broad object of optimization
It optimizes agent skills, not generic prompts, not generic tools, and not only final policies.

### 8.2 Same benchmark substrate
It evaluates on SkillsBench, which is already the main first substrate for current SkillX.

### 8.3 Same central question
At a high level, both projects ask:

> how can we improve skill quality so the agent performs better on real tasks?

### 8.4 Different enough to make comparison meaningful
Because EvoSkills emphasizes verifier co-evolution and per-task skill evolution, while SkillX emphasizes schema specialization and outer-loop assignment, a comparison would actually teach us something.

---

## 9. What this implies for future SkillX design

## 9.1 Xin’s current read is directionally correct
Xin’s current interpretation is basically right:

1. **the high-level pipeline is indeed similar in spirit**, and
2. **current SkillX inner loop is simpler than EvoSkills’ inner loop**.

That is the correct high-level takeaway.

## 9.2 The surrogate verifier idea is genuinely relevant future work
EvoSkills is strong evidence that SkillX should at least keep open a future branch like:

- current line: direct evaluator-in-the-loop optimization,
- future line: add a verifier-generation / surrogate-verifier layer when oracle access is weaker or expensive.

This is especially relevant if SkillX later wants to move from:
- full benchmark evaluators,
- to weaker production-time evaluators or partial rubrics.

## 9.3 But it should not block the current pipeline
The current project priority should remain:

1. run the present evaluator-in-the-loop pipeline end-to-end,
2. establish the schema-specialization outer loop cleanly,
3. only then add more ambitious verifier co-evolution machinery.

In other words:

> EvoSkills should influence the future SkillX roadmap, but it should not derail the current execution-first phase.

---

## 10. Bottom line

The cleanest current summary is:

> **EvoSkills is the nearest strong external baseline because it is an iterative skill-optimization system on SkillsBench, but its main novelty is surrogate-verifier co-evolution inside a task, whereas SkillX’s main novelty is evaluator-in-the-loop schema specialization across tasks.**

That means:
- yes, the two systems are genuinely similar at a high level;
- yes, current SkillX inner-loop logic is simpler than EvoSkills;
- yes, the surrogate verifier is a meaningful future direction;
- and yes, EvoSkills should be treated as a main comparison target for SkillX.
