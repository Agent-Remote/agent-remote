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
    assert manifest["schema_version"] == 3
    components = manifest["components"]
    assert isinstance(components, dict)
    browser = components["agent-remote-ego-browser"]
    assert isinstance(browser, dict)
    assert browser["version"] == "0.1.8"
    assert browser["commit"] == "cd716ca2b65a2a7c65c827b8b10e3613a6f7a284"
    assert browser["release_published"] is True
    assert browser["production_ready"] is True
    assert (
        browser["signer_certificate_sha256"]
        == "1b1527d1c0ac6b3a1e95ccd7d4e6462ece9f5a42d2f4d309d09170588a4197e5"
    )
    assert (
        browser["learning_bundle_digest"]
        == "6662ad11797f86d721b2d9121049c35b02eff3e71821dc06dfcc190d250788a7"
    )
    assert browser["learning_bundle_signing_key_id"] == "ego-browser-learning-2026-09"
    assert browser["readiness_blockers"] == []
    assert browser["apple_notarized"] is False
    assert browser["public_distribution"] is False


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
    assert "Bridge `0.1.8` promotion" in plan
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
    test_json_schema_inventory_matches_strict_parser()
    test_documentation_records_implementation_and_all_acceptance_rows()
    test_root_bridge_documents_record_promoted_readiness()
