"""Pilot A: reference solutions and null controls for interventional propagation tests.

Implements docs/PILOT_A_CAUSAL_PROPAGATION_PREREGISTRATION.md (protocol v1.0),
first stage only: analytic references, independent numerical evaluators, the
classification rule of criterion A3, and the adversarial controls N1-N4.

The interventional witness is S_M(r, t) = |E[O_r(t) | do(I_0)] - E[O_r(t) | do(I_none)]|.
For all four models the control world is the null state (zero field, all-zero
automaton, vacuum), so S equals the response of the intervened world, and
S(0, 0) = 1.

Everything here is deterministic except the N1 correlation control, which uses
one fixed seed. Distance and time are inputs of every model (continuous line for
W/H, ring distance for CA/Q); nothing is inferred from an observed front.

Evidence levels (do not mix them):
- Support classes in SUPPORT_CLASS are mathematical facts about the specified
  models (d'Alembert, positive heat kernel, induction for the automaton,
  analyticity of the quantum walk). They are inputs, not measurements.
- S_num vs S_ref agreement is a numerical observation about this code.
- Detection fronts r_eta(t) are threshold-dependent diagnostics, never a
  statement of strict causality.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
import time
from pathlib import Path

import numpy as np

PROTOCOL_VERSION = "1.0"

# Mathematical support class of each model, fixed by the preregistration (section 3).
SUPPORT_CLASS = {
    "W": "strict",       # |r| > a + c t  =>  u = 0 (d'Alembert)
    "H": "nonstrict",    # positive kernel: u > 0 for all r when t > 0
    "CA": "strict",      # ring distance > n R  =>  z = 0 (induction)
    "Q": "nonstrict",    # analytic in t; far sites generically nonzero for t > 0
}


# ----------------------------------------------------------------------------
# W: wave equation u_tt = c^2 u_xx on R, u(x,0) = 1_[-a,a], u_t(x,0) = 0
# ----------------------------------------------------------------------------

def wave_reference(r: float, t: float, a: float = 0.5, c: float = 1.0) -> float:
    """d'Alembert solution 1/2 [f(r - ct) + f(r + ct)] with f the closed top hat."""
    f = lambda x: 1.0 if abs(x) <= a else 0.0  # noqa: E731
    return 0.5 * (f(r - c * t) + f(r + c * t))


def wave_on_front(r: float, t: float, a: float = 0.5, c: float = 1.0) -> bool:
    """True where r lies on a discontinuity of the top-hat solution.

    The preregistration excludes these points from relative-error checks.
    """
    return any(math.isclose(abs(r - s * c * t), a, abs_tol=1e-12) for s in (-1.0, 1.0))


# ----------------------------------------------------------------------------
# H: heat equation u_t = kappa u_xx on R, same top hat
# ----------------------------------------------------------------------------

def heat_reference(r: float, t: float, a: float = 0.5, kappa: float = 1.0) -> float:
    """Closed form 1/2 [erfc((|r|-a)/s) - erfc((|r|+a)/s)], s = 2 sqrt(kappa t).

    By symmetry only |r| is used; for |r| >= a both erfc arguments are >= 0, so
    the larger term dominates and no catastrophic cancellation occurs. At t = 0
    the initial condition is returned.
    """
    if t == 0:
        return 1.0 if abs(r) <= a else 0.0
    s = 2.0 * math.sqrt(kappa * t)
    x = abs(r)
    if x >= a:
        return 0.5 * (math.erfc((x - a) / s) - math.erfc((x + a) / s))
    # inside the pulse: 1 - 1/2 [erfc((a-x)/s) + erfc((a+x)/s)]
    return 1.0 - 0.5 * (math.erfc((a - x) / s) + math.erfc((a + x) / s))


