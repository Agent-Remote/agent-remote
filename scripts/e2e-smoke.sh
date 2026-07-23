#!/usr/bin/env bash
set -euo pipefail

VERSION="${AGENT_REMOTE_VERSION:-0.0.4}"
OWNER="${AGENT_REMOTE_OWNER:-Agent-Remote}"
NETWORK_CHECKS="${AGENT_REMOTE_SMOKE_NETWORK:-1}"
COMPOSE_CHECKS="${AGENT_REMOTE_SMOKE_COMPOSE:-1}"
IMAGE_CHECKS="${AGENT_REMOTE_SMOKE_IMAGES:-0}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${VERSION#v}"

failures=0

log() {
  printf '%s\n' "$*"
}

ok() {
  log "ok  $*"
}

fail() {
  log "err $*" >&2
  failures=$((failures + 1))
}

need_cmd() {
  if command -v "$1" >/dev/null 2>&1; then
    ok "found $1"
  else
    fail "missing required command: $1"
  fi
}

check_url() {
  local label="$1"
  local url="$2"
  if curl --fail --silent --show-error --location --head --retry 3 --retry-all-errors --max-time 30 "$url" >/dev/null; then
    ok "$label"
  else
    fail "$label: $url"
  fi
}

check_release_tag() {
  local repo="$1"
  check_url "$repo release tag v$VERSION" "https://github.com/$OWNER/$repo/releases/tag/v$VERSION"
}

check_release_asset() {
  local repo="$1"
  local asset="$2"
  check_url "$repo asset $asset" "https://github.com/$OWNER/$repo/releases/download/v$VERSION/$asset"
}

check_raw_script() {
  local repo="$1"
  local path="$2"
  check_url "$repo raw $path" "https://raw.githubusercontent.com/$OWNER/$repo/main/$path"
}

check_image() {
  local image="$1"
  if docker manifest inspect "$image" >/dev/null 2>&1; then
    ok "image manifest $image"
  else
    fail "image manifest $image"
  fi
}

log "agent-remote E2E smoke"
log "version: v$VERSION"
log "owner:   $OWNER"
log ""

need_cmd curl
need_cmd docker

if [ "$COMPOSE_CHECKS" = "1" ]; then
  if docker compose version >/dev/null 2>&1; then
    if docker compose \
      --env-file "$ROOT_DIR/deploy/compose/.env.example" \
      -f "$ROOT_DIR/deploy/compose/docker-compose.yml" \
      config --quiet; then
      ok "compose bundle validates"
    else
      fail "compose bundle validates"
    fi
  else
    fail "docker compose plugin is unavailable"
  fi
else
  log "skip compose checks"
fi

if [ "$NETWORK_CHECKS" = "1" ]; then
  check_release_tag agent-remote
  check_release_asset agent-remote "agent-remote-deploy-$VERSION.tar.gz"

  check_release_tag agent-remote-server
  check_release_tag agent-remote-admin-web

  check_release_tag agent-remote-cli
  check_release_asset agent-remote-cli "agent-remote-cli-$VERSION-x86_64-unknown-linux-gnu.tar.gz"
  check_release_asset agent-remote-cli "agent-remote-cli-$VERSION-aarch64-unknown-linux-gnu.tar.gz"
  check_release_asset agent-remote-cli "agent-remote-cli-$VERSION-x86_64-apple-darwin.tar.gz"
  check_release_asset agent-remote-cli "agent-remote-cli-$VERSION-aarch64-apple-darwin.tar.gz"
  check_raw_script agent-remote-cli scripts/install.sh

  check_release_tag agent-remote-node
  check_release_asset agent-remote-node "agent-remote-node-$VERSION-darwin-amd64.tar.gz"
  check_release_asset agent-remote-node "agent-remote-node-$VERSION-darwin-arm64.tar.gz"
  check_release_asset agent-remote-node "agent-remote-node-$VERSION-linux-amd64-glibc.tar.gz"
  check_release_asset agent-remote-node "agent-remote-node-$VERSION-linux-arm64-glibc.tar.gz"
  check_release_asset agent-remote-node "agent-remote-node-$VERSION-linux-amd64-musl.tar.gz"
  check_release_asset agent-remote-node "agent-remote-node-$VERSION-linux-arm64-musl.tar.gz"
  check_raw_script agent-remote-node scripts/install.sh
else
  log "skip network checks"
fi

if [ "$IMAGE_CHECKS" = "1" ]; then
  check_image "ghcr.io/agent-remote/agent-remote-server:$VERSION"
  check_image "ghcr.io/agent-remote/agent-remote-admin-web:$VERSION"
fi

log ""
if [ "$failures" -eq 0 ]; then
  log "smoke result: pass"
  exit 0
fi

log "smoke result: failed ($failures)"
exit 1
