---
name: shared-skills-registry-access
description: Use when an agent or orchestrator needs to discover, inspect, retrieve, or install reusable skills from its configured Shared Skills Registry (SSR), while distinguishing registry access from caller-local installation.
version: 1.0.0
author: Shared Skills Registry MCP contributors
license: MIT
metadata:
  hermes:
    tags: [mcp, ssr, shared-skills, discovery, installation, orchestration]
    related_skills: []
---

# Shared Skills Registry Access

## Overview

Use the configured Shared Skills Registry (SSR) as the first place to look for reusable procedural capability. Search before improvising a duplicate skill, inspect the selected bundle before installation, and verify installation in the consuming agent's own runtime.

This workflow is runtime-neutral. It applies to any MCP-compatible orchestrator or agent that exposes the standard SSR tools. The registry supplies metadata and checksum-bearing bundles; the caller-local adapter decides whether and where files are written.

## When to Use

- An agent needs a reusable capability that may already exist in its SSR.
- An orchestrator is selecting capabilities for one or more workers.
- A user asks to inspect, retrieve, or install a shared skill.
- An install request succeeds at the registry layer but the skill is not visible locally.
- A team wants to avoid maintaining divergent copies of the same skill.

Do not use SSR as an arbitrary code-execution channel. A skill may contain instructions or scripts, but retrieval and installation do not grant permission to execute them.

## Standard SSR Tools

A compatible registry exposes these MCP operations:

- `list_shared_skills` — browse visible entries, optionally by category.
- `search_shared_skills` — find candidates from capability-oriented terms.
- `describe_shared_skill` — inspect one entry's metadata and applicability.
- `retrieve_shared_skill` — return `SKILL.md` and approved support files with checksums.
- `install_shared_skill` — request a caller-local installation through the configured adapter.

Tool names may be namespaced by the MCP client. Use the locally registered equivalents when a client prefixes server names.

## Consumer Agent Branch

Use this branch when installing a capability for the agent running the current task.

1. **Confirm SSR access.** Verify the five standard tools are available through the configured MCP server.
2. **Search by capability.** Use terms describing the missing work, not only a guessed skill name. Search multiple related terms when the first query is narrow.
3. **Describe before installing.** Check applicability, lifecycle status, owner, source, category, install guidance, and whether the capability actually matches the task.
4. **Retrieve and inspect.** Review the file list, `SKILL.md`, checksums, references, templates, scripts, and assets. Treat scripts as untrusted until reviewed.
5. **Install locally.** Call `install_shared_skill` only after selecting the exact skill. Use the runtime's configured local skills root; never invent or override a destination outside that boundary.
6. **Verify runtime visibility.** Confirm the installed `SKILL.md` exists in the expected local skill directory and start a fresh agent session or reload skills if the runtime caches discovery.
7. **Report exact state.** Distinguish “found,” “retrieved,” “installation authorized,” “written locally,” and “visible to a fresh runtime.”

Completion criterion: the intended agent can load the exact installed skill from its own runtime, or the report identifies the precise layer that remains incomplete.

## Orchestrator Branch

Use this branch when selecting skills for workers or multiple agents.

1. **Translate tasks into capabilities.** Derive search terms from each worker's assigned responsibility.
2. **Search once, select deliberately.** Prefer one canonical skill per capability. Avoid assigning overlapping skills unless their roles are explicitly different.
3. **Inspect dependencies.** Determine whether each bundle expects commands, credentials, APIs, files, operating systems, or companion skills. SSR distribution does not provide those prerequisites automatically.
4. **Respect agent boundaries.** Retrieval by the orchestrator does not prove a worker can access or install the skill. Each worker needs its own MCP access and caller-local install path.
5. **Delegate with an explicit contract.** Tell the worker which skill to retrieve, why it applies, what prerequisites to verify, and what proof of local visibility to return.
6. **Collect evidence per worker.** Record found/retrieved/installed/visible separately for every target. Do not infer fleet-wide installation from one successful caller.
7. **Avoid central god-mode writes.** Prefer worker-local installation. If an operator performs a cross-agent install, use the target runtime's documented profile/home configuration and verify the exact target path.

Completion criterion: every intended worker either proves local visibility of the selected skill or returns a bounded blocker without claiming installation.

## Selection Rules

When several skills match:

1. Prefer an active skill with the narrowest correct applicability.
2. Prefer a maintained, attributable source over an unknown copy.
3. Prefer a canonical umbrella over compatibility aliases or near-duplicates.
4. Inspect required tools and environment before choosing a dependency-heavy bundle.
5. Do not install merely because search returned a result; search is broad discovery, not approval.

## Safety Review

Before installing an unfamiliar or updated bundle:

- Confirm all paths are relative and remain under `SKILL.md`, `references/`, `templates/`, `scripts/`, or `assets/`.
- Verify the frontmatter `name` matches the selected registry entry.
- Verify every supplied checksum before writing.
- Review scripts and instructions for network calls, credential access, destructive commands, persistence, or unrelated data collection.
- Use an available skill scanner or static review tool when provenance is unfamiliar or policy requires it.
- Never place credentials, tokens, cookies, private keys, or environment files inside a shared skill bundle.

## Installation-State Vocabulary

Use precise language:

- **Listed/searched:** metadata was visible.
- **Described:** one exact registry entry was inspected.
- **Retrieved:** a bundle and checksums were returned.
- **Authorized:** server policy allowed an installation request.
- **Installed locally:** the caller-local adapter wrote validated files.
- **Runtime-visible:** a fresh or reloaded agent can discover and load the skill.

Only the final two states prove that the consuming agent can use the skill.

## Troubleshooting

### Tools are missing

Check the agent's MCP server configuration and run the client's server/tool discovery or connection test. Another agent's working SSR access does not prove this caller is configured.

### Search finds adjacent skills but not the expected one

Search is intentionally broad. Try the exact canonical name with `describe_shared_skill`. If exact describe fails, inspect the registry source or ask the registry owner whether the skill is published and active.

### Retrieve works but install does not

Confirm the caller-local adapter has an explicitly configured writable skills root. The central server should not write arbitrary remote profile paths.

### Install reports success but the skill is absent

Inspect the returned installed path, confirm `SKILL.md` exists there, verify its frontmatter name, and retry from a fresh runtime. Treat authorization-only responses as incomplete.

### A script exists in the bundle

Installation does not imply execution approval. Read the script, verify prerequisites and side effects, and follow the consuming environment's normal execution-approval rules.

## Verification Checklist

- [ ] The current agent exposes the standard SSR tools.
- [ ] Search and exact description identified the intended skill.
- [ ] Bundle paths, frontmatter, checksums, and scripts were reviewed.
- [ ] Required commands, credentials, APIs, and companion skills were checked separately.
- [ ] Installation stayed inside the configured caller-local skills root.
- [ ] A fresh or reloaded runtime can load the installed skill.
- [ ] Orchestrator reports preserve per-agent state instead of overclaiming fleet-wide success.
