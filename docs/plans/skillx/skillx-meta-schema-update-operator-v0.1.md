# SkillX Meta-Schema Update Operator v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-03
- **Role:** defines what the Meta schema optimization object actually is and how the MVP outer loop should update it
- **Status:** working MVP spec

---

## 1. Purpose

This document answers four practical questions:

1. What is the current form of a Meta schema?
2. Is it just a rubric bundle, or a full prompt, or something in between?
3. What exactly should the outer loop optimize?
4. Is this a combinatorial optimization problem, and if so, how should we handle it in MVP?

The short answer is:

> **A Meta schema is a semi-structured meta-policy object.**
>
> It is not just a label, not just a rubric checklist, and not just one free-form prompt string.
>
> In MVP, we should optimize it through constrained schema editing, not through unconstrained prompt search.

---

## 2. What a Meta schema is

The current Meta schema has a fixed structure like:

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

This means the optimization object has **two layers**.

### 2.1 Slot layer

This is the more structured layer:
- `semantic_intent`
- `emphasize`
- `avoid`
- `expected_good_fit`
- `expected_bad_fit`
- `hypothesized_primary_failure_modes`

These fields behave like a structured policy skeleton.

### 2.2 Realization layer

This is the more textual layer:
- `meta_prompt_seed`

This is the natural-language realization of the slot layer.
It is what later gets packaged by Render into a task-specific Meta skill.

### 2.3 Implication

So the Meta schema is best understood as:

> **a structured rewrite prior with a textual realization**

This is why it feels partly like a rubric and partly like a prompt.
That is not a bug — it is the intended object type.

---

## 3. What the outer loop optimizes

For MVP, the outer loop should optimize **only** the Meta schema.

It should **not** optimize:
- the Render layer
- the wrapper
- the output contract
- the task-specific Task skill directly
- the final task-specific Meta skill as an independent reusable object

So the optimization target is:

> **the class-level rewrite prior stored in the Meta schema**

More concretely, the outer loop is trying to improve:
1. what the class-level guidance tells the Skill Writer to emphasize
2. what it tells the Skill Writer to avoid
3. what failure modes it assumes are primary
4. what tasks it believes it should / should not cover
5. how those decisions are rendered into a stable seed guidance block

---

## 4. Is it a rubric bundle?

Partly, yes.
But not only.

### 4.1 Rubric-like components

These are rubric-like or checklist-like:
- `emphasize`
- `avoid`
- `expected_good_fit`
- `expected_bad_fit`
- `hypothesized_primary_failure_modes`

They can be edited as semi-discrete policy components.

### 4.2 Non-rubric components

These are not just rubric entries:
- `semantic_intent`
- `seed_rationale`
- `meta_prompt_seed`

These capture:
- category meaning
- why the schema exists
- how the schema is actually verbalized for the Skill Writer

### 4.3 Operational conclusion

So for MVP we should **not** think of Meta schema optimization as:
- “optimize one giant prompt string”

and also not as:
- “just select checklist items independently”

Instead we should think of it as:

> **structured policy editing + controlled text regeneration**

---

## 5. Is this a combinatorial optimization problem?

### 5.1 Strict answer

Yes, in a broad sense.

Because the search space contains:

1. **discrete / semi-discrete choices**
   - which `emphasize` items to include
   - which `avoid` items to include
   - how to adjust good-fit / bad-fit boundaries
   - which failure modes to treat as primary

2. **textual realization choices**
   - how to phrase the schema clearly
   - how to keep prompt distinctness visible
   - how to verbalize the policy without drift

So mathematically the space is mixed:

> **discrete policy structure + textual realization**

### 5.2 MVP answer

Even though it is combinatorial in principle, **we should not treat MVP as brute-force combinatorial search**.

We should instead treat MVP as:

> **constrained local editing in Meta-schema space**

That means:
- small edits
- interpretable edits
- contrastive edits
- versioned edits
- acceptance based on downstream evidence

This keeps the search stable and understandable.

---

## 6. MVP optimization stance

For MVP, the Meta schema should be optimized under five constraints:

### 6.1 Fixed schema shape

