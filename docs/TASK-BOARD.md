# Build Lane Task Board

## Gate 1 — Product promise

Status: **locked**

Owner: project owner decision, implementation agent records and enforces.

## Lane A — Repo and product story

Owner: docs agent

- [x] Create repo scaffold.
- [x] Seed README with product promise, MVP boundary, non-goals, and demo journey.
- [x] Add product promise doc.
- [ ] Review README tone so it sounds like a real public project, not internal notes.
- [ ] Add first screenshot/GIF placeholder once UI exists.

## Lane B — Registry core

Owner: backend agent

- [ ] Define registry entry shape.
- [ ] Define skill bundle file rules.
- [ ] Implement list/search/describe/retrieve over local sample registry.
- [ ] Add checksum generation/verification.
- [ ] Add tests for invalid paths and malformed bundles.

## Lane C — MCP server

Owner: MCP agent

- [ ] Expose `list_shared_skills`.
- [ ] Expose `search_shared_skills`.
- [ ] Expose `describe_shared_skill`.
- [ ] Expose `retrieve_shared_skill`.
- [ ] Document how to connect an MCP-compatible agent.

## Lane D — UI

Owner: UI agent

- [ ] Registry list page.
- [ ] Skill detail page.
- [ ] Validation/install status area.
- [ ] Audit/activity view.
- [ ] Empty/error states that make sense to new users.

## Lane E — Local install adapter

Owner: adapter agent

- [ ] Configure a local destination skill directory.
- [ ] Validate safe relative bundle paths.
- [ ] Write only allowed files/directories.
- [ ] Verify checksum before install.
- [ ] Record install result in audit log.

## Lane F — Trust, safety, and launch polish

Owner: security/docs/QA agents

- [ ] Security boundary doc.
- [ ] Secret/private-term scan before public release.
- [ ] Fresh clone smoke test.
- [ ] Known limitations section.
- [ ] Launch post/video outline.

## Cobi review gates

- [ ] Gate 2: First demo review.
- [ ] Gate 3: Public safety/readiness review.
- [ ] Gate 4: Release/go-no-go.
