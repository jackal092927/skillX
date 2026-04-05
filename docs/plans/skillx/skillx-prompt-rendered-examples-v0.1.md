# SkillX Prompt Rendered Examples v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-03
- **Role:** concrete two-category rendering examples for the current prompt-bank MVP
- **Status:** explanatory working example

---

## 1. Why this document exists

This note gives two concrete examples of the current SkillX prompt-bank design.

It is meant to answer four confusions directly:

1. What is `p_k`?
2. Is `p_k` just a category name?
3. How does `p_k` become the actual prompt used by the inner loop?
4. What is the difference between:
   - the category label,
   - the Meta schema,
   - the Rendered Meta skill,
   - and the task-specific skill object (what Xin referred to in conversation as “SkillKit”)?

---

## 2. The four layers

## 2.1 Category label

This is only a short identifier, e.g.:
- `artifact-generation`
- `engineering-composition`

It is **not** the prompt.

## 2.2 Meta schema `p_k`

This is the category-level **meta-protocol object**.

So yes:

> **`p_k` is our category-level meta-protocol object.**

But it is not only a string label.
It is a structured object with fields like:
- `category_id`
- `semantic_intent`
- `emphasize`
- `avoid`
- `expected_good_fit`
- `expected_bad_fit`
- `meta_prompt_seed`

## 2.3 Rendered Meta skill

This is the actual prompt injected into the Skill Writer in the inner loop.

It is already task-specific, because it contains task context, the current Task skill, and optional evidence.

Conceptually:

```text
Rendered Meta skill = Render(Meta schema, task, current Task skill, evidence)
```

The Rendered Meta skill is built from:
- a common wrapper,
- the category-level meta-protocol object `p_k`,
- the task context,
- the current task-specific skill,
- and optional run evidence.

## 2.4 Task-specific skill object (“SkillKit”, if we use that name)

This is the thing being rewritten and later executed on the task.

In this note, I will use the more explicit name:

> **task-specific skill object**

because `SkillKit` is not yet a frozen formal term in the project docs.

This task-specific skill object is:
- local to one task,
- the object that the inner loop edits,
- and the object later executed/evaluated.

---

## 3. Important clarification about `R0`

Xin asked whether the first Rendered Meta skill is basically the same thing as the experiment’s old `R0` prompt.

The answer is:

> **Not exactly.**

In the earlier refine protocol, `R0` meant:

> the **input skill** before refinement

not the instruction prompt used to refine it.

So, under the older refine notation:
- `R0` = input task-specific skill object
- `Render(Meta schema, task, R0, evidence)` = the Rendered Meta skill sent to the Skill Writer
- the first revised output produced under that Rendered Meta skill is closer to `R1`, not `R0`

So the first Rendered Meta skill is **the prompt that operates on `R0`**, not `R0` itself.

---

## 4. Rendering template used in these examples

For both examples below, use the same rendering skeleton:

```text
Rendered Meta skill =
  common_wrapper
  + meta_schema_block(p_k)
  + task_context_block(task)
  + current_skill_block
  + evidence_block
  + output_contract_block
```

### 4.1 Common wrapper

The common wrapper says:
- you are revising a task-specific skill,
- not solving the task directly,
- your job is to improve the skill under a category-level meta-protocol,
- return a revised skill plus a concise structured summary of changes.

### 4.2 Evidence block in the first render

For these examples, the evidence block is empty / initial:
- no prior score yet
- no prior failure summary yet
- no borderline competitor prompt yet

So these are **first-render examples**.

---

## 5. Example A — `artifact-generation`

## 5.1 Chosen category

```text
p_A = artifact-generation
```

## 5.2 Representative task

```text
task = offer-letter-generator
```

Task summary from local SkillsBench task file:
- fill placeholders in `offer_letter_template.docx`
- use `employee_data.json` as source truth
- handle the relocation conditional section correctly
- save final result to `/root/offer_letter_filled.docx`

## 5.3 The Meta schema `p_A`

Condensed from the current prompt bank:

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
meta_prompt_seed: |
  Optimize the skill for exactness of the final artifact, not breadth of procedure.
  Keep the skill lean.
  Only introduce stages or tools when clearly necessary.
  Do not guess missing values.
```

## 5.4 Example current task-specific skill object (`R0` / input skill)

For illustration, assume the current skill object is:

```text
1. Open the Word template.
2. Read employee_data.json.
3. Replace placeholders with values from the JSON.
4. If relocation package is enabled, keep the relocation section.
5. Save the file.
```

This is a plausible but underspecified starting skill:
- it says what to do,
- but it does not strongly enforce no-invention,
- exact placeholder handling,
- or a final contract check.

## 5.5 First Rendered Meta skill

```text
You are revising a task-specific skill.
Do NOT solve the task directly.
Your job is to improve the current skill under the given category-level meta-protocol.
Return a revised skill and a concise structured change summary.

