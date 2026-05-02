[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: retrieval-heavy-synthesis
Semantic intent: Gather evidence from sources, compress it correctly, and synthesize an output without dropping support.
Emphasize:
- retrieval plan that explicitly identifies external sources and access paths before processing
- evidence tracking with explicit provenance chains linking each claim to its supporting external source
- compression that preserves source citations and provenance chains alongside synthesized output
- abstain / unknown behavior when evidence is insufficient
- external source grounding discipline - explicitly identify and track which external source (file, API, database, document) supports each claim
- explicit provenance chains - maintain traceable mappings from output claims back to specific input evidence locations
- multi-source reconciliation - handle conflicting or partial evidence across multiple external sources with explicit conflict resolution
Avoid:
- unsupported synthesis
- hallucinated joins across sources
- excessive workflow scaffolding that obscures evidence use
- treating staged data processing as retrieval-synthesis when the task does not require external source provenance tracking
Expected good fit:
- information search
- handbook / database grounded QA
- report or answer generation from external sources
- tasks requiring multi-source evidence reconciliation with explicit provenance tracking
Expected bad fit:
- simulator/control tasks
- code patch workflows
- staged multi-step data processing pipelines without explicit external source grounding requirements
- tasks where the primary challenge is workflow orchestration rather than evidence provenance discipline
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for a retrieval-heavy-synthesis task.
Schema intent: Gather evidence from sources, compress it correctly, and synthesize an output without dropping support.

Outer-loop update mode: differentiating. Keep the Render layer fixed and change only schema-level guidance.

Prioritize:
1. retrieval plan that explicitly identifies external sources and access paths before processing
2. evidence tracking with explicit provenance chains linking each claim to its supporting external source
3. compression that preserves source citations and provenance chains alongside synthesized output
4. abstain / unknown behavior when evidence is insufficient
5. external source grounding discipline - explicitly identify and track which external source (file, API, database, document) supports each claim
6. explicit provenance chains - maintain traceable mappings from output claims back to specific input evidence locations
7. multi-source reconciliation - handle conflicting or partial evidence across multiple external sources with explicit conflict resolution

Avoid:
1. unsupported synthesis
2. hallucinated joins across sources
3. excessive workflow scaffolding that obscures evidence use
4. treating staged data processing as retrieval-synthesis when the task does not require external source provenance tracking

Good fit when:
- information search
- handbook / database grounded QA
- report or answer generation from external sources
- tasks requiring multi-source evidence reconciliation with explicit provenance tracking

Bad fit when:
- simulator/control tasks
- code patch workflows
- staged multi-step data processing pipelines without explicit external source grounding requirements
- tasks where the primary challenge is workflow orchestration rather than evidence provenance discipline

Primary failure modes to guard against:
- boundary ambiguity with analytic-pipeline on tasks that process data but don't require external source provenance tracking
- schema assignment to pipeline-pattern tasks that lack load-bearing evidence grounding requirements

Regenerate task-specific skill guidance from these slots; do not invent a new policy outside them.

[Task context block]
Task name: econ-detrending-correlation
Task summary: In macroeconomics, understanding business cycle dynamics requires separating the trend component (long-term growth) from the cyclical component (short-term fluctuations) of economic time series. This task involves applying standard detrending techniques to analyze how consumption and investment move together over the business cycle. Goal: Calculate the Pearson correlation coefficient between the detrended real personal consumption expenditures (PCE) and the detrended real private fixed investment (PFI) for the years 1973 to 2024 (inclusive).
Task constraints:
- seed schema prior: analytic-pipeline
- verifier mode: deterministic-output-contract
- workflow topology: staged-multi-step
- tool surface regime: tool-heavy-script-optional
- primary pattern: pipeline
- annotation confidence: high
- secondary patterns: tool-wrapper, reviewer
Task output requirements:
- verifier note: deterministic-output-contract
- current skill count: 1

[Current Task skill block]
Current Task skill:
## timeseries-detrending
---
name: timeseries-detrending
description: Tools and techniques for detrending time series data in macroeconomic analysis. Use when working with economic time series that need to be decomposed into trend and cyclical components. Covers HP filter, log transformations for growth series, and correlation analysis of business cycles.
---

# Time Series Detrending for Macroeconomic Analysis

This skill provides guidance on decomposing economic time series into trend and cyclical components, a fundamental technique in business cycle analysis.

## Overview

Economic time series like GDP, consumption, and investment contain both long-term trends and short-term fluctuations (business cycles). Separating these components is essential for:
- Analyzing business cycle correlations
- Comparing volatility across variables
- Identifying leading/lagging indicators

## The Hodrick-Prescott (HP) Filter

The HP filter is the most widely used method for detrending macroeconomic data. It decomposes a time series into a trend component and a cyclical component.

### Mathematical Foundation

Given a time series $y_t$, the HP filter finds the trend $\tau_t$ that minimizes:

$$\sum_{t=1}^{T}(y_t - \tau_t)^2 + \lambda \sum_{t=2}^{T-1}[(\tau_{t+1} - \tau_t) - (\tau_t - \tau_{t-1})]^2$$

Where:
- First term: Minimizes deviation of data from trend
- Second term: Penalizes changes in the trend's growth rate
- $\lambda$: Smoothing parameter controlling the trade-off

### Choosing Lambda (λ)

**Critical**: The choice of λ depends on data frequency:

| Data Frequency | Recommended λ | Rationale |
|----------------|---------------|-----------|
| Annual         | **100**       | Standard for yearly data |
| Quarterly      | **1600**      | Hodrick-Prescott (1997) recommendation |
| Monthly        | **14400**     | Ravn-Uhlig (2002) adjustment |

**Common mistake**: Using λ=1600 (quarterly default) for annual data produces an overly smooth trend that misses important cyclical dynamics.

### Python Implementation

```python
from statsmodels.tsa.filters.hp_filter import hpfilter
import numpy as np

# Apply HP filter
# Returns: (cyclical_component, trend_component)
cycle, trend = hpfilter(data, lamb=100)  # For annual data

# For quarterly data
cycle_q, trend_q = hpfilter(quarterly_data, lamb=1600)
```

**Important**: The function parameter is `lamb` (not `lambda`, which is a Python keyword).

## Log Transformation for Growth Series

### Why Use Logs?

For most macroeconomic aggregates (GDP, consumption, investment), you should apply the natural logarithm **before** filtering:

1. **Multiplicative to Additive**: Converts percentage changes to log differences
2. **Stabilizes Variance**: Growth rates become comparable across time
3. **Economic Interpretation**: Cyclical component represents percentage deviations from trend
4. **Standard Practice**: Required for business cycle statistics that compare volatilities

```python
import numpy as np

# Apply log transformation BEFORE HP filtering
log_series = np.log(real_series)
cycle, trend = hpfilter(log_series, lamb=100)

# The cycle now represents percentage deviations from trend
# e.g., cycle = 0.02 means 2% above trend
```

### When NOT to Use Logs

- Series that can be negative (net exports, current account)
- Series already expressed as rates or percentages
- Series with zeros

## Complete Workflow for Detrending

### Step-by-Step Process

1. **Load and clean data**: Handle missing values, ensure proper time ordering
2. **Convert to real terms**: Deflate nominal values using appropriate price index
3. **Apply log transformation**: For positive level variables
4. **Apply HP filter**: Use appropriate λ for data frequency
5. **Analyze cyclical component**: Compute correlations, volatilities, etc.

### Example: Business Cycle Correlation

```python
import pandas as pd
import numpy as np
from statsmodels.tsa.filters.hp_filter import hpfilter

# Load real (inflation-adjusted) data
real_consumption = pd.Series(...)  # Real consumption expenditure
real_investment = pd.Series(...)   # Real fixed investment

# Log transformation
ln_consumption = np.log(real_consumption)
ln_investment = np.log(real_investment)

# HP filter with λ=100 for annual data
cycle_c, trend_c = hpfilter(ln_consumption, lamb=100)
cycle_i, trend_i = hpfilter(ln_investment, lamb=100)

# Compute correlation of cyclical components
correlation = np.corrcoef(cycle_c, cycle_i)[0, 1]
print(f"Business cycle correlation: {correlation:.4f}")
```

## Dependencies

Ensure these packages are installed:
```bash
pip install statsmodels pandas numpy
```

The HP filter is in `statsmodels.tsa.filters.hp_filter`.

[Evidence block]
No Skills: `40`
With Skills: `60`
Delta: `20`
Failure summary: extract nominal series, deflate with CPI, HP-filter log-real series, compute Pearson correlation, output single number
Competing schema note: No prior round-0 pair evidence available.

[Output contract block]
Return YAML with fields:
revised_task_skill, change_summary{keep/add/remove/sharpen}, rationale

```yaml
revised_task_skill: |
  ...
change_summary:
  keep:
    - ...
  add:
    - ...
  remove:
    - ...
  sharpen:
    - ...
rationale: |
  ...
```

[Outer-loop candidate block]
Source round: outer-loop-round0
Next round: outer-loop-round1
Candidate id: retrieval-heavy-synthesis::round1::differentiating
Candidate mode: differentiating
Pair reason: full_matrix_eval
Next pair plan mode: full_matrix
Use this as a candidate schema rerun, not as an accepted final schema.
