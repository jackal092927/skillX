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
Task name: adaptive-cruise-control
Task summary: You need to implement an Adaptive Cruise Control (ACC) simulation that maintains the set speed (30m/s) when no vehicles are detected ahead, and automatically adjusts speed to maintain a safe following distance when a vehicle is detected ahead. The targets are: speed rise time <10s, speed overshoot <5%, speed steady-state error <0.5 m/s, distance steady-state error <2m, minimum distance >5m, control duration 150s. Also consider the constraints: initial speed ~0 m/s, acceleration limits [-8.0, 3.0] m/s^2, time headway 1.5s, minimum gap 10.0m, emergency TTC threshold 3.0s, timestep 0.1s. Data is available in vehicle_params.yaml(Vehicle specs and ACC settings)  and sensor_data.csv (1501 rows (t=0-150s) with columns: time, ego_speed, lead_speed, distance, collected from real-world driving). First, create pid_controller.py to implement the PID controller. Then, create acc_system.py to implement the ACC system and simulation.py to run the vehicle simulation. Next, tune the PID parameters for speed and distance control, saving results in tuning_results.yaml. Finally, run 150s simulations, producing simulation_results.csv and acc_report.md.
Task constraints:
- seed schema prior: environment-control
- verifier mode: benchmark-threshold
- workflow topology: staged-multi-step
- tool surface regime: tool-heavy-script-recommended
- primary pattern: pipeline
- annotation confidence: high
- secondary patterns: tool-wrapper, reviewer
Task output requirements:
- verifier note: benchmark-threshold
- current skill count: 5

[Current Task skill block]
Current Task skill:
## csv-processing
---
name: csv-processing
description: Use this skill when reading sensor data from CSV files, writing simulation results to CSV, processing time-series data with pandas, or handling missing values in datasets.
---

# CSV Processing with Pandas

## Reading CSV

```python
import pandas as pd

df = pd.read_csv('data.csv')

# View structure
print(df.head())
print(df.columns.tolist())
print(len(df))
```

## Handling Missing Values

```python
# Read with explicit NA handling
df = pd.read_csv('data.csv', na_values=['', 'NA', 'null'])

# Check for missing values
print(df.isnull().sum())

# Check if specific value is NaN
if pd.isna(row['column']):
    # Handle missing value
```

## Accessing Data

```python
# Single column
values = df['column_name']

# Multiple columns
subset = df[['col1', 'col2']]

# Filter rows
filtered = df[df['column'] > 10]
filtered = df[(df['time'] >= 30) & (df['time'] < 60)]

# Rows where column is not null
valid = df[df['column'].notna()]
```

## Writing CSV

```python
import pandas as pd

# From dictionary
data = {
    'time': [0.0, 0.1, 0.2],
    'value': [1.0, 2.0, 3.0],
    'label': ['a', 'b', 'c']
}
df = pd.DataFrame(data)
df.to_csv('output.csv', index=False)
```

## Building Results Incrementally

```python
results = []

for item in items:
    row = {
        'time': item.time,
        'value': item.value,
        'status': item.status if item.valid else None
    }
    results.append(row)

df = pd.DataFrame(results)
df.to_csv('results.csv', index=False)
```

## Common Operations

```python
# Statistics
mean_val = df['column'].mean()
max_val = df['column'].max()
min_val = df['column'].min()
std_val = df['column'].std()

# Add computed column
df['diff'] = df['col1'] - df['col2']

# Iterate rows
for index, row in df.iterrows():
    process(row['col1'], row['col2'])
```

## pid-controller
---
name: pid-controller
description: Use this skill when implementing PID control loops for adaptive cruise control, vehicle speed regulation, throttle/brake management, or any feedback control system requiring proportional-integral-derivative control.
---

# PID Controller Implementation

## Overview

A PID (Proportional-Integral-Derivative) controller is a feedback control mechanism used in industrial control systems. It continuously calculates an error value and applies a correction based on proportional, integral, and derivative terms.

## Control Law

```
output = Kp * error + Ki * integral(error) + Kd * derivative(error)
```

Where:
- `error` = setpoint - measured_value
- `Kp` = proportional gain (reacts to current error)
- `Ki` = integral gain (reacts to accumulated error)
- `Kd` = derivative gain (reacts to rate of change)

## Discrete-Time Implementation

```python
class PIDController:
    def __init__(self, kp, ki, kd, output_min=None, output_max=None):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max
        self.integral = 0.0
        self.prev_error = 0.0

    def reset(self):
        """Clear controller state."""
        self.integral = 0.0
        self.prev_error = 0.0

    def compute(self, error, dt):
        """Compute control output given error and timestep."""
        # Proportional term
        p_term = self.kp * error

        # Integral term
        self.integral += error * dt
        i_term = self.ki * self.integral

        # Derivative term
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        d_term = self.kd * derivative
        self.prev_error = error

        # Total output
        output = p_term + i_term + d_term

        # Output clamping (optional)
        if self.output_min is not None:
            output = max(output, self.output_min)
        if self.output_max is not None:
            output = min(output, self.output_max)

        return output
```

## Anti-Windup

Integral windup occurs when output saturates but integral keeps accumulating. Solutions:

1. **Clamping**: Limit integral term magnitude
2. **Conditional Integration**: Only integrate when not saturated
3. **Back-calculation**: Reduce integral when output is clamped

## Tuning Guidelines

**Manual Tuning:**
1. Set Ki = Kd = 0
2. Increase Kp until acceptable response speed
3. Add Ki to eliminate steady-state error
4. Add Kd to reduce overshoot

**Effect of Each Gain:**
- Higher Kp -> faster response, more overshoot
- Higher Ki -> eliminates steady-state error, can cause oscillation
- Higher Kd -> reduces overshoot, sensitive to noise

