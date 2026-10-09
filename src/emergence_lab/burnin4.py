"""Preregistered burn-in sensitivity, matched seeds across equilibration lengths.

Within each arm, each batch has distinct seeds. Across arms, seeds are deliberately
reused to produce paired *contrasts*; do not treat arms as independent samples.
"""
import argparse
import json
from pathlib import Path
from .coverage4 import run_coverage


def burnin_sensitivity(cfg: dict) -> dict:
    burnins = cfg["burn_sweeps_variants"]
    if not isinstance(burnins, list) or len(burnins) < 2 or len(set(burnins)) != len(burnins):
        raise ValueError("need distinct burn-in variants")
    if any(type(b) is not int or b < 0 for b in burnins):
        raise ValueError("burn-in values must be nonnegative integers")
    if max(burnins) > 2000 or len(burnins) > 4:
        raise ValueError("burn-in budget exceeded")
    shared = {key: value for key, value in cfg.items() if key != "burn_sweeps_variants"}
    if "burn_sweeps" in shared:
        raise ValueError("do not supply a second burn-in specification")
    if shared["batches"] * shared["chains_per_batch"] * len(shared["temperatures"]) * len(burnins) > 500:
        raise ValueError("combined chain budget exceeded")
    arms = []
    for burn in burnins:
        result = run_coverage({**shared, "burn_sweeps": burn})
        arms.append({"burn_sweeps": burn, "aggregates": result["aggregates"], "batches": result["batches"]})
    contrasts = []
    baseline = arms[0]["batches"]
    for arm in arms[1:]:
        for row0, row1 in zip(baseline, arm["batches"], strict=True):
            if (row0["temperature"], row0["batch"], row0["observable"]) != (
                row1["temperature"], row1["batch"], row1["observable"]
            ):
                raise AssertionError("paired batch alignment failed")
            contrasts.append({
                "burn_sweeps": arm["burn_sweeps"], "temperature": row0["temperature"],
                "batch": row0["batch"], "observable": row0["observable"],
                "paired_mean_shift": row1["mean"] - row0["mean"],
                "baseline_bias": row0["mean"] - row0["reference"],
                "variant_bias": row1["mean"] - row1["reference"],
                "baseline_covered": row0["covered"], "variant_covered": row1["covered"],
            })
    return {
        "config": cfg, "arms": arms, "paired_contrasts": contrasts,
        "caveats": [
            "Matched seeds across burn-in variants create paired, not independent, arms.",
            "Coverage fractions from 12 batches are imprecise and six observable-temperature cells are correlated.",
            "Differences in sample means mix equilibration bias and seed-specific trajectory changes.",
            "Non-significant differences cannot establish equilibrium; no multiple-comparison inference.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fixed-seed 4x4 Ising burn-in sensitivity")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    report = burnin_sensitivity(cfg)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    for arm in report["arms"]:
        for a in arm["aggregates"]:
            print(f"burn={arm['burn_sweeps']} T={a['temperature']} {a['observable']} coverage={a['covered_batches']}/{a['batches']}")


if __name__ == "__main__":
    main()
