#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

from shared_skills_registry_mcp.shared_skills import SharedSkillInstallError, install_shared_skill_bundle

URL = os.environ.get("SSR_MCP_URL", "http://127.0.0.1:8765").rstrip("/")
SKILLS_ROOT = os.environ.get("SSR_MCP_SKILLS_ROOT", "")

mcp = FastMCP("shared-skills-registry")


def post_tool(name: str, payload: dict[str, Any] | None = None) -> Any:
    path = f"/tools/{name}"
    with httpx.Client(timeout=180 if name in {"install_shared_skill", "retrieve_shared_skill"} else 65) as client:
        response = client.post(f"{URL}{path}", content=json.dumps(payload or {}), headers={"Content-Type": "application/json"})
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
def install_shared_skill(name: str, target_category: str | None = None, overwrite: bool = True, skills_root: str | None = None) -> Any:
    """Install a shared skill into a configured local skills directory."""
    bundle = post_tool("install_shared_skill", {"name": name, "target_category": target_category, "overwrite": overwrite})
    if not bundle.get("install_authorized"):
        raise RuntimeError("Shared Skills Registry install was not authorized")
    destination = skills_root or SKILLS_ROOT
    if not destination:
        raise RuntimeError("SSR_MCP_SKILLS_ROOT or skills_root is required for local install")
    try:
        return install_shared_skill_bundle(
            bundle,
            skills_root=Path(destination),
            target_category=target_category or bundle.get("target_category"),
            overwrite=overwrite,
        )
    except SharedSkillInstallError as exc:
        raise RuntimeError(f"Shared Skills Registry install failed safely: {exc}") from exc


if __name__ == "__main__":
    mcp.run()
