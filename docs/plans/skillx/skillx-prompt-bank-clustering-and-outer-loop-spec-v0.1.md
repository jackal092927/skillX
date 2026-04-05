# SkillX Prompt-Bank Clustering and Outer-Loop Spec v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-02
- **Role:** operational MVP spec for Meta-schema-bank clustering + outer-loop optimization
- **Status:** working MVP spec

---

## 1. Why this document exists

The previous clustering discussion produced two useful but incomplete ideas:

1. a **flat hybrid task-record schema**
2. a need for a more direct outer-loop object tied to **meta skill prompts**

After discussion with Xin, the current MVP direction is now clearer:

> **Cluster tasks by which category-level Meta schema produces the best task-specific Meta skill on them, then optimize those schemas and re-assign iteratively.**

This reframes clustering and optimization as a single alternating loop.

Derived implementation docs:
- `docs/plans/skillx/skillx-prompt-bank-v0.1.md`
- `docs/plans/skillx/skillx-render-template-frozen-v0.1.md`
- `docs/plans/skillx/skillx-assignment-matrix-protocol-v0.1.md`
- `docs/plans/skillx/skillx-outer-loop-update-protocol-v0.1.md`
- `docs/plans/skillx/skillx-meta-schema-update-operator-v0.1.md`
- `docs/plans/skillx/skillx-pilot-assignment-pass-v0.1.md`
- `docs/plans/skillx/skillx-pilot-round-0-manifest-v0.1.json`

The goal is not to discover the prettiest taxonomy.
The goal is to test whether there exist a small number of category-level Meta schemas that:
- meaningfully differ,
- induce meaningful task assignments,
- and improve performance when optimized cluster-wise.

---

## 2. Core idea

Maintain a bank of `K` category-level Meta schemas.

For each task:
- freeze Render,
- instantiate a task-specific Meta skill from each candidate Meta schema,
- run the task under each instantiated Meta skill,
- measure performance,
- assign the task to the best-performing schema.

Then for each schema category:
- gather the tasks currently assigned to it,
- optimize that category-level Meta schema using their evidence,
- rerun the assignment step.

This is intentionally similar to a hard-EM / K-means-like alternating process:

- **assignment step**: task -> best schema category
- **update step**: assigned tasks -> improved Meta schema
- **repeat**

The schema is analogous to a centroid / prototype, except the assignment signal is:
- not embedding distance,
- but **performance under the instantiated task-specific Meta skill**.

---

## 3. Relation to Mark Auto Research

For the MVP, both loops should use the current Pi-Auto-Research-derived execution framework, now referred to by Xin as **Mark Auto Research**.

### Inner loop
The inner loop remains task-local:
- given a task,
- a current Task skill / context,
- and a selected task-specific Meta skill,
- the system performs local skill writing / rewriting / evaluation.

### Outer loop
The outer loop is category-level:
- maintain the Meta-schema bank,
- assign tasks to schemas,
- update schemas from assigned-task evidence,
- rerun and reassign.

So the outer loop does **not** optimize one task at a time.
It optimizes the Meta-schema bank through repeated task assignment and schema revision.

Important MVP simplification:
- optimize the Meta schema
- freeze Render as much as possible
- do not treat wrapper / packaging logic as a co-equal optimization target in the first MVP loop

---

## 4. Meta-schema bank

### 4.1 Initial bank size

For the MVP:
- set `K = 6` or `K = 7`
- keep `K <= 10`

### 4.2 Category distinctness rule

A category is only worth keeping if its Meta schema is meaningfully different from the others.

That means each schema should differ in what it tells the Skill Writer to emphasize or avoid.

Examples of meaningful differences:
- emphasize stage contracts vs avoid over-scaffolding
- emphasize reviewer logic vs emphasize direct generation
- emphasize abstention / fit-check vs emphasize synthesis / completion
- emphasize wrappers / environment handling vs emphasize artifact discipline

If two categories do **not** imply meaningfully different prompt guidance, they should be merged.

### 4.3 Initial category bank (seed proposal)

The current best seed is the existing flat high-level task taxonomy, with a possible merge if prompt distinctness is weak:

1. `artifact-generation`
2. `analytic-pipeline`
3. `engineering-composition`
4. `retrieval-heavy-synthesis`
5. `environment-control`
6. `methodology-guardrail`
7. `orchestration-delegation`

Possible simplification:
- merge `methodology-guardrail` + `orchestration-delegation` if their prompt policies do not remain meaningfully distinct.

### 4.4 Meta-schema entry schema

Each Meta-schema bank member should have at least:

