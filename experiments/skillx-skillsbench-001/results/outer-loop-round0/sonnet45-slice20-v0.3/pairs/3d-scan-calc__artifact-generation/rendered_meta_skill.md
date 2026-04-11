[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: artifact-generation
Semantic intent: Produce a constrained artifact that must exactly satisfy an output contract.
Emphasize:
- exact output schema / format / placement requirements
- preservation constraints and no-invention discipline
- missing-input detection before finalization
- short final reviewer pass against explicit contract items
Avoid:
- unnecessary multi-stage scaffolding
- speculative filling of unknown fields
- tool usage that is not required by the artifact contract
Expected good fit:
- form filling
- formatting / conversion with strict output expectations
- single-artifact generation or transformation
Expected bad fit:
- benchmark-gated code repair
- control/simulation loops
- deep retrieval-heavy synthesis
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for an artifact-generation task.
Optimize the skill for exactness of the final artifact, not breadth of procedure.

Prioritize:
1. explicit statement of the required output artifact and allowed transformations,
2. no-invention / do-not-guess rules for missing or ambiguous inputs,
3. preservation of formatting, structure, or source truth where required,
4. a short final verification checklist before producing the final artifact.

Keep the skill lean.
Only introduce stages, tools, or wrappers when they are clearly necessary for meeting the artifact contract.

Do not turn the skill into a generic multi-stage workflow if the task is fundamentally a constrained artifact-writing problem.

[Task context block]
Task name: 3d-scan-calc
Task summary: You need to calculate the mass of a 3D printed part. The input (`/root/scan_data.stl`) is a binary STL, but the 2-byte "Attribute Byte Count" at the end of each triangle record is being used to store the **Material ID** of the object. You need to:
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
## mesh-analysis
---
name: mesh-analysis
description: "Analyzes 3D mesh files (STL) to calculate geometric properties (volume, components) and extract attribute data. Use this skill to process noisy 3D scan data and filter debris."
---

# Mesh Analysis

This skill provides the `MeshAnalyzer` tool for robustly processing 3D STL files. It handles Binary STL parsing and connected component analysis.

## When to Use

Use this skill for:
1.  **Geometric Analysis**: Calculating volume of complex or noisy meshes.
2.  **Noise Filtering**: Isolating the largest connected component from "dirty" scan data.
3.  **Attribute Extraction**: Extracting metadata (e.g. material IDs) stored in the STL file attribute bytes.

## Usage

The tool is provided as a Python module in the `scripts/` directory.

### Basic Workflow

```python
import sys
# Add skill path to sys.path
sys.path.append('/root/.claude/skills/mesh-analysis/scripts')

from mesh_tool import MeshAnalyzer

# Initialize with file path
analyzer = MeshAnalyzer('/path/to/your/file.stl')

# Analyze specific components
# Automatically identifies the largest component (main part)
report = analyzer.analyze_largest_component()

volume = report['main_part_volume']
mat_id = report['main_part_material_id']

print(f"Volume: {volume}")
print(f"Material ID: {mat_id}")
```

### Calculating Mass

The tool provides the **Volume** and **Material ID**. To calculate **Mass**:
1.  Read the **Material ID** from the analysis report.
2.  Consult your provided material reference data (e.g. density tables) to find the density.
3.  Calculate: `Mass = Volume * Density`.

**Critical Note on Units**:
*   The **Volume** returned is in the **same units** as the STL file's coordinates (cubed).
*   **Do not assume** millimeters or inches. Check your task instructions for the coordinate system units (e.g., if coordinates are in cm, volume is in cm³).
*   If your density table uses the same unit (e.g., g/cm³ and cm³), **multiply directly**. No unit conversion is needed.

## Critical Notes

*   **Binary Support**: The tool automatically handles Binary STL files.
*   **Attribute extraction**: The tool extracts the 2-byte attribute stored in the binary STL format (often used for color or material ID).

[Evidence block]
No Skills: `80`
With Skills: `80`
Delta: `0`
Failure summary: binary STL parsing, connected-component filtering, material lookup, and mass computation form an ordered geometry-analysis workflow into JSON
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
