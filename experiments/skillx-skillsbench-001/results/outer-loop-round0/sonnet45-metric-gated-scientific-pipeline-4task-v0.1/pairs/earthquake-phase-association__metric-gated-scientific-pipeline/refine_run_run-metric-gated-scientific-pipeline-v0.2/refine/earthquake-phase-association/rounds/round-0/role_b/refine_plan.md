# Refine Plan

## Diagnosis

- Round 0 underperformed because GaMMA setup failed serially at runtime: first `KeyError: 'oversample_factor'`, then a second rerun was needed before the missing `z(km)` contract was fully addressed.
- The failure pattern was not a modeling problem; it was a documentation-contract problem in `gamma-phase-associator/SKILL.md`. The skill listed some required pieces, but not the full copyable BGMM key set in one place.
- The highest-signal local fix is to make the full `association()` preflight explicit and add one known-good BGMM config block that includes the missing keys together.

## Atomic Operations

1. `op-1` `tighten_block` -> `skills/gamma-phase-associator/SKILL.md#association-preflight`
Added a one-pass preflight that checks `stations.columns`, `picks.columns`, and the complete required config contract before rerun.
Status: `applied`

2. `op-2` `rewrite_block` -> `skills/gamma-phase-associator/SKILL.md#config-required-keys`
Expanded the required config table so `x(km)`, `y(km)`, `z(km)`, and the `oversample_factor` guardrail are documented together.
Status: `applied`

3. `op-3` `rewrite_block` -> `skills/gamma-phase-associator/SKILL.md#minimal-bgmm-config`
Added a compact `use_amplitude=False` BGMM starter config that can be copied without omitting the keys that caused the round-0 retry loop.
Status: `applied`

## Applied Rewrite

- The staged next skillpack now tells the executor to stop after the first GaMMA `KeyError` and audit the full contract before rerunning.
- The required-key documentation now distinguishes station coordinate columns from config search-bound keys that share the same names.
- A single BGMM snippet now covers the working key set that avoided the round-0 missing-key loop.
