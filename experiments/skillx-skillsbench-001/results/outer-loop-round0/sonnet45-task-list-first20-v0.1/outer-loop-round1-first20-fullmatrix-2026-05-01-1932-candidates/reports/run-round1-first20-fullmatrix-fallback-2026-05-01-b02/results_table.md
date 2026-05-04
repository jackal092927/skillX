# SkillX Round0 Result Table: `run-round1-first20-fullmatrix-fallback-2026-05-01-b02`

- tasks: `adaptive-cruise-control, civ6-adjacency-optimizer, data-to-d3, econ-detrending-correlation, exceltable-in-ppt, find-topk-similiar-chemicals, fix-druid-loophole-cve`
- pairs: `49/49` completed
- succeeded: `48`
- failed: `1`
- started_at: `2026-05-04T13:13:16.824010+00:00`
- finished_at: `2026-05-04T13:13:17.314962+00:00`
- duration_sec: `0.491`

## adaptive-cruise-control

| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Evidence | Early Stop | Timeout |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- |
| artifact-generation | succeeded | 0 | completed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | 0.0 | 0.0 | measured | no | no |
| analytic-pipeline | succeeded | 0 | completed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | 0.0 | 0.0 | measured | no | no |
| engineering-composition | succeeded | 0 | completed | 0.0 | 0.0 | 0.0 | 100.0 | 100.0 | 100.0 | R1 (100.0) | 100.0 | 100.0 | measured | no | no |
| retrieval-heavy-synthesis | failed | 1 | failed | 0.0 | 0.0 | - | - | - | - | - | - | - | runtime-blocked | no | no |
| environment-control | succeeded | 0 | completed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | 0.0 | 0.0 | measured | no | no |
| methodology-guardrail | succeeded | 0 | completed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | 0.0 | 0.0 | measured | no | no |
| orchestration-delegation | succeeded | 0 | completed | 0.0 | 0.0 | 0.0 | 100.0 | 0.0 | 0.0 | R1 (100.0) | 100.0 | 100.0 | measured | no | no |

## civ6-adjacency-optimizer

| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Evidence | Early Stop | Timeout |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- |
| artifact-generation | succeeded | 0 | completed | 0.0 | 14.7 | 60.0 | 60.0 | 60.0 | 0.0 | R0 (60.0) | 60.0 | 45.3 | measured | no | no |
| analytic-pipeline | succeeded | 0 | completed | 0.0 | 14.7 | 60.0 | 0.0 | 70.0 | 0.0 | R2 (70.0) | 70.0 | 55.3 | measured | no | no |
| engineering-composition | succeeded | 0 | completed | 0.0 | 14.7 | 60.0 | 0.0 | 60.0 | 0.0 | R0 (60.0) | 60.0 | 45.3 | measured | no | no |
| retrieval-heavy-synthesis | succeeded | 0 | completed | 0.0 | 14.7 | 55.0 | 50.0 | 45.0 | 0.0 | R0 (55.0) | 55.0 | 40.3 | measured | no | no |
| environment-control | succeeded | 0 | completed | 0.0 | 14.7 | 60.0 | 60.0 | 0.0 | 55.0 | R0 (60.0) | 60.0 | 45.3 | measured | no | no |
| methodology-guardrail | succeeded | 0 | completed | 0.0 | 14.7 | 60.0 | 50.0 | 60.0 | 0.0 | R0 (60.0) | 60.0 | 45.3 | measured | no | no |
| orchestration-delegation | succeeded | 0 | completed | 0.0 | 14.7 | 0.0 | 55.0 | 60.0 | 0.0 | R2 (60.0) | 60.0 | 45.3 | measured | no | no |

## data-to-d3

| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Evidence | Early Stop | Timeout |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- |
| artifact-generation | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 100.0 | 0.0 | 0.0 | R1 (100.0) | 40.0 | 20.0 | measured | no | no |
| analytic-pipeline | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -60.0 | -80.0 | measured | no | no |
| engineering-composition | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 0.0 | 100.0 | 100.0 | R2 (100.0) | 40.0 | 20.0 | measured | no | no |
| retrieval-heavy-synthesis | succeeded | 0 | completed_with_runtime_failures | 60.0 | 80.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -60.0 | -80.0 | ambiguous | no | no |
| environment-control | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 100.0 | 100.0 | 0.0 | R1 (100.0) | 40.0 | 20.0 | measured | no | no |
| methodology-guardrail | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 0.0 | 0.0 | 100.0 | R3 (100.0) | 40.0 | 20.0 | measured | no | no |
| orchestration-delegation | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 100.0 | 100.0 | 100.0 | R1 (100.0) | 40.0 | 20.0 | measured | no | no |

## econ-detrending-correlation

| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Evidence | Early Stop | Timeout |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- |
| artifact-generation | succeeded | 0 | completed | 40.0 | 60.0 | 0.0 | 100.0 | 0.0 | 0.0 | R1 (100.0) | 60.0 | 40.0 | measured | no | no |
| analytic-pipeline | succeeded | 0 | completed | 40.0 | 60.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -40.0 | -60.0 | measured | no | no |
| engineering-composition | succeeded | 0 | completed | 40.0 | 60.0 | 0.0 | 100.0 | 0.0 | 100.0 | R1 (100.0) | 60.0 | 40.0 | measured | no | no |
| retrieval-heavy-synthesis | succeeded | 0 | completed | 40.0 | 60.0 | 0.0 | 100.0 | 100.0 | 0.0 | R1 (100.0) | 60.0 | 40.0 | measured | no | no |
| environment-control | succeeded | 0 | completed | 40.0 | 60.0 | 0.0 | 0.0 | 100.0 | 100.0 | R2 (100.0) | 60.0 | 40.0 | measured | no | no |
| methodology-guardrail | succeeded | 0 | completed | 40.0 | 60.0 | 0.0 | 0.0 | 100.0 | 0.0 | R2 (100.0) | 60.0 | 40.0 | measured | no | no |
| orchestration-delegation | succeeded | 0 | completed | 40.0 | 60.0 | 0.0 | 0.0 | 0.0 | 100.0 | R3 (100.0) | 60.0 | 40.0 | measured | no | no |

## exceltable-in-ppt

| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Evidence | Early Stop | Timeout |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- |
| artifact-generation | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 100.0 | 100.0 | 100.0 | R1 (100.0) | 40.0 | 20.0 | measured | no | no |
| analytic-pipeline | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -60.0 | -80.0 | measured | no | no |
| engineering-composition | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -60.0 | -80.0 | measured | no | no |
| retrieval-heavy-synthesis | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -60.0 | -80.0 | measured | no | no |
| environment-control | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 0.0 | 100.0 | 0.0 | R2 (100.0) | 40.0 | 20.0 | measured | no | no |
| methodology-guardrail | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -60.0 | -80.0 | measured | no | no |
| orchestration-delegation | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 100.0 | 0.0 | 0.0 | R1 (100.0) | 40.0 | 20.0 | measured | no | no |

## find-topk-similiar-chemicals

| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Evidence | Early Stop | Timeout |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- |
| artifact-generation | succeeded | 0 | completed | 20.0 | 10.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -10.0 | measured | no | no |
| analytic-pipeline | succeeded | 0 | completed | 20.0 | 10.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -10.0 | measured | no | no |
| engineering-composition | succeeded | 0 | completed | 20.0 | 10.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -10.0 | measured | no | no |
| retrieval-heavy-synthesis | succeeded | 0 | completed | 20.0 | 10.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -10.0 | measured | no | no |
| environment-control | succeeded | 0 | completed | 20.0 | 10.0 | 0.0 | 100.0 | 0.0 | 0.0 | R1 (100.0) | 80.0 | 90.0 | measured | no | no |
| methodology-guardrail | succeeded | 0 | completed | 20.0 | 10.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -10.0 | measured | no | no |
| orchestration-delegation | succeeded | 0 | completed | 20.0 | 10.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -10.0 | measured | no | no |

## fix-druid-loophole-cve

| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Evidence | Early Stop | Timeout |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- |
| artifact-generation | succeeded | 0 | completed | 20.0 | 80.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -80.0 | measured | no | no |
| analytic-pipeline | succeeded | 0 | completed | 20.0 | 80.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -80.0 | measured | no | no |
| engineering-composition | succeeded | 0 | completed | 20.0 | 80.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -80.0 | measured | no | no |
| retrieval-heavy-synthesis | succeeded | 0 | completed | 20.0 | 80.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -80.0 | measured | no | no |
| environment-control | succeeded | 0 | completed | 20.0 | 80.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -80.0 | measured | no | no |
| methodology-guardrail | succeeded | 0 | completed | 20.0 | 80.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -80.0 | measured | no | no |
| orchestration-delegation | succeeded | 0 | completed | 20.0 | 80.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -80.0 | measured | no | no |

## Evidence Notes

- `adaptive-cruise-control__artifact-generation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `adaptive-cruise-control__analytic-pipeline`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `adaptive-cruise-control__engineering-composition`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `adaptive-cruise-control__retrieval-heavy-synthesis`: `runtime-blocked` - Run failed before clean verifier evidence was produced.
- `adaptive-cruise-control__environment-control`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `adaptive-cruise-control__methodology-guardrail`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `adaptive-cruise-control__orchestration-delegation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `civ6-adjacency-optimizer__artifact-generation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `civ6-adjacency-optimizer__analytic-pipeline`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `civ6-adjacency-optimizer__engineering-composition`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `civ6-adjacency-optimizer__retrieval-heavy-synthesis`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `civ6-adjacency-optimizer__environment-control`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `civ6-adjacency-optimizer__methodology-guardrail`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `civ6-adjacency-optimizer__orchestration-delegation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `data-to-d3__artifact-generation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `data-to-d3__analytic-pipeline`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `data-to-d3__engineering-composition`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `data-to-d3__retrieval-heavy-synthesis`: `ambiguous` - A score exists, but runtime exceptions or failures make it hard to treat as clean evidence.
- `data-to-d3__environment-control`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `data-to-d3__methodology-guardrail`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `data-to-d3__orchestration-delegation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `econ-detrending-correlation__artifact-generation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `econ-detrending-correlation__analytic-pipeline`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `econ-detrending-correlation__engineering-composition`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `econ-detrending-correlation__retrieval-heavy-synthesis`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `econ-detrending-correlation__environment-control`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `econ-detrending-correlation__methodology-guardrail`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `econ-detrending-correlation__orchestration-delegation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `exceltable-in-ppt__artifact-generation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `exceltable-in-ppt__analytic-pipeline`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `exceltable-in-ppt__engineering-composition`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `exceltable-in-ppt__retrieval-heavy-synthesis`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `exceltable-in-ppt__environment-control`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `exceltable-in-ppt__methodology-guardrail`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `exceltable-in-ppt__orchestration-delegation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `find-topk-similiar-chemicals__artifact-generation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `find-topk-similiar-chemicals__analytic-pipeline`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `find-topk-similiar-chemicals__engineering-composition`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `find-topk-similiar-chemicals__retrieval-heavy-synthesis`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `find-topk-similiar-chemicals__environment-control`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `find-topk-similiar-chemicals__methodology-guardrail`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `find-topk-similiar-chemicals__orchestration-delegation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `fix-druid-loophole-cve__artifact-generation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `fix-druid-loophole-cve__analytic-pipeline`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `fix-druid-loophole-cve__engineering-composition`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `fix-druid-loophole-cve__retrieval-heavy-synthesis`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `fix-druid-loophole-cve__environment-control`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `fix-druid-loophole-cve__methodology-guardrail`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `fix-druid-loophole-cve__orchestration-delegation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.

## Failure Notes

- `adaptive-cruise-control__retrieval-heavy-synthesis`: `RuntimeError: expected exactly one trial dir under <repo-root>/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round1-first20-fullmatrix-2026-05-01-1932-candidates/pairs/adaptive-cruise-control__retrieval-heavy-synthesis/refine_run_run-round1-first20-fullmatrix-fallback-2026-05-01-b02/refine/adaptive-cruise-control/rounds/round-0/tune_check/adaptive-cruise-control-round-0-c4-tune, found 0`
