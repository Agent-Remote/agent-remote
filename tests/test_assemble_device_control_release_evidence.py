import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


SCRIPT = Path("scripts/assemble-device-control-release-evidence.py").resolve()
DIGEST = "a" * 64
LABELS = ("server", "node", "application", "proxy")
PUBLIC_ACTIONS = [
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
]
MACOS_SECURITY_SCENARIOS = [
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
]


def write(path: Path, value: str) -> Path:
    path.write_text(value, encoding="utf-8")
    return path


def write_evidence_archive(path: Path, name: str, content: bytes) -> Path:
    with tarfile.open(path, mode="w:gz") as archive:
        member = tarfile.TarInfo(name=name)
        member.size = len(content)
        archive.addfile(member, io.BytesIO(content))
    return path


def gate_details(name: str) -> dict[str, object]:
    if name == "security-tests":
        return {
            "application_signature_verified": True,
            "coverage": {
                "admin_branches": {"actual": 67.45, "minimum": 65},
                "admin_functions": {"actual": 82.85, "minimum": 80},
                "admin_lines": {"actual": 86.44, "minimum": 85},
                "admin_statements": {"actual": 83.66, "minimum": 80},
                "cli_lines": {"actual": 48.61, "minimum": 45},
                "device_rust_lines": {"actual": 82.78, "minimum": 75},
                "device_swift_lines": {"actual": 61.19, "minimum": 55},
                "node_statements": {"actual": 48.9, "minimum": 45},
                "server_lines": {"actual": 71.72, "minimum": 70},
            },
            "coverage_thresholds_passed": True,
            "cross_tenant_e2e_passed": True,
            "dedicated_macos_test_host": True,
            "failed": 0,
            "macos_permissions_passed": True,
            "macos_scenarios": {scenario: True for scenario in MACOS_SECURITY_SCENARIOS},
            "notarization_ticket_verified": True,
            "passed": 200,
            "protocol_fuzz_seconds": 60,
            "team_identifier": "AB12CD34EF",
            "test_run_url": "https://github.com/Agent-Remote/agent-remote/actions/runs/100",
        }
    if name == "security-review":
        return {
            "critical_open": 0,
            "high_open": 0,
            "independence_confirmed": True,
            "report_sha256": hashlib.sha256(b"raw-security-review").hexdigest(),
            "report_signature_identity": "reviewer@example.test",
            "report_signature_verified": True,
            "retest_complete": True,
            "reviewed_components": [
                "server",
                "node",
                "application",
                "proxy",
                "release-evidence",
            ],
            "reviewer": "Independent Security Review LLC",
        }
    if name == "outbound-policy":
        return {
            "active": True,
            "allowed_destinations": ["https://control.example.test", "https://node.example.test"],
            "allowed_probe_succeeded": True,
            "anthropic_probe_blocked": True,
            "attestor_mach_service": "dev.example.agent-remote-policy-attestor",
            "attestor_public_key_sha256": "d" * 64,
            "broker_bundle_identifier": "dev.agentremote.device.network-broker",
            "challenge_bound_probe": True,
            "network_extension_enforced": True,
            "policy_identifier": "com.example.agent-remote-egress",
            "team_identifier": "AB12CD34EF",
            "unauthorized_probe_blocked": True,
        }
    if name == "local-claude-isolation":
        return {
            "anthropic_connections": 0,
            "application_process_identity_verified": True,
            "claude_paths_accessed": 0,
            "file_sensor_active": True,
            "local_claude_installed": True,
            "local_claude_logged_in": True,
            "network_sensor_active": True,
            "observation_seconds": 300,
            "sensor_output_complete": True,
            "team_identifier": "AB12CD34EF",
        }
    if name == "stop-revocation":
        return {
            "failed": 0,
            "permission_residue": False,
            "scenarios": [
                "device_revocation",
                "escape_key",
                "executor_crash",
                "lease_expiry",
                "relay_disconnect",
                "screen_lock",
                "server_revocation",
            ],
            "unconfirmed_action_replayed": False,
        }
    if name == "compatibility":
        return {
            "claude_code_version": "1.2.3",
            "failed": 0,
            "long_sequence_completed": True,
            "managed_mcp_configuration_verified": True,
            "mcp_image_results_verified": True,
            "mcp_protocol_version": "2025-11-25",
            "public_actions": PUBLIC_ACTIONS,
            "test_run_url": "https://github.com/Agent-Remote/agent-remote/actions/runs/101",
            "turn_stop_observed": True,
        }
    raise AssertionError(f"unknown gate: {name}")


