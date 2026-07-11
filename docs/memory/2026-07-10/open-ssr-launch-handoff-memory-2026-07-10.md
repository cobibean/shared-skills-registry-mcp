# Open SSR launch handoff — 2026-07-10

## Purpose

Durable restart point after publishing the first Open SSR alpha. Cobibean plans to resume tomorrow and begin launch/content work.

## Status

Open SSR is technically released and ready to post about. No release-engineering blocker remains.

- Repository: https://github.com/cobibean/shared-skills-registry-mcp
- Release: https://github.com/cobibean/shared-skills-registry-mcp/releases/tag/v0.1.0a1
- Package: `0.1.0a1`
- Immutable tagged candidate: `29a3a2286d1e52f3f36964609f2a9688422c3ab7`
- Annotated tag object: `897a522fbccdbcac571f0d0a85d08ae2db1d0510`
- Release ID: `352256620`
- Final pre-handoff `main`: `74547312bd29f9f99c3a2ef40ad981e001b8b538`
- PyPI: intentionally not published
- Gates 2–4: complete

The repository was clean and local `HEAD` matched `origin/main` before this handoff note was added.

## Proven release evidence

- Local suite: 63 passed; one upstream Starlette/httpx deprecation warning.
- Candidate CI: https://github.com/cobibean/shared-skills-registry-mcp/actions/runs/29113193557
- Post-release CI: https://github.com/cobibean/shared-skills-registry-mcp/actions/runs/29113861522
- Final evidence CI: https://github.com/cobibean/shared-skills-registry-mcp/actions/runs/29113992350
- All runs used the four-job Python 3.11/3.14 fresh-source plus wheel/sdist matrix.
- Public wheel and sdist were downloaded, checksum-verified, installed in separate clean environments, and consumer-smoked.
- Published wheel passed UI, 14-entry catalog, five MCP tools, caller-local install, and audit.

Artifact SHA-256:

```text
f832436167cba409f5431f12e455eef8b26457876460b63f14bad56ce459ce8c  shared_skills_registry_mcp-0.1.0a1-py3-none-any.whl
0f995b0608f42256265a670f548b543a32cf0e9e2ea50edd6608d5fb21000f03  shared_skills_registry_mcp-0.1.0a1.tar.gz
```

Do not move `v0.1.0a1` or replace its artifacts. Any future alpha fix gets a new PEP 440 prerelease and tag.

## Tomorrow's next work

The next work is launch/content, not more release engineering:

1. Use `docs/DEMO-SCRIPT.md` to draft the first launch post.
2. Use the existing README GIF; a video is optional.
3. Link the repository, release, quickstart, Known Limitations, Threat Model, CONTRIBUTING, and private vulnerability reporting.
4. Choose posting channels and sequence.
5. Ask for feedback on first-time onboarding, trust-boundary clarity, and MCP-client compatibility.
6. Monitor GitHub issues and private vulnerability reports after posting.

No platform-specific launch copy has been drafted yet.

## Messaging boundaries

Always call the release an **alpha** for **loopback or controlled private networks**.

Do not claim:

- safe direct public-Internet exposure;
- built-in authentication, authorization, TLS, CSRF protection, rate limits, accounts, roles, or multi-tenancy;
- signed packages, verified publisher identity, sandboxing, or malware safety;
- hosted-marketplace or production-SLA status;
- PyPI availability;
- Windows/macOS release-gated support.

Canonical launch claims and forbidden claims are in `docs/DEMO-SCRIPT.md`. Security details are in `docs/KNOWN-LIMITATIONS.md` and `docs/THREAT-MODEL.md`.

## Useful artifacts

- `README.md`
- `docs/DEMO-SCRIPT.md`
- `docs/releases/v0.1.0a1.md`
- `docs/KNOWN-LIMITATIONS.md`
- `docs/THREAT-MODEL.md`
- `docs/RELEASE-CHECKLIST.md`
- `docs/assets/open-ssr-demo.gif`
- `.agent/runs/2026-07-10-v0.1.0a1-github-prerelease/implementation-notes.html`
- `docs/memory/project-memory.md`

## Review nuance

- Direct clean public-clone onboarding passed.
- The first delegated novice replay timed out and the bounded retry returned an infrastructure-overload error, so neither counts as independent novice pass evidence.
- Independent security comprehension did complete at 10/10; language precision findings were remediated.
- This nuance is already recorded in the Gate 3/4 ledgers and should not be rewritten as an external-human onboarding study.

## Environment note

The active Obsidian vault currently resolves to temporary-looking `/tmp/tmp.vU6Pv7uwPF/vault`. A reset Session Log and Daily Log backlink were written there, but this Git-backed file is the authoritative durable handoff until vault routing is fixed.
