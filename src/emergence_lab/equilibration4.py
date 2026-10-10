"""Exact-stationary vs random/ordered initialisation: random-site L=4 Ising kernel.

Independent seeds for distinct initialisation arms. Snapshots at fixed sweep counts
are diagnostic ensemble means, not autocorrelation or mixing-time upper bounds.
"""
import argparse
import json
import math
import os
import platform
from functools import lru_cache
from pathlib import Path

import numpy as np
from .exact4 import exact_observables
from .stats import independent_chain_interval


@lru_cache(maxsize=1)
def _exact_states():
    # Enumeration independently of the Monte-Carlo energy routine.
    states = np.arange(1 << 16, dtype=np.uint32)
    up = np.zeros(1 << 16, dtype=np.int16)
    unlike = np.zeros(1 << 16, dtype=np.int16)
    for site in range(16):
        up += ((states >> site) & 1).astype(np.int16)
        row, col = divmod(site, 4)
        for neighbor in (row * 4 + (col + 1) % 4, ((row + 1) % 4) * 4 + col):
            unlike += (((states >> site) ^ (states >> neighbor)) & 1).astype(np.int16)
    return states, -32 + 2 * unlike


def sample_exact_state(rng, temperature):
    states, energies = _exact_states()
    weights = np.exp(-(energies - energies.min()) / temperature)
    weights /= weights.sum()
    choice = int(rng.choice(len(states), p=weights))
    spinbits = ((states[choice] >> np.arange(16)) & 1).astype(np.int8)
    return (2 * spinbits - 1).reshape((4, 4))


def observables(spins):
    return {
        "energy_per_spin": float(-np.sum(spins * (np.roll(spins, 1, 0) + np.roll(spins, 1, 1))) / 16),
        "abs_magnetization": float(abs(np.mean(spins))),
    }


def trace(temperature, probes, seed, start):
    if start not in ("random", "ordered", "exact") or not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("invalid start or temperature")
    rng = np.random.default_rng(seed)
    if start == "exact":
        spins = sample_exact_state(rng, temperature)
    elif start == "ordered":
        spins = np.ones((4, 4), dtype=np.int8)
    else:
        spins = 2 * rng.integers(0, 2, size=(4, 4), dtype=np.int8) - 1
    records = []
    for sweep in range(max(probes) + 1):
        if sweep in probes:
            records.append({"sweep": sweep, **observables(spins)})
        if sweep == max(probes):
            break
        # Same random-site single-spin Metropolis update kernel as original ising.py.
        for _ in range(16):
            x = int(rng.integers(4)); y = int(rng.integers(4))
            s = int(spins[x, y]); neighbors = (int(spins[(x-1)%4, y]) + int(spins[(x+1)%4, y])
                                                + int(spins[x, (y-1)%4]) + int(spins[x, (y+1)%4]))
            de = 2 * s * neighbors
            if de <= 0 or rng.random() < np.exp(-de/temperature):
                spins[x, y] = -s
    return records


def run(cfg):
    temps = cfg["temperatures"]
    probes = cfg["probes"]
    repeats = cfg["repeats"]
    if (not isinstance(temps, list) or not temps or len(set(temps)) != len(temps)
            or any(not isinstance(t, (int, float)) or not math.isfinite(t) or t <= 0 for t in temps)
            or not isinstance(probes, list) or len(probes) < 3
            or any(type(s) is not int or s < 0 for s in probes)
            or sorted(set(probes)) != probes or probes[0] != 0
            or type(repeats) is not int or not 4 <= repeats <= 80
            or type(cfg["base_seed"]) is not int or len(temps)*3*repeats*(max(probes)+1)*16 > 5_000_000):
        raise ValueError("invalid or over-budget exact4 equilibration protocol")
    starts = ("random", "ordered", "exact")
    results = []
    for ti, t in enumerate(temps):
        for si, start in enumerate(starts):
            for rep in range(repeats):
                seed = cfg["base_seed"] + ti*100_000 + si*1000 + rep
                for item in trace(float(t), probes, seed, start):
                    results.append({"temperature": t, "start": start, "seed": seed, **item})
    summaries = []
    for t in temps:
        ref = exact_observables(float(t))
        for start in starts:
            for sweep in probes:
                subset = [r for r in results if r["temperature"] == t and r["start"] == start and r["sweep"] == sweep]
                row = {"temperature": t, "start": start, "sweep": sweep, "chains": repeats}
                for obs in ("energy_per_spin", "abs_magnetization"):
                    m, se, low, high = independent_chain_interval([r[obs] for r in subset])
                    row[obs] = {"mean": m, "reference": ref["mean_"+obs] if obs == "energy_per_spin" else ref["mean_abs_magnetization"],
                                "bias": m - (ref["mean_"+obs] if obs == "energy_per_spin" else ref["mean_abs_magnetization"]),
                                "stderr": se, "ci95_low": low, "ci95_high": high}
                summaries.append(row)
    return {"config": cfg, "environment": {"python": platform.python_version(), "numpy": np.__version__, "commit": os.getenv("GIT_SHA")},
            "summary": summaries, "raw": results, "proposals": len(temps)*3*repeats*max(probes)*16,
            "limitations": ["Single snapshots from independent chains show ensemble relaxation, not integrated correlation times.",
                            "Independent exact-initial states are stationary in the target distribution only if the Metropolis kernel is correct.",
                            "Multiple probe times and both observables are correlated; intervals are descriptive, not simultaneous tests."]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(json.loads(args.config.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("proposals",result["proposals"],"snapshots",len(result["raw"]))


if __name__ == "__main__":
    main()
