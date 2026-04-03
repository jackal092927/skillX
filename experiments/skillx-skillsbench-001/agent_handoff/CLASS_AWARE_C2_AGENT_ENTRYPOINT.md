# Class-Aware C2 Remote Agent Entrypoint

**Audience:** a remote coding agent executing the first direct class-aware comparison pilot  
**Experiment:** `experiments/skillx-skillsbench-001`  
**Immediate target:** `class-aware-c2-comparison-pilot-001`

Treat all paths below as repo-root relative.

## Mission

Run the first direct comparison between:
- `C0` — no skill
- `C1` — original skill
- `C2` — generic SkillX minimal rewrite
- `C2A` — class-aware SkillX minimal rewrite

Use the four frozen representative tasks:
1. `offer-letter-generator`
2. `parallel-tfidf-search`
3. `trend-anomaly-causal-inference`
4. `taxonomy-tree-merge`

The purpose is not leaderboard chasing.
The purpose is to test whether the new class-aware `C2A` condition is:
- cleanly injectable,
- structurally distinct from generic `C2`,
- and benchmark-informative enough to justify the next step.

## Required reading order

1. `experiments/skillx-skillsbench-001/agent_handoff/CLASS_AWARE_C2_AGENT_ENTRYPOINT.md`
2. `experiments/skillx-skillsbench-001/CLASS_AWARE_C2_COMPARISON_PROTOCOL.md`
3. `experiments/skillx-skillsbench-001/agent_handoff/CLASS_AWARE_C2_REMOTE_EXECUTION_PLAYBOOK.md`
4. `experiments/skillx-skillsbench-001/runs/class-aware-c2-comparison-pilot-001/RUN_BRIEF.md`
5. `experiments/skillx-skillsbench-001/conditions.md`
6. `experiments/skillx-skillsbench-001/README.md`

## Execution stance

- Use one fixed benchmark agent/model combo across all conditions.
- Keep the benchmark runtime as boring and stable as possible.
- Do not improvise new conditions.
- Do not mix in `C3` or `C4` during this pilot.

## Definition of done

The pilot is complete only if the run folder contains:
- environment notes
- execution log
- raw logs per condition-task pair
- structured result matrix / JSON
- short written conclusion about whether `C2A` looks worth keeping
