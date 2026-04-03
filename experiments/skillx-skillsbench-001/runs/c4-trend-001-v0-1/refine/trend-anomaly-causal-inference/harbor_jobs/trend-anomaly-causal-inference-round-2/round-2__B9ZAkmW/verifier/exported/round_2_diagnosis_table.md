# Round 2 Diagnosis Table

| Issue | Evidence | Suspected Cause | Edit Target | Confidence |
|-------|----------|-----------------|-------------|------------|
| Negative transfer from C2→C3 | C2: 0.9, C3: 0.7944 (Δ=-0.1056) | Derived Execution Layer adds over-prescriptive, potentially misleading constraints | All skills: Derived Execution Layer sections | High |
| Over-specification in postconditions | Derived layer contains exact row counts, percentile bounds, specific column names | Hallucinated requirements not grounded in actual task variability | data_cleaning: Postconditions section | High |
| Verbose failure mode lists | 9-10 failure modes per skill create cognitive load without clear prioritization | Undifferentiated failure warnings dilute critical guidance | All skills: High-Impact Failure Modes sections | Medium |
| Execution Notes redundancy | Execution Notes repeat Guidance content with less structure | Derived layer expanded without adding unique value | All skills: Execution Notes sections | Medium |
| Missing abstention boundaries | Skills don't explicitly warn against over-application | Lack of clear "when NOT to apply" guidance | All skills: scope_out, risks | Medium |
| Evaluator hooks speculation | Detailed P0/P1/P2 hook specifications not validated against actual tests | Derived layer invented test requirements without evidence | data_cleaning: Evaluator Hooks section | High |

## Primary Diagnosis

**Root cause**: The agent-derived expansion (C2→C3) added extensive "execution layer" guidance that increased cognitive load, introduced unsupported constraints, and potentially misled execution. The derived sections appear to be speculative elaborations rather than evidence-grounded refinements.

**Refine strategy for R2**: Compress and simplify the Derived Execution Layer across all skills. Remove speculative requirements, reduce list bloat, focus on high-signal guidance only.
