import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

SCRIPT = Path("scripts/assemble-community-device-control-release-evidence.py")
VERSION = "1.2.3"
DISTRIBUTION_VERSION = "9.8.7"
DEVICE_VERSION = "5.6.7"
COMPONENT_VERSIONS = {
    "agent-remote-server": VERSION,
    "agent-remote-node": "2.3.4",
    "agent-remote-cli": "3.4.5",
    "agent-remote-admin-web": "4.5.6",
    "agent-remote-device": DEVICE_VERSION,
}
TARGETS = (
    "linux-amd64-glibc",
    "linux-arm64-glibc",
    "linux-amd64-musl",
    "linux-arm64-musl",
)


def write(path: Path, value: object) -> Path:
    if isinstance(value, (dict, list)):
        path.write_text(json.dumps(value), encoding="utf-8")
    else:
        path.write_text(str(value), encoding="utf-8")
    return path


def arguments(root: Path) -> tuple[list[str], Path]:
    manifest = write(
        root / "release-manifest.json",
        {
            "schema_version": 2,
            "distribution_version": DISTRIBUTION_VERSION,
            "components": {
                name: {
                    "repository": f"Agent-Remote/{name}",
                    "release_workflow": "release.yml",
                    "version": COMPONENT_VERSIONS[name],
                    "commit": "c" * 40,
                }
                for name in (
                    "agent-remote-server",
                    "agent-remote-node",
                    "agent-remote-cli",
                    "agent-remote-admin-web",
                    "agent-remote-device",
                )
            },
        },
    )
    application = write(root / "application.artifact", "application-artifact")
    node_artifacts = {
        target: write(root / f"node-{target}.artifact", f"node-{target}")
        for target in TARGETS
    }
    proxy_artifacts = {
        target: write(root / f"proxy-{target}.artifact", f"proxy-{target}")
        for target in TARGETS
    }
    application_sha256 = hashlib.sha256(application.read_bytes()).hexdigest()
    server = write(
        root / "server.json",
        {"version": VERSION, "digest": f"sha256:{'a' * 64}"},
    )
    signing = write(
        root / "community-signing.json",
        {
            "schema_version": 1,
            "release_version": DEVICE_VERSION,
            "profile": "community-local-trust",
            "production_ready": True,
            "apple_notarized": False,
            "public_distribution": False,
            "signing_type": "project-self-signed",
            "signer_certificate_sha1": "A" * 40,
            "signer_certificate_sha256": "b" * 64,
            "application_signature_verified": True,
            "nested_signatures_verified": True,
            "hardened_runtime": True,
            "outbound_policy": "application-enforced",
            "application_sha256": application_sha256,
            "bundle_identifier": "dev.agentremote.device",
            "broker_bundle_identifier": "dev.agentremote.device.network-broker",
        },
    )
    automation = write(
        root / "automation.json",
        {
            "schema_version": 1,
            "release_version": DISTRIBUTION_VERSION,
            "profile": "community-local-trust",
            "production_ready": True,
            "official_runners_only": True,
            "critical_high_vulnerabilities": 0,
            "checks": {
                "certified_composition": True,
                "protocol_tests": True,
                "cross_component_e2e": True,
                "fuzz": True,
                "stop_revocation": True,
                "compatibility": True,
                "supply_chain": True,
            },
            "ci_runs": {
                repository: {
                    "sha": "c" * 40,
                    "url": f"https://github.com/Agent-Remote/{repository}/actions/runs/1",
                    "conclusion": "success",
                }
                for repository in (
                    "agent-remote",
                    "agent-remote-server",
                    "agent-remote-node",
                    "agent-remote-cli",
                    "agent-remote-admin-web",
                    "agent-remote-device",
                )
            },
        },
    )
    risk = write(
        root / "risk.json",
        {
            "schema_version": 1,
            "release_version": DISTRIBUTION_VERSION,
            "profile": "community-local-trust",
            "accepted": True,
            "accepted_by": "release-operator",
            "accepted_at": "2026-07-31T08:00:00Z",
            "accepted_risks": [
                "apple_notarization_absent",
                "manual_gatekeeper_trust",
                "system_network_filter_absent",
                "independent_security_review_absent",
            ],
        },
    )
    output = root / "output"
    values = [
        sys.executable,
        str(SCRIPT),
        "--release-version",
        VERSION,
        "--distribution-version",
        DISTRIBUTION_VERSION,
        "--release-manifest",
        str(manifest),
        "--server-metadata",
        str(server),
        "--application-artifact",
        str(application),
        "--community-signing",
        str(signing),
        "--automation-evidence",
        str(automation),
        "--risk-acceptance",
        str(risk),
        "--ci-run-url",
        "https://github.com/Agent-Remote/agent-remote/actions/runs/1",
        "--issued-at",
        "2026-07-31T08:00:00Z",
        "--expires-at",
        "2026-08-07T08:00:00Z",
        "--output-directory",
        str(output),
    ]
    for target in TARGETS:
        values.extend(("--node-artifact", f"{target}={node_artifacts[target]}"))
        values.extend(("--proxy-artifact", f"{target}={proxy_artifacts[target]}"))
    for option in ("sbom", "provenance"):
        labels = ["server", "application"] + [
            f"{component}-{target}"
            for component in ("node", "proxy")
            for target in TARGETS
        ]
        for label in labels:
            value = write(root / f"{label}.{option}.json", f"{label}-{option}")
            values.extend((f"--{option}", f"{label}={value}"))
    return values, output


