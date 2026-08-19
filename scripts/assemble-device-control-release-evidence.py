#!/usr/bin/env python3
"""Assemble an unsigned device-control release-evidence draft from exact files."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import stat
import tarfile
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Iterator
from urllib.parse import urlsplit

from release_manifest import load_release_manifest, release_manifest_sha256

_SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-.+][0-9A-Za-z.-]+)?$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_MAXIMUM_INPUT_BYTES = 256 * 1024 * 1024
_MAXIMUM_ARCHIVE_EXPANDED_BYTES = 512 * 1024 * 1024
_MAXIMUM_ARCHIVE_MEMBERS = 4_096
_MAXIMUM_EXTERNAL_GATE_AGE = timedelta(days=30)
_INVENTORY_LABELS = ("server", "node", "application", "proxy")
_PUBLIC_ACTIONS = {
    "double_click",
    "hold_key",
    "key",
    "left_click",
    "left_click_drag",
    "left_mouse_down",
    "left_mouse_up",
    "middle_click",
    "mouse_move",
    "right_click",
    "screenshot",
    "scroll",
    "triple_click",
    "type",
    "wait",
    "zoom",
}
_STOP_SCENARIOS = {
    "device_revocation",
    "escape_key",
    "executor_crash",
    "lease_expiry",
    "relay_disconnect",
    "screen_lock",
    "server_revocation",
}
_MACOS_SECURITY_SCENARIOS = {
    "application_control_levels",
    "clipboard_permission",
    "device_revoke",
    "display_hotplug",
    "drag_disconnect_release",
    "downgrade_rejected",
    "escape_global_stop",
    "escape_not_delivered_to_target",
    "fast_user_switch",
    "install_signed_app",
    "machine_lock_crash_release",
    "modifier_disconnect_release",
    "mouse_down_disconnect_release",
    "multi_display_negative_origin",
    "network_switch",
    "per_session_application_approval",
    "process_restart_after_tcc_change",
    "retina_scaling",
    "same_version_reinstall",
    "single_session_machine_lock",
    "sleep_wake",
    "tcc_accessibility_denied",
    "tcc_accessibility_first_grant",
    "tcc_accessibility_revoked",
    "tcc_screen_recording_denied",
    "tcc_screen_recording_first_grant",
    "tcc_screen_recording_revoked",
    "uninstall",
    "uninstall_permission_residue_absent",
    "unapproved_applications_hidden",
    "unapproved_applications_restored",
    "unapproved_windows_excluded_from_capture",
    "upgrade_signed_app",
    "window_move_between_displays",
}
_COVERAGE_MINIMUMS = {
    "admin_branches": 65.0,
    "admin_functions": 80.0,
    "admin_lines": 85.0,
    "admin_statements": 80.0,
    "cli_lines": 45.0,
    "device_rust_lines": 75.0,
    "device_swift_lines": 55.0,
    "node_statements": 45.0,
    "server_lines": 70.0,
}
_GATE_STATUS = {
    "security-tests": "passed",
    "security-review": "approved",
    "outbound-policy": "passed",
    "local-claude-isolation": "passed",
    "stop-revocation": "passed",
    "compatibility": "passed",
}
_GATE_NAMES = tuple(_GATE_STATUS)
_GATE_TOP_LEVEL_KEYS = {
    "artifacts",
    "collected_at",
    "details",
    "evidence_sha256",
    "gate",
    "method",
    "producer",
    "release_version",
    "schema_version",
    "status",
}


@contextmanager
def open_safe_file(path: Path) -> Iterator[BinaryIO]:
    """Open one bounded regular input through a single non-following descriptor."""

    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError(f"input is not a regular non-symlink file: {path}")
        if info.st_size <= 0 or info.st_size > _MAXIMUM_INPUT_BYTES:
            raise ValueError(f"input file size is invalid: {path}")
        with os.fdopen(descriptor, "rb") as source:
            descriptor = -1
            yield source
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def safe_file(path: Path) -> Path:
    """Validate that a path currently resolves to one bounded regular input file."""

    with open_safe_file(path):
        return path


def sha256(path: Path) -> str:
    """Calculate the lowercase SHA-256 digest of a validated input file."""

    digest = hashlib.sha256()
    with open_safe_file(path) as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    """Encode deterministic ASCII JSON terminated by one newline."""

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


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build a JSON object while rejecting duplicate member names."""

    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def load_json_object(path: Path, name: str) -> dict[str, Any]:
    """Load a validated JSON object with duplicate-key detection."""

    try:
        with open_safe_file(path) as source:
            value = json.load(source, object_pairs_hook=reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{name} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object")
    return value


def parse_timestamp(value: Any, name: str) -> datetime:
    """Parse a timezone-aware ISO 8601 timestamp."""

    if not isinstance(value, str):
        raise ValueError(f"{name} is not an ISO 8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} is not an ISO 8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must include a timezone")
    return parsed


def parse_labeled_paths(values: list[str], option: str) -> dict[str, Path]:
    """Parse exactly one LABEL=PATH entry for each release component."""

    paths: dict[str, Path] = {}
    for value in values:
        label, separator, raw_path = value.partition("=")
        if not separator or label not in _INVENTORY_LABELS or label in paths:
            raise ValueError(f"invalid {option} entry: {value}")
        paths[label] = safe_file(Path(raw_path))
    if tuple(sorted(paths)) != tuple(sorted(_INVENTORY_LABELS)):
        raise ValueError(f"{option} must include server, node, application, and proxy")
    return paths


def parse_gate_evidence_paths(values: list[str]) -> dict[str, Path]:
    """Parse exactly one raw evidence archive for every external release gate."""

    paths: dict[str, Path] = {}
    for value in values:
        gate, separator, raw_path = value.partition("=")
        if not separator or gate not in _GATE_NAMES or gate in paths:
            raise ValueError(f"invalid gate-evidence entry: {value}")
        paths[gate] = safe_file(Path(raw_path))
    if set(paths) != set(_GATE_NAMES):
        raise ValueError("gate-evidence must include every external release gate")
    return paths


def validate_evidence_archive(
    path: Path, gate: str, expected_report_digest: str | None = None
) -> None:
    """Validate a bounded gzip tar archive and an optional contained report digest."""

    names: set[str] = set()
    member_digests: set[str] = set()
    regular_files = 0
    expanded_bytes = 0
    try:
        with open_safe_file(path) as archive_source:
            with tarfile.open(fileobj=archive_source, mode="r:gz") as archive:
                for count, member in enumerate(archive, start=1):
                    if count > _MAXIMUM_ARCHIVE_MEMBERS:
                        raise ValueError(f"{gate} evidence archive has too many members")
                    member_path = PurePosixPath(member.name)
                    canonical_name = member_path.as_posix()
                    archived_name = member.name.rstrip("/") if member.isdir() else member.name
                    if (
                        not member.name
                        or "\\" in member.name
                        or member_path.is_absolute()
                        or any(part in ("", ".", "..") for part in member_path.parts)
                        or archived_name != canonical_name
                        or member.name in names
                    ):
                        raise ValueError(f"{gate} evidence archive member path is invalid")
                    names.add(member.name)
                    if member.isdir():
                        continue
                    if not member.isfile():
                        raise ValueError(f"{gate} evidence archive member type is invalid")
                    if member.size < 0:
                        raise ValueError(f"{gate} evidence archive member size is invalid")
                    regular_files += 1
                    expanded_bytes += member.size
                    if expanded_bytes > _MAXIMUM_ARCHIVE_EXPANDED_BYTES:
                        raise ValueError(f"{gate} evidence archive expands beyond the limit")
                    source = archive.extractfile(member)
                    if source is None:
                        raise ValueError(f"{gate} evidence archive member cannot be read")
                    digest = hashlib.sha256()
                    bytes_read = 0
                    with source:
                        while chunk := source.read(1024 * 1024):
                            bytes_read += len(chunk)
                            digest.update(chunk)
                    if bytes_read != member.size:
                        raise ValueError(f"{gate} evidence archive member is truncated")
                    member_digests.add(digest.hexdigest())
    except (OSError, tarfile.TarError) as exc:
        raise ValueError(f"{gate} evidence archive is not a valid gzip tar") from exc
    if regular_files == 0 or expanded_bytes == 0:
        raise ValueError(f"{gate} evidence archive contains no report data")
    if expected_report_digest is not None and expected_report_digest not in member_digests:
        raise ValueError(f"{gate} report digest is not present in the evidence archive")


def load_server_metadata(path: Path, version: str) -> tuple[dict[str, Any], str]:
    """Load the server release metadata and return its immutable image digest."""

    value = load_json_object(path, "server metadata")
    if value.get("version") != version:
        raise ValueError("server metadata version does not match the release")
    digest = value.get("digest")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise ValueError("server metadata does not contain an OCI SHA-256 digest")
    raw_digest = digest.removeprefix("sha256:")
    if not _SHA256.fullmatch(raw_digest):
        raise ValueError("server OCI digest is invalid")
    return value, raw_digest


def require_exact_keys(value: dict[str, Any], keys: set[str], name: str) -> None:
    """Require a JSON object to contain exactly the expected member names."""

    if set(value) != keys:
        raise ValueError(f"{name} fields are invalid")


def require_text(value: Any, name: str, maximum: int = 500) -> str:
    """Require bounded non-empty text without surrounding whitespace."""

    if not isinstance(value, str) or not value or value != value.strip() or len(value) > maximum:
        raise ValueError(f"{name} must be bounded non-empty text")
    return value


def require_nonnegative_integer(value: Any, name: str) -> int:
    """Require a nonnegative integer that is not a boolean."""

    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return value


def require_percentage(value: Any, name: str) -> float:
    """Require a finite JSON percentage in the inclusive zero-to-100 range."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a percentage")
    percentage = float(value)
    if not math.isfinite(percentage) or not 0 <= percentage <= 100:
        raise ValueError(f"{name} must be a percentage")
    return percentage


def require_https_url(value: Any, name: str) -> str:
    """Require a bounded HTTPS URL without embedded credentials."""

    text = require_text(value, name, maximum=2_048)
    parsed = urlsplit(text)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError(f"{name} must be an HTTPS URL without credentials")
    return text


def validate_security_tests(details: dict[str, Any]) -> None:
    """Validate automated and signed-install security-test results."""

    require_exact_keys(
        details,
        {
            "application_signature_verified",
            "coverage",
            "coverage_thresholds_passed",
            "computer_use_v2",
            "cross_tenant_e2e_passed",
            "dedicated_macos_test_host",
            "failed",
            "macos_permissions_passed",
            "macos_scenarios",
            "notarization_ticket_verified",
            "passed",
            "protocol_fuzz_seconds",
            "team_identifier",
            "test_run_url",
        },
        "security-tests details",
    )
    require_https_url(details["test_run_url"], "security-tests test_run_url")
    team_identifier = require_text(
        details["team_identifier"], "security-tests team_identifier", maximum=10
    )
    if not re.fullmatch(r"[A-Z0-9]{10}", team_identifier):
        raise ValueError("security-tests team identifier is invalid")
    if require_nonnegative_integer(details["passed"], "security-tests passed") == 0:
        raise ValueError("security-tests must contain at least one passing test")
    if require_nonnegative_integer(details["failed"], "security-tests failed") != 0:
        raise ValueError("security-tests contains failures")
    if require_nonnegative_integer(
        details["protocol_fuzz_seconds"], "security-tests protocol_fuzz_seconds"
    ) < 60:
        raise ValueError("security-tests protocol fuzzing is too short")
    coverage = details["coverage"]
    if not isinstance(coverage, dict) or set(coverage) != set(_COVERAGE_MINIMUMS):
        raise ValueError("security-tests coverage results are incomplete")
    for component, configured_minimum in _COVERAGE_MINIMUMS.items():
        result = coverage[component]
        if not isinstance(result, dict):
            raise ValueError(f"security-tests {component} coverage result is invalid")
        require_exact_keys(result, {"actual", "minimum"}, f"security-tests {component}")
        actual = require_percentage(result["actual"], f"security-tests {component} actual")
        minimum = require_percentage(result["minimum"], f"security-tests {component} minimum")
        if minimum < configured_minimum or actual < minimum:
            raise ValueError(f"security-tests {component} coverage threshold was not met")
    macos_scenarios = details["macos_scenarios"]
    if not isinstance(macos_scenarios, dict) or set(macos_scenarios) != _MACOS_SECURITY_SCENARIOS:
        raise ValueError("security-tests macOS scenarios are incomplete")
    for scenario, passed in macos_scenarios.items():
        if passed is not True:
            raise ValueError(f"security-tests macOS scenario {scenario} must be true")
    for field in (
        "application_signature_verified",
        "coverage_thresholds_passed",
        "cross_tenant_e2e_passed",
        "dedicated_macos_test_host",
        "macos_permissions_passed",
        "notarization_ticket_verified",
    ):
        if details[field] is not True:
            raise ValueError(f"security-tests {field} must be true")
    validate_computer_use_v2(details["computer_use_v2"])


def validate_computer_use_v2(value: Any) -> None:
    """Validate the release-bound Computer Use v2 production acceptance report."""

    if not isinstance(value, dict):
        raise ValueError("security-tests Computer Use v2 result must be an object")
    true_assertions = {
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
    }
    false_assertions = {
        "sensitive_telemetry_detected",
        "success_rate_regressed",
    }
    metric_fields = {
        "action_latency_p95_ms",
        "coordinate_fallback_percent",
        "model_visible_image_reduction_percent",
        "report_sha256",
        "settle_latency_p95_ms",
        "wrong_target_count",
    }
    require_exact_keys(
        value,
        true_assertions | false_assertions | metric_fields,
        "security-tests Computer Use v2",
    )
    for field in true_assertions:
        if value[field] is not True:
            raise ValueError(f"security-tests Computer Use v2 {field} must be true")
    for field in false_assertions:
        if value[field] is not False:
            raise ValueError(f"security-tests Computer Use v2 {field} must be false")
    report_digest = value["report_sha256"]
    if not isinstance(report_digest, str) or not _SHA256.fullmatch(report_digest):
        raise ValueError("security-tests Computer Use v2 report digest is invalid")
    if require_nonnegative_integer(
        value["wrong_target_count"], "security-tests Computer Use v2 wrong_target_count"
    ) != 0:
        raise ValueError("security-tests Computer Use v2 contains wrong-target actions")
    image_reduction = require_percentage(
        value["model_visible_image_reduction_percent"],
        "security-tests Computer Use v2 model_visible_image_reduction_percent",
    )
    if image_reduction < 70:
        raise ValueError("security-tests Computer Use v2 image reduction is below target")
    action_latency = require_nonnegative_integer(
        value["action_latency_p95_ms"],
        "security-tests Computer Use v2 action_latency_p95_ms",
    )
    if action_latency > 1_000:
        raise ValueError("security-tests Computer Use v2 action latency exceeds target")
    settle_latency = require_nonnegative_integer(
        value["settle_latency_p95_ms"],
        "security-tests Computer Use v2 settle_latency_p95_ms",
    )
    if settle_latency > 5_000:
        raise ValueError("security-tests Computer Use v2 settle latency exceeds target")
    coordinate_fallback = require_percentage(
        value["coordinate_fallback_percent"],
        "security-tests Computer Use v2 coordinate_fallback_percent",
    )
    if coordinate_fallback >= 20:
        raise ValueError("security-tests Computer Use v2 coordinate fallback exceeds target")


def validate_security_review(details: dict[str, Any]) -> None:
    """Validate independent security-review approval and retest results."""

    require_exact_keys(
        details,
        {
            "critical_open",
            "high_open",
            "independence_confirmed",
            "report_sha256",
            "report_signature_identity",
            "report_signature_verified",
            "retest_complete",
            "reviewed_components",
            "reviewer",
        },
        "security-review details",
    )
    require_text(details["reviewer"], "security-review reviewer", maximum=200)
    require_text(
        details["report_signature_identity"],
        "security-review report_signature_identity",
        maximum=500,
    )
    report_digest = details["report_sha256"]
    if not isinstance(report_digest, str) or not _SHA256.fullmatch(report_digest):
        raise ValueError("security-review report digest is invalid")
    reviewed_components = details["reviewed_components"]
    if (
        not isinstance(reviewed_components, list)
        or not all(isinstance(item, str) for item in reviewed_components)
        or len(reviewed_components) != len(_INVENTORY_LABELS) + 1
        or set(reviewed_components) != {*_INVENTORY_LABELS, "release-evidence"}
    ):
        raise ValueError("security-review scope is incomplete")
    if require_nonnegative_integer(details["critical_open"], "security-review critical_open"):
        raise ValueError("security-review has open critical findings")
    if require_nonnegative_integer(details["high_open"], "security-review high_open"):
        raise ValueError("security-review has open high findings")
    for field in (
        "independence_confirmed",
        "report_signature_verified",
        "retest_complete",
    ):
        if details[field] is not True:
            raise ValueError(f"security-review {field} must be true")


def validate_outbound_policy(details: dict[str, Any]) -> None:
    """Validate active signature-bound outbound-policy probe results."""

    require_exact_keys(
        details,
        {
            "active",
            "allowed_destinations",
            "allowed_probe_succeeded",
            "anthropic_probe_blocked",
            "attestor_mach_service",
            "attestor_public_key_sha256",
            "broker_bundle_identifier",
            "challenge_bound_probe",
            "network_extension_enforced",
            "policy_identifier",
            "team_identifier",
            "unauthorized_probe_blocked",
        },
        "outbound-policy details",
    )
    require_text(details["policy_identifier"], "outbound-policy policy_identifier", maximum=200)
    attestor_mach_service = require_text(
        details["attestor_mach_service"], "outbound-policy attestor_mach_service", maximum=255
    )
    if not re.fullmatch(r"[A-Za-z0-9.-]{1,255}", attestor_mach_service):
        raise ValueError("outbound-policy attestor mach service is invalid")
    if details["broker_bundle_identifier"] != "dev.agentremote.device.network-broker":
        raise ValueError("outbound-policy broker bundle identifier is invalid")
    public_key_digest = details["attestor_public_key_sha256"]
    if not isinstance(public_key_digest, str) or not _SHA256.fullmatch(public_key_digest):
        raise ValueError("outbound-policy attestor public key digest is invalid")
    team_identifier = require_text(
        details["team_identifier"], "outbound-policy team_identifier", maximum=10
    )
    if not re.fullmatch(r"[A-Z0-9]{10}", team_identifier):
        raise ValueError("outbound-policy team identifier is invalid")
    destinations = details["allowed_destinations"]
    if not isinstance(destinations, list) or not destinations:
        raise ValueError("outbound-policy allowed destinations are missing")
    for destination in destinations:
        url = require_https_url(destination, "outbound-policy destination")
        hostname = urlsplit(url).hostname or ""
        if "anthropic" in hostname.lower():
            raise ValueError("outbound-policy must not allow Anthropic destinations")
    for field in (
        "active",
        "allowed_probe_succeeded",
        "anthropic_probe_blocked",
        "challenge_bound_probe",
        "network_extension_enforced",
        "unauthorized_probe_blocked",
    ):
        if details[field] is not True:
            raise ValueError(f"outbound-policy {field} must be true")


def validate_local_claude_isolation(details: dict[str, Any]) -> None:
    """Validate runtime file and network isolation observations."""

    require_exact_keys(
        details,
        {
            "anthropic_connections",
            "application_process_identity_verified",
            "claude_paths_accessed",
            "file_sensor_active",
            "local_claude_installed",
            "local_claude_logged_in",
            "network_sensor_active",
            "observation_seconds",
            "sensor_output_complete",
            "team_identifier",
        },
        "local-claude-isolation details",
    )
    if require_nonnegative_integer(
        details["observation_seconds"], "local-claude-isolation observation_seconds"
    ) < 60:
        raise ValueError("local-claude-isolation observation is too short")
    if details["local_claude_installed"] is not True or details["local_claude_logged_in"] is not True:
        raise ValueError("local-claude-isolation was not tested with a logged-in local Claude")
    team_identifier = require_text(
        details["team_identifier"], "local-claude-isolation team_identifier", maximum=10
    )
    if not re.fullmatch(r"[A-Z0-9]{10}", team_identifier):
        raise ValueError("local-claude-isolation team identifier is invalid")
    for field in (
        "application_process_identity_verified",
        "file_sensor_active",
        "network_sensor_active",
        "sensor_output_complete",
    ):
        if details[field] is not True:
            raise ValueError(f"local-claude-isolation {field} must be true")
    if require_nonnegative_integer(
        details["claude_paths_accessed"], "local-claude-isolation claude_paths_accessed"
    ) != 0:
        raise ValueError("local-claude-isolation observed Claude path access")
    if require_nonnegative_integer(
        details["anthropic_connections"], "local-claude-isolation anthropic_connections"
    ) != 0:
        raise ValueError("local-claude-isolation observed Anthropic connections")


def validate_stop_revocation(details: dict[str, Any]) -> None:
    """Validate global-stop, revocation, and fail-closed drill results."""

    require_exact_keys(
        details,
        {"failed", "permission_residue", "scenarios", "unconfirmed_action_replayed"},
        "stop-revocation details",
    )
    scenarios = details["scenarios"]
    if (
        not isinstance(scenarios, list)
        or not all(isinstance(item, str) for item in scenarios)
        or len(scenarios) != len(_STOP_SCENARIOS)
        or set(scenarios) != _STOP_SCENARIOS
    ):
        raise ValueError("stop-revocation scenarios are incomplete")
    if require_nonnegative_integer(details["failed"], "stop-revocation failed") != 0:
        raise ValueError("stop-revocation contains failures")
    if details["permission_residue"] is not False:
        raise ValueError("stop-revocation found permission residue")
    if details["unconfirmed_action_replayed"] is not False:
        raise ValueError("stop-revocation replayed an unconfirmed action")


def validate_compatibility(details: dict[str, Any]) -> None:
    """Validate current Claude Code and MCP compatibility results."""

    require_exact_keys(
        details,
        {
            "claude_code_version",
            "failed",
            "long_sequence_completed",
            "managed_mcp_configuration_verified",
            "mcp_image_results_verified",
            "mcp_protocol_version",
            "public_actions",
            "test_run_url",
            "turn_stop_observed",
        },
        "compatibility details",
    )
    require_text(details["claude_code_version"], "compatibility claude_code_version", maximum=100)
    require_text(details["mcp_protocol_version"], "compatibility mcp_protocol_version", maximum=100)
    require_https_url(details["test_run_url"], "compatibility test_run_url")
    actions = details["public_actions"]
    if (
        not isinstance(actions, list)
        or not all(isinstance(item, str) for item in actions)
        or len(actions) != len(_PUBLIC_ACTIONS)
        or set(actions) != _PUBLIC_ACTIONS
    ):
        raise ValueError("compatibility public actions do not match the release contract")
    if require_nonnegative_integer(details["failed"], "compatibility failed") != 0:
        raise ValueError("compatibility contains failures")
    for field in (
        "long_sequence_completed",
        "managed_mcp_configuration_verified",
        "mcp_image_results_verified",
        "turn_stop_observed",
    ):
        if details[field] is not True:
            raise ValueError(f"compatibility {field} must be true")


_GATE_VALIDATORS = {
    "security-tests": validate_security_tests,
    "security-review": validate_security_review,
    "outbound-policy": validate_outbound_policy,
    "local-claude-isolation": validate_local_claude_isolation,
    "stop-revocation": validate_stop_revocation,
    "compatibility": validate_compatibility,
}


def validate_external_gate(
    path: Path,
    evidence_path: Path,
    gate: str,
    version: str,
    artifacts: dict[str, str],
    issued_at: datetime,
) -> None:
    """Validate one gate-specific record and its exact artifact bindings."""

    value = load_json_object(path, gate)
    require_exact_keys(value, _GATE_TOP_LEVEL_KEYS, gate)
    if (
        isinstance(value["schema_version"], bool)
        or value["schema_version"] != 1
        or value["release_version"] != version
    ):
        raise ValueError(f"{gate} schema or release version is invalid")
    if value["gate"] != gate or value["status"] != _GATE_STATUS[gate]:
        raise ValueError(f"{gate} identity or status is invalid")
    if value["artifacts"] != artifacts:
        raise ValueError(f"{gate} is not bound to the exact release artifacts")
    evidence_digest = value["evidence_sha256"]
    if not isinstance(evidence_digest, str) or not _SHA256.fullmatch(evidence_digest):
        raise ValueError(f"{gate} evidence digest is invalid")
    if evidence_digest != sha256(evidence_path):
        raise ValueError(f"{gate} raw evidence digest does not match")
    collected_at = parse_timestamp(value["collected_at"], f"{gate} collected_at")
    if collected_at > issued_at:
        raise ValueError(f"{gate} was collected after manifest issuance")
    if collected_at < issued_at - _MAXIMUM_EXTERNAL_GATE_AGE:
        raise ValueError(f"{gate} evidence is older than 30 days")
    require_text(value["producer"], f"{gate} producer", maximum=200)
    require_text(value["method"], f"{gate} method", maximum=500)
    details = value["details"]
    if not isinstance(details, dict):
        raise ValueError(f"{gate} details must be an object")
    _GATE_VALIDATORS[gate](details)


def validate_notarization(path: Path, version: str, application_digest: str) -> dict[str, Any]:
    """Validate release-bound Apple signing and notarization evidence."""

    value = load_json_object(path, "notarization evidence")
    require_exact_keys(
        value,
        {
            "application_sha256",
            "artifact_signature_verified",
            "attestor_mach_service",
            "attestor_public_key_sha256",
            "broker_bundle_identifier",
            "bundle_identifier",
            "gatekeeper_assessed",
            "hardened_runtime",
            "notarization_status",
            "notarization_submission_id",
            "outbound_policy_identifier",
            "release_version",
            "schema_version",
            "stapler_validated",
            "status",
            "team_identifier",
        },
        "notarization evidence",
    )
    if (
        isinstance(value["schema_version"], bool)
        or value["schema_version"] != 1
        or value["release_version"] != version
        or value["status"] != "passed"
        or value["application_sha256"] != application_digest
        or value["notarization_status"] != "Accepted"
    ):
        raise ValueError("notarization evidence is not accepted or release-bound")
    if value["bundle_identifier"] != "dev.agentremote.device":
        raise ValueError("notarization bundle identifier is invalid")
    if value["broker_bundle_identifier"] != "dev.agentremote.device.network-broker":
        raise ValueError("notarization broker bundle identifier is invalid")
    require_text(
        value["outbound_policy_identifier"],
        "notarization outbound policy identifier",
        maximum=200,
    )
    attestor_mach_service = require_text(
        value["attestor_mach_service"], "notarization attestor mach service", maximum=255
    )
    if not re.fullmatch(r"[A-Za-z0-9.-]{1,255}", attestor_mach_service):
        raise ValueError("notarization attestor mach service is invalid")
    public_key_digest = value["attestor_public_key_sha256"]
    if not isinstance(public_key_digest, str) or not _SHA256.fullmatch(public_key_digest):
        raise ValueError("notarization attestor public key digest is invalid")
    team_identifier = value["team_identifier"]
    if not isinstance(team_identifier, str) or not re.fullmatch(r"[A-Z0-9]{10}", team_identifier):
        raise ValueError("notarization team identifier is invalid")
    for field in (
        "artifact_signature_verified",
        "gatekeeper_assessed",
        "hardened_runtime",
        "stapler_validated",
    ):
        if value[field] is not True:
            raise ValueError(f"notarization {field} must be true")
    submission_id = value["notarization_submission_id"]
    if not isinstance(submission_id, str) or not re.fullmatch(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        submission_id,
    ):
        raise ValueError("notarization submission identifier is invalid")
    return value


def validate_outbound_policy_binding(
    details: dict[str, Any], notarization: dict[str, Any]
) -> None:
    """Require runtime policy evidence to match the policy pinned in the signed application."""

    pairs = (
        ("team_identifier", "team_identifier"),
        ("broker_bundle_identifier", "broker_bundle_identifier"),
        ("policy_identifier", "outbound_policy_identifier"),
        ("attestor_mach_service", "attestor_mach_service"),
        ("attestor_public_key_sha256", "attestor_public_key_sha256"),
    )
    if any(details[gate_key] != notarization[app_key] for gate_key, app_key in pairs):
        raise ValueError("outbound-policy evidence does not match the signed application policy")


def validate_signed_macos_gate_bindings(
    external_gates: dict[str, Path], notarization: dict[str, Any]
) -> None:
    """Bind signed-Mac runtime gates to the notarized application's Team ID."""

    for gate in ("security-tests", "local-claude-isolation"):
        value = load_json_object(external_gates[gate], gate)
        if value["details"]["team_identifier"] != notarization["team_identifier"]:
            raise ValueError(f"{gate} does not match the signed application identity")


def inventory(version: str, paths: dict[str, Path]) -> dict[str, object]:
    """Create a deterministic inventory for one evidence category."""

    return {
        "schema_version": 1,
        "release_version": version,
        "files": [
            {
                "component": label,
                "filename": paths[label].name,
                "sha256": sha256(paths[label]),
            }
            for label in _INVENTORY_LABELS
        ],
    }


def write_new(path: Path, data: bytes) -> None:
    """Create an owner-only output without overwriting an existing path."""

    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as output:
        output.write(data)
        output.flush()
        os.fsync(output.fileno())


def copy_new(source: Path, destination: Path) -> None:
    """Copy one validated evidence input to a new owner-only output file."""

    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with open_safe_file(source) as input_file, os.fdopen(descriptor, "wb") as output_file:
            descriptor = -1
            shutil.copyfileobj(input_file, output_file, length=1024 * 1024)
            output_file.flush()
            os.fsync(output_file.fileno())
    except Exception:
        if descriptor >= 0:
            os.close(descriptor)
        destination.unlink(missing_ok=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--distribution-version", required=True)
    parser.add_argument("--release-manifest", type=Path, required=True)
    parser.add_argument("--server-metadata", type=Path, required=True)
    parser.add_argument("--node-artifact", type=Path, required=True)
    parser.add_argument("--application-artifact", type=Path, required=True)
    parser.add_argument("--proxy-artifact", type=Path, required=True)
    parser.add_argument("--sbom", action="append", default=[], metavar="LABEL=PATH")
    parser.add_argument("--provenance", action="append", default=[], metavar="LABEL=PATH")
    parser.add_argument("--security-tests", type=Path, required=True)
    parser.add_argument("--security-review", type=Path, required=True)
    parser.add_argument("--signing-notarization", type=Path, required=True)
    parser.add_argument("--outbound-policy", type=Path, required=True)
    parser.add_argument("--local-claude-isolation", type=Path, required=True)
    parser.add_argument("--stop-revocation", type=Path, required=True)
    parser.add_argument("--compatibility", type=Path, required=True)
    parser.add_argument(
        "--gate-evidence", action="append", default=[], metavar="GATE=PATH"
    )
    parser.add_argument("--ci-run-url", required=True)
    parser.add_argument("--issued-at", required=True)
    parser.add_argument("--expires-at", required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    return parser


def main() -> None:
    """Validate all evidence inputs and write an unsigned release draft."""

    args = build_parser().parse_args()
    try:
        version = args.release_version
        if not _SEMVER.fullmatch(version):
            raise ValueError("release version is not semantic")
        manifest = load_release_manifest(args.release_manifest)
        components = manifest["components"]
        assert isinstance(components, dict)
        server_component = components["agent-remote-server"]
        device_component = components["agent-remote-device"]
        assert isinstance(server_component, dict)
        assert isinstance(device_component, dict)
        if manifest["distribution_version"] != args.distribution_version:
            raise ValueError("distribution version does not match the release manifest")
        if server_component["version"] != version:
            raise ValueError("server version does not match the release manifest")
        device_version = str(device_component["version"])
        if not args.ci_run_url.startswith("https://github.com/"):
            raise ValueError("CI run URL must be a GitHub HTTPS URL")
        issued_at = parse_timestamp(args.issued_at, "issued-at")
        expires_at = parse_timestamp(args.expires_at, "expires-at")
        if expires_at <= issued_at or expires_at > issued_at + timedelta(days=30):
            raise ValueError("evidence lifetime must be positive and no more than 30 days")

        _, server_digest = load_server_metadata(args.server_metadata, version)
        sbom_paths = parse_labeled_paths(args.sbom, "sbom")
        provenance_paths = parse_labeled_paths(args.provenance, "provenance")
        artifact_paths = {
            "node": safe_file(args.node_artifact),
            "application": safe_file(args.application_artifact),
            "proxy": safe_file(args.proxy_artifact),
        }
        artifact_digests = {
            "server": server_digest,
            "node": sha256(artifact_paths["node"]),
            "application": sha256(artifact_paths["application"]),
            "proxy": sha256(artifact_paths["proxy"]),
        }
        external_gates = {
            "security-tests": safe_file(args.security_tests),
            "security-review": safe_file(args.security_review),
            "outbound-policy": safe_file(args.outbound_policy),
            "local-claude-isolation": safe_file(args.local_claude_isolation),
            "stop-revocation": safe_file(args.stop_revocation),
            "compatibility": safe_file(args.compatibility),
        }
        gate_evidence_paths = parse_gate_evidence_paths(args.gate_evidence)
        for gate, path in external_gates.items():
            validate_external_gate(
                path,
                gate_evidence_paths[gate],
                gate,
                args.distribution_version,
                artifact_digests,
                issued_at,
            )
            expected_report_digest = None
            if gate == "security-review":
                review = load_json_object(path, gate)
                expected_report_digest = review["details"]["report_sha256"]
            elif gate == "security-tests":
                security_tests = load_json_object(path, gate)
                expected_report_digest = security_tests["details"]["computer_use_v2"][
                    "report_sha256"
                ]
            validate_evidence_archive(
                gate_evidence_paths[gate], gate, expected_report_digest
            )
        notarization = validate_notarization(
            args.signing_notarization,
            device_version,
            artifact_digests["application"],
        )
        outbound_policy = load_json_object(external_gates["outbound-policy"], "outbound-policy")
        validate_outbound_policy_binding(outbound_policy["details"], notarization)
        validate_signed_macos_gate_bindings(external_gates, notarization)
        gate_paths = {
            "security_tests_sha256": external_gates["security-tests"],
            "computer_use_v2_evidence_sha256": external_gates["security-tests"],
            "security_review_sha256": external_gates["security-review"],
            "signing_notarization_sha256": safe_file(args.signing_notarization),
            "outbound_policy_sha256": external_gates["outbound-policy"],
            "local_claude_isolation_sha256": external_gates["local-claude-isolation"],
            "stop_revocation_sha256": external_gates["stop-revocation"],
            "compatibility_sha256": external_gates["compatibility"],
        }

        output_directory: Path = args.output_directory
        output_directory.mkdir(mode=0o700, parents=False, exist_ok=False)
        written: list[Path] = []
        gates_directory: Path | None = None
        try:
            sbom_path = output_directory / "device-control-sbom-inventory.json"
            provenance_path = output_directory / "device-control-provenance-inventory.json"
            write_new(
                sbom_path,
                canonical_json(inventory(args.distribution_version, sbom_paths)),
            )
            written.append(sbom_path)
            write_new(
                provenance_path,
                canonical_json(
                    inventory(args.distribution_version, provenance_paths)
                ),
            )
            written.append(provenance_path)

            legacy_coordinated = (
                args.distribution_version == version
                and all(
                    isinstance(component, dict)
                    and component.get("version") == version
                    for component in components.values()
                )
            )
            draft: dict[str, object] = {
                "schema_version": 1 if legacy_coordinated else 7,
                "release_version": version,
                "issued_at": args.issued_at,
                "expires_at": args.expires_at,
                "server_sha256": server_digest,
                "node_sha256": artifact_digests["node"],
                "application_sha256": artifact_digests["application"],
                "proxy_sha256": artifact_digests["proxy"],
                "sbom_sha256": sha256(sbom_path),
                "provenance_sha256": sha256(provenance_path),
                "ci_run_url": args.ci_run_url,
            }
            if not legacy_coordinated:
                draft.update(
                    {
                        "distribution_version": args.distribution_version,
                        "release_manifest_sha256": release_manifest_sha256(
                            args.release_manifest
                        ),
                        "components": components,
                    }
                )
            draft.update({field: sha256(path) for field, path in gate_paths.items()})
            draft_path = output_directory / "release-evidence-draft.json"
            write_new(draft_path, canonical_json(draft))
            written.append(draft_path)

            gates_directory = output_directory / "gates"
            gates_directory.mkdir(mode=0o700)
            for gate in _GATE_NAMES:
                gate_record = gates_directory / f"{gate}.json"
                raw_evidence = gates_directory / f"{gate}.evidence.tar.gz"
                copy_new(external_gates[gate], gate_record)
                written.append(gate_record)
                copy_new(gate_evidence_paths[gate], raw_evidence)
                written.append(raw_evidence)

            checksums = "".join(
                f"{sha256(path)}  {path.relative_to(output_directory)}\n"
                for path in sorted(written)
            ).encode("ascii")
            write_new(output_directory / "SHA256SUMS", checksums)
        except Exception:
            for path in written:
                path.unlink(missing_ok=True)
            if gates_directory is not None:
                gates_directory.rmdir()
            (output_directory / "SHA256SUMS").unlink(missing_ok=True)
            output_directory.rmdir()
            raise
    except (OSError, ValueError) as exc:
        raise SystemExit(f"release evidence assembly failed: {exc}") from exc


if __name__ == "__main__":
    main()
