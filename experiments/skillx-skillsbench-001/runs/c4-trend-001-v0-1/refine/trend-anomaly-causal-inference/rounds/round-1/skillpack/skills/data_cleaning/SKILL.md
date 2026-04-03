---
skillx.name: data_cleaning
skillx.purpose: Clean messy tabular datasets (demographic surveys and transaction records) to prepare them for time-series analysis, anomaly detection, and causal inference. Handle duplicates, missing values, inconsistent formatting, outliers, and text processing.
skillx.scope_in: |
  - Deduplication based on logical keys and downstream requirements
  - Missing value handling (drop vs impute) based on column criticality
  - Text processing (extract numbers, clean whitespace, standardize formats)
  - Outlier handling (cap vs remove) based on statistical methods
  - Data type conversions and date parsing for time-series work
  - Ensuring referential integrity across related datasets
skillx.scope_out: |
  - Feature engineering or derived variable creation
  - Aggregation or reshaping for specific analyses (e.g., DID panel structure)
  - Statistical modeling or causal inference
  - Data validation rules beyond basic type checking
skillx.requires: |
  - pandas for dataframe operations
  - Understanding of downstream task to make informed cleaning decisions
  - Knowledge of which columns are critical vs optional
skillx.preferred_tools: |
  - `df.drop_duplicates(subset=...)` for deduplication with logical keys
  - `df.dropna(subset=...)` for critical columns
  - `df.fillna()` with median/mode for non-critical columns
  - `sklearn.impute.KNNImputer` when values can be inferred from related columns
  - `pd.to_datetime()` with error handling for date columns
  - IQR-based methods for outlier handling
  - String methods (`str.extract()`, `str.strip()`, `str.lower()`) for text cleaning
skillx.risks: |
  - Dropping too many rows harms sample size and statistical power
  - Imputing critical outcome variables or treatment indicators introduces bias
  - Removing outliers without understanding signal vs noise distorts conclusions
  - Inconsistent cleaning logic between datasets breaks joins
  - Over-cleaning removes legitimate variation needed for analysis
skillx.examples: |
  Remove duplicates by logical key:
  ```python
  df.drop_duplicates(subset=['customer_id', 'order_date'], keep='first')
  ```

  Drop rows with missing critical identifiers:
  ```python
  df.dropna(subset=['customer_id', 'order_date'], inplace=False)
  ```

  Impute non-critical numerical columns with median:
  ```python
  df['income'].fillna(df['income'].median(), inplace=True)
  ```

  Cap outliers using IQR:
  ```python
  Q1, Q3 = df['amount'].quantile([0.25, 0.75])
  IQR = Q3 - Q1
  lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
  df['amount'] = df['amount'].clip(lower, upper)
  ```
---

# Guidance

## Decision Framework

**Deduplication**: Check for duplicates first. Examine logical structure and downstream goals:
- Survey/demographic data: one row per respondent (remove duplicate IDs)
- Transaction data: multiple transactions per user are legitimate (do NOT deduplicate by user alone)
- Use appropriate subset of columns that define uniqueness

**Missing Value Strategy**:
1. Critical columns (IDs, dates, outcome variables): drop rows with missingness
2. Non-critical numerical: impute with median
3. Non-critical categorical: impute with mode
4. Non-critical with strong relationships to other columns: consider KNN imputation

**Outlier Handling**:
- If sample size is large and outliers are clearly errors: remove using IQR or Z-score
- If sample size is precious or outliers might be real: cap using winsorization
- Default: 1.5 for IQR multiplier, 3.0 for Z-score
- For causal inference: be cautious about removing extreme values

## Implementation Pattern

1. Read and preview data (`df.head()`, `df.info()`, `df.describe()`)
2. Check for duplicates and understand their source
3. Identify missing value patterns (`df.isnull().sum()`)
4. Clean in stages: identifiers → critical fields → non-critical fields → outliers
5. Verify referential integrity between related datasets
6. Document rows affected by each operation
7. Save cleaned outputs with clear naming

## Common Patterns

**Survey/Demographic Data**:
- Expect one row per respondent
- Remove duplicate Survey ResponseIDs
- Demographic columns may need imputation
- Verify IDs follow expected format

**Transaction/Purchase Data**:
- Multiple transactions per user are normal
- Date columns must be parseable and within expected range
- Price/amount should be positive and within reasonable bounds
- Category columns should not have nulls
- Verify Survey ResponseIDs link to demographic data

**Cross-Dataset Validation**:
- After cleaning, verify transaction IDs exist in demographic data
- Filter transactions to only include users in cleaned demographics if required
- Ensure date ranges align with analysis requirements

# Execution Notes

1. **Always preview before cleaning**: Use `df.head()`, `df.info()`, `df.describe()` to understand data structure before applying operations

2. **Document decisions**: Note why you chose each approach (e.g., "Dropping rows with missing Category because required for aggregation")

3. **Check referential integrity early**: Verify IDs in transaction data exist in demographic data before proceeding

4. **Be conservative with outlier removal**: For causal inference, extreme values may represent real effects. Prefer capping over removal unless clearly errors

5. **Validate cleaning results**: Check resulting dataset size and summary statistics after major operations

6. **Save outputs promptly**: Write cleaned datasets to specified paths before proceeding to analysis

7. **Handle date parsing carefully**: Use `pd.to_datetime()` with `errors='coerce'` and verify dates fall within expected ranges

# Derived Execution Layer

## Key Requirements Before Execution

- Input files exist and are readable
- Output directory is writable
- Required libraries available (pandas, sklearn if using KNN)
- Downstream task requirements understood (time-series needs parseable dates, causal inference needs referential integrity)

## Expected Outputs After Completion

- Output files exist with correct names
- Survey data has unique Survey ResponseID with no duplicates
- Purchase data has required columns with valid dates and positive prices
- Zero missing values in critical columns
- Cross-dataset referential integrity maintained (IDs in purchases exist in survey)

## High-Impact Failure Modes to Avoid

1. **Wrong deduplication logic**: Removing legitimate transactions or not removing duplicate survey responses
2. **Incomplete missing value handling**: Leaving nulls in columns that break downstream analysis
3. **Date parsing errors**: Not filtering to correct date range or failing to parse dates
4. **Referential integrity breaks**: Cleaning datasets independently without checking ID overlap
5. **Sample size disasters**: Over-aggressive filtering reduces data below minimum viable size
