#!/usr/bin/env bash
set -euo pipefail

output=${1:-dist/community-release-evidence-key}
if [ -e "$output" ]; then
  echo "output path already exists: $output" >&2
  exit 1
fi
mkdir -m 0700 -p "$output"
openssl genpkey -algorithm ED25519 -out "$output/private-key.pem"
openssl pkey -in "$output/private-key.pem" -pubout -out "$output/public-key.pem"
openssl pkey -in "$output/private-key.pem" -pubout -outform DER \
  | tail -c 32 | base64 | tr -d '\n' > "$output/public-key-base64.txt"
printf '\n' >> "$output/public-key-base64.txt"
chmod 0600 "$output/private-key.pem"
chmod 0644 "$output/public-key.pem" "$output/public-key-base64.txt"
printf 'Release evidence key created at %s\n' "$output"
printf 'Back up the private key securely before configuring GitHub.\n'

