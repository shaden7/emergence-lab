"""Small N=2,3 engineering fixtures only; no frozen target-grid evaluation."""
import builtins
import csv
from fractions import Fraction
import io
import json

import mpmath
from mpmath.libmp.libhyper import NoConvergence
import pytest

from emergence_lab import d2_m0_reference as reference


def test_frozen_config_does_not_evaluate(monkeypatch):
    monkeypatch.setattr(reference, 'compute_cell', lambda n: pytest.fail('must not evaluate'))
    config = reference.protocol_config()
    assert config['sizes'] == list(range(2, 33))
    assert config['weighted_check_sizes'] == [2, 3, 4, 8]
    assert config['independent_decimal_digits'] == 80
    assert config['retained_significant_digits'] >= 70
    assert config['bisection_width'] == '1e-65'
    config['sizes'].clear()
    assert reference.protocol_config()['sizes'] == list(range(2, 33))


def test_independent_inverse_endpoints_and_known_reference():
    before = mpmath.mp.dps
    context = mpmath.mp.clone()
    context.dps = 80
    one = reference.independent_dimension(Fraction(1))
    two = reference.independent_dimension(Fraction(1, 2))
    assert context.mpf(one) == 1
    assert abs(context.mpf(two) - 2) < context.mpf('1e-65')
    assert len(one.replace('.', '')) >= 70
    assert len(two.replace('.', '')) >= 70
    assert mpmath.mp.dps == before


@pytest.mark.parametrize('value', [Fraction(0), Fraction(-1), Fraction(2), .5, '1/2', True])
def test_independent_inverse_refuses_nonfraction_or_outside_domain(value):
    with pytest.raises(ValueError):
        reference.independent_dimension(value)


def test_independent_inverse_refuses_outside_frozen_bracket():
    with pytest.raises(ValueError, match='bracket'):
        reference.independent_dimension(Fraction(1, 10000))


def test_high_precision_fraction_is_not_binary64_rounded():
    # This is a single helper probe, not evaluation of an occupancy curve.
    # Binary64 loses the positive offset, while the independent path must not.
    context = mpmath.mp.clone()
    context.dps = 80
    fraction = Fraction(1, 2) + Fraction(1, 10**40)
    assert float(fraction) == .5
    result = context.mpf(reference.independent_dimension(fraction))
    assert result < 2
    assert context.mpf('1e-41') < 2 - result < context.mpf('1e-38')


def test_n2_analytic_endpoint_and_excluded_mass():
    part = reference.compute_cell(2)
    cell = part['cell']
    assert part['weights'] == dict(N=2, denominator=2, counts=[1, 1])
    assert all(part['exact_controls'].values())
    assert all(check['passed'] for check in part['numeric_checks'])
    assert cell['excluded_mass'] == dict(numerator=1, denominator=2)
    assert cell['conditioning_probability'] == dict(numerator=1, denominator=2)
    assert cell['mean_r'] == dict(numerator=1, denominator=2)
    assert cell['mean_r_positive'] == dict(numerator=1, denominator=1)
    assert cell['variance_r'] == dict(numerator=1, denominator=4)
    assert cell['dimension_of_mean_r'] == pytest.approx(2, abs=1e-12)
    assert cell['dimension_of_positive_mean_r'] == cell['mean_finite_dimension'] == 1
    assert cell['nonlinear_gap'] == 0
    assert cell['unconditioned_mean_dimension'] is None
    assert 'outcome' not in part  # A small fixture cannot certify the full curve.
    json.dumps(part, allow_nan=False)


def test_n3_exact_probabilities_and_independent_weighted_check():
    part = reference.compute_cell(3)
    cell = part['cell']
    assert part['weights'] == dict(N=3, denominator=6, counts=[1, 2, 2, 1])
    assert cell['positive_weight'] == 5
    assert cell['excluded_mass'] == cell['chain_probability'] == dict(numerator=1, denominator=6)
    assert cell['mean_r_positive'] == dict(numerator=3, denominator=5)
    assert cell['variance_r'] == dict(numerator=11, denominator=108)
    assert all(part['exact_controls'].values()) and cell['checks_passed']
    assert len(part['numeric_checks']) == 3
    assert all(check['passed'] for check in part['numeric_checks'])
    context = mpmath.mp.clone()
    context.dps = 80
    assert context.mpf(cell['dimension_of_positive_mean_r_hp']) < 2
    assert abs(context.mpf(cell['mean_finite_dimension_hp'])
               - context.mpf(cell['mean_finite_dimension'])) < context.mpf('1e-10')


def test_exact_control_defect_is_not_silently_accepted(monkeypatch):
    monkeypatch.setattr(reference, 'related_pair_counts', lambda n: (1, 2))
    with pytest.raises(reference.NumericalControlError, match='exact controls'):
        reference.compute_cell(2)


