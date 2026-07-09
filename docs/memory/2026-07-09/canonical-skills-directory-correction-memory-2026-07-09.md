# Canonical skills directory correction memory - 2026-07-09

## Session summary

Corrected the Open SSR starter catalog layout after user review. Bundled starter skills had been placed under `seed/skills/`, which incorrectly created a separate filesystem tier from user-added skills.

## Decision

`skills/<name>/` is the single canonical bundle tree for both bundled starters and user-added production skills.

“Seed,” “starter,” “imported,” and similar labels are registry provenance/catalog concepts. They must not create parallel bundle roots.

The explicit smoke-test bundle may remain under `examples/skills/` because it is labeled as an example rather than a production skill.

## Changes

- Moved all 13 production bundles from `seed/skills/` to `skills/` without content changes.
- Updated all 13 production `docs_path` values to `skills/<name>/SKILL.md`.
- Removed the `seed/` directory completely.
- Updated README instructions so users place their own bundles alongside starters under `skills/<name>/`.
- Updated docs and tests to enforce the canonical layout.

## Verification

Product commit: `425d481` (`Use canonical skills directory`).

- Local suite: `49 passed`.
- Fresh clone from GitHub at `425d481bcb514baa4f5383f71330a3fb0c8e489c`: `49 passed`.
- Fresh clone had 13 directories under `skills/`, no `seed/` directory, and all 13 production registry entries used `skills/...` paths.
- Live fresh-clone smoke: list HTTP 200 with 14 entries; `project-memory` retrieve HTTP 200 with `source_docs_path=skills/project-memory/SKILL.md` and 8 files; UI HTTP 200.
- Secret/private-term scan over the canonical skills tree and changed registry/docs: zero findings.
- Temporary server and fresh-clone directory were removed.

## Regression rule

Tests must continue asserting that every non-example registry entry has a `docs_path` beginning with `skills/`.
