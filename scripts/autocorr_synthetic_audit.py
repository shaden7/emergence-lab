"""Synthetic AR(1) stress test for existing Ising autocorrelation diagnostic.

Compares current first-nonpositive/5tau heuristic with Geyer-like initial
positive paired sequence and independent non-overlapping batch means.
Stationary AR(1) has exact tau_int=(1+phi)/(2*(1-phi)) for phi in [0,1).
These estimates are diagnostics, not rigorous confidence bounds on tau.
"""
import argparse
import json
import numpy as np
from emergence_lab.stats import autocorrelation_diagnostics


def geyer_initial_positive_pairs(x):
    x = np.asarray(x, float)
    n = len(x)
    y = x - np.mean(x)
    if n < 20 or float(y @ y) / n <= 1e-28:
        return None
    nfft = 1 << (2*n-1).bit_length()
    f = np.fft.rfft(y, nfft)
    ac = np.fft.irfft(f*f.conjugate(), nfft)[:n] / np.arange(n, 0, -1)
    rho = ac / ac[0]
    tau = 0.5
    for lag in range(1, n//2, 2):
        pair = float(rho[lag] + rho[lag+1])
        if pair <= 0:
            break
        tau += pair
    return max(0.5, tau)


def batch_means_tau(x, width):
    x = np.asarray(x, float)
    count = len(x)//width
    if count < 8 or np.var(x) <= 1e-28:
        return None
    means = x[:count*width].reshape(count, width).mean(axis=1)
    return float(width*np.var(means, ddof=1)/(2*np.var(x, ddof=1)))


def ar1(phi, seed, n=12000):
    rng = np.random.default_rng(seed)
    noise = rng.normal(size=n)
    x = np.empty(n)
    x[0] = noise[0]/np.sqrt(1-phi*phi)
    for i in range(1, n):
        x[i] = phi*x[i-1]+noise[i]
    return x


def evaluate():
    cases = []
    for phi in (0, 0.5, 0.9, 0.98, 0.995):
        rows = []
        for repeat in range(8):
            x = ar1(phi, 102938+repeat)
            rows.append({
                "old": autocorrelation_diagnostics(x)["tau_int"],
                "geyer_initial_positive_pairs": geyer_initial_positive_pairs(x),
                "batch250": batch_means_tau(x, 250),
                "batch500": batch_means_tau(x, 500),
            })
        cases.append({
            "phi": phi, "exact_tau_int": (1+phi)/(2*(1-phi)), "length": 12000,
            "seeds": list(range(102938, 102946)),
            "measurements": rows,
            "median_tau": {key: float(np.median([r[key] for r in rows])) for key in rows[0]},
        })
    return {
        "cases": cases,
        "constant_is_undefined": autocorrelation_diagnostics(np.ones(100))["tau_int"] is None,
        "short_is_undefined": autocorrelation_diagnostics(np.arange(10))["tau_int"] is None,
        "caveats": [
            "Eight samples per correlation level are descriptive, not precise bias estimates.",
            "AR(1) is a positive control with analytic tau, not a surrogate for Ising equilibration.",
            "The batch-means method can underestimate when blocks are shorter than several correlation times.",
            "IPS and the original heuristic may both be biased; neither replaces burn-in or multi-chain convergence tests.",
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    args = p.parse_args()
    from pathlib import Path
    out = evaluate()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2)+"\n")
    for case in out["cases"]:
        print("AR1", case["phi"], "true", case["exact_tau_int"], "median estimates", case["median_tau"])


if __name__ == "__main__":
    main()
