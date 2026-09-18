#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <version>" >&2
}

if [[ $# -ne 1 ]]; then
  usage
  exit 2
fi

VERSION="${1#v}"
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([-.+][0-9A-Za-z.-]+)?$ ]]; then
  echo "Invalid semantic version: $1" >&2
  exit 2
fi

python3 - "$VERSION" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

version = sys.argv[1]

Path("VERSION").write_text(f"{version}\n")

manifest = Path("release-manifest.json")
document = json.loads(manifest.read_text(encoding="utf-8"))
document["distribution_version"] = version
manifest.write_text(
    json.dumps(document, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

scripts/update-changelog.sh "$VERSION"

echo "Prepared agent-remote deployment bundle v${VERSION}"
