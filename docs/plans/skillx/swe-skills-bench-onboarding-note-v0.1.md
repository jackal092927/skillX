# SWE-Skills-Bench Onboarding Note v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-10
- **Role:** onboarding memo for using SWE-Skills-Bench as the second native benchmark for SkillX
- **Status:** native benchmark expansion note

---

## 1. Why SWE-Skills-Bench matters

SWE-Skills-Bench is a strong second native benchmark because it asks a stricter version of the SkillX question:

> do skills actually help in real-world software engineering tasks?

That skepticism is valuable.

It makes the benchmark useful not just for showing positive gains, but for revealing:
- when skills do nothing,
- when they hurt,
- when they are mismatched to repository version or context,
- when they are too broad, too stale, or too vague.

---

## 2. Task format

SWE-Skills-Bench appears to focus on requirement-driven software engineering tasks with concrete repository or project context.

For SkillX purposes, treat each evaluation unit as:

```text
(task, repo_state, requirement, candidate_skill, acceptance_tests)
```

This is narrower than SkillsBench, but also stricter.

### Expected task surface
- repository-bound or project-bound tasks,
- implementation or modification work,
- environment-sensitive instructions,
- explicit acceptance criteria.

---

## 3. Verifier type

### Expected verifier profile
- explicit acceptance criteria,
- execution-based tests,
- repository or environment-grounded correctness checks.

### Why this is attractive for SkillX
This matches Xin’s key benchmark principle very well:
- the evaluation is not supposed to come from a separate vague judge,
- it is tightly bound to the task definition,
- and it is relatively legitimate to optimize against.

### SkillX implication
SWE-Skills-Bench can become the benchmark where we stress-test:
- scope precision,
- environment assumptions,
- dependency/version fit,
- stale guidance detection,
- contract realism.

---

## 4. Skill attachment point

SWE-Skills-Bench is still skill-native, but the attachment is more demanding than in general SkillsBench.

### Native attachment modes for SkillX
1. **No skill**
2. **Original benchmark skill**
3. **SkillX rewrite of the original skill**
4. **SkillX rewrite plus context/contract expansion**
5. **Optional refined SWE-specialized variant**

### Special caution
For SWE tasks, skill attachment must not silently assume:
- wrong library versions,
- wrong repo structure,
- wrong CI behavior,
- wrong build/test workflows.

That means SkillX skills here should probably include stronger:
- boundary statements,
- environment assumptions,
- stale-context warnings,
- preferred validation sequence.

---

## 5. Paired evaluation protocol

## Recommended protocol

### Core conditions
- `S0` no skill
- `S1` original benchmark skill
- `S2` SkillX rewrite
- `S3` SkillX rewrite plus environment-aware contract expansion
- `S4` optional refined variant if the first three are stable

### Main readouts
- acceptance pass rate,
- regression rate,
- failure mode by mismatch type,
- token or execution overhead,
- cases where a skill actively degrades performance.

### Main diagnostic categories
Track at least:
- version mismatch,
- repository mismatch,
- overbroad guidance,
- under-specified validation,
- context-window overload from excessive skill length.

---

## 6. Adapter complexity

**Assessment:** medium

### Why not low
- The tasks are more environment-sensitive.
- The benchmark likely requires tighter repo/test execution discipline.
- Skills can fail for reasons unrelated to high-level reasoning quality.

### Why still worth it
- The benchmark question is still native to SkillX.
- The evaluation is strong.
- It gives us exactly the kind of hard negative evidence that helps refine skill design.

### Practical conclusion
SWE-Skills-Bench is more operationally demanding than SkillsBench, but conceptually very aligned.

---

## 7. Likely task-class coverage

Compared with SkillsBench, SWE-Skills-Bench likely over-indexes toward:
- engineering composition,
- environment control,
- methodology-heavy guardrail,
- repository-aware debugging or implementation.

This means it is especially valuable for testing whether SkillX can specialize appropriately when:
- environment assumptions matter,
- testing workflow matters,
- wrong advice can be actively harmful.

---

## 8. Main risks

1. **Benchmark-specific environment complexity may dominate**
   - Some failures may reflect runner issues rather than skill issues.

2. **Version mismatch can look like a skill-design failure**
   - Logging must separate stale factual assumptions from poor abstraction quality.

3. **Task surface may be too narrow if overused**
   - It should not replace broader SkillsBench coverage.

4. **Long or overly specific skills can become fragile**
   - Compression and scope control are especially important here.

---

## 9. Recommended use in the SkillX roadmap

### Current role
- **Second native benchmark**
- specialist benchmark for software-engineering realism
- negative-transfer stress test
- environment-fit benchmark

### What it should validate
- whether SkillX gains survive stricter repository-grounded tasks,
- whether better boundary writing beats longer generic guidance,
- whether contract-aware skills reduce harmful interventions.

---

## 10. Operational next step

1. Select a small SWE-Skills-Bench slice with clear acceptance tests.
2. Identify the original skills and their context assumptions.
3. Design a small SkillX rewrite policy specialized for SWE environments.
4. Run `S0/S1/S2` first.
5. Add environment-aware expansion only after base comparisons are stable.

---

## 11. Bottom line

> SWE-Skills-Bench is the right second native benchmark because it keeps the skill-efficacy question intact while adding a harsher real-world SWE setting where stale, vague, or overbroad skills are exposed quickly.
