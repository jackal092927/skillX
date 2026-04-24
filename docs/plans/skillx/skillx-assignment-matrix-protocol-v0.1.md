# SkillX Assignment Matrix Protocol v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-03
- **Role:** assignment-side protocol for Meta-schema-bank clustering MVP
- **Status:** working MVP protocol

---

## 1. Purpose

This document defines how to:
- build the task × Meta-schema score matrix,
- assign tasks to Meta-schema-bank categories,
- handle ties / ambiguity,
- and produce the assignment artifacts used by the outer loop.

This protocol assumes the Meta-schema bank is defined in:
- `docs/plans/skillx/skillx-prompt-bank-v0.1.md`
- `docs/plans/skillx/skillx-prompt-bank-v0.1.json`

and the broader loop is defined in:
- `docs/plans/skillx/skillx-prompt-bank-clustering-and-outer-loop-spec-v0.1.md`
- `docs/plans/skillx/skillx-render-template-frozen-v0.1.md`
- `docs/plans/skillx/skillx-pilot-assignment-pass-v0.1.md`
- `docs/plans/skillx/skillx-pilot-round-0-manifest-v0.1.json`

---

## 2. Inputs

Required inputs:

```yaml
task_set: [task_name]
meta_schema_bank: [meta_schema]
inner_loop_system: Mark Auto Research
evaluator: fixed benchmark evaluator
budget:
  per_pair_run_budget: object
  repeat_policy: object
optional_sidecar:
  task_record_jsonl: path
```

### 2.1 Fixed-budget rule

All `(task, meta_schema)` evaluations in the same assignment round should use the same budget policy as much as possible.

The score matrix is only meaningful if Meta-schema candidates are compared under a comparable budget.

MVP simplification:
- the variable part across columns is the Meta schema
- the Render layer should stay fixed across the whole assignment round

---

## 3. Score matrix

Define:

```text
S(task_i, schema_k)
```

Each entry is the result of running task `i` under schema `k` with the fixed inner-loop budget.

Operationally this means:
- freeze Render,
- instantiate a task-specific Meta skill from schema `k`,
- run the inner loop with that Meta skill,
- and record the evaluator score.

### 3.1 Primary score

Use the task evaluator score as the primary scalar assignment score.

For `R0 -> R3` inner-loop runs, the executable MVP should not use only
one terminal scalar when round-level scores are available. The default
assignment score should be trajectory-aware:

```text
assignment_score =
  0.50 * reported_score
  + 0.30 * weighted_mean(R0, R1, R2, R3)
  + 0.20 * clamp(50 + best(R0..R3) - R0, 0, 100)
```

Recommended default round weights:

```yaml
R0: 0.15
R1: 0.20
R2: 0.30
R3: 0.35
```

This keeps final quality central while also using:
- the full reward curve, so two equal final scores can differ if one
  was consistently better across the loop,
- R0-relative growth, so the assignment signal captures which schema
  actually induced useful improvement.

The raw `reported_score`, `selected_score`, `best_observed_score`, and
per-round scores should still be emitted. The trajectory-aware score is
the default assignment scalar, not a replacement for the audit fields.

### 3.2 Optional support metrics

In addition to the scalar score, collect:
- success / failure flag
- final score
- best score (if multiple inner rounds)
- per-round scores `R0`, `R1`, `R2`, `R3`
- weighted round mean
- `R0 -> best` and `R0 -> final` deltas
- runtime / timeout flags
- major failure family

These do not define assignment directly, but help later analysis.

### 3.3 First-pass evaluation policy

For the MVP first pass:
- run **one** evaluation per `(task, schema)` pair for broad coverage
- only run repeats when:
  - the assignment margin is small,
  - the task is high-priority,
  - or the outcome looks unstable / suspicious

This prevents the matrix from becoming too expensive before we know whether the clustering signal is real.

---

## 4. Assignment rule

## 4.1 Basic hard assignment

For each task `t`:

```text
assigned_schema(t) = argmax_k S(t, k)
```

