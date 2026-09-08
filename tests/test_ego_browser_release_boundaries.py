"""Focused trust-boundary tests for Bridge release evidence inputs."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import sys
import tarfile
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/assemble-community-device-control-release-evidence.py"
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("community_evidence", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def archive_with_members(path: Path, members: list[tuple[str, str, str]]) -> None:
    """Write a small gzip tar from (kind, name, value) tuples."""

    with tarfile.open(path, mode="w:gz") as archive:
        for kind, name, value in members:
            if kind == "file":
                data = value.encode("utf-8")
                member = tarfile.TarInfo(name)
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
            elif kind == "dir":
                member = tarfile.TarInfo(name)
                member.type = tarfile.DIRTYPE
                member.mode = 0o555
                archive.addfile(member)
            elif kind == "symlink":
                member = tarfile.TarInfo(name)
                member.type = tarfile.SYMTYPE
                member.linkname = value
                archive.addfile(member)
            elif kind == "hardlink":
                member = tarfile.TarInfo(name)
                member.type = tarfile.LNKTYPE
                member.linkname = value
                archive.addfile(member)
            else:
                raise AssertionError(f"unknown archive member kind: {kind}")


def assert_rejected(callback) -> None:
    try:
        callback()
    except ValueError:
        return
    raise AssertionError("unsafe release input was accepted")


def test_bridge_archive_rejects_dot_and_duplicate_normalized_paths() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        dot_archive = root / "dot.tar.gz"
        archive_with_members(dot_archive, [("dir", ".", "")])
        assert_rejected(
            lambda: MODULE.validate_archive_members(
                dot_archive, require_learning_bundle=False
            )
        )

        duplicate_archive = root / "duplicate.tar.gz"
        archive_with_members(
            duplicate_archive,
            [
                ("file", "learning-bundle/manifest.json", "{}"),
                ("dir", "learning-bundle/manifest.json/", ""),
            ],
        )
        assert_rejected(
            lambda: MODULE.validate_archive_members(
                duplicate_archive, require_learning_bundle=False
            )
        )


def test_bridge_archive_rejects_symlink_and_hardlink_members() -> None:
    for kind in ("symlink", "hardlink"):
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / f"{kind}.tar.gz"
            archive_with_members(
                archive,
                [(kind, "learning-bundle/escape", "../../outside")],
            )
            assert_rejected(
                lambda archive=archive: MODULE.validate_archive_members(
                    archive, require_learning_bundle=False
                )
            )


def test_bridge_archive_accepts_only_canonical_regular_members() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        archive = Path(temporary) / "valid.tar.gz"
        archive_with_members(
            archive,
            [
                ("dir", "learning-bundle", ""),
                ("dir", "learning-bundle/learnings", ""),
                ("file", "learning-bundle/manifest.json", "{}"),
                ("file", "learning-bundle/learnings/example", "signed"),
            ],
        )
        MODULE.validate_archive_members(archive, require_learning_bundle=True)


def test_learning_bundle_rejects_writable_directory() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        bundle = Path(temporary) / "bundle"
        (bundle / "learnings").mkdir(parents=True)
        (bundle / "manifest.json").write_text("{}", encoding="utf-8")
        for path in (bundle, bundle / "learnings", bundle / "manifest.json"):
            path.chmod(0o555 if path.is_dir() else 0o444)
        (bundle / "learnings").chmod(0o755)
        assert_rejected(lambda: MODULE.validate_read_only_tree(bundle, "bundle"))


def test_bridge_checksum_rejects_path_qualified_filename() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        target = root / "archive.tar.gz"
        target.write_bytes(b"release")
        checksum = root / "archive.tar.gz.sha256"
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        checksum.write_text(f"{digest}  nested/archive.tar.gz\n", encoding="ascii")
        assert_rejected(
            lambda: MODULE.validate_checksum_file(checksum, target, "archive")
        )
