# Demo Script

This is the target demo for the first public vertical slice.

The demo should make one idea obvious:

> Agent skills should not be scattered across random folders. Put them in a registry, let agents discover them over MCP, and install them locally with visibility and guardrails.

## Demo promise

In three minutes, a viewer should understand:

- what a reusable agent skill is;
- why a registry is useful;
- how an MCP-compatible agent finds a skill;
- how the skill bundle is retrieved;
- how a local install happens without giving the registry remote-control power.

## Demo path

```text
start with one demo skill → list/search it through SSR → inspect/retrieve the bundle → install into a scratch local skill directory → show audit/validation output
```

## Scene 1 — The messy before state

Show or describe the normal problem:

> I have useful agent skills, but they are spread across profiles, project folders, machines, and chat history. If I want another agent to use one, I either copy/paste it manually or hope I remember where the latest version lives.

The viewer should immediately get the pain: reusable skills exist, but distribution is sloppy.

## Scene 2 — The registry

Show `registry.example.yaml` and the example `demo-research-brief` bundle.

Point out that a registry entry answers the practical questions:

- What is this skill called?
- What does it do?
- Where is the bundle?
- What version/status/risk level is it?
- Which runtimes can install it?

## Scene 3 — MCP discovery

Show an MCP-compatible agent using the registry tools:

- list shared skills;
- search for a skill;
- describe the selected skill;
- retrieve the bundle.

The important point is not the exact UI. The important point is that the agent can discover a reusable capability without the user pasting the whole skill into chat.

## Scene 4 — Bundle inspection

Show the returned bundle contents:

```text
SKILL.md
templates/brief.md
```

Call out that skills can include both instructions and support files. This is why copy/paste is not enough once skills become real reusable packages.

## Scene 5 — Local install

Install the demo skill into a scratch local skill directory.

The install should demonstrate guardrails:

- destination directory is explicitly configured;
- bundle paths are checked before writing;
- checksum/validation output is visible;
- install result is recorded.

Say clearly:

> The registry is not remotely controlling my agent. It is providing a checked bundle; the local adapter installs it into a local configured destination.

## Scene 6 — Human visibility

Show the human-facing view or audit output:

- skill was listed/searched/retrieved;
- install was attempted;
- install succeeded or failed with a clear reason;
- destination path and checksum are visible without exposing secrets.

The goal is to make MCP infrastructure feel inspectable instead of invisible.

## Closing line

> Shared Skills Registry MCP is a self-hosted package manager/control panel for reusable AI-agent skills. It lets you publish a skill once, discover it across agents over MCP, and install it locally without exposing a whole private agent fleet.

## Demo acceptance checklist

- [ ] A fresh viewer understands the problem in under 30 seconds.
- [ ] One skill moves through the whole path.
- [ ] MCP discovery is visible.
- [ ] Local install is bounded to a scratch/configured directory.
- [ ] No private names, paths, secrets, or internal fleet details appear.
- [ ] Demo uses the local Python/MCP runtime shape from this repo.
