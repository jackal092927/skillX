from __future__ import annotations

import shutil
from pathlib import Path
from typing import Sequence

from .io_utils import ensure_dir


def discover_skill_names(skills_dir: Path) -> list[str]:
    if not skills_dir.exists():
        raise FileNotFoundError(f"skills directory not found: {skills_dir}")
    if not skills_dir.is_dir():
        raise FileNotFoundError(f"skills path is not a directory: {skills_dir}")
    skill_names = sorted(
        path.name
        for path in skills_dir.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    if not skill_names:
        raise FileNotFoundError(f"no skill directories with SKILL.md found under {skills_dir}")
    return skill_names


def copy_named_skill_dirs(
    *,
    source_skills_dir: Path,
    dest_skills_dir: Path,
    skill_names: Sequence[str],
    context_label: str,
) -> None:
    if not source_skills_dir.exists():
        raise FileNotFoundError(f"{context_label} directory not found: {source_skills_dir}")
    if not source_skills_dir.is_dir():
        raise FileNotFoundError(f"{context_label} path is not a directory: {source_skills_dir}")
    if dest_skills_dir.exists():
        shutil.rmtree(dest_skills_dir)
    ensure_dir(dest_skills_dir)
    for skill_name in skill_names:
        source_dir = source_skills_dir / skill_name
        skill_path = source_dir / "SKILL.md"
        if not source_dir.exists() or not source_dir.is_dir() or not skill_path.is_file():
            raise FileNotFoundError(
                f"{context_label} missing required skill file: {skill_path}"
            )
        shutil.copytree(source_dir, dest_skills_dir / skill_name)


__all__ = [
    "copy_named_skill_dirs",
    "discover_skill_names",
]
