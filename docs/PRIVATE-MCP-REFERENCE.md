# Private MCP → Shared Skills Registry MCP Reference

This document is a public-safe architecture reference for extracting the reusable Shared Skills Registry (SSR) pattern from a larger private cross-agent MCP server.

It intentionally does **not** document private infrastructure details, private agent names, network addresses, credentials, operator paths, or deployment topology. It captures the architectural lessons that matter for this open-source project.

## Why this exists

Shared Skills Registry MCP is being built from a real private SSR implementation that already supports skill discovery, bundle retrieval, and bounded local installation across multiple agents.

Before building a UI, we want the public project to stay aligned with the proven shape instead of drifting into a generic dashboard or marketplace.

The reusable product is:

- a registry of reusable agent skills;
- MCP tools for skill discovery and retrieval;
- checksum-bearing skill bundles;
- local-only install adapters;
- validation and audit visibility;
- no remote-control surface over agents.

## The private server, summarized

The private MCP server is larger than this project. It combines several layers:

1. **Fleet coordination** — roster/profile lookup, corpus lookup, health checks, and private operational surfaces.
2. **A2A messaging** — durable inboxes, acknowledgement, wakeups, and attention/dispatcher behavior.
3. **Fleet Capability Hub** — tool catalog, policy, approvals, runtime adapters, and visibility ledger.
4. **Shared Skills Registry** — skill metadata, list/search/describe, bundle retrieval, and bounded install authorization.

This public repo extracts layer 4 and only the minimum visibility/control needed to make it understandable and usable.

## What gets extracted

| Private capability | Public SSR equivalent | Notes |
|---|---|---|
| YAML-backed skill metadata | Registry metadata file | Keep the schema close to the working SSR model. |
| Skill discovery tools | MCP list/search/describe tools | Preserve familiar tool names where possible. |
| Source bundle retrieval | Checksum-bearing bundle response | Include `SKILL.md` plus allowed support files. |
| Install authorization | Local install review/authorization | Server should not mutate arbitrary remote profiles. |
| Caller-local install writer | Local adapter | Writes only into an explicitly configured local skill directory. |
| Visibility ledger | Narrow SSR activity log | Track registry/retrieve/install actions without storing secrets. |

## What does not get extracted

| Private capability | Public v1 treatment | Reason |
|---|---|---|
| Fleet roster/profile tools | Exclude | Private deployment-specific surface. |
| Corpus search | Exclude | Not part of reusable skill distribution. |
| A2A messaging | Exclude | Separate coordination product/layer. |
| Fleet health checks | Exclude | Private ops surface. |
| Generic tool catalog | Exclude from v1 | Broader than skills; possible later phase. |
| Approval system for arbitrary tools | Exclude from v1 | Too broad for the first public product. |
| Runtime adapter gateway | Exclude from v1 | Avoid implying arbitrary execution or remote control. |
| Private operator dashboard | Do not copy | Use only as inspiration for a narrow SSR UI. |

## Reference architecture

```text
┌─────────────────────────┐
│ Human / Agent Developer │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ SSR UI / CLI / MCP Tool │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Shared Skills Registry  │
│ - metadata              │
│ - search/list/describe  │
│ - bundle retrieval      │
│ - audit events          │
└────────────┬────────────┘
             │ returns checked bundle
             ▼
┌─────────────────────────┐
│ Local Install Adapter   │
│ - configured dest dir   │
│ - path validation       │
│ - checksum validation   │
│ - atomic writes         │
└────────────┬────────────┘
             │ writes locally only
             ▼
┌─────────────────────────┐
│ Local Agent Skill Dir   │
└─────────────────────────┘
```

The central design boundary:

> The registry can return a checked skill bundle. The local adapter decides whether and where to install it. The registry is not a remote-control plane for agents.

## Registry schema alignment

The existing private SSR model uses a simple YAML registry with `version: 1` and required skill metadata.

Recommended public v1 shape:

```yaml
version: 1
skills:
  - name: demo-research-brief
    title: Demo Research Brief
    summary: Create a concise research brief from public notes or URLs.
    category: demo
    owner: example
    source: local-example
    docs_path: examples/skills/demo-research-brief/SKILL.md
    applicability: Demonstrates registry browsing, MCP retrieval, and local install.
    lifecycle_status: active
    install_guidance: Install into a local scratch skills directory, then reload your agent skills if needed.
    tags:
      - demo
      - writing
      - research
```

Important fields:

- `name` — stable skill slug.
- `title` — human-readable name.
- `summary` — short description for search/list views.
- `category` — grouping/filtering.
- `owner` — person/team/source owner label.
- `source` — source label or upstream origin.
- `docs_path` — path to the skill's `SKILL.md`.
- `applicability` — when an agent should use this skill.
- `lifecycle_status` — active/draft/deprecated style status.
- `install_guidance` — what users or agents should do after install.
- `tags` — search/filter terms.

