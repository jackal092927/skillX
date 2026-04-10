# SkillX Baseline Collaborator Handoff v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-10
- **Role:** short execution handoff for baseline exploration
- **Status:** active handoff note

---

## 1. Mission

Run the baseline exploration in the following priority order and return results that are actually decision-useful for SkillX.

The purpose is **not** baseline rerun for its own sake.
The purpose is to answer:

1. how far current local results are from public or paper-reported numbers,
2. what each method is really optimizing and evaluating,
3. whether the method is a strong comparison target or only an adaptation reference for SkillX.

---

## 2. Priority order

### P1. Anthropic Skill Creator → SkillsBench
**Goal:** calibration baseline for present-day Claude-style auto-generated skills.

Questions to answer:
- How far is the local rerun from current public SkillsBench behavior?
- How far is it from paper- or method-reported numbers?
- What likely explains the gap?

### P2. EvoSkills with Sonnet 4.5 → same SkillsBench slice
**Goal:** strongest nearby method baseline.

Questions to answer:
- How close is the rerun to the paper result?
- What is the actual final metric?
- What signal is used inside the loop versus at final evaluation?

### P3. SKILL0 / ICRL
**Goal:** runability + SkillsBench adaptation feasibility.

Questions to answer:
- Can the code run?
- What is the native task / metric / skill object?
- How hard would it be to map onto SkillsBench?

### P4. Optional if time remains
- AutoSkill
- SkillRL
- Trace2Skill

Use these only as light scan targets unless P1-P3 are already stable.

---

## 3. Non-negotiable execution rules

### Rule A. Use one frozen SkillsBench slice for P1 and P2
Use the **same frozen 20-task slice** for:
- Anthropic Skill Creator
- EvoSkills

Do **not** describe this as “20/88”.
Use:

> **frozen 20-task slice**

Reason: SkillsBench denominators differ across public artifacts and papers. The first goal is apples-to-apples comparison, not denominator confusion.

### Rule B. Keep the substrate fixed where possible
Across P1 and P2, keep fixed if possible:
- task slice,
- harness version,
- task packaging,
- logging format,
- reporting schema.

### Rule C. Keep three score types separate
Always distinguish:
1. **public leaderboard score**
2. **paper rerun score**
3. **our local rerun score**

Do not collapse these into one number.

---

## 4. What to deliver for each baseline

Every baseline should return the same minimum packet.

### Required metadata
- method name
- code repo / commit / branch
- model used
- benchmark / task slice used
- harness / runner details
- run date

### Required quantitative results
- task-level outcomes
- aggregate result on the frozen slice
- denominator used
- cost/runtime notes if available

### Required interpretation
- what metric is actually being reported,
- what number it is being compared against,
- why any gap likely exists,
- whether the method should be treated as:
  - strong baseline,
  - secondary baseline,
  - adaptation reference only,
  - or low-priority scan.

---

## 5. Method-specific expected outputs

### Anthropic Skill Creator
Return:
- frozen-slice aggregate result,
- task-level results,
- short gap note vs public / prior reported lines,
- 3-5 representative failure cases.

### EvoSkills
Return:
- frozen-slice aggregate result,
- task-level results,
- explicit explanation of:
  - inner-loop signal,
  - verifier path,
  - final reported metric,
- short note on why it is or is not a strong SkillX comparison target.

### SKILL0 / ICRL
Return a feasibility note:
- run status: `runs` / `fails` / `partially runs`,
- native metric,
- native task type,
- mapping difficulty to SkillsBench: `low` / `medium` / `high`,
- recommendation: `pursue now` / `defer` / `reference only`.

### Optional scan methods
Return only a lightweight scan memo unless explicitly promoted.

---

## 6. Recommended sequence

1. Freeze the 20-task SkillsBench slice.
2. Write down the exact reporting template before running anything.
3. Run Anthropic Skill Creator first.
4. Run EvoSkills second on the exact same slice.
5. Treat SKILL0 / ICRL as a feasibility study before deeper adaptation.
6. Only then spend time on AutoSkill / SkillRL / Trace2Skill.

---

## 7. What matters most for SkillX

These reruns are useful only if they help clarify SkillX’s actual contribution.

The main SkillX story is still:

> **outer-loop task-class-aware specialization, assignment, and clustering value across tasks**

So baseline work should help answer:
- what strong nearby baselines already do,
- where SkillX is genuinely different,
- and whether SkillX needs more inner-loop complexity or should keep emphasizing outer-loop meaning.

---

## 8. Bottom line

> Start with the most decision-useful comparison first: calibrate current Claude-native auto-generated skills on a frozen SkillsBench slice, then run EvoSkills on that same slice, then treat SKILL0 / ICRL mainly as an adaptation-feasibility study before spending heavier effort.
