from __future__ import annotations

import base64
import hashlib
import json
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/promote-ego-browser-release.py"
BRIDGE_SOURCE = ROOT.parent / "agent-remote-ego-browser"
VERSION = "0.1.0"
CERTIFICATE = "a" * 64
LEARNING_KEY_ID = "ego-browser-learning-2026-01"
LEARNING_DIGEST = "b" * 64


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n"
    ).encode()


def compact(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode()


def write(path: Path, data: bytes | str | object, mode: int = 0o644) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data)
    elif isinstance(data, str):
        path.write_text(data, encoding="utf-8")
    else:
        path.write_bytes(canonical(data))
    path.chmod(mode)
    return path


def git(repository: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def make_bridge(root: Path) -> tuple[Path, Path, dict[str, object], str]:
    bridge = root / "agent-remote-ego-browser"
    bridge.mkdir()
    write(bridge / "VERSION", f"{VERSION}\n")
    write(bridge / ".gitignore", "__pycache__/\n")
    write(
        bridge / "scripts/release_manifest.py",
        (BRIDGE_SOURCE / "scripts/release_manifest.py").read_bytes(),
        0o755,
    )
    subprocess.run(["git", "init", "-q", str(bridge)], check=True)
    git(bridge, "config", "user.name", "Release Test")
    git(bridge, "config", "user.email", "release@example.invalid")
    git(
        bridge,
        "remote",
        "add",
        "origin",
        "https://github.com/Agent-Remote/agent-remote-ego-browser.git",
    )
    subprocess.run(["git", "-C", str(bridge), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(bridge), "commit", "-qm", "release fixture"], check=True
    )
    commit = git(bridge, "rev-parse", "HEAD")
    subprocess.run(["git", "-C", str(bridge), "tag", f"v{VERSION}"], check=True)

    artifacts = root / "bridge-artifacts"
    artifacts.mkdir()
    names = [
        f"agent-remote-ego-browser-wrapper-linux-amd64-glibc-{VERSION}.tar.gz",
        f"agent-remote-ego-browser-wrapper-linux-arm64-glibc-{VERSION}.tar.gz",
        f"agent-remote-ego-browser-wrapper-linux-amd64-musl-{VERSION}.tar.gz",
        f"agent-remote-ego-browser-wrapper-linux-arm64-musl-{VERSION}.tar.gz",
        f"agent-remote-ego-browser-macos-universal-{VERSION}.tar.gz",
    ]
    for name in names:
        write(artifacts / name, f"artifact:{name}\n", 0o444)
        write(artifacts / f"{name}.sigstore.json", b"{}\n", 0o444)
        write(
            artifacts / f"{name.removesuffix('.tar.gz')}.spdx.json",
            b'{"spdxVersion":"SPDX-2.3"}\n',
            0o444,
        )
        write(
            artifacts / f"{name.removesuffix('.tar.gz')}.spdx.json.sigstore.json",
            b"{}\n",
            0o444,
        )
    report = f"agent-remote-ego-browser-{VERSION}.cargo-audit.json"
    write(artifacts / report, b'{"vulnerabilities":[]}\n', 0o444)
    write(artifacts / f"{report}.sigstore.json", b"{}\n", 0o444)

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "bridge_manifest", bridge / "scripts/release_manifest.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manifest = module.generate_manifest(
        VERSION,
        CERTIFICATE,
        artifacts,
        learning_bundle_digest=LEARNING_DIGEST,
        learning_bundle_key_id=LEARNING_KEY_ID,
    )
    manifest_path = write(
        artifacts / f"agent-remote-ego-browser-{VERSION}.release-manifest.json",
        manifest,
        0o444,
    )
    write(artifacts / f"{manifest_path.name}.sigstore.json", b"{}\n", 0o444)
    write(
        artifacts / f"{manifest_path.name}.sha256",
        f"{hashlib.sha256(manifest_path.read_bytes()).hexdigest()}  {manifest_path.name}\n",
        0o444,
    )
    archive = artifacts / f"agent-remote-ego-browser-macos-universal-{VERSION}.tar.gz"
    signing = write(
        artifacts
        / f"agent-remote-ego-browser-macos-universal-{VERSION}.community-signing.json",
        {
            "schema_version": 1,
            "version": VERSION,
            "profile": "community-local-trust",
            "production_ready": True,
            "readiness_blockers": [],
            "apple_notarized": False,
            "public_distribution": False,
            "signing_type": "project-self-signed",
            "signer_certificate_sha256": CERTIFICATE,
            "bridge_signature_verified": True,
            "device_client_signature_verified": True,
            "nested_signatures_verified": True,
            "hardened_runtime": True,
            "outbound_policy": "application-enforced",
            "credential_profile": "community_file",
            "learning_bundle_digest": LEARNING_DIGEST,
            "learning_bundle_signing_key_id": LEARNING_KEY_ID,
        },
        0o444,
    )
    write(artifacts / f"{signing.name}.sigstore.json", b"{}\n", 0o444)
    write(
        artifacts / f"{signing.name}.sha256",
        f"{hashlib.sha256(signing.read_bytes()).hexdigest()}  {signing.name}\n",
        0o444,
    )
    write(
        archive.with_suffix(archive.suffix + ".sha256"),
        f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}\n",
        0o444,
    )
    return bridge, manifest_path, manifest, commit


