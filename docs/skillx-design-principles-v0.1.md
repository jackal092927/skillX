# SkillX Design Principles v0.1

- **Project:** `projects/multi-agent-protocol-design`
- **Date:** 2026-03-22
- **Role:** design-principles memo for the proposed SkillX / Skills Extension line
- **Status:** directional principles, not a locked schema or standard

---

## 1. Why this document exists

The literature review established a strong diagnosis:
- current skill ecosystems are good at **distribution / discoverability**,
- increasingly good at **typed tool I/O**,
- but still weak at **task-contract semantics, evaluator linkage, transfer handling, and governed evolution**.

At the same time, Xin added an equally important corrective constraint:

> **if SkillX becomes too heavy, it will fail the adoption test.**

So this document answers a narrower question than the full literature review:

> **What design principles should govern SkillX so that it becomes stronger than current skills without destroying the low-friction properties that made skills spread?**

---

## 2. Core framing

SkillX should not be designed as:
- a rigid replacement for today’s skills,
- a planning-language transplant,
- a heavy formal schema that everyone must satisfy upfront.

SkillX should instead be designed as:

> **a lightweight, optional, progressively enrichable framework that lets weakly structured skills grow into stronger task objects when the use case justifies it.**

That means SkillX is best understood as an **escalation framework**, not a one-shot formalism.

---

## 3. Principle 1 — Adoption comes first

If a skill framework cannot spread, it will not collect enough diverse real-world usage to discover what actually works.

Therefore:
- low authoring cost is a first-class design goal,
- partial/informal skill definitions must remain allowed,
- ordinary users should still be able to write lightweight skills quickly,
- strong structure should be **earned or added later**, not required everywhere from day one.

**Implication:** SkillX should measure success not only by rigor, but also by whether it preserves practical authoring flow.

---

## 4. Principle 2 — First-class does not mean heavyweight

A skill can be a first-class object without requiring a large mandatory schema.

The correct meaning of “first-class” here is:
- the system can recognize it,
- the system can version it,
- the system can evaluate it,
- the system can attach provenance to it,
- the system can gradually enrich it.

So the goal is **system-recognizable structure**, not maximal upfront formalization.

**Implication:** first-class identity should exist even for lightweight skills.

---

## 5. Principle 3 — Human provides intent; agent derives structure

Xin’s preferred authoring model is strong and should become a core principle:

> **The author should provide lightweight declarative intent/meta-information; the agent should help derive richer operational structure.**

This is the best compromise between adoption and quality.

### Human-authored minimal layer might include:
- purpose,
- rough scope,
- examples,
- preferred tools,
- risks / things to avoid,
- optional success hints.

### Agent-derived layer can propose:
- explicit allowed/forbidden operations,
- preconditions,
- postconditions,
- failure modes,
- evaluator hooks,
- transfer assumptions,
- upgrade suggestions.

**Implication:** SkillX should be designed as an **agent-assisted authoring system**, not just a static format.

---

## 6. Principle 4 — Progressive disclosure / optional escalation

SkillX should allow a skill to exist at different maturity levels.

A useful ladder is:

### Level 0 — Lightweight skill
- minimal metadata
- prose guidance
- near today’s skill ergonomics

### Level 1 — Contract-augmented skill
- scope hints
- tool and action hints
- basic preconditions / guardrails

### Level 2 — Evaluator-backed skill
- explicit outcome checks
- benchmark or harness references
- reliability criteria

### Level 3 — Transfer-aware skill
- model/tool/environment assumptions
- localization pack / adapter hints
- portability checks

### Level 4 — Evolvable skill
- versioning
- replay traces
- regression gates
- promotion / rollback / deprecation rules

The key design move is that **higher levels should remain optional**, but once a skill claims stronger status, stronger evidence should be required.

---

## 7. Principle 5 — Declarative metadata should be minimal but meaningful

If SkillX is too vague, it adds nothing. If it is too detailed, it raises the barrier too much.

So the minimal author-facing layer should focus on high-value declarative fields only.

Suggested minimal semantic fields:
- `purpose`
- `scope_in`
- `scope_out`
- `requires`
- `preferred_tools`
- `risks`
- `examples`
- `notes_for_agent`

These are intentionally lighter than a full contract, but stronger than plain free-text description.

**Implication:** the first public SkillX experiment should likely start here, not with a full formal contract language.

---

## 8. Principle 6 — Evaluation must be anti-cheat by construction

This is one of the strongest design conclusions from both the literature and Xin’s comments.

A skill evaluator should not be treated as a passive score calculator. It should be treated as a **defensive system**.

### Required evaluator mindset
The system must assume that in self-refine / self-evolve loops, the optimizing agent may discover:
- shortcut solutions,
- benchmark hacks,
- context leakage routes,
- weak spots in the acceptance layer.

So good evaluation design should include:
- execution/evaluation separation,
- fresh-context replay,
- independent verification lanes,
- hidden/adversarial tests,
- negative-transfer detection,
- contamination monitoring,
- evaluator versioning and audit trail.

**Implication:** SkillX should never equate “self-score improved” with “skill improved.”

---

## 9. Principle 7 — Builder, executor, and evaluator should be separable roles

The system should support clean role separation:
- **builder** — creates or edits the skill,
- **executor** — uses the skill on a task,
- **evaluator** — decides whether the outcome/process is acceptable.

Ideally, these roles can be assigned to:
- different runs,
- different models,
- different agents,
- or at least fresh isolated contexts.

This matters for both integrity and research quality.

**Implication:** evaluator independence should be a first-class feature of serious SkillX workflows.

---

## 10. Principle 8 — Cross-validation beats self-certification

