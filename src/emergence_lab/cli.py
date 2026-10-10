import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import platform
from pathlib import Path
import numpy as np
from .ising import run_chain
from .stats import summarize_replicates



def plan_seeded_experiments(cfg: dict, max_experiments: int = 2000,
                            max_spin_proposals: int = 100_000_000) -> list[tuple[int, float, int]]:
    """Fail closed on collisions and compute budget BEFORE creating output files.

    This intentionally preserves the legacy M3 seed schedule for historical
    reproducibility. Its rounded-temperature arithmetic is *not* injective:
    reject colliding plans instead of silently reusing the same RNG streams.
    """
    sizes, temperatures, repeats = cfg["sizes"], cfg["temperatures"], cfg["repeats"]
    if (not isinstance(sizes, list) or not sizes or
            not isinstance(temperatures, list) or not temperatures or
            type(repeats) is not int or repeats < 1 or
            type(cfg["base_seed"]) is not int or cfg["base_seed"] < 0 or
            any(type(size) is not int or size < 4 for size in sizes) or
            any(type(t) not in (float, int) or not np.isfinite(t) or t <= 0 for t in temperatures) or
            any(type(cfg[k]) is not int for k in ("burn_sweeps", "sample_sweeps", "sample_every")) or
            cfg["burn_sweeps"] < 0 or cfg["sample_sweeps"] < 1 or cfg["sample_every"] < 1 or
            max_experiments < 1 or max_spin_proposals < 1):
        raise ValueError("invalid or non-finite experiment configuration")
    total_chains = len(sizes) * len(temperatures) * repeats
    proposals = sum(size * size for size in sizes) * len(temperatures) * repeats * (
        cfg["burn_sweeps"] + cfg["sample_sweeps"])
    if total_chains > max_experiments or proposals > max_spin_proposals:
        raise ValueError(f"experiment exceeds budget: {total_chains} chains, {proposals} proposed flips")
    plans = []
    seen = set()
    for size in sizes:
        for t in temperatures:
            for repeat in range(repeats):
                seed = cfg["base_seed"] + 100000 * size + 1000 * int(round(t * 100)) + repeat
                if seed in seen:
                    raise ValueError(f"seed schedule collision at size={size}, T={t}, repeat={repeat}, seed={seed}")
                seen.add(seed)
                plans.append((size, float(t), seed))
    return plans

def main() -> None:
    parser = argparse.ArgumentParser(description="Reproducible 2D Ising experiments")
    parser.add_argument("--config", default="configs/smoke.json")
    parser.add_argument("--output", default="results")
    args = parser.parse_args()
    config_bytes = Path(args.config).read_bytes()
    cfg = json.loads(config_bytes)
    plan = plan_seeded_experiments(cfg, int(os.getenv("MAX_EXPERIMENTS", "2000")),
                                    int(os.getenv("MAX_SPIN_PROPOSALS", "100000000")))
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for size, t, seed in plan:
        rows.append(run_chain(size, t, cfg["burn_sweeps"],
                              cfg["sample_sweeps"], seed, cfg["sample_every"]))
    with (output / "measurements.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    summaries = summarize_replicates(rows)
    with (output / "summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summaries[0].keys())
        writer.writeheader()
        writer.writerows(summaries)
    manifest = {
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "config": cfg, "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "commit": os.getenv("GIT_SHA"),
        "python": platform.python_version(), "numpy": np.__version__,
        "model": "2d-ferromagnetic-ising-metropolis-periodic-J1-kB1",
        "result_rows": len(rows), "summary_rows": len(summaries),
        "uncertainty_method": {
            "chain": "positive-lag integrated autocorrelation heuristic, stop at first nonpositive rho or window lag>=5*tau; n>=20 and nonconstant required",
            "replicates": "independent-seed chain means; between-chain Student-t approximate 95% CI; conservative tabulated upper bounds for df>10",
        },
        "caveats": [
            "Autocorrelation time may be underestimated for slow chains; constant/short traces return missing diagnostics",
            "Independent-chain intervals assume approximately normal chain means and adequate equilibration; neither is verified",
            "Small number of repeats and critical slowing down make these intervals exploratory",
            "No finite-size scaling inference or phase-transition detection is claimed",
        ],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {len(rows)} measurements and {len(summaries)} summaries to {output.resolve()}")


if __name__ == "__main__":
    main()
