from __future__ import annotations

import time
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import Settings, load_settings
from .shared_skills import (
    SharedSkillNotFound,
    SharedSkillsConfigError,
    describe_shared_skill,
    list_shared_skills,
    retrieve_shared_skill,
    search_shared_skills,
)


class SharedSkillListIn(BaseModel):
    category: str | None = Field(default=None, max_length=64)
    limit: int = Field(default=50, ge=1, le=100)


class SharedSkillDescribeIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)


class SharedSkillSearchIn(BaseModel):
    query: str = Field(min_length=1, max_length=200)
    category: str | None = Field(default=None, max_length=64)
    limit: int = Field(default=10, ge=1, le=100)


class SharedSkillRetrieveIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    include_bundle: bool = True


class SharedSkillInstallIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    target_category: str | None = Field(default=None, max_length=64)
    overwrite: bool = True


TOOLS = [
    {"name": "list_shared_skills", "description": "List Shared Skills Registry metadata."},
    {"name": "describe_shared_skill", "description": "Describe one Shared Skills Registry entry."},
    {"name": "search_shared_skills", "description": "Search Shared Skills Registry metadata."},
    {"name": "retrieve_shared_skill", "description": "Retrieve a checksum-bearing source bundle."},
    {"name": "install_shared_skill", "description": "Authorize local install by returning a checked bundle for caller-local installation."},
]


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    app = FastAPI(title="Shared Skills Registry MCP", version="0.1.0")

    @app.get("/healthz")
    def healthz() -> dict[str, Any]:
        return {"ok": True, "bind_host": settings.bind_host, "tools": [t["name"] for t in TOOLS]}

    @app.get("/tools")
    def tools() -> dict[str, Any]:
        return {"tools": TOOLS}

    @app.post("/tools/list_shared_skills")
    def list_shared_skills_tool(inp: SharedSkillListIn | None = None) -> dict[str, Any]:
        payload = inp or SharedSkillListIn()
        started = time.monotonic()
        try:
            result = list_shared_skills(settings.shared_skills_path, category=payload.category, limit=payload.limit)
            result["latency_ms"] = int((time.monotonic() - started) * 1000)
            return result
        except SharedSkillsConfigError as exc:
            raise HTTPException(status_code=503, detail={"code": "directory_unavailable", "message": str(exc)}) from exc

    @app.post("/tools/describe_shared_skill")
    def describe_shared_skill_tool(inp: SharedSkillDescribeIn) -> dict[str, Any]:
        try:
            return describe_shared_skill(settings.shared_skills_path, inp.name)
        except SharedSkillNotFound as exc:
            raise HTTPException(status_code=404, detail={"code": "skill_not_found", "message": "unknown shared skill"}) from exc
        except SharedSkillsConfigError as exc:
            raise HTTPException(status_code=503, detail={"code": "directory_unavailable", "message": str(exc)}) from exc

    @app.post("/tools/search_shared_skills")
    def search_shared_skills_tool(inp: SharedSkillSearchIn) -> dict[str, Any]:
        try:
            return search_shared_skills(settings.shared_skills_path, inp.query, category=inp.category, limit=inp.limit)
        except SharedSkillsConfigError as exc:
            raise HTTPException(status_code=503, detail={"code": "directory_unavailable", "message": str(exc)}) from exc

    @app.post("/tools/retrieve_shared_skill")
    def retrieve_shared_skill_tool(inp: SharedSkillRetrieveIn) -> dict[str, Any]:
        try:
            return retrieve_shared_skill(
                settings.shared_skills_path,
                inp.name,
                content_roots=list(settings.shared_skill_content_roots),
                include_bundle=inp.include_bundle,
            )
        except SharedSkillNotFound as exc:
            raise HTTPException(status_code=404, detail={"code": "skill_not_found", "message": "unknown shared skill or source unavailable"}) from exc
        except SharedSkillsConfigError as exc:
            raise HTTPException(status_code=503, detail={"code": "directory_unavailable", "message": str(exc)}) from exc

    @app.post("/tools/install_shared_skill")
    def install_shared_skill_tool(inp: SharedSkillInstallIn) -> dict[str, Any]:
        try:
            bundle = retrieve_shared_skill(
                settings.shared_skills_path,
                inp.name,
                content_roots=list(settings.shared_skill_content_roots),
                include_bundle=True,
            )
            bundle["install_authorized"] = True
            bundle["target_category"] = inp.target_category or bundle["skill"].get("category")
            bundle["overwrite"] = inp.overwrite
            return bundle
        except SharedSkillNotFound as exc:
            raise HTTPException(status_code=404, detail={"code": "skill_not_found", "message": "unknown shared skill or source unavailable"}) from exc
        except SharedSkillsConfigError as exc:
            raise HTTPException(status_code=503, detail={"code": "directory_unavailable", "message": str(exc)}) from exc

    return app


app = create_app()
