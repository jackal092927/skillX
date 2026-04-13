#!/usr/bin/env python3
"""Orchestrate protocol-controlled SkillX C4 refine runs."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from skillx.io_utils import ensure_dir, read_json, write_json
from skillx.docker_health import probe_docker_health
from skillx.model_routing import (
    AUTH_BACKED_CLAUDE_CODE_IMPORT_PATH,
    AUTH_BACKED_CODEX_IMPORT_PATH,
    resolve_benchmark_agent_name,
)
from skillx.run_failure_utils import build_run_failure_payload, write_run_failure
from skillx.skillpack_utils import copy_named_skill_dirs, discover_skill_names
from skillx.c4ar.orchestrator import (
    ExecutorOutputs,
    OrchestratorConfig,
    OrchestratorInputs,
    OrchestratorOutputs,
    run_c4ar_round,
)
from skillx.c4ar.role_a import (
    RoleAConfig,
    RoleAOutputs,
    run_role_a,
)
from skillx.c4ar.role_b import (
    RoleBConfig,
    RoleBOutputs,
    run_role_b,
)
from skillx.c4ar.playbook_agent_runner import (
    PlaybookAgentExecutionError,
    PlaybookAgentOutputContractError,
    PlaybookAgentTimeoutError,
)
from skillx.c4ar.role_b_artifacts import load_and_canonicalize_role_b_artifact_files
from skillx.c4ar.contracts import (
    NextSkillpackManifest,
    RoundDecisionArtifact,
    SessionEvidenceArtifact,
    ensure_valid_session_evidence_artifact,
)
from skillx.decision import (
    SkillXDecisionBundle,
    SkillXRefineIntent,
    SkillXRoundDisposition,
    build_skillx_decision_bundle,
    decide_refine_intent,
    decide_round_disposition,
)
from skillx.evidence import classify_skillx_outcome
from skillx.models import SkillXC3Result, SkillXC4Summary, SkillXRoundResult
from skillx.session_evidence import (
    SessionDerivedEvidence,
    distill_session_logs,
    render_session_evidence_markdown,
)

EXPERIMENT_ROOT = ROOT / "experiments" / "skillx-skillsbench-001"
PLAYBOOK_ROOT = EXPERIMENT_ROOT / "playbooks"
DEFAULT_ROLE_A_PLAYBOOK = PLAYBOOK_ROOT / "C4AR_ROLE_A_SESSION_DISTILL_PLAYBOOK.md"
DEFAULT_ROLE_B_PLAYBOOK = PLAYBOOK_ROOT / "C4AR_ROLE_B_REFINE_BRAIN_PLAYBOOK.md"
DEFAULT_AGENT = "claude-code"
DEFAULT_MODEL = "anthropic/claude-sonnet-4-5"
DEFAULT_ORCHESTRATION_MODE = "legacy"
MIN_DOCKER_MEMORY_BYTES = 16_000_000_000
DEFAULT_REFINED_TASK_MEMORY_MB = 8192
DEFAULT_REFINED_TASK_STORAGE_MB = 20480
DEFAULT_RETRY_EXCLUDE = [
    "AgentTimeoutError",
    "VerifierTimeoutError",
    "RewardFileNotFoundError",
    "RewardFileEmptyError",
    "VerifierOutputParseError",
]
TIMEOUT_EXCEPTION_MARKERS = ("timeout",)
HARBOR_INFRA_FAILURE_EXCEPTION = "HarborJobExecutionError"


@dataclass(frozen=True)
class TaskInputs:
    task_id: str
    task_dir: Path
    instruction_path: Path
    task_toml_path: Path
    test_sh_path: Path
    test_outputs_path: Path
    skills_dir: Path
    skill_names: list[str]


@dataclass(frozen=True)
class RefinePaths:
    root_dir: Path
    static_dir: Path
    rounds_dir: Path
    jobs_dir: Path
    configs_dir: Path
    final_dir: Path
    manifest_path: Path
    ledger_path: Path
    summary_path: Path


@dataclass(frozen=True)
class SourceArtifacts:
    starting_skillpack_dir: Path
    starting_label: str
    starting_bundle_path: Path | None
    rewrite_manifest_path: Path | None


@dataclass(frozen=True)
class ProtocolInputs:
    refine_protocol_path: Path
    bundle_contract_path: Path


@dataclass(frozen=True)
class RefineRoundSpec:
    round_index: int
    task_dir: Path
    config_path: Path
    jobs_dir: Path
    expected_skill_names: list[str]
    has_bundle: bool


SESSION_LOG_SUFFIXES = {".json", ".jsonl", ".ndjson", ".log", ".txt"}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def update_failure_context(
    failure_context: dict[str, Any] | None,
    *,
    failed_stage: str | None = None,
    failed_round: int | None = None,
    manual_intervention: bool | None = None,
) -> None:
    if failure_context is None:
        return
    if failed_stage is not None:
        failure_context["failed_stage"] = failed_stage
    if failed_round is not None:
        failure_context["failed_round"] = failed_round
    if manual_intervention is not None:
        failure_context["manual_intervention"] = bool(manual_intervention)


def build_main_run_failure_payload(
    *,
    error: Exception,
    args: argparse.Namespace,
    failure_context: dict[str, Any],
) -> dict[str, Any]:
    return build_run_failure_payload(
        error=error,
        traceback_text=traceback.format_exc(),
        failed_stage=str(failure_context.get("failed_stage")) if failure_context.get("failed_stage") else None,
        failed_round=failure_context.get("failed_round"),
        manual_intervention=bool(failure_context.get("manual_intervention", False)),
        extra={
            "run_id": args.run_id,
            "task_id": args.task,
            "orchestration_mode": args.orchestration_mode,
        },
    )


def normalize_skill_files_within_skillpack(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    skillpack_dir_value = normalized.get("skillpack_dir")
    skill_files_value = normalized.get("skill_files")
    if not isinstance(skillpack_dir_value, str) or not isinstance(skill_files_value, list):
        return normalized

    skillpack_dir = Path(skillpack_dir_value)
    normalized_skill_files: list[Any] = []
    for item in skill_files_value:
        if not isinstance(item, str):
            normalized_skill_files.append(item)
            continue
        path = Path(item)
        if not path.is_absolute():
            normalized_skill_files.append(item)
            continue
        try:
            normalized_skill_files.append(str(path.relative_to(skillpack_dir)))
        except ValueError:
            normalized_skill_files.append(item)
    normalized["skill_files"] = normalized_skill_files
    return normalized


def _run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        text=True,
        capture_output=True,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"command failed ({proc.returncode}): {' '.join(cmd)}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def discover_task_inputs(skillsbench_root: Path, task_id: str) -> TaskInputs:
    task_dir = skillsbench_root / "tasks" / task_id
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
        instruction_path=instruction_path,
        task_toml_path=task_toml_path,
        test_sh_path=test_sh_path,
        test_outputs_path=test_outputs_path,
        skills_dir=skills_dir,
        skill_names=skill_names,
    )


def tune_result_has_timeout_exception(tune_result: dict[str, Any]) -> bool:
    exception_stats = tune_result.get("exception_stats") or {}
    if not isinstance(exception_stats, dict):
        return False
    for key in exception_stats:
        normalized = str(key).strip().lower()
        if any(marker in normalized for marker in TIMEOUT_EXCEPTION_MARKERS):
            return True
    return False


def tune_result_has_executor_unavailable(tune_result: dict[str, Any]) -> bool:
    return bool(tune_result.get("executor_unavailable"))


def build_tune_infra_failure_result(
    *,
    task_id: str,
    round_dir_path: Path,
    error: Exception,
    stage: str,
    attempt_timeout_multiplier: float,
) -> dict[str, Any]:
    message = f"{type(error).__name__}: {error}"
    return {
        "task_id": task_id,
        "condition": "c4",
        "reward": None,
        "eval_name": None,
        "exception_stats": {HARBOR_INFRA_FAILURE_EXCEPTION: [f"{stage}: {message}"]},
        "n_trials": 0,
        "n_errors": 1,
        "skill_source": str(round_dir_path / "skillpack"),
        "executor_unavailable": True,
        "failure_stage": stage,
        "failure_message": message,
        "attempt_timeout_multiplier": attempt_timeout_multiplier,
    }


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def claude_log_has_terminal_success(log_path: Path) -> bool:
    if not log_path.exists():
        return False
    with log_path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if '"type":"result"' not in line or '"subtype":"success"' not in line:
                continue
            if '"is_error":false' in line or '"is_error": false' in line:
                return True
    return False


def trial_is_false_claude_timeout(trial_dir: Path) -> bool:
    result_path = trial_dir / "result.json"
    if not result_path.exists():
        return False
    payload = read_json(result_path)
    exception_info = payload.get("exception_info")
    if not isinstance(exception_info, dict):
        return False
    if exception_info.get("exception_type") != "AgentTimeoutError":
        return False
    return claude_log_has_terminal_success(trial_dir / "agent" / "claude-code.txt")


def normalize_harbor_exception_stats(job_dir: Path, exception_stats: Any) -> dict[str, Any]:
    if not isinstance(exception_stats, dict):
        return {"__unparsed__": exception_stats}
    if "AgentTimeoutError" not in exception_stats:
        return exception_stats
    trial_dirs = sorted(path for path in job_dir.iterdir() if path.is_dir() and (path / "result.json").exists())
    if len(trial_dirs) != 1:
        return exception_stats
    if not trial_is_false_claude_timeout(trial_dirs[0]):
        return exception_stats
    normalized = dict(exception_stats)
    normalized.pop("AgentTimeoutError", None)
    return normalized


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
    exception_stats = normalize_harbor_exception_stats(job_dir, exception_stats)
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


def build_job_config(
    *,
    job_name: str,
    jobs_dir: Path,
    task_path: Path,
    agent_name: str | None,
    model_name: str,
    timeout_multiplier: float,
    n_concurrent_trials: int,
    override_memory_mb: int | None = None,
    override_storage_mb: int | None = None,
) -> dict[str, Any]:
    resolved_agent_name = resolve_benchmark_agent_name(agent_name, model_name)
    agent_payload: dict[str, Any] = {
        "name": resolved_agent_name,
        "import_path": None,
        "model_name": model_name,
        "override_timeout_sec": None,
        "override_setup_timeout_sec": None,
        "max_timeout_sec": None,
        "kwargs": {},
    }
    if resolved_agent_name == "claude-code":
        agent_payload["name"] = None
        agent_payload["import_path"] = AUTH_BACKED_CLAUDE_CODE_IMPORT_PATH
    elif resolved_agent_name == "codex":
        agent_payload["name"] = None
        agent_payload["import_path"] = AUTH_BACKED_CODEX_IMPORT_PATH
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
            "override_memory_mb": override_memory_mb,
            "override_storage_mb": override_storage_mb,
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
            agent_payload
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
    oauth_file: Path | None,
    agent_name: str,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "").strip()
    env["PYTHONPATH"] = str(SRC) if not existing_pythonpath else f"{SRC}:{existing_pythonpath}"
    if agent_name == "claude-code":
        if oauth_file is None:
            raise ValueError("oauth_file is required for claude-code runs")
        env["CLAUDE_CODE_OAUTH_TOKEN_FILE"] = str(oauth_file)
        token_text = oauth_file.read_text().strip()
        if token_text:
            env["CLAUDE_CODE_OAUTH_TOKEN"] = token_text
    elif agent_name == "codex":
        pass
    else:
        raise ValueError(f"unsupported benchmark agent: {agent_name}")
    return _run(["uv", "run", "harbor", "run", "-c", str(config_path.resolve())], cwd=skillsbench_root, env=env)


def check_environment(skillsbench_root: Path, oauth_file: Path | None, *, agent_name: str) -> dict[str, Any]:
    if not skillsbench_root.exists():
        raise FileNotFoundError(f"skillsbench root not found: {skillsbench_root}")
    if agent_name == "claude-code":
        if oauth_file is None:
            raise ValueError("oauth_file is required for claude-code runs")
        if not oauth_file.exists():
            raise FileNotFoundError(f"oauth file not found: {oauth_file}")
        codex_auth_file = None
    elif agent_name == "codex":
        codex_auth_file = Path.home() / ".codex" / "auth.json"
        if not codex_auth_file.exists():
            raise FileNotFoundError(f"codex auth file not found: {codex_auth_file}")
    else:
        raise ValueError(f"unsupported benchmark agent: {agent_name}")
    docker_health = probe_docker_health(min_memory_bytes=MIN_DOCKER_MEMORY_BYTES)
    if not docker_health["healthy"]:
        raise RuntimeError(f"Docker health check failed: {docker_health['message']}")
    docker_mem_bytes = int(docker_health["docker_mem_bytes"])
    uv_path = shutil.which("uv")
    if uv_path is None:
        raise RuntimeError("uv is not available in PATH")
    return {
        "docker_mem_bytes": docker_mem_bytes,
        "docker_health_category": docker_health["category"],
        "uv_path": uv_path,
        "oauth_file": None if oauth_file is None else str(oauth_file),
        "benchmark_agent": agent_name,
        "codex_auth_file": None if codex_auth_file is None else str(codex_auth_file),
    }


def ensure_refine_paths(run_dir: Path, task_id: str) -> RefinePaths:
    root_dir = ensure_dir(run_dir / "refine" / task_id)
    static_dir = ensure_dir(root_dir / "static")
    rounds_dir = ensure_dir(root_dir / "rounds")
    jobs_dir = ensure_dir(root_dir / "harbor_jobs")
    configs_dir = ensure_dir(root_dir / "configs")
    final_dir = ensure_dir(root_dir / "C4-final")
    return RefinePaths(
        root_dir=root_dir,
        static_dir=static_dir,
        rounds_dir=rounds_dir,
        jobs_dir=jobs_dir,
        configs_dir=configs_dir,
        final_dir=final_dir,
        manifest_path=root_dir / "bundle_manifest.json",
        ledger_path=root_dir / "refine_ledger.md",
        summary_path=root_dir / "refine_summary.json",
    )


def locate_source_artifacts(
    task_id: str,
    source_run_dir: Path,
    *,
    starting_skillpack_dir: Path | None = None,
    starting_bundle_path: Path | None = None,
    starting_label: str | None = None,
) -> SourceArtifacts:
    task_root = source_run_dir / "rewrite_jobs" / task_id / "outputs"
    default_starting_skillpack_dir = task_root / "materialized_skillpacks" / task_id / "c3_derived"
    default_starting_bundle_path = task_root / "rewrite_registry" / task_id / "skillx_derived__bundle__notes.yaml"
    manifest_path = task_root / "rewrite_manifest.json"
    resolved_starting_skillpack_dir = starting_skillpack_dir or default_starting_skillpack_dir
    if starting_label is None:
        starting_label = "C3" if resolved_starting_skillpack_dir == default_starting_skillpack_dir else "R0"
    if not resolved_starting_skillpack_dir.exists():
        raise FileNotFoundError(f"starting skillpack directory not found: {resolved_starting_skillpack_dir}")
    resolved_starting_bundle_path = starting_bundle_path
    if resolved_starting_bundle_path is None and resolved_starting_skillpack_dir == default_starting_skillpack_dir:
        resolved_starting_bundle_path = default_starting_bundle_path
    return SourceArtifacts(
        starting_skillpack_dir=resolved_starting_skillpack_dir,
        starting_label=starting_label,
        starting_bundle_path=resolved_starting_bundle_path if resolved_starting_bundle_path and resolved_starting_bundle_path.exists() else None,
        rewrite_manifest_path=manifest_path if manifest_path.exists() else None,
    )


def parse_condition_from_job_name(task_id: str, job_name: str) -> str | None:
    prefix = f"{task_id}-"
    if not job_name.startswith(prefix):
        return None
    return job_name[len(prefix) :]


def collect_tune_evidence(task_id: str, tune_run_dirs: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run_dir in tune_run_dirs:
        summary_path = run_dir / "results" / "benchmark_summary.json"
        if summary_path.exists():
            for row in read_json(summary_path):
                if row.get("task_id") == task_id:
                    copied = dict(row)
                    copied["source_run_dir"] = str(run_dir)
                    rows.append(copied)
            continue
        benchmark_jobs_dir = run_dir / "benchmark_jobs"
        if not benchmark_jobs_dir.exists():
            continue
        for job_dir in sorted(path for path in benchmark_jobs_dir.iterdir() if path.is_dir()):
            result_path = job_dir / "result.json"
            if not result_path.exists():
                continue
            condition = parse_condition_from_job_name(task_id, job_dir.name)
            if condition is None:
                continue
            row = parse_job_result(job_dir, condition=condition, task_id=task_id, skill_source=str(job_dir))
            row["source_run_dir"] = str(run_dir)
            rows.append(row)
    return sorted(rows, key=lambda item: (str(item.get("source_run_dir")), item["condition"]))


def best_condition_row(rows: list[dict[str, Any]], condition: str) -> dict[str, Any] | None:
    filtered = [row for row in rows if row.get("condition") == condition and row.get("reward") is not None]
    if not filtered:
        return None
    return max(filtered, key=lambda row: (float(row["reward"]), -len(str(row.get("source_run_dir", "")))))


def normalized_condition_label(label: str) -> str:
    return label.strip().lower()


def best_starting_row(rows: list[dict[str, Any]], starting_label: str) -> dict[str, Any] | None:
    condition = normalized_condition_label(starting_label)
    matching = [row for row in rows if normalized_condition_label(str(row.get("condition") or "")) == condition]
    if not matching:
        return None
    rewarded = [row for row in matching if row.get("reward") is not None]
    if rewarded:
        return max(rewarded, key=lambda row: (float(row["reward"]), -len(str(row.get("source_run_dir", "")))))
    return matching[-1]


def build_contrastive_summary(rows: list[dict[str, Any]]) -> str:
    with_rewards = [row for row in rows if row.get("reward") is not None]
    if not with_rewards:
        return "- no tune evidence with rewards available\n"
    strongest = max(with_rewards, key=lambda row: float(row["reward"]))
    weakest = min(with_rewards, key=lambda row: float(row["reward"]))
    lines = [
        "## Strongest observed case",
        f"- condition: `{strongest['condition']}`",
        f"- reward: `{strongest['reward']}`",
        f"- source_run_dir: `{strongest['source_run_dir']}`",
        "",
        "## Weakest observed case",
        f"- condition: `{weakest['condition']}`",
        f"- reward: `{weakest['reward']}`",
        f"- source_run_dir: `{weakest['source_run_dir']}`",
    ]
    return "\n".join(lines) + "\n"


def build_negative_transfer_note(rows: list[dict[str, Any]]) -> str:
    c0 = best_condition_row(rows, "c0")
    c1 = best_condition_row(rows, "c1")
    c2 = best_condition_row(rows, "c2")
    c3 = best_condition_row(rows, "c3")
    lines = ["# Negative Transfer Note", ""]
    if c0 and c1 and c1["reward"] is not None and c0["reward"] is not None:
        delta = float(c1["reward"]) - float(c0["reward"])
        lines.extend(
            [
                f"- `C1 - C0 = {delta:.4f}`",
                f"- baseline_c0: `{c0['reward']}`",
                f"- original_skill_c1: `{c1['reward']}`",
            ]
        )
    if c2 and c3 and c3["reward"] is not None and c2["reward"] is not None:
        delta = float(c3["reward"]) - float(c2["reward"])
        lines.extend(
            [
                f"- `C3 - C2 = {delta:.4f}`",
                f"- skillx_minimal_c2: `{c2['reward']}`",
                f"- skillx_derived_c3: `{c3['reward']}`",
            ]
        )
    if len(lines) == 2:
        lines.append("- insufficient prior evidence to compute deltas")
    return "\n".join(lines) + "\n"


def expand_session_log_paths(session_log_paths: list[Path]) -> list[Path]:
    expanded: list[Path] = []
    seen: set[Path] = set()
    for raw_path in session_log_paths:
        path = raw_path.resolve()
        candidates: list[Path]
        if path.is_file():
            candidates = [path]
        elif path.is_dir():
            candidates = sorted(
                candidate
                for candidate in path.rglob("*")
                if candidate.is_file()
                and (
                    candidate.suffix.lower() in SESSION_LOG_SUFFIXES
                    or "session" in candidate.name.lower()
                    or "log" in candidate.name.lower()
                )
            )
        else:
            candidates = []
        for candidate in candidates:
            if candidate in seen:
                continue
            seen.add(candidate)
            expanded.append(candidate)
    return expanded


def compact_tune_row(row: dict[str, Any]) -> dict[str, Any]:
    compact: dict[str, Any] = {}
    for key in (
        "round_index",
        "condition",
        "reward",
        "result_path",
        "round_dir",
        "eval_name",
        "exception_stats",
        "n_trials",
        "n_errors",
        "source_run_dir",
        "skill_source",
    ):
        value = row.get(key)
        if value is not None:
            compact[key] = value
    classification = row.get("classification")
    if isinstance(classification, dict):
        compact["classification"] = classification
    elif classification is not None and hasattr(classification, "to_dict"):
        compact["classification"] = classification.to_dict()
    return compact


def build_round_row(round_index: int, round_dir_path: Path, tune_result: dict[str, Any]) -> dict[str, Any]:
    reward = tune_result.get("reward")
    exception_stats = tune_result.get("exception_stats") or {}
    if not isinstance(exception_stats, dict):
        exception_stats = {"__unparsed__": exception_stats}
    return {
        "round_index": round_index,
        "reward": reward,
        "result_path": str(round_dir_path / "tune_check" / "result.json"),
        "round_dir": str(round_dir_path),
        "eval_name": tune_result.get("eval_name"),
        "exception_stats": exception_stats,
        "n_trials": tune_result.get("n_trials"),
        "n_errors": tune_result.get("n_errors"),
        "classification": classify_skillx_outcome(
            reward=reward,
            exception_stats=exception_stats,
            reward_missing=reward is None,
        ).to_dict(),
    }


def build_c3_result_from_row(task_id: str, row: dict[str, Any]) -> SkillXC3Result:
    reward = row.get("reward")
    exception_stats = row.get("exception_stats") or {}
    if not isinstance(exception_stats, dict):
        exception_stats = {"__unparsed__": exception_stats}
    reward_missing = reward is None
    classification = classify_skillx_outcome(
        reward=reward if reward is None else float(reward),
        exception_stats=exception_stats,
        reward_missing=reward_missing,
    )
    return SkillXC3Result(
        task_id=task_id,
        condition=str(row.get("condition") or "c3"),
        reward=None if reward is None else float(reward),
        result_path=str(row.get("result_path") or ""),
        source_run_dir=str(row.get("source_run_dir") or row.get("skill_source") or ""),
        eval_name=row.get("eval_name"),
        exception_stats=exception_stats,
        n_trials=row.get("n_trials") if isinstance(row.get("n_trials"), int) else None,
        n_errors=row.get("n_errors") if isinstance(row.get("n_errors"), int) else None,
        classification=classification,
        raw=compact_tune_row(row),
    )


def build_round_results(round_rows: list[dict[str, Any]]) -> list[SkillXRoundResult]:
    results: list[SkillXRoundResult] = []
    for row in round_rows:
        reward = row.get("reward")
        exception_stats = row.get("exception_stats") or {}
        if not isinstance(exception_stats, dict):
            exception_stats = {"__unparsed__": exception_stats}
        classification = classify_skillx_outcome(
            reward=None if reward is None else float(reward),
            exception_stats=exception_stats,
            reward_missing=reward is None,
        )
        results.append(
            SkillXRoundResult(
                round_index=int(row["round_index"]),
                reward=None if reward is None else float(reward),
                result_path=str(row.get("result_path") or ""),
                round_dir=str(row.get("round_dir") or ""),
                eval_name=row.get("eval_name"),
                exception_stats=exception_stats,
                n_trials=row.get("n_trials") if isinstance(row.get("n_trials"), int) else None,
                n_errors=row.get("n_errors") if isinstance(row.get("n_errors"), int) else None,
                classification=classification,
                raw=compact_tune_row(row),
            )
        )
    return results


def build_round_c4_summary(
    *,
    task_id: str,
    source_run_dir: Path,
    round_rows: list[dict[str, Any]],
) -> SkillXC4Summary:
    round_results = build_round_results(round_rows)
    selected = select_final_candidate(round_rows)
    selected_reward = selected.get("reward")
    return SkillXC4Summary(
        task_id=task_id,
        source_run_dir=str(source_run_dir),
        selected_round_index=int(selected["round_index"]),
        selected_reward=None if selected_reward is None else float(selected_reward),
        selected_result_path=str(selected.get("result_path") or None) if selected.get("result_path") else None,
        selected_round_dir=str(selected.get("round_dir") or None) if selected.get("round_dir") else None,
        rounds=round_results,
        raw={"round_rows": [compact_tune_row(row) for row in round_rows]},
    )


def render_round_evidence_bundle_markdown(
    *,
    task_id: str,
    round_index: int,
    evidence_bundle: dict[str, Any],
) -> str:
    c4_summary = evidence_bundle.get("c4_summary") or {}
    selected_round_index = c4_summary.get("selected_round_index")
    selected_reward = c4_summary.get("selected_reward")
    starting_result = evidence_bundle.get("starting_result") or {}
    lines = [
        "# Round Evidence Bundle",
        "",
        f"- task_id: `{task_id}`",
        f"- round_index: `R{round_index}`",
        f"- source_run_dir: `{evidence_bundle.get('source_run_dir')}`",
        f"- starting_label: `{evidence_bundle.get('starting_label')}`",
        f"- starting_reward: `{starting_result.get('reward')}`",
        f"- selected_round_index: `{selected_round_index}`",
        f"- selected_reward: `{selected_reward}`",
        f"- tune_rows: `{len(evidence_bundle.get('tune_evidence') or [])}`",
        f"- session_evidence_attached: `{evidence_bundle.get('session_evidence') is not None}`",
        "",
        "## Bounded Signals",
    ]
    for row in evidence_bundle.get("tune_evidence") or []:
        exception_keys = sorted((row.get("exception_stats") or {}).keys())
        lines.append(
            f"- {row.get('condition', 'unknown')}: reward={row.get('reward')}, exception_keys={exception_keys}"
        )
    session_evidence = evidence_bundle.get("session_evidence") or {}
    if session_evidence:
        lines.extend(
            [
                "",
                f"- session_dominant_failure_pattern: `{session_evidence.get('dominant_failure_pattern')}`",
                f"- session_recommended_edit_targets: `{', '.join(session_evidence.get('recommended_edit_targets') or []) or 'none'}`",
            ]
        )
    return "\n".join(lines) + "\n"


def render_round_decision_markdown(
    *,
    task_id: str,
    round_index: int,
    decision_context: dict[str, Any],
) -> str:
    disposition = decision_context["disposition"]
    intent = decision_context["refine_intent"]
    evidence_bundle = decision_context["evidence_bundle"]
    session_evidence = evidence_bundle.get("session_evidence") or {}
    lines = [
        "# Round Decision",
        "",
        f"- task_id: `{task_id}`",
        f"- round_index: `R{round_index}`",
        f"- retry_allowed: `{disposition['retry_allowed']}`",
        f"- keep_candidate: `{disposition['keep_candidate']}`",
        f"- reason: `{disposition['reason']}`",
        f"- primary_action: `{intent['primary_action']}`",
        f"- edit_targets: `{', '.join(intent.get('edit_targets') or []) or 'none'}`",
        f"- preserve_core_structure: `{intent['preserve_core_structure']}`",
        f"- compress_derived_layer: `{intent['compress_derived_layer']}`",
        f"- de_bloat_derived_layer: `{intent['de_bloat_derived_layer']}`",
        f"- anti_speculation: `{intent['anti_speculation']}`",
        f"- session_evidence_attached: `{bool(session_evidence)}`",
        "",
        "## Bounded Context",
        f"- evidence_bundle_path: `round_{round_index}_evidence_bundle.json`",
        f"- decision_artifact_path: `round_{round_index}_decision.json`",
    ]
    return "\n".join(lines) + "\n"


def write_session_evidence_artifacts(paths: RefinePaths, session_evidence: SessionDerivedEvidence) -> None:
    session_dir = ensure_dir(paths.static_dir / "session_evidence")
    write_json(session_dir / "session_evidence.json", session_evidence.to_dict())
    (session_dir / "session_evidence.md").write_text(render_session_evidence_markdown(session_evidence))


def write_round_context_artifacts(
    *,
    task: TaskInputs,
    round_index: int,
    source_run_dir: Path,
    round_rows: list[dict[str, Any]],
    tune_rows: list[dict[str, Any]],
    paths: RefinePaths,
    starting_label: str = "C3",
    session_evidence: SessionDerivedEvidence | None = None,
) -> dict[str, Any]:
    round_dir_path = round_dir(paths, round_index)
    starting_condition = normalized_condition_label(starting_label)
    starting_row = best_starting_row(tune_rows, starting_label)
    if starting_row is None:
        starting_row = {
            "condition": starting_condition,
            "reward": None,
            "result_path": "",
            "source_run_dir": str(source_run_dir),
            "exception_stats": {},
            "note": f"no prior {starting_condition} tune evidence available",
        }
    c3_result = build_c3_result_from_row(task.task_id, starting_row)
    c4_summary = build_round_c4_summary(task_id=task.task_id, source_run_dir=source_run_dir, round_rows=round_rows)
    decision_bundle = build_skillx_decision_bundle(
        c3_result=c3_result,
        c4_summary=c4_summary,
        session_evidence=session_evidence,
        source_notes=[
            f"round_index=R{round_index}",
            f"selected_round=R{c4_summary.selected_round_index}",
            f"session_evidence_attached={session_evidence is not None}",
        ],
    )
    disposition = decide_round_disposition(decision_bundle)
    intent = decide_refine_intent(decision_bundle)
    evidence_bundle = {
        "task_id": task.task_id,
        "round_index": round_index,
        "source_run_dir": str(source_run_dir),
        "starting_label": starting_label,
        "starting_condition": starting_condition,
        "starting_result": {
            key: value
            for key, value in c3_result.to_dict().items()
            if key != "raw"
        },
        "c4_summary": c4_summary.to_dict(),
        "tune_evidence": [compact_tune_row(row) for row in tune_rows],
        "session_evidence": None if session_evidence is None else session_evidence.to_dict(),
        "bounded": {
            "raw_session_logs_attached": False,
            "session_evidence_attached": session_evidence is not None,
            "tune_evidence_rows": len(tune_rows),
            "round_rows": len(round_rows),
        },
    }
    decision_context = {
        "task_id": task.task_id,
        "round_index": round_index,
        "evidence_bundle": evidence_bundle,
        "disposition": disposition.to_dict(),
        "refine_intent": intent.to_dict(),
        "source_notes": decision_bundle.source_notes,
    }
    decision_dir = ensure_dir(round_dir_path / "decision_context")
    write_json(decision_dir / f"round_{round_index}_evidence_bundle.json", evidence_bundle)
    (decision_dir / f"round_{round_index}_evidence_bundle.md").write_text(
        render_round_evidence_bundle_markdown(task_id=task.task_id, round_index=round_index, evidence_bundle=evidence_bundle)
    )
    write_json(decision_dir / f"round_{round_index}_decision.json", decision_context)
    (decision_dir / f"round_{round_index}_decision.md").write_text(
        render_round_decision_markdown(task_id=task.task_id, round_index=round_index, decision_context=decision_context)
    )
    return decision_context


def write_static_bundle(
    *,
    task: TaskInputs,
    paths: RefinePaths,
    protocols: ProtocolInputs,
    source: SourceArtifacts,
    tune_rows: list[dict[str, Any]],
    tune_run_dirs: list[Path],
    round_budget: int,
    source_run_dir: Path,
    session_evidence: SessionDerivedEvidence | None = None,
) -> None:
    protocols_dir = ensure_dir(paths.static_dir / "protocols")
    ancestry_dir = ensure_dir(paths.static_dir / "ancestry")
    task_context_dir = ensure_dir(paths.static_dir / "task_context")
    tune_dir = ensure_dir(paths.static_dir / "tune_evidence")
    constraints_dir = ensure_dir(paths.static_dir / "constraints")

    for src in [
        protocols.refine_protocol_path,
        protocols.bundle_contract_path,
        EXPERIMENT_ROOT / "conditions.md",
    ]:
        shutil.copy2(src, protocols_dir / src.name)

    original_skills_dir = ensure_dir(ancestry_dir / "original_c1_skills")
    current_starting_skillpack_dir = ensure_dir(ancestry_dir / "current_starting_skillpack")
    for skill_name in task.skill_names:
        ensure_dir(original_skills_dir / skill_name)
        shutil.copy2(task.skills_dir / skill_name / "SKILL.md", original_skills_dir / skill_name / "SKILL.md")
    copy_named_skill_dirs(
        source_skills_dir=source.starting_skillpack_dir,
        dest_skills_dir=current_starting_skillpack_dir,
        skill_names=task.skill_names,
        context_label="starting skillpack",
    )
    if source.starting_bundle_path:
        shutil.copy2(source.starting_bundle_path, ancestry_dir / source.starting_bundle_path.name)
    if source.rewrite_manifest_path:
        shutil.copy2(source.rewrite_manifest_path, ancestry_dir / source.rewrite_manifest_path.name)

    shutil.copy2(task.instruction_path, task_context_dir / "instruction.md")
    shutil.copy2(task.task_toml_path, task_context_dir / "task.toml")
    ensure_dir(task_context_dir / "tests")
    shutil.copy2(task.test_sh_path, task_context_dir / "tests" / "test.sh")
    shutil.copy2(task.test_outputs_path, task_context_dir / "tests" / "test_outputs.py")

    write_json(tune_dir / "condition_summary.json", tune_rows)
    (tune_dir / "contrastive_summary.md").write_text(build_contrastive_summary(tune_rows))
    (tune_dir / "negative_transfer_note.md").write_text(build_negative_transfer_note(tune_rows))
    if session_evidence is not None:
        write_session_evidence_artifacts(paths, session_evidence)

    constraints_text = "\n".join(
        [
            "# Refine Constraints",
            "",
            f"- source_run_dir: `{source_run_dir}`",
            f"- tune_run_dirs: `{', '.join(str(path) for path in tune_run_dirs)}`",
            f"- round_budget: `{round_budget}`",
            f"- starting_artifact: `{source.starting_label}`",
            f"- starting_skillpack_dir: `{source.starting_skillpack_dir}`",
            f"- starting_bundle_path: `{source.starting_bundle_path}`" if source.starting_bundle_path else "- starting_bundle_path: `none`",
            "- heldout_eval_visible: `false`",
            "- external_search_during_loop: `false`",
            "- final_heldout_execution: `placeholder only in this implementation`",
        ]
    )
    (constraints_dir / "refine_constraints.md").write_text(constraints_text + "\n")


def round_dir(paths: RefinePaths, round_index: int) -> Path:
    return ensure_dir(paths.rounds_dir / f"round-{round_index}")


def round_path(paths: RefinePaths, round_index: int) -> Path:
    return paths.rounds_dir / f"round-{round_index}"


def make_round_skill_summary(task: TaskInputs, round_index: int, skillpack_dir: Path, source_label: str) -> str:
    lines = [
        f"# Round {round_index} Skill Artifact",
        "",
        f"- task_id: `{task.task_id}`",
        f"- source: `{source_label}`",
        f"- n_skills: `{len(task.skill_names)}`",
        "",
        "## Skill paths",
    ]
    for skill_name in task.skill_names:
        lines.append(f"- `{skill_name}` -> `{skillpack_dir / skill_name / 'SKILL.md'}`")
    return "\n".join(lines) + "\n"


def make_round_zero_artifacts(
    *,
    task: TaskInputs,
    paths: RefinePaths,
    source: SourceArtifacts,
    tune_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    r0_dir = round_dir(paths, 0)
    skillpack_root = ensure_dir(r0_dir / "skillpack")
    skills_target = ensure_dir(skillpack_root / "skills")
    copy_named_skill_dirs(
        source_skills_dir=source.starting_skillpack_dir,
        dest_skills_dir=skills_target,
        skill_names=task.skill_names,
        context_label="starting skillpack",
    )
    if source.starting_bundle_path:
        shutil.copy2(source.starting_bundle_path, r0_dir / "skillpack_bundle.yaml")
    starting_condition = normalized_condition_label(source.starting_label)
    (r0_dir / "round_0_skill.md").write_text(
        make_round_skill_summary(task, 0, skills_target, f"existing-{source.starting_label}")
    )
    (r0_dir / "round_0_refine_memo.md").write_text(
        f"# Round 0 Refine Memo\n\n- baseline candidate copied from existing `{source.starting_label}`\n- no new edits applied\n"
    )
    (r0_dir / "round_0_diff_summary.md").write_text(
        f"# Round 0 Diff Summary\n\n- baseline round; no diff from source `{source.starting_label}`\n"
    )
    starting_row = best_starting_row(tune_rows, source.starting_label)
    effect_lines = ["# Round 0 Effect Estimate", ""]
    if starting_row and starting_row.get("reward") is not None:
        effect_lines.extend(
            [
                f"- prior_{source.starting_label}_reward: `{starting_row['reward']}`",
                f"- source_run_dir: `{starting_row['source_run_dir']}`",
                "- note: this is reused tune-side evidence for `R0`",
            ]
        )
    else:
        effect_lines.append(f"- prior_{source.starting_label}_reward: unavailable")
    (r0_dir / "round_0_effect_estimate.md").write_text("\n".join(effect_lines) + "\n")
    (r0_dir / "round_0_risk_note.md").write_text(
        f"# Round 0 Risk Note\n\n- baseline risks are inherited from the current `{source.starting_label}` artifact\n"
    )
    (r0_dir / "round_0_diagnosis_table.md").write_text(
        "\n".join(
            [
                "# Round 0 Diagnosis Table",
                "",
                "| issue | evidence | suspected cause | edit target | confidence |",
                "| --- | --- | --- | --- | --- |",
                "| bootstrap baseline | existing tune-side evidence | none yet | none | medium |",
            ]
        )
        + "\n"
    )
    tune_check_dir = ensure_dir(r0_dir / "tune_check")
    if starting_row:
        starting_tune_row = dict(starting_row)
        starting_tune_row["condition"] = starting_condition
        starting_tune_row["skill_source"] = str(source.starting_skillpack_dir)
        write_json(tune_check_dir / "result.json", starting_tune_row)
    else:
        write_json(
            tune_check_dir / "result.json",
            {
                "task_id": task.task_id,
                "condition": starting_condition,
                "reward": None,
                "exception_stats": {},
                "skill_source": str(source.starting_skillpack_dir),
                "note": f"no prior {starting_condition} tune evidence available",
            },
        )
    return read_json(tune_check_dir / "result.json")


def render_refine_instruction(*, task: TaskInputs, round_index: int) -> str:
    skill_lines = "\n".join(f"- `{name}`" for name in task.skill_names)
    bundle_line = (
        "- also write `/root/output/skillpack_bundle.yaml` if this task needs a task-level bundle note"
        if len(task.skill_names) > 1
        else "- no bundle yaml is required for single-skill tasks"
    )
    return "\n".join(
        [
            "You are running inside a protocol-controlled SkillX C4 refine task.",
            "",
            "Read the frozen refine inputs from `/root/refine_inputs` and write exactly one round artifact set.",
            "",
            f"- task id: `{task.task_id}`",
            f"- target round: `R{round_index}`",
            "- read first:",
            "  - `/root/refine_inputs/protocols/skillx-refine-protocol-v0.1.md`",
            "  - `/root/refine_inputs/protocols/skillx-refine-bundle-contract-v0.1.md`",
            "- current candidate lives under `/root/refine_inputs/current/skillpack/skills/`",
            "- current ledger lives at `/root/refine_inputs/refine_ledger.md`",
            "- bounded decision context lives under `/root/refine_inputs/decision_context/`",
            "- distilled session evidence, when present, lives under `/root/refine_inputs/static/session_evidence/`",
            "",
            "You must write all of these outputs under `/root/output`:",
            f"- `round_{round_index}_skill.md`",
            f"- `round_{round_index}_refine_memo.md`",
            f"- `round_{round_index}_diff_summary.md`",
            f"- `round_{round_index}_effect_estimate.md`",
            f"- `round_{round_index}_risk_note.md`",
            f"- `round_{round_index}_diagnosis_table.md`",
            "- a materialized refined skillpack under `/root/output/skillpack/skills/<skill>/SKILL.md` for each skill:",
            skill_lines,
            bundle_line,
            "",
            "Rules:",
            "- Stay inside the bounded refine protocol.",
            "- Use only the provided local refine inputs.",
            "- Do not solve the benchmark task directly.",
            "- Do not use held-out evidence.",
            "- Do not output commentary outside the required files.",
            "- Preserve the task's skillpack structure; refine it rather than replacing it with an unrelated strategy.",
            "- Every refined `/root/output/skillpack/skills/<skill>/SKILL.md` must still contain a `# Derived Execution Layer` section header.",
            "- You may compress or clarify the derived layer, but do not remove it entirely from any refined skill.",
            f"- You must write exactly `{len(task.skill_names)}` refined skill files, one for each listed skill, and omit none.",
            "- Before finishing, explicitly verify that every listed skill path exists under `/root/output/skillpack/skills/`.",
        ]
    ) + "\n"


def render_refine_round_test_outputs_py(*, round_index: int, skill_names: list[str], has_bundle: bool) -> str:
    skill_checks = "\n".join(
        [
            "    skillpack_root = OUTPUT_DIR / 'skillpack' / 'skills'",
            "    if not skillpack_root.exists():",
            "        raise SystemExit('missing skillpack/skills output')",
        ]
        + [
            f"    skill_path = skillpack_root / {skill_name!r} / 'SKILL.md'\n"
            "    if not skill_path.exists():\n"
            f"        raise SystemExit('missing refined skill for {skill_name}')\n"
            "    text = skill_path.read_text().strip()\n"
            "    if '# Derived Execution Layer' not in text:\n"
            f"        raise SystemExit('refined skill missing derived layer: {skill_name}')"
            for skill_name in skill_names
        ]
    )
    bundle_check = (
        "    if not (OUTPUT_DIR / 'skillpack_bundle.yaml').exists():\n"
        "        raise SystemExit('missing skillpack_bundle.yaml')\n"
        if has_bundle
        else ""
    )
    return f"""from __future__ import annotations

