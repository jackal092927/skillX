# SkillX Meta-Schema Acceptance Scorecard v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-05
- **Role:** defines how to judge whether a proposed Meta-schema update or challenger should replace the incumbent
- **Status:** working MVP scorecard

---

## 1. Purpose

This document defines the acceptance rule for Meta-schema evolution.

It answers a practical question left open by both:
- `skillx-meta-schema-update-operator-v0.1.md`
- `skillx-meta-schema-search-operator-v0.2.md`

namely:

> **When a category produces a challenger Meta schema, what exactly counts as “better enough” to accept it?**

This scorecard is designed so that the system does **not**:
- accept trivial local gains that destroy bank diversity
- reject useful broader exploration only because it is not locally minimal
- confuse a weak collapse with a strong universal finding

---

## 2. Design goal

The acceptance rule should balance five things:

1. **utility**
   - does the challenger help on tasks that matter?
2. **boundary quality**
   - does it behave better on ambiguous / low-margin cases?
3. **distinctness**
   - does it remain meaningfully different from nearby schemas?
4. **diversity contribution**
   - does it preserve a non-trivial bank decomposition?
5. **search discipline**
   - is the change understandable and not just noisy drift?

So the scorecard is explicitly **not** just:
- highest local mean score wins

---

## 3. Objects compared

For one category, compare:

- **incumbent Meta schema**
- one or more **challenger Meta schemas**

A challenger may be:
- conservative
- exploratory
- differentiating

The scorecard should work for all three.

---

## 4. Required evidence bundle

Before scoring a challenger, collect at least:

```yaml
category_id: string
incumbent_version: string
challenger_version: string
support_size: int
assigned_task_results:
  - task_name: string
    incumbent_score: float
    challenger_score: float
borderline_task_results:
  - task_name: string
    incumbent_score: float
    challenger_score: float
    main_competing_schema: string
cross_schema_context:
  nearest_neighbor_schema_ids:
    - string
bank_state:
  occupied_cluster_count_before: int
  largest_cluster_share_before: float
  cluster_size_entropy_before: float
  occupied_cluster_count_after_est: int | null
  largest_cluster_share_after_est: float | null
  cluster_size_entropy_after_est: float | null
schema_diff_summary:
  added_items: [string]
  removed_items: [string]
  rewritten_items: [string]
  boundary_changes: [string]
  prompt_seed_change_summary: string
```

Without this bundle, the scorecard should be treated as incomplete.

---

## 5. Scorecard dimensions

Use five primary dimensions.
Each dimension is scored qualitatively first, then optionally mapped to a numeric band.

---

## 5.1 Dimension A — Assigned-task utility

Question:

> Does the challenger improve performance on the tasks currently assigned to this schema?

Minimum signals:
- mean assigned-task score difference
- median assigned-task score difference
- worst-case regression
- count of materially improved tasks

Suggested judgment bands:
- **A+** strong improvement with no serious regression
- **A** moderate improvement, regressions minor
- **B** roughly flat but not worse
- **C** mixed improvement/regression
- **D** net harmful on assigned tasks

Red flag:
- a challenger should almost never be accepted if it clearly harms assigned-task utility without compensating boundary or diversity gains

---

## 5.2 Dimension B — Boundary / low-margin behavior

Question:

> Does the challenger behave better on ambiguous tasks near category boundaries?

Minimum signals:
- mean score change on low-margin tasks
- wins on tasks previously lost to the nearest competing schema
- whether margin becomes clearer or flatter

Suggested judgment bands:
- **A+** clearly improves borderline discrimination
- **A** helps several boundary cases
- **B** neutral
- **C** slightly worse / noisier
- **D** destroys useful boundary structure

Why this matters:
- a schema that only improves easy in-cluster cases may still be a weak challenger if it becomes worse exactly where category identity matters

---

## 5.3 Dimension C — Distinctness preservation

Question:

