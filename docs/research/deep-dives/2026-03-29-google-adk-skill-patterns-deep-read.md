# Google / ADK Skill Pattern Article — Deep Read Memo (2026-03-29)

- **Project:** `projects/skillX`
- **Date:** 2026-03-29
- **Role:** deep-read memo on the article circulated via Google Cloud Tech about skill content design patterns
- **Status:** first-pass analytical memo

---

## 1. What article this is

The XiaoHongShu post pointing to “Google把Skill讲透了：别再卷格式了” appears to trace back to the following article:

- **Title:** `5 Agent Skill Design Patterns Every ADK Developer Should Know`
- **Author / site:** Lavini G M (`lavinigam.com`)
- **URL:** `https://lavinigam.com/posts/adk-skill-design-patterns/`

This article was also explicitly amplified by the **Google Cloud Tech** X account in a post titled:

- `5 Agent Skill design patterns every ADK developer should know`

So the cleanest characterization is:

> this is not best read as a formal Google product-spec page, but as an ecosystem article tightly aligned with Google ADK and publicly amplified by Google Cloud Tech.

That is enough to treat it as an important reference text for the current SkillX line.

---

## 2. Core claim of the article

The article’s central claim is strong and clear:

> **The interesting problem is no longer the file format of `SKILL.md`; it is the content design problem inside the skill.**

This is the line that XiaoHongShu compressed into:

> “别再卷格式了”

The argument is:
- the outer package is becoming standardized;
- more than 30 agent tools are converging on similar skill layout ideas;
- therefore the differentiator is no longer how pretty the folder structure is;
- the differentiator is what reliable behavioral logic, templates, references, checklists, and gates are encoded inside the skill.

This is an important move because it shifts the center of gravity from:

- **skill as packaging format**

into:

- **skill as reusable cognitive protocol**

This is the deepest reason the article matters.

---

## 3. What problem the article is actually solving

The article is not mainly trying to answer:
- how to write frontmatter;
- how to name directories;
- how to arrange `references/`, `assets/`, and `scripts/`.

It is trying to answer a harder question:

> **Given a standardized skill container, how should one structure the internal logic of a skill?**

That is a much more consequential question.

The article observes that two skills can have the same outer layout but completely different internal structure and value:
- one may simply inject conventions;
- one may enforce a template;
- one may run a review checklist;
- one may interview the user before acting;
- one may enforce a sequential workflow with checkpoints.

So the article’s true contribution is a **content-design taxonomy**.

---

## 4. The five patterns, in stronger analytical terms

The article presents five practical patterns:

1. **Tool Wrapper**
2. **Generator**
3. **Reviewer**
4. **Inversion**
5. **Pipeline**

Below is the deeper reading of each pattern.

### 4.1 Tool Wrapper

At a shallow level, this sounds like “wrap a tool.”
But that is not the important part.

The real idea is:

> **package domain conventions and usage discipline as on-demand expertise.**

The point is not merely to expose a tool call.
The point is to encode:
- library conventions,
- framework best practices,
- internal API usage discipline,
- team-specific standards.

So Tool Wrapper is really a pattern for **rapid domain specialization**.

The skill does not mainly add capability.
It adds **contextual correctness**.

This is why the article emphasizes examples like FastAPI conventions.
The value is not “the agent can write APIs.”
The value is:

> the agent can write APIs *according to a stable domain-specific rule system*.

That distinction matters a lot for SkillX, because many of our strongest skills are not “do X” skills; they are “do X in the reliable way our system has learned” skills.

### 4.2 Generator

The article frames Generator as structured production from templates.

The deeper function is:

> **convert underspecified generation into stable artifact production.**

This matters because many agent failures are not “the model could not produce text.”
They are:
- omitted required fields,
- inconsistent structure,
- missing sections,
- low regularity across runs.

Generator addresses this by making the skill responsible for:
- the target artifact shape,
- the template or scaffold,
- the fill-in discipline,
- the handling of missing inputs.

So Generator is less about creativity and more about **artifact regularization**.

For SkillX purposes, this is a useful reminder that a large class of strong skills are actually “artifact contract skills.”

