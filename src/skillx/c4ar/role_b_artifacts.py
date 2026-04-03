from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .contracts import (
    NextSkillpackManifest,
    RefinePlanArtifact,
    RoundDecisionArtifact,
    ensure_valid_next_skillpack_manifest,
    ensure_valid_refine_plan_artifact,
    ensure_valid_round_decision_artifact,
)
from ..io_utils import read_json, write_json

OPERATION_STATUS_ALIASES = {
    "completed": "applied",
    "done": "applied",
    "finished": "applied",
}


@dataclass(frozen=True, slots=True)
class CanonicalRoleBArtifacts:
    refine_plan: RefinePlanArtifact
    next_skillpack_manifest: NextSkillpackManifest
    round_decision: RoundDecisionArtifact
    refine_plan_payload: dict[str, object]
    next_skillpack_manifest_payload: dict[str, object]
    round_decision_payload: dict[str, object]


def normalize_refine_plan_payload(payload: Mapping[str, object]) -> dict[str, object]:
    normalized = dict(payload)
    operations_value = normalized.get("atomic_operations")
    if not isinstance(operations_value, list):
        return normalized

    normalized_operations: list[object] = []
    for item in operations_value:
        if not isinstance(item, Mapping):
            normalized_operations.append(item)
            continue
        operation = dict(item)
        status = operation.get("status")
        if isinstance(status, str):
            operation["status"] = OPERATION_STATUS_ALIASES.get(status.strip().lower(), status)
        normalized_operations.append(operation)
    normalized["atomic_operations"] = normalized_operations
    return normalized


def normalize_next_skillpack_manifest_payload(payload: Mapping[str, object]) -> dict[str, object]:
    normalized = dict(payload)
    skillpack_dir_value = normalized.get("skillpack_dir")
    skill_files_value = normalized.get("skill_files")
    if not isinstance(skillpack_dir_value, str) or not isinstance(skill_files_value, list):
        return normalized

    skillpack_dir = Path(skillpack_dir_value)
    normalized_skill_files: list[object] = []
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


def canonicalize_role_b_artifacts(
    *,
    refine_plan_payload: Mapping[str, object],
    next_skillpack_manifest_payload: Mapping[str, object],
    round_decision_payload: Mapping[str, object],
) -> CanonicalRoleBArtifacts:
    canonical_refine_plan_payload = normalize_refine_plan_payload(refine_plan_payload)
    canonical_next_skillpack_manifest_payload = normalize_next_skillpack_manifest_payload(
        next_skillpack_manifest_payload
    )
    canonical_round_decision_payload = dict(round_decision_payload)

    return CanonicalRoleBArtifacts(
        refine_plan=ensure_valid_refine_plan_artifact(canonical_refine_plan_payload),
        next_skillpack_manifest=ensure_valid_next_skillpack_manifest(canonical_next_skillpack_manifest_payload),
        round_decision=ensure_valid_round_decision_artifact(canonical_round_decision_payload),
        refine_plan_payload=canonical_refine_plan_payload,
        next_skillpack_manifest_payload=canonical_next_skillpack_manifest_payload,
        round_decision_payload=canonical_round_decision_payload,
    )


def load_and_canonicalize_role_b_artifact_files(
    *,
    refine_plan_json_path: Path,
    next_skillpack_manifest_json_path: Path,
    round_decision_json_path: Path,
    rewrite: bool = False,
) -> CanonicalRoleBArtifacts:
    artifacts = canonicalize_role_b_artifacts(
        refine_plan_payload=read_json(refine_plan_json_path),
        next_skillpack_manifest_payload=read_json(next_skillpack_manifest_json_path),
        round_decision_payload=read_json(round_decision_json_path),
    )
    if rewrite:
        write_json(refine_plan_json_path, artifacts.refine_plan_payload)
        write_json(next_skillpack_manifest_json_path, artifacts.next_skillpack_manifest_payload)
        write_json(round_decision_json_path, artifacts.round_decision_payload)
    return artifacts


__all__ = [
    "CanonicalRoleBArtifacts",
    "OPERATION_STATUS_ALIASES",
    "canonicalize_role_b_artifacts",
    "load_and_canonicalize_role_b_artifact_files",
    "normalize_next_skillpack_manifest_payload",
    "normalize_refine_plan_payload",
]
