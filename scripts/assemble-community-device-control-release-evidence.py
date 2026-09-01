#!/usr/bin/env python3
"""Assemble an unsigned community-local-trust production evidence draft."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import tarfile
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import BinaryIO

from release_manifest import load_release_manifest, release_manifest_sha256

SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-.+][0-9A-Za-z.-]+)?$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
TARGETS = (
    "linux-amd64-glibc",
    "linux-arm64-glibc",
    "linux-amd64-musl",
    "linux-arm64-musl",
)
LABEL = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
MAXIMUM_INPUT_BYTES = 256 * 1024 * 1024
MAXIMUM_ARCHIVE_MEMBERS = 4_096
MAXIMUM_ARCHIVE_EXPANDED_BYTES = 512 * 1024 * 1024
MAXIMUM_V2_EVIDENCE_AGE = timedelta(days=30)
V2_EVIDENCE_KEYS = {
    "artifacts",
    "collected_at",
    "details",
    "evidence_sha256",
    "method",
    "producer",
    "release_profile",
    "release_version",
    "schema_version",
    "target",
}
V2_DETAIL_KEYS = {
    "action_latency_p95_ms",
    "artifact_digest_bound",
    "chrome_passed",
    "coordinate_fallback_percent",
    "current_mcp_runtime_passed",
    "electron_fallback_passed",
    "firefox_passed",
    "golden_prompt_replay_passed",
    "model_usage_summary_bound",
    "model_visible_image_reduction_percent",
    "native_application_passed",
    "report_sha256",
    "rollback_rehearsed",
    "safari_passed",
    "sensitive_telemetry_detected",
    "settle_latency_p95_ms",
    "signed_installation",
    "success_rate_regressed",
    "wrong_target_count",
}


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


def labeled_paths(
    values: list[str], option: str, required: set[str]
) -> dict[str, Path]:
    """Parse exactly one safe labeled path for every required input."""

    result: dict[str, Path] = {}
    for value in values:
        label, separator, raw_path = value.partition("=")
        if not separator or LABEL.fullmatch(label) is None or label in result:
            raise ValueError(f"invalid {option}: {value}")
        path = Path(raw_path)
        with open_safe(path):
            pass
        result[label] = path
    if set(result) != required:
        raise ValueError(f"{option} must include {', '.join(sorted(required))}")
    return result


def target_paths(values: list[str], option: str) -> dict[str, Path]:
    """Parse one artifact path for every supported Linux target."""

    return labeled_paths(values, option, set(TARGETS))


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


def copy_new(source_path: Path, output_path: Path) -> str:
    """Copy one safe input into an owner-only output and return its digest."""

    value = hashlib.sha256()
    descriptor = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as output, open_safe(source_path) as source:
        while chunk := source.read(1024 * 1024):
            output.write(chunk)
            value.update(chunk)
        output.flush()
        os.fsync(output.fileno())
    return value.hexdigest()


def validate_timestamp(value: str, name: str) -> str:
    """Require one timezone-aware ISO 8601 timestamp."""

    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must include a timezone")
    return value


def parse_timestamp(value: object, name: str) -> datetime:
    """Parse one timezone-aware ISO 8601 timestamp."""

    if not isinstance(value, str):
        raise ValueError(f"{name} must be an ISO 8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO 8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must include a timezone")
    return parsed


def require_nonnegative_integer(value: object, name: str) -> int:
    """Require a nonnegative JSON integer that is not a boolean."""

    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return value


def require_percentage(value: object, name: str) -> float:
    """Require a finite percentage in the inclusive zero-to-100 range."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a percentage")
    percentage = float(value)
    if not math.isfinite(percentage) or not 0 <= percentage <= 100:
        raise ValueError(f"{name} must be a percentage")
    return percentage


