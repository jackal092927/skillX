# Class-Aware C2 Bundle Notes — parallel-tfidf-search

## Bundle Objective

Primary objective: preserve correctness equivalence to the sequential TF-IDF/search baseline.

Secondary objectives:
1. achieve meaningful multi-core speedup,
2. keep memory/resource usage practical under parallel load.

This remains C2: role clarity + ordering + conflict policy, without heavy derived-layer machinery.

## Role Partitioning

- `python-parallelization` (**primary owner**)
  - decides concurrency model and worker-call boundaries
  - enforces equivalence-first acceptance gate
  - owns deterministic output assembly guarantees

- `workload-balancing` (**support: throughput shaping**)
  - tunes partitioning/scheduling once parallel model exists
  - reduces stragglers and idle cores
  - cannot change semantic behavior or override primary correctness constraints

- `memory-optimization` (**support: resource discipline**)
  - limits duplication/materialization/caching bloat
  - keeps RAM growth compatible with sustained parallel execution
  - cannot alter semantics or replace core parallel architecture decisions

## Objective Ordering (Application Sequence)

1. Establish correct parallel semantics (`python-parallelization`).
2. Improve distribution efficiency (`workload-balancing`).
3. Harden memory behavior under that execution plan (`memory-optimization`).
4. Re-check correctness after any balancing/memory adjustment.

## Precedence and Conflict Resolution

If advice conflicts, apply this order:
1. **Correctness-equivalence dominates** (primary gate).
2. **Parallel semantic stability** (from `python-parallelization`).
3. **Work distribution improvements** (from `workload-balancing`).
4. **Memory/resource refinements** (from `memory-optimization`).

Tie-break rules:
- Prefer a slower correct system over a faster drifting one.
- Prefer simpler balancing over aggressive heuristics when gains are marginal.
- Prefer bounded-memory designs when throughput gains are otherwise similar.

## Composition Guardrails

- Do not let all three skills fire as equal co-owners on every decision.
- Do not accept benchmark-only speed claims without correctness checks.
- Do not introduce benchmark-specific hacks or evaluator-targeted shortcuts.
- Keep changes task-local to parallel TF-IDF indexing/search.

## Expected C2 Value

- Less overlap/confusion about who decides what.
- Fewer contradictions between speed, balancing, and memory advice.
- Cleaner iterative loop: correct first, then optimize with explicit boundaries.
