"""S1b v0.2 deterministic *design* decision reference. No random seeds or tree samples.

Use this only to check the preregistered logic before a later, reviewed run
implementation. The thresholds are engineering rules, not calibrated coverage
guarantees. CLI self-check: python docs/experiments/s1b_outcome_reference.py
"""
import math


def classify_ci(lower: float, upper: float, margin: float = 0.03) -> str:
    """Disjoint confidence-interval rules, with strict inequalities at margins."""
    if not all(math.isfinite(x) for x in (lower, upper, margin)):
        raise ValueError("nonfinite CI or margin")
    if margin <= 0 or lower > upper:
        raise ValueError("invalid CI or margin")
    if lower > margin:
        return "MATERIAL-POSITIVE"
    if upper < -margin:
        return "MATERIAL-NEGATIVE"
    if lower > -margin and upper < margin:
        return "EQUIVALENT"
    return "INCONCLUSIVE"


def classify_family(
    *,
    counts: tuple[int, ...],
    expected_trees: int,
    expected_sizes: int,
    controls_passed: bool,
    budget_ok: bool,
    certified: bool,
    headroom_ok: bool,
    annealed_q_positive: bool,
    ci: tuple[float, float],
    delta_se: float,
    jackknife_se: float,
    influence_skew: float,
    max_squared_share: float,
    margin: float = 0.03,
) -> str:
    """Family verdict. Completeness/STOP precede all statistical classes.

    Counts include *all* sizes of the family, including descriptive CAY 2^14.
    A family with no full sample is BLOCKED, not conditionally 'equivalent'.
    """
    if (not controls_passed or not budget_ok or expected_trees <= 0
            or expected_sizes <= 0 or len(counts) != expected_sizes
            or any(n != expected_trees for n in counts)):
        return "BLOCKED"
    if not certified or not headroom_ok or not annealed_q_positive:
        return "UNRELIABLE"
    vals = (delta_se, jackknife_se, influence_skew, max_squared_share)
    if (not all(math.isfinite(x) for x in vals) or delta_se <= 0
            or jackknife_se < 0 or abs(influence_skew) > 1.5
            or max_squared_share > 0.5 or max_squared_share < 0
            or jackknife_se > 1.25 * delta_se):
        return "UNRELIABLE"
    try:
        return classify_ci(*ci, margin=margin)
    except (ValueError, TypeError):
        return "UNRELIABLE"


if __name__ == "__main__":
    examples = [
        ((0.010, 0.020), "EQUIVALENT"),
        ((0.031, 0.050), "MATERIAL-POSITIVE"),
        ((-0.050, -0.031), "MATERIAL-NEGATIVE"),
        ((0.015, 0.045), "INCONCLUSIVE"),
        ((0.030, 0.050), "INCONCLUSIVE"),
        ((-0.030, 0.030), "INCONCLUSIVE"),
    ]
    for ci, expected in examples:
        actual = classify_ci(*ci)
        assert actual == expected, (ci, expected, actual)
    print("S1b v0.2 reference case checks passed (no seeds drawn)")
