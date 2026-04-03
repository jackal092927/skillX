from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..validators import ValidationResult

VALID_ROUND_DECISIONS = ("continue", "stop", "keep_current", "select_final")
VALID_OPERATION_STATUSES = ("planned", "executed", "applied", "dropped")


def _mapping(data: Any, kind: str) -> tuple[dict[str, Any] | None, ValidationResult | None]:
    if hasattr(data, "to_dict"):
        payload = data.to_dict()
    else:
        payload = data
    if not isinstance(payload, Mapping):
        return None, ValidationResult(False, (f"{kind} must be a mapping or data object",))
    return dict(payload), None


def _ensure_string(name: str, value: Any, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{name} must be a non-empty string")


def _ensure_optional_string(name: str, value: Any, errors: list[str]) -> None:
    if value is None:
        return
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{name} must be a non-empty string or None")


def _ensure_non_negative_int(name: str, value: Any, errors: list[str]) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        errors.append(f"{name} must be a non-negative integer")


def _ensure_boolean(name: str, value: Any, errors: list[str]) -> None:
    if not isinstance(value, bool):
        errors.append(f"{name} must be a boolean")


def _ensure_nonempty_sequence_of_strings(name: str, value: Any, errors: list[str]) -> None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) == 0:
        errors.append(f"{name} must be a non-empty sequence")
        return
    for item in value:
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{name} must contain only non-empty strings")
            return


def _ensure_sequence_of_strings(name: str, value: Any, errors: list[str]) -> None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        errors.append(f"{name} must be a sequence")
        return
    for item in value:
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{name} must contain only non-empty strings")
            return


def _ensure_sequence_of_relative_paths(name: str, value: Any, errors: list[str]) -> None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) == 0:
        errors.append(f"{name} must be a non-empty sequence")
        return
    for item in value:
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{name} must contain only non-empty strings")
            return
        path = Path(item)
        if path.is_absolute():
            errors.append(f"{name} must contain only relative paths")
            return
        if ".." in path.parts:
            errors.append(f"{name} must not escape the skillpack root")
            return


@dataclass(slots=True)
class SessionEvidenceArtifact:
    task_id: str
    round_index: int
    role: str
    model_name: str
    source_log_paths: list[str]
    dominant_failure_pattern: str
    wasted_loop_signals: list[str] = field(default_factory=list)
    tool_misuse_signals: list[str] = field(default_factory=list)
    critical_turns: list[str] = field(default_factory=list)
    skill_misguidance_signals: list[str] = field(default_factory=list)
    recommended_edit_targets: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    observed_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> SessionEvidenceArtifact:
        return cls(
            task_id=str(data["task_id"]),
            round_index=int(data["round_index"]),
            role=str(data["role"]),
            model_name=str(data["model_name"]),
            source_log_paths=list(data["source_log_paths"]),
            dominant_failure_pattern=str(data["dominant_failure_pattern"]),
            wasted_loop_signals=list(data.get("wasted_loop_signals", [])),
            tool_misuse_signals=list(data.get("tool_misuse_signals", [])),
            critical_turns=list(data.get("critical_turns", [])),
            skill_misguidance_signals=list(data.get("skill_misguidance_signals", [])),
            recommended_edit_targets=list(data.get("recommended_edit_targets", [])),
            evidence_refs=list(data.get("evidence_refs", [])),
            observed_at=str(data["observed_at"]),
        )


@dataclass(slots=True)
class NextSkillpackManifest:
    task_id: str
    round_index: int
    role: str
    model_name: str
    skillpack_dir: str
    skill_files: list[str]
    prompt_invariant: bool
    derived_from_round: int
    bundle_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> NextSkillpackManifest:
        return cls(
            task_id=str(data["task_id"]),
            round_index=int(data["round_index"]),
            role=str(data["role"]),
            model_name=str(data["model_name"]),
            skillpack_dir=str(data["skillpack_dir"]),
            skill_files=list(data["skill_files"]),
            prompt_invariant=bool(data["prompt_invariant"]),
            derived_from_round=int(data["derived_from_round"]),
            bundle_path=data.get("bundle_path"),
        )


@dataclass(slots=True)
class RefinePlanArtifact:
    task_id: str
    round_index: int
    role: str
    model_name: str
    summary: str
    atomic_operations: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> RefinePlanArtifact:
        return cls(
            task_id=str(data["task_id"]),
            round_index=int(data["round_index"]),
            role=str(data["role"]),
            model_name=str(data["model_name"]),
            summary=str(data["summary"]),
            atomic_operations=[dict(item) for item in data.get("atomic_operations", [])],
        )


