---
skillx.name: feature_engineering
skillx.purpose: Engineer numeric features from survey demographic data for causal inference analysis (DiD)
skillx.scope_in:
  - Engineering features from cleaned survey demographic data
  - Converting categorical demographics (education, race, income, age, gender) to numeric representations
  - Creating derived features from demographic variables
  - Validating all outputs are numeric and suitable for regression
skillx.scope_out:
  - Raw data cleaning or imputation (data should already be cleaned)
  - Time-series or sequential feature engineering
  - Unstructured data (text, images)
  - Feature engineering from transaction/purchase data
skillx.requires:
  - Cleaned survey data with demographic columns and Survey ResponseID
  - Understanding of demographic variable types (binary, categorical, ordinal, numeric)
  - pandas for data manipulation
  - scikit-learn preprocessing utilities (OneHotEncoder, LabelEncoder, StandardScaler)
skillx.preferred_tools:
  - pandas for DataFrame operations and type checking
  - scikit-learn.preprocessing for encoding and scaling
  - Pipeline or sequential transformation pattern for reproducibility
skillx.risks:
  - Non-numeric features break downstream DiD regression
  - High-cardinality categorical encoding creates excessive dimensions
  - Constant or near-constant features provide no analytical value
  - Incomplete encoding leaves string/object columns that cause failures
skillx.examples:
  - Convert binary survey responses (Yes/No, True/False) to 0/1 integers
  - One-hot encode nominal categories (race, education) creating binary dummies
  - Label encode ordinal categories (income brackets, age ranges) preserving order
  - Validate output: df.select_dtypes(include='number') should contain all non-ID columns
---

# Guidance

## Workflow

1. **Inspect Survey Data**: Examine column names, data types, and sample values to identify Survey ResponseID and demographic columns

2. **Categorize Features by Type**:
   - Binary: Yes/No, True/False → convert to 0/1
   - Nominal categorical: Race, education (no natural order) → one-hot encode
   - Ordinal categorical: Income brackets, age ranges → label/ordinal encode
   - Numeric: Already numeric → may need scaling if used directly

3. **Apply Transformations**:
   - **Low cardinality (<10 categories)**: One-hot encoding
   - **Medium cardinality (10-50)**: Label encoding or frequency encoding
   - **High cardinality (>50)**: Consider hashing or dropping
   - For ordered categories, use ordinal encoding preserving order

4. **Validate Output Requirements**:
   ```python
   # All columns except ID must be numeric
   feature_cols = [c for c in df.columns if c != 'Survey ResponseID']
   non_numeric = [c for c in feature_cols if df[c].dtype not in ['int64', 'float64']]
   assert len(non_numeric) == 0, f"Non-numeric columns: {non_numeric}"

   # Check for constant features
   for col in feature_cols:
       if df[col].nunique() == 1:
           print(f"Warning: {col} is constant, consider removing")
   ```

5. **Save Output**: CSV with [Survey ResponseID, FEATURE1, FEATURE2, ..., FEATUREn], all features numeric

## Critical Requirements

1. **ALL features MUST be numeric (int or float)** - No string, object, or boolean dtypes (except Survey ResponseID). Validate: `df.select_dtypes(include='number').shape[1] == df.shape[1] - 1`

2. **Complete categorical encoding** - Every categorical column must be converted. Do not leave string columns in output

3. **Feature validation checklist**:
   - No missing values
   - No constant columns (all features have variance)
   - No infinite values
   - Reasonable feature count (at least 20 expected)

4. **Preserve data integrity**:
   - Same number of rows as input
   - Survey ResponseID matches cleaned survey exactly
   - One-to-one mapping per respondent

## Implementation Approach

```python
df = pd.read_csv('survey_cleaned.csv')

# 1. Separate ID from features
response_id = df['Survey ResponseID']
demo_features = df.drop('Survey ResponseID', axis=1)

# 2. Convert binary features
binary_cols = ['col1', 'col2']
for col in binary_cols:
    demo_features[col] = demo_features[col].map({'Yes': 1, 'No': 0})

# 3. One-hot encode nominal categoricals
nominal_cols = ['race', 'education']
demo_features = pd.get_dummies(demo_features, columns=nominal_cols, drop_first=False)

# 4. Label encode ordinals
from sklearn.preprocessing import LabelEncoder
ordinal_cols = ['income_bracket']
for col in ordinal_cols:
    le = LabelEncoder()
    demo_features[col] = le.fit_transform(demo_features[col])

# 5. Validate all numeric
assert demo_features.select_dtypes(include='number').shape == demo_features.shape

# 6. Combine and save
output_df = pd.concat([response_id, demo_features], axis=1)
output_df.to_csv('survey_feature_engineered.csv', index=False)
```

# Derived Execution Layer

## Key Requirements Before Execution

- Cleaned survey data file exists and is readable
- Data cleaning completed (no duplicates, no missing values in demographics)
- Survey ResponseID column exists and is unique
- pandas and scikit-learn libraries available

## Expected Outputs After Completion

- `survey_feature_engineered.csv` exists at output path
- Survey ResponseID column preserved with all values from input
- **ALL non-ID columns are numeric** (int64, float64) - MOST CRITICAL CHECK
- At least 20 engineered features present
- Same row count as input
- No constant features, no infinite values

## High-Impact Failure Modes to Avoid

1. **Incomplete categorical encoding** (MOST COMMON): Forgetting to encode demographic columns, leaving strings in output
2. **Boolean dtype not converted**: Using boolean output without .astype(int) conversion
3. **Row count mismatch**: Encoding methods dropping rows
