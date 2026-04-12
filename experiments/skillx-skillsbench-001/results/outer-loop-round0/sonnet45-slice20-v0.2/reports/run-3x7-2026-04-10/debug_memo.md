# SkillX Round0 Debug Memo: `run-3x7-2026-04-10`

- source report: `run_report.json`
- source matrix: `results_table.md`
- runtime status: `runtime_status.md`
- evaluation matrices: `evaluation_matrices.md`
- original run scope: `3 tasks x 7 schemas = 21 pairs`
- original run outcome: `13 succeeded / 8 failed`

## Authoritative Follow-Up

- `earthquake-phase-association` should no longer be read from the original `run-3x7-2026-04-10` result rows.
- The authoritative replacement is the dedicated rerun:
  `reports/earthquake-20260411-rerun/`
- Integration details are recorded in:
  `earthquake_followup_integration.md`

## Original Run Findings

### 1. `earthquake-phase-association` failed at bundle construction, not at tuning

- All 7 original `earthquake-phase-association` pairs failed almost immediately.
- The common root cause was:
  `FileNotFoundError: .../environment/skills/licenses/SKILL.md`
- This means the original run was trying to treat `licenses/` as a skill directory during static bundle assembly.
- The failure happened before any useful `R0-R3` round scores were produced for those original 7 pairs.

### 2. `energy-ac-optimal-power-flow__artifact-generation` failed after partial progress

- This pair completed `R0`, then reached `R1 role_a`.
- The final recorded failure payload is:
  `ManualRoleAStallTermination`
- The failure artifact says the `role_a` Codex process was terminated after prolonged inactivity so the launcher could continue.
- The recorded failure location is:
  `failed_stage = role_a`
  `failed_round = 1`
- This is operationally different from the `earthquake` failures:
  the pair did produce partial round evidence before stopping.

### 3. Launcher status was authoritative; some pair-local run status files were stale

- For the 7 failed original `earthquake-phase-association` pairs, launcher logs clearly recorded `pair_failed`.
- Their pair-local `RUN_STATUS.md` files still showed `running`.
- The exported `run_report.json` treats launcher outcome as the source of truth and marks these as failed while preserving the stale raw run status.

## Branch Deltas Already Present

Relative to `origin/exp/2026-04-10-round0-3x7`, this worktree already contains four experiment-driven fixes:

- `192d0b1` `Fix Claude Harbor false timeout handling`
- `c45977b` `Tighten tune timeout retry handling`
- `22fcaa0` `Handle stalled C4AR role agent failures`
- `2ec40b4` `Harden SkillX skill discovery`

What these commits appear to have addressed:

- false positive Harbor/Claude timeout interpretation
- retry behavior around tune timeout outcomes
- role-agent failure handling inside the C4AR loop
- filtering non-skill directories such as `licenses/` out of skill discovery

## Follow-Up Rerun Snapshot On This Branch

This branch already contains follow-up `earthquake` reruns:

- `earthquake-phase-association__artifact-generation/refine_run_earthquake-20260411-rerun`
  status: `completed`
  updated_at: `2026-04-11T06:21:57.302073+00:00`
- `earthquake-phase-association__analytic-pipeline/refine_run_earthquake-20260411-rerun`
  status: `completed`
  updated_at: `2026-04-11T06:55:42.667759+00:00`
- `earthquake-phase-association__engineering-composition/refine_run_earthquake-20260411-rerun`
  status: `running`
  updated_at: `2026-04-11T06:55:43.055159+00:00`

At memo capture time there was still an active rerun process for:

- `earthquake-phase-association__engineering-composition__earthquake-20260411-rerun`

This is useful evidence that the `licenses/` discovery problem was already fixed on this branch:
the reruns are now able to get past the original immediate bundle failure.

## Still Worth Modifying Next

### 1. Promote the launcher path fix into the branch baseline

- The current worktree contains a launcher fix so command build in the real run path receives `materialized_root`.
- Without that, the launcher can still fall back to absolute `pair_dir` paths baked into `pair_specs.jsonl`.

### 2. Stop materialized specs from pinning output to the main repo path

- `pair_specs.jsonl` still contains absolute `pair_dir` and `--output-dir` paths under the main repo checkout.
- That is why this run launched from a worktree but wrote pair outputs back into the main repo path.
- Future collaboration will be cleaner if materialized pair specs become repo-relative or are re-rooted to the active worktree.

### 3. Make structured failure payloads consistent for manual/operator interventions

- This run has a useful `ManualRoleAStallTermination` failure artifact.
- That is exactly the kind of structured signal we want, but it does not appear to be guaranteed by the generic top-level failure writer.
- Future hardening should make `run_failure.json` consistently include:
  `error_type`, `error_message`, `failed_stage`, `failed_round`, and `manual_intervention`.

### 4. Continue targeted reruns, not a blind full rerun

- Finish the `earthquake-phase-association` rerun sweep first.
- Then rerun `energy-ac-optimal-power-flow__artifact-generation` with the current branch fixes.
- Do not rerun the entire original `3x7` until the remaining failure modes are confirmed closed.