def make_learning_bundle(root: Path) -> tuple[Path, Path]:
    bundle = root / "learning-bundle"
    write(bundle / "manifest.json", {"signing_key_id": LEARNING_KEY_ID}, 0o444)
    write(bundle / "learnings/example/notes", b"signed learning\n", 0o444)
    for path in [
        bundle,
        bundle / "learnings",
        bundle / "learnings/example",
        bundle / "learnings/example/notes",
    ]:
        path.chmod(stat.S_IMODE(path.stat().st_mode) & ~0o222)
    verifier = write(
        root / "verify-learning-bundle",
        "#!/bin/sh\nprintf 'sha256:%s\\n' '" + LEARNING_DIGEST + "'\n",
        0o755,
    )
    return bundle, verifier


def make_root_manifest(path: Path) -> None:
    source = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))
    browser = source["components"]["agent-remote-ego-browser"]
    browser["version"] = VERSION
    browser["commit"] = "0" * 40
    browser["release_published"] = False
    browser["production_ready"] = False
    browser["readiness_blockers"] = [
        "unpublished_component_commit",
        "release_certificate_unpinned",
        "learning_bundle_signing_private_key_unavailable",
        "production_release_evidence_unavailable",
    ]
    browser["signer_certificate_sha256"] = None
    browser["learning_bundle_digest"] = None
    browser["learning_bundle_signing_key_id"] = LEARNING_KEY_ID
    write(path, source)


def base_args(root: Path, root_manifest: Path) -> list[str]:
    bridge, manifest, _value, commit = make_bridge(root)
    bundle, verifier = make_learning_bundle(root)
    archive = (
        manifest.parent / f"agent-remote-ego-browser-macos-universal-{VERSION}.tar.gz"
    )
    signing = (
        manifest.parent
        / f"agent-remote-ego-browser-macos-universal-{VERSION}.community-signing.json"
    )
    release_json = write(
        root / "release.json",
        {
            "tagName": f"v{VERSION}",
            "isDraft": False,
            "isPrerelease": False,
            "publishedAt": "2026-09-08T00:00:00Z",
        },
    )
    args = [
        sys.executable,
        str(SCRIPT),
        "--manifest",
        str(root_manifest),
        "--bridge-repository",
        str(bridge),
        "--bridge-release-manifest",
        str(manifest),
        "--bridge-release-archive",
        str(archive),
        "--bridge-artifact-dir",
        str(manifest.parent),
        "--bridge-signing-evidence",
        str(signing),
        "--bridge-archive-sigstore",
        str(archive) + ".sigstore.json",
        "--bridge-manifest-sigstore",
        str(manifest) + ".sigstore.json",
        "--bridge-provenance",
        str(write(root / "bridge.provenance.json", b"provenance\n", 0o444)),
        "--learning-bundle",
        str(bundle),
        "--learning-bundle-verifier",
        str(verifier),
        "--github-release-json",
        str(release_json),
        "--commit",
        commit,
        "--certificate-sha256",
        CERTIFICATE,
        "--learning-bundle-key-id",
        LEARNING_KEY_ID,
    ]
    return args


