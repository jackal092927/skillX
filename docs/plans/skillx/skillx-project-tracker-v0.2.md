# SkillX Project Tracker v0.2

This document is the top-level roadmap and progress tracker for the current
SkillX research cycle.

Its purpose is to answer three questions quickly:

1. What is the main scientific claim we are trying to validate?
2. Where are we in the overall research lifecycle?
3. What is the active execution sequence right now?

## North-Star Validation Question

The main near-term SkillX question is:

> Can the full SkillX pipeline, including the inner loop, the outer loop, and
> the adaptive clustering / schema-assignment layer, produce a larger aggregate
> improvement in skill performance on benchmark tasks?

This should be validated first on the current anchor benchmark, and only then
expanded to additional benchmark families.

## Current Position

Current milestone: `M1: Setting A to Round-1 E2E`

Current benchmark anchor: `SkillsBench`

Current active step: `#2 [P0] Run Setting A round-0 matrix on the 20-task slice`

Current framing:

- Primary setting: `Setting A = oracle evaluator in the loop`
- Primary benchmark objective: demonstrate that the full SkillX pipeline can
  improve benchmark-level skill delta on the current dataset
- Current experimental unit: `20 tasks x 7 schemas`
- Current default inner-loop budget: `R0 -> R3`
- Current execution focus: end-to-end benchmark validation, not paper
  polishing and not Setting B

## High-Level Research Roadmap

### Stage 0: Foundations And Protocol Freeze

Status: `Completed`

What this stage established:

- frozen prompt bank
- frozen render template
- official SkillsBench task-result cache
- 20-task pilot slice
- round-0 materializer and launcher
- evaluator-in-the-loop protocol
- first single-pair smoke validation

This stage answered:

- can the infrastructure run?
- can a single `(task, schema)` pair complete a full inner loop?

### Stage 1: Primary Benchmark End-to-End Validation

Status: `In Progress`

Primary benchmark:

- `SkillsBench`

Primary issues:

- `#2` Run full Setting A round-0 matrix
- `#3` Build score matrix / assignments / diagnostics
- `#8` Package first-round schema updates
- `#9` Run reduced round-1 rerun and compare before/after
- `#7` Close the first true outer-loop round-1 umbrella

Scientific objective:

- validate that the full SkillX pipeline, including inner loop, outer loop, and
  adaptive task-schema assignment, can improve benchmark-level skill utility on
  the current anchor dataset

This is the most important current work.

### Stage 2: Benchmark Expansion

Status: `Planned`

High-level objective:

- after the current benchmark is running end to end, expand the same proof line
  to at least two additional benchmark candidates

Current near-term candidate set from the latest benchmark-selection notes:

- `SWE-Skills-Bench` as the most natural second native benchmark
- one additional benchmark from the current shortlist, most likely:
  - `AppWorld` as the first adapted benchmark candidate, or
  - `SkillCraft` as the later bridge benchmark if we want a stronger
    composition / internalization-oriented extension

What is already decided:

- `SkillsBench` remains the anchor benchmark
- `SWE-Skills-Bench` is the preferred immediate secondary line

What is not fully frozen yet:

- the exact identity of the second extra benchmark beyond `SWE-Skills-Bench`
- the exact order of `AppWorld` versus `SkillCraft`

### Stage 3: Comparative Validation

Status: `Planned`

High-level objective:

- compare SkillX against previously published or closely related skill-evolution
  baselines

Current comparison target family:

- evolver-style or memory-evolver-style baselines such as `SkillEvolved`,
  `MemoryEvolved`, or the closest practically runnable analogue

Important note:

- exact baseline mapping still needs implementation-level clarification
- the goal is not name matching, but a credible comparison against the nearest
  prior method family

### Stage 4: Ablation And Mechanism Validation

Status: `Planned`

High-level objective:

- isolate which parts of SkillX actually matter

Likely ablation families:

- inner loop only vs full pipeline
- fixed schema vs adaptive schema assignment
- no outer loop vs one outer-loop update
- universal schema vs specialized schema bank
- round-budget sensitivity
- clustering / assignment update choices

This stage should answer:

- where the gains come from
- whether adaptive clustering and schema specialization are carrying real signal

### Stage 5: Paper Execution

Status: `Planned`

High-level objective:

- once the experimental story is coherent, convert it into a paper package

Main subgoals:

- freeze the claim set
- finalize figures / tables / benchmark comparisons / ablations
- write the paper
- complete submission

This stage should only start after the experiment story is stable enough.

## Current Mainline Execution Sequence

The current benchmark-validation mainline should be read in this order:

1. `#2` Run full Setting A round-0 matrix on the current benchmark slice
2. `#3` Build score matrix, assignments, and diagnostics
3. `#8` Package first-round schema updates
4. `#9` Run reduced round-1 rerun and compare before/after
5. `#7` Close the first true outer-loop round-1 umbrella

This is the current critical path because it is the first point where SkillX
can prove the full benchmark-level story rather than only isolated components.

## Current Success Criteria

### Stage-1 success

The current stage should count as successful if all of the following become
true on the current benchmark:

- the full `20 x 7` Setting A matrix is executed with auditable end states
- a structured `score matrix / assignment / diagnostics` package is produced
- at least one real schema-update pass is performed
- a reduced round-1 rerun produces a clear before/after comparison
- we can state whether the full SkillX pipeline improves benchmark-level skill
  utility on the anchor dataset

### Program-level success

The overall research cycle should count as successful if all of the following
become true:

- the current anchor benchmark story is validated end to end
- the result generalizes to at least two additional benchmark candidates
- SkillX is compared against credible prior or nearest-neighbor baselines
- the core pipeline is supported by targeted ablations
- the resulting evidence is strong enough to support a paper submission

## Open Decisions

The following items are still intentionally open:

- which benchmark becomes the second extra benchmark after
  `SWE-Skills-Bench`
- which prior baseline family is the fairest implementation-level comparison
- which ablations are mandatory versus optional
- exact paper target and submission timing

These are follow-up design decisions, not blockers for the current `Stage 1`
execution.

## Canonical Supporting Docs

- `skillx-evaluator-in-the-loop-evaluation-protocol-v0.1.md`
- `skillx-assignment-matrix-protocol-v0.1.md`
- `skillx-outer-loop-update-protocol-v0.1.md`
- `skillx-meta-schema-update-operator-v0.1.md`
- `skillx-meta-schema-search-operator-v0.2.md`
- `skillx-dataset-selection-note-v0.1.md`
- `skillsbench-benchmark-onboarding-note-v0.1.md`
- `swe-skills-bench-onboarding-note-v0.1.md`
- `skillcraft-onboarding-note-v0.1.md`
