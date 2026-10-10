"""Preregistered finite-size gate, Phase-0 report gate 5.

See docs/FINITE_SIZE_GATE_PREREGISTRATION.md. Checkerboard Metropolis chains
(``critical_gate.run_chain``, unchanged) from random and ordered starts at
L = 8..48 near Tc; between-chain (leave-one-chain-out jackknife) uncertainties;
weighted log-log fits for beta/nu, gamma/nu and 1/nu compared against the exact
2D Ising values with a preregistered tolerance; exact finite-torus energy and
specific heat as absolute per-size checks; an off-critical Ising control and an
i.i.d. J = 0 control that the same fit rule must reject. Criteria are fixed in
the config; this module only evaluates them.
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
from .critical_gate import STARTS, _welch, run_chain
from .exact_finite import exact_energy_per_spin
from .stats import independent_chain_interval

EXPONENTS = ("beta_over_nu", "gamma_over_nu", "one_over_nu")
# observable whose log-log slope estimates each exponent, and the sign convention
FIT_OBSERVABLE = {"beta_over_nu": ("abs_m", -1.0), "gamma_over_nu": ("chi", 1.0),
                  "one_over_nu": ("dlnm_dK", 1.0)}
CONFIG_KEYS = {"temperature", "sizes", "chains_per_start", "base_seed", "warmup_sweeps",
               "sample_sweeps", "sample_every", "max_proposals", "primary_window",
               "stability_windows", "exact_exponents", "criteria", "controls"}


def seed_for(base: int, size_index: int, start_index: int, rep: int) -> int:
    return base + size_index * 100000 + start_index * 1000 + rep


def _sweeps(cfg: dict, L: int) -> int:
    s = cfg["sample_sweeps"]
    return int(s[str(L)]) if isinstance(s, dict) else int(s)


def validate_config(cfg: dict) -> int:
    if set(cfg) - {"description"} != CONFIG_KEYS:
        raise ValueError("unexpected or missing config keys")
    sizes, reps, every = cfg["sizes"], cfg["chains_per_start"], cfg["sample_every"]
    if (not sizes or sorted(set(sizes)) != sizes
            or any(type(L) is not int or L % 2 or not 4 <= L <= 64 for L in sizes)
            or type(reps) is not int or not 2 <= reps <= 32 or type(every) is not int or every < 1
            or not math.isfinite(cfg["temperature"]) or cfg["temperature"] <= 0
            or cfg["warmup_sweeps"] < 0):
        raise ValueError("invalid gate design")
    for L in sizes:
        if _sweeps(cfg, L) < every or _sweeps(cfg, L) % every:
            raise ValueError("invalid sample sweeps")
    for w in [cfg["primary_window"], *cfg["stability_windows"]]:
        if len(w) < 3 or not set(w) <= set(sizes):
            raise ValueError("fit window must use >= 3 simulated sizes")
    if set(cfg["exact_exponents"]) != set(EXPONENTS) or set(cfg["criteria"]["tolerance"]) != set(EXPONENTS):
        raise ValueError("exponent keys")
    off = cfg["controls"]["off_critical"]
    proposals = sum(2 * reps * L * L * (cfg["warmup_sweeps"] + _sweeps(cfg, L)) for L in sizes)
    proposals += sum(2 * off["chains_per_start"] * L * L * (off["warmup_sweeps"] + off["sample_sweeps"])
                     for L in sizes)
    if proposals > cfg["max_proposals"] or cfg["max_proposals"] > 6_000_000_000:
        raise ValueError("gate budget exceeded")
    return proposals


# ---------------------------------------------------------------- estimators
def moments(e: np.ndarray, m: np.ndarray) -> dict:
    """Pooled per-spin moments over all draws of the given chains (rows)."""
    a = np.abs(m)
    m2 = m * m
    return {"e": float(e.mean()), "e2": float((e * e).mean()), "abs_m": float(a.mean()),
            "m2": float(m2.mean()), "m4": float((m2 * m2).mean()), "abs_m_e": float((a * e).mean())}


def derived(mo: dict, L: int, T: float) -> dict:
    n = L * L
    out = {"energy": mo["e"], "abs_m": mo["abs_m"],
           "chi": n * mo["m2"] / T,
           "chi_connected": n * (mo["m2"] - mo["abs_m"] ** 2) / T,
           "specific_heat": n * (mo["e2"] - mo["e"] ** 2) / T ** 2,
           "binder": 1.0 - mo["m4"] / (3.0 * mo["m2"] ** 2) if mo["m2"] > 0 else float("nan")}
    # d ln<|m|>/dK with K = 1/T and H = N e: = N (<e> - <|m| e>/<|m|>)
    out["dlnm_dK"] = n * (mo["e"] - mo["abs_m_e"] / mo["abs_m"]) if mo["abs_m"] > 0 else float("nan")
    return out


def _log(x: float) -> float:
    return math.log(x) if x > 0 else float("nan")


def jackknife(e: np.ndarray, m: np.ndarray, L: int, T: float) -> dict:
    """Leave-one-chain-out jackknife of derived quantities and of their logs."""
    k = e.shape[0]
    full = derived(moments(e, m), L, T)
    leave = [derived(moments(np.delete(e, i, 0), np.delete(m, i, 0)), L, T) for i in range(k)]
    out = {}
    for name, val in full.items():
        for key, f in ((name, lambda x: x), ("ln_" + name, _log)):
            th = np.array([f(d[name]) for d in leave])
            v = f(val)
            se = math.sqrt((k - 1) / k * float(((th - th.mean()) ** 2).sum())) if np.all(np.isfinite(th)) else float("nan")
            out[key] = {"value": v, "stderr": se}
    return out


def wls_slope(x, y, se) -> dict:
    """Weighted least squares y = a + b x; slope SE scaled by sqrt(max(1, chi2/dof))."""
    x, y, se = (np.asarray(v, float) for v in (x, y, se))
    if not (np.all(np.isfinite(y)) and np.all(np.isfinite(se)) and np.all(se > 0)):
        return {"slope": None, "stderr": None, "chi2_dof": None}
    w = 1.0 / se ** 2
    X = np.column_stack([np.ones_like(x), x])
    cov = np.linalg.inv(X.T @ (w[:, None] * X))
    a, b = cov @ (X.T @ (w * y))
    dof = len(x) - 2
    chi2 = float(np.sum(w * (y - a - b * x) ** 2))
    scale = math.sqrt(max(1.0, chi2 / dof)) if dof > 0 else 1.0
    return {"slope": float(b), "stderr": float(math.sqrt(cov[1, 1]) * scale),
            "stderr_unscaled": float(math.sqrt(cov[1, 1])), "chi2_dof": chi2 / dof if dof else None}


def fit_exponents(per_size: dict, window, cfg: dict) -> dict:
    crit = cfg["criteria"]
    out = {}
    for ex in EXPONENTS:
        obs, sign = FIT_OBSERVABLE[ex]
        rows = [per_size[str(L)]["jackknife"].get("ln_" + obs) for L in window]
        if any(r is None for r in rows):
            out[ex] = {"estimate": None, "pass": False}
            continue
        f = wls_slope([math.log(L) for L in window], [r["value"] for r in rows], [r["stderr"] for r in rows])
        if f["slope"] is None:
            out[ex] = {"estimate": None, "pass": False, **f}
            continue
        est = sign * f["slope"]
        dev = est - cfg["exact_exponents"][ex]
        allowed = crit["fit_sigma_multiplier"] * f["stderr"] + crit["tolerance"][ex]
        out[ex] = {"estimate": est, "stderr": f["stderr"], "stderr_unscaled": f["stderr_unscaled"],
                   "chi2_dof": f["chi2_dof"], "deviation": dev, "allowed": allowed,
                   "z_unscaled_no_tolerance": dev / f["stderr_unscaled"],
                   "pass": bool(abs(dev) <= allowed)}
    return out


# ---------------------------------------------------------------- simulation
def _chain_job(args):
    return run_chain(*args)


def iid_chain(size: int, draws: int, seed: int) -> dict:
    """Exact i.i.d. sampler for J = 0 (Metropolis is non-ergodic there)."""
    rng = np.random.default_rng(seed)
    e = np.empty(draws, dtype=np.int16)
    m = np.empty(draws, dtype=np.int16)
    for k in range(draws):
        s = 2 * rng.integers(0, 2, size=(size, size), dtype=np.int8) - 1
        e[k] = -int(np.sum(s * (np.roll(s, 1, 0) + np.roll(s, 1, 1))))
        m[k] = int(np.sum(s))
    return {"seed": seed, "start": "iid", "energy_sum": e, "magnetization_sum": m}


def _run(jobs, workers):
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            return list(ex.map(_chain_job, jobs))
    return [_chain_job(j) for j in jobs]


def simulate(cfg: dict, workers: int = 1) -> dict:
    T, reps, every = float(cfg["temperature"]), cfg["chains_per_start"], cfg["sample_every"]
    off, j0 = cfg["controls"]["off_critical"], cfg["controls"]["j0_iid"]
    jobs, keys = [], []
    for li, L in enumerate(cfg["sizes"]):
        for si, start in enumerate(STARTS):
            for r in range(reps):
                jobs.append((L, T, cfg["warmup_sweeps"], _sweeps(cfg, L), every,
                             seed_for(cfg["base_seed"], li, si, r), start))
                keys.append(("main", L))
            for r in range(off["chains_per_start"]):
                jobs.append((L, float(off["temperature"]), off["warmup_sweeps"], off["sample_sweeps"],
                             off["sample_every"], seed_for(off["base_seed"], li, si, r), start))
                keys.append(("off_critical", L))
    # longest chains first for better load balance
    order = sorted(range(len(jobs)), key=lambda i: -jobs[i][0] ** 2 * (jobs[i][2] + jobs[i][3]))
    res = _run([jobs[i] for i in order], workers)
    chains = {}
    for i, c in zip(order, res):
        chains.setdefault(keys[i], []).append(c)
    for li, L in enumerate(cfg["sizes"]):
        chains[("j0_iid", L)] = [iid_chain(L, j0["draws"], seed_for(j0["base_seed"], li, 0, r))
                                 for r in range(j0["chains"])]
    for v in chains.values():
        v.sort(key=lambda c: c["seed"])
    return chains


# ---------------------------------------------------------------- evaluation
def analyse_set(chains: dict, label: str, sizes, T: float, cfg: dict, reference: bool) -> dict:
    crit = cfg["criteria"]
    per_size, checks = {}, {}
    for L in sizes:
        cs = chains[(label, L)]
        n = L * L
        e = np.stack([c["energy_sum"] for c in cs]) / n
        m = np.stack([c["magnetization_sum"] for c in cs]) / n
        jk = jackknife(e, m, L, T)
        r = {"chains": len(cs), "draws_per_chain": int(e.shape[1]), "jackknife": jk}
        means_e = e.mean(axis=1)
        mean, se, lo, hi = independent_chain_interval(list(means_e))
        r["energy_chain_interval"] = {"mean": mean, "stderr": se, "ci95": [lo, hi]}
        if reference:
            ex = exact_energy_per_spin(T, L)["energy_per_spin"]
            h = 1e-4
            c_ex = (exact_energy_per_spin(T + h, L)["energy_per_spin"]
                    - exact_energy_per_spin(T - h, L)["energy_per_spin"]) / (2 * h)
            z_e = (mean - ex) / se
            z_c = (jk["specific_heat"]["value"] - c_ex) / jk["specific_heat"]["stderr"]
            r.update(exact_energy=ex, z_energy_vs_exact=z_e, exact_specific_heat=c_ex,
                     z_specific_heat_vs_exact=z_c)
            checks[f"E1_energy_L{L}"] = bool(abs(z_e) <= crit["z_max_per_size"])
            checks[f"E2_specific_heat_L{L}"] = bool(abs(z_c) <= crit["z_max_per_size"])
            hot = np.array([c["start"] == "random" for c in cs])
            absm_means = np.abs(m).mean(axis=1)
            for name, arr, means in (("energy", e, means_e), ("abs_m", np.abs(m), absm_means)):
                d = {"rhat_bulk": cv.rhat_bulk(arr), "rhat_tail": cv.rhat_tail(arr),
                     "ess_bulk": cv.ess_bulk(arr), "ess_tail": cv.ess_tail(arr),
                     "hot_minus_cold": _welch(means[hot], means[~hot])}
                d["chain_tau_median_draws"] = float(np.median([cv.chain_ess(row)["tau"] or np.nan for row in arr]))
                r["diagnostics_" + name] = d
                rh = max(x for x in (d["rhat_bulk"], d["rhat_tail"]) if x is not None)
                es = min(x for x in (d["ess_bulk"], d["ess_tail"]) if x is not None)
                checks[f"M1_rhat_{name}_L{L}"] = bool(rh < crit["rhat_max"])
                checks[f"M2_ess_{name}_L{L}"] = bool(es >= crit["ess_bulk_tail_min"])
                z = d["hot_minus_cold"]["z"]
                checks[f"M3_hot_cold_{name}_L{L}"] = bool(z is not None and abs(z) <= crit["z_max_per_size"])
        per_size[str(L)] = r
    fits = {"primary": fit_exponents(per_size, cfg["primary_window"], cfg)}
    for i, w in enumerate(cfg["stability_windows"]):
        fits[f"stability_{i + 1}"] = fit_exponents(per_size, w, cfg)
    return {"per_size": per_size, "fits": fits, "checks": checks}


def evaluate(chains: dict, cfg: dict) -> dict:
    sizes = cfg["sizes"]
    main = analyse_set(chains, "main", sizes, float(cfg["temperature"]), cfg, True)
    for wname, f in main["fits"].items():
        for ex in EXPONENTS:
            main["checks"][f"X_{ex}_{wname}"] = f[ex]["pass"]
    controls = {}
    for label in ("off_critical", "j0_iid"):
        T = float(cfg["controls"][label]["temperature"])
        c = analyse_set(chains, label, sizes, T, cfg, False)
        prim = c["fits"]["primary"]
        c["rejected"] = bool(not prim["beta_over_nu"]["pass"] and not prim["gamma_over_nu"]["pass"])
        controls[label] = c
        main["checks"][f"C_{label}_rejected"] = c["rejected"]
    return {"main": main, "controls": controls, "gate_pass": bool(all(main["checks"].values()))}


def raw_npz(chains: dict) -> bytes:
    buf = io.BytesIO()
    arrays = {}
    for (label, L), cs in sorted(chains.items()):
        arrays[f"{label}_L{L}_energy_sum"] = np.stack([c["energy_sum"] for c in cs])
        arrays[f"{label}_L{L}_magnetization_sum"] = np.stack([c["magnetization_sum"] for c in cs])
        arrays[f"{label}_L{L}_seeds"] = np.array([c["seed"] for c in cs])
        arrays[f"{label}_L{L}_starts"] = np.array([c["start"] for c in cs])
    np.savez_compressed(buf, **arrays)
    return buf.getvalue()


def load_npz(data: bytes) -> dict:
    z = np.load(io.BytesIO(data))
    chains = {}
    for k in z.files:
        if k.endswith("_energy_sum"):
            label, Ls = k[: -len("_energy_sum")].rsplit("_L", 1)
            p = f"{label}_L{Ls}"
            chains[(label, int(Ls))] = [
                {"energy_sum": z[p + "_energy_sum"][i], "magnetization_sum": z[p + "_magnetization_sum"][i],
                 "seed": int(z[p + "_seeds"][i]), "start": str(z[p + "_starts"][i])}
                for i in range(z[p + "_seeds"].shape[0])]
    return chains


def build_report(cfg: dict, chains: dict, raw: bytes, env: dict) -> dict:
    result = evaluate(chains, cfg)
    return {
        "config": cfg,
        "config_sha256": hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest(),
        "environment": env, "proposals": validate_config(cfg),
        "raw_npz_sha256": hashlib.sha256(raw).hexdigest(),
        **result,
        "caveats": [
            "Gate tests recovery of known exponents to a stated accuracy, not a precision measurement.",
            "One sampler and lattice convention; T is 3e-7 below exact Tc.",
            "Exact references: finite-torus energy and its numerical T-derivative only; |m|, chi, Binder have none.",
            "Exponent tolerances absorb corrections to scaling by assumption; fits use no correction terms.",
        ],
    }


def main():
    p = argparse.ArgumentParser(description="Preregistered finite-size gate (report gate 5)")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True, help="JSON report; raw .npz written alongside")
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--reanalyse", type=Path, help="evaluate a saved .npz instead of simulating")
    args = p.parse_args()
    cfg = json.loads(args.config.read_text())
    validate_config(cfg)
    t0 = time.time()
    if args.reanalyse:
        raw = args.reanalyse.read_bytes()
        chains = load_npz(raw)
    else:
        chains = simulate(cfg, args.workers)
        raw = raw_npz(chains)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.with_suffix(".npz").write_bytes(raw)
    env = {"python": platform.python_version(), "numpy": np.__version__, "commit": os.getenv("GIT_SHA"),
           "workers": args.workers, "wall_seconds": time.time() - t0,
           "reanalysed_from": str(args.reanalyse) if args.reanalyse else None}
    report = build_report(cfg, chains, raw, env)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print("raw_npz_sha256", report["raw_npz_sha256"])
    for w, f in report["main"]["fits"].items():
        print(w, {k: (round(v["estimate"], 4) if v["estimate"] is not None else None, v["pass"]) for k, v in f.items()})
    failed = [k for k, v in report["main"]["checks"].items() if not v]
    print("gate_pass", report["gate_pass"], "failed_checks", failed)


if __name__ == "__main__":
    main()
