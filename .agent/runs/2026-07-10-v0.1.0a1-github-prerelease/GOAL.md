# Goal: Open SSR v0.1.0a1 GitHub prerelease

## Objective

Publish the first Open SSR alpha as a GitHub-only prerelease using package version `0.1.0a1` and annotated tag `v0.1.0a1`, attaching one verified wheel, one verified sdist, and `SHA256SUMS` built exactly once from the tagged clean candidate commit.

## Finishing criteria

- Package metadata, release notes, artifact names, annotated tag, and GitHub prerelease all use `0.1.0a1` / `v0.1.0a1` consistently.
- Candidate source passes local tests, workflow lint, safety scan, public rendering, and hosted Python 3.11/3.14 source plus wheel/sdist CI.
- Final artifacts are built once from a clean clone of the exact candidate commit, pass Twine/archive/metadata/clean-install/UI/MCP/install/audit checks, and receive verified SHA-256 checksums.
- The annotated tag points to the verified candidate commit and is never moved.
- GitHub prerelease is created with the already-verified artifacts; no PyPI upload occurs.
- Public assets are downloaded, checksums verified, installed outside the checkout, and consumer-smoked.
- Release URL, tag SHA, artifact hashes, workflow runs, consumer evidence, and cleanup are recorded durably.

## Runtime goal coupling

Ledger: `.agent/runs/2026-07-10-v0.1.0a1-github-prerelease/implementation-notes.html`

## Safety constraints

- Do not publish to PyPI.
- Do not rebuild after final artifact verification.
- Do not move or replace a public tag.
- Keep release credentials profile-local and out of logs, files, remotes, and artifacts.
- Treat any failed or ambiguous gate before tag publication as NO-GO and fix forward with a new candidate.
