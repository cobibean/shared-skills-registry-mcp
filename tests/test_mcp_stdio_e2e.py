from __future__ import annotations

import hashlib
import json
import os
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
from typing import Iterator

import httpx
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TOOLS = {
    "list_shared_skills",
    "search_shared_skills",
    "describe_shared_skill",
    "retrieve_shared_skill",
    "install_shared_skill",
}


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _tool_json(result: CallToolResult) -> dict:
    assert not result.isError
    text_blocks = [
        getattr(block, "text", "")
        for block in result.content
        if getattr(block, "type", None) == "text"
    ]
    assert len(text_blocks) == 1
    value = json.loads(text_blocks[0])
    assert isinstance(value, dict)
    return value


@contextmanager
def _running_http_service(tmp_path: Path, auth_token: str | None = None) -> Iterator[tuple[str, Path]]:
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    audit_path = tmp_path / "server-audit.jsonl"
    log_path = tmp_path / "http-service.log"
    env = os.environ.copy()
    env.pop("SSR_MCP_AUTH_TOKEN", None)
    env.update(
        {
            "SSR_MCP_AUDIT_LOG": str(audit_path),
            "SSR_MCP_SHARED_SKILLS": str(ROOT / "config" / "shared_skills.yaml"),
            "SSR_MCP_SHARED_SKILL_CONTENT_ROOTS": str(ROOT),
        }
    )
    if auth_token:
        env["SSR_MCP_AUTH_TOKEN"] = auth_token
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "shared_skills_registry_mcp.app:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--log-level",
                "warning",
            ],
            cwd=ROOT,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            deadline = time.monotonic() + 15
            last_error: Exception | None = None
            ready = False
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    break
                try:
                    response = httpx.get(f"{url}/healthz", timeout=0.5)
                    if response.status_code == 200:
                        ready = True
                        break
                except Exception as exc:  # startup race, retained for failure context
                    last_error = exc
                time.sleep(0.05)
            if not ready:
                output = log_path.read_text(encoding="utf-8", errors="replace")
                raise AssertionError(
                    f"Open SSR HTTP service did not become ready; exit={process.poll()}, "
                    f"last_error={last_error!r}, log={output[-4000:]}"
                )
            yield url, audit_path
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


@pytest.mark.asyncio
async def test_real_mcp_stdio_protocol_lists_retrieves_and_installs(tmp_path: Path) -> None:
    with _running_http_service(tmp_path) as (url, server_audit):
        install_root = tmp_path / "installed-skills"
        local_audit = tmp_path / "local-install-audit.jsonl"
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "shared_skills_registry_mcp.stdio_server"],
            cwd=ROOT,
            env={
                "PYTHONPATH": str(ROOT / "src"),
                "SSR_MCP_URL": url,
                "SSR_MCP_SKILLS_ROOT": str(install_root),
                "SSR_MCP_AUDIT_LOG": str(local_audit),
            },
        )

        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(
                read_stream,
                write_stream,
                read_timeout_seconds=timedelta(seconds=20),
            ) as session:
                initialized = await session.initialize()
                assert initialized.serverInfo.name == "shared-skills-registry"

                tools = await session.list_tools()
                assert {tool.name for tool in tools.tools} == EXPECTED_TOOLS

                listed = _tool_json(await session.call_tool("list_shared_skills", {}))
                assert listed["count"] == 14
                assert any(skill["name"] == "shared-skills-registry-access" for skill in listed["skills"])

                searched = _tool_json(
                    await session.call_tool("search_shared_skills", {"query": "project continuity"})
                )
                assert any(skill["name"] == "project-memory" for skill in searched["skills"])

                described = _tool_json(
                    await session.call_tool("describe_shared_skill", {"name": "project-memory"})
                )
                assert described["skill"]["name"] == "project-memory"
                assert described["skill"]["docs_path"] == "skills/project-memory/SKILL.md"
                assert described["skill"]["retrieval_available"] is True

                rich_bundle = _tool_json(
                    await session.call_tool(
                        "retrieve_shared_skill",
                        {"name": "systematic-debugging", "include_bundle": True},
                    )
                )
                assert rich_bundle["file_count"] > 1
                assert any(item["path"].startswith("references/") for item in rich_bundle["files"])
                assert any(item["path"].startswith("scripts/") for item in rich_bundle["files"])

                project_bundle = _tool_json(
                    await session.call_tool(
                        "retrieve_shared_skill",
                        {"name": "project-memory", "include_bundle": True},
                    )
                )
                installed = _tool_json(
                    await session.call_tool(
                        "install_shared_skill",
                        {"name": "project-memory", "overwrite": True},
                    )
                )
                protocol_install_path = Path(installed["installed_path"])
                stale_file = protocol_install_path / "scripts" / "stale-from-previous-version.py"
                stale_file.parent.mkdir(parents=True, exist_ok=True)
                stale_file.write_text("raise RuntimeError('stale')\n", encoding="utf-8")
                installed = _tool_json(
                    await session.call_tool(
                        "install_shared_skill",
                        {"name": "project-memory", "overwrite": True},
                    )
                )

        installed_path = Path(installed["installed_path"])
        assert installed_path == install_root / "project-continuity" / "project-memory"
        assert installed["file_count"] == project_bundle["file_count"]
        assert installed["reload_required"] is True
        assert not (installed_path / "scripts" / "stale-from-previous-version.py").exists()

        expected_files = {item["path"]: item for item in project_bundle["files"]}
        assert set(installed["files"]) == set(expected_files)
        for relative_path, source in expected_files.items():
            destination = installed_path / relative_path
            assert destination.is_file()
            assert hashlib.sha256(destination.read_bytes()).hexdigest() == source["sha256"]

        assert local_audit.is_file()
        local_events = [json.loads(line) for line in local_audit.read_text().splitlines()]
        assert len(local_events) == 2
        assert all(event["event_type"] == "local_install" for event in local_events)
        assert all(event["status"] == "ok" for event in local_events)

        assert server_audit.is_file()
        server_events = [json.loads(line) for line in server_audit.read_text().splitlines()]
        tool_names = [event["tool_name"] for event in server_events]
        assert tool_names == [
            "list_shared_skills",
            "search_shared_skills",
            "describe_shared_skill",
            "retrieve_shared_skill",
            "retrieve_shared_skill",
            "install_shared_skill",
            "install_shared_skill",
        ]


