# SkillX Refine Protocol v0.1

- **Project:** `projects/multi-agent-protocol-design`
- **Date:** 2026-03-23
- **Role:** multi-round bounded refine protocol for `C4` in the SkillX / SkillsBench experiment line
- **Status:** planning draft for the first controlled refine stage

---

## 1. Why this document exists

The current SkillX experiment already defines:
- `C0` — no skill
- `C1` — original skill
- `C2` — SkillX minimal rewrite
- `C3` — SkillX minimal rewrite + agent-derived expansion
- optional later `C4` — refined variant

But `C4` was previously under-specified.

The important correction is:

> **`C4` should run as a multi-round autoresearch refine loop, but under a frozen refine protocol.**

In other words:
- the **protocol** is fixed for the duration of the experiment,
- but the **execution of that protocol** is explicitly multi-round.

This preserves both:
- the scientific interpretability of the benchmark, and
- the actual value proposition of autoresearch / self-refine / self-evolve style methods.

---

## 2. Core clarification

Two design choices were previously easy to conflate:

1. **Should the refine protocol be frozen or evolving?**
2. **Should the refine process itself be single-round or multi-round?**

These are not the same question.

### 2.1 Policy for v0.1
For the current SkillX benchmark:
- the **refine protocol should be frozen**
- the **refine execution should be multi-round by default**

### 2.2 Why this matters
If we freeze the protocol but allow multiple rounds, we still get:
- iterative diagnosis,
- accumulation of evidence,
- round-to-round skill improvement,
- and a meaningful role for memory.

But we avoid mixing in a second harder-to-interpret question:
- whether the system is also inventing a better refine protocol while it is optimizing the skill.

---

## 3. What `C4` means in v0.1

`C4` is:

> a **bounded multi-round refinement loop** that starts from `C3`, consumes tune-split evidence, and outputs a final refined skill candidate for held-out evaluation.

### 3.1 Short definition
- **starting artifact:** `C3`
- **refiner:** Pi-AutoResearch (or equivalent bounded refiner)
- **execution style:** multi-round
- **protocol status:** frozen
- **evidence source:** tune split only
- **evaluation claim:** held-out eval only

### 3.2 What `C4` is not
`C4` is **not**:
- a one-shot patch only,
- a free-form search over arbitrary new strategies,
- a benchmark-hack optimizer,
- a simultaneous search over the skill *and* the refine protocol,
- or a covert shift from “skill evaluation” to “optimizer evaluation.”

---

## 4. Role of Pi-AutoResearch in `C4`

Pi-AutoResearch is a natural fit for this stage, but its role must be explicit.

### 4.1 Allowed role
In `C4`, Pi-AutoResearch acts as a:
- **bounded multi-round skill refiner**
- **failure analyst**
- **evidence integrator**
- **iterative editor under constraints**

### 4.2 Disallowed role
In `C4`, Pi-AutoResearch does **not** act as a:
- free protocol inventor,
- open-ended benchmark search engine,
- unconstrained literature-search agent for every round,
- or refiner-of-the-refiner.

### 4.3 Why this matters
Pi-AutoResearch may still become central to the long-term contribution.
But inside the current benchmark line it should answer:

> “Can a fixed multi-round refine protocol improve a skill?”

not yet:

> “Can the system autonomously invent a better refine protocol while also optimizing the skill?”

That second question belongs to a later outer-loop study.

---

## 5. Inner loop vs outer loop

The cleanest framing is to separate two loops.

### 5.1 Inner loop — current benchmark loop
This is the loop that produces `C4`.

- **object being improved:** the skill artifact
- **protocol status:** fixed
- **execution style:** multi-round
- **question:** does bounded multi-round refine improve `C3` on held-out tasks?

### 5.2 Outer loop — later research loop
This is the loop that improves the refine protocol itself.

- **object being improved:** the refine algorithm / meta-protocol
- **protocol status:** evolving
- **question:** which refine protocol produces better refined skills with less overfitting and lower cost?

