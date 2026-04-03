---
skillx:
  name: did_causal_analysis
  purpose: Analyze e-commerce spending pattern changes using Difference-in-Differences causal inference to identify demographic drivers of category-level trend anomalies.
  scope_in:
    - Tasks requiring causal analysis of trend anomalies with demographic features
    - Identifying drivers of spending changes across treatment vs baseline periods
    - DiD analysis with both intensive margin (how much) and extensive margin (how many) estimation
    - Multi-step workflows combining data cleaning, anomaly detection, feature engineering, and causal inference
  scope_out:
    - Simple descriptive statistics or correlation analysis without causal inference
    - Time-series forecasting without treatment/control comparison
    - Single-period analysis without baseline-treatment structure
    - Tasks not requiring statistical significance testing (p-values)
  requires:
    - Cleaned demographic data with numeric engineered features for DiD covariates
    - Transaction data aggregated to user-category-period level (not raw transactions)
    - Clear definition of baseline and treatment periods (e.g., Jan-Feb 2020 vs March 2020)
    - Anomaly detection results identifying target categories for analysis
    - Python environment with pandas, statsmodels, and time-series libraries
  preferred_tools:
    - pandas for data manipulation and aggregation
    - statsmodels OLS/WLS for DiD regression with p-values
    - Prophet or similar for time-series anomaly detection
    - Standard statistical libraries (numpy, scipy)
  risks:
    - Confusing intensive margin (sparse, purchasers only) with extensive margin (complete panel, all users) - they require different data structures
    - Including non-participants in intensive margin analysis dilutes treatment effects and changes the research question
    - Not creating complete entity grid for extensive margin biases participation rate estimates
    - Using manual calculation instead of regression loses p-value significance testing
    - Wrong baseline period selection (e.g., using 2019 data instead of immediate pre-treatment months)
    - Forgetting to filter aggregated data to only top-N anomalous categories before DiD
  examples:
    - Analyzing March 2020 spending surge/slump by product category with demographic drivers
    - Comparing intensive margin (spending per buyer) vs extensive margin (adoption rate) effects
    - Identifying top 3 features explaining behavioral changes for surge vs slump categories
---

# Guidance

## Workflow Overview

This skill supports multi-step causal analysis workflows:

1. **Data Cleaning**: Remove duplicates, handle missing values, ensure data quality in both demographic and transaction datasets
2. **Anomaly Detection**: Use time-series forecasting (e.g., Prophet) to detect categories with unusual spending patterns in treatment period vs historical baseline
3. **Feature Engineering**: Transform demographic data into numeric features suitable for regression analysis
4. **DiD Analysis**: Apply Difference-in-Differences methodology to identify demographic drivers of anomalous spending changes

## DiD Methodology Core Concepts

### Intensive Margin vs Extensive Margin

**Intensive Margin** - How much behavior changed among participants:
- **Research Question**: "Did buyers spend MORE per purchase?"
- **Data Structure**: Sparse - only users who made purchases (excludes non-buyers)
- **Outcome**: Continuous (e.g., total spending per user-category-period)
- **Critical**: Do NOT include zeros for non-purchasers - this dilutes effects

**Extensive Margin** - How many people changed behavior:
- **Research Question**: "Did MORE people start buying?"
- **Data Structure**: Complete panel - ALL users × categories × periods (includes non-buyers)
- **Outcome**: Binary (0 = no purchase, 1 = made purchase)
- **Critical**: MUST include non-purchasers to measure participation rate changes

### Data Preparation Requirements

**For Intensive Margin:**
```python
# Only aggregate actual transactions - do NOT create complete grid
intensive_df = transactions.groupby(['user_id', 'category', 'period'])['spending'].sum().reset_index()
# Result: Only rows where purchases occurred (sparse data)
```

**For Extensive Margin:**
```python
# Create complete user × category × period grid
all_users = demographics['user_id'].unique()
all_categories = target_categories  # top-N anomalous categories only
all_periods = ['baseline', 'treatment']

complete_grid = pd.DataFrame(
    list(product(all_users, all_categories, all_periods)),
    columns=['user_id', 'category', 'period']
)

# Mark who purchased (1) vs who didn't (0)
purchases_lookup = transactions[['user_id', 'category', 'period']].drop_duplicates()
purchases_lookup['has_purchase'] = 1

extensive_df = complete_grid.merge(purchases_lookup, how='left')
extensive_df['has_purchase'] = extensive_df['has_purchase'].fillna(0).astype(int)
```

