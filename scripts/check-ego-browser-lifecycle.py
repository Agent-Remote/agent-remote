#!/usr/bin/env python3
"""Validate the ego-browser lifecycle contract and installed sibling sources."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from release_manifest import load_release_manifest


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ego-browser-humanized-lifecycle.md"
MANIFEST = ROOT / "release-manifest.json"
COMPONENT_PATHS = {
    name: ROOT.parent / name
    for name in (
        "agent-remote-cli",
        "agent-remote-node",
        "agent-remote-server",
        "agent-remote-admin-web",
        "agent-remote-ego-browser",
    )
}
REPOSITORY_PATHS = {"agent-remote": ROOT, **COMPONENT_PATHS}

ISSUE_REQUEST_FIELDS = {"expires_in_seconds", "ego_browser_enabled", "exchange_id"}
ISSUE_DATA_FIELDS = {"node_id", "code", "expires_at", "ego_browser_enabled"}
REVOKE_REQUEST_FIELDS = {"exchange_id"}
REVOKE_DATA_FIELDS = {"state"}
EXCHANGE_REQUEST_FIELDS = {
    "node_id",
    "version",
    "join_code",
    "exchange_id",
    "release_profile",
    "wrapper_version",
    "skill_version",
    "runtime_version",
    "artifact_digest",
    "profile_digest",
    "ego_browser_enabled",
}
EXCHANGE_DATA_FIELDS = {
    "node_id",
    "node_token",
    "ego_browser_enabled",
    "exchange_id",
    "server_origin",
    "release_profile",
    "wrapper_version",
    "skill_version",
    "runtime_version",
    "artifact_digest",
    "profile_digest",
    "ego_browser_enabled_intent",
}


@dataclass(frozen=True)
class EvidenceReference:
    """One stable test symbol and its outcome-defining assertions."""

    repository: str
    path: str
    test: str
    assertions: tuple[str, ...]


def evidence(
    repository: str,
    path: str,
    test: str,
    *assertions: str,
) -> EvidenceReference:
    return EvidenceReference(repository, path, test, assertions)


# Section 10 evidence matrix; compound scenarios may span repositories.
SECTION_10_EVIDENCE_MATRIX: tuple[tuple[str, tuple[EvidenceReference, ...]], ...] = (
    (
        "repeat-setup-keeps-one-device",
        (
            evidence(
                "agent-remote-ego-browser",
                "integration-tests/real-relay-e2e.sh",
                "run_managed_setup",
                "assert device_count == 1, device_count",
                "assert ensure_count == 1, ensure_count",
                "assert binding_count == 0, binding_count",
                "run_managed_cli ego-browser setup --yes",
            ),
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/lib.rs",
                "pending_registration_round_trip_reuses_identity_and_idempotency_key",
                "load_pending_registration()",
                "read recovered identity key",
            ),
            evidence(
                "agent-remote-server",
                "tests/test_ego_browser_api.py",
                "test_register_and_ensure_replay_one_logical_device_enrollment",
                'assert [item["id"] for item in devices.json()["data"]["items"]] == [device_id]',
            ),
        ),
    ),
    (
        "concurrent-setup-keeps-one-identity",
        (
            evidence(
                "agent-remote-ego-browser",
                "integration-tests/real-relay-e2e.sh",
                "run_concurrent_managed_setup",
                'result["error_code"] == "local_lock_busy"',
                "assert device_count == 1, device_count",
                '"$identity_sha256"',
            ),
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/lib.rs",
                "registration_lock_serializes_concurrent_ensure_without_replacing_the_key",
                "Err(CredentialError::LocalLockBusy)",
                "read retained identity key",
            ),
            evidence(
                "agent-remote-server",
                "tests/test_ego_browser_concurrency.py",
                "test_concurrent_first_ensure_creates_one_device_and_replays_one_credential",
                "assert first_credential.raw_token == second_credential.raw_token",
                "assert len(ensure_requests) == 1",
            ),
        ),
    ),
    (
        "node-default-and-failed-enable-are-fail-closed",
        (
            evidence(
                "agent-remote-node",
                "internal/config/config_test.go",
                "TestLoadMigratesMissingEgoBrowserEnabledToFalse",
                "missing ego-browser intent was not fail-closed",
                "migrated config did not persist explicit false",
            ),
            evidence(
                "agent-remote-node",
                "cmd/agent-remote-node/main_test.go",
                "TestInstallNodeExplicitEnableVerifiesBeforeReadingOrExchangingJoinCode",
                "invalid local release consumed the join exchange",
                "failed enable changed the existing config bytes",
            ),
        ),
    ),
    (
        "bridge-upgrade-preserves-device-identity",
        (
            evidence(
                "agent-remote-ego-browser",
                "tests/release_scripts_test.sh",
                "signed Bridge upgrade preserved Device identity",
                'bash "$root/installer/install-macos.sh"',
                "--upgrade --yes",
                '"$probe_key_digest"',
                "retained-upgrade-device",
            ),
            evidence(
                "agent-remote-cli",
                "src/ego_browser.rs",
                "bridge_upgrade_always_selects_the_fixed_profile_bootstrap",
                "BridgeInstallerSource::ManagedBootstrap",
            ),
        ),
    ),
    (
        "node-reinstall-preserves-intent-unless-explicit",
        (
            evidence(
                "agent-remote-node",
                "cmd/agent-remote-node/main_test.go",
                "TestConfigureEgoBrowserSynchronizesVersionWithoutEnabling",
                "for _, enabled := range []bool{false, true}",
                "updated.EgoBrowserEnabled != enabled",
            ),
            evidence(
                "agent-remote-server",
                "tests/test_node_join_codes.py",
                "test_existing_node_preserves_omitted_join_intent",
                "assert node.ego_browser_enabled is False",
            ),
            evidence(
                "agent-remote-server",
                "tests/test_node_join_codes.py",
                "test_existing_node_changes_join_intent_only_when_explicitly_echoed",
                "assert node.ego_browser_enabled is expected_enabled",
            ),
        ),
    ),
    (
        "managed-setup-reuses-login-and-discovers-profile",
        (
            evidence(
                "agent-remote-ego-browser",
                "integration-tests/real-relay-e2e.sh",
                "run_managed_setup",
                "AGENT_REMOTE_SECRET_BACKEND=file",
                'expected_device_args="ensure --server $server_url --token-stdin"',
                '"managed setup exposed its control-plane token"',
            ),
            evidence(
                "agent-remote-cli",
                "tests/cli_contract.rs",
                "ego_browser_setup_requires_exact_profile_trust_without_running_an_installer",
                '.args(["--json", "ego-browser", "setup"])',
                'write_user_token(&state_home, &server_url, "art_setup-trust-token");',
                'starts_with("GET /api/v1/ego-browser/policy HTTP/1.1")',
            ),
        ),
    ),
    (
        "expired-credential-refreshes-without-new-device",
        (
            evidence(
                "agent-remote-ego-browser",
                "integration-tests/real-relay-e2e.sh",
                "refresh_expired_credential_with_managed_setup",
                'credential["expires_at_unix"] = 1',
                'test "$refreshed_revision" -gt "$initial_revision"',
                "assert device_count == 1, device_count",
            ),
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/main.rs",
                "pending_ensure_reuses_only_a_credential_outside_refresh_skew",
                "credential.expires_at_unix = 10_300;",
                "assert!(!crate::registration::credential_is_fresh(",
            ),
            evidence(
                "agent-remote-server",
                "tests/test_ego_browser_api.py",
                "test_register_and_ensure_replay_one_logical_device_enrollment",
                'assert [item["id"] for item in devices.json()["data"]["items"]] == [device_id]',
            ),
        ),
    ),
    (
        "register-and-ensure-share-one-idempotent-operation",
        (
            evidence(
                "agent-remote-server",
                "tests/test_ego_browser_api.py",
                "test_register_and_ensure_replay_one_logical_device_enrollment",
                '"Idempotency-Key": "shared-register-ensure-key-123456"',
                '== registered.json()["data"]["credential"]["access_token"]',
            ),
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/lib.rs",
                "device_ensure_uses_canonical_endpoint_and_idempotency_key",
                'assert_eq!(idempotency, "policy-sync-idempotency-key");',
            ),
        ),
    ),
    (
        "device-rotate-reuses-pending-key-across-retries",
        (
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/lib.rs",
                "identity_rotation_is_monotonic_retryable_and_clears_the_old_handoff",
                "assert_eq!(recovered.public_key_b64(), pending.public_key_b64());",
                "assert_eq!(recovered.generation, pending.generation);",
                'expect("recover operation after key commit")',
            ),
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/lib.rs",
                "identity_rotation_finalizes_after_pending_key_cleanup_crash",
                "finish_interrupted_identity_rotation(&next, &rotated_credential)",
                "pending_rotation_metadata_path",
            ),
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/lib.rs",
                "identity_rotation_metadata_only_state_rejects_the_old_credential",
                "finish_interrupted_identity_rotation(&next, &current_credential)",
                'expect("retain rotation metadata")',
                'expect("retain old credential")',
            ),
            evidence(
                "agent-remote-server",
                "tests/test_ego_browser_api.py",
                "test_device_rotate_recovers_after_lost_response_without_advancing_twice",
                'assert recovered_data["device_generation"] == 2',
                'assert recovered_data["credential"]["credential_revision"] > first_revision',
            ),
        ),
    ),
    (
        "setup-rejects-server-without-admission-split",
        (
            evidence(
                "agent-remote-cli",
                "tests/cli_contract.rs",
                "ego_browser_setup_rejects_legacy_admission_before_creating_identity",
                'assert_eq!(value["error_code"], "server_capability_unavailable");',
                "assert!(!device_home.exists());",
                'starts_with("GET /api/v1/ego-browser/policy HTTP/1.1")',
            ),
            evidence(
                "agent-remote-cli",
                "src/ego_browser.rs",
                "maps_missing_admission_split_to_a_stable_capability_error",
                "error_code=server_capability_unavailable",
                "next_action=repair",
            ),
        ),
    ),
    (
        "revoked-or-corrupt-identity-is-not-recreated",
        (
            evidence(
                "agent-remote-server",
                "tests/test_ego_browser_api.py",
                "test_canonical_ensure_creates_initial_identity_but_retained_mode_requires_existing",
                '"EGO_BROWSER_DEVICE_NOT_FOUND"',
                '"EGO_BROWSER_DEVICE_CONFLICT"',
            ),
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/main.rs",
                "ensure_rejects_an_orphaned_corrupt_key_without_replacing_identity",
                "Some(CredentialError::Malformed)",
                'fs::read(&key_path).expect("read retained key")',
                "original_key",
                "ego-browser-pending-registration.json",
            ),
        ),
    ),
    (
        "lost-credential-commit-reuses-pending-identity",
        (
            evidence(
                "agent-remote-ego-browser",
                "integration-tests/real-relay-e2e.sh",
                "recover_lost_credential_commit_with_managed_setup",
                '"idempotency_key": operation_key',
                'cmp "$committed_credential" "$credential"',
                "assert ensure_count == 3, ensure_count",
                "assert credential_count == 3, credential_count",
            ),
            evidence(
                "agent-remote-server",
                "tests/test_ego_browser_api.py",
                "test_register_and_ensure_replay_one_logical_device_enrollment",
                '== registered.json()["data"]["credential"]["access_token"]',
            ),
        ),
    ),
    (
        "first-concurrent-registration-serializes-missing-row",
        (
            evidence(
                "agent-remote-server",
                "tests/test_ego_browser_concurrency.py",
                "test_concurrent_first_ensure_creates_one_device_and_replays_one_credential",
                "assert not second_task.done()",
                "assert [device.id for device in devices] == [device_id]",
            ),
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/lib.rs",
                "registration_lock_serializes_concurrent_ensure_without_replacing_the_key",
                "registration lock is reusable after the first setup",
            ),
        ),
    ),
    (
        "setup-never-claims-and-connect-requires-selection",
        (
            evidence(
                "agent-remote-ego-browser",
                "integration-tests/real-relay-e2e.sh",
                "run_managed_setup",
                "assert binding_count == 0, binding_count",
                'assert result["result"] == "ready", result',
            ),
            evidence(
                "agent-remote-cli",
                "src/ego_browser.rs",
                "candidate_selection_fails_closed_without_tty_and_for_ambiguous_prefixes",
                "error_code=confirmation_required",
                "next_action=select_session",
            ),
            evidence(
                "agent-remote-cli",
                "tests/cli_contract.rs",
                "ego_browser_setup_requires_exact_profile_trust_without_running_an_installer",
                "assert!(!bootstrap_probe.exists());",
            ),
        ),
    ),
    (
        "lifecycle-target-resolution-never-guesses",
        (
            evidence(
                "agent-remote-cli",
                "src/ego_browser.rs",
                "local_handoff_target_uses_exact_generation_without_server_lookup",
                '("binding-local".to_owned(), 9)',
            ),
            evidence(
                "agent-remote-cli",
                "src/ego_browser.rs",
                "lifecycle_target_fails_closed_without_tty_when_multiple_are_eligible",
                "state=multiple_bindings",
                "next_action=select_binding",
            ),
            evidence(
                "agent-remote-cli",
                "src/ego_browser.rs",
                "lifecycle_target_automatically_selects_the_only_eligible_binding",
                'assert_eq!(selected.id, "binding-only");',
            ),
            evidence(
                "agent-remote-cli",
                "src/ego_browser.rs",
                "lifecycle_target_interactive_index_selection_is_strict_and_bounded",
                'parse_lifecycle_binding_selection(" 2\\n", 3)',
                'for invalid in ["", "0", "4", "two", "1 2"]',
            ),
        ),
    ),
    (
        "remove-retires-runtime-and-forget-purges-identity",
        (
            evidence(
                "agent-remote-ego-browser",
                "integration-tests/real-relay-e2e.sh",
                "remove_then_forget_with_retained_release",
                'test ! -L "$install_root/current"',
                'test -f "$device_home/ego-browser-policy.json"',
                '"retire-local --confirmed-stopped"',
                '"purge-local --confirmed-revoked"',
                'assert devices == [("revoked",)], devices',
            ),
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/lib.rs",
                "local_metadata_is_non_secret_and_runtime_retirement_preserves_identity",
                'store.retire_runtime_state().expect("retire runtime state");',
                "load_identity(",
            ),
            evidence(
                "agent-remote-cli",
                "src/ego_browser.rs",
                "retained_release_device_client_rejects_links_and_unsafe_modes",
                "managed_device_client_at_root(&root)",
                "std::fs::hard_link(&client, &hard_link)",
                "symlink(&outside, &client)",
            ),
        ),
    ),
    (
        "offline-forget-persists-revocation-before-purge",
        (
            evidence(
                "agent-remote-cli",
                "tests/cli_contract.rs",
                "offline_forget_persists_revocation_and_preserves_local_identity",
                'assert_eq!(value["error_code"], "pending_revocation");',
                'assert_eq!(pending["retry_count"], 1);',
                "assert!(!purge_marker.exists());",
                "assert_eq!(fs::read(key_path).unwrap(), key_before);",
            ),
        ),
    ),
    (
        "join-code-rejects-invalid-use-and-replays-one-token",
        (
            evidence(
                "agent-remote-server",
                "tests/test_node_join_codes.py",
                "test_join_code_exchange_recovers_the_same_token",
                "assert first_token == recovered_token == replayed_token",
            ),
            evidence(
                "agent-remote-server",
                "tests/test_node_join_codes.py",
                "test_expired_join_code_is_rejected_without_consumption",
                'assert caught.value.code == "NODE_JOIN_CODE_EXPIRED"',
                "assert record.consumed_at is None",
            ),
            evidence(
                "agent-remote-server",
                "tests/test_node_join_codes.py",
                "test_consumed_join_code_rejects_replay_with_a_different_exchange",
                'assert caught.value.code == "NODE_JOIN_CODE_REPLAYED"',
                "assert records[0].exchange_id == original_exchange_id",
            ),
            evidence(
                "agent-remote-server",
                "tests/test_node_join_codes.py",
                "test_join_code_exchange_rejects_a_second_code_for_same_exchange",
                '"NODE_JOIN_CODE_EXCHANGE_CONFLICT"',
            ),
            evidence(
                "agent-remote-server",
                "tests/test_node_join_codes.py",
                "test_join_code_profile_metadata_tampering_fails_closed_before_consumption",
                '"NODE_JOIN_CODE_PROFILE_MISMATCH"',
                "assert record.consumed_at is None",
            ),
        ),
    ),
    (
        "admin-cannot-perform-local-authorization",
        (
            evidence(
                "agent-remote-admin-web",
                "src/pages/console/EgoBrowserPage.test.tsx",
                "keeps setup, connect, resume, and full-trust authorization local-only",
                'for (const name of ["Setup", "Ensure", "Connect", "Resume", "Authorize full trust"])',
                'queryByRole("button", { name })',
                "expect(requestMock).not.toHaveBeenCalled();",
            ),
        ),
    ),
    (
        "execution-admission-is-independent-and-fail-closed",
        (
            evidence(
                "agent-remote-server",
                "tests/test_ego_browser_api.py",
                "test_execution_gate_blocks_new_execution_but_allows_enrollment_and_cleanup",
                '"EGO_BROWSER_EXECUTION_ADMISSION_DISABLED"',
            ),
            evidence(
                "agent-remote-node",
                "internal/runtime/snapshot_test.go",
                "TestProbeEgoBrowserExecutionAdmissionIsIndependentFromEnrollment",
                "enrollment denial incorrectly closed execution",
                "execution denial was not fail-closed",
            ),
        ),
    ),
    (
        "certificate-pin-comes-from-verified-leaf-not-manifest",
        (
            evidence(
                "agent-remote",
                "tests/test_promote_ego_browser_release.py",
                "test_prepare_rejects_each_trust_boundary_without_mutating_root",
                '"certificate": lambda args, root:',
                "assert root_manifest.read_bytes() == before, label",
            ),
            evidence(
                "agent-remote-ego-browser",
                "tests/release_scripts_test.sh",
                "community verifier binds the signer pin to leaf DER bytes",
                'cp "$FAKE_CODESIGN_LEAF_DER" "${prefix}0"',
                'cp "$FAKE_CODESIGN_CHAIN_DER" "${prefix}1"',
                '"$leaf_package" "$chain_digest" "$current_version"',
            ),
        ),
    ),
    (
        "setup-and-repair-do-not-change-release",
        (
            evidence(
                "agent-remote-cli",
                "src/ego_browser.rs",
                "existing_bridge_setup_selects_only_the_current_release_installer",
                "BridgeInstallerSource::Installed(installer)",
            ),
            evidence(
                "agent-remote-cli",
                "tests/cli_contract.rs",
                "ego_browser_routine_repair_reuses_exact_trust_without_confirmation",
                'check_retained_device_registration("repair", "active", false);',
                'if matches!(operation, "repair" | "setup")',
                'fs::read_to_string(installer_log).unwrap(),',
                'format!("--{operation}\\n")',
            ),
        ),
    ),
    (
        "remove-preserves-reusable-state-until-forget",
        (
            evidence(
                "agent-remote-ego-browser",
                "integration-tests/real-relay-e2e.sh",
                "remove_then_forget_with_retained_release",
                'test -x "$release/bin/ego-browser-device"',
                'test -f "$device_home/ego-browser-policy.json"',
                'test ! -e "$device_home/ego-browser-credential.json"',
                '"purge-local --confirmed-revoked"',
            ),
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/lib.rs",
                "local_metadata_is_non_secret_and_runtime_retirement_preserves_identity",
                "load_identity(",
                ".is_ok());",
            ),
        ),
    ),
    (
        "origin-user-or-profile-change-requires-explicit-switch",
        (
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/main.rs",
                "ensure_rejects_a_retained_identity_on_a_different_server_origin",
                "origin change must require explicit switch-server",
                'assert_eq!(error.log_code(), "identity_origin_conflict");',
            ),
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/main.rs",
                "ensure_rejects_release_profile_change_without_migrating_identity",
                "Some(CredentialError::CompatibilityMismatch)",
                "ego-browser-pending-registration.json",
            ),
            evidence(
                "agent-remote-server",
                "tests/test_ego_browser_api.py",
                "test_ensure_rejects_an_identity_owned_by_another_user",
                'assert rejected.json()["error"]["code"] == "EGO_BROWSER_DEVICE_CONFLICT"',
                'assert second_owner_devices.json()["data"]["items"] == []',
            ),
        ),
    ),
    (
        "switch-server-does-not-reuse-old-origin-secrets",
        (
            evidence(
                "agent-remote-cli",
                "tests/cli_contract.rs",
                "switch_server_retries_only_the_incomplete_stage_and_preserves_operation_id",
                'assert_eq!(second_pending["operation_id"], operation_id);',
                'filter(|line| *line == "purge-local --confirmed-revoked")',
            ),
            evidence(
                "agent-remote-cli",
                "tests/cli_contract.rs",
                "switch_server_with_ensured_target_identity_only_finalizes",
                "Device Client was invoked during finalize-only recovery",
            ),
        ),
    ),
    (
        "trust-confirmation-is-bound-to-profile-and-pin",
        (
            evidence(
                "agent-remote-cli",
                "src/ego_browser.rs",
                "trust_confirmation_round_trips_as_owner_only_state",
                "assert_eq!(load_trust_confirmation(&paths).unwrap(), Some(confirmation));",
            ),
            evidence(
                "agent-remote-cli",
                "src/ego_browser.rs",
                "legacy_trust_confirmation_requires_the_exact_new_profile_tuple",
                "assert!(!trust_confirmation_matches(",
            ),
            evidence(
                "agent-remote-cli",
                "src/ego_browser.rs",
                "trust_confirmation_rejects_uppercase_or_wrong_pin",
                "load_trust_confirmation(&paths).is_err()",
            ),
        ),
    ),
    (
        "candidate-selection-and-requery-fail-closed",
        (
            evidence(
                "agent-remote-cli",
                "src/ego_browser.rs",
                "candidate_selection_fails_closed_without_tty_and_for_ambiguous_prefixes",
                "error_code=confirmation_required",
            ),
            evidence(
                "agent-remote-cli",
                "src/ego_browser.rs",
                "candidate_fingerprint_detects_requery_drift_before_claim",
                "assert!(!candidate_matches_selection(&selected, &drifted));",
            ),
        ),
    ),
    (
        "all-profile-policy-runtime-mismatch-closes-admission",
        (
            evidence(
                "agent-remote-ego-browser",
                "integration-tests/real-relay-e2e.sh",
                "mismatch_setup_closes_local_admission",
                'result["error_code"] == "compatibility_mismatch"',
                'admission["state"] == "closed"',
                "assert ensure_count == 2, ensure_count",
            ),
            evidence(
                "agent-remote-server",
                "tests/test_ego_browser_service.py",
                "test_profile_pin_drift_blocks_activation_renewal_ticket_and_reconnect",
                '"EGO_BROWSER_VERSION_MISMATCH"',
            ),
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/lib.rs",
                "policy_tamper_and_unsafe_permissions_fail_closed",
                "Err(CredentialError::PolicyInvalid)",
                "Err(CredentialError::UnsafePermissions)",
            ),
            evidence(
                "agent-remote-cli",
                "tests/cli_contract.rs",
                "ego_browser_setup_requires_exact_profile_trust_without_running_an_installer",
                'assert_eq!(admission["state"], "closed");',
                'assert!(admission["binding_id"].is_null());',
            ),
        ),
    ),
    (
        "production-rejects-development-and-maps-pin-fields",
        (
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/main.rs",
                "development_signer_sentinel_is_restricted_to_development_profiles",
                '"development".into()',
                ".is_err());",
            ),
            evidence(
                "agent-remote-ego-browser",
                "crates/device-client/src/tests/main.rs",
                "production_signer_requires_the_canonical_trust_pin",
                '"--signer-certificate-sha256".into()',
                "TRUSTED_COMMUNITY_SIGNER_CERTIFICATE_SHA256",
            ),
            evidence(
                "agent-remote-server",
                "tests/test_ego_browser_service.py",
                "test_signer_pin_never_accepts_missing_evidence",
                '"EGO_BROWSER_SIGNER_MISMATCH"',
            ),
        ),
    ),
    (
        "destructive-identity-actions-require-confirmation",
        (
            evidence(
                "agent-remote-cli",
                "tests/cli_contract.rs",
                "destructive_identity_commands_fail_closed_without_non_tty_confirmation",
                'assert_eq!(value["next_action"], "confirm_forget");',
                'assert_eq!(value["next_action"], "confirm_device_rotate");',
                'assert_eq!(value["next_action"], "confirm_switch_server");',
                '.join("ego-browser-pending-revocation.json")',
            ),
            evidence(
                "agent-remote-admin-web",
                "src/pages/console/EgoBrowserPage.test.tsx",
                "cancels destructive confirmation without submitting a mutation",
                "expect(requestMock).not.toHaveBeenCalled();",
                "expect(runAction).not.toHaveBeenCalled();",
            ),
        ),
    ),
    (
        "json-output-is-structured-and-content-free",
        (
            evidence(
                "agent-remote-cli",
                "tests/cli_contract.rs",
                "ego_browser_list_json_is_single_structured_content_free_document",
                'assert!(!rendered.contains("art_list-json-token"));',
                'assert!(!rendered.contains("Cookie"));',
                'assert!(!rendered.contains("private-key-material-do-not-leak"));',
            ),
            evidence(
                "agent-remote-cli",
                "tests/cli_contract.rs",
                "ego_browser_requests_json_is_single_structured_content_free_document",
                'assert_eq!(value["command"], "requests");',
                '"ciphertext"',
                '"private-key-material-do-not-leak"',
                "&server_url,",
            ),
            evidence(
                "agent-remote-cli",
                "src/main.rs",
                "json_error_projection_is_stable_and_secret_free",
                '.contains("do-not-leak"));',
            ),
        ),
    ),
)


def read_text(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"required source is not a regular file: {path}")
    return path.read_text(encoding="utf-8")


def read_json_object(path: Path) -> dict[str, object]:
    value = json.loads(read_text(path))
    if not isinstance(value, dict):
        raise ValueError(f"required JSON document is not an object: {path}")
    return value


def object_field(value: dict[str, object], name: str, label: str) -> dict[str, object]:
    field = value.get(name)
    if not isinstance(field, dict):
        raise ValueError(f"{label} is not an object")
    return field


def string_field(value: dict[str, object], name: str, label: str) -> str:
    field = value.get(name)
    if not isinstance(field, str):
        raise ValueError(f"{label} is not a string")
    return field


def require_fragments(text: str, fragments: tuple[str, ...], label: str) -> None:
    missing = [fragment for fragment in fragments if fragment not in text]
    if missing:
        raise ValueError(f"{label} is missing: {', '.join(missing)}")


def require_fields(actual: set[str], expected: set[str], label: str) -> None:
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"{label} fields differ; missing={missing}, extra={extra}")


def reject_patterns(text: str, patterns: tuple[str, ...], label: str) -> None:
    for pattern in patterns:
        if re.search(pattern, text, re.MULTILINE | re.DOTALL):
            raise ValueError(f"{label} contains forbidden lifecycle pattern: {pattern}")


def braced_block(text: str, start_pattern: str, label: str) -> str:
    match = re.search(start_pattern, text, re.MULTILINE)
    if match is None:
        raise ValueError(f"{label} declaration is missing")
    start = text.find("{", match.start(), match.end())
    if start < 0:
        raise ValueError(f"{label} opening brace is missing")
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : index]
    raise ValueError(f"{label} closing brace is missing")


def rust_struct_fields(text: str, name: str) -> set[str]:
    block = braced_block(
        text,
        rf"\bstruct\s+{re.escape(name)}(?:\s*<[^{{>]+>)?\s*\{{",
        f"Rust struct {name}",
    )
    return set(
        re.findall(r"^\s*(?:pub\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*:", block, re.MULTILINE)
    )


def typescript_type_fields(text: str, name: str) -> set[str]:
    block = braced_block(
        text,
        rf"\b(?:export\s+)?type\s+{re.escape(name)}\s*=\s*\{{",
        f"TypeScript type {name}",
    )
    return set(re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\??\s*:", block, re.MULTILINE))


def go_struct_json_fields(text: str, name: str) -> set[str]:
    block = braced_block(
        text,
        rf"\btype\s+{re.escape(name)}\s+struct\s*\{{",
        f"Go struct {name}",
    )
    return set(re.findall(r'`json:"([^",]+)', block))


def python_tree(text: str, path: Path) -> ast.Module:
    try:
        return ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        raise ValueError(f"cannot parse Python source {path}: {exc}") from exc


def python_class(tree: ast.Module, name: str) -> ast.ClassDef:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    raise ValueError(f"Python class {name} is missing")


def python_function(
    tree: ast.Module, name: str
) -> ast.FunctionDef | ast.AsyncFunctionDef:
    matches = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == name
    ]
    if len(matches) != 1:
        raise ValueError(f"Python function {name} count is {len(matches)}; expected 1")
    return matches[0]


def python_function_source(
    text: str, node: ast.FunctionDef | ast.AsyncFunctionDef
) -> str:
    if node.end_lineno is None:
        raise ValueError(f"Python function {node.name} has no source extent")
    return "\n".join(text.splitlines()[node.lineno - 1 : node.end_lineno])


def python_function_references(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
) -> set[str]:
    return {
        node.attr for node in ast.walk(function) if isinstance(node, ast.Attribute)
    } | {node.id for node in ast.walk(function) if isinstance(node, ast.Name)}


def reject_python_function_references(
    tree: ast.Module,
    function_names: tuple[str, ...],
    forbidden: set[str],
    label: str,
) -> None:
    for name in function_names:
        function = python_function(tree, name)
        references = python_function_references(function)
        rejected = sorted(references & forbidden)
        if rejected:
            raise ValueError(
                f"{label} {name} depends on forbidden enrollment gate(s): {rejected}"
            )


def python_class_fields(tree: ast.Module, name: str) -> set[str]:
    return {
        node.target.id
        for node in python_class(tree, name).body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }


def python_field_default_name(
    tree: ast.Module, class_name: str, field_name: str
) -> str:
    for node in python_class(tree, class_name).body:
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == field_name
            and isinstance(node.value, ast.Call)
        ):
            for keyword in node.value.keywords:
                if keyword.arg == "default" and isinstance(keyword.value, ast.Name):
                    return keyword.value.id
    raise ValueError(f"{class_name}.{field_name} has no named Field default")


def python_annotation_strings(
    tree: ast.Module, class_name: str, field_name: str
) -> set[str]:
    for node in python_class(tree, class_name).body:
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == field_name
        ):
            return {
                value.value
                for value in ast.walk(node.annotation)
                if isinstance(value, ast.Constant) and isinstance(value.value, str)
            }
    raise ValueError(f"{class_name}.{field_name} annotation is missing")


def python_string_constant(tree: ast.Module, name: str) -> str:
    for node in tree.body:
        targets: list[ast.expr] = []
        value: ast.expr | None = None
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value = node.value
        if (
            value is not None
            and any(
                isinstance(target, ast.Name) and target.id == name for target in targets
            )
            and isinstance(value, ast.Constant)
            and isinstance(value.value, str)
        ):
            return value.value
    raise ValueError(f"Python string constant {name} is missing")


def named_string(text: str, pattern: str, label: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if match is None:
        raise ValueError(f"{label} constant is missing")
    return match.group(1)


def require_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise ValueError(f"{label} is {actual!r}; expected {expected!r}")


def validate_section_10_evidence(*, require_components: bool) -> None:
    if len(SECTION_10_EVIDENCE_MATRIX) != 31:
        raise ValueError(
            "section 10 evidence matrix must contain exactly 31 scenarios; "
            f"found {len(SECTION_10_EVIDENCE_MATRIX)}"
        )
    identifiers = [identifier for identifier, _references in SECTION_10_EVIDENCE_MATRIX]
    if len(identifiers) != len(set(identifiers)) or any(
        not value for value in identifiers
    ):
        raise ValueError(
            "section 10 evidence scenario identifiers must be unique and non-empty"
        )

    compound_scenarios = {
        "repeat-setup-keeps-one-device",
        "concurrent-setup-keeps-one-identity",
        "bridge-upgrade-preserves-device-identity",
        "expired-credential-refreshes-without-new-device",
        "register-and-ensure-share-one-idempotent-operation",
        "device-rotate-reuses-pending-key-across-retries",
        "lost-credential-commit-reuses-pending-identity",
        "first-concurrent-registration-serializes-missing-row",
        "remove-retires-runtime-and-forget-purges-identity",
        "execution-admission-is-independent-and-fail-closed",
        "certificate-pin-comes-from-verified-leaf-not-manifest",
        "origin-user-or-profile-change-requires-explicit-switch",
        "all-profile-policy-runtime-mismatch-closes-admission",
        "production-rejects-development-and-maps-pin-fields",
    }
    matrix = dict(SECTION_10_EVIDENCE_MATRIX)
    for identifier in compound_scenarios:
        repositories = {reference.repository for reference in matrix[identifier]}
        if len(repositories) < 2:
            raise ValueError(
                f"compound section 10 scenario lacks cross-repository evidence: {identifier}"
            )

    json_references = matrix["json-output-is-structured-and-content-free"]
    if not any(
        reference.repository == "agent-remote-cli"
        and reference.test
        == "ego_browser_requests_json_is_single_structured_content_free_document"
        for reference in json_references
    ):
        raise ValueError(
            "section 10 JSON evidence must cover the successful requests command"
        )

    for identifier, references in SECTION_10_EVIDENCE_MATRIX:
        if not references:
            raise ValueError(f"section 10 scenario has no evidence: {identifier}")
        for reference in references:
            repository_root = REPOSITORY_PATHS.get(reference.repository)
            if repository_root is None:
                raise ValueError(
                    f"section 10 evidence names an unknown repository: {reference.repository}"
                )
            relative = Path(reference.path)
            if relative.is_absolute() or ".." in relative.parts or not reference.path:
                raise ValueError(
                    f"section 10 evidence path is unsafe: {reference.repository}/{reference.path}"
                )
            if not reference.test or not reference.assertions:
                raise ValueError(
                    f"section 10 evidence lacks a test or assertion: {identifier}"
                )
            if not repository_root.is_dir():
                if require_components:
                    raise ValueError(
                        f"section 10 evidence repository is missing: {reference.repository}"
                    )
                continue
            source = read_text(repository_root / relative)
            require_fragments(
                source,
                (reference.test, *reference.assertions),
                f"section 10 evidence {identifier} ({reference.repository}/{reference.path})",
            )


def validate_lifecycle_document(component: dict[str, object]) -> None:
    text = read_text(DOC)
    version = component["version"]
    pin = component["signer_certificate_sha256"]
    required_fragments = (
        "agent-remote ego-browser setup",
        "agent-remote ego-browser connect",
        "agent-remote ego-browser forget-this-mac",
        "POST /api/v1/ego-browser/devices/ensure",
        "Idempotency-Key",
        "device_generation",
        "binding_generation",
        "signer_certificate_sha256",
        "enrollment enabled",
        "server execution admission",
        "local admission",
        "pending_revocation",
        "exchange_id",
        "--join-code-stdin",
        "installed",
        "enabled",
        "registered",
        "available",
        "connected",
        "P0",
        "P1",
        "P2",
        "P3",
    )
    require_fragments(text, required_fragments, "lifecycle contract")

    if not isinstance(version, str):
        raise ValueError("Bridge release version is not a string")
    if version not in text and "release-manifest.json" not in text:
        raise ValueError(
            f"lifecycle contract does not identify release facts for Bridge {version}"
        )
    if pin and "release-manifest.json" not in text:
        raise ValueError(
            "lifecycle contract must defer certificate facts to the manifest"
        )
    if "EXPECTED_64_HEX_DIGEST" not in text:
        raise ValueError("lifecycle contract must document the legacy digest mapping")
    if "目标入口示例，不代表当前二进制已经支持" not in text:
        raise ValueError(
            "lifecycle contract must distinguish target and shipped interfaces"
        )
    section_10 = text.split("## 10.", 1)
    if len(section_10) != 2:
        raise ValueError("lifecycle contract section 10 is missing")
    section_10_body = section_10[1].split("## 11.", 1)[0]
    acceptance_rows = re.findall(r"(?m)^- ", section_10_body)
    if len(acceptance_rows) != 31:
        raise ValueError(
            "lifecycle contract section 10 must contain exactly 31 acceptance rows; "
            f"found {len(acceptance_rows)}"
        )


def validate_root_documents() -> None:
    architecture = read_text(ROOT / "docs" / "agent-remote-architecture.md")
    deployment = read_text(ROOT / "docs" / "ego-browser-bridge-deployment.md")
    shared = (
        "`installed`",
        "`enabled`",
        "`registered`",
        "`available`",
        "`connected`",
        "Server execution admission",
        "local admission",
        "`exchange_id`",
        "--join-code-stdin",
        "`pause`",
        "`stop`",
        "`EGB0\\n`",
    )
    require_fragments(architecture, shared, "root architecture")
    require_fragments(deployment, shared, "Bridge deployment runbook")
    require_fragments(
        architecture,
        ("不得把本机 `pause` 自动升级为远端 `stop`", "后续必须重新 `connect`"),
        "root architecture admission boundary",
    )
    require_fragments(
        deployment,
        ("must not turn a local `pause` into a remote `stop`", "fresh `connect`"),
        "Bridge deployment admission boundary",
    )


def validate_cli(path: Path) -> None:
    main = read_text(path / "src" / "main.rs")
    api = read_text(path / "src" / "api.rs")
    state = read_text(path / "src" / "node_install_state.rs")
    node_release = read_text(path / "src" / "node_release.rs")
    release_dependencies = read_json_object(path / "release-dependencies.json")
    ego = read_text(path / "src" / "ego_browser.rs")
    contracts = read_text(path / "tests" / "cli_contract.rs")

    require_fields(
        rust_struct_fields(state, "NodeInstallExchangeState"),
        {
            "version",
            "server_url",
            "node_id",
            "node_fingerprint_sha256",
            "exchange_id",
            "enable_ego_browser",
            "release_version",
            "release_target",
            "release_sha256",
            "stage",
            "created_at_unix",
            "expires_at",
        },
        "CLI persisted Node exchange",
    )
    require_fragments(
        state,
        (
            "OsRng.fill_bytes",
            "options.mode(0o600)",
            "libc::O_NOFOLLOW",
            "metadata.nlink() != 1",
            "fs::rename(&temporary, &destination)",
            "sync_directory(paths.home())",
        ),
        "CLI owner-only Node exchange state",
    )
    first_save = main.find("node_install_state::save(&paths")
    first_issue = main.find(".issue_node_join_code(")
    if first_save < 0 or first_issue < 0 or first_save > first_issue:
        raise ValueError("CLI must persist exchange_id before issuing a Node join code")
    require_fragments(
        main,
        (
            "posix_shell_quote(exchange_id)",
            'arguments.push_str(" --join-code-stdin")',
            "stdin.write_all(join_code.as_bytes())",
            ".revoke_node_join_code(&token, &node_id, &exchange.exchange_id)",
            "transfer_node_release(&ssh, user, host, port, &release)",
            "install_staged_node_release(&ssh, user, host, port, &release)",
        ),
        "CLI Node join transport",
    )
    transfer = main.find("transfer_node_release(&ssh, user, host, port, &release)")
    install = main.find("install_staged_node_release(&ssh, user, host, port, &release)")
    if (
        transfer < 0
        or install < 0
        or first_issue < 0
        or not transfer < install < first_issue
    ):
        raise ValueError(
            "CLI must authenticate, transfer, and install Node before issuing a code"
        )
    managed_node_version = string_field(
        object_field(release_dependencies, "node", "CLI managed Node release"),
        "version",
        "CLI managed Node release version",
    )
    certified_node_version = release_component("agent-remote-node")["version"]
    require_equal(managed_node_version, certified_node_version, "CLI managed Node release")
    node_version_path = COMPONENT_PATHS["agent-remote-node"] / "VERSION"
    if node_version_path.is_file():
        require_equal(
            managed_node_version,
            read_text(node_version_path).strip(),
            "CLI managed Node release",
        )
    require_fragments(
        node_release,
        (
            "pub use crate::managed_releases::MANAGED_NODE_VERSION;",
            "verify_checksum_file(&checksum, &archive_name, &sha256)",
            "verify_sigstore_with_program(cosign, &archive, &sigstore)",
            "refs/tags/v{MANAGED_NODE_VERSION}",
            "metadata.nlink() != 1",
        ),
        "CLI authenticated Node release",
    )
    require_fields(
        rust_struct_fields(api, "NodeJoinCodeRequest"),
        ISSUE_REQUEST_FIELDS,
        "CLI Node join-code issue request",
    )
    require_fields(
        rust_struct_fields(api, "NodeJoinCodeRevokeRequest"),
        REVOKE_REQUEST_FIELDS,
        "CLI Node join-code revoke request",
    )
    require_fields(
        rust_struct_fields(api, "NodeJoinCodeData"),
        ISSUE_DATA_FIELDS,
        "CLI Node join-code issue response data",
    )
    require_fragments(
        api,
        ("Revoked,", "Consumed,", "Missing,"),
        "CLI Node join-code revoke states",
    )
    require_fragments(
        contracts,
        (
            "node_install_persists_exchange_id_and_keeps_join_code_on_ssh_stdin",
            "node_install_recovers_consumed_exchange_without_reissuing_or_reusing_code",
            'assert_eq!(issue["exchange_id"], exchange_id)',
            'assert!(arguments.contains("--join-code-stdin"))',
            "assert!(!arguments.contains(join_code))",
            'format!("{join_code}\\n")',
        ),
        "CLI Node join integration contracts",
    )
    require_fragments(
        ego,
        (
            "let enabled = installed;",
            '"registered": serde_json::Value::Null',
            "status_projection_requires_local_installation_and_ready_supervisor",
            "status_registration_requires_the_exact_local_device_and_origin",
            "status_connection_ignores_unrelated_or_stale_server_bindings",
            "load_local_device_metadata(paths)?",
            "metadata.server_url == server_url",
            "device.id == metadata.device_id",
            "device_generation(device) == Some(metadata.device_generation)",
            "binding.id == binding_id",
            "binding_generation(binding) == expected_generation",
            'binding.lease_health == "healthy"',
        ),
        "CLI five-state projection",
    )
    reject_patterns(
        ego,
        (
            r"\blet\s+registered\s*=\s*devices\s*\.\s*iter\(\)\s*\.\s*any",
            r"\blet\s+available\s*=\s*[^;]{0,1000}\benrollment\b[^;]*;",
        ),
        "CLI local status projection",
    )
    setup_block = braced_block(
        ego,
        r"\basync\s+fn\s+setup\b[^{]*\{",
        "CLI ego-browser setup",
    )
    reject_patterns(
        setup_block,
        (
            r"\bclaim\s*\(",
            r'OsString::from\(\s*"claim"\s*\)',
            r"\.claim_ego_browser",
            r"\bconnect\s*\(",
        ),
        "CLI ego-browser setup",
    )
    reject_legacy_state_formulas(main + "\n" + ego, "CLI lifecycle source")


def validate_node(path: Path) -> None:
    main = read_text(path / "cmd" / "agent-remote-node" / "main.go")
    api = read_text(path / "internal" / "api" / "client.go")
    artifact = read_text(path / "internal" / "egobrowserartifact" / "artifact.go")
    generated_policy = read_text(
        path / "internal" / "egobrowserartifact" / "release_policy_generated.go"
    )
    release_dependencies = read_json_object(path / "release-dependencies.json")
    if release_dependencies.get("schema_version") != 4:
        raise ValueError("Node release dependency schema is unsupported")
    skill_source = read_json_object(path / "ego-browser-skill-source.json")
    broker = read_text(path / "internal" / "egobrowser" / "broker.go")
    snapshot = read_text(path / "internal" / "runtime" / "snapshot.go")

    require_fragments(
        main,
        (
            'fs.Bool("join-code-stdin"',
            "io.LimitReader(os.Stdin, 4097)",
            "JoinCode:          joinCode",
            "ExchangeID:        *exchangeID",
            "persisted.ExchangeID",
            "unix.O_NOFOLLOW",
            "stat.Nlink != 1",
            "unix.Renameat",
        ),
        "Node stdin join and owner-only recovery",
    )
    reject_patterns(
        main,
        (
            r'fs\.String\(\s*"join-code(?:"|-)',
            r"os\.(?:Getenv|LookupEnv)\([^\n]*(?:JOIN|join)[^\n]*(?:CODE|code)",
        ),
        "Node join-code source",
    )
    require_fields(
        go_struct_json_fields(main, "joinExchangeState"),
        {"version", "exchange_id", "server_url", "node_id", "created_at"},
        "Node persisted exchange state",
    )
    require_fields(
        go_struct_json_fields(api, "JoinCodeExchangeRequest"),
        EXCHANGE_REQUEST_FIELDS,
        "Node join-code exchange request",
    )
    require_fields(
        go_struct_json_fields(api, "JoinCodeExchangeResponse"),
        EXCHANGE_DATA_FIELDS | {"data", "request_id"},
        "Node join-code exchange response",
    )
    probe = braced_block(
        snapshot,
        r"\bfunc\s+probeEgoBrowserWithVerifier\b[^\{]*\{",
        "Node ego-browser capability probe",
    )
    assignment = re.search(r"NodeExecutionAllowed\s*=\s*([^\n]+)", probe)
    if assignment is None:
        raise ValueError("Node capability probe does not assign node_execution_allowed")
    require_equal(
        assignment.group(1).split("//", 1)[0].strip(),
        "config.ServerExecutionAdmission",
        "Node execution admission formula",
    )
    reject_patterns(
        probe,
        (
            r"NodeExecutionAllowed\s*=\s*[^\n]*(?:Enrollment|enrollment)",
            r"if\s+[^\n]*(?:Enrollment|enrollment)[^\n]*NodeExecutionAllowed",
        ),
        "Node execution admission formula",
    )

    component = browser_component()
    wrapper_policy = object_field(
        release_dependencies, "ego_browser_wrapper", "Node wrapper release policy"
    )
    candidate_wrapper_version = string_field(
        wrapper_policy, "version", "Node wrapper release version"
    )
    candidate_protocol_version = string_field(
        wrapper_policy, "protocol_version", "Node wrapper protocol version"
    )
    require_equal(candidate_wrapper_version, component["version"], "Node Bridge release")
    require_equal(
        string_field(wrapper_policy, "repository", "Node wrapper repository"),
        component["repository"],
        "Node wrapper repository",
    )
    require_equal(
        string_field(
            wrapper_policy, "release_workflow", "Node wrapper release workflow"
        ),
        component["release_workflow"],
        "Node wrapper release workflow",
    )
    require_equal(
        candidate_protocol_version,
        component["protocol_version"],
        "Node Bridge protocol",
    )
    bridge_path = COMPONENT_PATHS["agent-remote-ego-browser"]
    if bridge_path.is_dir():
        bridge_cargo = tomllib.loads(read_text(bridge_path / "Cargo.toml"))
        require_equal(
            candidate_wrapper_version,
            bridge_cargo.get("workspace", {}).get("package", {}).get("version"),
            "Node wrapper release version",
        )
    node_source_version = read_text(path / "VERSION").strip()
    certified_node_version = release_component("agent-remote-node")["version"]
    require_equal(node_source_version, certified_node_version, "Node source release")
    require_fragments(
        read_text(path / "docs" / "ego-browser-artifacts.md"),
        (
            f"release `{candidate_wrapper_version}`",
            "`release_published=false`",
            "`production_ready=false`",
        ),
        "Node Bridge release boundary",
    )
    require_fragments(
        artifact,
        (
            "config.WrapperVersion != PinnedWrapperVersion",
            "manifest.Version != OfficialSkillVersion",
            "manifest.UpstreamCommit != OfficialSkillSourceCommit",
            "manifest.TreeSHA256 != OfficialSkillTreeSHA256",
        ),
        "Node generated release policy consumers",
    )
    generated_fields = (
        ("PinnedWrapperVersion", candidate_wrapper_version, "Node wrapper"),
        (
            "PinnedProtocolVersion",
            candidate_protocol_version,
            "Node Bridge protocol",
        ),
        (
            "OfficialSkillName",
            string_field(skill_source, "name", "Node Skill name"),
            "Node Skill name",
        ),
        (
            "OfficialSkillVersion",
            string_field(skill_source, "version", "Node Skill version"),
            "Node Skill version",
        ),
        (
            "OfficialSkillUpstreamRepository",
            string_field(
                skill_source, "upstream_repository", "Node Skill upstream repository"
            ),
            "Node Skill upstream repository",
        ),
        (
            "OfficialSkillSourceCommit",
            string_field(skill_source, "upstream_commit", "Node Skill commit"),
            "Node Skill commit",
        ),
        (
            "OfficialSkillDocumentSHA256",
            string_field(
                skill_source, "skill_document_sha256", "Node Skill document digest"
            ),
            "Node Skill document digest",
        ),
        (
            "OfficialSkillTreeSHA256",
            string_field(skill_source, "tree_sha256", "Node Skill tree digest"),
            "Node Skill tree digest",
        ),
    )
    for constant, expected, label in generated_fields:
        require_equal(
            named_string(
                generated_policy,
                rf'\b{constant}\s*=\s*"([^"]+)"',
                label,
            ),
            expected,
            label,
        )
    require_equal(
        string_field(skill_source, "version", "Node Skill version"),
        component["skill_version"],
        "Node Skill version",
    )
    require_equal(
        string_field(skill_source, "upstream_commit", "Node Skill commit"),
        component["skill_commit"],
        "Node Skill commit",
    )
    require_equal(
        string_field(skill_source, "tree_sha256", "Node Skill tree digest"),
        component["skill_tree_sha256"],
        "Node Skill tree digest",
    )
    require_fragments(
        broker,
        ("ProtocolVersion = egobrowserartifact.PinnedProtocolVersion",),
        "Node generated protocol consumer",
    )


def validate_server(path: Path) -> None:
    schemas_path = path / "src" / "agent_remote_server" / "schemas" / "nodes.py"
    schemas = read_text(schemas_path)
    tree = python_tree(schemas, schemas_path)
    expected = {
        "NodeJoinCodeIssueRequest": ISSUE_REQUEST_FIELDS,
        "NodeJoinCodeIssueData": ISSUE_DATA_FIELDS,
        "NodeJoinCodeRevokeRequest": REVOKE_REQUEST_FIELDS,
        "NodeJoinCodeRevokeData": REVOKE_DATA_FIELDS,
        "NodeJoinCodeExchangeRequest": EXCHANGE_REQUEST_FIELDS,
        "NodeJoinCodeExchangeData": EXCHANGE_DATA_FIELDS,
    }
    for class_name, fields in expected.items():
        require_fields(
            python_class_fields(tree, class_name), fields, f"Server {class_name}"
        )
    require_fragments(
        schemas,
        ('Literal["revoked", "consumed", "missing"]', "default=900, ge=60, le=1800"),
        "Server Node join-code schema",
    )

    nodes_api = read_text(path / "src" / "agent_remote_server" / "api" / "nodes.py")
    node_api = read_text(path / "src" / "agent_remote_server" / "api" / "node_api.py")
    require_fragments(
        nodes_api,
        (
            '@router.post("/{node_id}/join-code", response_model=NodeJoinCodeIssueResponse)',
            '@router.post("/{node_id}/join-code/revoke", response_model=NodeJoinCodeRevokeResponse)',
            "admin: Annotated[User, Depends(require_admin)]",
            "exchange_id=payload.exchange_id",
        ),
        "Server administrator join-code API",
    )
    require_fragments(
        node_api,
        (
            '@router.post("/join-code/exchange", response_model=NodeJoinCodeExchangeResponse)',
            "join_code=payload.join_code",
            "exchange_id=payload.exchange_id",
            "ego_browser_enabled_intent=result.ego_browser_enabled_intent",
        ),
        "Server Node join-code exchange API",
    )

    config_path = path / "src" / "agent_remote_server" / "config.py"
    config_text = read_text(config_path)
    config_tree = python_tree(config_text, config_path)
    policy_path = (
        path / "src" / "agent_remote_server" / "ego_browser" / "release_policy.py"
    )
    policy_text = read_text(policy_path)
    policy_tree = python_tree(policy_text, policy_path)
    component = browser_component()
    field_map = {
        "ego_browser_expected_wrapper_version": (
            "EGO_BROWSER_WRAPPER_VERSION",
            "version",
        ),
        "ego_browser_expected_skill_version": (
            "EGO_BROWSER_SKILL_VERSION",
            "skill_version",
        ),
        "ego_browser_expected_skill_tree_sha256": (
            "EGO_BROWSER_SKILL_TREE_SHA256",
            "skill_tree_sha256",
        ),
        "ego_browser_expected_skill_commit": (
            "EGO_BROWSER_SKILL_COMMIT",
            "skill_commit",
        ),
        "ego_browser_expected_local_runtime_version": (
            "EGO_BROWSER_LOCAL_RUNTIME_VERSION",
            "local_ego_browser_runtime_version",
        ),
        "ego_browser_expected_protocol_version": (
            "EGO_BROWSER_PROTOCOL_VERSION",
            "protocol_version",
        ),
    }
    for field, (constant, manifest_field) in field_map.items():
        require_equal(
            python_field_default_name(config_tree, "Settings", field),
            constant,
            f"Server {field} policy source",
        )
        require_equal(
            python_string_constant(policy_tree, constant),
            component[manifest_field],
            f"Server {constant}",
        )
    profiles = python_annotation_strings(
        config_tree, "Settings", "ego_browser_expected_release_profile"
    )
    if component["profile"] not in profiles:
        raise ValueError("Server does not accept the release-manifest Bridge profile")

    release_path = (
        path / "src" / "agent_remote_server" / "device_control" / "release.py"
    )
    release_text = read_text(release_path)
    require_fragments(
        release_text,
        (
            "EGO_BROWSER_LOCAL_RUNTIME_VERSION as EGO_BROWSER_RUNTIME_VERSION",
            "component.skill_version != EGO_BROWSER_SKILL_VERSION",
            "component.skill_commit != EGO_BROWSER_SKILL_COMMIT",
            "component.protocol_version != EGO_BROWSER_PROTOCOL_VERSION",
            'profile: Literal["community-local-trust"]',
        ),
        "Server release profile validation",
    )
    service_root = path / "src" / "agent_remote_server" / "services" / "ego_browser"
    execution_functions = {
        service_root / "bindings.py": ("list_node_bindings", "claim"),
        service_root / "lifecycle.py": (
            "connected",
            "renew",
            "renew_for_node",
            "resume",
        ),
        service_root / "relay.py": ("relay_claims_are_current", "issue_relay_ticket"),
        service_root / "admission.py": ("admit_outer_envelope",),
    }
    forbidden_execution_gates = {
        "_require_enrollment",
        "_require_enabled",
        "ego_browser_enrollment_enabled",
    }
    for execution_path, function_names in execution_functions.items():
        execution_text = read_text(execution_path)
        execution_tree = python_tree(execution_text, execution_path)
        reject_python_function_references(
            execution_tree,
            function_names,
            forbidden_execution_gates,
            f"Server execution path {execution_path.name}",
        )

    direct_execution_checks = {
        service_root / "bindings.py": ("list_node_bindings", "claim"),
        service_root / "lifecycle.py": (
            "connected",
            "renew",
            "renew_for_node",
            "resume",
        ),
        service_root / "relay.py": ("issue_relay_ticket",),
    }
    for execution_path, function_names in direct_execution_checks.items():
        execution_text = read_text(execution_path)
        execution_tree = python_tree(execution_text, execution_path)
        for function_name in function_names:
            references = python_function_references(
                python_function(execution_tree, function_name)
            )
            if "_require_execution" not in references:
                raise ValueError(
                    f"Server execution path {execution_path.name} {function_name} "
                    "does not require execution admission"
                )

    devices_path = service_root / "devices.py"
    devices_text = read_text(devices_path)
    devices_tree = python_tree(devices_text, devices_path)
    challenge_source = python_function_source(
        devices_text, python_function(devices_tree, "issue_proof_challenge")
    )
    require_fragments(
        challenge_source,
        (
            'enrollment_operations = {"register_device", "device_rotate", "confirm_allowlist"}',
            '"claim_binding",',
            '"connect_binding",',
            '"renew_binding",',
            '"resume_binding",',
            '"issue_relay_ticket",',
            "if operation in enrollment_operations:",
            "self._require_enrollment()",
            "elif operation in execution_operations:",
            "self._require_execution()",
        ),
        "Server PoP challenge admission split",
    )

    ego_api_path = path / "src" / "agent_remote_server" / "api" / "ego_browser.py"
    ego_api = read_text(ego_api_path)
    ego_api_tree = python_tree(ego_api, ego_api_path)
    reject_python_function_references(
        ego_api_tree,
        ("ego_browser_relay",),
        forbidden_execution_gates,
        "Server relay WebSocket",
    )
    status_source = python_function_source(
        ego_api, python_function(ego_api_tree, "get_ego_browser_status")
    )
    reject_patterns(
        status_source,
        (r"\bavailable\b[^\n]{0,300}ego_browser_enrollment_enabled",),
        "Server available projection",
    )
    reject_legacy_state_formulas(ego_api, "Server lifecycle API")


def validate_admin(path: Path) -> None:
    page = read_text(path / "src" / "pages" / "console" / "EgoBrowserPage.tsx")
    tests = read_text(path / "src" / "pages" / "console" / "EgoBrowserPage.test.tsx")
    types = read_text(path / "src" / "types.ts")
    require_fields(
        typescript_type_fields(types, "NodeJoinCode"),
        ISSUE_DATA_FIELDS,
        "Admin Node join-code response",
    )
    require_fragments(
        page,
        (
            "useState<Record<string, boolean>>({})",
            "ego_browser_enabled: joinCodeEnableIntent[node.id] ?? false",
            'type="checkbox"',
            "checked={joinCodeEnableIntent[node.id] ?? false}",
            "[node.id]: event.target.checked",
            'me.role === "admin"',
        ),
        "Admin explicit Node join intent",
    )
    require_fragments(
        tests,
        (
            "expect(enableIntent).not.toBeChecked()",
            "ego_browser_enabled: false",
            "ego_browser_enabled: true",
            "hides them from users",
            "shows healthy Server records without claiming local readiness",
            'expect(within(summary).getByText("Not reported")).toBeVisible()',
            'expect(within(summary).getByText("agent-remote ego-browser status")).toBeVisible()',
        ),
        "Admin Node join intent tests",
    )
    reject_patterns(
        page,
        (
            r"/(?:ensure|register|rotate)\b",
            r"/(?:claim|connect|resume)\b",
        ),
        "Admin local-only lifecycle actions",
    )
    reject_legacy_state_formulas(page, "Admin lifecycle page")


def validate_ego_browser(path: Path) -> None:
    architecture = read_text(path / "docs" / "architecture.md")
    security = read_text(path / "docs" / "security.md")
    shared = (
        "`installed`",
        "`enabled`",
        "`registered`",
        "`available`",
        "`connected`",
        "Server execution admission",
        "local admission",
        "`exchange_id`",
        "--join-code-stdin",
        "`pause`",
        "`stop`",
        "`EGB0\\n`",
    )
    require_fragments(architecture, shared, "Bridge architecture")
    require_fragments(security, shared, "Bridge security model")

    device_main = read_text(path / "crates" / "device-client" / "src" / "main.rs")
    device_tests = read_text(
        path / "crates" / "device-client" / "src" / "tests" / "main.rs"
    )
    peer = read_text(path / "crates" / "local-bridge" / "src" / "device_peer.rs")
    peer_tests = read_text(
        path / "crates" / "local-bridge" / "src" / "tests" / "main.rs"
    )
    require_fragments(
        device_main,
        ('b"EGB1\\n"', 'b"EGB0\\n"'),
        "Device Client local admission frames",
    )
    admission_closed = peer.split("Ok(DevicePeerHeartbeat::AdmissionClosed) => {", 1)
    if len(admission_closed) != 2:
        raise ValueError("Bridge explicit admission-close branch is missing")
    admission_closed_block = admission_closed[1].split("Err(error) => {", 1)[0]
    require_fragments(
        admission_closed_block,
        ("supervisor.revoke();", "DevicePeerObserverOutcome::AdmissionClosed"),
        "Bridge explicit admission-close branch",
    )
    reject_patterns(
        admission_closed_block,
        (r"stop_binding", r"clear_active_binding", r"\.stop\("),
        "Bridge explicit admission-close branch",
    )
    require_fragments(
        peer,
        (
            "fail_closed_device_peer_loss",
            "store.clear_active_binding()",
            "stop_binding().await",
        ),
        "Bridge unexpected peer-loss path",
    )
    require_fragments(
        peer_tests,
        (
            "intentional_admission_close_revokes_supervisor_without_remote_stop",
            "assert!(!stop_called.load",
            'store.load_active_binding("device-test").is_ok()',
        ),
        "Bridge admission-close regression test",
    )

    component = browser_component()
    cargo = tomllib.loads(read_text(path / "Cargo.toml"))
    candidate_version = cargo.get("workspace", {}).get("package", {}).get("version")
    require_equal(candidate_version, component["version"], "Bridge source release")
    require_fragments(
        read_text(path / "docs" / "release.md"),
        (
            f"`{candidate_version}`",
            "tag-bound release",
            "artifact-bound canaries",
        ),
        "Bridge release boundary",
    )
    require_fragments(
        device_main + "\n" + device_tests,
        (
            'Some(env!("CARGO_PKG_VERSION"))',
            "schema_four_profile_authenticates_only_the_compiled_bridge_version",
            "root_release_manifest(",
        ),
        "Bridge manifest fail-closed boundary",
    )
    require_equal(
        named_string(
            read_text(path / "crates" / "protocol" / "src" / "lib.rs"),
            r'\bREPLACED_COMMUNITY_PROFILE\s*:\s*&str\s*=\s*"([^"]+)"',
            "Bridge replaced profile",
        ),
        component["replaces_profile"],
        "Bridge replacement boundary",
    )
    protocol = read_text(path / "crates" / "protocol" / "src" / "lib.rs")
    rust_constants = {
        "PROTOCOL_VERSION": "protocol_version",
        "SUPPORTED_SKILL_VERSION": "skill_version",
        "EGO_LITE_INSTALLER_COMMIT": "skill_commit",
        "SUPPORTED_SKILL_TREE_SHA256": "skill_tree_sha256",
        "SUPPORTED_LOCAL_RUNTIME_VERSION": "local_ego_browser_runtime_version",
        "COMMUNITY_PROFILE_ID": "profile",
        "TRUSTED_COMMUNITY_SIGNER_CERTIFICATE_SHA256": "signer_certificate_sha256",
        "ADMISSION_POLICY_REF": "admission_policy_ref",
        "EGO_LITE_INSTALLER_SHA256": "ego_lite_installer_sha256",
    }
    for constant, manifest_field in rust_constants.items():
        require_equal(
            named_string(
                protocol,
                rf'\b{constant}\s*:\s*&str\s*=\s*"([^"]+)"',
                f"Bridge {constant}",
            ),
            component[manifest_field],
            f"Bridge {constant}",
        )
    require_fragments(
        device_main,
        (
            '("profile", COMMUNITY_PROFILE_ID)',
            '("credential_profile", "community_file")',
            '("protocol_version", PROTOCOL_VERSION)',
            '("skill_version", SUPPORTED_SKILL_VERSION)',
            '("skill_commit", EGO_LITE_INSTALLER_COMMIT)',
            '("skill_tree_sha256", SUPPORTED_SKILL_TREE_SHA256)',
            "SUPPORTED_LOCAL_RUNTIME_VERSION,",
            '("profile_id", COMMUNITY_PROFILE_ID)',
            '("bridge_protocol_version", PROTOCOL_VERSION)',
            '("admission_policy_ref", ADMISSION_POLICY_REF)',
            '("ego_lite_installer_commit", EGO_LITE_INSTALLER_COMMIT)',
            '("ego_lite_installer_sha256", EGO_LITE_INSTALLER_SHA256)',
            '("replaces_profile", REPLACED_COMMUNITY_PROFILE)',
        ),
        "Bridge root manifest policy mapping",
    )

    release_manifest_path = path / "scripts" / "release_manifest.py"
    release_manifest_text = read_text(release_manifest_path)
    release_manifest_tree = python_tree(release_manifest_text, release_manifest_path)
    release_constants = {
        "PROTOCOL": "protocol_version",
        "SKILL_VERSION": "skill_version",
        "LOCAL_RUNTIME_VERSION": "local_ego_browser_runtime_version",
    }
    for constant, manifest_field in release_constants.items():
        require_equal(
            python_string_constant(release_manifest_tree, constant),
            component[manifest_field],
            f"Bridge release manifest {constant}",
        )
    require_fragments(
        release_manifest_text,
        (f'"profile": "{component["profile"]}"',),
        "Bridge release manifest profile",
    )


def reject_legacy_state_formulas(text: str, label: str) -> None:
    reject_patterns(
        text,
        (
            r"\binstalled\s*=\s*(?:\w+\.)?devices\.length\s*>\s*0",
            r"\benabled\s*=\s*installed\s*&&[^;\n]{0,200}\b(?:registered|enrollment)\b",
            r"\benabled\s*=\s*(?:server_)?enrollment\b",
            r"\b(?:let|const)\s+available\s*=\s*[^;]{0,1000}\benrollment\b[^;]*;",
            r"\bavailable\s*=\s*[^\n]{0,300}\benrollment\b",
            r"\bavailable\s*=\s*(?:execute|execution)\s*;",
        ),
        label,
    )


_RELEASE_COMPONENTS: dict[str, object] | None = None


def release_component(name: str) -> dict[str, object]:
    if _RELEASE_COMPONENTS is None:
        raise ValueError("release manifest has not been loaded")
    component = _RELEASE_COMPONENTS.get(name)
    if not isinstance(component, dict):
        raise ValueError(f"release manifest component is invalid: {name}")
    return component


def browser_component() -> dict[str, object]:
    return release_component("agent-remote-ego-browser")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-components",
        action="store_true",
        help="fail unless all five sibling component repositories are present",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_release_manifest(MANIFEST)
    components = manifest["components"]
    if not isinstance(components, dict):
        raise ValueError("release manifest components are invalid")
    component = components["agent-remote-ego-browser"]
    if not isinstance(component, dict):
        raise ValueError("release manifest Bridge component is invalid")
    global _RELEASE_COMPONENTS
    _RELEASE_COMPONENTS = components

    validate_lifecycle_document(component)
    validate_root_documents()
    missing = [name for name, path in COMPONENT_PATHS.items() if not path.is_dir()]
    if args.require_components and missing:
        raise ValueError(
            "required sibling repositories are missing: " + ", ".join(missing)
        )
    validate_section_10_evidence(require_components=args.require_components)

    validators = {
        "agent-remote-cli": validate_cli,
        "agent-remote-node": validate_node,
        "agent-remote-server": validate_server,
        "agent-remote-admin-web": validate_admin,
        "agent-remote-ego-browser": validate_ego_browser,
    }
    checked: list[str] = []
    for name, validator in validators.items():
        path = COMPONENT_PATHS[name]
        if not path.is_dir():
            continue
        validator(path)
        checked.append(name)

    version = component["version"]
    suffix = (
        f"; checked siblings: {', '.join(checked)}"
        if checked
        else "; standalone root check"
    )
    print(f"ego-browser lifecycle contract OK (Bridge {version}{suffix})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, tomllib.TOMLDecodeError) as exc:
        print(f"ego-browser lifecycle contract invalid: {exc}", file=sys.stderr)
        raise SystemExit(1)
