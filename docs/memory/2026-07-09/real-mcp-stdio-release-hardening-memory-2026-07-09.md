# Real MCP stdio release hardening memory - 2026-07-09

## Session summary

- Shipped release-grade coverage for the real Open SSR MCP stdio path.
- Added deterministic subprocess-level MCP tests, a generic MCP SDK smoke, clean local and remote Hermes E2Es, fresh-clone CI, and built-wheel CI.
- Corrected wheel packaging so the catalog, examples, UI, runtime paths, and stdio implementation work outside an editable repository checkout.
- Hardened caller-local installation after a real Hermes run exposed an unsafe root-selection edge case.
- Published release-hardening implementation commit `4e35d47e0402dba21f32d708a2bbe6e8676a3dd1` and independent-review remediation commit `4f5351a` to `main`.

## What we learned

- HTTP route tests do not prove MCP compatibility. The useful acceptance seam is an MCP client session that initializes a real stdio subprocess and calls tools through protocol framing.
- An overwrite operation must replace the entire validated bundle. Per-file merging leaves removed or vulnerable scripts active on disk even when the registry no longer ships them; stage the complete bundle, atomically swap directories, and restore the previous directory if the final swap fails.
- A distributable wheel can pass editable-checkout tests while omitting non-Python product assets. Installed-artifact testing must run outside the checkout.
- Hermes `mcp add --env` accepts multiple `KEY=value` items after one `--env`; repeating the flag can leave only the final group persisted. The installer now reads the saved config back and verifies every required environment key.
- An LLM may supply optional tool arguments even when a prompt asks it not to. A model-supplied `skills_root` must not override an operator-configured caller-local root by default.
- Logs from FastMCP/httpx remained on stderr; protocol stdout remained usable throughout initialize, discovery, calls, errors, and shutdown.

## Decisions made

- The supported stdio entry point is `shared-skills-registry-stdio`; `client/stdio_server.py` remains a compatibility shim.
- The supported HTTP entry point is `shared-skills-registry-http`.
- `SSR_MCP_SKILLS_ROOT` is authoritative. Per-call root overrides fail closed unless a trusted operator explicitly sets `SSR_MCP_ALLOW_SKILLS_ROOT_OVERRIDE=1`.
- `overwrite=true` performs a staged whole-directory replacement, removes stale files absent from the new bundle, and restores the previous installation if the final directory swap fails.
- Wheel builds force-include the canonical repository `config/`, `skills/`, `examples/skills/`, and `ui/` trees under private package data; the repository remains the single source of truth.
- Alpha CI uses committed Python 3.11/3.14 Linux dependency constraints and separately tests editable fresh-clone and clean wheel installs at the supported floor and ceiling.

## Files created or changed

- `.github/workflows/ci.yml`
- `requirements/ci-constraints.txt`
- `tests/test_mcp_stdio_e2e.py`
- `scripts/mcp_stdio_smoke.py`
- `src/shared_skills_registry_mcp/stdio_server.py`
- `src/shared_skills_registry_mcp/cli.py`
- `src/shared_skills_registry_mcp/runtime_paths.py`
- `client/stdio_server.py`
- `src/shared_skills_registry_mcp/config.py`
- `src/shared_skills_registry_mcp/app.py`
- `pyproject.toml`
- `README.md`
- `docs/MCP-CLIENT-CONFIG.md`
- `docs/SECURITY-BOUNDARY.md`
- `examples/mcp-client-config/`
- `.agent/`

## Commands and verification

- Source suite after independent review remediation: `python -m pytest -q` → `55 passed`, one upstream Starlette/httpx deprecation warning.
- Protocol suite: four real MCP tests passed:
  - positive initialize/list/search/describe/retrieve/install/checksum/audit flow;
  - missing local root fails closed;
  - per-call root override fails closed;
  - unreachable backend returns a tool error without corrupting the MCP session.
- Generic SDK smoke passed from both editable source and a clean wheel environment.
- Built wheel contained 73 files and included the registry, 13 production bundles, example bundle, UI, stdio module, and console entry points.
- Clean local Hermes E2E called search/describe/retrieve/install through MCP only, installed eight checksum-matching files into its scratch profile, and discovered the skill in a fresh session.
- Separate remote Linux Hermes E2E was rerun against the exact public independent-review closeout commit through a loopback-only private tunnel and packaged stdio command. A stale script was planted under the scratch destination before the real Hermes install; the install removed it, produced 11 checksum-matching files, wrote one local audit record, remained discoverable in a fresh session, and left existing profile configurations and services unchanged.
- Current fresh-clone jobs installed from committed constraints and passed all 55 tests on Python 3.11 and 3.14.
- GitHub Actions run `29051012487` passed all four jobs: fresh-clone MCP and built-wheel packaging on Python 3.11 and 3.14. The jobs allocate dynamic loopback ports, and third-party actions are pinned to audited full commit SHAs.
- `actionlint 1.7.12` passed the workflow.
- Changed-file safety scans found no credentials, private keys, JWTs, private operator paths, or private host identifiers.
- Temporary servers, tunnel, test homes, remote clone, credentials copy, and local clones were removed; the remote loopback listener was closed and no failed user services remained.

## Gotchas and constraints

- Do not use repeated Hermes `--env` flags for this command shape; pass all environment pairs after one `--env` and verify persisted configuration.
- Do not trust an MCP client or model to choose an installation root. Keep root authority in adapter configuration.
- Do not bind the combined unauthenticated HTTP/admin surface directly to a shared network merely to test a remote client. Use a loopback-only tunnel or an equivalent private forwarding mechanism.
- The committed constraints are for deterministic Python 3.11 Linux CI. Broader Python/platform compatibility should use an explicit matrix rather than silently treating this file as universal.

## Recommended next work

- Continue Gate 3 with the full threat model, Known Limitations, vulnerability reporting, and contribution guidance.
- Keep the real stdio and wheel-install jobs required for future release branches.
- Tag `v0.1.0-alpha` only after the remaining release documentation and final go/no-go review pass.
