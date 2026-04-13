# Research Packet

- task_id: `earthquake-phase-association`
- round_index: `1`
- reward: `1.0`
- failed_tests: `None`
- dominant_failure_pattern: recoverable runtime API mismatch followed by metric-blind completion (format checks without quality gating)
- staged_next_skillpack_dir: `/Users/Jackal/iWorld/projects/skillX/.worktrees/bug/issue-16-earthquake-negative-lift/experiments/skillx-skillsbench-001/results/outer-loop-round0/sonnet45-metric-gated-scientific-pipeline-4task-v0.1/pairs/earthquake-phase-association__metric-gated-scientific-pipeline/refine_run_run-metric-gated-scientific-pipeline-v0.2/refine/earthquake-phase-association/rounds/round-1/role_b/next_skillpack`
- staged_bundle_path: `none`

## Recommended Edit Targets

- seisbench-model-api/SKILL.md: add a canonical `classify_output = model.classify(...); picks = classify_output.picks` snippet and warn that `ClassifyOutput` is not list-like.
- metric-gated-scientific-pipeline skill: require a quality gate after first successful run (evaluator or explicit precision proxy), not only schema/time checks.
- earthquake-phase-association guidance: add a post-association sanity checklist (event-count and picks-per-event bounds) and require one retune pass when out of range.
