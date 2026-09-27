# Skill manager wire contract v1

This is the implementation-level contract for the reviewed user skill manager.

## Tree manifest

JSON has `version: 1` and `entries`, a list sorted by UTF-8 path bytes. Every entry has exactly
these fields: `path`, `kind`, `mode`, `size`, `sha256`, `target`, `content_kind`, `dependency`.
Unknown fields are rejected. `kind` is `file`, `directory`, `symlink`, or `runtime_link`.
Canonical output includes every field. On input, version defaults to 1, entries to an empty array,
mode to 420 and size to zero; the other metadata strings default to empty. Path and kind are
required. Explicit null values are never defaults. Total expanded size cannot exceed signed int64.

- Paths are NFC UTF-8 relative POSIX paths, with no empty/dot/dot-dot components, backslashes,
  control characters, or surrogates. Components are at most 255 bytes; paths at most 4096 bytes.
  Every parent is an explicit directory entry. The implicit manifest root is not an entry.
- Mode is an integer from 0 through 511, excluding special ownership bits. Symlink modes are 511.
- A file has nonnegative size, lowercase SHA-256, and `content_kind` of `text` or `binary`.
  Text means the complete file is valid UTF-8 with no NUL bytes. Content validation rechecks it.
- Other entries have size zero, empty SHA-256 and empty content_kind. Directories have empty
  target and dependency. Ordinary files also have empty target and dependency.
- Symlinks have a nonempty relative target resolving inside the complete manifest. Parent
  traversal in the target is allowed only when resolution stays inside the tree. Dangling links,
  link-resolution cycles and descendants beneath non-directory entries are rejected.
- Runtime links have an absolute target and a nonempty dependency identifier. Structural
  validation never grants filesystem authority: the target must additionally match the selected
  runtime adapter's independently validated dependency mapping before materialization.
  The Native Python adapter now discovers fixed protected system interpreter paths and binds
  CPython major/minor, ABI flags, byte order, Linux architecture and exact path in that identifier.
  See [runtime dependency behavior](../../agent-remote-node/docs/skill-runtime-dependencies.md).
  Historical generic identifiers are not automatically promoted to verified capabilities.
- Runtime copies add owner read/write access (and directory search) as needed; the immutable
  manifest still records the source mode. This never makes immutable packages writable.

The tree SHA-256 hashes `agent-remote-skill-tree-v1` followed by a NUL byte, then each entry's
eight fields in the order above, each UTF-8 encoded and followed by NUL. `mode` and `size`
are canonical unsigned decimal strings. Sorting and all fields, including permission, text/binary
classification and dependency identity, are covered. File bytes are separately addressed by their
SHA-256. Object ownership is authorized independently of knowing either digest.

All numbers reject booleans, fractional values and numeric strings. Entry count and expanded
byte quotas are checked independently of transport size. Uploads verify bytes before references
can be published. Runtime state limits and immutable package limits remain separate.

## Merge and rule resolution

Rules resolve enabled and revision independently: account, then tool, then user default.
Eligibility and an installation tombstone are separate from enabled. Inherit is absence of an
override, not a hardcoded default. A revision always belongs to the selected skill and owner.

Merging compares validated manifests by path, entry type, mode and content identity. A fast
forward or identical result succeeds. Distinct changes to the same path, invalid resulting tree,
or divergent opaque state yield conflicts and no publishable partial result. Binary changes and
recognized database sidecars conservatively group the entire skill. Services additionally enforce
the directory-wide transaction, exact starting manifest and generation/epoch preconditions.

Implementations in Python, Go and Rust must share golden vectors for the canonical digest;
none may use its language's default JSON serialization as the tree identity.

## Runtime directory scope

An immutable installation manifest is self-contained within the selected skill. Runtime captures
use a complete account discovery-directory manifest, excluding managed system entries. A runtime
checkpoint may reference that manifest's digest and a subtree prefix; such a view is not itself
a standalone manifest. Authorize the full directory by account before resolving any link. Relative
links between skills and root auxiliary data are validated in this complete manifest. Revalidate
the final assembled tree at session preparation; a disabled or otherwise absent target yields
`STATE_DEPENDENCY_MISSING`, never implicit enablement. Export must use account-directory scope
when a subtree alone would contain dangling links. Linked entries form a common merge unit;
opaque changes in that unit must not be split across independently published skill trees.

Snapshots retain both source modes and actual materialized modes. Capture compares final modes
with the actual starting modes; unchanged modes preserve source metadata. Actual chmod changes
and newly created entries retain their ordinary permission bits. This prevents writable-copy
normalization alone from becoming an account change.

Directory publication checks the directory epoch and all changed branch epochs. If any changed
branch has lost publication eligibility, the entire submission is detached. Ordinary head movement
without an epoch change permits a fresh merge and CAS retry. A directory reset/restore advances
the directory epoch as well as affected branch epochs. Superseded conflict plans retain their full
input snapshots. These checks are service responsibilities; pure manifest validation and merging
alone do not establish publication eligibility or runtime isolation.


## Node local durable bundle format

The implementation currently has private Linux primitives for a prepared bundle with `work/`,
`baseline.json` and a sealed `snapshot.json`. The baseline stores source and actual materialized
manifests. The sealed record binds user/account/node/session/snapshot IDs, directory epoch,
library generation, initial tree digest, resource limits, system exclusions and independently
validated adapter dependency paths. It is written before launch and must not be runtime-writable.

After the backend proves all writers exited, capture hashes/fsyncs the full directory. A temporary
finalization directory receives independent private `objects/{sha256}` files, `manifest.json` and
`record.json`; fsync and no-replace rename publish the whole frozen input. The parent directory is
then fsynced. `objects_version=1` records that ordinary file contents are retained independently of
the work directory, with each distinct digest copied once as helper-owned 0600 data. Links remain
manifest metadata and are never followed into external content. The configured disk reserve applies
before copying. The complete work tree is checked again before publication. Retries reuse that journal even
if the transient runtime spec is gone. Manifest corruption or binding drift fails closed. The
journal's tree digest always identifies the complete captured input, including conflicted/detached
input, rather than claiming it equals a later merged account head.

Older records without `objects_version` retain version 0. Only the quiescent finalizer upgrades them:
it copies exactly the saved manifest bytes, atomically publishes objects, verifies the complete set,
then durably advances the marker. A crash between object publication and marker publication resumes
verification, including when work has since disappeared. Missing/changed work or corrupt existing
objects remain errors; neither recapture nor changed clean/unclean classification is permitted.
Read-only transfer cannot perform this upgrade.

`open_skill_finalization_file` is a dedicated authenticated Helper socket operation. Its payload has
exactly `binding`, `kind`, `digest`, `tree_digest` and `unclean`. Binding is the complete original
snapshot owner/epoch/preparation identity. A manifest request uses kind=`manifest`, empty digests and
null unclean; an object request uses kind=`object`, the saved complete tree digest, the exact declared
file digest and a strict original clean/unclean boolean. The retained runtime must be Native and have
the canonical original unit identity. This operation never reads work, launches/stops writers, changes
the journal or grants cleanup.

Success returns protocol version 1 with exactly one SCM_RIGHTS O_RDONLY ordinary file descriptor and
`result={record,kind,size,entry}`. `record` is the original typed finalization; `entry` is null for a
manifest and its exact original file entry for an object. Files must be root-owned 0600, singly linked,
the declared size and marked CLOEXEC on receipt. The client verifies the full manifest digest; object
upload must independently verify streamed bytes. Metadata is capped at 32 KiB, manifests at 64 MiB.
Missing/extra/aliased/duplicate/null required fields, multiple/writable/unsafe descriptors and truncated
ancillary frames fail closed and close all received descriptors. The handler has a 30-second bound,
disconnect-cancellable lock wait and five-second descriptor ACK deadline. The one-byte ACK confirms
descriptor receipt only, never Server persistence or permission to remove content.

`list_skill_finalizations` is a separate read-only Helper operation with exactly
`payload={node_id,cursor}`. Node identity must match the configured Helper; cursor is empty or a
canonical original session UUID. `result={items,next_cursor,invalid_names}` contains at most 16
ascending session candidates. Each item has exactly `session_id`, nullable `record`, and `code`.
A present record includes the complete original binding; otherwise code is `not_finalized`,
`invalid_retained_state` or `unsupported_backend`. Corrupt metadata inside an existing bundle does
not count as an absent finalization. Malformed session names set the aggregate flag without exposing
paths. Directory enumeration uses bounded memory and cancellation, never creates a store, upgrades a
journal, accesses work or needs transient specs. A verified absent store is an empty page; unsafe
existing paths fail. Nonempty continuation is the last returned UUID and requires a full page.
Each new pass discovers earlier newly inserted IDs. The handler is bounded to 30 seconds and cancels
on disconnect, including during mutation-lock wait. Generations remain exact signed 64-bit integers.

`reconcile_skill_session` is a separate mutating Helper operation with exactly
`payload={node_id,session_id}` and `result={session_id,state,record}`. `record` is explicitly null
for `not_started` or `running`, and the complete original frozen record for `finalized`.
The configured Node and canonical session select an existing private bundle; caller paths, launch
inputs and broker credentials are forbidden. Existing captures replay unchanged without needing a
runtime spec. A genuinely absent launch intent returns not_started; incomplete/corrupt private
authority returns `FINALIZATION_PENDING`. A same-boot starting launch with a loaded unit must
first prove original private spec authority, valid invocation/transient/user/cgroup identity and a
stable repeated observation. Running units also require original published spec bytes and mount;
exited units require whole-cgroup quiescence and unchanged-or-absent transient spec bytes.
An additive `observed` phase pins that invocation in the schema-1 launch record without readiness.
Only separate leased recovery can verify readiness and promote the same invocation to started.
Absent starting units require repeated absence and cgroup quiescence before unclean capture.
For a started or invocation-observed same-boot launch, the Helper binds the original ready draft and preparation digest to
the retained runtime, then reads current systemd state, invocation, transient identity, user and
cgroup together. A running original unit must still have its original spec files and verified work
mount. This is an observation, never broker admission or a Server startup acknowledgement.
Natural exit requires a stable repeated unit observation and empty whole cgroup before releasing
the exited original service. It then checks stopped state and cgroup emptiness again before freezing.
It cannot stop a running/populated/replacement unit or relaunch. A successful original exit is clean;
failed or missing units are unclean. Original termination receipts preserve classification on retry.
The handler owns a 30-second cancellation scope, disconnect reader and cancellable mutation lock;
the client preserves integer generations and validates exact response fields and original identity.

`drain_unadmitted_skill_session` uses the same exact Node/session request and observation response,
but permits draining a proven original running Native invocation when its retained spec enabled
ego-browser. The authenticated local worker asserts loss of its process-local grant; this assertion
is not cryptographic broker evidence. The Helper independently loads the original private launch,
draft and preparation, requires the same boot and started/observed invocation, and rechecks invocation,
transient unit identity, user and cgroup throughout graceful exit and final stop. Replaced units,
unknown state and surviving writers remain pending. The common finalizer preserves original
clean/unclean evidence and frozen replay. Browser-disabled runtimes remain running after the usual
spec/mount checks. No broker nonce, replacement launch, caller-selected unit or host path is accepted.
This operation shares reconciliation's cancellation, serialization and bounded error envelope.

The worker serializes managed startup and background admission inspection through one cancellable
process-owned gate. Only its successful initial admission records the original session/nonce/UID;
recovery and historical Server receipts cannot populate this map. Running observations verify that
exact original grant against the current broker. Missing/revoked/changed grants invoke the separate
drain operation; registering or even granting a different nonce cannot adopt the old runtime. Frozen
or not-started observations retire only the matching local grant. The map and nonces are never persisted; a new
Worker starts empty. This handles started and independently observed same-boot launches.
Common managed stop paths also discover original private authority and pin the same invocation
throughout stop, including cancellation, failed-launch cleanup and missing transient specs. A loaded
unit cannot be stopped using an absent-launch intent or an earlier absent-unit observation.

Previous-boot Native bundles now use the separate passive proof documented in Node's
`docs/skill-runtime-recovery.md`, without changing either observation wire shape. A valid current
kernel boot must differ from the immutable prepared boot. The original private ready spec/draft
remains required, including when preparation preceded the launch intent; absent/starting/observed/started
launches may recover, while existing corrupt launch metadata cannot mean absent. Two observations
must prove absent systemd unit (not merely inactive), absent canonical cgroup directory, absent
network namespace, unchanged-or-missing transient spec and no runtime/work mounts or filesystem
aliases. Kernel mount paths are decoded and inventories bounded; unknown observations fail closed.
No stop/kill, network deletion, unmount or relaunch is permitted for previous-boot resources.
The common finalizer marks new input unclean, preserving any earlier immutable termination or
capture. Manual stop and cleanup_resources use the same recovery before transient artifact loading.

Acknowledged terminal captures permit previous-boot transient cleanup only after the same passive
proof and private authority checks. Removal is parent-synced before the existing completion receipt;
interrupted removal can resume with missing transient spec. Completed replay refuses reappearing
roots and resources. Work/frozen content remain retained. Existing upload/publish/acknowledgement
contracts are unchanged. Controlled earlier-boot metadata and real mount tests establish these
branches; actual kernel reboot and complete real Worker/Server/Claude acceptance remain required.

The Native worker's independent background loop processes one inventory page per iteration,
reconciles not_finalized candidates through that separate operation, and transfers new captures. It
never sends a partial page as a complete Server runtime_sessions snapshot. The loop
continues past individual errors. Its separate `<ledger_path>.skill-finalizations` ledger stores
schema 1 original capture, nullable exact finalization receipt and nullable exact publication receipt,
keyed by snapshot UUID. Original input precedes HTTP begin; `skill-finalization:<snapshot UUID>` is
the stable idempotency key. Each accepted upload precedes file transfer, and the retained incoming
checkpoint precedes publication. Lost begin replies replay that exact input; known uploads are first
inspected, and expired attempts may renew only under the original identity. Each distinct object is
streamed and verified once per transfer attempt. Complete/publish replies are separately fsynced
through conditional ledger updates. A superseded publication remains pending and never triggers an
automatic new publication attempt. The worker passes exact retained receipts through the dedicated
Helper acknowledgement operation; this ledger never directly authorizes deletion of local content.
The background loop requires neither task redelivery nor the
expired startup lease; Server terminal-session authorization still applies.

`acknowledge_skill_finalization` has exactly
`payload={version:1,capture,receipt,publication}`. `capture` is the full original frozen record,
`receipt` is the canonical typed Server finalization receipt, and `publication` is explicitly null
or the separate complete publication receipt. The schemas live in Node's neutral skillmanager package;
the HTTP API aliases them. The configured authorized worker supplies receipts after authenticated HTTP
validation and durable local storage. They are not Server-signed tokens, and no Node credentials or
HTTP calls enter the Helper. The operation revalidates full original Node/session/preparation identity
and the retained canonical Native resource, without relying on a transient spec. It persists private
`finalization/acknowledgement.json` with fsync/atomic rename before advancing `record.json`. A replay
resumes interrupted intermediate transitions. Older upload attempts, changed incoming checkpoints and
replacement publication decisions fail. Identical replay re-syncs the directory without rewriting the
acknowledgement. It cannot freeze work, upgrade objects, stop a runtime or remove resources.

An upload receipt proves only upload_pending. Complete input retention proves persisted or
persisted_unclean; a separate publication receipt is required for published/conflicted/detached.
Superseded remains persisted and cannot grant terminal cleanup. A success response is
`result={record}` with the exact original capture and acknowledged local phase. The worker checks
it before continuing. Lost Helper replies replay the already saved Server receipt; terminal Helper
retries do not issue another HTTP publication.

`cleanup_skill_finalization` has exactly `payload={capture}` and the same `result={record}` shape.
The record must be terminal and match the Helper's retained complete publication acknowledgement.
First cleanup currently requires the original boot. The operation passively verifies original
systemd/cgroup quiescence and matching available spec; absent specs use only retained bindings and
Helper-derived names. It never stops/kills a writer or adopts another runtime. Skill-work must be the
original mount; mounted tmp must be tmpfs. Both unmount normally without lazy detach. Network deletion
requires bounded namespace inspection before and after the command. Busy/linked/unknown resources
remain pending. It removes only SessionRoot, syncs its parent, then publishes private immutable
`finalization/runtime-cleanup.json` with the terminal capture and original Helper-selected root.
Completed replay checks for reappearing runtime roots, writers and namespace names without removing
replacement resources. All work, frozen bytes, manifests, bindings and receipts remain in independent
SkillStateRoot. The two operations each own 30-second cancellation, a cancellable lock wait and exact
64-bit metadata. Interrupted first cleanup across boots still requires separate reconciliation.

Local state transitions are local_durable -> upload_pending -> persisted ->
published/conflicted/detached. Unclean input instead uses persisted_unclean -> detached. A Server
persistence acknowledgement must retain the complete authorized snapshot reference; per-file
upload success cannot advance this state. The local terminal-state predicate permits only deleting
the session view, not removing its content. Worker receipts are retained separately and acknowledged
into the privileged journal before guarded transient cleanup. Complete lifecycle wiring, cross-boot
reconciliation and reference-aware local content reclamation remain pending. These interfaces enable
no advertised runtime capability.


Session-addressed Native preparation now publishes `session-<session UUID>/work`, `baseline.json`,
`snapshot.json` and `runtime.json` in one atomic no-replace rename. runtime.json binds the helper's
backend, resource ID, boot ID and numeric runtime UID/GID. It is helper-private. A repeated prepare
must match all sealed fields and never refresh an existing work tree. An incomplete existing bundle
is a corruption error, not an absent session. The transient Native spec has an optional
`skill_snapshot_id`; absence preserves legacy compatibility but never authorizes overwriting a
retained bundle. Node-bound streamed task preparation is still pending.

A Native stop with captured but not yet Server-retained state returns process status `stopped`,
`skill_snapshot_id`, `skill_state`, `skill_unclean`, and `state_pending: true`. Cleanup must refuse
that receipt. The Helper locates the same binding even if the runtime spec is missing, and verifies
writer exit before first capture. A repeated stop reuses the existing journal. Once a complete
terminal acknowledgement is retained, transient cleanup unmounts the skill work directory normally
before removing SessionRoot; local content remains in SkillStateRoot. These fields are local Helper
results. The independent worker now transfers and acknowledges the exact Server receipts; complete
stop/task/reconciliation integration and end-to-end Server/runtime acceptance remain required.


Before the first capture, `termination.json` atomically stores version 1, the complete snapshot
binding and the proven unclean boolean. It is helper-private and durable. Retries retain this first
classification even if the systemd unit has since unloaded or capture failed. The termination
receipt prevents relaunch. Existing complete finalization journals remain readable without this
additional record, since they already retain the original classification and binding.

## Server snapshot preparation reads

Behind `SKILL_MANAGER_ENABLED`, Node credentials may read:

- `GET /api/v1/node/skill-snapshots/{snapshot_id}?task_id={task UUID}`
- `GET /api/v1/node/skill-snapshots/{snapshot_id}/files/{file SHA-256}?task_id={task UUID}`

The task UUID is the database preparation-task identity, distinct from its human-readable `task_id`
string. Authorization requires the snapshot's exact assigned Node/task, an active user, a starting
session, a reserved snapshot and a live leased/running `create_tool_session` task. Its payload must
still match the snapshot's user, account, session and backend. Knowing a digest, sharing an account
or possessing another task on the same Node grants no read permission. Subsequent requests reject
expired leases, cancelled snapshots, terminal tasks and stopped sessions. An already authorized
file response may complete from its private verified copy.

The manifest response uses the existing `SkillResult` envelope, `status=ready`, `committed=false`.
Data contains `snapshot_id`, `user_id`, `account_id`, `node_id`, `session_id`, `task_id`,
`runtime_backend`, `library_generation`, `directory_epoch`, `starting_checkpoint_id`, `tree_digest`,
`manifest`, `items` and `system_releases`. Items contain `state_id`, `entry_name`, `state_epoch`,
`checkpoint_id` and the fixed field-resolution object. System release references are selected by
Server and are independent of the mutable user tree.

File responses stream `application/octet-stream` with Content-Length and a quoted SHA-256 ETag.
The file must be present in this snapshot's exact materialized manifest; the endpoint accepts no
alternate tree or user identifier. Server verifies bytes before responding and spools large files
to private disk with bounded memory. The transaction releases before network streaming.

Internal reservation holds the user storage write lock through fresh rule/head reads, branch
initialization, complete-directory composition and all snapshot references. Retries return the
original snapshot even after later configuration changes. An existing branch with another version
requires state migration; preparation cannot silently replace it with a pristine package. Managed
mode never falls back to legacy after all library entries become disabled.

Public managed session admission now uses these routes through the exact task binding described
below. Finalization authorization is separate. Node task consumption, transfer and durable cleanup
acknowledgements remain required before either backend can advertise support.

## Node finalization ingestion

Before the first upload, the Node calls
`POST /api/v1/node/skill-snapshots/{snapshot_id}/termination` with exactly session_id, task_id,
initial_tree_digest, directory_epoch, library_generation, incoming_digest and unclean from its durable
frozen capture. Node identity comes only from authentication; all owners and the original Native
managed task pointer are checked against the snapshot. No startup lease is required. Server stores
a per-snapshot termination receipt with immutable known digest/classification before returning
schema_version=1, status=stopped,
committed=true and an exact echo of the request. The Node validates every field and preserves 64-bit
integer generations. This receipt proves control-plane terminal acceptance only.

When writers are independently proven stopped but capture fails, the Node instead calls
`POST /api/v1/node/skill-snapshots/{snapshot_id}/capture-pending`. Its exact seven fields replace
`incoming_digest` with `capture_error`: `quota_exceeded`, `insufficient_storage`, `portability_error`,
or `capture_failed`. It returns the same committed stopped envelope and exact input echo. Helper
requires fresh original writer/resource proof, retained private termination evidence, and absence
of a finalization directory. It sends no raw diagnostic, content identity or local durability claim.
Migration 0053 permits a null digest only with one of these codes. First full frozen observation
fills the digest and clears the error; a late pending observation cannot downgrade it. The retained
clean/unclean classification never changes. Downgrade refuses any remaining null-digest rows.
Background recovery reports this observation without creating a content-transfer journal or
acknowledging/cleaning/reclaiming work, and keeps revisiting the original capture.

The user retention/session/task locks serialize termination against startup acceptance. An unaccepted
nonterminal create task is cancelled; an accepted startup result remains historical. Nonterminal
sessions become stopped (clean) or interrupted (unclean); existing terminal statuses are preserved.
Reserved/started snapshots become finalizing. Device/browser revocations commit atomically, with
relay closure/outbox delivery after commit. Replay cannot reapply lifecycle changes or change the
frozen digest/classification. Other sessions are not part of this request. An existing finalization
must match the termination observation, and subsequent begin requests cannot change it. Migration
0048 does not backfill historical receipts; existing terminal-session finalizations remain readable.

The worker durably retains its complete capture before this request. Lost replies retry the same
input without a new local journal phase. Known uploads continue through their original status route;
saved terminal publications retry only Helper acknowledgement/cleanup. Stopped confirmation cannot
advance the Helper journal to persisted or authorize deleting unuploaded work.

Finalization writes are separate from preparation reads:

- `POST /api/v1/node/skill-snapshots/{snapshot_id}/finalization`
- `GET /api/v1/node/skill-finalizations/{finalization_id}`
- `PUT /api/v1/node/skill-finalizations/{finalization_id}/files/{digest}?upload_id={upload UUID}`
- `POST /api/v1/node/skill-finalizations/{finalization_id}/complete?upload_id={upload UUID}`

Begin accepts exactly `session_id`, `idempotency_key`, `manifest` and strict-boolean `unclean`.
The original session must match the Server snapshot. User/account/Node/base revision/epochs are
inherited from that snapshot and cannot be overridden by the body. Authentication requires the
assigned live Node credential and an active owner. The Server session must be stopped, interrupted
or failed before ingestion. Unlike preparation reads, finalization does not depend on the old
preparation task lease: recovery may need to upload long after that task ended. Helper writer
quiescence and the sealed original termination classification remain mandatory Node prerequisites.

One snapshot accepts one immutable finalization input. Its canonical tree digest and unclean flag
cannot change, even when the original request is retried with another idempotency key. A matching
retry returns the original receipt. If its upload attempt expired, begin may create a replacement
lease under the same receipt and increment `upload_attempt`; the old `upload_id` then rejects
writes/completion with `UPLOAD_SUPERSEDED`. Status GET never renews a lease. The owning Node must
retain its complete local journal and bytes throughout failed/expired/quota-limited attempts.

The response data contains `id`, `snapshot_id`, `incoming_digest`, `unclean`, `status`,
`checkpoint_id`, `upload_id`, `upload_attempt`, `upload_status` and `expires_at`. The standard
`SkillResult` status mirrors finalization status. `committed=false` during `upload_pending` and
for individual file receipts. Only complete verified content with a retained directory checkpoint
returns `persisted` or `persisted_unclean` with `committed=true`. `expires_at` always includes an
explicit UTC timezone, including responses backed by SQLite. This is content persistence, not
account publication. Repeated completion returns the same checkpoint.

