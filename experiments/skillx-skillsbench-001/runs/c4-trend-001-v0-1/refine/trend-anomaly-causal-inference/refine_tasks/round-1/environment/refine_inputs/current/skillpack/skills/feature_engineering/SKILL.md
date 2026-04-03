---
skillx.name: feature_engineering
skillx.purpose: Engineer numeric features from survey demographic data for causal inference analysis (DiD)
skillx.scope_in:
  - Engineering features from cleaned survey demographic data for downstream causal analysis
  - Converting categorical demographics (education, race, income, age, gender) to numeric representations
  - Creating derived features from demographic variables
  - Validating all outputs are numeric and suitable for regression-based analysis
skillx.scope_out:
  - Not for raw data cleaning or imputation (data should already be cleaned)
  - Not for time-series or sequential feature engineering
  - Not for unstructured data (text, images)
  - Not for feature engineering from transaction/purchase data (separate pipeline)
skillx.requires:
  - Cleaned survey data with demographic columns and Survey ResponseID
  - Understanding of demographic variable types (binary, categorical, ordinal, numeric)
  - pandas for data manipulation
  - scikit-learn preprocessing utilities (OneHotEncoder, LabelEncoder, StandardScaler)
  - Downstream causal analysis requires numeric-only feature matrix
skillx.preferred_tools:
  - pandas for DataFrame operations and type checking
  - scikit-learn.preprocessing for encoding (OneHotEncoder, LabelEncoder) and scaling (StandardScaler, MinMaxScaler)
  - Pipeline or sequential transformation pattern for reproducibility
skillx.risks:
  - Non-numeric features will break downstream DiD regression analysis
  - High-cardinality categorical encoding can create excessive dimensions
  - Constant or near-constant features provide no analytical value
  - Incomplete encoding leaves string/object columns that cause analysis failures
skillx.examples:
  - Convert binary survey responses (Yes/No, True/False) to 0/1 integers
  - One-hot encode nominal categories (race, education level) creating binary dummy variables
  - Label encode ordinal categories (income brackets, age ranges) preserving order
  - Standardize numeric features if needed for model stability
  - Validate output: df.select_dtypes(include='number') should contain all columns except ID
---

# Guidance

Your task is to engineer numeric features from cleaned survey demographic data that will be used in causal inference analysis (Difference-in-Differences).

## Step 1: Inspect Survey Data Structure

Read the cleaned survey data and examine:
- Column names and data types (df.dtypes)
- Sample values (df.head()) to understand actual content
- Identify: Survey ResponseID (identifier), demographic columns (features)
- Check for demographic variables like age, race, education, income, gender

## Step 2: Categorize Features by Type

Group demographic columns into:
- **Binary features**: Yes/No, True/False, binary responses → convert to 0/1
- **Nominal categorical**: Race, education level (no natural order) → one-hot encode
- **Ordinal categorical**: Income brackets, age ranges (natural order) → label/ordinal encode
- **Numeric features**: Already numeric values → may need scaling if used directly

## Step 3: Apply Feature Engineering Transformations

### Convert Binary Features
- Transform Yes/No, True/False to 0/1 integers
- Ensure output dtype is int, not bool or string

### Encode Categorical Features
- **Low cardinality (<10 categories)**: Use one-hot encoding (creates binary columns per category)
- **Medium cardinality (10-50 categories)**: Use label encoding or frequency encoding
- **High cardinality (>50 categories)**: Consider hashing or dropping if not informative

### Handle Ordinal Features
- For ordered categories (income: low<medium<high), use ordinal encoding preserving order
- Map to integers: low=0, medium=1, high=2

### Optional: Create Interaction or Derived Features
- If domain knowledge suggests interactions (e.g., age×income), create them
- Keep feature count reasonable to avoid dimensionality issues

## Step 4: Validate Output Requirements

Critical validation before saving:

```python
# All columns except ID must be numeric
feature_cols = [c for c in df.columns if c != 'Survey ResponseID']
non_numeric = [c for c in feature_cols if df[c].dtype not in ['int64', 'float64']]
assert len(non_numeric) == 0, f"Non-numeric columns found: {non_numeric}"

# Check for constant features (no variance)
for col in feature_cols:
    if df[col].nunique() == 1:
        print(f"Warning: {col} is constant, consider removing")

# Verify reasonable feature count
print(f"Total engineered features: {len(feature_cols)}")
```

