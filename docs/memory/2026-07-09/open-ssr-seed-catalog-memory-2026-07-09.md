# Open SSR seed catalog memory - 2026-07-09

## Session summary

Expanded the default Open SSR registry from one demo bundle to a curated catalog with 12 approved public seed skills, one Open SSR companion skill, and one explicitly labeled example skill.

## Decisions made

- The default catalog contains no default Hermes skills.
- Third-party seed bundles are copied from pinned public sources and retain registry attribution.
- `shared-skills-registry-access` is maintained as a runtime-neutral Open SSR companion skill with separate consumer-agent and orchestrator branches.
- `demo-research-brief` remains available only as an explicit example/smoke-test bundle.
- The private SSR's 94-entry catalog will not be copied wholesale into Open SSR.

## Files created or changed

- `seed/skills/` — 12 pinned seed bundles plus `shared-skills-registry-access`.
- `config/shared_skills.yaml` — 14 active entries total.
- `examples/skills/demo-research-brief/SKILL.md` — explicit example labeling.
- `docs/SEED-CATALOG.md` — catalog composition, provenance, security findings, and verification contract.
- `THIRD_PARTY_NOTICES.md` and root `LICENSE`.
- `README.md`, `registry.example.yaml`, and registry/core tests.

## Commands and verification

- Clean editable environment created with `python3 -m venv .venv` and `pip install -e '.[test]'`.
- Full suite: `49 passed`, with one upstream Starlette/httpx deprecation warning.
- Every one of the 14 registry bundles retrieves with checksums and installs into a scratch local skills root in tests.
- Registry/frontmatter/allowlist validation: 14 entries, 14 unique names, zero issues.
- Private-term and secret-shape scan over the staged catalog/docs: zero findings.
- The 12 imported seed bundles preserve their approved private-SSR source content; one trailing blank line was normalized for a clean public diff.
- SkillSpector static scan covered all 14 bundles. Overall maximum score was 34/MEDIUM; no overall HIGH/CRITICAL bundle. Two reviewed heuristic findings are documented in `docs/SEED-CATALOG.md`.
- Fresh clone from GitHub at product commit `98e606e` installed cleanly and passed all 49 tests.
- Fresh-clone live smoke returned HTTP 200 for health, list, describe, retrieve, and UI; list count was 14, the generalized access skill was present, and `systematic-debugging` retrieved 11 files.

## Related internal inventory

A separate operator-only knowledge-corpus review dated 2026-07-09 inventories the private SSR's custom-skill publication candidates. It is intentionally not copied into this public repository because it discusses private fleet provenance and consolidation work.

## Recommended next work

Continue Gate 3 with final public docs/security polish and production deployment planning. Strong next standalone public skill candidates are `soul-grader`, a combined runtime-neutral Open SSR publisher/operator skill, and the `obsidian-memory-wiki` kit.
