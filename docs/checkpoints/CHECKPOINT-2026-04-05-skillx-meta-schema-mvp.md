# Checkpoint — 2026-04-05 — SkillX Meta-Schema MVP State

Project: `projects/skillX`  
Date: 2026-04-05  
Status: clean design / protocol checkpoint for current SkillX MVP line

## 1. What is frozen at this checkpoint

The current SkillX line has now been stabilized into a coherent MVP framing built around:

> **prompt-induced clustering + Meta-schema-bank outer-loop optimization under frozen Render**

At this checkpoint, the project is no longer primarily discussing loose prompt ideas.
It now has:
- a locked conceptual object model
- a frozen MVP Render layer
- a pilot manifest and pilot artifacts
- a baseline update operator
- a broader search operator
- an explicit acceptance scorecard for challenger schemas

This is therefore a legitimate stopping / handoff point.

---

## 2. Core interpretation now locked

The current MVP interpretation is:

- **Meta schema** = reusable class-level guidance object; the only primary Outer Loop optimization target in MVP
- **Render** = frozen packaging / wrapper layer; not optimized in MVP
- **Rendered Meta skill** = task-specific prompt sent to the inner loop after Render combines schema + task + current Task skill + evidence + output contract
- **Task skill** = task-specific skill artifact being edited / executed / evaluated

The most important correction preserved here is:

> the final Meta skill is task-specific
>
> the cross-task reusable object is the Meta schema, not the final rendered prompt

This resolved the earlier conceptual confusion between category label, prompt-bank entry, rendered prompt, and the skill object being edited.

---

## 3. Main architectural line

The MVP now follows this outer-loop logic:

1. maintain a small bank of category-level Meta schemas
2. keep Render frozen
3. instantiate task-specific Meta skills from each schema
4. run the inner loop (Mark Auto Research) on task × schema pairs
5. assign tasks to schemas by score
6. update or search over Meta schemas using assigned-task evidence
7. repeat

The important design shift is that:
- clustering is no longer feature-first in the primary sense
- clustering is induced by **which Meta schema works best on which task**
- sidecar task-record features remain useful, but are not the main clustering engine

---

## 4. Most important design corrections achieved

### A. Flat clustering first
The MVP no longer uses a two-level operational clustering hierarchy.
Subclusters remain analysis-only hypotheses, not runtime objects.

### B. Render frozen, not co-optimized
This sharply reduces attribution confusion.
If behavior changes, we try to explain it through Meta-schema changes first.

### C. Meta schema is semi-structured
It is not just:
- a label,
- a rubric,
- or a single free-form prompt.

It is a semi-structured meta-policy object with:
- structured slots
- plus textual realization

### D. Search-space concern explicitly acknowledged
The conservative v0.1 operator was intentionally useful for clarity, but may over-restrict search.
This concern is now formalized rather than implicit.

### E. Broader v0.2 search path exists
The project now explicitly allows a broader successor path:
- expandable semantic meta-item pools
- incumbent + challenger search
- explicit diversity-preserving pressure

So the line no longer depends on a tiny local-edit-only search space.

---

## 5. Current artifact stack

### Core framing / bank / render
- `docs/plans/skillx/skillx-prompt-bank-clustering-and-outer-loop-spec-v0.1.md`
- `docs/plans/skillx/skillx-prompt-bank-v0.1.md`
- `docs/plans/skillx/skillx-prompt-bank-v0.1.json`
- `docs/plans/skillx/skillx-prompt-rendering-and-injection-spec-v0.1.md`
- `docs/plans/skillx/skillx-render-template-frozen-v0.1.md`
- `docs/plans/skillx/skillx-prompt-rendered-examples-v0.1.md`

### Assignment / pilot / runner-facing docs
- `docs/plans/skillx/skillx-assignment-matrix-protocol-v0.1.md`
- `docs/plans/skillx/skillx-pilot-assignment-pass-v0.1.md`
- `docs/plans/skillx/skillx-pilot-round-0-manifest-v0.1.json`
- `docs/plans/skillx/skillx-pilot-task-slice-v0.1.json`
- `docs/plans/skillx/pilot-round-0-score-matrix.template.csv`
- `docs/plans/skillx/pilot-round-0-assignments.template.csv`
- `docs/plans/skillx/pilot-round-0-diagnostics.template.json`

