from __future__ import annotations

import secrets
import sys

import uvicorn

from .config import load_settings


def main() -> None:
    """Run the private/local HTTP service with validated bind settings."""
    settings = load_settings()
    if not settings.is_loopback_bind and not settings.auth_token:
        print(
            "WARNING: non-loopback bind without SSR_MCP_AUTH_TOKEN — every client that can "
            "reach this address can use the tool, registry-editing, and audit routes. "
            "Generate a token with shared-skills-registry-generate-token.",
            file=sys.stderr,
        )
    uvicorn.run(
        "shared_skills_registry_mcp.app:app",
        host=settings.bind_host,
        port=settings.port,
    )


def generate_token() -> None:
    """Print a fresh SSR bearer token as a ready-to-paste .env line."""
    token = secrets.token_urlsafe(32)
    print(f"SSR_MCP_AUTH_TOKEN={token}")
    print(
        "Set this in the HTTP service environment and in every MCP stdio adapter "
        "or client that talks to it. Treat it like a password.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
