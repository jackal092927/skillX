from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .io_utils import write_json


def timestamp_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_run_failure_payload(
    *,
    error: BaseException | None = None,
    error_type: str | None = None,
    error_message: str | None = None,
    traceback_text: str | None = None,
    observed_at: str | None = None,
    failed_stage: str | None = None,
    failed_round: int | None = None,
    manual_intervention: bool | None = None,
    returncode: int | None = None,
    command: Sequence[str] | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "error_type": error_type or (type(error).__name__ if error is not None else "UnknownError"),
        "error_message": error_message if error_message is not None else (str(error) if error is not None else ""),
        "observed_at": observed_at or timestamp_utc(),
        "failed_stage": failed_stage if failed_stage is not None else getattr(error, "failed_stage", None),
        "failed_round": failed_round if failed_round is not None else getattr(error, "failed_round", None),
        "manual_intervention": bool(
            manual_intervention if manual_intervention is not None else getattr(error, "manual_intervention", False)
        ),
    }
    if traceback_text:
        payload["traceback"] = traceback_text
    if returncode is not None:
        payload["returncode"] = int(returncode)
    elif error is not None and hasattr(error, "returncode"):
        try:
            payload["returncode"] = int(getattr(error, "returncode"))
        except (TypeError, ValueError):
            pass
    if command is not None:
        payload["command"] = [str(part) for part in command]
    if extra:
        for key, value in extra.items():
            if value is not None:
                payload[str(key)] = value
    return payload


def write_run_failure(path: Path, payload: Mapping[str, Any], *, overwrite: bool = True) -> None:
    if path.exists() and not overwrite:
        return
    write_json(path, dict(payload))


__all__ = [
    "build_run_failure_payload",
    "timestamp_utc",
    "write_run_failure",
]
