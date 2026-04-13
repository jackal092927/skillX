# SkillsBench Repo-Wide Docker Risk Audit v0.1

## Scope
- Generated at: `2026-04-13T07:15:58.693970+00:00`
- Task count: `87`
- Docker server: `linux` / `arm64`
- Docker MemTotal: `16748032000` bytes
- Global launcher memory gate: `16000000000` bytes

## Headline
- Any risk flag under current preflight rules: `66` / `87` tasks
- High / medium / low under current preflight rules: `0` / `12` / `54`
- Non-memory portability/build warnings: `1` task(s)
- High-confidence portability/build risks excluding memory-only reminders: `0` task(s)
- Memory-only reminders: `65` task(s)
- No current preflight risk: `21` task(s)

## Interpretation
The raw `affected_pairs_any` count is intentionally broad because it includes `high_task_memory_requirement` as a preflight reminder. That number should not be read as a prediction that all flagged tasks will fail Docker build or runtime.

The tighter portability/build interpretation is:
- confirmed current non-memory portability/build warnings: `1` task(s)
- confirmed current high-confidence portability/build risks: `0` task(s)
- these are the tasks that currently look most likely to behave differently across Docker architecture / native build environments

This export reflects the **current local workspace state**. In particular, the local `skillsbench-src` tree already contains the seismic Dockerfile fixes for `earthquake-phase-association` and `seismic-phase-picking`, so those two no longer show the previous toolchain-gap risk in this report.

## Non-Memory Portability / Build Warnings
- `glm-lake-mendota`: `medium`; Dockerfile pins linux/amd64 while Docker server arch is arm64; current Docker may rely on cross-architecture emulation. Base image: `--platform=linux/amd64 ubuntu:20.04`. memory_mb=4096

## Memory-Only Reminders (>= 8192 MB)
- `fix-druid-loophole-cve`: memory_mb=24576
- `taxonomy-tree-merge`: memory_mb=16384
- `latex-formula-extraction`: memory_mb=10240
- `quantum-numerical-simulation`: memory_mb=10240
- `earthquake-phase-association`: memory_mb=8192
- `energy-ac-optimal-power-flow`: memory_mb=8192
- `protein-expression-analysis`: memory_mb=8192
- `speaker-diarization-subtitles`: memory_mb=8192
- `syzkaller-ppdev-syzlang`: memory_mb=8192
- `trend-anomaly-causal-inference`: memory_mb=8192
- `video-tutorial-indexer`: memory_mb=8192
- `3d-scan-calc`: memory_mb=4096
- `court-form-filling`: memory_mb=4096
- `crystallographic-wyckoff-position-analysis`: memory_mb=4096
- `data-to-d3`: memory_mb=4096
- `dialogue-parser`: memory_mb=4096
- `dynamic-object-aware-egomotion`: memory_mb=4096
- `earthquake-plate-calculation`: memory_mb=4096
- `econ-detrending-correlation`: memory_mb=4096
- `energy-market-pricing`: memory_mb=4096

## Notes
- `high_task_memory_requirement` is a resource signal, not direct evidence of a Docker portability bug.
- `glm-lake-mendota` is architecture-sensitive because it pins `linux/amd64`, but a real local `docker build` and container smoke test now pass on the current `arm64` Docker Desktop via emulation, so it is tracked as a medium warning rather than a high-confidence failure risk.
- `earthquake-plate-calculation` was previously flagged heuristically, but a real `docker build` now passes on the current machine, so it is no longer treated as a portability/build warning.

## Artifact
- Full JSON audit: `/Users/Jackal/iWorld/projects/skillX/.worktrees/bug/issue-16-earthquake-negative-lift/experiments/skillx-skillsbench-001/results/infra-audits/repo-wide-docker-risk-audit-2026-04-13.json`
