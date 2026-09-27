# Skill manager interleaving audit

This maps every row in design §11.1 to executable evidence and its limits. It is a source-level
coverage audit, not a claim that the complete product or either runtime backend has passed acceptance.
The authoritative overall record remains [implementation status](skill-manager-implementation-status.md).
Requirements outside §11.1 are mapped in the [design-wide audit](skill-manager-requirement-audit.md).

Server transaction tests exercise real persisted models, service transactions, uploads and manifest
reads. Some seed stopped sessions instead of running a tool. CLI contract tests run the actual CLI
against controlled HTTP responses. Node primitive tests and opt-in Linux/systemd/kernel tests each
prove only their stated boundary. These layers cannot be combined into an unexecuted end-to-end claim.

## Design §11.1 mapping

| # | Required interleaving | Concrete evidence | Limit / remaining acceptance |
| --- | --- | --- | --- |
| 1 | Stage r4, pin only A; B keeps r3 | [Staged snapshots](../../agent-remote-server/tests/test_skill_staged_snapshots.py): `test_stage_r4_pin_a_reserves_a_r4_b_r3_and_keeps_tracking` first reserves both accounts on r3, stages r4, pins only A, then prepares and reserves actual A=r4/B=r3 snapshots. It rereads branch identities and actual object bytes, replays snapshot IDs and verifies unchanged default/Git tracking. | Passed on SQLite and PostgreSQL. Real two-account Claude acceptance remains separate. |
| 2 | Default changes from r2 to r3 during session preparation | [Design interleavings](../../agent-remote-server/tests/test_skill_design_interleavings.py): `test_default_revision_change_obeys_snapshot_transaction_boundary`, both before/after cases. It prepares real revisions, reserves snapshots, replays the original and reads the saved branch identity. | Verified Server transaction ordering, not a timing test around a running Claude process. |
| 3 | Reset advances epoch before old resolve arrives | [State commands](../../agent-remote-server/tests/test_skill_state_commands.py): `test_reset_supersedes_old_plan_without_executing_it`; [resolution persistence](../../agent-remote-server/tests/test_skill_resolution_persistence.py): `test_recomputation_after_reset_detaches_whole_input`. | Server coverage includes old choices, replacement detachment and unchanged current directory. |
| 4 | Remove E1, reinstall E2, then old session completes | [Design interleavings](../../agent-remote-server/tests/test_skill_design_interleavings.py): `test_reinstall_then_old_session_completion_never_advances_new_epoch`. | Actual remove/add/reset and late upload/publication preserve E1 data and E2 head. Runtime termination is fixture-supplied. |
| 5 | Disabled skill absent from a session is not a deletion | [Design interleavings](../../agent-remote-server/tests/test_skill_design_interleavings.py): `test_disabled_unexposed_skill_is_not_a_session_deletion`. | Actual account disable, new empty selection and root-file publication leave original learning/head intact. |
| 6 | One of two changed skills conflicts; neither publishes partially | [Design interleavings](../../agent-remote-server/tests/test_skill_design_interleavings.py): `test_conflict_in_one_existing_skill_withholds_both_changes_from_next_session`; [resolution service](../../agent-remote-server/tests/test_skill_resolution_service.py): `test_partial_plan_then_atomic_publish_and_immutable_retry`. | Both existing entries are exposed before concurrent writes; complete incoming files are reread. This does not run two simultaneous tools. |
| 7 | Stop, network loss, concurrent delete/cleanup | [Actual CLI lifecycle](../../agent-remote-server/tests/test_skill_cli_lifecycle_live.py), `upload-unavailable`, and [Helper refusal](../../agent-remote-node/tests/skilllifecycle/cli_retention_linux_test.go): actual pending stop, concurrent individual/bulk CLI deletion refusal with STATE_PENDING, privileged cleanup refusal and unchanged byte/inode/mode/owner/mtime/ctime inventories; upload restoration then publication, daemon restart, inheritance, reclamation and permitted deletion. Job **99651** passed in 133.46 s (`/tmp/skill-cli-retention-outage-verified.log`). | Actual Native HTTP 503 upload-admission outage, not a whole-Node TCP partition. Synthetic tool, not model inference. Intermittent clean-stop classification remains unresolved. |
| 8 | Fully uploaded conflict is persisted but not published | [Design interleavings](../../agent-remote-server/tests/test_skill_design_interleavings.py): `test_conflict_in_one_existing_skill_withholds_both_changes_from_next_session` checks persisted before conflict, retained bytes and unchanged next-session baseline; [Worker transfer](../../agent-remote-node/internal/worker/finalization_transfer_test.go): `TestFinalizationTransferSeparatesPersistenceAndPublication`. | Server/Worker contracts verified separately; actual Claude inheritance loop remains pending. |
| 9 | SIGKILL and reboot produce unclean/detached state | [Node journal](../../agent-remote-node/internal/skillmanager/journal_linux_test.go): `TestUncleanRecoveryCanOnlyPersistAndDetach`; [real kernel proof](../../agent-remote-node/internal/runtimehelper/skill_kernel_reboot_linux_test.go): `TestManagedSkillActualKernelReboot`; [Server publication](../../agent-remote-server/tests/test_skill_publication.py): `test_invalid_write_detaches_entire_submission[unclean]`. | Real ARM64/amd64 power-cut evidence exists in the tracker. It uses synthetic runtime programs/acknowledgements, not the full ordinary Server/Claude path. |
| 10 | Legacy import queued before managed mode | [Server import](../../agent-remote-server/tests/test_skill_config_import.py): `test_queued_legacy_import_is_rejected_by_start_and_fresh_authorization`; [Worker import](../../agent-remote-node/internal/worker/config_import_test.go): `TestQueuedImportRechecksModeAndExactIdentityBeforeBatchWrites`. | Exact current-mode authorization and no partial batch are covered; both layers preserve immutable denial/replay. |
| 11 | GC marks an object while pin/session adds references | [Snapshot GC interleavings](../../agent-remote-server/tests/test_skill_snapshot_gc_interleavings.py) runs real reclamation and exact reservation in both commit orders, checks stale-plan rejection/new snapshot protection and atomic deletion-marker denial. [PostgreSQL race](../../agent-remote-server/tests/test_skill_snapshot_gc_races.py): `test_postgres_snapshot_waits_for_shared_deletion_marker` observes real blocking PIDs and verifies commit rejection versus rollback success. Existing pin and late physical-worker tests remain in [retirement admission](../../agent-remote-server/tests/test_skill_content_retirement_admission.py) and [GC races](../../agent-remote-server/tests/test_skill_content_gc_races.py). | PostgreSQL marker races explicitly inject the marker at its write boundary; actual GC tests operate on unreferenced filtered-tree metadata and protect shared bytes. These are Server proofs; safe Node-local reclamation is separate. |
| 12 | Runtime venv interpreter links | [Native Python adapter](../../agent-remote-node/internal/runtimehelper/skill_python_linux.go) discovers fixed protected system interpreters under the actual session UID. [Mounted venv proof](../../agent-remote-node/internal/runtimehelper/skill_python_mount_linux_test.go): `TestNativeSkillPythonVenvSurvivesCaptureAndNextMountedSession` runs real non-root Bubblewrap, creates a venv, captures only dependency references, materializes a second session and executes its inherited interpreter/module. [Dependency regressions](../../agent-remote-node/internal/runtimehelper/skill_python_linux_test.go) cover changed/missing identity, unsafe files, bounded probes and historical retry/capture. | Native Linux mount/adapter round trip passed with real Python, without manual dependency mapping. Uses a shell test program instead of Claude and direct frozen-object transfer instead of Server publication; full lifecycle and Docker Sandbox remain unverified. Unsupported interpreter paths fail closed. |
| 13 | Session changes A/B; A reset before completion | [Design interleavings](../../agent-remote-server/tests/test_skill_design_interleavings.py): `test_reset_one_of_two_existing_skills_detaches_both_late_changes`. | Real reset, both originally exposed entries, later complete upload/publication, all heads unchanged, both files readable from retained input. |
| 14 | Directory reset before old root auxiliary write | [Design interleavings](../../agent-remote-server/tests/test_skill_design_interleavings.py): `test_directory_reset_prevents_late_root_auxiliary_resurrection`. | Real directory command advances epoch and removes auxiliary data; the late root-only edit is fully retained and detached. |
| 15 | A links to B, then B is disabled | [Design interleavings](../../agent-remote-server/tests/test_skill_design_interleavings.py): `test_disabling_link_target_preserves_history_and_refuses_new_snapshot`. | Real complete publication, disable and new reservation produce `STATE_DEPENDENCY_MISSING`, preserve full history and do not re-enable B. |
| 16 | 0555 source made writable without a real edit | [Permission baseline](../../agent-remote-node/internal/skillmanager/baseline_test.go): `TestPermissionBaselineDoesNotInventSessionEdits`; [capture](../../agent-remote-node/internal/skillmanager/capture_linux_test.go): `TestCapturePreservesSourceModesUntilRuntimeActuallyChangesThem`. | Ordinary-copy/capture identity is verified. The actual tool startup/finalization/inheritance path still needs acceptance. |
| 17 | Session corrupts SKILL.md format | [Node capture](../../agent-remote-node/internal/skillmanager/capture_linux_test.go): `TestCaptureKeepsInvalidSkillEditsRootDataAndDeletions`; [Server publication](../../agent-remote-server/tests/test_skill_publication.py): `test_deleted_or_invalid_known_skill_keeps_its_branch_identity`; [finalization](../../agent-remote-server/tests/test_skill_finalization.py): `test_invalid_format_and_unclean_bytes_are_retained`. | Bytes remain durable and new admission rejects the invalid branch. Full runtime/UI recovery remains part of overall acceptance. |
| 18 | Directory restore after effective revision/member set changes | [Design interleavings](../../agent-remote-server/tests/test_skill_design_interleavings.py): `test_directory_restore_after_revision_switch_rejects_without_changing_rules`; [state commands](../../agent-remote-server/tests/test_skill_state_commands.py): `test_directory_restore_checks_full_identity_set_and_restores_auxiliary`. | Actual changed revision and added-source cases reject with `STATE_SCOPE_MISMATCH`, preserving rules/generation and full directory. |
| 19 | Unbound install is stored; disconnected wait recovers original request | [Library tests](../../agent-remote-server/tests/test_skill_library.py): `test_add_is_atomic_and_replay_does_not_reset_rules`; [CLI mutation](../../agent-remote-cli/tests/skill_mutation_contract.rs): `skill_mutation_lost_reply_recovers_by_key_without_reapplying`; [CLI interruption](../../agent-remote-cli/tests/skill_configuration_interruption_contract.rs): `interrupted_configuration_post_keeps_original_pending_key_and_unknown_commitment`; [CLI status](../../agent-remote-cli/tests/skill_cli_contract.rs): bounded original-operation wait tests. | Real CLI process/HTTP contract and persisted command journal evidence; no single full deployed CLI/Server/Node acceptance claim. |

