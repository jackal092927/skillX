# SkillX Round0 Debug Memo: `run-remaining-17x7-2026-04-11-v2`

- source report: `run_report.json`
- source matrix: `results_table.md`
- runtime status: `runtime_status.md`
- evaluation matrices: `evaluation_matrices.md`
- run scope: `17 tasks x 7 schemas = 119 pairs`
- run outcome: `17 succeeded / 102 failed`

## Collapse Point

- First successful pair: `pdf-excel-diff__artifact-generation`
- Last successful pair before collapse:
  `syzkaller-ppdev-syzlang__engineering-composition`
- First failed pair:
  `syzkaller-ppdev-syzlang__retrieval-heavy-synthesis`
- First failed timestamp:
  `2026-04-11T23:06:49.349866+00:00`
- Continuous failure streak after collapse: `102` pairs

## Shared Failure Signature

- The first failed pair and the downstream failed pairs all record the same
  structured payload:
  `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- The failure is classified as:
  - `failed_stage = environment_check`
  - `manual_intervention = false`
- This means the majority of the batch did not fail inside schema-specific
  round logic; they failed before useful round execution began.

## Infrastructure Evidence

- Local checks on `2026-04-12` show Docker itself unhealthy:
  - `docker info` -> Docker API `Internal Server Error`
  - `docker ps` -> Docker API `Internal Server Error`
  - `docker version` -> Docker API `Internal Server Error`, client still
    reports context `desktop-linux`
- That evidence matches the `docker_mem_bytes = 0` failure signature seen in
  the run artifacts.

## Interpretation

- This run did finish from the launcher's perspective.
- Only the first `17` succeeded pairs should be treated as analytically usable
  task results.
- The remaining `102` failed pairs are best classified as an infrastructure
  incident, not as task- or schema-specific benchmark evidence.
