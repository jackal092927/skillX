# SkillX Prompt Bank v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-03
- **Role:** initial category-level Meta schema bank for prompt-induced clustering MVP
- **Status:** working seed bank

---

## 1. Purpose

This document defines the initial `K = 6–7` category-level **Meta schemas** used by the SkillX prompt-induced clustering loop.

Clarification:
- category name != Meta schema != Rendered Meta skill
- the layer separation and rendering path are now specified in:
  - `docs/plans/skillx/skillx-prompt-rendering-and-injection-spec-v0.1.md`

The bank is intentionally small.
Each category is worth keeping only if its Meta schema implies meaningfully different guidance for the Skill Writer.

This bank is the object that will be:
- applied across tasks,
- used for assignment,
- updated cluster-wise,
- and re-applied in later loops.

---

## 2. Bank-wide rules

## 2.1 Distinctness rule

A category prompt is valid only if it differs from the others in at least one of these ways:
- what it tells the Skill Writer to emphasize,
- what it tells the Skill Writer to avoid,
- what failure mode it treats as primary,
- what kind of workflow skeleton it prefers,
- or what kind of task it is expected to fit / not fit.

If two prompts collapse to the same operational guidance, merge them.

## 2.2 Common output contract for every prompt

Every category prompt should be written in the same structured format:

```yaml
category_id: string
semantic_intent: string
emphasize:
  - string
avoid:
  - string
expected_good_fit:
  - string
expected_bad_fit:
  - string
meta_prompt: |
  ...
```

## 2.3 Mark Auto Research assumption

All prompts below assume the task-local inner loop is executed through the current Pi-Auto-Research-derived system, referred to by Xin as **Mark Auto Research**.

The prompt therefore conditions the **Skill Writer / insight loop**, not the whole runtime.

---

## 3. Initial prompt bank

## 3.1 `artifact-generation`

```yaml
category_id: artifact-generation
semantic_intent: Produce a constrained artifact that must exactly satisfy an output contract.
emphasize:
  - exact output schema / format / placement requirements
  - preservation constraints and no-invention discipline
  - missing-input detection before finalization
  - short final reviewer pass against explicit contract items
avoid:
  - unnecessary multi-stage scaffolding
  - speculative filling of unknown fields
  - tool usage that is not required by the artifact contract
expected_good_fit:
  - form filling
  - formatting / conversion with strict output expectations
  - single-artifact generation or transformation
expected_bad_fit:
  - benchmark-gated code repair
  - control/simulation loops
  - deep retrieval-heavy synthesis
meta_prompt: |
  You are revising a skill for an artifact-generation task.
  Optimize the skill for exactness of the final artifact, not breadth of procedure.

  Prioritize:
  1. explicit statement of the required output artifact and allowed transformations,
  2. no-invention / do-not-guess rules for missing or ambiguous inputs,
  3. preservation of formatting, structure, or source truth where required,
  4. a short final verification checklist before producing the final artifact.

  Keep the skill lean.
  Only introduce stages, tools, or wrappers when they are clearly necessary for meeting the artifact contract.

  Do not turn the skill into a generic multi-stage workflow if the task is fundamentally a constrained artifact-writing problem.
```

---

## 3.2 `analytic-pipeline`

```yaml
category_id: analytic-pipeline
semantic_intent: Run an ordered analysis pipeline where intermediate processing quality strongly affects final correctness.
emphasize:
  - stage decomposition and stage ordering
  - explicit intermediate artifacts / checkpoints
  - handoff integrity between stages
  - final output tied back to pipeline evidence
avoid:
  - collapsing multiple sensitive transforms into one vague step
  - skipping intermediate validation
  - overly generic prose-only guidance
expected_good_fit:
  - scientific / signal / video / security analysis workflows
  - ordered transformation + measurement tasks
expected_bad_fit:
  - simple one-shot artifact tasks
  - pure code patch / compile-test loops
meta_prompt: |
  You are revising a skill for an analytic-pipeline task.
  Optimize the skill as a staged workflow whose correctness depends on preserving structure between stages.

  Prioritize:
  1. stage-by-stage decomposition,
  2. explicit intermediate artifacts or checks when a later step depends on earlier processing quality,
  3. clear handoff rules between extraction, transformation, analysis, and final reporting,
  4. a final output step that summarizes the pipeline result without dropping critical constraints.

  Strengthen stage contracts before adding more generic scaffolding.
  If the task is failing, assume stage-handoff weakness before assuming the task needs more general instructions.
```

---

## 3.3 `engineering-composition`

```yaml
category_id: engineering-composition
semantic_intent: Compose diagnosis, editing, execution, and verification into a disciplined engineering workflow.
emphasize:
  - diagnose -> patch/edit -> verify sequencing
  - tool wrappers / execution interfaces / reproducible commands
  - explicit precedence and dependency handling
  - benchmark / build / test gate awareness
avoid:
  - vague reviewer-only advice without execution discipline
  - unordered bundles of suggestions
  - generic prose that does not tell the agent how to validate changes
expected_good_fit:
  - build fixes
  - migrations
  - code implementation tasks with compile/test/benchmark constraints
expected_bad_fit:
  - pure retrieval/synthesis
  - simple output formatting tasks
meta_prompt: |
  You are revising a skill for an engineering-composition task.
  Optimize the skill as a disciplined execution bundle, not as a generic writing prompt.

  Prioritize:
  1. diagnose-before-edit behavior,
  2. explicit tool / command / wrapper interfaces where execution matters,
  3. ordered patching with dependency awareness,
  4. verification gates such as compile, test, or benchmark checks.

  If the task fails, first ask whether the skill lacks:
  - clear execution order,
  - explicit interfaces,
  - or a strong verify step.

  Do not over-expand into broad research or synthesis unless the task truly requires it.
```

