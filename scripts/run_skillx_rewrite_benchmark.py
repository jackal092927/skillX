#!/usr/bin/env python3
"""Orchestrate protocol-controlled SkillX rewrites and Harbor benchmark runs."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from skillx.io_utils import ensure_dir, read_json, write_json
from skillx.skillpack_utils import discover_skill_names

EXPERIMENT_ROOT = ROOT / "experiments" / "skillx-skillsbench-001"
DEFAULT_AGENT = "claude-code"
DEFAULT_MODEL = "anthropic/claude-sonnet-4-5"
DEFAULT_CONDITIONS = ("c0", "c1", "c2", "c3")
MIN_DOCKER_MEMORY_BYTES = 16_000_000_000
DEFAULT_RETRY_EXCLUDE = [
    "AgentTimeoutError",
    "VerifierTimeoutError",
    "RewardFileNotFoundError",
    "RewardFileEmptyError",
    "VerifierOutputParseError",
]


@dataclass(frozen=True)
class TaskInputs:
    task_id: str
    task_dir: Path
    no_skills_task_dir: Path | None
    instruction_path: Path
    task_toml_path: Path
    test_sh_path: Path
    test_outputs_path: Path
    skills_dir: Path
    skill_names: list[str]


@dataclass(frozen=True)
class RewritePaths:
    job_dir: Path
    inputs_dir: Path
    prompts_dir: Path
    logs_dir: Path
    outputs_dir: Path
    registry_dir: Path
    materialized_dir: Path
    manifest_path: Path


@dataclass(frozen=True)
class RewriteTaskSpec:
    mode: str
    skill_name: str | None
    task_dir: Path
    config_path: Path
    jobs_dir: Path
    output_filename: str
    registry_output_path: Path | None
    materialized_output_path: Path | None
    required_substring: str | None


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        input=input_text,
        text=True,
        capture_output=True,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"command failed ({proc.returncode}): {' '.join(cmd)}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def _zsh_command_output(command: str) -> str:
    proc = _run(["zsh", "-ic", command], check=True)
    return proc.stdout.strip()


def normalize_claude_model_name(model_name: str) -> str:
    return model_name.split("/", 1)[1] if "/" in model_name else model_name


def extract_fenced_block(markdown_text: str, heading: str) -> str:
    escaped = re.escape(heading)
    pattern = re.compile(rf"{escaped}.*?```(?:text)?\n(.*?)```", re.DOTALL)
    match = pattern.search(markdown_text)
    if not match:
        raise ValueError(f"unable to find fenced block after heading: {heading}")
    return match.group(1).strip()


def discover_task_inputs(skillsbench_root: Path, task_id: str) -> TaskInputs:
    task_dir = skillsbench_root / "tasks" / task_id
    no_skills_task_dir = skillsbench_root / "tasks-no-skills" / task_id
    instruction_path = task_dir / "instruction.md"
    task_toml_path = task_dir / "task.toml"
    test_sh_path = task_dir / "tests" / "test.sh"
    test_outputs_path = task_dir / "tests" / "test_outputs.py"
    skills_dir = task_dir / "environment" / "skills"
    missing = [
        str(path)
        for path in [instruction_path, task_toml_path, test_sh_path, test_outputs_path, skills_dir]
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError(f"missing task inputs for {task_id}: {missing}")
    skill_names = discover_skill_names(skills_dir)
    return TaskInputs(
        task_id=task_id,
        task_dir=task_dir,
        no_skills_task_dir=no_skills_task_dir if no_skills_task_dir.exists() else None,
        instruction_path=instruction_path,
        task_toml_path=task_toml_path,
        test_sh_path=test_sh_path,
        test_outputs_path=test_outputs_path,
        skills_dir=skills_dir,
        skill_names=skill_names,
    )


def make_rewrite_paths(run_dir: Path, task_id: str) -> RewritePaths:
    job_dir = ensure_dir(run_dir / "rewrite_jobs" / task_id)
    inputs_dir = ensure_dir(job_dir / "inputs")
    prompts_dir = ensure_dir(job_dir / "prompts")
    logs_dir = ensure_dir(job_dir / "logs")
    outputs_dir = ensure_dir(job_dir / "outputs")
    registry_dir = ensure_dir(outputs_dir / "rewrite_registry" / task_id)
    materialized_dir = ensure_dir(outputs_dir / "materialized_skillpacks" / task_id)
    return RewritePaths(
        job_dir=job_dir,
        inputs_dir=inputs_dir,
        prompts_dir=prompts_dir,
        logs_dir=logs_dir,
        outputs_dir=outputs_dir,
        registry_dir=registry_dir,
        materialized_dir=materialized_dir,
        manifest_path=outputs_dir / "rewrite_manifest.json",
    )


def snapshot_rewrite_inputs(task: TaskInputs, paths: RewritePaths) -> None:
    for skill_name in task.skill_names:
        source = task.skills_dir / skill_name / "SKILL.md"
        target = paths.registry_dir / f"original__{skill_name}__SKILL.md"
        target.write_text(source.read_text())
        copied = paths.inputs_dir / f"{skill_name}__original__SKILL.md"
        copied.write_text(source.read_text())
    for src in [task.instruction_path, task.task_toml_path, task.test_sh_path, task.test_outputs_path]:
        shutil.copy2(src, paths.inputs_dir / src.name)
    for src in [
        EXPERIMENT_ROOT / "C2_REWRITE_PROTOCOL.md",
        EXPERIMENT_ROOT / "C3_REWRITE_PROTOCOL.md",
        EXPERIMENT_ROOT / "conditions.md",
    ]:
        shutil.copy2(src, paths.inputs_dir / src.name)


def _safe_name(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def parse_condition_skill_sources(entries: list[str]) -> dict[str, Path]:
    condition_skill_sources: dict[str, Path] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError(f"invalid condition skill source mapping: {entry!r}")
        condition, raw_path = entry.split("=", 1)
        condition = condition.strip().lower()
        raw_path = raw_path.strip()
        if not condition or not raw_path:
            raise ValueError(f"invalid condition skill source mapping: {entry!r}")
        if condition in DEFAULT_CONDITIONS:
            raise ValueError(f"condition skill source overrides are reserved for built-in conditions: {condition}")
        if condition in condition_skill_sources:
            raise ValueError(f"duplicate condition skill source mapping: {condition}")
        condition_skill_sources[condition] = Path(raw_path).expanduser().resolve()
    return condition_skill_sources


def resolve_condition_skill_source(
    *,
    condition: str,
    task: TaskInputs,
    rewrite_paths: RewritePaths,
    condition_skill_sources: dict[str, Path] | None,
) -> Path | None:
    if condition == "c0":
        return None
    if condition == "c1":
        return task.skills_dir
    if condition == "c2":
        return rewrite_paths.materialized_dir / "c2_minimal"
    if condition == "c3":
        return rewrite_paths.materialized_dir / "c3_derived"
    if condition_skill_sources and condition in condition_skill_sources:
        return condition_skill_sources[condition]
    raise ValueError(f"unsupported condition: {condition}")


def render_rewrite_instruction(
    *,
    mode: str,
    task: TaskInputs,
    skill_name: str | None,
    output_filename: str,
) -> str:
    if mode == "c2":
        protocol_name = "C2_REWRITE_PROTOCOL.md"
        output_description = "the full rewritten SKILL.md for this single skill"
    elif mode == "c3":
        protocol_name = "C3_REWRITE_PROTOCOL.md"
        output_description = "the full derived SKILL.md for this single skill"
    else:
        protocol_name = "C3_REWRITE_PROTOCOL.md"
        output_description = "the bundle YAML for this multi-skill task"
    skill_line = f"- target skill: `{skill_name}`" if skill_name else "- target: task-level bundle"
    return "\n".join(
        [
            "You are running inside a protocol-controlled SkillX rewrite task.",
            "",
            "Your job is to read the frozen rewrite inputs from `/root/rewrite_inputs` and write exactly one final artifact.",
            "",
            f"- mode: `{mode}`",
            f"- task id: `{task.task_id}`",
            skill_line,
            f"- protocol file: `/root/rewrite_inputs/protocols/{protocol_name}`",
            f"- task instruction file: `/root/rewrite_inputs/task/instruction.md`",
            f"- task config file: `/root/rewrite_inputs/task/task.toml`",
            f"- task tests: `/root/rewrite_inputs/task/tests/`",
            f"- write the final artifact to `/root/output/{output_filename}`",
            "",
            "Rules:",
            "- Read the protocol file first and follow it exactly.",
            "- Read only the provided rewrite inputs under `/root/rewrite_inputs`.",
            "- Do not solve the benchmark task itself.",
            "- Do not output commentary, explanation, or markdown fences.",
            f"- The final file must be exactly {output_description}.",
        ]
    ) + "\n"


def render_rewrite_test_outputs_py(*, mode: str, output_filename: str, required_substring: str | None) -> str:
    required_expr = repr(required_substring) if required_substring is not None else "None"
    return f"""from __future__ import annotations

