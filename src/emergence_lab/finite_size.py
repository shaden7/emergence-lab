"""Bounded finite-size 2D Ising pilot and independent-spin null control.

Even-L checkerboard Metropolis half-sweeps each preserve the Gibbs target;
the J=0 control uses exact independent-spin heat-bath draws. Statistics are
calculated from independent chain estimates, not individual autocorrelated sweeps.
"""
import argparse
import json
import math
import os
import platform
from pathlib import Path

import numpy as np

from .stats import independent_chain_interval


def chain(size: int, temperature: float, burn_sweeps: int, sample_sweeps: int,
          sample_every: int, seed: int, interacting: bool = True) -> dict:
    if (type(size) is not int or size < 4 or size % 2 or not math.isfinite(temperature)
            or temperature <= 0 or type(burn_sweeps) is not int or burn_sweeps < 0
            or type(sample_sweeps) is not int or sample_sweeps < 1
            or type(sample_every) is not int or sample_every < 1):
        raise ValueError("even size>=4, T>0, and valid sweep counts required")
    rng = np.random.default_rng(seed)
    spins = 2 * rng.integers(0, 2, size=(size, size), dtype=np.int8) - 1
    parity = np.indices((size, size)).sum(axis=0) % 2
    n = size * size
    e, a, m, m2, m4 = [], [], [], [], []
    for sweep in range(burn_sweeps + sample_sweeps):
        if interacting:
            for color in (0, 1):
                neighbors = (np.roll(spins, 1, 0) + np.roll(spins, -1, 0)
                             + np.roll(spins, 1, 1) + np.roll(spins, -1, 1))
                delta = 2 * spins * neighbors
                accept = (delta <= 0) | (rng.random((size, size)) < np.exp(-np.maximum(delta, 0) / temperature))
                spins[(parity == color) & accept] *= -1
        else:
            # Exact equilibrium sampling of J=0 spins; not a Metropolis J=0 spin-flip chain.
            spins = 2 * rng.integers(0, 2, size=(size, size), dtype=np.int8) - 1
        if sweep >= burn_sweeps and (sweep - burn_sweeps) % sample_every == 0:
            signed = float(spins.mean())
            m.append(signed)
            a.append(abs(signed))
            m2.append(signed * signed)
            m4.append(signed ** 4)
            if interacting:
                e.append(float(-np.sum(spins * (np.roll(spins, 1, 0) + np.roll(spins, 1, 1))) / n))
            else:
                e.append(0.0)
    q2 = float(np.mean(m2))
    return {
        "size": size, "temperature": temperature, "seed": seed,
        "interacting": interacting, "measurements": len(m),
        "energy_per_spin": float(np.mean(e)),
        "abs_magnetization": float(np.mean(a)),
        # Convention explicitly uses abs-m mean (avoids low-T sign-flip susceptibility ambiguity).
        "susceptibility_abs": float(n / temperature * (q2 - np.mean(a) ** 2)),
        "binder": float(1 - np.mean(m4) / (3 * q2 * q2)) if q2 > 0 else None,
    }


def run_pilot(cfg: dict) -> dict:
    sizes = cfg["sizes"]
    temps = cfg["temperatures"]
    repeats = cfg["repeats"]
    burn, sample, every = cfg["burn_sweeps"], cfg["sample_sweeps"], cfg["sample_every"]
    if (not isinstance(sizes, list) or not sizes or any(type(s) is not int or s < 4 or s % 2 for s in sizes)
            or len(set(sizes)) != len(sizes) or not isinstance(temps, list) or not temps
            or any(not isinstance(t, (float, int)) or not math.isfinite(t) or t <= 0 for t in temps)
            or len(set(temps)) != len(temps) or type(repeats) is not int or not 4 <= repeats <= 50
            or type(cfg["base_seed"]) is not int or type(burn) is not int or type(sample) is not int
            or type(every) is not int or burn < 0 or sample < 1 or every < 1):
        raise ValueError("invalid configuration")
    chains = len(sizes) * len(temps) * repeats * 2
    proposals = sum(s*s for s in sizes) * len(temps) * repeats * (burn+sample)
    # Bound even though null control generates iid spins, and prohibit accidental expensive sweeps.
    if chains > 160 or proposals > 55_000_000 or max(sizes) > 32 or (burn+sample) > 1500:
        raise ValueError("pilot budget exceeded")
    records = []
    for model in (True, False):
        for ti, t in enumerate(temps):
            for si, size in enumerate(sizes):
                for rep in range(repeats):
                    # Blocked deterministic seed namespace, no temperature-rounding collisions.
                    seed = cfg["base_seed"] + (not model)*10_000_000 + ti * 100_000 + si * 1_000 + rep
                    records.append(chain(size, float(t), burn, sample, every, seed, model))
    summaries = []
    for model in (True, False):
        for t in temps:
            for size in sizes:
                group = [r for r in records if r["interacting"] == model and r["temperature"] == t and r["size"] == size]
                s = {"interacting": model, "temperature": t, "size": size, "replicates": repeats}
                for observable in ("energy_per_spin", "abs_magnetization", "susceptibility_abs", "binder"):
                    values = [r[observable] for r in group]
                    if None in values:
                        s[observable] = {"mean": None, "stderr": None, "ci95_low": None, "ci95_high": None}
                    else:
                        mean, se, low, high = independent_chain_interval(values)
                        s[observable] = {"mean": mean, "stderr": se, "ci95_low": low, "ci95_high": high}
                summaries.append(s)
    return {"config": cfg, "environment": {"python": platform.python_version(), "numpy": np.__version__, "commit": os.getenv("GIT_SHA")},
            "records": records, "summaries": summaries,
            "proposed_flips_interacting": proposals,
            "caveats": [
                "Exploratory pilot: no exponent fitting or binder crossings are justified by these few sizes/replicates.",
                "Checkerboard Metropolis is a second sampler: finite-size tests do not validate original random-site chain independently.",
                "Within-chain nonlinear susceptibility/Binder estimates can have finite-trajectory bias.",
                "Independent chain mean Student-t intervals require approximate normality and equilibration; neither follows from CI shape.",
                "Null spin samples are exact iid equilibrium J=0; this is an analytic negative control, not emergent behavior.",
            ]}


def main():
    parser = argparse.ArgumentParser(description="Budgeted L=4..32 finite-size Ising and J=0 pilot")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    report = run_pilot(cfg)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print("Wrote", len(report["records"]), "chain records,", len(report["summaries"]), "summaries")


if __name__ == "__main__":
    main()
