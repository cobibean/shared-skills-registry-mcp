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

Gate status: **Gate 2 is complete. The real-protocol release-hardening block of Gate 3 is complete.**

Open SSR / Shared Skills Registry MCP remains knwldg's top active project until it is shipped and production-tested. The next work is the remaining Gate 3 threat model, Known Limitations, vulnerability-reporting, contribution-guidance, and final public-readiness review.

Latest hardening memory: [`docs/memory/2026-07-09/real-mcp-stdio-release-hardening-memory-2026-07-09.md`](2026-07-09/real-mcp-stdio-release-hardening-memory-2026-07-09.md).

Earlier Gate 2 closeout memory: [`docs/memory/2026-07-09/open-ssr-gate-2-closeout-memory-2026-07-09.md`](2026-07-09/open-ssr-gate-2-closeout-memory-2026-07-09.md).

Current verified state includes:

- faithful backend/MCP SSR extraction;
- narrow audit/activity log;
- static registry-ledger UI;
- registry edit routes;
- negative-path guardrail tests;
- README UI demo GIF/screenshots;
- polished MCP client config examples;
- curated 14-entry public catalog with 13 canonical production/companion bundles and one explicit example;
- packaged HTTP and stdio console commands with wheel-safe registry, catalog, example, and UI assets;
- caller-local installation with configured-root authority, fail-closed override behavior, and staged whole-bundle replacement that removes stale files and rolls back failed swaps;
- real MCP, generic SDK, clean local Hermes, separate remote Hermes, fresh-clone, and built-wheel verification.

Current known mainline commits:

```text
49b12ac Curate public skill catalog
4e35d47 Harden real MCP stdio release path
4f5351a Make skill overwrites stale-free and atomic
```

Latest verified main before this rolling-memory refresh: `4f5351a`.

Latest verified test result:

```text
55 passed, 1 upstream deprecation warning
```

GitHub Actions run `29051012487` passed fresh-clone MCP and built-wheel packaging jobs on Python 3.11 and 3.14.

## Implemented shape

Public repo shape now matches the working private SSR pattern closely enough to be a real extraction:

```text
client/stdio_server.py                compatibility shim
config/shared_skills.yaml             YAML registry
skills/                               canonical production/companion bundles
src/shared_skills_registry_mcp/app.py HTTP tools, audit route, UI serving
src/shared_skills_registry_mcp/cli.py packaged HTTP entry point
src/shared_skills_registry_mcp/stdio_server.py packaged MCP stdio adapter
src/shared_skills_registry_mcp/runtime_paths.py source/wheel asset resolution
src/shared_skills_registry_mcp/audit.py JSONL activity log
src/shared_skills_registry_mcp/config.py settings
src/shared_skills_registry_mcp/registry_edit.py UI/admin registry edits
src/shared_skills_registry_mcp/shared_skills.py SSR core: registry, bundle, install validation
scripts/mcp_stdio_smoke.py             generic protocol smoke client
ui/index.html                          zero-build control panel
docs/assets/                           README GIF/screenshots
examples/mcp-client-config/            MCP client examples
tests/                                 HTTP, protocol, UI, admin, and guardrail tests
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
pip install -c requirements/ci-constraints.txt -e '.[test]'
pytest -q
shared-skills-registry-http
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

Finish **Gate 3 — Public safety/readiness review**.

Completed in the real-protocol hardening block:

- final changed-file public-safety and secret scans;
- exact public fresh-clone verification;
- generic MCP, clean local Hermes, and separate remote Hermes validation;
- installed-wheel catalog/UI/stdio verification;
- deterministic GitHub Actions coverage.

Recommended next work:

1. Complete the threat model and document trust assumptions for metadata editing, retrieval, local installation, and unauthenticated deployment.
2. Add a clear Known Limitations section.
3. Add vulnerability-reporting guidance and contributor documentation.
4. Perform final screenshot/GIF metadata and GitHub-rendering checks.
5. Prepare the short launch/demo outline.
6. Run the Gate 3 go/no-go review before creating an alpha tag.

## Good stopping point

As of the current release-hardening closeout:

- Gate 2 is complete and the protocol/packaging portion of Gate 3 is complete.
- Real MCP stdio, caller-local installation, source checkout, built wheel, clean local Hermes, separate remote Hermes, and hosted CI all pass.
- Remaining work is public-readiness documentation and release review, not core product or transport rescue.
