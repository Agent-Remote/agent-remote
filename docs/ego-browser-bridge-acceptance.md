# Local ego-browser Bridge Acceptance Evidence

Status date: 2026-09-09.

Overall status: **Bridge promotion complete (`production_ready=true`)**. The
published Bridge `0.1.9` has an exact commit/tag, certificate pin, retained
Site Learning bundle, and signed nested evidence; its blocker list is empty.
The stable root `0.2.26` release contains the tag-bound evidence; the final
artifact-bound logged-in canary remains before production enablement. A pending
canary cannot be waived by changing configuration.

| # | Acceptance requirement | Evidence | Status |
| --- | --- | --- | --- |
| 1 | Remote `fclaude` uses local ego lite without a remote browser | Real TLS/PoP + Redis relay E2E reaches a controlled fixture only at the final local runtime boundary; a separate real ego lite canary proves the actual runtime workflow | Blocked on published-composition end-to-end canary |
| 2 | Official Skill heredoc needs no Agent rewrite | Wrapper contract accepts `ego-browser nodejs` stdin and preserves helper workflow; Node packages exact Skill `1.2.3` | Implemented |
| 3 | Local login state stays local and its readable data may be exported | Server models omit profile/content; UI and security docs disclose full data access; the neutral real-runtime canary intentionally read no login data, so a release-bound logged-in-site canary remains outstanding | Blocked on release canary |
| 4 | Normal Skill uses a dedicated Task Space while full-trust bypass remains disclosed | Server derives and binds `agent-remote:<tool_session_id>`, Device Client validates/persists it, Node independently derives it from the nonce-bound session, and Bridge enforces label/scope while remapping only `useOrCreateTaskSpace`; relay and real-runtime canaries prove reuse and native ownership observation while claim/takeover remain native; docs explicitly deny isolation | Implemented and canary passed |
| 5 | Current binding, pause, stop, and end controls are visible | CLI has status/list/claim/pause/resume/stop/revoke; Admin has device/binding state with confirmed stop/revoke; local desktop/mobile interaction QA passed | Implemented |
| 6 | Relay, renewal/grace, generation, sequence, permit, locks, and revocation are tested | Real TLS/PoP Server + Redis + native-session Node broker + wrapper + Device Client heartbeat + outbound Bridge E2E covers native Task Space takeover, revoke-before-pause, explicit resume, and later stop; rootful Linux proves exact ACL and `SO_PEERCRED` UID enforcement; same-device rotation uses new-key PoP, a monotonic generation, exact response validation, and a retry-stable pending identity while revoking old bindings and credentials; unit/integration tests cover races, monitor failure, and ordering | Implemented |
| 7 | Local Bridge exposes no public/LAN listener | Production profile forces outbound mode and same-origin WSS; the development relay listener is unavailable in production, and production local IPC is owner-only Unix socket communication | Implemented |
| 8 | Logs/audit/metrics omit browser payload content | Outer-only schemas, bounded errors, finite metric taxonomies, and content-free events are tested across Server, Node, Bridge, and Device Client; real relay E2E asserts content-free metrics | Implemented automation; signed deployment review pending |
| 9 | Automatic screenshot artifact is bounded and staging-only | Bridge controlled request directory, type/size checks, safe collection/cleanup, and fake-relay artifact test | Implemented |
| 10 | Disconnect, timeout, and unknown result never replay | Broker/Bridge state machines and process-group timeout/revoke E2E return terminal/unknown errors without retry | Implemented |
| 11 | Exact compatibility; unknown capabilities reject | Shared strict schemas/vectors and Server/Node/Bridge version/capability tests pin wrapper `0.1.9`, Skill `1.2.3`, runtime `0.4.7.4` | Implemented |
| 12 | Copy says local Node full trust, whole-browser access, and export capability | Admin English/Chinese warning plus root and Bridge English/Chinese security docs | Implemented |
| 13 | Community signing, Hardened Runtime, pin, credentials, SBOM/provenance, egress, and `production_ready=true` are reviewable | Bridge `0.1.9` stable release, community signing record, certificate pin, exact artifact/SBOM/provenance inventory, and promoted root schema-v3 component are verified; the profile remains self-signed, non-notarized, and non-public by design | Implemented and promotion passed |
| 14 | Canonical allowlist limits and signed learning digest pass activation/recovery | Retained `ego-browser-learning-2026-09` bundle verifies to `6662ad11797f86d721b2d9121049c35b02eff3e71821dc06dfcc190d250788a7`; archive filtering and nested signature checks pass | Implemented and promotion passed |
| 15 | Removing the Bridge leaves ego lite independent and no other device product is required | Isolated macOS uninstaller execution proves default and `--remove-releases` remove only Bridge state while an external runtime stays byte-identical and runnable; the installed real runtime remains `0.4.7.4` and passed direct canaries; the repository-wide release contract prohibits cross-product references/dependencies | Implemented and canary passed |
| 16 | First bind and resume show same-UID/no-sandbox and supervisor limits | Device Client requires explicit confirmation; CLI and Admin warnings describe same UID, no sandbox, irreversible effects, and detached-process limit in both languages | Implemented |

## Gate evidence

Current automated results:

- Bridge workspace: 57 Rust tests plus eight Python release/documentation tests,
  learning/release shell tests, fake-relay E2E, and real distributed-relay E2E.
- Server: 229 passed with no skips and 72.41% line coverage against disposable
  PostgreSQL 16 and Redis 7; Ruff, mypy, and docstrings are clean. The complete
  Alembic chain reached `0021_ego_browser_cancel` and created all five
  ego-browser tables; a live cancellation row also survived the tested
  `head -> 0020 -> head` downgrade normalization cycle.
