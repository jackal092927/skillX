# SkillX Render Template (Frozen) v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-03
- **Role:** frozen MVP Render template for turning a Meta schema into a task-specific Meta skill
- **Status:** working MVP frozen-spec

---

## 1. Purpose

This document freezes the MVP Render layer.

In the current SkillX design:
- **Meta schema** is the reusable class-level guidance optimized by the Outer Loop
- **Render** is the frozen packaging logic
- **Meta skill** is the final task-specific prompt seen by the inner loop
- **Task skill** is the task-specific skill object being edited and later executed/evaluated

The goal of this document is to ensure the MVP has exactly one primary optimization target:

> **Optimize the Meta schema; keep Render fixed.**

---

## 2. Freeze rule

For MVP rounds, the following should be treated as frozen unless Xin explicitly opens a separate Render-ablation line:

1. block order
2. block names
3. common wrapper role statement
4. Task skill insertion location
5. evidence insertion location
6. Skill Writer output contract
7. omission behavior when evidence is absent

Allowed variation inside MVP:
- the **Meta schema** content
- the current task context values
- the current Task skill content
- the evidence values

Not allowed as routine MVP drift:
- changing wrapper wording every round
- moving evidence earlier/later to chase gains
- changing output contract shape between categories
- using different render layouts for different categories

---

## 3. Render inputs

A Render step takes exactly four semantic inputs plus one fixed contract:

1. **Meta schema**
   - class-level rewrite prior
2. **Task context**
   - task name
   - compact task description / contract
   - local constraints
3. **Current Task skill**
   - the current skill text being revised
4. **Evidence**
   - previous scores / failure notes / ambiguity notes when available
5. **Frozen output contract**
   - required structure of the Skill Writer response

---

## 4. Canonical Render block order

The final Meta skill should always be rendered in this order:

1. **Common wrapper**
2. **Meta schema block**
3. **Task context block**
4. **Current Task skill block**
5. **Evidence block**
6. **Output contract block**

This order is frozen for MVP.

---

## 5. Block semantics

### 5.1 Common wrapper

Purpose:
- tell the model it is revising a Task skill, not directly solving the task
- keep the operation focused on skill improvement
- prevent drift into free-form task completion

Frozen semantic content:
- you are revising a Task skill
- use the Meta schema as the class-level guidance prior
- produce a revised Task skill candidate
- explain changes briefly and structurally

### 5.2 Meta schema block

Purpose:
- inject the reusable class-level rewrite prior
- this is the main dynamic / optimizable block

Contents inserted from the selected Meta schema:
- category_id
- semantic_intent
- emphasize
- avoid
- expected_good_fit
- expected_bad_fit
- hypothesized_primary_failure_modes
- meta_prompt_seed

### 5.3 Task context block

Purpose:
- provide the local task contract
- localize the class-level Meta schema to the current task

Required fields:
- `task_name`
- `task_summary`
- `task_constraints`

Optional:
- `task_inputs`
- `task_output_requirements`
- `task_verifier_notes`

### 5.4 Current Task skill block

Purpose:
- make the edit target explicit
- avoid hidden state about what is being revised

Required field:
- full current Task skill text

### 5.5 Evidence block

Purpose:
- provide local optimization context without changing the class-level Meta schema itself

Allowed evidence items:
- prior score
- best prior score
- failure summary
- low-margin competitor info
- instability note
- verifier failure family

If no evidence exists yet:
- render a fixed placeholder such as `No prior run evidence available.`
- do **not** omit the block entirely

### 5.6 Output contract block

Purpose:
- force consistent Skill Writer output
- make later parsing / diffing / update audit easier

Frozen required response shape:

```yaml
revised_task_skill: |
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

---

## 6. Canonical render skeleton

```text
[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: ...
Semantic intent: ...
Emphasize:
- ...
Avoid:
- ...
Expected good fit:
- ...
Expected bad fit:
- ...
Hypothesized primary failure modes:
- ...
Meta schema seed guidance:
...

[Task context block]
Task name: ...
Task summary: ...
Task constraints:
- ...
Task output requirements:
- ...

[Current Task skill block]
Current Task skill:
...

[Evidence block]
Prior score: ...
Failure summary: ...
Competing schema note: ...

[Output contract block]
Return YAML with fields:
revised_task_skill, change_summary{keep/add/remove/sharpen}, rationale
```

---

## 7. Minimal omission rules

To keep Render frozen and comparable across tasks:

- never omit the Common wrapper
- never omit the Output contract block
- never omit the Current Task skill block
- never omit the Evidence block entirely; use a fixed empty placeholder when needed
- never switch block order per category

---

## 8. What the Outer Loop may and may not change

### 8.1 Outer Loop may change
- the Meta schema text/content
- the selected schema for a task
- later, whether two schemas should merge

### 8.2 Outer Loop should not change in MVP
- the Render structure
- the wrapper style
- the output contract
- the block order
- the evidence insertion format

This is the main control needed to keep optimization attributable.

---

## 9. Relationship to pilot execution

During the pilot:
- columns vary by **Meta schema**
- task rows vary by task
- Render stays fixed across the whole round

So a score difference between two columns should be interpreted primarily as:

> difference between Meta schemas under the same Render

not as wrapper drift.

---

## 10. Immediate use

This frozen spec should be referenced by:
- `docs/plans/skillx/skillx-pilot-assignment-pass-v0.1.md`
- `docs/plans/skillx/skillx-assignment-matrix-protocol-v0.1.md`
- any future pilot runner / manifest

The next implementation step is to use this exact frozen template in the pilot manifest and later runner so every `(task, schema)` pair is rendered comparably.
