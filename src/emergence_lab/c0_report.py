"""C0 report-contract validation (C0-G4 structure), shared by worker and supervisor.

The validator checks the *shape and internal consistency* of a C0 report: required
metadata, every required observed/oracle/residual value, finite numbers, complete
time/radius coverage, gate keys and labels; the arithmetic identities linking reported
derived fields (errors, residuals, offsets, log-ratios, local spectral slopes and
headroom outcomes) to the reported observed/oracle/infinite returns and floor; topology-field coherence; and agreement between each true gate and the reported
per-row evidence for that gate. It does not recompute kernels or oracles from graphs;
numerical agreement is established by the worker's gates C0-G0..G3, and this validator
only ensures a report cannot claim a true gate that its own rows contradict.
"""
import math

from emergence_lab.spectral_dimension import has_powerlaw_headroom, local_spectral_slope

TIMES = [8, 16, 32, 64, 128, 256]
RADII = [4, 8, 16, 32]
SLOPE_RADII = RADII[:-1]
GRAPHS = {  # name: (dimension_parameter, side, n, null, bipartite, floor)
    'C1024': (1, 1024, 1024, False, True, 2 / 1024),
    'T256': (2, 256, 65536, False, True, 2 / 65536),
    'C8': (1, 8, 8, True, True, 2 / 8),
    'K32': (0, 32, 32, True, False, 1 / 32),
}
GATES = [f'C0-G{i}' for i in range(4)]
TOPOLOGY_KEYS = ['connected', 'simple', 'undirected', 'no_self_loops', 'no_duplicate_edges']