The Go Node client now implements all five ingestion/status/publication operations. It checks exact
canonical receipt fields, immutable snapshot/digest/termination classification, positive upload
attempts and retained checkpoint consistency. A known finalization cannot change identity; a changed
upload ID requires a strictly newer attempt, and completion only accepts its exact submitted upload.
Unknown writes are never retried automatically. File streams must reach verified EOF before a receipt
is accepted. Separate publication preserves published/conflicted/detached/superseded distinctions and
cannot promote unclean input. These methods do not read privileged paths, supply writer-exit proof,
persist Helper acknowledgements or authorize local cleanup. That worker/Helper integration remains
required.

Uploads are bounded by the declared file sizes and verify size, digest and text/binary classification.
The complete directory, independent known skills, valid new skill directories and aggregate root
auxiliary data must satisfy their own state quotas; package file/staging limits do not truncate
runtime state. Candidate new SKILL.md directories are checked again from actual content before
completion so invalid candidates cannot split the aggregate auxiliary quota. Known invalid skills
keep their identity. Ordinary representable bytes, including binary or invalid SKILL.md, are saved
with format diagnostics; system skill paths are rejected. Any incomplete/corrupt/over-quota input
fails without partial checkpoint publication or acknowledgement.

The complete input directory checkpoint and surviving known item views commit atomically with the
receipt. Deleted entries are represented by absence from that verified complete manifest, not by
missing uploaded files. No ingestion endpoint advances a directory or branch head. Publication,
conflict plans, unclean detachment and Node background retries/acknowledgements remain separate
integration work; these endpoints alone do not advertise skill-manager runtime capability.

## Internal account-local candidates and snapshot selection

Migration 0030 gives account-local skills identities separate from the user library. The internal
candidate operation takes an authorized retained directory checkpoint and a valid top-level skill
name; repeated checkpoint/name registration reuses one staged identity. It verifies actual SKILL.md
bytes and retains the complete state tree plus subtree prefix, including cross-entry links. It is not
a public installation endpoint and does not activate the candidate or change any head.

Snapshots include only active, enabled local skills of their own account and record local revision
UUIDs with account field provenance. Staged/removed/disabled identities are omitted. An enabled
library source and active local source sharing a name fail with `SKILL_SOURCE_CONFLICT`; an expired
local branch requires reset/restore. Current directory dependencies still have to satisfy every link.
Library list/pin operations cannot select these local revisions. New directories with invalid skill
names stay auxiliary state and cannot split its aggregate quota. Publication/takeover must perform
the future atomic activation step.

## Atomic publication of a persisted finalization

`POST /api/v1/node/skill-finalizations/{finalization_id}/publish` is separate from ingestion and
requires the original authenticated Node, active owner and exact terminal snapshot binding. It takes
no body and does not trust caller-supplied epochs, heads, branch or owner IDs. Expired preparation and
upload leases do not revoke this authority over an already persisted input. An incomplete input
returns `STATE_PENDING`. A successful repeat returns the original publication attempt; it never
retries around an unresolved conflict.

The standard `SkillResult` has `committed=true` for the committed result, with status `published`,
`conflicted` or `detached`. `data` contains `id`, `finalization_id`, `attempt`, `status`, `reason`,
`result_checkpoint_id` and `conflict_count`. Only `published` advances account heads; the original
finalization status GET reflects the result. The input `checkpoint_id` remains the original incoming
checkpoint, while `result_checkpoint_id` identifies the published merged directory. Conflict counts
are explanations, not permission for the Node to select resolution sides.

The transaction holds the user storage lock and checks directory epoch plus the state/install epochs
of branches actually changed relative to the exact snapshot. Any invalid changed branch detaches the
whole input. Unchanged/unexposed branches do not count as writes. A new default revision does not
redirect late writes from an older session: those remain on the original branch. Unclean input is
always detached. A completely unchanged input returns published without creating a new head.

Current heads and incoming changes merge by connected units, retaining cross-entry link dependencies
and conservative binary/database divergence. Any conflict preserves the whole input and current
comparison references and changes no head. Valid new skill directories get stable staged local
identities; their activation commits only with the whole successful directory publication. Same-name
existing sources produce `source_conflict` even if bytes are identical. Omitted snapshot members are
preserved, not interpreted as deletions. Deleted or malformed known skills retain their branch state
and block later startup rather than silently reverting to the original package.

User conflict inspection/resolve and superseding/recomputing plans are described below.
Reset/restore and migration APIs are described below. Retention and Node transfer/cleanup
acknowledgement integration remain unfinished. Publication alone does not advertise backend capability.

## User conflict inspection and resolution

Migration 0032 and the pure resolver now support a strict choice with one of `use=current/incoming`,
`file_tree_digest`, or `directory_tree_digest`, scoped by `path`, a complete connected `unit`, or the
whole account directory. Files require a conflict path; directory replacements forbid `path`.
Custom trees are state trees authorized and fully verified by the user service.
Opaque units cannot be split; incomplete/invalid compositions produce no publishable partial tree.
The command also fixes `idempotency_key`, `expected_revision` and strict `dry_run`.

Active user tokens can use these routes under `/api/v1/skills/state`:

- `GET /conflicts?account_id=…&limit=…&cursor=…` lists bounded unresolved/superseded attempts.
- `GET /conflicts/{id}` explains exact inputs, branches, plan and replacement attempt.
- `GET /conflicts/{id}/diff?limit=…&cursor=…` returns bounded three-sided path metadata.
- `GET /conflicts/{id}/trees/{base|current|incoming}` returns the exact retained manifest;
  append `/files/{digest}` to stream a verified declared file.
- `POST /conflicts/{id}/uploads` accepts a client key and complete manifest. Its
  `/uploads/{upload_id}` GET, `/files/{digest}` PUT and `/complete` POST counterparts resume and
  verify custom state content. Upload identity is bound to that publication; completion alone
  saves no choice and advances no head.
- `POST /conflicts/{id}/resolve` accepts the command above. Overlapping saved choices are replaced;
  independent choices remain. Partial or invalid combined dependencies save only a pending plan.
- `GET /resolution-operations?key=…` returns the immutable original accepted command result.

`base.source=session_snapshot`, `current.source=publication_comparison`, and
`incoming.source=finalization` disambiguate the actual three retained trees. Device/Node credentials
cannot use these routes. No supplied owner/account/head overrides the original publication identity.

Resolution data contains `publication_id`, `operation_id`, `status`, `plan_revision`, `ready`,
`choices`, `remaining`, `result_tree_digest`, `result_checkpoint_id`, `replacement_id` and
`stale_reason`. Status is `preview`, `pending`, `published` or `superseded`; the envelope is committed
for accepted non-preview commands, which does not imply head publication for a pending plan.
Dry-run never saves a choice, receipt, replacement attempt or head. User-key replay precedes current
plan revision/status checks and returns the original response; changed input with that key fails.

The transaction rechecks directory and branch heads/epochs, original revisions/sources and source
name collisions. A stale command supersedes/recomputes from immutable input without applying or
copying its choices; dry-run only reports the stale reason. Reset/reinstall invalidity detaches the
original input. Whole incoming/custom results cannot revive an unchanged pre-reset branch or removed
source. Unexposed members remain protected. A colliding source requires explicit `use=current`
retaining its exact subtree; identical bytes never authorize takeover. Valid custom new skills may
activate account-local identities only with complete directory publication. All plan/receipt/head
changes roll back together on any failure. Existing Node `/publish` retries never execute a choice.

See Server `docs/skill-resolution-plans.md` for transaction and content details. State migrations,
reset/restore/retention, CLI commands and Node transfer/cleanup integration remain unfinished.

## User checkpoint queries and export units

The following user-token-only routes are now available under `/api/v1/skills/state`:

- `GET /checkpoints?account_id=…&skill=…&limit=…&cursor=…` lists one source's checkpoint history
  across versions/epochs. Use `scope=account-directory` instead of `skill` for complete directories.
- `GET /checkpoints/{id}` identifies the exact scope, stable source, revision, installation epoch,
  current branch/directory epochs, head flag, retained content digest and source session/finalization.
- `GET /checkpoints/{id}/members?limit=…&cursor=…` pages a directory's immutable member references.
- `GET /checkpoints/{id}/diff?limit=…&cursor=…` compares an item against its own original library or
  local revision, or a directory against its parent. Metadata paths retain account discovery-root
  prefixes. Expired baselines fail explicitly instead of appearing empty.
- `GET /checkpoints/{id}/tree` and `/files/{digest}` export a complete verified unit. Directory
  scope includes everything; item scope includes its complete connected link dependencies and
  reports additional `dependency_roots`, preserving original paths. Independent members are excluded.
  `source_tree_digest` and export `tree_digest` have distinct, explicit meanings.
- `GET /pending` accepts the same account/item or directory selector and independently pages
  incomplete finalization uploads. These name the source Node and explicitly cannot be exported
  from Server as a complete checkpoint. A pending identity is not a checkpoint identity.

History/pending/member pages have a 200-record maximum; diff pages have a 500-path maximum. Named
library/local collisions require a stable source UUID. Archived identities remain accessible by UUID;
account-local IDs cannot cross accounts. Directory scope and skill selectors are mutually exclusive.
Checkpoint and pending cursors cannot substitute another account/source. Queries create no state.

An exact branch head is not necessarily today's selected revision. `is_head`, source-session
`finalization_status`, retention and current epochs are separate fields. Complete deleted item inputs
retain empty views, including detached inputs, and exports label them `locally_removed=true`.
Metadata tombstones remain inspectable but cannot export. File reads verify before streaming and
return `CONTENT_INCOMPLETE` for missing bytes or `CONTENT_INVALID` for corrupt bytes.

Server `docs/skill-state-queries.md` defines the export layout and caller obligations. Current-effective selection/default state diff and reset/restore are described below. Migration,
prune/GC, pending Node-local export and CLI atomic safe destination materialization remain unfinished; these routes do not advertise backend readiness.

## Current effective state and explicit reset/restore

User-token routes under `/api/v1/skills/state` now include:

- `GET /current?account_id=…&skill=…`, or exclusive `scope=account-directory`, returns the exact
  selected sources/revisions, pin/enable provenance, installation epochs, optional branch heads,
  state epochs/expiry, library generation and directory mode/head/epoch. It creates no state.
- `GET /diff` takes that same selector with a bounded path page and compares the selected current
  head against the baseline described above. A missing/expired branch fails instead of falling back.
- `POST /commands` accepts `action=reset|restore`, `selector`, the complete `expected` precondition,
  `idempotency_key`, strict `dry_run`, and a `checkpoint_id` only for restore.
- `GET /operations?key=…` recovers an immutable accepted state-command response.

Reset restores the selected original library package or local initial subtree. Item restore requires
matching owner/account/stable source/name/revision; same-source old installation epochs may be
explicitly restored. Directory restore additionally requires exact effective member identity/name/
revision equality and reports scope differences. Directory reset clears root auxiliary data, while
both directory mutations preserve current nonselected members without enabling or changing their
branch state. Complete dependencies, actual bytes and per-scope/user storage limits are revalidated.

The result contains `before`, complete directory `changes`, per-target `branch_changes`, `affected`,
result tree/checkpoint IDs, `directory_epoch_advances` and `superseded_conflicts`. Per-branch comparison
uses each branch's own old head, which may differ from the version shown in the current directory.
An expired comparison baseline is explicitly unavailable. Previews create no branches, reservations,
checkpoints, receipts or epoch changes. Actual commands atomically publish new selected heads, advance
their state epochs and publish the complete directory; directory-scope commands also advance its epoch.
The library generation, pins and enabled rules remain unchanged. Old history remains recoverable.

Changing any expected rule/head/epoch returns `STATE_PRECONDITION_CHANGED`; a matching accepted key
replays its original response before checking today's state. Changed input cannot reuse that key.
A failure at the final directory CAS rolls back all earlier branch and receipt changes. Migration 0033
retains owner/account/scope-bound input/result checkpoint references in immutable state operation rows;
downgrade refuses to discard existing receipts.

Old unresolved attempts in the affected account become `superseded` with `state_reset` or
`state_restore`, without executing their input inside this command. Later user resolution may remerge
that original input into a new attempt, never copying/applying old choices. Invalid original epochs
produce detached replacements; late session uploads remain recoverable but cannot revive reset data.

See Server `docs/skill-state-mutations.md` for the complete implemented contract. Explicit reset of an
uninitialized selected revision is supported. Migration resolution and managed admission are described
below; retention/GC, takeover, Node/CLI integration and backend acceptance remain unfinished.

## First-use version preparation and durable migration inputs

User-token routes under `/api/v1/skills/state` now additionally include:

- `POST /prepare`: single-item `selector`, complete `expected` current-state precondition,
  persistent `idempotency_key`, and strict `dry_run`. The source must be an effectively enabled
  user-library entry in an already managed account. The request targets its selected revision.
- `GET /preparations?key=…`: immutable original preparation `result` plus `current_status`, which
  may subsequently become `superseded`. Lookup never executes migration again.

A successful exact snapshot reservation records the actual exposed library branch under account,
installation and installation epoch. Preview, failed reservation, migration attempts, old snapshot
retries and late finalization do not update this ledger. Preparation uses that branch's current
published head, skipping never-used registered intermediate revisions. Historical snapshot members without a trustworthy
ledger return `STATE_HISTORY_UNAVAILABLE`; a branch only initialized by reset without any actual
reservation is not prior use. Expired source state requires explicit recovery.

Preparation has four modes: `initial` uses the selected original package when there is no previous
branch history; `forward` compares old original / new original / old published state; `older` enters
an unused earlier registered revision from its original package and warns
`newer_state_not_migrated`; `resume` keeps an existing target head without replaying old changes.
Registration order makes no upstream compatibility claim. Pinning resolves to the pinned branch;
unpinning can expose a target that needs preparation.

The result includes explicit `base_source`, `current_source`, `incoming_source` labels and digests,
exact source revision/checkpoint/epoch, target state, result checkpoint/directory, conflicts and
warnings. Independent migration sides are complete prefixed member trees; the source checkpoint
separately retains the full original directory. A linked-state conflict preserves the full source
input. Conflict units use `.` for auxiliary scope and inspect both source and current-directory
links, including incoming links from other roots. They never silently import another source.

All bytes, complete dependencies and scope quotas are checked. Aggregate preview admission counts
the union of files across all retained inputs and result without upload reservations or cleanup.
Successful first-use preparation publishes the complete directory and target checkpoint together
through exact head/epoch CAS without advancing epochs or changing library rules. Existing target
resume leaves heads unchanged. A late CAS failure rolls back input references, branches and receipts.

`ready` means the selected branch is prepared; it does not assert runtime/backend readiness.
`conflicted` is a durable accepted preparation result with no target head publication. A committed
conflict response is not a claim that migration succeeded. Dry-run returns the prospective status
with `committed=false` and no operation ID. Duplicate accepted keys return their original results
before checking current configuration. Reset/restore supersedes pending preparation records while
retaining their inputs; their old keys never replay into the clean target.

Migration 0034 adds source/target owner/account/installation/epoch constraints and rooted comparison
trees. Public managed admission invokes preparation for every included uninitialized library target;
natural conflict evidence commits before session creation is denied. Explicit incremental migration,
last-migrated baselines, conflict inspection/export and resolution are described below. Retention,
Node/CLI workflows and real backend acceptance remain unfinished.
See Server `docs/skill-state-migrations.md`.

## Explicit incremental revision migration

Additional user-token routes under `/api/v1/skills/state`:

- `GET /migration/current?account_id=…&skill=…&from_revision=…&to_revision=…` accepts revision UUIDs
  or `rN` registration numbers and returns exact source/target state, directory head/epoch, library
  generation, installation epoch, latest successful migration and `source_has_unmigrated_checkpoint`.
- `POST /migrate` accepts `selector` with those same fields, the complete `expected` precondition,
  persistent `idempotency_key` and strict `dry_run`.
- `GET /migration/operations?key=…` returns immutable `result` plus current ready/conflicted/superseded
  status. Preparation and migration keys share a user namespace, but each uses its own typed receipt
  endpoint; the wrong endpoint returns `OPERATION_KIND_MISMATCH`.

The from/to versions must be different revisions of the account's same active user-library
installation and current installation epoch. They need not match the effective pin or enabled state.
Migration changes neither rules nor the last-effective snapshot ledger. Source must have a published
head; missing targets use their original package as the current side. Source/target expiry requires
explicit recovery. Other-source or other-account revisions never substitute even with equal bytes.

Migration 0035 adds source-branch `base_checkpoint_id`, target-branch `current_checkpoint_id` and a
unique successful `migration_sequence` scoped by source ID, target ID, both state epochs and directory
epoch. Complete successful first-use forward migration begins the sequence. Explicit migration uses
that latest success's source checkpoint as its baseline; with no success in this exact scope it uses
the source original package. It always compares against the target's own head. Thus target edits or
deletions of earlier imported files survive later unrelated source additions.

Side labels are `base_source=old_original|last_migrated`,
`current_source=target_original|target_published`, and `incoming_source=source_published`.
The response includes exact before-state, all three retained digests, full result references, target
`changes`, complete `directory_changes`, conflicts and actual successful sequence. Preview has no
operation/sequence and performs no writes. Conflicts retain complete inputs without a successful
sequence. A repeated source checkpoint produces an explicit no-change result and preserves both
heads. Accepted duplicate keys replay their original result before any current-state checks.

Publication, input references, success sequence and receipt commit together under the storage user
lock and complete head/epoch CAS. A late failure rolls them all back. Reset/restore supersedes pending
migration without executing it. New epochs form a new explicit migration scope and cannot silently
reuse old-epoch delta baselines. Missing retained baselines fail instead of replaying all historical
differences from the original package. Linked and opaque-state disagreements remain retained conflicts;
this endpoint has no force-overwrite bypass.

0035 backfills sequence 1 for compatible existing forward successes without rewriting their original
JSON receipts; incompatible duplicate history fails upgrade rather than guessing order. Downgrade
refuses incremental history before changing schema. Upgrade must quiesce old Server writers because
0034 code cannot supply the new successful-sequence invariant. Migration-specific conflict resolution
and managed admission are described below. CLI/Node integration remains separate work.

## Migration conflict inspection and exact export

User-token routes under `/api/v1/skills/state/migration/conflicts` use the independent preparation or
migration receipt ID; they never create synthetic session/finalization identities:

- `GET ?account_id=…&skill=…&limit=…&cursor=…` lists conflicted/superseded records, with optional
  stable-source selection and at most 200 records. The UUID cursor must belong to the selected
  account/source. Ordering is descending original creation time, then UUID.
- `GET /{id}` returns original mode, current status, source/target branch identities and saved epochs,
  immutable `original`, separate `base`, `current`, `incoming`, `directory` references and `live`
  diagnostics. Each reference has its actual source label, revision, optional checkpoint and exact
  saved tree digest. Successful preparations are not exposed as conflicts.
- `GET /{id}/diff?limit=…&cursor=…` returns at most 500 paths of saved three-sided metadata differences.
  `comparison=saved_inputs` explicitly means these are inputs, not approved writes. Its opaque cursor
  binds the receipt ID, all three digests and the previous differing path; a different attempt cannot
  reuse it even when its trees are equal. This endpoint does not read file bodies.
- `GET /{id}/trees/{side}` accepts `base|current|incoming|directory`. It returns the exact unmodified
  saved manifest, its input reference, `target_root` and `extra_roots`. Extra roots may include linked
  dependencies or independent context; their presence is not authorization to overwrite them.
  Paths and link targets are not cropped or rewritten.
- `GET /{id}/trees/{side}/files/{digest}` reads only files declared by that exact authorized side.
  It verifies the whole file before responding and releases the database transaction before streaming.

First-use sides retain `old_original/new_original/old_published` labels. Incremental sides retain
`old_original|last_migrated`, `target_original|target_published`, and `source_published`. Directory
context is separately labelled `account_directory` and references the saved complete directory;
it is never substituted for the migration's current side.

Live diagnostics compare installation removal/epoch, configuration generation, directory mode/head/
epoch, source and target expiry/epochs, target head and latest successful migration baseline.
A same-epoch source head change sets `source_head_advanced` without rewriting incoming or treating it
as a reset; any concurrent directory head change is reported independently. An unpublished target
branch created while retaining conflict evidence is not itself drift. Superseded and removed-source
history remains readable by stable identity. Expired directory context and unavailable/corrupt file
bytes fail explicitly. These reads create no library, branch, upload, plan or receipt, and Node/device
tokens cannot use them. Migration-specific resolution remains unfinished.

## Migration custom content and plan storage

Migration `0036_skill_migration_resolution` adds separate upload bindings, completed custom-content
grants, versioned plans, scoped choices and immutable user-keyed resolution receipts. Composite
foreign keys bind user/account/migration throughout. A custom choice may reference only a tree
explicitly completed for that same migration, including when another migration has identical bytes.
Plan storage uses revision CAS and a savepoint around version advancement and choice replacement.
These storage primitives alone do not authorize a resolved result or advance a successful migration
baseline. The atomic resolution command and user routes described below now provide that boundary.

Additional user routes under `/api/v1/skills/state/migration/conflicts/{id}`:

- `GET /plan` returns `migration_id`, `current_status`, `revision` and saved `choices`. An absent
  plan returns zero and an empty list without creating a row.
- `POST /uploads` accepts a bounded `idempotency_key` and complete `manifest`. New uploads require
  an active conflict. Already bound keys recover their original lease before current-status checks,
  so a lost response remains recoverable after reset; changed manifests reject key reuse.
- `GET /uploads/{upload_id}` returns the exact authorized lease and current expiry state.
- `PUT /uploads/{upload_id}/files/{digest}` receives only a declared file after validating the
  original migration binding, verifying size, digest and content type.
- `POST /uploads/{upload_id}/complete` verifies actual bytes and atomically commits the complete
  private state tree with its migration-scoped grant. Its `stored` result describes the upload only;
  it neither creates a plan nor publishes any checkpoint.

Internal keys use `migration-resolve:{id}:upload:{key-hash}`, but authorization also requires a real
upload binding row. A generic upload with a forged matching prefix cannot substitute. Existing
uploads can be recovered/completed after the conflict is superseded; this never restores publication
authority or creates a new upload. Repeated completions and different bound uploads of the same tree
retain one content grant. Missing/corrupt actual bytes fail, including when loading previously
completed custom choices. Device/Node/other-user credentials cannot inspect or mutate these routes.
Downgrade refuses before schema mutation while any of the five new tables has retained history.

The internal migration candidate planner now computes complete connected-unit results using saved
base/current/incoming plus the saved account directory. Whole choices affect the target's complete
connected unit; independent skills stay at their saved directory content even if an incoming export
contains older copies. `current` takes the target's own saved state and the directory's related
context, rather than other roots from the target checkpoint's historical backing tree. Reverse links
that exist only in the account directory still force a complete-unit choice. Invalid combinations
produce conflicts with no partial manifest.

Candidate calculations verify actual saved/custom bytes and quotas, retain exact target revision,
and distinguish changes against target current state, target original package and account directory.
They mark target modification separately and enumerate other changed roots. Current drift rejects an
old comparison before calculation. This planner is a read-only component; a valid candidate does not
authorize related-source writes by itself. The atomic service below supplies publication authorization.
The full resolver intercepts stale attempts using the recomputation protocol below.

The internal draft editor additionally supports version-CAS plan edits and immutable typed receipts.
Each new choice replaces intersecting saved ranges and preserves disjoint choices; the full remaining
plan is revalidated, including exact custom grants and bytes. Preview retains the current version and
writes nothing. Save advances the version and records the original response in one savepoint; a late
receipt error rolls back the choices and version. Same-user key replay returns that response before
checking later plan changes or supersession. A separate receipt view labels current migration status.
The response type `migration_resolution_draft` uses `planned` and `candidate_complete`, never a
published status. This internal draft editor has no public mutation route; the public final resolver
below has its own response and receipt type, including retained-input recomputation.

Checkpoint provenance (`0037_skill_checkpoint_provenance`) is now explicit in checkpoint list/detail:
`state_epoch` is the item creation epoch, `directory_epoch` is the directory creation epoch, and
`backing_directory_id` identifies the item's actual complete-tree context. Current epoch fields remain
separate. Directory member views include the original member checkpoint's `state_epoch`. Legacy
unknown values stay null, and independent package initialization legitimately has no backing directory.
The owner/account/scope/content-bound reference survives retirement of bytes without inventing history.

Complete migration candidates validate related current targets and, for whole incoming choices, the
source item's exact historical backing members. Matching bytes do not authorize another stable
identity/revision or pre-reset epoch. Unknown evidence returns `STATE_PROVENANCE_UNAVAILABLE`; identity
and epoch mismatches return explicit source/epoch errors. Same-identity same-epoch historical related
content can still be selected explicitly. Custom directories target the saved current identities.
Actual multi-branch publication, public resolve and stale recomputation are described below.


## Atomic migration resolution and typed receipts

