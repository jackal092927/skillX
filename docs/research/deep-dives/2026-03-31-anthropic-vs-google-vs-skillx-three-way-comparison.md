# Anthropic vs Google vs SkillX — Three-Way Comparison Memo

- **Project:** `projects/skillX`
- **Date:** 2026-03-31
- **Role:** three-way comparison memo positioning Anthropic Skill Creator, the Google / ADK 5-pattern line, and the current SkillX / REP / MARC trajectory
- **Status:** synthesis memo for project framing

---

## 1. Why this memo exists

By this point we have three adjacent but non-identical lines on the table:

1. **Anthropic Skill Creator**
2. **Google / ADK 5-pattern skill-design line**
3. **SkillX / REP V2 / MARC**

All three care about skills.
But they are not solving the same problem.

If they are not separated carefully, discussion drifts into superficial analogies like:
- “they are all doing skill evolution,”
- “this is basically the same thing,”
- “we should just copy that framework.”

That would be a mistake.

This memo therefore aims to do three things:
- identify the real center of gravity of each line,
- show where they overlap,
- and clarify what remains distinctive about SkillX.

---

## 2. Executive summary

The cleanest high-level summary is:

- **Anthropic** is strongest on **skill refinement infrastructure**.
- **Google** is strongest on **skill-content structure taxonomy**.
- **SkillX** is trying to become strongest on **experience-informed class-aware outer-loop evolution**.

In one sentence each:

### Anthropic
> A skill is a testable artifact that should be iteratively improved through evals, benchmarks, review, and reruns.

### Google
> A skill is a standardized container whose real power comes from the internal behavioral structure encoded inside it.

### SkillX
> A run should produce reusable experience that updates class-aware skill/template guidance rather than only improving one local skill artifact.

This is the core three-way split.

---

## 3. Each line’s primary question

A useful way to distinguish the three systems is to ask:

> **What is the main question each one is trying to answer?**

### 3.1 Anthropic’s main question

> **How do we iteratively improve a specific skill so that it performs better and triggers more reliably?**

This is a refinement question.
The unit of optimization is local and concrete.

### 3.2 Google’s main question

> **How should the internal content of a skill be structured so that it behaves reliably?**

This is a design-taxonomy question.
The unit of analysis is the internal morphology of a skill.

### 3.3 SkillX’s main question

> **What reusable guidance object should be learned from completed runs so that future tasks of the same class start from better structure?**

This is an outer-loop learning question.
The unit of interest is no longer just one skill file.

This distinction alone eliminates a lot of confusion.

---

## 4. The three systems by object of optimization

### 4.1 Anthropic — local skill artifact
Anthropic primarily optimizes:
- one skill body,
- one skill description,
- one benchmark slice,
- one iteration at a time.

Even when multiple iterations are compared, the object is still a **specific skill artifact**.

### 4.2 Google — internal content pattern
Google’s article is not mainly an optimizer, but the conceptual object it highlights is:
- the dominant internal pattern of a skill,
- or the mix of patterns inside the skill.

Its object is therefore closer to:
- Tool Wrapper,
- Generator,
- Reviewer,
- Inversion,
- Pipeline,

as design forms.

### 4.3 SkillX — class-aware template family
SkillX is moving toward optimizing:
- a task-class-aware template family,
- potentially informed by repeated runs,
- with richer structure than a single local skill rewrite.

That is a larger object than either:
- one skill artifact, or
- one pattern label.

This is why SkillX should not be reduced to either Anthropic’s or Google’s framing.

---

## 5. The three systems by main evidence source

### 5.1 Anthropic — evals + benchmark + human review
Anthropic’s strongest evidence sources are:
- with-skill vs baseline runs,
- assertions / grading,
- pass rate,
- token/time metrics,
- human review,
- blind comparison,
- trigger-rate measurement for description optimization.

This is a practical and rigorous engineering stack.

### 5.2 Google — conceptual pattern clarity
Google’s line is much lighter on explicit optimization evidence.
Its main contribution is not a benchmark protocol.
Its main contribution is a **taxonomy of internal structure**.

Its evidence is therefore more like:
- exemplars,
- structural reasoning,
- pattern categories,
- design interpretation.

