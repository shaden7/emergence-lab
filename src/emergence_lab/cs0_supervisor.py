"""CS0 containment building block; no study execution or seed authorization.

Linux only. The trusted worker must not fork or write files: its sole artifact
channel is stdout. RLIMIT_AS conservatively bounds virtual memory (and hence
RSS), RLIMIT_CPU bounds worker CPU, and the parent bounds captured output.
A Linux parent-death signal kills the direct worker if the supervisor dies.
A future study runner must account for its own CPU and artifact metadata too.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import selectors
import signal
import subprocess
import time


def _parent_death_guard(expected_parent: int, prctl):
    """Kill this trusted Linux worker if its launching supervisor disappears.

    The second check closes the race where the parent dies before prctl arms
    the signal. The worker must not fork, change credentials or clear the guard.
    """
    if prctl(1, signal.SIGKILL, 0, 0, 0) != 0:  # PR_SET_PDEATHSIG
        raise OSError(ctypes.get_errno(), 'PR_SET_PDEATHSIG failed')
    if os.getppid() != expected_parent:
        os.kill(os.getpid(), signal.SIGKILL)


@dataclass(frozen=True)
class Limits:
    cpu_seconds: int = 600
    wall_seconds: float = 900
    memory_bytes: int = 1024**3
    output_bytes: int = 50_000_000

    def validate(self):
        for name in ('cpu_seconds', 'memory_bytes', 'output_bytes'):
            value = getattr(self, name)
            if type(value) is not int or value <= 0:
                raise ValueError(f'{name} must be a positive integer')
        if not math.isfinite(self.wall_seconds) or self.wall_seconds <= 0:
            raise ValueError('wall_seconds must be finite and positive')


def checkpoint(path: Path, record: dict):
    """Atomic replacement with file and directory fsync; initial record survives kills."""
    temporary = path.with_suffix('.tmp')
    with temporary.open('w') as stream:
        json.dump(record, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def verify_checkout(root: Path, commit: str):
    """Reject dirty/untracked sources, wrong revisions and abbreviated pins."""
    if len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('an exact lowercase 40-character commit is required')
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root, text=True, timeout=10).strip()
    if git('rev-parse', 'HEAD') != commit:
        raise ValueError('checkout differs from pinned commit')
    if git('status', '--porcelain', '--untracked-files=all'):
        raise ValueError('checkout is dirty or has untracked files')


def supervise(command: list[str], output: Path, root: Path, commit: str,
              limits: Limits = Limits()) -> dict:
    """Capture a trusted, single-process worker; COMPLETE means engineering only.

    Output must be outside the checkout. This is deliberately not a PASS/FAIL
    scientific gate, nor a full CS0 runner. The caller must inspect the payload.
    The caller must be single-threaded (preexec_fn); the trusted worker must
    preserve its parent-death signal and must not fork or change credentials.
    """
    output = output.resolve()
    root = root.resolve()
    if output == root or root in output.parents:
        raise ValueError('output must be outside the checkout')
    output.mkdir(parents=True, exist_ok=False)
    manifest = output / 'manifest.json'
    record = dict(outcome='INCOMPLETE', stage='setup', commit=commit,
                  limits=asdict(limits), study_authorized=False)
    checkpoint(manifest, record)
    process = None
    usage = None
    start = time.monotonic()
    try:
        limits.validate()
        verify_checkout(root, commit)
        env = {**os.environ, **{key: '1' for key in (
            'OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
            'NUMEXPR_NUM_THREADS')}}
        env['PYTHONPATH'] = str(root / 'src')
        env.pop('PYTHONHOME', None)
        # Resolve libc before fork. preexec_fn requires a single-threaded caller.
        prctl = ctypes.CDLL(None, use_errno=True).prctl
        parent_pid = os.getpid()
        def restrict():
            _parent_death_guard(parent_pid, prctl)
            resource.setrlimit(resource.RLIMIT_CPU, (limits.cpu_seconds, limits.cpu_seconds))
            resource.setrlimit(resource.RLIMIT_AS, (limits.memory_bytes, limits.memory_bytes))
            # Worker file output is prohibited; stdout/stderr pipes remain usable.
            resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        process = subprocess.Popen(command, cwd=root, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, start_new_session=True,
                                   preexec_fn=restrict)
        record.update(stage='worker', pid=process.pid)
        checkpoint(manifest, record)
        count = 0
        digest = hashlib.sha256()
        reason = None
        with selectors.DefaultSelector() as selector, (output / 'worker.bin').open('wb') as stream:
            selector.register(process.stdout, selectors.EVENT_READ)
            while True:
                if usage is None:
                    pid, status, observed = os.wait4(process.pid, os.WNOHANG)
                    if pid:
                        process.returncode = os.waitstatus_to_exitcode(status)
                        usage = observed
                if time.monotonic() - start >= limits.wall_seconds:
                    reason = 'wall limit'
                    break
                events = selector.select(timeout=0.02)
                if events:
                    data = os.read(process.stdout.fileno(), 65536)
                    if not data:
                        selector.unregister(process.stdout)
                        if usage is not None:
                            break
                    else:
                        remaining = limits.output_bytes - count
                        retained = data[:remaining]
                        stream.write(retained)
                        digest.update(retained)
                        count += len(retained)
                        if len(data) > remaining:
                            reason = 'output limit'
                            break
                elif usage is not None:
                    if not selector.get_map():
                        break
                    # Pipe can remain open only through a prohibited descendant.
                    reason = 'worker exited without closing output'
                    break
            stream.flush()
            os.fsync(stream.fileno())
        record.update(output_bytes=count, output_sha256=digest.hexdigest())
        if reason:
            raise RuntimeError(reason)
        if process.returncode != 0:
            raise RuntimeError(f'worker exit {process.returncode}')
        verify_checkout(root, commit)
        record.update(outcome='COMPLETE', stage='finished')
    except Exception as error:
        record.update(outcome='INCOMPLETE', error=f'{type(error).__name__}: {error}')
    finally:
        if process is not None:
            # Also kill any unexpected surviving member of the worker session.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            if usage is None:
                _, status, usage = os.wait4(process.pid, 0)
                process.returncode = os.waitstatus_to_exitcode(status)
            process.stdout.close()
            record['exit_code'] = process.returncode
            record['worker_cpu_seconds'] = usage.ru_utime + usage.ru_stime
            record['worker_peak_rss_kib'] = usage.ru_maxrss
        record['wall_seconds'] = time.monotonic() - start
        checkpoint(manifest, record)
    return record
