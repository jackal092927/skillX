# Class-Aware C2 Bundle Notes — energy-ac-optimal-power-flow

## Task-Class Alignment
- Task class: `analytic-pipeline-bundle`
- Topology preserved: three-skill staged bundle
- C2 posture: stronger stage contracts + deterministic checks, without adding C3-style heavy derived layers

## Stage Graph (Preserved)
1. `power-flow-data`
   - own parsing + index mapping + unit boundary responsibilities
   - artifact out: `network_parsed`
2. `ac-branch-pi-model`
   - own exact branch physics + bidirectional thermal logic
   - artifact out: `branch_flow_state`
3. `casadi-ipopt-nlp`
   - own nonlinear formulation/solve + report emission
   - artifact out: `opf_solution_state` and final `report.json`

## Class-Aware C2 Upgrades Applied
- Added explicit **Input Artifact / Output Artifact / Handoff Rule** sections per stage.
- Tightened stage-local **scope_out** boundaries to reduce stage leakage.
- Added deterministic **pre-handoff checks** in each skill:
  - parser structure/index/unit checks
  - branch-equation and thermal-direction checks
  - solver residual/bound/schema checks
- Emphasized scientific-workflow constraints from rewrite notes:
  - no DC substitution
  - strict unit/sign discipline
  - no optimistic report on failed/infeasible solve

## Deterministic Validation Posture
- Validation is staged, not only end-of-pipeline.
- Any contract breach is treated as a stage failure, not deferred.
- Final report validity depends on both:
  1) schema completeness
  2) solver-backed physical feasibility consistency

## Intended Effect
- Reduce silent technical errors (bus mapping, TAP/SHIFT handling, unit mismatch).
- Improve evaluator compatibility through explicit artifact contracts.
- Keep guidance distributed across stages, avoiding monolithic bundle bloat.