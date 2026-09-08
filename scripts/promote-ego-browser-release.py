#!/usr/bin/env python3
"""Atomically promote a certified ego-browser Bridge release in the root manifest."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

# Loading release validators must not dirty a checked-out component repository
# with interpreter cache files while we are proving its clean-worktree state.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_REPOSITORY = "Agent-Remote/agent-remote-ego-browser"
BRIDGE_COMPONENT = "agent-remote-ego-browser"
LEARNING_BLOCKER = "learning_bundle_signing_private_key_unavailable"
ZERO_COMMIT = "0" * 40
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
KEY_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-.+][0-9A-Za-z.-]+)?$")

LEGACY_COMPONENTS = {
    "agent-remote-server",
    "agent-remote-node",
    "agent-remote-cli",
    "agent-remote-admin-web",
    "agent-remote-device",
}
ALL_COMPONENTS = LEGACY_COMPONENTS | {BRIDGE_COMPONENT}

SIGNING_EVIDENCE_FIELDS = {
    "schema_version",
    "version",
    "profile",
    "production_ready",
    "readiness_blockers",
    "apple_notarized",
    "public_distribution",
    "signing_type",
    "signer_certificate_sha256",
    "bridge_signature_verified",
    "device_client_signature_verified",
    "nested_signatures_verified",
    "hardened_runtime",
    "outbound_policy",
    "credential_profile",
    "learning_bundle_digest",
    "learning_bundle_signing_key_id",
}

PRODUCTION_EVIDENCE_REQUIRED = {
    "schema_version",
    "release_profile",
    "production_ready",
    "apple_notarized",
    "public_distribution",
    "manual_trust_required",
    "release_version",
    "issued_at",
    "distribution_version",
    "release_manifest_sha256",
    "components",
    "server_sha256",
    "application_sha256",
    "node_artifacts_sha256",
    "proxy_artifacts_sha256",
    "sbom_sha256",
    "provenance_sha256",
    "signing_notarization_sha256",
    "community_signing_sha256",
    "automated_release_checks_sha256",
    "risk_acceptance_sha256",
    "ego_browser_release_manifest_sha256",
    "ego_browser_release_archive_sha256",
    "ego_browser_signing_evidence_sha256",
    "ego_browser_learning_bundle_sha256",
    "ego_browser_sigstore_sha256",
    "ego_browser_provenance_sha256",
    "ci_run_url",
    "signature",
}

# These are the nullable fields emitted by the Server's schema-9 model.  Keeping
# the complete shape here prevents an evidence signer from omitting a defaulted
# field and accidentally signing a different canonical payload.
PRODUCTION_EVIDENCE_FIELDS = PRODUCTION_EVIDENCE_REQUIRED | {
    "node_sha256",
    "proxy_sha256",
    "security_tests_sha256",
    "security_review_sha256",
    "outbound_policy_sha256",
    "local_claude_isolation_sha256",
    "stop_revocation_sha256",
    "compatibility_sha256",
    "computer_use_v2_evidence_sha256",
}


def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Parse one JSON object while rejecting duplicate names."""

    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def load_object(path: Path) -> dict[str, Any]:
    """Load a bounded JSON object without accepting duplicate fields."""

    if not path.is_file() or path.is_symlink():
        raise ValueError(f"JSON input is not a regular file: {path}")
    raw = path.read_bytes()
    if not raw or len(raw) > 1024 * 1024:
        raise ValueError(f"JSON input size is invalid: {path}")
    value = json.loads(raw, object_pairs_hook=reject_duplicates)
    if not isinstance(value, dict):
        raise ValueError(f"JSON input is not an object: {path}")
    return value


def absolute_path(path: Path) -> Path:
    """Make a path absolute without resolving its final symlink."""

    return Path(os.path.abspath(path))