`POST /api/v1/skills/state/migration/conflicts/{id}/resolve` accepts the strict shared resolution
request: `idempotency_key`, `expected_revision`, one `choice`, and optional boolean `dry_run`.
The choice is exactly one of current/incoming, a migration-scoped uploaded single-file tree with a
path, or an uploaded complete directory. Whole choices cover the target's complete connected unit.
Overlapping saved choices are replaced; independent choices remain. Invalid scope or incomplete
content never grants authority to another source. Newly introduced or modified valid skill roots
outside the saved authorized names fail with `STATE_SCOPE_MISMATCH`.

The result has operation kind `migration_resolution`, status `preview | pending | published | superseded`, current
or saved `plan_revision`, complete choices, remaining conflicts, connected unit, candidate digest,
precise target revision/modified state and full differences against target current/original and the
saved account directory. `affected` lists every branch to be written with stable source, origin,
revision, installation/state epochs, original head, result checkpoint (only after publication), and
changes against that branch's own current and original content. Local sources use their own initial
revision. Unchanged related members retain their existing checkpoint and backing directory.

Incomplete plans save choices and an immutable receipt without publishing. Complete plans atomically
save choices, CAS all affected branch heads and the complete account directory, update the migration
result and success sequence, and save the final receipt. Any late failure rolls back the whole savepoint.
Deleted members retain an empty/invalid item view but leave the directory membership. Root auxiliary
changes are part of the same complete directory. Previews write no plans, receipts, checkpoints or
uploads and perform the same byte, scope, identity, epoch, quota and sequence-bound validation.

Only forward/incremental publication advances a successful migration sequence, using the original
saved source checkpoint. Later same-epoch source writes wait for another explicit migration. Initial
and older preparation may also conflict on invalid links; explicit repair preserves their mode and
leaves sequence null. Initial input has no invented source checkpoint; importing related stable
members without source provenance returns `STATE_PROVENANCE_UNAVAILABLE`.

`GET /api/v1/skills/state/migration/resolution-operations?key=...` returns the immutable original
`result` and separate `current_status`. Lookup requires the owner user token and rejects draft receipt
types. Original-key replay precedes version/status/drift checks, so a prior pending result remains
pending even after later publication. The original preparation response and source inputs never
change. Ready conflict diagnostics compare against their own published result and success baseline.
The skill feature gate applies to both routes. Mutating responses have `committed=true`; preview is
false. Operation lookup reports the original accepted status, not a new execution.

Stale comparisons do not apply submitted choices. The full resolver follows the retained-input
replacement protocol below. Public managed admission can use the resulting published branches;
these APIs do not advertise Node runtime capability.


## Retained-input migration recomputation

Migration `0038_skill_migration_replacement` adds nullable `recomputed_from_id`, `replacement_id` and
`superseded_reason` to preparation records. References bind owner/account; a unique predecessor
constraint prevents two direct recomputation children. Self-reference and replacement metadata on
active records are rejected. Legacy values stay null. Downgrade refuses before changing schema when
any replacement information exists.

After immutable key replay and plan revision checks, resolve detects stale input before evaluating the
submitted choice. Same-epoch target/directory head changes create one new attempt with the exact saved
source checkpoint and baseline, the current target, and current complete directory. A newer source
head remains unmigrated; it never becomes the replacement incoming. Complete historical link context
comes only from that original source checkpoint. Original plans, choices, scoped custom grants and
response JSON remain attached to the original attempt; the replacement has no saved choices.

The original request returns `superseded` with `replacement_id`, `stale_reasons` and
`recomputation_possible`. This status never becomes `published` merely because its replacement can
merge automatically. The replacement can be `ready` after a clean atomic merge or `conflicted` with a
new empty plan. Its detail endpoint permits inspection of that recomputed ready result as well as new
conflicts. New uploads/choices must target the new conflict. A retry against an already superseded
attempt returns its existing relation and creates no fork. Dry-run returns `preview`, classifies the
change and preserves any already-known replacement, but creates no attempt, plan, receipt or head.

Source/target reset/restore, installation epoch changes, expired sources/targets, or invalidated
actually changed linked members terminate the old attempt without reviving data. Reset/restore
persist their distinct reasons. A changed successful migration baseline points to the newer successful
record and cannot be rewound by old source input. A first-use preparation whose configured target is
no longer included or selected becomes superseded; an explicit incremental migration keeps its own
source/target selection independently of the default pin. Initial/older recomputation preserves their
original initialization semantics and never automatically imports newer learning or assigns a migration
success sequence.

Conflict summary/detail exposes predecessor, replacement and reason separately from the original
response. Preparation/migration/final-resolution operation receipts expose current replacement and
reason separately as well. A final superseded receipt remains unchanged if its replacement is later
resolved or reset. Any failure while publishing, saving the replacement/link, or saving the resolve
receipt rolls back the entire new attempt and all heads under the same user lock/savepoint.

Account-wide reset/restore cancellation is rechecked against actual affected epochs. An independent
or untouched linked member does not count as a write. A retained complete candidate defines related
writes by its differences against the saved directory; without a complete candidate, retained incoming
differences are the conservative boundary. If those writes remain authorized, resolve may create a new
empty-plan comparison using current directory context for untouched members. No old choices or custom
grants transfer. The original plan remains superseded. A new whole incoming choice still requires
historical source identity/epoch evidence, even when related bytes match; removal and reinstallation
also invalidate that historical source authorization.

Library mutations proactively supersede pending migrations targeting removed or outdated installation
epochs. Preparation additionally checks each account's effective inclusion and revision, preserving
independent account overrides and explicit incremental directions. Successful forward/incremental
publication immediately supersedes pending comparisons with matching owner, account, installation,
source/target direction and all epochs, linking them to that success. Initial/older publication has
no migration sequence and does not replace incremental baselines. Recomputed parents use their own
replacement CAS. Previously reset/restore-cancelled attempts without a replacement can also link to
same-epoch success; existing links and attempts from other epochs remain unchanged.
All invalidation shares the originating mutation's savepoint, including rollback on
a late receipt failure. Historical response replay remains immutable.


## Managed session admission and backend capability

The existing `POST /api/v1/sessions` now holds the user content lock across mode selection,
full-account preparation, session/task creation and exact snapshot reservation. One outer savepoint
rolls back all preparation, session/task, snapshot, effective-use and audit mutations on failure.
Session API errors retain their existing envelope; content quota/size errors return 413 and other
skill state errors return 409.

Natural preparation conflicts instead commit their retained inputs and return
`STATE_MIGRATION_REQUIRED` (409), with `account_id`, `migration_ids` and
`preparations_committed: true` in error details. No new session, task, snapshot or effective-use update
is created. Retries reuse active comparisons with the same complete normalized preconditions;
public idempotency keys cannot substitute another operation type or target. Existing published heads
remain unchanged, and expired included branches require explicit recovery.

Legacy accounts without included managed content retain the legacy path. Legacy accounts with
included content and accounts in `migrating` require takeover (`MIGRATION_PENDING`). A `managed_v1`
account always uses managed admission, including an empty or fully disabled library. The feature
switch must be enabled; no fallback is allowed.

Each backend separately reports this shape in its authenticated heartbeat:

```json
{
  "backends": ["native"],
  "skill_manager": {
    "native": {
      "protocol_version": 1,
      "manifest_version": 1,
      "writable_copies": true,
      "finalization": true,
      "recovery": true
    }
  }
}
```

The same independent object may appear under `docker_sandbox`. Versions are strict integers and
flags are strict booleans. Malformed replacement reports revoke old capability. Reports require a
nonfuture heartbeat younger than `node_offline_after_seconds`, explicit backend availability, and
the existing tool/region/backend allowlist checks. Active accounts remain pinned to their session
node; idle accounts may select another compatible candidate. Incompatibility returns
`SKILL_MANAGER_UNSUPPORTED`. Preparation completion refreshes Node state and rechecks capability
before snapshot reservation; failure rolls back the launch.

The existing `create_tool_session` payload gains only this pointer object:

```json
{
  "skill_manager": {
    "protocol_version": 1,
    "manifest_version": 1,
    "snapshot_id": "<snapshot UUID>",
    "task_id": "<database NodeTask UUID>"
  }
}
```

No manifest or file bytes are embedded. Downloads require the exact leased task, session, account,
user, backend and snapshot, and strictly check pointer versions when the binding is present.
Preexisting internal snapshots without the optional pointer retain their original exact authorization.
The snapshot separately records Server-selected ego-browser version/commit/tree references and,
when selected by the existing device gate, the device protocol and Node release reference. Node must
still consume and verify these references through the real component release paths.

The Node snapshot client now validates exact snapshot/task-record/Node/user/account/session/backend
identity, canonical manifest digest, positive directory/member epochs and nonnegative int64 library
generation. Snapshot/member/resolution objects require complete canonical fields; missing values,
case aliases, duplicate keys and nonnullable nulls fail. The full manifest response has a 64 MiB
ceiling; ordinary responses and error bodies retain 4 MiB. File reads require HTTP 200, octet-stream,
exact Content-Length and strong digest ETag, no content transformation or redirect, plus streamed
length/hash/text-classification verification. Any partial private staging must be discarded on error.
No successful download authorizes launch or substitutes for verified pinned system artifacts.

The legacy Node session decoder and Helper reject any present `skill_manager` marker, including
null and case aliases, with `SKILL_MANAGER_UNSUPPORTED`. The worker routes managed markers and
managed journal entries before generic terminal replay. Dedicated Native decoding requires canonical
creation fields, the exact four-field pointer, configured Node identity, poll record UUID, logical
idempotency key and positive attempt. Invalid input stays nonterminal and cannot use legacy launch.
The Helper checks before its old result cache; no historical legacy receipt certifies a snapshot.

Preparation now supports `POST /node/skill-snapshots/{snapshot_id}/lease?task_id=<record UUID>`
with the strict body `{"lease_attempt": <positive poll attempt>}`. Renewal checks the complete
original managed pointer, active owner, reserved snapshot, starting session and live leased/running
task under the user/task locks. It updates only the existing deadline, never the attempt or snapshot,
and grants at most 300 seconds. The `leased`, `committed=false` response returns all original
snapshot/task/Node/user/account/session/backend identities, exact attempt, `server_time`,
`lease_until` and `renew_after_milliseconds`. Old attempts, expired tasks, missing managed pointers
and terminal state cannot borrow or revive this authority.

Snapshot file routes select the exact immutable manifest member in a short authorization transaction,
commit before verified private disk staging, then reauthorize before returning the spool. Renewal and
revocation can therefore commit while copying is blocked. Files remain bounded and hash-verified;
revocation or deletion during staging fails closed. The worker translates the returned duration into
a conservative local deadline by subtracting round-trip time and cancels dependent HTTP/Helper work
on any uncertain renewal. The lease loop is owned and joined; preparation does not outlive it.

The internal worker preparation coordinator now composes lease renewal, authenticated snapshot fetch,
Helper spec creation and digest-only streaming. Its receipt is local preparation, not runtime
readiness or a terminal task outcome. The separate startup coordinator described below owns the
lease through launch/recovery and Server confirmation. Dedicated Native queue dispatch uses that
coordinator; the legacy Helper path continues to reject managed markers.

The separate Helper `prepare_skill_snapshot` stream now consumes a full validated snapshot for an
existing trusted Native spec. Its ordinary request contains only session/snapshot/task-record UUIDs
and the following input byte length. A separate input frame permits at most 64 MiB. The Helper then
requests only manifest file digests; each exact-length raw object ends with a completion byte emitted
after authenticated download verification. The Helper independently verifies size/hash/classification
and uses its own paths, identity and copy policy. No token or caller-selected host path is transferred.

Socket loss cancels input/materialization, including waits behind another Helper mutation. Pending
file transfer is bounded by a pipe and the entire stream has a ten-minute ceiling. Unpublished staging
is removed on failure; an atomically published complete bundle survives an uncertain response for
exact replay. Its sealed binding adds optional `task_id` and `preparation_digest` together; old internal
records remain readable but do not become streamed-preparation receipts. The complete input digest
includes original checkpoint, members, resolution and system references, normalizes object key order
and preserves integer precision. Different fixed inputs cannot reuse or replace retained work.
Preparation does not create a trusted spec, mount, start, renew a Server lease
or acknowledge runtime readiness; the worker startup coordinator must still connect those steps.

Helper preparation now requires the original canonical ego-browser version/commit/tree reference and
checks it against the embedded release; enabled external wrapper/Skill artifacts also undergo the
existing provenance and byte verification. Device selection must exactly match the trusted spec's
protocol and the Helper binary's compiled Node release, independently of the worker version label.
Unknown names, missing fields, aliases, nulls, duplicates and noninteger protocol values fail before
content reads. The sealed binding retains typed system pins for mount-time verification. Historical
records without pins remain readable for recovery, but cannot mount current artifacts as substitutes.
Native overlays omit the device skill when it was not selected. First mount and mount replay verify
the exact selected system trees, readonly ownership/modes, bytes and absence of extra entries or links;
verification does not repair already mounted system copies.

The Helper now separately accepts `prepare_managed_session_spec` with the original snapshot
identity/input digest, system pins and declarative Native session input. It requires the existing
closed account fence, no-follow account directories and an absent runtime before initial admission.
A private started intent binds the logical request and complete Helper configuration. A complete
nonce-free draft precedes immutable publication of `spec.json`, `timezone` and `resolv.conf`; a ready
receipt seals that draft's digest. Exact ready replay checks original files, UID/GID and boot without
rebuilding. Interrupted publication may reuse the same draft on the original boot. Missing or
conflicting completed state, retained work, foreign directories and uncertain unit state fail closed.
Shared account skills and account ownership/ACLs are not rewritten by this operation.

The operation returns only `spec_ready`, session/snapshot/task-record IDs, Native backend and internal
runtime UID. Public failures use `SKILL_SPEC_UNAVAILABLE`. Connection cancellation also interrupts
mutation-lock waits; cancellation during existing workspace/profile/ACL helpers is checked between
steps and before sealing ready. The connection context expires after 30 seconds, but a legacy helper
step may finish before observing cancellation. A ready receipt is required for new managed specs at
content preparation and launch; preparation additionally compares the original complete snapshot
digest and task record. This is not a lease, runtime readiness, or an authorization to relaunch after
an ambiguous start. The dedicated Native queue now invokes the startup coordinator.

The separate Helper `start_managed_session` now accepts the identical spec request and logical
request ID. It requires the original ready intent/private draft, exact retained prepared bundle,
original runtime identity and pinned artifacts. Before systemd execution it publishes a no-replace
private launch intent; readiness seals the original transient invocation ID. Exact completed replay
returns the historical `running` task result without recreating transient files or asserting current
liveness. Incomplete same-boot recovery can only inspect the original active unit and work mount:
unit user/cgroup/transient identity, stable invocation, exact mount identity, rw/nosuid/nodev/private
flags and actual system copies must still match. Recovery never mounts or repairs beneath a live
runtime. Missing or non-running units enter shared stop/finalization, never another systemd-run.

The 15-field result contains status, session/account/tool, workspace/account paths, tmux name/start
flag, empty sandbox/container fields, Native backend/unit/runtime UID and original snapshot/task-record
IDs. The client validates their types and bindings; runtime UID remains an internal field. The
operation bypasses legacy caching and shares the 30-second managed connection cancellation boundary.
`SKILL_START_PENDING` means retained recovery is unresolved; `SKILL_START_STOPPED` means startup ended
and retained state requires finalization. Neither allows replacement execution. Cancellation uses
fresh bounded writer cleanup. Queue dispatch and complete cross-boot task reconciliation remain pending. No backend capability is enabled.

`recover_managed_session` and `cancel_managed_session` accept the same complete original input and
logical request ID. They share managed socket cancellation and bypass generic result caching. With
no launch intent they return exactly status=`not_started`, session/snapshot/task-record IDs and Native
backend. Existing intents require original spec/private-draft authority; corrupt records, directories
and dangling links cannot authorize preparation. Recovery requires current original runtime evidence:
even completed launches must match their saved invocation and remain ready. Historical readiness alone
does not certify a running session; absent/non-running units enter retained finalization and return
`SKILL_START_STOPPED`. Only `start_managed_session` preserves historical success replay independent
of current liveness. Recovery never creates a new invocation. Cancellation checks exact
task/input/runtime binding and original active invocation, then uses common
stop/finalization before returning those five fields with status=`stopped`; this does not delete work
or certify remote persistence. Missing transient specs can use the existing retained finalizer.

The internal worker startup coordinator now holds one snapshot lease across authenticated fetch,
recovery, optional spec/content preparation, peer admission and launch. It recovers before preparing
without mistaking historical readiness for current liveness. Peer admission precedes first launch, and Helper
preparation/launch runtime UIDs must match; UID is stripped before returning a task result. After an
uncertain Helper operation or a success racing lease loss, it independently calls exact cancellation
under a fresh bounded context. Errors stay nonterminal and retain lease-loss/cancellation causes,
including uncertain cleanup. Managed peer context now comes from worker configuration/registration,
with task-supplied broker material removed. Initial peer admission may authorize the trusted UID;
recovery only verifies the original already-admitted session/nonce/UID in the current broker. Repeated
registration, revocation and broker restart cannot create replacement authorization for a live process.
Failed verification drains the original runtime and retains pending state; nonces remain process-local.
Dedicated Native queue integration preserves these distinct admission paths and nonterminal errors.

Managed Native startup confirmation now uses
`POST /node-api/tasks/{logical task_id}/managed-start-result`. Its body is an exact ready or stopped
outcome. Both contain `session_id`, `tool_account_id`, `runtime_backend=native`, canonical
`runtime_resource_id`, `skill_snapshot_id`, `task_record_id` and positive integer `lease_attempt`.
Ready adds `status=running`, `tool_type=claude` and the original `tmux_session_name`. Stopped instead
adds `code=SKILL_START_STOPPED` and the exact message
`Managed startup stopped; skill finalization is pending.` No paths, runtime UID, arguments, nonce,
manifest or file content are accepted. Unknown fields and mixed outcomes are rejected.

Initial confirmation requires active ownership, the unchanged managed task pointer, original reserved
snapshot, starting session and unexpired current attempt. User/session/task locks serialize it with
renewal and lifecycle mutations. It commits the existing Node task result and session transition
together: ready makes the task succeeded/session running and snapshot started; proven stopped makes
task/session failed and snapshot finalizing so the retained finalization path can proceed. Existing lifecycle revocation and retention clocks remain in
that transaction. Terminal replay must exactly match the original receipt and task outcome; it does
not reapply readiness to a later stopped session. Changed attempts or conflicting outcomes fail.
Persisted snapshot references prevent bypass by removing the task marker, and the existing generic
completion/failure routes also enforce this guard for managed tasks.

The dedicated response is a skill envelope with `schema_version=1`, `status=completed`,
`committed=true` and `data` equal to the complete accepted outcome. The Go client validates exact
identity, field completeness and the committed acknowledgement, refuses redirects and does not retry
uncertain writes automatically. A replay is historical Server acceptance, not current runtime liveness.
Native worker reporting retains the startup lease through durable proposal storage and confirmation.
A verified committed receipt wins a concurrent renewal rejection caused by that commit, including
local acknowledgement-write failure. An unknown response retains the proposal and drains the original
runtime. Helper-proven stopped recovery publishes only the bounded stopped result. This endpoint
does not advertise a managed backend.

The existing Node task ledger now publishes private temporary JSON through file sync, atomic rename
and parent-directory sync. Failed publication does not expose a new in-memory outcome. Uncertainty
after rename blocks reads and writes until reopen; the worker must not interpret this as a missing
task. Empty/null/corrupt existing ledgers are errors. Returned JSON values are detached, and integer
metadata retains its exact value through reopen and rewrite. This preserves the legacy disk format;
managed proposals use separate `managed_start_pending` and `managed_start_confirmed` states. Their
schema-1 payload contains only full snapshot binding and exact bounded outcome. Conditional writes
compare the entire saved record, preventing an old acknowledgement from replacing a newer proposal.

`POST /node-api/tasks/{logical task_id}/managed-start-result/inspect` accepts the same exact proposed
outcome and performs a read-only observation under the same user/session/task locks. Its data has
exactly `result`, `accepted`, `current_lease_attempt` and `task_status`. An accepted original receipt
returns status completed/committed true; absence returns unconfirmed/committed false. Conflicting
receipts or authority are errors, never absence. Inspection neither publishes results nor renews
leases, mutates retention clocks or grants runtime authority. Same-attempt absence cannot exclude an
in-flight publication on a live task. A strictly newer poll attempt fences a prior unaccepted
proposal; the worker must still recover the original runtime under the new lease before proposing
its outcome. Exact accepted=false/task_status=cancelled observation also excludes later acceptance
under the same Server locks. Node can retire that original proposal when current_lease_attempt is
at least its original attempt; expiry or an absent receipt alone does not permit retirement.

An independent worker loop inspects pending records even when Server acceptance has ended task
polling. It records an exact already-committed receipt and never republishes readiness or touches a
runtime. Unaccepted records await leased recovery unless the task is exactly observed cancelled.
Then a full-record CAS writes `managed_start_retired`, preserving the schema-1 binding/outcome and
adding `retirement` with that complete exact observation. Pending/confirmed disk payloads are
unchanged. Retired records leave the inspection queue and reject later startup replay; stale
observations cannot replace confirmed or newer proposals. This local bookkeeping is neither Server
acceptance nor writer/retention/cleanup proof, and does not alter independent finalization. Generic
task failure caching cannot consume any of these states. Re-registration made solely to inspect historical acceptance is rolled back without granting
peer access. Already-confirmed runtime recovery after broker restart, complete cross-boot handling
and finalization Helper transfer/worker orchestration/ack/cleanup remain required before managed capability release.

This is control-plane integration, including tests for both backend labels. Account takeover, Node
managed startup coordination, durable upload acknowledgements and real Native/Docker Sandbox runtime
acceptance remain unfinished. No real Node advertises this capability.

## Legacy configuration import ownership

`account import-config --exclude-skills` removes the account-level skills root before preview and
collection and uses the existing request `exclude` field. Server checks all requested include/file
paths under the user content lock. `managed_v1` and `migrating` reject any account-level skills path
with `SKILL_MANAGER_OWNS_PATH` (409) before profile/task/audit mutation. This ownership check remains
active with the skill feature switch disabled. Plugin content and project history are separate roots.

The existing task start endpoint repeats this check for queued imports. Node additionally calls:

`GET /api/v1/node-api/tasks/{task_id}/config-import-authorization`

This uses Node credentials and the external task ID from polling. Only the exact Node's currently
leased/running `import_tool_account_config` task with a live lease, active owner and matching account
and tool may obtain a response. The response uses the normal Node API `data` envelope with:

- `task_id`, `node_id`, `user_id`, `account_id`;
- `directory_mode`: `legacy`, `migrating` or `managed_v1`;
- `directory_epoch`: current positive epoch, or zero if no directory record exists.

No content or host path is returned. Node compares all identities, requires an explicit integer
epoch and known mode, and never trusts a mode from the queued payload. Missing/old Server responses
fail closed; upgrade Server before Node. Node checks the complete batch before any write, including
path safety, ownership, base64 and 1 MiB per-file / 8 MiB aggregate import limits. These existing
configuration limits are separate from skill package/state quotas. Linux/macOS writes anchor the
configured account root and walk account descendants with no-follow directory handles; all existing
targets are checked before any mutation. Symlink aliases, duplicate targets and file/directory
collisions reject the batch. Writes recheck through the anchor, fsync temporary files, atomically
rename and fsync parents; hardlinked old files are replaced without changing their other links.
Other platforms reject safe import as unsupported. Ownership denials retain their
stable code. A denial at start is journaled as failed; completed local tasks replay only their saved
result and never reimport over later edits.

This is a fresh execution check, not a takeover lease. Full takeover must still prevent new imports
under the same lock, drain queued and executing legacy writers, and obtain a local exclusion boundary
before stable capture and directory authority commit. Expired leases or cancelled task status alone
cannot prove writer quiescence. Directory takeover and its drain/local guard remain unfinished;
this endpoint does not advertise a runtime capability.

### Serialized Helper imports and durable account fences

The worker passes fresh authorization to the Linux Helper operation `import_account_config` using
the original external task ID. The strict payload contains `account` (identity, backend and files),
`directory_mode` and `directory_epoch`; it cannot select a host root, UID/GID or remote path. The
Helper chooses its configured account path and existing backend runtime identity. All writes run
under the Helper's existing serialization boundary. Non-Linux Helper execution fails explicitly.

Private SkillStateRoot records bind account fences to Node/user/account and the first nonlegacy
directory epoch. An existing fence is immutable; stale legacy grants cannot reopen it after restart.
Unsafe/corrupt records fail closed. Deleting or relocating private metadata is not a rollback API.
Only account skills are fenced; unrelated configuration remains importable. No fence removal or
public takeover operation is exposed.

Exact-task import receipts store identities, input digest and `started`, `succeeded` or `failed`,
without config bytes. The digest binds backend/files and the Helper-selected account path; fresh
mode/epoch are checked separately so completed retries survive a mode transition. Intent is fsynced
before writes and the terminal result afterward. Success returns its original file result; changed
input under the same task ID is rejected. A nonlegacy grant closes the fence even on completed replay.
Interrupted intent returns `CONFIG_IMPORT_PENDING`; retained failure returns `CONFIG_IMPORT_FAILED`.
Worker reports these stable content-free codes. Neither outcome silently writes again, and terminal
Server task status cannot substitute for inspection of a pending local receipt.

