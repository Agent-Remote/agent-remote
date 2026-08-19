import json
from pathlib import Path


release = Path(".github/workflows/release.yml").read_text(encoding="utf-8")
prepare = Path(".github/workflows/prepare-release.yml").read_text(encoding="utf-8")
evidence = Path(".github/workflows/device-control-release-evidence.yml").read_text(
    encoding="utf-8"
)
external_gates = Path(".github/workflows/device-control-external-gates.yml").read_text(
    encoding="utf-8"
)
community_evidence = Path(
    ".github/workflows/community-device-control-release-evidence.yml"
).read_text(encoding="utf-8")
community_v2_evidence = Path(
    ".github/workflows/community-computer-use-v2-evidence.yml"
).read_text(encoding="utf-8")

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
    "--manifest release-manifest.json",
    "needs.resolve.outputs.server-version",
    "needs.resolve.outputs.device-version",
    "--require-clean",
    "--require-tag",
    "--require-origin",
    "uses: ./.github/workflows/community-device-control-release-evidence.yml",
    "needs: [resolve, validate]",
    "needs: [resolve, validate, community-evidence]",
    "community-device-control-release-evidence-${{ needs.resolve.outputs.version }}",
    '"dist/${package}/deploy/compose/device-control-release-evidence.json"',
    "> device-control-release-evidence.SHA256SUMS",
    "DEVICE_CONTROL_RELEASE_EVIDENCE_FILE=./device-control-release-evidence.json",
    '(cd ".release/device-control-release-evidence"',
    "production-release-manifest.json",
    "SERVER_IMAGE=${server_image}@${server_digest}",
    "admin-workflow: ${{ steps.manifest.outputs.admin-workflow }}",
    "${ADMIN_WORKFLOW}@refs/tags/v${ADMIN_VERSION}",
    '--source-ref "refs/tags/v${ADMIN_VERSION}"',
)

if "\n        env:\n        run:" in release:
    raise SystemExit("release workflow contains an empty env mapping")

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
    '--source-ref "refs/tags/v${SERVER_VERSION}"',
    'Agent-Remote/agent-remote-server/.github/workflows/${SERVER_WORKFLOW}',
    "notarization-${DEVICE_VERSION}.json",
    '"$device/$signing_evidence.sigstore.json"',
    "pip-audit.json",
    "govulncheck.json",
    "cargo-audit.json",
    "swift-osv.json",
    'any(.[]; has("finding")) | not',
    "assemble-device-control-release-evidence.py",
    "export-release-manifest.py",
    '--release-version "$SERVER_VERSION"',
    '--distribution-version "$DISTRIBUTION_VERSION"',
    "--release-manifest release-manifest.json",
    "--gate-evidence security-tests=",
    "create_device_control_release_evidence.py",
    "DEVICE_CONTROL_RELEASE_PRIVATE_KEY_PEM",
    "retention-days: 30",
)
missing_evidence = [fragment for fragment in required_evidence_fragments if fragment not in evidence]
if missing_evidence:
    raise SystemExit(f"release evidence workflow is missing: {', '.join(missing_evidence)}")

unsupported_oci_bundle = '--bundle "$server/agent-remote-server-${SERVER_VERSION}.provenance.jsonl"'
if unsupported_oci_bundle in evidence or unsupported_oci_bundle in community_evidence:
    raise SystemExit("OCI provenance must use online GitHub attestation verification")
if '--bundle ".release/admin/agent-remote-admin-web-${ADMIN_VERSION}.provenance.jsonl"' in release:
    raise SystemExit("Admin OCI provenance must use online GitHub attestation verification")

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

