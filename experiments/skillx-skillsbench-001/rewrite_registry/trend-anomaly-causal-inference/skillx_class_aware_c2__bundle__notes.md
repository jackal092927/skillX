# Class-Aware C2 Bundle Notes — trend-anomaly-causal-inference

## Bundle Objective
Execute the four-stage analytic pipeline with explicit boundaries and deterministic handoffs:
1. Data cleaning
2. Feature engineering
3. Time-series anomaly detection
4. DiD causal analysis

This rewrite stays in **C2**: clearer stage contracts and artifact expectations, without adding C3-style heavy derived logic, benchmark hacks, or overfitted evaluator tricks.

## Stage Graph and Artifacts

### Stage 1 — data_cleaning
- In: raw survey + raw transactions
- Out:
  - `survey_cleaned.csv`
  - `transactions_cleaned.csv`
- Contract focus: preserve `Survey ResponseID`, datetime integrity, category labels, numeric spend values.

### Stage 2 — feature_engineering
- In: `survey_cleaned.csv`
- Out: `survey_feature_engineered.csv`
- Contract focus: respondent-keyed numeric covariates only; no outcome leakage.

### Stage 3 — time_series_anomaly_detection
- In: `transactions_cleaned.csv`
- Out: `category_anomaly_index.csv`
- Contract focus: pre-March training vs March evaluation split; directional anomaly ranking (surge and slump).

### Stage 4 — did_causal_analysis
- In:
  - `category_anomaly_index.csv`
  - `survey_feature_engineered.csv`
  - cleaned linkage-ready data from prior stages
- Out:
  - `did_intensive_analysis_data.csv`
  - `did_extensive_analysis_data.csv`
  - `causal_analysis_report.json`
- Contract focus: strict intensive (sparse) vs extensive (complete) panel separation; report consistency with intermediates.

## What Was Strengthened (vs generic minimal C2)
- Explicit per-stage input/output artifact contracts.
- Clear handoff rules to prevent stage leakage.
- Required pre-handoff checks tied to evaluator-sensitive failure points.
- Boundary-safe wording to keep each skill stage-local and non-overlapping.
- Consistent alignment with task profile risks:
  - stage-confusion-sensitive
  - negative-transfer-sensitive
  - evaluator-compatibility-sensitive

## Evaluator Compatibility Posture (C2 Level)
- Ensure required artifacts exist at each stage with expected semantics.
- Preserve treatment-window semantics (March vs baseline).
- Keep DiD margin construction faithful (intensive sparse, extensive complete).
- Keep final report structurally consistent with category selection and intermediate tables.

## Deliberate Non-Goals (to remain C2)
- No benchmark-specific hardcoded top-N hacks beyond task requirements.
- No heavy derived-layer monolith replacing stage-local guidance.
- No extra optimization/evaluator scripts introduced in this rewrite pass.