## First-use evidence outside the matrix

[The reproducible first-use suite](../../agent-remote-server/tests/test_skill_first_use_live.py)
adds ordinary authenticated HTTP acceptance, actual Go task polling, systemd descendant writers,
Helper first fence/capture, original takeover publication, discovery and resolved deployment. Both
normal confirmation and post-commit response loss pass. No task, lease, managed directory or Helper
receipt is seeded. Capability reports remain test inputs. The Worker runs in a root test process,
and application background loops are disabled. This is neither daemon/Claude nor Docker/sbx acceptance.

## Remaining work established by this audit

The matrix now has concrete Server transaction checks for the previously indirect reinstall, disabled
entry, two-existing-entry conflict/reset, root reset, snapshot revision timing, linked disable and
changed-version directory restore combinations. The nine cases in `test_skill_design_interleavings.py`
read saved identities and retained bytes; they do not mirror production helper internals.

Still required for the complete design:

- Full ordinary CLI/Server/unprivileged Worker/Helper/systemd/Claude session lifecycle, including
  finalization and a subsequent real session reading inherited edits/deletions/binary content.
- Backend dependency probing/restoration and Docker/sbx whole-writer lifecycle; containers alone
  cannot certify Docker Sandbox support.
- Interrupted account migration recovery with verified rollback and retained source authority.
- Frozen Native Node-only directory export is now implemented and checked with real authenticated
  Server HTTP, Go streams, an SSH process double for the CLI, and Linux Helper/nonroot descriptors.
  Recovery after local copy reserve rejection/runtime quota overflow now uses a separately guarded
  stopped-work stream, with actual nonroot Helper access and simulated original unit evidence.
  A separate 16 MiB tmpfs proof covers physical ENOSPC before termination retention: a recorded
  original invocation plus passive quiescence permits unclean read-only recovery. Real CLI/HTTP/SSH
  acceptance now covers both frozen data and actual configured runtime-quota overflow after daemon
  restart, including mid-transfer key revocation, complete byte/metadata checks and no partial
  publication (`test_skill_ssh_export_live.py`, 2026-09-25). Missing both forms of original evidence,
  content above fixed export bounds and real model/Docker lifecycle remain open.
