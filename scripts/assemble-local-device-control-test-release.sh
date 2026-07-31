#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
server_repo=$(cd "$root/../agent-remote-server" && pwd)
node_repo=$(cd "$root/../agent-remote-node" && pwd)
cli_repo=$(cd "$root/../agent-remote-cli" && pwd)
admin_repo=$(cd "$root/../agent-remote-admin-web" && pwd)
device_repo=$(cd "$root/../agent-remote-device" && pwd)
output="$root/dist/device-control-test-release"
release_version=$(tr -d '[:space:]' < "$root/VERSION")
if ! [[ "$release_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+([-.+][0-9A-Za-z.-]+)?$ ]]; then
  echo "invalid coordinated test-release version: $release_version" >&2
  exit 2
fi

app="$device_repo/dist/development/Agent Remote Device.app"
cli_archive="$cli_repo/dist/test-release/agent-remote-cli-$release_version-aarch64-apple-darwin.tar.gz"
node_amd64="$node_repo/dist/test-release/agent-remote-node-$release_version-linux-amd64-glibc.tar.gz"
node_arm64="$node_repo/dist/test-release/agent-remote-node-$release_version-linux-arm64-glibc.tar.gz"
proxy_amd64="$device_repo/dist/test-release/device-proxies/linux-amd64-glibc"
proxy_arm64="$device_repo/dist/test-release/device-proxies/linux-arm64-glibc"
server_image="agent-remote-server:device-test-$release_version"
admin_image="agent-remote-admin-web:device-test-$release_version"

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

docker image inspect "$server_image" >/dev/null
docker image inspect "$admin_image" >/dev/null

rm -rf "$output"
mkdir -p "$output/macos" "$output/cli" "$output/node" "$output/proxy" "$output/images"
cp -R "$root/deploy/compose" "$output/compose"
cp "$root/docs/local-device-control-test-release.md" "$output/README.md"

ditto -c -k --keepParent "$app" "$output/macos/Agent Remote Device.app.zip"
cp "$cli_archive" "$output/cli/"
cp "$node_amd64" "$node_arm64" "$output/node/"
tar -C "$proxy_amd64" -czf "$output/proxy/agent-remote-device-proxy-$release_version-linux-amd64-glibc.tar.gz" .
tar -C "$proxy_arm64" -czf "$output/proxy/agent-remote-device-proxy-$release_version-linux-arm64-glibc.tar.gz" .
docker save "$server_image" | gzip -9 > \
  "$output/images/agent-remote-server-device-test-$release_version.tar.gz"
docker save "$admin_image" | gzip -9 > \
  "$output/images/agent-remote-admin-web-device-test-$release_version.tar.gz"

{
  printf 'kind=device-control-test-release\n'
  printf 'production_ready=false\n'
  printf 'release_version=%s\n' "$release_version"
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
