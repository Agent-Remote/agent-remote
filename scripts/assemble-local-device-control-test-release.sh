#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
server_repo=$(cd "$root/../agent-remote-server" && pwd)
node_repo=$(cd "$root/../agent-remote-node" && pwd)
cli_repo=$(cd "$root/../agent-remote-cli" && pwd)
admin_repo=$(cd "$root/../agent-remote-admin-web" && pwd)
device_repo=$(cd "$root/../agent-remote-device" && pwd)
output="$root/dist/device-control-test-release"
manifest="$root/release-manifest.json"
release_version=$(jq -er .distribution_version "$manifest")
if ! [[ "$release_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+([-.+][0-9A-Za-z.-]+)?$ ]]; then
  echo "invalid distribution test-release version: $release_version" >&2
  exit 2
fi
server_version=$(jq -er '.components["agent-remote-server"].version' "$manifest")
node_version=$(jq -er '.components["agent-remote-node"].version' "$manifest")
cli_version=$(jq -er '.components["agent-remote-cli"].version' "$manifest")
admin_version=$(jq -er '.components["agent-remote-admin-web"].version' "$manifest")
device_version=$(jq -er '.components["agent-remote-device"].version' "$manifest")

app="$device_repo/dist/development/Agent Remote Device.app"
cli_archive="$cli_repo/dist/test-release/agent-remote-cli-$cli_version-aarch64-apple-darwin.tar.gz"
node_amd64="$node_repo/dist/test-release/agent-remote-node-$node_version-linux-amd64-glibc.tar.gz"
node_arm64="$node_repo/dist/test-release/agent-remote-node-$node_version-linux-arm64-glibc.tar.gz"
proxy_amd64="$device_repo/dist/test-release/device-proxies/linux-amd64-glibc"
proxy_arm64="$device_repo/dist/test-release/device-proxies/linux-arm64-glibc"
server_image="agent-remote-server:device-test-$server_version"
admin_image="agent-remote-admin-web:device-test-$admin_version"

for path in "$app" "$cli_archive" "$node_amd64" "$node_arm64" \
  "$proxy_amd64/agent-remote-device-proxy" "$proxy_amd64/VERSION" \
  "$proxy_amd64/SHA256SUMS" "$proxy_arm64/agent-remote-device-proxy" \
  "$proxy_arm64/VERSION" "$proxy_arm64/SHA256SUMS"; do
  if [ ! -e "$path" ] || [ -L "$path" ]; then
    echo "missing or unsafe test-release input: $path" >&2
    exit 1
  fi
done
for proxy_dir in "$proxy_amd64" "$proxy_arm64"; do
  (
    cd "$proxy_dir"
    shasum -a 256 --check SHA256SUMS
  )
done

docker buildx version >/dev/null

rm -rf "$output"
mkdir -p "$output/macos" "$output/cli" "$output/node" "$output/proxy" "$output/images"
cp -R "$root/deploy/compose" "$output/compose"
cp "$root/docs/local-device-control-test-release.md" "$output/README.md"

ditto -c -k --keepParent "$app" "$output/macos/Agent Remote Device.app.zip"
cp "$cli_archive" "$output/cli/"
cp "$node_amd64" "$node_arm64" "$output/node/"

package_managed_proxy() {
  local source_dir=$1
  local label=$2
  local staging="$output/proxy/.managed-$label"
  local archive="$output/proxy/agent-remote-device-proxy-$device_version-$label.tar.gz"
  mkdir -p "$staging/bin"
  install -m 0755 "$source_dir/agent-remote-device-proxy" \
    "$staging/bin/agent-remote-device-proxy"
  cp "$source_dir/VERSION" "$staging/VERSION"
  (
    cd "$staging"
    shasum -a 256 bin/agent-remote-device-proxy > SHA256SUMS
  )
  if tar --version 2>/dev/null | head -n 1 | grep -qi bsdtar; then
    tar --no-xattrs --uid 0 --gid 0 --uname root --gname root \
      -C "$staging" -czf "$archive" bin VERSION SHA256SUMS
  else
    tar --no-xattrs --owner=0 --group=0 --numeric-owner \
      -C "$staging" -czf "$archive" bin VERSION SHA256SUMS
  fi
  rm -rf "$staging"
}

package_managed_proxy "$proxy_amd64" linux-amd64-glibc
package_managed_proxy "$proxy_arm64" linux-arm64-glibc

build_image_archive() {
  local repository=$1
  local image=$2
  local component=$3
  local version=$4
  local architecture=$5
  local archive="$output/images/${component}-device-test-$version-linux-$architecture.tar"

  docker buildx build \
    --platform "linux/$architecture" \
    --build-arg "AGENT_REMOTE_VERSION=$version" \
    --tag "$image" \
    --output "type=docker,dest=$archive" \
    "$repository"
  gzip -9 "$archive"
}

for architecture in amd64 arm64; do
  build_image_archive "$server_repo" "$server_image" agent-remote-server "$server_version" "$architecture"
  build_image_archive "$admin_repo" "$admin_image" agent-remote-admin-web "$admin_version" "$architecture"
done

{
  printf 'kind=device-control-test-release\n'
  printf 'production_ready=false\n'
  printf 'distribution_version=%s\n' "$release_version"
  printf 'server_version=%s\n' "$server_version"
  printf 'node_version=%s\n' "$node_version"
  printf 'cli_version=%s\n' "$cli_version"
  printf 'admin_version=%s\n' "$admin_version"
  printf 'device_version=%s\n' "$device_version"
  printf 'image_platforms=linux/amd64,linux/arm64\n'
  printf 'created_at=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'root_head=%s\n' "$(git -C "$root" rev-parse HEAD)"
  printf 'server_head=%s\n' "$(git -C "$server_repo" rev-parse HEAD)"
  printf 'node_head=%s\n' "$(git -C "$node_repo" rev-parse HEAD)"
  printf 'cli_head=%s\n' "$(git -C "$cli_repo" rev-parse HEAD)"
  printf 'admin_head=%s\n' "$(git -C "$admin_repo" rev-parse HEAD)"
  printf 'device_head=%s\n' "$(git -C "$device_repo" rev-parse HEAD)"
} > "$output/BUILD-INFO.txt"

(
  cd "$output"
  find . -type f ! -name SHA256SUMS -print | LC_ALL=C sort | while IFS= read -r path; do
    shasum -a 256 "$path"
  done > SHA256SUMS
  shasum -a 256 -c SHA256SUMS
)

echo "$output"
