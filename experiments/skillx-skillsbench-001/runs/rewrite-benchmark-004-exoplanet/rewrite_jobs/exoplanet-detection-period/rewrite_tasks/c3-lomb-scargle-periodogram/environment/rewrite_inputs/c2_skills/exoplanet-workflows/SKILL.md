---
skillx:
  name: exoplanet-workflows
  purpose: Detect and characterize exoplanet transits from light curve data by preprocessing stellar noise and performing period searches
  scope_in:
    - Filtering light curve data using quality flags and outlier removal
    - Removing stellar activity (rotation, starspots, long-term trends) to expose transit signals
    - Period searches for transiting exoplanets using TLS, Lomb-Scargle, or BLS
    - Transit signal validation using detection metrics (SDE, SNR)
    - Choosing appropriate period search algorithms based on signal type
    - Refining period precision for strong candidates
  scope_out:
    - Radial velocity planet detection methods
    - Direct imaging techniques
    - Detailed orbital parameter fitting beyond period determination
    - Multi-planet system analysis (unless specifically requested)
    - Statistical validation of planet candidates for publication
    - Atmospheric characterization
  requires:
    - Python environment with scientific libraries
    - Light curve data with time, flux, quality flags, and flux uncertainties
    - "Libraries: lightkurve, transitleastsquares, numpy, scipy, matplotlib"
  preferred_tools:
    - Transit Least Squares (TLS) for transit-shaped signal detection
    - Lightkurve for data loading, quality filtering, and detrending
    - Lomb-Scargle periodogram for exploratory period searches
    - Phase-folding for visual validation of candidates
  risks:
    - Over-aggressive preprocessing (smoothing, outlier removal) can remove real transit signals
    - Period aliasing from data gaps may return 2x or 0.5x the true period
    - Low signal-to-noise transits may be missed or produce false positives
    - Quality flag conventions vary between missions (flag=0 may mean good OR bad data)
    - TLS requires flux uncertainties as mandatory input (not optional)
    - Insufficient period range may miss the true signal
  examples:
    - "Finding hot Jupiter period from TESS light curve with stellar rotation modulation: filter quality flags, detrend with Savitzky-Golay or splines, run TLS with 0.5-10 day period range"
    - "Detecting super-Earth transits after removing long-term trends: apply sigma-clipping for outliers, flatten light curve to remove stellar variability, search with TLS, validate using SDE and phase-folded plot"
---

# Guidance

## Essential Workflow

Exoplanet detection from light curves follows this pipeline:

1. **Data Loading**: Understand your data format (columns: time, flux, quality flags, flux uncertainties)
2. **Quality Control**: Filter bad data points using quality flags (verify convention - check if 0 means good or bad)
3. **Preprocessing**: Remove stellar noise while preserving planetary signals
   - Remove outliers (sigma-clipping: 3-sigma initially, 5-sigma after flattening)
   - Remove trends from stellar rotation/activity (detrending, flattening)
4. **Period Search**: Use appropriate algorithm for signal type
5. **Validation**: Verify candidate using detection metrics
6. **Refinement**: Narrow search around candidate for improved precision (if needed)

## Preprocessing Decisions

**What to remove:**
- Outliers: Yes, but not too aggressively (preserve transits)
- Stellar rotation trends: Yes, this masks transit signals
- Balance: Remove enough noise without removing the signal

**How much preprocessing:**
- Plot each step to verify improvement
- Under-preprocessing leaves noise; over-preprocessing removes transits
- If unsure, try multiple approaches and compare results

## Choosing Period Search Algorithm

**Transit Least Squares (TLS)** - primary choice for transits
- Use when: Searching for transiting exoplanets (box-shaped dips in flux)
- Advantages: Most sensitive for transits, handles grazing transits, provides transit parameters
- Disadvantages: Slower than Lomb-Scargle, only detects transits
- **Critical**: Requires flux uncertainties as third argument (mandatory, not optional)

**Lomb-Scargle Periodogram** - exploratory tool
- Use when: Quick exploration for any periodic signal, detecting stellar rotation, finding pulsations
- Advantages: Fast, works for any periodic signal
- Disadvantages: Less sensitive to shallow transits, may confuse harmonics

**Box Least Squares (BLS)** - alternative transit detector
- Use when: TLS unavailable or as comparison
- Available in astropy
- Note: TLS generally performs better for exoplanet detection

## Period Range Selection

Based on expected planet types:
- **Hot Jupiters**: 0.5-10 days
- **Warm planets**: 10-100 days
- **Habitable zone** (depends on star type):
  - Sun-like star: 200-400 days
  - M-dwarf: 10-50 days

Wider range = more complete search but slower computation.

## Signal Validation Criteria

**Strong candidate (TLS metrics):**
- SDE > 9: Very strong candidate
- SDE > 6: Strong candidate
- SNR > 7: Reliable signal

**Warning signs:**
- SDE < 6: Weak signal, possible false positive
- Period exactly half or double expected: Check for aliasing
- High odd-even mismatch: May not be planetary transit

**Validation steps:**
1. Check SDE and SNR thresholds
2. Phase-fold data at candidate period and visually inspect
3. Check odd-even transit consistency
4. Verify multiple transits are present

## Common Issues

**No significant detection (low SDE):**
- Check if preprocessing removed signal
- Try less aggressive outlier removal
- Check for data gaps during transits
- Signal may be too shallow for detection

**Period is 2x or 0.5x expected:**
- Caused by period aliasing from data gaps or missing alternate transits
- Solution: Check both periods manually, examine phase-folded light curves

**"flux_err required" error:**
- TLS requires flux uncertainties - they are mandatory, not optional

## Expected Transit Depths (for context)

- Hot Jupiters: 0.01-0.03 (1-3% dip)
- Super-Earths: 0.001-0.003 (0.1-0.3% dip)
- Earth-sized: 0.0001-0.001 (0.01-0.1% dip)

Detection difficulty increases dramatically for smaller planets.

# Notes for Agent

- Always include flux uncertainties when calling TLS - this is mandatory
- Visualize each preprocessing step to ensure data quality improves
- Verify quality flag convention before filtering (0 may mean good OR bad depending on mission)
- Use appropriate sigma thresholds: 3-sigma for initial outliers, 5-sigma after flattening
- For strong candidates, refine by narrowing period search range around detected period
- Phase-fold at candidate period for visual confirmation
- Document your workflow steps for reproducibility
- Consider data gaps in time series - they can cause period aliasing