### Regression Methods

Both margins use regression to estimate DiD effects: `Y = α + βX + γPost + δ(X × Post) + ε`
- The interaction coefficient δ is the DiD estimate for feature X
- Use statsmodels OLS/WLS to get p-values for significance testing

**Multivariate Heterogeneous DiD:**
- Estimates ALL features simultaneously in one regression
- Controls for confounding between features
- Use when: `n_observations ≥ n_features × 10` (minimum ~10k samples recommended)

**Univariate DiD:**
- Separate regression for EACH feature independently
- More robust with small samples or high-dimensional features
- Use when: Insufficient sample size for multivariate, or as fallback

The analysis should automatically try multivariate first, fall back to univariate if needed.

## Output Requirements

For each category (top 10 surge, top 10 slump):
- **Intensive margin**: Top 3 demographic features sorted by DiD estimate strength
  - For surge categories: sort descending (largest positive effects first)
  - For slump categories: sort ascending (largest negative effects first)
- **Extensive margin**: Top 3 demographic features sorted by DiD estimate strength
  - Same sorting logic as intensive margin
- Each driver must include: feature name, did_estimate, p_value, method used

## Period Definition

- **Baseline**: Immediate pre-treatment period (e.g., Jan-Feb 2020) - NOT distant history
- **Treatment**: The anomaly window being analyzed (e.g., March 2020)
- Using wrong baseline (like entire 2019) weakens the causal design

# Notes for Agent

## Critical Distinctions

1. **Intensive margin requires SPARSE data** (purchasers only) - including non-purchasers changes the question from "how much more did buyers spend" to something undefined

2. **Extensive margin requires COMPLETE panel** (all users) - missing non-purchasers biases participation rate calculations

3. **Filter to target categories BEFORE DiD** - only analyze the top-N anomalous categories identified in anomaly detection step

4. **Use regression, not manual calculation** - manual DiD loses p-values and statistical inference capabilities

## Common Mistakes

- Creating complete user grid for intensive margin → Wrong, dilutes effects with zeros
- Only including purchasers for extensive margin → Wrong, can't measure adoption rate changes
- Analyzing all categories instead of filtering to anomalous ones → Wastes computation, dilutes signal
- Using 2019 as baseline instead of immediate pre-treatment months → Weakens causal identification
- Not sorting drivers by effect magnitude before selecting top 3 → Returns arbitrary features

## Verification Steps

1. Check intensive margin has fewer rows than extensive margin (only purchasers vs all users)
2. Verify extensive margin has exactly: n_users × n_categories × n_periods rows
3. Confirm no duplicate user-category-period combinations in either dataset (DiD requires independent observations)
4. Validate period labels match exactly between intensive and extensive data (case-sensitive)
5. Ensure all features are numeric (categorical variables must be encoded first)
6. Check p-values are in [0, 1] range and method is reported correctly

## Statistical Interpretation

- **Significance level**: Typically p < 0.05 or p < 0.1 depending on context
- **Effect direction**: Positive DiD estimate = feature associated with increase; negative = decrease
- **Not all categories will have significant drivers** - some anomalies may be due to unmeasured factors
- **Top 3 drivers are ranked by magnitude**, not significance - include p-values for interpretation

# Derived Execution Layer

## Preconditions

Before executing this skill, the following must be satisfied:

1. **Upstream Data Availability**:
   - `survey_feature_engineered.csv` exists with numeric features ready for regression
   - `user_category_period_aggregated_intensive.csv` exists (sparse, purchasers only)
   - `user_category_period_aggregated_extensive.csv` exists (complete panel, all users)
   - `category_anomaly_index.csv` exists with anomaly scores for all categories

2. **Data Structure Requirements**:
   - Intensive margin data contains only actual purchasers (no zeros for non-purchasers)
   - Extensive margin data contains complete user × category × period grid with binary outcome
   - No duplicate user-category-period combinations in either dataset
   - Period labels are exactly "baseline" and "treatment" (or "Baseline" and "Treatment")

3. **Time Period Definition**:
   - Baseline period defined as January-February 2020 (immediate pre-treatment)
   - Treatment period defined as March 2020 (anomaly window)
   - NOT using 2019 or distant historical data as baseline

