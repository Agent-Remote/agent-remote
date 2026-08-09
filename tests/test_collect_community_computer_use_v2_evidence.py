import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path("scripts/collect-community-computer-use-v2-evidence.py")
VERSION = "1.2.3"


def run_collector(source: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--source-directory",
            str(source),
            "--output-directory",
            str(output),
            "--release-version",
            VERSION,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def write_inputs(source: Path) -> None:
    source.mkdir()
    archive = source / "community-computer-use-v2.evidence.tar.gz"
    archive.write_bytes(b"bounded-test-archive")
    record = {
        "schema_version": 1,
        "release_version": VERSION,
        "release_profile": "community-local-trust",
        "evidence_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }
    (source / "community-computer-use-v2-evidence.json").write_text(
        json.dumps(record), encoding="utf-8"
    )


def test_collector_copies_exact_protected_evidence_pair(tmp_path: Path) -> None:
    source = tmp_path / "source"
    output = tmp_path / "output"
    write_inputs(source)

    result = run_collector(source, output)

    assert result.returncode == 0, result.stderr
    assert {path.name for path in output.iterdir()} == {
        "community-computer-use-v2-evidence.json",
        "community-computer-use-v2.evidence.tar.gz",
    }
    assert all(path.stat().st_mode & 0o777 == 0o600 for path in output.iterdir())


def test_collector_rejects_archive_digest_mismatch(tmp_path: Path) -> None:
    source = tmp_path / "source"
    output = tmp_path / "output"
    write_inputs(source)
    (source / "community-computer-use-v2.evidence.tar.gz").write_bytes(b"changed")

    result = run_collector(source, output)

    assert result.returncode == 2
    assert "archive digest does not match" in result.stderr
    assert not output.exists()


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as first:
        test_collector_copies_exact_protected_evidence_pair(Path(first))
    with tempfile.TemporaryDirectory() as second:
        test_collector_rejects_archive_digest_mismatch(Path(second))
