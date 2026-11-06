"""Deterministic engineering failures only; no CS0 study seeds."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

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


@pytest.mark.parametrize('death_signal', [signal.SIGKILL, signal.SIGTERM])
def test_worker_stops_on_supervisor_death(checkout, tmp_path, death_signal):
    root, commit = checkout
    output = tmp_path / 'orphan-output'
    source = f'''
from pathlib import Path
import sys
from emergence_lab.cs0_supervisor import Limits, supervise
supervise([sys.executable, '-c', 'import time; time.sleep(30)'],
          Path({str(output)!r}), Path({str(root)!r}), {commit!r},
          Limits(wall_seconds=40))
'''
    # Launching supervisor imports the source under test; its worker uses fixture cwd.
    env = {**os.environ, 'PYTHONPATH': str(Path(__file__).resolve().parents[1] / 'src')}
    # Adopt and reap the orphan ourselves; /proc may expose a different PID
    # namespace, and container PID 1 need not reap zombies promptly.
    prctl = ctypes.CDLL(None, use_errno=True).prctl
    previous = ctypes.c_int()
    assert prctl(37, ctypes.byref(previous), 0, 0, 0) == 0  # GET_CHILD_SUBREAPER
    assert prctl(36, 1, 0, 0, 0) == 0  # SET_CHILD_SUBREAPER
    supervisor = subprocess.Popen([sys.executable, '-c', source], env=env)
    worker = None
    reaped = False
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            manifest = output / 'manifest.json'
            if manifest.exists():
                record = json.loads(manifest.read_text())
                if record['stage'] == 'worker':
                    worker = record['pid']
                    break
            if supervisor.poll() is not None:
                pytest.fail('supervisor exited before publishing worker PID')
            time.sleep(.01)
        assert worker is not None
        os.kill(worker, 0)
        supervisor.send_signal(death_signal)
        supervisor.wait(timeout=5)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            pid, status = os.waitpid(worker, os.WNOHANG)
            if pid:
                reaped = True
                assert os.waitstatus_to_exitcode(status) == -signal.SIGKILL
                break
            time.sleep(.01)
        assert reaped, 'worker survived supervisor death'
        durable = json.loads(manifest.read_text())
        assert durable['outcome'] == 'INCOMPLETE'
        assert durable['stage'] == 'worker'
    finally:
        if supervisor.poll() is None:
            supervisor.kill()
            supervisor.wait(timeout=5)
        if worker is not None and not reaped:
            try:
                os.killpg(worker, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                os.waitpid(worker, 0)
            except ChildProcessError:
                pass
        assert prctl(36, previous.value, 0, 0, 0) == 0


def test_parent_death_startup_race_fails_closed():
    result = subprocess.run([sys.executable, '-c', '''
import ctypes
from emergence_lab.cs0_supervisor import _parent_death_guard
_parent_death_guard(-1, ctypes.CDLL(None, use_errno=True).prctl)
raise AssertionError('mismatched parent must never execute worker')
'''], timeout=5)
    assert result.returncode == -signal.SIGKILL


def test_early_output_close_does_not_spin(checkout, tmp_path):
    start_cpu = time.process_time()
    result = run(checkout, tmp_path,
                 'import os,time; os.close(1); os.close(2); time.sleep(.6)')
    used_cpu = time.process_time() - start_cpu
    assert result['outcome'] == 'COMPLETE'
    assert result['output_bytes'] == 0
    assert used_cpu < .3, f'supervisor busy-spun for {used_cpu:.3f} CPU seconds'


def test_wall_stop_still_works_after_output_close(checkout, tmp_path):
    result = run(checkout, tmp_path,
                 'import os,time; os.close(1); os.close(2); time.sleep(20)',
                 Limits(wall_seconds=.2))
    assert result['outcome'] == 'INCOMPLETE'
    assert 'wall limit' in result['error']
    assert result['wall_seconds'] < 5
