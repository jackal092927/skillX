# SkillsBench Official Results Cache Design

- **Project:** `skillX`
- **Date:** 2026-04-08
- **Scope:** official SkillsBench task-level results caching for local prescan and pilot task selection
- **Status:** ready for review

## Goal

Create a small local cache of official SkillsBench task-level result matrices so
SkillX can:

1. select pilot tasks without repeatedly scraping the website by hand,
2. filter tasks by a baseline model such as `Claude Code (Sonnet 4.5)`,
3. support later outer-loop prescan and task-slice design with local search.

This design does **not** implement the pilot round-0 outer-loop runner yet.
It only creates the local result substrate that the runner will consume later.

## Source Of Truth

The source of truth is the public SkillsBench task detail page:

- `https://www.skillsbench.ai/tasks/<task-id>`

The page HTML embeds the task-level `results` matrix directly in the rendered
payload. We should extract from that embedded data instead of relying on manual
browser interaction.

Required stable row fields:

- `task`
- `model`
- `modelShort`
- `harness`
- `family`
- `condition`
- `score`
- `trials`
- `passCount`
- `perfectCount`

Optional future row fields:

- `trajectoryIndex`-derived per-run information such as `trialId`, `reward`,
  and `execTimeSec`

Version 0.1 should cache only the aggregated `results` matrix.

## Output Artifacts

Write all cache artifacts under:

- `experiments/skillx-skillsbench-001/results/official-task-results/`

Required outputs:

1. `tasks/<task-id>.json`
   - normalized per-task artifact
   - includes task id, cache timestamp, source URL, and full official results
2. `official_task_results.jsonl`
   - one normalized result row per line across all cached tasks
3. `official_task_results.csv`
   - flat analyst-friendly export for grep, pandas, and spreadsheet use
4. `manifest.json`
   - cache summary:
     - scrape timestamp
     - task count attempted
     - task count succeeded
     - task count missing results
     - baseline coverage stats for key models

Optional outputs only on failure:

- `raw_html/<task-id>.html`
  - store only when extraction fails or parsed rows are suspiciously empty

## Normalized Row Schema

Each JSONL/CSV row should use this normalized structure:

```json
{
  "task_id": "citation-check",
  "source_url": "https://www.skillsbench.ai/tasks/citation-check",
  "cached_at": "2026-04-08T00:00:00Z",
  "model": "Claude Code (Sonnet 4.5)",
  "model_short": "Sonnet 4.5",
  "harness": "Claude Code",
  "family": "anthropic",
  "condition": "With Skills",
  "score": 100.0,
  "trials": 5,
  "pass_count": 5,
  "perfect_count": 5
}
```

Canonical key for deduplication:

- `task_id`
- `harness`
- `model_short`
- `condition`

`model` remains display text and should not be the canonical key.

## Extraction Strategy

Implement a small script that:

1. reads the local SkillsBench task inventory from
   `docs/plans/skillx/skillsbench-task-cluster-inputs-v0.1.jsonl`,
2. fetches each task detail page HTML,
3. extracts the embedded `results` array from the page payload,
4. normalizes rows into the cache format,
5. writes per-task and aggregate artifacts.

Version 0.1 extraction policy:

- prefer embedded `results` payload extraction,
- do not require browser automation,
- do not depend on unstable CSS selectors,
- do not scrape rendered text tables as the primary method.

## Baseline Selection Support

The cache must make it cheap to query tasks by baseline model.

Version 0.1 should explicitly support:

- `Claude Code (Sonnet 4.5)`
- `Claude Code (Opus 4.6)`

The first consumer is pilot-task prescan.
The initial selection filter will prefer tasks where:

- the requested baseline exists,
- `condition = With Skills`,
- `score < 100`

This filter is only for task-slice construction.
It is not a claim about final evaluation policy.

## Failure Handling

If a task page fetch succeeds but no `results` rows are extracted:

1. record the task in `manifest.json` as `missing_results`,
2. optionally store raw HTML for later inspection,
3. continue the run instead of failing the whole cache build.

If duplicate rows appear for the same canonical key:

1. keep one row,
2. log the duplicate in the manifest,
3. mark the task for manual inspection only if the duplicated values disagree.

## Testing

Version 0.1 should include small deterministic tests for:

1. extracting `results` rows from a saved HTML fixture,
2. normalizing rows into the flat schema,
3. deduplicating repeated rows,
4. building aggregate JSONL/CSV outputs from multiple task payloads.

The implementation should avoid live network calls in unit tests.

## Non-Goals

This design does not yet include:

- pilot round-0 outer-loop execution,
- meta-schema rendering,
- C1/C4AR local benchmark execution,
- trajectory-level official run ingestion,
- automatic task selection logic beyond simple baseline filtering.

## Recommended First Implementation Slice

Implement the smallest useful path:

1. one cache script,
2. one cache directory,
3. per-task JSON artifacts,
4. aggregate JSONL/CSV exports,
5. baseline filtering support for `Sonnet 4.5`.

Once this is stable, use the cache to pick the 15-task pilot slice for the
minimal outer-loop runner.
