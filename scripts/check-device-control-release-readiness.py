#!/usr/bin/env python3
"""Validate one immutable device-control release train across all repositories."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

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
    parser.add_argument("--version", required=True)
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


def inspect_repository(
    name: str,
    path: Path,
    version: str,
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

    try:
        head = run_git(path, "rev-parse", "HEAD")
    except subprocess.CalledProcessError:
        head = None
        errors.append(f"{name}: repository has no commit at HEAD")
    result["head"] = head
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
            if head is not None and tagged_commit != head:
                errors.append(f"{name}: tag v{version} does not point to HEAD")
    return result, errors


def main() -> int:
    args = parse_args()
    version = args.version.removeprefix("v")
    if SEMVER.fullmatch(version) is None:
        print(f"invalid semantic version: {args.version}", file=sys.stderr)
        return 2
    try:
        paths = repository_paths(parse_overrides(args.repository))
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2

    inventory: dict[str, object] = {"schema_version": 1, "release_version": version}
    repositories: dict[str, object] = {}
    errors: list[str] = []
    for name in REPOSITORIES:
        result, repository_errors = inspect_repository(
            name,
            paths[name],
            version,
            require_clean=args.require_clean,
            require_tag=args.require_tag,
            require_origin=args.require_origin,
        )
        repositories[name] = result
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
