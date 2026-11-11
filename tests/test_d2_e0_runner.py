"""D2-E0 runner: containment, provenance, classification and failure paths.

Small engineering fixtures only (N<=10); the target N=2..32 is never evaluated.
"""
from __future__ import annotations

import copy
import json
import math
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time

import pytest

pytest.importorskip('mpmath')
from emergence_lab import d2_e0_reference as ref  # noqa: E402
from emergence_lab import d2_e0_runner as runner  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    sys.platform != 'linux' or platform.machine() not in ('x86_64', 'aarch64'),
    reason='partitioned containment is Linux x86_64/aarch64 only')

PYC = ['-X', f'pycache_prefix={runner.NO_PYCACHE}']
LAUNCH = ("import sys; sys.path.insert(0, sys.argv[1] + '/src'); "
          "import emergence_lab.d2_e0_runner as r; raise SystemExit(r.main(sys.argv[2:]))")


def _git(cwd, *args):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()


@pytest.fixture(scope='module')
def pinned(tmp_path_factory):
    """A clean clone of the working tree's content committed at one exact SHA."""
    base = tmp_path_factory.mktemp('pin')
    clone = base / 'repo'
    subprocess.check_call(['git', 'init', '-q', str(clone)])
    for name in _git(REPO, 'ls-files', '-co', '--exclude-standard', '--', 'src', runner.PROTOCOL, '.gitignore').splitlines():
        source = REPO / name
        if source.is_file() and '__pycache__' not in name and '.egg-info' not in name:
            target = clone / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
    subprocess.check_call(['git', 'add', '-A'], cwd=clone)
    subprocess.check_call(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'pin'], cwd=clone)
    return clone, _git(clone, 'rev-parse', 'HEAD')


def _launch(clone, commit, output, sizes, extra=()):
    return subprocess.run([sys.executable, '-I', '-B', *PYC, '-c', LAUNCH, str(clone), '--root', str(clone),
                           '--commit', commit, '--output', str(output), '--sizes', sizes, *extra],
                          capture_output=True, text=True, timeout=90)


def _manifest(output):
    return json.loads((output / ref.MANIFEST_NAME).read_text())


# ------------------------------------------------------------- containment
def test_budget_partition_sums_to_design_caps():
    c = runner.ceilings()
    assert c['total_cpu_bound'] <= runner.TOTAL_CPU == 30
    assert c['total_memory_bound'] <= runner.TOTAL_MEMORY == 512 * 1024 ** 2
    assert runner.TOTAL_WALL == 60


def test_seccomp_program_shape():
    raw, count = runner.seccomp_program('x86_64')
    assert len(raw) == 8 * count and count == 11
    raw, count = runner.seccomp_program('aarch64')
    assert count == 8
    with pytest.raises(OSError):
        runner.seccomp_program('riscv64')


PROBE = r'''
import os, resource, threading
try:
    pid = os.fork()
except PermissionError:
    print('fork-denied')
else:
    if pid == 0:
        os._exit(0)
    print('fork-allowed')
try:
    threading.Thread(target=lambda: 0).start(); print('thread-allowed')
except RuntimeError:
    print('thread-denied')
try:
    os.write(os.open('x', os.O_WRONLY | os.O_CREAT), b'1'); print('write-allowed')
except OSError:
    print('write-denied')
print(resource.getrlimit(resource.RLIMIT_CPU)[0], resource.getrlimit(resource.RLIMIT_AS)[0])
'''


def test_child_restrictor_denies_fork_threads_and_files(tmp_path):
    result = subprocess.run([sys.executable, '-I', '-c', PROBE], cwd=tmp_path, capture_output=True,
                            text=True, preexec_fn=runner.child_restrictor(3, 256 * 1024 ** 2), timeout=30)
    lines = result.stdout.split()
    assert result.returncode == 0, result.stderr
    assert lines[:3] == ['fork-denied', 'thread-denied', 'write-denied']
    assert (tmp_path / 'x').stat().st_size == 0


