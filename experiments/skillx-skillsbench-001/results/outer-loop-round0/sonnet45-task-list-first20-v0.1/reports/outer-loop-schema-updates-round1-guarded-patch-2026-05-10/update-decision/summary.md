# SkillX Outer-Loop Update Decision

- generated_at: `2026-05-10T07:26:58.554833+00:00`
- output_dir: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-schema-updates-round1-guarded-patch-2026-05-10/update-decision`
- global_update_mode: `guarded_patch`
- mode_reason: protected regressions exceed rewrite guard, but positive transfer evidence exists
- positive_transfer_pairs: `30`
- protected_regression_pairs: `12`

## Scorecard

| group | pairs | mean previous | mean current | mean delta |
| --- | ---: | ---: | ---: | ---: |
| all_common_pairs | 140 | 17.6714 | 18.0476 | 0.3762 |
| previous_primary_assignment | 15 | 77.4778 | 31.6667 | -45.8111 |
| previous_multi_assignment | 27 | 77.4969 | 25.3426 | -52.1543 |
| previous_schema_training_assignment | 28 | 75.8452 | 25.5536 | -50.2917 |

## Schema Decisions

| schema | mode | positives | protected regressions | reason |
| --- | --- | ---: | ---: | --- |
| analytic-pipeline | guarded_patch | 2 | 2 | schema has positive transfer evidence; patch against stable base |
| artifact-generation | guarded_patch | 6 | 0 | schema has positive transfer evidence; patch against stable base |
| engineering-composition | guarded_patch | 6 | 3 | schema has positive transfer evidence; patch against stable base |
| environment-control | guarded_patch | 3 | 2 | schema has positive transfer evidence; patch against stable base |
| methodology-guardrail | guarded_patch | 6 | 1 | schema has positive transfer evidence; patch against stable base |
| orchestration-delegation | guarded_patch | 2 | 2 | schema has positive transfer evidence; patch against stable base |
| retrieval-heavy-synthesis | guarded_patch | 5 | 2 | schema has positive transfer evidence; patch against stable base |
