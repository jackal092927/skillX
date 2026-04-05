# SkillX MVP Automatic Clustering Input Schema v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-02
- **Role:** supportive sidecar schema for clustering inputs in the SkillX / UltraLoop line
- **Status:** working MVP design

---

## 1. Why this document exists

This document remains useful, but its role has narrowed.

The newer MVP direction is now captured in:
- `docs/plans/skillx/skillx-prompt-bank-clustering-and-outer-loop-spec-v0.1.md`

That newer spec treats clustering as **Meta-schema-induced assignment**:
- maintain a bank of category-level Meta schemas,
- render task-specific Meta skills under a frozen Render layer,
- assign each task to the best-performing schema,
- optimize schemas,
- and re-assign iteratively.

Under that design, this document should be interpreted as the **supportive sidecar schema** for structured task records.

Its purpose is now to provide:
- semantic / contract priors,
- tool-topology priors,
- optimization-response summaries,
- and auxiliary audit features

for use in:
- Meta-schema-bank initialization,
- tie-breaking,
- balance support,
- collapse diagnosis,
- and post-hoc interpretation.

It should **not** be read as the primary clustering engine for the current MVP.

---

## 2. MVP design constraints

### 2.1 Flat clustering only

For the MVP, there is exactly **one clustering layer**.

We may still discuss subclusters in analysis notes, but they are:
- not runtime objects,
- not separate optimization objects,
- not separate cluster labels.

### 2.2 Manual label budget

The manually introduced clustering label space should remain **small**:
- target: **<= 10 labels**

Current practical choice:
- use the existing `task_object` space as the only manual seed label family
- keep it small and editable

### 2.3 Hybrid flat signals, not outcome-only signals

The clustering input should not be based on outcome curves alone.

For the MVP, the intended signal priority is:

1. **semantic / contract features** — what the task fundamentally asks the skill to do
2. **tool-topology features** — what workflow skeleton and tool coordination burden the task imposes
3. **optimization-response features** — how the task currently behaves under iterative rewrite / evaluation

Interpretation:
- the first two decide **what the Meta schema should contain**
- the third helps decide **how the Meta schema should be updated**

### 2.4 Fast end-to-end priority

The MVP objective is not the best possible ontology.
It is:
- get automatic clustering running,
- connect it to auto-loop optimization,
- and only then refine the representation.

So the MVP should prefer:
- a simple, inspectable feature set,
- auditable transformations,
- and a clustering result that is useful for optimization,

over elegant but overpowered representation learning.

---

## 3. What object should be clustered?

For the MVP, cluster **task-level aggregate records**, not raw runs.

That means the clustering unit is:

> one `task_cluster_record` per task, built from task-level semantic/topology descriptors plus aggregated run evidence under a fixed evaluation regime.

Why this unit?
- raw traces are too model- and runtime-dependent,
- individual runs are too noisy,
- but per-task aggregates are stable enough for a first automatic pass.

---

## 4. Clustering objective

The clustering objective is:

> group tasks that are likely to benefit from similar cluster-level rewrite guidance.

In the MVP, that means:
- **semantic / contract** features say what the skill must contain,
- **tool-topology** features say what workflow structure the skill must support,
- **optimization-response** features say where current rewriting fails or succeeds.

This is different from merely grouping tasks by subject matter or raw score similarity.

---

## 5. Input schema overview

Each clustering record has four parts:

1. **Identity fields** — bookkeeping only
2. **Primary input block A: semantic / contract features**
3. **Primary input block B: tool-topology features**
4. **Secondary input block: optimization-response features**
5. **Auxiliary audit tags** — interpretation aids only

---

## 6. Identity fields

```yaml
record_id: string                  # unique id for this task-level aggregate
benchmark: string                  # e.g. SkillsBench
task_name: string                  # canonical task slug
task_version: string | null        # optional task/repo version identifier
run_family_id: string              # identifies which runs were aggregated
model_family_set: [string]         # models appearing in aggregated runs
runtime_set: [string]              # runtimes/wrappers appearing in aggregated runs
support_runs: int                  # number of runs aggregated
support_rounds: int                # total rounds aggregated across runs
```

These fields are **not** clustering features by themselves, but they are needed for auditability and later normalization.

---

## 7. Primary input block A: semantic / contract features

These are the most important features for answering:

> **what kind of Meta-schema content should this task family want?**

### 7.1 Required MVP fields

```yaml
task_object_seed: string | null    # flat manual seed label; <=10 labels
verifier_mode: string | null       # correctness regime / output contract regime
```

Current role of these fields:
- `task_object_seed` gives a small interpretable semantic seed surface
- `verifier_mode` captures how correctness is enforced

