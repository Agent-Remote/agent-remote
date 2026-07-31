import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "collect-device-control-external-gates.py"
GATES = {
    "security-tests": "passed",
    "security-review": "approved",
    "outbound-policy": "passed",
    "local-claude-isolation": "passed",
    "stop-revocation": "passed",
    "compatibility": "passed",
}


def create_archive(path: Path, gate: str) -> None:
    data = f"real external evidence placeholder for contract test: {gate}\n".encode()
    with tarfile.open(path, "w:gz") as archive:
        info = tarfile.TarInfo(f"{gate}/report.txt")
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))


def create_source(path: Path, version: str = "1.2.3") -> None:
    path.mkdir()
    digests = {name: "a" * 64 for name in ("server", "node", "application", "proxy")}
    for gate, status in GATES.items():
        archive = path / f"{gate}.evidence.tar.gz"
        create_archive(archive, gate)
        record = {
            "schema_version": 1,
            "release_version": version,
            "gate": gate,
            "status": status,
            "artifacts": digests,
            "collected_at": datetime.now(UTC).isoformat(),
            "producer": "contract test",
            "method": "fixture",
            "evidence_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "details": {},
        }
        (path / f"{gate}.json").write_text(json.dumps(record), encoding="utf-8")


def run_collector(source: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--source-directory",
            str(source),
            "--output-directory",
            str(output),
            "--release-version",
            "1.2.3",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_collector_copies_exact_validated_gate_set() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "source"
        output = root / "output"
        create_source(source)

        result = run_collector(source, output)

        assert result.returncode == 0, result.stderr
        assert {path.name for path in output.iterdir()} == {
            f"{gate}{suffix}"
            for gate in GATES
            for suffix in (".json", ".evidence.tar.gz")
        }


def test_collector_rejects_extra_files_symlinks_and_digest_mismatch() -> None:
    for mutation in ("extra", "symlink", "digest"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            output = root / "output"
            create_source(source)
            if mutation == "extra":
                (source / "unexpected.txt").write_text("unexpected", encoding="utf-8")
            elif mutation == "symlink":
                record = source / "security-tests.json"
                target = source / "record-target"
                record.rename(target)
                record.symlink_to(target)
            else:
                record = source / "security-tests.json"
                value = json.loads(record.read_text(encoding="utf-8"))
                value["evidence_sha256"] = "b" * 64
                record.write_text(json.dumps(value), encoding="utf-8")

            result = run_collector(source, output)

            assert result.returncode != 0
            assert not output.exists()


def test_collector_rejects_duplicate_json_and_unsafe_archive_member() -> None:
    for mutation in ("duplicate", "unsafe_archive"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            output = root / "output"
            create_source(source)
            record = source / "security-tests.json"
            if mutation == "duplicate":
                raw = record.read_text(encoding="utf-8")
                record.write_text(raw.replace('{"schema_version": 1', '{"schema_version": 1, "schema_version": 1'), encoding="utf-8")
            else:
                archive = source / "security-tests.evidence.tar.gz"
                with tarfile.open(archive, "w:gz") as tar:
                    data = b"unsafe"
                    info = tarfile.TarInfo("../report.txt")
                    info.size = len(data)
                    tar.addfile(info, io.BytesIO(data))
                value = json.loads(record.read_text(encoding="utf-8"))
                value["evidence_sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
                record.write_text(json.dumps(value), encoding="utf-8")

            result = run_collector(source, output)

            assert result.returncode != 0
            assert not output.exists()


if __name__ == "__main__":
    test_collector_copies_exact_validated_gate_set()
    test_collector_rejects_extra_files_symlinks_and_digest_mismatch()
    test_collector_rejects_duplicate_json_and_unsafe_archive_member()
