"""Manufactured transport/control records only: never evaluate the M0 curve."""
import copy
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from emergence_lab.d2_m0_runner import _save_manifest, classify_payload, run_reference


CONFIG = dict(diagnostic='D2-M0', sizes=list(range(2, 33)), stochastic=False)


def payload():
    # These normalized support weights are deliberately NOT asserted to be
    # Mahonian. The fixture tests a reviewed producer's transport contract only.
    weights = []
    for n in range(2, 33):
        counts = [1] * (math.comb(n, 2) + 1)
        counts[len(counts) // 2] += math.factorial(n) - len(counts)
        weights.append(dict(N=n, denominator=math.factorial(n), counts=counts))
    return dict(schema=1, diagnostic='D2-M0', config=CONFIG,
        outcome='REFERENCE_COMPLETE', cs0_acceptance=False, stochastic=False,
        cells=[dict(N=n, checks_passed=True) for n in range(2, 33)],
        exact_weights=weights,
        exact_controls=[dict(N=n, checks=dict(fixture=True)) for n in range(2, 33)],
        numeric_checks=[dict(name=f'fixture-{n}', passed=True) for n in range(66)],
        probe_checks=[dict(name=f'probe-{n}', passed=True) for n in range(6)],
        versions=dict(python='fixture', numpy='fixture', scipy='fixture', mpmath='fixture'))


def worker(exit_code=0, error=None):
    return dict(outcome='COMPLETE' if exit_code == 0 else 'INCOMPLETE',
                exit_code=exit_code, **({} if error is None else dict(error=error)))


def test_valid_and_negative_outcomes_preserve_resource_precedence():
    record = payload()
    assert classify_payload(record, CONFIG, worker()) == 'REFERENCE_COMPLETE'
    record.update(outcome='NUMERICAL_CHECK_FAILED')
    record['cells'][4]['checks_passed'] = False
    stopped = worker(1, 'RuntimeError: worker exit 1')
    assert classify_payload(record, CONFIG, stopped) == 'NUMERICAL_CHECK_FAILED'
    for reason in ('RuntimeError: output limit', 'RuntimeError: wall limit', 'other'):
        assert classify_payload(record, CONFIG, worker(1, reason)) == 'INCOMPLETE'
    assert classify_payload(record, CONFIG, worker(-9, 'RuntimeError: worker exit -9')) == 'INCOMPLETE'


@pytest.mark.parametrize('mutation', [
    lambda r: r.update(schema=2), lambda r: r.update(cs0_acceptance=True),
    lambda r: r.update(stochastic=True), lambda r: r.update(config={}),
    lambda r: r['cells'].pop(), lambda r: r['cells'][0].update(N=3),
    lambda r: r['cells'][0].update(checks_passed=False),
    lambda r: r.update(numeric_checks=[]), lambda r: r.update(probe_checks=[]),
    lambda r: r['exact_weights'][0].update(counts=[1, 2]),
    lambda r: r.update(exact_controls=[]), lambda r: r.update(versions={}),
])
def test_inconsistent_success_is_incomplete(mutation):
    record = payload(); mutation(record)
    assert classify_payload(record, CONFIG, worker()) == 'INCOMPLETE'


@pytest.fixture
def committed_fixture(tmp_path):
    root = tmp_path / 'repo'; package = root / 'src/emergence_lab'; package.mkdir(parents=True)
    source = Path(__file__).resolve().parents[1] / 'src/emergence_lab'
    names = ['__init__', 'd2_m0_runner', 'cs0_engineering', 'cs0_supervisor', 'cs0_recheck']
    if (source / 'cs0_artifacts.py').exists(): names.append('cs0_artifacts')
    for name in names:
        (package / f'{name}.py').write_bytes((source / f'{name}.py').read_bytes())
    (root / 'docs').mkdir()
    (root / 'docs/CS0_D2_M0_PROTOCOL.md').write_text('Synthetic protocol transport fixture.\n')
    (root / '.gitignore').write_text('__pycache__/\n')
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    return root


def execute_fixture(root, output, record, exit_code=0, wrong_pin=False):
    package = root / 'src/emergence_lab'
    code = f'''import json,sys
CONFIG = {CONFIG!r}
def protocol_config(): return CONFIG
def generate_reference(): raise AssertionError('target must not run in fixtures')
def reference_csv(record):
    return 'N,fixture\\n' + ''.join(str(c['N'])+',synthetic\\n' for c in record['cells'])
if __name__ == '__main__':
    print(json.dumps({record!r}))
    raise SystemExit({exit_code})
'''
    (package / 'd2_m0_reference.py').write_text(code)
    subprocess.run(['git', 'add', '.'], cwd=root, check=True)
    subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=t@example.invalid',
                    'commit', '-qm', 'synthetic producer'], cwd=root, check=True)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if wrong_pin: commit = '0' * 40
    bootstrap = ('import sys; sys.path.insert(0,' + repr(str(root / 'src'))
                 + '); from emergence_lab.d2_m0_runner import main; sys.exit(main())')
    result = subprocess.run([sys.executable, '-I', '-B', '-X', f'pycache_prefix={output}-cache',
        '-c', bootstrap, '--root', str(root), '--commit', commit, '--output', str(output)],
        capture_output=True, text=True, timeout=20,
        env={**os.environ, 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'})
    assert result.returncode in (0, 1, 2), result.stderr
    return result, json.loads((output / 'manifest.json').read_text())


@pytest.mark.parametrize('negative', [False, True])
def test_committed_synthetic_producer_is_run_once_without_target_evaluation(committed_fixture, tmp_path, negative):
    record = payload()
    if negative:
        record['outcome'] = 'NUMERICAL_CHECK_FAILED'; record['cells'][5]['checks_passed'] = False
    result, manifest = execute_fixture(committed_fixture, tmp_path / 'out', record, int(negative))
    assert result.returncode == int(negative), manifest
    assert manifest['outcome'] == ('NUMERICAL_CHECK_FAILED' if negative else 'REFERENCE_COMPLETE')
    assert manifest['cs0_acceptance'] is False and manifest['stochastic'] is False
    assert manifest['strict_aggregate_containment'] is False
    assert manifest['retained_payload_bytes'] + 49152 <= 1_000_000
    assert set(manifest['artifacts']) == {'worker/worker.bin', 'worker/manifest.json',
        'curve.csv', 'exact_weights.json', 'checks/report.json'}
    assert (tmp_path / 'out/curve.csv').read_text().count('\n') == 32
    assert manifest['observed_pre_finalization_cpu_seconds'] > 0
    assert manifest['budgeted_total_cpu_seconds'] == manifest['observed_pre_finalization_cpu_seconds'] + 1
    assert manifest['budgeted_total_wall_seconds'] == manifest['observed_pre_finalization_wall_seconds'] + 1


def test_derived_output_budget_stops_before_extra_artifacts(committed_fixture, tmp_path):
    record = payload(); record['extra'] = 'x' * 630_000
    result, manifest = execute_fixture(committed_fixture, tmp_path / 'out', record)
    assert result.returncode == 2 and manifest['outcome'] == 'INCOMPLETE'
    assert 'retained-output budget' in manifest['error']
    assert not (tmp_path / 'out/curve.csv').exists()
    assert not (tmp_path / 'out/exact_weights.json').exists()
    assert manifest['retained_payload_bytes'] + 49152 <= 1_000_000


def test_wrong_revision_preserves_incomplete_without_child(committed_fixture, tmp_path):
    result, manifest = execute_fixture(committed_fixture, tmp_path / 'out', payload(), wrong_pin=True)
    assert result.returncode == 2 and manifest['outcome'] == 'INCOMPLETE'
    assert 'pinned commit' in manifest['error']
    assert not (tmp_path / 'out/worker').exists()


def test_oversized_manifest_never_publishes_completion(tmp_path):
    path = tmp_path / 'manifest.json'
    record = _save_manifest(path, dict(commit='a' * 40, outcome='REFERENCE_COMPLETE',
                                       padding='x' * 20000))
    assert record['outcome'] == 'INCOMPLETE'
    assert path.stat().st_size <= 16384
    assert record == json.loads(path.read_text())
    assert not path.with_suffix('.tmp').exists()


def test_nonprimitive_commit_cannot_execute_string_conversion_before_checkpoint(committed_fixture, tmp_path):
    class HostileCommit:
        def __str__(self): raise AssertionError('must not coerce commit objects')
    output = tmp_path / 'out'
    record = run_reference(committed_fixture, HostileCommit(), output)
    assert record['outcome'] == 'INCOMPLETE'
    assert record['commit'] == '<invalid commit>'
    assert (output / 'manifest.json').exists()
    assert not (output / 'worker').exists()
