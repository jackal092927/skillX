# Class-aware C2 Notes — offer-letter-generator

## How this differs from the generic C2

- Tightened to the **artifact-generator** class objective: output-contract preservation over broad docx technique coverage.
- Added explicit **contract language** (preserve template structure, section ordering, and clause stability unless markers say otherwise).
- Strengthened **missing-input policy**: request/flag missing required fields; do not invent values.
- Made **acceptance checks deterministic** (valid .docx, resolved-or-flagged placeholders, repeated-field consistency, no leftover control markers, no invented clauses).
- Kept the original high-value insight central: **split placeholders across runs** are the primary failure mode; paragraph-level replacement is required.

## Artifact-generator prior instantiated

Applied the template-family prior by emphasizing:
- `purpose / scope_in / scope_out / requires / risks / examples`
- preserve-structure rule
- no-invention rule
- required-field handling policy
- deterministic output-contract acceptance criteria

This remains **C2**: compact, operational guidance without C3-style heavy derived layers or benchmark-targeted tricks.