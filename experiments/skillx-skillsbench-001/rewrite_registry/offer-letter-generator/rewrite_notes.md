# Rewrite Notes — offer-letter-generator

## Why this task is in the dry run
- single-skill case
- likely positive-skill task
- clear output contract
- likely benefit from explicit scope/risk declaration with low authoring overhead

## Rewrite strategy
- preserve the original high-value technical insight: split placeholders across runs are the main failure mode
- compress the original long-form skill into a lighter structure with explicit boundaries
- move from generic tutorial style toward task-centered guidance

## Main SkillX additions
- explicit `scope_out`
- explicit `requires`
- explicit `risks`
- task-level framing around preserving template structure and avoiding invented content

## Expected value of the rewrite
- modest average performance gain is plausible
- stronger expected gain is cleaner triggering and fewer missed edge surfaces
- this task is a good test of whether SkillX can improve a skill without making it heavier