def validate_v2_details(value: object) -> str:
    """Validate the zero-content Community Computer Use v2 acceptance summary."""

    if not isinstance(value, dict) or set(value) != V2_DETAIL_KEYS:
        raise ValueError("Community Computer Use v2 detail fields are invalid")
    for field in {
        "artifact_digest_bound",
        "chrome_passed",
        "current_mcp_runtime_passed",
        "electron_fallback_passed",
        "firefox_passed",
        "golden_prompt_replay_passed",
        "model_usage_summary_bound",
        "native_application_passed",
        "rollback_rehearsed",
        "safari_passed",
        "signed_installation",
    }:
        if value[field] is not True:
            raise ValueError(f"Community Computer Use v2 {field} must be true")
    for field in {"sensitive_telemetry_detected", "success_rate_regressed"}:
        if value[field] is not False:
            raise ValueError(f"Community Computer Use v2 {field} must be false")
    report_digest = value["report_sha256"]
    if not isinstance(report_digest, str) or SHA256.fullmatch(report_digest) is None:
        raise ValueError("Community Computer Use v2 report digest is invalid")
    if (
        require_nonnegative_integer(value["wrong_target_count"], "wrong_target_count")
        != 0
    ):
        raise ValueError("Community Computer Use v2 contains wrong-target actions")
    if (
        require_percentage(
            value["model_visible_image_reduction_percent"], "image reduction"
        )
        < 70
    ):
        raise ValueError("Community Computer Use v2 image reduction is below target")
    if (
        require_nonnegative_integer(value["action_latency_p95_ms"], "action latency")
        > 1_000
    ):
        raise ValueError("Community Computer Use v2 action latency exceeds target")
    if (
        require_nonnegative_integer(value["settle_latency_p95_ms"], "settle latency")
        > 5_000
    ):
        raise ValueError("Community Computer Use v2 settle latency exceeds target")
    if (
        require_percentage(value["coordinate_fallback_percent"], "coordinate fallback")
        >= 20
    ):
        raise ValueError("Community Computer Use v2 coordinate fallback exceeds target")
    return report_digest


def validate_report_archive(path: Path, expected_report_digest: str) -> None:
    """Validate a bounded report archive and require the bound report as a member."""

    member_digests: set[str] = set()
    members = 0
    expanded_bytes = 0
    names: set[str] = set()
    try:
        with (
            open_safe(path) as source,
            tarfile.open(fileobj=source, mode="r:gz") as archive,
        ):
            for member in archive:
                members += 1
                if members > MAXIMUM_ARCHIVE_MEMBERS:
                    raise ValueError(
                        "Community Computer Use v2 archive has too many members"
                    )
                member_path = PurePosixPath(member.name)
                canonical_name = member_path.as_posix()
                archived_name = (
                    member.name.rstrip("/") if member.isdir() else member.name
                )
                if (
                    not member.name
                    or "\\" in member.name
                    or member_path.is_absolute()
                    or any(part in ("", ".", "..") for part in member_path.parts)
                    or archived_name != canonical_name
                    or member.name in names
                ):
                    raise ValueError(
                        "Community Computer Use v2 archive member path is invalid"
                    )
                names.add(member.name)
                if member.isdir():
                    continue
                if not member.isfile() or member.size < 0:
                    raise ValueError(
                        "Community Computer Use v2 archive member type is invalid"
                    )
                expanded_bytes += member.size
                if expanded_bytes > MAXIMUM_ARCHIVE_EXPANDED_BYTES:
                    raise ValueError(
                        "Community Computer Use v2 archive expands beyond the limit"
                    )
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise ValueError(
                        "Community Computer Use v2 archive member cannot be read"
                    )
                value = hashlib.sha256()
                bytes_read = 0
                with extracted:
                    while chunk := extracted.read(1024 * 1024):
                        bytes_read += len(chunk)
                        value.update(chunk)
                if bytes_read != member.size:
                    raise ValueError(
                        "Community Computer Use v2 archive member is truncated"
                    )
                member_digests.add(value.hexdigest())
    except (OSError, tarfile.TarError) as exc:
        raise ValueError(
            "Community Computer Use v2 evidence archive is invalid"
        ) from exc
    if expanded_bytes == 0 or expected_report_digest not in member_digests:
        raise ValueError(
            "Community Computer Use v2 report is not present in the archive"
        )


