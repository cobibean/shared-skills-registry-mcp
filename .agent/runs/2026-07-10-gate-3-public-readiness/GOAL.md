# Goal: Open SSR Gate 3 public-readiness artifacts

## Objective

Complete the six remaining public-readiness artifacts: a source-grounded threat model, clear Known Limitations, vulnerability-reporting guidance, contributor documentation, a polished README GIF made from the real catalog and audit activity, and a short launch/demo outline.

## Finishing criteria

- Threat model names assets, actors, trust boundaries, implemented controls, residual risks, and safe deployment requirements without claiming controls the product does not have.
- README contains a prominent Known Limitations section linked to deeper security guidance.
- `SECURITY.md` gives a private reporting path, supported-version policy, scope, response expectations, and safe disclosure guidance.
- `CONTRIBUTING.md` documents setup, canonical skill/catalog rules, required verification, security hygiene, attribution, and pull-request expectations.
- `docs/assets/open-ssr-demo.gif` is replaced with a legible, optimized capture using the actual 14-entry catalog and genuine list/search/describe/retrieve/install activity.
- Launch/demo outline tells a truthful alpha story and demonstrates the actual packaged workflow.
- README links the new artifacts; the stale screenshot task and six Gate 3 artifact tasks are updated accurately.
- Automated tests, workflow lint, link/path checks, asset metadata checks, public-safety scans, GitHub push, and hosted CI pass.

## Runtime goal coupling

Ledger: `.agent/runs/2026-07-10-gate-3-public-readiness/implementation-notes.html`

## Parent goal

Gate 3 — Public safety/readiness review.

## Escape hatch

Pause only for a public vulnerability-reporting address that cannot be inferred safely, a visual direction requiring user judgment, or an external publishing credential. Default to GitHub private vulnerability reporting if enabled/available; do not invent an email address.

## Safety constraints and protected paths

- Do not expose credentials, private hostnames, network topology, private profiles, customer material, or internal procedures.
- Do not claim authentication, sandboxing, provenance, signatures, moderation, or cross-platform support that the code does not implement.
- Do not bind the demo service publicly.
- Generate demo activity only in scratch audit/install paths and remove them after capture.
- Preserve canonical production bundles under `skills/` and the example under `examples/skills/`.
- Gate 3 and Gate 4 remain open until human/readiness review and release go/no-go occur.
