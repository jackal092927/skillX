# SkillX Index

This file is the shortest path for new collaborators.

## License

This repository is public for inspection and authorized collaboration only.
Commercial use, copying, redistribution, and derivative use are restricted by
the `LICENSE` file.

## Start Here

1. `README.md`
2. `INDEX.md`
3. `docs/INDEX.md`
4. `experiments/skillx-skillsbench-001/README.md`

If you are working on C4AR specifically, then read next:

5. `experiments/skillx-skillsbench-001/playbooks/C4AR_ROLE_A_SESSION_DISTILL_PLAYBOOK.md`
6. `experiments/skillx-skillsbench-001/playbooks/C4AR_ROLE_B_REFINE_BRAIN_PLAYBOOK.md`
7. `scripts/run_skillx_refine_benchmark.py`

If you are working on rewrite experiments first, then read instead:

5. `experiments/skillx-skillsbench-001/C2_REWRITE_PROTOCOL.md`
6. `experiments/skillx-skillsbench-001/C3_REWRITE_PROTOCOL.md`
7. `scripts/run_skillx_rewrite_benchmark.py`

If you are working on the newer meta-schema / outer-loop planning line, then
read:

5. `docs/checkpoints/INDEX.md`
6. `docs/plans/skillx/INDEX.md`
7. `docs/research/deep-dives/INDEX.md`

If you are actively developing, running experiments in parallel, or
coordinating multiple sessions or collaborators, then also read:

8. `docs/plans/skillx/skillx-parallel-development-playbook-v0.1.md`
9. `docs/plans/skillx/skillx-round0-mxn-runbook-v0.1.md`

## Repository Map

- `docs/`: design docs, references, checkpoints, deep dives, and planning material
- `docs/plans/skillx/`: newer SkillX planning line imported from MARC
- `docs/checkpoints/`: compact handoff checkpoints for the current framing
- `docs/research/deep-dives/`: external baseline and comparison memos
- `experiments/skillx-skillsbench-001/`: the active SkillsBench experiment line
- `src/skillx/`: the standalone SkillX Python package
- `src/skillx/c4ar/`: C4AR contracts, roles, and orchestrator
- `scripts/`: executable runners and support utilities
- `tests/`: focused `unittest` coverage for the extracted scope

## What Is Actually Standalone

Included in this repo:

- SkillX package code
- C4AR inner-loop code
- C4AR playbooks
- rewrite/refine scripts
- experiment protocols
- selected real fixtures used by tests

External at runtime:

- SkillsBench workspace
- Docker
- `uv`
- `codex`
- Claude Code OAuth token file
- model/API credentials required by the benchmark stack

## Canonical Commands

Install locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

Show CLI help:

```bash
python scripts/run_skillx_rewrite_benchmark.py --help
python scripts/run_skillx_refine_benchmark.py --help
```

## SkillsBench Links

- Website: <https://www.skillsbench.ai>
- GitHub: <https://github.com/benchflow-ai/skillsbench>
- Harbor docs: <https://harborframework.com/docs>

## Practical Warning

Some archived handoff notes still contain historical absolute paths from the incubation repo. When those notes disagree with the current repo layout, trust:

1. `README.md`
2. `INDEX.md`
3. the live code under `src/` and `scripts/`
