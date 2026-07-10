# Threat model

This document describes the security model of Shared Skills Registry MCP (Open SSR) `0.1.x`. It is written for operators deciding where to run the service, contributors changing trust-sensitive code, and users deciding whether to install a skill.

Open SSR is a self-hosted registry and caller-local installer. It is **not** an authentication gateway, malware sandbox, signed package ecosystem, or Internet-facing multi-tenant service.

See also:

- [`SECURITY.md`](../SECURITY.md) for private vulnerability reporting;
- [`SECURITY-BOUNDARY.md`](SECURITY-BOUNDARY.md) for the concise product boundary;
- [`KNOWN-LIMITATIONS.md`](KNOWN-LIMITATIONS.md) for current alpha limitations.

## Security objectives

Open SSR should:

1. expose only registry discovery, bundle retrieval, local installation authorization, audit, and metadata-editing behavior;
2. keep installation writes beneath an operator-configured caller-local skills root;
3. reject malformed, escaping, or checksum-invalid bundles before installation, and enforce documented size limits at registry retrieval;
4. avoid executing bundle content during retrieval or installation;
5. fail closed when the caller-local destination is absent or a model attempts to redirect it;
6. avoid placing bundle content or obvious secret-bearing values in the audit log;
7. avoid accidental wildcard or public-address binding;
8. preserve the previous installed bundle when a replacement cannot be committed safely.

It does not attempt to prove that a skill is benign, that a publisher is trustworthy, or that a reachable HTTP client is authorized.

## Assets

| Asset | Why it matters |
|---|---|
| Registry YAML | Controls which skills are visible and which local bundle paths they reference. |
| Skill bundle files | Become instructions, scripts, templates, references, or assets available to an agent after installation. |
| Caller-local skills root | A writable part of the consuming agent's capability surface. |
| Agent runtime and prompts | May later interpret or execute content from an installed skill. |
| Audit JSONL | May reveal skill names, operation timing, local destination paths, and errors. |
| Service availability | Discovery, retrieval, UI, and registry editing depend on the HTTP service. |
| Source and attribution metadata | Helps humans review provenance but is not a cryptographic identity guarantee. |

Credentials are deliberately outside the product model. Open SSR does not store provider keys or agent credentials.

## Actors

### Trusted operator

The operator chooses the bind address, registry file, content roots, audit path, and caller-local install root. Anyone who can change those values or write the underlying files already has equivalent local authority and is trusted accordingly.

### Registry editor

A client able to reach the HTTP service can use the metadata-editing routes. There is currently no built-in user authentication or role model. On the default loopback deployment this is treated as operator-local authority. On any shared private network, reachability alone is **not** sufficient authorization; place an authenticated proxy in front or do not expose the editing service.

### MCP client or agent

An MCP client may be partially untrusted: a model can choose tool arguments unexpectedly. The stdio adapter therefore treats its configured `SSR_MCP_SKILLS_ROOT` as authoritative and rejects per-call root overrides by default.

### Skill author or upstream source

Skill content is untrusted input. A skill can contain persuasive instructions or scripts that become dangerous if an agent later follows or executes them. Installation is not approval to execute.

### Network attacker

The default design assumes an attacker cannot reach the loopback service. Private-network deployments assume the operator controls network membership or adds transport authentication and encryption. Open SSR itself does not provide TLS or HTTP authentication.

## Trust boundaries and data flow

```text
skill author / local files
          |
          | operator review, registry metadata
          v
+------------------------+
| Open SSR HTTP service  |
| registry + retrieval   |
| UI + metadata editing  |
| server audit           |
+------------------------+
          |
          | HTTP bundle and checksums
          v
+------------------------+       MCP stdio       +------------------+
| caller-local adapter   | <-------------------- | MCP client/agent |
| validates and installs |                       +------------------+
+------------------------+
          |
          | bounded local write
          v
 configured skills root
```

Important boundary: the HTTP service returns a bundle and installation authorization. The stdio adapter beside the consuming client performs the local write. The registry service does not receive a remote agent-home path and does not centrally write into remote profiles.

## Implemented controls

### Network exposure

