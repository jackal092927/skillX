# SkillX Outer-Loop Update Protocol v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-03
- **Role:** category-level Meta-schema update + loop-control protocol for prompt-induced clustering MVP
- **Status:** working MVP protocol

---

## 1. Purpose

This document defines how the outer loop should:
- update the Meta-schema bank after assignment,
- monitor collapse and weak structure,
- checkpoint loop artifacts,
- and decide whether to continue, stop, or simplify.

This protocol assumes:
- Meta-schema bank defined in `docs/plans/skillx/skillx-prompt-bank-v0.1.md`
- frozen Render defined in `docs/plans/skillx/skillx-render-template-frozen-v0.1.md`
- assignment rule defined in `docs/plans/skillx/skillx-assignment-matrix-protocol-v0.1.md`
- Meta-schema edit operator defined in `docs/plans/skillx/skillx-meta-schema-update-operator-v0.1.md`
- Meta-schema search operator defined in `docs/plans/skillx/skillx-meta-schema-search-operator-v0.2.md`
- Meta-schema acceptance scorecard defined in `docs/plans/skillx/skillx-meta-schema-acceptance-scorecard-v0.1.md`
- umbrella framing in `docs/plans/skillx/skillx-prompt-bank-clustering-and-outer-loop-spec-v0.1.md`
- pilot manifest defined in `docs/plans/skillx/skillx-pilot-round-0-manifest-v0.1.json`

---

## 2. Outer-loop object

The outer loop does **not** directly optimize tasks one by one.

Its main object is:

> **the category-level Meta-schema bank**

Each round updates one or more Meta-schema entries using evidence from the tasks currently assigned to them.

Important MVP simplification:
- the outer loop optimizes the Meta schema
- the Render layer stays frozen as much as possible during MVP
- schema updates should be implemented as constrained schema edits, not unconstrained prompt rewrites

---

## 3. Update inputs

For each category `k`, define its current task set:

```text
T_k = { tasks assigned to category k }
```

The schema updater for category `k` should receive:
- assigned tasks `T_k`
- their score traces / summaries
- failed cases
- successful cases
- low-margin / ambiguous cases
- the top competing prompt for each ambiguous task
- cluster-size info
- optional task-record sidecar info for interpretation

---

## 4. Update rule

## 4.1 Core objective

Update each category Meta schema to:
- improve performance on its assigned tasks,
- sharpen the schema’s identity,
- reduce repeated failure patterns,
- and avoid drifting into a generic bank-wide schema unless the data truly supports that result.

## 4.2 Contrastive update principle

Each update should be contrastive.

That means it should ask:
- what is working for the tasks assigned here?
- what is consistently failing here?
- what are competing schemas doing better on borderline tasks?
- what should this schema explicitly *not* try to cover?

This is important because a non-contrastive updater will tend to homogenize the bank.

## 4.3 Update structure

The detailed operators are defined in:
- `docs/plans/skillx/skillx-meta-schema-update-operator-v0.1.md`
- `docs/plans/skillx/skillx-meta-schema-search-operator-v0.2.md`

Acceptance / replacement decisions should be judged through:
- `docs/plans/skillx/skillx-meta-schema-acceptance-scorecard-v0.1.md`

Each category update should explicitly consider:

```yaml
keep:
  - guidance that appears to help this category consistently
add:
  - missing guidance suggested by repeated failures
remove:
  - guidance that appears noisy, generic, or harmful
sharpen:
  - wording that clarifies what this category is for
exclude:
  - tasks / behaviors that seem outside the category's scope
```

## 4.4 Low-support rule

Do not aggressively update a category Meta schema when support is too small.

Recommended initial rule:
- if assigned task count `< 3`, prefer:
  - freeze the schema,
  - or perform only minimal wording edits,
  - or postpone the update until another round

This avoids unstable updates based on tiny clusters.

## 4.5 Empty-cluster rule

If a category receives no tasks:
- do not silently delete it immediately
- mark it as **unoccupied this round**
- inspect whether:
  - its schema is too weak,
  - it overlaps too much with another schema,
  - or it is simply unnecessary

If the category stays empty across multiple rounds, then merge or retire it.

---

## 5. Update artifact

Each category update should emit:

```yaml
category_id: string
old_version: string
new_version: string
support_size: int
mean_assigned_score: float
main_failure_patterns:
  - string
main_borderline_competitors:
  - string
change_summary:
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
expected_effect:
  - string
```

