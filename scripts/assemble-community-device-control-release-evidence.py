#!/usr/bin/env python3
"""Assemble an unsigned community-local-trust production evidence draft."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-.+][0-9A-Za-z.-]+)?$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
LABELS = ("server", "node", "application", "proxy")
MAXIMUM_INPUT_BYTES = 256 * 1024 * 1024


def open_safe(path: Path) -> BinaryIO:
    """Open one bounded regular input without following its final symlink."""

    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    info = os.fstat(descriptor)
    if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= MAXIMUM_INPUT_BYTES:
        os.close(descriptor)
        raise ValueError(f"unsafe input: {path}")
    return os.fdopen(descriptor, "rb")


def digest(path: Path) -> str:
    """Return the SHA-256 digest of one safe input."""

    value = hashlib.sha256()
    with open_safe(path) as source:
        while chunk := source.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Build a JSON object while rejecting duplicate names."""

    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def load_object(path: Path) -> dict[str, object]:
    """Load one safe JSON object with duplicate-key rejection."""

    with open_safe(path) as source:
        value = json.load(source, object_pairs_hook=reject_duplicates)
    if not isinstance(value, dict):
        raise ValueError(f"JSON input is not an object: {path}")
    return value


def labeled_paths(values: list[str], option: str) -> dict[str, Path]:
    """Parse exactly one labeled path for every release component."""

    result: dict[str, Path] = {}
    for value in values:
        label, separator, raw_path = value.partition("=")
        if not separator or label not in LABELS or label in result:
            raise ValueError(f"invalid {option}: {value}")
        path = Path(raw_path)
        with open_safe(path):
            pass
        result[label] = path
    if set(result) != set(LABELS):
        raise ValueError(f"{option} must include {', '.join(LABELS)}")
    return result


def canonical(value: object) -> bytes:
    """Encode deterministic ASCII JSON with one trailing newline."""

    return (
        json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n"
    )


def write_new(path: Path, data: bytes) -> None:
    """Create one owner-only output without overwriting an existing file."""

    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as output:
        output.write(data)
        output.flush()
        os.fsync(output.fileno())


def validate_timestamp(value: str, name: str) -> str:
    """Require one timezone-aware ISO 8601 timestamp."""

    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must include a timezone")
    return value


def validate_community_signing(
    path: Path, version: str, application_sha256: str
) -> None:
    """Validate the self-signing record against the exact application archive."""

    value = load_object(path)
    required = {
        "schema_version": 1,
        "release_version": version,
        "profile": "community-local-trust",
        "production_ready": True,
        "apple_notarized": False,
        "public_distribution": False,
        "signing_type": "project-self-signed",
        "application_signature_verified": True,
        "nested_signatures_verified": True,
        "hardened_runtime": True,
        "outbound_policy": "application-enforced",
        "application_sha256": application_sha256,
        "bundle_identifier": "dev.agentremote.device",
        "broker_bundle_identifier": "dev.agentremote.device.network-broker",
    }
    if any(value.get(key) != expected for key, expected in required.items()):
        raise ValueError("community signing evidence is inconsistent")
    for field in ("signer_certificate_sha1", "signer_certificate_sha256"):
        candidate = value.get(field)
        expected = r"[A-F0-9]{40}" if field.endswith("sha1") else r"[a-f0-9]{64}"
        if not isinstance(candidate, str) or re.fullmatch(expected, candidate) is None:
            raise ValueError(f"community signing {field} is invalid")


def validate_automation(path: Path, version: str) -> None:
    """Validate the official-runner automation summary."""

    value = load_object(path)
    if (
        value.get("schema_version") != 1
        or value.get("release_version") != version
        or value.get("profile") != "community-local-trust"
        or value.get("production_ready") is not True
        or value.get("official_runners_only") is not True
        or value.get("critical_high_vulnerabilities") != 0
    ):
        raise ValueError("community automation evidence is incomplete")
    checks = value.get("checks")
    required_checks = {
        "coordinated_release",
        "protocol_tests",
        "cross_component_e2e",
        "fuzz",
        "stop_revocation",
        "compatibility",
        "supply_chain",
    }
    if not isinstance(checks, dict) or set(checks) != required_checks:
        raise ValueError("community automation check inventory is invalid")
    if any(result is not True for result in checks.values()):
        raise ValueError("community automation checks did not all pass")
    ci_runs = value.get("ci_runs")
    repositories = {
        "agent-remote",
        "agent-remote-server",
        "agent-remote-node",
        "agent-remote-cli",
        "agent-remote-admin-web",
        "agent-remote-device",
    }
    if not isinstance(ci_runs, dict) or set(ci_runs) != repositories:
        raise ValueError("community CI run inventory is invalid")
    for repository, run in ci_runs.items():
        if (
            not isinstance(run, dict)
            or set(run) != {"sha", "url", "conclusion"}
            or run["conclusion"] != "success"
            or not isinstance(run["sha"], str)
            or GIT_SHA.fullmatch(run["sha"]) is None
            or not isinstance(run["url"], str)
            or not run["url"].startswith(
                f"https://github.com/Agent-Remote/{repository}/actions/runs/"
            )
        ):
            raise ValueError(f"community CI run is invalid for {repository}")


