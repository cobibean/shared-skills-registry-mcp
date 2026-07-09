#!/usr/bin/env python3
"""Protocol-level smoke client for a running Shared Skills Registry HTTP service."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

EXPECTED_TOOLS = {
    "list_shared_skills",
    "search_shared_skills",
    "describe_shared_skill",
    "retrieve_shared_skill",
    "install_shared_skill",
}


def _json_result(result: Any) -> dict[str, Any]:
    if result.isError:
        messages = [getattr(block, "text", str(block)) for block in result.content]
        raise RuntimeError("MCP tool returned an error: " + " | ".join(messages))
    blocks = [block.text for block in result.content if getattr(block, "type", None) == "text"]
    if len(blocks) != 1:
        raise RuntimeError(f"Expected one MCP text result, received {len(blocks)}")
    value = json.loads(blocks[0])
    if not isinstance(value, dict):
        raise RuntimeError("Expected an MCP JSON object result")
    return value


async def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    skills_root = Path(args.skills_root).resolve()
    audit_log = Path(args.audit_log).resolve()

    env = {
        "SSR_MCP_URL": args.url.rstrip("/"),
        "SSR_MCP_SKILLS_ROOT": str(skills_root),
        "SSR_MCP_AUDIT_LOG": str(audit_log),
    }
    if args.adapter:
        adapter = Path(args.adapter).resolve()
        if not adapter.is_file():
            raise RuntimeError(f"stdio adapter not found: {adapter}")
        command_args = [str(adapter)]
    else:
        command_args = ["-m", "shared_skills_registry_mcp.stdio_server"]
    params = StdioServerParameters(command=sys.executable, args=command_args, env=env)

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(
            read_stream,
            write_stream,
            read_timeout_seconds=timedelta(seconds=20),
        ) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()
            tool_names = {tool.name for tool in tools.tools}
            if tool_names != EXPECTED_TOOLS:
                raise RuntimeError(f"Unexpected tool set: {sorted(tool_names)}")

            listed = _json_result(await session.call_tool("list_shared_skills", {}))
            searched = _json_result(
                await session.call_tool("search_shared_skills", {"query": args.search_query})
            )
            described = _json_result(
                await session.call_tool("describe_shared_skill", {"name": args.skill})
            )
            retrieved = _json_result(
                await session.call_tool(
                    "retrieve_shared_skill",
                    {"name": args.skill, "include_bundle": True},
                )
            )
            installed = _json_result(
                await session.call_tool(
                    "install_shared_skill",
                    {"name": args.skill, "overwrite": True},
                )
            )

    installed_path = Path(installed["installed_path"])
    if not installed_path.is_dir() or not (installed_path / "SKILL.md").is_file():
        raise RuntimeError(f"MCP reported installation but SKILL.md is missing: {installed_path}")
    if installed["file_count"] != retrieved["file_count"]:
        raise RuntimeError("Retrieved and installed file counts differ")
    if not audit_log.is_file():
        raise RuntimeError(f"Local install audit was not written: {audit_log}")

    return {
        "ok": True,
        "server": initialized.serverInfo.name,
        "tool_count": len(tool_names),
        "registry_count": listed["count"],
        "search_count": searched["count"],
        "described_skill": described["skill"]["name"],
        "retrieved_file_count": retrieved["file_count"],
        "installed_path": str(installed_path),
        "installed_file_count": installed["file_count"],
        "audit_written": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Exercise Open SSR through a real generic MCP stdio client session."
    )
    parser.add_argument("--url", default=os.environ.get("SSR_MCP_URL", "http://127.0.0.1:8765"))
    parser.add_argument(
        "--adapter",
        help="Optional legacy stdio_server.py path; defaults to the installed package module",
    )
    parser.add_argument("--skills-root", required=True, help="Scratch/local destination for the installed skill")
    parser.add_argument("--audit-log", required=True, help="Caller-local install audit JSONL path")
    parser.add_argument("--skill", default="project-memory")
    parser.add_argument("--search-query", default="project continuity")
    return parser.parse_args()


def main() -> int:
    try:
        summary = asyncio.run(run_smoke(parse_args()))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
