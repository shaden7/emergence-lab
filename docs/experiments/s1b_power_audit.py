"""S1b v0.2 no-seed, plug-in power audit: python docs/experiments/s1b_power_audit.py

Pilot W=128..1024 tree-level SEs from docs/experiments/2026-10-17-s1-pilot.md.
Uses fixed-variance normal sampling with symmetric 90%-t CIs (df=2n-2),
not exact Welch/TOST power. These are *conditional design diagnostics*, not
new tree observations, validated CI coverage or physical conclusions.
"""
from math import sqrt
from scipy.stats import norm, t

MARGIN = 0.03
PILOT_N = 8
DESIGNS = {"CAY": (24, 0.028861), "UST": (48, 0.042157)}


def audit(n: int, pilot_se: float) -> dict:
    se = pilot_se * sqrt(PILOT_N / n)
    half_width = float(t.ppf(0.95, 2 * n - 2) * se)
    allowance = max(0.0, MARGIN - half_width)
    p_equiv_zero = float(2 * norm.cdf(allowance / se) - 1)
    # Strict containment of a 90% two-sided CI in +-MARGIN.
    def p_equiv(effect):
        if half_width >= MARGIN:
            return 0.0
        a = (-MARGIN + half_width - effect) / se
        b = (MARGIN - half_width - effect) / se
        return float(norm.cdf(b) - norm.cdf(a))
    # Lower 90%-CI endpoint above the *material* positive margin.
    def p_material(effect):
        return float(norm.sf((MARGIN + half_width - effect) / se))
    # v0.1's sign-only rule (for audit comparison, NOT the v0.2 verdict).
    def p_sign(effect):
        return float(norm.sf((half_width - effect) / se))
    n80_approx = (pilot_se * sqrt(PILOT_N)
                  * (norm.ppf(0.95) + norm.ppf(0.90)) / MARGIN) ** 2
    return {"se": se, "half_width": half_width,
            "p_equiv_zero": p_equiv_zero, "p_equiv_002": p_equiv(0.02),
            "p_material_000": p_material(0.0),
            "p_material_0035": p_material(0.035),
            "p_material_007": p_material(0.07),
            "p_old_sign_002": p_sign(0.02), "n80_approx": n80_approx}


def main() -> None:
    outcomes = {}
    for name, (n, pilot_se) in DESIGNS.items():
        x = audit(n, pilot_se)
        outcomes[name] = x
        print(f"{name} n={n}: SE={x['se']:.5f} 90%-CI halfwidth={x['half_width']:.5f}, "
              f"P(equivalent|D=0)={x['p_equiv_zero']:.2%} "
              f"P(material +|D=.07)={x['p_material_007']:.2%} "
              f"P(material +|D=.035)={x['p_material_0035']:.2%} "
              f"P(material +|D=0)={x['p_material_000']:.3%}, "
              f"approx trees/size for 80%-power equivalence={x['n80_approx']:.1f}")
    joint = outcomes["CAY"]["p_equiv_zero"] * outcomes["UST"]["p_equiv_zero"]
    print(f"P(both equivalent | both true D=0, independent)={joint:.3%}")
    assert joint < 0.01
    assert 0.70 < outcomes["CAY"]["p_material_007"] < 0.80
    assert outcomes["CAY"]["p_material_0035"] < 0.10
    assert outcomes["CAY"]["p_material_000"] < 0.001
    assert outcomes["CAY"]["p_old_sign_002"] > 0.25
    assert 0.09 < outcomes["CAY"]["p_equiv_zero"] < 0.11


if __name__ == "__main__":
    main()
