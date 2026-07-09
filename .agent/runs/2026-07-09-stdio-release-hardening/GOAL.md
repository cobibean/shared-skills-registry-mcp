# Goal: Open SSR real MCP stdio release hardening

## Objective

Ship a release-grade test phase proving the packaged Open SSR service and stdio adapter work through the actual MCP protocol, a clean local Hermes consumer, a remote-device Hermes consumer, a generic non-Hermes MCP client, and deterministic GitHub Actions fresh-clone CI.

## Finishing criteria

- Automated test launches the real HTTP service and packaged `shared_skills_registry_mcp.stdio_server` module, initializes an MCP client session, lists tools, calls list/search/describe/retrieve/install, and verifies caller-local files/checksums/audit.
- A clean isolated local Hermes profile discovers and calls the MCP tools, installs into a scratch skills root, and is independently verified.
- A remote-device isolated Hermes profile uses the central private HTTP service through its local stdio adapter and independently verifies local installation without touching production profiles.
- A generic MCP SDK client smoke succeeds outside pytest.
- GitHub Actions installs from a clean checkout and runs the entire suite, including stdio integration.
- Product code/config/docs are fixed for any failures; tests are not weakened to hide defects.
- Full suite, security scan, fresh clone, live smokes, CI, git push, and remote SHA are verified.

## Runtime goal coupling

Ledger: `.agent/runs/2026-07-09-stdio-release-hardening/implementation-notes.html`

## Escape hatch

Pause only for an external credential/user-auth requirement, unavailable remote host, or a mutation that would affect an existing production/client profile. Prefer disposable homes/profiles, scratch ports, scratch install roots, and cleanup.

## Safety constraints and protected paths

- Do not modify or restart existing production/client Hermes gateways.
- Do not expose Open SSR on a public bind; remote smoke uses tailnet/private networking only.
- Do not print or commit credentials, auth stores, private host details, or raw logs.
- Use separate scratch profile/home paths and remove them after evidence is captured.
- Preserve the Open SSR registry/server boundary: server authorizes/returns bundles; the client-local adapter writes locally.
