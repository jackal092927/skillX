# SkillX Outer-Loop Schema Update Package: `outer-loop-round0`

- generated_at: `2026-04-24T00:08:00.764746+00:00`
- output_dir: `experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/outer-loop-schema-updates`
- next_round_id: `outer-loop-round1`
- min_support_size: `2`
- max_update_schemas: `3`

## Round Update Plan

| schema_id | action | reason | support | reliable | priority | challenger |
| --- | --- | --- | ---: | ---: | ---: | --- |
| analytic-pipeline | update | selected_by_priority | 2 | 2 | 5.75 | differentiating |
| artifact-generation | freeze | freeze_low_support | 1 | 1 | 5.00 | incumbent |
| engineering-composition | freeze | freeze_low_support | 0 | 0 | 4.00 | incumbent |
| environment-control | freeze | freeze_low_support | 1 | 1 | 3.00 | incumbent |
| methodology-guardrail | update | selected_by_priority | 2 | 2 | 5.00 | differentiating |
| orchestration-delegation | freeze | freeze_low_support | 0 | 0 | 2.00 | incumbent |
| retrieval-heavy-synthesis | freeze | freeze_low_support | 0 | 0 | 3.00 | incumbent |

## Evidence Summary

- `artifact-generation`: support=`1`, reliable=`1`, mean_score=`90.0`, competitors=`analytic-pipeline (6), environment-control (1), engineering-composition (1)`
- `analytic-pipeline`: support=`2`, reliable=`2`, mean_score=`52.75`, competitors=`artifact-generation (4), environment-control (1), methodology-guardrail (1)`
- `engineering-composition`: support=`0`, reliable=`0`, mean_score=`None`, competitors=`analytic-pipeline (6), environment-control (1), artifact-generation (1)`
- `retrieval-heavy-synthesis`: support=`0`, reliable=`0`, mean_score=`None`, competitors=`analytic-pipeline (4), environment-control (1), methodology-guardrail (1)`
- `environment-control`: support=`1`, reliable=`1`, mean_score=`55.95`, competitors=`analytic-pipeline (3), artifact-generation (1)`
- `methodology-guardrail`: support=`2`, reliable=`2`, mean_score=`87.5`, competitors=`analytic-pipeline (5), retrieval-heavy-synthesis (1)`
- `orchestration-delegation`: support=`0`, reliable=`0`, mean_score=`None`, competitors=`analytic-pipeline (4)`

## Challenger Eval Plan

- `analytic-pipeline` / `differentiating`: 6 task(s): `earthquake-phase-association, pdf-excel-diff, citation-check, civ6-adjacency-optimizer, court-form-filling, powerlifting-coef-calc`
- `methodology-guardrail` / `differentiating`: 6 task(s): `citation-check, court-form-filling, earthquake-phase-association, energy-ac-optimal-power-flow, pdf-excel-diff, powerlifting-coef-calc`
