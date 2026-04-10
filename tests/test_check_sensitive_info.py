from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "check_sensitive_info.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("check_sensitive_info", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CheckSensitiveInfoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def test_scan_paths_flags_absolute_home_path_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / "docs" / "example.md"
            path.parent.mkdir(parents=True)
            path.write_text("use /Users/alice/.claude/claude-code-oauth-token\n")

            findings = self.module.scan_paths([path], root=root)

            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].kind, "content")
            self.assertIn("absolute macOS home path", findings[0].detail)

    def test_scan_paths_flags_raw_agent_runtime_artifact_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = (
                root
                / "experiments"
                / "demo"
                / "runs"
                / "trial"
                / "agent"
                / "claude-code.txt"
            )
            path.parent.mkdir(parents=True)
            path.write_text("{}\n")

            findings = self.module.scan_paths([path], root=root)

            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].kind, "path")
            self.assertIn("raw agent runtime artifacts", findings[0].detail)

    def test_scan_paths_allows_generic_home_lookup_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / "scripts" / "example.py"
            path.parent.mkdir(parents=True)
            path.write_text('DEFAULT_OAUTH_FILE = Path.home() / ".claude" / "claude-code-oauth-token"\n')

            findings = self.module.scan_paths([path], root=root)

            self.assertEqual(findings, [])

    def test_scan_paths_flags_hardcoded_env_assignment(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / "config.py"
            path.write_text('OPENAI_API_KEY = "abc123-secret-value"\n')

            findings = self.module.scan_paths([path], root=root)

            self.assertEqual(len(findings), 1)
            self.assertIn("hardcoded OPENAI_API_KEY assignment", findings[0].detail)


if __name__ == "__main__":
    unittest.main()
