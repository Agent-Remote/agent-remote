#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <version>" >&2
  echo "Example: $0 0.1.0" >&2
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

import re
import sys
from pathlib import Path

version = sys.argv[1]

deployment = Path("docs/deployment.md")
text = deployment.read_text()
text = re.sub(r"git tag v[0-9A-Za-z.+-]+", f"git tag v{version}", text)
text = re.sub(r"git push origin v[0-9A-Za-z.+-]+", f"git push origin v{version}", text)
deployment.write_text(text)
PY

echo "Prepared agent-remote deployment bundle v${VERSION}"
