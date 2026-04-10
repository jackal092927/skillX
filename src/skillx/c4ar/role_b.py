from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from .playbook_agent_runner import ensure_playbook_path, run_playbook_agent
from .agent_schemas import RoleBFinalResponse
from .role_b_artifacts import (
    canonicalize_role_b_artifacts,
    load_and_canonicalize_role_b_artifact_files,
)
from .contracts import (
    NextSkillpackManifest,
    RefinePlanArtifact,
    RoundDecisionArtifact,
    SessionEvidenceArtifact,
    ensure_valid_session_evidence_artifact,
)
from ..io_utils import ensure_dir, read_json, write_json


@dataclass(frozen=True, slots=True)
class RoleBInputs:
    task_id: str
    round_index: int
    verifier_summary_path: str
    session_evidence_path: str
    current_skillpack_dir: str
    output_dir: str
    prior_round_summary_path: str | None = None
    current_bundle_path: str | None = None


@dataclass(frozen=True, slots=True)
class RoleBConfig:
    model_name: str = "gpt-5.4"
    role_name: str = "role_b"
    playbook_path: str | None = None
    timeout_sec: float = 1200.0
    max_attempts: int = 3
    retry_backoff_sec: float = 5.0


@dataclass(frozen=True, slots=True)
class RoleBOutputs:
    refine_plan_json_path: str
    refine_plan_markdown_path: str
    next_skillpack_manifest_json_path: str
    round_decision_json_path: str
    next_skillpack_dir: str
    refine_plan: RefinePlanArtifact
    next_skillpack_manifest: NextSkillpackManifest
    round_decision: RoundDecisionArtifact


RoleBModelRunner = Callable[
    [RoleBInputs, RoleBConfig, Path],
    Mapping[str, object],
]


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_required_file(path_str: str, label: str) -> Path:
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"missing {label}: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"{label} is not a file: {path}")
    return path


def _validate_optional_file(path_str: str | None, label: str) -> Path | None:
    if path_str is None:
        return None
    return _validate_required_file(path_str, label)


def _validate_skillpack_dir(path_str: str) -> Path:
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"missing current skillpack directory: {path}")
    if not path.is_dir():
        raise FileNotFoundError(f"current skillpack path is not a directory: {path}")
    return path


def _collect_skill_files(skillpack_dir: Path) -> list[str]:
    files = sorted(
        str(path.relative_to(skillpack_dir))
        for path in skillpack_dir.rglob("SKILL.md")
        if path.is_file()
    )
    if not files:
        raise FileNotFoundError(f"no SKILL.md files found under next skillpack: {skillpack_dir}")
    return files


