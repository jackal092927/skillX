# Artifact Generator Template v0.1

- **Task class:** `artifact-generator`
- **Examples:** `offer-letter-generator`
- **Primary pattern:** `generator`
- **Typical topology:** `single-skill`

## 1. When to use this template

Use this template when the task is mainly:
- transforming known inputs into a structured output artifact,
- preserving a template or output contract,
- and avoiding invented or inconsistent content.

This class usually has:
- clear required inputs,
- a relatively deterministic output shape,
- and a verifier that can check output completeness and structure.

## 2. Core design goal

The main goal is **contract preservation**, not open-ended reasoning richness.

A good skill in this family should help the agent:
- preserve template structure,
- avoid fabricating content,
- detect missing inputs early,
- and produce a complete output artifact with minimal drift.

## 3. Default scaffold stance

- **Scaffold budget:** low to medium
- **Why:** stronger models often do better with compact, high-signal rules here
- **Risk:** too much prose can distract from the output contract

## 4. Recommended field emphasis

Within the minimal SkillX format, emphasize:
- `purpose`
- `scope_in`
- `scope_out`
- `requires`
- `risks`
- `examples`

Especially important additions for this family:
- explicit output contract summary
- placeholder / required-field policy
- preserve-structure rule
- no-invention rule

## 5. Recommended extra resources

Useful bundled resources include:
- output template examples
- placeholder maps
- style or formatting references
- validation checklist

Keep these small and focused.
Do not bundle broad tutorials unless truly necessary.

## 6. Script policy

- **Default:** optional
- Prefer scripts only when they support deterministic inspection, e.g.:
  - placeholder validation
  - template diff checks
  - structural completeness checks

## 7. Verifier shape

Best verifier posture for this family:
- deterministic output-contract check
- missing-field check
- preservation-of-template-structure check
- anti-invention / anti-drift review lane

## 8. Common failure modes

- dropped placeholders
- invented fields or clauses
- inconsistent repeated values
- formatting drift that breaks the artifact
- silently guessing missing inputs

## 9. Inner-loop refinement bias

Refinement should usually favor:
- compression over elaboration
- clearer contract statements over long tutorials
- stronger missing-input handling
- lighter but sharper risk language

Typical good edits:
- delete generic prose
- add compact preserve-structure rules
- tighten required-input statements
- remove redundant examples

## 10. Suggested skeleton

```markdown
---
skillx:
  name: artifact-generator-skill
  purpose: Produce a structured output artifact while preserving template and field integrity.
  scope_in:
    - user asks to fill, generate, or update a structured document or artifact from known inputs
  scope_out:
    - not for open-ended writing that lacks a clear output contract
    - not for inventing missing fields without explicit instruction
  requires:
    - output template or clear target format
    - all required input fields, or permission to mark them as missing
  risks:
    - placeholder loss
    - invented content
    - repeated-field inconsistency
  examples:
    - input: fill a template-based offer letter
      expected_behavior: preserve structure, request missing fields, avoid invention
---

# Guidance
- Preserve the output contract.
- If required inputs are missing, ask or mark them explicitly.
- Do not invent template content.

# Acceptance
- Output artifact is structurally complete.
- Repeated fields are consistent.
- No required placeholder is silently dropped.
```
