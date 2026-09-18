import copy
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from release_manifest import load_release_manifest  # noqa: E402


SOURCE_MANIFEST = ROOT / "release-manifest.json"
SOURCE_SCHEMA = ROOT / "release-manifest.schema.json"


def write_manifest(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_browser_component_records_promoted_release_evidence() -> None:
    manifest = load_release_manifest(SOURCE_MANIFEST)
    assert manifest["schema_version"] == 4
    components = manifest["components"]
    assert isinstance(components, dict)
    browser = components["agent-remote-ego-browser"]
    assert isinstance(browser, dict)
    assert browser["version"] == "0.1.13"
    assert browser["commit"] == "ed2b4cd316f1bcbf338e0dfef8766091b59cf003"
    assert browser["release_published"] is True
    assert browser["production_ready"] is True
    assert (
        browser["signer_certificate_sha256"]
        == "1b1527d1c0ac6b3a1e95ccd7d4e6462ece9f5a42d2f4d309d09170588a4197e5"
    )
    assert (
        browser["learning_bundle_digest"]
        == "4d782365e73284c55de320ef91a669c6da5d67650cf066a85c238b152d4f531f"
    )
    assert browser["learning_bundle_signing_key_id"] == "ego-browser-learning-2026-09-v2"
    assert browser["readiness_blockers"] == []
    assert browser["apple_notarized"] is False
    assert browser["public_distribution"] is False
    assert browser["profile_id"] == "community-local-trust"
    assert browser["profile_version"] == browser["version"]
    assert browser["bridge_version"] == browser["version"]
    assert browser["wrapper_version"] == browser["version"]
    assert browser["bridge_protocol_version"] == browser["protocol_version"]
    assert browser["ego_lite_runtime_version"] == browser["local_ego_browser_runtime_version"]
    assert browser["artifact_sha256"] == "7aceb9f7d8dc31dca7511f6a7e9bc9d6c081a16517bb57a3fdb4adb77b7d626a"
    assert browser["bridge_manifest_sha256"] == "df151e3f0a607d62b2ee159c700102cf83b732713d1a231e1bb0285fd101bf6c"
    assert browser["ego_lite_installer_sha256"] == "4cbbc9f211aca61244d9ada601c385cabbeba4ec4417b3a8be1819a01cb0221b"
    assert browser["valid_platforms"] == ["macos"]
    assert browser["allowed_server_origins"] == ["$active_login_origin"]
    assert browser["admission_policy_ref"] == "server-policy:ego-browser-v1"
    assert browser["issued_at"] == "2026-09-18T03:33:57Z"
    assert browser["replaces_profile"] == "community-local-trust@0.1.12"


def test_browser_component_rejects_inconsistent_readiness() -> None:
    for field, value in (
        ("production_ready", False),
        ("release_published", False),
        ("learning_bundle_digest", None),
        ("profile", "development-local"),
    ):
        source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
        source["components"]["agent-remote-ego-browser"][field] = value
        with tempfile.TemporaryDirectory() as temporary:
            manifest = Path(temporary) / "release-manifest.json"
            write_manifest(manifest, copy.deepcopy(source))
            try:
                load_release_manifest(manifest)
            except ValueError:
                pass
            else:
                raise AssertionError(f"accepted inconsistent browser field {field}")


def test_browser_component_requires_blockers_to_match_missing_evidence() -> None:
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    browser = source["components"]["agent-remote-ego-browser"]
    browser["readiness_blockers"] = [
        "learning_bundle_signing_private_key_unavailable",
        "production_release_evidence_unavailable",
    ]
    with tempfile.TemporaryDirectory() as temporary:
        manifest = Path(temporary) / "release-manifest.json"
        write_manifest(manifest, source)
        try:
            load_release_manifest(manifest)
        except ValueError:
            pass
        else:
            raise AssertionError("accepted blockers that omit unpublished and certificate state")


def test_schema_four_rejects_each_release_profile_drift() -> None:
    mutations = {
        "profile_version": "0.1.10",
        "bridge_version": "0.1.10",
        "wrapper_version": "0.1.10",
        "bridge_protocol_version": "ego-browser-bridge-v2",
        "ego_lite_runtime_version": "0.0.0",
        "artifact_url": "https://example.invalid/bridge.tar.gz",
        "artifact_sha256": "f" * 63,
        "bridge_manifest_sha256": None,
        "ego_lite_installer_commit": "f" * 40,
        "ego_lite_installer_sha256": "f" * 64,
        "valid_platforms": ["linux"],
        "allowed_server_origins": ["https://example.invalid"],
        "admission_policy_ref": "server-policy:other",
        "issued_at": None,
        "replaces_profile": "community-local-trust@0.1.13",
    }
    for field, value in mutations.items():
        source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
        source["components"]["agent-remote-ego-browser"][field] = value
        with tempfile.TemporaryDirectory() as temporary:
            manifest = Path(temporary) / "release-manifest.json"
            write_manifest(manifest, source)
            try:
                load_release_manifest(manifest)
            except ValueError:
                pass
            else:
                raise AssertionError(f"accepted inconsistent profile field {field}")


def test_schema_three_manifest_remains_parseable_for_migration() -> None:
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    source["schema_version"] = 3
    browser = source["components"]["agent-remote-ego-browser"]
    schema = json.loads(SOURCE_SCHEMA.read_text(encoding="utf-8"))
    for field in set(browser) - set(schema["$defs"]["egoBrowserComponent"]["required"]):
        browser.pop(field)
    for field in (
        "profile_id",
        "profile_version",
        "bridge_version",
        "bridge_protocol_version",
        "ego_lite_runtime_version",
        "wrapper_version",
        "artifact_url",
        "artifact_sha256",
        "bridge_manifest_sha256",
        "ego_lite_installer_url",
        "ego_lite_installer_commit",
        "ego_lite_installer_sha256",
        "valid_platforms",
        "allowed_server_origins",
        "admission_policy_ref",
        "issued_at",
        "replaces_profile",
    ):
        browser.pop(field, None)
    with tempfile.TemporaryDirectory() as temporary:
        manifest = Path(temporary) / "release-manifest.json"
        write_manifest(manifest, source)
        assert load_release_manifest(manifest)["schema_version"] == 3


def test_json_schema_inventory_matches_strict_parser() -> None:
    schema = json.loads(SOURCE_SCHEMA.read_text(encoding="utf-8"))
    required = schema["properties"]["components"]["required"]
    manifest = load_release_manifest(SOURCE_MANIFEST)
    components = manifest["components"]
    assert isinstance(components, dict)
    assert set(required) == set(components)
    browser_schema = schema["$defs"]["egoBrowserComponent"]
    browser = components["agent-remote-ego-browser"]
    assert isinstance(browser, dict)
    assert set(browser_schema["required"]) == set(browser)


def test_documentation_records_implementation_and_all_acceptance_rows() -> None:
    plan = (ROOT / "docs/remote-ego-browser-bridge-plan.md").read_text(encoding="utf-8")
    acceptance = (ROOT / "docs/ego-browser-bridge-acceptance.md").read_text(
        encoding="utf-8"
    )
    assert "方案状态：待实施" not in plan
    assert "Bridge `0.1.11` promotion" in plan
    assert "production_ready=true" in plan
    assert "capability 默认保持关闭" in plan
    rows = [int(value) for value in re.findall(r"^\| (\d+) \|", acceptance, re.MULTILINE)]
    assert rows == list(range(1, 17))
    for contract in (
        "Bridge promotion complete (`production_ready=true`)",
        "Retained `ego-browser-learning-2026-09` bundle verifies",
        "real local ego lite canary",
        "complete green gates from the exact tagged commits",
        "1440 x 900 and 390 x 844",
        "development evidence, not a substitute",
    ):
        assert contract in acceptance


def test_root_bridge_documents_record_promoted_readiness() -> None:
    for name in (
        "ego-browser-bridge-security.md",
        "ego-browser-bridge-deployment.md",
        "ego-browser-bridge-acceptance.md",
        "ego-browser-bridge-release-promotion.md",
    ):
        content = (ROOT / "docs" / name).read_text(encoding="utf-8")
        assert "production_ready=true" in content

    promotion_en = (ROOT / "docs" / "ego-browser-bridge-release-promotion.md").read_text(
        encoding="utf-8"
    )
    promotion = (ROOT / "docs" / "ego-browser-bridge-release-promotion.zh-CN.md").read_text(
        encoding="utf-8"
    )
    for blocker in (
        "unpublished_component_commit",
        "release_certificate_unpinned",
        "learning_bundle_signing_private_key_unavailable",
        "production_release_evidence_unavailable",
    ):
        assert blocker in promotion
    assert "--prepare-only" in promotion
    assert "--candidate-manifest" in promotion
    assert "cannot consume this uncommitted candidate" in promotion_en
    assert "release-evidence-draft.json" in promotion_en
    assert "重新生成 schema 9 evidence" in promotion


if __name__ == "__main__":
    test_browser_component_records_promoted_release_evidence()
    test_browser_component_rejects_inconsistent_readiness()
    test_browser_component_requires_blockers_to_match_missing_evidence()
    test_schema_four_rejects_each_release_profile_drift()
    test_schema_three_manifest_remains_parseable_for_migration()
    test_json_schema_inventory_matches_strict_parser()
    test_documentation_records_implementation_and_all_acceptance_rows()
    test_root_bridge_documents_record_promoted_readiness()
