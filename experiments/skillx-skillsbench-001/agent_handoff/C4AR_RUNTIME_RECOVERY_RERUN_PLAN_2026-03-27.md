# C4AR Runtime Recovery Rerun Plan — 2026-03-27

## Goal

Recover scientifically interpretable evidence from the three post-`trend` tasks without overwriting the first-pass `*-c4ar-001` artifacts.

## Why A New Plan Is Needed

The first post-`trend` batch mixed real task behavior with executor failures:

- `taxonomy` produced two valid rounds, then timed out / failed at later rounds
- `exoplanet` produced one valid `0.0` round, then timed out / failed
- `energy` never produced a runtime-valid round

The dominant failure classes were:

- `AgentSetupTimeoutError`
- `AgentTimeoutError`
- generic `RuntimeError`

So the next step should optimize for **getting interpretable outputs**, not for maximizing task parallelism.

## Recommended Recovery Policy

### 1. Preserve existing runs

Do not modify or delete:

- `taxonomy-tree-merge-c4ar-001`
- `exoplanet-detection-period-c4ar-001`
- `energy-ac-optimal-power-flow-c4ar-001`

Treat them as first-pass evidence.

### 2. Increase timeout budgets materially

The first batch used:

- `round_timeout_multiplier = 2.0`
- `tune_timeout_multiplier = 3.0`

Recovery reruns should double those:

- `round_timeout_multiplier = 4.0`
- `tune_timeout_multiplier = 6.0`

This is the simplest direct response to the observed timeout-heavy failure pattern.

### 3. Reduce concurrency

Recommended mode:

- run recovery reruns serially, not three-at-once

Reason:

- when the primary failure mode is “the agent timed out and returned nothing useful,” the cheapest way to improve evidence quality is to reduce contention and give each run more wall-clock room

### 4. Keep the rest of the recipe stable

Do not redesign the architecture.
Keep:

- `orchestration-mode = c4ar`
- `Role C` as real Harbor/Docker benchmark execution only
- the same class-aware `C2AR` starting packs
- the same `Role A` / `Role B` playbook-driven flow

This keeps the recovery rerun focused on runtime stability, not on changing the research question.

### 5. Add an executor timeout gate

After each executor round completes, inspect the executor result immediately.

If `exception_stats` contains a timeout-class failure such as:

- `AgentSetupTimeoutError`
- `AgentTimeoutError`

then do **not** continue the current run into the next refinement round.

Reason:

- once the executor round times out, the downstream `Role A` / `Role B` artifacts may still be syntactically valid
- but the scientific value of continuing is low because the run has already lost its clean measurement chain
- in the first post-`trend` batch, timeout-class failures were followed by additional `0.0` rounds and further runtime-invalid artifacts rather than recovery

So the preferred behavior is:

1. mark the current run as runtime-invalid from the timeout point onward
2. stop the run early
3. launch a fresh recovery rerun with doubled timeout settings

### 6. Cap timeout escalation

Do not keep doubling timeouts indefinitely.

Use one recovery step only:

- first pass: existing budget
- second pass: `timeout x2`

If the recovery rerun still hits timeout-class failures under:

- serial execution
- `round_timeout_multiplier = 4.0`
- `tune_timeout_multiplier = 6.0`

then stop escalating timeout budgets and treat the task as requiring a more specific executor/runtime intervention.

## Recovery Rerun Order

Recommended order:

1. `energy-ac-optimal-power-flow`
   - first run was fully runtime-invalid
   - highest value recovery target because there is currently no usable evidence
2. `exoplanet-detection-period`
   - only `R0` was runtime-valid
3. `taxonomy-tree-merge`
   - optional full rerun after the two above
   - lower urgency because `R0` and `R1` are already usable evidence

## Suggested New Run IDs

- `energy-ac-optimal-power-flow-c4ar-002-timeoutx2`
- `exoplanet-detection-period-c4ar-002-timeoutx2`
- `taxonomy-tree-merge-c4ar-002-timeoutx2`

## Command Shape

Use the same command family as before, but change only:

- `--run-id`
- `--output-dir`
- `--round-timeout-multiplier 4.0`
- `--tune-timeout-multiplier 6.0`

## Success Criteria For Recovery Runs

A recovery rerun is only useful if:

1. at least `round-0` through `round-3` complete without timeout-class executor exceptions
2. `Role A` and `Role B` still complete cleanly
3. the result can be compared to existing historical baselines without runtime-invalid contamination

## Operational Rule For Future Runs

Use this simple stop rule:

- if executor returns a normal result with no timeout-class exception, continue
- if executor returns a timeout-class exception, stop the run rather than spending more rounds on contaminated state
- only then create one fresh `timeout x2` rerun

This rule is intended to maximize interpretable evidence while avoiding long chains of obviously unproductive rounds.

## Interpretation Rules After Recovery

- if the timeout-expanded rerun becomes runtime-valid and still scores `0.0`, treat that as task evidence
- if the rerun becomes runtime-valid and improves, compare that to the current first-pass batch and note that the earlier failure mode was infrastructural
- if the rerun still times out under doubled multipliers and serial execution, treat that as evidence that the task or runtime envelope needs a more specific executor intervention before further scientific claims