import shutil
from pathlib import Path


OUTPUT_DIR = Path("/root/output")
EXPORT_DIR = Path("/logs/verifier/exported")
ROUND_INDEX = {round_index}
REQUIRED_FILES = [
    f"round_{{ROUND_INDEX}}_skill.md",
    f"round_{{ROUND_INDEX}}_refine_memo.md",
    f"round_{{ROUND_INDEX}}_diff_summary.md",
    f"round_{{ROUND_INDEX}}_effect_estimate.md",
    f"round_{{ROUND_INDEX}}_risk_note.md",
    f"round_{{ROUND_INDEX}}_diagnosis_table.md",
]


def main() -> int:
    for filename in REQUIRED_FILES:
        path = OUTPUT_DIR / filename
        if not path.exists():
            raise SystemExit(f"missing round artifact: {{filename}}")
        if not path.read_text().strip():
            raise SystemExit(f"empty round artifact: {{filename}}")
{skill_checks}
{bundle_check}    if EXPORT_DIR.exists():
        shutil.rmtree(EXPORT_DIR)
    shutil.copytree(OUTPUT_DIR, EXPORT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def render_refine_test_sh() -> str:
    return """#!/bin/bash
set -euo pipefail
python3 /tests/test_outputs.py
echo 1 > /logs/verifier/reward.txt
"""


def render_refine_task_toml(
    *,
    memory_mb: int = DEFAULT_REFINED_TASK_MEMORY_MB,
    storage_mb: int = DEFAULT_REFINED_TASK_STORAGE_MB,
) -> str:
    return """version = "1.0"

[metadata]
author_name = "OpenAI Codex"
author_email = "noreply@example.com"
difficulty = "medium"
category = "skillx"
tags = ["skillx", "c4", "refine", "protocol"]

[verifier]
timeout_sec = 180.0

[agent]
timeout_sec = 1200.0

[environment]
build_timeout_sec = 300.0
cpus = 1
memory_mb = {memory_mb}
storage_mb = {storage_mb}
gpus = 0
allow_internet = true

[verifier.env]

[solution.env]
""".format(memory_mb=memory_mb, storage_mb=storage_mb)


def render_refine_dockerfile() -> str:
    return """FROM python:3.12-slim

WORKDIR /root
RUN mkdir -p /root/output /root/refine_inputs
COPY refine_inputs /root/refine_inputs
"""


def populate_refine_inputs_dir(
    *,
    task: TaskInputs,
    paths: RefinePaths,
    protocols: ProtocolInputs,
    target_dir: Path,
    previous_round_dir: Path,
) -> None:
    protocols_dir = ensure_dir(target_dir / "protocols")
    static_dir = ensure_dir(target_dir / "static")
    current_dir = ensure_dir(target_dir / "current")
    copy_tree(paths.static_dir, static_dir)
    for src in [
        protocols.refine_protocol_path,
        protocols.bundle_contract_path,
    ]:
        shutil.copy2(src, protocols_dir / src.name)
    copy_tree(previous_round_dir / "skillpack", current_dir / "skillpack")
    bundle_path = previous_round_dir / "skillpack_bundle.yaml"
    if bundle_path.exists():
        shutil.copy2(bundle_path, current_dir / "skillpack_bundle.yaml")
    decision_context_dir = previous_round_dir / "decision_context"
    if decision_context_dir.exists():
        copy_tree(decision_context_dir, ensure_dir(target_dir / "decision_context"))
    shutil.copy2(paths.ledger_path, target_dir / "refine_ledger.md")
    task_context_dir = ensure_dir(target_dir / "task_context")
    shutil.copy2(task.instruction_path, task_context_dir / "instruction.md")
    shutil.copy2(task.task_toml_path, task_context_dir / "task.toml")
    ensure_dir(task_context_dir / "tests")
    shutil.copy2(task.test_sh_path, task_context_dir / "tests" / "test.sh")
    shutil.copy2(task.test_outputs_path, task_context_dir / "tests" / "test_outputs.py")


def create_refine_round_task_sandbox(
    *,
    task: TaskInputs,
    paths: RefinePaths,
    protocols: ProtocolInputs,
    round_index: int,
    previous_round_dir: Path,
    agent_name: str,
    model_name: str,
    round_timeout_multiplier: float,
    override_memory_mb: int | None = None,
    override_storage_mb: int | None = None,
) -> RefineRoundSpec:
    slug = f"round-{round_index}"
    task_dir = paths.root_dir / "refine_tasks" / slug
    if task_dir.exists():
        shutil.rmtree(task_dir)
    ensure_dir(task_dir / "environment")
    ensure_dir(task_dir / "tests")
    ensure_dir(task_dir / "solution")
    (task_dir / "instruction.md").write_text(render_refine_instruction(task=task, round_index=round_index))
    (task_dir / "task.toml").write_text(
        render_refine_task_toml(
            memory_mb=override_memory_mb or DEFAULT_REFINED_TASK_MEMORY_MB,
            storage_mb=override_storage_mb or DEFAULT_REFINED_TASK_STORAGE_MB,
        )
    )
    (task_dir / "environment" / "Dockerfile").write_text(render_refine_dockerfile())
    populate_refine_inputs_dir(
        task=task,
        paths=paths,
        protocols=protocols,
        target_dir=task_dir / "environment" / "refine_inputs",
        previous_round_dir=previous_round_dir,
    )
    (task_dir / "tests" / "test.sh").write_text(render_refine_test_sh())
    (task_dir / "tests" / "test_outputs.py").write_text(
        render_refine_round_test_outputs_py(
            round_index=round_index,
            skill_names=task.skill_names,
            has_bundle=len(task.skill_names) > 1,
        )
    )
    (task_dir / "solution" / "solve.sh").write_text("#!/bin/bash\nexit 0\n")
    config_path = paths.configs_dir / f"{task.task_id}-round-{round_index}.json"
    write_json(
        config_path,
        build_job_config(
            job_name=f"{task.task_id}-round-{round_index}",
            jobs_dir=paths.jobs_dir,
            task_path=task_dir,
            agent_name=agent_name,
            model_name=model_name,
            timeout_multiplier=round_timeout_multiplier,
            n_concurrent_trials=1,
            override_memory_mb=override_memory_mb,
            override_storage_mb=override_storage_mb,
        ),
    )
    return RefineRoundSpec(
        round_index=round_index,
        task_dir=task_dir,
        config_path=config_path,
        jobs_dir=paths.jobs_dir,
        expected_skill_names=task.skill_names,
        has_bundle=len(task.skill_names) > 1,
    )


def collect_refine_round_output(spec: RefineRoundSpec) -> Path:
    job_dir = spec.jobs_dir / spec.config_path.stem
    result_path = job_dir / "result.json"
    if not result_path.exists():
        raise FileNotFoundError(f"refine result missing: {result_path}")
    trial_dirs = sorted(path for path in job_dir.iterdir() if path.is_dir() and (path / "result.json").exists())
    if len(trial_dirs) != 1:
        raise RuntimeError(f"expected exactly one refine trial under {job_dir}, found {len(trial_dirs)}")
    trial_payload = read_json(trial_dirs[0] / "result.json")
    if trial_payload.get("exception_info"):
        raise RuntimeError(f"refine round failed: {trial_payload['exception_info']}")
    exported = trial_dirs[0] / "verifier" / "exported"
    if not exported.exists():
        raise FileNotFoundError(f"refine exported output missing: {exported}")
    return exported


def materialize_round_output(paths: RefinePaths, round_index: int, exported_dir: Path) -> Path:
    destination = round_dir(paths, round_index)
    for child in destination.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    for child in exported_dir.iterdir():
        target = destination / child.name
        if child.is_dir():
            copy_tree(child, target)
        else:
            shutil.copy2(child, target)
    return destination


def materialize_c4_sandbox(task: TaskInputs, run_dir: Path, round_dir_path: Path) -> Path:
    sandbox_dir = run_dir / "artifacts" / "task_sandboxes" / f"c4-{task.task_id}-{round_dir_path.name}"
    copy_tree(task.task_dir, sandbox_dir)
    skills_target = sandbox_dir / "environment" / "skills"
    if skills_target.exists():
        shutil.rmtree(skills_target)
    copy_tree(round_dir_path / "skillpack" / "skills", skills_target)
    return sandbox_dir


def resolve_tune_job_dir(tune_root: Path) -> Path:
    config_path = tune_root / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"missing tune config: {config_path}")
    config_payload = read_json(config_path)
    job_name = config_payload.get("job_name")
    if not isinstance(job_name, str) or not job_name.strip():
        raise ValueError(f"invalid tune job name in {config_path}")
    return tune_root / job_name


