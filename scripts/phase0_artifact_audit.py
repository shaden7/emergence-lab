"""Re-analyze M4/burn-in workflow ZIPs and finite-size pilot JSON.

Only NumPy is required. Inputs are primary raw JSON outputs, not transcribed rates.
No correction for correlated observables is inferred from per-cell intervals.
"""
import argparse
import json
import math
from pathlib import Path
from zipfile import ZipFile
import numpy as np

T9_975 = 2.262157163


def from_zip(path, filename):
    with ZipFile(path) as z:
        return json.loads(z.read(filename))


def mean_interval(x):
    x = np.asarray(x, float)
    if len(x) != 10 or not np.isfinite(x).all():
        raise ValueError("audit expects exactly 10 independent batches")
    m = float(x.mean())
    h = float(T9_975 * x.std(ddof=1) / math.sqrt(10))
    return {"mean": m, "low": m - h, "high": m + h}


def audit_coverage(report):
    out = []
    for row in report["aggregates"]:
        sub = [b for b in report["batches"] if b["temperature"] == row["temperature"] and b["observable"] == row["observable"]]
        hits = sum(bool(x["covered"]) for x in sub)
        if len(sub) != report["config"]["batches"] or hits != row["covered_batches"]:
            raise ValueError("M4 aggregate disagrees with raw batch rows")
        if any(bool(x["covered"]) != (x["lower"] <= x["reference"] <= x["upper"]) for x in sub):
            raise ValueError("M4 coverage flag inconsistent with interval")
        out.append({"temperature": row["temperature"], "observable": row["observable"], "hits": hits,
                    "batches": len(sub), "fraction": hits / len(sub),
                    "wilson95": [row["wilson95_low"], row["wilson95_high"]],
                    "batch_mean_bias": float(np.mean([x["mean"] - x["reference"] for x in sub]))})
    return out


def audit_burnin(report):
    arms = []
    for arm in report["arms"]:
        for agg in arm["aggregates"]:
            sub = [b for b in arm["batches"] if b["temperature"] == agg["temperature"] and b["observable"] == agg["observable"]]
            if len(sub) != 10 or sum(b["covered"] for b in sub) != agg["covered_batches"]:
                raise ValueError("burn-in aggregate disagrees with batches")
            arms.append({"burn_sweeps": arm["burn_sweeps"], "temperature": agg["temperature"],
                         "observable": agg["observable"], "bias_ci95": mean_interval([b["mean"] - b["reference"] for b in sub]),
                         "covered": agg["covered_batches"], "batches": 10})
    paired = []
    for burn in report["config"]["burn_sweeps_variants"][1:]:
        for t in report["config"]["temperatures"]:
            for observable in ("mean_energy_per_spin", "mean_abs_magnetization"):
                sub = [r for r in report["paired_contrasts"] if r["burn_sweeps"] == burn and r["temperature"] == t and r["observable"] == observable]
                if len(sub) != 10 or any(abs(r["variant_bias"] - r["baseline_bias"] - r["paired_mean_shift"]) > 1e-11 for r in sub):
                    raise ValueError("paired contrast inconsistent with raw arm means")
                paired.append({"burn_sweeps": burn, "temperature": t, "observable": observable,
                               "difference_ci95": mean_interval([r["paired_mean_shift"] for r in sub]),
                               "covered_to_missed": sum(r["baseline_covered"] and not r["variant_covered"] for r in sub),
                               "missed_to_covered": sum(not r["baseline_covered"] and r["variant_covered"] for r in sub)})
    return arms, paired


def audit_scaling(report, bootstrap_draws=3000, seed=20261009):
    cfg = report["config"]
    if len(report["records"]) != 2 * len(cfg["sizes"]) * len(cfg["temperatures"]) * cfg["repeats"]:
        raise ValueError("unexpected finite-size chain count")
    target = min(cfg["temperatures"], key=lambda t: abs(t-2.269185))
    rng = np.random.default_rng(seed)
    rows = []
    for model in (True, False):
        selected = [r for r in report["records"] if r["interacting"] == model and r["temperature"] == target]
        for obs in ("abs_magnetization", "susceptibility_abs"):
            groups = np.asarray([[r[obs] for r in selected if r["size"] == size] for size in cfg["sizes"]])
            if groups.shape != (len(cfg["sizes"]), cfg["repeats"]):
                raise ValueError("missing finite-size replicates")
            logs = np.log(cfg["sizes"])
            def slope(a, first):
                return float(np.polyfit(logs[first:], np.log(a[first:].mean(axis=1)), 1)[0])
            samples = np.stack([groups[i, rng.integers(0, cfg["repeats"], size=(bootstrap_draws, cfg["repeats"]))] for i in range(len(groups))])
            full = np.array([slope(samples[:, j, :], 0) for j in range(bootstrap_draws)])
            drop = np.array([slope(samples[:, j, :], 1) for j in range(bootstrap_draws)])
            rows.append({"interacting": model, "observable": obs, "temperature": target,
                         "slope": slope(groups, 0), "bootstrap95": np.quantile(full, [.025, .975]).tolist(),
                         "drop_smallest_slope": slope(groups, 1),
                         "drop_smallest_bootstrap95": np.quantile(drop, [.025, .975]).tolist()})
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--m4-zip", type=Path, required=True)
    p.add_argument("--burnin-zip", type=Path, required=True)
    p.add_argument("--fss-json", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    a = from_zip(args.m4_zip, "exact4_coverage.json")
    b = from_zip(args.burnin_zip, "exact4_burnin.json")
    f = json.loads(args.fss_json.read_text())
    arms, paired = audit_burnin(b)
    out = {"m4": audit_coverage(a), "burnin_arms": arms, "burnin_paired": paired,
           "finite_size_effective_slopes": audit_scaling(f),
           "limitations": ["18 paired comparisons are exploratory and unadjusted; individual 95% intervals cannot establish familywise effects.",
                           "Two arms with matched RNG seeds have distinct trajectory positions, so pairing does not isolate equilibration effects.",
                           "Bootstrap resamples chains only; finite-size correction and critical-temperature uncertainty are not included."]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print("Audited", len(out["m4"]), "coverage cells,", len(arms), "arms,", len(paired), "contrasts,", len(out["finite_size_effective_slopes"]), "slopes")


if __name__ == "__main__":
    main()
