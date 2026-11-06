"""Bounded artifacts for the reviewed, fixed-writer CS0 engineering pipeline.

This is not a filesystem quota or an arbitrary-code sandbox. Each admitted
regular-file slot has a one-million-byte ceiling; atomic replacement reserves
both old and temporary slots. Host wrapper files, filesystem metadata, runtime
scratch files and aggregate compute containment are outside this scope.
"""
from __future__ import annotations

import csv
import io
import json
import os
from pathlib import Path


MAX_ARTIFACT_BYTES = 1_000_000
ERROR_CHARACTERS = 1024
ENGINEERING_SLOTS = {
    name: MAX_ARTIFACT_BYTES for name in (
        'manifest.json', 'manifest.tmp',
        'worker/manifest.json', 'worker/manifest.tmp', 'worker/worker.bin',
        'measurements.csv', 'measurements.tmp', 'report.json', 'report.tmp',
    )
}
ENGINEERING_BOUND_BYTES = sum(ENGINEERING_SLOTS.values())


class ArtifactLimitError(ValueError):
    """Serialization would exceed an admitted artifact slot."""


def bounded_error(error: Exception) -> str:
    """Keep exception metadata bounded, even when exception formatting fails."""
    try:
        message = str(error)
    except Exception:
        message = '<exception formatting failed>'
    return (type(error).__name__ + ': ' + message[:ERROR_CHARACTERS])[:ERROR_CHARACTERS]


def safe_commit(commit) -> str | None:
    """Only admit an already bounded primitive identifier to initial records."""
    if (type(commit) is str and len(commit) == 40
            and all(c in '0123456789abcdef' for c in commit)):
        return commit
    return None


def json_bytes(record: dict, max_bytes: int = MAX_ARTIFACT_BYTES) -> bytes:
    """Serialize completely before opening a file, rejecting oversized output.

    Iterative encoding bounds retained serialization bytes. This is an artifact
    bound, not a bound on the input object's memory or encoder chunk allocation.
    """
    chunks, count = [], 0
    encoder = json.JSONEncoder(indent=2, sort_keys=True, allow_nan=False)
    for chunk in encoder.iterencode(record):
        encoded = chunk.encode('utf-8')
        count += len(encoded)
        if count + 1 > max_bytes:  # reserve the final newline
            raise ArtifactLimitError('JSON artifact exceeds its byte limit')
        chunks.append(encoded)
    return b''.join(chunks) + b'\n'


def csv_bytes(rows, columns: list[str], max_bytes: int = MAX_ARTIFACT_BYTES) -> bytes:
    """Pre-serialize rows while retaining at most one capped CSV artifact."""
    chunks, count = [], 0
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=columns)
    def retain():
        nonlocal count
        chunk = buffer.getvalue().encode('utf-8')
        count += len(chunk)
        if count > max_bytes:
            raise ArtifactLimitError('CSV artifact exceeds its byte limit')
        chunks.append(chunk)
        buffer.seek(0)
        buffer.truncate(0)
    writer.writeheader()
    retain()
    for row in rows:
        writer.writerow(row)
        retain()
    return b''.join(chunks)


def atomic_write(path: Path, payload: bytes, max_bytes: int = MAX_ARTIFACT_BYTES):
    """Replace a capped slot, with a separately reserved same-size .tmp slot."""
    if len(payload) > max_bytes:
        raise ArtifactLimitError('artifact exceeds its byte limit')
    temporary = path.with_suffix('.tmp')
    with temporary.open('wb') as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def checkpoint(path: Path, record: dict, max_bytes: int = MAX_ARTIFACT_BYTES):
    """An encoding refusal leaves the old durable manifest untouched."""
    atomic_write(path, json_bytes(record, max_bytes), max_bytes)


def manifest_checkpoint(path: Path, record: dict) -> dict:
    """Persist rich metadata or replace it with a minimal durable INCOMPLETE.

    Filesystem failures still propagate: no writer can promise persistence on a
    failed filesystem. Only encoding/size failures select the minimal fallback.
    """
    try:
        checkpoint(path, record)
        return record
    except (ValueError, TypeError, OverflowError, RecursionError):
        fallback = dict(outcome='INCOMPLETE', stage='checkpoint-fallback',
                        study_authorized=False,
                        error='rich manifest omitted: invalid or oversized metadata')
        if record.get('mode') == 'engineering':
            fallback['mode'] = 'engineering'
        commit = safe_commit(record.get('commit'))
        if commit is not None:
            fallback['commit'] = commit
        checkpoint(path, fallback)
        return fallback


def verify_engineering_slots(output: Path) -> dict[str, int]:
    """Check the fixed file set, including any interrupted atomic-write slots."""
    sizes = {}
    for path in output.rglob('*'):
        if path.is_symlink():
            raise ValueError('symlink in engineering artifact tree')
        if not path.is_file():
            continue
        name = path.relative_to(output).as_posix()
        if name not in ENGINEERING_SLOTS:
            raise ValueError('unexpected engineering artifact slot')
        size = path.stat().st_size
        if size > ENGINEERING_SLOTS[name]:
            raise ArtifactLimitError('engineering artifact exceeds slot byte limit')
        sizes[name] = size
    return sizes
