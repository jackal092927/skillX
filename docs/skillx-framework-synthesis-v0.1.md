# SkillX Framework Synthesis v0.1

- **Project:** `projects/multi-agent-protocol-design`
- **Date:** 2026-03-22
- **Role:** project-facing synthesis memo translating the SkillX literature review into concrete design directions
- **Status:** exploratory design memo, not a locked spec

---

## 1. Why this memo exists

The literature review suggests that today’s skill ecosystems are strong in three areas:
- portability/distribution,
- discoverability,
- typed tool I/O.

But they are still weak in the area that matters most for serious reuse and evolution:

> **a skill as a task object with explicit semantics, evaluation, transfer behavior, and upgrade path.**

This memo translates that research conclusion into design directions for a possible **SkillX / Skills Extension** layer.

---

## 2. Core project claim

SkillX should not be framed as “a stricter markdown format.”
It should be framed as:

> **a lightweight, adoption-friendly extension layer that lets a skill grow into a declarable, verifiable, transferable, and evolvable task object.**

The phrase “lightweight” matters. The goal is **not** to replace today’s free-form skills with a heavy mandatory formalism. The goal is to preserve why skills spread in the first place—low friction and diversity—while making it possible for stronger skills to carry more structure when needed.

---

## 3. Key design tension

### Tension A — rigor vs adoption

A highly formal schema can improve reliability, but it also raises authoring cost.
If SkillX requires too much upfront structure, many ordinary users will simply not adopt it.

### Tension B — flexibility vs verifiability

If everything remains prose-only, then skill quality, evaluator quality, and transfer quality stay under-specified.
But if everything becomes fully formal, the system becomes too rigid for many practical automations.

### Proposed resolution

SkillX should follow an **optional escalation model**:

1. **Level 0 — Lightweight skill**
   - minimal declarative metadata only
   - almost as easy to author as today’s skills

2. **Level 1 — Contract-augmented skill**
   - adds scope, allowed operations, basic success conditions

3. **Level 2 — Evaluator-backed skill**
   - adds executable tests / verifiers / benchmark hooks

4. **Level 3 — Transfer-aware skill**
   - adds localization/adaptation metadata and portability checks

5. **Level 4 — Evolvable skill**
   - adds versioning, replay, promotion rules, regression gates, and auto-refine hooks

This preserves low-friction authoring while allowing high-value skills to grow into stronger objects.

---

## 4. Recommended minimal SkillX architecture

### Layer A — Author-facing declarative metadata (minimal)

This is the part ordinary authors should be able to write with low burden.
Suggested fields:
- `name`
- `purpose`
- `scope_in`
- `scope_out`
- `requires`
- `preferred_tools`
- `risks`
- `examples`

The author should not need to fully specify every operational detail.
Instead, the system can help infer and propose the stronger structure.

### Layer B — Agent-derived task contract (semi-automatic)

From the minimal metadata, an agent can help derive:
- `allowed_operations`
- `forbidden_operations`
- `preconditions`
- `postconditions`
- `failure_modes`
- `repair_actions`
- `acceptance_hooks`

This matches Xin’s preferred authoring model:
- the human provides lightweight declarative intent,
- the agent does most of the heavy lifting.

### Layer C — Evaluator contract

Every serious SkillX object should be able to attach one or more evaluator hooks.
Suggested evaluation layers:

1. **Outcome verifier**
   - file/test/database/environment state
2. **Process verifier**
   - trajectory/tool policy/rule compliance
3. **Quality rubric**
   - LLM judge or human judge with calibration
4. **Reliability layer**
   - multi-run consistency / variance / pass@k-style reporting

### Layer D — Transfer / localization pack

To avoid false assumptions of portability, SkillX should support optional adapters for:
- model family,
- tool schema,
- environment/runtime,
- policy/safety constraints.

### Layer E — Evolution / governance layer

For mature skills, SkillX should support:
- versioning,
- candidate branches,
- replay-based validation,
- regression checks,
- promotion / rollback / deprecation.

---

## 5. Evaluator design: additional project conclusion

