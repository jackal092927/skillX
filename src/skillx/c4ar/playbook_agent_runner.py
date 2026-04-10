from __future__ import annotations

import json
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

from ..io_utils import ensure_dir, write_json
from ..model_routing import resolve_cli_model_name, resolve_playbook_cli_name

ROOT = Path(__file__).resolve().parents[3]


class PlaybookAgentError(RuntimeError):
    """Base class for playbook-driven role agent failures."""


class PlaybookAgentTimeoutError(PlaybookAgentError):
    """Raised when the underlying CLI command times out."""


class PlaybookAgentExecutionError(PlaybookAgentError):
    """Raised when the CLI command exits non-zero."""


class PlaybookAgentOutputContractError(PlaybookAgentError):
    """Raised when the CLI command succeeds but does not write valid outputs."""


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


def ensure_playbook_path(playbook_path: str | None, *, role_name: str) -> Path:
    if playbook_path is None or not playbook_path.strip():
        raise ValueError(f"{role_name} requires a playbook_path when no custom model_runner is provided")
    path = Path(playbook_path)
    if not path.exists():
        raise FileNotFoundError(f"missing {role_name} playbook: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"{role_name} playbook is not a file: {path}")
    return path


def _coerce_output_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _clear_stale_attempt_outputs(paths: Sequence[Path]) -> None:
    for path in paths:
        if path.exists():
            if path.is_dir():
                raise RuntimeError(f"refusing to clear directory output path from playbook runner: {path}")
            path.unlink()


def run_playbook_agent(
    *,
    role_name: str,
    model_name: str,
    playbook_path: Path,
    output_dir: Path,
    prompt: str,
    final_response_schema: dict[str, Any],
    expected_output_paths: Sequence[Path],
    timeout_sec: float | None = None,
    max_attempts: int = 1,
    retry_backoff_sec: float = 0.0,
    prepare_attempt: Callable[[int], None] | None = None,
    subprocess_runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> PlaybookAgentRunResult:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
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

    cli_name = resolve_playbook_cli_name(model_name)
    cli_model_name = resolve_cli_model_name(model_name)
    if cli_name == "claude":
        command = [
            "claude",
            "--print",
            "--dangerously-skip-permissions",
            "--output-format",
            "json",
            "--model",
            cli_model_name,
            "--json-schema",
            json.dumps(final_response_schema, separators=(",", ":")),
        ]
    else:
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

    attempts: list[dict[str, Any]] = []
    final_message: dict[str, Any] | None = None
    for attempt_index in range(1, max_attempts + 1):
        if prepare_attempt is not None:
            prepare_attempt(attempt_index)
        _clear_stale_attempt_outputs([last_message_path, *expected_output_paths])

        started = time.time()
        timed_out = False
        proc: subprocess.CompletedProcess[str] | None = None
        stdout_text = ""
        stderr_text = ""
        timeout_message: str | None = None
        try:
            proc = subprocess_runner(
                command,
                cwd=str(ROOT),
                input=prompt,
                text=True,
                capture_output=True,
                timeout=timeout_sec,
            )
            stdout_text = _coerce_output_text(proc.stdout)
            stderr_text = _coerce_output_text(proc.stderr)
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout_text = _coerce_output_text(exc.stdout)
            stderr_text = _coerce_output_text(exc.stderr)
            timeout_message = str(exc)
        duration_sec = time.time() - started

        attempt_stdout_path = agent_dir / f"stdout.attempt-{attempt_index}.jsonl"
        attempt_stderr_path = agent_dir / f"stderr.attempt-{attempt_index}.txt"
        attempt_stdout_path.write_text(stdout_text)
        attempt_stderr_path.write_text(stderr_text)
        stdout_path.write_text(stdout_text)
        stderr_path.write_text(stderr_text)

        attempts.append(
            {
                "attempt_index": attempt_index,
                "timeout_sec": timeout_sec,
                "timed_out": timed_out,
                "returncode": None if proc is None else proc.returncode,
                "duration_sec": duration_sec,
                "stdout_path": str(attempt_stdout_path),
                "stderr_path": str(attempt_stderr_path),
                "timeout_message": timeout_message,
            }
        )
        write_json(
            metadata_path,
            {
                "role_name": role_name,
                "model_name": model_name,
                "cli_name": cli_name,
                "cli_model_name": cli_model_name,
                "playbook_path": str(playbook_path),
                "expected_output_paths": [str(path) for path in expected_output_paths],
                "timeout_sec": timeout_sec,
                "max_attempts": max_attempts,
                "retry_backoff_sec": retry_backoff_sec,
                "attempts": attempts,
            },
        )

        if timed_out:
            if attempt_index < max_attempts:
                if retry_backoff_sec > 0:
                    time.sleep(retry_backoff_sec)
                continue
            raise PlaybookAgentTimeoutError(
                f"{role_name} agent run timed out after {max_attempts} attempt(s); see {metadata_path}"
            )
        assert proc is not None
        if proc.returncode != 0:
            raise PlaybookAgentExecutionError(
                f"{role_name} agent run failed ({proc.returncode}); see {stdout_path} and {stderr_path}"
            )
        if cli_name == "claude":
            try:
                payload = json.loads(stdout_text)
            except json.JSONDecodeError as exc:
                raise PlaybookAgentOutputContractError(
                    f"{role_name} Claude output is not valid JSON: {stdout_path}"
                ) from exc
            final_message = payload.get("structured_output")
            if not isinstance(final_message, dict):
                raise PlaybookAgentOutputContractError(
                    f"{role_name} Claude output missing structured_output object: {stdout_path}"
                )
            write_json(last_message_path, final_message)
        else:
            if not last_message_path.exists():
                raise PlaybookAgentOutputContractError(
                    f"{role_name} agent did not write final message: {last_message_path}"
                )
            try:
                final_message = json.loads(last_message_path.read_text())
            except json.JSONDecodeError as exc:
                raise PlaybookAgentOutputContractError(
                    f"{role_name} final message is not valid JSON: {last_message_path}"
                ) from exc

        missing = [str(path) for path in expected_output_paths if not path.exists()]
        if missing:
            raise PlaybookAgentOutputContractError(
                f"{role_name} agent did not produce expected outputs: {missing}"
            )
        break

    if final_message is None:
        raise PlaybookAgentOutputContractError(
            f"{role_name} agent did not produce a final message: {last_message_path}"
        )

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
    "PlaybookAgentError",
    "PlaybookAgentExecutionError",
    "PlaybookAgentOutputContractError",
    "PlaybookAgentTimeoutError",
    "ensure_playbook_path",
    "resolve_cli_model_name",
    "resolve_playbook_cli_name",
    "run_playbook_agent",
]