```yaml
category_id: string
category_name: string
version: string
semantic_intent: string
meta_prompt: string
emphasize:
  - string
avoid:
  - string
expected_good_fit:
  - string
expected_bad_fit:
  - string
update_history:
  - round_id
```

The `emphasize` / `avoid` lists are important because they make schema distinctness inspectable.

---

## 5. Score matrix

Define a task-prompt score matrix:

```text
S(task_i, prompt_k)
```

Where each entry is the performance of task `i` under category prompt `k` after running the Mark Auto Research inner loop under a fixed experimental budget.

### 5.1 Score definition

For the MVP, the primary score should be the task’s evaluator score.

If multiple repeats are run for the same `(task, prompt)` pair, use an aggregate such as:
- mean score,
- or mean final score with optional stability notes.

### 5.2 Practical first-pass rule

Because the full matrix can be expensive, the first pass can use:
- one run per `(task, prompt)` pair for broad coverage,
- then extra repeats only for ambiguous or high-value assignments.

That preserves scale while still allowing later stability checks.

---

## 6. Assignment rule

### 6.1 Basic assignment

For each task `t`, assign:

```text
c(t) = argmax_k S(t, k)
```

That is, assign the task to the prompt category with the highest score.

### 6.2 Assignment confidence

Define:

```text
margin(t) = top1_score(t) - top2_score(t)
```

This gives a simple confidence measure.

Interpretation:
- large margin -> confident assignment
- small margin -> ambiguous assignment / tie-like case

### 6.3 Assignment output artifact

Each assignment record should contain:

```yaml
task_name: string
assigned_category: string
best_score: float
second_best_category: string
second_best_score: float
margin: float
assignment_confidence: string   # high / medium / low
```

---

## 7. Tie-break rule

Tie-breaking should be used when:
- score margins are very small,
- or when score differences are unlikely to be meaningful.

### 7.1 Trigger condition

Treat a task as ambiguous when:

```text
margin(t) < epsilon
```

where `epsilon` is a configurable margin threshold.

### 7.2 Tie-break priority order

When ambiguity occurs, use this order:

1. **semantic match**
2. **cluster balance**
3. **previous assignment stability**
4. deterministic fallback rule

### 7.3 Semantic match

Semantic match should be based on the current interpretable task annotations.

Useful sources:
- `task_object_seed`
- `verifier_mode`
- `workflow_topology`
- `tool_surface_regime`

This is not the primary assignment mechanism.
It is only a tie-break prior when scores are too close.

### 7.4 Cluster balance

If semantic match does not resolve the tie, prefer the assignment that avoids pathological imbalance.

Important:
- balance should be a **soft preference**, not a hard equalization constraint
- we do not want to force artificial symmetry if one prompt really is better

### 7.5 Previous assignment stability

If the task was already assigned in the previous loop and the current tie remains unresolved, prefer keeping the prior assignment unless there is clear evidence to move it.

This helps reduce oscillation.

---

## 8. Update rule

After assignment, update each category-level meta prompt using the tasks currently assigned to it.

### 8.1 Update set

For category `k`, define:

```text
T_k = { tasks assigned to category k }
```

### 8.2 Update inputs

The prompt updater should receive:
- assigned tasks
- their scores
- failed cases
- successful cases
- top competing categories for ambiguous tasks
- margin distribution
- optional sidecar task-record features for interpretation

### 8.3 Update objective

The category prompt should be updated to:
- improve average performance on its assigned tasks,
- reduce repeated failure patterns,
- preserve or strengthen the prompt’s distinct identity,
- and avoid drifting into a generic “works for everything” prompt unless the data truly supports that outcome.

### 8.4 Contrastive update principle

Each prompt update should be contrastive, not only positive.

That means the updater should consider:
- what helps its own assigned tasks,
- what makes it lose to competing prompts,
- and what should remain outside its intended scope.

This helps prevent prompt-bank homogenization.

### 8.5 Output

For each category, produce:

```yaml
category_id: string
old_version: string
new_version: string
change_summary:
  added:
    - string
  removed:
    - string
  sharpened:
    - string
expected_effect:
  - string
```

---

## 9. Collapse diagnostics

Collapse is the main outer-loop failure mode.

A collapse means the prompt bank stops producing meaningful structure, for example because:
- one prompt wins almost everywhere,
- most prompts become semantically similar,
- or score differences become too flat to support real assignment.

### 9.1 Diagnostic metrics

Track at least:

```yaml
occupied_cluster_count: int
largest_cluster_share: float
cluster_size_entropy: float
mean_assignment_margin: float
low_margin_task_fraction: float
prompt_pair_score_correlation: float
prompt_text_similarity: float | null
```

### 9.2 Warning patterns

