#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace_root="$(cd "$repo_root/.." && pwd)"
cli_repo="${AGENT_REMOTE_CLI_REPO:-$workspace_root/agent-remote-cli}"
node_repo="${AGENT_REMOTE_NODE_REPO:-$workspace_root/agent-remote-node}"

if [[ ! -f "$cli_repo/Cargo.toml" || ! -f "$node_repo/go.mod" ]]; then
  echo "agent-remote-cli and agent-remote-node repositories must be sibling directories" >&2
  exit 2
fi

(cd "$cli_repo" && cargo build --bin agent-remote)
(cd "$node_repo" && go build -o "$node_repo/.e2e-agent-remote-attach" ./cmd/agent-remote-attach)
trap 'rm -f "$node_repo/.e2e-agent-remote-attach"' EXIT

python3 "$repo_root/tests/session_port_forwarding_e2e.py" \
  --cli "$cli_repo/target/debug/agent-remote" \
  --node-attach "$node_repo/.e2e-agent-remote-attach"
