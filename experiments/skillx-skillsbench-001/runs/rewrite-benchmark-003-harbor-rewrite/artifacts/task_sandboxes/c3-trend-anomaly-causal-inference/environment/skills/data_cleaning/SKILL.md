---
skillx.name: data_cleaning
skillx.purpose: Clean messy tabular datasets (demographic surveys and transaction records) to prepare them for time-series analysis, anomaly detection, and causal inference. Handle duplicates, missing values, inconsistent formatting, outliers, and text processing issues that prevent downstream statistical analysis.
skillx.scope_in: |
  - Deduplication based on logical keys and downstream requirements
  - Missing value handling (drop vs impute) based on column criticality and sample size impact
  - Text processing (extract numbers, clean whitespace, standardize formats)
  - Outlier handling (cap vs remove) based on statistical methods and downstream sensitivity
  - Data type conversions and date parsing for time-series work
  - Ensuring referential integrity across related datasets (e.g., survey IDs linking to transactions)
skillx.scope_out: |
  - Feature engineering or derived variable creation (separate step)
  - Aggregation or reshaping for specific analyses (e.g., DID panel structure)
  - Statistical modeling or causal inference itself
  - Data validation rules or schema enforcement beyond basic type checking
  - Performance optimization for very large datasets (>10M rows)
skillx.requires: |
  - pandas for dataframe operations
  - Understanding of the downstream task to make informed cleaning decisions
  - Knowledge of which columns are critical vs optional for the analysis
  - Sample size considerations (cost of dropping rows vs imputing)
skillx.preferred_tools: |
  - `df.drop_duplicates(subset=...)` for deduplication with logical keys
  - `df.dropna(subset=...)` for critical columns where imputation would harm analysis
  - `df.fillna()` with median/mode for non-critical columns with sufficient independence
  - `sklearn.impute.KNNImputer` when target column values can be inferred from related columns
  - `pd.to_datetime()` with error handling for date columns
  - IQR-based methods (winsorization or removal) for outlier handling
  - String methods (`str.extract()`, `str.strip()`, `str.lower()`) for text cleaning
skillx.risks: |
  - Dropping too many rows due to aggressive missing value or outlier removal can harm sample size and statistical power
  - Imputing critical outcome variables or treatment indicators can introduce bias
  - Removing outliers without understanding if they represent real signal vs noise can distort conclusions
  - Inconsistent cleaning logic between related datasets can break joins (e.g., survey IDs not matching transactions)
  - Over-cleaning can remove legitimate variation needed for causal analysis
  - Text processing that loses semantic information (e.g., extracting only numbers when categories matter)
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

  Cap outliers using IQR (winsorization to preserve sample size):
  ```python
  Q1, Q3 = df['amount'].quantile([0.25, 0.75])
  IQR = Q3 - Q1
  lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
  df['amount'] = df['amount'].clip(lower, upper)
  ```
---

# Guidance

## Decision Framework for Cleaning Operations

**Deduplication**: Always check for duplicates first. Examine the data's logical structure and downstream goals:
- For demographic/survey data: typically one row per respondent (duplicate Survey ResponseIDs should be removed)
- For transaction data: multiple transactions per user are legitimate (do NOT remove based on user ID alone)
- Use appropriate subset of columns that define uniqueness for the data type

**Missing Value Strategy**:
1. Assess criticality: Will missing values in this column directly harm downstream analysis performance?
2. Assess cost: How many rows would be lost by dropping vs potential bias from imputing?
3. Decision tree:
   - Critical columns (IDs, dates, outcome variables): drop rows with missingness
   - Non-critical numerical with sufficient independence: impute with median
   - Non-critical categorical with sufficient independence: impute with mode
   - Non-critical with strong relationships to other columns: consider KNN imputation
4. For KNN imputation: only use when you can identify semantically related columns (e.g., income can be inferred from age + education)

**Text Processing**: Preview column values to determine if cleaning is needed:
- Extract numbers from mixed text/number fields if downstream requires numeric values
- Standardize whitespace and case for categorical fields used in joins or grouping
- Remove special characters only if they interfere with analysis (preserve meaning otherwise)

**Outlier Handling**:
1. Understand if outliers represent real signal or data quality issues
2. Assess sample size impact of removal
3. Decision tree:
   - If sample size is large and outliers are clearly erroneous: remove using IQR or Z-score
   - If sample size is precious or outliers might be real: cap using winsorization (IQR method)
   - Default multiplier: 1.5 for IQR, 3.0 for Z-score
4. For causal inference work: be cautious about removing extreme values that may represent legitimate treatment effects

## Implementation Pattern

