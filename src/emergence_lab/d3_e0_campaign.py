"""D3-E0/M0 frozen-protocol v1 campaign runner (pilot + gated target).

Protocol: docs/CS0_D3_E0_PROTOCOL.md; frozen config: configs/d3_e0_v1.json.

* ``pilot`` (engineering only): measures per-cell SD(d), P(R=0) and CPU time on
  the executing host with the pilot seed root, and derives the target n_c by the
  frozen rule.  It never writes a cell mean (blinding: pilot estimates are not
  results and cannot be pooled or peeked at).
* ``target``: refuses unless a separately committed authorization pins the
  protocol, config, code blobs and the pilot record; runs the gates (quadrature,
  sampler agreement, MC-vs-quadrature, D=2 positive control) and the D=3 cells
  under one 600 CPU s / 512 MiB cap, and classifies by the frozen rules.

Nothing in this module asserts a result; its outputs are numerical observations
about one estimator in one prescribed flat geometry.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import resource
import signal
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

import numpy as np
from scipy.stats import chi2_contingency

from . import d3_e0 as m
from .causal_set_mm import causal_matrix, sprinkle_diamond

REPO = Path(__file__).resolve().parents[2]
CONFIG = REPO / "configs" / "d3_e0_v1.json"
PROTOCOL = REPO / "docs" / "CS0_D3_E0_PROTOCOL.md"
PINNED_PATHS = ("docs/CS0_D3_E0_PROTOCOL.md", "configs/d3_e0_v1.json",
                "src/emergence_lab/d3_e0.py", "src/emergence_lab/d3_e0_campaign.py",
                "src/emergence_lab/causal_set_mm.py",
                "docs/experiments/d2-e0-v1-20261111/ensemble_comparison.csv")
ARM_CODE = {"A": 0, "B": 1}


class CapExceeded(RuntimeError):
    pass


# --------------------------------------------------------------------------
# Config, environment, provenance
# --------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_config(path: Path = CONFIG) -> dict:
    cfg = json.loads(Path(path).read_text())
    if cfg.get("protocol") != "D3-E0/M0 v1":
        raise ValueError("not the D3-E0/M0 v1 config")
    if tuple(cfg["grid"]) != m.GRID:
        raise ValueError("config grid differs from the frozen grid")
    return cfg


def require_reference_extra(cfg: dict) -> dict:
    """Freeze item (a): the pinned `.[reference]` extra must be installed."""
    versions = {}
    for pkg, want in cfg["required_versions"].items():
        try:
            got = metadata.version(pkg)
        except metadata.PackageNotFoundError as exc:
            raise RuntimeError(f"required package {pkg}=={want} missing "
                               "(pip install -e '.[reference]')") from exc
        if want is not None and got != want:
            raise RuntimeError(f"{pkg} {got} != pinned {want}")
        versions[pkg] = got
    for pkg in ("numpy", "scipy"):
        versions.setdefault(pkg, metadata.version(pkg))
    versions["python"] = platform.python_version()
    return versions


def stochastic_cells(cfg: dict) -> list:
    det = {tuple(x) for x in cfg["deterministic_cells"]}
    return [(arm, n) for arm in ("A", "B") for n in cfg["grid"] if (arm, n) not in det]


def cell_rng(root: int, arm: str, d: int, n: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence(root, spawn_key=(ARM_CODE[arm], d, n)))


def cpu_seconds() -> float:
    ru = resource.getrusage(resource.RUSAGE_SELF)
    return ru.ru_utime + ru.ru_stime


def peak_rss_mib() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


class cpu_cap:
    """Soft RLIMIT_CPU at (used + seconds); SIGXCPU raises CapExceeded.

    The previous limit and handler are restored on exit.  The cap counts the
    whole process (gates, D=2 control and D=3 cells: one budget)."""

    def __init__(self, seconds: int):
        self.seconds = int(seconds)

    def __enter__(self):
        def _hit(signum, frame):
            raise CapExceeded(f"CPU cap {self.seconds} s exceeded")
        self._old_handler = signal.signal(signal.SIGXCPU, _hit)
        self._old = resource.getrlimit(resource.RLIMIT_CPU)
        soft = int(math.ceil(cpu_seconds())) + self.seconds
        hard = self._old[1]
        if hard != resource.RLIM_INFINITY:
            soft = min(soft, hard)
        resource.setrlimit(resource.RLIMIT_CPU, (soft, hard))
        return self

    def __exit__(self, *exc):
        resource.setrlimit(resource.RLIMIT_CPU, self._old)
        signal.signal(signal.SIGXCPU, self._old_handler)
        return False


# --------------------------------------------------------------------------
# Cell sampling with fixed R>0 count (arm B) and Welford accumulation
# --------------------------------------------------------------------------

def run_cell(arm: str, n: int, d: int, positives: int, rng: np.random.Generator,
             chunk: int, keep_raw: bool = False) -> dict:
    """Draw chunks until exactly ``positives`` replicates with R>0 are reached.

    The stopping rule depends only on R>0 indicators, which are independent of
    the d-values of the positive replicates, so the positives are i.i.d. from
    the conditional law.  Replicates are processed in draw order; the last chunk
    is truncated at the n_c-th positive so the result is deterministic."""
    table = m.inverse_table(n)
    acc = m.Welford()
    drawn = 0
    computed = 0
    raw = []
    t0 = cpu_seconds()
    while acc.n < positives:
        r = m.arm_counts(arm, n, d, chunk, rng)
        computed += r.size
        pos_idx = np.flatnonzero(r > 0)
        need = positives - acc.n
        if pos_idx.size >= need:
            cut = int(pos_idx[need - 1]) + 1
            r = r[:cut]
        drawn += r.size
        acc.add_batch(table[r[r > 0]])
        if keep_raw:
            raw.append(r.astype(np.uint16))
    sd = math.sqrt(max(acc.var, 0.0)) if acc.n > 1 else math.nan
    out = {"arm": arm, "N": n, "D": d, "positives": acc.n, "drawn": drawn,
           "computed": computed,
           "mean_d": acc.mean, "sd_d": sd,
           "se_d": sd / math.sqrt(acc.n) if acc.n > 1 else math.nan,
           "p_r0": 1.0 - acc.n / drawn, "cpu_s": cpu_seconds() - t0}
    if keep_raw:
        out["raw"] = np.concatenate(raw)
    return out


def steady_cpu_per_positive(res: dict) -> float:
    """Steady-state CPU per R>0 replicate (review r1).

    A cell computes whole chunks and discards the tail of the last one, so
    cpu_s / positives over-counts by up to chunk/positives at pilot sizes (4-11x
    observed).  Cost per *computed* replicate divided by the observed positive
    fraction is the cost at target sizes, where the truncated tail is negligible."""
    return res["cpu_s"] / res["computed"] * res["drawn"] / res["positives"]


# --------------------------------------------------------------------------
# Gates
# --------------------------------------------------------------------------

def quadrature_gates() -> dict:
    out = {}
    for d in (2, 3):
        q = m.three_point_probabilities(d)
        out[f"D{d}_q_pair_vs_f_over_2"] = abs(float(q["q_pair"]) - m.mm_forward(d) / 2)
        out[f"D{d}_q_chain_vs_chi3"] = abs(float(q["q_chain"]) - m.k_chain_probability(3, d))
    q2 = m.three_point_probabilities(2)
    out["D2_q_chain_vs_1_36"] = abs(float(q2["q_chain"]) - 1 / 36)
    out["D2_q_down_vs_1_9"] = abs(float(q2["q_down"]) - 1 / 9)
    ex = m.archived_d2_exact()
    c2 = m.exact_three_point_cells(2)
    out["D2_B3_vs_archived"] = abs(c2["B3_conditional_mean_d"] - ex[("B", 3)])
    out["D2_A5_vs_archived"] = abs(c2["A5_mean_d"] - ex[("A", 5)])
    passed = all(v <= 1e-11 for v in out.values())
    return {"passed": passed, "tolerance": 1e-11, "abs_errors": out}


def sampler_gates(cfg: dict, root: int) -> dict:
    g = cfg["gates"]["sampler"]
    res = {"pair": {}, "chi2": {}}
    f = m.mm_forward(3)
    n_pair = g["pair_replicates"]
    rng_d = np.random.default_rng(np.random.SeedSequence(root, spawn_key=(10, 3)))
    rng_r = np.random.default_rng(np.random.SeedSequence(root, spawn_key=(11, 3)))
    direct = m.relation_counts(m.direct_sample(n_pair, 2, 3, rng_d))
    rej = np.array([int(causal_matrix(sprinkle_diamond(2, 3, rng_r, batch=16)).sum())
                    for _ in range(n_pair)])
    se = math.sqrt(f * (1 - f) / n_pair)
    res["pair"] = {"direct_z": (direct.mean() - f) / se, "rejection_z": (rej.mean() - f) / se}
    ok = all(abs(z) <= g["z_max"] for z in res["pair"].values())
    for n in g["chi2_N"]:
        rd = np.random.default_rng(np.random.SeedSequence(root, spawn_key=(12, n)))
        rr = np.random.default_rng(np.random.SeedSequence(root, spawn_key=(13, n)))
        a = m.relation_counts(m.direct_sample(g["chi2_replicates"], n, 3, rd))
        b = np.array([int(causal_matrix(sprinkle_diamond(n, 3, rr, batch=64)).sum())
                      for _ in range(g["chi2_replicates"])])
        c = n * (n - 1) // 2
        ca, cb = np.bincount(a, minlength=c + 1), np.bincount(b, minlength=c + 1)
        keep = (ca + cb) > 0
        p = float(chi2_contingency(np.vstack([ca[keep], cb[keep]]))[1])
        res["chi2"][str(n)] = p
        ok = ok and p > g["chi2_p_min"]
    res["passed"] = bool(ok)
    return res


# --------------------------------------------------------------------------
# n_c rule (frozen) and classification
# --------------------------------------------------------------------------

def target_sizes(cfg: dict, pilot_cells: dict, gate_cpu_s: float) -> dict:
    """Frozen n_c rule.  pilot_cells: {"A|N": {"sd_d", "cpu_per_positive_D3",
    "cpu_per_positive_D2"}}.  Returns {"n_c": {...}, "projected_cpu_s", "status"}."""
    r = cfg["n_c_rule"]
    n_c = {}
    for key, pc in pilot_cells.items():
        n_c[key] = max(r["floor"], int(math.ceil((r["k_se"] * pc["sd_d"] / r["half_width"]) ** 2)))

    def projected(sizes):
        cell = sum(sizes[k] * (pilot_cells[k]["cpu_per_positive_D3"] +
                               pilot_cells[k]["cpu_per_positive_D2"]) for k in sizes)
        return r["safety_factor"] * (cell + gate_cpu_s)

    budget = cfg["caps"]["cpu_s"]
    proj = projected(n_c)
    status = "OK"
    if proj > budget:
        # Uniform scale-down toward the floor; floor-infeasible => no target.
        floor_sizes = {k: r["floor"] for k in n_c}
        if projected(floor_sizes) > budget:
            return {"n_c": n_c, "projected_cpu_s": proj, "status": "BUDGET_INFEASIBLE"}
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            trial = {k: max(r["floor"], int(v * mid)) for k, v in n_c.items()}
            lo, hi = (mid, hi) if projected(trial) <= budget else (lo, mid)
        n_c = {k: max(r["floor"], int(v * lo)) for k, v in n_c.items()}
        proj = projected(n_c)
        status = "CAP_BINDS"
    return {"n_c": n_c, "projected_cpu_s": proj, "status": status}


def arm_b_d_of_mean_r(p_pos: float, d: int) -> float:
    r = m.mm_forward(d) / p_pos
    if r >= 1.0:
        return 1.0
    from scipy.optimize import brentq
    return brentq(lambda x: m.mm_forward(x) - r, 1.0, 10.0, xtol=1e-14)


def arm_a_d_of_mean_r(n: int, d: int) -> float:
    c = n * (n - 1) / 2
    r = m.mm_forward(d) + (1 - m.mm_forward(d)) * (2 * n - 3) / c
    if r >= 1.0:
        return 1.0
    from scipy.optimize import brentq
    return brentq(lambda x: m.mm_forward(x) - r, 1.0, 10.0, xtol=1e-14)


def classify_cells(cells: list, cfg: dict) -> dict:
    z = m.bonferroni_z(cfg["decision"]["alpha"], len(cells))
    table = []
    for c in cells:
        delta = c["mean_d"] - cfg["D_target"]
        c = dict(c, delta=delta, z_bonf=z, label=m.classify(delta, c["se_d"], z))
        table.append(c)
    return {"z": z, "cells": table}


def outcome(gates_ok: bool, resources_ok: bool, labels: list) -> str:
    if not (gates_ok and resources_ok):
        return "INVALID"
    if any(lbl == "UNRESOLVED" for lbl in labels):
        return "UNDECIDABLE_AT_BUDGET"
    return "COMPLETE"


# --------------------------------------------------------------------------
# Entry points
# --------------------------------------------------------------------------

def _git(*args) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def _common_manifest(cfg_path: Path, mode: str, versions: dict) -> dict:
    return {"protocol": "D3-E0/M0 v1", "mode": mode,
            "started_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "config_sha256": sha256_file(cfg_path),
            "protocol_sha256": sha256_file(PROTOCOL),
            "git_head": _git("rev-parse", "HEAD"),
            "git_dirty_pinned": bool(_git("status", "--porcelain", "--", *PINNED_PATHS)),
            "versions": versions, "platform": platform.platform(),
            "host_cpus": os.cpu_count()}


def run_pilot(out_dir: Path, cfg_path: Path = CONFIG) -> dict:
    cfg = load_config(cfg_path)
    versions = require_reference_extra(cfg)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=False)
    pc = cfg["pilot"]
    man = _common_manifest(cfg_path, "pilot", versions)
    man["seed_root"] = cfg["seed_roots"]["pilot"]
    t0 = cpu_seconds()
    try:
        with cpu_cap(pc["cpu_s"]):
            g0 = cpu_seconds()
            quadrature_gates()
            sampler_gates(cfg, cfg["seed_roots"]["pilot"] + 1)
            gate_cpu = cpu_seconds() - g0
            cells = {}
            for arm, n in stochastic_cells(cfg):
                rec = {}
                for d in (3, 2):
                    res = run_cell(arm, n, d, pc["positives_per_cell"],
                                   cell_rng(cfg["seed_roots"]["pilot"], arm, d, n), cfg["chunk"])
                    rec[f"cpu_per_positive_D{d}"] = steady_cpu_per_positive(res)
                    if d == 3:
                        # Blinded: SD and P(R=0) only; the mean is never written.
                        rec["sd_d"] = res["sd_d"]
                        rec["p_r0_D3"] = res["p_r0"]
                cells[f"{arm}|{n}"] = rec
            sizes = target_sizes(cfg, cells, gate_cpu)
            man.update(status="PILOT_COMPLETE", gate_cpu_s=gate_cpu, cells=cells,
                       target_sizes=sizes)
    except CapExceeded as exc:
        man.update(status="PILOT_CAP_EXCEEDED", error=str(exc))
    man["cpu_s"] = cpu_seconds() - t0
    man["peak_rss_mib"] = peak_rss_mib()
    if man["peak_rss_mib"] > cfg["caps"]["rss_mib"]:
        man["status"] = "PILOT_RSS_EXCEEDED"
    (out_dir / "pilot_record.json").write_text(json.dumps(man, indent=2, sort_keys=True))
    return man


def _require_committed(path: Path, what: str) -> None:
    """Review r1: the file must be tracked at HEAD and unmodified.

    `git status --porcelain` alone is silent for gitignored files (e.g. under
    results/), so an uncommitted authorization or pilot record passed."""
    try:
        rel = str(Path(path).resolve().relative_to(REPO))
    except ValueError as exc:
        raise PermissionError(f"{what} is outside the repository") from exc
    try:
        _git("ls-files", "--error-unmatch", "--", rel)
    except subprocess.CalledProcessError as exc:
        raise PermissionError(f"{what} is not committed") from exc
    if _git("status", "--porcelain", "--", rel):
        raise PermissionError(f"{what} differs from the committed version")


def check_authorization(auth_path: Path, cfg_path: Path) -> dict:
    """The target refuses unless a committed authorization pins everything."""
    auth = json.loads(Path(auth_path).read_text())
    if auth.get("protocol") != "D3-E0/M0 v1" or auth.get("mode") != "target":
        raise PermissionError("authorization is not for the D3-E0/M0 v1 target")
    exp = datetime.fromisoformat(auth["expires_utc"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) >= exp:
        raise PermissionError("authorization expired")
    if auth["config_sha256"] != sha256_file(cfg_path):
        raise PermissionError("config hash mismatch")
    if auth["protocol_sha256"] != sha256_file(PROTOCOL):
        raise PermissionError("protocol hash mismatch")
    for p in PINNED_PATHS:
        blob = _git("rev-parse", f"HEAD:{p}")
        if auth["blobs"].get(p) != blob:
            raise PermissionError(f"pinned blob mismatch for {p}")
    if _git("status", "--porcelain", "--", *PINNED_PATHS):
        raise PermissionError("pinned paths dirty in the worktree")
    _require_committed(auth_path, "authorization file")
    pilot = Path(REPO / auth["pilot_record"])
    _require_committed(pilot, "pilot record")
    if sha256_file(pilot) != auth["pilot_record_sha256"]:
        raise PermissionError("pilot record hash mismatch")
    rec = json.loads(pilot.read_text())
    if rec.get("status") != "PILOT_COMPLETE" or rec["target_sizes"]["status"] == "BUDGET_INFEASIBLE":
        raise PermissionError("pilot did not authorize a feasible target")
    return {"auth": auth, "pilot": rec}


def run_target(out_dir: Path, auth_path: Path, cfg_path: Path = CONFIG) -> dict:
    cfg = load_config(cfg_path)
    versions = require_reference_extra(cfg)
    ok = check_authorization(auth_path, cfg_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=False)
    man = _common_manifest(cfg_path, "target", versions)
    man.update(seed_roots={k: cfg["seed_roots"][k] for k in ("gates", "target")},
               authorization_id=ok["auth"]["authorization_id"],
               status="INCOMPLETE")
    n_c = ok["pilot"]["target_sizes"]["n_c"]
    t0 = cpu_seconds()
    raw = {}
    try:
        with cpu_cap(cfg["caps"]["cpu_s"]):
            gates = {"quadrature": quadrature_gates(),
                     "sampler": sampler_gates(cfg, cfg["seed_roots"]["gates"])}
            d3, d2 = [], []
            for arm, n in stochastic_cells(cfg):
                k = f"{arm}|{n}"
                for d, sink in ((3, d3), (2, d2)):
                    res = run_cell(arm, n, d, n_c[k], cell_rng(cfg["seed_roots"]["target"], arm, d, n),
                                   cfg["chunk"], keep_raw=True)
                    raw[f"D{d}_{arm}_{n}"] = res.pop("raw")
                    sink.append(res)
            ex2 = m.archived_d2_exact()
            pc = []
            for c in d2:
                z = (c["mean_d"] - ex2[(c["arm"], c["N"])]) / c["se_d"]
                pc.append({"arm": c["arm"], "N": c["N"], "z": z})
            gates["d2_positive_control"] = {"passed": all(abs(x["z"]) <= cfg["gates"]["z_max"] for x in pc),
                                            "cells": pc}
            ex3 = m.exact_three_point_cells(3)
            qz = {}
            for c in d3:
                if (c["arm"], c["N"]) == ("B", 3):
                    qz["B3"] = (c["mean_d"] - ex3["B3_conditional_mean_d"]) / c["se_d"]
                if (c["arm"], c["N"]) == ("A", 5):
                    qz["A5"] = (c["mean_d"] - ex3["A5_mean_d"]) / c["se_d"]
            gates["d3_mc_vs_quadrature"] = {"passed": all(abs(v) <= cfg["gates"]["z_max"] for v in qz.values()),
                                            "z": qz}
            gates_ok = all(g["passed"] for g in gates.values())
            cls = classify_cells(d3, cfg)
            for c in cls["cells"]:
                if c["arm"] == "A":
                    c["d_of_mean_r"] = arm_a_d_of_mean_r(c["N"], 3)
                else:
                    c["d_of_mean_r"] = arm_b_d_of_mean_r(1 - c["p_r0"], 3)
                c["jensen_gap"] = c["mean_d"] - c["d_of_mean_r"]
            man.update(gates=gates, cells=cls["cells"], z_bonferroni=cls["z"],
                       deterministic_cells=[{"arm": a, "N": n, "d": 1.0, "label": "BELOW"}
                                            for a, n in cfg["deterministic_cells"]])
            rss_ok = peak_rss_mib() <= cfg["caps"]["rss_mib"]
            man["status"] = outcome(gates_ok, rss_ok, [c["label"] for c in cls["cells"]])
            labels = {(c["arm"], c["N"]): c["label"] for c in cls["cells"]}
            for a, n in cfg["deterministic_cells"]:
                labels[(a, n)] = "BELOW"
            man["sign_reversal_N"] = [n for n in cfg["grid"]
                                      if labels.get(("A", n)) == "BELOW" and labels.get(("B", n)) == "ABOVE"]
    except CapExceeded as exc:
        man.update(status="INVALID", error=str(exc))
    man["cpu_s"] = cpu_seconds() - t0
    man["peak_rss_mib"] = peak_rss_mib()
    if raw:
        np.savez_compressed(out_dir / "raw_counts.npz", **raw)
        man["raw_counts_sha256"] = sha256_file(out_dir / "raw_counts.npz")
    if "cells" in man:
        with open(out_dir / "cells.csv", "w", newline="") as fh:
            cols = ["arm", "N", "D", "positives", "drawn", "mean_d", "sd_d", "se_d", "p_r0",
                    "delta", "z_bonf", "label", "d_of_mean_r", "jensen_gap", "cpu_s"]
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(man["cells"])
    (out_dir / "manifest.json").write_text(json.dumps(man, indent=2, sort_keys=True, default=float))
    return man


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", choices=("pilot", "target"))
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--authorization", type=Path)
    a = ap.parse_args(argv)
    if a.mode == "pilot":
        man = run_pilot(a.output)
    else:
        if a.authorization is None:
            ap.error("target requires --authorization")
        man = run_target(a.output, a.authorization)
    print(man["status"])
    return 0 if man["status"] in ("PILOT_COMPLETE", "COMPLETE", "UNDECIDABLE_AT_BUDGET") else 1


if __name__ == "__main__":
    sys.exit(main())
