# SkillX Dataset Selection Note v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-10
- **Role:** executable shortlist for selecting the next benchmark datasets for SkillX
- **Status:** selection note, intended to freeze near-term benchmark priority

---

## 1. Purpose

This note reframes benchmark selection around the actual object SkillX wants to optimize.

The main question is **not**:

> Which benchmark is popular, or easiest to plug into a harness?

The main question is:

> Which datasets give us the cleanest signal for improving the design of external skills on matched tasks?

That means the ideal SkillX dataset should provide:

1. **task-level evaluation clarity**,
2. **evaluation tightly bound to the task description itself**,
3. a natural place to attach or compare **skill artifacts**,
4. support for **paired evaluation** (`no skill` vs `skill` vs `rewritten skill`),
5. interpretable failure modes including **negative transfer**.

This note therefore organizes candidates into:
- **native skill benchmarks**,
- **adapted skill benchmarks**,
- **not priority**.

---

## 2. Selection criteria

We will score candidates mainly along these axes.

### C1. Task-eval clarity
Does each task have a clear, stable, credible verifier?

### C2. Task-description binding
Is the evaluation criterion already implicit or explicit in the task itself, rather than added later as an ad hoc judge?

### C3. Skill-task fit
Can we naturally evaluate the marginal utility of an attached skill or scaffold on the task?

### C4. Paired-eval friendliness
Can we cleanly run:
- no skill,
- native/reference skill,
- SkillX rewrite,
- optional class-aware or refined variant?

### C5. Adapter complexity
How hard is it to run the benchmark under our current SkillX execution stack?

### C6. Interpretability for outer-loop learning
Will the results teach us something actionable about skill format, scope control, task-class fit, and negative transfer?

---

## 3. Category A — Native skill benchmarks

These benchmarks are already close to the real SkillX question: **how much does a skill help on a task, under a credible evaluation protocol?**

## A1. SkillsBench

**Priority:** `P0`  
**Role:** primary first substrate

### Why it is the best current fit
- It directly evaluates **skill usefulness** rather than only raw task success.
- It already supports the central SkillX question: whether a rewritten or re-structured skill improves marginal utility.
- It has strong paired-comparison logic built into the benchmark story.
- It already anchors much of the current SkillX taxonomy, prompt-bank, and rewrite planning work.

### Fit against criteria
- **Task-eval clarity:** high
- **Task-description binding:** high
- **Skill-task fit:** very high
- **Paired-eval friendliness:** very high
- **Adapter complexity:** low to medium
- **Interpretability:** very high

### Recommended SkillX use
Use as the **first official benchmark family** for:
- original-skill vs SkillX-rewrite comparisons,
- task-class-aware prompt-bank assignment experiments,
- negative-transfer analysis,
- lightweight refine / bounded refine comparisons.

### Near-term decision
**Keep SkillsBench as the primary SkillX benchmark.**

---

## A2. SWE-Skills-Bench

**Priority:** `P1`  
**Role:** second native skill benchmark, especially for SWE realism

### Why it matters
- It asks the right skeptical question: **do skills actually help in real-world SWE tasks?**
- It emphasizes marginal utility rather than assuming skills help by default.
- It appears to use requirement-driven tasks, explicit acceptance criteria, fixed environment assumptions, and execution-based testing.
- It is particularly valuable for exposing version mismatch, scope mismatch, and context incompatibility.

### Fit against criteria
- **Task-eval clarity:** high
- **Task-description binding:** high
- **Skill-task fit:** high
- **Paired-eval friendliness:** high
- **Adapter complexity:** medium
- **Interpretability:** high

### Important limitation
- It is more domain-specific than SkillsBench.
- It is not the best first substrate for broad task-class discovery.
- It is best viewed as a **native specialist lane** for SWE-heavy skill evaluation.

### Recommended SkillX use
Use after or alongside SkillsBench for:
- testing whether SkillX gains persist under stricter SWE execution conditions,
- analyzing when skills fail because they overfit outdated or mismatched context,
- stress-testing scope control and contract quality.

