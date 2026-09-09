# Local ego-browser Bridge Deployment and Recovery

## Compatibility row

| Component | Required identity |
| --- | --- |
| Remote wrapper / local Bridge / Device Client | `0.1.11` |
| Protocol | `ego-browser-bridge-v1` |
| Official Skill | `1.2.3` |
| Skill commit | `36053d07001a910cb806a15d42d00fdea1cdea3d` |
| Skill tree SHA-256 | `262110a09678fd3e0bbb382400588dacb98b24659b3b4a57903703b65d133c7c` |
| Local `ego-browser` runtime | `0.4.7.4` |
| Remote / local platform and backend | Native or Docker Sandbox Linux / macOS |

No component may silently fall back to a remote browser, a GUI-control relay,
raw CDP transport, or an automatically selected session when this row does not
match.

Release prerequisite: the current root manifest pins `agent-remote-server`
`0.2.15`, which contains the schema-9 Bridge admission fix. Keep the root
component pin and the candidate/evidence bound to that exact Server release
until a reviewed replacement is published. Do not substitute an older Server
release as the production Bridge control plane.

## Deployment order

1. Keep `EGO_BROWSER_BRIDGE_ENABLED=false` while staging and migrate the Server
   through Alembic revision `0021_ego_browser_cancel`.
2. Deploy Redis-backed relay state and every Server worker together. Sticky
   in-memory pairing is not an acceptable production topology.
3. Upgrade Node releases. Each Linux package contains a checksum-verified
   wrapper and the exact official Skill tree installed under the immutable
   `/opt/agent-remote/ego-browser/releases/VERSION` root. Eligible Native
   Runtime and Docker Sandbox sessions receive the same pinned content through
   their backend-specific verified startup contract.
4. Upgrade the CLI and Admin console so users can inspect, pause, stop, revoke,
   and diagnose browser bindings.
5. Install ego lite and official local `ego-browser` runtime `0.4.7.4` on the
   Mac. Do not copy its profile to the control plane.
6. Verify and install the macOS Bridge archive with its aggregate manifest,
   archive and manifest Sigstore bundles, and the signing-certificate digest
   obtained through a separate trusted channel.
7. Register the independent Device Client, list candidate sessions, select one
   exact tool-session ID, read the same-UID/no-sandbox warning, and explicitly
   confirm the claim.
8. Run `ego-browser --doctor`, verify versions and policy digests, then perform a
   single-user canary. Enable production admission only after every acceptance
   item and signed release gate is complete.

The component record is now the published Bridge `0.1.11` promotion with
`production_ready=true` and no blockers. The stable root `0.2.27` release
contains the tag-bound schema 9 evidence. Step 8 still cannot authorize
production enablement until its exact deployment bundle is installed and the
final logged-in canary is complete; the feature flag remains disabled by
default.

The exact path from the four blocked fields to a root release is in
[`ego-browser-bridge-release-promotion.md`](ego-browser-bridge-release-promotion.md).
It requires a two-phase candidate/evidence promotion and a new root
distribution tag; changing environment variables alone is never sufficient.

## Required Server policy when evidence exists

```text
EGO_BROWSER_BRIDGE_ENABLED=true
EGO_BROWSER_REQUIRE_DEVICE_POP=true
EGO_BROWSER_EXPECTED_RELEASE_PROFILE=community-local-trust
EGO_BROWSER_EXPECTED_SIGNER_CERTIFICATE_SHA256=<64 lowercase hex>
EGO_BROWSER_EXPECTED_WRAPPER_VERSION=0.1.11
EGO_BROWSER_EXPECTED_SKILL_VERSION=1.2.3
EGO_BROWSER_EXPECTED_SKILL_TREE_SHA256=262110a09678fd3e0bbb382400588dacb98b24659b3b4a57903703b65d133c7c
EGO_BROWSER_EXPECTED_SKILL_COMMIT=36053d07001a910cb806a15d42d00fdea1cdea3d
EGO_BROWSER_EXPECTED_LOCAL_RUNTIME_VERSION=0.4.7.4
EGO_BROWSER_EXPECTED_PROTOCOL_VERSION=ego-browser-bridge-v1
EGO_BROWSER_EXPECTED_LEARNING_BUNDLE_SIGNING_KEY_ID=ego-browser-learning-2026-09
EGO_BROWSER_EXPECTED_LEARNING_BUNDLE_SHA256=<64 lowercase hex>
EGO_BROWSER_EXPECTED_DISTRIBUTION_VERSION=<root distribution version>
EGO_BROWSER_EXPECTED_ROOT_MANIFEST_SHA256=<64 lowercase hex>
EGO_BROWSER_EXPECTED_BRIDGE_RELEASE_MANIFEST_SHA256=<64 lowercase hex>
EGO_BROWSER_EXPECTED_BRIDGE_RELEASE_ARCHIVE_SHA256=<64 lowercase hex>
EGO_BROWSER_EXPECTED_BRIDGE_SIGNING_EVIDENCE_SHA256=<64 lowercase hex>
EGO_BROWSER_EXPECTED_BRIDGE_SIGSTORE_SHA256=<64 lowercase hex>
EGO_BROWSER_EXPECTED_BRIDGE_PROVENANCE_SHA256=<64 lowercase hex>
```

