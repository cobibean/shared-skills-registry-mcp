# Goal: Open SSR Gate 3 human readiness and go/no-go

## Objective

Test the public repository as a first-time user and security-minded operator, verify release artifacts beyond the editable/wheel CI path, remediate findings, and issue a source-backed Gate 3 public-readiness decision without silently choosing or publishing an alpha version.

## Finishing criteria

- A clean external clone follows the README from setup through UI, real MCP discovery, caller-local installation, and audit evidence without undocumented operator knowledge.
- An independent reviewer can answer deployment, authority, provenance, execution, audit, and vulnerability-reporting questions from public docs alone.
- Wheel and sdist build from clean public source; metadata and bundled notices/resources validate; artifacts work outside the checkout.
- Human-visible README/GIF/security/contributor links render publicly.
- Any onboarding, documentation, packaging, or security finding is fixed and regression-tested.
- Source suite, actionlint, safety scan, fresh clone, wheel/sdist, hosted CI, and cleanup pass.
- `docs/TASK-BOARD.md` records an explicit Gate 3 go/no-go with evidence.
- No tag, GitHub Release, or PyPI publication occurs until the alpha version/artifact decision is explicit.

## Runtime goal coupling

Ledger: `.agent/runs/2026-07-10-gate-3-human-readiness/implementation-notes.html`

## Parent goal

Gate 3 — Public safety/readiness review.

## Escape hatch

Stop at the narrow Gate 4 decision if package version, tag name, or publication target remains ambiguous. Do not infer an irreversible release version.

## Safety constraints

- Use only the public repository and scratch homes/install roots for dogfood.
- Do not reuse private agent configuration, credentials, or infrastructure.
- Keep services on loopback and remove all scratch artifacts.
- Treat independent reviewers as evidence, not authority; verify their operational claims directly.