def validate_v2_evidence(
    record_path: Path,
    archive_path: Path,
    target: str,
    version: str,
    artifacts: dict[str, str],
    issued_at: datetime,
) -> str:
    """Validate one artifact-bound Community v2 evidence record and return its digest."""

    value = load_object(record_path)
    if set(value) != V2_EVIDENCE_KEYS:
        raise ValueError("Community Computer Use v2 evidence fields are invalid")
    if (
        value["schema_version"] != 1
        or value["release_version"] != version
        or value["release_profile"] != "community-local-trust"
        or value["target"] != target
        or value["artifacts"] != artifacts
    ):
        raise ValueError(
            "Community Computer Use v2 evidence is not bound to the release"
        )
    for field in ("producer", "method"):
        text = value[field]
        if (
            not isinstance(text, str)
            or not text
            or text != text.strip()
            or len(text) > 500
        ):
            raise ValueError(f"Community Computer Use v2 {field} is invalid")
    evidence_digest = value["evidence_sha256"]
    if not isinstance(evidence_digest, str) or evidence_digest != digest(archive_path):
        raise ValueError("Community Computer Use v2 archive digest does not match")
    collected_at = parse_timestamp(value["collected_at"], "collected_at")
    if collected_at > issued_at or collected_at < issued_at - MAXIMUM_V2_EVIDENCE_AGE:
        raise ValueError("Community Computer Use v2 evidence age is invalid")
    report_digest = validate_v2_details(value["details"])
    validate_report_archive(archive_path, report_digest)
    return digest(record_path)


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
        "certified_composition",
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