def resolve_single_trial_dir(job_dir: Path) -> Path:
    trial_dirs = sorted(path for path in job_dir.iterdir() if path.is_dir() and (path / "result.json").exists())
    if len(trial_dirs) != 1:
        raise RuntimeError(f"expected exactly one trial dir under {job_dir}, found {len(trial_dirs)}")
    return trial_dirs[0]


def find_executor_session_log_path(trial_dir: Path) -> Path:
    candidates = [
        trial_dir / "agent" / "claude-code.txt",
        trial_dir / "agent" / "codex.txt",
        trial_dir / "agent" / "trajectory.json",
        trial_dir / "trial.log",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    raise FileNotFoundError(f"missing executor session log under {trial_dir}")


def write_executor_verifier_summary(
    *,
    trial_dir: Path,
    tune_result: dict[str, Any],
    output_dir: Path,
) -> Path:
    report_path = trial_dir / "verifier" / "report.json"
    verifier_report = read_json(report_path) if report_path.exists() else {}
    summary = verifier_report.get("summary") or {}
    payload = {
        "reward": tune_result.get("reward"),
        "eval_name": tune_result.get("eval_name"),
        "exception_stats": tune_result.get("exception_stats") or {},
        "n_trials": tune_result.get("n_trials"),
        "n_errors": tune_result.get("n_errors"),
        "report_path": str(report_path) if report_path.exists() else None,
        "trial_result_path": str(trial_dir / "result.json"),
        "passed_tests": summary.get("passed"),
        "failed_tests": summary.get("failed"),
        "total_tests": summary.get("total"),
        "pytest_exitcode": verifier_report.get("exitcode"),
    }
    summary_path = ensure_dir(output_dir) / "verifier_summary.json"
    write_json(summary_path, payload)
    return summary_path


def write_executor_soft_failure_artifacts(
    *,
    round_dir_path: Path,
    tune_result: dict[str, Any],
) -> ExecutorOutputs:
    executor_dir = ensure_dir(round_dir_path / "executor")
    failure_dir = ensure_dir(executor_dir / "soft_failure")
    session_log_path = failure_dir / "executor_failure.log"
    exception_stats = tune_result.get("exception_stats") or {}
    message_lines = [
        f"status=executor_soft_failure task={round_dir_path.name}",
        f"failure_stage={tune_result.get('failure_stage') or 'unknown'}",
        f"failure_message={tune_result.get('failure_message') or 'unknown'}",
        f"exception_stats={json.dumps(exception_stats, sort_keys=True)}",
    ]
    session_log_path.write_text("\n".join(message_lines) + "\n")
    summary_path = executor_dir / "verifier_summary.json"
    write_json(
        summary_path,
        {
            "reward": tune_result.get("reward"),
            "eval_name": tune_result.get("eval_name"),
            "exception_stats": exception_stats,
            "n_trials": tune_result.get("n_trials"),
            "n_errors": tune_result.get("n_errors"),
            "report_path": None,
            "trial_result_path": None,
            "session_log_path": str(session_log_path),
            "soft_failure": True,
            "soft_failure_reason": tune_result.get("failure_message"),
            "soft_failure_stage": tune_result.get("failure_stage"),
            "passed_tests": None,
            "failed_tests": None,
            "total_tests": None,
            "pytest_exitcode": None,
        },
    )
    bundle_path = round_dir_path / "skillpack_bundle.yaml"
    current_bundle_path = str(bundle_path) if bundle_path.exists() else None
    return ExecutorOutputs(
        session_log_path=str(session_log_path),
        verifier_summary_path=str(summary_path),
        current_skillpack_dir=str(round_dir_path / "skillpack"),
        current_bundle_path=current_bundle_path,
    )


def _role_failure_stage_label(stage: str) -> str:
    if stage == "role_a":
        return "RoleA"
    if stage == "role_b":
        return "RoleB"
    raise ValueError(f"unsupported role failure stage: {stage}")


def _role_failure_exception_key(stage: str, error: Exception) -> str:
    prefix = _role_failure_stage_label(stage)
    if isinstance(error, PlaybookAgentTimeoutError):
        suffix = "AgentTimeoutError"
    elif isinstance(error, PlaybookAgentExecutionError):
        suffix = "AgentExecutionError"
    elif isinstance(error, PlaybookAgentOutputContractError):
        suffix = "AgentOutputContractError"
    else:
        suffix = type(error).__name__
    return f"{prefix}{suffix}"


def _role_failure_message(stage: str, error: Exception) -> str:
    return f"{stage}: {type(error).__name__}: {error}"


def annotate_tune_result_with_role_failure(
    *,
    round_dir_path: Path,
    tune_result: dict[str, Any],
    stage: str,
    error: Exception,
) -> dict[str, Any]:
    updated = dict(tune_result)
    exception_stats_raw = updated.get("exception_stats") or {}
    exception_stats: dict[str, list[str]] = {}
    if isinstance(exception_stats_raw, dict):
        for key, value in exception_stats_raw.items():
            if isinstance(value, list):
                exception_stats[str(key)] = [str(item) for item in value]
            elif value is None:
                exception_stats[str(key)] = []
            else:
                exception_stats[str(key)] = [str(value)]
    key = _role_failure_exception_key(stage, error)
    message = _role_failure_message(stage, error)
    bucket = exception_stats.setdefault(key, [])
    if message not in bucket:
        bucket.append(message)
    updated["exception_stats"] = exception_stats
    updated["role_agent_failed"] = True
    updated["failure_stage"] = stage
    updated["failure_message"] = message
    write_json(round_dir_path / "tune_check" / "result.json", updated)
    return updated


def _load_existing_session_evidence(path: Path) -> SessionEvidenceArtifact | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        return ensure_valid_session_evidence_artifact(read_json(path))
    except Exception:
        return None


def _write_session_evidence_markdown(path: Path, artifact: SessionEvidenceArtifact) -> None:
    path.write_text(
        "\n".join(
            [
                "# Session-Derived Evidence",
                "",
                f"- task_id: `{artifact.task_id}`",
                f"- round_index: `{artifact.round_index}`",
                f"- role: `{artifact.role}`",
                f"- model_name: `{artifact.model_name}`",
                f"- dominant_failure_pattern: `{artifact.dominant_failure_pattern}`",
                f"- source_log_paths: `{', '.join(artifact.source_log_paths) or 'none'}`",
                "",
                "## Critical Turns",
                "",
                *([f"- {item}" for item in artifact.critical_turns] or ["- none"]),
                "",
                "## Recommended Edit Targets",
                "",
                *([f"- {item}" for item in artifact.recommended_edit_targets] or ["- none"]),
                "",
                "## Evidence Refs",
                "",
                *([f"- {item}" for item in artifact.evidence_refs] or ["- none"]),
                "",
                f"- observed_at: `{artifact.observed_at}`",
            ]
        )
        + "\n"
    )


def _role_failure_artifact_ref(*, role_dir: Path, fallback: Path) -> str:
    candidates = [
        role_dir / "agent_run" / "run_metadata.json",
        role_dir / "agent_run" / "stderr.txt",
        role_dir / "agent_run" / "stdout.jsonl",
        fallback,
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return str(fallback)


def build_synthetic_c4ar_role_failure_outputs(
    *,
    task: TaskInputs,
    round_index: int,
    round_dir_path: Path,
    executor_outputs: ExecutorOutputs,
    tune_result: dict[str, Any],
    failure_stage: str,
    error: Exception,
    role_a_model_name: str,
    role_b_model_name: str,
) -> OrchestratorOutputs:
    role_a_dir = ensure_dir(round_dir_path / "role_a")
    role_b_dir = ensure_dir(round_dir_path / "role_b")
    event_log_path = round_dir_path / "orchestrator_log.ndjson"
    failure_message = tune_result.get("failure_message") or _role_failure_message(failure_stage, error)
    current_skillpack_dir = executor_outputs.current_skillpack_dir
    skillpack_dir = Path(current_skillpack_dir)
    skill_files = collect_skillpack_files(skillpack_dir)
    if not skill_files:
        skill_files = [f"skills/{skill_name}/SKILL.md" for skill_name in task.skill_names]
    session_evidence_json_path = role_a_dir / "session_evidence.json"
    session_evidence_md_path = role_a_dir / "session_evidence.md"
    existing_session_evidence = _load_existing_session_evidence(session_evidence_json_path)
    if existing_session_evidence is None:
        dominant_failure_pattern = (
            "role_a runtime failure"
            if failure_stage == "role_a"
            else "role_b runtime failure after role_a completed"
        )
        session_evidence = SessionEvidenceArtifact(
            task_id=task.task_id,
            round_index=round_index,
            role="role_a",
            model_name=role_a_model_name,
            source_log_paths=[executor_outputs.session_log_path],
            dominant_failure_pattern=dominant_failure_pattern,
            wasted_loop_signals=[],
            tool_misuse_signals=[],
            critical_turns=[failure_message],
            skill_misguidance_signals=[],
            recommended_edit_targets=[],
            evidence_refs=[f"{executor_outputs.session_log_path}:1"],
            observed_at=_timestamp(),
        )
        write_json(session_evidence_json_path, session_evidence.to_dict())
    else:
        session_evidence = existing_session_evidence
    _write_session_evidence_markdown(session_evidence_md_path, session_evidence)

    failure_reason = (
        f"{failure_stage.replace('_', ' ')} failed after executor completed; stopping this round"
    )
    refine_plan_json_path = role_b_dir / "refine_plan.json"
    refine_plan_md_path = role_b_dir / "refine_plan.md"
    next_manifest_json_path = role_b_dir / "next_skillpack_manifest.json"
    round_decision_json_path = role_b_dir / "round_decision.json"

    write_json(
        refine_plan_json_path,
        {
            "task_id": task.task_id,
            "round_index": round_index,
            "role": "role_b",
            "model_name": role_b_model_name,
            "summary": failure_reason,
            "atomic_operations": [],
        },
    )
    refine_plan_md_path.write_text(
        "\n".join(
            [
                "# Refine Plan",
                "",
                f"- summary: `{failure_reason}`",
                f"- failure_message: `{failure_message}`",
                "- atomic_operations: `none`",
            ]
        )
        + "\n"
    )

    next_manifest = NextSkillpackManifest(
        task_id=task.task_id,
        round_index=round_index,
        role="role_b",
        model_name=role_b_model_name,
        skillpack_dir=current_skillpack_dir,
        skill_files=skill_files,
        prompt_invariant=True,
        derived_from_round=round_index,
        bundle_path=executor_outputs.current_bundle_path,
    )
    round_decision = RoundDecisionArtifact(
        task_id=task.task_id,
        round_index=round_index,
        role="role_b",
        model_name=role_b_model_name,
        decision="stop",
        reason=failure_reason,
        next_round_index=None,
        next_skillpack_dir=None,
        selected_candidate_label=f"R{round_index}",
    )
    write_json(next_manifest_json_path, next_manifest.to_dict())
    write_json(round_decision_json_path, round_decision.to_dict())

    events = [
        {
            "task_id": task.task_id,
            "round_index": round_index,
            "role": "orchestrator",
            "event_type": "round_started",
            "status": "running",
            "timestamp": _timestamp(),
            "artifact_ref": current_skillpack_dir,
            "note": "starting sequential C4AR round",
        },
        {
            "task_id": task.task_id,
            "round_index": round_index,
            "role": "orchestrator",
            "event_type": "executor_completed",
            "status": "ok",
            "timestamp": _timestamp(),
            "artifact_ref": executor_outputs.verifier_summary_path,
            "note": None,
        },
    ]
    if failure_stage == "role_b":
        events.append(
            {
                "task_id": task.task_id,
                "round_index": round_index,
                "role": "orchestrator",
                "event_type": "role_a_completed",
                "status": "ok",
                "timestamp": _timestamp(),
                "artifact_ref": str(session_evidence_json_path),
                "note": "reused completed role_a outputs before role_b failure",
            }
        )
    events.extend(
        [
            {
                "task_id": task.task_id,
                "round_index": round_index,
                "role": "orchestrator",
                "event_type": f"{failure_stage}_failed",
                "status": "failed",
                "timestamp": _timestamp(),
                "artifact_ref": _role_failure_artifact_ref(
                    role_dir=role_a_dir if failure_stage == "role_a" else role_b_dir,
                    fallback=session_evidence_json_path if failure_stage == "role_a" else round_decision_json_path,
                ),
                "note": failure_message,
            },
            {
                "task_id": task.task_id,
                "round_index": round_index,
                "role": "orchestrator",
                "event_type": "round_decision_loaded",
                "status": "stop",
                "timestamp": _timestamp(),
                "artifact_ref": str(round_decision_json_path),
                "note": failure_reason,
            },
        ]
    )
    event_log_path.write_text("".join(json.dumps(event) + "\n" for event in events))

    return OrchestratorOutputs(
        event_log_path=str(event_log_path),
        session_evidence=session_evidence,
        next_skillpack_manifest=next_manifest,
        round_decision=round_decision,
    )


def materialize_c4ar_next_round(
    *,
    paths: RefinePaths,
    next_round_index: int,
    next_skillpack_dir: Path,
    bundle_path: Path | None,
) -> Path:
    target_round_dir = round_dir(paths, next_round_index)
    if target_round_dir.exists():
        shutil.rmtree(target_round_dir)
    ensure_dir(target_round_dir)
    copy_tree(next_skillpack_dir, target_round_dir / "skillpack")
    target_bundle_path = target_round_dir / "skillpack_bundle.yaml"
    if bundle_path is not None and bundle_path.exists():
        shutil.copy2(bundle_path, target_bundle_path)
    elif target_bundle_path.exists():
        target_bundle_path.unlink()
    return target_round_dir


def collect_skillpack_files(skillpack_dir: Path) -> list[str]:
    if not skillpack_dir.exists():
        return []
    return sorted(
        str(path.relative_to(skillpack_dir))
        for path in skillpack_dir.rglob("*")
        if path.is_file()
    )


def write_c4ar_terminal_round_artifacts(
    *,
    round_dir_path: Path,
    round_index: int,
    task: TaskInputs,
    tune_result: dict[str, Any],
) -> None:
    skillpack_dir = round_dir_path / "skillpack"
    skill_files = collect_skillpack_files(skillpack_dir)
    if not skill_files:
        skill_files = [f"skills/{skill_name}/SKILL.md" for skill_name in task.skill_names]
    verifier_summary_path = round_dir_path / "executor" / "verifier_summary.json"
    legacy_role_dirs = [name for name in ("role_a", "role_b") if (round_dir_path / name).exists()]
    terminal_reason = (
        "terminal evaluation round; role_a and role_b were skipped because there is no downstream refine round"
    )
    legacy_note = (
        f" Ignored legacy role artifacts: {', '.join(legacy_role_dirs)}."
        if legacy_role_dirs
        else ""
    )
    marker_path = round_dir_path / "terminal_round.json"
    write_json(
        marker_path,
        {
            "task_id": task.task_id,
            "round_index": round_index,
            "mode": "terminal_executor_only",
            "decision": "select_final",
            "reason": terminal_reason,
            "selected_candidate_label": f"R{round_index}",
            "current_skillpack_dir": str(skillpack_dir),
            "bundle_path": str(round_dir_path / "skillpack_bundle.yaml")
            if (round_dir_path / "skillpack_bundle.yaml").exists()
            else None,
            "verifier_summary_path": str(verifier_summary_path) if verifier_summary_path.exists() else None,
            "reward": tune_result.get("reward"),
            "eval_name": tune_result.get("eval_name"),
            "exception_stats": tune_result.get("exception_stats") or {},
            "ignored_legacy_role_dirs": legacy_role_dirs,
            "updated_at": _timestamp(),
        },
    )

    events = [
        {
            "task_id": task.task_id,
            "round_index": round_index,
            "role": "orchestrator",
            "event_type": "round_started",
            "status": "running",
            "timestamp": _timestamp(),
            "artifact_ref": None,
            "note": "terminal executor-only round",
        },
        {
            "task_id": task.task_id,
            "round_index": round_index,
            "role": "executor",
            "event_type": "executor_completed",
            "status": "completed",
            "timestamp": _timestamp(),
            "artifact_ref": str(verifier_summary_path) if verifier_summary_path.exists() else None,
            "note": "terminal evaluation completed",
        },
        {
            "task_id": task.task_id,
            "round_index": round_index,
            "role": "orchestrator",
            "event_type": "terminal_round_completed",
            "status": "select_final",
            "timestamp": _timestamp(),
            "artifact_ref": str(marker_path),
            "note": terminal_reason,
        },
    ]
    (round_dir_path / "orchestrator_log.ndjson").write_text(
        "".join(json.dumps(event) + "\n" for event in events)
    )

    (round_dir_path / f"round_{round_index}_skill.md").write_text(
        "\n".join(
            [
                "# Round Skill Snapshot",
                "",
                f"- task_id: `{task.task_id}`",
                f"- round_index: `R{round_index}`",
                f"- skill_files: `{', '.join(skill_files)}`",
                "- source: `current round skillpack (terminal evaluation)`",
            ]
        )
        + "\n"
    )

    (round_dir_path / f"round_{round_index}_refine_memo.md").write_text(
        "\n".join(
            [
                "# Refine Memo",
                "",
                f"- summary: `{terminal_reason}.{legacy_note}`",
            ]
        )
        + "\n"
    )

    (round_dir_path / f"round_{round_index}_diff_summary.md").write_text(
        "\n".join(
            [
                "# Diff Summary",
                "",
                "- recommended_edit_targets: `none`",
                "- prompt_invariant: `not-applicable (terminal evaluation only)`",
                "- next_skillpack_dir: `not-applicable`",
            ]
        )
        + "\n"
    )

    (round_dir_path / f"round_{round_index}_effect_estimate.md").write_text(
        "\n".join(
            [
                "# Effect Estimate",
                "",
                f"- reward: `{tune_result.get('reward')}`",
                f"- eval_name: `{tune_result.get('eval_name')}`",
                f"- exception_keys: `{', '.join(sorted((tune_result.get('exception_stats') or {}).keys())) or 'none'}`",
            ]
        )
        + "\n"
    )

    (round_dir_path / f"round_{round_index}_risk_note.md").write_text(
        "\n".join(
            [
                "# Risk Note",
                "",
                "- decision: `select_final`",
                f"- reason: `{terminal_reason}`",
            ]
        )
        + "\n"
    )

    (round_dir_path / f"round_{round_index}_diagnosis_table.md").write_text(
        "\n".join(
            [
                "# Diagnosis Table",
                "",
                "- dominant_failure_pattern: `not assessed in terminal evaluation round`",
                "",
                "## Planned Operations",
                "",
                "- none",
            ]
        )
        + "\n"
    )


def write_c4ar_round_artifacts(
    *,
    round_dir_path: Path,
    round_index: int,
    task: TaskInputs,
    orchestrator_outputs: OrchestratorOutputs,
    tune_result: dict[str, Any],
) -> None:
    role_b_dir = round_dir_path / "role_b"
    refine_plan_payload = {}
    refine_plan_json_path = role_b_dir / "refine_plan.json"
    if refine_plan_json_path.exists():
        refine_plan_payload = read_json(refine_plan_json_path)
    atomic_operations = refine_plan_payload.get("atomic_operations") or []
    recommended_targets = orchestrator_outputs.session_evidence.recommended_edit_targets
    skill_files = orchestrator_outputs.next_skillpack_manifest.skill_files

    (round_dir_path / f"round_{round_index}_skill.md").write_text(
        "\n".join(
            [
                "# Round Skill Snapshot",
                "",
                f"- task_id: `{task.task_id}`",
                f"- round_index: `R{round_index}`",
                f"- skill_files: `{', '.join(skill_files)}`",
            ]
        )
        + "\n"
    )

    refine_plan_markdown_path = role_b_dir / "refine_plan.md"
    if refine_plan_markdown_path.exists():
        shutil.copy2(refine_plan_markdown_path, round_dir_path / f"round_{round_index}_refine_memo.md")
    else:
        (round_dir_path / f"round_{round_index}_refine_memo.md").write_text(
            "\n".join(
                [
                    "# Refine Memo",
                    "",
                    f"- summary: `{refine_plan_payload.get('summary', 'not available')}`",
                ]
            )
            + "\n"
        )

    (round_dir_path / f"round_{round_index}_diff_summary.md").write_text(
        "\n".join(
            [
                "# Diff Summary",
                "",
                f"- recommended_edit_targets: `{', '.join(recommended_targets) or 'none'}`",
                f"- prompt_invariant: `{orchestrator_outputs.next_skillpack_manifest.prompt_invariant}`",
                f"- next_skillpack_dir: `{orchestrator_outputs.next_skillpack_manifest.skillpack_dir}`",
            ]
        )
        + "\n"
    )

    (round_dir_path / f"round_{round_index}_effect_estimate.md").write_text(
        "\n".join(
            [
                "# Effect Estimate",
                "",
                f"- reward: `{tune_result.get('reward')}`",
                f"- eval_name: `{tune_result.get('eval_name')}`",
                f"- exception_keys: `{', '.join(sorted((tune_result.get('exception_stats') or {}).keys())) or 'none'}`",
            ]
        )
        + "\n"
    )

    (round_dir_path / f"round_{round_index}_risk_note.md").write_text(
        "\n".join(
            [
                "# Risk Note",
                "",
                f"- decision: `{orchestrator_outputs.round_decision.decision}`",
                f"- reason: `{orchestrator_outputs.round_decision.reason}`",
            ]
        )
        + "\n"
    )

    op_lines = [f"- `{op.get('op_id')}` `{op.get('action_type')}` -> `{op.get('target_id')}`" for op in atomic_operations]
    if not op_lines:
        op_lines = ["- none"]
    (round_dir_path / f"round_{round_index}_diagnosis_table.md").write_text(
        "\n".join(
            [
                "# Diagnosis Table",
                "",
                f"- dominant_failure_pattern: `{orchestrator_outputs.session_evidence.dominant_failure_pattern}`",
                "",
                "## Planned Operations",
                "",
                *op_lines,
            ]
        )
        + "\n"
    )


def build_synthetic_c4ar_executor_failure_outputs(
    *,
    task: TaskInputs,
    round_index: int,
    round_dir_path: Path,
    executor_outputs: ExecutorOutputs,
    tune_result: dict[str, Any],
    role_a_model_name: str,
    role_b_model_name: str,
) -> OrchestratorOutputs:
    role_a_dir = ensure_dir(round_dir_path / "role_a")
    role_b_dir = ensure_dir(round_dir_path / "role_b")
    event_log_path = round_dir_path / "orchestrator_log.ndjson"
    skillpack_dir = Path(executor_outputs.current_skillpack_dir)
    skill_files = collect_skillpack_files(skillpack_dir)
    if not skill_files:
        skill_files = [f"skills/{skill_name}/SKILL.md" for skill_name in task.skill_names]

    failure_reason = (
        "executor/tune_check infrastructure failure; role_a and role_b were skipped for this round"
    )
    failure_message = tune_result.get("failure_message") or "Harbor executor failed before producing trial outputs"
    session_evidence = SessionEvidenceArtifact(
        task_id=task.task_id,
        round_index=round_index,
        role="role_a",
        model_name=role_a_model_name,
        source_log_paths=[executor_outputs.session_log_path],
        dominant_failure_pattern="executor infrastructure failure",
        wasted_loop_signals=[],
        tool_misuse_signals=[],
        critical_turns=[failure_message],
        skill_misguidance_signals=[],
        recommended_edit_targets=[],
        evidence_refs=[f"{executor_outputs.session_log_path}:1"],
        observed_at=_timestamp(),
    )
    next_manifest = NextSkillpackManifest(
        task_id=task.task_id,
        round_index=round_index,
        role="role_b",
        model_name=role_b_model_name,
        skillpack_dir=executor_outputs.current_skillpack_dir,
        skill_files=skill_files,
        prompt_invariant=True,
        derived_from_round=round_index,
        bundle_path=executor_outputs.current_bundle_path,
    )
    round_decision = RoundDecisionArtifact(
        task_id=task.task_id,
        round_index=round_index,
        role="role_b",
        model_name=role_b_model_name,
        decision="stop",
        reason=failure_reason,
        next_round_index=None,
        next_skillpack_dir=None,
        selected_candidate_label=f"R{round_index}",
    )

    session_evidence_json_path = role_a_dir / "session_evidence.json"
    session_evidence_md_path = role_a_dir / "session_evidence.md"
    refine_plan_json_path = role_b_dir / "refine_plan.json"
    refine_plan_md_path = role_b_dir / "refine_plan.md"
    next_manifest_json_path = role_b_dir / "next_skillpack_manifest.json"
    round_decision_json_path = role_b_dir / "round_decision.json"

    write_json(session_evidence_json_path, session_evidence.to_dict())
    session_evidence_md_path.write_text(
        "\n".join(
            [
                "# Session-Derived Evidence",
                "",
                f"- dominant_failure_pattern: `{session_evidence.dominant_failure_pattern}`",
                f"- critical_turn: `{failure_message}`",
                f"- source_log_path: `{executor_outputs.session_log_path}`",
            ]
        )
        + "\n"
    )
    write_json(
        refine_plan_json_path,
        {
            "task_id": task.task_id,
            "round_index": round_index,
            "role": "role_b",
            "model_name": role_b_model_name,
            "summary": failure_reason,
            "atomic_operations": [],
        },
    )
    refine_plan_md_path.write_text(
        "\n".join(
            [
                "# Refine Plan",
                "",
                f"- summary: `{failure_reason}`",
                "- atomic_operations: `none`",
            ]
        )
        + "\n"
    )
    write_json(next_manifest_json_path, next_manifest.to_dict())
    write_json(round_decision_json_path, round_decision.to_dict())

    events = [
        {
            "task_id": task.task_id,
            "round_index": round_index,
            "role": "orchestrator",
            "event_type": "round_started",
            "status": "running",
            "timestamp": _timestamp(),
            "artifact_ref": executor_outputs.current_skillpack_dir,
            "note": "starting sequential C4AR round",
        },
        {
            "task_id": task.task_id,
            "round_index": round_index,
            "role": "orchestrator",
            "event_type": "executor_soft_failed",
            "status": "failed",
            "timestamp": _timestamp(),
            "artifact_ref": executor_outputs.verifier_summary_path,
            "note": failure_message,
        },
        {
            "task_id": task.task_id,
            "round_index": round_index,
            "role": "orchestrator",
            "event_type": "round_decision_loaded",
            "status": "stop",
            "timestamp": _timestamp(),
            "artifact_ref": str(round_decision_json_path),
            "note": failure_reason,
        },
    ]
    event_log_path.write_text("".join(json.dumps(event) + "\n" for event in events))

    return OrchestratorOutputs(
        event_log_path=str(event_log_path),
        session_evidence=session_evidence,
        next_skillpack_manifest=next_manifest,
        round_decision=round_decision,
    )


def existing_c4ar_round_outputs(
    *,
    round_dir_path: Path,
    task_id: str,
) -> tuple[OrchestratorOutputs, dict[str, Any]] | None:
    tune_result = existing_tune_result(task_id=task_id, round_dir_path=round_dir_path, skill_source=str(round_dir_path / "skillpack"))
    if tune_result is None:
        return None
    session_evidence_path = round_dir_path / "role_a" / "session_evidence.json"
    next_manifest_path = round_dir_path / "role_b" / "next_skillpack_manifest.json"
    round_decision_path = round_dir_path / "role_b" / "round_decision.json"
    event_log_path = round_dir_path / "orchestrator_log.ndjson"
    if not (session_evidence_path.exists() and next_manifest_path.exists() and round_decision_path.exists()):
        return None
    from skillx.c4ar.contracts import (
        ensure_valid_next_skillpack_manifest,
        ensure_valid_round_decision_artifact,
        ensure_valid_session_evidence_artifact,
    )

    outputs = OrchestratorOutputs(
        event_log_path=str(event_log_path),
        session_evidence=ensure_valid_session_evidence_artifact(read_json(session_evidence_path)),
        next_skillpack_manifest=ensure_valid_next_skillpack_manifest(
            normalize_skill_files_within_skillpack(read_json(next_manifest_path))
        ),
        round_decision=ensure_valid_round_decision_artifact(read_json(round_decision_path)),
    )
    return outputs, tune_result


def existing_executor_outputs(
    *,
    round_dir_path: Path,
    task_id: str,
) -> tuple[ExecutorOutputs, dict[str, Any]] | None:
    tune_result = existing_tune_result(task_id=task_id, round_dir_path=round_dir_path, skill_source=str(round_dir_path / "skillpack"))
    if tune_result is None:
        return None
    verifier_summary_path = round_dir_path / "executor" / "verifier_summary.json"
    if not verifier_summary_path.exists():
        return None
    summary_payload = read_json(verifier_summary_path)
    session_log_path_value = summary_payload.get("session_log_path")
    session_log_path: Path | None = None
    if isinstance(session_log_path_value, str) and session_log_path_value.strip():
        candidate = Path(session_log_path_value)
        if candidate.exists() and candidate.is_file():
            session_log_path = candidate
    if session_log_path is None:
        trial_result_path = summary_payload.get("trial_result_path")
        if not isinstance(trial_result_path, str) or not trial_result_path.strip():
            return None
        trial_dir = Path(trial_result_path).parent
        if not trial_dir.exists():
            return None
        session_log_path = find_executor_session_log_path(trial_dir)
    bundle_path = round_dir_path / "skillpack_bundle.yaml"
    current_bundle_path = str(bundle_path) if bundle_path.exists() else None
    return (
        ExecutorOutputs(
            session_log_path=str(session_log_path),
            verifier_summary_path=str(verifier_summary_path),
            current_skillpack_dir=str(round_dir_path / "skillpack"),
            current_bundle_path=current_bundle_path,
        ),
        tune_result,
    )


def ensure_c4ar_executor_outputs(
    *,
    task: TaskInputs,
    round_dir_path: Path,
    skillsbench_root: Path,
    oauth_file: Path | None,
    agent_name: str,
    model_name: str,
    tune_timeout_multiplier: float,
    run_dir: Path,
    override_memory_mb: int | None = None,
    override_storage_mb: int | None = None,
) -> tuple[ExecutorOutputs, dict[str, Any]]:
    cached_executor = existing_executor_outputs(round_dir_path=round_dir_path, task_id=task.task_id)
    if cached_executor is not None:
        return cached_executor

    tune_root = round_dir_path / "tune_check"
    if (tune_root / "result.json").exists() and not (tune_root / "config.json").exists():
        (tune_root / "result.json").unlink()
    tune_result = run_round_tune_check(
        task=task,
        run_dir=run_dir,
        round_dir_path=round_dir_path,
        skillsbench_root=skillsbench_root,
        oauth_file=oauth_file,
        agent_name=agent_name,
        model_name=model_name,
        timeout_multiplier=tune_timeout_multiplier,
        override_memory_mb=override_memory_mb,
        override_storage_mb=override_storage_mb,
    )
    if tune_result_has_executor_unavailable(tune_result):
        return write_executor_soft_failure_artifacts(round_dir_path=round_dir_path, tune_result=tune_result), tune_result
    job_dir = resolve_tune_job_dir(tune_root)
    trial_dir = resolve_single_trial_dir(job_dir)
    session_log_path = find_executor_session_log_path(trial_dir)
    verifier_summary_path = write_executor_verifier_summary(
        trial_dir=trial_dir,
        tune_result=tune_result,
        output_dir=round_dir_path / "executor",
    )
    bundle_path = round_dir_path / "skillpack_bundle.yaml"
    current_bundle_path = str(bundle_path) if bundle_path.exists() else None
    return (
        ExecutorOutputs(
            session_log_path=str(session_log_path),
            verifier_summary_path=str(verifier_summary_path),
            current_skillpack_dir=str(round_dir_path / "skillpack"),
            current_bundle_path=current_bundle_path,
        ),
        tune_result,
    )


def infer_c4ar_resume_round_index(
    *,
    run_dir: Path,
    task_id: str,
    round_budget: int,
) -> int:
    rounds_dir = run_dir / "refine" / task_id / "rounds"
    if not rounds_dir.exists():
        return 0
    existing_indices = sorted(
        round_index
        for round_index in range(0, round_budget + 1)
        if (rounds_dir / f"round-{round_index}").exists()
    )
    if not existing_indices:
        return 0
    highest_complete_index: int | None = None
    highest_complete_outputs: OrchestratorOutputs | None = None
    for round_index in existing_indices:
        current_round_dir = rounds_dir / f"round-{round_index}"
        cached = existing_c4ar_round_outputs(round_dir_path=current_round_dir, task_id=task_id)
        if cached is None and round_index == round_budget:
            terminal_cached = existing_executor_outputs(round_dir_path=current_round_dir, task_id=task_id)
            if terminal_cached is not None:
                return round_budget
        if cached is None:
            return round_index
        highest_complete_index = round_index
        highest_complete_outputs, _ = cached
    if highest_complete_index is None or highest_complete_outputs is None:
        return 0
    round_decision = highest_complete_outputs.round_decision
    decision_name = round_decision["decision"] if isinstance(round_decision, dict) else round_decision.decision
    if decision_name != "continue":
        return min(highest_complete_index, round_budget)
    next_round_index = (
        round_decision.get("next_round_index")
        if isinstance(round_decision, dict)
        else round_decision.next_round_index
    )
    if isinstance(next_round_index, int):
        return max(0, min(next_round_index, round_budget))
    return max(0, min(highest_complete_index + 1, round_budget))


def existing_completed_round_rows(
    *,
    paths: RefinePaths,
    task_id: str,
    stop_before_round_index: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for round_index in range(0, stop_before_round_index):
        round_dir_path = round_dir(paths, round_index)
        tune_result = existing_tune_result(
            task_id=task_id,
            round_dir_path=round_dir_path,
            skill_source=str(round_dir_path / "skillpack"),
        )
        if tune_result is None:
            continue
        rows.append(build_round_row(round_index, round_dir_path, tune_result))
    return rows


def prepare_c4ar_resume_round(
    *,
    task: TaskInputs,
    paths: RefinePaths,
    round_index: int,
) -> None:
    if round_index <= 0:
        return
    current_round_dir = round_dir(paths, round_index)
    if (current_round_dir / "skillpack").exists():
        return
    previous_round_dir = round_dir(paths, round_index - 1)
    cached = existing_c4ar_round_outputs(round_dir_path=previous_round_dir, task_id=task.task_id)
    if cached is None:
        return
    orchestrator_outputs, _ = cached
    round_decision = orchestrator_outputs.round_decision
    decision_name = round_decision["decision"] if isinstance(round_decision, dict) else round_decision.decision
    if decision_name != "continue":
        return
    next_round_index = (
        round_decision.get("next_round_index")
        if isinstance(round_decision, dict)
        else round_decision.next_round_index
    )
    target_round_index = next_round_index if isinstance(next_round_index, int) else round_index
    if target_round_index != round_index:
        return
    next_manifest = orchestrator_outputs.next_skillpack_manifest
    skillpack_dir = Path(next_manifest["skillpack_dir"]) if isinstance(next_manifest, dict) else Path(next_manifest.skillpack_dir)
    bundle_path_str = next_manifest.get("bundle_path") if isinstance(next_manifest, dict) else next_manifest.bundle_path
    materialize_c4ar_next_round(
        paths=paths,
        next_round_index=round_index,
        next_skillpack_dir=skillpack_dir,
        bundle_path=Path(bundle_path_str) if bundle_path_str else None,
    )


def c4ar_resume_requires_backup(
    *,
    run_dir: Path,
    task_id: str,
    round_budget: int,
) -> bool:
    rounds_dir = run_dir / "refine" / task_id / "rounds"
    if not rounds_dir.exists():
        return False
    for round_index in range(0, round_budget + 1):
        current_round_dir = rounds_dir / f"round-{round_index}"
        if not current_round_dir.exists():
            continue
        cached = existing_c4ar_round_outputs(round_dir_path=current_round_dir, task_id=task_id)
        if cached is None and round_index == round_budget:
            terminal_cached = existing_executor_outputs(round_dir_path=current_round_dir, task_id=task_id)
            if terminal_cached is not None:
                continue
        if round_index > 0 and cached is None:
            return True
        if cached is None:
            continue
        if round_index >= round_budget:
            continue
        orchestrator_outputs, _ = cached
        round_decision = orchestrator_outputs.round_decision
        decision_name = round_decision["decision"] if isinstance(round_decision, dict) else round_decision.decision
        if decision_name != "continue":
            continue
        next_round_index = (
            round_decision.get("next_round_index")
            if isinstance(round_decision, dict)
            else round_decision.next_round_index
        )
        target_round_index = next_round_index if isinstance(next_round_index, int) else round_index + 1
        if (rounds_dir / f"round-{target_round_index}").exists():
            return True
    return False


def backup_run_dir_before_resume(
    *,
    run_dir: Path,
    reason: str,
    timestamp_label: str | None = None,
) -> Path:
    stamp = timestamp_label or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archives_root = ensure_dir(run_dir.parent.parent / "archives" / f"pre-resume-{run_dir.name}-{stamp}")
    archive_path = archives_root / f"{run_dir.name}.tar.gz"
    with tarfile.open(archive_path, "w:gz") as handle:
        handle.add(run_dir, arcname=str(run_dir.relative_to(run_dir.parent.parent)))
    manifest_lines = [
        "# Pre-Resume Safety Backup",
        "",
        f"- created_at_utc: `{stamp}`",
        f"- run_dir: `{run_dir}`",
        f"- archive: `{archive_path.name}`",
        f"- reason: `{reason}`",
    ]
    (archives_root / "BACKUP_MANIFEST.md").write_text("\n".join(manifest_lines) + "\n")
    return archive_path


def run_c4ar_round_with_harbor(
    *,
    task: TaskInputs,
    round_index: int,
    round_dir_path: Path,
    skillsbench_root: Path,
    oauth_file: Path | None,
    agent_name: str,
    model_name: str,
    tune_timeout_multiplier: float,
    run_dir: Path,
    override_memory_mb: int | None = None,
    override_storage_mb: int | None = None,
    role_a_model_name: str = "codex-5.3",
    role_b_model_name: str = "gpt-5.4",
    role_a_playbook_path: Path = DEFAULT_ROLE_A_PLAYBOOK,
    role_b_playbook_path: Path = DEFAULT_ROLE_B_PLAYBOOK,
    role_a_runner: Any = run_role_a,
    role_b_runner: Any = run_role_b,
) -> tuple[OrchestratorOutputs, dict[str, Any]]:
    cached = existing_c4ar_round_outputs(round_dir_path=round_dir_path, task_id=task.task_id)
    if cached is not None:
        return cached

    executor_outputs, tune_result = ensure_c4ar_executor_outputs(
        task=task,
        round_dir_path=round_dir_path,
        skillsbench_root=skillsbench_root,
        oauth_file=oauth_file,
        agent_name=agent_name,
        model_name=model_name,
        tune_timeout_multiplier=tune_timeout_multiplier,
        run_dir=run_dir,
        override_memory_mb=override_memory_mb,
        override_storage_mb=override_storage_mb,
    )
    if tune_result_has_executor_unavailable(tune_result):
        synthetic_outputs = build_synthetic_c4ar_executor_failure_outputs(
            task=task,
            round_index=round_index,
            round_dir_path=round_dir_path,
            executor_outputs=executor_outputs,
            tune_result=tune_result,
            role_a_model_name=role_a_model_name,
            role_b_model_name=role_b_model_name,
        )
        return synthetic_outputs, tune_result

    bundle_path = round_dir_path / "skillpack_bundle.yaml"
    current_bundle_path = bundle_path if bundle_path.exists() else None

    def executor_runner(executor_inputs: Any) -> ExecutorOutputs:
        del executor_inputs
        return executor_outputs

    failure_context: dict[str, Any] = {"stage": None}

    def role_a_runner_with_resume(inputs: Any, *, config: Any) -> Any:
        failure_context["stage"] = "role_a"
        output_dir = Path(inputs.output_dir)
        json_path = output_dir / "session_evidence.json"
        markdown_path = output_dir / "session_evidence.md"
        if json_path.exists() and markdown_path.exists():
            artifact = ensure_valid_session_evidence_artifact(read_json(json_path))
            return RoleAOutputs(
                json_path=str(json_path),
                    markdown_path=str(markdown_path),
                    artifact=artifact,
                )
        return role_a_runner(inputs, config=config)

    def role_b_runner_with_resume(inputs: Any, *, config: Any) -> Any:
        failure_context["stage"] = "role_b"
        output_dir = Path(inputs.output_dir)
        refine_plan_json_path = output_dir / "refine_plan.json"
        refine_plan_markdown_path = output_dir / "refine_plan.md"
        next_skillpack_manifest_json_path = output_dir / "next_skillpack_manifest.json"
        round_decision_json_path = output_dir / "round_decision.json"
        next_skillpack_dir = output_dir / "next_skillpack"
        if (
            refine_plan_json_path.exists()
            and refine_plan_markdown_path.exists()
            and next_skillpack_manifest_json_path.exists()
            and round_decision_json_path.exists()
            and next_skillpack_dir.exists()
        ):
            canonical_artifacts = load_and_canonicalize_role_b_artifact_files(
                refine_plan_json_path=refine_plan_json_path,
                next_skillpack_manifest_json_path=next_skillpack_manifest_json_path,
                round_decision_json_path=round_decision_json_path,
                rewrite=True,
            )
            return RoleBOutputs(
                refine_plan_json_path=str(refine_plan_json_path),
                refine_plan_markdown_path=str(refine_plan_markdown_path),
                next_skillpack_manifest_json_path=str(next_skillpack_manifest_json_path),
                round_decision_json_path=str(round_decision_json_path),
                next_skillpack_dir=str(next_skillpack_dir),
                refine_plan=canonical_artifacts.refine_plan,
                next_skillpack_manifest=canonical_artifacts.next_skillpack_manifest,
                round_decision=canonical_artifacts.round_decision,
            )
        return role_b_runner(inputs, config=config)

    try:
        orchestrator_outputs = run_c4ar_round(
            OrchestratorInputs(
                task_id=task.task_id,
                round_index=round_index,
                task_prompt_path=str(task.instruction_path),
                current_skillpack_dir=str(round_dir_path / "skillpack"),
                current_bundle_path=str(current_bundle_path) if current_bundle_path is not None else None,
                round_root_dir=str(round_dir_path),
            ),
            config=OrchestratorConfig(
                role_a_config=RoleAConfig(
                    model_name=role_a_model_name,
                    playbook_path=str(role_a_playbook_path),
                ),
                role_b_config=RoleBConfig(
                    model_name=role_b_model_name,
                    playbook_path=str(role_b_playbook_path),
                ),
            ),
            executor_runner=executor_runner,
            role_a_runner=role_a_runner_with_resume,
            role_b_runner=role_b_runner_with_resume,
        )
    except Exception as error:
        failure_stage = failure_context.get("stage")
        if failure_stage not in {"role_a", "role_b"}:
            raise
        tune_result = annotate_tune_result_with_role_failure(
            round_dir_path=round_dir_path,
            tune_result=tune_result,
            stage=str(failure_stage),
            error=error,
        )
        synthetic_outputs = build_synthetic_c4ar_role_failure_outputs(
            task=task,
            round_index=round_index,
            round_dir_path=round_dir_path,
            executor_outputs=executor_outputs,
            tune_result=tune_result,
            failure_stage=str(failure_stage),
            error=error,
            role_a_model_name=role_a_model_name,
            role_b_model_name=role_b_model_name,
        )
        return synthetic_outputs, tune_result
    return orchestrator_outputs, tune_result


def run_terminal_c4ar_round(
    *,
    task: TaskInputs,
    round_index: int,
    round_dir_path: Path,
    skillsbench_root: Path,
    oauth_file: Path | None,
    agent_name: str,
    model_name: str,
    tune_timeout_multiplier: float,
    run_dir: Path,
    override_memory_mb: int | None = None,
    override_storage_mb: int | None = None,
) -> dict[str, Any]:
    del round_index
    _, tune_result = ensure_c4ar_executor_outputs(
        task=task,
        round_dir_path=round_dir_path,
        skillsbench_root=skillsbench_root,
        oauth_file=oauth_file,
        agent_name=agent_name,
        model_name=model_name,
        tune_timeout_multiplier=tune_timeout_multiplier,
        run_dir=run_dir,
        override_memory_mb=override_memory_mb,
        override_storage_mb=override_storage_mb,
    )
    return tune_result


def is_round_materialized(
    *,
    task: TaskInputs,
    round_dir_path: Path,
    round_index: int,
) -> bool:
    required_files = [
        round_dir_path / f"round_{round_index}_skill.md",
        round_dir_path / f"round_{round_index}_refine_memo.md",
        round_dir_path / f"round_{round_index}_diff_summary.md",
        round_dir_path / f"round_{round_index}_effect_estimate.md",
        round_dir_path / f"round_{round_index}_risk_note.md",
        round_dir_path / f"round_{round_index}_diagnosis_table.md",
    ]
    if not all(path.exists() for path in required_files):
        return False
    skillpack_root = round_dir_path / "skillpack" / "skills"
    if not skillpack_root.exists():
        return False
    for skill_name in task.skill_names:
        if not (skillpack_root / skill_name / "SKILL.md").exists():
            return False
    if len(task.skill_names) > 1 and not (round_dir_path / "skillpack_bundle.yaml").exists():
        return False
    return True


def existing_tune_result(
    *,
    task_id: str,
    round_dir_path: Path,
    skill_source: str,
) -> dict[str, Any] | None:
    tune_root = round_dir_path / "tune_check"
    top_level_result = tune_root / "result.json"
    if top_level_result.exists():
        cached = read_json(top_level_result)
        config_path = tune_root / "config.json"
        if not config_path.exists():
            return cached
        config_payload = read_json(config_path)
        job_name = config_payload.get("job_name")
        if not isinstance(job_name, str):
            return cached
        job_dir = tune_root / job_name
        result_path = job_dir / "result.json"
        if not result_path.exists():
            return cached
        canonical = parse_job_result(job_dir, condition="c4", task_id=task_id, skill_source=skill_source)
        if canonical != cached:
            write_json(top_level_result, canonical)
        return canonical
    config_path = tune_root / "config.json"
    if not config_path.exists():
        return None
    config_payload = read_json(config_path)
    job_name = config_payload.get("job_name")
    if not isinstance(job_name, str):
        return None
    job_dir = tune_root / job_name
    result_path = job_dir / "result.json"
    if not result_path.exists():
        return None
    result = parse_job_result(job_dir, condition="c4", task_id=task_id, skill_source=skill_source)
    write_json(top_level_result, result)
    return result


def clear_job_dir(job_dir: Path) -> None:
    if job_dir.exists():
        shutil.rmtree(job_dir)


def is_retryable_refine_contract_failure(job_dir: Path) -> bool:
    trial_dirs = sorted(path for path in job_dir.iterdir() if path.is_dir())
    for trial_dir in trial_dirs:
        test_stdout = trial_dir / "verifier" / "test-stdout.txt"
        if not test_stdout.exists():
            continue
        text = test_stdout.read_text()
        if "missing refined skill for" in text:
            return True
        if "refined skill missing derived layer:" in text:
            return True
    return False


def run_round_tune_check(
    *,
    task: TaskInputs,
    run_dir: Path,
    round_dir_path: Path,
    skillsbench_root: Path,
    oauth_file: Path | None,
    agent_name: str,
    model_name: str,
    timeout_multiplier: float,
    override_memory_mb: int | None = None,
    override_storage_mb: int | None = None,
) -> dict[str, Any]:
    tune_root = ensure_dir(round_dir_path / "tune_check")
    existing = existing_tune_result(task_id=task.task_id, round_dir_path=round_dir_path, skill_source=str(round_dir_path / "skillpack"))
    if existing is not None:
        return existing
    sandbox_dir = materialize_c4_sandbox(task, run_dir, round_dir_path)
    job_name = f"{task.task_id}-{round_dir_path.name}-c4-tune"
    config_path = tune_root / "config.json"
    job_dir = tune_root / job_name

    def run_attempt(*, attempt_timeout_multiplier: float) -> dict[str, Any]:
        write_json(
            config_path,
            build_job_config(
                job_name=job_name,
                jobs_dir=tune_root,
                task_path=sandbox_dir,
                agent_name=agent_name,
                model_name=model_name,
                timeout_multiplier=attempt_timeout_multiplier,
                n_concurrent_trials=1,
                override_memory_mb=override_memory_mb,
                override_storage_mb=override_storage_mb,
            ),
        )
        clear_job_dir(job_dir)
        try:
            run_harbor_job(
                skillsbench_root=skillsbench_root,
                config_path=config_path,
                oauth_file=oauth_file,
                agent_name=agent_name,
            )
        except Exception as error:
            return build_tune_infra_failure_result(
                task_id=task.task_id,
                round_dir_path=round_dir_path,
                error=error,
                stage="harbor_run_failed",
                attempt_timeout_multiplier=attempt_timeout_multiplier,
            )
        try:
            return parse_job_result(
                job_dir,
                condition="c4",
                task_id=task.task_id,
                skill_source=str(round_dir_path / "skillpack"),
            )
        except Exception as error:
            return build_tune_infra_failure_result(
                task_id=task.task_id,
                round_dir_path=round_dir_path,
                error=error,
                stage="result_parse_failed",
                attempt_timeout_multiplier=attempt_timeout_multiplier,
            )

    result = run_attempt(attempt_timeout_multiplier=timeout_multiplier)
    if tune_result_has_timeout_exception(result):
        # Retry timeout outcomes once in-place with double timeout; other failures are final.
        result = run_attempt(attempt_timeout_multiplier=timeout_multiplier * 2.0)
    write_json(tune_root / "result.json", result)
    return result


def append_refine_ledger(
    *,
    paths: RefinePaths,
    round_index: int,
    parent_round_index: int | None,
    tune_result: dict[str, Any],
    note: str | None = None,
) -> None:
    lines: list[str]
    if paths.ledger_path.exists():
        lines = paths.ledger_path.read_text().splitlines()
    else:
        lines = [
            "# Refine Ledger",
            "",
            "| round | parent | reward | exceptions | note |",
            "| --- | --- | ---: | --- | --- |",
        ]
    round_prefix = f"| R{round_index} |"
    if any(line.startswith(round_prefix) for line in lines):
        return
    reward = tune_result.get("reward")
    exceptions = ",".join(sorted((tune_result.get("exception_stats") or {}).keys()))
    parent_label = "-" if parent_round_index is None else f"R{parent_round_index}"
    note_value = note if note is not None else ("bootstrap" if round_index == 0 else "generated round candidate")
    lines.append(f"| R{round_index} | {parent_label} | {reward} | {exceptions} | {note_value} |")
    paths.ledger_path.write_text("\n".join(lines) + "\n")


def select_final_candidate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("no round rows available for final selection")

    def _sort_key(row: dict[str, Any]) -> tuple[float, int]:
        reward = row.get("reward")
        numeric = float(reward) if reward is not None else float("-inf")
        return (numeric, -int(row["round_index"]))

    best = max(rows, key=_sort_key)
    return best


def write_bundle_manifest(
    *,
    paths: RefinePaths,
    task: TaskInputs,
    source_run_dir: Path,
    source: SourceArtifacts,
    tune_run_dirs: list[Path],
    round_budget: int,
    rounds: list[dict[str, Any]],
) -> None:
    payload = {
        "experiment_id": "skillx-skillsbench-001",
        "task_id": task.task_id,
        "run_id": paths.root_dir.parent.parent.name,
        "protocol_version": "skillx-refine-protocol-v0.1",
        "bundle_contract_version": "skillx-refine-bundle-contract-v0.1",
        "starting_artifact": source.starting_label,
        "starting_label": source.starting_label,
        "starting_skillpack_dir": str(source.starting_skillpack_dir),
        "starting_bundle_path": str(source.starting_bundle_path) if source.starting_bundle_path else None,
        "round_budget": round_budget,
        "heldout_eval_visible": False,
        "source_run_dir": str(source_run_dir),
        "tune_run_dirs": [str(path) for path in tune_run_dirs],
        "rounds": rounds,
    }
    write_json(paths.manifest_path, payload)


def write_final_bundle(
    *,
    task: TaskInputs,
    paths: RefinePaths,
    selected_row: dict[str, Any],
    tune_rows: list[dict[str, Any]],
) -> None:
    selected_round_dir = round_dir(paths, int(selected_row["round_index"]))
    selected_skillpack = selected_round_dir / "skillpack" / "skills"
    materialized_target = ensure_dir(paths.final_dir / "materialized_skillpack" / "skills")
    copy_tree(selected_skillpack, materialized_target)
    lines = [
        "# C4 Final Skill Summary",
        "",
        f"- selected_round: `R{selected_row['round_index']}`",
        f"- selected_reward: `{selected_row.get('reward')}`",
        f"- n_skills: `{len(task.skill_names)}`",
        "",
        "## Materialized skill paths",
    ]
    for skill_name in task.skill_names:
        lines.append(f"- `{skill_name}` -> `materialized_skillpack/skills/{skill_name}/SKILL.md`")
    (paths.final_dir / "SKILL.md").write_text("\n".join(lines) + "\n")

    shutil.copy2(
        selected_round_dir / f"round_{selected_row['round_index']}_refine_memo.md",
        paths.final_dir / "final_refine_memo.md",
    )
    shutil.copy2(
        selected_round_dir / f"round_{selected_row['round_index']}_diff_summary.md",
        paths.final_dir / "final_diff_summary.md",
    )
    candidate_pool = ", ".join(f"R{row['round_index']}" for row in tune_rows)
    selection_note = "\n".join(
        [
            "# Final Selection Note",
            "",
            f"- selected_round: `R{selected_row['round_index']}`",
            f"- selected_reward: `{selected_row.get('reward')}`",
            "- selection_rule: highest reward, earliest round on tie",
            f"- candidate_pool: `{candidate_pool}`",
        ]
    )
    (paths.final_dir / "final_selection_note.md").write_text(selection_note + "\n")
    heldout_report = "\n".join(
        [
            "# Held-Out Eval Report",
            "",
            "- status: `skipped`",
            "- reason: `this v0.1 implementation only creates the C4 refine skeleton and tune-side loop; real held-out execution is not connected yet`",
        ]
    )
    (paths.final_dir / "heldout_eval_report.md").write_text(heldout_report + "\n")


def write_environment_notes(run_dir: Path, env_payload: dict[str, Any], args: argparse.Namespace) -> None:
    notes = "\n".join(
        [
            f"- timestamp: `{_timestamp()}`",
            f"- skillsbench_root: `{args.skillsbench_root}`",
            f"- oauth_file: `{args.oauth_file or 'none'}`",
            f"- source_run_dir: `{args.source_run_dir}`",
            f"- tune_run_dirs: `{', '.join(str(path) for path in args.tune_run_dir)}`",
            f"- session_log_paths: `{', '.join(str(path) for path in (args.session_log_path or [])) or 'none'}`",
            f"- refine_protocol_path: `{args.refine_protocol_path}`",
            f"- bundle_contract_path: `{args.bundle_contract_path}`",
            f"- starting_skillpack_dir: `{args.starting_skillpack_dir}`",
            f"- starting_bundle_path: `{args.starting_bundle_path}`",
            f"- starting_label: `{args.starting_label}`",
            f"- benchmark_agent: `{args.agent}`",
            f"- benchmark_model: `{args.model}`",
            f"- round_budget: `{args.round_budget}`",
            f"- round_timeout_multiplier: `{args.round_timeout_multiplier}`",
            f"- tune_timeout_multiplier: `{args.tune_timeout_multiplier}`",
            f"- override_memory_mb: `{args.override_memory_mb}`",
            f"- override_storage_mb: `{args.override_storage_mb}`",
            f"- orchestration_mode: `{args.orchestration_mode}`",
            f"- docker_health_category: `{env_payload['docker_health_category']}`",
            f"- docker_mem_bytes: `{env_payload['docker_mem_bytes']}`",
            f"- uv_path: `{env_payload['uv_path']}`",
        ]
    )
    (run_dir / "ENVIRONMENT_NOTES.md").write_text(notes + "\n")


def write_run_status(run_dir: Path, status: str, args: argparse.Namespace) -> None:
    body = "\n".join(
        [
            f"- status: `{status}`",
            f"- run_id: `{args.run_id}`",
            f"- task: `{args.task}`",
            f"- source_run_dir: `{args.source_run_dir}`",
            f"- round_budget: `{args.round_budget}`",
            f"- orchestration_mode: `{args.orchestration_mode}`",
            f"- updated_at: `{_timestamp()}`",
        ]
    )
    (run_dir / "RUN_STATUS.md").write_text(body + "\n")


def run_refine_rounds(
    *,
    task: TaskInputs,
    paths: RefinePaths,
    protocols: ProtocolInputs,
    skillsbench_root: Path,
    oauth_file: Path | None,
    agent_name: str,
    model_name: str,
    round_timeout_multiplier: float,
    tune_timeout_multiplier: float,
    round_budget: int,
    r0_row: dict[str, Any] | None,
    run_dir: Path,
    source_run_dir: Path,
    starting_label: str,
    session_evidence: SessionDerivedEvidence | None,
    tune_rows: list[dict[str, Any]],
    orchestration_mode: str = DEFAULT_ORCHESTRATION_MODE,
    start_round_index: int = 0,
    failure_context: dict[str, Any] | None = None,
    override_memory_mb: int | None = None,
    override_storage_mb: int | None = None,
) -> list[dict[str, Any]]:
    if orchestration_mode == "c4ar":
        round_rows = existing_completed_round_rows(
            paths=paths,
            task_id=task.task_id,
            stop_before_round_index=start_round_index,
        )
        for round_index in range(start_round_index, round_budget + 1):
            update_failure_context(
                failure_context,
                failed_round=round_index,
                manual_intervention=False,
            )
            current_round_dir = round_dir(paths, round_index)
            if round_index == start_round_index and round_index > 0:
                prepare_c4ar_resume_round(task=task, paths=paths, round_index=round_index)
            if round_index == round_budget:
                update_failure_context(failure_context, failed_stage="terminal_round_executor")
                tune_result = run_terminal_c4ar_round(
                    task=task,
                    round_index=round_index,
                    round_dir_path=current_round_dir,
                    skillsbench_root=skillsbench_root,
                    oauth_file=oauth_file,
                    agent_name=agent_name,
                    model_name=model_name,
                    tune_timeout_multiplier=tune_timeout_multiplier,
                    run_dir=run_dir,
                    override_memory_mb=override_memory_mb,
                    override_storage_mb=override_storage_mb,
                )
                round_row = build_round_row(round_index, current_round_dir, tune_result)
                round_rows.append(round_row)
                append_refine_ledger(
                    paths=paths,
                    round_index=round_index,
                    parent_round_index=None if round_index == 0 else round_index - 1,
                    tune_result=tune_result,
                    note="terminal evaluation",
                )
                write_c4ar_terminal_round_artifacts(
                    round_dir_path=current_round_dir,
                    round_index=round_index,
                    task=task,
                    tune_result=tune_result,
                )
                break
            update_failure_context(failure_context, failed_stage="c4ar_round")
            orchestrator_outputs, tune_result = run_c4ar_round_with_harbor(
                task=task,
                round_index=round_index,
                round_dir_path=current_round_dir,
                skillsbench_root=skillsbench_root,
                oauth_file=oauth_file,
                agent_name=agent_name,
                model_name=model_name,
                tune_timeout_multiplier=tune_timeout_multiplier,
                run_dir=run_dir,
                override_memory_mb=override_memory_mb,
                override_storage_mb=override_storage_mb,
            )
            round_row = build_round_row(round_index, current_round_dir, tune_result)
            round_rows.append(round_row)
            append_refine_ledger(
                paths=paths,
                round_index=round_index,
                parent_round_index=None if round_index == 0 else round_index - 1,
                tune_result=tune_result,
            )
            write_c4ar_round_artifacts(
                round_dir_path=current_round_dir,
                round_index=round_index,
                task=task,
                orchestrator_outputs=orchestrator_outputs,
                tune_result=tune_result,
            )

            round_decision = orchestrator_outputs.round_decision
            decision_name = round_decision["decision"] if isinstance(round_decision, dict) else round_decision.decision
            next_round_index = (
                round_decision.get("next_round_index")
                if isinstance(round_decision, dict)
                else round_decision.next_round_index
            )
            if round_index >= round_budget or decision_name != "continue":
                break

            next_manifest = orchestrator_outputs.next_skillpack_manifest
            skillpack_dir = Path(next_manifest["skillpack_dir"]) if isinstance(next_manifest, dict) else Path(next_manifest.skillpack_dir)
            bundle_path_str = next_manifest.get("bundle_path") if isinstance(next_manifest, dict) else next_manifest.bundle_path
            target_round_index = next_round_index if isinstance(next_round_index, int) else round_index + 1
            if not round_path(paths, target_round_index).exists():
                materialize_c4ar_next_round(
                    paths=paths,
                    next_round_index=target_round_index,
                    next_skillpack_dir=skillpack_dir,
                    bundle_path=Path(bundle_path_str) if bundle_path_str else None,
                )
        return round_rows

    if r0_row is None:
        raise ValueError("legacy orchestration requires r0_row")
    round_rows: list[dict[str, Any]] = [build_round_row(0, round_dir(paths, 0), r0_row)]
    append_refine_ledger(paths=paths, round_index=0, parent_round_index=None, tune_result=r0_row)
    write_round_context_artifacts(
        task=task,
        round_index=0,
        source_run_dir=source_run_dir,
        round_rows=round_rows,
        tune_rows=tune_rows,
        paths=paths,
        starting_label=starting_label,
        session_evidence=session_evidence,
    )

    for round_index in range(1, round_budget + 1):
        update_failure_context(
            failure_context,
            failed_round=round_index,
            manual_intervention=False,
        )
        previous_round_dir = round_dir(paths, round_index - 1)
        current_round_dir = paths.rounds_dir / f"round-{round_index}"
        if current_round_dir.exists():
            existing = existing_tune_result(
                task_id=task.task_id,
                round_dir_path=current_round_dir,
                skill_source=str(current_round_dir / "skillpack"),
            )
            if existing is not None:
                append_refine_ledger(
                    paths=paths,
                    round_index=round_index,
                    parent_round_index=round_index - 1,
                    tune_result=existing,
                )
                round_rows.append(build_round_row(round_index, current_round_dir, existing))
                write_round_context_artifacts(
                    task=task,
                    round_index=round_index,
                    source_run_dir=source_run_dir,
                    round_rows=round_rows,
                    tune_rows=tune_rows,
                    paths=paths,
                    starting_label=starting_label,
                    session_evidence=session_evidence,
                )
                continue
        update_failure_context(failure_context, failed_stage="round_task_sandbox")
        spec = create_refine_round_task_sandbox(
            task=task,
            paths=paths,
            protocols=protocols,
            round_index=round_index,
            previous_round_dir=previous_round_dir,
            agent_name=agent_name,
            model_name=model_name,
            round_timeout_multiplier=round_timeout_multiplier,
            override_memory_mb=override_memory_mb,
            override_storage_mb=override_storage_mb,
        )
        if is_round_materialized(task=task, round_dir_path=current_round_dir, round_index=round_index):
            materialized_round_dir = current_round_dir
        else:
            existing_job_dir = spec.jobs_dir / spec.config_path.stem
            can_reuse_existing_job = False
            if (existing_job_dir / "result.json").exists():
                try:
                    exported_dir = collect_refine_round_output(spec)
                    can_reuse_existing_job = True
                except RuntimeError:
                    clear_job_dir(existing_job_dir)
            if not can_reuse_existing_job:
                update_failure_context(failure_context, failed_stage="round_harbor_run")
                run_harbor_job(
                    skillsbench_root=skillsbench_root,
                    config_path=spec.config_path,
                    oauth_file=oauth_file,
                    agent_name=agent_name,
                )
                try:
                    update_failure_context(failure_context, failed_stage="round_output_collect")
                    exported_dir = collect_refine_round_output(spec)
                except RuntimeError:
                    retry_job_dir = spec.jobs_dir / spec.config_path.stem
                    if not is_retryable_refine_contract_failure(retry_job_dir):
                        raise
                    clear_job_dir(retry_job_dir)
                    update_failure_context(failure_context, failed_stage="round_harbor_run_retry")
                    run_harbor_job(
                        skillsbench_root=skillsbench_root,
                        config_path=spec.config_path,
                        oauth_file=oauth_file,
                        agent_name=agent_name,
                    )
                    update_failure_context(failure_context, failed_stage="round_output_collect_retry")
                    exported_dir = collect_refine_round_output(spec)
            materialized_round_dir = materialize_round_output(paths, round_index, exported_dir)
        update_failure_context(failure_context, failed_stage="tune_check")
        tune_result = run_round_tune_check(
            task=task,
            run_dir=run_dir,
            round_dir_path=materialized_round_dir,
            skillsbench_root=skillsbench_root,
            oauth_file=oauth_file,
            agent_name=agent_name,
            model_name=model_name,
            timeout_multiplier=tune_timeout_multiplier,
            override_memory_mb=override_memory_mb,
            override_storage_mb=override_storage_mb,
        )
        append_refine_ledger(paths=paths, round_index=round_index, parent_round_index=round_index - 1, tune_result=tune_result)
        round_row = build_round_row(round_index, materialized_round_dir, tune_result)
        round_rows.append(round_row)
        write_round_context_artifacts(
            task=task,
            round_index=round_index,
            source_run_dir=source_run_dir,
            round_rows=round_rows,
            tune_rows=tune_rows,
            paths=paths,
            starting_label=starting_label,
            session_evidence=session_evidence,
        )
    return round_rows


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skillsbench-root", type=Path, required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--oauth-file", type=Path)
    parser.add_argument("--source-run-dir", type=Path, required=True)
    parser.add_argument("--starting-skillpack-dir", type=Path)
    parser.add_argument("--starting-bundle-path", type=Path)
    parser.add_argument("--starting-label")
    parser.add_argument("--tune-run-dir", type=Path, action="append")
    parser.add_argument("--session-log-path", type=Path, action="append")
    parser.add_argument("--agent")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--round-budget", type=int, default=3)
    parser.add_argument(
        "--refine-protocol-path",
        type=Path,
        default=ROOT / "plans" / "skillx" / "skillx-refine-protocol-v0.1.md",
    )
    parser.add_argument(
        "--bundle-contract-path",
        type=Path,
        default=ROOT / "plans" / "skillx" / "skillx-refine-bundle-contract-v0.1.md",
    )
    parser.add_argument("--round-timeout-multiplier", type=float, default=2.0)
    parser.add_argument("--tune-timeout-multiplier", type=float, default=1.0)
    parser.add_argument("--override-memory-mb", type=int)
    parser.add_argument("--override-storage-mb", type=int)
    parser.add_argument("--orchestration-mode", choices=("legacy", "c4ar"), default=DEFAULT_ORCHESTRATION_MODE)
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    args.skillsbench_root = args.skillsbench_root.resolve()
    args.output_dir = args.output_dir.resolve()
    args.agent = resolve_benchmark_agent_name(args.agent, args.model)
    args.oauth_file = args.oauth_file.resolve() if args.oauth_file else None
    args.source_run_dir = args.source_run_dir.resolve()
    args.starting_skillpack_dir = args.starting_skillpack_dir.resolve() if args.starting_skillpack_dir else None
    args.starting_bundle_path = args.starting_bundle_path.resolve() if args.starting_bundle_path else None
    args.refine_protocol_path = args.refine_protocol_path.resolve()
    args.bundle_contract_path = args.bundle_contract_path.resolve()
    args.tune_run_dir = [path.resolve() for path in (args.tune_run_dir or [args.source_run_dir])]
    args.session_log_path = [path.resolve() for path in (args.session_log_path or [])]
    run_dir = ensure_dir(args.output_dir)
    run_failure_path = run_dir / "run_failure.json"
    failure_context: dict[str, Any] = {
        "failed_stage": None,
        "failed_round": None,
        "manual_intervention": False,
    }
    try:
        update_failure_context(failure_context, failed_stage="discover_task_inputs")
        task = discover_task_inputs(args.skillsbench_root, args.task)
        if args.orchestration_mode == "c4ar" and c4ar_resume_requires_backup(
            run_dir=run_dir,
            task_id=task.task_id,
            round_budget=args.round_budget,
        ):
            update_failure_context(failure_context, failed_stage="backup_before_resume")
            backup_run_dir_before_resume(
                run_dir=run_dir,
                reason="automatic safety backup before c4ar resume that may rewrite existing round artifacts",
            )
        update_failure_context(failure_context, failed_stage="environment_check")
        env_payload = check_environment(args.skillsbench_root, args.oauth_file, agent_name=args.agent)
        write_environment_notes(run_dir, env_payload, args)
        write_run_status(run_dir, "running", args)

        paths = ensure_refine_paths(run_dir, task.task_id)
        protocols = ProtocolInputs(
            refine_protocol_path=args.refine_protocol_path,
            bundle_contract_path=args.bundle_contract_path,
        )
        update_failure_context(failure_context, failed_stage="locate_source_artifacts")
        source = locate_source_artifacts(
            task.task_id,
            args.source_run_dir,
            starting_skillpack_dir=args.starting_skillpack_dir,
            starting_bundle_path=args.starting_bundle_path,
            starting_label=args.starting_label,
        )
        update_failure_context(failure_context, failed_stage="collect_tune_evidence")
        tune_rows = collect_tune_evidence(task.task_id, args.tune_run_dir)
        update_failure_context(failure_context, failed_stage="expand_session_logs")
        session_log_paths = expand_session_log_paths(args.session_log_path)
        update_failure_context(failure_context, failed_stage="distill_session_logs")
        session_evidence = distill_session_logs(session_log_paths) if session_log_paths else None
        start_round_index = 0
        if args.orchestration_mode == "c4ar":
            update_failure_context(failure_context, failed_stage="infer_resume_round")
            start_round_index = infer_c4ar_resume_round_index(
                run_dir=run_dir,
                task_id=task.task_id,
                round_budget=args.round_budget,
            )
        r0_row: dict[str, Any] | None = None
        if not (args.orchestration_mode == "c4ar" and start_round_index > 0):
            update_failure_context(failure_context, failed_stage="write_static_bundle")
            write_static_bundle(
                task=task,
                paths=paths,
                protocols=protocols,
                source=source,
                tune_rows=tune_rows,
                tune_run_dirs=args.tune_run_dir,
                round_budget=args.round_budget,
                source_run_dir=args.source_run_dir,
                session_evidence=session_evidence,
            )
            update_failure_context(failure_context, failed_stage="make_round_zero_artifacts")
            r0_row = make_round_zero_artifacts(task=task, paths=paths, source=source, tune_rows=tune_rows)
        update_failure_context(failure_context, failed_stage="run_refine_rounds")
        round_rows = run_refine_rounds(
            task=task,
            paths=paths,
            protocols=protocols,
            skillsbench_root=args.skillsbench_root,
            oauth_file=args.oauth_file,
            agent_name=args.agent,
            model_name=args.model,
            round_timeout_multiplier=args.round_timeout_multiplier,
            tune_timeout_multiplier=args.tune_timeout_multiplier,
            round_budget=args.round_budget,
            r0_row=r0_row,
            run_dir=run_dir,
            source_run_dir=args.source_run_dir,
            starting_label=source.starting_label,
            session_evidence=session_evidence,
            tune_rows=tune_rows,
            orchestration_mode=args.orchestration_mode,
            start_round_index=start_round_index,
            failure_context=failure_context,
            override_memory_mb=args.override_memory_mb,
            override_storage_mb=args.override_storage_mb,
        )
        update_failure_context(failure_context, failed_stage="write_bundle_manifest")
        write_bundle_manifest(
            paths=paths,
            task=task,
            source_run_dir=args.source_run_dir,
            source=source,
            tune_run_dirs=args.tune_run_dir,
            round_budget=args.round_budget,
            rounds=round_rows,
        )
        update_failure_context(failure_context, failed_stage="select_final_candidate")
        selected_row = select_final_candidate(round_rows)
        update_failure_context(failure_context, failed_stage="write_final_bundle")
        write_final_bundle(task=task, paths=paths, selected_row=selected_row, tune_rows=round_rows)
        update_failure_context(failure_context, failed_stage="write_summary")
        write_json(paths.summary_path, {"task_id": task.task_id, "selected": selected_row, "rounds": round_rows})
        if run_failure_path.exists():
            run_failure_path.unlink()
        write_run_status(run_dir, "completed", args)
        return 0
    except Exception as error:
        write_run_failure(
            run_failure_path,
            build_main_run_failure_payload(
                error=error,
                args=args,
                failure_context=failure_context,
            ),
        )
        write_run_status(run_dir, "failed", args)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
