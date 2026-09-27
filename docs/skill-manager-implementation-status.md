# Skill manager implementation evidence

The complete contract is [the reviewed design](skill-manager-design.zh-CN.md).
This tracker records implementation evidence; a completed row cannot substitute for the full
design, its commands, invariants, runtime backends, or acceptance cases.

## Installation defaults — 2026-09-27

The default-on composition selects Server **0.2.29**, Node **0.2.31**, CLI **0.2.34**,
Admin Web/Device **0.2.15** and Ego Browser **0.1.19**. CLI's own dependency file now pins Node
0.2.31; the composition records the exact release commits and Server image tag.

Skill management is a default-on base feature in Server settings, deployment templates, Node
configuration and fresh installer configuration. Explicit false overrides survive upgrades; old
installer-generated false values require a one-time intentional migration. Missing Node fields
enable automatically. Native dependency, private storage and fresh heartbeat checks remain intact.
The earlier default-off descriptions below record historical release behavior.

The existing Node configuration was migrated and the actual Helper probe, Server heartbeat and
CLI regression passed. [Validation record](skill-default-on-validation.md) documents exact versions,
installation/update/rollback/rule checks, byte-verified downloads and cleanup. Temporary accounts
were deleted, active libraries restored empty and original account configuration preserved. Normal
archive receipts and generation remain. Real Claude learning/inheritance acceptance is still open.

## Production test repairs — 2026-09-27

The follow-up composition selects Server **0.2.28**, Node **0.2.30** and CLI **0.2.33**,
Admin Web/Device **0.2.15** and Ego Browser **0.1.19**. Exact source identities belong to
[the release manifest](../release-manifest.json). See [production findings](skill-production-troubleshooting.md).

The Node now has an explicit default-off Native Skill opt-in, a real private-volume/dependency
probe and strict Helper-to-heartbeat forwarding. Server library mutations omit unchanged global
targets while retaining explicit reapplication, disable/remove cleanup and unfinished attempts.
Upload filesystem failures return a structured storage error. Existing CLI 0.2.32 was checked
against that new HTTP response. Empty unsupported Node reports remain compatible with the isolated
lifecycle fixtures; they are not substituted for real supported reports in production.

Final local Server gates passed **1865 tests, 104 skips**, at **91.50%** coverage. Server CI
`36326613606` passed **1878 tests, 91 skips**, at **92.51%** coverage after fixing test metadata
isolation and synchronization. CLI 0.2.33 updates its embedded Node dependency from 0.2.29 to
0.2.30; distribution CI and release gates now check component-owned dependency manifests.
Node full local
gates and Linux amd64 compilation/vet passed; its published archive checksum, version and default-off
configuration were verified. No production configuration was changed in this repair phase.
R46 genuine Docker Sandbox and R49 actual model discovery/learning/inheritance remain open;
the new opt-in is not evidence that those acceptance cases passed.

## Earlier delivery status — 2026-09-27

Implementation and check-duration improvements have been committed and pushed to `main`.
The published deployment bundle is **0.2.42**, selecting Server **0.2.27**, Node **0.2.29**,
CLI **0.2.32**, Admin Web/Device **0.2.15**, and Ego Browser **0.1.19**. Component identities are
fixed in [the release manifest](../release-manifest.json); test-only follow-up commits on Node
and CLI main do not replace the immutable published source identities.

- [Deployment release 36316299879](https://github.com/Agent-Remote/agent-remote/actions/runs/36316299879)
  passed tag compatibility, component supply-chain verification and bundle publication.
- [Server CI 36315567738](https://github.com/Agent-Remote/agent-remote-server/actions/runs/36315567738)
  passed 1873 tests, with 91 skipped, and 92.50% line coverage in 650.38 seconds of pytest time.
- [Node CI 36314643609](https://github.com/Agent-Remote/agent-remote-node/actions/runs/36314643609)
  and [three-platform CLI CI 36315366122](https://github.com/Agent-Remote/agent-remote-cli/actions/runs/36315366122)
  passed. Local complete gates measured approximately 24 seconds, 104 seconds and 208 seconds
  for Node, CLI and Server respectively; required test scope and coverage thresholds remain.

The downloaded deployment archive matches the manifest exactly, and its checksum and exact-tag
provenance passed verification. Server release metadata, checksums and image provenance also passed.
Publishing these artifacts does not deploy a live service or complete the entire design acceptance.
`SKILL_MANAGER_ENABLED=false` remains the deployment default.

**Still open:** R46 genuine Docker Sandbox capability/runtime acceptance and R49 real Claude
enrollment, exact-session discovery, learning and inheritance, including independent accounts.
Related full-runtime verification boundaries remain as recorded in the requirement audit.
The user deferred remaining real Linux, Docker Sandbox and model acceptance until after release
with their assistance. Do not start those runs, copy host credentials, or count synthetic/skipped
tests as completing them. The overall goal remains unfinished.

## Historical implementation evidence

The initial work used `feature/skill-manager`. The table and chronological entries below retain
their original milestone boundaries; their earlier pending/release statements are historical.
The [section 11.1 audit](skill-manager-interleaving-audit.md) maps all 19 required interleavings to
concrete tests and identifies remaining combined/runtime acceptance gaps.

| Requirement group | Status | Evidence / remaining work |
| --- | --- | --- |
| Manifest v1, safe paths, exact content identity, portable links | In progress | Shared golden vectors pass in Python, Go and Rust; CLI stable local capture and Node writable permission baselines implemented; runtime capture lifecycle, directory views and adapter probing remain pending |
| Field-wise user/tool/account resolution and version pins | In progress | Persistent user/tool/account rules, field-specific inherit and pin APIs tested; exact Server snapshot resolution now implemented; CLI rule mutations and typed list/info are implemented; effective account diagnostics and original-session snapshot queries now preserve field origins, pin reasons and exact historical identities. Native startup queue and durable exact confirmation are connected; broader backend integration remains pending |
| Conservative three-way merge and complete-directory publication | In progress | Server linked merge units, atomic directory publication, epoch checks, retained conflicts and user resolution plans implemented and tested; migration resolution and CLI workflows are implemented as detailed below; runtime transfer and backend integration remain pending |
| User-private storage, quotas, reference-safe retention | In progress | Server migration 0026, private immutable streaming object store, idempotent upload leases, transactional package/state reservations and explicit tree-object foreign keys implemented and tested on SQLite and PostgreSQL 17. User-authenticated streaming HTTP and safe expired-upload/orphan reclamation implemented. exact snapshot-bound Node downloads, immutable finalization upload receipts and atomic publication implemented; internal owner-bounded retention protection analysis now has PostgreSQL evidence, including independent-connection lock serialization; migration 0040 now records transactional release/reacquisition clocks for seven historical identity types and exposes internal deadline diagnostics; 0041 adds internal comparison-history retirement while preserving audit digests/receipts; internal checkpoint retirement now preserves expired branches and retained-history dependencies; internal directory compaction now previews and atomically replaces equivalent views while preserving exact snapshots/baselines; read-only post-compaction protection projection, release forecasts and complete retained-history dependency planning/atomic retirement are implemented; migration 0042 adds complete-tree release clocks, actual retained FK inventories and cross-category deleting-object admission; migration 0043 now implements internal exact tree/object reclamation, category quota settlement and persistent physical deletion workers with SQL/disk fencing and coordinated deletion-state recovery evidence; 0044 adds lifecycle-bound deferred prune claims; 0045 and the CLI now implement public prune selection, complete paged confirmation, compact original-request recovery and immutable receipt/physical-progress status. Public user usage/policy/deletion diagnostics and exact revision/checkpoint retention diagnostics are now exposed through Server detail APIs and CLI info/status; broader runtime retention integration remains pending |
| Git/local discovery and atomic multi-skill installation | In progress | Atomic multi-item Server add and authenticated ingestion implemented; CLI local/Git acquisition, selection, stable private packaging, complete uploads and original-request recovery are implemented and tested; runtime distribution remains pending |
| List/info/effective/check/update/stage/rollback | In progress | Library APIs, stage, provenance observations and activation-history rollback implemented; CLI install/check/update/stage/rollback, original-operation recovery/status/wait and effective account/session/system queries are implemented. Queries distinguish saved/configured selection from actual model loading. Runtime deployment and the full completion audit remain pending |
| Enable/disable/inherit/pin/unpin/remove/reinstall epochs | In progress | Persistent scoped rules, atomic receipts, removal archives and same-source reinstall epochs tested; CLI enable/disable/inherit/pin/unpin/remove now consume these APIs with durable request identity; account-local list/info and enabled/inherit workflows are implemented; runtime takeover capture and distribution remain pending |
| State list/info/diff/conflicts/export/resolve/migrate/reset/restore/prune | In progress | Server conflict inspection/resolve and explicit-checkpoint history/diff/member references/dependency export implemented; effective selection/default diff, atomic reset/restore and first-use version preparation, explicit incremental migration and migration conflict inspection/exact export and scoped custom uploads/plan persistence implemented; atomic multi-branch migration resolution and typed user API, retained-input recomputation, precise linked-member invalidation, and proactive library/success supersession implemented; full-account managed preflight is now connected. CLI history/diff/export, reset/restore, separate publication/migration conflict listing and saved-input diff, confirmed resolution with custom state capture/upload, and explicit incremental migration with exact-request recovery and original ID/key status are implemented; CLI prune now implements complete disclosure, confirmation, original-request recovery and receipt/physical-progress status; Frozen Native Node-only directory export is implemented through user authorization, live Node rechecks, existing Helper capture descriptors or separately verified stopped work after local copy reserve/runtime quota failure, and verified CLI publication; real CLI/HTTP/SSH frozen and runtime-quota export acceptance now passes; recovery without either termination or recorded invocation evidence/above export bounds, broader command/runtime acceptance and final audit remain pending |
| Operation status/wait/retry and JSON/exit codes | In progress | Typed result envelopes and receipt lookup by operation ID or idempotency key implemented. Compatible bound Native accounts now enter pending under explicit policy; incompatible accounts remain unsupported. CLI original-operation status and bounded waiting now implemented; rule/remove/rollback mutations now retain user-bound exact requests and recover lost acceptance by key; installation/update original-request recovery is implemented; schema 0047 now saves immutable per-account configuration plans, normalized version/epoch references and plan digests, with retryable-terminal retention; Native finalization status now uses original snapshot operation IDs, honest awaiting-node/local/upload/persisted/latest-publication phases and bounded fclaude stop/status waiting; ordinary first-use Native admission now returns exact no-session takeover receipts with owner/device status and bounded CLI polling/single resumed creation; schema 0049 now persists exact target attempt chains and retry receipts; public original-operation retry POST/key lookup and CLI exact-request recovery are implemented with targeted evidence below; new configuration now supersedes older unfinished operations only when saved effective target selection changes, preserving active target roots and first replacement identity; schema 0050 now binds independent full-directory inputs to exact Node tasks; dedicated leased worker/Helper preparation and atomic Server success/inspection are implemented; schema 0051 now binds original revocation to exact permanent drain and atomic terminal confirmation; Worker durable failure/supersession recovery is connected. Schema 0052 seals initial takeover discovery separately from accepted plans; bounded ordinary polling now schedules original pending targets. Full backend acceptance remains pending |
| Exact session snapshot transaction and runtime capability selection | In progress | Migration 0028 and locked reservation tested, including stale ORM refresh and concurrent retries; public session admission now prepares all enabled branches, retains conflicts, gates backend capabilities and binds exact snapshot/task atomically. Native task consumption and durable exact startup confirmation are connected; first-use Native takeover now commits one original-node reservation before a no-session pending response, with concurrent PostgreSQL admission evidence; full backend acceptance remains pending |
| Native writable copies, aliases and system mounts | In progress | Linux ordinary-copy, Helper stop/finalization integration and actual non-root Bubblewrap alias/system-mount proofs pass; task-bound Native Helper preparation, at-most-once launch/recovery/cancellation and continuous leased internal startup are implemented; real systemd launch/exit/cleanup tested with synthetic tools; Native queue dispatch, independent lost-ACK inspection and exact-cancellation retirement are implemented; background natural-exit finalization, original broker-admission-loss draining and passive previous-boot recovery have Linux/systemd evidence. Same-boot starting recovery now pins an observed invocation without readiness, with real systemd admission/exit/cancellation evidence. Real ARM64 and amd64 two-kernel VM power-cut tests now verify unclean recovery without tool replay; complete real Server/worker/Claude acceptance remains pending |
| Docker writable copies, aliases and system mounts | In progress | Same verified copy primitive available; Docker Sandbox mount/lifecycle integration remains pending. The local Docker CLI reports its sandbox command removed. Linux container proofs are not Docker Sandbox acceptance |
| Finalization journal, stop/delete/cleanup and unclean recovery | In progress | Independent SkillStateRoot, atomic session preparation, Native quiescence checks, stop journaling, missing-spec recovery and pending-state cleanup refusal tested on Linux. Native pane exit classification and complete systemd lifecycle now tested with synthetic programs. Server snapshot reads and session/account deletion guards now tested. Server finalization upload/persistence/publication and strict Go HTTP transport are implemented; Helper atomic frozen objects and exact-bound read-only descriptor transfer have Linux/non-root/systemd evidence; independent worker transfer, exact Server termination, Helper acknowledgement and stopped-runtime cleanup are integrated. Passive previous-boot recovery and interrupted transient cleanup have simulated earlier-boot and actual bind-mount tests. Normal-stop bounded saving, durable owner/device status and CLI waiting/re-query are implemented. Real ARM64 and amd64 two-kernel VM power cuts now verify unclean retained recovery. Complete real Server/worker/Claude acceptance and Docker lifecycle remain pending |
| Legacy import exclusion, account-local entries and directory takeover | In progress | Server account-local discovery, activation and checkpoints implemented; CLI import-config supports --exclude-skills before preview/collection; Server planning/start and exact leased-task Node execution authorization now enforce directory mode, with complete batch preflight and durable denial/replay tests. Serialized Helper writes, persistent fences/receipts and delayed legacy writer admission guards have Linux evidence. Server initial takeover reservation, immutable inventory/capture upload and atomic local-source/directory publication are now tested; Helper private stable capture and internal Native writer/cgroup inspection now have Linux and real systemd evidence; exact-task authenticated transfer routes and the streaming Go client now have HTTP/race and real cross-language network evidence; read-only Helper descriptor transfer now has non-root Linux and adversarial protocol evidence; lease maintenance and internal retained-transfer orchestration verified; dedicated Native capture dispatch and lease renewal now recover from original reservations and immutable Helper captures; ordinary session admission initiates original-node reservations and owner/device status plus CLI wait are connected. Account-local CLI list/info and enable/inherit are implemented; complete Docker/backend-copy proof, interrupted recovery and verified rollback remain pending |
| Cross-user authorization, node task binding and race scenarios | In progress | SQLite/PostgreSQL composite ownership and exact Node preparation lease authorization tested; finalization authorization now tested; full cross-component interleavings remain pending |
| Deployment config, migration/upgrade/backup and user documentation | In progress | Root Compose now provides a private persistent content volume and disabled-by-default Server settings; coordinated database/content and Node pending-state backup boundaries documented. Compose interpolation/overlay and isolated volume archive/restore verified. Full release/upgrade, referenced-object restore validation and actual backend recovery acceptance remain pending |
| Required repository quality gates | In progress | Latest full Server gate: 1817 passed, 97 skipped, 83.04% coverage (13970); final fixture additions also passed focused Ruff/mypy/docstring checks and live SSH. Latest full Node gate passed at 62.6% coverage (33504; stop boundary and completed previous-boot migration recovery); latest full CLI gate passed all Cargo/static checks (94834), including negotiated recovery and six export contracts. Actual Linux Helper continuation/descriptor tests passed without skips (64896), including a real 30-second stalled output. Small frozen and stopped-work live SSH regression passed (47539). Long frozen/stopped-work SSH acceptance passed; combined daemon capacity failed in its second finalization and remains open. Real model/backend acceptance and the complete requirements audit remain pending |
| Native CLI install/selection/sync/stop/restart/inheritance | Synthetic acceptance passed | Current CLI, real Mutagen and forced-command SSH, authenticated Server, unprivileged Worker and Helper/shipped systemd units passed complete writable state publication and independent-session inheritance after daemon restart, plus reclamation and status after deletion. Source includes binary data, permissions, deletion, links and account-local content. Explicit test-only identity/capability setup and synthetic tool; real account enrollment and Claude inference/learning acceptance remain pending |
| Published default capacity | Partial full-runtime acceptance passed | Complete Native 100000-entry daemon pipeline passed (36891): two clean publications, restart and independent full inheritance. Combined 10 GiB / 100000-entry stopped-work SSH export passed (74214); above-default byte recovery passed (21325); actual 10 GiB frozen capture/export passed (86312), all including revocation and unchanged source inventory. Combined frozen export also passed (9223). Complete byte-only daemon publication/inheritance/reclamation passed (34085); combined daemon 11363 failed during second finalization; observed reproduction 11193 passed first publication/reclamation, then failed successor admission with HTTP 409 |
| Full design completion audit | Pending | Every requirement and every interleaving scenario in design section 11.1 must have direct evidence |

No goal completion is claimed while any row remains pending or only indirectly verified.

Latest review also requires account-directory state commands, directory epochs, cross-entry link
validation, actual materialization permission baselines, invalid-format state preservation and
aggregate quotas. Some persistence and composition contracts now have direct evidence below; complete runtime capability remains unadvertised.

## 2026-09-21 — durable private content foundation

Added in `agent-remote-server`:

- `models/skill_storage.py` and migration `0026_skill_content_storage`: private objects,
  complete trees, ownership-bound tree references, upload plans and independent usage counters.
- `services/skills/content.py` plus its repository: idempotent plans, write-locked admission,
  complete-tree publication, rollback-safe retries, lease expiry and authorized tree-based reads.
- `skill_manager/storage/`: bounded streaming verification, per-user object namespaces,
  fsync-before-publication, no-overwrite deduplication, descriptor-relative no-follow access,
  worker cancellation cleanup, short-write-safe copies and design-default resource policies.
- `SKILL_STORAGE_ROOT` / `SKILL_STORAGE_POLICY` and server
  `docs/skill-content-storage.md` document configuration and caller transaction responsibilities.

Direct evidence: 22 object-storage tests passed; 9 database service tests passed on both
SQLite (foreign keys enabled) and PostgreSQL 17, including concurrent quota admission and
cross-user reference denial. An isolated PostgreSQL instance applied all migrations and then
successfully downgraded 0026 and upgraded it again. The disposable test instance was removed.

## 2026-09-21 — persistent library and authenticated APIs

Added migration `0027_skill_library`, library/revision/override/activation/source-observation/
operation models and the corresponding repository, services and user-token-only HTTP endpoints.
Multi-item add commits atomically. Generation CAS, durable idempotency receipts, independent rule
fields, retained removal/reinstall epochs, candidate staging and real activation-history rollback
have direct tests. Local source identities cannot be usable absolute paths. Safe bounded YAML
parsing preserves original SKILL.md bytes and supports optional Claude frontmatter.

Content APIs stream declared uploads and authorized tree downloads. Expired staging cleanup now
preserves registered content and live upload leases in both quota categories, reclaims orphan
objects and crash temporaries, and retains reservations when physical cleanup fails. Disk worker
cancellation waits for completion. Read-only library/content queries do not create state rows.

Account deletion removes only that account's overrides after existing lifecycle checks. New legacy
sessions with effectively enabled managed skills fail explicitly; attaching existing sessions is
unchanged. This guard is not a managed runtime implementation. Bound account operations report
unsupported rather than claiming deployment; unbound accounts report stored/deploy_on_first_use.

Evidence: 22 library + 12 content-service tests passed on PostgreSQL; migration 0027 was upgraded,
downgraded to 0026 and upgraded again. The Server full gate passed with 428 tests, 73.09% coverage,
Ruff, mypy, docstrings and whitespace checks; seven API tests passed again after adding lookup by
idempotency key. See Server `docs/skill-library-api.md` and `docs/skill-content-storage.md`.

The manager is not complete. Node-bound authorization, managed account state, exact session
snapshots, writable copies, finalization, merge publication, recovery, retained-history GC, CLI
commands and real Native/Docker acceptance remain required. No backend advertises the capability.

## 2026-09-21 — stable source packages and Linux writable-copy primitive

CLI `skills/discovery.rs`, `metadata.rs`, `source_fs.rs` and `snapshot.rs` now provide:

- Bounded discovery with optional Claude frontmatter, dependency-cache exclusions, no descent
  beneath recognized skills, duplicate-name diagnostics and explicit multi-source selection.
- Capability-relative, no-follow reads; root aliases are resolved once, internal links are stored
  without reading external targets, and full staged manifests validate link portability.
- Before/after identity/length/time checks and a final full metadata walk; complete private staged
  objects remain unchanged when source files change later. Exact modes, empty directories, bytes,
  binary/text identity and original SKILL.md contents are preserved.
- Expanded byte/entry limits, Git LFS pointer rejection, streaming UTF-8 classification and
  digest-only access to staged files. No remote mutation or command wiring is implied.

Verification: CLI full gate passed (303 Rust tests), all 21 focused source tests passed on macOS
and Linux, and the source modules plus applicable tests compiled for Windows. The Windows check
is compilation evidence, not proof of Windows runtime behavior. The Linux/Windows checks used an
isolated harness for the actual source modules, avoiding unrelated platform toolchain dependencies.

Node `internal/skillmanager` now has a Linux ordinary-copy primitive. It validates a complete
manifest, runtime identity and adapter dependency map, checks expanded disk space/inode capacity,
streams and verifies every object, applies and rechecks actual permissions/ownership, fsyncs the
complete bundle, and publishes with no-replace rename. Existing bundles are never overwritten.
The runtime-owned `work` tree is separate from the helper-owned baseline. Source and actual
permission manifests prevent owner-write normalization from becoming a false checkpoint change.

`tests/linux_skill_copy_test.sh` reproduces the Linux tests in a root container and is wired into
CI. It exercises actual non-root execution/writes, protected baseline denial, independent copies,
large runtime files, corrupt/truncated/overlong objects, classification, cancellation, disk reserves,
system-name rejection and adapter-bound dependency links. These tests do not launch Native or
Docker Sandbox sessions, establish runtime aliases, or prove readonly system mounts. Capture and journal primitives are now tested below; Helper/backend lifecycle wiring and recovery orchestration remain pending.

The task-created PostgreSQL test container has been removed after the verified Server tests.

## 2026-09-21 — complete runtime capture and bound local finalization journal

Node capture hashes and fsyncs the complete quiescent account directory, including root auxiliary
state, additions, deletions, empty directories, binary databases and invalid SKILL.md edits. It
checks stable file identities/lengths/timestamps before and after reads and rewalks the whole tree.
Internal cross-entry links remain links; only exact helper-adapter external dependencies become
runtime_link records. Quota or portability failures preserve the work tree. Unchanged actual copy
modes map back to original source modes; actual chmod changes remain edits.

A sealed prepared snapshot binds owner, account, Node, session, snapshot, directory epoch,
library generation, starting tree and capture policy. Finalization publishes its complete manifest
and journal together with fsync and atomic no-replace rename. Repeated finalization reuses the
journal after reopening the bundle and without a runtime spec; corrupted/incomplete journals
fail closed and never silently recapture. State advancement requires expected state and binding.
Unclean input can only advance to persisted_unclean/detached. Local durability or upload-pending
never permits session-view deletion; the terminal retained states do not authorize content GC.

The reproducible Linux suite covers these primitives alongside the ordinary-copy tests. It does
not yet prove stop-process-group quiescence, backend alias mounts, network upload recovery, or
Server finalization publication. Runtime Helper lifecycle and Server state/snapshot models remain
required before the manager is usable or any backend can advertise support.

Latest Node verification: full quality gate passed with 60.3% host statement coverage; the final Linux suite passed 26 top-level tests plus shared-vector subcases. Linux-specific `go vet` also passed. No skill runtime capability has been advertised.


## 2026-09-21 — private root configuration and Native lifecycle integration

Node configuration now defines `skill_state_root` and explicit policy values. The default is
`/var/lib/agent-remote-skill-state`, outside the installer's worker-owned data directory. The root
helper walks safe root-owned ancestors without following symlinks, rejects overlaps (including
resolved aliases), and requires an existing root to be root-owned 0700. It does not silently chmod
unsafe roots. English/Chinese Node READMEs and configuration examples document units and rollout
limits. Per-item checkpoint quota enforcement still needs the Server's item/directory scope mapping;
the current copy/capture primitives enforce complete-directory byte and entry ceilings.

Atomic session preparation publishes work, baseline, snapshot binding and backend/resource/boot/
UID/GID metadata together under `session-<UUID>`. Identical retries preserve runtime edits. Existing
incomplete/corrupt bindings fail closed. The Helper's internal Native preparation function checks
node/user/account/session identity and selects paths, identity and capture policy itself. It is not
yet exposed through task-bound streamed content transfer or wired to a Server snapshot reservation.

Native stop now requires successful systemctl stop, terminal unit state and proof that the complete
cgroup has no writers. Bounded/malformed/cancelled/ambiguous inspection and failed stops preserve
files. Failed/cancelled launches use a fresh bounded cleanup context and the same writer checks;
managed failed launches retain unclean state. Native stop captures into the durable journal and
returns stopped plus state_pending while Server retention is pending. Cleanup refuses this state.
The retained session binding supports recovery after spec loss and permits transient cleanup only
after a terminal retention acknowledgement. Tests inject that acknowledgement locally; authenticated
Server upload and publication are not implemented by these tests.

For sealed Native specs, launch now binds the private work tree onto a controlled host mountpoint.
Both Claude discovery aliases use the same copy, and both system skill names are readonly at both
aliases. System bytes come from the embedded release sources (or verified enabled ego-browser
artifact), not the shared mutable account tree. Mount checks use actual inode/device and mount ID;
normal unmount must succeed before session deletion, and busy mounts preserve the directory.

Evidence: Node full quality gate passed with 60.7% host statement coverage. The root/Linux suite
passed 32 skill-store/copy/capture/journal tests and 10 Native stop/recovery tests. Two separately gated
mount tests passed with real Linux bind mounts and the actual generated Bubblewrap arguments run as
UID 12345: writes and executable scripts work through both aliases, system writes/deletions fail,
unmount plus transient deletion preserves the durable copy, and busy mounts refuse cleanup.
Both reproducible scripts are wired into CI. Linux-specific vet and shell/whitespace checks passed.

These proofs do not launch a full systemd/Claude session. Natural-exit status propagation remains an
explicit integration issue: systemd --collect can discard terminal exit data, and the current
supervisor observes tmux disappearance rather than retaining the tool's exact exit status. This must
be resolved before clean automatic publication is enabled. No backend advertises skill-manager
support. Docker Sandbox acceptance is additionally unavailable in this environment: the installed
Docker CLI reports `docker sandbox` deprecated and removed. Ordinary Docker containers were used
only for isolated Linux filesystem/Bubblewrap tests, never as a substitute runtime backend.


## 2026-09-21 — real Native systemd exit and recovery proof

Managed Native supervisors now retain and inspect the original tmux pane. A normal zero pane exit
is required for successful supervisor exit; nonzero, missing, signaled or malformed pane outcomes
remain failures. Managed units retain natural exit state with RemainAfterExit and omit --collect.
Reconciliation recognizes an exited, quiescent unit as stopped. Stop preserves pre-stop successful
exit evidence only after proving the whole cgroup empty, so unit collection cannot erase it and
residual writers cannot become a clean submission.

Explicit managed stop requests Claude's terminal workflow through the supervisor: one Ctrl-C and
one further Ctrl-C after a second if still alive. A normal pane exit is still required. The Helper
allows ten seconds for cooperative exit, then systemd KillMode=mixed / TimeoutStopSec=10s ensures
forced cleanup targets the complete cgroup. Canonical-terminal signal death and timeout killing
remain unclean. A sealed termination.json is fsynced before capture; quota/portability failure and
retries cannot change that classification. Any termination receipt blocks relaunch, even without a
completed finalization manifest.

`tests/linux_skill_systemd_test.sh` now runs the actual runtime executable and Engine.launch under
an isolated systemd PID 1, with a private writable cgroup namespace and no host filesystem/cgroup
mounts. It exercises real namespaces, firewall commands, tmpfs, tmux, Bubblewrap, stop inspection,
capture and cleanup. Six cases passed: normal exit, exit 7, SIGKILL, cooperative raw-terminal stop,
canonical-terminal interruption and forced timeout. The first and cooperative cases preserve clean
state; all abnormal cases retain unclean data. The forced case actually waited through the graceful
and hard-stop windows (about 22 seconds including launch). Every case preserved runtime writes
through finalization and transient deletion. Server retention acknowledgements are explicit test
inputs; these are synthetic terminal programs, not the Claude binary or a Server/API integration.

Additional evidence: real tmux tests cover normal/nonzero/signaled pane exit and a lost tmux server;
actual bind/alias and busy-mount proofs still pass. The root Linux suite passed 33 skillmanager tests
and 14 Native tests (47 total), with three separately gated mount/systemd tests skipped there and
executed by their own scripts. Node full quality gate passed at 60.2% host coverage; Linux-specific
vet, shell, workflow contract and whitespace checks passed. All three Linux proof scripts are wired
into CI. Test containers, temporary image tags and test binaries are removed by the scripts.

The Native systemd classification gap recorded above is now addressed and directly tested. Managed
preparation still lacks task-bound content transfer and Server snapshot reservation; Server account
state/publication, CLI commands and full end-to-end acceptance remain unfinished. Docker Sandbox
still needs its own actual backend support and evidence. No skill-manager capability is advertised.

## 2026-09-21 — account runtime schema and exact snapshot preparation

Server migration `0028_skill_runtime_state` now stores library-backed account directory mode/head/
epoch, per-installation-epoch/revision branches, complete-tree checkpoints and immutable directory
membership, exact session snapshots/items and finalization metadata. Composite foreign keys bind
users, accounts, branches, sessions, Nodes and preparation tasks. Scope checks prevent item/directory
head substitution. Finalization metadata distinguishes pending uploads from durable complete trees
and rejects clean publication statuses for unclean input. Account-local revisions are still absent.

The internal snapshot service requires a previously managed account directory. It holds the existing
user storage write lock throughout current rule/head reads, initial branch materialization, content
verification and snapshot/reference insertion. It fixes library generation and directory/branch
epochs together. Duplicate concurrent requests reuse one snapshot; later configuration changes do
not replace an existing snapshot. Queries explicitly refresh ORM entities loaded before lock
acquisition, preventing a new generation from being combined with stale defaults or overrides.
A version without an initialized branch cannot discard existing state: it reports
`STATE_MIGRATION_REQUIRED` until the separate migration workflow is implemented.

Directory composition keeps root auxiliary data and removes only known member namespaces from
this session's view. Disabled items remain in retained account checkpoints. Selected item views
are combined before relative links are validated; an absent dependency reports
`STATE_DEPENDENCY_MISSING`, without re-enabling or copying an anonymous target. Name collisions,
reserved system paths, missing subtree roots and per-item expanded byte quota violations fail.
Each enabled SKILL.md is validated from the complete materialized tree before reservation commits.

Node-authenticated preparation read endpoints expose only the exact snapshot manifest and files.
They check active owner, assigned Node, exact task UUID/payload, snapshot/session lifecycle and a
live leased/running preparation deadline on every request. Same-user unrelated content remains
inaccessible. Downloads verify content and stream from bounded-memory private disk staging after
the database transaction ends. User credentials and guessed content identifiers grant no Node
preparation permission.

Single and bulk session deletion now reject pending skill state before other deletion side effects.
A retained snapshot with a complete published/conflicted/detached finalization can release only its
relational session ID; its source ID, content and finalization remain. Account deletion keeps all
previous guards and also refuses a runtime-state root. A managed or migrating account cannot use
legacy admission even if all user-library skills are disabled.

PostgreSQL 17 evidence: migration 0028 downgraded to 0027 and upgraded successfully; all seven new
tables and both new parent unique constraints match ORM metadata. Whole-schema comparison still
reports only the previously known unrelated JSON/JSONB and sessions index drift. The 56 runtime
constraint, snapshot, lifecycle and authenticated Node HTTP tests pass against the migrated
PostgreSQL schema. SQLite also exercises those paths; seven pure directory-composition tests cover
cross-item dependency filtering, original modes, root data, collisions and expanded quotas.

This is not an enabled end-to-end managed runtime. Public session admission remains gated; Node
task-driven preparation, permission-baseline receipt persistence, finalization upload/publication,
account-local skills, takeover/import exclusion, state migration/conflict/retention operations,
CLI command wiring and actual Docker Sandbox acceptance remain unfinished. No backend advertises
skill-manager support, and no commit, release or deployment was performed.

Final Server gate for this increment: 491 passed, 15 skipped, 73.99% line coverage; Ruff formatting/
lint, Mypy, Chinese docstring checks and whitespace checks passed. The task-created PostgreSQL test
container was removed after the migrated-schema verification and integration tests.

## 2026-09-21 — immutable finalization ingestion and renewable transfers

Migration `0029_skill_finalization_uploads` adds a current upload-attempt binding for each immutable
finalization. Composite foreign keys bind its owner and incoming digest to an account-directory
lease; another digest or package scope cannot be substituted. Each active upload attempt belongs
to only one transfer. Expiry renewal changes only the lease/attempt number, never the incoming
manifest, source snapshot or first clean/unclean classification. No cascade can remove this binding
by deleting the upload or session.

Node-authenticated begin/status/file/complete endpoints now ingest the assigned snapshot's frozen
input after the session reaches a terminal process state. They do not rely on an old preparation
lease. Every request rechecks Node ownership, active user and session/snapshot identity. Bodies do
not accept arbitrary owner/account/path fields, file streams are bounded and verified, and replaced
upload attempts lose write/completion permission. Failed or oversized bytes cannot become a complete
receipt. Both user package and Node state streams share the same verified private staging helper.

Complete ingestion records a full incoming directory checkpoint, surviving known item views and
format diagnostics in the same transaction as content references and the receipt. Safe but invalid
SKILL.md and binary runtime bytes remain retained. A verified empty directory records intentional
deletion; missing file uploads cannot do so. Completion reports persisted/persisted_unclean and
never advances account/branch heads. It does not yet authorize terminal Node cleanup.

State quotas check the full directory, each known skill and aggregate root auxiliary data. New
SKILL.md candidates are initially bounded separately, then actual metadata is checked at completion:
invalid candidates stay auxiliary data and cannot split the auxiliary quota. Known invalid skills
retain their identity. New-session composition now also enforces the aggregate auxiliary quota.
This does not yet register account-local skill identities, which remain required before publication.

PostgreSQL evidence: upgrade to 0029, downgrade to 0028 and re-upgrade passed; affected schema and
parent composite constraints match ORM metadata. All 23 finalization service/HTTP cases passed
against that migrated schema, including concurrent begin/complete, changed-key/digest/termination
rejection, expired-attempt renewal, rollback after complete, same-user scope constraints, real
cross-Node credential rejection, bad network bytes, invalid/binary content, complete deletion and
quota reclassification. The same 23 cases also pass on SQLite.

Remaining work is unchanged in scope: publication and linked merge units, conflict storage/resolve,
unclean detachment, complete state commands, account-local identities, legacy takeover/import
exclusion, Node preparation/background transfer/acknowledgements, CLI command/API wiring and both
real backend acceptance paths. Managed public admission remains gated and no backend advertises
skill-manager capability. No commit, release or deployment was performed.

Final Server gate: 515 passed, 15 skipped, 74.51% coverage. Ruff format/lint, Mypy, Chinese
docstring/Pydantic-description checks and whitespace checks passed. The isolated PostgreSQL test
container was removed after migration and integration verification.

## 2026-09-21 — linked directory merge units and account-local identities

Directory merging now derives connected units from explicit member identities and all relative links
in base/current/incoming, including intermediate symlink hops and links removed on one side. Root
auxiliary data forms one scope. Opaque divergence is conservative within each connected unit; one
unit's conflict suppresses the entire publishable result. Nine tests exercise independent updates,
linked databases, removed links, auxiliary scopes, text merges and combined link cycles.

Migration `0030_account_local_skills` adds staged/active/removed account identities, complete-tree
initial revision views and exclusive library/local branch origins. Composite keys prevent cross-account
source/revision/head substitution. Staged same-name candidates retain distinct identities; active
names are account-unique. Internal registration validates real content under the storage user lock,
reuses stable checkpoint/name identities on concurrent retries and never activates candidates or
advances heads. New names that cannot become local identities remain aggregate auxiliary data for
quota accounting.

Exact snapshot selection now includes only active, enabled local skills belonging to that account.
It records account rule provenance and local revision identities, rejects library/local name collisions,
and requires explicit reset/restore for expired branches. Complete original trees retain cross-entry
links, but snapshot composition still requires the current directory dependencies; it cannot silently
copy historical auxiliary state. The user library and pin surfaces remain separate.

Evidence for this increment: Server full gate passed with 540 tests, 15 skips and 74.96% coverage;
Ruff, Mypy, Chinese docstrings and whitespace checks passed. The 34 local/finalization cases pass on
SQLite and PostgreSQL. Migration 0030 upgrade/down/up passed and affected tables match ORM metadata.
With local data present, downgrade refused before mutation and preserved all ten tested identities
and schema version. Publication work starts next; candidate activation is not yet wired to ingestion.
No capability advertisement, commit, release or deployment occurred.

## 2026-09-21 — atomic initial publication and retained conflict attempts

Migration `0031_skill_publications` now preserves owner/account/finalization-bound publication
attempts, current comparison tree references, expected directory heads/epochs, structured conflict
lists and exact exposed-branch head/epoch preconditions. Guarded downgrade refuses to discard any
publication history. Successful, conflicted and detached outcomes retain the original snapshot and
incoming checkpoint; merged results have a separate directory checkpoint identity.

The initial publication service runs under the user storage lock, checks source/state/directory epochs
and advances branch/directory heads through CAS in one transaction. Any invalid changed branch
detaches the whole submission. Unchanged branches do not block unrelated writes merely because their
epoch changed. Default revision updates leave late writes on the original revision branch, including
when the new revision already has a migrated head. A no-change input does not advance any head.

Connected directory merges retain all current unexposed members and never turn snapshot omission
into deletion. Conflicts save all input and comparison references without publishing another item.
Safe invalid/deleted known skills retain their branch identity; later preparation cannot silently
restore the original package. Valid new skills activate account-local identities atomically with
publication. Two sessions creating the same name produce distinct candidate identities and an
explicit source conflict even when bytes match. A failed final directory CAS rolls back prior branch
changes and candidate activation.

The separate authenticated Node `/publish` endpoint rechecks the original Node, active owner and
terminal snapshot binding. It refuses incomplete uploads, returns the original result on retries,
and reports published/conflicted/detached distinctly. It does not expose comparison content through
Node download routes or bypass unresolved conflicts. Finalization completion remains persistence only.

Evidence: 17 publication service cases and seven authenticated Node finalization/publication cases
pass on SQLite and the migrated PostgreSQL 17 schema. Migration 0031 upgrade/down/up passed; affected
columns, keys, indexes and check-constraint names match ORM metadata. With 23 attempts present,
downgrade refused before mutation and preserved schema version and history. Full Server gate passed:
559 tests, 15 skipped, 75.42% coverage, plus Ruff, Mypy, Chinese docstrings and whitespace checks.

Remaining scope includes user conflict inspection/resolve plans and stale-plan recomputation,
state migration/reset/restore/retention/GC, account takeover/import exclusion, Node task preparation
and durable background transfer/acknowledgements, CLI commands/API wiring, distribution and real
backend acceptance. Managed public admission stays gated; no backend capability is advertised.
No commit, release or deployment occurred. The temporary PostgreSQL test container was removed after
verification.

## 2026-09-21 — resolution engine, plan persistence and attempt recomputation

The pure resolution engine now applies explicit path, complete linked-unit or whole-directory
choices against immutable base/current/incoming trees. Custom files require two ordinary file sides;
structural/deletion choices preserve a complete selected subtree. Linked opaque/database state cannot
be split into path choices. Overlapping and unrelated choices are rejected, partial plans expose no
publishable tree, and the complete result is revalidated for cycles, dangling links and types. A
selected modified file whose parent was deleted restores only its required ancestor directories,
without resurrecting unselected siblings. Fifteen pure cases cover these boundaries and strict choice
request shapes.

Migration `0032_skill_resolution_plans` adds owner/account/publication-bound monotonic plans,
independent choice rows with retained same-user custom state-tree references, and immutable user-keyed
operation receipts. Repository queries preserve owner/account boundaries. Internal publication
recomputation now supersedes a conflict and creates a new attempt from the unchanged original input,
using attempt-specific content keys. It retains previous inputs and never copies old choices.
Changed heads are remerged; reset epoch changes detach the whole old input. Repeating a superseded
attempt returns its latest replacement.

This is not a completed user resolve flow. The schema and pure engine are implemented, but no user
endpoint saves a plan, performs dry-run orchestration or executes these choices yet. Query/detail/diff,
user-token HTTP authorization, plan-revision/idempotency transactions, stale-target checks, source
identity handling and final application still need wiring. The precise remaining boundary is recorded
in Server `docs/skill-resolution-plans.md`; no currently available endpoint is claimed to provide it.

Evidence: 23 recomputation/persistence/publication cases pass on SQLite and migrated PostgreSQL 17.
Migration 0032 upgrade/down/up passed, and affected columns/keys/indexes/check names match ORM metadata.
With a saved plan and operation present, downgrade refused before mutation and retained both records
and schema version. Final Server gate: 580 passed, 15 skipped, 75.56% coverage; Ruff, Mypy, Chinese
docstrings and whitespace checks passed. The temporary PostgreSQL test container was removed after
verification. No commit, deployment, release or runtime capability advertisement occurred. All other
remaining cross-repository scope from the previous entry remains active.

## 2026-09-21 — user conflict inspection, custom content and atomic resolution

The Server now exposes user-token-only conflict list/detail/metadata-diff, exact three-side exports,
scoped resumable custom state uploads, transactional resolve and immutable operation lookup by key.
Inputs explicitly label session snapshot, publication comparison and finalization. Upload completion
stores content only. Device/Node/other-user credentials, cross-account cursors and cross-conflict
upload substitutions are rejected. Upload lease timestamps stay identical across initial/retry reads.

Resolution saves nonoverlapping versioned choices under the storage user lock. Key replay precedes
current status/revision checks. Dry-run saves no choices, receipts, replacements or heads. Stale
heads/epochs/source occupancy create a replacement from unchanged original inputs and never copy
choices. Complete results recheck actual branch writes, original revision/epochs/source identity,
content, quotas and dependencies before atomic publication. A late CAS failure rolls back the whole
command. Same-byte candidate collisions still require explicit retention of the current identity.
Custom new valid skills activate as account-local identities only with the complete result.

Additional regression evidence covers full incoming/custom choices after an unchanged branch reset,
removed unchanged source projection/revival, edits to unexposed local members and cyclic links formed
by otherwise valid individual choices. Invalid combined dependencies preserve a pending plan and old
heads, then accept an explicit whole-tree repair. HTTP tests exercise corrupt upload bytes, exact
exports, dry-run, two-step resolution and immutable replay after publication.

Verification: 35 service/API/publication tests passed against PostgreSQL 17 after migration to 0032.
The full Server gate passed: **598 passed, 15 skipped, 76.02% coverage**, Ruff format/lint, Mypy,
Chinese docstring/field-description checks and whitespace checks. No schema change beyond 0032 was
needed. The disposable PostgreSQL container was removed. No commit, deployment, release or backend
capability advertisement occurred.

This supersedes the previous entry's statement that user resolve endpoints were pending. The full
manager remains incomplete: state queries/migration/reset/restore/retention/GC, takeover/import
exclusion, managed admission, Node preparation/transfer/acknowledgements, CLI workflows, distribution
and real Native/Docker Sandbox acceptance remain active work.


## 2026-09-21 — checkpoint history, explicit-baseline diffs and dependency exports

Added user-token-only bounded checkpoint history, detail, historical directory member references,
explicit-checkpoint metadata diff, complete linked-unit tree/file export and separately paginated
pending-upload queries. Item selection uses stable library/account-local identity across versions and
installation epochs; same-name collisions require an ID, archived sources remain readable by ID and
account-local sources cannot cross accounts. Current branch heads and current epochs are labelled
separately from the source session's finalization status.

Item diff uses its own original library package or local initial revision; directory diff uses the
parent checkpoint. Export keeps the selected subtree and its complete connected link dependencies
with original paths, explicitly lists extra roots and excludes independent members. The export digest
is distinct from the complete backing-tree digest. File access is restricted to the export unit and
verifies bytes before streaming. Missing/corrupt bytes produce explicit content errors. Expired
metadata remains inspectable but never produces an invented empty export or baseline.

Finalization now retains an item view even when that known skill was deleted, including detached or
unclean input, while keeping absent entries out of directory membership. Tests verify the resulting
explicit `locally_removed` empty export and deletion diff. Pending uploads stay separate, identify the
source Node and explicitly state that Server does not yet have exportable complete content. New-user
reads, including conflict listing, create no library, usage or branch records.

Verification: 46 history/finalization/publication cases passed on PostgreSQL 17 after all migrations
through 0032; the subsequent 24 query/content cases and six read-only-lock/conflict API cases also
passed there. Latest full Server gate: **610 passed, 15 skipped, 75.90% coverage**, plus Ruff, Mypy,
Chinese docstring checks and whitespace checks. The final read-only-lock follow-up also passed 17
SQLite API cases; format/lint/type checks were rerun afterward. No new migration was required and
the temporary PostgreSQL container was removed.

See Server `docs/skill-state-queries.md` for exact routes, export layout and limitations. This does not
complete current-effective selection/default CLI diff, reset/restore/migrate/prune/retention/GC, pending
Node-local export, CLI destination materialization or the remaining runtime/distribution acceptance.
The entire manager goal remains active. No commit, deployment, release or capability advertisement
occurred.


## 2026-09-21 — effective state selection and atomic reset/restore

Implemented read-only current account selection with independent pin/enabled provenance, precise
revision/installation epoch and optional initialized/expired branch heads, plus default state diff.
The user reset/restore command carries a complete generation/directory/branch precondition and a
persistent idempotency key. Preview validates content, dependencies and scope/user quotas without
creating branches, upload reservations, checkpoints or receipts. It reports both complete directory
changes and each affected branch's own head differences, including old pinned-branch data absent
from the current directory.

Item reset uses the selected immutable original package/local initial state. Restore requires exact
owner/account/stable source/name/revision identity; same-source reinstall history is explicitly
recoverable across installation epochs. Directory restore checks complete effective membership and
reports mismatches. Directory reset clears root auxiliary state and resets enabled effective sources;
nonselected current members and their heads are preserved. All selected branch epochs advance, with
directory epoch advancement for directory scope. Expired or uninitialized selected branches can be
explicitly reset. Library rules/generation stay unchanged and old checkpoints remain recoverable.

The transaction publishes every selected branch and the complete directory through exact CAS, then
saves an immutable receipt. Concurrent duplicate keys replay one result; stale previews cannot
replace a newer head. Late CAS failure rolls back all writes. Old account conflict plans become
superseded without being executed. A later user resolve can recompute the retained original input
without applying or copying choices; old changed-branch epochs detach instead of reviving reset data.

Migration **0033_skill_state_operations** retains owner/account/scope-constrained source/result
checkpoint references and immutable responses. Upgrade/down/up passed on PostgreSQL 17; the new
schema's columns, primary/unique keys, foreign keys and check names match ORM metadata. With real
receipts present, downgrade refused before schema mutation and preserved all 15 inspected receipts.

Evidence: 48 state-command/resolution/publication tests passed on SQLite and PostgreSQL 17. Full
Server gate: **628 passed, 15 skipped, 76.41% coverage**; Ruff, Mypy, Chinese docstring and whitespace
checks passed. The temporary database container was removed. No commit, deployment, release or
runtime capability advertisement occurred.

Remaining full-goal scope includes automatic/incremental state migration and its conflict plans,
retention/prune/GC, account takeover/import exclusion, managed admission and deployment operations,
Node preparation/background transfer/acknowledgements, complete CLI commands/source acquisition,
distribution and real Native/Docker Sandbox acceptance. Explicit reset is not a substitute for state
migration. See Server `docs/skill-state-mutations.md` and the root wire contract for implemented APIs.


## 2026-09-21 — first-use version preparation and durable migration inputs

Added independent Server branch preparation with migration **0034_skill_branch_preparation**.
The last-effective ledger references actual complete snapshot members under account, installation
and installation epoch. Successful reservation updates it; old snapshot retries, previews, failed
reservations, migration attempts and late finalization cannot rewind it. Only-reset branches that
were never reserved do not count as prior use. Historical snapshot members without a trustworthy
ledger fail explicitly instead of guessing from revision order or write timestamps.

The user preparation endpoint supports original initialization, conservative forward migration,
entering an unused earlier registered revision with a warning, and resuming an existing target head.
Forward migration uses the last effective branch's current published checkpoint, skipping unused
intermediate revisions. Explicit old pins keep their existing branch; unpin exposes the new target.
Independent upstream and learned paths survive together. Same-path, opaque database and linked-state
conflicts preserve inputs without moving heads. Link grouping checks both old source and current
directory, including reverse links from auxiliary roots; auxiliary units are labelled `.`.

Preparation receipts have their own identities and explicit old-original/new-original/old-published
side labels, never synthetic sessions or finalizations. First-use success publishes target and
complete directory through head/epoch CAS in one savepoint. Nonselected sources stay intact. Preview
checks actual bytes and aggregate distinct-file storage admission across all retained inputs/result,
without upload or branch writes. Late CAS failure rolls back every reference and receipt. Accepted
keys replay immutable results before current-rule checks; stale previews and changed-key inputs fail.

Conflicts are durable accepted results, separate from successful migration. Reset/restore supersedes
pending preparation under the same transaction and includes those records in its invalidated-conflict
count. Original receipts remain immutable; lookup reports current status separately. A clean target
subsequently resumes without applying cancelled inputs. Late old sessions keep their old branch
changes and do not overwrite the already prepared target.

PostgreSQL 17 verification: **52** preparation/auth/constraint/snapshot/state-command tests passed on
the migration-created schema. Upgrade → downgrade to 0033 → upgrade passed; new columns, primary keys,
unique/FK/check constraints matched ORM metadata. Guarded downgrade with data preserved all **83**
preparation receipts and **139** effective-branch records and left the head at 0034. The disposable
container and its anonymous volume were removed.

This is a first-use preparation increment, not completion of design section 6 or the whole manager.
Migration-specific user conflict resolution/export, explicit incremental migration and last-migrated
baselines, automatic managed-admission preflight orchestration, retention/GC, takeover/import exclusion,
Node preparation/transfer/acknowledgements, full CLI workflows, distribution and real backend acceptance
remain active work. No commit, deployment, release or runtime capability advertisement occurred.

Latest full Server gate for this increment: **652 passed, 15 skipped, 76.81% coverage**, Ruff
format/lint, Mypy, Chinese docstring/field-description checks and whitespace checks all passed.
Log: `/tmp/skill-preparation-quality-complete.log`. PostgreSQL verification log:
`/tmp/skill-preparation-pg-complete.log`.


## 2026-09-21 — explicit incremental revision migration

Implemented Server from/to migration for distinct revisions of the same active library installation
and current installation epoch, including non-effective targets and reverse migration to older
versions. It does not change pins, enabled rules or the last-effective snapshot ledger. Query reports
exact source/target heads and epochs, directory conditions, the latest successful migration and
whether the source has an unmigrated checkpoint. Preview and commit require the same complete state.

Migration **0035_skill_incremental_migration** extends the existing independent preparation journal
with exact source baseline and target current checkpoint references and a successful sequence scoped
by both branches, both state epochs and directory epoch. Automatic first-use forward successes seed
that sequence. Incremental merge uses the latest successful source checkpoint as base and the target's
own published state as current. With no prior success it uses the source original; a missing retained
baseline fails rather than silently replaying all original differences.

Tests prove that a target's deletion of already imported learning survives later unrelated source
additions, and that late old-session data moves only on an explicit request. Repeating an unchanged
source preserves both heads. Conflicts, dry runs and failed CAS never advance the baseline. Reset
supersedes conflicts and starts a new epoch scope, while immutable original receipts remain replayable.
Preview reports target-own changes separately from complete-directory changes and checks actual bytes,
linked/opaque units and aggregate retained-input/result quota without reservations. Final publication,
input roots, successful sequence and receipt share one savepoint; late failure rolls everything back.

Shared original/checkpoint content verification and complete branch/directory publication were
extracted for first-use and incremental paths. No synthetic session or finalization is introduced.
User-token HTTP preview/commit/receipt tests cover distinct side labels and reject other users, Node
and device credentials. Wrong typed receipt endpoints return an explicit operation-kind mismatch.

Verification: **672 passed, 15 skipped, 77.15% coverage**, plus Ruff format/lint, Mypy, Chinese
docstring/field-description and whitespace checks. **72** relevant cases passed on PostgreSQL 17 using
the migrated schema. 0035 upgrade/down/upgrade preserved seven compatible forward receipts and their
original JSON while backfilling sequence 1. Deliberately duplicated incompatible forward history made
upgrade fail atomically without changing the 0034 schema. Columns/nullability, FK column mappings,
unique column mappings and check names match ORM metadata. Downgrade with incremental data refused
before mutation and preserved all 16 incremental receipts, sequences, references and JSON. The
disposable database container and anonymous volume were removed. Logs:
`/tmp/skill-incremental-quality.log` and `/tmp/skill-incremental-pg-tests.log`.

The full manager remains incomplete. Migration-specific conflict inspection/export/resolution,
managed-admission preflight, retention/prune/GC, account takeover/import exclusion, Node preparation
and background transfer/acknowledgements, full CLI commands and source acquisition, distribution and
real Native/Docker Sandbox acceptance remain active. No commit, release, deployment or runtime
capability advertisement occurred.


## 2026-09-22 — migration conflict inspection and exact export

Implemented user-authenticated migration conflict list/detail, bound three-sided metadata diff, exact
saved manifest export and verified side-file download. These routes use independent preparation
identities, including automatic first-use and explicit incremental conflicts. Original responses and
side labels remain immutable; current status and live branch/directory/configuration diagnostics are
reported separately. A conflict-created target without a head is not incorrectly marked stale. A
source's later same-epoch head does not replace saved incoming or masquerade as a reset; concurrent
directory head changes remain separately visible.

Exports preserve full saved trees and original link paths, explicitly listing extra context roots.
The fourth directory side is the saved account context, never substituted for target current state.
File authorization is bound to the selected side, verifies bytes before streaming and releases the
request transaction before network output. Missing/corrupt files and expired directory context fail
explicitly. Reads create no branches, checkpoints, uploads, plans or migration receipts. Removed
sources and superseded conflicts remain accessible through stable authorized identity.

Thirteen new tests cover both migration modes, original side identities, target initialization, linked
and independent context roots, exact exports, read-only behavior, scoped list cursors, attempt-bound
diff cursors (including equal trees and malformed inputs), reset/removal history, source advancement,
last-migrated baseline labels, content faults and rejection of other users/Node/device credentials.

Full Server gate passed: **685 passed, 15 skipped, 77.14% coverage**, plus Ruff format/lint, Mypy,
Chinese docstring/field-description and whitespace checks. **41** migration/preparation/query cases
passed on PostgreSQL 17 after applying the complete Alembic chain to head
**0035_skill_incremental_migration**. No schema changes were needed. Logs:
`/tmp/skill-migration-conflicts-quality.log`, `/tmp/skill-migration-conflicts-pg-upgrade.log`, and
`/tmp/skill-migration-conflicts-pg-tests.log`. The disposable database container and volume were removed.

This completes the inspection/export increment only. Migration-specific versioned resolution plans,
scoped custom uploads, safe linked resolution and stale recomputation remain unfinished, along with
managed admission, retention/GC, takeover/import exclusion, Node task/transfer integration, full CLI
workflows, distribution and real backend acceptance. The original full-manager goal remains active.
No commit, release, deployment or runtime capability advertisement occurred.


## 2026-09-22 — migration custom uploads and resolution persistence

Implemented Server migration **0036_skill_migration_resolution** with independent migration-scoped
upload bindings, completed custom-content grants, versioned plans, selector choices and immutable
operation receipts. Composite foreign keys preserve owner/account/migration throughout; custom
choices can reference only content completed for that exact migration. A matching digest or forged
internal upload-key prefix alone cannot authorize content. Existing preparation JSON is unchanged.

The user API can begin/resume/upload/complete custom files or directory manifests and inspect the
saved plan. Real upload bindings are created in the same savepoint as leases; completed content and
its authorization commit together. Concurrent retries and different uploads of one tree retain one
grant. Already bound keys recover the original lease before current conflict-status checks, including
after reset and lost responses. Superseded conflicts cannot initiate new uploads. Completing existing
edits retains them without restoring publication authority, changing plans or advancing any head or
successful migration baseline. Plan inspection does not initialize a plan.

Plan repository replacement uses revision CAS and a savepoint spanning version advancement and all
choice changes. Constraint failures preserve the prior version and choices, even if the outer request
commits. Content loading rechecks actual bytes and exact migration authorization. This is storage and
upload foundation: the public resolve command, full linked-identity validation, stale recomputation,
complete-result previews and atomic migration publication remain unfinished. No partial resolver is
advertised as complete.

**28** new tests cover actual user HTTP authentication, device/Node/other-user rejection, cross-migration
and forged-prefix isolation, bounded file verification, upload key/manifest consistency, concurrent
completion, expiry, reset recovery, late grant rollback, plan CAS and constraint rollback, completed
custom-tree authorization, corrupt/missing objects, ownership/scope constraints and stable receipts.
**69** migration/preparation/query/upload/persistence tests passed on PostgreSQL 17 across the existing
28-case suite and new 41-case suite. Upgrade → downgrade to 0035 → upgrade preserved all **29** existing
preparation records and original JSON. Columns/nullability, primary keys, foreign-key column mappings,
unique column mappings and check names match ORM. Guarded downgrade preserved **26** upload bindings,
**10** grants, **7** plans, **3** choices, **1** resolution receipt and **74** preparation records, leaving
head 0036. The disposable PostgreSQL container and volume were removed.

Verification logs: `/tmp/skill-migration-resolution-pg-migration.log`,
`/tmp/skill-migration-resolution-pg-existing.log`, `/tmp/skill-migration-resolution-pg-tests.log`.
Full Server gate passed: **713 passed, 15 skipped, 77.39% coverage**, Ruff format/lint, Mypy, Chinese
docstring/field-description and whitespace checks. Schema registration tests include all five new
tables and the new Alembic head. Log: `/tmp/skill-migration-resolution-quality-complete.log`.

The full-manager goal remains active: migration resolution orchestration, managed admission,
retention/prune/GC, takeover/import exclusion, Node preparation/transfer/acknowledgements, CLI workflows,
distribution and real backend acceptance are still required. No commit, release, deployment or runtime
capability advertisement occurred.


## 2026-09-22 — complete migration candidates and read-only resolution planning

Added pure migration resolution over the four saved trees and a read-only Server planner. Target
current state stays distinct from account-directory context. Linked units include reverse links from
the saved directory and require whole-unit choices; independent historical roots in source exports
cannot overwrite current independent sources. Custom directories may carry unchanged context to keep
links valid but cannot modify unrelated sources. Invalid combined links/types return no partial tree.

The planner authorizes the original migration, validates exact custom-content grants and actual bytes,
checks full directory limits and state quotas, and reports target-own, original-package and complete
directory changes separately. It retains the exact target revision and explicitly reports whether the
candidate modifies that revision's original package. Saved member identities define scope and quota;
SKILL.md presence does not create an independent source identity. Calculation changes no plans,
receipts, content reservations, heads or success baselines. Stale comparisons are rejected pending the
full resolver's recomputation path; a valid candidate alone is not linked-source publication authority.

Full Server gate: **745 passed, 15 skipped, 77.65% coverage**, with Ruff format/lint, Mypy, Chinese
docstring/field-description and whitespace checks passing. **67** migration/planner/query/upload/
persistence cases passed on PostgreSQL 17 after upgrading through unchanged head 0036. The disposable
container and volume were removed. Logs: `/tmp/skill-migration-resolution-plan-quality.log`,
`/tmp/skill-migration-resolution-plan-pg-upgrade.log`,
`/tmp/skill-migration-resolution-plan-pg-tests.log`.

This increment does not add public resolve or publication orchestration. Versioned plan editing,
linked-source authorization, stale recomputation and atomic migration publication remain required,
as do managed admission, retention/GC, takeover/import exclusion, Node integration, full CLI workflows,
distribution and real Native/Docker Sandbox acceptance. The full-manager goal remains active.
No commit, release, deployment or runtime capability advertisement occurred.


## 2026-09-22 — internal versioned migration plan edits and immutable draft receipts

Added an internal draft service that edits real migration conflict plans under the user storage lock.
A new choice replaces intersecting saved scopes and preserves independent choices; the complete
remaining plan is revalidated before saving. Custom content retained by the plan must still pass
migration-scoped authorization and byte verification. An explicitly replaced custom choice need not
be loaded again, allowing a damaged draft to be replaced safely.

Dry-run returns the current revision with no writes. Save uses plan-revision CAS and stores the full
original typed response in the same savepoint. Concurrent duplicate keys replay one acceptance;
different commands competing for one revision cannot both save. Replay precedes later version/status/
drift checks and remains immutable after subsequent edits or reset. Receipt lookup separately labels
the migration's current status. Late receipt failure rolls back both newly created and existing plans,
including when the outer transaction catches the error and commits.

The type `migration_resolution_draft` reports `planned` and `candidate_complete` separately. Even a
complete candidate creates no checkpoints/uploads, advances no head or migration sequence, and leaves
the original preparation response intact. This is an internal component with no public mutation route.
Final linked-source authorization, stale recomputation and atomic resolve publication remain required.
Historical related-source epochs cannot be inferred from current branch IDs or equal tree digests;
this evidence gap and the current single-branch publisher boundary are recorded in the Server design.

All **17** draft cases passed on SQLite and PostgreSQL 17. PostgreSQL also passed the **49**-case
combined draft/planner/persistence suite before the final additional rollback case; the final draft
suite then passed independently. The migrated head remains 0036 and the disposable database container
and anonymous volume were removed. Logs: `/tmp/skill-migration-drafts-targeted-final.log`,
`/tmp/skill-migration-drafts-pg-upgrade.log`, `/tmp/skill-migration-drafts-pg-tests.log`,
`/tmp/skill-migration-drafts-pg-final.log`.

The entire manager remains incomplete: the final migration resolver, managed admission, retention/GC,
account takeover/import exclusion, Node preparation/transfer/acknowledgements, complete CLI workflows,
distribution and real Native/Docker Sandbox acceptance remain active. No commit, release, deployment
or runtime capability advertisement occurred.

Final full Server gate for this increment: **762 passed, 15 skipped, 77.75% coverage**. Ruff
format/lint, Mypy, Chinese docstring/field-description checks and whitespace checks all passed.
Log: `/tmp/skill-migration-drafts-quality-final.log`.


## 2026-09-22 — immutable checkpoint provenance and linked migration identity checks

Added migration **0037_skill_checkpoint_provenance**. Item checkpoints now record their creation
state epoch and exact backing-directory identity where one exists; directory checkpoints record their
creation directory epoch. A composite owner/account/scope/content-digest foreign key prevents another
user, account, item or different complete tree from substituting for that backing context. Legacy
unknown provenance stays null. Independent package initialization creates no invented directory.

All production checkpoint creation paths now record their actual epochs/context: initial branches,
local initial views, raw finalization inputs, ordinary and manual publication, first-use/incremental
migration, and reset/restore. Raw late input keeps its snapshot epochs after a reset. Reset/restore
records the resulting new epochs and preserves old metadata. Deleted item views keep their backing
reference without requiring directory membership; unchanged members retain their original item and
backing. Checkpoint list/detail and directory member queries expose historical epochs separately from
current epochs. Retiring content does not erase the backing identity proof.

Complete migration candidates now validate actual changed related targets and all stable members
selected by a whole incoming choice. Historical source members come only from the source item's exact
backing directory. Matching bytes do not authorize a different source/revision or a pre-reset member
epoch. Missing history produces STATE_PROVENANCE_UNAVAILABLE; invalid identity and epoch produce
explicit errors. Same-identity same-epoch historical related content remains explicitly selectable.
Custom directories target saved current identities. Final write-lock/CAS validation is still required.

**25** new cases cover creation paths, late raw inputs, deletion, historical HTTP metadata, actual
cross-account/user/content/scope constraints, provenance after content retirement, linked same-epoch
history, equal-byte reset/reinstall rejection, missing evidence and explicit custom results. **109**
relevant cases passed on PostgreSQL 17 across the 70-case provenance/publication/migration/preparation/
manual-resolution suite and the 39-case linked-source/planner/draft suite.

Guarded downgrade preserved all **778** checkpoints (including **661** with new provenance) and all
preparation records/JSON at head 0037. In the disposable database, clearing only the new fields to
simulate legacy data allowed downgrade to 0036 and re-upgrade; all 778 legacy records and original
JSON stayed unchanged, with missing provenance still null. Columns/nullability, primary keys, unique
column mappings, foreign-key column mappings, check names and removed temporary defaults match ORM.
The temporary database container and volume were removed. Logs:
`/tmp/skill-provenance-pg-upgrade.log`, `/tmp/skill-provenance-pg-tests.log`,
`/tmp/skill-provenance-related-pg-tests.log`, `/tmp/skill-provenance-pg-audit.log`, and
`/tmp/skill-provenance-pg-migration.log`.

This closes the identified creation-evidence gap for new history and adds linked candidate identity
validation. Multi-branch atomic migration publication, stale recomputation and public resolve remain
unfinished, along with managed admission, retention/GC, takeover/import exclusion, Node integration,
complete CLI workflows, distribution and real Native/Docker Sandbox acceptance. The full-manager goal
remains active. No commit, release, deployment or runtime capability advertisement occurred.

Final full Server gate: **787 passed, 15 skipped, 77.85% coverage**; Ruff format/lint, Mypy,
Chinese docstring/field-description and whitespace checks passed.
Log: `/tmp/skill-provenance-quality-final.log`.


## 2026-09-22 — atomic multi-branch migration resolution and user API

The final migration resolution service now combines version-CAS plan edits, exact multi-branch and
complete-directory publication, successful migration sequence, and a typed immutable receipt under
one user write lock/savepoint. Partial choices save a pending plan only. Complete previews validate
bytes, scope, linked identities, epochs, quota and sequence bounds without writes. Every written branch
has its own current/original diff and exact source/revision/installation/state-epoch identity; local
sources use their own initial revision. Unchanged related members retain their checkpoint/backing;
deleted members keep their new historical item view but leave directory membership. The legacy
single-branch publication wrapper explicitly rejects hidden related writes.

Success updates the migration's status/result/sequence without altering original source inputs or the
first preparation response. The next migration baseline is the exact saved source checkpoint, even if
its live head advanced later. Newer successful migrations cannot be rewound by an old conflict.
Initial and older preparations can genuinely conflict on dangling links; explicit custom repair (or
valid older incoming) preserves the mode and leaves migration sequence null. Initial input cannot
claim related named source identity without a historical checkpoint. New unrelated skill roots cannot
be smuggled into an auxiliary custom scope.

Added user-only, feature-gated routes:

- POST `/api/v1/skills/state/migration/conflicts/{id}/resolve`.
- GET `/api/v1/skills/state/migration/resolution-operations?key=...`.

The API connects the existing migration-scoped uploads and plan query to preview, partial-plan save
and complete atomic publication. Typed final receipts reject internal drafts. Key replay precedes
current version/status/drift checks and returns the original pending/published response; receipt lookup
separately exposes today's migration status. The original preparation and its side exports remain
immutable. HTTP and service late-failure tests ensure no partial heads, plans or success baselines
survive even if a caller handles the error or retries a lost response.

**24** new service/preparation cases cover forward/incremental and initial/older modes, both retained
sides, custom repairs, pending-to-published plans, linked library/local branches, deletions, same-key
concurrency, sequence exhaustion, scope/owner/type boundaries, reset replay, and injected branch,
directory, migration-row and receipt failures. The **108**-case PostgreSQL 17 suite passed at head
0037. **11** additional HTTP cases cover upload-to-resolution flow, real user/device/Node/other-user
credentials, concurrent key replay, immutable receipt status, version/key/type errors, strict request
validation, stale/reset refusals and late HTTP rollback/retry.

Remaining protocol gap: stale comparisons are explicitly rejected, not recomputed. Preserved-input
replacement attempts/links and reset/restore/reinstall supersession semantics still need their complete
implementation. Managed admission, retention/GC, takeover/import exclusion, Node transfer and durable
acknowledgements, complete CLI workflows, distribution and real Native/Docker Sandbox acceptance also
remain unfinished. The full-manager goal remains active; these APIs do not advertise runtime capability.
No commit, release or deployment occurred.

Logs: `/tmp/skill-atomic-resolution-quality-final.log` (service gate: **811 passed, 15 skipped,
78.06% coverage**), `/tmp/skill-atomic-resolution-pg-final.log` (**108 passed**),
`/tmp/skill-migration-resolution-api-final.log`, `/tmp/skill-migration-resolution-api-pg.log`,
and `/tmp/skill-atomic-resolution-api-quality-final.log` (final API-inclusive gate).

Final API-inclusive full Server gate: **822 passed, 15 skipped, 78.18% coverage**. Ruff format/lint,
Mypy (**327 source files**), Chinese docstrings/field descriptions and whitespace checks passed.
The **11** HTTP cases also passed on PostgreSQL 17, making **119** relevant PostgreSQL cases in this
increment (108 service suite + 11 HTTP suite). No schema change; head remains 0037. The disposable
`skill-atomic-resolution-pg` container and anonymous volume were removed after all PostgreSQL checks.


## 2026-09-22 — retained-input stale migration recomputation

Added migration **0038_skill_migration_replacement** with nullable owner/account-bound predecessor and
replacement references plus supersession reason. A unique predecessor prevents forks; self references
and replacement metadata on active rows are rejected. Legacy relations remain unknown. Conflict
summary/detail and original preparation/migration/final-resolution receipts expose current replacement
and reason separately from immutable original responses.

Resolve now classifies stale comparisons before applying a submitted choice. Same-epoch head changes
create one replacement from the exact retained source checkpoint, original baseline, current target
and current directory. Source head advances never substitute for saved incoming. Historical linked
context comes from the original source checkpoint. No choices or custom grants transfer to the new
attempt. New conflicts start with an empty plan; clean recomparisons may publish atomically. The old
request still returns superseded, with a replacement ID, rather than claiming its own success.
Dry-run classifies the change and saves nothing. Existing-key replay remains immutable, and new
requests on the superseded record return its existing relation without creating another child.

Reset/restore retains distinct reasons and never recreates a publishable old comparison. Changed
installation/branch/directory epochs, expired state, removed or reinstalled linked sources terminate
the old attempt. Newer successful migration baselines supersede older conflicts and cannot be rewound.
First-use preparation stops when its target is no longer selected/included; explicit incremental
migration retains its exact requested direction independently of pin changes. Initial/older
recomputation preserves initialization semantics and never silently imports newer learning or creates
a migration sequence. Late final receipt failure rolls back the replacement, links, heads and baseline.

**25** new cases cover recomputation, original choices/input preservation, different-key and concurrent
same-key retries, clean publication, source-head isolation, initial/older modes, reset/restore,
configuration selection and accurate new rule provenance, linked removal/reinstall, and direct database scope/status/one-child
constraints. Existing HTTP stale and newer-success tests now verify the superseded/replacement contract.
PostgreSQL 17 passed **111** related cases (106 main suite plus 5 invalidation cases).

PostgreSQL inspection matched ORM columns/nullability, primary key, **13** foreign keys, **4** unique
constraints and **11** check-constraint names. Guarded downgrade preserved all **134** preparation
records and their exact original fields/JSON, including **27** records with replacement metadata, at
head 0038. In the disposable database only, clearing the three new columns simulated legacy data;
0038→0037→0038 preserved all 134 original records and kept unknown relations null. The temporary
container and anonymous volume were removed. Logs: `/tmp/skill-recomputation-pg-upgrade.log`,
`/tmp/skill-recomputation-pg-tests.log`, `/tmp/skill-recomputation-pg-invalidation.log`,
`/tmp/skill-recomputation-pg-audit.log`, `/tmp/skill-recomputation-pg-downgrade.log`, and
`/tmp/skill-recomputation-pg-roundtrip.log`.

The full manager remains incomplete. Broader lifecycle-triggered supersession and interleaving audits,
managed admission, retained-history GC, takeover/import exclusion, local-skill user commands, Node
transfer/acknowledgements, full CLI workflows, distribution and real Native/Docker Sandbox acceptance
remain active. No commit, release, deployment or runtime capability advertisement occurred.

Additional refinement: account-wide reset/restore cancellation no longer prevents an unrelated skill's
retained input from being recomputed. The resolver checks actual source/target/directory and related
epochs before creating a single empty-plan replacement; the reset skill remains unchanged. Two new
cases cover independent reset/restore. Linked-unit epoch invalidation is still conservative across
the saved unit; the remaining interleaving audit must distinguish actually changed and unchanged
related members before full design completion. Proactive invalidation on library removal/reinstall
and new successful migration also remains to be integrated across lifecycle writers.

Final refinements were also verified on PostgreSQL: the 15-case recomputation/invalidation suite
passed after the real rule-provenance correction; the 8-case invalidation suite passed after independent
reset/restore handling. These overlap the preceding 111 cases; they are repeat regression evidence,
not additional distinct-case counts. Logs: `/tmp/skill-recomputation-pg-provenance-final.log` and
`/tmp/skill-recomputation-pg-epoch-final.log`. All temporary test containers/volumes were removed.

Final gate against the complete current Server tree: **847 passed, 15 skipped, 78.39% coverage**.
Ruff formatting/lint, Mypy (**332 source files**), Chinese docstrings/field descriptions and whitespace
checks all passed. Log: `/tmp/skill-recomputation-quality-verified.log`. Earlier quality logs reflect
intermediate revisions; this is the final verification after both metadata and independent-reset fixes.

## 2026-09-22 — precise linked writes and proactive migration lifecycle invalidation

Migration recomputation now derives related writes from a retained complete candidate's actual
changes against its saved directory. Without a complete candidate, incoming differences provide the
conservative write boundary. Untouched linked members no longer terminate a comparison solely because
they were reset, restored, removed, reinstalled or switched to another revision. Fresh current choices
use the new saved directory and retain those members' exact checkpoints and heads. Changed related
members still invalidate the entire old attempt. Missing current membership cannot silently replace
an old written identity. No saved choices or custom-content grants transfer to a replacement.

Whole incoming choices continue to require exact historical source identities and epochs, even for
identical bytes; they now also reject inactive removed/reinstalled sources when their bytes would be
unchanged. This does not prevent a fresh current choice from retaining an untouched related member.

Library mutations proactively supersede pending attempts targeting removed or outdated installation
identities. First-use preparations additionally evaluate each account's actual included revision,
preserving independent account/tool overrides, pinned targets and explicit incremental directions.
All four successful forward/incremental writers (preparation, explicit migration, resolution and
recomputation) now supersede old conflicts in the same owner/account/installation/direction/epoch
scope. The replacement points to the successful attempt. Recomputed parent records retain their
separate replacement CAS; initial/older success never becomes an incremental baseline.

Added **33** regression cases: 11 linked-member cases, 17 lifecycle cases, 3 scope/epoch cases and
2 late-failure rollback cases. Library and resolution failure tests catch errors inside an outer transaction and then commit
that transaction, proving the inner savepoint restores old conflicts, heads, plan versions and library
configuration. Existing changed-linked-source removal/reinstall cases now use actually changed input.
The **127**-case PostgreSQL 17 regression passed, including linked sources, recomputation, lifecycle,
resolution, library, preparation and explicit migration. Log: `/tmp/skill-lifecycle-pg.log`.
The disposable `skill-lifecycle-postgres` container and its anonymous volume were removed.

A subsequent same-epoch success also links a previously reset/restore-cancelled attempt when it has
no replacement yet. Existing replacement links remain unchanged; different target directions and
actual source/target/directory epoch changes remain outside the supersession scope.

No schema change; Alembic head remains 0038. Broader interleaving coverage, managed admission,
retention/GC, takeover/import exclusion, account-local user commands, Node transfer/acknowledgements,
CLI remote workflows, deployment documentation and real Native/Docker Sandbox acceptance remain
unfinished. The full-manager goal stays active. No commit, release, deployment or runtime capability
advertisement occurred.

After the final cancelled-attempt linkage refinement, **50** focused lifecycle/recomputation cases
also passed on PostgreSQL 17. They overlap the earlier 127-case regression and are not an additional
50 distinct scenarios. Log: `/tmp/skill-lifecycle-pg-final.log`. The final disposable PostgreSQL
container and anonymous volume were also removed.

Final Server gate after all lifecycle refinements: **880 passed, 15 skipped, 78.51% coverage**.
Ruff formatting/lint, Mypy (**338 source files**), Chinese docstrings/field descriptions and whitespace
checks passed. Log: `/tmp/skill-lifecycle-quality-final.log`. The earlier 875-case
`/tmp/skill-lifecycle-quality.log` predates the final five lifecycle/scope cases.


## 2026-09-22 — full-account preparation and public managed session admission

The existing session creation service now holds the user content lock from mode selection through
full-account preparation, session/task creation and exact snapshot reservation. All mutations share
one outer savepoint. Invalid content, quota, capability, snapshot or audit failure rolls back the
entire attempt even if the caller catches the error and commits its transaction. Session errors use
the existing API envelope. Natural preparation conflicts instead commit retained migration inputs
and return `STATE_MIGRATION_REQUIRED`, all migration IDs and `preparations_committed: true`, without
creating a session/task/snapshot or updating the effective-use ledger.

Uninitialized included library targets use the existing first-use preparation service; published
heads are preserved, local sources enter through complete-directory composition, and expired targets
require explicit recovery. Normalized complete-precondition keys prevent empty target creation from
duplicating conflicts on retry. Internal key prefixes confer no authority: saved type, preconditions
and exact target identity are validated before reuse. Explicit user resolution permits a later launch.

Managed admission requires an enabled feature switch, explicit backend availability and a fresh,
complete per-backend protocol/manifest/copy/finalization/recovery report. Strict integer and boolean
checks reject coercion. Heartbeat normalization revokes malformed replacement reports despite Python
JSON equality between booleans and integers. Idle accounts can select a compatible alternate Node;
active accounts remain pinned. A final fresh Node read prevents stale ORM capability from surviving
preparation. Empty managed accounts still receive a snapshot; legacy/migrating accounts cannot bypass
required takeover, while legacy empty accounts retain the existing launch behavior.

Tasks carry only strict protocol/manifest versions and exact snapshot/task UUIDs. Leased Node reads
validate these pointers in addition to their existing owner/account/session/backend/lease boundary.
The fixed snapshot retains Server-selected system release references; their actual Node consumption
and verification remain unfinished. This increment does not alter any real Node capability report.

Added **32** cases covering both backend labels, learned-state migration plus another enabled skill,
multiple retained conflicts and stable retries, forged public key collisions, final snapshot/audit
rollback, stale cached Node capability, empty managed accounts, takeover guards, candidate selection,
real HTTP conflict-resolution-retry, authenticated lease-bound downloads and malformed heartbeat/task
versions. PostgreSQL initially exposed two test-isolation assumptions: global row counts and candidate
Nodes from prior cases. Tests now scope the effective-use count to the owner and use an isolated
region for each account; production scheduling remains unchanged.

The complete manager remains unfinished: takeover/import exclusion, retained-history GC, local-skill
commands, Node transfer/helper wiring/durable acknowledgements, CLI workflows, distribution and real
Native/Docker Sandbox acceptance remain required. Docker control-plane coverage is not Docker Sandbox
runtime acceptance. No schema migration, commit, release, deployment or capability advertisement was
performed; Alembic head remains **0038_skill_migration_replacement**.

Final Server gate: **912 passed, 15 skipped, 78.97% coverage**. Ruff formatting/lint,
Mypy (**345 source files**), Chinese docstrings/field descriptions and whitespace checks passed.
Log: `/tmp/skill-admission-quality-verified.log`. Earlier admission gate logs predate the final
strict-pointer test fixture fix and are not the final verification.

Final PostgreSQL 17 regression: **82 passed** across admission, snapshots, exact Node content,
preparation and runtime lifecycle. Log: `/tmp/skill-admission-pg-verified.log`. The earlier 79-case
run predates the three final capability/pointer cases; counts overlap. The disposable
`skill-admission-postgres` container and anonymous volume were removed and their absence verified.


## 2026-09-22 — explicit CLI exclusion for legacy configuration imports

`account import-config --exclude-skills` now removes `~/.claude/skills` before discovery results,
confirmation, file collection and upload. The existing request exclusion list also includes the root;
no Server schema change is required. Default imports retain skills. Plugin-provided skills and
optional project/history content keep their independent selection rules. Empty results use the
existing no-files behavior. English/Chinese READMEs and CLI architecture rules explain the option.

Three filesystem tests cover default behavior, exclusion before an oversized skill can be read,
plugin/history preservation and an account containing only skills. A CLI help contract test exposes
the new flag alongside the existing preview/history flags. This option does not provide managed
ownership enforcement: Server planning rejection, Node execution rechecks and atomic takeover/import
draining remain unfinished.

Final CLI gate passed: **307 Rust tests**, shell syntax checks, rustfmt, Clippy with warnings denied,
Ruby release-workflow contracts, managed-tool cache checks and whitespace checks.
Log: `/tmp/skill-import-exclusion-cli-quality.log`. No commit, release or deployment occurred.


## 2026-09-22 — configuration import planning and execution ownership checks

Server planning now checks all include/file paths under the user content lock, including paths hidden
outside include or behind a client-supplied exclusion. Migrating/managed ownership rejects the entire
batch before profile, task or audit mutation. The guard remains active when the skill feature switch
is disabled. The original task start endpoint also checks queued legacy imports against today's mode.

A new Node-authenticated exact-task authorization route validates task type, Node, live lease,
active owner, account and tool before returning mode/epoch and bound identities. Node uses its
`internal/api` client, checks every identity and requires a known mode and explicit integer epoch.
Old/empty/malformed responses and unavailable Servers fail closed; rollout requires Server first.
Tasks cannot self-report legacy mode. No file content or host path appears in authorization responses.

The import implementation now preflights the complete batch before any filesystem mutation, checking
ownership, safe lexical paths, base64 and the existing independent config-import resource ceilings.
Late bad content/path and owned skill paths cannot leave earlier settings written. Managed accounts
can still import ordinary config, plugin content and explicitly selected history. Worker start-time
ownership denial is journaled with `SKILL_MANAGER_OWNS_PATH`; completed task replay reports the saved
result without touching later edits.

Added **19 Server cases** and **12 Go top-level tests** with additional subcases. Tests cover mixed
batches, dry-run, HOME alias, hidden file paths, feature-off ownership, ordinary config/plugin imports,
legacy tasks after mode change, expired/pending/terminal/type/owner/account boundaries, malformed
responses, wrong returned identities, unavailable authorization, preflight failures, durable denial
and successful replay. **51 PostgreSQL 17 cases passed** across the new Server cases and prior public
session admission tests. Log: `/tmp/skill-import-pg.log`.

Full account takeover remains required: new-import exclusion, draining queued/in-flight legacy tasks,
local writer exclusion, stable source capture and atomic directory authority commit are not supplied
by one fresh authorization response. In particular, expiry/cancellation alone is not quiescence.
Configuration writes now use no-follow directory handles and complete target preflight on Linux/macOS.
Symlinked user/account/config directories, non-skill aliases into skills, leaf links and batch path
collisions are rejected before any mutation. Configured-root aliases remain supported, and replacing
hardlinked target files preserves the other links. Temporary files and parent directories are fsynced.
The **9-case Linux import suite**, including subcases, passed in a disposable Debian container using
the cross-compiled real package test binary. Log: `/tmp/skill-import-linux.log`. This is filesystem
evidence, not Native/Docker Sandbox runtime acceptance. Takeover's writer exclusion and eventual
privileged-helper integration remain required; pathname safety alone is not writer quiescence. No Node advertises skill-manager support. No schema migration, commit, release or
deployment occurred; the complete-manager goal remains active.


Final Server gate: **931 passed, 15 skipped, 78.99% coverage**; formatting/lint, Mypy
(**350 source files**), Chinese docstrings/field descriptions and whitespace checks passed.
Log: `/tmp/skill-import-server-quality.log`. PostgreSQL's `skill-import-postgres` container and
anonymous volume were removed and their absence verified after the 51-case regression.

Final Node gate passed after all no-follow/preflight changes: shell syntax, generated-policy checks,
gofmt, go vet, all Go tests and coverage, installer tests, managed/official-skill consistency,
Ruby release contracts and whitespace. Log: `/tmp/skill-import-node-quality-final.log`.
The earlier `/tmp/skill-import-node-quality.log` predates the no-follow filesystem refinement.


## 2026-09-22 — serialized Helper imports and persistent account fences

The worker now obtains and validates fresh exact-task authorization, clears any remote account path,
then calls the Linux Helper's `import_account_config` operation. The Helper selects the configured
account root and existing Native/Docker non-root identity; the worker no longer performs account
configuration filesystem writes. Newly created account descendants and replacement files receive
that identity without recursively changing existing directories. Unknown backend/root/UID/path/task
fields are rejected. Non-Linux Helper imports fail explicitly.

Helper serialization and private SkillStateRoot now protect immutable account fences and exact-input
import receipts. A nonlegacy grant closes the fence, including on completed replay; an older legacy
grant cannot reopen it after restart. Corrupt/unsafe/foreign records fail closed. No reset/delete API
exists, and privileged metadata deletion or store relocation is not a supported rollback. Ordinary
configuration remains importable while the account-level skills root is fenced.

Receipts bind the original task, Node/user/account and a digest of backend/files plus the selected
account path. They contain no configuration bytes. Intent is fsynced before writes, followed by an
immutable success/failure outcome. Successful replay leaves later edits intact; changed task input
is denied. Interrupted intent returns `CONFIG_IMPORT_PENDING`, saved failure returns
`CONFIG_IMPORT_FAILED`, and worker task reporting preserves these content-free codes. A terminal
Server task does not establish that a pending Helper receipt is drained. Fresh mode/epoch is checked
separately from immutable input, so successful replay can also close a newly required fence.

The former 1 MiB transport bound could not carry the already permitted 8 MiB raw import. Only the
one-task polling response and Helper import frames now allow 16 MiB; ordinary calls retain 1 MiB.
Server and Node additionally bound encoded file-list JSON to 12 MiB while preserving 1 MiB/file and
8 MiB raw total. The Server conservatively counts Unicode and HTML-sensitive JSON escapes and rejects
oversize before profile/task/audit mutation. Deployment notes require Server first, then coordinated
worker/Helper upgrades and consistent backup of private import metadata with account data.

Added persistent fence/receipt, ownership, restart, stale-grant, forged-input, worker delegation,
stable-error, response-bound and encoded-quota coverage. `tests/linux_config_import_test.sh` is now
part of Node CI. It runs actual cross-compiled Go package tests as root in a disposable Linux
container: **3** fence/receipt tests, **6** Helper import tests and **9** import filesystem tests,
with additional subcases. The Helper test sends **8 × 1 MiB** through the real Client/Server Unix
socket and verifies every file. A real non-root reader traverses the Helper-created private account
directories without relaxing their permissions. Only Go-created test fixture ancestors receive
traverse permissions; custom TMPDIR ancestors and private SkillStateRoot remain untouched.
Failed receipt replay after repairing a filesystem obstacle also leaves configuration unwritten.
Log: `/tmp/skill-fence-linux-final.log`. Containers use `--rm` and test binaries are removed by a trap.

Final Server gate: **932 passed, 15 skipped, 79.00% coverage**; Ruff format/lint, Mypy (**350 source
files**), Chinese docstring checks and whitespace passed. Log: `/tmp/skill-fence-server-quality.log`.
PostgreSQL 17 regression: **52 passed**, split into 29 configuration-import/public-admission cases
and 23 preparation/capability/scheduling cases. Logs: `/tmp/skill-fence-pg.log` and
`/tmp/skill-fence-pg-admission.log`. The disposable `skill-fence-postgres` container and anonymous
volume were removed and their absence verified.

Node full gate passed, including **60.7% statement coverage**, vet, formatting, shell/installer,
managed-skill/release contracts and whitespace. Log: `/tmp/skill-fence-node-quality.log`.
Final Linux verification includes the subsequent test-only permissions tightening and corrected
receipt-test selector; shell syntax and release workflow contracts were checked after CI wiring.

This completes the import/fence prerequisite, not account takeover. Still required: legacy session
and account-binding writer quiescence without force stopping, queued/in-flight import draining,
stable original-directory capture/upload, one Server authority commit and verified abort/rollback.
Node managed snapshot transfer/finalization acknowledgements, retention, account-local user commands,
full CLI workflows and real Native/Docker Sandbox acceptance also remain unfinished. Linux container
tests are not backend session acceptance. No runtime capability was advertised and no schema
migration, commit, release or deployment occurred; head remains **0038_skill_migration_replacement**.


## 2026-09-22 — exclude delayed legacy runtime writers during takeover

Server binding and backend-migration planning now acquire the user content lock before refreshing
directory mode. Migrating/managed accounts return `MIGRATION_PENDING` before account/profile/task/audit
changes, including when the feature switch is disabled. A caller that catches the error and commits
still leaves those records unchanged. Existing legacy accounts keep their original flow. These are
legacy-directory operations; reopening them for managed accounts needs a dedicated snapshot/retention
adapter, not a capability flag or removal of the guard.

The Node Helper applies its persistent account fence before all five existing legacy writer paths:
Native/Docker session launch, Native/Docker account binding, and backend migration. Native's internal
launch boundary checks again. A task cannot bypass the guard by claiming managed mode or a snapshot
ID. The existing managed Native mount path still validates its exact private snapshot and runtime
binding. Completed tasks replay their saved result without relaunching. The worker preserves the
content-free `MIGRATION_PENDING` error code. Existing inspection and explicit stop remain available;
the admission guard never sends a stop/kill command to an existing legacy writer.

Docker now derives account paths from the checked identity instead of honoring task-selected
`account_remote_path`. Existing user/account/config/discovery ancestors receive no-follow descriptor
preflight; a filesystem alias cannot pass that preflight as another account directory. The configured
account root may still be an administrator-selected alias. This check does not establish exclusion
of already running writers or a stable takeover capture.

A new Linux admission test exposed a prior persistence flaw: a dangling fence symlink was returned
as not-found by `os.Root.OpenFile`, so an execution check could reopen the account. The previous
test proved only that the unsafe record could not be replaced. Private JSON reads now use kernel
`openat(O_NOFOLLOW)` against a verified private directory and permit only flat record names.
Direct reads reject both dangling links and links to valid private records; Helper tests also prove
that neither runtime admission nor skill imports reopen on corrupt/unsafe/foreign records.
The shared fix applies to snapshot, baseline, termination and finalization metadata as well as fences.

Added **11 Server tests** for both planning paths/modes, feature-off behavior, catch-and-commit
atomicity, real HTTP errors and stale ORM refresh. Added **9 Go top-level tests** for all five delayed
writer paths, restart, unsafe/foreign metadata, direct Native launch, saved replay, Docker path
substitution, six filesystem-alias positions, legacy store compatibility, configured-root aliases,
explicit stop availability and safe worker error reporting. Existing fence tests gained stronger
direct-read assertions. No schema change, commit, release, deployment or capability advertisement.

Final Server gate: **943 passed, 15 skipped, 79.02% coverage**; Ruff, Mypy (**352 source files**),
Chinese documentation checks and whitespace passed. Log: `/tmp/skill-writer-server-quality.log`.
PostgreSQL 17: **40 passed** across writer guards, config imports and public admission.
Log: `/tmp/skill-writer-pg.log`. The disposable `skill-writer-postgres` container and anonymous volume
were removed and their absence verified. Head remains **0038_skill_migration_replacement**.

Node full gate passed with **60.5% statement coverage**, vet/formatting, installer/shell checks,
managed/official-skill consistency, release contracts and whitespace.
Log: `/tmp/skill-writer-node-quality-final.log`. The earlier writer gate predates filesystem-alias
preflight. The final Linux writer/import run includes the subsequent test-only explicit-stop case:
**24 top-level tests passed**, with additional subcases; `/tmp/skill-writer-linux-final.log`.
The complete Linux copy/journal suite also passed after the shared metadata reader fix:
`/tmp/skill-writer-copy-linux.log`.

Actual Bubblewrap/mount tests passed for both aliases, system readonly content and busy unmount:
`/tmp/skill-writer-mount-linux.log`. The real isolated systemd lifecycle passed all six synthetic
terminal-program cases (normal, error, SIGKILL, cooperative exit, canonical interrupt and forced stop):
`/tmp/skill-writer-systemd-linux.log`. This proves that the new admission check and metadata reader
preserve the existing Native primitive; it is not real Claude or Docker Sandbox acceptance.

Full takeover is still unfinished. Next work must persist the takeover operation, enumerate legacy
session/binding resources and imports, prove writer quiescence, capture/upload stable original content,
and atomically publish account-local identities plus directory authority with verified retry/rollback.
The complete-manager goal remains active, including all other pending runtime, CLI and retention work.

## 2026-09-22 — durable Server first-takeover transaction

Migration `0039_skill_account_takeover` and the internal `SkillAccountTakeoverService` now retain
one exact Node task, immutable legacy writer inventory, first directory epoch, Helper capture
identity, current scoped upload and original committed checkpoint. Reservation uses the user
storage lock and a savepoint to publish migrating mode, inventory, task and receipt together.
Historical cancelled/expired/failed bindings, sessions, imports and backend migrations remain in
the inventory; unknown original backends stay unknown. Ordinary non-skill imports do not block it.
No public takeover route, automatic session dispatch or runtime capability is enabled.

Each capture/file/complete request verifies the active owner, exact Node/task/payload and live
lease. The strict capture declaration fixes the Helper receipt, directory epoch, inventory digest
and complete tree; changed input under the same receipt is rejected. Current control-plane writers
must be terminal and a subset of the retained inventory. These checks do not prove local process
quiescence. Helper drain, stable original-source retention and local extra-resource inspection
remain required before this service can be exposed through orchestration.

Publication verifies actual bytes, system exclusions, skill format and aggregate auxiliary quotas.
The complete directory and all account-local identities/revisions/branches/members commit with one
exact epoch/null-head CAS. Invalid new skill folders remain auxiliary content. Same-name library
installations do not replace manual sources; subsequent session preparation reports the conflict.
Late publication failure rolls back all new references even if the caller catches the exception and
commits. Committed retries retain the original receipt while preserving later directory heads/epochs.
Expired uploads renew only the same capture, and stale attempts cannot write or complete.

Added **72 takeover tests**. The final focused SQLite run, including persistence metadata tests,
passed **89 cases** (`/tmp/skill-takeover-focused-final.log`). The final PostgreSQL 17 run passed all
**72 takeover cases** (`/tmp/skill-takeover-pg-final.log`), including independent-connection races
for reservation, upload binding and completion; one task/upload/checkpoint survives each race.
Coverage includes exact authorization and JSON boolean/integer distinctions, historical writer
inventory, natural drain, new/foreign writers, immutable inputs, expired upload attempts, missing
bytes, mixed trees and source conflicts, real quotas, and late failure rollback. Database tests
bypass services to verify phase checks, Node/task binding, composite upload/checkpoint ownership,
digest/scope and unique account/key/task constraints. Session history validation now returns stable
`STATE_WRITERS_UNKNOWN` for malformed original metadata.

A disposable PostgreSQL 17 instance applied the migration chain from scratch, twice downgraded
0039 to 0038 and upgraded again while preserving an existing legacy account's mode/epoch/head.
After reservation, downgrade was refused before mutation; version, receipt, task, migrating directory
and all **13 database constraints** remained intact. Log: `/tmp/skill-takeover-migration-proof.log`.
The final 72-case run also used a fresh database upgraded through actual migrations. Both disposable
PostgreSQL containers and their anonymous volumes were removed; no matching containers remain.

This completes the internal Server transaction increment only. Actual Helper writer quiescence,
stable source capture and transfer, public orchestration, verified rollback, Node snapshot/finalization
integration, retention, account-local commands, full CLI flows and real Native/Docker Sandbox
acceptance remain unfinished. The full-manager goal remains active. No commit, release, deployment
or runtime capability advertisement occurred.

Final Server full gate: **1015 passed, 15 skipped, 79.37% coverage**, including the final head-preserving
retry and concurrent takeover cases. Ruff formatting/lint, Mypy (**364 source files**), Chinese
docstring checks and whitespace passed. Log: `/tmp/skill-takeover-server-quality-final.log`.
The first full run exposed a stale expected-table registry; it was updated for the new table before
this final complete rerun. Alembic head is now **0039_skill_account_takeover**.

## 2026-09-22 — retained Helper account capture and Native quiescence evidence

Added a Helper-private initial capture format: exact takeover/task/account binding, immutable random
Helper receipt identity, original complete manifest and independently copied digest objects under
`takeover-<account UUID>` in SkillStateRoot. Capture excludes only reserved system roots; it preserves
binary state, malformed skill documents, original modes, empty directories and cross-entry links.
Objects are private ordinary files, not hardlinks to the source. Descriptor-relative no-follow reads,
streamed byte verification, a second complete source check and fsync/no-replace publication prevent
partial captures. Failures preserve the source. A missing discovery root records an explicit empty
capture. Retries survive source changes/removal without recapturing, and reject changed identities,
corrupt metadata and unsafe object aliases. Original paths and permissions remain unchanged.

The internal Native Helper method validates the exact Server inventory digest, permanently fences
the account, checks local import intents, then inspects historical session/binding units and locally
retained specs, systemd units and leftover cgroups. It reads specs through root-owned no-follow
handles; it does not reuse reconciliation's skip-on-error behavior. Active, populated, missing or
ambiguous proof fails closed. It never sends stop/kill. Nullable backend identities remain unknown;
unknown/Docker history, historical backend-copy tasks and same-user/unattributable Docker specs
require further reconciliation. The method is deliberately not yet wired to a Helper socket operation
or worker task: sandbox-wide/orphan-Docker inventory, backend-copy exit proof, authenticated task
transfer and verified rollback remain necessary before exposing account takeover.

Added **17 top-level tests**, with additional subcases. The final Linux fence/import/capture suite
passed **40 top-level cases**, covering the new primitives and previous admission/import regressions:
`/tmp/skill-capture-linux-final-v2.log`. A Python-derived nullable inventory hash also passes in Go.
CI's existing Linux fence/import script now selects the capture and Native inspection cases.

The actual isolated systemd suite proves a synthetic managed main process can exit successfully
while a descendant still writes the old account tree. Takeover is rejected until that entire cgroup
empties naturally, then retains the descendant's late write without modifying/removing the original.
This new case and all six prior lifecycle cases passed in the final run:
`/tmp/skill-capture-systemd-final.log`. CI includes the new case. No host filesystem/cgroup mounts
were used, and test containers/images are removed by the scripts. This is systemd/cgroup evidence,
not real Claude or Docker Sandbox acceptance.

Final Node full quality gate passed: **60.6% statement coverage**, formatting, vet, Go tests,
installer/shell/release contracts, official/managed skill consistency and whitespace:
`/tmp/skill-capture-node-quality-final.log`. Server's latest verified baseline remains **1015 passed,
15 skipped, 79.37%**, schema head **0039_skill_account_takeover**; no Server code changed here.
No commit, release, deployment, public takeover route or runtime capability advertisement occurred.
The full-manager goal remains active; runtime transfer, complete backend proof, public orchestration,
rollback, retention, account-local commands, full CLI workflows and final acceptance remain required.

## 2026-09-22 — exact-task takeover HTTP and streaming Node client

Added Node-authenticated takeover status/capture/file/complete routes and a typed, content-free
receipt view. Every request binds the original Node/takeover/task; capture authorization happens
before bounded body reading and again before acceptance. Status exposes the immutable inventory
while old writers drain so the Helper can close its fence first. Capture/complete still require drain.
Inventory is bounded to 10,000 records; capture transport is bounded to 64 MiB. File streams verify
manifest membership, exact size, digest and classification before fresh authorization and storage.
Missing complete bytes return stable `CONTENT_INCOMPLETE` without changing directory authority.
Committed responses retain the original checkpoint, including terminal-task replay, while continuing
to check owner and exact task binding. Task polling now returns additive `task_record_id`, preserving
the existing logical `task_id` for StartTask/results/ledger replay. The exact UUID can therefore be
obtained from the authenticated envelope instead of guessed from a logical name or payload. No response grants permission to delete original sources.

The Go client validates every reservation field, canonical inventory hash, versions and phase
invariants; completion also compares the retained Helper receipt, capture digest and current upload.
Files use raw readers with streamed SHA-256, exact length, UTF-8/binary classification and verified
EOF. An early successful response cannot acknowledge an unread file. Readers close exactly once;
redirects and oversized/malformed/duplicate-key responses reject. Skill response bodies allow 4 MiB
for the bounded inventory, without widening unrelated API limits. Requests honor cancellation and a
10-minute outer timeout, do not replay uncertain writes automatically, and retain only bounded error
codes rather than private Server messages. A shared portable content verifier preserves the existing
Linux copy classifier.

Direct evidence: **31 takeover HTTP cases** passed with real Node token authentication and fresh request
transactions, including all four routes' cross-Node/task/lease/owner/payload rejection, original
commit replay, malformed declarations, bounded bodies, corrupt/short/long files and lease expiry
*during* streaming before bytes enter the content volume. Log:
`/tmp/skill-takeover-http-tests-final.log`. Added **13 Go top-level tests** with subcases;
API and skillmanager packages pass the race detector:
`/tmp/skill-takeover-node-race-final.log`. A dedicated 10,000-writer response exceeds the ordinary
1 MiB budget and passes only the bounded skill-specific path.

A real loopback HTTP test used the actual Go client against Python routes and real token validation.
It uploaded a mixed directory including a 1.4 MB binary state object, replayed each file, committed
and replayed completion with the exact original checkpoint. Log:
`/tmp/skill-takeover-cross-language.log`. Temporary harness files and the listening server were removed.
The final Linux copy suite passed **61 top-level cases**, including private account capture and
existing Native cleanup guards: `/tmp/skill-takeover-transfer-linux.log`. These are transport and
synthetic lifecycle proofs, not real Claude or Docker Sandbox acceptance.

Helper descriptor transfer and worker orchestration remain pending. Existing worker execution
caches any execution error as a terminal failure, so transient writer-drain/transfer states require
an explicit durable retry path before task dispatch can be connected. Complete mixed-backend writer
proof and task-lease maintenance are also required: StartTask currently does not extend the lease,
and an HTTP timeout is not a task authorization renewal. Verified rollback, snapshot/finalization
task integration, retention, account-local commands,
full CLI workflows and final acceptance remain unfinished. No user-facing reservation, automatic
new task dispatch, runtime capability advertisement, commit, release or deployment was enabled.

Final full gates after the additive poll-envelope change: Server **1046 passed, 15 skipped,
79.39% coverage**, Ruff format/lint, Mypy (**366 source files**), docstrings and whitespace passed:
`/tmp/skill-takeover-transfer-server-quality-final.log`. Node full gate passed with **61.2% statement
coverage**, formatting, vet, all Go tests, installer/shell/release checks, managed/official Skill
consistency and whitespace: `/tmp/skill-takeover-transfer-node-quality-final.log`. The focused Server
run includes **31 takeover HTTP + 9 existing Node API cases (40 passed)**. PostgreSQL migration and
service evidence remains the earlier verified 72-case run; this increment changes no database schema.
The full-manager goal remains active and incomplete.


## 2026-09-22 — retained capture descriptors and the non-root upload boundary

Added `open_account_capture_file`, a read-only Helper operation for existing sealed account captures,
and typed `ReadAccountCapture` / `OpenAccountCaptureObject` clients. Requests select only the exact
binding and manifest or digest object; object requests additionally match Helper receipt and complete
tree digest. The Helper checks peer UID, private root, fence, capture, manifest membership and ordinary
root-owned single-link file permissions. `OpenExistingStateStore` retains all protected-root checks
without creating absent directories. No arbitrary path, directory descriptor, capture initiation,
fence release, cleanup or task dispatch was added.

SCM_RIGHTS handoff carries one read-only file, with small metadata and a bounded acknowledgement.
The client uses atomic CLOEXEC receive, validates file access/type/owner/mode/length, and closes
unadopted descriptors on every failed or cancelled read. It supports fragmented stream frames and
rejects malformed/truncated/multiple descriptors without leaking them. Metadata has a dedicated
32 KiB ceiling for worst-case JSON escaping of a valid 4096-byte path; complete manifests stay within
64 MiB and travel through the descriptor. Typed decoding preserves epochs above 2^53 without using
floating-point intermediates. Manifest bytes are checked against the retained tree digest before
return; object byte verification remains mandatory in the HTTP transfer client.

Added **12 top-level Linux tests** with subcases. A real admitted non-root subprocess cannot open the
private store or write its file, but can read/verify the handed-off descriptor; another UID is denied.
Protocol tests cover FD_CLOEXEC, source removal and retry, changed task/Node/user/account/epoch/backend/
inventory/receipt/tree/object identities, forged paths, unsafe metadata/object links and permissions,
missing-store noncreation, partial frames, cancellation and descriptor cleanup, a >1 MiB manifest,
escaped paths and full-width epoch matching. The combined Helper-to-HTTP-client test uploads the
original object, then modifies the private object without changing its size and proves the streamed
hash check refuses a false remote acknowledgement. This does not use a real Claude process or Docker
Sandbox, and does not establish mixed-backend takeover proof.

The full-manager goal remains active. The worker must still obtain fresh Server authorization before
these local reads, maintain task leases and preserve recoverable waiting states rather than caching
all execution errors as permanent failure. Capture initiation, complete Docker/orphan/backend-copy
quiescence, verified rollback, managed snapshot/finalization orchestration, retention, account-local
commands, full CLI flows and final backend acceptance remain unfinished. No capability advertisement,
public reservation, automatic takeover dispatch, commit, release or deployment occurred.


Final evidence: the updated Linux fence/import/transfer script passed **52 top-level cases**:
`/tmp/skill-capture-fd-linux-final.log`. All **12 descriptor cases** passed with Go 1.26.6's Linux
race detector in a disposable container, including actual admitted/denied non-root subprocesses:
`/tmp/skill-capture-fd-linux-race-final.log`. The existing Linux copy/retention suite passed **61
top-level cases** after the protected-store opener refactor:
`/tmp/skill-capture-fd-linux-copy.log`. CI's existing Linux import script now selects the descriptor
cases. Temporary compilation files were removed; no descriptor-test container remains.

Final Node full quality gate passed with **59.9% host statement coverage**, formatting, vet, Go tests,
installer/shell/release checks, managed/official Skill consistency and whitespace:
`/tmp/skill-capture-fd-node-quality-final.log`. The Linux-only positive descriptor paths are verified
separately above and are not counted as covered by the macOS host run. Server/CLI code was unchanged;
the last Server full gate remains **1046 passed, 15 skipped, 79.39% coverage**, migration head **0039**.
The full design remains incomplete and the goal remains active.


## 2026-09-22 — takeover lease maintenance and retained transfer coordination

Added exact-task takeover lease renewal with a strict positive `lease_attempt` from the authenticated
poll envelope. The attempt is the task retry counter; stale attempts, expired/pending/terminal tasks,
revoked owners and committed takeovers cannot renew. A renewal extends only the existing task deadline
by the configured positive duration, capped at 300 seconds, and returns Server timestamps plus the
renewal interval. It creates no task, upload or authority checkpoint.

Capture and file routes now commit preliminary authorization before streaming the request body, then
reauthorize before accepting the declaration or storing verified bytes. This prevents their user/task
locks from blocking lease renewal while still rejecting owner revocation during the stream. Polling
uses `FOR UPDATE SKIP LOCKED` so a concurrent poll cannot overwrite a renewal's deadline or claim the
same pending task before the first claimant updates its status.

Node validates typed lease responses and derives a monotonic local budget from request start plus
Server lease duration. Round-trip latency reduces this budget; host wall-clock skew cannot extend it.
Renewal requests cannot outlive the previous budget. An uncertain renewal cancels dependent work with
bounded `TAKEOVER_LEASE_LOST`; all loop exits join the renewal goroutine. This error must remain
recoverable when task dispatch is implemented.

The internal retained-transfer coordinator refreshes authorization before Helper access, returns an
already committed Server receipt directly, otherwise renews before reading the original sealed capture.
It begins the exact capture upload, streams each distinct file digest once through Helper descriptors,
and completes the current upload. Descriptor metadata must match the manifest; the existing API client
owns closure and verifies actual bytes. A verified committed receipt remains authoritative if renewal
simultaneously rejects the completed task. Failure/cancellation never deletes the original or retained
capture. This entry point consumes an existing capture only; it neither initiates capture nor changes
worker task dispatch.

Focused SQLite verification passed **58 cases, 2 PostgreSQL-only skipped**. PostgreSQL verification
passed **51 cases**, including live upload/renewal/revocation concurrency, independent renewal
transactions, poll-versus-renewal row locking and concurrent pending-task selection:
`/tmp/skill-takeover-lease-postgres.log`. The disposable database used metadata fixtures; no migration
changed in this increment. Node API/worker race tests passed:
`/tmp/skill-takeover-transfer-node-race.log`. Coordinator cases include duplicate file digests, early
committed replay, fresh authorization ordering, failures at each transfer stage, descriptor closure,
retained content after failure, lease-loss cancellation, and commit/renewal races at begin and complete.

Full Node gate passed with **60.3% host statement coverage**:
`/tmp/skill-takeover-lease-node-quality.log`. The host run does not claim Linux-only Helper positive
paths or actual runtime acceptance; prior dedicated Linux descriptor/systemd evidence remains separate.

Complete Docker Sandbox/orphan/backend-copy writer proof, capture initiation, durable waiting/retry
execution, verified acknowledgement/rollback, managed snapshot/finalization orchestration, retention,
account-local commands, full CLI workflows and real backend acceptance remain unfinished. No automatic
takeover dispatch, public reservation, capability advertisement, commit, release or deployment occurred.
The complete skill-manager goal remains active and incomplete.

Final full Server gate passed: **1064 passed, 17 skipped, 79.39% coverage**, Ruff format/lint,
Mypy (**367 source files**), docstrings and whitespace:
`/tmp/skill-takeover-lease-server-quality.log`. Subsequent poll-contract assertions passed all **9
Node API tests** and static/docstring checks: `/tmp/skill-takeover-poll-envelope.log`. They verify
that reissued tasks preserve the exact database UUID while incrementing `lease_attempt` from 1 to 2.
The disposable PostgreSQL container was stopped and removed. No schema migration was added.


## 2026-09-22 — typed CLI library queries and original-operation waiting

Added user-authenticated `skill list`, `skill info NAME_OR_UUID`, and `skill status OPERATION_UUID`
with `--wait` / `--timeout` and global `--json`. Tool/account filters are mutually exclusive;
account listing requires `--effective`, IDs are full UUIDs and names cannot inject path components.
All network calls remain in `api::skills`, using the existing redirect-refusing client and 1 MiB
bounded body reader. Typed library/revision/source/override/effective/target structures preserve the
version-1 envelope and int64 values without floating-point conversion. Metadata/tracking/details
remain the Server's explicitly flexible object fields. Wrong schema or original-operation identity,
missing data and malformed responses reject without printing raw response bodies.

The commands use the existing user credential refresh lifecycle; device credentials cannot substitute.
Terminal list/info show revision identities, retained versions, scoped overrides and independent field
origins; status shows configuration commitment separately from each target's readiness and replacement.
Server-controlled terminal text escapes control characters. JSON emits one complete envelope to stdout;
explanations use stderr. Authentication/transport/decoding failures use bounded local messages.

Waiting uses a monotonic deadline, only queries the original operation, stops on known failure/conflict/
supersession and never follows a replacement as if it were the original success. Pending inspection
without `--wait` is a successful query. Waiting timeout returns 3 with the last known pending receipt;
known failures return 1, argument errors 2, success 0 and interrupted waiting 130. Transient read failures
retry within the original deadline. Later authorization/decoding failures retain the already observed
operation ID, configuration commitment and data instead of incorrectly resetting `committed=false`.
These read-only commands never resubmit, cancel or modify remote operations.

Added **14 real CLI subprocess/HTTP contract tests**, covering exact authentication/scope, lossless
large integer output, provenance/override presentation, pending -> stored waiting, timeout, partial
failure, supersession, error envelopes, wrong identities/versions, missing user login, invalid arguments,
terminal control characters, transient disconnection, authorization loss and malformed refreshes.
Log: `/tmp/skill-cli-query-contract-final.log`.

A separate actual Rust CLI -> Python Server loopback check passed **5 cases**. It bootstrapped a real
user token, uploaded and installed a real package through HTTP, then compared CLI list, tool-scoped list,
info, committed status/wait and missing-installation error JSON with the live Server's responses.
Log: `/tmp/skill-cli-loopback.log`. The temporary application/database/credential directory was removed
and the server thread/socket stopped. This validates real wire compatibility, not runtime deployment.

Runtime migration inspection confirmed its historical `cp` execution has no independent durable writer
exit record. Historical migration tasks therefore still deny takeover rather than treating Server task
termination as proof. No writer-proof bypass or backend capability advertisement was introduced.

The CLI view is currently the Server's library/rule view. Session-pinned snapshots, system/account-local
entries, runtime checkpoints/conflict/sync details and complete effective discovery are still missing.
Git/private-auth acquisition, installation/mutation/state commands, durable mutation idempotency and retry
remain required. Node mixed-backend proof, capture/retry dispatch, snapshot/finalization orchestration,
rollback/retention and actual Claude/Docker Sandbox acceptance remain unfinished. The full-manager goal
remains active; these query commands are not a complete skill-manager delivery.

Final CLI full gate passed **321 Rust tests**, rustfmt, Clippy with warnings denied, shell syntax,
Ruby release-workflow contracts, managed-tool cache tests and whitespace:
`/tmp/skill-cli-query-quality-verified.log`. The first run identified missing new argument help;
all new arguments now have help and the complete command-tree help contract passes. Node/Server
runtime code was unchanged this increment; their latest verified gates remain recorded above.


## 2026-09-22 — CLI rule changes, rollback and durable acceptance recovery

Added `skill enable`, `disable`, `pin`, `unpin`, `inherit`, `remove` and `rollback`. Rules support
explicit tool/account scopes, repeated unique tools, inherited fields and `disable --all-scopes`.
Pin/unpin/inherit require scope; rollback/remove cannot accidentally accept account scope. Revision
references are full UUIDs or `rN`. Noninteractive mutations require `--yes` (exit 2 otherwise), while
`--dry-run` performs remote reads only and writes no mutation record. Scoped preflight reads validate
the selected Server tool/account before confirmation. Default waiting is 60 seconds, with `--timeout`
and `--no-wait`; known target failure still returns nonzero while preserving `committed=true`.

Mutation payloads have explicit tagged Rust types and use the dedicated rules/removals/rollbacks
endpoints. Plans resolve the current library name to a stable skill UUID and freeze the library
generation. Reply validation requires the original skill and exact changed/no-op generation step;
protocol or identity mismatch cannot be saved as successful acceptance.

SQLite schema version 4 adds a backward-compatible `skill_commands` table. Before POST, it persists
Server identity, authenticated `/users/me` UUID, intent digest, random idempotency key and canonical
request JSON. It contains no credentials or source bytes. Server URLs are normalized and reject
embedded credentials/query/fragment before they enter the journal. A unique pending-intent index
lets independent processes share the original request instead of overwriting uncertain input.
Received operation IDs remain bound to the exact request, even when deployment is pending or failed.

Recovery first queries the original key. If acceptance exists it returns that receipt without
another mutation; only `OPERATION_NOT_FOUND` allows identical input to be resubmitted. Neither
restart nor transport recovery refreshes generation or silently replans. Known generation conflict
is terminal for that attempt. Authentication failures never trigger automatic retries. An uncertain
result retains the request, explicitly reports `status=unknown` and `details.commit_state=unknown`,
and only transient transport/server failures are marked retryable. `committed=false` in that case
means no confirmation was received, not evidence that the Server rolled back.

`skill status --last` queries the latest locally recorded command for this exact Server/user. It
uses the saved operation ID or original key and never submits a mutation, allowing recovery after
successful output was lost. A new explicit rollback after a received operation remains a new command;
`--last` is the way to inspect the prior result. Existing original-ID status/wait behavior is preserved.

Added **9 top-level real CLI HTTP contract tests** with command/flag subcases, plus **2 SQLite tests**
(including independent-connection concurrency). They cover all seven mutation commands, stable-ID
resolution, scopes, dry-run nonmutation, confirmation and invalid arguments, saved original operation
identity, lost replies, restart without generation refresh, pending/default wait versus no-wait,
partial unsupported targets, generation conflict, authentication denial and `--last` recovery.
The prior **14 query tests** continue to pass. Logs:
`/tmp/skill-cli-mutation-contract-final2.log` and `/tmp/skill-cli-mutation-journal.log`.

An actual Rust CLI -> Python Server loopback passed **11 cases** using a real authenticated user,
two HTTP-uploaded package revisions and real activation history. It verified dry-run, no-op generation,
eight rule/rollback mutations, logical removal and latest-receipt lookup, comparing accepted receipts
against the live Server. Log: `/tmp/skill-cli-mutation-loopback.log`. The temporary application,
SQLite/content volume, credentials and server thread/socket were removed; no deployment occurred.

Account-local commands and library/local-name ambiguity handling remain unfinished; current commands
operate on the user library. Complete effective discovery, Git/private-auth acquisition, add/update,
state/export workflows and ended-operation retry still remain. Node mixed-backend writer proof,
capture/retry dispatch, snapshot/finalization integration, verified rollback/retention and actual Claude/
Docker Sandbox acceptance remain required. No goal completion, release or capability enablement is claimed.

Final CLI verification passed **334 Rust tests**, rustfmt, Clippy with warnings denied, shell parsing,
Ruby release-workflow contracts, managed-tool cache tests and whitespace:
`/tmp/skill-cli-mutation-quality-final-state.log`. This includes the final authentication-versus-transient
`retryable` assertions and journal work on blocking threads without connections spanning HTTP awaits.
The temporary loopback harness file was removed. Server/Node implementation was unchanged in this CLI
increment; their earlier full gates and runtime limitations remain applicable. The goal remains active.

### Account-local configuration and name ambiguity increment

This increment supersedes the earlier account-local query/rule limitation. The existing authenticated
list endpoint now includes a separate `local_items` collection only for an explicit owned account,
including disabled active sources. Local detail carries its account, source checkpoint and retained
state revisions, without Git provenance. Stable IDs can query removed local history; staged candidates
remain outside public configuration. Reads do not require or create a user-library row.

Server name resolution checks library and local sources together. Ambiguous names return
`SKILL_SOURCE_CONFLICT`; exact IDs choose the source. Local query/enable/disable/inherit requires the
owning account. Inherit(enabled/all) restores enabled=true, independent of user/tool rules; local
pin/unpin/revision inheritance is rejected. Library-only update/remove/rollback cannot mutate a local
identity. Rules reuse the existing user lock, generation CAS, savepoint, operation ledger and original
receipt replay. Only a real flag change advances configuration generation. Targets contain only the
owning account; state/directory heads and epochs, content references and existing snapshots remain
unchanged. No migration or runtime readiness claim was introduced.

The CLI asks Server to resolve the original input before saving a stable ID, preserving ambiguity
checks even if the library listing has a name match. It renders typed local list/detail results and
rejects unsupported local commands before confirmation or journaling. A detail response with a
mismatched name/ID fails before mutation. Missing required account scope exits 2 for both queries and
mutations. Existing pending journals still replay their exact original IDs/requests without replanning.
Both CLI READMEs, architecture notes and the version-1 wire document describe the new behavior.

Added **7 Server cases** for scope/owner isolation, disabled visibility, reads without a library row,
unsupported revision rules, generation/no-op behavior, original replay, snapshot/head preservation,
name ambiguity and actual authenticated HTTP. The existing takeover collision test now verifies that
a short name is rejected and its stable library ID remains queryable. Consolidated Server info into
one union-returning query; there is no second library-only query implementation.

Added **6 CLI contract tests** with subcases for local queries, terminal escaping, all supported rules,
unsupported commands without journal/POST, missing scope, mismatched detail identity and ambiguity
that must not be bypassed by a library name match. All prior query/mutation recovery tests still pass.
The final CLI full gate passed **340 Rust tests**, rustfmt, Clippy with warnings denied, shell/release
contracts, managed-tool cache tests and whitespace:
`/tmp/skill-local-cli-quality-final-scope.log`.

The final real Rust CLI -> authenticated Python Server loopback passed **13 cases**, using complete
uploaded directory bytes and seeded active local identities. It checked disabled listing, detail,
dry-run, disable/inherit generation changes, original `--last`, illegal pin, missing scope exits,
name collision and exact-ID mutation. This proves the HTTP/CLI contract, not live runtime capture or
Claude execution. Log: `/tmp/skill-local-cli-loopback-final-scope.log`. Its temporary SQLite/content/
credential directories, HTTP listener/task and harness file were removed.

The final Server full gate passed **1071 tests**, with **17 skipped**, **79.46% coverage**, Mypy over
**370 files**, Ruff formatting/lint, Chinese docstring checks and whitespace:
`/tmp/skill-local-server-quality-final.log`. An earlier full run found one outdated takeover-test
expectation; the corrected related suite passed **34 cases** before the final full run. All test
processes and temporary loopback resources are terminal/removed. Node code was unchanged in this
increment; its previously recorded verification and runtime limitations still apply.

The overall goal remains active. Complete account diagnostics and system/session effective views,
Git/private-auth acquisition, add/update/check/upload orchestration, state/history/conflict/export/
reset/restore/prune CLI, ended-operation retry, mixed-backend writer proof, capture/transfer dispatch,
snapshot materialization and finalization integration, retention/rollback evidence and real Native
Claude/Docker Sandbox acceptance remain required. This increment does not enable takeover dispatch,
capability advertisement, release or deployment.


### Local-source CLI installation increment

`skill add LOCAL_DIRECTORY` now connects the existing source discovery/capture implementation to
real content upload and atomic library installation. It supports no-login `--list`, automatic single
selection, explicit/interactive multiple selection, `--all`, repeated `--skill`, `--path`, tool/account
scope, dry-run, confirmation and common operation waiting. `--yes` does not choose a source. All
selected packages are complete private snapshots before preview or upload. Source changes afterward
cannot alter transmitted bytes; explicit subpath descent cannot escape through directory links.
Direct-directory and equivalent subpath selection produce the same opaque local source identity.

Typed content APIs verify full returned manifests, upload/tree/file IDs, digests and persistence flags.
Content envelopes have a bounded 64 MiB ceiling while metadata queries retain 1 MiB. File reads and
hashing run off the async runtime. Transient transfer recovery reuses the original upload key/ID,
queries its exact status and reads only captured digest objects. Expired plans fail explicitly;
files/trees are not mislabeled as installed configuration. All trees complete before one multi-item
installation POST. A conflicting candidate cannot cause partial installation.

Extracted the existing configuration acceptance/wait/recovery flow into a shared module, preserving
all rule/remove/rollback behavior. Installation requests enter the existing Server/user-bound SQLite
journal before POST; schema remains version 4, with a 4 MiB metadata request bound for up to 100 items.
An uncertain accepted command resumes from its original key/items/generation before any source read,
including after the source disappears. It never refreshes generation or silently rebuilds a different
package. Process interruption before configuration submission can leave lease-bound content staging;
it does not promise durable local package recovery or partial installation. Both READMEs and wire/
architecture/state docs describe these boundaries.

Verification: **11 CLI installation contract tests**, **2 content HTTP tests**, and **2 new discovery
cases** cover selection/scopes, dry-run nonmutation, upload ordering, live-source changes, lost upload
creation/file responses, exact restart recovery, malformed receipts, expiry, source identity, subpath
isolation and complete manifests above the normal metadata response cap. The final full CLI gate
passed **355 Rust tests**, formatting, Clippy with warnings denied, shell/Ruby release contracts,
managed-tool cache tests and whitespace. Log: `/tmp/skill-add-cli-quality.log`.
Focused logs: `/tmp/skill-install-contract.log`, `/tmp/skill-install-contract-more.log` and
`/tmp/skill-install-discovery.log` (the last lost-begin-response case is in the final full gate).

A real Rust CLI -> authenticated Python Server loopback passed **18 cases**. It checked binary bytes,
internal links and empty directories against content downloaded back from the Server, whole-selection
atomic rollback on a conflicting second source, no-op repeats, equivalent source selection, tool/
account initial rules, update-required rejection, original `--last`, and injected lost file/installation
responses after actual Server persistence. Log: `/tmp/skill-add-cli-loopback.log`. The temporary HTTP
listener/task, SQLite/content/credential directories and harness file were removed. Server and Node
code were unchanged in this increment, so their previous gates and runtime limitations still apply.

The goal remains active. Git/private-auth acquisition, update/check, state/history/conflict/export/
reset/restore/prune CLI, full system/session/account diagnostics, ended-operation retry, mixed-backend
writer proof, safe takeover/capture dispatch, managed snapshot/finalization wiring, retention/rollback
verification and real Claude/Docker Sandbox acceptance remain unfinished. No release, deployment,
automatic takeover dispatch or runtime capability advertisement was enabled.


### Git-source acquisition and CLI installation increment

`skill add` now accepts GitHub owner/repo and credential-free HTTPS Git URLs, with literal `--ref`
and repository-relative `--path`. Default acquisition records the actual remote default branch;
branch/tag ambiguity requires an explicit namespace, annotated tags peel to a full commit, and only
commit objects are packaged. Native Git credential helpers run noninteractively in a private cwd;
username/password Basic credentials enter only URL-scoped child environment configuration. Transport
uses isolated Git configuration, HTTPS-only protocols, no redirects, TLS verification, no inherited
trace/execution configuration and no credential storage operation. Private CA files remain supported.

A private bare repository supplies raw tree/blob objects. No checkout, source hooks, filters, archive
export attributes or install scripts run. Git discovery uses the same candidate-selection rules as
local sources; internal instruction links work, invalid root metadata stops nested discovery, and
absolute instruction links are invalid candidates. Packaging preserves execute modes, binary bytes,
internal links and all selected assets independently of host filesystem representation. Selected
unfetched gitlinks and LFS pointers fail before uploads; unselected submodules do not prevent an
explicit subpath installation. Explicit --path enumerates only that Git subtree, so unrelated
nonportable filenames and metadata limits do not invalidate it. Content hashes and durable package
writes run on blocking workers.

The existing atomic content-upload/installation pipeline consumes these complete packages with exact
repository URL, subpath and branch/tag/commit provenance. Git journal intent is independent of cwd;
optional refs preserve old local intent serialization. Pending legacy local owner/repo records are
checked before the new GitHub shorthand interpretation. Recovery uses the original completed content
and full commit even after the repository disappears, without fetching or loading Git credentials.
Both CLI READMEs, command help, architecture notes and wire documentation describe the new behavior.

All Git subprocess stdout/stderr and raw-object batches are bounded. Credentials, ref discovery,
fetch and object reads have individual deadlines, plus a 240-second acquisition/discovery deadline
and a separate 240-second bound for each selected capture. Unix groups and Windows kill-on-close jobs
contain subprocess descendants; Ctrl-C during acquisition reports one envelope and exit 130. Fetch
staging is sampled every 100 ms against 512 MiB/100000 entries and checked again on completion. This
can overshoot between samples and is explicitly **not a hard network-byte quota**.

Ten isolated HTTPS Git/CLI contract tests cover private helper authentication, exact manifests and
provenance, branch/tag/full-commit refs, ref ambiguity, listing without Server login, redirect refusal,
TLS enforcement, inherited config isolation, submodule/LFS rejection, instruction links, invalid
metadata, original installation recovery, legacy local journal compatibility and Ctrl-C. Fixture TLS
keys and synthetic credentials are temporary; no real developer Git credentials are accessed.
Unit cases additionally cover source/ref/tree/blob parsing, process output limits, sparse-file disk
limits, timeout and future cancellation with descendant termination. The final full CLI gate passed **375 Rust tests**, formatting, Clippy with warnings denied,
shell/Ruby release contracts, managed-tool cache tests and whitespace. Logs:
`/tmp/skill-git-cli-quality-final.log`, `/tmp/skill-git-contract-final.log`,
`/tmp/skill-git-unit-final.log` and `/tmp/skill-git-legacy-contract.log`.

The Windows-specific process module compiled for x86_64-pc-windows-msvc using the repository's Tokio
version. A whole-library Windows cross-check could not compile bundled SQLite because this macOS host
lacks Windows SDK C headers; Windows runtime process containment is not yet tested. Logs:
`/tmp/skill-git-windows-module.log` and `/tmp/skill-git-windows-check.log`. The isolated compile project
was removed. Server/Node implementation did not change in this increment; their earlier gates and
runtime limitations still apply.

The overall goal remains active. Update/check, state/history/conflict/export/reset/restore/prune CLI,
full system/session/account diagnostics, ended-operation retry, mixed-backend writer proof, safe
capture/takeover dispatch, managed snapshot/finalization wiring, retention/rollback verification,
real Native Claude/Docker Sandbox acceptance and final requirement-by-requirement audit remain.
No commits, releases, deployments, automatic takeover dispatch or capability advertisement were made.


### Check/update, candidate activation and independent batch CLI increment

Implemented `skill check [SKILL]`, single `skill update` with --ref/--from/--stage and common mutation
options, plus `update --all`. Checks capture complete branch packages without content/configuration
writes or journal entries and report up_to_date/update_available/pinned/local_source/errors. Fixed
and local sources are skipped automatically. Recorded branch selection is stable even if remote HEAD
changes or a same-named tag appears. Git root/name drift reports expected/actual layout; local --from
supports a new device's directory while preserving the original opaque installation source identity.

Typed updates consume the existing Server /skills/updates contract. Candidate staging leaves the
default, upstream policy and account state unchanged. Retained matching content is reused without
another upload, including staged candidate activation. New content completes before one configuration
POST. Default-enabled fields and independent tool/account pins are preserved by the existing Server
transaction. Known moved tags fail locally and the Server separately checks its observation history.

Refactored shared acceptance to return its observed result independently of rendering, allowing one
JSON batch envelope while preserving existing add/rule/remove/rollback behavior. Single update stores
exact skill/item/generation/key/stage/tracking-switch metadata before POST. Pending lookup occurs
before fresh source/configuration reads; changed/missing sources cannot replace uncertain requests.
Batch updates recover pending automatic Git requests before current listing/source acquisition,
including removed/pinned items, then process fresh eligible items independently. Per-item fresh
generation reads are not permission to rebase a submitted request. Failures do not erase successful
receipts; every row retains its own operation/commitment/status. No global batch transaction or ID is
claimed. Journal enumeration is Server/user scoped and bounded; SQLite schema remains unchanged.

Added cancellation around update preparation, upload and interactive confirmation. Shared submission
also handles Ctrl-C with an unknown-acceptance envelope and original key, retaining the journal and
returning 130. This does not imply rollback; post-acceptance waiting retains known commitment. Full
batch output retains prior results on later interruption. Both READMEs, CLI help, architecture/state
notes and wire contracts describe selection, recovery, per-item waiting and aggregate commitment.

Thirteen CLI update/check contract tests cover source comparison, fixed/local skips, stage/content
reuse, local identity, dry-run nonmutation, layout/tag drift, source disappearance, missing-item batch
recovery, multi-item partial success and per-item generations, invalid arguments, forged receipts,
recorded-branch stability and submission interruption. Existing storage isolation tests additionally
exercise pending enumeration owner/origin/received filtering. Earlier focused add/rule/update tests
all passed after acceptance extraction. The final full CLI gate passed **388 Rust tests**, formatting, Clippy with warnings denied,
shell/Ruby release contracts, managed-tool cache tests and whitespace. Logs:
`/tmp/skill-update-cli-quality-final.log`, `/tmp/skill-update-contract-expanded.log` and
`/tmp/skill-update-contract-final.log` (the last recorded-branch case is included in the final full gate).

A real Rust CLI -> authenticated Python Server loopback passed **24 cases** for local and private
HTTPS Git updates: read-only checks, staged revisions, activation without uploading retained content,
independent tool pins and disabled defaults, real binary content download fidelity, same-content
no-op revision/generation behavior, rollback and explicit branch resumption, moved-tag rejection,
source-layout failure, batch skips/activation, and a dropped response after actual Server update
commit. It verified exactly one update POST and one new revision for that lost-response case.
Log: `/tmp/skill-update-cli-loopback.log`. Its temporary app/database/content/credential directories,
HTTP/TLS listeners and harness file were removed. No Server/Node implementation changed in this increment,
and no runtime deployment/model-loading evidence is inferred from the loopback.

The goal remains active. State/history/conflict/export/reset/restore/prune CLI, full system/session/
account diagnostics, ended-operation retry, mixed-backend writer proof, safe takeover/capture
initiation and dispatch, managed snapshot/finalization wiring, retention/rollback lifecycle evidence,
real Native Claude/Docker Sandbox acceptance and final requirement-by-requirement audit remain.
Existing Git-add/rule synchronous confirmation and upload cancellation outside their documented
acquisition/submission/wait phases still need a final interruption audit. No commit, release,
deployment, automatic takeover dispatch or capability advertisement was performed.


### Account state history, immutable diff pagination and portable export CLI increment

Implemented `skill state list/info/diff/export` against the existing authenticated Server APIs.
Item and account-directory selectors are mutually exclusive; account identity is explicit except
item export may infer it from the requested checkpoint. List returns independent checkpoint and
pending-finalization pages with separate cursors, retaining every revision/epoch, current-head flags,
source finalization outcome and persistence location. Pending Node-only records never become fake
restorable checkpoints. Info includes all historical/current epochs and references, with optional
paged directory members; expired metadata succeeds with state_expired while export fails.

Diff preserves the Server's original package/local-initial/directory baseline and metadata-only path
changes. The first current-head response identifies an immutable checkpoint; subsequent --cursor
requires --checkpoint and forbids moving account/skill selectors. Typed responses validate exact IDs,
account/scope, page size, next cursors, sorted paths, manifest entry invariants and read-only envelopes.
Queries initialize no branches and write no mutation journal. Structured errors preserve Server
rejections, and terminal rendering escapes untrusted metadata.

Exports resolve the selected checkpoint's exact account/source/scope and verify the complete returned
manifest digest before obtaining any bytes. Cross-item dependency roots require a backing directory
checkpoint export, even though the underlying Server endpoint can return a connected dependency unit.
The portable agent-remote-skill-checkpoint-v1 directory contains checkpoint.json, manifest.json and
objects/<sha256>; original paths, modes, empty directories and ordinary/runtime links remain lossless
manifest metadata. No source-controlled paths or links are instantiated locally. This deliberate
portable bundle is not a prepared runtime tree or a direct resolve --directory input.

Content downloads stream with constant-memory SHA-256 and whole-file UTF-8/NUL classification,
validate exact length/ETag, and deduplicate equal object digests without quadratic membership scans.
Manifest envelopes have a 64 MiB ceiling; other metadata keeps its 1 MiB bound. Local expanded export
size is capped at 10 GiB. File requests have a one-hour deadline plus 30-second header/error-body/
stream-idle deadlines. Files and metadata are fsynced within private sibling staging; publication is
one directory rename after all files succeed. The destination must be absent or empty and is checked
again immediately before publication. Existing data, symlinks and concurrent destination writes are
not overwritten. Failed/truncated/corrupt/expired/missing content leaves no published partial bundle.
A verified locally_removed checkpoint can intentionally export an empty manifest with deletion
metadata. Ctrl-C before publication discards staging and exits 130; publication itself is observed to
completion. Successful export leaves remote committed=false and reports its local output identity.

Fifteen CLI contract tests cover selector validation, lossless historical integers, independent pages,
forged scope/identity/cursors, expired info, immutable diffs, binary fidelity, link metadata, object
deduplication, wrong accounts/sources, cross-item dependencies, incomplete/corrupt/misclassified files,
nonempty/symlink destinations, a concurrent destination writer, explicit deletion and interruption.
A focused streaming-classifier unit case covers UTF-8 split at every boundary, invalid UTF-8, NUL and
incomplete code points. The final full CLI gate passed **405 Rust tests**, formatting, Clippy with
warnings denied, shell/Ruby release contracts, managed-tool cache tests and whitespace checks.
Log: `/tmp/skill-state-cli-quality-final.log`. Earlier focused contracts:
`/tmp/skill-state-cli-contract.log` (14 cases before the final interruption case).

Actual Rust CLI -> authenticated Python Server loopback passed **18 command cases**, including real
publication/history paging, original baselines, immutable directory membership, binary/link export,
account mismatch, directory roots and cross-item dependencies, account-local identities, Node-only
pending records and retained expired metadata. Final log: `/tmp/skill-state-cli-loopback-final.log`.
Its temporary database/content/credential directories, loopback listener and harness were removed.
No Server or Node implementation changed; no real Claude/Docker runtime readiness is inferred.
Both READMEs and architecture/wire notes now document the query and portable bundle contracts.

The goal remains active. Conflict listing/diff/resolution, state reset/restore/migrate/prune CLI,
Node-only pending export access, complete system/session/account diagnostics, ended-operation retry,
older add/rule interruption audit, mixed-backend writer proof, safe capture/takeover dispatch,
managed snapshot/finalization wiring, retention/rollback lifecycle evidence, real Native Claude/
Docker Sandbox acceptance and final requirement-by-requirement audit remain. No commit, release,
deployment, automatic takeover dispatch or capability advertisement was performed.


### State reset/restore CLI, exact publication recovery and generic status increment

Implemented item and account-directory `skill state reset/restore` with common dry-run, confirmation
and waiting flags. Planning uses /state/current and the Server's complete nonpersisting preview.
Item names resolve once and the actual selector carries the stable source UUID. The exact generation,
source/base revision, installation/state/directory epochs, heads, effective target set and result tree
are fixed before confirmation. Preview/terminal results distinguish directory changes from each
branch's own prior content, including unavailable expired baselines. No state or content is written
by a dry run; its JSON explicitly contains request, preview and recovering_original_request.

Actual requests use the existing owner/origin-bound journal schema and 4 MiB record bound. A distinct
canonical state wrapper retains the exact request and confirmed result-tree digest, without file
bytes. Shared authenticated context was extracted from the update planner; batch update recognizes
and skips valid state records. The independent state acceptance path validates full original
preconditions, affected branches, changes, digest and receipt identities. Lost responses query the
original state key first; only OPERATION_NOT_FOUND allows identical replay. No stale head/epoch is
silently refreshed, and a malformed/forged result leaves acceptance unknown and the journal pending.
Received receipts preserve observed commitment if local acknowledgement fails.

A repeated uncertain command recovers before any fresh state selection. Dry-run recovery only queries
an existing receipt or re-previews the original request; it never replays the actual mutation or
acknowledges the local record. An earlier committed original receipt can therefore correctly be shown
as committed during a later read-only invocation. Cancellation remains registered across planning,
journal persistence and submission. Planning interruption submits nothing; submission interruption
retains the original key and explicit unknown commitment with exit 130. A dedicated input-only thread
allows interactive confirmation to terminate on Ctrl-C without hanging Tokio on a blocking stdin read.
The existing older add/rule/update confirmation audit remains separate work.

State publication is synchronous and atomic on the Server, so successful receipts are already
published with an operation ID. Common no-wait/timeout options do not invent a deployment queue.
Added owner-authorized GET /skills/state/operations/{id} in the Server repository/service/API layers;
it returns immutable original response_json and never runs a command. Generic `skill status ID`
tries this typed route only after an explicit library OPERATION_NOT_FOUND. `status --last` routes by
the retained request type/key. State status --wait preserves its original deadline across fallback,
and interrupting it changes no remote operation. Existing library operation/wait behavior stays on
its original path. Architecture/state/wire docs and both CLI READMEs describe these boundaries.

Fourteen new CLI contract tests verify item/directory scope, read-only complete previews, stable-ID
submission, exact journal metadata, lost-response and restart recovery, stale precondition rejection,
forged tree/source/epoch receipts, identical replay only after original-key absence, dry-run recovery,
generic status/last, package-batch isolation, query deadlines, planning/submission interruption, and
real PTY yes/no/Ctrl-C confirmation with exactly one prompt. Existing nine mutation contracts also
passed after status routing changes. The full CLI quality gate passed **419 Rust tests**, formatting,
Clippy with warnings denied, shell/Ruby release contracts, managed-tool cache and whitespace checks.
Logs: `/tmp/skill-state-mutation-cli-quality.log`,
`/tmp/skill-state-mutation-cli-contract-final.log`.

Server API tests now verify ID/key receipt equivalence after later state changes, absent IDs and
cross-user/device/node rejection for the new lookup. The complete Server gate passed **1071 tests,
17 skipped, 79.45% coverage**, Mypy over 370 files, Ruff formatting/lint, docstring and whitespace
checks. Logs: `/tmp/skill-state-mutation-server-quality.log` and
`/tmp/skill-state-mutation-server-focused.log`. No schema migration or Node implementation changed.

A real Rust CLI -> authenticated Python Server loopback passed **17 command cases**. It verified
read-only dry runs, original binary/data removal, item and directory epoch changes, preserved root
helpers for item reset, unchanged library generation, detached old-session input, explicit restoration
of that input, directory member-set mismatch, account-local reset, old-revision restore rejection and
new-branch reset. After dropping the HTTP body only after an actual committed state transaction, it
observed exactly one actual POST/epoch advance and recovered the original receipt by key; ID/--last
and later ID queries retained that receipt. Log: `/tmp/skill-state-mutation-loopback.log`. Temporary
harness, private database/content/credentials and loopback listener were cleaned up. These tests use
controlled persisted session fixtures, not real Claude/Docker runtime writer proof.

The goal remains active. Conflict listing/diff/resolution and migrate/prune CLI, Node-only export,
complete system/session/account diagnostics, ended-operation retry, older command interruption audit,
mixed-backend writer proof, safe capture/takeover dispatch, managed snapshot/finalization integration,
retention/rollback lifecycle evidence, actual Native Claude/Docker Sandbox acceptance and final
requirement-by-requirement audit remain. No commit, release, deployment, automatic takeover dispatch
or capability advertisement was performed.

### Conflict history and saved-input diff CLI increment

Implemented `skill state conflicts SKILL --account-id UUID` and account-directory selection, plus
`skill state diff --conflict UUID`. Lists preserve separate publication and migration pages/cursors;
name selection resolves once to a stable library/account-local source UUID. Successful inspections
emit one ready/noncommitted envelope while retaining the record's actual status in its details.
No state initialization, migration recomputation, resolution choice or local mutation journal occurs.

Server publication listing now accepts an optional skill selector. The existing scope service handles
ownership, archived IDs and library/local ambiguity. Repository EXISTS filtering over saved branches
runs before LIMIT and also verifies cursor membership; unchanged observed branches remain included
because conflicts block complete-directory publication. Account-only callers retain their behavior.
The two added API cases cover filtering before pagination, wrong-source cursors, unchanged branches,
real local-member conflicts, ambiguous names and foreign-account local IDs. No schema migration changed.

Typed CLI detail/diff validation keeps original publication snapshot/comparison/finalization references
and exact branch revisions. Migration details retain the full original preparation/incremental receipt,
saved four-side provenance and live drift separately. Revision/checkpoint references must agree with
original preconditions, never live defaults. Only an explicit publication CONFLICT_NOT_FOUND allows
migration-domain fallback; transport, authentication, malformed data and expiry errors remain failures.

Diffs contain bounded manifest metadata only, including binary and link entries. Publication cursors
remain relative paths; migration cursors preserve their native attempt/three-digest/path binding and
16384-byte limit, including valid values larger than the checkpoint cursor bound. Both domains validate
sorted changed paths, entry identities, page boundaries and immutable attempt IDs. Terminal output
escapes remote text. Ctrl-C during a diff emits one noncommitted interruption result with exit 130.

Twelve CLI contracts cover source resolution, independent pages, selector conflicts, exact saved
sources and large integer epochs, cross-domain fallback, forged provenance/envelopes/entries/cursors,
large migration cursor round trips, terminal safety and real process interruption. Both READMEs and
architecture/wire notes document these user-facing contracts.

The final full CLI gate passed **431 Rust tests**, formatting, Clippy with warnings denied,
shell/Ruby release contracts, managed-tool cache checks and whitespace checks. Logs:
`/tmp/skill-conflicts-cli-quality-final.log` and `/tmp/skill-conflicts-cli-contract-final.log`.

The full Server quality gate passed **1073 tests, 17 skipped, 79.47% coverage**, Mypy over 370 files,
Ruff formatting/lint, docstrings and whitespace checks. Log: `/tmp/skill-conflicts-server-quality.log`.
The focused Server API run passed seven cases, including the two additions:
`/tmp/skill-conflicts-server-focused.log`.

Actual Rust CLI -> authenticated Python Server loopback passed **17 command cases** across session
publication, first-use forward preparation and explicit incremental migration conflicts. It verified
item/directory listings, metadata pagination, exact original receipts and absence of query writes.
After later same-epoch source publication, the live diagnostic reported advancement while all saved
inputs and the original receipt remained unchanged. Log: `/tmp/skill-conflicts-cli-loopback-final.log`.
The temporary listener, harness and private test database/content/credential directories were cleaned
up. These are controlled persisted-session fixtures, not evidence of real runtime writer quiescence.

The full goal remains active. Resolution/custom upload and migrate/prune CLI, Node-only export,
complete system/session/account diagnostics, ended-operation retry, older command interruption audit,
mixed-backend writer proof, safe capture/takeover dispatch, managed snapshot/finalization integration,
retention/rollback lifecycle, actual Native Claude/Docker Sandbox acceptance and final design audit
remain. No commit, release, deployment, public takeover dispatch or capability advertisement occurred.

### Upload-free custom resolution preview prerequisite

While connecting CLI resolution, found that both existing verified dry-run endpoints require custom
content already uploaded. That cannot satisfy the design's --file/--directory --dry-run promise of
no upload. Added separate metadata-only content-preview endpoints for both session publication and
migration conflicts. CLI resolve itself is still pending; this increment completes its necessary
Server protocol prerequisite rather than declaring the entire workflow finished.

Requests contain an exact manifest, matching custom choice and expected plan revision; no file bytes,
mutation flag or command key. User/conflict authorization precedes a bounded 64 MiB body read, with
the read transaction released during reception and state rechecked afterward. Canonical digest
validation and pure resolution computation run on workers. The existing conflict algorithms determine
partial versus complete candidates, enforce file/structural/linked-unit rules and replace overlapping
choices only in memory. Existing choices retain their original content authorization.

Responses explicitly remain metadata_only=true, content_verified=false and ready_to_publish=false.
A complete metadata candidate includes its exact digest and full directory changes. Migration results
also show target current-side changes, original-package changes, exact target revision and modified
flag. File bytes, source authorization, user quota admission and final head checks remain pending;
custom metadata never creates a content grant or substitutes for verified publication. Stale input is
rejected rather than recomputed or silently moved to another attempt.

Eighteen new authenticated HTTP cases cover session/forward/incremental directories, partial session
file choices and plan CAS, forward/incremental file previews, deletion-conflict rejection, independent
migration-member rejection, user/device/Node authorization, digest/method/schema mismatch, reset
invalidation, transport bounds and declared quotas. They verify unchanged uploads, trees, grants,
plans, operations, checkpoints, disk files, current-state preconditions and original conflict details.
Real scoped uploads then pass normal verified preview and publication with matching candidate digests;
migration target/original/directory changes match too. An unuploaded preview digest still fails the
normal resolve path. Focused new/existing resolution API regression passed **36 cases** in
`/tmp/skill-resolution-preview-focused.log`; the earlier 15-case iteration is in
`/tmp/skill-resolution-preview-tests.log`.

The final complete Server quality gate passed **1091 tests, 17 skipped, 79.45% coverage**,
Ruff formatting/lint, Mypy over 374 files, Chinese docstrings and whitespace checks. Log:
`/tmp/skill-resolution-preview-server-quality.log`. CLI code is unchanged from the previous verified
431-test gate; no new CLI completion claim is made.

No schema migration, CLI command, Node runtime behavior, public takeover dispatch or capability
advertisement changed. The goal remains active. Next required resolution work includes exact local
state capture (preserving runtime data rather than applying package-only exclusions), typed CLI
preview/upload/receipt APIs, one confirmation, durable original-key acceptance/recovery and status
routing for both conflict domains. The remaining migration/prune/runtime/retention/acceptance and
full design audit requirements remain unchanged.


### 2026-09-23 — confirmed CLI resolution and exact original-request recovery

Implemented `skill state resolve CONFLICT_ID` for session publication, forward preparation and
incremental migration conflicts. All three methods are connected: saved current/incoming side,
ordinary `--path --file`, and complete `--directory`. Clap enforces exactly one method and explicit
file/path semantics. Previews include the original typed conflict and saved side provenance. Native
migration results retain the exact original target revision, modified flag and every target,
original-package and directory override. No incomplete plan is presented as a published checkpoint.

Runtime capture now has a separate state entry point over the shared descriptor-relative copier.
It preserves `.git`, LFS-looking text, exact binary bytes, empty directories, portable modes and
ordinary relative links. State limits replace package file/total defaults, with no extra 10 MiB file
cap. A file is captured as one canonical `content` entry. Final rewalk/change detection includes all
state entries, and capture checks cooperative cancellation. Unsupported local absolute links fail
explicitly because a local symlink cannot provide runtime dependency identity; choosing a saved side
retains existing runtime-link metadata. Recognized checkpoint export bundles are not accepted as
materialized resolution directories. Existing package exclusion/LFS behavior remains verified.

Custom dry runs send only the exact captured manifest to the read-only content-preview endpoint:
no file bytes, uploads, grants, plan edits or local mutation journal. One confirmation precedes scoped
upload. Streaming uses 64 KiB chunks and backpressure, retains staging until completion, and never
reopens the live input. A verified native preview must agree with the reviewed metadata candidate
before journaling/submitting an actual choice. Server quota/source/head checks remain authoritative;
a complete metadata candidate cannot bypass them. A migration directory that alters independent
context fails explicitly before upload. Upload persistence is never mislabeled as choice acceptance.

The `state_resolution` journal stores exact request/domain/conflict, original provenance, prior
choices and the reviewed verified result under the existing Server/user/intent identity and 4 MiB
bound. No content bytes, credentials or local source paths enter request metadata. Recovery precedes
capture or fresh selection, even after the input file disappears. Only a definite nonretryable,
noncommitted original-key OPERATION_NOT_FOUND with no operation ID permits identical replay. Accepted
normal outcomes must match the review and target branch identities; supersession must retain prior
choices and the unchanged plan revision. Invalid/lost acceptance remains unknown under the original
key. A recovery dry run only queries/re-previews and never acknowledges local pending metadata.

Pending choices return committed pending/exit 1, published checkpoints exit 0, superseded original
attempts exit 1 (corrected in the following migration increment to match design §4.6). Ctrl-C during planning/confirmation saves no choice; submission interruption preserves
unknown acceptance and exits 130. The detached input-only confirmation helper is shared with existing
reset/restore, whose PTY and interruption contracts still pass. Package update --all skips validated
resolution records. Generic status/--last routes original typed receipts, retaining the original wait
deadline and allowing domain fallback only on an explicit miss.

Added owner-bound ID lookup for both resolution operation domains in Server repositories/services/API.
Publication lookup returns original response JSON; migration lookup returns the immutable original
result plus separate current diagnostics. ID and original-key lookups agree even after later choices
publish the conflict. Tests cover missing IDs and cross-user/device/Node rejection. No schema, runtime
capability, writer admission, public takeover dispatch or Node deployment behavior changed.

Evidence: 10 new state-capture tests, 19 CLI resolution contracts and 2 real HTTP streaming contracts.
The streaming contract verifies binary data larger than 10 MiB from staged objects after deleting the
source, for both domains. CLI tests cover metadata-only review, unchanged staged bytes, exact journal
and restart replay, misleading missing-key responses, plan CAS, stale supersession, forged previews/
branch provenance, historical status/--last, batch isolation, one real PTY confirmation and Ctrl-C.
The final complete CLI gate passed **462 Rust tests**, Clippy with warnings denied, formatting,
shell/Ruby release checks, managed-tool cache contracts and whitespace checks. Logs:
`/tmp/skill-resolution-cli-quality-verified.log`, `/tmp/skill-resolution-cli-contract-final.log`,
`/tmp/skill-resolution-stream-tests.log`. Focused reset/restore recovery regression also passed in
`/tmp/skill-resolution-recovery-final.log`.

The Server focused API run passed **18 cases** with additional ID/key/ownership assertions:
`/tmp/skill-resolution-id-server-focused.log`. Its final complete gate passed **1091 tests, 17 skipped,
79.43% coverage**, Mypy over 374 source files, Ruff formatting/lint, Chinese docstring checks and
whitespace checks: `/tmp/skill-resolution-id-server-quality.log`.

A real Rust CLI -> authenticated Python Server loopback passed **43 commands across nine scenarios**:
saved-side/file/directory resolution for session publication, forward preparation and incremental
migration. It verifies write-free metadata preview, partial plan then complete publication, preserved
old pending receipts, 12 MiB binary/directory data including Git/LFS/links, correct migration override
reporting and rejection of independent context changes. Replacing the accepted response body with
invalid JSON preserves unknown acceptance; after removing the original local file, repetition recovers
the original receipt with exactly one actual resolution POST. Both generic ID and --last queries keep
that receipt. Final log: `/tmp/skill-resolution-cli-loopback-verified.log`. Temporary harness,
listeners, private fixture databases/content and credentials were removed. These are controlled
persisted-session fixtures, not real Native Claude/Docker writer-quiescence evidence.

The full goal remains active. Migrate/prune CLI, Node-only pending export, full system/session/account
diagnostics, ended-operation retry, older command interruption audit, mixed-backend writer proof,
safe durable takeover dispatch, managed snapshot materialization/finalization, retention/rollback
lifecycle, actual Native Claude/Docker Sandbox acceptance, distribution/upgrade/backup documentation
and the requirement-by-requirement final audit remain. No commit, release or deployment was performed.

### Explicit incremental migration CLI and exit-code correction (2026-09-23)

Implemented `skill state migrate SKILL --account-id UUID --from-revision REV --to-revision REV`,
accepting UUID/rN/positive registration numbers and all common mutation options. It rejects identical
normalized revisions before networking, resolves stable skill/version identities exactly once, and
previews the complete original/last-migrated source baseline against the target's own original/head.
Target and directory diff baselines remain separate. One cancellable confirmation precedes the exact
metadata journal and real submission. Missing target initialization, reverse direction and no-change
migration preserve rule and effective-use semantics.

The distinct `state_migration` schema-4 journal retains the original selector, stable exact request,
complete precondition and reviewed content metadata within the existing 4 MiB bound. Recovery happens
before fresh selection; only definite nonretryable/uncommitted key absence with no operation ID permits
identical replay. Receipts must match reviewed identities, three-side labels/digests, conflicts and
diffs. Publication IDs and sequence are separately checked; unchanged migration must reuse the
original heads. Invalid or lost acceptance keeps the original key and unknown commitment. Recovery
dry-run neither replays nor acknowledges the pending record. Ctrl-C planning/confirmation saves no
request; post-journal interruption preserves unknown acceptance and exits 130. Batch updates skip
validated migration records.

Added owner-bound incremental migration receipt ID lookup without schema changes. ID and key queries
share type/ownership checks and reject first-use preparation identities. Generic CLI status/--last
routes these receipts, keeps original `data.result` separate from current status/replacement/reason,
and retains the original waiting deadline. Successful synchronous publication exits 0; conflicted
preview/acceptance and current supersession exit 1. Also corrected resolution pending/superseded
from exit 2 to exit 1 to match design §4.6, including tests and both READMEs.

Fourteen focused CLI migration contracts cover exact stable request identity, write-free preview,
conflict/no-wait, missing-key replay, lost response recovery, forged metadata rejection, stale
preconditions, independent current status, dry-run recovery, package-batch isolation, PTY confirmation
and interruption. All 19 existing resolution contracts pass with corrected exits. The complete CLI
gate passes **476 Rust tests**, Clippy with warnings denied, formatting, shell/Ruby/cache and whitespace
checks: `/tmp/skill-migrate-cli-quality.log`. Focused logs: `/tmp/skill-migrate-cli-contract.log`,
`/tmp/skill-migrate-resolution-regression.log`. Server focused API tests passed five cases, including
ID/key equivalence, missing IDs, preparation type rejection and cross-user/device/Node denial:
`/tmp/skill-migrate-server-focused.log`.
The complete Server gate passes **1092 tests, 17 skipped, 79.45% coverage**, Ruff formatting/lint,
Mypy over 374 source files, Chinese docstring checks and whitespace checks:
`/tmp/skill-migrate-server-quality.log`.

Real Rust CLI -> authenticated Python Server loopback passed **26 commands across four scenarios**:
late source increments preserve target deletion and target-only work; repeated no-change migration
keeps heads; reverse migration preserves pin; confirmed conflict keeps the directory unchanged and
last-success baseline fixed; reset supersedes the old receipt and permits a new-epoch migration.
An intentionally malformed accepted response preserves unknown acceptance; a fresh CLI invocation
recovers by original key with exactly one actual migration POST. ID and --last return the original
result. Final log: `/tmp/skill-migrate-loopback-verified.log`. The first harness attempt lacked the
repository pytest configuration; the next assumed malformed-response recovery happened in-process.
The final run explicitly supplies the configuration and exercises restart recovery. No product
validation was bypassed. Temporary harness, listeners, credential and twelve fixture directories were
removed. These remain controlled persisted-session fixtures, not actual runtime backend acceptance.

The overall goal remains active. Prune requires Server history retirement, retention clocks and
reference-safe GC as well as CLI wiring; only staging expiration exists today. Node-only pending
export, full system/session/account diagnostics, ended-operation retry, older command interruption
audit, mixed-backend writer proof, safe durable takeover dispatch, managed snapshot materialization
and finalization, retention/rollback lifecycle, actual Native Claude/Docker Sandbox acceptance,
distribution/upgrade/backup docs and the final requirement-by-requirement audit remain. No commit,
release, deployment, public takeover dispatch or runtime capability advertisement was performed.

### Retention protection graph and reference inventory (2026-09-23)

Continued toward prune by auditing all current content and historical foreign keys. Existing retained
snapshot/finalization/preparation rows would permanently retain data if prune merely cleared checkpoint
flags. Current directory membership also requires explicit compaction before historical branch
retirement. These dependencies are now documented in Server `docs/skill-retention.md`; this increment
implements the shared reference analysis needed by that lifecycle, without claiming prune complete.

Added `SkillRetentionInspector`, an owner-scoped repository index, explicit reference-table policies,
and a bounded pure graph plus focused service modules for branches/content/operations/migrations.
Roots cover active defaults, explicit package pins (including saved pins on removed installations),
current branches even while disabled, applicable current-epoch branch pins, local initial snapshots,
active session snapshots, pending finalizations, complete unresolved publication/migration comparisons,
authorized custom trees, valid latest incremental baselines, pending takeover, live upload leases and
fixed revisions of pending library operations. Unknown operation status/missing fixed identity rejects
analysis. Package/state quota identities remain separate while shared physical blobs are protected by
either category or an active upload.

Historical parent and effective-use pointers are deliberately not perpetual roots. Current directory
members are reported as compaction obligations; full contexts retained by active snapshots,
finalizations, conflicts and local originals retain their member checkpoints. The result is a
protection analysis, not an immediately deletable candidate list. New skill tables or foreign-domain
skill reference tables must be explicitly classified. Existing-table column/state changes still need
manual reference review; the table guard does not prove those changes safe.

Repository reads omit unrelated potentially large JSON, cap total index rows and preflight required
JSON text size before decoding. The graph has explicit node/edge limits and cannot produce a closure
after a limit failure. New users do not acquire synthetic storage rows; existing-user inspection uses
the production storage lock without modifying lock counters, content or clocks.

Focused tests cover shared-reason propagation and cycles, metadata/graph bounds, owner isolation and
write-free reads, disabled current roots, tool/account pin scope, old head/parent eligibility with
explicit directory obligations, pending inputs, conflict/custom-content protection and reset release,
latest baseline replacement and epoch changes, local reset baselines, upload expiry, takeover roots,
unknown pending operation shapes and reference-schema classification. **23 cases passed on PostgreSQL
17** against a database initialized by Alembic through head 0039. An independent reader/writer/observer
connection test proves the inspection transaction blocks new references under the same user lock.
Logs: `/tmp/skill-retention-postgres-migration.log`, `/tmp/skill-retention-postgres.log`. Temporary
container and its anonymous volume were removed. SQLite test success is not substituted for this
production row-lock evidence.

Prune remains incomplete: retention clock schema and transactional release/reacquisition updates,
explicit retirement of historical snapshot/finalization/migration content references, current-directory
compaction, candidate deadlines and usage diagnostics, two-phase durable physical GC with rollback/
retry, exact preview/commit API and CLI are still required. No deletion endpoint, schema migration,
public takeover dispatch, runtime capability advertisement, commit, release or deployment was added.
The full goal remains active, including the runtime/backend and delivery requirements recorded above.

The retention increment complete Server gate passed **1114 tests, 18 skipped, 79.80% coverage**,
Ruff formatting/lint, Mypy (389 checked files), Chinese docstrings and whitespace checks. Log:
`/tmp/skill-retention-server-quality.log`. The added skipped case in this default gate is the
PostgreSQL independent-connection lock test, separately passed in the 23-case PostgreSQL run.
CLI and Node were unchanged in this increment; their prior gate evidence remains recorded above.


### Transactional history release clocks (2026-09-23)

Server migration `0040_skill_retention_clocks` adds nullable UTC `retention_released_at` to package
revisions, local revisions, checkpoints, session snapshots, finalizations, publications and branch
preparations. Existing unknown release times remain NULL. A timestamp is neither a content-retirement
flag nor deletion authorization, and original identities, digests and immutable receipts stay intact.

The explicit async `retention_mutation` freezes the before-protection set under the common storage
user lock, executes the domain mutation inside a savepoint, then records final release/reacquisition
transitions. New unprotected candidates begin their clock in the transaction that creates them;
existing unprotected records are not initialized or reset by observation. Protection clears the clock;
a later release starts it again. Nested domain calls share the outer analysis while preserving inner
rollback savepoints. Analysis failure rolls back domain changes even if the caller catches the error
and commits its outer transaction. There are no synchronous database events or commit hooks.

Integrated existing library/rule/epoch changes, state reset/restore, preparation, migration, both
resolution domains, snapshot reservation, finalization begin/complete, publication/recomputation,
local candidate registration, takeover completion, account-override removal and session-reference
release. Existing Node result/failure, runtime reconciliation and interrupted-session stop also join
the context before mutating references. Multi-owner reconciliation locks owners in stable order;
users with no storage record do not acquire one from ordinary runtime lifecycle writes. Contexts
finish before the caller commits or publishes external revocations. Future runtime snapshot start/
cancellation writers must join this same boundary when those integration paths are implemented.

The internal read-only history inspector returns protection reasons, release times, archive status
and policy-derived waiting deadlines. Defaults are 30 days ordinary and 90 days archived; old
installation epochs stay archived after reinstall. Complete contexts containing archived members use
the archive period. Unknown clocks and protected identities have no usable deadline. CLI/API info and
status exposure still need integration. Deadline expiry cannot bypass current-directory compaction,
active roots, historical foreign-key retirement or physical deletion protocol.

Thirteen focused clock cases cover last-reference release, late finalization, pin reacquisition,
preview/replay/unknown legacy history, outer rollback, analysis failure with caught exception, nested
rollback/reuse, complete conflict release, task completion/failure/reconciliation, interrupted stop,
archive/reinstall/custom policy deadlines and two independent PostgreSQL pin races. Default SQLite
runs skip only the two production lock races; both were separately run on PostgreSQL 17. Together
with existing retention tests and the caught cross-user-error regression, **37 PostgreSQL cases passed** against a schema created by Alembic
through 0040: `/tmp/skill-clocks-postgres.log` and `/tmp/skill-clocks-postgres-migration.log`.

A separate database copy verified each of seven populated tables independently blocks downgrade
before any column is removed. With unknown NULL clocks only, 0040 -> 0039 -> 0040 preserves all seven
tables' full identity/content/receipt fingerprints and leaves legacy clocks NULL. Log:
`/tmp/skill-clocks-migration-roundtrip.log`. Temporary PostgreSQL container, anonymous volume and
harness scripts were removed. No test or fixture proof is presented as Native Claude/Docker Sandbox
runtime acceptance.

These clocks apply to retained history identities, not standalone tree/object leases. Upload roots
point to objects and do not propagate backward into those identities; natural upload expiry therefore
does not release these history roots. Object-level lease cutoffs, historical snapshot/finalization/
comparison-reference retirement, directory compaction, durable two-phase deletion and retry,
public prune preview/commit and CLI still remain. The complete goal stays active, including the
runtime/backend, diagnostics, export, operation recovery, distribution and final acceptance work
recorded above. No commit, release, deployment, public takeover dispatch or capability advertisement.


The first full gate found one caught-error regression: acquiring storage by creating a new row outside
the business savepoint could leave that row after an unauthorized operation failed and the caller
committed its outer transaction. The fix locks existing rows before the savepoint using an UPDATE
that also establishes SQLite's real outer write transaction when no row matches; only new-row
creation happens inside the savepoint. This preserves both caught-error cleanup and outer rollback.
The combined clock/migration-resolution regression run passed **31 tests, 2 PostgreSQL-only skips**:
`/tmp/skill-clocks-regression-fixed.log`. The final PostgreSQL rerun of **37 tests** includes the exact
caught-error case and both connection races. The final full-gate evidence is recorded separately below;
`/tmp/skill-clocks-server-quality.log` retains the earlier failed run.


The final complete Server gate passed **1125 tests, 20 skipped, 80.42% coverage**, Ruff format/lint,
Mypy over **394 files**, Chinese docstrings and whitespace checks:
`/tmp/skill-clocks-server-quality-verified.log`. The two additional skips are the new independent
PostgreSQL clock races, both passed in the final 37-case PostgreSQL run. CLI and Node repositories
were unchanged in this increment; previous gate evidence remains recorded above. Server-side
existing Node-result/session lifecycle handlers were updated as described here.

Server retention documentation now also inventories nine historical tables with eleven direct
stored-tree foreign keys, plus the tree/object dependency table's two foreign keys. Explicit retirement
must separate immutable digest/identity evidence from live content references, particularly where a
digest is a primary key or required by terminal-state checks. It remains unimplemented. Before GC
can ship, deployment/restore acceptance must also prohibit mixed old Server writers or explicitly
invalidate clocks whose complete writer coverage cannot be proved. Schema compatibility alone is
not GC readiness. The full goal remains active and incomplete.


### Historical comparison content retirement (2026-09-23)

Migration `0041_skill_history_retirement` separates immutable audit digests from live tree foreign
keys on six tables: session snapshots, finalizations, publications, branch preparations, publication
resolution choices and migration custom-content grants. Nullable `content_retired_at` controls eight
stored generated `retained_*` references. Original digests, primary keys, choices, source identities,
checkpoint pointers and receipts stay unchanged. Active snapshots, pending finalizations and unresolved
comparisons cannot use retirement to bypass their content constraints. The finalization/checkpoint
composite foreign key now binds immutable `content_digest`, preserving exact user/account/scope/
checkpoint/content identity while allowing future explicit checkpoint-content retirement.

`SkillHistoryRetirementService` is an internal account-bound entry point for an exact set of snapshot,
finalization, publication or preparation identities. It verifies the entire selection before changing
anything, under the existing user lock and retention savepoint. Hard roots always reject retirement;
normal requests also require a known expired waiting deadline. Explicit all-unreferenced bypasses
waiting only. A retained finalization blocks retirement of its snapshot; a retained publication blocks
retirement of its finalization unless that parent is selected too. Active scoped migration uploads
also block retirement, preserving their existing transfer contract. Choices and custom grants retire
atomically with their comparison, and repeated retirement returns no new changes.

Retired comparison info exposes unavailable sides as NULL without changing original receipts or
saved provenance. Diff/export and new resolution/recomputation reject expired inputs even when another
record retains identical bytes. Migration upload status/key recovery remains readable; content transfer
or completion cannot recreate content grants after retirement. The protection graph no longer follows
retired full-comparison content, but retains independent valid successful incremental checkpoint
baselines. A late runtime result that would reactivate a retired snapshot fails STATE_EXPIRED and
rolls back both the task result and session state even when its caller catches the error.

Eleven new tests cover protection and ordinary deadline refusal, explicit early retirement, exact
account/identity preflight, retained-parent dependencies, outer rollback, original response replay,
custom-choice and grant identity preservation, shared-content expired reads, actual generated-FK
release, active-status database constraints, cross-account same-digest checkpoint substitution,
continued incremental migration through a retired successful comparison, and late-runtime rejection.
The fixture-only tree deletion test proves the grant's foreign key is released; the production service
does not delete trees or objects or settle quotas.

The final PostgreSQL 17 run passed **47 cases** against a schema created by Alembic through 0041,
combining the eleven retirement cases with existing retention/clock cases, including independent
connection lock tests: `/tmp/skill-retirement-postgres-verified.log` and
`/tmp/skill-retirement-postgres-migration.log`. An independent database seeded with normal retained
histories verified all six downgrade guards and eight generated references. With no retirement evidence,
0041 -> 0040 -> 0041 preserves complete historical identity/digest/choice/receipt fingerprints and
leaves legacy retirement timestamps NULL. Logs: `/tmp/skill-retirement-migration-roundtrip.log`,
`/tmp/skill-retirement-upgrade-fixtures.log`. Temporary PostgreSQL container and anonymous volume,
and the migration/model harness scripts were removed.

The full goal remains active. This step retires comparison content references only. Public prune still
requires exact reviewed selection/recovery, current-directory compaction, checkpoint retirement and
expired-branch handling, quota settlement and durable two-phase physical GC with object lease/reuse
checks. Package/history cleanup outside state-prune, runtime materialization/finalization, actual Native
Claude/Docker Sandbox acceptance, Node-only pending export, complete diagnostics/retry/interruption,
deployment/backup and the final requirement-by-requirement audit also remain. No public prune or
takeover dispatch, runtime capability advertisement, commit, release or deployment was added.

### Checkpoint content retirement and expired branches (2026-09-23)

The internal exact-account history retirement transaction now accepts checkpoints alongside comparison
histories, using existing retained/tree_digest and branch expired fields. Migration head remains 0041.
Every selected identity must pass current protection and its own waiting deadline before any mutation.
Retained snapshots/items, finalizations, publication inputs/results, migration inputs/results, complete
directory members and item backing directories block retirement unless the dependent histories also
retire. Directory membership and parent/backing identities remain audit records. Current-directory
materialization therefore still blocks unsafe historical-member retirement until compaction is built.

Retiring a historical branch head atomically clears its checkpoint content reference and marks the
branch expired, retaining the original head pointer and state epoch. Retiring other history does not
expire the live branch. Selecting/pinning an expired version keeps an honest expired view; ordinary
preparation and snapshot reservation reject STATE_EXPIRED. Explicit reset creates a new head and epoch;
restore/export of the retired checkpoint rejects even when shared bytes remain stored. Current directory
or other protected exact references cannot target retired checkpoints; the retention mutation rolls
back late reference changes, including when the outer caller catches the error and commits.

Seven new SQLite cases passed, with two PostgreSQL-specific races skipped locally. A combined
PostgreSQL 17 run passed **52 tests** against Alembic-created schema 0041. Independent connections prove
that pin and retirement really wait for the same user lock: pin-first rejects retirement, while
retirement-first permits later pin but preserves expired state. Evidence:
`/tmp/skill-checkpoint-retirement-tests.log`, `/tmp/skill-checkpoint-retirement-postgres-verified.log`,
`/tmp/skill-checkpoint-retirement-postgres-migration-verified.log`. The temporary database container and anonymous
volume were removed. The final full Server gate passed **1143 tests, 22 skipped, 80.70% coverage**, including Ruff, Mypy (402 files), docstrings and whitespace checks: `/tmp/skill-checkpoint-retirement-server-quality-verified.log`.

This internal step does not compact current directories, release tree/object rows, settle quotas,
physically delete files, or expose public prune. Exact preview/commit recovery and CLI wiring remain.
CLI and Node code are unchanged in this increment. The overall goal remains active and incomplete.

The retained first revision of a staged/removed account-local source also blocks retirement of its
source checkpoint: later materialization uses that exact backing identity. This is a retained-history
dependency, not an additional active root or permission for state prune to delete original revisions.
Its regression and the final PostgreSQL run pass. The first full checkpoint gate passed 1142 tests,
22 skipped, 80.70% coverage; the final full rerun passed **1143 tests, 22 skipped, 80.70% coverage**, including the subsequently added local-source case.
The next compaction constraints are documented in Server `docs/skill-directory-compaction.md`; no
compaction implementation is claimed.

### Compose content persistence preparation (2026-09-23)

Root Compose now mounts a dedicated `skill-content` named volume at
`/var/lib/agent-remote/skill-storage`; the fixed Server root is its private `content` child so the
service can create mode 0700 without treating Docker's default volume-root permissions as private.
The env example exposes disabled-by-default SKILL_MANAGER_ENABLED and JSON SKILL_STORAGE_POLICY.
Existing component/image pins remain unchanged. This prepares storage without enabling takeover,
GC or runtime capability, and is not a deployment or release.

Deployment and backup documentation now separates PostgreSQL-only backups from coordinated skill
backups, preserves the original Compose project/volume identity, stops all content writers/workers
for the snapshot pair, restores into empty isolated storage, and includes configured Node-only
pending state. Permission/digest validation and complete writer coverage are required before future
GC; a database restore cannot recreate missing object bytes or erase retirement evidence.

Validation: Compose defaults with and without new env fields, custom JSON policy, and the existing
device-test overlay all parse correctly. Isolated Docker volumes survive container recreation and
tar backup/restore with identical fixture bytes, UID and 0700/0400 modes. This uses the cached
PostgreSQL image only as an isolated shell/tar harness, not as actual Server-image or backend recovery
acceptance. Fixture volumes were removed. Root release-workflow contract and whitespace checks pass.
Evidence: `/tmp/skill-compose-persistence-check.log`. Complete DB/object consistency restore, upgrade,
release composition and real Node/Native/Docker recovery remain pending.

### Internal current-directory compaction (2026-09-23)

Server `services/skills/compaction/` now provides read-only preview and exact-plan atomic apply for
1–1000 account-owned item checkpoints. It checks current protection and each selected history's real
ordinary/archive deadline; explicit all-unreferenced bypasses waiting only. It reads the current
complete directory and the explicit backing directories of protected branch heads, preserving root
auxiliary data and every unselected identity. Link-connected roots that cannot be separated are
reported as blocked. Protected subtree views independently prevent removal even when an old member
identity aliases the same root. Legacy heads without backing evidence remain unchanged.

Content changes propagate through head/backing/member references to determine every directory that
needs a new identity. Apply rebuilds the complete plan under the retention user lock/savepoint before
registering any content, creates new directories and equivalent item checkpoints, then swaps all
heads and current member references atomically. Branch/directory epochs and library rules stay fixed.
Old checkpoints, memberships, snapshot inputs, original receipts and exact successful migration
baselines remain unchanged. A baseline still protects its old checkpoint after an equivalent head
replacement; a real subsequent incremental migration is tested successfully.

Preview verifies actual bytes, limits and aggregate quota without creating uploads, clocks or usage
changes. Missing bytes or a lowered quota reject before mutation. No-op plans create no new content;
final CAS failure, caught errors and outer rollback preserve the original domain state. Old views
start their waiting clock only when they actually lose protection. The service does not retire old
history, settle quotas or claim reclaimed physical space. It is internal and has no durable request
receipt; public prune must supply that contract before exposing apply.

Initial SQLite tests passed 13 cases, and four additional boundary cases passed: active snapshot
protection, legacy backing omission, invalid-format preservation and archived old epochs after
same-source reinstall. Two PostgreSQL-only races prove that compaction waits for an uncommitted pin,
rejects after its commit, and proceeds only after its rollback. Initial combined PostgreSQL 17 tests
passed 63 cases against Alembic schema 0041; the final combined PostgreSQL run passed **67 cases**
and its container/anonymous volume were removed. The final full Server gate passed **1160 tests,
24 skipped, 80.90% coverage**, including Ruff, Mypy (411 files), docstring and whitespace checks:
`/tmp/skill-directory-compaction-server-quality-verified.log`. Evidence is recorded in Server
`docs/skill-directory-compaction.md`.

Remaining work includes public item/account-directory prune scope, complete reviewed loss preview,
original-request recovery, composition with historical retirement, exact tree/object reference release
and quota settlement, durable two-phase deletion, deleting-object admission and lease cutoff checks.
The broader runtime/backend, CLI diagnostics/retry, deployment acceptance and full design audit also
remain. No public prune or takeover dispatch, runtime capability advertisement, commit or release was
introduced. CLI and Node were unchanged this increment.

The public prune integration constraints are now collected in Server `docs/skill-state-prune.md`,
including compact digest-bound confirmation compatible with the CLI's 4 MiB exact-request journal,
protection analysis after hypothetical compaction without dry-run writes, cross-batch dependencies,
and atomic logical retirement/deletion-task admission. This is a design for the next implementation
step, not a claim that a prune route, CLI command or GC worker exists.

Final directory-compaction validation: **1160 passed, 24 skipped, 80.90% coverage** in the full Server
gate; Mypy covered 411 files, with format/lint/docstrings/whitespace all passing. The extra two skips
are compaction/pin races already proven in the PostgreSQL run. Final PostgreSQL evidence is
`/tmp/skill-directory-compaction-postgres-verified.log` (**67 passed**), with schema initialized by
Alembic through 0041. The initial 1156-test gate predates four additional boundary cases; use
`/tmp/skill-directory-compaction-server-quality-verified.log` for final full-gate evidence.


### Read-only protection after directory compaction (2026-09-23)

The internal `SkillDirectoryCompactionService.retention_preview(user_id, expected_plan)` now
rebuilds and compares the exact compaction plan under the user read lock, then computes before/after
protection at one fixed time without editing ORM rows, flushing hypothetical heads or creating
uploads. A bounded graph overlay introduces stable preview-only checkpoint identities, complete
result-tree/object dependencies and replacement current heads/members. Original historical
checkpoints, backing references, members, snapshots, comparisons and exact migration baselines remain
unchanged. Preview identities record their original checkpoint and reject collisions with actual
checkpoints; they are not valid persisted checkpoint IDs.

The result includes original histories' forecast protection and deadlines, plus newly released
identities. Newly released history starts its forecast waiting at analysis time even if a stale
release timestamp exists. Unknown unprotected clocks remain unknown; protected identities have no
usable expiry. Archive classification remains conservative, including complete directories and
views originating in an archived session. These forecasts do not mutate durable clocks and must not
be serialized as a final prune authorization or interpreted as reclaimed space.

Nine new service cases cover commit-after-preview fingerprints and empty ORM mutation sets,
full graph equivalence with real publication (including linked no-op), owner/pin revalidation,
unknown/stale clocks, collision rejection, 90-day archive forecasts, a package upload lease
protecting a shared blob removed from the state result, active snapshot identity retention, legacy
heads without backing evidence, and changed-plan rejection. The final focused run passed all nine:
`/tmp/skill-compaction-projection-final-tests.log`. Existing tests additionally compare exact
projected versus actual graphs for metadata-only cross-directory propagation and successful migration
baselines. The actual next incremental migration still succeeds. Original retained-history dependency
checks continue to reject retirement; this projection does not simulate history retirement.

**44 PostgreSQL 17 cases passed**, with schema created by Alembic through 0041, including two new
independent-connection projection/pin races. Projection demonstrably waits for the pin lock, rejects
the old plan after pin commit and remains read-only after pin rollback. Temporary database container
and anonymous volume were removed. Evidence: `/tmp/skill-compaction-projection-postgres.log` and
`/tmp/skill-compaction-projection-postgres-migration.log`. Full Server gate evidence is recorded below. No model/schema migration, public route, CLI or Node change was introduced.

The complete goal remains active. Public prune still needs stable scope selection, complete reviewed
loss/dependency enumeration, compact digest-bound durable request recovery, atomic retirement and
quota settlement, persistent two-phase deletion jobs, shared user/digest admission barriers and
unbound completed-upload retention. Runtime/backend acceptance and all other outstanding groups
remain. Server `docs/skill-state-prune.md` now records the concrete projection entry point and the
cross-category storage/replay/expiry-collector barriers required before physical GC.


The complete Server gate passed **1167 tests, 26 skipped, 81.00% coverage**, with Ruff format/lint,
Mypy over **414 files**, Chinese docstrings and whitespace checks:
`/tmp/skill-compaction-projection-server-quality.log`. Its pytest collection preceded the final two
active-snapshot/legacy projection tests; all **nine** projection cases subsequently passed together in
`/tmp/skill-compaction-projection-final-tests.log`, with formatting/lint checked again. Production
implementation did not change after the full-gate run started. The two additional PostgreSQL-only
skips are the projection/pin races already passed in the 44-case PostgreSQL run. No test database or
fixture volume remains.


### Complete retained-history dependency plans (2026-09-23)

Server now uses one explicit retained-history dependency graph for both preview and actual
retirement. Edges distinguish backing directories, directory members, local originals, snapshots,
finalizations, publication inputs and the six migration checkpoint roles. Terminal retained
comparisons remain consumers; retired comparisons and ordinary parent/audit pointers do not create
permanent recovery obligations. Reverse closure includes every retained consumer, handles cycles and
shared inputs, and retains each consumer's complete input edges for exact revalidation. Other inputs
are displayed without becoming automatic retirement targets.

`SkillHistoryRetirementPlanner.preview` returns a complete account-bound plan with original
selection, dependent recovery losses, immutable content digests, retention deadlines, blockers and
expiring branches. Current protection, pending migration input uploads, unknown or unexpired waiting,
local original revisions and projected replacement members are explicit blockers. An invalid initial
identity/owner/account rejects the whole selection. No preview writes ORM rows, clocks or uploads.
`apply` reconstructs and compares the entire original plan under the user lock/savepoint before
calling the unified retirement service. A changed pin, new consumer, upload or eligibility invalidates
the original plan. Any blocker refuses the whole plan rather than silently retiring its easy subset.

The old 1000-identity retirement limit is replaced by the complete index's safety budget of one
million identities and four million dependency edges; exceeding a budget fails the whole analysis.
Migration upload lookup reads all selected IDs in 500-ID SQL chunks with exact ownership and a fixed
lease cutoff. This is a correctness bound, not capacity acceptance. Tests create 1001 additional
actual backing-dependent views and prove whole-group rollback and retirement without truncation.

Compaction's `retirement_preview` combines its exact protection projection with the full consumer
plan. Normal mode preserves the real waiting period of newly released old equivalent views. Early
mode still rejects precise migration baselines, retained local originals, active inputs and new
replacement references. A verified complete early selection can compose existing compaction and
retirement services in the same outer retention savepoint; injected failure after actual retirement
flush rolls everything back even when the outer caller catches it and commits.

Thirteen new cases (three graph, six planner, four compaction-composition cases) plus two strengthened
upload/baseline regressions passed as a **15-case focused run**:
`/tmp/skill-history-plan-final-tests.log`. **39 PostgreSQL 17 cases passed**, including two new
independent-connection exact-plan/pin orderings and the large dependency rollback case. The schema was
created by Alembic through 0041. Logs: `/tmp/skill-history-plan-postgres.log` and
`/tmp/skill-history-plan-postgres-migration.log`. Its container and anonymous volume were removed.

No schema migration, public prune operation receipt, CLI command, quota settlement or physical
reclamation is introduced. Internal exact-plan apply is not a durable idempotent public endpoint;
after retirement its old preview changes, while a new preview of an already retired identity is an
explicit no-op. Public original-receipt recovery must precede expired-input access. Full account
candidate selection, compact digest-bound confirmation, cross-batch compaction, actual tree/object
reference release and two-phase deletion remain. The complete goal stays active, including runtime,
backend, diagnostics, distribution and final acceptance requirements above.


Final complete Server gate: **1182 passed, 28 skipped, 81.14% coverage**, Ruff format/lint,
Mypy (**421 files**), Chinese docstrings and whitespace checks all passed:
`/tmp/skill-history-plan-server-quality.log`. This run includes all thirteen new cases and the prior
turn's final two added projection cases. Two new PostgreSQL-only skips are the exact-plan/pin races
already passed in the 39-case PostgreSQL run. No live test processes, temporary database containers
or fixture volumes remain. No commit, release, deployment, public takeover dispatch or runtime
capability advertisement was added. CLI and Node repositories were unchanged this increment.


### Stored-tree clocks and shared-content deletion admission (2026-09-23)

Migration `0042_skill_tree_retention` adds nullable UTC release clocks to complete stored trees.
Fresh successful upload completion starts or refreshes unprotected waiting, including complete
unbound uploads and fresh reuse of existing trees. Committed completion replay and metadata reads
do not refresh clocks. Existing reference transactions now maintain tree clocks alongside history
clocks: hard protection clears them, final root release starts waiting, and retiring already
unprotected history does not add a second waiting period. Legacy unknown clocks remain NULL.
The internal history UUID selection contract is unchanged; unbound trees do not acquire a fabricated
account scope. Loading the tree inventory defers manifests; content reads explicitly reload complete
trees so retention analysis cannot leave content callers with inaccessible deferred attributes.

`SkillRetentionInspector.trees` provides read-only deadlines, protection reasons and complete actual
historical FK references, including generated retained digests and composite authorization keys.
Schema classification checks every real incoming tree digest FK, even additions to already-classified
tables. Original package/local revisions, checkpoint content, retained snapshots/finalizations,
publication and migration comparisons, resolution choices and custom grants are explicitly covered.
Expired ordinary tree waiting does not override archived history deadlines or retained historical
FKs. The result is not deletion authorization and does not claim reclaimed bytes.

Shared-content admission now checks all quota categories for the same user/digest. Any deleting
marker rejects new upload acceptance, prepare/put, fresh or replayed complete, actual tree/file reads,
state admission previews and existing package install/pin references. Exact original upload begin/get
and mutation receipt queries remain available as metadata recovery. Checks share the user lock with
reference writes. The existing staging collector continues to retain all registered objects,
including deleting objects. This increment does not create deletion markers or implement a worker.

Focused SQLite evidence: **27 passed, 2 PostgreSQL-only skipped** for new clock/admission tests,
plus **5 passed** for strengthened actual-reference retirement tests. Logs:
`/tmp/skill-tree-admission-final-tests.log` and `/tmp/skill-tree-reference-tests.log`.
**68 PostgreSQL 17 cases passed**, including independent-connection deleting-marker commit/rollback
races, tree clocks, historical FK inventories, retirement, compaction and pin ordering. Database schema
was created through Alembic 0042. Evidence: `/tmp/skill-tree-postgres.log` and
`/tmp/skill-tree-postgres-migration.log`.

A separate disposable database verifies that 0041→0042 preserves the complete legacy tree fingerprint
and leaves its clock NULL. A non-NULL clock blocks downgrade before any schema, row or Alembic version
change. After resetting the clock only in this disposable fixture, 0042→0041→0042 preserves the whole
original row and NULL clock. Evidence: `/tmp/skill-tree-migration-roundtrip.log`, reproducible script
`/tmp/verify_skill_tree_migration.py`. The temporary container and anonymous volume were removed.

Public prune still requires complete reviewed scope selection, compact digest-bound durable receipts,
account-wide compaction, actual tree/object reference retirement, per-category quota settlement and
persistent two-phase physical deletion. Same-category zero-reservation upload leases must remain safe
when category objects are retired, and another category's physical file retention must not be confused
with quota release. The complete runtime/backend, diagnostics, distribution and acceptance groups
remain outstanding. No commit, release, deployment, public takeover dispatch or runtime capability
advertisement was added. CLI and Node were unchanged in this increment.


Final complete Server gate: **1209 passed, 30 skipped, 81.22% coverage**; Ruff format/lint,
Mypy (**427 files**), Chinese docstrings and whitespace checks all passed:
`/tmp/skill-tree-server-quality-final.log`. All new tests and strengthened reference inventories were
included. The two new PostgreSQL-only skips are the deleting-marker races already passed in the
68-case PostgreSQL run. The migration graph now asserts the actual unique 0042 head. No test process,
temporary database container or fixture volume remains. The full goal remains active.


### Actual content reclamation and persistent deletion workers (2026-09-23)

Server migration `0043_skill_content_deletions` adds original deletion UUIDs, immutable user/digest/
size/category masks, pending/complete state, completion time and bounded retry metadata. A partial
unique index permits only one pending task per shared user/digest. Upgrade rejects preexisting
unowned deleting markers before creating the task table; downgrade rejects any deletion history or
marker before changing schema. Available legacy trees and objects are not backfilled or rewritten.

`SkillContentReclamationService.preview/apply` now provides internal exact tree/object reclamation.
The plan carries actual tree clocks, hard protection and retained FKs, both categories of each affected
file, original object creation identities, all actual tree edges and exact live upload identities/
deadlines. Apply re-creates and compares the complete plan under the same user lock/savepoint before
any mutation. Unknown/unexpired tree waiting, protection, retained-history references, foreign owners
or unavailable content refuse the whole plan. Early mode only bypasses tree waiting. Explicit orphan
object selection can clean up objects previously left behind for upload leases; it never silently
expands to another category or account's history.

Deleting selected tree edges only releases a category object when no other tree or same-category
active upload retains it. Zero-reservation uploads preserve the original category usage. Another
category's object or any live upload retains shared file bytes while allowing genuinely unused
category quota to be released. The last physical release atomically settles category usage, marks
objects deleting and inserts the original pending task. Deleting rows no longer consume logical
quota; completion removes only markers and never subtracts quota twice. Results distinguish category
release from pending physical bytes and never claim that SQL acceptance already freed disk space.

The new worker owns independent transactions, so it cannot consume its caller's uncommitted mark.
It revalidates exact markers, both categories, actual tree edges and uploads under the user lock;
I/O failures retain barriers and sanitized error codes with bounded backoff. Missing files converge
after unlink-before-commit crashes. Cancellation waits for actual disk threads to exit before SQL
rollback or lock release. Terminal task replay does not touch files uploaded again under the digest.

The disk layer additionally uses a process-shared flock on the stable private user directory and
per-original-task completion receipts in `.deletions`. This covers database connection loss while
old I/O is still runnable: completed receipts prevent late duplicate disk calls from deleting new
content even after another worker has completed the SQL task. Receipt creation/fsync follows actual
unlink/fsync and precedes SQL completion. Staging collection leaves these receipts untouched.
Coordinated backup/restore must preserve both receipts and the matching task table; the root runbook
now documents that boundary.

Server lifespan now consumes only already committed tasks when `SKILL_MANAGER_ENABLED` is enabled.
The flag remains false by default. New bounded settings expose a 30-second polling interval and
100-task batch, with matching root Compose/default and device-test overlay rendering verified.
There is no automatic selection of histories or trees. No deployment or live user's cleanup was run.

Focused tests: **30 passed, 3 PostgreSQL-only skipped**, plus **1 passed** for complete history
retirement + tree/quota/task composition in one outer savepoint. Logs:
`/tmp/skill-content-gc-final-tests.log` and `/tmp/skill-content-gc-history.log`.
The expanded **76-case PostgreSQL 17 run passed**, including three independent-connection tests:
uncommitted marks cannot authorize unlink; new uploads wait for actual worker completion/commit;
and forcibly terminating a real worker DB connection allows a second worker to complete and a new
upload to succeed, while the old delayed I/O still leaves the new bytes intact. Other cases cover
thread cancellation/flock, filesystem safety, zero-reservation and cross-category leases, changed
plans, marker/consumer revalidation, immutable task replay, state constraints, lifecycle retry and
prior clock/compaction invariants. Evidence: `/tmp/skill-content-gc-postgres-final.log`, with Alembic
0043 schema in `/tmp/skill-content-gc-postgres-migration.log`.

An independent PostgreSQL upgrade fixture verified marker-blocked upgrade, unchanged full legacy
tree/object fingerprints across 0042→0043→0042→0043, and refusal to downgrade even completed task
history before any schema/version/row change. Logs: `/tmp/skill-content-gc-migration-roundtrip.log`;
script: `/tmp/verify_skill_gc_migration.py`. The test container and anonymous volume were removed.

Public prune still needs complete account/item scope and candidate selection, account-wide atomic
compaction, compact digest-bound confirmation and durable original-key/ID recovery. These must compose
history retirement and this actual content layer under one user transaction. Public usage/deadline/
deletion progress diagnostics, broader capacity and coordinated restore acceptance, and all pending
CLI/Node/runtime/backend/distribution groups remain. Internal exact-plan apply is not a public
idempotent receipt endpoint. No commit, release, deployment, public takeover dispatch or runtime
capability advertisement was added; CLI and Node repositories were unchanged this increment.

Additional coordinated recovery proof used real PostgreSQL `pg_dump -Fc`/`pg_restore` and complete
content `tar` archival into a second database and private directory. Complete task/object/tree/
reference/upload/quota fingerprints and both immutable disk receipts matched after restore. A pending
task with already-completed disk deletion converged without double quota deduction. An older completed
task, including a direct late disk replay, preserved the same-digest content uploaded afterwards, and
another retained file remained readable. Evidence: `/tmp/skill-content-gc-restore.log`, script
`/tmp/verify_skill_gc_restore.py`, source migration `/tmp/skill-content-gc-restore-migration.log`.
Its fixture directories, database container and anonymous volume were removed. This proves this
specific deletion recovery protocol, not complete Node/runtime or all-history restore acceptance.


Final complete Server gate: **1240 passed, 33 skipped, 81.48% coverage**; Ruff format/lint,
Mypy (**440 files**), Chinese docstrings and whitespace checks all passed:
`/tmp/skill-content-gc-server-quality-final.log`. This includes all 31 new non-PostgreSQL-only cases,
the three new real-connection cases as optional skips, the actual 0043 head and explicit task-table/
index registry checks. All three new skipped cases passed in the 76-case PostgreSQL run. Root and
Server final whitespace checks passed. No live test process, temporary database container or
anonymous fixture volume remains; the explicit recovery fixture directories were removed.
The full goal remains active.

### Read-only compaction/content forecasts and exact atomic composition (2026-09-23)

Directory compaction now accepts exact selections beyond its former independent 1000-item limit,
using the complete retention index's one-million identity safety budget. Protected views share that
budget and full manifest entries retain their separate one-million bound. Selection membership and
preserved roots are indexed once; no partial batches are committed. The >1000 test is a bounded
correctness proof, not a production capacity claim.

`SkillDirectoryCompactionService.reclamation_preview` combines full compaction projection, complete
reverse history dependencies, projected real tree FKs and shared quota/object/upload rules without
mutating ORM or persistence. Replacement checkpoints protect existing same-digest trees, and new
complete-tree/object edges prevent shared objects from being falsely counted as released. Only
state trees whose real historical FKs are removed by this exact selection are considered. Other
categories, accounts and unrelated unbound uploads are not implicitly selected. Trees with remaining
history references or waiting retain their diagnostics and may yield zero release.

`apply_reclamation` re-creates the complete preview at its original analysis timestamp under the
user lock, then compacts, retires the whole history selection and registers actual reclamation in
one outer retention savepoint. Real content actions must match the forecast's exact trees, objects,
edges, leases and release amounts. Only forecast release timestamps can differ from actual events;
original clock facts were already revalidated. Blocked ordinary history refuses the entire operation.
No public operation receipts or retry authorization are implied by this internal API.

Tests explicitly preserve original uploaded inputs that share a tree with a retired published head:
retirement can legitimately release zero bytes until those inputs are also explicitly selected.
Full user business-table fingerprints and empty ORM mutation sets verify read-only forecast commits.
Additional cases prove replacement file preservation, zero-reservation/cross-category leases,
last-task-flush failure rollback, new pin/upload/consumer invalidation, invalid analysis timestamps,
and >1000 exact identities with complete rollback and successful atomic application.

Focused related regressions: **35 passed**. Independent PostgreSQL 17, migrated through 0043:
**48 passed**, including four real row-lock races against committed/rolled-back pins and zero-reservation
uploads. Logs: `/tmp/skill-prune-projection-postgres.log` and
`/tmp/skill-prune-projection-migration.log`. No schema change was needed.

Public prune still needs account/item candidate selection, full dependency groups and compaction-only
actions that start ordinary waiting, stable cutoff and compact digest-bound confirmation, and durable
original-key/operation-ID recovery. Public usage/deadline/deletion diagnostics and all earlier pending
CLI/Node/runtime/backend/distribution groups remain. No commit, release, deployment, public takeover
dispatch or runtime capability advertisement was added. The full goal remains active.

Final complete Server gate: **1252 passed, 37 skipped, 81.55% coverage**. Ruff format/lint,
Mypy (**445 files**), Chinese docstrings and whitespace passed:
`/tmp/skill-prune-projection-server-quality.log`. All twelve new default-environment cases and four
PostgreSQL-only cases were included; the latter four passed separately in the 48-case PostgreSQL run.
The temporary database container and anonymous volume were removed. No test processes remain.
Root and Server whitespace checks passed. The complete Skill Manager goal remains unfinished.

### Account/item prune candidates and lifecycle-bound deferred cleanup (2026-09-23)

The internal `SkillPruneService.preview/apply` now resolves `SkillStateSelector` to a canonical
user/account/stable-source scope and fixes the original analysis cutoff. Account scope includes
state history throughout the account; item scope includes the source's branches across versions and
installation epochs plus associated migrations. Complete reverse consumers remain visible even when
created after the cutoff. Original versions are never implicit state-retirement targets.

Candidate planning first computes complete directory compaction, then propagates direct blockers
from retained consumers to their inputs. Cycles remain whole, while independent consumers of an
unselected shared input remain independent. The plan explicitly records the complete diagnostic
graph, executable roots/groups, compaction actions, projected clocks and exact content amounts.
Apply re-creates and compares that entire plan before mutation; it never skips groups on failure.
Ordinary mode can execute explicitly previewed compaction to start waiting while retaining blocked
history groups. Eligible independent groups still execute as part of the original preview. The
same outer savepoint covers heads, whole-group retirement, deferred cleanup claims and quota/tasks.

Migration `0044_skill_prune_claims` adds `skill_prune_content_claims`. A unique random claim UUID
binds the original user/account/source scope to an actual state tree or object row. Composite
owner/category FKs and explicit content `ON DELETE CASCADE` remove only the derived cleanup authority
when its original row is deleted. Same-digest reuploads do not inherit it. Claims are not protection
roots or retained-history obligations, are included in the complete retention-index budget, and
are created only in real retirement transactions. Read-only previews never create them. Duplicate
registration retains the original UUID/time. Upgrade adds an empty table; it never guesses lineage
from tombstone digests or wall-clock timestamps. Nonempty claims block downgrade before mutation.

Claims let later account/source prune finish cleanup after tree waiting or zero-reservation upload
leases end, including state objects whose tree was already removed. Another category, live lease,
retained tree/history or active protection still prevents improper release. Deleting objects stay
with their original worker and are not deducted twice. Single-item scope cannot inherit claims
created by an account-directory request; account scope may finish its own source-specific claims.
Legacy already-retired content without claims still requires future explicit storage-cleanup
authorization, not guessed account ownership. Root backup guidance now includes these rows.

New tests cover read-only full SQL/ORM fingerprints, both scopes, complete groups, ordinary compaction
and later retirement, waiting-tree continuation, independent blocked/local-original groups, late
consumers outside the cutoff, >1000 identities, owner/cutoff checks, last-task-flush rollback,
zero-reservation object continuation, claim constraints/identity preservation and same-digest
unbound reuploads. PostgreSQL 17 migrated through 0044: **55 passed**, including four new real
candidate/pin/upload lock races, all previous exact-composition races, GC and tree-retention
regressions. Log: `/tmp/skill-prune-candidates-postgres-final.log`; schema upgrade:
`/tmp/skill-prune-candidates-migration.log`.

A separate PostgreSQL fixture verified complete existing SQL fingerprints across 0043→0044 and
empty downgrade/upgrade, no guessed backfill, both actual cascade FKs, and nonempty downgrade refusal
with unchanged schema version/data. Script: `/tmp/verify_skill_prune_claim_migration.py`; log:
`/tmp/skill-prune-claims-migration-roundtrip.log`. The temporary PostgreSQL container and anonymous
volume, plus the temporary content fixture directory, were removed.

Public prune routes/CLI still require compact digest-bound confirmation, complete paginated loss
disclosure and durable original-key/operation-ID receipts that are queried before expired inputs.
Public retention/usage/deletion-progress diagnostics, Node-only export, takeover/runtime integration,
real Native/Docker acceptance and the remaining distribution/recovery groups remain. No commit,
release, deployment, public takeover dispatch or runtime capability advertisement was added.
The full Skill Manager goal remains active and incomplete.

Final complete Server gate: **1268 passed, 41 skipped, 81.77% coverage**; Ruff format/lint,
Mypy (**459 files**), Chinese docstrings and whitespace all passed:
`/tmp/skill-prune-candidates-server-quality.log`. This includes all sixteen new default-environment
cases, four new PostgreSQL-only races, the actual unique 0044 migration head and explicit claims
table/index inventories. All four new skipped races passed in the 55-case PostgreSQL run. No test
process or temporary database container/volume remains. Root and Server whitespace checks passed.
The complete goal remains unfinished; the next public-prune work is confirmation/receipt/API/CLI
integration on top of this now implemented internal account/source candidate and execution layer.

## Increment: public prune preview, confirmation and durable receipts

The Server now exposes the additive authenticated `/skills/state/prune` protocol described in
Server `docs/skill-prune-api.md` and the root wire contract. This completes the Server confirmation
and receipt layer; it does not complete the CLI prune workflow or the overall Skill Manager goal.

`services/skills/prune_commands/` separates streaming canonical plan hashing, complete disclosure,
signed page/confirm envelopes, read-only preview, command acceptance and content-independent queries.
Every page rebuilds the original cutoff plan and compares its full digest. All candidates and
complete dependency edges, selected groups, blockers, deadlines, compactions and removed/blocked
members are paged in bounded rows. Only the final page issues an execution credential. The command
contains only its original key and confirmation, including when more than 1000 histories are lost.

The command acquires the existing user storage lock and checks its original key/request before
signature verification, retention graph loading or file access. Accepted replay therefore survives
original physical deletion, an inaccessible content path and signing-key rotation. Conflicting input
under that key fails rather than replanning. For a new request, the complete confirmed plan is rebuilt
and compared before the internal prune applies. The outer retention savepoint includes all heads,
history retirement, claims, logical quota settlement, deletion tasks, receipt and complete details.
A failure after the last detail/task-link flush rolls all business changes back even when the caller
catches the exception and commits; only the existing storage lock counter/timestamp can advance.

Migration `0045_skill_prune_operations` adds three empty tables: immutable operations, ordinal
entries and original deletion-task links. Composite FKs bind account ownership and both child
relationships; the existing task table gains `(user_id,id)` uniqueness. No original signed credential
is stored, and terminal receipt metadata does not become a content root. Receipt entries retain all
original rows and add actual replacement IDs. Current pending/completed/retrying task counts and
physical bytes are queried separately, without changing original status `accepted`.

Verification includes full read-only SQL fingerprints, complete paged disclosure, >1000-history
confirmation/receipt recovery, signature tampering/stage/user checks, late pin/upload/consumer
invalidation, API feature and authority gates, exact replay after deletion/key rotation, conflicting
keys, whole-transaction fault rollback, owner FKs and independent physical retry progress. The focused
public suite passed **14 tests**; the additional persistence/retry test passed separately. PostgreSQL
17 migrated through 0045 passed **24 tests**, including six new same-key/confirmation lock races and
four existing candidate lock races. The additional ownership/retry test also passed on PostgreSQL.
Logs: `/tmp/skill-prune-public-focused.log`, `/tmp/skill-prune-public-persistence.log`,
`/tmp/skill-prune-public-postgres.log`, `/tmp/skill-prune-public-persistence-postgres.log`.

A separate actual 0044→0045 migration fixture preserved every old SQL row, including an existing
completed deletion task, and created no guessed receipts. Empty downgrade/upgrade removed/recreated
only the new tables and auxiliary constraint, preserving old rows. A real accepted prune then blocked
downgrade before any schema/version/data change, retaining every original disclosure row. All four
actual non-cascading owner FKs were inspected. Evidence:
`/tmp/verify_skill_prune_public_migration.py`, `/tmp/skill-prune-public-migration-roundtrip.log` and
`/tmp/skill-prune-public-migration.log`. The temporary PostgreSQL container and its anonymous volume,
plus the isolated content fixture, have been removed.

Full Server quality gate passed: **1282 passed, 47 skipped, 82.07% coverage**, recorded in
`/tmp/skill-prune-public-server-quality.log`. Format/lint, Mypy, Chinese docstrings and whitespace
passed. Latest static checks including the additional persistence test cover **476 Mypy files**.
The additional persistence test was added while the full regression was already running and was
verified separately on SQLite and PostgreSQL; no production code changed during that full run.

Next: CLI typed API validation, `skill state prune` selection/flags, complete paged loss display and
one final confirmation, compact original-request journaling, unknown-acceptance recovery, and generic
status/`--last` routing. `update --all` must skip validated prune journals. The CLI's 1 MiB response and
4 MiB exact-request limits remain unchanged; large plans must never be stored inline. No CLI files
were changed by this increment. Public usage/deadline diagnostics, Node-only export, takeover/runtime
integration, actual Native/Docker acceptance and broader distribution/recovery audits remain.
No commit, release, deployment, public takeover dispatch or runtime capability advertisement was added.
The full goal remains active and incomplete.


## Increment: complete CLI prune review and original receipt recovery

The CLI now implements `skill state prune` with explicit item/account-directory selection,
`--all-unreferenced`, dry-run, complete display and one confirmation. Typed prune API modules keep
ordinary HTTP response limits at 1 MiB. Every page must preserve the canonical summary/total and
contiguous offsets, terminal credential rules, history order and complete loss/group/compaction
counts. Large disclosures are privately spooled up to 2 GiB and streamed row by row; they never enter
the 4 MiB journal or become one unbounded heap vector. Any incomplete or oversized review fails
before journaling or submission. Human review is printed even under `--yes`; the confirmation
credential is never printed.

The `state_prune` journal retains the exact small command, original supplied intent, canonical
summary/count and original key. Recovery queries that key before any fresh preview; only definite
`OPERATION_NOT_FOUND` permits identical replay. Authentication/protocol uncertainty and mismatched
receipts keep the original pending record. A pending dry-run only queries acceptance; if unknown,
it explicitly reports the saved summary without claiming complete reconstructed disclosure.
`update --all` skips validated pending prune commands without querying or changing their receipt.

Generic status by ID and `--last` validate and return the immutable original receipt, all persisted
rows and separate current physical deletion progress. Logical `accepted` remains terminal while
physical work is pending/retrying. Progress byte totals are checked against original acceptance.
Status waiting bounds the entire read and display without submitting anything. Ctrl-C before
submission sends no command; during acceptance it preserves the pending key and unknown commitment.
A detached output-only worker cannot acquire submission authority. During streamed output,
interruption/deadline returns an exit code without competing for a blocked output lock or appending
another JSON envelope. Actual subprocess tests keep pipes deliberately unread to verify this behavior.

English/Chinese CLI READMEs, CLI architecture/local-state rules and the root wire contract document
selection, early cleanup, JSON shapes, scoped confirmation metadata, receipt recovery, output limits,
row ordering, interruption and the logical/physical distinction.

Verification:

- Full CLI gate passed: **490 tests, zero failures/ignored**, plus shell syntax, formatting, Clippy
  with denied warnings, Ruby/cache checks and whitespace. `/tmp/skill-prune-cli-quality.log`.
- Final prune contract suite: **14 passed**, including two tests added after the full gate started
  (pending-prune batch isolation and oversized/incomplete disclosure). Interruption suite: **2 passed**,
  covering blocked JSON/human pipes, status deadline, HTTP preview and acceptance SIGINT. Logs:
  `/tmp/skill-prune-cli-contract-final.log`, `/tmp/skill-prune-cli-contract-expanded.log`.
- Final static checks passed after those test additions and documentation updates:
  `/tmp/skill-prune-cli-static-final.log`. No production code changed after the full gate started.
- Real CLI subprocesses used actual authenticated Server routes, isolated SQLite and private content
  storage. Item scope traversed **247 rows / 116 history losses**, directory scope **249 rows / 118
  losses**. Both completed dry-run, confirmed submission, original-ID and `--last` status. Actual
  persisted deletion tasks were processed; subsequent CLI status retained the identical receipt and
  showed **10 deleted bytes / 1 completed task / no pending bytes** for each scope. Script:
  `/tmp/verify_skill_prune_cli_live.py`; evidence: `/tmp/skill-prune-cli-live.log`. Fixture databases,
  content, credentials and HTTP listeners were removed on completion.

This verifies the CLI/HTTP/SQL/physical-deletion protocol, not Native Claude or Docker Sandbox runtime
acceptance. The full goal remains active: public usage/deadline diagnostics, Node-only pending export,
full effective system/session/account diagnostics, ended-operation retry/interruption audit, durable
mixed-backend writer proof and takeover dispatch, runtime transfer/mount/finalization integration,
actual backend acceptance and full distribution/upgrade/restore/completion audits remain. No commits,
releases, deployments, public takeover dispatch or runtime capability advertisement were added.


## Increment: current Server storage and exact history diagnostics

Server `GET /api/v1/skills/storage` now exposes current owner-wide logical package/state usage,
separate upload reservations, actual configured limits/retention policy and independent physical
pending/retrying/completed task aggregates. Completed deletion bytes sum recorded task sizes across
content lifecycles; they do not imply free disk space or measure reclaimed filesystem capacity.
Node/session-copy storage remains explicitly `not_observed`.

Skill library/local-source details add per-revision retention observations and user-wide storage;
checkpoint details add the same current diagnostics for their exact checkpoint identity. The service
uses the existing complete protection graph and original release clocks, distinguishing protected,
waiting, due, release_unknown and retired. Protected/retired histories have no effective deadline;
missing release evidence stays unknown. Due is not authorization to retire dependencies or delete
files. New-user queries create no rows, reads do not write clocks/heads/lock versions, and no original
operation receipt is changed. Dedicated SQL aggregates avoid loading every physical deletion task.
The schema head stays 0045.

CLI `skill status --storage` is a separate, cancellable, read-only query without a command journal;
operation ID, --last, --wait and explicit --timeout are mutually exclusive with it. Info and state-info
render the additive diagnostics. Typed validation binds each history to its exact kind/id/retained
state and configured retention period, rejects inconsistent protection/deletion fields, and accepts
real over-quota usage after administrators reduce limits. Older detail responses lacking optional
fields remain supported without inventing zero usage or unlimited retention. The ordinary 1 MiB
metadata response cap is unchanged.

Architecture/persistence rules and `Server/docs/skill-storage-diagnostics.md` were written before
behavior changes. Both CLI READMEs and the root wire contract document the public shapes, scopes,
missing-field compatibility and retention/deletion semantics.

Verification:

- Server full gate: **1293 passed, 47 skipped, 82.12% coverage**, with formatting/lint, Mypy,
  Chinese docstrings and whitespace passed. `/tmp/skill-diagnostics-server-quality.log`. The
  additional PostgreSQL reservation race was added after full-suite collection and passed separately;
  final static checks include it. No production code changed during the full run.
- Server focused suite: **23 passed**, covering read-only/owner isolation, custom policy, real
  upload reservations, waiting/unknown/due/protected/retired histories, archived retention,
  real two-category single-file deletion and retry, and existing checkpoint/local detail contracts.
  `/tmp/skill-diagnostics-server-final-focused.log`.
- PostgreSQL 17: **11 passed**, plus a separate **1 passed** independent-connection reservation race.
  The latter observes actual `pg_blocking_pids`: a concurrent upload waits behind the diagnostic's
  owner lock, and only the next observation sees its reservation. Logs:
  `/tmp/skill-diagnostics-postgres.log`, `/tmp/skill-diagnostics-postgres-race.log`. The temporary
  PostgreSQL container and its anonymous volume were removed.
- CLI full gate: **497 passed**, zero failures/ignored, with formatting, denied-warning Clippy,
  shell/Ruby/cache checks and whitespace. `/tmp/skill-diagnostics-cli-quality.log`.
  One additional Ctrl-C test was added after the full gate began; the final focused suite passed
  **6 tests**, and the final static gate passed. `/tmp/skill-diagnostics-cli-contract-final.log`,
  `/tmp/skill-diagnostics-cli-static-final.log`. No production code changed during the full gate.
- Actual CLI subprocesses against authenticated Server/SQLite/private-content fixtures verified
  `status --storage`, library and checkpoint detail diagnostics before/after real prune and worker
  completion in both item and account-directory scopes. Logical state quota decreased, pending
  physical bytes reached zero, cumulative deletion reported 10 bytes, and retired checkpoint info
  remained available. Script: `/tmp/verify_skill_diagnostics_cli_live.py`; evidence:
  `/tmp/skill-diagnostics-cli-live.log`. Temporary data, credentials and HTTP listeners were removed.
- Final Server static checks: **480 Mypy files**, formatting/lint, Chinese docstrings and whitespace
  passed. `/tmp/skill-diagnostics-static-final.log`.

The full goal stays active. Effective system/session/account diagnostics, Node-only pending export,
ended-operation retry/interruption audit, durable mixed-backend writer proof and takeover dispatch,
managed materialization/mount/finalization transfer, actual Native Claude/Docker Sandbox acceptance,
and full distribution/upgrade/restore/requirement audits remain. No public takeover dispatch,
runtime capability advertisement, commits, releases or deployments were added.

## Increment: effective account and original session queries

Server adds system catalog rows to explicit ordinary lists and all effective queries. Account list
and info expose exact selected branch/head/epoch, directory mode/head/epoch, version selection reason,
preparation/expiry, separate publication/migration conflict counts and latest IDs, and recorded sync
evidence. Disabled sources retain honest branch diagnostics. Reads never substitute another revision's
head or invoke preparation, takeover, reservation or dispatch. Conflict counts span the source's
versions/epochs and are not claims that every historical conflict blocks the next start.

`GET /api/v1/skills/sessions/{session_id}` returns bounded original snapshot members and saved system
references. Original names, revisions, installation/state epochs, starting checkpoints and field
origins survive rule changes, current branch epoch changes, session deletion and content retirement.
Current retention is reported separately. Owned live sessions without snapshots return explicit
`legacy_unrecorded`; unknown/foreign sessions fail. Pagination uses explicit byte collation for both
ordering and cursor comparison, independent of PostgreSQL locale. Cursors must be original members.
Project discovery remains not_inspected; no query claims model loading or Node deployment readiness.

Migration `0046_skill_sync_time` adds nullable `SkillFinalization.persisted_at`, set exactly once when
complete content and the incoming checkpoint persist in the same transaction. Failed completion and
rollback leave it unknown; replay, publication and retirement preserve it. Legacy rows stay NULL,
never reconstructed from mutable updated_at. Downgrade refuses recorded timestamps before mutation.
Current diagnostics distinguish latest known sync time from historical persisted rows lacking times.

CLI adds `list --session ID --effective`, session-only --limit/--cursor, --include-system and optional
account-state display. Typed validation binds session/account identities, exact saved revisions,
ordered members, continuation and system origins before output. Missing older ordinary diagnostics
remain absent. No query journal is created. Both READMEs, Server architecture/persistence notes,
the wire contract and coordinated backup requirements document these behaviors.

A full CLI run exposed a pre-existing oversize-response test race: the bounded client correctly
rejected Content-Length, but the test server unconditionally required its oversized body write to
succeed. The fixture now permits only BrokenPipe/ConnectionReset when the body exceeds the metadata
limit; command rejection and absence of a mutation journal remain asserted. The focused regression
passed. This changes test infrastructure only.

Verification:

- Final Server full gate: **1308 passed, 48 optional integration tests skipped, 82.18% coverage**,
  including all 15 new effective-query cases. Formatting/lint, Mypy (**485 files**), Chinese
  docstrings and whitespace passed. `/tmp/skill-effective-server-quality.log`. The migration graph
  assertion now expects 0046; the focused persistence suite also passed **17 cases** in
  `/tmp/skill-effective-persistence-final.log`. The final full run includes the exclusive downgrade
  lock and the corrected head assertion.
- Final CLI full gate: **504 passed, zero failures/ignored**, including six new effective-query
  contract cases and the oversize-response fixture regression. Formatting, denied-warning Clippy,
  shell/Ruby/cache checks and whitespace passed. `/tmp/skill-effective-cli-quality.log`.
  Focused evidence: `/tmp/skill-effective-cli-focused.log`,
  `/tmp/skill-effective-cli-prune-regression.log`.
- Related API/finalization/local-management focused regressions passed **33 cases** before later
  expansion; all final tests are included in the full gate above.
- Final PostgreSQL 17 effective-query suite: **15 passed**, including real publication/migration
  conflicts, local/library pagination, locale-independent byte ordering, authorization, read-only
  queries, original deleted/retired snapshot identity and one-time sync evidence.
  `/tmp/skill-effective-postgres.log`.
- Actual 0045→0046 upgrade, empty-time downgrade/upgrade and legacy persisted-row roundtrip preserved
  complete existing SQL fingerprints. A timestamp from genuine completed content blocks downgrade
  before schema/data/version changes; the pending/timestamp constraint rejects inconsistent state.
  Independent PostgreSQL connections additionally verify that a concurrent writer blocks downgrade
  at the exclusive table lock, and its newly committed timestamp is then observed and preserved.
  `/tmp/verify_skill_sync_migration.py`, `/tmp/skill-effective-migration.log`.
- Actual CLI subprocesses against authenticated Server/SQLite/private content verified systems,
  account state, local/library pagination, recorded content sync, and unchanged original selection
  after rule change and session deletion. No command journal was created.
  `/tmp/verify_skill_effective_cli_live.py`, `/tmp/skill-effective-cli-live.log`.
- Temporary PostgreSQL container/volume and live HTTP fixture data/credentials/listener were removed.

The full goal remains active. Node-only pending export, ended-operation retry/interruption audit,
durable mixed-backend writer proof and takeover dispatch, managed materialization/mount/finalization
transfer, actual Native Claude/Docker Sandbox acceptance, and full distribution/upgrade/restore and
requirement audits remain. No public takeover dispatch, runtime capability advertisement, commits,
releases or deployments were added.

Read-only follow-up audit (not implemented by this increment): `skill_commands/mutations.rs::confirm`
still reads unbounded stdin synchronously, and `install_source.rs::choose` can block a Tokio blocking
worker on interactive selection. `install_source::bounded_git` registers Ctrl-C handling, while later
legacy add confirmation and package upload do not share a cancellation boundary. These paths require
real interrupted subprocess/PTY tests and a scoped fix; existing source/acceptance/wait coverage is
not proof that the gaps are closed. Server library operations currently store `retryable=false` and
bound-node targets as unsupported, with no durable retryable deployment-attempt workflow; CLI has no
`skill retry` command. Implementing a superficial replay of the original library mutation would not
satisfy ended-operation retry or preserve successful targets. That work remains tied to immutable
plans and the actual runtime deployment/dispatch state machine.

## Increment: configuration preparation, interactive input and interruption

CLI add and rule/remove/rollback now separate preparation from exact-request acceptance. User login,
Server identity/recovery lookup, source acquisition/selection, review and content uploads run within a
cancellable preparation phase without configuration POST or mutation-journal authority. A prepared
submission hands its original request to the existing acceptance/recovery implementation. Large
preparation futures are boxed to avoid debug-build stack overflow; actual subprocess tests exercise
this boundary.

One task-scoped Ctrl-C listener is registered before configuration work and retains the event through
phase transitions, SQLite journal writes, acceptance and waiting. Cancellation wins before polling a
POST. Uncertain acceptance preserves the original key and unknown commitment; interruption after a
verified response preserves known commitment. Existing nonconfiguration command scopes are unchanged.
Updates now include cancellable authentication and share the bounded confirmation reader.

Interactive source selection and confirmation use detached input/output-only threads (8192/4096 input
bytes respectively). They cannot upload, journal or submit. Source warnings, source catalog results
and configuration dry-run results no longer block the async command's cancellation path. Result output
is explicitly marked before a display worker starts, so interruption does not append another JSON
envelope or contend for its blocked stdout. Output may be partial. Human configuration/update
cancellation exits 130 without another terminal message; JSON retains the appropriate result when
result streaming has not begun. SOURCE_INTERRUPTED compatibility remains intact for preparation;
uncertain submission continues to use SKILL_INTERRUPTED. Server uploads can remain staged/stored and
older journaled operations remain queryable; no remote cancellation or rollback is implied.

Verification:

- **Full CLI quality gate passed: 513 tests, 0 failed, 0 ignored**, with formatting, denied-warning
  Clippy, shell syntax, release/cache contracts and whitespace checks.
  `/tmp/skill-interruption-cli-quality.log`.
- **9 new subprocess contract tests passed**, including multi-stage authenticated read interruption,
  real PTY source selection and add/rule/update confirmation in JSON and human modes, ordinary yes/no,
  oversized input refusal, each package upload phase, SQLite journal-lock transition, uncertain POST
  identity, blocked source warnings and unread JSON/human source-catalog pipes.
  `/tmp/skill-interruption-final-focused.log`.
- **82 related contract tests passed** for install, rules, updates, state mutations, resolution,
  migration and prune interruption during development. Git's **10 cases** also passed, including the
  existing interrupted credential-helper behavior. `/tmp/skill-interruption-regressions.log`,
  `/tmp/skill-interruption-expanded.log`.
- Actual CLI → authenticated Server/SQLite/private-content verification paused responses only after
  real transactions committed. Interrupted package completion retained the uploaded package but
  created no installation or journal. Interrupted installation acceptance retained a pending original
  key; recovery after deleting the local source returned the original committed receipt with exactly
  one installation POST and unchanged library generation. Script:
  `/tmp/verify_skill_configuration_interruption_live.py`; log:
  `/tmp/skill-configuration-interruption-live.log`. Temporary files, credentials, listeners and child
  processes were removed.

Both CLI READMEs, CLI architecture notes and the root wire contract describe these interruption
boundaries. This closes the specifically audited add/rule input/preparation/upload gaps; it is not a
claim that every remaining CLI/output/runtime interruption scenario has been audited. Ended-operation
retry still requires immutable deployment plans and per-target durable attempts; no superficial
library-mutation replay or unsupported runtime capability was added. Node-only pending export,
mixed-backend writer proof/takeover dispatch, managed runtime transfer/mount/finalization, real Native
Claude/Docker Sandbox acceptance and the full distribution/restore/completion audit remain. The full
goal remains active; no commits, releases or deployments were performed.

## Increment: interruptible final configuration and update output

Configuration acceptance and single/batch update results now render on owned output-only threads.
Verified receipt persistence still precedes rendering. A retained Ctrl-C bounds final output to a
250 ms drain allowance before exit 130, including when the interruption diagnostic itself encounters
an unread pipe. Output can be partial; the command never appends a second envelope or gives a display
worker submission/journal authority. Read-only check output keeps its prior behavior.

Three additional subprocess contracts cover JSON and human accepted rule/update results blocked on
stdout/stderr, read-only batch update result streaming, and a large retained pending receipt emitted
after interruption during status polling. Accepted operations remain `received` in SQLite; a separate
`skill status --last` process retrieves the original committed operation without another POST.
The original nine configuration preparation/input/upload contracts remain part of the same suite.
Output cases live in `tests/skill_configuration_interruption/output.rs`, sharing the parent contract
fixture instead of duplicating subprocess/PTY/authentication helpers.

The actual CLI → authenticated Server interruption/recovery script passed again after the output
change: package completion remains stored without installation acceptance, while interrupted committed
installation acceptance recovers the original result after source deletion with one installation POST.
Evidence: `/tmp/skill-output-interruption-live.log`. Temporary data and listeners were removed.
Both CLI READMEs, architecture notes and the root wire contract document partial output and receipt
recovery. Final full CLI quality gate passed: **516 tests, 0 failed, 0 ignored**, formatting,
denied-warning Clippy, shell syntax, release/cache contracts and whitespace checks. The final gate
includes all **12 configuration interruption subprocess contracts** after splitting output cases.
Evidence: `/tmp/skill-output-interruption-cli-quality-final.log`.

Further read-only audit identified remaining synchronous output boundaries in state commands:
`state_mutations::run` calls `render::show_plan` before confirmation; `state_migrations::run` calls
`show`; `state_resolutions::plan` calls `preview::render`. These output calls execute inside their
async preparation futures. Their final result/dry-run renderers also remain synchronous. The retained
state Ctrl-C future and existing input tests do not prove those pipes are cancellable. This increment
does not change them; focused blocked-preview/result and late-receipt tests are still required.

Node-only pending export, ended-operation retry with immutable deployment plans and durable target
attempts, mixed-backend writer proof and takeover dispatch, managed runtime transfer/materialization/
mount/finalization, actual Native Claude and Docker Sandbox acceptance, coordinated distribution/
upgrade/restore and the full requirement audit remain outstanding. No runtime capability was
advertised; no commits, releases or deployments were performed. The full goal remains active.

## Increment: state mutation review, receipt persistence and output interruption

State reset/restore, migrate and resolve now use the retained command-scoped signal from entry through
preparation, exact journaling, acceptance, receipt persistence and final output. Their acceptance paths
check cancellation before polling an actual POST. A verified response is recorded even when Ctrl-C
arrives while SQLite receipt persistence is blocked; output exits 130 without downgrading commitment.
Unknown acceptance retains its original key and immutable request.

Shared `skill_commands/output.rs` now contains the owned output-only workers previously local to
configuration. State review workers hold only display metadata and use stderr, with no mutation
capability. JSON can report planning interruption before result streaming starts; human interruption
returns 130 without contending for a blocked review/prompt writer. Dry-run and final output use the
irreversible result-start marker and bounded 250 ms drain allowance. Existing resolution capture
cancellation and configuration behavior remain covered by their regression suites.

Direct evidence:

- **9 new subprocess contracts passed**, exercising reset and restore, explicit migration, publication
  resolution and migration resolution in JSON/human modes. They cover unread large interactive review,
  dry-run output, accepted receipt output, and Ctrl-C during an exclusive SQLite receipt-write lock.
  Preview interruption creates no journal or actual mutation; accepted receipts stay `received` with
  the original operation ID. Cases are in `tests/skill_state_output/`, with shared subprocess/PTY/lock
  helpers under `tests/support/skill_output.rs`. `/tmp/skill-state-output-focused-final.log`.
- The pre-existing configuration/state mutation/migration/resolution contracts passed after the
  production changes. `/tmp/skill-state-output-regressions.log`.
- Actual authenticated CLI → Server/SQLite/private-content verification published **1000 learned
  paths** first. Interrupting blocked reset review created no journal or actual command and left heads
  and epochs unchanged. Interrupting blocked JSON after actual reset publication retained the original
  committed operation; `status --last` recovered it, with one actual POST and exactly one state-epoch
  advance. `/tmp/verify_skill_state_output_live.py`, `/tmp/skill-state-output-live.log`.
  Temporary content, credentials, processes and listeners were removed.

Both CLI READMEs, architecture notes and the root wire contract document the behavior. Full CLI quality
gate passed: **525 tests, 0 failed, 0 ignored**, formatting, denied-warning Clippy, shell syntax,
release/cache contracts and whitespace checks. `/tmp/skill-state-output-cli-quality.log`.
This closes the previously recorded state mutation review/final-output gaps; state queries/export, status and other output paths still need
completion-audit coverage. Node-only pending export, immutable deployment retry plans and durable
attempts, mixed-backend writer proof/takeover dispatch, managed transfer/materialization/mounts/
finalization, actual Native Claude and Docker Sandbox acceptance, and coordinated distribution/
upgrade/restore plus the full requirement audit remain outstanding. No capability advertisement,
commits, releases or deployments were added. The full goal remains active.

## Increment: supervised backend-migration backup copy evidence

Node `Engine.migrateAccount` now replaces its unsupervised direct `cp` child with a Helper-selected
systemd copy service. Before launch, `internal/skillmanager/account_copy_linux.go` fsyncs a private
no-replace intent bound to exact Node/user/account/logical task, source/target/path digest, boot ID
and deterministic service name. The service uses fixed `/bin/cp` arguments, whole-cgroup kill policy,
no restart, a ten-minute runtime limit, bounded stop time, disabled core dumps and discarded output.
The Helper separately checks terminal unit state and the entire cgroup before advancing copy evidence.
Cancellation, ambiguous launch, a live/uninspectable group or changed boot keeps `started`.

This is explicitly **copy-phase evidence**, not complete migration success, power-loss verification
of backup contents, ownership/ACL subprocess termination, rollback or takeover permission. An existing
copy record cannot restart later ownership work or re-copy a changed source. Same-task Helper replay
requires recovery (`STATE_COPY_PENDING`/`STATE_COPY_FAILED`); existing worker terminal-ledger replay
is unchanged. Helper and worker preserve these stable codes without raw command diagnostics.
Source and partial backups are retained.

Takeover also scans private local copy records, including records omitted from Server inventory.
Matching copy-only history and malformed/aliased/foreign-node metadata fail closed. Other verified
account identities are not mistaken for the selected account. Historical backend migrations without
receipts still fail `STATE_WRITERS_UNKNOWN`. The existing internal Native takeover path remains
unexposed; no task dispatch or capability advertisement was added.

Evidence:

- Linux receipt tests cover reopen durability, no-replace intent, immutable input and outcome,
  cross-boot refusal, damaged JSON, link/mode/identity/unit/task corruption, and account-scoped local
  copy history denial. Helper tests cover recorded-before-launch intent, successful/failed/unknown/
  active/populated/cancelled copy observations, no replay and continued takeover denial with or without
  Server inventory. Existing Linux fence/capture/import/descriptor contracts also passed.
  `/tmp/skill-copy-linux-final.log`.
- Actual isolated systemd copied real content, executable mode and relative links, verified cgroup
  exit and retained the copy receipt. A deliberately delayed synthetic service survived cancellation
  of its systemd client; the receipt remained started, and later natural service exit did not permit
  replay. Both copy cases, the prior real descendant takeover check, and all six Native lifecycle
  cases passed. `/tmp/skill-copy-systemd-verified.log`. The synthetic wrapper lives on executable
  container storage because the test container's `/tmp` mount is noexec. All disposable test containers,
  images and wrapper directories were removed.
- Full Node gate passed: formatting, shell syntax, generated policy, Go vet/tests, **60.3% host statement
  coverage**, installer/managed-skill/release contracts and whitespace. `/tmp/skill-copy-node-quality.log`.
  Linux-target vet also passed: `/tmp/skill-copy-linux-vet.log`. Host coverage does not claim coverage of
  the Linux-only implementation; the independent Linux and systemd evidence above covers that boundary.

Node READMEs, architecture/persistence rules and `docs/skill-account-capture.md` document the exact
boundary. Next runtime work must supervise ownership/ACL writers and establish durable whole-migration
recovery before relaxing backend-history denial, then prove Docker/sandbox and orphan writers. Safe
capture initiation/dispatch, Node-only pending export, immutable deployment retries, managed content
materialization/mount/finalization, actual Claude/Docker Sandbox acceptance and complete coordinated
upgrade/restore/distribution and requirement audits remain. The full goal stays active. No commits,
releases or deployments were performed.

## Increment: complete backend-migration writer evidence and terminal replay

Node now records a private whole-migration intent before backup creation. It binds the original
copy intent and the Helper-selected execution configuration. Target and rollback ownership walks
run synchronously under Helper serialization; every recursive/default/traversal ACL command runs
in its own bounded systemd service with independent launcher and whole-cgroup exit checks. Unknown
target writers forbid rollback. Unknown local migration history also blocks a replacement logical
task before creating another backup.

After account and backup filesystem sync, the same boot can persist immutable succeeded/failed
migration evidence. Exact terminal replay checks both the migration and its original completed copy,
returns the saved result and does not repeat copy or ownership, including after legacy admission is
fenced. A known failure certifies migration-writer termination, not successful restoration of source
permissions. `STATE_MIGRATION_PENDING` and `STATE_MIGRATION_FAILED` remain bounded Helper/worker
codes. Interrupted started records still require recovery; this increment does not implement
automatic crash continuation or authorize backup deletion.

Native takeover's backend inventory check now accepts only complete terminal migration evidence
with its original completed copy. The local scanner checks both record types even when Server
inventory omits them. Missing, old copy-only, corrupt, mismatched and aliased records still deny
capture. Session, Docker sandbox and orphan-writer checks remain independent; no public takeover
dispatch or capability advertisement was added.

Evidence:

- Linux receipt lifecycle/corruption cases and Helper replay/takeover cases passed. The latter cover
  succeeded, failed, started, missing, copy-only, missing-copy, corrupt and changed-input evidence,
  fence-closed replay and no account/backup mutation. Existing legacy fence, import, capture and
  descriptor suites also passed. `/tmp/skill-migration-linux-final.log`.
- Isolated real systemd tests passed for successful migration, known target/rollback ACL failure,
  and cancellation while an ACL writer survives its launcher. Replays retained the original backup;
  unresolved work blocked a replacement task. The suite additionally verifies supervised copy,
  descendant takeover and all six Native lifecycle cases. `/tmp/skill-migration-systemd-final.log`.
  These use synthetic tool/auth fixtures and are not real Claude or Docker Sandbox acceptance.
- Two test-environment defects were fixed: account data uses ACL-capable `/var/tmp`, and migration
  fixtures use a different real account from Native fixtures with fixed numeric IDs. A separately
  reproduced startup race reported `Failed to connect to bus: No such file or directory`: root
  systemctl's private socket became ready before systemd-run's system bus. The harness now waits
  for a successful system-bus query. Three fresh-container startup checks passed after that change
  (`/tmp/skill-copy-startup-fixed-{1,2,3}.log`); production uncertainty still fails closed.
- Full Node quality gate passed with **60.6% host statement coverage**, formatting, shell syntax,
  Go vet/tests, installer, managed-skill/release contracts and whitespace checks.
  `/tmp/skill-migration-node-quality.log`. Linux-target vet passed separately:
  `/tmp/skill-migration-linux-vet.log`. Host coverage does not cover Linux-only behavior.

Node READMEs, architecture/persistence/capture documentation and the root wire contract now describe
this narrower complete-terminal-evidence boundary. Started migration recovery, mixed Docker/native
and orphan writer proof, safe capture initiation/dispatch, Node-only pending export, immutable
operation retry plans and target attempts, managed transfer/materialization/mount/finalization,
actual Native Claude and Docker Sandbox acceptance, CLI query/status/output audit and coordinated
upgrade/restore/distribution plus the requirement audit remain outstanding. No commits, releases or
deployments were performed; the full goal remains active.

## Increment: state-query/export interruption through final output

CLI state list/info/diff/conflicts/export now retain the same task-scoped Ctrl-C listener as state
mutations. Preparation, success rendering and error rendering no longer lose the signal between
phases. Final display runs in owned output-only workers with the existing 250 ms cancellation drain
allowance; a blocked stdout/stderr cannot hold shutdown and no second JSON envelope is appended.
Already-started result errors also suppress fallback envelopes.

Read-only queries do not create a command journal or issue mutations. Export checks retained
cancellation before local publication. Once publication begins, the CLI observes its result; a
verified published bundle survives cancellation during final output. Before publication, staging
continues to be discarded. Node-only pending export remains a separate unimplemented path.

Three new subprocess tests prefill the inherited output pipe before launch. They cover successful
and failed query output in JSON/human modes, an interrupted query whose JSON interruption envelope
is itself blocked, and completed export output interrupted with exact manifest/object bytes and
no leftover staging or journal. Existing state contracts, including download interruption and
scope/content validation, pass with these tests: **18 passed** in the focused state suite.
`/tmp/skill-query-output-focused-final.log`. The full CLI quality gate passed with **528 tests,
0 failed, 0 ignored**, formatting, denied-warning Clippy, shell syntax, managed-tool cache/release
contracts and whitespace checks. It includes the final byte-preservation export case.
`/tmp/skill-query-output-cli-quality.log`.

Both CLI READMEs, architecture rules and root wire contract document this behavior. General skill
list/info/check/status and prune still require their separate remaining cancellation/output audit;
this increment does not claim those paths are covered. The broader runtime/distribution/recovery
work listed above remains, and the full implementation goal stays active.

## Increment: reject removed Docker Sandbox adapters and retain writer evidence

The previous turn was verified implementation progress. Current integration inspection found a real
runtime prerequisite failure: this environment's installed `docker sandbox` prints that the plugin
has been removed and exits zero. Ordinary Docker still operates. The prior Helper/installer probe
accepted the zero exit, so it could falsely report backend support; queued stop/cleanup could likewise
treat an inert sandbox rm as removal and discard the trusted runtime spec.

Node now positively checks each create/exec/rm command's usage with a shared ten-second Helper budget,
64 KiB output limit, process-group cancellation and bounded pipe drain. Installer checks each command
with a timeout and forced-kill grace. Empty/generic help, successful removal notices, missing commands,
failed help and oversized output are rejected. Binding/session starts recheck compatibility after
account fencing but before mutable runtime/account/workspace preparation. Stop/cleanup check before
killing tmux or removing the original spec; incompatible adapters return `CAPABILITY_UNAVAILABLE`.
The worker retains its existing privilege boundary and no new backend capability is enabled.

Evidence:

- Host tests cover positive per-command usage, removed/empty/generic help, absent exec/rm, nonzero
  status, oversized output, pre-cancellation and a stalled command with descendants. The actual
  installed removed plugin was tested through the same Helper probe and rejected.
  `/tmp/skill-docker-capability-final.log`.
- New start/stop/cleanup contracts verify unavailable adapters create no account/workspace/runtime
  state and preserve existing trusted spec bytes. The real Linux fence/import/capture suite includes
  these tests and passed. `/tmp/skill-docker-capability-linux-final.log`. Its old dependency probe now
  supplies an explicit test Git binary so the minimal container is not mistaken for a complete host.
- Installer contracts include six semantic help variants. Full Node quality gate passed with **60.9%
  host statement coverage**, formatting, vet/tests, shell syntax, installer, managed-skill/release and
  whitespace checks. `/tmp/skill-docker-capability-quality.log`. Final focused host tests and Linux
  vet also passed (`/tmp/skill-docker-capability-linux-vet.log`). Linux-only coverage remains separate.

Both Node READMEs, architecture/capture documentation and the root wire contract record this boundary.
Docker's current documentation exposes the separate standalone `sbx` interface; it cannot be silently
substituted for the configured legacy adapter. No compatible sandbox lifecycle exists in the current
runtime environment, so real Docker writer/orphan proof is still unverified. The broader goal is not
blocked: explicit adapter work, Native runtime integration and the other recorded requirements remain
available. No public takeover dispatch, managed capability, commit, release or deployment was added.
The full skill-manager objective remains active and incomplete.


## Increment: immutable original configuration plans and retry retention

Server schema `0047_skill_deployment_plans` now saves each original account's complete effective
library/local selection in the configuration acceptance transaction. Targets retain the original
account/node/tool/backend identities; entries retain exact revision/content identities, library
installation epochs, names and effective enabled values, including disabled sources and account
pins. Composite foreign keys bind entries to the owning operation, source, epoch and revision.
Historical target identities do not follow later account/node binding changes.

Canonical digests bind the operation, generation, target binding and sorted selection. Status and
idempotent replay verify the original inventory and digest without fetching upstream or parsing
current rules. Historical operations keep `plan_version=NULL` and are never backfilled from today's
configuration. The additive target `plan_digest` survives typed CLI JSON output, while missing
historical fields remain compatible.

Pending operations and retryable terminal failures retain every original plan revision, including
account pins absent from the mutation's selected-revision summary. Supersession releases these
references through the existing retention-clock transaction. Ordinary terminal plans remain audit
metadata and do not permanently protect old bytes. Unknown versions, missing targets, changed
bindings/digests and unavailable active dependencies fail retention analysis instead of authorizing
collection with an incomplete reference graph.

New tests cover separate-transaction replay after account/backend/epoch changes, exact disabled
account pin retention and release clocks, whole-savepoint rollback after the second target has
already been written, corrupt plan rejection, owner/source/epoch foreign keys, exact local account
references, and legacy no-plan behavior. SQLite final focused checks passed **25 tests, 1 optional
PostgreSQL test skipped** (`/tmp/skill-plans-sqlite-final.log`). The actual migrated PostgreSQL 17
suite passed **48 tests** including library/retention regressions
(`/tmp/skill-plans-postgres-verified.log`). Its fixtures now filter rollback counts by owner and
select an operation with actual targets, rather than relying on database row order.

Actual Alembic fresh upgrade, empty-plan downgrade/re-upgrade, and nonempty downgrade refusal were
verified in an isolated disposable database. Refusal preserved head 0047 and recorded plan rows.
New columns, primary keys and composite foreign keys matched the migrated PostgreSQL schema.
Logs: `/tmp/skill-plans-migration.log`, `/tmp/skill-plans-downgrade-empty.log`,
`/tmp/skill-plans-downgrade-protected.log`, `/tmp/skill-plans-schema-parity.log`. The temporary
PostgreSQL container has been removed. These checks do not claim full runtime backup/restore.

CLI full quality gate passed with **529 tests, 0 failed, 0 ignored**, formatting, denied-warning
Clippy, shell/cache/release and whitespace checks (`/tmp/skill-plans-cli-quality.log`). Final Server
full quality gate passed with **1321 tests, 48 optional integration tests skipped, 82.30% coverage**,
formatting/lint, Mypy (**492 files**), Chinese docstrings and whitespace checks
(`/tmp/skill-plans-quality-final.log`).

The stored plan is a configuration projection, not a managed runtime snapshot or a target-attempt
ledger. Durable target attempts, retry dispatch, replacement/conflict guards and the public
`skill retry` command still require implementation. Bound targets remain unsupported and no runtime
capability was enabled. The broader runtime transfer/materialization/mount/finalization,
Docker adapter and writer proof, started-migration recovery, Node-only export, remaining cancellation
work, real backend acceptance and complete design audit remain outstanding. The full goal stays
active; no commit, release or deployment was performed.

## Increment: authenticated snapshot downloads and explicit legacy startup rejection

Node now retrieves the original managed snapshot through the authenticated Server content routes,
binding every request to the snapshot and database task-record UUID plus Node/user/account/session/
backend identity. The client preserves int64 generations and epochs above JavaScript's exact integer
range, checks the canonical manifest digest and included member resolutions, and requires complete
canonical snapshot/member/resolution fields. Missing/null fixed values, case aliases, duplicate keys,
invalid versions, changed identities and nonready response envelopes fail before preparation.
Full snapshot responses allow 64 MiB; unrelated responses and error bodies retain 4 MiB limits.

Files stream through exact size/hash/text-classification verification. HTTP 200, octet-stream,
strong digest ETag and exact Content-Length are required; redirects, transformed content, partial
responses, truncation and extra bytes fail. Cancellation closes blocked network reads, and errors
expose only bounded stable Server codes. Callers must discard partial private staging on every
failure. System release references are preserved, but Helper verification of actual pinned artifacts
is still required; this client is not launch authorization or proof of materialization.

Integration inspection also found that the existing session decoder discarded unknown
`skill_manager` fields. Legacy decoding and both Helper start operations now reject any such marker
with `SKILL_MANAGER_UNSUPPORTED`, including null and case aliases. The Helper checks before reading
its legacy success cache, preserving the original receipt while refusing to reinterpret it as a
managed launch. Existing terminal worker ledger replay remains unchanged. Tests cover both backend
labels, rejection before any runtime directory creation, legacy cache isolation and content-free
worker error reporting. The dedicated managed startup handler remains to be implemented.

Verification:

- Final full Node quality gate passed: **61.3% host statement coverage**, formatting, vet, Go tests,
  shell syntax, installer, managed-skill/release and whitespace checks.
  `/tmp/skill-snapshot-node-quality-final.log`.
- Focused race tests passed across API, tool-session decoding, Helper and worker, including final
  strict JSON decoding and startup rejection. `/tmp/skill-snapshot-race-final.log`.
- Linux amd64 vet passed for all four changed Go packages. `/tmp/skill-snapshot-linux-vet.log`.
- Actual FastAPI/Uvicorn and Go HTTP integration passed with real Node-token authentication,
  SQLite foreign keys and private object storage. The logical task ID differed from its record UUID.
  Original manifest and file reads succeeded; expiring the task lease denied both routes and left
  the reserved snapshot/digest unchanged. Temporary credentials and fixture storage were removed.
  `/tmp/skill-snapshot-live-summary.log`, `/tmp/skill-snapshot-live-valid.log`, and
  `/tmp/skill-snapshot-live-revoked.log`. The optional Go contract uses
  `AGENT_REMOTE_TEST_SKILL_SNAPSHOT_FIXTURE`; ordinary tests skip it without an isolated fixture.

Node READMEs, architecture/control rules and the root wire contract record the exact boundary.
This increment does not add target attempts or `skill retry`, worker/Helper managed dispatch,
materialization/mount/start integration, pinned artifact verification, lease-aware runtime recovery,
finalization transfer/acknowledgement, Docker adapter/writer proof or real backend acceptance. Those
and the other previously recorded design requirements remain outstanding. The full goal stays active
and incomplete; no capability advertisement, commit, release or deployment was performed.

## Increment: authenticated content stream into atomic Helper preparation

Node now has a dedicated `prepare_skill_snapshot` Helper operation and typed client. It consumes
the original full snapshot only for an existing matching trusted Native session spec, then asks the
unprivileged caller for manifest file digests. The caller streams authenticated HTTP content without
passing Node credentials, arbitrary host paths or file contents in JSON. A per-object completion byte
is sent only after the downloader and client verifier accept all bytes. The Helper independently
checks content and materializes using its existing private-store, UID/GID, quota and atomic bundle
primitives. The result is a preparation receipt, not runtime readiness.

Snapshot validation and strict JSON schemas now live in `internal/skillmanager`, with API aliases
preserving callers and HTTP behavior. The stream input has an independent 64 MiB ceiling; ordinary
Helper requests keep existing limits. Fixed metadata is revalidated on both sides. The sealed binding
adds the task-record UUID and a complete preparation digest, including original checkpoint, member
resolutions and system references. Object key order is normalized and integers remain exact. Older
internal receipts remain readable but cannot be upgraded implicitly into a streamed preparation.
Identical replay leaves learned content intact; any changed original input conflicts.

Socket cancellation owns and closes the bounded input pipe and its reader goroutine, including
periods between object reads. A disconnected operation also stops waiting for the Helper mutation
lock. The entire transfer has a ten-minute ceiling. Failures before atomic publication discard
private staging; a complete bundle published before response loss remains available for exact replay.
The operation neither creates specs nor mounts or launches processes, and it does not renew Server
task leases. Full system-artifact verification still belongs in the future startup coordinator.

Verification:

- Actual rootful Linux HTTP-to-Unix-socket-to-filesystem tests passed. They use the real API client,
  Helper handler and materializer with a local authenticated HTTP fixture. They prove byte identity,
  private ownership, exact replay without download, preservation of simulated session learning,
  rejection of changed task/epoch/generation/checkpoint/system inputs, rejection of foreign owner/
  Node/backend/spec identities, and absence of partial bundles after cancellation, failed source
  completion and malicious wrong-hash content. A 17 MiB metadata case verifies the independent stream
  bound. `/tmp/skill-preparation-linux-final.log` also includes existing copy/finalization regression
  tests. Its optional real-systemd test remains skipped; this is not Claude runtime acceptance.
- Existing rootful Linux import/fence/capture-descriptor tests passed after the bounded frame reader
  change, including complete import payloads and original descriptor ACK contracts.
  `/tmp/skill-preparation-existing-protocols.log`.
- Final focused race tests passed for preparation, HTTP snapshot reads and takeover transport.
  `/tmp/skill-preparation-race-final.log`. Linux amd64 vet passed for API, Helper and skillmanager.
  `/tmp/skill-preparation-linux-vet.log`.
- Actual FastAPI/Uvicorn-to-Go snapshot and file reads passed again after the shared schema move;
  lease expiry still denied both routes. `/tmp/skill-preparation-server-wire.log`. This separate
  Server test does not claim a combined real Server/Helper/runtime end-to-end launch.
- Final full Node quality gate passed with **60.9% host statement coverage**, Go formatting/vet/tests,
  shell syntax, installer, managed-skill/release and whitespace checks. Linux-only coverage is
  separate. `/tmp/skill-preparation-node-quality-final.log`.

The Node READMEs, architecture/control/persistence rules and root wire contract describe the new
operation and recovery boundary. Worker managed admission, safe spec creation, fixed system artifact
verification, lease supervision, mount/start and ambiguous-launch recovery are still disconnected;
legacy managed markers continue to return `SKILL_MANAGER_UNSUPPORTED`. Durable target attempts,
deployment retry/API/CLI, finalization transfer/acknowledgement, Docker adapter and writer proof,
started migration recovery, Node-only export, remaining command audits, real backend acceptance and
the complete design audit remain outstanding. The full goal stays active and incomplete. No managed
capability, commit, release or deployment was added.

## Increment: fixed system releases and verified Native system overlays

Helper preparation now consumes the snapshot's actual system release selection before requesting
file content. Ego-browser requires exact canonical version, commit and tree digest fields matching
the reviewed embedded source. If the trusted spec enables its external wrapper, the existing artifact
verifier additionally checks current wrapper/Skill bytes, metadata and source provenance. Device
selection requires the exact trusted runtime protocol and the Helper binary's compiled Node release
(`config.DefaultVersion`, set by the existing release ldflags), not the worker's configurable version
label. Unknown names, absent/extra/case-aliased/null/duplicate fields and noninteger protocols fail.

Typed comparable system pins are sealed in the private snapshot binding and rechecked before every
Native mount, including mount replay. Old internal records without recorded pins remain readable for
stop/finalization/recovery, but cannot launch with today's artifacts; valid historical pins for a
different release likewise preserve the bundle and refuse a new mount. This avoids changing fixed
snapshot behavior after a binary upgrade. The preparation digest still binds the full original input.

Inspection found that Native managed overlays previously exposed the device skill even when the
snapshot had not selected a device protocol. Native now always overlays the selected ego-browser skill
and overlays agent-remote-device only when the trusted spec selects that capability. Both discovery
aliases receive the same readonly system selection. Legacy account installation behavior is unchanged.

The actual selected per-session system trees are checked before first mount and on mount replay:
all expected directories and files must be present, bytes must match the verified embedded sources,
modes must be readonly, and Linux ownership must be root. Extra files/directories, symlinks, hard links,
missing files and permission drift fail. Verification never repairs an already mounted tree. This
closes the gap where a valid release label could otherwise mask stale or extra per-session files.

Evidence:

- Strict metadata, exact device selection, Helper build drift, enabled external artifact byte drift,
  complete selected-tree verification and HTTP-to-Helper preparation regressions passed on host and
  actual rootful Linux. New Linux recovery cases prove missing/historical pins refuse mount before
  changing mount state while finalization still succeeds. `/tmp/skill-system-pins-host-final.log`
  and `/tmp/skill-system-pins-linux-final.log`. The previous large unknown-reference fixture now
  correctly fails system selection; valid known references still prepare and replay.
- Real Bubblewrap mount tests passed as non-root UID 12345: unselected device skills are absent;
  selected device files are readonly through both aliases; ego-browser and ordinary writable skill
  behavior remain correct. Added mount replay rejects an extra system file without repairing it.
  Busy-mount preservation still passes. `/tmp/skill-system-pins-mount-final.log`.
- The actual runtime binary passed all six isolated systemd lifecycle cases: normal/nonzero exit,
  SIGKILL, graceful stop, canonical interrupt and forced stop. They exercise mounts, writer exit,
  capture and cleanup using synthetic tool programs. `/tmp/skill-system-pins-systemd.log`. The
  disposable container/image were removed. This is not real Claude, real ego-browser relay/device
  functionality, Server finalization transfer or Docker Sandbox acceptance.
- Final focused race tests and Linux amd64 vet passed: `/tmp/skill-system-pins-race-final.log` and
  `/tmp/skill-system-pins-linux-vet.log`. Full Node quality gate passed with **61.3% host statement
  coverage**, formatting/vet/tests, shell syntax, installer, managed-source/release consistency and
  whitespace checks. `/tmp/skill-system-pins-node-quality.log`.

Node README/rules and the root wire contract now describe fixed artifact admission and historical
recovery. No Server schema or production API change was needed. Safe managed spec creation, worker
startup coordination, lease/ambiguous-launch recovery, target attempts and deployment retry, finalization
transfer/acknowledgement, Docker adapter/writer proof, interrupted migration recovery, Node-only export,
remaining command audits and full real-backend/design acceptance remain outstanding. The full goal
stays active and incomplete. No managed capability, commit, release or deployment was added.

## Increment: immutable managed Native spec creation

The Helper now exposes `prepare_managed_session_spec` and a typed client, without launching a
runtime. Its immutable input binds the logical task, original snapshot/task-record/owners, complete
snapshot digest, system pins, launch parameters and Helper configuration. Initial admission requires
an existing closed account fence and no-follow account directories, no preexisting session directory
or retained work, and a systemd `not-found` unit. Shared account ownership, ACLs and skills are not
rewritten. Workspace/developer-profile setup uses existing Helper primitives.

Private started intent precedes session mutation. An immutable complete nonce-free spec draft is
retained before runtime publication, allowing recovery across a crash between publication and the
ready receipt. Spec, timezone and resolver files use no-follow exact-byte checks, fsync and no-replace
rename. A ready receipt must match the original draft digest. Exact replay verifies original files,
private records, current runtime UID/GID and boot; it cannot repair or recreate missing completed
state. Started recovery reuses the same complete draft on the original boot and refuses existing
units/work. Cross-boot recovery remains explicit unfinished work.

New specs retain an optional `managed_skills` binding. Launch and snapshot content preparation require
the complete spec receipt; content preparation also checks the original task-record UUID and full
snapshot input digest. Old internal specs remain compatible with their existing mount checks.
Private JSON readers now reject hard-linked metadata, in addition to existing link/ownership/mode
checks; new Linux regression tests exposed and closed that gap.

The operation bypasses legacy result caching. Its typed client validates every response identity and
closes the socket on cancellation. The handler owns its disconnect reader, cancels on unexpected
trailing bytes and exits lock waits on disconnect. Connection context expires after 30 seconds;
existing workspace/profile/ACL calls are not individually context-aware, so cancellation is checked
between steps and before ready publication. Incomplete state remains retained. Public errors are
fixed `SKILL_SPEC_UNAVAILABLE` messages. Descriptor-transfer ACK protocols remain unchanged.

Validation:

- Actual rootful Linux store, Helper socket and filesystem tests passed, with real `useradd` and
  `setfacl`. Tests cover exact replay, preserved shared skill content, complete snapshot transfer,
  rejected changed launch/config/task/snapshot inputs, started-draft publication recovery, missing
  ready state, foreign directories/work/units/fences, wrong UID/boot, changed resolver/timezone files,
  symlink/hardlink corruption and cancellation. `tests/linux_skill_copy_test.sh` now installs the
  required ACL/passwd tools and includes these cases. `/tmp/managed-spec-linux-final.log`.
- Host focused race tests passed for new protocol cancellation/receipt checks and existing preparation
  streams/pins: `/tmp/managed-spec-race.log`. Linux amd64 vet passed:
  `/tmp/managed-spec-linux-vet.log`.
- Full Node quality gate passed, including formatting, vet, all host Go tests, shell/installer,
  managed-source/release and whitespace checks, with **61.3% host statement coverage**.
  `/tmp/managed-spec-node-quality.log`. Linux-only code has separate test evidence.

The Linux fixture uses scripted systemctl observations and does not launch Claude. No new real
systemd, Bubblewrap, Server-finalization or Docker acceptance is claimed by this increment. Node
READMEs/rules and the root wire contract describe this boundary. Worker managed dispatch and lease /
mount/start/ambiguous-launch coordination, target attempt ledger and deployment retry, takeover
initiation, finalization transfer/ack/cleanup, Docker adapter/writer proof, started migration recovery,
Node-only export, remaining command audits and the full design/real-backend acceptance remain
outstanding. The goal stays active and incomplete. No capability advertisement, commit, release or
deployment was performed.

## Increment: leased snapshot preparation across Server and worker

Server now exposes `POST /node/skill-snapshots/{snapshot_id}/lease?task_id=<record UUID>` with a strict
positive `lease_attempt`. It checks the original managed pointer, active user, reserved snapshot,
starting session and live leased/running task under the existing user/task locks. Only the original
deadline changes; renewal neither increments the attempt nor revives expired/terminal tasks. The
response binds all Node/user/account/session/backend/snapshot/task identities and grants a positive
server-relative duration capped at 300 seconds. This reuses existing task columns, without migration.

Inspection also found that snapshot file staging previously held user/task locks through disk
copying, which could starve renewal for large files. The route now fixes its immutable manifest entry
in a short authorization transaction, commits before verified private disk copying, and reauthorizes
before returning the spool. Concurrent renewal/revocation can commit during a stalled copy. Changed
authority or missing/corrupt content fails closed without returning partial file content.

The Node client validates every lease identity, exact attempt, canonical non-null fields and bounded
duration. The worker now shares one owned timing loop between snapshot preparation and takeover,
while preserving their separate authorization endpoints and bindings. It subtracts complete request
latency from its local deadline, cancels dependent work on uncertain renewal, joins its loop on exit,
and checks the last confirmed deadline before accepting work completion. A late response cannot make
an already exhausted authorization successful. Lease loss remains a nonterminal recovery condition.

An internal worker coordinator now composes fresh lease acquisition, authenticated original snapshot
fetch, bound Native spec creation, and authenticated file streaming into atomic Helper preparation.
It validates the original input at each boundary and returns only local preparation identity/digest/
runtime UID. Initial denial, foreign snapshots, spec failure, download failure and lease loss return
no success receipt. Shared task-result dispatch is intentionally still disconnected until actual
launch and ambiguous-start recovery can safely own the prepared state; existing managed markers still
return `SKILL_MANAGER_UNSUPPORTED`. This does not complete a create task or advertise a backend.

Evidence:

- New authenticated Server lease/stream tests and existing snapshot download regressions passed on
  an isolated real PostgreSQL database: **37 passed**. This includes concurrent renewal, poll
  `SKIP LOCKED` exclusion while renewal commits, original attempt preservation, strict request types,
  expired/terminal/foreign authority refusal and renewal/revocation during blocked disk copying.
  `/tmp/skill-snapshot-lease-postgres.log`. The disposable PostgreSQL container was removed.
- Real FastAPI/Uvicorn-to-Go lease, manifest and content reads passed; expired task authority denied
  both renewal and downloads while preserving the reserved snapshot.
  `/tmp/skill-snapshot-lease-wire-final.log`, `/tmp/skill-snapshot-lease-live-valid.log` and
  `/tmp/skill-snapshot-lease-live-revoked.log`. Fixture tokens were disposable and temporary files
  were removed. This is HTTP contract evidence, not Claude startup acceptance.
- Focused API/worker/Helper race tests passed, including preparation ordering, cancellation, deadline
  exhaustion and takeover lease/transfer regressions: `/tmp/skill-snapshot-preparation-race-final.log`.
  Linux amd64 vet passed for those packages: `/tmp/skill-snapshot-preparation-linux-vet.log`.
- Full Node quality gate passed with **61.4% host statement coverage**, all host Go tests, formatting,
  vet, installer, shell, managed-source/release and whitespace checks.
  `/tmp/skill-snapshot-lease-node-quality-final.log`. Additional deadline regression and live-wire
  tests also passed after that run; no Linux mount/lifecycle implementation changed this increment.
- Full Server quality gate passed with **1341 passed, 48 skipped**, **82.23% coverage**, Ruff, mypy,
  docstring and whitespace checks: `/tmp/skill-snapshot-lease-server-quality.log`. Later-added lease
  concurrency/configuration cases are included in the independent PostgreSQL run; final static
  checks cover those additions. PostgreSQL-specific skipped cases outside this increment are not
  claimed as newly verified.

Node READMEs/rules, Server architecture/control/persistence rules and the root wire contract describe
the new boundary. Remaining work includes queue dispatch with lease-aware mount/start and ambiguous
launch recovery, target attempt ledger/deployment retry, takeover initiation, finalization transfer /
acknowledgement/cleanup, Docker adapter/writer proof, interrupted migration recovery, Node-only export,
remaining command audits and full design/real-backend acceptance. The full goal remains active and
incomplete. No commit, release, deployment or managed capability advertisement was performed.

## 2026-09-23 — at-most-once managed Native Helper launch

The dedicated `start_managed_session` operation now consumes the same complete input and logical
request identity as managed spec preparation. It bypasses the generic Helper result cache. A private
`session-launch-<session UUID>.json` binds the original ready spec/draft, boot and unit, with durable
no-replace starting intent before systemd-run. Readiness seals the original nonzero invocation ID;
terminal receipts cannot change that invocation. Historical success replay survives transient spec
cleanup and never recreates files or restarts a process. It does not assert current session liveness.

An incomplete same-boot launch can recover only the original active transient service. Recovery
verifies user/cgroup/invocation identity, exact retained work and mount, rw/nosuid/nodev/private flags,
selected system copies, and stable invocation across readiness. It performs no mount or repair under
live writers. Missing/non-running units enter common stop/finalization and return SKILL_START_STOPPED;
uncertain or corrupt evidence returns SKILL_START_PENDING. Neither permits another execution.
Cancellation/disconnect uses independent bounded writer cleanup and retains unclean work. A starting
record plus termination/finalization evidence remains retained, never a new launch opportunity.

The typed client validates all 15 result fields, exact task/snapshot/session/account/backend/unit,
non-root UID, tmux identity, empty sandbox/container fields and canonical owner/workspace/account path
suffixes. The managed socket handler preserves bounded errors and cancellation-aware mutation locking.
No broker nonce is persisted in launch/spec authority. Completed replay needs the original private
spec records but not the transient runtime files.

Evidence:

- Rootful Linux private-store, spec, launch, content-copy and selected system-tree suites passed:
  `/tmp/managed-launch-linux-final.log`. Cases cover immutable intents/invocations, changed binding,
  missing private authority, absent-unit unclean finalization, no launch without prepared work,
  historical replay after cleanup, client receipt validation and malformed/unsafe mount metadata.
- Real isolated systemd managed launch and recovery passed. Simulated loss of the readiness receipt,
  repeated requests and cleanup replay preserved one invocation and one synthetic tool execution.
  Deliberately removing nosuid caused pending recovery without repair; restoring it permitted exact
  recovery. Disconnect during startup stopped writers, retained the original work and unclean journal,
  and subsequent requests returned stopped. The six existing Native lifecycle cases (normal, error,
  SIGKILL, graceful stop, canonical interrupt and forced stop) also passed:
  `/tmp/managed-launch-systemd-verified.log`. Disposable systemd container/image were removed by the
  harness. These are synthetic tool tests, not real Claude or Docker Sandbox acceptance.
- Focused host race tests passed: `/tmp/managed-launch-race-final.log`. Linux amd64 vet passed for
  Helper, skillmanager and worker: `/tmp/managed-launch-linux-vet.log`. Linux-only private-store and
  mount paths are covered by the rootful runs, not by host race coverage.
- Full Node quality gate passed with **61.5% host statement coverage**, all Go tests, vet, formatting,
  shell, installer, managed-source/release and whitespace checks:
  `/tmp/managed-launch-node-quality-final.log`.

Node READMEs and architecture/control/persistence rules plus the root wire contract now describe this
operation. Worker dispatch is still disconnected: preparation currently ends its lease before any
launch, and generic task execution still treats operation failures as terminal. Integration must own
a continuous preparation/start lease, inspect/recover original launch state before repeating spec
preparation, preserve ambiguous/lease-lost work as nonterminal, and handle broker registration/nonce
ownership. Incomplete starts from another boot still fail closed pending explicit recovery; completed
historical receipts remain replayable. Broker restart recovery is not implemented by this increment.

The full goal remains active and incomplete. Durable target attempts/retry, takeover initiation,
finalization transfer/publication/acknowledgement/cleanup, Docker lifecycle/writer proof, interrupted
migration recovery, Node-only export, remaining command audits and full real-backend acceptance remain
required. No commit, release, deployment or managed capability advertisement was performed.

## 2026-09-23 — continuous leased internal startup and exact recovery/cancellation

The Helper now exposes `recover_managed_session` before preparation and `cancel_managed_session`
after uncertain startup. Both require the original complete spec request and logical request ID,
bypass generic task caching, and share managed socket cancellation/serialization. No launch intent
returns a strictly validated five-field not_started receipt. Existing intents require the original
ready spec and immutable draft; corrupt records, directories and dangling links cannot authorize
preparation. Recovery cannot submit a new invocation. Completed historical readiness can replay
without transient files; incomplete original launches use the existing recovery/finalization rules.

Exact cancellation validates original task/input/runtime authority before common writer stop and
finalization. A changed request cannot stop the original process. Success returns a five-field
stopped receipt; it does not delete retained work or certify Server persistence. Repeated cancellation
reuses the retained finalization. It does not overwrite a historical readiness record or imply that
its historical running result describes current liveness.

The internal `startManagedSnapshot` worker coordinator now maintains one lease from authenticated
snapshot fetch through recovery, optional spec/content preparation, explicit peer admission and
launch. It recovers before preparing, admits the selected non-root UID before first launch, checks
that launch returns the same UID, and removes the internal UID from its result. Lease loss, response
loss, peer-admission failure or inconsistent state yields a nonterminal pending error. Once Helper
has been contacted, every failed path independently requests exact cancellation under a fresh bounded
context, including when a successful launch response races lease loss or caller cancellation.
Uncertain cancellation remains pending; no retained copy is deleted or replaced. The original lease
loop is joined before cleanup, and its failure/cancellation cause is preserved.

Evidence:

- Rootful Linux copy/store/Helper suite passed with absent-before-preparation, historical cleanup
  replay, missing-unit finalization and corrupt/dangling/directory launch-intent tests:
  `/tmp/managed-startup-linux.log`.
- Real systemd recovery and both cancellation paths passed: `/tmp/managed-startup-systemd-final.log`.
  Explicit cancellation rejects changed input without stopping the original service, then stops it
  through repeated exact requests and preserves original files/finalization. Existing invocation and
  weakened-mount recovery proofs passed again. The first explicit cancellation run exposed a test
  fixture's 20-second socket deadline, shorter than the production 30-second operation; the fixture
  now permits 45 seconds so it does not inject an unrelated disconnect. Production deadlines did not
  change. Disposable test container/image were removed by the harness.
- Worker and Helper race tests passed: `/tmp/managed-startup-race-final.log`. Cases include ordered
  admission, historical recovery without preparation, initial lease denial, foreign snapshot refusal,
  preparation/content/admission/launch errors, changed UID, late successful responses after lease loss
  or cancellation, and uncertain cleanup. Strict typed recovery/cancel receipt tests also passed.
- Linux amd64 vet passed: `/tmp/managed-startup-linux-vet-final.log`. Full Node gate passed with
  **61.6% host statement coverage**, all host tests, vet, formatting, installer, shell, source/release
  and whitespace checks: `/tmp/managed-startup-node-quality-final.log`.

READMEs, Node architecture/control rules and the root wire contract now distinguish local preparation,
leased internal startup and actual queue integration. The coordinator still requires its caller to
own the original broker registration; it cannot rotate a live nonce. Generic worker task dispatch and
terminal reporting remain disconnected and still need nonterminal ledger handling, broker ownership/
restart recovery, stopped-versus-historical-readiness reconciliation and cross-boot incomplete-start
recovery. Finalization transport/ack/cleanup and the broader remaining requirements listed above are
still required. No managed backend capability, commit, release or deployment was enabled. The full
goal remains active and incomplete.

## 2026-09-23 — current runtime recovery and original broker peer admission

Recovery now separates current liveness from historical startup success. `start_managed_session`
still preserves its immutable historical ready receipt. `recover_managed_session`, which the internal
worker startup coordinator uses, requires the original live/ready service and the saved invocation ID
for completed launches. It cannot treat an old ready receipt as evidence that the runtime is still
running. Absent/non-running units enter retained stop/finalization; missing transient specs do not
recreate runtime files. Finalized/terminated original work returns SKILL_START_STOPPED. This supersedes
the previous increment's statement that the recovery operation itself replays historical running
results after cleanup. Historical replay remains available only through the original start operation.

Exact cancellation now also checks active systemd identity and the saved invocation before stopping.
A same-named service with a different invocation is retained as uncertain rather than adopted or
stopped. Cancellation during recovery uses the same independent check before failed-launch cleanup.
Active recovery still requires original-boot spec identity; absent services use the common retained
finalizer without requiring active-runtime artifacts. Complete cross-boot task reconciliation is not
claimed from these absence tests.

Broker peer admission is now explicitly split. `VerifyToolSessionPeer` checks the original session,
nonce and UID together under the broker lock, without creating sockets, changing ACLs or authorizing
a replacement capability. Initial startup may authorize its trusted UID; recovered startup only uses
this existing-grant verification. A registration alone, even after repeated registration calls, does
not prove original admission. Revoked/restarted brokers cannot silently adopt the capability still
held by an existing process. No nonce is persisted or resurrected.

The worker's managed peer adapter removes task-controlled broker context, derives context from its
own configuration and current registration, prepares the broker socket, and supplies separate initial
and recovery admission methods. Invalid-input rollback removes only a newly created exact registration;
stale rollback cannot revoke a later registration. Cancelled contexts, root UID, changed registration
and changed runtime UID are denied. Failed recovery admission enters the startup coordinator's exact
cancellation path and remains pending for retained-state finalization. Browser-disabled sessions do
not require a broker grant, but still reject untrusted injected browser context.

Evidence:

- Broker/worker/Helper race tests passed: `/tmp/managed-peer-race-final.log`. Tests exercise existing
  admission, repeated unadmitted registration, nonce/UID/session mismatch, revocation, real broker
  close/reconstruction over the same state/socket paths, cancellation, disabled browser context,
  rollback ownership, and startup-coordinator cancellation after original peer revocation.
- Rootful Linux private-store/copy/Helper suite passed: `/tmp/managed-peer-linux-final.log`. Added
  checks prove that a completed historical launch with missing transient files becomes stopped and
  retains unclean finalization through recovery while its original start receipt remains replayable.
- Real isolated systemd launch/recovery/cancellation passed: `/tmp/managed-peer-systemd-final.log`.
  Injecting a different saved invocation makes both recovery and cancellation refuse to adopt the
  live unit; restoring original authority permits recovery without another tool execution. Historical
  start replay after cleanup remains successful, while recovery correctly reports stopped. Existing
  unsafe-mount, disconnect and exact repeated-cancellation proofs passed again. These remain synthetic
  tool tests, not real Claude/Docker acceptance. The harness removed its disposable container/image.
- Linux amd64 vet passed: `/tmp/managed-peer-linux-vet.log`. Full Node gate passed with **61.7% host
  statement coverage**, Go tests, vet, formatting, installer, shell, managed-source/release and
  whitespace checks: `/tmp/managed-peer-node-quality-final.log`. The later rollback-only regression
  is covered by the final race run; production code was unchanged after the full gate.

Node READMEs, architecture/control rules and the root wire contract now document these distinctions.
Queue dispatch and terminal task ledger/reporting remain disconnected. Integration still must map
stopped startup to retained finalization/reconciliation, preserve nonterminal lease/recovery errors,
and complete cross-boot task handling. Finalization transfer/ack/cleanup, durable target attempts,
takeover dispatch, Docker lifecycle and the remaining complete-design audit are still required.
The full goal remains active. No capability advertisement, commit, release or deployment was performed.


## 2026-09-23 — exact managed startup confirmation and atomic Node task ledger

Managed Native startup now has a dedicated authenticated confirmation route and typed Go client.
Ready results contain ten fixed fields; stopped results contain nine. Both bind the original
snapshot, task-record UUID, session/account/backend, canonical unit and exact positive poll attempt.
No content, paths, runtime UID, argv or broker material enters these outcomes. The Server requires
the unchanged managed pointer, active owner, reserved snapshot, starting session and unexpired
current lease before first acceptance. User/session/task locks serialize first publication with
renewal. The existing task-result/lifecycle/retention transaction owns the result and session change;
accepted readiness also marks the snapshot started, and accepted stopped startup marks it finalizing.

Exact committed replay is historical acceptance only. It skips task/session state reapplication and
repeated revocation, including after finalization and content retirement. Opposite outcomes, changed
attempts and changed authority conflict. Persisted snapshot references prevent missing task markers
or changed task types from falling back to generic completion. Generic completion/failure routes
also enforce the guard. The dedicated route cannot upgrade legacy tasks into managed receipts.
The Go client requires schema/status/committed agreement and an exact original outcome echo;
missing, duplicate, aliased, null, foreign and mixed receipt fields fail closed. It never retries an
uncertain write implicitly. Real Uvicorn-to-Go tests cover both outcomes and explicit exact replay.

The Node task ledger now retains its original JSON map format but writes a private temporary file,
syncs it, atomically renames it and syncs the parent directory. Memory changes only after publication.
An uncertain post-rename result blocks subsequent reads and writes until reopen, rather than returning
an apparent missing task. Empty/null/corrupt existing ledgers fail closed. Saved and returned values
are detached from caller-owned maps. JSON integer values survive reopen and unrelated rewrites without
float64 rounding. Worker reporting now propagates all ledger failures before reporting an outcome.
This is persistence groundwork; managed pending-confirmation records are not yet wired.

The prior four full-gate failures were obsolete retention-test assumptions: three recreated an
active session through an unguarded late create result, and one expected a later retirement error
instead of strict result rejection. Their lifecycle-clock tests now use explicit stop or controlled
active-session fixtures, and separate regressions prove late results leave task/session/snapshot
state and release clocks unchanged, before and after content retirement. Additional tests prove
an accepted original receipt still replays after retirement and a later lifecycle exception rolls
back the result, task, session and snapshot phase even if the caller commits the outer transaction.

Verified evidence:

- Final focused PostgreSQL group: **49 passed**, including independent concurrent same/opposite
  publications, retention clocks, late-result rejection, retired receipt replay and savepoint rollback:
  `/tmp/skill-start-atomic-postgres-final.log`. The disposable PostgreSQL container was stopped and
  removed; no host database or volume was modified.
- SQLite final start-result tests: **25 passed, 2 PostgreSQL-only skips**:
  `/tmp/skill-start-atomic-tests.log`. The preceding focused retention/confirmation group passed
  **42 tests with 4 PostgreSQL-only skips**: `/tmp/skill-start-phase-tests.log`.
- Real Go-to-Uvicorn confirmation/replay/changed-attempt denial for both outcomes:
  `/tmp/skill-start-confirmation-wire-final.log`. Private disposable credentials were cleaned up.
- Final Node full gate passed, **62.0% host statement coverage**:
  `/tmp/managed-confirmation-ledger-node-quality-final.log`. API/ledger/worker race checks passed in
  `/tmp/managed-confirmation-ledger-race-final.log`; the final integer-preservation increment passed
  `/tmp/managed-ledger-integer-race-final.log`. Linux amd64 API/ledger/worker vet passed in
  `/tmp/managed-confirmation-ledger-linux-vet.log`.
- Ledger tests also passed in an isolated Linux container running as UID/GID 65534, with no network,
  read-only root and private temporary filesystem: `/tmp/managed-ledger-linux-proof.log`. The
  container and temporary test binary were removed. This proves Linux file publication behavior,
  not physical power-loss recovery or managed runtime acceptance.
- The first repaired Server full gate passed **1370 tests, 51 skips, 82.26% coverage** in
  `/tmp/skill-start-results-server-quality-final.log`. It began before the final snapshot-phase and
  three added regression cases. The final-current Server full gate then passed **1373 tests,
  51 skips, 82.32% coverage**, Ruff format/lint, mypy (497 source files), docstrings and whitespace
  checks: `/tmp/skill-start-results-server-quality-current.log`.

Queue integration remains the immediate next requirement. It must strictly decode the original
managed pointer and poll record, retain one lease through startup and Server confirmation, and
persist the exact pending outcome before network publication. A verified committed receipt must win
renewal rejection caused by that same commit. A lost acknowledgement cannot be retried only on task
redelivery: the Server may have committed and stopped polling that task. Background pending-result
recovery is required. Conversely, an uncommitted outcome from an expired earlier attempt cannot be
blindly relabeled with the new poll attempt; first establish its Server acceptance/absence and recover
the original runtime. These recovery transitions and their authoritative query contract remain to be
implemented before connecting the generic dispatcher. Saved historical success never proves current
runtime readiness, and generic failed-result caching must not consume nonterminal managed errors.

A bounded read-only integration audit reconfirmed that Node worker dispatch still has no managed
startup/takeover/finalization branches; the takeover coordinator consumes retained captures but does
not initiate capture; no Node finalization HTTP client is present; deployment models retain original
plans but not execution attempts; and real Docker managed launch remains unimplemented. Durable target
attempts/retry APIs and CLI, takeover dispatch, finalization transport/publication/ack/cleanup,
cross-boot and interrupted migration recovery, Node-only export, real Claude/Docker acceptance and
the complete design audit remain necessary. The full goal is active. No capability advertisement,
commit, release or deployment was performed.


## 2026-09-23 — durable startup receipt recovery and Native queue dispatch

The dedicated Native task path now strictly decodes the original four-field managed pointer and
poll envelope before Helper work. It validates canonical creation fields, configured backend and
Node, exact task-record UUID/idempotency key and positive int32 poll attempt. Real Server
`git_sync_policy` metadata is validated separately from Helper execution input. Null/aliased managed
markers and existing managed ledger entries cannot enter legacy start or generic terminal replay.
The queue retains one lease through original-runtime recovery, preparation, broker admission,
Helper startup and Server confirmation. Nonterminal failures are not cached as generic failed tasks.

The Server now exposes an exact read-only managed-result inspection route. Under the original
user/session/task authority locks it returns the original proposal, acceptance, current poll attempt
and task status. Inspection cannot renew a lease, change lifecycle state, create missing usage rows
or move retention clocks. Changed authority or a conflicting receipt fails closed. Same-attempt
absence cannot exclude an in-flight publication; only an observed strictly newer attempt fences an
older unaccepted proposal. The Go client validates every receipt and never implicitly republishes.

The Node journal stores schema-1 pending/confirmed records containing only the complete snapshot
binding and exact bounded outcome. It persists the proposal before HTTP publication. Ledger
compare-and-swap serializes updates against the entire original record; detached, sorted pending
enumeration allows background recovery independently of task redelivery. That loop only inspects
Server acceptance and saves an exact acknowledgement; it never launches, republishes readiness,
renews leases or touches runtime authority. A stale observation cannot overwrite a newer proposal.
Identical concurrent acknowledgements are idempotent. Malformed/aliased/null journal metadata stays
an error, including after ledger reopen. A known Server commit wins concurrent lease rejection even
when persisting the local acknowledgement fails.

Historical acceptance remains distinct from runtime liveness. A newly created broker registration
used only to inspect an accepted receipt is rolled back without granting a replacement peer;
an existing original peer is preserved. Already-confirmed live sessions still need separate
reconciliation/drain after broker restart. Complete cross-boot recovery is not claimed.

Evidence:

- Server full gate: **1382 passed, 52 skipped, 82.34% coverage**, with Ruff, format, mypy (498 source
  files), Chinese docstrings and whitespace checks: `/tmp/managed-start-recovery-server-quality.log`.
- Final PostgreSQL inspection/start-result/snapshot-lease group: **62 passed**, including concurrent
  old confirmation and inspection behind a transaction advancing the poll attempt:
  `/tmp/managed-start-inspection-postgres-final.log`. The initial test barrier was repaired to observe
  task lookup before lock acquisition; the final run supersedes the earlier failed test-harness run.
  The exact disposable PostgreSQL container was stopped and removed.
- Node full gate at this increment: **62.5% coverage**:
  `/tmp/managed-start-recovery-node-quality.log`. Full API/ledger/worker race tests passed in
  `/tmp/managed-start-dispatch-race.log`; additional journal corruption/concurrent-ACK/historical-peer
  tests passed in `/tmp/managed-start-journal-boundary-race.log` and the subsequent final race run.
- Actual Go-to-Uvicorn inspection/confirmation/replay for ready and stopped outcomes passed:
  `/tmp/managed-start-inspection-wire.log`. Linux amd64 vet passed:
  `/tmp/managed-start-recovery-linux-vet.log`.

The queue is now connected. A full real Worker-to-Helper-to-systemd managed session remains to be
accepted; queue lease/dispatch, fake-Helper coordination, real HTTP and the earlier standalone
systemd proofs cover different boundaries and are not a substitute for that full acceptance.


## 2026-09-23 — exact Node finalization HTTP transport

The Go API client now implements immutable finalization begin, read-only status, verified streaming
file upload, exact-upload completion and separate whole-directory publication. Requests carry the
original snapshot/session, durable idempotency key, tree digest and clean/unclean classification.
Known receipts cannot change finalization identity or regress upload attempts. Upload ID changes
require a strictly newer attempt; completion must acknowledge the exact submitted upload. A retained
incoming checkpoint cannot disappear or be replaced by a publication result checkpoint.

All finalization/publication/file receipt fields are typed and canonical; missing, extra, aliased,
duplicate and invalid null fields fail closed. File transfer consumes and closes its source, verifies
length/digest/classification and requires verified EOF before accepting acknowledgement. The shared
HTTP boundary refuses redirects, bounds responses and does not retry uncertain writes. Publication
preserves published/conflicted/detached/superseded decisions. Unclean input can only return detached
with its original unclean reason. Single-file success never means complete persistence, and neither
HTTP persistence nor publication alone acknowledges local cleanup.

Real Go-to-Uvicorn testing found SQLite finalization receipts omitted the expiry timezone. The Server
schema now applies the same UTC normalization already used by package upload receipts, with an HTTP
regression assertion. This change preserves the upload deadline and does not grant client-side lease
authority. The preceding Server full gate predates this small schema fix; the finalization service/
HTTP group subsequently passed **26 tests** (`/tmp/managed-finalization-expiry-tests.log`), and the
static checks were rerun.

Final transport evidence:

- Node full gate passed with **63.0% host statement coverage**, all Go tests, vet, formatting,
  installer, shell, managed-source/release consistency and whitespace checks:
  `/tmp/managed-finalization-node-quality.log`. The later optional live-test extension changes only
  test code and passed all four real-wire scenarios below.
- API/ledger/worker race tests passed: `/tmp/managed-finalization-start-race.log`; Linux amd64 vet
  passed: `/tmp/managed-finalization-linux-vet.log`.
- Four actual Uvicorn-to-Go scenarios passed: clean/unclean input, each with fresh/expired upload.
  They verify incomplete-content rejection, full streaming/persistence/publication, exact replay,
  changed-classification rejection, status without renewal, stable finalization identity across a
  newer upload, and rejection of writes/completion from the superseded upload:
  `/tmp/managed-finalization-live-wire-final.log`. Fixtures used private disposable credentials and
  database/content directories, all cleaned after completion. These are transport tests, not full
  Worker/Helper runtime acceptance.
- Final Server Ruff lint/format, mypy (498 files), Chinese docstrings and whitespace checks passed
  after the UTC normalization. No Server service or database mutation logic changed in that fix.

The transport is groundwork for the remaining Helper retained-file protocol and durable worker
transfer/publication/ACK/cleanup loop. It does not read privileged filesystem paths, prove writer
quiescence, initiate finalization, persist a Helper acknowledgement, or advertise managed capability.
Already-confirmed broker-restart reconciliation, cross-boot recovery, takeover capture dispatch,
durable deployment attempts/retry API/CLI, Docker managed adapters, interrupted migration recovery,
Node-only pending export, real Claude/Docker acceptance and the complete design audit remain required.
The full goal remains active. No commit, release, deployment or capability advertisement was performed.


## 2026-09-23 — independently frozen finalization bytes and Helper descriptor transfer

A direct storage audit found that the prior finalization journal retained the manifest but still
relied on runtime-owned work files for ordinary content. That was insufficient evidence for a
complete independent frozen upload input. New finalizations now copy every distinct ordinary-file
digest into helper-owned 0600 `objects/` content beneath the same private staging directory as the
manifest and record. The copy verifies length, digest and text classification, uses no-follow source
walks, and fsyncs each object and directory. A second complete capture must match before atomic
no-replace publication and parent sync. Links remain manifest metadata. Helper stop/finalization now
passes its configured filesystem reserve to this additional copy admission. Failure preserves work
and the original termination receipt; a retry cannot reclassify unclean data as clean.

The additive `objects_version=1` marker certifies independent frozen bytes. Common snapshot binding,
finalization record and capture types now live in platform-neutral files for the worker/client, while
privileged filesystem operations remain Linux-only. Binding and journal decoding require explicit
original generations and termination classification; aliases, missing/null fields and duplicate
record/binding keys cannot silently turn into zero/default authority.

Old manifest-only records remain readable as version 0. The quiescent finalizer can upgrade them
without recapturing: copy exactly the saved manifest bytes, atomically publish the object directory,
verify the complete object set, then durably advance only the format marker. A crash after objects
but before the marker resumes verification, even if work is subsequently absent. Missing/changed
original bytes or a corrupt existing object set fails closed, preserving the old record. Read-only
transfer cannot initiate this migration or alter clean/unclean classification or lifecycle phase.

`open_skill_finalization_file` now exposes a separate bounded read-only Helper protocol. It checks
the complete original Node/user/account/session/snapshot/epoch/preparation binding and retained
canonical Native resource. An object request additionally supplies the original tree digest,
clean/unclean flag and a declared file digest. It never accepts host paths or consults work. Success
transfers one read-only, root-owned 0600 ordinary descriptor with exact typed record/entry/size
metadata; the client atomically receives CLOEXEC, rejects unsafe descriptors and validates the
manifest digest. The uploader still must independently validate streamed bytes. Errors are bounded
and omit private paths. The handler owns its reader, cancellation, cancellable mutation-lock wait,
30-second lifetime and five-second descriptor ACK wait. ACK means descriptor receipt only.

Account capture and finalization now share the existing bounded Unix descriptor framing, cancellation,
ancillary parsing and descriptor-safety check. They retain independent authority schemas and error
codes. Existing account-capture adversarial tests were rerun to verify that this extraction did not
weaken its protocol. No new ambient worker filesystem privilege was granted.

Verified evidence:

- The expanded isolated Linux copy/Helper gate passed in
  `/tmp/finalization-descriptor-linux-final.log`: complete storage tests, original Native stop/spec/
  startup tests, account-capture descriptor regressions and new finalization descriptor tests.
  New storage cases verify bytes after work removal, duplicate digest storage, symlink/hardlink/mode/
  directory rejection, foreign identity refusal, disk-reserve failure, and both sides of interrupted
  legacy object publication. These simulate interruption states; physical power-loss recovery is not
  claimed from them.
- Actual root Helper to UID 65534 transfer passed. That process cannot traverse the private store or
  write the transferred file; UID 65533 is denied. Malformed, multiple, truncated, writable and pipe
  descriptors, missing/null/aliased metadata, fragmented responses and cancelled lock waits all
  passed with no observed descriptor leak. These tests are included in the same Linux log and now
  in `tests/linux_skill_copy_test.sh`.
- Full isolated systemd lifecycle/copy/migration/startup-recovery/cancellation proof passed:
  `/tmp/finalization-frozen-systemd.log`. An additional current lifecycle test then passed all six
  normal/error/SIGKILL/graceful-stop/canonical-interrupt/forced-stop cases, removes transient and work
  files, and retrieves the actual tool's original `learned` bytes through the real Helper socket:
  `/tmp/finalization-descriptor-systemd-final.log`. Terminal Server acknowledgement remains an
  explicit test fixture, not a claim of full Worker-to-Server publication. Both scripts cleaned their
  exact disposable containers and images.
- Node full gate passed with **61.6% host statement coverage**:
  `/tmp/finalization-frozen-node-quality.log`. Linux-only behavior is established by the proofs above;
  moving shared record validation and adding descriptor clients changes the host coverage denominator.
  Skillmanager/runtimehelper/worker/API race tests passed:
  `/tmp/finalization-frozen-node-race.log`. Linux amd64 vet passed:
  `/tmp/finalization-frozen-linux-vet.log`. The final systemd descriptor-read extension is test-only
  and passed its dedicated current run after this gate.

The next integration must enumerate retained finalizations independently of polled create tasks,
stream these exact objects through the existing authenticated HTTP client, persist exact Server
acknowledgements, and coordinate publication/local state advancement without deleting pending data.
Already-confirmed runtime reconciliation after broker restart, complete cross-boot recovery,
takeover initiation/dispatch, durable target attempts/retry APIs/CLI, Docker managed lifecycle,
interrupted account migration recovery, Node-only export and the full design acceptance audit remain
required. The goal remains active; no capability advertisement, commit, release or deployment occurred.

## 2026-09-23 — independent finalization inventory and durable background transfer

The Node now runs a separate finalization loop for configured Native nodes with control-plane
credentials. It does not depend on task redelivery or reuse the expired startup lease. The loop
consumes a read-only Helper inventory, transfers only the already frozen original objects, and
persists the exact Server input-retention and publication decisions independently. This increment
closes the worker transfer/restart gap; it does not yet advance the privileged Helper journal or
release transient resources.

`list_skill_finalizations` validates the configured Node and a canonical session cursor, walks only
the existing private store, and returns at most 16 sorted candidates. Directory entries are read in
bounded batches and only the smallest next-page IDs are retained in memory. A candidate independently
revalidates its original preparation/baseline, Native runtime resource and finalization manifest.
Missing finalization directories, invalid retained state and unsupported backends have distinct
bounded diagnostics. Corrupt/linked/incomplete candidates cannot masquerade as successful or absent
finalization and do not prevent later candidates from progressing. Malformed session names are
reported as an aggregate flag without exposing paths. Only a verified no-follow ENOENT can produce
an empty absent-store inventory; links and unsafe roots remain errors. The operation never creates
state, accesses work, upgrades a legacy journal or requires transient specs. Its handler owns a
30-second timeout, disconnect cancellation and cancellable mutation-lock wait. Inventory is not a
transactional snapshot; newly inserted earlier IDs are revisited in the next pass.

The client preserves `json.Number` for this new operation without changing legacy response types.
This matters for original generations above 2^53: the generic Helper map decoder previously used
float64. Exact large generations now survive the complete socket/typed-page/worker-ledger path.

The worker uses a separate `<ledger_path>.skill-finalizations` ledger keyed by original snapshot
UUID. Schema 1 contains the original typed Helper capture and nullable exact Server finalization
and publication receipts; it stores no manifests, content or credentials. Original input is fsynced
before begin, current upload before file transfer, and complete incoming checkpoint before publication.
The stable idempotency key is `skill-finalization:<snapshot UUID>`. Updates use the existing atomic,
parent-fsync, whole-record compare-and-swap ledger implementation and preserve integer identities.
Changed owner/capture/termination, stale upload attempts and changed retained incoming checkpoints
fail closed. Incoming and merged-result checkpoint references remain separate.

After a lost begin reply, the same original body/key is replayed. Known finalizations are inspected
before resuming; an expired upload may renew only within its original finalization identity and a
strictly greater attempt. Distinct ordinary digests are streamed once per transfer attempt from
Helper descriptors through the authenticated API client. Lost complete replies recover persistence
through status without repeating object transfer/completion; lost publish replies replay the original
publication request. Verified Server responses followed by local write failures retain the previous
durable record and recover after restart. Published/conflicted/detached decisions are saved, while
superseded remains explicitly pending and cannot start a new publication attempt automatically.
Per-candidate failure does not prevent the inventory cursor advancing to later sessions. Public
worker logs use one bounded pending error rather than filesystem paths or HTTP response bodies.

Verified evidence:

- Node full quality gate passed, **61.4% host statement coverage**:
  `/tmp/finalization-background-node-quality.log`. This includes all Go tests/vet, shell parsing,
  installer tests, managed-source consistency and whitespace checks.
- Host race tests passed for worker/API/skillmanager/runtimehelper:
  `/tmp/finalization-background-race-final.log`. An earlier run found a race in the new HTTP test
  fixture's unsynchronized call-history assertion; synchronized snapshots fixed it. No production
  race was reported by that run. Full Linux amd64 vet passed:
  `/tmp/finalization-background-linux-vet-final.log`.
- Expanded isolated Linux storage/Helper/worker tests passed:
  `/tmp/finalization-background-linux-final.log`. The script now runs the finalization worker group
  as well as all previous copy/descriptor regressions. New tests cover bounded pagination, broken
  candidates, absent versus unsafe stores, legacy read-only inventory, foreign Node refusal,
  large generations and disconnect cancellation while waiting for the Helper mutation lock.
- Worker tests use the actual authenticated Go HTTP client against a fixture HTTP server. They
  cover distinct digest deduplication, clean/unclean publication, conflict/detached/superseded
  separation, lost responses at all four mutation stages, expired upload renewal, local write
  failures after Server acceptance, original object corruption, cancelled transfer, stale CAS
  and continued progress past a corrupt earlier candidate.
- Additional Linux integration uses the real private skill store, real Helper socket and descriptor
  transfer, actual worker scan/transfer coordinator, and HTTP fixture. Clean and unclean cases remove
  work before transfer and lose the complete response, then reopen the worker ledger and recover via
  independent inventory/status. They verify original frozen bytes remain readable and the privileged
  Helper journal remains unchanged. This fixture starts from already-quiescent synthetic files; it
  is not a new systemd, real Claude or real Server database publication acceptance claim. The script
  removed its disposable container and crosscompiled test files.

Next, the exact durable Server receipts must be acknowledged into the Helper under the original
full binding, with crash-recoverable state advancement and stopped-session transient cleanup. The
worker ledger alone is not root-owned retention authority; descriptor/file ACKs and superseded
publication cannot authorize cleanup. Full natural-exit/restart finalization, already-confirmed
broker restart drain, cross-boot writer proof, takeover initiation/dispatch, durable target attempts
and retry APIs/CLI, Docker managed lifecycle, interrupted migration recovery, Node-only export and
the complete design acceptance audit remain required. The goal remains active and incomplete.
No capability advertisement, commit, release or deployment was performed.

## 2026-09-23 — privileged finalization acknowledgement and stopped-runtime cleanup

The worker now transfers its durably saved Server receipts into the privileged Helper journal, then
requests a separate guarded cleanup of the stopped Native runtime's transient resources. It retains
all original work, frozen objects, manifests and snapshot references. This closes the acknowledgement
and same-boot transient-cleanup gap in the independent background transfer path; it does not claim
complete lifecycle entry-point or cross-boot recovery.

Finalization input/receipt/publication schemas and their strict validation now live in the neutral
`internal/skillmanager` package. `internal/api` retains aliases and all authenticated HTTP operations;
no transport client or Node credentials enter the Helper. Original wire fields, explicit nullable
references, integer bounds, upload identity and clean/unclean publication checks remain enforced.
The per-file HTTP receipt retains its own strict bounded decoder.

`acknowledge_skill_finalization` accepts exactly version 1, the full original frozen capture, complete
Server finalization receipt and an explicit nullable publication receipt. The configured authorized
worker is the delegated source of authenticated Server observations; this protocol is not a Server
signature. The Helper independently validates original Node/session/preparation identity and canonical
Native resource, then fsyncs/atomically publishes `finalization/acknowledgement.json` before advancing
`record.json` through supported phases. It cannot create a capture, upgrade legacy objects, reclassify
termination, stop writers or delete resources. Replay resumes interruption after acknowledgement or
an intermediate state write. Identical replay re-syncs its directory without rewriting the receipt.
Changed original inputs, older upload attempts, replaced incoming checkpoints and changed existing
publication decisions fail closed. Superseded remains persisted and grants no terminal cleanup.

The worker acknowledges each receipt only after its own ledger publication. Complete persistence
precedes the publication request, and the full publication receipt precedes terminal Helper state.
Lost Helper responses reuse the saved exact Server receipt; terminal ACK/cleanup retries do not issue
another Server publication. If the worker ledger is missing/restored behind an already-terminal root
journal, it obtains the full original publication before acknowledging that phase, rather than trying
to regress the Helper to persisted.

`cleanup_skill_finalization` accepts only the exact terminal capture and requires the separately
retained publication acknowledgement. It passively verifies systemd state and complete cgroup
quiescence; it never sends stop/kill or admits a replacement runtime. An existing spec must match the
original binding/boot/unit/UID/GID; missing specs use only retained identity and Helper-derived names.
First cleanup remains restricted to the original boot until complete cross-boot reconciliation exists.
The original skill-work mount must match retained work and unmount normally. A mounted tmp must be
actual tmpfs and also unmount normally; linked, busy or uncertain mounts stay pending. Network deletion
is preceded and followed by bounded namespace inspection; failures are not ignored as absence.
SessionRoot removal is parent-directory-synced before private immutable
`finalization/runtime-cleanup.json` records the terminal capture and Helper-selected original root.
Completed replay checks that runtime root, writers and namespace have not reappeared, and never
removes replacement resources. A changed configured runtime root cannot reuse the old cleanup marker.
Both operations use exact integer decoding, owned 30-second cancellation and cancellable lock waits.

Verified evidence:

- Node full gate passed with **61.1% host statement coverage**:
  `/tmp/finalization-ack-node-quality.log`. Moving receipt validation into the neutral package changes
  the host package coverage denominator; Linux-only storage/cleanup behavior is verified separately.
  Full Linux amd64 vet passed: `/tmp/finalization-ack-linux-vet-final.log`.
- Host worker/API/skillmanager/runtimehelper race tests passed:
  `/tmp/finalization-ack-race.log`. A later receipt-validation simplification and Linux duplicate-ACK
  directory-sync optimization were covered by the final full gate and Linux gate below.
- Expanded isolated Linux storage/Helper/worker proof passed:
  `/tmp/finalization-ack-linux-final.log`. Storage tests retain exact original receipts, resume after
  acknowledgement-only/partial state progression, reject changed authority and linked/hardlinked/
  unsafe acknowledgement files, prohibit persistence-only cleanup and bind cleanup markers to the
  original runtime root. These are interruption-state tests, not physical power-loss simulations.
- Real Helper socket tests cover published/conflicted/detached acknowledgements and cleanup while
  preserving work/frozen content, superseded refusal, exact replay, reappearing-root protection,
  active units/populated cgroups, changed spec/Node/boot, unknown network inventory and linked tmp.
  The actual worker/HTTP-fixture/private-store/Helper integration now acknowledges the root journal,
  retains cleanup completion and reconstructs terminal receipts even after removing the worker ledger.
  Worker tests separately lose Helper replies at upload_pending, persisted, published and cleanup;
  they recover without republishing already acknowledged Server data.
- The complete isolated systemd lifecycle/copy/migration/startup recovery/cancellation suite passed:
  `/tmp/finalization-ack-systemd.log`. All six real Native lifecycle cases now use the actual Helper
  acknowledgement and cleanup socket operations instead of test-only direct journal transitions.
  They verify transient-root removal and retrieve the real test tool's learned bytes after work
  removal. The Server receipt remains an explicit fixture, so this is not yet a complete real
  Server-database-to-real-Claude end-to-end acceptance claim. The disposable containers/images and
  temporary crosscompiled artifacts were handled by the scripts' cleanup traps.
- Root and Node whitespace checks passed. Node README EN/CN, architecture/state/control rules and the
  root wire protocol were updated to distinguish worker receipts, root acknowledgements, transient
  cleanup and retained content.

Next required work includes natural-exit/restart lifecycle reconciliation, already-confirmed runtime
handling after broker restart and complete cross-boot writer/cleanup proof. Normal stop's bounded
save wait and operation reporting still need complete Server/worker acceptance. Takeover initiation/
dispatch, durable deployment attempts and retry APIs/CLI, Docker managed lifecycle, interrupted account
migration recovery, Node-only pending export, reference-aware local content reclamation and the full
design requirement audit remain incomplete. The goal stays active. No capability advertisement,
commit, release or deployment was performed.

## 2026-09-23 — same-boot natural-exit reconciliation

The independent Native finalization loop now invokes a separate `reconcile_skill_session` Helper
operation for each not_finalized inventory candidate, then transfers any newly frozen capture through
the existing durable receipt/acknowledgement/cleanup pipeline. Inventory itself remains read-only.
The worker never reports a partial inventory page as a complete Server runtime session snapshot.

The exact request contains only configured Node and canonical session identity; the exact response
contains session_id, state and an explicitly nullable record. States are not_started, running and
finalized. Invalid or uncertain state returns the bounded FINALIZATION_PENDING error. The handler
owns a 30-second cancellation scope, disconnect reader and cancellable mutation lock; the typed
client closes on cancellation and preserves full integer generations. Worker errors remain bounded,
and per-session failures do not starve later page entries.

Session-addressed launch discovery reads the original private launch using the verified prepared
bundle, validates all owner/task/snapshot/backend identities and original boot/unit, and revalidates
its ready spec intent and immutable draft. Only absence of the launch filename means not_started;
missing or linked authority inside an existing launch remains an error. Starting records and launches
from another boot cannot trigger capture. The Helper additionally validates the draft's preparation
digest, original managed request identity and UID/GID against the retained preparation. No transient
spec is recreated and no launch command is replayed.

For completed same-boot launches, one bounded systemd query reads unit state, invocation, transient
identity, user and cgroup together. Loaded replacement invocations and contradictory observations
fail. A running result additionally requires the original spec files and verified work mount; this
observation is not broker admission or a Server readiness acknowledgement. Natural exit requires a
stable repeated unit observation and empty whole cgroup before releasing an already-exited original
RemainAfterExit service. A second stopped-unit/cgroup proof precedes the common frozen-object capture.
Running, transitioning, populated and replacement units are never drained by this operation.
Successful original exits are clean; failed or absent units are unclean, subject to the immutable
previous termination receipt. Existing frozen captures replay unchanged without private launch drafts
or transient specs. This increment does not change Server terminal authorization.

Verified evidence:

- Full Node quality gate passed with **61.1% host statement coverage**:
  `/tmp/skill-reconciliation-node-quality.log`. Final Linux amd64 vet passed:
  `/tmp/skill-reconciliation-linux-vet-final.log`.
- Host worker/Helper race tests passed: `/tmp/skill-reconciliation-race.log`.
- Expanded isolated Linux storage/Helper/worker suite passed:
  `/tmp/skill-reconciliation-linux-final.log`. Actual Helper socket tests cover clean/error/missing
  units, missing transient specs, immutable frozen replay after draft removal, pending starting
  records, missing/linked authority, replacement invocation, populated cgroup, foreign Node and
  running-without-mount refusal. Protocol tests reject noncanonical fields and prove cancelled lock
  waits terminate. Worker tests verify newly frozen input enters the full existing transfer pipeline,
  while unfinished or foreign observations never upload or clean data.
- The real systemd original-runtime test now uses the new Helper operation while running and after
  natural exit, deliberately removes spec.json before capture, then uses actual Helper socket
  acknowledgement and guarded cleanup. It verifies no duplicate tool execution or historical replay
  relaunch. The Server publication receipt is still an explicit fixture, and the tool is synthetic;
  this is not a complete real Server/Claude acceptance claim. Targeted proof passed:
  `/tmp/skill-reconciliation-systemd-final.log`.
- The full isolated systemd lifecycle/copy/migration/startup recovery/cancellation suite also passed:
  `/tmp/skill-reconciliation-systemd-suite.log`. Its six existing Native lifecycle cases continue to
  pass after the shared unit-reader change. The scripts removed disposable test resources via traps.
- README EN/CN, Node architecture/state/control rules and the root wire contract were updated.
  Root and Node whitespace checks passed. No Server or CLI code changed in this increment.

Next required work remains exact Server terminal reporting (without treating a partial page as a
complete runtime inventory), already-confirmed broker restart handling and cross-boot writer/cleanup
proof. Normal-stop bounded-save reporting, complete real Server/worker/Claude acceptance, takeover
initiation/dispatch, durable deployment attempts and retry APIs/CLI, Docker managed lifecycle,
interrupted account migration recovery, Node-only pending export, reference-aware local reclamation
and the full design audit are still incomplete. The goal remains active; no capability advertisement,
commit, release or deployment was performed.

## 2026-09-23 — exact Server termination observation before background upload

The Native background transfer path now reports one frozen session's exact termination before its
first upload. It no longer waits for the independent full runtime inventory to make the Server
session terminal. The request cannot mark unreported sessions missing, restore broker admission or
substitute stopped acknowledgement for complete persistence/publication.

Server migration 0048 adds one immutable `skill_snapshot_terminations` receipt per original snapshot,
retaining the incoming tree digest and unclean flag. All original owners, task/session references,
initial tree and generations remain on the immutable snapshot and are revalidated on every request.
The receipt has no content foreign key; pending bytes remain protected by the finalizing snapshot.
The schema is classified in the retention reference registry, has no cascade deletion/backfill, and
refuses downgrade once receipts exist. The contract is in Server `docs/skill-session-termination.md`.

`POST /api/v1/node/skill-snapshots/{snapshot_id}/termination` accepts exactly session_id, task_id,
initial_tree_digest, directory_epoch, library_generation, incoming_digest and unclean. Authentication
selects the Node; the original Native snapshot and canonical managed task pointer establish owners.
The original task-record identity is required, but its startup lease need not remain active. The
existing user retention, session and task locks serialize this observation against startup results.
Unaccepted nonterminal create tasks become cancelled without inventing a startup result. Accepted
startup results remain historical and cannot revive the stopped session. Nonterminal sessions become
stopped for clean exit or interrupted for unclean exit; existing terminal statuses remain unchanged.
Reserved/started snapshots become finalizing. Device/browser revocation shares the transaction;
connection closure and outbox delivery follow commit. Replays preserve the original receipt and do
not reapply lifecycle transitions, including after session-view deletion.

An existing finalization must match the termination observation. Conversely, a new or renewed begin
cannot change a retained termination digest/classification. Legacy terminal-session finalizations
remain readable without inventing historical termination receipts. The new committed stopped envelope
echoes all seven original fields and is separate from content persistence. Helper writer proof remains
the authenticated Node's responsibility; this is not cryptographically signed kernel evidence.

Node `internal/api` now sends and strictly validates this exact receipt, including 64-bit generations,
canonical fields, boolean classification and no redirects/automatic uncertain-write retry. The worker
persists its full original capture before sending termination. A lost stopped response retries that
same input and cannot begin upload. No new local ledger phase is necessary: a known upload already
passed Server terminal authorization, and saved publication retries still touch only Helper ACK and
cleanup. The frozen capture, original manifests and objects remain retained on every failure.

Verified evidence:

- Node full quality gate passed, **61.2% host statement coverage**:
  `/tmp/skill-termination-node-quality.log`. API/worker race passed:
  `/tmp/skill-termination-node-race.log`. Full Linux amd64 vet passed:
  `/tmp/skill-termination-linux-vet.log`.
- Expanded isolated Linux storage/Helper/worker suite passed:
  `/tmp/skill-termination-linux.log`. The actual worker/private-store/Helper/HTTP-fixture path includes
  the new pre-upload termination exchange. Worker tests lose its reply and recover after reopening
  the ledger without uploading before confirmation or replacing original input.
- PostgreSQL tests passed **82/82**, including exact termination, startup/inspection/lease contracts,
  and concurrent startup/termination, identical observation and conflicting observation races:
  `/tmp/skill-termination-postgres.log`. This disposable database was migrated from the initial schema
  through 0048, downgraded to 0047 while empty, upgraded again, and refused nonempty downgrade while
  retaining the 0048 head. The script removed its disposable PostgreSQL container.
- Real Uvicorn-to-Go transport passed all four clean/unclean and first/expired-upload scenarios:
  `/tmp/skill-termination-live-wire.log`, using `/tmp/verify-skill-termination-wire.py`. First-upload
  cases begin with a Server-confirmed running session and use Go's exact termination client before
  upload, persistence and publication. Inputs are synthetic frozen manifests, not an actual
  Helper/systemd/Claude runtime. The expired-upload cases replay an already accepted termination.
- Additional Server terminal/deletion/security tests passed **19**, with **3** PostgreSQL-only
  concurrency tests skipped on SQLite (covered by the PostgreSQL run above):
  `/tmp/skill-termination-server-security-final.log`. They cover foreign Node/inactive owner/changed
  pointer/generation refusal, late readiness, device revocation and injected browser-revocation
  rollback, unrelated-session preservation, pending-content deletion refusal and post-publication
  session-view deletion with retained termination replay.
- The full Server quality gate passed: **1401 passed, 55 skipped**, **82.31% coverage**, followed by
  successful docstring and whitespace checks: `/tmp/skill-termination-server-quality-final.log`.
  Its first run found the new table missing from the exact metadata-table test inventory; that
  inventory was corrected without changing production behavior before the complete gate rerun.

Full broker restart handling and cross-boot writer/cleanup proof remain next. Normal-stop operation
reporting, complete real Server/worker/Helper/systemd/Claude
acceptance, takeover initiation/dispatch, durable deployment attempts and retry APIs/CLI, Docker
managed lifecycle, interrupted migration recovery, Node-only pending export, reference-aware local
reclamation and the complete design audit remain required. The goal remains active. No capability
advertisement, commit, release or deployment was performed.

## 2026-09-23 — same-boot broker admission loss drains the original runtime

The independent Native finalization reader now checks original process-local browser admission for
running observations. `Worker.New` owns a shared cancellable gate and session/nonce/UID registry, so
value-receiver Worker copies cannot race startup against a background missing-grant decision. Startup
holds this gate through preparation, initial authorization, launch and confirmation, recording its
initial successful grant before releasing ownership, including uncertain outcomes. Recovery checks
the retained original grant and cannot populate the registry. Historical Server readiness and a later
registration cannot supply original process authority; even an independently authorized replacement
nonce fails original-grant recovery. No nonce or admission map enters persistent storage.

For a running observation whose exact original grant is unavailable/revoked/changed, the reader calls
the separate `drain_unadmitted_skill_session` Helper operation. Its exact Node/session request and
session_id/state/nullable-record response reuse reconciliation's strict protocol and 30-second
cancellation/serialized mutation boundary. The local worker asserts admission loss; this is delegated
trusted-worker authority, not cryptographic evidence from the broker. The Helper independently loads
the original private launch, ready draft and prepared bundle, and requires a sealed same-boot Native
invocation. Only a retained browser-enabled runtime may be drained; a disabled runtime remains running
after normal spec/mount validation. A new runtime or broker grant is never created.

Drain uses common Native graceful exit and final stop, additionally checking the original invocation,
transient identity, user and canonical cgroup at each unit inspection, including after the graceful
attempt and after stop. Replaced/unknown units and surviving whole-cgroup writers cannot authorize
capture. The common finalizer retains proven clean/unclean classification and original frozen replay.
The existing worker pipeline then confirms exact Server termination, uploads and publishes the capture,
acknowledges Helper retention and performs guarded transient cleanup. Errors preserve original data.
Frozen inventory/observations retire only the matching nonce; later registrations are not revoked by
stale cleanup. Not-started observations also retire obsolete initial admission, so failed preparation
does not leave its unused grant in the registry indefinitely.

Verified evidence:

- Full Node quality gate passed with **61.3% host statement coverage**:
  `/tmp/skill-admission-node-quality-final.log`. Worker/Helper race tests passed:
  `/tmp/skill-admission-race-final.log`. Linux amd64 vet passed:
  `/tmp/skill-admission-linux-vet.log`.
- Expanded isolated Linux storage/Helper/worker suite passed:
  `/tmp/skill-admission-linux-final.log`. Helper socket tests cover original forced exit and immutable
  replay, disabled runtime refusal without a verified mount, replacement invocation (including one
  appearing during graceful inspection), populated cgroup, missing draft and foreign Node. Protocol
  tests reject changed/aliased/duplicate/null/extra response fields and cancelled mutation-lock waits.
- Worker tests use the actual broker with fixture Helper/HTTP transport to exercise original grants,
  empty restarted registry, revocation, replacement registration/grant, changed UID, disabled browser,
  uncertain drain and the full new-capture transfer pipeline. Concurrent background inspection waits
  for startup ownership and cannot drain its new grant; cancellation releases blocked waits. Final
  host/race tests additionally cover not-started retirement and frozen-inventory retirement preserving
  a later nonce. No extra peer grants are issued during recovery.
- The complete isolated systemd lifecycle/copy/migration/startup recovery/cancellation suite passed:
  `/tmp/skill-admission-systemd-suite.log`. Its added actual Helper/socket/systemd/tmux/Bubblewrap case
  proves disabled runtimes stay running and enabled lost-admission runtimes stop with an empty cgroup,
  retain one execution's bytes as unclean, replay the same capture, and clean transient resources only
  after acknowledged retention. Targeted proof: `/tmp/skill-admission-systemd-target4.log`.
  The test uses a synthetic terminal tool and wrapper plus fixture Server acknowledgement; it does
  not claim real Claude, real broker relay traffic or a complete real Server/worker/systemd flow.
  Initial enabled-fixture failures exposed private fixture artifact permissions; fixture traversal
  and readonly tree permissions were corrected without weakening runtime verification. Disposable
  containers/images and temporary binaries were removed by the scripts' cleanup traps.
- Root wire contract, Node README EN/CN and architecture/state/control rules were updated. Root,
  Server and Node whitespace checks passed. All verification tool handles ended. Server changed
  only its metadata-table expectation to finish the preceding increment; CLI did not change.

Starting records, cross-boot writer proof and interrupted transient cleanup remain incomplete;
same-boot original admission recovery does not relax those boundaries. Pending startup proposals
cancelled by termination also need explicit local convergence without inventing accepted readiness.
Next work remains cross-boot recovery, normal-stop bounded-save/operation reporting, complete real
Server/worker/Helper/systemd/Claude acceptance, takeover initiation/dispatch, durable deployment target
attempts and retry APIs/CLI, Docker managed lifecycle, interrupted account migration recovery,
Node-only pending export, reference-aware local reclamation and the complete design audit. The full
goal stays active and incomplete. No capability advertisement, commit, release or deployment occurred.

## 2026-09-23 — passive Native recovery across kernel boot identities

Retained prepared Native bundles now recover after a valid current kernel boot differs from their
immutable original boot. The existing reconciliation/drain wire shapes remain unchanged. Original
ready-spec discovery covers preparation before launch intent; absent, starting and started launch
phases can recover. An existing corrupt launch, missing private authority, changed owners/task/input,
runtime UID/GID or configured runtime root remains pending. Same-boot starting records still use
their existing conservative recovery boundary.

Helper loads the original digest-verified private draft and proves current resource absence twice
under its mutation lock. The current boot must remain valid/distinct. The original unit must be
genuinely absent (loaded inactive/failed units are also refused), the complete canonical cgroup must
be absent, and bounded successful network inventory must contain no original namespace. Existing
transient spec bytes must exactly match their original publication, while a missing spec is allowed.
No current wrapper installation is required to recover the original data.

Canonical resource paths reject symlink ancestors. Bounded kernel mount parsing decodes escaped
paths, checks numeric identities and rejects malformed/truncated/excessive input. Recovery refuses
mounts at/below runtime root or work and filesystem-root/device aliases of those trees or ancestors
elsewhere in the Helper namespace. This assumes the existing trusted Helper is the sole privileged
runtime/mount controller: a genuine reboot excludes original processes/descriptors/namespaces, and
serialized Helper mutation excludes replacement managed mounts while proof/capture runs. It is not
an orphan-process proof for Docker or an untrusted privileged actor outside the Helper.

The common finalizer captures new reboot input as unclean. An already retained termination or frozen
record preserves its original classification/input, including clean termination before an interrupted
capture. Manual Native stop and cleanup_resources route previous-boot retained bundles through passive
recovery before loading transient artifacts. Common managed stop now refuses old/unavailable boot
identity before issuing commands, preventing delayed cancellation/stop from targeting a new unit.
Previous-boot proof never stops/signals/releases a unit, deletes a namespace or unmounts resources.

After normal exact Server termination/upload/publication and Helper acknowledgement, previous-boot
transient cleanup repeats the same passive proof and original private authority checks. It removes
only the obsolete unmounted runtime root, syncs its parent and writes the existing completion receipt.
Missing transient spec and interrupted directory removal can resume; work/frozen objects stay retained.
Completed replay refuses reappearing roots and, across another boot, current runtime resources.
No schema migration, new persistent reboot marker or guessed historical receipt was introduced.
The detailed authority/proof/cleanup contract is Node `docs/skill-runtime-recovery.md`.

Verified evidence:

- Full Node quality gate passed with **61.4% host statement coverage**:
  `/tmp/skill-reboot-node-quality.log`. Worker/Helper race tests passed:
  `/tmp/skill-reboot-race.log`. Full Linux amd64 vet passed:
  `/tmp/skill-reboot-linux-vet-final.log`.
- Expanded isolated Linux storage/Helper/worker suite passed:
  `/tmp/skill-reboot-linux-target2.log`. Actual Helper socket tests cover prepared/starting/started
  earlier-boot records, missing transient specs, immutable frozen replay, premature-cleanup refusal,
  unclean capture, retained clean termination, manual stop, and interrupted removal without a cleanup
  marker. Captures survive work removal; completed replay refuses a new runtime root. Negative tests
  cover present/running/inactive units, surviving cgroup, present/unknown network, changed spec,
  linked runtime/work, corrupt launch and missing draft; manual stop cannot bypass the same refusal.
- Host/Linux parser tests cover mounted roots/descendants, separate filesystems, exact/child/parent
  bind aliases, escaped paths, sibling-prefix distinctions, invalid escapes/device/IDs, duplicate
  IDs, truncation, bounds and cancellation. Existing host natural-exit tests now explicitly verify
  refusal when kernel boot identity is unavailable; Linux still exercises actual exit classification.
- The complete isolated systemd lifecycle/copy/migration/startup recovery/cancellation suite passed:
  `/tmp/skill-reboot-systemd-final.log`. Added kernel mount tests use actual systemd/network inventory
  and bind mounts of work, a work child, the private bundle, runtime tmp and runtime root. Both capture
  and acknowledged cleanup refuse current mounts without removing them; recovery succeeds only after
  explicit test-owned unmount. Targeted proof passed: `/tmp/skill-reboot-mounts2.log`. The initial
  mount fixture's temporary executable was unavailable in the systemd environment; the fixture was
  corrected to use actual systemctl/ip/cgroup inventory before the full suite rerun. No production
  inspection was weakened. Disposable containers/images and test binaries were removed by traps.
- Node README EN/CN, architecture/state/control rules and root wire contract were updated. Root and
  Node whitespace checks passed. All verification jobs ended. No Server or CLI code changed.

The tests construct coherent earlier-boot disk records; they do **not** reboot a kernel or simulate
physical power loss. Actual kernel-reboot acceptance and the complete real Server/worker/Helper/
systemd/Claude flow remain required. Further work includes same-boot starting recovery, explicit
retirement of startup proposals cancelled by termination, normal-stop bounded-save/operation reporting,
takeover initiation/dispatch, durable deployment attempts and retry APIs/CLI, Docker managed lifecycle,
interrupted account migration recovery, Node-only pending export, reference-aware local reclamation
and the complete design audit. The full objective remains active and incomplete. No capability
advertisement, commit, release or deployment was performed.

## 2026-09-23 — retire exactly cancelled startup proposals

Node now durably converges an unaccepted startup proposal after exact Server inspection reports
`task_status=cancelled`, the unchanged original outcome, `accepted=false`, and a current attempt at
least the proposed attempt. Cancellation is serialized with startup acceptance by existing Server
locks; a cancelled managed create task cannot be polled or subsequently accepted. Pending/live/expired
observations remain pending. A newer live attempt still uses the existing leased runtime recovery
before it may replace an older proposal.

The distinct `managed_start_retired` ledger state preserves the original schema-1 binding/outcome
and adds `retirement` containing the full exact observation. Existing pending/confirmed payloads are
unchanged. Strict decoding rejects missing/null/extra/aliased, mismatched, accepted, older or noncancelled
evidence. Full-entry CAS prevents late observations from replacing a newer or confirmed proposal;
identical concurrent retirement is idempotent. Failed persistence retains the pending proposal
and reports pending, never a completed local retirement.

Background inspection retires these entries without task redelivery. Retired entries leave that
queue and reject later startup replay before broker registration, lease renewal, Helper recovery,
preparation or launch. They remain excluded from generic task execution/result replay. Retirement
never marks readiness accepted, fabricates a task result, or grants content/runtime deletion.
The independent finalization ledger and its capture/termination/upload/publication/acknowledgement
requirements remain authoritative. A stale startup publisher seeing a retired entry cannot resend
its outcome; a confirmation already in flight is fenced by Server cancellation.

Verified evidence:

- Node worker/API targeted suites passed: `/tmp/skill-start-retirement-target.log`.
- Full Node quality gate passed, **61.5% host statement coverage**:
  `/tmp/skill-start-retirement-node-quality-final.log`. Worker/API/ledger race suites passed:
  `/tmp/skill-start-retirement-race-final.log`.
- Tests exercise exact evidence, reopen, concurrent retirement, stale confirmation/replacement,
  pending/live/expired observations, write failure, corrupt evidence, generic-dispatch exclusion,
  and absence of Helper/peer operations. Actual Go HTTP client plus worker inspection persists a
  cancelled proposal and performs no further HTTP work after reopen or delayed valid task replay.
- Server termination tests now assert the exact inspection envelope for clean/unclean termination,
  preserving accepted historical readiness or reporting the unaccepted original proposal cancelled,
  followed by late-confirmation rejection and independent finalization. Targeted SQLite suites:
  **28 passed, 4 skipped**, `/tmp/skill-start-retirement-server-target.log`.
- Isolated PostgreSQL termination/start-result/lease/inspection suite: **84 passed**,
  `/tmp/skill-start-retirement-postgres.log`; existing migration upgrade/empty downgrade and nonempty
  downgrade refusal also passed. The disposable database container was removed by the cleanup trap.
- Full Server quality gate passed: **1401 passed, 55 skipped**, **82.31% coverage**, Ruff, Mypy
  (503 source files), Chinese docstrings and whitespace checks:
  `/tmp/skill-start-retirement-server-quality.log`.
- Root wire contract, Node README EN/CN and architecture/state/control rules were updated. Root and
  Node whitespace checks passed. All verification jobs ended. Server changed only the termination
  test assertions; no Server production code, Helper code or CLI code changed in this increment.

Same-boot starting reconciliation, real kernel-reboot acceptance, bounded normal-stop save/operation
reporting, complete Server/worker/Helper/systemd/Claude acceptance, takeover initiation/dispatch,
durable deployment attempts and retry APIs/CLI, Docker managed lifecycle, interrupted migration,
Node-only pending export, reference-aware local reclamation and the complete design audit remain.
The full objective stays active and incomplete. No managed capability advertisement, commit,
release or deployment occurred.

## 2026-09-24 — same-boot interrupted startup observation and finalization

Retained Native starting launches now converge without another launch request. A stable loaded unit
must match the original private ready draft/prepared binding, same kernel boot, canonical nonzero
invocation, transient service, original runtime user and cgroup. Running units additionally require
the original published spec and unchanged work/system mounts. Exited units require whole-cgroup
quiescence; their transient spec may be absent, but changed existing bytes are rejected. Removed
runtime artifacts do not prevent exited-data recovery.

An additive schema-1 launch phase, `observed`, durably pins that invocation before running observation
or exited-unit release. It is distinct from `started`: no historical readiness, Server acceptance or
broker grant is manufactured. Existing starting/started records remain readable unchanged; older
binaries must not process the new phase. Observed/started invocation identity cannot change; exact
observation/readiness replay re-syncs the parent after possible rename uncertainty. Leased recovery
also pins an unobserved invocation before waiting for current readiness, so cancellation cannot later
adopt another invocation. Only verified readiness promotes that same invocation to started.

Background running observations retain the existing original process-owned admission check. Missing
or revoked grants drain the original browser-enabled invocation and preserve data; browser-disabled
runtimes remain running. Stable natural exits share existing whole-cgroup proof and finalization.
Missing starting units require repeated absence and complete cgroup quiescence before unclean capture.
They cannot become historical readiness or be relaunched. Existing termination/frozen records keep
their original classification and bytes. Unknown/transitional/changed state remains pending.

Common managed stop now discovers private authority and the same invocation across manual stop,
cleanup_resources, cancellation, failed-start cleanup and missing transient specs. An unobserved
loaded starting unit must first pass the same observation checks. Absent unit observations use an
absence-only fence through stop; a newly loaded unit cannot match it. A prepared bundle without a
launch intent cannot authorize stopping a loaded service. Original pre-streaming internal bundles
without task-bound launch authority retain their compatibility path. First observation assumes the
Helper remains the sole privileged runtime controller; it is not proof against an independent
malicious root administrator creating a matching service.

Verification:

- Full Node quality gate passed, **61.6% host statement coverage**:
  `/tmp/skill-start-recovery-node-quality-final.log`; Helper/worker/skillmanager race suites passed:
  `/tmp/skill-start-recovery-race-final.log`. Final Linux amd64 vet passed:
  `/tmp/skill-start-recovery-linux-vet-verified.log`.
- Isolated Linux copy/storage/Helper/worker suite passed:
  `/tmp/skill-start-recovery-linux-complete.log`. Tests cover observed-phase persistence/reopen,
  immutable invocation, readiness promotion, phase compatibility, clean/failed/absent starting exits,
  missing transient specs, no relaunch, bad user/transient/cgroup/invocation, changed spec/draft,
  populated cgroups, absent live mounts, unstable unit observations, replacement refusal even without
  a transient spec, and absent-intent/absent-unit inability to authorize stopping a loaded service.
  Previous-boot simulations now also include observed launch records.
- Actual systemd targeted tests passed for starting/started x browser-enabled/disabled admission
  recovery, no duplicate execution, and leased readiness completion:
  `/tmp/skill-start-recovery-systemd-target.log`. Actual clean/SIGKILL exit tests passed:
  `/tmp/skill-start-recovery-systemd-exit.log`. The subsequent complete systemd suite also covered
  missing transient specs for both exits, retained capture, acknowledgement and cleanup:
  `/tmp/skill-start-recovery-systemd-complete.log`.
- Final complete systemd run covering the last leased-recovery pin-before-wait change passed:
  `/tmp/skill-start-recovery-systemd-verified.log`. Every verification handle ended; disposable
  containers/images and binaries were removed by cleanup traps. No Server or CLI code changed.
  Root wire, Node README EN/CN, recovery contract and architecture/state/control rules were updated.
  Root and Node whitespace checks passed.

These tests use real isolated systemd, cgroups, mounts and Helper sockets with synthetic tools; they
are not real Claude or kernel-reboot acceptance. Bounded normal-stop save/operation reporting, real
Server/worker/Helper/systemd/Claude acceptance and kernel reboot, takeover initiation/dispatch,
durable deployment attempts/retry APIs/CLI, Docker managed lifecycle, interrupted account migration,
Node-only pending export, reference-aware local reclamation and complete design audit remain. The
full objective stays active and incomplete. No capability advertisement, commit, release or deployment.

## 2026-09-24 — bounded Native stop saving and durable owner status

Managed stop now connects process quiescence, frozen input, bounded saving and independent status
across Node, Server and CLI. New `stop_tool_session:<session UUID>` tasks carry a distinct
`skill_finalization` pointer with original snapshot/preparation/user/account identity. Native dispatch
rejects malformed/case-alias markers outside generic permanent failure caching. After task start
reporting, the worker stops the original writers and requires exact full object-backed reconciliation;
a generic Helper stop map, historical stop replay or absent runtime spec cannot prove data saving.

The immediate saving attempt is bounded to 10 seconds after freezing, including transfer-gate wait.
Worker copies and background inventory now share one pointer-owned coordinator, cancellable gate and
lazy-opened finalization ledger. Two independently mutable ledger instances cannot overwrite each
other. Stop releases runtime admission ownership before waiting for this gate, preserving the
background transfer/admission lock order. Root-owned frozen input remains the recovery source on
network, ledger-open or timeout failure; independent inventory resumes the same capture and key.

Task completion retains only the immutable six-field stopped result: status, original session,
Native backend, snapshot operation ID, incoming digest and unclean classification. Server identifies
managed stop from the original logical session identity as well as persistent snapshots, even when
the task marker is removed. Missing/changed payload session IDs cannot bypass the guard. Completion
requires the separately committed original termination observation; mismatched or failed reports do
not consume the task or release retention protection. Exact receipt replay checks the original task
record/status and has no session lifecycle side effects. Unclean completion preserves interrupted.
The old retention-clock tests now use valid frozen evidence for completion and assert that rejected
failure reporting keeps history protected.

The original snapshot UUID is the durable finalization operation ID. Single-session create/detail/
current-project/stop responses expose it through nullable `skill_finalization_operation_id`.
`GET /api/v1/sessions/skill-finalizations/{operation_id}` uses existing session user/device credentials,
rejects Node credentials and authorizes the immutable snapshot owner after session deletion. It is
metadata-only and remains available when new managed admission is disabled. One SQL statement reads
snapshot, termination, incoming finalization, latest publication and optional display session.
`awaiting_node` is honest lack of frozen evidence; local_durable/upload_pending/persisted/
persisted_unclean/published/conflicted/detached/superseded remain separate. Exact process confirmation,
current display-session status, incoming checkpoint, latest publication and content retention are
separate fields. Retired content never becomes available merely because an old publication succeeded.

`fclaude stop SESSION [--timeout 60]` prints the original operation ID before bounded managed saving
wait. `fclaude stop-status OPERATION_ID [--wait] [--timeout 60]` re-queries with the same device login,
including after display-session deletion. One retained Ctrl+C future and deadline cover all saving
status HTTP requests and polling. Exit codes follow design: published 0; ordinary non-waiting pending
query 0; timed-out wait 3; conflicted/detached/superseded review or HTTP/identity errors 1; interruption
130. Waiting success also requires exact process-stop confirmation. The CLI validates operation and
session identity and required phase/checkpoint/publication metadata before displaying success.
Legacy stop remains an immediate request. No status query submits another stop or upload.

Verification:

- Final full Server quality gate passed: **1409 passed, 55 skipped**, **82.27% coverage**, Ruff,
  Mypy, Chinese docstrings and whitespace: `/tmp/skill-stop-server-quality-final.log`.
  An earlier full run found two outdated retention-clock expectations; both were corrected to the
  new evidence boundary and included in this final clean full run.
- Broad PostgreSQL lifecycle validation passed **92 tests**:
  `/tmp/skill-stop-server-postgres.log`. Final PostgreSQL stop/status/retention-clock validation passed
  **21 tests**: `/tmp/skill-stop-server-postgres-final.log`, including latest-publication ordering,
  exact replay, user/device/Node authorization, pending deletion refusal and post-delete status.
  Existing migration upgrade/empty downgrade and recorded-termination downgrade refusal also passed;
  the schema remains `0048_skill_terminations`. Disposable databases were removed by cleanup traps.
- Final full Node quality gate passed with **61.7% host statement coverage**:
  `/tmp/skill-stop-node-quality-final.log`. Worker race suite passed:
  `/tmp/skill-stop-node-race.log`. Linux amd64 vet passed:
  `/tmp/skill-stop-node-linux-vet-final.log`. Isolated Linux copy/storage/Helper/worker tests passed:
  `/tmp/skill-stop-node-linux.log`; the script includes the new stop/gate tests.
  Tests verify strict dispatch, no transient failure caching, exact frozen identity, shared-ledger
  cancellation, timeout retention/background resume, and stop-result replay with an unavailable Helper.
- Full CLI quality gate passed, including **534 test executions**:
  `/tmp/skill-stop-cli-quality.log`. Subsequent response-invariant and exit-code refinements passed
  the final **7** launcher contract tests: `/tmp/skill-stop-cli-contract-final.log`, with final
  formatting, Clippy and whitespace verification: `/tmp/skill-stop-cli-clippy-final.log`.
  Contracts cover persisted-to-published waiting, timeout during HTTP, Ctrl+C, legacy behavior,
  read-only status, review exits, unknown Node evidence and rejection of false publication metadata.
- Root wire contract, Server stop-status contract, Node architecture/state/control rules, CLI control
  rules and all affected README EN/CN files were updated. No managed capability, commit, release or
  deployment was introduced.

## 2026-09-24 — real ARM64 kernel power-cut recovery acceptance

Added `agent-remote-node/tests/linux_skill_kernel_reboot_test.sh` and the opt-in
`TestManagedSkillActualKernelReboot`. The runner compiles the current Helper and Linux test binary,
builds a disposable Debian/QEMU image, creates a private raw ext4 guest disk, and runs two actual
kernels under TCG. It uses an unprivileged Docker container without host devices, KVM, exposed ports
or guest network. Both architecture branches are implemented; this environment verified ARM64.

The first guest starts a real managed Native systemd/bubblewrap/tmux runtime with the existing
synthetic tool. That tool writes `executions=entered` through its private writable Skill mount and
remains running. After guest disk sync, the outer runner SIGKILLs QEMU: no guest shutdown or
finalization hook executes. The second kernel boots the same disk with a different actual boot ID,
then uses the Helper protocol to recover the original snapshot as object-backed local_durable and
unclean. Original work remains intact and the execution marker proves no tool replay. Cleanup before
Server retention acknowledgement is refused. A synthetic exact persisted_unclean/detached receipt
permits idempotent transient cleanup and retained reconciliation replay without deleting work.

Actual successful boot IDs were `02388d85-89c5-4942-b6b2-1b0d02783616` and
`b6c9d856-b121-479d-b9ed-de67d6046ea0`; final recovery was detached. Complete proof output:
`/tmp/skill-actual-kernel-reboot.log`. The script exited successfully, and its VM/container/image/
compiled artifacts were removed. Final Node quality and Linux amd64 vet above include the new test
source and shell syntax. Node recovery documentation and README EN/CN describe the verified scope.

This proves actual ARM64 kernel replacement after abrupt VM power loss for a previously running
managed Native session, with real cgroups, mounts and Helper communication. It uses a synthetic tool
and synthetic Server acknowledgement; it is not real Claude or complete real Server/worker transfer
acceptance. The amd64 VM branch remains unexecuted here. Existing prepared/starting/observed phase
and negative resource tests retain their separate simulated-boot/systemd evidence.

The complete design remains active and incomplete: full real Server/worker/Helper/systemd/Claude
acceptance, amd64 VM verification, takeover capture initiation and durable worker dispatch, durable
deployment target attempts and retry APIs/CLI, Docker/sbx managed lifecycle, interrupted account
migration recovery, Node-only pending export, reference-aware local content reclamation/coordinated
restore, and the requirement-by-requirement completion audit remain. No capability advertisement,
commit, release or deployment occurred.

All verification jobs for these increments ended. Final whitespace checks passed in root, Server,
Node and CLI; no owned test containers or kernel-test images remain running or retained.

## 2026-09-24 — Native takeover capture initiation and durable queue recovery

Connected the existing Native takeover proof/capture and transfer machinery through the privileged
`capture_account_takeover` socket operation and the dedicated `takeover_tool_account_skills`
worker dispatch. This completes initiation/dispatch for existing Native reservations, not public
reservation creation, Docker/sbx takeover or capability advertisement.

The Helper accepts the exact original binding and authenticated immutable writer inventory, never
host paths or a caller-supplied writer-proof flag. Existing peer-UID authorization and cancellable
mutation serialization protect capture. Requests allow 4 MiB for at most 10,000 inventory entries;
the five-minute capture bound is cancelled by disconnect, extra input or worker context cancellation.
The handler joins its connection reader before returning. Binding epochs remain int64 across JSON.
The operation bypasses generic result caches, closes the original durable import fence, proves Native
writers quiescent without stop/kill, then creates or reopens the immutable capture. A bounded
`MIGRATION_PENDING` response contains no paths or underlying filesystem error text. Original source
and retained capture are preserved; no new cleanup/rollback authority was added.

Worker dispatch validates the eight canonical payload fields, versions, Native backend, current
poll-attempt range, exact task-record UUID, and Node/logical/idempotency identity before networking.
It refreshes exact Server authorization before Helper access and owns one renewable task lease
through capture and retained transfer. Each distinct digest still streams once. Renewal uncertainty
cancels capture/upload and retains recovery input. Neither transient failure nor a historical generic
worker-ledger outcome can consume the takeover task. Recovery uses the durable Server reservation
and immutable Helper capture instead of opening another mutable worker ledger. Lease expiry reissues
the pending task; an uncertain authority commit is recovered by GET of the same reservation.
Committed replay skips lease renewal, Helper and old-source access.

The completion result contains exactly status=committed, takeover_id, task_record_id,
tool_account_id, original checkpoint_id and capture_digest. Server's new `TakeoverResultGuard`
identifies the persistent task relation even if task_type is altered. It locks the original user and
exact task, revalidates the active owner and exact task payload, requires the independently committed
initial checkpoint and checks the immutable six-field result. Generic failure cannot terminate an
unfinished reservation. Exact saved-result replay has no directory/head side effects; task/result
identity drift or cancellation rejects completion. No migration or new durable format is required.

Tests cover lease maintenance during capture, lease loss before upload, strict task decoding,
no transient failure caching, committed replay with an unavailable Helper and an old failure cache,
actual Unix socket capture/restart/source-change preservation, exact 64-bit epochs, the maximum
inventory, blocked-handler cancellation, malformed receipts and generic Helper-cache bypass.
The real systemd descendant test now uses the new socket entrypoint: capture waits while a surviving
child still owns its cgroup, never stops it, and retains its late write after natural exit.

Verification:

- PostgreSQL takeover/Node HTTP/result validation: **129 passed**,
  `/tmp/skill-takeover-postgres.log`. The disposable PostgreSQL container was removed.
- Node full quality gate: **61.8%** host statement coverage, formatting, vet, tests, installer,
  release/managed-skill contracts and whitespace passed:
  `/tmp/skill-takeover-node-quality-final.log`.
- Worker race suite: `/tmp/skill-takeover-node-race.log`.
- New Helper protocol race tests: `/tmp/skill-takeover-protocol-race.log`.
- Final isolated Linux copy/storage/Helper/worker validation:
  `/tmp/skill-takeover-linux-final.log`.
- Linux amd64 vet: `/tmp/skill-takeover-linux-vet-final.log`.
- Actual isolated systemd descendant proof through the new socket operation:
  `/tmp/skill-takeover-systemd.log`; test image/container removed.
- Server full quality gate passed: **1415 passed, 55 skipped**, **82.32%** coverage, Ruff,
  Mypy, Chinese docstrings and whitespace: `/tmp/skill-takeover-server-quality.log`.

Node/Server architecture, control/persistence rules, takeover contracts and README EN/CN plus the
root wire contract were updated. The full goal remains active and incomplete. Public/automatic
reservation initiation and migration progress still need connection to ordinary account/session
flows. Full real Server→worker→Helper/systemd→Claude acceptance, amd64 VM execution, durable
deployment target attempts/retry APIs/CLI and supersession, Docker/sbx lifecycle and writer proof,
interrupted account migration recovery, Node-only pending export, reference-aware local reclamation
and coordinated restore, and the requirement-by-requirement completion audit remain required.
No commit, release, deployment or managed capability advertisement occurred.

All verification jobs for this increment ended successfully. Disposable test containers/images and
owned temporary runner artifacts were cleaned up; proof logs remain under the recorded `/tmp` paths.

## 2026-09-24 — ordinary Native takeover admission and bounded launcher wait

Ordinary managed session admission now initiates first-use Native takeover on the account's original
bound node. A legacy account without effectively enabled library content keeps its existing path.
When managed admission is required, the existing user lock and session savepoint create or reuse the
original takeover reservation, immutable writer inventory and dedicated capture task. The reservation
is committed before HTTP 409 `MIGRATION_PENDING` explicitly reports `reservation_committed=true` and
`session_created=false`, with the original account, takeover ID and phase. This response creates no
session, startup task, runtime snapshot or effective-use record and never stops an existing session.

Existing reservations must retain their original directory epoch/head, node/backend, task record,
logical task identity, exact payload and active task phase. Missing or inconsistent evidence returns
`TAKEOVER_RECOVERY_REQUIRED`; admission never invents a replacement reservation. An offline original
node cannot be replaced by a healthy node to capture an empty directory. Capability withdrawal before
the pending response rolls back reservation. Committed takeover proceeds through existing full-account
preparation and exact snapshot reservation. Docker first-use takeover remains unsupported.

`GET /api/v1/sessions/skill-takeovers/{operation_id}` exposes owner-scoped metadata using existing
session user/device authentication; Node credentials are rejected. The route remains readable when
new managed admission is disabled. One query observes the original reservation and exact task without
renewing leases, creating tasks, exposing writer inventory or accessing content. Reserved/uploading/
committed authority, task status, original checkpoint and recovery requirement remain distinct.
Committed authority does not regress merely because task-result confirmation is delayed.

`fclaude` now uses one 60-second deadline and retained Ctrl+C handler over its initial session POST,
read-only takeover polling and at most one resumed POST. Only the exact typed HTTP 409 no-session
receipt authorizes waiting. The launcher prints the original operation ID, polls that same operation
and account, and resumes the identical creation request only after committed checkpoint evidence.
Malformed/mismatched progress, recovery-required state or HTTP errors stop the flow. An uncertain
creation response is never replayed automatically; a second pending response does not start another
loop. Timeout exits 3, interruption 130 and other errors 1. New and replacement creation share this
coordinator; existing attach remains unchanged. Documentation explains checking `fclaude list` after
a POST timeout because creation may already have committed.

Verification for this increment:

- Final PostgreSQL admission/session preparation/legacy writer/takeover-result suite: **50 passed**,
  `/tmp/skill-admission-postgres.log`. Actual concurrent ordinary creates share one reservation.
  SQLite tests exercise serial retry; its nested read/write concurrency cannot substitute for
  PostgreSQL row-lock evidence. The disposable PostgreSQL container was removed by its cleanup trap.
- Admission tests preserve manual skill files and SHA-256-verified binary learned state together
  with library content in the first real managed session snapshot. They cover absent reservations,
  changed task/account bindings, unavailable originals, capability withdrawal, disabled admission,
  cross-user and Node denial, device access and read-only status after commit.
- Final CLI full quality gate passed: **545 test executions**, shell/cache/release checks,
  formatting, Clippy with warnings denied and whitespace:
  `/tmp/skill-admission-cli-quality.log`. Its **9** creation contract tests include a real child
  process SIGINT during an outstanding status HTTP request, timeout across HTTP, exact resumed
  input, malformed no-session receipts, cancelled recovery and uncertain resumed POST handling.
- Final Server full quality gate passed: **1432 passed, 56 skipped**, **82.39% coverage**, Ruff,
  Mypy (**518 source files**), Chinese docstrings and whitespace:
  `/tmp/skill-admission-server-quality-final.log`. The first full run found two obsolete expected
  errors in capability tests whose fixtures retained an existing directory head while relabeling
  its mode. They now require HEAD_CHANGED / TAKEOVER_RECOVERY_REQUIRED and verify no new session,
  task, snapshot or takeover reservation. All **15** capability tests passed separately before
  the final clean full gate: `/tmp/skill-admission-capabilities-final.log`.

Root wire contracts, Server architecture/control/persistence and takeover/admission documents,
CLI control rules, Node capture notes and all affected README EN/CN files describe these boundaries.
No schema change, commit, release, deployment or managed capability advertisement occurred.

The full design remains active and incomplete. Complete real Server→worker→Helper/systemd→Claude
acceptance, amd64 VM acceptance, durable deployment target attempts/retries/API/CLI and supersession,
background deployment scheduling, Docker/sbx lifecycle and whole-writer proof, interrupted account
migration recovery and verified rollback, Node-only pending export, reference-aware local reclamation,
coordinated restore and the requirement-by-requirement completion audit remain required.


## 2026-09-24 — amd64 and ARM64 actual kernel recovery acceptance

The disposable VM runner now accepts `AGENT_REMOTE_KERNEL_TEST_ARCH=arm64|amd64` while preserving
Docker host architecture as the default. The guest kernel, Debian userspace and both Go binaries
use the selected architecture. A separate Docker stage runs QEMU natively on the Docker host;
explicit guest and final-image platforms avoid double emulation and ambiguous image selection.
The original guest dependency set is preserved, allowing reuse of previously verified build layers.
A precreated seed log removes a harmless race between QEMU redirection and the observation loop.
No production timeout, runtime behavior, capability report or recovery assertion was weakened.

Final actual two-kernel tests passed for both architectures on the ARM64 Docker host:

- **amd64**: `/tmp/skill-actual-kernel-reboot-amd64-verified.log`. Original boot
  `a563516b-3e86-4c7d-a73c-79b9081e9a6a`; recovered boot
  `044e9e04-8613-41c0-8094-e9f41d5128f3`; final retained state `detached`.
- **ARM64**: `/tmp/skill-actual-kernel-reboot-arm64-verified.log`. Original boot
  `d3bbe45e-9e6f-46ff-add3-904d8288d11a`; recovered boot
  `2c95cf7c-e1e3-4088-9a5f-3d620ee3755c`; final retained state `detached`.

Both runs launched real systemd/bubblewrap/tmux managed Native processes, retained the tool's durable
write across an external SIGKILL of QEMU, recovered without tool replay through the Helper socket,
refused cleanup before retained Server acknowledgement, and replayed acknowledged cleanup while
preserving original work. The tools and Server receipts remain synthetic, so this closes actual
amd64 kernel recovery evidence but does not establish complete real Server/worker/Claude acceptance.

The initial double-emulated amd64 run timed out during Helper startup. Subsequent image builds hit
transient Debian download failures; the split-platform runner and retained guest build layers resolved
those harness/environment issues. An intermediate final-image platform mismatch was corrected before
the successful runs above. Final Node shell syntax and all four repository whitespace checks passed.
All owned VM processes, containers, tagged test images and temporary runner artifacts were cleaned;
evidence logs remain at their recorded paths. README EN/CN and the Node recovery contract now describe
both verified architectures and the explicit synthetic boundaries.

The complete goal remains active and incomplete. Complete real Server/worker/Helper/systemd/Claude
acceptance, durable deployment attempts/retries and supersession, background deployment scheduling,
Docker/sbx lifecycle, interrupted migration recovery and verified rollback, Node-only pending export,
reference-aware local reclamation, coordinated restore and the complete design audit remain required.
No commit, release, deployment or managed capability advertisement occurred.


## 2026-09-24 — durable deployment attempts and original-plan retry

Migration `0049_skill_deployment_attempts` adds a nullable attempt-version marker on original
operations, owner/operation/account-bound attempt chains, and owner-scoped idempotent retry receipts.
New library acceptance records attempt 1 inside its existing savepoint. Historical operations remain
unmarked; current rules never reconstruct missing history. Unbound targets remain stored and bound
targets remain explicitly unsupported. No runtime readiness or managed capability is advertised.

Each attempt preserves the original plan digest, positive sequence and same-target predecessor.
Database foreign keys, checks and uniqueness prevent foreign-owner targets, forks, unknown statuses
and unclassified retryable failures. Status and retention validate complete gap-free chains and
agreement with the operation projection. Unknown historical attempts remain subject to their prior
retention obligations but cannot advertise the new retry authority. Per-target status includes
attempt ID, sequence, retryability and bounded errors. Owner-scoped status holds the existing read
lock and refreshes ORM observations without creating attempts.

Exact retry validates every selected current transient failed attempt, original operation generation,
account ownership/active state, original node/backend/tool binding and still-applicable selection
before appending any pending successor. Successful targets and failed predecessors are preserved.
Unrelated account generations do not invalidate an unchanged original selection. Same-key recovery
returns the original operation even after later success; changed requests, stale attempts, permissions,
conflicts, supersession and changed plans are rejected. Request receipts and all successors commit
atomically. Retry never fetches a source, uploads content, creates a session or authorizes Node work.

Retention now continues rooting original plan content for active targets of a superseded operation;
only the end of every active target releases that operation root. Migration downgrade refuses any
recorded attempt marker, history or receipt before schema mutation. Backups must retain all new
metadata alongside its exact library plans/content; no legacy backfill is performed.

Verification from the completed persistence increment:

- PostgreSQL **76 passed**, including independent-connection same-key concurrency, exact recovery,
  FK/check boundaries, migration upgrade/empty downgrade/re-upgrade and recorded-history downgrade
  refusal: `/tmp/skill-attempts-postgres-final.log`,
  `/tmp/skill-attempts-downgrade-refusal.log`.
- Final focused attempts/retention review **75 passed, 4 skipped**:
  `/tmp/skill-attempts-final-review.log`. This includes active-target retention under supersession
  and the refusal to advertise retryability for unknown historical attempts.
- CLI full gate for per-target status metadata and preparing waits: **548 test executions**,
  `/tmp/skill-attempts-cli-quality.log`.
- The initial Server full gate finished with **1458 passed, 57 skipped, 1 failed**, **82.51% coverage**:
  `/tmp/skill-attempts-server-quality-final.log`. Its sole failure was the expected core-table inventory
  missing the two new tables. That inventory has been corrected. The subsequent complete gate for
  the persistence and public-interface changes is recorded below when finished.

The PostgreSQL container and owned temporary runner were removed; evidence logs remain. Schema 0049
implements durable acceptance, not an actual deployment executor. The complete design remains active.

## 2026-09-24 — public deployment retry and durable CLI recovery

The original operation now exposes `POST /api/v1/skills/operations/{operation_id}/retries` and a
separate read-only `GET` on the same subresource with the retry key. Both use existing live-user
identity and feature gating. POST commits the complete validated selection before responding; GET
requires an actual owner/operation-bound retry receipt and never infers acceptance from current
status or a library acceptance key. Replies preserve the original operation and generation.

`agent-remote skill retry OPERATION_ID` selects only eligible ended transient failed targets from
one original status observation. It supports dry-run, confirmation, no-wait and bounded waiting,
and journals original generation, account/attempt IDs, sequences and plan digests before POST in the
existing user/Server-bound SQLite component. Recovery precedes new selection and looks up the exact
retry receipt first; only absence permits an identical resend. `skill status --last` recognizes the
retry journal and performs only receipt/status reads. No new SQLite schema, credentials, source bytes
or local file paths are introduced. Receipt validation fixes original identity/generation and requires
later attempts on the original plans. Existing library journal compatibility is preserved.

Targeted Server HTTP/persistence checks passed **23 tests**:
`/tmp/skill-retry-api-targeted.log`. They include real commit/query/replay after later success,
changed-key input refusal, cross-user/anonymous/device/disabled-feature rejection, malformed/extra
inputs and all-or-nothing target selection. Runtime task observations in these tests are fixtures;
actual Node dispatch and full Server/worker/Helper/systemd/Claude acceptance remain pending.

Additional direct verification:

- CLI focused regression **46 passed**, including **12** retry contract cases:
  `/tmp/skill-retry-cli-targeted-final.log`. Coverage includes full 64-bit generation preservation,
  exact failed selection, no repeated successful target, missing-versus-lost retry receipt,
  restart before fresh selection, read-only `status --last`, malformed successor/plan/operation
  refusal, noninteractive confirmation, accepted wait timeout and real SIGINT while POST is pending.
  The test observes the exact SQLite request before the Server responds, then verifies restart only
  recovers its receipt. The first broader run caught overly strict parsing of old library journals
  in `status --last`; retry-tag-specific validation fixed that regression without weakening the new
  retry record checks. All existing mutation/update/interruption cases passed in the final run.
- Actual compiled Rust CLI → live loopback Uvicorn Server → disposable SQLite acceptance passed:
  `/tmp/skill-retry-live-final.log`. Dry-run, submission, metadata-only journal, original-key status,
  subsequent success and exact replay share the real HTTP schema. Generation remains unchanged and
  no Node task is created. Initial direct replay used the bootstrap token that normal CLI remembered
  login had revoked; using the current CLI token completed the proof. This was a test-credential
  mistake, not a retry failure. Runtime progress remains fixture-seeded, so this does not establish
  Server/worker/Helper or actual tool deployment acceptance. Temporary server, database, credentials
  and CLI home were removed.

Final quality gates passed:

- Server: **1467 passed, 57 skipped**, **82.51% coverage**, Ruff format/lint, Mypy (**528 source
  files**), Chinese docstrings and whitespace: `/tmp/skill-retry-server-quality.log`. This full run
  includes both final persistence/retention refinements, the corrected core-table inventory and
  the new public retry routes/tests.
- CLI: **560 test executions**, formatting, denied-warning Clippy, shell/cache/release checks and
  whitespace: `/tmp/skill-retry-cli-quality.log`.
- All four repositories passed final whitespace checks and remain on `feature/skill-manager`.
  All owned verification jobs ended; no owned test containers, live test Server or disposable
  credentials remain. Proof logs are retained under the paths above.

The completed increment adds durable attempt history and public exact-request retry/recovery. The
complete goal remains active and incomplete: actual deployment scheduling/task-bound progress and
automatic supersession, complete real Server/worker/Helper/systemd/Claude acceptance, Docker/sbx
managed lifecycle and whole-writer proof, interrupted migration recovery and verified rollback,
Node-only pending export, reference-aware local reclamation, coordinated restore and the full
requirement-by-requirement audit remain required. No commit, release, deployment or managed
capability advertisement occurred.


## 2026-09-24 — automatic deployment configuration supersession

Changed library acceptance now compares its immutable new account plans with older unfinished
operations under the same user lock/savepoint. Comparison ignores only the operation UUID and
configuration generation. The exact node/backend, source/revision/digest, enabled choice and
installation epoch remain significant. Only an actually changed unfinished common target causes
replacement; a mere generation increment cannot replace unchanged pinned or unrelated account plans.
Staging/no-op commands and unknown legacy attempt histories do not create inferred replacements.
Completed successes, stored targets and terminal nonretryable failures remain historical evidence;
changing one of those cannot invalidate another unchanged retryable failure.

The existing operation replacement field records the first newer accepted operation and makes the
parent superseded/nonretryable without rewriting original plans or terminal/current attempt history.
Later replacements do not redirect that first link. Original ID/key lookup and previously accepted
retry-key recovery preserve the original operation and generation. New retries fail superseded.
Late target success cannot turn the parent ready. Active pending/running/conflicted targets remain
content roots until independently ended; supersession is not proof of Node cancellation or drain.

Status and retention validate same-owner, strictly increasing generation, real changed acceptance
and saved common-target selection evidence. Missing, self/backward, foreign, unrelated and no-op
replacement references fail closed. New configuration, replacement markers and reference release
clocks share the existing rollback boundary. No schema migration, Node runtime change or capability
advertisement is introduced. Dedicated modules own candidate queries, saved-plan comparison and
supersession so library orchestration does not absorb another conditional state machine.

Verification so far:

- Focused SQLite deployment suite: **59 passed, 2 skipped**, including replacement/retry/savepoint/
  retention boundaries: `/tmp/skill-supersession-targeted-final.log`.
- Independent PostgreSQL suite: **74 passed**, including retry versus changed-configuration
  concurrency, complete original history, first replacement stability, rollback after real flush,
  and existing retention clocks: `/tmp/skill-supersession-postgres.log`. The owned container and
  temporary runner were removed; unrelated containers were untouched.
- Ruff format/lint, Mypy (**533 source files**) and Chinese docstrings passed before the full gate.

- Existing CLI status contract: **18 passed**, including superseded status/exit/replacement identity:
  `/tmp/skill-supersession-cli-contract-final.log`. An initial concurrent run passed all functional
  assertions but exceeded one existing four-second process timing bound; serial replay passed the
  unchanged test. No CLI production code or test threshold changed in this increment.

- Final Server full gate passed: **1490 passed, 58 skipped**, **82.57% coverage**, Ruff format/lint,
  Mypy (**533 source files**), Chinese docstrings and whitespace:
  `/tmp/skill-supersession-server-quality.log`. The complete run includes the final implementation
  and all new supersession tests. Earlier focused review corrected a rule that would have let an
  already ended unsupported target replace an unrelated retryable failure; the final tests cover
  successful, unsupported and permission-failed terminal targets separately.

All four repositories remain on `feature/skill-manager` and passed final whitespace checks. All
owned verification jobs ended, and the disposable PostgreSQL container/runner were removed.
No commit, release, deployment or managed capability advertisement occurred.

The full goal remains active and incomplete. This increment completes configuration supersession,
not Node execution: actual deployment dispatch, task-bound progress/cancellation, complete real
Server/worker/Helper/systemd/Claude acceptance, Docker/sbx lifecycle and whole-writer proof,
interrupted migration recovery and verified rollback, Node-only pending export, reference-aware
local reclamation, coordinated restore and the requirement-by-requirement audit remain required.

## 2026-09-24 — independent deployment input and exact task reservation

This increment adds the **internal** Server preparation/authorization boundary for actual deployment.
It does not enable public scheduling or Node execution. Bound library acceptance still honestly
reports unsupported; no Node/Helper capability advertisement or runtime behavior was changed.

Migration **0050_skill_deployment_tasks** composite-binds the original user, operation, account and
attempt to one exact NodeTask and one owned full-directory checkpoint. The saved original plan and
content digests cannot be substituted with another owner's/account's input. Empty migration rollback
is supported; rollback with any recorded task binding refuses before deleting history.

The new `SkillDeploymentDispatch` service:

- Validates the full saved plan/attempt chain under the user storage lock and retention savepoint.
  It rejects supersession, inactive owners/accounts, binding/selection changes and unsupported Nodes.
- Requires the feature gate, fresh complete Native backend support and strict integer optional
  `skill_manager.native.deployment_protocol_version=1`. Current Node does **not** advertise it.
- Reuses the existing original-node takeover admission and preserves ordinary migration conflicts
  as `needs_resolution`, without creating an incomplete deployment task.
- Uses shared `AccountMaterialization` to prepare the complete account directory with enabled
  library/local branches, root data and existing format/dependency/quota checks. Session snapshots
  now use this same composer, retaining their separate snapshot and effective-use publication.
- Saves an independent directory checkpoint with normalized exact members. This is neither an
  account head nor a fabricated session/effective-use observation. Preparation never writes ready.
- Creates exactly one canonical `prepare_account_skills` task per pending attempt. A retry creates a
  new task but reuses the first complete input, even after actual session publication advances heads.
  Changed directory/member epochs reject reuse; preceding tasks must have reached failed/cancelled
  control-plane states. Complete Node drain evidence still requires the future result protocol.

`authorize_deployment` rechecks the authenticated original Node, exact task record and attempt,
canonical payload, positive current poll attempt and active lease, current original configuration,
owner status, capability and state epochs. It grants no arbitrary digest read and is not yet exposed
as an HTTP content route. Generic task success/failure independently rejects this task type or any
saved binding, even if mutable task type/payload was tampered with. A dedicated verified outcome
protocol remains required before execution can be enabled.

Retention now reads bounded task identity/status columns through the owner binding without loading
payload JSON or disturbing cached task entities. Pending/leased/running Node tasks protect their
complete input independently of attempt projection. Pending/running/conflicted attempts and current
retryable failures also protect it. Supersession or a failed attempt alone cannot release still-active
work. Terminal bindings keep only metadata; explicit normal checkpoint retirement releases the tree
while preserving the binding and original digest. Existing member-history dependencies and clocks
continue to govern content reclamation.

Optional capability normalization removes invalid deployment versions, avoiding the ORM's `True == 1`
equality from silently preserving a previous grant. The test for a boolean task payload uses an actual
SQL JSON update because an ordinary equal-valued ORM assignment correctly does not issue a write.

Evidence completed before the final full gate:

- New SQLite deployment tests: **47 passed, 1 skipped** (PostgreSQL concurrency case):
  `/tmp/skill-dispatch-targeted.log`.
- Shared directory/session preparation and capability regression run: **72 passed**:
  `/tmp/skill-dispatch-focused-final.log`.
- PostgreSQL 17 with a fresh database cloned from the **actual migrated schema** per test:
  **109 passed**, including independent concurrent reservation, cross-owner/task/content constraints,
  original-input retry after real published head progress, reference retirement, supersession and
  existing snapshot/persistence tests: `/tmp/skill-dispatch-postgres.log`.
- The same PostgreSQL run proved empty 0050→0049→0050 migration round-trip and populated downgrade
  refusal without changing the recorded version or task count. Its owned container was removed.
- Ruff format/lint, Mypy (**545 checked files**) and Chinese docstrings passed.

Final Server full gate passed: **1537 passed, 59 skipped**, **82.77% coverage**; Ruff format/lint,
Mypy (**545 checked files**), Chinese docstrings and whitespace passed:
`/tmp/skill-dispatch-server-quality.log`. This run includes the final task-status retention guard,
optional capability normalization and all new tests. No test threshold or existing behavior assertion
was weakened. All owned verification jobs ended; the temporary PostgreSQL runner and owned container
were removed. All four repositories remain on `feature/skill-manager` and pass whitespace checks.
No commit, release, deployment or managed capability advertisement occurred.

Next execution work must implement the bounded dedicated deployment manifest/file/lease/result API,
worker decoding and durable confirmation, and a Helper-owned full-directory preparation path without
fabricating a session or changing live session files. It must define cancellation/drain and superseded
acknowledgement before allowing generic task terminal transitions. Public initial pending acceptance
and scheduler integration remain disabled until that path exists. Existing session-only
`prepare_skill_snapshot` requires real session/spec identity and cannot simply be called with a fake
session for deployment. Takeover may discover new account-local sources; subsequent plan authority
must explicitly handle the resulting selection change rather than silently rewriting an accepted plan.

The complete goal remains active and incomplete: this increment does not prove actual Node execution,
full Server/worker/Helper/systemd/Claude acceptance, Docker/sbx lifecycle and whole-writer proof,
interrupted migration recovery and verified rollback, Node-only pending export, reference-aware local
reclamation, coordinated restore or the full requirement-by-requirement audit.

## 2026-09-24 — original deployment content transport

Dedicated authenticated Node manifest/file/lease routes now expose only previously reserved exact
deployment tasks. Every request binds the original Node, operation/account/attempt/task and current
poll lease, with the existing configuration, owner, capability and directory/member epoch checks.
The manifest returns the original full plan, complete directory and exact members as
`prepared_input`, `committed=false`; encoded envelopes are limited to 64 MiB. The original plan's
generation and disabled sources survive transport. No session identity is fabricated.

File downloads authorize manifest membership, release the database transaction, copy and verify all
bytes in private disk-backed staging, then reauthorize the original poll before streaming. This
allows concurrent lease renewal while disk copying waits, without allowing a changed poll to receive
the staged bytes. Missing/corrupt files and unrelated same-user digests fail closed. Staging closes
on failure, cancellation and completion. Lease renewal accepts a strict integer current poll only,
rejects expiry/replacement and returns the full original identity with a server-relative budget of
at most 300 seconds. Neither reads nor renewal advance attempts, heads, use observations or readiness.

The Go client adds separate deployment input, file and lease methods plus neutral original plan and
member types. Strict decoding rejects missing/null/aliased/duplicate fields and wrong integer types.
Canonical plan hashing preserves int64 values, sorts copied sources and matches Python's digest.
Input validation checks the full expected identity, plan/tree hashes, exact enabled members,
state/checkpoint identities, positive epochs and required directories/SKILL.md files. A shared golden
fixture generated using the real Python schemas includes generations and epochs above 2^53. Existing
snapshot file streaming and deployment downloads share private bounded byte/digest validation; each
caller retains its own authorization. Redirects, unsafe error bodies and automatic write retries
remain rejected. The opt-in live test stores no credentials in the repository.

Completed evidence:

- Focused Server deployment/content/lease regression suite: **91 passed, 1 skipped**:
  `/tmp/skill-deployment-transport-server-final-targeted.log`. The 21 new API tests include real Node
  authentication, another authenticated Node denial, exact poll identity, strict lease body,
  configuration supersession, corrupt/missing retained bytes, envelope limits and copy/renewal races.
- Ruff format/lint, Mypy (**549 files**) and Chinese docstrings passed before the full gate.
- Focused Go API/skillmanager tests passed:
  `/tmp/skill-deployment-transport-go-final-targeted.log`.
- Complete Node quality gate passed with exit 0, including Go tests/vet, formatting, shell/installer
  tests and managed/official Skill consistency checks; **62.2% statement coverage**:
  `/tmp/skill-deployment-transport-node-quality.log`.
- Actual Go client → live loopback Uvicorn → SQLite/content store passed all four scenarios:
  original manifest/two full files/current lease; reissued poll rejects the old attempt; expired lease
  rejects reads and renewal; real library disable supersedes the original operation and revokes all
  routes. `/tmp/skill-deployment-transport-live.log`. The fixture seeds reservation capability and
  the poll lease, so this proves transport only, not worker/Helper execution. The runner shut down
  its Server and removed its private database, content and credentials in its cleanup path.

Final Server full quality gate passed with exit 0: **1558 passed, 59 skipped**, **82.74% coverage**;
Ruff format/lint, Mypy (**549 files**), Chinese docstrings and whitespace checks all passed:
`/tmp/skill-deployment-transport-server-quality.log`. This run covers the final transport implementation
and all new tests. No schema migration was added; head remains **0050_skill_deployment_tasks**. The
root wire contract and Server/Node architecture, control rules and READMEs describe this boundary.
All four repositories remain on `feature/skill-manager` and passed whitespace checks. The shared
golden fixtures match byte-for-byte. All owned verification jobs ended; the disposable live Server,
private data/credentials and temporary runner were removed. No capability advertisement was added.

Worker decoding/lease supervision, Helper-owned independent full-directory preparation, durable
result inspection/acknowledgement and cancellation/drain must precede initial pending acceptance and
scheduler activation. Generic deployment task results remain rejected, and the current Node still
does not advertise deployment capability. The complete goal remains active and incomplete, including
real Server/worker/Helper/systemd/Claude acceptance, Docker/sbx lifecycle and whole-writer proof,
interrupted migration recovery/rollback, Node-only pending export, reference-aware local reclamation,
coordinated restore and the full requirement audit. No commit, release or deployment occurred.

The next lifecycle increment must explicitly account for the generic Node task status `expired`:
deployment retention currently rejects unknown statuses rather than treating timeout as drain, and
no deployment expiry transition is implemented. It must also preserve the takeover boundary: newly
discovered local sources can change effective selection, so scheduling must reconcile that change
with immutable accepted plans rather than silently replacing them. Session-only
`prepare_skill_snapshot` cannot serve independent deployment through a fabricated session.

## 2026-09-24 — independent durable Helper deployment preparation

The private authenticated Helper socket now implements `prepare_skill_deployment` with a matching
typed Go client. Its bounded attempt/task/size header is followed by the strictly decoded complete
original Server input and manifest-bound file streams. No caller can supply a session, host path,
runtime UID or process identity. The Helper requires its configured original Native Node and an
existing matching account fence; the immutable fence's initial epoch is a lower bound, not a new
claim of current Server authorization. It neither creates nor advances that fence.

The low-level preparation publishes `deployment-<attempt UUID>/` under independent SkillStateRoot.
The complete materialized directory, private permission baseline and schema-1 `deployment.json`
receipt share fsync/no-replace atomic publication. The receipt fixes the original binding, complete
input digest, directory epoch, original generation and Helper-generated UUID. Every content entry
remains Helper-owned; no account/session tree, head, process, mount or effective-use record changes.
The shared materialization core now separates validated manifest/copy policy from ownership selection;
existing public session preparation still requires non-root runtime UID/GID. Deployment is the private
Helper-owned caller, not a relaxation of ordinary session isolation.

Exact retry and Helper restart verify the original receipt, baseline, ownership, normalized modes,
single-link ordinary files and every retained byte. They preserve the same receipt and never
redownload or repair a damaged published bundle. Only absent bundles allow first preparation.
Unpublished failure stages are removed; publication/fsync uncertainty retains complete evidence for
the next exact inspection. The socket shares bounded streaming with independent input/result frames;
the downloader completion byte cannot replace the Helper's own size/hash/classification checks.
Disconnect/deadline cancels both filesystem work and waiting for Helper mutation serialization.

Verification completed:

- Cross-platform focused deployment protocol/input tests passed:
  `/tmp/skill-deployment-helper-protocol.log`.
- Final Node full quality gate passed with exit 0: formatting, Go vet/tests, **62.0% statement
  coverage**, installer/shell/release/Skill consistency and whitespace checks:
  `/tmp/skill-deployment-helper-node-quality.log`.
- Final root-owned Linux filesystem/Helper regression passed with exit 0: **223 top-level test
  executions passed, 10 skipped** across the script's skillmanager/runtimehelper/managedskills/worker
  selection: `/tmp/skill-deployment-helper-linux-final.log`. This includes actual HTTP client → Unix
  Helper socket → private complete directory, restart replay without the HTTP source, altered
  identities/epochs/input, missing/foreign fence, corrupt or missing records/bytes, symlinks/hardlinks,
  changed ownership/permissions, quota/reserve failure, source verification failure, missing completion
  marker and disconnect while waiting for serialization. Shared session preparation/lifecycle and
  takeover regressions also passed. The HTTP source is a controlled test server; this is not the full
  live control-plane/worker/systemd/Claude acceptance. Kernel/systemd-gated skips remain separate.

Architecture, state/control rules, dedicated preparation documentation, READMEs and the root wire
contract describe this boundary. The Linux verification script now includes the dedicated Helper
tests. Owned verification jobs ended and the script removed its temporary binaries/container.
No Server schema/code, CLI behavior, scheduler activation or capability advertisement changed.

Next work remains exact worker task decoding and continuous lease supervision, dedicated durable
Server result inspection/acknowledgement, cancellation/drain and then initial pending acceptance and
scheduling. Generic deployment completion remains rejected. A prepared local receipt alone cannot
mark the operation ready. The complete original goal stays active and incomplete, including real
Server/worker/Helper/systemd/Claude acceptance, Docker/sbx whole-writer lifecycle proof, interrupted
migration recovery/rollback, Node-only pending export, reference-aware local reclamation, coordinated
restore and the requirement-by-requirement completion audit. No commit, release or deployment occurred.


## 2026-09-24 — durable deployment success and actual worker confirmation

Dedicated Node `POST /skill-deployments/{attempt_id}/result` now accepts the exact original poll
and complete Helper preparation receipt. Its separate `/result/inspect` route observes the same
proposal without changing authority or retention. First confirmation reconstructs original complete
input and validates its hash, directory epoch, original generation, current unexpired poll, active
owner, configuration and capability. The original user lock followed by exact task lock serializes
one retention savepoint: task success, cleared lease, one immutable NodeTaskResult, original attempt
ready, operation projection and release clocks. Generic task completion/failure remains rejected.
No new migration was added; head remains **0050_skill_deployment_tasks**.

Exact replay and inspection recover the original committed result even after actual input retirement
or feature/capability withdrawal, while retaining original Node/binding and active-owner checks.
Changed receipt/poll/identity, duplicate/corrupt/missing terminal rows, changed terminal poll or a
terminal lease fail closed. Inspection never reconstructs content or reacquires references. The
Server validates delegated authenticated Node evidence, not a cryptographic Helper signature.

The worker now intercepts deployment tasks before generic decoding/caches, strictly validates the
canonical ten-field payload and original task identity, and maintains one lease through manifest,
file transfer, Helper preparation, original receipt validation, proposal persistence and dedicated
confirmation. Pending/confirmed schema-1 metadata records use full-record CAS in the existing ledger;
int64 values retain integer precision. A newer poll may replace an unaccepted pending proposal only
after exact inspection at that newer poll and with the identical Helper receipt. Confirmed cannot
downgrade. Accepted Server success wins a concurrent terminal renewal rejection. Bounded uncertain
errors remain DEPLOYMENT_PENDING, never generic task failure.

An independent background loop only inspects pending proposals and saves exact accepted results.
It neither obtains a lease, invokes Helper nor submits a new confirmation. Python-generated shared
full-input digest vectors verify int64 values above 2^53 and Unicode/HTML/U+2028/U+2029 escaping in Go.
Root wire contract, Node/Server architecture/state/control documents and both README languages now
describe these boundaries.

Verification completed:

- Server focused result/API tests: **23 passed, 2 skipped** (PostgreSQL cases run separately),
  `/tmp/skill-deployment-result-http-final.log`; additional boundary tests: **7 passed**,
  `/tmp/skill-deployment-result-boundaries.log`. Coverage includes real Node authentication,
  configuration supersession, unchanged read-only lock version, terminal-history corruption and
  rollback after an actual flushed result insertion.
- PostgreSQL migrated-schema regression: **65 passed**, including independent concurrent same and
  differing confirmations, `/tmp/skill-deployment-result-postgres.log`. Temporary databases and
  owned container were removed. A preimported-anyio assertion-rewrite warning is test-runner-only.
- Server final full gate exited 0: **1588 passed, 61 skipped**, **82.83% coverage**, Ruff formatting
  and lint, Mypy (**556 source files**), Chinese docstrings and whitespace:
  `/tmp/skill-deployment-result-server-quality.log`.
- Node full gate exited 0 with **62.3% coverage**, formatting, vet, all Go tests, installer/shell/
  release/Skill consistency and whitespace: `/tmp/skill-deployment-result-node-quality.log`.
- Root-owned Linux regression exited 0: **231 top-level executions passed, 11 skipped**:
  `/tmp/skill-deployment-result-linux.log`. Ten skips require separate kernel/systemd fixtures;
  the eleventh is the live Server test run separately below.
- Worker/runtimehelper/API deployment race checks passed:
  `/tmp/skill-deployment-result-race.log`.
- Actual Uvicorn/SQLite Server → Linux Go worker lease/download → authenticated root Helper socket →
  private complete directory → dedicated Server result passed twice: ordinary confirmation and
  deliberately lost HTTP response after the real confirmation committed. Recovery/replay ran after
  shutting down Helper, proving read-only acknowledgement recovery. Python checked one immutable
  result, succeeded task, ready operation and unchanged session/snapshot/effective-use counts:
  `/tmp/skill-deployment-result-live.log`. Temporary Server, containers, binary, private database,
  content and credential fixture were removed. The reservation capability, poll lease and initial
  account fence were fixture-seeded; this is **not ordinary scheduler, systemd or Claude acceptance**.

The complete goal remains active and incomplete. Dedicated failure/cancellation/drain and superseded
acknowledgement must precede public pending acceptance, scheduling and capability advertisement.
Generic task `expired` still needs deliberate retention treatment: timeout is not drain evidence.
Takeover-discovered local sources must be reconciled with immutable accepted plans without silently
rewriting them. Other outstanding requirements include real ordinary Server/polling worker/Helper/
systemd/Claude acceptance, Docker/sbx whole-writer lifecycle proof, interrupted migration recovery and
verified rollback, Node-only pending export, reference-aware local reclamation, coordinated restore
and the requirement-by-requirement completion audit. No commit, release, deployment or capability
advertisement occurred.


## 2026-09-24 — permanent local deployment drain and expired-input protection

Server retention now recognizes Node task `expired` as non-drained. It protects the original
complete directory and member dependencies even after an independently failed nonretryable attempt
projection or actual configuration supersession. Unknown task states still fail closed. Expiry
cannot authorize content preparation, successful confirmation, lease renewal or a new overlapping
retry execution. This reuses the existing task status and retention graph, with no schema change.

The Node adds the private authenticated `drain_skill_deployment` operation and typed client. It
accepts only the complete original ten-field Native deployment binding, checks the configured Node
and existing account fence, and uses the same cancel-aware mutation lock as preparation. A live
copy/publication must finish or fail before drain acknowledgement. The 30-second handler cancels
its lock wait on deadline/disconnect; it does not infer drain from an expired Server poll.

First drain requires any existing prepared bundle to retain its safe matching original receipt.
It then atomically publishes private `deployment-drain-<attempt UUID>.json` containing schema 1,
complete binding and Helper-generated receipt UUID. File and parent fsync precede acknowledgement;
exact replay revalidates the record and repeats parent fsync. No-replace publication prevents
rewriting original identity. An absent work bundle remains absent, and all existing content remains
untouched, including damaged bytes. Missing/corrupt identity in an existing prepared bundle blocks
new drain rather than guessing its owner. This receipt does not claim retained content integrity.

Preparation now checks the permanent drain before requesting object bytes, including requests that
already read metadata but were waiting for serialization. Exact or altered same-attempt input cannot
reopen after restart. Corrupt, linked, non-private or foreign-owned drain records prevent preparation
and remain unrepaired. Separate historical preparation reads do not restore execution authority.
The operation touches no account/session/workspace directory, head, mount or process and authorizes
no local reclamation or Server terminal result.

Verification completed:

- The new expiry tests first reproduced the gap (**3 failed, 1 passed**) before the implementation.
  The final focused expiry/input-retention/task-boundary regression passed **17 tests, 1 skipped**
  (existing PostgreSQL-only concurrency case): `/tmp/skill-deployment-expiry-after.log`. Tests use
  real storage lock/savepoints, configuration supersession and retirement checks; an expired old
  task prevents successor reservation despite accepted retry intent.
- Server full quality gate exited 0: **1592 passed, 61 skipped**, **82.83% coverage**, Ruff format/lint,
  Mypy (**557 source files**), Chinese docstrings and whitespace:
  `/tmp/skill-deployment-expiry-server-quality.log`.
- Node full quality gate exited 0: **62.2% host statement coverage**, formatting/vet, all Go tests,
  installer/shell/release/Skill consistency and whitespace:
  `/tmp/skill-deployment-drain-node-quality.log`.
- Root-owned Linux filesystem/Helper/worker regression exited 0: **241 top-level executions passed,
  11 skipped**, `/tmp/skill-deployment-drain-linux-verified.log`. New tests cover absent/prepared
  attempts, immutable exact retry/restart, damaged content preservation, foreign/missing identity,
  malformed/aliased/duplicate/null records, symlinks/hardlinks, permissions/ownership, cancelled lock
  waiting, a real active preparation versus drain, and a proxy dropping the response only after the
  actual authenticated Helper handler saved its durable fence. Restart recovers the identical
  receipt and rejects delayed preparation. Existing kernel/systemd/live-Server opt-in skips remain.
- Host deployment protocol race checks passed for runtimehelper and skillmanager:
  `/tmp/skill-deployment-drain-race.log`. Linux-only filesystem tests were executed by the separate
  root-owned Linux regression above, not by this macOS race run.

The Linux script now includes all dedicated deployment Helper tests. Wire contract, state/control/
architecture rules, dedicated preparation documentation and Node README translations describe the
new local boundary. Owned verification jobs ended; the Linux script removed its temporary binaries
and container. No migration, commit, release, deployment or capability advertisement occurred.

The complete goal remains active and incomplete. Next work must bind the original durable drain to
Server failure/cancellation/superseded terminal confirmation and independent Worker recovery before
public pending acceptance or scheduling. A local receipt alone must never advance Server state or
release pending content. Initial takeover can discover sources that change effective selection;
those changes must be reconciled with the immutable accepted plan. Remaining full-scope work still
includes ordinary Server/polling worker/Helper/systemd/Claude acceptance, Docker/sbx whole-writer
lifecycle proof, interrupted migration recovery and verified rollback, Node-only pending export,
reference-aware local reclamation, coordinated restore and the full requirement completion audit.


## 2026-09-24 — original Server revocation and exact drained terminal confirmation

Schema head is now `0051_skill_deployment_drains`. One immutable termination intent references the
exact original independent deployment-task binding, retaining original poll/error and Server-selected
failed/superseded classification. No existing task is backfilled; downgrade locks and refuses recorded
intent. The table participates in retention classification. Revocation alone releases no input and
changes no task/attempt terminal status.

Dedicated original-Node APIs now request/look up revocation and confirm/inspect the saved intent
plus permanent Helper drain. First revocation and first success compete under the same original
user/task lock order. Committed success cannot be revoked; committed revocation permanently fences
input, renewal and first success. An expired original lease may revoke, while a stale poll cannot
revoke newer execution. Actual operation replacement selects nonretryable supersession while keeping
the original request. Generic task failure/completion remains forbidden.

One retention savepoint confirms task failed/cancelled, attempt failed/superseded, operation projection,
release clocks and one exact NodeTaskResult. Both terminal outcomes use the existing result-table
category `failed`, preserving superseded semantics in the dedicated result. This distinction was
caught and corrected against the actual migrated PostgreSQL status constraint. The final accepted
poll is frozen alongside the original complete result. Altered, duplicate/missing history, retained
terminal leases and changed polls fail closed. Exact replay survives input retirement, capability
closure and a retry successor without modifying that successor. Retry reservation now requires an
exact dedicated accepted drain result, not task flags alone.

Go HTTP transport strictly validates nested canonical fields, original identities, bounded codes,
retryability, exact drain and final poll. Missing/null/aliased/duplicate outer data cannot become a
false absent-intent observation. Python-generated failed/superseded fixtures are shared with Go.
Uncertain POSTs are not automatically retried. The root wire contract, Server/Node architecture and
control rules, dedicated docs and English/Chinese READMEs describe the boundaries.

Evidence:

- Dedicated HTTP/core/prior-success regression: **36 passed, 2 skipped**;
  `/tmp/skill-deployment-termination-http.log`. Boundary/input-retention/task-boundary regression:
  **20 passed, 4 skipped**, `/tmp/skill-deployment-termination-boundaries.log`. Final focused suite:
  **28 passed, 3 skipped**, `/tmp/skill-deployment-termination-focused-final.log`. The additional
  predecessor-status-only retry rejection test and its complete module passed **7 tests**;
  `/tmp/skill-deployment-termination-retry-final.log`.
- Actual migrated PostgreSQL suite: **66 passed**;
  `/tmp/skill-deployment-termination-postgres-final.log`. It covers empty downgrade/upgrade roundtrip,
  recorded-intent downgrade refusal, concurrent independent success/revocation with exactly one
  winner, and same/different concurrent drain confirmations. Databases, container and content removed.
- Node HTTP transport full gate exited 0 with **62.4% coverage**;
  `/tmp/skill-deployment-termination-node-complete.log`. API race checks passed;
  `/tmp/skill-deployment-termination-go-race-final.log`.
- Actual Uvicorn → Go HTTP client → root Linux Helper → terminal confirmation passed both normally
  and with deliberate HTTP 503 after real commit; `/tmp/skill-deployment-termination-live-final.log`.
  Real original bytes were downloaded and prepared, revocation denied late content/success, permanent
  drain preserved the complete directory, and recovery/replay succeeded with Helper stopped. The
  original reservation/poll/fence were fixture-seeded. This initial proof did not execute Worker
  termination dispatch; the next increment supplies that evidence.
- The full Server gate initially found one omitted new table in the expected metadata inventory:
  **1 failed, 1611 passed, 64 skipped**. After correcting the expected inventory, the final full gate
  exited 0: **1613 passed, 64 skipped**, **82.93% coverage**, Ruff, Mypy (**565 source files**),
  Chinese docstrings and whitespace; `/tmp/skill-deployment-termination-server-complete.log`.


## 2026-09-24 — durable Worker termination dispatch and independent recovery

The Worker now checks original Server revocation before leased preparation. Typed renewal causes
survive lease cancellation, preserving actual supersession classification. Known bounded Server
failures, lease/cancellation, Helper unavailability and network errors can start dedicated termination;
unknown responses remain pending. Uncertain success confirmation retains its original success proposal.
A definite later renewal/confirmation rejection can begin revocation while preserving that proposal;
termination first inspects it so a competing accepted success still wins.

The original task ledger admits requested/revoked/drained/confirmed termination phases. The bounded
request is durable before revocation HTTP; exact committed intent is durable before Helper drain;
exact permanent drain is durable before terminal HTTP; accepted observation freezes the final poll.
Every phase retains any original pending preparation proposal with exact integer metadata. Full-record
CAS prevents stale writers, changed receipts and discarded success evidence. Confirmed success cannot
be downgraded. Requested recovery checks original intent first, and restores exact competing accepted
success without Helper access. New task polls may advance only a still-uncommitted request after
absent-intent lookup; an existing intent keeps its original poll and classification.

The background loop checks pending success proposals for revocation, then independently resumes
requested/revoked/drained journals without preparation leases or backend admission. Lost revocation
uses original lookup; lost Helper acknowledgement repeats the original binding; once drain is saved,
result inspection precedes exact terminal resubmission and no Helper call repeats. Bad or foreign
records fail individually. Queue dispatch and all journal phases bypass generic task replay. No
runtime preparation/launch, content deletion or capability advertisement follows from recovery.

Verification completed:

- Focused Worker deployment tests and race checks pass;
  `/tmp/skill-deployment-worker-focused.log`, `/tmp/skill-deployment-worker-race.log`. Cases include
  lost replies at all three external transitions, ledger reopen, exact final-poll replay, retained
  large-integer success proposals, stale/concurrent writers, competing committed success, foreign/
  malformed records, failed intent persistence before Helper, invalid drain, newer-poll recovery and
  definite supersession after an earlier pending success (both renewal and confirmation boundaries).
- Node full quality gate exited 0, **62.8% host statement coverage**, all Go tests, formatting/vet,
  shell/install/release/Skill checks and whitespace; `/tmp/skill-deployment-worker-node-quality-final.log`.
- Root-owned Linux filesystem/Helper/Worker regression exited 0: **252 top-level executions passed,
  12 skipped**; `/tmp/skill-deployment-worker-linux-final.log`. Existing opt-in kernel/systemd/live-Server
  cases are not counted as passed by this generic Linux run.
- Actual Server → dedicated Worker dispatch → root Helper → durable terminal confirmation passed
  normally and with deliberate post-commit response loss; `/tmp/skill-deployment-worker-live.log`.
  The Worker retained the prior preparation, saved revocation before drain and drain before terminal
  confirmation. After Helper shutdown and ledger reopen, background inspection and task replay
  recovered the same accepted receipt without Helper. Python also checked one Server result and
  unchanged Session/Snapshot/EffectiveBranch counts. Reservation, original poll/account fence and
  Server revocation were fixture-seeded; this is not ordinary scheduling, systemd or Claude acceptance.
- All four repositories remain on `feature/skill-manager`; tracked and untracked whitespace checks
  pass. Temporary verification runners, owned services/containers, binaries, databases, content and
  credentials were removed. No commit, release, deployment or capability advertisement occurred.

The complete goal remains active and incomplete. Next work is ordinary pending acceptance and
scheduling, including reconciliation of takeover-discovered sources with immutable accepted plans.
Real ordinary Server/polling Worker/Helper/systemd/Claude acceptance, Docker/sbx whole-writer lifecycle,
interrupted migration recovery and verified rollback, Node-only pending export, reference-aware
local reclamation, coordinated restore and the full requirement/interleaving audit remain required.


## 2026-09-24 — immutable first-takeover discovery and ordinary pending scheduling

Schema head is now `0052_skill_deployment_discovery`. New acceptance for an unmanaged bound account
saves its expected initial directory epoch beside the unchanged original plan digest. The original
takeover publication atomically resolves only matching active/retryable current attempts, recording
its exact receipt and normalized original manual sources/first revisions. Empty discovery still
seals the receipt. Terminal unsupported/stored/ready and nonretryable failed history does not expand.
No historical backfill or later-head reconstruction is permitted. Any discovery failure rolls back
the complete initial authority publication while preserving the original capture/upload for retry.

Discovery preserves original operation identity, generation, accepted plan rows and attempt digests.
Task/content digests identify the separate resolved execution plan, using unchanged protocol v1.
Authorization, retry, supersession, replacement validation and retention use that saved selection.
Later local changes remain real configuration drift. Composite foreign keys enforce original owner/
account receipt and revision boundaries; receipt queries are explicitly owner-scoped. Retention checks
original source checkpoints and revision-one metadata even after tombstoning, and terminal discovery
metadata alone does not permanently retain content. Downgrade refuses recorded boundaries.

New ordinary API acceptance now passes explicit deployment policy to the library service. Active
bound Native accounts with complete saved deployment reports start pending; known compatible offline
Nodes can wait. Unbound accounts stay stored, and incompatible/missing reports remain unsupported.
Acceptance creates no task and reports no readiness. All initial attempt/operation projections remain
validated against the same immutable accepted plans. Missing service policy context stays fail-closed.

Before task lease locks, authenticated Node polling examines at most four original-Node latest pending
or needs-resolution attempts with no task binding. Each owner transaction reloads the current chain
and binding inventory, then commits separately. Existing reservation rechecks active owner/account,
original selection/binding and fresh capability; first use reserves takeover, later polls consume
resolved discovery and build complete input. Conflicts resume the same attempt after real resolution.
Existing updated_at rotates waiting candidates. No-task superseded attempts can terminate, while
already-bound attempts remain exclusively subject to dedicated revocation/drain. Explicit account,
binding and materialization failures become terminal; quota failure retains retryability. Lost
freshness waits; actual capability withdrawal becomes unsupported. Unknown failures roll back.

Completed evidence so far:

- Discovery/termination/takeover PostgreSQL suite: **74 passed**, including actual migration, empty
  downgrade/upgrade, recorded-discovery downgrade refusal, owner/account constraints and independent
  concurrent acceptance/publication; `/tmp/skill-discovery-postgres-latest.log`.
- Scheduling focused suite: **26 passed, 1 skipped** (independent PostgreSQL polling case),
  `/tmp/skill-scheduling-focused.log`. Cases include offline recovery, complete-report withdrawal,
  owner/account/binding revocation, actual quota failure, bounded batch rotation, stale candidates,
  rollback after real reservation, unchanged task redelivery, supersession before/after binding,
  actual migration conflict resolution/resume, ordinary first-takeover discovery, and authenticated
  HTTP acceptance/poll/content/result/replay with simulated Helper evidence.
- Actual migrated PostgreSQL combined suite: **101 passed**, including concurrent independent polls
  producing one exact task and one current lease; `/tmp/skill-scheduling-postgres.log`. Owned
  databases, container and test content removed by the runner.
- Real disposable Uvicorn → ordinary authenticated HTTP acceptance/poll → Linux Go Worker → root
  Helper → exact ready/result recovery: **2 passed**, normal and deliberate post-commit response
  loss; `/tmp/skill-scheduled-live.log`. The task/reservation/poll were created by production paths,
  and original-request replay recovered the same result. Exactly one accepted result and unchanged
  Session/Snapshot/EffectiveBranch counts were verified. Managed account state, capability report
  and initial Helper fence remain fixture-supplied: **not first-use Worker takeover, systemd/Claude
  or Docker acceptance**. No Node code or capability advertisement changed in this increment. The disposable Server,
  containers, credentials, database/content, binary and temporary proof runners were removed.
- The earlier discovery full gate passed **1626 tests, 65 skipped**, **82.12% coverage**, but its
  collection preceded scheduling changes; it is not final scheduling evidence. The scheduling full run reported **1651 passed, 66 skipped, one fixture failure**,
  **83.16% coverage**, `/tmp/skill-scheduling-server-quality.log`. The stricter malformed-report
  test assigned True over 1, which Python/SQLAlchemy regarded as unchanged, so its intended corrupt
  input was never persisted. The fixture now explicitly marks that JSON field modified; production
  heartbeat normalization already rejects that boolean. Corrected acceptance/authorization tests
  passed **39 tests**, `/tmp/skill-scheduling-boolean-final.log`. Final Ruff format/lint, Mypy
  (**581 source files**), Chinese docstrings and whitespace passed. Production code is unchanged
  since the full run. The complete corrected gate now passed **1652 tests, 66 skipped**,
  **83.16% coverage**, with Ruff, Mypy (**581 source files**), Chinese docstrings and whitespace;
  `/tmp/skill-scheduling-server-quality-complete.log`.

The complete goal remains active and incomplete. Required remaining work includes ordinary first-use
Worker/Helper/systemd/Claude acceptance, Docker/sbx whole-writer lifecycle, interrupted migration
recovery and verified rollback, Node-only pending export, reference-aware local reclamation,
coordinated restore and the full requirement/interleaving audit. No commit, release, deployment or
capability advertisement occurred.


## 2026-09-24 — real first-use Worker/Helper/systemd capture and deployment

Ordinary HTTP installation on a legacy Native account now has real cross-process evidence through
actual Go polling, dedicated Worker dispatch, authenticated root Helper, initial fence/capture,
Server discovery and complete deployment. No task, lease, takeover, managed directory, local fence,
capture or deployment input was fixture-seeded. A real systemd main process exits while its child
keeps the old directory open for writing: capture remains pending, preserves the child, and saves
its late write only after whole-cgroup quiescence.

Normal completion and deliberately lost post-commit takeover confirmation both pass. Original
committed task replay succeeds with Helper stopped and altered old source bytes. After Helper
restart, the next ordinary poll produces the original operation's resolved library/manual directory,
including the captured late write and root auxiliary file. Dedicated deployment confirmation matches
the durable local preparation and leaves the initial capture unchanged. Server checks confirm two
original tasks/results, unchanged accepted plan digest and no Session/Snapshot/EffectiveBranch rows.

- Live final proof: **2 passed in 12.94s**, `/tmp/skill-first-use-verified.log`.
- Node full gate exited 0: **62.8% host statement coverage**, `/tmp/skill-first-use-node-quality.log`.
  Linux ARM64 test compilation, Linux amd64 Worker vet, host Worker tests and shell parsing passed.
- The default 2 GiB disk reserve is preserved. Container state uses `/var/tmp` on container disk;
  the first small-tmpfs fixture correctly failed the unchanged storage policy.
- Temporary private fixtures, runner, binary, owned systemd containers/images and Uvicorn were removed.

Scope remains explicit: the Node capability report is fixture-supplied; this is neither full daemon
heartbeat-loop nor Claude-session acceptance. This proof runs Worker and Helper in a root test
process; separate nonroot protocol evidence does not change that boundary. Docker/sbx acceptance,
interrupted migration recovery/verified rollback, Node-only pending export, reference-aware local
reclamation, coordinated restore and complete requirement/interleaving audit remain required.
No capability advertisement, commit, release or deployment occurred. The full goal remains active.


## 2026-09-24 — reproducible first-use suite and explicit §11.1 audit

The first-use proof now lives in both repositories: Server
`tests/test_skill_first_use_live.py` / `tests/skill_first_use_live_support.py` own a disposable real
HTTP listener, private fixture identity and optional post-commit response loss. Node
`tests/linux_skill_first_use_test.sh` owns the systemd container, test binary and read-only connection
fixture. The shell handles interruption and maps the Docker host gateway for Linux as well as Docker
Desktop. No task, lease, takeover, managed directory, capture or local fence is seeded. The reproducible
command and exact root-process/background-loop limitations are documented in the Node first-use guide
and Server scheduling guide. Opt-in repository execution passed **2 tests in 7.42s**,
`/tmp/skill-first-use-repository.log`; ordinary collection skips both and starts no network/container.

[The audit](skill-manager-interleaving-audit.md) maps every one of the 19 §11.1 rows to named tests,
distinguishing actual persisted Server transaction checks, CLI contracts, Node primitives and real
Linux/systemd/kernel evidence. It does not aggregate separate layers into fictitious end-to-end
acceptance. It explicitly records remaining two-account staged snapshot, GC-versus-snapshot,
backend dependency adapter and real runtime combinations. Requirements outside §11.1 still need
their complete audit.

New `tests/test_skill_design_interleavings.py` adds nine actual transaction checks: snapshot
revision changes before/after reservation; remove/reinstall with late E1 upload; absence of a
disabled skill; conflict across two already-existing skills with next-session baseline verification;
reset of one of two exposed skills; directory reset followed by root-only late writes; disabling a
linked target; and directory restore after a version switch. Detached/conflicted inputs are read
back through original content authorization, including actual bytes. Current heads, rules and
generations are checked rather than inferred from a returned status. These cases pass **9 tests**,
with the two opt-in first-use cases correctly skipped during default collection;
`/tmp/skill-design-interleavings-complete.log`. Final Ruff format/lint, Mypy (**584 source files**)
and Chinese docstring checks pass. Related scheduling HTTP, state-command, publication and snapshot
regressions passed **47 tests**, `/tmp/skill-first-use-audit-regression.log`. The earlier full gate
predates these test-only additions; it is not presented as a new full-suite run. All four repositories
remain on `feature/skill-manager`, with tracked and untracked whitespace checks passing. The owned
first-use container/image/build directories and private test database/content fixtures were removed.
No Server or Node production behavior changed in this increment.

Full ordinary Claude and unprivileged daemon acceptance, Docker/sbx lifecycle, interrupted migration
recovery with verified rollback, Node-only pending export, reference-aware local reclamation and
coordinated restore remain required. The full goal remains active, with no commit, release,
deployment or capability advertisement.

## 2026-09-24 — frozen Native Node export and verified CLI publication

Implemented an additive `skill state export --snapshot UUID --scope account-directory
--account-id UUID --output PATH` workflow across Server, Node and CLI. It recovers a complete
already-frozen original Native snapshot directly over the existing SSH gateway, independently of
Server upload quota. It cannot read live work or cause stop/capture/upload/publication/cleanup.
Existing Server checkpoint item and directory exports retain their semantics.

Server issues a fixed-lived, domain-separated grant for the original snapshot, original user token,
exact active device and SSH key. It ensures/reuses only the existing key-sync task, including leased
observations. Verification rechecks original identities and revocation without depending on current
account configuration, startup lease or advertised capability. Known termination/finalization facts
must agree. Malformed request validation returns no input fields, avoiding credential echo.

The Node command parses only the fixed snapshot/protocol command, takes device/key from installed
forced-command identity, and accepts the grant only on bounded stdin. It reads an existing Helper
record and read-only retained object descriptors. It reauthorizes periodically, around each object
and before completion; revocation closes blocked output. All frozen records remain unchanged.
No inbound Node HTTP surface was added.

CLI uses the live user credential and local registration metadata, bounds key-sync waiting and the
SSH child, validates the original binding/manifest and every streamed object's size/digest/content
classification, and requires the final completion frame, EOF and successful SSH exit. It publishes
private staging atomically only to an absent/empty destination. Interruptions terminate SSH and leave
no claimed complete bundle. The bundle has the existing manifest/object layout and the separate
`agent-remote-skill-node-snapshot-v1` metadata format; it is not a Server checkpoint or a durability
acknowledgement. Grants enter neither argv, diagnostics, SQLite nor bundle files.

Evidence:

- Server focused authorization: **31 passed**, `/tmp/skill-node-export-server-expanded.log`.
  These exercise real HTTP authentication, exhausted state quota, unchanged upload count,
  revocation, user-token lifetime, leased-key reuse, foreign identities, contradictory observations,
  a separate HMAC protocol domain, disabled Node and input-redacted validation failures.
- The real Go producer's fixed binary stream is shared with Python manifest/identity verification
  and Rust CLI contracts. CLI tests use an SSH process double and verify exact binary/text bytes,
  deduplication, original large integer identities, forbidden connection substitution, incomplete/
  corrupt streams, failed SSH exit, no secret exposure and cancellation killing the child.
  `/tmp/skill-node-export-cli-contract.log`: **5 passed**.
- Final Linux suite: **253 passed, 12 skipped**, `/tmp/skill-node-export-linux-composed.log`.
  The allowed UID 65534 cannot traverse the root-owned store but completes the real stream through
  the Helper socket; UID 65533 remains denied. The original older fixture lacked a preparation task
  and was correctly rejected. This proof now seeds a task-bound immutable capture before the read;
  no process is launched, and its fixed grant authority is a fixture, not a real Server login.
- Node HTTP/stream/forced-command race checks passed:
  `/tmp/skill-node-export-go-tests.log`. Additional full gateway dispatch checks passed:
  `/tmp/skill-node-export-dispatch.log`.
- Complete Server gate: **1693 passed, 68 skipped**, **83.26% coverage**, Mypy **592 files**,
  Ruff format/lint, Chinese docstrings and whitespace, `/tmp/skill-node-export-server-quality.log`.
- Complete Node gate: **62.7% host coverage**, vet, formatting, all host tests, installer/shell/
  consistency/whitespace checks, `/tmp/skill-node-export-node-quality.log`. Later changes are tests
  only: frozen inspection under allowed/denied nonroot identities and the composed Helper stream.
- Complete CLI gate: **565 test executions**, denied-warning Clippy, formatting, shell/cache/release
  and whitespace, `/tmp/skill-node-export-cli-quality.log`. A subsequent interruption wording change
  clarifies that no remote *skill* state changed (key synchronization may have occurred); **23 focused
  tests passed**, `/tmp/skill-node-export-cli-final-contract.log`.

Scope remains explicit: this is complete-directory export of an existing Native frozen capture.
The HTTP, SSH-process-double and Linux Helper proofs do not constitute a single deployed SSH/Claude
lifecycle. Export after local disk pressure prevents freezing itself still needs separate recovery
work; no quota bypass or live-work fallback is claimed. Docker/sbx, real Claude inheritance,
interrupted migration rollback, local reclamation, coordinated restore and the remaining full design
and interleaving audit are still open. The goal remains active and incomplete. No commit, release,
deployment, capability advertisement or subagent work occurred.


## 2026-09-24 — stopped-work export after local freezing failure

The existing snapshot export now has a separate guarded read path for a stopped original Native
work directory when allocating immutable frozen objects fails. Helper requires the exact sealed
snapshot and ready spec/launch authority, safe directory identity,
and repeated passive proof that the original whole cgroup has no writers. A previous-boot source
also requires absent runtime resources. Original termination evidence preserves classification;
if it is absent, a recorded canonical original invocation is additionally required and recovery is
always unclean. Corrupt or linked evidence remains an error. Only absence of the finalization
directory permits this
path; existing corrupt, linked, incomplete or legacy captures remain errors.

The private `stream_stopped_skill_export` operation holds the cancellable Helper mutation lock
through scan, transfer and final verification, for at most fifteen minutes. It does not issue stop,
reconciliation, capture, fsync, upload, acknowledgement or cleanup, and does not allocate another
content copy. It uses the export protocol's separate 100000-entry/10 GiB limits so runtime quota
excess does not itself prevent a bounded recovery. Root rechecks authority, work identity, complete
tree digest and writers before completion. No `FinalizationRecord` or local-durable claim is created.

Gateway grant revalidation now starts before Helper inspection, including long initial scans.
The verified private relay checks the binding, manifest, each object's digest/length/classification,
footer and EOF before forwarding completion. Frozen exports preserve the existing golden wire.
CLI initial/final scan waits use the overall transfer deadline; object and frame payload reads keep
30-second idle bounds. User command, metadata format and atomic publication remain unchanged.

Evidence:

- Focused Go recovery/relay and periodic authorization race checks pass in
  `/tmp/skill-stopped-export-stream.log`; final HTTP/stream/forced-command race checks pass in
  `/tmp/skill-stopped-export-race.log`.
- Full Linux suite: **258 passed, 13 skipped**, `/tmp/skill-stopped-export-linux-suite.log`.
  New cases exercise copy-reserve rejection, retained runtime quota overflow, original exited or
  missing units, previous-boot data, linked/corrupt identities, complete-tree changes, returning
  writers, same/previous-boot missing termination with recorded invocation, rejection when both
  termination and launch evidence are missing, and cancellable lock waits. The first run found linked work was
  rejected only at final verification; explicit pre-scan directory identity checks now prevent any
  disclosure from that case. Final suite includes full gateway/Helper reads as UID 65534 with direct
  private-store access denied and UID 65533 rejected. The tests use controlled systemctl responses
  and fixed grant authority, not a running Claude process or deployed SSH/Server authentication.
- Full Node gate passes at **62.7% host coverage**, including vet, all host tests, formatting,
  installer and consistency checks: `/tmp/skill-stopped-export-node-quality.log`.
  Linux ARM64 Helper/skillmanager vet also passes: `/tmp/skill-stopped-export-linux-vet.log`.
- Full CLI gate: **571 test executions** plus formatting, denied-warning Clippy, shell/cache/release
  and whitespace checks: `/tmp/skill-stopped-export-cli-quality.log`. Virtual-clock tests prove
  initial/final scans can exceed 30 seconds, stalled objects still fail, and the overall deadline
  leaves no published bundle. Tokio test-clock support is a development-only feature.

The opt-in `tests/linux_skill_export_enospc_test.sh` also passed a real physical ENOSPC test:
`/tmp/skill-stopped-export-enospc.log`. Only a disposable size-checked 16 MiB tmpfs is filled.
Termination retention fails with ENOSPC before creating its record; the complete stream recovers
unclean content from the recorded original invocation and passive writer proof. Termination and
finalization remain absent and the volume remains full afterward. Runtime/workspace fixtures stay
on the normal container filesystem so their ACL support is independent of the small private volume.
The ordinary Linux suite correctly skips this separately opted-in fill test.

This closes bounded recovery after copy-reserve/runtime-quota failure and actual ENOSPC before
termination retention when the original invocation was recorded. Missing both forms of original
evidence, content above fixed bounds, Docker/sbx support and full ordinary CLI/Server/unprivileged
Worker/Helper/systemd/Claude acceptance remain open. The transfer lock can delay other Helper
mutations for its lifetime. No capability advertisement, commit, release or deployment occurred.


## 2026-09-24 — staged account snapshots and exact reservation versus GC

Added three Server test modules without changing production behavior:

- `test_skill_staged_snapshots.py` establishes two accounts on r3, stages r4 and pins only A, then
  prepares and reserves actual A=r4/B=r3 snapshots. It checks original branch identities, resolution
  metadata, exact content bytes, idempotent snapshot replay, unchanged default revision and real Git
  branch tracking, unchanged post-pin generation and absence of any B/r4 branch.
- `test_skill_snapshot_gc_interleavings.py` tests both real commit orders for reclamation of an
  unreferenced filtered tree versus an exact snapshot acquiring that same tree. Snapshot-first
  invalidates the stale GC plan; GC-first releases only redundant tree metadata and reservation
  safely reconstructs references to still-protected bytes. Subsequent GC cannot reclaim the
  snapshot's tree. A separate explicitly injected cross-category deletion marker makes actual
  reservation fail atomically, leaving no snapshot, branch head change or new upload.
- `test_skill_snapshot_gc_races.py` uses independent PostgreSQL connections and
  `pg_blocking_pids` to prove reservation actually waits for a marker transaction. Marker commit
  yields `CONTENT_UNAVAILABLE` with no partial snapshot; rollback permits one complete reservation.
  The marker is injected at the write boundary; this test is not a physical GC deletion scenario.

The new cases passed **4 tests on SQLite** (two lock-only cases require PostgreSQL) and **6 tests
on an isolated PostgreSQL 17 instance**, `/tmp/skill-snapshot-postgres.log`. The temporary container
was removed. The §11.1 audit now records this direct evidence and its limits. No actual Claude,
Node-local reclamation or coordinated restore proof is inferred from these Server transactions.


Final verification for this increment: complete Server gate **1697 passed, 70 skipped**, **83.26%
coverage**, Mypy **595 files**, Ruff format/lint, Chinese docstrings and whitespace, recorded in
`/tmp/skill-stopped-export-server-quality.log`. Node and CLI full gates above passed; subsequent
help/error wording removes the frozen-only description and passed **60 CLI contract executions**
(`/tmp/skill-stopped-export-cli-final-contract.log`) plus Go stream/gateway contracts
(`/tmp/skill-stopped-export-node-final-contract.log`). All test processes are reaped; the owned
PostgreSQL container, disposable tmpfs containers and temporary binaries were removed. All four
repositories remain on `feature/skill-manager` with tracked/untracked whitespace checks clean.
The complete design goal remains active and incomplete; no commit, release, deployment or backend
capability advertisement occurred.

## 2026-09-24 — Native Python discovery and real mounted venv inheritance

The Helper now discovers runtime dependencies during actual Native snapshot preparation. Fixed
`/usr/bin/python3` and `/usr/local/bin/python3` candidates and their same-directory versioned targets
require protected root-owned no-follow path chains and native ELF architecture. A fixed isolated
Python query runs as the session UID/GID with sanitized environment, bounded stdout and timeout.
Dependency identity includes CPython major/minor, ABI flags, byte order, Linux architecture and the
exact link target. Neither task input nor manifest entries select probe executables.

Preparation uses and seals one discovered map for both materialization and later capture. Exact
retries reuse the retained map, including historical empty mappings, and preserve learned work.
Mounting revalidates original interpreter dependencies before changing the filesystem view. Changed
or missing dependencies fail launch, while historical finalization/export remain readable without
the old interpreter installation. Unsupported external links still retain `portability_error`.
No target interpreter bytes are copied into captured objects. This uses the existing manifest and
snapshot formats, with no protocol migration or new Go dependency.

`TestNativeSkillPythonVenvSurvivesCaptureAndNextMountedSession` now proves a real mounted round trip:
the actual non-root Bubblewrap runtime creates a venv and Python module, executes it, freezes work,
then a newly prepared and mounted session executes the inherited venv/module and writes new state.
The test uses production discovery with no manually supplied dependency mapping. It directly
transfers frozen objects and uses a shell test program; it does not claim Server publication,
unprivileged Worker/systemd lifecycle, real Claude acceptance or Docker Sandbox support.

Validation:

- Node complete quality gate: **62.7% host coverage**, vet, all host tests, formatting, shell,
  installer, consistency and whitespace checks, `/tmp/skill-python-node-quality.log`.
- Final Linux component suite: **263 passed, 14 skipped**, `/tmp/skill-python-linux-suite.log`.
  The separately opted-in mount, systemd, reboot and physical ENOSPC tests remain skipped here.
- Real Linux mount suite: **11 passed**, `/tmp/skill-python-mount.log`. It includes real Python
  discovery, unsafe executable rejection, bounded output, original-map replay, missing-dependency
  mount denial with successful historical capture, and the actual venv inheritance case.
- Final Linux ARM64 Helper/skillmanager vet passes. Later Linux-only ELF hardening and unsafe-file
  regressions are covered by the final Linux component and mount runs; no host behavior changed.

See Node `docs/skill-runtime-dependencies.md` and audit row 12 for precise supported paths and limits.
Host Python installations must remain stable while sessions use them; this adapter does not freeze
host package upgrades or certify arbitrary binary extension portability. Complete product acceptance,
Docker/sbx, interrupted migration recovery/verified rollback, reference-aware local reclamation,
coordinated restore and recovery above fixed export bounds remain open. No commit, release,
deployment or backend capability advertisement occurred. The overall design goal remains active.

## 2026-09-25 — Fresh remote reclamation proof and local durable intent

Server now exposes a separate authenticated full-content reclamation authorization for the original
Node. It binds a fresh request challenge and revalidates the unretired original stopped snapshot,
incoming directory checkpoint, terminal publication, manifest, all object metadata and complete
physical bytes under the user storage lock. Historical receipts alone cannot authorize loss of a
Node-only copy after an inconsistent DB/content restore. Missing/corrupt/linked/retired/deleting
content fails closed. No new lease, retention root, clock or quota mutation is introduced.

Node transport enforces the exact original acknowledgement binding, strict JSON fields and 64-bit
publication attempts. A later terminal publication may retain the same original incoming checkpoint.
Its nonpersistent monotonic deadline charges the entire HTTP request against the fixed 60-second
window. Random per-request challenges and `no-store` prevent old response reuse; no redirects or
automatic retries are permitted.

Linux `skillmanager` now has durable intent/read/completion primitives. First marking requires the
exact terminal object-backed capture, retained publication acknowledgement and runtime-cleanup
receipt, a fresh monotonic budget, and a full work rehash against frozen content. Excluded system
paths must be absent or empty, preserving uncaptured data. Intent records original work/object
filesystem identities. Immutable no-replace records plus fsync support restart and partial removal;
completion requires both roots absent, parent sync and unchanged original intent. Replaced roots,
unsafe records and orphan completion fail closed. Exact replay does not mint a fresh HTTP deadline.

Frozen transfer, export, recapture and work mounting reject marked content. Audit reads retain exact
snapshot/manifest/acknowledgement history. Inventory reports `reclamation_pending` or
`content_reclaimed`; Worker never interprets these as new capture/upload work, skips completed
reclamation and retires only the original admission grant. `OpenSessionWork` now uses kernel
`openat(O_NOFOLLOW)` to reject a same-root leaf symlink that `os.Root.OpenFile` could resolve.

**Actual local deletion is not implemented or scheduled.** No Helper reclamation socket operation
exists yet. The journal's caller contract still requires independent writer, runtime/network,
mount/alias and local-reference absence proof. Tests explicitly model content removal to verify
interruption/reader behavior; they are not evidence of a production deletion executor. A separate
safe cancellable deletion/resume path and Worker integration remain necessary, including a policy
for deliberately retired remote history that this authorization refuses.

Validation of remote authorization:

- Complete Server gate: **1710 passed, 70 skipped**, **83.25% coverage**, in
  `/tmp/skill-node-reclamation-server-quality.log`. This run began before final nonce/no-store and
  PostgreSQL race additions; the final focused contracts cover those changes.
- Final SQLite contracts including an 11 MiB runtime object's last-byte corruption: **21 passed,
  2 PostgreSQL-only skipped**, `/tmp/skill-node-reclamation-server-latest.log`.
- Isolated PostgreSQL 17 authorization/HTTP/race contracts: **22 passed**,
  `/tmp/skill-node-reclamation-postgres.log`, before the later large-file test addition. Independent
  connections and `pg_blocking_pids` prove storage-lock retention through physical verification and
  cancellation. This is not an actual GC physical deletion test. The owned container was removed.
- Final Server Ruff format/lint, Chinese docstrings and Mypy **600 source files** passed after the
  large-file test. Node API/neutral receipt contracts and race tests passed.

Local-journal verification and remaining lifecycle evidence are recorded in Node
`docs/skill-node-reclamation.md`. The complete product goal remains active. Real ordinary
CLI/Server/unprivileged Worker/Helper/systemd/Claude inheritance, Docker/sbx writer lifecycle,
interrupted migration recovery with verified rollback, actual local reclamation, coordinated restore,
recovery above fixed export bounds and the complete requirement audit remain open. No commit,
release, deployment or capability advertisement occurred.

Local-journal verification: final Linux component suite **271 passed, 14 skipped**, no failures,
`/tmp/skill-reclamation-journal-suite-final.log`; skipped cases remain separately opted-in mount,
systemd, reboot and ENOSPC tests. Node full gate passed with **62.8% host coverage**,
`/tmp/skill-reclamation-journal-quality.log`; the subsequent admission-retirement update passed
Worker/API/skillmanager race tests (`/tmp/skill-reclamation-journal-final-race.log`), and the later
excluded-content guard passed the final Linux suite. Final Linux ARM64 vet passed. Journal tests use
real Linux files/fsync and reopen between modeled deletion phases, but removal itself is deliberately
test-driven because the production deletion executor does not exist. All owned test processes were
reaped and the temporary cross-compiled binary removed.

A final Linux-only review also makes a remaining frozen-object directory retain private Helper
ownership/mode during intent recovery. Its added corruption case passed the focused Linux reclamation
suite (`/tmp/skill-reclamation-journal-linux-final.log`) and ARM64 vet after the full suite above.
All four repositories remain on `feature/skill-manager`; tracked/untracked whitespace checks passed.

## 2026-09-25 — Actual Linux reclamation executor and interruption recovery

`ReclaimFinalizationContent` now removes only the original `work` and `finalization/objects` roots
bound by a valid durable intent. It requires an independent caller proof function and inspects both
remaining trees before deleting anything in an invocation. Every survivor must match the frozen
manifest or an allowed empty system directory. Partial absence permits resume; changed/new data,
unsafe objects, unknown types, permissions or link targets preserve the affected content. Original
materialization-mode normalization is respected.

Deletion uses descriptor-relative no-follow traversal and kernel mount IDs. Same-inode/device bind
mounts cannot pass as ordinary directories/files. Complete file length/hash/classification and stable
metadata are checked again before unlink; the original root remains bound after independent proof.
Directories and removed-root parents are synced before retaining completion. Cancellation/errors
leave immutable intent and audit metadata for recovery. No recursive path-based `RemoveAll` performs
production content deletion.

The new isolated `tests/linux_skill_reclamation_test.sh` exercises actual removal, cancellation
between file/root phases, reopen and resumed completion, nested empty directories, symlinks,
permission normalization and real bind-mount refusal. Callback-driven mutations prove changed files
and root substitution between verification and unlink remain protected. Existing tests that model
partial removal remain useful journal tests but no longer stand in for executor evidence.

Design §5.2's unresolved-conflict protection is now explicit at local marking and persisted-intent
validation. A fresh `conflicted` remote response proves available bytes but cannot mark local deletion.
A later resolved publication can authorize the same original incoming input. Equal publication
ID/attempt cannot rewrite its terminal decision. The Server observation endpoint itself remains
read-only; no API migration was introduced by this local restriction.

This does **not** complete Node-local reclamation integration. No Helper reclamation socket operation
or Worker scheduler invokes the executor. Actual runtime/network/cgroup absence, mount aliases,
local-reference exclusion and active transfer/export lifetimes still require production orchestration
and interleaving tests. Tests use controlled proof callbacks. Coordinated restore and the other full
product requirements listed above remain open. No commit, deployment or capability advertisement.

Executor verification: Node full quality gate passed with **62.8% host coverage**
(`/tmp/skill-reclamation-executor-quality-final.log`); final Linux component suite **279 passed,
15 skipped** (`/tmp/skill-reclamation-executor-suite-final.log`); separate real-mount/reclamation
suite **15 passed, no skips** (`/tmp/skill-reclamation-executor-mount-resolved.log`). Linux ARM64
vet and host API/skillmanager race tests passed (`/tmp/skill-reclamation-executor-race.log`). The
mount run includes the resolved-conflict policy and same-publication immutability changes; a later
test-fixture-only refactor is covered by the final component and host gates. All owned runs were
reaped, disposable containers removed and the temporary binary deleted.

## 2026-09-25 — Kernel read holds across Helper replacement

Frozen upload/export now acquire a read-only descriptor holding a shared kernel flock on the private
immutable manifest inode. It spans the complete operation and closes on success, error or cancellation.
Using existing immutable metadata keeps frozen export read-only and avoids allocating a lock file on
a full filesystem. The additive private descriptor kind `hold` retains strict original capture/size/
entry/count validation and ordinary peer authentication. No credential or process-memory lease is
stored in this mechanism.

First marking and deletion take nonblocking exclusive locks on the same inode. Raw manifest reads
also hold a shared lock; standalone frozen-object descriptors retain shared inode locks that deletion
preflight checks before removing siblings. SCM_RIGHTS preserves the open-file-description lock across
sender shutdown. Linux tests terminate the original and a replacement Helper server instance while
client descriptors remain alive, and verify the last reader's closure releases exclusion. Actual
unprivileged UID 65534 can hold/read through the socket without traversing the private store; UID 65533
is denied. These are actual protocol/kernel tests, not a full deployed Helper daemon restart test.

Worker/Gateway callers validate the held original capture before accessing bytes. Upload failure
phases and export revocation/blocked output tests verify closure, preventing a lost operation from
leaking its content reference. Existing golden export framing remains unchanged. No Helper
reclamation socket operation or Worker deletion scheduler has been enabled; actual runtime, network,
cgroup and mount-alias proof still needs to surround the executor.

Read-hold verification: Node full quality gate passed with **62.8% host coverage**
(`/tmp/skill-finalization-hold-quality.log`); API-independent host race checks for skillmanager,
Helper, Worker and export passed (`/tmp/skill-finalization-hold-race.log`), as did Linux ARM64 vet.
Final Linux component suite **285 passed, 15 skipped** (`/tmp/skill-finalization-hold-linux-complete.log`),
real-mount/reclamation suite **15 passed, no skips** (`/tmp/skill-finalization-hold-mount.log`), and final
Helper/nonroot/descriptor-frame cases **3 passed** (`/tmp/skill-finalization-hold-peer-final.log`).
Final export hold/revocation cases passed (`/tmp/skill-finalization-hold-export-final.log`).

The first Linux run exposed a test synchronization mistake: a sender can briefly retain its own
transferred descriptor until acknowledgement processing completes. The corrected test shuts down
and joins both sending server instances before asserting final receiver release. An ensuing default
Debian HTTP dependency download failed before tests began. The complete successful Linux run uses
the same repository test bodies/binaries with a temporary HTTPS bootstrap and explicitly verified
host public CA bundle; TLS verification remained enabled. The temporary runner is
`/tmp/skill-finalization-hold-linux-https.sh`. No product or permanent test source configuration was
changed for the network workaround. All test handles were reaped and disposable containers removed.

Final lock-handoff review keeps the manifest shared lock open until the object's shared inode lock
is acquired, eliminating an admission gap between the two descriptors. Focused Linux read-hold,
object-reader and reclamation tests pass (`/tmp/skill-finalization-hold-handoff.log`) with final
ARM64 vet. Temporary test binaries were removed. All four repositories remain on
`feature/skill-manager` with tracked/untracked whitespace checks clean; no commits or deployment.

## 2026-09-25 — Passive Helper reclamation proof and private coordinator

The private Helper coordinator now holds its cancellable lifecycle mutex across original Native
capture/spec/launch validation, fresh authorization, marking and deletion. It requires the original
runtime-cleanup receipt and an absent transient root. Same-boot inspection checks a stable original
inactive/failed/absent unit and whole-cgroup quiescence; a remaining unit must retain its recorded
invocation, transient user and canonical cgroup. Previous-boot recovery requires a stable distinct
kernel boot and absent current unit/cgroup, including prepared inputs with no launch record. Missing
managed preparation authority, corrupt launch evidence and reappearing resources preserve content.

Passive network and mount inspection covers the runtime root, work and frozen objects, including
individual-file and enclosing-bundle aliases. The coordinator never stops processes, changes launch
authority, repairs mounts or deletes namespaces. It rechecks resources around initial marking and
every deletion phase. Per-entry guards check cancellation, boot, runtime-root absence and whole cgroup
under lifecycle exclusion; the executor retains all inode, content, mount-ID and reader-lock checks.
External systemctl/network commands therefore remain bounded independently of captured file count.
Partial intent and completed receipt replay use original saved authority without requesting renewal.

Tests exercise actual filesystem removal through this private coordinator with controlled remote
authorization and systemctl/ip fixtures. A mount-fixture path mistake was fixed before the final
real-bind run. Final Linux component suite: **291 passed, 16 skipped**
(`/tmp/skill-reclamation-runtime-linux.log`); independent reclamation/runtime/real-mount suite:
**22 passed, no skips** (`/tmp/skill-reclamation-runtime-mount-final.log`). The extra ordinary-suite
skip is the new opted-in mount test, which passes in the separate run. Node full quality gate passes
at **62.8% host coverage** (`/tmp/skill-reclamation-runtime-quality.log`), with final Linux ARM64 vet
and Helper/skillmanager host race checks (`/tmp/skill-reclamation-runtime-race.log`). Linux dependency
bootstrap uses the previously documented temporary HTTPS/public-CA workaround, with TLS verification.

This does not enable a reclamation socket operation or Worker scheduling. The remaining handoff must
start a Helper-process monotonic budget before a fresh Worker/Server challenge on the same live
connection, charge IPC/network/scan delay and cancel on disconnect. It must never serialize/rebuild
a deadline. Worker must invoke reclamation after upload read holds close and separately resume pending
intent. Real systemd/Server/Worker/Claude acceptance, retired-history policy, coordinated restore and
the broader requirements above remain open. No commit, deployment or capability advertisement.

## 2026-09-25 — Live reclamation protocol and Worker scheduling

The authenticated Helper socket now exposes separate `reclaim_skill_finalization` and
`resume_skill_reclamation` operations, outside generic task-result replay. First marking binds the
exact terminal capture to a random Helper challenge and Helper-process monotonic 60-second budget
started before challenge transmission. Worker echoes that challenge through the authenticated Server
HTTP endpoint and returns only strict authorization JSON; it never serializes or rebuilds a deadline.
Initial proof/scanning/marking honors the original deadline. The outer connection/deletion context is
bounded to 15 minutes, with cancellable lifecycle waits, owned input-reader shutdown, no path input
and fixed public failure frames. Helper shutdown/timeout while HTTP is running cancels that request.

Already marked intent resumes with original Node/session identity and independent runtime/reference
proof. It does not request fresh authorization, reupload bytes or need Worker transfer receipts. Only
fsynced completion returns the original capture. Actual Unix socket tests combine authenticated HTTP
fixtures with filesystem deletion; unread completion replies recover on a new Helper instance. Real
UID 65534 can reclaim/resume without traversing the private store; UID 65533 cannot reach authority or
resume. Virtual-clock tests verify both IPC and remote delays consume the original budget, including
exact expiry and stale challenge rejection. Malformed/oversized frames and changed identity fail closed.

Worker's existing independent finalization page coordinator now schedules first reclamation after
`transferFinalization` returns, closing its read hold and completing terminal acknowledgement/transient
cleanup. It validates saved terminal receipts and exact Helper completion. Pending inventory resumes
directly; completed inventory skips content. Failure remains pending without starving later page
items. Tests cover closed-reader ordering, missing/uncertain receipts, remote failure, conflict
preservation, changed completion and independent resume without transfer/HTTP. The prior real-Helper
transfer fixture intentionally lacks original managed launch authority: upload/ledger recovery still
completes, while its local content remains preserved with pending reclamation.

Validation: Node full quality gate passed at **62.8% host coverage**
(`/tmp/skill-reclamation-orchestration-quality.log`); Linux component suite **299 passed, 16 skipped**
(`/tmp/skill-reclamation-orchestration-linux.log`); focused protocol/runtime/nonroot suite **13 passed,
1 mount-only skip** (`/tmp/skill-reclamation-socket-peer.log`). API/Helper/Worker/skillmanager race tests
passed (`/tmp/skill-reclamation-orchestration-race.log`), as did Linux ARM64 vet. Existing temporary
HTTPS/public-CA Linux bootstrap was used with TLS verification enabled. No production mount-proof
relaxation or capability advertisement accompanies this integration.

The full goal is still incomplete. Complete deployed CLI/Server/unprivileged Worker/Helper/systemd/
real-Claude lifecycle and next-session inheritance, Docker Sandbox lifecycle, retired-history policy,
migration recovery/verified rollback, coordinated restore, oversized recovery/export and the complete
design audit remain open. The tests above use controlled HTTP and systemctl/ip fixtures and do not
substitute for those acceptance requirements. No commit, release or deployment was performed.
# Production Native daemon lifecycle and reconciliation boundary

The separate Node `docs/skill-lifecycle-acceptance.md` harness now builds the formal Node/Helper
binaries and runs the shipped systemd units with an independent nonroot Worker, root Helper and
distinct runtime UID. Its real Claude Code 2.1.220 Linux ARM64 `--version` case passed on 2026-09-25:
ordinary authenticated install/takeover/deployment/admission, production local pty attach, natural
exit, exact termination, frozen upload, clean publication, fresh reclamation authorization and
durable local reclamation all completed. The Server independently checked the retained records.
No runtime result, capture, launch authority or finalization was fixture-created.

This surfaced a real integration race: generic Node reconciliation could mark a managed session
interrupted while its create task was still queued/leased, or override a clean natural exit before
its exact termination observation arrived. The Server now excludes sessions with persisted skill
snapshots from legacy list-based reconciliation, using the stable session reference rather than a
mutable task marker. Eleven HTTP regressions failed before this change and passed afterward; managed
history also stays protected until exact termination evidence releases it.

The real-learning opt-in is implemented for two Claude inference sessions with a daemon restart,
unpredictable learned bytes and a second-session witness, but awaits explicit Linux test credentials.
It remains unverified. The capability report is still an explicit isolated fixture; product capability
advertisement, CLI/SSH/sync/account-onboarding acceptance, Docker Sandbox, kernel reboot and
coordinated restore remain outside this runtime-only result. This is not completion of the design.

## 2026-09-25 — Retain incomplete backend rollback as pending

Backend migration now preserves its original started intent on every rollback error. Previously,
a known failed rollback ACL service or source-identity failure could still produce a terminal failed
receipt. Only a rollback whose ownership walk and all three ACL commands succeed can now reach
terminal failure; the existing same-boot, writer-quiescence and filesystem-sync checks still apply.
Pending replay remains read-only, retains the original backup and blocks replacement migration.
Historical failed receipts retain their existing writer-termination meaning; this change does not
relabel them as verified source recovery or add automatic interrupted-migration continuation.

The actual isolated systemd regression reproduced failures at all three rollback ACL phases before
the fix (`/tmp/skill-migration-rollback-before.log`). After the fix, **7 subcases passed**
(`/tmp/skill-migration-rollback-after.log`): successful migration, failed target ACL with successful
rollback, access/default/traversal rollback failures, invalid source runtime identity and an ACL
service surviving launcher cancellation. Successful rollback additionally checks restored UID/GID
and reads the original learned file as the unprivileged source identity. Pending cases verify retained
backup and denial of both same-task mutation and replacement migration.

Node's full host quality gate passed at **62.8% coverage**
(`/tmp/skill-migration-rollback-quality.log`), together with Linux ARM64 Helper/skillmanager vet.
The systemd runner uses the repository test bodies and a temporary HTTPS/public-CA dependency
bootstrap with TLS verification enabled. Owned test containers/images were removed and all process
handles reaped. This is an ownership/receipt regression, not Docker Sandbox lifecycle or complete
rollback/recovery acceptance. No capability advertisement, commit, release or deployment was added.

## Backend migration admission across Server and Helper

Interrupted backend migration now closes all new legacy writer paths, not just replacement
migration/takeover. Helper checks private migration/copy history before Native/Docker binding,
session launch and config-import mutation. Started, incomplete, copy-only and failed-copy evidence
remains pending after Helper replacement; completed exact import/task replay remains read-only.
Worker preserves fixed diagnostics for both local and Server migration denial without raw messages.

Server admission and result confirmation share the content-user lock and refresh account/profile/task
state. Recorded incomplete/historical-failed migrations cannot be bypassed by editing account.status.
Failure preserves the source backend and records recovery_required, without reactivating a disabled
account. Results must match the original task, owner, Node, source and target. Exact terminal replay
cannot mutate a newer operation, and conflicting or malformed completion is rejected before writes.
Node config-import authorization checks current task/owner/lease/payload before exposing migration
diagnostics; terminal start attempts preserve the preexisting generic conflict response.

Validation:

- Nine initial HTTP regressions failed before the change; final adjacent API regressions passed
  **59 tests**, including the later successful/failed completion after an intervening disable
  (`/tmp/skill-migration-admission-regressions-final.log`). Final config-import authorization checks
  passed **35 tests**, including leased/pending/terminal/expired task precedence
  (`/tmp/skill-migration-import-authorization-final.log`).
- Real PostgreSQL tests passed **2 cases**, observing blocking PIDs and verifying refreshed admission
  after commit versus rollback (`/tmp/skill-migration-admission-pg.log`).
- Linux Helper regression run passed **12 top-level tests and 55 subcases**, including actual systemd
  writer survival and the four incomplete phases across six writer entry points
  (`/tmp/skill-migration-admission-node-fixed.log`). The first expanded run exposed Docker's noexec
  `/tmp` fixture location; the permanent systemd runner now supplies `TMPDIR=/var/tmp` for its tests.
- Node full host quality passed at **62.8% coverage** with Linux ARM64 vet and Helper/skillmanager/
  Worker race checks. The final Worker error-mapping change also passed its race check
  (`/tmp/skill-migration-admission-node-quality-final.log`,
  `/tmp/skill-migration-admission-worker-race-final.log`).
- The production Node/Helper daemon harness with actual Claude `--version` passed again:
  **1 passed, 1 deselected**, completing ordinary install/admission/exit/publication/reclamation
  (`/tmp/skill-migration-admission-daemon.log`). No inference credentials were used.
- Full Server quality run passed **1732 tests, 74 skips**, with **83.11% coverage** in 973.78 seconds
  (`/tmp/skill-migration-admission-server-quality.log`). It had already loaded modules before the
  final config-import authorization-order correction and later added tests; that correction is
  covered by the final 35-test run above. No second full run is claimed. Final global format, lint,
  Mypy (**609 files**) and docstring checks passed on the resulting source.

All owned containers and process handles were cleaned/reaped. Temporary Linux dependency bootstrap
still uses HTTPS with the host public CA and TLS verification. This does not deliver an interrupted
migration recovery command or source rollback attestation. Coordinated restore, complete CLI/SSH and
real learning/inheritance acceptance, Docker Sandbox and the other design requirements remain open.
The objective remains incomplete; no commit, deployment or capability advertisement was performed.

## Coordinated SQL/content restore and fresh Node materialization

Added `tests/skill_restore_support.py`, `skill_restore_seed.py`, `skill_restore_node.py` and
`test_skill_coordinated_restore.py` in Server, plus Node's
`internal/skillmanager/restore_materialization_linux_test.go` and
`tests/linux_skill_restore_test.sh`. The existing prepared-runtime fixture now delegates to a helper
so source and restored content volumes can be chosen independently.

The opt-in acceptance passed with real PostgreSQL 16 `pg_dump`/`pg_restore` and a full content tar:
**1 passed in 7.61 seconds** (`/tmp/skill-coordinated-restore.log`). Source SQL is dropped and its content
path moved before restore. Every ORM business table's full sorted-row digest and Alembic version
matches before restored service mutations; filesystem content/modes and all retained tree objects
match too. Explicit nonempty assertions cover revisions, tool/account overrides, account and local
skills, directory memberships, snapshots/finalizations, operation/deployment plans and attempts, and
partial conflict choices/receipts. Owner isolation survives same-package installation by a second user.

The saved resolution plan replays revision 1 and completes revision 2. A new fixture Node then uses
actual Server session admission, task leasing and authorized content downloads; the previous Node
cannot read its snapshot. A networkless ordinary Debian container receives only the downloaded
manifest/objects and the compiled test binary. Actual Node materialization verifies binary/root/local
state, both resolved learning files, absent deleted/detached files, independent regular copies,
runtime UID/GID 12345 and source-mode roundtripping through capture. The runner requires the exact
Go test's PASS marker, so an empty test selection cannot count as success.

Final global Server format/lint, Mypy (**613 files**) and Chinese docstring checks passed. Node host
skillmanager tests, Linux ARM64 skillmanager vet and shell syntax checks passed. Related Server
snapshot/resolution/admission regressions passed **26 tests, 1 opt-in skip** in 11.33 seconds
(`/tmp/skill-coordinated-restore-regressions.log`). All owned containers and process handles were cleaned/reaped.
No full-suite rerun or new coverage percentage is claimed for this test-only increment.

Initial termination, account readiness, replacement registration/affinity and capabilities are explicit
fixtures. This does not certify automatic failover/onboarding, old runtime-journal restore, full daemon
restore/SSH, real learning/inheritance, Docker Sandbox or interrupted migration recovery. Those and
the remaining full-design audit stay open. No capability advertisement, commit, deployment or release
was added; the overall objective remains incomplete.

## Durable backend migration writer authority

Backend recovery previously retained whole-migration/copy intents without the exact identity of a
surviving privileged service. New copies now carry `writer_version: 1`; each copy or target/rollback
ACL phase writes a private launch intent before systemd execution. Its Helper-generated description
binds one observed invocation, original account/task/boot and command/configuration digest. Root
transient services retain exited state until the whole cgroup is proven empty and terminal evidence
is durable. Cancellation preserves the original service. Internal observation through a replacement
Engine never relaunches it; cleanup requires the original terminal receipt and revalidates identity.

Whole-migration completion now requires its successful original copy and the applicable complete ACL
phase proofs. Missing, mismatched-version, pending or orphaned records keep admission closed.
Historical schema-0 receipts remain readable with their original meaning. They do not gain invocation
identity or source rollback authority. Node architecture/control/persistence rules and
`docs/skill-backend-writer-recovery.md` document the new records and retained recovery boundary.

Review also found that generic Helper success caching bypassed `migrate_account` input/evidence
validation. Five dispatch regression cases failed before correction
(`/tmp/skill-writer-cache-before.log`). Migration dispatch now bypasses that cache, revalidates exact
original receipts, and refuses both success and new writes when only a historical cache survives.
The real systemd lifecycle tests now exercise the public Engine dispatch for ordinary migration.

Validation on the final source:

- Linux skillmanager plus adjacent Helper regressions: **115 top-level passes, 308 passing subcases,
  5 opt-in skips**, `/tmp/skill-writer-linux-final.log`.
- Actual isolated systemd copy, ACL/rollback, cancellation, replacement observation, identity rejection
  and cache-dispatch tests: **6 top-level passes, 26 passing subcases**,
  `/tmp/skill-writer-systemd-verified.log`. A live original service survives caller cancellation,
  a replacement Engine observes that same invocation through its journal, and natural exit converges
  with exactly one execution. Historical cleanup leaves a different same-name service running.
- Final Node full quality gate passed with **62.8% coverage**, plus Linux ARM64 Helper/skillmanager
  vet and host race tests (`/tmp/skill-writer-node-quality-final.log`,
  `/tmp/skill-writer-race-final.log`). Private JSON corruption, symlink/hardlink, permissions, input
  binding, immutable outcome and missing-phase/orphan cases are covered by the Linux tests.

Systemd dependency bootstrap used a temporary HTTPS/public-CA runner with TLS verification. Owned
containers/images and process handles were cleaned/reaped. This proves durable phase supervision and
passive component observation, not full daemon restart or a user recovery command. Explicit Server
recovery authorization, recovery of absent/previous-boot phases, source permission attestation and
user-facing completion still remain. No capability advertisement, commit, deployment or release was
added; the full skill-manager objective remains active and incomplete.

## Completion recovery for original backend migration work

Added Node metadata-only completion recovery at original `migrate_account` dispatch. A same-boot
writer-version-2 task can observe its original completed phases, finish a missing copied receipt,
repeat passive quiescence checks after filesystem synchronization, and record its original successful
or failed whole-migration outcome. It never recreates a phase, launches copy/ACL commands, changes
ownership, stops live writers or overwrites the backup. Successful target recovery repeats the existing
read-only account verifier. Completed rollback preserves failure; it is not source permission proof.
Older pending evidence, absent/incomplete phases, live/populated/foreign services, invalid account
state, missing backup and cancellation remain pending.

Implementation review exposed a new recovery-specific crash window: direct rollback Lchown preceded
its first ACL receipt, so complete target receipts plus no rollback ACL could be misread as success.
An actual systemd prefix test reproduced the false success
(`/tmp/skill-completion-rollback-gap-before.log`). New copies now use writer_version=2 and persist
`MigrationOwnershipIntent` before target/rollback identity lookup or direct ownership changes. A
rollback intent alone blocks target-success inference. Phase creation, whole outcomes and inventory
validate original copy/migration links and protect orphaned intents. Started version-0/1 migrations
are deliberately not upgraded into this stronger recovery authority; historical terminal outcomes
remain readable and immutable.

Validation:

- Three initial metadata-completion cases failed before implementation
  (`/tmp/skill-completion-before.log`). Final focused completion tests cover 15 cases, including
  rollback-intent-only, legacy version 0, pre-ownership version 1 and previous-boot records.
- Actual isolated systemd acceptance passed **4 top-level tests and 27 subcases**
  (`/tmp/skill-completion-systemd-final.log`). Five crash-prefix cases execute real copy and ownership
  routines, omit only the later result step, then exercise public dispatch through a replacement
  Engine: completed target, completed rollback, missing copy receipt, live final ACL followed by
  natural exit, and rollback interrupted before its first ACL. Launcher counts and original backup
  bytes prove recovery starts no new writer and retains the original data.
- Linux skillmanager plus adjacent Helper regressions passed **118 top-level tests and 333 subcases,
  6 opt-in skips** (`/tmp/skill-completion-linux-final.log`). New ownership corruption, link, mode,
  cross-owner/boot/version, immutable intent and orphan cases are included. A fixture initially used
  an unchanged boot ID for its foreign-boot case; correcting that fixture produced the final pass.
- Node full quality passed with **62.8% coverage**, Linux ARM64 vet and host race checks passed.
  The affected migration suites also passed under the **Linux race detector** in a networkless
  Go 1.26.6 container (`/tmp/skill-completion-node-quality.log`, `/tmp/skill-completion-race.log`,
  `/tmp/skill-completion-linux-race.log`).

The actual systemd proof uses a temporary HTTPS/public-CA dependency bootstrap with TLS verification.
Owned containers/images and process handles were cleaned/reaped. This is original Helper task
convergence, not a user recovery command: generic Worker/Server terminal failures remain immutable,
and explicit authorized recovery task issuance, interrupted ownership repair, previous-boot recovery
and source permission attestation are still unfinished. No capability advertisement, commit,
deployment or release was added. The full objective remains active and incomplete.


## 2026-09-25 — explicit passive backend migration recovery

Server now issues a distinct administrator-only recovery task for an exact original terminal
migration and caller-retained UUID key. Fresh authorization and first result acceptance recheck
current ownership, affinity, legacy mode, original profile, no active sessions, live lease and
poll attempt under user/task locks. Exact terminal replay is read-only even after a newer migration.
Target success preserves the original failed result and account disable; failure keeps admission
closed. Separate status reads never dispatch. No new database schema is needed.

Node uses a dedicated Worker path that bypasses generic terminal ledger replay, fetches fresh
Server authority and sends only that exact binding to `recover_account_migration`. The Helper
opens existing state only, refuses managed fences and requires same-boot writer-version-2 original
copy/ownership/ACL evidence. Started or already-successful whole receipts undergo passive phase,
quiescence, account and backup checks. Recovery never starts missing writers, copies bytes again,
changes ownership/ACLs or stops anything. Missing/old/foreign/live/failed evidence stays blocked.

CLI adds `account recover-runtime ACCOUNT_UUID --original-task TASK_ID --request-id RECOVERY_UUID`
and read-only `account recovery-status ACCOUNT_UUID --request-id RECOVERY_UUID`. Both use an
administrator user login and support a typed version-1 JSON response. The explicit key survives
uncertain acceptance without silently planning a new request. Exit 0 confirms submission/query
transport and validation; status and target_completion_confirmed carry the original outcome.

Evidence includes authenticated Server HTTP tests; 6 real PostgreSQL lock-interleaving tests;
Worker HTTP/socket tests including cached success/failure bypass and mismatched authority; Linux
race tests for explicit/local completion; and 5 real systemd crash-prefix scenarios through the
new explicit operation, retaining launch counts and original backup bytes. CLI tests cover exact
POST/GET contracts and required identities. These do not yet prove deployed end-to-end command
execution, genuine interrupted ownership repair, source rollback attestation or previous-boot
migration recovery. No capability is advertised and the overall design remains incomplete.

A subsequent review found that status/same-key replay still advanced the shared usage lock counter.
A regression reproduced this (counter 4 → 6), and those read/replay paths now lock only existing
rows without creating or updating storage metadata. The final focused Server set passed 35 cases,
and the six real PostgreSQL interleavings passed again after this refinement. Final static checks
covered 670 formatted Python files and 617 Mypy sources; Chinese docstrings passed. Node full gate
passed at 62.7% host coverage, with Linux ARM64 vet and both host/Linux affected-suite race checks.
CLI full gate passed all 575 test executions.

Server full quality run completed: 1756 passed, 77 skipped, 82.85% coverage in 997 seconds.
The read-only refinement made while that full run was active was separately verified by the final
35-case focused set, six PostgreSQL cases, the exact no-write replay regression and full static
checks. Logs for this increment use `/tmp/skill-explicit-recovery-*`. All disposable PostgreSQL
and systemd containers were removed. No commits, release, deployment or capability advertisement
were performed. The overall skill-manager goal remains active and incomplete.

## 2026-09-25 — real CLI, HTTP and restarted-daemon recovery acceptance

Added an opt-in Server acceptance runner backed by current CLI/Node binaries and the shipped
Worker/Helper systemd units in a disposable Linux container. The original migration is created
through authenticated HTTP and executes one real copy plus three ACL writers. A temporary
UID-restricted Unix proxy drops only the successful original Helper reply; the ordinary Worker
retains/reports failure. Both daemons restart with different PIDs, and explicit recovery uses the
production Helper socket directly. Worker UID 22000 retains zero effective capabilities and
NoNewPrivileges. Migration receipts/results are produced by normal execution, not fixture seeding.

Both acceptance cases passed: lost replies and missing backup. The first loses a committed recovery
submission reply, rejects the first completion before commit, then loses the next committed
completion reply. Fresh lease authorization and exact result replay converge under the original key.
The second retains the backup under another name and verifies that recovery fails without copying
or repairing anything. Both preserve the original failed task/result and current account disable;
complete account/backup inventories retain hashes, links, modes, UID/GID, sizes, mtime, ctime, inode
and device. Exactly four original writer launches remain, with none added by recovery.

This acceptance exposed a CLI bug: generic device-admission JSON swallowed recovery identity and
unknown acceptance; malformed HTTP 200 responses were also mislabeled as rejection. Dedicated
recovery failures now retain validated account/request/original-task IDs, fixed content-free codes,
unknown target confirmation and the exact original-key status command. Submission preparation is
not_submitted, explicit 4xx rejection applies only to that invocation, and transport/5xx/malformed
success stays unknown. Status failure never proves prior acceptance absent. Invalid identities and
configuration/credential/remote error content are not echoed. Human errors use stderr; JSON errors
use one version-1 stdout envelope. Success output and required-argument exit behavior are unchanged.

Evidence:

- The new malformed-success CLI contract failed before the fix and passed afterward
  (`/tmp/skill-recovery-cli-error-before.log`, `/tmp/skill-recovery-cli-error-after.log`).
- Real cross-component acceptance passed **2 cases in 42.77 seconds**
  (`/tmp/skill-recovery-live-fixed.log`). The earlier missing-backup case passed before the CLI fix;
  the successful-recovery case exposed the actual command error contract.
- Server focused regressions passed **35 cases, 2 opt-in skips**; static checks covered 672 Python
  files and 619 Mypy sources, and Chinese docstrings passed. Logs include
  `/tmp/skill-recovery-live-regression.log`. No Server production behavior changed in this increment.
- Node full quality passed at **62.7% host coverage**; new acceptance package Linux ARM64 compile
  and vet passed. The shell runner syntax and whitespace checks passed. Node gate log:
  `/tmp/skill-recovery-live-node-quality.log`.
- CLI full quality passed **579 test executions, zero failures/skips**, including dedicated
  malformed-success output, local preparation/invalid identity redaction, and acceptance
  classification. Shell parsing, rustfmt, Clippy with warnings denied, release/cache contracts and
  whitespace checks passed (`/tmp/skill-recovery-cli-quality-final.log`).

The runner bootstraps dependencies with HTTPS and verified public CA certificates. Private fixture
credentials are mounted only at runtime, outside the image build context. Task-owned containers and
images were removed and verified absent. This is synthetic backend recovery proof using actual CLI,
HTTP authentication and production daemon lifecycle; no model credentials or inference were used.
It does not establish actual model learning/inheritance, complete SSH/CLI skill acceptance or Docker
Sandbox lifecycle. Interrupted ownership repair, previous-boot migration recovery, source rollback
attestation, oversized recovery policy and final requirement audit remain unfinished. No commit,
release, deployment or capability advertisement was performed; the full goal remains active.

## 2026-09-25 — real SSH export of frozen and quota-exceeded Native work

Added `tests/test_skill_ssh_export_live.py` and its bounded process/SSH support in Server, plus
Node `tests/linux_skill_ssh_export_test.sh` and `tests/skilllifecycle/export_linux_test.go`. Shared
real-CLI construction, private test identity and original process observation now live in
`tests/live_acceptance_support.py`; backend recovery acceptance reuses those small helpers.

The new opt-in acceptance uses the actual current host CLI, isolated host-only SSH key/agent, real
OpenSSH server, production forced-command gateway, shipped nonroot Worker and root Helper units,
real authenticated Server routes and actual Native systemd/bubblewrap execution. Account/device/key
and unpublished capabilities are explicit test fixtures; takeover, deployment, startup, local
termination/capture and SSH-key sync run through their production paths. Finalization uploads are
refused so Server cannot supply the exported bytes. Both daemons restart before export. Direct
nonroot access to the private Skill store is refused.

A synthetic mounted tool creates text learning, a binary database, an 8192-byte binary file, root
auxiliary content, executable permissions, an empty directory and a relative link. The frozen case
reads the original immutable capture. The runtime-quota case applies an actual 1 KiB Node policy
before preparation; the completed work exceeds it and no finalization directory is allowed to
appear. The stopped-work path still exports all content without another frozen copy. The exported
manifest and every distinct object/length/digest are verified, including the binary and large files.
Both cases perform another real CLI transfer while its registered SSH key is revoked during online
verification; the failed transfer publishes no bundle and leaves no staging directory. Full original
work/finalization byte, inode, mode, ownership, mtime and ctime inventories remain unchanged.

Evidence:

- Initial frozen SSH acceptance passed in 100.93 seconds, including cold image/dependency build
  (`/tmp/skill-ssh-export-live-first.log`). The extended combined run passed the frozen export and
  both existing backend-recovery cases. Its quota case completed export and revocation but exposed
  an incorrect test expectation that Server already had a termination receipt. When local freezing
  fails, that receipt is absent; export must not manufacture it. The assertion now requires absence.
- Final two-case export acceptance passed **2 tests in 29.09 seconds**
  (`/tmp/skill-ssh-export-live-passed.log`). The two migration recovery cases passed after extracting
  the shared helpers (`/tmp/skill-ssh-export-live-final.log`).
- Server authenticated export/wire/lifecycle-fixture regressions passed **33 tests in 12.30 seconds**
  (`/tmp/skill-ssh-export-server-regression.log`). Global Ruff formatting/lint, Mypy over **622 source
  files**, and Chinese docstrings passed; formatter checked **675 Python files**.
- Node final full quality passed at **62.7% host statement coverage**, including shell parsing,
  formatting, vet, host tests, installer and consistency checks
  (`/tmp/skill-ssh-export-node-final.log`). The changed Linux acceptance package compiled and passed
  Linux ARM64 vet. No CLI production code changed in this increment; actual current CLI compilation
  and the complete SSH command execution provide the relevant additional evidence.

Dependency bootstrap uses HTTPS with public CA verification. Private fixture credentials stay outside
image build context; the private SSH key never enters the container. All task-owned processes,
containers/images and coordination credentials are cleaned by the runner. This proves real SSH
transport and complete read-only export for frozen and configured-quota-exceeded Native data, not
model inference or default-limit capacity. Real Claude learning/inheritance, full CLI session command
acceptance, Docker Sandbox lifecycle, interrupted/previous-boot migration recovery and rollback
attestation, export beyond fixed protocol bounds, and the full requirement audit remain unfinished.
No commits, deployment, release or capability advertisement occurred. The overall goal remains active.

## 2026-09-25 — stopped writers with failed capture remain independently observable

Closed the status gap exposed by quota-exceeded SSH acceptance. Helper reconciliation now returns
`capture_pending` only after fresh original writer/resource checks, an existing valid private
termination receipt and verified absence of a finalization directory. It preserves original exit
classification and emits only `quota_exceeded`, `insufficient_storage`, `portability_error`, or
`capture_failed`. Corrupt/missing evidence, active writers and existing incomplete captures still
fail closed. A later successful freeze retains the original clean/unclean classification.

Worker background inventory reports this observation through the new authenticated
`POST /node/skill-snapshots/{snapshot_id}/capture-pending` without creating a transfer journal,
uploading, acknowledging, cleaning or reclaiming content. Capture remains retryable. Explicit stop
also requests a fresh observation after its initial stop/capture call fails. Exact pending evidence
must be committed by Server before the six-field process result can complete with a null digest.
Runtime admission grants are forgotten under their gate before network requests. The original
process result replays unchanged after later frozen capture upgrades the authoritative state.

Migration 0053 extends the existing termination row with a nullable digest and finite capture error.
SQL constraints require either a known digest without an error or a null digest with one known code.
Known classification cannot change. Frozen evidence upgrades pending evidence; late pending requests
cannot downgrade it. Migration preserves historical frozen rows and refuses downgrade while any
pending capture exists. All authorization, session/task locking and connection revocation continue
through the existing termination service. Export can carry known exit classification before the
content digest, and gateway reauthorization cannot forget or change either previously known fact.

Server saving status now separates `process_stopped=true` from `capture_pending`, with no content
or durability claim. CLI displays the finite cause and an export command bound to the original
account/snapshot. `--wait` ends with exit 1 instead of waiting through a blocked capture; future reads
can observe normal saving. Unknown/malformed successful responses produce a fixed error rather than
echoing raw diagnostics. English/Chinese README, repository rules, stop/recovery notes and wire
contract document the behavior.

Evidence:

- Real CLI → authenticated Server → OpenSSH → forced-command gateway → shipped Worker/Helper
  acceptance passed **2 tests in 56.29 seconds**, including frozen and actual 1 KiB runtime-quota
  cases, daemon restart, all original bytes/metadata, and mid-transfer SSH-key revocation
  (`/tmp/skill-capture-pending-ssh-live.log`). The quota case now observes a committed stop receipt
  with null digest and `quota_exceeded` before export. No finalization/checkpoint is manufactured.
- Server focused HTTP/service/persistence regressions passed **111 tests, 3 PostgreSQL-only skips**
  in 54.18 seconds (`/tmp/skill-capture-pending-server-regression.log`). Separate real PostgreSQL
  pending/frozen races, pending stop-result replay and migration tests passed **15 tests in 13.29
  seconds** (`/tmp/skill-capture-pending-postgres-verified.log`). Existing termination/startup races
  passed **3 cases** during the initial PostgreSQL run.
- The full Alembic chain upgraded an empty disposable PostgreSQL database through 0053
  (`/tmp/skill-capture-pending-alembic.log`). The formal migration test preserves old digests,
  rejects invalid SQL combinations, refuses lossy downgrade and permits downgrade after capture
  recovery. Its private transactional schema prevents unrelated tests' retained pending rows from
  invalidating the initial legacy-schema setup.
- Server Ruff lint/format, Mypy over **624 sources**, Chinese docstrings and whitespace checks
  passed; formatter checked **678 Python files**. Initial migration-test failures were fixture
  setup issues (timestamps, absent snapshot and shared pending rows), corrected without weakening
  the actual migration's preservation rules.
- Node full quality passed at **62.7% host statement coverage**
  (`/tmp/skill-capture-pending-node-quality.log`). Focused race-enabled API/Worker/export/Helper
  tests passed (`/tmp/skill-capture-pending-node-race.log`), including exact response validation,
  failed-response replay, no transfer on capture failure, eventual transfer, independent export
  classification and exact stop identity. Linux ARM64 vet passed for affected packages.
- Actual Linux Helper tests passed for pending observation, uncertain evidence rejection, quota
  retry/recovery and existing reconciliation contracts (`/tmp/skill-capture-pending-helper-linux.log`).
  Explicit stop queue tests verify a failed stop/capture response followed by fresh pending evidence
  and immutable null-digest replay (`/tmp/skill-capture-pending-stop-queue.log`).
- CLI full quality passed **581 test executions, zero failures/ignored tests**, including nine
  session-saving contracts, rustfmt, Clippy with warnings denied, shell/cache/release contracts and
  whitespace (`/tmp/skill-capture-pending-cli-quality.log`). Tests cover finite errors, malformed
  durability combinations, prompt blocked-wait exit and later local-durable recovery.

All task-owned PostgreSQL/Helper/SSH containers and SSH images were removed; the SSH runner also
cleaned its isolated key/agent and private coordination data. No model credentials or inference were
used. No commit, release, deployment or capability advertisement occurred. This completes the
capture-pending status increment, not the overall Skill Manager. Real Claude learning/inheritance,
full CLI session lifecycle acceptance, Docker Sandbox, interrupted/previous-boot backend migration
repair and source rollback attestation, export beyond fixed protocol bounds, and the final full
requirement audit remain unfinished. The overall goal remains active.

## 2026-09-25 — full synthetic Native CLI lifecycle acceptance

The new opt-in `tests/test_skill_cli_lifecycle_live.py` in Server drives the current host
agent-remote/fclaude binaries through local `skill add`, account-effective selection, `fclaude new`,
workspace synchronization, forced-command SSH attach, runtime writes, explicit stop/publication,
Worker/Helper restart, independent-session inheritance, reclamation and display-session deletion.
The original snapshot operation remains queryable as published with process status deleted.

This uses official Mutagen 0.18.1 with pinned platform SHA-256, per-run device/token/SSH identity,
the production Server routes and shipped Node/Helper units. Only initial identity and explicit
capability setup use test fixtures; no creation, stop, publication or cleanup receipt is injected.
A deterministic synthetic tool verifies text and binary contents, source deletion, mode 0750,
empty directories, a relative symlink, modified instructions, account-local skill creation and both
managed directory aliases. The workspace marker travels through actual Mutagen in both directions.
The original source is read-only; runtime edits prove writable session materialization.

The first full flow found a production CLI parsing defect: `fclaude --home PATH stop SESSION`
entered default run/attach, and a global option before `new` similarly hid the explicit command.
A new regression failed with Run instead of Stop before the fix. Clap now prioritizes explicit
subcommands without the conflicting global-argument rule. Two focused regressions cover command
routing and unchanged direct/model-flag/`--` prompt passthrough. Both README languages describe
option placement. The fixture now handles the supervisor's terminal shutdown request and exits zero;
its earlier signal-only termination correctly yielded unclean/detached state rather than publication.

Acceptance and verification:

- Full synthetic CLI lifecycle: **1 passed**, 30.47 seconds;
  `/tmp/skill-cli-lifecycle-live-graceful.log`.
- Existing frozen and actual runtime-quota SSH exports: **2 passed**, 39.20 seconds;
  `/tmp/skill-cli-lifecycle-ssh-regression.log`. This verifies shared runner/support changes.
- Server stop/status regression: **10 passed, 2 opt-in lifecycle skips**;
  `/tmp/skill-cli-lifecycle-server-regression.log`. Those skipped tests are separate from the
  explicitly executed CLI and export acceptance above.
- Server global Ruff lint/format (680 files), Mypy (626 sources), Chinese docstrings and whitespace
  checks passed. No new full Server suite is claimed for this increment.
- Node full quality gate passed at **62.8% statement coverage**;
  `/tmp/skill-cli-lifecycle-node-quality.log`. Linux ARM64 lifecycle-package compile/vet and shell
  syntax checks also passed.
- CLI routing regression reproduced the defect in `/tmp/skill-cli-command-routing-before.log`;
  the fixed launcher tests passed in `/tmp/skill-cli-command-routing-fixed.log`.
- CLI full quality gate passed **583 test executions, zero failures/ignored tests**, including
  formatting, denied-warning Clippy, shell/cache/release and whitespace checks;
  `/tmp/skill-cli-lifecycle-cli-quality.log`.

The short Mutagen data root, CLI credential root and SSH keys are cleaned on setup/teardown failures.
Successful runs removed their test containers/images and temporary processes. Task-owned archive and
cross-compiled test binary were removed; pre-existing host SSH agent and Mutagen were left intact.
No commits, releases, deployment or production capability advertisement occurred.

This closes the synthetic CLI/SSH/sync/session-command lifecycle gap. The complete design goal
remains unfinished: real Claude inference/learning inheritance and account enrollment, full remaining
command/backend audit, Docker Sandbox lifecycle, interrupted/previous-boot migration repair and
source rollback attestation, export beyond fixed protocol bounds, and default-limit capacity proof
are separate work. Effective selection in this run explicitly retains model_loaded=false.

## 2026-09-25 — actual default-limit copies/capture and Helper deadline repair

Added Node's opt-in `tests/linux_skill_capacity_test.sh` with independent `entries`, `bytes` and
`helper` modes. Defaults are unchanged: 1 GiB per item, 10 GiB directory, 100,000 entries and the
published disk reserves. The entry case uses 100,000 distinct files/digests; the 10 GiB case uses ten
distinct large binary objects plus valid instructions, so deduplication cannot reduce it to 1 GiB.
Every source byte is streamed into ordinary files. All frozen objects are read and hashed and the
complete source/frozen manifests and reopened finalization identity are verified.

This work found two concrete gaps:

- Every sequential file copy allocated another 64 KiB scratch buffer. Materialization/frozen-copy
  loops and capture now reuse operation-local buffers. For the same 100,000-file case, cumulative
  allocations at materialization fell from **7,635,568,192 to 1,082,029,280 bytes** (about 86%).
  Hashing, ownership/modes, per-object fsync, complete verification and atomic publication remain.
  No wall-clock speedup is claimed: concurrent verification affected the later timing.
- Client and Helper reconciliation each imposed a generic **30-second** deadline. Actual default-limit
  socket capture failed after **33.71 s** including setup. Observation/admission-loss draining now use
  a shared **15-minute** ceiling, while earlier caller deadlines and disconnect cancellation win.
  The same-scale socket test passed in **149.82 s**, including **141.344 s** in reconciliation.
  All 100,000 output manifest entries are checked; no finalization receipt is seeded.

Capacity results (Linux ARM64; each test container limited to 2 CPUs/2 GiB):

| Case | Materialize | Freeze | Verify every retained object | Result |
| --- | --- | --- | --- | --- |
| 100,000 distinct files | 55.121 s | 92.190 s | 7.549 s | Passed |
| 1,073,741,824 expanded bytes | 1.952 s | 3.747 s | 0.670 s | Passed |
| 10,737,418,240 expanded bytes | 14.515 s | 35.779 s | 8.301 s | Passed |

The entry case ran on Docker's overlay filesystem. A direct macOS shared-directory byte test correctly
failed Linux ownership verification; checks were not weakened. Final byte tests used a dedicated
40 GiB ext4 loop image backed by the host filesystem, avoiding modifications to the user's Docker
disk. Runtime/object files were fully written, not sparse. Peak process RSS was 314,588 KiB in the
entry case and 7,708 KiB in the byte case; these figures exclude filesystem cache charged to the
container. The Helper-capacity fixture uses real authenticated Unix sockets and complete production
capture with controlled runtime/systemctl exit observations, not a full runtime launch proof.

Evidence:

- `/tmp/skill-default-capacity-entries.log` and `-entries-reuse.log`: actual pre/post buffer-reuse
  entry-limit runs passed. The latter completed in 160.98 seconds including verification/replay.
- `/tmp/skill-default-capacity-bytes-ext4.log`: both byte cases passed, 72.13 seconds total.
- `/tmp/skill-default-capacity-helper-before.log` reproduced the deadline defect;
  `/tmp/skill-default-capacity-helper-fixed.log` passed after both boundaries were corrected.
- `/tmp/skill-default-capacity-linux-regression.log`: **34 top-level actual Linux tests passed** for
  copy/capture/finalization, permission independence, corruption and session journal behavior.
- `/tmp/skill-default-capacity-node-quality-final.log`: full Node quality gate passed at **62.8%**
  statement coverage. Linux ARM64 vet, shell syntax and whitespace checks passed.
- `/tmp/skill-default-capacity-race.log`: cancellation/deadline and strict observation-response tests
  passed with the race detector. Both observation and admission-loss draining use the public client
  timeout path in those cancellation checks.

Current-state Docker prerequisite inspection still reports the installed sandbox plugin removed;
no standalone sbx is present. No backend capability, commit, release or deployment was added.
The full design goal remains active: full default-limit HTTP/SSH/Server lifecycle (including
100,000 distinct object transfers and Server storage quotas), real Claude learning, Docker Sandbox,
interrupted/previous-boot backend repair, source rollback attestation and recovery beyond fixed
export bounds remain open. See Node `docs/skill-capacity-acceptance.md` for reproducible commands.

## 2026-09-25 — bounded frozen-object readers and 100,000-descriptor acceptance

Worker finalization upload and frozen SSH export now use a dedicated persistent Helper reader,
`read_skill_finalization_objects`. Previously each object request re-opened/revalidated the full
session baseline and frozen manifest, making complete transfer quadratic in entry count. The new
reader validates the original Native capture and full manifest once, builds a bounded digest index,
and holds descriptor anchors for one connection (15 minutes, at most 100,000 object requests).

The initial manifest FD transfers the existing shared kernel lock to the client, preserving read
protection after Helper shutdown. Every object has original membership/binding/classification,
read-only/CLOEXEC/single-link checks, independent shared flock, and manifest/directory metadata
rechecks. Consumers still hash/classify bytes and retain existing Server authorization. Lifecycle
serialization ends after initial validation; an owned input pump cancels lock waiting and closes on
EOF/expiry. Earlier caller deadlines apply. There is no global cache, new journal, host path input,
recapture fallback, persistence acknowledgement or capability advertisement.

Validation:

- `/tmp/skill-reader-capacity-live.log`: actual 100,000 unique-file Helper capture and **100,000
  descriptor reads**, hashing every received object's bytes, passed in **126.91 s** under 2 CPU/2 GiB
  limits and unchanged default policies. Capture took **88.556 s**; object transfer/verification took
  **31.298 s**. No full pre-change object-loop run was measured, so no speedup ratio is claimed.
- `/tmp/skill-reader-linux-regression-final.log`: **66 top-level Linux tests passed**, including new
  reader corruption/reclamation/shutdown and descriptor-leak/cancellation tests. Three separate
  privileged mount/physical-ENOSPC opt-ins skipped; this run does not claim those acceptance cases.
- `/tmp/skill-reader-linux-race.log`: actual Linux reader, malformed-frame/cancellation, skillmanager
  and Worker transfer tests passed with the race detector. Its export selector matched no tests;
  `/tmp/skill-reader-export-race.log` separately passed the complete export package on the host.
- `/tmp/skill-reader-node-quality.log`: full Node gate passed at **62.1%** statement coverage.
  Linux ARM64 vet passed for affected packages and the lifecycle fixture.
- `/tmp/skill-reader-ssh-fixed.log`: **2 real CLI/SSH export cases passed**, including frozen input
  through the new reader and the separate runtime-quota stopped-work recovery path. An initial
  run failed its daemon UID check before export. Shipped Type=simple units may report started
  before the child execs/applies its UID; the fixture now awaits expected executable plus UID.

The additional full CLI lifecycle rerun initially retained an unclean/detached stop rather than the
expected clean publication (`/tmp/skill-reader-cli-lifecycle.log`). A diagnostic rerun completed the
entire lifecycle in 132.47 seconds (`/tmp/skill-reader-cli-lifecycle-diagnostic.log`), observing the
synthetic tool receive the intended interrupt byte 3. A further monitored run passed in 127.14 seconds
(`/tmp/skill-reader-cli-lifecycle-monitored.log`, process observations in
`/tmp/skill-reader-cli-monitor.log`). The original intermittent stop failure has not been attributed
to a specific cause and must not be treated as solved by these successful retries. Test-only fixed byte evidence is saved in the
synthetic workspace, not production logs or skill content.

The full design remains incomplete: full default-limit HTTP/SSH/Server capacity and quotas, real
model learning/account enrollment, Docker Sandbox lifecycle, interrupted/old-boot backend ownership
repair/source rollback attestation, and export beyond fixed protocol bounds remain separate work.
No commit, release, deployment or capability advertisement occurred.

Next confirmed scalability boundary: Server `services/skills/content.py` still reconstructs the full
upload manifest and unique-file map in both `prepare_file` and `put_file`; repeated object HTTP
requests therefore retain a separate quadratic validation cost. This was a read-only source finding,
not changed or capacity-tested in this increment. The new Node reader does not fix that Server path.
All increment-owned test containers/images and temporary runner scripts were removed; evidence logs
remain. No live test handle is left running.

## 2026-09-26 — indexed Server uploads, retention capacity and long-reader replacement

This increment adds migration `0054_skill_upload_object_index`, the owner/upload/tree/scope-bound
`skill_upload_objects` declaration projection, and an atomic version/count marker on original uploads.
New admission creates the complete unique-file index in the original quota transaction. Legacy
uploads backfill once under the user lock after complete canonical manifest/digest verification.
Single-file prepare/put loads only current lease metadata and the selected validated entry. Node
finalization file authorization retains exact Node/snapshot/stopped-session/current-attempt checks
while avoiding the previous whole-user collection during every object request. Completion still
checks original full-manifest identity and all bytes; terminal phases remove projection rows and
preserve original audit metadata. No new public API or capability advertisement is introduced.

The real 100,000-unique-object HTTP test exposed another default-capacity defect: retention counted a
full 20+ MiB upload manifest against a 16 MiB aggregate metadata guard and returned 500 before upload.
Retention now reads only counted digest references for indexed staged inputs. Missing/extra references
fail the entire analysis, and those rows consume the unchanged complete-index row budget. Legacy
staged manifests retain full validation/JSON budget; terminal manifests are audit-only. Retention
and GC forecasting now share the same active-upload interpretation, including zero-reservation and
cross-category consumers. The first full Server gate exposed the remaining old GC forecast reader;
that failure was reproduced, fixed and covered by focused regressions before restarting the gate.

Default-scale HTTP duration also outlives the new Helper reader's 15-minute connection. Node Worker
now renews only the exact-capture reader between files after ten minutes. The replacement hold is
acquired before releasing the old one, and the outer whole-upload hold remains. Slow existing file
FDs survive connection expiry. This changes no Server lease, original capture, byte verification or
completion acknowledgement. SSH's separate complete-export deadline is unchanged.

Completed evidence:

- `/tmp/skill-upload-index-postgres-gc-final.log`: **89 real PostgreSQL tests passed**, including all
  migrations through 0054, upgrade/downgrade preservation, exact composite foreign keys, legacy
  backfill/rollback/concurrency, owner isolation, invalid declarations, expired leases, quota release,
  retention and GC/compaction/deletion races. The runner removed its own database and temporary root.
- `/tmp/skill-upload-index-gc-regression.log`: **44 passed, 1 PostgreSQL-only skip** on host SQLite
  after unifying retention/GC declaration interpretation.
- `/tmp/skill-upload-index-cli-lifecycle.log`: real CLI/HTTP/SSH/Mutagen install, stop/publication,
  restart/inheritance, reclamation and deletion passed in **133.54 s** with indexed Server uploads.
  This run preceded the later Worker reader-rotation change.
- `/tmp/skill-upload-index-cli-rotation.log`: the same real complete lifecycle passed again in
  **132.98 s** with the new Worker reader replacement. Its process and test resources are reaped.
- `/tmp/skill-upload-reader-rotation-race.log`: focused Worker rotation/transfer race checks passed.
- `/tmp/skill-upload-reader-rotation-quality.log`: full Node gate passed at **62.1%** coverage.
  `/tmp/skill-upload-reader-rotation-linux-vet.log`: Linux ARM64 Worker vet passed.

Capacity run and full-gate status (latest continuation below):

- **81532**: `AGENT_REMOTE_RUN_SKILL_UPLOAD_TEST=1 AGENT_REMOTE_SKILL_UPLOAD_TEST_MODE=capacity
  tests/postgres_skill_upload_test.sh`; log `/tmp/skill-upload-index-capacity-final.log`. Real Uvicorn,
  real authenticated Node routes and PostgreSQL; unchanged defaults, 100,000 distinct ordinary files,
  all file requests, zero full-upload-manifest SQL reads required during the loop, complete-byte
  verification and index retirement after persistence. Fixture ceiling is three hours. DB container
  has 2 CPUs/1 GiB; Server/client/filesystem run on the host without artificial CPU/memory limits.
- The original full Server gate **11803** finished and is reaped. Its log
  `/tmp/skill-upload-index-quality-final.log` reports 1,781 passed, 91 skipped and two stale schema
  expectation failures; see the correction and fresh full-gate handle in the next section.

The earlier capacity run `/tmp/skill-upload-index-capacity-indexed-retention.log` reached its first
10,000 objects in 419.642 seconds and continued to about 17,000 before deliberate cancellation: its
one-hour test-fixture deadline was too short at observed throughput. It was not a capacity pass.
The owned process/container were stopped and cleaned before the complete three-hour-ceiling rerun.
No production deadline or input size was relaxed. Other initial logs record the metadata-budget
failure (`/tmp/skill-upload-index-capacity-diagnostic.log`) and the interrupted first Server gate
(`/tmp/skill-upload-index-quality.log`); neither is counted as final acceptance.

The full design remains incomplete. In addition to the live gates above, actual combined default-limit
Worker/Helper/Server lifecycle, Server byte quotas, large SSH export, real model learning/enrollment,
Docker Sandbox, interrupted/old-boot backend repair/source rollback attestation, fixed-bound export
recovery and the previously observed intermittent unclean CLI stop remain unclosed. The read-only
review also confirms Server content downloads still load full tree manifests in `content.read_file`;
this is a separate scalability boundary for large preparation/download loops. No commits, releases,
deployment or production capability advertisement occurred.

## 2026-09-26 — real Server default byte-capacity acceptance

Added opt-in `bytes` and `packages` modes to Server `tests/postgres_skill_upload_test.sh`.
They use real loopback Uvicorn, production authentication/routes, independent PostgreSQL
transactions, fully written random ordinary files and unchanged production storage policies.
No sparse sources, virtual byte readers, duplicated content or reduced quotas stand in for capacity.
The runner owns and cleans its database container and temporary source/content filesystem.

The package case reserves 41 manifests containing 205 distinct files at once. Every file stays
within 10 MiB and each package within 50 MiB. It transfers and completes exactly 2 GiB, cross-checks
SQL object sums and accounting after every completion, rejects one-byte excesses at staged and
retained capacity, rejects per-file/per-package excesses, and leaves runtime accounting zero.
At unchanged defaults the retained package and staging bounds coincide; this is evidence for their
combined admission behavior rather than isolation of the staging-only branch.

- `/tmp/skill-package-byte-capacity.log`: **1 passed in 49.46 s**. Fixture generation and all network
  work completed; process **85287** reaped, task-owned container/temp directory cleaned.
- `/tmp/skill-byte-capacity-default-optout.log`: both new expensive tests skip unless explicitly
  enabled, **2 skipped**. This is an opt-out check, not a capacity pass.
- Full Ruff format/lint, mypy (**637 source files**), docstring, shell syntax and whitespace checks
  passed after adding the new fixtures and optional real user authentication to the shared HTTP helper.

The first runtime byte test completed successfully: `/tmp/skill-upload-byte-capacity.log`,
**1 passed in 300.74 s**. Its enclosing runner then exited 2 because this increment edited the
shared shell script while Bash still had it open. The EXIT trap removed its own database/container
and temp root; handle **64400** is reaped. The current script passes `bash -n`. The fresh full
runtime case verified the final runner as well as pytest: `/tmp/skill-upload-byte-capacity-final.log`, **1 passed in 304.07 s**, enclosing process
exit **0**. Handle **11678** is reaped and its database/temp root were cleaned. The long object-count
runner's open script was waiting at its original EOF. The finished repository script was atomically placed on a
new inode and the detached old descriptor's EOF restored at that observed offset, preserving the
already running pytest workload and original cleanup handler without replaying any requests.

The runtime case constructs ten valid 1 GiB skills in one exact 10 GiB directory. A second original
stopped snapshot supplies enough distinct bytes to fill the same user's retained runtime total, including
its existing baseline, to exactly 20 GiB. Both uploads reserve before transfer. The test checks item,
directory and user one-byte excesses, staged-versus-retained accounting, full-byte completion,
idempotent completion replay, physical object sizes and terminal upload-index cleanup. Both complete
directories passed in the first pytest run, ending at exactly **21,474,836,480 retained runtime
bytes**. The fresh run repeated all transfers, completions, replays and quota refusals, reaching the
same exact retained total before its successful runner cleanup.

The earlier full Server run **11803** is now reaped: **1,781 passed, 91 skipped, 2 failed**, with
**82.98% coverage** (above 70%). Both failures were stale `tests/test_persistence.py` expectations:
the table inventory omitted `skill_upload_objects`, and the migration graph still expected head
0053. Those explicit expectations now match the existing 0054 migration; no production behavior
was changed to satisfy them. `/tmp/skill-upload-index-persistence-final.log`: **17 passed in 1.61 s**.
A fresh full gate is running as **19015**, log `/tmp/skill-upload-index-quality-schema-final.log`.
Do not count the earlier failed gate as a full pass or start a duplicate of the new run.

The **81532** 100,000-object run remains live, with 48,000 requests observed in
`/tmp/skill-upload-index-capacity-final.log`. Its full completion is still required.

Review also strengthened the directory-only negative boundary: append one root auxiliary byte to
an otherwise exact 10 GiB directory, keeping every individual skill within 1 GiB. The item-only
negative case separately keeps the whole directory exactly 10 GiB. This prevents either quota guard
from masking absence of the other. The repeat including this stronger assertion passed:
`/tmp/skill-upload-byte-capacity-isolated-limits.log`, **1 passed in 294.72 s**, enclosing runner
exit **0**. Handle **13050** is reaped and its database/temp root were cleaned. All bytes were
regenerated, transferred and completely verified again. Final Ruff format/lint, mypy, docstring and
whitespace checks pass; the separate full test-gate rerun remains live as stated above.

These Server tests run on the host without client/Server CPU or memory caps; PostgreSQL alone has
2 CPUs/1 GiB. Runtime writer exit is simulated after real snapshot reservation. Separate entry-count
and byte cases do not prove a combined 100,000-entry/10 GiB Worker/Helper/Server pipeline, actual
runtime launch, account publication, SSH export or model learning. These default Server byte limits
now have full actual network/storage evidence. The full design goal remains active and incomplete:
combined default-scale lifecycle, large SSH export, real model learning/enrollment, Docker Sandbox,
interrupted/old-boot backend repair/source rollback attestation, fixed-bound export recovery, download
scalability and the intermittent unclean CLI stop remain separate work. No commit, release, deployment or
production capability advertisement occurred.

## 2026-09-26 — tree-member downloads and renewed stop investigation

Per-file content, Node preparation and deployment downloads now authorize through the existing
exact owner/category/tree/object reference relation, created atomically by whole-tree completion.
They read verified object metadata rather than reconstructing the full canonical directory JSON for
every file. Manifest endpoints keep the full path/mode/link representation. All file bytes still
undergo size/SHA-256/type verification. The owner lock, exact original Node/task/snapshot/attempt and
lease checks, and existing post-copy reauthorization remain in place.

The new `SkillTreeFileRepository` queries unavailable objects across both categories against every
member of the original tree; it does not weaken the barrier to the requested file alone. Migration
`0055_skill_object_availability` adds only the partial `skill_object_unavailable_idx` access path on
owner/digest where status differs from available. No content rows, quota, clocks, protocol fields,
retention roots, or public capabilities are changed. `tests/test_persistence.py` now names the actual
0055 head and required index. Server `docs/skill-tree-downloads.md` records the transaction contract.

Completed evidence:

- `/tmp/skill-tree-download-regression.log`: **110 passed, 1 PostgreSQL-only skip**, covering owner/
  category/tree binding, whole-tree and cross-category deletion barriers, unrelated markers, missing
  requested references, duplicate aliases, disk corruption, actual Node routes with zero manifest
  SELECTs, existing deployment authorization and lease/copy revocation tests.
- `/tmp/skill-tree-download-postgres.log`: **172 passed in 218.58 s**, all migrations through 0055,
  real index upgrade/downgrade preservation, upload/content/GC/compaction and Node authorization
  regressions. Handle **65440** is reaped; its database and temporary root were cleaned.
- Full format/lint, mypy (**641 source files**), docstrings, shell syntax and whitespace checks passed.
- `/tmp/skill-tree-download-index-usage.log`: a read-only PostgreSQL statistics observation during
  the live download test confirms the unavailable-object partial index is used repeatedly. This is
  query-path evidence, not a substitute for completing the full capacity test.

Live runs; poll these exact handles rather than starting another copy:

- **81532** — **completed and reaped, runner exit 0**, log
  `/tmp/skill-upload-index-capacity-final.log`: **1 passed in 4224.21 s**. All **100,000** distinct
  objects uploaded in **4157.912 s**, with **zero full-manifest reads** during the object loop.
  Complete and all-byte verification took **52.444 s**. Owned PostgreSQL/container/temp-root cleanup
  ran successfully. This code predates 0055; upload behavior is unchanged by the download optimization.
  Node `skillRequestLimit` already overrides the ordinary 15-second HTTP timeout with **10 minutes**,
  while preserving an earlier caller deadline. The measured completion does not expose that suspected
  timeout defect. This Server transport acceptance is not combined Worker/Helper lifecycle proof.
- **7379** — new default 100,000-file download acceptance, log
  `/tmp/skill-tree-download-capacity.log`, latest observed **47,000** files; still running. Its actual fixture took
  **243.156 s** to write unique ordinary files, fully verify/commit the tree and reserve a snapshot.
  Each response must pass size/hash/ETag checks, no full manifest SELECT is allowed in the loop,
  the same 30-second task lease is renewed through the actual HTTP endpoint, and final revocation
  must deny further reads. Initial account-head seeding and task claiming are fixtures, not proofs
  of real account publication or Worker scheduling. Three-hour test ceiling; unchanged defaults.
- **21520** — current full Server gate, `/tmp/skill-tree-download-quality.log`. Static gates passed;
  pytest remains live. The earlier **19015** gate was deliberately interrupted after this production
  change because it had loaded the old code. It is reaped (interrupt caused pytest tmpdir teardown
  noise/exit 1); `/tmp/skill-upload-index-quality-schema-final.log` is not a full passing gate.

The actual CLI/HTTP/SSH/Mutagen lifecycle rerun failed its first stop with unclean/detached content:
`/tmp/skill-tree-download-cli-lifecycle.log`, **1 failed in 128.04 s**, handle **72137** reaped and
owned daemons/resources cleaned. This repeats the earlier unresolved intermittent failure, not a
complete lifecycle pass. Its synchronized `project/stop-byte` contained exactly `3`; this fixed-byte
evidence is preserved in `/tmp/skill-tree-download-cli-stop-byte.log`. The synthetic tool therefore
received the requested interrupt, but the cause of the unclean exit classification remains unknown.

A diagnostic-only opt-in, `AGENT_REMOTE_TEST_NATIVE_STOP_OBSERVATIONS=1`, now installs wrappers solely
inside the disposable Native CLI test image. They preserve command results and record only bounded
numeric tmux pane exit observations plus fixed systemd state/result/code fields. No arguments,
private paths, tokens, configuration or tool stdout are logged. Cleanup copies this bounded record
to the fixture's `node/control/native-observations` with mode 0600 before removing the container.
The first diagnostic CLI run **82744** passed in **133.11 s** and is reaped, with owned runtime
resources cleaned (`/tmp/skill-native-stop-observed.log`). Both normal pane exits were `1|0`, followed
by systemd success/code 1/status 0. Its record is preserved in
`/tmp/skill-native-stop-observations-pass.log`. This verifies the diagnostic fixture, not a fix.

**14779** completed its three bounded diagnostic cases: **126.85 s**, **127.83 s**, **125.64 s**,
all passed. The runner exited 0, is reaped and cleaned its temporary root. Logs are
`/tmp/skill-native-stop-repeat-N.log` and corresponding `.trace` (N = 1–3, trace mode 0600). All
three traces show two normal `1|0` pane exits each. Successful diagnostic retries do not resolve
the intermittent failure without cause and regression proof. Test-only observations now additionally
record tmux interrupt/cleanup and systemd signal/stop results, plus nearby fixed cgroup population.
The population sample is diagnostic only, not the Helper's exact read or an authorization change.
Handle **55946** runs at most three enhanced diagnostic cases, stopping on failure, in
`/tmp/skill-native-stop-detailed-N.{log,trace}`; do not duplicate it.
No production Node/Helper behavior has been changed for this investigation.

The full design remains active and incomplete. In addition to the live checks and stop investigation,
combined default-scale Worker/Helper/Server lifecycle, large SSH export and fixed-bound recovery,
real model learning/enrollment, Docker Sandbox lifecycle, interrupted/old-boot ownership repair and
source rollback attestation remain required. Other user conflict-resolution paths may still inspect
full manifests; this increment specifically removes that cost from shared file copying and the
high-volume snapshot/deployment authorization paths. No commit, release, deployment or production
backend/capability advertisement occurred.

## 2026-09-26 — preparation transfer budget and actual daemon capacity pipeline

The previous full Server gate **21520** completed successfully and is reaped:
`/tmp/skill-tree-download-quality.log`, **1788 passed, 95 skipped in 1767.93 s**, coverage
**83.03%**, all static/docstring gates passed. This includes migration 0055 and the optimized
download authorization; the subsequently added opt-in pipeline test was checked separately.

The measured real download loop exceeded 30 minutes before 70,000 files, exposing a separate
Node compatibility issue: snapshot/deployment preparation had a ten-minute *total* Helper budget.
Both client and server share a three-hour absolute preparation deadline now. Earlier caller
deadlines, bounded individual HTTP calls, exact-attempt renewal and cancellation/disconnect
remain mandatory; no receipt or authority rule changes. The lifecycle lock remains held during
preparation, so other Helper mutations can wait behind a large transfer. This change does not
claim throughput improvement or whole-pipeline acceptance.

New protocol regression tests cover both client callbacks, server stream lifetime, earlier
caller deadlines and blocked-input cancellation. Focused tests passed. Full Node gate **52375**
passed and is reaped (`/tmp/skill-preparation-budget-node-quality.log`, **62.2% coverage**,
including installer/consistency checks). The new pipeline fixture files were added afterward;
Linux cross-compilation, shell parsing and whitespace checks passed separately. Focused race
handle **89508** and actual Linux preparation regression handle **51175** are still to be reaped.

Enhanced stop diagnostic loop **55946** completed and is reaped: **124.51**, **122.47**,
**122.96 seconds**, all passed. Every pane exit was normal; tmux interrupt/cleanup and systemd
signal/stop returned zero; terminal population samples were absent or zero. Logs and mode-0600
traces are `/tmp/skill-native-stop-detailed-N.{log,trace}`. Its temporary root is cleaned. These
observations do not identify or fix the earlier intermittent unclean stop.

A new opt-in default-entry pipeline runs the real non-root Worker, privileged Helper, Native
systemd runtime, HTTP Server and PostgreSQL. Its tool writes exactly **100,000 entries / 99,999
unique files**, waits for actual capture/upload/publication, restarts daemons, verifies every
file in an independent materialized session and waits for that session's clean publication.
Only registration, identity and unreleased capability admission are fixture-controlled. No
publication, claim, exit or preparation receipt is seeded. Default policies remain unchanged.
PostgreSQL alone has 2 CPU/1 GiB limits; Node/host Server are unbounded. This is entry capacity,
not a combined 10 GiB workload, model learning, SSH export or reclamation proof.

The first run **45632** failed in **18.01 s** because the synthetic test tool used its host
artifact path instead of the Native mount; it exited and cleaned its resources. The fixture
path and a final storage-category assertion were corrected before rerun. Handle **23726**
is now live: `/tmp/skill-default-pipeline-capacity-final.log`. Do not duplicate it. The existing
download handle **7379** was last observed at **86,000** files and remains live.
Reproducible instructions and evidence limits: Server `docs/skill-pipeline-capacity.md`.

The goal remains active and incomplete. No commit, release, deployment, production capability
advertisement or substitute for the unavailable Docker Sandbox backend occurred.

Terminal updates for the runs above:

- **7379**: **passed and reaped, runner exit 0**. `/tmp/skill-tree-download-capacity.log`: all
  **100,000** file downloads completed in **2494.944 s**, **zero full-manifest SELECTs**, **248**
  exact-attempt HTTP lease renewals. Complete case **1 passed in 2744.16 s**, including fixture
  persistence/reservation and final revocation rejection. Owned PostgreSQL container and temp
  root are removed. This is Server download/authorization capacity, not daemon materialization.
- **89508**: focused race checks passed and are reaped. Runtimehelper tests exercised the new
  deadline and existing preparation cancellation contracts; the supplied Worker name filter
  matched no tests, so no Worker-race evidence is claimed from that command.
- **63379**: intentional old-budget Go overlay reproduced failures for both client preparations
  and the Helper stream. The overlay changed only test compilation; source remained at the fix.
  `/tmp/skill-preparation-budget-before.log` is expected failure evidence, not a quality pass.
- **87491**: actual root Linux preparation regression passed and is reaped, **22 top-level tests,
  zero skips**, `/tmp/skill-preparation-budget-linux-complete.log`, disposable container removed.
  Earlier launch handles **51175** and **64465** failed before tests because the borrowed fixture
  image had already been removed; both are reaped and are not test failures or acceptance passes.
- **23726** and **41976** are reaped failures, **19.39 s** and **19.23 s**, respectively. The fixed
  synthetic tool's raw filesystem count incorrectly included the system-reserved mount root.
  The diagnostic recorded only `cardinality:AssertionError`. The fixture now excludes exactly
  `ego-browser` and `agent-remote-device`, matching production user-manifest exclusions; the
  final canonical manifest must still contain exactly 100,000 entries. Resources were cleaned.
- **10469** is the current and only live pipeline attempt,
  `/tmp/skill-default-pipeline-capacity-original-count.log`. It has entered actual finalization
  after writing the complete workload. A read-only observation found 100,001 raw work entries
  (including the reserved system root), with no published capture yet. Do not duplicate it.

The separate upload and download capacity passes plus the preparation deadline fix do not yet
prove this full pipeline. The intermittent stop investigation also remains unresolved.

Latest pipeline transition: **10469** reached a verified clean original capture and actual
Server `upload_pending` (99,999 frozen ordinary files) before intentional interruption. The
fixture still used its smoke-case 20-second session API timeout; large snapshot reservation may
perform full content verification, so the capacity case now explicitly allows ten minutes,
matching production Skill HTTP. Other lifecycle tests keep their 20-second default. Linux
cross-compilation, Python fixture syntax, shell parsing and whitespace checks passed.

Uvicorn consumed the initial SIGINT without cancelling the outer test, so only the exact
owned Node process group and then pipeline runner group were terminated. **10469** is reaped
(exit 143); its Node container/image, PostgreSQL container and temporary root are verified absent.
Its interrupted log is not a capacity pass. The current sole pipeline handle is **36891**,
`/tmp/skill-default-pipeline-capacity-bounded.log`; poll it without restarting.

The corrected Worker race selection **21319** also passed and is reaped:
`/tmp/skill-preparation-budget-worker-race.log`. It covers snapshot preparation, deployment lease
loss and committed-receipt/renewal races. Server fixture static/type/docstring gates **32581**
passed and are reaped. All earlier upload/download/full-quality/diagnostic jobs are terminal.

Final verification for this increment: full Node gate **36144** passed after all fixture changes
and is reaped (`/tmp/skill-preparation-budget-node-quality-fixtures.log`, **62.2% coverage**,
installer and consistency gates passed). Pipeline default opt-out **63316** passed and is reaped
(`/tmp/skill-pipeline-default-optout.log`, **1 skipped in 2.46 s**).

Current **36891** has now reached a clean actual captured input: a read-only database observation
shows one `upload_pending`, `unclean=false` finalization, matching the Helper's retained
`upload_pending` record. The sole task-owned live containers at this checkpoint are
`agent-remote-pipeline-test.ahmrsM` and `agent-remote-ssh-export.cY9ZkL`; their runner owns cleanup.
Current log: `/tmp/skill-default-pipeline-capacity-bounded.log`. Full publication, restart, second
materialization and second publication remain pending. No completion claim is made.

## 2026-09-26 — default-entry real SSH export acceptance in progress

The prior goal turn was **progress**: both 100,000-object Server acceptance runs finished,
preparation timeout behavior changed with regression proof, and the full daemon capacity
fixture began actual upload. Handle **36891** remains live and was polled directly. A subsequent
read-only observation counted **21,194** real files / **529,876 bytes** in its private Server
object store, confirming transfer progress rather than only a retained pending status.

Added a separate opt-in `AGENT_REMOTE_RUN_SKILL_SSH_EXPORT_CAPACITY=1` to the existing real
SSH test. It generates exactly **100,000 user entries / 99,997 unique file objects** beside
existing binary data, permission changes, an empty directory and a relative symlink. Both
frozen-default and deliberately 1 KiB runtime-quota recovery cases use real daemons, actual
SSH, periodic Server authorization, full CLI bundle verification and revoked-key rejection.
Source byte/inode/mode/owner/mtime/ctime inventories still must remain unchanged. Only fixture
waits were extended to cover the existing fifteen-minute production export ceiling; no export
protocol limit, capability or production timeout changed. Export above fixed 10 GiB/100,000
protocol bounds remains incomplete. Instructions: Node `docs/skill-node-export.md`.

The shell runner was replaced atomically with a new inode after syntax validation, so the live
pipeline shell continues reading its original script inode. Its already-built image/binary and
workload were not changed or restarted. Linux test cross-compilation, Python fixture syntax,
Server Ruff/mypy and docstring checks passed. Full Node quality **15135** passed and is reaped;
`/tmp/skill-ssh-capacity-node-quality.log`. Default opt-out **30529** passed and is reaped,
**4 skipped in 2.67 s**, `/tmp/skill-capacity-fixtures-default-optout.log`.

**16806** is the live two-case SSH capacity run, `/tmp/skill-ssh-export-capacity.log`. The first
case has an actual local-durable capture; export completion is still pending. Do not duplicate.
An additional single bounded stop diagnostic is running while both bulk transfers are active;
its trace can test whether the intermittent classification appears under concurrent capacity
load. A successful retry will not close that issue. Its runner and per-case logs are
`/tmp/skill-native-stop-under-capacity-runner.log` and
`/tmp/skill-native-stop-under-capacity-1.{log,trace}`.

The overall goal remains active and incomplete. No commits, releases, deployment or production
backend/capability advertisement occurred. Docker Sandbox has not been replaced by another backend.

## 2026-09-26 — bounded SSH export authorization at default entry capacity

The under-load Native stop diagnostic **3280** is terminal and reaped: **1 passed in 130.77 s**,
runner exit zero. Its retained trace shows normal clean shutdown under concurrent bulk transfer.
This is additional negative evidence, not a root cause or fix for intermittent unclean stops.

Actual default-entry SSH export exposed per-object network amplification: the original gateway
performed HTTP authorization before and after each distinct file. A 99,997-object stream therefore
required roughly 200,000 remote checks inside its fixed fifteen-minute lifetime. The first frozen
case of **16806** has now reported failure; the exact traceback remains pending until the second
case finishes. Do not count the initial run as a pass or infer its terminal reason from timing alone.

Node production authorization now uses only a connection-local validity window measured from
HTTP request **start**, lasting the Server-returned 1–10 seconds and capped by original grant expiry.
Per-object checks enforce current validity, cancellation and the immutable observed binding/digest/
classification. Renewal begins at half the current window; a separate expiry watcher cancels a
blocked HTTP request or output write. Failed/late responses cannot revive authority. Every successful
new permission preserves original identity/expiry and all learned facts. Both frozen and stopped-work
streams force fresh HTTP verification before their public header and successful footer. No window is
persisted or shared across connections. The internal stopped-stream callback identifies these forced
boundaries; JSON/socket framing and public object/byte/lifetime limits are unchanged.

Regression tests cover 200,000 local object checks without per-object network calls, independent
connections, blocked output plus stalled HTTP renewal, earlier caller cancellation and joined workers,
initial response delay, shortened intervals, late successful responses, grant expiry, identity/fact
changes, sticky failures and denied header/footer proof. The stopped relay also verifies exactly two
forced boundaries. Documentation in Node, Server and the root wire contract describes the revised
remote/local authorization behavior explicitly.

Verification completed and reaped:

- **95418**, `/tmp/skill-export-window-race-final.log`: Skill export/API/SSH gateway race tests pass.
- **11047**, `/tmp/skill-export-window-node-quality-final.log`: full Node quality passes,
  **62.3% coverage**, including installer/consistency/format/vet/whitespace checks.
- **91563**, `/tmp/skill-export-window-linux.log`: **12 top-level Linux root Helper tests pass,
  zero skips**, including stopped recovery, changed-source rejection, cancellation, descriptor
  lifetime and allowed/denied unprivileged gateway peers.
- **87795**, `/tmp/skill-export-window-linux-frozen.log`: actual unprivileged frozen Helper export
  passes (one top-level test, zero skips).
- **97225**: modified Server fixture Ruff/type/docstring checks pass; default opt-out is
  **2 skipped in 2.46 s**, `/tmp/skill-export-window-server-optout.log`. No production Server code
  changed, so the prior full Server gate remains the broad production baseline.

Server SSH fixture expectations now require initial/header/footer proof and revoke on the third
verification of a new export; small streams must still reject immediately before successful completion.
Capacity streams can hit the same revocation during periodic verification. Every failure must leave
no published or temporary bundle.

Live jobs at this checkpoint (poll exact handles; do not restart):

- **36891**, `/tmp/skill-default-pipeline-capacity-bounded.log`: original full daemon pipeline,
  still first upload. Latest independent filesystem count: **43,385 real files / 1,084,651 bytes**.
  First publication, restart, second materialization and second publication remain pending.
- **16806**, `/tmp/skill-ssh-export-capacity.log`: original frozen case failed; second runtime-quota
  case rebuilt Node after the authorization change and is actively exporting (20,274 staged objects
  observed). Its running Python fixture retains the earlier +5 revocation trigger. Container
  `agent-remote-ssh-export.nKoeZI`; previous frozen container is gone.
- **94575**, `/tmp/skill-ssh-export-capacity-window-frozen.log`: fresh frozen-only acceptance using
  current Node and the +3 revocation fixture. The original frozen case already ended, so this does
  not duplicate an active transfer.

The overall goal remains active and incomplete. Actual capacity export success is still pending.
Fixed 10 GiB/100,000-entry export bounds, actual 10 GiB SSH transfer, combined capacity, real model
learning, Docker Sandbox, interrupted/old-boot ownership repair and rollback attestation remain open.
No commits, release, deployment, production capability advertisement or backend substitution occurred.

Follow-up: **83298** passed and is reaped, `/tmp/skill-ssh-export-window-small-recovery.log`,
**1 passed, 1 deselected in 25.41 s**. This is actual small runtime-quota CLI/SSH recovery with
current authorization and revocation at the third (final) verification, including unpublished
bundle cleanup and unchanged source inventory.

The first revised frozen-only capacity run **94575** is terminal and reaped: **1 failed, 1 deselected
in 306.17 s**, `/tmp/skill-ssh-export-capacity-window-frozen.log`. It never reached SSH export.
`LiveDaemonProcess.wait_ready()` still had an unconditional 300-second smoke-case guard; this
expired while waiting for the original frozen capture. Its container/image were runner-cleaned.
Read-only observation just before timeout showed the complete generated work and clean termination,
but no completed frozen record. This is a fixture readiness failure, not an export result.

The shared wait now accepts an optional timeout with unchanged 300-second default. Only SSH capacity
passes 1200 seconds, matching its existing twenty-minute preparation phase. No production deadline,
wire field or limit changed. Server Ruff/type/docstring verification **27643** passed and is reaped.
The replacement sole frozen capacity job is **25818**, `/tmp/skill-ssh-export-capacity-window-ready.log`,
container `agent-remote-ssh-export.NGgJY7`. **16806** runtime-quota transfer and **36891** full pipeline
remain live; their successful completion is still required.

**16806** is now terminal and reaped: `/tmp/skill-ssh-export-capacity.log`, **2 failed in 1805.32 s**.
The original frozen case returned `STATE_EXPORT_UNAVAILABLE` with no successful bundle. The revised
runtime-quota case did complete the full 100,000-entry / 99,997-object export and independent byte/hash
verification in **672.191 s**. Its follow-up revoked-key assertion failed: the old running fixture
requested revocation at total verification 25, but the second attempt ended after total 23, so
`reports.revoked` stayed false. That second failure's CLI result was not included by the old assertion;
its cause is not proven. Do not count this run as complete acceptance or claim preserved-source checks
ran after the failure. Its owned container/image have been removed.

A fresh runtime-quota capacity run with the current third-check revocation fixture is **16161**,
`/tmp/skill-ssh-export-capacity-window-recovery.log`. **25818** remains the only frozen capacity run;
it now has an actual completed frozen record (no remaining capture staging), but initial inventory/
coordination has not yet emitted readiness. **36891** remains the original full daemon pipeline.
No duplicate copies of these active cases were started.

Final checkpoint for this increment: **36891**, **25818** and **16161** were all polled directly and
remain live. Both revised capacity cases now reached actual host CLI export; private staging is under
`pytest-1307/test_cli_exports_unuploaded_na0` (frozen) and
`pytest-1308/test_cli_exports_unuploaded_na0` (recovery). Each must finish, revoke on the third check,
leave no failed bundle and verify unchanged source inventory before acceptance can pass. The latest
pipeline log is still first finalization (2703.3 seconds), not publication. No test failure was erased
or converted into a pass; all terminal handles above are reaped. Node/Server/root whitespace checks
pass after the final documentation updates. The goal remains active with real capacity work running.

## 2026-09-26 — actual pending-state deletion exposed a CLI envelope mismatch

The previous goal turn was **progress**, with the bounded export authorization implementation and
completed regression gates. This turn directly repolled **36891**, **25818** and **16161** before
continuing. The full daemon pipeline **36891** remains live; its latest log was first finalization
at 3844.8 seconds, not a completed publication.

SSH capacity results are now terminal and reaped:

- **25818**, `/tmp/skill-ssh-export-capacity-window-ready.log`: complete frozen export and independent
  content verification succeeded in **895.402 s**, but the subsequent revoked-key assertion failed
  before the trigger (verification count 32 versus trigger 34). **1 failed, 1 deselected in 1212.04 s**.
  Source-inventory verification after that assertion did not run, so this is not full acceptance.
- **16161**, `/tmp/skill-ssh-export-capacity-window-recovery.log`: the initial recovery export failed
  with `STATE_EXPORT_UNAVAILABLE`, **1 failed, 1 deselected in 975.19 s**. Both large SSH transfers
  were concurrent; staging was being removed after the fifteen-minute CLI deadline. This does not
  negate the earlier complete 672.191-second standalone recovery, but concurrency is not a pass.
- **29240**, `/tmp/skill-ssh-export-capacity-window-diagnostic.log`: a subsequent frozen diagnostic
  failed its initial export in **191.09 s** overall. Its initial-error assertion did not yet expose
  verification timing, so its cause is unresolved. All three owned export containers are removed.

The SSH fixture now records only the latest sixteen (sequence, HTTP status, elapsed-seconds)
verification observations and includes these plus the bounded CLI result on both export assertions.
No grant, request body, token or private data is recorded. Its complete local bundle verification now
runs with `asyncio.to_thread`: hashing 100,000 files must not block the same event loop that serves
Node authorization/heartbeat HTTP. This fixture correction is not claimed as the cause or cure of
the observed failures. No new SSH capacity pass has yet been obtained.

Added an opt-in `upload-unavailable` variant to the actual CLI/Mutagen/SSH/unprivileged Worker/Helper
lifecycle test. It blocks only real finalization upload admission with HTTP 503 after the original
mounted writer starts. The intended sequence checks pending exit 3, original clean local-durable
status, concurrent single/bulk CLI deletion denial, and an actual Helper `cleanup_resources` denial
with byte/inode/mode/owner/mtime/ctime inventories of work and frozen objects unchanged. It then
restores upload service and must complete original publication, daemon restart, successor inheritance,
reclamation and permitted final deletion. This is a service-upload outage, not a literal whole-Node
TCP partition or real model inference proof.

The first two real runs **90895** and **10528** failed and are reaped:
`/tmp/skill-cli-retention-outage-live.log` (**136.38 s**) and
`/tmp/skill-cli-retention-outage-diagnostic.log` (**119.64 s**). Both reached the actual Helper cleanup
proof (`pending-retention-checked` exists), and the stop trace showed byte 3 plus clean pane/systemd
exit. The second exposed the exact problem: both real CLI deletes returned HTTP 409 but printed
`server returned an invalid error response` instead of `STATE_PENDING`.

Production Server correctly returned its version-1 Skill error envelope. The CLI's ordinary API
error parser accepted only the legacy `{error:{code,message}}` shape. `api::error_response` now accepts
validated failed Skill envelopes as well, preserving stable code/message and HTTP status, while
refusing malformed versions, committed/success payloads, unexpected data, invalid operation identity,
unsafe codes/control characters or oversized messages. Details and raw malformed bodies are never
rendered. Existing legacy error behavior and launcher exit codes remain unchanged. CLI English/Chinese
README and architecture rules document pending-retention deletion refusal.

Regression **21644** reproduced the old parser failure (2 passed, 1 failed),
`/tmp/skill-session-error-before.log`; **12381** then passed all three regression tests after the fix,
`/tmp/skill-session-error-after.log`. Both are reaped. Node full quality **33624** passed and is reaped,
`/tmp/skill-cli-retention-node-quality.log`; the new Linux lifecycle fixture cross-compiled successfully
(**40953**). Server fixture type/docstring/default-opt-out checks passed (**5331**, **77669**, **40032**
all reaped; opt-out **2 skipped in 2.50 s**).

Current jobs in addition to **36891**:

- **34709**, `/tmp/skill-session-error-cli-quality.log`: full CLI quality gate after production fix.
- **47219**, `/tmp/skill-cli-retention-outage-fixed.log`: actual outage lifecycle rerun with corrected CLI.

The design goal remains active and incomplete. No commit, release, deployment, capability advertisement,
subagent or replacement of Docker Sandbox occurred.

## 2026-09-26 — complete upload-outage lifecycle and first capacity publication

The preceding pending jobs have terminal evidence: **34709** passed the complete CLI quality gate
(`/tmp/skill-session-error-cli-quality.log`). **47219** failed before business execution because its
fclaude build exceeded the old 30-second fixture deadline while waiting for the quality gate's Cargo
lock. The fixture now uses the main CLI build's 180-second budget. After the gate completed,
**99651** passed the actual upload-outage lifecycle: **1 passed, 1 deselected in 133.46 s**,
`/tmp/skill-cli-retention-outage-verified.log`. Both handles were reaped. This proves pending stop,
concurrent individual/bulk deletion refusal with STATE_PENDING, privileged cleanup refusal and
unchanged source inventories, then restored upload, publication, daemon restart, inheritance,
reclamation and permitted deletion. The fault is HTTP 503 on real upload admission, not a literal
whole-Node TCP partition; the tool is synthetic, not model inference. It does not resolve the
intermittent clean-stop classification failure.

SSH diagnostic **53477** is terminal and reaped: **1 failed, 1 deselected in 141.54 s**,
`/tmp/skill-ssh-export-capacity-observed.log`. Initial export returned STATE_EXPORT_UNAVAILABLE after
exactly one observed successful authorization, HTTP 200 in 0.006 seconds. No second authorization
or header boundary was reached; the exact failing stage remains unresolved. Its owned container
has been removed. This is not capacity acceptance.

The original full capacity pipeline **36891** remains live. Its first finalization/publication
completed at **4698.5 s**; the successor materialization has started. This advances beyond the earlier
persisted-only observation, but full independent inheritance and second publication remain required.
No replacement pipeline was started. The overall goal remains active and incomplete.

## 2026-09-26 — frozen inspection preserves authority and cancellation

Review of the pre-header export path found a separate production defect: `Client.Call` omitted
`inspect_skill_finalization` from both exact JSON-number decoding and context-triggered connection
closure. A successful inspection could silently round original 64-bit generations; cancelled
authority could leave a queued Helper inspection waiting for the generic socket deadline. Inspection
now receives the same protections as finalization inventory. No timeout, content limit or protocol
shape changed. Architecture rules describe the boundary.

Two real Unix-socket regressions reproduce the original defects: **17561**,
`/tmp/skill-export-inspection-before.log`, **2 failed** (rounded identity with nil error and ignored
cancellation). Corrected **87391** passes both; race **8179** passes. Actual Linux **64753** passes both
new tests and all six existing exact-frozen-inspection cases with no skips,
`/tmp/skill-export-inspection-linux.log`. Full Node gate **11577** passes, 62.5% coverage,
`/tmp/skill-export-inspection-quality.log`. All these terminal handles are reaped.

This defect is not established as the cause of the capacity failure. One diagnostic SSH capacity
run **30574** remains live, `/tmp/skill-ssh-export-stage-diagnostic.log`, owned container
`agent-remote-ssh-export.rrhW5y`. It uses a temporary Go overlay in
`/tmp/skill-export-stage-overlay` to record only a fixed terminal stage and timestamp through the
existing disposable observation file. Production source has no diagnostic hook; grants/content are
not recorded. This binary predates the inspection fix above. It has passed initial preparation and
is transferring actual files, but no full acceptance result exists yet. The original full pipeline
**36891** is still materializing the independent successor after its first clean publication.

The new [design-wide requirement audit](skill-manager-requirement-audit.md) maps 49 grouped
requirements across §§1–12 to executable contracts and their actual evidence boundaries. All local
links were checked. It complements the nineteen interleavings; it is not a new test execution or a
completion declaration. Seven rows explicitly retain implementation/acceptance work (SSH/capacity,
clean-stop classification, oversized recovery, Docker Sandbox, backend recovery and real models).

Diagnostic **30574** is now terminal and reaped: **1 failed, 1 deselected in 513.14 s**. Its
retained content-free observation reports `export-stage=objects-loop`; the attempt therefore passed
header authorization and entered actual object transfer. This is different from the earlier one-check
pre-header failure. The owned container/image were removed. The Server fixture now prints bounded
numeric authorization observations explicitly, because pytest abbreviated the assertion's list.
A second temporary diagnostic overlay distinguishes object open/copy/check, authorization cancellation
and Helper reader error sites without rendering error messages or private content.

Detailed capacity diagnostic **36193** is terminal and reaped: **1 failed, 1 deselected in 162.68 s**,
`/tmp/skill-ssh-export-stage-v2.log`. Initial CLI export failed in **8.011 s**, with exactly one
Server verification (200, 0.005 s). Fixed-site observations identify authorization renewal rejection
(`authorization.go` line 155), followed by the held-file socket read failing after cancellation;
the gateway ended at `hold`, with zero objects sent. This narrows the pre-header failure to renewal,
not frozen manifest validation. It does not yet establish why the second verification was not seen
by Server. Its owned container/image were removed. Server numeric-observation fixture checks passed
(**96508**, reaped): Ruff, mypy, full docstrings and whitespace.

A temporary transport-only diagnostic now records connection reuse, request-write and response-start
events plus fixed error classes (never raw messages or grants). A seven-second test-only pause before
the real read hold lets the small genuine frozen fixture exercise periodic renewal without another
100,000-file build. Results from this artificial-delay diagnostic cannot count as product acceptance.

The small transport diagnostics both passed and are reaped: **61667**,
`/tmp/skill-ssh-export-renewal-transport.log`, **1 passed, 1 deselected in 35.60 s**, with a seven-second
read-hold pause; **84184**, `/tmp/skill-ssh-export-renewal-repeat.log`, **1 passed, 1 deselected in
99.32 s**, with a seventy-second pause. The latter completed sixteen successful initial verifications
and rejected the second export at the intended revoked-key response (409). HTTP traces show both
new and reused connections at the five-second renewal boundary, but no transport error in either
small case. Thus connection reuse is only a hypothesis, not an established defect; no production
transport behavior was changed. The temporary v5 overlay removes the artificial pause and carries
HTTP observations into the actual 100,000-entry fixture.

## 2026-09-26 — full frozen 100,000-entry SSH acceptance passed with observations

**7633** is terminal and reaped: **1 passed, 1 deselected in 670.42 s**,
`/tmp/skill-ssh-export-transport-capacity.log`. This is the complete actual frozen case, not only an
initial transfer: all **100,000 entries / 99,997 unique objects** exported, every local byte/hash and
manifest verified, the second export rejected at the intended third verification after real SSH-key
revocation (HTTP 409), no failed/staging bundle remained, and the Node's final full source inventory
matched the original. CLI initial completion was **467.170 s**; independent content verification
completed by **482.655 s**. The Node had sent all 99,997 objects and a valid footer before local CLI
fsync/hash work finished. Its owned container/image were removed.

The binary used the v5 temporary observation overlay: fixed stage/error-site labels and HTTP
connection/write/response event metadata only. It had **no artificial delay**, fake authorization,
fake data, changed limit or changed lifetime, and included the current inspection precision/cancel
fix. This pass does not causally explain earlier renewal failures; no production HTTP transport fix
or keep-alive hypothesis is asserted. Reproducing/diagnosing intermittent renewal remains open.

The frequent-local-check small timing diagnostic **66600** also passed and is reaped: **1 passed,
1 deselected in 107.81 s**, `/tmp/skill-ssh-export-renewal-local-checks.log`. Its artificial 70-second
check loop cannot count as capacity acceptance. All three small timing probes observed normal
renewal and the intended HTTP 409 on revoked authority, not the unexplained transport failure.

A single current-production stopped-work runtime-quota capacity acceptance has now started,
`/tmp/skill-ssh-export-recovery-capacity-current.log`. It uses no Go overlay or artificial pause.
The original full daemon pipeline **36891** remains live in successor materialization.

Final checkpoint for this increment: production recovery capacity is **48561**, owned container
`agent-remote-ssh-export.RLfRel`; original pipeline **36891** uses
`agent-remote-ssh-export.cY9ZkL` plus `agent-remote-pipeline-test.ahmrsM`. Both were directly polled
and remain live. Pipeline successor materialization last reported **2361.7 s**; do not restart it.
Root, Node and Server whitespace checks pass. The goal remains active and incomplete; no commit,
release, deployment, capability advertisement, subagent or Docker Sandbox substitution occurred.

## 2026-09-26 — preparing actual byte-plus-entry SSH acceptance

The previous goal turn was progress: inspection precision/cancellation fixed and gated, full frozen
100,000-entry SSH acceptance passed with diagnostic observations, and the design-wide audit added.
Both original live handles were directly polled before continuing; neither was restarted.
Pipeline **36891** now completed successor materialization at **2392.5 s**, attached the independent
verifier, and entered its second finalization. This is not yet a complete two-publication pass.

The actual SSH fixture now supports a separate byte-capacity opt-in and its combination with the
existing entry-capacity opt-in. The real mounted synthetic tool writes ten distinct payloads,
exactly 10 GiB overall and no more than 1 GiB per skill; auxiliary bytes reduce the learning payload.
Byte-only expects 36 entries / 24 unique files; combined expects 100,000 entries / 99,988 unique
files. Node and Server independently check size/cardinality/uniqueness. Source inventories and
bundle verification now hash with bounded buffers. No production limit or timeout changed.
The active runner shell was replaced through a new inode so its original executing instance is
preserved. The byte writer is a separate fixture script; the original pipeline generator is intact.

Fixture checks: **55763** Linux cross-compilation/shell/whitespace passed; **99613** Ruff/mypy/full
Server docstrings passed (default opt-out: 2 skipped in 1.64 s); **7542** full Node gate passed. All
three handles are reaped. The new Python fixture was additionally Ruff-formatted and linted.
Actual byte-capacity execution is still required. The current Docker VM has about 16 GiB free,
which accommodates the stopped-work quota case but not both 10 GiB work and frozen objects. No
unrelated image, volume or build cache was removed. The existing production recovery **48561** is
still live, with more than 88,000 local objects written; it must finish before another large SSH run.

Production recovery **48561** is now terminal and reaped: **1 failed, 1 deselected in 581.28 s**,
`/tmp/skill-ssh-export-recovery-capacity-current.log`. Initial complete 100,000-entry export succeeded
in **533.656 s**, with independent manifest/byte/hash verification by **549.820 s**. The second attempt
failed after **5.509 s**, with only one additional HTTP 200 (0.005 s); count 28 did not reach the
revocation trigger at 30. Therefore the final source-inventory check did not run, and this is not a
full recovery acceptance pass. Its owned container/image are removed.

To reduce diagnostic timing changes, a new temporary v7 overlay records only a fixed error class
*after* a failed Node verification HTTP call (or invalid permission). Successful calls have no
httptrace callbacks, logging, sleeps or polling additions. Its existing HTTP contract regression
**92549** passed and is reaped. Actual **10 GiB + 100,000 entries** stopped-work acceptance **61529**
is running with this observation-only overlay, `/tmp/skill-ssh-export-combined-capacity.log`. It uses
the current real byte fixture and the ordinary production authority/streaming path; actual success
is still unproven. It is the only large SSH test running.

Read-only PostgreSQL observation of original pipeline **36891** now shows two stopped sessions, one
clean published finalization and one clean upload_pending finalization. Reaching its second
finalization means the independent tool completed its full inherited-byte check. The second
publication remains required; latest progress was 660.7 seconds into that phase.

## 2026-09-26 — observed export HTTP EOF and scoped connection fix

Combined byte/entry stopped-work test **61529** is terminal and reaped: **1 failed, 1 deselected
in 763.33 s**, `/tmp/skill-ssh-export-combined-capacity.log`. The initial CLI export failed after
**690.143 s**, with **135** completed Server verification requests; the last sixteen all returned
HTTP 200 in 0.004–0.008 seconds. The error-only v7 observation captured
`2026-09-25T20:27:14.61864188Z export-http-failure=eof`. The next verification did not appear at
Server. Thus an actual transport EOF is now established; this alone does not prove the exact
server idle-expiry timing. No complete bundle, second revoked export or final unchanged-source
inventory was accepted. The disposable container/image were removed by the runner.

A deterministic real TCP regression closes a reused connection after consuming its verification
POST. Before the fix, both HTTP and private-trust TLS variants failed with EOF (**96805**, reaped;
`/tmp/skill-export-connection-before.log`). Export verification now sets the per-request HTTP/1
close policy so an authorization response does not leave its connection idle for the next periodic
renewal. Common authenticated request construction and bounded response parsing remain shared;
other API calls keep normal connection pooling. There is no automatic retry, increased five-second
HTTP timeout, extended grant, changed authorization window or production diagnostic output.
Separate actual-socket tests require uncertain first-request EOF to remain terminal with one request
and verify ordinary API calls still reuse their connection. This addresses the reproduced reused-
connection failure mode; capacity confirmation remains necessary.

Verification: API and export tests **98048** passed; race checks **55219** passed; full Node quality
gate **62547** passed at **62.5%** statement coverage, including installer/consistency checks. All
three are reaped. Logs are `/tmp/skill-export-connection-{after,race,quality}.log`.

The actual combined **10 GiB / 100,000-entry / 99,988-object** stopped-work acceptance was restarted
only after the failed predecessor and its resources had terminated: **9315**,
`/tmp/skill-ssh-export-combined-capacity-fresh-http.log`. It uses current production code with no Go
overlay, wrapper observations or artificial delay. Its owned container is
`agent-remote-ssh-export.msigZU`. This is not yet a pass. Original complete Native pipeline **36891**
is still running its second clean upload; it was not restarted. The goal remains active/incomplete.

Actual Linux ARM64 socket/export verification is also complete: **90055** passed with no skipped
tests, `/tmp/skill-export-connection-linux-complete.log`; the handle is reaped. The preceding disposable
runner **89928** lacked the existing `testdata/frozen-export-v1.bin` fixture, causing three file-not-
found failures after all new HTTP/private-TLS tests passed. Copying that unchanged fixture and setting
the correct working directory fixed the runner; no production or test assertion was changed. Both
disposable component containers were automatically removed. Cross-compilation handles **95118** and
**27591** are reaped. No further source changes followed the full quality gate.

The running **9315** uses the existing unoptimized `target/debug/agent-remote`. A three-second
host stack sample (**8078**, reaped; `/tmp/skill-export-combined-cli-sample.txt`) shows software
SHA-256 compression dominating its active object-verification worker; the CLI was using about one
CPU. This is a development-build performance observation, not a failed hash or completed transfer.
Future entry/byte capacity runs now explicitly build the current CLI with Cargo's ordinary release
profile and print `ssh_export_cli_profile=release`. Only compilation gets a longer setup budget;
all transfer/authorization lifetimes, sizes, hash checks and fsync behavior stay unchanged. Ordinary
small live cases keep their debug build. This is local optimized compilation, not publishing a release.

Fixture validation passed: Ruff format/lint, mypy **95826**, full docstrings **1677**, whitespace,
and default opt-out **25256** (2 skipped in 5.19 s). Handles are reaped; skipped cases are not live
acceptance. Optimized local compilation **11512** is running, `/tmp/skill-export-optimized-cli-build.log`.
The existing debug run is not stopped or retroactively relabeled as optimized acceptance.

A separate bounded diagnostic **81341** runs at most three small real CLI lifecycle cases, stopping
on the first failure: `/tmp/skill-native-stop-errors-N.log`. Its temporary Go overlay records only
after a failed tmux operation/parse/cleanup or unclean classification, with fixed labels/booleans and
numeric exit codes, never credentials, arguments or tool output. It adds no success logging, delay,
wrapper or behavior change. A failure's bounded observation is retained in the fixture's
`node/control/native-stop-failure`; it cannot establish a production fix. The overlay's existing
focused native-stop tests **69381** passed and are reaped. Original pipeline and combined SSH jobs
continue independently.

Local optimized CLI build **11512** completed successfully in **2m 33s** and is reaped.
The existing release-profile Node-export CLI contract is running as **37330**,
`/tmp/skill-export-optimized-cli-contract.log`; no release packaging or publication was invoked.
Failure-only stop diagnostic case 1 passed in **132.63 s**; **81341** continues its bounded loop.

Optimized CLI Node-export contracts **37330** passed: **5 passed, 0 ignored**, 8.94 seconds
for the tests, `/tmp/skill-export-optimized-cli-contract.log`; the handle is reaped. Stop diagnostic
case 2 also passed in **130.60 s**; case 3 remains running. These small successful cases do not
explain the earlier intermittent unclean classification.

The unoptimized current-production combined test **9315** is now terminal and reaped: **1 failed,
1 deselected in 981.65 s**, `/tmp/skill-ssh-export-combined-capacity-fresh-http.log`. Initial CLI
failure was **913.298 s**, with **183** completed verification requests and its final sixteen all
HTTP 200 in 0.004–0.009 seconds. This reaches the existing fifteen-minute transfer/grant envelope
plus local teardown. It is not a capacity pass; this run had no error-class overlay, so its output
does not independently pinpoint the terminal failure site. Host sampling established substantial
debug-build software SHA-256 work. No timeout or authorization limit was increased. The owned
container/image were removed. The optimized-build actual combined rerun is now running, with no Go
overlay or observation wrappers, `/tmp/skill-ssh-export-combined-capacity-optimized.log`.

Failure-only stop diagnostic **81341** completed and is reaped: all three small actual CLI lifecycle
cases passed in **132.63 / 130.60 / 124.89 seconds**, with owned resources cleaned. No production stop
behavior was changed. These passes do not establish the cause of earlier unclean classifications.

Current live checkpoint: optimized combined SSH is **74214**, owned container
`agent-remote-ssh-export.WwxbOY`; its log confirms `ssh_export_cli_profile=release`. Original Native
pipeline is still **36891**, with `agent-remote-ssh-export.cY9ZkL` and
`agent-remote-pipeline-test.ahmrsM`; latest second-finalization observation was 2644.7 seconds.
Both handles were directly polled and remain live. Do not restart either. Root, Node and Server
whitespace checks pass. The full goal remains active and incomplete; no commit, release publication,
deployment, production capability advertisement, subagent or Docker Sandbox substitution occurred.

## 2026-09-26 — remove fixed export byte admission, retain protocol safeguards

The prior turn was progress: a real verification EOF was captured, scoped HTTP/1 connection handling
was fixed and gated, and optimized-capacity setup was added. Original handles **74214** and **36891**
were directly polled and remain live; neither was restarted. Combined export currently uses its
already-built pre-byte-limit-change binaries, so its outcome will retain that precise evidence scope.

Node's scanner/stream formerly rejected complete recovery above 10 GiB, as did shared CLI bundle
staging, even when runtime capture quota was exceeded or an administrator allowed larger state.
Export now uses the complete authorized manifest's signed 64-bit byte count. Node propagates that
encoding bound into the read-only stopped scanner; object enumeration keeps checked addition.
CLI relies on canonical manifest size/overflow validation instead of the second fixed byte cap.
The 100000-entry bound, 64 MiB frames, bounded streaming buffers, private staging, exact hashes,
source recheck, live authorization and original transfer deadlines are unchanged. Runtime admission
and storage default quotas stay finite and unchanged. This does not implement over-entry recovery
or unlimited-duration exports; R41 remains open.

New Node header regression **60793** failed before the change with STATE_EXPORT_UNAVAILABLE; CLI
staging regression **22988** failed before the change with the explicit 10 GiB limit. Both handles
are reaped, logs `/tmp/skill-export-byte-limit-{node,cli}-before.log`. These are metadata admission
proofs, not claims of transferring 10 GiB. Overflow rejection and no-content/private-staging cleanup
are tested separately. Full Node gate **34695** passed at **62.6%** coverage and is reaped;
`/tmp/skill-export-byte-limit-node-quality.log`. CLI full gate **18577** is still running,
`/tmp/skill-export-byte-limit-cli-quality.log`.

The actual SSH fixture now has explicit `AGENT_REMOTE_RUN_SKILL_SSH_EXPORT_OVERSIZE=1`, valid only
with byte capacity and stopped-work quota mode. It writes a real additional 1 MiB into the learning
payload, for 10 GiB + 1 MiB, keeping the same entry/object counts. Both Node and Server independently
require that larger complete total; there are no sparse/reflink/dedup shortcuts. Actual complete
export, revoked second attempt and unchanged full source inventory are still required. Its Linux
cross-compilation **78026** and Server Ruff/mypy/docstring/default-opt-out checks **24287** passed;
handles are reaped. Default skips do not certify the pending actual run. The live shell runner was
replaced through a new inode to preserve the original pipeline's executing script.

Wire documentation, Node/CLI architecture rules and English/Chinese CLI usage now describe export
by complete manifest size and explicitly retain the entry/deadline limits. Oversized acceptance must
wait for **74214** to end before starting another large SSH workload.

## 2026-09-26 — complete current-production combined SSH acceptance passed

**74214** completed and is reaped: **1 passed, 1 deselected in 676.69 s**,
`/tmp/skill-ssh-export-combined-capacity-optimized.log`. This is actual **10 GiB / 100000 entries /
99988 distinct objects** stopped-work recovery over the real HTTP Server, nonroot SSH gateway and
privileged Native Helper. Actual runtime capture quota rejection preserved the original work.
Initial CLI export completed in **558.489 s**; independent complete byte/hash/manifest verification
finished by **585.763 s**. The second export failed in **10.681 s** at the intended third verification
with a genuinely revoked SSH key (verification 100, HTTP 409). No failed/staging bundle remained,
and the full final Node inventory matched the original bytes and filesystem metadata. Runner cleanup
removed its owned container/image.

This run used current connection-close production code, no Go overlay, no diagnostic wrappers and no
artificial delay, with the CLI's ordinary optimized profile. Its binaries preceded the byte-ceiling
removal, which was developed while this immutable run continued. It establishes combined default-
capacity stopped-work acceptance and a complete large-scale connection-fix rerun, not arbitrary
oversize recovery, Docker Sandbox or model inference.

Actual above-byte-ceiling acceptance is now running as **21325**,
`/tmp/skill-ssh-export-oversize-byte-acceptance.log`, using current Node/CLI byte-limit changes,
10 GiB + 1 MiB / 36 entries / 24 distinct files. It is sequential after **74214**, with the same full
revocation and unchanged-source assertions. Local optimized rebuild **85898** is being reaped;
full CLI quality gate **18577** remains live. Original whole pipeline **36891** is unchanged and live.

Full CLI quality gate **18577** completed successfully and is reaped, including static checks,
all Cargo tests and the new metadata/overflow regressions. Optimized current CLI rebuild **85898**
also passed in **1m 17s** and is reaped. Above-default byte acceptance is **21325**, owned container
`agent-remote-ssh-export.aJVFYo`, and is currently running the optimized CLI through actual SSH.
No acceptance claim is made before its final source-inventory assertions finish. Read-only SQL for
original **36891** still shows two stopped sessions, one clean published finalization and one clean
upload_pending finalization, with one publication. It remains active without restart.

## 2026-09-26 — above-default byte recovery acceptance passed

**21325** completed and is reaped: **1 passed, 1 deselected in 233.89 s**,
`/tmp/skill-ssh-export-oversize-byte-acceptance.log`. Current production Node and optimized CLI
exported exactly **10 GiB + 1 MiB / 36 entries / 24 distinct files** after actual capture rejection.
Initial export completed in **115.008 s**; complete independent byte/hash/manifest checks by
**121.522 s**. The second export was rejected at the intended third check (verification 27,
HTTP 409) in **10.452 s**, with no failed/staging bundle. Final full source inventory was unchanged.
Owned container/image were removed. No observation overlay, wrappers, sparse files, shared-file or
byte-dedup shortcuts were used. This closes the fixed-byte-ceiling recovery defect with real transfer
evidence; over-entry and grant-duration recovery remain open. Full Node and CLI gates both passed.

The Docker VM currently has 17,192,919,040 bytes free, insufficient for 10 GiB work plus a second
10 GiB frozen copy and the configured reserve. Build-cache inspection identified 249 non-shared,
reclaimable records from disposable agent-remote/proof fixture builds, about 8.55 GB. A scoped cleanup
uses a validated exact-ID regex selected from that read-only inventory; it does not prune arbitrary
cache, images, volumes or containers. Selection is retained at
`/tmp/skill-capacity-owned-cache-selection.json`, output `/tmp/skill-capacity-cache-prune.log`.
Space must be rechecked before starting actual frozen byte-capacity acceptance.

Scoped task-cache cleanup **79061** reclaimed **6.756 GB** and is reaped. Six selected parent
records remained because nine disposable proof-worker/locale child cache records still referenced
them. Their exact parent graph and descriptions were inspected; all fifteen were non-shared and
reclaimable. Exact-ID follow-up **75969** reclaimed **1.81 GB** and is reaped. Logs and reviewed
selections are `/tmp/skill-capacity-cache-{prune,final-prune}.log` and
`/tmp/skill-capacity-cache-{descendants,final-selection}.json`. No image, volume, container or
unrelated build cache was removed. Actual VM free bytes increased to **25,650,536,448**.

An actual **10 GiB frozen capture plus SSH export** run is starting,
`/tmp/skill-ssh-export-frozen-byte-acceptance.log`, preserving work and frozen copies and the default
reserve. It has 36 entries / 24 distinct files and includes independent full verification, revoked
second export and unchanged-source proof. Combined frozen byte+entry acceptance remains separate;
its extra small-file storage must wait for the original pipeline's owned storage to be released.
No capacity requirement has been reduced or marked complete by the byte-only run.

## 2026-09-26 — original complete Native entry-capacity pipeline passed

Original **36891** completed and is reaped: **1 passed in 11233.68 s (3:07:13)**,
`/tmp/skill-default-pipeline-capacity-bounded.log`. First clean capture/upload/publication completed
in **4698.5 s**, successor materialization after Worker/Helper restart in **2392.5 s**, and the second
clean finalization/publication in **4079.3 s**. The actual independent successor verified every
inherited file. The fixture required both clean published Server records, distinct snapshots and
exact **100000 entries / 99999 distinct objects**. No claim/exit/preparation/publication receipt was
seeded; the real nonroot Worker, privileged Helper, Native runtime, HTTP Server and PostgreSQL owned
the transitions. Default quotas/copy policies were unchanged. This is entry capacity, not 10 GiB
pipeline capacity or actual model inference.

The original job was never restarted because of observation waits. Its own Native and PostgreSQL
containers/images/temp roots have now been cleaned by the runner. Neither remains in `docker ps`.
R40 and Server pipeline documentation now record the complete passing result and remaining scope.
Frozen 10 GiB SSH acceptance remains live as **86312**,
`/tmp/skill-ssh-export-frozen-byte-acceptance.log`; its image is being rebuilt after task-cache cleanup.
No frozen-byte or combined frozen acceptance is yet claimed.

## 2026-09-26 — actual default-byte frozen capture and SSH export passed

Original **86312** completed and is reaped: **1 passed, 1 deselected in 246.35 s**,
`/tmp/skill-ssh-export-frozen-byte-acceptance.log`. The actual Native runtime produced and retained
both 10 GiB work and independent frozen objects, with **36 entries / 24 distinct files** and the
default reserve. Initial optimized CLI export completed in **75.390 s**; independent complete
manifest/byte/hash verification finished by **80.970 s**. The second export failed in **5.495 s**
at the intended third verification (verification 20, HTTP 409). No failed/staging output remained
and the complete final source inventory was unchanged. Runner-owned container/image were removed.
Current production binaries were used without observation overlays or wrappers. This establishes
default-byte frozen capture/export, not the Server upload/publication/inheritance pipeline.

After cleanup, a disposable read-only filesystem check reported **26,575,392,768 bytes** free in
the Docker VM. Combined **10 GiB / 100000-entry / 99988-object** frozen acceptance is now running
as **9223**, `/tmp/skill-ssh-export-frozen-combined-acceptance.log`, sequentially after 86312.
The complete byte-capacity daemon pipeline is being extended separately; no pending result is a pass.

The Native pipeline fixture now has explicit `AGENT_REMOTE_RUN_SKILL_PIPELINE_BYTES=1` and optional
`AGENT_REMOTE_RUN_SKILL_PIPELINE_COMBINED=1` workloads. Byte-only creates 10 GiB / 30 entries /
20 distinct files; combined creates 10 GiB / 100000 entries / 99990 distinct files. Ten valid skills
respect individual 1 GiB limits and ordinary sequential writes allocate all bytes. A separate
successor checks every expected instruction/payload/auxiliary byte. Node and Server independently
require exact counts and both clean published records with distinct snapshots. Byte runs wait for
normal fresh-authorized reclamation after each publication (and prove the first work/object roots
absent before successor admission), without manually deleting retained data or reducing reserves.

The executing SSH runner was replaced atomically through a new inode; 9223 continues its original
binaries unchanged. Fixture checks passed: Linux ARM64 lifecycle compilation **24064**, Linux vet,
Server Ruff/mypy/full Chinese docstrings/default opt-out **29278** (1 skipped in 2.17 s), shell
syntax, new Python fixture formatting/syntax and cross-repository whitespace. Skips and compilation
are not byte-pipeline acceptance. The first actual byte pipeline waits for the sole large SSH run.

## 2026-09-26 — combined default-byte/entry frozen acceptance passed

**9223** completed and is reaped: **1 passed, 1 deselected in 775.93 s**,
`/tmp/skill-ssh-export-frozen-combined-acceptance.log`. Actual Native frozen capture plus optimized
CLI/HTTP/SSH export preserved both 10 GiB work and independent frozen objects under default reserve,
with exactly **100000 entries / 99988 distinct files**. Initial export took **511.385 s**; independent
complete manifest/hash/byte verification finished by **532.305 s**. The second export failed in
**13.916 s** at its intended third verification (89, HTTP 409). No failed/staging bundle remained;
the complete final source content/metadata inventory was unchanged. The owned container/image were
removed. Current production binaries used no Go overlay, wrapper or artificial delay.

This closes the combined frozen capture/export acceptance gap in R40. Full byte/combined daemon
upload, publication, restart, inheritance and reclamation still require their own passing runs.
The default-byte pipeline fixture's final Linux compile **58040**, Linux vet and Server docstring
check **19685** also passed; handles are reaped. No production source changed in this step.

After runner cleanup the Docker VM had **26,574,323,712 bytes** free. Actual byte-only complete
daemon pipeline is now running as **34085**, `/tmp/skill-default-byte-pipeline-acceptance.log`,
with `AGENT_REMOTE_RUN_SKILL_PIPELINE_CAPACITY=1 AGENT_REMOTE_RUN_SKILL_PIPELINE_BYTES=1`.
It is sequential after the complete combined SSH run; no other large workload is active.
This is the new 10 GiB / 30-entry / 20-distinct-file pipeline, not the mixed SSH fixture.

## 2026-09-26 — complete default-byte Native daemon pipeline passed

**34085** completed and is reaped: **1 passed in 380.80 s (6m 20s)**,
`/tmp/skill-default-byte-pipeline-acceptance.log`. This is actual **10 GiB / 30 entries / 20 distinct
files**, ten valid skills within individual default checkpoint quotas. Real nonroot Worker,
privileged Helper, Native runtime, HTTP Server and disposable PostgreSQL owned every transition.
First clean capture/upload/publication took **124.5 s**; normal fresh-authorized reclamation took
**50.3 s** and removed both original work and frozen objects before successor admission.
After Worker/Helper restart, independent successor materialization took **58.9 s**. That session
verified every expected instruction and payload byte, then cleanly published in **68.4 s** and
reclaimed in **53.1 s**. Server independently checked both clean published receipts, distinct
snapshots, equal complete tree identity and exact byte/entry/distinct-object totals. No transition
receipt was seeded; default quotas/reserves and ordinary copy policy were unchanged.

The runner removed its Native and PostgreSQL containers, image and temporary roots. A read-only
SQL observation attempted just after completion found the already-removed database container;
this does not affect the test's completed assertions. No production source changed or observation
overlay was used. This closes byte-only full-daemon capacity acceptance, not combined byte/entry
capacity, real Claude inference or Docker Sandbox. Those remain explicitly separate.

After byte-only cleanup the Docker VM had **26,438,270,976 bytes** free. Actual combined daemon
pipeline is now running as **11363**, `/tmp/skill-default-combined-pipeline-acceptance.log`, with
all three explicit pipeline flags set (`CAPACITY`, `BYTES`, `COMBINED`). It must independently prove
**10 GiB / 100000 entries / 99990 distinct files**, two clean publications, daemon restart, complete
successor byte verification and both authorized reclamations. It is the only large active workload.
Poll this original handle; observation waits are not a reason to restart it. All four repository
whitespace checks passed after the acceptance/documentation changes. The goal remains active and
incomplete; no commit, release, deployment, production capability advertisement, subagent or Docker
Sandbox substitution occurred.

## 2026-09-26 — explicit live-grant continuation service

The preceding goal turn made concrete progress: actual frozen-byte, combined frozen and complete
byte-only daemon acceptance passed, and the combined daemon fixture was implemented and started.
Original **11363** was directly polled this turn and remains live; no observation timeout caused a
restart. Its Node/PostgreSQL containers are `agent-remote-ssh-export.302RJD` and
`agent-remote-pipeline-test.RnvqGK`. It is still working on first clean finalization/publication.

Server now implements additive Node-authenticated `POST /node/skill-state-exports/{snapshot}/renew`
as a prerequisite for recovery beyond the original fifteen-minute grant. It shares all original
user/token/device/key/snapshot and conflicting-observation checks with `/verify`. The response binds
the exact predecessor credential digest to a successor and current permission. Grant ID, original
user token and all original snapshot identities are preserved. Each successor lasts at most fifteen
minutes and never exceeds the original user's current token expiry. The predecessor must still be
valid after database observation at issuance; expiry during observation is rejected. No authorization,
content, quota or task rows are written. Existing `/verify` retains its response and fixed expiry.
Credentials remain memory-only and all malformed-request diagnostics stay sanitized.

Before implementation **18888** failed at the missing route (HTTP 404),
`/tmp/skill-export-renewal-before.log`; it is reaped. Focused **74630** passed 55 cases; an initial
test-clock type override failed mypy and was corrected without changing production behavior. Final
**62291** passed Ruff/mypy/full Chinese docstrings and **57 tests in 32.51 s**, including explicit
expiry during database observation, shared revocation/foreign identity/input sanitization and live
Node-authentication rejection on both endpoints. Logs are `/tmp/skill-export-renewal-focused-final.log`
and `/tmp/skill-export-renewal-focused.log`; handles are reaped. Service contract, identity rules and
wire documentation are updated.

Full Server quality gate **80392** is running, `/tmp/skill-export-renewal-server-quality.log`.
Node/Helper/CLI still enforce their original complete-transfer limits and do not consume this new
endpoint yet. This prerequisite is not a completed long-export workflow; R41 remains open alongside
over-entry recovery. Production capability advertisement remains disabled and no release/deployment
or Docker Sandbox substitution occurred.

Node now also has the typed `RenewNodeExport` HTTP transport and strict ephemeral
`NodeExportRenewal` decoder. It checks the exact predecessor digest, grant size/shape, original
Node/snapshot/forced-command device/key and complete permission envelope. Verification and renewal
share request validation and strict envelope decoding; both keep independent HTTP/1 connections,
a five-second request budget and no uncertain replay. Malformed/error responses return no successor
credential. The gateway does not call this transport yet, so existing export lifetime behavior is
unchanged and no complete long-transfer acceptance is claimed.

Focused Node packages **52718** passed, `/tmp/skill-export-renewal-node-focused.log`. Full Node gate
**39330** passed at **62.6%** coverage with installer/consistency checks,
`/tmp/skill-export-renewal-node-quality.log`. First race run **19546** found an unsynchronized
request counter in the new EOF test (not production state). It was replaced by `atomic.Int64`;
current API/export race run **35930** passed, `/tmp/skill-export-renewal-node-race-fixed.log`.
All four handles are reaped. The full Node gate preceded only that test-counter correction; current
focused race execution includes it. Tests cover changed predecessors, malformed/extra/aliased/null/
duplicate fields, foreign identity, committed/operation envelopes, redirects, denial, oversized
responses and uncertain EOF without replay or credential disclosure.

Latest live checks directly polled **80392** (full Server gate, approximately 34% through pytest)
and original combined pipeline **11363** (first finalization, 1082.1 seconds observed). Both are
still running and were not restarted. Read-only PostgreSQL observation confirmed one clean
`upload_pending` finalization. No current long-transfer or combined-pipeline pass is claimed.


## 2026-09-26 — integrated renewable export lifetime and progress bounds

The gateway now consumes `/renew` after initial `/verify`, preserving exact predecessor linkage,
original user/device/key/snapshot identity and all learned facts. A successor is accepted only
while the previous connection-local short window remains live; a late response cannot revive it.
Legacy in-process authorities retain fixed-expiry verification. The real updated gateway requires
the matching Server endpoint, with Server-before-Node ordering documented for any later rollout.
No uncertain HTTP operation is replayed and credentials remain memory-only.

Node, Helper and CLI no longer impose a separate fifteen-minute whole-transfer ceiling. Initial
metadata/scanning, Helper lifecycle-lock acquisition and stopped-work final verification remain
bounded to fifteen minutes each. Gateway/Helper output is written in at most 32 KiB blocks, each
bounded to thirty seconds; owner cancellation closes the transport. Helper request submission has
its own thirty-second write deadline. CLI resets a thirty-second progress timer after partial reads,
with separate fifteen-minute initial/final scan waits. Earlier caller cancellation and original user
token expiry still apply. Frozen readers rotate between objects after ten minutes, acquiring the
replacement before closing the old reader while retaining the outer immutable manifest hold.
Complete content validation, final source recheck, private staging and footer/EOF/SSH-success checks
are unchanged. Runtime byte/entry admission and capability advertisement remain unchanged.

Focused continuation tests **52560** passed, `/tmp/skill-export-continuation-node-clock-fixed.log`.
They cross original grant expiry, reject changed credentials/bindings/facts and late renewal, stream
more than fifteen virtual minutes, verify every byte/footer and prove reader rotation plus immutable
hold ownership. The initial virtual-clock delayed-response case deadlocked because a mutex wait is
not synctest-durable; the same compiled test was diagnosed under a bounded five-second invocation
before that unit process was terminated and reaped. The late-response case now uses a real 300 ms
reply delay against an already-partly-consumed window; no production behavior was weakened.
CLI virtual-clock phase/progress tests passed (42708), including independent scan expiry cleanup.

Full Server **80392** passed **1814 tests / 97 skips / 83.04% coverage**, plus Ruff/mypy/docstrings:
`/tmp/skill-export-renewal-server-quality.log`. It includes all renewal production code; later changes
are test-only. Full Node **18548** and focused race **15329** passed. After adding the separate Helper
request write bound and Linux blocked-output regression, final full Node **41953** also passed at
**62.7%** coverage, with installer/consistency checks. Logs:
`/tmp/skill-export-continuation-node-{quality,race,quality-final}.log`.
Full CLI **59888** passed all static/Cargo/installer gates and five Node-export contracts:
`/tmp/skill-export-continuation-cli-quality.log`. All these handles are terminal and reaped.

Actual small CLI/HTTP/SSH frozen and over-quota stopped-work regression **47539** passed:
**2 passed in 50.26 s**, `/tmp/skill-export-continuation-small-ssh.log`. Both complete exports passed
independent object verification, then failed their second export at the intended third authority
check with HTTP 409. No failed bundle or staging survived, and final source inventory was unchanged.
The middleware now counts both `/verify` and `/renew`, preserving the intended revocation trigger.

Extra Linux Helper executions **67710** and **87032** failed during fixture preparation: the shared
Docker filesystem had fallen below its existing five-percent reserve while the combined daemon
pipeline retained its two 10 GiB copies. These did not reach the new assertions. A first isolated
runner **55528** failed in package setup (dpkg error), also before assertions. All three are reaped.
The final disposable runner reused this task's already-built Native image and mounted a private
sparse 4 GiB ext4 test filesystem, keeping the production 2 GiB/five-percent reserve unchanged.
**64896** passed all 13 selected Linux Helper test functions with no skips:
`/tmp/skill-export-continuation-helper-isolated-ready-linux.log`. This includes descriptor lifetime,
nonroot authorization, source-change rejection, cancellation, and real thirty-second output stall.
Every stalled/cancelled/trailing-input case releases the lifecycle lock and permits a fresh complete
read. The runner owns cleanup; this is component evidence, not capacity or Docker Sandbox evidence.

The long-transfer fixture is now explicit: `AGENT_REMOTE_RUN_SKILL_SSH_EXPORT_LONG=1` generates a
32 MiB file and routes only test SSH through a bounded localhost encrypted-stream proxy. The first
download is paced at at most 16 KiB/s for 930 seconds after handshake; subsequent revocation is
unpaced. A pass requires a successful renewal more than 900 seconds after initial verification,
complete independent byte/hash checks, revoked second export rejection and unchanged source inventory.
This uses actual current binaries and real Server authority, without changing clocks, grants or
production delays. Fixture Ruff/mypy/full docstrings **12710** passed; Linux compilation/vet and
shell syntax passed. The original small SSH run retained its already-loaded fixture/binaries.

Actual long stopped-work **30245** and frozen **60917** are running:
`/tmp/skill-export-continuation-long-recovery-ssh.log` and
`/tmp/skill-export-continuation-long-frozen-ssh.log`. Both have prepared their exact 9-entry,
6-object, 33,562,777-byte source trees; no long-transfer pass is claimed yet. Their own containers
are `agent-remote-ssh-export.6TIaWX` and `agent-remote-ssh-export.EO7Yv3` (readiness verified on both;
individual case/container mapping was not used as authority). The later Helper request-write bound
was added after these launches; the lifetime/renewal implementation is the version under test.

Original combined daemon pipeline **11363** remains live with its original binaries and ownership;
latest observed first finalization was 2944.2 seconds. Read-only SQL still shows clean upload_pending.
No observation wait caused a restart. R41 remains open pending actual long acceptance and over-entry
recovery; the other design/audit gaps remain active. No commit, release publication, deployment,
production capability advertisement, subagent or Docker Sandbox substitution occurred.


A subsequent review found that CLI initial-magic/final-footer prefix reads retained the scan budget
for the entire prefix, even after its first byte arrived. New regression **12809** correctly failed
before the fix (`/tmp/skill-export-continuation-cli-prefix-before.log`). `read_after_scan` now waits
up to fifteen minutes only for the first byte, then applies ordinary thirty-second progress bounds
to the rest. This matches the Helper relay's phase transition and closes the partial-prefix stall.
Focused **85245** passed all six phase/progress tests, including staging cleanup for both prefix
stalls (`/tmp/skill-export-continuation-cli-prefix-after.log`); both handles are reaped. Final CLI
full gate **2065** is running (`/tmp/skill-export-continuation-cli-quality-final.log`). The two actual
long SSH tests retain their already-running CLI binaries; the prefix-stall change does not alter
continuation or their continuously progressing traffic. All four repository whitespace checks passed.


## 2026-09-26 — actual long frozen and stopped-work SSH continuation passed

Original long runs are terminal and reaped. **30245** (stopped-work) passed **1 test / 1 deselected
in 959.44 s**; **60917** (frozen) passed **1 test / 1 deselected in 955.36 s**. Logs remain:
`/tmp/skill-export-continuation-long-recovery-ssh.log` and
`/tmp/skill-export-continuation-long-frozen-ssh.log`.

The actual first CLI transfers took **932.732 / 932.563 seconds**, with the last successful renewal
**931.214 / 930.953 seconds after initial verification**, independently beyond the original grant's
maximum 900-second lifetime. Each used the complete **9-entry / 6-distinct-file / 33,562,777-byte**
source. Independent full content hashes and manifest metadata passed. Read-only observation confirmed
the deliberately slow 32 MiB object is first in digest order and has five objects after it; frozen
export therefore continues object opens after its original Helper reader's fifteen-minute lifetime.
The existing reader-rotation implementation and outer immutable hold preserve these reads.

Each initial transfer made **187** authority checks. The revoked second attempts failed at their
intended third check (**190**, HTTP 409) in **6.606 / 2.690 seconds**, leaving no failed output or
private staging. Complete final source inventories were unchanged and no Server finalization was
created. Both runners cleaned their own containers/images/temporary state. Their binaries preceded
only the later Helper request-write deadline and CLI partial-prefix progress tightening; current
Node/Helper and CLI focused/full checks separately cover those changes. This is actual throttled
SSH/HTTP/Native synthetic evidence, not arbitrary throughput guarantees, real Claude inference or
Docker Sandbox support.

R17/R41 and wire/Server/Node docs now close the original-grant-duration acceptance gap while keeping
recovery above the 100,000-entry protocol bound open. Original combined daemon capacity **11363**
remains active on its original handle/binaries; latest first-finalization observation is 3604.9 s.
Its completion and all other full-design audit gaps remain required. No overall completion is claimed.


Final CLI quality gate **2065** passed and is reaped. It includes the partial-prefix progress fix,
all six stream timing tests, all five Node-export contracts and complete static/Cargo/installer
checks: `/tmp/skill-export-continuation-cli-quality-final.log`. Both long-run containers are absent
from `docker ps`; only original combined-capacity resources remain from this work. This goal turn
made concrete progress in production continuation, failure handling, full gates and actual >900-second
SSH acceptance. The full objective remains active; no completion or blocked audit has passed.


## 2026-09-26 — combined daemon run failed in second finalization

On the next authoritative poll, original **11363** was terminal with exit 1 and is now reaped:
**1 failed in 16628.92 s (4h 37m)**, `/tmp/skill-default-combined-pipeline-acceptance.log`.
The runner completed first clean publication in **3817.9 s**, normal authorized reclamation in
**143.3 s**, daemon restart and independent successor materialization in **1777.6 s**. The successor
then verified every inherited byte (the fixture reaches its second finalization wait only after
that witness). Its second finalization did not reach local published state before the existing
three-hour phase deadline; last reported elapsed time was **10766.4 s**. This is an actual test
failure, not an observation timeout. Both owned containers are absent after runner cleanup.
No complete combined acceptance is claimed and no production timeout was changed.

The previous output retained only phase elapsed times. It cannot distinguish absent/pending local
capture from upload, publication or Helper acknowledgement failure; no causal explanation is yet
established. The fixture now emits only bounded local finalization states and filesystem free-byte/
inode counters once per minute. A separate owned Server observation task reports grouped finalization,
capture-error and upload states, runtime usage/reservation numbers, and sanitized template-route HTTP
counts. It selects no manifest/content/credential/identity columns, performs no writes and records a
last observation before cleanup. This diagnostic change does not replace actual acceptance or repair
the unknown failure. First static validation found a nonexistent owner column on termination rows;
the query now joins the original snapshot ownership as required. Fresh validation is in progress.


Diagnostic fixture validation passed: **30970** Ruff/mypy/full Chinese docstrings and default opt-out
(one skip, not live acceptance), **17723** Linux ARM64 compilation/vet and whitespace. The first
actual byte-control run revealed two display-only gaps: FastAPI exposes inner route templates without
`/api/v1`, and committed uploads were omitted from the fixed label set. A no-auth local ASGI
observation confirmed the route form. The filter now accepts both observed template forms while
rejecting query/body/newline strings, and `committed` is included. Final **21515** static/docstring
checks passed; all three handles are reaped. The running control retained its earlier loaded labels,
so its HTTP summary is empty and committed upload labels read unknown; its DB/capture/disk evidence
and all existing acceptance assertions remained valid.

Actual byte-only diagnostic control **24677** passed **1 test in 423.12 s**, reaped:
`/tmp/skill-pipeline-observation-byte-control.log`. First publication **157.7 s**, reclamation **55.1 s**,
successor materialization **60.1 s**, second publication **70.1 s**, final reclamation **48.1 s**.
Both complete byte checks/publications and authorized reclamations passed. Terminal DB observation
shows two clean published finalizations, 10 GiB state usage and zero state reservation. Its owned
Native/PostgreSQL resources were removed. Read-only Docker build-cache inventory was inspected to
understand shared filesystem pressure; no cache, image or unrelated resource was pruned or changed.

A new combined **10 GiB / 100000-entry / 99990-distinct-file** reproduction is now starting with the
corrected diagnostic observer, `/tmp/skill-combined-pipeline-observed.log`. This is a new execution
after the failed original and successful byte control terminated, not a restart after an observation
timeout. Production timeouts, quotas, reserve policies, transfer semantics and acceptance assertions
are unchanged. The original combined failure still has no established cause. Over-entry recovery
was inspected but no replacement protocol is implemented; v1's explicit count bound remains intact.


The combined reproduction's original live handle is **11193**. Continue polling that handle and
`/tmp/skill-combined-pipeline-observed.log`; do not restart it for observation waits. All four
repository whitespace checks passed after these diagnostics and documentation changes. No further
production code changed after the recorded Node/Server/CLI gates. The goal remains active/incomplete.

## 2026-09-26 — observed storage recovery and bounded over-entry scanner

Combined reproduction **11193** reported actual `insufficient_storage` capture-pending observations
before its first freeze. Free space was approximately **14,227,144,704 bytes**, filesystem capacity
**62,671,097,856 bytes**. The unchanged copy policy includes complete file bytes, one block per entry,
encoded metadata and `max(2 GiB, 5%)` reserve. This establishes storage admission failure for this
run only; the original **11363** second-finalization failure still has no established cause.

Read-only BuildKit inspection identified four obsolete task-specific binary COPY layers and their
descendants. An anchored exact-ID filter was verified by `docker buildx du`; all **23** selected
records were reclaimable and unshared. Only that filter was pruned, reclaiming **255.5 MB**. Exact
selection/provenance is retained in `/tmp/skill-obsolete-cache-selection.json`. No image, container,
source tree, current-run cache layer or unrelated cache was deleted. Production reserve and quotas
were unchanged. The original live process continued without restart: at **420.9 s**, its local
record was `upload_pending`, Server termination capture error had cleared to `none`, and finalization
was `upload_pending, unclean=false`. At **841.6 s**, **18,059** file PUTs had succeeded; the run remains
live and is not a combined acceptance pass. Keep polling its original handle and log.

Implemented the Linux `skillmanager.WalkRecoveryTree` primitive and documented its exact boundary in
[over-entry recovery](../../agent-remote-node/docs/skill-over-entry-recovery.md). It processes 256
names per directory with bounded depth and the original bounded preparation baseline, without a
tree-sized manifest/map, Node staging file or second content copy. It preserves ordinary entry
metadata, normalization, exclusions and runtime dependency identity. Internal link validation shares
the original manifest resolver through a metadata lookup; external content is never followed.
Capture byte/entry quotas do not truncate the read observation; signed arithmetic remains checked.
Separate recovery-domain tree and private source digests permit full-pass comparison, including
same-byte inode replacement. One pass/callback is explicitly provisional: earlier siblings can
change after local checks, so integration must compare initial/transfer/final complete observations
under independently proven writer quiescence. No v1 entry limit or production export was widened.

Validation:

- Actual Linux component **77597** passed **six test functions**, including **100,001 actual files
  in one directory**, two matching complete passes and rejection by ordinary v1 capture. The
  over-entry case took **1.62 s**; `/tmp/skill-recovery-scan-linux.log`. Additional cases cover capture
  metadata parity, unsafe links/FIFO rejection, mutation, same-byte inode replacement, earlier-sibling
  mutation, cancellation, visitor denial, byte-quota independence and depth bounds. The disposable
  container used an existing task image, read-only root and a private 256 MiB tmpfs, and was removed.
  Empty-file count evidence is not nonempty byte/SSH/lifecycle or Docker Sandbox evidence.
- Node full gate **15366** passed **62.6% coverage**, installer and consistency checks;
  `/tmp/skill-recovery-scan-node-quality.log`. Linux ARM64 vet and ARM64/AMD64 test compilation passed.
- Initial focused host **99185** and Linux **67665** also passed and were reaped; final expanded
  cases above supersede those narrower runs. All scanner/gate processes are terminal and reaped.

**Still required:** retained stopped-source coordination, separate complete recovery framing,
gateway validation, CLI bounded private staging and actual over-entry SSH acceptance. The scanner
is not reachable through the production export endpoint and does not close R17/R41. Clean-stop
classification was inspected but no cause or fix is claimed. Other outstanding audit gaps remain.
Only **11193** remains live. No commit, release publication, deployment, production capability
advertisement, subagent or Docker Sandbox substitution occurred. The full goal remains active.

The same turn then implemented `OpenStoppedWorkRecovery` and its retained source handle. It shares
the existing stopped-export source opener, keeps original snapshot/baseline/termination/work
identity, and compares complete initial/transfer/final observations. Per-file callback consumption
must match exact bytes, hash and classification; callbacks cannot skip bytes and still succeed.
Changed authority, linked/replaced work, existing captures, cancellation and source edits remain
errors. The production Helper still uses v1 export; separate recovery framing/gateway/CLI integration
and the independent Helper writer/lifecycle coordinator remain open.

Final source/scanner Linux **66642** passed all **ten test functions**, including **100,001 nonempty
files / 100,008 bytes**, complete consumption and final comparison, in **3.05 s** for that source
case. `/tmp/skill-recovery-source-linux.log`; the disposable 768 MiB tmpfs container was removed.
This small source fixture disables reserve only for creating its sealed setup metadata and is not
default disk-admission evidence. Full Node gate **20545** passed **62.6% coverage** and all installer/
consistency checks, `/tmp/skill-recovery-source-node-quality.log`; Linux ARM64 vet and ARM64/AMD64
test compilation passed. These source changes followed the earlier scanner-only gate.

Actual Linux Helper regression **82464** passed all **13 selected test functions**, no skips,
including ordinary v1 stopped/frozen export, source/writer mutation rejection, nonroot gateway,
cancellation and the real **30.05-second** idle-output stall followed by successful retry.
`/tmp/skill-recovery-source-helper-ext4-linux.log`. The disposable container used the existing task
image and a private sparse **4 GiB ext4** filesystem backed by **512 MiB tmpfs**, preserving the
production 2 GiB/5% reserve without consuming shared Docker disk for the fixture. It was unmounted
and removed. Earlier runner attempts failed before stopped-export assertions because tmpfs defaulted
to noexec, a read-only root denied useradd, and this kernel's tmpfs lacks required ACL support;
logs `/tmp/skill-recovery-source-helper-{linux,exec-linux,ready-linux}.log` retain those failures.
Their handles (including **15319/61123**) are terminal and reaped; no test assertion or production
behavior was changed to make them pass. Only combined pipeline **11193** remains live; latest
observed first-finalization progress was **1322.1 s / 41,760 successful file PUTs**, still clean and
upload-pending, with capture error cleared. Its original containers and log remain runner-owned.


## 2026-09-26 — negotiated recovery integrated; capacity fixture concurrency repaired

Node, Helper, SSH gateway and CLI now implement explicit `recovery_version:1` negotiation and the
separate `ARSKRC` recovery stream. Frozen and legacy streams keep their original format. Complete
manifest v1 remains capped at 100,000 entries; recovery uses bounded entry frames, streamed content
with trailing hash/classification, signed counters, a distinct ordered recovery digest and a CLI
private disk index. Initial/transfer/final complete source observations, original stopped-writer
proof, renewable authorization, final footer/EOF and SSH success remain required. No recovery read
creates a Node content copy, finalization receipt or deletion authority. See the updated wire contract.

Verified results:

- Node full gate **19715** passed (62.6% coverage). CLI full gate **94834** passed, including six
  export contracts; additional recovery SSH-exit contract **12031** passed.
- Actual Linux **33024** passed scanner/source and Helper tests without skips: over-entry source,
  nonroot peers, unauthorized peers, cancellation, trailing input and real stalled-output expiry
  for both formats. Log: `/tmp/skill-recovery-wire-linux.log`.
- Actual small frozen/recovery SSH **37579** passed both cases in 78.63 s, including revocation,
  independent complete bundle checks and unchanged source inventories.
- Actual CLI disk-index **61576** passed 100,001 entries in 531.30 s. Its original handle is reaped.
  This component evidence does not substitute for complete SSH acceptance.
- Actual over-entry SSH **88590** remains running on its original handle and resources:
  `/tmp/skill-recovery-over-entry-ssh.log`. New-format >900-second SSH **49223** is running:
  `/tmp/skill-recovery-wire-long-ssh.log`. Neither is a pass yet.

Combined reproduction **11193** is terminal and reaped: 1 failed in 3046.36 s. Its unchanged
process recovered from first-freeze storage admission after the previously documented exact cache
reclamation, completed first clean publication in 2898.4 s and authorized reclamation in 128.2 s,
then failed successor session admission with HTTP 409. No successor was created or inherited. Final
Server observation shows one clean publication, 10 GiB state, zero reservation and 99,990 successful
file PUTs. Both runner-owned containers were removed. The historical 409 error code was not captured;
new lifecycle errors now emit only an allowlisted code alongside status. This failure is distinct
from original **11363**'s second-finalization deadline. Neither combined run passed.

The fixture serialized **all** HTTP routes under one lock to inject unpublished test capability
after heartbeat commit. A local real HTTP reproduction established that a delayed body request
times out behind an unrelated route and subsequently returns HTTP 400 after disconnect. This
explains a concrete harness defect consistent with the observed heartbeat/reconcile 400s, but does
not identify the historical admission 409. The fixture now inserts only its explicitly test-only
skill capability into the original heartbeat request before production authentication/transaction,
without a global route lock or a post-commit readiness gap. Production Node advertisement is still
absent and asserted absent. Actual backend availability is preserved, including failed probes.

Regression **34509** passed three tests plus Ruff/mypy/Chinese docstrings: a held slow route does
not block authenticated heartbeat, failed backend reports remain unavailable, unauthorized heartbeat
stays rejected, and bounded node diagnostics omit raw probe text. The capacity observer now records
finite status, heartbeat age, native/skill-report presence and probe-error count. New small actual
SSH control **35918** is running with this fixture; existing **88590/49223** retain their originally
loaded fixture. All four whitespace checks passed. Full goal and requirement audit remain incomplete.


Actual over-entry SSH **88590** passed and is reaped: **1 passed / 1 deselected in 1051.80 s**.
The first CLI export completed in **919.515 s** after 162 authority checks; independent verification
of all **100,001 entries**, the ordered recovery journal, complete disk index and every object
finished by **952.551 s**. The second attempt rejected the deliberate revocation at check 165
(HTTP 409) in **10.675 s**, with no failed bundle or staging. Final complete source inventory was
unchanged and no Server finalization was created. Its runner cleaned the owned container. This
closes the actual over-entry SSH gap, without changing published manifest v1 or claiming unlimited
throughput. The distinct deliberately paced new-format continuation run **49223** is still active.

New-fixture small real SSH **35918** passed both frozen/recovery cases in **34.08 s**, including
revocation and unchanged inventory. Server full gate **13970** is running. Byte-control **35580**
uses the repaired concurrent fixture but currently preserves its original 10 GiB work after
`insufficient_storage`; reserve was not lowered. Observer shows that healthy and degraded Native
reports alternate during Helper activity. The running control has a diagnostic-only route-label
limitation: copying ASGI scope hid heartbeat route counters while heartbeat commits still updated
age/status. The fixture now preserves the original per-request scope; regression **96088** passed
with exact success/rejection route-counter assertions. Existing runs retain their loaded code.


Actual new-format paced SSH **49223** passed and is reaped: **1 passed / 1 deselected in 954.91 s**.
The complete CLI transfer took **933.562 s** with **186** authorization checks; the last renewal
was **930.951 s** after original verification. The deliberate revoked retry failed at check 189
(HTTP 409) in **3.880 s**. Full bundle hashes, unchanged source inventory and no Server finalization
assertions passed; the runner removed its container. Log: `/tmp/skill-recovery-wire-long-ssh.log`.

Byte-control **35580** stayed on its original process while storage admission retried. Exact cache
cleanup selected only the obsolete test binary COPY record `olthjl7ha11b7e2rttp975pgc` and its five
descendants; all six were unshared/reclaimable and the anchored-ID preview matched exactly. Prune
reported **63.91 MB**. Selection is `/tmp/skill-concurrent-fixture-obsolete-cache-selection.json`;
no image/container/source or unrelated cache was removed. Together with completed export-run cleanup,
this let the original control begin freezing at about 480 s without changing production reserve.

A separately opted-in macOS destination-exhaustion fixture is now implemented using an owned 8 MiB
HFS disk image, a >32 MiB stopped-work source, real CLI/SSH, observed free-space/pending-file counters,
failed-output cleanup and a subsequent complete retry on the ordinary destination. The disk-image
create/attach/detach probe passed; focused Ruff/mypy/full docstrings **70741** passed. Actual export
acceptance has not run yet. It waits for the byte-control storage-sensitive phase to finish.


Destination-exhaustion setup **60017** failed before any export because the independent Node runner
correctly rejected the missing matching opt-in. Added a separate `export_destination_full` fixture
field and explicitly forwarded environment flag; ordinary long-link configuration stays separate.
Linux ARM64 vet, shell syntax and focused Server static checks passed. Retry **71250** passed and
is reaped: **1 passed / 1 deselected in 29.27 s**. The isolated 8 MiB HFS image began with
**8,146,944** free bytes; observed free space fell to **20,480** while the pending object reached
**8,060,928** bytes. CLI failure left no output or staging. A fresh ordinary-destination export
completed in **2.325 s**, independently verified all >32 MiB content, and the deliberate revoked
retry failed at check 8 (HTTP 409) in **2.267 s**. Full source inventory stayed unchanged. Image
detach/removal and runner-owned container cleanup completed. No production code changed for this test.

The byte control **35580** completed first publication (605.2 s), reclamation (60.1 s), actual daemon
restart, successor admission and full independent materialization (64.9 s). Its second source is
retained at storage admission while other test builds expanded the shared Docker cache. A verified
anchored-ID filter removed only nine obsolete task-cache records: the old test package layer
`j5d39e5ho1c18cqx1p6v6gfhc` and two descendants, plus the completed over-entry binary COPY
`h71eakse80vkxldvoch7qobo6` and five descendants. All were unshared/reclaimable; prune reported
**508.4 MB**. Exact selection: `/tmp/skill-completed-runs-cache-selection.json`. The now-unused,
task-owned `agent-remote-recovery-component:local` image was also removed after confirming no
container used it. No live source, unrelated image/cache or production reserve was changed.
The byte control and Server full quality gate **13970** remain active on original handles.


Server full gate **13970** passed and is reaped: **1817 passed, 97 skipped, 83.04% coverage**,
all required formatting/lint/type/docstring checks passed. It loaded tests before the later
destination-exhaustion addition and route-scope diagnostic correction; those changes passed their
separate focused static/live/regression checks. Log:
`/tmp/skill-recovery-concurrent-fixture-server-quality.log`.

The second capacity freeze resumed on the original process after removal of the six exact
unshared/reclaimable cache records rooted at the failed setup's obsolete binary COPY
`taos34e5tczj3bs4kiiq2t9u6` (64.01 MB; preview and IDs retained in
`/tmp/skill-failed-destination-setup-cache-selection.json`). This preserves the successful latest
destination-test build and live byte-control build cache. At the next direct filesystem observation,
free space was 3,175,297,024 bytes because the second 10 GiB frozen copy had been allocated.
The actual control is still running; allocation is not publication.


Byte-control **35580** is terminal and reaped: the Native Go test **passed** both clean publications
(605.2 / 606.9 s), original-authorized reclamations (60.1 / 53.2 s), daemon restart and full independent
successor inheritance (materialization 64.9 s), in **1416.09 s**. The **overall Python test failed**
in **1423.31 s** because editing the shell runner while Bash waited inside it changed the remaining
file offsets: after Go reported PASS, Bash resumed with `unexpected EOF while looking for matching
quote`. Final Python DB assertions therefore did not execute. This is a launcher failure, not a
complete acceptance pass or a failed Native publication; all owned containers were cleaned.

Both Server launchers now execute an immutable copy of the script text through structured
`bash -c` arguments with the original script path as argv[0]; the runner derives its repo path from
that original argv[0]. No fixture secrets enter the script text. Later workspace script edits cannot
change its exit/cleanup phase. Focused Ruff/mypy/docstrings **83700** and shell syntax passed.
The new-format actual **10 GiB + 1 MiB** stopped-recovery SSH regression is running as **6924**:
`/tmp/skill-recovery-wire-oversize-ssh.log`. After that, repeat the byte control with the immutable
launcher before starting the combined capacity reproduction.

Now that byte-control resources are gone, the obsolete earlier package/cache chain rooted at
`zonzf5wy0rsmm3g2bc28huyhl` and all eight descendants was separately previewed and pruned by exact
anchored IDs, all unshared/reclaimable. The reported **508.4 MB** cleanup preserves the current
package and binary cache used by the running above-byte export. Selection:
`/tmp/skill-completed-byte-control-cache-selection.json`. No broad prune or reserve change occurred.


Actual new-format above-default-byte SSH **6924** passed and is reaped: **1 passed / 1 deselected
in 239.79 s**. The complete **10 GiB + 1 MiB / 36-entry** export took **71.964 s**, with independent
all-object verification finished by **76.639 s**. The revoked retry failed at check 18 (HTTP 409)
in **9.130 s**, leaving no failed output/staging. Final source inventory stayed unchanged and no
Server finalization was created. The immutable shell launcher completed successfully and removed
its resources. Together with 88590, 49223 and 71250, this closes the recorded R17/R41 recovery
acceptance gaps without widening manifest v1 or enabling production/Docker Sandbox capability.

The repeat byte control **91240** failed during test-image setup in 3.90 s, before Native work.
The fixture's public CA now uses a BuildKit mount instead of COPY into the package layer so rotating
CA input does not duplicate that entire cache on each run. Its initial mount was root-only; APT's
unprivileged downloader could not use it. The public CA mount now specifies 0444. Shell syntax
passes. A fresh byte control **34942** is running with the immutable launcher and corrected mount:
`/tmp/skill-pipeline-immutable-byte-control-retry.log`. This is a new execution after the failed
setup ended, not an observation-timeout restart. All original capacity assertions and reserve
policy remain intact. No success for 34942 or combined reproduction is claimed yet.


The immutable-runner byte control **34942** passed and is reaped: **1 passed in 494.11 s**.
Both clean publications (165.5 / 62.2 s), original-authorized reclamations (47.3 / 54.1 s),
actual daemon restart and full independent successor inheritance (53.6 s) passed, including the
final Python database assertions. Final state was two clean published finalizations, exactly
10 GiB state and zero reservations. HTTP observations included 119 successful heartbeats, 141
successful reconciliations, two successful session admissions and 40 successful file PUTs; no
heartbeat/reconcile HTTP 400 was reported. Both owned containers were removed. The initial
insufficient-storage capture was retained and retried without changing the reserve policy.
Log: `/tmp/skill-pipeline-immutable-byte-control-retry.log`.

Concurrent-fixture actual CLI lifecycle **69090** also passed and is reaped: **2 passed in
375.93 s**, covering normal and upload-unavailable cases through the actual CLI, SSH, Mutagen,
Worker and Helper with the bounded stop observations enabled. Owned runtime resources were
removed. Log: `/tmp/skill-concurrent-fixture-cli-lifecycle.log`. These synthetic tool passes
do not resolve the historical intermittent unclean stop or establish actual Claude learning.

New combined 10 GiB / 100,000-entry daemon reproduction **3109** is running on its original
handle with the repaired concurrent fixture, immutable runner and stable package cache.
Log: `/tmp/skill-pipeline-concurrent-combined.log`. Its owned resources are
`agent-remote-ssh-export.RVfYhy` and `agent-remote-pipeline-test.7nZwAm`. The first reported
capacity observation had 13,359,210,496 free bytes before a frozen capture. No broad cache
pruning, production reserve reduction or restart was performed. A running test is not a pass.


Combined **3109** retained its first source after insufficient-storage admission. Exact cache
reclamation removed ten reviewed unshared/reclaimable records: the obsolete byte-control package
chain rooted at `5qncu1zzjm4l1vhsg8t84c2fk` (nine records) and the unused earlier kernel-acceptance
package record `ysyldhl9fv1hau3pm0i3vffta` (no descendants). The latter command was matched to
`tests/linux_skill_kernel_reboot_test.sh`; no kernel test container remained. Anchored exact-ID
preview was revalidated immediately before pruning; **1.277 GB** was reclaimed. Selections and
preview: `/tmp/skill-combined-obsolete-package-selection.json`,
`/tmp/skill-combined-retired-kernel-cache-selection.json`,
`/tmp/skill-combined-headroom-cache-preview.jsonl`; log:
`/tmp/skill-combined-headroom-cache-prune.log`. Current package cache, running containers and all
source/state were preserved. The original process subsequently froze and began uploading its
clean first finalization, with the full 10 GiB reservation. No restart or reserve reduction occurred.

A separate R25 review found a deterministic classification defect: managed stop could use a
successful unit result observed only after `systemctl stop` to certify clean input, although forced
cleanup may have killed remaining writers. The new Linux regression first failed with
`Unclean:false` for that scenario; its graceful control passed. Managed clean classification now
requires normal success plus empty whole cgroup **before** forced cleanup. Legacy stop reporting
keeps its prior semantics. The clean capture fixture now models an already completed normal exit
instead of incorrectly equating forced-cleanup success with clean application exit. This stricter
classification does not identify or fix the historical intermittent **unclean** classification.

Focused Linux stop/cgroup/exit/capture regressions passed. Full Node gate **67378** passed with
**62.6%** coverage and is reaped; log: `/tmp/skill-native-stop-clean-boundary-quality.log`.
Actual systemd Native lifecycle **27595** passed all six cases in **34.60 s**: normal, error,
SIGKILL, graceful stop, canonical interrupt and forced stop. It used current test/runtime binaries
mounted read-only into an independent private-cgroup container, reusing the existing fixture image
without rebuilding packages. Its container was removed; log:
`/tmp/skill-native-stop-clean-systemd.log`. The combined capacity run loaded the earlier binary
and is not relabeled as coverage of this later stop change. Full Linux Helper package **3710**
is still running: `/tmp/skill-native-stop-linux-helper.log`.


Full Linux Helper package **3710** passed and is reaped, completing the stop-boundary change checks.
No actual capacity result is inferred from that package gate.

R48 now has a narrowly scoped previous-boot completed-result path. A separately authorized recovery
may revalidate an original writer-version-2 **whole-migration succeeded** receipt after kernel
change. It must retain the original copy/target ownership and phase proofs, no rollback, valid
account/backup, unchanged metadata and repeated absence of current services/cgroups. Empty or linked
current cgroups also block it. This path cannot create phase/whole receipts, rewrite the original boot,
change ownership/ACLs or promote started old-boot work. Historical whole success follows filesystem
sync; old phase successes alone are deliberately insufficient. Server/CLI request/result shapes
are unchanged; their shared contract notes were updated.

Focused Linux run **80705** passed all twelve new previous-boot cases and the existing explicit/
completion recovery tests; its first attempt **38462** failed only because the test tried to add
a rollback intent after an immutable terminal receipt. The test now constructs rollback-pending
input before terminal completion, preserving the production invariant. Full Node gate **33504**
and full Linux Helper package **91894** passed and are reaped; Linux ARM64 vet passed. Logs:
`/tmp/skill-migration-oldboot-focused.log`, `/tmp/skill-migration-oldboot-quality.log`,
`/tmp/skill-migration-oldboot-linux-helper.log`. These gates precede the later kernel-test addition.

A genuine two-kernel acceptance case is now implemented behind
`AGENT_REMOTE_KERNEL_TEST_CASE=migration tests/linux_skill_kernel_reboot_test.sh`. It executes
original copy/ownership services, retains whole-completed and phase-only fixtures, then checks after
an external power cut that only whole completion recovers, with unchanged full inventories and
no additional writer launches. It has passed compilation/vet and shell syntax, but has **not run**.
Its VM allocation is deferred until combined **3109** releases first-source space. R48 remains open
for that actual acceptance, interrupted ownership repair, incomplete old-boot work and rollback
attestation. No production capability, release or deployment was enabled.


Current checkpoint: combined **3109** is still running on its original handle and containers.
At 1261.6 seconds in first finalization it had **40,209** successful object PUTs, 541 successful
heartbeats and 975 successful reconciliations. The first input remains clean/upload_pending with
its 10 GiB reservation; publication, restart, inheritance and second finalization are still pending.
Log: `/tmp/skill-pipeline-concurrent-combined.log`. No heartbeat/reconcile HTTP 400 was observed.

Final formatting, shell syntax, Linux ARM64 vet and all four whitespace checks passed after the
kernel fixture addition. The kernel fixture also compiled for Linux amd64 (**12512**, reaped).
No actual kernel execution has started; wait for combined first-source reclamation to provide
space for its owned VM disk and image. The combined run loaded code before the two production
fixes in this continuation; its result must retain that execution boundary.


Actual previous-boot migration acceptance **40101** passed and is reaped. An amd64 guest ran on
native arm64 QEMU; the seed kernel executed real copy/ownership services for both whole-completed
and phase-only original migrations. After external power cut, the second kernel accepted only the
durable whole success, rejected phase-only completion, verified unchanged complete account/backup/
receipt inventories and retained exactly four original writer launches for each input. Recovery
test time was **1.44 s**. Kernel boot IDs were independently distinct. Log:
`/tmp/skill-migration-actual-kernel-retry.log`. This is actual Helper/VM evidence with synthetic
accounts, not account enrollment, model inference or Docker Sandbox runtime acceptance.

The first run **96824** failed and was reaped during image setup: the foreign-architecture shell
could not execute the permission-only chmod layer (exec format error). No VM or migration ran.
The runner now uses `COPY --chmod`, avoiding that foreign execution. The optional
`AGENT_REMOTE_KERNEL_TEST_DISK_ON_HOST=1` places its owned raw disk in the private host test directory,
while retaining the same guest ext4, cache mode, fsync, power-cut and reboot assertions. Both seed
and recovery kernels ran successfully; all owned VM/container/image/disk/temp resources were removed.

Five exact reviewed cache records from the completed/failed kernel runs were then previewed and
pruned: the native QEMU package chain `zo5k1adoug47kmoipvz7v99sp` and two descendants, plus the two
obsolete guest fixture COPY records `2lz6gs6nqv3n8opdohav3h4p1` and `zv7gvbl007enkaz3y386qgik6`.
All were unshared/reclaimable; **1.172 GB** was reclaimed. Selection, anchored preview and log:
`/tmp/skill-migration-completed-cache-selection.json`,
`/tmp/skill-migration-completed-cache-preview.jsonl`,
`/tmp/skill-migration-completed-cache-prune.log`. The current capacity fixture/package and sources
were untouched; observed free space returned to **3,230,064,640** bytes. No reserve was reduced.
Combined **3109** remains live on the original process.


## Continuation: bounded Claude discovery evidence and runtime diagnostics (2026-09-26)

Claude learning acceptance now selects `learning` by name, enables the real Skill tool and uses
independent canonical session UUIDs. Private account-local JSONL verification requires a matching
successful Skill invocation/result in each exact session. Direct reads, wrong sessions, failed or
unmatched calls, malformed/truncated/oversized traces, duplicate transcripts and symlinks are rejected.
All 22 parser cases and eight actual Linux filesystem cases pass; no transcript/model output is logged.
The dedicated Linux credential-path question remains pending. Host auth availability was inspected
without reading/exporting login state; it is not the requested fixture or inference evidence.

The learning runner now uses HTTPS APT with a public CA BuildKit secret and immutable script text;
private fixture/credential copies remain outside the build context. Node host gate **36513** passed,
Linux compilation/vet and shell syntax passed, and Server Mypy/docstring plus focused fixture tests
passed (two tests, two opt-in skips). Real inference remains unexecuted.

Stop diagnostic **52439** from the preceding continuation failed during `skill add` admission before
any session existed, after package-cache growth reduced free disk below the production reserve.
Nine exact reviewed reclaimable cache records rooted at `ifujc6m76luieg32i0g92pq59` released 508.5 MB;
selection/preview/prune logs are `/tmp/skill-stop-failed-admission-cache-*`. This is no stop evidence.
The subsequent retry **29110** failed downloading Mutagen; runtime smoke **50424** failed APT TLS.
Both direct and existing local proxy routes failed TLS; neither attempt reached runtime execution.

A temporary immutable runner snapshot reused the existing owned Native image's installed packages
and rebuilt/replaced current binaries and real Claude. An initial SHA-only FROM attempt **30152**
failed image resolution. The tagged local-image retry **17226** passed runtime-only acceptance in
21.81 s; a later pass **55611**, with the probe/pane-wait changes below, took 26.16 s. Logs:
`/tmp/skill-discovery-runtime-cached-retry.log`, `/tmp/skill-probe-pane-runtime-smoke.log`.
These runs do not test fresh package downloads, inference, enrollment or Docker Sandbox.

During the long combined run, lifecycle-lock contention made independent health probes expire.
The new regression **30875** failed before the fix with a socket timeout while the mutation mutex
was held. Probes now use an independent cancellable mutex, with a shared three-second queue/command
budget, bounded output and child-process-group cancellation. Authentication, payload checks, current
availability checks and mutating-operation serialization remain. No capability advertisement was
enabled. Focused regression **51597**, full Node gate **2436** and full Linux Helper **96242** passed.
Logs: `/tmp/skill-probe-mutation-{before,after}.log`, `/tmp/skill-probe-pane-quality.log`,
`/tmp/skill-probe-pane-linux-helper.log`.

Repeated actual systemd graceful-stop testing reproduced R25: **46071** passed 27/30, with three
missing tmux exit statuses; current binaries plus a bounded missing-status wait (**77125**) passed
96/100, so that wait alone does NOT resolve R25. The wait covers a separate deterministic case:
a HUP-ignoring process closes its pty and then exits zero. The original observer fails this case
(**52505**); the new observer passes it, but the full pane integration **62085** still saw an
intermittent ordinary-zero failure. An earlier fixture lacked HUP handling and was corrected;
its failure does not establish a normal-exit regression. Unknown/late/nonzero statuses remain
unclean and pre-stop whole-cgroup proof remains mandatory. Diagnostic-only observations **78756**
and **90964** showed no final status/signal, with the pane process a zombie and tmux still sleeping.
A separate child-event diagnostic **11157** is still running. No historical CLI failure is yet
claimed causally resolved. Original repetition logs are `/tmp/skill-stop-{repeat-current,
repeat-fixed,signal-observation,process-observation,reap-observation}.log`.

Combined **3109** remains on its original process and loaded code. It completed first clean
publication in 2801.8 s and authorized local reclamation in 125.3 s. Daemon restart and successor
admission succeeded. Full successor materialization is progressing; inheritance and second clean
publication/reclamation remain pending. It predates this continuation's production changes and
cannot certify them. R25/R40/R46/R48/R49 remain open; no commits, deployment or release occurred.


Child-event diagnostic **11157** finished (retaining its original failed result): the pane was a
zombie, tmux sleeping, and the fixed no-op child caused the original pane's actual zero status to
be collected. The final bounded recovery now requests that fixed child at most once per 200 ms
within the original one-second missing-status window; only the original canonical zero exit can
succeed. It does not send new terminal interrupts or infer status from the no-op. Whole-cgroup and
original-invocation checks remain required. Final current-production systemd repetition **67940**
passed **100/100**; **85701** passed 50/50 actual tmux cases; **54606** passed all six systemd lifecycle
cases. All are terminal and reaped. Full Node gate and Linux Helper **56826** pass (62.9% host
coverage), Linux ARM64 vet and AMD64 compilation **75712** pass. Logs are linked in the Node stop
diagnostic document. This fixes the reproduced component failure; full current CLI verification
remains blocked by external Mutagen download TLS, without relabeling all historical failures.

Full Server gate **2441** passed and is reaped: **1,817 passed, 97 skipped**, **83.04%** coverage,
plus Ruff, Mypy, docstrings and whitespace. Log: `/tmp/skill-discovery-server-quality.log`.
Current runtime-only Claude smoke **14239** is running with the same explicitly recorded cached-base
adaptation. Combined **3109** remains live; at 1752.8 s its successor was still materializing.
The original combined log and execution boundary remain unchanged. No credential path has arrived.


Final current-binary real Claude runtime-only smoke **14239** passed in **20.29 s** and was reaped.
It verifies ordinary Native startup, clean publication and authorized reclamation with the current
probe and reaping fixes, using the previously documented cached dependency image. Its log is
`/tmp/skill-reaping-runtime-smoke.log`. All newly owned diagnostic/smoke containers have exited and
been removed. The task-only local base-image alias was removed; the original combined image and
containers remain. Combined **3109** is still live at successor materialization, with 94,714 successful
snapshot-object GETs and 180 lease renewals at 1813.2 s. No full combined pass is claimed yet.


## Continuation: backup integrity, renewable recovery, and production status constraint (2026-09-26)

Passive same-boot completion and previous-boot whole-success recovery now compare the complete
account and original backup, twice around filesystem synchronization. Bounded descriptor-relative
openat2/statx traversal hashes streamed content, empty directories, opaque links, within-tree hardlink
topology and data xattrs. Separate private digests cover UID/GID/mode/all xattrs and original inode/
mount/timestamp observations. Special files, linked roots/ancestors, nested bind mounts, external
hardlinks, changed or incomplete copies fail closed. No content/path/fingerprint is exported.
These are current retained-copy checks, not historical pre-copy or exact rollback attestation.

The explicit v1 recovery remains passive. A new Node-only lease POST repeats original account/task/
poll eligibility under user/task locks, extends at most 300 seconds and returns conservative duration
metadata. Worker supervises renewal through Helper inspection and result acceptance, cancels on
uncertain renewal and allows an acknowledged terminal result to win a concurrent terminal refusal.
The dedicated Helper call/handler have a 15-minute total deadline, disconnect cancellation and
cancellable lifecycle-lock waiting. The 11-field binding and terminal result are unchanged.

Initial Linux existing recovery contracts passed (34764). Inventory boundary cases, including actual
bind-mount refusal, passed (13027's inventory subset and clean focused rerun). That broad 13027 run
also selected real-systemd cases in a container without init and failed setup; it is not a full pass.
Correct systemd runs 3215 and 51937 pass all migration cases. Full Linux Helper 58160 and current
lease-integrated 64306 pass. Current Node host gate 70376 passes with 62.9% coverage; ARM64 vet and
AMD64 compilation 41685 pass. Actual two-kernel migration proof 25345 passes with current binaries:
complete old-boot success recovers, incomplete original stays blocked, bytes/metadata/launch counts
remain unchanged. Logs are `/tmp/skill-migration-inventory-{boundaries,systemd-final,kernel}.log`,
`/tmp/skill-migration-lease-{node-quality,linux-helper,node-tests}.log`.

PostgreSQL testing first exposed an invalid old fixture Node status (`online`), then a production
schema gap: migration service uses `migrating` but the account check constraint omitted it. Fixture
uses `healthy`; migration 0056 and ORM metadata now include the existing migrating state. No rows
are rewritten; downgrade locks the table and refuses any migrating account before changing the
constraint. Six genuine PostgreSQL concurrency cases pass (39943); all six plus real guarded
upgrade/downgrade pass (79041). Tests cover fresh authorization/renewal after a blocking transaction
commits or rolls back its profile change. HTTP authority/lease tests pass, including wrong binding,
expired/reissued/terminal attempts, configured duration bounds and non-Node authentication. Logs:
`/tmp/skill-migration-lease-postgres{,-fixed,-schema-fixed,-final}.log`; the first two are failed
reproductions, not passing evidence. Full Server gate 61528 is still running and predates the ORM/
0056 addition; a final current-schema gate remains required.

GitHub Mutagen downloads now work. The official Darwin ARM64 0.18.1 archive was downloaded and
matches SHA256 `6f810416d9e5fc4fd5e18431146f8b3c5a2056ba5a24f76c1e66da86eb3257e2`.
Current full CLI normal/upload-unavailable acceptance 50719 passes both cases in 65.20 s. It uses
current CLI/Node/Helper binaries, real Mutagen, synthetic tool content and cached Native dependency
image a4ac1b1c...; no Sandbox substitute or real inference claim. The temporary runner builds binaries
on the host and bind-mounts the exact current proof files into a fresh container, installing only
current synthetic fixture scripts there. It avoids new package/image copies on the constrained disk.
The original image/container is retained. Initial temporary plugin 83622 failed before test setup
because of a function-name typo; corrected run 50719 is the passing evidence. Log:
`/tmp/skill-current-cli-lifecycle-cached-retry.log`. Current daemon/CLI passive recovery 13996 is running
with the same explicitly adapted runner; its final outcome is pending.

Original combined capacity 3109 remains live. It completed successor materialization in 2801.2 s,
then could not freeze within the production disk reserve. Twelve exact independently reclaimable
cache records from completed runtime smokes released 1.218 GB. After the current two-kernel proof,
five exact completed kernel-test cache records (including its unused guest-package cache) released
1.970 GB. Preview/prune logs are `/tmp/skill-inventory-{owned,kernel}-cache-*`; no broad prune,
reserve lowering, original fixture/source deletion, restart or binary replacement occurred.
The second complete snapshot is now clean and upload_pending; both capture diagnostics are `none`,
and upload object PUTs have advanced beyond 108,000. Full second publication/reclamation is pending.
This process still predates current stop/probe/recovery fixes and cannot certify those changes.

R40/R46/R48/R49 remain open. No dedicated Linux Claude credential path has arrived; no host login
state was read/exported. No commit, release, deployment or production Skill advertisement occurred.


Current CLI/production-daemon passive recovery 13996 passed both lost-replies and missing-backup
cases in **24.93 s**, with the current lease and inventory changes and the documented cached-base
runner. Its log is `/tmp/skill-current-recovery-daemon-cached.log`. Current HTTP model tests pass
41 cases; lease duration edge cases pass separately. PostgreSQL 79041 passed all seven concurrency
and guarded status-migration cases. Temporary acceptance containers have exited and been removed.
No full fresh dependency-image build is claimed. The original combined process is now transferring
its second clean frozen snapshot (beyond 108,000 total PUTs); its complete result remains pending.
A functions execution cell **6789** owns waiting on original Server gate **61528**, then starts the
final current-schema full gate at `/tmp/skill-migration-final-server-quality.log`. Preserve those
handles: the earlier gate was started before ORM/0056 edits and does not certify that final schema.


Final inventory review added explicit rejection when account and backup resolve to the same root
inode, including different bind-mount IDs. A same-path backup is also rejected. Current migration
systemd suite **44231** passed with the real root-alias mount regression; ARM64 vet and whitespace
passed again. This is an additional independent-backup guard, not a change to passive recovery
semantics. Log: `/tmp/skill-migration-inventory-root-alias-systemd.log`. Lease duration tests passed
14 HTTP cases (`/tmp/skill-migration-lease-duration-tests.log`). The original Server gate remains
running; cell 6789 still owns its final-schema follow-up. Combined 3109 is still on its original
handle, uploading the second clean snapshot; no complete combined pass is claimed.


## 2026-09-26: historical migration permissions and immutable attestation

New Node whole-migration receipts now use version 2, separately from the unchanged copy/writer
version 2 and external passive-recovery binding version 1. Before the original backup starts,
Helper saves a private immutable baseline after two full source scans and repeated parent checks.
It binds original task/configuration/boot, account root identity, complete content/topology/data
xattrs, UID/GID/full mode/all xattrs and the original parent chain's identities and ACL values.
Baseline creation is rejected after any original copy receipt. Historical whole-version-1 records
retain their original proof requirements and are never upgraded into historical attestation.

New ownership requires the baseline. Before target writes, current source and independent backup
must both match the original content and permissions. At completion, repeated checks around syncfs
and original writer/quiescence revalidation precede an immutable baseline-bound attestation and
terminal whole receipt. Failure additionally requires exact original account and parent permissions.
Source-backend ACL commands that leave target named-user ACLs or other permission differences now
leave the migration pending. Local admission and terminal replay require version-2 baseline and
attestation integrity; damaged, linked, missing and orphaned evidence stays closed. Passive recovery
checks historical backup permissions even for a previously succeeded original.

Fresh backup directories use anchored no-follow traversal and exclusive mkdir; existing backups,
including empty directories, are retained errors. A real daemon test caught an initial overly strict
StateRoot check: production deliberately grants Worker traversal and uses the Worker group. The
corrected implementation permits root-owned, non-writable-by-others StateRoot traversal, while
requiring root-owned mode 0700 only for its migrations child. It preserves existing permissions and
checks cancellation between directory operations. Linked ancestors, unsafe parent modes/owners,
foreign paths and reuse are rejected before copy.

Evidence completed so far:

- Host Node quality gates 84508 and 2868 passed (62.9% statement coverage). ARM64 vet and AMD64
  compilation passed; newer Linux-only destination checks also passed focused ARM64 vet.
- Actual systemd migration/baseline suites 14913, 71602, 55420, 97692 and corrected traversal suite
  66857 passed. Complete Linux SkillManager and Helper packages plus actual systemd migration
  cases passed in 37579 before the later destination-directory guard. Complete-backup tampering,
  mutually modified trees, parent replacement/ACL changes, source rollback differences and exact
  passive revalidation of new records are covered. Two-kernel acceptance predates this new baseline.
- Private journal/attestation corruption and terminal-history checks passed in 18441. Actual
  source baseline and existing/new schema compatibility tests passed. Logs:
  `/tmp/skill-migration-baseline-{linux-final,compat-systemd,attestation}.log`.
- Initial 44295 reproduced the old fixture's false assumption that source-backend ACL application
  proves original permissions. The revised fixture includes both exact restored source permissions
  and retained residual target ACLs. Initial full-package runner 86588 lacked testdata; corrected
  37579 mounts the actual testdata and passes. Neither failed run is a full pass.
- Current CLI/production-daemon tests passed 86271 (2 cases, 26.72 s) and 31794 before the new
  destination guard. Guard run 84535 exposed the actual traversable StateRoot compatibility issue;
  corrected current daemon acceptance 5086 passed both cases in 22.94 s, using freshly built
  Node/Helper binaries and the production units. Log:
  `/tmp/skill-migration-baseline-compatible-daemon.log`. The earlier guard run failed both cases
  in 368.49 s and is retained as the failed reproduction. All its containers have been cleaned.

Original Server quality 61528 passed 1827 tests, 99 skipped, 82.97% coverage. Its watcher 6789
started current-schema gate 15723, which finished with 1830 passed, 100 skipped and one failure:
`test_alembic_revision_graph_has_one_resolvable_head` still expected 0055 after the intentional 0056
status-constraint migration. The expected head is corrected to 0056; all 17 focused persistence/
status-migration tests pass, with the opt-in PostgreSQL case skipped in this command. Ruff and
Chinese-docstring checks also pass. The previous genuine PostgreSQL seven-case proof remains valid.
This is a completed full run with its single stale test assertion corrected separately, not a claim
that the original full-gate invocation returned success or that a second full run occurred.

Original combined capacity handle 3109 remains running on its older binaries, with the second clean
snapshot upload advancing beyond 189,000 total object PUTs. First publication/reclamation, daemon
restart and complete successor materialization remain passed; final second publication/reclamation
is pending. No original resources were restarted, replaced, pruned or removed in this continuation.

R48 now has historical baseline and exact rollback verification for new original execution.
Actual permission restoration when the original source differs, supervised interrupted repair,
incomplete previous-boot recovery and explicit Server source-profile reopening remain unfinished.
R40/R46/R49 also remain open. Dedicated Linux Claude credentials have not arrived; no host login
state was copied. No commit, release, deployment, production capability advertisement or subagent
was used. The implementation goal remains active and incomplete.


Final outcomes for this continuation:

- Corrected current CLI/production-daemon migration recovery 5086 passed **2 cases in 22.94 s**.
  The new baseline, immutable attestation and safe private backup creation all ran through the
  current shipped Worker/Helper service units. Its earlier strict-StateRoot reproduction 84535
  failed both cases; corrected tests retain the production root traversal and Worker group.
- Full current Linux SkillManager, Helper and actual systemd migration suites **93179 passed**,
  including all final baseline/attestation and backup-directory changes. Log:
  `/tmp/skill-migration-baseline-current-linux.log`. ARM64 vet and four-repository whitespace
  checks passed. The prior full Node host gate passed at **62.9% coverage**.
- Original combined capacity **3109 passed: 1 case in 10083.97 s (2:48:03)**. Both sessions
  published clean snapshots with the same full content identity; daemon restart and complete
  independent successor byte verification passed, followed by both fresh-authorized reclamations.
  First publication took 2801.8 s, first reclamation 125.3 s, successor materialization 2801.2 s,
  second publication 4118.8 s and second reclamation 152.4 s. Final HTTP counters include **199,980 successful object PUTs**,
  two completion/publication calls and two fresh reclamation-authorization reads. Both capture
  diagnostics were none. Node's final observation returned healthy with no probe errors.
  Log: `/tmp/skill-pipeline-concurrent-combined.log`.

R40's complete combined capacity scenario now has direct passing evidence. This long process
retained its original older binaries throughout, so it does not certify current stop/probe or the
new migration implementation. Temporary degraded probe observations during reclamation remain
part of that old-binary log; they are not hidden or reclassified as current-code results. No reserve
was lowered and no original unique input was removed to make capture succeed. The existing runner
owns cleanup after its completed test.

R46/R48/R49 remain open: actual Docker Sandbox is unavailable; interrupted ownership repair,
exact permission restoration and Server source-profile reopening remain to implement; real Claude
inference/enrollment and independent accounts/sessions still await the dedicated Linux credentials.
The full implementation goal is not complete. No new permission request or rollout was made.


Original combined shell handle 3109 has now exited with status 0. Its owned export and PostgreSQL
containers are gone. The runner's normal image cleanup also removed shared Native base image
`sha256:a4ac1b1cebad6f748d87fed959667e271db44e7bff2968a80c1fbd4a1fb3cbea`; an explicit inspect
confirms it is no longer available. Do not reuse the temporary cached-base acceptance runner while
assuming that image still exists. Future Linux acceptance needs an available verified dependency
image or an ordinary fresh build. The verified host Mutagen archive and Claude executable remain.
All other test handles from this continuation are terminal; Server watcher cell 6789 is finished.


## 2026-09-26: exact original permission restoration during rollback

The preceding goal turn was substantive progress: historical baselines/attestation landed and
combined capacity 3109 completed. This continuation implements the next R48 behavior rather than
leaving source-backend ACL reapplication as the only rollback operation.

During first original whole-version-2 migration execution, successful drained rollback ACL phases
now lead to exact historical permission restoration. The Helper requires its original pending
record/current boot, distinct target/source ownership intents, copy success, complete rollback
writers and unchanged historical content/backup permissions. Existing rollback intent precedes all
synchronous writes. The executor is not reachable from passive replay or the v1 recovery operation.

Descriptor-anchored traversal restores original UID/GID, full mode, POSIX access/default ACLs and
file capabilities from the verified independent backup, with capabilities last after chown/chmod.
Absent original ACLs are removed. Opaque symlinks receive only no-follow ownership restoration.
Retained bounded inode/hardlink indexes reject unknown inodes, link-count changes and swaps between
known canonical link groups; nested mounts, root aliases and substitutions remain rejected.
Shared traversal parents must retain their original identity and ownership and receive only their
saved modes/ACLs. File content and ordinary data xattrs are not rewritten, and backup evidence is
unchanged. Any cancellation or error keeps the whole migration pending; final repeated inventory,
syncfs, quiescence and immutable attestation still precede terminal failure.

Code is in Node `internal/runtimehelper/migration_restore{,_tree}_linux.go`, integrated into
`account_migration_linux.go`. The inventory scanner now optionally returns its existing private
hardlink index; public task/results and historical schema are unchanged. No new process, service,
privilege, API action or original-writer identity is introduced for these synchronous first-run
writes. Explicit interrupted repair still needs a separate new recovery task and authority.

Validation:

- Actual systemd migration suite 76939 passed, including rollback from custom original source
  permissions and residual target ACLs. Previously these cases stayed pending because source
  policy ACLs differed from the historical baseline; now they return the original terminal failure
  only after restoring its exact source permissions.
- Extended suite 75214 passed cancellation after an actual file-mode write, unchanged backup/
  account bytes, capabilities/set-ID bits, internal hardlinks, opaque-link ownership, parent ACL
  restoration and changed/aliased-input rejection. No completed restoration is returned on cancel.
- Full Linux SkillManager/Helper and actual systemd migration suites **29025 passed** after the
  final original-target-intent guard. Log: `/tmp/skill-migration-restore-linux.log`.
- Full host Node quality **66856 passed**, with **62.9% coverage**. ARM64 vet and AMD64 compile
  passed; four-repository whitespace verification remains clean.
- Current CLI/production-daemon passive recovery **79547 passed 2 cases in 25.11 s**, confirming
  the unchanged v1 contract and original reply-loss/missing-backup behavior. It uses newly built
  current binaries and production service files, with no synthetic mutation receipt inserted as
  proof. Log: `/tmp/skill-migration-restore-daemon.log`.

A fresh isolated Native dependency image was built from Debian for these tests because the original
combined runner correctly removed its old image. The new owned test image is
`agent-remote-migration-repair-proof:20260926`, immutable ID
`sha256:8ead145a652dcf965ed89b867b4db9e28cce0a04e90da640c98e77e0f2d5ad2c`.
Only public CA material and dependency instructions entered its build context. Current test binaries
are compiled on the host and mounted read-only. Its image remains available for subsequent disposable
acceptance; no production container/image was changed. Temporary runners are
`/tmp/skill-migration-restore-{systemd,linux}.sh` and `/tmp/skill-restore-live-harness/`; their cleanup
is scoped to their own temporary directory/container. No Docker Sandbox substitution is claimed.

A new full Server quality run is live on original handle **84212** at
`/tmp/skill-migration-restoration-server-quality.log`, after the previous one-line Alembic-head test
correction. Preserve and poll that handle; do not start a parallel coverage run. It has not yet
finished and must not be reported as passed. All other test handles above are terminal.

R48 still needs explicit interrupted/previous-boot repair and Server source-profile reopening.
The existing source restoration only runs within first original execution; it does not reopen the
Server profile or mutate an interrupted task during v1 passive recovery. R46/R49 retain their genuine
Docker Sandbox and dedicated-Linux-Claude-credential gaps. No host login state was copied; no commit,
release, deployment, production capability advertisement, subagent or permission request occurred.
The complete design objective remains active and incomplete.


## 2026-09-26: explicit verification of an already restored source

The preceding continuation implemented exact original rollback permissions. This continuation adds
`account recover-runtime --verify-source` across CLI, Server, neutral Node binding, Worker and Helper.
Default recovery remains version 1 with exactly eleven binding fields and its two-field submission.
Source verification submits `action: "verify_source"` and receives a twelve-field version-2 binding.
Explicit null/empty/unknown actions and version/action mismatches are rejected. Same-key replay,
authorization, lease renewal and successful results retain the exact selected action. CLI source
output uses schema version 2, `source_restoration_confirmed`, and false target confirmation; source
submission errors retain action and unknown confirmation without inventing acceptance.

The new Helper branch only reads existing whole-version-2 failed originals with pre-copy baseline,
immutable failed attestation, original target/source ownership intents, complete copy and all three
successful rollback phases. Every present phase must already be terminal. Repeated full inventory,
exact original source/backup permissions and parent identities/ACLs, syncfs and passive writer
quiescence remain mandatory. Previous-boot verification requires absent current units/cgroups and
unchanged boot. It never refreshes incomplete phases, restores permissions or rewrites original
receipts. The Server keeps the source backend, original failure and account disable; only a fresh
matching success changes the original profile to `rolled_back` and releases its admission gate.
Failed verification remains gated, and old replay cannot affect newer migrations.

Validation so far:

- Previous full Server gate **84212 passed**: 1831 passed, 100 skipped, 82.82% coverage, docstrings
  passed, 1047.52 seconds. This is the pre-action loaded suite, not the current complete gate.
- Source Server tests **10651 passed**: 46 tests including both actions, lease substitution,
  same-key action conflict, disabled account, failed verification and stale result replay.
- Node neutral binding/API/Worker **43385 passed**. The initial real source daemon run found the
  Worker's redundant hardcoded eleven-field result check; it now relies on the strict shared
  versioned binding decoder. Expanded Worker tests **91715 passed** for both actions, including
  action substitution in grants, lease replies and Helper results.
- Full Linux SkillManager/Helper and systemd migration **21406 passed**. An earlier run **40053**
  found a dangling cgroup link treated as absence in the new same-boot source branch; that branch
  now independently lstat-checks group type. All 32 simulated same/previous-boot source cases pass,
  including baseline/attestation/backup/permission/parent tampering, cgroups and cancellation.
  Log `/tmp/skill-migration-source-linux-fixed.log`.
- Real current CLI/Server/production Worker/Helper **68113 passed: 4 tests, 41.03 seconds**. Both
  default target and explicit source actions cover missing backup plus lost acceptance/completion,
  renewed poll attempt, actual daemon restart, exact launch counts and unchanged account/backup.
  Source fixture runs a real failing target ACL followed by original exact restoration. No private
  completion receipt is fabricated. Log `/tmp/skill-migration-source-daemon-fixed.log`.
- Full CLI quality **77466 passed**, including formatting, Clippy and all contracts.
- Final host Node quality **77874 passed**, following the Worker fix. Linux ARM64 vet passed.
  Logs `/tmp/skill-migration-source-{cli-quality,node-quality-final}.log`.

Current live handles (preserve; do not duplicate gates):

- **5739**: full current Server quality, `/tmp/skill-migration-source-server-quality.log`.
- **88135**: actual ARM64 two-kernel source/target proof,
  `/tmp/skill-migration-source-kernel-arm64.log`. The amd64 attempt **91575** ended during the
  foreign-architecture package build with exit 255; no VM ran in that attempt. The ARM64 retry
  builds and executes native-architecture packages before using independent QEMU guest kernels.

The opt-in kernel fixture now retains four originals: completed target, target phases without
whole completion, completed exact source rollback, and fully restored source without final
attestation/whole completion. It expects only the two completed originals to verify after an
external power cut, with all original bytes/metadata and writer counts unchanged. Its old target
phase-only setup was updated to capture the mandatory baseline before any copy and use exclusive
backup directory creation. This is still passive completion verification, not interrupted repair.
The runner `/tmp/skill-migration-source-kernel.sh` uses its own scoped cleanup and host-backed
private disk. Source permission repair for interrupted same/previous-boot originals remains open.
No dedicated Linux Claude credentials have arrived; no host credentials were copied. Genuine Docker
Sandbox acceptance remains unavailable. No commit, release, deployment, production capability
advertisement, subagent or permission request occurred. The overall design goal remains incomplete.


Actual current source/target two-kernel acceptance **16282 passed** after the HTTPS package-build
correction. ARM64 QEMU boot IDs changed from `66ca7edb-6dd6-4760-a107-13ed4b31e534` to
`4ce95248-7d81-4f6a-b0e6-320f4cb0210e` under external power cut. The second kernel accepted only
attested completed target/source originals and rejected target phases and exact restored source
without whole completion. Every recorded account/backup/receipt inventory and original writer count
remained unchanged. Recovery test: **4.98 seconds**. The runner removed its owned VM container,
image, disk and temporary directory. Log `/tmp/skill-migration-source-kernel-https.log`.
This uses synthetic account content and proves Helper/real-kernel behavior, not Claude inference
or Docker Sandbox execution. The earlier ARM64 attempt **88135** failed at package installation;
no VM ran. The repository kernel script now also uses HTTPS with public trust roots and strict
apt index errors, matching the successful runner; shell syntax and whitespace pass.

Final Node host coverage is **63.1%**. Current Linux ARM64 vet passes after the kernel fixture
extension; AMD64 vet/compilation passed before its attempted guest build. Full current Server
quality **5739** remains the only live test handle at this checkpoint. Preserve it.


Next R48 implementation must give interrupted permission repair its own explicit action and durable
intent/completion journal, bound to the original baseline and independent recovery identity. It must
preserve original whole/phase outcomes, including started old-boot records. Direct permission writes
must remain synchronous under Helper lifecycle exclusion, with complete preflight inventory and
fresh lease cancellation. Shared parent ACLs require additional preflight ownership checks: a repair
must not erase unrelated parent ACL changes made by other account operations since the original
baseline. The first-run restorer's parent-identity/owner check alone is insufficient authority to
reuse it after a long interruption. This is a design constraint for the next implementation, not a
newly enabled repair operation. No further question about the pending dedicated credentials is needed.


Full current Server quality **5739 passed and is reaped**: **1846 passed, 100 skipped**,
**83.02% coverage**, **1116.99 seconds**; formatting, lint, mypy, docstrings and whitespace pass.
The expanded opt-in live test's four cases ran separately and passed as recorded above. All test
handles from this continuation are now terminal; no gate or VM remains running. Final four-repository
whitespace checks pass. The source-verification milestone is complete; the overall design goal stays
active and incomplete for interrupted permission repair and the previously recorded real-environment
acceptance gaps. No goal-complete or goal-blocked status was set.


## 2026-09-26: independent interrupted source permission repair

Implemented `account recover-runtime --repair-source` across CLI, Server, neutral Node binding,
Worker and privileged Helper. Submission uses `action: "repair_source"`; binding/output version 3
contains twelve fields. It conflicts with `--verify-source`. Default v1 (eleven fields) and read-only
source verification v2 retain their original contracts. Request key, current authorization, renewal
and successful result pin the selected action. Source repair failure explicitly reports unconfirmed
restoration because cancellation may leave partial permission changes; v1/v2 failure text remains.
Server success preserves original task failure and account disable, keeps the source backend and
marks only the original profile `rolled_back` before releasing its gate.

The Helper requires a whole-v2 started original, durably completed backup, immutable historical
baseline, full content and exact backup permissions. Every present original writer is passively
checked twice without updating its receipt; previous-boot records additionally require absent
current units/cgroups. Shared-parent preflight accepts only unchanged original metadata and exact
original traversal ACL effects. Unrelated user/group/default ACL, xattr, owner, mode and inode
changes block before account writes. Interrupted chmod-before-ACL states require a prior repair
intent or all successful original rollback phases. Actual parent mid-write cancellation and safe
resumption are tested. Each parent observation is rechecked immediately before writing.

Independent private repair intent binds original Server record, source/target, baseline and all
original journal evidence. Attempts bind recovery task/record, poll attempt and boot; immutable
completion pins one successful attempt. Intent permanently fences original metadata writer APIs.
All original whole/phase outcomes remain unchanged, including started old-boot records. Synchronous
anchored permission restoration runs under the existing cancellable Helper lifecycle lock. No new
identity or process writer is created; backup/content/data xattrs stay unchanged. Repeated exact
source/backup/parent verification, syncfs on every participating filesystem, quiescence and stable
boot precede completion. Completed retry only revalidates and cannot begin another permission writer.

Validation:

- Foundational parent guard and private journal full Linux test **50296 passed** and is reaped,
  log `/tmp/skill-migration-repair-journal-linux.log`.
- Full Linux SkillManager/Helper plus actual systemd migration **18109 passed**, log
  `/tmp/skill-migration-repair-executor-linux-fixed.log`. The earlier cancellation test initially
  observed its context only after timeout wrapping; it now exercises the actual synchronous
  writer directly and cancels on its first real chmod, proving pending journal and next-lease resume.
- Expanded actual systemd migration/ACL suite **90332 passed**, log
  `/tmp/skill-migration-repair-directions-linux.log`. Both Native and Docker source permission
  directions reject a live original traversal, restore after its exit, preserve original phase
  metadata and backup, retain launch counts, reject original replay and revalidate completion.
  This also includes actual shared-parent chmod/ACL cancellation/resumption.
- Server focused cases **32229 passed**: 71 passed, 6 skipped. Final action/failure cases
  **42608 passed**: 60 tests. Final Ruff, mypy (653 source files) and docstrings **35031 passed**.
- Full CLI quality **44645 passed**. Final mutual-flag/version-action contract tests **11986 passed**;
  final formatting/Clippy/shell/cache checks **22678 passed**.
- Full Node host quality **25506 passed**, 63.1% coverage, installer/consistency gates passed.
  Linux ARM64 vet passes; a final full Linux ARM64 vet is running after acceptance-only test edits.
- Actual ARM64 two-kernel power-cut **23539 passed**. Boot IDs changed from
  `7b932fb7-a90a-4ad6-81f8-afa886a6cb7c` to `8105202e-5966-47ab-81f8-31d09e4d6386`.
  The original completed source/target proofs still verify; passive recovery still rejects all
  pending originals. Explicit repair then restores three pending sources, including a real target
  traversal process left alive until power loss. All original receipt files, backup and writer
  launch counts remain unchanged; subsequent completed repair is read-only. Recovery: 25.90 seconds.
  Log `/tmp/skill-migration-repair-kernel.log`; owned VM/container/image/disk have been removed.
- Actual current CLI/Server/production-daemon repair **69717 passed**: 2 cases, 22.01 seconds.
  Fault injection kills the real Helper after the first target ACL completes; source permissions
  remain changed until explicit repair. Tests cover exact restored source, original metadata,
  unchanged backup/launch count, missing backup, lost acceptance/completion replies and new poll
  attempt. The original four target/source-verification cases also passed in **54926**, whose two
  repair cases failed in the test harness's writer-exit wait. A retained oneshot service correctly
  remains `active/exited`; the corrected wait checks `SubState`, as production quiescence does.
  The earlier context-only injection did not interrupt the legacy migration client, so the fixture
  now kills the Helper process explicitly. No original receipt is fabricated for these tests.
  Logs `/tmp/skill-migration-repair-daemon{,-fixed,-exited}.log`.

The old reusable dependency image had been removed by a prior temporary daemon runner's cleanup.
It was rebuilt from public dependencies as `agent-remote-migration-repair-proof:20260926`, immutable
ID `sha256:3a3076f27e9e23c5985388f46b9002d9aeb4d8bbfbf97eb1cf0f33946e1075e8`. Temporary borrowed-image
runners now remove only their own containers/directories, retaining this image. No credentials enter
image layers; current binaries are built on the host and mounted read-only. No production Docker
resource is modified and no Docker Sandbox substitution is claimed.

Outstanding at this checkpoint: full Server quality **57467** at
`/tmp/skill-migration-repair-server-quality.log` remains running. It loaded source before the final
v3 failure wording; the final changed service/schema/tests were separately rechecked as above.
The obsolete intermediate daemon retry **44799** is still finishing its old test wait; preserve its
original handle and reap it. Current successful daemon handle **69717** needs reaping. R46/R49 still
require genuine Docker Sandbox and the previously requested dedicated Linux Claude credentials.
No repeat credential question, subagent, commit, release, deployment or capability advertisement.
The overall design objective remains active and incomplete.


All implementation, Linux, kernel and daemon handles above are now terminal and reaped, except
full Server **57467**. Final full Linux ARM64 vet **63516 passed**. Intermediate daemon **44799**
ended with one old exit-wait failure and one pass; final corrected **69717** passes both repair
cases. The integration Go test now has the accurate name `TestRuntimeRecoveryThroughProductionDaemons`;
repository and temporary runner filters match. Final four-repository whitespace checks pass.


Final full Server quality **57467 passed and is reaped**: **1857 passed, 102 skipped**, **82.95%**
coverage, **1210.20 seconds**. Its full run and the final 60-case action/failure rerun together
cover the current service behavior; final formatting, lint, mypy and docstrings also pass.
All test handles from this milestone are terminal. Final four-repository whitespace checks pass.
R48 interrupted source permission repair is implemented and has real systemd, production-daemon and
external kernel power-cut acceptance. R46 and R49 retain the previously recorded genuine Docker
Sandbox and dedicated Linux Claude acceptance gaps, so the overall design is not marked complete.


## 2026-09-26: remaining environment audit, first blocked continuation

The preceding goal turn made substantive progress: R48 implementation and actual systemd, daemon
and cross-kernel acceptance completed. This continuation re-read the design's backend acceptance
and real-tool requirements plus the current requirement audit. No implementation or test remains
running from that milestone; Docker lists no task-owned `agent-remote` container.

Current direct environment evidence: Docker is **29.7.2 (a7dcaa6)**. `docker sandbox version`
returns exit **1** with `"docker sandbox" is deprecated and has been removed.` No `sandbox`,
`docker-sandbox` or `docker-sandboxes` executable is installed on PATH; the installed application
inventory has Docker.app but no separate Sandboxes app. This is an unavailable required backend,
not a passing compatibility probe. No substitute backend was installed or used.

`AGENT_REMOTE_TEST_CLAUDE_CREDENTIALS` is not configured, and no dedicated credential response has
arrived. Only configuration presence was checked; no credential contents or host login state were
read or copied. The existing learning runner explicitly requires a private Linux credential file;
the real discovery assertion still requires exact-session successful Skill invocation evidence.
Runtime-only synthetic tests cannot complete that requirement.

There is no next executable real-environment acceptance action without an external change.
This is the first consecutive blocked continuation after the substantive R48 milestone. Keep the
full goal active; do not mark complete or blocked yet, repeat the credential question, rerun already
passing suites, or invent unrelated implementation work to conceal the acceptance gap.


## 2026-09-26: third consecutive blocked audit

Three consecutive continuations after the completed R48 milestone have verified the same external
blockers. Current `docker sandbox version` still exits 1 with the removal notice; no independent
Sandbox executable is installed. The dedicated Linux Claude credential fixture remains unconfigured,
and no credential response has arrived. No task-owned acceptance container or live test handle remains.
The previous continuation made no progress; this check found no external change or further executable
acceptance action. The full objective therefore meets the blocked threshold and must be marked
`blocked`, not complete. Resume requires the genuine supported Sandbox environment and/or the dedicated
Linux Claude fixture so their respective outstanding acceptance can proceed. Existing implementation,
passing evidence and all original requirements remain preserved. No substitute runtime, copied host
credentials, repeated credential request, commit, deployment or capability advertisement was used.


## 2026-09-27: release authorized; real-environment acceptance deferred

The user explicitly requested release preparation and publication now, with remaining real Linux
and genuine Docker Sandbox acceptance deferred until after release with their assistance. This
supersedes the preceding no-commit/no-release and environment-blocked execution instructions.
No new real-environment acceptance run is part of this release task. Existing evidence remains
historical; skipped or deferred checks are not passing evidence. R46/R49 and actual model discovery
remain pending. Standard repository hooks, unit/contract checks and release supply-chain gates
remain required. Planned independent versions are Node 0.2.29, Server 0.2.27, CLI 0.2.31 and
deployment bundle 0.2.42. Release does not certify completion of the full design acceptance.

### Release execution checkpoint — 2026-09-27

The user subsequently required commits pushed to `main`, publication through each repository's
`prepare-release` Action, and verification that all inter-repository dependencies select the latest
compatible published versions. No direct Node tag push reached origin; the local unpublished tag
was removed before switching to the requested workflow.

Node 0.2.29 was published successfully through prepare run `36294302607` and release run
`36294356971`, at `b835e7d7c976cf541b7707e25e755938af975839`. Its release includes 23 assets.
Unprivileged Linux contract tests now assert rejection of non-root-owned fixtures, while root
success-path coverage remains in the dedicated runtime acceptance runner. Per the user's deferred
acceptance decision, the new Skill copy/config-import/mount/systemd CI runners moved to manually
triggered `skill-runtime-acceptance.yml`. The preceding hosted mount failure (`bwrap: setting up uid
map: Permission denied`) is retained as failed environment evidence. Node main CI `36294568154`
passes; this does not turn deferred real-environment checks into acceptance.

CLI prepare run `36294926738` created 0.2.31, but its release run `36295054044` was cancelled before
publication after Windows CI found platform-specific mutability and main-stack overflow issues.
The tag is preserved. Independent fixes scope Unix directory-builder mutability and heap-pin the
large command futures; a size regression reproduced 150464 bytes before the latter fix and passes
its 128 KiB bound afterward. Final CLI release is planned as 0.2.32, still pinned to Node 0.2.29.
Linux/macOS CI and three-platform installer smoke checks passed before the stack correction; final
Windows and complete release verification remain pending at this checkpoint.

Server source commit `1c24f42` passed its complete pre-commit gate: 1857 passed, 104 skipped,
83.02% coverage in 1375.65 seconds. The first pre-push repeat had a two-second body-wait timeout
and a start-confirmation 409 in short-lease fixtures; its result is not passing evidence. The two
affected modules subsequently passed (37 passed, 5 skipped), and the complete pre-push repeat is
running. No check or production lease validation was bypassed.

Admin Web 0.2.15, Device 0.2.15 and Ego Browser 0.1.19 remain their repositories' latest published
versions and match the unchanged dependency identities. Deployment bundle 0.2.42 remains pending
until final Server and CLI tags, immutable commits and release assets are available. The complete
design acceptance remains unfinished; genuine Sandbox and user-assisted model/runtime acceptance
are deferred, not certified by these release actions.

### Release execution follow-up — Server workflow duration

CLI 0.2.32 prepare `36309090170`, release `36309223703`, and final three-platform CI
`36308835232` all passed. Its immutable source is `0f51c844832cfcaa0d878607b5456dd3e0d1b90e`.
The 29-asset release is published; its macOS ARM64 archive checksum, exact-tag GitHub provenance,
version output and Skill/recovery help passed artifact checks. Node's Linux ARM64 glibc archive
checksum and exact-tag provenance passed, with internal versions Node 0.2.29, Device 0.2.15 and
Ego Browser 0.1.19 matching the pinned composition.

Server `1c24f42c52370223b50fa1cb0985ced1a75a0c29` reached remote main after two further complete
passing gates (1857 passed, 104 skipped, 83.02% coverage). The first upload disconnected after its
passing gate; a later HTTPS push with `Connection: close` and HTTP/1.1 succeeded. No hook was skipped.
Cloud CI `36310470086` and prepare `36310537137` were cancelled by their 15-minute job limit; CI
had reached only 32%. The check annotation explicitly reports `The job has exceeded the maximum
execution time of 15m0s`. A workflow-only follow-up raises both job budgets to 90 minutes while
retaining every test and check. Server 0.2.27 and deployment 0.2.42 are still pending; no complete
Server cloud test result or Server 0.2.27 publication is claimed at this checkpoint.

### Check-duration optimization — 2026-09-27

At the user's request, test speed was optimized without removing tests, lowering coverage gates,
or bypassing hooks. Node commit `3d7da54` reuses Go's content-addressed build cache for real
installer package checks, runs full vet once, and isolates protocol probes from the host Docker
daemon. Its complete pre-push gate took 23.89 seconds and CI `36314643609` passed.
CLI commit `d4368fa` uses pinned nextest 0.9.146 across test binaries with eight isolated processes,
retains Cargo doc tests, and keeps a complete four-thread Cargo fallback. Its full commit gate
passed 608 tests in 108.95 seconds. These are test/CI-only follow-ups to published Node 0.2.29
and CLI 0.2.32; the deployment manifest continues to pin their immutable published tag commits.

The first Server optimization run passed 1860 tests with 104 deferred/unavailable checks skipped,
using four workers and independent SQLite copies of an empty schema. It took 536.94 seconds
for pytest, compared with 1061.90 seconds immediately before optimization. Final validation of
CPU-aware workers (maximum eight) and Python 3.13 system-monitoring coverage is pending.

Final Server optimization commit `5b048cb` passed all 1860 tests (104 skipped) in 232.20 seconds;
the complete hook took 240.32 seconds. Source scope remains 25584 statements and the gate remains
70%. System-monitoring coverage reports 91.48%. A controlled comparison on the same seven HTTP
tests found that the old C tracer misses coroutine continuation lines after SQLAlchemy awaits:
for example, successful content uploads necessarily execute `SkillContentService.begin`'s row
creation and return, but those lines were absent from C-tracer coverage and present with system
monitoring. A separate 12-test direct async service comparison had no extra executed lines under
system monitoring (only one nondeterministic line fewer). The higher percentage is not evidence
of newly added behavior coverage, and is not compared numerically with the old tracer as such.

CLI follow-up `68bacc4` separates child-process startup from the interruption deadline: startup
readiness may wait up to ten seconds under concurrent process load, but Ctrl+C must still exit
within the original three seconds without replaying creation. The complete gate passed again
in 103.72 seconds. The preceding pre-push failure is retained as evidence, not treated as passed.

The final Server pre-push repeat also passed (1860 passed, 104 skipped, 91.48% coverage), with
pytest taking 198.40 seconds and the entire push taking 207.82 seconds. Main now contains
`5b048cbf412eaf20fafaf7ec33105c560b67eb13`; prepare-release `36315594046` is preparing 0.2.27.
CLI main now contains `68bacc4d3b539deaf7c549a003a99d6f76f1dded`; optimized CI `36315366122`
has passed Ubuntu coverage and Windows checks, with macOS still pending at this checkpoint.

Optimized CLI CI `36315366122` completed successfully on Ubuntu, macOS and Windows, and installer
smoke `36315366096` passed. This confirms the runner and interruption changes across all supported
CI platforms; it does not replace the deferred real Skill runtime/model acceptance.

Server prepare `36315594046` completed successfully on four hosted workers: 1858 passed,
106 platform/deferred checks skipped in 499.92 seconds. It created immutable tag 0.2.27 at
`40e9407032de7fe50b32ca1ddd8821c397189172` and dispatched release `36316080787`. The deployment
manifest now selects this exact Server source alongside published Node 0.2.29 and CLI 0.2.32.
