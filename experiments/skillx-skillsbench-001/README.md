# SkillX SkillsBench Experiment 001

- **Project:** `skillX`
- **Date initialized:** 2026-03-22
- **Role:** first execution-facing experiment scaffold for testing SkillX on SkillsBench
- **Parent plan:** `docs/experiment-plans/skillsbench-to-skillx-rewrite-experiment-plan-v0.1.md`

Canonical onboarding for collaborators now lives at the repo root:

- `README.md`
- `INDEX.md`
- `docs/INDEX.md`

---

## Goal

Test whether **lightweight SkillX rewriting** improves skill usefulness relative to the original SkillsBench skill format.

This experiment is intentionally narrow.
It does **not** test the entire SkillX vision at once.
It first asks:

> Does adding lightweight declarative structure + optional agent-derived expansion materially help existing benchmark skills?

---

## Current stage

Current stage = **ready for the first real remote micro-shakedown**.

What is frozen so far:
- experiment scaffold created
- task-selection criteria frozen
- first 3 dry-run tasks selected
- original benchmark skills snapshotted into `rewrite_registry/`
- first-batch SkillX minimal rewrites completed
- first-batch agent-derived expansion notes completed
- `offer-letter-generator` C2/C3 condition packs materialized for direct benchmark injection
- remote-agent handoff docs written under `agent_handoff/`
- canonical run folder created for `micro-shakedown-001-offer-letter`

What remains next:
1. run the remote micro-shakedown on `offer-letter-generator`
2. verify `C0/C1/C2/C3` condition wiring and result capture
3. inspect benchmark execution friction and artifact quality
4. decide whether to scale to the 3-task dry run

---

## Conditions

- `C0` — no skill
- `C1` — original SkillsBench skill(s)
- `C2` — SkillX minimal rewrite
- `C3` — SkillX minimal rewrite + agent-derived expansion
- optional later `C4` — bounded **multi-round** refine on a tune/eval split under a frozen protocol

See `conditions.md` for details.

---

## Current dry-run tasks

1. `offer-letter-generator`
2. `parallel-tfidf-search`
3. `taxonomy-tree-merge`

These were selected to intentionally cover:
- a strong positive-skill task
- a multi-skill bundle task
- a likely negative-transfer / over-guidance task

See `task_selection.yaml` and `task_selection_criteria.md` for rationale.

---

## Directory layout

```text
experiments/skillx-skillsbench-001/
  README.md
  conditions.md
  task_selection_criteria.md
  task_selection.yaml
  agent_handoff/
    AGENT_ENTRYPOINT.md
    REMOTE_EXECUTION_PLAYBOOK.md
    ARTIFACT_CONTRACT.md
  rewrite_registry/
    offer-letter-generator/
    parallel-tfidf-search/
    taxonomy-tree-merge/
  materialized_skillpacks/
    offer-letter-generator/
  runs/
    micro-shakedown-001-offer-letter/
    pilot-a/
    pilot-b/
  results/
  audits/
```

---

## Design stance

This experiment follows the SkillX design principles already frozen in project docs:
- adoption first
- first-class does not mean heavyweight
- human provides intent; agent derives structure
- evaluation should be anti-cheat by design
- negative transfer matters as much as average lift

## Related planning docs

- `anthropic-baseline-vs-skillx-experiment-matrix-v0.1.md`
- `../../docs/plans/skillx/INDEX.md`

---

## Immediate next action

Use `agent_handoff/AGENT_ENTRYPOINT.md` to execute `micro-shakedown-001-offer-letter` on a remote machine, then decide whether the execution path is clean enough to scale to the 3-task dry run.
