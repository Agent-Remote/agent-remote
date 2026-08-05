#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <version>" >&2
  echo "Example: $0 0.2.1" >&2
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
import stat
import sys
import tempfile
from pathlib import Path

version = sys.argv[1]

Path("VERSION").write_text(f"{version}\n")

test_environment = Path("deploy/compose/.env.device-test")
text = test_environment.read_text()
text, count = re.subn(
    r"(?m)^AGENT_REMOTE_VERSION=[^\s]+$",
    f"AGENT_REMOTE_VERSION={version}",
    text,
    count=1,
)
if count != 1:
    raise SystemExit("test Compose version was not updated exactly once")
test_environment.write_text(text)

test_release = Path("docs/local-device-control-test-release.md")
text = test_release.read_text()
text = re.sub(
    r"agent-remote-server-device-test-[0-9A-Za-z.+-]+\.tar\.gz",
    f"agent-remote-server-device-test-{version}.tar.gz",
    text,
)
text = re.sub(
    r"agent-remote-admin-web-device-test-[0-9A-Za-z.+-]+\.tar\.gz",
    f"agent-remote-admin-web-device-test-{version}.tar.gz",
    text,
)
test_release.write_text(text)

script = Path("scripts/prepare-release.sh")
text = script.read_text()
text = re.sub(r"Example: \$0 [0-9A-Za-z.+-]+", f"Example: $0 {version}", text)
mode = stat.S_IMODE(script.stat().st_mode)
with tempfile.NamedTemporaryFile(
    mode="w", encoding="utf-8", dir=script.parent, delete=False
) as temporary:
    temporary.write(text)
replacement = Path(temporary.name)
replacement.chmod(mode)
replacement.replace(script)

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
