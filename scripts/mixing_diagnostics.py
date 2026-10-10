"""Split-Rhat and autocorrelation-window diagnostics on persisted finite-size traces.

Classic unranked split-Rhat is a descriptive warning, not an equilibrium proof.
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np


def split_rhat(chains):
    """Classic two-half split-R-hat; unlike rank-normalized/folded modern R-hat."""
    a = np.asarray(chains, dtype=float)
    if a.ndim != 2 or len(a) < 4 or a.shape[1] < 20 or not np.isfinite(a).all():
        raise ValueError("expected >=4 independent chains with >=20 finite measurements")
    n = a.shape[1] // 2
    chunks = np.concatenate((a[:, :n], a[:, -n:]), axis=0)
    within = float(np.var(chunks, axis=1, ddof=1).mean())
    if within <= 1e-28:
        return None
    between = float(n * np.var(chunks.mean(axis=1), ddof=1))
    return float(math.sqrt(max(0.0, ((n - 1) / n * within + between / n) / within)))


def evaluate(j):
    cfg = j["config"]
    rows = j["records"]
    expected = 2 * len(cfg["sizes"]) * len(cfg["temperatures"]) * cfg["repeats"]
    if len(rows) != expected or len({r["seed"] for r in rows}) != expected:
        raise ValueError("wrong chain count or repeated RNG seeds")
    result = []
    for temperature in cfg["temperatures"]:
        for size in cfg["sizes"]:
            selected = [r for r in rows if r["temperature"] == temperature and r["size"] == size]
            if len(selected) != 2 * cfg["repeats"]:
                raise ValueError("missing group")
            for obs in ("energy", "abs_magnetization"):
                chains = [r["raw_series"][obs] for r in selected]
                size_expected = (cfg["sample_sweeps"]+cfg["sample_every"]-1)//cfg["sample_every"]
                if any(len(x) != size_expected for x in chains):
                    raise ValueError("truncated raw series")
                ess = [r["observables"][obs]["ess_last"] for r in selected]
                tau = [r["observables"][obs]["tau_last"] for r in selected]
                batch_tau = [r["observables"][obs]["tau_batch20_last"] for r in selected]
                both = [(a,b) for a,b in zip(tau,batch_tau) if a is not None and b is not None]
                result.append({
                    "size": size, "temperature": temperature, "observable": obs,
                    "classic_split_rhat": split_rhat(chains),
                    "ess_last_median": float(np.median([v for v in ess if v is not None])) if any(v is not None for v in ess) else None,
                    "ess_last_min": min((v for v in ess if v is not None), default=None),
                    "chains_ess_under25": sum(v is not None and v < 25 for v in ess),
                    "chains_ess_undefined": sum(v is None for v in ess),
                    "median_tau_last": float(np.median([x for x in tau if x is not None])) if any(x is not None for x in tau) else None,
                    "median_batch20_tau_last": float(np.median([x for x in batch_tau if x is not None])) if any(x is not None for x in batch_tau) else None,
                    "batch20_tau_less_than_half_window_tau": sum(b < a/2 for a,b in both),
                })
    return {
        "source_environment": j.get("environment"), "config": cfg, "diagnostics": result,
        "caveats": ["Classic unranked split-Rhat is not Vehtari rank-normalized/folded Rhat and misses some nonconvergence modes.",
                    "Chain splits share histories; this indicator is approximate and correlated with ESS.",
                    "Rhat close to one is not proof of equilibrium. Both Rhat and τ estimators can be optimistic for modes not seen.",
                    "12 correlated size/temperature/observable comparisons are exploratory without multiplicity control."],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mixing-json", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    report = evaluate(json.loads(args.mixing_json.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+"\n")
    for row in report["diagnostics"]:
        print(row["size"], row["temperature"], row["observable"],
              "Rhat", row["classic_split_rhat"], "ESS<25", row["chains_ess_under25"])


if __name__ == "__main__":
    main()