def write_gate(
    root: Path,
    name: str,
    artifacts: dict[str, str],
    evidence_digest: str,
) -> Path:
    value = {
        "artifacts": artifacts,
        "collected_at": "2026-07-30T23:00:00+00:00",
        "details": gate_details(name),
        "evidence_sha256": evidence_digest,
        "gate": name,
        "method": f"release-bound {name} validation",
        "producer": "production-device-release environment",
        "release_version": "1.2.3",
        "schema_version": 1,
        "status": "approved" if name == "security-review" else "passed",
    }
    return write(root / f"{name}.json", json.dumps(value, sort_keys=True))


def command(root: Path, output: Path) -> list[str]:
    server_metadata = write(
        root / "server.json",
        json.dumps({"version": "1.2.3", "digest": f"sha256:{DIGEST}"}),
    )
    node = write(root / "node.tar.gz", "node")
    application = write(root / "application.zip", "application")
    proxy = write(root / "proxy.tar.gz", "proxy")
    artifacts = {
        "server": DIGEST,
        "node": hashlib.sha256(b"node").hexdigest(),
        "application": hashlib.sha256(b"application").hexdigest(),
        "proxy": hashlib.sha256(b"proxy").hexdigest(),
    }
    arguments = [
        sys.executable,
        str(SCRIPT),
        "--release-version",
        "1.2.3",
        "--server-metadata",
        str(server_metadata),
        "--node-artifact",
        str(node),
        "--application-artifact",
        str(application),
        "--proxy-artifact",
        str(proxy),
    ]
    for option in ("sbom", "provenance"):
        for label in LABELS:
            path = write(root / f"{label}.{option}.json", f"{label}-{option}")
            arguments.extend((f"--{option}", f"{label}={path}"))
    gate_evidence: dict[str, Path] = {}
    for option in (
        "security-tests",
        "security-review",
        "outbound-policy",
        "local-claude-isolation",
        "stop-revocation",
        "compatibility",
    ):
        evidence_path = write_evidence_archive(
            root / f"{option}.evidence.tar.gz",
            "report.json",
            f"raw-{option}".encode(),
        )
        gate_evidence[option] = evidence_path
        path = write_gate(
            root,
            option,
            artifacts,
            hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
        )
        arguments.extend((f"--{option}", str(path)))
    for gate, evidence_path in gate_evidence.items():
        arguments.extend(("--gate-evidence", f"{gate}={evidence_path}"))
    notarization = write(
        root / "notarization.json",
        json.dumps(
            {
                "application_sha256": artifacts["application"],
                "artifact_signature_verified": True,
                "attestor_mach_service": "dev.example.agent-remote-policy-attestor",
                "attestor_public_key_sha256": "d" * 64,
                "broker_bundle_identifier": "dev.agentremote.device.network-broker",
                "bundle_identifier": "dev.agentremote.device",
                "gatekeeper_assessed": True,
                "hardened_runtime": True,
                "notarization_status": "Accepted",
                "notarization_submission_id": "12345678-1234-1234-1234-123456789abc",
                "outbound_policy_identifier": "com.example.agent-remote-egress",
                "release_version": "1.2.3",
                "schema_version": 1,
                "stapler_validated": True,
                "status": "passed",
                "team_identifier": "AB12CD34EF",
            }
        ),
    )
    arguments.extend(("--signing-notarization", str(notarization)))
    arguments.extend(
        (
            "--ci-run-url",
            "https://github.com/Agent-Remote/agent-remote/actions/runs/123",
            "--issued-at",
            "2026-07-31T00:00:00+00:00",
            "--expires-at",
            "2026-08-07T00:00:00+00:00",
            "--output-directory",
            str(output),
        )
    )
    return arguments


def test_assembler_writes_exact_artifact_and_inventory_digests() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        result = subprocess.run(command(root, output), capture_output=True, text=True)

        assert result.returncode == 0, result.stderr
        draft = json.loads((output / "release-evidence-draft.json").read_text())
        assert draft["server_sha256"] == DIGEST
        assert draft["node_sha256"] == hashlib.sha256(b"node").hexdigest()
        assert draft["application_sha256"] == hashlib.sha256(b"application").hexdigest()
        assert draft["proxy_sha256"] == hashlib.sha256(b"proxy").hexdigest()
        assert draft["sbom_sha256"] == hashlib.sha256(
            (output / "device-control-sbom-inventory.json").read_bytes()
        ).hexdigest()
        assert (output.stat().st_mode & 0o777) == 0o700
        assert (output / "release-evidence-draft.json").stat().st_mode & 0o777 == 0o600
        assert (output / "gates" / "security-tests.json").is_file()
        assert (output / "gates" / "security-tests.evidence.tar.gz").is_file()


def test_assembler_rejects_symlinks_and_existing_output() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        node_index = arguments.index("--node-artifact") + 1
        node_link = root / "node-link.tar.gz"
        node_link.symlink_to(Path(arguments[node_index]))
        arguments[node_index] = str(node_link)

        linked = subprocess.run(arguments, capture_output=True, text=True)

        assert linked.returncode != 0
        assert not output.exists()

        output.mkdir()
        existing = subprocess.run(command(root, output), capture_output=True, text=True)

        assert existing.returncode != 0
        assert output.is_dir()


