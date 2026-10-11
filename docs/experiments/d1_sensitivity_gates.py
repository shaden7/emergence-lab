"""D1 (Issue #4) post-hoc sensitivity of the *gate outcomes* (prereg v1.0 §5, "Sensitivity").

Descriptive only, never gated. Reads a D1 `result.json`, re-applies the frozen §2 verdict rule to the
stored mean ball sizes B̄(r) under each preregistered sensitivity setting (ε ∈ {0.10, 0.20},
r_min ∈ {2, 8}, guard N/4 or N/16), and re-evaluates gates D-G1…D-G4 with the unchanged gate code.
D-G0 is an exactness check of the implementation and is not re-evaluated. No graph is regenerated.

Usage: python docs/experiments/d1_sensitivity_gates.py results/d1_full/result.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from emergence_lab.dimension_d1 import CONFIG_PATH, evaluate_gates, verdict


def settings(cfg: dict) -> dict:
    est = cfg["estimator"]
    base = dict(r_min=est["r_min"], eps=est["plateau_epsilon"], guard_fraction=0.125)
    out = {"main": base}
    sens = cfg["sensitivity_not_gated"]
    for e in sens["plateau_epsilon"]:
        out[f"eps={e}"] = {**base, "eps": e}
    for rm in sens["r_min"]:
        out[f"r_min={rm}"] = {**base, "r_min": rm}
    for gf in sens["saturation_guard_fraction"]:
        out[f"guard={gf}"] = {**base, "guard_fraction": gf}
    return out


def recompute(result: dict, cfg: dict, s: dict) -> list[dict]:
    est = cfg["estimator"]
    out = []
    for r in result["results"]:
        bbar = {int(k): v for k, v in r["bbar"].items()}
        v = verdict(bbar, r["n"], s["r_min"], s["eps"], est["plateau_min_scales"], s["guard_fraction"])
        out.append({**r, **{k: v[k] for k in ("verdict", "d_hat", "window", "post_window_drift",
                                              "admissible", "d_eff")}})
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    result = json.loads(Path(argv[0]).read_text())
    cfg = json.loads(Path(CONFIG_PATH).read_text())
    table = {}
    for name, s in settings(cfg).items():
        res = recompute(result, cfg, s)
        g = evaluate_gates(res, cfg)
        table[name] = {k: g[k]["pass"] for k in ("D-G1", "D-G2", "D-G3", "D-G4") if k in g}
        if "D-G3" in g:
            table[name]["D-G3_means"] = {N: round(v["mean"], 6) if "mean" in v else None
                                         for N, v in g["D-G3"]["by_N"].items()}
            table[name]["D-G3_n_plateau"] = {N: v["n_plateau"] for N, v in g["D-G3"]["by_N"].items()}
    main_ = table["main"]
    for name, row in table.items():
        row["flips_vs_main"] = [k for k in ("D-G1", "D-G2", "D-G3", "D-G4") if row.get(k) != main_.get(k)]
    print(json.dumps(table, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
