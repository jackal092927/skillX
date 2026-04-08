[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: retrieval-heavy-synthesis
Semantic intent: Gather evidence from sources, compress it correctly, and synthesize an output without dropping support.
Emphasize:
- retrieval plan and source grounding
- evidence tracking / provenance discipline
- compression without support loss
- abstain / unknown behavior when evidence is insufficient
Avoid:
- unsupported synthesis
- hallucinated joins across sources
- excessive workflow scaffolding that obscures evidence use
Expected good fit:
- information search
- handbook / database grounded QA
- report or answer generation from external sources
Expected bad fit:
- simulator/control tasks
- code patch workflows
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for a retrieval-heavy synthesis task.
Optimize the skill for evidence-grounded synthesis rather than free-form completion.

Prioritize:
1. retrieving the right evidence before answering,
2. keeping track of what each source supports,
3. compressing evidence into the final answer without dropping required support,
4. explicit unknown / abstain behavior when the evidence does not justify completion.

If the task is failing, suspect evidence-loss or unsupported synthesis before adding more procedural bulk.

[Task context block]
Task name: threejs-to-obj
Task summary: You are a helpful 3D programmer who can write scripts to convert the Three.js code into simulation-ready 3D assets that can be imported by Blender. The three.js file is located at `/root/data/object.js` and contains a well-built 3D object represented by multiple functions from the three.js library.
Task constraints:
- seed schema prior: artifact-generation
- verifier mode: deterministic-output-contract
- workflow topology: staged-multi-step
- tool surface regime: tool-heavy-script-optional
- primary pattern: tool-wrapper
- annotation confidence: high
- secondary patterns: pipeline, reviewer
Task output requirements:
- verifier note: deterministic-output-contract
- current skill count: 2

[Current Task skill block]
Current Task skill:
## obj-exporter
---
name: obj-exporter
description: Three.js OBJExporter utility for exporting 3D geometry to Wavefront OBJ format. Use when converting Three.js scenes, meshes, or geometries to OBJ files for use in other 3D software like Blender, Maya, or MeshLab.
---

# OBJExporter Guide

## Basic Structure

OBJ is a text-based 3D geometry format:

```
# Comment
v x y z        # Vertex position
vn x y z       # Vertex normal
f v1 v2 v3     # Face (triangle)
f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3  # Face with texture/normal indices
```

Example:
```
# Cube
v 0 0 0
v 1 0 0
v 1 1 0
v 0 1 0
f 1 2 3
f 1 3 4
```

## Three.js OBJExporter

Three.js provides `OBJExporter` in examples:

```javascript
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter.js';

const exporter = new OBJExporter();
const objString = exporter.parse(object3D);

// Write to file (Node.js)
import fs from 'fs';
fs.writeFileSync('output.obj', objString);
```

## Exporting with World Transforms

To export geometry in world coordinates:

```javascript
// Update world matrices first
root.updateMatrixWorld(true);

// Clone and transform geometry
const worldGeometry = mesh.geometry.clone();
worldGeometry.applyMatrix4(mesh.matrixWorld);

// Create new mesh for export
const exportMesh = new THREE.Mesh(worldGeometry);
const objData = exporter.parse(exportMesh);
```

## Merging Multiple Geometries

```javascript
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';

const geometries = [];
root.traverse((obj) => {
  if (obj instanceof THREE.Mesh) {
    const geom = obj.geometry.clone();
    geom.applyMatrix4(obj.matrixWorld);
    geometries.push(geom);
  }
});

const merged = mergeGeometries(geometries);
const mergedMesh = new THREE.Mesh(merged);
const objData = exporter.parse(mergedMesh);
```

## Node.js ES Module Setup

For running Three.js in Node.js:

```json
// package.json
{ "type": "module" }
```

```javascript
// script.js
import * as THREE from 'three';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter.js';
```

## threejs
---
name: threejs
description: Three.js scene-graph parsing and export workflows: mesh baking, InstancedMesh expansion, part partitioning, per-link OBJ export, and URDF articulation.
---

# Three.js Scene Graph + Export

## Quick start

1) Load the module, call `createScene()`, then `updateMatrixWorld(true)`.
2) Treat **named `THREE.Group` nodes as parts/links**.
3) Assign each mesh to its **nearest named ancestor**.
4) Bake world transforms into geometry before export.
5) Export per-part OBJ (and optionally URDF) using deterministic ordering.

## Scene graph essentials

```
Object3D (root)
├── Group (part)
│   ├── Mesh
│   └── Group (child part)
│       └── Mesh
└── Group (another part)
    └── Mesh
```

- `THREE.Scene` / `THREE.Object3D`: containers
- `THREE.Group`: logical part (no geometry)
- `THREE.Mesh`: geometry + material

## Part partitioning rules

- Parts are **named groups** at any depth.
- Each mesh belongs to the **nearest named ancestor**.
- Nested named groups are separate parts; **do not merge** their meshes into parents.
- Skip empty parts; sort part names for determinism.

```javascript
function buildPartMap(root) {
  const parts = new Map();
  root.traverse((obj) => {
    if (obj.isGroup && obj.name) parts.set(obj.name, { group: obj, meshes: [] });
  });
  root.traverse((obj) => {
    if (!obj.isMesh) return;
    let parent = obj.parent;
    while (parent && !(parent.isGroup && parent.name)) parent = parent.parent;
    if (parent && parts.has(parent.name)) parts.get(parent.name).meshes.push(obj);
  });
  return Array.from(parts.values()).filter((p) => p.meshes.length > 0);
}
```

## Mesh baking (world transforms)

Always bake transforms before export:

```javascript
root.updateMatrixWorld(true);
let geom = mesh.geometry.clone();
geom.applyMatrix4(mesh.matrixWorld);
if (geom.index) geom = geom.toNonIndexed();
if (!geom.attributes.normal) geom.computeVertexNormals();
```

### InstancedMesh expansion

```javascript
const tempMatrix = new THREE.Matrix4();
const instanceMatrix = new THREE.Matrix4();
obj.getMatrixAt(i, instanceMatrix);
tempMatrix.copy(obj.matrixWorld).multiply(instanceMatrix);
```

### Axis conversion (Y-up to Z-up)

```javascript
const axisMatrix = new THREE.Matrix4().makeRotationX(-Math.PI / 2);
geom.applyMatrix4(axisMatrix);
```

## Per-part OBJ export

- Collect meshes owned by each part.
- **Do not traverse into child named groups** when exporting a part.
- Merge baked geometries per part and write `<part>.obj`.

Reference: `references/link-export-rules.md`.

## Relation between Three.js and URDF articulation

- Use named groups as links.
- Parent is the nearest named ancestor link.
- Joint type defaults to `fixed` unless evidence suggests `revolute`/`prismatic`.
- Sort link and joint names for determinism.

References:
- `references/joint-type-heuristics.md`
- `references/urdf-minimal.md`

## Scripts

- InstancedMesh OBJ exporter: `node scripts/export_instanced_obj.mjs`
- Per-link OBJ exporter: `node scripts/export_link_objs.mjs --input <scene_js> --out-dir <dir>`
- URDF builder: `node scripts/build_urdf_from_scene.mjs --input <scene_js> --output <file.urdf> --mesh-dir <mesh_dir>`

Adjust inputs/outputs inside scripts as needed.

[Evidence block]
No Skills: `20`
With Skills: `60`
Delta: `40`
Failure summary: task is centered on writing/export tooling that converts a Three.js-defined object into a Blender-ready OBJ with coordinate-frame adjustment
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
