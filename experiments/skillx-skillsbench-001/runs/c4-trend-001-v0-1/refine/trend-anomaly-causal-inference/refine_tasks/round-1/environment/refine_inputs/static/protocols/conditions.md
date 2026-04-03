# Conditions — SkillX SkillsBench Experiment 001

## Condition definitions

### C0 — No Skill
- benchmark baseline
- no skill package available

### C1 — Original Skill
- task runs with the original SkillsBench skill set exactly as shipped

### C2 — SkillX Minimal Rewrite
- original skill(s) rewritten into the SkillX minimal authoring format
- preserve original task intent
- only add lightweight declarative structure

### C3 — SkillX Minimal Rewrite + Agent-Derived Expansion
- same as C2, plus a derived layer with candidate:
  - preconditions
  - forbidden operations / risks
  - failure modes
  - evaluator hooks
  - scope clarifications

### Optional C4 — Bounded Multi-Round Refine
- only after rewrite-only evidence exists
- start from `C3`
- run a bounded **multi-round refine loop** on the tune split
- keep the refine protocol frozen during the loop
- select a final `C4` candidate after the bounded loop ends
- evaluate only the final `C4` candidate on held-out tasks

## Comparison logic

- `C1 vs C0` → does the original skill help?
- `C2 vs C1` → does lightweight SkillX restructuring help?
- `C3 vs C2` → does agent-derived structure help beyond metadata?
- `C4 vs C3` → does bounded **multi-round** refine help without overfitting?

## Evaluation stance

Primary outcome lane:
- benchmark deterministic verifier

Secondary audit lane:
- fresh-context or independent review on a smaller subset

Protected-task logic:
- negative-transfer cases must be explicitly recorded, not hidden by averages


Secondary audit lane:
- fresh-context or independent review on a smaller subset

Protected-task logic:
- negative-transfer cases must be explicitly recorded, not hidden by averages