Do not change the field structure itself.
The schema stays:
- `semantic_intent`
- `emphasize`
- `avoid`
- `expected_good_fit`
- `expected_bad_fit`
- `hypothesized_primary_failure_modes`
- `seed_rationale`
- `meta_prompt_seed`

### 6.2 Fixed Render

Render stays frozen.
So when performance changes, we can attribute the change mainly to the Meta schema update.

### 6.3 Slot-first optimization

Treat the slot layer as the main source of truth.
Then update `meta_prompt_seed` so it matches the updated slots.

This is crucial.
Otherwise the seed prompt can drift semantically away from the schema.

### 6.4 Local edits only

Each round should make limited, auditable changes.
Do not fully rewrite everything unless there is very strong evidence.

### 6.5 Contrastive evidence

Every update should look not only at:
- what helps assigned tasks

but also at:
- which competing schemas beat this one on borderline tasks
- what this schema should stop trying to cover

---

## 7. Which fields should be optimized directly?

## 7.1 Primary editable fields

These are the main optimization surface in MVP:
- `emphasize`
- `avoid`
- `expected_good_fit`
- `expected_bad_fit`
- `hypothesized_primary_failure_modes`

These are the most important because they directly control the rewrite prior.

## 7.2 Secondary editable fields

These can be edited, but more conservatively:
- `semantic_intent`
- `seed_rationale`

`semantic_intent` should usually remain stable unless the category boundary genuinely changes.

`seed_rationale` is explanatory rather than causal.
It can be updated for clarity, but it should not be treated as the main optimization lever.

## 7.3 Derived / regenerated field

This should usually be rewritten **after** slot edits:
- `meta_prompt_seed`

The MVP rule should be:

> first edit the policy slots, then regenerate the prompt seed so it faithfully realizes the updated policy.

So `meta_prompt_seed` is important, but should not be treated as a free-floating independent object.

## 7.4 Frozen fields in MVP

These should not be optimized as ordinary outer-loop variables:
- `category_id`
- schema field names / structure
- Render wrapper
- output contract

---

## 8. Allowed edit operators

The MVP operator should use a small set of explicit edit actions.

## 8.1 Slot edit operators

### `add_emphasize(item)`
Add a missing priority that repeated evidence suggests is helpful.

### `remove_emphasize(item)`
Remove an emphasis item that appears generic, noisy, or harmful.

### `sharpen_emphasize(old, new)`
Keep the intent but make it more precise.

### `add_avoid(item)`
Add a newly observed anti-pattern.

### `remove_avoid(item)`
Remove an avoid rule that is unnecessary or overly suppressive.

### `sharpen_avoid(old, new)`
Make an anti-goal more operational.

### `expand_good_fit(item)`
Widen the schema’s intended coverage when evidence supports transfer.

### `shrink_good_fit(item)`
Narrow the schema’s intended coverage when it is overreaching.

### `expand_bad_fit(item)`
Mark newly observed mismatch zones.

### `shrink_bad_fit(item)`
Remove boundaries that turned out to be too strict.

### `add_failure_mode(item)`
Add a primary failure mode seen repeatedly in assigned tasks.

### `remove_failure_mode(item)`
Remove one that is no longer explanatory.

### `sharpen_failure_mode(old, new)`
Refine a vague failure hypothesis into a more actionable one.

## 8.2 Realization operator

### `rewrite_meta_prompt_seed()`
Regenerate `meta_prompt_seed` so it faithfully reflects the updated slot layer.

Constraint:
- the rewrite should not invent a new policy not represented in the slots
- it should express the slot-layer policy more clearly, not silently replace it

## 8.3 Optional explanatory operator

### `refresh_seed_rationale()`
Update rationale text so future readers know why the current schema looks this way.

This is optional and secondary.

---

## 9. Update operator input bundle

For each schema `p_k`, the update operator should consume an evidence bundle like:

```yaml
category_id: string
support_size: int
assigned_task_summaries:
  - task_name: string
    score: float
    outcome: success|failure|mixed
    main_failure_notes:
      - string
ambiguous_borderline_cases:
  - task_name: string
    current_schema_score: float
    competing_schema_id: string
    competing_schema_score: float
    margin: float
cross_schema_losses:
  - task_name: string
    won_by: string
    suspected_reason: string
stability_notes:
  - string
```

