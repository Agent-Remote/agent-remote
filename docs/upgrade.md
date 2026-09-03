# Upgrade

The coordinated Community upgrade procedure for the session full-trust release is documented in
[`session-full-trust-community-upgrade.md`](session-full-trust-community-upgrade.md). It includes
the required commit, push, CI, prepare-release sequence for every repository, component pinning,
deployment configuration, manual macOS installation, acceptance checks, and rollback steps.

## Control Plane

The signed device-control release evidence is part of the root deployment bundle, not a separately
expiring lease. Upgrade the Server image and the read-only evidence file from the same root release;
do not copy an evidence file from another version. Schema 9 has no `expires_at`; the Server verifies
the exact root composition and signature at startup. A schema 1-7 file is migration-only and must be
replaced by a current schema 9 file before enabling device control on the upgraded release. Already
issued schema 8 evidence remains permanently verifiable for its exact signed composition, but is not
emitted for a new composition.

Before upgrading:

```sh
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml ps
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml exec postgres pg_dump -U agent_remote -d agent_remote > backup.sql
```

Upgrade images:

```sh
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml pull
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml up -d
```

The server image runs Alembic migrations on startup. If startup fails, inspect:

```sh
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml logs server
```

## Node

Re-run the same one-command installer used for registration. It upgrades all three node binaries and the managed Claude runtime, refreshes systemd/SSH configuration, reuses the existing node token, and verifies the helper probe and heartbeat:

```sh
curl -fsSL https://raw.githubusercontent.com/Agent-Remote/agent-remote-node/main/scripts/install.sh | \
  bash -s -- \
  --server-url https://agent-remote.example.com \
  --node-id <node-id> \
  --registration-token <original-registration-token>
```

The installer also ensures Native developer tooling (`git`, `gh`, and the OpenSSH client) is present. Sessions created before an upgrade that adds runtime mounts or developer credential injection must be stopped and recreated; an existing Bubblewrap process cannot acquire new mounts.

For the SSH agent forwarding rollout, upgrade the node first, then the control plane and CLI. Trigger one attach so the versioned `sync_ssh_keys` task refreshes the gateway entry, wait for the node to consume it, and create a new Native session for validation.

Confirm:

```sh
sudo systemctl status agent-remote-runtime agent-remote-node
```

Use `--force-register` only when intentionally replacing the node token. Before changing an account's pinned backend, stop all active sessions and use the explicit runtime migration action; changing a node default does not migrate existing accounts.

## CLI

Replace the local CLI package, then verify:

```sh
agent-remote doctor --fix
agent-remote status --online
```

Do not delete `~/.config/agent-remote` during upgrades unless you intentionally want to remove local device identity and sync metadata.

Re-running `agent-remote login` against the same configured server reuses the active device and
rotates its credential instead of registering another device. To clean up duplicate records created
by older releases, pause and delete each related sync session in the console, then delete its
workspace, revoke the old device, and finally delete the device.
