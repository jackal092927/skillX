# Rewrite Orchestrator Design v0.1

## Purpose

This document specifies the concrete orchestration shape for automatically generating `C2` and `C3` with Docker-hosted `Claude Code`, and then running benchmark trials with the generated artifacts.

This is an implementation design for the protocol in:

- [`REWRITE_AUTOMATION_PROTOCOL.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/REWRITE_AUTOMATION_PROTOCOL.md)

It is intentionally decision-complete enough that another engineer or agent can implement the orchestrator without needing to invent the main interfaces.

---

## 1. Implementation Form

The orchestrator should be implemented as one Python CLI script under:

- `mac_autoresearch_support/scripts/run_skillx_rewrite_benchmark.py`

Reasons:

- existing repo utilities already use Python CLI scripts in `mac_autoresearch_support/scripts/`
- the orchestration is mostly filesystem work, subprocess control, and JSON manifest emission
- the repo already has similar script patterns such as `check_benchmark_env.py` and `run_direct_claude_cli_instance.py`

---

## 2. Script Responsibilities

The script has five responsibilities:

1. preflight-check the local environment
2. assemble rewrite input bundles for selected task(s)
3. run the rewrite phase for `C2` and `C3`
4. validate generated rewrite outputs
5. materialize benchmark sandboxes and launch benchmark runs

The script is an orchestrator only. It is not the benchmark solver and not the rewrite model.

---

## 3. Command-Line Interface

The script should expose this CLI shape:

```text
./.venv-swebench/bin/python -m mac_autoresearch_support.scripts.run_skillx_rewrite_benchmark \
  --skillsbench-root /abs/path/to/skillsbench \
  --task trend-anomaly-causal-inference \
  --task exoplanet-detection-period \
  --task energy-ac-optimal-power-flow \
  --run-id rewrite-run-001 \
  --output-dir experiments/skillx-skillsbench-001/runs/rewrite-run-001 \
  --agent claude-code \
  --model anthropic/claude-sonnet-4-5 \
  --oauth-file <CLAUDE_CODE_OAUTH_TOKEN_FILE> \
  --conditions c0,c1,c2,c3 \
  --max-concurrency 2
```

Required arguments:

- `--skillsbench-root`
- `--task` (repeatable)
- `--run-id`
- `--output-dir`
- `--oauth-file`

Optional arguments with fixed defaults:

- `--agent` default `claude-code`
- `--model` default `anthropic/claude-sonnet-4-5`
- `--conditions` default `c0,c1,c2,c3`
- `--max-concurrency` default `1`
- `--skip-rewrite` default `false`
- `--skip-benchmark` default `false`
- `--reuse-existing-rewrites` default `false`

---

## 4. Input Discovery Rules

For each task, the script should discover:

- original skill directory from the SkillsBench task environment
- task `instruction.md`
- task `task.toml`
- task `tests/test.sh`
- task `tests/test_outputs.py`

The script should fail if any required input is missing.

Expected local protocol inputs:

- [`C2_REWRITE_PROTOCOL.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/C2_REWRITE_PROTOCOL.md)
- [`C3_REWRITE_PROTOCOL.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/C3_REWRITE_PROTOCOL.md)
- [`conditions.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/conditions.md)

---

## 5. Run Directory Layout

For one run, the script should create:

```text
runs/<run_id>/
  RUN_STATUS.md
  ENVIRONMENT_NOTES.md
  rewrite_jobs/
    <task_id>/
      inputs/
      prompts/
      logs/
      outputs/
        rewrite_registry/<task_id>/
        materialized_skillpacks/<task_id>/c2_minimal/
        materialized_skillpacks/<task_id>/c3_derived/
        rewrite_manifest.json
  benchmark_jobs/
  artifacts/
    task_sandboxes/
  results/
    rewrite_summary.json
    benchmark_summary.json
    matrix.md
```

The run directory should be self-contained enough to audit what inputs were used and what outputs were generated.

---

## 6. Rewrite Phase Execution

For each task, the script should run one rewrite job with a fresh Docker-hosted `Claude Code` context.

Within that rewrite job, the script should drive two internal substeps:

1. `C2` generation
2. `C3` derivation from the generated `C2`

The script should write two frozen prompt files into:

- `rewrite_jobs/<task_id>/prompts/c2_prompt.txt`
- `rewrite_jobs/<task_id>/prompts/c3_prompt.txt`