def validate_risk_acceptance(path: Path, version: str) -> None:
    """Validate explicit deployment acceptance of the reduced security profile."""

    value = load_object(path)
    required_risks = {
        "apple_notarization_absent",
        "manual_gatekeeper_trust",
        "system_network_filter_absent",
        "independent_security_review_absent",
    }
    if (
        value.get("schema_version") != 1
        or value.get("release_version") != version
        or value.get("profile") != "community-local-trust"
        or value.get("accepted") is not True
        or not isinstance(value.get("accepted_by"), str)
        or not value["accepted_by"]
        or set(value.get("accepted_risks", [])) != required_risks
    ):
        raise ValueError("community risk acceptance is incomplete")
    validate_timestamp(str(value.get("accepted_at", "")), "accepted_at")


def main() -> None:
    """Validate inputs and create the schema-2 unsigned production draft."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--server-metadata", type=Path, required=True)
    parser.add_argument("--node-artifact", type=Path, required=True)
    parser.add_argument("--application-artifact", type=Path, required=True)
    parser.add_argument("--proxy-artifact", type=Path, required=True)
    parser.add_argument("--sbom", action="append", default=[])
    parser.add_argument("--provenance", action="append", default=[])
    parser.add_argument("--community-signing", type=Path, required=True)
    parser.add_argument("--automation-evidence", type=Path, required=True)
    parser.add_argument("--risk-acceptance", type=Path, required=True)
    parser.add_argument("--ci-run-url", required=True)
    parser.add_argument("--issued-at", required=True)
    parser.add_argument("--expires-at", required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()

    try:
        if SEMVER.fullmatch(args.release_version) is None:
            raise ValueError("release version is invalid")
        issued_at = validate_timestamp(args.issued_at, "issued_at")
        expires_at = validate_timestamp(args.expires_at, "expires_at")
        artifacts = {
            "node": args.node_artifact,
            "application": args.application_artifact,
            "proxy": args.proxy_artifact,
        }
        artifact_digests = {label: digest(path) for label, path in artifacts.items()}
        server = load_object(args.server_metadata)
        server_digest = server.get("digest")
        if server.get("version") != args.release_version or not isinstance(server_digest, str):
            raise ValueError("server metadata does not match the release")
        server_sha256 = server_digest.removeprefix("sha256:")
        if SHA256.fullmatch(server_sha256) is None:
            raise ValueError("server image digest is invalid")

        sboms = labeled_paths(args.sbom, "sbom")
        provenance = labeled_paths(args.provenance, "provenance")
        validate_community_signing(
            args.community_signing,
            args.release_version,
            artifact_digests["application"],
        )
        validate_automation(args.automation_evidence, args.release_version)
        validate_risk_acceptance(args.risk_acceptance, args.release_version)

        args.output_directory.mkdir(mode=0o700, parents=True, exist_ok=False)
        sbom_inventory = args.output_directory / "sbom-inventory.json"
        provenance_inventory = args.output_directory / "provenance-inventory.json"
        write_new(
            sbom_inventory,
            canonical({label: digest(path) for label, path in sorted(sboms.items())}),
        )
        write_new(
            provenance_inventory,
            canonical({label: digest(path) for label, path in sorted(provenance.items())}),
        )
        automation_sha256 = digest(args.automation_evidence)
        signing_sha256 = digest(args.community_signing)
        risk_sha256 = digest(args.risk_acceptance)
        draft = {
            "schema_version": 2,
            "release_profile": "community-local-trust",
            "production_ready": True,
            "apple_notarized": False,
            "public_distribution": False,
            "manual_trust_required": True,
            "release_version": args.release_version,
            "issued_at": issued_at,
            "expires_at": expires_at,
            "server_sha256": server_sha256,
            "node_sha256": artifact_digests["node"],
            "application_sha256": artifact_digests["application"],
            "proxy_sha256": artifact_digests["proxy"],
            "sbom_sha256": digest(sbom_inventory),
            "provenance_sha256": digest(provenance_inventory),
            "security_tests_sha256": None,
            "security_review_sha256": None,
            "signing_notarization_sha256": signing_sha256,
            "outbound_policy_sha256": None,
            "local_claude_isolation_sha256": None,
            "stop_revocation_sha256": None,
            "compatibility_sha256": None,
            "community_signing_sha256": signing_sha256,
            "automated_release_checks_sha256": automation_sha256,
            "risk_acceptance_sha256": risk_sha256,
            "ci_run_url": args.ci_run_url,
        }
        write_new(args.output_directory / "release-evidence-draft.json", canonical(draft))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"community evidence assembly failed: {exc}\n")


if __name__ == "__main__":
    main()
