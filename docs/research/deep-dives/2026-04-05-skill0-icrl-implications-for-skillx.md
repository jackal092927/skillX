# Skill0 / ICRL 对 SkillX 的启发

_Date: 2026-04-05_

## Why this memo exists

Recent work around **SKILL0** and **ICRL** is directly relevant to SkillX because it
shifts the question from:

- how to retrieve and inject skills better at inference time

to:

- how to use skills as training-time scaffolds and then **internalize** them into
  the policy so they can be removed at inference time.

That is not the same problem SkillX is currently solving, but it is close enough
that it changes how we should think about the long-term role of SkillX artifacts.

## Papers

### 1) SKILL0

- Title: `SKILL0: In-Context Agentic Reinforcement Learning for Skill Internalization`
- arXiv: <https://arxiv.org/abs/2604.02268>
- Code: <https://github.com/ZJU-REAL/SkillZero>

### 2) ICRL

- Title: `In-Context Reinforcement Learning for Tool Use in Large Language Models`
- arXiv: <https://arxiv.org/abs/2603.08068>

## Executive summary

### SKILL0 in one sentence

SKILL0 treats skills as **temporary training-time support**: provide them during
RL rollouts, measure whether each skill still helps the current policy, and
progressively withdraw them until the agent succeeds in a fully zero-skill
inference setting.

### ICRL in one sentence

ICRL replaces SFT-based tool-use bootstrapping with an RL-only regime where the
model first sees in-context tool-use demonstrations during rollout, then learns
to invoke tools after those demonstrations are gradually removed.

### The shared pattern

Both papers instantiate the same higher-level idea:

> External structure is useful early, but the end goal is not permanent external
> dependence. The end goal is autonomous competence after scaffold withdrawal.

This is the core reason they matter for SkillX.

## What SKILL0 is actually contributing

## Problem framing

SKILL0 starts from a critique of standard inference-time skill augmentation:

1. retrieval can be noisy
2. injected skills cost tokens every step
3. the model may be executing a skill description without actually learning it

The paper's main conceptual move is to say that "good skill use" and "skill
internalization" are different objectives.

- **skill augmentation**: make runtime retrieval + injection effective
- **skill internalization**: transfer competence from external context into model
  parameters

That distinction is important for SkillX because our current work is primarily
on the augmentation-side object: prompt templates, task-class-aware structures,
rewrite/refine protocols, and outer-loop update rules.

## Method sketch

SKILL0 has three notable components.

### 1) ICRL-style training loop

During training rollouts, the policy receives skill context as guidance.
At inference time, those skills are removed entirely.
This forces RL to optimize for eventual zero-skill competence rather than
permanent skill-conditioned execution.

### 2) Helpfulness-driven dynamic curriculum

Rather than withdrawing all skills on a fixed schedule, SKILL0 estimates whether
an individual skill file is still useful to the current policy.
The curriculum keeps skills that still help and removes those that no longer add
marginal value, under a budget that shrinks to zero.

This is the most interesting part of the paper from a SkillX perspective.

### 3) Context rendering / compression

The paper also compresses interaction history + skill context into visual form
for a VL model, reducing token overhead. This may matter for their specific
setup, but it is probably not the main reusable idea for SkillX.

The key reusable idea is not "render text as images." The key reusable idea is
"measure scaffold helpfulness and retire scaffolds adaptively."

## What ICRL is actually contributing

ICRL is a more general and cleaner precursor pattern.

## Problem framing

Tool-use post-training often relies on an expensive pipeline:

- collect or synthesize demonstrations
- do SFT
- then do RL

ICRL asks whether SFT can be skipped.
Its answer is to use **in-context examples during RL rollouts** as soft
training-time supervision.
Then those examples are gradually reduced until the model performs tool use in a
zero-shot setting.

## Main contribution

The paper establishes the scaffold-withdrawal template in a simpler form:

- external demonstrations are used during RL
- RL turns them into internalized behavior
- scaffold quantity is annealed down over time

SKILL0 appears to extend this pattern from tool-use examples to a richer notion
of reusable agent skills.

## Direct comparison: ICRL vs SKILL0

## What is being internalized?

### ICRL

- tool-use behavior
- structured calling patterns
- reasoning + invocation formatting induced by few-shot examples

### SKILL0

- reusable skill files / procedural guidance
- multi-turn action patterns tied to task categories
- a broader notion of agent behavior than simple tool-call formatting

## What is provided during training?

### ICRL

- few-shot in-context examples

### SKILL0

- retrieved / grouped skill files
- task-aligned skill categories
- interaction-history-conditioned skill support

## What is withdrawn?

### ICRL

- the number of in-context examples

### SKILL0

- the active skill subset
- eventually all skill context

## What is special about the curriculum?

### ICRL

- staged reduction of examples
- cleaner demonstration that RL can internalize external structure without SFT

### SKILL0

- more explicit per-skill helpfulness evaluation
- a retirement policy for scaffold components rather than just a global count

## Why this matters for SkillX

SkillX is not an RL training framework, and that distinction should remain
clear. But the papers suggest a deeper interpretation of what SkillX artifacts
could become.

## Current SkillX role

Right now SkillX mostly treats skills / templates as:

- external artifacts
- authorable and rewritable objects
- class-aware prompt structures
- outer-loop units for comparison, assignment, and update

That is already useful.
But SKILL0/ICRL suggests a second role:

- **training-time curriculum objects**

This opens a new two-layer framing.

### Layer A: external competence scaffolds

This is the current SkillX layer.
SkillX helps define, refine, compare, and route structured task-class-aware
external support.

### Layer B: internalization substrates

Some of those external artifacts may later be used as scaffolds that are meant
to disappear after post-training or continual-training.