Those prompts should be rendered directly from the protocol documents, not manually improvised at runtime.

The rewrite job output should be captured into:

- `rewrite_jobs/<task_id>/logs/`
- `rewrite_jobs/<task_id>/outputs/`

---

## 7. Rewrite Output Validation

After each rewrite job completes, the script must validate:

- every expected `C2` skill file exists
- every expected `C3` skill file exists
- every `C3` skill file contains `# Derived Execution Layer`
- every multi-skill task has `skillx_derived__bundle__notes.yaml`
- `rewrite_manifest.json` exists
- manifest model and protocol versions match the requested run configuration

If any validation step fails, benchmark execution for that task must not start.

This is a hard failure, not a warning.

---

## 8. Benchmark Sandbox Materialization

For each task-condition pair, the script should materialize a dedicated benchmark sandbox under:

- `artifacts/task_sandboxes/<condition>-<task_id>/`

Skill injection rules:

- `c0`: no injected skills
- `c1`: inject original SkillsBench skills
- `c2`: inject generated `materialized_skillpacks/<task_id>/c2_minimal/`
- `c3`: inject generated `materialized_skillpacks/<task_id>/c3_derived/`

The benchmark sandbox should preserve the task's adjusted timeout and reasoning-effort policy if the run configuration asks for it.

---

## 9. Benchmark Phase Execution

The benchmark phase should launch one fresh job per condition-task pair.

Each benchmark job must:

- use `claude-code`
- use `anthropic/claude-sonnet-4-5`
- use the OAuth file configuration
- not inherit rewrite chat history
- only see the final task environment plus injected skill directory

The orchestrator should support bounded concurrency through a simple local queue.

Initial default:

- `max_concurrency = 1`

Recommended tested setting on the current machine:

- `max_concurrency = 2`

---

## 10. Results and Manifests

The script should emit:

- one per-task rewrite manifest
- one run-level rewrite summary
- one run-level benchmark summary
- one human-readable matrix markdown file

The benchmark summary should include, per condition-task pair:

- task id
- condition
- reward
- exception status
- benchmark job path
- skill source path

The rewrite summary should include, per task:

- task id
- number of original skills
- number of generated `C2` skills
- number of generated `C3` skills
- whether bundle artifact was generated
- manifest path

---

## 11. Environment Preconditions

Before any rewrite or benchmark launch, the script should verify:

- `docker info` succeeds
- Docker memory is at least `16 GiB`
- `claude-code` runner prerequisites are available
- OAuth file exists
- SkillsBench root exists
- all selected task directories exist

If Docker memory is below `16 GiB`, the script should fail with a clear message rather than running in a likely polluted configuration.

---

## 12. Failure Handling

The script should fail closed at these boundaries:

- missing task input files
- rewrite job non-zero exit code
- invalid or incomplete rewrite outputs
- benchmark sandbox materialization failure
- benchmark job submission failure

The script should not silently fall back to:

- manual rewrites
- API-token auth
- partial skill injection

Any such fallback would change the experiment.

---

## 13. Minimal Internal Architecture

The script should be organized into functions roughly like:

- `check_environment(...)`
- `discover_task_inputs(...)`
- `build_rewrite_prompt(...)`
- `run_rewrite_job(...)`
- `validate_rewrite_outputs(...)`
- `materialize_benchmark_sandbox(...)`
- `run_benchmark_job(...)`
- `collect_results(...)`
- `write_run_summaries(...)`

It does not need a larger framework abstraction in v0.1.

---

## 14. Initial Scope for First Implementation

The first implementation should support exactly these three tasks:

- `trend-anomaly-causal-inference`
- `exoplanet-detection-period`
- `energy-ac-optimal-power-flow`

It should support the full condition set:

- `c0`
- `c1`
- `c2`
- `c3`

It should target the current host environment and current local SkillsBench checkout, without attempting generalized remote execution yet.

---

## 15. Acceptance Criteria

The orchestrator is complete when it can do all of the following in one run:

1. discover all inputs for one or more selected tasks
2. generate protocol-controlled `C2` and `C3` with Docker-hosted `Claude Code`
3. validate the generated outputs structurally
4. inject those outputs into condition-specific benchmark sandboxes
5. run fresh benchmark jobs against those sandboxes
6. write run-level manifests and result summaries that make the full rewrite-to-benchmark chain auditable