def test_malformed_distribution_keeps_exact_input_weights(monkeypatch):
    monkeypatch.setattr(reference, 'related_pair_counts', lambda n: (1,))
    with pytest.raises(reference.NumericalControlError, match='support') as caught:
        reference.compute_cell(2)
    assert caught.value.weights == dict(N=2, denominator=2, counts=[1])
    assert caught.value.exact_controls == {}


@pytest.mark.parametrize('error_type', [ValueError, RuntimeError, ArithmeticError, NoConvergence])
@pytest.mark.parametrize('solver', ['_binary64_dimension', 'independent_dimension'])
def test_known_numeric_solver_exceptions_keep_weights_and_controls(monkeypatch, error_type, solver):
    def failing(*args):
        raise error_type('manufactured solver failure')
    monkeypatch.setattr(reference, solver, failing)
    with pytest.raises(reference.NumericalControlError, match='manufactured solver') as caught:
        reference.compute_cell(2)
    assert caught.value.weights == dict(N=2, denominator=2, counts=[1, 1])
    assert all(caught.value.exact_controls.values())
    assert type(caught.value.__cause__) is error_type


@pytest.mark.parametrize('error_type', [ValueError, RuntimeError, ArithmeticError, NoConvergence])
@pytest.mark.parametrize('solver', ['_binary64_dimension', 'independent_dimension'])
def test_probe_solver_exceptions_are_retained_numeric_failures(monkeypatch, error_type, solver):
    def failing(*args):
        raise error_type('manufactured solver failure')
    monkeypatch.setattr(reference, solver, failing)
    check = reference._probe_check(Fraction(1), {})
    assert check['passed'] is False
    assert check['fraction'] == dict(numerator=1, denominator=1)
    assert error_type.__name__ in check['error']
    json.dumps(check, allow_nan=False)


@pytest.mark.parametrize('method', ['cell', 'probe'])
def test_memory_error_remains_a_resource_stop(monkeypatch, method):
    def failing(*args):
        raise MemoryError('manufactured resource exhaustion')
    monkeypatch.setattr(reference, '_binary64_dimension', failing)
    with pytest.raises(MemoryError):
        if method == 'cell':
            reference.compute_cell(2)
        else:
            reference._probe_check(Fraction(1), {})


@pytest.mark.parametrize('method', ['cell', 'probe'])
def test_missing_dependency_remains_a_setup_failure(monkeypatch, method):
    def missing():
        raise reference.ReferenceDependencyError('manufactured missing dependency')
    monkeypatch.setattr(reference, '_mp_module', missing)
    with pytest.raises(reference.ReferenceDependencyError):
        if method == 'cell':
            reference.compute_cell(2)
        else:
            reference._probe_check(Fraction(1), {})


def test_nonfinite_positive_inverse_is_rejected(monkeypatch):
    monkeypatch.setattr(reference, '_binary64_dimension', lambda r: float('nan'))
    with pytest.raises(reference.NumericalControlError, match='finitely inverted') as caught:
        reference.compute_cell(2)
    assert caught.value.weights == dict(N=2, denominator=2, counts=[1, 1])
    assert all(caught.value.exact_controls.values())


def test_numeric_disagreement_stays_failed():
    check = reference._comparison('manufactured wrong inverse', 2.1, '2')
    assert check['passed'] is False
    assert check['tolerance'] == 1e-10


def test_nonfinite_probe_is_a_retained_numeric_failure(monkeypatch):
    monkeypatch.setattr(reference, '_binary64_dimension', lambda r: float('nan'))
    check = reference._probe_check(Fraction(1), {})
    assert check['passed'] is False
    assert check['fraction'] == dict(numerator=1, denominator=1)
    assert 'nonfinite' in check['error']
    json.dumps(check, allow_nan=False)


def test_csv_serializes_existing_cells_without_evaluation(monkeypatch):
    cell = reference.compute_cell(2)['cell']
    monkeypatch.setattr(reference, 'generate_reference', lambda: pytest.fail('must not reevaluate'))
    table = reference.reference_csv(dict(cells=[cell]))
    rows = list(csv.DictReader(io.StringIO(table)))
    assert len(rows) == 1 and rows[0]['N'] == '2'
    assert rows[0]['excluded_mass'] == '1/2'
    assert rows[0]['mean_r_positive'] == '1'
    assert rows[0]['unconditioned_mean_dimension'] == ''
    assert len(rows[0]['dimension_of_positive_mean_r_hp'].replace('.', '')) >= 70


def test_missing_optional_dependency_has_actionable_error(monkeypatch):
    original = builtins.__import__
    def refusing(name, *args, **kwargs):
        if name == 'mpmath':
            raise ImportError('fixture unavailable')
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', refusing)
    with pytest.raises(RuntimeError, match='requires mpmath'):
        reference.independent_dimension(Fraction(1, 2))
