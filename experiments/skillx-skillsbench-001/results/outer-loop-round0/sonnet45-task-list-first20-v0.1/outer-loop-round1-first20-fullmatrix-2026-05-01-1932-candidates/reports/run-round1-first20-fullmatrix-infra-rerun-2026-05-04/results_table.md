# SkillX Round0 Result Table: `run-round1-first20-fullmatrix-infra-rerun-2026-05-04`

- tasks: `3d-scan-calc, data-to-d3`
- pairs: `2/2` completed
- succeeded: `2`
- failed: `0`
- started_at: `2026-05-04T13:56:28.181674+00:00`
- finished_at: `2026-05-04T14:27:12.304886+00:00`
- duration_sec: `1844.123`

## 3d-scan-calc

| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Evidence | Early Stop | Timeout |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- |
| artifact-generation | succeeded | 0 | skipped_baseline_perfect | 80.0 | 80.0 | 100.0 | - | - | - | R0 (100.0) | 20.0 | 20.0 | measured | no | no |

## data-to-d3

| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Evidence | Early Stop | Timeout |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- |
| retrieval-heavy-synthesis | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 100.0 | 100.0 | 0.0 | R1 (100.0) | 40.0 | 20.0 | measured | no | no |

## Evidence Notes

- `3d-scan-calc__artifact-generation`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `data-to-d3__retrieval-heavy-synthesis`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
