from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

import shared_skills_registry_mcp.shared_skills as shared_skills_module
from fastapi.testclient import TestClient
from shared_skills_registry_mcp.app import create_app
from shared_skills_registry_mcp.config import Settings
from shared_skills_registry_mcp.registry_edit import upsert_registry_skill
from shared_skills_registry_mcp.shared_skills import (
    SharedSkillInstallError,
    SharedSkillNotFound,
    SharedSkillsConfigError,
    install_shared_skill_bundle,
    load_shared_skills,
    retrieve_shared_skill,
)

SKILL = "guard-skill"


def _entry(**overrides) -> dict:
    entry = {
        "name": SKILL,
        "title": "Guardrail Skill",
        "summary": "Fixture skill for negative-path tests.",
        "category": "demo",
        "owner": "example",
        "source": "local-example",
        "docs_path": f"skills/{SKILL}/SKILL.md",
        "applicability": "Guardrail testing.",
        "lifecycle_status": "active",
        "install_guidance": "Scratch installs only.",
        "tags": ["demo"],
    }
    entry.update(overrides)
    return entry


def _frontmatter(name: str) -> str:
    return f"---\nname: {name}\ndescription: guardrail fixture\n---\n\n# {name}\n"


def _build_repo(tmp_path: Path, *, docs_path: str | None = None, frontmatter_name: str | None = None, extra_files: dict[str, str] | None = None) -> tuple[Path, Path]:
    """Create a content root with a registry and one skill bundle. Returns
    (registry_path, repo_root)."""
    repo = tmp_path / "repo"
    (repo / "config").mkdir(parents=True, exist_ok=True)
    registry = repo / "config" / "shared_skills.yaml"
    entry = _entry(**({"docs_path": docs_path} if docs_path else {}))
    registry.write_text(yaml.safe_dump({"version": 1, "skills": [entry]}), encoding="utf-8")

    skill_dir = repo / "skills" / SKILL
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(_frontmatter(frontmatter_name or SKILL), encoding="utf-8")
    (skill_dir / "templates").mkdir(exist_ok=True)
    (skill_dir / "templates" / "note.md").write_text("template body\n", encoding="utf-8")
    for rel, content in (extra_files or {}).items():
        target = skill_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return registry, repo


def _bundle(registry: Path, repo: Path) -> dict:
    return retrieve_shared_skill(registry, SKILL, content_roots=[repo], include_bundle=True)


def _rehash(item: dict) -> None:
    item["sha256"] = hashlib.sha256(item["content"].encode("utf-8")).hexdigest()


# ── 1. path escape rejection ────────────────────────────────────────────────


def test_retrieve_rejects_docs_path_escaping_content_roots(tmp_path):
    registry, repo = _build_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "SKILL.md").write_text(_frontmatter(SKILL), encoding="utf-8")

    for docs_path in ("../outside/SKILL.md", str(outside / "SKILL.md")):
        registry.write_text(
            yaml.safe_dump({"version": 1, "skills": [_entry(docs_path=docs_path)]}),
            encoding="utf-8",
        )
        with pytest.raises(SharedSkillNotFound):
            retrieve_shared_skill(registry, SKILL, content_roots=[repo], include_bundle=True)


def test_install_rejects_escaping_bundle_file_paths(tmp_path):
    registry, repo = _build_repo(tmp_path)
    skills_root = tmp_path / "install-root"
    for bad_path in ("../evil.md", "templates/../../evil.md", "/tmp/evil.md", ".."):
        bundle = _bundle(registry, repo)
        item = bundle["files"][1]
        item["path"] = bad_path
        _rehash(item)
        with pytest.raises(SharedSkillInstallError):
            install_shared_skill_bundle(bundle, skills_root=skills_root)
        assert not skills_root.exists()


def test_install_rejects_symlinked_category_escaping_skills_root(tmp_path):
    registry, repo = _build_repo(tmp_path)
    skills_root = tmp_path / "install-root"
    skills_root.mkdir()
    outside = tmp_path / "outside-target"
    outside.mkdir()
    (skills_root / "linked").symlink_to(outside, target_is_directory=True)

    bundle = _bundle(registry, repo)
    with pytest.raises(SharedSkillInstallError, match="escapes"):
        install_shared_skill_bundle(bundle, skills_root=skills_root, target_category="linked")
    assert list(outside.iterdir()) == []


# ── 2. unsupported bundle directories ───────────────────────────────────────


def test_retrieve_excludes_files_outside_allowed_support_dirs(tmp_path):
    registry, repo = _build_repo(
        tmp_path,
        extra_files={
            "secrets/creds.txt": "hunter2",
            ".ssh/id_rsa": "not-a-real-key",
            "private/notes.md": "internal",
            "references/ok.md": "allowed",
        },
    )
    bundle = _bundle(registry, repo)
    paths = [item["path"] for item in bundle["files"]]
    assert paths == ["SKILL.md", "references/ok.md", "templates/note.md"]


def test_install_rejects_bundle_files_in_unsupported_dirs(tmp_path):
    registry, repo = _build_repo(tmp_path)
    skills_root = tmp_path / "install-root"
    for bad_path in ("secrets/creds.txt", ".ssh/id_rsa", "private/notes.md", "SKILL2.md"):
        bundle = _bundle(registry, repo)
        content = "smuggled"
        bundle["files"].append({"path": bad_path, "size_bytes": len(content), "sha256": hashlib.sha256(content.encode()).hexdigest(), "content": content})
        with pytest.raises(SharedSkillInstallError, match="allowed skill directories|unsafe"):
            install_shared_skill_bundle(bundle, skills_root=skills_root)
        assert not skills_root.exists()


# ── 3. SKILL.md frontmatter validation ──────────────────────────────────────


