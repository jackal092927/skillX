# Round 2 Refine Memo

## What Changed

Round 2 implements a **compression and simplification strategy** across all four skills in the skillpack. The primary intervention targets the "Derived Execution Layer" sections that were added during the C2→C3 expansion.

### Changes by Skill

**All Skills (Cross-cutting)**:
- Compressed Derived Execution Layer sections by 40-60%
- Reduced High-Impact Failure Modes from 7-10 items to 5-6 most critical
- Removed redundant "Notes for Agent" sections
- Simplified postconditions to focus on essential requirements only
- Eliminated speculative constraints (e.g., exact row counts, percentile bounds)

**data_cleaning**:
- Removed extensive Evaluator Hooks section (10 P0/P1/P2 items) - unvalidated test specifications
- Compressed Postconditions from 10 detailed items to 5 essential checks
- Simplified Failure Modes from 9 to 5
- Removed redundant validation prose

**feature_engineering**:
- Streamlined guidance without changing core decision framework
- Kept critical "ALL features must be numeric" emphasis
- Simplified failure modes from 5 to 5 (already concise)

**time_series_anomaly_detection**:
- Compressed Execution Notes from verbose to essential
- Maintained critical Prophet parameters and anomaly index formula
- Simplified failure mode descriptions

**did_causal_analysis**:
- Preserved complex intensive/extensive margin distinction (critical for correctness)
- Compressed verification steps and common mistakes
- Maintained regression methodology (cannot simplify without losing correctness)

## Why It Changed

**Evidence**: Negative transfer from C2→C3 (Δ = -0.1056). C2 (minimal) achieved 0.9 reward, while C3 (derived expansion) dropped to 0.7944.

**Root Cause Hypothesis**: The agent-derived expansion added verbose, over-prescriptive guidance that:
1. Increased cognitive load for executor agents
2. Introduced noise through speculative requirements
3. Created false constraints that limited valid solution paths
4. Diluted high-signal guidance with lower-signal elaborations

**Evidence Supporting Hypothesis**:
- Derived sections contained unvalidated assumptions (e.g., "at least 4500-5500 rows expected")
- Evaluator hooks section specified P0/P1/P2 priorities without evidence from actual tests
- Multiple failure modes described edge cases without clear prioritization
- Postconditions included environment-specific details not grounded in task specification

## Which Evidence Justified It

**Primary Evidence**: Tune split negative transfer (C3 < C2 by 0.1056)

**Supporting Pattern**: The performance degradation came after adding "helpful" execution guidance, suggesting:
- More is not better for skill artifacts
- Agent-generated expansions may hallucinate constraints
- Verbose guidance competes with core decision frameworks for attention

**Contrastive Evidence**: C2 (minimal rewrite) scored 0.9 without extensive derived layers, demonstrating that:
- Core skillx fields (purpose, scope, requires, risks) carry sufficient signal
- Guidance sections should be decision frameworks, not exhaustive checklists
- Derived layers should clarify, not expand

## What Uncertainty Remains

**Primary Uncertainty**: Whether the negative transfer came from:
1. **Noise in derived content** (removed speculative requirements will help), OR
2. **Loss of implicit flexibility** (skills became too rigid), OR
3. **Cognitive overload** (too much text to parse), OR
4. **Specific wrong guidance** (one or more harmful pieces of advice)

**Cannot Distinguish Without**: Additional tune-split evaluation comparing:
- R2 (compressed) vs C3 (verbose) vs C2 (minimal)
- Ablation studies removing individual derived sections

**Open Questions**:
- Did the compression go far enough? (Could simplify more)
- Did it go too far? (May have removed useful structure)
- Are there specific sections that carry disproportionate harm/value?

## Round Classification

**Primary refine operation**: **Compression and clarification**

**Secondary operations**:
- Removing unsupported claims
- Reducing list bloat
- Focusing guidance on high-signal elements

**Not attempted in this round**:
- Adding new guidance
- Expanding scope
- Introducing new constraints
- Changing core methodology