- Reference-aware Node-local reclamation and coordinated database/content/Node restore validation.
- The complete audit of commands/requirements outside §11.1 and the remaining real runtime
  combinations noted above. Staged two-account and GC-versus-snapshot Server tests now have direct
  SQLite/PostgreSQL evidence.

No capability advertisement or release approval follows from this document.

## Node-local reclamation groundwork (2026-09-25)

[Server authorization](../../agent-remote-server/tests/test_skill_node_reclamation.py) verifies
complete original physical content again before permitting a fresh local decision, including
11 MiB last-byte corruption and mismatched restored content with readable historical receipts.
[PostgreSQL ordering](../../agent-remote-server/tests/test_skill_node_reclamation_races.py) uses
independent connections and actual blocking PIDs to prove the shared storage lock survives full
verification and cancellation; it does not run physical GC deletion.

[Linux journal regressions](../../agent-remote-node/internal/skillmanager/reclamation_journal_linux_test.go)
exercise immutable intent, changed/uncaptured work protection, safe private records, modeled partial
removal and reopen, preserved metadata, explicit transfer denial and replacement-root rejection.
[Helper inventory](../../agent-remote-node/internal/runtimehelper/finalization_inventory_linux_test.go)
passes pending/completed/corrupt states through the actual private socket.
[Worker handling](../../agent-remote-node/internal/worker/finalization_reconciliation_test.go) avoids
recapture/upload; admission tests retire only the original nonce. Actual local deletion, independent
runtime/mount/reference proof and its interleavings remain unimplemented. These tests cannot be used
to close row 11's local-reclamation limitation or coordinated-restore acceptance.

