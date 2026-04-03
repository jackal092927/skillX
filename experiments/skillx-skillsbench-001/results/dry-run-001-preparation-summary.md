# Dry Run 001 Preparation Summary

- **Experiment:** `experiments/skillx-skillsbench-001`
- **Date:** 2026-03-22
- **Status:** preparation complete; benchmark execution not yet run

## What was completed

1. Created the experiment scaffold.
2. Froze dry-run task-selection criteria.
3. Selected the first 3 tasks:
   - `offer-letter-generator`
   - `parallel-tfidf-search`
   - `taxonomy-tree-merge`
4. Snapshotted the original SkillsBench skill files into `rewrite_registry/`.
5. Wrote SkillX minimal rewrites for the selected tasks.
6. Wrote agent-derived expansion notes for the selected tasks.

## Why these three tasks

- `offer-letter-generator`
  - single-skill, likely positive-skill case
- `parallel-tfidf-search`
  - multi-skill bundle case
- `taxonomy-tree-merge`
  - likely negative-transfer / over-guidance case

Together they give the first dry run a more informative spread than three uniformly easy positive-skill tasks.

## Main qualitative hypothesis

- `offer-letter-generator` should test whether SkillX can improve clarity with low burden.
- `parallel-tfidf-search` should test whether SkillX helps disentangle overlapping skill roles.
- `taxonomy-tree-merge` should test whether SkillX can reduce harm on an over-prescriptive skill.

## Not done yet

- no benchmark runs have been executed for C0/C1/C2/C3 on this dry run yet
- no authoring-time measurements have been recorded yet
- no independent audit lane has been run yet

## Immediate next step

Use the remote-agent entrypoint to run the first real benchmark execution on exactly one task first:
- entrypoint: `experiments/skillx-skillsbench-001/agent_handoff/AGENT_ENTRYPOINT.md`
- run: `experiments/skillx-skillsbench-001/runs/micro-shakedown-001-offer-letter/`
- scope: `offer-letter-generator`, `C0/C1/C2/C3`

Only after that micro-shakedown is clean should the experiment expand to the 3-task dry run.
