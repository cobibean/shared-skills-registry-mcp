from __future__ import annotations

import hashlib
import os
import re
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import yaml

SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,127}$")
REQUIRED_FIELDS = {
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
}
VISIBLE_STATUSES = {"active"}
_ALLOWED_BUNDLE_DIRS = {"references", "templates", "scripts", "assets"}
_MAX_SKILL_FILE_BYTES = 200_000
_MAX_SKILL_BUNDLE_BYTES = 750_000
_CATEGORY_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,63}$")


class SharedSkillsConfigError(ValueError):
    """Raised when the Shared Skills Registry is malformed."""


class SharedSkillNotFound(KeyError):
    """Raised when a shared skill is unknown or not visible."""


class SharedSkillInstallError(ValueError):
    """Raised when a shared skill bundle cannot be installed safely."""


def _clean_str(value: Any, *, field: str, skill_name: str, max_len: int = 1000) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SharedSkillsConfigError(f"{skill_name}.{field} must be a non-empty string")
    cleaned = value.strip()
    if len(cleaned) > max_len:
        raise SharedSkillsConfigError(f"{skill_name}.{field} is too long")
    return cleaned


def _validate_skill(raw: Any, index: int) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise SharedSkillsConfigError(f"shared skill entry {index} must be an object")
    skill_name = str(raw.get("name", f"entry_{index}"))
    missing = REQUIRED_FIELDS - set(raw)
    if missing:
        raise SharedSkillsConfigError(f"{skill_name} missing required fields: {', '.join(sorted(missing))}")
    name = _clean_str(raw["name"], field="name", skill_name=skill_name, max_len=128)
    if not SKILL_NAME_RE.fullmatch(name):
        raise SharedSkillsConfigError(f"{name} has invalid shared skill name")
    tags = raw.get("tags", [])
    if tags is None:
        tags = []
    if not isinstance(tags, list) or not all(isinstance(tag, str) and tag.strip() for tag in tags):
        raise SharedSkillsConfigError(f"{name}.tags must be a list of strings")
    lifecycle_status = _clean_str(raw["lifecycle_status"], field="lifecycle_status", skill_name=name, max_len=64).lower()
    return {
        "name": name,
        "title": _clean_str(raw["title"], field="title", skill_name=name, max_len=160),
        "summary": _clean_str(raw["summary"], field="summary", skill_name=name, max_len=1200),
        "category": _clean_str(raw["category"], field="category", skill_name=name, max_len=64).lower(),
        "owner": _clean_str(raw["owner"], field="owner", skill_name=name, max_len=64).lower(),
        "source": _clean_str(raw["source"], field="source", skill_name=name, max_len=160),
        "docs_path": _clean_str(raw["docs_path"], field="docs_path", skill_name=name, max_len=300),
        "applicability": _clean_str(raw["applicability"], field="applicability", skill_name=name, max_len=1200),
        "lifecycle_status": lifecycle_status,
        "install_guidance": _clean_str(raw["install_guidance"], field="install_guidance", skill_name=name, max_len=1200),
        "tags": [tag.strip().lower() for tag in tags],
    }


