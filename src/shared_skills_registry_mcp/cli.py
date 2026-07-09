from __future__ import annotations

import uvicorn

from .config import load_settings


def main() -> None:
    """Run the private/local HTTP service with validated bind settings."""
    settings = load_settings()
    uvicorn.run(
        "shared_skills_registry_mcp.app:app",
        host=settings.bind_host,
        port=settings.port,
    )


if __name__ == "__main__":
    main()
