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
    ):
        assert f"]({target})" in readme


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


def test_demo_gif_is_optimized_and_has_expected_readme_dimensions():
    gif = ROOT / "docs" / "assets" / "open-ssr-demo.gif"
    payload = gif.read_bytes()
    assert payload[:6] in {b"GIF87a", b"GIF89a"}
    width, height = struct.unpack("<HH", payload[6:10])
    assert (width, height) == (800, 450)
    assert 100_000 < len(payload) < 3_000_000


def test_third_party_notice_is_packaged_with_imported_bundles():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    force_include = config["tool"]["hatch"]["build"]["targets"]["wheel"]["force-include"]
    assert force_include["THIRD_PARTY_NOTICES.md"] == (
        "shared_skills_registry_mcp/_bundled/THIRD_PARTY_NOTICES.md"
    )


def test_gate_three_stays_open_for_human_readiness_review():
    board = (ROOT / "docs" / "TASK-BOARD.md").read_text(encoding="utf-8")
    assert "- [ ] Human onboarding and security-operator dogfood" in board
    assert "- [ ] Gate 3: Public safety/readiness review." in board
    assert "- [ ] Gate 4: Release/go-no-go." in board