### Meta-schema evolution docs
- `docs/plans/skillx/skillx-meta-schema-update-operator-v0.1.md`
- `docs/plans/skillx/skillx-meta-schema-search-operator-v0.2.md`
- `docs/plans/skillx/skillx-meta-schema-acceptance-scorecard-v0.1.md`
- `docs/plans/skillx/skillx-outer-loop-update-protocol-v0.1.md`

### Sidecar / task-surface / classification support
- `docs/plans/skillx/skillsbench-task-profile-annotations-v0.1.md`
- `docs/plans/skillx/skillsbench-task-cluster-inputs-v0.1.jsonl`
- `docs/plans/skillx/skillsbench-initial-classification-v0.1.md`
- `docs/plans/skillx/skillx-task-clustering-and-taxonomy-v0.1.md`
- `docs/plans/skillx/skillx-mvp-automatic-clustering-input-schema-v0.1.md`

---

## 6. Current bank and pilot scope

### Category bank
Current seed bank is still:
1. `artifact-generation`
2. `analytic-pipeline`
3. `engineering-composition`
4. `retrieval-heavy-synthesis`
5. `environment-control`
6. `methodology-guardrail`
7. `orchestration-delegation`

Most likely early merge candidate if distinctness remains weak:
- `methodology-guardrail` + `orchestration-delegation`

### Pilot stance
Current pilot assumptions remain:
- Tier 1 micro-pilot: 7 tasks × 7 schemas
- fixed Render
- `U0` universal baseline retained as non-assignable control
- assignments by score with tie-break rules for ambiguity

---

## 7. Meta-schema evolution line at this checkpoint

Two operator layers now coexist intentionally:

### v0.1 = conservative baseline
`skillx-meta-schema-update-operator-v0.1.md`
- fixed schema shape
- slot-first edits
- constrained local editing
- good for attribution and sanity

### v0.2 = broader successor search
`skillx-meta-schema-search-operator-v0.2.md`
- same high-level schema structure
- larger semantic meta-item pool
- allows pool expansion / contraction / borrowing / challenger construction
- explicitly tries to avoid trivial convergence under an overly small search space

This relationship is important:
- v0.1 should not be deleted
- v0.2 should not be treated as “just more words”
- together they give a meaningful baseline-vs-broader-search comparison

---

## 8. Acceptance logic now exists

A major gap has now been closed:

`docs/plans/skillx/skillx-meta-schema-acceptance-scorecard-v0.1.md`

This scorecard evaluates challengers along five axes:
1. assigned-task utility
2. boundary behavior
3. distinctness preservation
4. diversity contribution
5. search quality / interpretability

It also defines explicit decision outcomes:
- `accept_replace`
- `accept_branch`
- `accept_soft_merge_signal`
- `hold_incumbent`
- `reject_collapse`

This is a key checkpoint milestone because broader search without acceptance logic would be too unconstrained.

---

## 9. What is still not built yet

This checkpoint is strong on specification maturity, but some pieces are still not implemented:

### Not built yet
- an actual runnable pilot runner / execution config consuming the manifest end-to-end
- real task × schema score matrix artifacts from pilot-round-0
- real challenger serialization / comparison implementation
- a concrete decision on whether the first runnable loop uses:
  - only v0.1-style incumbent updates,
  - or v0.2-style incumbent + challenger search from the start

### Therefore
This checkpoint represents:
- **design maturity + protocol maturity**
not yet
- **empirical execution maturity**

---

## 10. Best immediate next steps after this checkpoint

If work resumes from here, the strongest next options are:

1. decide runner scope:
   - `incumbent + 1 challenger`
   - or full `incumbent + 3 challengers`
2. serialize challenger schema artifacts explicitly
3. build the first real pilot runner around:
   - frozen Render
   - pilot manifest
   - schema bank
   - score-matrix / assignment / diagnostics outputs
4. run `pilot-round-0`
5. only after the first real round, revisit whether v0.1 is too conservative in practice

---

## 11. Why this is a meaningful checkpoint

This checkpoint is valuable because the SkillX line is now no longer just:
- “some prompt bank ideas”
- or “some clustering intuition”

It is now a coherent, navigable stack with:
- a locked object model
- frozen MVP Render
- a pilot manifest
- schema update/search protocols
- and an explicit acceptance scorecard

The most important result is not empirical performance yet.
The most important result is that the project now has:
- a clean optimization target,
- a broader but still bounded search interpretation,
- and a disciplined path from design into execution.

This is a legitimate checkpoint and handoff point.
