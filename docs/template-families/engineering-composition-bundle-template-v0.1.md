# Engineering Composition Bundle Template v0.1

- **Task class:** `engineering-composition-bundle`
- **Examples:** `parallel-tfidf-search`
- **Primary pattern:** `pipeline`
- **Typical topology:** `multi-skill-flat-bundle`

## 1. When to use this template

Use this template when the task depends on multiple engineering skills that each influence the outcome, but no single skill should dominate unconditionally.

Typical cases involve tradeoffs such as:
- correctness vs speed,
- memory vs throughput,
- local optimization vs system-level behavior.

## 2. Core design goal

The main goal is **coordination clarity across overlapping skills**.

A good skill bundle in this family should help the agent:
- understand the role of each sub-skill,
- know which objective is primary,
- resolve conflicts among recommendations,
- and avoid applying every skill equally at every step.

## 3. Default scaffold stance

- **Scaffold budget:** medium
- Enough structure is needed to clarify roles and precedence.
- Too much duplicated bundle prose will create noise.

## 4. Recommended field emphasis

At the bundle level, emphasize:
- primary task objective
- role of each sub-skill
- precedence / conflict-resolution policy
- correctness-before-optimization rule
- explicit interaction note

At the per-skill level, emphasize:
- narrow `purpose`
- tight `scope_in`
- explicit `scope_out`
- role-specific `risks`

## 5. Recommended extra resources

Useful bundled resources include:
- bundle manifest
- interaction matrix
- conflict-resolution note
- small benchmark or profiling notes
- reference snippets for dominant tools/frameworks

## 6. Script policy

- **Default:** recommended
- Good scripts include:
  - correctness-equivalence checks
  - profiling helpers
  - resource-usage checks

## 7. Verifier shape

Best verifier posture for this family:
- correctness check first
- performance / resource check second
- conflict-resolution audit
- check that optimization claims are backed by evidence

## 8. Common failure modes

- unclear precedence between skills
- speed advice overriding correctness
- multiple skills firing redundantly
- bundle-level guidance collapsing into one blurry monolith
- local improvements harming global behavior

## 9. Inner-loop refinement bias

Refinement should usually favor:
- clearer role partitioning
- tighter scope boundaries per sub-skill
- explicit dominance / precedence rules
- deletion of duplicated bundle prose
- explicit objective ordering

Typical good edits:
- add bundle manifest
- shrink overlapping skill text
- make correctness objective explicit
- remove ambiguous "do everything" guidance

## 10. Suggested skeleton

```markdown
---
skillx:
  name: engineering-composition-bundle
  purpose: Coordinate multiple engineering sub-skills toward one system-level objective.
  scope_in:
    - task combines performance, memory, concurrency, or systems tradeoffs
  scope_out:
    - not for single-skill tasks with a dominant obvious solution path
  requires:
    - ability to verify correctness before optimization claims
  risks:
    - objective conflict
    - composition confusion
    - premature optimization
---

# Bundle Objective
- Primary objective: preserve correctness.
- Secondary objectives: improve performance / resource efficiency.

# Sub-skill Roles
- Skill A: concurrency design
- Skill B: workload partitioning
- Skill C: memory discipline

# Precedence
- If recommendations conflict, preserve correctness first.
- Use optimization guidance only after correctness is stable.

# Acceptance
- Output remains correct.
- Claimed optimization is supported by evidence.
- Bundle roles were applied coherently.
```
