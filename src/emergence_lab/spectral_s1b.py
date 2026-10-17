"""Locked S1b v0.2 orchestration. Engineering runs never use S1b seeds.

This implementation does not authorize an S1b run. See S1B_RUN_AUTHORIZED in
spectral_s1; even an environment flag cannot activate the preregistered seeds.
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

from emergence_lab import spectral_s1 as s1
from emergence_lab.dimension_d2 import CAY, UST

FAMILIES = (CAY, UST)
CONFIG = Path("configs/spectral_s1b.json")
PREREG = Path("docs/SPECTRAL_S1B_PREREGISTRATION.md")
ENGINEERING_SEED = 2036101797
ENGINEERING_BOOTSTRAP = 2036101798
GIB = 1024 ** 3


def design(cfg: dict, engineering: bool = False) -> dict:
    """Reject drift of the preregistered allocation, estimand and stopping rules."""
    expected = {CAY: {"N": [16384, 65536, 262144], "trees": 24, "sources": 32},
                UST: {"L": [128, 256], "trees": 48, "sources": 32}}
    reliability = {"max_abs_influence_skew": 1.5, "max_squared_influence_share": .5,
                   "max_jackknife_to_delta_se_ratio": 1.25,
                   "require_positive_annealed_q": True, "require_finite_se_and_ci": True,
                   "require_certified_error": True, "min_headroom_per_source": 10,
                   "bootstrap_resamples": 4096}
    o, b = cfg["outcomes"], cfg["budget"]
    if not (cfg["version"] == "0.2" and cfg["families"] == expected
            and cfg["seed_base"] == s1.S1B_SEED_BASE and cfg["bootstrap_seed"] == 2036101799
            and cfg["family_index_order"] == list(FAMILIES)
            and cfg["T"] == 4096 and cfg["ladder"] is None
            and cfg["primary_window"] == [128, 1024]
            and cfg["kernel"]["eta"] == 1e-4 and cfg["kernel"]["R_start"] == 64
            and cfg["kernel"]["per_source_edge_step_cap"] == 2_000_000_000
            and o["margin"] == .03 and o["confidence_level"] == .9
            and o["full_samples_required"] is True and o["reliability"] == reliability
            and o["exact_trees_per_size"] == {CAY: 24, UST: 48}
            and o["primary_comparison"] == {"family": CAY, "larger": 262144, "smaller": 65536}
            and o["secondary_comparison"] == {"family": UST, "larger": 256, "smaller": 128}
            and b["cores"] == 1 and b["memory_GiB"] == 2
            and b["projected_cpu_min"] == 130 and b["hard_stop_total_cpu_min"] == 200
            and b["family_hard_stop_factor"] == 1.5 and b["host"] == "not Lightsail"):
        raise ValueError("S1b config differs from reviewed v0.2")
    d = {"mode": "s1b", "seed_base": cfg["seed_base"],
         "bootstrap_seed": cfg["bootstrap_seed"], "T": cfg["T"],
         "window": cfg["primary_window"], "eta": cfg["kernel"]["eta"],
         "r_start": cfg["kernel"]["R_start"],
         "edge_step_cap": cfg["kernel"]["per_source_edge_step_cap"],
         "families": {f: {"sizes": list(expected[f]["N" if f == CAY else "L"]),
                           "trees": expected[f]["trees"], "sources": 32} for f in FAMILIES},
         "margin": .03, "level": .9, "n_boot": 4096, "headroom": 10,
         "total_cpu_s": 12000., "family_cpu_s": {CAY: 105 * 60 * 1.5, UST: 23 * 60 * 1.5},
         "max_memory_bytes": 2 * GIB}
    if engineering:
        d.update(mode="engineering", seed_base=ENGINEERING_SEED,
                 bootstrap_seed=ENGINEERING_BOOTSTRAP, T=32, window=[4, 32],
                 r_start=8, n_boot=64, total_cpu_s=120.,
                 family_cpu_s={CAY: 100., UST: 100.},
                 families={CAY: {"sizes": [128, 256, 512], "trees": 8, "sources": 4},
                           UST: {"sizes": [12, 16], "trees": 8, "sources": 4}})
    return d


def schedule(d: dict) -> list[dict]:
    """Replicate-major order; size indices match the frozen lists, never sorted anew."""
    return [{"family": f, "size": size, "i_size": i, "i_rep": rep,
             "seed": [d["seed_base"], FAMILIES.index(f), i, rep]}
            for rep in range(max(d["families"][f]["trees"] for f in FAMILIES))
            for f in FAMILIES for i, size in enumerate(d["families"][f]["sizes"])
            if rep < d["families"][f]["trees"]]


def classify_ci(lo: float, hi: float, margin: float = .03) -> str:
    if not all(math.isfinite(x) for x in (lo, hi, margin)) or lo > hi or margin <= 0:
        return "UNRELIABLE"
    if lo > margin:
        return "MATERIAL-POSITIVE"
    if hi < -margin:
        return "MATERIAL-NEGATIVE"
    if lo > -margin and hi < margin:
        return "EQUIVALENT"
    return "INCONCLUSIVE"


def _clean(value):
    """Strict JSON, with invalid descriptive floats represented by null."""
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, dict):
        return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [_clean(v) for v in value]
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, (int, np.integer)):
        return int(value)
    return value


def write_json(path: Path, value):
    # Atomic report replacement; a killed run retains the prior checkpoint.
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(_clean(value), sort_keys=True, indent=2, allow_nan=False) + "\n")
    for attempt in range(5):
        try:
            tmp.replace(path)
            break
        except PermissionError:
            # Windows file indexing can briefly hold the destination. Keep the
            # prior checkpoint intact; never delete it to make replacement work.
            if os.name != "nt" or attempt == 4:
                raise
            time.sleep(.02)


def append_event(path: Path, value):
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(_clean(value), sort_keys=True, allow_nan=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


class Budget:
    """Includes completed P0 subprocess CPU, unlike process_time alone."""
    def __init__(self, total):
        self.total = total
        self.start = self.cpu()

    @staticmethod
    def cpu():
        child = 0.
        if os.name == "posix":
            import resource
            r = resource.getrusage(resource.RUSAGE_CHILDREN)
            child = r.ru_utime + r.ru_stime
        return time.process_time() + child

    def used(self):
        return self.cpu() - self.start

    def exceeded(self):
        return self.used() >= self.total


def _size_summary(d: dict, f: str, size: int, i_size: int, records: list) -> tuple[dict, np.ndarray]:
    times = s1.dyadic_half_times(d["T"])
    spec = d["families"][f]
    rows = [r for r in records if r["family"] == f and r["i_size"] == i_size]
    groups = {}
    for r in rows:
        groups.setdefault(r["i_rep"], []).append(r)
    complete, invalid = [], []
    for rep, group in sorted(groups.items()):
        valid = (0 <= rep < spec["trees"] and len(group) == spec["sources"]
                 and len({r["res"].source for r in group}) == spec["sources"]
                 and all(r["res"].status == "OK" for r in group))
        (complete if valid else invalid).append(rep)
    selected = [r for rep in complete for r in groups[rep]]
    ix = [t - 1 for t in times]
    Q = np.array([np.mean([r["res"].q_lower[ix] for r in groups[rep]], axis=0)
                  for rep in complete])
    out = {"size": size, "complete_reps": complete, "invalid_reps": invalid,
           "complete": complete == list(range(spec["trees"])) and not invalid,
           "n_trees": len(complete), "n_source_rows": len(rows)}
    if len(complete) < 2:
        return out, Q
    lo, hi = d["window"]
    finite_q = bool(np.all(np.isfinite(Q)) and np.all(Q > 0))
    out["positive_finite_q"] = finite_q
    if not finite_q:
        out["reliable"] = False
        return out, Q
    psi = s1.tree_influences(Q, lo, hi, times)
    rel = s1.projection_reliability(psi, Q.mean(axis=0))
    delta = float(np.std(psi, ddof=1) / math.sqrt(len(psi)))
    loo = np.array([s1.annealed_window_slope(np.delete(Q, k, axis=0), lo, hi, times)
                    for k in range(len(Q))])
    jk = float(np.sqrt((len(Q)-1)/len(Q) * np.sum((loo-loo.mean()) ** 2)))
    certified = all(np.all(np.isfinite(r["res"].killed))
                    and np.all(r["res"].killed >= 0)
                    and r["res"].killed[-1] <= d["eta"] * r["res"].q_lower[-1]
                    and s1.even_time_monotone(r["res"].q_lower)
                    for r in selected)
    headroom = min(r["res"].q_lower[hi-1] / (r["res"].degree/(r["n"]-1))
                   for r in selected)
    out.update(qbar=Q.mean(axis=0), influence=rel, delta_se=delta, jackknife_se=jk,
               jackknife_delta_ratio=jk/delta if delta > 0 else float("nan"),
               certified=bool(certified), headroom_min=float(headroom),
               windows={f"{a}-{b}": s1.annealed_window_slope(Q, a, b, times)
                        for a, b in s1.candidate_windows(d["T"])},
               q_t1=float(Q[:, 0].mean()),
               source_degree_1_fraction=float(np.mean([r["res"].degree == 1 for r in selected])))
    out["reliable"] = bool(rel["reliable"] and delta > 0 and np.isfinite(jk)
                           and jk <= 1.25*delta and certified and headroom >= d["headroom"])
    return out, Q


def analyze(d: dict, records: list, controls_passed: bool, global_ok: bool,
            family_ok: dict) -> dict:
    """Full cohort gate precedes all inference; never pool pilot data or drop bad trees."""
    authorize(d)  # Also protects the frozen bootstrap seed in this callable API.
    result = {}
    times = s1.dyadic_half_times(d["T"])
    lo, hi = d["window"]
    # Engineering bootstrap has its own base; no S1b bootstrap draw before activation.
    for f in FAMILIES:
        analysis_start = time.process_time()
        summaries, matrices = [], []
        for i, size in enumerate(d["families"][f]["sizes"]):
            summary, Q = _size_summary(d, f, size, i, records)
            summaries.append(summary)
            matrices.append(Q)
        out = {"sizes": summaries, "verdict": "BLOCKED", "ci": None}
        result[f] = out
        if not (controls_passed and global_ok and family_ok[f]
                and all(s["complete"] for s in summaries)):
            out["analysis_cpu_s"] = time.process_time()-analysis_start
            continue
        # S1 P3 screens are applied to EACH size, including descriptive CAY 2^14.
        if not all(s.get("reliable", False) for s in summaries):
            out["verdict"] = "UNRELIABLE"
        small, large = matrices[-2:]
        if not all(np.all(np.isfinite(q)) and np.all(q > 0) for q in (small, large)):
            out["verdict"] = "UNRELIABLE"
            out["analysis_cpu_s"] = time.process_time()-analysis_start
            continue
        contrast = s1.size_equivalence(small, large, lo, hi, times, d["margin"], d["level"])
        contrast["equivalent"] = classify_ci(*contrast["ci"], d["margin"]) == "EQUIVALENT"
        out.update(contrast=contrast, ci=contrast["ci"])
        out["jackknife_se"] = math.hypot(summaries[-2]["jackknife_se"], summaries[-1]["jackknife_se"])
        # Independent resampling for the two independent size cohorts, one fixed stream.
        rng = np.random.Generator(np.random.PCG64(d["bootstrap_seed"]))
        bs = []
        for Q in (small, large):
            idx = rng.integers(0, len(Q), size=(d["n_boot"], len(Q)))
            q = Q[idx].mean(axis=1)
            bs.append(-2 * (np.log(q[:, times.index(hi)]) - np.log(q[:, times.index(lo)])) / math.log(hi/lo))
        out["bootstrap_percentile_90"] = np.quantile(bs[1]-bs[0], [.05, .95])
        out["bootstrap_resamples"] = d["n_boot"]
        if out["verdict"] != "UNRELIABLE":
            out["verdict"] = classify_ci(*contrast["ci"], d["margin"])
        out["analysis_cpu_s"] = time.process_time()-analysis_start
    return result


def authorize(d: dict):
    if d["mode"] == "s1b" or d["seed_base"] == s1.S1B_SEED_BASE:
        if not s1.S1B_RUN_AUTHORIZED or os.environ.get("S1B_ALLOW_SEEDS") != "1":
            raise PermissionError("S1b run locked until separate implementation review and activation")
    elif d["mode"] != "engineering" or d["seed_base"] != ENGINEERING_SEED:
        raise ValueError("engineering must use the disjoint engineering seed")


def run(d: dict, outdir: Path, root: Path = Path("."), *, controls=True) -> dict:
    """Append-only attempted-seed ledger, per-source checkpoints, no overwrite/resume."""
    authorize(d)  # Before mkdir, P0 or any generator; also enforced in build_instance.
    if d["mode"] == "s1b":
        if d != design(json.loads((root/CONFIG).read_text())):
            raise ValueError("full S1b design drift")
        if not controls:
            raise ValueError("S1b requires all P0 controls")
        from emergence_lab.s1b_limits import ResourceGuard
        with ResourceGuard(outdir, d["total_cpu_s"], d["max_memory_bytes"]):
            return _run(d, outdir, root, controls=True)
    return _run(d, outdir, root, controls=controls)


def _run(d: dict, outdir: Path, root: Path, *, controls=True) -> dict:
    authorize(d)
    if d["mode"] == "s1b" and not controls:
        raise ValueError("S1b requires all P0 controls")
    # Fail on an existing directory even if a previous run crashed before its report.
    outdir.mkdir(parents=True, exist_ok=False)
    budget = Budget(d["total_cpu_s"])
    plan = schedule(d)
    manifest = s1.manifest(root)
    if d["mode"] == "s1b" and (len(manifest["commit"]) != 40
            or any(c not in "0123456789abcdef" for c in manifest["commit"])):
        raise ValueError("full S1b requires traceable code revision")
    manifest.update(config_sha256=hashlib.sha256((root/CONFIG).read_bytes()).hexdigest(),
                    prereg_sha256=hashlib.sha256((root/PREREG).read_bytes()).hexdigest(),
                    seed_tuples_planned=[j["seed"] for j in plan],
                    seed_tuples_attempted=[], mode=d["mode"], source_protocol="dimension_d1._seed_seq: graph uses ss, sources use ss.spawn(1)[0]",
                    source_sha256={p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in
                        ("src/emergence_lab/spectral_s1b.py", "src/emergence_lab/spectral_s1.py",
                         "src/emergence_lab/dimension_d1.py", "src/emergence_lab/dimension_d2.py",
                         "src/emergence_lab/s1b_limits.py")},
                    run_status="STARTED", caveat="nominal inference, not calibrated coverage or physical evidence")
    write_json(outdir/"manifest.json", manifest)
    p0 = s1.run_p0(root) if controls else {"pass": False, "skipped_engineering_only": True}
    write_json(outdir/"controls.json", p0)
    records, events = [], []
    costs = {f: 0. for f in FAMILIES}
    family_ok = {f: True for f in FAMILIES}
    controls_passed = bool(p0.get("pass"))
    # Engineering may exercise the scheduler without expensive controls, but never infer.
    proceed = controls_passed or (d["mode"] == "engineering" and not controls)
    header = s1.CSV_HEADER + ["T"] + [f"q_t{t}" for t in s1.dyadic_half_times(d["T"])]
    with (outdir/"numeric.csv").open("w", newline="", encoding="utf-8") as numeric:
        writer = csv.writer(numeric, lineterminator="\n")
        writer.writerow(header)
        for job in plan if proceed else []:
            f = job["family"]
            if budget.exceeded():
                break
            if not family_ok[f]:
                continue
            if costs[f] >= d["family_cpu_s"][f]:
                family_ok[f] = False
                continue
            event = dict(job, status="STARTED", sources_finished=0)
            # Persist the attempt BEFORE graph/source RNG. A crash forbids seed reuse.
            append_event(outdir/"attempts.jsonl", event)
            manifest["seed_tuples_attempted"].append(job["seed"])
            write_json(outdir/"manifest.json", manifest)
            c0, w0 = budget.cpu(), time.perf_counter()
            try:
                spec = d["families"][f]
                g, srcs = s1.build_instance(f, job["size"], job["i_size"], job["i_rep"], spec["sources"], d["seed_base"])
                event["sources"] = srcs.tolist()
                for v in srcs.tolist():
                    if budget.exceeded() or costs[f] + budget.cpu()-c0 >= d["family_cpu_s"][f]:
                        event["status"] = "PARTIAL"
                        break
                    source_cpu, source_wall = budget.cpu(), time.perf_counter()
                    r = s1.certified_returns(g, v, d["T"], eta=d["eta"], r_start=d["r_start"], edge_step_cap=d["edge_step_cap"])
                    append_event(outdir/"sources.jsonl", dict(job, source=v, status=r.status,
                        cpu_s=budget.cpu()-source_cpu, wall_s=time.perf_counter()-source_wall,
                        R=r.R, ball_size=r.ball_size, edge_steps=r.edge_steps,
                        relative_bracket=r.relative_bracket()))
                    records.append(dict(job, n=g.n, res=r))
                    vals = s1.rows_csv([(f, job["size"], job["i_size"], job["i_rep"], r)], d["T"]).decode().splitlines()[1].split(",")
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
                spent = budget.cpu()-c0
                costs[f] += spent
                event.update(cpu_s=spent, wall_s=time.perf_counter()-w0)
                if costs[f] >= d["family_cpu_s"][f] or budget.exceeded():
                    family_ok[f] = False
                    if event["status"] == "COMPLETED":
                        event["status"] = "PARTIAL"
                if event["status"] != "COMPLETED":
                    family_ok[f] = False
                events.append(event)
                append_event(outdir/"attempts.jsonl", event)
    global_ok = not budget.exceeded()
    results = analyze(d, records, controls_passed, global_ok, family_ok)
    for f, result in results.items():
        costs[f] += result["analysis_cpu_s"]
        if costs[f] >= d["family_cpu_s"][f]:
            family_ok[f] = False
            result["verdict"] = "BLOCKED"
    # Analysis/bootstrap CPU also counts; a final overrun vetoes every verdict.
    global_ok = not budget.exceeded()
    if not global_ok:
        for result in results.values():
            result["verdict"] = "BLOCKED"
    report = dict(mode=d["mode"], design=d, controls_passed=controls_passed,
                  cpu_s=budget.used(), global_budget_ok=global_ok, family_cpu_s=costs,
                  family_budget_ok=family_ok, attempts=events, families=results,
                  s2_run_authorized=False,
                  s2_design_may_be_drafted=d["mode"] == "s1b" and all(r["verdict"] == "EQUIVALENT" for r in results.values()))
    write_json(outdir/"report.json", report)
    manifest.update(run_status="FINISHED" if global_ok and all(family_ok.values()) and controls_passed else "PARTIAL", cpu_s=budget.used(),
                    outputs={p: hashlib.sha256((outdir/p).read_bytes()).hexdigest()
                             for p in ("numeric.csv", "controls.json", "report.json", "attempts.jsonl", "sources.jsonl")
                             if (outdir/p).exists()})
    write_json(outdir/"manifest.json", manifest)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mode", choices=["engineering", "s1b"], default="engineering")
    parser.add_argument("--no-controls", action="store_true", help="engineering only")
    parser.add_argument("--contained-engineering", action="store_true", help="exercise Linux containment on engineering seeds only")
    args = parser.parse_args(argv)
    d = design(json.loads(CONFIG.read_text()), engineering=args.mode == "engineering")
    if args.contained_engineering:
        if args.mode != "engineering":
            parser.error("--contained-engineering requires engineering mode")
        from emergence_lab.s1b_limits import ResourceGuard
        with ResourceGuard(args.output, d["total_cpu_s"], d["max_memory_bytes"]):
            result = run(d, args.output, controls=not args.no_controls)
    else:
        result = run(d, args.output, controls=not args.no_controls)
    print(json.dumps({f: r["verdict"] for f, r in result["families"].items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
