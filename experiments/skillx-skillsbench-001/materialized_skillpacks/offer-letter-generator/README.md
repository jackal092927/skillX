# Materialized Skillpacks — offer-letter-generator

This folder contains pre-materialized condition assets for the first real SkillX micro-shakedown.

Purpose:
- avoid runtime ambiguity about how `C2` and `C3` should be assembled
- let a remote execution agent copy a ready-to-use skill package directly into the benchmark task sandbox

Available condition packs:
- `c2_minimal/docx/SKILL.md`
- `c2_class_aware/docx/SKILL.md`
- `c3_derived/docx/SKILL.md`

Interpretation:
- `C2` = generic minimal SkillX rewrite
- `C2A` = class-aware minimal SkillX rewrite
- `C3` = minimal SkillX rewrite plus integrated derived execution layer
