"""Preregistered many-batch coverage gate (Phase-0 report gate 4).

See docs/COVERAGE_GATE_PREREGISTRATION.md. For each lattice size, independent
batches of randomly started checkerboard-Metropolis chains (the sampler of
``critical_gate``) are summarized by a Student-t interval over the batch's chain
means; the fraction of batches whose nominal 95 % interval contains the exact
finite-torus energy per spin (Kaufman/Beale, ``exact_finite``) is the primary
observable. Chains are recorded from sweep 0, so the discarded warmup segment is
kept in the raw data and supplies the prespecified power control.

This module only evaluates criteria fixed in the config and the preregistration.
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
from scipy import stats as sps

from . import convergence as cv
from .coverage4 import wilson_interval
from .critical_gate import run_chain
from .exact_finite import exact_energy_per_spin
from .stats import independent_chain_interval

Z975 = 1.959963984540054
KEYS = {"sizes", "temperature", "batches", "chains_per_batch", "base_seed", "warmup_sweeps",
        "sample_sweeps", "sample_every", "power_control_sweeps", "max_proposals", "criteria"}
CRITERIA = {"wilson_halfwidth_max", "wilson_lower_min", "bias_z_flag"}


def seed_for(cfg: dict, size_index: int, batch: int, chain: int) -> int:
    return cfg["base_seed"] + size_index * 100_000 + batch * 10 + chain


def validate_config(cfg: dict) -> int:
    if set(cfg) - {"description"} != KEYS or set(cfg["criteria"]) != CRITERIA:
        raise ValueError("unexpected or missing config keys")
    sizes, nb, k, every = cfg["sizes"], cfg["batches"], cfg["chains_per_batch"], cfg["sample_every"]
    if (not sizes or len(set(sizes)) != len(sizes) or len(sizes) > 9
            or any(type(L) is not int or L % 2 or not 4 <= L <= 64 for L in sizes)
            or type(nb) is not int or not 10 <= nb <= 1000
            or type(k) is not int or not 3 <= k <= 9
            or type(cfg["base_seed"]) is not int
            or not math.isfinite(cfg["temperature"]) or cfg["temperature"] <= 0
            or type(every) is not int or every < 1
            or cfg["warmup_sweeps"] % every or cfg["sample_sweeps"] % every
            or cfg["power_control_sweeps"] % every
            or not 0 < cfg["power_control_sweeps"] <= cfg["warmup_sweeps"]
            or cfg["sample_sweeps"] < 10 * every):
        raise ValueError("invalid coverage-gate design")
    seeds = [seed_for(cfg, i, b, c) for i in range(len(sizes)) for b in range(nb) for c in range(k)]
    if len(set(seeds)) != len(seeds):
        raise ValueError("seed collision")
    sweeps = cfg["warmup_sweeps"] + cfg["sample_sweeps"]
    proposals = sum(nb * k * L * L * sweeps for L in sizes)
    if proposals > cfg["max_proposals"] or cfg["max_proposals"] > 10_000_000_000:
        raise ValueError("coverage-gate budget exceeded")
    return proposals


def binomial_two_sided_p(k: int, n: int, p: float) -> float:
    return float(sps.binomtest(k, n, p).pvalue)


def batch_coverage(chain_means: np.ndarray, reference: float | None) -> dict:
    """(batches, chains) chain means -> per-batch t intervals and their coverage."""
    rows = [independent_chain_interval(list(r)) for r in chain_means]
    means = np.array([r[0] for r in rows])
    ses = [r[1] for r in rows]
    out = {"batch_means": means.tolist(), "batch_stderr": ses,
           "undefined_intervals": int(sum(s is None for s in ses))}
    defined = np.array([s for s in ses if s is not None], dtype=float)
    # Reference-free calibration: spread of batch means vs. the reported standard errors.
    out["sd_batch_means_over_rms_stderr"] = (
        float(means.std(ddof=1) / math.sqrt(np.mean(defined ** 2))) if len(defined) > 1 else None)
    if reference is not None:
        hits = [r[1] is not None and r[2] <= reference <= r[3] for r in rows]
        n, c = len(hits), int(sum(hits))
        lo, hi = wilson_interval(c, n)
        out.update({"covered": c, "batches": n, "coverage": c / n, "wilson95": [lo, hi],
                    "wilson_halfwidth": (hi - lo) / 2,
                    "binomial_p_vs_0.95": binomial_two_sided_p(c, n, 0.95),
                    "covered_flags": [bool(h) for h in hits]})
    return out


def per_chain_coverage(series: np.ndarray, reference: float) -> dict:
    """Secondary: mean +- 1.96 sd/sqrt(Geyer ESS) per chain, against the exact reference."""
    hits, undefined, ess = 0, 0, []
    for row in series:
        est = cv.chain_ess(row)
        if not est["ess"]:
            undefined += 1
            continue
        ess.append(est["ess"])
        half = Z975 * float(row.std(ddof=1)) / math.sqrt(est["ess"])
        hits += abs(float(row.mean()) - reference) <= half
    n = len(series)
    lo, hi = wilson_interval(hits, n)
    return {"covered": int(hits), "chains": n, "undefined": undefined, "coverage": hits / n,
            "wilson95": [lo, hi], "ess_median": float(np.median(ess)) if ess else None,
            "ess_min": float(min(ess)) if ess else None}


def evaluate_size(energy: np.ndarray, absm: np.ndarray, cfg: dict, reference: float,
                  first: int, last: int | None) -> dict:
    """energy/absm: (batches, chains, draws); window [first:last) in draws."""
    crit = cfg["criteria"]
    e, m = energy[:, :, first:last], absm[:, :, first:last]
    e_cov = batch_coverage(e.mean(axis=2), reference)
    m_cov = batch_coverage(m.mean(axis=2), None)
    chain_means = e.mean(axis=2).ravel()
    pooled = float(chain_means.mean())
    pooled_se = float(chain_means.std(ddof=1) / math.sqrt(chain_means.size))
    bias_z = (pooled - reference) / pooled_se
    checks = {"C1_wilson_halfwidth": e_cov["wilson_halfwidth"] < crit["wilson_halfwidth_max"],
              "C2_wilson_lower": e_cov["wilson95"][0] >= crit["wilson_lower_min"]}
    return {"draws_per_chain": int(e.shape[2]), "exact_energy": reference,
            "energy": e_cov, "abs_magnetization": m_cov,
            "pooled_energy": pooled, "pooled_energy_stderr": pooled_se, "bias_z": bias_z,
            "bias_flag": abs(bias_z) > crit["bias_z_flag"],
            "checks": checks, "pass": bool(all(checks.values()))}


def _job(args):
    L, T, sweeps, every, seed = args
    c = run_chain(L, T, 0, sweeps, every, seed, "random")
    return c["energy_sum"], c["magnetization_sum"]


def run_gate(cfg: dict, workers: int = 1):
    proposals = validate_config(cfg)
    T, nb, k, every = float(cfg["temperature"]), cfg["batches"], cfg["chains_per_batch"], cfg["sample_every"]
    sweeps = cfg["warmup_sweeps"] + cfg["sample_sweeps"]
    w, pc = cfg["warmup_sweeps"] // every, cfg["power_control_sweeps"] // every
    t0, c0 = time.time(), time.process_time()
    raw_arrays, results = {}, {}
    for si, L in enumerate(cfg["sizes"]):
        jobs = [(L, T, sweeps, every, seed_for(cfg, si, b, c)) for b in range(nb) for c in range(k)]
        if workers > 1:
            with ProcessPoolExecutor(workers) as ex:
                out = list(ex.map(_job, jobs, chunksize=8))
        else:
            out = [_job(j) for j in jobs]
        e_sum = np.stack([o[0] for o in out]).reshape(nb, k, -1)
        m_sum = np.stack([o[1] for o in out]).reshape(nb, k, -1)
        raw_arrays[f"energy_sum_L{L}"] = e_sum
        raw_arrays[f"magnetization_sum_L{L}"] = m_sum
        n = L * L
        energy, absm = e_sum / n, np.abs(m_sum) / n
        ref = exact_energy_per_spin(T, L)["energy_per_spin"]
        main = evaluate_size(energy, absm, cfg, ref, w, None)
        main["per_chain_energy"] = per_chain_coverage(energy[:, :, w:].reshape(nb * k, -1), ref)
        control = evaluate_size(energy, absm, cfg, ref, 0, pc)
        for part in ("energy", "abs_magnetization"):
            for key in ("batch_means", "batch_stderr", "covered_flags"):
                control[part].pop(key, None)
        results[str(L)] = {"main": main, "power_control": control}
    wall = time.time() - t0
    buf = io.BytesIO()
    np.savez_compressed(buf, **raw_arrays)
    raw = buf.getvalue()
    report = {
        "config": cfg,
        "config_sha256": hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest(),
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "commit": os.getenv("GIT_SHA"), "workers": workers,
                        "wall_seconds": wall, "parent_cpu_seconds": time.process_time() - c0},
        "proposals": proposals,
        "seed_rule": "base_seed + size_index*100000 + batch*10 + chain; random starts",
        "raw_npz_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_digests": {name: hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
                        for name, a in raw_arrays.items()},
        "sizes": results,
        "gate_pass": bool(all(r["main"]["pass"] for r in results.values())),
        "power_control_expected": "C2 fails at every size; a pass is reported as non-discriminating",
        "caveats": [
            "Only the energy per spin has an exact finite-L reference; |m| gets a reference-free spread ratio only.",
            "One temperature (rounded Tc), one sampler, random starts only.",
            "Coverage of wide 4-chain t intervals is insensitive to biases well below their half-width; see bias_z.",
            "Independence of chains rests on distinct PCG64 seeds, not on a proof.",
        ],
    }
    return report, raw


def main():
    p = argparse.ArgumentParser(description="Preregistered many-batch coverage gate")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True, help="JSON report; raw .npz written alongside")
    p.add_argument("--workers", type=int, default=1)
    args = p.parse_args()
    report, raw = run_gate(json.loads(args.config.read_text()), args.workers)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".npz").write_bytes(raw)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print("raw_npz_sha256", report["raw_npz_sha256"])
    for L, r in report["sizes"].items():
        m, c = r["main"], r["power_control"]
        print(f"L={L} covered {m['energy']['covered']}/{m['energy']['batches']} "
              f"wilson95={m['energy']['wilson95']} bias_z={m['bias_z']:.3f} "
              f"ratioE={m['energy']['sd_batch_means_over_rms_stderr']:.3f} "
              f"ratioM={m['abs_magnetization']['sd_batch_means_over_rms_stderr']:.3f} "
              f"per_chain={m['per_chain_energy']['covered']}/{m['per_chain_energy']['chains']} "
              f"pass={m['pass']} | control covered {c['energy']['covered']} pass={c['pass']}")
    print("gate_pass", report["gate_pass"])


if __name__ == "__main__":
    main()