import shutil
from pathlib import Path


OUTPUT_PATH = Path("/root/output/{output_filename}")
EXPORT_DIR = Path("/logs/verifier/exported")
REQUIRED_SUBSTRING = {required_expr}


def main() -> int:
    if not OUTPUT_PATH.exists():
        raise SystemExit("missing output artifact")
    text = OUTPUT_PATH.read_text().strip()
    if not text:
        raise SystemExit("output artifact is empty")
    if REQUIRED_SUBSTRING and REQUIRED_SUBSTRING not in text:
        raise SystemExit(f"required substring missing: {{REQUIRED_SUBSTRING}}")
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUTPUT_PATH, EXPORT_DIR / OUTPUT_PATH.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def render_rewrite_test_sh() -> str:
    return """#!/bin/bash
set -euo pipefail
python3 /tests/test_outputs.py
echo 1 > /logs/verifier/reward.txt
"""


def render_rewrite_task_toml() -> str:
    return """version = "1.0"

[metadata]
author_name = "OpenAI Codex"
author_email = "noreply@example.com"
difficulty = "medium"
category = "skillx"
tags = ["skillx", "rewrite", "protocol"]

[verifier]
timeout_sec = 180.0

[agent]
timeout_sec = 900.0

[environment]
build_timeout_sec = 300.0
cpus = 1
memory_mb = 2048
storage_mb = 4096
gpus = 0
allow_internet = true

[verifier.env]

[solution.env]
"""


