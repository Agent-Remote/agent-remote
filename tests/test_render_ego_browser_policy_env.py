import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render-ego-browser-policy-env.py"
SOURCE_MANIFEST = ROOT / "release-manifest.json"


def evidence_for(manifest_path: Path) -> dict[str, object]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    browser = manifest["components"]["agent-remote-ego-browser"]
    return {
        "schema_version": 9,
        "distribution_version": manifest["distribution_version"],
        "release_manifest_sha256": hashlib.sha256(
            manifest_path.read_bytes()
        ).hexdigest(),
        "release_profile": browser["profile"],
        "production_ready": True,
        "components": manifest["components"],
        "ego_browser_learning_bundle_sha256": browser["learning_bundle_digest"],
        "ego_browser_release_manifest_sha256": browser["bridge_manifest_sha256"],
        "ego_browser_release_archive_sha256": browser["artifact_sha256"],
        "ego_browser_signing_evidence_sha256": "a" * 64,
        "ego_browser_sigstore_sha256": "b" * 64,
        "ego_browser_provenance_sha256": "c" * 64,
    }


def run_renderer(evidence_path: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(SOURCE_MANIFEST),
            "--evidence",
            str(evidence_path),
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def test_renderer_uses_manifest_and_evidence_as_the_only_policy_sources(
    tmp_path: Path,
) -> None:
    evidence = evidence_for(SOURCE_MANIFEST)
    evidence_path = tmp_path / "evidence.json"
    output = tmp_path / "ego-browser-policy.env"
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

    result = run_renderer(evidence_path, output)

    assert result.returncode == 0, result.stderr
    rendered = dict(
        line.split("=", 1) for line in output.read_text(encoding="utf-8").splitlines()
    )
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    browser = manifest["components"]["agent-remote-ego-browser"]
    assert (
        rendered["EGO_BROWSER_EXPECTED_WRAPPER_VERSION"] == browser["wrapper_version"]
    )
    assert rendered["EGO_BROWSER_EXPECTED_SKILL_COMMIT"] == browser["skill_commit"]
    assert (
        rendered["EGO_BROWSER_EXPECTED_ROOT_MANIFEST_SHA256"]
        == evidence["release_manifest_sha256"]
    )
    assert rendered["EGO_BROWSER_EXPECTED_BRIDGE_PROVENANCE_SHA256"] == "c" * 64


def test_renderer_rejects_evidence_digest_drift(tmp_path: Path) -> None:
    evidence = evidence_for(SOURCE_MANIFEST)
    evidence["ego_browser_release_archive_sha256"] = "d" * 64
    evidence_path = tmp_path / "evidence.json"
    output = tmp_path / "ego-browser-policy.env"
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

    result = run_renderer(evidence_path, output)

    assert result.returncode == 2
    assert "evidence digests do not match" in result.stderr
    assert not output.exists()


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as first:
        test_renderer_uses_manifest_and_evidence_as_the_only_policy_sources(Path(first))
    with tempfile.TemporaryDirectory() as second:
        test_renderer_rejects_evidence_digest_drift(Path(second))
