"""Independent exact finite-lattice reference for the periodic 4x4 Ising benchmark.

Enumerates all 2**16 spin configurations using bitwise bond disagreements,
independently of the Monte Carlo energy and update implementations.
"""
import argparse
import csv
import hashlib
import json
from math import sqrt
from pathlib import Path

import numpy as np


def exact_observables(temperature: float) -> dict:
    """Boltzmann-weighted 4x4 absolute magnetization and energy per spin."""
    if not np.isfinite(temperature) or temperature <= 0:
        raise ValueError("temperature must be finite and positive")
    configurations = np.arange(1 << 16, dtype=np.uint32)
    up = np.zeros(len(configurations), dtype=np.int16)
    unlike_bonds = np.zeros(len(configurations), dtype=np.int16)
    for site in range(16):
        up += ((configurations >> site) & 1).astype(np.int16)
        row, col = divmod(site, 4)
        right = row * 4 + (col + 1) % 4
        down = ((row + 1) % 4) * 4 + col
        for neighbor in (right, down):
            unlike_bonds += (((configurations >> site) ^ (configurations >> neighbor)) & 1).astype(np.int16)
    # Exactly 32 undirected bonds in the 4x4 periodic square lattice.
    energies = -32 + 2 * unlike_bonds
    abs_magnetization = np.abs(2 * up - 16) / 16
    weights = np.exp(-(energies - energies.min()) / temperature)
    weights /= weights.sum()
    return {
        "mean_energy_per_spin": float(np.dot(weights, energies) / 16),
        "mean_abs_magnetization": float(np.dot(weights, abs_magnetization)),
        "mean_signed_magnetization": float(np.dot(weights, (2 * up - 16) / 16)),
    }


def assess_difference(estimate: float, stderr: float, reference: float, sigma_limit: float = 3.5) -> dict:
    """Exploratory threshold, not a coverage guarantee or calibrated hypothesis test."""
    values = (estimate, stderr, reference, sigma_limit)
    if not all(np.isfinite(value) for value in values) or sigma_limit <= 0:
        raise ValueError("expected finite estimate/reference/threshold")
    # A zero across-chain SEM is not evidence of perfect accuracy.
    z = abs(estimate - reference) / stderr if stderr > 0 else None
    return {
        "reference": reference, "estimate": estimate, "between_chain_stderr": stderr,
        "absolute_difference": abs(estimate - reference), "standard_error_units": z,
        "passes_3p5_sem_diagnostic": z is not None and z <= sigma_limit,
    }


def validate_results(config_path: Path, results_dir: Path) -> dict:
    """Check expected independent chains and compare summary means to enumeration."""
    config_bytes = config_path.read_bytes()
    cfg = json.loads(config_bytes)
    if cfg["sizes"] != [4] or cfg["repeats"] < 4:
        raise ValueError("exact validation requires only L=4 and at least 4 independent chains")
    if len(set(cfg["temperatures"])) != len(cfg["temperatures"]):
        raise ValueError("duplicate temperatures")
    manifest = json.loads((results_dir / "manifest.json").read_text())
    sha256 = hashlib.sha256(config_bytes).hexdigest()
    if manifest["config_sha256"] != sha256 or manifest["config"] != cfg:
        raise ValueError("manifest and benchmark config differ")
    with (results_dir / "measurements.csv").open(newline="") as f:
        measurements = list(csv.DictReader(f))
    with (results_dir / "summary.csv").open(newline="") as f:
        summaries = list(csv.DictReader(f))
    expected_count = len(cfg["temperatures"]) * cfg["repeats"]
    if len(measurements) != expected_count or len(summaries) != len(cfg["temperatures"]):
        raise ValueError("wrong number of chains or temperature summaries")

    by_temperature = {}
    all_seeds = set()
    for row in measurements:
        if int(row["size"]) != 4:
            raise ValueError("incorrect size in measurement")
        t = float(row["temperature"])
        if t not in cfg["temperatures"]:
            raise ValueError("unconfigured temperature in measurement")
        seed = int(row["seed"])
        if seed in all_seeds:
            raise ValueError("duplicate RNG seed in measurements")
        all_seeds.add(seed)
        by_temperature.setdefault(t, []).append(row)

    by_summary = {}
    for row in summaries:
        if int(row["size"]) != 4:
            raise ValueError("incorrect summary size")
        t = float(row["temperature"])
        if t in by_summary or t not in cfg["temperatures"]:
            raise ValueError("invalid/duplicate summary temperature")
        by_summary[t] = row

    comparisons = []
    for t in cfg["temperatures"]:
        chain_rows = by_temperature.get(t, [])
        if len(chain_rows) != cfg["repeats"] or t not in by_summary:
            raise ValueError("missing independent chains/summary")
        reference = exact_observables(t)
        summary = by_summary[t]
        if int(summary["replicates"]) != cfg["repeats"]:
            raise ValueError("incorrect summary replicate count")
        for name in ("mean_energy_per_spin", "mean_abs_magnetization"):
            chain_means = np.array([float(r[name]) for r in chain_rows])
            mean = float(chain_means.mean())
            sem = float(chain_means.std(ddof=1) / sqrt(len(chain_means)))
            summary_sem_key = "energy_stderr" if name == "mean_energy_per_spin" else "magnetization_stderr"
            if abs(float(summary[name]) - mean) > 1e-10 or abs(float(summary[summary_sem_key]) - sem) > 1e-10:
                raise ValueError("summary disagrees with independent-chain calculations")
            assessed = assess_difference(mean, sem, reference[name])
            lower_key = "energy_ci95_low" if name == "mean_energy_per_spin" else "magnetization_ci95_low"
            upper_key = "energy_ci95_high" if name == "mean_energy_per_spin" else "magnetization_ci95_high"
            assessed.update({
                "temperature": t, "observable": name, "replicates": len(chain_rows),
                "reference_inside_reported_ci95": float(summary[lower_key]) <= reference[name] <= float(summary[upper_key]),
            })
            comparisons.append(assessed)
    return {
        "passed": all(r["passes_3p5_sem_diagnostic"] for r in comparisons),
        "method": "Exact enumeration of 2^16 spin states; compare independent-chain means within 3.5 observed between-chain SEM",
        "config_sha256": sha256,
        "commit_from_manifest": manifest.get("commit"),
        "comparisons": comparisons,
        "caveats": [
            "A 3.5-SEM cutoff is an exploratory anomaly screen, not a statistically calibrated multiple-testing criterion.",
            "Coverage cannot be established from one holdout; autocorrelation and equilibration bias require longer tests.",
            "Finite 4x4 equilibrium validation does not establish infinite-size critical behavior.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Exact periodic 4x4 Ising validation")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()
    report = validate_results(args.config, args.results)
    (args.results / "exact4_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    for row in report["comparisons"]:
        print(f"T={row['temperature']}: {row['observable']}, z={row['standard_error_units']}, pass={row['passes_3p5_sem_diagnostic']}")
    if not report["passed"]:
        raise SystemExit("Exact 4x4 validation FAILED; see exact4_validation.json")


if __name__ == "__main__":
    main()
