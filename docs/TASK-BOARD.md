# Build Lane Task Board

## Gate 1 — Product promise

Status: **locked**

Owner: project owner decision, implementation agent records and enforces.

## Lane A — Repo and product story

Owner: docs agent

- [x] Create repo scaffold.
- [x] Seed README with product promise, MVP boundary, non-goals, and demo journey.
- [x] Add product promise doc.
- [x] Rewrite README so it explains what this is, why to use it, and how to run it.
- [x] Capture and embed a polished README GIF using the real 14-entry catalog, real bundle checksums, and genuine MCP activity.

## Lane B — Registry core

Owner: backend agent

- [x] Align registry entry shape with the working private SSR v1 schema.
- [x] Define skill bundle file rules.
- [x] Implement list/search/describe/retrieve over local sample registry.
- [x] Add checksum generation/verification.
- [x] Add tests for invalid/malformed registry and checksum failure.

## Lane C — MCP / HTTP server

Owner: MCP agent

- [x] Expose HTTP `/tools/list_shared_skills`.
- [x] Expose HTTP `/tools/search_shared_skills`.
- [x] Expose HTTP `/tools/describe_shared_skill`.
- [x] Expose HTTP `/tools/retrieve_shared_skill`.
- [x] Expose HTTP `/tools/install_shared_skill` as authorization/bundle-return path.
- [x] Add packaged SSR-only MCP stdio adapter with a compatibility shim at `client/stdio_server.py`.
- [x] Add polished MCP client configuration examples.
- [x] Prove all five tools through real MCP stdio, generic SDK, clean local Hermes, and separate remote Hermes consumers.

## Lane D — UI

Owner: UI agent

- [x] Registry list page.
- [x] Skill detail page.
- [x] Validation/install status area (bundle checksums, missing-source warnings).
- [x] Audit/activity view.
- [x] Empty/error states that make sense to new users.
- [x] Registry entry editing (add/edit/deprecate/delete, metadata-only).

## Lane E — Local install adapter

Owner: adapter agent

- [x] Configure a local destination skill directory.
- [x] Validate safe relative bundle paths.
- [x] Write only allowed files/directories.
- [x] Verify checksum before install.
- [x] Record install result in audit log.

## Lane F — Trust, safety, and launch polish

Owner: security/docs/QA agents

- [x] Security boundary doc.
- [x] Public-safe private MCP extraction reference.
- [x] Secret/private-term scan before public release.
- [x] Fresh local test smoke: `pytest -q`.
- [x] Deterministic fresh-clone plus built-wheel and built-sdist GitHub Actions verification.
- [x] Full threat model with assets, actors, trust boundaries, controls, residual risks, and safe deployment profiles.
- [x] Known Limitations section and detailed alpha limitations document.
- [x] Private vulnerability-reporting guidance with GitHub private reporting enabled.
- [x] Contributor setup, catalog, security, attribution, test, and pull-request guidance.
- [x] Launch post and three-minute video/demo outline.
- [x] Independent source review of security claims and contributor/release workflow.
- [x] Package and verify `THIRD_PARTY_NOTICES.md` alongside imported wheel and sdist bundles.
- [x] Clean first-time-user onboarding replay plus independent security-operator comprehension dogfood against the candidate.

## Review gates

- [x] Gate 2: First demo review.
- [x] Gate 3: Public safety/readiness review — **GO** for public-source readiness; Gate 4 must change the stable-looking `0.1.0` package version to an approved PEP 440 prerelease before tagging.
- [ ] Gate 4: Release/go-no-go.