The raw import ceilings remain 1 MiB/file and 8 MiB total. Server and Node also limit the encoded
file list to 12 MiB, including escaped metadata; Server rejects oversize with
`CONFIG_IMPORT_TOO_LARGE` (413) before dispatch. Task polling (one task per response) and Helper import
frames allow 16 MiB; other responses/Helper operations retain 1 MiB limits. Upgrade Server first,
then the worker and Helper together. Include private fence/receipt metadata in consistent backups.

### Legacy runtime writers during account takeover

Existing account binding and backend-migration planning now hold the user content lock from directory
mode inspection through task/account mutation. Nonlegacy mode returns `MIGRATION_PENDING` (409)
before any task, profile, account or audit change, even when managed admission is disabled. These
paths still operate the legacy account directory; managed binding/backend migration require dedicated
snapshot/retention adapters before they can be enabled.

The Helper's account fence rejects delayed Native/Docker launch and binding requests plus backend
migration before filesystem work. Worker task reporting preserves `MIGRATION_PENDING` with a fixed
content-free message. Docker account paths derive from the checked identity, ignoring caller-selected
remote paths; existing account descendants/discovery roots reject filesystem aliases through
no-follow directory preflight. Configured-root aliases remain supported. Native launch also checks
the fence; a managed snapshot still requires the exact private receipt and protected mount. Merely
adding a snapshot ID or mode to a legacy task does not grant managed launch permission.

Completed helper tasks replay saved results without relaunch. Existing session inspection/stops
remain available and no admission guard calls stop/kill. Private metadata reads now use kernel
`openat(O_NOFOLLOW)` on verified private directory handles; dangling links and links to valid records
cannot be mistaken for absent or valid fences. This closes writer admission only. It does not replace
account takeover's required process-group/binding/import drain and stable capture/authority commit.

### Internal first-takeover transaction

Migration `0039_skill_account_takeover` adds a durable initial takeover receipt. This is an internal
Server service contract; no public takeover route, automatic dispatch or Node capability is enabled.
`SkillTakeoverRequest` fixes an idempotency key and the expected legacy directory epoch (zero when no
record exists). Reservation holds the user storage lock and atomically creates `migrating`, the next
epoch, one `takeover_tool_account_skills` task, and the receipt. It never stops existing resources.

The task carries only `takeover_id`, `user_id`, `tool_account_id`, `runtime_backend`,
`directory_epoch`, `inventory_digest`, `protocol_version: 1` and `manifest_version: 1`. The receipt
stores the exact database task UUID separately. It retains a sorted inventory of historical session,
binding, skill-import and backend-migration identities, including terminal tasks. Task records and
Session rows complement each other; the latest profile binding is not a complete history. Unknown
original backends remain null. Inventory contains no config bytes, file lists or host paths. Historical
resources on another Node require reconciliation before reservation.

`SkillTakeoverCapture` binds the exact live task lease, directory epoch, inventory digest, nonzero
Helper receipt UUID, strict `writers_quiescent: true`, and complete manifest. The Server requires all
current relevant resources to be terminal and present in the original inventory. This is necessary
control-plane evidence only: the Helper must close its durable fence, inspect known and locally
unlisted processes/imports, prove actual quiescence and retain a stable original source. These Helper
steps and their task integration remain unfinished.

The first accepted capture fixes its manifest digest and Helper receipt identity. Expired upload
attempts may be replaced only for that identical capture; only the current owner/digest/scope-bound
`account_directory` upload accepts files or completion. Each request rechecks the exact task and
active user. Boolean protocol values cannot impersonate integer versions through JSON equality.

Complete capture bytes, actual skill format, system exclusions and root/per-skill quotas are checked
before publication. One savepoint retains the initial complete directory, account-local skill/revision
identities, branches and members, then changes the exact migrating epoch/null head to `managed_v1`
and records the committed checkpoint. Manual sources stay account-local, including when the user
library has the same name; later session preparation reports `SKILL_SOURCE_CONFLICT`. Invalid new
skill folders remain auxiliary content, including their quota. Empty directories, binary data and
cross-entry links remain part of the complete tree.

Late failure rolls back every new database reference even when the caller catches the exception and
commits. Committed retries return the original checkpoint without restoring a later directory epoch
or head. The database binds tasks to their Node and upload/checkpoint references to their owner,
account, digest and scope; task payload ownership is checked by the service. Any takeover receipt
blocks schema downgrade before mutation. There is no generic reset to legacy or fence removal API;
verified abort/rollback and runtime/CLI orchestration remain required.

### Helper retained capture and internal Native writer inspection

The Node now has an internal Native takeover/capture method; it is not exposed as a Helper socket
operation or worker task. `AccountTakeoverBinding` fixes version, Node/user/account, takeover/task
UUIDs, backend, directory epoch and inventory digest. Nullable writer backend/task fields retain the
Server JSON form; the canonical identity digest has a Python/Go compatibility test. The Helper closes
its immutable exact-epoch account fence before inspection, so waiting does not admit new legacy work.

Native inspection reads all local specs through root-owned, descriptor-relative no-follow handles.
Damaged specs are errors, not skipped entries. It checks historical session/binding units, local
managed units from systemd and leftover managed system.slice cgroups. A main process exit or an
unloaded unit alone cannot prove quiescence. Active writers, populated groups and unavailable or
ambiguous inspection deny capture; the method never issues stop/kill. Same-account incomplete import
receipts also deny capture. Unknown/Docker resource backends, backend-copy history and same-user or
unattributable Docker specs require further reconciliation. Sandbox-wide/orphan-Docker inventory and
backend-copy exit proof remain an integration gate before any public takeover dispatch.

A quiescent source becomes `takeover-<account UUID>/` under independent private SkillStateRoot.
`record.json` contains the exact binding, random Helper receipt UUID, digest and explicit source
existence. `manifest.json` retains the complete original modes, files, directories and portable links;
reserved system paths are excluded. `objects/<sha256>` contains ordinary Helper-owned 0600 copies
under 0700 parents, never hardlinks to mutable account files. Source reads walk every path component
with kernel no-follow flags and reject nonregular files. The source is checked again after verified
copying. Whole-bundle fsync and no-replace rename publish one durable receipt.

The original discovery tree is never removed, renamed or chmodded. A genuinely absent root creates
an explicit empty capture without creating account directories. Retried captures validate the saved
binding, fence and manifest before opening any source; source removal or later edits do not alter the
receipt. Incomplete or corrupt existing metadata cannot trigger recapture. Object streaming is scoped
to the retained manifest and verifies private ownership, modes, links and length; the transfer path
must still verify the streamed content digest before remote acceptance. No successful capture grants
permission to remove originals or reopen the fence. Transfer acknowledgement, verified rollback and
retention are still required.

### Authenticated initial-takeover transfer

The Node-only transport now exposes `/api/v1/node/skill-takeovers/{takeover_id}` under the skill
feature switch. Every call supplies the original database `task_id`; files and completion also
supply the current `upload_id`. Poll envelopes now provide this database UUID as additive
`task_record_id`; the existing logical `task_id` remains the StartTask/result/ledger key. These are
distinct identities and cannot be substituted or inferred from task payloads. There is still no
public reservation or automatic takeover dispatch.

| Method / suffix | Contract |
| --- | --- |
| `GET` | Exact task authorization, immutable identities/inventory and current original receipt; no upload renewal |
| `POST /capture` | Authorize before reading a bounded 64 MiB capture declaration, then reauthorize and require writer drain |
| `PUT /files/{digest}` | Manifest-scoped raw stream, exact length/digest/classification, fresh authorization before storage |
| `POST /complete` | Atomic complete publication and original checkpoint receipt; missing bytes return `CONTENT_INCOMPLETE` |

All state responses use `SkillResult[SkillTakeoverView]`, protocol/manifest version 1, and retain the
original Node/user/account/backend/epoch plus takeover/task IDs. Inventory is capped at 10,000 records.
The response includes its immutable digest, status, nullable Helper receipt/capture digest/upload ID,
upload attempt and nullable original checkpoint. It contains no original file listing, bytes, host
paths or user idempotency key. `committed` is true only in the committed phase. That phase remains
replayable after the exact task becomes terminal, subject to active owner and unchanged task binding;
it does not permit further file writes or Helper/source cleanup.

The Go client validates response binding, inventory hash, versions, phase fields, exact file receipt
and complete capture/upload/checkpoint identity. File bodies are streamed through a bounded content
verifier; successful HTTP alone is insufficient if local EOF, length, digest or classification was
not verified. It refuses redirects, caps responses at 4 MiB, honors cancellation and a 10-minute
request timeout, and does not automatically replay uncertain writes. Existing control-plane calls
retain their response limits. Network access remains in `internal/api`; the Helper FD transport and
worker orchestration are still required before these APIs can execute an actual takeover task.

### Retained takeover descriptors across the Helper boundary

The Helper now exposes read-only `open_account_capture_file` for an **existing** sealed capture.
The existing root-owned socket and peer UID checks remain authoritative. Requests carry the exact
`AccountTakeoverBinding`, `kind` (`manifest` or `object`), and empty object fields for a manifest.
An object additionally requires `helper_receipt_id`, `tree_digest` and `digest`. No host paths,
directory handles or caller-selected execution identity are accepted. This operation never initiates
capture, creates a missing store, reopens the original source, alters the fence or acknowledges cleanup.
Fresh Server task authorization remains the worker's responsibility before the local operation.

Under Helper serialization, retained fence/receipt/manifest scope selects an ordinary private file.
One read-only root-owned 0600 single-link descriptor travels via SCM_RIGHTS with bounded metadata;
the serialization lock is released before the network handoff. The client receives CLOEXEC atomically,
checks type, permissions, ownership, access mode and exact size, and resets its offset. Small metadata
allows up to 32 KiB for legal paths expanded by JSON escaping; complete manifests remain bounded at
64 MiB and travel through the descriptor. Duplicate/oversized/fragmented-invalid frames, extra or
truncated descriptors and identity mismatches fail closed with descriptor cleanup. Normal stream
fragmentation is supported. Direct typed decoding preserves the signed 64-bit directory epoch.

`ReadAccountCapture` validates the complete manifest digest before returning a receipt and tree.
`OpenAccountCaptureObject` returns a reader and declared entry from the same immutable capture;
its caller must verify all streamed bytes and close it. `PutSkillTakeoverFile` already performs both.
A handoff ACK is not a durable Server acknowledgement. Capture initiation, complete backend writer
proof, worker retry/lease orchestration and verified rollback remain required before live dispatch.


### Takeover lease renewal and retained-capture transfer

Poll envelopes additionally carry `lease_attempt`, the positive current `NodeTask.retry_count`.
`POST /api/v1/node/skill-takeovers/{takeover_id}/lease?task_id={task_record_id}` accepts strict JSON
`{"lease_attempt": N}`. Only the active owner, exact task binding, unexpired leased/running task and
current attempt may renew. Pending, expired, terminal and committed tasks cannot be revived. Renewal
updates only the deadline for at most 300 seconds; it does not create a task or upload attempt.
The `leased` / `committed=false` envelope returns takeover/task/Node IDs, attempt, `server_time`,
`lease_until` and `renew_after_milliseconds`.

Polling locks candidate rows with PostgreSQL `FOR UPDATE SKIP LOCKED`; concurrent claimers cannot
lease the same pending row, and a renewal's locked row cannot be overwritten from an earlier deadline.
Capture and file routes release preliminary authorization locks before reading the request stream,
then reauthorize before accepting the complete declaration or storing verified bytes. This lets a
long stream renew without allowing an owner revocation during streaming to pass final authorization.

Node computes a conservative monotonic deadline from request start plus the Server's lease duration,
so request latency reduces the local budget and host wall-clock skew cannot extend it. Subsequent
renewal requests are bounded by the previous budget. Uncertain renewal cancels dependent work and
joins the renewal goroutine; the bounded `TAKEOVER_LEASE_LOST` error is recoverable and must not become
a cached terminal task failure.

The internal transfer coordinator first gets a fresh Server grant, returns an existing committed
receipt without Helper access, otherwise renews before reading the sealed manifest. It begins the
exact retained upload, transfers each unique regular-file digest through a verified Helper descriptor,
and completes the current upload. A verified commit remains authoritative if renewal simultaneously
rejects the now-terminal task. No path deletes retained content or treats a transport ACK as cleanup
permission. Capture initiation, mixed-backend writer proof, durable retry dispatch and rollback remain
unfinished; this coordinator is not connected to public reservation or automatic task execution.


### CLI library queries and status waiting

The CLI now exposes `skill list`, `skill info NAME_OR_UUID` and `skill status OPERATION_UUID` through
the existing user-authenticated `/api/v1/skills`, `/installations/{identifier}` and
`/operations/{operation_id}` endpoints. Tool/account scopes are mutually exclusive; account lists
require `--effective`. These responses describe library rules, not complete runtime discovery or
model loading. Original session/system effective views and account-local configuration
views are described below.

Typed Rust models retain the version-1 result envelope, original operation ID, independent field
origins, revision/source provenance, target readiness and replacement ID. HTTP redirects are refused;
metadata query responses retain the current 1 MiB client ceiling and fail explicitly above it. There is no implicit
truncation; original-session pagination is explicit as specified below. Queries use the existing user credential lifecycle, never device credentials.
JSON emits one envelope on stdout; explanations and bounded diagnostics go to stderr. Terminal text
escapes untrusted control characters. Protocol version/shape and operation identity mismatches fail.

Status inspection without waiting can report pending with exit 0. `--wait` follows the original ID
until a known terminal result or the monotonic `--timeout` deadline (default 60 seconds). Transient
read failures retry within that same deadline. Timeout returns 3 with the last known pending result;
failure/conflict/supersession returns 1, argument errors 2, completion 0 and interrupted waiting 130.
Later refresh rejection or malformed responses append an error while preserving already observed
data and configuration commitment. Timeout/interruption never cancels, resubmits or follows a
replacement operation. Mutation idempotency is described below; explicit retry commands and complete
command coverage remain pending.


### CLI exact-request mutation recovery

CLI rules/removal/rollback call the existing typed `/skills/rules`, `/skills/removals` and
`/skills/rollbacks` routes with stable skill UUID, `expected_generation`, `idempotency_key` and exact
command fields. The first confirmed request is saved in local SQLite before POST. Local recovery is
partitioned by normalized Server URL and fresh `/users/me` UUID; tokens/content bytes are excluded.
A partial unique index prevents replacement of a pending intent by a concurrent process.

A lost response triggers original-key lookup before any repeat POST. Recovery reuses the saved body
and generation, and never interprets a generation conflict as permission to replan. Accepted replies
must match the skill and generation delta. SQLite retains the original operation ID; deployment
readiness is a separate Server state. `skill status --last` reads the latest saved ID/key for the
current login and does not mutate. Authentication/protocol failures are not automatically retryable.
Unknown acceptance is explicit and retains the original key; repeating the same confirmed command
can recover it after connectivity/authorization is restored.

All mutation commands provide `--dry-run`, `--yes`, `--no-wait` and bounded `--timeout`. Dry-run does
not POST or create an acceptance journal row. Noninteractive missing confirmation returns 2. Default
waiting is 60 seconds; pending timeout returns 3, and known failure/conflict remains 1 even when the
configuration is committed. These flows cover library rules/remove/rollback and the account-local
rules below, Git/local-source installation and update ingestion described afterward. Exact
ended-operation retry uses the separate public retry protocol documented below.


### Account-local configuration and shared name resolution

`GET /skills?account_id=UUID&effective=true` adds `data.local_items`, separate from library `items`.
Only active local sources in the exact owned account appear, including disabled entries. Unscoped
and tool lists return an empty local collection. A missing user-library record does not hide local
sources or create a library during a read.

`GET /skills/installations/{identifier}?account_id=UUID` can return a local detail with
`origin=account_local`, stable ID, owning account ID, name/status/enabled, initial revision ID,
source directory checkpoint ID, retained revisions and resolved account rule. Local revisions carry
content digest, subtree prefix and metadata; no Git source/provenance is invented. The existing
library detail shape remains unchanged. Stable IDs can query removed local history; staged candidates
are not public configuration. These views do not establish runtime deployment or model loading.

Name resolution considers library and active local identities together. Within an explicit account,
a library/local name collision returns `SKILL_SOURCE_CONFLICT`; unqualified/tool-scoped names also
reject collisions with the user's owned local sources. A local identity requires its matching account
scope (`LOCAL_SKILL_SCOPE_REQUIRED` without one); another account cannot select it. Full stable UUIDs
resolve the exact source. The CLI queries the original input before writing the resolved ID to its
journal and rejects a mismatched name/UUID response before mutation. Missing local account scope
returns CLI exit 2 for both queries and mutations, without posting a change.

`POST /skills/rules` accepts local enable/disable/inherit(enabled or all) only for the owning account.
Inherit restores enabled=true independently of all library rules. Pin/unpin and revision inheritance
return `LOCAL_SKILL_COMMAND_UNSUPPORTED`; package remove/rollback/update cannot select a local source.
The same user lock, expected generation, savepoint and original-key replay protocol apply. A changed
flag increments configuration generation once, a no-op does not. The operation records the local ID
and exactly its account target. State heads/epochs, directory head/epoch and existing snapshots remain
unchanged; runtime readiness remains independently reported. No schema migration is required.


### CLI local-source installation and content transfer

`skill add LOCAL_DIRECTORY` supports `--list`, repeated `--skill`, `--all`, relative `--path`, tool
or account scope, and the common dry-run/confirmation/wait options. Listing discovers candidates and
issues locally without credentials or network calls. A single candidate selects automatically;
multiple candidates require an explicit or interactive selection. `--yes` never selects candidates.
Explicit subpath descent remains capability-bound and refuses directory links/escape attempts.

All chosen packages are fully copied before preview/confirmation. Captured bytes are immutable upload
inputs; later changes to the source do not alter the plan. Preview includes names, tree digests, byte
and entry counts, scope and expected generation. Local source identity hashes the canonical selected
directory, with no reusable host path in Server metadata. Direct-directory and equivalent `--path`
selection use the same identity. Invalid candidates are reported; selecting all chooses valid ones.

The content client uses the existing `/skills/content/uploads`, `/uploads/{id}`,
`/uploads/{id}/files/{digest}` and `/uploads/{id}/complete` routes. It verifies the exact returned
manifest, tree digest, upload/file identity and persistence state. Complete content envelopes have a
64 MiB transport ceiling; ordinary metadata requests keep 1 MiB. Per-file reads and byte hashing run
on blocking workers. Each unique file digest is sent once per transfer attempt, using captured bytes
with verified size/digest; links and empty directories remain in the canonical manifest.

Within an invocation, uncertain upload creation reuses its original key. Later transient failures
query the known exact upload before resuming, without creating a new plan or reviving an expired
lease. Already committed plans are accepted only with an exact matching manifest. An expired plan
fails with `UPLOAD_EXPIRED`. File persistence does not imply full-tree or installation acceptance.

Only after every selected tree is Server-complete does the CLI send one `SkillAddRequest` to
`POST /skills/installations`. The Server retains its atomic all-item validation and generation CAS.
The exact canonical request is first stored in the existing Server/user-bound `skill_commands`
journal (schema version 4, bounded to 4 MiB to support up to 100 metadata-only items). Shared
acceptance code preserves rule/remove/rollback behavior and validates installation receipt counts,
UUIDs and the exact generation delta. `committed`, target readiness, waits and `--last` remain separate.

If configuration acceptance is uncertain, repeating the same source/selection/scope restores the
saved request before source discovery; missing or changed local files cannot replace it. Relative
source recovery also requires the same working directory. Original-key lookup precedes identical
replay and never refreshes the original generation. Before configuration submission, a process crash
may leave staged or complete unreferenced content but cannot partially install the selection; a new
invocation captures and confirms again, and Server retention handles abandoned staging. No source
bytes, credentials or plain live-source paths enter the local command journal.

Git acquisition and check/update orchestration are described below. These installation paths do not
establish Node runtime deployment, takeover dispatch or model loading.


### CLI Git acquisition

`skill add` additionally accepts GitHub `owner/repo` or credential-free HTTPS Git URLs, with `--ref`
and `--path`. Plain two-component names denote GitHub; use `./owner/repo` for local directories.
No arbitrary web page interpretation or SSH/file transport is enabled. An omitted ref resolves remote
HEAD's symbolic default branch; literal names must unambiguously denote a branch or tag. Explicit
`refs/heads/` and `refs/tags/` disambiguate. Full SHA-1/SHA-256 commits are supported when native Git and
the remote support that object format. Annotated tags peel to the full commit. A ref targeting a
non-commit fails before packaging. The existing Server observation contract rejects moved tags.

`source.kind=git`, credential-free `source.locator`, repository-relative `source.subpath`, and
`provenance={ref_kind,ref,commit}` enter the unchanged installation payload. Default-branch provenance
records the actual branch name, never a moving HEAD alias. Intent metadata includes an optional ref;
its omission preserves existing local journal hashes. Git intent is independent of cwd. Before any
new fetch, pending original-key recovery runs; legacy local-only shorthand journals are checked first
so the new owner/repo interpretation cannot replace an uncertain local request.

Private authentication comes from native noninteractive credential helpers in a private cwd. Only
username/password Basic material is currently consumed. Transport has separate isolated Git config,
HTTPS-only protocols, redirects disabled, TLS verification enabled and URL-scoped authorization in
child environment configuration. Credentials, helper diagnostics and raw Git stderr are never emitted
or uploaded. No credential approval/storage operation or interactive Git login is initiated.

Private bare object storage and raw ls-tree/cat-file batches avoid checkout, filters, hooks and archive
attributes. Portable manifests retain raw binary bytes, execute modes and links on every host. Source
selection shares the local candidate rules; metadata honors internal SKILL.md links. Selected gitlinks
and unresolved LFS pointers reject incomplete content; unselected submodules do not prevent --path
installation. Explicit --path enumerates the selected Git tree directly, without validating unrelated
repository filenames or imposing whole-repository discovery limits on that subtree. Complete packages
and all subsequent content/acceptance behavior use the existing flow.

Git acquisition/discovery and each selected capture have 240-second outer deadlines. Credentials have
30 seconds, ref discovery 60 seconds, fetch 120 seconds and raw-object reads 30 seconds per process.
Stdout/stderr, tree metadata, entries, symlink targets and expanded package bytes have explicit bounds.
Fetch staging checks 512 MiB/100000 entries every 100 ms and once at completion; this sampled disk guard
can overshoot and is not a hard network-byte quota. Unix process groups and Windows kill-on-close jobs
contain descendants for timeout/cancellation; Ctrl-C during Git work reports exit 130. No Node runtime,
takeover dispatch or model-loading claim follows from Git acquisition or installation acceptance.


### CLI check and independent source updates

`skill check [SKILL]` is read-only with respect to Server configuration, content and the command
journal. It fetches and captures complete recorded branch packages before comparing their digests
with the current default revision. Results distinguish up_to_date/update_available/pinned/local_source
and failures. A fixed tag/commit/rollback policy is skipped, and a local installation is reported as
local_source. The recorded branch is explicitly selected; remote HEAD changes and a same-named tag
cannot redirect automatic updates. Source or network failures produce a nonzero exit.

`skill update SKILL` uses a tracked branch; fixed Git policies require explicit --ref. Local sources
require --from with a complete directory and unchanged metadata name. Explicit --from retains the
installed opaque source identity even when another device uses a different local path. Git name/root
changes produce SOURCE_LAYOUT_CHANGED with expected/actual details. Missing Git subdirectories are
distinguished from transport failures. Known moved tags fail locally; the Server remains authoritative
for all retained source observations and independently rejects SOURCE_DRIFT.

The existing POST /skills/updates receives a typed exact request with command=update, skill UUID,
item, stage, switch_tracking, expected_generation and idempotency_key. --stage is single-item only and
does not activate a default, change upstream tracking or mutate account state. Explicit --ref sets
switch_tracking; activation can resume branch tracking after rollback. Captured content matching a
retained revision uses its already-verified Server tree without new content uploads. Fresh content
must complete the normal upload protocol before configuration acceptance. Enabled fields, tool pins
and account pins are not reset. New observations do not rewrite old immutable revision provenance.

Update journal intent includes the original identifier, optional ref, stage flag and a hash of an
explicit local --from path. It contains no source bytes, credentials or reusable local path. Relative
--from hashes include the working directory. Pending intent lookup precedes fresh configuration/source
reads; recovery uses the saved skill, item, key and generation even if the source disappears. Original
receipt validation requires exactly the retained skill, one valid revision ID and the exact generation
delta. The existing SQLite schema and 4 MiB per-request metadata ceiling remain unchanged.

`skill update --all` is a sequence of independent per-skill transactions, not a global transaction.
It forbids --ref/--from/--stage, skips fixed/local sources, continues after individual failures and
returns nonzero for partial failure. Without --yes it confirms each eligible plan separately, after
that skill's complete capture. Each fresh plan reads its own current generation; a rejected or
uncertain submitted request is never silently rebased. Before a fresh listing, pending automatic Git
updates are recovered, including an item removed or pinned after uncertain acceptance. Pending journal
enumeration is exact Server/user scoped, excludes received records and is bounded to 1000 records /
16 MiB. Repeating a batch can evaluate new current items after recovering retained requests; the CLI
does not invent a global batch operation ID or replay completed items under their old keys.