@dataclass(slots=True)
class RoundDecisionArtifact:
    task_id: str
    round_index: int
    role: str
    model_name: str
    decision: str
    reason: str
    next_round_index: int | None = None
    next_skillpack_dir: str | None = None
    selected_candidate_label: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> RoundDecisionArtifact:
        return cls(
            task_id=str(data["task_id"]),
            round_index=int(data["round_index"]),
            role=str(data["role"]),
            model_name=str(data["model_name"]),
            decision=str(data["decision"]),
            reason=str(data["reason"]),
            next_round_index=data.get("next_round_index"),
            next_skillpack_dir=data.get("next_skillpack_dir"),
            selected_candidate_label=data.get("selected_candidate_label"),
        )


@dataclass(slots=True)
class OrchestratorEvent:
    task_id: str
    round_index: int
    role: str
    event_type: str
    status: str
    timestamp: str
    artifact_ref: str | None = None
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> OrchestratorEvent:
        return cls(
            task_id=str(data["task_id"]),
            round_index=int(data["round_index"]),
            role=str(data["role"]),
            event_type=str(data["event_type"]),
            status=str(data["status"]),
            timestamp=str(data["timestamp"]),
            artifact_ref=data.get("artifact_ref"),
            note=data.get("note"),
        )


def validate_session_evidence_artifact(data: Any) -> ValidationResult:
    payload, error = _mapping(data, "session evidence artifact")
    if error is not None:
        return error
    errors: list[str] = []
    _ensure_string("task_id", payload.get("task_id"), errors)
    _ensure_non_negative_int("round_index", payload.get("round_index"), errors)
    _ensure_string("role", payload.get("role"), errors)
    _ensure_string("model_name", payload.get("model_name"), errors)
    _ensure_nonempty_sequence_of_strings("source_log_paths", payload.get("source_log_paths"), errors)
    _ensure_string("dominant_failure_pattern", payload.get("dominant_failure_pattern"), errors)
    _ensure_sequence_of_strings("evidence_refs", payload.get("evidence_refs", []), errors)
    _ensure_string("observed_at", payload.get("observed_at"), errors)
    for field_name in (
        "wasted_loop_signals",
        "tool_misuse_signals",
        "critical_turns",
        "skill_misguidance_signals",
        "recommended_edit_targets",
    ):
        _ensure_sequence_of_strings(field_name, payload.get(field_name, []), errors)
    return ValidationResult(not errors, tuple(errors))


def validate_next_skillpack_manifest(data: Any) -> ValidationResult:
    payload, error = _mapping(data, "next skillpack manifest")
    if error is not None:
        return error
    errors: list[str] = []
    _ensure_string("task_id", payload.get("task_id"), errors)
    _ensure_non_negative_int("round_index", payload.get("round_index"), errors)
    _ensure_string("role", payload.get("role"), errors)
    _ensure_string("model_name", payload.get("model_name"), errors)
    _ensure_string("skillpack_dir", payload.get("skillpack_dir"), errors)
    _ensure_sequence_of_relative_paths("skill_files", payload.get("skill_files"), errors)
    _ensure_boolean("prompt_invariant", payload.get("prompt_invariant"), errors)
    _ensure_non_negative_int("derived_from_round", payload.get("derived_from_round"), errors)
    _ensure_optional_string("bundle_path", payload.get("bundle_path"), errors)
    return ValidationResult(not errors, tuple(errors))


def validate_refine_plan_artifact(data: Any) -> ValidationResult:
    payload, error = _mapping(data, "refine plan artifact")
    if error is not None:
        return error
    errors: list[str] = []
    _ensure_string("task_id", payload.get("task_id"), errors)
    _ensure_non_negative_int("round_index", payload.get("round_index"), errors)
    _ensure_string("role", payload.get("role"), errors)
    _ensure_string("model_name", payload.get("model_name"), errors)
    _ensure_string("summary", payload.get("summary"), errors)
    operations = payload.get("atomic_operations")
    if not isinstance(operations, Sequence) or isinstance(operations, (str, bytes)):
        errors.append("atomic_operations must be a sequence")
    else:
        for operation in operations:
            if not isinstance(operation, Mapping):
                errors.append("atomic_operations must contain only mappings")
                break
            op = dict(operation)
            for field_name in ("op_id", "action_type", "target_id", "rationale", "expected_effect", "risk"):
                _ensure_string(f"atomic_operations.{field_name}", op.get(field_name), errors)
            if op.get("status") not in VALID_OPERATION_STATUSES:
                errors.append(f"atomic_operations.status must be one of {VALID_OPERATION_STATUSES}")
    return ValidationResult(not errors, tuple(errors))


