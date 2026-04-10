# Checkpoint — 2026-04-08 — SkillX Round-0 Materialization State

Project: `projects/skillX`  
Date: 2026-04-08  
Status: executable outer-loop input checkpoint

## 1. What changed at this checkpoint

The project has moved one step past pure outer-loop protocol design.

At this checkpoint, the repo now contains:
- a local cache of official SkillsBench task-level results,
- a `Sonnet 4.5`-anchored round-0 candidate slice expanded to 20 tasks,
- a minimal round-0 materializer script,
- and a fully materialized `20 × 7 = 140` `(task, schema)` pair set ready to feed the existing refine runner.

This is therefore the first checkpoint where the outer-loop line has a concrete runnable input surface rather than only a frozen conceptual protocol.

---

## 2. Official baseline cache now exists locally

The repository now has a local cache for official SkillsBench task results under:

- `experiments/skillx-skillsbench-001/results/official-task-results/`

This cache includes:
- per-task JSON payloads,
- aggregate `jsonl`,
- aggregate `csv`,
- and a cache manifest.

Current cache coverage:
- attempted tasks: `89`
- tasks with extracted official results: `71`
- tasks still missing extracted results: `18`

Tracked baseline coverage at this checkpoint:
- `Claude Code (Sonnet 4.5) / With Skills`: `71`
- `Claude Code (Opus 4.6) / With Skills`: `71`

This closes an important practical gap:
- task selection for pilots no longer depends on repeated manual website inspection,
- and official baseline filtering can now be done locally.

---

## 3. Pilot task slice is now 20 tasks, not 7

The original documentation freeze still referenced a tiny 7-task micro-pilot.

At this checkpoint, the working round-0 pilot slice has been updated operationally to:

> **20 tasks × 7 schemas**

The current working task slice artifact is:

- `experiments/skillx-skillsbench-001/results/official-task-results/sonnet45-round0-candidate-slice-v0.2.json`
- `experiments/skillx-skillsbench-001/results/official-task-results/sonnet45-round0-candidate-slice-v0.2.md`

The current selection logic is intentionally **difficulty / headroom oriented**, not “where official skills already work” oriented.

That means added tasks now preferentially include:
- low `With Skills` score tasks,
- low `No Skills` score tasks,
- zero-delta tasks,
- and negative-delta tasks

because the immediate goal is to maximize room for improvement in the first outer-loop iteration.

Important examples now included for that reason:
- `parallel-tfidf-search`
- `pdf-excel-diff`
- `adaptive-cruise-control`
- `gh-repo-analytics`
- `latex-formula-extraction`

---

## 4. Round-0 materializer now exists

The repo now contains a dedicated materializer:

- `scripts/materialize_skillx_round0_runner.py`

Its role is deliberately narrow:

1. read the working task slice,
2. read the prompt bank,
3. read task-cluster sidecar inputs,
4. read official baseline scores,
5. load each task’s native SkillsBench `environment/skills` directory as the `C1` starting point,
6. render a task-specific Meta skill for every `(task, schema)` pair under the frozen Render contract,
7. emit pair specs and refine commands,
8. write a launch script for later execution.

This script does **not** replace the existing refine runner.

Instead, it turns the outer-loop state into concrete inputs for:

- `scripts/run_skillx_refine_benchmark.py`

This is the correct architectural split for the current stage:
- outer-loop materialization stays thin,
- inner-loop execution remains delegated to the already existing refine stack.

---

## 5. Fully materialized round-0 input bundle now exists

The real round-0 materialization output is now present at:

- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/`

This output contains:
- `manifest.json`
- `pair_specs.jsonl`
- `launch_round0.sh`
- one directory per `(task, schema)` pair containing:
  - `pair_spec.json`
  - `rendered_meta_skill.md`

Current verified materialization counts:
- task count: `20`
- schema count: `7`
- pair count: `140`
- round budget in generated commands: `3`

The launch commands are already wired to:
- the local SkillsBench root,
- the local Claude Code OAuth token path,
- the existing refine benchmark script,
- and each task’s native `C1` skillpack directory.

This means the repository now contains the first genuinely runnable outer-loop assignment-pass input bundle.

---

## 6. Important interpretation at this checkpoint

The project still has **not** completed a full pilot execution pass.

What now exists is:
- a frozen schema bank,
- a frozen render template,
- a curated 20-task pilot slice,
- a local official baseline cache,
- and a materialized `task × schema` execution surface.

What still does **not** exist yet:
- actual `140` refine runs completed,
- a real score matrix from those runs,
- assignments derived from those runs,
- diagnostics from those runs,
- outer-loop schema updates driven by those diagnostics.

So this checkpoint should be interpreted as:

> **execution readiness checkpoint**

not yet

> **outer-loop result checkpoint**

---

## 7. Most important files at this checkpoint

### Existing frozen outer-loop inputs
- `docs/plans/skillx/skillx-prompt-bank-v0.1.json`
- `docs/plans/skillx/skillx-render-template-frozen-v0.1.md`
- `docs/plans/skillx/skillsbench-task-cluster-inputs-v0.1.jsonl`

### New official baseline cache
- `scripts/cache_skillsbench_official_results.py`
- `tests/test_cache_skillsbench_official_results.py`
- `experiments/skillx-skillsbench-001/results/official-task-results/manifest.json`
- `experiments/skillx-skillsbench-001/results/official-task-results/official_task_results.jsonl`

### New task-slice working artifacts
- `experiments/skillx-skillsbench-001/results/official-task-results/sonnet45-round0-candidate-slice-v0.2.json`
- `experiments/skillx-skillsbench-001/results/official-task-results/sonnet45-round0-candidate-slice-v0.2.md`

### New outer-loop materialization layer
- `scripts/materialize_skillx_round0_runner.py`
- `tests/test_materialize_skillx_round0_runner.py`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/manifest.json`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/pair_specs.jsonl`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/launch_round0.sh`

---

## 8. Immediate next step after this checkpoint

The next practical step is no longer “design the outer-loop runner.”

That has now been done at a minimal but sufficient level.

The immediate next step is:

1. run a small smoke slice from the materialized bundle,
2. verify the real Docker + refine path from `C1` starting skills works under this new outer-loop wrapper,
3. then scale to broader pair execution.

Recommended first execution shape:
- `1 task × 7 schemas` or `3 tasks × 7 schemas`

before committing to the full `140`-pair pilot.