Together, they approximate:
- what the task fundamentally is,
- and what “done correctly” means.

### 7.2 Optional future semantic additions (not required for MVP)

These can be added later if we want richer automatic extraction from task instructions:

```yaml
output_artifact_family: string | null
hard_constraint_family: string | null
requires_external_retrieval: bool | null
preservation_constraint_present: bool | null
```

These are deferred because they increase extraction burden and manual bias if added too early.

---

## 8. Primary input block B: tool-topology features

These are the most important features for answering:

> **what workflow skeleton should the Meta schema encourage?**

### 8.1 Required MVP fields

```yaml
workflow_topology: string | null
tool_surface_regime: string | null
```

Current role of these fields:
- `workflow_topology` captures shape:
  - single-step
  - staged multi-step
  - branching / abstention
  - multi-skill composition
- `tool_surface_regime` captures operating surface:
  - tool-light
  - tool-heavy-script-optional
  - tool-heavy-script-recommended
  - etc.

Together, they approximate:
- coordination burden,
- stage sensitivity,
- and how much the skill needs wrappers / stage contracts / explicit orchestration.

### 8.2 Optional future topology additions (not required for MVP)

```yaml
intermediate_artifact_required: bool | null
stage_count_bucket: string | null
multi_tool_coordination_burden: string | null
branching_required: bool | null
```

These should remain deferred until we have more evidence that the basic topology fields are not enough.

---

## 9. Secondary input block: optimization-response features

These features should **not** define the semantics of the cluster by themselves.
They are used to:
- refine grouping,
- detect false merges,
- detect optimization bottlenecks,
- and later guide cluster-level updates.

### 9.1 Outcome level

```yaml
success_rate: float                # fraction of runs reaching task success threshold
mean_score: float                  # average task score
score_std: float                   # score variance across aggregated runs
```

### 9.2 Improvement dynamics

```yaml
delta_r0_to_best: float            # best score minus initial score
delta_r0_to_last: float            # final score minus initial score
best_last_gap: float               # best score minus final score (instability proxy)
rounds_to_first_success: float     # normalized rounds until first success; 1.0 if never
```

### 9.3 Failure mixture

```yaml
timeout_rate: float                # share of runs/rounds ending in timeout-like failure
invalid_output_rate: float         # malformed / missing / schema-invalid output rate
verifier_fail_rate: float          # output produced but verifier/benchmark still fails
runtime_error_rate: float          # execution/build/tool/runtime crash-like failure rate
```

### 9.4 Budget / search pressure

```yaml
mean_round_budget_fraction_used: float   # average used_rounds / available_round_budget
```

Interpretation:
- semantic / contract + topology answer **what kind of prompt family this wants**
- response features answer **where current optimization is getting stuck**

---

## 10. Auxiliary audit tags

These fields are useful, but in the MVP they should be treated as:
- side information,
- audit metadata,
- dashboard filters,
- or ablation features.

They should **not** define a second clustering layer.

```yaml
primary_pattern: string | null
secondary_patterns: [string] | null
confidence: string | null
evidence_note: string | null
```

Recommended MVP usage:
- `primary_pattern` / `secondary_patterns` help explain cluster morphology after the fact
- `confidence` helps prioritize audit
- `evidence_note` helps humans inspect whether a cluster is semantically coherent

---

## 11. Explicitly excluded from MVP primary clustering input

Do **not** use these as primary clustering features in the MVP:

- raw tool-call order
- raw chain-of-thought / reasoning text
- prompt wording
- response verbosity
- token count by itself
- free-form trace embeddings without normalization
- manually authored subcluster ids

Reason:
- too model-dependent,
- too prompt-dependent,
- too easy to overfit,
- or too much manual inductive bias for the current benchmark size.

---

## 12. JSON schema sketch

```json
{
  "record_id": "skillsbench:parallel-tfidf-search:skillx-v0",
  "benchmark": "skillsbench",
  "task_name": "parallel-tfidf-search",
  "task_version": null,
  "run_family_id": "skillx-rewrite-benchmark-v0",
  "model_family_set": ["claude-sonnet-4.5"],
  "runtime_set": ["harbor-docker-claude-code"],
  "support_runs": 4,
  "support_rounds": 12,
  "cluster_inputs": {
    "semantic_contract": {
      "task_object_seed": "engineering-composition",
      "verifier_mode": "benchmark-threshold"
    },
    "tool_topology": {
      "workflow_topology": "multi-skill-composition",
      "tool_surface_regime": "tool-heavy-script-recommended"
    },
    "optimization_response": {
      "success_rate": 0.25,
      "mean_score": 0.33,
      "score_std": 0.41,
      "delta_r0_to_best": 1.0,
      "delta_r0_to_last": 0.0,
      "best_last_gap": 1.0,
      "rounds_to_first_success": 0.67,
      "timeout_rate": 0.25,
      "invalid_output_rate": 0.00,
      "verifier_fail_rate": 0.50,
      "runtime_error_rate": 0.00,
      "mean_round_budget_fraction_used": 1.0
    }
  },
  "tags": {
    "primary_pattern": "pipeline",
    "secondary_patterns": ["tool-wrapper", "reviewer"],
    "confidence": "high",
    "evidence_note": "bundle-style retrieval + execution task with benchmark gating"
  }
}
```

