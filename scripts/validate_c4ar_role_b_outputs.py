from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from skillx.c4ar.role_b import _validate_next_skillpack_manifest_contents
from skillx.c4ar.role_b_artifacts import load_and_canonicalize_role_b_artifact_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and canonicalize Role B C4AR outputs.")
    parser.add_argument("--refine-plan", required=True, dest="refine_plan")
    parser.add_argument("--next-skillpack-manifest", required=True, dest="next_skillpack_manifest")
    parser.add_argument("--round-decision", required=True, dest="round_decision")
    parser.add_argument("--task-id", required=False, dest="task_id")
    parser.add_argument("--round-index", type=int, required=False, dest="round_index")
    parser.add_argument("--role-name", required=False, dest="role_name")
    parser.add_argument("--rewrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        artifacts = load_and_canonicalize_role_b_artifact_files(
            refine_plan_json_path=Path(args.refine_plan),
            next_skillpack_manifest_json_path=Path(args.next_skillpack_manifest),
            round_decision_json_path=Path(args.round_decision),
            rewrite=args.rewrite,
        )

        if args.task_id is not None:
            for field_name, value in (
                ("refine_plan.task_id", artifacts.refine_plan.task_id),
                ("next_skillpack_manifest.task_id", artifacts.next_skillpack_manifest.task_id),
                ("round_decision.task_id", artifacts.round_decision.task_id),
            ):
                if value != args.task_id:
                    raise ValueError(f"{field_name} must equal {args.task_id!r}")

        if args.round_index is not None:
            for field_name, value in (
                ("refine_plan.round_index", artifacts.refine_plan.round_index),
                ("next_skillpack_manifest.round_index", artifacts.next_skillpack_manifest.round_index),
                ("round_decision.round_index", artifacts.round_decision.round_index),
            ):
                if value != args.round_index:
                    raise ValueError(f"{field_name} must equal {args.round_index}")

        if args.role_name is not None:
            for field_name, value in (
                ("refine_plan.role", artifacts.refine_plan.role),
                ("next_skillpack_manifest.role", artifacts.next_skillpack_manifest.role),
                ("round_decision.role", artifacts.round_decision.role),
            ):
                if value != args.role_name:
                    raise ValueError(f"{field_name} must equal {args.role_name!r}")

        if not (
            artifacts.refine_plan.model_name
            == artifacts.next_skillpack_manifest.model_name
            == artifacts.round_decision.model_name
        ):
            raise ValueError("model_name mismatch across Role B outputs")

        if artifacts.round_decision.decision == "continue":
            if artifacts.round_decision.next_round_index != artifacts.round_decision.round_index + 1:
                raise ValueError("continue decision must advance exactly one round")
            if artifacts.round_decision.next_skillpack_dir != artifacts.next_skillpack_manifest.skillpack_dir:
                raise ValueError("round decision next_skillpack_dir must match next skillpack manifest")

        _validate_next_skillpack_manifest_contents(artifacts.next_skillpack_manifest)
    except Exception as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)]}, indent=2))
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "normalized": {
                    "refine_plan": artifacts.refine_plan_payload,
                    "next_skillpack_manifest": artifacts.next_skillpack_manifest_payload,
                    "round_decision": artifacts.round_decision_payload,
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
