"""Supervised D2-E0 runner with partitioned kernel ceilings (NOT frozen, NOT authorized).

Design: docs/CS0_D2_ENDPOINT_CONTROL_PROPOSAL.md ("Implementation step 2").
Importing this module evaluates nothing. ``main`` refuses the target
N=2..32 unconditionally: no freeze or once-only authorization exists. Only
small engineering fixtures (N<=FIXTURE_MAX_N) can be evaluated.

Containment model ("partitioned ceilings", Linux x86_64/aarch64 only). The
controller is the root of the accountable process tree. Strict upper bounds
are the *sums of kernel-enforced per-process hard limits* of processes that
can never overlap, not observations:

* controller: soft RLIMIT_CPU/RLIMIT_AS on itself (set first in ``main``) and a
  real-time itimer whose default SIGALRM action terminates it at the total
  wall deadline measured from process start;
* children (at most ``GIT_CALLS`` git helpers plus one worker), started
  strictly sequentially, each with its own RLIMIT_CPU/RLIMIT_AS, no file
  output (RLIMIT_FSIZE=0), a parent-death SIGKILL and a seccomp filter that
  makes fork/vfork/clone/clone3 fail with EPERM, so no child can create a
  descendant or a thread. The worker verifies the filter by a fork probe
  before computing and refuses if fork succeeds.

Hence total CPU <= CONTROLLER_CPU + GIT_CALLS*GIT_CPU + WORKER_CPU and
simultaneous virtual memory (thus RSS) <= CONTROLLER_AS + CHILD_AS, up to the
kernel's per-process tick granularity in enforcing RLIMIT_CPU. Not covered:
the launching shell, kernel/page-cache memory, filesystem failures, a
concurrent adversary modifying the checkout, or an untrusted interpreter or
mpmath installation. A SIGALRM/RLIMIT kill of the controller leaves the last
INCOMPLETE checkpoint manifest, never a complete-looking reference.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import selectors
import signal
import struct
import subprocess
import sys
import time

PROTOCOL = 'docs/CS0_D2_ENDPOINT_CONTROL_PROPOSAL.md'
TARGET_SIZES = tuple(range(2, 33))
FIXTURE_MAX_N = 10

MIB = 1024 ** 2
TOTAL_CPU, TOTAL_WALL, TOTAL_MEMORY = 30, 60.0, 512 * MIB
CONTROLLER_CPU, CONTROLLER_AS = 4, 128 * MIB
GIT_CALLS, GIT_CPU, GIT_WALL = 6, 1, 10.0
WORKER_CPU, CHILD_AS = 20, 384 * MIB
WORKER_STDOUT_BYTES = 8_000_000  # in controller memory only; never written raw
FINALIZATION_WALL = 5.0
assert CONTROLLER_CPU + GIT_CALLS * GIT_CPU + WORKER_CPU <= TOTAL_CPU
assert CONTROLLER_AS + CHILD_AS <= TOTAL_MEMORY

GIT_CONFIG = ('--no-optional-locks', '-c', 'core.preloadIndex=false', '-c', 'index.threads=1',
              '-c', 'core.fsmonitor=false', '-c', 'core.untrackedCache=false')

# ------------------------------------------------------------ seccomp filter
_ARCH = {'x86_64': (0xC000003E, (56, 57, 58, 435)),   # clone fork vfork clone3
         'aarch64': (0xC00000B7, (220, 435))}           # clone clone3
_RET_ALLOW, _RET_EPERM, _RET_KILL = 0x7FFF0000, 0x00050001, 0x80000000


def seccomp_program(machine: str | None = None) -> tuple[bytes, int]:
    """Classic BPF: wrong arch -> kill; x32 or process/thread creation -> EPERM."""
    machine = machine or platform.machine()
    if machine not in _ARCH:
        raise OSError(f'unsupported architecture for no-fork filter: {machine}')
    arch, numbers = _ARCH[machine]
    tests = ([('jge', 0x40000000)] if machine == 'x86_64' else []) + [('jeq', n) for n in numbers]
    allow = 3 + len(tests)
    eperm, kill = allow + 1, allow + 2
    code = [(0x20, 0, 0, 4), (0x15, 0, kill - 2, arch), (0x20, 0, 0, 0)]
    for position, (op, value) in enumerate(tests, start=3):
        code.append((0x35 if op == 'jge' else 0x15, eperm - position - 1, 0, value))
    code += [(0x06, 0, 0, _RET_ALLOW), (0x06, 0, 0, _RET_EPERM), (0x06, 0, 0, _RET_KILL)]
    return b''.join(struct.pack('HBBI', *row) for row in code), len(code)


class _Fprog(ctypes.Structure):
    _fields_ = [('len', ctypes.c_ushort), ('filter', ctypes.c_void_p)]


def child_restrictor(cpu_seconds: int, memory_bytes: int):
    """Build (before fork) the preexec function applied to every child."""
    libc = ctypes.CDLL(None, use_errno=True)
    raw, count = seccomp_program()
    buffer = ctypes.create_string_buffer(raw, len(raw))
    program = _Fprog(count, ctypes.cast(buffer, ctypes.c_void_p))
    parent = os.getpid()

    def restrict():
        _keep = buffer  # noqa: F841 - keep the filter alive in the child
        if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:  # PR_SET_PDEATHSIG
            raise OSError(ctypes.get_errno(), 'PR_SET_PDEATHSIG failed')
        if os.getppid() != parent:
            os.kill(os.getpid(), signal.SIGKILL)
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        if libc.prctl(38, 1, 0, 0, 0) != 0:  # PR_SET_NO_NEW_PRIVS
            raise OSError(ctypes.get_errno(), 'PR_SET_NO_NEW_PRIVS failed')
        if libc.prctl(22, 2, ctypes.byref(program), 0, 0) != 0:  # SECCOMP_MODE_FILTER
            raise OSError(ctypes.get_errno(), 'seccomp filter refused')
    return restrict


# --------------------------------------------------------- controller limits
def _process_age() -> float:
    """Seconds since this process started (includes interpreter startup)."""
    fields = Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()
    start = int(fields[19]) / os.sysconf('SC_CLK_TCK')
    return time.clock_gettime(time.CLOCK_BOOTTIME) - start


def limit_controller():
    """Apply the controller's own hard ceilings; irreversible for this process."""
    # Soft limits: the kernel enforces the soft value (SIGXCPU, default action
    # terminate; ENOMEM beyond AS). Hard limits stay higher only so that a
    # non-root child may be given its own larger allotment; the trusted
    # controller never raises its soft limits.
    for kind, value in ((resource.RLIMIT_CPU, CONTROLLER_CPU), (resource.RLIMIT_AS, CONTROLLER_AS)):
        soft, hard = resource.getrlimit(kind)
        needed = WORKER_CPU if kind == resource.RLIMIT_CPU else CHILD_AS
        if hard != resource.RLIM_INFINITY and hard < needed:
            raise RuntimeError('inherited hard limit below a child allotment')
        resource.setrlimit(kind, (value, hard))
    signal.signal(signal.SIGXCPU, signal.SIG_DFL)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    remaining = TOTAL_WALL - _process_age()
    if remaining <= FINALIZATION_WALL:
        raise RuntimeError('wall budget exhausted before controller start')
    signal.signal(signal.SIGALRM, signal.SIG_DFL)
    signal.setitimer(signal.ITIMER_REAL, remaining)
    return time.monotonic() + remaining