The subsequent [Linux executor tests](../../agent-remote-node/internal/skillmanager/reclamation_delete_linux_test.go)
now perform actual content removal and interrupt it between file/root phases, then reopen and resume
the original intent. They also refuse changed/new bytes, substituted roots, private-object hardlinks,
nested links and real same-inode bind mounts. The reproducible opted-in runner is
[linux_skill_reclamation_test.sh](../../agent-remote-node/tests/linux_skill_reclamation_test.sh).
This improves the earlier modeled-deletion evidence; the caller's writer/reference proof remains a
test callback, so Helper/Worker orchestration and active export lifetimes remain unverified.

[Read lifetime tests](../../agent-remote-node/internal/skillmanager/finalization_hold_linux_test.go)
now block marking for shared manifest readers and block all deletion for an outstanding raw object
reader. [Helper descriptor tests](../../agent-remote-node/internal/runtimehelper/finalization_hold_linux_test.go)
retain SCM_RIGHTS descriptors across original/replacement server shutdown and check exact final-reader
release. Worker transfer and gateway export hold that reference throughout their operation and test
failure/revocation cleanup. The production runtime/mount/reference proof and scheduling remain open;
these locks close the previously missing active-transfer lifetime boundary only.

The [private Helper coordinator tests](../../agent-remote-node/internal/runtimehelper/finalization_reclamation_linux_test.go)
now apply original ready-spec/launch authority and passive runtime/network/cgroup proof around actual
marking/deletion. They preserve reappearing resources, missing/changed authority and active readers,
cancel lifecycle-lock waits, and resume interrupted actual deletion without renewed authorization.
[Real mount tests](../../agent-remote-node/internal/runtimehelper/finalization_reclamation_mount_linux_test.go)
reject work/object/file/bundle aliases and same-inode mounts. These use controlled systemctl/ip and
authorization fixtures; they do not establish a Helper socket challenge/deadline exchange, Worker
scheduling, deployed systemd lifecycle or coordinated restore. Those acceptance gaps remain open.