## Step 5: Save Engineered Features

Output format: CSV with columns [Survey ResponseID, FEATURE1, FEATURE2, ..., FEATUREn]
- Keep Survey ResponseID as identifier (not encoded)
- All other columns are numeric features
- Save to specified output path

# Notes for Agent

**Critical Requirements:**

1. **ALL engineered features MUST be numeric (int or float)**
   - No string, object, or boolean dtypes allowed (except Survey ResponseID)
   - Downstream DiD analysis uses these features in regression and cannot handle non-numeric types
   - Validate with: `df.select_dtypes(include='number').shape[1] == df.shape[1] - 1`

2. **Complete categorical encoding**
   - Every categorical column must be converted to numbers
   - Common demographics that need encoding: race, education, income, age_range, gender
   - Do not leave any string columns in the output

3. **Feature validation checklist**
   - No missing values (imputation should be complete before feature engineering)
   - No constant columns (all features should have variance)
   - No extreme outliers or infinite values
   - Reasonable feature count (at least 20 features expected for demographic data)

4. **Use pipeline pattern for reproducibility**
   - Create a sequence of transformation steps
   - Document which encoding method was used for which columns
   - Keep track of engineered feature names

5. **Preserve data integrity**
   - Same number of rows as input (no dropping)
   - Survey ResponseID must match the cleaned survey data exactly
   - One-to-one mapping: each survey respondent gets one row of features

**Implementation approach:**

```python
# Typical workflow
df = pd.read_csv('survey_cleaned.csv')

# 1. Separate ID from features
response_id = df['Survey ResponseID']
demo_features = df.drop('Survey ResponseID', axis=1)

# 2. Identify and convert binary features
binary_cols = ['col1', 'col2']  # Replace with actual binary columns
for col in binary_cols:
    demo_features[col] = demo_features[col].map({'Yes': 1, 'No': 0})

# 3. One-hot encode nominal categoricals
nominal_cols = ['race', 'education']  # Replace with actual columns
demo_features = pd.get_dummies(demo_features, columns=nominal_cols, drop_first=False)

# 4. Label encode ordinals if needed
from sklearn.preprocessing import LabelEncoder
ordinal_cols = ['income_bracket']  # Replace with actual columns
for col in ordinal_cols:
    le = LabelEncoder()
    demo_features[col] = le.fit_transform(demo_features[col])

# 5. Validate all numeric
assert demo_features.select_dtypes(include='number').shape == demo_features.shape

# 6. Combine and save
output_df = pd.concat([response_id, demo_features], axis=1)
output_df.to_csv('survey_feature_engineered.csv', index=False)
```

**Common pitfalls to avoid:**

- Forgetting to encode a categorical column (leaves strings in output)
- Using boolean dtype instead of int (convert with .astype(int))
- Creating too many dummy variables from high-cardinality features
- Not validating output before saving
- Dropping rows during encoding (breaks alignment with other datasets)

# Derived Execution Layer

## Preconditions

The following conditions must be satisfied before executing this skill:

1. **Input data availability**
   - Cleaned survey data file exists at specified input path
   - File is in CSV format and readable by pandas
   - File is not empty and has valid structure

2. **Data cleaning completed**
   - Duplicate rows have been removed
   - Missing values in demographic columns have been handled (imputed or removed)
   - Data types are consistent within columns
   - No corrupt or malformed records

3. **Required columns present**
   - `Survey ResponseID` column exists and is unique (serves as primary key)
   - Demographic feature columns exist (e.g., Q-demos-age, Q-demos-race, Q-demos-education, Q-demos-income, Q-demos-gender)
   - Column names are consistent and recognizable

4. **Upstream dependencies satisfied**
   - Data cleaning skill has completed successfully
   - Survey data has been validated for structural integrity
   - No blockers from data preprocessing stage

5. **Environment requirements**
   - pandas library available for data manipulation
   - scikit-learn library available for encoding utilities
   - Sufficient memory to load and transform the dataset

## Postconditions

The following conditions must be true after successful execution:

1. **Output file created**
   - File `survey_feature_engineered.csv` exists at specified output path (typically `/app/output/`)
   - File is valid CSV format and loadable by pandas
   - File permissions allow reading by downstream processes

