---
skillx:
  name: time_series_anomaly_detection
  purpose: Detect anomalous trends in time series data by category using counterfactual prediction with Facebook Prophet
  scope_in:
    - Time series anomaly detection using Prophet for trend/seasonality modeling
    - Anomaly index calculation (scaled -100 to 100) to rank categories by deviation
    - Counterfactual prediction to identify spending surges and slumps
  scope_out:
    - Not general-purpose forecasting - focuses on anomaly detection and ranking
    - Not real-time detection - works with historical data for post-hoc analysis
    - Does not handle complex multivariate time series
  requires:
    - Python with pandas, numpy, fbprophet/prophet
    - Clean transaction data with date, category, and value columns
    - Sufficient historical data per category (180+ days recommended)
  preferred_tools:
    - pandas for data manipulation and aggregation
    - Prophet for time series modeling and counterfactual prediction
    - Data cleaning: dropna, drop_duplicates, type conversion, outlier handling
  risks:
    - Prophet requires sufficient training data - filter sparse categories
    - Anomaly detection sensitive to confidence interval width and prior scales
    - Counterfactual assumes stationarity in trend/seasonality patterns
  examples:
    - "Identify product categories with unusual sales in March 2020 vs historical trends"
    - "Detect spending surges and slumps during intervention period using Prophet"

# Guidance

## Core Workflow

1. **Aggregate to Time Series**: Convert transaction data to daily category-level time series
2. **Split Data**: Training (historical) vs prediction (target anomaly window)
3. **Fit Prophet Models**: Per category using training data
4. **Generate Predictions**: For target period
5. **Calculate Anomaly Index**: Based on deviation from confidence intervals

## Anomaly Index Calculation (CRITICAL)

- If actual value within confidence interval: Index = 0
- If above upper bound: raw_index = (actual - upper) / std
- If below lower bound: raw_index = (actual - lower) / std
- Scaled Index = 100 × tanh(raw_index) → bounded to [-100, 100]
  - 1σ → ~76 points, 2σ → ~96 points, 3σ → ~99.5 points

## Key Prophet Parameters

- `min_training_days`: Minimum historical days required (e.g., 180) - filter out categories below threshold
- `confidence_interval`: Width for anomaly detection (0.68 = ±1σ recommended)
- `changepoint_prior_scale`: Trend flexibility (0.05 default, 0.1 for smaller datasets)
- `seasonality_prior_scale`: Seasonality strength (10.0 default)

## Required Inputs

- `date_col`: Temporal dimension column name
- `category_col`: Grouping dimension (e.g., product category)
- `value_col`: Metric to analyze (e.g., price, revenue)
- `cutoff_date`: Training/prediction split date (YYYY-MM-DD)
- `prediction_end`: End of anomaly detection window
- `agg_func`: Aggregation method ('sum', 'mean', 'count', or None if pre-aggregated)

## Expected Output Structure

- DataFrame sorted by Anomaly_Index descending
- Columns: category name, Anomaly_Index, summary statistics
- Index range: [-100, 100] with both positive (surge) and negative (slump) values
- At least 20 categories to support top-10 surge + top-10 slump selection

# Execution Notes

1. **Read task requirements fully** - need multiple interdependent outputs

2. **Aggregate BEFORE modeling** - transaction data to daily category level

3. **Prophet workflow**:
   - Use historical data (before cutoff) to train
   - Generate counterfactual predictions for target period
   - Calculate anomaly indices using tanh-scaled formula
   - Sort output by anomaly index descending

4. **Filter categories by training data**: Ensure minimum days threshold met

5. **Output requirements**:
   - CSV sorted descending by anomaly index
   - Both positive and negative anomalies present
   - At least 20 categories for downstream top-N selection

6. **Common pitfalls**:
   - Not filtering categories with insufficient training data
   - Using treatment period data in Prophet training (data leakage)
   - Wrong sorting direction (must be descending)

# Derived Execution Layer

## Key Requirements Before Execution

- Transaction data with date, category, price/value, and user ID columns
- Historical data spans at least 180 days before target window
- At least 20-30 categories expected to have adequate data
- Cutoff date for Prophet training/prediction split determined

## Expected Outputs After Completion

- `category_anomaly_index.csv` exists
- Sorted by Anomaly_Index in strict descending order
- All indices bounded within [-100, 100]
- Both positive (surge) and negative (slump) anomalies present
- At least 20 categories with valid indices

## High-Impact Failure Modes to Avoid

1. **Insufficient data filtering**: Not filtering categories by minimum training days, resulting in fewer than 20 categories
2. **Data leakage**: Using treatment period data in Prophet training
3. **Sorting errors**: Not sorting anomaly index descending
