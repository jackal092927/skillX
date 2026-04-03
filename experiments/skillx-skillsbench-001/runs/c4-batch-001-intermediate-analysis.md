# C4 Batch 001 Intermediate Analysis

- timestamp: `2026-03-23T12:00:00Z`
- scope: first `C4` inner-loop batch over
  - `trend-anomaly-causal-inference`
  - `exoplanet-detection-period`
  - `energy-ac-optimal-power-flow`
- status: `in_progress`

## Confirmed Signals

### 1. `trend-anomaly-causal-inference` has a real positive `C4` signal

- prior clean baseline from adjusted run:
  - `C0 = 1.0`
  - `C1 = 0.7444`
- current SkillX baseline:
  - `C2 = 0.9`
  - `C3 = 0.7944`
- current `C4`:
  - `R2 = 1.0`

Interpretation:

- `C4 R2 - C3 = +0.2056`
- `C4 R2 - C2 = +0.1000`
- `C4 R2 - C1 = +0.2556`

This is the first strong evidence that bounded refine can recover and exceed the degraded `C3` condition on a known negative-transfer task.

### 2. Compression of speculative `Derived Execution Layer` content is currently the strongest working mechanism

The winning `trend R2` diagnosis and diff artifacts converge on the same pattern:

- remove speculative evaluator hooks
- compress verbose postconditions
- shrink undifferentiated failure-mode catalogs
- keep core decision frameworks and correctness-critical methodology intact

Working hypothesis:

- `C3` becomes harmful when the derived layer expands into unsupported constraints, redundant notes, and overly detailed failure catalogs
- `C4` helps when it removes low-signal derived content without stripping away correctness-critical guidance

### 3. `exoplanet` and `energy` currently expose contract-completion failures more than task-level scientific failures

Observed failure classes so far:

- `energy R1` initial failure:
  - missing `# Derived Execution Layer` in one refined skill
- `exoplanet R2` initial failure:
  - missing required refined skill file (`box-least-squares/SKILL.md`)

These are not useful benchmark deltas. They are refine-output contract failures.

## Runner / Protocol Changes Already Applied

To keep the loop moving without contaminating the science:

- runner now resumes from existing completed rounds instead of restarting whole runs
- tune-check path recovery is fixed
- ledger deduplication is fixed for resumed runs
- refine prompt now explicitly requires:
  - every refined skill file to exist
  - every refined skill to preserve `# Derived Execution Layer`
- runner now auto-retries one time for refine-stage contract failures only when verifier output indicates:
  - `missing refined skill`
  - `refined skill missing derived layer`

These retries are intentionally narrow. They do not retry low scores or clean scientific failures.

## Proto-`v0.2` Meta-Protocol Ideas

The current evidence suggests `C4 v0.2` should likely add:

1. Explicit completeness self-check before finish
- require the refiner to verify that all expected skill files exist
- require the refiner to verify that each skill still contains the required derived-layer header

2. Stronger anti-speculation rule for `Derived Execution Layer`
- derived content must be evidence-grounded in tune-side failures
- disallow invented row counts, exact schema assumptions, and evaluator details unless directly supported

3. Stronger compression bias
- prefer short, prioritized failure lists
- prefer essential postconditions only
- remove duplicated execution notes when they restate guidance

4. Clearer “preserve structure, shrink bloat” instruction
- the current best result came from preserving core skill structure while compressing harmful elaboration

## Harness / Controller Note

Current conclusion:

- do not replace the active `Harbor + Claude Code` execution chain mid-batch
- `PydanticAI` remains a candidate for a later outer-loop controller layer, not for immediate inner-loop replacement

Potential later use of `PydanticAI`:

- structured delta aggregation
- refine-failure taxonomy
- protocol-diff proposal generation
- outer-loop memo synthesis

## Next Actions

1. Let `trend` finish the remaining scheduled round(s)
2. Let `energy` complete the repaired `R1`
3. Let `exoplanet` retry `R2` under the stronger completion constraints
4. Once batch-1 closes, draft `C4 meta-protocol v0.2`
5. Run one mock outer-loop update with that `v0.2`
