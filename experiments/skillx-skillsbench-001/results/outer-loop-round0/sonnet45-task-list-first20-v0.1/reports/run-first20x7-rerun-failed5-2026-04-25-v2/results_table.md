# SkillX Round0 Result Table: `run-first20x7-rerun-failed5-2026-04-25-v2`

- tasks: `azure-bgp-oscillation-route-leak, data-to-d3`
- pairs: `5/5` completed
- succeeded: `5`
- failed: `0`
- started_at: `2026-04-26T03:15:19.620881+00:00`
- finished_at: `2026-04-26T04:21:25.623273+00:00`
- duration_sec: `3966.002`

## azure-bgp-oscillation-route-leak

| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Evidence | Early Stop | Timeout |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- |
| analytic-pipeline | succeeded | 0 | completed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | R3 (100.0) | 100.0 | 100.0 | measured | no | no |
| engineering-composition | succeeded | 0 | completed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | 0.0 | 0.0 | measured | no | no |
| retrieval-heavy-synthesis | succeeded | 0 | completed | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | 0.0 | 0.0 | measured | no | no |

## data-to-d3

| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Evidence | Early Stop | Timeout |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- |
| environment-control | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 100.0 | 0.0 | 0.0 | R1 (100.0) | 40.0 | 20.0 | measured | no | no |
| methodology-guardrail | succeeded | 0 | completed | 60.0 | 80.0 | 0.0 | 100.0 | 0.0 | 0.0 | R1 (100.0) | 40.0 | 20.0 | measured | no | no |

## Evidence Notes

- `azure-bgp-oscillation-route-leak__analytic-pipeline`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `azure-bgp-oscillation-route-leak__engineering-composition`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `azure-bgp-oscillation-route-leak__retrieval-heavy-synthesis`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `data-to-d3__environment-control`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
- `data-to-d3__methodology-guardrail`: `measured` - Clean verifier-facing score available for comparison against C0/C1.
