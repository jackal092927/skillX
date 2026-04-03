# SkillX Progress Checkpoint — 2026-03-26

## Addendum — 2026-03-28 Batch Closeout

The batch that was still open at the time of this progress checkpoint is now closed out.

Final readout:

- `trend`
  - clean uninterrupted full-chain `C4AR` success
  - best observed reward `0.95`
  - freeze `R1`
- `taxonomy`
  - best retained result `0.7712`
  - evidence spans a damaged default-timeout rerun plus a later `R2` resume branch
- `energy`
  - clean `R0 = 1.0`
  - run intentionally stopped after `R0` because no score headroom remained
- `exoplanet`
  - completed through `R3`
  - clean `0.0` through `R2`
  - `R3` timed out

Important caveat:

- not all four task lines were uninterrupted `R0 -> R3` chains
- only `trend` meets that standard

Authoritative closeout references:

- [`MILESTONE_REPORT_2026-03-28_C4AR_BATCH_CLOSEOUT.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/MILESTONE_REPORT_2026-03-28_C4AR_BATCH_CLOSEOUT.md)
- [`SUMMARY_2026-03-28_C4AR_BATCH_CLOSEOUT.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/SUMMARY_2026-03-28_C4AR_BATCH_CLOSEOUT.md)
- [`CHECKPOINT_2026-03-28_C4AR_BATCH_CLOSEOUT.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/CHECKPOINT_2026-03-28_C4AR_BATCH_CLOSEOUT.md)
- [`C4AR_BATCH_CLOSEOUT_HANDOFF_2026-03-28.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/agent_handoff/C4AR_BATCH_CLOSEOUT_HANDOFF_2026-03-28.md)

## Scope

This checkpoint records the current project state after the shift from:

- prior handcrafted `C4`

to:

- class-aware `C2AR` starting skills
- the new `C4AR` architecture
- the real 3-agent inner-loop design

This is a **progress checkpoint**, not just a code checkpoint.
It is intended to let a new session continue both:

1. the completed `trend` result interpretation
2. the broader multi-task project evolution after that result landed

## High-Level Status

The project is now in a mixed state:

- the old `C3 / C4` line is complete enough to serve as a scientific reference
- the new `C2AR / C4AR` line is architecturally ready
- the first real `R0 = C2AR` shakedown was already validated on `trend`
- the first real end-to-end `C4AR` loop has now been run on `trend`
- the accepted `trend` run has been fully completed through `round_budget = 3`
- the three remaining frozen tasks have now each been executed once

So the current state is:

- **design complete enough**
- **code bridge complete enough**
- **starting-point execution validated**
- **four full `C4AR` task runs completed**
- **batch expansion executed once**
- **runtime recovery rerun logic hardened**
- **one taxonomy rerun numerically salvaged but not fully artifact-reproducible**

## What Was Already Completed Before C4AR

### 1. Historical baseline work

The project already established usable historical anchors:

- `C0` — no skill
- `C1` — original skill
- `C2` — generic SkillX minimal rewrite
- `C3` — generic SkillX derived
- prior handcrafted `C4`

The strongest historical takeaways were:

- `trend-anomaly-causal-inference` was a real negative-transfer task
- prior handcrafted `C4` materially improved `trend`
- `exoplanet` and `energy` did not improve under prior handcrafted `C4`

Reference:

