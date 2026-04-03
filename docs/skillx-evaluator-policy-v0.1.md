# SkillX Evaluator Policy v0.1

- **Project:** `projects/multi-agent-protocol-design`
- **Date:** 2026-03-22
- **Role:** evaluator policy memo for SkillX / Skills Extension
- **Status:** exploratory policy draft, focused on anti-cheat evaluation and evidence quality

---

## 1. Why this document exists

The SkillX literature review produced a strong warning:

> **Evaluators can lie.**

A benchmark or verifier may look rigorous while still being exploitable through:
- shortcut discovery,
- context leakage,
- evaluator blind spots,
- contamination,
- or overfitting to superficial signals.

This becomes especially dangerous in self-refine / self-evolve loops, because the optimizing system is actively searching for anything that improves the score—whether or not that improvement reflects real task quality.

Xin added the critical operational correction:

> **builder/executor and evaluator must be kept as independent as possible, and mature evaluation should include cross-validation and adversarial pressure, not just passive acceptance.**

This document turns that conclusion into a concrete evaluator policy for SkillX.

---

## 2. Core claim

A SkillX evaluator should not be treated as a single score function.
It should be treated as a **defensive evaluation system** whose job is to distinguish genuine skill quality from exploitative score improvement.

That means a good evaluator policy must address not only:
- whether the task succeeded,

but also:
- whether the process respected constraints,
- whether the skill generalizes beyond the exact evaluation context,
- whether the result survives independent checking,
- whether the score could have been achieved through a shortcut.

---

## 3. Policy goals

### Goal A — protect against cheating and shortcut optimization
The evaluator should assume the agent may discover loopholes.

### Goal B — separate outcome quality from evaluator weakness
A high score should not be accepted as evidence unless the evaluator is itself credible.

### Goal C — make evidence levels explicit
Evaluation should produce not only scores, but a confidence-backed evidence class.

### Goal D — support lightweight and advanced SkillX levels
The evaluator policy should work for both small local skills and stronger benchmark-backed skills.

### Goal E — stay practical
Not every skill needs a full adversarial benchmark suite. The policy should support escalation by maturity level.

---

## 4. Evaluator mindset: assume optimization pressure

The most important evaluator design principle is psychological and methodological:

> **Do not assume the optimizing system is honest just because the authors are honest.**

In iterative refinement settings, any scoring surface can become an objective.
If the score is weakly aligned with real quality, the system may learn to exploit the gap.

Therefore the evaluator must be designed under the assumption that the following may happen:
- the agent learns the format of visible tests,
- the agent reuses leaked context from the builder path,
- the agent produces outputs that satisfy shallow checks while violating deeper intent,
- the agent overfits to static public benchmark artifacts,
- the agent learns to optimize one metric while harming another.

This does not imply distrust of a specific agent. It is simply the correct assumption for any optimization loop.

---

## 5. Required role separation

A mature SkillX workflow should distinguish at least three roles:

### 5.1 Builder
Creates or edits the skill definition.

### 5.2 Executor
Uses the skill on concrete tasks.

### 5.3 Evaluator
Decides whether the result is acceptable.

These roles should be separable by:
- fresh run context,
- different session,
- different agent,
- different model,
- or an external deterministic harness.

The stricter the claim, the stronger the role separation should be.

### Policy implication
A skill should not receive strong evidence status solely because the same context that created it also declared it successful.

---

## 6. Evaluation independence ladder

### Level E0 — self-check only
- same agent, same run, same context
- useful for draft-stage iteration only
- **not enough for serious promotion**

### Level E1 — fresh-context replay
- same agent or model allowed
- but evaluation happens in a separate fresh context or post-hoc replay
- protects against some context leakage

### Level E2 — independent evaluator lane
- separate evaluator agent/model or separate deterministic verifier
- builder/executor does not directly control final acceptance

### Level E3 — cross-model or cross-agent corroboration
- at least one additional independent evaluation lane using a different model/agent family
- useful for portability/reliability claims

### Level E4 — adversarial evaluation
- hidden tests, perturbation checks, challenge cases, negative-transfer probes, contamination defense
- required for strong claims about robustness or safety

