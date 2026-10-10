"""G3 addendum: AR(1) high-phi stress test of ``emergence_lab.convergence``.

Preregistered in ``docs/experiments/2026-10-10-g3-ar1-stress.md``. Exact
answer: tau = (1 + phi) / (1 - phi) in the 1 + 2*sum(rho) convention.
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys

import numpy as np

from emergence_lab import convergence as cv

CHAINS = 16
CELLS = [
    # name, phi, length multiple of tau, seed
    ("long_phi0.98", 0.98, 500, 2031100001),
    ("long_phi0.995", 0.995, 500, 2031100002),
    ("short_phi0.98", 0.98, 20, 2031100003),
    ("short_phi0.995", 0.995, 20, 2031100004),
]


def exact_tau(phi: float) -> float:
    return (1.0 + phi) / (1.0 - phi)


def ar1(rng: np.random.Generator, m: int, n: int, phi: float) -> np.ndarray:
    x = np.empty((m, n))
    x[:, 0] = rng.normal(size=m) / np.sqrt(1.0 - phi * phi)
    e = rng.normal(size=(m, n))
    for t in range(1, n):
        x[:, t] = phi * x[:, t - 1] + e[:, t]
    return x


def run_cell(name: str, phi: float, mult: int, seed: int) -> dict:
    tau = exact_tau(phi)
    n = int(round(mult * tau))
    x = ar1(np.random.default_rng(seed), CHAINS, n, phi)
    per = [cv.chain_ess(row) for row in x]
    taus = np.array([p["tau"] if p["tau"] is not None else np.nan for p in per])
    esss = np.array([p["ess"] if p["ess"] is not None else np.nan for p in per])
    multi = cv.ess(x)
    out = {
        "name": name, "phi": phi, "seed": seed, "chains": CHAINS, "n": n,
        "tau_exact": tau,
        "tau_multi": multi["tau"],
        "ess_bulk": cv.ess_bulk(x),
        "nominal_total_ess": CHAINS * n / tau,
        "chain_tau": taus.tolist(),
        "chain_ess": esss.tolist(),
        "chain_tau_median": float(np.nanmedian(taus)),
        "chain_tau_ratio_min": float(np.nanmin(taus) / tau),
        "chain_tau_ratio_max": float(np.nanmax(taus) / tau),
    }
    if name.startswith("long"):
        out["checks"] = {
            "A1_multi_tau_within_15pct": abs(multi["tau"] / tau - 1) <= 0.15,
            "A2_median_chain_tau_within_20pct": abs(out["chain_tau_median"] / tau - 1) <= 0.20,
            "A3_at_most_2_chains_below_half": int(np.sum(taus < 0.5 * tau)) <= 2,
        }
    else:
        out["checks"] = {
            "S1_all_chains_ess_below_100": bool(np.all(~(esss >= 100))),
            "S2_ess_bulk_below_400": out["ess_bulk"] is None or out["ess_bulk"] < 400,
        }
    out["checks"] = {k: bool(v) for k, v in out["checks"].items()}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True)
    args = ap.parse_args(argv)
    cells = [run_cell(*c) for c in CELLS]
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                text=True, check=True).stdout.strip()
    except Exception:  # pragma: no cover
        commit = None
    res = {
        "preregistration": "docs/experiments/2026-10-10-g3-ar1-stress.md",
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "platform": platform.platform(), "commit": commit},
        "cells": cells,
        "gate_pass": all(all(c["checks"].values()) for c in cells),
    }
    with open(args.output, "w") as fh:
        json.dump(res, fh, indent=2)
    for c in cells:
        print(c["name"], "tau_exact=%.1f tau_multi=%.1f median_chain=%.1f ess_bulk=%s"
              % (c["tau_exact"], c["tau_multi"], c["chain_tau_median"], c["ess_bulk"]), c["checks"])
    print("gate_pass", res["gate_pass"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
