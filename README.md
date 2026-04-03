# SkillX

SkillX is the standalone repository for the skill-specification, rewrite, and bounded-refinement line that was incubated inside MARC.

This repo intentionally contains:

- core SkillX design docs
- SkillsBench rewrite and C4AR experiment assets
- the thin Python runtime used to analyze evidence and orchestrate refine rounds
- targeted real experiment fixtures needed by the current tests

This repo intentionally does not vendor the full benchmark substrate. `skillsbench-src` remains an external dependency and should live alongside this repo at:

- `<SKILLSBENCH_ROOT>`

## Layout

- `docs/` design docs, protocols, references, templates
- `experiments/skillx-skillsbench-001/` experiment assets and selected real fixtures
- `src/skillx/` standalone Python package
- `scripts/` rewrite/refine runners and helpers
- `tests/` focused `unittest` coverage

## Development

Use the shared Python 3.14 virtualenv from the MARC repo unless and until this repo gets its own environment:

```bash
<INCUBATOR_REPO_ROOT>/.venv-swebench/bin/python -m unittest discover -s tests
```

Example runner entrypoints:

```bash
<INCUBATOR_REPO_ROOT>/.venv-swebench/bin/python scripts/run_skillx_rewrite_benchmark.py --help
<INCUBATOR_REPO_ROOT>/.venv-swebench/bin/python scripts/run_skillx_refine_benchmark.py --help
```

Both runners expect a local SkillsBench checkout passed through `--skillsbench-root`.
