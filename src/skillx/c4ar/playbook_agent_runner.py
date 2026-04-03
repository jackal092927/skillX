from __future__ import annotations

import json
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

from ..io_utils import ensure_dir, write_json

ROOT = Path(__file__).resolve().parents[3]

MODEL_NAME_ALIASES = {
    "codex-5.3": "gpt-5.3-codex",
    "gpt-5.4": "gpt-5.4",
}


@dataclass(frozen=True, slots=True)
class PlaybookAgentRunResult:
    command_path: str
    prompt_path: str
    stdout_path: str
    stderr_path: str
    schema_path: str
    last_message_path: str
    metadata_path: str
    final_message: dict[str, Any]


def resolve_cli_model_name(model_name: str) -> str:
    return MODEL_NAME_ALIASES.get(model_name, model_name)


def ensure_playbook_path(playbook_path: str | None, *, role_name: str) -> Path:
    if playbook_path is None or not playbook_path.strip():
        raise ValueError(f"{role_name} requires a playbook_path when no custom model_runner is provided")
    path = Path(playbook_path)
    if not path.exists():
        raise FileNotFoundError(f"missing {role_name} playbook: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"{role_name} playbook is not a file: {path}")
    return path


def run_playbook_agent(
    *,
    role_name: str,
    model_name: str,
    playbook_path: Path,
    output_dir: Path,
    prompt: str,
    final_response_schema: dict[str, Any],
    expected_output_paths: Sequence[Path],
    subprocess_runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> PlaybookAgentRunResult:
    agent_dir = ensure_dir(output_dir / "agent_run")
    schema_path = agent_dir / "final_response_schema.json"
    prompt_path = agent_dir / "prompt.txt"
    stdout_path = agent_dir / "stdout.jsonl"
    stderr_path = agent_dir / "stderr.txt"
    command_path = agent_dir / "command.txt"
    last_message_path = agent_dir / "last_message.json"
    metadata_path = agent_dir / "run_metadata.json"

    write_json(schema_path, final_response_schema)
    prompt_path.write_text(prompt + "\n")

    cli_model_name = resolve_cli_model_name(model_name)
    command = [
        "codex",
        "exec",
        "--dangerously-bypass-approvals-and-sandbox",
        "--skip-git-repo-check",
        "--json",
        "--model",
        cli_model_name,
        "--output-schema",
        str(schema_path),
        "--output-last-message",
        str(last_message_path),
        "--",
    ]
    command_path.write_text(" ".join(shlex.quote(part) for part in command) + "\n")

    started = time.time()
    proc = subprocess_runner(
        command,
        cwd=str(ROOT),
        input=prompt,
        text=True,
        capture_output=True,
    )
    duration_sec = time.time() - started

    stdout_path.write_text(proc.stdout)
    stderr_path.write_text(proc.stderr)
    write_json(
        metadata_path,
        {
            "role_name": role_name,
            "model_name": model_name,
            "cli_model_name": cli_model_name,
            "playbook_path": str(playbook_path),
            "returncode": proc.returncode,
            "duration_sec": duration_sec,
            "expected_output_paths": [str(path) for path in expected_output_paths],
        },
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f"{role_name} agent run failed ({proc.returncode}); see {stdout_path} and {stderr_path}"
        )
    if not last_message_path.exists():
        raise RuntimeError(f"{role_name} agent did not write final message: {last_message_path}")
    try:
        final_message = json.loads(last_message_path.read_text())
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{role_name} final message is not valid JSON: {last_message_path}") from exc

    missing = [str(path) for path in expected_output_paths if not path.exists()]
    if missing:
        raise RuntimeError(f"{role_name} agent did not produce expected outputs: {missing}")

    return PlaybookAgentRunResult(
        command_path=str(command_path),
        prompt_path=str(prompt_path),
        stdout_path=str(stdout_path),
        stderr_path=str(stderr_path),
        schema_path=str(schema_path),
        last_message_path=str(last_message_path),
        metadata_path=str(metadata_path),
        final_message=final_message,
    )


__all__ = [
    "PlaybookAgentRunResult",
    "ensure_playbook_path",
    "resolve_cli_model_name",
    "run_playbook_agent",
]
