import json
import subprocess
import tempfile
from pathlib import Path


SCRIPT = Path("scripts/check-device-control-release-readiness.py").resolve()
REPOSITORIES = (
    "agent-remote",
    "agent-remote-server",
    "agent-remote-node",
    "agent-remote-cli",
    "agent-remote-admin-web",
    "agent-remote-device",
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def initialize_repository(path: Path, name: str, version: str) -> None:
    path.mkdir()
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(
        ["git", "-C", str(path), "config", "user.name", "Release Test"], check=True
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "user.email", "release@example.invalid"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(path),
            "remote",
            "add",
            "origin",
            f"https://github.com/Agent-Remote/{name}.git",
        ],
        check=True,
    )
    if name == "agent-remote":
        write(path / "VERSION", f"{version}\n")
    elif name == "agent-remote-server":
        write(path / "pyproject.toml", f'[project]\nversion = "{version}"\n')
        write(path / "Dockerfile", f"ARG AGENT_REMOTE_VERSION={version}\n")
    elif name == "agent-remote-node":
        write(
            path / "internal/config/config.go", f'var DefaultVersion = "{version}"\n'
        )
        write(
            path / "scripts/build-release.sh",
            f'VERSION="${{VERSION:-{version}}}"\n',
        )
        write(path / "config.example.json", json.dumps({"version": version}))
    elif name == "agent-remote-cli":
        write(path / "Cargo.toml", f'[package]\nversion = "{version}"\n')
        write(
            path / "Cargo.lock",
            f'[[package]]\nname = "agent-remote-cli"\nversion = "{version}"\n',
        )
    elif name == "agent-remote-admin-web":
        write(path / "package.json", json.dumps({"version": version}))
        write(
            path / "package-lock.json",
            json.dumps({"version": version, "packages": {"": {"version": version}}}),
        )
        write(path / "Dockerfile", f"ARG AGENT_REMOTE_VERSION={version}\n")
    elif name == "agent-remote-device":
        write(
            path / "Cargo.toml",
            f'[workspace.package]\nversion = "{version}"\n',
        )
        write(
            path / "Cargo.lock",
            f'[[package]]\nname = "agent-remote-device-proxy"\nversion = "{version}"\n',
        )
    subprocess.run(["git", "-C", str(path), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(path), "commit", "-qm", "release fixture"], check=True
    )
    subprocess.run(["git", "-C", str(path), "tag", f"v{version}"], check=True)


def run_check(workspace: Path, version: str) -> subprocess.CompletedProcess[str]:
    arguments = [
        "python3",
        str(SCRIPT),
        "--version",
        version,
        "--require-clean",
        "--require-tag",
        "--require-origin",
    ]
    for name in REPOSITORIES:
        arguments.extend(["--repository", f"{name}={workspace / name}"])
    return subprocess.run(arguments, check=False, capture_output=True, text=True)


def test_release_train_accepts_only_exact_clean_tagged_repositories() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        workspace = Path(temporary)
        for name in REPOSITORIES:
            initialize_repository(workspace / name, name, "1.2.3")
        result = run_check(workspace, "1.2.3")
        assert result.returncode == 0, result.stderr or result.stdout
        inventory = json.loads(result.stdout)
        assert inventory["ready"] is True
        assert set(inventory["repositories"]) == set(REPOSITORIES)


def test_release_train_reports_version_dirty_origin_and_tag_failures() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        workspace = Path(temporary)
        for name in REPOSITORIES:
            initialize_repository(workspace / name, name, "1.2.3")
        write(workspace / "agent-remote" / "VERSION", "1.2.4\n")
        subprocess.run(
            [
                "git",
                "-C",
                str(workspace / "agent-remote-node"),
                "remote",
                "set-url",
                "origin",
                "https://example.invalid/node.git",
            ],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(workspace / "agent-remote-device"), "tag", "-d", "v1.2.3"],
            check=True,
            capture_output=True,
        )
        device_branch = subprocess.run(
            [
                "git",
                "-C",
                str(workspace / "agent-remote-device"),
                "symbolic-ref",
                "--short",
                "HEAD",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        subprocess.run(
            [
                "git",
                "-C",
                str(workspace / "agent-remote-device"),
                "update-ref",
                "-d",
                f"refs/heads/{device_branch}",
            ],
            check=True,
        )
        result = run_check(workspace, "1.2.3")
        assert result.returncode == 1
        inventory = json.loads(result.stdout)
        assert inventory["ready"] is False
        errors = "\n".join(inventory["errors"])
        assert "VERSION declares 1.2.4" in errors
        assert "worktree is not clean" in errors
        assert "unexpected origin" in errors
        assert "tag v1.2.3 is missing" in errors
        assert "repository has no commit at HEAD" in errors


if __name__ == "__main__":
    test_release_train_accepts_only_exact_clean_tagged_repositories()
    test_release_train_reports_version_dirty_origin_and_tag_failures()
