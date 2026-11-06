"""Exact finite-N D=2 ordering-fraction reference, with no RNG or simulation.

For an ideal i.i.d. continuous uniform flat 2D diamond, sorting by one
light-cone coordinate makes the other coordinate's ranks a uniform permutation.
Related pairs R are the complement of its inversion count. The same law holds
for the intersection of two independent uniform linear orders.

These are model-level combinatorial facts, not new physics. They neither change
CS0 gates nor establish finite-sample t-reference coverage. Distribution tables
are capped at N=32; closed-form Fraction moments do not construct a table.
"""
from __future__ import annotations

from fractions import Fraction
from math import factorial


MAX_DISTRIBUTION_N = 32


def _validate_n(n: int, *, distribution: bool = False) -> None:
    if type(n) is not int or n < 2:
        raise ValueError('N must be an integer >= 2')
    if distribution and n > MAX_DISTRIBUTION_N:
        raise ValueError(f'exact distribution tables require N <= {MAX_DISTRIBUTION_N}')


def inversion_counts(n: int) -> tuple[int, ...]:
    """Return exact counts of permutations with I=0,...,C(N,2) inversions.

    Inserting the new largest element creates j=0,...,m-1 inversions, so
    M(m,k)=sum(M(m-1,k-j),j=0,...,m-1). A sliding integer window computes
    this recurrence in O(N**3) integer operations and O(N**2) stored integers.
    The tuple is immutable, and no shared mutable cache is retained.
    """
    _validate_n(n, distribution=True)
    counts = [1]
    for m in range(2, n + 1):
        updated = []
        window = 0
        for k in range(m * (m - 1) // 2 + 1):
            if k < len(counts):
                window += counts[k]
            if 0 <= k - m < len(counts):
                window -= counts[k - m]
            updated.append(window)
        counts = updated
    return tuple(counts)


def related_pair_counts(n: int) -> tuple[int, ...]:
    """Integer weights for R=0,...,C(N,2), with common denominator N!.

    R=C(N,2)-I, so weights reverse the inversion distribution. Their symmetry
    is a mathematical consequence, not an assumption used by the recurrence.
    """
    return inversion_counts(n)[::-1]


def related_pair_probabilities(n: int) -> tuple[Fraction, ...]:
    """Exact probabilities P(R=k), k=0,...,C(N,2), as rational numbers."""
    counts = related_pair_counts(n)
    denominator = factorial(n)
    return tuple(Fraction(weight, denominator) for weight in counts)


def ordering_fraction_mean(n: int) -> Fraction:
    """E[R/C(N,2)] = 1/2 under the ideal uniform-permutation model."""
    _validate_n(n)
    return Fraction(1, 2)


def ordering_fraction_variance(n: int) -> Fraction:
    """Var(R/C(N,2)) = (2N+5)/(18N(N-1)), exact for every N>=2."""
    _validate_n(n)
    return Fraction(2 * n + 5, 18 * n * (n - 1))