def _copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _default_model_runner(inputs: RoleBInputs, config: RoleBConfig, output_dir: Path) -> Mapping[str, object]:
    playbook_path = ensure_playbook_path(config.playbook_path, role_name=config.role_name)
    verifier_summary = read_json(Path(inputs.verifier_summary_path))
    session_evidence = ensure_valid_session_evidence_artifact(read_json(Path(inputs.session_evidence_path)))
    next_skillpack_dir = output_dir / "next_skillpack"
    copied_bundle = output_dir / "next_skillpack_bundle.yaml"
    bundle_path = str(copied_bundle) if inputs.current_bundle_path is not None else None

    def stage_next_skillpack(_attempt_index: int) -> None:
        _copy_tree(Path(inputs.current_skillpack_dir), next_skillpack_dir)
        if inputs.current_bundle_path is not None:
            shutil.copy2(inputs.current_bundle_path, copied_bundle)
        elif copied_bundle.exists():
            copied_bundle.unlink()

    stage_next_skillpack(1)

    packet = {
        "task_id": inputs.task_id,
        "round_index": inputs.round_index,
        "verifier_summary_path": inputs.verifier_summary_path,
        "verifier_summary": verifier_summary,
        "session_evidence_path": inputs.session_evidence_path,
        "session_evidence": session_evidence.to_dict(),
        "current_skillpack_dir": inputs.current_skillpack_dir,
        "staged_next_skillpack_dir": str(next_skillpack_dir),
        "staged_bundle_path": bundle_path,
        "prior_round_summary_path": inputs.prior_round_summary_path,
        "task_prompt_invariant": True,
        "edit_policy": {
            "default_write_budget": 3,
            "prefer_delete_and_merge": True,
            "allowed_high_risk_escape_hatch": "rewrite_section_or_skill_only_if_local_ops_are_insufficient",
        },
        "generated_at": _timestamp(),
    }
    packet_json_path = output_dir / "research_packet.json"
    packet_md_path = output_dir / "research_packet.md"
    write_json(packet_json_path, packet)
    edit_target_lines = [f"- {value}" for value in session_evidence.recommended_edit_targets] or ["- none"]
    packet_md_path.write_text(
        "\n".join(
            [
                "# Research Packet",
                "",
                f"- task_id: `{inputs.task_id}`",
                f"- round_index: `{inputs.round_index}`",
                f"- reward: `{verifier_summary.get('reward', 'unknown')}`",
                f"- failed_tests: `{verifier_summary.get('failed_tests', 'unknown')}`",
                f"- dominant_failure_pattern: {session_evidence.dominant_failure_pattern}",
                f"- staged_next_skillpack_dir: `{next_skillpack_dir}`",
                f"- staged_bundle_path: `{bundle_path or 'none'}`",
                "",
                "## Recommended Edit Targets",
                "",
                *edit_target_lines,
            ]
        )
        + "\n"
    )

    refine_plan_json_path = output_dir / "refine_plan.json"
    refine_plan_markdown_path = output_dir / "refine_plan.md"
    next_manifest_json_path = output_dir / "next_skillpack_manifest.json"
    round_decision_json_path = output_dir / "round_decision.json"
    validator_script_path = (
        Path(__file__).resolve().parents[3]
        / "scripts"
        / "validate_c4ar_role_b_outputs.py"
    )
    final_schema = RoleBFinalResponse.model_json_schema()
    prompt = "\n".join(
        [
            f"You are {config.role_name} for the SkillX C4AR loop.",
            f"First read the playbook at: {playbook_path}",
            f"Then read the research packet JSON at: {packet_json_path}",
            f"Also read the research packet markdown at: {packet_md_path}",
            f"Edit the staged next skillpack in place at: {next_skillpack_dir}",
            "The task prompt is invariant across rounds. Do not modify or reinterpret it.",
            "You must perform three things in order: diagnosis, atomic refine plan, then actual skillpack rewrite.",
            "Write these files exactly:",
            f"- {refine_plan_json_path}",
            f"- {refine_plan_markdown_path}",
            f"- {next_manifest_json_path}",
            f"- {round_decision_json_path}",
            "After writing the JSON artifacts, run the validator script below and keep fixing the files until it exits 0:",
            (
                "./.venv-swebench/bin/python "
                f"{validator_script_path} "
                f"--refine-plan {refine_plan_json_path} "
                f"--next-skillpack-manifest {next_manifest_json_path} "
                f"--round-decision {round_decision_json_path} "
                f"--task-id {inputs.task_id} "
                f"--round-index {inputs.round_index} "
                f"--role-name {config.role_name} "
                "--rewrite"
            ),
            "The validator prints structured JSON. If it reports errors, repair the artifacts and rerun it.",
            "The refine plan must use bounded atomic operations. Prefer delete and merge when redundancy or over-guidance is present.",
            "The next skillpack manifest must point at the staged next skillpack and preserve prompt_invariant=true.",
            "The round decision should normally be continue unless you have a strong reason to stop or keep_current.",
            "In atomic_operations.status, use only these canonical values: planned, executed, applied, dropped.",
            "If an edit already landed in staged next_skillpack, use applied.",
            "In the final response, return JSON matching the provided schema and point to the files you wrote only after the validator succeeds.",
        ]
    )
    run_playbook_agent(
        role_name=config.role_name,
        model_name=config.model_name,
        playbook_path=playbook_path,
        output_dir=output_dir,
        prompt=prompt,
        final_response_schema=final_schema,
        expected_output_paths=[
            refine_plan_json_path,
            refine_plan_markdown_path,
            next_manifest_json_path,
            round_decision_json_path,
        ],
        timeout_sec=config.timeout_sec,
        max_attempts=config.max_attempts,
        retry_backoff_sec=config.retry_backoff_sec,
        prepare_attempt=stage_next_skillpack,
    )
    return {
        "refine_plan_json_path": str(refine_plan_json_path),
        "refine_plan_markdown_path": str(refine_plan_markdown_path),
        "next_skillpack_manifest_json_path": str(next_manifest_json_path),
        "round_decision_json_path": str(round_decision_json_path),
        "next_skillpack_dir": str(next_skillpack_dir),
    }


