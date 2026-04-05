# SkillX Pilot Assignment Pass v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-03
- **Role:** first runnable pilot for Meta-schema-bank clustering under Mark Auto Research
- **Status:** working MVP pilot spec

---

## 1. Purpose

This document defines the first pilot assignment pass before scaling to the full task × Meta-schema matrix.

The pilot has three jobs:
1. verify that the Meta-schema bank is operationally distinct enough to induce nontrivial assignments
2. verify that the score matrix / tie-break / artifact pipeline works end-to-end
3. detect early collapse or trivial near-tie behavior before paying for the full matrix

This pilot consumes:
- `docs/plans/skillx/skillx-prompt-bank-v0.1.md`
- `docs/plans/skillx/skillx-prompt-bank-v0.1.json`
- `docs/plans/skillx/skillx-render-template-frozen-v0.1.md`
- `docs/plans/skillx/skillx-assignment-matrix-protocol-v0.1.md`
- `docs/plans/skillx/skillx-outer-loop-update-protocol-v0.1.md`
- `docs/plans/skillx/skillx-pilot-round-0-manifest-v0.1.json`

---

## 2. Pilot philosophy

The first pilot should be:
- balanced across the seed categories
- high-confidence in task labeling
- cheap enough to run
- but broad enough to expose Meta-schema-bank weakness or collapse

So the pilot is intentionally staged:
- **Tier 1:** micro-pilot for infrastructure + obvious structure
- **Tier 2:** expanded class-balance pilot if Tier 1 looks nontrivial

---

## 3. Meta-schema bank used in the pilot

Use the 7-category Meta-schema bank as currently defined:
- artifact-generation
- analytic-pipeline
- engineering-composition
- retrieval-heavy-synthesis
- environment-control
- methodology-guardrail
- orchestration-delegation

If early dry inspection suggests two schemas are nearly identical, note that explicitly but still run the pilot once before merging.

---

## 4. Tier 1 micro-pilot task slice

Use one high-confidence representative task per category:

1. `offer-letter-generator` -> artifact-generation
2. `trend-anomaly-causal-inference` -> analytic-pipeline
3. `parallel-tfidf-search` -> engineering-composition
4. `enterprise-information-search` -> retrieval-heavy-synthesis
5. `adaptive-cruise-control` -> environment-control
6. `taxonomy-tree-merge` -> methodology-guardrail
7. `scheduling-email-assistant` -> orchestration-delegation

### Why this slice

This gives:
- one anchor task per schema
- strong semantic spread
- at least one known representative from each current seed category
- a small but meaningful `7 tasks × 7 schemas = 49 pair evaluations`

This is the cheapest pilot that can still expose:
- schema indistinguishability
- total collapse
- or a broken assignment pipeline

---

## 5. Tier 2 expanded class-balance slice

If Tier 1 produces nontrivial structure, expand to two tasks per category:

### artifact-generation
- `offer-letter-generator`
- `court-form-filling`

### analytic-pipeline
- `trend-anomaly-causal-inference`
- `flood-risk-analysis`

### engineering-composition
- `parallel-tfidf-search`
- `fix-build-agentops`

### retrieval-heavy-synthesis
- `enterprise-information-search`
- `gh-repo-analytics`

### environment-control
- `adaptive-cruise-control`
- `pddl-tpp-planning`

### methodology-guardrail
- `taxonomy-tree-merge`
- `citation-check`

### orchestration-delegation
- `scheduling-email-assistant`
- `pg-essay-to-audiobook`

This produces:
- `14 tasks × 7 schemas = 98 pair evaluations`

Use Tier 2 only after Tier 1 confirms that Meta-schema-induced assignment is at least somewhat informative.

---

## 6. Evaluation budget

## 6.1 Per-pair budget (pilot-light-v0)

For each `(task, schema)` pair, use:

