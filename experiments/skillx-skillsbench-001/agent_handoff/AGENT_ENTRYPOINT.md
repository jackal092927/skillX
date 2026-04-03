# SkillX Remote Agent Entrypoint

**Audience:** a remote coding agent (for example Codex on another machine)
**Experiment:** `experiments/skillx-skillsbench-001`
**Immediate target:** `micro-shakedown-001-offer-letter`

Treat all paths below as **repo-root relative**.

---

## 1. Why this file exists

This file is the single entrypoint for a remote agent that will execute the first real SkillX benchmark run on another machine.

The local chat machine should **not** run this benchmark now because local disk space is constrained.
The experiment should instead be executed on a separate machine, with this repository pulled fresh from GitHub.

---

## 2. Big picture in plain language

This repository contains several related lines. For this execution task, only two matter:

1. **MARC / MAC AutoResearch**
   - broader platform goal: a community system for reusable agent-improvement artifacts, evaluation, transfer, and iteration

2. **SkillX**
   - a narrower focus inside that broader direction
   - current question: can a more structured, lightweight, verifiable skill format outperform current loose skill packaging?

This experiment is **not** trying to prove the entire SkillX vision.
It is only testing the first narrow claim:

> If we take an existing SkillsBench skill and rewrite it into a lightweight SkillX form, does benchmark usefulness improve?

---

## 3. Immediate assignment

Run the first real execution pass as a **micro-shakedown**:

- task: `offer-letter-generator`
- conditions: `C0`, `C1`, `C2`, `C3`
- objective: verify that benchmark execution, condition wiring, artifact capture, and result parsing all work cleanly before scaling out

Do **not** jump straight to the 3-task batch unless this micro-shakedown is clean.

---

## 4. Required reading order

Read these files in order before acting:

1. `experiments/skillx-skillsbench-001/agent_handoff/AGENT_ENTRYPOINT.md`
2. `experiments/skillx-skillsbench-001/runs/micro-shakedown-001-offer-letter/RUN_BRIEF.md`
3. `experiments/skillx-skillsbench-001/agent_handoff/REMOTE_EXECUTION_PLAYBOOK.md`
4. `experiments/skillx-skillsbench-001/agent_handoff/ARTIFACT_CONTRACT.md`
5. `experiments/skillx-skillsbench-001/conditions.md`
6. `plans/skillx/skillsbench-to-skillx-rewrite-experiment-plan-v0.1.md`

If execution details are unclear, then consult:

7. `playbooks/skillsbench-integration-playbook.md`
8. `experiments/skillx-skillsbench-001/README.md`
9. `experiments/skillx-skillsbench-001/results/dry-run-001-preparation-summary.md`

---

## 5. Frozen execution scope

### Task
- `offer-letter-generator`

### Conditions
- `C0` — no skill
- `C1` — original SkillsBench skill
- `C2` — SkillX minimal rewrite
- `C3` — SkillX minimal rewrite + agent-derived expansion

### Materialized skillpacks for direct use
- `experiments/skillx-skillsbench-001/materialized_skillpacks/offer-letter-generator/c2_minimal/docx/SKILL.md`
- `experiments/skillx-skillsbench-001/materialized_skillpacks/offer-letter-generator/c3_derived/docx/SKILL.md`

These are intentionally pre-materialized so you do **not** have to improvise condition packaging at runtime.

---

## 6. Execution stance

This is a **wiring/debug execution**, not a leaderboard claim.

Priority order:
1. get all four conditions to run cleanly on the same task
2. capture deterministic outputs and run metadata correctly
3. identify condition-injection ambiguities or benchmark harness problems
4. only then discuss broader performance interpretation

Use one fixed benchmark agent + model across all conditions.
Prefer a combination that is already known to work on the remote machine.
If there is a choice, prefer the most boring stable option over the fanciest model.

---

## 7. Non-goals

Do **not** do any of the following in this run unless explicitly needed to unblock execution:

- do not scale to the 3-task dry run
- do not run the 12-task pilot
- do not redesign SkillX documents
- do not widen the benchmark substrate
- do not spend long cycles debating model fairness if one stable agent/model combo already works
- do not write results into arbitrary project files outside the run folder until the run artifacts are complete

---

## 8. What to do if blocked

If the remote machine lacks a healthy SkillsBench environment, agent runtime, API key, or task path:

1. write the blocker immediately to:
   - `experiments/skillx-skillsbench-001/runs/micro-shakedown-001-offer-letter/BLOCKERS.md`
2. update:
   - `experiments/skillx-skillsbench-001/runs/micro-shakedown-001-offer-letter/RUN_STATUS.md`
3. stop instead of guessing

A high-quality blocker report is better than a fake partial run.

---

## 9. Definition of done for this micro-shakedown

This run counts as complete only if all of the following exist:

- a filled `RUN_STATUS.md`
- a filled `ENVIRONMENT_NOTES.md`
- per-condition raw logs under `logs/`
- per-condition result entries in `results/condition_results.json`
- a human-readable matrix in `results/condition_matrix.md`
- a short synthesis in `RESULT_SUMMARY.md`

If the run fails or stops early, the blocker path above is still required.

---

## 10. After completion

After the run artifacts are complete, you may optionally append a short summary to project-wide tracking docs.
But **artifact completeness comes first**.

The primary deliverable of this remote execution is the run folder itself.
