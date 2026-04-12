# SkillX Round0 Debug Memo: `earthquake-20260411-rerun`

- source report: `run_report.json`
- source matrix: `results_table.md`
- runtime status: `runtime_status.md`
- evaluation matrices: `evaluation_matrices.md`
- run scope: `1 task x 7 schemas = 7 pairs`
- run outcome: `7 succeeded / 0 failed`

## Core Finding

- This rerun fixed the original bundle-construction failure and executed all 7
  `earthquake-phase-association` schemas to completion.
- Despite the operational success, all 7 rerun pairs selected a final score of
  `0.0`.
- Official baselines for this task are:
  - `C0 = 20.0`
  - `C1 = 20.0`
- The resulting delta is therefore `-20.0pp` versus both `C0` and `C1` across
  all 7 schemas.

## Interpretation

- This run is a valid negative-lift result, not another launcher-level failure.
- The rerun shows that once the original skill-discovery bug was removed, the
  current schema-conditioned meta-skill generation still failed to improve this
  task family.
- Several pair-level rounds also record task-local runtime exceptions, so the
  negative-lift story is entangled with environment fragility inside this task.
- The correct next investigation is therefore:
  - inspect the task-specific failure mode for `earthquake-phase-association`
  - separately evaluate whether the current meta-schema / meta-skill guidance is
    mismatched for this task family

## Pair-Level Outcome

| Pair | Final score | Delta vs C0 | Delta vs C1 |
| --- | ---: | ---: | ---: |
| `earthquake-phase-association__artifact-generation` | `0.0` | `-20.0pp` | `-20.0pp` |
| `earthquake-phase-association__analytic-pipeline` | `0.0` | `-20.0pp` | `-20.0pp` |
| `earthquake-phase-association__engineering-composition` | `0.0` | `-20.0pp` | `-20.0pp` |
| `earthquake-phase-association__retrieval-heavy-synthesis` | `0.0` | `-20.0pp` | `-20.0pp` |
| `earthquake-phase-association__environment-control` | `0.0` | `-20.0pp` | `-20.0pp` |
| `earthquake-phase-association__methodology-guardrail` | `0.0` | `-20.0pp` | `-20.0pp` |
| `earthquake-phase-association__orchestration-delegation` | `0.0` | `-20.0pp` | `-20.0pp` |

## Archival Rule

- For `earthquake-phase-association`, use this rerun report as the authoritative
  result record.
- Treat the 7 original `run-3x7-2026-04-10` `earthquake` rows only as evidence
  of the historical `licenses/SKILL.md` bundle-construction bug.