2. **Required columns present**
   - `Survey ResponseID` column exists with exact name match (case-sensitive)
   - Column is preserved from input without modification
   - All Survey ResponseID values from input are present in output

3. **All features are numeric** (CRITICAL)
   - Every column except `Survey ResponseID` has numeric dtype (int64, float64, int32, float32)
   - No string, object, or boolean dtypes in feature columns
   - Validation: `pd.api.types.is_numeric_dtype(df[col])` returns True for all feature columns

4. **Feature count requirement met**
   - At least 20 engineered features present (excluding Survey ResponseID)
   - Sufficient feature expansion from demographic variables
   - Feature count is reasonable (not excessive dimensionality)

5. **Row count preserved**
   - Output has same number of rows as input cleaned survey data
   - No rows dropped during transformation
   - One-to-one mapping maintained for join with other datasets

6. **Data quality standards met**
   - No constant features (all columns have > 1 unique value)
   - No infinite values (inf, -inf) in any feature
   - No extreme outliers (> 10 standard deviations from mean in > 1% of rows)
   - At least 95% of features have meaningful variance (std > 0.01)
   - No missing values in engineered features

7. **Ready for downstream analysis**
   - Features are in format suitable for DiD regression
   - Data can be merged with transaction data on Survey ResponseID
   - Feature matrix is ready for causal inference analysis

## Failure Modes

Common failure patterns and their causes:

1. **Incomplete categorical encoding** (MOST COMMON)
   - **Symptom**: String/object dtype columns remain in output
   - **Cause**: Forgetting to encode one or more demographic columns (race, education, income, etc.)
   - **Detection**: Type checking fails, downstream analysis crashes with "could not convert string to float"
   - **Prevention**: Explicit validation that all non-ID columns are numeric before saving

2. **Boolean dtype not converted to int**
   - **Symptom**: Boolean columns present in output instead of 0/1 integers
   - **Cause**: Using boolean output from comparisons or map operations without .astype(int)
   - **Detection**: Numeric type check may pass (bool is numeric) but some systems reject boolean types
   - **Prevention**: Explicitly convert boolean columns to int: `df[col].astype(int)`

3. **Row count mismatch**
   - **Symptom**: Output has fewer rows than input cleaned survey data
   - **Cause**: Encoding methods dropping rows with unknown categories, or filtering during transformation
   - **Detection**: Row count comparison fails, IDs missing in output
   - **Impact**: Cannot join with other datasets, breaks data pipeline alignment
   - **Prevention**: Use encoding methods that preserve all rows, avoid filtering operations

4. **Insufficient feature count**
   - **Symptom**: Output has fewer than 20 features
   - **Cause**: Not applying one-hot encoding to categorical variables, dropping too many features
   - **Detection**: Feature count check fails
   - **Impact**: Insufficient information for downstream causal analysis
   - **Prevention**: Verify feature expansion from categoricals, check feature count before saving

5. **Constant features present**
   - **Symptom**: Some features have only one unique value (no variance)
   - **Cause**: Demographic variable has only one value after cleaning, or encoding error
   - **Detection**: Variance check fails, downstream models may crash or ignore features
   - **Impact**: Wastes dimensionality, no analytical value
   - **Prevention**: Check for constant features and remove before saving

6. **Survey ResponseID corruption**
   - **Symptom**: Survey ResponseID modified, lost, or duplicated during transformation
   - **Cause**: Including ID column in encoding operations, not separating ID before transformation
   - **Detection**: ID validation fails, cannot join with other datasets
   - **Impact**: Data pipeline breaks, cannot link features to survey respondents
   - **Prevention**: Separate Survey ResponseID before encoding, verify ID integrity after transformation

7. **Extreme or infinite values**
   - **Symptom**: Features contain inf, -inf, or extreme outliers
   - **Cause**: Division by zero, log of negative numbers, or improper scaling
   - **Detection**: Infinite value check fails, statistical tests produce NaN
   - **Impact**: Downstream regression analysis fails or produces invalid results
   - **Prevention**: Check for infinities after transformations, handle edge cases in derived features

