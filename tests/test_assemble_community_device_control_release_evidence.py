import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path("scripts/assemble-community-device-control-release-evidence.py")
VERSION = "1.2.3"


def write(path: Path, value: object) -> Path:
    if isinstance(value, (dict, list)):
        path.write_text(json.dumps(value), encoding="utf-8")
    else:
        path.write_text(str(value), encoding="utf-8")
    return path


def arguments(root: Path) -> tuple[list[str], Path]:
    artifacts = {
        label: write(root / f"{label}.artifact", f"{label}-artifact")
        for label in ("node", "application", "proxy")
    }
    application_sha256 = hashlib.sha256(artifacts["application"].read_bytes()).hexdigest()
    server = write(
        root / "server.json",
        {"version": VERSION, "digest": f"sha256:{'a' * 64}"},
    )
    signing = write(
        root / "community-signing.json",
        {
            "schema_version": 1,
            "release_version": VERSION,
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
            "release_version": VERSION,
            "profile": "community-local-trust",
            "production_ready": True,
            "official_runners_only": True,
            "critical_high_vulnerabilities": 0,
            "checks": {
                "coordinated_release": True,
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
            "release_version": VERSION,
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
        "--server-metadata",
        str(server),
        "--node-artifact",
        str(artifacts["node"]),
        "--application-artifact",
        str(artifacts["application"]),
        "--proxy-artifact",
        str(artifacts["proxy"]),
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
    for option in ("sbom", "provenance"):
        for label in ("server", "node", "application", "proxy"):
            value = write(root / f"{label}.{option}.json", f"{label}-{option}")
            values.extend((f"--{option}", f"{label}={value}"))
    return values, output


def test_community_assembler_creates_an_explicit_production_profile(tmp_path: Path) -> None:
    values, output = arguments(tmp_path)
    subprocess.run(values, check=True)

    draft = json.loads((output / "release-evidence-draft.json").read_text(encoding="utf-8"))
    assert draft["schema_version"] == 2
    assert draft["release_profile"] == "community-local-trust"
    assert draft["production_ready"] is True
    assert draft["apple_notarized"] is False
    assert draft["public_distribution"] is False
    assert draft["manual_trust_required"] is True
    assert draft["community_signing_sha256"] == draft["signing_notarization_sha256"]
    assert draft["automated_release_checks_sha256"]
    assert draft["risk_acceptance_sha256"]
    for field in (
        "security_tests_sha256",
        "security_review_sha256",
        "outbound_policy_sha256",
        "local_claude_isolation_sha256",
        "stop_revocation_sha256",
        "compatibility_sha256",
    ):
        assert draft[field] is None


def test_community_assembler_rejects_missing_risk_acceptance(tmp_path: Path) -> None:
    values, _ = arguments(tmp_path)
    risk_path = tmp_path / "risk.json"
    risk = json.loads(risk_path.read_text(encoding="utf-8"))
    risk["accepted"] = False
    risk_path.write_text(json.dumps(risk), encoding="utf-8")

    result = subprocess.run(values, capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert "risk acceptance is incomplete" in result.stderr


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as first:
        test_community_assembler_creates_an_explicit_production_profile(Path(first))
    with tempfile.TemporaryDirectory() as second:
        test_community_assembler_rejects_missing_risk_acceptance(Path(second))
