# SkillX Prompt Rendering and Injection Spec v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-03
- **Role:** defines what a category-level Meta schema actually is, how its content is constructed, how schema distinctness is judged, and how it is rendered into a task-specific Meta skill for Mark Auto Research
- **Status:** working MVP spec

---

## 1. Why this document exists

The current SkillX prompt-bank design already defines **seed Meta schemas** for each category.

However, several layers were getting conflated:

1. **category label**
2. **category-level Meta schema**
3. **Render** (the frozen packaging logic)
4. **Rendered Meta skill** (the task-specific prompt injected into the Skill Writer)
5. **Task skill** (the task-specific skill object being edited/executed)

This document separates those layers.

It also answers two important questions:

1. **How do we determine what each Meta schema should contain?**
2. **How do we make different Meta schemas genuinely distinct, rather than just differently named?**

---

## 2. Terminology

## 2.1 Category label

A category label is only a short identifier, e.g.:
- `artifact-generation`
- `analytic-pipeline`
- `engineering-composition`

A label is **not** the prompt.

## 2.2 Meta schema

A Meta schema is the reusable class-level guidance object stored in the prompt bank.

We write the prompt bank as:

```text
P = {p_1, p_2, ..., p_K}
```

Each `p_k` is **not just a name**.
It is a structured Meta schema containing:
- the category id
- the semantic intent
- what to emphasize
- what to avoid
- what tasks it is expected to fit / not fit
- and a seed natural-language guidance block

## 2.3 Render

Render is the fixed packaging logic that combines:
- the Meta schema,
- the current task,
- the current task skill,
- and optional evidence / feedback

into the final prompt seen by the Skill Writer.

For the MVP, Render should be treated as **frozen infrastructure**, not the main outer-loop optimization object.

## 2.4 Rendered Meta skill

A Rendered Meta skill is the actual prompt sent to the Skill Writer inside Mark Auto Research.

It is task-specific because it already contains the current task, current task skill, and optional evidence.

Conceptually, it is produced by:

```text
Rendered Meta skill = Render(Meta schema, task, current task skill, evidence)
```

## 2.5 Task skill

The Task skill is the task-specific skill object being edited and later executed / evaluated.

So:
- **label** != **Meta schema** != **Rendered Meta skill** != **Task skill**

---

## 3. What a Meta schema `p_k` is

For the MVP, each `p_k` should be treated as this object:

```yaml
category_id: string
version: string
semantic_intent: string
emphasize:
  - string
avoid:
  - string
expected_good_fit:
  - string
expected_bad_fit:
  - string
hypothesized_primary_failure_modes:
  - string
seed_rationale: string
meta_prompt_seed: |
  ...
```

### Field meanings

- `category_id`
  - short label only
- `version`
  - schema version for updates across loops
- `semantic_intent`
  - one-sentence statement of what kind of task this prompt is for
- `emphasize`
  - what the Skill Writer should bias toward
- `avoid`
  - what the Skill Writer should actively not overdo
- `expected_good_fit`
  - examples of task families likely to benefit from this prompt
- `expected_bad_fit`
  - examples of task families likely to be mismatched
- `hypothesized_primary_failure_modes`
  - current guess about what typically goes wrong for this class
- `seed_rationale`
  - why this prompt was constructed this way
- `meta_prompt_seed`
  - the natural-language core guidance block later packaged into a Rendered Meta skill

---

## 4. How we determine the initial content of each `p_k`

The initial prompt-bank entries are **seed Meta schemas**, not final truths.

They are currently constructed from four evidence sources.

## 4.1 Evidence source A — task-class annotation pass

We annotated all `89` SkillsBench tasks with first-pass fields such as:
- `task_object`
- `workflow_topology`
- `tool_surface_regime`
- `verifier_mode`
- `primary_pattern`
- `secondary_patterns`

This gave the initial flat class surface.

That surface answers:
- what broad kinds of tasks exist,
- and which tasks appear to belong to the same coarse class.

But this alone does **not** determine the final task-specific rendered prompt.

## 4.2 Evidence source B — representative seed tasks

For each class, we picked representative tasks and read their instructions / constraints.

Those representative tasks help identify:
- what sort of mistakes are dangerous,
- what kind of workflow the class wants,
- what kind of over-scaffolding hurts,
- and what the Skill Writer should be taught to do first.

This is the main source of the current `emphasize` / `avoid` content.

## 4.3 Evidence source C — second-pass failure / rewrite hypotheses

We also seeded second-pass overlay fields such as:
- `risk_profile`
- `dominant_failure_mode`
- `rewrite_response_hypothesis`

Even though those are not part of the flat clustering object, they are useful for prompt construction.

They help answer:
- does this class usually need stronger reviewer logic?
- stronger stage contracts?
- stronger abstention?
- clearer bundle interfaces?
- less scaffolding?

This is the main source of the current prompt **biases**.