def make_evidence(
    root: Path, candidate: dict[str, object], bridge_args: list[str]
) -> Path:
    fields: dict[str, object] = {
        "schema_version": 9,
        "release_profile": "community-local-trust",
        "production_ready": True,
        "apple_notarized": False,
        "public_distribution": False,
        "manual_trust_required": True,
        "release_version": candidate["components"]["agent-remote-server"]["version"],
        "issued_at": "2026-09-08T00:00:00Z",
        "distribution_version": candidate["distribution_version"],
        "release_manifest_sha256": hashlib.sha256(canonical(candidate)).hexdigest(),
        "components": candidate["components"],
        "server_sha256": "1" * 64,
        "application_sha256": "2" * 64,
        "node_artifacts_sha256": {
            target: "3" * 64
            for target in (
                "linux-amd64-glibc",
                "linux-arm64-glibc",
                "linux-amd64-musl",
                "linux-arm64-musl",
            )
        },
        "proxy_artifacts_sha256": {
            target: "4" * 64
            for target in (
                "linux-amd64-glibc",
                "linux-arm64-glibc",
                "linux-amd64-musl",
                "linux-arm64-musl",
            )
        },
        "sbom_sha256": "5" * 64,
        "provenance_sha256": "6" * 64,
        "signing_notarization_sha256": "7" * 64,
        "community_signing_sha256": "8" * 64,
        "automated_release_checks_sha256": "9" * 64,
        "risk_acceptance_sha256": "a" * 64,
        "ego_browser_release_manifest_sha256": hashlib.sha256(
            Path(
                bridge_args[bridge_args.index("--bridge-release-manifest") + 1]
            ).read_bytes()
        ).hexdigest(),
        "ego_browser_release_archive_sha256": hashlib.sha256(
            Path(
                bridge_args[bridge_args.index("--bridge-release-archive") + 1]
            ).read_bytes()
        ).hexdigest(),
        "ego_browser_signing_evidence_sha256": hashlib.sha256(
            Path(
                bridge_args[bridge_args.index("--bridge-signing-evidence") + 1]
            ).read_bytes()
        ).hexdigest(),
        "ego_browser_learning_bundle_sha256": LEARNING_DIGEST,
        "ego_browser_sigstore_sha256": hashlib.sha256(
            Path(
                bridge_args[bridge_args.index("--bridge-archive-sigstore") + 1]
            ).read_bytes()
        ).hexdigest(),
        "ego_browser_provenance_sha256": hashlib.sha256(
            Path(bridge_args[bridge_args.index("--bridge-provenance") + 1]).read_bytes()
        ).hexdigest(),
        "ci_run_url": "https://github.com/Agent-Remote/agent-remote/actions/runs/1",
        "node_sha256": None,
        "proxy_sha256": None,
        "security_tests_sha256": None,
        "security_review_sha256": None,
        "outbound_policy_sha256": None,
        "local_claude_isolation_sha256": None,
        "stop_revocation_sha256": None,
        "compatibility_sha256": None,
        "computer_use_v2_evidence_sha256": None,
    }
    key = Ed25519PrivateKey.generate()
    fields["signature"] = base64.b64encode(key.sign(compact(fields))).decode()
    evidence = write(root / "production-evidence.json", fields, 0o444)
    public = key.public_key().public_bytes_raw()
    write(root / "production-public-key.txt", base64.b64encode(public).decode(), 0o444)
    return evidence


