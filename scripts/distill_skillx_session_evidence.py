#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from skillx.io_utils import write_json
from skillx.session_evidence import (
    distill_session_logs,
    render_session_evidence_markdown,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Distill high-signal evidence from Claude Code session logs")
    parser.add_argument("session_logs", nargs="+", help="Local session log paths to distill")
    parser.add_argument("--output-json", required=True, help="Path to write the distilled JSON artifact")
    parser.add_argument(
        "--output-md",
        help="Optional markdown output path. Defaults to the JSON path with a .md suffix.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    session_paths = [Path(path) for path in args.session_logs]
    evidence = distill_session_logs(session_paths)

    output_json = Path(args.output_json)
    output_md = Path(args.output_md) if args.output_md else output_json.with_suffix(".md")

    write_json(output_json, evidence.to_dict())
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_session_evidence_markdown(evidence))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
