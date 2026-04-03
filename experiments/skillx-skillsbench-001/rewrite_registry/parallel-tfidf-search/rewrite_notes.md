# Rewrite Notes — parallel-tfidf-search

## Why this task is in the dry run
- multi-skill bundle case
- medium-difficulty engineering task
- good test of whether SkillX can clarify overlapping skill roles instead of only rewriting single-skill prompts

## Rewrite strategy
- preserve the existing three-skill structure rather than merging everything into one monolith
- make each skill’s role narrower and more legible:
  - `python-parallelization` = primary concurrency design
  - `workload-balancing` = chunking / scheduling support
  - `memory-optimization` = resource-discipline support
- add a bundle-level derived note to explain interaction and ordering

## Main SkillX additions
- sharper `scope_in` / `scope_out` boundaries for each skill
- explicit task-centered purpose statements
- clearer statement that correctness equivalence outranks superficial speed claims
- explicit interaction note for the bundle

## Expected value of the rewrite
- likely less benefit from any one field than in a simple single-skill case
- main expected gain is reduced confusion about which skill should dominate at each decision point
- this task is a useful burden test: if SkillX cannot help here, its multi-skill story is weak
