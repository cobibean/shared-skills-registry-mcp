# Launch post drafts — Open SSR v0.1.0a2

Drafts for the first public launch. Claims follow the allowed/forbidden lists in
[`DEMO-SCRIPT.md`](DEMO-SCRIPT.md); do not add capability claims when adapting per platform.
Fill in the PyPI link only after the `v0.1.0a2` release workflow has published successfully.

## Long form (Show HN / r/LocalLLaMA / r/mcp / blog)

**Title options**

- Show HN: Open SSR – a self-hosted, runtime-neutral registry for AI-agent skills (MCP)
- I got tired of agent skills drifting across machines, so I built a self-hosted skill registry any MCP client can use

**Body**

I got tired of reusable agent skills living as drifting folders across laptops, Claude Code
projects, agent profiles, and chat history — so I extracted the registry layer from my private
agent setup and made it a small self-hosted OSS project.

Agent skills stop being simple prompts quickly. They grow templates, scripts, references, and
provenance — and then copies drift across machines and agents, with no version, source, owner, or
install history. First-party plugin marketplaces solve this for one runtime at a time. I wanted
the part they won't build: a registry **I** host that **every** MCP-capable agent can pull from.

Open SSR is one small Python service:

- a YAML-backed registry with a curated 14-entry public starter catalog (documented sources and notices);
- five real MCP tools — list, search, describe, retrieve, install — plus matching HTTP endpoints;
- a zero-build web control panel for browsing, inspecting bundles/checksums, and watching activity;
- a caller-local install adapter: the server never writes into an agent's home — it returns a
  checksum-bearing bundle, and the adapter beside the consuming agent validates paths, frontmatter,
  and SHA-256s, then installs only beneath an explicitly configured skills root;
- staged whole-bundle replacement, so stale files don't survive updates;
- a JSONL audit trail of every tool call and install;
- optional bearer-token auth: one `shared-skills-registry-generate-token` command, set `SSR_MCP_AUTH_TOKEN` on the service and in each agent's `.env`, and the tool/admin/audit routes require it.

Install:

```bash
pipx install --pip-args=--pre shared-skills-registry-mcp
shared-skills-registry-http
```

Then connect Claude Code, Claude Desktop, Cursor, Windsurf, Hermes, or a generic MCP SDK — the
repo has copy-paste configs for each.

Being upfront about the trust posture: this is an **alpha for loopback or controlled private
networks**. Auth is a single optional shared token (no accounts, roles, or TLS — it crosses the
wire in plaintext); checksums prove bundle consistency, not publisher identity; installation never
executes content, but your agent may later follow what it installed — normal tool-approval hygiene
still applies. The repo ships a real threat model and
a known-limitations doc instead of marketing claims.

I'd especially like feedback on three things:

1. Can a first-time user get from install to a successful MCP skill install without help?
2. Are the trust boundary and limitations obvious before you deploy it?
3. Which MCP clients or skill formats should get the next compatibility tests?

Repo: https://github.com/cobibean/shared-skills-registry-mcp
Release: https://github.com/cobibean/shared-skills-registry-mcp/releases/tag/v0.1.0a2
Threat model: https://github.com/cobibean/shared-skills-registry-mcp/blob/main/docs/THREAT-MODEL.md
Known limitations: https://github.com/cobibean/shared-skills-registry-mcp/blob/main/docs/KNOWN-LIMITATIONS.md

## Short form (X / Bluesky / Mastodon)

Post 1 (hook):

> Agent skills shouldn't live as drifting folders copied between machines and agent profiles.
>
> Open SSR: a self-hosted, runtime-neutral skill registry. Publish once; any MCP client (Claude
> Code, Cursor, Hermes, your own SDK) can discover, inspect checksums, and install locally.
>
> `pipx install --pip-args=--pre shared-skills-registry-mcp`
>
> [repo link + GIF]

Post 2 (trust boundary, reply):

> Honest scope: it's an alpha for loopback/private networks — auth is one optional shared token
> (no TLS), checksums ≠ publisher signatures, installs never execute content. Threat model and
> known-limitations docs are in the repo, not fine print. Feedback on onboarding + trust clarity
> very welcome.

## Posting sequence

1. Publish `v0.1.0a2` (tag push → release workflow → PyPI + GitHub prerelease) and verify a clean
   `pip install --pre` from PyPI first.
2. Long-form post (Show HN or one subreddit — not both the same day) with the README GIF.
3. Short-form thread linking the long-form post.
4. Monitor GitHub issues and private vulnerability reports; answer onboarding friction reports
   quickly — they are the launch's primary ask.
