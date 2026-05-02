[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: analytic-pipeline
Semantic intent: Run an ordered analysis pipeline where intermediate processing quality strongly affects final correctness.
Emphasize:
- stage decomposition and stage ordering
- explicit intermediate validation when downstream stages depend on upstream output quality or correctness
- handoff integrity between stages
- final output tied back to pipeline evidence
- the quality-cascade property: intermediate processing quality determines downstream correctness
- explicit schema boundary: choose this when stage output quality matters for later stages, not just final artifact structure
- extract task-specific stage dependencies and failure modes before adding generic pipeline scaffolding
Avoid:
- collapsing multiple sensitive transforms into one vague step
- skipping intermediate validation
- overly generic prose-only guidance
- treating single-artifact generation as a pipeline when only the final output contract matters
Expected good fit:
- scientific / signal / video / security analysis workflows
- ordered transformation + measurement tasks
- multi-stage workflows where intermediate processing errors propagate to final output quality
Expected bad fit:
- simple one-shot artifact tasks
- pure code patch / compile-test loops
- single-artifact tasks where all verification occurs on the final output only
- form-filling or template tasks where stage ordering is arbitrary or cosmetic
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for a analytic-pipeline task.
Schema intent: Run an ordered analysis pipeline where intermediate processing quality strongly affects final correctness.

Outer-loop update mode: differentiating. Keep the Render layer fixed and change only schema-level guidance.

Prioritize:
1. stage decomposition and stage ordering
2. explicit intermediate validation when downstream stages depend on upstream output quality or correctness
3. handoff integrity between stages
4. final output tied back to pipeline evidence
5. the quality-cascade property: intermediate processing quality determines downstream correctness
6. explicit schema boundary: choose this when stage output quality matters for later stages, not just final artifact structure
7. extract task-specific stage dependencies and failure modes before adding generic pipeline scaffolding

Avoid:
1. collapsing multiple sensitive transforms into one vague step
2. skipping intermediate validation
3. overly generic prose-only guidance
4. treating single-artifact generation as a pipeline when only the final output contract matters

Good fit when:
- scientific / signal / video / security analysis workflows
- ordered transformation + measurement tasks
- multi-stage workflows where intermediate processing errors propagate to final output quality

Bad fit when:
- simple one-shot artifact tasks
- pure code patch / compile-test loops
- single-artifact tasks where all verification occurs on the final output only
- form-filling or template tasks where stage ordering is arbitrary or cosmetic

Primary failure modes to guard against:
- boundary ambiguity with artifact-generation when both schemas fit but artifact-generation workflow is more natural for single-output tasks
- over-matching on generator tasks that have review steps but no quality-cascade between stages

Regenerate task-specific skill guidance from these slots; do not invent a new policy outside them.

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

[Outer-loop candidate block]
Source round: outer-loop-round0
Next round: outer-loop-round1
Candidate id: analytic-pipeline::round1::differentiating
Candidate mode: differentiating
Pair reason: boundary_case
Next pair plan mode: full_matrix
Use this as a candidate schema rerun, not as an accepted final schema.
