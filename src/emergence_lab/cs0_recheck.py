"""Independent CS0 stored-count consistency checks; no simulation or authorization.

This module intentionally imports neither the causal-set producer nor its worker.
Stored pair counts cannot establish that their original relations were partial
orders, points lay in diamonds, or the correct RNG was used. A successful full
report is therefore conditional on upstream G0/provenance certification.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import re
from itertools import combinations
from statistics import fmean, stdev

from scipy.optimize import brentq
from scipy.stats import t as student_t

ENGINEERING_ENTROPY = 2036110697
_FIELDS = {'family', 'D_or_k', 'N', 'rep', 'spawn_key', 'R', 'r', 'd_mm',
           'classification'}
_FAMILIES = (('diamond', 2, 0), ('diamond', 3, 0), ('diamond', 4, 0),
             ('two_layer', 0, 1), ('k_order', 3, 2), ('k_order', 4, 2),
             ('chain', 0, 3), ('antichain', 0, 4))
_LIMITATION = ('MM alone does not distinguish a flat-diamond sprinkling from a '
               'random k-order and cannot certify manifold-likeness. CS0 is a '
               'global instrument calibration, not evidence of dimensional reduction.')


def _decimal_integer(value: str) -> int:
    if re.fullmatch(r'0|-?[1-9][0-9]*', value) is None:
        raise ValueError('expected a canonical decimal integer')
    return int(value)


def read_rows_csv(path: Path) -> list[dict]:
    """Read the actual persisted nine-column artifact without lossy coercion.

    Headers must contain each frozen field exactly once; their order may vary.
    Count/identity columns use canonical decimal integers, never float parsing.
    Semantic finite-value, identity and count checks belong to ``check_rows``.
    """
    rows = []
    try:
        with Path(path).open(newline='', encoding='utf-8') as stream:
            reader = csv.reader(stream, strict=True)
            header = next(reader, [])
            if len(header) != len(_FIELDS) or set(header) != _FIELDS:
                raise ValueError('CSV headers differ from the frozen nine-column schema')
            for fields in reader:
                if len(fields) != len(header):
                    raise ValueError(f'CSV row {reader.line_num} has the wrong column count')
                row = dict(zip(header, fields))
                for field in ('D_or_k', 'N', 'rep', 'R'):
                    row[field] = _decimal_integer(row[field])
                row['spawn_key'] = json.loads(row['spawn_key'])
                row['r'] = float(row['r'])
                row['d_mm'] = None if row['d_mm'] == '' else float(row['d_mm'])
                rows.append(row)
    except csv.Error as error:
        raise ValueError(f'malformed CSV: {error}') from error
    return rows


def _fraction(d: float) -> float:
    return math.exp(math.lgamma(d + 1) + math.lgamma(d / 2)
                    - math.log(2) - math.lgamma(1.5 * d))


def _dimension(r: float) -> float | None:
    if r == 1:
        return 1.0
    if r <= _fraction(64):
        return None
    return float(brentq(lambda d: _fraction(d) - r, 1, 64,
                        xtol=1e-13, rtol=1e-13, maxiter=200))


def _settings(mode: str, entropy: int):
    if type(entropy) is not int or entropy < 0:
        raise ValueError('entropy must be a nonnegative integer')
    if mode == 'engineering':
        if entropy != ENGINEERING_ENTROPY:
            raise ValueError('engineering requires its fixed disjoint entropy')
        return (8, 12), 3
    if mode == 'full':
        return (128, 256, 512, 1024), 30
    raise ValueError('mode must be engineering or full')


def _reference(family: str, parameter: int, n: int) -> float:
    if family == 'diamond':
        # Fractions independent of the producer; also audit the lgamma formula.
        exact = {2: .5, 3: 8 / 35, 4: .1}[parameter]
        if not math.isclose(_fraction(parameter), exact, rel_tol=2e-14):
            raise ValueError('independent closed-form reference disagreement')
        return exact
    if family == 'two_layer':
        return .5 * (n // 2) * (n - n // 2) / math.comb(n, 2)
    if family == 'k_order':
        return 2.0 ** (1 - parameter)
    return 1.0 if family == 'chain' else 0.0


def _number(value, name):
    try:
        valid = type(value) in (float, int) and math.isfinite(value)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(f'{name} must be a finite real number')
    return float(value)


def _mean_test(values: list[float], expected: float, cutoff: float) -> dict:
    mean = fmean(values)
    se = stdev(values) / math.sqrt(len(values))
    difference = mean - expected
    # A zero-variance sample has no defined t-reference, even at exact equality.
    # Conservatively fail the operational mean gate; this is not defect proof.
    defined = se != 0
    unbounded = se == 0 and difference != 0
    statistic = difference / se if defined else None
    return dict(mean_r=mean, se_r=se, expected_r=expected,
                t=statistic, t_defined=defined, t_unbounded=unbounded,
                mean_test_pass=defined and abs(statistic) <= cutoff)


def check_rows(rows: list[dict], mode: str, entropy: int) -> dict:
    """Validate frozen identities, counts, fractions, dimensions and mean gates.

    Malformed/incomplete artifacts raise ValueError (resource/provenance failures
    are INCOMPLETE at the launcher). Well-formed stochastic gate failures return
    FAIL in full mode and remain descriptive in engineering mode. No entropy is
    generated here; checking spawn keys cannot prove which RNG produced counts.
    """
    sizes, reps = _settings(mode, entropy)
    if type(rows) is not list:
        raise ValueError('rows must be a list')
    expected = {}
    for n in sizes:
        for family, parameter, index in _FAMILIES:
            for rep in range(1 if family in ('chain', 'antichain') else reps):
                expected[(family, parameter, n, rep)] = [index, parameter, n, rep]
    if len(rows) != len(expected):
        raise ValueError('missing or extra rows in frozen design')
    grouped = {}
    seen = set()
    for row in rows:
        if type(row) is not dict or set(row) != _FIELDS:
            raise ValueError('row fields differ from the frozen schema')
        if type(row['family']) is not str:
            raise ValueError('family must be a string')
        for field in ('D_or_k', 'N', 'rep', 'R'):
            if type(row[field]) is not int:
                raise ValueError(f'{field} must be an integer')
        identity = (row['family'], row['D_or_k'], row['N'], row['rep'])
        if identity not in expected or identity in seen:
            raise ValueError('unknown or duplicate realization identity')
        seen.add(identity)
        key = row['spawn_key']
        if (type(key) is not list or any(type(x) is not int for x in key)
                or key != expected[identity]):
            raise ValueError('spawn key differs from the frozen realization identity')
        n = row['N']
        pairs = math.comb(n, 2)
        count = row['R']
        if not 0 <= count <= pairs:
            raise ValueError('related-pair count outside [0,C(N,2)]')
        r = count / pairs
        stored_r = _number(row['r'], 'r')
        if not 0 <= stored_r <= 1 or not math.isclose(r, stored_r, rel_tol=0, abs_tol=1e-14):
            raise ValueError('ordering fraction disagrees with stored R')
        dimension = _dimension(r)
        classification = ('TOTAL_ORDER' if r == 1 else
                          'OUT_OF_RANGE' if dimension is None else 'IN_RANGE')
        if row['classification'] != classification:
            raise ValueError('classification disagrees with stored R')
        if dimension is None:
            if row['d_mm'] is not None:
                raise ValueError('OUT_OF_RANGE dimension must be null')
        elif not math.isclose(_number(row['d_mm'], 'd_mm'), dimension,
                              rel_tol=2e-12, abs_tol=2e-12):
            raise ValueError('dimension disagrees with independent inversion')
        family, parameter, _, _ = identity
        if family == 'chain' and count != pairs:
            raise ValueError('chain is not an exact total order')
        if family == 'antichain' and count != 0:
            raise ValueError('antichain contains related pairs')
        grouped.setdefault((family, parameter, n), []).append((r, dimension))
    if seen != set(expected):
        raise ValueError('frozen realizations are missing')

    # The engineering grid is descriptive: it cannot replace 24-cell t(29).
    cutoff = float(student_t.ppf(1 - .05 / (2 * 24), reps - 1))
    cells = []
    summaries = {}
    for (family, parameter, n), values in sorted(grouped.items()):
        fractions = [r for r, _ in values]
        dimensions = [d for _, d in values if d is not None]
        summary = dict(family=family, D_or_k=parameter, N=n,
                       realizations=len(values), expected_r=_reference(family, parameter, n))
        if family not in ('chain', 'antichain'):
            summary.update(_mean_test(fractions, summary['expected_r'], cutoff))
        else:
            summary.update(mean_r=fractions[0], se_r=0.0, t=None,
                           t_defined=False, t_unbounded=False, mean_test_pass=True)
        summary['mean_d_mm'] = fmean(dimensions) if dimensions else None
        summary['finite_d_mm_count'] = len(dimensions)
        summary['d_mm_of_mean_r'] = _dimension(summary['mean_r'])
        cells.append(summary)
        summaries[(family, parameter, n)] = summary
    discriminations = []
    for a, b in combinations((2, 3, 4), 2):
        left = summaries[('diamond', a, max(sizes))]
        right = summaries[('diamond', b, max(sizes))]
        gap = abs(left['mean_r'] - right['mean_r'])
        combined = math.hypot(left['se_r'], right['se_r'])
        discriminations.append(dict(dimensions=[a, b], N=max(sizes),
                                    mean_gap=gap, combined_se=combined,
                                    pass_check=gap > 6 * combined))
    gates = dict(G0_rows=True,
                 G1=all(c['mean_test_pass'] for c in cells if c['family'] == 'diamond'),
                 G2=all(c['pass_check'] for c in discriminations),
                 G3=all(c['mean_test_pass'] for c in cells
                        if c['family'] in ('two_layer', 'k_order')))
    conditional = all(gates.values())
    return dict(mode=mode, entropy=entropy, rows=len(rows),
                verdict=('ENGINEERING_ONLY' if mode == 'engineering' else
                         'PASS_CONDITIONAL_G0' if conditional else 'FAIL'),
                study_authorized=False, scientific_acceptance=False,
                upstream_g0_required=True,
                g0_scope='Stored counts only; order checks, point support and exact-commit tests need upstream certification.',
                gates=gates, cells=cells, discrimination=discriminations,
                cutoff=cutoff, df=reps - 1, bonferroni_cells=24,
                zero_variance_policy='Undefined t statistics, including exact mean/reference equality, fail the stochastic mean gate; failure alone does not prove a defect.',
                t_reference_caveat='Nominal 5% family-wise error is conditional on approximate t-reference assumptions, not finite-sample calibrated.',
                limitation=_LIMITATION)


def main(argv: list[str] | None = None) -> int:
    """Check a persisted CSV only; never generate orders, seeds or authorization."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--mode', choices=('engineering', 'full'), required=True)
    parser.add_argument('--entropy', required=True)
    args = parser.parse_args(argv)
    try:
        entropy = _decimal_integer(args.entropy)
        report = check_rows(read_rows_csv(args.input), args.mode, entropy)
    except (ValueError, OSError) as error:
        print(json.dumps(dict(verdict='INCOMPLETE', study_authorized=False,
                              error=f'{type(error).__name__}: {error}'),
                         allow_nan=False, sort_keys=True))
        return 2
    print(json.dumps(report, allow_nan=False, sort_keys=True))
    return 1 if report['verdict'] == 'FAIL' else 0


if __name__ == '__main__':
    raise SystemExit(main())