def render_rewrite_dockerfile() -> str:
    return """FROM python:3.12-slim

WORKDIR /root
RUN mkdir -p /root/output /root/rewrite_inputs
COPY rewrite_inputs /root/rewrite_inputs
"""


def populate_rewrite_inputs_dir(
    *,
    target_dir: Path,
    task: TaskInputs,
    skill_name: str | None,
    mode: str,
    c2_outputs: dict[str, Path] | None,
) -> None:
    task_dir = ensure_dir(target_dir / "task")
    protocols_dir = ensure_dir(target_dir / "protocols")
    original_dir = ensure_dir(target_dir / "original_skills")
    shutil.copy2(task.instruction_path, task_dir / "instruction.md")
    shutil.copy2(task.task_toml_path, task_dir / "task.toml")
    ensure_dir(task_dir / "tests")
    shutil.copy2(task.test_sh_path, task_dir / "tests" / "test.sh")
    shutil.copy2(task.test_outputs_path, task_dir / "tests" / "test_outputs.py")
    shutil.copy2(EXPERIMENT_ROOT / "conditions.md", target_dir / "conditions.md")
    shutil.copy2(EXPERIMENT_ROOT / "C2_REWRITE_PROTOCOL.md", protocols_dir / "C2_REWRITE_PROTOCOL.md")
    shutil.copy2(EXPERIMENT_ROOT / "C3_REWRITE_PROTOCOL.md", protocols_dir / "C3_REWRITE_PROTOCOL.md")
    skill_names = [skill_name] if skill_name else task.skill_names
    for one_skill in skill_names:
        ensure_dir(original_dir / one_skill)
        shutil.copy2(task.skills_dir / one_skill / "SKILL.md", original_dir / one_skill / "SKILL.md")
    if mode in {"c3", "bundle"} and c2_outputs:
        c2_dir = ensure_dir(target_dir / "c2_skills")
        for one_skill in task.skill_names:
            ensure_dir(c2_dir / one_skill)
            shutil.copy2(c2_outputs[one_skill], c2_dir / one_skill / "SKILL.md")


