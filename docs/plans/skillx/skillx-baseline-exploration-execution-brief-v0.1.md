# SkillX Baseline Exploration Execution Brief v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-10
- **Role:** collaborator-facing execution brief for near-term baseline exploration
- **Status:** active working brief

---

## 1. Purpose

This brief turns the current SkillX baseline discussion into an executable priority order.

The goal is **not** replication for its own sake.

The goal is to answer a concrete SkillX decision question:

> Which baseline methods are close enough to the current SkillX problem that rerunning them gives real calibration value, methodological clarity, or adaptation guidance?

The current priority order is:

1. **Anthropic Skill Creator** on a frozen SkillsBench slice
2. **EvoSkills** on the same frozen SkillsBench slice
3. **SKILL0 / ICRL** as a runability + adaptation study
4. **Optional scan:** AutoSkill / SkillRL / Trace2Skill

---

## 2. Main operating principle

Use reruns to answer one of three questions:

1. **Calibration**
   - How far is present-day local performance from reported public / paper numbers?

2. **Method understanding**
   - What is the real optimization loop, evaluator, and final metric used by the method?

3. **Adapter feasibility**
   - Can the method be mapped onto SkillsBench cleanly enough to be a relevant SkillX comparison target?

If a run does not answer one of those questions, it is probably not worth doing yet.

---

## 3. Frozen comparison policy

## 3.1 Use one frozen SkillsBench slice for the first two baselines

For:
- Anthropic Skill Creator
- EvoSkills

use the **same frozen 20-task SkillsBench slice**.

Do **not** describe this as “20/88” in the working protocol.
Use:

> **frozen 20-task slice**

Reason:
- SkillsBench public materials use multiple denominators across artifacts (`71`, `84`, `89` have all appeared in discussion or reporting contexts).
- A frozen slice is clearer and more reproducible.
- The first goal is apples-to-apples comparison across methods under our current environment.

## 3.2 Keep the run substrate fixed where possible

Across the first two baselines, keep fixed when possible:
- task slice,
- harness version,
- task packaging,
- logging schema,
- model naming,
- reporting format.

If something differs, record it explicitly.

---

## 4. Priority 1 — Anthropic Skill Creator on SkillsBench

## 4.1 Why this is first

This is the best **calibration baseline**.

It is the closest to:
- current Claude-native skill authoring behavior,
- the practical "auto-generated skill" question,
- and the public reference line most people will immediately compare against.

## 4.2 Main objective

Measure how current local Claude behavior compares with:
- public SkillsBench leaderboard behavior,
- and paper-reported skill-generation / skill-conditioned baselines.

## 4.3 What to run

On the frozen 20-task slice:
- generate skills using the Anthropic skill-creator style workflow,
- run the resulting skills through the SkillsBench setup,
- collect task-level results.

## 4.4 Main questions to answer

1. How far is the current local result from the public SkillsBench line?
2. How far is it from the paper-reported or previously discussed baseline line?
3. Are differences mostly due to:
   - model drift,
   - harness drift,
   - task-slice choice,
   - or workflow implementation details?

## 4.5 Expected output

Deliver a short result packet with:
- exact model used,
- exact skill-generation workflow used,
- exact task slice,
- task-level scores,
- aggregate score on the slice,
- qualitative failure cases,
- brief explanation of the gap versus public or paper-reported numbers.

---

## 5. Priority 2 — EvoSkills with Sonnet 4.5

## 5.1 Why this is second

EvoSkills is the strongest nearby **method baseline**.

It is more relevant than OPRO / APE / DSPy because it actually studies iterative skill optimization and reports results on SkillsBench.

## 5.2 Main objectives

This run should answer two separate questions.

### A. Reproduction gap
How far is present-day local EvoSkills performance from the paper-reported result?

### B. Metric / evaluator clarification
What does EvoSkills actually optimize at each stage?
Specifically:
- what dense signal does it use,
- what hidden or final evaluator does it use,
- what metric is finally reported in the paper?

## 5.3 What to run

On the same frozen 20-task slice:
- run the available EvoSkills code with **Sonnet 4.5**,
- collect task-level results,
- document the evaluator and scoring path clearly.

## 5.4 Main questions to answer

