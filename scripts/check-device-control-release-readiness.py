#!/usr/bin/env python3
"""Validate one immutable production distribution across component repositories."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

from release_manifest import COMPONENTS, load_release_manifest

REPOSITORIES = (
    "agent-remote",
    "agent-remote-server",
    "agent-remote-node",
    "agent-remote-cli",
    "agent-remote-admin-web",
    "agent-remote-device",
)
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-.+][0-9A-Za-z.-]+)?$")
EXPECTED_ORIGINS = {
    name: f"Agent-Remote/{name}" for name in REPOSITORIES
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--repository",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Override a repository path; may be repeated.",
    )
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument("--require-tag", action="store_true")
    parser.add_argument("--require-origin", action="store_true")
    parser.add_argument("--json-output", type=Path)
    return parser.parse_args()


def run_git(path: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(path), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def canonical_github_origin(value: str) -> str | None:
    patterns = (
        r"^https://github\.com/([^/]+/[^/]+?)(?:\.git)?$",
        r"^git@github\.com:([^/]+/[^/]+?)(?:\.git)?$",
        r"^ssh://git@github\.com/([^/]+/[^/]+?)(?:\.git)?$",
    )
    for pattern in patterns:
        match = re.fullmatch(pattern, value)
        if match is not None:
            return match.group(1)
    return None


def parse_overrides(values: list[str]) -> dict[str, Path]:
    overrides: dict[str, Path] = {}
    for value in values:
        name, separator, raw_path = value.partition("=")
        if separator != "=" or name not in REPOSITORIES or not raw_path:
            raise ValueError(f"invalid repository override: {value}")
        if name in overrides:
            raise ValueError(f"duplicate repository override: {name}")
        overrides[name] = Path(raw_path).expanduser().resolve()
    return overrides


def repository_paths(overrides: dict[str, Path]) -> dict[str, Path]:
    current = Path.cwd().resolve()
    parent = current.parent if current.name == "agent-remote" else current
    paths = {name: (parent / name).resolve() for name in REPOSITORIES}
    paths.update(overrides)
    return paths


def toml_version(path: Path, *keys: str) -> str:
    value: object = tomllib.loads(path.read_text(encoding="utf-8"))
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            raise ValueError(f"missing {'.'.join(keys)} in {path}")
        value = value[key]
    if not isinstance(value, str):
        raise ValueError(f"non-string {'.'.join(keys)} in {path}")
    return value


def json_version(path: Path, *keys: str) -> str:
    value: object = json.loads(path.read_text(encoding="utf-8"))
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            raise ValueError(f"missing {'.'.join(keys)} in {path}")
        value = value[key]
    if not isinstance(value, str):
        raise ValueError(f"non-string {'.'.join(keys)} in {path}")
    return value


def match_version(path: Path, pattern: str) -> str:
    match = re.search(pattern, path.read_text(encoding="utf-8"), re.MULTILINE)
    if match is None:
        raise ValueError(f"version pattern was not found in {path}")
    return match.group(1)


def lock_version(path: Path, package_name: str) -> str:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    matches = [
        package.get("version")
        for package in data.get("package", [])
        if package.get("name") == package_name
    ]
    if len(matches) != 1 or not isinstance(matches[0], str):
        raise ValueError(f"expected one {package_name} package in {path}")
    return matches[0]


def declared_versions(name: str, path: Path) -> dict[str, str]:
    if name == "agent-remote":
        return {"VERSION": (path / "VERSION").read_text(encoding="utf-8").strip()}
    if name == "agent-remote-server":
        return {
            "pyproject.toml": toml_version(path / "pyproject.toml", "project", "version"),
            "Dockerfile": match_version(
                path / "Dockerfile", r"^ARG AGENT_REMOTE_VERSION=([^\s]+)$"
            ),
        }
    if name == "agent-remote-node":
        return {
            "internal/config/config.go": match_version(
                path / "internal/config/config.go", r'^var DefaultVersion = "([^"]+)"$'
            ),
            "scripts/build-release.sh": match_version(
                path / "scripts/build-release.sh",
                r'^VERSION="\$\{VERSION:-([^}]+)\}"$',
            ),
            "config.example.json": json_version(path / "config.example.json", "version"),
        }
    if name == "agent-remote-cli":
        return {
            "Cargo.toml": toml_version(path / "Cargo.toml", "package", "version"),
            "Cargo.lock": lock_version(path / "Cargo.lock", "agent-remote-cli"),
        }
    if name == "agent-remote-admin-web":
        return {
            "package.json": json_version(path / "package.json", "version"),
            "package-lock.json": json_version(path / "package-lock.json", "version"),
            "package-lock.json#root": json_version(
                path / "package-lock.json", "packages", "", "version"
            ),
            "Dockerfile": match_version(
                path / "Dockerfile", r"^ARG AGENT_REMOTE_VERSION=([^\s]+)$"
            ),
        }
    if name == "agent-remote-device":
        return {
            "Cargo.toml": toml_version(
                path / "Cargo.toml", "workspace", "package", "version"
            ),
            "Cargo.lock": lock_version(path / "Cargo.lock", "agent-remote-device-proxy"),
        }
    raise ValueError(f"unsupported repository: {name}")


def load_manifest(path: Path) -> tuple[str, dict[str, dict[str, str]]]:
    value = load_release_manifest(path)
    distribution_version = value["distribution_version"]
    raw_components = value["components"]
    assert isinstance(distribution_version, str)
    assert isinstance(raw_components, dict)
    components: dict[str, dict[str, str]] = {}
    for name in COMPONENTS:
        component = raw_components[name]
        assert isinstance(component, dict)
        repository = component["repository"]
        version = component["version"]
        commit = component["commit"]
        release_workflow = component.get("release_workflow", "release.yml")
        assert isinstance(repository, str)
        assert isinstance(version, str)
        assert isinstance(commit, str)
        assert isinstance(release_workflow, str)
        components[name] = {
            "repository": repository,
            "version": version,
            "commit": commit,
            "release_workflow": release_workflow,
        }
    return distribution_version, components


def inspect_repository(
    name: str,
    path: Path,
    version: str,
    expected_commit: str | None,
    release_workflow: str | None,
    *,
    require_clean: bool,
    require_tag: bool,
    require_origin: bool,
) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    result: dict[str, object] = {"path": str(path)}
    if not path.is_dir() or not (path / ".git").exists():
        return result, [f"{name}: repository is missing at {path}"]
    try:
        versions = declared_versions(name, path)
    except (OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        return result, [f"{name}: {error}"]
    result["declared_versions"] = versions
    for source, declared in versions.items():
        if declared != version:
            errors.append(f"{name}: {source} declares {declared}, expected {version}")
    if release_workflow is not None:
        workflow_path = path / ".github" / "workflows" / release_workflow
        result["release_workflow"] = release_workflow
        if not workflow_path.is_file() or workflow_path.is_symlink():
            errors.append(f"{name}: release workflow is missing: {release_workflow}")

    try:
        head = run_git(path, "rev-parse", "HEAD")
    except subprocess.CalledProcessError:
        head = None
        errors.append(f"{name}: repository has no commit at HEAD")
    result["head"] = head
    if expected_commit is not None and head is not None and head != expected_commit:
        errors.append(f"{name}: HEAD is {head}, expected manifest commit {expected_commit}")
    try:
        dirty = bool(run_git(path, "status", "--porcelain=v1", "--untracked-files=all"))
    except subprocess.CalledProcessError:
        dirty = True
        errors.append(f"{name}: worktree status could not be read")
    result["dirty"] = dirty
    if require_clean and dirty:
        errors.append(f"{name}: worktree is not clean")

    if require_origin:
        try:
            origin = run_git(path, "remote", "get-url", "origin")
        except subprocess.CalledProcessError:
            errors.append(f"{name}: origin remote is missing")
        else:
            result["origin"] = origin
            if canonical_github_origin(origin) != EXPECTED_ORIGINS[name]:
                errors.append(f"{name}: unexpected origin {origin}")

    if require_tag:
        tag = f"refs/tags/v{version}^{{commit}}"
        try:
            tagged_commit = run_git(path, "rev-parse", "--verify", tag)
        except subprocess.CalledProcessError:
            errors.append(f"{name}: tag v{version} is missing")
        else:
            result["tagged_commit"] = tagged_commit
            if expected_commit is not None and tagged_commit != expected_commit:
                errors.append(
                    f"{name}: tag v{version} points to {tagged_commit}, "
                    f"expected manifest commit {expected_commit}"
                )
            if head is not None and tagged_commit != head:
                errors.append(f"{name}: tag v{version} does not point to HEAD")
    return result, errors


def main() -> int:
    args = parse_args()
    try:
        paths = repository_paths(parse_overrides(args.repository))
        distribution_version, components = load_manifest(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        return 2

    inventory: dict[str, object] = {
        "schema_version": 2,
        "distribution_version": distribution_version,
        "manifest": str(args.manifest.resolve()),
    }
    repositories: dict[str, object] = {}
    errors: list[str] = []
    for name in REPOSITORIES:
        if name == "agent-remote":
            version = distribution_version
            expected_commit = None
            release_workflow = None
        else:
            version = components[name]["version"]
            expected_commit = components[name]["commit"]
            release_workflow = components[name]["release_workflow"]
        result, repository_errors = inspect_repository(
            name,
            paths[name],
            version,
            expected_commit,
            release_workflow,
            require_clean=args.require_clean,
            require_tag=args.require_tag,
            require_origin=args.require_origin,
        )
        repositories[name] = result
        if name != "agent-remote":
            result["manifest"] = components[name]
        errors.extend(repository_errors)
    inventory["repositories"] = repositories
    inventory["ready"] = not errors
    inventory["errors"] = errors

    encoded = json.dumps(inventory, indent=2, sort_keys=True) + "\n"
    if args.json_output is not None:
        if args.json_output.exists() or args.json_output.is_symlink():
            print(f"refusing to overwrite {args.json_output}", file=sys.stderr)
            return 2
        args.json_output.write_text(encoded, encoding="utf-8")
    sys.stdout.write(encoded)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
