"""Pilot A N5: preregistered detector-noise stress, never a causal-cone estimator.

Frozen design: docs/PILOT_A_N5_NOISE_PREREGISTRATION.md, commit
8686ae276e6cb4892c8410874136ae2baf31c93e.
Only development reference fixtures are evaluated; the one-shot holdout is not touched.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np

from emergence_lab import pilot_a as pa

PREREG_COMMIT = "8686ae276e6cb4892c8410874136ae2baf31c93e"
PREREG_BLOB_SHA = "966a36a163033e62883b8ebb28ae3e27a21260ff"
MODEL_ORDER = ("W", "H", "CA", "Q")
SUPPORT = {"W": "strict", "H": "nonstrict", "CA": "strict", "Q": "nonstrict"}
EXPECTED_CONFIG = {
    "parent_protocol": "docs/PILOT_A_CAUSAL_PROPAGATION_PREREGISTRATION.md",
    "parent_protocol_sha256": "c8061aed335bda61c9f35cc72b601aac8d1287436c49c83883ea5ec36b9e4c96",
    "preregistration": "docs/PILOT_A_N5_NOISE_PREREGISTRATION.md",
    "seed_base": 2027101005, "replicates": 20, "sites": [0, 1, 2, 4, 6, 8, 12],
    "sigmas": [0, 1e-6, 1e-4], "thresholds": [1e-3, 1e-6, 1e-9],
    "models": {"W": {"t": 1}, "H": {"t": 1}, "CA": {"n": 2, "L": 128},
               "Q": {"t": 1, "L": 128}},
    "sentinel_r": 6,
    "noise_model": "independent Gaussian per arm per cell; S_hat=abs(S_true+eps_do-eps_control)",
}
CSV_FIELDS = ("model", "sigma", "eta", "replicate", "r", "S_true",
              "noise_do", "noise_control", "S_hat", "detected", "support_class",
              "theorem_zero_exterior", "false_positive", "seed_base",
              "sigma_index", "eta_index", "replicate_index", "model_index")


def check_frozen_config(cfg: dict) -> None:
    if cfg != EXPECTED_CONFIG:
        raise ValueError("N5 parameters changed from the preregistered configuration")
    if dict(pa.SUPPORT_CLASS) != SUPPORT:
        raise ValueError("parent mathematical support classes changed")


def _git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def validate_protocol_files(cfg: dict) -> dict:
    """Fail closed if the pinned parent protocol or N5 preregistration changed."""
    parent = Path(cfg["parent_protocol"]).read_bytes()
    prereg = Path(cfg["preregistration"]).read_bytes()
    if hashlib.sha256(parent).hexdigest() != cfg["parent_protocol_sha256"]:
        raise ValueError("parent preregistration digest mismatch")
    if _git_blob_sha(prereg) != PREREG_BLOB_SHA:
        raise ValueError("N5 preregistration changed since frozen commit")
    return {"parent_protocol_sha256": hashlib.sha256(parent).hexdigest(),
            "n5_prereg_sha256": hashlib.sha256(prereg).hexdigest(),
            "n5_prereg_git_blob_sha": _git_blob_sha(prereg)}


def reference_values(cfg: dict) -> dict[str, list[float]]:
    """Exact/independent reference paths, NOT results of a noisy simulation."""
    sites = cfg["sites"]
    L = cfg["models"]["Q"]["L"]
    q = pa.qwalk_fourier(L, cfg["models"]["Q"]["t"])
    refs = {
        "W": [pa.wave_reference(r, cfg["models"]["W"]["t"]) for r in sites],
        "H": [pa.heat_reference(r, cfg["models"]["H"]["t"]) for r in sites],
        "CA": [float(pa.ca_reference(r, cfg["models"]["CA"]["n"], cfg["models"]["CA"]["L"]))
               for r in sites],
        "Q": [float(q[r]) for r in sites],
    }
    for model, values in refs.items():
        if len(values) != len(sites) or not all(math.isfinite(v) and v >= 0 for v in values):
            raise ValueError(f"invalid reference for {model}")
    if refs["W"][sites.index(6)] != 0 or refs["CA"][sites.index(6)] != 0:
        raise ValueError("preregistered sentinel is no longer an analytic zero")
    if not (refs["H"][sites.index(6)] > 0 and refs["Q"][sites.index(6)] > 0):
        raise ValueError("nonstrict positive counter-witness invalid")
    return refs


def is_exterior_theorem_zero(model: str, r: int, cfg: dict) -> bool:
    if model == "W":
        return abs(r) > 0.5 + cfg["models"]["W"]["t"]
    if model == "CA":
        return pa.ring_distance(r, cfg["models"]["CA"]["L"]) > cfg["models"]["CA"]["n"]
    return False


def wilson95(k: int, n: int) -> tuple[float, float]:
    if not 0 <= k <= n or n == 0:
        raise ValueError("invalid independent replicate counts")
    z = 1.959963984540054
    p = k / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    radius = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, center - radius), min(1.0, center + radius)


def gaussian_false_detection_probability(sigma: float, eta: float) -> float:
    if sigma < 0 or eta <= 0:
        raise ValueError("sigma must be nonnegative and eta positive")
    return 0.0 if sigma == 0 else math.erfc(eta / (2 * sigma))


def run(cfg: dict) -> dict:
    """20 disjoint seeded detector worlds per (sigma, threshold, model)."""
    check_frozen_config(cfg)
    t0 = time.process_time()
    refs = reference_values(cfg)
    sites = cfg["sites"]
    rows, trials, summaries = [], [], []
    seed_keys = set()
    g1, g2, g3, g4, g6 = True, True, True, True, True

    for i_sigma, sigma in enumerate(cfg["sigmas"]):
        for i_eta, eta in enumerate(cfg["thresholds"]):
            for i_model, model in enumerate(MODEL_ORDER):
                values = np.asarray(refs[model], dtype=float)
                sent_hits = 0
                any_false_count = 0
                front_hist: dict[str, int] = {}
                zero_count = 0
                for i_rep in range(cfg["replicates"]):
                    key = (cfg["seed_base"], i_sigma, i_eta, i_rep, i_model)
                    if key in seed_keys:
                        raise ValueError("duplicate random seed tuple")
                    seed_keys.add(key)
                    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(key)))
                    do_noise = rng.normal(0.0, sigma, len(sites))
                    control_noise = rng.normal(0.0, sigma, len(sites))
                    observed = np.abs(values + do_noise - control_noise)
                    detected = observed >= eta
                    front = pa.detection_front(sites, observed, eta)
                    front_key = "undefined" if front is None else str(front)
                    front_hist[front_key] = front_hist.get(front_key, 0) + 1
                    clean_front = pa.detection_front(sites, values, eta)
                    if sigma == 0:
                        zero_count += 1
                        g1 &= bool(np.array_equal(observed, values) and front == clean_front)
                    sentinel_detected = bool(detected[sites.index(cfg["sentinel_r"])])
                    if model in ("W", "CA"):
                        sent_hits += int(sentinel_detected)
                        if sigma == 0 and sentinel_detected:
                            g1 = False
                    false_sites = []
                    for j, r in enumerate(sites):
                        exterior = is_exterior_theorem_zero(model, r, cfg)
                        false_pos = bool(exterior and detected[j])
                        if exterior:
                            if values[j] != 0:
                                g6 = False
                            false_sites.append(false_pos)
                        rows.append({
                            "model": model, "sigma": sigma, "eta": eta, "replicate": i_rep,
                            "r": r, "S_true": float(values[j]),
                            "noise_do": float(do_noise[j]), "noise_control": float(control_noise[j]),
                            "S_hat": float(observed[j]), "detected": bool(detected[j]),
                            "support_class": SUPPORT[model],
                            "theorem_zero_exterior": exterior, "false_positive": false_pos,
                            "seed_base": cfg["seed_base"], "sigma_index": i_sigma,
                            "eta_index": i_eta, "replicate_index": i_rep, "model_index": i_model,
                        })
                    any_false = any(false_sites)
                    any_false_count += int(any_false)
                    trials.append({"model": model, "sigma": sigma, "eta": eta, "replicate": i_rep,
                                   "r_eta": front, "clean_r_eta": clean_front,
                                   "sentinel_detected": sentinel_detected if model in ("W", "CA") else None,
                                   "any_false_exterior": any_false if model in ("W", "CA") else None,
                                   "seed": list(key)})
                    g2 &= bool(np.all(np.isfinite(observed)) and np.all(observed >= 0)
                               and SUPPORT[model] == pa.SUPPORT_CLASS[model])

                condition = {"model": model, "sigma": sigma, "eta": eta,
                             "independent_replicates": cfg["replicates"],
                             "front_histogram": front_hist,
                             "reference_front": pa.detection_front(sites, values, eta)}
                if model in ("W", "CA"):
                    null_p = gaussian_false_detection_probability(sigma, eta)
                    condition.update({"sentinel_r": cfg["sentinel_r"],
                                      "sentinel_false_detection": sent_hits,
                                      "sentinel_wilson95": wilson95(sent_hits, cfg["replicates"]),
                                      "analytic_gaussian_null_p": null_p,
                                      "any_false_exterior": any_false_count})
                    if sigma == 1e-6 and eta == 1e-3:
                        g3 &= sent_hits == 0
                    if sigma == 1e-4 and eta == 1e-9:
                        g3 &= sent_hits >= 19
                    if sigma == 1e-6 and eta == 1e-6:
                        g4 &= 2 <= sent_hits <= 18
                summaries.append(condition)

    n = cfg["replicates"]
    g5 = (len(seed_keys) == 3 * 3 * 4 * n and len(trials) == len(seed_keys)
          and len(rows) == len(seed_keys) * len(sites))
    g6 &= all(row["support_class"] == SUPPORT[row["model"]]
              and (not row["false_positive"] or row["theorem_zero_exterior"])
              for row in rows)
    return {
        "references": {model: dict(zip(sites, vals)) for model, vals in refs.items()},
        "rows": rows, "trials": trials, "conditions": summaries,
        "gates": {"N5-G1": bool(g1), "N5-G2": bool(g2), "N5-G3": bool(g3),
                  "N5-G4": bool(g4), "N5-G5": bool(g5), "N5-G6": bool(g6)},
        "cpu_seconds": time.process_time() - t0,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Frozen Pilot A N5 detector noise (development only)")
    parser.add_argument("--config", default="configs/pilot_a_n5.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    cfg_path = Path(args.config)
    cfg_bytes = cfg_path.read_bytes()
    cfg = json.loads(cfg_bytes)
    check_frozen_config(cfg)
    digests = validate_protocol_files(cfg)
    result = run(cfg)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "rows.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(result["rows"])
    csv_sha256 = hashlib.sha256((out / "rows.csv").read_bytes()).hexdigest()
    manifest = {
        "schema": 1, "preregistration_commit": PREREG_COMMIT, **digests,
        "executing_commit": os.environ.get("GIT_SHA"),
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "config": str(cfg_path), "config_sha256": hashlib.sha256(cfg_bytes).hexdigest(),
        "python": sys.version.split()[0], "numpy": np.__version__,
        "bit_generator": "PCG64", "platform": platform.platform(),
        "noise_model": cfg["noise_model"], "sigma": cfg["sigmas"],
        "eta": cfg["thresholds"], "models": cfg["models"], "sites": cfg["sites"],
        "seed_base": cfg["seed_base"], "seed_tuple": ["seed_base", "sigma_index", "eta_index",
                                                      "replicate_index", "model_index"],
        "replicates_per_condition": cfg["replicates"],
        "theoretical_null": "erfc(eta/(2*sigma)) for independent arm readout noise at S_true=0",
        "rows_csv_sha256": csv_sha256, "cpu_seconds": result["cpu_seconds"],
        "limitations": ["Single observation per arm and site, not ensemble expectation.",
                        "No holdout re-evaluation; all sites are development fixtures.",
                        "Detector noise cannot modify mathematical support classes.",
                        "Within-replicate sites and cross-condition comparisons are not CI replicates."],
    }
    summary = {k: v for k, v in result.items() if k not in ("rows", "trials")}
    summary["manifest"] = manifest
    (out / "result.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"gates": result["gates"], "n_rows": len(result["rows"]),
                      "n_trials": len(result["trials"]), "rows_sha256": csv_sha256}, indent=2))
    return 0 if all(result["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
