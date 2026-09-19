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
    assert browser["release_published"] is True
    assert browser["production_ready"] is True
    assert browser["readiness_blockers"] == []
    assert browser["nested_signatures_verified"] is True
    for field in (
        "signer_certificate_sha256",
        "learning_bundle_digest",
        "artifact_sha256",
        "bridge_manifest_sha256",
        "issued_at",
    ):
        assert browser[field]


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
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    browser_version = source["components"]["agent-remote-ego-browser"]["version"]
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
        "replaces_profile": f"community-local-trust@{browser_version}",
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