def test_child_restrictor_sets_limits(tmp_path):
    code = 'import resource; print(resource.getrlimit(resource.RLIMIT_CPU), resource.getrlimit(resource.RLIMIT_AS))'
    out = subprocess.check_output([sys.executable, '-I', '-c', code], cwd=tmp_path, text=True,
                                  preexec_fn=runner.child_restrictor(3, 256 * 1024 ** 2), timeout=30)
    assert out.strip() == f'(3, 3) ({256 * 1024 ** 2}, {256 * 1024 ** 2})'


def _controller(tmp_path, seconds=60.0):
    return runner.Controller(tmp_path, time.monotonic() + seconds)


def test_worker_wall_limit_kills(tmp_path):
    started = time.monotonic()
    raw, code, reason = _controller(tmp_path, runner.FINALIZATION_WALL + 1.0).worker(
        [sys.executable, '-c', 'import time\nwhile True: time.sleep(0.01)'])
    assert reason == 'worker wall limit' and code == -signal.SIGKILL
    assert time.monotonic() - started < 5


def test_worker_cpu_limit_kills(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'WORKER_CPU', 1)
    raw, code, reason = _controller(tmp_path).worker([sys.executable, '-c', 'while True: pass'])
    assert reason is None and code in (-signal.SIGXCPU, -signal.SIGKILL)


def test_worker_memory_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'CHILD_AS', 128 * 1024 ** 2)
    raw, code, reason = _controller(tmp_path).worker(
        [sys.executable, '-c', 'x = bytearray(512 * 1024 ** 2)'])
    assert code == 1 and reason is None


def test_worker_output_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'WORKER_STDOUT_BYTES', 1000)
    raw, code, reason = _controller(tmp_path).worker(
        [sys.executable, '-c', 'import sys; sys.stdout.write("x" * 100000)'])
    assert reason == 'worker output limit' and len(raw) <= 1000


def test_git_helper_budget_is_bounded(tmp_path):
    subprocess.check_call(['git', 'init', '-q', str(tmp_path)])
    controller = _controller(tmp_path)
    for _ in range(runner.GIT_CALLS):
        controller.git('rev-parse', '--show-toplevel')
    with pytest.raises(RuntimeError, match='budget exhausted'):
        controller.git('rev-parse', '--show-toplevel')


# ----------------------------------------------------------- end to end
def test_fixture_reference_complete(pinned, tmp_path):
    clone, commit = pinned
    output = tmp_path / 'out'
    result = _launch(clone, commit, output, '2,3,4,5')
    assert result.returncode == 0, (output / ref.MANIFEST_NAME).read_text()
    manifest = _manifest(output)
    assert manifest['outcome'] == 'REFERENCE_COMPLETE' and manifest['stage'] == 'finished'
    assert manifest['strict_aggregate_containment'] is True and manifest['frozen'] is False
    assert manifest['authorized'] is False and manifest['engineering_fixture'] is True
    assert manifest['commit'] == commit and manifest['git_calls_used'] == runner.GIT_CALLS
    assert sorted(os.listdir(output)) == sorted([ref.LOG_NAME, ref.MANIFEST_NAME, ref.REFERENCE_NAME])
    assert manifest['worker']['stdout_sha256'] == manifest['raw_sha256']


def test_target_and_oversized_sizes_refused(pinned, tmp_path):
    clone, commit = pinned
    for sizes in (','.join(map(str, range(2, 33))), '2,3,11', '1,2'):
        result = _launch(clone, commit, tmp_path / sizes.replace(',', '_'), sizes)
        assert result.returncode == 4 and 'REFUSED' in result.stdout
        assert not (tmp_path / sizes.replace(',', '_')).exists()


