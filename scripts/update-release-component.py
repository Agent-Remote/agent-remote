#!/usr/bin/env python3
"""Update one component identity in the certified production composition."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path

from release_manifest import (
    COMPONENTS,
    GIT_SHA,
    RELEASE_WORKFLOW,
    SEMVER,
    load_release_manifest,
)


def replace_line(path: Path, name: str, value: str) -> None:
    """Replace exactly one assignment in a text environment file."""

    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        rf"(?m)^{re.escape(name)}=[^\s]+$", f"{name}={value}", text, count=1
    )
    if count != 1:
        raise ValueError(f"{path}: expected exactly one {name} assignment")
    path.write_text(updated, encoding="utf-8")


def write_atomic(path: Path, value: dict[str, object]) -> None:
    """Atomically replace one JSON file without changing its mode."""

    mode = path.stat().st_mode
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as output:
        json.dump(value, output, indent=2, sort_keys=True)
        output.write("\n")
    replacement = Path(output.name)
    replacement.chmod(mode)
    os.replace(replacement, path)


def main() -> None:
    """Validate and update one release-manifest component pin."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("component", choices=COMPONENTS)
    parser.add_argument("version")
    parser.add_argument("commit")
    parser.add_argument(
        "--release-workflow",
        help="Signer workflow filename; retain the current identity when omitted",
    )
    parser.add_argument(
        "--manifest", type=Path, default=Path("release-manifest.json")
    )
    parser.add_argument(
        "--test-environment",
        type=Path,
        default=Path("deploy/compose/.env.device-test"),
    )
    args = parser.parse_args()
    if SEMVER.fullmatch(args.version) is None:
        parser.error("component version is not semantic")
    if GIT_SHA.fullmatch(args.commit) is None:
        parser.error("component commit is not a full lowercase Git SHA")
    if (
        args.release_workflow is not None
        and RELEASE_WORKFLOW.fullmatch(args.release_workflow) is None
    ):
        parser.error("component release workflow filename is invalid")

    manifest = load_release_manifest(args.manifest)
    components = manifest["components"]
    assert isinstance(components, dict)
    component = components[args.component]
    assert isinstance(component, dict)
    component["version"] = args.version
    component["commit"] = args.commit
    if args.release_workflow is not None:
        component["release_workflow"] = args.release_workflow
    write_atomic(args.manifest, manifest)

    if args.component == "agent-remote-server":
        replace_line(args.test_environment, "SERVER_VERSION", args.version)
    elif args.component == "agent-remote-admin-web":
        replace_line(args.test_environment, "ADMIN_WEB_VERSION", args.version)

    load_release_manifest(args.manifest)


if __name__ == "__main__":
    main()
