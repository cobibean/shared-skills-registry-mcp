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
APPROVED_SEEDS = {
    "project-memory",
    "website-copywriting",
    "codebase-design",
    "diagnosing-bugs",
    "domain-modeling",
    "prototype",
    "tdd",
    "triage",
    "handoff",
    "teach",
    "writing-great-skills",
    "systematic-debugging",
}
COMPANION_SKILLS = {"shared-skills-registry-access"}
EXAMPLE_SKILLS = {"demo-research-brief"}
EXPECTED_SKILLS = APPROVED_SEEDS | COMPANION_SKILLS | EXAMPLE_SKILLS


def test_load_list_search_describe_public_seed_registry():
    directory = load_shared_skills(REGISTRY)
    assert directory["version"] == 1
    assert {skill["name"] for skill in directory["skills"]} == EXPECTED_SKILLS

    listed = list_shared_skills(REGISTRY)
    assert listed["count"] == len(EXPECTED_SKILLS)
    assert {skill["name"] for skill in listed["skills"]} == EXPECTED_SKILLS
    assert all(skill["retrieval_available"] is True for skill in listed["skills"])
    assert all(skill["execution_available"] is False for skill in listed["skills"])

    searched = search_shared_skills(REGISTRY, "research brief")
    assert searched["count"] >= 1
    assert "demo-research-brief" in {skill["name"] for skill in searched["skills"]}

    described = describe_shared_skill(REGISTRY, "demo-research-brief")
    assert described["skill"]["category"] == "example"
    assert "example" in described["skill"]["tags"]


def test_seed_catalog_does_not_include_default_hermes_skills():
    directory = load_shared_skills(REGISTRY)
    names = {skill["name"] for skill in directory["skills"]}
    assert names == EXPECTED_SKILLS
    assert "hermes-agent" not in names
    assert all(skill["owner"] != "hermes-agent" for skill in directory["skills"])
    assert all("hermes-agent" not in skill["source"].lower() for skill in directory["skills"])
    assert all(
        skill["docs_path"].startswith("skills/")
        for skill in directory["skills"]
        if skill["name"] not in EXAMPLE_SKILLS
    )


def test_retrieve_example_bundle_includes_skill_and_allowed_support_files():
    bundle = retrieve_shared_skill(REGISTRY, "demo-research-brief", content_roots=[ROOT], include_bundle=True)
    paths = [item["path"] for item in bundle["files"]]
    assert paths == ["SKILL.md", "templates/brief.md"]
    assert bundle["file_count"] == 2
    assert all(item["sha256"] for item in bundle["files"])
    assert bundle["execution_available"] is False
    assert bundle["install_available"] is True


@pytest.mark.parametrize("name", sorted(EXPECTED_SKILLS))
def test_every_seed_retrieves_and_installs_into_scratch_root(name, tmp_path):
    bundle = retrieve_shared_skill(REGISTRY, name, content_roots=[ROOT], include_bundle=True)
    assert bundle["file_count"] >= 1
    assert bundle["files"][0]["path"] == "SKILL.md"
    assert all(item["sha256"] for item in bundle["files"])

    result = install_shared_skill_bundle(bundle, skills_root=tmp_path / "skills")
    install_dir = Path(result["installed_path"])
    assert result["installed"] is True
    assert install_dir.is_relative_to(tmp_path / "skills")
    assert (install_dir / "SKILL.md").is_file()


def test_install_bundle_writes_example_to_configured_scratch_skills_root(tmp_path):
    bundle = retrieve_shared_skill(REGISTRY, "demo-research-brief", content_roots=[ROOT], include_bundle=True)
    result = install_shared_skill_bundle(bundle, skills_root=tmp_path / "skills")

    install_dir = tmp_path / "skills" / "example" / "demo-research-brief"
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