### Near-term decision
**Adopt as the second benchmark family after SkillsBench.**

---

## A3. SkillCraft

**Priority:** `P2`  
**Role:** second-wave native benchmark, but not the same question as SkillsBench

### Why it is still relevant
SkillCraft is skill-related in a real sense, but its main object is different.

It focuses more on:
- tool composition,
- online skill formation,
- reusable skill libraries,
- efficiency and reuse of composed skills.

In other words, it is closer to:

> can agents learn and reuse composed skills?

than to:

> how should we write an external skill artifact so it helps a matched task?

### Fit against criteria
- **Task-eval clarity:** medium to high
- **Task-description binding:** medium
- **Skill-task fit:** medium for current SkillX, high for future internalization/composition work
- **Paired-eval friendliness:** medium
- **Adapter complexity:** medium to high
- **Interpretability:** medium for current SkillX line

### Why it is not first-wave
- The benchmark question is not identical to the current SkillX question.
- It mixes in the agent’s own skill-discovery ability.
- Its runtime seems to rely on a more custom skill-library protocol rather than the simpler “attach external skill and compare” setup.

### Recommended SkillX use
Treat SkillCraft as a **future bridge benchmark** between:
- the current augmentation-first SkillX line, and
- the later internalization / self-composition line.

### Near-term decision
**Do not use SkillCraft as a replacement for SkillsBench or SWE-Skills-Bench.**  
Use it later if we want to test whether SkillX artifacts become good substrates for agent-generated reusable skills.

---

## 4. Category B — Adapted skill benchmarks

These benchmarks are not natively about skill efficacy, but can be converted into useful SkillX substrates by attaching skills and using paired evaluation.

## B1. AppWorld

**Priority:** `P1-adapted`

### Why it is promising
- Strong task definitions and stateful evaluation.
- Multi-app workflows make it a good target for task-class-aware scaffolds.
- The verifier is not a vague external judge, which matches the SkillX selection principle.

### Why it is adapted rather than native
- The benchmark itself does not ask the “do skills help?” question by default.
- We would need to define the skill attachment protocol ourselves.

### Recommended SkillX use
Best first adapted benchmark after the native pair.

---

## B2. FeatureBench

**Priority:** `P2-adapted`

### Why it is promising
- Structured implementation tasks are good for testing engineering-composition skills.
- Likely good fit for contract-heavy or decomposition-heavy SkillX artifacts.

### Caveat
- Less directly skill-native than SkillsBench.
- More useful for a later generalization check than for the first proof.

---

## B3. ML-Dev-Bench

**Priority:** `P2-adapted`

### Why it is promising
- Good for analytic-pipeline and methodology-heavy scaffolds.
- Could reveal whether SkillX transfers to multi-step ML development work.

### Caveat
- More integration work.
- Less directly aligned with current benchmark-native proof obligations.

---

## B4. Terminal-Bench 2.0

**Priority:** `P3-adapted`

### Why it still matters
- It likely fits Harbor-style execution well.
- It is a strong technical specialist lane for terminal-native tasks.
- It is useful for testing whether prompt-bank or scaffold gains transfer to terminal-heavy settings.

### Why it is not first priority
- It is not a native skill-efficacy benchmark.
- Its task family is narrower and more terminal/devops-shaped than the current core SkillX question.

### Recommended SkillX use
Use later as a technical transfer benchmark, not the first main substrate.

---

## 5. Category C — Not priority

These datasets may be useful eventually, but they are not the best near-term targets for the current SkillX question.

## C1. GAIA / GAIA2

### Why not now
- Valuable as a broad assistant benchmark, but less clean for isolating skill utility.
- Harder to ensure that evaluation remains tightly bound to the task description in the specific way we need for skill optimization.
- More mixed signals, more confounds, less clean marginal-utility reading.

