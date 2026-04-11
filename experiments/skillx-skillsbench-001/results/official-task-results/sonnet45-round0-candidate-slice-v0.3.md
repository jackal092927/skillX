# Sonnet 4.5 Round-0 Candidate Slice v0.3

- baseline model: `Claude Code (Sonnet 4.5)`
- baseline conditions: `No Skills`, `With Skills`
- source cache: `official_task_results.jsonl`
- selection target: `20` tasks
- predecessor slice excluded: `sonnet45-round0-candidate-slice-v0.2.json`

## Selection Heuristic

1. exclude the existing `v0.2` slice20 tasks
2. rank the remaining official Sonnet 4.5 tasks by descending `C0 + C1`
3. use `C1`, then `C0`, as tie-breakers
4. keep the selected twenty roughly balanced across available seed-schema buckets
5. order the final list in a balanced round-robin so partial launches are less
   schema-skewed than a pure score-sorted list

## Selected Counts

- `analytic-pipeline`: `5`
- `artifact-generation`: `5`
- `engineering-composition`: `4`
- `retrieval-heavy-synthesis`: `4`
- `environment-control`: `1`
- `methodology-guardrail`: `1`

## Selected Tasks

| order | task | seed schema | C0 | C1 | C0+C1 |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | `citation-check` | `methodology-guardrail` | `100.0` | `100.0` | `200.0` |
| 2 | `powerlifting-coef-calc` | `artifact-generation` | `100.0` | `100.0` | `200.0` |
| 3 | `spring-boot-jakarta-migration` | `engineering-composition` | `100.0` | `100.0` | `200.0` |
| 4 | `trend-anomaly-causal-inference` | `analytic-pipeline` | `84.3` | `90.6` | `174.9` |
| 5 | `sec-financial-report` | `retrieval-heavy-synthesis` | `0.0` | `100.0` | `100.0` |
| 6 | `virtualhome-agent-planning` | `environment-control` | `0.0` | `0.0` | `0.0` |
| 7 | `3d-scan-calc` | `analytic-pipeline` | `80.0` | `80.0` | `160.0` |
| 8 | `data-to-d3` | `artifact-generation` | `60.0` | `80.0` | `140.0` |
| 9 | `fix-druid-loophole-cve` | `engineering-composition` | `20.0` | `80.0` | `100.0` |
| 10 | `reserves-at-risk-calc` | `retrieval-heavy-synthesis` | `0.0` | `0.0` | `0.0` |
| 11 | `mars-clouds-clustering` | `analytic-pipeline` | `40.0` | `100.0` | `140.0` |
| 12 | `exceltable-in-ppt` | `artifact-generation` | `60.0` | `80.0` | `140.0` |
| 13 | `simpo-code-reproduction` | `engineering-composition` | `0.0` | `40.0` | `40.0` |
| 14 | `shock-analysis-demand` | `retrieval-heavy-synthesis` | `0.0` | `0.0` | `0.0` |
| 15 | `multilingual-video-dubbing` | `analytic-pipeline` | `40.0` | `100.0` | `140.0` |
| 16 | `offer-letter-generator` | `artifact-generation` | `0.0` | `100.0` | `100.0` |
| 17 | `fix-build-agentops` | `engineering-composition` | `0.0` | `0.0` | `0.0` |
| 18 | `shock-analysis-supply` | `retrieval-heavy-synthesis` | `0.0` | `0.0` | `0.0` |
| 19 | `lab-unit-harmonization` | `analytic-pipeline` | `39.6` | `60.4` | `100.0` |
| 20 | `protein-expression-analysis` | `artifact-generation` | `0.0` | `100.0` | `100.0` |

## Notes

- After removing the `v0.2` slice20, the remaining official pool has no
  `orchestration-delegation` candidates.
- The remaining official pool has only one `environment-control` task and one
  `methodology-guardrail` task, so those buckets cannot be balanced more
  aggressively.
- This slice is tuned for the next parallel `20 x 7` batch, not for a final
  fixed benchmark subset.
