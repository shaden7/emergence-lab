"""S1b engineering/synthetic checks. Never draw S1b graph OR bootstrap seeds."""
import copy
import json
import math
from pathlib import Path
import runpy

import numpy as np
import pytest

from emergence_lab import spectral_s1 as s1
from emergence_lab import spectral_s1b as sb
from emergence_lab.dimension_d2 import CAY, UST
from emergence_lab import s1b_limits as limits


def config():
    return json.loads(sb.CONFIG.read_text())


def tiny():
    d = sb.design(config(), engineering=True)
    # Fixed generous budgets avoid timing-dependent tests on millisecond instances.
    d.update(total_cpu_s=600., family_cpu_s={CAY: 600., UST: 600.})
    return d


def synthetic(d, contrast=.07):
    rows = []
    for job in sb.schedule(d):
        f, rep, i = job['family'], job['i_rep'], job['i_size']
        # Symmetric deterministic tree variation; no RNG and no use of locked seeds.
        exponent = .85 + (contrast if i == len(d['families'][f]['sizes'])-1 else 0)
        exponent += .003 * (rep - (d['families'][f]['trees']-1)/2)
        q = .8 * np.arange(1, d['T']+1, dtype=float) ** (-exponent/2)
        n = job['size'] if f == CAY else job['size'] ** 2
        for v in range(d['families'][f]['sources']):
            res = s1.KilledBallResult(v, 1, 64, d['T'], 10, 18, q.copy(), np.zeros(d['T']))
            rows.append(dict(job, n=n, res=res))
    return rows


def analyze(d, rows, **kwargs):
    args = dict(controls_passed=True, global_ok=True, family_ok={CAY: True, UST: True})
    args.update(kwargs)
    return sb.analyze(d, rows, **args)


def test_frozen_plan_allocation_and_round_robin_without_draws():
    d = sb.design(config())
    jobs = sb.schedule(d)
    assert len(jobs) == 168
    assert [j['seed'] for j in jobs[:5]] == [[2036101701, 0, 0, 0], [2036101701, 0, 1, 0],
        [2036101701, 0, 2, 0], [2036101701, 1, 0, 0], [2036101701, 1, 1, 0]]
    assert jobs[5]['seed'] == [2036101701, 0, 0, 1]
    assert len({tuple(j['seed']) for j in jobs}) == 168
    assert all(j['family'] == UST for j in jobs[120:])
    assert d['total_cpu_s'] == 12000 and d['family_cpu_s'] == {CAY: 9450, UST: 2070}


@pytest.mark.parametrize('change', ['seed', 'size', 'sources', 'window', 'budget', 'margin', 'eta', 'bootstrap'])
def test_config_drift_rejected(change):
    cfg = config()
    if change == 'seed': cfg['seed_base'] += 1
    if change == 'size': cfg['families'][CAY]['N'].reverse()
    if change == 'sources': cfg['families'][UST]['sources'] = 33
    if change == 'window': cfg['primary_window'] = [64, 512]
    if change == 'budget': cfg['budget']['hard_stop_total_cpu_min'] = 201
    if change == 'margin': cfg['outcomes']['margin'] = .04
    if change == 'eta': cfg['kernel']['eta'] = .001
    if change == 'bootstrap': cfg['bootstrap_seed'] += 1
    with pytest.raises(ValueError, match='reviewed'):
        sb.design(cfg)


def test_activated_code_still_requires_env_before_any_rng_or_files(monkeypatch, tmp_path):
    # A reviewed authorization flag does not let pytest draw scientific seeds.
    # Only the once-only workflow may supply the separate environment gate.
    monkeypatch.delenv('S1B_ALLOW_SEEDS', raising=False)
    monkeypatch.setattr(s1, '_seed_seq', lambda *a: pytest.fail('scientific RNG reached'))
    assert s1.S1B_RUN_AUTHORIZED is True
    with pytest.raises(PermissionError, match='locked'):
        s1.build_instance(CAY, 8, 0, 0, 1, s1.S1B_SEED_BASE)
    out = tmp_path/'locked'
    with pytest.raises(PermissionError, match='locked'):
        sb.run(sb.design(config()), out)
    assert not out.exists()
    with pytest.raises(PermissionError):
        sb.main(['--mode', 's1b', '--output', str(out)])
    with pytest.raises(PermissionError):
        sb._run(sb.design(config()), out, Path('.'))
    with pytest.raises(PermissionError):
        sb.analyze(sb.design(config()), [], True, True, {CAY: True, UST: True})