def heat_quadrature(r: float, t: float, a: float = 0.5, kappa: float = 1.0,
                    nodes: int = 96) -> float:
    """Independent evaluation: Gauss-Legendre quadrature of the heat kernel over [-a, a].

    Shares no code with heat_reference (no erfc). The integrand is a smooth
    Gaussian, so the quadrature is accurate in a *relative* sense even in the
    far tail, until float64 underflow (~1e-308).
    """
    if t == 0:
        return 1.0 if abs(r) <= a else 0.0
    y, w = np.polynomial.legendre.leggauss(nodes)
    y = a * y
    w = a * w
    vals = np.exp(-((r - y) ** 2) / (4.0 * kappa * t))
    return float(np.dot(w, vals) / math.sqrt(4.0 * math.pi * kappa * t))


def heat_explicit_euler(sites, t: float, a: float = 0.5, kappa: float = 1.0,
                        dx: float = 0.5, dt: float = 0.1):
    """N4 artifact demonstration: forward-Euler stencil for the heat equation.

    Each step couples only nearest grid neighbours, so after n = t/dt steps the
    numerical solution is exactly zero beyond a + n dx, although the continuum
    PDE has unbounded support. Returns ({r: value}, hard_front_radius).
    This is a solver artifact, not physics; labelled as such in every output.
    """
    lam = kappa * dt / dx ** 2
    if lam > 0.5:
        raise ValueError("explicit Euler unstable (kappa dt / dx^2 > 1/2)")
    n = int(round(t / dt))
    if not math.isclose(n * dt, t, rel_tol=0, abs_tol=1e-12):
        raise ValueError("t must be an integer multiple of dt")
    rmax = max(abs(float(s)) for s in sites)
    half = int(math.ceil((rmax + a) / dx)) + n + 2
    x = dx * np.arange(-half, half + 1)
    u = (np.abs(x) <= a + 1e-12).astype(float)
    for _ in range(n):
        u[1:-1] = u[1:-1] + lam * (u[2:] - 2 * u[1:-1] + u[:-2])
    out = {}
    for s in sites:
        k = int(round(float(s) / dx)) + half
        if not math.isclose(x[k], float(s), abs_tol=1e-9):
            raise ValueError("site not on Euler grid")
        out[float(s)] = float(u[k])
    support = a + n * dx
    return out, support


# ----------------------------------------------------------------------------
# CA: Boolean OR automaton with radius 1 on Z/LZ
# ----------------------------------------------------------------------------

def ring_distance(r: int, L: int) -> int:
    r %= L
    return min(r, L - r)


def ca_simulate(L: int, n: int) -> np.ndarray:
    """Direct synchronous simulation z_j(n+1) = z_{j-1} or z_j or z_{j+1}; seed bit at 0."""
    z = np.zeros(L, dtype=bool)
    z[0] = True
    for _ in range(n):
        z = z | np.roll(z, 1) | np.roll(z, -1)
    return z


def ca_reference(r: int, n: int, L: int) -> int:
    """Inductive reference (valid for n < L/2): 1 iff ring distance <= n."""
    if not n < L / 2:
        raise ValueError("CA reference requires n < L/2")
    return 1 if ring_distance(r, L) <= n else 0


# ----------------------------------------------------------------------------
# Q: continuous-time quantum walk on a ring, H = -J sum (|j+1><j| + h.c.)
# ----------------------------------------------------------------------------

def ring_hamiltonian(L: int, J: float = 1.0, shortcut: tuple[int, float] | None = None) -> np.ndarray:
    """Single-particle hopping matrix; optional extra hop 0 <-> r* with coupling eps (N2)."""
    H = np.zeros((L, L))
    j = np.arange(L)
    H[j, (j + 1) % L] = -J
    H[(j + 1) % L, j] = -J
    if shortcut is not None:
        rs, eps = shortcut
        H[0, rs % L] += -eps
        H[rs % L, 0] += -eps
    return H


