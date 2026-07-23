# Backup And Restore

## What To Back Up

Control plane:

- PostgreSQL database.
- `.env` deployment file.
- Caddy data if you rely on automatic TLS certificates.

Node:

- `/etc/agent-remote-node/config.json`.
- `/var/lib/agent-remote/users`.
- `/opt/agent-remote/runtimes/claude` metadata or the exact pinned Claude version and checksum needed to reinstall it.
- `/var/lib/agent-remote/browser-sessions` only if active browser troubleshooting is required.

Client:

- `~/.config/agent-remote/config.toml`.
- `~/.config/agent-remote/state.sqlite3`.
- platform credential store entries for the device token.

## PostgreSQL Backup

```sh
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml exec postgres \
  pg_dump -U agent_remote -d agent_remote > agent_remote.sql
```

## PostgreSQL Restore

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
