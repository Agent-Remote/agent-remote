#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace_root="$(cd "$repo_root/.." && pwd)"
server_repo="${AGENT_REMOTE_SERVER_REPO:-$workspace_root/agent-remote-server}"
node_repo="${AGENT_REMOTE_NODE_REPO:-$workspace_root/agent-remote-node}"
device_repo="${AGENT_REMOTE_DEVICE_REPO:-$workspace_root/agent-remote-device}"

if [[ ! -x "$server_repo/.venv/bin/python" || ! -f "$node_repo/go.mod" || ! -f "$device_repo/Cargo.toml" ]]; then
  echo "server, node, and device repositories must be available as sibling directories" >&2
  exit 2
fi

"$server_repo/.venv/bin/python" "$repo_root/tests/local_device_control_e2e.py" \
  --server-repo "$server_repo" \
  --node-repo "$node_repo" \
  --device-repo "$device_repo" \
  "$@"