def qwalk_numeric(L: int, t: float, J: float = 1.0,
                  shortcut: tuple[int, float] | None = None) -> np.ndarray:
    """Occupation probabilities |<r| exp(-iHt) |0>|^2 via dense numerical diagonalisation."""
    evals, evecs = np.linalg.eigh(ring_hamiltonian(L, J, shortcut))
    amp = evecs @ (np.exp(-1j * evals * t) * evecs[0, :].conj())
    return np.abs(amp) ** 2


def qwalk_fourier(L: int, t: float, J: float = 1.0) -> np.ndarray:
    """Independent finite-ring reference p_L(r,t) = |1/L sum_k e^{2iJt cos(2pi k/L)} e^{2pi i k r/L}|^2.

    Evaluated by explicit summation (no eigensolver, no FFT), long-double free,
    using math.fsum on real and imaginary parts for each r.
    """
    k = 2.0 * math.pi * np.arange(L) / L
    phase0 = 2.0 * J * t * np.cos(k)
    out = np.empty(L)
    for r in range(L):
        ph = phase0 + k * r
        re = math.fsum(np.cos(ph)) / L
        im = math.fsum(np.sin(ph)) / L
        out[r] = re * re + im * im
    return out


def bessel_j(n: int, x: float, terms: int = 80) -> float:
    """Integer-order Bessel J_n(x) by its power series (adequate for |x| <= ~10)."""
    n = abs(n)
    half = x / 2.0
    acc = []
    term = half ** n / math.factorial(n)
    for m in range(terms):
        acc.append(term)
        term *= -(half * half) / ((m + 1) * (m + 1 + n))
        if abs(term) < 1e-300:
            break
    return math.fsum(acc)


def qwalk_bessel_line(r: int, t: float, J: float = 1.0) -> float:
    """Infinite-line limit |J_r(2Jt)|^2 (a separate limit check, not the ring reference)."""
    return bessel_j(r, 2.0 * J * t) ** 2


def qwalk_taylor(L: int, t: float, J: float = 1.0,
                 shortcut: tuple[int, float] | None = None, tol: float = 1e-20) -> np.ndarray:
    """Independent check of exp(-iHt)|0> by direct Taylor summation (no eigensolver).

    Used as the A5 reference for the shortcut model. Intended for ||tH|| <~ 10.
    """
    H = ring_hamiltonian(L, J, shortcut)
    v = np.zeros(L, dtype=complex)
    v[0] = 1.0
    total = v.copy()
    k = 0
    while True:
        k += 1
        v = (-1j * t / k) * (H @ v)
        total += v
        if np.max(np.abs(v)) < tol or k > 400:
            break
    return np.abs(total) ** 2


# ----------------------------------------------------------------------------
# Classification (criterion A3) and detection fronts (N3 / A6)
# ----------------------------------------------------------------------------

def precision_status(model: str, s_num: float, s_ref: float, *,
                     abs_floor: float = 1e-11, rel: float = 1e-6,
                     censor_below: float = 1e-8, analytic_zero: bool = False,
                     on_front: bool = False) -> str:
    """Return one of: match, mismatch, censored, analytic_zero_ok, analytic_zero_violated, front_excluded.

    - analytic_zero: the reference is zero by theorem (W outside the cone, CA beyond n).
      The numerical value must then be exactly zero; this is a consistency check, not a proof.
    - censored: |S_ref| < censor_below for a nonstrict model; never reported as "zero".
    """
    if on_front:
        return "front_excluded"
    if analytic_zero:
        return "analytic_zero_ok" if s_num == 0.0 else "analytic_zero_violated"
    if s_ref < censor_below:
        return "censored"
    tol = max(abs_floor, rel * s_ref)
    return "match" if abs(s_num - s_ref) <= tol else "mismatch"


def detection_front(sites, values, eta: float):
    """r_eta = max{r among measured sites: Q(r) >= eta}, else None (undefined)."""
    hits = [r for r, q in zip(sites, values) if q >= eta]
    return max(hits) if hits else None


# ----------------------------------------------------------------------------
# N1: correlation without intervention effect
# ----------------------------------------------------------------------------