def load_shared_skills(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    try:
        loaded = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except FileNotFoundError as exc:
        raise SharedSkillsConfigError(f"Shared Skills Registry not found: {p}") from exc
    if not isinstance(loaded, dict):
        raise SharedSkillsConfigError("Shared Skills Registry must be a mapping")
    version = loaded.get("version", 1)
    if version != 1:
        raise SharedSkillsConfigError("unsupported Shared Skills Registry version")
    raw_skills = loaded.get("skills", [])
    if not isinstance(raw_skills, list):
        raise SharedSkillsConfigError("shared skills 'skills' must be a list")
    skills = [_validate_skill(raw, idx) for idx, raw in enumerate(raw_skills)]
    seen: set[str] = set()
    for skill in skills:
        if skill["name"] in seen:
            raise SharedSkillsConfigError(f"duplicate shared skill entry: {skill['name']}")
        seen.add(skill["name"])
    return {"version": 1, "skills": skills}


def _public_skill(skill: dict[str, Any]) -> dict[str, Any]:
    public = dict(skill)
    public["execution_available"] = False
    public["retrieval_available"] = True
    public["install_available"] = True
    public["profile_mutation_available"] = True
    return public


def _visible(skill: dict[str, Any]) -> bool:
    return skill["lifecycle_status"] in VISIBLE_STATUSES


def _matches(skill: dict[str, Any], *, query: str | None = None, category: str | None = None) -> bool:
    if category and skill["category"] != category.strip().lower():
        return False
    if not query:
        return True
    terms = [term for term in re.findall(r"[a-z0-9_.-]+", query.lower()) if len(term) > 1]
    if not terms:
        return False
    haystack = " ".join([
        skill["name"], skill["title"], skill["summary"], skill["category"], skill["owner"], skill["applicability"], " ".join(skill["tags"])
    ]).lower()
    return any(term in haystack for term in terms)


def list_shared_skills(path: str | Path, *, category: str | None = None, limit: int = 50) -> dict[str, Any]:
    directory = load_shared_skills(path)
    skills = [_public_skill(skill) for skill in directory["skills"] if _visible(skill) and _matches(skill, category=category)]
    skills.sort(key=lambda item: (item["category"], item["name"]))
    skills = skills[: max(1, min(int(limit), 100))]
    return {"directory_version": directory["version"], "count": len(skills), "skills": skills}


def describe_shared_skill(path: str | Path, name: str) -> dict[str, Any]:
    directory = load_shared_skills(path)
    normalized = name.strip().lower()
    for skill in directory["skills"]:
        if skill["name"] == normalized and _visible(skill):
            return {"directory_version": directory["version"], "skill": _public_skill(skill)}
    raise SharedSkillNotFound("unknown shared skill")


def search_shared_skills(path: str | Path, query: str, *, category: str | None = None, limit: int = 10) -> dict[str, Any]:
    directory = load_shared_skills(path)
    scored: list[tuple[int, dict[str, Any]]] = []
    terms = [term for term in re.findall(r"[a-z0-9_.-]+", query.lower()) if len(term) > 1]
    if not terms:
        return {"directory_version": directory["version"], "count": 0, "skills": []}
    for skill in directory["skills"]:
        if not _visible(skill) or not _matches(skill, category=category):
            continue
        haystack = " ".join([
            skill["name"], skill["title"], skill["summary"], skill["category"], skill["owner"], skill["applicability"], " ".join(skill["tags"])
        ]).lower()
        score = sum(haystack.count(term) for term in terms)
        if score > 0:
            scored.append((score, _public_skill(skill)))
    scored.sort(key=lambda pair: (-pair[0], pair[1]["category"], pair[1]["name"]))
    skills = [skill for _, skill in scored[: max(1, min(int(limit), 100))]]
    return {"directory_version": directory["version"], "count": len(skills), "skills": skills}


def _safe_resolve_under(root: Path, rel_path: str) -> Path | None:
    if not rel_path or "\x00" in rel_path:
        return None
    candidate = Path(rel_path)
    if candidate.is_absolute():
        return None
    try:
        resolved_root = root.resolve(strict=True)
        resolved = (resolved_root / candidate).resolve(strict=False)
    except OSError:
        return None
    if resolved == resolved_root or resolved_root in resolved.parents:
        return resolved
    return None


def _content_roots(shared_skills_path: str | Path, content_roots: Sequence[str | Path] | None = None) -> list[Path]:
    roots: list[Path] = []
    for raw in content_roots or []:
        text = str(raw).strip() if raw is not None else ""
        if text:
            roots.append(Path(text))
    try:
        roots.append(Path(shared_skills_path).resolve(strict=False).parent.parent)
    except OSError:
        pass
    deduped: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root)
        if key not in seen:
            deduped.append(root)
            seen.add(key)
    return deduped


