"""Bounded near-critical finite-size mixing diagnostic, not a mixing-time proof.

Even-L checkerboard Metropolis run from independent random and ordered starts.
Compare windows, hot/cold end-ensemble means and correlation times from an
explicitly finite measurement series. Reject unbounded sweep configurations.
"""
import argparse
import json
import math
import os
import platform
from pathlib import Path

import numpy as np
from .stats import autocorrelation_diagnostics, independent_chain_interval


def _block_tau(x, width):
    """Correlated batch-means estimator; too-short blocks may underestimate tau."""
    x = np.asarray(x, float)
    n = len(x) // width
    if n < 8 or np.var(x) < 1e-28:
        return None
    m = x[:n * width].reshape(n, width).mean(axis=1)
    return float(max(0.5, width * np.var(m, ddof=1) / (2 * np.var(x, ddof=1))))


def run_chain(size, temperature, samples, every, seed, start):
    if size % 2 != 0 or size < 4 or start not in ("random", "ordered"):
        raise ValueError("even grid and random/ordered starts required")
    rng = np.random.default_rng(seed)
    if start == "ordered":
        s = np.ones((size, size), dtype=np.int8)
    else:
        s = (2 * rng.integers(0, 2, size=(size, size), dtype=np.int8) - 1)
    parity = (np.indices((size, size)).sum(axis=0) % 2)
    energy, mag = [], []
    initial_energy = float(-np.sum(s * (np.roll(s, 1, 0) + np.roll(s, 1, 1))) / s.size)
    initial_abs_m = float(np.abs(np.mean(s)))
    for sweep in range(samples):
        for color in (0, 1):
            nb = np.roll(s, 1, 0) + np.roll(s, -1, 0) + np.roll(s, 1, 1) + np.roll(s, -1, 1)
            de = 2 * s * nb
            accept = (de <= 0) | (rng.random((size, size)) < np.exp(-np.maximum(0, de) / temperature))
            s[(parity == color) & accept] *= -1
        if sweep % every == 0:
            mag.append(float(abs(np.mean(s))))
            energy.append(float(-np.sum(s * (np.roll(s, 1, 0) + np.roll(s, 1, 1))) / s.size))
    half = len(mag)//2
    metrics = {}
    for name, trace in (("energy", energy), ("abs_magnetization", mag)):
        left, right = trace[:half], trace[half:]
        first, second, full = (autocorrelation_diagnostics(x) for x in (left, right, trace))
        metrics[name] = {
            "first_mean": float(np.mean(left)), "last_mean": float(np.mean(right)),
            "drift": float(np.mean(right)-np.mean(left)),
            "tau_first": first["tau_int"], "tau_last": second["tau_int"],
            "tau_full": full["tau_int"], "ess_last": second["effective_samples"],
            "tau_batch20_last": _block_tau(right, 20),
        }
    return {"size": size, "temperature": temperature, "start": start, "seed": seed,
            "initial_energy": initial_energy, "initial_abs_magnetization": initial_abs_m,
            "measurements": len(mag), "raw_series": {"energy": energy, "abs_magnetization": mag},
            "observables": metrics}


