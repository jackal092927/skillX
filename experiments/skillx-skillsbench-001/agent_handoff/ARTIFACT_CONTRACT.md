# Artifact Contract — SkillX Micro-Shakedown 001

Treat all paths below as **repo-root relative**.

Primary run folder:
- `experiments/skillx-skillsbench-001/runs/micro-shakedown-001-offer-letter/`

---

## 1. Mandatory files

### Top-level run files
- `README.md` — short directory-purpose note
- `RUN_BRIEF.md` — frozen task/condition scope
- `RUN_STATUS.md` — current state and verdict
- `ENVIRONMENT_NOTES.md` — remote-machine and benchmark setup facts
- `EXECUTION_LOG.md` — chronological execution log
- `BLOCKERS.md` — blockers if run cannot complete
- `RESULT_SUMMARY.md` — short synthesis after execution

### Results directory
- `results/condition_results.json`
- `results/condition_matrix.md`

### Raw outputs
- `logs/`
- `artifacts/`

---

## 2. Status lifecycle

`RUN_STATUS.md` should use one of these states:
- `planned`
- `running`
- `blocked`
- `completed`
- `partial`

Recommended semantics:
- `planned` — docs created, execution not started
- `running` — benchmark process started
- `blocked` — cannot proceed without human help or infra repair
- `partial` — some conditions executed, others not trustworthy/incomplete
- `completed` — all intended condition artifacts captured and summarized

---

## 3. condition_results.json minimum schema

The file should keep this basic shape:

```json
{
  "experiment_id": "skillx-skillsbench-001",
  "run_id": "micro-shakedown-001-offer-letter",
  "task_id": "offer-letter-generator",
  "status": "planned|running|blocked|partial|completed",
  "benchmark_agent": null,
  "model": null,
  "benchmark_repo_path": null,
  "conditions": {
    "C0": {},
    "C1": {},
    "C2": {},
    "C3": {}
  },
  "summary": {}
}
```

Per condition, capture at least:
- `condition_id`
- `label`
- `task_path`
- `skill_source`
- `command_summary`
- `timestamp_start`
- `timestamp_end`
- `exit_status`
- `verifier_result`
- `score_or_reward`
- `log_path`
- `notes`

---

## 4. condition_matrix.md minimum content

Include one row per condition with at least:
- condition
- skill source
- exit status
- verifier / score
- short note

This file should be readable by a human without opening JSON.

---

## 5. logs directory

Put raw command output here.
Suggested filenames:
- `C0.log`
- `C1.log`
- `C2.log`
- `C3.log`

If setup and run are separate, either combine or suffix them clearly.

---

## 6. artifacts directory

Use this for supporting run artifacts such as:
- copied command manifests
- exported benchmark job metadata
- condition-specific sandbox notes
- copied result snippets that are useful for audit

Do **not** rely on memory or chat history as the primary record.

---

## 7. Project-wide updates policy

Do not update project-wide navigation/tracking files until the run folder itself is complete.

If the run is successful, an optional follow-up may append a short note to:
- `TRACKING.md`
- `task_plan.md`

But these are secondary. The run folder is the primary artifact.
