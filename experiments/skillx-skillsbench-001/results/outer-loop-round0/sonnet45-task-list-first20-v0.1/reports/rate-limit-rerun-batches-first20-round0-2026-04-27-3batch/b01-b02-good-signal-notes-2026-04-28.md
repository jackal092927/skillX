# B01/B02 Good-Signal Notes

Generated from completed `run-first20-rate-limit-rerun-2026-04-27-3batch-b01` and `b02`.
Scores are percentages from effective R0 and R1-R3 inner-loop rewards.

## Scope

| Batch | Completed | Succeeded | Failed | Aborted |
|---|---:|---:|---:|---|
| b01 | 40/40 | 40 | 0 | false |
| b02 | 36/36 | 36 | 0 | false |

Across b01+b02:

| Metric | Count |
|---|---:|
| Total succeeded pairs | 76 |
| Baseline-perfect skipped pairs | 26 |
| Pairs that actually ran inner-loop | 50 |
| Stale R0 rerun reports handled with active R0 | 1 |
| Gold: R0 < 100 and R1=R2=R3=100 | 9 |
| Full monotonic positive: R0 <= R1 <= R2 <= R3 and R3 > R0 | 15 |
| Positive delta with no inner-loop regression below R0 | 22 |
| Any positive best delta vs R0 | 24 |
| Any inner-loop regression below R0 | 4 |
| No best delta vs R0 | 24 |

Interpretation: the strongest clean signal is already present in 9 pairs where baseline is imperfect and all three inner-loop rounds reach 100. A broader stable-positive signal appears in 22/50 inner-loop runs when using best delta plus no regression below R0. Regressions are rare in b01+b02 and concentrated in `civ6-adjacency-optimizer`.

## Signal Definitions

- `Gold`: effective R0 is below 100 and R1, R2, R3 are all 100.
- `Full monotonic positive`: R0 <= R1 <= R2 <= R3 and final R3 is above R0.
- `Positive no-regression`: best(R1, R2, R3) is above R0 and every inner-loop round is at least R0.
- `Regression`: any of R1/R2/R3 falls below effective R0.
- `Stale rerun report`: if `baseline_perfect_rerun.final_reward` disagrees with active `round-0/tune_check/result.json`, this note uses active R0, matching the dashboard monitor semantics.

## Gold Examples

These are the clearest cherry-picks: low baseline followed by stable perfect inner-loop performance.

| Batch | Pair | Schema | R0 | R1 | R2 | R3 | Best Delta |
|---|---|---|---:|---:|---:|---:|---:|
| b01 | `court-form-filling__analytic-pipeline` | analytic-pipeline | 0 | 100 | 100 | 100 | +100 |
| b01 | `dapt-intrusion-detection__methodology-guardrail` | methodology-guardrail | 0 | 100 | 100 | 100 | +100 |
| b01 | `dapt-intrusion-detection__retrieval-heavy-synthesis` | retrieval-heavy-synthesis | 0 | 100 | 100 | 100 | +100 |
| b02 | `earthquake-phase-association__analytic-pipeline` | analytic-pipeline | 0 | 100 | 100 | 100 | +100 |
| b02 | `earthquake-phase-association__engineering-composition` | engineering-composition | 0 | 100 | 100 | 100 | +100 |
| b02 | `earthquake-phase-association__orchestration-delegation` | orchestration-delegation | 0 | 100 | 100 | 100 | +100 |
| b02 | `earthquake-plate-calculation__orchestration-delegation` | orchestration-delegation | 0 | 100 | 100 | 100 | +100 |
| b02 | `econ-detrending-correlation__orchestration-delegation` | orchestration-delegation | 0 | 100 | 100 | 100 | +100 |
| b02 | `energy-ac-optimal-power-flow__environment-control` | environment-control | 0 | 100 | 100 | 100 | +100 |

## Additional Monotonic Examples

These are not all perfect from R1 onward, but the trajectory is non-strictly upward and ends improved.

