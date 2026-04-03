# Rewrite Notes — taxonomy-tree-merge

## Why this task is in the dry run
- likely negative-transfer or over-guidance case
- hard task with complex methodology-heavy original skill
- useful for testing whether SkillX can improve *control* rather than only raw capability

## Rewrite strategy
- preserve the core pipeline idea: normalize → embed/weight → cluster recursively → name → export
- reduce the sense that every detailed implementation choice is mandatory
- make structural constraints, risks, and scope boundaries more explicit

## Main SkillX additions
- explicit separation between what is essential to the task and what is one recommended methodology
- stronger `risks` section around brittleness, naming overlap, source imbalance, and runtime heaviness
- task-centered framing that emphasizes satisfying the benchmark contract over copying a heavy reference pipeline verbatim

## Expected value of the rewrite
- the most plausible gain is reduced harm, not necessarily higher average score
- if SkillX works here, it suggests the framework can help when original skills are too dense or over-prescriptive
- if SkillX fails here, it may mean hard methodology-heavy tasks need a stronger contract layer than the minimal format provides
