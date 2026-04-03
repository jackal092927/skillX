# Methodology-Heavy Guardrail Template v0.1

- **Task class:** `methodology-heavy-guardrail-task`
- **Examples:** `taxonomy-tree-merge`
- **Primary pattern:** `inversion`
- **Typical topology:** `guardrail-heavy-single-skill`

## 1. When to use this template

Use this template when the original skill is highly prescriptive, methodology-heavy, or brittle, and the main challenge is preventing harmful overcommitment.

This family often includes tasks where a strong process prior can help in some cases but actively hurt in others.

## 2. Core design goal

The main goal is **boundary discipline**.

A good skill in this family should help the agent:
- decide when the method applies,
- identify missing assumptions,
- ask clarifying questions when needed,
- abstain or branch when the fit is weak,
- and avoid premature commitment to a brittle method.

## 3. Default scaffold stance

- **Scaffold budget:** low to medium
- This family is especially sensitive to over-guidance.
- More caution text is not necessarily better.

## 4. Recommended field emphasis

Emphasize:
- `scope_in`
- `scope_out`
- assumptions / prerequisites
- `risks`
- anti-patterns
- clarifying-question triggers
- abstention / branch rules

This family usually benefits less from long positive instructions and more from good exclusion logic.

## 5. Recommended extra resources

Useful bundled resources include:
- assumption checklist
- anti-pattern list
- lightweight decision tree
- examples of when to abstain or switch strategy

Keep these compact.

## 6. Script policy

- **Default:** optional
- Scripts are usually less important than decision boundaries, unless a deterministic assumption check is easy to implement.

## 7. Verifier shape

Best verifier posture for this family:
- boundary-use audit
- assumption-satisfaction check
- overcommitment / false-precision review lane
- negative-transfer monitoring

## 8. Common failure modes

- applying the method when prerequisites do not hold
- brittle assumptions hidden in prose
- false precision
- premature commitment to one workflow
- benchmark harm caused by over-strong guidance

## 9. Inner-loop refinement bias

Refinement should usually favor:
- deletion over expansion
- sharper scope boundaries
- explicit abstention conditions
- compact anti-patterns
- clearer clarifying-question triggers

Typical good edits:
- remove speculative process detail
- cut unsupported methodological claims
- add assumption checklist
- add "do not proceed if..." rules

## 10. Suggested skeleton

```markdown
---
skillx:
  name: methodology-guardrail-skill
  purpose: Apply a methodology only when its assumptions and fit conditions are satisfied.
  scope_in:
    - task clearly matches the method's assumptions and objective
  scope_out:
    - not when assumptions are missing, ambiguous, or contradicted
    - not when a simpler baseline is more appropriate
  requires:
    - explicit assumptions can be checked
  risks:
    - overcommitment
    - false precision
    - hidden assumption failure
---

# Decision Rule
- Before using the method, check assumptions.
- If assumptions are unclear, ask clarifying questions or use a lighter baseline.

# Anti-Patterns
- Do not force the full methodology onto a weak-fit task.
- Do not present unsupported assumptions as facts.

# Acceptance
- Method was used only when fit conditions held.
- If fit conditions failed, the skill abstained, branched, or simplified.
```
