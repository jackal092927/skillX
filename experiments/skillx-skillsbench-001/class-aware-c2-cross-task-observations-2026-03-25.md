# Class-Aware C2 Cross-Task Observations — 2026-03-25

- **Project:** `projects/multi-agent-protocol-design`
- **Experiment line:** `experiments/skillx-skillsbench-001`
- **Role:** first review memo over isolated subagent-produced class-aware C2 drafts
- **Status:** review memo after 6 isolated Codex 5.3 workers completed

---

## 1. Purpose

This memo reviews the first batch of **class-aware C2** rewrites produced in isolated subagent contexts.

The goal is not yet to judge benchmark performance.
The goal is to understand what kinds of structural changes the class-aware template families are actually inducing, and whether those changes look coherent enough to justify the next experimental step.

The reviewed tasks are:
1. `offer-letter-generator`
2. `parallel-tfidf-search`
3. `trend-anomaly-causal-inference`
4. `exoplanet-detection-period`
5. `energy-ac-optimal-power-flow`
6. `taxonomy-tree-merge`

---

## 2. High-Level Conclusion

The class-aware C2 approach appears to be doing something meaningful and coherent.

The rewrites do **not** merely rephrase the generic C2 baseline. Instead, they systematically shift emphasis in ways that match the intended task class:

- **Artifact Generator** → output contract + no-invention + missing-input discipline
- **Engineering Composition Bundle** → role partitioning + objective ordering + conflict resolution
- **Analytic Pipeline Bundle** → stage-local artifacts + handoff contracts + completion gates
- **Methodology-Heavy Guardrail** → fit checks + assumptions + abstention/branch rules + anti-patterns

This is a good sign.
It suggests the task-class templates are acting as real structural priors rather than decorative labels.

---

## 3. Cross-Task Structural Pattern

Across all six tasks, the main class-aware C2 effect is:

> **moving from “what the skill knows” toward “what kind of structure this task requires.”**

In practice, the rewrites repeatedly did four things:

### 3.1 Made acceptance more explicit
Even though these are still C2 rewrites, most outputs added sharper acceptance posture:
- output contract checks,
- completion gates,
- stage checks,
- or boundary-use checks.

This suggests that class-awareness naturally pulls verifier thinking *earlier* in the authoring stack.

### 3.2 Made boundaries more explicit
This appeared in different forms:
- `scope_out` / no-invention on artifact generation,
- role boundaries in engineering bundles,
- stage boundaries in analytic pipelines,
- method-fit boundaries in guardrail tasks.

This is important because our earlier SkillX findings already suggested that much of the gain is about **conditional utility control**, not raw average performance lift.

### 3.3 Replaced generic prose with task-shape-specific discipline
The rewrites consistently removed or deemphasized generic tutorial-like language in favor of compact structure:
- contract language,
- sequencing rules,
- handoff rules,
- assumptions,
- anti-patterns.

This is especially aligned with the broader insight that stronger models often need **less**, but **sharper**, guidance.

### 3.4 Localized guidance instead of centralizing it
In the analytic pipeline tasks especially, the rewrites did not inflate one giant bundle-level monolith.
Instead, they distributed guidance into stage-local contracts and handoff expectations.

This is likely a very important design principle for future C3/C4 work.

---

## 4. Per-Class Observations

### 4.1 Artifact Generator (`offer-letter-generator`)

The class-aware prior pushed the rewrite toward:
- explicit output contract,
- preserve-structure rule,
- no-invention rule,
- deterministic acceptance,
- stronger missing-input handling.

This looks like a clean and plausible class effect.
The rewrite is still lightweight, but it is more sharply aligned to the actual task shape than the generic C2.

### 4.2 Engineering Composition Bundle (`parallel-tfidf-search`)

This class-aware rewrite did the most obvious coordination work:
- one primary owner,
- secondary support roles,
- objective ordering,
- explicit conflict resolution.

This is exactly the kind of structure generic minimal rewrites are likely to under-specify.
It gives us a concrete way to test whether the class-aware family improves multi-skill usability.

### 4.3 Analytic Pipeline Bundle (`trend`, `exoplanet`, `energy`)

This class was the most consistent across tasks.
All three rewrites emphasized:
- stage graph,
- explicit input/output artifacts,
- handoff rules,
- stage-local checks,
- bundle completion discipline.

This is promising because it means the class-aware template is inducing repeatable structure across distinct domains (analytics, astronomy, energy optimization), not just one task.

This may be the strongest current candidate for the first true outer-loop learning object.

### 4.4 Methodology-Heavy Guardrail (`taxonomy-tree-merge`)

This rewrite clearly moved in the intended direction:
- fit/decision gate,
- surfaced assumptions,
- branch/abstention logic,
- compact anti-patterns,
- reduced methodological overcommitment.

This seems especially important because it operationalizes the idea that sometimes the right class-aware edit is **deletion and restraint**, not elaboration.

---

## 5. What This Suggests About the Project Design

The current results support a stronger interpretation of the two-loop framing.

### 5.1 Class-aware C2 can serve as a meaningful R0
A class-aware C2 rewrite is not yet C3 or C4, but it already behaves like a **template-instantiated starting point** for the inner-loop skill evolver.

More precisely:
- **Outer Loop / MetaEvolver** provides the template family prior.
- **Class-aware C2** instantiates that prior for a specific task.
- **Inner Loop** can then refine from that starting point using derived expansion and bounded refine.

This is a clean and useful decomposition.

### 5.2 The outer-loop object should be “template family,” not “one universal prompt rule”
These drafts reinforce that the portable object is not a universal skill law.
It is a **family-specific structural prior**.

That makes the outer loop more realistic and experimentally tractable.

### 5.3 Risk and verifier posture should stay first-class
Even in C2, risk and verifier-related structure kept reappearing naturally.
That supports Xin's judgment that these dimensions should remain part of the high-level clustering and not be treated as optional afterthoughts.

---

## 6. Recommended Next Step

The next experiment should not jump directly to class-aware C4.
The cleanest next comparison is:

> **generic C2 vs class-aware C2**

for one task per class.

Recommended first comparison set:
1. `offer-letter-generator`
2. `parallel-tfidf-search`
3. `trend-anomaly-causal-inference`
4. `taxonomy-tree-merge`

That would let us test whether the class-aware template family improves:
- trigger/usefulness,
- boundary control,
- multi-skill coordination,
- and negative-transfer resistance.

---

## 7. Working Takeaway

The first isolated subagent batch supports the following working claim:

> **Task-class-aware templates are a plausible outer-loop object because they induce systematic, class-specific structural changes in C2 rewrites before any heavy derived expansion or bounded refine begins.**

That is exactly the kind of intermediate object MARC needs if it wants to move from local skill optimization toward reusable meta-guidance.
