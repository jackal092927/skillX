---
skillx:
  name: transit-least-squares
  purpose: Detect exoplanet transit periods from stellar light curves using the Transit Least Squares algorithm, optimized for transit-shaped periodic signals
  scope_in:
    - Finding exoplanet orbital periods from time-series photometry data
    - Processing TESS, Kepler, or similar space telescope light curves
    - Detecting periodic transit-like dips in brightness caused by planetary transits
    - Extracting best-fit period, transit epoch, depth, and signal strength metrics
  scope_out:
    - General periodicity detection (use Lomb-Scargle for non-transit signals)
    - Stellar rotation or pulsation analysis (different signal shapes)
    - Non-periodic variability or aperiodic flares
    - Light curve simulation or synthetic data generation
  requires:
    - Python environment with transitleastsquares package
    - Light curve data with time, flux, and flux uncertainty arrays
    - Quality-filtered and preprocessed photometry (outliers removed, detrended)
  preferred_tools:
    - transitleastsquares Python package for transit detection
    - lightkurve for light curve preprocessing and manipulation
    - numpy for array operations
    - Standard Python file I/O for reading data and writing results
  risks:
    - Period aliasing (reported period may be 2x or 0.5x true period due to data gaps)
    - Weak signals (SDE < 6) may be false positives requiring validation
    - Missing flux uncertainties degrades TLS performance significantly
    - Insufficient detrending may hide transit signal under stellar variability
    - Over-aggressive flattening may remove real transit signal
  examples:
    - "Find the orbital period of an exoplanet from TESS light curve data"
    - "Detect transiting planet candidate and report period to 5 decimal places"
    - "Process photometry, remove stellar activity, and identify transit period"
---

# Guidance

Transit Least Squares (TLS) is optimized for detecting exoplanet transits by fitting actual transit models at different periods. It is more sensitive than Lomb-Scargle for transit-shaped signals.

## Standard Workflow

1. **Load and filter data**: Read light curve with time, flux, and flux_err arrays. Filter by quality flags and remove outliers (sigma=3-5).

2. **Preprocess**: Detrend or flatten to remove stellar activity (rotational modulation, starspots). This step is critical for uncovering transit signals hidden by stellar variability.

3. **Run TLS**: Create TLS object with time, flux, and flux_err (uncertainties are required). Call `.power()` to search for transits.

4. **Extract results**: Best period is in `out_tls.period`. Other useful outputs: `period_uncertainty`, `T0` (epoch), `depth`, `snr`, `sde`.

## Basic Usage Pattern

```python
import transitleastsquares as tls
import lightkurve as lk

# Load and clean data
lc = lk.LightCurve(time=time, flux=flux, flux_err=error)
lc_clean = lc.remove_outliers(sigma=3)
lc_flat = lc_clean.flatten()  # Remove stellar variability

# Run TLS (flux_err is required for best results)
pg_tls = tls.transitleastsquares(
    lc_flat.time.value,
    lc_flat.flux.value,
    lc_flat.flux_err.value
)

# Search for transits
out_tls = pg_tls.power(show_progress_bar=False, verbose=False)

# Get period
best_period = out_tls.period
```

## Period Refinement Strategy

For higher precision: run initial broad search, then narrow the period range around the candidate (±2% to ±10%) and re-run TLS. Narrower ranges use finer grids for better precision.

```python
# After initial search finds candidate at ~X days
results_refined = pg_tls.power(
    period_min=X * 0.95,  # 5% below candidate
    period_max=X * 1.05   # 5% above candidate
)
```

## Signal Validation

- **SDE (Signal Detection Efficiency)**: >6 is a candidate, >9 is strong
- **SNR (Signal-to-Noise Ratio)**: >7 is generally reliable
- Check for period aliasing: if TLS warns about missing transits, try `period * 2`

## Output Format Requirements

When writing period results to file:
- Single numerical value in days
- Round to specified decimal places (typically 5)
- Plain text format, one value per line

