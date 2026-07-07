# Deployment

Phase 12 provides a self-hosted deployment path for the control plane, admin web, node runtime, and local CLI packages.

## Control Plane

Requirements:

- Linux host with Docker and Docker Compose plugin.
- Public DNS name for the admin/API endpoint.
- Open inbound ports `80` and `443`.

Steps:

```sh
mkdir -p /opt/agent-remote
cd /opt/agent-remote
cp deploy/compose/.env.example deploy/compose/.env
```

Edit `deploy/compose/.env`:

- `AGENT_REMOTE_DOMAIN`
- `AGENT_REMOTE_PUBLIC_BASE_URL`
- `AGENT_REMOTE_SECRET_KEY`
- `POSTGRES_PASSWORD`
- `CORS_ALLOWED_ORIGINS`

Start services:

```sh
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml up -d
```

Check health:

```sh
curl -fsS https://$AGENT_REMOTE_DOMAIN/healthz
```

Bootstrap the first administrator from the admin web. The normal CLI initialization flow does not create users.

## Node

Requirements on each VPS node:

- Docker with the Docker Sandbox CLI available.
- OpenSSH server.
- `tmux`.
- `mutagen` if the node runs node-side sync commands.
- TUN support for WireGuard networking.

The node installer checks these dependencies and prints explicit warnings when they are missing. It does not silently install Docker or OpenSSH because those packages usually require host-specific firewall, group, and daemon policy decisions.

Install the node:

```sh
curl -fsSL https://example.com/agent-remote-node/install-node.sh | sudo bash
```

Register the node from a registration token created in the admin web:

```sh
sudo agent-remote-node register \
  --config /etc/agent-remote-node/config.json \
  --server-url https://agent-remote.example.com \
  --node-id <node-id> \
  --registration-token <registration-token>
sudo systemctl enable --now agent-remote-node
```

## CLI

Install the packaged CLI for macOS or Linux, then run:

```sh
agent-remote init
agent-remote status --online
fclaude
```

`agent-remote init` configures the API URL, logs in with an existing user, registers the local device, writes local state, checks managed dependencies, and fetches WireGuard config when available.

## External Runtime Dependencies

Release packages should include or install:

- `agent-remote` CLI.
- `fclaude`.
- `agent-remote-wireguard` helper.
- Mutagen binary and license notice.
- Node binaries: `agent-remote-node`, `agent-remote-attach`.

The browser runtime defaults to the external `kasmweb/chrome:1.18.0` image. Deployments that mirror or redistribute that image must keep the exact image digest and notices.

## Automated Releases

Every repository uses a two-step release flow:

1. Run the `prepare-release` workflow on `main` with the target version.
2. Let the pushed `v*` tag trigger the release build.

The prepare workflow updates repository-owned version files, commits `chore: release vX.Y.Z`, pushes `main`, and then pushes the matching tag. Tag-triggered release workflows only build and publish artifacts; they do not modify source files.

- `agent-remote` publishes a deployment bundle containing `deploy/`, `docs/`, and license notices.
- `agent-remote-protocol` publishes a protocol bundle containing OpenAPI, JSON Schema, examples, docs, and notices.
- `agent-remote-server` publishes a GHCR image named `ghcr.io/<owner>/agent-remote-server`.
- `agent-remote-admin-web` publishes a GHCR image named `ghcr.io/<owner>/agent-remote-admin-web`.
- `agent-remote-node` publishes Linux release archives.
- `agent-remote-cli` publishes macOS and Linux release archives with managed Mutagen and the WireGuard helper.

Create a release from GitHub Actions by running `prepare-release` in the repositories that need to ship together. For local manual releases, run the repository's prepare script first, then commit and tag the same version:

```sh
scripts/prepare-release.sh 0.1.0
git add .
git commit -m "chore: release v0.1.0"
git tag v0.0.2
git push origin v0.0.2
```