def run_pilot(cfg):
    sizes, temps = cfg["sizes"], cfg["temperatures"]
    reps, samples, every = cfg["repeats"], cfg["sample_sweeps"], cfg["sample_every"]
    if (not isinstance(sizes, list) or not sizes or len(set(sizes)) != len(sizes)
            or any(type(s) is not int or s < 8 or s > 32 or s % 2 for s in sizes)
            or not isinstance(temps, list) or not temps or len(set(temps)) != len(temps)
            or any(type(t) not in (int, float) or not math.isfinite(t) or t <= 0 for t in temps)
            or type(reps) is not int or not 8 <= reps <= 24
            or type(cfg["base_seed"]) is not int or type(samples) is not int or not 500 <= samples <= 2400
            or type(every) is not int or every < 1 or every > 10 or samples // every < 100):
        raise ValueError("invalid mixing pilot design")
    chains = 2 * len(sizes) * len(temps) * reps
    proposals = 2 * sum(s*s for s in sizes) * len(temps) * reps * samples
    if chains > 180 or proposals > 300_000_000:
        raise ValueError("mixing pilot budget exceeded")
    traces = []
    for ti, t in enumerate(temps):
        for si, size in enumerate(sizes):
            for start_idx, start in enumerate(("random", "ordered")):
                for rep in range(reps):
                    seed = cfg["base_seed"] + ti * 100000 + si * 10000 + start_idx * 1000 + rep
                    traces.append(run_chain(size, float(t), samples, every, seed, start))
    groups = []
    for t in temps:
        for size in sizes:
            bundle = {start: [r for r in traces if r["temperature"] == t and r["size"] == size and r["start"] == start]
                      for start in ("random", "ordered")}
            for name in ("energy", "abs_magnetization"):
                a = [r["observables"][name]["last_mean"] for r in bundle["random"]]
                b = [r["observables"][name]["last_mean"] for r in bundle["ordered"]]
                drift_a = [r["observables"][name]["drift"] for r in bundle["random"]]
                drift_b = [r["observables"][name]["drift"] for r in bundle["ordered"]]
                ess_a = [r["observables"][name]["ess_last"] for r in bundle["random"]]
                ess_b = [r["observables"][name]["ess_last"] for r in bundle["ordered"]]
                rng = np.random.default_rng(cfg["base_seed"]+int(temperature_seed(t, ti=temps.index(t)))+size+(name=="energy")*10)
                da = np.asarray(a)
                db = np.asarray(b)
                diffs = da[rng.integers(0, reps, size=(3000, reps))].mean(1)-db[rng.integers(0, reps, size=(3000, reps))].mean(1)
                low, high = np.quantile(diffs, [0.025, 0.975])
                bound = 0.12 if name == "energy" else 0.08
                ess = [x for x in ess_a+ess_b if x is not None]
                groups.append({"size": size, "temperature": t, "observable": name,
                               "random_end": independent_chain_interval(a)[0],
                               "ordered_end": independent_chain_interval(b)[0],
                               "random_minus_ordered": float(np.mean(a)-np.mean(b)),
                               "bootstrap95_difference": [float(low),float(high)],
                               "equivalence_bound": bound,
                               "equivalent_by_ci": bool(low > -bound and high < bound),
                               "drift_random_ci95": independent_chain_interval(drift_a)[2:4],
                               "drift_ordered_ci95": independent_chain_interval(drift_b)[2:4],
                               "min_last_ess": min(ess) if ess else None,
                               "undefined_ess": len(ess_a)+len(ess_b)-len(ess),
                               "all_last_ess_ge25": len(ess) == 2*reps and all(x >= 25 for x in ess)})
    return {"config": cfg, "environment": {"python": platform.python_version(), "numpy": np.__version__,
                                                  "commit": os.getenv("GIT_SHA")},
            "records": traces, "groups": groups,
            "proposals": proposals,
            "prospective_pass": bool(all(g["equivalent_by_ci"] and g["all_last_ess_ge25"] for g in groups)),
            "limitations": ["Stationary distribution in each arm is hypothesized, not certified by this pilot.",
                            "Bootstrap CI for arm differences uses iid across-chain resampling; correlated sweeps stay within chains.",
                            "Within-chain ESS heuristic and block20 tau can underestimate long autocorrelation tails; undefined is not zero.",
                            "Checking many correlated size/temperature/observable cells inflates familywise error; rule is conservative screening, not significance test.",
                            "No proof of total variation mixing time or critical exponent estimation."]}


def temperature_seed(temperature, ti):
    # Use index only: no rounding temperatures into collision-prone seed identifiers.
    return ti * 101


def main():
    parser = argparse.ArgumentParser(description="Bounded finite-size start-state and ESS audit")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_pilot(json.loads(args.config.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print("proposals",result["proposals"],"chains",len(result["records"]),"groups",len(result["groups"]),"pass",result["prospective_pass"])


if __name__ == "__main__":
    main()
