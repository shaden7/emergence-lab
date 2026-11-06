"""Fixed-writer artifact boundaries, including interrupted replacement slots."""
import json

import pytest

from emergence_lab import cs0_artifacts as artifacts


def test_oversized_json_leaves_old_checkpoint_untouched(tmp_path):
    path = tmp_path / 'manifest.json'
    artifacts.checkpoint(path, {'outcome': 'INCOMPLETE', 'stage': 'old'})
    previous = path.read_bytes()
    with pytest.raises(artifacts.ArtifactLimitError):
        artifacts.checkpoint(path, {'value': 'x' * artifacts.MAX_ARTIFACT_BYTES})
    assert path.read_bytes() == previous
    assert not path.with_suffix('.tmp').exists()


@pytest.mark.parametrize('record', [
    {'oversized': 'x' * artifacts.MAX_ARTIFACT_BYTES},
    {'bad': float('nan')}, {'bad': object()},
])
def test_rich_manifest_failure_has_durable_minimal_incomplete(tmp_path, record):
    path = tmp_path / 'manifest.json'
    result = artifacts.manifest_checkpoint(path, {'outcome': 'COMPLETE', **record})
    assert result['outcome'] == 'INCOMPLETE'
    assert result['stage'] == 'checkpoint-fallback'
    assert result == json.loads(path.read_text())
    assert path.stat().st_size < 1024
    assert not path.with_suffix('.tmp').exists()


def test_csv_oversize_refuses_before_open_or_replacement(tmp_path):
    path = tmp_path / 'measurements.csv'
    previous = b'value\r\nold\r\n'
    artifacts.atomic_write(path, previous)
    with pytest.raises(artifacts.ArtifactLimitError):
        artifacts.atomic_write(path, artifacts.csv_bytes(
            [{'value': 'x' * artifacts.MAX_ARTIFACT_BYTES}], ['value']))
    assert path.read_bytes() == previous
    assert not path.with_suffix('.tmp').exists()


def test_utf8_byte_limit_is_not_a_character_limit():
    with pytest.raises(artifacts.ArtifactLimitError):
        artifacts.csv_bytes([{'value': '\u00e9' * 20}], ['value'], max_bytes=30)


def test_replacements_reserve_both_old_and_temporary_slots(tmp_path, monkeypatch):
    path = tmp_path / 'manifest.json'
    limit = 1024
    original_replace = artifacts.os.replace
    observed = []
    def replace(source, target):
        sizes = [p.stat().st_size for p in tmp_path.iterdir() if p.is_file()]
        observed.append(sizes)
        assert max(sizes) <= limit
        assert sum(sizes) <= 2 * limit
        original_replace(source, target)
    monkeypatch.setattr(artifacts.os, 'replace', replace)
    for index in range(10):
        artifacts.checkpoint(path, {'index': index, 'text': 'x' * 900}, max_bytes=limit)
    assert len(observed[0]) == 1
    assert all(len(sizes) == 2 for sizes in observed[1:])
    assert json.loads(path.read_text())['index'] == 9
    assert not path.with_suffix('.tmp').exists()


def test_nine_slot_bound_includes_all_temporary_slots(tmp_path):
    assert len(artifacts.ENGINEERING_SLOTS) == 9
    assert artifacts.ENGINEERING_BOUND_BYTES == 9_000_000 < 50_000_000
    for name, limit in artifacts.ENGINEERING_SLOTS.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'x' * limit)
    sizes = artifacts.verify_engineering_slots(tmp_path)
    assert sum(sizes.values()) == artifacts.ENGINEERING_BOUND_BYTES
    target = tmp_path / 'worker/manifest.tmp'
    with target.open('ab') as stream:
        stream.write(b'x')
    with pytest.raises(artifacts.ArtifactLimitError):
        artifacts.verify_engineering_slots(tmp_path)


def test_unknown_file_and_symlink_refuse(tmp_path):
    unexpected = tmp_path / 'extra.bin'
    unexpected.write_bytes(b'')
    with pytest.raises(ValueError, match='unexpected'):
        artifacts.verify_engineering_slots(tmp_path)
    unexpected.unlink()
    (tmp_path / 'manifest.json').symlink_to(tmp_path / 'elsewhere')
    with pytest.raises(ValueError, match='symlink'):
        artifacts.verify_engineering_slots(tmp_path)


def test_exception_metadata_is_bounded_even_if_formatting_fails():
    assert len(artifacts.bounded_error(ValueError('x' * 2_000_000))) <= 1024
    class BrokenError(Exception):
        def __str__(self):
            raise TypeError('cannot format')
    assert 'formatting failed' in artifacts.bounded_error(BrokenError())
