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
Task name: data-to-d3
Task summary: Please use D3.js (v6) to visualize input data stored at `/root/data/stock-descriptions.csv` and `/root/data/indiv-stock/` for company stock details and individual stock price histories. Please return the output as a single-page web app at `/root/output/index.html`. I should be able to open it in a web browser.
Task constraints:
- seed schema prior: artifact-generation
- verifier mode: deterministic-artifact-plus-stage-check
- workflow topology: staged-multi-step
- tool surface regime: tool-medium
- primary pattern: pipeline
- annotation confidence: high
- secondary patterns: generator, reviewer
Task output requirements:
- verifier note: deterministic-artifact-plus-stage-check
- current skill count: 1

[Current Task skill block]
Current Task skill:
## d3-visualization
---
name: d3js-visualization
description: Build deterministic, verifiable data visualizations with D3.js (v6). Generate standalone HTML/SVG (and optional PNG) from local data files without external network dependencies. Use when tasks require charts, plots, axes/scales, legends, tooltips, or data-driven SVG output.
---

# D3.js Visualization Skill

Use this skill to turn structured data (CSV/TSV/JSON) into **clean, reproducible** visualizations using **D3.js**. The goal is to produce **stable outputs** that can be verified by diffing files or hashing.

## When to use

Activate this skill when the user asks for any of the following:

- “Make a chart/plot/graph/visualization”
- bar/line/scatter/area/histogram/box/violin/heatmap
- timelines, small multiples, faceting
- axis ticks, scales, legends, tooltips
- data-driven SVG output for a report or web page
- converting data to a static SVG or HTML visualization

If the user only needs a quick table or summary, **don’t** use D3—use a spreadsheet or plain markdown instead.

---

## Inputs you should expect

- One or more local data files: `*.csv`, `*.tsv`, `*.json`
- A chart intent:
  - chart type (or you infer the best type)
  - x/y fields and aggregation rules
  - sorting/filtering rules
  - dimensions (width/height) and margins
  - color rules (categorical / sequential)
  - any labeling requirements (title, axis labels, units)
- Output constraints:
  - “static only”, “no animation”, “must be deterministic”, “offline”, etc.

If details are missing, **make reasonable defaults** and document them in comments near the top of the output file.

---

## Outputs you should produce

Prefer producing **all of** the following when feasible:

1. `dist/chart.html` — standalone HTML that renders the visualization
2. `dist/chart.svg` — exported SVG (stable and diff-friendly)
3. (Optional) `dist/chart.png` — if the task explicitly needs a raster image

Always keep outputs in a predictable folder (default: `dist/`), unless the task specifies paths.

---

## Determinism rules (non-negotiable)

To keep results stable across runs and machines:

### Data determinism
- **Sort** input rows deterministically before binding to marks (e.g., by x then by category).
- Use stable grouping order (explicit `Array.from(grouped.keys()).sort()`).
- Avoid locale-dependent formatting unless fixed (use `d3.format`, `d3.timeFormat` with explicit formats).

### Rendering determinism
- **No randomness**: do not use `Math.random()` or `d3-random`.
- **No transitions/animations** by default (transitions can introduce timing variance).
- **Fixed** `width`, `height`, `margin`, `viewBox`.
- Use **explicit tick counts** only when needed; otherwise rely on D3 defaults but keep domains fixed.
- Avoid layout algorithms with non-deterministic iteration unless you control seeds/iterations (e.g., force simulation). If a force layout is required:
  - fix the tick count,
  - fix initial positions deterministically (e.g., sorted nodes placed on a grid),
  - run exactly N ticks and stop.

### Offline + dependency determinism
- Do **not** load D3 from a CDN.
- Pin D3 to a specific version (default: **d3@7.9.0**).
- Prefer vendoring a minified D3 bundle (e.g., `vendor/d3.v7.9.0.min.js`) or bundling with a lockfile.

### File determinism
- Stable SVG output:
  - Avoid auto-generated IDs that may change.
  - If you must use IDs (clipPath, gradients), derive them from stable strings (e.g., `"clip-plot"`).
- Use LF line endings.
- Keep numeric precision consistent (e.g., round to 2–4 decimals if needed).

---

## Recommended project layout

If the task doesn't specify an existing structure, use:

```
dist/
  chart.html        # standalone HTML with inline or linked JS/CSS
  chart.svg         # exported SVG (optional but nice)
  chart.png         # rasterized (optional)
vendor/
  d3.v7.9.0.min.js  # pinned D3 library
```

---

## Interactive features (tooltips, click handlers, hover effects)

When the task requires interactivity (e.g., tooltips on hover, click to highlight):

### Tooltip pattern (recommended)

1. **Create a tooltip element** in HTML:
```html
<div id="tooltip" class="tooltip"></div>
```

2. **Style with CSS** using `.visible` class for show/hide:
```css
.tooltip {
    position: absolute;
    padding: 10px;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    border-radius: 4px;
    pointer-events: none;  /* Prevent mouse interference */
    opacity: 0;
    transition: opacity 0.2s;
    z-index: 1000;
}

.tooltip.visible {
    opacity: 1;  /* Show when .visible class is added */
}
```

3. **Add event handlers** to SVG elements:
```javascript
svg.selectAll('circle')
    .on('mouseover', function(event, d) {
        d3.select('#tooltip')
            .classed('visible', true)  // Add .visible class
            .html(`<strong>${d.name}</strong><br/>${d.value}`)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px');
    })
    .on('mouseout', function() {
        d3.select('#tooltip').classed('visible', false);  // Remove .visible class
    });
```

**Key points:**
- Use `opacity: 0` by default (not `display: none`) for smooth transitions
- Use `.classed('visible', true/false)` to toggle visibility
- `pointer-events: none` prevents tooltip from blocking mouse events
- Position tooltip relative to mouse with `event.pageX/pageY`

### Click handlers for selection/highlighting

```javascript
// Add 'selected' class on click
svg.selectAll('.bar')
    .on('click', function(event, d) {
        // Remove previous selection
        d3.selectAll('.bar').classed('selected', false);
        // Add to clicked element
        d3.select(this).classed('selected', true);
    });
```

CSS for highlighting:
```css
.bar.selected {
    stroke: #000;
    stroke-width: 3px;
}
```

### Conditional interactivity

Sometimes only certain elements should be interactive:
```javascript
.on('mouseover', function(event, d) {
    // Example: Don't show tooltip for certain categories
    if (d.category === 'excluded') {
        return;  // Exit early, no tooltip
    }
    // Show tooltip for others
    showTooltip(event, d);
})
```

---

[Evidence block]
No Skills: `60`
With Skills: `80`
Delta: `20`
Failure summary: task requires a coupled multi-file web artifact with precise D3 chart behavior, layout constraints, and linked interactions
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
Pair reason: full_matrix_eval
Next pair plan mode: full_matrix
Use this as a candidate schema rerun, not as an accepted final schema.
