# SkillX Checkpoint — 2026-03-24

## Scope

This checkpoint records the current completed state of:

- `C3` (`SkillX Derived`, SkillX 衍生版)
- first-batch `C4` (`bounded multi-round refine`, 受限多轮精修)

Tasks covered:

- `trend-anomaly-causal-inference`
- `exoplanet-detection-period`
- `energy-ac-optimal-power-flow`

Execution environment used in this batch:

- agent: `claude-code`
- model: `anthropic/claude-sonnet-4-5`
- auth: `CLAUDE_CODE_OAUTH_TOKEN_FILE`
- harness: `Harbor + Docker`
- orchestrators:
  - `C2/C3`: `mac_autoresearch_support/scripts/run_skillx_rewrite_benchmark.py`
  - `C4`: `mac_autoresearch_support/scripts/run_skillx_refine_benchmark.py`

## C3 Results

Completed `C3` results:

| task | C3 reward | source |
|---|---:|---|
| `trend-anomaly-causal-inference` | `0.7944` | `rewrite-benchmark-003-harbor-rewrite` |
| `exoplanet-detection-period` | `0.0` | `rewrite-benchmark-004-exoplanet` |
| `energy-ac-optimal-power-flow` | `0.0` | `rewrite-benchmark-005-energy` |

Interpretation:

- `trend` remained below its clean `C0` baseline and therefore stayed a useful negative-transfer recovery target.
- `exoplanet` and `energy` both had clean `C3 = 0.0` outcomes for this batch.

## C4 Batch-1 Results

The first `C4` batch ran a bounded inner loop from `R0` through `R3`, with `R0 = C3`.

Final selected results:

| task | selected round | C4-final reward | delta vs C3 |
|---|---:|---:|---:|
| `trend-anomaly-causal-inference` | `R2` | `1.0` | `+0.2056` |
| `exoplanet-detection-period` | `R0` | `0.0` | `+0.0` |
| `energy-ac-optimal-power-flow` | `R0` | `0.0` | `+0.0` |

Round traces:

- `trend`: `R0 0.7944 -> R1 0.7944 -> R2 1.0 -> R3 0.95`
- `exoplanet`: `R0 0.0 -> R1 0.0 -> R2 0.0 -> R3 0.0`
- `energy`: `R0 0.0 -> R1 0.0 -> R2 0.0 -> R3 0.0`

Interpretation:

- `trend` is the first strong positive `C4` result in this line.
- `exoplanet` and `energy` did not improve under `C4 v0.1`.
- Selecting `C4-final` by best round rather than "last round wins" was necessary and correct.

## What Actually Helped In C4

The `trend` win came from `R2`, not from adding more derived content.

The highest-signal change pattern was:

- compress the `Derived Execution Layer` (衍生执行层)
- remove speculative evaluator hooks (猜测性的评测钩子)
- shrink over-detailed postconditions (过度具体的后置条件)
- reduce long failure catalogs to a shorter, higher-signal set
- preserve core methodology and decision logic

Working hypothesis:

- `C3` becomes harmful when the derived layer grows into low-signal, redundant, or unsupported execution detail
- `C4` helps when it removes harmful elaboration without deleting correctness-critical guidance

## Failures And Repairs During Batch-1

This batch surfaced real runner/protocol failures that were fixed during execution:

1. `tune_check` resume path bug
- the runner initially failed to recover nested Harbor tune results correctly
- fix was implemented in `run_skillx_refine_benchmark.py`

2. refine contract failures
- `energy` initially produced a refined skill missing `# Derived Execution Layer`
- `exoplanet` initially produced a missing refined skill file
- prompt and runner behavior were tightened to require:
  - all expected refined skill files must exist
  - every refined skill must preserve `# Derived Execution Layer`
- narrow auto-retry was added only for these refine-output contract failures

These fixes were intended to keep the loop scientifically interpretable:

- retry contract failures once
- do not retry low scores
- do not retry clean scientific failures

## Current Scientific Takeaway

At this checkpoint, the evidence is:

- `C3` alone is not sufficient on all target tasks
- bounded `C4` refine can materially improve a negative-transfer task
- this improvement is not coming from "more rules"
- it is currently coming from pruning speculative and bloated derived content

This is encouraging, but not yet a complete claim for `C4`, because:

- only one of the three tasks improved
- held-out evaluation is still placeholder-only in the current implementation
- `C4 v0.1` appears under-specified for tasks like `exoplanet` and `energy`

## Status

What is complete:

- `C3` batch for the three selected tasks
- first `C4` inner-loop batch (`v0.1`)
- task-level `C4-final` selection

What is not complete:

- `C4` held-out evaluation
- `C4 meta-protocol v0.2`
- mock outer-loop rerun under the updated refine protocol

## Next Recommended Step

The next step should be:

1. write `C4 meta-protocol v0.2`
2. make the outer-loop changes global, not task-specific
3. rerun one mock `C4` batch under `v0.2`
4. compare:
   - `C4 v0.2` vs `C4 v0.1`
   - `C4 v0.2` vs `C3`

The most justified `v0.2` directions from current evidence are:

- stronger anti-speculation rule for `Derived Execution Layer`
- stronger completion self-check before finalizing a refined round
- stronger compression bias
- clearer instruction to preserve core structure while shrinking bloat

## Primary Artifact Pointers

Batch-level summary:

- `experiments/skillx-skillsbench-001/runs/c4-batch-001-intermediate-analysis.md`

Task-level `C4` summaries:

- `experiments/skillx-skillsbench-001/runs/c4-trend-001-v0-1/refine/trend-anomaly-causal-inference/refine_summary.json`
- `experiments/skillx-skillsbench-001/runs/c4-exoplanet-001-v0-1/refine/exoplanet-detection-period/refine_summary.json`
- `experiments/skillx-skillsbench-001/runs/c4-energy-001-v0-1/refine/energy-ac-optimal-power-flow/refine_summary.json`

Task-level final selections:

- `experiments/skillx-skillsbench-001/runs/c4-trend-001-v0-1/refine/trend-anomaly-causal-inference/C4-final/final_selection_note.md`
- `experiments/skillx-skillsbench-001/runs/c4-exoplanet-001-v0-1/refine/exoplanet-detection-period/C4-final/final_selection_note.md`
- `experiments/skillx-skillsbench-001/runs/c4-energy-001-v0-1/refine/energy-ac-optimal-power-flow/C4-final/final_selection_note.md`