[Socket tests](../../agent-remote-node/internal/runtimehelper/finalization_reclamation_socket_linux_test.go)
now combine credential-checked Unix sockets, authenticated HTTP fixtures and actual deletion. First
marking charges challenge transmission, HTTP and response IPC against one Helper-process monotonic
budget; virtual-clock tests reject exact expiry and a replayed challenge. An unread completion reply
recovers on a replacement Helper without renewing authority. Nonroot child tests allow UID 65534 and
deny UID 65533 without private-store access. Cancellation joins the reader and releases lifecycle
exclusion, including when authorization is outstanding.

[Worker ordering tests](../../agent-remote-node/internal/worker/finalization_reclamation_test.go) now
exercise scheduled first reclamation only after upload holds close and terminal cleanup completes,
and resume pending intent without transfer or another HTTP call. The production page loop invokes
these paths and preserves uncertain/legacy/conflicted input. This closes the earlier missing protocol
and scheduling implementation, but controlled service/HTTP fixtures still do not prove the complete
deployed CLI/Server/Worker/systemd/Claude lifecycle or coordinated restore.
# Generic reconciliation racing managed launch and exit

The production daemon acceptance exposed this sequence: ordinary session admission commits a
`starting` session and exact snapshot; the independent Worker reconciliation loop reports a list
observed before the create task launches; the legacy Server path marks the session interrupted;
the original task then loses preparation authorization. The same path could turn a clean natural
exit into an interrupted session before the dedicated termination confirmation arrived.

Server generic reconciliation now selects only legacy active sessions without any persisted snapshot
for the stable session reference. It cannot revoke managed connections, enqueue legacy cleanup or
advance retention clocks based on a missing/inactive list entry. Current task marker damage cannot
remove this guard. Dedicated original-bound start/termination/stop protocols retain authority.

`tests/test_skill_generic_reconciliation.py` covers empty-list-before-start acceptance and all
starting/running/active × missing/inactive/process-exited observations, followed by clean exact
termination, plus a removed task marker. All 11 cases failed before the fix and pass afterward.
The retention-clock regression now verifies that generic reconciliation preserves the active managed
history root. Legacy session reconciliation tests still pass. Actual Node/Helper daemon verification
with real credential-free Claude `--version` completed clean publication and local reclamation;
real learning/inheritance, CLI/SSH and backend-wide concurrency certification are still separate.

## Failed backend rollback followed by replay or takeover

Target ownership can fail after the backup succeeds, followed by a rollback command that exits
nonzero with an empty cgroup. Writer termination alone does not mean source ownership was restored.
New Helper execution now retains started migration state for every rollback error, including source
identity failure, instead of emitting a terminal failed receipt. Replay cannot repeat ownership or
copy; a replacement task cannot bypass the retained intent. Historical terminal failures continue
to describe writer termination only and are not upgraded to verified rollback authority.

[Systemd migration tests](../../agent-remote-node/internal/runtimehelper/account_migration_systemd_linux_test.go)
reproduced all three ACL rollback failure phases before the fix. Seven subcases now pass, including
source-UID access after successful rollback and retained backup/replacement denial after failure.
Interrupted-migration recovery, historical source validation and Docker Sandbox lifecycle remain
separate requirements; no automatic recovery or new backend capability is enabled.

## Incomplete backend migration followed by a new legacy writer

An interrupted migration can retain a live ACL service after the original Helper request returns.
Previously its local started intent prevented only a replacement migration/takeover. Ordinary legacy
binding/session admission and config imports could still mutate the account. Server failure handling
also restored the prior active status, and replaying an old migration result could alter a later
migration profile. These paths undermined the exclusive source needed for eventual recovery.