## 4.4 Evidence source D — external design priors

We also used prior conceptual work from:
- Anthropic’s skill-creator line
- Google / ADK five-pattern lens
- the current SkillX / REP / MARC / MetaSkill design memos

These priors do **not** determine the final categories.
But they help articulate reusable distinctions such as:
- generator vs reviewer bias
- pipeline vs wrapper bias
- abstention / fit-check bias
- discipline around evidence and handoffs

---

## 5. Current construction rule for seed prompts

The current seed schema construction rule is:

> For each high-level category, identify the most reusable **rewrite prior** that should help a class of tasks, then encode that prior as a structured Meta schema.

The important phrase is:

> **rewrite prior**

This means each `p_k` is not a task description.
It is a hypothesis about:
- what kind of guidance tends to help tasks of that class,
- and what kind of guidance tends to hurt or distract.

So different `p_k` are distinguished by their **biases about how to rewrite a skill**, not just by the nouns in their labels.

---

## 6. How prompt distinctness is currently enforced

A Meta schema should only survive if it has a clearly different answer to at least some of the following questions.

## 6.1 Distinctness dimensions

For each `p_k`, ask:

1. **Primary optimization objective**
   - What should the rewritten skill optimize first?
   - e.g. exact artifact contract, stage integrity, execution discipline, evidence grounding, control loop validity, abstention, orchestration order

2. **Default workflow bias**
   - Should the prompt push toward:
     - lean one-shot execution,
     - stage decomposition,
     - diagnose→patch→verify,
     - retrieval→compress→answer,
     - control-loop feedback,
     - fit-check / abstention,
     - or ordering / delegation?

3. **Primary suspected failure mode**
   - What does this prompt assume is most likely going wrong?
   - e.g. placeholder invention, stage-handoff break, precedence conflict, evidence loss, premature commitment

4. **Anti-goal**
   - What kind of over-optimization should this prompt explicitly resist?
   - e.g. too much scaffolding, too much textual synthesis, too much eagerness, too little verification

5. **Expected good-fit / bad-fit boundary**
   - What kinds of tasks should this prompt probably win on?
   - What kinds of tasks should it probably lose on?

If two prompts answer these almost identically, they are probably not distinct enough and should be merged.

---

## 7. Current seed prompt differences by category

Below is the intended difference in **rewrite prior**, not just in name.

## 7.1 `artifact-generation`

### Primary rewrite prior
Make the skill more exact, contract-aware, and no-invention disciplined.

### Primary failure suspicion
The skill is too loose about output contract, formatting, or missing inputs.

### Anti-goal
Do **not** turn a constrained artifact task into an over-scaffolded multi-stage workflow.

### Distinctive signature
- favors exactness over breadth
- favors short reviewer pass over large orchestration
- strongly penalizes hallucinated filling

---

## 7.2 `analytic-pipeline`

### Primary rewrite prior
Make the skill more stage-structured and handoff-safe.

### Primary failure suspicion
The skill is losing correctness between extraction / transform / analysis / reporting stages.

### Anti-goal
Do **not** compress a fragile pipeline into vague prose or one giant step.

### Distinctive signature
- favors explicit stage boundaries
- favors intermediate artifacts / checks
- assumes stage-handoff weakness before generic reasoning weakness

---

## 7.3 `engineering-composition`

### Primary rewrite prior
Make the skill more execution-disciplined and verification-aware.

### Primary failure suspicion
The skill lacks diagnose→edit→verify order, interface clarity, or benchmark-gated discipline.

### Anti-goal
Do **not** over-expand into generic synthesis or reviewer-only prose when execution structure is the real bottleneck.

### Distinctive signature
- favors explicit wrappers / commands / execution interfaces
- favors precedence and dependency clarity
- favors compile/test/benchmark gates

---

## 7.4 `retrieval-heavy-synthesis`

### Primary rewrite prior
Make the skill more evidence-grounded and less hallucination-prone.

### Primary failure suspicion
The skill retrieves poorly, compresses evidence badly, or answers beyond support.

### Anti-goal
Do **not** bury the task in workflow scaffolding that obscures evidence tracking.

### Distinctive signature
- favors retrieval plan
- favors provenance and evidence retention
- favors explicit abstain/unknown behavior when support is weak

---

## 7.5 `environment-control`

### Primary rewrite prior
Make the skill more loop-aware around state, action, parameter, and metric feedback.

### Primary failure suspicion
The skill is treating an environment-facing task too textually and not closing the control/evaluation loop.

### Anti-goal
Do **not** reframe a control/planning problem as generic analysis or artifact writing.

### Distinctive signature
- favors modeling state/action/parameter space
- favors evaluate-and-adjust structure
- favors metric-validity checks after candidate actions or plans

---

## 7.6 `methodology-guardrail`

### Primary rewrite prior
Make the skill more judgmental, abstention-capable, and fit-check-aware.

