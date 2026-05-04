# SkillX Post Inner-Loop Audit Reference v0.1

## Purpose

After each inner-loop run completes, run a post-inner-loop audit before feeding
results into outer-loop optimization. The audit separates clean evidence from
runtime or infrastructure artifacts, then prepares targeted rerun manifests.

Source of truth:

- `scripts/audit_skillx_inner_loop_results.py`
- `tests/test_audit_skillx_inner_loop_results.py`

## Rerun Policy

| Decision | Meaning | Outer-loop use |
| --- | --- | --- |
| `required` | Current result is invalid or too questionable to trust. | Do not feed into outer-loop until rerun or explicitly overridden. |
| `recommended` | Result has usable signal, but the trajectory is not clean. | Outer-loop may continue if cost matters, but rerun is preferred for clean evidence. |
| `none` | No rerun needed by default. | Safe to consume, possibly with notes. |

## Reference Examples From Round1 First20

These examples are intentionally mirrored by synthetic tests so future code
changes preserve the intended classification.

| Pair | Observed issue | Decision | Reason |
| --- | --- | --- | --- |
| `adaptive-cruise-control__retrieval-heavy-synthesis` | `failed` with `expected exactly one trial dir ... found 0` | `required` | The R0 tune_check artifact was incomplete, so no valid inner-loop result exists. |
| `data-to-d3__retrieval-heavy-synthesis` | `completed_with_runtime_failures`, selected `R0`, score `0.0`, runtime failures in later rounds | `required` | Later rounds did not produce reliable evidence and may hide possible improvement. |
| `3d-scan-calc__artifact-generation` | `completed_with_runtime_failures`, runtime failures in early rounds, selected positive clean round | `recommended` | The selected result has positive evidence, but the trajectory is not clean. |

## Non-Rerun Notes

- `rate_limit_fallback` is not a rerun reason by itself when final evidence is
  complete; it is recorded as `valid_with_notes`.
- Claude account fallback is not a model-family change and is not a rerun reason
  by itself.
- `basic_model_fallback` is a rerun-required issue because it changes the
  executor/model family.
- `skipped_baseline_perfect` is an intentional R0 guard outcome, not a failure.

## Standard Command

```bash
python3 scripts/audit_skillx_inner_loop_results.py \
  --materialized-root <materialized-root> \
  --run-label <inner-run-label>
```

The outer-loop wrapper runs this by default and stops before global status
rebuild when `rerun_required > 0`.