def _read_bundle_file(base_dir: Path, path: Path, rel_name: str) -> tuple[dict[str, Any], int]:
    try:
        resolved_base = base_dir.resolve(strict=True)
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise SharedSkillsConfigError("Shared Skills Registry source file is not readable") from exc
    if resolved_base not in resolved.parents and resolved != resolved_base:
        raise SharedSkillsConfigError("Shared Skills Registry source path escapes skill directory")
    size = resolved.stat().st_size
    if size > _MAX_SKILL_FILE_BYTES:
        raise SharedSkillsConfigError("Shared Skills Registry source file is too large")
    content = resolved.read_text(encoding="utf-8")
    return {"path": rel_name, "size_bytes": size, "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(), "content": content}, size


def retrieve_shared_skill(path: str | Path, name: str, *, content_roots: Sequence[str | Path] | None = None, include_bundle: bool = True) -> dict[str, Any]:
    described = describe_shared_skill(path, name)
    skill = described["skill"]
    docs_path = skill["docs_path"]
    source_file: Path | None = None
    for root in _content_roots(path, content_roots):
        candidate = _safe_resolve_under(root, docs_path)
        if candidate and candidate.exists() and candidate.is_file():
            source_file = candidate
            break
    if source_file is None:
        raise SharedSkillNotFound("Shared Skills Registry source unavailable")

    skill_dir = source_file.parent
    main_file, total = _read_bundle_file(skill_dir, source_file, "SKILL.md")
    files = [main_file]
    if include_bundle:
        for child in sorted(skill_dir.rglob("*")):
            if not child.is_file() or child == source_file:
                continue
            try:
                rel = child.relative_to(skill_dir)
            except ValueError:
                continue
            parts = rel.parts
            if not parts or parts[0] not in _ALLOWED_BUNDLE_DIRS:
                continue
            item, size = _read_bundle_file(skill_dir, child, rel.as_posix())
            total += size
            if total > _MAX_SKILL_BUNDLE_BYTES:
                raise SharedSkillsConfigError("shared skill bundle is too large")
            files.append(item)
    return {
        "directory_version": described["directory_version"],
        "skill": skill,
        "bundle_version": 1,
        "source_docs_path": docs_path,
        "file_count": len(files),
        "total_size_bytes": total,
        "files": files,
        "install_available": True,
        "profile_mutation_available": True,
        "execution_available": False,
    }


def validate_skill_frontmatter(content: str, expected_name: str) -> dict[str, Any]:
    if not content.startswith("---\n"):
        raise SharedSkillInstallError("SKILL.md must start with YAML frontmatter")
    try:
        _, frontmatter, _body = content.split("---", 2)
    except ValueError as exc:
        raise SharedSkillInstallError("SKILL.md frontmatter is not terminated") from exc
    try:
        parsed = yaml.safe_load(frontmatter) or {}
    except yaml.YAMLError as exc:
        raise SharedSkillInstallError("SKILL.md frontmatter is invalid YAML") from exc
    if not isinstance(parsed, dict):
        raise SharedSkillInstallError("SKILL.md frontmatter must be a mapping")
    name = str(parsed.get("name", "")).strip().lower()
    if name != expected_name.strip().lower():
        raise SharedSkillInstallError("SKILL.md frontmatter name does not match requested skill")
    return parsed


def _safe_install_rel_path(rel_path: str) -> Path:
    if rel_path == "SKILL.md":
        return Path("SKILL.md")
    candidate = Path(rel_path)
    if candidate.is_absolute() or "\x00" in rel_path:
        raise SharedSkillInstallError("bundle file path is unsafe")
    parts = candidate.parts
    if not parts or parts[0] not in _ALLOWED_BUNDLE_DIRS or any(part in {"", ".", ".."} for part in parts):
        raise SharedSkillInstallError("bundle file path is outside allowed skill directories")
    return candidate


def install_shared_skill_bundle(
    bundle: dict[str, Any],
    *,
    skills_root: str | Path,
    target_category: str | None = None,
    overwrite: bool = True,
) -> dict[str, Any]:
    skill = bundle.get("skill") or {}
    skill_name = str(skill.get("name", "")).strip().lower()
    if not SKILL_NAME_RE.fullmatch(skill_name):
        raise SharedSkillInstallError("bundle skill name is invalid")
    category = (target_category or skill.get("category") or "shared").strip().lower()
    if not _CATEGORY_RE.fullmatch(category):
        raise SharedSkillInstallError("target category is invalid")
    files = bundle.get("files")
    if not isinstance(files, list) or not files:
        raise SharedSkillInstallError("bundle does not contain files")
    by_path: dict[str, dict[str, Any]] = {}
    for item in files:
        if not isinstance(item, dict):
            raise SharedSkillInstallError("bundle file entry is invalid")
        rel = str(item.get("path", ""))
        _safe_install_rel_path(rel)
        content = item.get("content")
        digest = item.get("sha256")
        if not isinstance(content, str) or not isinstance(digest, str):
            raise SharedSkillInstallError("bundle file entry is missing content or checksum")
        if hashlib.sha256(content.encode("utf-8")).hexdigest() != digest:
            raise SharedSkillInstallError("bundle checksum mismatch")
        by_path[rel] = item
    if "SKILL.md" not in by_path:
        raise SharedSkillInstallError("bundle is missing SKILL.md")
    frontmatter = validate_skill_frontmatter(str(by_path["SKILL.md"]["content"]), skill_name)
    root = Path(skills_root).expanduser().resolve(strict=False)
    install_dir = (root / category / skill_name).resolve(strict=False)
    if root not in install_dir.parents:
        raise SharedSkillInstallError("install path escapes configured skills directory")
    if install_dir.exists() and not overwrite:
        raise SharedSkillInstallError("skill already installed; pass overwrite=true to replace it")
    install_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for rel, item in sorted(by_path.items(), key=lambda pair: pair[0]):
        rel_path = _safe_install_rel_path(rel)
        target = (install_dir / rel_path).resolve(strict=False)
        if install_dir not in target.parents and target != install_dir:
            raise SharedSkillInstallError("target file path escapes install directory")
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(str(item["content"]))
            os.replace(tmp_name, target)
        finally:
            try:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
            except OSError:
                pass
        written.append(rel)
    return {
        "installed": True,
        "skill_name": skill_name,
        "category": category,
        "installed_path": str(install_dir),
        "file_count": len(written),
        "files": written,
        "frontmatter": {"name": frontmatter.get("name"), "description": frontmatter.get("description")},
        "reload_required": True,
        "reload_hint": "Reload your agent skills or start a new session for the installed skill to become available.",
    }
