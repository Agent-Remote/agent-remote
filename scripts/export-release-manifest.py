#!/usr/bin/env python3
"""Export a certified release manifest for GitHub Actions workflows."""

from __future__ import annotations

import argparse
from pathlib import Path

from release_manifest import load_release_manifest, release_manifest_sha256

OUTPUT_NAMES = {
    "agent-remote-server": "server",
    "agent-remote-node": "node",
    "agent-remote-cli": "cli",
    "agent-remote-admin-web": "admin",
    "agent-remote-device": "device",
}


def append_lines(path: Path, lines: list[str]) -> None:
    """Append validated single-line values to one GitHub Actions command file."""

    with path.open("a", encoding="utf-8") as output:
        output.write("\n".join(lines) + "\n")


def main() -> None:
    """Validate a release manifest and export component identities."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-distribution-version", required=True)
    parser.add_argument("--github-env", type=Path, required=True)
    parser.add_argument("--github-output", type=Path, required=True)
    args = parser.parse_args()

    manifest = load_release_manifest(args.manifest)
    distribution_version = manifest["distribution_version"]
    if distribution_version != args.expected_distribution_version:
        parser.error("distribution version does not match the release manifest")
    components = manifest["components"]
    assert isinstance(components, dict)
    environment = [f"DISTRIBUTION_VERSION={distribution_version}"]
    outputs = [f"distribution-version={distribution_version}"]
    for component_name, output_name in OUTPUT_NAMES.items():
        component = components[component_name]
        assert isinstance(component, dict)
        version = component["version"]
        commit = component["commit"]
        workflow = component.get("release_workflow", "release.yml")
        environment.extend(
            (
                f"{output_name.upper()}_VERSION={version}",
                f"{output_name.upper()}_COMMIT={commit}",
                f"{output_name.upper()}_WORKFLOW={workflow}",
            )
        )
        outputs.extend(
            (
                f"{output_name}-version={version}",
                f"{output_name}-commit={commit}",
                f"{output_name}-workflow={workflow}",
            )
        )
    manifest_digest = release_manifest_sha256(args.manifest)
    environment.append(f"RELEASE_MANIFEST_SHA256={manifest_digest}")
    outputs.append(f"release-manifest-sha256={manifest_digest}")
    append_lines(args.github_env, environment)
    append_lines(args.github_output, outputs)


if __name__ == "__main__":
    main()
