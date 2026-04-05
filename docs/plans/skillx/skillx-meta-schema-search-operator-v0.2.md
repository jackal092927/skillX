# SkillX Meta-Schema Search Operator v0.2

- **Project:** `projects/skillX`
- **Date:** 2026-04-05
- **Role:** broadened Meta-schema search operator that preserves schema structure while expanding the searchable meta-item pool
- **Status:** exploratory successor / candidate upgrade to v0.1

---

## 1. Why v0.2 exists

`skillx-meta-schema-update-operator-v0.1.md` intentionally defined a conservative MVP:
- fixed schema shape
- slot-first editing
- constrained local edits
- frozen Render

That version is useful for clarity and attribution.

However, Xin raised a valid concern:

> if the Meta-schema search space is too small, then with only ~7 categories the system may converge too quickly,
> collapse for uninteresting reasons,
> and produce a result that is trivial rather than meaningful.

So v0.2 changes the search stance.

The goal is now:

> **keep the Meta schema structured enough to stay interpretable, but enlarge the searchable semantic pool enough to avoid trivial convergence.**

This document therefore treats Meta-schema optimization less like tiny checklist repair and more like:

> **bounded, diversity-preserving search over semi-structured class-level policy objects**

---

## 2. Core change from v0.1

## 2.1 v0.1 stance

v0.1 effectively said:
- keep schema shape fixed
- edit mostly within existing slots
- prefer small local edits
- regenerate `meta_prompt_seed`

## 2.2 v0.2 stance

v0.2 says:
- keep the **top-level schema structure** mostly stable
- but allow the **semantic item pool inside that structure** to expand, contract, and recombine more freely
- allow both conservative and exploratory schema proposals
- explicitly preserve schema diversity as an optimization objective

So the new stance is:

> **freeze Render, but do not over-freeze Meta-schema content.**

---

## 3. What stays fixed vs what becomes more open

## 3.1 Still fixed in MVP

These should remain fixed:
- Render
- wrapper
- output contract
- runner I/O shape
- category count ceiling (`K <= 10`)
- core identity of categories as class-level objects

These are the controls that make results interpretable.

## 3.2 No longer over-restricted

These should become more open:
- which semantic items appear in each slot
- how large each slot’s candidate pool may become
- whether a schema adds new semantically relevant guidance items
- whether a schema drops stale items entirely
- how aggressively `meta_prompt_seed` can be rewritten to reflect the updated policy
- whether challengers can differ substantially from incumbents

So the main relaxation is not “let Render drift.”
It is:

> **let Meta schemas explore a larger but still relevant semantic search space.**

---

## 4. Object model in v0.2

The main new idea is to separate three things:

1. **schema structure**
2. **active schema content**
3. **candidate meta-item pool**

## 4.1 Schema structure

The outer shape remains recognizable:

```yaml
category_id: string
version: string
semantic_intent: string
emphasize: [string]
avoid: [string]
expected_good_fit: [string]
expected_bad_fit: [string]
hypothesized_primary_failure_modes: [string]
seed_rationale: string
meta_prompt_seed: |
  ...
```

This is still useful because it keeps the object interpretable and compatible with the frozen Render template.

## 4.2 Active schema content

This is the currently selected content inside those fields.

Example:
- current `emphasize` items
- current `avoid` items
- current fit boundary
- current failure hypotheses

## 4.3 Candidate meta-item pool

This is the important new piece.

Each schema should now have access to a **larger candidate pool** of semantically relevant meta items, not just its currently active items.

Conceptually:

```yaml
meta_item_pool:
  emphasize_candidates: [item]
  avoid_candidates: [item]
  good_fit_candidates: [item]
  bad_fit_candidates: [item]
  failure_mode_candidates: [item]
```

The active schema is a selected realization from that larger pool.

This means the search space is not limited to:
- tweaking the current few items already visible in the schema

but can also include:
- activating new items
- deactivating old items
- rewriting item phrasing
- splitting an item into two
- merging redundant items

---

## 5. What counts as a “meta item”

A meta item should be something semantically relevant to class-level rewrite behavior.

Allowed item families include:

### 5.1 Objective / emphasis items
Examples:
- preserve exact artifact contract
- strengthen stage handoff integrity
- enforce diagnose-before-edit
- keep evidence provenance explicit
- use abstain behavior when unsupported

### 5.2 Anti-goal / avoid items
Examples:
- avoid speculative filling
- avoid collapsing stages into vague prose
- avoid unordered execution bundles
- avoid unsupported synthesis
- avoid over-scaffolding simple tasks

