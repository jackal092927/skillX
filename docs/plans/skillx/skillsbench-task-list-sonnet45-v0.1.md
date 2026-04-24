# SkillsBench Task List with Sonnet 4.5 Official Results v0.1

This task list is the compact, one-row-per-task view used by SkillX planning.

Source files:

- Task inventory: `docs/plans/skillx/skillsbench-task-cluster-inputs-v0.1.jsonl`
- Official scraped results: `experiments/skillx-skillsbench-001/results/official-task-results/official_task_results.csv`
- Official scrape manifest: `experiments/skillx-skillsbench-001/results/official-task-results/manifest.json`

Canonical CSV:

- `docs/plans/skillx/skillsbench-task-list-sonnet45-v0.1.csv`

## Scope

- Total rows: 89 tasks.
- Rows `001` to `071`: tasks with available official scraped result rows.
- Rows `072` to `089`: tasks whose official result rows could not be scraped from the SkillsBench website.

The 18 missing-official-result tasks are placed at the end by design. Their `official_missing_reason` column records whether the page returned `404`, `500`, or returned `200` without embedded result rows.

## Columns

- `skillx_task_id`: SkillX-local stable task index, formatted as `001` to `089`.
- `task_id`: SkillsBench task id.
- `initial_schema_seed`: initial semantic schema seed from the task inventory. This is an early SkillX clustering/assignment hint, not the final outer-loop schema assignment.
- `official_result_status`: `available` or `missing_official_results`.
- `official_missing_reason`: scrape failure reason for missing official results.
- `source_url`: SkillsBench task page URL.
- `sonnet45_no_skills_score`: Claude Code Sonnet 4.5 official score under `No Skills`.
- `sonnet45_with_skills_score`: Claude Code Sonnet 4.5 official score under `With Skills`.
- `sonnet45_self_generated_score`: Claude Code Sonnet 4.5 official score under `Self-Generated`.

## Notes

The CSV intentionally keeps only the three Sonnet 4.5 score columns to stay compact. The raw official scrape still contains `trials`, `pass_count`, and `perfect_count` in `experiments/skillx-skillsbench-001/results/official-task-results/official_task_results.csv`.
