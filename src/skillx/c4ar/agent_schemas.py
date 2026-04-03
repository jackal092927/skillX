from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RoleAFinalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    json_path: str
    markdown_path: str
    notes: str


class RoleBFinalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    refine_plan_json_path: str
    refine_plan_markdown_path: str
    next_skillpack_manifest_json_path: str
    round_decision_json_path: str
    next_skillpack_dir: str
    notes: str


__all__ = [
    "RoleAFinalResponse",
    "RoleBFinalResponse",
]
