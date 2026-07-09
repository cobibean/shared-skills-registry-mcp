from __future__ import annotations

import os
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import yaml

from .shared_skills import (
    SharedSkillNotFound,
    SharedSkillsConfigError,
    _safe_resolve_under,
    _validate_skill,
    load_shared_skills,
)

# Registry editing is a public-repo addition (the private SSR edits its YAML by
# hand). It reuses the ported validation so the file can never be written into
# a state that load_shared_skills would reject.

_FIELD_ORDER = (
    "name",
    "title",
    "summary",
    "category",
    "owner",
    "source",
    "docs_path",
    "applicability",
    "lifecycle_status",
    "install_guidance",
    "tags",
)


def _ordered(skill: dict[str, Any]) -> dict[str, Any]:
    return {field: skill[field] for field in _FIELD_ORDER}


def _write_registry(path: str | Path, skills: list[dict[str, Any]]) -> None:
    doc = {"version": 1, "skills": [_ordered(skill) for skill in skills]}
    # Validate the full document before it can replace the live registry.
    for idx, raw in enumerate(doc["skills"]):
        _validate_skill(raw, idx)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, default_flow_style=False)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp_name, target)
    finally:
        try:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
        except OSError:
            pass


def list_registry_skills(path: str | Path, *, content_roots: Sequence[str | Path] | None = None) -> dict[str, Any]:
    """Admin listing: every entry regardless of lifecycle_status, plus whether
    the referenced SKILL.md actually resolves under a content root."""
    directory = load_shared_skills(path)
    skills = []
    for skill in directory["skills"]:
        entry = dict(skill)
        entry["source_exists"] = _docs_path_resolves(skill["docs_path"], content_roots or [])
        skills.append(entry)
    return {"directory_version": directory["version"], "count": len(skills), "skills": skills}


def _docs_path_resolves(docs_path: str, content_roots: Sequence[str | Path]) -> bool:
    for root in content_roots:
        try:
            candidate = _safe_resolve_under(Path(root), docs_path)
        except OSError:
            continue
        if candidate and candidate.is_file():
            return True
    return False


def upsert_registry_skill(path: str | Path, entry: dict[str, Any]) -> dict[str, Any]:
    validated = _validate_skill(entry, 0)
    directory = load_shared_skills(path)
    skills = [dict(skill) for skill in directory["skills"]]
    created = True
    for idx, skill in enumerate(skills):
        if skill["name"] == validated["name"]:
            skills[idx] = validated
            created = False
            break
    else:
        skills.append(validated)
    _write_registry(path, skills)
    return {"saved": True, "created": created, "skill": validated}


def delete_registry_skill(path: str | Path, name: str) -> dict[str, Any]:
    normalized = name.strip().lower()
    directory = load_shared_skills(path)
    skills = [dict(skill) for skill in directory["skills"]]
    remaining = [skill for skill in skills if skill["name"] != normalized]
    if len(remaining) == len(skills):
        raise SharedSkillNotFound("unknown shared skill")
    _write_registry(path, remaining)
    return {"deleted": True, "skill_name": normalized, "remaining": len(remaining)}


__all__ = [
    "SharedSkillNotFound",
    "SharedSkillsConfigError",
    "delete_registry_skill",
    "list_registry_skills",
    "upsert_registry_skill",
]
