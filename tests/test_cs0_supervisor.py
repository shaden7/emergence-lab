"""Deterministic engineering failures only; no CS0 study seeds."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from emergence_lab.cs0_supervisor import Limits, supervise


@pytest.fixture
def checkout(tmp_path):
    root = tmp_path / 'repo'
    root.mkdir()
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    (root / 'source.txt').write_text('fixture\n')
    subprocess.run(['git', 'add', '.'], cwd=root, check=True)
    subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                    'commit', '-qm', 'fixture'], cwd=root, check=True)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    return root, commit


def run(checkout, tmp_path, code, limits=Limits()):
    root, commit = checkout
    result = supervise([sys.executable, '-c', code], tmp_path / 'out', root, commit, limits)
    assert result == json.loads((tmp_path / 'out/manifest.json').read_text())
    assert result['study_authorized'] is False
    return result


def test_success_and_digest(checkout, tmp_path):
    result = run(checkout, tmp_path, "print('engineering')")
    assert result['outcome'] == 'COMPLETE'
    assert result['output_sha256'] == hashlib.sha256(b'engineering\n').hexdigest()


@pytest.mark.parametrize('failure', ['dirty', 'untracked', 'wrong_commit'])
def test_provenance_refuses_before_worker(checkout, tmp_path, failure):
    root, commit = checkout
    if failure == 'wrong_commit':
        checkout = root, '0' * 40
    else:
        (root / ('source.txt' if failure == 'dirty' else 'extra.py')).write_text('changed')
    result = run(checkout, tmp_path, "raise Exception('MUST NOT RUN')")
    assert result['outcome'] == 'INCOMPLETE'
    assert 'pid' not in result
    assert not (tmp_path / 'out/worker.bin').exists()


def test_output_flood_is_truncated_and_preserved(checkout, tmp_path):
    result = run(checkout, tmp_path, "import os; os.write(1,b'x'*100000)",
                 Limits(output_bytes=1024))
    assert result['outcome'] == 'INCOMPLETE'
    assert 'output limit' in result['error']
    assert (tmp_path / 'out/worker.bin').stat().st_size == 1024


def test_wall_stop(checkout, tmp_path):
    result = run(checkout, tmp_path, 'import time; time.sleep(20)', Limits(wall_seconds=.15))
    assert result['outcome'] == 'INCOMPLETE'
    assert 'wall limit' in result['error']
    assert result['wall_seconds'] < 5


def test_cpu_stop(checkout, tmp_path):
    result = run(checkout, tmp_path, 'while True: pass', Limits(cpu_seconds=1, wall_seconds=5))
    assert result['outcome'] == 'INCOMPLETE'
    assert result['exit_code'] < 0
    assert result['worker_cpu_seconds'] < 2


def test_memory_stop(checkout, tmp_path):
    result = run(checkout, tmp_path, 'x=bytearray(512*1024**2)',
                 Limits(memory_bytes=128*1024**2))
    assert result['outcome'] == 'INCOMPLETE'
    assert result['exit_code'] != 0


def test_failure_and_invalid_setup(checkout, tmp_path):
    result = run(checkout, tmp_path, 'pass', Limits(output_bytes=0))
    assert result['outcome'] == 'INCOMPLETE'
    assert 'pid' not in result


def test_output_cannot_dirty_checkout(checkout):
    root, commit = checkout
    with pytest.raises(ValueError, match='outside'):
        supervise(['false'], root / 'results', root, commit)
    assert not (root / 'results').exists()


def test_worker_cannot_write_artifact_file(checkout, tmp_path):
    result = run(checkout, tmp_path, "with open('forbidden.bin','wb') as f: f.write(b'x'); f.flush()")
    assert result['outcome'] == 'INCOMPLETE'
    assert (checkout[0] / 'forbidden.bin').stat().st_size == 0
