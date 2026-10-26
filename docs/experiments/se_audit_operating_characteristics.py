"""SE-audit v0.1 operating characteristics (no project seeds, no tree data).

    python docs/experiments/se_audit_operating_characteristics.py

Part 1 is analytic: in the linear (delta) approximation the batch estimate is
the mean of 12 i.i.d. tree influences, so R^2 = MS_between / MS_within is the
one-way ANOVA F statistic with (B-1, B(m-1)) = (15, 176) df.
Part 2 is a synthetic Monte Carlo: per-tree annealed returns Q_i(lo), Q_i(hi)
are drawn from correlated lognormal or log-t laws, NOT from trees. It checks
the size of the F-referenced rule for the *nonlinear* annealed slope and shows
how the design responds to heavy tails. The synthetic seed 2036101991 is used
only here and is disjoint from every graph/bootstrap seed base in the repo.
These are design diagnostics, not observations and not coverage guarantees.
"""
from math import log, sqrt

import numpy as np
from scipy.stats import chi2, f

B, M = 16, 12
LO, HI = 128, 1024
DF1, DF2 = B - 1, B * (M - 1)
SYNTH_SEED = 2036101991


def analytic() -> dict:
    fcrit = f.ppf(0.95, DF1, DF2)
    out = {"F_crit": fcrit, "R_crit": sqrt(fcrit),
           "R_crit_known_denominator": sqrt(chi2.ppf(0.95, DF1) / DF1)}
    for rho in (1.3, 1.6, 2.0):
        out[f"power_rho_{rho}"] = f.sf(fcrit / rho ** 2, DF1, DF2)
    return out


def batch_stats(qlo: np.ndarray, qhi: np.ndarray) -> tuple[float, float]:
    """Annealed batch slope and its tree-level delta SE (S1 P3 formula)."""
    c = -2.0 / log(HI / LO)
    mlo, mhi = qlo.mean(), qhi.mean()
    d = c * (log(mhi) - log(mlo))
    psi = c * ((qhi - mhi) / mhi - (qlo - mlo) / mlo)
    return d, psi.std(ddof=1) / sqrt(len(psi))


def simulate(law: str, cv: float, reps: int, rng) -> dict:
    rcrit = analytic()["R_crit"]
    rs, vols = [], []
    for _ in range(reps):
        z = rng.standard_normal((B * M, 2))
        if law == "log-t3":  # heavy-tailed log-returns
            z = z / np.sqrt(rng.chisquare(3, (B * M, 1)) / 3)
        s = sqrt(log(1 + cv ** 2))
        x_lo = s * z[:, 0]
        x_hi = s * (0.8 * z[:, 0] + 0.6 * z[:, 1])  # corr 0.8 between times
        qlo, qhi = np.exp(x_lo).reshape(B, M), 1e-3 * np.exp(x_hi).reshape(B, M)
        d, se = zip(*(batch_stats(qlo[b], qhi[b]) for b in range(B)))
        d, se = np.array(d), np.array(se)
        rs.append(d.std(ddof=1) / sqrt(np.mean(se ** 2)))
        vols.append(se.std(ddof=1) / se.mean())
    rs = np.array(rs)
    return {"law": law, "cv": cv, "P(R>R_crit)": float(np.mean(rs > rcrit)),
            "median_R": float(np.median(rs)), "median_CV_SE": float(np.median(vols))}


if __name__ == "__main__":
    a = analytic()
    for k, v in a.items():
        print(f"{k:28s} {v:.4f}")
    rng = np.random.default_rng(SYNTH_SEED)
    for law, cv in (("lognormal", 0.125), ("lognormal", 0.3), ("lognormal", 1.0), ("log-t3", 0.3), ("log-t3", 1.0)):
        r = simulate(law, cv, 4000, rng)
        print(f"{r['law']:9s} cv={r['cv']:.3f}  P(R>R_crit)={r['P(R>R_crit)']:.3f}"
              f"  median R={r['median_R']:.3f}  median CV(SE_b)={r['median_CV_SE']:.3f}")
