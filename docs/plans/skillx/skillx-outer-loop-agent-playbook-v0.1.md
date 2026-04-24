# SkillX Outer-Loop Agent Playbook v0.1

- **Project:** `skillX`
- **Purpose:** standard Coding Agent procedure for turning one completed inner-loop round into the next round's schema-task inputs
- **Status:** executable control-plane playbook

## 1. When To Use

Use this playbook when a previous outer-loop round has produced task x schema pair results and the next step is to prepare the following inner-loop run.

The expected input is the previous round's pair status and run reports, not a running benchmark session.

## 2. Control-Plane Contract

The outer-loop control plane is:

```text
previous task-schema pair results
  -> score matrix
  -> assignment artifacts
  -> schema evidence bundles
  -> LLM-authored schema update operations
  -> candidate prompt bank
  -> next-round SchemaTask pair materialization
```

The control plane does not run the long benchmark itself. It prepares the next materialized root that the inner-loop launcher can run.

## 3. One-Command Path

Run from the repo root or the active experiment worktree:

```bash
uv run python scripts/run_outer_loop_optimization.py
```

The default command reads the standard round-0 locations and writes:

- `experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/outer-loop-control-plane/`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/reports/outer-loop-schema-updates/`
- `experiments/skillx-skillsbench-001/results/outer-loop-round0/outer-loop-round1-candidate-rerun/`

For a deterministic dry control-plane run that avoids calling the LLM rewrite step:

```bash
uv run python scripts/run_outer_loop_optimization.py --rewrite-mode deterministic
```

For the intended LLM-authored update operation path:

```bash
uv run python scripts/run_outer_loop_optimization.py \
  --rewrite-mode llm \
  --llm-model anthropic/claude-sonnet-4-5
```

## 4. Required Environment

- `uv` works in the project.
- The previous round's `global_pair_status.json` exists.
- The previous round's run reports are discoverable under the round root.
- `skillsbench-src` exists next to the shared repo checkout, or pass `--skillsbench-root`.
- Claude Code authentication exists if `--rewrite-mode llm` uses a Claude model.

The wrapper uses authenticated CLI execution for LLM rewrite operations. It does not require API keys.

## 5. Important Outputs

Control-plane outputs:

- `score_matrix.csv`
- `score_matrix.json`
- `score_matrix_wide.csv`
- `assignments.csv`
- `assignments.json`
- `schema_training_assignments.csv`
- `diagnostics.json`
- `control_plane_bundle.json`

Schema update outputs:

- `schema_update_package.json`
- `schema_evidence_bundles.json`
- `schema_update_proposals.json`
- `round_update_plan.json`
- `challenger_eval_plan.json`
- `round1_candidate_prompt_bank.json`

Next-round materialized root:

- `manifest.json`
- `pair_specs.jsonl`
- `next_round_pair_plan.json`
- `next_round_pair_plan.csv`
- `round1_candidate_prompt_bank.json`
- `pairs/<task>__<schema>/pair_spec.json`
- `pairs/<task>__<schema>/rendered_meta_skill.md`
- `launch_next_round.sh`

The next-round materialized root is compatible with `scripts/launch_skillx_round0.py` via `--materialized-root`.

## 6. Running The Next Inner Loop

After the wrapper finishes, inspect the materialized root:

```bash
uv run python scripts/launch_skillx_round0.py \
  --materialized-root experiments/skillx-skillsbench-001/results/outer-loop-round0/outer-loop-round1-candidate-rerun \
  --list-tasks
```

Then run the selected pairs using the same launcher pattern as round 0:

```bash
uv run python scripts/launch_skillx_round0.py \
  --materialized-root experiments/skillx-skillsbench-001/results/outer-loop-round0/outer-loop-round1-candidate-rerun \
  --output-suffix round1-candidate-run
```

For long runs, use the existing tmux pattern rather than running directly in a fragile terminal.

## 7. Agent Procedure

When asked to run the outer loop, the Coding Agent should:

1. Check `git status` and confirm the intended worktree.
2. Run the wrapper with either `--rewrite-mode llm` or `--rewrite-mode deterministic`.
3. Verify the generated `outer_loop_optimization_summary.json`.
4. Verify the next materialized root has `manifest.json` and `pair_specs.jsonl`.
5. Do not launch the long inner-loop rerun unless explicitly asked.
6. Commit code changes separately from large experiment outputs when possible.

## 8. Acceptance Boundary

The generated `round1_candidate_prompt_bank.json` is a candidate bank, not an accepted incumbent bank.

Acceptance requires a follow-up inner-loop rerun and a comparison against the previous round. Only after that comparison should a candidate schema be promoted to the next incumbent prompt bank.

## 9. Why This Is A Playbook, Not A Skill Yet

This workflow is project-specific and still evolving. A playbook plus CLI wrapper keeps the behavior explicit, testable, and easy to revise.

Once the interface stabilizes across multiple outer-loop rounds, this playbook can be wrapped as a Codex skill.
