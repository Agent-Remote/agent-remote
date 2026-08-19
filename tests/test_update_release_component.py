import json
import subprocess
import tempfile
from pathlib import Path


SCRIPT = Path("scripts/update-release-component.py").resolve()
EXPORT_SCRIPT = Path("scripts/export-release-manifest.py").resolve()
SOURCE_MANIFEST = Path("release-manifest.json").resolve()
SOURCE_ENVIRONMENT = Path("deploy/compose/.env.device-test").resolve()


def test_updates_only_selected_component_and_derived_test_version() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        manifest = root / "release-manifest.json"
        environment = root / ".env.device-test"
        manifest.write_bytes(SOURCE_MANIFEST.read_bytes())
        environment.write_bytes(SOURCE_ENVIRONMENT.read_bytes())
        before = json.loads(manifest.read_text(encoding="utf-8"))

        subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "agent-remote-server",
                "1.4.2",
                "a" * 40,
                "--manifest",
                str(manifest),
                "--test-environment",
                str(environment),
            ],
            check=True,
        )

        after = json.loads(manifest.read_text(encoding="utf-8"))
        assert after["distribution_version"] == before["distribution_version"]
        assert after["components"]["agent-remote-server"]["version"] == "1.4.2"
        assert after["components"]["agent-remote-server"]["commit"] == "a" * 40
        assert (
            after["components"]["agent-remote-server"]["release_workflow"]
            == before["components"]["agent-remote-server"]["release_workflow"]
        )
        assert after["components"]["agent-remote-node"] == before["components"]["agent-remote-node"]
        assert "SERVER_VERSION=1.4.2" in environment.read_text(encoding="utf-8")


def test_rejects_unversioned_or_ambiguous_component_identity() -> None:
    result = subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "agent-remote-node",
            "latest",
            "short",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "component version is not semantic" in result.stderr


def test_exports_independent_component_versions_for_github_actions() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        environment = root / "github-env"
        outputs = root / "github-output"
        environment.touch()
        outputs.touch()
        source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
        distribution_version = source["distribution_version"]
        server_version = source["components"]["agent-remote-server"]["version"]
        device_commit = source["components"]["agent-remote-device"]["commit"]
        device_workflow = source["components"]["agent-remote-device"][
            "release_workflow"
        ]

        subprocess.run(
            [
                "python3",
                str(EXPORT_SCRIPT),
                "--manifest",
                str(SOURCE_MANIFEST),
                "--expected-distribution-version",
                distribution_version,
                "--github-env",
                str(environment),
                "--github-output",
                str(outputs),
            ],
            check=True,
        )

        exported = outputs.read_text(encoding="utf-8")
        assert f"distribution-version={distribution_version}" in exported
        assert f"server-version={server_version}" in exported
        assert f"device-commit={device_commit}" in exported
        assert f"device-workflow={device_workflow}" in exported


if __name__ == "__main__":
    test_updates_only_selected_component_and_derived_test_version()
    test_rejects_unversioned_or_ambiguous_component_identity()
    test_exports_independent_component_versions_for_github_actions()