class Controller:
    """Sequential child launcher that counts against the partitioned budget."""

    def __init__(self, root: Path, deadline: float):
        self.root, self.deadline, self.git_calls = root, deadline, 0

    def git(self, *args) -> bytes:
        if self.git_calls >= GIT_CALLS:
            raise RuntimeError('git helper budget exhausted')
        self.git_calls += 1
        timeout = min(GIT_WALL, self.deadline - time.monotonic() - FINALIZATION_WALL)
        if timeout <= 0:
            raise RuntimeError('wall budget exhausted before git helper')
        env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
               'GIT_CONFIG_NOSYSTEM': '1', 'HOME': '/nonexistent'}
        return subprocess.run(['git', *GIT_CONFIG, *args], cwd=self.root, env=env,
                              stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, timeout=timeout, check=True,
                              preexec_fn=child_restrictor(GIT_CPU, CHILD_AS)).stdout

    def worker(self, command: list[str]) -> tuple[bytes, int, str | None]:
        """Run the single worker; returns (stdout, exit code, failure reason)."""
        timeout = self.deadline - time.monotonic() - FINALIZATION_WALL
        if timeout <= 0:
            return b'', -1, 'wall budget exhausted before worker'
        env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LC_ALL': 'C',
               **{k: '1' for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')}}
        process = subprocess.Popen(command, cwd=self.root, env=env, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                   start_new_session=True,
                                   preexec_fn=child_restrictor(WORKER_CPU, CHILD_AS))
        chunks, size, reason, started = [], 0, None, time.monotonic()
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                while True:
                    if time.monotonic() - started >= timeout:
                        reason = 'worker wall limit'
                        break
                    if not selector.select(timeout=0.05):
                        continue
                    data = os.read(process.stdout.fileno(), 65536)
                    if not data:
                        break
                    size += len(data)
                    if size > WORKER_STDOUT_BYTES:
                        reason = 'worker output limit'
                        break
                    chunks.append(data)
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            process.stdout.close()
        return b''.join(chunks), process.returncode, reason


def verify_tree(controller: Controller, root: Path, commit: str) -> dict:
    """Pin checkout, tracked src/ bytes and protocol bytes with three git calls."""
    if type(commit) is not str or len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('an exact lowercase 40-character commit is required')
    head, top = controller.git('rev-parse', 'HEAD', '--show-toplevel').decode().split('\n')[:2]
    if head != commit or Path(top).resolve() != root:
        raise ValueError('checkout differs from pinned commit or root')
    if controller.git('status', '--porcelain', '--untracked-files=all'):
        raise ValueError('checkout is dirty or has untracked files')
    listing = controller.git('ls-tree', '-r', '-z', commit, '--', 'src', PROTOCOL)
    expected = {}
    for entry in listing.split(b'\0'):
        if entry:
            meta, name = entry.split(b'\t', 1)
            mode, kind, blob = meta.decode().split()
            if mode != '100644' or kind != 'blob':
                raise ValueError('unexpected tracked mode or type')
            expected[name.decode()] = blob
    if PROTOCOL not in expected or not any(n.startswith('src/') for n in expected):
        raise ValueError('pinned commit lacks protocol or sources')
    for path in (root / 'src').rglob('*'):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ValueError('symlink in source tree')
        if path.is_file() and relative not in expected:
            inert = (len(path.relative_to(root).parts) == 3
                     and path.parent.name == 'emergence_lab.egg-info')
            if not inert and not (path.suffix == '.pyc' and path.parent.name == '__pycache__'):
                raise ValueError(f'unexpected file in source tree: {relative}')
    for name, blob in expected.items():
        data = (root / name).read_bytes()
        if hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() != blob:
            raise ValueError(f'source bytes differ: {name}')
    return dict(tracked_files=len(expected),
                listing_sha256=hashlib.sha256(listing).hexdigest(),
                protocol_blob=expected[PROTOCOL])


# ------------------------------------------------------------------- worker
def worker_main(sizes: list[int]):
    """Child entry point: verify no-fork containment, compute, emit JSON."""
    try:
        pid = os.fork()
    except PermissionError:
        pid = None
    if pid == 0:
        os._exit(0)
    if pid is not None:
        os.waitpid(pid, 0)
        raise SystemExit(3)  # filter absent: refuse before any computation
    reference = __import__('emergence_lab.d2_e0_reference', fromlist=['generate_reference'])
    payload = reference.generate_reference(tuple(sizes))
    sys.stdout.buffer.write(reference._json(payload))
    sys.stdout.flush()


# ------------------------------------------------------------ classification
def classify(payload, sizes: tuple[int, ...]) -> tuple[str, str | None]:
    """Independent runner-side contract check; INCOMPLETE on any mismatch."""
    from emergence_lab import d2_e0_reference as ref
    if type(payload) is not dict or payload.get('schema') != 1 or payload.get('diagnostic') != 'D2-E0':
        return 'INCOMPLETE', 'payload schema'
    if payload.get('config') != ref.protocol_config(sizes):
        return 'INCOMPLETE', 'payload config differs from expected'
    if payload.get('cs0_acceptance') is not False or payload.get('stochastic') is not False:
        return 'INCOMPLETE', 'payload acceptance/stochastic flags'
    weights, coverage = payload.get('weights'), payload.get('coverage')
    fractions, summaries = payload.get('fractions'), payload.get('summaries')
    if any(type(x) is not list for x in (weights, coverage, fractions, summaries,
                                          payload.get('spot_checks'), payload.get('failures'))):
        return 'INCOMPLETE', 'payload containers'
    if len(weights) != len(sizes) or len(coverage) != len(sizes) or len(summaries) != len(sizes):
        return 'INCOMPLETE', 'per-N lengths'
    expected_distinct, supports = set(), []
    for n, w, c, s in zip(sizes, weights, coverage, summaries):
        exact = ref.endpoint_weights(n)  # recomputed exactly, not trusted
        if w != exact or type(c) is not dict or c.get('N') != n or type(s) is not dict or s.get('N') != n:
            return 'INCOMPLETE', f'N={n} weights or identity'
        values, checks = ref.exact_controls(exact)
        if (s.get('mean_r') != ref._rational(values['mean_r'])
                or s.get('variance_r') != ref._rational(values['variance_r'])
                or s.get('exact_checks') != checks or not all(checks.values())):
            return 'INCOMPLETE', f'N={n} exact controls'
        support = [ref.support_fraction(exact, k) for k in range(len(exact['counts']))]
        expected_distinct.update(support)
        index = c.get('fraction_index')
        if type(index) is not list or len(index) != len(support):
            return 'INCOMPLETE', f'N={n} coverage length'
        supports.append(support)
    distinct = sorted(expected_distinct)
    if len(fractions) != len(distinct):
        return 'INCOMPLETE', 'distinct fraction count'
    for r, row in zip(distinct, fractions):
        if type(row) is not dict or row.get('r') != ref._rational(r) or type(row.get('passed')) is not bool:
            return 'INCOMPLETE', 'fraction table'
    position = {r: i for i, r in enumerate(distinct)}
    for c, support in zip(coverage, supports):
        if c['fraction_index'] != [position[r] for r in support]:
            return 'INCOMPLETE', f'N={c["N"]} coverage indices'
    if any(type(s.get('checks_passed')) is not bool for s in summaries):
        return 'INCOMPLETE', 'summary flags'
    spot = payload['spot_checks']
    if len(spot) != 3 * len([n for n in ref.SPOT_CHECK_SIZES if n in sizes]) or any(
            type(x) is not dict or type(x.get('passed')) is not bool for x in spot):
        return 'INCOMPLETE', 'spot checks'
    all_passed = (all(f['passed'] for f in fractions) and all(s['checks_passed'] for s in summaries)
                  and all(x['passed'] for x in spot) and payload.get('monotone') is True)
    claimed, failures = payload.get('outcome'), payload['failures']
    if claimed == 'REFERENCE_COMPLETE' and all_passed and failures == []:
        return 'REFERENCE_COMPLETE', None
    if claimed == 'NUMERICAL_CHECK_FAILED' and not all_passed and failures:
        return 'NUMERICAL_CHECK_FAILED', None
    return 'INCOMPLETE', 'claimed outcome inconsistent with check flags'


# ---------------------------------------------------------------- runner
def _manifest(writer, record: dict):
    from emergence_lab import d2_e0_reference as ref
    writer.replace(ref.MANIFEST_NAME, ref._json(record))


def _costs() -> dict:
    own, children = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return dict(observed_controller_cpu_seconds=round(own.ru_utime + own.ru_stime, 6),
                observed_children_cpu_seconds=round(children.ru_utime + children.ru_stime, 6),
                observed_controller_maxrss_kib=own.ru_maxrss,
                observed_children_maxrss_kib=children.ru_maxrss,
                observed_wall_seconds_since_process_start=round(_process_age(), 6))


def ceilings() -> dict:
    return dict(model='partitioned kernel ceilings (sequential children, seccomp no-fork)',
                controller_cpu=CONTROLLER_CPU, git_calls=GIT_CALLS, git_cpu=GIT_CPU,
                worker_cpu=WORKER_CPU, controller_as=CONTROLLER_AS, child_as=CHILD_AS,
                total_cpu_bound=CONTROLLER_CPU + GIT_CALLS * GIT_CPU + WORKER_CPU,
                total_memory_bound=CONTROLLER_AS + CHILD_AS, wall_bound=TOTAL_WALL,
                worker_stdout_bytes=WORKER_STDOUT_BYTES)


def run(root: Path, commit: str, output: Path, sizes: tuple[int, ...],
        dependency_path: Path | None, deadline: float) -> dict:
    """Assumes ``limit_controller`` already ran in this process."""
    from emergence_lab import d2_e0_reference as ref
    root, output = Path(root).resolve(), Path(output).resolve()
    if output == root or root in output.parents:
        raise ValueError('output must be outside checkout')
    writer = ref.FixedWriter(output)
    base = dict(schema=1, diagnostic='D2-E0', commit=str(commit)[:64], sizes=list(sizes),
                engineering_fixture=tuple(sizes) != TARGET_SIZES, frozen=False,
                authorized=False, strict_aggregate_containment=True, ceilings=ceilings(),
                cs0_acceptance=False, stochastic=False,
                versions=dict(python=platform.python_version()))
    record = dict(base, outcome='INCOMPLETE', stage='setup')
    _manifest(writer, record)
    stage = 'provenance'
    try:
        controller = Controller(root, deadline)
        for module in (sys.modules['emergence_lab'], ref, sys.modules[__name__]):
            name = Path(module.__file__).resolve()
            if root / 'src' not in name.parents:
                raise ValueError(f'loaded module outside checkout: {module.__name__}')
        pins = verify_tree(controller, root, commit)
        config = ref.protocol_config(sizes)
        base.update(provenance=pins, config_sha256=hashlib.sha256(ref._json(config)).hexdigest())
        record = dict(base, outcome='INCOMPLETE', stage='worker')
        _manifest(writer, record)
        stage = 'worker'
        paths = [str(root / 'src')] + ([str(Path(dependency_path).resolve(strict=True))]
                                       if dependency_path is not None else [])
        bootstrap = (f'import sys; sys.path[:0]={paths!r}; '
                     f'import emergence_lab.d2_e0_runner as r; r.worker_main({list(sizes)!r})')
        raw, code, reason = controller.worker([sys.executable, '-I', '-B', '-c', bootstrap])
        base['worker'] = dict(exit_code=code, stdout_bytes=len(raw), reason=reason,
                              stdout_sha256=hashlib.sha256(raw).hexdigest())
        if reason or code != 0:
            raise RuntimeError(f'worker failed: exit={code} reason={reason}')
        stage = 'classify'
        payload = json.loads(raw)
        outcome, why = classify(payload, sizes)
        if outcome == 'INCOMPLETE':
            raise RuntimeError(f'payload classification: {why}')
        stage = 'provenance-after'
        if verify_tree(controller, root, commit) != pins:
            raise RuntimeError('provenance changed during execution')
        base['versions'] = dict(payload.get('versions') or {})
        stage = 'write'
        base.update(_costs(), git_calls_used=controller.git_calls)
        result = ref.write_reference(output, payload, base, writer=writer)
        return result
    except Exception as error:
        reason = f'{type(error).__name__}: {error}'[:1024]
        record = dict(base, outcome='INCOMPLETE', stage=stage, reason=reason, **_costs())
        try:
            for name in (ref.REFERENCE_NAME, ref.REFERENCE_NAME + '.tmp'):
                if (output / name).exists():
                    (output / name).unlink()
            _manifest(writer, record)
        except Exception as nested:
            record['manifest_persisted'] = False
            record['nested'] = f'{type(nested).__name__}: {nested}'[:256]
        return record


EXIT = {'REFERENCE_COMPLETE': 0, 'NUMERICAL_CHECK_FAILED': 1, 'INCOMPLETE': 2}


def main(argv=None):
    deadline = limit_controller()  # before argument parsing or any project import
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--sizes', required=True, help='comma-separated fixture sizes')
    parser.add_argument('--dependency-path', type=Path)
    args = parser.parse_args(argv)
    sizes = tuple(int(x) for x in args.sizes.split(','))
    if sizes == TARGET_SIZES or max(sizes) > FIXTURE_MAX_N or min(sizes) < 2:
        print(json.dumps(dict(outcome='REFUSED', reason='target or oversized sizes: '
                              'protocol not frozen and no once-only authorization')))
        return 4
    result = run(args.root, args.commit, args.output, sizes, args.dependency_path, deadline)
    durability = result.get('durability_unverified')
    print(json.dumps(dict(outcome=result.get('outcome'), diagnostic='D2-E0',
                          durability_unverified=durability, cs0_acceptance=False)))
    if durability:
        return 3
    return EXIT.get(result.get('outcome'), 2)


if __name__ == '__main__':
    raise SystemExit(main())
