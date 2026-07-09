# Security Boundary

Shared Skills Registry MCP is designed as a self-hosted registry and visibility layer for reusable AI-agent skills.

## Safe default boundary

- The registry can store, list, search, describe, and retrieve skill bundles.
- MCP tools should expose registry operations, not arbitrary host control.
- Local installs should happen only through configured local adapters.
- Install adapters must validate paths and checksums before writing files.
- Important actions should be written to an audit trail.

## Caller-local install authority

- `SSR_MCP_SKILLS_ROOT` is configured on the stdio adapter running beside the consuming MCP client. The registry service does not receive a remote agent-home path and does not write into remote profiles.
- The configured root is authoritative. Model- or caller-supplied `skills_root` overrides are rejected by default so a tool call cannot redirect an install to another writable location.
- A trusted operator can explicitly opt into dynamic local roots with `SSR_MCP_ALLOW_SKILLS_ROOT_OVERRIDE=1`; this broadens the adapter's write authority and should not be enabled for ordinary agent use.
- Install paths remain category/name descendants of the selected root and are validated along with bundle paths, frontmatter, and SHA-256 checksums before files are committed.
- Missing root configuration, attempted root override, checksum failure, path escape, and frontmatter mismatch fail closed. Local install success and policy failures are auditable when `SSR_MCP_AUDIT_LOG` is configured.

## Explicitly out of scope

- Remote control of agents.
- Fleet orchestration.
- A2A messaging.
- Arbitrary shell execution.
- Secret storage for internal operations.
- Hosted marketplace trust guarantees.

## Public release rule

No private fleet names, internal network paths, tokens, credentials, customer/client material, or cobi-specific operational docs belong in this repository.