### Primary failure suspicion
The skill is committing too early, forcing a method onto the wrong case, or answering beyond what the rules justify.

### Anti-goal
Do **not** over-proceduralize if the real need is reviewer-style judgment and refusal discipline.

### Distinctive signature
- favors fit-check before action
- favors abstain / unknown behavior
- favors reviewer-style rule comparison
- explicitly resists premature commitment

---

## 7.7 `orchestration-delegation`

### Primary rewrite prior
Make the skill more order-sensitive, dependency-aware, and handoff-safe across substeps or systems.

### Primary failure suspicion
The skill is doing the right things in the wrong order, or triggering side effects before constraints are extracted.

### Anti-goal
Do **not** collapse coordination problems into generic reasoning or reviewer-only prompts.

### Distinctive signature
- favors constraint extraction before action
- favors correct dependency ordering
- favors explicit state handoff between stages/tools
- favors side-effect awareness

---

## 8. Prompt distinctness acceptance test

Before a prompt bank is considered usable, run this acceptance test.

For every pair `(p_i, p_j)`:

### 8.1 Pairwise checklist

Ask:
- Do these prompts have different primary optimization objectives?
- Do they suspect different failure modes first?
- Do they discourage different anti-patterns?
- Do they imply different update actions on the Skill Writer?
- Would they likely choose different tasks as good-fit / bad-fit examples?

### 8.2 Practical acceptance rule

A pair should only survive as separate prompts if at least **two or three** of the above differences are substantial.

If not, merge them.

### 8.3 Early merge candidate

The strongest current merge candidate remains:
- `methodology-guardrail`
- `orchestration-delegation`

because they can drift toward similar “be careful / don’t act too early” wording unless deliberately sharpened.

---

## 9. From Meta schema to Rendered Meta skill

The Rendered Meta skill should not be just `meta_prompt_seed` pasted raw.

Instead, it is produced by a frozen Render template.

## 9.1 Render template

Conceptually:

```text
Rendered Meta skill =
  common_wrapper
  + meta_schema_block(p_k)
  + task_context_block(task)
  + current_task_skill_block
  + evidence_block(evidence)
  + output_contract_block
```

### 9.2 Common wrapper

This tells the Skill Writer:
- you are revising a skill, not solving the task directly
- your goal is to improve the Task skill under the current Meta schema
- return a structured revised skill artifact and concise change rationale

### 9.3 Meta schema block

This comes from `p_k` and includes:
- semantic intent
- emphasize
- avoid
- expected good fit / bad fit
- meta_prompt_seed

This is the main place where different categories diverge and the main outer-loop optimization target for the MVP.

### 9.4 Task context block

This should include:
- task name
- compact task description / contract
- any relevant task-local constraints

### 9.5 Current Task skill block

This should include the current task-specific skill text being revised.

### 9.6 Evidence block

This should include, when available:
- previous score(s)
- failure summary
- borderline competitor prompt
- ambiguity note
- known failure family

### 9.7 Output contract block

This should force the Skill Writer to return something structured, e.g.:

```yaml
revised_skill: string
change_summary:
  keep:
    - string
  add:
    - string
  remove:
    - string
  sharpen:
    - string
rationale: string
```

---

## 10. Injection point in Mark Auto Research

The current intended injection point is:

> **the Skill Writer / insight loop**, not the whole runtime shell.

That means the Rendered Meta skill should condition:
- how the skill is rewritten,
- what kinds of revisions are prioritized,
- and what kinds of mistakes are assumed likely.

It should **not** directly replace:
- the task statement,
- the evaluator,
- or the runtime sandbox policy.

---

## 11. What is already defined vs not yet finished

## 11.1 Already defined

We already have seed versions of `p_k` as Meta schemas with:
- category_id
- semantic_intent
- emphasize
- avoid
- expected_good_fit
- expected_bad_fit
- meta_prompt_seed

in:
- `docs/plans/skillx/skillx-prompt-bank-v0.1.md`
- `docs/plans/skillx/skillx-prompt-bank-v0.1.json`

## 11.2 Not yet fully frozen

The following layer is still to be finalized:
- the exact injection implementation inside the runner

For MVP, the intended simplification is:
- optimize the Meta schema
- freeze Render as much as possible

The frozen Render template is now specified in:
- `docs/plans/skillx/skillx-render-template-frozen-v0.1.md`

So the seed schema bank exists and the MVP Render layer is now frozen at the spec level; what remains is wiring it into the runner.

---

## 12. Immediate next step

After this clarification, the next concrete move should be:

1. freeze the runtime rendering template
2. define the output contract for the Skill Writer
3. generate one rendered runtime prompt per category for a representative task
4. inspect whether the category differences remain clearly visible after rendering

That step is what will turn the current seed prompt objects into fully execution-ready prompt payloads.

Concrete worked examples now exist in:
- `docs/plans/skillx/skillx-prompt-rendered-examples-v0.1.md`