Helper now checks local migration/copy history at each new legacy writer boundary and keeps exact
completed replay read-only. The actual systemd cancellation test proves the gate while its original
ACL service remains live. Linux tests cover four incomplete evidence phases across binding, session,
backend and import entry points after Helper replacement, including unrelated-account usability.

Server writer admission and original-result validation share the user content lock and refresh
cached account/profile/task state. Failure records recovery_required and cannot reopen source writes;
editing account.status cannot bypass the profile. Exact terminal replay is read-only even after a
later migration, conflicting results are rejected before mutation, and intervening disable survives.
Nine HTTP regressions failed before this fix; the final focused set includes eleven new cases.
Two actual PostgreSQL tests observe blocking PIDs and verify commit-denial versus rollback-admission
with stale ORM profile state. The separate passive recovery command described below can now settle
completed target work; source permission attestation and automatic resume remain unavailable. See the Server `docs/skill-backend-migration-recovery.md` for these boundaries.

## Restore of a partially resolved publication followed by new Node preparation

The coordinated archive test backs up a stopped SQL/content fixture while its two-path conflict has
one saved choice. It drops source SQL and moves source content aside, restores new targets, and
compares every business row and every content file/mode before allowing target mutations. Nonempty
snapshot, finalization, local-state, rule, deployment and resolution tables prevent vacuous comparisons.
The saved idempotency key still returns its original partial plan; a second explicit choice completes
publication. Unclean detached input stays detached and a previously deleted file stays absent.

A fixture replacement Node obtains a newly created/leased snapshot through actual services and receives
only individually authorized content; the old Node is denied. A separate networkless Linux container
materializes the download without access to either Server volume or old Node state and verifies
ownership, independent copies, exact binary/text bytes and source permission restoration. This tests
service continuity after coordinated SQL/content restoration. It does not resolve concurrent live
backup writers, automatic Node failover, restoration of an old pending runtime journal, or backend
migration recovery; operational backup still requires stopping all writers as the runbook specifies.

## Cancelled backend writer followed by replacement Helper observation

New copy/ACL phases persist a unique launch description before starting a root transient systemd
service, then durably pin its invocation. Exited services remain available until terminal evidence
has been saved after whole-cgroup checks. A replacement Engine may observe the original live service
and its later natural exit; an existing intent cannot cause another launch. Missing/foreign or
previous-boot runtime evidence remains pending. Same-name services with different invocation/description
cannot be adopted or stopped by historical cleanup. Actual systemd acceptance verifies survival after
cancellation, one execution, same-invocation convergence and protection of a distinct replacement.

New whole-migration completion requires its matching-version copy and phase proofs; a parent receipt
alone cannot hide missing or pending phase evidence. Inventory also detects orphaned writer records.
Historical receipts preserve their older meaning and do not certify rollback or new recovery authority.

The review exposed a generic result-cache bypass at public Helper dispatch. Five cases reproduced it.
`migrate_account` now always checks typed original migration evidence; an old cache without that evidence
cannot report success or restart copy/ownership work. A user-authorized recovery command and source
permission attestation remain separate unfinished work; current Server recovery gates stay closed.

## Completed backend phases before the whole result, and rollback before its first ACL

Exact original Helper dispatch can now finish same-boot writer-version-2 metadata from original
complete phase evidence. Recovery passively observes the same services, requires empty cgroups,
synchronizes both filesystems and repeats phase/quiescence checks before the whole result. Missing
steps never run implicitly. Completed rollback remains failed, not source-readiness authority.

A real systemd prefix test first exposed false target-success inference after direct rollback
ownership changed but the first rollback ACL never started. The fix adds a durable ownership intent
before either direction's identity lookup or Lchown. A rollback intent without ACL records is already
incomplete rollback. Target success cannot ignore it. ACL phase creation, final outcomes and local
inventory require matching ownership/copy/migration authority, including orphan protection. Old
pending version-0/1 evidence cannot support this new inference; old terminal receipts remain immutable.