4. **Category Selection**:
   - Top 10 surge categories identified (highest positive anomaly indices)
   - Top 10 slump categories identified (lowest negative anomaly indices)
   - Categories ranked and selected from `category_anomaly_index.csv`

5. **Feature Preparation**:
   - All demographic features are numeric (categorical variables already encoded)
   - Features merged with aggregated transaction data on Survey ResponseID
   - Sufficient sample size for regression (at least hundreds of observations per category)

## Postconditions

After successful execution, verify:

1. **Output File Existence**:
   - `causal_analysis_report.json` created in `/app/output/` directory
   - File is valid JSON and parseable

2. **Report Structure Completeness**:
   - `metadata` section contains: baseline_start, baseline_end, treatment_start, treatment_end, total_features_analyzed
   - `surge_categories` array contains exactly 10 category objects
   - `slump_categories` array contains exactly 10 category objects
   - `summary` section contains surge and slump subsections with totals

3. **Category-Level Results**:
   - Each category has: category name, anomaly_index, baseline/treatment statistics
   - Each category has `intensive_margin` array with 3 driver objects
   - Each category has `extensive_margin` array with 3 driver objects
   - Surge categories have positive anomaly_index values
   - Slump categories have negative anomaly_index values

4. **Driver Object Completeness**:
   - Each driver contains: feature (string), did_estimate (numeric), p_value (numeric or null), method (string)
   - Drivers are sorted correctly:
     - Surge categories: descending by did_estimate (largest positive first)
     - Slump categories: ascending by did_estimate (largest negative first)

5. **Statistical Validity**:
   - P-values are in [0, 1] range or null
   - DiD estimates are finite (not NaN or infinite)
   - Method field correctly indicates "Multivariate Heterogeneous DiD" or "Univariate DiD"
   - At least 15-20% of drivers across all categories show statistical significance (p < 0.1)

6. **Data Consistency**:
   - Categories in report match top 10 surge/slump from `category_anomaly_index.csv`
   - Baseline/treatment dates contain "2020" with correct month indicators
   - Total features analyzed matches count in feature engineering output

## Failure Modes

Common failures and their indicators:

1. **Wrong Baseline Period**:
   - **Symptom**: Metadata dates show 2019 or full year 2020 instead of Jan-Feb 2020
   - **Impact**: Weakens causal identification, invalid treatment effect estimates
   - **Detection**: Check `metadata.baseline_start` contains "2020" and "01", `metadata.baseline_end` contains "2020" and "02"

2. **Intensive Margin Data Contamination**:
   - **Symptom**: Intensive margin row count equals extensive margin row count
   - **Impact**: Dilutes treatment effects by including non-purchasers in "how much" analysis
   - **Detection**: Verify `len(intensive_df) < len(extensive_df)` and intensive has no zero Total_Spend values

3. **Incomplete Extensive Margin Panel**:
   - **Symptom**: Extensive margin missing user-category-period combinations for non-purchasers
   - **Impact**: Biases participation rate estimates, cannot measure adoption changes
   - **Detection**: Check `len(extensive_df) == n_users × n_categories × 2` where n_categories = 20

4. **Category Filtering Omission**:
   - **Symptom**: DiD analysis run on all categories instead of top 20 anomalous
   - **Impact**: Wastes computation, dilutes signal from anomalous categories
   - **Detection**: Verify report contains exactly 10 surge + 10 slump categories matching anomaly index top/bottom 10

5. **Driver Sorting Errors**:
   - **Symptom**: Drivers not sorted by magnitude, or sorted in wrong direction
   - **Impact**: Top 3 drivers don't represent strongest effects
   - **Detection**: For surge intensive_margin, verify `estimates[0] >= estimates[1] >= estimates[2]`; for slump, verify `estimates[0] <= estimates[1] <= estimates[2]`

6. **Duplicate Observations**:
   - **Symptom**: Multiple rows for same user-category-period combination
   - **Impact**: Violates DiD independence assumption, inflates statistical significance
   - **Detection**: Check for duplicates in intensive/extensive aggregated data before DiD

7. **Manual Calculation Instead of Regression**:
   - **Symptom**: P-values all equal to null or missing
   - **Impact**: Cannot assess statistical significance, loses inferential power
   - **Detection**: Verify p_value fields are numeric and method indicates regression approach