def add_v2_arguments(root: Path, values: list[str]) -> tuple[Path, Path]:
    target = "linux-amd64-glibc"
    report = b"zero-content Community Computer Use v2 acceptance report"
    report_digest = hashlib.sha256(report).hexdigest()
    archive = root / "community-computer-use-v2.evidence.tar.gz"
    with tarfile.open(archive, mode="w:gz") as output:
        member = tarfile.TarInfo("reports/computer-use-v2.json")
        member.size = len(report)
        output.addfile(member, io.BytesIO(report))
    details = {
        "action_latency_p95_ms": 900,
        "artifact_digest_bound": True,
        "chrome_passed": True,
        "coordinate_fallback_percent": 19.99,
        "current_mcp_runtime_passed": True,
        "electron_fallback_passed": True,
        "firefox_passed": True,
        "golden_prompt_replay_passed": True,
        "model_usage_summary_bound": True,
        "model_visible_image_reduction_percent": 70,
        "native_application_passed": True,
        "report_sha256": report_digest,
        "rollback_rehearsed": True,
        "safari_passed": True,
        "sensitive_telemetry_detected": False,
        "settle_latency_p95_ms": 5_000,
        "signed_installation": True,
        "success_rate_regressed": False,
        "wrong_target_count": 0,
    }
    application = root / "application.artifact"
    record = write(
        root / "community-computer-use-v2-evidence.json",
        {
            "schema_version": 1,
            "release_version": DISTRIBUTION_VERSION,
            "release_profile": "community-local-trust",
            "target": target,
            "artifacts": {
                "server": "a" * 64,
                "node": hashlib.sha256(
                    (root / f"node-{target}.artifact").read_bytes()
                ).hexdigest(),
                "application": hashlib.sha256(application.read_bytes()).hexdigest(),
                "proxy": hashlib.sha256(
                    (root / f"proxy-{target}.artifact").read_bytes()
                ).hexdigest(),
            },
            "collected_at": "2026-07-31T07:00:00Z",
            "evidence_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "producer": "protected Community acceptance Mac",
            "method": "signed artifact-bound acceptance corpus",
            "details": details,
        },
    )
    risk_path = root / "risk.json"
    risk = json.loads(risk_path.read_text(encoding="utf-8"))
    risk["accepted_risks"].append(
        "community_computer_use_v2_without_apple_notarization"
    )
    risk_path.write_text(json.dumps(risk), encoding="utf-8")
    values.extend(
        (
            "--computer-use-v2-evidence",
            str(record),
            "--computer-use-v2-evidence-archive",
            str(archive),
            "--computer-use-v2-target",
            target,
        )
    )
    return record, archive


def test_community_assembler_creates_an_explicit_production_profile(
    tmp_path: Path,
) -> None:
    values, output = arguments(tmp_path)
    subprocess.run(values, check=True)

    draft = json.loads(
        (output / "release-evidence-draft.json").read_text(encoding="utf-8")
    )
    assert draft["schema_version"] == 5
    assert draft["distribution_version"] == DISTRIBUTION_VERSION
    assert draft["components"]["agent-remote-node"]["version"] == "2.3.4"
    assert draft["release_profile"] == "community-local-trust"
    assert draft["production_ready"] is True
    assert draft["apple_notarized"] is False
    assert draft["public_distribution"] is False
    assert draft["manual_trust_required"] is True
    assert draft["community_signing_sha256"] == draft["signing_notarization_sha256"]
    assert draft["automated_release_checks_sha256"]
    assert draft["risk_acceptance_sha256"]
    assert draft["computer_use_v2_evidence_sha256"] is None
    assert set(draft["node_artifacts_sha256"]) == set(TARGETS)
    assert set(draft["proxy_artifacts_sha256"]) == set(TARGETS)
    assert "node_sha256" not in draft
    assert "proxy_sha256" not in draft
    for field in (
        "security_tests_sha256",
        "security_review_sha256",
        "outbound_policy_sha256",
        "local_claude_isolation_sha256",
        "stop_revocation_sha256",
        "compatibility_sha256",
    ):
        assert draft[field] is None


