"""Strict parsing helpers for certified production release manifests."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

COMPONENTS = (
    "agent-remote-server",
    "agent-remote-node",
    "agent-remote-cli",
    "agent-remote-admin-web",
    "agent-remote-device",
)
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-.+][0-9A-Za-z.-]+)?$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
RELEASE_WORKFLOW = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\.ya?ml$")


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
        value["schema_version"] not in {1, 2}
        or not isinstance(distribution_version, str)
        or SEMVER.fullmatch(distribution_version) is None
    ):
        raise ValueError("release manifest header is invalid")
    components = value["components"]
    if not isinstance(components, dict) or set(components) != set(COMPONENTS):
        raise ValueError("release manifest component inventory is invalid")
    for name in COMPONENTS:
        component = components[name]
        expected_fields = {"repository", "version", "commit"}
        if value["schema_version"] == 2:
            expected_fields.add("release_workflow")
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
    return value


def release_manifest_sha256(path: Path) -> str:
    """Return the exact source manifest SHA-256 after validating it."""

    load_release_manifest(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()
