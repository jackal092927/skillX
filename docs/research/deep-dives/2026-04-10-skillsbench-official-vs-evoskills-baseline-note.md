# SkillsBench Official Leaderboard vs EvoSkills Rerun Baseline

- **Project:** `projects/skillX`
- **Date:** 2026-04-10
- **Role:** discrepancy note for interpreting external baselines correctly
- **Status:** short reference memo

---

## 1. Why this note exists

While discussing EvoSkills, a number mismatch appeared:

- the **EvoSkills paper** reports **53.5%** for human-curated skills on Claude Code + Opus 4.6;
- the **current official SkillsBench leaderboard** appears substantially lower for the same rough model/harness line.

This note records the discrepancy and the safest interpretation for SkillX.

---

## 2. Verified numbers

## 2.1 Current official SkillsBench leaderboard

On the public SkillsBench leaderboard page accessed on **2026-04-10**, the row for:

> **Claude Code (Opus 4.6)**

shows approximately:

- **No Skills:** `30.6`
- **Self-Generated:** `32.0`
- **With Skills:** `44.5`

So the current public official number for curated/pre-installed skills on that line is:

> **~44.5%**, not 53.5%.

## 2.2 Local cached official results sanity check

Our local cached official-results scrape in this repo is directionally consistent with the public site.

Aggregating the cached `official_task_results.csv` gives for:

> **Claude Code (Opus 4.6)**

- **No Skills:** `31.276`
- **Self-Generated:** `32.207`
- **With Skills:** `45.275`

This local cache is **not** the canonical public score because the current cached scrape only has visible task-level results for **71 tasks** and is missing others. But it is close enough to confirm that the public official result is in the **mid-40s**, not in the low-50s.

## 2.3 EvoSkills paper numbers

In the EvoSkills paper, the main comparison section reports on **Claude Opus 4.6 + Claude-Code**:

- **EvoSkills:** `71.1%`
- **No-skill baseline:** `30.6%`
- **Human-curated skills:** `53.5%`
- **Skill-Creator baseline:** `34.1%`
- **SkillsBench self-generated baseline:** `32.0%`

So the discrepancy is real:

> **official public with-skills ≈ 44.5%**  
> **EvoSkills rerun human-curated baseline = 53.5%**

That is a gap of about **9 percentage points**.

---

## 3. Safest interpretation

The safest reading is:

> **53.5% should not be cited as the official SkillsBench public baseline for Opus 4.6.**

Instead, it should be treated as:

> **the human-curated baseline obtained under the EvoSkills paper’s own rerun / evaluation setup.**

In other words, these two numbers are not the same object.

---

## 4. Why the numbers may differ

We should be careful here and avoid overclaiming causes we have not fully audited.

But plausible reasons include:

- **benchmark-version / task-set differences**
  - the public benchmark materials and public leaderboard framing do not appear perfectly frozen to one denominator across all artifacts;
- **coverage / denominator differences**
  - public leaderboard summaries, paper reruns, and local caches may not be using the exact same eligible task set;
- **evaluation-setup differences**
  - small changes in harness, skill pre-installation details, instruction wrapper, or rerun protocol can move skill-conditioned results materially;
- **time/version drift**
  - SkillsBench public scores can change as benchmark coverage, harness fixes, or cached traces evolve.

Until fully audited, the correct stance is:

> **treat 44.5 and 53.5 as two different baseline measurements under different setups, not as a contradiction to “resolve away” casually.**

---

## 5. What SkillX should say publicly

For clean external writing:

### If we mean the public official benchmark page
Use:

> **SkillsBench public leaderboard currently shows Claude Code (Opus 4.6) at about 44.5% with skills.**

### If we mean the EvoSkills comparison table
Use:

> **EvoSkills reports a 53.5% human-curated baseline under its own rerun setup on Claude Code + Opus 4.6.**

Do **not** collapse these into one number.

---

## 6. Why this helps SkillX framing

This discrepancy actually sharpens SkillX’s story.

Even on the official public benchmark, curated skills are useful but far from universally strong.
That means the central problem is probably **not** just “how do we build an even fancier inner-loop evolver?”

A stronger research question is:

> **why do some skills help a lot on some tasks, help little on others, and hurt on still others?**

That question points directly toward SkillX’s outer-loop thesis:

- clustering tasks by meaningful structure,
- learning which skill/schema family matches which task class,
- assigning tasks to the right schema rather than assuming one universal skill form,
- and updating schema families based on cross-task evidence.

So the main SkillX selling point should remain:

> **outer-loop specialization and assignment over task classes**,

not an arms race in ever more complicated inner-loop evolution.

EvoSkills remains a strong baseline, but mostly as:

> **a per-task skill-evolution baseline**

whereas SkillX should emphasize:

> **cross-task schema specialization and clustering as the main object of learning**.

---

## 7. Bottom line

The cleanest summary is:

> **EvoSkills’ 53.5% human-curated baseline is a paper-specific rerun baseline, whereas the current public SkillsBench leaderboard for Claude Code (Opus 4.6) is about 44.5% with skills.**

For SkillX, this strengthens the argument that the real open problem is not merely better local refinement, but better **outer-loop task-class-aware specialization**.