This is a hard assignment, not a soft mixture.

## 4.2 Margin

Also compute:

```text
margin(t) = top1_score(t) - top2_score(t)
```

This is the key ambiguity measure.

### 4.3 Recommended confidence bands

If scores are normalized to `[0, 1]`, a practical initial rule is:

- `margin >= 0.10` -> **high-confidence assignment**
- `0.05 <= margin < 0.10` -> **medium-confidence assignment**
- `margin < 0.05` -> **low-confidence / tie-like assignment**

These thresholds are starting points, not frozen truths.

---

## 5. Tie-break rule

Tie-break logic should be triggered when `margin < epsilon`.

Recommended initial value:

```yaml
epsilon: 0.05
```

if the primary evaluator score is in `[0,1]`.

## 5.1 Tie-break order

When ambiguity occurs, apply:

1. semantic match
2. cluster balance, only when the score loss is very small
3. previous assignment stability
4. seeded random fallback

---

## 5.2 Semantic match tie-break

Use the task-record sidecar only as a prior when scores are close.

Relevant sidecar fields:
- `task_object_seed`
- `verifier_mode`
- `workflow_topology`
- `tool_surface_regime`

### Suggested rule

For the ambiguous top-2 schemas, assign each a small semantic prior score:

```text
semantic_prior(schema, task) in {0, 1, 2, 3}
```

where higher means better fit between:
- the schema’s intended category
- and the task’s semantic/topology profile

Then prefer the schema with the higher semantic prior.

Important:
- this does **not** override large score differences
- it only resolves near-ties

---

## 5.3 Cluster-balance tie-break

If semantic match does not resolve the tie, prefer the assignment that avoids pathological imbalance.

### Recommended rule

Only apply balance as a soft preference inside ambiguous cases.

Examples of valid use:
- one cluster is nearly empty, while another is already dominant
- both schemas are nearly tied and semantically plausible

Examples of invalid use:
- forcing equal cluster sizes when one schema is clearly better

A simple initial balance heuristic:

```text
balance_penalty(schema_k) = lambda * current_cluster_share(schema_k)
```

Use only within low-margin cases.

For the first executable pass, balance should not override a clearly better
score. A practical starting guardrail is:

```text
balance_tie_max_loss <= 0.01
```

when scores are normalized to `[0, 1]` (`<= 1pp` in percent-score space).
This lets balance resolve near-identical choices without turning assignment
into forced equalization.

---

## 5.4 Previous-assignment stability

If the task already had an assignment in the prior outer-loop round, and the current round remains ambiguous, prefer staying with the previous assignment unless the new schema wins by a clearly meaningful margin.

This reduces oscillation.

### Suggested rule

If:
- `margin < epsilon`
- and previous assigned prompt is in the top-2

then keep the previous assignment.

---

## 5.5 Seeded random fallback

If ambiguity still remains, use seeded random tie-breaking over the remaining
candidates.

The seed should be recorded in the artifact config. This keeps reruns
reproducible while avoiding lexicographic or fixed-priority bias toward any
schema id.

---

## 6. Universal baseline control

To interpret possible collapse, include:

```yaml
U0: universal meta-protocol baseline
```

This is evaluated like any other prompt for comparison purposes.

However, in the first MVP implementation, `U0` can be handled as:
- a non-bank control row/column,
- not necessarily an assignable cluster,
- unless we later decide to allow it as an explicit bank member.

This keeps the Meta-schema bank focused while still allowing universal-protocol comparison.

---

## 7. Assignment artifacts

Each round should emit at least:

### 7.1 Score matrix artifact

```yaml
score_matrix_round_r:
  rows: tasks
  columns: Meta-schema categories
  values: scores
```

### 7.2 Assignment table

Per task:

```yaml
task_name: string
assigned_category: string
best_score: float
second_best_category: string
second_best_score: float
margin: float
assignment_confidence: high|medium|low
tie_break_used: bool
tie_break_reason: string | null
```

### 7.3 Round summary

