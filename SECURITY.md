# Security policy

## Supported versions

Shared Skills Registry MCP is currently an alpha. Security fixes are made on the latest published `0.1.x` release and the `main` branch.

| Version | Security support |
|---|---|
| Latest `0.1.x` | Best-effort support |
| Older alpha versions | Update to the latest release before reporting unless the issue also affects current `main` |
| Unreleased forks or modified deployments | Maintainers will assess upstream impact but cannot support private modifications |

Before `1.0`, interfaces may change when necessary to close a security boundary. Material changes will be documented in release notes.

## Report a vulnerability privately

**Do not open a public issue for an undisclosed vulnerability.**

Use GitHub's private vulnerability-reporting form:

<https://github.com/cobibean/shared-skills-registry-mcp/security/advisories/new>

Private vulnerability reporting is enabled for this repository. If GitHub prevents you from using the form, contact the maintainer through the repository owner's GitHub profile without including exploit details, secrets, or sensitive logs in a public message. Ask for a private reporting channel.

## What to include

Please provide enough information to reproduce and assess the issue safely:

- affected commit or release;
- component and deployment shape;
- impact and realistic attacker prerequisites;
- minimal reproduction steps or proof of concept;
- whether the issue affects default configuration;
- suggested mitigation, if known;
- whether any secret, private host, or real user data was involved.

Use scratch paths and synthetic skill content where possible. Redact credentials, private network details, and unrelated audit records.

## In scope

Security reports are especially useful for:

- writes escaping `SSR_MCP_SKILLS_ROOT`;
- symlink, traversal, overwrite, rollback, or stale-file installation defects;
- checksum or bundle-validation bypasses;
- retrieval outside configured content roots;
- registry-edit validation or atomicity failures;
- unauthenticated behavior that contradicts the documented local/private deployment boundary;
- secret or bundle-content exposure through audit records or errors;
- stored or reflected script injection in the control panel;
- dependency, wheel, or GitHub Actions supply-chain weaknesses;
- denial-of-service paths that bypass documented size and request limits;
- private data, credentials, customer material, or internal infrastructure accidentally committed to the public repository.

## Known behavior that is not by itself a vulnerability

Unless it contradicts the documentation or enables an unexpected bypass, these are current alpha limitations rather than undisclosed vulnerabilities:

- no built-in HTTP authentication, authorization, TLS, CSRF protection, rate limiting, or multi-tenant roles;
- no direct-public-Internet deployment support;
- checksums without publisher signatures or a transparency log;
- no semantic guarantee that an installed skill is benign;
- no install-time sandbox for content an agent may later use;
- local YAML and JSONL storage without multi-writer transactions or tamper-evident logging;
- Linux-only release-gated CI.

See [`docs/KNOWN-LIMITATIONS.md`](docs/KNOWN-LIMITATIONS.md) and [`docs/THREAT-MODEL.md`](docs/THREAT-MODEL.md).

## Response process

This is a maintainer-run alpha, so response times are best effort rather than an SLA. The intended process is:

1. acknowledge a complete report within seven calendar days;
2. reproduce and assess severity privately;
3. agree on disclosure timing with the reporter when practical;
4. prepare a fix, regression test, and release note;
5. publish a GitHub Security Advisory/CVE when appropriate;
6. credit the reporter unless they prefer anonymity.

If active exploitation or accidental secret publication is suspected, rotate affected credentials and restrict the deployment immediately rather than waiting for a code release.

## Disclosure expectations

Please allow a reasonable remediation window before public disclosure. Do not access data that is not yours, degrade shared services, persist on systems, or use real credentials when a synthetic proof is sufficient.

The maintainers will not ask you to conceal a vulnerability indefinitely. Coordinated disclosure should balance user safety with a clear path to publication.

## Deployment guidance

The supported alpha posture is loopback or a controlled private network. Do not expose the service directly to the public Internet. For cross-machine operation, add authenticated TLS termination or use a private network that is itself the intended trust boundary.
