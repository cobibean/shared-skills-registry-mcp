from __future__ import annotations

import re
import struct
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_DOCS = (
    ROOT / "README.md",
    ROOT / "SECURITY.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "docs" / "SECURITY-BOUNDARY.md",
    ROOT / "docs" / "THREAT-MODEL.md",
    ROOT / "docs" / "KNOWN-LIMITATIONS.md",
    ROOT / "docs" / "DEMO-SCRIPT.md",
    ROOT / "docs" / "RELEASE-CHECKLIST.md",
    ROOT / "docs" / "releases" / "v0.1.0a1.md",
    ROOT / "docs" / "TASK-BOARD.md",
)


def test_release_readiness_documents_exist_and_are_linked_from_readme():
    for path in RELEASE_DOCS:
        assert path.is_file(), path

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for target in (
        "SECURITY.md",
        "CONTRIBUTING.md",
        "docs/THREAT-MODEL.md",
        "docs/KNOWN-LIMITATIONS.md",
        "docs/DEMO-SCRIPT.md",
        "docs/RELEASE-CHECKLIST.md",
        "docs/releases/v0.1.0a1.md",
    ):
        assert f"]({target})" in readme
    assert "SSR_MCP_PORT=18765 shared-skills-registry-http" in readme
    assert "use it consistently" in readme


def test_release_document_local_links_resolve():
    missing: list[tuple[str, str]] = []
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for source in RELEASE_DOCS:
        for target in link_pattern.findall(source.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            local_target = target.split("#", 1)[0]
            if local_target and not (source.parent / local_target).resolve().exists():
                missing.append((str(source.relative_to(ROOT)), target))
    assert missing == []


def test_security_policy_uses_private_reporting_and_states_alpha_boundary():
    policy = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "security/advisories/new" in policy
    assert "Do not open a public issue" in policy
    assert "no built-in HTTP authentication" in policy

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    limitations = (ROOT / "docs" / "KNOWN-LIMITATIONS.md").read_text(encoding="utf-8")
    boundary = (ROOT / "docs" / "SECURITY-BOUNDARY.md").read_text(encoding="utf-8")
    threat_model = (ROOT / "docs" / "THREAT-MODEL.md").read_text(encoding="utf-8")
    assert "heuristic redaction can miss" in readme
    assert "does not authenticate same-host clients" in limitations
    assert "restore the previous installation when possible" in boundary
    assert "### Write map" in threat_model


def test_demo_gif_is_optimized_and_has_expected_readme_dimensions():
    gif = ROOT / "docs" / "assets" / "open-ssr-demo.gif"
    payload = gif.read_bytes()
    assert payload[:6] in {b"GIF87a", b"GIF89a"}
    width, height = struct.unpack("<HH", payload[6:10])
    assert (width, height) == (800, 450)
    assert 100_000 < len(payload) < 3_000_000


def test_release_metadata_identifies_alpha_and_public_project_surfaces():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = config["project"]
    assert project["version"] == "0.1.0a1"
    assert "Development Status :: 3 - Alpha" in project["classifiers"]
    assert project["requires-python"] == ">=3.11,<3.15"
    assert {"Homepage", "Repository", "Documentation", "Issues", "Security"} <= set(project["urls"])
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "https://raw.githubusercontent.com/cobibean/shared-skills-registry-mcp/main/docs/assets/open-ssr-demo.gif" in readme


def test_sdist_excludes_internal_project_records():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    excluded = set(config["tool"]["hatch"]["build"]["targets"]["sdist"]["exclude"])
    assert {"/.agent", "/docs/memory"} <= excluded


def test_third_party_notice_is_packaged_with_imported_bundles():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    force_include = config["tool"]["hatch"]["build"]["targets"]["wheel"]["force-include"]
    assert force_include["THIRD_PARTY_NOTICES.md"] == (
        "shared_skills_registry_mcp/_bundled/THIRD_PARTY_NOTICES.md"
    )


def test_gate_three_is_go_while_gate_four_stays_blocked_on_prerelease_decision():
    board = (ROOT / "docs" / "TASK-BOARD.md").read_text(encoding="utf-8")
    assert "- [x] Clean first-time-user onboarding replay" in board
    assert "- [x] Gate 3: Public safety/readiness review — **GO**" in board
    assert "- [x] Gate 4: Release/go-no-go — **GO/PUBLISHED**" in board
    assert "releases/tag/v0.1.0a1" in board
    assert "no PyPI publication" in board
