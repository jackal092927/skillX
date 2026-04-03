from __future__ import annotations

import shutil
from pathlib import Path


OUTPUT_DIR = Path("/root/output")
EXPORT_DIR = Path("/logs/verifier/exported")
ROUND_INDEX = 2
REQUIRED_FILES = [
    f"round_{ROUND_INDEX}_skill.md",
    f"round_{ROUND_INDEX}_refine_memo.md",
    f"round_{ROUND_INDEX}_diff_summary.md",
    f"round_{ROUND_INDEX}_effect_estimate.md",
    f"round_{ROUND_INDEX}_risk_note.md",
    f"round_{ROUND_INDEX}_diagnosis_table.md",
]


def main() -> int:
    for filename in REQUIRED_FILES:
        path = OUTPUT_DIR / filename
        if not path.exists():
            raise SystemExit(f"missing round artifact: {filename}")
        if not path.read_text().strip():
            raise SystemExit(f"empty round artifact: {filename}")
    skillpack_root = OUTPUT_DIR / 'skillpack' / 'skills'
    if not skillpack_root.exists():
        raise SystemExit('missing skillpack/skills output')
    skill_path = skillpack_root / 'data_cleaning' / 'SKILL.md'
    if not skill_path.exists():
        raise SystemExit('missing refined skill for data_cleaning')
    text = skill_path.read_text().strip()
    if '# Derived Execution Layer' not in text:
        raise SystemExit('refined skill missing derived layer: data_cleaning')
    skill_path = skillpack_root / 'did_causal_analysis' / 'SKILL.md'
    if not skill_path.exists():
        raise SystemExit('missing refined skill for did_causal_analysis')
    text = skill_path.read_text().strip()
    if '# Derived Execution Layer' not in text:
        raise SystemExit('refined skill missing derived layer: did_causal_analysis')
    skill_path = skillpack_root / 'feature_engineering' / 'SKILL.md'
    if not skill_path.exists():
        raise SystemExit('missing refined skill for feature_engineering')
    text = skill_path.read_text().strip()
    if '# Derived Execution Layer' not in text:
        raise SystemExit('refined skill missing derived layer: feature_engineering')
    skill_path = skillpack_root / 'time_series_anomaly_detection' / 'SKILL.md'
    if not skill_path.exists():
        raise SystemExit('missing refined skill for time_series_anomaly_detection')
    text = skill_path.read_text().strip()
    if '# Derived Execution Layer' not in text:
        raise SystemExit('refined skill missing derived layer: time_series_anomaly_detection')
    if not (OUTPUT_DIR / 'skillpack_bundle.yaml').exists():
        raise SystemExit('missing skillpack_bundle.yaml')
    if EXPORT_DIR.exists():
        shutil.rmtree(EXPORT_DIR)
    shutil.copytree(OUTPUT_DIR, EXPORT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