- [`CHECKPOINT_2026-03-24_C3_C4_BATCH_001.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/CHECKPOINT_2026-03-24_C3_C4_BATCH_001.md)

### 2. Negative-transfer PoC direction was frozen

The project then explicitly moved away from:

- family-coverage comparison

and toward:

- negative-transfer repair proof of concept

Frozen task set for this PoC:

- `trend-anomaly-causal-inference`
- `taxonomy-tree-merge`
- `exoplanet-detection-period`
- `energy-ac-optimal-power-flow`

The intent is:

- start from new class-aware `C2AR`
- treat runtime `R0` as the measured execution of that `C2AR`
- then let MAC AutoResearch refine from there

Reference:

- [`RUN_BRIEF.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/RUN_BRIEF.md)
- [`BASELINE_VALIDITY.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/BASELINE_VALIDITY.md)

## What Is Already Validated In The New C2AR/C4AR Line

### 1. `R0 = C2AR` was executed for `trend`

This has already been run in the real environment:

- environment:
  - Harbor
  - Docker
  - Claude Code
  - deterministic SkillsBench verifier
- task:
  - `trend-anomaly-causal-inference`
- condition:
  - `R0 = class-aware C2 starting skill`

Verified result:

- `R0 = 0.8444`
- runtime-valid
- no infra contamination

Interpretation:

- better than old `C1 = 0.7444`
- better than old generic `C3 = 0.7944`
- still below old generic `C2 = 0.9`
- still below old `C0 = 1.0`

This means:

- the new class-aware starting point is not broken
- it is scientifically credible
- it is worth refining
- but it is not yet the best known score on `trend`

Reference:

- [`RESULT_SUMMARY.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/RESULT_SUMMARY.md)
- [`RUN_STATUS.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/RUN_STATUS.md)

### 2. The new C4AR code path is built

The following are already implemented:

- typed handoff contracts
- thin per-task orchestrator
- playbook-driven `Role A`
- playbook-driven `Role B`
- preserved `Role C`
- `legacy` vs `c4ar` orchestration switch

Current role split:

- `Role A`
  - external `codex exec`
  - model label: `codex-5.3`
  - job: distilled session evidence
- `Role B`
  - external `codex exec`
  - model label: `gpt-5.4`
  - job: diagnosis, atomic refine plan, next skillpack
- `Role C`
  - Harbor/Docker executor
  - model: `anthropic/claude-sonnet-4-5`
  - job: benchmark execution only

### 3. Role boundaries are frozen

These boundaries are now explicit:

- `Task Prompt` is fixed across rounds
- only the `Skill Pack` changes
- `Role C` does not read:
  - refine plan
  - round decision
  - session evidence
- `Role A/B` are the only research roles

This is important because it means the new loop is actually testing:

- skill refinement

not:

- hidden prompt optimization

## New Recovery-State Update

After the first post-`trend` batch, additional recovery work established:

- `energy-ac-optimal-power-flow`
  - clean `C1 = 0.0`
  - clean class-aware `R0 = 1.0`
  - freeze as complete for now
- `taxonomy-tree-merge`
  - default-timeout recovery rerun reached:
    - `R0 = 0.7212`
    - `R1 = 0.7596`
    - `R2 = 0.2654` with timeout
  - but a failed resume attempt damaged part of that run's top-level artifact tree
  - numeric evidence is still retained
  - full original artifact reproducibility is not

So the project is no longer in a simple "recovery planning pending" state.
It is now in a mixed recovery-execution state:

- some tasks already have clean resolved evidence
- some tasks have salvageable but artifact-damaged evidence
- remaining work should proceed only with the hardened resume safeguards

## What The New System Looks Like Right Now

### Thin orchestrator

The orchestrator is intentionally not a fourth intelligent agent.

It does only:

1. prepare round directories
2. launch `Role C`
3. wait for completion / validate outputs
4. launch `Role A`
5. wait for completion / validate outputs
6. launch `Role B`
7. wait for completion / validate outputs
8. materialize next round state

So the architecture is:

- `3 agents`
- `1 thin process controller`

### Role A

`Role A` is now agent-backed, not just local heuristics.

It uses:

- preprocessed session packet
- `C4AR_ROLE_A_SESSION_DISTILL_PLAYBOOK.md`
- external `codex exec`

It produces:

- `session_evidence.json`
- `session_evidence.md`

### Role B

`Role B` is now agent-backed, not just local template generation.

It uses:

- verifier summary
- session evidence
- current skillpack
- `C4AR_ROLE_B_REFINE_BRAIN_PLAYBOOK.md`
- external `codex exec`

It produces:

- `refine_plan.json`
- `refine_plan.md`
- `next_skillpack_manifest.json`
- `round_decision.json`
- edited `next_skillpack/`

### Role C

`Role C` remains intentionally boring:

- real benchmark execution only
- no access to research artifacts
- same style of execution as the already-validated `R0`

## What Has Been Verified Technically

The new code path is not just uncompiled code.

The following have already been verified locally:

- contracts compile
- A/B/C bridge compiles
- tests pass
- `--orchestration-mode c4ar` is exposed
- `Role C` sandbox isolation is tested
- A/B output validation is tested

Recent implementation commits include:

- `5739255` `feat(mac): add C4AR handoff contracts`
- `a99ec50` `feat(mac): add C4AR role A driver`
- `6549fad` `feat(mac): add C4AR role B driver`
- `aa2a68a` `feat(mac): add C4AR thin orchestrator`
- `f77cf46` `fix(mac): harden C4AR role B handoff validation`
- `39edc59` `feat(mac): add playbook-driven C4AR role runners`
- `4f7aefb` `docs(skillx): add trend C4AR execution handoff`

### 4. The first real C4AR loop has now been completed on `trend`

Accepted task run:

- `trend-c4ar-001`

Accepted results:

- task-run `round-0 = 0.95`
- `R1 = 0.95`
- `R2 = 0.95`
- `R3 = 0.8944`

Interpretation:

- the real `Role C -> Role A -> Role B` loop now works end to end in the target runtime
- the loop found strong intermediate candidates, but did not produce monotonic gains
- the best observed reward plateaued at `0.95`
- the final freeze choice is `R1` over `R2` because the scores tie and `R1` is simpler

References:

- [`CHECKPOINT_2026-03-26_TREND_C4AR_RUN_SUMMARY.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/task_runs/trend-c4ar-001/CHECKPOINT_2026-03-26_TREND_C4AR_RUN_SUMMARY.md)
- [`RESULT_SUMMARY.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/RESULT_SUMMARY.md)

## What Is Still Not Verified

What still matters more than any extra local test is:

- whether the repaired `C4AR` loop generalizes beyond `trend`

So the major open question is no longer:

- do `Role A -> Role B -> Role C` work together at all?

It is now:

- where does the repaired loop transfer across the remaining frozen negative-transfer tasks?

## Current Scientific Position

At this exact checkpoint, the project has enough evidence to say:

1. negative-transfer repair remains a meaningful target
2. `trend` is still the best anchor task
3. the new `C2AR` starting point is real and nontrivial
4. the new `C4AR` loop is real and worth expanding

But it is still too early to claim:

- `C4AR` beats old handcrafted `C4`
- the repaired `C4AR` recipe improves every frozen task
- the repaired `C4AR` recipe generalizes to the broader frozen task set

Those claims remain pending stable reruns of the runtime-invalid post-`trend` tasks.

## Post-Trend Batch Outcome

### 1. `taxonomy-tree-merge-c4ar-001`

Observed results:

- `round-0 = 0.6327`
- `round-1 = 0.6327`
- `round-2 = 0.0` with `AgentSetupTimeoutError`
- `round-3 = 0.0` with `RuntimeError`

Interpretation:

- the run produced two runtime-valid rounds
- those valid rounds did not beat clean historical `C0 = 0.6481`
- later rounds are runtime-invalid and should not be used as scientific evidence

### 2. `exoplanet-detection-period-c4ar-001`

Observed results:

- `round-0 = 0.0`
- `round-1 = 0.0` with `AgentSetupTimeoutError`
- `round-2 = 0.0` with `RuntimeError`
- `round-3 = 0.0` with `RuntimeError`

Interpretation:

- `round-0` is runtime-valid but task-failed
- later rounds are runtime-invalid
- this run does not yet tell us whether the recipe transfers under stable runtime conditions

### 3. `energy-ac-optimal-power-flow-c4ar-001`

Observed results:

- `round-0 = 0.0` with `AgentTimeoutError`
- `round-1 = 0.0` with `RuntimeError`
- `round-2 = 0.0` with `RuntimeError`
- `round-3 = 0.0` with `RuntimeError`

Interpretation:

- this first pass is runtime-invalid across all four rounds
- it should be treated as an execution failure, not as evidence of task-level non-transfer

### 4. Cross-task conclusion after the first full batch

At this checkpoint:

- `trend` remains the only clean strong post-repair success case
- `taxonomy` produced partial usable evidence
- `exoplanet` and `energy` remain scientifically unresolved because runtime failures contaminated most or all rounds

This means the correct next question is no longer just:

- does the loop generalize?

It is now:

- can the remaining tasks be rerun under less timeout-prone execution settings so that we obtain interpretable evidence?

Reference:

- [`RUNTIME_ERROR_TABLE_2026-03-27.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/RUNTIME_ERROR_TABLE_2026-03-27.md)