def test_wrong_commit_and_dirty_checkout_incomplete(pinned, tmp_path):
    clone, commit = pinned
    result = _launch(clone, '0' * 40, tmp_path / 'a', '2,3')
    assert result.returncode == 2 and _manifest(tmp_path / 'a')['stage'] == 'provenance'
    extra = clone / 'src/emergence_lab/zz_untracked.py'
    extra.write_text('')
    try:
        result = _launch(clone, commit, tmp_path / 'b', '2,3')
    finally:
        extra.unlink()
    manifest = _manifest(tmp_path / 'b')
    assert result.returncode == 2 and manifest['outcome'] == 'INCOMPLETE'
    assert not (tmp_path / 'b' / ref.REFERENCE_NAME).exists()


def test_killed_controller_leaves_incomplete_and_no_orphan(pinned, tmp_path):
    clone, commit = pinned
    output = tmp_path / 'out'
    process = subprocess.Popen([sys.executable, '-I', '-B', *PYC, '-c', LAUNCH, str(clone), '--root', str(clone),
                                '--commit', commit, '--output', str(output), '--sizes',
                                ','.join(map(str, range(2, 11)))], stdout=subprocess.DEVNULL)
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            if _manifest(output).get('stage') == 'worker':
                break
        except (OSError, ValueError):
            pass
        time.sleep(0.005)
    else:
        process.kill(); pytest.fail('worker stage not reached')
    children = []
    for _ in range(400):
        children = subprocess.run(['pgrep', '-P', str(process.pid)], capture_output=True,
                                  text=True).stdout.split()
        if children:
            break
        time.sleep(0.005)
    assert children, 'worker child not observed'
    process.send_signal(signal.SIGKILL)
    process.wait()
    time.sleep(0.5)
    for pid in children:
        assert not Path(f'/proc/{pid}').exists() or 'Z' in Path(f'/proc/{pid}/stat').read_text().split()[2]
    manifest = _manifest(output)
    assert manifest['outcome'] == 'INCOMPLETE' and manifest['stage'] in ('worker', 'setup')
    assert not (output / ref.REFERENCE_NAME).exists()


# ------------------------------------------------------- classification
@pytest.fixture(scope='module')
def payload():
    return ref.generate_reference((2, 3, 4))


def test_classify_accepts_consistent_payload(payload):
    assert runner.classify(copy.deepcopy(payload), (2, 3, 4)) == ('REFERENCE_COMPLETE', None)


@pytest.mark.parametrize('mutate', [
    lambda p: p['weights'][1]['counts'].__setitem__(0, 2),
    lambda p: p['coverage'][2]['fraction_index'].reverse(),
    lambda p: p['fractions'].pop(),
    lambda p: p['fractions'][0].__setitem__('passed', False),
    lambda p: p.__setitem__('failures', ['x']),
    lambda p: p['summaries'][0].__setitem__('mean_r', [1, 3]),
    lambda p: p['config'].__setitem__('frozen', True),
    lambda p: p.__setitem__('cs0_acceptance', True),
    lambda p: p.__setitem__('outcome', 'NUMERICAL_CHECK_FAILED'),
    lambda p: p.__setitem__('monotone', False),
    lambda p: p['spot_checks'].pop(),
    lambda p: p.__setitem__('weights', None),
    lambda p: p['fractions'][0].__setitem__('sign_check', False),
    lambda p: p['fractions'][1].__setitem__('converged', False),
    lambda p: p['fractions'][1].__setitem__('error', 'x'),
    lambda p: p['fractions'][0].__setitem__('independent_check', False),
    lambda p: p['spot_checks'][0].__setitem__('newton', None),
])
def test_classify_rejects_tampering(payload, mutate):
    tampered = copy.deepcopy(payload)
    mutate(tampered)
    assert runner.classify(tampered, (2, 3, 4))[0] == 'INCOMPLETE'


def test_classify_wrong_sizes(payload):
    assert runner.classify(copy.deepcopy(payload), (2, 3))[0] == 'INCOMPLETE'