required_community_evidence_fragments = (
    "runs-on: ubuntu-latest",
    "environment: production-device-release-evidence",
    "accept_reduced_security",
    'test "$ACCEPTED" = "true"',
    "community-local-trust",
    "official_runners_only",
    "critical_high_vulnerabilities:0",
    "community-signing.json",
    'verify_blob Agent-Remote/agent-remote-server "$SERVER_WORKFLOW" "$SERVER_VERSION"',
    'verify_blob Agent-Remote/agent-remote-device "$DEVICE_WORKFLOW" "$DEVICE_VERSION"',
    "workflows/${DEVICE_WORKFLOW}",
    "govulncheck.json.sha256",
    "swift-osv.json.sha256",
    "identity['version']",
    'if sha != identity["commit"]',
    'run["event"] == "push"',
    'run["path"] == ".github/workflows/ci.yml"',
    'run["event"] == "workflow_dispatch"',
    'trusted_release = f".github/workflows/{identity[\'release_workflow\']}"',
    "! -name SHA256SUMS",
    "assemble-community-device-control-release-evidence.py",
    "create_device_control_release_evidence.py",
    "DEVICE_CONTROL_RELEASE_PRIVATE_KEY_PEM",
    "retention-days: 30",
    "workflow_call:",
    "linux-amd64-glibc",
    "linux-arm64-glibc",
    "linux-amd64-musl",
    "linux-arm64-musl",
    "--node-artifact",
    "--proxy-artifact",
    "node-${target}=release-input/node/agent-remote-node-${NODE_VERSION}.spdx.json",
    "proxy-${target}=release-input/device/agent-remote-device-proxy-${target}-${DEVICE_VERSION}.spdx.json",
    "for attempt in range(40)",
    "time.sleep(30)",
    'current_run["path"] == ".github/workflows/release.yml"',
    'current_run["head_sha"] != sha',
    'current_run["status"] != "in_progress"',
    "computer_use_v2_run_id",
    'case "$RUN_ID" in',
    "community-computer-use-v2-evidence-${DISTRIBUTION_VERSION}",
    '.path == ".github/workflows/community-computer-use-v2-evidence.yml"',
    "--computer-use-v2-evidence",
    "--computer-use-v2-evidence-archive",
    "--computer-use-v2-target",
    "community_computer_use_v2_without_apple_notarization",
)
missing_community_evidence = [
    fragment
    for fragment in required_community_evidence_fragments
    if fragment not in community_evidence
]
if missing_community_evidence:
    raise SystemExit(
        "community release evidence workflow is missing: "
        + ", ".join(missing_community_evidence)
    )

required_community_v2_fragments = (
    'test "$GITHUB_REF" = "refs/tags/v${VERSION}"',
    "runs-on: [self-hosted, macOS, ARM64, agent-remote-device-gates]",
    "environment: production-device-release-gates",
    "COMMUNITY_COMPUTER_USE_V2_EVIDENCE_DIRECTORY",
    "collect-community-computer-use-v2-evidence.py",
    "community-computer-use-v2-evidence-${{ inputs.version }}",
    "if-no-files-found: error",
    "retention-days: 30",
)
missing_community_v2 = [
    fragment
    for fragment in required_community_v2_fragments
    if fragment not in community_v2_evidence
]
if missing_community_v2:
    raise SystemExit(
        "Community Computer Use v2 evidence workflow is missing: "
        + ", ".join(missing_community_v2)
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
release_manifest = json.loads(Path("release-manifest.json").read_text(encoding="utf-8"))
if release_manifest["schema_version"] != 2:
    raise SystemExit("release manifest must bind signing workflow identities")
for name, component in release_manifest["components"].items():
    if not component.get("release_workflow", "").endswith((".yml", ".yaml")):
        raise SystemExit(f"release manifest workflow identity is missing for {name}")
server_version = release_manifest["components"]["agent-remote-server"]["version"]
admin_version = release_manifest["components"]["agent-remote-admin-web"]["version"]
test_environment = Path("deploy/compose/.env.device-test").read_text(encoding="utf-8")
for fragment in (
    f"AGENT_REMOTE_VERSION={release_version}",
    f"SERVER_VERSION={server_version}",
    f"ADMIN_WEB_VERSION={admin_version}",
    "SERVER_IMAGE=agent-remote-server:device-test-${SERVER_VERSION}",
    "ADMIN_WEB_IMAGE=agent-remote-admin-web:device-test-${ADMIN_WEB_VERSION}",
):
    if fragment not in test_environment:
        raise SystemExit(f"local device test environment is missing: {fragment}")

test_release_assembler = Path(
    "scripts/assemble-local-device-control-test-release.sh"
).read_text(encoding="utf-8")
for fragment in (
    'release_version=$(jq -er .distribution_version',
    'agent-remote-cli-$cli_version-aarch64-apple-darwin.tar.gz',
    'agent-remote-node-$node_version-linux-amd64-glibc.tar.gz',
    '"$proxy_amd64/SHA256SUMS"',
    '"$proxy_arm64/SHA256SUMS"',
    'shasum -a 256 --check SHA256SUMS',
    '"$staging/bin/agent-remote-device-proxy"',
    'shasum -a 256 bin/agent-remote-device-proxy > SHA256SUMS',
    '--uid 0 --gid 0 --uname root --gname root',
    '--owner=0 --group=0 --numeric-owner',
    'tar --no-xattrs',
    '-C "$staging" -czf "$archive" bin VERSION SHA256SUMS',
    'docker buildx build',
    '--platform "linux/$architecture"',
    '--build-arg "AGENT_REMOTE_VERSION=$version"',
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
