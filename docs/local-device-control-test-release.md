# Local Device-Control Test Release

This package is for functional testing with non-sensitive data. The macOS application is ad-hoc
signed, the Docker services run in development mode, and the package is not notarized. It is not a
production release and cannot satisfy the production release-evidence gate.

## Start the control plane

Select the image archive matching the Docker host, load the two local images, then start PostgreSQL,
Redis, Server, and Admin Web:

```sh
case "$(uname -m)" in
  x86_64) image_arch=amd64 ;;
  arm64|aarch64) image_arch=arm64 ;;
  *) echo "unsupported image architecture: $(uname -m)" >&2; exit 1 ;;
esac
docker load -i "images/agent-remote-server-device-test-0.1.0-linux-${image_arch}.tar.gz"
docker load -i "images/agent-remote-admin-web-device-test-0.1.0-linux-${image_arch}.tar.gz"
docker compose \
  --env-file compose/.env.device-test \
  -f compose/docker-compose.yml \
  -f compose/docker-compose.device-test.yml \
  up -d postgres redis server admin-web
```

The API is available at `http://127.0.0.1:8000` and Admin Web at
`http://127.0.0.1:8080`. Device control is explicitly enabled only by the test override.

## Components

- `macos/Agent Remote Device.app.zip`: ad-hoc signed arm64 development application.
- `cli/`: native arm64 macOS CLI package.
- `node/`: Linux amd64 and arm64 glibc Node packages with the matching proxy embedded.
- `proxy/`: standalone Linux amd64 and arm64 glibc MCP proxies.
- `images/`: Linux amd64 and arm64 Server and Admin Web Docker image archives.

Managed proxy tar entries are normalized to numeric root ownership (`0:0`) on both
macOS and Linux packagers. The runtime rejects an extracted managed proxy directory
or binary that is not root-owned.

The production CLI intentionally rejects the ad-hoc application because it does not carry the
protected Apple Team ID. For this test build, unzip and launch the app directly. Full control still
fails closed unless the required local outbound-policy attestor and macOS permissions are present.
The repository-level synthetic `Server -> Node -> Rust -> Swift` E2E uses the real component
binaries and can be rerun with:

```sh
scripts/run-local-device-control-e2e.sh
```

The harness seeds only the user, device, node, and tool session, then uses the authenticated public
API to claim the tool session with `session_full_trust_v1` and advance the returned binding from
`pending_device` to `active` through `device-connected`. It passes the resulting dynamic session ID,
expiry, and lease to every peer. Through the real nested-TLS relay it first reads global clipboard
text without application state, launches `TextEdit` by its unique name and requires the first
bounded AX observation, then sends a follow-up `observe(auto)`. It requires monotonic
state-generation advances for GUI observations and no screenshot-generation advance across the
three operations.

Verify every packaged file before use:

```sh
shasum -a 256 -c SHA256SUMS
```
