# SkillX Meta-Schema Proposal: `metric-gated-scientific-pipeline` v0.1

## Purpose

Propose a new SkillX meta-schema for a narrow subset of `analytic-pipeline`
tasks where:

- correctness is only weakly visible from the final artifact shape,
- upstream scientific / measurement quality dominates downstream score,
- the verifier applies a benchmark threshold or simulation-quality gate rather
  than a simple exact-answer contract,
- small stage errors can collapse the final score from "passable" to `0`.

This proposal is motivated by the negative-lift failure on
`earthquake-phase-association`, but the intended category is broader than that
single task.

## Recommendation

Do **not** introduce a broad category like `scientific-discovery`.

That label is too wide and does not match the operational failure mode seen in
SkillsBench. The relevant pattern is not novelty-oriented research. It is:

> tasks that run an end-to-end scientific or measurement pipeline whose success
> is exposed mainly through a metric gate.

Recommended category id:

- `metric-gated-scientific-pipeline`

Recommended short name:

- Metric-Gated Scientific Pipeline

## Why Existing `analytic-pipeline` Is Not Enough

The current `analytic-pipeline` prior says:

- make the skill more stage-structured,
- preserve stage handoffs,
- add intermediate artifacts and checks.

That is directionally right, but too generic for tasks where the main risk is:

1. losing domain-specific measurement fidelity,
2. optimizing the final artifact instead of the metric path,
3. rewriting away incumbent domain bundle structure,
4. confusing runtime failure with measured low quality.

In `earthquake-phase-association`, the task is not merely "multi-stage." It is:

- waveform loading,
- deep-learning phase picking,
- event association,
- timestamp emission,
- F1-thresholded evaluation.

The same broad `analytic-pipeline` prior also covers tasks like
`earthquake-plate-calculation`, which is much more deterministic and artifact
contract oriented. Those two tasks are not rewrite-equivalent even though both
are stage-heavy.

## Evidence Slice

### Exact `analytic-pipeline + benchmark-threshold` tasks in current annotations

There are only 4 tasks in the current exact slice:

1. `civ6-adjacency-optimizer`
2. `earthquake-phase-association`
3. `manufacturing-fjsp-optimization`
4. `seismic-phase-picking`

This slice is small, so the proposed family should also use the benchmark's
working-hypothesis labels such as `threshold-fragile` and
`stage-handoff-break`.

### Relevant task-profile hypotheses already present in repo

The following tasks are already tagged as `threshold-fragile` and/or
`stage-handoff-break` in
`docs/plans/skillx/skillsbench-task-profile-annotations-v0.1.md`:

- `seismic-phase-picking`
- `glm-lake-mendota`
- `adaptive-cruise-control`
- `r2r-mpc-control`
- `trend-anomaly-causal-inference`
- `data-to-d3`
- `speaker-diarization-subtitles`
- `shock-analysis-demand`

Only some of these should enter this new family. The proposal is **not** "all
threshold-fragile tasks." It is the narrower scientific / measurement subset.

## Proposed Inclusion Rule

A task belongs in `metric-gated-scientific-pipeline` if most of the following
are true:

1. The task starts from raw or noisy observational / experimental / simulation
   data rather than already-clean symbolic inputs.
2. The main score depends on latent quality of one or more intermediate
   scientific measurement stages.
3. The verifier is threshold-like or quality-gated:
   F1, RMSE, simulation success + metric threshold, detection accuracy, etc.
4. The final artifact is not by itself a reliable proxy for correctness.
5. Domain-specific defaults, calibration choices, or preprocessing decisions
   materially affect score.
6. A bundled incumbent skillpack contains several narrow domain skills whose
   interaction matters.

## Proposed Exclusion Rule

Do **not** assign tasks here if they are mainly:

- exact JSON / CSV / text contract tasks where correctness is explicit in the
  final output,
- code repair / compile-test / patch validation tasks,
- control / planning tasks where the main difficulty is action sequencing
  rather than preserving scientific measurement fidelity,
- retrieval-heavy reporting tasks where evidence synthesis dominates the work.

## Candidate Tasks

### Strong candidates

These are the clearest initial members:

1. `earthquake-phase-association`
   - raw waveform -> pick -> associate -> event times -> F1 gate
2. `seismic-phase-picking`
   - raw traces -> P/S picks -> F1 gate
3. `glm-lake-mendota`
   - scientific simulation setup/tuning -> netCDF output -> RMSE threshold
4. `exoplanet-detection-period`
   - noisy lightcurve preprocessing -> period discovery -> tolerance gate

### Medium-confidence candidates

These may belong, but need one more pass of task-level inspection:

1. `trend-anomaly-causal-inference`
   - multi-stage quantitative analysis with correctness bottlenecked by valid
     intermediate data prep and anomaly estimation
2. `flood-risk-analysis`
   - likely scientific analysis, but current note suggests over-scaffolding may
     hurt more than help

### Likely not in this category

These are fragile or metric-gated, but probably belong elsewhere:

1. `adaptive-cruise-control`
   - better fit for `environment-control`
2. `r2r-mpc-control`
   - better fit for `environment-control`
3. `manufacturing-fjsp-optimization`
   - better fit for optimization / scheduling pipeline, not scientific
     measurement
4. `civ6-adjacency-optimizer`
   - benchmark-thresholded, but not scientific / measurement oriented