This ladder supports progressive escalation without forcing every lightweight skill into the heaviest setup.

---

## 7. Four-layer evaluator stack

A SkillX evaluator should ideally be composed from four layers.

### 7.1 Layer 1 — Outcome verifier
This is the most important layer whenever possible.
It checks whether the world ended up in the correct state.

Examples:
- unit/integration tests pass,
- expected files are created or modified correctly,
- database state matches expected outcome,
- environment/task state satisfies the goal,
- all placeholders resolved or explicitly flagged.

### 7.2 Layer 2 — Process verifier
Some skills constrain *how* a task should be solved, not just the final state.
This layer checks:
- tool choice/order,
- policy compliance,
- prohibited action avoidance,
- retry/rollback correctness,
- evidence submission behavior.

### 7.3 Layer 3 — Quality rubric
Some task qualities are too nuanced for a purely deterministic checker.
This layer may use:
- LLM-as-judge,
- human review,
- structured rubrics.

However, this layer should be treated as a supplement, not the sole source of truth, unless deterministic checking is impossible.

### 7.4 Layer 4 — Reliability and variance
A skill should not be treated as strong if it only works once.
This layer evaluates:
- repeatability,
- pass@k / pass^k,
- seed variance,
- stability across slightly varied inputs,
- regression risk.

---

## 8. Anti-cheat policy requirements

### 8.1 Fresh-context evaluation
The evaluator should, when feasible, run in a context that does not include hidden builder reasoning or prior attempts.

### 8.2 Hidden or held-out checks
Not all evaluator logic should be fully visible to the optimizing system.
This may include:
- hidden test cases,
- held-out task splits,
- private verifier logic,
- randomized perturbation cases.

### 8.3 Adversarial challenge cases
A strong evaluator should include cases designed to trigger common shortcuts.
Examples:
- output formatting traps,
- policy-violation temptations,
- spurious correlations,
- fragile assumptions,
- common benchmark hacks.

### 8.4 Negative-transfer probes
A skill should be tested not only where it is expected to help, but also on protected tasks where it must not cause harm.

### 8.5 Cross-lane corroboration
Where claims are strong, at least one independent lane should verify the result.

### 8.6 Audit trail
Every meaningful evaluation should leave a record of:
- evaluator version,
- task slice,
- execution context type,
- result,
- evidence references,
- failure classification.

---

## 9. Evaluator types by task regime

### 9.1 Deterministic artifact/state evaluators
Best when available.
Examples:
- tests,
- file diffs,
- schema checks,
- DB state checks,
- placeholder completeness,
- structured output validity.

### 9.2 Simulator/environment evaluators
Useful when tasks happen in interactive environments.
Examples:
- browser or OS tasks,
- benchmark environments like WebArena/OSWorld/τ-bench.

### 9.3 LLM-judge evaluators
Useful for:
- nuanced writing quality,
- structured compliance where deterministic parsing is incomplete,
- preference-like dimensions.

But they must be calibrated and bounded.

### 9.4 Human review evaluators
Most expensive but often the most valuable for:
- ambiguous edge cases,
- rubric auditing,
- evaluator debugging,
- adjudicating unresolved conflicts.

### Policy implication
The evaluator policy should prefer the strongest available evaluator type, not default to the easiest one.

---

## 10. LLM-as-judge policy

LLM-as-judge is allowed, but with constraints.

### It should generally be used for:
- nuanced quality signals,
- rubric-based comparison,
- ambiguity resolution,
- second-order process assessment.

### It should generally not be the only evaluator when:
- deterministic state verification is possible,
- the task is safety-sensitive,
- the task is easily benchmarked by execution,
- the skill is making strong reliability claims.

### Additional safeguards
- use explicit rubric prompts,
- calibrate against periodic human review,
- test for judge inconsistency,
- use pairwise or comparative judging where helpful,
- separate builder and judge contexts,
- prefer different model families when feasible.

---

## 11. Evidence classes for SkillX evaluation

A useful evidence ladder is:

