# Rewrite Automation Protocol v0.1

## Purpose

This document defines how `Claude Code` running inside Docker should automatically generate `C2 = SkillX Minimal` and `C3 = SkillX Derived` before benchmark execution.

The goal is to make rewrite generation:

- context-isolated
- model-unified
- protocol-driven
- auditable
- reusable across tasks

This protocol is the execution-layer companion to:

- [`C2_REWRITE_PROTOCOL.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/C2_REWRITE_PROTOCOL.md)
- [`C3_REWRITE_PROTOCOL.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/C3_REWRITE_PROTOCOL.md)

---

## 1. High-Level Shape

The system must run in two phases.

### Phase A: Rewrite Phase

A fresh `Claude Code + Sonnet 4.5` agent inside Docker receives the frozen rewrite inputs and produces:

- `C2` skill files
- `C3` skill files
- one `bundle` artifact for multi-skill tasks
- rewrite audit metadata

This phase does not execute the benchmark task itself.

### Phase B: Benchmark Phase

A second fresh `Claude Code + Sonnet 4.5` agent inside Docker runs the benchmark task using one of the conditions:

- `C0 = No Skill`
- `C1 = Original Skill`
- `C2 = SkillX Minimal`
- `C3 = SkillX Derived`

The benchmark agent must not inherit rewrite-phase conversation history.

---

## 2. Why Two Phases Are Required

This split is mandatory because it preserves experimental meaning.

If the same agent first rewrites the skill and then solves the benchmark in the same context, the experiment stops measuring "injected skill quality" and starts measuring "agent memory of how it wrote the skill."

The required isolation boundary is therefore:

- rewrite outputs may flow into benchmark execution
- rewrite chat history may not flow into benchmark execution

---

## 3. Fixed Runtime

Both phases must use:

- `agent = claude-code`
- `model = anthropic/claude-sonnet-4-5`
- `auth = CLAUDE_CODE_OAUTH_TOKEN_FILE` or equivalent OAuth file-based configuration

The rewrite phase must not switch to API-token execution unless explicitly approved outside this protocol.

---

## 4. Rewrite Inputs

For one task, the rewrite container receives only:

- the task's original `SKILL.md` files
- `instruction.md`
- `task.toml`
- `tests/test.sh`
- `tests/test_outputs.py`
- [`C2_REWRITE_PROTOCOL.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/C2_REWRITE_PROTOCOL.md)
- [`C3_REWRITE_PROTOCOL.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/C3_REWRITE_PROTOCOL.md)
- [`conditions.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/conditions.md)

It must not receive:

- prior benchmark scores
- prior rewrite outputs for other tasks
- manual task-specific hints outside the frozen protocol
- reference answers

---

## 5. Rewrite Outputs

For each task, the rewrite phase must materialize all outputs under a task-scoped output directory.

Required outputs:

- `rewrite_registry/<task_id>/`
- `materialized_skillpacks/<task_id>/c2_minimal/.../SKILL.md`
- `materialized_skillpacks/<task_id>/c3_derived/.../SKILL.md`
- `rewrite_manifest.json`

For multi-skill tasks, required additional output:

- `rewrite_registry/<task_id>/skillx_derived__bundle__notes.yaml`

The manifest must record at least:

- `task_id`
- `writer_agent`
- `writer_model`
- `c2_protocol_version`
- `c3_protocol_version`
- `input_files`
- `output_files`
- `prompt_hashes`
- `timestamp`

---

## 6. Rewrite Agent Responsibilities

The rewrite agent has exactly four responsibilities:

1. Snapshot original skills into the task's `rewrite_registry`
2. Generate `C2` according to the `C2 Rewrite Protocol`
3. Generate `C3` according to the `C3 Rewrite Protocol`
4. Materialize the benchmark-injectable skillpack layout

The rewrite agent must not:

- run the task solver
- inspect prior benchmark rewards
- tune itself against observed task performance

---

## 7. Benchmark Agent Responsibilities

The benchmark agent has exactly one responsibility:

- solve the benchmark task under a supplied condition using the prepared environment

The benchmark agent may receive:

- no skill directory for `C0`
- original skill directory for `C1`
- generated `c2_minimal` skill directory for `C2`
- generated `c3_derived` skill directory for `C3`

The benchmark agent must not receive:

- rewrite manifests as instructions
- rewrite chat transcripts
- protocol authoring discussion

It may only see the final injected skills and the normal task environment.

---

## 8. Orchestration Contract

The orchestrator must treat rewrite and benchmark as separate jobs.

Recommended execution order for one task:

1. prepare task input bundle
2. launch rewrite job in Docker
3. validate expected rewrite outputs exist
4. copy generated outputs into condition-specific benchmark sandboxes
5. launch fresh benchmark job(s)
6. collect reward, logs, and rewrite metadata together under the run folder

The orchestrator must fail closed if rewrite outputs are incomplete.

Examples:

- missing one `C2` skill file -> stop
- missing one `C3` skill file -> stop
- missing bundle artifact for a multi-skill task -> stop
- missing manifest -> stop

---

## 9. Recommended Filesystem Layout

For one run:

```text
runs/<run_id>/
  rewrite_jobs/
    <task_id>/
      inputs/
      outputs/
      logs/
  benchmark_jobs/
    <condition>-<task_id>/
      ...
  manifests/
    rewrite_manifests/
      <task_id>.json
```

Inside rewrite outputs:

```text
outputs/
  rewrite_registry/<task_id>/
  materialized_skillpacks/<task_id>/c2_minimal/
  materialized_skillpacks/<task_id>/c3_derived/
  rewrite_manifest.json
```

---

## 10. Prompt Injection Strategy

The rewrite phase should not rely on ad hoc human chat.

Instead, the orchestrator should provide:

- one frozen `C2` system/user prompt payload
- one frozen `C3` system/user prompt payload
- explicit file paths for the allowed inputs

The rewrite agent should be invoked in two internal steps:

1. generate `C2`
2. derive `C3` from the generated `C2`

The prompt text should come directly from the frozen protocol documents, not from handwritten run-time edits.

---

## 11. Validation Rules

Before benchmark execution, the orchestrator should run lightweight validation:

- every expected `C2` file exists
- every expected `C3` file exists
- every `C3` file contains `# Derived Execution Layer`
- every multi-skill task has a bundle artifact
- manifest versions match the frozen protocols

This validation is structural only. It is not yet a quality judgment.

---

## 12. Minimal Implementation Shape

The simplest correct implementation is:

- one local orchestration script
- one rewrite Docker job per task
- one benchmark Docker job per condition-task pair

The script should:

- assemble the rewrite input bundle
- invoke `claude-code` with the frozen protocol prompt
- capture outputs into the task-scoped rewrite directory
- validate output structure
- populate benchmark sandboxes from generated skillpacks
- launch normal benchmark runs afterward

This should be implemented as orchestration around the existing Harbor/benchmark workflow, not as a special benchmark task that rewrites and solves in one session.

---

## 13. Experimental Meaning

Under this protocol:

- `C2` measures the value of protocol-controlled minimal rewrite
- `C3` measures the value of protocol-controlled derived execution layer

Because rewrite and benchmark are separated by a fresh-context boundary, any observed effect is attributable to the generated skill artifacts rather than to rewrite-session memory.
