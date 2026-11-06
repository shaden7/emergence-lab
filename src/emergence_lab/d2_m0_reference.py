"""D2-M0 deterministic finite-occupancy reference; no RNG or CS0 acceptance.

The frozen protocol is docs/CS0_D2_M0_PROTOCOL.md. Importing this module does
not evaluate the curve. ``generate_reference`` is the explicit full evaluation;
``compute_cell`` permits small engineering fixtures. Resource/provenance limits
belong to the separately reviewed caller, not this pure computation module.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction
import io
import json
import math
import platform
import time

import numpy
import scipy

from emergence_lab.causal_set_exact2 import (
    ordering_fraction_variance, related_pair_counts,
)
from emergence_lab.causal_set_mm import myrheim_meyer_dimension as _binary64_dimension


SIZES = tuple(range(2, 33))
WEIGHTED_CHECK_SIZES = (2, 3, 4, 8)
PROBE_FRACTIONS = (Fraction(1), Fraction(1, 2), Fraction(1, 3),
                   Fraction(2, 3), Fraction(1, 496), Fraction(495, 496))
ABSOLUTE_TOLERANCE = 1e-10
CSV_FIELDS = (
    'N', 'pairs', 'total_weight', 'positive_weight', 'excluded_mass',
    'chain_probability', 'conditioning_probability', 'mean_r',
    'mean_r_positive', 'variance_r', 'dimension_of_mean_r',
    'dimension_of_positive_mean_r', 'dimension_of_positive_mean_r_hp',
    'mean_finite_dimension', 'mean_finite_dimension_hp', 'nonlinear_gap',
    'unconditioned_mean_dimension', 'checks_passed', 'error',
)


class NumericalControlError(ValueError):
    """A reference control cannot be evaluated consistently; never a CS0 PASS."""

    def __init__(self, message, *, weights=None, exact_controls=None):
        super().__init__(message)
        self.weights = weights
        self.exact_controls = {} if exact_controls is None else exact_controls


class ReferenceDependencyError(RuntimeError):
    """Missing reference assets are setup failures, not numerical findings."""


def protocol_config() -> dict:
    """Return the frozen design without evaluating any occupancy or inverse."""
    return dict(diagnostic='D2-M0', sizes=list(SIZES), ambient_dimension=2,
                mandatory_interval_endpoints=False, conditioned_on='R > 0',
                weighted_check_sizes=list(WEIGHTED_CHECK_SIZES),
                probe_fractions=[_rational(r) for r in PROBE_FRACTIONS],
                independent_decimal_digits=80, retained_significant_digits=75,
                inverse_bracket=[1, 10], bisection_width='1e-65',
                absolute_tolerance=ABSOLUTE_TOLERANCE,
                stochastic=False, cs0_acceptance=False)


def _rational(value: Fraction) -> dict:
    return dict(numerator=value.numerator, denominator=value.denominator)


def _mp_module():
    try:
        import mpmath
    except ImportError as error:
        raise ReferenceDependencyError('D2-M0 requires mpmath; install the reviewed '
                                       'reference dependency before evaluation') from error
    return mpmath


def _mp_context():
    context = _mp_module().mp.clone()
    context.dps = 80
    return context


def _numeric_exceptions():
    # Resolve the optional dependency outside the solver try/except. In mpmath
    # 1.3.0 NoConvergence derives directly from Exception, not ArithmeticError.
    _mp_module()
    from mpmath.libmp.libhyper import NoConvergence
    return (ValueError, RuntimeError, ArithmeticError, NoConvergence)


def _as_mp(context, value: Fraction):
    # Never round an exact rational through binary64 before high precision.
    return context.mpf(value.numerator) / context.mpf(value.denominator)


def _decimal(context, value) -> str:
    # Width 1e-65 is the stopping condition; 75 printed digits are retained
    # representation, not a claim that all printed digits are certified.
    return context.nstr(value, 75, strip_zeros=False)


def independent_dimension(r: Fraction) -> str:
    """Independent 80-digit direct-gamma inverse, returned as 75-digit text.

    Only the protocol bracket [1,10] is supported. Exact endpoint r=1 is
    handled analytically; r=0 has no finite estimate and is refused.
    """
    if type(r) is not Fraction or not 0 < r <= 1:
        raise ValueError('independent inverse requires an exact Fraction in (0,1]')
    context = _mp_context()
    if r == 1:
        return _decimal(context, context.mpf(1))
    target = _as_mp(context, r)
    low, high = context.mpf(1), context.mpf(10)
    def fraction(d):
        return (context.gamma(d + 1) * context.gamma(d / 2)
                / (2 * context.gamma(3 * d / 2)))
    if target < fraction(high):
        raise ValueError('fraction is outside the frozen [1,10] inverse bracket')
    width = context.mpf('1e-65')
    while high - low > width:
        middle = (low + high) / 2
        if fraction(middle) > target:
            low = middle
        else:
            high = middle
    return _decimal(context, (low + high) / 2)


def _hp(r: Fraction, cache: dict[Fraction, str]) -> str:
    if r not in cache:
        cache[r] = independent_dimension(r)
    return cache[r]


def _comparison(name: str, observed: float, independent: str) -> dict:
    context = _mp_context()
    if not math.isfinite(observed):
        raise NumericalControlError(f'{name}: nonfinite binary64 estimate')
    error = abs(context.mpf(observed) - context.mpf(independent))
    return dict(name=name, passed=bool(error <= context.mpf('1e-10')),
                binary64=observed, independent_hp=independent,
                absolute_error=_decimal(context, error),
                tolerance=ABSOLUTE_TOLERANCE)


def _cell_numerics(n, weights, pairs, positive_weight, mean, positive_mean, cache):
    estimates = [_binary64_dimension(float(Fraction(r, pairs)))
                 for r in range(1, pairs + 1)]
    if any(not math.isfinite(d) for d in estimates):
        raise NumericalControlError(f'N={n}: positive fraction was not finitely inverted')
    mean_dimension = math.fsum(w / positive_weight * d
                               for w, d in zip(weights[1:], estimates))
    dimension_mean = _binary64_dimension(float(mean))
    dimension_positive_mean = _binary64_dimension(float(positive_mean))
    if not all(math.isfinite(value) for value in
               (mean_dimension, dimension_mean, dimension_positive_mean)):
        raise NumericalControlError(f'N={n}: nonfinite dimension summary')
    positive_mean_hp = _hp(positive_mean, cache)
    checks = [
        _comparison(f'N={n}:d(E[r])=2', dimension_mean, '2'),
        _comparison(f'N={n}:conditioned-mean inverse',
                    dimension_positive_mean, positive_mean_hp),
    ]
    weighted_hp = None
    if n in WEIGHTED_CHECK_SIZES:
        context = _mp_context()
        weighted = context.fsum(
            _as_mp(context, Fraction(w, positive_weight))
            * context.mpf(_hp(Fraction(r, pairs), cache))
            for r, w in enumerate(weights) if r > 0)
        weighted_hp = _decimal(context, weighted)
        checks.append(_comparison(f'N={n}:weighted finite dimension',
                                  mean_dimension, weighted_hp))
    values = dict(dimension_of_mean_r=dimension_mean,
                  dimension_of_positive_mean_r=dimension_positive_mean,
                  dimension_of_positive_mean_r_hp=positive_mean_hp,
                  mean_finite_dimension=mean_dimension,
                  mean_finite_dimension_hp=weighted_hp,
                  nonlinear_gap=mean_dimension - dimension_positive_mean,
                  unconditioned_mean_dimension=None)
    return values, checks


def compute_cell(n: int, *, _hp_cache: dict[Fraction, str] | None = None) -> dict:
    """Evaluate one occupancy, preserving its exact weights and excluded mass.

    Unit engineering fixtures use N=2,3. Full target evaluation must wait for
    the protocol's reviewed/merged state and an explicitly authorized caller.
    """
    weights = related_pair_counts(n)  # Also enforces strict N and N<=32.
    pairs = math.comb(n, 2)
    denominator = math.factorial(n)
    weights_record = dict(N=n, denominator=denominator, counts=list(weights))
    if (len(weights) != pairs + 1
            or any(type(w) is not int or w <= 0 for w in weights)):
        raise NumericalControlError(f'N={n}: invalid integer distribution support',
                                    weights=weights_record)
    positive_weight = sum(weights[1:])
    mean = sum((Fraction(r * w, pairs * denominator)
                for r, w in enumerate(weights)), Fraction())
    variance = sum((Fraction(w, denominator) * (Fraction(r, pairs) - mean) ** 2
                    for r, w in enumerate(weights)), Fraction())
    positive_mean = Fraction(sum(r * w for r, w in enumerate(weights)),
                             pairs * positive_weight)
    exact_controls = dict(
        normalization=sum(weights) == denominator,
        symmetry=weights == weights[::-1],
        endpoint_weights=weights[0] == weights[-1] == 1,
        excluded_mass=Fraction(weights[0], denominator) == Fraction(1, denominator),
        chain_mass=Fraction(weights[-1], denominator) == Fraction(1, denominator),
        mean=mean == Fraction(1, 2),
        positive_mean=positive_mean == Fraction(denominator, 2 * (denominator - 1)),
        variance=variance == ordering_fraction_variance(n),
    )
    if not all(exact_controls.values()):
        raise NumericalControlError(f'N={n}: failed exact controls {exact_controls}',
                                    weights=weights_record, exact_controls=exact_controls)
    cache = {} if _hp_cache is None else _hp_cache
    numeric_errors = _numeric_exceptions()
    try:
        values, checks = _cell_numerics(n, weights, pairs, positive_weight,
                                       mean, positive_mean, cache)
    except ReferenceDependencyError:
        raise
    except NumericalControlError as error:
        error.weights = weights_record
        error.exact_controls = exact_controls
        raise
    except numeric_errors as error:
        raise NumericalControlError(f'N={n}: {type(error).__name__}: {error}',
                                    weights=weights_record,
                                    exact_controls=exact_controls) from error
    if n == 2:
        exact_controls['n2_conditioned_dimensions'] = (
            values['dimension_of_positive_mean_r'] == values['mean_finite_dimension'] == 1.0)
    cell = dict(N=n, pairs=pairs, total_weight=denominator,
                positive_weight=positive_weight,
                excluded_mass=_rational(Fraction(weights[0], denominator)),
                chain_probability=_rational(Fraction(weights[-1], denominator)),
                conditioning_probability=_rational(Fraction(positive_weight, denominator)),
                mean_r=_rational(mean), mean_r_positive=_rational(positive_mean),
                variance_r=_rational(variance), **values,
                checks_passed=all(exact_controls.values()) and all(c['passed'] for c in checks))
    return dict(cell=cell, exact_controls=exact_controls, numeric_checks=checks,
                weights=weights_record)


def _probe_check(r: Fraction, cache: dict[Fraction, str]) -> dict:
    numeric_errors = _numeric_exceptions()
    try:
        check = _comparison(f'probe r={r}', _binary64_dimension(float(r)), _hp(r, cache))
    except ReferenceDependencyError:
        raise
    except numeric_errors as error:
        check = dict(name=f'probe r={r}', passed=False,
                     error=f'{type(error).__name__}: {error}')
    check['fraction'] = _rational(r)
    return check


def generate_reference() -> dict:
    """Explicitly evaluate the entire frozen target; never called on import."""
    mpmath = _mp_module()
    started = time.process_time()
    cache: dict[Fraction, str] = {}
    parts = []
    for n in SIZES:
        try:
            parts.append(compute_cell(n, _hp_cache=cache))
        except NumericalControlError as error:
            # Keep the occupancy in the complete table; never selectively drop it.
            parts.append(dict(cell=dict(N=n, checks_passed=False, error=str(error)),
                              exact_controls=error.exact_controls,
                              numeric_checks=[], weights=error.weights))
    probe_checks = [_probe_check(r, cache) for r in PROBE_FRACTIONS]
    passed = (tuple(part['cell']['N'] for part in parts) == SIZES
              and all(part['cell']['checks_passed'] for part in parts)
              and all(check['passed'] for check in probe_checks))
    return dict(schema=1, diagnostic='D2-M0', config=protocol_config(),
                outcome='REFERENCE_COMPLETE' if passed else 'NUMERICAL_CHECK_FAILED',
                cs0_acceptance=False, stochastic=False,
                cells=[part['cell'] for part in parts],
                exact_controls=[dict(N=part['cell']['N'], checks=part['exact_controls'])
                                for part in parts],
                numeric_checks=[check for part in parts for check in part['numeric_checks']],
                probe_checks=probe_checks,
                exact_weights=[part['weights'] for part in parts],
                versions=dict(python=platform.python_version(), numpy=numpy.__version__,
                              scipy=scipy.__version__, mpmath=mpmath.__version__),
                compute_cpu_seconds=time.process_time() - started,
                unconditioned_mean_dimension_status='UNDEFINED: positive mass at R=0',
                limitation='Fixed input D=2 and no mandatory endpoints; estimator-control calculation, not physical dimensional reduction.')


def reference_csv(record: dict) -> str:
    """Serialize an already-computed result; never reevaluate the target."""
    table = io.StringIO(newline='')
    writer = csv.DictWriter(table, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for cell in record['cells']:
        row = {}
        for name in CSV_FIELDS:
            value = cell.get(name)
            if isinstance(value, dict) and set(value) == {'numerator', 'denominator'}:
                value = str(Fraction(value['numerator'], value['denominator']))
            row[name] = value
        writer.writerow(row)
    return table.getvalue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--format', choices=('json', 'csv'), default='json')
    args = parser.parse_args(argv)
    try:
        record = generate_reference()
    except Exception as error:
        print(json.dumps(dict(outcome='INCOMPLETE', cs0_acceptance=False,
                              error=f'{type(error).__name__}: {error}'), allow_nan=False))
        return 2
    if args.format == 'csv':
        print(reference_csv(record), end='')
    else:
        print(json.dumps(record, allow_nan=False, sort_keys=True))
    return 0 if record['outcome'] == 'REFERENCE_COMPLETE' else 1


if __name__ == '__main__':
    raise SystemExit(main())