Five real execution-prefix cases now verify no repeated launcher calls and retained original backup
bytes, including an active final ACL which becomes recoverable only after natural exit. These are
component tests using replacement Engine instances; full daemon recovery and a separate authorized
Server task after terminal failure remain unfinished.


Explicit backend completion recovery now uses a separate administrator-authorized task and exact
original binding rather than overwriting a failed task result. Real PostgreSQL tests observe
same-key/different-key contention and fresh profile reads after user-lock waits. HTTP tests reject
expired/replaced authority and preserve later migration state on historical replay. Real systemd
completion recovery repeats no writer and retains backup bytes. This closes the passive completed
original-task control-plane gap only; interrupted writes, source permission proof, prior-boot
migration recovery and a deployed CLI/Server/daemon run remain separate acceptance work.

## Capture failure after durable writer termination

Process stop and complete frozen content now have separate evidence. A failed capture cannot invent
an incoming digest or local durability. Helper requires fresh original quiescence and the private
termination record before emitting one finite pending cause. Existing corrupt capture state never
falls back to a pending proof or stopped-work export. Explicit stop reconciles after capture errors;
background reporting keeps the original work without creating transfer/cleanup authority.

The existing Server user/session/task locks serialize pending and frozen observations. Original
classification is immutable; only the first full capture can fill a previously absent digest. A late
pending request cannot erase frozen evidence. Real PostgreSQL races verify both matching and
conflicting classifications. A null-digest stop result confirms process exit only and replays after
subsequent frozen upgrade; current saving status remains independently queried. Export authorization
may know classification before digest, but rechecks cannot forget either already-known fact.

Real SSH quota acceptance observes capture_pending before exporting complete stopped work, then
revokes the SSH key during a second transfer. No published/staging bundle survives that failure and
original Node bytes remain unchanged. CLI bounded waiting ends with an actionable export instruction;
unknown cause strings are rejected without echoing diagnostics. These checks do not establish model
learning, Docker support, or recovery above the export protocol's fixed bounds.

## CLI launch, graceful stop, restart and inheritance

The complete synthetic Native CLI flow now runs current agent-remote/fclaude with official Mutagen,
real workspace synchronization, registered temporary device/SSH identity and forced-command SSH.
The test installs the source through CLI, reads account-effective selection, writes changed instructions
and arbitrary state in the running session, then requires the original stop operation to publish.
Both shipped daemons restart before another independent session verifies inherited binary bytes,
permissions, deletion, empty directories, a relative link, account-local content and directory aliases.
The Node verifier observes reclamation for both snapshots; deleting the first display session leaves
its original saving operation queryable as published/deleted. No lifecycle result is fabricated.

This revealed a launcher parsing defect: global options before `stop` selected default run/attach.
The regression reproduced Run instead of Stop before the fix. Explicit subcommands now take
precedence while direct model flags, prompt words and `--`-delimited command names retain passthrough
semantics. The acceptance also rejected the original signal-only synthetic shutdown as unclean;
the final tool consumes the ordinary terminal shutdown request and exits zero before capture.

The final lifecycle test passed; both pre-existing real SSH export cases passed after the shared
runner changes. This closes the synthetic CLI/SSH/sync/daemon lifecycle acceptance gap, not real
Claude inference, real account enrollment, production capability readiness or Docker Sandbox support.

## Default-size capture outlives the generic Helper deadline

A real 100,000-file capture through the ordinary Helper socket failed at the former 30-second
operation boundary. Retrying would restart the expensive uncommitted capture. Both observation and
admission-loss draining now allow one 15-minute budget with earlier caller deadlines and disconnect
cancellation preserved. The unchanged scale passed in 141.344 seconds of socket reconciliation;
all original manifest paths/sizes/digests were compared. Explicit cancellation and shorter-deadline
lock-wait tests cover both operations, including under the race detector. Runtime/systemctl exit
proof in this specific capacity fixture is simulated; it does not replace the independent real
systemd lifecycle acceptance.

