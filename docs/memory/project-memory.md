# Open SSR project memory

Last updated: 2026-07-09

Project: **Shared Skills Registry MCP**
Shorthand: **Open SSR**
Repo: <https://github.com/cobibean/shared-skills-registry-mcp>

This file is public-safe temporary project memory. Keep secrets and private deployment details out. Delete `docs/memory/` later after this state is captured in durable public docs/issues/release notes.

## Product promise

Shared Skills Registry MCP is a self-hosted registry, control panel, and MCP interface for reusable AI-agent skills.

The useful product boundary is:

```text
publish a skill -> discover it over MCP -> inspect/retrieve the checksum-bearing bundle -> install it locally with guardrails
```

The public repo is an SSR-only extraction from an already-working private MCP server. The project should keep inheriting the proven SSR shape rather than becoming a new invented app.

## Non-goals / scope boundaries

Do not add these without an explicit product decision:

- Docker/Compose-first assumptions.
- Hosted marketplace behavior.
- Fleet orchestration.
- A2A messaging.
- Remote agent control.
- Arbitrary code execution.
- Secret-bearing internal ops dashboards.
- Marketplace schema fields that drift from the current SSR registry contract.

The server may return or authorize checked bundles. Caller-local adapters perform writes into an explicitly configured local skills root.

## Current state

Gate status: **Gate 2 is complete.**

Closeout note: cobibean explicitly set Open SSR / Shared Skills Registry MCP as knwldg's top active project until it is shipped and tested in production. Next session should start Gate 3 and should not switch projects unless cobibean interrupts with a higher-priority issue.

Dated closeout memory: [`docs/memory/2026-07-09/open-ssr-gate-2-closeout-memory-2026-07-09.md`](2026-07-09/open-ssr-gate-2-closeout-memory-2026-07-09.md).

Gate 2 now includes:

- faithful backend/MCP SSR extraction;
- narrow audit/activity log;
- static registry-ledger UI;
- registry edit routes;
- negative-path guardrail tests;
- README UI demo GIF/screenshots;
- polished MCP client config examples.

Current known mainline commits:

```text
0a4b8c6 Port working SSR MCP core shape
1d8d8cb Add narrow SSR audit log and refresh extraction docs
b924569 Add control panel UI and registry editing
c562bd4 Add negative-path tests for SSR guardrails
211e505 Add README UI demo and MCP client examples
```

Latest verified main at time of this memory: `211e505`.

Latest verified test result at time of this memory:

```text
34 passed
```

## Implemented shape

Public repo shape now matches the working private SSR pattern closely enough to be a real extraction:

```text
client/stdio_server.py                MCP stdio adapter
config/shared_skills.yaml             YAML registry
src/shared_skills_registry_mcp/app.py HTTP tools, audit route, UI serving
src/shared_skills_registry_mcp/audit.py JSONL activity log
src/shared_skills_registry_mcp/config.py settings
src/shared_skills_registry_mcp/registry_edit.py UI/admin registry edits
src/shared_skills_registry_mcp/shared_skills.py SSR core: registry, bundle, install validation
ui/index.html                         zero-build control panel
docs/assets/                          README GIF/screenshots
examples/mcp-client-config/           MCP client examples
tests/                                happy path, audit, UI, admin, guardrail tests
```

## Registry schema

The public source-of-truth schema is the private-compatible `version: 1` shape:

```yaml
version: 1
skills:
  - name:
    title:
    summary:
    category:
    owner:
    source:
    docs_path:
    applicability:
    lifecycle_status:
    install_guidance:
    tags:
```

Do not reintroduce the earlier placeholder marketplace-ish schema as the primary contract.

## Implemented endpoints

Agent-facing SSR-only tool surface:

```text
POST /tools/list_shared_skills
POST /tools/search_shared_skills
POST /tools/describe_shared_skill
POST /tools/retrieve_shared_skill
POST /tools/install_shared_skill
```

