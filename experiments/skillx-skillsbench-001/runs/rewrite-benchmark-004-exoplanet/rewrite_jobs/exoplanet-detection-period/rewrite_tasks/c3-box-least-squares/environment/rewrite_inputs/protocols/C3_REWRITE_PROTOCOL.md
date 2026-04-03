# C3 Rewrite Protocol v0.1

## Purpose

This protocol defines how to derive `C3 = SkillX Derived` from `C2 = SkillX Minimal`.

The purpose of `C3` is to add a constrained execution layer on top of a valid `C2` skill without changing the task's underlying intent or silently introducing new unsupported strategy.

`C3` is intended to add:

- explicit execution constraints
- explicit deliverable-completion checks
- explicit self-check guidance for common failure paths
- explicit task-level coordination for multi-skill tasks

`C3` is not intended to:

- replace `C2`
- invent new benchmark-specific tactics
- leak answers from tests
- add unsupported domain knowledge that is not grounded in the allowed inputs

---

## 1. Relationship to C2

`C3` is a derived layer, not a fresh rewrite from scratch.

That means:

- every `C3` skill must start from one valid `C2` skill
- `C3` preserves the full `C2` content
- `C3` adds a `Derived Execution Layer`
- `C3` does not change the base purpose, scope, or core technical guidance of `C2`

For multi-skill tasks, `C3` also adds one task-level bundle artifact that captures cross-skill execution structure.

---

## 2. Fixed Writer Model

All `C3` derivations must use the same fixed writer model:

- `Claude Code + Sonnet 4.5`

Within a single experiment run, no other derivation model may be mixed in.

---

## 3. Fresh Derivation Context

Each task derivation must run in a fresh context.

Requirements:

- one task = one derivation session
- no inherited derivation history from other tasks
- no inherited benchmark execution history
- no access to benchmark scores for the same task

If the task has multiple skills, the derivation session may see all `C2` skills for that task, but may not see derived outputs for other tasks.

---

## 4. Allowed Input Bundle

The derivation agent may only see the following inputs for a given task:

- all valid `C2` skill files for the task
- original `SKILL.md`
- `instruction.md`
- `task.toml`
- `tests/test.sh`
- `tests/test_outputs.py`
- experiment-wide [`conditions.md`](<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/conditions.md)

The derivation agent must not be given:

- prior benchmark scores for the same task
- task-specific manual derivation hints
- reference answers
- other tasks' derived outputs
- extra human hints outside the protocol

---

## 5. Derivation Principles

The derivation must:

- preserve the full `C2` skill content
- add only execution-contract information supported by the allowed inputs
- make preconditions, postconditions, failure modes, and evaluator-facing risk points explicit
- improve task completion reliability without turning into a benchmark-specific checklist
- remain concise and task-centered

The derivation must not:

- change the task's intended solution class
- add unsupported new core algorithmic strategy
- reverse-engineer the final answer from tests
- encode test assertions as a literal pass-the-test recipe

---

## 6. What C3 Adds Beyond C2

Compared with `C2`, `C3` adds the following new material:

- `Derived Execution Layer`
- `Preconditions`
- `Postconditions`
- `Failure Modes`
- `Evaluator Hooks`

For multi-skill tasks, `C3` also adds:

- one task-level `bundle` artifact describing stage order, handoff boundaries, and task-level completion checks

These are the core differences between `V2` and `V3` in this experiment:

- `V2` clarifies what the skill is and when to use it
- `V3` adds how to execute it safely and how to know it is actually complete

---

## 7. C3 Skill Output Contract

Each derived `C3` skill must be a complete `SKILL.md` file.

It must preserve the full `C2` frontmatter and body, and then append exactly one additional section:

- `# Derived Execution Layer`

Within that section, the following subsections must appear in exactly this order:

1. `## Preconditions`
2. `## Postconditions`
3. `## Failure Modes`
4. `## Evaluator Hooks`

The derived section must be additive. It must not rewrite the earlier `C2` sections into a different shape.

---

## 8. Bundle Output Contract for Multi-Skill Tasks

For tasks with multiple skills, `C3` must also produce one task-level bundle artifact.

Recommended filename:

- `skillx_derived__bundle__notes.yaml`

