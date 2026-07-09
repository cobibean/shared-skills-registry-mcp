# Upstream source — project-memory

Imported from public GitHub repository:

- Repository: https://github.com/cobibean/project-memory-skill
- Commit: `498d15752c660ab2c2d7426a2668d03ae2934393`
- Skill name: `project-memory`

## SSR bundle contents

This SSR bundle includes:

- `SKILL.md` from upstream, unchanged.
- `templates/memory-template.md`.
- Public example memory files from upstream `examples/` under `references/examples/`.
- `docs/launch-checklist.md` under `references/launch-checklist.md`.
- `agents/openai.yaml` under `references/agent-metadata/openai.yaml`.

This SSR bundle intentionally excludes:

- `.git/`, `.gitignore`, `LICENSE`, and packaging-only repository files.
- `assets/project-memory-skill-social-preview.png`; it is a binary image and exceeds the SSR text file limit.
- Upstream `docs/memory/` dogfood memory examples; they are repo-launch history, not required for runtime use, and include public account-specific provenance terms.