> Does the challenger remain meaningfully distinct from neighboring schemas?

Evaluate on at least these dimensions:
1. primary optimization objective
2. default workflow bias
3. primary failure assumption
4. anti-goal
5. good-fit / bad-fit boundary

Suggested judgment bands:
- **A+** meaningfully sharper and more distinct
- **A** distinctness preserved or improved
- **B** still distinct enough
- **C** noticeable homogenization
- **D** nearly collapses into an existing schema

Important rule:
- local utility gains do **not** automatically justify erasing schema distinctness unless the broader bank evidence supports real universalization

---

## 5.4 Dimension D — Diversity contribution

Question:

> If this challenger becomes incumbent, does it help preserve a non-trivial decomposition of the task space?

This should look at bank-level effects, not only local category effects.

Useful signals:
- estimated effect on occupied cluster count
- effect on largest cluster share
- effect on cluster entropy
- effect on low-margin task fraction
- whether this challenger helps keep a meaningful neighboring category alive

Suggested judgment bands:
- **A+** clearly strengthens non-trivial structure
- **A** supports healthy diversity
- **B** roughly neutral
- **C** nudges toward weak collapse
- **D** strongly accelerates uninformative collapse

Important nuance:
- if the entire bank is converging for genuinely strong reasons, diversity loss may be acceptable
- this dimension is therefore not an absolute veto, but a strong caution axis

---

## 5.5 Dimension E — Search quality / interpretability

Question:

> Is the challenger a coherent policy improvement, or just noisy drift?

Look at:
- is the change interpretable?
- are added / removed items semantically motivated?
- does the rewritten `meta_prompt_seed` match the slot-level changes?
- is the challenger internally coherent?
- is the change size proportionate to the available evidence?

Suggested judgment bands:
- **A+** coherent, well-grounded, and clearly motivated
- **A** good quality update
- **B** acceptable but not elegant
- **C** noisy or weakly justified
- **D** drift / incoherence / overfit-like change

This dimension protects against accepting challengers that win by noise or accidental phrasing artifacts.

---

## 6. Special dimension for exploratory challengers

Exploratory challengers deserve one extra question:

> Even if the local gain is modest, does this challenger open a new useful search direction?

This matters because v0.2 explicitly values broader search and non-trivial exploration.

So exploratory challengers may be accepted under a different threshold if they:
- improve boundary behavior
- preserve distinctness
- increase bank diversity
- and create a clearly interpretable alternate schema direction

This should be tracked as:

```yaml
exploration_value: high | medium | low
```

---

## 7. Decision rule

After scoring A–E, choose one of five outcomes.

### 7.1 `accept_replace`
Use the challenger as the new incumbent.

Use when:
- assigned-task utility is clearly better
- boundary behavior is better or neutral
- distinctness is preserved
- diversity contribution is not harmful

### 7.2 `accept_branch`
Keep the incumbent, but also preserve the challenger as an active branch / challenger for the next round.

Use when:
- the challenger is promising
- but evidence is still too ambiguous for full replacement
- or it opens a valuable exploratory direction

This is especially appropriate for v0.2 exploratory challengers.

### 7.3 `accept_soft_merge_signal`
Do not replace immediately, but record that the challenger suggests this schema may be converging toward a merge with a neighbor.

Use when:
- local gain exists
- but distinctness drops materially
- and bank-level evidence suggests possible genuine simplification

This does **not** mean merge now.
It means “watch this carefully.”

### 7.4 `hold_incumbent`
Keep the incumbent and reject the challenger for now.

Use when:
- gains are too small
- evidence is too weak
- or the challenger causes too much ambiguity

### 7.5 `reject_collapse`
Explicitly reject the challenger because it appears to improve only by washing out schema identity and accelerating uninformative collapse.

Use when:
- local score gain is weak or narrow
- and distinctness/diversity damage is strong
- and the bank is not yet in a convincingly universal regime

