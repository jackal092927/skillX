# SkillX Minimal Authoring Format v0.1

- **Project:** `projects/multi-agent-protocol-design`
- **Date:** 2026-03-22
- **Role:** first concrete authoring proposal for the lightweight SkillX entry layer
- **Status:** exploratory format draft, optimized for low author burden and agent-assisted expansion

---

## 1. Purpose

This document proposes the **minimum viable authoring format** for SkillX.

It is intentionally not a full contract language.
It is designed to satisfy five constraints at once:

1. stay close to why current skills spread so easily,
2. keep authoring burden low,
3. make the skill machine-recognizable,
4. give agents enough declarative signal to derive stronger structure,
5. leave room for later escalation into evaluator-backed / transfer-aware / evolvable skills.

The core design bet is:

> **the author should only need to provide a small amount of declarative intent; the agent and later evaluation layers can derive the heavier structure.**

---

## 2. Design goals

### Goal A — low friction first
A normal user should be able to write a valid SkillX draft in a few minutes.

### Goal B — human-readable + LLM-readable
The format should be simple enough for both humans and agents to parse and extend.

### Goal C — structured enough to derive stronger layers
Even the lightweight format should expose enough semantics for an agent to infer:
- likely preconditions,
- allowed tools,
- out-of-scope cases,
- candidate evaluator hooks.

### Goal D — backward-compatible in spirit
SkillX should feel like an extension of today’s skills, not a foreign formal system.

### Goal E — progressive enhancement
The same skill should be able to move from lightweight to stronger maturity levels without rewrite-from-scratch.

---

## 3. Non-goals

This minimal authoring format does **not** attempt to fully specify:
- formal planning semantics,
- complete preconditions/postconditions,
- exhaustive failure taxonomy,
- benchmark contracts,
- localization packs,
- evolution/promotion rules.

Those belong to later SkillX layers.

---

## 4. Recommended file shape

The recommended minimal shape is:

1. a **small YAML metadata block** at the top,
2. followed by a **free-form markdown body**.

This balances structure and flexibility.

### Recommended skeleton

```markdown
---
skillx:
  name: short-skill-name
  purpose: one-sentence description of what this skill is for
  scope_in:
    - when this skill should be used
  scope_out:
    - when this skill should NOT be used
  requires:
    - inputs, files, tools, permissions, or assumptions needed
  preferred_tools:
    - tools/frameworks the agent should prefer if available
  risks:
    - common failure or safety risks
  examples:
    - input: short example situation
      expected_behavior: what the agent should roughly do
---

# Guidance

Free-form guidance for the agent.

# Notes for Agent

Optional extra hints, heuristics, edge cases, or style preferences.
```

This keeps the structured part small while preserving the expressive power of normal skill markdown.

---

## 5. Minimal required fields

The first version should require only **three fields**:

### 5.1 `name`
A stable human-readable identifier.

### 5.2 `purpose`
A one-sentence statement of what the skill is for.

### 5.3 `scope_in`
At least one bullet describing when the skill should be used.

These three fields are the smallest viable declarative identity.

---

## 6. Strongly recommended fields

These should not be mandatory in v0.1, but they should be strongly encouraged.

### 6.1 `scope_out`
The most valuable missing signal in many current skills is what **not** to use them for.
This field forces at least a lightweight boundary.

### 6.2 `requires`
Helps expose missing dependencies and lets the agent detect when prerequisites are absent.

### 6.3 `preferred_tools`
This is lighter than a hard `allowed_operations` contract but still useful.
It tells the agent what to reach for first.

### 6.4 `risks`
A lightweight way to surface likely failure or misuse patterns without requiring a full safety schema.

### 6.5 `examples`
Examples remain useful, but in SkillX they should be framed as **illustrative signals**, not the only definition of success.

---

## 7. Field semantics

### `scope_in`
Use for:
- triggers,
- situations,
- task categories,
- user intents,
- environmental cues.

Good examples:
- user asks to summarize a research paper into structured notes
- task involves filling a template-based offer letter
- user wants a benchmark-backed comparison of with-skill vs no-skill behavior

### `scope_out`
Use for:
- situations where the skill should abstain,
- tasks outside intended domain,
- cases where another skill is more appropriate,
- safety-sensitive or high-risk contexts.

Good examples:
- not for legal advice generation without human review
- not for destructive filesystem operations unless explicitly confirmed
- not for tasks requiring live web login to sensitive new accounts

### `requires`
Use for:
- required files,
- required tool access,
- permissions,
- assumed data availability,
- environment assumptions.

### `preferred_tools`
Use for:
- the best default tools,
- libraries or frameworks the skill expects,
- preferred execution channel.

### `risks`
Use for:
- common failure modes,
- shortcut temptations,
- likely evaluation traps,
- privacy/safety concerns,
- regression hazards.

### `examples`
Use short, high-signal examples.
Do not try to encode the whole skill through examples alone.

---

## 8. Canonical example