[CATEGORY META-PROTOCOL]
Category: artifact-generation
Semantic intent: Produce a constrained artifact that must exactly satisfy an output contract.

Emphasize:
- exact output schema / format / placement requirements
- preservation constraints and no-invention discipline
- missing-input detection before finalization
- short final reviewer pass against explicit contract items

Avoid:
- unnecessary multi-stage scaffolding
- speculative filling of unknown fields
- tool usage that is not required by the artifact contract

Expected good fit:
- form filling
- formatting / conversion with strict output expectations
- single-artifact generation or transformation

Expected bad fit:
- benchmark-gated code repair
- control/simulation loops
- deep retrieval-heavy synthesis

Seed instruction:
Optimize the skill for exactness of the final artifact, not breadth of procedure.
Keep the skill lean.
Only introduce stages or tools when clearly necessary.
Do not guess missing values.

[TASK CONTEXT]
Task: offer-letter-generator
Task summary:
- Fill placeholders in a Word template using employee_data.json.
- Handle the conditional relocation section correctly.
- Save the final output to /root/offer_letter_filled.docx.

[CURRENT TASK-SPECIFIC SKILL]
1. Open the Word template.
2. Read employee_data.json.
3. Replace placeholders with values from the JSON.
4. If relocation package is enabled, keep the relocation section.
5. Save the file.

[EVIDENCE]
No prior run evidence yet. This is the initial category-conditioned rewrite.

[OUTPUT CONTRACT]
Return YAML with the following fields:
revised_skill: |
  ...
change_summary:
  keep:
    - ...
  add:
    - ...
  remove:
    - ...
  sharpen:
    - ...
rationale: |
  ...
```

## 5.6 What this prompt is trying to induce

This Rendered Meta skill should push the Skill Writer toward:
- adding explicit no-invention rules
- clarifying that placeholder replacement must follow source truth exactly
- handling the relocation conditional as a formal contract rule
- adding a final verification checklist
- *not* turning the task into a big multi-stage workflow

So the core rewrite prior is:

> **make the skill more exact and contract-aware, not more elaborate**

---

## 6. Example B — `engineering-composition`

## 6.1 Chosen category

```text
p_B = engineering-composition
```

## 6.2 Representative task

```text
task = parallel-tfidf-search
```

Task summary from local SkillsBench task file:
- parallelize a single-thread TF-IDF search engine in Python
- implement required functions in `/root/workspace/parallel_solution.py`
- maintain identical search results
- hit speedup targets for indexing and searching

## 6.3 The Meta schema `p_B`

Condensed from the current prompt bank:

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
meta_prompt_seed: |
  Optimize the skill as a disciplined execution bundle, not as a generic writing prompt.
  Favor diagnose-before-edit, explicit interfaces, ordered patching, and benchmark-aware verification.
```

## 6.4 Example current task-specific skill object (`R0` / input skill)

For illustration, assume the current skill object is:

```text
1. Read the existing sequential implementation.
2. Write a parallel version.
3. Make sure the functions return the same type of outputs.
4. Try to improve speed.
5. Save the file.
```

This starting skill is also plausible but too weak:
- it lacks an explicit diagnose-before-edit step
- it does not define verification sequence
- it does not foreground benchmark gates
- it does not warn about preserving exact output equivalence

## 6.5 First Rendered Meta skill

