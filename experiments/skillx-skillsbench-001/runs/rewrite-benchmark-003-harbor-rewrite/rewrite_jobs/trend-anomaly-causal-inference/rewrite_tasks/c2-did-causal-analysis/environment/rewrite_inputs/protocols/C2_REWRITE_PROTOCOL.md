# C2 Rewrite Protocol v0.2

## Purpose

This protocol defines how to rewrite one original SkillsBench skill into `C2 = SkillX Minimal`.

The purpose of `C2` is to:

- preserve original task intent
- preserve the core technical content of the original skill
- restructure the skill into a lightweight SkillX format
- improve clarity, boundary legibility, and task alignment

`C2` is not intended to:

- introduce task-specific prompt tuning
- introduce benchmark-specific hacks
- infer answers from tests
- act like `C3` with a strong execution-contract layer

---

## 1. Fixed Writer Model

All `C2` rewrites must use the same fixed writer model:

- `Claude Code + Sonnet 4.5`

Within a single experiment run, no other rewrite model may be mixed in.

---

## 2. Fresh Rewrite Context

Each task rewrite must run in a fresh context.

Requirements:

- one task = one rewrite session
- no inherited rewrite history from other tasks
- no inherited benchmark execution history
- no access to previously rewritten outputs for other tasks

---

## 3. Allowed Input Bundle

The rewrite agent may only see the following inputs for a given task:

- original `SKILL.md`
- `instruction.md`
- `task.toml`
- `tests/test.sh`
- `tests/test_outputs.py`
- experiment-wide [`conditions.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/conditions.md)

The rewrite agent must not be given:

- prior benchmark scores for the same task
- task-specific rewrite notes
- other tasks' rewrites
- reference answers
- extra human task-specific hints outside the protocol

---

## 4. Rewrite Principles

The rewrite must:

- preserve original task intent
- preserve the main technical guidance already present in the inputs
- prefer restructuring, compressing, and clarifying over expanding
- move from generic tutorial style toward task-centered guidance
- make scope boundaries explicit
- make dependencies, preferred tools, and risks explicit

The rewrite must not:

- add unsupported new core strategy
- introduce benchmark-specific hacks
- reverse-engineer the final answer from tests
- silently turn `C2` into `C3`

---

## 5. C2 Output Contract

The output must be a complete `SKILL.md` file.

The YAML frontmatter must contain the following fields in exactly this order:

1. `skillx.name`
2. `skillx.purpose`
3. `skillx.scope_in`
4. `skillx.scope_out`
5. `skillx.requires`
6. `skillx.preferred_tools`
7. `skillx.risks`
8. `skillx.examples`

The body must contain exactly these sections in this order:

1. `# Guidance`
2. `# Notes for Agent`

---

## 6. What C2 May Include

`C2` may include:

- task-centered purpose
- explicit `scope_in`
- explicit `scope_out`
- execution dependencies in `requires`
- recommended tools in `preferred_tools`
- lightweight risk reminders in `risks`
- task-oriented examples
- concise guidance for the agent

---

## 7. What C2 Must Not Include

`C2` must not include:

- `Derived Execution Layer`
- `Candidate Preconditions`
- `Candidate Postconditions`
- `Candidate Failure Modes`
- `Candidate Evaluator Hooks`
- any standalone failure-mode section
- evaluator-facing instructions
- benchmark score references
- answer leakage

Important boundary:

- `C2` may include lightweight `risks`
- `C2` may not include explicit failure-mode taxonomy

Those belong to `C3`.

---

## 8. Use of Tests

`tests/test_outputs.py` and `tests/test.sh` are allowed as inputs.

They may be used only to understand:

- the task's output contract
- the shape of the required deliverables
- what kinds of outputs the benchmark actually validates

They must not be used to:

- infer the final answer
- translate the skill into an evaluator checklist
- encode benchmark-specific hacks

---

## 9. Standard Rewrite Prompt

All tasks must use the same prompt:

```text
You are rewriting one benchmark skill into C2: SkillX Minimal Rewrite.

Your job is to transform the provided original skill into a clearer, lighter, more task-centered SkillX skill while preserving original task intent.

You must follow these rules:

1. Preserve the original task intent and the core technical guidance already present in the inputs.
2. Do not introduce benchmark-specific hacks or infer the answer from the tests.
3. Do not add a derived execution layer, evaluator hooks, explicit preconditions/postconditions, or explicit failure-mode sections. Those belong to C3, not C2.
4. Prefer restructuring, compressing, and clarifying over expanding.
5. Move from generic tutorial style toward task-centered guidance.
6. Make scope boundaries explicit: what this skill is for, and what it is not for.
7. Make dependencies, preferred tools, and main risks explicit.
8. Use the tests only to understand the task’s output contract, not to reverse-engineer the answer.
9. The output must be a single SkillX-style SKILL.md and must follow the required field order exactly.

Use only the provided inputs:
- original SKILL.md
- instruction.md
- task.toml
- tests/test.sh
- tests/test_outputs.py
- experiment conditions.md

Required output format:

YAML frontmatter with exactly this field order:
- skillx.name
- skillx.purpose
- skillx.scope_in
- skillx.scope_out
- skillx.requires
- skillx.preferred_tools
- skillx.risks
- skillx.examples

Then exactly these sections in this order:
- # Guidance
- # Notes for Agent

Write the final answer as the full contents of the rewritten SKILL.md only.
```

---

## 10. Audit Metadata

Each `C2` rewrite should record at least:

- `task_id`
- `writer_model`
- `protocol_version`
- `prompt_text` or `prompt_hash`
- `input_files`
- `output_file`
- `timestamp`

Recommended additional metadata:

- original skill path
- rewritten skill path
- session id or run id

---

## 11. Expected Character of a Valid C2 Output

A valid `C2` output should be:

- more task-centered than the original skill
- easier to scan
- clearer about scope boundaries
- clearer about dependencies and risks
- still recognizably grounded in the original skill content

An invalid `C2` output typically:

- remains a loose tutorial
- leaks into `C3`
- overfits to the tests
- invents unsupported strategy

---

## 12. Experimental Meaning

Within the experiment, `C2` represents:

- a uniform, lightweight, protocol-controlled SkillX rewrite

So `C2 vs C1` should be interpreted as:

- whether a standardized SkillX minimal rewrite helps relative to the original skill format
- without adding a stronger derived execution layer