- Node: complete quality gate, 56.6% Go statement coverage, installer and
  immutable Skill checks, plus the rootful Linux UID/ACL/`SO_PEERCRED` proof.
- CLI: complete Rust formatting, lint, installer, release-contract, and 171-test
  gate.
- Admin: production build and 65 tests pass at 84.84% statements, 70.78%
  branches, 84.10% functions, and 87.87% lines.
- Root schema-v3, release/readiness, evidence-assembly, workflow, Compose, and
  documentation contracts pass.
- Shared Rust/Go/Python protocol and PoP vectors pass.
- Isolated `prepare-release.sh 0.1.1` rehearsal passes.

The final content-free audit injects browser-content secrets into cancellation
completion and failure paths and proves that neither Server nor Node persistence
retains them. Node broker lifecycle failures, Bridge failures, and Device Client
top-level failures now emit only finite error codes; wrapper stdout/stderr and
artifact paths remain the explicitly authorized remote command result channel.

The real control-plane relay command was:

```sh
AGENT_REMOTE_INTEGRATION_REDIS_URL=redis://127.0.0.1:55685/14 \
  bash integration-tests/real-relay-e2e.sh
```

Its fixture creates a native Linux Claude session. The gate ran the actual TLS
Server WebSocket route, Redis ticket/presence/PubSub state, Node broker,
wrapper, Device Client heartbeat, and outbound Bridge; only the final local
runtime executable was synthetic. It proved three encrypted rounds, a native
`agent` to `user` ownership transition, external termination of a request that
caught its helper error, descendant cleanup, Server state `paused` at
generation 2 with reason `task_space_takeover`, explicit confirmed resume to
generation 3, a subsequent in-flight stop to generation 4, replay
ledger/outbox convergence, and content-free metrics. The wrapper environment
deliberately supplied `user-owned-space`; the executed preamble instead
contained the Node permit's `agent-remote:<tool_session_id>` value. The
repeatable fake-relay gate also
executes that preamble with stubbed official helpers and proves the poisoned
name is never selected while claim/takeover helpers remain unchanged. The
ownership monitor uses only `listTaskSpaces()` and native `ownership`, arms
only after `agent`, and never calls or wraps create/claim/takeover helpers.

The independent Device Client same-device rotation tests prove that the
registration request is signed by the new generation rather than the retiring
key; interrupted attempts recover one owner-only pending identity; a partial
local commit converges on retry; successful commit removes the old handoff; and
stale revisions, mismatched response keys, or non-`0600` credential files fail
closed.

The development real local ego lite canary used a dedicated agent Task Space
and `https://example.com/`. It navigated, produced semantic Snapshots before and
after interaction, filled `bridge-canary-value`, clicked the exact button,
verified the submitted DOM state, and captured a screenshot. A second heredoc
reused Task Space `2`, the same sole tab ID, and all page state. There were no
pre-existing Task Spaces in the canary inventory, and a dedicated final heredoc
returned `{"done":true}` from `completeTaskSpace(2, { keep: false })`.

A second real-runtime canary exercised the exact new preamble. A normal
`useOrCreateTaskSpace('must-not-be-selected')` call selected
`agent-remote:bridge-preamble-canary-20260907`, and no space with the supplied
name was created. A second heredoc passed nonexistent numeric ID `999999` but
reused Task Space `3`, tab `EC5B72760D0AA3F826F456757EC9416E`, and the
`https://example.com/` Snapshot. `claimTaskSpace` and `takeOverTaskSpace`
remained native functions, and a dedicated cleanup heredoc returned
`{"done":true}`.

The macOS uninstall proof ran the real uninstaller against an isolated
home-contained Bridge fixture. Default uninstall removed both launch-agent
definitions and `current`; `--remove-releases` also removed only the fixture's
release tree. A separately located `ego-browser` executable remained
byte-identical and runnable after both operations. The actual installed runtime
also remained version `0.4.7.4` with SHA-256
`8390233269674994d78bc79fa4aa4206ae65bc957b4bd5c74b606958c14e2032`;
the direct real-runtime Task Space probes completed and their temporary space
was closed. No `agent-remote-device` runtime or repository was used.

Local Admin visual QA used the real Vite application with a loopback-only API
fixture. English and Simplified Chinese loading, error, data, and empty views,
mobile drawer navigation, retry/refresh behavior, stop confirmation, and exact
request-cancellation confirmation were inspected at 1440 x 900 and 390 x 844.
The delayed cancellation kept its action disabled before reaching
`cancel_requested`; its request path retained the encoded `%2F`, its body was
the exact generation/sequence pair, and bearer authentication was present. A
retry-to-populated transition also proved that the newly rendered cancel action
does not open under the pointer. Both viewports had no page-wide horizontal
overflow; compatibility and lease metadata remained visible after wrapping.
This is development evidence, not a substitute for an artifact-bound screenshot
run from the eventual tagged release.

Before enabling production, capture and bind to the final root release manifest:

1. release-bound desktop/mobile Admin screenshots and interaction evidence
   from the exact tagged build (local development visual QA is complete);
2. a published-composition end-to-end real local ego lite canary through the
   wrapper/relay/Bridge for logged-in state, explicit bypass, takeover, and
   disconnect; repeat the now-proven navigation,
   Snapshot, click, fill, screenshot, Task Space reuse, and cleanup checks;
3. complete green gates from the exact tagged commits in all six affected
   repositories and root schema-v3 production evidence with no blockers.

The certificate and retained learning-bundle evidence listed in the original
blocker table are carried forward by the Bridge `0.1.9` promotion (originally
established by `0.1.7`). The stable
root `v0.2.26` release binds those records to its tag-bound evidence; deployment
still requires the exact bundle and the final canary.
