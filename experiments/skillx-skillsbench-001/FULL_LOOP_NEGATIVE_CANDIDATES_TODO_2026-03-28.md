# Full-Loop Negative Candidates TODO — 2026-03-28

## Goal

Pick one task for the next `C4AR` full-loop validation run where:

- the original benchmark evidence includes a negative skill delta or a strong local negative-transfer signal
- execution is relatively simple, using original task timeout settings as a rough proxy
- `C0` is preferably not `1.0`
- the task is already operationally close enough to run in the current SkillX line

## Important Clarification

`trend-anomaly-causal-inference` already has one clean uninterrupted `R0 -> R3` `C4AR` run in the current project.

The present selection question is therefore narrower:

- find the best next task for an additional full-loop validation run
- prefer a task that is simpler and still tied to negative-transfer motivation

## Immediate Candidate Pool

### Tier 1 — Best fit for the next run

1. `taxonomy-tree-merge`
   - why it fits:
     - official paper-cited negative case: `-39.3pp`
     - local clean baseline exists: `C0 = 0.6481` in `negative-transfer-candidate-check-001`
     - `C0` is not `1.0`
     - shortest timeout profile among the paper-cited negative cases already in the current SkillX line:
       - verifier `180s`
       - agent `500s`
       - build `200s`
     - existing SkillX assets already present:
       - rewrite registry
       - materialized `c2_class_aware`
       - prior `C4AR` execution history
   - main risk:
     - this task has shown runtime-policy sensitivity
     - local negative replay and later adjusted replay disagree on sign
   - use case:
     - best match if we want a negative-transfer-motivated task with `C0 != 1.0` and a relatively short benchmark envelope

### Tier 2 — Strong backup if we want a more stable negative anchor

2. `trend-anomaly-causal-inference`
   - why it fits:
     - official paper-cited negative case: `-12.9pp`
     - local adjusted canonical replay remains negative: `1.0 -> 0.7444`
     - timeout profile is still relatively short on verifier/build:
       - verifier `200s`
       - agent `900s`
       - build `200s`
     - existing SkillX assets already present
     - already proven to run cleanly through `R0 -> R3`
   - downside:
     - `C0` is `1.0` in the adjusted canonical replay
     - it does not satisfy the preferred `C0 != 1.0` condition
     - because it already proved the loop once, it is less informative as a new demonstration target

### Tier 3 — Keep for later, not first choice for the next full-loop proof

3. `exoplanet-detection-period`
   - why it stays on the list:
     - official paper-cited negative case: `-11.4pp`
     - clean historical `C0 = 0.0`
     - existing SkillX assets already present
   - why not first:
     - long timeout profile:
       - verifier `900s`
       - agent `1200s`
       - build `900s`
     - local evidence remains nondiscriminative / zero-valued
     - poor choice if the main objective is to maximize odds of a clean fast full-loop demonstration

4. `energy-ac-optimal-power-flow`
   - why it stays on the list:
     - official paper-cited negative case: `-14.3pp`
     - existing SkillX assets already present
   - why not first:
     - `C0` is not currently a clean comparator in our local line
     - long timeout profile:
       - verifier `900s`
       - agent `900s`
       - build `600s`
     - current class-aware `R0` evidence is already positive and saturated at `1.0`
     - weak fit for “find a simple negative-transfer task to prove the loop”

## Secondary Batch Candidates

These are useful for a later batch but weaker for the immediate full-loop proof:

1. `parallel-tfidf-search`
   - existing SkillX assets are present
   - local replay did not preserve the expected negative-transfer anecdote
   - keep only as a low-confidence later-batch candidate

2. `powerlifting-coef-calc`
   - local paired replay in project tracking showed `1.0 -> 0.0`
   - task difficulty is `easy`
   - timeout profile is moderate:
     - verifier `600s`
     - agent `600s`
     - build `600s`
   - not a preferred immediate candidate because:
     - `C0 = 1.0`
     - it is not part of the current prepared SkillX task line

## C0 Availability Check

Current status for the main immediate candidates:

- `taxonomy-tree-merge`
  - yes, already reported
  - clean `C0 = 0.6481`
- `trend-anomaly-causal-inference`
  - yes, already reported
  - `C0 = 0.95` in one local replay, `1.0` in adjusted canonical replay
- `exoplanet-detection-period`
  - yes, already reported
  - clean `C0 = 0.0`
- `energy-ac-optimal-power-flow`
  - no clean `C0` comparator for current use
  - historical no-skill reference remains timeout contaminated

Therefore:

- no immediate `C0` rerun is required before choosing between `taxonomy` and `trend`
- a fresh `C0` rerun would only be needed if we insisted on reviving `energy` as the selection target

## Recommended Next Action

If the goal is:

- **best match to the stated criteria**: pick `taxonomy-tree-merge`
- **highest confidence of another clean full-loop execution right away**: pick `trend-anomaly-causal-inference`

My current recommendation is:

1. choose `taxonomy-tree-merge` as the primary next full-loop candidate
2. keep `trend-anomaly-causal-inference` as the fallback safety candidate
3. do not spend time rerunning `C0` before that choice, because the needed `C0` evidence is already available for both

## Later Session Override

This recommendation was later superseded by an explicit user preference:

- prioritize a task that had **not** previously been run in the current `C4AR` line
- accept a weaker prior confidence ranking if that produced a cleaner "new-task full-loop" validation

Under that later preference, the project selected:

- `parallel-tfidf-search`

Follow-up execution then happened in:

- `<INCUBATOR_REPO_ROOT>/experiments/skillx-skillsbench-001/runs/parallel-tfidf-full-loop-001`