Potential collapse signs:
- occupied clusters <= 2
- largest cluster share very high
- most tasks have tiny top1-top2 margins
- prompt pair scores highly correlated across tasks
- prompt texts become too similar after updates

### 9.3 Interpretation rule

Collapse is **not automatically failure**.

There are at least two possibilities:

1. **real universal protocol**
   - one meta-protocol genuinely works best almost everywhere
2. **bad collapse**
   - prompt initialization too weak
   - prompt updates homogenized the bank
   - score noise too high
   - assignment rule too coarse

The experiment should distinguish these, not assume either one in advance.

### 9.4 Universal-prompt control

To interpret collapse properly, include a control condition:

- `U0 = one universal meta-protocol applied to all tasks`

If the learned system collapses to one dominant prompt, compare it against `U0`.

If the dominant prompt is no better than a simple universal baseline, that is evidence the multi-prompt bank may not yet be doing meaningful clustering.

If it clearly beats `U0`, then a universal best protocol may be a real empirical result.

---

## 10. Role of the hybrid task-record schema

The earlier hybrid task-record schema is still useful, but its role changes.

It should now be treated as a **supportive sidecar**, not the main clustering engine.

### 10.1 What it is useful for

Use it for:
- prompt-bank initialization priors
- tie-break support
- balance support in ambiguous assignments
- collapse diagnosis
- post-hoc interpretation of learned clusters

### 10.2 What it should not do in the MVP

Do **not** use it as:
- the primary assignment mechanism
- a second clustering hierarchy
- a replacement for prompt-induced assignment

This keeps the MVP centered on performance-induced clustering while preserving useful structure for audit and rescue.

---

## 11. One-loop protocol

A single outer-loop iteration should look like this:

### Step A — freeze prompt bank
- freeze current category prompts `P_1 ... P_K`

### Step B — run assignment matrix
- for each task `t`
- for each prompt `P_k`
- run the Mark Auto Research inner loop
- record score `S(t, k)`

### Step C — assign tasks
- assign each task to the highest-scoring prompt
- apply tie-break rule where needed
- compute assignment margins and balance stats

### Step D — diagnose
- inspect occupancy, margins, collapse diagnostics
- check whether cluster structure looks meaningful enough to update

### Step E — update prompt bank
- update each category prompt using tasks currently assigned to it
- preserve category distinctness

### Step F — checkpoint artifacts
Write:
- score matrix
- assignment table
- cluster diagnostics
- updated prompt versions
- change summaries

---

## 12. Multi-loop protocol

Repeat the one-loop protocol for several rounds.

### 12.1 Recommended MVP schedule

Start with a small number of outer loops, e.g.:
- `L = 2` to `4`

This is enough to test whether:
- assignments stabilize,
- prompts specialize,
- and collapse appears.

### 12.2 Stop conditions

Stop when any of the following holds:
- assignment stability becomes high across successive rounds
- overall gains plateau
- prompt updates become negligible
- collapse becomes stable and interpretable
- budget is exhausted

### 12.3 Re-assignment rule

After each prompt update:
- rerun assignment under the updated bank
- do **not** keep assignments fixed across loops
- the whole point is to let the prompt bank and clustering co-evolve

---

## 13. Minimal artifact set

The MVP should produce at least:

1. `prompt_bank_v0.x.md/json`
2. `score_matrix_round_r.csv/json`
3. `assignments_round_r.csv/json`
4. `collapse_diagnostics_round_r.md/json`
5. `prompt_update_summaries_round_r.md`
6. optional sidecar:
   - `task_cluster_sidecar_v0.x.jsonl`

---

## 14. Recommended experimental rollout

### Phase 0 — bank definition
- define the initial `6–7` prompts
- make prompt distinctness explicit

### Phase 1 — small pilot
- run the full prompt bank over a representative task slice
- debug scoring, tie-breaks, and update behavior

### Phase 2 — broader matrix
- run the bank over the full SkillsBench set (or the current chosen benchmark slice)

### Phase 3 — 2–4 outer loops
- assignment
- update
- rerun
- reassign

### Phase 4 — interpretation
- determine whether:
  - meaningful multi-cluster structure emerged,
  - weak structure emerged,
  - or a universal meta-protocol appears to dominate.

---

## 15. Bottom line

The MVP clustering / outer-loop design is now:

> **prompt-induced flat clustering**
> + **category-level meta prompt bank**
> + **alternating assignment / update loop**
> + **hybrid task-record sidecar for tie-break, balance, and collapse diagnosis**

This directly optimizes for the thing we actually care about:

> **Which tasks should share the same meta skill prompt, and how should those prompts evolve over repeated loops?**
