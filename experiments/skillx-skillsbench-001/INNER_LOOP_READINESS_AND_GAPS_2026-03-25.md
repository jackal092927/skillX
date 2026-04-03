# Inner-Loop Readiness and Remaining Gaps — 2026-03-25

- **Project:** `projects/multi-agent-protocol-design`
- **Experiment:** `experiments/skillx-skillsbench-001`
- **Role:** readiness memo for immediate next-step execution
- **Status:** updated after class-aware C2 docs + skillpack materialization

---

## Short answer

**Yes — for the immediate next experiment, the document stack is now basically ready.**

The main remaining gaps are no longer conceptual-documentation gaps.
They are mostly **execution-side / operational** gaps:
- remote environment health,
- fixed benchmark agent/model choice,
- and pushing the latest commits so the remote machine can pull the newest experiment state.

---

## 1. What was already ready before this pass

The repo already had the core generic SkillX inner-loop docs:

- `C2_REWRITE_PROTOCOL.md`
- `C3_REWRITE_PROTOCOL.md`
- `plans/skillx/skillx-refine-protocol-v0.1.md`
- `plans/skillx/skillx-refine-bundle-contract-v0.1.md`
- `conditions.md`
- generic remote handoff docs for the first micro-shakedown under `agent_handoff/`
- materialized generic `C2` / `C3` packs for several tasks

So the original generic inner-loop line was already documented.

---

## 2. What was missing for the new class-aware direction

Before this pass, the main gaps were:

1. **No frozen comparison protocol** for generic `C2` vs class-aware `C2A`
2. **No remote agent entrypoint** for the class-aware comparison pilot
3. **No remote execution playbook** for that comparison
4. **No run-folder scaffold** for the first class-aware pilot
5. **No materialized `C2A` skillpacks** for benchmark injection
6. Missing generic `C2` materialization for some tasks (`parallel-tfidf-search`, `taxonomy-tree-merge`)

These were the practical blockers to saying “we can directly run the next experiment.”

---

## 3. What was added in this pass

### 3.1 New protocol / handoff docs
Added:
- `CLASS_AWARE_C2_COMPARISON_PROTOCOL.md`
- `agent_handoff/CLASS_AWARE_C2_AGENT_ENTRYPOINT.md`
- `agent_handoff/CLASS_AWARE_C2_REMOTE_EXECUTION_PLAYBOOK.md`

These freeze:
- the new comparison object (`C2A`)
- the comparison matrix (`C0`, `C1`, `C2`, `C2A`)
- the first 4-task representative pilot
- the remote worker's execution stance

### 3.2 New run scaffold
Added:
- `runs/class-aware-c2-comparison-pilot-001/README.md`
- `RUN_BRIEF.md`
- `RUN_STATUS.md`
- `ENVIRONMENT_NOTES.md`
- `EXECUTION_LOG.md`
- `BLOCKERS.md`
- `RESULT_SUMMARY.md`
- `results/condition_results.json`
- `results/condition_matrix.md`
- empty `logs/` and `artifacts/` directories

### 3.3 Materialized skillpacks
Materialized `C2A` packs are now available for:
- `offer-letter-generator`
- `parallel-tfidf-search`
- `trend-anomaly-causal-inference`
- `exoplanet-detection-period`
- `energy-ac-optimal-power-flow`
- `taxonomy-tree-merge`

Also filled missing generic `C2` materialization for:
- `parallel-tfidf-search`
- `taxonomy-tree-merge`

This means the remote benchmark worker no longer has to improvise how to inject the class-aware condition.

---

## 4. What is now ready to run immediately

The following immediate next experiment is now execution-ready **on paper**:

> **class-aware-c2-comparison-pilot-001**

Frozen scope:
- tasks:
  1. `offer-letter-generator`
  2. `parallel-tfidf-search`
  3. `trend-anomaly-causal-inference`
  4. `taxonomy-tree-merge`
- conditions:
  - `C0`
  - `C1`
  - `C2`
  - `C2A`

In other words, the repo now contains the minimum documentation and skillpack structure needed to run the next clear inner-loop experiment.

---

## 5. Remaining gaps

### 5.1 External / operational gaps
These are the main real remaining blockers:

1. **Remote environment must be healthy**
   - SkillsBench repo available
   - Docker healthy
   - `uv` healthy
   - API keys present

2. **A fixed benchmark agent/model must be chosen and frozen for the pilot**
   - one combo only across all `(task, condition)` runs

3. **The latest local commits must be pushed if the remote machine will pull from GitHub**
   - otherwise the remote side will not see the newest class-aware docs and skillpacks

### 5.2 Nice-to-have but not hard blockers
These are useful but not strictly required for the immediate pilot:

1. A small manifest describing how each isolated subagent generated each `C2A` rewrite
2. A one-page reviewer checklist for quickly auditing whether `C2A` overreaches into `C3`
3. A later class-aware `C3` protocol draft
4. A later class-aware `C4` protocol addendum

These can wait until after the first comparison pilot.

---

## 6. Bottom line

If the question is:

> “Are we still missing major experiment-design documents before we can run the next inner-loop experiment?”

My answer is:

> **No. The main design/documentation gap for the next step has been closed.**

If the question is:

> “Can we press go this second without any further work?”

My answer is:

> **Almost — but the remaining blockers are now operational, not conceptual:** remote environment, fixed benchmark agent/model, and pushing the latest commits.
