# Upgrade

## Control Plane

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

Upgrade node binaries with the node installer, then restart:

```sh
sudo systemctl stop agent-remote-node
sudo install -m 0755 agent-remote-node /usr/local/bin/agent-remote-node
sudo install -m 0755 agent-remote-attach /usr/local/bin/agent-remote-attach
sudo systemctl start agent-remote-node
```

Confirm:

```sh
sudo systemctl status agent-remote-node
```

## CLI

Replace the local CLI package, then verify:

```sh
agent-remote doctor --fix
agent-remote status --online
```

Do not delete `~/.config/agent-remote` during upgrades unless you intentionally want to remove local device identity and sync metadata.

