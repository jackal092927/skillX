# Issue #16 Handoff: `earthquake-phase-association` Negative Lift

## Scope

- issue: [#16](https://github.com/jackal092927/skillX/issues/16)
- branch: `bug/issue-16-earthquake-negative-lift`
- worktree: `<repo-root>/.worktrees/bug/issue-16-earthquake-negative-lift`
- objective: explain why all 7 schema variants for
  `earthquake-phase-association` completed successfully but still ended at
  `0.0`, then implement a targeted fix

## What Is Already Known

- The original launcher-level bundle failure is no longer the blocker.
- The dedicated rerun `earthquake-20260411-rerun` executed all 7 schema pairs
  successfully.
- All 7 pairs still selected a final score of `0.0`.
- Official baselines are:
  - `C0 = 20.0`
  - `C1 = 20.0`
- So every schema currently shows `-20.0pp` vs `C0` and `-20.0pp` vs `C1`.

## Authoritative Evidence

- Cross-run summary:
  `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/round0-40x7-summary-2026-04-12.md`
- Rerun debug memo:
  `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/earthquake-20260411-rerun/debug_memo.md`
- Rerun result table:
  `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/earthquake-20260411-rerun/results_table.md`
- Rerun runtime status:
  `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/earthquake-20260411-rerun/runtime_status.md`
- Full structured export:
  `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/earthquake-20260411-rerun/run_report.json`
- Follow-up integration note:
  `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/run-3x7-2026-04-10/earthquake_followup_integration.md`

## Strong Working Hypothesis

- This is not an infrastructure incident.
- The current meta-schema framing and/or generated meta-skill content is a bad
  fit for this task family.
- There may also be task-local runtime fragility entangled with the poor score.
- The right diagnostic split is:
  - task/runtime fragility inside `earthquake-phase-association`
  - harmful schema/meta-skill guidance relative to the incumbent skillpack

## Suggested First Reads In Code

- `scripts/run_skillx_refine_benchmark.py`
- `src/skillx/c4ar/`
- `src/skillx/model_routing.py`
- `scripts/export_round0_run_report.py`

## Suggested Artifact Comparisons

1. Compare the incumbent task skillpack against the generated meta-skill for all
   7 schemas.
2. Inspect pair-level `refine_summary.json`, `round_decision.json`, and
   `orchestrator_log.ndjson` for each schema.
3. Check whether the meta-skill is over-constraining the solver, suppressing a
   working incumbent behavior, or pushing the agent into an irrelevant mode.
4. Separate runtime exceptions from actual quality degradation.

## Success Criteria For This Branch

- Produce a concrete diagnosis for the negative lift.
- If the fix is small and local, implement it.
- If a fix needs a rerun, leave the code ready and document the minimal rerun
  target.
- Update issue `#16` with a technically defensible root-cause summary.

## Constraints

- Do not treat the result as a launcher bug unless the artifacts support that.
- Do not broaden this branch into generic schema redesign.
- Prefer a task-local or task-family-local explanation over a vague global one.

## Session Bootstrap Prompt

```text
Work on GitHub issue #16 in this worktree only.

Goal: diagnose and fix the negative-lift result for earthquake-phase-association.

Known facts:
- The authoritative rerun is earthquake-20260411-rerun.
- All 7 schemas ran successfully but all final scores are 0.0.
- Official C0 and C1 are both 20.0, so every schema is -20pp.
- This is believed to be a substantive task/schema/meta-skill mismatch, not a Docker or launcher incident.

Start by reading:
- docs/plans/skillx/issue-16-earthquake-negative-lift-handoff-v0.1.md
- experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/earthquake-20260411-rerun/debug_memo.md
- experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/reports/earthquake-20260411-rerun/run_report.json

Then inspect the relevant generated meta-skills, incumbent skillpack, and round artifacts. Keep the investigation narrow and evidence-driven. If you make code changes, verify them locally before summarizing.
```
