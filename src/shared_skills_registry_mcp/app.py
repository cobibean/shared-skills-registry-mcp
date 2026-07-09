from __future__ import annotations

import time
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, Field

from .audit import AuditLog
from .config import Settings, load_settings
from .registry_edit import delete_registry_skill, list_registry_skills, upsert_registry_skill
from .runtime_paths import default_ui_path
from .shared_skills import (
    SharedSkillNotFound,
    SharedSkillsConfigError,
    describe_shared_skill,
    list_shared_skills,
    retrieve_shared_skill,
    search_shared_skills,
)

_UI_INDEX = default_ui_path()


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


class RegistrySkillIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    title: str = Field(min_length=1, max_length=160)
    summary: str = Field(min_length=1, max_length=1200)
    category: str = Field(min_length=1, max_length=64)
    owner: str = Field(min_length=1, max_length=64)
    source: str = Field(min_length=1, max_length=160)
    docs_path: str = Field(min_length=1, max_length=300)
    applicability: str = Field(min_length=1, max_length=1200)
    lifecycle_status: str = Field(min_length=1, max_length=64)
    install_guidance: str = Field(min_length=1, max_length=1200)
    tags: list[str] = Field(default_factory=list, max_length=20)


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
    audit = AuditLog(settings.audit_log_path)

    def _elapsed_ms(started: float) -> int:
        return int((time.monotonic() - started) * 1000)

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse(url="/ui")

    @app.get("/ui", include_in_schema=False)
    def ui() -> FileResponse:
        return FileResponse(_UI_INDEX, media_type="text/html")

    @app.get("/healthz")
    def healthz() -> dict[str, Any]:
        return {"ok": True, "bind_host": settings.bind_host, "tools": [t["name"] for t in TOOLS]}

    @app.get("/registry/skills")
    def registry_skills() -> dict[str, Any]:
        try:
            return list_registry_skills(settings.shared_skills_path, content_roots=list(settings.shared_skill_content_roots))
        except SharedSkillsConfigError as exc:
            raise HTTPException(status_code=503, detail={"code": "directory_unavailable", "message": str(exc)}) from exc

    @app.put("/registry/skills/{name}")
    def registry_upsert(name: str, inp: RegistrySkillIn) -> dict[str, Any]:
        started = time.monotonic()
        entry = inp.model_dump()
        if name.strip().lower() != inp.name.strip().lower():
            raise HTTPException(status_code=400, detail={"code": "name_mismatch", "message": "path name does not match body name"})
        try:
            result = upsert_registry_skill(settings.shared_skills_path, entry)
            audit.record_event(event_type="registry_edit", tool_name="upsert_registry_skill", arguments={"name": inp.name}, result_summary={"created": result["created"]}, status="ok", latency_ms=_elapsed_ms(started))
            return result
        except SharedSkillsConfigError as exc:
            audit.record_event(event_type="registry_edit", tool_name="upsert_registry_skill", arguments={"name": inp.name}, status="error", error_class=type(exc).__name__, latency_ms=_elapsed_ms(started))
            raise HTTPException(status_code=422, detail={"code": "invalid_skill_entry", "message": str(exc)}) from exc

    @app.delete("/registry/skills/{name}")
    def registry_delete(name: str) -> dict[str, Any]:
        started = time.monotonic()
        try:
            result = delete_registry_skill(settings.shared_skills_path, name)
            audit.record_event(event_type="registry_edit", tool_name="delete_registry_skill", arguments={"name": name}, result_summary={"remaining": result["remaining"]}, status="ok", latency_ms=_elapsed_ms(started))
            return result
        except SharedSkillNotFound as exc:
            audit.record_event(event_type="registry_edit", tool_name="delete_registry_skill", arguments={"name": name}, status="error", error_class="SharedSkillNotFound", latency_ms=_elapsed_ms(started))
            raise HTTPException(status_code=404, detail={"code": "skill_not_found", "message": "unknown shared skill"}) from exc
        except SharedSkillsConfigError as exc:
            audit.record_event(event_type="registry_edit", tool_name="delete_registry_skill", arguments={"name": name}, status="error", error_class=type(exc).__name__, latency_ms=_elapsed_ms(started))
            raise HTTPException(status_code=503, detail={"code": "directory_unavailable", "message": str(exc)}) from exc

    @app.get("/tools")
    def tools() -> dict[str, Any]:
        return {"tools": TOOLS}

    @app.get("/audit/recent")
    def audit_recent(limit: int = 100) -> dict[str, Any]:
        events = audit.recent(limit=limit)
        return {"count": len(events), "events": events}

    @app.post("/tools/list_shared_skills")
    def list_shared_skills_tool(inp: SharedSkillListIn | None = None) -> dict[str, Any]:
        payload = inp or SharedSkillListIn()
        started = time.monotonic()
        try:
            result = list_shared_skills(settings.shared_skills_path, category=payload.category, limit=payload.limit)
            audit.record_tool_call(tool_name="list_shared_skills", arguments=payload.model_dump(), result_summary={"count": result["count"]}, status="ok", latency_ms=_elapsed_ms(started))
            result["latency_ms"] = _elapsed_ms(started)
            return result
        except SharedSkillsConfigError as exc:
            audit.record_tool_call(tool_name="list_shared_skills", arguments=payload.model_dump(), status="error", error_class=type(exc).__name__, latency_ms=_elapsed_ms(started))
            raise HTTPException(status_code=503, detail={"code": "directory_unavailable", "message": str(exc)}) from exc

    @app.post("/tools/describe_shared_skill")
    def describe_shared_skill_tool(inp: SharedSkillDescribeIn) -> dict[str, Any]:
        started = time.monotonic()
        try:
            result = describe_shared_skill(settings.shared_skills_path, inp.name)
            audit.record_tool_call(tool_name="describe_shared_skill", arguments=inp.model_dump(), result_summary={"skill": result["skill"]["name"]}, status="ok", latency_ms=_elapsed_ms(started))
            return result
        except SharedSkillNotFound as exc:
            audit.record_tool_call(tool_name="describe_shared_skill", arguments=inp.model_dump(), status="error", error_class="SharedSkillNotFound", latency_ms=_elapsed_ms(started))
            raise HTTPException(status_code=404, detail={"code": "skill_not_found", "message": "unknown shared skill"}) from exc
        except SharedSkillsConfigError as exc:
            audit.record_tool_call(tool_name="describe_shared_skill", arguments=inp.model_dump(), status="error", error_class=type(exc).__name__, latency_ms=_elapsed_ms(started))
            raise HTTPException(status_code=503, detail={"code": "directory_unavailable", "message": str(exc)}) from exc

    @app.post("/tools/search_shared_skills")
    def search_shared_skills_tool(inp: SharedSkillSearchIn) -> dict[str, Any]:
        started = time.monotonic()
        try:
            result = search_shared_skills(settings.shared_skills_path, inp.query, category=inp.category, limit=inp.limit)
            audit.record_tool_call(tool_name="search_shared_skills", arguments=inp.model_dump(), result_summary={"count": result["count"]}, status="ok", latency_ms=_elapsed_ms(started))
            return result
        except SharedSkillsConfigError as exc:
            audit.record_tool_call(tool_name="search_shared_skills", arguments=inp.model_dump(), status="error", error_class=type(exc).__name__, latency_ms=_elapsed_ms(started))
            raise HTTPException(status_code=503, detail={"code": "directory_unavailable", "message": str(exc)}) from exc

    @app.post("/tools/retrieve_shared_skill")
    def retrieve_shared_skill_tool(inp: SharedSkillRetrieveIn) -> dict[str, Any]:
        started = time.monotonic()
        args = {"name": inp.name, "include_bundle": inp.include_bundle}
        try:
            result = retrieve_shared_skill(
                settings.shared_skills_path,
                inp.name,
                content_roots=list(settings.shared_skill_content_roots),
                include_bundle=inp.include_bundle,
            )
            audit.record_tool_call(tool_name="retrieve_shared_skill", arguments=args, result_summary={"skill": result["skill"]["name"], "file_count": result["file_count"], "total_size_bytes": result["total_size_bytes"]}, status="ok", latency_ms=_elapsed_ms(started))
            return result
        except SharedSkillNotFound as exc:
            audit.record_tool_call(tool_name="retrieve_shared_skill", arguments=args, status="error", error_class="SharedSkillNotFound", latency_ms=_elapsed_ms(started))
            raise HTTPException(status_code=404, detail={"code": "skill_not_found", "message": "unknown shared skill or source unavailable"}) from exc
        except SharedSkillsConfigError as exc:
            audit.record_tool_call(tool_name="retrieve_shared_skill", arguments=args, status="error", error_class=type(exc).__name__, latency_ms=_elapsed_ms(started))
            raise HTTPException(status_code=503, detail={"code": "directory_unavailable", "message": str(exc)}) from exc

    @app.post("/tools/install_shared_skill")
    def install_shared_skill_tool(inp: SharedSkillInstallIn) -> dict[str, Any]:
        started = time.monotonic()
        args = inp.model_dump()
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
            audit.record_tool_call(tool_name="install_shared_skill", arguments=args, result_summary={"skill": bundle["skill"]["name"], "file_count": bundle["file_count"], "target_category": bundle["target_category"]}, status="ok", latency_ms=_elapsed_ms(started))
            return bundle
        except SharedSkillNotFound as exc:
            audit.record_tool_call(tool_name="install_shared_skill", arguments=args, status="error", error_class="SharedSkillNotFound", latency_ms=_elapsed_ms(started))
            raise HTTPException(status_code=404, detail={"code": "skill_not_found", "message": "unknown shared skill or source unavailable"}) from exc
        except SharedSkillsConfigError as exc:
            audit.record_tool_call(tool_name="install_shared_skill", arguments=args, status="error", error_class=type(exc).__name__, latency_ms=_elapsed_ms(started))
            raise HTTPException(status_code=503, detail={"code": "directory_unavailable", "message": str(exc)}) from exc

    return app


app = create_app()
