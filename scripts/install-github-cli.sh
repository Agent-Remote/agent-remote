#!/usr/bin/env bash
set -euo pipefail

version=2.89.0
archive="gh_${version}_linux_amd64.tar.gz"
expected_sha256=d0422caade520530e76c1c558da47daebaa8e1203d6b7ff10ad7d6faba3490d8

if [[ "${RUNNER_OS:-Linux}" != "Linux" || "${RUNNER_ARCH:-X64}" != "X64" ]]; then
  echo "GitHub CLI installer only supports Linux X64 runners" >&2
  exit 1
fi

runner_temp=${RUNNER_TEMP:-$(mktemp -d)}
download="$runner_temp/$archive"
checksum="$runner_temp/$archive.sha256"
extract=$(mktemp -d "$runner_temp/github-cli-$version.XXXXXX")

curl --fail --location --retry 3 --output "$download" \
  "https://github.com/cli/cli/releases/download/v${version}/${archive}"
echo "$expected_sha256  $archive" > "$checksum"
(cd "$runner_temp" && sha256sum --check "$checksum")
tar -xzf "$download" --strip-components=1 -C "$extract"

"$extract/bin/gh" version
if [[ -n "${GITHUB_PATH:-}" ]]; then
  echo "$extract/bin" >> "$GITHUB_PATH"
else
  echo "Add $extract/bin to PATH" >&2
fi