Visibility/admin/UI surface:

```text
GET  /audit/recent?limit=N
GET  /registry/skills
PUT  /registry/skills/{name}
DELETE /registry/skills/{name}
GET  /ui
```

Admin registry editing is metadata-only. It points at existing `SKILL.md` files already on the server host. It does not upload files or execute code.

## Guardrails to preserve

Keep these behaviors protected by tests:

- duplicate registry entry rejection;
- active-visible filtering for agent-facing tool calls;
- safe path resolution;
- no absolute paths/null bytes/path escapes;
- allowed support directories only: `references/`, `templates/`, `scripts/`, `assets/`;
- `SKILL.md` required;
- YAML frontmatter validation;
- frontmatter `name` must match registry/requested name;
- file and aggregate bundle size limits;
- SHA-256 per file;
- checksum verification before writes;
- atomic local installs;
- failed installs do not write partial files outside the configured root;
- admin edit rejection keeps registry YAML loadable;
- audit records omit bundle content and redact secret-like fields.

## UI state

The UI is a single static file served by FastAPI at `/ui`.

Views shipped:

- Registry search/filter, including drafts/deprecated entries.
- Skill detail slide-over with metadata, files, sizes, checksum ribbons, and content previews.
- Activity timeline from `/audit/recent`.
- Editor for add/edit/deprecate/delete registry entries.

Design notes:

- no Node build step;
- no external fonts/CDNs;
- works offline;
- light paper + dark carbon themes via `prefers-color-scheme`;
- serif display + monospace data;
- signal-orange accent;
- stamped lifecycle badges;
- SHA-256 checksums rendered as click-to-copy hex ribbons.

## Docs/assets state

README currently includes:

- product promise;
- quickstart;
- control panel description;
- MCP usage;
- registry schema;
- bundle rules;
- audit log;
- non-goals;
- project layout;
- UI demo GIF near the top.

MCP config examples currently live at:

```text
docs/MCP-CLIENT-CONFIG.md
examples/mcp-client-config/shared-skills-registry.mcp.json
examples/mcp-client-config/hermes-add-shared-skills-registry.sh
```

README media currently lives at:

```text
docs/assets/open-ssr-demo.gif
docs/assets/open-ssr-control-panel.png
docs/assets/open-ssr-skill-detail.png
docs/assets/open-ssr-activity.png
```

## How to verify locally

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
pytest -q
uvicorn shared_skills_registry_mcp.app:app --host 127.0.0.1 --port 8765
```

Then open:

```text
http://127.0.0.1:8765/ui
```

HTTP smoke:

```bash
curl -s http://127.0.0.1:8765/healthz
curl -s -X POST http://127.0.0.1:8765/tools/list_shared_skills \
  -H 'Content-Type: application/json' \
  -d '{}'
```

## Next gate

Next gate is **Trust, safety, and polish pass**.

Recommended next work:

1. Final public-safety/secret scan across committed source, docs, examples, screenshots, and GIF metadata.
2. Fresh clone verification from scratch.
3. Public docs polish pass:
   - tighten README for first-time users;
   - make quickstart impossible to misread;
   - improve MCP client examples if any real client smoke exposes friction;
   - ensure docs never imply fleet/A2A/private control-plane features.
4. Security/threat model polish:
   - explicit file/write boundary;
   - audit redaction behavior;
   - local install trust assumptions;
   - unsupported directory and path traversal rejection.
5. Launch/demo prep:
   - short demo script;
   - screenshot/GIF sanity check on GitHub rendering;
   - one concise architecture diagram if useful;
   - tag/release candidate only after fresh clone passes.

## Good stopping point

As of `211e505`, this is a reasonable stopping point for the night:

- Gate 2 is complete.
- Backend, audit, UI, guardrail tests, README media, and MCP client examples are in place.
- Tests pass.
- The next work is polish/verification, not core product rescue.
