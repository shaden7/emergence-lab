"""Independent spot-check of the archived D2-M0 curve (2026-11-07 run).

Does not import emergence_lab. Recounts Mahonian weights by brute-force
enumeration of permutations (N <= 8), inverts the Myrheim-Meyer ordering
fraction r(d) = Gamma(d+1) Gamma(d/2) / (2 Gamma(3d/2)) with mpmath bisection,
and compares E[d|R>0] and d(E[r|R>0]) to the archived curve.csv.

Usage: python -I docs/experiments/d2_m0_recheck.py docs/experiments/d2-m0-run-20261107/curve.csv
Requires mpmath. Agreement is a numerical cross-check, not a proof.
"""
import csv
import itertools
import sys

import mpmath as mp

mp.mp.dps = 50


def r_of_d(d):
    return mp.gamma(d + 1) * mp.gamma(d / 2) / (2 * mp.gamma(3 * d / 2))


def d_of_r(r):
    if r == 1:
        return mp.mpf(1)
    return mp.findroot(lambda d: r_of_d(d) - r, (1, 10), solver="bisect")


def main(path):
    rows = {int(r["N"]): r for r in csv.DictReader(open(path))}
    worst = 0.0
    for n in range(2, 9):
        c = n * (n - 1) // 2
        w = [0] * (c + 1)
        for p in itertools.permutations(range(n)):
            w[sum(1 for i in range(n) for j in range(i + 1, n) if p[i] < p[j])] += 1
        pos = sum(w[1:])
        ed = sum(w[k] * d_of_r(mp.mpf(k) / c) for k in range(1, c + 1)) / pos
        er = sum(w[k] * mp.mpf(k) / c for k in range(1, c + 1)) / pos
        e1 = abs(float(ed) - float(rows[n]["mean_finite_dimension"]))
        e2 = abs(float(d_of_r(er)) - float(rows[n]["dimension_of_positive_mean_r"]))
        worst = max(worst, e1, e2)
        print(n, mp.nstr(ed, 15), mp.nstr(d_of_r(er), 15), f"{e1:.2e}", f"{e2:.2e}")
    print("max_abs_discrepancy", worst)
    return 0 if worst <= 1e-10 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
