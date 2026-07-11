from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

from .audit import AuditLog
from .shared_skills import SharedSkillInstallError, install_shared_skill_bundle

URL = os.environ.get("SSR_MCP_URL", "http://127.0.0.1:8765").rstrip("/")
AUTH_TOKEN = os.environ.get("SSR_MCP_AUTH_TOKEN", "").strip()
SKILLS_ROOT = os.environ.get("SSR_MCP_SKILLS_ROOT", "")
AUDIT_LOG_PATH = os.environ.get("SSR_MCP_AUDIT_LOG", "")
ALLOW_SKILLS_ROOT_OVERRIDE = os.environ.get("SSR_MCP_ALLOW_SKILLS_ROOT_OVERRIDE", "").lower() in {
    "1",
    "true",
    "yes",
}


def _record_install_result(
    *,
    skill_name: str,
    status: str,
    result_summary: dict[str, Any] | None = None,
    error_class: str | None = None,
) -> None:
    if not AUDIT_LOG_PATH:
        return
    AuditLog(AUDIT_LOG_PATH).record_event(
        event_type="local_install",
        tool_name="install_shared_skill",
        arguments={"name": skill_name},
        result_summary=result_summary,
        status=status,
        error_class=error_class,
    )


mcp = FastMCP("shared-skills-registry")


def post_tool(name: str, payload: dict[str, Any] | None = None) -> Any:
    path = f"/tools/{name}"
    timeout = 180 if name in {"install_shared_skill", "retrieve_shared_skill"} else 65
    headers = {"Content-Type": "application/json"}
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    with httpx.Client(timeout=timeout) as client:
        response = client.post(
            f"{URL}{path}",
            content=json.dumps(payload or {}),
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
def list_shared_skills(category: str | None = None, limit: int = 50) -> Any:
    """List Shared Skills Registry metadata."""
    return post_tool("list_shared_skills", {"category": category, "limit": limit})


@mcp.tool()
def describe_shared_skill(name: str) -> Any:
    """Describe one Shared Skills Registry skill entry."""
    return post_tool("describe_shared_skill", {"name": name})


@mcp.tool()
def search_shared_skills(query: str, category: str | None = None, limit: int = 10) -> Any:
    """Search Shared Skills Registry metadata."""
    return post_tool("search_shared_skills", {"query": query, "category": category, "limit": limit})


@mcp.tool()
def retrieve_shared_skill(name: str, include_bundle: bool = True) -> Any:
    """Retrieve a checksum-bearing Shared Skills Registry source bundle."""
    return post_tool("retrieve_shared_skill", {"name": name, "include_bundle": include_bundle})


@mcp.tool()
def install_shared_skill(
    name: str,
    target_category: str | None = None,
    overwrite: bool = True,
    skills_root: str | None = None,
) -> Any:
    """Install a shared skill into a configured local skills directory."""
    bundle = post_tool(
        "install_shared_skill",
        {"name": name, "target_category": target_category, "overwrite": overwrite},
    )
    if not bundle.get("install_authorized"):
        raise RuntimeError("Shared Skills Registry install was not authorized")
    if skills_root and not ALLOW_SKILLS_ROOT_OVERRIDE:
        _record_install_result(
            skill_name=name,
            status="error",
            error_class="SkillsRootOverrideDisabled",
        )
        raise RuntimeError(
            "Per-call skills_root overrides are disabled; configure SSR_MCP_SKILLS_ROOT "
            "on the caller-local stdio adapter"
        )
    destination = skills_root if ALLOW_SKILLS_ROOT_OVERRIDE and skills_root else SKILLS_ROOT
    if not destination:
        _record_install_result(
            skill_name=name,
            status="error",
            error_class="SkillsRootNotConfigured",
        )
        raise RuntimeError("SSR_MCP_SKILLS_ROOT is required for local install")
    try:
        result = install_shared_skill_bundle(
            bundle,
            skills_root=Path(destination),
            target_category=target_category or bundle.get("target_category"),
            overwrite=overwrite,
        )
        _record_install_result(
            skill_name=name,
            status="ok",
            result_summary={
                "installed_path": result["installed_path"],
                "file_count": result["file_count"],
            },
        )
        return result
    except SharedSkillInstallError as exc:
        _record_install_result(
            skill_name=name,
            status="error",
            error_class=type(exc).__name__,
        )
        raise RuntimeError(f"Shared Skills Registry install failed safely: {exc}") from exc


def main() -> None:
    """Run the MCP server over stdin/stdout."""
    mcp.run()


if __name__ == "__main__":
    main()
