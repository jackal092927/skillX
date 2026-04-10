# Sonnet 4.5 Round-0 Candidate Slice v0.2

- baseline model: `Claude Code (Sonnet 4.5)`
- baseline condition: `With Skills`
- source cache: `official_task_results.jsonl`
- selection target: `20` tasks

## Selection Heuristic

1. prefer tasks with official `Sonnet 4.5 / With Skills < 100`
2. preserve seed-schema coverage
3. after coverage is satisfied, add tasks with lower `With Skills` scores and weaker
   or negative `No Skills -> With Skills` deltas before adding tasks that already
   benefited strongly from the official skill pack

## Selected Tasks

### analytic-pipeline

- `civ6-adjacency-optimizer` — `14.7`
- `earthquake-phase-association` — `20`
- `energy-ac-optimal-power-flow` — `20`
- `pdf-excel-diff` — `40`

### artifact-generation

- `court-form-filling` — `20`
- `syzkaller-ppdev-syzlang` — `20`
- `threejs-to-obj` — `60`
- `latex-formula-extraction` — `0`

### engineering-composition

- `setup-fuzzing-py` — `9.8`
- `find-topk-similiar-chemicals` — `10`
- `fix-erlang-ssh-cve` — `40`
- `parallel-tfidf-search` — `0`

### retrieval-heavy-synthesis

- `organize-messy-files` — `20`
- `travel-planning` — `20`
- `gh-repo-analytics` — `0`

### environment-control

- `pddl-tpp-planning` — `0`
- `glm-lake-mendota` — `80`
- `adaptive-cruise-control` — `0`

### methodology-guardrail

- `taxonomy-tree-merge` — `0`

### orchestration-delegation

- `pg-essay-to-audiobook` — `0`

## Added In v0.2

- `parallel-tfidf-search` — `60 -> 0` (`-60`)
- `pdf-excel-diff` — `80 -> 40` (`-40`)
- `adaptive-cruise-control` — `0 -> 0` (`0`)
- `gh-repo-analytics` — `0 -> 0` (`0`)
- `latex-formula-extraction` — `0 -> 0` (`0`)

## Notes

- `methodology-guardrail` currently has only one non-saturated official
  `Sonnet 4.5` task in the local cache.
- `orchestration-delegation` currently has only one non-saturated official
  `Sonnet 4.5` task in the local cache.
- This version prioritizes harder tasks with lower official `With Skills`
  performance or negative deltas, because the immediate goal is to maximize
  headroom for the first outer-loop iteration rather than mirror where the
  official skill pack already works well.
- This slice is intended for pilot round-0 prescan / outer-loop smoke testing,
  not as a fixed final benchmark subset.