- Default bind is `127.0.0.1`.
- Wildcard binds (`0.0.0.0` and `::`) are rejected.
- Accepted non-loopback literals are limited to private, link-local IPv6, or Tailscale CGNAT ranges.
- Arbitrary public IP literals and non-`localhost` hostnames are rejected.

These controls reduce accidental exposure. They do not authenticate clients on an accepted private address.

They are also launcher guardrails, not an unbreakable network policy. An operator can bypass them by invoking Uvicorn directly, or broaden reachability through a container, proxy, tunnel, port forward, or firewall rule. Use `shared-skills-registry-http` for the supported launch path and verify the effective network boundary separately.

### Registry validation and editing

- Registry documents use `yaml.safe_load` and require schema version `1`.
- Required fields, names, lengths, tags, and duplicate names are validated.
- Metadata edits validate the complete resulting registry before replacing the live YAML.
- Registry writes use a temporary sibling file followed by `os.replace`.
- Editing changes metadata only; it cannot upload bundle files or execute commands.
- Successful and failed edits are written to the server audit log.

An entry may reference a currently missing `docs_path`; the admin view reports that state and agent retrieval fails until the bundle exists.

### Bundle retrieval

- `docs_path` must resolve beneath one of the configured content roots.
- Symlink resolution is included in containment checks.
- Only `SKILL.md` and files under `references/`, `templates/`, `scripts/`, and `assets/` are returned.
- Individual files are limited to 200,000 bytes and a bundle to 750,000 bytes.
- Returned files include SHA-256 checksums.
- Retrieval reads text as UTF-8 and does not execute bundle content.

### Caller-local installation

- `SSR_MCP_SKILLS_ROOT` is required and authoritative.
- Model- or caller-supplied `skills_root` is rejected unless a trusted operator explicitly enables `SSR_MCP_ALLOW_SKILLS_ROOT_OVERRIDE=1`.
- Skill and category names are restricted to conservative character sets and lengths.
- Absolute paths, null bytes, `..`, unsupported top-level directories, malformed frontmatter, name mismatches, and checksum mismatches fail closed.
- Every incoming file is validated before the destination is replaced.
- Installation stages the complete bundle in a sibling directory and commits it as a whole.
- `overwrite=true` removes stale files that are absent from the new bundle.
- If the final directory swap fails, the previous installation is restored when possible.
- Installation does not execute scripts or other bundle content.
- Local success and policy failures can be written to a caller-local audit log.

The adapter trusts the operator-configured `SSR_MCP_URL`. It does not authenticate that backend, independently cap the backend response size, or cryptographically bind the returned checksums to a publisher. Duplicate bundle paths are not explicitly rejected; the last duplicate wins in the in-memory map. Use only a trusted backend and transport.

### Audit minimization

- Bundle `content` and `files` payloads are omitted.
- Keys containing common secret markers are redacted.
- Strings containing common authorization/token markers are redacted.
- Text and total record sizes are capped.
- Recent-event responses are capped at 500 records.

Redaction is defense in depth, not a guarantee that arbitrary sensitive prose can never appear.

### Verification and supply-chain hygiene

- Real MCP subprocess tests cover initialize, discovery, all five tools, installation, audits, and negative paths.
- Guardrail tests cover path escape, symlinks, malformed frontmatter, oversize bundles, checksum tampering, stale-file removal, and rollback.
- CI tests fresh source and built-wheel installations on Python 3.11 and 3.14.
- GitHub Actions are pinned to full commit SHAs.
- The bundled public catalog records source commits and third-party notices.
- Static SkillSpector results for the bundled catalog are documented in [`SEED-CATALOG.md`](SEED-CATALOG.md).

## Threat analysis