```text
You are revising a task-specific skill.
Do NOT solve the task directly.
Your job is to improve the current skill under the given category-level meta-protocol.
Return a revised skill and a concise structured change summary.

[CATEGORY META-PROTOCOL]
Category: engineering-composition
Semantic intent: Compose diagnosis, editing, execution, and verification into a disciplined engineering workflow.

Emphasize:
- diagnose -> patch/edit -> verify sequencing
- tool wrappers / execution interfaces / reproducible commands
- explicit precedence and dependency handling
- benchmark / build / test gate awareness

Avoid:
- vague reviewer-only advice without execution discipline
- unordered bundles of suggestions
- generic prose that does not tell the agent how to validate changes

Expected good fit:
- build fixes
- migrations
- code implementation tasks with compile/test/benchmark constraints

Expected bad fit:
- pure retrieval/synthesis
- simple output formatting tasks

Seed instruction:
Optimize the skill as a disciplined execution bundle, not as a generic writing prompt.
Favor diagnose-before-edit, explicit interfaces, ordered patching, and benchmark-aware verification.

[TASK CONTEXT]
Task: parallel-tfidf-search
Task summary:
- Parallelize a single-thread TF-IDF search engine in Python.
- Implement required functions in /root/workspace/parallel_solution.py.
- Preserve identical search results.
- Achieve speedup targets for indexing and searching.

[CURRENT TASK-SPECIFIC SKILL]
1. Read the existing sequential implementation.
2. Write a parallel version.
3. Make sure the functions return the same type of outputs.
4. Try to improve speed.
5. Save the file.

[EVIDENCE]
No prior run evidence yet. This is the initial category-conditioned rewrite.

[OUTPUT CONTRACT]
Return YAML with the following fields:
revised_skill: |
  ...
change_summary:
  keep:
    - ...
  add:
    - ...
  remove:
    - ...
  sharpen:
    - ...
rationale: |
  ...
```

## 6.6 What this prompt is trying to induce

This Rendered Meta skill should push the Skill Writer toward:
- explicitly diagnosing the sequential implementation before patching
- separating correctness-preservation from speed optimization
- making validation concrete (same outputs, benchmark targets, worker settings, comparison protocol)
- ensuring edit order and verification order are explicit
- *not* drifting into broad prose guidance

So the core rewrite prior is:

> **make the skill more execution-disciplined and benchmark-aware, not just more detailed**

---

## 7. Compare the two examples

These two prompts are different in a much deeper way than label choice.

## 7.1 Different optimization objective

- `artifact-generation`
  - optimize exact output contract
- `engineering-composition`
  - optimize diagnose→edit→verify engineering discipline

## 7.2 Different primary failure suspicion

- `artifact-generation`
  - likely failure = placeholder invention, missing-input guessing, format drift
- `engineering-composition`
  - likely failure = wrong edit order, weak verification, interface ambiguity, benchmark miss

## 7.3 Different anti-goal

- `artifact-generation`
  - avoid over-scaffolding
- `engineering-composition`
  - avoid vague reviewer-only guidance without execution discipline

## 7.4 Different result on the rewritten skill

Even if the two starting skills were equally weak, the two runtime prompts would push the Skill Writer to produce very different revised skills.

That is the point of having separate `p_k`.

---

## 8. Is the first Rendered Meta skill the experiment’s `R0` prompt?

Short answer:

> **No. It is the prompt that operates on `R0`, not `R0` itself.**

Under the old refine notation:
- `R0` = input task-specific skill object
- Rendered Meta skill = the instruction used to rewrite `R0`
- output after applying the Rendered Meta skill = the first revised candidate, closer to `R1`

So the first rendered runtime prompt is more like:

```text
WriterPrompt_0(task, p_k, R0, evidence_0)
```

not:

```text
R0
```

---

## 9. What is the difference between the Rendered Meta skill and the task-specific skill object (“SkillKit”)?

If we use Xin’s informal phrase “SkillKit” to mean the current task-specific skill bundle / skill text, then:

## 9.1 Task-specific skill object (“SkillKit”)

This is:
- the thing being edited
- task-local
- executable / evaluable on the task
- the object that becomes `R0`, `R1`, `R2`, ... across refine rounds

## 9.2 Rendered Meta skill

This is:
- the instruction given to the Skill Writer
- category-conditioned by the Meta schema `p_k`
- not executed on the benchmark directly
- used to transform the current task-specific skill object into a better one

## 9.3 `p_k`

This is:
- the category-level Meta schema
- more stable than any one task-specific skill
- part of the outer-loop bank
- what gets assigned / updated cluster-wise across tasks

So the relationship is:

```text
p_k (category-level Meta schema)
  -> rendered into a task-specific Meta skill
  -> applied by the Skill Writer to revise the current task-specific skill object
  -> produce next candidate skill
  -> candidate skill is executed/evaluated on the task
```

---

## 10. Bottom line

The cleanest interpretation is:

- **category label** = short name only
- **`p_k`** = category-level Meta schema
- **Rendered Meta skill** = task-specific editing prompt built from Meta schema + task context + current skill + evidence
- **task-specific skill object** = the local skill being revised/executed (`R0`, `R1`, `R2`, ...)

So yes, I have now shown two concrete `p_k` examples and how they render into two visibly different task-specific Meta skills.
The next natural step would be to freeze one concrete rendering template and render all `K` bank entries through the exact same wrapper so the differences are fully comparable.