## Next Session: Concrete Experiment Plan

The next session should not redesign the architecture.
It should perform targeted runtime recovery reruns.

### Stage 1. Preflight

Confirm:

- repo path
- SkillsBench path
- Docker
- `uv`
- Claude OAuth file
- `codex exec`
- Harbor-equivalent oauth-only Claude invocation still works

Do not switch runtimes unless forced by a real blocker.

### Stage 2. Execute timeout-expanded recovery reruns

Targets:

- `exoplanet-detection-period`
- `energy-ac-optimal-power-flow`
- optional targeted `taxonomy-tree-merge` rerun only if we need a clean later-round transfer test rather than relying on `round-0/round-1`

Execution adjustments:

- preserve all existing `*-c4ar-001` directories as historical evidence
- create new run ids for recovery reruns
- double the timeout budget relative to the first batch
- prefer lower concurrency or serial execution for the recovery pass
- keep `Role C` as real benchmark execution only

Reference handoff:

- [`C4AR_POST_TREND_BATCH_HANDOFF.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/agent_handoff/C4AR_POST_TREND_BATCH_HANDOFF.md)

### Stage 3. Validate the result scientifically, not just operationally

After the recovery reruns, the next session should answer:

1. was the run runtime-valid?
2. did the A/B/C handoffs work cleanly?
3. what is the final selected round?
4. how does `C4AR-best` compare to:
   - `C2AR = R0`
   - `C1`
5. does the trend-validated recipe transfer at all?

These are the headline scores:

- `Delta(C4AR-best, C2AR)`
- `Delta(C4AR-best, C1)`

Other scores should still be recorded in the matrix, but are secondary.

## Post-Experiment Decision Tree

The next session should not treat every outcome the same.

### Branch A. Runtime failure

If the real run fails because of:

- auth
- malformed A/B outputs
- handoff contract breakage
- Role C contamination
- Harbor/Docker runtime issues

then the correct next step is:

- fix the specific failing stage
- do **not** expand to more tasks yet
- rerun only the current task after the failure mode is isolated and repaired

### Branch B. Runtime-valid but no gain over `R0`

If the run completes cleanly, but:

- `C4AR-final <= R0`

then the correct next step is:

- inspect Role A evidence quality
- inspect Role B diagnosis quality
- inspect whether atomic operations are too weak, too generic, or too noisy
- revise playbooks and/or operation constraints
- decide whether the current task needs a targeted rerun before expanding

This would mean:

- the architecture works
- but the research brain is not yet good enough

### Branch C. Runtime-valid and useful lift over `R0`

If:

- `C4AR-final > R0`

and the gain looks scientifically interpretable, then the next step is:

1. write a short new checkpoint
2. freeze what helped
3. expand to the next task

Recommended expansion order:

1. `taxonomy-tree-merge`
2. `exoplanet-detection-period`
3. `energy-ac-optimal-power-flow`

Reason:

- `taxonomy` is still a strong negative-transfer anchor
- `exoplanet` is a clean zero case
- `energy` is useful but more runtime-sensitive

### Branch D. Runtime-valid but suspiciously large jump

If the run jumps upward too aggressively, the next session should explicitly verify:

- no prompt leakage
- no Role C exposure to refine artifacts
- no bundle contamination
- no accidental change to task prompt

This branch matters because the whole point of the current architecture is to keep:

- prompt fixed
- skill mutable

## What The Next Session Should Produce

At minimum, the next session should leave behind:

1. the real task run folder
2. updated:
   - `RUN_STATUS.md`
   - `EXECUTION_LOG.md`
   - `RESULT_SUMMARY.md`
3. a short checkpoint-style result note for the selected task run
4. one explicit recommendation:
   - expand
   - fix and rerun
   - or stop

## Artifact Pointers

Main run folder:

- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001`

Main execution handoff:

- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/agent_handoff/C4AR_POST_TREND_BATCH_HANDOFF.md`

Main experiment plan:

- `<INCUBATOR_REPO_ROOT>/docs/superpowers/plans/2026-03-25-mac-autoresearch-real-c4-experiment-plan.md`

Role playbooks:

- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/playbooks/C4AR_ROLE_A_SESSION_DISTILL_PLAYBOOK.md`
- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/playbooks/C4AR_ROLE_B_REFINE_BRAIN_PLAYBOOK.md`

Current `R0` summary:

- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/class-aware-c2-negative-transfer-poc-001/RESULT_SUMMARY.md`

## Bottom Line

This project is now past the pure-design phase.

The important remaining gap is now very specific:

- the remaining three real `C4AR` runs on the frozen negative-transfer tasks

If those runs work and give meaningful deltas, the project can move from:

- architecture-building

to:

- cross-task iterative experimental progress

If they fail, the failures will still be highly informative, because the current system is now instrumented enough to say exactly which role or handoff broke.