| Batch | Pair | Schema | R0 | R1 | R2 | R3 | Best Delta |
|---|---|---|---:|---:|---:|---:|---:|
| b01 | `court-form-filling__methodology-guardrail` | methodology-guardrail | 0 | 0 | 100 | 100 | +100 |
| b01 | `court-form-filling__retrieval-heavy-synthesis` | retrieval-heavy-synthesis | 0 | 0 | 0 | 100 | +100 |
| b02 | `energy-market-pricing__environment-control` | environment-control | 0 | 0 | 100 | 100 | +100 |
| b02 | `energy-market-pricing__retrieval-heavy-synthesis` | retrieval-heavy-synthesis | 0 | 0 | 100 | 100 | +100 |
| b01 | `civ6-adjacency-optimizer__analytic-pipeline` | analytic-pipeline | 0 | 0 | 0 | 55 | +55 |
| b01 | `civ6-adjacency-optimizer__engineering-composition` | engineering-composition | 0 | 0 | 0 | 40 | +40 |

## Positive But Less Stable

These show a positive best delta and no drop below R0, but the trajectory is not monotonic. They are useful secondary examples but weaker than the tables above.

| Batch | Pair | Schema | R0 | R1 | R2 | R3 | Best Delta |
|---|---|---|---:|---:|---:|---:|---:|
| b01 | `adaptive-cruise-control__orchestration-delegation` | orchestration-delegation | 0 | 100 | 0 | 0 | +100 |
| b01 | `adaptive-cruise-control__retrieval-heavy-synthesis` | retrieval-heavy-synthesis | 0 | 0 | 100 | 0 | +100 |
| b01 | `court-form-filling__artifact-generation` | artifact-generation | 0 | 100 | 0 | 0 | +100 |
| b01 | `court-form-filling__orchestration-delegation` | orchestration-delegation | 0 | 100 | 0 | 0 | +100 |
| b02 | `earthquake-phase-association__retrieval-heavy-synthesis` | retrieval-heavy-synthesis | 0 | 100 | 0 | 100 | +100 |
| b02 | `earthquake-plate-calculation__artifact-generation` | artifact-generation | 0 | 0 | 100 | 0 | +100 |
| b01 | `civ6-adjacency-optimizer__artifact-generation` | artifact-generation | 0 | 60 | 55 | 55 | +60 |

## Stale R0 Rerun Report

This pair has a stale `baseline_perfect_rerun` final reward and is therefore not counted as gold. Active R0 is used here.

| Batch | Pair | Schema | Active R0 | R1 | R2 | R3 | Best Delta |
|---|---|---|---:|---:|---:|---:|---:|
| b02 | `earthquake-phase-association__artifact-generation` | artifact-generation | 100 | 100 | 100 | 100 | 0 |

## Regression Cases

These should not be used as positive examples. They are all in one task family.

| Batch | Pair | Schema | R0 | R1 | R2 | R3 | Best Delta |
|---|---|---|---:|---:|---:|---:|---:|
| b01 | `civ6-adjacency-optimizer__environment-control` | environment-control | 50 | 0 | 60 | 45 | +10 |
| b01 | `civ6-adjacency-optimizer__methodology-guardrail` | methodology-guardrail | 55 | 50 | 60 | 0 | +5 |
| b01 | `civ6-adjacency-optimizer__orchestration-delegation` | orchestration-delegation | 60 | 0 | 55 | 0 | -5 |
| b01 | `civ6-adjacency-optimizer__retrieval-heavy-synthesis` | retrieval-heavy-synthesis | 45 | 0 | 0 | 0 | -45 |

## Schema-Level Snapshot

Computed over the 50 pairs that actually ran inner-loop.

| Schema | N | Positive Delta | Positive No-Regression | Gold | Regression | Mean Delta |
|---|---:|---:|---:|---:|---:|---:|
| analytic-pipeline | 8 | 3 | 3 | 2 | 0 | +31.9 |
| artifact-generation | 8 | 3 | 3 | 0 | 0 | +32.5 |
| engineering-composition | 7 | 2 | 2 | 1 | 0 | +20.0 |
| environment-control | 7 | 3 | 2 | 1 | 1 | +30.0 |
| methodology-guardrail | 5 | 3 | 2 | 1 | 1 | +41.0 |
| orchestration-delegation | 7 | 5 | 5 | 3 | 1 | +70.7 |
| retrieval-heavy-synthesis | 8 | 5 | 5 | 1 | 1 | +56.9 |

## Current Takeaway

The best current story from b01+b02 is not just "best delta is positive"; it is that a meaningful subset has stable improvement across the whole inner loop. The strongest evidence is the 9 gold pairs, followed by 6 additional monotonic positive pairs. The rare regressions are localized enough that they should be framed as task-family-specific rather than a broad method failure, pending b03 completion.