8. **Period Label Mismatch**:
   - **Symptom**: Inconsistent capitalization between intensive/extensive (e.g., "Baseline" vs "baseline")
   - **Impact**: Data merge failures, incomplete analysis
   - **Detection**: Verify Period column values match exactly between datasets

9. **Non-Numeric Features**:
   - **Symptom**: Regression fails with dtype errors
   - **Impact**: DiD analysis cannot run on categorical string features
   - **Detection**: Check all feature columns are numeric dtype before regression

10. **Insufficient Statistical Power**:
    - **Symptom**: All p-values > 0.5, no significant drivers found
    - **Impact**: May indicate sample size too small or weak signals
    - **Detection**: Check median p-value across all drivers; if > 0.7, signal may be weak

## Evaluator Hooks

The benchmark evaluator checks the following surfaces:

1. **File Existence and Parseability**:
   - `causal_analysis_report.json` must exist at `/app/output/causal_analysis_report.json`
   - File must be valid JSON (parseable without errors)

2. **Structure Validation (P0 - 50% weight)**:
   - Required sections present: metadata, surge_categories, slump_categories, summary
   - Metadata keys: baseline_start, baseline_end, treatment_start, treatment_end, total_features_analyzed
   - Summary structure: surge.{total_categories, total_intensive_drivers, total_extensive_drivers}
   - Summary structure: slump.{total_categories, total_intensive_drivers, total_extensive_drivers}

3. **Category Count Validation (P1 - 35% weight)**:
   - Exactly 10 surge categories in `surge_categories` array
   - Exactly 10 slump categories in `slump_categories` array
   - Categories match top 10 and bottom 10 from `category_anomaly_index.csv`

4. **Period Correctness (P1 - 35% weight)**:
   - Baseline period must be in 2020: `baseline_start` and `baseline_end` contain "2020"
   - Baseline ends in February: `baseline_end` contains "02" or "2-"
   - Treatment is in March 2020: `treatment_start` contains "2020" and ("03" or "3-")

5. **Driver Structure Validation (P1 - 35% weight)**:
   - Each category has `intensive_margin` array
   - Each category has `extensive_margin` array
   - Each margin array is non-empty (length > 0)
   - Each margin array has ≤ 3 drivers (top 3 requirement)
   - Each driver has required fields: feature, did_estimate, p_value, method

6. **Driver Content Validation (P1 - 35% weight)**:
   - `did_estimate` is numeric (int or float)
   - `p_value` is numeric or null (can be null for Manual method)
   - If `p_value` is numeric, it's in [0, 1] range
   - `feature` is non-empty string
   - `method` is non-empty string

7. **Driver Sorting Validation (P1 - 35% weight)**:
   - Surge categories: intensive_margin sorted descending by did_estimate
   - Surge categories: extensive_margin sorted descending by did_estimate
   - Slump categories: intensive_margin sorted ascending by did_estimate (most negative first)
   - Slump categories: extensive_margin sorted ascending by did_estimate (most negative first)

8. **Anomaly Index Sign Validation (P1 - 35% weight)**:
   - All surge categories have positive `anomaly_index` values
   - All slump categories have negative `anomaly_index` values

9. **Statistical Health Checks (P1 - 35% weight)**:
   - At least 15% of all drivers (across all categories) have p < 0.1
   - Median p-value across all drivers is between 0.05 and 0.8 (realistic distribution)
   - Both positive and negative did_estimate values present (variation)

10. **Cross-File Consistency (P2 - 15% weight)**:
    - Intensive margin data has fewer rows than extensive margin (purchasers vs all users)
    - Extensive margin user count matches survey_feature_engineered.csv user count
    - No duplicate user-category-period combinations in aggregated datasets
    - Total spending conserved during aggregation (within 10% tolerance for outlier capping)
    - Aggregation correctly represents filtered transactions for top 20 categories only

11. **Descriptive Statistics Validation (P1 - 35% weight)**:
    - Each category has: baseline_avg_spend, treatment_avg_spend (non-negative)
    - Each category has: n_purchasers_baseline, n_purchasers_treatment (non-negative integers)
    - Each category has: baseline_purchase_rate, treatment_purchase_rate (in [0, 1])
    - Each category has: n_at_risk (positive integer, total users in analysis)

12. **Data Independence Validation (P2 - 15% weight)**:
    - User-category-period combinations are unique (no duplicates)
    - Aggregation performed at correct granularity for DiD assumptions
    - Sample verification: randomly check 20 rows for correct aggregation math
