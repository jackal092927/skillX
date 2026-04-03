from __future__ import annotations

import shutil
from pathlib import Path


OUTPUT_PATH = Path("/root/output/bundle.yaml")
EXPORT_DIR = Path("/logs/verifier/exported")
REQUIRED_SUBSTRING = None


def main() -> int:
    if not OUTPUT_PATH.exists():
        raise SystemExit("missing output artifact")
    text = OUTPUT_PATH.read_text().strip()
    if not text:
        raise SystemExit("output artifact is empty")
    if REQUIRED_SUBSTRING and REQUIRED_SUBSTRING not in text:
        raise SystemExit(f"required substring missing: {REQUIRED_SUBSTRING}")
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUTPUT_PATH, EXPORT_DIR / OUTPUT_PATH.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