## simulation-metrics
---
name: simulation-metrics
description: Use this skill when calculating control system performance metrics such as rise time, overshoot percentage, steady-state error, or settling time for evaluating simulation results.
---

# Control System Performance Metrics

## Rise Time

Time for system to go from 10% to 90% of target value.

```python
def rise_time(times, values, target):
    """Calculate rise time (10% to 90% of target)."""
    t10 = t90 = None

    for t, v in zip(times, values):
        if t10 is None and v >= 0.1 * target:
            t10 = t
        if t90 is None and v >= 0.9 * target:
            t90 = t
            break

    if t10 is not None and t90 is not None:
        return t90 - t10
    return None
```

## Overshoot

How much response exceeds target, as percentage.

```python
def overshoot_percent(values, target):
    """Calculate overshoot percentage."""
    max_val = max(values)
    if max_val <= target:
        return 0.0
    return ((max_val - target) / target) * 100
```

## Steady-State Error

Difference between target and final settled value.

```python
def steady_state_error(values, target, final_fraction=0.1):
    """Calculate steady-state error using final portion of data."""
    n = len(values)
    start = int(n * (1 - final_fraction))
    final_avg = sum(values[start:]) / len(values[start:])
    return abs(target - final_avg)
```

## Settling Time

Time to stay within tolerance band of target.

```python
def settling_time(times, values, target, tolerance=0.02):
    """Time to settle within tolerance of target."""
    band = target * tolerance
    lower, upper = target - band, target + band

    settled_at = None
    for t, v in zip(times, values):
        if v < lower or v > upper:
            settled_at = None
        elif settled_at is None:
            settled_at = t

    return settled_at
```

## Usage

```python
times = [row['time'] for row in results]
values = [row['value'] for row in results]
target = 30.0

print(f"Rise time: {rise_time(times, values, target)}")
print(f"Overshoot: {overshoot_percent(values, target)}%")
print(f"SS Error: {steady_state_error(values, target)}")
```

## vehicle-dynamics
---
name: vehicle-dynamics
description: Use this skill when simulating vehicle motion, calculating safe following distances, time-to-collision, speed/position updates, or implementing vehicle state machines for cruise control modes.
---

# Vehicle Dynamics Simulation

## Basic Kinematic Model

For vehicle simulations, use discrete-time kinematic equations.

**Speed Update:**
```python
new_speed = current_speed + acceleration * dt
new_speed = max(0, new_speed)  # Speed cannot be negative
```

**Position Update:**
```python
new_position = current_position + speed * dt
```

**Distance Between Vehicles:**
```python
# When following another vehicle
relative_speed = ego_speed - lead_speed
new_distance = current_distance - relative_speed * dt
```

## Safe Following Distance

The time headway model calculates safe following distance:

```python
def safe_following_distance(speed, time_headway, min_distance):
    """
    Calculate safe distance based on current speed.

    Args:
        speed: Current vehicle speed (m/s)
        time_headway: Time gap to maintain (seconds)
        min_distance: Minimum distance at standstill (meters)
    """
    return speed * time_headway + min_distance
```

## Time-to-Collision (TTC)

TTC estimates time until collision at current velocities:

```python
def time_to_collision(distance, ego_speed, lead_speed):
    """
    Calculate time to collision.

    Returns None if not approaching (ego slower than lead).
    """
    relative_speed = ego_speed - lead_speed

    if relative_speed <= 0:
        return None  # Not approaching

    return distance / relative_speed
```

## Acceleration Limits

Real vehicles have physical constraints:

```python
def clamp_acceleration(accel, max_accel, max_decel):
    """Constrain acceleration to physical limits."""
    return max(max_decel, min(accel, max_accel))
```

## State Machine Pattern

Vehicle control often uses mode-based logic:

```python
def determine_mode(lead_present, ttc, ttc_threshold):
    """
    Determine operating mode based on conditions.

    Returns one of: 'cruise', 'follow', 'emergency'
    """
    if not lead_present:
        return 'cruise'

    if ttc is not None and ttc < ttc_threshold:
        return 'emergency'

    return 'follow'
```

## yaml-config
---
name: yaml-config
description: Use this skill when reading or writing YAML configuration files, loading vehicle parameters, or handling config file parsing with proper error handling.
---

# YAML Configuration Files

## Reading YAML

Always use `safe_load` to prevent code execution vulnerabilities:

```python
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Access nested values
value = config['section']['key']
```

## Writing YAML

```python
import yaml

data = {
    'settings': {
        'param1': 1.5,
        'param2': 0.1
    }
}

with open('output.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
```

## Options

- `default_flow_style=False`: Use block style (readable)
- `sort_keys=False`: Preserve insertion order
- `allow_unicode=True`: Support unicode characters

## Error Handling

```python
import yaml

try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    config = {}  # Use defaults
except yaml.YAMLError as e:
    print(f"YAML parse error: {e}")
    config = {}
```

## Optional Config Loading

```python
import os
import yaml

def load_config(filepath, defaults=None):
    """Load config file, return defaults if missing."""
    if defaults is None:
        defaults = {}

    if not os.path.exists(filepath):
        return defaults

    with open(filepath, 'r') as f:
        loaded = yaml.safe_load(f) or {}

    # Merge loaded values over defaults
    result = defaults.copy()
    result.update(loaded)
    return result
```

[Evidence block]
No Skills: `0`
With Skills: `0`
Delta: `0`
Failure summary: controller design, simulation, tuning, and metric targets form an ordered control-system workflow
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
Pair reason: assigned_support;boundary_case;competitor_check
Next pair plan mode: full_matrix
Use this as a candidate schema rerun, not as an accepted final schema.
