"""Preregistered L32 critical-mixing gate (see docs/L32_CRITICAL_GATE_PREREGISTRATION.md).

Even-L checkerboard Metropolis (the sampler of ``mixing_pilot``) from random and
ordered starts, explicit discarded warmup, then thinned measurements. Raw
integer energy/magnetization sums are kept losslessly in an ``.npz`` file whose
SHA-256 is recorded in the JSON report. Gate criteria are fixed in the config
and in the preregistration; this module only evaluates them.
"""
import argparse
import hashlib
import io
import json
import math
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from . import convergence as cv
from .exact_finite import exact_energy_per_spin
from .stats import independent_chain_interval

STARTS = ("random", "ordered")


def run_chain(size: int, temperature: float, warmup: int, sweeps: int, every: int,
              seed: int, start: str) -> dict:
    if size % 2 or size < 4 or start not in STARTS or warmup < 0 or sweeps < 1 or every < 1:
        raise ValueError("invalid chain parameters")
    rng = np.random.default_rng(seed)
    if start == "ordered":
        s = np.ones((size, size), dtype=np.int8)
    else:
        s = (2 * rng.integers(0, 2, size=(size, size), dtype=np.int8) - 1)
    masks = [(np.indices((size, size)).sum(axis=0) % 2) == c for c in (0, 1)]
    n_meas = sweeps // every
    e_sum = np.empty(n_meas, dtype=np.int16)
    m_sum = np.empty(n_meas, dtype=np.int16)
    k = 0
    for sweep in range(warmup + sweeps):
        for mask in masks:
            nb = np.roll(s, 1, 0) + np.roll(s, -1, 0) + np.roll(s, 1, 1) + np.roll(s, -1, 1)
            de = 2 * s * nb
            accept = (de <= 0) | (rng.random((size, size)) < np.exp(-np.maximum(0, de) / temperature))
            s[mask & accept] *= -1
        t = sweep - warmup
        if t >= 0 and (t + 1) % every == 0:
            e_sum[k] = -int(np.sum(s * (np.roll(s, 1, 0) + np.roll(s, 1, 1))))
            m_sum[k] = int(np.sum(s))
            k += 1
    return {"seed": seed, "start": start, "energy_sum": e_sum, "magnetization_sum": m_sum}


def _chain_job(args):
    return run_chain(*args)


def validate_config(cfg: dict) -> int:
    keys = {"size", "temperature", "chains_per_start", "base_seed", "warmup_sweeps",
            "sample_sweeps", "sample_every", "max_proposals", "criteria", "power_control_sweeps"}
    if set(cfg) - {"description"} != keys:
        raise ValueError("unexpected or missing config keys")
    L, reps = cfg["size"], cfg["chains_per_start"]
    if (type(L) is not int or L % 2 or not 8 <= L <= 64 or type(reps) is not int or not 4 <= reps <= 32
            or type(cfg["base_seed"]) is not int or not math.isfinite(cfg["temperature"])
            or cfg["temperature"] <= 0 or cfg["sample_sweeps"] % cfg["sample_every"]
            or cfg["power_control_sweeps"] % cfg["sample_every"]
            or not 0 < cfg["power_control_sweeps"] < cfg["sample_sweeps"]):
        raise ValueError("invalid gate design")
    proposals = 2 * reps * L * L * (cfg["warmup_sweeps"] + cfg["sample_sweeps"])
    if proposals > cfg["max_proposals"] or cfg["max_proposals"] > 5_000_000_000:
        raise ValueError("gate budget exceeded")
    return proposals


def _per_chain(series: np.ndarray, reference: float | None) -> dict:
    est = cv.chain_ess(series)
    mean = float(series.mean())
    sd = float(series.std(ddof=1))
    out = {"mean": mean, "sd": sd, "ess": est["ess"], "tau": est["tau"]}
    if est["ess"]:
        half = 1.959963984540054 * sd / math.sqrt(est["ess"])
        out["ci95"] = [mean - half, mean + half]
        if reference is not None:
            out["covers_reference"] = bool(mean - half <= reference <= mean + half)
    return out


def _welch(a, b) -> dict:
    a, b = np.asarray(a, float), np.asarray(b, float)
    diff = float(a.mean() - b.mean())
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return {"difference": diff, "stderr": se, "z": diff / se if se > 0 else None}