def _render_refine_plan_markdown(
    refine_plan: RefinePlanArtifact,
    *,
    session_evidence: SessionEvidenceArtifact,
    verifier_summary: Mapping[str, Any],
) -> str:
    lines = [
        "# Refine Plan",
        "",
        f"- task_id: `{refine_plan.task_id}`",
        f"- round_index: `{refine_plan.round_index}`",
        f"- role: `{refine_plan.role}`",
        f"- model_name: `{refine_plan.model_name}`",
        f"- summary: {refine_plan.summary}",
        f"- dominant_failure_pattern: {session_evidence.dominant_failure_pattern}",
        f"- verifier_reward: `{verifier_summary.get('reward', 'unknown')}`",
        f"- failed_tests: `{verifier_summary.get('failed_tests', 'unknown')}`",
        "",
        "## Atomic Operations",
        "",
    ]
    for operation in refine_plan.atomic_operations:
        lines.extend(
            [
                f"- `{operation['op_id']}` `{operation['action_type']}` -> `{operation['target_id']}`",
                f"  rationale: {operation['rationale']}",
                f"  expected_effect: {operation['expected_effect']}",
                f"  risk: {operation['risk']}",
                f"  status: `{operation['status']}`",
            ]
        )
    return "\n".join(lines)


def _validate_next_skillpack_manifest_contents(manifest: NextSkillpackManifest) -> None:
    skillpack_dir = Path(manifest.skillpack_dir)
    if not skillpack_dir.exists():
        raise FileNotFoundError(f"next skillpack directory missing: {skillpack_dir}")
    for relative_path in manifest.skill_files:
        skill_path = skillpack_dir / relative_path
        if not skill_path.exists():
            raise FileNotFoundError(f"listed skill file missing: {skill_path}")
    if manifest.bundle_path is not None and not Path(manifest.bundle_path).exists():
        raise FileNotFoundError(f"listed bundle path missing: {manifest.bundle_path}")


def _validate_output_alignment(
    *,
    inputs: RoleBInputs,
    config: RoleBConfig,
    refine_plan: RefinePlanArtifact,
    next_skillpack_manifest: NextSkillpackManifest,
    round_decision: RoundDecisionArtifact,
) -> None:
    shared_values = (
        ("task_id", inputs.task_id, refine_plan.task_id, next_skillpack_manifest.task_id, round_decision.task_id),
        ("round_index", inputs.round_index, refine_plan.round_index, next_skillpack_manifest.round_index, round_decision.round_index),
        ("role", config.role_name, refine_plan.role, next_skillpack_manifest.role, round_decision.role),
    )
    for field_name, expected, refine_value, manifest_value, decision_value in shared_values:
        if not (refine_value == manifest_value == decision_value == expected):
            raise ValueError(f"{field_name} mismatch across Role B outputs")
    if not (
        refine_plan.model_name
        == next_skillpack_manifest.model_name
        == round_decision.model_name
    ):
        raise ValueError("model_name mismatch across Role B outputs")
    if next_skillpack_manifest.prompt_invariant is not True:
        raise ValueError("next skillpack manifest must preserve prompt_invariant=True")
    if round_decision.decision == "continue":
        if round_decision.next_round_index != inputs.round_index + 1:
            raise ValueError("continue decision must advance exactly one round")
        if round_decision.next_skillpack_dir is None:
            raise ValueError("continue decision must include next_skillpack_dir")
        if Path(round_decision.next_skillpack_dir) != Path(next_skillpack_manifest.skillpack_dir):
            raise ValueError("round decision next_skillpack_dir must match next skillpack manifest")


