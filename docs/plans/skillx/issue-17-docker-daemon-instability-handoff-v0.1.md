# Issue #17 Handoff: Docker Daemon Instability In Large Round0 Sweeps

## Scope

- issue: [#17](https://github.com/jackal092927/skillX/issues/17)
- branch: `bug/issue-17-docker-daemon-instability`
- worktree: `<repo-root>/.worktrees/bug/issue-17-docker-daemon-instability`
- objective: harden the launcher/runtime path so large sweeps fail early and
  clearly when Docker is unhealthy, instead of recording long invalid failure
  streaks

## What Is Already Known

- The late-stage failures in the two larger batches were caused by a Docker
  infrastructure incident, not by task/schema behavior.
- Shared failure signature:
  - `failed_stage = environment_check`
  - `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- Local host triage also showed:
  - `docker info` -> Docker API `Internal Server Error`
  - `docker ps` -> Docker API `Internal Server Error`
  - `docker version` -> Docker API `Internal Server Error` on server side

## Collapse Points

### remaining17x7

- run: `run-remaining-17x7-2026-04-11-v2`
- last success:
  `syzkaller-ppdev-syzlang__engineering-composition`
- first failure:
  `syzkaller-ppdev-syzlang__retrieval-heavy-synthesis`
- onset:
  `2026-04-11T23:06:49.349866+00:00`
- downstream invalid failures: `102`

### next20x7

- run: `run-next20x7-2026-04-11`
- last success:
  `spring-boot-jakarta-migration__retrieval-heavy-synthesis`
- first failure:
  `spring-boot-jakarta-migration__environment-control`
- onset:
  `2026-04-11T22:59:56.967704+00:00`
- downstream invalid failures: `122`

## Authoritative Evidence

- Issue text itself: GitHub issue `#17`
- Remaining-17 debug memo:
  `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/run-remaining-17x7-2026-04-11-v2/debug_memo.md`
- Next20 debug memo:
  `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.3/reports/run-next20x7-2026-04-11/debug_memo.md`
- Cross-run summary:
  `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/round0-40x7-summary-2026-04-12.md`

## Suggested Fix Direction

Focus on infra hardening, not benchmark logic:

1. Add a pre-run Docker health gate before batch launch.
2. Add a mid-run Docker health probe so the launcher can stop early when Docker
   becomes invalid.
3. Preserve structured failure output, but avoid generating long tails of
   analytically useless pair failures.
4. Keep the failure classification explicit as infrastructure failure.

## High-Value Code To Inspect

- `scripts/launch_skillx_round0.py`
- `scripts/run_skillx_refine_benchmark.py`
- `src/skillx/run_failure_utils.py`
- `scripts/run_round0_experiment_tmux.sh`
- `scripts/run_round0_remaining_17x7_tmux.sh`
- `scripts/run_round0_next20x7_tmux.sh`

## Success Criteria For This Branch

- A large sweep with broken Docker should fail fast, before recording a long
  suffix of invalid pair failures.
- The launcher should surface a clear infra-health error.
- The solution should not regress the current report/export pipeline.
- Add tests for the new health-gate behavior.

## Constraints

- Do not overfit to a single literal error string if a slightly broader Docker
  health classification is possible.
- Do not silently suppress failures; classify them clearly.
- Keep the implementation local to launcher/runtime hardening.

## Session Bootstrap Prompt

```text
Work on GitHub issue #17 in this worktree only.

Goal: harden large round0 sweeps against Docker daemon instability.

Known facts:
- remaining17x7 and next20x7 both collapsed into continuous failures after a specific onset point.
- The shared structured failure was:
  RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes
- Live host checks also showed docker info / docker ps / docker version server-side Internal Server Error.
- The right fix direction is preflight + mid-run Docker health gating and clearer infrastructure failure handling.

Start by reading:
- docs/plans/skillx/issue-17-docker-daemon-instability-handoff-v0.1.md
- experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/run-remaining-17x7-2026-04-11-v2/debug_memo.md
- experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.3/reports/run-next20x7-2026-04-11/debug_memo.md

Then inspect launcher/runtime code and implement a fail-fast Docker health strategy with tests.
```