---

## 13. How to build the clustering matrix in the MVP

### 13.1 Build a hybrid flat matrix

The first automatic clustering pass should use a single flat vector composed of:

1. one-hot encoded **semantic / contract** features
2. one-hot encoded **tool-topology** features
3. normalized numeric **optimization-response** features

Conceptually:

```text
X_mvp = concat(
  one_hot(task_object_seed, verifier_mode),
  one_hot(workflow_topology, tool_surface_regime),
  zscore(success / improvement / failure / budget features)
)
```

### 13.2 Weighting rule

For the MVP, the first pass should bias slightly toward semantic/topology structure.

A simple initial rule:
- semantic / contract block weight = `1.0`
- tool-topology block weight = `1.0`
- optimization-response block weight = `0.5`

Reason:
- we do not want current noisy score curves to swamp the more semantically meaningful structure
- but we do want response signals to correct obviously bad merges

This weighting can be tuned later.

### 13.3 First clustering pass

Recommended MVP procedure:

1. aggregate per-task records
2. one-hot encode semantic/topology categorical fields
3. z-score normalize numeric response features
4. apply block weights
5. run a simple clustering baseline on the final flat matrix
6. compare resulting clusters against `task_object_seed` only as an audit, not as supervision
7. inspect whether clusters are:
   - interpretable,
   - not too tiny,
   - semantically coherent,
   - and useful for optimization grouping

### 13.4 Cluster-count rule

For the MVP:
- target **4–8 clusters**
- hard ceiling: **10**

If the clustering naturally wants more than 10 clusters, that is a sign the representation is too detailed for the benchmark size and should be simplified first.

---

## 14. Minimal algorithm recommendation

To keep the MVP simple and auditable:

### Recommended baseline
- hierarchical agglomerative clustering over the hybrid flat matrix

Why:
- easy to inspect
- easy to cut at different `k`
- works fine with one-hot + normalized numeric features
- no need to commit to latent representations yet

### Selection rule
Pick `k` by balancing:
- silhouette / compactness
- minimum cluster size
- interpretability
- and usefulness for later optimization

Not by fit metric alone.

---

## 15. How this connects to the outer loop

The output of MVP clustering should be:

```yaml
cluster_assignment:
  task_name: string
  cluster_id: string
  cluster_confidence: float
  nearest_neighbors: [task_name]
  audit_tags:
    task_object_seed: string | null
    verifier_mode: string | null
    workflow_topology: string | null
    tool_surface_regime: string | null
```

Then the outer loop uses clusters as the grouping object for:
- evidence aggregation,
- shared rewrite proposals,
- transfer experiments,
- and cluster-level optimization statistics.

The intended split of labor is:
- cluster semantics/topology decide **what kind of rewrite prior belongs here**
- response signals decide **what direction the next update should push**

This is enough to run a real end-to-end loop without introducing a second hierarchy.

---

## 16. What to defer until after MVP

Defer these until later:
- subcluster operationalization
- two-level hierarchy
- raw trajectory clustering
- trace embeddings as a primary clustering input
- model-family-normalized clustering corrections
- learned cluster routers
- cluster-specific MetaSkill harness objects

These may all become useful later.
But they are not required to prove the MVP loop.

---

## 17. Immediate next step

A first machine-readable seed artifact has now been materialized at:

- `docs/plans/skillx/skillsbench-task-cluster-inputs-v0.1.jsonl`

Current state of that artifact should now be interpreted as:
- one line per SkillsBench task (`89` records)
- semantic / contract seed fields populated
- tool-topology seed fields populated
- audit tags populated from the annotation sheet
- optimization-response slots present but still `null`

So the next concrete step is now:
- populate the optimization-response fields from real run / verifier aggregates,
- then run the first hybrid flat automatic clustering pass.

That JSONL artifact is now the handoff point between:
- the current annotation / analysis work,
- and the first automatic clustering pass.