def test_community_assembler_preserves_legacy_schema_for_one_version_composition(
    tmp_path: Path,
) -> None:
    values, output = arguments(tmp_path)
    values[values.index("--distribution-version") + 1] = VERSION

    manifest_path = Path(values[values.index("--release-manifest") + 1])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["distribution_version"] = VERSION
    for component in manifest["components"].values():
        component["version"] = VERSION
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    for option in ("--community-signing", "--automation-evidence", "--risk-acceptance"):
        evidence_path = Path(values[values.index(option) + 1])
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["release_version"] = VERSION
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

    subprocess.run(values, check=True)

    draft = json.loads(
        (output / "release-evidence-draft.json").read_text(encoding="utf-8")
    )
    assert draft["schema_version"] == 3
    assert "distribution_version" not in draft
    assert "release_manifest_sha256" not in draft
    assert "components" not in draft


def test_community_assembler_rejects_missing_risk_acceptance(tmp_path: Path) -> None:
    values, _ = arguments(tmp_path)
    risk_path = tmp_path / "risk.json"
    risk = json.loads(risk_path.read_text(encoding="utf-8"))
    risk["accepted"] = False
    risk_path.write_text(json.dumps(risk), encoding="utf-8")

    result = subprocess.run(values, capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert "risk acceptance is incomplete" in result.stderr


def test_community_assembler_creates_schema_v4_with_bound_v2_evidence(
    tmp_path: Path,
) -> None:
    values, output = arguments(tmp_path)
    record, archive = add_v2_arguments(tmp_path, values)

    subprocess.run(values, check=True)

    draft = json.loads(
        (output / "release-evidence-draft.json").read_text(encoding="utf-8")
    )
    assert draft["schema_version"] == 6
    assert (
        draft["computer_use_v2_evidence_sha256"]
        == hashlib.sha256(record.read_bytes()).hexdigest()
    )
    assert (output / record.name).read_bytes() == record.read_bytes()
    assert (output / archive.name).read_bytes() == archive.read_bytes()


def test_community_assembler_rejects_v2_artifact_mismatch(tmp_path: Path) -> None:
    values, _ = arguments(tmp_path)
    record, _ = add_v2_arguments(tmp_path, values)
    content = json.loads(record.read_text(encoding="utf-8"))
    content["artifacts"]["proxy"] = "f" * 64
    record.write_text(json.dumps(content), encoding="utf-8")

    result = subprocess.run(values, capture_output=True, text=True, check=False)

    assert result.returncode == 2
    assert "not bound to the release" in result.stderr


def test_community_assembler_rejects_v2_threshold_failure(tmp_path: Path) -> None:
    values, _ = arguments(tmp_path)
    record, _ = add_v2_arguments(tmp_path, values)
    content = json.loads(record.read_text(encoding="utf-8"))
    content["details"]["wrong_target_count"] = 1
    record.write_text(json.dumps(content), encoding="utf-8")

    result = subprocess.run(values, capture_output=True, text=True, check=False)

    assert result.returncode == 2
    assert "wrong-target actions" in result.stderr


def test_community_assembler_requires_bound_report_archive_member(
    tmp_path: Path,
) -> None:
    values, _ = arguments(tmp_path)
    record, _ = add_v2_arguments(tmp_path, values)
    content = json.loads(record.read_text(encoding="utf-8"))
    content["details"]["report_sha256"] = "f" * 64
    record.write_text(json.dumps(content), encoding="utf-8")

    result = subprocess.run(values, capture_output=True, text=True, check=False)

    assert result.returncode == 2
    assert "report is not present" in result.stderr


def test_community_assembler_requires_explicit_v2_risk_acceptance(
    tmp_path: Path,
) -> None:
    values, _ = arguments(tmp_path)
    add_v2_arguments(tmp_path, values)
    risk_path = tmp_path / "risk.json"
    risk = json.loads(risk_path.read_text(encoding="utf-8"))
    risk["accepted_risks"].remove(
        "community_computer_use_v2_without_apple_notarization"
    )
    risk_path.write_text(json.dumps(risk), encoding="utf-8")

    result = subprocess.run(values, capture_output=True, text=True, check=False)

    assert result.returncode == 2
    assert "risk acceptance is incomplete" in result.stderr


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as first:
        test_community_assembler_creates_an_explicit_production_profile(Path(first))
    with tempfile.TemporaryDirectory() as second:
        test_community_assembler_preserves_legacy_schema_for_one_version_composition(
            Path(second)
        )
    with tempfile.TemporaryDirectory() as third:
        test_community_assembler_rejects_missing_risk_acceptance(Path(third))
    with tempfile.TemporaryDirectory() as fourth:
        test_community_assembler_creates_schema_v4_with_bound_v2_evidence(Path(fourth))
    with tempfile.TemporaryDirectory() as fifth:
        test_community_assembler_rejects_v2_artifact_mismatch(Path(fifth))
    with tempfile.TemporaryDirectory() as sixth:
        test_community_assembler_rejects_v2_threshold_failure(Path(sixth))
    with tempfile.TemporaryDirectory() as seventh:
        test_community_assembler_requires_bound_report_archive_member(Path(seventh))
    with tempfile.TemporaryDirectory() as eighth:
        test_community_assembler_requires_explicit_v2_risk_acceptance(Path(eighth))
