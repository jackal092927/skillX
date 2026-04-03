---
skillx:
  name: box-least-squares
  purpose: Detect transiting exoplanet periods from photometric time series using the Box Least Squares (BLS) periodogram, particularly when stellar activity or other variability obscures the transit signal.
  scope_in:
    - Finding periodic box-shaped transit signals in stellar lightcurves
    - Detrending data with stellar variability (rotation, spots) to reveal transits
    - Searching for exoplanet orbital periods in TESS, Kepler, or similar data
    - Validating transit candidates using statistical metrics
  scope_out:
    - General periodic signal detection (use Lomb-Scargle for sinusoidal signals)
    - Non-planetary eclipsing binaries with asymmetric or irregular eclipses
    - Continuous sinusoidal variations like stellar pulsations
    - Raw data calibration or quality flag generation
  requires:
    - Python environment
    - astropy (>=4.0 for astropy.timeseries.BoxLeastSquares)
    - numpy for array operations and data handling
    - matplotlib (optional, for visualization)
    - lightkurve (optional, for TESS/Kepler-specific preprocessing)
  preferred_tools:
    - Read for loading lightcurve data files
    - Bash for installing dependencies (pip install astropy numpy)
    - Write for saving detected period values
  risks:
    - Over-aggressive detrending removes real transit signals along with stellar variability
    - Insufficient detrending leaves noise that masks weak transits
    - Coarse period grid spacing misses the true period
    - Searching with wrong duration range fails to detect transits
    - Period aliasing produces 2× or 0.5× the true period due to data gaps or missed transits
  examples:
    - task: Find exoplanet period in TESS lightcurve dominated by stellar rotation
      approach: Filter quality flags, apply gentle detrending to remove stellar variability while preserving transit shapes, run BLS with multiple duration values, validate strongest peak with compute_stats
    - task: Detect planetary transit period from pre-processed Kepler data
      approach: Load clean lightcurve, search using BLS autopower with expected duration range, verify candidate using odd-even depth consistency and SNR metrics
---

# Guidance

## Task Pattern

When searching for transiting exoplanet periods in photometric time series:

1. **Load and filter data**: Read lightcurve file (time, flux, quality flags, uncertainties). Remove points with bad quality flags and obvious outliers.

2. **Detrend stellar variability**: Remove long-term trends and stellar activity (rotation, spots) that obscure the transit signal. Use methods that preserve the box-shaped transit profile.

3. **Run BLS period search**: Use astropy's BoxLeastSquares to search for periodic transit signals across a range of periods and durations.

4. **Validate the candidate**: Use compute_stats to check depth SNR, odd-even consistency, and transit count.

## Using Box Least Squares

BLS models transits as periodic upside-down box shapes and searches for the period, duration, depth, and reference time that best fit the data.

### Basic workflow

```python
import numpy as np
import astropy.units as u
from astropy.timeseries import BoxLeastSquares

# Load data (time in days, normalized flux, flux uncertainties)
data = np.loadtxt('lightcurve.txt')
time = data[:, 0] * u.day
flux = data[:, 1]
flux_err = data[:, 3]

# Filter bad data using quality flags
quality = data[:, 2]
mask = (quality == 0)  # Keep only good data
time = time[mask]
flux = flux[mask]
flux_err = flux_err[mask]

# Detrend to remove stellar variability
# (preserve transit shapes - use gentle methods)

# Create BLS model
model = BoxLeastSquares(time, flux, dy=flux_err)

# Search multiple durations
durations = np.linspace(0.05, 0.3, 10) * u.day
periodogram = model.autopower(durations)

# Find best period
max_idx = np.argmax(periodogram.power)
best_period = periodogram.period[max_idx]
best_duration = periodogram.duration[max_idx]
best_t0 = periodogram.transit_time[max_idx]

# Validate
stats = model.compute_stats(best_period, best_duration, best_t0)
print(f"Period: {best_period:.5f}")
print(f"Depth SNR: {stats['depth_snr']:.2f}")
print(f"Transits: {stats['transit_count']}")
```

### Detrending considerations

