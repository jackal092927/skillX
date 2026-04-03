# Analytic Pipeline Bundle Template v0.1

- **Task class:** `analytic-pipeline-bundle`
- **Examples:** `trend-anomaly-causal-inference`, `exoplanet-detection-period`, `energy-ac-optimal-power-flow`
- **Primary pattern:** `pipeline`
- **Typical topology:** `multi-skill-staged-bundle`

## 1. When to use this template

Use this template when the task is naturally decomposed into several analytic stages, each with:
- a distinct role,
- a distinct intermediate artifact,
- and a clear handoff to the next stage.

This family often appears in scientific, quantitative, or multi-step analysis tasks.

## 2. Core design goal

The main goal is **stage integrity**.

A good skill bundle in this family should help the agent:
- preserve stage boundaries,
- produce evaluator-compatible intermediate artifacts,
- maintain handoff contracts,
- and avoid silently blending preprocessing, inference, ranking, and final analysis.

## 3. Default scaffold stance

- **Scaffold budget:** medium to high, but distributed across stages
- Important rule: do **not** accumulate all guidance in one monolithic derived layer
- Guidance should be localized to the stage where it matters

## 4. Recommended field emphasis

At the bundle level, emphasize:
- stage graph / stage ordering
- end-to-end task objective
- bundle-level acceptance criteria

At the stage level, emphasize:
- `purpose`
- `scope_in`
- `scope_out`
- expected input artifact
- expected output artifact
- stage-local risks
- handoff note to next stage

## 5. Recommended extra resources

Useful bundled resources include:
- stage manifests
- data schema notes
- artifact examples
- invariant checklists
- stage-specific reference docs
- minimal evaluator scripts

## 6. Script policy

- **Default:** recommended to required
- Good scripts include:
  - schema checks
  - artifact validators
  - invariant checks
  - stage-level sanity tests

## 7. Verifier shape

Best verifier posture for this family:
- per-stage artifact checks
- handoff contract checks
- end-to-end outcome verification
- review lane for evaluator compatibility and silent stage leakage

## 8. Common failure modes

- stage confusion
- malformed intermediate artifacts
- data leakage across stages
- wrong ordering
- locally plausible but evaluator-incompatible final outputs
- missing stage outputs in refined bundles

## 9. Inner-loop refinement bias

Refinement should usually favor:
- clearer stage boundaries
- stronger handoff contracts
- more explicit expected artifacts
- distributed guidance rather than bundle bloat
- deterministic validation where feasible

Typical good edits:
- split one broad guidance block into stage-local notes
- add input/output artifact statements
- add stage-local failure checks
- delete duplicated cross-stage prose

## 10. Suggested skeleton

```markdown
---
skillx:
  name: analytic-pipeline-bundle
  purpose: Execute a staged analytic workflow with explicit handoff contracts and stage-level verification.
  scope_in:
    - task requires ordered multi-stage quantitative or scientific analysis
  scope_out:
    - not for one-shot analysis without meaningful intermediate artifacts
  requires:
    - clear stage ordering and expected artifacts
  risks:
    - stage confusion
    - artifact mismatch
    - evaluator incompatibility
---

# Bundle Objective
- Complete the full analytic workflow while preserving stage integrity.

# Stage Graph
1. Stage A -> produce cleaned / normalized artifact
2. Stage B -> produce transformed / candidate artifact
3. Stage C -> rank / infer / optimize
4. Stage D -> generate final interpretation or report

# Stage Contracts
- For each stage, define input artifact, output artifact, and handoff rule.

# Acceptance
- Each stage output exists and is valid.
- Handoffs satisfy stated contracts.
- Final output is compatible with the benchmark verifier.
```
