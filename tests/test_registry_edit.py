from __future__ import annotations

import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from shared_skills_registry_mcp.app import create_app
from shared_skills_registry_mcp.config import Settings
from shared_skills_registry_mcp.shared_skills import load_shared_skills

ROOT = Path(__file__).resolve().parents[1]


def _client(tmp_path) -> tuple[TestClient, Path]:
    registry = tmp_path / "config" / "shared_skills.yaml"
    registry.parent.mkdir(parents=True)
    shutil.copy(ROOT / "config" / "shared_skills.yaml", registry)
    shutil.copytree(ROOT / "examples", tmp_path / "examples")
    shutil.copytree(ROOT / "seed", tmp_path / "seed")
    app = create_app(
        Settings(
            shared_skills_path=str(registry),
            shared_skill_content_roots=(str(tmp_path),),
            audit_log_path=str(tmp_path / "audit.jsonl"),
        )
    )
    return TestClient(app), registry


def _entry(**overrides) -> dict:
    entry = {
        "name": "second-skill",
        "title": "Second Skill",
        "summary": "Another demo skill entry.",
        "category": "demo",
        "owner": "example",
        "source": "local-example",
        "docs_path": "examples/skills/demo-research-brief/SKILL.md",
        "applicability": "Testing registry editing.",
        "lifecycle_status": "draft",
        "install_guidance": "Install into a scratch directory.",
        "tags": ["demo"],
    }
    entry.update(overrides)
    return entry


def test_registry_listing_includes_non_active_and_source_flag(tmp_path):
    client, _ = _client(tmp_path)
    assert client.put("/registry/skills/second-skill", json=_entry()).status_code == 200
    missing = _entry(name="ghost-skill", docs_path="examples/skills/nope/SKILL.md")
    assert client.put("/registry/skills/ghost-skill", json=missing).status_code == 200

    listing = client.get("/registry/skills").json()
    by_name = {s["name"]: s for s in listing["skills"]}
    assert len(by_name) == 16
    assert {"demo-research-brief", "shared-skills-registry-access", "second-skill", "ghost-skill"} <= set(by_name)
    assert by_name["second-skill"]["lifecycle_status"] == "draft"
    assert by_name["second-skill"]["source_exists"] is True
    assert by_name["ghost-skill"]["source_exists"] is False

    # draft entries stay hidden from the agent-facing tool surface
    public = client.post("/tools/list_shared_skills", json={}).json()
    assert public["count"] == 14
    assert "second-skill" not in {s["name"] for s in public["skills"]}


def test_upsert_updates_existing_entry_and_registry_stays_loadable(tmp_path):
    client, registry = _client(tmp_path)
    client.put("/registry/skills/second-skill", json=_entry())
    updated = client.put("/registry/skills/second-skill", json=_entry(title="Renamed Title", lifecycle_status="active"))
    assert updated.status_code == 200
    assert updated.json()["created"] is False

    directory = load_shared_skills(registry)
    by_name = {s["name"]: s for s in directory["skills"]}
    assert by_name["second-skill"]["title"] == "Renamed Title"
    assert by_name["second-skill"]["lifecycle_status"] == "active"


def test_upsert_rejects_invalid_name_and_path_mismatch(tmp_path):
    client, registry = _client(tmp_path)
    bad = client.put("/registry/skills/Bad%20Name", json=_entry(name="Bad Name"))
    assert bad.status_code == 422

    mismatch = client.put("/registry/skills/other-name", json=_entry())
    assert mismatch.status_code == 400

    # registry untouched
    assert len(load_shared_skills(registry)["skills"]) == 14


def test_delete_removes_entry_and_unknown_404s(tmp_path):
    client, registry = _client(tmp_path)
    client.put("/registry/skills/second-skill", json=_entry())
    deleted = client.delete("/registry/skills/second-skill")
    assert deleted.status_code == 200
    assert deleted.json()["remaining"] == 14
    assert client.delete("/registry/skills/second-skill").status_code == 404
    assert len(load_shared_skills(registry)["skills"]) == 14


def test_registry_edits_are_audited(tmp_path):
    client, _ = _client(tmp_path)
    client.put("/registry/skills/second-skill", json=_entry())
    client.delete("/registry/skills/second-skill")

    events = client.get("/audit/recent").json()["events"]
    tools = [e["tool_name"] for e in events if e["event_type"] == "registry_edit"]
    assert tools == ["delete_registry_skill", "upsert_registry_skill"]


def test_ui_route_serves_control_panel(tmp_path):
    client, _ = _client(tmp_path)
    page = client.get("/ui")
    assert page.status_code == 200
    assert "Shared Skills Registry" in page.text
    root = client.get("/", follow_redirects=False)
    assert root.status_code == 307
    assert root.headers["location"] == "/ui"
