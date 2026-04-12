# SkillX Round0 Debug Memo: `run-next20x7-2026-04-11`

- source report: `run_report.json`
- source matrix: `results_table.md`
- runtime status: `runtime_status.md`
- evaluation matrices: `evaluation_matrices.md`
- run scope: `20 tasks x 7 schemas = 140 pairs`
- run outcome: `18 succeeded / 122 failed`

## Collapse Point

- First successful pair: `citation-check__artifact-generation`
- Last successful pair before collapse:
  `spring-boot-jakarta-migration__retrieval-heavy-synthesis`
- First failed pair:
  `spring-boot-jakarta-migration__environment-control`
- First failed timestamp:
  `2026-04-11T22:59:56.967704+00:00`
- Continuous failure streak after collapse: `122` pairs

## Shared Failure Signature

- The first failed pair and all downstream failed pairs share the same
  structured failure payload:
  `RuntimeError: Docker memory too low: 0 bytes < required 16000000000 bytes`
- The failure is classified as:
  - `failed_stage = environment_check`
  - `manual_intervention = false`
- The collapse started immediately after the first `18` successful pairs, then
  persisted for the rest of the batch.

## Infrastructure Evidence

- Local checks on `2026-04-12` show Docker itself unhealthy:
  - `docker info` -> Docker API `Internal Server Error`
  - `docker ps` -> Docker API `Internal Server Error`
  - `docker version` -> Docker API `Internal Server Error`, client still
    reports context `desktop-linux`
- That is consistent with the run-time `docker_mem_bytes = 0` readings in the
  failed pair artifacts.

## Interpretation

- This batch completed as a launcher run, but only the first `18` pairs are
  usable as benchmark evidence.
- The downstream `122` failed pairs should be treated as a Docker incident
  rather than as model/schema evidence.