### 5.3 Fit boundary items
Examples:
- good fit for strict artifact transformation
- bad fit for simulator/control loops
- good fit for benchmark-gated code repair
- bad fit for deep retrieval-heavy synthesis

### 5.4 Failure hypothesis items
Examples:
- stage-handoff-break
- precedence-conflict
- placeholder-invention
- premature-commitment
- evidence-loss-under-compression

### 5.5 Optional workflow-bias items
If needed, the pool may also carry semantically adjacent items like:
- prefer short exact workflow
- prefer staged decomposition
- require explicit verification gate
- require evidence check before answer

These are allowed **only if they remain clearly relevant to task-class rewrite behavior**.

---

## 6. Scope rule: how the search space may expand without becoming junk

Xin’s suggestion is not to introduce arbitrary unrelated variables.
That is correct.

So v0.2 should follow this rule:

> **Expand the meta-item pool, but only with semantically adjacent items that plausibly affect class-level rewrite behavior.**

That means:
- yes: add richer failure-mode hypotheses, workflow-bias items, fit-boundary items, verification-bias items
- no: introduce unrelated environment knobs, random style preferences, or variables that are not meaningfully tied to the category’s rewrite prior

The expansion should be:
- **broader**, not **arbitrary**

---

## 7. Sources for expanding the meta-item pool

New candidate items should come from interpretable sources.

## 7.1 Assigned-task evidence

When many assigned tasks fail in a similar way, generate new candidate items from the shared pattern.

Example:
- repeated loss due to unsupported synthesis
  -> add candidate avoid item: `avoid unsupported synthesis without explicit evidence support`

## 7.2 Borderline / competing-schema evidence

When tasks are frequently low-margin between two schemas, candidate items can be generated to sharpen distinctness.

Example:
- a retrieval schema repeatedly loses to analytic-pipeline on stage-heavy evidence tasks
  -> add candidate emphasize item around staged evidence processing
  -> or add candidate bad-fit boundary saying pure retrieval schema should not absorb strongly stage-dependent analysis tasks

## 7.3 Cross-schema borrowing

A schema may borrow and adapt items from another schema’s pool.

Example:
- engineering-composition might borrow a stricter reviewer-style verification item
- methodology-guardrail might borrow a more explicit abstention trigger from retrieval-heavy-synthesis

Borrowing is allowed because it expands the search space without inventing unrelated concepts.

## 7.4 Human / literature priors

Seed additions may also come from:
- Anthropic / Google / SkillX prior analyses
- class-level representative task reads
- explicit human design suggestions from Xin

These should be treated as candidate items, not forced truths.

---

## 8. Search mode: incumbent + challengers

v0.2 should not update each schema by producing only one next version.

Instead, each schema should maintain:

```yaml
incumbent_schema: object
challenger_schemas:
  - object
  - object
  - object
```

Recommended challenger families:

### 8.1 Conservative challenger
- small local cleanup
- low risk
- good for exploitation

### 8.2 Exploratory challenger
- larger change to slot contents or item activation
- allowed to change semantic emphasis more aggressively
- good for expanding search

### 8.3 Differentiating challenger
- explicitly optimized to increase distance from the most confusable neighboring schema
- good for anti-collapse / anti-homogenization

So each category is no longer updated by a single deterministic patch.
It is updated by **competition among candidate schema variants**.

---

## 9. Allowed operator set in v0.2

v0.1 operators are still allowed, but v0.2 adds broader search operators.

## 9.1 Pool-expansion operators

### `add_candidate_item(slot, item, source)`
Add a new semantically relevant candidate to the pool.

### `retire_candidate_item(slot, item)`
Remove a candidate that never helps or is clearly redundant.

### `borrow_candidate_item(from_schema, to_schema, slot, item)`
Copy/adapt a semantically relevant item from another schema’s pool.

## 9.2 Activation operators

### `activate_item(slot, item)`
Move a candidate into the active schema.

### `deactivate_item(slot, item)`
Remove an active item from the current schema body.

### `swap_item(slot, item_out, item_in)`
Replace an active item with another candidate from the pool.

## 9.3 Restructuring operators

### `split_item(slot, item, item_a, item_b)`
Split a vague item into two sharper ones.

### `merge_items(slot, item_a, item_b, merged_item)`
Merge redundant items.

### `rewrite_item(slot, old, new)`
Rewrite an item more freely than v0.1 allowed.

## 9.4 Boundary operators

### `expand_schema_scope(boundary_item)`
Allow the schema to try covering a broader region.

### `shrink_schema_scope(boundary_item)`
Narrow the schema to preserve distinctness.

## 9.5 Realization operator

### `rewrite_meta_prompt_seed(mode)`
Regenerate the textual seed guidance.