def create_rewrite_task_sandbox(
    *,
    task: TaskInputs,
    paths: RewritePaths,
    mode: str,
    skill_name: str | None,
    c2_outputs: dict[str, Path] | None,
) -> RewriteTaskSpec:
    stem = f"{mode}-{skill_name}" if skill_name else f"{mode}-bundle"
    slug = _safe_name(stem)
    task_dir = paths.job_dir / "rewrite_tasks" / slug
    if task_dir.exists():
        shutil.rmtree(task_dir)
    ensure_dir(task_dir / "environment")
    ensure_dir(task_dir / "tests")
    ensure_dir(task_dir / "solution")
    output_filename = "bundle.yaml" if mode == "bundle" else "SKILL.md"
    required_substring = "# Derived Execution Layer" if mode == "c3" else None
    (task_dir / "instruction.md").write_text(
        render_rewrite_instruction(mode=mode, task=task, skill_name=skill_name, output_filename=output_filename)
    )
    (task_dir / "task.toml").write_text(render_rewrite_task_toml())
    (task_dir / "environment" / "Dockerfile").write_text(render_rewrite_dockerfile())
    populate_rewrite_inputs_dir(
        target_dir=task_dir / "environment" / "rewrite_inputs",
        task=task,
        skill_name=skill_name,
        mode=mode,
        c2_outputs=c2_outputs,
    )
    (task_dir / "tests" / "test.sh").write_text(render_rewrite_test_sh())
    (task_dir / "tests" / "test_outputs.py").write_text(
        render_rewrite_test_outputs_py(
            mode=mode,
            output_filename=output_filename,
            required_substring=required_substring,
        )
    )
    (task_dir / "solution" / "solve.sh").write_text("#!/bin/bash\nexit 0\n")
    jobs_dir = ensure_dir(paths.job_dir / "harbor_jobs")
    config_dir = ensure_dir(paths.job_dir / "rewrite_configs")
    registry_output_path = None
    materialized_output_path = None
    if mode == "c2" and skill_name:
        registry_output_path = paths.registry_dir / f"skillx_minimal__{skill_name}__SKILL.md"
        materialized_output_path = paths.materialized_dir / "c2_minimal" / skill_name / "SKILL.md"
    elif mode == "c3" and skill_name:
        materialized_output_path = paths.materialized_dir / "c3_derived" / skill_name / "SKILL.md"
    elif mode == "bundle":
        registry_output_path = paths.registry_dir / "skillx_derived__bundle__notes.yaml"
    job_name = f"{_safe_name(task.task_id)}-{slug}"
    config_path = config_dir / f"{job_name}.json"
    write_json(
        config_path,
        build_job_config(
            job_name=job_name,
            jobs_dir=jobs_dir,
            task_path=task_dir,
            agent_name=DEFAULT_AGENT,
            model_name=DEFAULT_MODEL,
            timeout_multiplier=1.0,
            n_concurrent_trials=1,
        ),
    )
    return RewriteTaskSpec(
        mode=mode,
        skill_name=skill_name,
        task_dir=task_dir,
        config_path=config_path,
        jobs_dir=jobs_dir,
        output_filename=output_filename,
        registry_output_path=registry_output_path,
        materialized_output_path=materialized_output_path,
        required_substring=required_substring,
    )


def collect_rewrite_job_output(spec: RewriteTaskSpec) -> str:
    job_dir = spec.jobs_dir / spec.config_path.stem
    result_path = job_dir / "result.json"
    if not result_path.exists():
        raise FileNotFoundError(f"rewrite result missing: {result_path}")
    trial_dirs = sorted(
        path
        for path in job_dir.iterdir()
        if path.is_dir() and (path / "result.json").exists()
    )
    if len(trial_dirs) != 1:
        raise RuntimeError(f"expected exactly one rewrite trial under {job_dir}, found {len(trial_dirs)}")
    trial_payload = read_json(trial_dirs[0] / "result.json")
    if trial_payload.get("exception_info"):
        raise RuntimeError(f"rewrite task failed: {trial_payload['exception_info']}")
    exported = trial_dirs[0] / "verifier" / "exported" / spec.output_filename
    if not exported.exists():
        raise FileNotFoundError(f"rewrite exported output missing: {exported}")
    return exported.read_text()


def validate_rewrite_outputs(task: TaskInputs, paths: RewritePaths) -> list[str]:
    errors: list[str] = []
    for skill_name in task.skill_names:
        c2_path = paths.materialized_dir / "c2_minimal" / skill_name / "SKILL.md"
        c3_path = paths.materialized_dir / "c3_derived" / skill_name / "SKILL.md"
        if not c2_path.exists():
            errors.append(f"missing C2 skill: {c2_path}")
        if not c3_path.exists():
            errors.append(f"missing C3 skill: {c3_path}")
        elif "# Derived Execution Layer" not in c3_path.read_text():
            errors.append(f"C3 missing derived layer heading: {c3_path}")
    if len(task.skill_names) > 1:
        bundle_path = paths.registry_dir / "skillx_derived__bundle__notes.yaml"
        if not bundle_path.exists():
            errors.append(f"missing bundle artifact: {bundle_path}")
    if not paths.manifest_path.exists():
        errors.append(f"missing rewrite manifest: {paths.manifest_path}")
    return errors


