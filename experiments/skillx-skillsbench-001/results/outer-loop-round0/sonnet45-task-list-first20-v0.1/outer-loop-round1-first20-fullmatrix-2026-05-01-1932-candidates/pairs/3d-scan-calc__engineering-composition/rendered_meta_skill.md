[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: engineering-composition
Semantic intent: Compose diagnosis, editing, execution, and verification into a disciplined engineering workflow.
Emphasize:
- diagnose -> patch/edit -> verify sequencing
- tool wrappers and execution infrastructure when build/test/deployment gates matter, not just script orchestration
- explicit precedence and dependency handling
- benchmark / build / test gate awareness
- extract task-specific engineering constraints (build/compile/test/deploy requirements) before adding procedural scaffolding
- make the staged-multi-step workflow assumption explicit when rendering task guidance
- articulate why engineering verification gates (compile/test/benchmark) are load-bearing for this task vs pure output validation
Avoid:
- vague advice that doesn't specify which engineering gates (compile/test/deploy/benchmark) to validate against
- unordered bundles of suggestions
- generic prose that does not tell the agent how to validate changes
- treating all pipeline-structured tasks as engineering tasks without identifying engineering verification gates
Expected good fit:
- build fixes
- migrations
- code implementation tasks with compile/test/benchmark constraints
- tasks requiring code modification with cross-file dependency tracking or compilation
Expected bad fit:
- pure retrieval/synthesis
- simple output formatting tasks
- pure analytical pipelines where the pipeline output is the final deliverable
- tasks with only output-contract or result verification, no build/compile/test gates
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for a engineering-composition task.
Schema intent: Compose diagnosis, editing, execution, and verification into a disciplined engineering workflow.

Outer-loop update mode: differentiating. Keep the Render layer fixed and change only schema-level guidance.

Prioritize:
1. diagnose -> patch/edit -> verify sequencing
2. tool wrappers and execution infrastructure when build/test/deployment gates matter, not just script orchestration
3. explicit precedence and dependency handling
4. benchmark / build / test gate awareness
5. extract task-specific engineering constraints (build/compile/test/deploy requirements) before adding procedural scaffolding
6. make the staged-multi-step workflow assumption explicit when rendering task guidance
7. articulate why engineering verification gates (compile/test/benchmark) are load-bearing for this task vs pure output validation

Avoid:
1. vague advice that doesn't specify which engineering gates (compile/test/deploy/benchmark) to validate against
2. unordered bundles of suggestions
3. generic prose that does not tell the agent how to validate changes
4. treating all pipeline-structured tasks as engineering tasks without identifying engineering verification gates

Good fit when:
- build fixes
- migrations
- code implementation tasks with compile/test/benchmark constraints
- tasks requiring code modification with cross-file dependency tracking or compilation

Bad fit when:
- pure retrieval/synthesis
- simple output formatting tasks
- pure analytical pipelines where the pipeline output is the final deliverable
- tasks with only output-contract or result verification, no build/compile/test gates

Primary failure modes to guard against:
- boundary ambiguity with analytic-pipeline: losing tasks that have pipeline structure but lack clear engineering verification gates

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
Candidate id: engineering-composition::round1::differentiating
Candidate mode: differentiating
Pair reason: boundary_case;competitor_check
Next pair plan mode: full_matrix
Use this as a candidate schema rerun, not as an accepted final schema.
