"""Runtime checks shared by SkillX command-line scripts."""

from __future__ import annotations

import inspect
import os
from pathlib import Path
import sys


SUSPICIOUS_VENV_REENTRY_MARKERS = (
    b'$(pwd)/.venv/bin/python',
    b"${PWD}/.venv/bin/python",
    b".venv/bin/python",
)


def assert_healthy_python_executable(executable: str | os.PathLike[str] | None = None) -> Path:
    """Fail fast when a Python executable path is a known-bad recursive wrapper."""
    executable_path = Path(executable or sys.executable)
    command_path = executable_path if executable_path.is_absolute() else Path.cwd() / executable_path
    try:
        command_path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise SystemExit(f"Python executable does not exist: {executable_path}") from exc

    if not os.access(command_path, os.X_OK):
        raise SystemExit(f"Python executable is not executable: {command_path}")

    try:
        header = command_path.read_bytes()[:512]
    except OSError as exc:
        raise SystemExit(f"Could not inspect Python executable {command_path}: {exc}") from exc

    if header.startswith(b"#!") and any(marker in header for marker in SUSPICIOUS_VENV_REENTRY_MARKERS):
        raise SystemExit(
            "Python executable appears to be a recursive .venv wrapper, which can deadlock uv "
            f"interpreter probing: {command_path}. Reinstall the uv-managed Python runtime "
            "with `uv --no-config --directory /tmp python install 3.11.14 --reinstall --force` "
            "and recreate the project virtualenv if needed."
        )

    return command_path


def assert_supported_python_runtime() -> None:
    """Fail early when a CLI is launched with an unsupported Python runtime."""
    assert_healthy_python_executable()

    if sys.version_info < (3, 11):
        raise SystemExit(
            "SkillX CLI scripts require Python >= 3.11. "
            f"Current runtime is Python {sys.version.split()[0]} at {sys.executable}. "
            "Run through `uv run --python 3.11 python ...` or set SKILLX_PYTHON=3.11+."
        )

    import dataclasses

    dataclass_params = inspect.signature(dataclasses.dataclass).parameters
    if "slots" not in dataclass_params:
        dataclasses_file = getattr(dataclasses, "__file__", "<unknown>")
        raise SystemExit(
            "SkillX CLI scripts require dataclasses.dataclass(slots=...). "
            f"The imported dataclasses module does not support slots: {dataclasses_file}. "
            "Use the Python 3.11+ standard-library dataclasses module."
        )
