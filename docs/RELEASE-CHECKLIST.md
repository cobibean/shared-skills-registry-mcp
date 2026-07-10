# Release checklist

This checklist governs Open SSR alpha releases. It does not authorize a release by itself. A tag, GitHub Release, or package-index upload requires an explicit Gate 4 decision.

## 1. Decide the release identity

Use one version consistently in `pyproject.toml`, built artifact names, the Git tag, and release notes.

| Distribution plan | Recommended package version | Recommended tag | Notes |
| --- | --- | --- | --- |
| GitHub prerelease, with or without attached Python artifacts | `0.1.0a1` | `v0.1.0a1` | PEP 440-compliant and unambiguously pre-release. |
| PyPI prerelease plus GitHub prerelease | `0.1.0a1` | `v0.1.0a1` | Preferred if `pip install --pre shared-skills-registry-mcp` should work. |
| Source snapshot only, no Python artifact publication | still `0.1.0a1` | `v0.1.0a1` | Avoid a stable-looking `0.1.0` package version for alpha code. |

Do not combine package version `0.1.0` with a `v0.1.0-alpha` tag. The source and distribution metadata would look stable while the GitHub label says alpha.

Before choosing PyPI, re-check that the project name is still available and configure a project-scoped trusted-publishing workflow or similarly narrow credential. Do not paste a long-lived account-wide token into commands, CI logs, or repository settings.

## 2. Freeze the candidate

- [ ] Gate 3 public-safety/readiness review is recorded as `GO`.
- [ ] The approved version is set in `pyproject.toml`.
- [ ] Release notes describe capabilities, trust boundary, limitations, supported Python versions, and upgrade expectations.
- [ ] `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, Threat Model, Known Limitations, and third-party notices match the candidate.
- [ ] The working tree is clean and local `HEAD` equals `origin/main`.

Record the candidate commit before building anything.

## 3. Run source and workflow gates

From a clean clone of the candidate commit:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -c requirements/ci-constraints.txt -e '.[test]'
pytest -q
actionlint .github/workflows/ci.yml
git diff --check
```

Also complete:

- [ ] changed-file secret/private-infrastructure scan;
- [ ] README and documentation link check;
- [ ] browser UI and console pass;
- [ ] official-SDK MCP stdio smoke into a scratch skills root;
- [ ] scratch audit verification;
- [ ] public GitHub rendering check.

## 4. Build and validate artifacts

Build from the clean candidate checkout, not from an editable working tree with uncommitted files:

```bash
rm -rf build dist
python -m pip install -c requirements/ci-constraints.txt build hatchling twine
python -m build --sdist --wheel --no-isolation
python -m twine check dist/*
```

Verify:

- [ ] wheel and sdist filenames contain the approved version;
- [ ] metadata name, version, Python requirement, project URLs, and license are correct;
- [ ] both artifacts contain `THIRD_PARTY_NOTICES.md` and required public documentation;
- [ ] bundled catalog, skill bundles, example bundle, and UI assets are present;
- [ ] both artifacts install in clean environments outside the checkout;
- [ ] packaged HTTP and stdio commands exist;
- [ ] the wheel-installed runtime passes UI, five-tool MCP, caller-local install, and audit smoke;
- [ ] the sdist-installed runtime resolves the same packaged notice and resources.

Generate checksums only after the final artifact build:

```bash
sha256sum dist/* > dist/SHA256SUMS
sha256sum -c dist/SHA256SUMS
```

## 5. Approve the publication target

Choose explicitly:

- **GitHub prerelease only** — attach wheel, sdist, and `SHA256SUMS`; no package-index install path.
- **GitHub prerelease plus PyPI prerelease** — publish the same verified wheel and sdist; do not rebuild between targets.

For PyPI, prefer trusted publishing bound to this repository and release workflow. If that is unavailable, stop and review the credential plan rather than improvising.

## 6. Publish without rebuilding

After explicit approval:

1. create the approved annotated tag on the verified candidate commit;
2. push only that tag;
3. create a GitHub **prerelease** with the approved release notes;
4. attach the already-verified wheel, sdist, and checksum file;
5. if approved, upload those exact artifacts to PyPI;
6. record release URLs, artifact hashes, workflow run, and publication result in project memory.

Never run a second build between verification and publication.

## 7. Verify as a consumer

From a new temporary environment and a directory outside the repository:

- [ ] download the GitHub artifacts and verify `SHA256SUMS`;
- [ ] install the wheel and exercise HTTP/UI/MCP/install/audit;
- [ ] install the sdist in a separate environment and verify packaged resources;
- [ ] if published to PyPI, install the exact prerelease version using `--pre` and repeat the smoke;
- [ ] confirm the GitHub release is marked prerelease and links to the security and limitation documents;
- [ ] confirm private vulnerability reporting remains enabled.

## 8. Failure handling

- A failed or ambiguous gate is a **NO-GO**; fix forward on `main`, then build a new candidate.
- Do not move an existing public tag to a different commit.
- If a PyPI artifact is defective, follow PyPI yank guidance; uploaded files cannot be replaced under the same version.
- If a GitHub artifact is defective, mark the release accordingly and publish a new prerelease version rather than silently replacing verified provenance.
