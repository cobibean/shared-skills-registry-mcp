# MCP client configuration examples

Shared Skills Registry MCP has two processes:

1. **HTTP service** — serves `/tools/...`, `/registry/...`, `/audit/recent`, and `/ui`.
2. **MCP stdio adapter** — the `shared-skills-registry-stdio` command, which exposes the SSR tools to MCP clients and talks to the HTTP service through `SSR_MCP_URL`. `client/stdio_server.py` remains as a repository-relative compatibility shim.

Start the HTTP service first. If you installed from PyPI with pipx or uv, both commands are already on your `PATH`:

```bash
pipx install --pip-args=--pre shared-skills-registry-mcp   # or: uv tool install --prerelease=allow shared-skills-registry-mcp
shared-skills-registry-http
```

Or from a source checkout:

```bash
cd /absolute/path/to/shared-skills-registry-mcp
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
shared-skills-registry-http
```

Then configure your MCP client to launch the stdio adapter. With a pipx/uv install, `command` can simply be `shared-skills-registry-stdio` (or its absolute path from `command -v shared-skills-registry-stdio` for clients that do not inherit your shell `PATH`). With a source checkout, use the venv path shown in the examples below.

## Environment variables

| Variable | Required? | Purpose |
|---|---:|---|
| `SSR_MCP_URL` | no | HTTP service URL. Defaults to `http://127.0.0.1:8765`. |
| `SSR_MCP_SKILLS_ROOT` | yes for install | Local directory where `install_shared_skill` writes skills. |
| `SSR_MCP_AUDIT_LOG` | no | Optional JSONL log for local install results. |
| `SSR_MCP_ALLOW_SKILLS_ROOT_OVERRIDE` | no | Unsafe-by-default escape hatch. Set to `1` only when a trusted caller must select a per-call local root; otherwise model-supplied root overrides are rejected. |
| `PYTHONPATH` | legacy raw-script use only | Set to the repo `src/` directory only when using `client/stdio_server.py` without installing the project. |

Use absolute paths in client configs. Most MCP clients launch servers from a different working directory than your shell.

## Generic `mcpServers` JSON

This shape works for clients that accept Claude Desktop/Cursor/Windsurf-style MCP JSON.

```json
{
  "mcpServers": {
    "shared-skills-registry": {
      "command": "/absolute/path/to/shared-skills-registry-mcp/.venv/bin/shared-skills-registry-stdio",
      "args": [],
      "env": {
        "SSR_MCP_URL": "http://127.0.0.1:8765",
        "SSR_MCP_SKILLS_ROOT": "/absolute/path/to/local/skills",
        "SSR_MCP_AUDIT_LOG": "/absolute/path/to/shared-skills-registry-mcp/data/ssr_audit.jsonl"
      }
    }
  }
}
```

Tools exposed to the client:

- `list_shared_skills`
- `search_shared_skills`
- `describe_shared_skill`
- `retrieve_shared_skill`
- `install_shared_skill`

## Claude Code

Claude Code has a native MCP add command. With the HTTP service running:

```bash
mkdir -p ~/ssr-skills   # scratch install root; review bundles before pointing at a real skills directory
claude mcp add shared-skills-registry \
  --env SSR_MCP_URL=http://127.0.0.1:8765 \
  --env SSR_MCP_SKILLS_ROOT="$HOME/ssr-skills" \
  --env SSR_MCP_AUDIT_LOG="$HOME/ssr-skills/.ssr-local-audit.jsonl" \
  -- shared-skills-registry-stdio
```

If Claude Code cannot find `shared-skills-registry-stdio`, replace it with the absolute path printed by `command -v shared-skills-registry-stdio` (pipx/uv install) or `/absolute/path/to/shared-skills-registry-mcp/.venv/bin/shared-skills-registry-stdio` (source checkout).

Verify inside a new Claude Code session: run `/mcp`, confirm the five `*_shared_skills` tools are listed, then ask the agent to list shared skills.

## Hermes Agent

Hermes has native MCP client commands. With the HTTP service running, add the stdio adapter like this:

```bash
cd /absolute/path/to/shared-skills-registry-mcp
hermes mcp add shared-skills-registry \
  --command /absolute/path/to/shared-skills-registry-mcp/.venv/bin/shared-skills-registry-stdio \
  --env \
    SSR_MCP_URL=http://127.0.0.1:8765 \
    SSR_MCP_SKILLS_ROOT=/absolute/path/to/local/skills \
    SSR_MCP_AUDIT_LOG=/absolute/path/to/shared-skills-registry-mcp/data/ssr_audit.jsonl
```

Hermes performs discovery first and asks which tools to enable. Choose `Y` to enable all five; then start a new session. In unattended test automation, pipe one explicit approval (`printf 'y\n' | hermes mcp add ...`) and always verify with `hermes mcp list` afterward—an interactive cancellation may not be distinguishable from success by exit status alone.

Verify:

```bash
hermes mcp list
hermes mcp test shared-skills-registry
```

The command above is installed by `pip install -e .` and by the built wheel, so it does not depend on the MCP client's working directory.

## Claude Desktop / Cursor / Windsurf

Use the generic `mcpServers` JSON above and replace the placeholder paths.

Suggested local install roots:

```text
# scratch/demo install root
/tmp/ssr-demo-skills

# project-local skill root
/absolute/path/to/your-project/.agent-skills
```

If you point `SSR_MCP_SKILLS_ROOT` at a real agent skills directory, review a retrieved bundle in the UI first and keep `SSR_MCP_AUDIT_LOG` enabled so local installs are visible in the activity trail.

## Real MCP stdio smoke

With the HTTP service running, use the included generic MCP client to test protocol initialization, tool discovery, list/search/describe/retrieve, and caller-local installation:

```bash
tmp="$(mktemp -d)"
python scripts/mcp_stdio_smoke.py \
  --url http://127.0.0.1:8765 \
  --skills-root "$tmp/skills" \
  --audit-log "$tmp/local-audit.jsonl"
```

The default smoke installs `project-memory` under its registry category:

```text
$tmp/skills/project-continuity/project-memory/SKILL.md
```

That category nesting is part of the install contract. Use `--skill <name>` and `--search-query <query>` to exercise another entry. The script exits nonzero if the protocol, tool set, tool calls, local files, or install audit fail.

## HTTP contract check

HTTP calls are useful for diagnosing the backing service, but they do not prove the MCP stdio transport:

```bash
curl -s -X POST http://127.0.0.1:8765/tools/list_shared_skills \
  -H 'Content-Type: application/json' \
  -d '{}'

curl -s -X POST http://127.0.0.1:8765/tools/retrieve_shared_skill \
  -H 'Content-Type: application/json' \
  -d '{"name":"demo-research-brief","include_bundle":true}'
```

The HTTP service authorizes and returns a checksum-bearing bundle. The MCP stdio adapter performs the caller-local write into `SSR_MCP_SKILLS_ROOT` after re-validating paths, frontmatter, and checksums.
