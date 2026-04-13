# SkillX Round0 Rerun Recovery Handoff v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-13
- **Role:** handoff for the next `main` session
- **Status:** active execution handoff

---

## 1. Mission

Continue round0 execution on the repaired codebase and rerun the pairs that were
previously blocked by infrastructure or task-packaging exceptions.

The current default rerun scope is:

- `217` pairs whose latest failure was a Docker incident
- `7` pairs for `setup-fuzzing-py` that previously failed in
  `discover_task_inputs`

So the default next batch is:

- **`224` rerun pairs total**

This handoff intentionally excludes the one non-infra stalled pair
`energy-ac-optimal-power-flow__artifact-generation`. That pair is still worth
retrying later, but it is not part of the current default rerun batch.

---

## 2. What Is Already Fixed

### Docker incident handling

These fixes are already merged into local `main`:

- `e1f38f7` `Harden SkillX against Docker daemon failures`
- `37c8890` `Add Docker health fault injection for round0 validation`

Net effect:

- round0 launcher now performs Docker health gating
- unhealthy Docker can trigger automatic recovery
- sweeps stop early instead of generating long tails of invalid failures
- Docker infra failures are classified explicitly
- tmux launch scripts were updated to use the raised resource overrides and
  auto-recovery path

### Missing verifier-entry compatibility

This fix is also already merged into local `main`:

- `b10db10` `Relax verifier input assumptions for SkillX tasks`

Net effect:

- `run_skillx_refine_benchmark.py` no longer hard-requires
  `tests/test_outputs.py`
- `run_skillx_rewrite_benchmark.py` no longer hard-requires
  `tests/test_outputs.py`
- both runners now treat the entire `tests/` directory as the task verifier
  payload and copy it wholesale

This specifically unblocks:

- `setup-fuzzing-py`

And it also preemptively covers the same verifier-structure pattern for:

- `react-performance-debugging`

---

## 3. Source Of Truth

Use these generated artifacts as the authoritative coverage/rerun state:

- global CSV:
  `experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/global-round0-status/global_pair_status.csv`
- global JSON:
  `experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/global-round0-status/global_pair_status.json`
- global task x schema matrix:
  `experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/global-round0-status/global_status_matrix.md`
- builder script:
  `scripts/build_round0_global_status.py`

The global status currently says:

- detected tasks: `87`
- schemas: `7`
- total possible pairs: `609`
- attempted pairs: `280`
- completed pairs: `55`
- Docker-incident pairs: `217`
- other failed pairs: `8`
- unrun pairs: `329`

The rerun plan in this handoff is based on the current contents of that global
status report.

---

## 4. Current Default Rerun Scope

### A. Docker-incident reruns: `217` pairs

#### Full 7-schema rerun tasks

The following `30` tasks should be rerun across all `7` schemas:

- `3d-scan-calc`
- `adaptive-cruise-control`
- `data-to-d3`
- `exceltable-in-ppt`
- `find-topk-similiar-chemicals`
- `fix-build-agentops`
- `fix-druid-loophole-cve`
- `fix-erlang-ssh-cve`
- `gh-repo-analytics`
- `glm-lake-mendota`
- `lab-unit-harmonization`
- `latex-formula-extraction`
- `mars-clouds-clustering`
- `multilingual-video-dubbing`
- `offer-letter-generator`
- `organize-messy-files`
- `parallel-tfidf-search`
- `pddl-tpp-planning`
- `pg-essay-to-audiobook`
- `protein-expression-analysis`
- `reserves-at-risk-calc`
- `sec-financial-report`
- `shock-analysis-demand`
- `shock-analysis-supply`
- `simpo-code-reproduction`
- `taxonomy-tree-merge`
- `threejs-to-obj`
- `travel-planning`
- `trend-anomaly-causal-inference`
- `virtualhome-agent-planning`

#### Partial rerun tasks

These two tasks were only partially completed before Docker collapsed:

- `spring-boot-jakarta-migration`
  - rerun schemas:
    `environment-control`, `methodology-guardrail`,
    `orchestration-delegation`
- `syzkaller-ppdev-syzlang`
  - rerun schemas:
    `retrieval-heavy-synthesis`, `environment-control`,
    `methodology-guardrail`, `orchestration-delegation`

### B. Verifier-contract reruns: `7` pairs

Rerun all `7` schemas for:

- `setup-fuzzing-py`

Schemas:

- `artifact-generation`
- `analytic-pipeline`
- `engineering-composition`
- `retrieval-heavy-synthesis`
- `environment-control`
- `methodology-guardrail`
- `orchestration-delegation`

### C. Explicitly excluded from the default rerun batch

This pair still exists as a non-Docker, non-verifier failure, but is not part
of the current default rerun set:

- `energy-ac-optimal-power-flow__artifact-generation`
  - latest failure type: `ManualRoleAStallTermination`
  - latest run:
    `run-3x7-2026-04-10`

If you later decide to include it, the rerun total becomes:

- **`225` pairs**

---

## 5. Why These Pairs Need Rerun

### Docker incidents

These failures were produced after Docker became unhealthy mid-sweep. They are
not useful as task/schema judgments.

The two collapse runs were:

- `run-remaining-17x7-2026-04-11-v2`
- `run-next20x7-2026-04-11`

The characteristic symptom was:

- `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`

That symptom was later confirmed to be Docker daemon/API instability rather than
true task-level out-of-memory logic.

### setup-fuzzing-py

These `7` failures occurred before the inner loop really started.

Root cause:

- the task did not ship `tests/test_outputs.py`
- our runner previously assumed every task had that file
- the task instead provided an alternate verifier structure under `tests/`

That runner assumption is now fixed.

---

## 6. Suggested Execution Order

1. Regenerate the global status report if any new round0 reports have appeared:
   `uv run python scripts/build_round0_global_status.py`
2. Run a very small canary on the repaired paths before the full rerun:
   - one `setup-fuzzing-py` schema
   - one Docker-incident pair from a previously polluted task
3. If the canary passes, launch the full `224`-pair rerun batch.
4. After the rerun, regenerate the global status report again.
5. Re-check whether only the optional
   `energy-ac-optimal-power-flow__artifact-generation` stall pair remains.

Practical recommendation:

- verify `setup-fuzzing-py` first, because that checks the new verifier
  compatibility fix directly
- then run the Docker-polluted rerun set

---

## 7. Session Bootstrap Prompt

```text
Work on local main in projects/skillX.

Goal: continue round0 execution on the repaired codebase and rerun the pairs
that previously failed due to Docker incidents or the old verifier contract
assumption.

Read first:
- docs/plans/skillx/round0-rerun-recovery-handoff-v0.1.md
- experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/global-round0-status/global_status_matrix.md
- experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/global-round0-status/global_pair_status.json

Current default rerun target:
- 217 docker-incident pairs
- 7 setup-fuzzing-py pairs
- total = 224 pairs

Do not start from scratch. Reuse the current global status report and the
already-merged fixes:
- Docker hardening is already merged
- verifier compatibility for tasks without tests/test_outputs.py is already merged

First refresh the global status if needed, then run a small canary, then
prepare the rerun batch for the 224 target pairs.
```