1. Does the local rerun land near the paper’s numbers or far from them?
2. Is the reported metric:
   - task pass rate,
   - surrogate-verifier score,
   - oracle pass rate,
   - or some mixture across stages?
3. What parts of the loop are essential versus optional implementation detail?
4. Which parts are actually relevant to SkillX, and which parts are mainly inner-loop machinery?

## 5.5 Expected output

Deliver a result packet with:
- exact repo / commit / config used,
- exact model used,
- frozen task slice,
- task-level results,
- aggregate result,
- clear description of inner-loop signal,
- clear description of final reported metric,
- concise explanation of why EvoSkills is or is not a strong SkillX comparison target after the rerun.

---

## 6. Priority 3 — SKILL0 / ICRL

## 6.1 Why this is third

SKILL0 / ICRL is methodologically interesting, but it is not yet the cleanest apples-to-apples SkillX baseline.

Right now it should be treated as an **adapter feasibility study**, not a first-line comparison run.

## 6.2 Main objectives

1. Get the code running.
2. Identify the native task object, evaluator, and skill object.
3. Assess how hard it would be to map the method onto SkillsBench.

## 6.3 What to do first

Before attempting a SkillsBench run, clarify:
- what the original code is optimizing,
- whether it assumes a different training/inference setting,
- whether the “skill” object is compatible with SkillX-style external skill artifacts,
- and what adapter work would be required.

## 6.4 Expected output

Deliver a feasibility note with:
- run status (`runs` / `fails` / `partially runs`),
- native metric,
- native benchmark/task type,
- mapping difficulty to SkillsBench (`low` / `medium` / `high`),
- brief recommendation: pursue now, defer, or only use as conceptual reference.

---

## 7. Priority 4 — Optional scan

Methods:
- **AutoSkill**
- **SkillRL**
- **Trace2Skill**

These should remain optional unless the first three lanes are already stable.

## 7.1 Purpose

Do not over-invest in implementation early.

Instead, use them to answer:
- are any of these closer to current SkillX than expected?
- do any contain a particularly reusable evaluation idea or skill object design?
- are any worth promoting into a later real baseline lane?

## 7.2 Expected output

A lightweight scan memo is enough:
- core method object,
- native benchmark,
- metric,
- likely relation to SkillX,
- estimated rerun / adapter cost,
- recommendation (`ignore for now` / `watch` / `promote later`).

---

## 8. Common reporting requirements

Every explored baseline should return the same minimum packet.

## 8.1 Required metadata
- method name
- code source / commit / branch
- model name
- benchmark / task slice
- harness or runner details
- date of run

## 8.2 Required quantitative results
- task-level outcomes
- aggregate score on the slice
- denominator used
- cost / token / runtime notes when available

## 8.3 Required interpretation
- what number is being compared against what number,
- whether the comparison is against:
  - public leaderboard,
  - paper rerun baseline,
  - or our own local rerun,
- what likely explains any gap,
- and whether the result changes SkillX design decisions.

## 8.4 Important discipline

Always distinguish:
1. **public benchmark score**
2. **paper-specific rerun score**
3. **our local rerun score**

Do not collapse them into one baseline number.

---

## 9. Why this priority order makes sense for SkillX

This order intentionally moves from:

1. **fast calibration on the most directly comparable Claude-native baseline**,
2. to **the strongest nearby iterative-skill method baseline**,
3. to **adjacent but less directly aligned methods**,
4. then to optional broader scan.

That sequence preserves the current SkillX thesis.

The main goal is still **not** to build the fanciest inner loop.
The main goal is to clarify the strongest comparison environment for SkillX’s actual contribution:

> **outer-loop task-class-aware specialization, assignment, and clustering value across tasks.**

---

## 10. Recommended immediate next action

1. Freeze the 20-task SkillsBench slice.
2. Write down the exact reporting template for all baseline runs.
3. Start with Anthropic Skill Creator.
4. Run EvoSkills second on the exact same slice.
5. Treat SKILL0 / ICRL as a feasibility study before committing to deeper adaptation.

---

## 11. Bottom line

> The near-term SkillX baseline plan should be: first calibrate current Claude-native auto-generated skills on a frozen SkillsBench slice, then run the strongest nearby iterative skill-optimization baseline on that same slice, then evaluate adjacent methods mainly through adapter-feasibility rather than immediate full comparison runs.
