---
skillx:
  name: time_series_anomaly_detection
  purpose: Detect anomalous trends in time series data by category using counterfactual prediction with Facebook Prophet, then perform causal inference to identify demographic drivers of the anomalies
  scope_in:
    - Time series anomaly detection using Prophet for trend/seasonality modeling
    - Anomaly index calculation (scaled -100 to 100) to rank categories by deviation from expected trend
    - Data cleaning and preparation for transactional and demographic datasets
    - Feature engineering on demographic data for causal analysis
    - Difference-in-differences (DiD) analysis to identify demographic drivers of anomalies
    - Both intensive margin (spending among purchasers) and extensive margin (purchase propensity) analysis
  scope_out:
    - Not a general-purpose forecasting tool - focuses on anomaly detection and ranking
    - Not for real-time detection - works with historical data for post-hoc analysis
    - Does not provide business recommendations - only quantifies anomalies and identifies correlates
    - Does not handle complex multivariate time series - analyzes univariate series per category
  requires:
    - Python with pandas, numpy, fbprophet/prophet
    - Statsmodels or similar for DiD regression analysis
    - Clean transaction data with date, category, and value columns
    - Demographic/feature data linkable to transactions via user ID
    - Sufficient historical data per category (typically 180+ days recommended for Prophet)
  preferred_tools:
    - pandas for data manipulation and aggregation
    - Prophet for time series modeling and counterfactual prediction
    - Statistical libraries (statsmodels, scipy) for DiD analysis
    - Data cleaning: dropna, drop_duplicates, type conversion, outlier handling
  risks:
    - Prophet requires sufficient training data - categories with sparse history should be filtered
    - Anomaly detection is sensitive to confidence interval width and prior scales
    - Counterfactual prediction assumes stationarity in underlying trend/seasonality patterns
    - DiD assumes parallel trends - verify baseline trends are comparable before interpretation
    - Feature engineering quality directly impacts causal analysis validity
    - Aggregation to user-category-period level is critical for DiD independence assumptions
  examples:
    - "Analyze e-commerce transaction data to identify which product categories showed unusual sales patterns in March 2020 compared to historical trends, then determine what customer demographics explain these anomalies"
    - "Detect spending surges and slumps across product categories during an intervention period using Prophet-based anomaly detection, followed by DiD analysis to isolate demographic drivers"

# Guidance

## Core Workflow

This task combines time series anomaly detection with causal inference:

1. **Data Preparation**: Clean transactional and demographic datasets - handle duplicates, missing values, type inconsistencies, and outliers
2. **Anomaly Detection**: Use Prophet to model historical trends per category and identify deviations during the target period
3. **Feature Engineering**: Transform demographic data into numeric features suitable for regression analysis
4. **Causal Analysis**: Run DiD on top anomalous categories to identify demographic factors associated with spending changes

## Time Series Anomaly Detection with Prophet

**Purpose**: Generate counterfactual predictions for each category to measure how much actual values deviate from expected trends.

**Implementation approach**:
- Aggregate transaction data to daily category-level time series
- Split data into training (historical) and prediction (target anomaly window) periods
- Fit Prophet model per category using training data
- Generate predictions for the target period
- Calculate anomaly index based on deviation from confidence intervals

**Anomaly Index Calculation** (CRITICAL):
- If actual value is within confidence interval: Index = 0
- If above upper bound: raw_index = (actual - upper) / std
- If below lower bound: raw_index = (actual - lower) / std
- Scaled Index = 100 × tanh(raw_index) → bounded to [-100, 100]
  - This scaling maps: 1σ → ~76 points, 2σ → ~96 points, 3σ → ~99.5 points

**Key Prophet parameters**:
- `min_training_days`: Minimum historical days required per category (e.g., 180) - filter out categories below threshold
- `confidence_interval`: Width for anomaly detection (0.68 = ±1σ recommended for interpretability)
- `changepoint_prior_scale`: Trend flexibility (0.05 default, increase to 0.1 for smaller datasets)
- `seasonality_prior_scale`: Seasonality strength (10.0 default)

**Required inputs**:
- `date_col`: Temporal dimension column name
- `category_col`: Grouping dimension (e.g., product category)
- `value_col`: Metric to analyze (e.g., price, revenue)
- `cutoff_date`: Training/prediction split date (YYYY-MM-DD format)
- `prediction_end`: End of anomaly detection window
- `agg_func`: Aggregation method ('sum', 'mean', 'count', or None if pre-aggregated)

**Expected output structure**:
- DataFrame sorted by Anomaly_Index (descending)
- Columns: category name, Anomaly_Index, summary statistics (days_with_data, avg_daily_anomaly, total_actual, total_predicted)
- Index range: [-100, 100] with both positive (surge) and negative (slump) values

## Feature Engineering for Causal Analysis

Transform demographic/survey data into numeric features for regression:
- One-hot encode categorical variables (age groups, education levels, income brackets, etc.)
- Create binary indicators for demographic attributes
- Ensure all output features are numeric (required for downstream DiD analysis)
- Handle missing values appropriately (imputation or indicators)
- Maintain user ID as the key for merging with transaction data

