# Agentic Proposing and SkillX: Overlap, Boundary, and Design Takeaways

- **Project:** `projects/skillX`
- **Date:** 2026-04-10
- **Role:** external paper deep-dive for SkillX framing
- **Primary source:** arXiv:2602.03279, *Agentic Proposing: Enhancing Large Language Model Reasoning via Compositional Skill Synthesis*
- **Status:** reading note

---

## 1. Why this memo exists

A Xiaohongshu post framed this paper as a possible “next-generation Agent paradigm” around recursive skill composition.

That framing is directionally interesting, but too loose for SkillX.

This note clarifies three things:

1. what the paper is actually about,
2. where it genuinely overlaps with SkillX,
3. where the research object is different enough that it should **not** displace SkillX’s main outer-loop story.

Short answer:

> **Agentic Proposing is a skill-composition-driven synthetic-data / problem-synthesis framework, not the same research object as SkillX.**

It is worth borrowing ideas from, especially around explicit skill representation and dynamic skill management, but it should be treated as adjacent inspiration rather than a direct template for SkillX.

---

## 2. What paper the Xiaohongshu post actually points to

The post footer points to:

- **arXiv:2602.03279**
- **Title:** *Agentic Proposing: Enhancing Large Language Model Reasoning via Compositional Skill Synthesis*

This is the correct source paper.

It should **not** be confused with CycleQD or other “skill acquisition” papers that use nearby language about recursive composition.

---

## 3. What the paper is actually doing

## 3.1 Main object

The paper’s main object is a **specialized proposer agent for synthetic problem generation**.

It is not primarily about:
- inference-time task routing,
- benchmark-time skill rewriting,
- or cross-task schema-bank assignment.

Instead, it asks how to train a proposer that can generate:
- high-difficulty,
- logically sound,
- verifiable

problems and trajectories for downstream solver training.

## 3.2 Core framing

The paper models problem synthesis as a **goal-driven sequential decision process / POMDP**, rather than as plain text generation.

The proposer maintains and manipulates a modular skill set while moving through cognitive stages such as:
- draft,
- check,
- refine,
- finalize.

## 3.3 Three-stage pipeline

The pipeline is roughly:

1. **Skill acquisition / library formalization**
   - collect and formalize modular skills from mixed corpora using a teacher policy and filtering.

2. **Agentic SFT**
   - train proposer trajectories with internal reflection, tool use, and dynamic skill editing / pruning.

3. **Agentic RL with MGPO**
   - further optimize the proposer as an interactive policy over the synthesis process.

## 3.4 Skill representation

One genuinely useful detail is that skills are represented explicitly and structurally, not only as loose prose.

The paper describes skill attributes along lines such as:
- intent,
- method,
- difficulty effect,
- tool-use hint.

This matters because it makes skills more composable and more governable inside an agent loop.

## 3.5 Why the paper is interesting

The paper’s strongest idea is not just “skills are useful.”

It is the claim that a proposer can:
- select a relevant subset of skills,
- compose them into harder or more novel reasoning problems,
- reflect on the current synthesis attempt,
- use tools,
- and dynamically prune misaligned skills during the process.

That is a concrete operationalization of compositional skill use.

---

## 4. What overlaps with SkillX

There is real overlap.

## 4.1 Skills are explicit external objects

Both Agentic Proposing and SkillX treat skill-like objects as things that can be:
- written down,
- manipulated,
- composed,
- and improved.

This is already closer to SkillX than papers where “skill” is only an implicit latent capability.

## 4.2 Closed-loop behavior matters

Both lines assume that one-shot prompting is not enough.

Useful behavior arises in a loop involving some combination of:
- structure,
- execution,
- checking,
- refinement,
- and selective retention.

## 4.3 Composition is operational, not decorative

Agentic Proposing gives evidence that modular skill composition can be implemented as part of a real control loop, rather than only as a conceptual story.

That is a useful existence proof for SkillX.

## 4.4 Dynamic pruning is relevant

The paper’s skill pruning idea is especially relevant.

SkillX does not have to assume that more schema content is always better.
It may matter to:
- shrink the active schema,
- drop irrelevant components,
- or render only a task-matched subset.

