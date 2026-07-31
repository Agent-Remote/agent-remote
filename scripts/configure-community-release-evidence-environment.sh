#!/usr/bin/env bash
set -euo pipefail

key_directory=${1:-dist/community-release-evidence-key}
repository=${GITHUB_REPOSITORY:-Agent-Remote/agent-remote}
environment=production-device-release-evidence
private_key="$key_directory/private-key.pem"

if [ ! -f "$private_key" ] || [ -L "$private_key" ]; then
  echo "missing or unsafe private key: $private_key" >&2
  exit 1
fi

gh api --method PUT "repos/$repository/environments/$environment" >/dev/null
gh secret set DEVICE_CONTROL_RELEASE_PRIVATE_KEY_PEM \
  --env "$environment" --repo "$repository" < "$private_key"
printf 'Configured %s for %s\n' "$environment" "$repository"

