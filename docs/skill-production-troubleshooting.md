# Skill production test findings and fixes

The 2026-09-27 test used CLI 0.2.32, Server 0.2.27 and Node 0.2.29. It confirmed library content and
configuration behavior, but did not establish actual model execution or next-session inheritance.

## Installation default correction

Skill management now defaults to enabled in the Server application, Compose templates, Node
configuration defaults and installer example. Explicit false overrides remain respected. The earlier
Node installer wrote false, so existing installations need a one-time false-to-true migration;
missing fields enable automatically. Native dependencies and storage probes remain mandatory.
The findings below describe the earlier releases, including their former default-off policy.

## Missing content volume

The deployed Compose file lacked the `skill-content` mount even though the release template already
contained it. Pulling an image does not merge Compose changes. The first file PUT therefore raised
`FileNotFoundError`; the plain HTTP 500 response appeared in CLI as `INVALID_SKILL_RESPONSE`.

The operator repaired the persistent mount, and real installation plus eight downloads across two
versions passed byte/SHA-256 checks. The Server fix now maps upload filesystem failures to HTTP 503
`CONTENT_STORAGE_UNAVAILABLE` without revealing private paths. A regression test removes the actual
volume parent, verifies the structured error, repairs the directory and completes the original
upload. It deliberately does not create an ephemeral parent to conceal a missing volume.

## Native capability report absent

Node 0.2.29 did not implement the Helper report or the Worker heartbeat field. This was an
unconditional rollout gate, not a stale heartbeat or incompatible CLI version. Server capability
rejection was correct. The fix adds a default-off Node `skill_manager_enabled` boolean and the
complete Native report through the actual Helper/Worker path. Native dependency checks, configured
runtime executable, private storage permissions, no-follow paths, non-overlap and disk reserves are
required; the actual volume is probed with a durable write/rename/read/remove cycle.

Upgrade both Node Worker and Helper to the fixed release, explicitly opt in in the deployed Node
config, and restart both `agent-remote-runtime` and `agent-remote-node`. Check the fresh heartbeat's
`skill_manager.native` and `skill_manager_checks`. The Server API switch remains independent.
Missing, malformed or withdrawn Helper reports yield no capability. Docker Sandbox is not claimed.
This opt-in is not real Claude learning acceptance; use an isolated account to verify that next.

## Unrelated account reported as unsupported

Global update/rollback/remove originally targeted every account in scope, including an existing
bound account where the test Skill was disabled. Library configuration committed successfully,
then the unrelated account caused deployment failure and CLI exit 1.

The Server fix compares enabled source/epoch/revision selection before and after the mutation.
Unchanged global/tool targets are omitted, including accounts pinned to unaffected versions.
Previously enabled sources still produce cleanup targets on disable/remove. Explicit account
requests, reapplication of enabled sources and unfinished attempts retain their deployment and
conflict/supersession behavior. Immutable receipts and `committed` semantics remain unchanged.

## Retained test history

The test's active Skill and temporary accounts were removed. The 739 bytes of archived package
content, immutable receipts and monotonic generation remain governed by retention and reference
rules. A deletion polling interval does not retire package revisions or override retained-history
references. This is expected archival behavior, not an unaccounted upload reservation; reservations
and runtime-state bytes were zero. No forced SQL deletion or generation rollback was performed.

## Cross-repository release dependencies

The composition manifest alone is insufficient: CLI 0.2.32 embeds Node 0.2.29 in
`release-dependencies.json`, so its Node install/upgrade path still selects the old Node even when
the distribution selects 0.2.30. The CLI dependency must be updated and a new CLI binary published.

The release audit checks these component-owned inputs as well as each repository's own version:

| Repository | Dependency source | Required association |
| --- | --- | --- |
| CLI | `release-dependencies.json`, `build.rs` | Node 0.2.30; Bridge 0.1.19, exact bootstrap commit/SHA-256, profile and signer |
| Node | `release-dependencies.json` | Device proxy 0.2.15 at its release commit; Ego Browser wrapper 0.1.19 |
| Node | `internal/egobrowserartifact/release_policy_generated.go`, `ego-browser-skill-source.json` | Generated wrapper/Skill policy agrees with the manifest and Server |
| Server | `src/agent_remote_server/ego_browser/release_policy.py` | Wrapper 0.1.19, protocol v1, upstream Skill 2.0.0 and runtime 0.5.0.32 |
| Ego Browser | Protocol constants and `scripts/install.sh` | Same profile, signer, protocol, upstream Skill and local runtime identities |
| Device / Admin Web | Protocol contracts and build metadata | Device protocol compatibility; no additional component release-number pin |
| Distribution | `release-manifest.json`, Compose environment files | Exact component tags/commits; Server 0.2.28 and Admin Web 0.2.15 image defaults |

Node's `managed-skill-source.json` records the reviewed Device Skill source commit, not a required
Device binary version. Its embedded Skill was compared byte-for-byte with Device 0.2.15 and matches;
the source tree has no changes between that recorded commit and the selected Device release.
Upstream Skill 2.0.0 and local runtime 0.5.0.32 are separate version domains from Bridge 0.1.19.

CI now checks the CLI/Node dependency files at the exact selected component commits. The final
release readiness gate checks those files again after checking out the release tags, rejecting
stale versions, repositories, workflows, Device commits, and Bridge identity mismatches. The
component updater also synchronizes Compose image defaults, with a regression check for drift.