### 4.3 Reviewer

Reviewer is one of the most important patterns in the article.

Its key move is a clean separation between:
- **what to check**
- **how to check**

This is excellent because it turns review from improvised judgment into modular system design.

A Reviewer skill can therefore encode:
- severity buckets,
- evaluation dimensions,
- pass/fail rubrics,
- checklist files,
- structured findings outputs.

What matters here is that the article treats review not as a post-hoc vibe check, but as a reusable system asset.

This strongly aligns with one of our ongoing themes:

> reliable systems improve when evaluation structure is made explicit and portable.

For SkillX and REP, Reviewer matters because it highlights that some of the most valuable skill content is not action logic but **verification logic**.

### 4.4 Inversion

Inversion is arguably the most philosophically important pattern in the article.

Its core claim is:

> **do not let the agent begin by pretending it already has the right problem representation.**

Instead, the agent should ask questions first.

The article’s point is not merely “clarify requirements.”
It is more structural:
- the agent should gather variables before generation;
- the agent should force phase completion before proceeding;
- the agent should not guess through underspecification.

This matters because many failure cascades start with premature task instantiation.
The model starts “solving” before it has correctly represented the task.

Inversion is thus a pattern for **front-loading epistemic discipline**.

That makes it a particularly relevant pattern for:
- planning tasks,
- requirements capture,
- user-facing generation with hidden constraints,
- any setting where missing assumptions create expensive downstream errors.

It also resonates strongly with Xin’s recurring insistence on:
- hypothesis before action,
- explicit variables,
- discovering the real task shape first.

### 4.5 Pipeline

Pipeline is presented as strict sequential workflow with checkpoints.

The deeper point is:

> **some tasks require process discipline more than raw model intelligence.**

Pipeline exists for tasks where the main risk is not inability to generate content but:
- skipped stages,
- missing validation,
- invalid handoffs,
- bypassed approvals,
- premature completion claims.

So Pipeline is really a pattern for **execution governance**.

This is especially relevant to current multi-agent and orchestration work, because it treats workflow as a first-class skill concern rather than leaving it implicit in one large prompt.

For our line, Pipeline is the closest of the five patterns to the move from local skill text toward more explicit workflow objects.

---

## 5. The real synthesis across the five patterns

The article is most useful when the five patterns are not treated as a flat list.

The deeper structure is something like this:

- **Tool Wrapper** = encode domain correctness
- **Generator** = encode artifact regularity
- **Reviewer** = encode evaluation logic
- **Inversion** = encode problem-formation discipline
- **Pipeline** = encode execution-order discipline

Seen this way, the five patterns are not just categories.
They are five major ways a skill can add value:

1. by improving **domain fit**;
2. by improving **artifact shape**;
3. by improving **quality control**;
4. by improving **task understanding before action**;
5. by improving **multi-step process adherence**.

This is a much more useful reading than merely memorizing the labels.

---

## 6. What the article gets very right

### 6.1 It identifies the correct frontier
The article is right that the field is moving from format questions to content questions.
That is a meaningful maturation step.

### 6.2 It makes skill structure legible
One practical problem in skill work is that people often have good skills but poor vocabulary for describing why they are good.
This article helps create a shared language.

### 6.3 It emphasizes reusable patterns instead of one-off prompt hacks
That is important because it pushes the field toward composable design rather than ad hoc prompt folklore.

### 6.4 It implicitly values protocols, not just outputs
A strong skill is not merely one that “gets a good answer.”
It is one that makes the answer-generation process more reliable.
That is exactly the right direction.

---

## 7. What the article does *not* yet solve

This is where the memo matters for our work.
The article is strong, but it does not answer the outer-loop questions we care about most.

### 7.1 It does not really explain how these patterns evolve
The article classifies patterns, but does not tell us:
- how a system should discover which pattern is best for a task,
- how pattern choice should improve over time,
- how experience from one task should update future skills.

So it is mainly a **design taxonomy**, not an evolution framework.

### 7.2 It stays mostly at single-skill granularity
Even when Pipeline moves toward workflow logic, the article still largely treats the skill as the object.
It does not yet ask whether the real object of learning should be:
- a task-class template family,
- a protocol family,
- or a reusable meta-guidance object.

