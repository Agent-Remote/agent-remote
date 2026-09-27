# Backup And Restore

## What To Back Up

Control plane:

- PostgreSQL database.
- The complete Server `skill-content` volume, coordinated with the database snapshot.
- `.env` deployment file.
- Caddy data if you rely on automatic TLS certificates.

Node:

- `/etc/agent-remote-node/config.json`.
- `/var/lib/agent-remote/users`.
- The configured Node `SkillStateRoot`, including pending finalization and takeover journals;
  use the actual Node configuration rather than assuming every pending byte is on the Server.
- `/opt/agent-remote/runtimes/claude` metadata or the exact pinned Claude version and checksum needed to reinstall it.
- `/var/lib/agent-remote/browser-sessions` only if active browser troubleshooting is required.

Client:

- `~/.config/agent-remote/config.toml`.
- `~/.config/agent-remote/state.sqlite3`.
- platform credential store entries for the device token.

## PostgreSQL Backup

For a deployment with skill content, use the coordinated procedure below instead of taking this
database-only backup while content writers are running.

```sh
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml exec postgres \
  pg_dump -U agent_remote -d agent_remote > agent_remote.sql
```

## PostgreSQL Restore

For skill-manager data, restore the matching content volume using the coordinated procedure below;
do not start Server after restoring only PostgreSQL.

Stop the server first:

```sh
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml stop server
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml exec -T postgres \
  psql -U agent_remote -d agent_remote < agent_remote.sql
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml start server
```

## Node Restore

Restore `/etc/agent-remote-node/config.json` and `/var/lib/agent-remote/users`, reinstall the same managed Claude runtime, then:

```sh
sudo systemctl restart agent-remote-runtime agent-remote-node
```

Do not restore `/var/lib/agent-remote-runtime` as live process state. If Native systemd units or Docker containers were not restored, running sessions should be reconciled as `interrupted` or lost and recreated from the control plane; commands must not be replayed automatically.

## Coordinated Skill Content Backup

Stop all Server replicas and content/GC workers before taking the database and filesystem backups.
Keep them stopped until both backups finish. The current single-Server Compose layout uses:
Use the deployment's original Compose project name (including its `-p` option, if any), so the helper
container mounts the existing content volume.

```sh
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml stop server
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml exec -T postgres \
  pg_dump -U agent_remote -d agent_remote -Fc > agent_remote.pgdump
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml \
  run --rm --no-deps -T --entrypoint tar server \
  -C /var/lib/agent-remote/skill-storage -cpf - . > skill-content.tar
```

Treat these files, the deployment configuration, encryption key and exact component versions as one
private backup set. Check each command's exit status and archive readability before starting Server
again. Do not use `docker compose down -v`: it removes the database and content volumes. Pending
Node-only state needs a separate application-consistent Node backup after its writers are stopped;
this Server procedure does not capture live working copies or certify backend recovery.

Restore into an isolated deployment with an empty database and empty content volume, keeping all
Server replicas/workers stopped. Use the same service UID and a compatible Server/schema version.
For the Compose layout, after PostgreSQL is available:

```sh
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml exec -T postgres \
  pg_restore -U agent_remote -d agent_remote --exit-on-error --no-owner --no-acl < agent_remote.pgdump
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml \
  run --rm --no-deps -T --entrypoint tar server \
  -C /var/lib/agent-remote/skill-storage -xpf - < skill-content.tar
```

Preserve directory ownership/mode and immutable object permissions. A database from a later backup
must not be paired with an earlier content archive. Before reopening access, verify retained tree
and object digests against the restored files and reconcile Node leases/journals without replaying
old commands. Schema rollback must obey the migrations' data-loss guards; retired history cannot
be recovered by merely changing retained flags. Future GC activation also requires complete Server
writer coverage: mixed older writers or clocks with unknown coverage cannot authorize deletion.

The content archive must include each user's private `.deletions` directory. These zero-content
completion receipts fence delayed disk operations after a database connection fails; they are not
temporary upload files. Restore them together with the matching `skill_content_deletions` table.
Never remove just the receipts, just the pending task rows or just the `deleting` object markers to
resume uploads. Stop every Server replica and worker, including disk threads, before restoring either
side; a pending task may legitimately refer to a file already unlinked before its SQL completion.

This runbook describes the required backup boundary. Full skill-manager upgrade, restore and actual
Native/Docker recovery acceptance remain tracked in [skill-manager-implementation-status.md](skill-manager-implementation-status.md).

The 0043 deletion protocol has an isolated PostgreSQL + content-archive recovery proof: full task,
object, tree, upload and quota rows survived real `pg_dump`/`pg_restore`, along with both durable disk
receipts. A restored pending task whose file was already unlinked converged without another quota
charge; old completed-task and delayed disk replays preserved reuploaded content. Evidence is in
`/tmp/skill-content-gc-restore.log` and `/tmp/verify_skill_gc_restore.py`. This bounded fixture does not
prove complete Node/runtime recovery, mixed-version upgrades or every retained-history restore case.

Schema 0044 also requires `skill_prune_content_claims` in the coordinated SQL backup. These rows
bind deferred tree/object cleanup to the actual content row and the original account/source scope.
Their cascading content foreign keys discard only this derived cleanup authority when the original
row disappears; later same-digest uploads do not inherit it. Restore claims with matching tree,
object, quota and deletion-task state. Never reconstruct them from historical digests or wall-clock
creation times, or drop them independently to force a downgrade. A nonempty claims table blocks
0044 downgrade before schema changes. This requirement does not establish full runtime restore
acceptance.