def validate_round_decision_artifact(data: Any) -> ValidationResult:
    payload, error = _mapping(data, "round decision artifact")
    if error is not None:
        return error
    errors: list[str] = []
    decision = payload.get("decision")
    if decision not in VALID_ROUND_DECISIONS:
        errors.append(f"decision must be one of {VALID_ROUND_DECISIONS}")
    _ensure_string("task_id", payload.get("task_id"), errors)
    _ensure_non_negative_int("round_index", payload.get("round_index"), errors)
    _ensure_string("role", payload.get("role"), errors)
    _ensure_string("model_name", payload.get("model_name"), errors)
    _ensure_string("reason", payload.get("reason"), errors)
    next_round_index = payload.get("next_round_index")
    if next_round_index is not None:
        _ensure_non_negative_int("next_round_index", next_round_index, errors)
    _ensure_optional_string("next_skillpack_dir", payload.get("next_skillpack_dir"), errors)
    _ensure_optional_string("selected_candidate_label", payload.get("selected_candidate_label"), errors)
    if decision == "continue":
        if next_round_index is None:
            errors.append("continue decision requires next_round_index")
        if payload.get("next_skillpack_dir") is None:
            errors.append("continue decision requires next_skillpack_dir")
    else:
        if next_round_index is not None:
            errors.append(f"{decision} decision must not include next_round_index")
        if payload.get("next_skillpack_dir") is not None:
            errors.append(f"{decision} decision must not include next_skillpack_dir")
    if decision == "select_final" and payload.get("selected_candidate_label") is None:
        errors.append("select_final decision requires selected_candidate_label")
    return ValidationResult(not errors, tuple(errors))


def validate_orchestrator_event(data: Any) -> ValidationResult:
    payload, error = _mapping(data, "orchestrator event")
    if error is not None:
        return error
    errors: list[str] = []
    _ensure_string("task_id", payload.get("task_id"), errors)
    _ensure_non_negative_int("round_index", payload.get("round_index"), errors)
    _ensure_string("role", payload.get("role"), errors)
    _ensure_string("event_type", payload.get("event_type"), errors)
    _ensure_string("status", payload.get("status"), errors)
    _ensure_string("timestamp", payload.get("timestamp"), errors)
    _ensure_optional_string("artifact_ref", payload.get("artifact_ref"), errors)
    _ensure_optional_string("note", payload.get("note"), errors)
    return ValidationResult(not errors, tuple(errors))


def ensure_valid_session_evidence_artifact(data: Any) -> SessionEvidenceArtifact:
    result = validate_session_evidence_artifact(data)
    if not result.ok:
        raise ValueError("; ".join(result.errors))
    if isinstance(data, SessionEvidenceArtifact):
        return data
    return SessionEvidenceArtifact.from_dict(data)


def ensure_valid_next_skillpack_manifest(data: Any) -> NextSkillpackManifest:
    result = validate_next_skillpack_manifest(data)
    if not result.ok:
        raise ValueError("; ".join(result.errors))
    if isinstance(data, NextSkillpackManifest):
        return data
    return NextSkillpackManifest.from_dict(data)


def ensure_valid_refine_plan_artifact(data: Any) -> RefinePlanArtifact:
    result = validate_refine_plan_artifact(data)
    if not result.ok:
        raise ValueError("; ".join(result.errors))
    if isinstance(data, RefinePlanArtifact):
        return data
    return RefinePlanArtifact.from_dict(data)


def ensure_valid_round_decision_artifact(data: Any) -> RoundDecisionArtifact:
    result = validate_round_decision_artifact(data)
    if not result.ok:
        raise ValueError("; ".join(result.errors))
    if isinstance(data, RoundDecisionArtifact):
        return data
    return RoundDecisionArtifact.from_dict(data)


def ensure_valid_orchestrator_event(data: Any) -> OrchestratorEvent:
    result = validate_orchestrator_event(data)
    if not result.ok:
        raise ValueError("; ".join(result.errors))
    if isinstance(data, OrchestratorEvent):
        return data
    return OrchestratorEvent.from_dict(data)


__all__ = [
    "NextSkillpackManifest",
    "OrchestratorEvent",
    "RefinePlanArtifact",
    "RoundDecisionArtifact",
    "SessionEvidenceArtifact",
    "VALID_OPERATION_STATUSES",
    "VALID_ROUND_DECISIONS",
    "ensure_valid_next_skillpack_manifest",
    "ensure_valid_refine_plan_artifact",
    "ensure_valid_orchestrator_event",
    "ensure_valid_round_decision_artifact",
    "ensure_valid_session_evidence_artifact",
    "validate_next_skillpack_manifest",
    "validate_refine_plan_artifact",
    "validate_orchestrator_event",
    "validate_round_decision_artifact",
    "validate_session_evidence_artifact",
]
