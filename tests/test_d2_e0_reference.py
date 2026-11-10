"""D2-E0 reference/fixed-writer tests. Small-N fixtures only; the N=2..32
target is never evaluated here (no D2-E0 diagnostic is authorized)."""
from fractions import Fraction
from itertools import permutations
import gzip
import json
import math
import os

import pytest

pytest.importorskip('mpmath')

from emergence_lab import d2_e0_reference as e0  # noqa: E402

SMALL = (2, 3, 4, 5, 6)


def _brute_weights(n):
    """Direct endpoint-ensemble pair counts over all inner permutations."""
    m = n - 2
    counts = {}
    for perm in permutations(range(m)):
        inner = sum(1 for i in range(m) for j in range(i + 1, m) if perm[i] < perm[j])
        R = (2 * n - 3) + inner
        counts[R] = counts.get(R, 0) + 1
    return counts


@pytest.mark.parametrize('n', range(2, 10))
def test_weights_match_brute_force(n):
    w = e0.endpoint_weights(n)
    brute = _brute_weights(n)
    assert {w['offset'] + k: c for k, c in enumerate(w['counts'])} == brute
    assert sum(w['counts']) == math.factorial(n - 2) == w['denominator']


@pytest.mark.parametrize('n', range(2, 33))
def test_exact_controls_all_sizes(n):
    values, checks = e0.exact_controls(e0.endpoint_weights(n))
    assert all(checks.values()), checks
    assert values['mean_r'] == Fraction(1, 2) + Fraction(2 * n - 3, n * (n - 1))


def test_n4_explicit_control():
    w = e0.endpoint_weights(4)
    assert (w['offset'], w['counts'], w['pairs']) == (5, [1, 1], 6)


def test_invalid_sizes_refused():
    for bad in (1, 33, 2.0, True):
        with pytest.raises(ValueError):
            e0.endpoint_weights(bad)
    with pytest.raises(ValueError):
        e0.generate_reference((3, 2))


def test_r_one_exact_without_iteration():
    rec = e0.newton_inverse(Fraction(1), 1.0)
    assert rec['iterations'] == 0 and rec['d'].startswith('1.0000') and rec['residual_ok']


def test_newton_matches_independent_bisection():
    r = Fraction(5, 6)
    rec = e0.newton_inverse(r, e0._binary64_dimension(r))
    assert rec['converged'] and rec['sign_check'] and rec['residual_ok']
    assert abs(float(rec['d']) - float(e0.bisection_inverse(r))) < 1e-14


def test_newton_refuses_bad_seed_without_raising():
    rec = e0.newton_inverse(Fraction(1, 2), math.nan)
    assert rec['error'] and not rec['converged'] and rec['d'] is None


def test_inverse_refuses_binary64_input():
    with pytest.raises(ValueError):
        e0.newton_inverse(0.5, 2.0)
    with pytest.raises(ValueError):
        e0.bisection_inverse(Fraction(0))


def test_small_reference_complete_and_complete_coverage():
    p = e0.generate_reference(SMALL)
    assert p['outcome'] == 'REFERENCE_COMPLETE' and p['failures'] == []
    assert p['cs0_acceptance'] is False and p['config']['frozen'] is False
    rows = sum(len(e0.endpoint_weights(n)['counts']) for n in SMALL)
    assert p['counts']['support_rows'] == rows
    for cov, n in zip(p['coverage'], SMALL):
        w = e0.endpoint_weights(n)
        got = [Fraction(*p['fractions'][i]['r']) for i in cov['fraction_index']]
        assert got == [e0.support_fraction(w, k) for k in range(len(w['counts']))]
    by_n = {s['N']: s for s in p['summaries']}
    assert by_n[2]['dimension_of_mean_r'] == by_n[3]['mean_dimension'] == '1'
    for n in (4, 5, 6):
        assert float(by_n[n]['dimension_of_mean_r']) < 2
    assert all(c['passed'] for c in p['spot_checks']) and p['monotone']


def test_failed_inverse_is_retained_not_dropped():
    def broken(r, seed):
        rec = e0.newton_inverse(r, seed)
        if r == Fraction(5, 6):
            rec = dict(rec, sign_check=False)
        return rec
    p = e0.generate_reference((2, 3, 4), _inverse=broken)
    assert p['outcome'] == 'NUMERICAL_CHECK_FAILED'
    assert any(not f['passed'] and f['r'] == [5, 6] for f in p['fractions'])
    assert [s['N'] for s in p['summaries']] == [2, 3, 4]
    assert not {s['N']: s for s in p['summaries']}[4]['checks_passed']


def test_nonfinite_binary64_is_numerical_failure():
    def nan_at(r):
        return math.nan if r == Fraction(5, 6) else e0._binary64_dimension(r)
    p = e0.generate_reference((4,), _binary64=nan_at)
    assert p['outcome'] == 'NUMERICAL_CHECK_FAILED'
    assert any(f['binary64'] == 'nonfinite' for f in p['fractions'])


def test_binary64_discrepancy_gate():
    p = e0.generate_reference((5,), _binary64=lambda r: e0._binary64_dimension(r) + 1e-9)
    assert p['outcome'] == 'NUMERICAL_CHECK_FAILED'


# ------------------------------------------------------------ fixed writer

def test_slot_arithmetic():
    assert e0.SLOT_SUM == 1_763_840 and e0.TOTAL_CONTENT_BYTES - e0.SLOT_SUM == 236_160


