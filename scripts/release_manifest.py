"""Strict parsing helpers for certified production release manifests."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

LEGACY_COMPONENTS = (
    "agent-remote-server",
    "agent-remote-node",
    "agent-remote-cli",
    "agent-remote-admin-web",
    "agent-remote-device",
)
EGO_BROWSER_COMPONENT = "agent-remote-ego-browser"
COMPONENTS = (*LEGACY_COMPONENTS, EGO_BROWSER_COMPONENT)
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-.+][0-9A-Za-z.-]+)?$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
RELEASE_WORKFLOW = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\.ya?ml$")
UNPUBLISHED_COMMIT = "0" * 40
EGO_BROWSER_FIELDS = {
    "release_published",
    "profile",
    "signing_type",
    "signer_certificate_sha256",
    "production_ready",
    "readiness_blockers",
    "apple_notarized",
    "public_distribution",
    "hardened_runtime",
    "nested_signatures_verified",
    "outbound_policy",
    "credential_profile",
    "learning_bundle_digest",
    "learning_bundle_signing_key_id",
    "skill_version",
    "skill_commit",
    "skill_tree_sha256",
    "local_ego_browser_runtime_version",
    "protocol_version",
}


def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Build a JSON object while rejecting duplicate fields."""

    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate release manifest field: {key}")
        value[key] = item
    return value


def load_release_manifest(path: Path) -> dict[str, object]:
    """Load and strictly validate one production release manifest."""

    if not path.is_file() or path.is_symlink():
        raise ValueError("release manifest must be a regular file")
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=reject_duplicates)
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "distribution_version",
        "components",
    }:
        raise ValueError("release manifest fields are invalid")
    distribution_version = value["distribution_version"]
    if (
        isinstance(value["schema_version"], bool)
        or not isinstance(value["schema_version"], int)
        or value["schema_version"] not in {1, 2, 3}
        or not isinstance(distribution_version, str)
        or SEMVER.fullmatch(distribution_version) is None
    ):
        raise ValueError("release manifest header is invalid")
    schema_version = value["schema_version"]
    expected_components = COMPONENTS if schema_version == 3 else LEGACY_COMPONENTS
    components = value["components"]
    if not isinstance(components, dict) or set(components) != set(expected_components):
        raise ValueError("release manifest component inventory is invalid")
    for name in expected_components:
        component = components[name]
        expected_fields = {"repository", "version", "commit"}
        if schema_version >= 2:
            expected_fields.add("release_workflow")
        if schema_version == 3 and name == EGO_BROWSER_COMPONENT:
            expected_fields.update(EGO_BROWSER_FIELDS)
        if not isinstance(component, dict) or set(component) != expected_fields:
            raise ValueError(f"{name}: release manifest fields are invalid")
        if component["repository"] != f"Agent-Remote/{name}":
            raise ValueError(f"{name}: release manifest repository is invalid")
        version = component["version"]
        commit = component["commit"]
        if not isinstance(version, str) or SEMVER.fullmatch(version) is None:
            raise ValueError(f"{name}: release manifest version is invalid")
        if not isinstance(commit, str) or GIT_SHA.fullmatch(commit) is None:
            raise ValueError(f"{name}: release manifest commit is invalid")
        workflow = component.get("release_workflow", "release.yml")
        if not isinstance(workflow, str) or RELEASE_WORKFLOW.fullmatch(workflow) is None:
            raise ValueError(f"{name}: release manifest workflow is invalid")
        if name == EGO_BROWSER_COMPONENT:
            _validate_ego_browser_component(component)
    return value


def _validate_ego_browser_component(component: dict[str, object]) -> None:
    """Validate the browser Bridge release and security-evidence state."""

    blockers = component["readiness_blockers"]
    certificate = component["signer_certificate_sha256"]
    learning_digest = component["learning_bundle_digest"]
    learning_key_id = component["learning_bundle_signing_key_id"]
    if (
        component["profile"] != "community-local-trust"
        or component["signing_type"] != "project-self-signed"
        or component["apple_notarized"] is not False
        or component["public_distribution"] is not False
        or component["hardened_runtime"] is not True
        or component["outbound_policy"] != "application-enforced"
        or component["credential_profile"] != "community_file"
        or not isinstance(learning_key_id, str)
        or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", learning_key_id) is None
        or component["skill_version"] != "1.2.3"
        or component["skill_commit"]
        != "36053d07001a910cb806a15d42d00fdea1cdea3d"
        or component["skill_tree_sha256"]
        != "262110a09678fd3e0bbb382400588dacb98b24659b3b4a57903703b65d133c7c"
        or component["local_ego_browser_runtime_version"] != "0.4.7.4"
        or component["protocol_version"] != "ego-browser-bridge-v1"
    ):
        raise ValueError("agent-remote-ego-browser: release profile is invalid")
    if (
        not isinstance(blockers, list)
        or any(not isinstance(item, str) or not item or len(item) > 128 for item in blockers)
        or len(blockers) != len(set(blockers))
    ):
        raise ValueError("agent-remote-ego-browser: readiness blockers are invalid")
    if certificate is not None and (
        not isinstance(certificate, str) or SHA256.fullmatch(certificate) is None
    ):
        raise ValueError("agent-remote-ego-browser: certificate digest is invalid")
    if learning_digest is not None and (
        not isinstance(learning_digest, str) or SHA256.fullmatch(learning_digest) is None
    ):
        raise ValueError("agent-remote-ego-browser: learning bundle digest is invalid")

    published = component["release_published"]
    ready = component["production_ready"]
    commit = component["commit"]
    nested_signatures = component["nested_signatures_verified"]
    if not isinstance(published, bool) or not isinstance(ready, bool):
        raise ValueError("agent-remote-ego-browser: readiness flags are invalid")
    if not published:
        if commit != UNPUBLISHED_COMMIT or ready:
            raise ValueError("agent-remote-ego-browser: unpublished state is invalid")
    elif commit == UNPUBLISHED_COMMIT:
        raise ValueError("agent-remote-ego-browser: published commit is invalid")
    if not isinstance(nested_signatures, bool):
        raise ValueError("agent-remote-ego-browser: signature evidence flag is invalid")

    expected_blockers: set[str] = set()
    if not published:
        expected_blockers.add("unpublished_component_commit")
    if certificate is None:
        expected_blockers.add("release_certificate_unpinned")
    if learning_digest is None:
        expected_blockers.add("learning_bundle_signing_private_key_unavailable")
    if not ready:
        expected_blockers.add("production_release_evidence_unavailable")
    if set(blockers) != expected_blockers:
        raise ValueError("agent-remote-ego-browser: readiness blockers do not match evidence")
    if ready and (
        not published
        or certificate is None
        or learning_digest is None
        or nested_signatures is not True
    ):
        raise ValueError("agent-remote-ego-browser: production readiness is unsupported")


def release_manifest_sha256(path: Path) -> str:
    """Return the exact source manifest SHA-256 after validating it."""

    load_release_manifest(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()