Checks and batches emit one SkillResult v1 envelope with data.items. Each row contains skill_id, name,
status, exit_code and its complete nested result, including its own operation/commitment/errors.
Outer committed means at least one item was confirmed committed; failures are also collected in outer
errors, and any interrupted row takes exit 130 precedence, then failures (1), then pending timeout (3).
All-success checks/batches exit 0. Single update preserves the original operation result envelope;
argument/policy selection failures exit 2. Dry runs produce planned results and no new journal entry.
Their reuse_server_content field describes the plan's upload decision, not fresh retention/lease
proof; recovering_original_request identifies a saved original plan.

Update read/capture/upload/confirmation waits can be interrupted before submitting that item. Shared
configuration submission now also listens for Ctrl-C: it keeps the pending journal, returns unknown
acceptance with original idempotency_key and commit_state=unknown, and exits 130. It does not declare a
rollback or cancel a remote operation. Waiting after observed acceptance preserves commitment and the
original operation ID. Batch results retain earlier item receipts if a later item is interrupted.
--no-wait and --timeout apply independently to each accepted operation.


### CLI account state history and portable export

`skill state list SKILL --account-id UUID` and directory scope use the existing authorized
/checkpoints and /pending routes. CLI `data={selector,checkpoints,pending}` preserves two independent
pages, each with items/next_cursor. --limit defaults to 100 and allows 1–200; --cursor is the checkpoint
cursor, --pending-cursor is the finalization cursor. Pagination does not silently filter to the current
revision or epoch. Pending records explicitly remain source_node/upload_pending/nonexportable.
Both requests must succeed before the CLI emits a successful combined page; they are independent
reads, not a claimed transactionally consistent snapshot of the two collections.

`state info CHECKPOINT_UUID` returns data.checkpoint and optional data.members. --members applies only
to directory checkpoints and accepts an independent name cursor/page limit. Expired metadata remains
queryable with status=state_expired and exit 0; content export still fails with STATE_EXPIRED. Original
checkpoint epochs, current branch/directory epochs, backing directory, parent and source finalization
references remain distinct fields. State queries use user authentication, no mutation journal, and
never initialize a missing branch.

`state diff SKILL --account-id UUID` or directory scope queries the exact selected current head and
returns the Server's CheckpointDiff unchanged. The baseline is explicitly a package revision, local
initial revision or directory checkpoint. Entries contain only path/type/mode/size/digest/link metadata.
The CLI accepts 1–500 paths per page. Continuing with --cursor requires --checkpoint UUID and forbids
current scope/account/skill selectors, so later pages stay attached to the immutable returned head.
No text or binary semantic merge is inferred. Checkpoint identity, sorted path order, page bounds,
next cursors, entry metadata and read-only envelope consistency are checked before rendering.

`state export SKILL --checkpoint UUID --output PATH` infers the checkpoint account unless an explicit
--account-id is provided; directory export requires --scope account-directory --account-id UUID and
forbids positional skill. Exact source ID, account and scope must match. Names resolve via account
skill_info, retaining Server ambiguity rules; explicit UUIDs also support historical identities.
Item dependency_roots require the backing directory checkpoint export (STATE_SCOPE_MISMATCH), even
though the underlying tree HTTP endpoint can return the complete connected dependency unit.

The portable local format is agent-remote-skill-checkpoint-v1:

- manifest.json: the exact complete export manifest using the shared NUL-delimited tree-digest rules.
- checkpoint.json: format, full authorized checkpoint metadata, checkpoint_id, source_tree_digest,
  exported tree_digest, subtree_prefix, dependency_roots and locally_removed.
- objects/<sha256>: every unique file's exact bytes; paths, directories, permissions and ordinary or
  runtime links are represented only in the manifest, never instantiated on the local host.

This bundle retains all content and metadata without requiring host symlink privileges, POSIX names,
or the remote runtime's absolute dependency paths. It is not a prepared runtime tree and cannot be
passed directly as resolve --directory. No source-controlled path participates in local extraction.
Only locally validated fixed digest names are written. The expanded manifest uses the shared signed
64-bit byte-count validation and 100000-entry bound, without a separate 10 GiB export admission
ceiling. Manifest envelopes remain capped at 64 MiB; other metadata at the existing 1 MiB limit. Content streams with bounded
memory, validates exact Content-Length/ETag, file length/SHA-256 and whole-file UTF-8/NUL classification,
and uses a one-hour request deadline plus 30-second header, error-body and stream-idle deadlines.

The absent/empty target is checked before download and again before publication. Files and bundle
metadata are fsynced in private sibling staging, followed by one directory rename after all objects
are verified. Nonempty targets and target symlinks are rejected; no file is incrementally exposed in
the final directory. An explicit locally_removed record may export a verified empty manifest with
metadata, while pending/missing/corrupt/expired content cannot synthesize a successful empty bundle.
The CLI catches Ctrl-C before publication, discards staging and exits 130 with one envelope; after
publication starts it waits for its result. Successful exports report status=ready, committed=false
(remote state is unchanged), the absolute local path, tree digest and unique object count.

This increment does not add conflict queries/resolution, reset/restore/migrate/prune CLI, access to
Node-only pending bytes, or runtime dispatch/materialization capability advertisement.


### CLI reset/restore, durable state acceptance and operation status

`skill state reset SKILL --account-id UUID` and `restore ... --checkpoint UUID` now use the existing
state current/commands contracts. Both accept directory scope instead of positional skill, plus the
common --dry-run/--yes/--no-wait/--timeout options. An item name resolves once via /state/current;
the subsequent preview/actual selector uses its stable source UUID with the complete returned
precondition. No revision, head, directory/installation/state epoch, member set or library generation
is recomputed after confirmation or uncertain submission.

A fresh invocation posts dry_run=true to obtain a complete nonpersisting Server preview before
confirmation. JSON preview data contains request, preview and recovering_original_request; request
includes its recovery key, action, selector, exact expected precondition and restore checkpoint.
Preview distinguishes full-directory changes from each selected branch's own prior content, including
baseline_available=false for expired bytes. Interactive confirmation displays all of this once;
noninteractive mutation requires --yes. A dedicated input-only thread cannot keep Tokio shutdown
blocked on stdin after Ctrl-C and has no authority to submit a command.

The existing secret-free SQLite skill_commands table stores a canonical wrapper:
command=state, request=<exact StateCommand with dry_run=false>, preview_tree_digest=<confirmed tree>.
It keeps the existing schema and 4 MiB record ceiling. Intent hashes have a state domain and bind the
original action, account/scope/identifier and restore checkpoint; waiting/confirmation flags do not
change the intent. No captured checkpoint bytes enter the journal. Complete current/preview/receipt
HTTP envelopes have a separate 64 MiB bound; paged metadata retains its existing 1 MiB cap.

Actual acceptance has an independent typed state path. Receipt validation checks action, full original
selection/precondition, every affected branch and change source, result tree digest, operation ID,
committed/published flags and result checkpoint. A transport failure queries the original state key;
only explicit OPERATION_NOT_FOUND permits an identical POST. Malformed receipts, auth rejection or a
mismatched result cannot trigger re-selection or silent rebasing. Definite business rejection marks
that attempt received; its next explicit invocation may make a fresh plan. Unknown acceptance keeps
the original pending record and emits status=unknown, commit_state=unknown and idempotency_key.
Cancellation stays registered across preview, journal persistence and submission, so an interruption
between phases cannot accidentally continue with a new POST. Submission interruption exits 130 and
never claims rollback. Local receipt-write failure preserves the observed remote commitment.

A recovered normal invocation queries the original receipt before fresh current-state or preview
reads. Dry-run recovery is also read-only: an existing receipt is shown unchanged (and can correctly
be committed=true from a previous invocation); otherwise only the retained request's dry-run preview
is evaluated. This does not acknowledge or rewrite the original local record. Concurrent identical
intents retain the first pending request. Package update --all recognizes and skips valid state
records instead of decoding them as library update commands.

State commands publish within one Server transaction and already return status=published,
committed=true, the original operation ID and new directory checkpoint. There is no additional
Node deployment queue for these receipts; common no-wait/timeout settings do not invent pending
deployment targets or imply control over existing sessions. Reset/restore preserve the existing
Server epoch, detached-late-input, original-content and compatible-restore semantics.

GET /skills/state/operations/{operation_id} now complements the original ?key=... route. Its repository
query filters by authenticated owner and reads immutable response_json; it neither runs the command
nor substitutes current state. The same feature gate and user-only authorization apply. Generic CLI
skill status ID tries this route only after the library route explicitly returns OPERATION_NOT_FOUND;
status --last uses the retained request shape and exact state key directly. State status --wait keeps
the original local deadline across fallback and reports an unavailable receipt if no result can be
observed; it does not claim an unobserved remote operation is pending or rolled back. IDs work across
logged-in devices without the originating local journal. Existing library status/wait behavior remains
on its original typed path.

### CLI conflict history and saved-input diff

`skill state conflicts SKILL --account-id UUID` also accepts `--scope account-directory` instead of
SKILL. JSON data contains selector, publications and migrations. Both pages keep their native summary
shapes, items and next_cursor; --cursor advances publications and --migration-cursor advances migrations.
Each page defaults to 100 records, maximum 200. A name resolves once to a stable source UUID before the
independent page reads. Their snapshots are independent requests, not a combined transactional page.

GET /skills/state/conflicts now accepts optional skill. Server source authorization uses the existing
state selection rules, including account-local identities and ambiguous-name rejection. Saved observed
branches define membership across revisions/epochs; unchanged members remain related to the complete
directory conflict. Repository source filtering precedes pagination and also constrains cursor identity.
Omitting skill retains the existing account-wide API behavior. No schema migration is needed.

`skill state diff --conflict UUID` returns data.kind=publication|migration, data.conflict (full typed
native details) and data.diff (native metadata page). It selects the migration API only after a definite
publication CONFLICT_NOT_FOUND; authentication, transport, protocol and expiry errors cannot trigger
fallback. Publication details show original session snapshot/comparison/finalization inputs, fixed
branches, conflicts, plan revision and choices. Migration details preserve original preparation or
incremental receipt plus exact base/current/incoming/directory inputs and independent live diagnostics.
Current source advancement does not rewrite saved input or automatically recompute the attempt.

Diff --limit defaults to 100, maximum 500. The selected conflict ID and returned --cursor continue the
same saved comparison. Publication cursors are relative paths. Migration cursors retain their native
base64-encoded [attempt,base_digest,current_digest,incoming_digest,path] binding, with 16384-byte bound;
they are never parsed as checkpoint or publication path cursors. The API client validates provenance,
read-only envelopes, UUIDs/epochs, sorted changed paths, manifest entry metadata, independent list pages,
exact diff identity, returned cursor boundaries and saved-digest bindings. No file bodies are loaded.

A successful inspection emits status=ready, committed=false, no operation ID, exit 0; the inspected
record's own conflicted/superseded/resolved status remains in data.conflict.status. Failed/expired reads
remain errors, and Ctrl-C emits one noncommitted interruption envelope with exit 130. Queries initialize
no state, save no choice, move no head, and write no local command journal. CLI resolution/custom upload,
migration mutations and pruning remain subsequent increments; no runtime readiness is implied.

### Upload-free custom-resolution metadata preview

Both conflict domains now expose POST /skills/state/conflicts/{publication_id}/content-preview and
POST /skills/state/migration/conflicts/{migration_id}/content-preview behind the existing skill gate
and user-only authentication. This closes a required protocol gap before CLI resolve can support
--file/--directory --dry-run: the existing verified dry-run requires already uploaded custom bytes.

The new request contains expected_revision, one custom choice, and its exact manifest. It accepts no
file bytes, idempotency key or mutation flag. Canonical manifest digest must match the declared custom
file/directory digest. The conflict is authorized before reading a bounded 64 MiB body, then ownership,
plan revision, active status and saved-input preconditions are rechecked after reception. Existing
choices retain their original content authorization. Overlap replacement and pure resolution use the
same algorithms as actual resolve, with the new manifest supplied only to this in-memory calculation.

The response is status=preview, committed=false, no operation ID. Data includes kind, conflict/account
identity, unchanged plan_revision, proposed_tree_digest, complete in-memory choices, remaining conflicts,
unit and saved current/directory digests. Complete metadata candidates include result_tree_digest and
full directory changes; migration candidates additionally retain exact target_revision_id,
target_modified, target_changes relative to the target's saved current side and original_changes
relative to its original package. Incomplete candidates expose no partial result/diff.

metadata_only=true, content_verified=false and ready_to_publish=false are fixed, separate from
candidate_complete. pending_checks identifies custom_content, source_authorization, quota_admission
and head_preconditions. This preview neither proves file-byte validity nor grants publication rights.
It creates no uploads, trees, scoped grants, plans, operations, checkpoints or file objects. Declared
custom trees retain the existing directory resource limits. Stale inputs fail explicitly and are not
silently recomputed or transferred to a replacement.

Actual resolution schemas and checks are unchanged. A client must confirm the concrete metadata
candidate, complete the exact scoped upload, obtain the normal fully verified dry-run result, verify
it matches the reviewed candidate, then persist and submit its exact resolution request. Neither a
metadata preview nor its digest can substitute for complete content and final source/head validation.
CLI orchestration, content staging, confirmation and durable resolution acceptance are described below.

### CLI conflict resolution and original-receipt recovery

`skill state resolve CONFLICT_ID` accepts exactly one of `--use current|incoming`, `--file PATH`, or
`--directory PATH`. `--file` requires a canonical conflict `--path`; `--directory` forbids it. Scope
comes from the saved attempt. Publication-to-migration identification falls back only on a definite
`CONFLICT_NOT_FOUND`, never authentication, transport, expired-input or protocol errors.

Fresh preview JSON keeps one outer noncommitted `preview` envelope. Its `data.source` is the typed
saved publication/migration conflict and its full provenance. `data.verification` is `metadata` or
`verified`; `data.preview` is the native typed preview envelope. Migration views retain all target,
original-package and full-directory changes, the exact target revision and modified flag. Choosing
an old incoming side cannot claim an untouched new package revision.

Local runtime capture is distinct from package capture. It includes `.git` entries, preserves
LFS-looking text as ordinary bytes, streams large/binary files, records empty directories and portable
modes/relative links, and verifies descriptor identities plus a final complete rewalk. File input
becomes one ordinary `content` entry. Limits are 1 GiB item/file or 10 GiB full directory and 100000
entries; Server quotas remain authoritative. A local absolute symlink cannot supply the required
runtime dependency identity and fails with `RUNTIME_LINK_METADATA_REQUIRED`; no dependency is inferred.
Recognized checkpoint export bundles are rejected as `--directory` input, not silently interpreted.

For custom input, metadata preview uploads no file bytes or mutation key. After exactly one
confirmation (or --yes), conflict-scoped upload consumes only the fixed staged objects. HTTP file
bodies use 64 KiB chunks, backpressure, exact Content-Length and a bounded one-hour transfer timeout.
The completed upload is storage acceptance only. A normal verified resolution dry run must match the
reviewed choices, complete candidate digest and migration overrides before an actual choice is
journaled. Verification drift returns `RESOLUTION_PREVIEW_CHANGED` without submitting the choice.

The shared local journal uses command `state_resolution` and retains exact domain/attempt, actual
request, prior choices, reviewed verified outcome and original conflict provenance. Intent hashing
binds method, path and local input argument (relative to its original working directory); file bytes
and local source paths are not retained in request metadata. The existing 4 MiB record limit applies.
Acceptance is synchronous: committed `pending` means a saved incomplete plan, committed `published`
means an atomic checkpoint publication, and committed `superseded` means the old requested choice was
not applied. Pending/superseded exit 1; published exits 0. --no-wait/--timeout do not invent deployment
work. A stale response must retain the original plan revision and prior choices; a normal receipt
must match the reviewed result and identities apart from assigned operation/checkpoint IDs.

Pending recovery precedes all source-file reads and fresh conflict selection. It queries the original
key; only a nonretryable, noncommitted `OPERATION_NOT_FOUND` with no operation ID permits identical
replay. Unknown/mismatched acceptance preserves its key with commit_state=unknown, including exit 130
on submission interruption. Planning interruption saves no resolution choice; confirmation interruption precedes content upload.
Custom content capture is cooperatively cancellable. Recovery --dry-run only queries or re-previews the original
request and does not acknowledge its local record. A previously committed receipt can consequently
be shown during a later read-only invocation. Package update --all skips validated resolution records.

Added user-only GET endpoints alongside existing key lookup:

- `/api/v1/skills/state/resolution-operations/{operation_id}` returns the original publication
  `SkillResolutionView`.
- `/api/v1/skills/state/migration/resolution-operations/{operation_id}` returns the original
  `SkillMigrationResolutionReceipt`, with current migration diagnostics separate from its result.

Repositories filter by authenticated owner and ID. Queries never execute, replan or modify a choice;
internal migration draft receipts cannot masquerade as full resolution operations. CLI `status ID`
tries library, state command, publication resolution and migration resolution domains only after an
explicit operation miss. `status --last` routes by journal tag/key. Resolution command/status data use
`kind=publication|migration` and `result=<original native result>`; migration queries additionally
return `current` diagnostics. A status wait keeps its original deadline across domain fallback.

### CLI explicit incremental migration

`skill state migrate SKILL --account-id UUID --from-revision REV --to-revision REV` accepts a
revision UUID, `rN` or positive registration number. Both versions must be different revisions of the
same active installation. There is no implicit directory scope or rule change. The CLI first queries
`/state/migration/current`, then resolves the skill and both revisions to stable UUIDs for all preview
and actual POSTs to `/state/migrate`. Full source/target heads and epochs, installation epoch, library
generation, directory head/epoch and last successful migration remain in `expected`.

A preview retains the native `ready|conflicted` status, `committed=false` and no operation ID. It shows
`old_original|last_migrated`, `target_original|target_published`, `source_published`, all three digests,
target `changes` and independent `directory_changes`; a conflicted preview has no partial result.
Preview ready exits 0; determined conflict exits 1. Before actual submission, a single confirmation
(or explicit `--yes`) authorizes either full publication or retaining a complete conflict for later
resolution. Noninteractive missing confirmation exits 2. Synchronous acceptance has no Node deployment
queue, so common `--no-wait`/`--timeout` options do not turn a determined conflict into success.

The schema-4, 4 MiB shared metadata journal has a distinct `state_migration` tag containing the original
selector, exact stable request (`dry_run=false`) and reviewed preview. Recovery finds pending intent
before any fresh branch query. An original-key lookup may authorize identical replay only on explicit
nonretryable/noncommitted OPERATION_NOT_FOUND without an operation ID. Corrupt or mismatched acceptance
keeps its original key with `commit_state=unknown`; it never selects new heads. Receipt comparison
ignores only Server-assigned operation/checkpoint/sequence fields and validates those fields against
publication status, original sequence and no-change behavior separately. A recovery dry run only
queries or re-previews the exact original request and never acknowledges the pending local record.
Ctrl-C before journaling makes no new submission; after journaling it retains unknown acceptance and
returns 130. Batch package updates skip validated migration journals.

Mutation output normalizes the accepted view into the receipt shape `data.result` plus
`data.current_status`, `replacement_id`, `superseded_reason`. Outer status denotes current status;
the original view is immutable even when a conflict has since been resolved or superseded.
`GET /state/migration/operations/{operation_id}` adds owner-bound ID queries alongside the key endpoint.
Both reject preparation identities with OPERATION_KIND_MISMATCH. Generic CLI status falls through
library/state/publication-resolution/migration-resolution to incremental migration only on definite
not-found results, while `--last` uses the saved command tag and original key. Ready receipts exit 0;
conflicted/superseded receipts exit 1. Queries retain the original waiting deadline and never execute
the migration.

Exit-code correction: accepted incomplete resolution plans (`pending`) and `superseded` resolution
receipts also exit 1, per design section 4.6. They are determined conflicts or supersession, not
argument errors (2) or a pending deployment timeout (3).

### Internal retention protection analysis

Server now has an internal, read-only `SkillRetentionInspector` and an explicit owner-scoped reference
index. Its semantic closure protects active library defaults, package pins, current account branches
even when disabled, applicable branch pins, local initial content, active snapshots, pending inputs,
unresolved publication/migration comparisons and authorized custom trees, current-epoch latest
incremental baselines, pending takeover and live upload leases. Logical package/state objects point
to a shared owner/digest blob, so category retirement cannot imply permission to delete shared bytes.
Pending library operation references require fixed saved revision IDs; unknown operation shapes fail
analysis rather than producing a partial protection result.

Ordinary parent history and effective-use history do not propagate permanent content protection.
Current directory members are returned separately as mandatory compaction obligations. Complete
directory contexts held by snapshots/finalizations/conflicts/local original content continue to
protect their member checkpoints. This distinction is necessary before retiring a historical branch
still materialized in the current directory; it is not permission to edit an immutable directory.

The index bounds total rows and checks required JSON size before decoding; unrelated large metadata
is deferred. Graph size limits fail the entire analysis and invalidate further use of that graph.
New skill reference tables, including foreign-domain consumers of skill FKs, require explicit
classification. This internal inspector does not expose prune, update retention clocks, retire
references, release quota or delete blobs. Default deadlines, transactional clock updates, atomic
history/directory retirement, durable deletion/retry and CLI/API wiring remain required.


### Internal transactional history clocks

Migration 0040 adds `retention_released_at` to seven Server history identity tables. Existing writes
now update last-release and reacquisition clocks under the same owner lock/savepoint as their root
changes, including runtime session lifecycle results. Existing wire receipts remain unchanged.
Nested mutations coalesce their protection analysis; rollback discards both domain and clock changes.
Preview and status reads do not start clocks or infer missing legacy release times from creation.

Internal history diagnostics combine current protection with ordinary/archive policy (30/90 days by
default), retaining old-epoch archive classification after reinstall. They are not yet public info/
status fields or prune authorization. Current-directory materialization obligations, explicit content
reference retirement, exact object lease expiry, quota settlement, two-phase physical deletion,
reviewed prune commit and CLI integration remain pending. See Server `docs/skill-retention.md` for
schema and boundary details and the implementation tracker for PostgreSQL and full-gate evidence.


### Internal history content retirement

Migration 0041 preserves historical digest/identity evidence while allowing explicit retirement of
snapshot/finalization/publication/preparation and associated custom-choice content references.
Stored generated retained-digest columns maintain the actual foreign keys. Existing live reads and
original operation receipts keep their prior shape. After retirement, comparison side tree_digest
fields use their existing nullable form; diff/export/new resolution return STATE_EXPIRED even if
another retained object has the same digest. Original-key receipt and upload-status recovery continue
to return original metadata, without promising expired content remains downloadable.

The internal service accepts exact identities in one account, validates hard roots, deadlines,
retained parent histories and active input transfers, and applies the whole set in one savepoint.
This is not a public prune API or content GC. Checkpoint retirement, directory compaction, reviewed
CLI confirmation/recovery, quota settlement and physical deletion/reuse remain unfinished. See Server
`docs/skill-retention.md` and the implementation tracker for the exact schema and validation evidence.

The internal history transaction also supports checkpoint retirement using existing retained content
and branch expired fields (no schema or public API addition). Historical branch heads retain their
identity after retirement. Existing checkpoint views expose retained=false/storage_location=expired;
current selection exposes expired=true after that version is selected again. Preparation and snapshot
reservation return STATE_EXPIRED until an explicit reset/restore establishes new content. A retired
checkpoint cannot be exported/restored merely because another reference retains identical bytes.
Retained comparison inputs, directory members and backing contexts must retire together or block the
selection; current-directory compaction and public prune remain pending.

### Internal directory compaction

The Server can now preview and atomically apply compaction for exact account-owned historical item
checkpoint identities. This is an internal service, with no new HTTP route or public command. It
creates equivalent views for affected current/backing directories and heads, preserves all old audit
identities and exact baseline/snapshot inputs, and leaves linked or otherwise protected roots intact.
The plan compares original heads/epochs, library generation, members, manifests and intended results;
apply revalidates it under the same user lock. Existing history/view schemas continue to describe the
resulting checkpoints. Compaction itself neither retires history nor promises quota/physical savings.

A future public prune command must add durable original-request/receipt recovery and reviewed loss
selection, then compose compaction, history retirement, quota settlement and recoverable physical GC.
The internal apply method alone is not a wire-level idempotency contract.

### Public state prune confirmation and receipts

The authenticated, feature-gated Server surface now adds:

- `POST /skills/state/prune/preview`: `selector`, `all_unreferenced` (default false), optional
  `cursor`, and `limit` (1–100). Each response contains `summary`, continuous `offset`, complete
  `total`, bounded `rows`, `next_cursor`, and an optional final-page `confirmation`.
- `POST /skills/state/prune`: only `idempotency_key` and the original `confirmation`.
- `GET /skills/state/prune/operations?key=...` and `/operations/{operation_id}`: immutable acceptance.
- `GET /skills/state/prune/operations/{operation_id}/entries?offset=...&limit=...`: complete original
  disclosure, with actual replacement checkpoint IDs after acceptance.
