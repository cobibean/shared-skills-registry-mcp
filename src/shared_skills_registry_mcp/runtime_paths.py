from __future__ import annotations

import os
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parent
_SOURCE_ROOT = Path(__file__).resolve().parents[2]
_BUNDLED_ROOT = _PACKAGE_ROOT / "_bundled"


def runtime_content_root() -> Path:
    """Return the source checkout root or the wheel's bundled-data root."""
    if (_SOURCE_ROOT / "config" / "shared_skills.yaml").is_file():
        return _SOURCE_ROOT
    return _BUNDLED_ROOT


def default_registry_path() -> Path:
    return runtime_content_root() / "config" / "shared_skills.yaml"


def default_ui_path() -> Path:
    return runtime_content_root() / "ui" / "index.html"


def default_audit_path() -> Path:
    if runtime_content_root() == _SOURCE_ROOT:
        return _SOURCE_ROOT / "data" / "ssr_audit.jsonl"
    state_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return state_home / "shared-skills-registry-mcp" / "ssr_audit.jsonl"