This makes it useful as a language resource, but not sufficient as a standalone evolution engine.

### 5.3 SkillX — cross-task comparison + run-derived experience
SkillX’s intended evidence stack is richer and more layered:
- variant comparison (`C0/C1/C2/C2A/...`),
- task-level verifier outcomes,
- failure signatures,
- eventually REP V2 run-level extraction,
- and later aggregation across tasks / classes.

This means SkillX wants to combine:
- benchmark-style evidence,
- structural pattern evidence,
- and post-run experience abstraction.

That is a broader evidence ambition than either of the external lines alone.

---

## 6. The three systems by loop topology

### 6.1 Anthropic — refine loop
The core Anthropic loop is:

> **draft -> eval -> review -> improve -> rerun**

This is a local refinement loop.
It is highly practical and grounded.

### 6.2 Google — taxonomy / design lens, not a full refine loop
Google’s article does not primarily present a closed optimization loop.
Instead, it offers a vocabulary for internal design choices.
Its shape is closer to:

> **identify the right internal structure -> encode it into the skill -> use the skill**

This is valuable, but it is not yet a full evolution loop.

### 6.3 SkillX — comparison -> extraction -> abstraction -> template update
The emerging SkillX loop is more like:

> **run / compare -> inspect outcomes -> extract reusable experience -> abstract to class-aware guidance -> test again**

This is why REP V2 matters.
It is not merely another benchmark helper.
It is an attempt to formalize the transition from:
- one completed run,
into
- reusable guidance.

That is the key outer-loop move.

---

## 7. The three systems by generalization target

### 7.1 Anthropic — stronger local skill + better triggering
Anthropic’s generalization target is practical but still local:
- make this skill work better,
- make it trigger more reliably,
- keep it resilient as models change.

### 7.2 Google — reusable internal design patterns
Google’s generalization target is:
- make skill design more legible,
- let builders choose appropriate internal structures,
- and reuse structural motifs across skills.

### 7.3 SkillX — task-class-level reusable guidance
SkillX’s generalization target is more ambitious:

> **move from local success cases to class-aware reusable guidance that transfers across tasks of similar shape.**

This is the real reason SkillX still has a distinct research claim.

---

## 8. The three systems by abstraction level

This may be the single cleanest comparison axis.

### Anthropic = optimization of a local artifact
- abstraction level: low to medium
- object: concrete skill
- question: how do we improve this?

### Google = taxonomy of local structure
- abstraction level: medium
- object: internal pattern / structural motif
- question: what kind of skill structure is this?

### SkillX = outer-loop abstraction of reusable guidance
- abstraction level: medium to high
- object: task-class-aware template family / meta-guidance candidate
- question: what should future similar tasks inherit from this run?

This makes the relationship very clear:

> Anthropic goes deep on local refinement.
> Google goes deep on structure naming.
> SkillX wants to go deep on what should be abstracted and transferred.

---

## 9. What each line gets importantly right

### 9.1 What Anthropic gets right
Anthropic gets the engineering discipline right:
- baseline comparison is explicit,
- review is not purely subjective,
- measurement is practical,
- iteration is normalized,
- triggering is treated as first-class.

SkillX should continue borrowing heavily from this line on:
- comparison discipline,
- benchmark hygiene,
- iteration artifact structure,
- blind review where helpful.

### 9.2 What Google gets right
Google gets the representational framing right:
- format is not the frontier,
- internal skill structure matters,
- different skills embody different behavioral patterns,
- structural vocabulary is valuable.

SkillX should borrow from this line on:
- better language for internal content design,
- pattern-level diagnosis,
- distinguishing skill morphology from packaging.

### 9.3 What SkillX is trying to get right
SkillX is trying to solve a harder bridge problem:
- how local run evidence becomes reusable experience,
- how reusable experience becomes class-aware guidance,
- and how that guidance can improve future tasks before full local re-optimization.

That is the distinctive ambition.

---

## 10. Where SkillX should be careful not to collapse

### 10.1 Do not collapse into Anthropic
If SkillX collapses into Anthropic, it becomes:
- strong local iterative refinement,
- but loses the richer outer-loop object,
- and REP V2 shrinks into a benchmark-adjacent helper.

