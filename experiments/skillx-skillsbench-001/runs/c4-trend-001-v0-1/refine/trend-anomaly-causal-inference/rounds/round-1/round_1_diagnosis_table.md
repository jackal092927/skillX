# Round 1 Diagnosis Table

| Issue | Evidence | Suspected Cause | Edit Target | Confidence |
|-------|----------|----------------|-------------|------------|
| Negative transfer from C2→C3 | C2: 0.9, C3: 0.7944 (-0.1056) | Agent-derived expansion added excessive verbosity and complexity that overwhelms agent execution | All four skills: compress Derived Execution Layer, streamline guidance | High |
| Excessive skill length | data_cleaning: 307 lines (vs C1: 85), time_series_anomaly: 403 lines (vs C1: 130) | C3 expansion added 3-4x more text with redundant preconditions, postconditions, failure modes | Compress verbose sections, remove redundant guidance | High |
| Overlapping coordination logic | Both individual skills AND bundle contain detailed failure modes and stage dependencies | Dual encoding causes confusion about where orchestration logic lives | Consolidate coordination in bundle, simplify skill-level guidance | Medium |
| Over-specified evaluator hooks | Extensive P0/P1/P2 test descriptions in each skill | Creates false precision - agent may optimize for described tests rather than actual task | Remove test implementation details, keep only core requirements | Medium |
| Verbose failure mode catalogs | 9-10 detailed failure scenarios per skill with detection/prevention/mitigation | Too many hypothetical cases distract from core execution path | Keep only 3-4 highest-impact failure modes per skill | Medium |
| Redundant guidance repetition | Similar concepts repeated across purpose, scope, guidance, notes, preconditions, postconditions | Creates conflicting signals and makes it harder to find relevant guidance | Consolidate related concepts, remove repetition | Medium |
| Task-specific constraints leak into general guidance | References to specific file paths, column names, date ranges in abstract guidance sections | Reduces skill reusability and creates confusion between general pattern and specific instance | Separate task-specific constraints from general methodology | Low |
