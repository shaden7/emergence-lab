"""Predeclared exploratory frequentist coverage audit for exact 4x4 Ising targets.

A batch consists of independently seeded chain means. Coverage is evaluated
across nonoverlapping batches, never across correlated sweeps.
"""
import argparse
import json
from math import sqrt
from pathlib import Path

from .exact4 import exact_observables
from .ising import run_chain
from .stats import summarize_replicates

OBSERVABLES = {
    "mean_energy_per_spin": ("energy_ci95_low", "energy_ci95_high"),
    "mean_abs_magnetization": ("magnetization_ci95_low", "magnetization_ci95_high"),
}


def wilson_interval(successes: int, trials: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson binomial interval; batch-independence assumption is essential."""
    if not 0 <= successes <= trials or trials < 1:
        raise ValueError("invalid coverage count")
    p = successes / trials
    d = 1 + z*z/trials
    middle = (p + z*z/(2*trials))/d
    half = z * sqrt(p*(1-p)/trials + z*z/(4*trials*trials))/d
    return middle - half, middle + half


def run_coverage(cfg: dict) -> dict:
    """Check nominal 95% CI coverage against exact finite-system expectations."""
    required = ("temperatures", "batches", "chains_per_batch", "base_seed",
                "burn_sweeps", "sample_sweeps", "sample_every")
    if any(key not in cfg for key in required):
        raise ValueError("missing configuration")
    temps = cfg["temperatures"]
    if not temps or len(set(temps)) != len(temps):
        raise ValueError("temperatures must be nonempty and unique")
    if cfg["batches"] < 2 or cfg["chains_per_batch"] < 4:
        raise ValueError("at least two batches and four chains per batch required")
    if cfg["burn_sweeps"] < 0 or cfg["sample_sweeps"] < 1 or cfg["sample_every"] < 1:
        raise ValueError("invalid sweeps")
    if not all(isinstance(cfg[k], int) for k in ("batches","chains_per_batch","base_seed","burn_sweeps","sample_sweeps","sample_every")):
        raise ValueError("integer run parameters required")
    maximum = cfg["batches"] * cfg["chains_per_batch"] * len(temps)
    if maximum > 500:
        raise ValueError("maximum 500 chains per audit")
    exact = {str(t): exact_observables(float(t)) for t in temps}
    records = []
    for t_index, t in enumerate(temps):
        for batch in range(cfg["batches"]):
            rows = []
            for chain in range(cfg["chains_per_batch"]):
                # Explicit nonoverlapping seed blocks. Never reuse exact4 holdout seeds.
                seed = cfg["base_seed"] + (t_index * cfg["batches"] + batch) * cfg["chains_per_batch"] + chain
                rows.append(run_chain(4, float(t), cfg["burn_sweeps"], cfg["sample_sweeps"], seed, cfg["sample_every"]))
            summary = summarize_replicates(rows)[0]
            for observable, (lower, upper) in OBSERVABLES.items():
                target = exact[str(t)][observable]
                records.append({
                    "temperature": t, "batch": batch, "observable": observable,
                    "mean": summary[observable], "lower": summary[lower], "upper": summary[upper],
                    "reference": target, "covered": summary[lower] <= target <= summary[upper],
                })
    aggregates = []
    for t in temps:
        for name in OBSERVABLES:
            subset = [r for r in records if r["temperature"] == t and r["observable"] == name]
            hits = sum(r["covered"] for r in subset)
            low, high = wilson_interval(hits, len(subset))
            aggregates.append({
                "temperature": t, "observable": name, "batches": len(subset),
                "covered_batches": hits, "coverage_fraction": hits/len(subset),
                "wilson95_low": low, "wilson95_high": high,
            })
    return {
        "config": cfg, "aggregates": aggregates, "batches": records,
        "interpretation": "Exploratory nominal-95% interval coverage for finite 4x4 Ising; Wilson ranges are conditional on independent batches and do not correct for multiple observables.",
        "limitations": [
            "A small pilot cannot establish calibrated coverage.",
            "Burn-in bias and slowly mixing chains can invalidate coverage.",
            "Reference is finite-L exact enumeration, not an infinite-lattice phase transition.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent-batch exact4 confidence-interval coverage pilot")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    report = run_coverage(cfg)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    for row in report["aggregates"]:
        print(f"T={row['temperature']} {row['observable']}: {row['covered_batches']}/{row['batches']} covered (Wilson 95% {row['wilson95_low']:.3f}–{row['wilson95_high']:.3f})")


if __name__ == "__main__":
    main()