8. **High-cardinality explosion**
   - **Symptom**: Hundreds or thousands of features created from one-hot encoding
   - **Cause**: Applying one-hot encoding to high-cardinality categorical (e.g., zip codes, unique IDs)
   - **Detection**: Feature count exceeds reasonable limit (e.g., > 500 features)
   - **Impact**: Curse of dimensionality, memory issues, slow downstream analysis
   - **Prevention**: Use label/hash encoding for high-cardinality features, check cardinality before one-hot encoding

9. **Missing final validation**
   - **Symptom**: Output file created but fails quality checks
   - **Cause**: Skipping validation step before saving output
   - **Detection**: Downstream tests fail
   - **Impact**: Wasted computation, need to rerun entire pipeline
   - **Prevention**: Always run comprehensive validation before saving output file

## Evaluator Hooks

The benchmark evaluator checks these output contract surfaces:

### P0: Core Functionality (50% weight)

1. **File existence check**
   - File `survey_feature_engineered.csv` must exist at output directory
   - Path: `/app/output/survey_feature_engineered.csv`

2. **Required column: Survey ResponseID**
   - Column name must be exactly `Survey ResponseID` (case-sensitive)
   - Column must be present in output DataFrame

3. **Numeric dtype enforcement** (CRITICAL - most common failure)
   - ALL columns except `Survey ResponseID` must be numeric
   - Test checks: `pd.api.types.is_numeric_dtype(df[col])` for each feature column
   - Failure message: "Feature '{col}' is not numeric (dtype: {df[col].dtype}) - all features must be numeric for downstream analysis"
   - This is the primary test failure point

4. **Minimum feature count**
   - At least 20 features required (excluding Survey ResponseID)
   - Test checks: `len(df.columns) - 1 >= 20`
   - Failure message: "Expected ≥20 features, got {n_features}"

### P1: Quality & Correctness (35% weight)

5. **Row count preservation**
   - Output must have same number of rows as input `survey_cleaned.csv`
   - Test checks: `len(fe_df) == len(survey_df)`
   - Failure message: "Feature engineered data has {len(fe_df)} rows, survey has {len(survey_df)}"

6. **No constant features**
   - All features must have more than 1 unique value
   - Test checks: `df[col].nunique() > 1` for each feature column
   - Failure message: "Feature '{col}' is constant (only {n_unique} unique value)"

7. **No infinite values**
   - Features cannot contain inf or -inf
   - Test checks: `not df[col].isin([float('inf'), float('-inf')]).any()`
   - Failure message: "Feature '{col}' contains infinite values"

8. **No extreme outliers**
   - Values should not exceed 10 standard deviations from mean for more than 1% of rows
   - Test checks: `outliers < len(fe_df) * 0.01` where outliers are > 10σ from mean
   - Failure message: "Feature '{col}' has {outliers} extreme outliers (>10σ)"

9. **Meaningful variance distribution**
   - At least 95% of features should have standard deviation > 0.01
   - Test checks: `sum(fe_df[col].std() > 0.01 for col in feature_cols) >= len(feature_cols) * 0.95`
   - Failure message: "Only {non_zero_variance}/{len(feature_cols)} features have meaningful variance (expected ≥95%)"

### P2: Cross-file Consistency (15% weight)

10. **Survey ResponseID integrity**
    - Set of Survey ResponseID values in output must exactly match input survey data
    - Test checks: `set(fe_df['Survey ResponseID']) == set(survey_df['Survey ResponseID'])`
    - Used for cross-file consistency validation

### Key Evaluator Expectations

- **Parseability**: Output must be valid CSV loadable by `pd.read_csv()`
- **Schema shape**: Single-table format with ID column + numeric feature columns
- **No missing data**: Engineered features should not have NaN values (imputation should be complete)
- **Numeric format**: int64 or float64 dtypes, not object, string, or bool
- **Feature naming**: Feature column names can be anything (no specific naming convention enforced)
- **Feature ordering**: No specific column order required (except Survey ResponseID should be present)

### Common Test Failures

1. **Non-numeric features** (most common): Forgetting to encode categorical columns
2. **Insufficient features**: Not expanding categoricals via one-hot encoding
3. **Row count mismatch**: Dropping rows during transformation
4. **Constant features**: Not removing zero-variance columns
5. **Missing validation**: Skipping final dtype/quality checks before saving
