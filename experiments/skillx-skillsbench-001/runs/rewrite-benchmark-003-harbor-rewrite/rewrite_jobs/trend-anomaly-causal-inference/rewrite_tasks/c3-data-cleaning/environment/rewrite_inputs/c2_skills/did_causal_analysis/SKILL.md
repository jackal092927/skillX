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