Separate actual filesystem cases passed one 1 GiB skill, ten distinct 1 GiB skills (10 GiB total),
and 100,000 unique objects with ordinary copying, frozen objects, complete byte hashing and reopened
journal replay. Per-operation buffer reuse reduced materialization allocations by about 86% without
removing fsync or content/permission checks. These are capacity-component results, not whole-product
HTTP/SSH transfer or Server quota acceptance. Per-object Helper manifest revalidation and full
100,000-object transport remain to be measured and addressed.

## Frozen-object transfer validation scales with one pinned manifest

The scoped Helper reader removes complete session/manifest revalidation from each object request.
The original manifest and capture are validated once per bounded connection; each descriptor request
still verifies membership, binding, tree identity, clean/unclean classification and private anchor
metadata. The manifest read lock transfers to the client, so Helper shutdown does not let reclamation
race outstanding consumption. Cancellation/deadlines while waiting for the lifecycle lock or a
blocked object reply release the connection and owned descriptors. Malformed ancillary/JSON frames
are rejected without descriptor leaks. Actual Linux corruption, lock and shutdown tests pass; focused
Linux reader/transfer tests and the export package pass the race detector.

A real 100,000-unique-object Helper run passed with full byte hashing in 31.298 seconds for the object
loop, after 88.556 seconds of capture (126.91 seconds including setup). This closes the per-object
Helper scalability item noted above. It does not close 100,000-object HTTP/SSH transport or Server
quota acceptance. Both ordinary real SSH export cases passed after correcting a fixture race:
Type=simple startup can return before the daemon execs with its configured UID, so the fixture now
waits for the expected executable and complete UID tuple.

## Indexed upload admission, complete retention and reader rotation

Server single-file admission now uses a durable declaration projection instead of rebuilding the
whole manifest. User locks serialize initial index publication and legacy backfill; composite foreign
keys bind every row to the exact owner/upload/tree/scope. Completion rechecks the original canonical
digest and every content byte. Expired and superseded attempts cannot gain authority through an index.
The real PostgreSQL regression covers concurrent backfill, rollback, owner isolation, malformed
entries, migration/downgrade, quota release, shared-category deletion barriers and complete graph/GC
forecasts. All 89 selected cases passed in `/tmp/skill-upload-index-postgres-gc-final.log`.

Actual 100,000-object HTTP acceptance initially failed before file transfer because the old retention
metadata guard counted the entire 20+ MiB upload manifest against 16 MiB. Indexed retention now reads
only counted digest references and checks missing/extra rows, while preserving JSON and row budgets.
Both retention graphs and GC forecasts share that interpretation; zero-byte reservations still
protect original files. Full Server gate and the corrected complete network-capacity run remain in
progress, so this is not yet final default-limit transfer acceptance.

The measured network cost also exceeds one Helper reader lifetime. Worker now rotates exact-input
readers between files after ten minutes, acquiring the next hold before closing the old one. Focused
race tests cover 31 minutes of simulated transfer time, an individual file interval longer than the
reader lifetime, unavailable replacement, cancellation and closure. Node's complete quality gate and
Linux Worker vet passed. Actual combined Worker/Helper/Server default-limit transfer remains required.

## 2026-09-26 — normalized download membership and complete-tree barriers

File download authorization now queries the existing owner/category/tree/object reference relation
and registered immutable object metadata under the same user lock as GC. The entire requested tree
is checked against unavailable objects in both categories, using migration 0055's partial index.
GC still removes references and parent tree atomically; a request cannot observe a partially retired
normal transaction. Exact Node/task/session/attempt/lease checks and post-copy reauthorization remain.
No global authorization cache or target-file-only deletion check was introduced.

Focused regressions: 110 passed / one PostgreSQL-only skip. Real PostgreSQL regression/migration:
172 passed, including cross-category admission, exact bindings, lease/copy revocation and GC races.
Large download acceptance remains live. A real CLI lifecycle attempt again observed the existing
unclean/detached stop (`/tmp/skill-tree-download-cli-lifecycle.log`); the synchronized `stop-byte`
file contained exactly `3`. That proves the synthetic tool received the intended interrupt, but
neither identifies the incorrect/abnormal exit observation nor proves the complete lifecycle.
The failure remains unresolved and is not replaced by a small passing download test.