def run_role_b(
    inputs: RoleBInputs,
    *,
    config: RoleBConfig | None = None,
    model_runner: RoleBModelRunner | None = None,
) -> RoleBOutputs:
    config = config or RoleBConfig()
    verifier_summary_path = _validate_required_file(inputs.verifier_summary_path, "verifier summary")
    session_evidence_path = _validate_required_file(inputs.session_evidence_path, "session evidence")
    current_skillpack_dir = _validate_skillpack_dir(inputs.current_skillpack_dir)
    _validate_optional_file(inputs.prior_round_summary_path, "prior round summary")
    _validate_optional_file(inputs.current_bundle_path, "current bundle")

    output_dir = ensure_dir(Path(inputs.output_dir))
    runner = model_runner or _default_model_runner
    raw_outputs = runner(inputs, config, output_dir)
    if "refine_plan_json_path" in raw_outputs:
        refine_plan_json_path = Path(str(raw_outputs["refine_plan_json_path"]))
        refine_plan_markdown_path = Path(str(raw_outputs["refine_plan_markdown_path"]))
        next_skillpack_manifest_json_path = Path(str(raw_outputs["next_skillpack_manifest_json_path"]))
        round_decision_json_path = Path(str(raw_outputs["round_decision_json_path"]))
        next_skillpack_dir = Path(str(raw_outputs["next_skillpack_dir"]))
        canonical_artifacts = load_and_canonicalize_role_b_artifact_files(
            refine_plan_json_path=refine_plan_json_path,
            next_skillpack_manifest_json_path=next_skillpack_manifest_json_path,
            round_decision_json_path=round_decision_json_path,
            rewrite=True,
        )
        refine_plan = canonical_artifacts.refine_plan
        next_skillpack_manifest = canonical_artifacts.next_skillpack_manifest
        round_decision = canonical_artifacts.round_decision
    else:
        canonical_artifacts = canonicalize_role_b_artifacts(
            refine_plan_payload=raw_outputs["refine_plan"],
            next_skillpack_manifest_payload=raw_outputs["next_skillpack_manifest"],
            round_decision_payload=raw_outputs["round_decision"],
        )
        refine_plan = canonical_artifacts.refine_plan
        next_skillpack_manifest = canonical_artifacts.next_skillpack_manifest
        round_decision = canonical_artifacts.round_decision
        refine_plan_json_path = output_dir / "refine_plan.json"
        refine_plan_markdown_path = output_dir / "refine_plan.md"
        next_skillpack_manifest_json_path = output_dir / "next_skillpack_manifest.json"
        round_decision_json_path = output_dir / "round_decision.json"
        next_skillpack_dir = Path(next_skillpack_manifest.skillpack_dir)

    _validate_next_skillpack_manifest_contents(next_skillpack_manifest)
    _validate_output_alignment(
        inputs=inputs,
        config=config,
        refine_plan=refine_plan,
        next_skillpack_manifest=next_skillpack_manifest,
        round_decision=round_decision,
    )

    verifier_summary = read_json(verifier_summary_path)
    session_evidence = ensure_valid_session_evidence_artifact(read_json(session_evidence_path))

    write_json(refine_plan_json_path, refine_plan.to_dict())
    if not refine_plan_markdown_path.exists():
        refine_plan_markdown_path.write_text(
            _render_refine_plan_markdown(
                refine_plan,
                session_evidence=session_evidence,
                verifier_summary=verifier_summary,
            )
            + "\n"
        )
    write_json(next_skillpack_manifest_json_path, next_skillpack_manifest.to_dict())
    write_json(round_decision_json_path, round_decision.to_dict())

    return RoleBOutputs(
        refine_plan_json_path=str(refine_plan_json_path),
        refine_plan_markdown_path=str(refine_plan_markdown_path),
        next_skillpack_manifest_json_path=str(next_skillpack_manifest_json_path),
        round_decision_json_path=str(round_decision_json_path),
        next_skillpack_dir=str(next_skillpack_dir),
        refine_plan=refine_plan,
        next_skillpack_manifest=next_skillpack_manifest,
        round_decision=round_decision,
    )


__all__ = [
    "RoleBConfig",
    "RoleBInputs",
    "RoleBModelRunner",
    "RoleBOutputs",
    "run_role_b",
]
