---
skillx:
  name: lomb-scargle-periodogram
  purpose: Detect periodic signals in unevenly sampled astronomical time series using Lomb-Scargle periodogram analysis
  scope_in:
    - Finding periods in light curves from Kepler, K2, TESS missions
    - Detecting stellar rotation periods from photometric variability
    - Identifying exoplanet orbital periods from transit signals
    - Analyzing eclipsing binary periods
    - Detecting stellar pulsation frequencies
  scope_out:
    - Not for evenly sampled data where standard FFT is more efficient
    - Not optimized specifically for transit detection (consider TLS/BLS for exoplanets)
    - Not for trend analysis or non-periodic signal characterization
    - Not for detrending or removing stellar variability
  requires:
    - Python environment with lightkurve, numpy, matplotlib
    - Time series data with time, flux, and optional flux_err columns
    - Knowledge of expected period range for the target phenomenon
  preferred_tools:
    - lightkurve.LightCurve.to_periodogram() for periodogram computation
    - matplotlib for visualization and validation
    - numpy for data manipulation
  risks:
    - Aliasing can produce false periods, especially at short timescales
    - Harmonics (period/2, period*2) may appear as strong peaks
    - Very wide period ranges increase computation time significantly
    - Strong stellar activity or systematics can mask weaker periodic signals
    - Window function artifacts from data gaps can create spurious peaks
  examples:
    - Finding 25-day rotation period in a solar-type star from Kepler data
    - Detecting 5-day exoplanet orbital period in TESS light curve
    - Identifying 0.2-day pulsation in delta Scuti star
---

# Guidance

## Creating and Running Periodogram

Use `lightkurve` to compute Lomb-Scargle periodograms from time series data:

```python
import lightkurve as lk

# Create light curve object
lc = lk.LightCurve(time=time_array, flux=flux_array, flux_err=error_array)

# Compute periodogram with appropriate period range
pg = lc.to_periodogram(minimum_period=0.5, maximum_period=50)

# Get strongest period
period = pg.period_at_max_power
power = pg.max_power
```

## Period Range Selection

Choose period ranges based on your target phenomenon:

- **Stellar rotation**: 0.1 to 100 days
- **Exoplanet transits**: 0.5 to 50 days (short-period planets more common)
- **Eclipsing binaries**: 0.1 to 100 days
- **Stellar pulsations**: 0.001 to 1 day

Wider ranges increase computation time. Narrow the range if you have prior constraints.

## Interpreting Results

**Single strong peak**: Likely the true period if it makes physical sense.

**Multiple peaks**: Check for harmonic relationships:
- Peaks at period/2, period*2 suggest harmonics of a fundamental period
- The true period is typically the longest harmonic in the series

**Validation**: Visualize the periodogram and check peak significance:

```python
pg.plot(view='period')  # Plot vs period (not frequency)
```

Use `view='period'` to see periods directly in days instead of frequencies.

## Model Fitting

Once you identify a period, fit and visualize the model:

```python
frequency = pg.frequency_at_max_power
model = pg.model(time=lc.time, frequency=frequency)

# Plot data with model overlay for validation
lc.plot(label='Data')
model.plot(label='Model')
```

## When to Use Alternatives

- **For exoplanet transit detection**: Consider Transit Least Squares (TLS) or Box Least Squares (BLS) after initial Lomb-Scargle analysis, as they are specifically optimized for box-shaped transit signals
- **For evenly sampled data**: Standard FFT-based periodogram is faster
- **For multi-periodic signals**: May need iterative pre-whitening (fit and remove strongest signal, repeat)

# Notes for Agent

- Always specify appropriate `minimum_period` and `maximum_period` based on the expected phenomenon. Default ranges may be inappropriate.
- Check for harmonics: if you see peaks at P and P/2, the true period is likely P (the longer one).
- Aliasing from observational window functions can create spurious peaks, especially at 1-day and its harmonics for ground-based data.
- For exoplanet detection tasks where stellar activity is present, you may need to first remove low-frequency variability (stellar rotation, trends) before running the periodogram to detect transits.
- The period is the inverse of frequency: period = 1/frequency. Lightkurve handles this conversion.
- Install dependencies with: `pip install lightkurve numpy matplotlib`
