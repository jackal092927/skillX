---
skillx:
  name: light-curve-preprocessing
  purpose: Preprocess astronomical light curves by filtering quality flags, removing outliers, removing stellar variability trends, and preparing data for exoplanet transit period detection
  scope_in:
    - Filtering light curve data using quality flags
    - Removing outliers from flux measurements
    - Removing long-term stellar activity trends (rotation, instrumental drift)
    - Detrending to reveal short-duration transit signals
    - Preparing clean time series for periodogram analysis
  scope_out:
    - Period-finding algorithms themselves (use separate period-detection skills)
    - Initial data acquisition or format conversion
    - Statistical model fitting beyond preprocessing
    - Creating publication-quality visualizations
  requires:
    - Python environment with numpy, lightkurve, matplotlib
    - Input light curve data with time, flux, quality flags, flux uncertainty
    - Understanding of which quality flag convention is used (0=good vs 0=bad varies by source)
  preferred_tools:
    - lightkurve.LightCurve for preprocessing operations
    - lightkurve remove_outliers() for sigma clipping
    - lightkurve flatten() for trend removal with Savitzky-Golay filter
    - numpy for manual filtering and calculations
  risks:
    - Over-aggressive preprocessing can remove shallow transit signals
    - Quality flag conventions vary by data source (TESS standard: 0=good, but exported files may differ)
    - Flattening window length must preserve transit duration while removing stellar rotation
    - Removing periodic signals via sine fitting will erase the transit pattern if applied incorrectly
  examples:
    - Filter TESS light curve by quality==0, remove 3-sigma outliers, flatten with window_length=500
    - Remove stellar rotation signal to reveal exoplanet transits masked by brightness variations
    - Two-pass outlier removal: before detrending (aggressive) and after detrending (conservative)
---

# Guidance

Preprocessing light curves for exoplanet detection requires removing contaminating signals while preserving the transit pattern. Follow this sequence:

## 1. Quality Filtering

Apply quality flags first. **Verify the flag convention for your data source:**
- TESS standard format: `quality == 0` means good data
- Some exported files: `quality != 0` means good data

Check both approaches and verify which produces cleaner results.

```python
good = quality == 0  # or != 0, depending on format
time_filtered = time[good]
flux_filtered = flux[good]
error_filtered = error[good]
```

## 2. Outlier Removal

Remove outliers using sigma clipping before detrending:

```python
import lightkurve as lk

lc = lk.LightCurve(time=time_filtered, flux=flux_filtered, flux_err=error_filtered)
lc_clean = lc.remove_outliers(sigma=3)
```

Sigma parameter guidelines:
- sigma=3: Standard approach (removes ~0.3% of data)
- sigma=5: Conservative (fewer points removed)
- sigma=2: Aggressive (more points removed, higher risk of removing real signals)

## 3. Trend Removal

Remove long-term stellar variability using flatten():

```python
lc_flat = lc_clean.flatten(window_length=500)
```

Window length selection:
- Must be **longer than transit duration** (transits typically last hours)
- Must be **shorter than stellar rotation period** (typically days to weeks)
- For TESS data: 300-500 cadences is typical
- Too short: doesn't remove trends
- Too long: removes transit signals

The flatten() method uses Savitzky-Golay filtering which preserves short-duration dips while removing longer trends.

## 4. Removing Stellar Variability for Transit Detection

If stellar activity (rotation with starspots) is masking the transit signal, use iterative sine fitting:

```python
def remove_stellar_activity(lc, iterations=50):
    """Remove dominant periodic signals by iterative sine fitting."""
    lc_processed = lc.copy()
    for i in range(iterations):
        pg = lc_processed.to_periodogram()
        model = pg.model(time=lc_processed.time, frequency=pg.frequency_at_max_power)
        lc_processed.flux = lc_processed.flux / model.flux
    return lc_processed

lc_detrended = remove_stellar_activity(lc_flat)
```

This iteratively fits and removes the strongest periodic signal. Use after basic preprocessing to avoid fitting noise.

## 5. Output Format

Always preserve flux uncertainties in the cleaned dataset. Period-finding algorithms weight measurements by uncertainty for better accuracy.

# Notes for Agent

**Processing Order**: Quality flags → outliers → trends → stellar variability. Do not reorder these steps.

**Quality Flag Ambiguity**: TESS data has inconsistent quality flag conventions. Test both `quality == 0` and `quality != 0` to determine which is correct for the specific file. The correct choice will have more data points and cleaner flux distribution.

**Window Length Selection**: For TESS 2-minute cadence data, window_length=500 corresponds to ~16-17 hours, which removes stellar rotation (~days) while preserving transits (~hours). Adjust if using different cadence data.

**Iterative Sine Fitting**: Use this specifically to remove stellar rotation signals that obscure transits. The number of iterations (typically 50) should be sufficient to remove the dominant periodic component without overfitting noise.

**Visualization**: Plot the light curve after each major step (quality filtering, outlier removal, flattening, stellar variability removal) to verify that transit-like dips remain visible while noise and trends are suppressed.

**Don't Over-Process**: More preprocessing is not always better. Stop when the light curve shows clear transit-like periodic dips without overwhelming noise or trends.