def test_write_reference_roundtrip(tmp_path):
    payload = e0.generate_reference((2, 3, 4))
    record = e0.write_reference(tmp_path / 'out', payload, dict(commit='a' * 40))
    assert record['outcome'] == 'REFERENCE_COMPLETE' and record['stage'] == 'finished'
    data = (tmp_path / 'out' / e0.REFERENCE_NAME).read_bytes()
    assert json.loads(gzip.decompress(data)) == json.loads(json.dumps(payload))
    assert set(os.listdir(tmp_path / 'out')) == {e0.REFERENCE_NAME, e0.MANIFEST_NAME, e0.LOG_NAME}
    assert sum(record['present'].values()) <= e0.SLOT_SUM


def test_existing_directory_refused(tmp_path):
    (tmp_path / 'out').mkdir()
    with pytest.raises(FileExistsError):
        e0.FixedWriter(tmp_path / 'out')


def test_oversized_reference_refused_before_open(tmp_path, monkeypatch):
    opened = []
    real_open = os.open
    monkeypatch.setattr(e0.os, 'open', lambda p, *a, **k: (opened.append(str(p)), real_open(p, *a, **k))[1])
    record = e0.write_reference(tmp_path / 'out', dict(outcome='REFERENCE_COMPLETE'), {},
                                _compress=lambda raw: b'x' * (e0.REFERENCE_BYTES + 1))
    assert record['outcome'] == 'INCOMPLETE' and record['manifest_persisted']
    assert not any(e0.REFERENCE_NAME in p for p in opened)
    assert not (tmp_path / 'out' / e0.REFERENCE_NAME).exists()
    manifest = json.loads((tmp_path / 'out' / e0.MANIFEST_NAME).read_bytes())
    assert manifest['outcome'] == 'INCOMPLETE' and manifest['stage'] == 'compress'


def test_compression_failure_is_incomplete(tmp_path):
    def boom(raw):
        raise MemoryError('simulated')
    record = e0.write_reference(tmp_path / 'out', dict(outcome='REFERENCE_COMPLETE'), {}, _compress=boom)
    assert record['outcome'] == 'INCOMPLETE' and 'MemoryError' in record['reason']
    record = e0.write_reference(tmp_path / 'o2', dict(outcome='REFERENCE_COMPLETE'), {},
                                _compress=lambda raw: gzip.compress(raw[:-2]))
    assert record['outcome'] == 'INCOMPLETE' and 'round-trip' in record['reason']


def test_nonserializable_payload_is_incomplete(tmp_path):
    record = e0.write_reference(tmp_path / 'out', dict(outcome='REFERENCE_COMPLETE', x=math.nan), {})
    assert record['outcome'] == 'INCOMPLETE' and record['stage'] == 'serialize'


def test_interrupted_replacement_keeps_bound_and_incomplete(tmp_path, monkeypatch):
    real = os.replace
    def fail_reference(src, dst):
        if str(dst).endswith(e0.REFERENCE_NAME):
            raise OSError('simulated power loss during replace')
        return real(src, dst)
    monkeypatch.setattr(e0.os, 'replace', fail_reference)
    record = e0.write_reference(tmp_path / 'out', dict(outcome='REFERENCE_COMPLETE'), {})
    assert record['outcome'] == 'INCOMPLETE' and record['stage'] == 'reference'
    monkeypatch.setattr(e0.os, 'replace', real)
    out = tmp_path / 'out'
    assert not (out / e0.REFERENCE_NAME).exists()
    writer = e0.FixedWriter.__new__(e0.FixedWriter)
    writer.directory, writer._log_used = out, 0
    present = writer.audit()  # stale temporary is a counted slot within bound
    assert sum(present.values()) <= e0.SLOT_SUM
    writer.replace(e0.REFERENCE_NAME, b'ok')  # stale temporary removed first
    assert set(os.listdir(out)) == {e0.REFERENCE_NAME, e0.MANIFEST_NAME, e0.LOG_NAME}


def test_unexpected_entry_refused(tmp_path):
    writer = e0.FixedWriter(tmp_path / 'out')
    (tmp_path / 'out' / 'spill.bin').write_bytes(b'x')
    with pytest.raises(e0.WriterRefusal):
        writer.replace(e0.MANIFEST_NAME, b'{}')
    with pytest.raises(e0.WriterRefusal):
        writer.replace('other.json', b'{}')


def test_log_is_bounded(tmp_path):
    writer = e0.FixedWriter(tmp_path / 'out')
    for _ in range(200):
        writer.log('y' * 4000)
    size = (tmp_path / 'out' / e0.LOG_NAME).stat().st_size
    assert size <= e0.LOG_BYTES
    assert (tmp_path / 'out' / e0.LOG_NAME).read_bytes().endswith(b'[log truncated]\n')


def test_oversized_manifest_base_degrades_to_minimal(tmp_path):
    record = e0.write_reference(tmp_path / 'out', dict(outcome='REFERENCE_COMPLETE'),
                                dict(commit='c' * 40, blob='z' * 40_000))
    assert record['outcome'] == 'INCOMPLETE' and record['stage'] == 'manifest'
    assert (tmp_path / 'out' / e0.MANIFEST_NAME).stat().st_size <= e0.MANIFEST_BYTES


def test_import_evaluates_nothing():
    import subprocess, sys
    code = ('import sys,time;t=time.process_time();import emergence_lab.d2_e0_reference;'
            'assert "mpmath" not in sys.modules;print(time.process_time()-t)')
    out = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
