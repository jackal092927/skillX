"""Minimal validator types used by the standalone SkillX repo."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidationResult:
    ok: bool
    errors: tuple[str, ...]


__all__ = ["ValidationResult"]