def test_assembler_rejects_cross_artifact_gate_evidence() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        gate_path = Path(arguments[arguments.index("--security-review") + 1])
        gate = json.loads(gate_path.read_text())
        gate["artifacts"]["application"] = "c" * 64
        gate_path.write_text(json.dumps(gate), encoding="utf-8")

        result = subprocess.run(arguments, capture_output=True, text=True)

        assert result.returncode != 0
        assert "exact release artifacts" in result.stderr
        assert not output.exists()


def test_assembler_rejects_gate_specific_false_claims() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        policy_path = Path(arguments[arguments.index("--outbound-policy") + 1])
        policy = json.loads(policy_path.read_text())
        policy["details"]["allowed_destinations"].append("https://api.anthropic.com")
        policy_path.write_text(json.dumps(policy), encoding="utf-8")

        result = subprocess.run(arguments, capture_output=True, text=True)

        assert result.returncode != 0
        assert "must not allow Anthropic" in result.stderr
        assert not output.exists()


def test_assembler_requires_every_real_macos_security_scenario() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        gate_path = Path(arguments[arguments.index("--security-tests") + 1])
        gate = json.loads(gate_path.read_text())
        del gate["details"]["macos_scenarios"]["display_hotplug"]
        gate_path.write_text(json.dumps(gate), encoding="utf-8")

        missing = subprocess.run(arguments, capture_output=True, text=True)

        assert missing.returncode != 0
        assert "macOS scenarios are incomplete" in missing.stderr
        assert not output.exists()

        output = root / "second-output"
        arguments = command(root, output)
        gate_path = Path(arguments[arguments.index("--security-tests") + 1])
        gate = json.loads(gate_path.read_text())
        gate["details"]["macos_scenarios"]["downgrade_rejected"] = False
        gate_path.write_text(json.dumps(gate), encoding="utf-8")

        failed = subprocess.run(arguments, capture_output=True, text=True)

        assert failed.returncode != 0
        assert "macOS scenario downgrade_rejected must be true" in failed.stderr
        assert not output.exists()


def test_assembler_requires_each_repository_coverage_threshold() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        gate_path = Path(arguments[arguments.index("--security-tests") + 1])
        gate = json.loads(gate_path.read_text())
        gate["details"]["coverage"]["node_statements"]["actual"] = 44.99
        gate_path.write_text(json.dumps(gate), encoding="utf-8")

        result = subprocess.run(arguments, capture_output=True, text=True)

        assert result.returncode != 0
        assert "node_statements coverage threshold was not met" in result.stderr
        assert not output.exists()


def test_assembler_requires_observed_claude_code_compatibility_behaviors() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        gate_path = Path(arguments[arguments.index("--compatibility") + 1])
        gate = json.loads(gate_path.read_text())
        gate["details"]["turn_stop_observed"] = False
        gate_path.write_text(json.dumps(gate), encoding="utf-8")

        result = subprocess.run(arguments, capture_output=True, text=True)

        assert result.returncode != 0
        assert "compatibility turn_stop_observed must be true" in result.stderr
        assert not output.exists()


def test_assembler_requires_independent_signed_security_review_scope() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        gate_path = Path(arguments[arguments.index("--security-review") + 1])
        gate = json.loads(gate_path.read_text())
        gate["details"]["reviewed_components"].remove("release-evidence")
        gate_path.write_text(json.dumps(gate), encoding="utf-8")

        result = subprocess.run(arguments, capture_output=True, text=True)

        assert result.returncode != 0
        assert "security-review scope is incomplete" in result.stderr
        assert not output.exists()


def test_assembler_binds_security_review_report_to_raw_archive() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        gate_path = Path(arguments[arguments.index("--security-review") + 1])
        gate = json.loads(gate_path.read_text())
        gate["details"]["report_sha256"] = "e" * 64
        gate_path.write_text(json.dumps(gate), encoding="utf-8")

        result = subprocess.run(arguments, capture_output=True, text=True)

        assert result.returncode != 0
        assert "report digest is not present in the evidence archive" in result.stderr
        assert not output.exists()


def test_assembler_requires_complete_signed_macos_sensor_evidence() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        gate_path = Path(arguments[arguments.index("--local-claude-isolation") + 1])
        gate = json.loads(gate_path.read_text())
        gate["details"]["network_sensor_active"] = False
        gate_path.write_text(json.dumps(gate), encoding="utf-8")

        result = subprocess.run(arguments, capture_output=True, text=True)

        assert result.returncode != 0
        assert "local-claude-isolation network_sensor_active must be true" in result.stderr
        assert not output.exists()