def null_correlation(seed: int, samples: int, shift: float = 1.0) -> dict:
    """Hidden common cause Z seen at two sites; intervention acts only at site A.

    X_A = Z + e_A (+ shift under do(I_0)), X_B = Z + e_B. Paired background
    (same Z, e_A, e_B in both worlds). Prediction: corr(X_A, X_B) > 0 but the
    interventional difference at B is exactly zero for every sample.
    """
    rng = np.random.default_rng(seed)
    z = rng.standard_normal(samples)
    ea = rng.standard_normal(samples)
    eb = rng.standard_normal(samples)
    xa_ctrl, xb_ctrl = z + ea, z + eb
    xa_do, xb_do = z + ea + shift, z + eb
    corr = float(np.corrcoef(xa_ctrl, xb_ctrl)[0, 1])
    # Fisher-z 95% interval for the observational correlation
    fz = math.atanh(corr)
    se = 1.0 / math.sqrt(samples - 3)
    ci = (math.tanh(fz - 1.96 * se), math.tanh(fz + 1.96 * se))
    return {
        "observational_corr": corr,
        "observational_corr_ci95": ci,
        "remote_delta_max_abs": float(np.max(np.abs(xb_do - xb_ctrl))),
        "local_delta_mean": float(np.mean(xa_do - xa_ctrl)),
        # manipulation check: the intervention must change the local observable
        "a1_pass": bool(ci[0] > 0 and np.all(xb_do == xb_ctrl) and shift != 0
                        and math.isclose(float(np.mean(xa_do - xa_ctrl)), shift)),
    }


# ----------------------------------------------------------------------------
# Runner (development phase by default; holdout requires an explicit flag)
# ----------------------------------------------------------------------------

def _rows_for_phase(cfg: dict, phase: str):
    p, tol = cfg["parameters"], cfg["tolerance"]
    g = cfg[phase]
    a, c, kappa, J = p["a"], p["c"], p["kappa"], p["J"]
    rows = []

    def add(model, L, r, t, s_num, s_ref, status, **extra):
        rows.append({"model": model, "phase": phase, "L": L, "r": r, "t": t,
                     "S_num": s_num, "S_ref": s_ref,
                     "abs_err": None if s_ref is None else abs(s_num - s_ref),
                     "precision_status": status, "support_class": SUPPORT_CLASS.get(model, ""),
                     **extra})

    kw = dict(abs_floor=tol["abs_floor"], rel=tol["rel"], censor_below=tol["censor_below"])
    for t in g["continuum_times"]:
        for r in g["sites"]:
            # W: the numerical value is the closed form itself (no PDE solver in this stage)
            ref = wave_reference(r, t, a, c)
            outside = abs(r) > a + c * t
            # Zeros of the closed form are exact: outside the cone (support theorem) and,
            # for t > a, between the two separating pulses (|r| < t - a).
            add("W", None, r, t, ref, ref,
                precision_status("W", ref, ref, analytic_zero=(ref == 0.0),
                                 on_front=wave_on_front(r, t, a, c), **kw),
                outside_cone=outside)
            ref_h = heat_reference(r, t, a, kappa)
            num_h = heat_quadrature(r, t, a, kappa)
            add("H", None, r, t, num_h, ref_h, precision_status("H", num_h, ref_h, **kw))
    for L in g["ring_sizes"]:
        for n in g["ca_steps"]:
            z = ca_simulate(L, n)
            for r in g["sites"]:
                ref = ca_reference(r, n, L)
                add("CA", L, r, n, float(z[r % L]), float(ref),
                    precision_status("CA", float(z[r % L]), float(ref),
                                     analytic_zero=(ref == 0), **kw))
        for t in g["continuum_times"]:
            num = qwalk_numeric(L, t, J)
            ref = qwalk_fourier(L, t, J)
            norm_err = abs(math.fsum(num) - 1.0)
            for r in g["sites"]:
                add("Q", L, r, t, float(num[r]), float(ref[r]),
                    precision_status("Q", float(num[r]), float(ref[r]), **kw),
                    bessel_line=qwalk_bessel_line(r, t, J),
                    norm_err=norm_err)
    return rows


