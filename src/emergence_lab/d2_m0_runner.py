"""Supervised deterministic D2-M0 reference; never a CS0 acceptance decision.

Child limits are enforced. Aggregate costs are conservatively observed and
checked, not kernel-enforced for the controller and all of its subprocesses.
Importing this module does not import scientific dependencies or evaluate M0.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

PROTOCOL = 'docs/CS0_D2_M0_PROTOCOL.md'
TOTAL_BYTES, MANIFEST_BYTES = 1_000_000, 16_384
RESERVE = 3 * MANIFEST_BYTES  # Outer old/new plus two <=8KiB worker records.
FINALIZATION_SECONDS = 1.0


def _commit_value(value):
    return value[:128] if type(value) is str else '<invalid commit>'


def _json(value):
    return (json.dumps(value, sort_keys=True, allow_nan=False) + '\n').encode()


def _atomic(path, data):
    temporary = path.with_suffix('.tmp')
    path.parent.mkdir(parents=True, exist_ok=True)
    with temporary.open('wb') as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)
    fd = os.open(path.parent, os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)


def _save_manifest(path, record):
    try:
        data = _json(record)
    except (TypeError, ValueError):
        data = b'x' * (MANIFEST_BYTES + 1)
    if len(data) > MANIFEST_BYTES:
        record = dict(schema=1, diagnostic='D2-M0', outcome='INCOMPLETE',
                      commit=_commit_value(record.get('commit', ''))[:40], cs0_acceptance=False,
                      stochastic=False, error='manifest exceeds reserved slot')
        data = _json(record)
    _atomic(path, data)
    return record


def _usage():
    own, child = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + child.ru_utime + child.ru_stime, own.ru_maxrss + child.ru_maxrss


def _check_cost(started):
    cpu, rss = _usage()
    if cpu + FINALIZATION_SECONDS > 30 or time.monotonic() - started + FINALIZATION_SECONDS > 60 or rss > 512 * 1024:
        raise ValueError('observed aggregate budget exceeded')


def classify_payload(payload, config, worker):
    """Resource/provenance failure takes precedence over a negative calculation."""
    if (type(payload) is not dict or type(payload.get('schema')) is not int or payload.get('schema') != 1
            or payload.get('diagnostic') != 'D2-M0' or payload.get('config') != config
            or payload.get('cs0_acceptance') is not False or payload.get('stochastic') is not False):
        return 'INCOMPLETE'
    cells = payload.get('cells')
    if (type(cells) is not list or len(cells) != 31
            or any(type(c) is not dict or type(c.get('N')) is not int
                   or c['N'] != n or type(c.get('checks_passed')) is not bool
                   for n, c in zip(range(2, 33), cells))):
        return 'INCOMPLETE'
    for name in ('exact_weights', 'exact_controls'):
        items = payload.get(name)
        if type(items) is not list or len(items) != 31:
            return 'INCOMPLETE'
        if any(item is not None and (type(item) is not dict or item.get('N') != n)
               for n, item in zip(range(2, 33), items)):
            return 'INCOMPLETE'
    for name in ('numeric_checks', 'probe_checks'):
        if type(payload.get(name)) is not list or any(
                type(c) is not dict or type(c.get('passed')) is not bool for c in payload[name]):
            return 'INCOMPLETE'
    if type(payload.get('versions')) is not dict or any(
            type(payload['versions'].get(k)) is not str for k in ('python', 'numpy', 'scipy', 'mpmath')):
        return 'INCOMPLETE'
    claimed = payload.get('outcome')
    checks_passed = all(c['checks_passed'] for c in cells) and all(
        c['passed'] for name in ('numeric_checks', 'probe_checks') for c in payload[name])
    if claimed == 'REFERENCE_COMPLETE':
        if len(payload['numeric_checks']) != 66 or len(payload['probe_checks']) != 6:
            return 'INCOMPLETE'
        for n, weights, controls in zip(range(2, 33), payload['exact_weights'], payload['exact_controls']):
            if (type(weights) is not dict or type(controls) is not dict
                    or type(controls.get('checks')) is not dict or not controls['checks']
                    or any(v is not True for v in controls['checks'].values())):
                return 'INCOMPLETE'
            counts = weights.get('counts')
            if (type(counts) is not list or len(counts) != math.comb(n, 2) + 1
                    or any(type(c) is not int or c <= 0 for c in counts)
                    or weights.get('denominator') != math.factorial(n)
                    or sum(counts) != math.factorial(n)):
                return 'INCOMPLETE'
    if (claimed == 'REFERENCE_COMPLETE' and checks_passed
            and worker.get('outcome') == 'COMPLETE' and worker.get('exit_code') == 0
            and not worker.get('error')):
        return claimed
    if (claimed == 'NUMERICAL_CHECK_FAILED' and not checks_passed
            and worker.get('outcome') == 'INCOMPLETE'
            and worker.get('exit_code') == 1
            and worker.get('error') == 'RuntimeError: worker exit 1'):
        return claimed
    return 'INCOMPLETE'


def run_reference(root: Path, commit: str, output: Path, dependency_path: Path | None = None):
    started, initial_cpu = time.monotonic(), _usage()[0]
    root, output = Path(root).resolve(), Path(output).resolve()
    if output == root or root in output.parents:
        raise ValueError('output must be outside checkout')
    output.mkdir(parents=True, exist_ok=False)
    manifest = output / 'manifest.json'
    record = dict(schema=1, diagnostic='D2-M0', outcome='INCOMPLETE', stage='setup',
                  commit=_commit_value(commit), cs0_acceptance=False, stochastic=False,
                  strict_aggregate_containment=False)
    record = _save_manifest(manifest, record)
    try:
        # No project/scientific imports precede the durable setup checkpoint.
        engineering = importlib.import_module('emergence_lab.cs0_engineering')
        supervisor = importlib.import_module('emergence_lab.cs0_supervisor')
        reference = importlib.import_module('emergence_lab.d2_m0_reference')
        sources = engineering.verify_sources(root, commit)
        engineering.verify_runtime(root)
        for module in (sys.modules['emergence_lab'], sys.modules[__name__], engineering, supervisor, reference):
            name = '__init__' if module.__name__ == 'emergence_lab' else module.__name__.split('.')[-1]
            if module is sys.modules[__name__]: name = 'd2_m0_runner'
            if Path(module.__file__).resolve() != root / f'src/emergence_lab/{name}.py':
                raise ValueError('loaded project module origin differs from checkout')
        protocol = (root / PROTOCOL).read_bytes()
        stored = subprocess.check_output(['git', 'show', f'{commit}:{PROTOCOL}'], cwd=root, timeout=10)
        if protocol != stored:
            raise ValueError('protocol bytes differ from pinned commit')
        config = reference.protocol_config()
        record.update(config=config, config_sha256=hashlib.sha256(_json(config)).hexdigest(),
                      protocol_sha256=hashlib.sha256(protocol).hexdigest(), source_sha256=sources,
                      interpreter=sys.executable, stage='worker')
        record = _save_manifest(manifest, record)
        if record.get('stage') != 'worker': raise ValueError('setup manifest could not fit its reserved slot')
        paths = [str(root / 'src')]
        if dependency_path is not None:
            dependency_path = Path(dependency_path).resolve(strict=True)
            if not dependency_path.is_dir(): raise ValueError('dependency path must be a trusted directory')
            paths.append(str(dependency_path)); record['trusted_dependency_path'] = str(dependency_path)
        cache = output / 'empty-cache'; cache.mkdir()
        bootstrap = ('import sys,runpy; sys.path[:0]=' + repr(paths)
                     + "; runpy.run_module('emergence_lab.d2_m0_reference',run_name='__main__')")
        _check_cost(started)
        worker = supervisor.supervise([sys.executable, '-I', '-B', '-X', f'pycache_prefix={cache}',
            '-c', bootstrap], output / 'worker', root, commit,
            supervisor.Limits(cpu_seconds=27, wall_seconds=55, memory_bytes=384 * 1024**2,
                              output_bytes=700_000))
        record['worker'] = {k: worker[k] for k in ('outcome', 'error', 'exit_code',
                          'worker_cpu_seconds', 'worker_peak_rss_kib') if k in worker}
        _check_cost(started)
        for path in (output / 'worker/manifest.json', output / 'worker/manifest.tmp'):
            if path.exists() and path.stat().st_size > MANIFEST_BYTES // 2:
                raise ValueError('worker metadata exceeds reserved space')
        raw = (output / 'worker/worker.bin').read_bytes()
        if len(raw) > 700_000 or hashlib.sha256(raw).hexdigest() != worker.get('output_sha256'):
            raise ValueError('worker raw digest or size mismatch')
        payload = json.loads(raw)
        outcome = classify_payload(payload, config, worker)
        if outcome == 'INCOMPLETE': raise ValueError('worker or payload did not satisfy reference contract')
        report = {k: v for k, v in payload.items() if k not in ('cells', 'exact_weights')}
        planned = {'exact_weights.json': _json(payload['exact_weights']),
                   'curve.csv': reference.reference_csv(payload).encode(), 'checks/report.json': _json(report)}
        if len(raw) + sum(map(len, planned.values())) + RESERVE > TOTAL_BYTES:
            raise ValueError('derived artifacts exceed total retained-output budget')
        for name, data in planned.items():
            path = output / name
            if path.exists() or path.with_suffix('.tmp').exists(): raise ValueError('refusing artifact replacement')
            _atomic(path, data)
        if engineering.verify_sources(root, commit) != sources:
            raise ValueError('source changed during execution')
        if (root / PROTOCOL).read_bytes() != protocol: raise ValueError('protocol changed during execution')
        record.update(outcome=outcome, stage='finished', versions=payload['versions'])
    except Exception as error:
        record.update(outcome='INCOMPLETE', error=f'{type(error).__name__}: {error}'[:2048])
    finally:
        files = [p for p in output.rglob('*') if p.is_file() and p != manifest]
        record['artifacts'] = {p.relative_to(output).as_posix(): dict(bytes=p.stat().st_size,
            sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files}
        cpu, rss = _usage()
        elapsed = time.monotonic() - started
        record.update(observed_pre_finalization_cpu_seconds=cpu,
                      observed_interval_cpu_seconds=cpu - initial_cpu,
                      observed_pre_finalization_wall_seconds=elapsed,
                      finalization_margin_cpu_seconds=FINALIZATION_SECONDS,
                      finalization_margin_wall_seconds=FINALIZATION_SECONDS,
                      budgeted_total_cpu_seconds=cpu + FINALIZATION_SECONDS,
                      budgeted_total_wall_seconds=elapsed + FINALIZATION_SECONDS,
                      cost_scope='CPU includes process bootstrap and all previously waited children; wall starts at run entry. API reuse can overestimate this run. Final manifest replacement uses the explicit reserve, not measured final cost.',
                      conservative_peak_rss_kib=rss,
                      retained_payload_bytes=sum(p.stat().st_size for p in files))
        if (record['budgeted_total_cpu_seconds'] > 30 or record['budgeted_total_wall_seconds'] > 60
                or rss > 512 * 1024 or record['retained_payload_bytes'] + RESERVE > TOTAL_BYTES):
            record.update(outcome='INCOMPLETE', error='observed aggregate budget exceeded')
        record = _save_manifest(manifest, record)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--dependency-path', type=Path)
    args = parser.parse_args(argv)
    result = run_reference(args.root, args.commit, args.output, args.dependency_path)
    print(json.dumps(dict(outcome=result['outcome'], diagnostic='D2-M0', cs0_acceptance=False)))
    return {'REFERENCE_COMPLETE': 0, 'NUMERICAL_CHECK_FAILED': 1, 'INCOMPLETE': 2}[result['outcome']]


if __name__ == '__main__':
    raise SystemExit(main())