For complex cleaning pipelines:
1. Read and preview data first (`df.head()`, `df.info()`, `df.describe()`)
2. Check for duplicates and understand their source
3. Identify missing value patterns (`df.isnull().sum()`)
4. Clean in stages: identifiers → critical fields → non-critical fields → outliers
5. Verify referential integrity between related datasets before proceeding to merges
6. Document the number of rows affected by each operation
7. Save cleaned outputs with clear naming (e.g., `survey_cleaned.csv`, not `survey_v2.csv`)

## Common Patterns for This Task Domain

**Survey/Demographic Data**:
- Expect one row per respondent
- Check for duplicate Survey ResponseIDs and remove
- Demographic columns may have missingness requiring imputation
- Verify all IDs follow expected format (e.g., start with 'R_')

**Transaction/Purchase Data**:
- Multiple transactions per user are normal (do NOT deduplicate by user)
- Date columns must be parseable and within expected range
- Price/amount columns should be positive and within reasonable bounds
- Category columns should not have nulls (either drop rows or impute with mode)
- Verify Survey ResponseIDs link to the demographic data

**Cross-Dataset Validation**:
- After cleaning both datasets, verify that transaction IDs exist in demographic data
- Filter transactions to only include users present in cleaned demographics if required for analysis
- Ensure date ranges align with analysis requirements (e.g., 2019-2020 for this task)

# Notes for Agent

1. **Always preview before cleaning**: Use `df.head()`, `df.info()`, `df.describe()`, and `df.isnull().sum()` to understand the data structure and quality issues before applying any cleaning operations.

2. **Document your decisions**: For each cleaning step, note why you chose that approach (e.g., "Dropping rows with missing Category because it's required for downstream aggregation and only affects 7% of data").

3. **Check referential integrity early**: Before proceeding to analysis steps, verify that IDs in transaction data exist in demographic data. This prevents downstream join issues.

4. **Be conservative with outlier removal**: For causal inference tasks, extreme values may represent real effects. Prefer winsorization (capping) over removal unless outliers are clearly data errors.

5. **Validate cleaning results**: After each major operation, check the resulting dataset size and summary statistics to ensure cleaning didn't inadvertently remove too much data or introduce new issues.

6. **Save intermediate outputs**: Write cleaned datasets to the specified output paths as soon as cleaning is complete, before proceeding to analysis steps. This enables inspection and debugging.

7. **Handle date parsing carefully**: Use `pd.to_datetime()` with `errors='coerce'` to identify unparseable dates, then decide whether to drop or fix them. Verify all dates fall within expected ranges for the analysis.

8. **KNN imputation requires setup**: When using KNN imputation, explicitly specify which features to use for inference and ensure they are numeric. Convert categorical features to numeric first if needed.

# Derived Execution Layer

## Preconditions

Before applying this skill, verify:

1. **Input files exist and are readable**:
   - `/app/data/survey_dirty.csv` contains demographic data
   - `/app/data/amazon-purchases-2019-2020_dirty.csv` contains transaction data
   - Both files are valid CSV format and can be loaded by pandas

2. **Output directory is writable**:
   - `/app/output/` directory exists and has write permissions

3. **Required libraries are available**:
   - pandas is installed and importable
   - sklearn is available if KNN imputation is needed

4. **Downstream task requirements are understood**:
   - Time-series anomaly detection requires parseable dates in 2019-2020 range
   - Causal inference requires referential integrity between survey and transaction data
   - Feature engineering requires complete demographic data (no missing values)
   - All downstream steps require "Survey ResponseID" as linking key

5. **Expected data structure assumptions**:
   - Survey data represents one row per respondent (duplicates are errors)
   - Transaction data allows multiple rows per user (duplicates are legitimate purchases)
   - Survey ResponseID is the primary identifier across both datasets

## Postconditions

After successful execution, verify:

1. **Output files exist with correct names**:
   - `/app/output/survey_cleaned.csv` is created
   - `/app/output/amazon-purchases-2019-2020-filtered.csv` is created

2. **Survey cleaned data meets quality requirements**:
   - Contains "Survey ResponseID" column with unique values
   - All Survey ResponseID values start with "R_" prefix
   - Zero duplicate rows
   - Demographic columns (Q-demos-age, Q-demos-race, Q-demos-education, Q-demos-income, Q-demos-gender) have zero missing values
   - Row count is between 4500-5500 (allows for reasonable duplicate removal)
   - All rows have non-null Survey ResponseID

3. **Purchase cleaned data meets quality requirements**:
   - Contains required columns: "Survey ResponseID", "Order Date", "Category"
   - Contains one price column (accepting flexible naming: "Item Total", "Total Price", "Purchase Price Per Unit", or variants)
   - Zero missing values in Category column
   - Zero missing values in Survey ResponseID column
   - Order Date is parseable and all dates fall within 2019-2020 range
   - Price values are positive and below $10,000 (no extreme outliers)
   - Row count is between 200,000-500,000 (filtered to 2019-2020 and cleaned)

