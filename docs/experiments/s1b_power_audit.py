"""No-seed plug-in power audit for S1b v0.1. Run: python docs/experiments/s1b_power_audit.py

Pilot W=128..1024 tree-level delta-method SEs from docs/experiments/
2026-10-17-s1-pilot.md; no pilot data are re-sampled or simulated here.
Normal fixed-SE and symmetric-t-df approximation, NOT exact TOST power,
and optimistic under unequal Welch df, variance uncertainty or heavy tails.
"""
from math import sqrt
from scipy.stats import norm, t

MARGIN = 0.03
PILOT_N = 8
DESIGNS = {
    "CAY": (24, 0.028861),
    "UST": (48, 0.042157),
}


def audit(n: int, pilot_se: float) -> dict:
    se = pilot_se * sqrt(PILOT_N / n)
    half_width = float(t.ppf(0.95, 2 * n - 2) * se)
    allowable_center = max(0.0, MARGIN - half_width)
    p_equiv_zero = float(2 * norm.cdf(allowable_center / se) - 1)
    p_positive_if_002 = float(norm.cdf((0.02 - half_width) / se))
    p_positive_if_007 = float(norm.cdf((0.07 - half_width) / se))
    n80_approx = (pilot_se * sqrt(PILOT_N) *
                  (norm.ppf(0.95) + norm.ppf(0.90)) / MARGIN) ** 2
    return {"se": se, "half_width": half_width, "p_equiv_zero": p_equiv_zero,
            "p_positive_if_002": p_positive_if_002,
            "p_positive_if_007": p_positive_if_007, "n80_approx": n80_approx}


def main() -> None:
    result = {}
    for name, (n, pilot_se) in DESIGNS.items():
        x = audit(n, pilot_se)
        result[name] = x
        print(f"{name}: n={n}, SE={x['se']:.5f}, "
              f"90% CI half-width={x['half_width']:.5f}, "
              f"P(equivalent|D=0)={x['p_equiv_zero']:.2%}, "
              f"P(CI>0|D=.02)={x['p_positive_if_002']:.2%}, "
              f"P(CI>0|D=.07)={x['p_positive_if_007']:.2%}, "
              f"approx n per size for 80% equivalence={x['n80_approx']:.1f}")
    joint = result["CAY"]["p_equiv_zero"] * result["UST"]["p_equiv_zero"]
    print(f"P(both equivalent|both true D=0, independent seeds)={joint:.3%}")
    assert joint < 0.01
    assert result["CAY"]["p_positive_if_002"] > 0.25
    # v0.1 logic overlaps: [0.01, 0.02] is both positive and within +/-0.03.
    assert 0.01 > 0 and -MARGIN < 0.01 < 0.02 < MARGIN


if __name__ == "__main__":
    main()