---

## 3.4 `retrieval-heavy-synthesis`

```yaml
category_id: retrieval-heavy-synthesis
semantic_intent: Gather evidence from sources, compress it correctly, and synthesize an output without dropping support.
emphasize:
  - retrieval plan and source grounding
  - evidence tracking / provenance discipline
  - compression without support loss
  - abstain / unknown behavior when evidence is insufficient
avoid:
  - unsupported synthesis
  - hallucinated joins across sources
  - excessive workflow scaffolding that obscures evidence use
expected_good_fit:
  - information search
  - handbook / database grounded QA
  - report or answer generation from external sources
expected_bad_fit:
  - simulator/control tasks
  - code patch workflows
meta_prompt: |
  You are revising a skill for a retrieval-heavy synthesis task.
  Optimize the skill for evidence-grounded synthesis rather than free-form completion.

  Prioritize:
  1. retrieving the right evidence before answering,
  2. keeping track of what each source supports,
  3. compressing evidence into the final answer without dropping required support,
  4. explicit unknown / abstain behavior when the evidence does not justify completion.

  If the task is failing, suspect evidence-loss or unsupported synthesis before adding more procedural bulk.
```

---

## 3.5 `environment-control`

```yaml
category_id: environment-control
semantic_intent: Interact with a simulator, planner, or dynamic environment under explicit metric or validity constraints.
emphasize:
  - world / simulator / environment state understanding
  - explicit control or planning loop structure
  - parameter, policy, or plan validation
  - metric-facing evaluation after execution
avoid:
  - overly textual synthesis behavior
  - weak feedback loops between action and evaluation
  - artifact-first thinking when the task is really environment-facing
expected_good_fit:
  - control design
  - planning with validity constraints
  - simulator-driven evaluation tasks
expected_bad_fit:
  - document formatting / artifact generation
  - pure evidence synthesis tasks
meta_prompt: |
  You are revising a skill for an environment-control task.
  Optimize the skill around interacting with a planner, simulator, or controlled environment under explicit validity or metric constraints.

  Prioritize:
  1. clear modeling of state, parameters, or action space,
  2. an execution loop that includes evaluate-and-adjust behavior,
  3. explicit metric / validity checks after candidate actions or plans,
  4. concise recording of outputs needed by the evaluator.

  If the task is failing, first strengthen control-loop structure and metric feedback before adding generic analysis scaffolding.
```

---

## 3.6 `methodology-guardrail`

```yaml
category_id: methodology-guardrail
semantic_intent: Prevent premature or unsafe completion by enforcing fit-checks, abstention, and rule-aware judgment.
emphasize:
  - fit-check before commitment
  - abstention / unknown / needs-clarification behavior
  - rule hierarchy and anti-hallucination discipline
  - reviewer-style judgment over direct eager generation
avoid:
  - premature completion
  - overconfident synthesis when the task is underdetermined
  - unnecessary multi-stage pipeline expansion
expected_good_fit:
  - taxonomy merge / fit-check tasks
  - citation / rule / policy screening tasks
  - abstention-sensitive validation tasks
expected_bad_fit:
  - straightforward artifact generation
  - benchmark-driven engineering loops
meta_prompt: |
  You are revising a skill for a methodology-heavy guardrail task.
  Optimize the skill for disciplined judgment, fit-checking, and safe refusal when needed.

  Prioritize:
  1. checking whether the task instance actually fits the intended method,
  2. explicit abstain / unknown / request-clarification behavior,
  3. reviewer-style comparison against criteria or rules,
  4. preventing premature commitment to a single answer path.

  If the task is failing, prefer stronger judgment discipline over adding more execution scaffolding.
```

---

## 3.7 `orchestration-delegation`

```yaml
category_id: orchestration-delegation
semantic_intent: Coordinate ordered external actions or substeps where sequence and dependency management matter.
emphasize:
  - constraint extraction before action
  - ordering across dependent steps / systems
  - state handoff between stages or tools
  - fail-safe finalization and side-effect awareness
avoid:
  - eager direct completion without dependency checks
  - reviewer-only prompts that lack execution choreography
  - over-abstract synthesis that ignores operational order
expected_good_fit:
  - scheduling / delegation workflows
  - multi-system action coordination
  - tasks where one substep creates constraints for the next
expected_bad_fit:
  - static artifact-only tasks
  - deep scientific analysis pipelines
meta_prompt: |
  You are revising a skill for an orchestration/delegation task.
  Optimize the skill as a coordination protocol, not just as a content-generation prompt.

  Prioritize:
  1. extracting constraints before taking actions,
  2. preserving correct action order across dependent systems or stages,
  3. making state handoffs explicit,
  4. preventing side effects from happening before prerequisites are checked.

  If the task is failing, first strengthen dependency ordering and handoff logic before adding more general reasoning guidance.
```

---

## 4. Merge pressure note

The most likely early merge candidate is:
- `methodology-guardrail`
- `orchestration-delegation`

If early experiments show that their prompts converge or assignments remain weakly separable, merge them into a single category rather than forcing a seven-way bank.

---

## 5. Immediate next use

This bank is intended to feed:
- `skillx-assignment-matrix-protocol-v0.1.md`
- `skillx-outer-loop-update-protocol-v0.1.md`
- `skillx-pilot-assignment-pass-v0.1.md`

Machine-readable companion artifact:
- `skillx-prompt-bank-v0.1.json`

The next experiment should use this bank to produce the first task × prompt score matrix under a fixed Mark Auto Research inner-loop budget.
