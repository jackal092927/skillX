from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping

from .playbook_agent_runner import ensure_playbook_path, run_playbook_agent
from .agent_schemas import RoleAFinalResponse
from .contracts import (
    SessionEvidenceArtifact,
    ensure_valid_session_evidence_artifact,
)
from ..io_utils import ensure_dir, read_json, write_json
from ..session_evidence import distill_session_logs


@dataclass(frozen=True, slots=True)
class RoleAInputs:
    task_id: str
    round_index: int
    source_log_paths: list[str]
    output_dir: str


@dataclass(frozen=True, slots=True)
class RoleAConfig:
    model_name: str = "codex-5.3"
    role_name: str = "role_a"
    playbook_path: str | None = None
    timeout_sec: float = 1200.0
    max_attempts: int = 3
    retry_backoff_sec: float = 5.0


@dataclass(frozen=True, slots=True)
class RoleAOutputs:
    json_path: str
    markdown_path: str
    artifact: SessionEvidenceArtifact


RoleAModelRunner = Callable[[RoleAInputs, RoleAConfig], SessionEvidenceArtifact | Mapping[str, object]]


def _validate_source_logs(source_log_paths: list[str]) -> list[Path]:
    resolved: list[Path] = []
    for raw_path in source_log_paths:
        path = Path(raw_path)
        if not path.exists():
            raise FileNotFoundError(f"missing session log: {path}")
        if not path.is_file():
            raise FileNotFoundError(f"session log is not a file: {path}")
        resolved.append(path)
    return resolved


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_session_packet(inputs: RoleAInputs, source_logs: list[Path]) -> tuple[dict[str, object], str]:
    evidence = distill_session_logs(source_logs)
    critical_slices: list[dict[str, str]] = []
    for log_path in source_logs:
        for line_no, raw_line in enumerate(log_path.read_text().splitlines(), start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            lowered = stripped.lower()
            if not any(token in lowered for token in ("timeout", "error", "failed", "verifier", "missing", "tool", "read_file", "edit", "write")):
                continue
            critical_slices.append(
                {
                    "ref": f"{log_path}:{line_no}",
                    "text": stripped[:320],
                }
            )
            if len(critical_slices) >= 24:
                break
        if len(critical_slices) >= 24:
            break

    packet = {
        "task_id": inputs.task_id,
        "round_index": inputs.round_index,
        "source_log_paths": [str(path) for path in source_logs],
        "heuristic_summary": evidence.to_dict(),
        "critical_slices": critical_slices,
        "packet_policy": {
            "raw_logs_forwarded": False,
            "max_packet_tokens_target": 100000,
            "preferred_packet_tokens_target": 40000,
            "instruction": "Use this packet as the primary source. Do not expand to full raw session logs unless absolutely necessary.",
        },
        "generated_at": _timestamp(),
    }
    critical_slice_lines = [f"- `{item['ref']}` {item['text']}" for item in critical_slices] or ["- none"]
    markdown = "\n".join(
        [
            "# Session Packet",
            "",
            f"- task_id: `{inputs.task_id}`",
            f"- round_index: `{inputs.round_index}`",
            f"- dominant_failure_pattern: {evidence.dominant_failure_pattern}",
            f"- source_log_paths: `{', '.join(str(path) for path in source_logs)}`",
            "",
            "## Critical Slices",
            "",
            *critical_slice_lines,
        ]
    )
    return packet, markdown


def _default_model_runner(inputs: RoleAInputs, config: RoleAConfig) -> SessionEvidenceArtifact:
    playbook_path = ensure_playbook_path(config.playbook_path, role_name=config.role_name)
    output_dir = ensure_dir(Path(inputs.output_dir))
    source_logs = [Path(path) for path in inputs.source_log_paths]
    packet, packet_markdown = _build_session_packet(inputs, source_logs)
    session_packet_json_path = output_dir / "session_packet.json"
    session_packet_markdown_path = output_dir / "session_packet.md"
    write_json(session_packet_json_path, packet)
    session_packet_markdown_path.write_text(packet_markdown + "\n")

    session_evidence_json_path = output_dir / "session_evidence.json"
    session_evidence_markdown_path = output_dir / "session_evidence.md"
    final_schema = RoleAFinalResponse.model_json_schema()
    prompt = "\n".join(
        [
            f"You are {config.role_name} for the SkillX C4AR loop.",
            f"First read the playbook at: {playbook_path}",
            f"Then read the preprocessed session packet JSON at: {session_packet_json_path}",
            f"Also read the packet markdown at: {session_packet_markdown_path}",
            "Do not consume the full raw session logs unless the packet is clearly insufficient.",
            "Your job is to produce a high-signal session-derived evidence artifact for the research brain.",
            "Write these files exactly:",
            f"- {session_evidence_json_path}",
            f"- {session_evidence_markdown_path}",
            "The JSON artifact must match the session evidence contract fields exactly.",
            "Keep recommended_edit_targets concise and actionable.",
            "Keep evidence_refs tied to concrete packet refs or source log refs.",
            "In the final response, return JSON matching the provided schema and point to the two files you wrote.",
        ]
    )
    run_playbook_agent(
        role_name=config.role_name,
        model_name=config.model_name,
        playbook_path=playbook_path,
        output_dir=output_dir,
        prompt=prompt,
        final_response_schema=final_schema,
        expected_output_paths=[session_evidence_json_path, session_evidence_markdown_path],
        timeout_sec=config.timeout_sec,
        max_attempts=config.max_attempts,
        retry_backoff_sec=config.retry_backoff_sec,
    )
    artifact = ensure_valid_session_evidence_artifact(read_json(session_evidence_json_path))
    return {
        "artifact": artifact.to_dict(),
        "json_path": str(session_evidence_json_path),
        "markdown_path": str(session_evidence_markdown_path),
    }


def _render_session_evidence_markdown(artifact: SessionEvidenceArtifact) -> str:
    lines = [
        "# Session-Derived Evidence",
        "",
        f"- task_id: `{artifact.task_id}`",
        f"- round_index: `{artifact.round_index}`",
        f"- role: `{artifact.role}`",
        f"- model_name: `{artifact.model_name}`",
        f"- source_log_paths: `{', '.join(artifact.source_log_paths)}`",
        f"- dominant_failure_pattern: {artifact.dominant_failure_pattern}",
    ]
    sections = (
        ("Wasted Loop Signals", artifact.wasted_loop_signals),
        ("Tool Misuse Signals", artifact.tool_misuse_signals),
        ("Critical Turns", artifact.critical_turns),
        ("Skill Misguidance Signals", artifact.skill_misguidance_signals),
        ("Recommended Edit Targets", artifact.recommended_edit_targets),
        ("Evidence Refs", artifact.evidence_refs),
    )
    for title, values in sections:
        lines.extend(["", f"## {title}", ""])
        if values:
            lines.extend(f"- {value}" for value in values)
        else:
            lines.append("- none")
    lines.extend(["", f"- observed_at: `{artifact.observed_at}`"])
    return "\n".join(lines)


def run_role_a(
    inputs: RoleAInputs,
    *,
    config: RoleAConfig | None = None,
    model_runner: RoleAModelRunner | None = None,
) -> RoleAOutputs:
    config = config or RoleAConfig()
    _validate_source_logs(inputs.source_log_paths)
    output_dir = ensure_dir(Path(inputs.output_dir))

    runner = model_runner or _default_model_runner
    raw_outputs = runner(inputs, config)

    json_path = output_dir / "session_evidence.json"
    markdown_path = output_dir / "session_evidence.md"
    if isinstance(raw_outputs, Mapping) and ("json_path" in raw_outputs or "markdown_path" in raw_outputs):
        if "artifact" in raw_outputs:
            artifact = ensure_valid_session_evidence_artifact(raw_outputs["artifact"])
        else:
            artifact = ensure_valid_session_evidence_artifact(read_json(Path(str(raw_outputs["json_path"]))))
        if "json_path" in raw_outputs:
            json_path = Path(str(raw_outputs["json_path"]))
        if "markdown_path" in raw_outputs:
            markdown_path = Path(str(raw_outputs["markdown_path"]))
        if not json_path.exists():
            write_json(json_path, artifact.to_dict())
        if not markdown_path.exists():
            markdown_path.write_text(_render_session_evidence_markdown(artifact) + "\n")
    else:
        artifact = ensure_valid_session_evidence_artifact(raw_outputs)
        write_json(json_path, artifact.to_dict())
        markdown_path.write_text(_render_session_evidence_markdown(artifact) + "\n")

    return RoleAOutputs(
        json_path=str(json_path),
        markdown_path=str(markdown_path),
        artifact=artifact,
    )


__all__ = [
    "RoleAConfig",
    "RoleAInputs",
    "RoleAModelRunner",
    "RoleAOutputs",
    "run_role_a",
]
