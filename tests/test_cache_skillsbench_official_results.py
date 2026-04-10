from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "cache_skillsbench_official_results.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("cache_skillsbench_official_results", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CacheSkillsbenchOfficialResultsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def test_extract_results_rows_from_embedded_html(self) -> None:
        html = r"""
<html>
<body>
<script>
self.__next_f.push([1,"{\"results\":[{\"task\":\"citation-check\",\"model\":\"Claude Code (Sonnet 4.5)\",\"modelShort\":\"Sonnet 4.5\",\"harness\":\"Claude Code\",\"family\":\"anthropic\",\"condition\":\"With Skills\",\"score\":80,\"trials\":5,\"passCount\":4,\"perfectCount\":4},{\"task\":\"citation-check\",\"model\":\"Claude Code (Sonnet 4.5)\",\"modelShort\":\"Sonnet 4.5\",\"harness\":\"Claude Code\",\"family\":\"anthropic\",\"condition\":\"No Skills\",\"score\":40,\"trials\":5,\"passCount\":2,\"perfectCount\":2}],\"trajectoryIndex\":[]}"]);
</script>
</body>
</html>
""".strip()
        rows = self.module.extract_results_rows(html, task_id="citation-check")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["condition"], "With Skills")
        self.assertEqual(rows[0]["modelShort"], "Sonnet 4.5")
        self.assertEqual(rows[1]["score"], 40)

    def test_normalize_result_row_flattens_fields(self) -> None:
        row = {
            "task": "citation-check",
            "model": "Claude Code (Sonnet 4.5)",
            "modelShort": "Sonnet 4.5",
            "harness": "Claude Code",
            "family": "anthropic",
            "condition": "With Skills",
            "score": 80,
            "trials": 5,
            "passCount": 4,
            "perfectCount": 4,
        }
        normalized = self.module.normalize_result_row(
            task_id="citation-check",
            source_url="https://www.skillsbench.ai/tasks/citation-check",
            cached_at="2026-04-08T00:00:00Z",
            row=row,
        )
        self.assertEqual(normalized["task_id"], "citation-check")
        self.assertEqual(normalized["model_short"], "Sonnet 4.5")
        self.assertEqual(normalized["pass_count"], 4)
        self.assertEqual(normalized["condition"], "With Skills")

    def test_write_cache_outputs_creates_task_and_aggregate_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            task_payloads = [
                {
                    "task_id": "citation-check",
                    "source_url": "https://www.skillsbench.ai/tasks/citation-check",
                    "cached_at": "2026-04-08T00:00:00Z",
                    "results": [
                        {
                            "task_id": "citation-check",
                            "source_url": "https://www.skillsbench.ai/tasks/citation-check",
                            "cached_at": "2026-04-08T00:00:00Z",
                            "model": "Claude Code (Sonnet 4.5)",
                            "model_short": "Sonnet 4.5",
                            "harness": "Claude Code",
                            "family": "anthropic",
                            "condition": "With Skills",
                            "score": 80,
                            "trials": 5,
                            "pass_count": 4,
                            "perfect_count": 4,
                        }
                    ],
                }
            ]
            aggregate_rows = task_payloads[0]["results"]
            manifest = {
                "task_count_attempted": 1,
                "task_count_succeeded": 1,
                "task_count_missing_results": 0,
            }

            self.module.write_cache_outputs(
                output_dir=output_dir,
                task_payloads=task_payloads,
                aggregate_rows=aggregate_rows,
                manifest=manifest,
            )

            task_json = output_dir / "tasks" / "citation-check.json"
            jsonl_path = output_dir / "official_task_results.jsonl"
            csv_path = output_dir / "official_task_results.csv"
            manifest_path = output_dir / "manifest.json"

            self.assertTrue(task_json.exists())
            self.assertTrue(jsonl_path.exists())
            self.assertTrue(csv_path.exists())
            self.assertTrue(manifest_path.exists())

            payload = json.loads(task_json.read_text())
            self.assertEqual(payload["task_id"], "citation-check")
            self.assertEqual(payload["results"][0]["model_short"], "Sonnet 4.5")

            jsonl_rows = [json.loads(line) for line in jsonl_path.read_text().splitlines() if line.strip()]
            self.assertEqual(len(jsonl_rows), 1)
            self.assertIn("model_short,condition,score", csv_path.read_text())


if __name__ == "__main__":
    unittest.main()