### Class A — self-claimed
- self-check only
- no fresh replay
- no independent verifier

### Class B — locally verified
- deterministic or fresh-context checks
- but limited task slice and no independent corroboration

### Class C — independently corroborated
- separate evaluator lane or model
- multiple successful checks
- negative-transfer not yet fully established

### Class D — robust
- replayed,
- independently checked,
- adversarially challenged,
- variance characterized,
- no major known evaluator caveats on tested scope

### Class E — portable
- robust plus transfer evidence across at least some held-out models, environments, or agent lanes

This ladder helps prevent overclaiming.

---

## 12. Benchmark governance policy

Because benchmarks can decay or be gamed, evaluator policy must include benchmark governance.

### Required governance items
- evaluator versioning,
- benchmark versioning,
- known-failure-mode ledger,
- contamination monitoring,
- challenger/counterexample process,
- deprecation path when a benchmark becomes unreliable.

### Key rule
A skill should not retain “strong evidence” status forever by inertia.
If the evaluator weakens or becomes stale, evidence status should be re-audited.

---

## 13. Failure taxonomy requirements

A good evaluator should not produce only pass/fail.
It should also classify failure types where practical.

Suggested failure categories:
- missing prerequisite / invalid input,
- wrong outcome,
- policy violation,
- prohibited action taken,
- partial completion,
- shortcut exploit / evaluator gaming,
- regression on protected tasks,
- unsupported transfer / environment mismatch,
- judge disagreement / ambiguous result.

This is important because evaluator-guided evolution depends on knowing *how* the skill failed.

---

## 14. Recommended minimum evaluator policy by skill maturity level

### Draft / lightweight skill
- self-check allowed
- at least one fresh-context replay recommended
- no strong quality claims

### Contract-augmented skill
- deterministic or structured outcome checks preferred
- basic process constraints where relevant
- fresh-context evaluation required for serious local use

### Evaluator-backed skill
- explicit outcome verifier required
- independent evaluator lane recommended
- multi-run reliability measurement recommended

### Transfer-aware skill
- at least one independent corroboration lane
- explicit negative-transfer probes
- held-out context or alternate-model checks when feasible

### Evolvable skill
- replay corpus,
- regression suite,
- adversarial challenge lane,
- full audit trail,
- evaluator/version governance required.

---

## 15. Candidate evaluation checklist

For each serious evaluation run, the evaluator policy should encourage logging answers to the following:

1. What was the claimed scope of the skill?
2. What task slice was used?
3. Was evaluation fresh-context or same-context?
4. Was there an independent evaluator lane?
5. What deterministic checks were used?
6. What rubric-based checks were used?
7. Were there hidden or adversarial cases?
8. Was negative transfer tested?
9. What was the reliability signal (single-run vs multi-run)?
10. What evaluator/benchmark version was used?
11. What failure type occurred, if any?
12. What caveats remain?

---

## 16. First concrete experiment path for this project

For the current project, the most natural first application is a small SkillsBench-aligned pilot.

### Proposed pilot
1. Select a small set of tasks where existing skills show mixed effects.
2. Compare:
   - no skill,
   - original skill,
   - SkillX minimal rewrite,
   - SkillX minimal rewrite + agent-derived evaluator hints.
3. Evaluate with at least two lanes:
   - deterministic benchmark verifier lane,
   - fresh-context or independent review lane.
4. Add at least one anti-shortcut probe:
   - hidden case,
   - protected-task regression check,
   - or perturbed input slice.
5. Record failure taxonomy and negative-transfer cases.

This would test not just whether SkillX helps, but whether its evaluator policy improves scientific trustworthiness.

---

## 17. Bottom line

The strongest evaluator principle for SkillX is simple:

> **Do not optimize for easy scoring. Optimize for trustworthy evidence.**

That means:
- independence over convenience,
- adversarial pressure over passive acceptance,
- auditability over vague confidence,
- and explicit evidence classes over unqualified success claims.

If SkillX gets this layer right, it has a chance to avoid the biggest failure mode of many skill/evolution systems: looking better because the evaluator got weaker.
