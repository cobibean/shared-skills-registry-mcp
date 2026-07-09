---
name: project-memory
description: >-
  Use this skill when starting or finishing substantial project work that would
  benefit from durable continuity across Codex, Claude, or other agent sessions.
  It teaches agents to read recent project memory before work and write concise
  Markdown session memory after meaningful work under
  docs/memory/YYYY-MM-DD/descriptive-slug-memory-YYYY-MM-DD.md, including
  what happened, what was learned, decisions made, gotchas, changed files,
  verification, constraints, open decisions, and useful next context while
  avoiding secrets and sensitive details.
---

# Project Memory

Use project memory to preserve durable project context for humans and future
agents.

Project memory is a record of what happened, what was learned, what decisions
were made, and what still needs judgment. It is not primarily an agent handoff.
Only include handoff or resume instructions when work is incomplete,
interrupted, or the user explicitly asks for a handoff.

Project memory lives at:

```txt
docs/memory/YYYY-MM-DD/descriptive-slug-memory-YYYY-MM-DD.md
```

Memory is append-only by default. Create a new file for new work.
Do not overwrite, delete, or rewrite prior memory unless the user explicitly
asks.

## Before Work

For substantial work:

1. Find the project root.
2. Check whether `docs/memory/` exists.
3. If it exists, list recent memory files:

```bash
find docs/memory -type f -name '*.md' | sort | tail -10
```

4. Read the most recent relevant memory files.
5. Read any source-of-truth docs referenced by those files when they matter for
   the task.
6. Briefly summarize the relevant context before acting.

If no memory exists, continue normally.
Do not create memory at the start unless the user asks.

## After Meaningful Work

Create a new memory file when the session produced context that future humans or
agents would be annoyed to rediscover.

Use today's local date and create the dated folder if needed:

```txt
docs/memory/YYYY-MM-DD/
```

Use a lowercase descriptive slug:

```txt
docs/memory/2026-05-18/auth-flow-memory-2026-05-18.md
```

Do not write memory for tiny edits, quick answers, routine formatting, or work
that leaves no durable decisions, constraints, verification, or next actions.

## What To Capture

Capture durable context, not a transcript:

- session summary
- what was learned
- decisions made
- open decisions that still need judgment
- files created or changed
- source-of-truth docs
- commands, tests, builds, screenshots, or checks run
- known constraints, gotchas, and failure modes
- open questions
- recommended next work, when useful
- handoff or resume notes, only when work is incomplete or explicitly handed off

## What Not To Capture

Do not store:

- secrets, API keys, tokens, passwords, or private credentials
- PHI, unnecessary personal data, or sensitive client details
- raw logs containing secrets or private data
- verbose transcripts
- every routine command
- speculation that will not help future work

Mention that a secret was configured or verified without recording the secret
value.

## Memory Template

Use only the sections that matter:

```md
# <Project or Task> Memory - YYYY-MM-DD

## Session summary

## What we learned

## Decisions made

## Open decisions

## Files created or changed

## Source-of-truth docs

## Commands and verification

## Gotchas and constraints

## Open questions

## Recommended next work

## Handoff or resume notes
```

## Writing Style

Write Markdown a human or agent can skim in under two minutes.

Prefer:

- short sections
- bullets for concrete facts
- exact file paths
- exact commands when verification matters
- clear next actions when there are real next actions
- the reason behind decisions when that reason would be easy to lose

Avoid:

- long narrative
- generic handoff framing when the work is already complete
- duplicated repo docs
- vague claims like "fixed stuff"
- rewriting history from older memory files

## Safety Rules

- Follow stricter local repo instructions first.
- Never overwrite prior memory unless explicitly asked.
- If existing memory must be amended, preserve prior content and add a dated
  note.
- Redact sensitive values.
- If old memory conflicts with current source-of-truth docs, trust the newer
  source of truth and mention the conflict.
- If work is interrupted, write current status, exact resume instructions, and
  known verification state.
