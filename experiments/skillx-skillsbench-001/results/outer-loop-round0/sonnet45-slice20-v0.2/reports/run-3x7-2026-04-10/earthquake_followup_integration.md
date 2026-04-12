# Earthquake Follow-Up Integration

## Summary

- Original location: `run-3x7-2026-04-10`
- Follow-up rerun: `../earthquake-20260411-rerun/`
- Original failure mode: immediate bundle-construction failure on
  `environment/skills/licenses/SKILL.md`
- Follow-up status: all 7 schema pairs executed successfully
- Follow-up outcome: all 7 schema pairs ended at `0.0`, which is `-20.0pp`
  relative to both official `C0` and official `C1`

## How To Read The First Batch Now

- Keep the original `3x7` report as the historical record of the first run.
- Do not use the original `earthquake-phase-association` rows as the final task
  outcome.
- For any downstream analysis of the first twenty tasks, replace those 7 rows
  with the rerun results from `earthquake-20260411-rerun`.

## Implication

- The first `3x7` batch is no longer blocked by a missing-skill discovery bug on
  `earthquake-phase-association`.
- The new problem is substantive: the current SkillX schema / meta-skill path
  still performs strictly worse than the incumbent for this task family.