- `GET /skills/state/prune/operations/{operation_id}/progress`: current progress of the original
  linked deletion tasks, separate from the original acceptance.

All paths have the existing `/api/v1` prefix and `SkillResult` envelope. Preview is uncommitted;
acceptance and its queries retain status `accepted`. No new runtime capability is advertised.
Every page binds the authenticated owner, stable source/account selector, fixed cutoff, wait mode,
and a versioned streaming digest of the entire internal plan. Subsequent requests must echo the
canonical selector and mode. Changed facts return `HEAD_CHANGED`; malformed or wrong-owner/stage
credentials return `INVALID_REQUEST`. Clients must traverse and validate all offsets, totals and the
unchanged summary before displaying a final confirmation prompt. A page cursor cannot execute prune.

The discriminated disclosure rows are `history`, `dependency`, `compaction`, and `member`. They
include every candidate and dependency, selected loss groups, direct/propagated blockers, protection
and deadlines, changed directory/item views, and removed/blocked members. File bodies and complete
manifests are excluded from these bounded rows. The opaque plan digest still covers full manifests,
graphs, leases, amounts and lifecycle claim identities. Each response stays below the CLI's 1 MiB
response bound; the final command stays small regardless of the number of histories.

New commands verify the final signature and rebuild the whole plan under the owner storage lock.
Compaction, retirement, claims, quota settlement, deletion tasks, original receipt and every detail
row commit together. A known exact key/request returns the saved receipt before signature checking,
retention graph loading or content access; a different request under the same key returns
`IDEMPOTENCY_CONFLICT`. Queries and accepted replays survive deleted input and signing-key rotation.
Missing or foreign operation lookups return `OPERATION_NOT_FOUND`.

The immutable receipt includes `operation_id`, original `idempotency_key`, status `accepted`,
`confirmation_fingerprint`, the original `summary`, and `disclosure_rows`. It never stores the raw
signed confirmation. Progress separately reports pending/completed/retrying task counts and
pending/deleted physical bytes. Acceptance releases logical quota as specified by the summary;
it does not claim disk deletion has finished. Schema 0045 preserves the original rows independently
of expired content; terminal receipt metadata is not a GC root.

The CLI implements `skill state prune [SKILL] --account-id ID`, explicit `--scope account-directory`,
`--all-unreferenced`, dry-run and one final confirmation. Disclosure order is part of this protocol:
history rows come first, strictly ascending by `(history.kind, history.id)`, without duplicates.
The first appearance of each selected group follows contiguous group numbers starting at one.
Dependency and compaction/member rows follow history rows. Accepted details preserve that original
order and only add actual replacement identities. Clients check complete selected/blocked/group and
compaction counts against the fixed summary before confirming or displaying a recovered result.

CLI display uses a private temporary spool capped at 2 GiB and reads one row at a time; it does not
inflate the 4 MiB request journal. Exceeding the spool bound fails the entire preview. A fresh JSON
dry run returns one envelope with `data.summary`, `disclosure_rows`, complete `rows`, and
`recovering_original_request=false`. Actual commands show the full review on stderr even with
`--yes`, followed by one small receipt envelope on stdout. The final confirmation is never printed.

The `state_prune` journal binds the supplied selector/early flag, canonical reviewed summary/count,
exact compact command and its original key to the authenticated user and Server. Its scoped
confirmation credential is retained privately as command metadata; it is not a login credential.
Recovery precedes any fresh preview. Only definite original-key `OPERATION_NOT_FOUND` allows identical
replay. Invalid/mismatched receipts and authentication/protocol uncertainty preserve the pending key.
Pending dry-run recovery only queries acceptance: if absent it returns explicit unknown acceptance,
the saved summary and `disclosure_available=false`, without POST, replanning or claiming a full list.
An already accepted recovery dry-run can show the immutable receipt; full saved rows are available
through status. `update --all` skips validated prune journals.

Generic status by ID falls through older operation domains only after definite not-found; `--last`
routes directly from the journal. Its JSON `data` is `{receipt, deletion_progress, disclosure_rows,
rows}`. All original details and current progress are validated before rendering. Pending plus deleted
physical bytes must match the original receipt. `accepted` is terminal logical cleanup and does not
assert disk-worker completion. Command waiting flags do not wait for physical deletion. Status
`--wait --timeout N` bounds the complete read/display, never resubmits. Ctrl-C exits 130; before
submission it sends no command, while interrupted acceptance retains the original pending key.
Cancellation or timeout during streaming may leave partial output and exits without appending another
envelope or waiting for a blocked pipe. Native/Docker runtime acceptance remains a separate task.

### Current storage and retention diagnostics

`GET /api/v1/skills/storage` requires the same active user token and feature gate as other skill
queries. It returns an uncommitted `ready` envelope with current user-wide `scope="user"`, UTC
`observed_at`, `package_bytes`, `state_bytes`, `package_reserved_bytes`, `state_reserved_bytes`,
the complete configured storage `policy`, and `node_storage="not_observed"`. `deletion` contains
pending/retrying/completed task counts, `pending_file_bytes` and `cumulative_deleted_bytes`.
Reservations remain separate from logically charged retained objects. Policy reductions may leave
usage above configured limits; the observation must not clamp or reject that genuine condition.

Physical aggregation counts one task per file lifecycle, even when a file belonged to both package
and state categories. Completed bytes sum recorded sizes of completed tasks across distinct deletion lifecycles; re-uploaded
content may later be counted again. Neither logical quota release nor cumulative deleted bytes
asserts available disk space. Node filesystem capacity and session copies remain a separate domain.
The observation reads persisted counters/tasks without expiring uploads, creating missing usage
rows, incrementing lock versions, reading file content or invoking deletion. Production PostgreSQL
owner locks serialize it with new reservations/reference changes and physical worker transactions.
This storage diagnostic increment adds no schema migration (its baseline was 0045).

Existing installation/local-source detail adds optional `storage` and per-revision `retention`.
Checkpoint detail adds optional `storage` and `retention`. Lists may omit these observations (or
return null). Retention binds `kind` (`revision`, `local_revision`, `checkpoint`), exact `id`,
`observed_at`, `retained`, `state`, sorted `protected_by`, `archived`, actual `retention_days`,
`released_at` and `expires_at`. It reuses the complete current protection graph and recorded clocks;
creation timestamps cannot substitute for missing release evidence.

States are `protected`, `waiting`, `due`, `release_unknown` and `retired`. Protected/retired histories
have no effective deadline. Unprotected retained history with no recorded release remains unknown;
otherwise its release plus the configured ordinary/archive days determines waiting/due. Due is an
observation about that object's own waiting period, never a retirement/deletion grant. Full prune
candidate/dependency review and transaction revalidation remain necessary. Diagnostics are current
observations and never modify or become part of an immutable accepted operation receipt.

The CLI exposes `skill status --storage` as a read-only query mutually exclusive with operation ID,
`--last`, `--wait` and explicit `--timeout`. It writes no journal. Existing info/state-info render
provided diagnostics and retain their existing JSON shape with additive fields. New CLI versions
accept older detail responses without those fields, without inventing zero usage or infinite
retention. Typed validation rejects wrong historical identities, inconsistent retention/physical
states and invalid policy limits, while accepting real over-quota usage. Ordinary 1 MiB metadata
response limits remain unchanged.

### Effective accounts and original session selections

`GET /api/v1/skills?include_system=true` adds `system_items`; effective queries include those rows
inherently. Each system row has `name`, `origin="system"`, `read_only=true`, nullable `selected`,
`selection_reason` and a bounded `release` map. Current configured releases do not establish Node
readiness. Device selection is false when disabled and conditional until actual startup capability
selection otherwise. Original-session system rows use only the saved release references, with
`selected=true` and `selection_reason="session_snapshot"`; old string references remain explicit
`legacy_reference` values. They are never upgraded to the current configured release in a query.

Account list rows and account-scoped installation/local info add `account_state`. It contains exact
`account_id`, `revision_selection_reason` (`account_pin`, `tool_pin`, `user_default`,
`account_local_revision`), `directory_mode`, optional directory epoch/checkpoint, selected state
ID/epoch/checkpoint, `state_expired`, and `preparation` (`initialized`, `uninitialized`,
`migration_required`, `state_expired`). The selected rule's revision is authoritative; another
revision's old head is never substituted. Disabled selections retain honest stored-state diagnostics.
Separate publication/migration conflict counts and latest IDs cover the source across revisions and
epochs, without claiming all historical conflicts block current startup. `last_recorded_sync_at`
reports known content persistence evidence; `unknown_sync_times` separately acknowledges older
persisted finalizations with no recorded time. Queries do not prepare, reserve, initialize or dispatch.

`GET /api/v1/skills/sessions/{session_id}?limit=100&cursor=ENTRY_NAME` returns a user-owned original
selection page in an uncommitted `ready` envelope. Limit is 1–200 and cursor must be an original member
of that exact snapshot. `basis="session_snapshot"` includes original session/account/snapshot IDs,
snapshot status and current content retention, fixed backend, library generation, directory epoch,
starting checkpoint, immutable tree digest, saved system references and `items`. Each member preserves
original name, source kind/ID, revision, installation/state epoch, state and checkpoint IDs, current
checkpoint retention and saved field-by-field `resolution`. `next_cursor` is the last returned member
name when more members exist. Ordering and cursor comparison use explicit byte collation, independent
of PostgreSQL language defaults. No query applies current rules/heads to the original selection.

Snapshots remain owner-queryable after session deletion or content retirement. A live owned session
without a saved snapshot instead returns `basis="legacy_unrecorded"`, empty members/systems and null
snapshot facts. Missing/foreign identities return `SESSION_NOT_FOUND`. Both views explicitly retain
`project_discovery="not_inspected"` and `model_loaded=false`. CLI exposes this as
`skill list --session ID --effective`, with session-only `--limit` and `--cursor`; session/account/tool
scopes are mutually exclusive. Missing optional ordinary list/info diagnostics stay compatible with
older Servers. Session queries require the additive endpoint; all metadata responses retain the 1 MiB
bound. Original query results never create journals or runtime authority.

Schema 0046 adds nullable `skill_finalizations.persisted_at`. It is assigned exactly once on successful
complete-content finalization, atomically with its incoming checkpoint, and cannot coexist with
`upload_pending`. Old rows remain unknown; created_at/updated_at are not substitutes. Replay,
publication and retirement preserve the timestamp. Downgrade locks the finalization table exclusively
before checking and refuses any recorded value before schema changes; concurrent completion cannot
insert evidence between that check and column removal. The storage diagnostics increment itself added
no migration; its combined head was 0046. Configuration plans below extend the head to 0047.

### Configuration preparation interruption

CLI add and rule/remove/rollback commands now separate cancellable preparation from exact-request
acceptance. User authentication, original-request lookup, source selection/capture, confirmation and
package upload cannot submit configuration or create a mutation journal themselves. Ctrl-C exits 130
with the existing `SOURCE_INTERRUPTED` code before acceptance. Already uploaded bytes can remain
staged or stored, and an older journaled operation remains independently queryable; interruption is
not a content deletion or rollback request. Update authentication and confirmation use the same input
and scoped signal primitives.

Interactive selection input is bounded to 8192 bytes; confirmation input to 4096 bytes. Detached
input/output-only threads do not hold HTTP/journal/submission authority. One scoped Ctrl-C listener
survives phase boundaries and local journal writes. After the handoff, cancellation is observed before
polling configuration POST. Uncertain acceptance retains the original key and `commit_state=unknown`
with `SKILL_INTERRUPTED`; verified responses retain their known commitment even if local receipt
persistence or waiting overlaps interruption. Human configuration/update cancellation exits 130 without
appending terminal output; JSON preserves the corresponding envelope. Existing original-key recovery
and `status --last` behavior remain authoritative.

Source catalog and configuration dry-run output are handled by output-only workers. Interruption
while display is in progress can leave partial output, exits 130, and never appends a second JSON
envelope or waits for an unread output pipe. Display cannot acquire submission authority. This
increment does not implement ended-operation `skill retry` or advertise runtime deployment support.

Final configuration acceptance and single/batch update results use the same output-only boundary.
Ctrl-C during blocked stdout/stderr exits 130 with no second envelope. Final output has a 250 ms
drain allowance after the retained signal, including when that signal predates the interruption
diagnostic itself. Output may be partial. Verified receipts are journaled before display;
`skill status --last` still retrieves the original operation without another configuration POST.

### State review and receipt output interruption

CLI state reset/restore, migrate and resolve retain one command-scoped Ctrl-C listener across
preparation, exact-request journaling, submission, local receipt persistence and rendering. Their
acceptance paths check the retained event before polling an actual POST. Known Server responses are
validated and recorded before final output; a signal during SQLite receipt persistence does not turn
known commitment into unknown acceptance. Uncertain submissions keep their original key and request.

Interactive review metadata uses detached stderr-only workers with no upload/journal/submission
capability. Cancellation before acceptance exits 130 with `SKILL_INTERRUPTED` in JSON, provided result
streaming has not started; human mode adds no further terminal output. Prepared resolution uploads
may remain stored. Existing cooperative custom-capture cancellation remains in force.

Dry-run and final result workers share the irreversible result-start marker and 250 ms drain allowance
with configuration output. A blocked stdout/stderr cannot prevent cancellation; output may be partial
and no second envelope is appended. `skill status --last` can retrieve the original verified receipt.
State query/export and prune cancellation retain their separate implementations and require their own
remaining output audit; this is not a claim that every command output path is covered.

### Backend migration copy phase

New Node backend migrations retain private copy intent before launching a Helper-selected systemd
service. Copy-phase outcomes are independent of complete migration outcomes. `STATE_COPY_PENDING`
means the retained task cannot safely resume from available evidence; `STATE_COPY_FAILED` means the
copy phase failed after its writers were proven drained. Neither code authorizes replay, cleanup,
rollback or takeover. Worker task results preserve only the stable bounded code/message. No new
public skill API, task dispatch or runtime capability is introduced by these local records.
Historical backend tasks and local copy-only histories remain insufficient for takeover until the
whole migration, including ownership/ACL subprocesses, has durable exit/recovery evidence.


### Backend migration terminal evidence

The Helper now records whole-migration started/succeeded/failed evidence bound to the exact copy
intent and execution configuration. Copy and each target/rollback ACL service require independently
observed terminal unit state and an empty cgroup. Unknown target writers forbid rollback; unresolved
local history also blocks replacement tasks. Filesystem sync of account and backup precedes terminal
persistence. Exact completed input replays the retained result without account mutation, even when
a later takeover has fenced legacy admission. Changed inputs cannot reuse that receipt.

`STATE_MIGRATION_PENDING` retains interrupted or unverified work for recovery;
`STATE_MIGRATION_FAILED` replays a known whole-migration failure. Failure does not certify successful
rollback. Public errors stay bounded and content-free. These records do not authorize backup cleanup.
Native takeover's backend-writer check requires both terminal migration evidence and its original
completed copy; historical, copy-only and damaged records still fail closed. Docker/session/orphan
proof, started-task recovery and public takeover dispatch remain separate outstanding integration.

### State query and export output interruption

State list/info/diff/conflicts/export preserve one Ctrl-C event through authenticated reads and
success/error rendering. Rendering uses output-only workers with the shared 250 ms cancellation
drain allowance. Interruption exits 130, can leave partial output, and never appends a second result
envelope. It does not create a command journal or issue remote mutations. Before local export
publication, cancellation discards staging. Once publication starts, its outcome is observed; an
already-published verified bundle survives cancellation during final display. General skill
list/info/check/status and prune still require their remaining separate cancellation/output audit.

### Docker Sandbox lifecycle compatibility prerequisite

Backend availability cannot be inferred from `docker sandbox --help` returning zero. The installed
Docker version inspected during integration returns a removal notice with that status, while ordinary
Docker still works. Node now requires bounded, command-specific create/exec/rm usage before advertising
legacy Docker Sandbox compatibility. New binding/session starts recheck before account/workspace
mutation. Stop and batch cleanup preserve the trusted runtime spec when those commands are unavailable,
returning `CAPABILITY_UNAVAILABLE` instead of treating a no-op `rm` as confirmed removal. Existing
completed task receipts remain historical replay and do not start processes again.

This compatibility check does not prove sandbox-wide quiescence. The standalone sbx product is a
separate API; mixed-backend capture and managed Docker capabilities remain disabled until an explicit
adapter and real sandbox writer/mount/finalization acceptance are completed.

### Original configuration deployment plans

Server migration `0047_skill_deployment_plans` records each new library operation's original
target binding and complete effective library/local selection. New per-account receipts add the
optional `plan_digest`; old receipts may omit it or return null. CLI JSON preserves a supplied
digest. Source selection includes disabled sources, exact account pins and installation epochs.
Normalized composite foreign keys enforce owner/source/revision identity; the canonical digest
also binds the operation, generation, account, node, tool and backend. Idempotent replay and status
verify the saved plan without recomputing later rules or fetching upstream.

Pending or retryable terminal operations retain all original revision dependencies. Supersession
releases these references through the existing retention-clock transaction. Missing targets,
changed digests or unknown plan versions fail closed before collection. Historical operations
remain explicitly without a plan; there is no current-configuration backfill. Downgrade refuses
to discard recorded plans. These are configuration inputs, not runtime snapshots. Durable target
attempts, ended-operation retry and runtime dispatch remain outstanding; readiness and capability
advertisement are unchanged.

## Native normal stop and durable saving status

A managed stop task uses the existing `stop_tool_session:<session UUID>` logical identity and
adds `skill_finalization` to the ordinary stop payload:

```json
{
  "snapshot_id": "original snapshot UUID",
  "task_id": "original preparation task-record UUID",
  "user_id": "original owner UUID",
  "account_id": "original account UUID"
}
```

This marker is separate from `skill_manager` startup dispatch. Any case alias or malformed marker
cannot fall through to legacy permanent failure caching. Native dispatch validates the original
identity, stops managed writers, then requires a full object-backed frozen reconciliation record
or independently validated capture-pending observation. A capture error from the stop call alone
never proves writer exit; fresh reconciliation is required even after that call fails.
A Helper stop map or missing transient spec alone never proves completed saving. The worker then
makes a cancellable 10-second saving attempt, including waiting for its shared transfer gate. That
gate and the single lazy-opened finalization ledger are pointer-owned across Worker copies and the
independent background inventory loop. Runtime admission ownership is released before the transfer
gate, preventing inversion with background admission observation. No saving network request precedes
writer stop and the applicable fresh Helper observation.

The immutable stop task result contains exactly `status="stopped"`, `session_id`,
`runtime_backend="native"`, `skill_finalization_operation_id` (original snapshot UUID),
`incoming_digest`, and boolean `unclean`. It does not cache a saving phase. Generic Server completion
locates the original snapshot from the logical stop identity even if the marker or payload is lost;
changed payload identities cannot bypass managed validation. Completion requires the separately
committed exact termination observation and identical original classification. A pending-capture
process result has a null incoming digest; its exact replay remains valid after later frozen upgrade.
A supplied digest must match the retained frozen identity. Until that
observation arrives the task remains pending. Exact accepted replay has no lifecycle side effects;
unclean completion preserves `interrupted`. The background transfer remains independent of stop
redelivery and retains its original input/key after any foreground timeout.

Single-session responses (create, detail, current project and stop) add nullable
`skill_finalization_operation_id`; legacy sessions return null. Collection responses do not resolve
this optional detail. `GET /api/v1/sessions/skill-finalizations/{operation_id}` uses the existing
session user/device bearer authentication and original snapshot owner. Node tokens are rejected.
It remains a read-only metadata query even when new managed admissions are disabled and after
session deletion. It returns the ordinary session envelope `{data, request_id}` with:

- Original `operation_id`, `session_id`, `account_id`.
- `process_status` from the optional display session, or `deleted`.
- `process_stopped`, true only with a retained exact termination observation.
- `status`: `awaiting_node`, `capture_pending`, `local_durable`, `upload_pending`, `persisted`, `persisted_unclean`,
  `published`, `conflicted`, `detached`, or `superseded`.
- Nullable `unclean`, `finalization_id`, incoming `checkpoint_id`, latest `publication_id`.
- Nullable `capture_error`, one of the four finite causes only while status is `capture_pending`.
- `content_retained`, independently showing whether the complete incoming content remains on Server.

One SQL statement observes snapshot/termination/finalization/latest-publication/session together.
No stop observation means `awaiting_node`. A pending capture confirms process stop but has no
finalization/checkpoint/publication or durability claim. Latest publication
attempts override stale finalization labels; historical publication and current content retention are
separate. This API neither authorizes local cleanup nor mutates/recomputes publication.

`fclaude stop SESSION [--timeout 60]` prints the operation ID and waits for managed saving; legacy
stop stays immediate. `fclaude stop-status OPERATION_ID [--wait] [--timeout 60]` uses the existing
device login for read-only re-query. The wait covers status HTTP requests and polling under one
retained Ctrl+C future and deadline. Exit codes are 0 for published (or a plain pending status query),
3 for wait timeout, 1 for capture_pending/conflicted/detached/superseded review, 130 for interruption,
and 1 for HTTP
or identity errors. Capture failure prints the original account/snapshot export command and ends
waiting immediately; subsequent queries can observe successful recovery. A waiting successful result
also requires exact process-stop confirmation.

The optional Native reboot acceptance now includes an actual two-kernel ARM64 VM power-cut test:
`agent-remote-node/tests/linux_skill_kernel_reboot_test.sh`. It preserves the first running session's
original disk identity, kills the VM without shutdown/finalization, and requires a distinct second
kernel boot ID. Helper reconciliation produces an unclean frozen capture, refuses premature cleanup,
and retains exact detached replay after a synthetic Server acknowledgement. This test does not run
real Claude or the complete real Server/worker transfer flow; the amd64 VM branch remains unverified.

## Native takeover capture dispatch and completion

`takeover_tool_account_skills` tasks retain the existing eight-field Server payload. The worker
requires canonical fields, Native backend, protocol/manifest version 1, the exact polled task-record
UUID and attempt, and matching Node/logical/idempotency identities. Before Helper access it reads
current exact Server authorization. One lease supervisor covers initial capture and retained upload;
any uncertain renewal cancels dependent work without reporting permanent failure.

The new local `capture_account_takeover` operation accepts `{binding, inventory}` only. The binding
contains the original Node/user/account/takeover/task/backend/epoch/inventory digest. The Helper
independently establishes Native writer quiescence under its durable account fence and serialized
mutation gate. The complete request is capped at 4 MiB, inventory at 10,000 entries, and operation at
five minutes. Disconnect, extra input and worker cancellation cancel the owned handler. The response
is the exact version-1 `AccountCapture`, preserving int64 epochs. Failure returns content-free
`MIGRATION_PENDING`. No path or caller-supplied quiescence proof crosses this operation.

The durable Server reservation and immutable Helper capture own restart recovery. Transient errors
never enter generic failed-task caching. A committed GET skips capture, transfer and lease renewal;
later source changes cannot replace the original capture. The worker confirms only this six-field
result through the existing task completion route:

```json
{
  "status": "committed",
  "takeover_id": "original takeover UUID",
  "task_record_id": "original task-record UUID",
  "tool_account_id": "original account UUID",
  "checkpoint_id": "original initial directory checkpoint UUID",
  "capture_digest": "original complete-tree SHA-256"
}
```

Server task completion checks the persistent takeover relation even if task type was altered. It
locks the active original owner and exact task, validates the original task payload, requires the
separately committed initial checkpoint and checks the exact immutable result. Generic failure is
rejected. Exact result replay has no directory/head side effects. An expired task lease after content
commit does not invalidate that immutable receipt; cancelled/failed/replaced tasks cannot be consumed.
Neither completion nor upload authorizes original source or local capture deletion. Ordinary Native
session admission now initiates reservations as described below. Docker/sbx writer proof and capability
enablement remain separate integration requirements.

## First-use Native takeover through ordinary session admission

The existing POST /api/v1/sessions can now reserve the original account's Native takeover when
effectively enabled library content first requires managed mode. Existing user/device, account,
workspace and replacement-session authorization applies before reservation. The account must retain
its original affinity Node and pinned Native backend, and that same Node must satisfy current
managed admission. Selecting a healthy replacement Node cannot authorize capture of an empty source.

The user content lock covers original reservation or replay. Only the migrating directory, exact
takeover receipt/inventory and unique takeover task are committed; no new session, startup task,
snapshot or effective-use receipt is created. Existing legacy sessions continue normally. A final
fresh Node capability check occurs before committing the reservation. HTTP 409 returns:

```json
{
  "error": {
    "code": "MIGRATION_PENDING",
    "message": "Account skill takeover is pending; existing sessions may finish normally.",
    "details": {
      "account_id": "original account UUID",
      "takeover_id": "original takeover UUID",
      "takeover_status": "reserved",
      "reservation_committed": true,
      "session_created": false
    }
  }
}
```

`takeover_status` can be reserved or uploading. Retries reuse the same reservation. Missing or
changed directory/task/binding evidence, or a terminal unfinished task, returns
TAKEOVER_RECOVERY_REQUIRED instead of inventing a new reservation. Docker/sbx first takeover remains
SKILL_MANAGER_UNSUPPORTED until its writer-proof adapter is integrated. Existing managed backends
retain their separate admission behavior and capability gate.

