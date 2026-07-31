from pathlib import Path


release = Path(".github/workflows/release.yml").read_text(encoding="utf-8")
prepare = Path(".github/workflows/prepare-release.yml").read_text(encoding="utf-8")
evidence = Path(".github/workflows/device-control-release-evidence.yml").read_text(
    encoding="utf-8"
)
external_gates = Path(".github/workflows/device-control-external-gates.yml").read_text(
    encoding="utf-8"
)

required_release_fragments = (
    'test "$GITHUB_REF" = "refs/tags/v${version}"',
    'tr -d \'[:space:]\' < VERSION',
    "id-token: write",
    "attestations: write",
    "anchore/sbom-action@",
    "cosign sign-blob",
    "cosign verify-blob",
    "actions/attest-build-provenance@",
    "gh attestation verify",
    "sha256sum --check",
    "fail_on_unmatched_files: true",
    "check-device-control-release-readiness.py",
    "--require-clean",
    "--require-tag",
    "--require-origin",
)

missing = [fragment for fragment in required_release_fragments if fragment not in release]
if missing:
    raise SystemExit(f"release workflow is missing: {', '.join(missing)}")

expected_dispatch = 'gh workflow run release.yml --ref "v${version}" -f version="${version}"'
if expected_dispatch not in prepare:
    raise SystemExit("prepare workflow must dispatch the immutable release tag")

required_evidence_fragments = (
    'test "$GITHUB_REF" = "refs/tags/v${VERSION}"',
    "environment: production-device-release-evidence",
    "device-control-release-gates",
    "${name}.evidence.tar.gz",
    '.evidence_sha256 == $evidence_sha256',
    '.conclusion == "success" and .head_branch == $ref and .head_sha == $sha',
    "cosign verify-blob",
    "gh attestation verify",
    ".spdx.json.sigstore.json",
    "verify_sbom",
    "--bundle \"$server/agent-remote-server-${VERSION}.provenance.jsonl\"",
    "notarization-${VERSION}.json",
    '"$device/$signing_evidence.sigstore.json"',
    "pip-audit.json",
    "govulncheck.json",
    "cargo-audit.json",
    "swift-osv.json",
    'any(.[]; has("finding")) | not',
    "assemble-device-control-release-evidence.py",
    "--gate-evidence security-tests=",
    "create_device_control_release_evidence.py",
    "DEVICE_CONTROL_RELEASE_PRIVATE_KEY_PEM",
    "retention-days: 30",
)
missing_evidence = [fragment for fragment in required_evidence_fragments if fragment not in evidence]
if missing_evidence:
    raise SystemExit(f"release evidence workflow is missing: {', '.join(missing_evidence)}")

required_external_gate_fragments = (
    'test "$GITHUB_REF" = "refs/tags/v${VERSION}"',
    "environment: production-device-release-gates",
    "runs-on: [self-hosted, macOS, ARM64, agent-remote-device-gates]",
    "DEVICE_CONTROL_EXTERNAL_GATE_DIRECTORY",
    "collect-device-control-external-gates.py",
    "name: device-control-release-gates",
    "if-no-files-found: error",
    "retention-days: 30",
)
missing_external_gates = [
    fragment for fragment in required_external_gate_fragments if fragment not in external_gates
]
if missing_external_gates:
    raise SystemExit(
        f"external gate workflow is missing: {', '.join(missing_external_gates)}"
    )

test_compose = Path("deploy/compose/docker-compose.device-test.yml").read_text(
    encoding="utf-8"
)
for fragment in (
    "AGENT_REMOTE_ENV: development",
    'DEVICE_CONTROL_ENABLED: "true"',
):
    if fragment not in test_compose:
        raise SystemExit(f"local device test compose is missing: {fragment}")

release_version = Path("VERSION").read_text(encoding="utf-8").strip()
test_environment = Path("deploy/compose/.env.device-test").read_text(encoding="utf-8")
for fragment in (
    f"AGENT_REMOTE_VERSION={release_version}",
    "SERVER_IMAGE=agent-remote-server:device-test-${AGENT_REMOTE_VERSION}",
    "ADMIN_WEB_IMAGE=agent-remote-admin-web:device-test-${AGENT_REMOTE_VERSION}",
):
    if fragment not in test_environment:
        raise SystemExit(f"local device test environment is missing: {fragment}")

test_release_assembler = Path(
    "scripts/assemble-local-device-control-test-release.sh"
).read_text(encoding="utf-8")
for fragment in (
    'release_version=$(tr -d',
    'agent-remote-cli-$release_version-aarch64-apple-darwin.tar.gz',
    'agent-remote-node-$release_version-linux-amd64-glibc.tar.gz',
    '"$proxy_amd64/SHA256SUMS"',
    '"$proxy_arm64/SHA256SUMS"',
    'shasum -a 256 --check SHA256SUMS',
    'docker buildx build',
    '--platform "linux/$architecture"',
    '--output "type=docker,dest=$archive"',
    "for architecture in amd64 arm64",
    "image_platforms=linux/amd64,linux/arm64",
    "admin_head=%s",
    'git -C "$admin_repo" rev-parse HEAD',
    "device_head=%s",
    'git -C "$device_repo" rev-parse HEAD',
):
    if fragment not in test_release_assembler:
        raise SystemExit(f"local test release assembler is missing: {fragment}")
