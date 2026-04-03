# Rewrite Notes — energy-ac-optimal-power-flow

## Why this task is in scope
- paper-cited negative example
- still within the rewrite set even though the original local replay was polluted by a no-skills timeout
- good test of whether SkillX structure can help a technically dense multi-skill optimization task

## Rewrite strategy
- preserve the original three-skill bundle
- give each skill a narrower ownership boundary:
  - `power-flow-data` = parse and map MATPOWER-style inputs safely
  - `ac-branch-pi-model` = exact branch-flow and loading equations
  - `casadi-ipopt-nlp` = formulate and solve the nonlinear AC OPF
- bias the rewrite toward evaluator compatibility: exact report schema, unit discipline, and feasibility constraints

## Main SkillX additions
- task-centered purpose statements instead of generic references
- explicit warnings against DC approximations, unit/sign mistakes, and report-schema drift
- bundle-level derived layer around feasibility, branch limits, and solver-status reporting

## Expected value of the rewrite
- clearer separation between parsing, physics equations, and optimization
- fewer silent sign/unit mistakes
- better chance of producing a complete feasible `report.json` rather than a partial optimization attempt

