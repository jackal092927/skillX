---
skillx:
  name: did_causal_analysis
  purpose: Analyze spending pattern changes using Difference-in-Differences causal inference to identify demographic drivers of category-level anomalies
  scope_in:
    - Causal analysis of trend anomalies with demographic features
    - Identifying drivers of spending changes across treatment vs baseline periods
    - DiD with both intensive margin (how much) and extensive margin (how many) estimation
  scope_out:
    - Simple descriptive statistics without causal inference
    - Time-series forecasting without treatment/control comparison
    - Single-period analysis without baseline-treatment structure
  requires:
    - Cleaned demographic data with numeric engineered features
    - Transaction data aggregated to user-category-period level
    - Clear baseline and treatment period definitions
    - Anomaly detection results identifying target categories
    - Python with pandas, statsmodels for DiD regression
  preferred_tools:
    - pandas for data manipulation and aggregation
    - statsmodels OLS/WLS for DiD regression with p-values
    - Standard statistical libraries (numpy, scipy)
  risks:
    - Confusing intensive (purchasers only) with extensive (all users) margins
    - Including non-participants in intensive margin dilutes effects
    - Not creating complete grid for extensive margin biases rates
    - Using manual calculation loses p-value significance testing
    - Wrong baseline period selection (e.g., 2019 instead of immediate pre-treatment)
  examples:
    - Analyzing March 2020 spending surge/slump with demographic drivers
    - Comparing intensive (spending per buyer) vs extensive (adoption rate) effects
    - Identifying top 3 features explaining behavioral changes

# Guidance

## DiD Methodology Core Concepts

### Intensive Margin vs Extensive Margin

**Intensive Margin** - How much behavior changed among participants:
- **Question**: "Did buyers spend MORE per purchase?"
- **Data**: Sparse - only users who made purchases (excludes non-buyers)
- **Outcome**: Continuous (total spending per user-category-period)
- **CRITICAL**: Do NOT include zeros for non-purchasers

**Extensive Margin** - How many people changed behavior:
- **Question**: "Did MORE people start buying?"
- **Data**: Complete panel - ALL users × categories × periods
- **Outcome**: Binary (0 = no purchase, 1 = made purchase)
- **CRITICAL**: MUST include non-purchasers

### Data Preparation

**For Intensive Margin:**
```python
# Only aggregate actual transactions - do NOT create complete grid
intensive_df = transactions.groupby(['user_id', 'category', 'period'])['spending'].sum().reset_index()
# Result: Only rows where purchases occurred (sparse)
```

**For Extensive Margin:**
```python
# Create complete user × category × period grid
complete_grid = pd.DataFrame(
    list(product(all_users, target_categories, ['baseline', 'treatment'])),
    columns=['user_id', 'category', 'period']
)

# Mark who purchased
purchases_lookup = transactions[['user_id', 'category', 'period']].drop_duplicates()
purchases_lookup['has_purchase'] = 1

extensive_df = complete_grid.merge(purchases_lookup, how='left')
extensive_df['has_purchase'] = extensive_df['has_purchase'].fillna(0).astype(int)
```

### Regression Methods

DiD regression: `Y = α + βX + γPost + δ(X × Post) + ε`
- Interaction coefficient δ is the DiD estimate for feature X
- Use statsmodels OLS/WLS to get p-values

**Multivariate Heterogeneous DiD**: All features simultaneously, controls for confounding (use when n_observations ≥ n_features × 10)

**Univariate DiD**: Separate regression per feature, more robust with small samples

## Output Requirements

For each category (top 10 surge, top 10 slump):
- **Intensive margin**: Top 3 features sorted by DiD estimate strength
  - Surge: descending (largest positive first)
  - Slump: ascending (largest negative first)
- **Extensive margin**: Top 3 features sorted by DiD estimate strength (same logic)
- Each driver: feature name, did_estimate, p_value, method

## Period Definition

- **Baseline**: Immediate pre-treatment (e.g., Jan-Feb 2020) - NOT distant history
- **Treatment**: Anomaly window (e.g., March 2020)

# Execution Notes

## Critical Distinctions

1. **Intensive requires SPARSE data** (purchasers only) - including non-purchasers changes the question
2. **Extensive requires COMPLETE panel** (all users) - missing non-purchasers biases rates
3. **Filter to target categories BEFORE DiD** - only top-N anomalous categories
4. **Use regression, not manual calculation** - to get p-values and significance

## Common Mistakes

- Creating complete grid for intensive → Wrong, dilutes effects
- Only including purchasers for extensive → Wrong, can't measure adoption rates
- Analyzing all categories instead of filtering → Wastes computation
- Using 2019 as baseline instead of immediate pre-treatment → Weakens causal identification
- Not sorting drivers by magnitude → Returns arbitrary features

## Verification Steps

1. Intensive has fewer rows than extensive (purchasers vs all users)
2. Extensive has exactly: n_users × n_categories × n_periods rows
3. No duplicate user-category-period in either dataset
4. Period labels match exactly between datasets
5. All features are numeric
6. P-values in [0, 1] range

# Derived Execution Layer

## Key Requirements Before Execution

- `survey_feature_engineered.csv` exists with numeric features
- `user_category_period_aggregated_intensive.csv` exists (sparse, purchasers only)
- `user_category_period_aggregated_extensive.csv` exists (complete panel)
- `category_anomaly_index.csv` exists with anomaly scores
- Period labels are "baseline" and "treatment" (or "Baseline"/"Treatment")
- No duplicate user-category-period combinations
- Baseline defined as Jan-Feb 2020, treatment as March 2020

## Expected Outputs After Completion

- `causal_analysis_report.json` created
- Valid JSON structure with metadata, surge_categories, slump_categories, summary
- Exactly 10 surge categories (positive anomaly indices) and 10 slump categories (negative)
- Each category has intensive_margin and extensive_margin arrays with 3 drivers
- Drivers have: feature, did_estimate, p_value, method
- Drivers sorted correctly (descending for surge, ascending for slump)
- Baseline dates contain "2020" and "01"/"02", treatment contains "2020" and "03"
- At least 15-20% of drivers show statistical significance (p < 0.1)

## High-Impact Failure Modes to Avoid

1. **Wrong baseline period**: Using 2019 or full 2020 instead of Jan-Feb 2020
2. **Intensive contamination**: Including non-purchasers (row count equals extensive)
3. **Incomplete extensive panel**: Missing non-purchaser combinations
4. **Category filtering omission**: Running DiD on all categories instead of top 20
5. **Driver sorting errors**: Not sorted by magnitude or wrong direction
6. **Duplicate observations**: Multiple rows for same user-category-period