def _fronts(cfg: dict, phase: str):
    g, p = cfg[phase], cfg["parameters"]
    out = []
    for L in g["ring_sizes"]:
        for t in g["continuum_times"]:
            ref = qwalk_fourier(L, t, p["J"])
            vals = [ref[r] for r in g["sites"]]
            for eta in cfg["thresholds"]:
                out.append({"model": "Q", "L": L, "t": t, "eta": eta,
                            "r_eta": detection_front(g["sites"], vals, eta),
                            "note": "threshold diagnostic; Q support is nonstrict"})
    for t in g["continuum_times"]:
        vals = [heat_reference(r, t, p["a"], p["kappa"]) for r in g["sites"]]
        for eta in cfg["thresholds"]:
            out.append({"model": "H", "L": None, "t": t, "eta": eta,
                        "r_eta": detection_front(g["sites"], vals, eta),
                        "note": "threshold diagnostic; H support is nonstrict"})
    return out


def _shortcut(cfg: dict):
    sc, J = cfg["shortcut"], cfg["parameters"]["J"]
    tol = cfg["tolerance"]
    out = []
    for L in sc["ring_sizes"]:
        rs = L // 4
        for t in sc["times"]:
            num = qwalk_numeric(L, t, J, (rs, sc["epsilon"]))
            ref = qwalk_taylor(L, t, J, (rs, sc["epsilon"]))
            local = qwalk_fourier(L, t, J)[rs]
            out.append({"L": L, "r_star": rs, "t": t, "S_num": float(num[rs]),
                        "S_ref_taylor": float(ref[rs]), "S_without_shortcut": float(local),
                        "precision_status": precision_status(
                            "Q", float(num[rs]), float(ref[rs]),
                            abs_floor=tol["abs_floor"], rel=tol["rel"],
                            censor_below=tol["censor_below"]),
                        "note": "far response via the built-in edge; distance measured in the original ring metric"})
    return out


def _far_witness(cfg: dict, rows):
    out = []
    for t, r in cfg["far_witnesses"]:
        sel = [x for x in rows if x["model"] in ("W", "H", "Q") and x["t"] == t and x["r"] == r]
        for x in sel:
            out.append({k: x[k] for k in ("model", "L", "r", "t", "S_num", "S_ref", "precision_status")})
    return out


def run(cfg: dict, phase: str = "development") -> dict:
    t0 = time.process_time()
    rows = _rows_for_phase(cfg, phase)
    a = cfg["parameters"]["a"]
    euler, euler_support = heat_explicit_euler([4, 6], 1.0, a, cfg["parameters"]["kappa"])
    result = {
        "phase": phase,
        "rows": rows,
        "fronts": _fronts(cfg, phase),
        "shortcut_n2": _shortcut(cfg) if phase == "development" else None,
        "null_n1": null_correlation(cfg["null_correlation"]["seed"],
                                    cfg["null_correlation"]["samples"],
                                    cfg["null_correlation"]["intervention_shift"]),
        "euler_artifact_n4": {
            "label": "SOLVER ARTIFACT DEMO (not physics)", "dx": 0.5, "dt": 0.1, "t": 1.0,
            "numerical_hard_front": euler_support,
            "values": {str(k): v for k, v in euler.items()},
            "continuum_reference": {str(r): heat_reference(r, 1.0, a, cfg["parameters"]["kappa"])
                                    for r in (4, 6)},
        },
    }
    result["far_witness_a3"] = _far_witness(cfg, rows)
    statuses = [x["precision_status"] for x in rows]
    result["summary"] = {s: statuses.count(s) for s in sorted(set(statuses))}
    result["a1_pass"] = result["null_n1"]["a1_pass"]
    # A2: no theorem zero violated, and every W site outside |r| <= a + ct carries S = 0.
    result["a2_pass"] = ("analytic_zero_violated" not in statuses
                         and all(x["S_num"] == 0.0 for x in rows
                                 if x["model"] == "W" and x.get("outside_cone")))
    result["a3_pass"] = all(x["precision_status"] == "match" for x in result["far_witness_a3"]
                            if x["model"] in ("H", "Q"))
    q_rows = [x for x in rows if x["model"] == "Q"]
    result["a4_pass"] = (all(x["precision_status"] in ("match", "censored") for x in q_rows)
                         and max(x["norm_err"] for x in q_rows) < 1e-12)
    result["no_mismatch"] = "mismatch" not in statuses
    if result["shortcut_n2"] is not None:
        result["a5_pass"] = all(x["precision_status"] == "match" and x["S_num"] > 1e3 * x["S_without_shortcut"]
                                for x in result["shortcut_n2"])
    result["cpu_seconds"] = time.process_time() - t0
    return result


