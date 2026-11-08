"""Independent exact D2 endpoint-law check; no MM inversion or study run.
Run: python3 -I docs/experiments/d2_e0_exact_recheck.py
Uses coordinate-order pair counting for every permutation at m<=7,
then an independent insertion convolution for exact moments through N=32.
"""
from collections import Counter
from fractions import Fraction
from itertools import permutations
from math import factorial
import json
import platform
import time

def coordinate_counts(m):
    counts = Counter()
    for order in permutations(range(1, m + 1)):
        points = [(0, 0)] + list(enumerate(order, 1)) + [(m + 1, m + 1)]
        related = sum(x < u and y < v for x, y in points for u, v in points)
        counts[related] += 1
    return counts

def insertion_weights(m):
    weights = [1]
    for size in range(1, m + 1):
        new = [0] * (len(weights) + size - 1)
        for inversion, weight in enumerate(weights):
            for added in range(size):
                new[inversion + added] += weight
        weights = new
    return weights

def check():
    start = time.process_time()
    enumerated = 0
    for n in range(2, 33):
        m, c = n - 2, n * (n - 1) // 2
        weights = insertion_weights(m)
        law = {2 * n - 3 + k: w for k, w in enumerate(weights)}
        if m <= 7:
            actual = coordinate_counts(m)
            assert actual == law, (n, actual, law)
            enumerated += sum(actual.values())
        total = sum(law.values())
        mean = sum(Fraction(r * w, c) for r, w in law.items()) / total
        variance = sum(w * (Fraction(r, c) - mean) ** 2 for r, w in law.items()) / total
        assert total == factorial(m)
        assert weights == weights[::-1]
        assert min(law) == 2 * n - 3 and max(law) == c
        assert 0 not in law and all(w > 0 for w in weights)
        assert mean == Fraction(n*n + 3*n - 6, 2*n*(n-1))
        assert variance == Fraction(m*(m-1)*(2*m+5), 72*c*c)
        assert mean > Fraction(1, 2)
        if n <= 3:
            assert law == {c: 1} and mean == 1 and variance == 0
    # Explicit N=4 counterexample: endpoint counts 5 or 6, each probability 1/2.
    assert coordinate_counts(2) == {5: 1, 6: 1}
    return dict(outcome="EXACT_CONTROLS_PASS", sizes_checked=31,
                enumerated_permutations=enumerated, enumeration_N=[2, 9],
                python=platform.python_version(), cpu_seconds=time.process_time()-start,
                mm_curve_executed=False, scientific_acceptance=False)

if __name__ == "__main__":
    print(json.dumps(check(), sort_keys=True, indent=2))
