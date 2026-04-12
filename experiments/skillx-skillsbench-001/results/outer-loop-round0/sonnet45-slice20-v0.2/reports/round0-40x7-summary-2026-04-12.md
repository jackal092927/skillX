# SkillX Round0 40x7 Summary

## Summary

- Effective unique coverage now spans `40 tasks x 7 schemas = 280 unique pairs`.
- Total launcher executions across all runs were `287` pairs because
  `earthquake-phase-association` was rerun after the original 7-pair failure.
- The authoritative first-batch interpretation is:
  - use `run-3x7-2026-04-10` for `civ6-adjacency-optimizer` and
    `energy-ac-optimal-power-flow`
  - use `earthquake-20260411-rerun` for `earthquake-phase-association`

## Run Table

| Run | Scope | Executed pairs | Succeeded | Failed | Analytically usable as-is | Notes |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `run-3x7-2026-04-10` | first `3 x 7` | `21` | `13` | `8` | partial | original `earthquake` rows superseded by rerun |
| `earthquake-20260411-rerun` | `earthquake` only | `7` | `7` | `0` | yes | operationally clean rerun, but all 7 are negative lift |
| `run-remaining-17x7-2026-04-11-v2` | remaining `17 x 7` | `119` | `17` | `102` | only first `17` pairs | continuous Docker failure began at pair `18` |
| `run-next20x7-2026-04-11` | next `20 x 7` | `140` | `18` | `122` | only first `18` pairs | continuous Docker failure began at pair `19` |

## Authoritative Coverage

- Authoritative usable pair outcomes currently available:
  - first task block: `21`
    - original `3x7`, except `earthquake` taken from rerun
  - remaining-17 block before Docker collapse: `17`
  - next20 block before Docker collapse: `18`
- Total analytically usable pair outcomes currently available: `56`

## Known Caveats

- `earthquake-phase-association` is a valid negative-lift result after rerun, not
  an unresolved launcher failure.
- The latter two large batches suffered a shared infrastructure incident:
  `Docker memory too low: 0 bytes < required 16000000000 bytes`
- On `2026-04-12`, local `docker info`, `docker ps`, and `docker version` all
  returned Docker API `Internal Server Error`, which is consistent with the
  failure signature recorded in those runs' `run_failure.json` files.
- Because of that Docker incident, the post-collapse failures in the latter two
  batches should not be interpreted as evidence against the affected
  tasks/schemas.

## Pointers

- Original first batch:
  `run-3x7-2026-04-10/`
- Earthquake rerun:
  `earthquake-20260411-rerun/`
- Remaining 17 batch:
  use branch `exp/2026-04-11-round0-remaining-17x7`
- Next 20 batch:
  use branch `exp/2026-04-11-round0-next20x7`