## Family-Level Failure Modes

The new schema should suspect these failure modes first:

1. The rewrite preserves stage order but drops crucial domain subskills.
2. The rewrite makes the skill more generic and less calibrated.
3. The rewrite emphasizes output placement over metric-sensitive preprocessing.
4. The rewrite omits intermediate metric probes or sanity checks.
5. The tuning system records runtime exceptions as `0.0` and they are mistaken
   for real measured low quality.
6. The rewrite collapses a domain bundle into one monolithic instruction block
   and loses task-local tool selection knowledge.

## Distinctive Rewrite Prior

Relative to `analytic-pipeline`, this schema should shift the rewrite prior
toward:

- metric path preservation over generic stage structure,
- domain calibration over generic decomposition,
- intermediate observability over polished final reporting,
- incumbent bundle preservation over aggressive consolidation,
- verifier evidence clarity over superficial completion.

## Proposed Prompt-Bank Entry

```yaml
category_id: metric-gated-scientific-pipeline
semantic_intent: Run a scientific or measurement pipeline where upstream data-processing fidelity is exposed mainly through a final metric gate rather than a deterministic output contract.
emphasize:
  - preserve the end-to-end measurement chain, not just the final artifact
  - explicit metric target, threshold, and what upstream stages most affect it
  - domain-calibrated preprocessing, model/tool choice, and parameter defaults
  - stage-level observability such as counts, distributions, spot checks, and quick metric probes
  - preserving useful incumbent bundle structure when multiple narrow domain skills jointly matter
  - separating runtime failure evidence from measured low-quality evidence
avoid:
  - rewriting the task as a generic stage checklist with weak domain content
  - optimizing output formatting while neglecting the metric path
  - collapsing several domain-specific skills into one vague synthetic blob
  - assuming a score of 0 means true measured failure when verifier evidence is missing
  - overconfident parameter invention without sanity checks against the task's metric
expected_good_fit:
  - scientific signal extraction and event detection tasks
  - simulation or calibration tasks with RMSE/F1/quality thresholds
  - observational-data pipelines where preprocessing quality dominates final score
expected_bad_fit:
  - deterministic exact-answer analysis tasks
  - code patch / compile-test loops
  - action-planning or control tasks where state/action sequencing is the main bottleneck
meta_prompt: |
  You are revising a skill for a metric-gated scientific pipeline task.
  Optimize the skill to preserve the metric-sensitive scientific workflow, not merely to make it more staged or more polished.

  Prioritize:
  1. preserving the full upstream-to-downstream measurement chain,
  2. naming the true target metric, threshold, and the stages that most affect it,
  3. keeping domain-specific defaults, preprocessing rules, and calibration guidance explicit,
  4. adding lightweight observability checks on intermediate outputs before finalization,
  5. preserving multiple incumbent subskills when they jointly support the metric path,
  6. distinguishing runtime failure from genuine low metric performance.

  If the task is failing, first suspect:
  - loss of domain calibration,
  - dropped upstream measurement steps,
  - or missing intermediate metric checks,
  before adding broader generic scaffolding.
```

## What This Schema Should Change In Practice

For tasks in this family, the rewrite should usually push the task skill toward:

1. A named metric section.
   Example: "Target metric is F1 over event times with 5-second tolerance."

2. An upstream critical-path section.
   Example: "Bad picks guarantee bad association; do not optimize association in
   isolation."

3. Intermediate artifact expectations.
   Example: pick counts, event counts, coverage by trace/station, quick
   spot-check tables, simulation diagnostics, residual summaries.

4. Conservative domain defaults.
   Example: preserve known-good model families, tolerances, coordinate
   transforms, or filtering rules unless there is evidence to change them.

5. A runtime-evidence clause.
   Example: if the verifier did not produce clean metric evidence, do not treat
   the observed score as a genuine quality signal.

## Initial Assignment Proposal

### Assign now

- `earthquake-phase-association`
- `seismic-phase-picking`
- `glm-lake-mendota`
- `exoplanet-detection-period`

### Hold for review

- `trend-anomaly-causal-inference`
- `flood-risk-analysis`

### Keep in current schemas

- `adaptive-cruise-control` -> `environment-control`
- `r2r-mpc-control` -> `environment-control`
- `manufacturing-fjsp-optimization` -> `analytic-pipeline` or a future
  optimization-specific subclass
- `civ6-adjacency-optimizer` -> `analytic-pipeline`

## Validation Plan

The proposal is only useful if it yields distinct prompt behavior from
`analytic-pipeline`.

Minimum validation:

1. Re-render the rewrite prompt for the 4 strong candidates under both
   `analytic-pipeline` and `metric-gated-scientific-pipeline`.
2. Check that the new prompt explicitly adds:
   - metric naming,
   - upstream critical-path preservation,
   - intermediate observability,
   - runtime-vs-quality separation.
3. Run a narrow A/B on:
   - `earthquake-phase-association`
   - `seismic-phase-picking`
   - `glm-lake-mendota`
4. Reject the schema if it does not produce behavior meaningfully different from
   `analytic-pipeline`.

## Bottom Line

The benchmark evidence does support a narrower family, but the right abstraction
is not "science" in general. It is:

> scientific / measurement pipelines whose success is revealed through metric
> gates and whose failure often comes from losing domain-specific upstream
> fidelity.

That is a real enough pattern to justify a trial meta-schema.
