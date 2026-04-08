# Round-0 Materializer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal round-0 outer-loop materializer that expands a task slice and schema bank into concrete `(task, schema)` pair specs and refine commands.

**Architecture:** Add one standalone script that reads the existing slice, prompt bank, task inventory, official baseline cache, and SkillsBench task files. The script writes a machine-readable manifest, per-pair rendered meta skills, and a launch script that delegates actual execution to the existing refine benchmark runner.

**Tech Stack:** Python 3.12, existing `src/skillx/io_utils.py`, `unittest`

---

### Task 1: Lock the Materializer Contract

**Files:**
- Create: `tests/test_materialize_skillx_round0_runner.py`
- Create: `scripts/materialize_skillx_round0_runner.py`

- [x] **Step 1: Write the failing test**

```python
def test_build_pair_specs_expands_task_schema_matrix(self) -> None:
    result = module.build_round0_materialization(...)
    assert result["manifest"]["pair_count"] == 4
```

- [x] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=tests:src python3.12 -m unittest tests.test_materialize_skillx_round0_runner`
Expected: FAIL because `scripts/materialize_skillx_round0_runner.py` does not exist yet.

- [x] **Step 3: Write minimal implementation**

```python
def build_round0_materialization(...):
    ...
    return {"manifest": manifest, "pair_specs": pair_specs}
```

- [x] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=tests:src python3.12 -m unittest tests.test_materialize_skillx_round0_runner`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_materialize_skillx_round0_runner.py scripts/materialize_skillx_round0_runner.py docs/superpowers/plans/2026-04-08-round0-materializer.md
git commit -m "feat(skillx): add round0 materializer"
```

### Task 2: Materialize the Real 20-task Slice

**Files:**
- Modify: `experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2/**`

- [ ] **Step 1: Run the materializer on the real inputs**

```bash
python3.12 scripts/materialize_skillx_round0_runner.py \
  --skillsbench-root ../skillsbench-src \
  --task-slice experiments/skillx-skillsbench-001/results/official-task-results/sonnet45-round0-candidate-slice-v0.2.json \
  --prompt-bank docs/plans/skillx/skillx-prompt-bank-v0.1.json \
  --inventory docs/plans/skillx/skillsbench-task-cluster-inputs-v0.1.jsonl \
  --official-results experiments/skillx-skillsbench-001/results/official-task-results/official_task_results.jsonl \
  --render-template docs/plans/skillx/skillx-render-template-frozen-v0.1.md \
  --output-dir experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2 \
  --run-id sonnet45-slice20-v0.2 \
  --oauth-file /Users/Jackal/.claude/claude-code-oauth-token \
  --round-budget 3
```

- [ ] **Step 2: Verify the materialized outputs**

Run: `python3.12 - <<'PY' ...`
Expected: `task_count == 20`, `schema_count == 7`, `pair_count == 140`

- [ ] **Step 3: Commit**

```bash
git add experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-slice20-v0.2
git commit -m "data(skillx): materialize round0 pair specs"
```
