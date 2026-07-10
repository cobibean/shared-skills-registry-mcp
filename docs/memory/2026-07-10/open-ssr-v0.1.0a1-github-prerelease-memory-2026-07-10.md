# Open SSR v0.1.0a1 GitHub prerelease — 2026-07-10

## Release

- URL: https://github.com/cobibean/shared-skills-registry-mcp/releases/tag/v0.1.0a1
- GitHub release ID: `352256620`
- Package version: `0.1.0a1`
- Annotated tag: `v0.1.0a1`
- Candidate commit: `29a3a2286d1e52f3f36964609f2a9688422c3ab7`
- Annotated tag object: `897a522fbccdbcac571f0d0a85d08ae2db1d0510`
- Publication target: GitHub prerelease only
- PyPI: not published

## Candidate verification

- Local suite: 63 passed, one upstream Starlette/httpx deprecation warning.
- Candidate Actions run: https://github.com/cobibean/shared-skills-registry-mcp/actions/runs/29113193557
- All four jobs passed: fresh source and wheel/sdist release artifacts on Python 3.11 and 3.14.
- Actionlint, shell syntax, docs links, safety scan, and public candidate rendering passed.

## Immutable artifact provenance

Artifacts were built once from a clean clone of candidate `29a3a22` and never rebuilt between verification and publication.

```text
f832436167cba409f5431f12e455eef8b26457876460b63f14bad56ce459ce8c  shared_skills_registry_mcp-0.1.0a1-py3-none-any.whl
0f995b0608f42256265a670f548b543a32cf0e9e2ea50edd6608d5fb21000f03  shared_skills_registry_mcp-0.1.0a1.tar.gz
```

`SHA256SUMS` SHA-256:

```text
0cbb0cffb6bf22cb05b299ea8cbaa6745a1612353f493b29405a048ef1ad4f39
```

Verification included Twine, archive contents, alpha metadata, no `.agent`/`docs/memory` leakage, notices/resources, commands, clean wheel/sdist installs, UI, all five MCP tools, caller-local install, and audit.

## Publication sequence

1. Verified tag and release did not exist.
2. Created annotated tag on the exact candidate and pushed only that tag.
3. API-dereferenced the annotated tag to candidate `29a3a22`.
4. Created a draft GitHub prerelease.
5. Uploaded the already-verified wheel, sdist, and checksum file.
6. Read back asset names, sizes, states, and GitHub SHA-256 digests.
7. Published the draft as a prerelease.
8. Inspected the public page for prerelease state, tag/commit, security boundary, artifacts, and reporting link.

## Public consumer verification

- Downloaded all three assets from the public tagged release without repository credentials.
- `sha256sum -c SHA256SUMS` passed.
- Public downloads were byte-identical to the frozen local artifacts.
- Downloaded wheel and sdist installed in separate new unconstrained environments as `0.1.0a1`.
- Both resolved notices/resources and commands.
- Published wheel served the UI and passed the five-tool MCP, 14-entry catalog, caller-local install, and audit smoke.

## Repository closeout

Post-release closeout commit:

```text
235ea992934b0d47f24165671a252039a6a5022a Record v0.1.0a1 GitHub prerelease
```

Hosted workflow:

```text
https://github.com/cobibean/shared-skills-registry-mcp/actions/runs/29113861522
```

All four Python 3.11/3.14 source and wheel/sdist jobs passed. Release scratch environments, public-download consumer environments, test listeners, and temporary credential helpers were removed.

## Next work

No immediate release mutation is required. Future alpha changes use a new PEP 440 prerelease version and a new immutable tag; never move `v0.1.0a1` or replace its provenance silently.