def write_rewrite_manifest(
    *,
    task: TaskInputs,
    paths: RewritePaths,
    model_name: str,
    c2_prompt_text: str,
    c3_prompt_text: str,
    c2_outputs: dict[str, Path],
    c3_outputs: dict[str, Path],
    bundle_path: Path | None,
) -> None:
    output_files = [str(path) for path in c2_outputs.values()] + [str(path) for path in c3_outputs.values()]
    if bundle_path:
        output_files.append(str(bundle_path))
    payload = {
        "task_id": task.task_id,
        "writer_agent": DEFAULT_AGENT,
        "writer_model": model_name,
        "writer_runtime": "harbor-docker-claude-code-v0.1",
        "c2_protocol_version": "v0.2",
        "c3_protocol_version": "v0.1",
        "prompt_hashes": {
            "c2": _sha256_text(c2_prompt_text),
            "c3": _sha256_text(c3_prompt_text),
        },
        "input_files": sorted(str(path) for path in paths.inputs_dir.iterdir()),
        "output_files": sorted(output_files),
        "timestamp": _timestamp(),
    }
    write_json(paths.manifest_path, payload)


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def materialize_task_sandbox(
    *,
    task: TaskInputs,
    run_dir: Path,
    condition: str,
    rewrite_paths: RewritePaths,
    condition_skill_sources: dict[str, Path] | None = None,
) -> Path:
    sandbox_dir = run_dir / "artifacts" / "task_sandboxes" / f"{condition}-{task.task_id}"
    if condition == "c0":
        base = task.no_skills_task_dir or task.task_dir
    else:
        base = task.task_dir
    copy_tree(base, sandbox_dir)
    skills_target = sandbox_dir / "environment" / "skills"
    source = resolve_condition_skill_source(
        condition=condition,
        task=task,
        rewrite_paths=rewrite_paths,
        condition_skill_sources=condition_skill_sources,
    )
    if source is None:
        if skills_target.exists():
            shutil.rmtree(skills_target)
    elif condition == "c1":
        pass
    else:
        if skills_target.exists():
            shutil.rmtree(skills_target)
        copy_tree(source, skills_target)
    return sandbox_dir


def build_job_config(
    *,
    job_name: str,
    jobs_dir: Path,
    task_path: Path,
    agent_name: str,
    model_name: str,
    timeout_multiplier: float,
    n_concurrent_trials: int,
) -> dict[str, Any]:
    return {
        "job_name": job_name,
        "jobs_dir": str(jobs_dir),
        "n_attempts": 1,
        "timeout_multiplier": timeout_multiplier,
        "debug": False,
        "orchestrator": {
            "type": "local",
            "n_concurrent_trials": n_concurrent_trials,
            "quiet": False,
            "retry": {
                "max_retries": 0,
                "include_exceptions": None,
                "exclude_exceptions": DEFAULT_RETRY_EXCLUDE,
                "wait_multiplier": 1.0,
                "min_wait_sec": 1.0,
                "max_wait_sec": 60.0,
            },
            "kwargs": {},
        },
        "environment": {
            "type": "docker",
            "import_path": None,
            "force_build": False,
            "delete": True,
            "override_cpus": None,
            "override_memory_mb": None,
            "override_storage_mb": None,
            "override_gpus": None,
            "kwargs": {},
        },
        "verifier": {
            "override_timeout_sec": None,
            "max_timeout_sec": None,
            "disable": False,
        },
        "metrics": [],
        "agents": [
            {
                "name": agent_name,
                "import_path": None,
                "model_name": model_name,
                "override_timeout_sec": None,
                "override_setup_timeout_sec": None,
                "max_timeout_sec": None,
                "kwargs": {},
            }
        ],
        "datasets": [],
        "tasks": [
            {
                "path": str(task_path),
                "git_url": None,
                "git_commit_id": None,
                "overwrite": False,
                "download_dir": None,
                "source": None,
            }
        ],
    }


