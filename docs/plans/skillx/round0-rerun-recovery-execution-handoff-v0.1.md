# SkillX Round0 Rerun Recovery Execution Handoff v0.1

- **Project:** `projects/skillX`
- **Branch:** `exp/2026-04-13-round0-rerun-recovery`
- **Worktree:** `<repo-root>/.worktrees/exp/2026-04-13-round0-rerun-recovery`
- **Status:** ready for execution

---

## 1. Mission

Run the repaired round0 rerun-recovery flow from a clean experiment worktree.

This branch is not for new implementation. It is an execution branch for:

- one canary run
- one full rerun-recovery batch
- one post-run finalize pass

The frozen rerun target is already defined and should not be edited during the
run unless the canary reveals a real blocker.

---

## 2. Source Of Truth

Read these first:

- `docs/plans/skillx/round0-rerun-recovery-handoff-v0.1.md`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/rerun-recovery/round0-rerun-recovery-v0.1.md`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/rerun-recovery/round0-rerun-recovery-v0.1.pair-manifest.json`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/global-round0-status/global_status_matrix.md`

The current frozen rerun scope is:

- `224` total pairs
- `217` latest `docker_incident`
- `7` `setup-fuzzing-py` verifier-contract reruns

Excluded by default:

- `energy-ac-optimal-power-flow__artifact-generation`

---

## 3. Scripts To Use

Use only these scripts for this execution branch:

- canary launcher:
  `scripts/run_round0_rerun_canary_tmux.sh`
- full rerun launcher:
  `scripts/run_round0_rerun_recovery_tmux.sh`
- monitor:
  `scripts/run_round0_monitor.sh`
- finalize:
  `scripts/finalize_round0_rerun_recovery.sh`
- rematerialize:
  `scripts/rematerialize_round0_rerun_recovery_root.sh`

Do not manually reconstruct the pair list in the shell.

---

## 4. Default Run Order

### Step A. Canary

Run the canary first:

- `setup-fuzzing-py__artifact-generation`
- `spring-boot-jakarta-migration__environment-control`

Default command:

```bash
scripts/run_round0_rerun_canary_tmux.sh
```

Expected behavior:

- rematerialize the rerun-recovery root
- open a tmux session with `run` and `dashboard`
- serve a dashboard on the first free port starting at `8770`

Canary success means:

- both pairs launch successfully
- neither pair fails immediately in `discover_task_inputs`
- neither pair fails immediately in `docker_health_gate`
- real round execution begins and run artifacts appear

If the canary fails, stop and debug. Do not start the full 224-pair batch.

### Step B. Full rerun recovery

Only after canary success:

```bash
scripts/run_round0_rerun_recovery_tmux.sh
```

Expected behavior:

- uses the frozen pair manifest
- selects exactly `224` pairs
- writes outputs under:
  `experiments/skillx-skillsbench-001/results/outer-loop-round0/round0-rerun-recovery-v0.1`
- serves a dashboard on the first free port starting at `8771`

### Step C. Finalize

After the full batch ends:

```bash
scripts/finalize_round0_rerun_recovery.sh run-round0-rerun-recovery-2026-04-13
```

This will:

- export the structured run report
- rebuild global round0 status

---

## 5. Operational Notes

- Use a fresh run label if you rerun the canary or full batch.
- Do not reuse a non-empty `launcher_logs/<run-label>` directory.
- The monitor script now supports a custom results root; use it if you need to
  inspect the rerun-recovery root manually.
- The rerun-recovery materialized root is generated at runtime and should not be
  edited by hand.

---

## 6. Session Bootstrap Prompt

```text
Work only in this worktree:
/Users/Jackal/iWorld/projects/skillX/.worktrees/exp/2026-04-13-round0-rerun-recovery

Goal: execute the round0 rerun-recovery flow on the repaired codebase.

Read first:
- docs/plans/skillx/round0-rerun-recovery-execution-handoff-v0.1.md
- docs/plans/skillx/round0-rerun-recovery-handoff-v0.1.md
- experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/rerun-recovery/round0-rerun-recovery-v0.1.md

Do not redesign the rerun scope unless the canary exposes a concrete blocker.

Execution order:
1. Run the canary via scripts/run_round0_rerun_canary_tmux.sh
2. Inspect tmux/dashboard/logs and confirm the canary is healthy
3. If healthy, run the full batch via scripts/run_round0_rerun_recovery_tmux.sh
4. After completion, run scripts/finalize_round0_rerun_recovery.sh with the actual run label
5. Summarize the new global-status deltas and remaining blockers

Stay focused on execution, monitoring, and post-run bookkeeping. Do not start unrelated code changes unless the canary or full rerun reveals a real bug.
```
