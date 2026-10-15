"""S1 pilot orchestration: tree-0 ladder, CPU/memory accounting, P1-P6 report, §7 decision.

Preregistration: docs/SPECTRAL_S1_PREREGISTRATION.md v0.2 (§4-§7), config
configs/spectral_s1_pilot.json. Kernel, exact references, P0 gates and the statistics
helpers live in `spectral_s1` (merged via PR #45); this module only orchestrates them.

Two modes:
- ``engineering`` (default): the engineering seed base TEST_SEED_BASE and a scaled-down
  design (`ENGINEERING_DESIGN`). Used by tests and CI. Its numbers are **not** pilot data.
- ``pilot``: the frozen config and the pilot seed base 2036101301. Requires
  ``S1_ALLOW_PILOT_SEEDS=1`` (enforced by `spectral_s1.build_instance`) **and** the
  explicit flag ``--i-understand-this-draws-pilot-seeds``. It must only be run after the
  later-pass review of this orchestration code.

Nothing here classifies a spectral dimension or makes a physical claim. The §7 decision is
an engineering feasibility decision for a later, separately preregistered S2.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import resource
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy import stats

from emergence_lab import spectral_s1 as s1
from emergence_lab.dimension_d2 import CAY, RRT, UST

POSITIVE = (CAY, UST)
SIZE_KEY = {CAY: "N", UST: "L", RRT: "N"}
GIB = 1024 ** 3
SKIPPED_OVER_CAP = "OVER_CAP"


def pilot_design(cfg: dict) -> dict:
    """Design dict from the frozen config (prereg §4-§7). Raises if the config drifted."""
    if cfg.get("version") != "0.2" or cfg.get("seed_base") != s1.PILOT_SEED_BASE:
        raise ValueError("unexpected S1 config version or seed base")
    fams = cfg["families"]
    d = cfg["decision_rule"]
    return {
        "mode": "pilot",
        "seed_base": cfg["seed_base"],
        "bootstrap_seed": cfg["statistics"]["bootstrap_seed"],
        "n_boot": cfg["statistics"]["bootstrap_tree_resamples"],
        "families": {f: {"sizes": list(fams[f][SIZE_KEY[f]]), "trees": fams[f]["trees"],
                         "sources": fams[f]["sources"]} for f in s1.FAMILY_ORDER},
        "T_ladder": list(cfg["T_ladder"]),
        "eta": cfg["kernel"]["eta"],
        "r_start": cfg["kernel"]["R_start"],
        "edge_step_cap": cfg["kernel"]["per_source_edge_step_cap"],
        "ladder_trigger_cpu_s": 60.0 * cfg["budget"]["ladder_trigger_cpu_min_per_family"],
        "total_cpu_s": 60.0 * cfg["budget"]["max_cpu_minutes_total"],
        "hard_stop_factor": 1.5,
        "max_memory_bytes": int(cfg["budget"]["max_memory_gib"] * GIB),
        "s2_budget_cpu_s": 60.0 * d["s2_budget_cpu_min_per_family"],
        "s2_sources": cfg["statistics"]["sources_per_tree_fixed"],
        "t_lo_min": d["t_lo_min"], "min_slopes": d["window_min_slopes"],
        "headroom": d["headroom"], "go_full": d["go_full_halfwidth"],
        "go_reduced": d["go_reduced_halfwidth"], "margin": d["size_equivalence_margin"],
        "level": d["size_equivalence_ci_level"],
        "max_adjacent": d["max_adjacent_dyadic_slope_difference"],
        "min_projected_trees": d["min_projected_trees"],
        "skew_max": d["skew_abs_max"], "share_max": d["max_squared_influence_share"],
        "variance_multipliers": list(cfg["statistics"]["variance_sensitivity_multipliers"]),
    }


def engineering_design(cfg: dict) -> dict:
    """Scaled-down design on engineering seeds: same rules, tiny sizes and budgets."""
    d = pilot_design(cfg)
    d.update({
        "mode": "engineering",
        "seed_base": s1.TEST_SEED_BASE,
        "n_boot": 256,
        "families": {CAY: {"sizes": [1024, 4096], "trees": 8, "sources": 8},
                     UST: {"sizes": [32, 64], "trees": 8, "sources": 8},
                     RRT: {"sizes": [1024], "trees": 4, "sources": 8}},
        "T_ladder": [128, 64, 32],
        "r_start": 16,
        "ladder_trigger_cpu_s": 60.0,
        "total_cpu_s": 600.0,
        "s2_budget_cpu_s": 60.0,
    })
    return d


# ----------------------------------------------------------------------------- accounting
def peak_rss_bytes() -> int:
    """Process peak resident set size (Linux ru_maxrss is KiB). Monotone over the run."""
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


@dataclass
class SourceRecord:
    family: str
    size: int
    i_size: int
    i_rep: int
    T: int
    n: int
    res: s1.KilledBallResult
    cpu_s: float
    wall_s: float
    peak_rss: int


@dataclass
class FamilyRun:
    family: str
    T: int = 0
    ladder: list = field(default_factory=list)
    status: str = "COMPLETE"   # COMPLETE | PARTIAL | BLOCKED
    projected_cpu_s: float = float("nan")
    cpu_s: float = 0.0
    tree_cpu_s: dict = field(default_factory=dict)   # (i_size, i_rep) -> cpu incl. generation
    records: list = field(default_factory=list)
    notes: list = field(default_factory=list)


class Budget:
    """Global CPU budget (process CPU time). Checked between sources, never mid-kernel."""

    def __init__(self, total_cpu_s: float):
        self.total = total_cpu_s
        self.t0 = time.process_time()

    def used(self) -> float:
        return time.process_time() - self.t0

    def exceeded(self) -> bool:
        return self.used() > self.total


def _run_tree(design: dict, fam: str, i_size: int, size: int, i_rep: int, T: int,
              recompute_only=None):
    """Generate one tree and its certified source curves at half-time horizon T."""
    c0, w0 = time.process_time(), time.perf_counter()
    spec = design["families"][fam]
    g, srcs = s1.build_instance(fam, size, i_size, i_rep, spec["sources"], design["seed_base"])
    gen_cpu = time.process_time() - c0
    out = []
    for v in srcs.tolist():
        if recompute_only is not None and v not in recompute_only:
            continue
        cs, ws = time.process_time(), time.perf_counter()
        r = s1.certified_returns(g, v, T, eta=design["eta"], r_start=design["r_start"],
                                 edge_step_cap=design["edge_step_cap"])
        out.append(SourceRecord(fam, size, i_size, i_rep, T, g.n, r,
                                time.process_time() - cs, time.perf_counter() - ws,
                                peak_rss_bytes()))
    return out, gen_cpu, time.process_time() - c0, time.perf_counter() - w0


def truncate(rec: SourceRecord, T: int) -> SourceRecord:
    """Restrict a certified result to a smaller horizon T' <= T (prereg §6, tree 0 counts).

    Valid for status OK: m_R(2t) <= m_R(2T) <= eta q_R(2T) <= eta q_R(2t) for t <= T, so the
    relative certification still holds at every t <= T'. OVER_CAP records are not truncated.
    """
    r = rec.res
    if r.status != "OK" or T > r.T:
        raise ValueError("cannot truncate")
    nr = s1.KilledBallResult(r.source, r.degree, r.R, T, r.ball_size, r.nnz,
                             r.q_lower[:T].copy(), r.killed[:T].copy(), {}, r.status)
    return SourceRecord(rec.family, rec.size, rec.i_size, rec.i_rep, T, rec.n, nr,
                        rec.cpu_s, rec.wall_s, rec.peak_rss)


def run_family(design: dict, fam: str, budget: Budget) -> FamilyRun:
    """Ladder from tree 0 of the smallest size (cost only, §6), then all remaining trees."""
    spec = design["families"][fam]
    sizes = sorted(spec["sizes"])
    n_trees_total = spec["trees"] * len(sizes)
    fr = FamilyRun(fam)
    c_fam = time.process_time()
    ladder = list(design["T_ladder"])
    T = ladder[0]
    recs0, _gen, cpu0, _w = _run_tree(design, fam, 0, sizes[0], 0, T)
    tree0_cpu = cpu0
    while True:
        over = [r for r in recs0 if r.res.status != "OK"]
        projected = tree0_cpu * n_trees_total
        step = {"T": T, "tree0_cpu_s": tree0_cpu, "projected_family_cpu_s": projected,
                "over_cap_sources": [r.res.source for r in over],
                "trigger_cpu_s": design["ladder_trigger_cpu_s"]}
        fr.ladder.append(step)
        if projected <= design["ladder_trigger_cpu_s"] and not over:
            step["decision"] = "accept"
            break
        k = ladder.index(T)
        if k + 1 >= len(ladder):
            step["decision"] = "BLOCKED (budget)"
            fr.status = "BLOCKED"
            fr.T = T
            fr.records = recs0
            fr.tree_cpu_s[(0, 0)] = tree0_cpu
            fr.cpu_s = time.process_time() - c_fam
            fr.notes.append("ladder exhausted on tree 0; family stopped (prereg §6)")
            return fr
        step["decision"] = f"reduce T to {ladder[k + 1]}"
        T = ladder[k + 1]
        # Tree 0 still counts: OK sources are truncated, OVER_CAP sources recomputed at T.
        ok = [truncate(r, T) for r in recs0 if r.res.status == "OK"]
        redo_src = {r.res.source for r in recs0 if r.res.status != "OK"}
        redo, _g, cpu_redo, _w = (_run_tree(design, fam, 0, sizes[0], 0, T, redo_src)
                                  if redo_src else ([], 0.0, 0.0, 0.0))
        recs0 = sorted(ok + redo, key=lambda r: r.res.source)
        # Projection for the reduced T is not measured directly for truncated sources;
        # scale the measured tree-0 cost by the step ratio (edge-steps are linear in T).
        tree0_cpu = (sum(r.cpu_s for r in ok) * T / ladder[k] + cpu_redo)
        step["note"] = "next step projects tree-0 cost by linear T scaling of OK sources"
    fr.T = T
    fr.projected_cpu_s = projected
    fr.records.extend(recs0)
    # Cost model entry for tree 0 at the final T (measured if no ladder step, else scaled);
    # the actually spent tree-0 CPU is kept in the ladder record.
    fr.tree_cpu_s[(0, 0)] = tree0_cpu
    fr.ladder[0]["tree0_actual_cpu_s"] = cpu0
    hard_stop = design["hard_stop_factor"] * projected
    for i_size, size in enumerate(sizes):
        for i_rep in range(spec["trees"]):
            if i_size == 0 and i_rep == 0:
                continue
            if budget.exceeded():
                fr.status = "PARTIAL"
                fr.notes.append(f"global CPU budget {budget.total:.0f} s reached")
                break
            if time.process_time() - c_fam > hard_stop:
                fr.status = "PARTIAL"
                fr.notes.append(f"family hard stop 1.5x projection ({hard_stop:.1f} s) reached")
                break
            recs, _gen, cpu, _w = _run_tree(design, fam, i_size, size, i_rep, T)
            fr.records.extend(recs)
            fr.tree_cpu_s[(i_size, i_rep)] = cpu
        if fr.status == "PARTIAL":
            break
    fr.cpu_s = time.process_time() - c_fam
    return fr


# ----------------------------------------------------------------------------- analysis
def _slopes(qbar: np.ndarray, times: list[int]) -> list[float]:
    return [float(-2.0 * math.log2(qbar[k + 1] / qbar[k])) for k in range(len(times) - 1)]


def tree_matrix(records: list[SourceRecord], i_size: int, times: list[int]):
    """Q (trees x times) of per-tree source means, plus per-source rows (OK only)."""
    by_tree: dict[int, list[SourceRecord]] = {}
    for r in records:
        if r.i_size == i_size:
            by_tree.setdefault(r.i_rep, []).append(r)
    reps = sorted(by_tree)
    complete = [k for k in reps if all(r.res.status == "OK" for r in by_tree[k])]
    idx = [t - 1 for t in times]
    Q = np.array([np.mean([r.res.q_lower[idx] for r in by_tree[k]], axis=0) for k in complete])
    return Q, {k: by_tree[k] for k in complete}, [k for k in reps if k not in complete]


def source_jackknife_sd(per_tree: dict, lo: int, hi: int, times: list[int]) -> float:
    """Descriptive within-tree delete-one-source jackknife SD of the annealed window slope."""
    idx = [t - 1 for t in times]
    reps = sorted(per_tree)
    rows = {k: np.array([r.res.q_lower[idx] for r in per_tree[k]]) for k in reps}
    Q = np.array([rows[k].mean(axis=0) for k in reps])
    var = 0.0
    for a, k in enumerate(reps):
        S = rows[k].shape[0]
        if S < 2:
            return float("nan")
        vals = []
        for j in range(S):
            Qj = Q.copy()
            Qj[a] = np.delete(rows[k], j, axis=0).mean(axis=0)
            vals.append(s1.annealed_window_slope(Qj, lo, hi, times))
        vals = np.array(vals)
        var += (S - 1) / S * float(np.sum((vals - vals.mean()) ** 2))
    return math.sqrt(var)


def degree_bias(per_tree: dict, times: list[int]) -> dict:
    """P4: mean q_v(t) by source degree class and the leaf share of the annealed mean."""
    idx = [t - 1 for t in times]
    rows = [r for k in sorted(per_tree) for r in per_tree[k]]
    q = np.array([r.res.q_lower[idx] for r in rows])
    deg = np.array([r.res.degree for r in rows])
    classes = {"1": deg == 1, "2": deg == 2, ">=3": deg >= 3}
    out = {"n_sources": int(len(rows))}
    for name, m in classes.items():
        out[name] = {"count": int(m.sum()),
                     "mean_q": ([float(x) for x in q[m].mean(axis=0)] if m.any() else None)}
    tot = q.sum(axis=0)
    out["leaf_share"] = [float(x) for x in q[classes["1"]].sum(axis=0) / tot]
    return out


def size_summary(design: dict, fr: FamilyRun, i_size: int, times: list[int]) -> dict:
    """P2/P3/P4 and per-window headroom for one family size."""
    Q, per_tree, incomplete = tree_matrix(fr.records, i_size, times)
    size = sorted(design["families"][fr.family]["sizes"])[i_size]
    n_v = next((r.n for r in fr.records if r.i_size == i_size), None)
    out = {"size": size, "n_vertices": n_v, "n_trees": int(Q.shape[0]) if Q.size else 0,
           "incomplete_trees": incomplete}
    if not Q.size or Q.shape[0] < 2:
        out["insufficient"] = True
        return out
    qbar = Q.mean(axis=0)
    out["qbar"] = [float(x) for x in qbar]
    out["dyadic_slopes"] = _slopes(qbar, times)
    out["per_tree_dyadic_slopes"] = [_slopes(Q[a], times) for a in range(Q.shape[0])]
    out["degree_bias"] = degree_bias(per_tree, times)
    recs = [r for k in sorted(per_tree) for r in per_tree[k]]
    out["max_rel_bracket"] = float(max(r.res.relative_bracket() for r in recs))
    out["certified"] = bool(all(r.res.killed[-1] <= design["eta"] * r.res.q_lower[-1]
                                for r in recs))
    windows = {}
    for lo, hi in s1.candidate_windows(times[-1], design["t_lo_min"], design["min_slopes"]):
        psi = s1.tree_influences(Q, lo, hi, times)
        i, j = times.index(lo), times.index(hi)
        tree_slopes = -2.0 * (np.log(Q[:, j]) - np.log(Q[:, i])) / math.log(hi / lo)
        q_hi = np.array([r.res.q_lower[hi - 1] for r in recs])
        degs = np.array([r.res.degree for r in recs])
        floor_ratio = q_hi / (degs / (n_v - 1))
        windows[f"{lo}-{hi}"] = {
            "lo": lo, "hi": hi,
            "d_W": s1.annealed_window_slope(Q, lo, hi, times),
            "psi": [float(x) for x in psi],
            "reliability": s1.projection_reliability(psi, [qbar[i], qbar[j]],
                                                     design["skew_max"], design["share_max"]),
            "bootstrap": s1.bootstrap_slopes(Q, lo, hi, times, design["n_boot"],
                                             design["bootstrap_seed"]),
            "source_jackknife_sd": source_jackknife_sd(per_tree, lo, hi, times),
            "mean_of_tree_slopes": float(tree_slopes.mean()),
            "sd_of_tree_slopes": float(tree_slopes.std(ddof=1)),
            "headroom_min": float(floor_ratio.min()),
            "headroom_quantiles": [float(x) for x in np.quantile(floor_ratio, [0, .1, .5, .9, 1])],
            "adjacent_ok": s1.adjacent_slopes_ok(qbar, times, lo, hi, design["max_adjacent"]),
        }
    out["windows"] = windows
    return out


def s2_projection(design: dict, psi: np.ndarray, cpu_per_tree_s: float) -> dict:
    """P3/§7: h(n') at fixed S for every multiplier; smallest n' meeting each target in budget."""
    n_max = int(design["s2_budget_cpu_s"] // cpu_per_tree_s) if cpu_per_tree_s > 0 else 0
    out = {"cpu_per_tree_s": cpu_per_tree_s, "n_max_in_budget": n_max, "by_multiplier": {}}
    lo_n = design["min_projected_trees"]
    for mult in design["variance_multipliers"]:
        if n_max < lo_n:
            out["by_multiplier"][str(mult)] = {"h_at_n_max": float("nan"),
                                               "n_needed": {"full": None, "reduced": None}}
            continue
        proj = s1.power_projection(psi, [n_max], mult)
        U = proj["U"]

        def h(m):
            return float(stats.t.ppf(0.975, m - 1) * math.sqrt(U / m))

        need = {}
        for name, target in (("full", design["go_full"]), ("reduced", design["go_reduced"])):
            need[name] = None
            if h(n_max) <= target:
                a, b = lo_n, n_max          # h is decreasing in m: binary search
                while a < b:
                    mid = (a + b) // 2
                    if h(mid) <= target:
                        b = mid
                    else:
                        a = mid + 1
                need[name] = a
        out["by_multiplier"][str(mult)] = {"U": U, "h_at_n_max": h(n_max), "n_needed": need}
    return out


def family_analysis(design: dict, fr: FamilyRun) -> dict:
    times = s1.dyadic_half_times(fr.T) if fr.T else []
    spec = design["families"][fr.family]
    sizes = sorted(spec["sizes"])
    out = {"family": fr.family, "status": fr.status, "T": fr.T, "ladder": fr.ladder,
           "notes": fr.notes, "cpu_s": fr.cpu_s, "projected_cpu_s": fr.projected_cpu_s,
           "over_cap_records": [(r.i_size, r.i_rep, r.res.source) for r in fr.records
                                if r.res.status != "OK"],
           "sizes": {}}
    if fr.status == "BLOCKED":
        return out
    for i_size in range(len(sizes)):
        out["sizes"][str(sizes[i_size])] = size_summary(design, fr, i_size, times)
    # P1 cost model: CPU per tree (generation + all sources) at each size.
    cost = {}
    for i_size, size in enumerate(sizes):
        c = [v for (a, _b), v in fr.tree_cpu_s.items() if a == i_size and (a, _b) != (0, 0)]
        if i_size == 0:
            c = c + [fr.tree_cpu_s[(0, 0)]] if (0, 0) in fr.tree_cpu_s else c
        srcs = [r for r in fr.records if r.i_size == i_size]
        cost[str(size)] = {
            "trees_timed": len(c), "cpu_per_tree_mean_s": float(np.mean(c)) if c else float("nan"),
            "cpu_per_tree_max_s": float(np.max(c)) if c else float("nan"),
            "cpu_per_source_s": [float(np.quantile([r.cpu_s for r in srcs], q)) for q in (0, .5, 1)]
            if srcs else None,
            "R_values": sorted({r.res.R for r in srcs}),
            "ball_size_max": int(max(r.res.ball_size for r in srcs)) if srcs else None,
            "edge_steps_max": int(max(r.res.edge_steps for r in srcs)) if srcs else None,
        }
    out["P1_cost"] = cost
    return out


def _sizes_pair(fa: dict):
    keys = list(fa["sizes"])
    if len(keys) < 2:
        return None
    small, large = fa["sizes"][keys[0]], fa["sizes"][keys[-1]]
    if small.get("insufficient") or large.get("insufficient"):
        return None
    return small, large


def decide_family(design: dict, fr: FamilyRun, fa: dict) -> dict:
    """§7 window qualification and projected half-width for one positive family.

    Interpretations flagged for review (prereg is silent): (i) headroom, adjacent-slope
    stability, certification and reliability are required at **both** pilot sizes
    (conservative); (ii) the S2 projection uses the larger pilot size's influences and its
    measured CPU per tree; (iii) the primary variance multiplier is 1 (3U is sensitivity).
    """
    res = {"family": fr.family, "qualifying": [], "failures": {}, "W_star": None,
           "h": None, "tested_windows": 0}
    if fr.status != "COMPLETE":
        res["failures"]["family"] = f"status {fr.status}"
        return res
    if fa["over_cap_records"]:
        res["failures"]["family"] = "OVER_CAP sources present"
        return res
    pair = _sizes_pair(fa)
    if pair is None:
        res["failures"]["family"] = "fewer than two analysable sizes"
        return res
    small, large = pair
    times = s1.dyadic_half_times(fr.T)
    sizes = sorted(design["families"][fr.family]["sizes"])
    Qs, _, _ = tree_matrix(fr.records, 0, times)
    Ql, _, _ = tree_matrix(fr.records, len(sizes) - 1, times)
    cpu_large = fa["P1_cost"][str(sizes[-1])]["cpu_per_tree_mean_s"]
    peak = max(r.peak_rss for r in fr.records)
    if peak > design["max_memory_bytes"]:
        res["failures"]["family"] = f"peak RSS {peak} B over budget"
        return res
    for key, wl in large["windows"].items():
        res["tested_windows"] += 1
        ws = small["windows"].get(key)
        lo, hi = wl["lo"], wl["hi"]
        reasons = []
        if ws is None:
            reasons.append("window absent at smaller size")
        else:
            eq = s1.size_equivalence(Qs, Ql, lo, hi, times, design["margin"], design["level"])
            wl["size_equivalence"] = eq
            if not eq["equivalent"]:
                reasons.append("size_equivalence")
            if ws["headroom_min"] < design["headroom"] or wl["headroom_min"] < design["headroom"]:
                reasons.append("headroom")
            if not (ws["adjacent_ok"] and wl["adjacent_ok"]):
                reasons.append("adjacent_slopes")
            if not (ws["reliability"]["reliable"] and wl["reliability"]["reliable"]):
                reasons.append("unreliable_projection")
            if not (small["certified"] and large["certified"]):
                reasons.append("certification")
        proj = s2_projection(design, np.array(wl["psi"]), cpu_large)
        wl["s2_projection"] = proj
        if reasons:
            res["failures"][key] = reasons
            continue
        res["qualifying"].append({"window": key, "lo": lo, "hi": hi,
                                  "h": proj["by_multiplier"]["1"]["h_at_n_max"],
                                  "n_needed": proj["by_multiplier"]["1"]["n_needed"],
                                  "n_max": proj["n_max_in_budget"]})
    if res["qualifying"]:
        best = sorted(res["qualifying"],
                      key=lambda w: (w["h"] if np.isfinite(w["h"]) else math.inf, w["lo"], w["hi"]))[0]
        res["W_star"], res["h"] = best["window"], best["h"]
        res["n_needed"], res["n_max"] = best["n_needed"], best["n_max"]
    return res


def decision(fam_decisions: dict, design: dict) -> dict:
    """§7: GO (full) / GO (reduced) / NO-GO (scoped)."""
    hs = {f: fam_decisions[f]["h"] for f in POSITIVE}
    ok = {f: (h is not None and np.isfinite(h)) for f, h in hs.items()}
    full = all(ok[f] and hs[f] <= design["go_full"] for f in POSITIVE)
    reduced = all(ok[f] and hs[f] <= design["go_reduced"] for f in POSITIVE)
    if full:
        verdict = "GO (full S2)"
    elif reduced:
        verdict = "GO (reduced)"
    else:
        verdict = "NO-GO (scoped)"
    single = [f for f in POSITIVE if ok[f] and hs[f] <= design["go_reduced"]]
    return {"verdict": verdict, "h": hs,
            "single_family_feasible_descriptive": single if verdict.startswith("NO-GO") else [],
            "note": ("engineering feasibility decision for a separately preregistered S2; "
                     "not a calibration verdict and no physical claim")}


# ----------------------------------------------------------------------------- outputs
TIMING_HEADER = ["family", "size", "i_size", "i_rep", "source", "T", "status", "R", "cpu_s",
                 "wall_s", "peak_rss_bytes"]


def numeric_csv(fr_list: list[FamilyRun]) -> bytes:
    """Deterministic numeric CSV (no timings), one block per family at its final T."""
    parts = []
    for fr in fr_list:
        rows = [(r.family, r.size, r.i_size, r.i_rep, r.res) for r in fr.records]
        if rows:
            parts.append(s1.rows_csv(rows, fr.T))
    return b"".join(parts)


def timing_csv(fr_list: list[FamilyRun]) -> bytes:
    lines = [",".join(TIMING_HEADER)]
    for fr in fr_list:
        for r in fr.records:
            lines.append(",".join(str(x) for x in (r.family, r.size, r.i_size, r.i_rep,
                                                  r.res.source, r.T, r.res.status, r.res.R,
                                                  f"{r.cpu_s:.6f}", f"{r.wall_s:.6f}",
                                                  r.peak_rss)))
    return ("\n".join(lines) + "\n").encode()


def tree_rows_replay(design: dict, fam: str, i_size: int, i_rep: int, T_path: list[int]) -> bytes:
    """Independent replay of one tree along the ladder path actually taken (P0d on pilot data).

    For each source: compute at the first rung, keep it (truncated to the final rung) if OK,
    otherwise recompute at the next rung; equivalent to `run_family`'s ladder bookkeeping.
    """
    spec = design["families"][fam]
    size = sorted(spec["sizes"])[i_size]
    g, srcs = s1.build_instance(fam, size, i_size, i_rep, spec["sources"], design["seed_base"])
    T_final = T_path[-1]
    rows = []
    for v in srcs.tolist():
        res = None
        for T in (T_path if (i_size, i_rep) == (0, 0) else [T_final]):
            res = s1.certified_returns(g, v, T, eta=design["eta"], r_start=design["r_start"],
                                       edge_step_cap=design["edge_step_cap"])
            if res.status == "OK":
                break
        rec = SourceRecord(fam, size, i_size, i_rep, res.T, g.n, res, 0.0, 0.0, 0)
        if res.status == "OK" and res.T != T_final:
            rec = truncate(rec, T_final)
        rows.append((fam, size, i_size, i_rep, rec.res))
    return s1.rows_csv(rows, T_final)


def p0d_pilot_tree(design: dict, fr: FamilyRun, root: Path = Path(".")) -> dict:
    """P0d on the run's own CAY tree 0: byte identity with a replay in a separate process."""
    import os
    import subprocess
    import sys
    rows = [(r.family, r.size, r.i_size, r.i_rep, r.res) for r in fr.records
            if (r.i_size, r.i_rep) == (0, 0)]
    here = hashlib.sha256(s1.rows_csv(rows, fr.T)).hexdigest()
    path = [s["T"] for s in fr.ladder]
    code = ("import sys,json,hashlib;from emergence_lab import spectral_s1_pilot as sp;"
            "a=json.load(sys.stdin);"
            "sys.stdout.write(hashlib.sha256(sp.tree_rows_replay(a['d'],a['f'],0,0,a['p'])).hexdigest())")
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    other = subprocess.run([sys.executable, "-c", code], cwd=root, env=env, text=True,
                           input=json.dumps({"d": design, "f": fr.family, "p": path}),
                           capture_output=True, check=True).stdout.strip()
    return {"family": fr.family, "T_path": path, "in_run_sha256": here,
            "replay_sha256": other, "pass": bool(here == other)}


def run_pilot(design: dict, outdir: Path, root: Path = Path("."), families=None,
              controls: bool = True) -> dict:
    """Run families in the frozen order with the global budget; write CSVs and report JSON."""
    outdir.mkdir(parents=True, exist_ok=True)
    budget = Budget(design["total_cpu_s"])
    families = list(families or s1.FAMILY_ORDER)
    runs, analyses = [], {}
    for fam in s1.FAMILY_ORDER:
        if fam not in families:
            continue
        if budget.exceeded():
            fr = FamilyRun(fam, status="PARTIAL", notes=["global CPU budget reached before start"])
        else:
            fr = run_family(design, fam, budget)
        runs.append(fr)
        analyses[fam] = family_analysis(design, fr)
    fam_dec = {}
    for fam in POSITIVE:
        fr = next((r for r in runs if r.family == fam), None)
        fam_dec[fam] = (decide_family(design, fr, analyses[fam]) if fr is not None else
                        {"family": fam, "h": None, "failures": {"family": "not run"}})
    report = {
        "mode": design["mode"],
        "design": design,
        "manifest": s1.manifest(root, seeds=[[design["seed_base"], "i_family", "i_size", "i_rep"]]),
        "families": analyses,
        "P6_null_note": "RRT is a null without finite dimension; reported, not gated",
        "family_decisions": fam_dec,
        "decision": decision(fam_dec, design),
    }
    if controls:
        cay = next((r for r in runs if r.family == CAY and r.records), None)
        report["controls"] = {"P0a": s1.p0a(), "P0c": s1.p0c(),
                              "P0d_pilot_tree0": (p0d_pilot_tree(design, cay, root) if cay
                                                  else {"pass": False, "reason": "no CAY tree"})}
    # Controls count toward the whole-pilot budget (prereg §6); the replay subprocess CPU
    # is reported via RUSAGE_CHILDREN.
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    report["budget"] = {"cpu_s_used": budget.used(),
                        "child_cpu_s": children.ru_utime + children.ru_stime,
                        "cpu_s_total": design["total_cpu_s"],
                        "within_total": budget.used() + children.ru_utime + children.ru_stime
                        <= design["total_cpu_s"],
                        "peak_rss_bytes": peak_rss_bytes(),
                        "memory_ok": peak_rss_bytes() <= design["max_memory_bytes"]}
    num, tim = numeric_csv(runs), timing_csv(runs)
    (outdir / "s1_pilot_numeric.csv").write_bytes(num)
    (outdir / "s1_pilot_timing.csv").write_bytes(tim)
    report["numeric_csv_sha256"] = hashlib.sha256(num).hexdigest()
    report["timing_csv_sha256"] = hashlib.sha256(tim).hexdigest()
    (outdir / "s1_pilot_report.json").write_text(
        json.dumps(report, sort_keys=True, indent=1, default=_json_default))
    return report


def _json_default(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, tuple):
        return list(o)
    return str(o)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="S1 pilot orchestration (engineering by default)")
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--mode", choices=("engineering", "pilot"), default="engineering")
    ap.add_argument("--i-understand-this-draws-pilot-seeds", action="store_true",
                    dest="unlock")
    ap.add_argument("--no-controls", action="store_true")
    args = ap.parse_args(argv)
    cfg = json.loads(s1.CONFIG_PATH.read_text())
    if args.mode == "pilot":
        if not args.unlock:
            ap.error("pilot mode draws the preregistered pilot seeds; pass the explicit flag")
        design = pilot_design(cfg)
    else:
        design = engineering_design(cfg)
    rep = run_pilot(design, args.output, controls=not args.no_controls)
    print(json.dumps({"mode": rep["mode"], "decision": rep["decision"]["verdict"],
                      "h": rep["decision"]["h"],
                      "families": {f: a["status"] for f, a in rep["families"].items()},
                      "T": {f: a["T"] for f, a in rep["families"].items()},
                      "cpu_s": rep["budget"]["cpu_s_used"],
                      "numeric_csv_sha256": rep["numeric_csv_sha256"]}, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
