"""SE audit v0.1 (docs/SPECTRAL_SE_AUDIT_PREREGISTRATION.md): batch calibration of the
tree-level delta SE of the annealed CAY window slope at N = 2^14.

Instrument diagnosis only. Engineering runs never use the audit seed base. Audit seed
use requires spectral_s1.SE_AUDIT_RUN_AUTHORIZED (False in this implementation; a
separately reviewed run-authorization change must flip it), SE_AUDIT_ALLOW_SEEDS=1,
and the Linux containment guard. Nothing here unlocks S2.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import time
from pathlib import Path

import numpy as np
from scipy import stats

from emergence_lab import spectral_s1 as s1
from emergence_lab.dimension_d2 import CAY
from emergence_lab.spectral_s1b import Budget, append_event, write_json

CONFIG = Path("configs/spectral_se_audit.json")
PREREG = Path("docs/SPECTRAL_SE_AUDIT_PREREGISTRATION.md")
ENGINEERING_SEED = 2036101997
R_CRIT_FROZEN = 1.313
GIB = 1024 ** 3
REJECTED, NOT_REJECTED, BLOCKED = "SE-REJECTED", "SE-NOT-REJECTED", "BLOCKED"


def r_critical(batches: int, per_batch: int, alpha: float = .05) -> float:
    """sqrt of the upper-alpha F(B-1, B(m-1)) quantile (estimated denominator)."""
    return math.sqrt(float(stats.f.ppf(1 - alpha, batches - 1, batches * (per_batch - 1))))


def design(cfg: dict, engineering: bool = False) -> dict:
    """Reject drift from the reviewed v0.1 design."""
    k, st, b = cfg["kernel"], cfg["statistic"], cfg["budget"]
    if not (cfg["version"] == "0.1" and cfg["family"] == CAY and cfg["N"] == 2 ** 14
            and cfg["batches"] == 16 and cfg["trees_per_batch"] == 12 and cfg["sources"] == 32
            and cfg["T"] == 4096 and cfg["ladder"] is None and cfg["primary_window"] == [128, 1024]
            and k["eta"] == 1e-4 and k["R_start"] == 64 and k["per_source_edge_step_cap"] == 2_000_000_000
            and cfg["seed_base"] == s1.SE_AUDIT_SEED_BASE
            and cfg["engineering_seed_base"] == ENGINEERING_SEED
            and st["alpha"] == .05 and st["R_crit"] == R_CRIT_FROZEN
            and round(r_critical(16, 12), 3) == R_CRIT_FROZEN
            and cfg["outcomes"]["full_samples_required"] is True
            and b["cores"] == 1 and b["memory_GiB"] == 2 and b["projected_cpu_min"] == 53
            and b["hard_stop_total_cpu_min"] == 100 and b["host"] == "not Lightsail"):
        raise ValueError("SE-audit config differs from reviewed v0.1")
    d = {"mode": "se_audit", "seed_base": cfg["seed_base"], "N": cfg["N"],
         "batches": 16, "per_batch": 12, "sources": 32, "T": cfg["T"],
         "window": list(cfg["primary_window"]), "eta": k["eta"], "r_start": k["R_start"],
         "edge_step_cap": k["per_source_edge_step_cap"], "r_crit": R_CRIT_FROZEN,
         "total_cpu_s": 100 * 60., "max_memory_bytes": 2 * GIB}
    if engineering:
        d.update(mode="engineering", seed_base=ENGINEERING_SEED, N=128, batches=4,
                 per_batch=3, sources=4, T=32, window=[4, 32], r_start=8,
                 r_crit=r_critical(4, 3), total_cpu_s=120.)
    return d


def schedule(d: dict) -> list[dict]:
    """Tree-major order; batch membership is fixed by i_tree, never re-formed."""
    m = d["per_batch"]
    return [{"family": CAY, "size": d["N"], "i_size": 0, "i_rep": i, "batch": i // m,
             "seed": [d["seed_base"], s1.FAMILY_ORDER.index(CAY), 0, i]}
            for i in range(d["batches"] * m)]


def classify(r: float, r_crit: float) -> str:
    if not (math.isfinite(r) and math.isfinite(r_crit) and r >= 0 and r_crit > 0):
        return BLOCKED
    return REJECTED if r > r_crit else NOT_REJECTED


def batch_statistic(Q: np.ndarray, batches: int, per_batch: int, lo: int, hi: int,
                    times: list[int]) -> dict:
    """Q: (B*m) trees x times, row i = tree i. Returns d_b, SE_b and R (prereg § 2)."""
    Q = np.asarray(Q, dtype=float)
    if Q.shape[0] != batches * per_batch:
        raise ValueError("Q must contain exactly B*m trees")
    blocks = Q.reshape(batches, per_batch, Q.shape[1])
    d_b = np.array([s1.annealed_window_slope(q, lo, hi, times) for q in blocks])
    psi = [s1.tree_influences(q, lo, hi, times) for q in blocks]
    se_b = np.array([np.std(p, ddof=1) / math.sqrt(per_batch) for p in psi])
    denom = math.sqrt(float(np.mean(se_b ** 2)))
    r = float(np.std(d_b, ddof=1) / denom) if denom > 0 else float("nan")
    s_psi = math.sqrt(float(np.mean([np.var(p, ddof=1) for p in psi])))
    return {"d_b": d_b, "se_b": se_b, "R": r, "rms_se": denom, "psi_pooled_sd": s_psi,
            "psi": np.concatenate(psi)}


def _descriptives(Q: np.ndarray, st: dict, d: dict, times: list[int]) -> dict:
    """Prereg § 2 descriptive outputs. None of these enters the decision."""
    lo, hi = d["window"]
    B, m = d["batches"], d["per_batch"]
    df = B * (m - 1)
    s = st["psi_pooled_sd"]
    psi_all = s1.tree_influences(Q, lo, hi, times)
    delta = float(np.std(psi_all, ddof=1) / math.sqrt(len(Q)))
    loo = np.array([s1.annealed_window_slope(np.delete(Q, k, axis=0), lo, hi, times)
                    for k in range(len(Q))])
    jk = float(np.sqrt((len(Q) - 1) / len(Q) * np.sum((loo - loo.mean()) ** 2)))
    z = np.sort((st["d_b"] - st["d_b"].mean()) / st["rms_se"])
    nq = stats.norm.ppf((np.arange(1, B + 1) - .375) / (B + .25))

    def shape(x):
        return {"cv": float(np.std(x, ddof=1) / np.mean(x)), "skew": float(stats.skew(x)),
                "excess_kurtosis": float(stats.kurtosis(x))}

    qlo, qhi = Q[:, times.index(lo)], Q[:, times.index(hi)]
    return {
        "pooled_psi_sd": s, "pooled_psi_sd_df": df,
        "pooled_psi_sd_ci90": [s * math.sqrt(df / stats.chi2.ppf(.95, df)),
                               s * math.sqrt(df / stats.chi2.ppf(.05, df))],
        "cv_se_b": float(np.std(st["se_b"], ddof=1) / np.mean(st["se_b"])),
        "cv_se_b_normal_reference": 1 / math.sqrt(2 * (m - 1)),
        "all_trees_slope": s1.annealed_window_slope(Q, lo, hi, times),
        "all_trees_delta_se": delta, "all_trees_jackknife_se": jk,
        "jackknife_delta_ratio": jk / delta if delta > 0 else float("nan"),
        "q_lo": shape(qlo), "q_hi": shape(qhi),
        "corr_ln_q_lo_hi": float(np.corrcoef(np.log(qlo), np.log(qhi))[0, 1]),
        "qq_standardized_batch_deviations": {
            "sorted_z": z, "normal_quantiles": nq,
            "max_abs_gap": float(np.max(np.abs(z - nq))),
            "corr": float(np.corrcoef(z, nq)[0, 1])},
        "note": "descriptive only; the pooled slope is not compared with 4/3 as a calibration verdict",
    }


def _certified(r: dict, eta: float) -> bool:
    res = r["res"]
    return bool(res.status == "OK" and np.all(np.isfinite(res.killed)) and np.all(res.killed >= 0)
                and res.killed[-1] <= eta * res.q_lower[-1] and s1.even_time_monotone(res.q_lower))


def analyze(d: dict, records: list, controls_passed: bool = True, budget_ok: bool = True) -> dict:
    """Full-sample gate precedes inference; no tree is dropped or replaced."""
    times = s1.dyadic_half_times(d["T"])
    lo, hi = d["window"]
    n_trees = d["batches"] * d["per_batch"]
    groups: dict[int, list] = {}
    for r in records:
        groups.setdefault(r["i_rep"], []).append(r)
    complete, invalid = [], []
    for i in range(n_trees):
        g = groups.get(i, [])
        ok = (len(g) == d["sources"] and len({r["res"].source for r in g}) == d["sources"]
              and all(_certified(r, d["eta"]) for r in g))
        (complete if ok else invalid).append(i)
    stray = sorted(set(groups) - set(range(n_trees)))
    out = {"verdict": BLOCKED, "r_crit": d["r_crit"], "n_complete_trees": len(complete),
           "invalid_trees": invalid, "stray_trees": stray, "controls_passed": controls_passed,
           "budget_ok": budget_ok}
    reasons = [x for x, bad in (("controls", not controls_passed), ("budget", not budget_ok),
                                ("incomplete_or_uncertified", bool(invalid)),
                                ("stray_trees", bool(stray))) if bad]
    if reasons:
        out["blocked_reasons"] = reasons
        return out
    ix = [t - 1 for t in times]
    Q = np.array([np.mean([r["res"].q_lower[ix] for r in groups[i]], axis=0)
                  for i in range(n_trees)])
    blocks = Q.reshape(d["batches"], d["per_batch"], len(times)).mean(axis=1)
    if not (np.all(np.isfinite(Q)) and np.all(blocks > 0)):
        out["blocked_reasons"] = ["non_finite_or_non_positive_batch_mean"]
        return out
    st = batch_statistic(Q, d["batches"], d["per_batch"], lo, hi, times)
    out.update(R=st["R"], d_b=st["d_b"], se_b=st["se_b"], rms_se=st["rms_se"],
               verdict=classify(st["R"], d["r_crit"]))
    if out["verdict"] == BLOCKED:
        out["blocked_reasons"] = ["non_finite_statistic"]
        return out
    out["descriptive"] = _descriptives(Q, st, d, times)
    out["wording"] = ("SE model not rejected at N=2^14 (not 'validated'; 2^16-2^18 uncertified)"
                      if out["verdict"] == NOT_REJECTED else
                      "SE model rejected at N=2^14: option C (new estimator) per decision record")
    return out


def authorize(d: dict):
    if d["mode"] == "se_audit" or d["seed_base"] == s1.SE_AUDIT_SEED_BASE:
        if not s1.SE_AUDIT_RUN_AUTHORIZED or os.environ.get("SE_AUDIT_ALLOW_SEEDS") != "1":
            raise PermissionError("SE-audit run locked until a reviewed run authorization")
    elif d["mode"] != "engineering" or d["seed_base"] != ENGINEERING_SEED:
        raise ValueError("engineering must use the disjoint engineering seed")


def run(d: dict, outdir: Path, root: Path = Path("."), *, controls=True) -> dict:
    authorize(d)  # Before mkdir, P0 or any generator; also enforced in build_instance.
    if d["mode"] == "se_audit":
        if d != design(json.loads((root / CONFIG).read_text())):
            raise ValueError("full SE-audit design drift")
        if not controls:
            raise ValueError("SE audit requires all P0 controls")
        from emergence_lab.s1b_limits import ResourceGuard
        with ResourceGuard(outdir, d["total_cpu_s"], d["max_memory_bytes"]):
            return _run(d, outdir, root, controls=True)
    return _run(d, outdir, root, controls=controls)


def _run(d: dict, outdir: Path, root: Path, *, controls=True) -> dict:
    authorize(d)
    outdir.mkdir(parents=True, exist_ok=False)
    budget = Budget(d["total_cpu_s"])
    plan = schedule(d)
    manifest = s1.manifest(root)
    if d["mode"] == "se_audit" and (len(manifest["commit"]) != 40
                                    or any(c not in "0123456789abcdef" for c in manifest["commit"])):
        raise ValueError("full SE audit requires traceable code revision")
    manifest.update(
        config_sha256=hashlib.sha256((root / CONFIG).read_bytes()).hexdigest(),
        prereg_sha256=hashlib.sha256((root / PREREG).read_bytes()).hexdigest(),
        seed_tuples_planned=[j["seed"] for j in plan], seed_tuples_attempted=[], mode=d["mode"],
        source_protocol="dimension_d1._seed_seq: graph uses ss, sources use ss.spawn(1)[0]",
        source_sha256={p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in
                       ("src/emergence_lab/spectral_se_audit.py", "src/emergence_lab/spectral_s1.py",
                        "src/emergence_lab/spectral_s1b.py", "src/emergence_lab/dimension_d1.py",
                        "src/emergence_lab/dimension_d2.py", "src/emergence_lab/s1b_limits.py")},
        run_status="STARTED", caveat="instrument diagnosis; nominal F reference, not physical evidence")
    write_json(outdir / "manifest.json", manifest)
    p0 = s1.run_p0(root) if controls else {"pass": False, "skipped_engineering_only": True}
    write_json(outdir / "controls.json", p0)
    controls_passed = bool(p0.get("pass"))
    proceed = controls_passed or (d["mode"] == "engineering" and not controls)
    records, events, ok = [], [], True
    header = s1.CSV_HEADER + ["T"] + [f"q_t{t}" for t in s1.dyadic_half_times(d["T"])]
    with (outdir / "numeric.csv").open("w", newline="", encoding="utf-8") as numeric:
        writer = csv.writer(numeric, lineterminator="\n")
        writer.writerow(header)
        for job in plan if proceed else []:
            if budget.exceeded() or not ok:
                ok = False
                break
            event = dict(job, status="STARTED", sources_finished=0)
            # Persist the attempt BEFORE graph/source RNG. A crash forbids seed reuse.
            append_event(outdir / "attempts.jsonl", event)
            manifest["seed_tuples_attempted"].append(job["seed"])
            write_json(outdir / "manifest.json", manifest)
            c0, w0 = budget.cpu(), time.perf_counter()
            try:
                g, srcs = s1.build_instance(CAY, job["size"], 0, job["i_rep"], d["sources"], d["seed_base"])
                event["sources"] = srcs.tolist()
                for v in srcs.tolist():
                    if budget.exceeded():
                        event["status"] = "PARTIAL"
                        break
                    sc, sw = budget.cpu(), time.perf_counter()
                    r = s1.certified_returns(g, v, d["T"], eta=d["eta"], r_start=d["r_start"],
                                             edge_step_cap=d["edge_step_cap"])
                    append_event(outdir / "sources.jsonl", dict(
                        job, source=v, status=r.status, cpu_s=budget.cpu() - sc,
                        wall_s=time.perf_counter() - sw, R=r.R, ball_size=r.ball_size,
                        edge_steps=r.edge_steps, relative_bracket=r.relative_bracket()))
                    records.append(dict(job, n=g.n, res=r))
                    vals = s1.rows_csv([(CAY, job["size"], 0, job["i_rep"], r)], d["T"]).decode().splitlines()[1].split(",")
                    writer.writerow(vals[:len(s1.CSV_HEADER)] + [d["T"]] + vals[len(s1.CSV_HEADER):])
                    numeric.flush()
                    os.fsync(numeric.fileno())
                    event["sources_finished"] += 1
                    if r.status != "OK":
                        event["status"] = "OVER_CAP"
                        break
                else:
                    event["status"] = "COMPLETED"
            except (ArithmeticError, MemoryError, ValueError, AssertionError) as exc:
                event.update(status="FAILED", error=type(exc).__name__ + ": " + str(exc))
            finally:
                # Per-tree CPU is logged so a budget stop is diagnosable (later-pass note 1).
                event.update(cpu_s=budget.cpu() - c0, wall_s=time.perf_counter() - w0)
                if event["status"] != "COMPLETED" or budget.exceeded():
                    ok = False
                events.append(event)
                append_event(outdir / "attempts.jsonl", event)
    analysis_start = budget.cpu()
    result = analyze(d, records, controls_passed, budget_ok=not budget.exceeded())
    result["analysis_cpu_s"] = budget.cpu() - analysis_start
    budget_ok = not budget.exceeded()
    if not budget_ok:  # Analysis CPU also counts; a final overrun vetoes the verdict.
        result["verdict"] = BLOCKED
        result.setdefault("blocked_reasons", []).append("budget")
    report = dict(mode=d["mode"], design=d, controls_passed=controls_passed, cpu_s=budget.used(),
                  budget_ok=budget_ok, attempts=events, result=result, s2_run_authorized=False)
    write_json(outdir / "report.json", report)
    manifest.update(run_status="FINISHED" if result["verdict"] != BLOCKED else "BLOCKED",
                    cpu_s=budget.used(),
                    outputs={p: hashlib.sha256((outdir / p).read_bytes()).hexdigest()
                             for p in ("numeric.csv", "controls.json", "report.json",
                                       "attempts.jsonl", "sources.jsonl") if (outdir / p).exists()})
    write_json(outdir / "manifest.json", manifest)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mode", choices=["engineering", "se_audit"], default="engineering")
    parser.add_argument("--no-controls", action="store_true", help="engineering only")
    args = parser.parse_args(argv)
    if args.no_controls and args.mode != "engineering":
        parser.error("--no-controls is engineering only")
    d = design(json.loads(CONFIG.read_text()), engineering=args.mode == "engineering")
    result = run(d, args.output, controls=not args.no_controls)
    print(json.dumps({"verdict": result["result"]["verdict"], "R": result["result"].get("R")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