The external artifact is not the final product.
It is the teaching interface.

## Concrete implications for SkillX design

## 1) Skill value should not be measured only by immediate task gain

Today it is natural to ask:

- does this prompt/template improve performance on the task?
- does this rewrite beat the baseline?

SKILL0 suggests a stronger evaluation question:

- does this scaffold help the policy become less dependent on the scaffold over
  time?

That implies a new latent metric family for SkillX:

- **instant utility**
- **transfer utility**
- **internalization utility**

The third metric is the new one.
A skill can be immediately helpful but poor for internalization if it is too
verbose, too entangled, too narrow, or too hard to compress into stable policy.

## 2) The outer-loop object may be broader than "skill content"

SkillX currently focuses on template families, rewrite quality, refine loops,
and class-aware structure.
SKILL0 suggests that the outer loop could also optimize:

- scaffold dosage
- scaffold retirement policy
- class-specific withdrawal schedule
- which skill families should remain external vs be targeted for internalization

In other words, the future outer loop may evolve not only the artifact itself,
but also the policy for how long the artifact should stay in the loop.

## 3) Class-aware structure becomes even more important

If artifacts are ever used for internalization, then loose and mixed natural
language skills become less attractive.
You would prefer artifacts that are:

- compact
- typed
- class-aware
- behaviorally coherent
- verifier-compatible
- easy to ablate or retire in parts

This aligns strongly with the newer SkillX direction around task classes,
template families, and meta-schema / outer-loop structure.

A messy skill may still help at inference time.
A cleanly typed skill is more likely to support both inference-time use and
training-time internalization.

## 4) SkillX should preserve the distinction between augmentation and internalization

A tempting mistake would be to collapse these into one objective.
That would be premature.

SkillX should keep the distinction explicit:

- **augmentation track**: how to help an agent right now using external support
- **internalization track**: how to convert some of that external support into
  policy-level competence

These tracks interact, but they are not identical.
A strong augmentation artifact is not automatically a strong internalization
artifact.

## 5) SkillX may eventually need an ablation-friendly artifact contract

If we ever want to test internalization-oriented hypotheses, SkillX artifacts
should be easier to:

- add/remove by component
- evaluate with vs without support
- compare under shrinking scaffold budgets
- map to task classes and verifier outcomes

This points toward contracts that make decomposition explicit.
The more monolithic the artifact, the harder it is to run helpfulness-driven
withdrawal experiments.

## A useful long-term synthesis

The most promising joint framing is:

- **SkillX** as the system that discovers, structures, rewrites, and evaluates
  external skill artifacts
- **ICRL / Skill0-like training** as the mechanism that internalizes selected
  external artifacts into the policy

In that world, SkillX is not replaced by internalization.
Instead, SkillX becomes the upstream generator of candidate curricula.

That yields a possible future pipeline:

1. generate / evolve task-class-aware scaffold artifacts
2. evaluate them for immediate utility and transfer utility
3. select some artifacts as internalization candidates
4. train with scaffold withdrawal
5. measure which artifacts remain useful externally vs which can be absorbed

This is substantially more interesting than a pure retrieval-only future.

## What I do **not** think these papers prove yet

We should keep some caution.

### 1) They do not prove that all useful skills should be internalized

Some capabilities may be better kept external because they are:

- changing too fast
- expensive to train into weights
- audit-sensitive
- domain- or user-specific

### 2) They do not prove that benchmark zero-skill transfer equals general skill learning

Showing that an agent still performs after scaffold removal is important, but it
is not the same as showing broad abstraction, recomposition, or long-range
transfer.

### 3) They do not eliminate the need for external memory systems

Even if some skills are internalized, we will still need external structures for:

- rare procedures
- user-specific preferences
- fast-moving knowledge
- debuggability and interpretability

For SkillX, this means internalization should be viewed as one destination for
some artifacts, not the only destiny of all artifacts.

## Proposed SkillX research questions triggered by these papers

## RQ1. Internalization utility

Can SkillX define a practical metric for whether a prompt/template/skill artifact
is not only helpful, but also a good candidate for scaffold withdrawal?

## RQ2. Helpfulness-driven retirement

Can the SkillX outer loop learn when a class-specific scaffold should be reduced,
retained, branched, or retired?

## RQ3. Artifact granularity

What decomposition level produces the best tradeoff between immediate utility and
internalization-readiness?

## RQ4. Task-class-specific scaffold schedules

Do different task classes require different withdrawal dynamics?
For example, retrieval-heavy tasks may want a different scaffold-retirement logic
than engineering-composition or methodology-guardrail tasks.

## RQ5. Dual-destination artifacts

Can one SkillX artifact family be explicitly designed with two destinations:

- inference-time external use
- training-time internalization use

## Five concrete takeaways for current SkillX planning

1. **Do not treat SkillX artifacts as inference-only objects.**
   Some should be designed as potential internalization scaffolds.

2. **Add a new evaluation lens: internalization utility.**
   Immediate benchmark gain is not the whole story.

3. **Prefer typed, class-aware, decomposable artifacts.**
   They support both better augmentation and cleaner scaffold withdrawal.

4. **Extend the outer-loop concept.**
   Future outer loops may optimize not only artifact content, but scaffold dosage
   and retirement policy.

5. **Keep augmentation and internalization as separate but linked tracks.**
   SkillX should remain clear about which problem it is solving at each stage.

## Bottom line

ICRL and SKILL0 do not replace the need for SkillX.
They make SkillX more interesting.

They suggest that the artifacts SkillX is learning to produce may eventually be
valuable not only because they help agents **while present in context**, but
also because they can help agents **graduate beyond needing them**.
