"""Exact arithmetic/enumeration checks only; no seeds or generated study data."""
from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations
from math import comb, factorial

import pytest

from emergence_lab.causal_set_exact2 import (
    inversion_counts, ordering_fraction_mean, ordering_fraction_variance,
    related_pair_counts, related_pair_probabilities,
)


def test_small_manual_distributions():
    assert inversion_counts(2) == (1, 1)
    assert inversion_counts(3) == (1, 2, 2, 1)
    assert related_pair_probabilities(2) == (Fraction(1, 2), Fraction(1, 2))
    assert related_pair_probabilities(3) == (
        Fraction(1, 6), Fraction(1, 3), Fraction(1, 3), Fraction(1, 6))
    assert ordering_fraction_variance(2) == Fraction(1, 4)
    assert ordering_fraction_variance(3) == Fraction(11, 108)


@pytest.mark.parametrize('n', range(2, 8))
def test_recurrence_matches_independent_permutation_enumeration(n):
    # Count comparisons directly; do not use insertion recurrence or producer.
    observed = Counter()
    observed_related = Counter()
    for permutation in permutations(range(n)):
        inversions = sum(permutation[i] > permutation[j]
                         for i, j in combinations(range(n), 2))
        comparable = sum(permutation[i] < permutation[j]
                         for i, j in combinations(range(n), 2))
        observed[inversions] += 1
        observed_related[comparable] += 1
    expected = tuple(observed[k] for k in range(comb(n, 2) + 1))
    assert inversion_counts(n) == expected
    assert related_pair_counts(n) == tuple(observed_related[k] for k in range(comb(n, 2) + 1))


@pytest.mark.parametrize('n', [2, 3, 4, 7, 12, 24, 32])
def test_normalization_symmetry_and_exact_moments(n):
    counts = related_pair_counts(n)
    probabilities = related_pair_probabilities(n)
    pairs = comb(n, 2)
    assert len(counts) == pairs + 1
    assert all(type(weight) is int and weight > 0 for weight in counts)
    assert sum(counts) == factorial(n)
    assert counts == counts[::-1]
    assert counts[0] == counts[-1] == 1
    assert sum(probabilities) == 1
    mean = sum(Fraction(r, pairs) * probability
               for r, probability in enumerate(probabilities))
    variance = sum((Fraction(r, pairs) - mean) ** 2 * probability
                   for r, probability in enumerate(probabilities))
    assert mean == ordering_fraction_mean(n) == Fraction(1, 2)
    assert variance == ordering_fraction_variance(n)


def test_triple_covariances_by_six_rank_orders():
    triples = []
    for a, b, c in permutations(range(3)):
        triples.append((int(a > b), int(a > c), int(b > c)))
    def covariance(left, right):
        return sum(Fraction(row[left] * row[right], 6) for row in triples) - Fraction(1, 4)
    assert covariance(0, 1) == Fraction(1, 12)
    assert covariance(0, 2) == Fraction(-1, 12)
    assert covariance(1, 2) == Fraction(1, 12)


@pytest.mark.parametrize('n', [128, 256, 512, 1024, 10**12])
def test_closed_form_moments_do_not_build_distribution(n):
    assert ordering_fraction_mean(n) == Fraction(1, 2)
    assert ordering_fraction_variance(n) == Fraction(2 * n + 5, 18 * n * (n - 1))


@pytest.mark.parametrize('n', [None, True, False, 2.0, '2', -1, 0, 1])
@pytest.mark.parametrize('function', [inversion_counts, related_pair_counts,
                                     related_pair_probabilities,
                                     ordering_fraction_mean,
                                     ordering_fraction_variance])
def test_invalid_n_refused(function, n):
    with pytest.raises(ValueError, match='integer >= 2'):
        function(n)


@pytest.mark.parametrize('function', [inversion_counts, related_pair_counts,
                                     related_pair_probabilities])
def test_distribution_resource_cap(function):
    with pytest.raises(ValueError, match='N <= 32'):
        function(33)
