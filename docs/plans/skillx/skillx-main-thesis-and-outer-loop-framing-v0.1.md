# SkillX Main Thesis and Outer-Loop Framing v0.1

- **Project:** `projects/skillX`
- **Date:** 2026-04-10
- **Role:** project and paper framing note
- **Status:** working thesis note

---

## 1. Why this note exists

As the benchmark and baseline landscape became clearer, the main SkillX question also became clearer.

The project should **not** primarily define itself as:
- another inner-loop skill evolver,
- another one-task-at-a-time refinement system,
- or another attempt to win by making local skill writing more elaborate.

Those directions may still matter, but they are not the best main story.

The stronger SkillX story is:

> **the real object of learning is the outer loop: how to cluster tasks, assign them to different schema families, and optimize those families using cross-task evidence.**

---

## 2. Main thesis

The main SkillX thesis should be:

> **Agent skills should not be treated as one universal object. Different task classes want different skill schemas, and the key learning problem is to discover, assign, and improve those schemas at the outer-loop level.**

In short:

> **SkillX is about outer-loop task-class-aware specialization.**

The clustering line matters because it turns “skill improvement” from a purely local rewrite problem into a structured cross-task learning problem.

---

## 3. What SkillX should not over-claim

SkillX should avoid centering its identity on:

### 3.1 Inner-loop sophistication as the main novelty
Even if future versions add stronger refine logic, verifier co-evolution, or more advanced search, that should be treated as supporting machinery.

### 3.2 A claim that all tasks want the same kind of skill
That would collapse away the main reason SkillX exists.

### 3.3 Pure taxonomy-for-taxonomy’s-sake
The point of clustering is not to produce a pretty ontology.
The point is to discover distinctions that matter for:
- task-skill fit,
- performance,
- transfer,
- and future assignment.

---

## 4. The outer-loop object of learning

The outer loop should be understood as learning over at least four coupled objects:

1. **schema bank**
   - a small set of category-level meta-skill / schema families
2. **assignment rule**
   - which tasks are best served by which schema family
3. **update rule**
   - how a schema family changes after seeing evidence from its assigned tasks
4. **cluster meaning**
   - what task distinction the cluster is actually capturing

This is the real research object.

The inner loop exists mainly to instantiate and test candidates under this outer-loop structure.

---

## 5. Why clustering matters in practical terms

The outer loop is only interesting if clustering has practical meaning.

For SkillX, that practical meaning is:

### 5.1 Predictive meaning
If two tasks land in the same cluster, a schema that helps one should be more likely to help the other.

### 5.2 Assignment meaning
A new task should be assignable to a schema family in a way that improves performance over a one-size-fits-all baseline.

### 5.3 Update meaning
Evidence from multiple tasks in the same cluster should produce better schema updates than treating every task independently.

### 5.4 Transfer meaning
The cluster should support reusable structure, not just post hoc labeling.

So the cluster is not merely descriptive.
It should be:

> **operationally useful for specialization, transfer, and update.**

---

## 6. Why this is stronger than an inner-loop-first story

The current benchmark evidence actually supports the outer-loop emphasis.

Official SkillsBench results suggest that even curated skills are useful but far from universally strong.
That means the open problem is not simply:

> “how do we make a stronger skill writer?”

A more important question is:

> “when does a given skill schema help, when does it fail, and how should tasks be routed to different schemas?”

This is exactly an outer-loop question.

That is why SkillX should emphasize:
- matched task-skill structure,
- schema family distinctness,
- assignment across tasks,
- and specialization from cross-task evidence.

Inner-loop evolvers may help, but they are not the core conceptual contribution.

---

## 7. Positioning relative to nearby prior work

A useful high-level contrast is:

### SkillsBench / SWE-Skills-Bench
They show that skills can help, hurt, or fail to transfer, but they do not by themselves solve the schema-assignment problem.

### Anthropic Skill Creator / one-pass self-generation lines
They focus more on generating or authoring a skill artifact for a task.

### EvoSkills
EvoSkills is a strong nearby baseline because it performs iterative per-task skill evolution with a surrogate verifier.
But its main learning object is still largely **within-task** skill improvement.

### SkillX
SkillX should emphasize a different main object:

> **cross-task schema specialization and assignment**

That is, not just “improve this task’s skill,” but:

> **learn which kinds of tasks want which kinds of skills, and update those schema families over time.**

---

## 8. Implications for benchmark choice

This framing reinforces the current benchmark principle:

> choose benchmarks that expose clear task-skill relationships under task-intrinsic evaluation.

That is why SkillsBench remains the primary substrate:
- explicit task descriptions,
- objective verifiers,
- meaningful skill-conditioned comparisons,
- and enough task diversity to support clustering / assignment questions.

Benchmark choice should therefore be driven less by benchmark brand and more by whether it supports:
- matched task-skill evaluation,
- clean attribution of help vs hurt,
- and outer-loop learning across heterogeneous tasks.

---

## 9. Implications for the paper story

A good SkillX paper should probably be framed less as:

> “we built a better skill evolver”

and more as:

> “we identify the outer-loop schema-assignment problem in agent skills, and show that task-class-aware specialization is a more meaningful object of learning than one universal skill form.”

A compact paper-story version:

1. skills are not uniformly useful,
2. the main missing variable is task-skill fit,
3. fit should be learned at the schema-family level,
4. clustering + assignment + schema update define the real outer loop,
5. SkillX is a first system built around that outer-loop object.

---

## 10. Operational consequence for current project priority

Current project priority should remain:

1. get the current end-to-end SkillX pipeline running,
2. make the schema bank / assignment / evaluation loop explicit,
3. test whether cluster-wise specialization produces meaningful gain,
4. only later decide whether stronger inner-loop evolution is worth the complexity.

So the recommended emphasis is:

> **outer-loop clarity first, inner-loop upgrades later.**

---

## 11. Bottom line

The most important SkillX claim is not that it can endlessly refine a skill inside one task.

The more important claim is:

> **SkillX treats the outer loop itself as the learning problem: discover useful task classes, assign tasks to schema families, and improve those families using cross-task evidence.**

If that claim holds, then clustering is not auxiliary bookkeeping.
It is the main source of practical and conceptual value.
