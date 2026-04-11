# SkillX Round0 Result Table: `run-3x7-2026-04-10`

- tasks: `civ6-adjacency-optimizer, earthquake-phase-association, energy-ac-optimal-power-flow`
- pairs: `21/21` completed
- succeeded: `13`
- failed: `8`
- started_at: `2026-04-10T07:56:04.289489+00:00`
- finished_at: `2026-04-11T06:33:04.887956+00:00`
- duration_sec: `81420.598`

## civ6-adjacency-optimizer

| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Early Stop | Timeout |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- |
| artifact-generation | succeeded | 0 | completed | 0.0 | 14.7 | 0.0 | 0.0 | 60.0 | 0.0 | R2 (60.0) | 60.0 | 45.3 | no | no |
| analytic-pipeline | succeeded | 0 | completed | 0.0 | 14.7 | 0.0 | 55.0 | 0.0 | 0.0 | R1 (55.0) | 55.0 | 40.3 | no | no |
| engineering-composition | succeeded | 0 | completed | 0.0 | 14.7 | 60.0 | 50.0 | 0.0 | 60.0 | R0 (60.0) | 60.0 | 45.3 | no | no |
| retrieval-heavy-synthesis | succeeded | 0 | completed | 0.0 | 14.7 | 60.0 | 0.0 | 0.0 | 55.0 | R0 (60.0) | 60.0 | 45.3 | no | no |
| environment-control | succeeded | 0 | completed | 0.0 | 14.7 | 50.0 | 0.0 | 60.0 | 60.0 | R2 (60.0) | 60.0 | 45.3 | no | no |
| methodology-guardrail | succeeded | 0 | completed | 0.0 | 14.7 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | 0.0 | -14.7 | no | no |
| orchestration-delegation | succeeded | 0 | completed | 0.0 | 14.7 | 0.0 | 0.0 | 35.0 | 0.0 | R2 (35.0) | 35.0 | 20.3 | no | no |

## earthquake-phase-association

| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Early Stop | Timeout |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- |
| artifact-generation | failed | 1 | failed | 20.0 | 20.0 | - | - | - | - | - | - | - | no | no |
| analytic-pipeline | failed | 1 | failed | 20.0 | 20.0 | - | - | - | - | - | - | - | no | no |
| engineering-composition | failed | 1 | failed | 20.0 | 20.0 | - | - | - | - | - | - | - | no | no |
| retrieval-heavy-synthesis | failed | 1 | failed | 20.0 | 20.0 | - | - | - | - | - | - | - | no | no |
| environment-control | failed | 1 | failed | 20.0 | 20.0 | - | - | - | - | - | - | - | no | no |
| methodology-guardrail | failed | 1 | failed | 20.0 | 20.0 | - | - | - | - | - | - | - | no | no |
| orchestration-delegation | failed | 1 | failed | 20.0 | 20.0 | - | - | - | - | - | - | - | no | no |

## energy-ac-optimal-power-flow

| Schema | Launcher | Return | Run | C0 | C1 | R0 | R1 | R2 | R3 | Final Best | dC0 | dC1 | Early Stop | Timeout |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- |
| artifact-generation | failed | 1 | failed | 20.0 | 20.0 | 0.0 | 0.0 | - | - | - | - | - | no | no |
| analytic-pipeline | succeeded | 0 | completed | 20.0 | 20.0 | 100.0 | 0.0 | 0.0 | 0.0 | R0 (100.0) | 80.0 | 80.0 | no | no |
| engineering-composition | succeeded | 0 | completed | 20.0 | 20.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -20.0 | no | no |
| retrieval-heavy-synthesis | succeeded | 0 | completed | 20.0 | 20.0 | 0.0 | 0.0 | 100.0 | 100.0 | R2 (100.0) | 80.0 | 80.0 | no | no |
| environment-control | succeeded | 0 | completed | 20.0 | 20.0 | 0.0 | 0.0 | 0.0 | 0.0 | R0 (0.0) | -20.0 | -20.0 | no | no |
| methodology-guardrail | succeeded | 0 | completed | 20.0 | 20.0 | 0.0 | 100.0 | 0.0 | 100.0 | R1 (100.0) | 80.0 | 80.0 | no | no |
| orchestration-delegation | succeeded | 0 | completed | 20.0 | 20.0 | 0.0 | 0.0 | 100.0 | 0.0 | R2 (100.0) | 80.0 | 80.0 | no | no |

## Failure Notes

- `earthquake-phase-association__artifact-generation`: `FileNotFoundError: [Errno 2] No such file or directory: '~/iWorld/projects/skillsbench-src/tasks/earthquake-phase-association/environment/skills/licenses/SKILL.md'`
- `earthquake-phase-association__analytic-pipeline`: `FileNotFoundError: [Errno 2] No such file or directory: '~/iWorld/projects/skillsbench-src/tasks/earthquake-phase-association/environment/skills/licenses/SKILL.md'`
- `earthquake-phase-association__engineering-composition`: `FileNotFoundError: [Errno 2] No such file or directory: '~/iWorld/projects/skillsbench-src/tasks/earthquake-phase-association/environment/skills/licenses/SKILL.md'`
- `earthquake-phase-association__retrieval-heavy-synthesis`: `FileNotFoundError: [Errno 2] No such file or directory: '~/iWorld/projects/skillsbench-src/tasks/earthquake-phase-association/environment/skills/licenses/SKILL.md'`
- `earthquake-phase-association__environment-control`: `FileNotFoundError: [Errno 2] No such file or directory: '~/iWorld/projects/skillsbench-src/tasks/earthquake-phase-association/environment/skills/licenses/SKILL.md'`
- `earthquake-phase-association__methodology-guardrail`: `FileNotFoundError: [Errno 2] No such file or directory: '~/iWorld/projects/skillsbench-src/tasks/earthquake-phase-association/environment/skills/licenses/SKILL.md'`
- `earthquake-phase-association__orchestration-delegation`: `FileNotFoundError: [Errno 2] No such file or directory: '~/iWorld/projects/skillsbench-src/tasks/earthquake-phase-association/environment/skills/licenses/SKILL.md'`
- `energy-ac-optimal-power-flow__artifact-generation`: `ManualRoleAStallTermination: terminated stalled role_a codex exec after prolonged inactivity so the launcher could continue`
