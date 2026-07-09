# Seed catalog

The default Open SSR registry is intentionally curated. It is not a copy of a private profile and it contains no default Hermes skills.

## Catalog composition

- 12 pinned public seed skills
- 1 Open SSR companion skill
- 1 explicit example skill
- 14 active entries total

## Public seed skills

| Skill | Category | Source |
|---|---|---|
| `project-memory` | Project continuity | `cobibean/project-memory-skill@498d15752c660ab2c2d7426a2668d03ae2934393` |
| `website-copywriting` | Marketing | `cobibean/website-copywriting-skill@35b727026d6300740c4760b3f59530c7a5b40ecc` |
| `codebase-design` | Software development | `mattpocock/skills@6eeb81b5fcfeeb5bd531dd47ab2f9f2bbea27461` |
| `diagnosing-bugs` | Software development | `mattpocock/skills@6eeb81b5fcfeeb5bd531dd47ab2f9f2bbea27461` |
| `domain-modeling` | Software development | `mattpocock/skills@6eeb81b5fcfeeb5bd531dd47ab2f9f2bbea27461` |
| `prototype` | Software development | `mattpocock/skills@6eeb81b5fcfeeb5bd531dd47ab2f9f2bbea27461` |
| `tdd` | Software development | `mattpocock/skills@6eeb81b5fcfeeb5bd531dd47ab2f9f2bbea27461` |
| `triage` | Software development | `mattpocock/skills@6eeb81b5fcfeeb5bd531dd47ab2f9f2bbea27461` |
| `handoff` | Productivity | `mattpocock/skills@6eeb81b5fcfeeb5bd531dd47ab2f9f2bbea27461` |
| `teach` | Productivity | `mattpocock/skills@6eeb81b5fcfeeb5bd531dd47ab2f9f2bbea27461` |
| `writing-great-skills` | Skill authoring | `mattpocock/skills@6eeb81b5fcfeeb5bd531dd47ab2f9f2bbea27461` |
| `systematic-debugging` | Software development | `obra/superpowers@6fd4507659784c351abbd2bc264c7162cfd386dc` |

The bundles under `seed/skills/` preserve the approved SSR bundle content from those pinned source copies, with only repository-level whitespace normalization where required. Attribution and licenses are recorded in [`../THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).

## Open SSR companion skill

`shared-skills-registry-access` is maintained in this repository. It provides two runtime-neutral branches:

- a consumer-agent branch for finding, reviewing, installing, and verifying a skill from that agent's configured SSR;
- an orchestrator branch for selecting capabilities and collecting per-worker install/visibility evidence without central god-mode writes.

## Example-only skill

`demo-research-brief` is labeled as an example in both registry metadata and `SKILL.md`. It exists to smoke-test the complete list/search/describe/retrieve/install flow and is not presented as a production research methodology.

## Security scan record

Static SkillSpector scans covered all 14 bundles.

- 10 imported seed skills, the Open SSR companion skill, and the example skill: score `0`, severity `LOW`, no findings.
- `diagnosing-bugs`: score `27`, severity `MEDIUM`. The single heuristic finding matches the comment phrase “show instruction” in a human-in-the-loop shell template; it does not print or request a system prompt.
- `systematic-debugging`: score `34`, severity `MEDIUM`. The two heuristic findings match a debugging example that inspects macOS signing keychain state. The commands are directly visible in the upstream skill, do not extract secret values, and are relevant to the documented debugging scenario. Treat them as explicit commands requiring normal execution approval, not as silent install-time behavior.

No bundle exceeded the publication gate (`>50`, `HIGH`, or `CRITICAL` overall score/severity). Installation does not execute scripts or examples.

## Verification contract

The test suite must continue proving:

- exactly the intended 14 names are present;
- no default Hermes skill is registered;
- every bundle retrieves with checksums;
- every bundle installs into a scratch local skills root;
- the example remains labeled `example`;
- the caller-local installation boundary remains intact.
