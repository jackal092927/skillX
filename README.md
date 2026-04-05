# SkillX

SkillX is a standalone repository for SkillX specification work, SkillsBench rewrite experiments, and the C4AR bounded-refinement inner loop.

This repository is intended to be collaboration-ready. The SkillX code, playbooks, protocols, scripts, and focused experiment assets live here. The benchmark substrate itself remains external.

See [INDEX.md](INDEX.md) for the recommended reading order.

## License and Usage

This repository is public for inspection and authorized collaboration, but it
is not open source.

- Commercial use is not permitted.
- Copying, mirroring, redistribution, and casual reuse are not permitted.
- Derivative works and service use are not permitted without prior written
  permission.
- Explicitly authorized collaborators may make the minimum copies and edits
  needed for that collaboration.

See `LICENSE` for the controlling terms.

## Standalone Status

What is already self-contained in this repo:

- the `skillx` Python package under `src/skillx/`
- the full C4AR inner-loop runtime under `src/skillx/c4ar/`
- the rewrite and refine runners under `scripts/`
- the C4AR Role A and Role B playbooks under `experiments/skillx-skillsbench-001/playbooks/`
- experiment protocols, materialized skillpacks, and selected real fixtures under `experiments/skillx-skillsbench-001/`
- `93` passing `unittest` tests for the current extracted scope

What is still external:

- a local SkillsBench workspace
- Docker
- `uv`
- a working `codex` CLI for C4AR Role A and Role B
- a Claude Code OAuth token file for Harbor-based benchmark execution
- model/API access required by the benchmark environment

In other words: the SkillX codebase is standalone, but full benchmark execution still depends on external tooling and the external SkillsBench task substrate.

## External Benchmark Dependency

SkillX currently targets SkillsBench as the benchmark substrate:

- SkillsBench website: <https://www.skillsbench.ai>
- SkillsBench GitHub: <https://github.com/benchflow-ai/skillsbench>
- Harbor docs: <https://harborframework.com/docs>

The runners in this repo expect a local SkillsBench checkout passed through `--skillsbench-root`.

Example local layout:

```text
projects/
  skillX/
  skillsbench-src/
```

## Requirements

Minimum local requirements for collaborators:

- Python `>=3.11` for the SkillX package and scripts
- Docker with at least `16 GB` memory available to the daemon
- `uv` on `PATH`
- `codex` on `PATH` if you want to run the default C4AR Role A / Role B flow
- a local SkillsBench checkout
- a valid Claude Code OAuth token file if you want to run the default Harbor-backed executor flow

## Quick Start

Create an isolated environment and install SkillX in editable mode:

```bash
cd /path/to/skillX
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

Smoke-test the two main CLIs:

```bash
python scripts/run_skillx_rewrite_benchmark.py --help
python scripts/run_skillx_refine_benchmark.py --help
```

## What Is Included For C4AR

The C4AR inner loop is included in this repository:

- orchestrator: `src/skillx/c4ar/orchestrator.py`
- Role A: `src/skillx/c4ar/role_a.py`
- Role B: `src/skillx/c4ar/role_b.py`
- playbook runner: `src/skillx/c4ar/playbook_agent_runner.py`
- artifact contracts: `src/skillx/c4ar/contracts.py`
- validator: `scripts/validate_c4ar_role_b_outputs.py`
- default playbooks:
  - `experiments/skillx-skillsbench-001/playbooks/C4AR_ROLE_A_SESSION_DISTILL_PLAYBOOK.md`
  - `experiments/skillx-skillsbench-001/playbooks/C4AR_ROLE_B_REFINE_BRAIN_PLAYBOOK.md`

So the answer to "is the inner-loop code and config included?" is yes for the SkillX side of the loop.

The remaining runtime dependencies are external because Role C executes benchmark jobs through SkillsBench and Harbor, and the default Role A / Role B execution path invokes `codex exec`.

## Main Entrypoints

Rewrite benchmark:

```bash
python scripts/run_skillx_rewrite_benchmark.py \
  --skillsbench-root /path/to/skillsbench \
  --task offer-letter-generator \
  --run-id rewrite-local-001 \
  --output-dir experiments/skillx-skillsbench-001/runs/rewrite-local-001 \
  --oauth-file /path/to/claude-code-oauth-token
```

C4AR refine benchmark:

```bash
python scripts/run_skillx_refine_benchmark.py \
  --skillsbench-root /path/to/skillsbench \
  --task trend-anomaly-causal-inference \
  --run-id c4ar-local-001 \
  --output-dir experiments/skillx-skillsbench-001/runs/c4ar-local-001 \
  --oauth-file /path/to/claude-code-oauth-token \
  --source-run-dir /path/to/prior-rewrite-run \
  --orchestration-mode c4ar
```

## Notes For Collaborators

- Use `README.md`, `INDEX.md`, and the current Python scripts as the canonical setup source.
- Some historical handoff notes under `experiments/skillx-skillsbench-001/agent_handoff/` still preserve incubator-era paths from the original MARC workspace. Treat those as historical execution notes, not as the canonical repo layout.
