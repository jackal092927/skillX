# SkillsBench Benchmark Onboarding Note v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-10
- **Role:** onboarding memo for using SkillsBench as the primary native benchmark for SkillX
- **Status:** active benchmark entry note

---

## 1. Why SkillsBench is first

SkillsBench is the best current benchmark fit for SkillX because it already centers the main question we care about:

> how much does an external skill help on a matched task?

It is the cleanest first substrate for evaluating:
- original skill vs rewritten skill,
- skill structure quality,
- negative transfer,
- class-aware prompt/scaffold improvements,
- bounded refine gains.

This is why SkillsBench remains the primary native benchmark in the current dataset shortlist.

---

## 2. Task format

SkillsBench tasks are benchmark tasks designed around explicit task goals with a strong skill-usage framing.

For SkillX purposes, treat each evaluation unit as:

```text
(task, task_description, native_skill, verifier)
```

This is a strong match for SkillX because it lets us add:
- SkillX minimal rewrites,
- class-aware render variants,
- refined variants,
without changing the underlying task identity.

### Expected task surface
- diverse domains,
- mostly multi-step execution,
- often tool-mediated or artifact-producing,
- structured enough to support deterministic or semi-deterministic evaluation.

---

## 3. Verifier type

### Expected verifier profile
- task-level pass/fail or score output,
- benchmark-defined execution and validation logic,
- strong enough to support paired comparison across skill conditions.

### Why it is good for SkillX
The verifier is close to the task itself rather than being a free-floating external judge.
That makes it a good optimization target for skill design:
- legitimate,
- relatively stable,
- less vulnerable to pure evaluator gaming.

### SkillX implication
SkillsBench should be the reference environment for measuring:
- marginal utility,
- negative transfer,
- scope-control improvements,
- prerequisite handling,
- refinement gains that survive replay.

---

## 4. Skill attachment point

This is the main reason SkillsBench is a native benchmark.

Each task already has a natural skill attachment story.

### Native attachment modes for SkillX
1. **No skill**
2. **Original benchmark skill**
3. **SkillX minimal rewrite**
4. **SkillX rewrite plus contract/evaluator expansion**
5. **Optional refined SkillX variant**

### What this enables
We can isolate:
- format effect,
- scope effect,
- contract effect,
- refine effect,
without replacing the task itself.

---

## 5. Paired evaluation protocol

## Recommended baseline protocol

### Core conditions
- `C0` no skill
- `C1` original SkillsBench skill
- `C2` SkillX minimal rewrite
- `C3` SkillX rewrite plus agent-derived expansion
- `C4` optional bounded refined variant

### Minimum viable comparison
For a first pass, run:
- `C0`
- `C1`
- `C2`

### What to compare
- task success / pass rate,
- failure mode distribution,
- negative transfer cases,
- token or execution cost when relevant,
- revision efficiency when using refine loops.

### Replay discipline
Use fresh-context replay and avoid carrying hidden state across variants.

---

## 6. Adapter complexity

**Assessment:** low to medium

### Why relatively low
- The benchmark question already matches the SkillX question.
- Existing local docs and experiment plans already assume SkillsBench as the main substrate.
- Current taxonomy, prompt-bank, and rewrite work were all built around SkillsBench tasks.

### Main integration burden
- stable runner setup,
- variant injection plumbing,
- artifact logging,
- making sure refined or rewritten skills are inserted cleanly without accidental benchmark leakage.

### Practical conclusion
SkillsBench is the benchmark where SkillX should do the least conceptual adaptation and the most actual measurement.

---

## 7. Likely task-class coverage

SkillsBench appears to cover a good spread of the task classes we already use in SkillX planning, including:
- artifact generation,
- analytic pipeline,
- engineering composition,
- retrieval-heavy synthesis,
- environment control,
- methodology-heavy guardrail,
- orchestration/delegation.

This makes it unusually useful for:
- prompt-bank clustering,
- assignment-matrix experiments,
- class-aware outer-loop optimization.

---

## 8. Main risks

1. **Overfitting to benchmark-native patterns**
   - SkillX artifacts may improve SkillsBench specifically without generalizing.

2. **Apparent gains from formatting rather than robust skill design**
   - Must check whether gains survive multiple tasks and fresh replay.

3. **Task-local exploit behavior**
   - Stronger logging and review lanes are needed for suspicious gains.

4. **False confidence from average lift**
   - Conditional utility matters more than one global mean.

---

## 9. Recommended use in the SkillX roadmap

### Current role
- **Primary native benchmark**
- first proof substrate
- first prompt-bank and rewrite substrate
- first negative-transfer substrate

### What should be frozen first
- selected benchmark slice,
- injection contract,
- logging schema,
- replay discipline,
- comparison conditions.

---

## 10. Operational next step

1. Freeze the first SkillsBench task slice.
2. Map each chosen task to current SkillX task classes.
3. Run `C0/C1/C2` first.
4. Add `C3` only after the minimal rewrite lane is stable.
5. Use SkillsBench as the anchor benchmark before expanding into other datasets.

---

## 11. Bottom line

> SkillsBench is the cleanest first native benchmark because it already measures the thing SkillX most wants to optimize: the marginal utility of external skills on matched tasks under task-intrinsic evaluation.