4. **Cross-dataset referential integrity**:
   - All Survey ResponseID values in purchase data exist in survey cleaned data
   - Or, purchase data is filtered to only include IDs present in cleaned survey

5. **Data is ready for downstream processing**:
   - No structural issues that would break pandas operations
   - Date columns are datetime type, not strings
   - Numeric columns are numeric type
   - No duplicate column names

## Failure Modes

Common ways execution can fail even with the right skill:

1. **Incomplete missing value handling**:
   - Imputing only some demographic columns but not others, leaving missing values that fail validation
   - Forgetting to check for nulls after text processing operations
   - Missing the need to impute vs drop based on column criticality

2. **Wrong deduplication logic**:
   - Removing duplicate transactions thinking they're errors (they're legitimate repeat purchases)
   - Not removing duplicate survey responses (should be one per respondent)
   - Using wrong subset of columns to define uniqueness

3. **Date parsing and filtering errors**:
   - Parsing dates but not filtering to 2019-2020 range, leaving out-of-scope data
   - Using wrong date format assumptions causing parse failures
   - Not handling edge cases like Feb 29 in leap year 2020

4. **Referential integrity breaks**:
   - Cleaning datasets independently without checking ID overlap
   - Over-aggressive survey cleaning that removes IDs present in transactions
   - Forgetting to filter transactions to only include users in cleaned survey

5. **Outlier handling mistakes**:
   - Removing too many price outliers, dropping below minimum row count
   - Not capping outliers, leaving extreme values that distort downstream analysis
   - Using wrong IQR multiplier (too aggressive or too lenient)

6. **Column naming inconsistencies**:
   - Not standardizing column names after cleaning
   - Creating new column names that tests don't recognize
   - Losing required columns during merge or drop operations

7. **Partial completion presented as done**:
   - Cleaning only one dataset and stopping
   - Saving intermediate files without final validation
   - Not verifying both output files exist before reporting completion

8. **File I/O errors**:
   - Wrong output path (not using `/app/output/`)
   - Wrong output filenames (not matching expected names exactly)
   - Forgetting to actually save files after cleaning in memory

9. **Sample size disasters**:
   - Over-aggressive filtering reduces survey below 4500 rows
   - Over-aggressive filtering reduces purchases below 200,000 rows
   - Cascading drops (missing values + outliers + date filter) compound to excessive loss

## Evaluator Hooks

The benchmark evaluator will check these output-contract surfaces:

1. **File existence** (P0 - critical):
   - `/app/output/survey_cleaned.csv` must exist
   - `/app/output/amazon-purchases-2019-2020-filtered.csv` must exist

2. **File parseability** (P0 - critical):
   - Both files must be valid CSV format
   - pandas can read both files without errors

3. **Required columns present** (P0 - critical):
   - Survey: "Survey ResponseID" column exists
   - Purchase: "Survey ResponseID", "Order Date", "Category" columns exist
   - Purchase: At least one price column with recognized name (accepts multiple variants: "Item Total", "Total Price", "item_total", "total_price", "Purchase Price Per Unit", "purchase_price_per_unit")

4. **Minimum row counts** (P0 - critical):
   - Survey: at least 1000 rows (target: 4500-5500)
   - Purchase: at least 10,000 rows (target: 200,000-500,000)

5. **Uniqueness constraints** (P0 - critical):
   - Survey ResponseID must be unique in survey_cleaned.csv (no duplicates)

6. **Data quality validations** (P1 - important):
   - Survey ResponseID format: all values start with "R_"
   - Zero duplicate rows in survey data
   - Zero missing values in survey demographic columns (complete imputation)
   - Date column is parseable and within 2019-2020 range
   - Zero missing values in Category column
   - Price values are positive and below $10,000
   - Expected row count ranges (not just minimums)

7. **Cross-file consistency** (P2 - advanced):
   - Survey ResponseID values in purchase data must exist in survey data
   - Or equivalently: purchase data filtered to only include survey-linked users

8. **Numeric type constraints** (implicit):
   - Price columns must be numeric type (not string)
   - No infinite values in numeric columns
   - Reasonable value ranges (checked via z-score or percentile bounds in tests)

9. **Schema stability**:
   - Column names are consistent and recognizable
   - No extra unexpected columns that suggest data corruption
   - Original column semantics preserved (e.g., Category still means product category)

10. **Date handling precision**:
    - Date filtering is inclusive of boundary dates (2019-01-01 through 2020-12-31)
    - Date parsing preserves day-level granularity (not rounded to months)