def test_interval_rules_match_design_reference_grid():
    ref = runpy.run_path('docs/experiments/s1b_outcome_reference.py')['classify_ci']
    for a in range(-60, 61):
        for b in range(a, 61):
            assert sb.classify_ci(a/1000, b/1000) == ref(a/1000, b/1000)
    assert sb.classify_ci(math.nan, .05) == 'UNRELIABLE'
    assert sb.classify_ci(.04, .03) == 'UNRELIABLE'


@pytest.mark.parametrize('effect,expected', [(.07,'MATERIAL-POSITIVE'), (-.07,'MATERIAL-NEGATIVE'),
                                           (0,'EQUIVALENT'), (.03,'INCONCLUSIVE')])
def test_synthetic_contrast_and_diagnostics(effect, expected):
    d = tiny()
    out = analyze(d, synthetic(d, effect))
    for f in sb.FAMILIES:
        assert out[f]['verdict'] == expected
        assert out[f]['contrast']['diff'] == pytest.approx(effect, abs=1e-12)
        assert out[f]['bootstrap_resamples'] == 64
        assert out[f]['jackknife_se'] > 0
        assert all(s['influence']['reliable'] for s in out[f]['sizes'])


def test_missing_descriptive_cay_size_blocks_even_complete_pair():
    d = tiny()
    rows = [r for r in synthetic(d) if not (r['family'] == CAY and r['i_size'] == 0)]
    assert analyze(d, rows)[CAY]['verdict'] == 'BLOCKED'
    assert analyze(d, rows)[UST]['verdict'] == 'MATERIAL-POSITIVE'


@pytest.mark.parametrize('fault', ['missing_source', 'duplicate_source', 'over_cap', 'missing_tree'])
def test_no_dropping_incomplete_or_censored_trees(fault):
    d = tiny(); rows = synthetic(d)
    row = next(r for r in rows if r['family'] == CAY and r['i_size'] == 0 and r['i_rep'] == 0)
    if fault == 'missing_source': rows.remove(row)
    if fault == 'duplicate_source': rows.append(row)
    if fault == 'over_cap': row['res'].status = 'OVER_CAP'
    if fault == 'missing_tree': rows = [r for r in rows if not (r['family'] == CAY and r['i_size'] == 0 and r['i_rep'] == 0)]
    assert analyze(d, rows)[CAY]['verdict'] == 'BLOCKED'


@pytest.mark.parametrize('fault', ['certification', 'headroom', 'zero_variance', 'nan'])
def test_per_size_reliability_veto_includes_descriptive_size(fault):
    d = tiny(); rows = synthetic(d)
    for r in rows:
        if r['family'] != CAY or r['i_size'] != 0: continue
        if fault == 'certification': r['res'].killed[-1] = 1
        if fault == 'headroom': r['res'].q_lower *= .001
        if fault == 'zero_variance': r['res'].q_lower[:] = .8*np.arange(1,d['T']+1)**(-.85/2)
        if fault == 'nan': r['res'].q_lower[-1] = np.nan
    assert analyze(d, rows)[CAY]['verdict'] == 'UNRELIABLE'


def test_controls_and_global_stop_block_both_family_stop_only_one():
    d = tiny(); rows = synthetic(d)
    assert all(x['verdict'] == 'BLOCKED' for x in analyze(d, rows, controls_passed=False).values())
    assert all(x['verdict'] == 'BLOCKED' for x in analyze(d, rows, global_ok=False).values())
    out = analyze(d, rows, family_ok={CAY: False, UST: True})
    assert out[CAY]['verdict'] == 'BLOCKED' and out[UST]['verdict'] == 'MATERIAL-POSITIVE'


def test_engineering_pipeline_byte_determinism_and_ledger(tmp_path):
    d = tiny()
    for name in ('a', 'b'):
        rep = sb.run(d, tmp_path/name, controls=False)
        assert all(r['verdict'] == 'BLOCKED' for r in rep['families'].values())
        assert not rep['s2_run_authorized'] and not rep['s2_design_may_be_drafted']
    assert (tmp_path/'a/numeric.csv').read_bytes() == (tmp_path/'b/numeric.csv').read_bytes()
    manifest = json.loads((tmp_path/'a/manifest.json').read_text())
    assert len(manifest['seed_tuples_attempted']) == 40
    assert {x[0] for x in manifest['seed_tuples_attempted']} == {sb.ENGINEERING_SEED}
    events = [json.loads(s) for s in (tmp_path/'a/attempts.jsonl').read_text().splitlines()]
    assert len(events) == 80 and all(x['status'] == 'STARTED' for x in events[::2])
    assert all(x['status'] == 'COMPLETED' for x in events[1::2])
    with pytest.raises(FileExistsError): sb.run(d, tmp_path/'a', controls=False)