The final eight values come from the exact signed schema 9 evidence and root
manifest used for the deployment. The Server compares every value at startup;
missing or changed pins fail closed. These settings are necessary but are not
permission to override the root manifest's false readiness status.

## Remote identity and relay prerequisites

The runtime helper resolves a dedicated non-root host UID for Native Runtime or
the configured fixed non-root UID/GID for Docker Sandbox. The Node worker
removes that identity from its public task result, rejects UID 0, and grants
only directory traverse plus socket read/write through numeric ACLs. Docker
startup must additionally validate its root-owned trusted spec and the exact
release-pinned wrapper, Skill, and broker mounts. Every broker connection must
match the resolved UID through Linux `SO_PEERCRED` and present the exact
process-local session nonce. Never repair an authorization failure by widening
modes, granting `other`, adding a runtime user to the Node group, or running the
wrapper as root.

Run the real Linux boundary proof after any broker, ACL, runtime identity, or
session startup change:

```sh
(cd ../agent-remote-node && tests/linux_ego_browser_uid_acl_test.sh)
```

Production PostgreSQL deployments require Redis-backed relay state. Tickets and
proof challenges are atomically consumed; binding/generation/role presence has
a five-second TTL; endpoint-specific Pub/Sub channels carry opaque frames and
close notifications. Missing or duplicate presence, missing subscribers,
malformed shared state, and Redis failure all close the pair. Lifecycle changes
commit a PostgreSQL revocation outbox row before workers publish cross-worker
close notifications.

## Operations

The local Device Client owns registration and authorization:

```sh
ego-browser-device candidates
ego-browser-device claim TOOL_SESSION_ID --confirm
ego-browser-device status BINDING_ID
ego-browser-device pause BINDING_ID --generation GENERATION
ego-browser-device resume BINDING_ID --generation GENERATION --confirm
ego-browser-device stop BINDING_ID --generation GENERATION
ego-browser-device revoke BINDING_ID --generation GENERATION
```

The default lease is 60 seconds, renewal interval 20 seconds, admission window
20 seconds, renewal-failure grace 10 seconds, per-request timeout 120 seconds,
maximum concurrency four, and absolute binding TTL eight hours. Stop and revoke
win over renewal. Unknown results and disconnected requests are never replayed.

The Device Client sends a same-UID local heartbeat every two seconds. The
Bridge requires the initial heartbeat and treats five seconds without a valid
heartbeat as authorization loss. It first revokes its supervisor and terminates
managed executions, then clears the active-binding handoff, and only then tries
a generation-bound Server stop for at most ten seconds. A failed stop never
restores admission.

At claim, the Server derives the only valid Task Space label as
`agent-remote:<tool_session_id>`; the Device Client validates the returned
label before saving the owner-only handoff, and resume must return the same
label at the next generation. The Bridge runs a separate supervised ownership
monitor which uses only ego lite's native `listTaskSpaces()` state. It arms only after
observing `ownership=agent`. A later `agentDelegatedToUser` or `user` transition
first revokes admission and terminates managed executions, then requests a
generation-bound pause with `stop_reason=task_space_takeover`. Monitor failure
uses `task_space_monitor_unavailable` and also fails closed. Neither path parses
helper errors or automatically claims/takes over a space.

