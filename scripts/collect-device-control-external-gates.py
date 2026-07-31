#!/usr/bin/env python3
"""Collect exact external device-control gate reports from a protected runner."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import tarfile
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Iterator

_GATE_STATUS = {
    "security-tests": "passed",
    "security-review": "approved",
    "outbound-policy": "passed",
    "local-claude-isolation": "passed",
    "stop-revocation": "passed",
    "compatibility": "passed",
}
_TOP_LEVEL_KEYS = {
    "artifacts",
    "collected_at",
    "details",
    "evidence_sha256",
    "gate",
    "method",
    "producer",
    "release_version",
    "schema_version",
    "status",
}
_ARTIFACTS = {"server", "node", "application", "proxy"}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_MAXIMUM_JSON_BYTES = 1024 * 1024
_MAXIMUM_ARCHIVE_BYTES = 256 * 1024 * 1024
_MAXIMUM_EXPANDED_BYTES = 512 * 1024 * 1024
_MAXIMUM_ARCHIVE_MEMBERS = 4_096
_MAXIMUM_GATE_AGE = timedelta(days=30)


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build one JSON object while rejecting duplicate member names."""

    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


@contextmanager
def open_source_file(
    directory_descriptor: int, filename: str, maximum_bytes: int
) -> Iterator[BinaryIO]:
    """Open one bounded regular source file relative to the pinned source directory."""

    descriptor = os.open(
        filename,
        os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
        dir_fd=directory_descriptor,
    )
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError(f"external gate input is not a regular file: {filename}")
        if info.st_size <= 0 or info.st_size > maximum_bytes:
            raise ValueError(f"external gate input size is invalid: {filename}")
        with os.fdopen(descriptor, "rb") as source:
            descriptor = -1
            yield source
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def load_record(directory_descriptor: int, filename: str) -> tuple[dict[str, Any], bytes]:
    """Load one bounded external gate record with strict duplicate-key handling."""

    with open_source_file(directory_descriptor, filename, _MAXIMUM_JSON_BYTES) as source:
        raw_record = source.read(_MAXIMUM_JSON_BYTES + 1)
    if len(raw_record) > _MAXIMUM_JSON_BYTES:
        raise ValueError(f"external gate record is too large: {filename}")
    try:
        value = json.loads(raw_record, object_pairs_hook=reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"external gate record is not valid JSON: {filename}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"external gate record must be an object: {filename}")
    return value, raw_record


def parse_timestamp(value: object, name: str) -> datetime:
    """Parse one timezone-aware ISO 8601 timestamp."""

    if not isinstance(value, str):
        raise ValueError(f"{name} must be an ISO 8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO 8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must include a timezone")
    return parsed


def validate_record(value: dict[str, Any], gate: str, version: str, now: datetime) -> str:
    """Validate common external gate fields and return the raw evidence digest."""

    if set(value) != _TOP_LEVEL_KEYS:
        raise ValueError(f"{gate} record fields are invalid")
    if (
        isinstance(value["schema_version"], bool)
        or value["schema_version"] != 1
        or value["release_version"] != version
        or value["gate"] != gate
        or value["status"] != _GATE_STATUS[gate]
    ):
        raise ValueError(f"{gate} record identity is invalid")
    artifacts = value["artifacts"]
    if (
        not isinstance(artifacts, dict)
        or set(artifacts) != _ARTIFACTS
        or any(not isinstance(item, str) or not _SHA256.fullmatch(item) for item in artifacts.values())
    ):
        raise ValueError(f"{gate} artifact bindings are invalid")
    for field in ("producer", "method"):
        text = value[field]
        if not isinstance(text, str) or not text or text != text.strip() or len(text) > 500:
            raise ValueError(f"{gate} {field} is invalid")
    if not isinstance(value["details"], dict):
        raise ValueError(f"{gate} details must be an object")
    collected_at = parse_timestamp(value["collected_at"], f"{gate} collected_at")
    if collected_at > now or collected_at < now - _MAXIMUM_GATE_AGE:
        raise ValueError(f"{gate} collection time is outside the permitted window")
    evidence_digest = value["evidence_sha256"]
    if not isinstance(evidence_digest, str) or not _SHA256.fullmatch(evidence_digest):
        raise ValueError(f"{gate} raw evidence digest is invalid")
    return evidence_digest


def validate_archive(source: BinaryIO, gate: str) -> None:
    """Validate one bounded gzip tar without extracting it."""

    members = 0
    regular_files = 0
    expanded_bytes = 0
    names: set[str] = set()
    source.seek(0)
    try:
        with tarfile.open(fileobj=source, mode="r:gz") as archive:
            for member in archive:
                members += 1
                if members > _MAXIMUM_ARCHIVE_MEMBERS:
                    raise ValueError(f"{gate} evidence archive has too many members")
                member_path = PurePosixPath(member.name)
                canonical_name = member_path.as_posix()
                archived_name = member.name.rstrip("/") if member.isdir() else member.name
                if (
                    not member.name
                    or "\\" in member.name
                    or member_path.is_absolute()
                    or any(part in ("", ".", "..") for part in member_path.parts)
                    or archived_name != canonical_name
                    or member.name in names
                ):
                    raise ValueError(f"{gate} evidence archive member path is invalid")
                names.add(member.name)
                if member.isdir():
                    continue
                if not member.isfile() or member.size < 0:
                    raise ValueError(f"{gate} evidence archive member type is invalid")
                regular_files += 1
                expanded_bytes += member.size
                if expanded_bytes > _MAXIMUM_EXPANDED_BYTES:
                    raise ValueError(f"{gate} evidence archive expands beyond the limit")
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise ValueError(f"{gate} evidence archive member cannot be read")
                bytes_read = 0
                with extracted:
                    while chunk := extracted.read(1024 * 1024):
                        bytes_read += len(chunk)
                if bytes_read != member.size:
                    raise ValueError(f"{gate} evidence archive member is truncated")
    except (OSError, tarfile.TarError) as exc:
        raise ValueError(f"{gate} evidence archive is not a valid gzip tar") from exc
    if regular_files == 0 or expanded_bytes == 0:
        raise ValueError(f"{gate} evidence archive contains no report data")


def write_new(path: Path, source: BinaryIO | bytes) -> str:
    """Write one owner-only output without overwriting and return its SHA-256 digest."""

    digest = hashlib.sha256()
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            descriptor = -1
            if isinstance(source, bytes):
                output.write(source)
                digest.update(source)
            else:
                source.seek(0)
                while chunk := source.read(1024 * 1024):
                    output.write(chunk)
                    digest.update(chunk)
            output.flush()
            os.fsync(output.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    return digest.hexdigest()


def collect(source_directory: Path, output_directory: Path, version: str) -> None:
    """Validate and copy the exact external gate artifact from a protected runner directory."""

    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-.+][0-9A-Za-z.-]+)?", version):
        raise ValueError("release version is not semantic")
    expected_names = {
        f"{gate}{suffix}"
        for gate in _GATE_STATUS
        for suffix in (".json", ".evidence.tar.gz")
    }
    descriptor = os.open(
        source_directory,
        os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_DIRECTORY,
    )
    try:
        if set(os.listdir(descriptor)) != expected_names:
            raise ValueError("external gate source directory must contain exactly 12 expected files")
        output_directory.mkdir(mode=0o700, parents=False, exist_ok=False)
        try:
            now = datetime.now(UTC)
            for gate in _GATE_STATUS:
                record_name = f"{gate}.json"
                archive_name = f"{gate}.evidence.tar.gz"
                record, raw_record = load_record(descriptor, record_name)
                expected_digest = validate_record(record, gate, version, now)
                with open_source_file(descriptor, archive_name, _MAXIMUM_ARCHIVE_BYTES) as archive:
                    validate_archive(archive, gate)
                    actual_digest = write_new(output_directory / archive_name, archive)
                if actual_digest != expected_digest:
                    raise ValueError(f"{gate} raw evidence digest does not match")
                write_new(output_directory / record_name, raw_record)
        except Exception:
            shutil.rmtree(output_directory)
            raise
    finally:
        os.close(descriptor)


def main() -> None:
    """Parse command-line arguments and collect protected external gate evidence."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-directory", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--release-version", required=True)
    args = parser.parse_args()
    try:
        collect(args.source_directory, args.output_directory, args.release_version)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"external gate collection failed: {exc}") from exc


if __name__ == "__main__":
    main()