def test_control_failure_precedes_generation_and_records_no_attempt(tmp_path, monkeypatch):
    monkeypatch.setattr(s1, 'run_p0', lambda root: {'pass': False})
    monkeypatch.setattr(s1, 'build_instance', lambda *a: pytest.fail('control STOP ignored'))
    report = sb.run(tiny(), tmp_path/'stopped')
    assert report['attempts'] == []
    assert all(r['verdict'] == 'BLOCKED' for r in report['families'].values())


def test_attempt_is_persisted_before_generator_failure(tmp_path, monkeypatch):
    out = tmp_path/'failed'
    def fail(*args):
        first = json.loads((out/'attempts.jsonl').read_text().splitlines()[0])
        assert first['status'] == 'STARTED'
        raise ValueError('synthetic generation failure')
    monkeypatch.setattr(s1, 'build_instance', fail)
    report = sb.run(tiny(), out, controls=False)
    assert len(report['attempts']) == 2  # first failure in each family, never replace it
    assert all(a['status'] == 'FAILED' for a in report['attempts'])


def test_final_tree_budget_overrun_vetoes_family(tmp_path, monkeypatch):
    d = tiny()
    original = s1.certified_returns
    used = [0.]
    class Clock:
        def __init__(self, total): self.total = total
        @staticmethod
        def cpu(): return used[0]
        def used(self): return used[0]
        def exceeded(self): return used[0] >= self.total
    def compute(*a, **k):
        r = original(*a, **k)
        used[0] += 1
        return r
    monkeypatch.setattr(sb, 'Budget', Clock)
    monkeypatch.setattr(s1, 'certified_returns', compute)
    d['family_cpu_s'][CAY] = 96  # 3 sizes * 8 trees * 4 sources
    rep = sb.run(d, tmp_path/'budget', controls=False)
    assert rep['family_budget_ok'][CAY] is False
    assert rep['families'][CAY]['verdict'] == 'BLOCKED'


def cgroup(tmp_path, monkeypatch):
    for name, value in {'cpu.max': '100000 100000', 'memory.max': str(2*sb.GIB),
                        'memory.swap.max': '0', 'cpu.stat': 'usage_usec 1234567\n'}.items():
        (tmp_path/name).write_text(value)
    monkeypatch.setattr(limits.socket, 'if_nameindex', lambda: [(1,'lo')])
    monkeypatch.setenv('S1B_HOST_CLASS', 'non-lightsail')
    for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        monkeypatch.setenv(k, '1')
    return tmp_path


def test_cgroup_preflight_and_cpu_counter(tmp_path, monkeypatch):
    path = cgroup(tmp_path, monkeypatch)
    assert limits.preflight(path, 2*sb.GIB)['memory.swap.max'] == '0'
    assert limits.cgroup_cpu(path) == pytest.approx(1.234567)


@pytest.mark.parametrize('name,value', [('cpu.max','max 100000'), ('cpu.max','200000 100000'),
    ('memory.max','max'), ('memory.max',str(3*sb.GIB)), ('memory.swap.max','max')])
def test_unbounded_resources_rejected(tmp_path, monkeypatch, name, value):
    path = cgroup(tmp_path, monkeypatch); (path/name).write_text(value)
    with pytest.raises(PermissionError): limits.preflight(path, 2*sb.GIB)


def test_network_or_host_attestation_missing_rejected(tmp_path, monkeypatch):
    path = cgroup(tmp_path, monkeypatch)
    monkeypatch.setattr(limits.socket, 'if_nameindex', lambda: [(1,'lo'), (2,'eth0')])
    with pytest.raises(PermissionError, match='network'): limits.preflight(path, 2*sb.GIB)
    monkeypatch.setattr(limits.socket, 'if_nameindex', lambda: [(1,'lo')])
    monkeypatch.delenv('S1B_HOST_CLASS')
    with pytest.raises(PermissionError, match='Lightsail'): limits.preflight(path, 2*sb.GIB)


def test_watchdog_trips_before_total_and_fails_closed_on_missing_counter(tmp_path, monkeypatch):
    path = cgroup(tmp_path, monkeypatch)
    guard = limits.ResourceGuard(tmp_path, 10., 2*sb.GIB, path)
    guard.start = 0.
    (path/'cpu.stat').write_text('usage_usec 8000000\n')
    calls = []
    monkeypatch.setattr(guard, 'stop', lambda why: calls.append(why))
    guard.watch()
    assert 'reserve' in calls[0]
    (path/'cpu.stat').unlink(); calls.clear()
    guard.watch()
    assert 'unavailable' in calls[0]