### Status
**Later generalization benchmark, not near-term priority.**

---

## C2. BFCL

### Why not now
- Better for tool-calling protocol quality than for general skill-artifact design.
- Could be useful for a narrow API/tool-use line, but not for the main SkillX benchmark question.

### Status
**Not current priority.**

---

## C3. PIXIU

### Why not now
- Too domain-specific for the current general SkillX line.
- Better as a domain transfer probe after the main method stabilizes.

### Status
**Not current priority.**

---

## C4. Legacy broad benchmarks previously discussed

Examples include:
- GAIA v1,
- TAU / TAU2-style lines,
- FRAMES,
- GDPval,
- coding-only broad lanes such as generic SWE-bench use.

### Why not now
Most of these fail one or more of the current needs:
- too saturated,
- too broad and noisy for clean skill marginal-utility measurement,
- not naturally skill-centered,
- or not cleanly bound to task-intrinsic evaluation.

---

## 6. Recommended shortlist freeze

## Phase 1 — Immediate native shortlist

1. **SkillsBench**
2. **SWE-Skills-Bench**

These should be treated as the current official shortlist for the first serious SkillX evaluation line.

### Why this pair
- Both are close to the real object of interest: **skill efficacy on matched tasks**.
- Both support strong evaluation discipline.
- Both make negative transfer and conditional utility visible.
- Neither requires us to redefine the benchmark question from scratch.

---

## Phase 2 — Near-next exploratory shortlist

3. **SkillCraft**
4. **AppWorld**

### Why this pair next
- **SkillCraft** extends toward skill composition and possible internalization / self-constructed skill reuse.
- **AppWorld** extends toward realistic multi-app workflow adaptation under stronger task-state constraints.

---

## Phase 3 — Transfer/generalization shortlist

5. **FeatureBench**
6. **ML-Dev-Bench**
7. **Terminal-Bench 2.0**

These should be used after the native benchmark story is already coherent.

---

## 7. Practical execution recommendation

## Recommended official stance right now

> SkillX should optimize for **task-skill pairs with task-intrinsic evaluation**, not for benchmark-name coverage.

That means the current benchmark plan should be:

### Primary line
- **SkillsBench**

### Immediate secondary line
- **SWE-Skills-Bench**

### Deferred but important bridge line
- **SkillCraft**

### First adapted non-native line
- **AppWorld**

---

## 8. Concrete next actions

1. **Freeze the native shortlist** in project planning as:
   - SkillsBench
   - SWE-Skills-Bench
   - SkillCraft (deferred second-wave native)

2. **Update benchmark language** in SkillX docs so the main object is:
   - not “benchmark compatibility,”
   - but “skill marginal utility on matched tasks with task-intrinsic evaluation.”

3. **Create one benchmark-onboarding memo per shortlisted dataset** covering:
   - task format,
   - verifier type,
   - skill attachment point,
   - paired evaluation protocol,
   - adapter complexity,
   - likely task-class coverage.

4. **Do not expand into broad benchmark collection yet.**
   The next evidence should come from a small number of well-chosen datasets with clean signal.

---

## 9. Final recommendation

If SkillX needs a clean, defensible, near-term dataset selection note, the answer is:

### Native skill benchmarks
- **SkillsBench** — primary
- **SWE-Skills-Bench** — secondary
- **SkillCraft** — later bridge benchmark

### Adapted skill benchmarks
- **AppWorld** — first adapted candidate
- **FeatureBench** — later technical expansion
- **ML-Dev-Bench** — later technical expansion
- **Terminal-Bench 2.0** — later specialist transfer benchmark

### Not priority
- **GAIA / GAIA2** for now
- **BFCL** for now
- **PIXIU** for now
- other broad or saturated lines not centered on clean skill marginal-utility measurement

The central design rule should remain:

> **Prefer datasets where the task description already implies the evaluation, so SkillX can optimize skills against a legitimate, task-intrinsic signal rather than an extra judge layer.**
