# Shared Skills Registry MCP

**Open SSR is a self-hosted control panel and MCP server for sharing reusable AI-agent skills across multiple agents and devices.**

Shared Skills Registry MCP gives AI-agent builders a simple way to publish reusable skills once, browse them in a dashboard, expose them over MCP, and install them safely into local agent skill directories.

## MVP promise

MVP = **registry + UI + MCP access + local install path**.

- People can add or import skills.
- People can browse and search skills in a UI.
- Agents can list, search, describe, and retrieve skills over MCP.
- Installs happen safely into a local configured skill directory.
- Important actions appear in an audit trail.

## What this is not

- Not an internal fleet control plane.
- Not fleet orchestration.
- Not A2A messaging.
- Not remote control of agents.
- Not a hosted marketplace.
- Not arbitrary code execution.
- Not a secret-bearing internal ops dashboard.

## Demo journey

> Publish a skill → see it in the UI → retrieve it over MCP → install it locally.

See [`docs/DEMO-SCRIPT.md`](docs/DEMO-SCRIPT.md).

## Planned project layout

```text
apps/api/               Registry API and audit log service
apps/web/               Dashboard UI
packages/registry-core/ Shared registry types, validation, bundle logic
packages/mcp-server/    MCP tools for skill list/search/describe/retrieve
packages/adapters/      Local install adapters for supported agent runtimes
examples/skills/        Generic demo skills safe for public release
docs/                   Product promise, demo script, task board, security boundary
```

## Status

Build lane setup is in progress. This scaffold is intentionally plain until the first vertical slice is implemented.
