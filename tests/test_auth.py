from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from shared_skills_registry_mcp.app import create_app
from shared_skills_registry_mcp.cli import generate_token
from shared_skills_registry_mcp.config import Settings

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "unit-test-token-c8Qm2vXk9LpR4tYw"

PROTECTED_REQUESTS = (
    ("GET", "/tools", None),
    ("POST", "/tools/list_shared_skills", {}),
    ("POST", "/tools/search_shared_skills", {"query": "research"}),
    ("POST", "/tools/describe_shared_skill", {"name": "demo-research-brief"}),
    ("POST", "/tools/retrieve_shared_skill", {"name": "demo-research-brief"}),
    ("POST", "/tools/install_shared_skill", {"name": "demo-research-brief"}),
    ("GET", "/registry/skills", None),
    ("PUT", "/registry/skills/anything", {}),
    ("DELETE", "/registry/skills/anything", None),
    ("GET", "/audit/recent", None),
)


def _client(tmp_path: Path, auth_token: str | None) -> TestClient:
    app = create_app(
        Settings(
            shared_skills_path=str(ROOT / "config" / "shared_skills.yaml"),
            shared_skill_content_roots=(str(ROOT),),
            audit_log_path=str(tmp_path / "ssr_audit.jsonl"),
            auth_token=auth_token,
        )
    )
    return TestClient(app)


def _request(client: TestClient, method: str, path: str, body, headers=None):
    kwargs = {"headers": headers or {}}
    if body is not None:
        kwargs["json"] = body
    return client.request(method, path, **kwargs)


def test_protected_routes_reject_missing_and_wrong_tokens(tmp_path):
    client = _client(tmp_path, TOKEN)
    for method, path, body in PROTECTED_REQUESTS:
        missing = _request(client, method, path, body)
        assert missing.status_code == 401, (method, path)
        assert missing.headers["www-authenticate"] == "Bearer"
        assert missing.json()["detail"]["code"] == "invalid_token"

        wrong = _request(client, method, path, body, headers={"Authorization": "Bearer wrong-token"})
        assert wrong.status_code == 401, (method, path)

        malformed = _request(client, method, path, body, headers={"Authorization": TOKEN})
        assert malformed.status_code == 401, (method, path)


def test_open_routes_never_require_token(tmp_path):
    client = _client(tmp_path, TOKEN)
    assert client.get("/healthz").status_code == 200
    assert client.get("/ui").status_code == 200
    root = client.get("/", follow_redirects=False)
    assert root.status_code in {302, 307}


def test_correct_token_grants_access_to_every_protected_surface(tmp_path):
    client = _client(tmp_path, TOKEN)
    headers = {"Authorization": f"Bearer {TOKEN}"}

    listed = client.post("/tools/list_shared_skills", json={}, headers=headers)
    assert listed.status_code == 200
    assert listed.json()["count"] == 14

    tools = client.get("/tools", headers=headers)
    assert tools.status_code == 200

    registry = client.get("/registry/skills", headers=headers)
    assert registry.status_code == 200

    audit = client.get("/audit/recent", headers=headers)
    assert audit.status_code == 200


def test_auth_failures_are_audited_without_leaking_the_token(tmp_path):
    client = _client(tmp_path, TOKEN)
    client.post("/tools/list_shared_skills", json={})
    client.get("/audit/recent", headers={"Authorization": "Bearer wrong-token"})

    audit_path = tmp_path / "ssr_audit.jsonl"
    raw = audit_path.read_text(encoding="utf-8")
    events = [json.loads(line) for line in raw.splitlines()]
    failures = [event for event in events if event["event_type"] == "auth_failure"]
    assert [event["error_class"] for event in failures] == ["MissingAuthToken", "InvalidAuthToken"]
    assert all(event["status"] == "error" for event in failures)
    assert failures[0]["arguments"]["path"] == "/tools/list_shared_skills"
    assert TOKEN not in raw
    assert "wrong-token" not in raw


def test_unset_token_keeps_current_open_behavior(tmp_path):
    client = _client(tmp_path, None)
    assert client.post("/tools/list_shared_skills", json={}).status_code == 200
    assert client.get("/audit/recent").status_code == 200
    assert client.get("/registry/skills").status_code == 200


def test_generate_token_emits_env_line_with_strong_token(capsys):
    generate_token()
    captured = capsys.readouterr()
    line = captured.out.strip().splitlines()[0]
    assert line.startswith("SSR_MCP_AUTH_TOKEN=")
    token = line.split("=", 1)[1]
    assert len(token) >= 40
    assert all(ch.isalnum() or ch in "-_" for ch in token)
    assert "Treat it like a password" in captured.err
