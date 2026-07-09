from __future__ import annotations

from pathlib import Path

import pytest

from shared_skills_registry_mcp.shared_skills import (
    SharedSkillInstallError,
    SharedSkillsConfigError,
    describe_shared_skill,
    install_shared_skill_bundle,
    list_shared_skills,
    load_shared_skills,
    retrieve_shared_skill,
    search_shared_skills,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "shared_skills.yaml"


def test_load_list_search_describe_public_example_registry():
    directory = load_shared_skills(REGISTRY)
    assert directory["version"] == 1
    assert directory["skills"][0]["name"] == "demo-research-brief"

    listed = list_shared_skills(REGISTRY)
    assert listed["count"] == 1
    assert listed["skills"][0]["retrieval_available"] is True
    assert listed["skills"][0]["execution_available"] is False

    searched = search_shared_skills(REGISTRY, "research brief")
    assert searched["count"] == 1
    assert searched["skills"][0]["name"] == "demo-research-brief"

    described = describe_shared_skill(REGISTRY, "demo-research-brief")
    assert described["skill"]["category"] == "demo"


def test_retrieve_bundle_includes_skill_and_allowed_support_files():
    bundle = retrieve_shared_skill(REGISTRY, "demo-research-brief", content_roots=[ROOT], include_bundle=True)
    paths = [item["path"] for item in bundle["files"]]
    assert paths == ["SKILL.md", "templates/brief.md"]
    assert bundle["file_count"] == 2
    assert all(item["sha256"] for item in bundle["files"])
    assert bundle["execution_available"] is False
    assert bundle["install_available"] is True


def test_install_bundle_writes_to_configured_scratch_skills_root(tmp_path):
    bundle = retrieve_shared_skill(REGISTRY, "demo-research-brief", content_roots=[ROOT], include_bundle=True)
    result = install_shared_skill_bundle(bundle, skills_root=tmp_path / "skills")

    install_dir = tmp_path / "skills" / "demo" / "demo-research-brief"
    assert result["installed"] is True
    assert result["installed_path"] == str(install_dir)
    assert (install_dir / "SKILL.md").read_text(encoding="utf-8").startswith("---\nname: demo-research-brief")
    assert (install_dir / "templates" / "brief.md").exists()


def test_install_rejects_checksum_mismatch(tmp_path):
    bundle = retrieve_shared_skill(REGISTRY, "demo-research-brief", content_roots=[ROOT], include_bundle=True)
    bundle["files"][0]["content"] += "tampered"
    with pytest.raises(SharedSkillInstallError, match="checksum mismatch"):
        install_shared_skill_bundle(bundle, skills_root=tmp_path / "skills")


def test_registry_rejects_duplicate_skill_names(tmp_path):
    registry = tmp_path / "shared_skills.yaml"
    registry.write_text(
        """
version: 1
skills:
  - name: duplicate
    title: First
    summary: First skill.
    category: demo
    owner: example
    source: local
    docs_path: examples/skills/demo-research-brief/SKILL.md
    applicability: demo
    lifecycle_status: active
    install_guidance: demo
  - name: duplicate
    title: Second
    summary: Second skill.
    category: demo
    owner: example
    source: local
    docs_path: examples/skills/demo-research-brief/SKILL.md
    applicability: demo
    lifecycle_status: active
    install_guidance: demo
""".lstrip(),
        encoding="utf-8",
    )
    with pytest.raises(SharedSkillsConfigError, match="duplicate"):
        load_shared_skills(registry)
