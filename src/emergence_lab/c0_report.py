"""C0 report-contract validation (C0-G4 structure), shared by worker and supervisor.

The validator checks the *shape and internal consistency* of a C0 report: required
metadata, every required observed/oracle/residual value, finite numbers, complete
time/radius coverage, gate keys and labels. It does not recompute kernels or oracles;
numerical agreement is established by the worker's gates C0-G0..G3.
"""
import math

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
        _numbers(returns[str(t)], keys, f'return {t}')
    slopes = row.get('spectral_slopes')
    _need(isinstance(slopes, list) and [s.get('half_time') if isinstance(s, dict) else None
                                        for s in slopes] == TIMES[:-1], 'spectral slope coverage')
    for s in slopes:
        _numbers(s, ['observed', 'oracle', 'residual'] +
                 (['infinite_slope_offset'] if positive_lattice else []), 'slope')
        head = s.get('headroom')
        _need(isinstance(head, dict) and set(head) == {'5', '10', '20'}
              and all(isinstance(v, bool) for v in head.values()), 'headroom outcomes')
    topology = row.get('topology')
    _need(isinstance(topology, dict) and set(TOPOLOGY_KEYS) <= set(topology)
          and all(isinstance(topology[k], bool) for k in TOPOLOGY_KEYS), 'topology evidence')
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
    expected = 'PASS' if all(gates.values()) else 'FAIL'
    _need(payload.get('outcome') == expected, 'outcome inconsistent with gates')