Where possible, SkillX should prefer:
- cross-model validation,
- cross-agent validation,
- independent replay,
- external verifier execution,
- adversarial challenge lanes.

This is especially important for skills that claim:
- safety,
- reliability,
- portability,
- or benchmark superiority.

**Implication:** a mature SkillX system should be able to say not just “the generating agent believes this works,” but “independent lanes corroborated it.”

---

## 11. Principle 9 — Task contracts should be borrowable, not mandatory

The literature suggests that strong task semantics are useful. Classical planning languages prove this.
But Xin’s concern is also correct: a niche heavy formal language is not the right starting point.

So SkillX should borrow ideas such as:
- preconditions,
- postconditions/effects,
- decomposition,
- explicit failure semantics,
- analyzable constraints,

without requiring users to author in a heavyweight planning syntax.

**Implication:** SkillX should prefer a light modern contract layer, potentially generated or suggested by agents, rather than direct PDDL/HDDL authoring.

---

## 12. Principle 10 — Typed I/O is useful but not sufficient

JSON Schema, OpenAPI, MCP, PydanticAI, and similar tools are valuable.
But they mainly constrain tool invocation structure.
They do **not** by themselves define:
- what the task actually is,
- what success means,
- what the skill should refuse to do,
- how to behave under failure,
- or how to localize to a different environment.

**Implication:** SkillX must add a task-level semantic layer above typed I/O, not confuse the two.

---

## 13. Principle 11 — Portability should be explicit, not assumed

A skill that works in one setting should not silently imply cross-model or cross-environment portability.

SkillX should distinguish between:
- **portable abstract knowledge**
- and **local executable adaptation**

This means serious skills may need optional adapter packs for:
- model family,
- tool schema,
- runtime/environment,
- policy/safety context.

**Implication:** “works here” and “transfers elsewhere” should be different claims with different evidence levels.

---

## 14. Principle 12 — Negative transfer must be first-class

SkillsBench and related evidence show that a skill can hurt performance.
So SkillX should not only ask:
- “does this skill ever help?”

It should also ask:
- “where does this skill hurt?”
- “what protected tasks regress?”
- “what transfer failures are systematic?”

**Implication:** negative-transfer accounting should be part of promotion criteria, not an afterthought.

---

## 15. Principle 13 — Evolution must distinguish prompt, memory, and skill updates

The literature review showed that many self-improvement systems blur these layers.
SkillX should not.

The system should distinguish:
- **prompt updates**
- **memory updates**
- **skill-object updates**
- **localization/adapter updates**

This matters because each layer has different:
- provenance,
- portability,
- evaluator needs,
- rollback semantics,
- and scientific interpretation.

**Implication:** a SkillX auto-refine loop should always record which layer changed.

---

## 16. Principle 14 — Promotion should be evidence-gated

Not every skill needs to become a “strong skill.”
But if a skill claims stronger status, then the required evidence should increase.

Example promotion path:
- **draft** → lightweight authoring only
- **tested** → passes local evaluator hooks
- **reliable** → survives multi-run replay/regression tests
- **portable** → survives transfer checks across at least some held-out settings
- **evolvable** → has versioning, replay, rollback, and auto-refine support

**Implication:** maturity status should be tied to evidence, not only to author intent.

---

## 17. Principle 15 — Provenance, versioning, and rollback should exist early

Even lightweight skills benefit from having:
- stable identity,
- provenance,
- change history,
- ability to compare versions,
- and rollback.

Without this, auto-refine and community contribution become fragile.

**Implication:** SkillX should treat versioning/provenance as foundational infrastructure, even if full evaluator/transfer layers come later.

---

## 18. Principle 16 — Community diversity is a feature, not noise

Xin’s adoption argument is deeper than ergonomics. It is epistemic.
If many people use skills in diverse environments, that diversity becomes the testing ground from which better abstractions emerge.

So SkillX should not try to eliminate diversity too early. It should create a framework where diversity can be:
- captured,
- compared,
- evaluated,
- and gradually abstracted.

**Implication:** the framework should tolerate heterogeneous weak skills at the bottom while supporting stronger standardization higher up.

---

## 19. Principle 17 — The framework should be agent-native

If SkillX is intended for modern agent ecosystems, then the framework itself should be friendly to agent workflows:
- easy for LLMs to read,
- easy for LLMs to extend,
- easy for LLMs to critique,
- easy for agents to derive stronger structure from weak structure.

This means avoiding premature commitment to obscure or overly rigid syntax.

**Implication:** human readability + agent readability should both matter.

---

## 20. Principle 18 — Benchmark governance is part of the framework

Because evaluators can drift, saturate, or be gamed, SkillX should treat benchmark governance as part of system design.

This includes:
- evaluator changelogs,
- known-failure-mode ledgers,
- contamination checks,
- public vs private test splits,
- periodic refresh,
- adversarial challenge suites.

**Implication:** SkillX should not define skill quality without defining benchmark/evaluator maintenance responsibilities.

---

## 21. What these principles imply for next steps

These principles suggest that the right immediate project step is **not** to write a maximal formal standard.
Instead, the right next step is likely:

1. define a **minimal declarative authoring layer**,
2. define an **agent-assisted derivation workflow**,
3. define an **anti-cheat evaluator policy**,
4. test the result on a small SkillsBench rewrite experiment,
5. only then decide how much additional formalism is worth standardizing.

---

## 22. Bottom line

If reduced to one sentence, the strongest design principle is:

> **SkillX should maximize learning value per unit of authoring burden.**

That means:
- keeping authoring light,
- making rigor optional but available,
- using agents to derive structure,
- using evaluators to decide what survives,
- and using evidence to decide what gets promoted.

This is the most promising way to make SkillX stronger than today’s skills without making it too heavy to spread.