This makes Meta-schema evolution auditable.
The final task-specific Meta skill is instantiated later by the frozen Render layer.

---

## 6. Collapse diagnostics

Collapse is the main system-level failure mode.

A collapse means the bank stops producing meaningful structure, for example because:
- one schema wins almost everywhere,
- most schema scores are nearly tied,
- or schema updates make the bank increasingly similar.

## 6.1 Track these metrics every round

```yaml
occupied_cluster_count: int
largest_cluster_share: float
cluster_size_entropy: float
mean_assignment_margin: float
low_margin_task_fraction: float
schema_pair_score_correlation: float
schema_text_similarity: float | null
schema_update_diversity: float | null
```

## 6.2 Warning patterns

Potential collapse signs:
- occupied clusters <= 2
- largest cluster share very high
- low-margin task fraction very high
- score columns highly correlated
- prompts becoming textually or behaviorally too similar

## 6.3 Important interpretation rule

Collapse is not automatically a failure.

Possible interpretations:

1. **real universal protocol**
   - one schema genuinely works best almost everywhere
2. **bad collapse**
   - schemas were initialized too similarly
   - update rule removed schema distinctness
   - evaluator noise flattened differences
   - assignment rule was too coarse

The outer loop must distinguish these possibilities.

## 6.4 Universal baseline comparison

If one schema dominates most tasks, compare it to:
- `U0 = universal meta-protocol baseline`

If the dominant prompt does not beat `U0`, then the bank may not be learning meaningful structure.
If it clearly beats `U0`, then a universal best prompt may be a real empirical outcome.

---

## 7. One-loop protocol

A single outer-loop iteration should be:

### Step A — freeze Meta-schema bank
Freeze the current Meta-schema bank `P_1 ... P_K`.

Also keep the Render layer fixed for the whole round.

### Step B — run assignment matrix
Run all required `(task, schema)` evaluations under the fixed inner-loop budget.

### Step C — assign tasks
Use the assignment protocol to assign tasks to Meta-schema categories.

### Step D — inspect structure
Before updating, inspect:
- cluster occupancy
- assignment margins
- ambiguous cases
- collapse indicators

### Step E — update Meta schemas
Update each Meta schema using the tasks currently assigned to it.

### Step F — checkpoint
Write all round artifacts:
- score matrix
- assignments
- diagnostics
- Meta-schema updates
- updated Meta-schema bank versions

---

## 8. Multi-loop protocol

Repeat the one-loop protocol for several rounds.

## 8.1 Recommended MVP schedule

Start with:
- `L = 2` to `4` outer loops

This is enough to test whether:
- assignments stabilize,
- schemas specialize,
- collapse appears,
- or a universal prompt begins to dominate.

## 8.2 Stop conditions

Stop when any of the following holds:
- assignments become stable across successive rounds
- overall gains plateau
- prompt edits become negligible
- collapse becomes stable and interpretable
- experiment budget is exhausted

## 8.3 Re-assignment is mandatory

After each Meta-schema update:
- rerun the assignment step
- do **not** keep assignments fixed across loops

The whole point is to let:
- prompt quality,
- task assignment,
- and cluster structure

co-evolve.

---

## 9. Role of the hybrid sidecar during updates

The sidecar task-record schema should assist updates, but not replace performance-induced assignment.

Use it for:
- diagnosing why a cluster is collapsing
- spotting category drift
- understanding whether a borderline task is semantically off-cluster
- deciding whether balance intervention is reasonable
- post-hoc analysis of what the learned Meta-schema bank has discovered

Do not use it to override strong performance evidence.

---

## 10. Recommended first experimental rollout

### Phase 0 — initialize bank
- write the initial 6–7 category Meta schemas
- make schema distinctness explicit

### Phase 1 — matrix pilot
- run a representative task slice against the full Meta-schema bank
- debug assignment margins, tie-breaks, and obvious collapse

### Phase 2 — full matrix pass
- run the broader task set
- produce the first prompt-induced clustering result

### Phase 3 — first update
- update prompts from assigned-task evidence
- checkpoint prompt diffs clearly

### Phase 4 — rerun and reassign
- run the second round
- inspect whether structure sharpens, weakens, or collapses

---

## 11. Bottom line

The outer loop should now be understood as:

> **Meta-schema-bank optimization through repeated assignment, update, and re-assignment**

with:
- collapse explicitly monitored,
- universal-prompt success treated as a valid possible outcome,
- and the hybrid task-record schema used as a supportive diagnostic sidecar rather than as the main clustering mechanism.