The literature review already showed that evaluator quality is a bottleneck. Xin added an important design correction that sharpens this further:

> **evaluator design must actively defend against cheating, shortcut exploitation, and context leakage.**

This implies several concrete design requirements.

### 5.1 Execution / evaluation separation

The agent that designs or executes a solution should not share too much context with the final acceptance layer.
At minimum, SkillX eval should support:
- execution context isolation,
- independent test harness execution,
- post-hoc replay in a fresh context.

### 5.2 Cross-model / cross-agent validation

Whenever possible, the system should evaluate a skill with a different grader or validator agent than the one that generated the solution.
The strongest setups may include:
- model diversity,
- independent review agent,
- independent replay/verifier lane.

### 5.3 Adversarial evaluator design

A mature SkillX evaluator should not only check nominal success.
It should also include anti-shortcut probes such as:
- adversarial hidden tests,
- perturbation checks,
- policy-violation traps,
- context-isolation stress tests,
- negative-transfer detection on protected task subsets.

### 5.4 Benchmark governance

SkillX should assume that benchmarks can decay or become gameable over time.
Therefore benchmark management should include:
- evaluator versioning,
- known-failure-mode logs,
- contamination checks,
- periodic refresh or private tracks.

---

## 6. Why PDDL/HDDL matter—and why they are not the current answer

The literature review found that classical planning languages are still the clearest reference point for strong declarative task semantics.
They offer:
- preconditions,
- effects,
- decomposition,
- analyzable contracts.

But Xin’s concern is correct and important:
- they are relatively niche,
- they may be awkward for LLM-first authoring,
- they may create integration burden if they require external planning infrastructure,
- and they are not the current product/research priority.

So the correct takeaway is **not** “SkillX should adopt PDDL/HDDL.”
It is:

> **SkillX should borrow the useful semantic ideas of planning languages without inheriting their authoring burden or integration weight.**

If a future DSL is needed, it should likely be a lighter, modern, Agent-AI-friendly contract language rather than a direct transplant of classical planning syntax.

---

## 7. Strongest concrete design directions

### Direction 1 — Optional contract blocks, not mandatory heavy formalism
The default adoption path must stay light.

### Direction 2 — Human writes intent; agent proposes structure
This is likely the best compromise between quality and adoption.

### Direction 3 — SkillX promotion should be evidence-gated
A skill can remain lightweight, but promotion to stronger statuses should require evidence.

### Direction 4 — Evaluation should be anti-cheat by construction
Fresh context, cross-agent validation, adversarial acceptance design.

### Direction 5 — Transfer should be explicit, not assumed
A skill that works only in one model/tool/runtime should not silently claim generality.

### Direction 6 — Evolution must distinguish prompt vs memory vs skill updates
Otherwise attribution and governance break down.

---

## 8. A practical mental model

A good working mental model is:

- **today’s skills** ≈ lightweight packageable guidance
- **SkillX** ≈ a ladder that allows some skills to remain lightweight while letting stronger ones accumulate contract, evaluator, transfer, and evolution layers

So SkillX should be understood less as a replacement format and more as an **escalation framework**.

---

## 9. First candidate experiment path

The literature now supports a concrete experiment path inside this project:

1. Take a subset of **SkillsBench** tasks/skills.
2. Rewrite selected skills into **SkillX Level 0/1** (light declarative metadata + basic contract hints).
3. Let an agent derive fuller contract/evaluator structure.
4. Run paired benchmark evaluation:
   - no skill,
   - original skill,
   - SkillX rewritten skill.
5. Add anti-cheat / isolated-evaluator settings.
6. Measure:
   - average gain,
   - per-task gain,
   - negative transfer,
   - reliability,
   - evaluator robustness.

This creates a controlled first test of whether declarative augmentation actually helps.

---

## 10. Bottom line

The right next step is probably **not** to design a maximal formal SkillX standard immediately.
The right next step is to design a **lightweight, optional, agent-assisted contract layer** that preserves adoption while enabling stronger evaluation and evolution where needed.

That is the most project-compatible interpretation of the current literature and Xin’s design preferences.