| Threat | Implemented mitigation | Residual risk / operator action |
|---|---|---|
| Unauthorized registry mutation | Loopback default, private-address bind checks in the packaged launcher, schema validation, atomic YAML replacement, audit events | Every reachable client can use admin, tool, and audit routes. There is no authentication, authorization, CSRF protection, or role model. Direct Uvicorn/proxy/tunnel configuration can bypass the launcher bind check. Keep the service local or put authenticated transport and route policy in front of it. |
| Installation outside the intended root | Authoritative configured root, conservative names, resolved containment checks, per-call override rejection | Enabling the override escape hatch broadens write authority. The adapter process still has all permissions of its OS user. |
| Path traversal or symlink escape | Resolved content/install paths, allowed-directory checks, absolute/`..` rejection, tests | Filesystem state can change concurrently. Do not share writable content/install trees with untrusted local users. |
| Tampered bundle in transit | Adapter recomputes each checksum before writing | Checksums and bundle travel together and are not signed. A malicious or compromised registry server can provide matching malicious content and hashes. Use trusted transport and server ownership. |
| Oversized or malformed alternate-backend response | Registry retrieval applies file and bundle byte caps; install revalidates paths, frontmatter, and checksums | The adapter trusts its configured backend and does not independently cap total response size or reject duplicate paths. Do not point it at an untrusted server. |
| Malicious skill or prompt injection | Curated catalog, source metadata, static scans, no install-time execution | Open SSR is not a sandbox or semantic malware detector. Review skills before installation and retain normal tool approvals when agents use them. |
| Stale vulnerable file after update | Whole-directory staged replacement | Concurrent installers are not locked; last successful writer wins. Coordinate updates to one destination. |
| Registry edit races | Atomic file replacement | There is no optimistic concurrency token or lock. Concurrent edits can overwrite one another. Use one editor at a time or version-control the registry. |
| Denial of service | Request-field limits, list limits, file/bundle caps, client timeouts | No built-in rate limiting, quotas, authentication, or worker isolation. Do not expose to untrusted networks. Large audit files are read linearly. |
| Audit disclosure | Redaction, payload omission, record caps | Audit routes have no authentication; logs can contain operational metadata and local install paths; file permissions follow the process environment. Store logs in an access-controlled location. |
| Audit tampering, loss, or ambiguous mutation result | Append-only JSONL behavior | No signatures, hash chaining, locking, fsync guarantee, rotation, retention, or external durability. Local install auditing is optional. An audit-write failure can surface after a mutation already succeeded. Forward logs externally if they are compliance evidence and verify state after ambiguous failures. |
| Network interception | Loopback/private deployment expectation | HTTP is plaintext and has no server/client identity. Use a trusted private network or authenticated TLS reverse proxy across machines. |
| UI content injection | Dynamic values are escaped before HTML insertion in the bundled UI | Treat future UI changes as security-sensitive and test untrusted metadata. No Content Security Policy is currently provided. |
| Dependency or CI compromise | Constrained dependencies, wheel tests, pinned action SHAs | Python dependencies are version-constrained rather than hash-locked; no SBOM or signed release artifact is currently published. |
| Local privilege expansion | Caller-local adapter and explicit destination | The adapter runs with the invoking user's privileges. Do not run it as root merely to install skills. |

## Safe deployment profiles

### Recommended: one operator, one machine

- Keep the default loopback bind.
- Run the HTTP service and stdio adapter as an unprivileged user.
- Set an explicit, least-privilege `SSR_MCP_SKILLS_ROOT`.
- Keep registry, content roots, and audit files writable only by that operator.

### Acceptable with additional controls: private multi-machine use

- Bind only to a specific private or tailnet address.
- Restrict network membership and firewall access.
- Use authenticated TLS termination when the private network is not itself the trust boundary.
- Do not expose unauthenticated registry-editing or audit routes to users who are not registry administrators.
- Keep the stdio adapter and install root on each consuming machine.

### Unsupported: direct public Internet exposure

Do not expose the current alpha directly to the public Internet. It has no built-in authentication, authorization, TLS, rate limiting, or multi-tenant isolation.

## Security-sensitive change checklist

Changes to any of these areas require focused tests and threat-model review:

- bind validation or remote deployment guidance;
- registry editing or new write routes;
- bundle path/content rules or size limits;
- checksum or provenance behavior;
- install-root selection, overwrite, rollback, or symlink handling;
- audit fields, redaction, retention, or exposure;
- UI rendering of registry-controlled values;
- dependency, build, or GitHub Actions configuration.

## Out of scope

- proving that arbitrary skill instructions are safe;
- sandboxing an agent that later uses an installed skill;
- hosted marketplace moderation or publisher reputation;
- identity, role-based access control, or tenant isolation;
- secret management;
- fleet orchestration, remote agent control, or arbitrary command execution;
- compliance certification or forensic-grade audit retention.
