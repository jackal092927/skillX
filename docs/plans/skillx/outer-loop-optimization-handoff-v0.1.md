# SkillX Outer-Loop Optimization Handoff v0.1

- project: `skillX`
- branch: `feat/2026-04-19-outer-loop-optimization`
- worktree: `.worktrees/feat/2026-04-19-outer-loop-optimization`
- purpose: turn the current round-0 / rerun evidence into a runnable outer-loop control plane

## 1. PM-Level Reading Of Current Results

### What the product already proved

1. SkillX is not blocked by the inner-loop idea anymore.
   We already have many real `(task, schema)` runs that finish end-to-end, and
   the rerun-recovery branch shows the Docker hardening is materially improving
   execution reliability.

2. "One universal schema for everything" is probably the wrong product shape.
   The data already shows different tasks behave differently under different
   schemas. That means routing and specialization are real opportunities, not
   just theory.

3. But specialization is not automatically good.
   `earthquake-phase-association` is the clearest warning sign: after the clean
   rerun, all `7/7` schema variants finished operationally but all stayed
   negative lift. Product meaning: for some task families, our current schema
   bank is not helping and may be actively mismatched.

### What the product has *not* proved yet

1. We have not yet shown that the outer loop can learn better schemas from the
   observed results.
2. We have not yet shown that the system can take round-0 evidence, update a
   subset of schemas, rerun a reduced slice, and improve performance.
3. We do not yet have a stable automatic path from raw run outputs to:
   - score matrix
   - assignment table
   - diagnostics package
   - schema-update package

### PM takeaway

The current product question is no longer:

> "Can the system run many schema-conditioned experiments?"

It is now:

> "Can the system decide when to specialize, when to hold steady, and how to
> update the schema bank without making things worse?"

That is exactly the outer-loop optimization problem.

## 2. Product Implications For Outer-Loop v1

The first outer-loop version should be conservative.

Recommended product principles:

- do not update all `7` schemas at once
- only update schemas with enough evidence support
- exclude infrastructure-corrupted rows from learning
- treat negative-lift families like `earthquake-phase-association` as special
  cases, not training signal to blindly absorb
- keep render frozen and update only schema-level guidance

The first good outer-loop win is not:

- "rewrite everything"

The first good outer-loop win is:

- "take reliable round-0 evidence"
- "choose 2-3 schemas worth updating"
- "make auditable changes"
- "show a small reduced rerun improves or clarifies behavior"

## 3. Current Progress Snapshot

### Implemented

- round-0 materialization
- launcher / dashboard / run recovery
- global pair status builder
- rerun-recovery selection and execution flow
- protocol docs for:
  - assignment
  - outer-loop update
  - schema-update operator
  - schema-search operator

### Still missing in executable form

- score-matrix builder from run artifacts
- assignment engine with margins / confidence / tie-breaks
- diagnostics emitter
- schema-update package generator
- reduced round-1 rerun constructor
- before/after comparator for round-1 vs round-0

Short version:

- data plane exists
- control plane is still mostly design-doc level

## 4. Repo Locations To Read First

- `docs/plans/skillx/skillx-assignment-matrix-protocol-v0.1.md`
- `docs/plans/skillx/skillx-outer-loop-update-protocol-v0.1.md`
- `docs/plans/skillx/skillx-meta-schema-update-operator-v0.1.md`
- `docs/plans/skillx/skillx-meta-schema-search-operator-v0.2.md`
- `docs/plans/skillx/skillx-project-tracker-v0.2.md`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/round0-40x7-summary-2026-04-12.md`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/global-round0-status/global_status_matrix.md`

Relevant issues:

- `#3` build score matrix / assignments / diagnostics
- `#7` outer-loop umbrella
- `#8` package first-round schema updates
- `#9` reduced round-1 rerun and comparison

## 5. Recommended Scope For This Branch

Primary goal:

- make outer-loop v1 executable, not just well-specified

Suggested implementation order:

1. build a programmatic score-matrix extractor from existing round-0 reports
2. emit assignment artifacts:
   - assignments csv/json
   - margins
   - confidence bands
   - tie-break fields
3. emit diagnostics:
   - low-margin tasks
   - empty / weak schemas
   - schema occupancy
   - collapse indicators
4. package first-round schema updates for a small subset of schemas
5. stop there unless time remains

Avoid trying to implement full round-1 rerun in the same first pass unless the
control-plane pieces above are already clean.

## 6. Non-Goals For The First Session

- do not rerun the big benchmark batches again
- do not redesign the full schema bank from scratch
- do not fold `earthquake` directly into generic schema updates
- do not broaden scope to benchmark-expansion or ablations

## 7. Success Criteria

This branch is successful if it leaves the repo with an auditable and runnable
outer-loop pipeline that can answer:

- which schema each task is currently assigned to
- how confident that assignment is
- which schemas are weak / ambiguous / collapsed
- which 2-3 schemas should be updated first

## 8. Session Bootstrap Prompt

```text
Work only in this worktree:
/Users/Jackal/iWorld/projects/skillX/.worktrees/feat/2026-04-19-outer-loop-optimization

Goal: make the SkillX outer-loop optimization path executable.

Read first:
- docs/plans/skillx/outer-loop-optimization-handoff-v0.1.md
- docs/plans/skillx/skillx-assignment-matrix-protocol-v0.1.md
- docs/plans/skillx/skillx-outer-loop-update-protocol-v0.1.md
- experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/round0-40x7-summary-2026-04-12.md
- experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/global-round0-status/global_status_matrix.md

Focus on the control plane, not more benchmark execution.

Target deliverables for this branch:
1. score matrix builder
2. assignment artifacts with margins/confidence
3. diagnostics package for weak / ambiguous / collapsed schemas
4. a small, auditable schema-update package proposal for 2-3 schemas

Do not expand scope to full round-1 rerun unless the control-plane pieces above are already in place and validated.
```
