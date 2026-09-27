"""Check component-owned release dependencies against the selected composition."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from release_manifest import load_release_manifest


def dependency_errors(
    paths: dict[str, Path], components: dict[str, object]
) -> list[str]:
    """Reject stale or missing runtime pins even when every component tag exists."""
    errors: list[str] = []
    edges = {
        "agent-remote-cli": {
            "node": (
                "agent-remote-node",
                ("repository", "version", "release_workflow"),
            ),
            "ego_browser_bridge": (
                "agent-remote-ego-browser",
                (
                    "repository",
                    "version",
                    "protocol_version",
                    "profile_id",
                    "credential_profile",
                    "signer_certificate_sha256",
                ),
            ),
        },
        "agent-remote-node": {
            "device_proxy": (
                "agent-remote-device",
                ("repository", "version", "commit", "release_workflow"),
            ),
            "ego_browser_wrapper": (
                "agent-remote-ego-browser",
                ("repository", "version", "protocol_version", "release_workflow"),
            ),
        },
    }
    for owner, dependencies in edges.items():
        path = paths[owner] / "release-dependencies.json"
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(document, dict):
                raise ValueError("expected a JSON object")
            expected_schema = 1 if owner == "agent-remote-cli" else 4
            if document.get("schema_version") != expected_schema:
                raise ValueError(f"expected schema_version {expected_schema}")
            for key, (target, fields) in dependencies.items():
                dependency = document.get(key)
                expected = components[target]
                if not isinstance(dependency, dict) or not isinstance(expected, dict):
                    raise ValueError(f"missing dependency {key}")
                for field in fields:
                    if dependency.get(field) != expected.get(field):
                        errors.append(
                            f"{owner}: release-dependencies.json {key}.{field} declares "
                            f"{dependency.get(field)!r}, expected {expected.get(field)!r} "
                            f"from {target}"
                        )
                if owner == "agent-remote-cli" and key == "ego_browser_bridge":
                    bootstrap = dependency.get("bootstrap")
                    if (
                        not isinstance(bootstrap, dict)
                        or bootstrap.get("commit") != expected["commit"]
                    ):
                        errors.append(
                            f"{owner}: Bridge bootstrap commit does not match {target}"
                        )
        except (OSError, ValueError, KeyError) as error:
            errors.append(
                f"{owner}: cannot validate release-dependencies.json: {error}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--cli-repository", type=Path, required=True)
    parser.add_argument("--node-repository", type=Path, required=True)
    args = parser.parse_args()
    manifest = load_release_manifest(args.manifest)
    errors = dependency_errors(
        {
            "agent-remote-cli": args.cli_repository,
            "agent-remote-node": args.node_repository,
        },
        manifest["components"],
    )
    if errors:
        print("\n".join(errors))
        return 1
    print("Component-owned release dependencies match the selected composition")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