The bundle artifact must summarize:

- stage ordering across skills
- handoff boundaries between skills
- cross-skill dependencies
- task-level failure modes
- task-level deliverables that must exist by the end
- task-level evaluator-sensitive checks

The bundle artifact must not replace per-skill `C3` files. It exists in addition to them.

---

## 9. Meaning of Each New Section

### Preconditions

State what must already be true before this skill is used.

Examples:

- required input files exist
- required columns or schema are present
- upstream stage has completed
- key assumptions about units, data shape, or environment are satisfied

### Postconditions

State what should be true after the skill is executed correctly.

Examples:

- required output file exists
- output is parseable in the expected format
- expected artifact fields are present
- the result is ready for the next stage

### Failure Modes

State the most common realistic ways the agent can fail even if it chose the right skill.

Examples:

- stage order mistakes
- unit conversion mistakes
- missing output file
- over-aggressive preprocessing
- wrong identifier mapping
- partial completion presented as final completion

### Evaluator Hooks

State the main output-contract surfaces that are likely to matter to the benchmark evaluator.

These are not test-derived answer hints. They are limited to:

- file existence
- parseability
- schema shape
- numeric format or precision constraints
- obvious task-level deliverable checks

---

## 10. Use of Tests

`tests/test_outputs.py` and `tests/test.sh` are allowed as inputs.

They may be used only to understand:

- what final artifacts are required
- which artifact shapes are evaluator-visible
- which classes of structural mistakes are likely to fail validation

They must not be used to:

- infer the final numeric or semantic answer
- convert the skill into a literal test-checklist
- add benchmark-specific hacks

---

## 11. Standard Derivation Prompt

All tasks must use the same derivation prompt:

```text
You are deriving one benchmark skill from C2 into C3: SkillX Derived.

Your job is to preserve the provided C2 skill and add a constrained derived execution layer that makes execution requirements, completion checks, common failure modes, and evaluator-visible output risks explicit.

You must follow these rules:

1. Preserve the full C2 skill content and its core technical guidance.
2. Do not introduce benchmark-specific hacks or infer the final answer from the tests.
3. Add only execution-contract information that is supported by the allowed inputs.
4. Do not change the task's intended solution class.
5. Use the tests only to understand output-contract surfaces, not to reverse-engineer the answer.
6. Append exactly one section named `# Derived Execution Layer`.
7. Inside that section, include exactly these subsections in this order:
   - `## Preconditions`
   - `## Postconditions`
   - `## Failure Modes`
   - `## Evaluator Hooks`
8. Keep the derived layer concise, task-centered, and additive.

Use only the provided inputs:
- C2 skill file(s)
- original SKILL.md
- instruction.md
- task.toml
- tests/test.sh
- tests/test_outputs.py
- experiment conditions.md

For multi-skill tasks, also produce one task-level bundle summary describing stage order, cross-skill dependencies, task-level failure modes, task-level deliverables, and evaluator-sensitive checks.

Write the final answer as:
- the full contents of the derived SKILL.md for each skill
- plus the bundle artifact when the task has multiple skills
```

---

## 12. Audit Metadata

Each `C3` derivation should record at least:

- `task_id`
- `writer_model`
- `protocol_version`
- `prompt_text` or `prompt_hash`
- `input_files`
- `source_c2_files`
- `output_files`
- `timestamp`

Recommended additional metadata:

- original skill paths
- bundle artifact path
- session id or run id

---

## 13. Expected Character of a Valid C3 Output

A valid `C3` output should be:

- clearly traceable back to `C2`
- more execution-safe than `C2`
- explicit about completion conditions
- explicit about common failure paths
- explicit about evaluator-visible structural risks

An invalid `C3` output usually looks like:

- a rewritten `C2` rather than a derived layer
- an evaluator checklist disguised as guidance
- a hidden answer leak
- a large expansion of domain content rather than an execution-contract layer

---

## 14. Experimental Meaning

In this experiment, `C3` represents:

- the effect of adding a constrained execution-contract layer on top of a fixed `C2` rewrite

So `C3 vs C2` should be interpreted as:

- whether explicit execution constraints, completion checks, failure modes, and evaluator-visible output guidance improve task execution beyond minimal structural rewrite alone
