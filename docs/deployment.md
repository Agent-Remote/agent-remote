# Deployment

agent-remote provides a self-hosted deployment path for the control plane, admin web, node runtime, and local CLI packages.

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

Device control remains disabled in the example. Select either the default
`community-local-trust` profile documented in `community-local-trust-release.md` or the stricter
`apple-developer-id` profile documented in `device-control-release-evidence.md`, then set the
following deployment-owned values after that profile's release gates pass:

- `DEVICE_CONTROL_RELEASE_EVIDENCE_FILE`: signed manifest path mounted read-only. Official
  deployment bundles include the coordinated multi-architecture manifest and preconfigure this as
  `./device-control-release-evidence.json`; source checkouts keep the disabled `/dev/null` default.
- `DEVICE_CONTROL_RELEASE_PUBLIC_KEY`: Base64 raw Ed25519 verification key.
- `DEVICE_SESSION_RETENTION_DAYS`: approved non-zero terminal session metadata period.
- `DEVICE_SESSION_AUDIT_RETENTION_DAYS`: approved non-zero audit period, not shorter than the
  session period.
- `DEVICE_CONTROL_ENABLED=true`: set only after the preceding values and external policy are ready.
- `DEVICE_CONTROL_V2_ENABLED=true`: the default. Each new generation automatically uses the full
  Computer Use v2 capability set when the assigned Node advertises every required capability and
  otherwise falls back atomically to v1. Set it to `false` only as an emergency rollback for new
  generations; active generations never downgrade in place.

Production Server startup rejects an enabled capability when either retention period is zero or
the general signed schema 8 evidence cannot be verified. The evidence is shipped inside the same
root release/deployment bundle as `release-manifest.json` and is permanently valid for that exact
signed component/artifact composition; it is not renewed by changing a clock or copying a JSON file.
Computer Use v2 acceptance metadata is optional
quality evidence and does not authorize runtime capability negotiation. A schema 8
`community-local-trust` manifest may validly
declare `production_ready=true` while also declaring that Apple notarization, public distribution,
and automatic trust are unavailable. The deployment administrator explicitly accepts those limits;
the Compose setting does not turn them into Apple, MDM, or independent-review guarantees.

## Node

Requirements on each VPS node:

- Debian 12+ or Ubuntu 22.04+ with Linux 5.15+, systemd 249+, and cgroup v2.
- Root access, or a regular account with `sudo` access.
- TUN support for WireGuard networking when the deployment uses WireGuard.
- Docker with the Docker Sandbox CLI only when `docker_sandbox` compatibility is enabled.

The one-command installer installs missing Native Runtime packages and a consistent AI development command baseline, installs and pins Claude Code through Anthropic's official installer, installs a checksum-verified Node.js 22 runtime with npm and npx, configures the restricted SSH gateway and root runtime helper, registers the node, starts both systemd services, and verifies the runtime probe and control-plane heartbeat. It does not proactively upgrade OS packages already installed and does not install Docker.

Install the node:

```sh
curl -fsSL https://raw.githubusercontent.com/Agent-Remote/agent-remote-node/main/scripts/install.sh | \
  bash -s -- \
  --server-url https://agent-remote.example.com \
  --node-id <node-id> \
  --registration-token <registration-token>
```

The default backend is `native`. Add `--runtime-backends native,docker_sandbox` only after installing a Docker CLI that provides `docker sandbox`. Re-running the same command upgrades managed binaries and Claude while reusing the existing node token.

## CLI

Install the packaged CLI for macOS or Linux:

```sh
curl -fsSL https://raw.githubusercontent.com/Agent-Remote/agent-remote-cli/main/scripts/install.sh | bash
```

Initialize it:

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
- Node binaries: `agent-remote-node`, `agent-remote-attach`, and `agent-remote-runtime`.
- A versioned managed Claude Code runtime on Native nodes.

The browser runtime defaults to the external `kasmweb/chrome:1.18.0` image. Deployments that mirror or redistribute that image must keep the exact image digest and notices.

Production browser sessions require `browser_public_base_url` to point to a node-side HTTPS reverse proxy that exposes the KasmVNC endpoint used by signed `/stream` pages. Redis must be available because browser embed tokens are short-lived and validated through Redis.

## Automated Releases

Every component repository releases independently with a two-step flow:

1. Run the `prepare-release` workflow on `main` with the target version.
2. Let the pushed `v*` tag trigger the release build.

The prepare workflow updates only repository-owned version files, commits `chore: release vX.Y.Z`,
pushes `main`, and then pushes the matching tag. It never changes another repository's version.
Tag-triggered release workflows only build and publish artifacts; they do not modify source files.

- `agent-remote` publishes a deployment bundle containing `deploy/`, `docs/`, `scripts/`, license
  notices, and the automatically generated signed multi-architecture community release evidence.
- `agent-remote-server` publishes a GHCR image named `ghcr.io/<owner>/agent-remote-server`.
- `agent-remote-admin-web` publishes a GHCR image named `ghcr.io/<owner>/agent-remote-admin-web`.
- `agent-remote-node` publishes Linux release archives.
- `agent-remote-cli` publishes Windows x64/ARM64, macOS, and Linux release archives with managed Mutagen and the WireGuard helper. Windows packages integrate with the official WireGuard for Windows tunnel service and the built-in OpenSSH Client.

Release a component from its own repository whenever it is ready:

```sh
gh workflow run prepare-release.yml --ref main -f version=0.2.16
```

The root repository has a separate distribution version. `release-manifest.json` pins the exact
version, commit, and release-signing workflow of each supported production component. After a
component release, update its pin without changing any other component or the root distribution
version:

```sh
python3 scripts/update-release-component.py \
  agent-remote-server 0.3.1 FULL_40_CHARACTER_COMMIT_SHA \
  --release-workflow release.yml
python3 scripts/check-device-control-release-readiness.py \
  --manifest release-manifest.json --require-clean --require-tag --require-origin
```

Commit the manifest update and let CI validate the exact composition. When that composition is
ready for production, run the root `prepare-release` with a new root distribution version. The
root workflow downloads each component from its independently pinned tag, verifies the manifest
commit, signatures, SBOMs, provenance, vulnerability reports, and cross-component tests, then
publishes a deployment bundle whose Server and Admin images are pinned by digest.

For a local manual component release, run that repository's prepare script, then commit and tag its
own version:

```sh
scripts/prepare-release.sh 0.2.16
git add .
git commit -m "chore: release v0.2.16"
git tag v0.2.16
git push origin main v0.2.16
```
