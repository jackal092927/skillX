#!/usr/bin/env python3
"""Fail fast on tracked or staged sensitive/local-environment artifacts."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PATH_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"^experiments/.+/agent/"),
        "raw agent runtime artifacts must not be versioned; keep summaries instead",
    ),
)

FORBIDDEN_CONTENT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"/Users/[^/\s]+/"),
        "absolute macOS home path",
    ),
    (
        re.compile(r"/home/[A-Za-z0-9._-]+/"),
        "absolute Linux home path",
    ),
    (
        re.compile(r"\bOPENAI_API_KEY\s*=\s*['\"](?!\$\{)[^'\"]+['\"]"),
        "hardcoded OPENAI_API_KEY assignment",
    ),
    (
        re.compile(r"\bANTHROPIC_API_KEY\s*=\s*['\"](?!\$\{)[^'\"]+['\"]"),
        "hardcoded ANTHROPIC_API_KEY assignment",
    ),
    (
        re.compile(r"\bBearer\s+[A-Za-z0-9._-]{20,}"),
        "bearer token literal",
    ),
    (
        re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
        "OpenAI-style API key literal",
    ),
    (
        re.compile(r"['\"](?:access_token|refresh_token)['\"]\s*:\s*['\"][^'\"]{20,}['\"]"),
        "token JSON field literal",
    ),
)


@dataclass(frozen=True)
class Finding:
    path: Path
    kind: str
    detail: str
    line_no: int | None = None
    line_text: str | None = None

    def render(self) -> str:
        rel_path = self.path.as_posix()
        if self.line_no is None:
            return f"{rel_path}: {self.kind}: {self.detail}"
        excerpt = (self.line_text or "").strip()
        return f"{rel_path}:{self.line_no}: {self.kind}: {self.detail}: {excerpt}"


def _git_paths(*, staged: bool) -> list[Path]:
    command = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"] if staged else ["git", "ls-files"]
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"git command failed: {' '.join(command)}")
    return [Path(line) for line in proc.stdout.splitlines() if line.strip()]


def _candidate_paths(staged: bool, explicit_paths: list[str]) -> list[Path]:
    if explicit_paths:
        return [Path(path) for path in explicit_paths]
    return _git_paths(staged=staged)


def scan_paths(paths: Iterable[Path], *, root: Path = ROOT) -> list[Finding]:
    findings: list[Finding] = []
    for raw_path in paths:
        path = raw_path if raw_path.is_absolute() else (root / raw_path)
        if not path.exists() or not path.is_file():
            continue
        rel_path = path.relative_to(root) if path.is_relative_to(root) else raw_path
        rel_text = rel_path.as_posix()

        for pattern, detail in FORBIDDEN_PATH_PATTERNS:
            if pattern.search(rel_text):
                findings.append(Finding(path=rel_path, kind="path", detail=detail))

        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern, detail in FORBIDDEN_CONTENT_PATTERNS:
            for line_no, line in enumerate(text.splitlines(), start=1):
                if pattern.search(line):
                    findings.append(
                        Finding(
                            path=rel_path,
                            kind="content",
                            detail=detail,
                            line_no=line_no,
                            line_text=line,
                        )
                    )
    return findings


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true", help="scan staged files instead of all tracked files")
    parser.add_argument("paths", nargs="*", help="optional explicit paths to scan")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    findings = scan_paths(_candidate_paths(args.staged, args.paths))
    if findings:
        for finding in findings:
            print(finding.render(), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