def require_directory(path: Path, label: str) -> None:
    """Require an absolute, non-symlink directory for release inputs."""

    if not path.is_absolute() or not path.is_dir() or path.is_symlink():
        raise ValueError(f"{label} must be an absolute non-symlink directory")


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one regular file."""

    if not path.is_file() or path.is_symlink():
        raise ValueError(f"digest input is not a regular file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    """Encode deterministic JSON used for release-manifest hashes."""

    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def canonical_compact_json(value: object) -> bytes:
    """Encode deterministic compact JSON used by the Server evidence signer."""

    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def load_root_helpers() -> Any:
    """Load the root manifest validator without relying on the current directory."""

    path = ROOT / "scripts" / "release_manifest.py"
    spec = importlib.util.spec_from_file_location(
        "agent_remote_root_release_manifest", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("root release manifest validator is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_bridge_helpers(repository: Path) -> Any:
    """Load the Bridge's strict release-manifest validator."""

    path = repository / "scripts" / "release_manifest.py"
    if not path.is_file() or path.is_symlink():
        raise ValueError("Bridge release-manifest validator is missing")
    spec = importlib.util.spec_from_file_location("ego_browser_release_manifest", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Bridge release-manifest validator is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_git(repository: Path, *arguments: str) -> str:
    """Run a read-only Git query and return trimmed output."""

    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def verify_bridge_repository(
    repository: Path, version: str, expected_commit: str
) -> None:
    """Verify the Bridge worktree, exact tag, and canonical GitHub origin."""

    if (
        not repository.is_absolute()
        or not repository.is_dir()
        or repository.is_symlink()
        or not (repository / ".git").exists()
        or (repository / ".git").is_symlink()
    ):
        raise ValueError("Bridge repository is missing")
    head = run_git(repository, "rev-parse", "HEAD")
    if not GIT_SHA.fullmatch(head) or head != expected_commit:
        raise ValueError("Bridge HEAD does not match the certified commit")
    tagged = run_git(
        repository, "rev-parse", "--verify", f"refs/tags/v{version}^{{commit}}"
    )
    if tagged != expected_commit:
        raise ValueError("Bridge version tag does not match the certified commit")
    status = run_git(repository, "status", "--porcelain=v1", "--untracked-files=all")
    if status:
        raise ValueError("Bridge repository is not clean")
    origin = run_git(repository, "remote", "get-url", "origin")
    normalized = re.sub(r"\.git$", "", origin)
    if normalized not in (
        BRIDGE_REPOSITORY,
        f"https://github.com/{BRIDGE_REPOSITORY}",
        f"git@github.com:{BRIDGE_REPOSITORY}",
        f"ssh://git@github.com/{BRIDGE_REPOSITORY}",
    ):
        raise ValueError(
            "Bridge repository origin is not the canonical GitHub repository"
        )


def verify_github_release(
    *,
    version: str,
    release_json: Path | None,
    repository: str = BRIDGE_REPOSITORY,
) -> dict[str, Any]:
    """Verify that GitHub has a published, non-draft, non-prerelease tag release."""

    if release_json is not None:
        value = load_object(release_json)
    else:
        completed = subprocess.run(
            [
                "gh",
                "release",
                "view",
                f"v{version}",
                "--repo",
                repository,
                "--json",
                "tagName,isDraft,isPrerelease,publishedAt,url",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        value = json.loads(completed.stdout, object_pairs_hook=reject_duplicates)
        if not isinstance(value, dict):
            raise ValueError("GitHub release response is not an object")
    if (
        value.get("tagName") != f"v{version}"
        or value.get("isDraft") is not False
        or value.get("isPrerelease") is not False
        or not isinstance(value.get("publishedAt"), str)
        or not value["publishedAt"].strip()
    ):
        raise ValueError("Bridge GitHub release is not published for the exact tag")
    return value


def verify_bridge_manifest(
    path: Path,
    artifact_directory: Path | None,
    *,
    version: str,
    commit: str,
    certificate: str,
    learning_digest: str,
    learning_key_id: str,
    repository: Path,
) -> dict[str, Any]:
    """Verify the Bridge aggregate manifest and its exact release artifacts."""

    helpers = load_bridge_helpers(repository)
    manifest = helpers.load_manifest(path)
    if (
        manifest.get("component") != BRIDGE_COMPONENT
        or manifest.get("version") != version
        or manifest.get("production_ready") is not True
        or manifest.get("readiness_blockers") != []
        or manifest.get("signer_certificate_sha256") != certificate
        or manifest.get("learning_bundle_digest") != learning_digest
        or manifest.get("learning_bundle_signing_key_id") != learning_key_id
        or manifest.get("nested_signatures_verified") is not True
    ):
        raise ValueError("Bridge release manifest is incomplete or mismatched")
    if artifact_directory is None:
        artifact_directory = path.parent
    helpers.verify_files(manifest, artifact_directory)
    return manifest


def verify_signing_evidence(
    path: Path,
    *,
    version: str,
    certificate: str,
    learning_digest: str,
    learning_key_id: str,
) -> dict[str, Any]:
    """Verify the Bridge's signed-component and trust evidence record."""

    value = load_object(path)
    if set(value) != SIGNING_EVIDENCE_FIELDS:
        raise ValueError("Bridge signing evidence fields are invalid")
    expected: dict[str, object] = {
        "schema_version": 1,
        "version": version,
        "profile": "community-local-trust",
        "production_ready": True,
        "readiness_blockers": [],
        "apple_notarized": False,
        "public_distribution": False,
        "signing_type": "project-self-signed",
        "signer_certificate_sha256": certificate,
        "bridge_signature_verified": True,
        "device_client_signature_verified": True,
        "nested_signatures_verified": True,
        "hardened_runtime": True,
        "outbound_policy": "application-enforced",
        "credential_profile": "community_file",
        "learning_bundle_digest": learning_digest,
        "learning_bundle_signing_key_id": learning_key_id,
    }
    if value != expected:
        raise ValueError("Bridge signing evidence is incomplete or mismatched")
    return value


def _check_bundle_tree(bundle: Path) -> None:
    """Check that a learning bundle is a bounded read-only regular-file tree."""

    if not bundle.is_dir() or bundle.is_symlink() or not bundle.is_absolute():
        raise ValueError("learning bundle must be an absolute non-symlink directory")
    manifest = bundle / "manifest.json"
    learnings = bundle / "learnings"
    if (
        not manifest.is_file()
        or manifest.is_symlink()
        or not learnings.is_dir()
        or learnings.is_symlink()
    ):
        raise ValueError("learning bundle is incomplete")
    members = 0
    for path in (bundle, *bundle.rglob("*")):
        members += 1
        if members > 4096 or path.is_symlink():
            raise ValueError("learning bundle contains an unsafe or excessive entry")
        info = path.stat()
        mode = info.st_mode
        if stat.S_ISREG(mode):
            if mode & 0o222 or info.st_nlink != 1:
                raise ValueError("learning bundle is writable")
        elif not stat.S_ISDIR(mode):
            raise ValueError("learning bundle contains a non-regular entry")
        elif mode & 0o222:
            raise ValueError("learning bundle is writable")


def verify_learning_bundle(
    bundle: Path,
    *,
    key_id: str,
    expected_digest: str | None,
    verifier: str | None,
    public_key_file: Path | None,
    repository: Path,
) -> str:
    """Verify a signed Site Learning bundle and return its measured digest."""

    if not KEY_ID.fullmatch(key_id):
        raise ValueError("learning bundle signing key ID is invalid")
    _check_bundle_tree(bundle)
    if public_key_file is not None and (
        not public_key_file.is_file() or public_key_file.is_symlink()
    ):
        raise ValueError("learning bundle public key must be a regular file")
    manifest = load_object(bundle / "manifest.json")
    if manifest.get("signing_key_id") != key_id:
        raise ValueError(
            "learning bundle signing key ID does not match the release pin"
        )
    command: list[str]
    if verifier:
        command = [verifier]
    else:
        command = [str(repository / "scripts" / "verify-learning-bundle.sh")]
    command.extend(("--bundle", str(bundle), "--key-id", key_id))
    if public_key_file is not None:
        command.extend(("--public-key-file", str(public_key_file)))
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("learning bundle signature verification failed") from exc
    output = completed.stdout.strip().removeprefix("sha256:")
    if SHA256.fullmatch(output) is None:
        raise ValueError("learning bundle verifier returned an invalid digest")
    if expected_digest is not None and output != expected_digest:
        raise ValueError("learning bundle digest does not match the Bridge release")
    return output


def _validate_digest(value: object, label: str, *, allow_none: bool = False) -> None:
    """Validate one lowercase SHA-256 field."""

    if allow_none and value is None:
        return
    if not isinstance(value, str) or SHA256.fullmatch(value) is None:
        raise ValueError(f"{label} is not a lowercase SHA-256 digest")


def _verify_ed25519(value: dict[str, Any], public_key_base64: str) -> None:
    """Verify a Server schema 9 evidence signature when its pinned key is available."""

    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        public_key = Ed25519PublicKey.from_public_bytes(
            base64.b64decode(public_key_base64.strip(), validate=True)
        )
        signature = base64.b64decode(str(value["signature"]), validate=True)
        unsigned = dict(value)
        unsigned.pop("signature", None)
        unsigned.pop("expires_at", None)
        public_key.verify(signature, canonical_compact_json(unsigned))
        return
    except Exception as exc:
        raise ValueError("schema 9 production evidence signature is invalid") from exc


def verify_production_evidence(
    path: Path,
    *,
    distribution_version: str,
    server_version: str,
    expected_manifest_sha256: str,
    expected_components: dict[str, Any],
    expected_bridge_digests: dict[str, str],
    public_key_base64: str | None,
) -> dict[str, Any]:
    """Verify complete schema 9 community evidence bound to a candidate root manifest."""

    value = load_object(path)
    if set(value) != PRODUCTION_EVIDENCE_FIELDS:
        raise ValueError("schema 9 production evidence fields are incomplete")
    if (
        value["schema_version"] != 9
        or value["release_profile"] != "community-local-trust"
        or value["production_ready"] is not True
        or value["apple_notarized"] is not False
        or value["public_distribution"] is not False
        or value["manual_trust_required"] is not True
        or value["release_version"] != server_version
        or value["distribution_version"] != distribution_version
        or value["release_manifest_sha256"] != expected_manifest_sha256
    ):
        raise ValueError("schema 9 production evidence is not bound to this release")
    components = value["components"]
    if not isinstance(components, dict) or set(components) != ALL_COMPONENTS:
        raise ValueError(
            "schema 9 production evidence component inventory is incomplete"
        )
    if components != expected_components:
        raise ValueError("schema 9 production evidence component identity differs")
    for field, expected in expected_bridge_digests.items():
        if value.get(field) != expected:
            raise ValueError(f"schema 9 production evidence {field} is not bound")
    for field in (
        "server_sha256",
        "application_sha256",
        "sbom_sha256",
        "provenance_sha256",
        "signing_notarization_sha256",
        "community_signing_sha256",
        "automated_release_checks_sha256",
        "risk_acceptance_sha256",
    ):
        _validate_digest(value[field], field)
    for field in ("node_artifacts_sha256", "proxy_artifacts_sha256"):
        mapping = value[field]
        if not isinstance(mapping, dict) or set(mapping) != {
            "linux-amd64-glibc",
            "linux-arm64-glibc",
            "linux-amd64-musl",
            "linux-arm64-musl",
        }:
            raise ValueError(f"{field} does not cover every supported target")
        for digest in mapping.values():
            _validate_digest(digest, field)
    if not public_key_base64:
        raise ValueError("schema 9 production evidence public key is required")
    _verify_ed25519(value, public_key_base64)
    return value


def build_candidate_manifest(
    original: dict[str, Any],
    *,
    bridge_manifest: dict[str, Any],
    commit: str,
    certificate: str,
    learning_digest: str,
    learning_key_id: str,
) -> dict[str, Any]:
    """Build and validate the complete promoted root manifest in memory."""

    candidate = copy.deepcopy(original)
    components = candidate.get("components")
    if not isinstance(components, dict) or BRIDGE_COMPONENT not in components:
        raise ValueError("root manifest does not contain the Bridge component")
    component = components[BRIDGE_COMPONENT]
    if not isinstance(component, dict):
        raise ValueError("root Bridge component is invalid")
    if bridge_manifest.get("version") != component.get("version"):
        raise ValueError("Bridge version does not match the root component pin")
    component.update(
        {
            "commit": commit,
            "release_published": True,
            "signer_certificate_sha256": certificate,
            "learning_bundle_digest": learning_digest,
            "learning_bundle_signing_key_id": learning_key_id,
            "nested_signatures_verified": True,
            "production_ready": True,
            "readiness_blockers": [],
        }
    )
    helpers = load_root_helpers()
    with tempfile.NamedTemporaryFile(mode="wb", dir=ROOT, delete=False) as temporary:
        temporary.write(canonical_json(candidate))
        temporary_path = Path(temporary.name)
    try:
        helpers.load_release_manifest(temporary_path)
    finally:
        temporary_path.unlink(missing_ok=True)
    return candidate


def atomic_write(path: Path, value: dict[str, Any], expected_original: bytes) -> None:
    """Atomically replace a manifest after checking it was not concurrently changed."""

    if not path.is_file() or path.is_symlink():
        raise ValueError("root release manifest must be a regular file")
    current = path.read_bytes()
    if current != expected_original:
        raise ValueError("root release manifest changed during promotion")
    mode = path.stat().st_mode
    encoded = canonical_json(value)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        os.fchmod(descriptor, mode & 0o7777)
        with os.fdopen(descriptor, "wb") as output:
            descriptor = -1
            output.write(encoded)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_path, path)
        directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        temporary_path.unlink(missing_ok=True)


def write_candidate(path: Path, value: dict[str, Any]) -> bytes:
    """Write one canonical candidate manifest without overwriting an input."""

    if path.exists() or path.is_symlink():
        raise ValueError(f"refusing to overwrite candidate manifest: {path}")
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise ValueError("candidate manifest parent must be a regular directory")
    encoded = canonical_json(value)
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        0o600,
    )
    try:
        with os.fdopen(descriptor, "wb") as output:
            descriptor = -1
            output.write(encoded)
            output.flush()
            os.fsync(output.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    return encoded


def load_canonical_candidate(path: Path) -> tuple[dict[str, Any], bytes]:
    """Load a candidate and require the exact canonical bytes we sign."""

    if not path.is_file() or path.is_symlink():
        raise ValueError("candidate manifest must be a regular file")
    raw = path.read_bytes()
    value = load_root_helpers().load_release_manifest(path)
    encoded = canonical_json(value)
    if raw != encoded:
        raise ValueError("candidate manifest is not canonical")
    return value, raw


def parse_args() -> argparse.Namespace:
    """Parse promotion command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "release-manifest.json")
    parser.add_argument(
        "--bridge-repository",
        "--bridge-repo",
        type=Path,
        default=ROOT.parent / "agent-remote-ego-browser",
    )
    parser.add_argument(
        "--bridge-release-manifest", "--bridge-manifest", type=Path, required=True
    )
    parser.add_argument("--bridge-release-archive", type=Path, required=True)
    parser.add_argument("--bridge-artifact-dir", type=Path)
    parser.add_argument(
        "--bridge-signing-evidence", "--signing-evidence", type=Path, required=True
    )
    parser.add_argument("--bridge-archive-sigstore", type=Path, required=True)
    parser.add_argument("--bridge-manifest-sigstore", type=Path, required=True)
    parser.add_argument("--bridge-provenance", type=Path, required=True)
    parser.add_argument(
        "--learning-bundle", "--learning-bundle-root", type=Path, required=True
    )
    parser.add_argument("--learning-bundle-verifier")
    parser.add_argument(
        "--learning-bundle-public-key", "--learning-bundle-public-key-file", type=Path
    )
    parser.add_argument("--production-evidence", "--release-evidence", type=Path)
    parser.add_argument(
        "--production-evidence-public-key", "--release-evidence-public-key"
    )
    parser.add_argument(
        "--candidate-output",
        type=Path,
        help="Write a canonical candidate manifest for a later evidence-signing step",
    )
    parser.add_argument(
        "--candidate-manifest",
        type=Path,
        help="Use the previously prepared canonical candidate during promotion",
    )
    parser.add_argument(
        "--prepare-only",
        "--prepare-candidate",
        action="store_true",
        help="Validate Bridge inputs and write the candidate without consuming production evidence",
    )
    parser.add_argument("--github-release-json", "--release-json", type=Path)
    parser.add_argument("--version", "--expected-version")
    parser.add_argument("--commit", "--expected-commit")
    parser.add_argument("--certificate-sha256", "--signer-certificate-sha256")
    parser.add_argument("--learning-bundle-key-id", "--expected-learning-key-id")
    parser.add_argument("--check-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Validate every release input and atomically promote the root component."""

    args = parse_args()
    try:
        if args.prepare_only:
            if args.candidate_output is None or args.candidate_manifest is not None:
                raise ValueError(
                    "--prepare-only requires --candidate-output and forbids --candidate-manifest"
                )
        elif args.production_evidence is None:
            raise ValueError(
                "--production-evidence is required when applying a promotion"
            )
        elif args.candidate_output is not None:
            raise ValueError("--candidate-output is only valid with --prepare-only")
        root_manifest_path = absolute_path(args.manifest)
        if not root_manifest_path.is_file() or root_manifest_path.is_symlink():
            raise ValueError("root release manifest must be a regular file")
        original_bytes = root_manifest_path.read_bytes()
        root_helpers = load_root_helpers()
        root_manifest = root_helpers.load_release_manifest(root_manifest_path)
        root_components = root_manifest["components"]
        assert isinstance(root_components, dict)
        root_component = root_components[BRIDGE_COMPONENT]
        assert isinstance(root_component, dict)
        version = args.version or str(root_component["version"])
        if not SEMVER.fullmatch(version):
            raise ValueError("Bridge release version is invalid")
        bridge_repository = absolute_path(args.bridge_repository)
        bridge_release_manifest = absolute_path(args.bridge_release_manifest)
        bridge_signing_evidence = absolute_path(args.bridge_signing_evidence)
        bridge_archive_sigstore = absolute_path(args.bridge_archive_sigstore)
        bridge_manifest_sigstore = absolute_path(args.bridge_manifest_sigstore)
        bridge_provenance = absolute_path(args.bridge_provenance)
        release_archive = absolute_path(args.bridge_release_archive)
        learning_bundle = absolute_path(args.learning_bundle)
        learning_bundle_public_key = (
            absolute_path(args.learning_bundle_public_key)
            if args.learning_bundle_public_key is not None
            else None
        )
        commit = args.commit or run_git(bridge_repository, "rev-parse", "HEAD")
        if not GIT_SHA.fullmatch(commit) or commit == ZERO_COMMIT:
            raise ValueError("Bridge release commit is invalid")
        certificate = args.certificate_sha256 or str(
            root_component.get("signer_certificate_sha256") or ""
        )
        if not SHA256.fullmatch(certificate):
            raise ValueError("signer certificate SHA-256 is required")
        key_id = args.learning_bundle_key_id or str(
            root_component.get("learning_bundle_signing_key_id")
            or "ego-browser-learning-2026-01"
        )
        if not KEY_ID.fullmatch(key_id):
            raise ValueError("learning bundle signing key ID is invalid")
        verify_bridge_repository(bridge_repository, version, commit)
        verify_github_release(version=version, release_json=args.github_release_json)
        bridge_helpers = load_bridge_helpers(bridge_repository)
        bridge_manifest = bridge_helpers.load_manifest(bridge_release_manifest)
        learning_digest_from_manifest = bridge_manifest.get("learning_bundle_digest")
        if not isinstance(learning_digest_from_manifest, str) or not SHA256.fullmatch(
            learning_digest_from_manifest
        ):
            raise ValueError("Bridge release manifest has no signed learning digest")
        expected_archive_name = (
            f"agent-remote-ego-browser-macos-universal-{version}.tar.gz"
        )
        if release_archive.name != expected_archive_name:
            raise ValueError("Bridge release archive filename is invalid")
        artifact_directory = (
            absolute_path(args.bridge_artifact_dir)
            if args.bridge_artifact_dir is not None
            else release_archive.parent
        )
        require_directory(artifact_directory, "Bridge artifact directory")
        if release_archive.parent != artifact_directory:
            raise ValueError("Bridge release archive is outside the artifact directory")
        verify_bridge_manifest(
            bridge_release_manifest,
            artifact_directory,
            version=version,
            commit=commit,
            certificate=certificate,
            learning_digest=learning_digest_from_manifest,
            learning_key_id=key_id,
            repository=bridge_repository,
        )
        for evidence_path in (
            bridge_archive_sigstore,
            bridge_manifest_sigstore,
            bridge_provenance,
        ):
            if not evidence_path.is_file() or evidence_path.is_symlink():
                raise ValueError(f"Bridge evidence file is missing: {evidence_path}")
        verify_signing_evidence(
            bridge_signing_evidence,
            version=version,
            certificate=certificate,
            learning_digest=learning_digest_from_manifest,
            learning_key_id=key_id,
        )
        learning_digest = verify_learning_bundle(
            learning_bundle,
            key_id=key_id,
            expected_digest=learning_digest_from_manifest,
            verifier=args.learning_bundle_verifier,
            public_key_file=learning_bundle_public_key,
            repository=bridge_repository,
        )
        bridge_digests = {
            "ego_browser_release_manifest_sha256": sha256_file(
                bridge_release_manifest
            ),
            "ego_browser_release_archive_sha256": sha256_file(
                release_archive
            ),
            "ego_browser_signing_evidence_sha256": sha256_file(
                bridge_signing_evidence
            ),
            "ego_browser_learning_bundle_sha256": learning_digest,
            "ego_browser_sigstore_sha256": sha256_file(bridge_archive_sigstore),
            "ego_browser_provenance_sha256": sha256_file(bridge_provenance),
        }
        candidate = build_candidate_manifest(
            root_manifest,
            bridge_manifest=bridge_manifest,
            commit=commit,
            certificate=certificate,
            learning_digest=learning_digest,
            learning_key_id=key_id,
        )
        candidate_bytes = canonical_json(candidate)
        candidate_digest = hashlib.sha256(candidate_bytes).hexdigest()
        if args.prepare_only:
            assert args.candidate_output is not None
            write_candidate(absolute_path(args.candidate_output), candidate)
            print(
                json.dumps(
                    {
                        "candidate_manifest": str(absolute_path(args.candidate_output)),
                        "manifest_sha256": candidate_digest,
                        "version": version,
                        "commit": commit,
                        "distribution_version": candidate["distribution_version"],
                        "root_manifest_sha256": candidate_digest,
                        "bridge_artifact_digests": bridge_digests,
                        "release_published": True,
                        "production_ready": True,
                        "readiness_blockers": [],
                        "check_only": False,
                        "prepare_only": True,
                    },
                    sort_keys=True,
                )
            )
            return 0
        if args.candidate_manifest is not None:
            supplied_candidate, supplied_bytes = load_canonical_candidate(
                absolute_path(args.candidate_manifest)
            )
            if supplied_candidate != candidate or supplied_bytes != candidate_bytes:
                raise ValueError(
                    "candidate manifest does not match the certified Bridge inputs"
                )
            candidate_bytes = supplied_bytes
            candidate_digest = hashlib.sha256(candidate_bytes).hexdigest()
        candidate_components = candidate["components"]
        assert isinstance(candidate_components, dict)
        production_public_key = args.production_evidence_public_key
        if production_public_key is None:
            public_key_path = ROOT / "deploy/compose/community-release-public-key.txt"
            if public_key_path.is_file() and not public_key_path.is_symlink():
                production_public_key = public_key_path.read_text(encoding="ascii").strip()
        if not production_public_key:
            raise ValueError(
                "schema 9 production evidence public key is required; pass --production-evidence-public-key"
            )
        verify_production_evidence(
            args.production_evidence,
            distribution_version=str(root_manifest["distribution_version"]),
            server_version=str(candidate_components["agent-remote-server"]["version"]),
            expected_manifest_sha256=candidate_digest,
            expected_components=candidate_components,
            expected_bridge_digests={
                field: bridge_digests[field]
                for field in (
                    "ego_browser_release_manifest_sha256",
                    "ego_browser_release_archive_sha256",
                    "ego_browser_signing_evidence_sha256",
                    "ego_browser_learning_bundle_sha256",
                    "ego_browser_sigstore_sha256",
                    "ego_browser_provenance_sha256",
                )
            },
            public_key_base64=production_public_key,
        )
        if not args.check_only:
            atomic_write(root_manifest_path, candidate, original_bytes)
        print(
            json.dumps(
                {
                    "manifest": str(root_manifest_path),
                    "version": version,
                    "commit": commit,
                    "distribution_version": candidate["distribution_version"],
                    "root_manifest_sha256": candidate_digest,
                    "bridge_artifact_digests": bridge_digests,
                    "release_published": True,
                    "production_ready": True,
                    "readiness_blockers": [],
                    "signer_certificate_sha256": certificate,
                    "learning_bundle_digest": learning_digest,
                    "learning_bundle_signing_key_id": key_id,
                    "nested_signatures_verified": True,
                    "manifest_sha256": candidate_digest,
                    "check_only": args.check_only,
                },
                sort_keys=True,
            )
        )
        return 0
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"ego-browser release promotion failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