```yaml
budget_profile: pilot-light-v0
inner_loop_system: Mark Auto Research
initial_pass_repeats: 1
repeat_policy:
  default_repeats: 1
  ambiguous_pair_extra_repeats: 1
  max_total_repeats_per_pair: 2
ambiguity_trigger:
  score_margin_lt: 0.05
```

Interpretation:
- first pass = one run per pair
- only rerun pairs when needed for ambiguity resolution
- do not burn repeats on obviously bad or obviously dominant pairs in the pilot

## 6.2 Budget discipline

All Meta-schema candidates in the same round must be run under the same per-pair budget profile.

If a task requires a special-case runtime policy, note it explicitly in the round manifest instead of silently changing the budget.

MVP simplification:
- the variable part across columns is the Meta schema
- the Render layer should stay fixed across the whole pilot round

---

## 7. Score matrix artifacts

The pilot should emit these concrete artifacts.

## 7.1 Score matrix CSV

Path suggestion:
- `docs/plans/skillx/pilot-round-0-score-matrix.csv`

Columns:

```text
round_id,task_name,schema_id,score,success,best_score,final_score,timeout_flag,invalid_output_flag,verifier_fail_flag,runtime_error_flag,notes
```

## 7.2 Assignment table CSV

Path suggestion:
- `docs/plans/skillx/pilot-round-0-assignments.csv`

Columns:

```text
round_id,task_name,assigned_schema,best_score,second_best_schema,second_best_score,margin,assignment_confidence,tie_break_used,tie_break_reason,semantic_prior_used,balance_adjust_used,previous_assignment_used
```

## 7.3 Round diagnostics JSON

Path suggestion:
- `docs/plans/skillx/pilot-round-0-diagnostics.json`

Fields:

```json
{
  "round_id": "pilot-round-0",
  "task_count": 0,
  "prompt_count": 0,
  "occupied_cluster_count": 0,
  "cluster_sizes": {},
  "largest_cluster_share": 0.0,
  "mean_assignment_margin": 0.0,
  "low_margin_task_fraction": 0.0,
  "collapse_warning": false,
  "notes": []
}
```

## 7.4 Meta-schema update summary

Path suggestion:
- `docs/plans/skillx/pilot-round-1-meta-schema-updates.md`

This should summarize, per category:
- support size
- common failures
- ambiguous competitors
- added / removed / sharpened Meta-schema guidance

---

## 8. Tie-break policy in the pilot

The pilot uses the same tie-break rule as the main spec, but it should be recorded very explicitly for debug purposes.

Order:
1. semantic prior
2. cluster balance soft preference
3. previous assignment stability (only in later rounds)
4. deterministic fallback

In round 0, there is no previous assignment, so only the first two are active before fallback.

---

## 9. Collapse checks for the pilot

The pilot should immediately flag any of the following:
- one schema wins nearly all tasks
- most tasks have margins `< 0.05`
- two or more schema columns are nearly indistinguishable by score profile
- methodology-guardrail and orchestration-delegation are effectively inseparable

If that happens, do **not** immediately treat it as failure.
Instead classify the result as one of:
- possible universal-protocol signal
- weak schema distinctness
- scoring too noisy / too flat
- task slice too easy or too small

---

## 10. Success criteria for moving past Tier 1

Advance to Tier 2 if most of the following hold:
- infrastructure works end-to-end
- score matrix is complete
- at least 3 schema categories receive tasks
- mean margin is not trivially near zero
- assignments are at least partly aligned with semantic intuition
- collapse, if present, looks interesting rather than obviously degenerate

If these do not hold, revise the Meta-schema bank before expanding.

---

## 11. Bottom line

The first runnable pilot is:
- **Tier 1:** 7 anchor tasks × 7 schemas = 49 pair evaluations
- **Tier 2:** 14 balanced tasks × 7 schemas = 98 pair evaluations

The goal is not benchmark scale yet.
The goal is to verify that Meta-schema-induced clustering is real enough to justify a larger outer-loop experiment.