Schema 0045 adds `skill_prune_operations`, `skill_prune_operation_entries` and
`skill_prune_operation_deletions` to the coordinated SQL backup. Preserve all original disclosure
rows and the links to matching deletion-task UUIDs, even after the corresponding content is gone.
These terminal records are not content roots and must not be reconstructed from current heads or
current task progress. Existing acceptance replay uses the exact original request fingerprint before
checking its old signature; rotating the Server secret invalidates unaccepted previews but does not
invalidate accepted receipts. No raw confirmation credential is stored in these tables. Any retained
prune operation blocks 0045 downgrade before schema changes. The isolated 0044→0045 roundtrip and
nonempty downgrade guard are verified separately from full runtime backup/restore acceptance.

Schema 0046 adds `skill_finalizations.persisted_at` to the coordinated SQL backup. This is the original
complete-content synchronization time, independent of later publication/retirement updates. Existing
0045 rows upgrade with NULL; never reconstruct the time from `created_at` or `updated_at`. Preserve
recorded values during restore. Any non-NULL value blocks downgrade to 0045 before schema changes,
because that evidence cannot be recreated. Downgrade takes an exclusive table lock before checking,
including against concurrent content completion. Isolated PostgreSQL roundtrip and downgrade-refusal
checks cover this column; full Native/Docker coordinated runtime restore acceptance remains separate.

Schema 0047 adds `skill_operations.plan_version`, `skill_deployment_targets` and
`skill_deployment_entries`. Back up these original configuration plans with the operation ledger
and revision/epoch metadata. Preserve target bindings, selection rows and digests exactly; never
rebuild missing plans from current account rules. Historical operations keep a NULL plan version.
Pending and retryable terminal operations protect the exact original package/local revisions, while
ordinary terminal plan metadata alone does not permanently retain bytes. Recorded plans block
downgrade to 0046 under an exclusive operation-table lock. Isolated PostgreSQL migration, empty-plan
roundtrip, nonempty downgrade refusal and schema/ORM reference parity are verified; runtime restore
and target-attempt recovery remain separate acceptance work.

Schema 0049 adds `skill_operations.attempts_version`, `skill_deployment_attempts` and
`skill_deployment_retries`. Preserve original attempt UUIDs, sequence/predecessor links, plan digests,
error/retryability classification, the current operation projection and exact retry keys/digests in
the same database backup. Missing history must fail status/retention validation; it must never be
replaced by a fresh attempt inferred from current rules. Historical NULL attempt versions remain
unknown. Retry appends successors to original plans and does not duplicate successful targets.
Recorded attempts, retry receipts or version markers block downgrade to 0048 before any schema
mutation. PostgreSQL upgrade/empty downgrade/re-upgrade and history-preserving downgrade refusal are
verified. Full coordinated runtime restore and actual deployment-task recovery remain separate work.

The coordinated restore acceptance now has a repeatable, opt-in test in
`agent-remote-server/tests/test_skill_coordinated_restore.py`. From the Server repository, with
Docker available and the Node repository beside it, run:

```sh
AGENT_REMOTE_RUN_SKILL_RESTORE_TEST=1 uv run pytest -q tests/test_skill_coordinated_restore.py
```

Set `AGENT_REMOTE_TEST_NODE_REPO` if the Node checkout is elsewhere. The test creates and removes its
own PostgreSQL container; it never accepts an existing database as a restore target. It migrates the
source to head, seeds actual library/publication services, performs `pg_dump` plus a full content
archive, drops the source database and moves its content aside, then restores an empty target.
Before any target mutation it compares every ORM business table's complete sorted-row digest,
Alembic version, all content bytes and filesystem modes. Required nonempty tables include revisions,
layered overrides, account/local state, directory membership, snapshots/finalizations, operation and
deployment plans/attempts, publications, and partially saved resolution choices/receipts. Every
retained tree is also verified against physical objects under its owner.

The restored partial conflict plan resumes to publication without losing binary/local/root files or
resurrecting deleted or detached data. A fixture registers a different Node and moves account
affinity; actual session creation, task polling and snapshot content authorization then supply a
fresh Linux container. That container has no network, original content volume, credentials or old
Node state. The production materializer verifies ordinary independent copies, runtime UID/GID,
bytes and source-mode roundtripping. Requests from the old Node and a different content owner are
rejected. This covers Server SQL/content restoration and new-Node materialization, not automated
onboarding/failover, old runtime-journal restoration, daemon startup/SSH, actual model learning,
Docker Sandbox lifecycle, or interrupted backend-migration recovery. Keep these acceptance limits
separate when deciding whether to reopen a production deployment.

For Node-local backend migrations, retain `migration-writer-*.json` with the corresponding
`account-copy-*.json` and `migration-account-copy-*.json` records. New copies carry `writer_version: 1`;
phase receipts bind original command identity, boot, launch UUID, invocation and terminal result.
They must not be removed independently, downgraded to old evidence or reconstructed from unit names.
A restored previous-boot pending writer remains unresolved; restoring metadata alone never proves
source permissions or authorizes restarting a privileged copy/ACL command. Server coordinated restore
acceptance above does not certify restoration of these Node journals.

Writer-version-2 Node migrations additionally require `migration-ownership-*.json`. These intents
are written before direct target/rollback ownership changes, including the window before any ACL
service exists. Preserve them with the original copy, writer phases and whole-migration receipt.
Absence of an older ACL receipt cannot be used to infer that rollback never began. Same-boot complete
version-2 metadata may converge on exact Helper replay, but old/previous-boot or incomplete work
remains retained and cannot be settled by restoring or deleting individual journal files.
