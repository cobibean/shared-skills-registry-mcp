# Security Boundary

Shared Skills Registry MCP is designed as a self-hosted registry and visibility layer for reusable AI-agent skills.

## Safe default boundary

- The registry can store, list, search, describe, and retrieve skill bundles.
- MCP tools should expose registry operations, not arbitrary host control.
- Local installs should happen only through configured local adapters.
- Install adapters must validate paths and checksums before writing files.
- Important actions should be written to an audit trail.

## Explicitly out of scope

- Remote control of agents.
- Fleet orchestration.
- A2A messaging.
- Arbitrary shell execution.
- Secret storage for internal operations.
- Hosted marketplace trust guarantees.

## Public release rule

No private fleet names, internal network paths, tokens, credentials, customer/client material, or cobi-specific operational docs belong in this repository.