After takeover, confirm the durable binding is paused at the incremented
generation and old relay presence has disappeared. Inspect browser state,
explicitly run `resume ... --confirm`, and only then use ego lite's native
`takeOverTaskSpace('agent-remote:<tool_session_id>')` workflow if the user has
chosen to return control. Never replay the interrupted heredoc. If the Server
pause was not confirmed, keep local admission closed and reconcile binding and
outbox state before issuing any new authorization.

## Operational checks and response

Run the real distributed relay proof against a disposable Redis database:

```sh
(cd ../agent-remote-ego-browser && \
  AGENT_REMOTE_INTEGRATION_REDIS_URL=redis://127.0.0.1:6379/14 \
  bash integration-tests/real-relay-e2e.sh)
```

Only the final local runtime executable is a fixture. A separate real ego lite
canary is still mandatory.

The relay proof also drives ownership from `agent` to `user` while a
request that caught its helper error remains alive. It verifies external
request and descendant termination, Server state `paused` at the next
generation with reason `task_space_takeover`, explicit confirmed resume, and a
later in-flight stop. The ownership monitor never claims or takes over the
space.

Inspect metadata without fetching relay values or browser content:

```sql
SELECT count(*) AS pending, min(created_at) AS oldest
FROM ego_browser_revocation_outbox
WHERE delivered_at IS NULL;

SELECT status, lease_health, count(*)
FROM ego_browser_bindings
GROUP BY status, lease_health
ORDER BY status, lease_health;
```

```sh
redis-cli --scan --pattern 'agent-remote:ego-browser:*' | sed -n '1,100p'
```

Alert on role imbalance beyond the pair timeout plus presence TTL, sustained
transport/frame-limit failures, outbox age beyond three cleanup intervals and
at least 30 seconds, active bindings without a pair, repeated renewal/lease
failure beyond the 20+10-second window, local peer loss, and any
`unknown_result`. Metrics come from content-free Server, Node, Bridge, and
Device Client structured log events; collectors attach the trusted component
identity and preserve the finite label sets in each component runbook.

Containment first disables new claims, then stop/revokes every live generation
through the normal lifecycle service and waits for the outbox and role gauges
to reach zero. If Redis is down, leave outbox rows pending. Recovery verifies
PostgreSQL, Redis `GETDEL`, Pub/Sub, presence expiry, revocation subscribers,
exact artifacts, and the backend identity/ACL proof before a fresh explicit claim. Never
restore an old ticket, nonce, permit, handoff, sequence lease, generation, or
unknown request.

## Upgrade

Disable new claims, drain or revoke current bindings, then upgrade Server,
Node, CLI/Admin, and local Bridge in that order. The local installer verifies a
new immutable release before atomically changing `current`; it leaves old
release directories available. Reconfirm full trust and create a fresh
generation after every recovery. An existing broker ticket or permit must never
cross a process restart, policy revision, digest change, or release change.

Certificate rotation requires an explicit dual-certificate rollout: publish
new signed evidence, authorize both pins for a bounded window, install with
explicit local trust, create new generations, then revoke the old certificate.
The installer rejects implicit pin replacement.

## Rollback

1. Set `EGO_BROWSER_BRIDGE_ENABLED=false` and stop new claims/reconnects.
2. Revoke every active binding through the shared revocation service.
3. Wait through at most the 10-second renewal grace and managed process cleanup.
4. Confirm no Node broker has an active request or consumable permit.
5. Roll back Server and Node to the compatible row without destructive schema
   downgrade.
6. Run the local verified `rollback-macos.sh PREVIOUS_VERSION`; it checks the
   protected certificate pin and launch-agent files before changing `current`.
7. Preserve terminal binding and audit metadata. Keep retired certificate pins
   on the revocation list.
8. Require a new explicit claim before any later re-enable. Never replay an old
   or unknown heredoc.

If only the local component is uninstalled, ego lite, the separately installed
`ego-browser` executable, and the browser profile remain independently usable.
The uninstall contract tests both the default removal and `--remove-releases`
against an isolated Bridge home and verifies the external runtime stays
byte-identical and executable.