@pytest.mark.asyncio
async def test_mcp_install_without_local_root_fails_closed(tmp_path: Path) -> None:
    with _running_http_service(tmp_path) as (url, server_audit):
        local_audit = tmp_path / "must-not-exist.jsonl"
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "shared_skills_registry_mcp.stdio_server"],
            cwd=ROOT,
            env={
                "PYTHONPATH": str(ROOT / "src"),
                "SSR_MCP_URL": url,
                "SSR_MCP_AUDIT_LOG": str(local_audit),
            },
        )
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(
                read_stream,
                write_stream,
                read_timeout_seconds=timedelta(seconds=20),
            ) as session:
                await session.initialize()
                result = await session.call_tool(
                    "install_shared_skill",
                    {"name": "project-memory"},
                )

        assert result.isError is True
        error_text = "\n".join(
            getattr(block, "text", "")
            for block in result.content
            if getattr(block, "type", None) == "text"
        )
        assert "SSR_MCP_SKILLS_ROOT is required" in error_text
        assert local_audit.is_file()
        local_events = [json.loads(line) for line in local_audit.read_text().splitlines()]
        assert local_events[-1]["status"] == "error"
        assert local_events[-1]["error_class"] == "SkillsRootNotConfigured"
        assert not (tmp_path / "project-memory").exists()

        events = [json.loads(line) for line in server_audit.read_text().splitlines()]
        assert [event["tool_name"] for event in events] == ["install_shared_skill"]


@pytest.mark.asyncio
async def test_mcp_rejects_per_call_skills_root_override_by_default(tmp_path: Path) -> None:
    with _running_http_service(tmp_path) as (url, _server_audit):
        configured_root = tmp_path / "configured-skills"
        attempted_override = tmp_path / "model-chosen-skills"
        local_audit = tmp_path / "override-audit.jsonl"
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "shared_skills_registry_mcp.stdio_server"],
            cwd=ROOT,
            env={
                "PYTHONPATH": str(ROOT / "src"),
                "SSR_MCP_URL": url,
                "SSR_MCP_SKILLS_ROOT": str(configured_root),
                "SSR_MCP_AUDIT_LOG": str(local_audit),
            },
        )
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(
                read_stream,
                write_stream,
                read_timeout_seconds=timedelta(seconds=20),
            ) as session:
                await session.initialize()
                result = await session.call_tool(
                    "install_shared_skill",
                    {
                        "name": "project-memory",
                        "skills_root": str(attempted_override),
                    },
                )

        assert result.isError is True
        error_text = "\n".join(
            getattr(block, "text", "")
            for block in result.content
            if getattr(block, "type", None) == "text"
        )
        assert "Per-call skills_root overrides are disabled" in error_text
        assert not configured_root.exists()
        assert not attempted_override.exists()
        events = [json.loads(line) for line in local_audit.read_text().splitlines()]
        assert events[-1]["error_class"] == "SkillsRootOverrideDisabled"


