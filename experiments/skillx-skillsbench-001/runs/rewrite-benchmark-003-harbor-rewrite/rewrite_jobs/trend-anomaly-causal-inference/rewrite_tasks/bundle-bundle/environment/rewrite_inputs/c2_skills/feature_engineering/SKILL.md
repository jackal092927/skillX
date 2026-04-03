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