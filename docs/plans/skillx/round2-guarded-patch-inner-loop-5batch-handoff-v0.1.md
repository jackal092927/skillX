# SkillX Round2 Guarded-Patch Inner-Loop Handoff v0.1

- project: `skillX`
- workspace: `/Users/Jackal/iWorld/projects/skillX`
- branch at handoff: `main`
- latest committed outer-loop code/artifacts: `e08dd4b Add guarded patch outer-loop optimization`
- handoff purpose: start the next inner-loop round for the guarded-patch meta-schema candidate with five parallel threads

## Current State

We have a new guarded-patch candidate prompt bank, not an accepted final schema bank. It was built from the stable previous schema plus selected positive-transfer evidence from the regressed round.

Confirmed before this handoff:

- outer-loop update decision: `guarded_patch`
- positive-transfer pairs: `30`
- protected regression pairs: `12`
- schema patch verification: `passed`
- schema patches completed: `7/7`
- next candidate inner-loop plan: `20 tasks x 7 schemas = 140 pairs`

Primary artifacts:

- schema update package: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-schema-updates-round1-guarded-patch-2026-05-10/schema_update_package.json`
- update decision summary: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-schema-updates-round1-guarded-patch-2026-05-10/update-decision/summary.md`
- candidate prompt bank: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/round1_candidate_prompt_bank.json`
- materialized root: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10`
- 5-batch plan dir: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-round2-guarded-patch-2026-05-10-5batch`

Important local-file note: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/manifest.json`, `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/pair_specs.jsonl`, and `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/pairs/` are intentionally git-ignored runtime files. They exist on this machine now. If a future session starts from a fresh clone instead of this local workspace, regenerate the outer-loop materialization first.

## Goal For New Session

Run the guarded-patch inner-loop candidate on all `140` task-schema pairs using five parallel tmux sessions.

Execution shape:

- 5 batches
- 4 tasks per batch
- 7 schemas per task
- 28 pairs per batch
- each batch runs serially internally with `SKILLX_MAX_CONCURRENT_PAIRS=1`
- total parallelism is 5 launcher threads

## Batch Partition

| batch | run label suffix | tmux session | dashboard | pairs | tasks |
| --- | --- | --- | --- | ---: | --- |
| `batch-01` | `b01` | `skillx-round2-guarded-patch-b01` | `http://127.0.0.1:8782/` | `28` | `adaptive-cruise-control, earthquake-phase-association, energy-ac-optimal-power-flow, data-to-d3` |
| `batch-02` | `b02` | `skillx-round2-guarded-patch-b02` | `http://127.0.0.1:8783/` | `28` | `citation-check, energy-market-pricing, exceltable-in-ppt, fix-build-google-auto` |
| `batch-03` | `b03` | `skillx-round2-guarded-patch-b03` | `http://127.0.0.1:8784/` | `28` | `civ6-adjacency-optimizer, exoplanet-detection-period, fix-druid-loophole-cve, azure-bgp-oscillation-route-leak` |
| `batch-04` | `b04` | `skillx-round2-guarded-patch-b04` | `http://127.0.0.1:8785/` | `28` | `court-form-filling, earthquake-plate-calculation, financial-modeling-qa, 3d-scan-calc` |
| `batch-05` | `b05` | `skillx-round2-guarded-patch-b05` | `http://127.0.0.1:8786/` | `28` | `dapt-intrusion-detection, econ-detrending-correlation, find-topk-similiar-chemicals, fix-build-agentops` |

No task appears in more than one batch. The manifests are:

- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-round2-guarded-patch-2026-05-10-5batch/batch-01_pair_manifest.json`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-round2-guarded-patch-2026-05-10-5batch/batch-02_pair_manifest.json`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-round2-guarded-patch-2026-05-10-5batch/batch-03_pair_manifest.json`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-round2-guarded-patch-2026-05-10-5batch/batch-04_pair_manifest.json`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-round2-guarded-patch-2026-05-10-5batch/batch-05_pair_manifest.json`

## Preflight Checks

Run from `/Users/Jackal/iWorld/projects/skillX`:

```bash
git status --short --branch
test -f experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/manifest.json
test -f experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/pair_specs.jsonl
test -x experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-round2-guarded-patch-2026-05-10-5batch/launch_round2_guarded_patch_batches.sh
python3 - <<'PY'
import json
from pathlib import Path
root = Path('experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10')
plan = json.loads((root / 'next_round_pair_plan.json').read_text())['pairs']
print('pair_count=', len(plan))
print('task_count=', len({row['task_name'] for row in plan}))
print('schema_count=', len({row['schema_id'] for row in plan}))
PY
```

Expected output: `pair_count=140`, `task_count=20`, `schema_count=7`.

Check ports before launch if needed:

```bash
for p in 8782 8783 8784 8785 8786; do lsof -nP -iTCP:$p -sTCP:LISTEN || true; done
```

## Launch Command

```bash
bash experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-round2-guarded-patch-2026-05-10-5batch/launch_round2_guarded_patch_batches.sh
```

Defaults used by the launcher:

- run prefix: `run-round2-guarded-patch-2026-05-10`
- session prefix: `skillx-round2-guarded-patch`
- dashboard ports: `8782` to `8786`
- primary Claude OAuth file: `$HOME/.claude/claude-code-oauth-token`
- fallback Claude OAuth file: `$HOME/.claude-skillx-fallback/claude-code-oauth-token`
- model: `anthropic/claude-sonnet-4-5`
- Docker auto recover: enabled
- skip existing succeeded pairs: enabled

To override token files:

```bash
SKILLX_ROUND2_PRIMARY_CLAUDE_OAUTH_FILE="$HOME/.claude/claude-code-oauth-token" \
SKILLX_ROUND2_FALLBACK_CLAUDE_OAUTH_FILE="$HOME/.claude-skillx-fallback/claude-code-oauth-token" \
bash experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/reports/outer-loop-round2-guarded-patch-2026-05-10-5batch/launch_round2_guarded_patch_batches.sh
```

## Monitor

Dashboards:

- b01: `http://127.0.0.1:8782/`
- b02: `http://127.0.0.1:8783/`
- b03: `http://127.0.0.1:8784/`
- b04: `http://127.0.0.1:8785/`
- b05: `http://127.0.0.1:8786/`

Useful tmux commands:

```bash
tmux ls
tmux attach -t skillx-round2-guarded-patch-b01
tmux attach -t skillx-round2-guarded-patch-b02
tmux attach -t skillx-round2-guarded-patch-b03
tmux attach -t skillx-round2-guarded-patch-b04
tmux attach -t skillx-round2-guarded-patch-b05
```

Launcher logs are under:

```text
experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-task-list-first20-v0.1/outer-loop-round2-guarded-patch-candidate-rerun-2026-05-10/launcher_logs/run-round2-guarded-patch-2026-05-10-bXX/
```

## Failure/Resume Rules

- Do not restart from scratch if a machine reboot or Codex restart happens. Relaunch the same batch launcher; it passes `--skip-existing-succeeded`.
- Do not delete successful pair directories unless explicitly requested.
- If a batch reports a hard rate/quota limit, confirm fallback was attempted before marking the pair invalid.
- If Docker is unavailable during a round, that round is not valid signal; rerun the affected pair after Docker is healthy.
- Keep `SKILLX_MAX_CONCURRENT_PAIRS=1` inside each batch unless the user explicitly accepts higher Docker/memory pressure.
- Do not touch old first20 ports `8767-8769` or prior round1 ports `8772-8774` unless the user explicitly asks; this plan uses `8782-8786`.

## Completion Criteria

The round is ready for checkpointing when all five run reports show completed coverage for their 28 pairs. After completion, build a merged checkpoint/global status for the guarded-patch round and compare it against:

- stable baseline: `checkpoint-first20-round0-rate-limit-rerun-3batch-final-2026-04-29`
- regressed full-matrix round: `checkpoint-round1-first20-fullmatrix-effective-2026-05-04`

The key PM question is whether guarded patch recovers protected regressions while preserving positive-transfer improvements.
