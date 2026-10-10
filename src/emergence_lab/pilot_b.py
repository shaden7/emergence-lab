"""Pilot B stage 1: generator, noisy oracle, exact references and evaluator.

Frozen design: docs/PILOT_B_BLINDED_INTERVENTION_PREREGISTRATION.md (v1.0-r1, Git blob
dd5dbefe950add3341366224b76ba179326282c8) and configs/pilot_b.json (SHA-256 3fc24afa...).
Methodology only: every instance is a stipulated linear ring dynamics whose support class is
known to this evaluator. Nothing here concerns physical spacetime or signalling.

The analyst lives in ``emergence_lab.pilot_b_analyst`` and never imports this module.

Implementation choices not fixed numerically by the preregistration (recorded in the stage-1
note, fixed before any blind key exists):
* parameter draws: one Generator ``default_rng(SeedSequence([key_int, 1]))``; classes are drawn
  in config order S1,S2,S3,C1,C2,N1,N2,N3, each instance's parameters in the order listed in
  ``_draw_params``; afterwards ``perm = rng.permutation(40)`` and instance index ``i`` is the
  ``perm[i]``-th drawn instance.
* ``key_int = int.from_bytes(key[:16], "big")`` for both parameter and noise streams.
* cell index ``c = time_index * len(sites) + site_index``; arm index control=0, do=1.
* circulant convention ``x_{t+1}(i) = sum_j a_j x_t(i - j)``, so ``A e_0`` carries ``a_j`` at
  site ``j``; ring Laplacian ``(Du)(i) = u(i+1) + u(i-1) - 2u(i)``.
* the control arm starts from x_0 = 0, so its noise-free value is exactly 0 for every
  (linear) member; for C2 the do arm is identical to control.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np

from emergence_lab import pilot_b_analyst as analyst

PREREG_PATH = "docs/PILOT_B_BLINDED_INTERVENTION_PREREGISTRATION.md"
CONFIG_PATH = "configs/pilot_b.json"
PREREG_BLOB_SHA = "dd5dbefe950add3341366224b76ba179326282c8"
CONFIG_SHA256 = "3fc24afa33c31c91eb0f96be8ac7b785a7abb13083725fd39d6df406640d6d2e"
CLASS_ORDER = ("S1", "S2", "S3", "C1", "C2", "N1", "N2", "N3")
GROUP = {"S1": "strict", "S2": "strict", "S3": "strict", "C1": "null", "C2": "null",
         "N1": "nonstrict", "N2": "nonstrict", "N3": "nonstrict"}
REFERENCE_TOL = 1e-12
FORBIDDEN_VERDICT_TERMS = ("strict", "proved", "causal cone", "speed of light")
CSV_FIELDS = ("instance", "t", "r", "exterior", "D", "SE", "z", "detect_front",
              "detect_exterior", "verdict", "class", "S_true")


# ----------------------------------------------------------------------------- keys
def dev_key(cfg: dict) -> bytes:
    return hashlib.sha256(cfg["dev_key"].encode("ascii")).digest()


def blind_key(round_number: int, randomness_hex: str) -> bytes:
    """Section 6.3: SHA-256(b'pilot-b-v1|' + ascii_decimal(R) + b'|' + bytes.fromhex(rand))."""
    if not isinstance(round_number, int) or round_number < 1:
        raise ValueError("round must be a positive integer")
    raw = bytes.fromhex(randomness_hex)
    if len(raw) != 32 or len(randomness_hex) != 64:
        raise ValueError("randomness must be 64 hex characters")
    return hashlib.sha256(b"pilot-b-v1|" + str(round_number).encode("ascii") + b"|" + raw).digest()


def key_int(key: bytes) -> int:
    return int.from_bytes(key[:16], "big")


# ------------------------------------------------------------------------ generator
def _sym_stencil(rng, k):
    half = rng.uniform(0.1, 1.0, k + 1)  # w_0 .. w_k
    w = np.concatenate([half[:0:-1], half])
    return (w / w.sum()).tolist()


def _draw_params(code: str, rng, cfg: dict) -> dict:
    if code in ("S1", "C2"):
        k = int(rng.integers(1, 5))
        w = rng.uniform(0.1, 1.0, 2 * k + 1)
        return {"k": k, "weights": (w / w.sum()).tolist()}
    if code == "S2":
        return {"k": 1, "c2": float(rng.uniform(0.25, 1.0))}
    if code == "S3":
        k = int(rng.integers(1, 5))
        signs = rng.integers(0, 2, 2 * k + 1) * 2 - 1
        mags = rng.uniform(0.1, 1.0, 2 * k + 1)
        return {"k": k, "weights": (signs * mags / mags.sum()).tolist()}
    if code == "C1":
        return {"k": 0}
    if code == "N1":
        return {"gamma": float(math.exp(rng.uniform(math.log(0.2), math.log(1.0))))}
    if code == "N2":
        return {"alpha": float(rng.uniform(2.0, 4.0))}
    if code == "N3":
        k = int(rng.integers(1, 3))
        w = _sym_stencil(rng, k)
        eps = float(math.exp(rng.uniform(math.log(1e-6), math.log(1e-2))))
        d = int(rng.integers(20, 101))
        return {"k": k, "weights": w, "epsilon": eps, "d": d}
    raise ValueError(code)


def instances(key: bytes, cfg: dict) -> list[dict]:
    rng = np.random.default_rng(np.random.SeedSequence([key_int(key), 1]))
    drawn = []
    for code in CLASS_ORDER:
        for _ in range(cfg["class_counts"][code]):
            drawn.append({"class": code, "group": GROUP[code], "params": _draw_params(code, rng, cfg)})
    perm = rng.permutation(len(drawn))
    out = []
    for i, j in enumerate(perm):
        inst = dict(drawn[int(j)])
        inst["index"] = i
        out.append(inst)
    return out


# ------------------------------------------------------------------ exact references
def _circulant_column(L: int, weights, offsets) -> np.ndarray:
    a = np.zeros(L)
    for w, j in zip(weights, offsets):
        a[j % L] += w
    return a


def _circulant(a: np.ndarray) -> np.ndarray:
    L = len(a)
    idx = (np.arange(L)[:, None] - np.arange(L)[None, :]) % L
    return a[idx]


def _laplacian(L: int) -> np.ndarray:
    return _circulant(_circulant_column(L, [1.0, -2.0, 1.0], [-1, 0, 1]))


def _stencil_column(inst: dict, L: int) -> np.ndarray | None:
    p, c = inst["params"], inst["class"]
    if c in ("S1", "S3"):
        k = p["k"]
        return _circulant_column(L, p["weights"], range(-k, k + 1))
    if c == "C1":
        return _circulant_column(L, [1.0], [0])
    if c == "N2":
        offs = np.arange(-127, 129)
        w = (1.0 + np.abs(offs)) ** (-p["alpha"])
        return _circulant_column(L, w / w.sum(), offs)
    if c == "N3":
        k = p["k"]
        return _circulant_column(L, p["weights"], range(-k, k + 1))
    return None


def _n3_matrix(inst: dict, L: int) -> np.ndarray:
    B = _circulant(_stencil_column(inst, L))
    eps, d = inst["params"]["epsilon"], inst["params"]["d"]
    A = B.copy()
    A[0, d] += eps
    A[d, 0] += eps
    A[0, 0] -= eps
    A[d, d] -= eps
    return A


def response_matrix_path(inst: dict, L: int, times) -> dict[int, np.ndarray]:
    """Path 1: matrix power (companion matrix for S2, expm for N1). Column of G_t e_0."""
    c, p = inst["class"], inst["params"]
    e0 = np.zeros(L)
    e0[0] = 1.0
    out = {}
    if c == "C2":
        return {t: np.zeros(L) for t in times}
    if c == "N1":
        from scipy.linalg import expm
        D = _laplacian(L)
        return {t: expm(t * p["gamma"] * D)[:, 0].copy() for t in times}
    if c == "S2":
        D = _laplacian(L)
        I = np.eye(L)
        M = np.block([[2 * I + p["c2"] * D, -I], [I, np.zeros((L, L))]])
        v0 = np.concatenate([e0, e0])
        for t in times:
            out[t] = (np.linalg.matrix_power(M, t) @ v0)[:L]
        return out
    A = _n3_matrix(inst, L) if c == "N3" else _circulant(_stencil_column(inst, L))
    for t in times:
        out[t] = np.linalg.matrix_power(A, t)[:, 0].copy()
    return out


def response_spectral_path(inst: dict, L: int, times) -> dict[int, np.ndarray]:
    """Path 2: explicit circulant Fourier sum; eigh for the non-translation-invariant N3."""
    c, p = inst["class"], inst["params"]
    if c == "C2":
        return {t: np.zeros(L) for t in times}
    if c == "N3":
        A = _n3_matrix(inst, L)
        w, V = np.linalg.eigh(A)
        return {t: V @ (w ** t * V[0, :]) for t in times}
    q = np.arange(L)
    j = np.arange(L)
    phase = np.exp(-2j * np.pi * np.outer(q, j) / L)  # phase[q, j] = exp(-2 pi i q j / L)
    lap_eig = 2.0 * np.cos(2 * np.pi * q / L) - 2.0
    if c == "N1":
        hats = {t: np.exp(t * p["gamma"] * lap_eig) for t in times}
    elif c == "S2":
        hats, prev, cur = {}, np.ones(L), np.ones(L)
        for step in range(1, max(times) + 1):
            prev, cur = cur, (2.0 + p["c2"] * lap_eig) * cur - prev
            if step in times:
                hats[step] = cur.copy()
    else:
        a_hat = phase @ _stencil_column(inst, L)
        hats = {t: a_hat ** t for t in times}
    inv = np.conj(phase) / L  # inv[q, r] = exp(+2 pi i q r / L) / L
    out = {}
    for t in times:
        val = hats[t] @ inv
        if np.max(np.abs(val.imag)) > 1e-12:
            raise RuntimeError("non-real Fourier reconstruction")
        out[t] = val.real
    return out


def true_support_radius(inst: dict, t: int) -> int | None:
    """Radius bound k*t for H0-satisfying instances (C2: no support; C1: 0)."""
    c = inst["class"]
    if c == "C2":
        return None
    if c == "C1":
        return 0
    if inst["group"] == "strict":
        return inst["params"]["k"] * t
    raise ValueError("no finite radius for non-strict instance")


# --------------------------------------------------------------------------- oracle
class Oracle:
    """Noisy black box. Each grid (t, r, arm) may be read exactly once (50 readouts)."""

    def __init__(self, truth: dict, index: int, kint: int, cfg: dict, sigma: float | None = None):
        self._truth = truth  # {(t, r): S}
        self._index = index
        self._kint = kint
        self._times = list(cfg["times"])
        self._sites = list(cfg["sites"])
        self._n = int(cfg["readouts_per_arm_per_cell"])
        self._sigma = float(cfg["sigma"] if sigma is None else sigma)
        self._used = set()

    def readouts(self, t: int, r: int, arm: str) -> np.ndarray:
        if t not in self._times or r not in self._sites or arm not in analyst.ARMS:
            raise ValueError("query outside the declared grid")
        if (t, r, arm) in self._used:
            raise RuntimeError("repeated query: budget is one batch per cell and arm")
        self._used.add((t, r, arm))
        c = self._times.index(t) * len(self._sites) + self._sites.index(r)
        a = analyst.ARMS.index(arm)
        rng = np.random.Generator(np.random.PCG64(
            np.random.SeedSequence([self._kint, 2, self._index, c, a])))
        mean = self._truth[(t, r)] if arm == "do" else 0.0
        return mean + self._sigma * rng.standard_normal(self._n)

    @property
    def queries(self) -> int:
        return len(self._used)


# ------------------------------------------------------------------------ evaluator
def design_from_config(cfg: dict) -> dict:
    return {"times": cfg["times"], "sites": cfg["sites"], "sigma": cfg["sigma"],
            "n": cfg["readouts_per_arm_per_cell"], "v_max": cfg["v_max"],
            "z_exterior": cfg["z_exterior"], "z_front": cfg["z_front"]}


def _wilson(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return None
    ph = k / n
    den = 1 + z * z / n
    centre = (ph + z * z / (2 * n)) / den
    half = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    lo = 0.0 if k == 0 else max(0.0, centre - half)
    hi = 1.0 if k == n else min(1.0, centre + half)
    return [lo, hi]


def evaluate(key: bytes, cfg: dict) -> tuple[dict, list[dict]]:
    L, times, sites = cfg["ring_L"], list(cfg["times"]), list(cfg["sites"])
    v_max = cfg["v_max"]
    design = design_from_config(cfg)
    se = analyst.standard_error(cfg["sigma"], cfg["readouts_per_arm_per_cell"])
    det_limit = cfg["z_exterior"] * se
    kint = key_int(key)
    insts = instances(key, cfg)
    rows, records = [], []
    g0_max_diff, g0_nonzero_exterior = 0.0, []
    for inst in insts:
        mp = response_matrix_path(inst, L, times)
        sp = response_spectral_path(inst, L, times)
        diff = max(float(np.max(np.abs(mp[t] - sp[t]))) for t in times)
        g0_max_diff = max(g0_max_diff, diff)
        truth = {(t, r): float(mp[t][r]) for t in times for r in sites}
        if inst["group"] != "nonstrict":
            for t in times:
                if np.any(mp[t][[r for r in range(L) if min(r, L - r) > v_max * t]] != 0.0):
                    g0_nonzero_exterior.append(inst["index"])
        oracle = Oracle(truth, inst["index"], kint, cfg)
        res = analyst.analyse(oracle, design)
        if oracle.queries != 2 * len(times) * len(sites):
            raise RuntimeError("analyst did not use the fixed budget")
        max_ext = max(abs(truth[(t, r)]) for t in times for r in sites if r > v_max * t)
        rec = {"index": inst["index"], "class": inst["class"], "group": inst["group"],
               "params": inst["params"], "verdict": res["verdict"], "r_hat": res["r_hat"],
               "reference_max_abs_diff": diff, "max_abs_exterior_S": max_ext}
        if inst["group"] != "nonstrict":
            rec["true_radius"] = {str(t): true_support_radius(inst, t) for t in times}
        spurious_cells = []
        for cell in res["cells"]:
            s = truth[(cell["t"], cell["r"])]
            rows.append({"instance": inst["index"], "t": cell["t"], "r": cell["r"],
                         "exterior": int(cell["exterior"]), "D": repr(cell["D"]),
                         "SE": repr(cell["SE"]), "z": repr(cell["z"]),
                         "detect_front": int(cell["detect_front"]),
                         "detect_exterior": int(cell["detect_exterior"]),
                         "verdict": res["verdict"], "class": inst["class"], "S_true": repr(s)})
            if inst["group"] == "null":
                outside = inst["class"] == "C2" or cell["r"] > 0
                if (outside and cell["detect_front"]) or cell["detect_exterior"]:
                    spurious_cells.append({"t": cell["t"], "r": cell["r"], "z": cell["z"]})
        if inst["group"] == "null":
            rec["spurious_cells"] = spurious_cells
        if inst["class"] == "C1":
            rec["r0_detected_all_t"] = all(c["detect_front"] for c in res["cells"] if c["r"] == 0)
        if inst["group"] == "strict":
            k = inst["params"]["k"]
            rec["speed_overestimate"] = any(
                res["r_hat"][str(t)] is not None and res["r_hat"][str(t)] > k * t for t in times)
        records.append(rec)

    P = [r for r in records if r["group"] != "nonstrict"]
    K = [r for r in records if r["group"] == "strict"]
    C = [r for r in records if r["group"] == "null"]
    N = [r for r in records if r["group"] == "nonstrict"]
    g = cfg["gates"]
    false_rej = [r["index"] for r in P if r["verdict"] == "H0_REJECTED"]
    over = [r["index"] for r in K if r["speed_overestimate"]]
    spurious = [r["index"] for r in C if r["spurious_cells"]]
    c1_ok = all(r["r0_detected_all_t"] for r in C if r["class"] == "C1")
    detectable = [r for r in N if r["max_abs_exterior_S"] >= g["B_G4_detectable_factor"] * det_limit]
    power_hits = sum(r["verdict"] == "H0_REJECTED" for r in detectable)
    power_frac = power_hits / len(detectable) if detectable else None
    verdict_terms_ok = all(r["verdict"] in analyst.VERDICTS and
                           not any(w in r["verdict"].lower() for w in FORBIDDEN_VERDICT_TERMS)
                           for r in records)
    undetected_N = [{"index": r["index"], "class": r["class"], "verdict": r["verdict"],
                     "max_abs_exterior_S": r["max_abs_exterior_S"], "detection_limit": det_limit}
                    for r in N if r["verdict"] != "H0_REJECTED"]
    gates = {
        "B_G0": {"pass": g0_max_diff <= g["reference_tolerance"] and not g0_nonzero_exterior,
                 "max_abs_diff": g0_max_diff, "nonzero_exterior_instances": g0_nonzero_exterior},
        "B_G1": {"pass": len(false_rej) <= g["B_G1_max_false_rejections_of_24"],
                 "false_rejections": false_rej, "of": len(P)},
        "B_G2": {"pass": len(over) <= g["B_G2_max_speed_overestimates_of_16"],
                 "speed_overestimates": over, "of": len(K)},
        "B_G3": {"pass": c1_ok and len(spurious) <= g["B_G3_max_spurious_null_controls_of_8"],
                 "c1_r0_all_detected": c1_ok, "spurious_instances": spurious, "of": len(C)},
        "B_G4": {"pass": (power_frac is None or power_frac >= g["B_G4_min_power_detectable"]),
                 "detectable": [r["index"] for r in detectable], "rejected": power_hits,
                 "fraction": power_frac,
                 "power_untested": len(detectable) < 3,
                 "threshold_abs_S": g["B_G4_detectable_factor"] * det_limit},
        "B_G5": {"pass": verdict_terms_ok, "undetected_nonstrict": undetected_N},
    }
    by_class = {}
    for code in CLASS_ORDER:
        rs = [r for r in records if r["class"] == code]
        rej = sum(r["verdict"] == "H0_REJECTED" for r in rs)
        by_class[code] = {"n": len(rs), "H0_REJECTED": rej, "wilson95_rejected": _wilson(rej, len(rs))}
    summary = {"gates": gates, "by_class": by_class, "detection_limit": det_limit, "SE": se,
               "instances": records}
    return summary, rows


# ------------------------------------------------------------------------ provenance
def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def validate_frozen_files(root: Path = Path(".")) -> dict:
    prereg = (root / PREREG_PATH).read_bytes()
    cfg_raw = (root / CONFIG_PATH).read_bytes()
    if git_blob_sha(prereg) != PREREG_BLOB_SHA:
        raise ValueError("Pilot B preregistration changed from the pinned blob")
    if hashlib.sha256(cfg_raw).hexdigest() != CONFIG_SHA256:
        raise ValueError("Pilot B config changed from the pinned SHA-256")
    return {"prereg_blob_sha": PREREG_BLOB_SHA, "config_sha256": CONFIG_SHA256}


def rows_to_csv(rows: list[dict]) -> bytes:
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=CSV_FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode()


def run(phase: str, output: Path, beacon: dict | None = None, root: Path = Path(".")) -> dict:
    pins = validate_frozen_files(root)
    cfg = json.loads((root / CONFIG_PATH).read_text())
    if phase == "dev":
        key = dev_key(cfg)
        key_source = {"dev_key": cfg["dev_key"]}
    elif phase == "blind":
        if not beacon or not beacon.get("signature_verified"):
            raise RuntimeError("blind phase requires a verified drand quicknet beacon record")
        key = blind_key(int(beacon["round"]), beacon["randomness"])
        key_source = {"beacon": beacon}
    else:
        raise ValueError(phase)
    t0 = time.process_time()
    summary, rows = evaluate(key, cfg)
    cpu = time.process_time() - t0
    output.mkdir(parents=True, exist_ok=True)
    csv_bytes = rows_to_csv(rows)
    (output / "rows.csv").write_bytes(csv_bytes)
    result = {"phase": phase, "key_hex": key.hex(), "key_source": key_source, **pins,
              "summary": summary, "rows_sha256": hashlib.sha256(csv_bytes).hexdigest()}
    result_bytes = (json.dumps(result, indent=1, sort_keys=True) + "\n").encode()
    (output / "result.json").write_bytes(result_bytes)
    manifest = {"phase": phase, "code_commit": os.environ.get("GIT_SHA"),
                "python": platform.python_version(), "numpy": np.__version__,
                "scipy": __import__("scipy").__version__, "cpu_seconds": round(cpu, 3),
                "outputs": {"rows.csv": hashlib.sha256(csv_bytes).hexdigest(),
                            "result.json": hashlib.sha256(result_bytes).hexdigest()},
                "budget": cfg["budget"]}
    all_pass = all(g["pass"] for g in summary["gates"].values())
    manifest["gates_pass_B_G0_to_G5"] = all_pass
    (output / "manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    return {"manifest": manifest, "gates": summary["gates"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--phase", choices=("dev", "blind"), default="dev")
    ap.add_argument("--beacon", type=Path, help="verified beacon JSON (blind phase only)")
    ap.add_argument("--allow-blind", action="store_true")
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args(argv)
    beacon = None
    if a.phase == "blind":
        if not a.allow_blind:
            ap.error("the blind evaluation runs once, on main, via GitHub Actions: pass --allow-blind")
        beacon = json.loads(a.beacon.read_text())
    out = run(a.phase, a.output, beacon)
    for name, g in out["gates"].items():
        brief = {k: v for k, v in g.items() if k not in ("undetected_nonstrict",)}
        print(f"{name}: {'PASS' if g['pass'] else 'FAIL'} {json.dumps(brief)}")
    print("manifest:", json.dumps(out["manifest"], sort_keys=True))
    return 0 if out["manifest"]["gates_pass_B_G0_to_G5"] else 1


if __name__ == "__main__":
    sys.exit(main())