def run_harbor_job(
    *,
    skillsbench_root: Path,
    config_path: Path,
    oauth_file: Path,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CLAUDE_CODE_OAUTH_TOKEN_FILE"] = str(oauth_file)
    token_text = oauth_file.read_text().strip()
    if token_text:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = token_text
    return _run(["uv", "run", "harbor", "run", "-c", str(config_path.resolve())], cwd=skillsbench_root, env=env, check=True)


def parse_job_result(job_dir: Path, condition: str, task_id: str, skill_source: str) -> dict[str, Any]:
    result_path = job_dir / "result.json"
    payload = read_json(result_path)
    evals = payload.get("stats", {}).get("evals", {})
    reward_mean = None
    exception_stats: dict[str, Any] = {}
    eval_name = None
    if evals:
        eval_name, eval_payload = next(iter(evals.items()))
        metrics = eval_payload.get("metrics") or []
        if metrics:
            reward_mean = metrics[0].get("mean")
        exception_stats = eval_payload.get("exception_stats") or {}
    return {
        "task_id": task_id,
        "condition": condition,
        "job_dir": str(job_dir),
        "result_path": str(result_path),
        "reward": reward_mean,
        "eval_name": eval_name,
        "exception_stats": exception_stats,
        "skill_source": skill_source,
    }


def render_matrix(results: list[dict[str, Any]]) -> str:
    lines = [
        "| task_id | condition | reward | exceptions | skill_source |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in results:
        exceptions = ",".join(sorted(row["exception_stats"].keys())) if row["exception_stats"] else ""
        lines.append(
            f"| {row['task_id']} | {row['condition']} | {row['reward']} | {exceptions} | {row['skill_source']} |"
        )
    return "\n".join(lines) + "\n"


def check_environment(skillsbench_root: Path, oauth_file: Path) -> dict[str, Any]:
    if not skillsbench_root.exists():
        raise FileNotFoundError(f"skillsbench root not found: {skillsbench_root}")
    if not oauth_file.exists():
        raise FileNotFoundError(f"oauth file not found: {oauth_file}")
    docker_info = _run(["docker", "info", "--format", "{{json .MemTotal}}"], check=True)
    try:
        docker_mem_bytes = int(json.loads(docker_info.stdout.strip()))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"unable to parse docker memory: {docker_info.stdout}") from exc
    if docker_mem_bytes < MIN_DOCKER_MEMORY_BYTES:
        raise RuntimeError(
            f"Docker memory too low: {docker_mem_bytes} bytes < required {MIN_DOCKER_MEMORY_BYTES} bytes"
        )
    uv_path = shutil.which("uv")
    if uv_path is None:
        raise RuntimeError("uv is not available in PATH")
    return {
        "docker_mem_bytes": docker_mem_bytes,
        "uv_path": uv_path,
        "oauth_file": str(oauth_file),
    }


def write_environment_notes(run_dir: Path, env_payload: dict[str, Any], args: argparse.Namespace) -> None:
    notes = "\n".join(
        [
            f"- timestamp: `{_timestamp()}`",
            f"- skillsbench_root: `{args.skillsbench_root}`",
            f"- oauth_file: `{args.oauth_file}`",
            f"- benchmark_agent: `{args.agent}`",
            f"- benchmark_model: `{args.model}`",
            f"- docker_mem_bytes: `{env_payload['docker_mem_bytes']}`",
            f"- uv_path: `{env_payload['uv_path']}`",
            f"- max_concurrency: `{args.max_concurrency}`",
            f"- timeout_multiplier: `{args.timeout_multiplier}`",
        ]
    )
    (run_dir / "ENVIRONMENT_NOTES.md").write_text(notes + "\n")


def write_run_status(run_dir: Path, status: str, args: argparse.Namespace) -> None:
    body = "\n".join(
        [
            f"- status: `{status}`",
            f"- run_id: `{args.run_id}`",
            f"- tasks: `{', '.join(args.task)}`",
            f"- conditions: `{','.join(args.conditions)}`",
            f"- updated_at: `{_timestamp()}`",
        ]
    )
    (run_dir / "RUN_STATUS.md").write_text(body + "\n")


def run_rewrite_phase(
    *,
    task: TaskInputs,
    run_dir: Path,
    skillsbench_root: Path,
    oauth_file: Path,
    agent_name: str,
    model_name: str,
    reuse_existing: bool,
    max_concurrency: int,
) -> tuple[RewritePaths, dict[str, Path], dict[str, Path], Path | None]:
    c2_protocol = (EXPERIMENT_ROOT / "C2_REWRITE_PROTOCOL.md").read_text()
    c3_protocol = (EXPERIMENT_ROOT / "C3_REWRITE_PROTOCOL.md").read_text()
    c2_prompt_template = extract_fenced_block(c2_protocol, "## 9. Standard Rewrite Prompt")
    c3_prompt_template = extract_fenced_block(c3_protocol, "## 11. Standard Derivation Prompt")
    paths = make_rewrite_paths(run_dir, task.task_id)
    snapshot_rewrite_inputs(task, paths)
    existing_c2 = {name: paths.materialized_dir / "c2_minimal" / name / "SKILL.md" for name in task.skill_names}
    existing_c3 = {name: paths.materialized_dir / "c3_derived" / name / "SKILL.md" for name in task.skill_names}
    have_existing = reuse_existing and all(path.exists() for path in [*existing_c2.values(), *existing_c3.values()])
    if have_existing and paths.manifest_path.exists():
        bundle_path = paths.registry_dir / "skillx_derived__bundle__notes.yaml"
        return paths, existing_c2, existing_c3, bundle_path if bundle_path.exists() else None
    c2_outputs: dict[str, Path] = {}
    c2_specs = [
        create_rewrite_task_sandbox(task=task, paths=paths, mode="c2", skill_name=skill_name, c2_outputs=None)
        for skill_name in task.skill_names
    ]

    def _run_rewrite_spec(spec: RewriteTaskSpec) -> tuple[RewriteTaskSpec, str]:
        payload = read_json(spec.config_path)
        payload["agents"][0]["name"] = agent_name
        payload["agents"][0]["model_name"] = model_name
        write_json(spec.config_path, payload)
        run_harbor_job(skillsbench_root=skillsbench_root, config_path=spec.config_path, oauth_file=oauth_file)
        return spec, collect_rewrite_job_output(spec)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, max_concurrency)) as executor:
        futures = [executor.submit(_run_rewrite_spec, spec) for spec in c2_specs]
        for future in concurrent.futures.as_completed(futures):
            spec, text = future.result()
            assert spec.skill_name is not None
            if spec.registry_output_path is None or spec.materialized_output_path is None:
                raise RuntimeError(f"missing C2 output paths for {spec.skill_name}")
            ensure_dir(spec.materialized_output_path.parent)
            spec.registry_output_path.write_text(text)
            spec.materialized_output_path.write_text(text)
            c2_outputs[spec.skill_name] = spec.materialized_output_path

    c3_outputs: dict[str, Path] = {}
    c3_specs = [
        create_rewrite_task_sandbox(task=task, paths=paths, mode="c3", skill_name=skill_name, c2_outputs=c2_outputs)
        for skill_name in task.skill_names
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, max_concurrency)) as executor:
        futures = [executor.submit(_run_rewrite_spec, spec) for spec in c3_specs]
        for future in concurrent.futures.as_completed(futures):
            spec, text = future.result()
            assert spec.skill_name is not None
            if spec.materialized_output_path is None:
                raise RuntimeError(f"missing C3 output path for {spec.skill_name}")
            ensure_dir(spec.materialized_output_path.parent)
            spec.materialized_output_path.write_text(text)
            c3_outputs[spec.skill_name] = spec.materialized_output_path

    bundle_path = None
    if len(task.skill_names) > 1:
        bundle_spec = create_rewrite_task_sandbox(task=task, paths=paths, mode="bundle", skill_name=None, c2_outputs=c2_outputs)
        spec, text = _run_rewrite_spec(bundle_spec)
        if spec.registry_output_path is None:
            raise RuntimeError(f"missing bundle output path for {task.task_id}")
        spec.registry_output_path.write_text(text)
        bundle_path = spec.registry_output_path
    write_rewrite_manifest(
        task=task,
        paths=paths,
        model_name=model_name,
        c2_prompt_text=c2_prompt_template,
        c3_prompt_text=c3_prompt_template,
        c2_outputs=c2_outputs,
        c3_outputs=c3_outputs,
        bundle_path=bundle_path,
    )
    errors = validate_rewrite_outputs(task, paths)
    if errors:
        raise RuntimeError(f"rewrite validation failed for {task.task_id}: {errors}")
    return paths, c2_outputs, c3_outputs, bundle_path