That would be too narrow.

### 10.2 Do not collapse into Google
If SkillX collapses into Google, it becomes:
- a pattern taxonomy / annotation system,
- but loses explicit learning dynamics,
- and the project risks becoming descriptive rather than evolutionary.

That would also be too narrow.

### 10.3 Proper synthesis instead of collapse
The right move is:
- borrow Anthropic’s **evaluation and iteration discipline**,
- borrow Google’s **structure vocabulary**,
- preserve SkillX’s own focus on **experience extraction and class-aware outer-loop learning**.

That is the productive synthesis.

---

## 11. A useful layered mental model

A practical way to think about the three systems together is as three stacked layers.

### Layer 1 — Google: structure vocabulary
Google tells us:

> what internal structural ingredients a skill may be made of.

Examples:
- Tool Wrapper,
- Generator,
- Reviewer,
- Inversion,
- Pipeline.

### Layer 2 — Anthropic: local optimization loop
Anthropic tells us:

> how to locally test, compare, and refine a skill artifact.

Examples:
- skill vs no-skill,
- iteration folders,
- metrics,
- blind comparison,
- trigger optimization.

### Layer 3 — SkillX / REP / MARC: abstraction and transfer loop
SkillX wants to answer:

> after local optimization episodes occur, what reusable guidance should survive and transfer to future tasks of the same class?

Examples:
- task-class template families,
- REP V2 extraction,
- class-aware outer-loop update,
- community-scale accumulation under MARC.

This stacked view is probably the cleanest synthesis available right now.

---

## 12. Concrete comparison table

| Axis | Anthropic | Google / ADK 5-pattern line | SkillX / REP / MARC |
|---|---|---|---|
| Primary question | How to improve a skill? | How should a skill be internally structured? | What reusable guidance should runs produce? |
| Main object | local skill artifact | internal pattern / morphology | task-class template family / outer-loop guidance |
| Main contribution | eval-driven refine workflow | content-design taxonomy | experience-informed abstraction framework |
| Main evidence | benchmark + review + trigger eval | structural exemplars and pattern lens | comparison results + verifier signal + REP extraction |
| Loop shape | draft -> eval -> review -> improve | structure selection / design lens | compare -> extract -> abstract -> update |
| Generalization target | stronger local skill | reusable design vocabulary | cross-task class-aware transfer |
| Strongest borrowed idea | baseline + iteration discipline | pattern vocabulary for skill internals | not borrowed; this is the project’s own center |
| Main limitation | stays mostly local | lacks explicit evolution loop | still being operationalized |

---

## 13. What this means for project positioning

If someone asks, “What are we doing that is not just Anthropic or Google?”, the best short answer is:

> **Anthropic gives the local refine loop, Google gives the internal structure vocabulary, and SkillX is trying to learn what reusable class-aware guidance should survive across runs and tasks.**

If someone asks, “What should we borrow?”, the best answer is:

> **borrow Anthropic’s benchmarking discipline and Google’s structural language, but keep the SkillX outer-loop object distinct.**

If someone asks, “Where is the core research claim?”, the answer is:

> **the move from local outcomes to reusable experience to class-aware guidance remains the distinctive claim.**

---

## 14. Recommended next framing for future docs

Future project docs should probably keep these three labels explicit:

- **Anthropic = refine baseline**
- **Google = structure taxonomy**
- **SkillX = outer-loop abstraction framework**

This would make later memos much easier to read and would reduce repeated conceptual drift.

---

## 15. Bottom line

Anthropic, Google, and SkillX are adjacent but non-equivalent.

- Anthropic is best understood as the strongest current **practical refinement baseline**.
- Google is best understood as the clearest current **skill-structure taxonomy**.
- SkillX remains distinct to the extent that it can turn **run-derived evidence into reusable class-aware guidance** rather than merely improving one skill or naming one structure.

The right synthesis is therefore not replacement, but layering:

> **Google supplies the language of structure. Anthropic supplies the discipline of local refinement. SkillX must supply the mechanism of abstraction and transfer.**