Stellar activity creates brightness variations that hide transits. The detrending must remove these variations without removing the transits themselves.

**Gentle detrending options:**
- Moving median or polynomial fit with window >> transit duration
- Lightkurve's `flatten()` method (if using TESS/Kepler data)
- Gaussian process regression with appropriate kernel timescale

**Critical:** The detrending window must be much longer than the transit duration. Too short removes transits. Too long leaves stellar noise.

### Period and duration search

**autopower (recommended):**
```python
# Single duration
periodogram = model.autopower(0.2 * u.day)

# Multiple durations (recommended)
durations = np.linspace(0.05, 0.3, 10) * u.day
periodogram = model.autopower(durations)
```

**Custom period grid (advanced):**
```python
periods = np.linspace(2.0, 10.0, 1000) * u.day
periodogram = model.power(periods, 0.2 * u.day)
```

**Duration selection:** For planets, transit duration depends on orbital period and stellar radius. Typical range: 0.05–0.3 days. Searching multiple values increases detection chance.

**Period grid quality:** BLS is sensitive to grid spacing. `autopower()` handles this automatically. Custom grids need sufficient resolution to avoid missing the true period.

### Validation with compute_stats

Always validate the strongest candidate:

```python
stats = model.compute_stats(best_period, best_duration, best_t0)

# Key validation metrics:
# - depth_snr > 7: strong signal
# - depth_odd ≈ depth_even: consistent transits (planetary)
# - transit_count >= 3: multiple observed transits
# - depth within reasonable range for planets

odd_even_diff = abs(stats['depth_odd'] - stats['depth_even'])
if odd_even_diff > 3 * stats['depth_err']:
    # Large odd-even mismatch suggests eclipsing binary, not planet
    pass
```

**Odd-even depth test:** Planets have consistent transit depth. Large differences between odd and even transits suggest an eclipsing binary or instrumental artifact.

### Objective functions

BLS supports two objective functions:

- `objective='likelihood'` (default): Maximizes statistical likelihood
- `objective='snr'`: Uses signal-to-noise ratio, can be better with correlated noise

```python
periodogram = model.autopower(durations, objective='snr')
```

## Output format

When writing detected periods to files, use the format specified by the task. Common requirements:
- Single numerical value in days
- Specified decimal precision (e.g., 5 decimal places: `2.44535`)
- Plain text, no additional formatting

# Notes for Agent

## Implementation sequence

1. **Read the lightcurve file** - Understand column structure (time, flux, quality, uncertainty)
2. **Filter bad data** - Remove flagged points (quality ≠ 0) and outliers
3. **Detrend** - Remove stellar variability while preserving transit shapes
4. **Choose duration range** - Based on expected transit characteristics or search broadly
5. **Run BLS** - Use `autopower()` with multiple durations for robustness
6. **Extract best period** - Find the index with maximum power
7. **Validate** - Use `compute_stats()` to check SNR, odd-even consistency, transit count
8. **Format output** - Write period with required precision

## Common patterns

**Loading TESS/Kepler data:**
```python
data = np.loadtxt('/path/to/lightcurve.txt')
time = data[:, 0] * u.day  # Column 0: time in days
flux = data[:, 1]          # Column 1: normalized flux
quality = data[:, 2]       # Column 2: quality flags (0 = good)
flux_err = data[:, 3]      # Column 3: flux uncertainty
```

**Simple detrending with moving median:**
```python
from scipy.ndimage import median_filter

# Window much longer than expected transit duration
window = 101  # Must be odd
trend = median_filter(flux, size=window)
detrended_flux = flux / trend
```

**Finding multiple candidates:**
```python
# Get top N peaks
sorted_idx = np.argsort(periodogram.power)[::-1]
top_candidates = sorted_idx[:5]

for idx in top_candidates:
    period = periodogram.period[idx]
    stats = model.compute_stats(
        period,
        periodogram.duration[idx],
        periodogram.transit_time[idx]
    )
    print(f"Period: {period:.5f}, SNR: {stats['depth_snr']:.2f}")
```

## Period interpretation

