# Known limitations

Shared Skills Registry MCP is an early self-hosted alpha. The real MCP, local/remote Hermes, source, and wheel paths are tested, but the project intentionally does not yet provide the controls expected from a public hosted package marketplace.

## Deployment and access control

- **No built-in HTTP authentication or authorization.** Any client that can reach the service can list and retrieve bundles, request install payloads, read audits, and create, edit, deprecate, or delete registry metadata. The separate admin route names are not an access-control boundary.
- **No built-in TLS.** The default loopback deployment is safe from network interception on the host. Cross-machine operators must supply a trusted private network or authenticated TLS proxy.
- **Not safe for direct public Internet exposure.** The packaged launcher blocks wildcard and public-address literals, but private-network reachability is not user authentication. Direct Uvicorn commands, containers, proxies, tunnels, port forwarding, and firewall configuration can bypass or broaden the launcher boundary.
- **No multi-user or multi-tenant isolation.** There are no accounts, roles, per-user registries, or per-client audit partitions.
- **No built-in rate limiting or quotas.** Request and bundle sizes are bounded, but an untrusted reachable client can still consume service and disk resources.
- **No CSRF, trusted-host, or route-level admin middleware.** If a reverse proxy is used, it must provide the intended access policy rather than merely forwarding every route.

## Skill trust and provenance

- **Checksums provide integrity, not publisher authenticity.** The registry sends content and checksums together. A compromised registry can send malicious content with matching hashes.
- **No package signing, transparency log, or verified publisher identity.** Source/owner fields and pinned upstream commits are review metadata, not cryptographic attestations.
- **No semantic sandbox or malware guarantee.** Installation does not execute content, but an installed skill can contain instructions or scripts that an agent may later follow or run.
- **Static scanning has limits.** The bundled catalog was reviewed and scanned, but scanners can miss malicious intent and can flag benign examples.
- **No automatic upstream update verification.** Curated bundles are repository copies tied to documented source commits; maintainers must deliberately review and import updates.
- **No dependency resolution.** A skill that expects external binaries, Python packages, services, or credentials must document and manage those requirements itself.

## Installation behavior

- **Caller reload is required.** Most agents need a new session or explicit skill reload after installation.
- **One writer at a time is assumed.** Installs use staged whole-directory replacement but do not lock the destination. Concurrent installers can race; the last successful replacement wins.
- **Overwrite defaults to true and keeps no history.** A successful update replaces the complete installed directory and deletes its temporary backup. There is no built-in previous-version store.
- **The adapter inherits its OS user's authority.** Path checks bound Open SSR writes, but the process can still access anything permitted to that user through unrelated code or dependencies. Run it unprivileged.
- **The root-override escape hatch broadens authority.** `SSR_MCP_ALLOW_SKILLS_ROOT_OVERRIDE=1` lets individual tool calls choose a destination and is intentionally disabled by default.
- **Text bundles only.** Bundle files are read and transported as UTF-8 text. Arbitrary binary package payloads are not supported.
- **Bundle shape and size are intentionally narrow.** Only `SKILL.md`, `references/`, `templates/`, `scripts/`, and `assets/` are included; files are capped at 200 KB and complete bundles at 750 KB.
- **The stdio adapter trusts its configured backend.** Retrieval-side size caps and the `install_authorized` flag are supplied by that server. The adapter revalidates paths, frontmatter, and checksums but does not independently cap the full response or reject duplicate file paths. Do not point it at an untrusted `SSR_MCP_URL`.
- **No uninstall or rollback command.** A failed replacement attempts to restore the previous directory, but users remove an installed skill manually and there is no version history UI.

## Registry and UI

- **Metadata editing does not upload bundle content.** Files must already exist under a configured content root before an entry can retrieve successfully.
- **A registry entry may reference a missing bundle.** The admin view reports `source_exists=false`, but saving the metadata is allowed and retrieval then fails until the files are present.
- **Concurrent metadata editing is not coordinated.** YAML replacement is atomic, but there is no lock or revision token; simultaneous editors can overwrite each other's changes.
- **Registry storage is local YAML, not a database.** This keeps deployment simple but does not provide transactions, replication, access-control records, or large-catalog indexing.
- **Search is lightweight substring scoring.** It is deterministic but not semantic search, typo correction, ranking personalization, or embedding retrieval.
- **No content approval workflow.** Lifecycle status controls public visibility, but the UI does not implement reviewer roles, signed approvals, or promotion gates.
- **The UI is desktop-first.** It is a zero-build single-page control panel, not a fully tested mobile or assistive-technology application.

## Audit and operations

- **The audit log is operational, not forensic.** JSONL records are not signed, hash-chained, access-controlled by the application, or protected from a host administrator.
- **No built-in rotation or retention.** Operators must rotate, archive, or forward logs themselves. Reading recent events scans the file linearly.
- **Redaction is heuristic.** Bundle bodies are omitted and common secret markers are redacted, but arbitrary sensitive prose may not be recognized. Do not send secrets as registry metadata or tool arguments.
- **Audit failures can make outcomes ambiguous.** Some writes occur before their audit append. A failed audit write can return an error after the underlying mutation or installation already succeeded; verify live state before retrying.
- **Caller-local install auditing is optional.** It is disabled when `SSR_MCP_AUDIT_LOG` is not configured, and audit records do not identify an authenticated actor or client.
- **No metrics, tracing, backup scheduler, or high-availability mode.** Health, JSONL activity, process supervision, backups, and recovery are operator responsibilities.

## Platform and release support

- **CI currently targets Linux.** Python 3.11 and 3.14 are tested at the supported floor and ceiling. macOS and Windows are not release-gated yet.
- **No container image, system package, or hosted service is published.** The supported alpha shape is a Python source/wheel installation with the packaged HTTP and stdio commands.
- **No stability guarantee before `1.0`.** Registry fields, UI details, command flags, and audit shapes may evolve with release notes and migration guidance.
- **No formal deprecation window.** Alpha consumers should pin releases and review changes before updating.

## Not product goals

Open SSR is not intended to become:

- a fleet control plane;
- remote command execution;
- an A2A message bus;
- a secret manager;
- an autonomous marketplace trust authority;
- a substitute for human review of code and agent instructions.

For the detailed trust analysis and safe deployment profiles, see [`THREAT-MODEL.md`](THREAT-MODEL.md).