### 5.3 Policy
Do not mix inner-loop and outer-loop claims in the same benchmark result.

---

## 6. Recommended round structure

The default `C4` shape should be a bounded round sequence.

### 6.1 Round naming
- `R0` = input `C3` skill
- `R1` = first refined candidate
- `R2` = second refined candidate
- `R3` = third refined candidate
- ...
- `C4-final` = final selected refined skill after the bounded loop ends

### 6.2 Minimal recommended budget
For v0.1:
- default recommended range = **3 to 4 refine rounds total**
- enough to test real iterative behavior,
- not so many that the first study turns into unconstrained search.

### 6.3 Why multiple rounds are important
Single-round refine underuses the core value of autoresearch.
Multi-round refine allows:
- diagnosis correction,
- memory accumulation,
- refinement of earlier edits,
- and better separation between noisy first reactions and more stable later improvements.

---

## 7. Input bundle for the loop

A `C4` refiner should consume a structured **refine bundle**.

The bundle should evolve round by round, but it should stay within tune-split boundaries.

### 7.1 Required inputs
These are required to start the loop:

#### Skill ancestry
- current `C3` skill artifact
- original `C1` skill snapshot
- if available, a short `C2 -> C3` diff summary

#### Task context
- task instruction
- task metadata / category / difficulty
- known task constraints

#### Tune evidence
- per-condition benchmark result summary (`C0/C1/C2/C3` or latest relevant state)
- deterministic verifier outputs
- at least one failed or weak case
- at least one successful or near-success case for contrast
- negative-transfer note when applicable

#### Refine constraints
- allowed edit surface
- forbidden edit surface
- round budget / stopping rules
- explicit ban on held-out eval visibility

### 7.2 Strongly recommended inputs
These are not strictly required, but should usually be present:
- suspicious-success notes
- manual audit notes
- disagreement between verifier lane and review lane
- authoring burden note
- cross-task pattern memo derived only from tune split

### 7.3 Optional inputs
These may help later rounds but are not required in v0.1:
- previous refine memos from earlier experiments
- small frozen heuristic library
- a curated research note prepared in advance by humans

### 7.4 Forbidden inputs
Do **not** allow:
- held-out eval examples or traces
- hidden test details
- oracle outputs
- arbitrary open-ended internet search during the refine loop
- uncontrolled prompt history from unrelated chats

---

## 8. Per-round memory objects

Because this is multi-round, memory is not optional; it is the point.

Each round should leave durable artifacts that the next round can read.

### 8.1 Required per-round artifacts
For each round `Ri`, create:
1. `round_i_skill.md` or equivalent final artifact
2. `round_i_refine_memo.md`
3. `round_i_diff_summary.md`
4. `round_i_effect_estimate.md`
5. `round_i_risk_note.md`

### 8.2 Refine ledger
Also maintain one cumulative ledger that records:
- what changed each round
- which evidence triggered each change
- whether the change seemed helpful, neutral, or harmful on tune evidence
- whether the same kind of edit is repeating

This ledger is the minimum structured memory substrate for the loop.

---

## 9. Diagnosis categories

The refiner should diagnose failure in a structured way rather than editing arbitrarily.

Recommended diagnosis categories:

1. **Trigger too broad**
   - skill fires where it should abstain

2. **Scope unclear**
   - `scope_in` / `scope_out` boundaries are under-specified

3. **Requirements under-specified**
   - prerequisites are missing or too weak

4. **Risk statement too weak**
   - failure surfaces are known but not encoded clearly

5. **Tool guidance misaligned**
   - skill nudges toward unhelpful or harmful tools/paths

6. **Example or framing misleads**
   - examples anchor the agent toward the wrong policy

7. **Derived layer hallucination**
   - the agent-derived expansion invented unsupported claims/constraints

8. **Evaluator hooks too weak**
   - the skill lacks enough structure to support trustworthy checking

