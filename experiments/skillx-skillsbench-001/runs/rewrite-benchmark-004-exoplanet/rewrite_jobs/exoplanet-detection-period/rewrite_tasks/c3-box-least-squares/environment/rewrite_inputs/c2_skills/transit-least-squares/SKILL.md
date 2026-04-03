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