Modes may include:
- conservative
- exploratory
- differentiating

Unlike v0.1, this rewrite may be more substantial, as long as it still reflects the current active schema content.

---

## 10. Diversity is now an explicit optimization goal

v0.2 should optimize not only for local score.
It should also optimize for:

1. schema usefulness
2. schema distinctness
3. non-trivial bank occupancy
4. non-flat assignment margins

So the objective is no longer just:
- improve the assigned-task score for each schema

It is now:

> **improve score while preserving enough diversity that the bank remains an informative decomposition of the task space**

---

## 11. New collapse interpretation rule

In v0.2, collapse should be interpreted against the actual search-space size.

### 11.1 Weak-collapse case
If collapse occurs under a tiny and overly restricted search space, the result is weak evidence.

### 11.2 Strong-collapse case
If collapse still occurs after:
- pool expansion
- challenger competition
- differentiating proposals
- and broader schema exploration

then collapse becomes much more meaningful.

So v0.2 gives us a better empirical test:

> **Did the bank collapse because the problem truly has a universal protocol, or because we gave it too little room to differentiate?**

---

## 12. Recommended search loop

For each outer-loop round:

### Step 1 — assignment
Evaluate tasks under current incumbent schemas using frozen Render.

### Step 2 — evidence aggregation
Summarize:
- wins
- losses
- low-margin cases
- competitor schemas
- repeated failure families
- cluster occupancy / entropy / margins

### Step 3 — candidate-pool expansion
For each schema, generate new candidate items where needed.

### Step 4 — challenger construction
Construct at least:
- one conservative challenger
- one exploratory challenger
- one differentiating challenger

### Step 5 — challenger evaluation
Evaluate challengers on:
- assigned tasks
- borderline tasks
- confusable neighboring tasks

### Step 6 — selection
Choose the next incumbent using a scorecard that combines:
- local task performance
- boundary performance
- distinctness preservation
- anti-collapse value

### Step 7 — rerender and continue
Keep Render frozen, rerender task-specific Meta skills from the selected incumbent schemas, and run the next outer-loop round.

---

## 13. Minimal scorecard for selecting the next incumbent

A challenger should not win just because it improves one score on one task.

Use at least these dimensions:

### 13.1 Utility
- mean score on assigned tasks
- best/worst-case score shift

### 13.2 Boundary behavior
- performance on low-margin tasks
- ability to beat or separate from the main confusable neighbor

### 13.3 Distinctness
- difference in active item set
- difference in failure assumptions
- difference in workflow bias
- prompt-text similarity not too high

### 13.4 Diversity contribution
- does this challenger help preserve non-trivial occupied clusters?
- or does it collapse into an already dominant schema without strong justification?

---

## 14. Answer to Xin’s “pool expansion” idea

Yes — the Meta schema can and should be viewed as defining the broad scope of the search space.

But that does **not** mean we should only permute the currently visible items already present in the schema.

The better interpretation is:

> the schema structure defines the search *container*,
> while the meta-item pool inside that container can expand, contract, and recombine.

So the search is not merely:
- try permutations of the initial visible items

It can also be:
- add new semantically relevant items
- remove stale ones
- move category boundaries
- generate more diverse schema challengers

This is the main reason v0.2 should be more expressive than v0.1.

---

## 15. Relationship to v0.1

v0.1 remains useful as a conservative baseline.

- **v0.1** = constrained local schema editing baseline
- **v0.2** = broader Meta-schema search operator with expandable semantic pools and challenger competition

This is the right relationship.
We do not need to delete v0.1.
We can compare:
- whether v0.1 converges too quickly
- whether v0.2 preserves more interesting schema diversity
- whether any apparent collapse remains meaningful after broader search

---

## 16. Practical recommendation

For the next experimental phase, do **not** immediately expand category count.

First try:
- same 7 top-level categories
- broader internal schema search per category
- challenger competition
- explicit anti-collapse diversity pressure

If the bank still collapses or becomes trivial, then we will know much more.
That result will be stronger than collapse under a tiny restricted search space.

---

## 17. Immediate next use

This document should be used to revise or extend:
- `docs/plans/skillx/skillx-outer-loop-update-protocol-v0.1.md`
- future pilot runner / update logic
- any acceptance scorecard for schema revisions

Most immediate follow-up:
1. ✅ wrote a **Meta-schema acceptance scorecard**:
   - `docs/plans/skillx/skillx-meta-schema-acceptance-scorecard-v0.1.md`
2. define how challenger schemas are serialized / compared
3. decide whether the first runner should support only `incumbent + 1 challenger` or full `incumbent + 3 challengers`
