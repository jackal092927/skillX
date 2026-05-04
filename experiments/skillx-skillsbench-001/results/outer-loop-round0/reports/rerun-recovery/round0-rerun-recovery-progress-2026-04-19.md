# Round0 Rerun Recovery Progress Checkpoint 2026-04-19

- branch: `exp/2026-04-13-round0-rerun-recovery`
- worktree: `.worktrees/exp/2026-04-13-round0-rerun-recovery`
- checkpoint purpose: preserve rerun progress after an unexpected host restart terminated tmux, terminal, and Docker-side execution

## Current Recovery State

- frozen rerun target: `224` pair(s)
- first recovery run: `run-round0-rerun-recovery-2026-04-13-v1`
- resumed run: `run-round0-rerun-recovery-2026-04-14-resume1`
- current authoritative summary file:
  `experiments/skillx-skillsbench-001/results/outer-loop-round0/round0-rerun-recovery-v0.1/launcher_logs/run-round0-rerun-recovery-2026-04-14-resume1/summary.json`

## Effective Completed Coverage

- `v1` completed `18/224` pair(s) successfully before launcher-side interruption
- `resume1` completed `131/206` pair(s) successfully before the host restart
- effective recovered total so far: `149/224` pair(s)
- effective remaining total so far: `75/224` pair(s)

## What Happened In The Two Runs

### `run-round0-rerun-recovery-2026-04-13-v1`

- final good pair before interruption:
  `data-to-d3__environment-control`
- task execution itself succeeded at
  `2026-04-13T23:58:54.315214+00:00`
- launcher then recorded a `run_exception` with
  `error = [Errno 32] Broken pipe`
- this interrupted batch accounting after `18` fully recorded successes

### `run-round0-rerun-recovery-2026-04-14-resume1`

- selected remaining scope: `206` pair(s)
- current recorded progress: `131` succeeded, `0` failed
- last fully completed pair:
  `sec-financial-report__analytic-pipeline`
- completion timestamp:
  `2026-04-18T23:23:46.836962+00:00`
- next pair that had already started when the host restarted:
  `sec-financial-report__engineering-composition`

## Last Known In-Flight Pair

Pair:
- `sec-financial-report__engineering-composition`

Run directory:
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/round0-rerun-recovery-v0.1/pairs/sec-financial-report__engineering-composition/refine_run_run-round0-rerun-recovery-2026-04-14-resume1`

Last known pair-local state:
- `RUN_STATUS.md` still says `running`
- `round-0` exists
- `executor_completed` is recorded
- `role_a_completed` is recorded at `2026-04-18T23:31:26.674094+00:00`
- `role_b_completed` is not recorded
- `role_b` has already staged `next_skillpack/` content and wrote research packet artifacts

Practical interpretation:
- the interrupted pair was not blocked in Docker bootstrap
- it had already entered `C4AR round-0 / role_b`
- the safest restart assumption is "resume from pair 132 onward", not "resume from the start of the batch"

## Docker Fix Validation So Far

The resumed run provides positive evidence for the Docker hardening work:

- `resume1` has progressed through `131` pair(s) with `0` recorded failures
- the latest event before the restart is still a healthy Docker probe for pair `132`
- no repeated `docker_incident` suffix has reappeared in the resumed batch so far

This does not prove the rerun is fully done, but it does show that the previous daemon-instability failure mode did not recur during the first `131` resumed pairs.

## Key Evidence Files

- `experiments/skillx-skillsbench-001/results/outer-loop-round0/round0-rerun-recovery-v0.1/launcher_logs/run-round0-rerun-recovery-2026-04-13-v1/summary.json`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/round0-rerun-recovery-v0.1/launcher_logs/run-round0-rerun-recovery-2026-04-13-v1/events.ndjson`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/round0-rerun-recovery-v0.1/launcher_logs/run-round0-rerun-recovery-2026-04-14-resume1/summary.json`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/round0-rerun-recovery-v0.1/launcher_logs/run-round0-rerun-recovery-2026-04-14-resume1/events.ndjson`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/round0-rerun-recovery-v0.1/pairs/sec-financial-report__engineering-composition/refine_run_run-round0-rerun-recovery-2026-04-14-resume1/RUN_STATUS.md`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/round0-rerun-recovery-v0.1/pairs/sec-financial-report__engineering-composition/refine_run_run-round0-rerun-recovery-2026-04-14-resume1/refine/sec-financial-report/rounds/round-0/orchestrator_log.ndjson`

## Recommended Next Step

Use the resume manifest:

- `experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/rerun-recovery/round0-rerun-recovery-v0.1.resume-after-run-round0-rerun-recovery-2026-04-13-v1.pair-manifest.json`

and restart from the last incomplete pair forward rather than rerunning the already recovered `149` pair(s).
