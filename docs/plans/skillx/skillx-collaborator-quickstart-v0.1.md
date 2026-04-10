# SkillX Collaborator Quickstart v0.1

This note is a short entry point for collaborators and future agents working on
the current SkillX line.

## 1. Start Here

If you only read one file first, read:

- `docs/plans/skillx/INDEX.md`

That is the canonical entry file for the current project documentation.

Recommended first read order:

1. `docs/plans/skillx/INDEX.md`
2. `docs/plans/skillx/skillx-project-tracker-v0.2.md`
3. `docs/plans/skillx/skillx-evaluator-in-the-loop-evaluation-protocol-v0.1.md`
4. `docs/plans/skillx/skillx-assignment-matrix-protocol-v0.1.md`
5. `docs/plans/skillx/skillx-outer-loop-update-protocol-v0.1.md`

If you want the shortest possible orientation:

- `INDEX.md` tells you what exists.
- `skillx-project-tracker-v0.2.md` tells you where the project is now.
- the protocol docs tell you how the current experiment is supposed to work.

## 2. How To Use The GitHub Project

We use the GitHub repo issues plus `SkillX-project` to track execution.

Basic rule:

- if a work item should be tracked, it should become a GitHub issue
- if the issue belongs to the current roadmap, it should also be added to the
  GitHub Project

When creating or updating an issue, use this structure:

1. `Motivation`
2. `Overall Goal`
3. `Current Status`
4. `Execution Checklist`
5. `Definition of Done`
6. `References` when useful

Please make `Definition of Done` explicit. For this project, success criteria
and evaluation criteria should be written down rather than implied.

Current project organization:

- `M1: Setting A to Round-1 E2E`
  current main execution line on the anchor benchmark
- `M2: Benchmark Expansion`
  validate SkillX on additional benchmark candidates
- `M3: Comparative Validation And Ablations`
  prior-baseline comparison plus ablation studies
- `M4: Paper Execution`
  paper planning, writing, and submission prep

Current project fields:

- `Priority`
- `Execution Order`
- `Status`

Please set those fields when adding an issue to the project.

## 3. Current Code And Experiment Status

The current development should be understood as two coupled parts:

### 3.1 Inner Loop

Status: `mostly implemented for the current SkillsBench line`

Current understanding:

- the inner-loop refine pipeline is the more mature part of the codebase
- on the current SkillsBench setup, the refine runner can complete a real
  `R0 -> R3` loop for a single `(task, schema)` pair
- the launcher and round-0 materialization flow already know how to call this
  runner repeatedly across `task x schema` pairs

Main code entry points:

- `scripts/run_skillx_refine_benchmark.py`
- `scripts/run_skillx_rewrite_benchmark.py`
- `scripts/launch_skillx_round0.py`

Important caveat:

- the current refine implementation is still primarily a `tune-side` loop
- real held-out execution is not yet fully connected in the current
  `run_skillx_refine_benchmark.py`

So the inner loop is usable for the current main experiment, but it is not yet
the final fully validated evaluation stack.

### 3.2 Outer Loop

Status: `partially specified, partially scaffolded, not yet fully run end to end`

Current understanding:

- the outer-loop design is documented clearly enough to support the current
  roadmap
- round-0 materialization already exists
- the project can already generate the `task x schema` pair specs and launch
  pair-level inner-loop runs
- however, the full outer-loop path has not yet been fully completed end to end
  on the current benchmark

In practice, this means:

- the protocol and artifacts are defined
- parts of the execution tooling are implemented
- but the full automatic path from:
  `round-0 matrix -> assignments -> diagnostics -> schema update -> round-1 rerun`
  is still the main unfinished system-level milestone

Main code / protocol files for this part:

- `scripts/materialize_skillx_round0_runner.py`
- `scripts/launch_skillx_round0.py`
- `docs/plans/skillx/skillx-assignment-matrix-protocol-v0.1.md`
- `docs/plans/skillx/skillx-outer-loop-update-protocol-v0.1.md`
- `docs/plans/skillx/skillx-meta-schema-update-operator-v0.1.md`
- `docs/plans/skillx/skillx-meta-schema-search-operator-v0.2.md`

So the short answer is:

- `Inner Loop`: relatively complete for current SkillsBench experimentation
- `Outer Loop`: not yet fully closed end to end

## 4. What To Read For Design vs Code

If you want the main design docs, start with:

- `docs/plans/skillx/INDEX.md`
- `docs/plans/skillx/skillx-project-tracker-v0.2.md`
- `docs/plans/skillx/skillx-prompt-bank-clustering-and-outer-loop-spec-v0.1.md`
- `docs/plans/skillx/skillx-render-template-frozen-v0.1.md`
- `docs/plans/skillx/skillx-evaluator-in-the-loop-evaluation-protocol-v0.1.md`
- `docs/plans/skillx/skillx-assignment-matrix-protocol-v0.1.md`
- `docs/plans/skillx/skillx-outer-loop-update-protocol-v0.1.md`

If you want the main code entry points, start with:

- `scripts/run_skillx_refine_benchmark.py`
- `scripts/launch_skillx_round0.py`
- `scripts/materialize_skillx_round0_runner.py`
- `scripts/run_skillx_rewrite_benchmark.py`

## 5. What To Read For Baselines And Benchmark Survey

For benchmark dataset selection and benchmark expansion, start with:

- `docs/plans/skillx/skillx-dataset-selection-note-v0.1.md`
- `docs/plans/skillx/skillsbench-benchmark-onboarding-note-v0.1.md`
- `docs/plans/skillx/swe-skills-bench-onboarding-note-v0.1.md`
- `docs/plans/skillx/skillcraft-onboarding-note-v0.1.md`

For current roadmap placement of those benchmarks, also read:

- `docs/plans/skillx/skillx-project-tracker-v0.2.md`

For baseline-method comparison:

- the project already tracks this as a roadmap item in GitHub Project
- the most relevant current issue is the prior-baseline comparison issue in
  `M3`
- there is not yet a dedicated standalone survey note for prior methods in the
  repo; this is still an open follow-up item

So for now:

- benchmark survey material is already documented in repo files
- prior-baseline comparison is mostly tracked in the roadmap / project layer,
  not yet in a dedicated literature-comparison memo

## 6. Short Practical Advice

- Start from `INDEX.md`.
- Use the GitHub Project for all non-trivial tracked work.
- Treat the current main goal as: finish the anchor benchmark end-to-end.
- Do not assume the outer loop is already fully automated just because the
  protocol docs exist.
- If in doubt, read the tracker first, then inspect the relevant script entry
  point.
