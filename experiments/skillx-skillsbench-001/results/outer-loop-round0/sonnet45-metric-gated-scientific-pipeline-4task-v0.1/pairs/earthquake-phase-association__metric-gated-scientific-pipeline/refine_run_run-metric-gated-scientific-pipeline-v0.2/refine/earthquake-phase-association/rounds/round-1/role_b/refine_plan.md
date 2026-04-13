# Refine Plan

## Diagnosis

- Round 1 still spent its first full run on a recoverable SeisBench API contract miss: the agent called `len()` on `ClassifyOutput` instead of extracting `.picks`.
- After that patch, the pipeline became runnable but not well-gated. The accepted result had 222 predicted events, while the evaluator window contained 102 catalog events and reported precision `0.468`, recall `0.980`, and F1 `0.634`.
- The highest-signal local fix is therefore not a broader rewrite. It is a bounded contract-tightening pass across three existing blocks: correct the SeisBench `classify()` contract, require a post-run metric gate for GaMMA outputs, and add one concrete picker-threshold retune ladder for the over-splitting case.

## Atomic Operations

1. `op-1` `tighten_block` -> `skills/seisbench-model-api/SKILL.md#classify-function`
Corrected the `classify()` guidance so `PhaseNet.classify()` is treated as `ClassifyOutput` with `.picks`, not a list-like object.
Status: `applied`

2. `op-2` `tighten_block` -> `skills/gamma-phase-associator/SKILL.md#post-association-acceptance-gate`
Added a post-association acceptance gate that requires one evaluator pass or a bounded sanity check before stopping, with exactly one retune pass when the catalog looks over-split.
Status: `applied`

3. `op-3` `tighten_block` -> `skills/seismic-picker-selection/SKILL.md#precision-retune-ladder`
Added a compact retune ladder that raises picker thresholds before changing methods or over-tightening association.
Status: `applied`

## Applied Rewrite

- The staged next skillpack now makes the `ClassifyOutput` contract explicit enough to avoid the round-1 retry.
- GaMMA guidance now treats the first successful `results.csv` as a candidate that still needs a metric check.
- Picker guidance now supplies the missing first retune knob for the high-recall, low-precision failure mode.
