# Contributing

Thanks for helping improve Shared Skills Registry MCP (Open SSR).

This project has a deliberately narrow boundary: a self-hosted registry returns reviewed, checksum-bearing skill bundles; a caller-local MCP adapter installs them beneath an explicitly configured local skills root. Contributions must preserve that boundary.

Please read:

- [`README.md`](README.md) for the product and local workflow;
- [`docs/THREAT-MODEL.md`](docs/THREAT-MODEL.md) before changing security-sensitive behavior;
- [`docs/KNOWN-LIMITATIONS.md`](docs/KNOWN-LIMITATIONS.md) before expanding release claims;
- [`SECURITY.md`](SECURITY.md) for private vulnerability reporting;
- [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) before importing external content.

## Ways to contribute

Good contributions include:

- reproducible bug reports;
- tests for real MCP, bundle validation, packaging, or installation boundaries;
- accessibility and first-run UX improvements;
- clearer self-hosting and MCP-client documentation;
- public-safe skills with documented provenance and licenses;
- security hardening that keeps writes caller-local;
- fixes that work in both editable source and built-wheel installations.

Please discuss large changes before implementing them. Open an issue describing the user problem, boundary changes, and proposed verification. Do not use a public issue for an undisclosed vulnerability.

## Development setup

Requires Python 3.11–3.14. CI tests Linux at the supported floor and ceiling.

```bash
git clone https://github.com/cobibean/shared-skills-registry-mcp.git
cd shared-skills-registry-mcp
python -m venv .venv
. .venv/bin/activate
python -m pip install -c requirements/ci-constraints.txt -e '.[test]'
python -m pytest -q
```

Start the service:

```bash
shared-skills-registry-http
```

Then open <http://127.0.0.1:8765/ui>.

Keep development services on loopback. Do not use a wildcard or public bind.

## Exercise the real MCP path

HTTP tests alone do not prove MCP compatibility. With the HTTP service running:

```bash
tmp="$(mktemp -d)"
python scripts/mcp_stdio_smoke.py \
  --url http://127.0.0.1:8765 \
  --skills-root "$tmp/skills" \
  --audit-log "$tmp/local-audit.jsonl"
rm -rf "$tmp"
```

The smoke must initialize the official MCP client, discover all five tools, call the registry workflow, install beneath the scratch root, and record local audit evidence.

## Build and verify the wheel

Changes to packaging, runtime paths, UI assets, commands, catalog content, or dependencies require a clean wheel check outside the source checkout:

```bash
python -m pip install -c requirements/ci-constraints.txt build hatchling
rm -rf build dist
python -m build --wheel --no-isolation
python -m venv /tmp/open-ssr-wheel-check
/tmp/open-ssr-wheel-check/bin/pip install \
  -c "$PWD/requirements/ci-constraints.txt" \
  dist/*.whl
cd /tmp
/tmp/open-ssr-wheel-check/bin/shared-skills-registry-http
```

Verify the packaged UI, 14-entry catalog, both console commands, generic stdio smoke, caller-local installation, and audit records. Remove the temporary environment afterward.

## Repository layout

```text
config/shared_skills.yaml        Registry metadata and canonical public catalog
skills/                          Production and companion skill bundles
examples/skills/                 Explicit example-only bundles
examples/mcp-client-config/      Client setup examples
src/shared_skills_registry_mcp/  HTTP service, stdio adapter, registry/install logic
tests/                           Core, HTTP, UI, guardrail, package, and MCP tests
ui/index.html                    Zero-build control panel
docs/                            Architecture, security, catalog, and launch docs
```

There is no runtime `seed/skills/` namespace. Do not introduce one.

## Add or update a skill

Production and companion bundles live at:

```text
skills/<name>/
```

The tutorial bundle lives under `examples/skills/` and must remain clearly example-only.

A bundle must contain:

```text
SKILL.md
```

It may also contain UTF-8 text files under:

```text
references/
templates/
scripts/
assets/
```

Rules:

1. `SKILL.md` starts with valid YAML frontmatter.
2. Frontmatter `name` exactly matches the registry name and directory name.
3. Names and categories use lowercase letters, numbers, `_`, `.`, or `-`.
4. No absolute paths, `..`, symlink escapes, credentials, private infrastructure, customer material, or internal operator procedures.
5. Keep each file below 200 KB and the retrieved bundle below 750 KB.
6. Installation must not execute bundle content.
7. Add matching metadata to `config/shared_skills.yaml` using `docs_path: skills/<name>/SKILL.md`.
8. Record upstream repository and pinned source commit in metadata/docs when importing content.
9. Update `THIRD_PARTY_NOTICES.md` for external content and preserve its license requirements.
10. Run the catalog, retrieval, installation, and public-safety tests.

Do not add default Hermes skills or private fleet procedures to the public catalog.

## Security expectations

Treat these changes as security-sensitive:

- HTTP bind behavior or deployment documentation;
- registry editing or new write routes;
- content-root/path resolution;
- bundle inclusion rules or size limits;
- checksums, provenance, or install authorization;
- local destination selection, overwrite, rollback, or symlinks;
- audit fields and redaction;
- UI rendering of registry-controlled values;
- dependencies, build configuration, or CI actions.

Required posture:

- add a regression test that fails before the fix;
- preserve the caller-local write boundary;
- fail closed on missing configuration and unsafe input;
- do not weaken tests to make a failure disappear;
- do not claim authentication, sandboxing, signatures, or platform support that is not implemented;
- report undisclosed vulnerabilities through [`SECURITY.md`](SECURITY.md), not a public issue.

## Tests and checks

Before submitting a pull request:

```bash
python -m pytest -q
bash -n examples/mcp-client-config/hermes-add-shared-skills-registry.sh
git diff --check
```

Also run when relevant:

- `tests/test_mcp_stdio_e2e.py` for protocol/adapter changes;
- `tests/test_guardrails.py` for retrieval/install/security changes;
- clean built-wheel smoke for package/resource/command changes;
- generic MCP smoke for client-facing changes;
- browser and console checks for UI changes;
- static skill scan and manual content review for catalog changes;
- `actionlint .github/workflows/ci.yml` for workflow changes.

CI must pass every fresh-clone and built-wheel job on Python 3.11 and 3.14.

## Pull requests

Keep pull requests focused and include:

- the user-visible problem;
- the chosen behavior and security-boundary impact;
- files or surfaces changed;
- exact tests and smokes run;
- screenshots or GIFs for UI changes;
- attribution/license updates for imported content;
- known limitations or follow-up work;
- confirmation that no credentials or private infrastructure were committed.

Do not commit generated virtual environments, build output, audit logs, local install roots, credentials, or private test evidence.

## Code and documentation style

- Prefer small, explicit Python modules and standard-library solutions where practical.
- Keep MCP stdout protocol-clean; diagnostics belong on stderr or in audit logs.
- Keep docs copy-pasteable and honest about alpha limitations.
- Prefer durable tests and repository artifacts over chat-only verification.
- Follow existing naming and schema conventions.

## License

By contributing, you agree that your contribution may be distributed under this repository's MIT license. Only contribute content you have the right to license, and identify third-party material clearly.