**Common issues:**
- **No clear peak:** Transits too shallow, wrong duration range, over-detrended, or period outside search range
- **Period is 2× or 0.5× expected:** Missing alternating transits due to data gaps or low SNR
- **Multiple similar peaks:** Harmonics or aliases - check which has better odd-even consistency

**Resolution:**
- If unclear, try different detrending strengths
- Expand period and duration search ranges
- Check raw data visually for transit-like dips
- Compare top candidates using validation metrics

## Astropy units

BLS requires astropy Quantity objects with units. Always include `* u.day`:

```python
import astropy.units as u

time = time_array * u.day
periods = np.linspace(2, 10, 1000) * u.day
duration = 0.2 * u.day
```

Results from BLS also have units. Access values with `.value`:

```python
best_period = periodogram.period[max_idx]
print(f"{best_period:.5f}")  # Prints with units
print(f"{best_period.value:.5f}")  # Numeric value only
```

## Dependencies installation

```bash
pip install astropy numpy
# or using uv:
uv pip install astropy numpy
```

For TESS/Kepler preprocessing:
```bash
pip install lightkurve
```

# Derived Execution Layer

## Preconditions

Before applying this skill, verify:

- Input lightcurve file exists at the specified path (e.g., `/root/data/tess_lc.txt`)
- Lightcurve file contains required columns in correct order: Time (days or MJD), Normalized flux, Quality flag, Flux uncertainty
- Python environment has astropy (>=4.0) and numpy installed
- Data contains sufficient time coverage to detect multiple transits (at least 3 complete orbital periods for reliable detection)
- Quality flags are interpretable (0 = good data is common convention for TESS/Kepler)
- Flux is normalized or in consistent units across the time series

## Postconditions

After successful execution, verify:

- Output file exists at the exact path specified by the task (e.g., `/root/period.txt`)
- File contains a single numerical value representing the orbital period in days
- Value is a positive number (periods must be > 0)
- Value is formatted with the required decimal precision (commonly 5 decimal places, e.g., `5.35699`)
- No extraneous text, whitespace, or formatting is present in the output file
- The detected period corresponds to the strongest BLS peak that passes validation criteria

## Failure Modes

Common failure patterns even when the skill is correctly selected:

- **Over-aggressive detrending**: Using too short a detrending window or too high polynomial order removes the transit signal along with stellar variability. Symptom: No clear BLS peak or very weak power.

- **Insufficient detrending**: Leaving too much stellar activity noise in the data masks weak transits. Symptom: Multiple false peaks in the periodogram, low SNR for true candidate.

- **Wrong duration range**: Searching with durations far from the true transit duration reduces sensitivity. Symptom: Missing the true period or finding harmonics/aliases instead.

- **Coarse period grid**: Using too few period samples causes the search to miss the true period between grid points. Symptom: Detected period is slightly off or finding nearby harmonic.

- **Period aliasing**: Data gaps or low transit count cause detection at 2× or 0.5× the true period. Symptom: `compute_stats` shows fewer transits than expected, or odd-even depth mismatch.

- **Output format errors**: Writing period with wrong precision (too many/few decimals), including units in the output, or adding explanatory text. Symptom: Test fails on format validation.

- **Wrong output path**: Writing to incorrect file location or filename. Symptom: Evaluator cannot find output file.

- **Premature completion**: Stopping after finding first peak without validation or before writing output. Symptom: No output file despite finding valid period.

## Evaluator Hooks

The following output-contract elements are likely to be verified by the benchmark evaluator:

- **File existence**: Output file must exist at the exact specified path (commonly `/root/period.txt`)

- **Parseability**: File content must be parseable as a floating-point number using standard parsing (e.g., Python's `float()`)

- **Value sign**: Period value must be positive (> 0)

- **Numeric format**: Value must be formatted with at most the specified number of decimal places (commonly 5 decimal places)

- **Numeric accuracy**: The detected period should match the true period within a specified tolerance (commonly ±0.01 days for planetary transits)

- **Schema validation**: File should contain only the numerical value with no additional text, labels, units, or formatting
