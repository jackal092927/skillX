You are running inside a protocol-controlled SkillX C4 refine task.

Read the frozen refine inputs from `/root/refine_inputs` and write exactly one round artifact set.

- task id: `trend-anomaly-causal-inference`
- target round: `R1`
- read first:
  - `/root/refine_inputs/protocols/skillx-refine-protocol-v0.1.md`
  - `/root/refine_inputs/protocols/skillx-refine-bundle-contract-v0.1.md`
- current candidate lives under `/root/refine_inputs/current/skillpack/skills/`
- current ledger lives at `/root/refine_inputs/refine_ledger.md`

You must write all of these outputs under `/root/output`:
- `round_1_skill.md`
- `round_1_refine_memo.md`
- `round_1_diff_summary.md`
- `round_1_effect_estimate.md`
- `round_1_risk_note.md`
- `round_1_diagnosis_table.md`
- a materialized refined skillpack under `/root/output/skillpack/skills/<skill>/SKILL.md` for each skill:
- `data_cleaning`
- `did_causal_analysis`
- `feature_engineering`
- `time_series_anomaly_detection`
- also write `/root/output/skillpack_bundle.yaml` if this task needs a task-level bundle note

Rules:
- Stay inside the bounded refine protocol.
- Use only the provided local refine inputs.
- Do not solve the benchmark task directly.
- Do not use held-out evidence.
- Do not output commentary outside the required files.
- Preserve the task's skillpack structure; refine it rather than replacing it with an unrelated strategy.