This connects naturally to SkillX questions about:
- schema size,
- granularity,
- negative transfer,
- and compression / internalization later on.

---

## 5. Where the boundary with SkillX is decisive

This is the most important section.

## 5.1 Agentic Proposing is mainly a synthetic-data / proposer-training paper

Its outer loop is mainly about improving a proposer that generates better training problems and trajectories.

That is different from SkillX’s main current object.

## 5.2 SkillX is about cross-task schema specialization

SkillX’s main thesis is:

> different task classes want different schema families, and the key learning problem is to discover, assign, and improve those schema families across tasks.

That means SkillX is centered on:
- schema bank design,
- task-to-schema assignment,
- cluster meaning,
- cross-task update,
- and task-class-aware specialization.

Agentic Proposing is **not** mainly solving that problem.

## 5.3 Their “outer loop” is not our outer loop

Agentic Proposing has a policy-training / data-generation loop.

SkillX’s outer loop is better described as:
- learn useful task partitions,
- learn which schemas fit which tasks,
- and update those schemas using evidence from many tasks.

So even though both involve iterative structure over skills, the outer-loop object is different.

## 5.4 Do not over-read the headline result

The reported downstream solver gains, including the strong AIME25 number, are downstream solver results after training on synthesized data.

They are **not** evidence that “recursive skill composition” by itself has solved general runtime-agent skill routing.

So the hype should be cooled.

---

## 6. What SkillX should borrow

The paper is still quite useful as a design source.

## 6.1 Borrow a more typed skill/schema format

SkillX should seriously consider explicit schema fields along lines such as:
- intent,
- method,
- expected effect,
- tool-use hint,
- maybe difficulty / risk effect.

This fits SkillX well because typed schema structure is easier to:
- render,
- prune,
- compare,
- compress,
- and potentially internalize later.

## 6.2 Borrow active-subset thinking

Instead of always injecting a full schema bundle, SkillX can ask:
- which parts are active for this task,
- which parts are removable,
- which parts are harmful noise.

That is useful both for augmentation quality now and internalization probes later.

## 6.3 Borrow composition as a first-class operation

SkillX should not assume a schema is a flat blob.

A more useful view may be:
- schemas have components,
- components can be activated or suppressed,
- and some task classes may need structured composition of multiple components.

## 6.4 Borrow pruning, not the entire proposer agenda

The pruning idea is easy to absorb.

The full proposer-training / MGPO agenda is much less aligned with current SkillX priority and would risk pulling the project away from its main contribution.

---

## 7. What SkillX should not borrow right now

## 7.1 Do not let this paper redefine SkillX as a data-generation project

That would blur the project’s center of gravity.

## 7.2 Do not let it shift priority away from outer-loop clarity

Current SkillX priority is still:
- make schema-bank differences real,
- make assignment explicit,
- test cross-task specialization,
- and show that clustering has operational value.

## 7.3 Do not over-invest in RL/proposer machinery before the outer-loop story is proven

The paper contains interesting RL machinery, but that should remain secondary inspiration for now.

---

## 8. Relevance to the current SkillX thesis

The cleanest relation is:

> **Agentic Proposing supports the claim that skills can be explicit, compositional, and dynamically managed.**

But it does **not** replace SkillX’s main thesis that:

> **the real missing object is outer-loop schema specialization across tasks.**

So this paper is best used as:
- a design-idea donor,
- a representation inspiration source,
- and a caution against treating skills as undifferentiated text blobs.

It is not the main comparative baseline for SkillX.

---

## 9. Reproducibility note

At the time of reading, the linked GitHub repository existed but appeared effectively empty.

So the paper should be treated as a useful conceptual and methodological reference, but not yet as a strong reproducible implementation package.

---

## 10. Bottom line

Agentic Proposing is best understood as:

> **a skill-composition-driven proposer framework for synthetic data generation and reasoning-task synthesis.**

For SkillX, the most useful takeaways are:
- explicit typed skill/schema structure,
- active subset selection,
- dynamic pruning,
- and stronger thinking about composition.

But the paper should **not** steal the main story from SkillX.

The main SkillX contribution should still be framed as:

> **outer-loop task-class-aware schema specialization, assignment, and cross-task update.**
