"""Diagnostic uncertainty estimates for Ising Monte Carlo chains.

Autocorrelation estimates are finite-sample diagnostics, not convergence proofs.
Independent-chain intervals use between-seed variation and Student-t critical values.
"""
from collections import defaultdict
from math import sqrt

import numpy as np


# 97.5th percentiles of Student's t distribution, df = 1 ... 10.
_T975 = (12.706204736, 4.302652730, 3.182446305, 2.776445105,
         2.570581836, 2.446911851, 2.364624252, 2.306004135,
         2.262157163, 2.228138852)


def autocorrelation_diagnostics(samples) -> dict:
    """Estimate autocorrelation-adjusted SEM, ESS, integrated correlation time.

    Heuristic positive-sequence sum, stopping at first nonpositive lag or
    self-consistent 5*tau window. For <20 samples or constant series the
    diagnostics are undefined (rather than misleadingly precise zero).
    """
    x = np.asarray(samples, dtype=float)
    if x.ndim != 1 or not np.all(np.isfinite(x)):
        raise ValueError("Expected finite one-dimensional samples")
    n = len(x)
    missing = {"stderr": None, "tau_int": None, "effective_samples": None}
    if n < 20:
        return missing
    centered = x - x.mean()
    variance = float(np.dot(centered, centered) / n)
    if variance <= 1e-28:
        return missing
    tau = 0.5
    for lag in range(1, n // 2 + 1):
        rho = float(np.dot(centered[:-lag], centered[lag:]) / ((n - lag) * variance))
        if rho <= 0:
            break
        tau += rho
        if lag >= 5 * tau:
            break
    tau = max(0.5, tau)
    stderr = sqrt(float(np.var(x, ddof=1)) * 2 * tau / n)
    return {"stderr": stderr, "tau_int": tau,
            "effective_samples": min(float(n), n / (2 * tau))}


def independent_chain_interval(values) -> tuple[float, float | None, float | None, float | None]:
    """Mean, between-chain SEM and approximate two-sided 95% t interval.

    Each input is one *independently seeded chain mean*, not individual sweeps.
    Critical values for df > 10 are rounded *up* to conservative bounds.
    """
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or len(x) == 0 or not np.all(np.isfinite(x)):
        raise ValueError("Expected nonempty finite independent-chain means")
    mean = float(x.mean())
    if len(x) == 1:
        return mean, None, None, None
    sem = float(np.std(x, ddof=1) / sqrt(len(x)))
    # A frozen sample of chain means is NOT an infinitely precise estimate.
    # It may indicate no effective mixing, even when all observed values agree.
    if sem == 0.0:
        return mean, None, None, None
    df = len(x) - 1
    critical = _T975[df - 1] if df <= 10 else (2.23 if df <= 30 else 2.05)
    return mean, sem, mean - critical * sem, mean + critical * sem


def summarize_replicates(rows: list[dict]) -> list[dict]:
    """Aggregate chain means by (lattice size, temperature); no sweep pooling."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["size"], row["temperature"])].append(row)
    summaries = []
    for (size, temperature), group in sorted(grouped.items()):
        m = independent_chain_interval([r["mean_abs_magnetization"] for r in group])
        e = independent_chain_interval([r["mean_energy_per_spin"] for r in group])
        summaries.append({
            "size": size, "temperature": temperature, "replicates": len(group),
            "mean_abs_magnetization": m[0], "magnetization_stderr": m[1],
            "magnetization_ci95_low": m[2], "magnetization_ci95_high": m[3],
            "mean_energy_per_spin": e[0], "energy_stderr": e[1],
            "energy_ci95_low": e[2], "energy_ci95_high": e[3],
            "min_magnetization_effective_samples": _min_available(group, "magnetization_effective_samples"),
            "min_energy_effective_samples": _min_available(group, "energy_effective_samples"),
        })
    return summaries


def _min_available(group: list[dict], key: str) -> float | None:
    values = [r[key] for r in group if r[key] is not None]
    return min(values) if len(values) == len(group) else None
