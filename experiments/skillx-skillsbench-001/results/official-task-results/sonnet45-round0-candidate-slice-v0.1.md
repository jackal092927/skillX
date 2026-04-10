# Sonnet 4.5 Round-0 Candidate Slice v0.1

- baseline model: `Claude Code (Sonnet 4.5)`
- baseline condition: `With Skills`
- source cache: `official_task_results.jsonl`
- selection target: `15` tasks

## Selection Heuristic

1. prefer tasks with official `Sonnet 4.5 / With Skills < 100`
2. preserve seed-schema coverage
3. avoid a slice made entirely of zero-score tasks when non-zero headroom
   examples exist

## Selected Tasks

### analytic-pipeline

- `civ6-adjacency-optimizer` — `14.7`
- `earthquake-phase-association` — `20`
- `energy-ac-optimal-power-flow` — `20`

### artifact-generation

- `court-form-filling` — `20`
- `syzkaller-ppdev-syzlang` — `20`
- `threejs-to-obj` — `60`

### engineering-composition

- `setup-fuzzing-py` — `9.8`
- `find-topk-similiar-chemicals` — `10`
- `fix-erlang-ssh-cve` — `40`

### retrieval-heavy-synthesis

- `organize-messy-files` — `20`
- `travel-planning` — `20`

### environment-control

- `pddl-tpp-planning` — `0`
- `glm-lake-mendota` — `80`

### methodology-guardrail

- `taxonomy-tree-merge` — `0`

### orchestration-delegation

- `pg-essay-to-audiobook` — `0`

## Notes

- `methodology-guardrail` currently has only one non-saturated official
  `Sonnet 4.5` task in the local cache.
- `orchestration-delegation` currently has only one non-saturated official
  `Sonnet 4.5` task in the local cache.
- This slice is intended for pilot round-0 prescan / outer-loop smoke testing,
  not as a fixed final benchmark subset.
