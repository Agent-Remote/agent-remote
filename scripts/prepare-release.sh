#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <version>" >&2
  echo "Example: $0 0.0.4" >&2
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

script = Path("scripts/prepare-release.sh")
text = script.read_text()
text = re.sub(r"Example: \$0 [0-9A-Za-z.+-]+", f"Example: $0 {version}", text)
script.write_text(text)

smoke = Path("scripts/e2e-smoke.sh")
text = smoke.read_text()
text = re.sub(r'VERSION="\$\{AGENT_REMOTE_VERSION:-[0-9A-Za-z.+-]+\}"', f'VERSION="${{AGENT_REMOTE_VERSION:-{version}}}"', text)
smoke.write_text(text)

acceptance = Path("docs/e2e-acceptance.md")
text = acceptance.read_text()
text = re.sub(r"AGENT_REMOTE_VERSION=[0-9A-Za-z.+-]+ scripts/e2e-smoke\.sh", f"AGENT_REMOTE_VERSION={version} scripts/e2e-smoke.sh", text)
acceptance.write_text(text)

deployment = Path("docs/deployment.md")
text = deployment.read_text()
text = re.sub(r"gh workflow run prepare-release\.yml --ref main -f version=[0-9A-Za-z.+-]+", f"gh workflow run prepare-release.yml --ref main -f version={version}", text)
text = re.sub(r"scripts/prepare-release\.sh [0-9A-Za-z.+-]+", f"scripts/prepare-release.sh {version}", text)
text = re.sub(r'git commit -m "chore: release v[0-9A-Za-z.+-]+"', f'git commit -m "chore: release v{version}"', text)
text = re.sub(r"git tag v[0-9A-Za-z.+-]+", f"git tag v{version}", text)
text = re.sub(r"git push origin main v[0-9A-Za-z.+-]+", f"git push origin main v{version}", text)
text = re.sub(r"git push origin v[0-9A-Za-z.+-]+", f"git push origin v{version}", text)
deployment.write_text(text)
PY

scripts/update-changelog.sh "$VERSION"

echo "Prepared agent-remote deployment bundle v${VERSION}"