GET /api/v1/sessions/skill-takeovers/{operation_id} uses ordinary session user/device authentication,
rejects Node credentials, and reads only the immutable original owner's metadata. The ordinary
{data, request_id} envelope contains operation_id, account_id, status (reserved/uploading/committed),
task_status, nullable original checkpoint_id and recovery_required. It remains readable when new
managed admission is disabled, does not renew a lease, and exposes no content or writer inventory.
Only committed confirms the initial authority switch; a task result alone never does.

The fclaude launcher retains one 60-second deadline and Ctrl+C future across initial creation,
read-only progress and one resumed creation. It waits only on the exact 409 identity receipt above,
including strict booleans proving no session was created. Once the same operation/account returns
committed with a valid checkpoint and no recovery requirement, it submits the identical creation
input once. Transport failures, malformed receipts and uncertain POST responses never authorize
automatic replay. Timeout exits 3, interruption 130, and recovery/identity/HTTP failure 1.
After a timeout during POST, session list must be checked before manually requesting another new
session. The remote takeover remains durable and is not cancelled by ending the CLI wait.

## Per-target deployment attempt metadata

New configuration acceptance records an original attempt for every account target in the same
transaction as its immutable plan. Operation target responses add nullable `attempt_id` and
`attempt_number`, plus a per-target `retryable` boolean. Historical records have no reconstructed
attempt identity. The operation's own `retryable` remains distinct: an active operation or one with
unresolved conflicts cannot be resumed as an ended retryable operation merely because another
account has a failed attempt.

Attempt chains preserve original user/operation/account and plan digest, require contiguous positive
sequence numbers and exactly one direct predecessor, and retain terminal predecessors when a retry
appends a pending successor. Only classified transient failures are retryable. Complete chain and
current projection must agree before status or content retention can use them. Owner-scoped status
holds the existing user read lock and refreshes ORM observations; it neither creates attempts nor
rebuilds plans. Initial unbound targets remain stored/deploy-on-first-use; current bound targets
remain unsupported until runtime deployment dispatch is implemented.

The internal retry transaction requires the original operation generation, an idempotency key and
explicit original account/current-attempt pairs. It validates the complete selection and current
account binding/effective selection before appending any successor. Same-key identical replay returns
the original operation without selecting or queuing more targets. Configuration generation, source
bytes, successful targets and predecessor results are unchanged. Changed bindings/plans, supersession,
permission failures, unsupported targets and unresolved conflicts cannot be bypassed by retry.
The public API and CLI consume this ledger through the separate retry protocol below. This
persistence layer grants no Node deployment authorization.

The CLI preserves supplied attempt fields in JSON, displays sequence/retryability, treats absent
historical metadata as unknown, validates supplied identities/digest/transient retry classification,
and recognizes preparing as pending in its existing bounded read-only status wait.

### Public exact deployment retry

`POST /api/v1/skills/operations/{operation_id}/retries` accepts only
`{idempotency_key, expected_generation, targets:[{account_id, attempt_id}]}`. Generation belongs to
that original operation; it does not increment configuration. All explicitly selected attempts must
be current ended transient failures on still-applicable original plans. The whole set commits once,
returning the original operation envelope and current successor metadata. Successful targets remain
unchanged. Same-key changed requests, supersession, permissions, conflicts and changed bindings/plans
are rejected. This endpoint creates no source upload or session and does not grant Node execution.

`GET` on the same subresource with `key` recovers an already committed retry receipt for that owner
and original operation. An existing operation alone is not acceptance evidence; absent/wrong-owner/
wrong-operation retry keys return `OPERATION_NOT_FOUND`. Library acceptance-key lookup remains
separate. Reads do not append attempts, modify journal state or resubmit work. The existing live
user-token and skill-manager feature gate apply.

CLI `skill retry OPERATION_ID` selects all eligible transient failed targets from one original status
observation and journals exact request metadata before POST. `--dry-run` only displays that selection;
noninteractive submission requires `--yes`. Restart and transport recovery query the original retry
key first; only absence allows an identical replay. Receipt validation fixes operation/generation,
original plan digests and successor attempt progression. `status --last` recognizes the retry journal
and uses the same read-only lookup. Existing bounded wait, `--no-wait`, timeout (3), interruption (130)
and failure (1) semantics apply. Ordinary bound targets still report unsupported until deployment
scheduling is connected; acceptance and CLI transport tests do not prove a runtime executor.

### Automatic configuration supersession

A changed library acceptance compares its saved effective account plans with older unfinished plans
inside the same user lock/savepoint. The comparison ignores only operation ID and generation; node,
backend, exact sources/revisions/digests, installation epochs and enabled selection must agree.
Only a changed target that remains pending/running/conflicted or retryably failed can supersede its
parent operation. A completed nonretryable target does not invalidate another unchanged failure.
Staging, no-op changes, other account/tool scopes and unchanged effective pins do not trigger a
replacement merely because library generation increased. Unknown legacy attempts are not inferred.

The original operation then reports `superseded`, `retryable=false`, and the first replacing ID in
`data.replacement_id`. All original attempt observations and plan digests remain intact; per-attempt
failure classification does not override the parent's retry prohibition. Later changes do not rewrite
the first link. Same-key previously accepted retry lookup still returns that original operation,
while new retry requests fail `OPERATION_SUPERSEDED`. A late successful target cannot revive its parent.

Replacement IDs require same-owner higher-generation accepted operations with saved changed-target
selection evidence. Status/retention reject missing, foreign, backward or unrelated evidence.
Pending/running/conflicted targets retain original content roots until independently ended. A
replacement marker alone proves neither task cancellation nor writer drain. New acceptance, its
supersession markers and content release clocks commit or roll back together. Actual dispatch,
leased attempt progress and task revocation remain separate implementation boundaries.

## Internal deployment reservation boundary (schema 0050)

`skill_deployment_tasks` binds each original user/operation/account/attempt to one exact NodeTask
and an owned full-directory checkpoint. Its member references pin the selected branch checkpoints;
retry successors reuse the original complete input rather than preparing current heads again.
Reservation remains an internal service boundary. The dedicated Node transport below exposes only
previously reserved inputs. Dedicated success confirmation is specified below; public scheduling
remains unavailable.

The reserved task type is `prepare_account_skills`. Its canonical metadata payload contains
`protocol_version=1`, `user_id`, `operation_id`, `tool_account_id`, `attempt_id`, `task_record_id`,
`checkpoint_id`, `tree_digest`, `plan_digest`, and `runtime_backend=native`. It contains no file
bytes, manifest, host path or session identity. Admission requires the existing fresh full managed
backend report plus strict integer `skill_manager.native.deployment_protocol_version=1`. The
current Node does not advertise this optional field. Invalid optional versions are removed during
normalization, preventing boolean/integer equality from preserving a previous grant.

Authorization binds the authenticated node, original task record, attempt and current `lease_attempt`
and rechecks original selection, account binding, owner status and directory/member epochs under the
user lock. Generic task success/failure rejects both this task type and durable deployment bindings,
even when their mutable type/payload has changed. No result can claim deployment readiness through
this reservation boundary. Dedicated worker/Helper preparation and success confirmation are
implemented below, including durable termination recovery; public dispatch remains gated before activation.

### Original deployment input and short poll lease

All routes below require the original authenticated Node and the manager feature gate. They repeat
the exact task/attempt/poll authorization above; neither a known digest nor another valid Node token
grants access. Route `task_id` is the NodeTask database UUID, distinct from the deployment attempt UUID.

| Request | Parameters | Successful response |
| --- | --- | --- |
| `GET /api/v1/node/skill-deployments/{attempt_id}` | Query `task_id`, `lease_attempt` | SkillResult envelope, `schema_version=1`, `status=prepared_input`, `committed=false` |
| `GET /api/v1/node/skill-deployments/{attempt_id}/files/{digest}` | Query `task_id`, `lease_attempt` | Verified `application/octet-stream`, exact Content-Length, quoted digest ETag |
| `POST /api/v1/node/skill-deployments/{attempt_id}/lease` | Query `task_id`; body `{"lease_attempt": N}` | SkillResult envelope, `schema_version=1`, `status=leased`, `committed=false` |

Poll attempts range from 1 through 2147483647. The lease body permits only that field and requires a
JSON integer; missing/null, booleans, strings, fractional numbers and extra fields are rejected.
Reads do not renew a lease. Renewal cannot revive an expired lease or authorize a replaced poll.

Manifest `data` contains the complete immutable identity: `operation_id`, `attempt_id`, `task_id`,
`user_id`, `account_id`, `node_id`, `checkpoint_id`, `plan_digest`, `tree_digest` and
`runtime_backend=native`. It adds positive `directory_epoch`, original `plan`, complete `manifest`,
and `items`. Each item has `entry_name`, `state_id`, positive `state_epoch` and `checkpoint_id`.
Items are sorted by entry name. Plan sources are sorted by `(origin, source_id)` and retain disabled
choices; plan generation is the original accepted generation, never the current library generation.
The encoded complete envelope has a hard 64 MiB transport limit.

Only ordinary files belonging to this original full manifest can be downloaded. The Server releases
the initial authorization transaction before copying and verifying all bytes into private staging,
then reauthorizes the same original Node/task/attempt/poll before streaming. Staging spills to disk
above 1 MiB and is closed on failure, cancellation or completion. Missing or corrupt retained content
does not produce a successful partial file. Unrelated same-owner content is also inaccessible.

Lease `data` repeats the complete immutable identity and adds `lease_attempt`, `server_time`,
`lease_until` and positive `renew_after_milliseconds`. The server-relative duration is positive and
at most 300 seconds; the renewal interval is shorter than that duration. The current Node client
checks the full binding, exact current poll attempt and duration before accepting the response.
Original selection, epochs, active owner/account and fresh capability remain prerequisites on every
request, including renewal. Configuration supersession rejects all three routes.

The Go client validates original plan and tree digests, exact enabled member inventory and complete
identity before returning input. Canonical plan hashing preserves int64 values and sorts a copy of
the sources. The shared `tests/fixtures/skill-deployment-v1.json` fixture matches the Node fixture
generated using the Python schemas and canonical digest functions, including integers above 2^53.
The client rejects malformed/duplicate identity fields, redirects and invalid requests before use;
it performs no automatic write retries or filesystem publication.

These endpoints neither advance account heads nor record tool use, attempt progress or readiness.
They create no task or session and do not authorize generic task completion. Independent Helper
preparation, worker lease supervision and durable success results are specified below.
Cancellation/drain and scheduler activation remain separate requirements. The current Node still
does not advertise deployment capability.

### Independent Helper preparation

The authenticated private Helper socket accepts `prepare_skill_deployment`. Its standard version-1
request envelope contains a bounded logical `request_id`; payload contains only `attempt_id`,
`task_id` and `input_size` (positive integer, at most 64 MiB). No session, host path, runtime UID or
process identity is accepted. The subsequent input bytes are the complete original deployment
`data` above, strictly decoded and matched to the header and configured Native Node.

Frames are newline-delimited JSON with required `version=1` and `kind`. Helper `input` asks for
exactly `input_size` bytes. Helper `object` adds a manifest-bound `digest`, asking for exactly that
file's declared bytes followed by byte `0x06` only after the downloader's complete verification.
The Helper independently checks bytes, digest, classification and completion marker. Frames are
limited to 4096 bytes; unknown/null/duplicate fields are rejected. The complete exchange has a
10-minute ceiling, and socket disconnect cancels copying or waiting for mutation serialization.

Helper `prepared` adds a `receipt` with `version=1`, complete original `binding`, `input_digest`,
positive `directory_epoch`, original `generation` and Helper-generated `helper_receipt_id` UUID.
This receipt is local preparation evidence, not a generic task result or Server readiness receipt.
`failed` exposes no content, filesystem path or unrestricted internal error.

Preparation requires the existing original owner/account/Node fence; its initial directory epoch
cannot exceed the requested epoch. It does not create or advance that fence. The full directory,
permission baseline and private `deployment.json` receipt publish atomically beneath independent
SkillStateRoot as `deployment-<attempt UUID>/`, with Helper ownership and fsync/no-replace semantics.
Request IDs identify transport calls; the immutable deployment attempt and complete input identify
durable idempotency. Reissue of the same input can recover a lost response without redownloading.
Replay verifies private metadata, ownership, normalized permissions and every retained byte.
Corrupt/incomplete existing bundles are retained errors, not absence or permission to repair them.

The client checks the entire receipt against the original full input, including plan/member fields
through `input_digest`; a matching tree alone is insufficient. The worker remains responsible for
current Server lease authority. This operation neither mounts content nor starts a process, modifies
account/session files, publishes a head or records effective use. Dedicated worker success dispatch
and durable Server results are specified below. Cancellation/drain and scheduling still precede
capability activation.

### Durable deployment success and read-only recovery

Both routes require the authenticated original Node and query `task_id=<NodeTask database UUID>`:

| Request | Successful envelope |
| --- | --- |
| `POST /api/v1/node/skill-deployments/{attempt_id}/result` | `schema_version=1`, `status=confirmed`, `committed=true` |
| `POST /api/v1/node/skill-deployments/{attempt_id}/result/inspect` | `schema_version=1`, `status=observed`, `committed=false` |

The strict body contains exactly `lease_attempt` and `preparation`. The former is the original poll
integer (1 through 2147483647); the latter is the complete schema-1 Helper receipt above. Response
`data` contains exactly `result` (the submitted body), `accepted` (boolean), `current_lease_attempt`
and `task_status`. Confirmation requires accepted=true, succeeded and the exact submitted poll.
Inspection remains committed=false even when it observes an already accepted result.

First confirmation reconstructs the complete original input and requires its matching digest,
directory epoch and original plan generation, the current unexpired poll, active owner, matching
configuration/state epochs and fresh capability. The original user lock precedes the exact task
lock. One retention savepoint saves task success, clears its lease, inserts one immutable existing
`node_task_results` row, marks the original target attempt ready and updates the operation projection
and release clocks. No session, snapshot, head or effective-use record is created. Success
confirmation adds no migration beyond reservation schema 0050. The authenticated Node submits
Helper evidence; the receipt is not a cryptographic signature.

Exact accepted replay and inspection validate saved metadata without reconstructing content or
requiring the current feature/capability gate. They still require the active original owner and
exact authenticated Node/task/attempt binding. Normal input retirement does not erase the receipt.
Altered receipt/poll/identity, duplicate/missing/corrupt terminal results, changed terminal poll or a
retained terminal lease fail closed. Historical readiness does not assert current selection or
content availability. Unaccepted inspection grants no execution authority; an observed newer poll
fences an older proposal through the same locks used by confirmation.

The full-input digest uses SHA-256 over recursively key-sorted compact JSON with preserved integer
values and array order, UTF-8 text, Go JSON escaping of `&`, `<`, `>` and U+2028/U+2029. Both languages
verify `tests/fixtures/skill-deployment-input-digests-v1.json`, including int64 values above 2^53 and
Chinese/HTML/line-separator characters. This differs from merely hashing the directory tree.

The worker intercepts exact deployment task types/logical IDs before generic result caching. It
validates the exact ten-field canonical payload, original task UUID, Node, idempotency key, Native
backend and poll. One renewable lease covers input retrieval, file transfer, Helper preparation,
receipt validation, durable proposal persistence and dedicated confirmation. Errors remain bounded
`DEPLOYMENT_PENDING`; neither generic failure nor success can consume the task. A verified committed
receipt wins a concurrent renewal rejection caused by its own task's terminal transition.

The existing worker task ledger stores metadata-only schema-1 `{schema_version,result}` records
under `deployment_prepared_pending` or `deployment_prepared_confirmed`. Integer metadata is preserved
without float conversion. Full-record compare-and-swap prevents stale observations from replacing
newer proposals. A newer poll can replace a pending proposal only after exact unaccepted inspection
at that newer poll, retaining the identical Helper receipt; confirmed records cannot downgrade.
An independent background loop only inspects pending proposals and saves exact accepted observations.
It never acquires a lease, invokes Helper preparation or submits a new confirmation.

Dedicated Server revocation and drain confirmation are specified below. Timeout
or configuration supersession alone cannot release pending content. Ordinary scheduling and managed
deployment capability remain disabled.

### Permanent local deployment drain

The private authenticated Helper operation `drain_skill_deployment` accepts the complete original
ten-field deployment identity as its payload. It accepts no paths, file content, session/process
identity, current generation or poll number. The configured Native Node and an existing original
account fence must match. Its 30-second handler shares preparation's cancel-aware mutation lock;
socket disconnect or deadline cancels lock waiting. Any active preparation copy/publication must
finish or fail before the drain record can publish.

On first drain, an existing `deployment-<attempt UUID>/` must contain a safe original
`deployment.json` with matching full binding. Missing/corrupt/foreign identity or an unsafe bundle
blocks drain. Corrupt content bytes need not be verified or repaired to fence the original attempt.
An absent prepared bundle remains absent. The Helper atomically publishes a private immutable
`deployment-drain-<attempt UUID>.json` with exactly `version=1`, complete `binding` and its own
`helper_receipt_id` UUID. File and parent fsync precede acknowledgement; exact replay revalidates
the receipt and repeats parent fsync to recover a lost publication acknowledgement.

The standard Helper response contains `result={receipt:<the exact drain record>}`. Clients reject
missing, null, duplicate, aliased, unknown or changed receipt/binding fields. A failed or uncertain
operation reports bounded `DEPLOYMENT_DRAIN_PENDING`; absence of an acknowledgement never means
the record did not publish. Repeat the same original binding to recover its exact saved receipt.

Preparation checks the drain before downloading object bytes, including delayed requests that
already read input metadata. The same attempt cannot reopen after restart or by changing task,
owner, plan or other binding fields. Corrupt/linked/non-private/foreign-owned drain records fail
closed and are never repaired. No retained bytes, account directory, session, mount or process is
modified or deleted. The receipt establishes only local permanent preparation exclusion, not content
integrity, Server cancellation, supersession acknowledgement or reclamation authority.

Server retention now recognizes task `expired` as a known non-drained state, protecting its original
directory and members even after failed projections or configuration supersession. Unknown states
still fail retention analysis. Expired tasks cannot authorize success, renewal or overlapping retry
execution. Dedicated Server failure/cancellation confirmation and worker recovery are specified below.
This local operation does not activate ordinary scheduling or deployment capability.


### Original revocation and drained terminal confirmation (schema 0051)

Migration `0051_skill_deployment_drains` adds one immutable `skill_deployment_terminations` intent
per original deployment-task binding. The attempt primary key references that binding, preserving
its original owner/account/operation/Node/task/content authority. An independent unique intent UUID,
request poll, bounded original error code and Server-selected failed/superseded outcome are stored.
No previous task is backfilled. Downgrade locks and refuses any recorded intent before mutation.

All dedicated routes require the original Node token and query `task_id=<original task database UUID>`:

| Request under `/api/v1/node/skill-deployments/{attempt_id}` | Body | Successful envelope |
| --- | --- | --- |
| `POST /termination` | `{lease_attempt,error_code}` | `drain_required`, committed=true, data is original intent |
| `GET /termination` | None | `observed`, committed=false, data is `{intent:<original or null>}` |
| `POST /termination/result` | `{intent,drain}` | `confirmed`, committed=true |
| `POST /termination/result/inspect` | Same original `{intent,drain}` | `observed`, committed=false |

Intent contains exactly `version=1`, `intent_id`, complete original `binding`, exact original
`request`, `outcome`, `error_code` and `retryable`. Poll is a strict JSON integer from 1 through
2147483647. Permitted request codes are NODE_UNAVAILABLE, TRANSFER_FAILED, QUOTA_EXCEEDED,
DEPLOYMENT_INTERRUPTED, AUTHORIZATION_DENIED, SKILL_MANAGER_UNSUPPORTED, DEPLOYMENT_INPUT_INVALID
and OPERATION_SUPERSEDED. Only the first four permit failed-target retry. The Server selects
superseded only when the original operation has an actual replacement; its resulting error is
OPERATION_SUPERSEDED and retryable=false, preserving the original request. A claimed supersession
without an actual replacement conflicts. Public operation status retains its original replacement ID.

First revocation requires the canonical original task, active original owner and current poll;
lease expiry does not prevent revocation because it grants no execution authority. An older poll
cannot revoke a newer execution. The original user lock precedes the exact task lock, sharing the
success-confirmation lock order. An accepted success cannot receive a drain intent. If revocation
wins, all subsequent manifest/file authorization, renewal and first success are rejected with
DEPLOYMENT_REVOKED. Intent publication changes no task/attempt terminal state and releases no input.
Exact request replay recovers the same intent; changed requests conflict. Existing intent lookup
requires original authentication, but no current poll, content, feature or capability grant.

Only a matching saved intent and exact permanent Helper drain can submit terminal confirmation.
Drain contains `version=1`, the identical complete binding and nonzero `helper_receipt_id` UUID.
Task failure/cancellation, original target failed/superseded state, one existing NodeTaskResult,
projection and release clocks commit in one retention savepoint. Failed and cancelled tasks both
use the existing result-table category failed; the dedicated result preserves superseded semantics.
Result JSON records `{result:<exact submitted body>,lease_attempt:<poll at terminal commit>}`.
Polls issued after revocation cannot reopen preparation; confirmation fixes the final observed poll.

Confirmation/inspection data contains `result`, `accepted`, `current_lease_attempt` and `task_status`.
Accepted failed outcomes require failed tasks; superseded requires cancelled. Exact replay validates
saved metadata, final poll and cleared lease even after normal input retirement, capability closure
or creation of a retry successor. It never replaces the successor's state. Duplicate, missing or
changed terminal evidence conflicts. Read-only inspection remains committed=false even when accepted.
Retryable failure preserves the original input; a successor reservation requires the predecessor's
exact accepted dedicated drain result, not merely a failed/cancelled task status.

The Go transport validates canonical nested fields, explicit booleans, exact identities, bounded
codes and Server-selected retryability before returning authority. It performs no automatic uncertain
POST retries. Shared Python-generated failed/superseded response vectors live at
`tests/fixtures/skill-deployment-termination-v1.json`. HTTP transport alone does not invoke Helper,
change the worker ledger, schedule an ordinary operation or advertise capability. Dedicated Worker
orchestration now follows the durable phases below.


### Worker termination journal and recovery

The canonical original task-ledger key admits four additional schema-1 phases:
`deployment_termination_requested`, `deployment_termination_revoked`,
`deployment_termination_drained`, and `deployment_termination_confirmed`. The exact payload fields
are `schema_version`, complete `binding`, bounded original `request`, and nullable `preparation`,
`intent`, `drain`, `confirmation`. A retained preparation is the full original pending success
proposal, not rewritten or rounded. Confirmed success cannot enter termination.

The request is durable before revocation HTTP; committed intent is durable before Helper drain;
exact drain is durable before terminal HTTP. Full-record CAS rejects stale writers and immutable
receipt changes. No content, paths, credentials or session identifiers enter this journal. The final
accepted observation fixes its original poll and cannot be replaced by later observations.

Dispatch looks up revocation before preparation. Known bounded failure codes and lease/cancellation/
network/Helper unavailability can create a request; unknown errors remain pending. Renewal retains
typed Server causes. Uncertain success confirmation keeps its original success proposal. Background
recovery checks pending success proposals for revocation and separately advances terminal journals
without leasing or preparation. Requested recovery looks up original intent before any POST; if no
intent exists, an exact accepted pending success is restored without Helper access. A newer task
poll can update an uncommitted request only after absent-intent lookup. Existing intent always wins.

Lost Helper acknowledgement repeats only the identical drain binding. Once a drain is saved,
recovery inspects the original Server result before exact resubmission, without touching Helper.
Malformed/foreign records fail independently. No phase grants content reclamation, session/process
mutation or capability advertisement. Ordinary deployment scheduling is specified below; full backend
acceptance remains pending.


### First-takeover deployment discovery (schema 0052)

A new accepted bound target whose account directory is still legacy/migrating records a separate
`skill_deployment_discoveries` boundary: original user/operation/account, unchanged accepted plan
digest, and expected first takeover directory epoch. Unbound and already managed accounts get no
new discovery authority. Historical plans are not backfilled or reinterpreted.

The exact initial takeover publication resolves matching current active/retryable target boundaries
in its own user-locked transaction. Terminal unsupported/stored/ready and nonretryable failed
history does not expand when a later takeover publishes. Resolution fixes the original takeover ID and resolved digest, plus normalized
`skill_deployment_discovered_sources` rows for the initial local sources/first revisions. It never
substitutes a later account head, default revision or enabled value. Empty discovery still seals a
receipt. Failed resolution rolls back the entire initial authority publication; retained capture
and upload remain available for retry. Cross-account/user receipt and revision references have
composite foreign keys, and application validation also verifies original Node/backend and epoch.

Accepted plans, attempt digests, operation identity/generation and original idempotency records remain
unchanged. A resolved execution plan appends only those fixed initial local entries. Deployment
protocol version 1 and its input shape remain unchanged: task/content `plan_digest` now identifies
that execution plan where a discovery exists. The actual complete directory is still independently
bound to the task/input. It includes original root auxiliary data; discovering no valid new skill
never permits dropping that data. Conflicting names remain explicit materialization errors.

