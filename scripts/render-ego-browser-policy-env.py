#!/usr/bin/env python3
"""Render one Compose policy file from certified ego-browser release metadata."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path

from ego_browser_policy import EGO_BROWSER_COMPONENT
from release_manifest import load_release_manifest, release_manifest_sha256

MAXIMUM_EVIDENCE_BYTES = 2 * 1024 * 1024
SHA256 = re.compile(r"^[0-9a-f]{64}$")
MANIFEST_FIELDS = (
    ("EGO_BROWSER_EXPECTED_RELEASE_PROFILE", "profile"),
    ("EGO_BROWSER_EXPECTED_SIGNER_CERTIFICATE_SHA256", "signer_certificate_sha256"),
    ("EGO_BROWSER_EXPECTED_WRAPPER_VERSION", "wrapper_version"),
    ("EGO_BROWSER_EXPECTED_SKILL_VERSION", "skill_version"),
    ("EGO_BROWSER_EXPECTED_SKILL_TREE_SHA256", "skill_tree_sha256"),
    ("EGO_BROWSER_EXPECTED_SKILL_COMMIT", "skill_commit"),
    ("EGO_BROWSER_EXPECTED_LOCAL_RUNTIME_VERSION", "local_ego_browser_runtime_version"),
    ("EGO_BROWSER_EXPECTED_PROTOCOL_VERSION", "protocol_version"),
    (
        "EGO_BROWSER_EXPECTED_LEARNING_BUNDLE_SIGNING_KEY_ID",
        "learning_bundle_signing_key_id",
    ),
)
EVIDENCE_FIELDS = (
    (
        "EGO_BROWSER_EXPECTED_LEARNING_BUNDLE_SHA256",
        "ego_browser_learning_bundle_sha256",
    ),
    (
        "EGO_BROWSER_EXPECTED_BRIDGE_RELEASE_MANIFEST_SHA256",
        "ego_browser_release_manifest_sha256",
    ),
    (
        "EGO_BROWSER_EXPECTED_BRIDGE_RELEASE_ARCHIVE_SHA256",
        "ego_browser_release_archive_sha256",
    ),
    (
        "EGO_BROWSER_EXPECTED_BRIDGE_SIGNING_EVIDENCE_SHA256",
        "ego_browser_signing_evidence_sha256",
    ),
    ("EGO_BROWSER_EXPECTED_BRIDGE_SIGSTORE_SHA256", "ego_browser_sigstore_sha256"),
    (
        "EGO_BROWSER_EXPECTED_BRIDGE_PROVENANCE_SHA256",
        "ego_browser_provenance_sha256",
    ),
)


def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Build a JSON object while rejecting duplicate fields."""

    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate release evidence field: {key}")
        value[key] = item
    return value


def load_evidence(path: Path) -> dict[str, object]:
    """Load a bounded regular schema-9 evidence document."""

    metadata = path.stat(follow_symlinks=False)
    if (
        path.is_symlink()
        or not path.is_file()
        or not 0 < metadata.st_size <= MAXIMUM_EVIDENCE_BYTES
    ):
        raise ValueError("release evidence must be a bounded regular file")
    value = json.loads(path.read_bytes(), object_pairs_hook=reject_duplicates)
    if not isinstance(value, dict) or value.get("schema_version") != 9:
        raise ValueError("schema-9 release evidence is required")
    return value


def require_text(value: object, label: str, *, sha256: bool = False) -> str:
    """Return one safe environment value."""

    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\n" in value
        or "\r" in value
        or len(value) > 512
        or (sha256 and SHA256.fullmatch(value) is None)
    ):
        raise ValueError(f"{label} is invalid")
    return value


def render(manifest_path: Path, evidence_path: Path) -> str:
    """Render policy values after checking their release bindings."""

    manifest = load_release_manifest(manifest_path)
    evidence = load_evidence(evidence_path)
    components = manifest["components"]
    assert isinstance(components, dict)
    component = components[EGO_BROWSER_COMPONENT]
    assert isinstance(component, dict)
    manifest_digest = release_manifest_sha256(manifest_path)
    distribution_version = require_text(
        manifest["distribution_version"], "distribution version"
    )
    if (
        evidence.get("distribution_version") != distribution_version
        or evidence.get("release_manifest_sha256") != manifest_digest
        or evidence.get("release_profile") != component["profile"]
        or evidence.get("production_ready") is not True
        or evidence.get("components") != components
    ):
        raise ValueError("release evidence is not bound to the root manifest")

    values = [
        (name, require_text(component[field], field)) for name, field in MANIFEST_FIELDS
    ]
    evidence_values = {
        field: require_text(evidence.get(field), field, sha256=True)
        for _, field in EVIDENCE_FIELDS
    }
    if (
        evidence_values["ego_browser_learning_bundle_sha256"]
        != component["learning_bundle_digest"]
        or evidence_values["ego_browser_release_manifest_sha256"]
        != component["bridge_manifest_sha256"]
        or evidence_values["ego_browser_release_archive_sha256"]
        != component["artifact_sha256"]
    ):
        raise ValueError("ego-browser evidence digests do not match the root manifest")
    values.extend((name, evidence_values[field]) for name, field in EVIDENCE_FIELDS)
    values.extend(
        (
            ("EGO_BROWSER_EXPECTED_DISTRIBUTION_VERSION", distribution_version),
            ("EGO_BROWSER_EXPECTED_ROOT_MANIFEST_SHA256", manifest_digest),
        )
    )
    return "".join(f"{name}={value}\n" for name, value in values)


def write_atomic(path: Path, content: str) -> None:
    """Replace the destination with a complete owner-written policy file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as temporary:
        temporary.write(content)
        temporary.flush()
        os.fsync(temporary.fileno())
        replacement = Path(temporary.name)
    replacement.chmod(0o644)
    replacement.replace(path)


def main() -> None:
    """Parse arguments and write the generated policy file."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        content = render(args.manifest, args.evidence)
        write_atomic(args.output, content)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
