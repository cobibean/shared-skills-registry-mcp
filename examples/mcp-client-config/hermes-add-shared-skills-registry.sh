#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/absolute/path/to/shared-skills-registry-mcp}"
SKILLS_ROOT="${SSR_MCP_SKILLS_ROOT:-/tmp/ssr-demo-skills}"
AUDIT_LOG="${SSR_MCP_AUDIT_LOG:-$REPO_ROOT/data/ssr_audit.jsonl}"
SSR_URL="${SSR_MCP_URL:-http://127.0.0.1:8765}"
HERMES_BIN="${HERMES_BIN:-hermes}"

"$HERMES_BIN" mcp add shared-skills-registry \
  --command "$REPO_ROOT/.venv/bin/shared-skills-registry-stdio" \
  --env \
    "SSR_MCP_URL=$SSR_URL" \
    "SSR_MCP_SKILLS_ROOT=$SKILLS_ROOT" \
    "SSR_MCP_AUDIT_LOG=$AUDIT_LOG"

config_path="$("$HERMES_BIN" config path)"
"$REPO_ROOT/.venv/bin/python" - "$config_path" <<'PY'
from pathlib import Path
import sys
import yaml

config_path = Path(sys.argv[1])
config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
server = (config.get("mcp_servers") or {}).get("shared-skills-registry")
if not isinstance(server, dict) or not server.get("enabled", True):
    raise SystemExit(
        "shared-skills-registry was not persisted as an enabled MCP server; "
        "rerun and approve tool enablement"
    )
server_env = server.get("env") or {}
required_env = {"SSR_MCP_URL", "SSR_MCP_SKILLS_ROOT", "SSR_MCP_AUDIT_LOG"}
missing_env = sorted(required_env - set(server_env))
if missing_env:
    raise SystemExit(
        "shared-skills-registry configuration is missing environment values: "
        + ", ".join(missing_env)
    )
PY

test_output="$("$HERMES_BIN" mcp test shared-skills-registry 2>&1)"
printf '%s\n' "$test_output"
if [[ "$test_output" != *"✓ Connected"* ]] || [[ "$test_output" != *"✓ Tools discovered: 5"* ]]; then
  echo "Shared Skills Registry MCP connection verification failed" >&2
  exit 1
fi

echo "Shared Skills Registry MCP is configured. Start a new Hermes session to use its tools."