def run_benchmark_phase(
    *,
    task: TaskInputs,
    run_dir: Path,
    rewrite_paths: RewritePaths,
    skillsbench_root: Path,
    conditions: list[str],
    condition_skill_sources: dict[str, Path] | None,
    agent_name: str,
    model_name: str,
    oauth_file: Path,
    timeout_multiplier: float,
    max_concurrency: int,
) -> list[dict[str, Any]]:
    benchmark_jobs_dir = ensure_dir(run_dir / "benchmark_jobs")
    config_dir = ensure_dir(benchmark_jobs_dir / "_configs")
    jobs: list[tuple[str, Path, str]] = []
    for condition in conditions:
        sandbox_dir = materialize_task_sandbox(
            task=task,
            run_dir=run_dir,
            condition=condition,
            rewrite_paths=rewrite_paths,
            condition_skill_sources=condition_skill_sources,
        )
        job_name = f"{task.task_id}-{condition}"
        config_payload = build_job_config(
            job_name=job_name,
            jobs_dir=benchmark_jobs_dir,
            task_path=sandbox_dir,
            agent_name=agent_name,
            model_name=model_name,
            timeout_multiplier=timeout_multiplier,
            n_concurrent_trials=1,
        )
        config_path = config_dir / f"{job_name}.json"
        write_json(config_path, config_payload)
        skill_source_path = resolve_condition_skill_source(
            condition=condition,
            task=task,
            rewrite_paths=rewrite_paths,
            condition_skill_sources=condition_skill_sources,
        )
        skill_source = "none" if skill_source_path is None else str(skill_source_path)
        jobs.append((condition, config_path, skill_source))

    results: list[dict[str, Any]] = []

    def _run_one(job: tuple[str, Path, str]) -> dict[str, Any]:
        condition, config_path, skill_source = job
        run_harbor_job(skillsbench_root=skillsbench_root, config_path=config_path, oauth_file=oauth_file)
        return parse_job_result(
            benchmark_jobs_dir / config_path.stem,
            condition=condition,
            task_id=task.task_id,
            skill_source=skill_source,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, max_concurrency)) as executor:
        futures = [executor.submit(_run_one, job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    return sorted(results, key=lambda row: (row["task_id"], row["condition"]))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skillsbench-root", type=Path, required=True)
    parser.add_argument("--task", action="append", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--oauth-file", type=Path, required=True)
    parser.add_argument("--agent", default=DEFAULT_AGENT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--conditions", default=",".join(DEFAULT_CONDITIONS))
    parser.add_argument(
        "--condition-skill-source",
        action="append",
        default=[],
        metavar="CONDITION=PATH",
        help="Inject a skillpack directory for a custom benchmark condition label.",
    )
    parser.add_argument("--max-concurrency", type=int, default=1)
    parser.add_argument("--timeout-multiplier", type=float, default=1.0)
    parser.add_argument("--skip-rewrite", action="store_true")
    parser.add_argument("--skip-benchmark", action="store_true")
    parser.add_argument("--reuse-existing-rewrites", action="store_true")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    args.skillsbench_root = args.skillsbench_root.resolve()
    args.output_dir = args.output_dir.resolve()
    args.oauth_file = args.oauth_file.resolve()
    args.conditions = [item.strip().lower() for item in args.conditions.split(",") if item.strip()]
    args.condition_skill_sources = parse_condition_skill_sources(args.condition_skill_source)
    run_dir = ensure_dir(args.output_dir)
    env_payload = check_environment(args.skillsbench_root, args.oauth_file)
    write_environment_notes(run_dir, env_payload, args)
    write_run_status(run_dir, "running", args)

    rewrite_summary: list[dict[str, Any]] = []
    benchmark_summary: list[dict[str, Any]] = []

    for task_id in args.task:
        task = discover_task_inputs(args.skillsbench_root, task_id)
        if args.skip_rewrite:
            rewrite_paths = make_rewrite_paths(run_dir, task.task_id)
            c2_outputs = {name: rewrite_paths.materialized_dir / "c2_minimal" / name / "SKILL.md" for name in task.skill_names}
            c3_outputs = {name: rewrite_paths.materialized_dir / "c3_derived" / name / "SKILL.md" for name in task.skill_names}
            bundle_path = rewrite_paths.registry_dir / "skillx_derived__bundle__notes.yaml"
        else:
            rewrite_paths, c2_outputs, c3_outputs, bundle_path = run_rewrite_phase(
                task=task,
                run_dir=run_dir,
                skillsbench_root=args.skillsbench_root,
                oauth_file=args.oauth_file,
                agent_name=args.agent,
                model_name=args.model,
                reuse_existing=args.reuse_existing_rewrites,
                max_concurrency=args.max_concurrency,
            )
        rewrite_summary.append(
            {
                "task_id": task.task_id,
                "n_original_skills": len(task.skill_names),
                "n_c2_skills": len(c2_outputs),
                "n_c3_skills": len(c3_outputs),
                "bundle_generated": bool(bundle_path and bundle_path.exists()),
                "rewrite_manifest": str(rewrite_paths.manifest_path),
            }
        )
        if not args.skip_benchmark:
            benchmark_summary.extend(
                run_benchmark_phase(
                    task=task,
                    run_dir=run_dir,
                    rewrite_paths=rewrite_paths,
                    skillsbench_root=args.skillsbench_root,
                    conditions=args.conditions,
                    condition_skill_sources=args.condition_skill_sources,
                    agent_name=args.agent,
                    model_name=args.model,
                    oauth_file=args.oauth_file,
                    timeout_multiplier=args.timeout_multiplier,
                    max_concurrency=args.max_concurrency,
                )
            )

    results_dir = ensure_dir(run_dir / "results")
    write_json(results_dir / "rewrite_summary.json", rewrite_summary)
    write_json(results_dir / "benchmark_summary.json", benchmark_summary)
    (results_dir / "matrix.md").write_text(render_matrix(benchmark_summary))
    write_run_status(run_dir, "completed", args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