@pytest.mark.asyncio
async def test_real_mcp_stdio_with_auth_token_enforced_end_to_end(tmp_path: Path) -> None:
    token = "e2e-test-token-mK7dQx2nRb8sVw4z"
    with _running_http_service(tmp_path, auth_token=token) as (url, server_audit):
        assert httpx.get(f"{url}/healthz", timeout=5).status_code == 200
        unauthenticated = httpx.post(f"{url}/tools/list_shared_skills", json={}, timeout=5)
        assert unauthenticated.status_code == 401
        assert unauthenticated.headers["www-authenticate"] == "Bearer"

        install_root = tmp_path / "installed-skills"
        base_env = {
            "PYTHONPATH": str(ROOT / "src"),
            "SSR_MCP_URL": url,
            "SSR_MCP_SKILLS_ROOT": str(install_root),
        }

        tokenless_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "shared_skills_registry_mcp.stdio_server"],
            cwd=ROOT,
            env=base_env,
        )
        async with stdio_client(tokenless_params) as (read_stream, write_stream):
            async with ClientSession(
                read_stream,
                write_stream,
                read_timeout_seconds=timedelta(seconds=20),
            ) as session:
                await session.initialize()
                denied = await session.call_tool("list_shared_skills", {})
        assert denied.isError is True
        denied_text = "\n".join(
            getattr(block, "text", "")
            for block in denied.content
            if getattr(block, "type", None) == "text"
        )
        assert "401" in denied_text

        authed_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "shared_skills_registry_mcp.stdio_server"],
            cwd=ROOT,
            env={**base_env, "SSR_MCP_AUTH_TOKEN": token},
        )
        async with stdio_client(authed_params) as (read_stream, write_stream):
            async with ClientSession(
                read_stream,
                write_stream,
                read_timeout_seconds=timedelta(seconds=20),
            ) as session:
                await session.initialize()
                listed = _tool_json(await session.call_tool("list_shared_skills", {}))
                assert listed["count"] == 14
                installed = _tool_json(
                    await session.call_tool("install_shared_skill", {"name": "project-memory"})
                )
        assert (Path(installed["installed_path"]) / "SKILL.md").is_file()

        server_raw = server_audit.read_text(encoding="utf-8")
        server_events = [json.loads(line) for line in server_raw.splitlines()]
        assert [e["error_class"] for e in server_events if e["event_type"] == "auth_failure"] == [
            "MissingAuthToken",
            "MissingAuthToken",
        ]
        assert [e["tool_name"] for e in server_events if e["event_type"] == "tool_call"] == [
            "list_shared_skills",
            "install_shared_skill",
        ]
        assert token not in server_raw


@pytest.mark.asyncio
async def test_mcp_backend_failure_is_a_tool_error_not_protocol_corruption(tmp_path: Path) -> None:
    unreachable_url = f"http://127.0.0.1:{_free_port()}"
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "shared_skills_registry_mcp.stdio_server"],
        cwd=ROOT,
        env={
            "PYTHONPATH": str(ROOT / "src"),
            "SSR_MCP_URL": unreachable_url,
            "SSR_MCP_SKILLS_ROOT": str(tmp_path / "skills"),
        },
    )
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(
            read_stream,
            write_stream,
            read_timeout_seconds=timedelta(seconds=20),
        ) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert {tool.name for tool in tools.tools} == EXPECTED_TOOLS
            result = await session.call_tool("list_shared_skills", {})

    assert result.isError is True
    error_text = "\n".join(
        getattr(block, "text", "")
        for block in result.content
        if getattr(block, "type", None) == "text"
    )
    assert "ConnectError" in error_text or "connection" in error_text.lower()
