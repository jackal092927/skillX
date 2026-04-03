from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .contracts import (
    NextSkillpackManifest,
    OrchestratorEvent,
    RoundDecisionArtifact,
    SessionEvidenceArtifact,
    ensure_valid_next_skillpack_manifest,
    ensure_valid_orchestrator_event,
    ensure_valid_round_decision_artifact,
    ensure_valid_session_evidence_artifact,
)
from ..io_utils import ensure_dir, read_json
from .role_a import RoleAConfig, RoleAInputs
from .role_b import RoleBConfig, RoleBInputs


@dataclass(frozen=True, slots=True)
class ExecutorInputs:
    task_id: str
    round_index: int
    task_prompt_path: str
    skillpack_dir: str
    bundle_path: str | None
    output_dir: str


@dataclass(frozen=True, slots=True)
class ExecutorOutputs:
    session_log_path: str
    verifier_summary_path: str
    current_skillpack_dir: str
    current_bundle_path: str | None = None


@dataclass(frozen=True, slots=True)
class OrchestratorInputs:
    task_id: str
    round_index: int
    task_prompt_path: str
    current_skillpack_dir: str
    current_bundle_path: str | None
    round_root_dir: str


@dataclass(frozen=True, slots=True)
class OrchestratorConfig:
    role_name: str = "orchestrator"
    role_a_config: RoleAConfig | None = None
    role_b_config: RoleBConfig | None = None


@dataclass(frozen=True, slots=True)
class OrchestratorOutputs:
    event_log_path: str
    session_evidence: SessionEvidenceArtifact
    next_skillpack_manifest: NextSkillpackManifest
    round_decision: RoundDecisionArtifact


ExecutorRunner = Callable[[ExecutorInputs], ExecutorOutputs]
RoleARunner = Callable[..., Any]
RoleBRunner = Callable[..., Any]


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_event(log_path: Path, event: OrchestratorEvent) -> None:
    ensure_valid_orchestrator_event(event)
    ensure_dir(log_path.parent)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event.to_dict()) + "\n")


def _validate_file(path_str: str, label: str) -> Path:
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"missing {label}: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"{label} is not a file: {path}")
    return path


def _validate_dir(path_str: str, label: str) -> Path:
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"missing {label}: {path}")
    if not path.is_dir():
        raise FileNotFoundError(f"{label} is not a directory: {path}")
    return path