9. **Body guidance too vague / too verbose**
   - the natural-language body is either too loose to help or too bloated to use

The refiner should connect each proposed edit to one or more diagnosis classes.

---

## 10. Allowed edit surface

`C4` should only change a bounded set of skill fields/components.

### 10.1 Allowed edits
- `purpose`
- `scope_in`
- `scope_out`
- `requires`
- `preferred_tools`
- `risks`
- examples / example framing
- candidate preconditions
- candidate postconditions
- candidate failure modes
- candidate evaluator hooks
- wording changes that compress, clarify, or remove ambiguity
- deletion of clearly harmful or misleading guidance

### 10.2 Allowed structural operations
- tighten
- clarify
- compress
- reorder
- split one overloaded rule into smaller explicit rules
- remove unsupported claims
- strengthen abstention boundaries
- strengthen anti-shortcut warnings

### 10.3 Disallowed edits
- task-answer leakage
- benchmark-specific hacks
- hidden reliance on held-out tasks
- inventing capabilities not grounded in the task or original skill
- replacing the original task strategy with an unrelated new one unless explicitly justified and flagged
- importing large outside knowledge blocks per round without protocol approval

---

## 11. Multi-round refine procedure

The loop should follow a fixed sequence each round.

### Step 1 — Read current bundle state
Read:
- current skill version
- refine ledger
- tune evidence
- previous round memo(s)
- current constraints

### Step 2 — Update diagnosis table
Produce or revise a diagnosis table with:
- failure type
- evidence
- suspected cause
- edit target
- confidence

### Step 3 — Propose bounded edits
For each diagnosis item, propose edits limited to the allowed edit surface.

### Step 4 — Produce round candidate
Generate the next round skill artifact (`R1`, `R2`, ...).

### Step 5 — Write explainability memo
Write a per-round memo that states:
- what changed
- why it changed
- what evidence justified it
- what new risk it may introduce
- whether this round mainly tightened, clarified, or repaired

### Step 6 — Record lineage
Store:
- parent skill version
- evidence used
- protocol version
- round index

### Step 7 — Run tune-side check
Evaluate the round candidate only on the tune side or tune-derived evidence.
Do not peek at held-out eval tasks.

### Step 8 — Update refine ledger
Append the round outcome to the ledger before the next round begins.

---

## 12. Stopping criteria

A multi-round loop needs explicit stopping conditions.

The loop should stop when any one of the following holds:

### 12.1 Maximum round budget reached
For v0.1, this is expected to be small (for example 3–4 rounds).

### 12.2 Diminishing returns
Two consecutive rounds produce no meaningful improvement on tune evidence.

### 12.3 Harm increases
Negative transfer or suspicious-success risk gets clearly worse.

### 12.4 Complexity inflation
The skill becomes materially heavier or less adoption-friendly without commensurate gain.

### 12.5 Edit repetition
The refiner starts making the same type of edit repeatedly without new evidence.

### 12.6 Confidence collapse
The diagnosis table becomes too uncertain or too contradictory to justify another round.

---

## 13. Selecting `C4-final`

`C4-final` should not automatically mean “last round wins.”

### 13.1 Candidate pool
The final selector may compare:
- `R0` (`C3`)
- `R1`
- `R2`
- `R3`
- ...

### 13.2 Selection principle
Choose the candidate that gives the best overall tradeoff on tune evidence between:
- performance
- harm control
- reliability
- complexity / authoring burden

### 13.3 Conservative default
If later rounds do not clearly dominate, it is acceptable to choose an earlier round as `C4-final`.

This is another reason to treat the loop as bounded search rather than automatic “latest version is best.”

---

## 14. Held-out evaluation policy

Held-out evaluation stays outside the loop.

### 14.1 Hard rule
No held-out eval evidence should be visible during any refine round.

### 14.2 Evaluation moment
Only after `C4-final` is selected should the system run held-out evaluation.