def test_install_rejects_frontmatter_name_mismatch(tmp_path):
    registry, repo = _build_repo(tmp_path, frontmatter_name="some-other-skill")
    with pytest.raises(SharedSkillInstallError, match="does not match"):
        install_shared_skill_bundle(_bundle(registry, repo), skills_root=tmp_path / "install-root")


@pytest.mark.parametrize(
    "content, match",
    [
        ("# no frontmatter at all\n", "must start with YAML frontmatter"),
        ("---\nname: guard-skill\nno terminator", "not terminated"),
        ("---\nname: [unclosed\n---\nbody", "invalid YAML"),
        ("---\n- just\n- a\n- list\n---\nbody", "must be a mapping"),
        ("---\ndescription: name is missing\n---\nbody", "does not match"),
    ],
)
def test_install_rejects_missing_or_malformed_frontmatter(tmp_path, content, match):
    registry, repo = _build_repo(tmp_path)
    skills_root = tmp_path / "install-root"
    bundle = _bundle(registry, repo)
    bundle["files"][0]["content"] = content
    _rehash(bundle["files"][0])
    with pytest.raises(SharedSkillInstallError, match=match):
        install_shared_skill_bundle(bundle, skills_root=skills_root)
    assert not skills_root.exists()


def test_install_requires_skill_md(tmp_path):
    registry, repo = _build_repo(tmp_path)
    bundle = _bundle(registry, repo)
    bundle["files"] = [f for f in bundle["files"] if f["path"] != "SKILL.md"]
    with pytest.raises(SharedSkillInstallError, match="missing SKILL.md"):
        install_shared_skill_bundle(bundle, skills_root=tmp_path / "install-root")


# ── 4. oversize files / bundles ─────────────────────────────────────────────


def test_retrieve_rejects_oversize_single_file(tmp_path, monkeypatch):
    registry, repo = _build_repo(tmp_path)
    monkeypatch.setattr(shared_skills_module, "_MAX_SKILL_FILE_BYTES", 10)
    with pytest.raises(SharedSkillsConfigError, match="too large"):
        retrieve_shared_skill(registry, SKILL, content_roots=[repo], include_bundle=False)


def test_retrieve_rejects_oversize_total_bundle(tmp_path, monkeypatch):
    registry, repo = _build_repo(tmp_path)
    main_size = (repo / "skills" / SKILL / "SKILL.md").stat().st_size
    monkeypatch.setattr(shared_skills_module, "_MAX_SKILL_BUNDLE_BYTES", main_size + 1)
    with pytest.raises(SharedSkillsConfigError, match="bundle is too large"):
        retrieve_shared_skill(registry, SKILL, content_roots=[repo], include_bundle=True)


# ── 5/6. checksum tampering and partial-write safety ────────────────────────


def test_tampered_support_file_rejected_before_any_write(tmp_path):
    registry, repo = _build_repo(tmp_path)
    skills_root = tmp_path / "install-root"
    bundle = _bundle(registry, repo)
    # SKILL.md is intact; the second file is tampered after hashing.
    bundle["files"][1]["content"] += " tampered"
    with pytest.raises(SharedSkillInstallError, match="checksum mismatch"):
        install_shared_skill_bundle(bundle, skills_root=skills_root)
    assert not skills_root.exists(), "failed install must not leave partial writes"


def test_missing_content_or_checksum_rejected(tmp_path):
    registry, repo = _build_repo(tmp_path)
    skills_root = tmp_path / "install-root"
    for mutate in (lambda f: f.pop("content"), lambda f: f.pop("sha256"), lambda f: f.__setitem__("sha256", 12345)):
        bundle = _bundle(registry, repo)
        mutate(bundle["files"][0])
        with pytest.raises(SharedSkillInstallError, match="missing content or checksum"):
            install_shared_skill_bundle(bundle, skills_root=skills_root)
        assert not skills_root.exists()


# ── 7. admin edit rejection ─────────────────────────────────────────────────


def test_upsert_rejects_invalid_entries_and_leaves_registry_intact(tmp_path):
    registry, _ = _build_repo(tmp_path)
    before = registry.read_bytes()

    invalid_entries = [
        _entry(name="Invalid Name!"),          # fails SKILL_NAME_RE
        _entry(name="-leading-dash"),          # must start alphanumeric
        _entry(summary=""),                    # empty required field
        _entry(docs_path="   "),               # whitespace-only path
        _entry(tags=["ok", 42]),               # non-string tag
        {k: v for k, v in _entry().items() if k != "source"},  # missing field
    ]
    for bad in invalid_entries:
        with pytest.raises(SharedSkillsConfigError):
            upsert_registry_skill(registry, bad)

    assert registry.read_bytes() == before, "rejected edits must not touch the file"
    directory = load_shared_skills(registry)
    assert [s["name"] for s in directory["skills"]] == [SKILL]


def test_admin_api_rejects_invalid_edit_and_registry_still_loads(tmp_path):
    registry, repo = _build_repo(tmp_path)
    app = create_app(
        Settings(
            shared_skills_path=str(registry),
            shared_skill_content_roots=(str(repo),),
            audit_log_path=str(tmp_path / "audit.jsonl"),
        )
    )
    client = TestClient(app)
    before = registry.read_bytes()

    bad = _entry(name="Invalid Name!")
    assert client.put("/registry/skills/Invalid%20Name!", json=bad).status_code == 422

    incomplete = {k: v for k, v in _entry().items() if k != "summary"}
    assert client.put(f"/registry/skills/{SKILL}", json=incomplete).status_code == 422

    assert registry.read_bytes() == before
    listed = client.post("/tools/list_shared_skills", json={})
    assert listed.status_code == 200
    assert [s["name"] for s in listed.json()["skills"]] == [SKILL]