---

## 8. Minimal acceptance thresholds

A practical MVP threshold set:

### Replace immediately only if all are true:
1. Assigned-task utility >= **A**
2. Boundary behavior >= **B**
3. Distinctness >= **B**
4. Diversity contribution >= **C**
5. Search quality >= **B**

### Keep as branch if:
- utility is mixed but exploratory value is high
- or boundary improvement is strong but support size is still small
- or distinctness is improved but mean score gain is not yet stable

### Reject if any are true:
- distinctness = **D** and utility gain is not overwhelming
- diversity contribution = **D** without strong universal-bank evidence
- search quality = **D**
- support size too small and change too large

---

## 9. Weak collapse vs strong collapse

The scorecard must explicitly distinguish these two cases.

## 9.1 Weak collapse

Treat collapse as weak / uninformative if:
- search space was tiny
- challenger diversity was low
- bank entries were already too similar
- margins are low everywhere
- universal baseline `U0` is not clearly beaten

In this regime, challengers that homogenize the bank should usually be rejected or only soft-accepted.

## 9.2 Strong collapse

Treat collapse as potentially meaningful if:
- challenger search was already broad
- distinct exploratory variants were tried
- margins are not just low everywhere but actually favor one schema robustly
- the dominant schema beats `U0`
- the bank keeps collapsing even after diversity-preserving search

In that case, a converged universal protocol may actually be the result.

---

## 10. Numeric scaffold (optional)

If we want a lightweight numeric overlay, use:

```yaml
utility_weight: 0.35
boundary_weight: 0.20
distinctness_weight: 0.20
diversity_weight: 0.15
search_quality_weight: 0.10
```

But this should remain secondary.

Why:
- the scorecard is fundamentally a structured judgment rule
- a crude weighted sum should support decisions, not replace them

If a numeric score is used, call it:

```text
acceptance_index
```

and always log the per-dimension grades alongside it.

---

## 11. Acceptance artifact

Every challenger decision should emit:

```yaml
category_id: string
incumbent_version: string
challenger_version: string
challenger_type: conservative | exploratory | differentiating
support_size: int
scores:
  assigned_task_utility: A+|A|B|C|D
  boundary_behavior: A+|A|B|C|D
  distinctness_preservation: A+|A|B|C|D
  diversity_contribution: A+|A|B|C|D
  search_quality: A+|A|B|C|D
exploration_value: high | medium | low | n/a
decision: accept_replace | accept_branch | accept_soft_merge_signal | hold_incumbent | reject_collapse
decision_rationale:
  - string
notes:
  - string
```

This gives us a durable audit trail for why a schema changed or did not change.

---

## 12. Recommended first use with v0.2

For the first runnable v0.2-style loop, do not score an unlimited number of challengers.

Use:
- 1 incumbent
- 1 conservative challenger
- 1 exploratory challenger
- 1 differentiating challenger

Then apply this scorecard after each round.

This is enough to test whether broader search actually helps without exploding compute.

---

## 13. Relationship to existing docs

This scorecard should be used by:
- `docs/plans/skillx/skillx-meta-schema-search-operator-v0.2.md`
- `docs/plans/skillx/skillx-meta-schema-update-operator-v0.1.md`
- `docs/plans/skillx/skillx-outer-loop-update-protocol-v0.1.md`
- future runner logic for schema challenger selection

It should also inform pilot diagnostics once the first real challenger-based rounds exist.

---

## 14. Final practical rule

If there is any doubt, prefer this order of interpretation:

1. **Does the challenger really help on important tasks?**
2. **Does it improve boundary behavior?**
3. **Does it stay meaningfully distinct?**
4. **Does it help preserve a non-trivial bank?**
5. **Is it a coherent change rather than random drift?**

That order gives the right MVP bias:
- empirical performance first,
- but not at the cost of turning the whole bank into one noisy or trivial schema.
