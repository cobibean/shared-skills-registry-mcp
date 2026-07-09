# Launch Checklist

## Repo Setup

- Choose repo name: `project-memory-skill` is the recommended default.
- Add `SKILL.md`, `README.md`, `LICENSE`, `templates/`, `examples/`,
  `docs/`, and `agents/`.
- Confirm `SKILL.md` frontmatter has only `name` and `description`.
- Confirm examples contain no secrets, credentials, PHI, or private client
  details.
- Add repository topics:
  - `agents`
  - `codex`
  - `claude`
  - `ai-agents`
  - `developer-tools`
  - `memory`

## Validation

- Run skill validation:

```bash
python /path/to/quick_validate.py .
```

- Read the README as a first-time user.
- Read `SKILL.md` as an agent would: confirm the workflow is clear without
  opening examples.
- Install locally and use it once in a real repo.

## First Release

- Publish the GitHub repo.
- Add a short description:

```txt
A tiny agent skill for durable project memory under docs/memory/YYYY-MM-DD/.
```

- Create the first release tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Dogfood

- After publishing, create the first real memory file for this repo:

```txt
docs/memory/YYYY-MM-DD/project-memory-skill-launch-memory-YYYY-MM-DD.md
```

- Capture what shipped, any naming decisions, validation performed, and
  recommended next improvements.
