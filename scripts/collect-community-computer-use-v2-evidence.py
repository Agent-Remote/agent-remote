#!/usr/bin/env python3
"""Collect bounded Community Computer Use v2 evidence from a protected Mac."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
from pathlib import Path

RECORD_NAME = "community-computer-use-v2-evidence.json"
ARCHIVE_NAME = "community-computer-use-v2.evidence.tar.gz"
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-.+][0-9A-Za-z.-]+)?$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
MAXIMUM_RECORD_BYTES = 1024 * 1024
MAXIMUM_ARCHIVE_BYTES = 256 * 1024 * 1024


def open_source(directory: int, name: str, maximum_bytes: int) -> int:
    """Open one bounded regular source file without following a symlink."""

    descriptor = os.open(
        name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=directory
    )
    info = os.fstat(descriptor)
    if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= maximum_bytes:
        os.close(descriptor)
        raise ValueError(f"unsafe Community Computer Use v2 input: {name}")
    return descriptor


def copy_new(source: int, output: Path) -> str:
    """Copy a pinned descriptor into an owner-only output and return its digest."""

    value = hashlib.sha256()
    os.lseek(source, 0, os.SEEK_SET)
    output_descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with (
        os.fdopen(os.dup(source), "rb") as input_file,
        os.fdopen(output_descriptor, "wb") as output_file,
    ):
        while chunk := input_file.read(1024 * 1024):
            output_file.write(chunk)
            value.update(chunk)
        output_file.flush()
        os.fsync(output_file.fileno())
    return value.hexdigest()


def collect(source_directory: Path, output_directory: Path, version: str) -> None:
    """Validate the protected input identity and copy the exact evidence pair."""

    if SEMVER.fullmatch(version) is None:
        raise ValueError("release version is invalid")
    directory = os.open(
        source_directory, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_DIRECTORY
    )
    try:
        if set(os.listdir(directory)) != {RECORD_NAME, ARCHIVE_NAME}:
            raise ValueError(
                "Community Computer Use v2 directory must contain exactly two files"
            )
        record_descriptor = open_source(directory, RECORD_NAME, MAXIMUM_RECORD_BYTES)
        archive_descriptor = open_source(directory, ARCHIVE_NAME, MAXIMUM_ARCHIVE_BYTES)
        try:
            with os.fdopen(os.dup(record_descriptor), "rb") as source:
                record = json.load(source)
            if (
                not isinstance(record, dict)
                or record.get("schema_version") != 1
                or record.get("release_version") != version
                or record.get("release_profile") != "community-local-trust"
            ):
                raise ValueError("Community Computer Use v2 record identity is invalid")
            output_directory.mkdir(mode=0o700, parents=False, exist_ok=False)
            try:
                archive_digest = copy_new(
                    archive_descriptor, output_directory / ARCHIVE_NAME
                )
                if (
                    record.get("evidence_sha256") != archive_digest
                    or SHA256.fullmatch(str(record.get("evidence_sha256", ""))) is None
                ):
                    raise ValueError(
                        "Community Computer Use v2 archive digest does not match"
                    )
                copy_new(record_descriptor, output_directory / RECORD_NAME)
            except Exception:
                shutil.rmtree(output_directory)
                raise
        finally:
            os.close(record_descriptor)
            os.close(archive_descriptor)
    finally:
        os.close(directory)


def main() -> None:
    """Collect one protected Community Computer Use v2 evidence pair."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-directory", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--release-version", required=True)
    args = parser.parse_args()
    try:
        collect(args.source_directory, args.output_directory, args.release_version)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Community Computer Use v2 collection failed: {exc}\n")


if __name__ == "__main__":
    main()
