from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from shared_skills_registry_mcp.app import create_app
from shared_skills_registry_mcp.audit import AuditLog
from shared_skills_registry_mcp.config import Settings

ROOT = Path(__file__).resolve().parents[1]


def _client(tmp_path) -> tuple[TestClient, Path]:
    audit_path = tmp_path / "audit" / "ssr_audit.jsonl"
    app = create_app(
        Settings(
            shared_skills_path=str(ROOT / "config" / "shared_skills.yaml"),
            shared_skill_content_roots=(str(ROOT),),
            audit_log_path=str(audit_path),
        )
    )
    return TestClient(app), audit_path


def _events(audit_path: Path) -> list[dict]:
    return [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_tool_calls_write_audit_events(tmp_path):
    client, audit_path = _client(tmp_path)

    assert client.post("/tools/list_shared_skills", json={}).status_code == 200
    assert client.post("/tools/retrieve_shared_skill", json={"name": "demo-research-brief"}).status_code == 200
    assert client.post("/tools/install_shared_skill", json={"name": "demo-research-brief"}).status_code == 200

    events = _events(audit_path)
    assert [e["tool_name"] for e in events] == ["list_shared_skills", "retrieve_shared_skill", "install_shared_skill"]
    assert all(e["status"] == "ok" and e["event_type"] == "tool_call" for e in events)
    retrieve = events[1]
    assert retrieve["result_summary"]["skill"] == "demo-research-brief"
    assert retrieve["result_summary"]["file_count"] == 2
    # Audit records must never carry bundle content.
    assert "content" not in json.dumps(events)


def test_failed_tool_call_writes_error_event(tmp_path):
    client, audit_path = _client(tmp_path)

    assert client.post("/tools/describe_shared_skill", json={"name": "no-such-skill"}).status_code == 404

    events = _events(audit_path)
    assert events[-1]["status"] == "error"
    assert events[-1]["error_class"] == "SharedSkillNotFound"


def test_audit_recent_endpoint_returns_newest_first(tmp_path):
    client, _ = _client(tmp_path)

    client.post("/tools/list_shared_skills", json={})
    client.post("/tools/search_shared_skills", json={"query": "research"})

    response = client.get("/audit/recent", params={"limit": 10})
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
    assert payload["events"][0]["tool_name"] == "search_shared_skills"
    assert payload["events"][1]["tool_name"] == "list_shared_skills"


def test_audit_redacts_secret_like_keys_and_omits_payloads(tmp_path):
    audit = AuditLog(tmp_path / "audit.jsonl")
    audit.record_tool_call(
        tool_name="example",
        arguments={"name": "demo", "api_key": "abc123", "nested": {"authorization": "Bearer xyz"}},
        result_summary={"files": [{"path": "SKILL.md", "content": "full text"}]},
        status="ok",
    )
    event = audit.recent()[0]
    assert event["arguments"]["api_key"] == "[REDACTED]"
    assert event["arguments"]["nested"]["authorization"] == "[REDACTED]"
    assert event["result_summary"]["files"] == "[OMITTED]"
