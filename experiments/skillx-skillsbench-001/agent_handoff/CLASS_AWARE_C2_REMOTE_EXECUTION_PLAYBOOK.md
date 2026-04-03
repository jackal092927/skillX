# Class-Aware C2 Remote Execution Playbook

Treat all paths below as repo-root relative.

## 1. Mission

Execute the first direct class-aware comparison pilot for four tasks under four conditions:
- `C0`
- `C1`
- `C2`
- `C2A`

Frozen tasks:
1. `offer-letter-generator`
2. `parallel-tfidf-search`
3. `trend-anomaly-causal-inference`
4. `taxonomy-tree-merge`

## 2. Preflight

Before running anything, record in `runs/class-aware-c2-comparison-pilot-001/ENVIRONMENT_NOTES.md`:
- hostname / OS
- repo path
- SkillsBench repo path
- Docker availability
- `uv` availability
- benchmark agent/model
- API-key availability
- task-path mapping for all four tasks

If any required item is missing, stop and write a blocker.

## 3. Condition sources

Use these sources exactly:
- `C0` — isolated task copy with skill directory disabled or removed
- `C1` — benchmark task as shipped
- `C2` — generic minimal skillpack under `materialized_skillpacks/<task>/c2_minimal/...`
- `C2A` — class-aware minimal skillpack under `materialized_skillpacks/<task>/c2_class_aware/...`

## 4. Isolation rule

Do not mutate the benchmark repo in place.
Use one isolated condition sandbox per `(task, condition)` pair, or an equivalent reversible isolated copy.

## 5. Recommended order

For each task:
1. run `C0`
2. run `C1`
3. run `C2`
4. run `C2A`
5. normalize the result immediately

Why this order:
- baseline first,
- then original skill,
- then generic SkillX,
- then class-aware SkillX.

## 6. Result capture

For each `(task, condition)` record at least:
- task id
- condition id
- skill source path
- benchmark agent
- model
- timestamp start/end
- exit status
- verifier result / reward / score
- log path
- one-sentence interpretation

Write structured outputs to the pilot run folder.

## 7. Pilot-specific question

For every task, answer:
- Is `C2A` structurally cleaner than `C2`?
- Does `C2A` appear to help, hurt, or do nothing relative to `C2`?
- If it hurts, does the failure look class-specific or accidental?

## 8. Success criteria

The pilot succeeds if:
- all comparison conditions are wired cleanly,
- the `C2A` packaging is unambiguous,
- and the resulting differences are interpretable enough to decide whether class-aware C3/C4 is worth pursuing.
