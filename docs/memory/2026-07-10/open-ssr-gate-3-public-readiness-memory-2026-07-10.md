# Open SSR Gate 3 public-readiness artifacts — 2026-07-10

## Scope

Completed the six public-readiness artifacts requested after the real-protocol and packaging hardening phase:

1. full threat model;
2. Known Limitations;
3. private vulnerability-reporting policy;
4. contributor guide;
5. replacement README GIF built from the real catalog and genuine MCP activity;
6. truthful launch post/video outline.

Gate 3 itself remains open for human onboarding and security-operator dogfood. Gate 4 remains open for release/version go-no-go.

## Durable artifacts

- `docs/THREAT-MODEL.md`
- `docs/KNOWN-LIMITATIONS.md`
- `SECURITY.md`
- `CONTRIBUTING.md`
- `docs/assets/open-ssr-demo.gif`
- `docs/DEMO-SCRIPT.md`
- `.agent/runs/2026-07-10-gate-3-public-readiness/`

README and `docs/TASK-BOARD.md` link and track these artifacts.

## Security posture documented

The supported alpha is a trusted single-operator, loopback or controlled-private-network deployment. It has no built-in HTTP authentication, authorization, TLS, CSRF protection, tenant isolation, rate limiting, or route-level admin policy. Every reachable client can use tool, admin, and audit routes.

The packaged launcher rejects wildcard/public bind literals, but that is an accidental-exposure guardrail rather than authentication. Direct Uvicorn invocation, containers, proxies, tunnels, port forwarding, or firewall rules can broaden exposure.

The caller-local adapter enforces the configured install root, rejects model-supplied overrides by default, validates paths/frontmatter/checksums, and stages whole-directory replacement with rollback. It still trusts its configured backend, does not independently cap the complete backend response, and does not reject duplicate paths. Checksums prove consistency with the returned manifest, not publisher or server authenticity.

Installation does not execute content, but downstream agents may follow skill instructions or execute bundled scripts later. Audits are minimized operational JSONL, not authenticated, tamper-evident, or forensic logs.

GitHub private vulnerability reporting was enabled and verified at the repository-native advisory route. No reporting email was invented.

## Demo asset

The old synthetic three-frame GIF was replaced by a six-stage workflow:

1. real 14-entry catalog;
2. `systematic-debugging` search;
3. real source/applicability/install metadata;
4. real 11-file bundle with sizes and SHA-256 rows;
5. exactly five events produced through an official-SDK MCP stdio session: list, search, describe, retrieve, install;
6. return to the populated registry.

Final asset: 800×450, 31 frames, 16.25 seconds, 2,265,739 bytes. Source capture used only public catalog data and scratch loopback audit/install paths. Scratch services and files were removed.

## Independent-review remediation

Two read-only reviewers audited the source security boundary and contributor/release workflow. Their findings were folded into the durable docs, including direct-Uvicorn bind bypass, unauthenticated admin/audit reachability, trusted-backend assumptions, overwrite defaults, missing bundle references, optional/ambiguous audit behavior, and unsupported multi-writer behavior.

The contributor review also found that the built wheel contained imported skill bundles but omitted `THIRD_PARTY_NOTICES.md`. The notice is now forced into `shared_skills_registry_mcp/_bundled/THIRD_PARTY_NOTICES.md`, and CI verifies the installed resource.

## Verification before push

- full suite: 61 passed, one known upstream Starlette/httpx deprecation warning;
- actionlint 1.7.12: checksum verified and passed;
- wheel build: 74 files, packaged third-party notice verified;
- clean wheel outside checkout: HTTP UI, five-tool official MCP smoke, caller-local installation, and audits passed;
- release-document local links: passed;
- GIF metadata and six-stage visual review: passed;
- changed-file public-safety scan: no credentials, private paths, private addresses, keys, or JWTs;
- scratch services and environments: removed.

## Public closeout

Implementation commit:

```text
dbc1c6bd437bbef2f31b1b823879408bb9499bf3 Complete Gate 3 public readiness artifacts
```

Hosted workflow:

```text
https://github.com/cobibean/shared-skills-registry-mcp/actions/runs/29108657727
```

All four jobs passed: fresh source and built wheel on Python 3.11 and 3.14. Public GitHub rendering was inspected after push: the README GIF loaded at native 800×450, the Important alpha warning rendered, and links to Threat Model, Known Limitations, Security, and Contributing were present.

## Next gate

1. Run first-time-user onboarding dogfood against the exact release candidate.
2. Run a security-operator comprehension review against Threat Model and Known Limitations.
3. Resolve alpha version semantics: package metadata currently says `0.1.0`, while the proposed Git tag has been `v0.1.0-alpha`; prefer a deliberate PEP 440 prerelease such as `0.1.0a1` or explicitly document the mismatch.
4. Decide the release artifact contract: GitHub release only versus PyPI; add sdist/metadata validation and artifact publication checks as appropriate.
5. Conduct Gate 3 public-readiness go/no-go, then Gate 4 release go/no-go before tagging.
