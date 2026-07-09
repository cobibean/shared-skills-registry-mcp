from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from shared_skills_registry_mcp.app import create_app
from shared_skills_registry_mcp.config import Settings

ROOT = Path(__file__).resolve().parents[1]


def test_ssr_http_tools_match_private_endpoint_shape(tmp_path):
    app = create_app(
        Settings(
            shared_skills_path=str(ROOT / "config" / "shared_skills.yaml"),
            shared_skill_content_roots=(str(ROOT),),
            audit_log_path=str(tmp_path / "ssr_audit.jsonl"),
        )
    )
    client = TestClient(app)

    health = client.get("/healthz")
    assert health.status_code == 200
    assert "list_shared_skills" in health.json()["tools"]

    listed = client.post("/tools/list_shared_skills", json={})
    assert listed.status_code == 200
    assert listed.json()["count"] == 14
    assert "shared-skills-registry-access" in {skill["name"] for skill in listed.json()["skills"]}

    searched = client.post("/tools/search_shared_skills", json={"query": "research"})
    assert searched.status_code == 200
    assert searched.json()["count"] == 1

    described = client.post("/tools/describe_shared_skill", json={"name": "demo-research-brief"})
    assert described.status_code == 200
    assert described.json()["skill"]["retrieval_available"] is True

    retrieved = client.post("/tools/retrieve_shared_skill", json={"name": "demo-research-brief", "include_bundle": True})
    assert retrieved.status_code == 200
    assert [item["path"] for item in retrieved.json()["files"]] == ["SKILL.md", "templates/brief.md"]

    install = client.post("/tools/install_shared_skill", json={"name": "demo-research-brief", "overwrite": True})
    assert install.status_code == 200
    payload = install.json()
    assert payload["install_authorized"] is True
    assert payload["target_category"] == "example"
