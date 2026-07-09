from __future__ import annotations

import os
import ipaddress
from dataclasses import dataclass, field
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_SHARED_SKILLS_PATH = str(_REPO_ROOT / "config" / "shared_skills.yaml")


@dataclass
class Settings:
    bind_host: str = "127.0.0.1"
    port: int = 8765
    shared_skills_path: str = _DEFAULT_SHARED_SKILLS_PATH
    shared_skill_content_roots: tuple[str, ...] = field(default_factory=lambda: (str(_REPO_ROOT),))

    @property
    def base_url(self) -> str:
        return f"http://{self.bind_host}:{self.port}"


def load_settings() -> Settings:
    roots_raw = os.environ.get("SSR_MCP_SHARED_SKILL_CONTENT_ROOTS", str(_REPO_ROOT))
    settings = Settings(
        bind_host=os.environ.get("SSR_MCP_BIND", "127.0.0.1"),
        port=int(os.environ.get("SSR_MCP_PORT", "8765")),
        shared_skills_path=os.environ.get("SSR_MCP_SHARED_SKILLS", _DEFAULT_SHARED_SKILLS_PATH),
        shared_skill_content_roots=tuple(item.strip() for item in roots_raw.split(",") if item.strip()),
    )
    _validate_private_or_local_bind(settings.bind_host)
    return settings


def _validate_private_or_local_bind(bind_host: str) -> None:
    if bind_host in {"0.0.0.0", "::"}:
        raise ValueError("SSR_MCP_BIND must not be a wildcard/public bind")
    try:
        ip = ipaddress.ip_address(bind_host)
    except ValueError:
        if bind_host not in {"localhost"}:
            raise ValueError("SSR_MCP_BIND must be localhost or a private/tailnet IP literal")
        return
    if ip.is_loopback:
        return
    tailscale_cgnat = ipaddress.ip_network("100.64.0.0/10")
    if ip.version == 4 and (ip.is_private or ip in tailscale_cgnat):
        return
    if ip.version == 6 and (ip.is_private or ip.is_link_local):
        return
    raise ValueError("SSR_MCP_BIND must be localhost, private, or Tailscale CGNAT address")
