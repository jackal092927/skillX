# Rewrite Notes — trend-anomaly-causal-inference

## Why this task is in scope
- strongest current negative-transfer case under the adjusted local policy
- multi-skill bundle where ordering and boundary clarity likely matter
- useful test of whether SkillX structure can reduce vague over-guidance without changing task intent

## Rewrite strategy
- preserve the original four-skill decomposition instead of collapsing into one monolith
- narrow each skill to one stage of the pipeline:
  - `data_cleaning` = produce analysis-safe cleaned tables
  - `feature_engineering` = produce numeric DID-ready features
  - `time_series_anomaly_detection` = rank surge/slump categories using pre-March history
  - `did_causal_analysis` = estimate intensive/extensive drivers on the selected categories
- make handoff points between stages explicit so the agent does not blur preprocessing, anomaly ranking, and causal analysis

## Main SkillX additions
- explicit `scope_in` / `scope_out` for each skill
- task-centered `purpose` instead of generic library-tutorial framing
- hard emphasis on preserving IDs, date semantics, and March-vs-baseline split
- stronger warnings against leaking nonnumeric features into DID inputs
- bundle-level derived layer to describe stage ordering, failure modes, and evaluator hooks

## Expected value of the rewrite
- better sequencing and less skill overlap
- fewer malformed intermediate artifacts
- lower chance of a locally coherent but evaluator-incompatible report