def evaluate(energy: np.ndarray, absm: np.ndarray, starts: list, cfg: dict, reference: float) -> dict:
    """Apply the preregistered criteria to (chains, draws) arrays."""
    crit = cfg["criteria"]
    obs = {"energy": energy, "abs_magnetization": absm}
    report, checks = {}, {}
    hot = np.array([s == "random" for s in starts])
    for name, a in obs.items():
        ref = reference if name == "energy" else None
        chains = [_per_chain(row, ref) for row in a]
        means = [c["mean"] for c in chains]
        mean, se, lo, hi = independent_chain_interval(means)
        r = {"rhat_bulk": cv.rhat_bulk(a), "rhat_tail": cv.rhat_tail(a),
             "ess_bulk": cv.ess_bulk(a), "ess_tail": cv.ess_tail(a),
             "chain_ess_min": min((c["ess"] for c in chains if c["ess"]), default=None),
             "chain_ess_median": float(np.median([c["ess"] for c in chains if c["ess"]])),
             "chain_tau_median_draws": float(np.median([c["tau"] for c in chains if c["tau"]])),
             "pooled_mean": mean, "pooled_stderr": se, "pooled_ci95": [lo, hi],
             "hot_minus_cold": _welch(np.asarray(means)[hot], np.asarray(means)[~hot]),
             "chains": chains}
        r["rhat_max"] = max(r["rhat_bulk"], r["rhat_tail"])
        checks[f"G1_rhat_{name}"] = r["rhat_max"] < crit["rhat_max"]
        checks[f"G2_ess_{name}"] = min(r["ess_bulk"], r["ess_tail"]) >= crit["ess_bulk_tail_min"]
        checks[f"G3_chain_ess_{name}"] = (all(c["ess"] for c in chains)
                                          and r["chain_ess_min"] >= crit["chain_ess_min"])
        z = r["hot_minus_cold"]["z"]
        checks[f"G4_hot_cold_{name}"] = z is not None and abs(z) <= crit["z_max"]
        if name == "energy":
            z_ref = (mean - reference) / se
            r["exact_reference"] = reference
            r["z_vs_exact"] = z_ref
            checks["G5_exact_energy"] = bool(lo <= reference <= hi and abs(z_ref) <= crit["z_max"])
            covered = sum(bool(c.get("covers_reference")) for c in chains)
            r["chains_covering_exact"] = covered
            checks["G6_chain_coverage"] = covered >= crit["chain_coverage_min"]
        report[name] = r
    return {"observables": report, "checks": checks, "gate_pass": bool(all(checks.values()))}


def run_gate(cfg: dict, workers: int = 1):
    proposals = validate_config(cfg)
    L, T, reps = cfg["size"], float(cfg["temperature"]), cfg["chains_per_start"]
    jobs = [(L, T, cfg["warmup_sweeps"], cfg["sample_sweeps"], cfg["sample_every"],
             cfg["base_seed"] + si * 1000 + rep, start)
            for si, start in enumerate(STARTS) for rep in range(reps)]
    t0, c0 = time.time(), time.process_time()
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            chains = list(ex.map(_chain_job, jobs))
    else:
        chains = [_chain_job(j) for j in jobs]
    wall = time.time() - t0
    n = L * L
    e_sum = np.stack([c["energy_sum"] for c in chains])
    m_sum = np.stack([c["magnetization_sum"] for c in chains])
    starts = [c["start"] for c in chains]
    energy, absm = e_sum / n, np.abs(m_sum) / n
    reference = exact_energy_per_spin(T, L)["energy_per_spin"]
    main = evaluate(energy, absm, starts, cfg, reference)
    k = cfg["power_control_sweeps"] // cfg["sample_every"]
    control = evaluate(energy[:, :k], absm[:, :k], starts, cfg, reference)
    for o in control["observables"].values():
        o.pop("chains")
    buf = io.BytesIO()
    np.savez_compressed(buf, energy_sum=e_sum, magnetization_sum=m_sum,
                        seeds=np.array([c["seed"] for c in chains]),
                        starts=np.array(starts))
    raw = buf.getvalue()
    report = {
        "config": cfg,
        "config_sha256": hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest(),
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "commit": os.getenv("GIT_SHA"), "workers": workers,
                        "wall_seconds": wall, "parent_cpu_seconds": time.process_time() - c0},
        "proposals": proposals, "draws_per_chain": int(e_sum.shape[1]),
        "seeds": [c["seed"] for c in chains], "starts": starts,
        "raw_npz_sha256": hashlib.sha256(raw).hexdigest(),
        "main": main,
        "power_control": {"draws_per_chain": k, **control,
                          "expected": "G3 fails; otherwise G3 is flagged non-discriminating"},
        "caveats": [
            "Diagnostics cannot detect regions of state space that no chain visited.",
            "|m| has no exact finite-L reference here; only R-hat, ESS and hot/cold checks apply.",
            "One size and one temperature; says nothing about other L, T or samplers.",
            "Per-chain intervals use a normal approximation with Geyer ESS.",
        ],
    }
    return report, raw


def main():
    p = argparse.ArgumentParser(description="Preregistered L32 critical-mixing gate")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True, help="JSON report path; raw .npz written alongside")
    p.add_argument("--workers", type=int, default=1)
    args = p.parse_args()
    report, raw = run_gate(json.loads(args.config.read_text()), args.workers)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".npz").write_bytes(raw)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print("raw_npz_sha256", report["raw_npz_sha256"])
    for name, o in report["main"]["observables"].items():
        print(name, "pooled_mean", repr(o["pooled_mean"]), "rhat_max", repr(o["rhat_max"]),
              "chain_ess_min", repr(o["chain_ess_min"]))
    print("gate_pass", report["main"]["gate_pass"], json.dumps(report["main"]["checks"]))
    print("power_control", json.dumps(report["power_control"]["checks"]))


if __name__ == "__main__":
    main()