def test_classify_nonfinite_is_numerical_check_failed():
    failed = ref.generate_reference((2, 3, 4), _binary64=lambda r: math.nan)
    assert failed['outcome'] == 'NUMERICAL_CHECK_FAILED'
    assert runner.classify(failed, (2, 3, 4)) == ('NUMERICAL_CHECK_FAILED', None)
    failed['failures'] = []
    assert runner.classify(failed, (2, 3, 4))[0] == 'INCOMPLETE'


def test_planted_bytecode_is_provenance_failure(pinned, tmp_path):
    clone, commit = pinned
    cache = clone / 'src/emergence_lab/__pycache__'
    cache.mkdir()
    (cache / 'd2_e0_runner.cpython-0.pyc').write_bytes(b'planted')
    try:
        result = _launch(clone, commit, tmp_path / 'out', '2,3')
    finally:
        (cache / 'd2_e0_runner.cpython-0.pyc').unlink(); cache.rmdir()
    manifest = _manifest(tmp_path / 'out')
    assert result.returncode == 2 and 'bytecode cache' in manifest['reason']
    assert not (tmp_path / 'out' / ref.REFERENCE_NAME).exists()


def test_run_refuses_target_sizes_directly(tmp_path):
    with pytest.raises(ValueError, match='not frozen'):
        runner.run(tmp_path, '0' * 40, tmp_path / 'o', runner.TARGET_SIZES, None, time.monotonic() + 60)
    assert not (tmp_path / 'o').exists()


def test_manifest_records_capability(pinned, tmp_path):
    clone, commit = pinned
    _launch(clone, commit, tmp_path / 'out', '2')
    assert _manifest(tmp_path / 'out')['cap_sys_resource'] in (True, False)


@pytest.mark.parametrize('capability', [True, None])
def test_unverified_or_elevated_capability_refuses_before_worker(pinned, tmp_path, capability):
    clone, commit = pinned
    output = tmp_path / 'out'
    code = ("import sys; sys.path.insert(0, sys.argv[1] + '/src'); "
            "import emergence_lab.d2_e0_runner as r; "
            f"r._has_cap_sys_resource = lambda: {capability!r}; "
            "raise SystemExit(r.main(sys.argv[2:]))")
    result = subprocess.run([sys.executable, '-I', '-B', *PYC, '-c', code, str(clone),
                             '--root', str(clone), '--commit', commit, '--output', str(output),
                             '--sizes', '2,3'], capture_output=True, text=True, timeout=30)
    manifest = _manifest(output)
    assert result.returncode == 2 and manifest['outcome'] == 'INCOMPLETE'
    assert 'CAP_SYS_RESOURCE' in manifest['reason'] and 'worker' not in manifest
    assert not (output / ref.REFERENCE_NAME).exists()


def test_kill_after_reference_replace_leaves_authoritative_incomplete(pinned, tmp_path):
    """Kill in the documented final-write window, after reference fsync/replace."""
    clone, commit = pinned
    output = tmp_path / 'out'
    code = r"""
import os, signal, sys
sys.path.insert(0, sys.argv[1] + '/src')
from emergence_lab import d2_e0_reference as ref
from emergence_lab import d2_e0_runner as runner
original = ref.FixedWriter.replace
def kill_after_reference(self, name, data):
    original(self, name, data)
    if name == ref.REFERENCE_NAME:
        os.kill(os.getpid(), signal.SIGKILL)
ref.FixedWriter.replace = kill_after_reference
raise SystemExit(runner.main(sys.argv[2:]))
"""
    result = subprocess.run([sys.executable, '-I', '-B', *PYC, '-c', code, str(clone),
                             '--root', str(clone), '--commit', commit, '--output', str(output),
                             '--sizes', '2,3,4'], capture_output=True, text=True, timeout=30)
    assert result.returncode == -signal.SIGKILL
    assert (output / ref.REFERENCE_NAME).exists()
    manifest = _manifest(output)
    assert manifest['outcome'] == 'INCOMPLETE' and manifest['stage'] != 'finished'
    assert sum(p.stat().st_size for p in output.iterdir()) <= ref.SLOT_SUM


