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

This runbook describes the required backup boundary. Current Skill restore and real Native/Claude
validation gaps are tracked in the [acceptance status](skill-acceptance-plan.md).
Docker Sandbox is outside the current acceptance scope.

## Skill Restore Invariants and Verification

Restore the complete database, not a hand-picked subset of Skill tables. Preserve original cleanup
claims/deletion-task IDs, prune disclosures/receipts, finalization `persisted_at`, configuration plans,
deployment attempt chains and retry keys alongside revisions/epochs and object state. Historical NULL
values remain unknown. Do not reconstruct plans from current rules, infer persistence from update times,
or reuse cleanup authority for a later same-digest upload. Schema downgrades must obey retained-data guards.
Accepted receipts keep their original request identity; secret rotation invalidates unaccepted prune
previews, not accepted receipts.

Back up the entire Node SkillStateRoot with matching account data and migration backups. This includes
copy, writer-phase, ownership, whole-migration, baseline/attestation and repair records, as well as
snapshot/finalization/cleanup/reclamation evidence. Never restore or discard individual journal phases
to manufacture completion. Restored metadata alone does not prove writer quiescence or source permissions;
use the [exact recovery contract](skill-manager-wire-v1.md) before reopening admission.

The reusable Server test is
[tests/test_skill_coordinated_restore.py](https://github.com/Agent-Remote/agent-remote-server/blob/main/tests/test_skill_coordinated_restore.py).
From the Server repository, in an explicitly selected disposable test environment with Docker and the
Node sibling checkout:

```sh
AGENT_REMOTE_RUN_SKILL_RESTORE_TEST=1 uv run pytest -q tests/test_skill_coordinated_restore.py
```

Set `AGENT_REMOTE_TEST_NODE_REPO` for a different Node checkout. The runner creates its own PostgreSQL
container, restores SQL and content into an empty target, compares all ORM rows/digests/modes, resumes
saved conflict choices and verifies fresh-Node materialization through actual snapshot authorization.
It never accepts an existing production database as its restore target. Historical isolated GC tests
also verified pending deletion recovery and delayed replay protection for reuploaded content.

These proofs cover SQL/content restoration and synthetic new-Node materialization. They do not certify
production failover, restored old Node/runtime journals, daemon/SSH startup or real model learning.
Use the [current acceptance status](skill-acceptance-plan.md) for outstanding production work;
Docker Sandbox is outside that plan.
