# SkillX Project Tracker v0.1

This document is the top-level tracker for the current SkillX research cycle.
Its purpose is to answer two questions quickly:

1. Where is the project in the overall research lifecycle?
2. What is the active execution sequence right now?

## Current Phase

Current milestone: `M1: Setting A to Round-1 E2E`

Current active step: `#2 [P0] Run Setting A round-0 matrix on the 20-task slice`

Current framing:

- Primary setting: `Setting A = oracle evaluator in the loop`
- Primary objective: run the first full `round-0 -> assignment -> round-1 update`
- Current experimental unit: `20 tasks x 7 schemas`
- Current default inner-loop budget: `R0 -> R3`

## Research Lifecycle

### Phase 0: Foundations And Protocol Freeze

Status: `Completed`

Includes:

- frozen prompt bank
- frozen render template
- official SkillsBench task-result cache
- 20-task pilot slice
- round-0 materializer and launcher
- evaluator-in-the-loop protocol
- single-pair smoke validation

### Phase 1: Setting A Round-0 Matrix

Status: `In Progress`

Primary issue:

- `#2` Run Setting A round-0 matrix on the 20-task slice

Goal:

- execute the full `20 x 7` matrix
- recover one selected incumbent per completed `(task, schema)` pair

### Phase 2: Assignment And Clustering Signal Extraction

Status: `Queued`

Primary issue:

- `#3` Build round-0 score matrix, assignments, and diagnostics

Goal:

- convert raw run outputs into `score matrix / assignment / diagnostics`
- determine whether schema specialization signal is already visible

### Phase 3: First Outer-Loop Update

Status: `Queued`

Primary issues:

- `#8` Package first-round schema updates from round-0 diagnostics
- `#9` Run reduced round-1 rerun and compare against round-0 incumbents
- `#7` Umbrella issue for the first real round-1 outer-loop pass

Goal:

- update a small number of schemas
- rerender and rerun a reduced slice
- verify whether outer-loop learning produces measurable improvement

### Phase 4: Supportive Validation

Status: `Queued`

Primary issues:

- `#4` Baselines: generic refine and universal schema
- `#5` Convergence and round-budget analysis

Goal:

- strengthen the claim that `schema specialization + assignment` adds value
- justify the default round budget with data rather than intuition

### Phase 5: Extension Track

Status: `Later`

Primary issue:

- `#6` Pilot Setting B with task-derived rubrics

Goal:

- test whether task-derived rubrics can approximate oracle-evaluator guidance

## Active Execution Sequence

The current mainline should be read in this order:

1. `#2` Run full Setting A round-0 matrix
2. `#3` Build score matrix, assignments, and diagnostics
3. `#8` Package first-round schema updates
4. `#9` Run reduced round-1 rerun and compare before/after
5. `#7` Close the first true outer-loop round-1 umbrella

This means the project is no longer in the “design only” stage. It is now in
the first real end-to-end execution stage.

## Current Success Criteria

The current research cycle should count as successful if all of the following
become true:

- the full `20 x 7` Setting A matrix is executed with auditable end states
- a structured `score matrix / assignment / diagnostics` package is produced
- at least one real schema-update pass is performed
- the round-1 rerun produces a clear before/after comparison
- we can state whether outer-loop specialization is learning anything useful

## Canonical Supporting Docs

- `skillx-evaluator-in-the-loop-evaluation-protocol-v0.1.md`
- `skillx-assignment-matrix-protocol-v0.1.md`
- `skillx-outer-loop-update-protocol-v0.1.md`
- `skillx-meta-schema-update-operator-v0.1.md`
- `skillx-meta-schema-search-operator-v0.2.md`