### 14.3 Allowed claim
The only valid public `C4` performance claim is the held-out evaluation result of `C4-final`.

Tune improvements are useful for search and diagnosis, but not sufficient as the final claim.

---

## 15. Required outputs of a `C4` run

A proper `C4` run should create at least these artifacts:

1. **Round artifact set**
   - per-round skill versions
   - per-round memos
   - per-round diff summaries
   - per-round risk notes

2. **Refine ledger**
   - cumulative memory object across the loop

3. **Final skill artifact**
   - `C4-final`

4. **Final refine memo**
   - why this final candidate was chosen

5. **Evidence manifest**
   - what tune evidence was used across rounds

6. **Held-out evaluation report**
   - the only valid place to claim `C4` performance

---

## 16. Acceptance criteria for `C4`

A `C4` variant should only be considered promising if it shows at least one of the following on held-out tasks:

1. better pass rate than `C3`
2. lower negative transfer than `C3`
3. more reliable/stable behavior than `C3`
4. similar performance with meaningfully cleaner scope control or lower harm

And it should **not** be promoted if:
- gains appear to come from benchmark exploitation,
- held-out performance drops while tune performance rises,
- harmful cases increase,
- or the refined artifact becomes much more complex without meaningful gain.

---

## 17. Anti-overfit safeguards

### 17.1 Tune/eval separation is mandatory
Refine on tune tasks, judge on held-out eval tasks.

### 17.2 No test-peeking
Held-out eval examples must not be read during refine.

### 17.3 Fixed protocol during the run
The refine protocol itself should not mutate mid-loop.

### 17.4 Bounded round budget
The loop must stop under explicit round and risk criteria.

### 17.5 Preserve artifact comparability
Do not let `C4` become so different from `C3` that the story changes from “refined skill” to “new strategy package.”

### 17.6 Require explicit evidence mapping
Every major edit should be traceable to observed tune evidence, not free invention.

---

## 18. Interaction with evaluator policy

This refine protocol depends on the broader evaluator-policy document.

In particular:
- builder / executor / evaluator separation should remain intact
- held-out evaluation should be preserved
- negative-transfer probes remain important
- suspicious successes should be flagged, not celebrated automatically

A good refine loop is not just a score maximizer.
It is a controlled multi-round search under an anti-cheat evaluator regime.

---

## 19. Recommended file/artifact layout for future `C4` runs

Suggested pattern:

```text
experiments/skillx-skillsbench-001/
  runs/
    pilot-b/
      tune/
      eval/
      refine/
        refine_protocol_v0.1.md
        input_bundle/
          c3_skill/
          ancestry/
          task_context/
          tune_evidence/
          constraints/
        rounds/
          round-0/
          round-1/
          round-2/
          round-3/
        refine_ledger.md
        c4_final/
          SKILL.md
          final_refine_memo.md
          final_diff_summary.md
          heldout_eval_report.md
```

The exact filenames can evolve, but the core principles should remain:
- separate tune evidence from held-out eval
- keep ancestry explicit
- make round history auditable
- preserve a cumulative memory object across the loop

---

## 20. Future stage: meta-protocol search

This document does **not** answer how to optimize the refine protocol itself.
It intentionally postpones that question.

A later project may study:
- protocol variants (`v0.1`, `v0.2`, `v0.3`)
- whether external retrieval helps refine quality
- whether memory of prior refines improves outcomes
- whether Pi-AutoResearch can improve the refine algorithm itself
- whether community-shared refine operators should become first-class MARC artifacts

That later stage is important, but it should be framed as a distinct outer-loop research question.

---

## 21. Bottom line

For the current SkillX benchmark line:

> **Use Pi-AutoResearch to run a bounded multi-round refine loop over the skill, not to redesign the refine protocol inside the same experiment.**

This gives us the clean first practical answer we want:

> **Does fixed-protocol, multi-round autoresearch refine help beyond `C3`?**

Only after that answer is visible should the refine protocol itself become the next optimization target.
