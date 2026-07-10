# Launch and demo outline

This is the truthful alpha launch story for Shared Skills Registry MCP (Open SSR).

## One-line promise

> Publish a reusable agent skill once, let MCP-compatible agents discover it, inspect the exact bundle, and install it locally with checksums, bounded writes, stale-free updates, and visible activity.

## Audience

- people maintaining skills across several agents, projects, or machines;
- MCP client and agent-framework builders;
- teams that want a self-hosted catalog without granting a central service write access to every agent home;
- skill authors who want provenance, support files, and install visibility beyond copy/paste.

## Claims the launch may make

- self-hosted Python service and zero-build control panel;
- 14-entry public starter catalog with documented sources and notices;
- five real MCP tools: list, search, describe, retrieve, install;
- caller-local adapter with an explicit install root;
- path, frontmatter, size, and SHA-256 validation;
- staged whole-bundle replacement that removes stale files;
- source, wheel, and sdist tests on Python 3.11 and 3.14;
- verified generic MCP, clean local Hermes, and separate remote Hermes consumers.

## Claims the launch must not make

- safe for direct public Internet exposure;
- authenticated, multi-tenant, or hosted;
- signed packages or verified publisher identity;
- malware-proof or sandboxed skills;
- automatic execution, dependency resolution, or fleet deployment;
- production support SLA;
- Windows/macOS release-gated support.

Link [`KNOWN-LIMITATIONS.md`](KNOWN-LIMITATIONS.md) and [`THREAT-MODEL.md`](THREAT-MODEL.md) in the launch post rather than hiding the alpha boundary.

## README GIF: 16-second loop

The README GIF should communicate the product without terminal text:

1. **Registry — populated:** show the real 14-entry catalog and category cards.
2. **Search:** filter for `systematic-debugging`.
3. **Inspect:** open the real registry entry and show source, applicability, tags, and install guidance.
4. **Bundle:** reveal the 11-file bundle and SHA-256 rows.
5. **Activity:** switch to the genuine audit timeline populated by list, search, describe, retrieve, and install calls.
6. **End card:** return to the populated registry with the server-up indicator visible.

Do not show private profiles, tokens, hostnames, or operator paths. Use a scratch audit log and installation root.

## Three-minute launch video

### 0:00–0:20 — The problem

Visual: a few scattered `SKILL.md` folders, then the populated Open SSR registry.

Voiceover:

> Useful agent skills stop being simple prompts pretty quickly. They grow templates, scripts, references, versions, and provenance—and then copies drift across machines and agent profiles. Open SSR gives those skills one self-hosted catalog and a real MCP distribution path.

### 0:20–0:45 — Start the packaged service

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
shared-skills-registry-http
```

Visual: open <http://127.0.0.1:8765/ui>.

Call out:

- loopback by default;
- 14 public-safe starter entries;
- registry, detail, bundle, activity, and metadata editing in one zero-build UI.

### 0:45–1:15 — Discover a real skill

Use `systematic-debugging`, not the tutorial-only example.

Visual actions:

1. search `systematic-debugging`;
2. open the skill;
3. show pinned source metadata and applicability;
4. reveal the complete bundle;
5. point to file paths, sizes, and SHA-256 checksums.

Voiceover:

> An agent can discover the capability by metadata, then retrieve the exact multi-file bundle instead of asking a human to paste instructions into chat.

### 1:15–1:55 — Prove real MCP and local installation

Run the generic client against a scratch destination:

```bash
tmp="$(mktemp -d)"
python scripts/mcp_stdio_smoke.py \
  --url http://127.0.0.1:8765 \
  --skills-root "$tmp/skills" \
  --audit-log "$tmp/local-audit.jsonl"
```

Show that the client:

- initializes MCP over stdio;
- discovers all five tools;
- lists, searches, describes, retrieves, and installs;
- writes only under the configured scratch root;
- creates a caller-local audit record.

Voiceover:

> The HTTP registry never writes into the agent's home. It returns an authorized bundle; the stdio adapter beside the consuming agent validates and installs it locally.

### 1:55–2:20 — Show update safety

Plant or show a harmless stale file in a scratch-installed skill, then reinstall with `overwrite=true`.

Call out:

- the complete new bundle is staged first;
- stale files disappear instead of surviving an update;
- a failed final swap restores the prior directory when possible;
- no skill script is executed during installation.

### 2:20–2:40 — Human visibility

Switch the UI to Activity.

Show genuine events for:

```text
list_shared_skills
search_shared_skills
describe_shared_skill
retrieve_shared_skill
install_shared_skill
```

Voiceover:

> The registry path is inspectable. You can see what was requested, whether it succeeded, and what was installed without logging bundle bodies or obvious secret values.

### 2:40–3:00 — Boundary and call to action

Voiceover:

> This is an alpha for loopback or controlled private deployments. It is not an authenticated public marketplace and checksums are not publisher signatures. If you maintain skills across agents, try the release, connect your MCP client, and tell us where onboarding or the trust model is still unclear.

Visual links:

- README quickstart;
- MCP client configuration;
- Known Limitations;
- Threat Model;
- contributing and private vulnerability reporting.

## Launch post outline

### Hook

> I got tired of reusable agent skills living as drifting folders across profiles, repos, and chat history—so I extracted the registry layer from my private agent setup and made it a small self-hosted MCP project.

### Problem

- skills are multi-file capabilities, not just prompts;
- manual copying loses source, version, checksums, and install history;
- a central service should not need god-mode write access to every agent machine.

### What shipped

- YAML registry plus 14-entry public-safe starter catalog;
- FastAPI service and zero-build UI;
- packaged HTTP and MCP stdio commands;
- generic MCP and Hermes client examples;
- caller-local bounded installation;
- real protocol, wheel, local/remote consumer, and Python floor/ceiling CI.

### Trust posture

State plainly:

- loopback/private alpha;
- no built-in auth/TLS or public-hosting claim;
- no signing or malware guarantee;
- installation does not execute content;
- human review and normal agent tool approvals still matter.

### Ask

Request feedback on three specific areas:

1. Can a first-time user get from clone to successful MCP install without help?
2. Are the trust boundary and limitations obvious before deployment?
3. Which MCP clients or skill formats should receive the next compatibility tests?

### Links

- repository;
- quickstart;
- demo GIF/video;
- Known Limitations;
- Threat Model;
- CONTRIBUTING;
- private vulnerability reporting.

## Recording checklist

- [ ] Use the exact tagged release candidate.
- [ ] Use only public catalog entries and scratch paths.
- [ ] Populate activity through genuine tool calls.
- [ ] Confirm no shell history, credentials, private profiles, hostnames, or private network details appear.
- [ ] Record at 1280×720 or 1440×900 with readable browser zoom.
- [ ] Keep cursor movement deliberate and remove loading/dead time.
- [ ] Add captions for silent playback.
- [ ] Verify commands from a clean environment.
- [ ] Show the alpha boundary before the final call to action.
- [ ] Recheck links and GitHub rendering after upload.

## Release acceptance

The launch package is ready when:

- a fresh viewer understands the problem in under 30 seconds;
- one real production skill moves through discover → inspect → retrieve → install;
- the caller-local boundary is stated and visible;
- the activity view contains genuine events;
- Known Limitations and private security reporting are one click away;
- no private or synthetic-looking data appears;
- the exact release artifact passes source, wheel, and human onboarding smokes.
