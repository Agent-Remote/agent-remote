#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <version>" >&2
  exit 2
fi

VERSION="${1#v}"
DATE="${RELEASE_DATE:-$(date -u +%Y-%m-%d)}"
PREVIOUS_TAG="$(git tag --list 'v[0-9]*' --sort=-v:refname | grep -v "^v${VERSION}$" | head -n 1 || true)"

if [ -n "$PREVIOUS_TAG" ]; then
  RANGE="${PREVIOUS_TAG}..HEAD"
else
  RANGE="HEAD"
fi

TMP="$(mktemp)"
{
  echo "# Changelog"
  echo
  echo "All notable changes to this repository are recorded here."
  echo
  echo "## v${VERSION} - ${DATE}"
  echo
  NOTES="$(git log --no-merges --pretty=format:'- %s (%h)' "$RANGE" || true)"
  if [ -n "$NOTES" ]; then
    printf "%s\n" "$NOTES"
  else
    echo "- Release metadata update."
  fi
  echo
  if [ -f CHANGELOG.md ]; then
    awk -v version="v${VERSION}" '
      /^## / {
        keep = 1
        skip = ($2 == version)
      }
      keep && !skip { print }
    ' CHANGELOG.md
  fi
} > "$TMP"

mv "$TMP" CHANGELOG.md
