# Class-aware C2 Notes — taxonomy-tree-merge

## What changed vs generic C2

1. Added explicit **decision gate** up front (fit checks before method commitment).
2. Added an **assumptions-to-surface** section so key priors are declared, not implicit.
3. Kept the core 5-step pipeline, but reframed detailed settings as **tunable** rather than mandatory.
4. Added explicit **branch/abstention discipline** for weak inputs, missing targets, runtime limits, and baseline mismatch.
5. Added compact **anti-patterns** focused on overcommitment and false precision.
6. Tightened **acceptance criteria** around boundary use, not just pipeline completion.

## Why this matches the task class

- Emphasizes boundary discipline (`scope_in`, `scope_out`, fit checks).
- Prioritizes assumption visibility and clarifying triggers.
- Reduces brittle prescriptiveness while preserving task intent (normalize → represent/weight → recursive cluster → name → export).
- Avoids C3-style heavy derived content, evaluator hacks, or benchmark-specific tricks.

## Soft-prior use of methodology-heavy-guardrail template

Applied as a compact prior:
- stronger exclusion logic,
- explicit abstain/branch behavior,
- deletion of unnecessary procedural bulk,
- no expansion into large methodological doctrine.