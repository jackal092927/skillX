# Task Selection Criteria — SkillX SkillsBench Experiment 001

## Purpose

Freeze the selection logic for the first SkillX dry run and the later 12-task pilot.

The first dry run should not simply pick the easiest tasks.
It should pick tasks that are likely to reveal whether SkillX matters.

---

## Criteria for the 3-task dry run

Each chosen task should satisfy at least one of the following:

1. **Positive-skill candidate**
- likely to benefit from explicit scope, prerequisites, or tool hints

2. **Negative-transfer candidate**
- likely to show over-guidance, mis-scoping, or benchmark harm

3. **Multi-skill / composition candidate**
- useful for testing whether SkillX can clarify interactions among multiple skills

4. **Task-domain diversity**
- prefer tasks from clearly different domains

5. **Verifier clarity**
- prefer tasks with clear deterministic success/failure signal

6. **Rewrite interpretability**
- avoid tasks where rewriting would require inventing a completely new strategy rather than restructuring existing guidance

---

## Current dry-run choice

### 1) `offer-letter-generator`
- Why chosen:
  - strong positive-skill candidate
  - single-skill task
  - clear document-generation scope
  - likely benefit from `scope_out`, `requires`, and `risks`
- What it tests:
  - whether SkillX helps convert a good but prose-heavy skill into a cleaner, more bounded one without losing usefulness

### 2) `parallel-tfidf-search`
- Why chosen:
  - multi-skill composition case
  - medium-difficulty engineering task
  - likely benefits from clarifying boundaries among speedup, memory, and load-balancing advice
- What it tests:
  - whether SkillX can make a skill bundle easier to use by making each skill’s role and scope more explicit

### 3) `taxonomy-tree-merge`
- Why chosen:
  - likely negative-transfer / over-guidance candidate
  - hard task with a very prescriptive methodology-heavy skill
  - useful for testing whether better scope/assumption declarations reduce harm
- What it tests:
  - whether SkillX can reduce misuse or overcommitment on tasks where the original skill may be too heavy or too brittle

---

## Criteria for expansion to the 12-task pilot

The later 12-task pilot should aim for:
- at least 4 domains
- at least 1 multi-skill bundle task
- at least 2 tasks with known or plausible negative-transfer risk
- at least 2 tasks where skills look strongly beneficial
- at least 2 tasks where skills appear weak/mixed
- mostly self-contained tasks with deterministic verifiers

---

## Exclusions for the first dry run

Avoid for now:
- tasks requiring additional external APIs or fragile auth
- tasks whose original skill is too tiny to meaningfully restructure
- tasks where rewriting would require heavy new domain research before even testing the format

---

## Decision rule

The dry run is successful if it gives clear evidence on at least one of these:
- SkillX minimal rewrite improves a positive-skill case
- SkillX clarifies a multi-skill composition case
- SkillX reduces harm or over-guidance on a difficult case

If none of those signals appear, the 12-task pilot should be reconsidered before scaling.