def test_assembler_binds_runtime_tests_to_notarized_team_identity() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        gate_path = Path(arguments[arguments.index("--security-tests") + 1])
        gate = json.loads(gate_path.read_text())
        gate["details"]["team_identifier"] = "ZZ98YX76WV"
        gate_path.write_text(json.dumps(gate), encoding="utf-8")

        result = subprocess.run(arguments, capture_output=True, text=True)

        assert result.returncode != 0
        assert "security-tests does not match the signed application identity" in result.stderr
        assert not output.exists()


def test_assembler_rejects_policy_not_pinned_by_signed_application() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        policy_path = Path(arguments[arguments.index("--outbound-policy") + 1])
        policy = json.loads(policy_path.read_text())
        policy["details"]["attestor_public_key_sha256"] = "e" * 64
        policy_path.write_text(json.dumps(policy), encoding="utf-8")

        result = subprocess.run(arguments, capture_output=True, text=True)

        assert result.returncode != 0
        assert "does not match the signed application policy" in result.stderr
        assert not output.exists()


def test_assembler_rejects_raw_gate_evidence_digest_mismatch() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        gate_argument = next(
            value
            for index, value in enumerate(arguments)
            if arguments[index - 1] == "--gate-evidence"
            and value.startswith("security-tests=")
        )
        evidence_path = Path(gate_argument.partition("=")[2])
        evidence_path.write_text("tampered evidence", encoding="utf-8")

        result = subprocess.run(arguments, capture_output=True, text=True)

        assert result.returncode != 0
        assert "raw evidence digest does not match" in result.stderr
        assert not output.exists()


def test_assembler_rejects_unsafe_gate_evidence_archive() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        gate_argument = next(
            value
            for index, value in enumerate(arguments)
            if arguments[index - 1] == "--gate-evidence"
            and value.startswith("security-tests=")
        )
        evidence_path = Path(gate_argument.partition("=")[2])
        write_evidence_archive(evidence_path, "../outside.json", b"unsafe")
        gate_path = Path(arguments[arguments.index("--security-tests") + 1])
        gate = json.loads(gate_path.read_text())
        gate["evidence_sha256"] = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        gate_path.write_text(json.dumps(gate), encoding="utf-8")

        result = subprocess.run(arguments, capture_output=True, text=True)

        assert result.returncode != 0
        assert "archive member path is invalid" in result.stderr
        assert not output.exists()


def test_assembler_rejects_future_and_duplicate_key_evidence() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        compatibility_path = Path(arguments[arguments.index("--compatibility") + 1])
        compatibility = json.loads(compatibility_path.read_text())
        compatibility["collected_at"] = "2026-08-01T00:00:00+00:00"
        compatibility_path.write_text(json.dumps(compatibility), encoding="utf-8")

        future = subprocess.run(arguments, capture_output=True, text=True)

        assert future.returncode != 0
        assert "after manifest issuance" in future.stderr
        compatibility_path.write_text(
            '{"schema_version":1,"schema_version":1}', encoding="utf-8"
        )
        duplicate = subprocess.run(arguments, capture_output=True, text=True)

        assert duplicate.returncode != 0
        assert "duplicate JSON key" in duplicate.stderr


def test_assembler_rejects_external_gate_evidence_older_than_thirty_days() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        output = root / "output"
        arguments = command(root, output)
        gate_path = Path(arguments[arguments.index("--local-claude-isolation") + 1])
        gate = json.loads(gate_path.read_text())
        gate["collected_at"] = "2026-06-30T23:59:59+00:00"
        gate_path.write_text(json.dumps(gate), encoding="utf-8")

        result = subprocess.run(arguments, capture_output=True, text=True)

        assert result.returncode != 0
        assert "evidence is older than 30 days" in result.stderr
        assert not output.exists()


if __name__ == "__main__":
    test_assembler_writes_exact_artifact_and_inventory_digests()
    test_assembler_rejects_symlinks_and_existing_output()
    test_assembler_rejects_cross_artifact_gate_evidence()
    test_assembler_rejects_gate_specific_false_claims()
    test_assembler_requires_every_real_macos_security_scenario()
    test_assembler_requires_each_repository_coverage_threshold()
    test_assembler_requires_observed_claude_code_compatibility_behaviors()
    test_assembler_requires_independent_signed_security_review_scope()
    test_assembler_binds_security_review_report_to_raw_archive()
    test_assembler_requires_complete_signed_macos_sensor_evidence()
    test_assembler_binds_runtime_tests_to_notarized_team_identity()
    test_assembler_rejects_policy_not_pinned_by_signed_application()
    test_assembler_rejects_raw_gate_evidence_digest_mismatch()
    test_assembler_rejects_unsafe_gate_evidence_archive()
    test_assembler_rejects_future_and_duplicate_key_evidence()
    test_assembler_rejects_external_gate_evidence_older_than_thirty_days()
