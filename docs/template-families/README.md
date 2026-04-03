# SkillX Template Families v0.1

- **Project:** `projects/multi-agent-protocol-design`
- **Date:** 2026-03-25
- **Role:** first template-family skeleton set for the task-class-aware outer-loop direction
- **Status:** optional overlay, not baseline replacement

## Purpose

These template families are the first concrete bridge between:
- the current generic SkillX baseline (`C0/C1/C2/C3/C4`), and
- the longer-term MARC / MetaEvolver vision.

They are meant to serve as **class-aware priors**.
They do **not** replace the current SkillX minimal authoring format.
Instead, they answer a narrower question:

> If a task belongs to a known task class, what should a good initial skill structure look like before inner-loop refinement begins?

## Family set

1. `artifact-generator-template-v0.1.md`
2. `engineering-composition-bundle-template-v0.1.md`
3. `analytic-pipeline-bundle-template-v0.1.md`
4. `methodology-heavy-guardrail-template-v0.1.md`

## How to use these templates

Use them as **soft priors**, not hard schemas.
A class-aware C2/C3/C4 variant may use them to decide:
- which fields deserve more emphasis,
- how much scaffolding is appropriate,
- whether scripts should be bundled,
- what acceptance / verification layer is expected,
- what kinds of edits are especially valuable,
- and what kinds of content should often be deleted.

## Relation to the current project design

These templates should be read together with:
- `plans/skillx/skillx-task-class-taxonomy-and-metaevolver-design-v0.1.md`
- `drafts/skillx/skillx-minimal-authoring-format-v0.1.md`
- `drafts/skillx/skillx-design-principles-v0.1.md`
- `plans/skillx/skillx-refine-protocol-v0.1.md`

## Design stance

- Keep the baseline generic SkillX line intact.
- Add class-aware structure as an optional experimental overlay.
- Let the inner loop adapt the instantiated template to the actual model/runtime/task.
- Let the outer loop compare many such refinements and learn which structural priors transfer within a task class.