The public repo may add optional fields later (`license`, semantic version, runtime compatibility, risk level), but the first working slice should not diverge from the proven SSR shape without a concrete reason.

## Skill bundle rules

A skill bundle is rooted at the directory containing `SKILL.md`.

Always include:

```text
SKILL.md
```

Allowed support directories:

```text
references/
templates/
scripts/
assets/
```

Bundle response should include per-file metadata:

```json
{
  "path": "templates/brief.md",
  "size_bytes": 1234,
  "sha256": "...",
  "content": "..."
}
```

Validation rules to preserve:

- reject absolute paths;
- reject null bytes;
- reject `..` path escapes;
- reject unsupported top-level directories;
- enforce per-file size limits;
- enforce total bundle size limits;
- hash every file with SHA-256;
- require `SKILL.md`;
- validate `SKILL.md` frontmatter;
- require frontmatter `name` to match the requested skill.

## MCP tool surface

The public SSR MCP surface should start with these tools:

- `list_shared_skills(category?: string, limit?: number)`
- `search_shared_skills(query: string, category?: string, limit?: number)`
- `describe_shared_skill(name: string)`
- `retrieve_shared_skill(name: string, include_bundle?: boolean)`
- `install_shared_skill(name: string, target_category?: string, overwrite?: boolean)`

The private server exposes many other tools. Public v1 should not expose non-SSR tools.

## Local install adapter behavior

The install adapter should be local-first and explicit.

Install flow:

1. Request or receive a bundle from the registry.
2. Confirm the bundle is installable/authorized for the current context.
3. Resolve a configured local destination skill directory.
4. Validate every file path.
5. Verify every checksum.
6. Validate `SKILL.md` frontmatter.
7. Write files atomically.
8. Return written paths and reload guidance.

Install destination shape:

```text
<configured-skill-root>/<category>/<skill-name>/
```

The adapter must not silently write outside the configured skill root.

## Audit / activity model

The private server has a broad visibility ledger. Public v1 only needs a narrow SSR activity log.

Track events such as:

- registry loaded;
- skill listed/searched/described;
- bundle retrieved;
- install requested;
- install succeeded;
- install failed;
- validation failed;
- checksum mismatch;
- unsafe path rejected.

Audit records should store summaries and redacted arguments, not raw secrets or unnecessary full bundle content.

## UI implications

Do not design the UI as a generic fleet dashboard. Design it as visibility/control for the SSR workflow.

Minimum useful screens:

| Screen | Purpose |
|---|---|
| Registry browser | Search/filter available skills. |
| Skill detail | Show metadata, applicability, status, guidance. |
| Bundle view | Show file list, checksums, and allowed support files. |
| Install review | Show configured local destination and validation status. |
| Activity timeline | Show retrieve/install/validation events. |

The UI should make these boundaries obvious:

- A skill is metadata + bundle files.
- MCP discovery does not equal remote execution.
- Install is local and explicitly configured.
- The registry is not controlling agents remotely.
- Unsafe bundles should fail visibly.

## Side-by-side comparison

| Area | Private MCP server | Shared Skills Registry MCP public repo | Decision |
|---|---|---|---|
| Product scope | Fleet coordination + A2A + capability hub + SSR | SSR only | Keep public scope narrow. |
| Runtime | Python service + MCP stdio adapter | Scaffold moving toward same shape | Use Python/MCP shape, no Docker assumption. |
| Registry | YAML metadata + skill source tree | Example YAML + demo skill | Align schema with private SSR v1. |
| Discovery | list/search/describe implemented | Not implemented yet | Port registry core first. |
| Retrieval | Checked bundle with file hashes | Not implemented yet | Port bundle retrieval behavior. |
| Install | Server authorizes, local adapter writes | Not implemented yet | Preserve split exactly. |
| Visibility | Broad private ledger | Docs mention audit | Implement narrow SSR activity log. |
| UI | Private operator/admin visibility | Not built yet | Build SSR-specific UI after backend contracts exist. |
| Excluded layers | Fleet/A2A/corpus/health/tool hub | Not present | Keep excluded in v1. |

## Recommended implementation order before UI

1. Convert `registry.example.yaml` to the private-compatible v1 schema.
2. Port registry loading/list/search/describe into `packages/registry-core`.
3. Port bundle retrieval and validation.
4. Port local install adapter behavior.
5. Add tests for example skill → list/search/describe/retrieve → install into scratch dir.
6. Add SSR-only MCP server tools.
7. Add narrow activity/audit events.
8. Build UI against those real contracts.

## Bottom line

Shared Skills Registry MCP should copy the useful SSR pattern from the private MCP server, not the whole private control plane.

The public product promise is strongest when it stays simple:

> Publish reusable skills once, let agents discover them over MCP, retrieve checked bundles, and install them locally with visible guardrails.
