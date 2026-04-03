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

# Derived Execution Layer

## Preconditions

- Input light curve file exists at the specified path (e.g., `/root/data/tess_lc.txt`)
- Input file contains required columns: time, flux, quality flag, flux uncertainty
- Python environment includes lightkurve, numpy, and matplotlib packages
- Flux values are normalized (typically around 1.0 for normalized flux)
- Time column uses consistent units (MJD or similar)
- Quality flag column exists and uses a consistent convention (must be determined: 0=good or 0=bad)

## Postconditions

- Preprocessed light curve data is available in memory for subsequent period-finding analysis
- All required data arrays are preserved: time, cleaned flux, flux uncertainties
- Data has been processed in the correct sequence: quality filtering → outlier removal → trend removal → stellar variability removal
- Cleaned light curve shows reduced noise and trends while preserving short-duration transit-like features
- The preprocessing did not remove or significantly distort potential transit signals
- Visual inspection (if performed) confirms that periodic dips remain visible in the cleaned data

## Failure Modes

- **Wrong quality flag convention**: Using `quality == 0` when the file uses `quality != 0` convention (or vice versa) results in filtering out all good data instead of bad data. This leaves an empty or severely truncated dataset.
- **Incorrect processing order**: Applying trend removal before quality filtering or outlier removal can cause the detrending algorithm to fit contaminated data, producing incorrect baseline removal.
- **Over-aggressive outlier removal**: Using sigma=2 or multiple aggressive outlier removal passes can remove shallow but real transit signals, especially if transits are only 1-2% deep.
- **Inappropriate flattening window**: Window length shorter than transit duration removes the transit signal itself; window length longer than stellar rotation period fails to remove stellar variability trends.
- **Excessive iterative sine fitting**: Too many iterations or applying sine fitting before basic preprocessing can overfit noise or remove transit periodicity along with stellar rotation.
- **Missing flux uncertainties**: Dropping or not preserving flux_err values prevents downstream period-finding algorithms from properly weighting measurements.
- **Stopping after partial preprocessing**: Completing quality filtering and outlier removal but skipping stellar variability removal when the instruction explicitly requires removing stellar activity to reveal hidden transit signals.
- **Not verifying preprocessing effectiveness**: Failing to check (visually or programmatically) whether stellar variability was actually removed, leaving the transit signal still masked.

## Evaluator Hooks

This skill is an intermediate preprocessing stage. The evaluator does not directly check preprocessing outputs, but preprocessing quality directly affects the downstream period-finding results.

Preprocessing failures that cascade to evaluation failures:
- **Inadequate preprocessing** → stellar variability remains → period-finding identifies stellar rotation period instead of transit period → wrong period value in `/root/period.txt`
- **Over-preprocessing** → transit signals removed → period-finding finds noise or spurious signals → wrong period value in `/root/period.txt`
- **Data corruption** → empty or malformed dataset after preprocessing → period-finding crashes or produces no output → `/root/period.txt` missing or unparseable

The ultimate evaluator hook is the period output file at `/root/period.txt`, which must:
- Exist at the specified path
- Contain a single numerical value (parseable as float)
- Be positive
- Have at most 5 decimal places
- Match the true exoplanet period within tolerance

Preprocessing must support the full workflow that produces this output, even though the preprocessing step itself does not create the final file.
