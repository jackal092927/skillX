"""Runtime checks shared by SkillX command-line scripts."""

from __future__ import annotations

import inspect
import sys


def assert_supported_python_runtime() -> None:
    """Fail early when a CLI is launched with an unsupported Python runtime."""
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