def run_c4ar_round(
    inputs: OrchestratorInputs,
    *,
    config: OrchestratorConfig | None = None,
    executor_runner: ExecutorRunner,
    role_a_runner: RoleARunner,
    role_b_runner: RoleBRunner,
) -> OrchestratorOutputs:
    config = config or OrchestratorConfig()
    round_root_dir = ensure_dir(Path(inputs.round_root_dir))
    event_log_path = round_root_dir / "orchestrator_log.ndjson"
    _validate_dir(inputs.current_skillpack_dir, "current skillpack")

    executor_output_dir = str(ensure_dir(round_root_dir / "executor"))
    role_a_output_dir = str(ensure_dir(round_root_dir / "role_a"))
    role_b_output_dir = str(ensure_dir(round_root_dir / "role_b"))

    _write_event(
        event_log_path,
        OrchestratorEvent(
            task_id=inputs.task_id,
            round_index=inputs.round_index,
            role=config.role_name,
            event_type="round_started",
            status="ok",
            timestamp=_timestamp(),
            artifact_ref=inputs.current_skillpack_dir,
            note="starting sequential C4AR round",
        ),
    )

    executor_outputs = executor_runner(
        ExecutorInputs(
            task_id=inputs.task_id,
            round_index=inputs.round_index,
            task_prompt_path=inputs.task_prompt_path,
            skillpack_dir=inputs.current_skillpack_dir,
            bundle_path=inputs.current_bundle_path,
            output_dir=executor_output_dir,
        )
    )
    _validate_file(executor_outputs.session_log_path, "executor session log")
    _validate_file(executor_outputs.verifier_summary_path, "executor verifier summary")
    _validate_dir(executor_outputs.current_skillpack_dir, "executor current skillpack")
    if executor_outputs.current_bundle_path is not None:
        _validate_file(executor_outputs.current_bundle_path, "executor bundle")
    _write_event(
        event_log_path,
        OrchestratorEvent(
            task_id=inputs.task_id,
            round_index=inputs.round_index,
            role=config.role_name,
            event_type="executor_completed",
            status="ok",
            timestamp=_timestamp(),
            artifact_ref=executor_outputs.verifier_summary_path,
        ),
    )

    role_a_outputs = role_a_runner(
        RoleAInputs(
            task_id=inputs.task_id,
            round_index=inputs.round_index,
            source_log_paths=[executor_outputs.session_log_path],
            output_dir=role_a_output_dir,
        ),
        config=config.role_a_config or RoleAConfig(),
    )
    session_evidence_path = _validate_file(role_a_outputs.json_path, "session evidence")
    _validate_file(role_a_outputs.markdown_path, "session evidence markdown")
    session_evidence = ensure_valid_session_evidence_artifact(read_json(session_evidence_path))
    _write_event(
        event_log_path,
        OrchestratorEvent(
            task_id=inputs.task_id,
            round_index=inputs.round_index,
            role=config.role_name,
            event_type="role_a_completed",
            status="ok",
            timestamp=_timestamp(),
            artifact_ref=str(session_evidence_path),
        ),
    )

    role_b_outputs = role_b_runner(
        RoleBInputs(
            task_id=inputs.task_id,
            round_index=inputs.round_index,
            verifier_summary_path=executor_outputs.verifier_summary_path,
            session_evidence_path=str(session_evidence_path),
            current_skillpack_dir=executor_outputs.current_skillpack_dir,
            prior_round_summary_path=None,
            current_bundle_path=executor_outputs.current_bundle_path,
            output_dir=role_b_output_dir,
        ),
        config=config.role_b_config or RoleBConfig(),
    )
    next_skillpack_manifest_path = _validate_file(
        role_b_outputs.next_skillpack_manifest_json_path,
        "next skillpack manifest",
    )
    round_decision_path = _validate_file(role_b_outputs.round_decision_json_path, "round decision")
    _validate_file(role_b_outputs.refine_plan_json_path, "refine plan")
    _validate_file(role_b_outputs.refine_plan_markdown_path, "refine plan markdown")
    next_skillpack_manifest = ensure_valid_next_skillpack_manifest(read_json(next_skillpack_manifest_path))
    round_decision = ensure_valid_round_decision_artifact(read_json(round_decision_path))
    _validate_dir(role_b_outputs.next_skillpack_dir, "next skillpack")
    _write_event(
        event_log_path,
        OrchestratorEvent(
            task_id=inputs.task_id,
            round_index=inputs.round_index,
            role=config.role_name,
            event_type="role_b_completed",
            status="ok",
            timestamp=_timestamp(),
            artifact_ref=str(round_decision_path),
        ),
    )

    _write_event(
        event_log_path,
        OrchestratorEvent(
            task_id=inputs.task_id,
            round_index=inputs.round_index,
            role=config.role_name,
            event_type="round_decision_loaded",
            status=round_decision.decision,
            timestamp=_timestamp(),
            artifact_ref=str(round_decision_path),
        ),
    )

    return OrchestratorOutputs(
        event_log_path=str(event_log_path),
        session_evidence=session_evidence,
        next_skillpack_manifest=next_skillpack_manifest,
        round_decision=round_decision,
    )


__all__ = [
    "ExecutorInputs",
    "ExecutorOutputs",
    "ExecutorRunner",
    "OrchestratorConfig",
    "OrchestratorInputs",
    "OrchestratorOutputs",
    "RoleARunner",
    "RoleBRunner",
    "run_c4ar_round",
]
