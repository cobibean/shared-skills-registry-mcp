#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/absolute/path/to/shared-skills-registry-mcp}"
SKILLS_ROOT="${SSR_MCP_SKILLS_ROOT:-/tmp/ssr-demo-skills}"
AUDIT_LOG="${SSR_MCP_AUDIT_LOG:-$REPO_ROOT/data/ssr_audit.jsonl}"

hermes mcp add shared-skills-registry \
  --command "$REPO_ROOT/.venv/bin/python" \
  --env "PYTHONPATH=$REPO_ROOT/src" \
  --env "SSR_MCP_URL=http://127.0.0.1:8765" \
  --env "SSR_MCP_SKILLS_ROOT=$SKILLS_ROOT" \
  --env "SSR_MCP_AUDIT_LOG=$AUDIT_LOG" \
  --args "$REPO_ROOT/client/stdio_server.py"

hermes mcp test shared-skills-registry
