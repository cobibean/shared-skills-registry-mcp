# MCP client configuration examples

Shared Skills Registry MCP has two processes:

1. **HTTP service** — serves `/tools/...`, `/registry/...`, `/audit/recent`, and `/ui`.
2. **MCP stdio adapter** — `client/stdio_server.py`, which exposes the SSR tools to MCP clients and talks to the HTTP service through `SSR_MCP_URL`.

Start the HTTP service first:

```bash
cd /absolute/path/to/shared-skills-registry-mcp
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
uvicorn shared_skills_registry_mcp.app:app --host 127.0.0.1 --port 8765
```

Then configure your MCP client to launch the stdio adapter.

## Environment variables

| Variable | Required? | Purpose |
|---|---:|---|
| `SSR_MCP_URL` | no | HTTP service URL. Defaults to `http://127.0.0.1:8765`. |
| `SSR_MCP_SKILLS_ROOT` | yes for install | Local directory where `install_shared_skill` writes skills. |
| `SSR_MCP_AUDIT_LOG` | no | Optional JSONL log for local install results. |
| `PYTHONPATH` | only if not installed editable | Set to the repo `src/` directory when launching with a raw Python script. |

Use absolute paths in client configs. Most MCP clients launch servers from a different working directory than your shell.

## Generic `mcpServers` JSON

This shape works for clients that accept Claude Desktop/Cursor/Windsurf-style MCP JSON.

```json
{
  "mcpServers": {
    "shared-skills-registry": {
      "command": "/absolute/path/to/shared-skills-registry-mcp/.venv/bin/python",
      "args": [
        "/absolute/path/to/shared-skills-registry-mcp/client/stdio_server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/shared-skills-registry-mcp/src",
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

## Hermes Agent

Hermes has native MCP client commands. With the HTTP service running, add the stdio adapter like this:

```bash
cd /absolute/path/to/shared-skills-registry-mcp
hermes mcp add shared-skills-registry \
  --command /absolute/path/to/shared-skills-registry-mcp/.venv/bin/python \
  --env PYTHONPATH=/absolute/path/to/shared-skills-registry-mcp/src \
  --env SSR_MCP_URL=http://127.0.0.1:8765 \
  --env SSR_MCP_SKILLS_ROOT=/absolute/path/to/local/skills \
  --env SSR_MCP_AUDIT_LOG=/absolute/path/to/shared-skills-registry-mcp/data/ssr_audit.jsonl \
  --args /absolute/path/to/shared-skills-registry-mcp/client/stdio_server.py
```

Verify:

```bash
hermes mcp list
hermes mcp test shared-skills-registry
```

If your Hermes install already runs from a project where `shared-skills-registry-mcp` is installed into the environment, `PYTHONPATH` can be omitted.

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

## Smoke test without an MCP client

You can exercise the same server-side tool contracts over HTTP:

```bash
curl -s -X POST http://127.0.0.1:8765/tools/list_shared_skills \
  -H 'Content-Type: application/json' \
  -d '{}'

curl -s -X POST http://127.0.0.1:8765/tools/retrieve_shared_skill \
  -H 'Content-Type: application/json' \
  -d '{"name":"demo-research-brief","include_bundle":true}'
```

The HTTP service authorizes and returns a checksum-bearing bundle. The MCP stdio adapter performs the caller-local write into `SSR_MCP_SKILLS_ROOT` after re-validating paths, frontmatter, and checksums.