```markdown
---
skillx:
  name: offer-letter-template-assist
  purpose: Help fill and validate template-based offer letters with placeholders, conditional blocks, and basic consistency checks.
  scope_in:
    - user asks to generate or fill an offer letter from a template
    - task includes placeholder substitution and conditional clauses
  scope_out:
    - not for giving legal employment advice
    - not for final sign-off without human review
  requires:
    - access to the template file or template text
    - company/job details and candidate details
  preferred_tools:
    - docx/template processing tools
    - structured diff or placeholder validation tools if available
  risks:
    - missing nested placeholders
    - inconsistent dates, salary, or title across sections
    - inventing contract language that was not in the template
  examples:
    - input: Fill this offer letter template for a Senior Data Scientist in Boston starting July 1.
      expected_behavior: Extract required fields, fill placeholders, flag missing inputs, and preserve original legal structure.
---

# Guidance

Preserve the original template structure whenever possible.
If required fields are missing, ask for them or mark them explicitly instead of guessing.

# Notes for Agent

Check for repeated fields across multiple sections.
Pay extra attention to conditional clauses, compensation formatting, and signature blocks.
```

This is already more useful than a pure prose skill, while still being easy to author.

---

## 9. Agent-assisted expansion path

The minimal format is not supposed to remain the whole skill forever.
A SkillX-capable agent should be able to derive a richer second layer.

From the example above, an agent could infer:
- candidate preconditions,
- likely forbidden operations,
- expected artifacts,
- evaluator hooks,
- transfer assumptions,
- missing test cases.

### Example of derived structure (not authored manually)

```yaml
agent_derived:
  candidate_preconditions:
    - template source is available
    - key employment fields are present or explicitly marked missing
  candidate_postconditions:
    - all referenced placeholders are resolved or flagged
    - legal template text is not silently invented
  candidate_evaluator_hooks:
    - placeholder completeness check
    - cross-field consistency check
    - preserved-template-structure diff check
```

This is the intended SkillX workflow:
- **human authors the light layer**,
- **agent proposes the stronger layer**,
- **evaluation decides what survives**.

---

## 10. Authoring guidance

### Prefer concrete scope over generic claims
Bad:
- helps with documents

Better:
- helps fill template-based offer letters with placeholder substitution and consistency checks

### Write at least one explicit out-of-scope rule
This is one of the cheapest high-value additions.

### Keep examples short and realistic
Do not overload the examples section with edge-case noise.

### Prefer “risks” over fake exhaustiveness
A short honest risks list is better than pretending the skill has full guarantees.

### Avoid hidden assumptions
If a tool, permission, or file is needed, put it in `requires`.

---

## 11. How this differs from today’s skills

Compared to many existing free-form skills, this format adds lightweight declarative anchors:
- purpose,
- in-scope,
- out-of-scope,
- prerequisites,
- preferred tools,
- risks.

That is enough to make the skill more machine-derivable without forcing the author to write a heavy contract.

---

## 12. Why YAML + markdown is the current recommendation

This choice is pragmatic, not ideological.

### Advantages
- easy for humans,
- easy for LLMs,
- easy to version control,
- easy to extend later,
- works well with existing skill authoring habits.

### Why not a custom DSL yet?
Because the current project priority is adoption-friendly experimentation, not maximal formalism.
A DSL may emerge later if the experiment shows a real need.

---

## 13. Upgrade path to stronger SkillX levels

The same minimal authoring format should support progressive enhancement.

### Minimal → Contract-augmented
Add agent-derived or human-refined:
- preconditions,
- postconditions,
- forbidden operations,
- failure modes.

### Contract-augmented → Evaluator-backed
Add:
- executable checks,
- benchmark references,
- replay instructions,
- verifier metadata.

### Evaluator-backed → Transfer-aware
Add:
- model assumptions,
- tool/environment adapters,
- portability notes,
- transfer test results.

### Transfer-aware → Evolvable
Add:
- version history,
- regression gates,
- replay corpus,
- promotion/deprecation logic.

---

## 14. Anti-patterns to avoid

### Anti-pattern 1 — Overloading examples to define the whole skill
Examples are not a substitute for scope.

### Anti-pattern 2 — Hiding hard assumptions in prose
Put them in `requires`.

### Anti-pattern 3 — Writing only positive trigger language
Always try to include at least one `scope_out` item.

### Anti-pattern 4 — Pretending lightweight format gives guarantees
This layer is for intent and derivation, not formal proof.

### Anti-pattern 5 — Turning the minimal layer into a pseudo-formal monster
If the minimal layer becomes too big, SkillX fails its adoption goal.

---

## 15. Suggested first experiment

A concrete first project experiment would be:

1. take a small subset of SkillsBench skills,
2. rewrite them using this minimal SkillX format,
3. ask an agent to derive stronger contract/evaluator structure,
4. benchmark:
   - no skill,
   - original skill,
   - SkillX minimal rewrite,
   - SkillX minimal rewrite + derived contract layer,
5. compare:
   - average task performance,
   - per-task deltas,
   - negative transfer,
   - evaluator robustness,
   - authoring overhead.

This would test whether lightweight declarative augmentation is already useful before a heavier framework is introduced.

---

## 16. Bottom line

The minimal SkillX authoring format should be judged by one criterion above all:

> **Does it add enough semantic signal to improve derivation, evaluation, and reuse—without making ordinary skill authoring too annoying?**

The format proposed here is intentionally conservative.
It tries to add just enough structure to unlock better downstream tooling while staying close to the ergonomics that made current skills popular.