### 7.3 It does not include explicit run-level experience extraction
This is important.
The article shows what kinds of skill content exist, but not how to systematically extract reusable experience from completed runs and feed that back into redesign.

That is precisely where REP V2 enters.

### 7.4 It does not address cross-task transfer in a strong way
It implies reuse through patterns, but it does not operationalize:
- same-class transfer,
- cross-benchmark reuse,
- or abstraction of lessons across multiple tasks.

So it is still closer to **skill design wisdom** than **meta-evolution machinery**.

---

## 8. Why this article matters to SkillX specifically

This article should not be read as a competitor to SkillX.
It should be read as a useful upstream clarification.

It sharpens at least four things for us.

### 8.1 It confirms that “format optimization” is not the main game
This externally validates the move away from superficial `SKILL.md` polishing.
What matters is the internal behavioral structure.

### 8.2 It gives a better vocabulary for describing current skill families
Some of our current distinctions can likely be re-described more clearly with these pattern labels.
That does **not** mean collapsing our system into Google’s five labels.
But it does mean they may be useful descriptive handles.

### 8.3 It helps separate skill content object from outer-loop learning object
The article is about **how to structure a skill well**.
SkillX is trying to answer a different but adjacent question:

> **what should the outer loop learn from runs so that future skills or templates become better?**

That distinction becomes clearer after reading this piece.

### 8.4 It may give us a better baseline language
If we later compare our work to external systems, this article helps define a credible baseline layer:
- content-structured skill design,
- but not yet REP-style experience extraction,
- and not yet task-class-aware outer-loop evolution.

---

## 9. Best way to position this against Anthropic and our current line

A useful rough positioning is:

### Anthropic skill-creator line
- emphasis: eval-driven skill refinement infrastructure
- main question: how do we improve a skill through benchmark + review + iteration?

### Google / ADK skill-pattern line
- emphasis: content-design taxonomy for skill internals
- main question: what structural pattern should a skill use internally?

### SkillX / REP / MARC line
- emphasis: outer-loop learning object and reusable experience abstraction
- main question: what should be extracted from runs and how should it update future task-class guidance?

So:
- Anthropic gives us a **refinement baseline**;
- Google gives us a **content-structure taxonomy**;
- our line is trying to build an **evolution / abstraction framework** on top.

This makes the three lines complementary rather than redundant.

---

## 10. Most important distilled takeaway

If the article is compressed into one research-useful sentence, it is this:

> **A skill should not be thought of as a formatted prompt package, but as a portable container for reliable cognitive structure.**

That is the most valuable sentence to carry forward.

And if compressed one step further for our project:

> **Google’s article clarifies the internal design space of skills; our remaining question is how run-derived experience should select, revise, and abstract those structures across tasks.**

---

## 11. Immediate implications / recommended follow-up

### Recommendation A — treat the five patterns as a descriptive vocabulary, not a replacement ontology
Use them to annotate or interpret parts of SkillX, but do not collapse the current outer-loop framing into these five labels too early.

### Recommendation B — consider a lightweight mapping exercise
For a subset of current skills or task classes, ask:
- which of the five patterns dominates?
- which patterns are mixed?
- where do current failures correspond to missing Reviewer / Inversion / Pipeline structure?

This could be a useful analysis pass without changing the main architecture.

### Recommendation C — preserve the distinction between pattern taxonomy and evolution mechanism
Google gives a stronger answer to **what structures exist**.
We still need our own answer to:
- how structures are selected,
- how they are revised,
- and how lessons become transferable.

That should remain the center of the project.

---

## 12. Bottom line

This article is worth taking seriously.
It does **not** solve the whole SkillX problem, but it does clarify an important layer that many people are still muddy about.

Its real contribution is not the catchy list of five patterns.
Its real contribution is the stronger reframing:

> **the bottleneck in skill engineering is no longer file format; it is the design of reusable behavioral structure.**

That makes it a valuable input for our work — especially as a language and framing resource — while still leaving the main SkillX / REP / MARC research problem fully open.