# Notes for Agent

TLS requires three inputs: time array, flux array, and flux_err array. Always include flux uncertainties for proper data weighting.

The preprocessing step (flattening/detrending) is essential when stellar activity dominates the signal. Use `lightkurve.flatten()` or similar methods to remove low-frequency variability before running TLS.

Default period range is auto-computed from data duration. You can specify `period_min` and `period_max` to constrain the search.

The `.power()` method returns a results object with attributes: `period`, `period_uncertainty`, `T0`, `depth`, `duration`, `snr`, `sde`, and phase-folded data arrays.

Period aliasing is common when data has gaps. If TLS reports a warning about missing transits, check whether doubling or halving the period gives a stronger signal.

Installation: `pip install transitleastsquares lightkurve`

# Derived Execution Layer

## Preconditions

Before using this skill, the following must be true:

1. **Input data file exists** with required columns: time (MJD), normalized flux, quality flags, and flux uncertainties
2. **Preprocessing completed**: Data must be quality-filtered, outlier-removed, and detrended to remove stellar activity (rotational modulation, starspots)
3. **Python environment ready** with `transitleastsquares` and `lightkurve` packages installed
4. **Flux uncertainties available**: TLS requires flux_err as mandatory input (not optional)
5. **Light curve is flattened**: Long-term trends and stellar variability have been removed to expose transit signals
6. **Quality flag convention verified**: Correct filtering applied (TESS standard: quality==0 means good data, but verify for specific file)

## Postconditions

After successful execution, the following must be true:

1. **Period extracted**: Best period value obtained from `out_tls.period` attribute
2. **Output file created**: `/root/period.txt` exists and is writable
3. **Correct format**: File contains exactly one numerical value in days, rounded to 5 decimal places
4. **Valid value**: Period is positive and within physically reasonable range (typically 0.5-100 days for known exoplanets)
5. **No extra content**: File contains only the period value, no labels, units, or additional text
6. **Signal validated**: If weak signal (SDE < 6), additional validation performed or documented

## Failure Modes

Common ways execution can fail even when the skill is correctly chosen:

1. **Skipping preprocessing**: Running TLS on raw light curve without removing stellar activity results in weak or missed detections
2. **Missing flux uncertainties**: Forgetting to include `flux_err` array causes TLS to fail or perform poorly
3. **Wrong output path**: Writing period to incorrect location (not `/root/period.txt`) fails evaluator check
4. **Incorrect format**: Including units, labels, or not rounding to 5 decimals fails format validation
5. **Period aliasing**: Reporting 2x or 0.5x the true period due to data gaps without checking alternatives
6. **Accepting weak signals**: Using periods with SDE < 6 without validation leads to false positives
7. **Over-preprocessing**: Aggressive flattening (window_length too small) removes real transit signal
8. **Under-preprocessing**: Insufficient detrending leaves stellar variability that obscures transits
9. **Wrong quality flag convention**: Using `quality != 0` when `quality == 0` means good data (or vice versa) removes valid points
10. **Incomplete workflow**: Stopping after initial broad search without considering period refinement for precision

## Evaluator Hooks

The benchmark evaluator checks the following output contract surfaces:

1. **File existence**: `/root/period.txt` must exist at this exact path
2. **Parseability**: File content must be parseable as a valid floating-point number using Python's `float()`
3. **Value constraint**: Parsed value must be positive (> 0)
4. **Format precision**: Value should have at most 5 decimal places (trailing zeros may be omitted)
5. **Numerical accuracy**: Period value must be within tolerance (±0.01 days) of the true exoplanet period
6. **Single-value format**: File should contain only the numerical value, no additional text or formatting

Expected period range based on task context: approximately 5-6 days (hot Jupiter candidate from TESS data with visible transits after preprocessing). Values significantly outside this range (e.g., < 1 day or > 20 days) likely indicate period aliasing or detection failure requiring investigation.