Authorization and retry compare current configuration with the saved execution selection, so later
local disable/removal/version changes cannot modify old input. Configuration replacement and its
historical validation compare resolved selections on both sides. Retention keeps original takeover
content and normalized local revisions reachable while the operation is pending/retryable; active
Node tasks still independently retain their complete original input. Terminal discovery metadata is
not a permanent content root. Downgrade refuses any recorded discovery before schema mutation.

This closes the first-takeover plan-consistency dependency. Ordinary pending acceptance/scheduling
is specified below; full real runtime acceptance remains pending and no backend capability is advertised.


### Ordinary pending acceptance and bounded deployment scheduling

Explicit Server policy and a complete saved Native deployment report classify new active bound
targets as `pending`, including known compatible offline Nodes. Unbound accounts remain `stored`
with `deploy_on_first_use=true`; missing/malformed/incompatible reports remain `unsupported`.
An operation with any pending target projects `preparing`. Acceptance persists immutable plans,
initial attempts and any discovery boundary without creating tasks or declaring runtime readiness.

Authenticated polling examines at most four latest unbound original-Node attempts before taking
task lease locks. Each candidate is reloaded under its original owner lock and committed independently.
Reservation rechecks fresh capabilities, active ownership, exact binding and unchanged saved selection.
First use reserves original takeover; later polls consume the sealed discovery and reserve complete
input. Unresolved migrations remain `needs_resolution`; resolved migrations resume the same attempt.
The attempt's metadata timestamp rotates waiting candidates so later accounts are examined.

Existing deployment bindings are excluded and independently rechecked under the owner lock. They
retain ordinary lease/redelivery plus dedicated success/revocation/drain confirmation. Superseded
attempts without any task for that attempt may become terminal without inventing a drain receipt;
older bound attempts independently retain their input. Definite pre-dispatch account/binding/content
failures become terminal; quota failure is retryable. Lost freshness on a known compatible Node waits,
while actual capability withdrawal becomes unsupported. Unknown failures roll back and surface.

The task, content, result and termination wire shapes remain protocol version 1. Capability
advertisement still requires full backend acceptance. Current first-use evidence uses ordinary HTTP
acceptance/polling, Linux Worker/root Helper and actual systemd descendant-writer inspection. The
first fence, immutable manual capture, takeover publication, discovery and complete deployment all
come from production execution, including lost takeover confirmation and replay with Helper stopped.
Only the original legacy account, accepted library package and compatible Node report are fixture
inputs. This does not prove the full daemon heartbeat loop, Claude launch, an unprivileged Worker
process in this proof, or Docker/sbx acceptance.

## Frozen Node export

`skill state export --snapshot UUID --scope account-directory --account-id UUID --output PATH`
selects one original Native snapshot. `--snapshot` and retained Server `--checkpoint` are mutually
exclusive; the existing checkpoint item/directory selection is unchanged. Frozen Node export is
complete-directory only, preserving cross-entry links and root auxiliary data. The source must
already have a complete immutable object-backed capture. No live-work or capture-on-read fallback
exists. Server quota exhaustion does not require uploading these bytes to Server.

`POST /api/v1/skills/state/node-exports/{snapshot_id}/authorize` requires the current user token and
`{device_id,ssh_key_id}`. It checks live user/token/device/key, original snapshot and original Node,
and ensures only the existing idempotent SSH-key sync task. The `authorized`, `committed=false`
result contains `binding`, `device_id`, `ssh_key_id`, `grant`, `expires_at`, `ssh_host`, `ssh_port`,
`ssh_user`, `authorization_task_id` and `authorization_task_status`. CLI waits up to 60 seconds for
`succeeded`; each observation must preserve the original binding. A grant is not local capture proof.

The binding is exactly `snapshot_id`, `session_id`, `user_id`, `account_id`, `node_id`, `task_id`,
`library_generation`, `directory_epoch`, `initial_tree_digest`. IDs are canonical UUIDs, integers
retain signed 64-bit precision, the library generation is nonnegative, and directory epoch positive.
The source is never rebuilt from today's account affinity or rules.

The HMAC grant uses domain `agent-remote:frozen-node-export:v1` plus NUL and exact URL-safe Base64
payload bytes. Payload version 1 contains that binding, random grant ID, original user token ID,
device/key, issue time and fixed expiry. Its lifetime is at most 900 seconds and cannot outlive the
issuing token. It is only retained in memory and SSH stdin; no arguments, logs, journal or exported
metadata contain it. Request validation errors never echo input fields.

The existing SSH gateway recognizes only `agent-remote-skill-export --snapshot UUID --protocol 1`.
Its device and SSH key come from installed forced-command arguments. Node authenticates each
`POST /api/v1/node/skill-state-exports/{snapshot_id}/verify` with its Node token and sends
`{device_id,ssh_key_id,grant}`. The result has the exact binding/device/key/expiry, `recheck_seconds`
(1–10), and explicitly nullable `incoming_digest`/`unclean`. Classification may be known before the digest when capture is pending. A known digest requires
known classification. Every known fact must match all saved termination/finalization records and
cannot disappear or change on subsequent verification.
Every `/verify` check revalidates original identities and revocation; that grant's expiry never advances.

The additive `POST /api/v1/node/skill-state-exports/{snapshot_id}/renew` uses the same authenticated
Node and exact `{device_id,ssh_key_id,grant}` request. It returns an uncommitted `authorized` result
whose data is `{previous_grant_digest,grant,permission}`. The predecessor digest is lowercase SHA-256
of the exact UTF-8 request grant. `permission` has the existing exact permission schema, with current
capture observations and the successor's expiry. The successor preserves grant ID, original user
token ID, device/key and the entire original binding. Its issue time is current Server time and its
expiry is at most 900 seconds later, capped by that original user token's current expiry. The input
grant must still be valid at issuance after database checks; expired input cannot be resurrected.
Every identity, revocation and retained-snapshot check remains mandatory. No tasks, content, quota
reservations or authorization rows are created. Existing `/verify` is unchanged. Consumers must
match the predecessor digest, keep all original input/learned facts and continue enforcing the
current short validity window; receiving another credential never restores a missed window.
The gateway consumes `/renew` after initial `/verify`, checks exact predecessor linkage and all
original/learned facts, and accepts the successor only while the previous short window remains live.
Helper/CLI enforce independent scan/progress budgets instead of a fixed whole-transfer ceiling.
Actual frozen and stopped-work SSH continuation beyond the original fifteen-minute grant passed;
see the implementation-status records for 60917/30245 and their precise synthetic evidence scope.

SSH stdin contains only `{version:1,grant:...}` followed by EOF. Handshake is capped at 8192 bytes,
grant at 4096 characters, and handshake time at ten seconds. Node inspects existing Helper
finalization metadata, reads its manifest and obtains read-only immutable object descriptors.
It requires ObjectsVersion 1, exact binding and all known Server capture facts. Inspection creates
nothing and cannot stop, reconcile, freeze, upload, acknowledge, publish or reclaim state.

Output framing:

1. Eight magic bytes `ARSKEX\x00\x01`.
2. Unsigned 32-bit big-endian length, then UTF-8 JSON (at most 64 MiB):
   `{version:1,binding,tree_digest,unclean,manifest,file_objects}`.
3. Distinct manifest file objects in lexicographic SHA-256 order. Each contributes exactly its
   declared raw length, followed by byte `1` only after Node verifies its content and checks current connection-local authority.
   Repeated digest entries must agree on length and content classification.
4. A length-prefixed completion JSON frame (at most 4096 bytes):
   `{version:1,tree_digest,file_objects,complete:true}`.
5. EOF and successful SSH exit are both required.

Node verifies remotely initially and immediately before the public header and completion footer.
Each successful response creates a connection-local validity window from HTTP request start plus
`recheck_seconds`, capped by the current grant expiry. Before/after objects, local checks enforce that
window, cancellation and unchanged observed facts. Renewal begins halfway through the current
window (checked every 100 ms), and honors a dynamically shortened interval. An independent expiry
watcher cancels blocked renewal/output; failed or late renewal is terminal and cannot revive authority.
No window is shared between connections or persisted. Remote revocation is enforced within the
last confirmed 1–10-second window, including initial Helper scans and stopped-work final rescans. CLI also
verifies manifest identity, object lengths/digests/text classification, completion identity and EOF.
Each initial metadata/scan phase and final stopped-work verification has a fifteen-minute budget.
Gateway/Helper output writes are at most 32 KiB and individually bounded to thirty seconds; CLI
partial reads reset a thirty-second progress timeout. Initial/final scan waits end at the first
prefix byte; the rest of that prefix uses the progress bound. SSH handshake-write/final-exit waits remain
ten seconds. Authorized progressing transfers have no separate fixed whole-transfer ceiling;
earlier caller cancellation and original user-token expiry still end the transfer. Legacy v1 retains
the 100000-entry bound. The separate negotiated recovery format below removes that dependency;
both formats enforce signed byte-count overflow validation. Export follows the complete manifest
size rather than applying a second fixed 10 GiB runtime-admission ceiling; buffers remain bounded.

Only a fully verified private staging directory can be atomically published to an absent/empty
output. Bundle files remain `checkpoint.json`, `manifest.json`, `objects/<sha256>`; no original
paths or links are instantiated. Frozen metadata uses `format=agent-remote-skill-node-snapshot-v1`,
original `binding`, `tree_digest`, `unclean`, and `file_objects`. It is not a Server checkpoint or a
publication receipt. Export does not authorize local cleanup. Missing recoverable data and interrupted
transfers leave no claimed complete bundle.

The Go-generated `frozen-export-v1.bin` fixture is checked by Go, Python and the Rust CLI receiver.
CLI contracts use an SSH process double; Linux Helper tests include allowed/denied nonroot peers.
These proofs remain separate from full deployed SSH/Claude/backend lifecycle acceptance.

### Stopped-work recovery without another Node content copy

The separate private Helper operation `stream_stopped_skill_export` accepts exactly the original
nine-field export binding above. The authenticated Node gateway may request it after failed frozen
inspection, but the Helper itself requires no-follow ENOENT for the finalization directory. Existing
incomplete, corrupt, linked or legacy captures never allow work fallback. It accepts no source path,
user grant, caller-provided process evidence or cleanup receipt.

The Helper holds its cancellable preparation/mutation lock for the entire bounded connection. It
requires the original sealed Native session snapshot, ready spec/draft, retained launch authority,
safe work ownership, and either private termination evidence or a recorded canonical original
invocation. Same-boot access proves the original invocation
or noncontradictory unit absence, stable repeated unit readings and empty whole cgroup. A distinct
boot additionally requires absent unit/cgroup/network/mount resources and stable boot identity.
Existing retained termination determines the exported unclean flag. If that record is absent,
only a retained canonical original invocation permits recovery, which is always unclean. Corrupt
or linked evidence is never absence, and export never writes a replacement record.

Scanning hashes every portable entry using original permission baselines and dependency mappings,
without fsync, a second content copy, capture publication or any runtime mutation. The independent
legacy v1 export constraints (100000 entries, signed 64-bit expanded byte count, bounded buffers and deadlines)
replace only the original runtime capture quota on this read. Runtime byte overflow remains recoverable
within these protocol constraints; invalid/overflowing metadata fails without truncation. The same framing carries the complete
observation and distinct verified bytes. Helper rechecks retained authority, work identity, the full
tree digest and passive writer proof before emitting completion. The gateway verifies the private
stream and exact EOF before forwarding its footer, with live grant checks active during initial
inspection, scans, blocked writes and transfer. Any disconnect, unexpected input, cancellation,
revocation, changed source or missing proof aborts without a complete export.

Success is recovered content, not a `FinalizationRecord`, `local_durable` receipt, upload or cleanup
authorization. The lock can delay other Helper mutations throughout an authorized progressing
transfer; initial/final scans remain separately bounded. Missing both termination evidence and a
recorded original invocation still prevents recovery. Renewable authorization now supports transfer
beyond the original grant lifetime. The separately negotiated recovery format below handles
over-entry sources without changing manifest v1; its acceptance is recorded independently. An isolated size-checked tmpfs test proves recovery
under actual ENOSPC before termination retention, without reclaiming any space. No Docker/sbx capability
or deployed Claude/SSH lifecycle evidence follows from the Linux fixture tests.

### Fresh Node content reclamation observation and local audit states

`GET /api/v1/node/skill-finalizations/{finalization_id}/reclamation-authorization?request_id=<UUID>`
requires the original authenticated Node, active owner, original stopped session/snapshot and feature
gate. A fresh random request UUID is echoed in a `Cache-Control: no-store` response. Under the user
storage lock, Server verifies the unretired original terminal finalization, complete incoming directory
checkpoint, latest terminal publication, manifest and every physical object's length, SHA-256 and
classification. Missing/corrupt/linked/retired/deleting input returns `STATE_RECLAMATION_UNAVAILABLE`.
Historical status can remain readable while this stronger authorization is refused. Cancellation
joins disk verification before releasing the lock. No Server lease, retention clock or reference is
created or changed.

The bounded response is `{schema_version:1,status:"reclaimable",committed:true,retryable:false,data}`.
Data requires exactly `version:1`, `request_id`, `node_id`, `user_id`, `account_id`, `session_id`,
`snapshot_id`, `finalization_id`, `checkpoint_id`, `tree_digest`, `unclean`, `publication_id`,
`publication_attempt`, `publication_status`, `verified_at`, `expires_at`. All UUIDs and the original
input bind the saved terminal acknowledgement. Publication may advance to a later terminal decision
without replacing the incoming checkpoint; attempts preserve integer precision. UTC expiry is exactly
60 seconds after verification. Node conservatively charges the entire request against that duration
using a process-local monotonic deadline from request start. It refuses redirects, automatic retries,
stale challenges, malformed fields and exhausted budgets. The deadline cannot be serialized or
reconstructed from persisted timestamps. `committed` describes retained remote content, not deletion.

Linux local journal primitives now retain separate immutable `finalization/reclamation.json` and
`finalization/reclaimed.json` records. Intent binds version, exact terminal capture, authorization,
original cleanup session root, and device/inode identities of work and frozen-object directories.
First mark requires exact acknowledgement/cleanup, fresh budget and complete unchanged captured work;
excluded system paths must be absent or empty. Completion requires both content roots absent and
parent sync. Audit metadata remains. No current Helper operation or Worker scheduler writes these
records or performs deletion; caller-side writer, mount/alias and local-reference proofs and a safe
delete/resume executor remain required.

`list_skill_finalizations` / `inspect_skill_finalization` now permit nil record with diagnostic
`reclamation_pending` or `content_reclaimed`, in addition to existing diagnostics. Valid audit records
remain readable through content removal; transfer/export rejects both reclamation states, and corrupt
markers remain `invalid_retained_state`. Worker skips completed reclamation, leaves pending deletion
unresolved and does not recapture/reupload either state. Both retire original admission grants without
revoking a replacement broker nonce. These diagnostics are not a new content-deletion socket API.

The Linux filesystem executor now consumes the immutable local intent and performs exact
manifest-checked no-follow deletion with cancellation/restart recovery. This is an internal primitive,
not another Helper wire operation; Worker scheduling is still absent. First marking and intent
validation reject a current `publication_status:"conflicted"` observation until a later resolved
publication preserves the original incoming checkpoint. Equal publication ID/attempt must keep its
terminal status. Remote content availability alone does not override unresolved-conflict protection.

### Frozen read lifetime descriptor

The existing private `open_skill_finalization_file` request permits `kind:"hold"`, with the original
full `binding`, `digest:""`, `tree_digest:""` and `unclean:null`. Response metadata retains the
existing shape `{record,kind,size,entry}`: full original capture, `kind:"hold"`, positive manifest
length bounded to 64 MiB and `entry:null`, plus exactly one read-only close-on-exec descriptor.
The descriptor holds a shared kernel flock on the immutable private manifest inode. No new lock
file, path input, credential, deadline or lease token is introduced. SCM_RIGHTS preserves its lock
across sender shutdown; the receiver closes it after its entire upload/export operation.

Worker content transfer and frozen gateway export now hold this descriptor before reading the
manifest through final success/failure. Marking and deletion require a nonblocking exclusive lock
on that same inode. Marked content cannot grant another read hold. Raw manifest/object descriptors
also take shared inode locks, and object deletion preflight refuses active object readers. All
existing binding, peer, field, size, cancellation and descriptor-transfer checks remain mandatory.
This additive read operation does not expose a reclamation socket operation or enable scheduling.

### Live local reclamation exchange

The authenticated private `reclaim_skill_finalization` operation accepts exactly
`{capture:<full terminal object-backed capture>}`. It bypasses generic task-result replay and owns a
15-minute cancellable connection, lifecycle-lock wait and deletion context. An unmarked original
input first produces `{version:1,kind:"authorize",challenge:<fresh UUID>,acknowledgement:<saved ack>}`.
The Helper starts its original monotonic 60-second budget **before** sending this frame. Worker calls
the authenticated Server reclamation endpoint using exactly that challenge and sends only the strict
`ReclamationAuthorization` JSON object back on the same socket. No deadline, duration, path, credential
or generic receipt cache crosses this boundary. Both IPC directions and Server scanning consume that
same Helper budget. Initial marking is deadline-cancelled; durable intent can finish deletion under
the remaining outer context without refreshing authority.

`resume_skill_reclamation` accepts exactly `{node_id,session_id}`. It finds only an already-valid
immutable intent and repeats original runtime/reference proof before continuing. It never creates
intent or emits an authorization challenge. Neither Worker transfer metadata nor a saved HTTP response
is permission to resume a different capture.

Both operations return `{version:1,kind:"reclaimed",record:<exact original terminal capture>}` only
after fsynced completion. Failure returns only `{version:1,kind:"pending"}` or interrupted EOF. All
frames are bounded to 16 KiB and reject missing, duplicate, aliased, null and extra fields. Worker
checks the original capture on challenge and completion. EOF, unexpected trailing input, cancellation
and expiry close/join the operation; Helper disconnect while HTTP is in flight cancels that request.
A lost completion reply resumes through the exact durable intent, including on a replacement Helper.

The independent Worker page loop now requests first reclamation after transfer has returned and
closed its read hold, with terminal acknowledgement and transient cleanup already complete. Pending
inventory resumes without another upload or HTTP authorization; complete inventory skips content.
Uncertain/legacy authority and unresolved conflict preserve local input and pending status. No new
Worker ledger phase or backend capability advertisement is introduced.

## Default-limit reconciliation budget

The Native `reconcile_skill_session` and `drain_unadmitted_skill_session` clients and Helper handlers
use one bounded 15-minute operation budget, including lock waiting, exit inspection and frozen
capture. Earlier caller deadlines and socket-disconnect cancellation remain effective. Other generic
Helper operations retain their existing short deadline; public CLI stop/status waiting is unchanged.
The former 30-second ceiling prevented an actual 100,000-entry default-limit capture from completing.
A real Helper socket regression failed before the change and passed with the full manifest afterward.
This changes no capture binding, clean/unclean rule, reference, acknowledgement or capability contract.

## Scoped frozen-object descriptor reader

The authenticated private Helper operation `read_skill_finalization_objects` accepts exactly
`{capture:<complete original object-backed finalization record>}`. It validates the original Native
session and complete frozen manifest once, pins the immutable manifest and object directory, and
returns the existing version-1 descriptor response with kind `manifest`, exact record, size and null
entry. This read-only manifest FD transfers the shared kernel content lock to the client. The Helper
releases its lifecycle mutex after initial validation; the kernel lock prevents concurrent reclamation.

The same connection then accepts up to 100,000 sequential existing object selectors with exactly
`binding`, `kind:"object"`, `digest`, `tree_digest`, and `unclean`. Each selector must match the pinned
capture and original manifest membership. Replies use the existing exact object metadata plus one
read-only, close-on-exec, single-link regular-file FD with an independent shared lock. Existing bounded
ACK and strict ancillary/JSON validation apply to every response. Anchored manifest and directory
metadata are checked before and after opening each object. Complete content hashing/classification
remains the consumer's responsibility. The reader closes on failure; no recapture or input substitution
is permitted. The connection has a 15-minute ceiling and earlier caller deadlines win.

EOF and cancellation close/join the input pump and cancel lifecycle-lock waiting. A client still
holding the transferred manifest FD remains protected after Helper shutdown. Worker upload and
frozen SSH export use this bounded reader; legacy one-file calls and stopped-work recovery retain
separate semantics. Reader closure cannot acknowledge persistence or authorize deletion. There is
no new journal, global cache, path input or capability advertisement.

## Server upload declaration projection and long Worker transfers

Migration 0054 adds an internal, reproducible object declaration index bound by a composite foreign
key to original owner/upload/tree/scope. The complete unique-file index, its version and expected row
count publish atomically with upload admission. Legacy version-0 inputs backfill under the same user
write lock after full original-manifest/digest validation. A single-file HTTP request reads only the
current upload metadata and exact declaration; all existing attempt, expiry, ownership, byte length,
digest, classification and shared-object deletion checks remain required. Index rows retire on complete
or expiration; canonical upload metadata and content remain governed by the existing retention rules.

Retention graphs and GC forecasts use one active-lease interpretation. Indexed references are
count-checked and consume the existing row budget; missing references abort the whole analysis.
Legacy staged manifests keep full validation and the existing JSON budget. No full canonical JSON is
loaded for indexed/terminal upload graph entries. Zero-reservation leases still protect their bytes.
No new public wire schema, endpoint, backend capability or content publication boundary is introduced.

Worker HTTP transfers may outlive the Helper's bounded object-reader connection. Between files,
Worker replaces a ten-minute-old reader using the exact original capture and acquires the replacement
hold before releasing the prior reader. The outer upload hold remains throughout. This is not Server
lease renewal, recapture or upload completion. Frozen SSH export now uses the same rotation
strategy under its separate renewable authorization and continuous outer hold.

### Server tree-member download queries (2026-09-26)

Per-file content, Node snapshot and deployment downloads now use the existing exact
owner/category/tree/object references created with whole-tree completion. The canonical manifest
remains the directory/path/mode/link response. File bytes still undergo full size/digest/type checks.
A partial index over unavailable objects supports the whole-tree cross-category deletion barrier:
a healthy requested member is still rejected while any other member has a shared deletion marker.
Unrelated objects cannot grant membership or block another tree. Original Node/task/snapshot/attempt
and lease authorization, plus post-copy reauthorization, are unchanged. No wire fields, endpoint,
lease duration, feature capability or backend advertisement is added. See Server
`docs/skill-tree-downloads.md`; full 100,000-response HTTP acceptance remains a separate live test.


## Negotiated complete recovery stream

The fixed SSH forced command remains protocol 1. New CLI stdin adds `recovery_version:1` to the
exact `{version:1,grant:...}` handshake. Only integer 1 is supported; duplicates, nulls and unknown
fields fail. Legacy requests retain the existing complete-manifest stream. Negotiated frozen reads
also retain it. Only an absent capture, exact original retained source and independent stopped-writer
proof permit `stream_stopped_skill_recovery`. An existing Server incoming digest forbids recovery;
a later learned capture digest must match or terminate the live authorization chain. No fallback
retries an uncertain grant request or revives expired authority.

Recovery magic is eight bytes `ARSKRC\x00\x01`. Frames have a four-byte unsigned big-endian JSON
length. Header (maximum 4096 bytes) has exactly `version`, `binding`, `recovery_digest`, `unclean`,
`entries`, `file_bytes`, `file_objects`. Counts are nonnegative signed-64-bit bounded; file_objects
counts file entries including identical content at different paths. The header digest uses the
recovery domain and complete entry fields in filesystem enumeration order, never manifest v1 identity.
Private source inode digests are not sent. Complete manifest v1 stays capped at 100,000 entries.

Exactly `entries` entry frames follow, each at most 64 KiB with all eight ordinary entry fields.
Non-files have normal complete metadata. A file start has declared size, empty sha256/content_kind;
it is followed immediately by exactly size bytes and a maximum-4096-byte content frame containing
only `sha256` and `content_kind`. Source hashes during this same read; relay and CLI independently
verify all bytes before accepting trailing claims. Explicit counts bound remaining bytes/objects.
The final frame has exactly `version`, `recovery_digest`, `entries`, `file_bytes`, `file_objects`,
`complete:true`, and must repeat the original header facts after full source and writer verification.
No malformed/duplicate/unknown/null fields or trailing bytes are accepted. Initial/final scan and
ordinary progress budgets, live original authority and revocation behavior remain unchanged.

CLI privately stages format `agent-remote-skill-node-recovery-v1`, original binding, recovery_digest,
termination classification and counts in checkpoint.json; ordered complete entries in recovery.jsonl;
path-SHA256-addressed metadata in entries/; and content-addressed objects/. Its index checks unique
paths, explicit directory parents, depth, internal link targets/cycles and non-directory traversal
without tree-sized in-memory metadata. Files and metadata are verified/fsynced; whole journal digest,
footer, EOF and SSH exit success precede atomic destination publication. JSON command output retains
its common tree_digest field, interpreted under its explicit format. No v1 manifest.json is created.
This is a distinct recovery bundle, not an importable published checkpoint or retention acknowledgement.
