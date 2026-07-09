# Shared Skills Registry MCP

**A self-hosted registry and MCP server for reusable AI-agent skills.**

Shared Skills Registry MCP lets you keep agent skills in one place, make them discoverable to multiple agents, and install them into local agent runtimes without turning the registry into a remote-control system.

Think of it as a small package manager for agent skills:

- publish a skill once;
- search and inspect it from a UI or an MCP-compatible agent;
- retrieve the exact bundle with metadata and checksums;
- install it into a configured local skill directory;
- keep a visible audit trail of what was retrieved or installed.

## Why this exists

Agent teams are starting to build useful skills, prompts, workflows, and support files. The problem is that they usually live in scattered local folders:

- one skill copy on a laptop;
- another inside a Claude Code project;
- another inside a Hermes profile;
- another pasted into a repo or chat thread;
- no clear version, source, owner, or install history.

That gets messy fast. Skills drift, agents miss updates, and humans lose track of what is actually installed where.

Shared Skills Registry MCP gives those skills a home.

## What it does

The first public version is intentionally narrow:

1. **Registry** — stores public-safe skill metadata and bundle locations.
2. **MCP access** — exposes tools so agents can list, search, describe, and retrieve skills.
3. **Local install path** — installs only into configured local skill directories, with path/checksum validation.
4. **Visibility** — gives humans a simple way to see available skills, details, validation state, and important activity.

The core demo path is:

```text
publish a skill → discover it over MCP → inspect/retrieve the bundle → install it locally
```

## Who this is for

Use this if you are:

- running more than one AI agent or agent runtime;
- building reusable skills you want to share across agents/devices;
- tired of copy-pasting `SKILL.md` folders by hand;
- experimenting with MCP as infrastructure, not just one-off tools;
- trying to make agent capabilities visible and governable.

## How it works

A skill bundle is a directory containing a `SKILL.md` plus optional support files such as references, templates, scripts, or assets.

The registry tracks metadata like:

- name and description;
- version/status/category/tags;
- bundle path/source;
- supported runtimes;
- risk level;
- checksum/validation state.

Agents talk to the registry through MCP tools. Local installs are handled by an adapter that writes to an explicitly configured local destination. The registry should not get arbitrary shell access or mutate remote agent profiles directly.

## Planned MCP tools

The initial MCP surface mirrors the existing SSR shape:

- `list_shared_skills`
- `search_shared_skills`
- `describe_shared_skill`
- `retrieve_shared_skill`
- bounded install/authorization flow for local skill installation

## Example registry entry

```yaml
skills:
  - name: demo-research-brief
    title: Demo Research Brief
    description: A generic public-safe example skill used to demonstrate registry browsing, MCP retrieval, and local install.
    version: 0.1.0
    category: demo
    tags: [demo, writing, research]
    license: MIT
    status: draft
    risk_level: low
    bundle_path: examples/skills/demo-research-brief
    installable_runtimes: [generic-filesystem]
```

See [`registry.example.yaml`](registry.example.yaml) and [`examples/skills/demo-research-brief`](examples/skills/demo-research-brief).

## What this is not

This project is deliberately not a full agent fleet control plane.

It is not:

- fleet orchestration;
- A2A messaging;
- remote control of agents;
- a hosted marketplace;
- arbitrary code execution;
- a secret-bearing internal ops dashboard.

The point is to make reusable skills portable and visible without giving the registry broad power over your agents.

## Current status

This repository currently contains the public scaffold, product boundary, example registry, and demo skill bundle. The next implementation step is to port the working SSR-style registry/MCP behavior into this public repo as a small vertical slice.

See:

- [`docs/PRODUCT-PROMISE.md`](docs/PRODUCT-PROMISE.md)
- [`docs/DEMO-SCRIPT.md`](docs/DEMO-SCRIPT.md)
- [`docs/TASK-BOARD.md`](docs/TASK-BOARD.md)
- [`docs/SECURITY-BOUNDARY.md`](docs/SECURITY-BOUNDARY.md)

## Development shape

No Docker assumption. The first working version should run as a normal local service/MCP server, matching the existing SSR MCP direction as closely as possible.

Planned layout:

```text
apps/api/               Registry API and audit log service
apps/web/               Dashboard UI
packages/registry-core/ Shared registry metadata, validation, bundle logic
packages/mcp-server/    MCP tools for skill list/search/describe/retrieve
packages/adapters/      Local install adapters for supported agent runtimes
examples/skills/        Generic demo skills safe for public release
docs/                   Product promise, demo script, task board, security boundary
tests/                  Registry, MCP, and local install verification
```
