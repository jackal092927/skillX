# Round 2 Risk Note

## New Regressions This Round Might Introduce

### 1. Over-Compression Risk

**Nature**: Removed too much structure, leaving skills under-specified

**Symptoms to Watch**:
- Executor agents struggle with ambiguous requirements
- Increased variation in execution quality
- New failure modes from missing guidance
- Agents inventing requirements not in skills

**Likelihood**: Low-Medium (20%)

**Severity if Occurs**: Medium (Δ = -0.03 to -0.05)

**Mitigation in R2**: Preserved all core guidance frameworks and critical validations

---

### 2. Loss of Helpful Scaffolding

**Nature**: Some verbose sections may have provided useful structure for less capable executors

**Symptoms to Watch**:
- Postcondition validation failures increase
- Cross-dataset integrity breaks more frequent
- Agents miss non-obvious requirements
- Execution time increases (more trial-and-error)

**Likelihood**: Low (15%)

**Severity if Occurs**: Low (Δ = -0.01 to -0.03)

**Mitigation in R2**: Retained all "High-Impact Failure Modes" (compressed but not removed)

---

### 3. Over-Tightening Without Realizing

**Nature**: Compression may have inadvertently removed flexibility

**Symptoms to Watch**:
- Skills become less applicable to task variations
- Execution gets more brittle
- Valid approaches excluded by tighter interpretation

**Likelihood**: Very Low (5%)

**Severity if Occurs**: Low (Δ = -0.02 to -0.04)

**Mitigation in R2**: No changes to scope_in/scope_out or core methodology

---

### 4. Information Asymmetry

**Nature**: Removed sections contained non-obvious insights that C2 conveyed differently

**Symptoms to Watch**:
- Specific failure modes from R1/C3 reappear
- Execution misses subtle requirements
- Performance parity with R1 instead of improvement

**Likelihood**: Low (10%)

**Severity if Occurs**: Low-Medium (Δ = -0.03 to -0.05)

**Mitigation in R2**: Systematic preservation of correctness-critical content

---

### 5. Compression Insufficient

**Nature**: Removed only low-signal content; core bloat remains

**Symptoms to Watch**:
- R2 reward ≈ R1 reward (no improvement)
- Negative transfer not recovered
- Skills still feel verbose in practice

**Likelihood**: Medium (30%)

**Severity if Occurs**: Low (Δ ≈ 0, no change)

**Mitigation for R3**: If this occurs, R3 should compress more aggressively

---

## Cross-Skill Failure Modes

### Coordination Degradation

**Risk**: Simplified skills have less explicit handoff contracts

**Watch For**:
- Cross-dataset validation failures
- Period label mismatches (baseline/treatment)
- Feature name or format inconsistencies

**R2 Mitigation**: Preserved all handoff requirements in bundle YAML and individual skills

### Evaluation Brittleness

**Risk**: Removed evaluator hooks section may have captured implicit test requirements

**Watch For**:
- New test failures on edge cases
- Validator rejections for missing postconditions
- File format or naming issues

**R2 Mitigation**: Preserved essential postconditions; removed only speculative P0/P1/P2 structure

---

## Monitoring Recommendations

**If R2 shows improvement (+0.05 or more)**:
- Validate that improvement is real, not evaluation noise
- Check if specific skills drove the gain (may be heterogeneous)
- Consider further compression in R3 if gains are robust

**If R2 shows no change (±0.02)**:
- Diagnosis: Either compression was insufficient, or negative transfer has different cause
- R3 strategy: Consider structural changes beyond compression, or revert to C2-like minimal form

**If R2 shows regression (-0.03 or worse)**:
- Diagnosis: Over-compression or removed critical content
- R3 strategy: Restore key sections, focus on targeted clarification instead of compression

---

## Conservative Principle

Given uncertainty about which content caused C3's negative transfer, R2 takes a **moderate compression approach**:
- Remove obviously speculative content (evaluator hooks, exact row counts)
- Compress verbose lists (failure modes, postconditions)
- Preserve all correctness-critical guidance

**Trade-off**: This may under-correct (insufficient compression) rather than over-correct (excessive compression)

**Rationale**: Safer to require R3 for additional compression than to over-remove and require restoration