def test_promotion_prepares_and_applies_atomically(tmp_path: Path) -> None:
    root_manifest = tmp_path / "release-manifest.json"
    make_root_manifest(root_manifest)
    args = base_args(tmp_path, root_manifest)
    candidate_path = tmp_path / "candidate.json"
    prepare = subprocess.run(
        [*args, "--prepare-only", "--candidate-output", str(candidate_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(prepare.stdout)["production_ready"] is True
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    evidence = make_evidence(tmp_path, candidate, args)
    public_key = tmp_path / "production-public-key.txt"
    before = root_manifest.read_bytes()
    subprocess.run(
        [
            *args,
            "--candidate-manifest",
            str(candidate_path),
            "--production-evidence",
            str(evidence),
            "--production-evidence-public-key",
            public_key.read_text().strip(),
        ],
        check=True,
    )
    assert root_manifest.read_bytes() != before
    promoted = json.loads(root_manifest.read_text(encoding="utf-8"))["components"][
        "agent-remote-ego-browser"
    ]
    assert promoted["release_published"] is True
    assert promoted["production_ready"] is True
    assert promoted["readiness_blockers"] == []
    assert promoted["commit"] != "0" * 40


def test_promotion_rejects_bad_evidence_without_mutating_manifest(
    tmp_path: Path,
) -> None:
    root_manifest = tmp_path / "release-manifest.json"
    make_root_manifest(root_manifest)
    args = base_args(tmp_path, root_manifest)
    candidate_path = tmp_path / "candidate.json"
    subprocess.run(
        [*args, "--prepare-only", "--candidate-output", str(candidate_path)], check=True
    )
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    evidence = make_evidence(tmp_path, candidate, args)
    value = json.loads(evidence.read_text(encoding="utf-8"))
    value["ego_browser_release_archive_sha256"] = "f" * 64
    evidence.chmod(0o600)
    evidence.write_bytes(canonical(value))
    before = root_manifest.read_bytes()
    result = subprocess.run(
        [
            *args,
            "--candidate-manifest",
            str(candidate_path),
            "--production-evidence",
            str(evidence),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert root_manifest.read_bytes() == before


def test_promotion_rejects_candidate_digest_drift(tmp_path: Path) -> None:
    root_manifest = tmp_path / "release-manifest.json"
    make_root_manifest(root_manifest)
    args = base_args(tmp_path, root_manifest)
    candidate_path = tmp_path / "candidate.json"
    subprocess.run(
        [*args, "--prepare-only", "--candidate-output", str(candidate_path)], check=True
    )
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    evidence = make_evidence(tmp_path, candidate, args)
    candidate["components"]["agent-remote-ego-browser"]["readiness_blockers"] = [
        "drift"
    ]
    candidate_path.write_bytes(canonical(candidate))
    before = root_manifest.read_bytes()
    result = subprocess.run(
        [
            *args,
            "--candidate-manifest",
            str(candidate_path),
            "--production-evidence",
            str(evidence),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert root_manifest.read_bytes() == before


def test_prepare_rejects_each_trust_boundary_without_mutating_root(
    tmp_path: Path,
) -> None:
    """Every pre-promotion trust failure must leave the root manifest untouched."""

    mutators = {
        "missing-tag": lambda args, root: subprocess.run(
            ["git", "-C", args[args.index("--bridge-repository") + 1], "tag", "-d", f"v{VERSION}"],
            check=True,
            capture_output=True,
        ),
        "prerelease": lambda args, root: None,
        "draft-release": lambda args, root: None,
        "certificate": lambda args, root: args.__setitem__(
            args.index("--certificate-sha256") + 1, "c" * 64
        ),
        "learning-digest": lambda args, root: write(
            root / "verify-learning-bundle",
            "#!/bin/sh\nprintf 'sha256:%s\\n' 'c" + "c" * 63 + "'\n",
            0o755,
        ),
        "dirty-worktree": lambda args, root: write(
            Path(args[args.index("--bridge-repository") + 1]) / "untracked.txt",
            b"dirty\n",
        ),
        "nested-signatures": lambda args, root: None,
    }

    for label, mutator in mutators.items():
        with tempfile.TemporaryDirectory(dir=tmp_path) as temporary:
            case_root = Path(temporary)
            root_manifest = case_root / "release-manifest.json"
            make_root_manifest(root_manifest)
            args = base_args(case_root, root_manifest)
            if label in {"prerelease", "draft-release"}:
                release_path = Path(args[args.index("--github-release-json") + 1])
                value = json.loads(release_path.read_text(encoding="utf-8"))
                value["isPrerelease" if label == "prerelease" else "isDraft"] = True
                write(release_path, value)
            elif label == "nested-signatures":
                manifest_path = Path(
                    args[args.index("--bridge-release-manifest") + 1]
                )
                value = json.loads(manifest_path.read_text(encoding="utf-8"))
                value["nested_signatures_verified"] = False
                manifest_path.chmod(0o644)
                write(manifest_path, value, 0o444)
            else:
                mutator(args, case_root)
            candidate = case_root / "candidate.json"
            before = root_manifest.read_bytes()
            result = subprocess.run(
                [*args, "--prepare-only", "--candidate-output", str(candidate)],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 2, label
            assert root_manifest.read_bytes() == before, label
            assert not candidate.exists(), label


def test_promotion_rejects_manifest_and_candidate_symlinks(tmp_path: Path) -> None:
    """Promotion inputs must keep their final path component non-following."""

    case_one = tmp_path / "case-one"
    case_one.mkdir()
    real_manifest = case_one / "real-release-manifest.json"
    make_root_manifest(real_manifest)
    manifest_link = case_one / "release-manifest.json"
    manifest_link.symlink_to(real_manifest)
    args = base_args(case_one, manifest_link)
    candidate = case_one / "candidate.json"
    before = real_manifest.read_bytes()
    result = subprocess.run(
        [*args, "--prepare-only", "--candidate-output", str(candidate)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert real_manifest.read_bytes() == before

    # A dangling link must not be resolved into an arbitrary output target.
    case_two = tmp_path / "case-two"
    case_two.mkdir()
    real_manifest = case_two / "release-manifest.json"
    make_root_manifest(real_manifest)
    target = case_two / "candidate-target.json"
    candidate_link = case_two / "candidate-link.json"
    candidate_link.symlink_to(target)
    args = base_args(case_two, real_manifest)
    result = subprocess.run(
        [*args, "--prepare-only", "--candidate-output", str(candidate_link)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert not target.exists()
