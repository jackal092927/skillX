# C4AR Trend Execution Handoff

**Audience:** a fresh coding session that should execute, not redesign  
**Experiment:** `experiments/skillx-skillsbench-001`  
**Immediate target:** real `C4AR` shakedown on `trend-anomaly-causal-inference`

Treat all repo paths below as absolute unless otherwise stated.

## Mission

Execute the first real end-to-end `C4AR` loop on:

- `task = trend-anomaly-causal-inference`

Use the already-validated class-aware starting skill as:

- `C2AR = R0`

Do **not** rerun old baselines.
Do **not** redesign the architecture in this session.
Do **not** expand to `taxonomy`, `exoplanet`, or `energy` yet.

The purpose of this session is:

1. prove the new 3-agent `C4AR` pipeline runs end to end in the real environment
2. confirm the result is runtime-valid and scientifically interpretable
3. record the result in the run folder so the next batch decision can be made cleanly

## What Is Already Done

Code is already pushed.

Key code status:

- `Role A` is now playbook-driven and launched via external `codex exec`
- `Role B` is now playbook-driven and launched via external `codex exec`
- `Role C` remains the real Harbor/Docker/Claude Code executor
- thin orchestrator wiring is already in place
- `legacy` and `c4ar` orchestration modes are both supported

Current model split:

- `Role A`: `codex-5.3`
- `Role B`: `gpt-5.4`
- `Role C`: `anthropic/claude-sonnet-4-5`

Current contract split:

- `Task Prompt`: invariant across rounds
- `Skill Pack`: mutable across rounds
- `Role C` must only consume:
  - task prompt
  - current skillpack
  - bundle if present
- `Role C` must not consume:
  - refine plan
  - round decision
  - session evidence

## Prior Verified Result

This task already has a verified `R0` shakedown:

- `R0 = 0.8444`
- runtime-valid
- no build failure
- no setup failure
- no verifier exception
- no timeout contamination

Reference files:

- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/RESULT_SUMMARY.md`
- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/RUN_STATUS.md`

Interpretation of the starting point:

- better than old `C1 = 0.7444`
- better than old generic `C3 = 0.7944`
- still below old generic `C2 = 0.9`
- still below old `C0 = 1.0`

So `R0` is credible, but not yet dominant.

## Required Reading Order

1. `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/agent_handoff/C4AR_TREND_EXECUTION_HANDOFF.md`
2. `<INCUBATOR_REPO_ROOT>/docs/superpowers/plans/2026-03-25-mac-autoresearch-real-c4-experiment-plan.md`
3. `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/RUN_BRIEF.md`
4. `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/BASELINE_VALIDITY.md`
5. `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/playbooks/C4AR_ROLE_A_SESSION_DISTILL_PLAYBOOK.md`
6. `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/playbooks/C4AR_ROLE_B_REFINE_BRAIN_PLAYBOOK.md`

## Preflight

Before running, verify:

- repo root exists:
  - `<INCUBATOR_REPO_ROOT>`
- SkillsBench root exists:
  - `<SKILLSBENCH_ROOT>`
- venv Python works:
  - `./.venv-swebench/bin/python`
- Docker works
- `uv` works
- Claude OAuth file exists:
  - `<CLAUDE_CODE_OAUTH_TOKEN_FILE>`
- `codex exec` works in the current shell

Do not switch the pipeline to API-token mode just because auth is inconvenient.
Keep the current CLI/authentication-based runtime unless there is a real blocker.

## Frozen Inputs

Use these exact starting inputs for the `trend` run:

- `source_run_dir`
  - `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001`
- `starting_skillpack_dir`
  - `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/materialized_skillpacks/trend-anomaly-causal-inference/c2_class_aware`
- `starting_label`
  - `r0`
- `oauth_file`
  - `<CLAUDE_CODE_OAUTH_TOKEN_FILE>`
- `skillsbench_root`
  - `<SKILLSBENCH_ROOT>`
- `output_dir`
  - `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/task_runs/trend-c4ar-001`

Use these tune evidence dirs:

- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/negative-transfer-candidate-check-002-adjusted`
- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/rewrite-benchmark-003-harbor-rewrite`
- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/task_runs/trend-r0-001`

Do not pass a starting bundle unless you confirm a real bundle file exists for this `R0`.
The current class-aware `trend` starting pack is skill-only.

## Execution Command

Run exactly one task, in `c4ar` mode:

```bash
./.venv-swebench/bin/python mac_autoresearch_support/scripts/run_skillx_refine_benchmark.py \
  --skillsbench-root <SKILLSBENCH_ROOT> \
  --task trend-anomaly-causal-inference \
  --run-id trend-c4ar-001 \
  --output-dir <INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/task_runs/trend-c4ar-001 \
  --oauth-file <CLAUDE_CODE_OAUTH_TOKEN_FILE> \
  --source-run-dir <INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001 \
  --starting-skillpack-dir <INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/materialized_skillpacks/trend-anomaly-causal-inference/c2_class_aware \
  --starting-label r0 \
  --tune-run-dir <INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/negative-transfer-candidate-check-002-adjusted \
  --tune-run-dir <INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/rewrite-benchmark-003-harbor-rewrite \
  --tune-run-dir <INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/task_runs/trend-r0-001 \
  --round-budget 3 \
  --round-timeout-multiplier 2.0 \
  --tune-timeout-multiplier 3.0 \
  --orchestration-mode c4ar
```

## Runtime Expectations

For each active round, expect:

- `Role C` runs first and produces a real benchmark result
- `Role A` reads the resulting session log and writes:
  - `role_a/session_evidence.json`
  - `role_a/session_evidence.md`
- `Role B` reads the verifier result, session evidence, and current skillpack, then writes:
  - `role_b/refine_plan.json`
  - `role_b/refine_plan.md`
  - `role_b/next_skillpack_manifest.json`
  - `role_b/round_decision.json`
  - updated `next_skillpack/`

The orchestrator should remain thin:

- start step
- wait/check step completion
- validate artifacts
- hand off to next role

## Acceptance Gates

Do not call this run successful just because the code exits cleanly.

The run is acceptable only if all of the following are true:

1. **Runtime-valid**
   - no Docker build failure
   - no setup failure
   - no verifier parse failure
   - no timeout-only collapse

2. **Role handoff-valid**
   - `Role A` outputs exist and validate
   - `Role B` outputs exist and validate
   - `Role C` input boundary is preserved

3. **Scientifically interpretable**
   - `R0`, `R1..R3`, and final selection can be read from artifacts
   - the final result can be compared to:
     - `C1`
     - `C2AR = R0`
   - the observed failure or improvement mode is understandable

## What To Record

Update these files after the run:

- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/RUN_STATUS.md`
- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/EXECUTION_LOG.md`
- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/RESULT_SUMMARY.md`

Also write a short checkpoint-style note under the new task run dir if the end-to-end shakedown finishes.

## Stop Conditions

Stop and document a blocker if any of these happens:

- `codex exec` auth/runtime fails for Role A or Role B
- Role A or Role B produces malformed structured output
- Role C sees refine-only artifacts in its sandbox
- the run completes but the result is clearly runtime-invalid

Do not proceed to other tasks in this session.

## Definition of Done for This Session

This session is done only if one of these is true:

1. `trend` `C4AR` end-to-end shakedown completes and the result is documented
2. a concrete blocker is identified, written down, and tied to the exact failing stage

Nothing else is required in this handoff session.