def validate_risk_acceptance(path: Path, version: str, require_v2: bool) -> None:
    """Validate explicit deployment acceptance of the reduced security profile."""

    value = load_object(path)
    required_risks = {
        "apple_notarization_absent",
        "manual_gatekeeper_trust",
        "system_network_filter_absent",
        "independent_security_review_absent",
    }
    if require_v2:
        required_risks.add("community_computer_use_v2_without_apple_notarization")
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
    """Validate inputs and create a certified multi-version production draft."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--distribution-version", required=True)
    parser.add_argument("--release-manifest", type=Path, required=True)
    parser.add_argument("--server-metadata", type=Path, required=True)
    parser.add_argument("--node-artifact", action="append", default=[])
    parser.add_argument("--application-artifact", type=Path, required=True)
    parser.add_argument("--proxy-artifact", action="append", default=[])
    parser.add_argument("--sbom", action="append", default=[])
    parser.add_argument("--provenance", action="append", default=[])
    parser.add_argument("--community-signing", type=Path, required=True)
    parser.add_argument("--automation-evidence", type=Path, required=True)
    parser.add_argument("--risk-acceptance", type=Path, required=True)
    parser.add_argument("--computer-use-v2-evidence", type=Path)
    parser.add_argument("--computer-use-v2-evidence-archive", type=Path)
    parser.add_argument("--computer-use-v2-target", choices=TARGETS)
    parser.add_argument("--ci-run-url", required=True)
    parser.add_argument("--issued-at", required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()

    try:
        if SEMVER.fullmatch(args.release_version) is None:
            raise ValueError("release version is invalid")
        manifest = load_release_manifest(args.release_manifest)
        components = manifest["components"]
        assert isinstance(components, dict)
        if manifest["distribution_version"] != args.distribution_version:
            raise ValueError("distribution version does not match the release manifest")
        server_component = components["agent-remote-server"]
        node_component = components["agent-remote-node"]
        device_component = components["agent-remote-device"]
        assert isinstance(server_component, dict)
        assert isinstance(node_component, dict)
        assert isinstance(device_component, dict)
        if server_component["version"] != args.release_version:
            raise ValueError("server version does not match the release manifest")
        issued_at = validate_timestamp(args.issued_at, "issued_at")
        issued_at_value = parse_timestamp(issued_at, "issued_at")
        v2_inputs = (
            args.computer_use_v2_evidence,
            args.computer_use_v2_evidence_archive,
            args.computer_use_v2_target,
        )
        if any(value is not None for value in v2_inputs) and not all(
            value is not None for value in v2_inputs
        ):
            raise ValueError(
                "Community Computer Use v2 inputs must be provided together"
            )
        v2_enabled = all(value is not None for value in v2_inputs)
        node_artifacts = target_paths(args.node_artifact, "node artifact")
        proxy_artifacts = target_paths(args.proxy_artifact, "proxy artifact")
        application_sha256 = digest(args.application_artifact)
        node_digests = {
            target: digest(path) for target, path in sorted(node_artifacts.items())
        }
        proxy_digests = {
            target: digest(path) for target, path in sorted(proxy_artifacts.items())
        }
        server = load_object(args.server_metadata)
        server_digest = server.get("digest")
        if server.get("version") != args.release_version or not isinstance(
            server_digest, str
        ):
            raise ValueError("server metadata does not match the release")
        server_sha256 = server_digest.removeprefix("sha256:")
        if SHA256.fullmatch(server_sha256) is None:
            raise ValueError("server image digest is invalid")

        inventory_labels = {"server", "application"} | {
            f"{component}-{target}"
            for component in ("node", "proxy")
            for target in TARGETS
        }
        sboms = labeled_paths(args.sbom, "sbom", inventory_labels)
        provenance = labeled_paths(args.provenance, "provenance", inventory_labels)
        validate_community_signing(
            args.community_signing,
            str(device_component["version"]),
            application_sha256,
        )
        validate_automation(args.automation_evidence, args.distribution_version)
        validate_risk_acceptance(
            args.risk_acceptance, args.distribution_version, v2_enabled
        )

        v2_evidence_sha256 = None
        if v2_enabled:
            target = str(args.computer_use_v2_target)
            v2_evidence_sha256 = validate_v2_evidence(
                args.computer_use_v2_evidence,
                args.computer_use_v2_evidence_archive,
                target,
                args.distribution_version,
                {
                    "server": server_sha256,
                    "node": node_digests[target],
                    "application": application_sha256,
                    "proxy": proxy_digests[target],
                },
                issued_at_value,
            )

        args.output_directory.mkdir(mode=0o700, parents=True, exist_ok=False)
        sbom_inventory = args.output_directory / "sbom-inventory.json"
        provenance_inventory = args.output_directory / "provenance-inventory.json"
        write_new(
            sbom_inventory,
            canonical({label: digest(path) for label, path in sorted(sboms.items())}),
        )
        write_new(
            provenance_inventory,
            canonical(
                {label: digest(path) for label, path in sorted(provenance.items())}
            ),
        )
        if v2_enabled:
            copied_record_digest = copy_new(
                args.computer_use_v2_evidence,
                args.output_directory / "community-computer-use-v2-evidence.json",
            )
            copied_archive_digest = copy_new(
                args.computer_use_v2_evidence_archive,
                args.output_directory / "community-computer-use-v2.evidence.tar.gz",
            )
            if (
                copied_record_digest != v2_evidence_sha256
                or copied_archive_digest
                != load_object(args.computer_use_v2_evidence)["evidence_sha256"]
            ):
                raise ValueError(
                    "Community Computer Use v2 evidence changed during assembly"
                )
        automation_sha256 = digest(args.automation_evidence)
        signing_sha256 = digest(args.community_signing)
        risk_sha256 = digest(args.risk_acceptance)
        draft = {
            "schema_version": 8,
            "release_profile": "community-local-trust",
            "production_ready": True,
            "apple_notarized": False,
            "public_distribution": False,
            "manual_trust_required": True,
            "release_version": args.release_version,
            "issued_at": issued_at,
            "distribution_version": args.distribution_version,
            "release_manifest_sha256": release_manifest_sha256(args.release_manifest),
            "components": components,
            "server_sha256": server_sha256,
            "application_sha256": application_sha256,
            "node_artifacts_sha256": node_digests,
            "proxy_artifacts_sha256": proxy_digests,
            "sbom_sha256": digest(sbom_inventory),
            "provenance_sha256": digest(provenance_inventory),
            "security_tests_sha256": None,
            "security_review_sha256": None,
            "signing_notarization_sha256": signing_sha256,
            "outbound_policy_sha256": None,
            "local_claude_isolation_sha256": None,
            "stop_revocation_sha256": None,
            "compatibility_sha256": None,
            "computer_use_v2_evidence_sha256": v2_evidence_sha256,
            "community_signing_sha256": signing_sha256,
            "automated_release_checks_sha256": automation_sha256,
            "risk_acceptance_sha256": risk_sha256,
            "ci_run_url": args.ci_run_url,
        }
        write_new(
            args.output_directory / "release-evidence-draft.json", canonical(draft)
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"community evidence assembly failed: {exc}\n")


if __name__ == "__main__":
    main()
