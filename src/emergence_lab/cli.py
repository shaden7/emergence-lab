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


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproducible 2D Ising experiments")
    parser.add_argument("--config", default="configs/smoke.json")
    parser.add_argument("--output", default="results")
    args = parser.parse_args()
    config_bytes = Path(args.config).read_bytes()
    cfg = json.loads(config_bytes)
    temperatures = cfg["temperatures"]
    sizes = cfg["sizes"]
    repeats = cfg["repeats"]
    if not sizes or not temperatures or not isinstance(repeats, int) or repeats < 1:
        raise ValueError("Config requires nonempty sizes/temperatures and positive repeats")
    max_experiments = int(os.getenv("MAX_EXPERIMENTS", "2000"))
    if len(sizes) * len(temperatures) * repeats > max_experiments:
        raise ValueError("Experiment exceeds MAX_EXPERIMENTS")
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for size in sizes:
        for t in temperatures:
            for repeat in range(repeats):
                seed = int(cfg["base_seed"]) + 100000 * int(size) + 1000 * int(round(float(t) * 100)) + repeat
                rows.append(run_chain(int(size), float(t), int(cfg["burn_sweeps"]),
                                      int(cfg["sample_sweeps"]), seed, int(cfg["sample_every"])))
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
