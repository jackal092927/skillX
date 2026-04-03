from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "skillx" / "session_evidence.py"
SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "distill_skillx_session_evidence.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("skillx_session_evidence", MODULE_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_script():
    spec = importlib.util.spec_from_file_location("distill_skillx_session_evidence", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SkillxSessionEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        cls.script = _load_script()

    def test_distill_text_log_extracts_bounded_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "session.log"
            log_path.write_text(
                "\n".join(
                    [
                        "tool=read_file path=skill.md",
                        "tool=search query=refine protocol",
                        "tool=read_file path=skill.md",
                        "tool=read_file path=skill.md",
                        "timeout while waiting for verifier",
                        "retry after timeout",
                        "final note: skill may be misleading the agent",
                    ]
                )
                + "\n"
            )
            evidence = self.module.distill_session_logs([log_path])
            self.assertIn("wasted loop", evidence.wasted_loop_signals[0].lower())
            self.assertTrue(any("timeout" in text.lower() for text in evidence.critical_turns))
            self.assertTrue(any("misleading" in text.lower() for text in evidence.skill_misguidance_signals))
            self.assertIn("compress_derived_layer", evidence.recommended_edit_targets)
            self.assertGreaterEqual(len(evidence.evidence_refs), 1)

    def test_distill_jsonl_log_prefers_high_signal_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "session.jsonl"
            rows = [
                {"type": "tool_call", "tool": "read_file", "path": "skill.md", "message": "read skill"},
                {"type": "tool_call", "tool": "read_file", "path": "skill.md", "message": "read skill"},
                {"type": "tool_call", "tool": "read_file", "path": "skill.md", "message": "read skill"},
                {"type": "tool_call", "tool": "bash", "message": "bash"},
                {"type": "tool_call", "tool": "todowrite", "message": "todowrite"},
                {"type": "observation", "message": "verifier contract failed: missing refined skill"},
                {"type": "note", "message": "irrelevant chatter"},
            ]
            log_path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
            evidence = self.module.distill_session_logs([log_path])
            self.assertTrue(any("repeated" in text.lower() for text in evidence.wasted_loop_signals))
            self.assertTrue(any("contract" in text.lower() for text in evidence.critical_turns))
            self.assertTrue(any(target in evidence.recommended_edit_targets for target in ["remove_speculative_evaluator_content", "tighten_scope_boundary"]))
            self.assertTrue(all("irrelevant chatter" not in text for text in evidence.critical_turns))
            self.assertTrue(all("bash" not in text.lower() for text in evidence.wasted_loop_signals))
            self.assertTrue(all("todowrite" not in text.lower() for text in evidence.wasted_loop_signals))

    def test_critical_turns_are_short_human_readable_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "session.jsonl"
            log_path.write_text(
                json.dumps(
                    {
                        "type": "observation",
                        "tool": "verifier",
                        "message": "verifier contract failed: missing refined skill",
                        "content": {
                            "deep": {"nested": "value"},
                            "another": ["should", "not", "surface"],
                        },
                    }
                )
                + "\n"
            )
            evidence = self.module.distill_session_logs([log_path])
            self.assertEqual(len(evidence.critical_turns), 1)
            self.assertLess(len(evidence.critical_turns[0]), 120)
            self.assertNotIn("{", evidence.critical_turns[0])
            self.assertIn("missing refined skill", evidence.critical_turns[0].lower())

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            log_path = tmp / "session.log"
            log_path.write_text("tool=read_file path=skill.md\n" * 3)
            json_out = tmp / "artifact.json"
            md_out = tmp / "artifact.md"
            exit_code = self.script.main(
                [
                    str(log_path),
                    "--output-json",
                    str(json_out),
                    "--output-md",
                    str(md_out),
                ]
            )
            self.assertEqual(exit_code, 0)
            payload = json.loads(json_out.read_text())
            self.assertIn("dominant_failure_pattern", payload)
            self.assertTrue(md_out.exists())
            self.assertIn("# Session-Derived Evidence", md_out.read_text())


if __name__ == "__main__":
    unittest.main()
