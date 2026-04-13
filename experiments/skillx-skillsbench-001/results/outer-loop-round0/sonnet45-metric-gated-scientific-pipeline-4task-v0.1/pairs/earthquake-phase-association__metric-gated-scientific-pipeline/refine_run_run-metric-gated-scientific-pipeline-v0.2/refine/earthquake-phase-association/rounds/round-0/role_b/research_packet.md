# Research Packet

- task_id: `earthquake-phase-association`
- round_index: `0`
- reward: `1.0`
- failed_tests: `None`
- dominant_failure_pattern: serial runtime config-key failures in GaMMA setup before eventual success
- staged_next_skillpack_dir: `/Users/Jackal/iWorld/projects/skillX/.worktrees/bug/issue-16-earthquake-negative-lift/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-metric-gated-scientific-pipeline-4task-v0.1/pairs/earthquake-phase-association__metric-gated-scientific-pipeline/refine_run_run-metric-gated-scientific-pipeline-v0.2/refine/earthquake-phase-association/rounds/round-0/role_b/next_skillpack`
- staged_bundle_path: `none`

## Recommended Edit Targets

- gamma-phase-associator/SKILL.md: add a compact REQUIRED_KEYS checklist for `association()` (must include `oversample_factor`, `x(km)`, `y(km)`, `z(km)`).
- gamma-phase-associator/SKILL.md: add a minimal known-good BGMM config snippet that can be copied without omissions.
- Executor guidance: after first config `KeyError`, require a full key-audit against REQUIRED_KEYS before rerun (avoid one-key-at-a-time patch loops).
