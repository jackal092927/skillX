# Remote Execution Playbook — SkillX Micro-Shakedown 001

Treat all paths below as **repo-root relative**.

---

## 1. Mission

Execute the first real SkillX benchmark run on a remote machine for:
- task: `offer-letter-generator`
- conditions: `C0`, `C1`, `C2`, `C3`

This is a **micro-shakedown** whose purpose is to validate execution wiring before scaling out.

---

## 2. Preflight

Before running any benchmark condition, record the following in:
- `experiments/skillx-skillsbench-001/runs/micro-shakedown-001-offer-letter/ENVIRONMENT_NOTES.md`

Minimum preflight checks:
1. remote machine hostname / OS
2. local path of the checked-out `multi-agent-protocol-design` repo
3. local path of the SkillsBench repo
4. Docker availability
5. `uv` availability
6. benchmark agent + model selected for this run
7. task path for `offer-letter-generator`
8. whether required API keys are present

If any required item is missing and cannot be repaired quickly, stop and write a blocker.

---

## 3. Benchmark agent/model policy

Use **one fixed benchmark agent/model** across all four conditions.

Preferred rule:
- use the most stable benchmark agent/model combo already working on the remote machine
- keep it constant for `C0/C1/C2/C3`
- record exact agent + model string in `ENVIRONMENT_NOTES.md` and `results/condition_results.json`

Do not turn this run into a model-selection project.

---

## 4. Condition materialization policy

### C0 — No skill
Recommended implementation:
- remove or disable the task skill directory in an isolated task copy
- do not mutate the canonical benchmark checkout destructively

### C1 — Original skill
Use the benchmark task exactly as shipped.

### C2 — SkillX minimal rewrite
Replace the original task skill package with:
- `experiments/skillx-skillsbench-001/materialized_skillpacks/offer-letter-generator/c2_minimal/docx/`

### C3 — SkillX minimal rewrite + agent-derived expansion
Replace the original task skill package with:
- `experiments/skillx-skillsbench-001/materialized_skillpacks/offer-letter-generator/c3_derived/docx/`

---

## 5. Isolation recommendation

Do **not** mutate the benchmark repo in-place if avoidable.

Preferred pattern:
1. create an isolated working copy per condition, or a reversible per-condition task sandbox
2. keep condition-specific logs separate
3. ensure the only intended variable is the skill condition

Condition isolation is more important than speed in this first run.

---

## 6. Recommended execution sequence

1. preflight and environment notes
2. prepare isolated condition sandboxes
3. run `C0`
4. run `C1`
5. run `C2`
6. run `C3`
7. normalize and record results
8. write result summary

If a condition fails because of harness/environment issues rather than task logic, record that explicitly instead of treating it as a skill failure.

---

## 7. Logging policy

For each condition, save raw command output under:
- `experiments/skillx-skillsbench-001/runs/micro-shakedown-001-offer-letter/logs/`

Suggested naming:
- `C0.log`
- `C1.log`
- `C2.log`
- `C3.log`

If there are multiple subcommands, either:
- append them in chronological order to the same condition log, or
- add suffixed files like `C2.setup.log`, `C2.run.log`

---

## 8. Result capture policy

For each condition, record at least:
- condition id
- task id
- benchmark agent
- model
- benchmark repo path
- task path used
- timestamp
- command summary
- exit status
- deterministic verifier result / reward / score when available
- short interpretation note

Write the structured record to:
- `experiments/skillx-skillsbench-001/runs/micro-shakedown-001-offer-letter/results/condition_results.json`

Also write a human-readable matrix to:
- `experiments/skillx-skillsbench-001/runs/micro-shakedown-001-offer-letter/results/condition_matrix.md`

---

## 9. Success criteria

A successful micro-shakedown does **not** require that SkillX wins.
It requires that:
- all conditions are wired correctly
- outputs are captured consistently
- result interpretation is possible
- the next step (scale or debug) becomes obvious

A run where `C2/C3` lose but the wiring is clean is still a successful shakedown.

---

## 10. Failure / blocker policy

Write blockers immediately to:
- `experiments/skillx-skillsbench-001/runs/micro-shakedown-001-offer-letter/BLOCKERS.md`

Common blocker classes:
- benchmark repo missing
- Docker not healthy
- benchmark agent/model unavailable
- API keys missing
- task path mismatch
- condition injection ambiguity
- result file location unclear

Do not silently substitute a different experiment.

---

## 11. Final synthesis

At the end, write:
- `RUN_STATUS.md`
- `RESULT_SUMMARY.md`

The summary should answer:
1. Did `C0/C1/C2/C3` all run?
2. If not, what blocked them?
3. Was condition packaging clean?
4. Are result artifacts trustworthy enough to scale to the 3-task dry run?
5. What is the single best next action?