def _manifest(cfg_path: Path, cfg_bytes: bytes, phase: str) -> dict:
    import os
    return {
        "protocol_version": PROTOCOL_VERSION,
        "config": str(cfg_path),
        "config_sha256": hashlib.sha256(cfg_bytes).hexdigest(),
        "git_sha": os.environ.get("GIT_SHA"),
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.platform(),
        "phase": phase,
        "metric": {"W": "continuous line |x|", "H": "continuous line |x|",
                   "CA": "ring distance min(r, L-r)", "Q": "ring distance min(r, L-r)"},
        "time": {"W": "continuous t (c=1)", "H": "continuous t (kappa=1)",
                 "CA": "integer ticks", "Q": "continuous t (J=1)"},
        "deviations": [
            "W has no independent PDE solver in this stage; S_num is the closed form.",
            "N2 shortcut times (0.5, 1, 2) are a development choice; the protocol fixes only eps and L.",
            "N4 Euler grid (dx=0.5, dt=0.1) is a demonstration choice; the protocol does not fix it.",
            "N5 measurement noise (optional in the protocol) is not implemented.",
        ],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default="configs/pilot_a.json")
    ap.add_argument("--phase", choices=("development", "holdout"), default="development")
    ap.add_argument("--allow-holdout", action="store_true",
                    help="required for the holdout phase; evaluate it once, unchanged")
    ap.add_argument("--output", required=True, help="directory for result.json and rows.csv")
    args = ap.parse_args(argv)
    if args.phase == "holdout" and not args.allow_holdout:
        ap.error("holdout evaluation requires --allow-holdout (one-shot, no retuning)")
    cfg_path = Path(args.config)
    cfg_bytes = cfg_path.read_bytes()
    cfg = json.loads(cfg_bytes)
    proto = Path(cfg["protocol"])
    if proto.exists() and hashlib.sha256(proto.read_bytes()).hexdigest() != cfg["protocol_sha256"]:
        raise SystemExit("protocol file differs from pinned preregistration digest")
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    result = run(cfg, args.phase)
    result["manifest"] = _manifest(cfg_path, cfg_bytes, args.phase)
    with open(out / "rows.csv", "w", newline="") as fh:
        cols = ["model", "phase", "L", "r", "t", "S_num", "S_ref", "abs_err",
                "precision_status", "support_class", "outside_cone", "bessel_line", "norm_err"]
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for row in result["rows"]:
            w.writerow({k: (repr(v) if isinstance(v, float) else v) for k, v in row.items()})
    rows_digest = hashlib.sha256((out / "rows.csv").read_bytes()).hexdigest()
    result["manifest"]["rows_csv_sha256"] = rows_digest
    (out / "result.json").write_text(json.dumps(result, indent=1, default=float))
    keys = [k for k in result if k.endswith("_pass")] + ["no_mismatch"]
    print(json.dumps({k: result[k] for k in keys} | {"summary": result["summary"],
                     "rows_csv_sha256": rows_digest}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