@pytest.fixture
def authorization(tmp_path):
    from datetime import datetime, timedelta, timezone
    from importlib.metadata import version
    import hashlib
    root, output = tmp_path / 'repo', tmp_path / 'out'
    (root / 'docs').mkdir(parents=True)
    (root / 'src/emergence_lab').mkdir(parents=True)
    (root / runner.PROTOCOL).write_text('fixture protocol')
    names = ('d2_e0_runner.py', 'd2_e0_reference.py', 'causal_set_mm.py')
    for name in names:
        (root / 'src/emergence_lab' / name).write_text('# fixture')
    auth = dict(schema=1, diagnostic='D2-E0', id='fixture-only', sizes=list(runner.TARGET_SIZES),
                max_invocations=1, not_after=(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),
                host_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                root=str(root), output=str(output), interpreter=sys.executable,
                python=platform.python_version(),
                protocol_sha256=hashlib.sha256((root / runner.PROTOCOL).read_bytes()).hexdigest(),
                config_sha256=hashlib.sha256(ref._json(ref.protocol_config(runner.TARGET_SIZES))).hexdigest(),
                source_sha256={name: hashlib.sha256((root/'src/emergence_lab'/name).read_bytes()).hexdigest()
                               for name in names},
                dependencies={name: version(name) for name in ('mpmath', 'scipy', 'numpy')})
    return root, output, auth


def test_target_authorization_validates_only_metadata_no_target_evaluation(authorization):
    root, output, auth = authorization
    (root / runner.AUTHORIZATION).write_text(json.dumps(auth))
    checked = runner.target_authorization(root, output, 'fixture-only')
    assert checked['id'] == 'fixture-only' and len(checked['sha256']) == 64
    assert not output.exists()


@pytest.mark.parametrize('field,value', [
    ('schema', 2), ('id', 'other'), ('diagnostic', 'other'), ('sizes', [2, 3]),
    ('max_invocations', 2), ('not_after', '2000-01-01T00:00:00Z'),
    ('host_boot_id', 'another-host'), ('output', '/other'), ('root', '/other'),
    ('interpreter', '/other'), ('python', '0'), ('protocol_sha256', '0'*64),
    ('config_sha256', '0'*64), ('source_sha256', {}), ('dependencies', {}),
])
def test_target_authorization_rejects_changed_pins(authorization, field, value):
    root, output, auth = authorization
    auth[field] = value
    (root / runner.AUTHORIZATION).write_text(json.dumps(auth))
    with pytest.raises(ValueError):
        runner.target_authorization(root, output, 'fixture-only')
    assert not output.exists()


def test_target_with_id_but_no_committed_authorization_never_starts_worker(pinned, tmp_path):
    clone, commit = pinned
    output = tmp_path / 'out'
    result = _launch(clone, commit, output, ','.join(map(str, runner.TARGET_SIZES)),
                     ['--authorization-id', 'missing'])
    manifest = _manifest(output)
    assert result.returncode == 2 and manifest['outcome'] == 'INCOMPLETE'
    assert 'worker' not in manifest and not (output / ref.REFERENCE_NAME).exists()


def test_existing_output_cannot_be_reused(pinned, tmp_path):
    clone, commit = pinned
    output = tmp_path / 'out'
    first = _launch(clone, commit, output, '2,3')
    before = {p.name: p.read_bytes() for p in output.iterdir()}
    second = _launch(clone, commit, output, '2,3')
    assert first.returncode == 0 and second.returncode != 0
    assert {p.name: p.read_bytes() for p in output.iterdir()} == before
