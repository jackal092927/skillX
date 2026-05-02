[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: orchestration-delegation
Semantic intent: Coordinate ordered external actions or substeps where sequence and dependency management matter.
Emphasize:
- constraint extraction before action
- ordering across dependent steps / systems
- state handoff between stages or tools
- fail-safe finalization and side-effect awareness
- extract coordination-specific failure modes (state conflicts, ordering violations, side-effect races) before adding general procedural scaffolding
- make multi-system or multi-stage handoff protocols explicit when one component's output constrains another's input
- name which execution stage outputs become binding constraints or prerequisites for downstream stages
Avoid:
- eager direct completion without dependency checks
- reviewer-only prompts that lack execution choreography
- over-abstract synthesis that ignores operational order
Expected good fit:
- scheduling / delegation workflows
- multi-system action coordination
- tasks where one substep creates constraints for the next
- tasks where execution order matters due to external side effects, system state changes, or cross-tool dependencies
Expected bad fit:
- static artifact-only tasks
- deep scientific analysis pipelines
- tasks primarily focused on data transformation pipelines without external coordination requirements
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for a orchestration-delegation task.
Schema intent: Coordinate ordered external actions or substeps where sequence and dependency management matter.

Outer-loop update mode: differentiating. Keep the Render layer fixed and change only schema-level guidance.

Prioritize:
1. constraint extraction before action
2. ordering across dependent steps / systems
3. state handoff between stages or tools
4. fail-safe finalization and side-effect awareness
5. extract coordination-specific failure modes (state conflicts, ordering violations, side-effect races) before adding general procedural scaffolding
6. make multi-system or multi-stage handoff protocols explicit when one component's output constrains another's input
7. name which execution stage outputs become binding constraints or prerequisites for downstream stages

Avoid:
1. eager direct completion without dependency checks
2. reviewer-only prompts that lack execution choreography
3. over-abstract synthesis that ignores operational order

Good fit when:
- scheduling / delegation workflows
- multi-system action coordination
- tasks where one substep creates constraints for the next
- tasks where execution order matters due to external side effects, system state changes, or cross-tool dependencies

Bad fit when:
- static artifact-only tasks
- deep scientific analysis pipelines
- tasks primarily focused on data transformation pipelines without external coordination requirements

Primary failure modes to guard against:
- boundary confusion with analytic-pipeline on tasks that have both coordination aspects and analysis workflows, where the schema fails to articulate why orchestration concerns dominate

Regenerate task-specific skill guidance from these slots; do not invent a new policy outside them.

[Task context block]
Task name: earthquake-plate-calculation
Task summary: You are a geospatial analyst with expertise in plate tectonics and earthquake analysis. I want to find the earthquake that occurred furthest from the Pacific plate boundary within the Pacific plate itself. Use GeoPandas projections. Output the result to `/root/answer.json` as a JSON file with the following fields: - `id`: The earthquake ID
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
## geospatial-analysis
---
name: geospatial-analysis
description: Analyze geospatial data using geopandas with proper coordinate projections. Use when calculating distances between geographic features, performing spatial filtering, or working with plate boundaries and earthquake data.
license: MIT
---

# Geospatial Analysis with GeoPandas

## Overview

When working with geographic data (earthquakes, plate boundaries, etc.), using geopandas with proper coordinate projections provides accurate distance calculations and efficient spatial operations. This guide covers best practices for geospatial analysis.

## Key Concepts

### Geographic vs Projected Coordinate Systems

| Coordinate System | Type | Units | Use Case |
|-------------------|------|-------|----------|
| EPSG:4326 (WGS84) | Geographic | Degrees (lat/lon) | Data storage, display |
| EPSG:4087 (World Equidistant Cylindrical) | Projected | Meters | Distance calculations |

**Critical Rule**: Never calculate distances directly in geographic coordinates (EPSG:4326). Always project to a metric coordinate system first.

### Why Projection Matters

```python
# ❌ INCORRECT: Calculating distance in EPSG:4326
# This treats degrees as if they were equal distances everywhere on Earth
gdf = gpd.GeoDataFrame(..., crs="EPSG:4326")
distance = point1.distance(point2)  # Wrong! Returns degrees, not meters

# ✅ CORRECT: Project to metric CRS first
gdf_projected = gdf.to_crs("EPSG:4087")
distance_meters = point1_proj.distance(point2_proj)  # Correct! Returns meters
distance_km = distance_meters / 1000.0
```

## Loading Geospatial Data

### From GeoJSON Files

```python
import geopandas as gpd

# Load GeoJSON files directly
gdf_plates = gpd.read_file("plates.json")
gdf_boundaries = gpd.read_file("boundaries.json")
```

### From Regular Data with Coordinates

```python
from shapely.geometry import Point
import geopandas as gpd

# Convert coordinate data to GeoDataFrame
data = [
    {"id": 1, "lat": 35.0, "lon": 140.0, "value": 5.5},
    {"id": 2, "lat": 36.0, "lon": 141.0, "value": 6.0},
]

geometry = [Point(row["lon"], row["lat"]) for row in data]
gdf = gpd.GeoDataFrame(data, geometry=geometry, crs="EPSG:4326")
```

## Spatial Filtering

### Finding Points Within a Polygon

```python
# Get the polygon of interest
target_poly = gdf_plates[gdf_plates["Name"] == "Pacific"].geometry.unary_union

# Filter points that fall within the polygon
points_inside = gdf_points[gdf_points.within(target_poly)]

print(f"Found {len(points_inside)} points inside the polygon")
```

### Using `.unary_union` for Multiple Geometries

When you have multiple polygons or lines that should be treated as one:

```python
# Combine multiple boundary segments into one geometry
all_boundaries = gdf_boundaries.geometry.unary_union

# Or filter first, then combine
pacific_boundaries = gdf_boundaries[
    gdf_boundaries["Name"].str.contains("PA")
].geometry.unary_union
```

## Distance Calculations

### Point to Line/Boundary Distance

```python
# 1. Load your data
gdf_points = gpd.read_file("points.json")
gdf_boundaries = gpd.read_file("boundaries.json")

# 2. Project to metric coordinate system
METRIC_CRS = "EPSG:4087"
points_proj = gdf_points.to_crs(METRIC_CRS)
boundaries_proj = gdf_boundaries.to_crs(METRIC_CRS)

# 3. Combine boundary segments if needed
boundary_geom = boundaries_proj.geometry.unary_union

# 4. Calculate distances (returns meters)
gdf_points["distance_m"] = points_proj.geometry.distance(boundary_geom)
gdf_points["distance_km"] = gdf_points["distance_m"] / 1000.0
```

### Finding Furthest Point

```python
# Sort by distance and get the furthest point
furthest = gdf_points.nlargest(1, "distance_km").iloc[0]

print(f"Furthest point: {furthest['id']}")
print(f"Distance: {furthest['distance_km']:.2f} km")
```

## Common Workflow Pattern

Here's a complete example for analyzing earthquakes near plate boundaries:

```python
import geopandas as gpd
from shapely.geometry import Point

# 1. Load data
earthquakes_data = [...]  # Your earthquake data
gdf_plates = gpd.read_file("plates.json")
gdf_boundaries = gpd.read_file("boundaries.json")

# 2. Create earthquake GeoDataFrame
geometry = [Point(eq["longitude"], eq["latitude"]) for eq in earthquakes_data]
gdf_eq = gpd.GeoDataFrame(earthquakes_data, geometry=geometry, crs="EPSG:4326")

# 3. Spatial filtering - find earthquakes in specific plate
target_plate = gdf_plates[gdf_plates["Code"] == "PA"].geometry.unary_union
earthquakes_in_plate = gdf_eq[gdf_eq.within(target_plate)].copy()

# 4. Calculate distances (project to metric CRS)
METRIC_CRS = "EPSG:4087"
eq_proj = earthquakes_in_plate.to_crs(METRIC_CRS)

# Filter and combine relevant boundaries
plate_boundaries = gdf_boundaries[
    gdf_boundaries["Name"].str.contains("PA")
].to_crs(METRIC_CRS).geometry.unary_union

# Calculate distances
earthquakes_in_plate["distance_km"] = eq_proj.geometry.distance(plate_boundaries) / 1000.0

# 5. Find the furthest earthquake
furthest_eq = earthquakes_in_plate.nlargest(1, "distance_km").iloc[0]
```

## Filtering by Attributes

```python
# Filter by name or code
pacific_plate = gdf_plates[gdf_plates["PlateName"] == "Pacific"]
pacific_plate_alt = gdf_plates[gdf_plates["Code"] == "PA"]

# Filter boundaries involving a specific plate
pacific_bounds = gdf_boundaries[
    (gdf_boundaries["PlateA"] == "PA") | 
    (gdf_boundaries["PlateB"] == "PA")
]

# String pattern matching
pa_related = gdf_boundaries[gdf_boundaries["Name"].str.contains("PA")]
```

## Performance Tips

1. **Filter before projecting**: Reduce data size before expensive operations
2. **Project once**: Convert to metric CRS once, not in loops
3. **Use `.unary_union`**: Combine geometries before distance calculations
4. **Copy when modifying**: Use `.copy()` when creating filtered DataFrames

```python
# Good: Filter first, then project
small_subset = gdf_large[gdf_large["region"] == "Pacific"]
small_projected = small_subset.to_crs(METRIC_CRS)

# Avoid: Projecting large dataset just to filter
# gdf_projected = gdf_large.to_crs(METRIC_CRS)
# small_subset = gdf_projected[gdf_projected["region"] == "Pacific"]
```

## Common Pitfalls

| Issue | Problem | Solution |
|-------|---------|----------|
| Distance in degrees | Using EPSG:4326 for distance calculations | Project to EPSG:4087 or similar metric CRS |
| Antimeridian issues | Manual longitude adjustments (±360) | Use geopandas spatial operations, they handle it |
| Slow performance | Calculating distance to each boundary point separately | Use `.unary_union` + single `.distance()` call |
| Missing geometries | Some features have no geometry | Filter with `gdf[gdf.geometry.notna()]` |

## When NOT to Use Manual Calculations

Avoid implementing your own:
- Haversine distance formulas (use geopandas projections instead)
- Point-in-polygon checks (use `.within()`)
- Iterating through boundary points (use `.distance()` with `.unary_union`)

These manual approaches are slower, more error-prone, and less accurate than geopandas methods.

## Best Practices Summary

1. ✅ Load GeoJSON with `gpd.read_file()`
2. ✅ Use `.within()` for spatial filtering
3. ✅ Project to metric CRS (`EPSG:4087`) before distance calculations
4. ✅ Combine geometries with `.unary_union` before distance calculation
5. ✅ Use `.distance()` method for point-to-geometry distances
6. ✅ Use `.nlargest()` / `.nsmallest()` for finding extreme values
7. ❌ Never calculate distances in EPSG:4326
8. ❌ Avoid manual Haversine implementations
9. ❌ Don't iterate through individual boundary points

[Evidence block]
No Skills: `0`
With Skills: `60`
Delta: `60`
Failure summary: geospatial analysis using GeoPandas: filter earthquakes inside Pacific plate, compute max boundary distance, emit JSON
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
Candidate id: orchestration-delegation::round1::differentiating
Candidate mode: differentiating
Pair reason: assigned_support
Next pair plan mode: full_matrix
Use this as a candidate schema rerun, not as an accepted final schema.