Output should have one row per user with all demographic features as columns.

## Difference-in-Differences Analysis

**Purpose**: Identify demographic features that best explain anomalous spending patterns by comparing treatment vs baseline periods.

**Data structure requirements**:
- **Intensive margin** (spending analysis): User-category-period aggregated spending, ONLY for users who made purchases
- **Extensive margin** (purchase propensity): User-category-period with binary purchase indicator (0/1), for ALL users

**Critical aggregation**:
- Aggregate to user-category-period level to ensure independence for regression
- Each observation should be unique on (user_id, category, period)
- Period should be labeled (e.g., "baseline" vs "treatment")

**DiD estimation approach**:
- For each category and each demographic feature, estimate: Y = β₀ + β₁·Treatment + β₂·Feature + β₃·(Treatment × Feature) + ε
- The interaction coefficient β₃ is the DiD estimate - measures differential effect of the feature in treatment vs baseline
- Run separately for intensive margin (spending) and extensive margin (purchase indicator)

**Method selection**:
- Univariate DiD: Simpler, one feature at a time, easier to interpret
- Multivariate heterogeneous DiD: Multiple features simultaneously, controls for confounding, requires sufficient sample size

**Output requirements**:
- For each category (top 10 surge + top 10 slump), report top 3 drivers for each margin
- Intensive margin: Sorted by did_estimate (descending for surge, ascending for slump) - shows which features correlate with largest spending changes
- Extensive margin: Sorted by did_estimate (descending for surge, ascending for slump) - shows which features correlate with purchase rate changes
- Each driver: feature name, did_estimate, p_value, method
- Include descriptive statistics: baseline/treatment average spend, purchaser counts, purchase rates, sample size

## Data Quality Considerations

**Survey/demographic data**:
- Remove duplicates on user ID
- Verify user IDs follow expected format
- Impute or handle missing demographic values before feature engineering
- Ensure demographic columns have no nulls after cleaning

**Transaction data**:
- Parse and validate dates - filter to relevant time range
- Remove rows with missing categories or invalid prices
- Handle outliers in price/quantity (cap or remove extreme values)
- Ensure positive prices and reasonable ranges
- Link to survey data via user ID (inner join to keep only matched users)

**Period definitions**:
- Baseline period: Define clearly (e.g., Jan-Feb of target year)
- Treatment period: Define clearly (e.g., March of target year)
- Ensure periods are contiguous and don't overlap
- Label periods consistently across all datasets

# Notes for Agent

When executing this task:

1. **Read and understand the full task requirements first** - you need to produce multiple interdependent outputs with specific formats

2. **Data cleaning is foundational** - invest time upfront to handle dirty data properly. Both datasets likely have issues that will break downstream analysis if not addressed.

3. **Prophet anomaly detection workflow**:
   - Aggregate transaction data to daily category level BEFORE modeling
   - Use historical data (before cutoff) to train Prophet models
   - Generate counterfactual predictions for the target period
   - Calculate anomaly indices using the tanh-scaled formula from the original methodology
   - Sort final output by anomaly index descending (highest surge to lowest slump)

4. **Feature engineering must produce numeric features** - the tests verify this explicitly. All demographic attributes should be converted to numbers (one-hot encoding, binary indicators, etc.)

5. **DiD analysis aggregation is critical**:
   - Intensive margin: Filter to ONLY purchasers, aggregate spending per user-category-period
   - Extensive margin: Include ALL users, create binary purchase indicator per user-category-period
   - Both must be aggregated to user-category-period level (no duplicate user-category-period combinations)
   - Apply the survey merge (inner join) BEFORE aggregation to ensure consistency

6. **Top 10 surge and top 10 slump selection**:
   - Take the 10 highest anomaly indices (surge)
   - Take the 10 lowest anomaly indices (slump)
   - Run DiD analysis only on these 20 categories
   - Sorting direction for drivers matters: descending for surge (largest positive effects first), ascending for slump (largest negative effects first)

7. **Period definitions from the tests**:
   - Baseline is Jan-Feb 2020 (not 2019!)
   - Treatment is March 2020
   - Filter transaction data to this window for DiD analysis

8. **Output file format compliance**:
   - CSV files: Follow exact column name requirements (or acceptable aliases from tests)
   - JSON file: Follow exact structure from instruction.md schema
   - Ensure all required fields are present and correctly formatted
   - Anomaly index file must be sorted descending by anomaly index

9. **Statistical validity**:
   - Ensure sufficient categories are modeled (at least 20 to select top 10 surge + top 10 slump)
   - Verify anomaly distribution makes sense (not all extreme values)
   - Check that DiD results have reasonable p-value distributions
   - Validate that effect sizes have both positive and negative values

10. **Common pitfalls to avoid**:
    - Don't use 2019 data as the baseline for DiD - use Jan-Feb 2020
    - Don't forget to filter out categories with insufficient training data
    - Don't create duplicate user-category-period rows in aggregated data
    - Don't forget to merge with survey data before final aggregations
    - Don't forget to sort anomaly indices descending and DiD drivers by magnitude (direction depends on surge vs slump)