```yaml
occupied_cluster_count: int
cluster_sizes: {category: count}
mean_margin: float
low_margin_fraction: float
```

### 7.4 Schema training assignment table

Per `(schema, task)` update-evidence row:

```yaml
schema_id: string
task_name: string
evidence_role: primary_assignment|floor_top_score
schema_score: float
schema_rank_for_task: int
primary_assigned_category: string | null
task_best_schema: string | null
task_best_score: float | null
```

This table is intentionally many-to-many. It is the artifact consumed by
schema update packaging, while the primary assignment table remains the
single-label score interpretation.

---

## 8. Minimum diagnostics at assignment time

The assignment round should immediately flag:
- empty prompts
- near-empty prompts
- extremely dominant prompts
- unusually flat score columns
- tasks whose top-3 prompts are almost tied

This lets us see weak structure early.

---

## 9. Minimum training/evidence allocation for schema updates

### 9.1 Problem

The primary hard assignment (Section 4) can leave some schemas with
zero or very few assigned tasks. A schema with no assigned tasks
receives no evidence during the update pass and cannot evolve, even
if it showed moderate scores on several tasks. Over iterations this
creates a silent death spiral: the schema never improves because it
never gets signal.

### 9.2 Rule: guaranteed update evidence floor

After the primary assignment pass, compute a **schema training assignment set**
for each schema `k`:

```text
training_tasks(k) = primary_assigned_tasks(k)
                    ∪ top_scoring_tasks(k, floor_K)
                    where duplicates are removed

floor_K = max(2, ceil(0.10 * |task_set|))
```

That is: for every schema, always include the `floor_K` tasks on which
that schema scored highest — even if those tasks were assigned to a
different schema in the primary pass.

In the first few outer-loop iterations, this floor is intentionally
exploratory. It is acceptable for a schema to receive its best 2-3 available
tasks even when it is not the top-ranked schema for those tasks, because the
purpose is to prevent empty clusters from receiving no update signal.

### 9.3 Separation of concerns

This does **not** change the primary single-label assignment or the score matrix.
The primary assignment remains `argmax_k S(t, k)` as defined in
Section 4.

The schema training assignment set is used **only** for feeding the schema
update operator. It answers a different question:
- Primary assignment: "which schema is best for this task right now?"
- Training assignment: "which tasks give this schema the most useful
  signal for improvement?"

Because this is a training/evidence allocation, it is many-to-many: the same
task may provide update signal to multiple schemas.

### 9.4 Why `max(2, ceil(10%))`

- The fixed floor of 2 prevents any schema from being starved even in
  small task pools (e.g., a 7-task pilot would give `max(2, 1) = 2`).
- The 10% fraction scales with larger task sets (e.g., 100 tasks
  gives a floor of 10).
- Using `max` rather than a single rule avoids degenerate behavior at
  both ends of the scale.

### 9.5 Interaction with diagnostics

The minimum diagnostics (Section 8) should additionally report:

```yaml
schemas_below_floor:
  - category: string
    primary_assigned_count: int
    floor_K: int
    top_K_tasks_added: [task_name]
    training_evidence_count: int
```

This makes it visible when and where the floor allocation is doing
work, so you can judge whether a schema is genuinely weak (and a
merge candidate) versus simply underexplored.

---

## 10. Recommended first experiment schedule

### Phase A — representative pilot

Before running all tasks × all prompts:
- choose a small representative slice
- verify that scores are stable enough to produce nontrivial margins
- debug tie-break logic

### Phase B — broad assignment matrix

Then run the broader task set against the full Meta-schema bank.

### Phase C — ambiguity repeats

Only after the first assignment pass:
- rerun the ambiguous low-margin tasks
- if needed, average repeated scores for the tie-break region

This is much cheaper than repeating the whole matrix blindly.

---

## 11. Bottom line

The assignment rule for the MVP is:

> **assign each task to the prompt category that performs best on it**
> with **semantic prior + balance + assignment stability** used only to resolve near-ties.

This keeps the clustering result driven primarily by performance while still using the hybrid task-record structure where it is most useful.