This keeps updates grounded in actual assigned-task evidence instead of vague intuition.

---

## 10. Update operator output bundle

The operator should emit a structured patch, not just a new raw prompt.

```yaml
category_id: string
old_version: string
new_version: string
operator_summary:
  keep:
    - string
  add:
    - string
  remove:
    - string
  sharpen:
    - string
  exclude:
    - string
slot_edits:
  emphasize:
    add: [string]
    remove: [string]
    sharpen: [{old: string, new: string}]
  avoid:
    add: [string]
    remove: [string]
    sharpen: [{old: string, new: string}]
  expected_good_fit:
    add: [string]
    remove: [string]
  expected_bad_fit:
    add: [string]
    remove: [string]
  hypothesized_primary_failure_modes:
    add: [string]
    remove: [string]
    sharpen: [{old: string, new: string}]
realization_update:
  meta_prompt_seed_rewritten: true
expected_effect:
  - string
acceptance_notes:
  - string
```

This makes schema evolution auditable and comparable across rounds.

---

## 11. Acceptance rule for schema updates

A proposed Meta-schema update should not be accepted just because it “sounds better.”

The acceptance logic should check at least four things.

### 11.1 Assigned-task utility

Did the updated schema improve performance on tasks assigned to it?

### 11.2 Borderline competitiveness

Did the updated schema become more competitive on low-margin tasks near category boundaries?

### 11.3 Distinctness preservation

Did the updated schema remain meaningfully distinct from the others?

### 11.4 Minimality

Was the update reasonably local, or did it rewrite too much at once without enough support?

---

## 12. Distinctness preservation rule

A Meta schema should only stay independent if it still differs from the others on at least 2–3 of these dimensions:

1. primary optimization objective
2. default workflow bias
3. primary suspected failure mode
4. anti-goal
5. good-fit / bad-fit boundary

So an update is bad if it increases score locally but makes all schemas converge into one generic prompt family without evidence that such collapse is real.

---

## 13. Practical MVP algorithm

The intended MVP loop is:

### Step 1 — assignment
Assign tasks to schemas by performance under fixed Render.

### Step 2 — evidence aggregation
For each schema, summarize:
- successful assigned tasks
- failed assigned tasks
- low-margin tasks
- losses to competing schemas

### Step 3 — slot edits
Propose explicit edits to:
- `emphasize`
- `avoid`
- `expected_good_fit`
- `expected_bad_fit`
- `hypothesized_primary_failure_modes`

### Step 4 — prompt-seed rewrite
Regenerate `meta_prompt_seed` so it matches the updated slots.

### Step 5 — distinctness check
Reject or soften updates that erase useful schema boundaries too aggressively.

### Step 6 — rerun next round
Evaluate the new schemas under the same frozen Render.

This is much closer to **iterative structured editing** than to open-ended prompt search.

---

## 14. Final answer to the “combinatorial optimization” question

If someone asks:

> Is Meta-schema optimization a combinatorial optimization problem?

The best concise answer is:

> **In principle yes, because the schema has discrete policy components and textual realization choices.**
>
> **But in MVP we should operationalize it as constrained local schema editing, not brute-force combinatorial search.**

That means:
- structured slots are the main optimization surface
- prompt text is regenerated from updated slots
- edits are local and auditable
- Render stays fixed

So the practical MVP problem is:

> **optimize a semi-structured Meta-policy object by local contrastive edits under a frozen execution wrapper**

—not “search over all possible prompt combinations.”

---

## 15. Immediate next use

This document should now guide:
- `docs/plans/skillx/skillx-outer-loop-update-protocol-v0.1.md`
- future prompt-bank update operators
- any later runner that performs category-level schema revision

The next concrete follow-up would be:

1. wire this operator into the outer-loop update protocol
2. define a minimal acceptance scorecard for schema patches
3. later, only if needed, explore a stronger combinatorial or evolutionary search variant as a separate line