def _finite(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def _need(condition, message):
    if not condition:
        raise ValueError(message)


def _numbers(entry, keys, where):
    _need(isinstance(entry, dict), where + ': not an object')
    for key in keys:
        _need(_finite(entry.get(key)), f'{where}: missing or non-finite {key}')


def _same(reported, recomputed, where):
    """Exact identity check: derived fields are computed by the same float expression."""
    _need(reported == recomputed, where + ': derived field inconsistent with reported values')


def validate_row(row):
    """Fail closed on missing kernel evidence, coverage gaps or inconsistent labels."""
    _need(isinstance(row, dict), 'row is not an object')
    if row.get('kernel') != 'graph_even_returns':
        raise ValueError('missing graph kernel evidence')
    _need(row.get('volume_kernel') == 'shell_counts', 'missing volume kernel evidence')
    _need(isinstance(row.get('bipartite'), bool) and isinstance(row.get('n'), int)
          and row['n'] > 0, 'missing graph metadata')
    expected_floor = (2 if row['bipartite'] else 1) / row['n']
    if row.get('floor') != expected_floor:
        raise ValueError('wrong stationary floor')
    returns = row.get('returns')
    _need(isinstance(returns, dict), 'missing returns')
    for t in TIMES[:-1]:
        if str(t) not in returns or str(2 * t) not in returns:
            raise ValueError('missing doubled endpoint')
    _need(set(returns) == {str(t) for t in TIMES}, 'unexpected return times')
    if row.get('null') and row.get('classification') != 'SATURATED':
        raise ValueError('invalid positive null classification')
    _need(isinstance(row.get('null'), bool), 'missing null flag')
    if not row['null']:
        _need(row.get('classification') == 'POINTWISE_CONTROL', 'invalid positive classification')
    positive_lattice = row.get('dimension_parameter') in (1, 2)
    for t in TIMES:
        keys = ['observed', 'oracle', 'absolute_error', 'relative_error']
        if positive_lattice:
            keys += ['infinite', 'finite_relative_to_infinite']
        entry = returns[str(t)]
        _numbers(entry, keys, f'return {t}')
        _need(entry['oracle'] > 0, f'return {t}: non-positive oracle')
        _same(entry['absolute_error'], abs(entry['observed'] - entry['oracle']), f'return {t}')
        _same(entry['relative_error'], entry['absolute_error'] / entry['oracle'], f'return {t}')
        if positive_lattice:
            _need(entry['infinite'] > 0, f'return {t}: non-positive infinite-lattice value')
            _same(entry['finite_relative_to_infinite'],
                  (entry['oracle'] - entry['infinite']) / entry['infinite'], f'return {t}')
    slopes = row.get('spectral_slopes')
    _need(isinstance(slopes, list) and [s.get('half_time') if isinstance(s, dict) else None
                                        for s in slopes] == TIMES[:-1], 'spectral slope coverage')
    for s in slopes:
        _numbers(s, ['observed', 'oracle', 'residual'] +
                 (['infinite_slope_offset'] if positive_lattice else []), 'slope')
        t = s['half_time']
        early, late = returns[str(t)], returns[str(2 * t)]
        # Slopes and headroom are derived from the reported returns with the worker's own
        # functions, so these identities are exact (and survive a JSON round trip).
        _same(s['observed'], local_spectral_slope(early['observed'], late['observed']),
              f'slope {t} observed vs returns')
        _same(s['oracle'], local_spectral_slope(early['oracle'], late['oracle']),
              f'slope {t} oracle vs returns')
        _same(s['residual'], s['observed'] - s['oracle'], 'slope')
        if positive_lattice:
            _same(s['infinite_slope_offset'],
                  local_spectral_slope(early['infinite'], late['infinite'])
                  - row['dimension_parameter'], f'slope {t} infinite offset')
        head = s.get('headroom')
        _need(isinstance(head, dict) and set(head) == {'5', '10', '20'}
              and all(isinstance(v, bool) for v in head.values()), 'headroom outcomes')
        for k in (5, 10, 20):
            _same(head[str(k)], all(has_powerlaw_headroom(e['observed'], row['floor'], ratio=k)
                                    for e in (early, late)), f'slope {t} headroom {k}')
    topology = row.get('topology')
    _need(isinstance(topology, dict) and set(TOPOLOGY_KEYS) <= set(topology)
          and all(isinstance(topology[k], bool) for k in TOPOLOGY_KEYS), 'topology evidence')
    _need(topology['simple'] == (topology['no_self_loops'] and topology['no_duplicate_edges']),
          'topology: simple inconsistent with no_self_loops/no_duplicate_edges')
    volume = row.get('volume')
    verdict = row.get('volume_verdict')
    _need(isinstance(volume, list) and isinstance(verdict, dict), 'missing volume evidence')
    if row['null']:
        _need(volume == [] and verdict.get('verdict') == 'INSUFFICIENT_RANGE'
              and verdict.get('d_hat') is None, 'null volume verdict')
    else:
        _need([v.get('radius') if isinstance(v, dict) else None for v in volume] == SLOPE_RADII,
              'volume slope coverage')
        for v in volume:
            _numbers(v, ['ball', 'double_ball', 'oracle_ball', 'oracle_double_ball', 'observed',
                         'oracle', 'residual', 'limiting_d', 'finite_radius_offset'], 'volume')
            _need(v.get('classification') == 'FINITE_RADIUS_CORRECTION', 'volume label')
            _need(v['ball'] > 0 and v['oracle_ball'] > 0, 'volume: non-positive ball')
            _same(v['observed'], math.log2(v['double_ball'] / v['ball']), 'volume observed')
            _same(v['oracle'], math.log2(v['oracle_double_ball'] / v['oracle_ball']), 'volume oracle')
            _same(v['residual'], v['observed'] - v['oracle'], 'volume residual')
            _same(v['limiting_d'], row.get('dimension_parameter'), 'volume limiting_d')
            _same(v['finite_radius_offset'], v['oracle'] - v['limiting_d'], 'volume offset')


def check_gate_evidence(rows, gates):
    """A true gate must not be contradicted by the report's own per-row evidence.

    Thresholds are the worker's frozen C0 gate thresholds. This is a necessary-condition
    check on reported values only; it cannot detect a fabricated but self-consistent report.
    """
    if gates['C0-G0']:
        for row in rows:
            _need(all(row['topology'][k] for k in TOPOLOGY_KEYS),
                  'C0-G0 true but topology evidence false for ' + row['graph'])
    if gates['C0-G1']:
        for row in rows:
            for v in row['volume']:
                _need(v['ball'] == v['oracle_ball'] and v['double_ball'] == v['oracle_double_ball']
                      and abs(v['residual']) <= 1e-12,
                      'C0-G1 true but volume evidence disagrees for ' + row['graph'])
    if gates['C0-G2']:
        for row in rows:
            for e in row['returns'].values():
                _need(e['absolute_error'] <= 1e-12 and e['relative_error'] <= 1e-9,
                      'C0-G2 true but return error exceeds tolerance for ' + row['graph'])
            for s in row['spectral_slopes']:
                _need(abs(s['residual']) <= 1e-9,
                      'C0-G2 true but slope residual exceeds tolerance for ' + row['graph'])
    if gates['C0-G3']:
        for row in rows:
            if not row['null']:
                _need(all(s['headroom']['10'] for s in row['spectral_slopes']),
                      'C0-G3 true but positive-control headroom false for ' + row['graph'])
            else:
                _need(abs(row['spectral_slopes'][-1]['observed']) <= 0.02
                      and all(abs(row['returns'][str(t)]['observed'] / row['floor'] - 1) <= 0.01
                              for t in (128, 256))
                      and row['volume_verdict'].get('verdict') == 'INSUFFICIENT_RANGE',
                      'C0-G3 true but null control not saturated for ' + row['graph'])


def validate_report(payload):
    """Validate a whole C0 report; raises ValueError on any contract violation."""
    _need(isinstance(payload, dict), 'report is not an object')
    _need(payload.get('schema') == 1, 'schema')
    _need(payload.get('rng') == 'not used', 'rng declaration')
    _need(payload.get('time_units') == 'half_steps_2t', 'time convention')
    _need(payload.get('radii') == RADII and payload.get('return_half_times') == TIMES, 'grids')
    rows = payload.get('graphs')
    _need(isinstance(rows, list) and [r.get('graph') if isinstance(r, dict) else None
                                      for r in rows] == list(GRAPHS), 'graph list')
    for row in rows:
        d, side, n, null, bipartite, floor = GRAPHS[row['graph']]
        _need((row.get('dimension_parameter'), row.get('side'), row.get('n'), row.get('null'),
               row.get('bipartite'), row.get('source')) == (d, side, n, null, bipartite, 0),
              'graph definition ' + row['graph'])
        _need(row.get('floor') == floor, 'wrong stationary floor')
        validate_row(row)
    gates = payload.get('gates')
    _need(isinstance(gates, dict) and set(gates) == set(GATES)
          and all(isinstance(v, bool) for v in gates.values()), 'gate set')
    check_gate_evidence(rows, gates)
    expected = 'PASS' if all(gates.values()) else 'FAIL'
    _need(payload.get('outcome') == expected, 'outcome inconsistent with gates')
