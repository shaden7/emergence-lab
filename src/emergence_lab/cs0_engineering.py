"""Engineering-only CS0 orchestration. Never authorizes or executes a full study.

The aggregate resource fields are measurements, not hard aggregate containment.
Only the worker has the existing supervisor's per-process enforcement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

from emergence_lab.cs0_recheck import check_rows, read_rows_csv
from emergence_lab.cs0_supervisor import Limits, checkpoint, supervise, verify_checkout
from emergence_lab.cs0_artifacts import (
    ENGINEERING_BOUND_BYTES, ENGINEERING_SLOTS, MAX_ARTIFACT_BYTES,
    atomic_write, bounded_error, csv_bytes, manifest_checkpoint, safe_commit,
    verify_engineering_slots,
)


ENGINEERING_ENTROPY = 2036110697
ENGINEERING_DESIGN = dict(mode='engineering', sizes=[8, 12], replicates=3,
    diamond_dimensions=[2, 3, 4], k_orders=[3, 4], two_layer_p=.5,
    family_indices=dict(diamond=0, two_layer=1, k_order=2, chain=3, antichain=4))


def verify_runtime(root: Path):
    """Refuse a launcher/supervisor/rechecker imported from another checkout."""
    for name, relative in (
        ('emergence_lab', '__init__.py'),
        (__name__, 'cs0_engineering.py'),
        ('emergence_lab.cs0_supervisor', 'cs0_supervisor.py'),
        ('emergence_lab.cs0_recheck', 'cs0_recheck.py'),
        ('emergence_lab.cs0_artifacts', 'cs0_artifacts.py'),
    ):
        module = sys.modules[name]
        if Path(module.__file__).resolve() != root / 'src/emergence_lab' / relative:
            raise ValueError(f'launcher runtime origin differs: {name}')


def verify_sources(root: Path, commit: str) -> dict[str, str]:
    """Compare every project source byte to Git, including status-hidden changes.

    Source cache reads use a fresh external pycache prefix in the child. This
    does not attest the interpreter, third-party dependencies or concurrent
    adversarial filesystem changes.
    """
    verify_checkout(root, commit)
    top = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'],
                                  cwd=root, text=True, timeout=10).strip()
    if Path(top).resolve() != root:
        raise ValueError('root must be the checkout top level')
    paths = subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', commit, '--', 'src'],
        cwd=root, text=True, timeout=10).splitlines()
    expected = set(paths)
    if not expected or any(not p.endswith('.py') for p in paths):
        raise ValueError('only tracked Python source is supported')
    for path in (root / 'src').rglob('*'):
        if path.is_symlink():
            raise ValueError('symlink in source tree')
        if path.is_file() and path.relative_to(root).as_posix() not in expected:
            relative = path.relative_to(root)
            # pip's editable install emits inert distribution metadata here.
            # Do not admit Python/.pth/extension files or nested directories.
            if (len(relative.parts) == 3
                    and relative.parts[1] == 'emergence_lab.egg-info'
                    and relative.name in {'PKG-INFO', 'SOURCES.txt',
                        'dependency_links.txt', 'entry_points.txt',
                        'requires.txt', 'top_level.txt'}):
                continue
            # Only conventional caches are ignored; no alternate modules/.so.
            if path.suffix != '.pyc' or path.parent.name != '__pycache__':
                raise ValueError('unexpected file in source tree')
    hashes = {}
    for name in paths:
        path = root / name
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != root):
            raise ValueError('symlink in tracked source path')
        actual = path.read_bytes()
        stored = subprocess.check_output(['git', 'show', f'{commit}:{name}'],
                                         cwd=root, timeout=10)
        if actual != stored:
            raise ValueError(f'source bytes differ: {name}')
        hashes[name] = hashlib.sha256(actual).hexdigest()
    return hashes


def _cpu():
    own = resource.getrusage(resource.RUSAGE_SELF)
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + child.ru_utime + child.ru_stime


def run_engineering(root: Path, commit: str, output: Path) -> dict:
    """Run only the disjoint miniature fixture and preserve a durable handoff."""
    root, output = root.resolve(), output.resolve()
    if output == root or root in output.parents:
        raise ValueError('output must be outside checkout')
    output.mkdir(parents=True, exist_ok=False)
    manifest = output / 'manifest.json'
    record = dict(schema=1, mode='engineering', study_authorized=False,
                  outcome='INCOMPLETE', stage='setup',
                  entropy=ENGINEERING_ENTROPY,
                  aggregate_caps_enforced=False,
                  inner_artifact_bound_bytes=ENGINEERING_BOUND_BYTES,
                  inner_artifact_slots=ENGINEERING_SLOTS.copy())
    if safe_commit(commit) is not None:
        record['commit'] = commit
    checkpoint(manifest, record)
    start, start_cpu = time.monotonic(), _cpu()
    try:
        hashes = verify_sources(root, commit)
        verify_runtime(root)
        record['source_sha256'] = hashes
        config_bytes = json.dumps(ENGINEERING_DESIGN, sort_keys=True).encode()
        record['config_sha256'] = hashlib.sha256(config_bytes).hexdigest()
        record['stage'] = 'worker'
        checkpoint(manifest, record)
        cache = output / 'empty-pycache'
        cache.mkdir()
        bootstrap = ('import sys; sys.path.insert(0, ' + repr(str(root / 'src')) +
                     '); from emergence_lab.cs0_worker import main; main()')
        command = [sys.executable, '-I', '-B', '-X', f'pycache_prefix={cache}',
                   '-c', bootstrap, '--mode', 'engineering', '--entropy',
                   str(ENGINEERING_ENTROPY)]
        child = supervise(command, output / 'worker', root, commit,
                          Limits(cpu_seconds=15, wall_seconds=30,
                                 memory_bytes=512 * 1024**2,
                                 output_bytes=MAX_ARTIFACT_BYTES))
        record['worker_outcome'] = child['outcome']
        if child['outcome'] != 'COMPLETE':
            raise ValueError(f'worker incomplete: {child.get("error")}')
        payload = (output / 'worker/worker.bin').read_bytes()
        if hashlib.sha256(payload).hexdigest() != child['output_sha256']:
            raise ValueError('worker output digest mismatch')
        messages = [json.loads(line) for line in payload.splitlines()]
        if not messages or messages[0].get('type') != 'metadata':
            raise ValueError('missing worker metadata')
        metadata = messages[0]
        if (metadata.get('schema') != 1 or metadata.get('mode') != 'engineering'
                or metadata.get('entropy') != ENGINEERING_ENTROPY
                or metadata.get('design') != ENGINEERING_DESIGN):
            raise ValueError('worker identity mismatch')
        if (set(metadata.get('versions', {})) != {'python', 'numpy', 'scipy'}
                or any(type(v) is not str or not v for v in metadata['versions'].values())):
            raise ValueError('invalid version metadata')
        if Path(metadata['modules']['package']).resolve() != root / 'src/emergence_lab/__init__.py':
            raise ValueError('wrong package resolution')
        for module in ('cs0_worker', 'causal_set_mm'):
            if Path(metadata['modules'][module]).resolve() != root / f'src/emergence_lab/{module}.py':
                raise ValueError(f'wrong module resolution: {module}')
        if any(m.get('type') != 'row' for m in messages[1:]):
            raise ValueError('unexpected worker message')
        rows = [{k: v for k, v in m.items() if k != 'type'} for m in messages[1:]]
        columns = ['family', 'D_or_k', 'N', 'rep', 'spawn_key', 'R', 'r',
                   'd_mm', 'classification']
        serialized = csv_bytes(
            ({**row, 'spawn_key': json.dumps(row['spawn_key'])} for row in rows), columns)
        atomic_write(output / 'measurements.csv', serialized)
        stored_rows = read_rows_csv(output / 'measurements.csv')
        report = check_rows(stored_rows, mode='engineering', entropy=ENGINEERING_ENTROPY)
        if report['verdict'] != 'ENGINEERING_ONLY':
            raise ValueError('engineering recheck must not certify a study')
        checkpoint(output / 'report.json', report)
        if verify_sources(root, commit) != hashes:
            raise ValueError('source snapshot changed during execution')
        record.update(outcome='COMPLETE', stage='finished', rows=len(rows),
                      metadata=metadata, report_verdict=report['verdict'])
    except Exception as error:
        record.update(outcome='INCOMPLETE', error=bounded_error(error))
    finally:
        record['observed_aggregate_cpu_seconds'] = _cpu() - start_cpu
        record['wall_seconds'] = time.monotonic() - start
        try:
            sizes = verify_engineering_slots(output)
            record['inner_artifact_slots_verified'] = True
            record['artifacts'] = {
                name: dict(bytes=size,
                    sha256=hashlib.sha256((output / name).read_bytes()).hexdigest())
                for name, size in sizes.items()
                if name not in ('manifest.json', 'manifest.tmp')}
        except (OSError, ValueError) as error:
            record.update(outcome='INCOMPLETE', inner_artifact_slots_verified=False,
                          error=bounded_error(error), artifacts={})
        # Manifest includes itself only via the total after final replacement;
        # the value below is explicitly payload-only, avoiding self-hash claims.
        record['payload_bytes'] = sum(v['bytes'] for v in record['artifacts'].values())
        record = manifest_checkpoint(manifest, record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    record = run_engineering(args.root, args.commit, args.output)
    print(json.dumps(record, sort_keys=True))
    return 0 if record['outcome'] == 'COMPLETE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
