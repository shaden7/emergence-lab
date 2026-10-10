"""Preregistered fresh-seed replication of the 4x4 burn-in findings.

See docs/BURNIN_REPLICATION_PREREGISTRATION.md. The experiment itself reuses
``burnin4.burnin_sensitivity`` (paired arms, shared seeds across burn-in arms);
this module fixes the primary hypotheses and evaluates them. Batches within an
arm have disjoint seeds and are the independent replicates; arm-to-arm
contrasts are paired by batch.
"""
import argparse
import json
import math
import platform
from pathlib import Path

import numpy as np

from .burnin4 import burnin_sensitivity

E, M = "mean_energy_per_spin", "mean_abs_magnetization"

# (id, kind, temperature, observable, burn_sweeps, expected sign, original estimate)
# kind "bias": arm mean minus exact reference; kind "shift": arm minus burn-in-0 arm, same seeds.
PRIMARY = (
    ("P1", "bias", 1.5, M, 0, -1, -0.0032),
    ("P2", "bias", 1.5, E, 0, +1, +0.0069),
    ("P3", "shift", 1.5, E, 100, -1, -0.0086),
    ("P4", "shift", 1.5, M, 100, +1, +0.0039),
    ("P5", "shift", 2.269185, E, 100, -1, -0.0113),
    ("P6", "shift", 2.269185, M, 100, +1, +0.0050),
    ("P7", "bias", 1.5, E, 1600, +1, +0.0033),
)
FAMILY_ALPHA = 0.05
REQUIRED_CONFIG = {"temperatures": [1.5, 2.269185], "burn_sweeps_variants": [0, 100, 1600],
                   "chains_per_batch": 4, "sample_sweeps": 800, "sample_every": 5}


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the regularized incomplete beta (Lentz)."""
    tiny = 1e-300
    c, d = 1.0, 1.0 - (a + b) * x / (a + 1.0)
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        for num in (m * (b - m) * x / ((a + m2 - 1) * (a + m2)),
                    -(a + m) * (a + b + m) * x / ((a + m2) * (a + m2 + 1))):
            d = 1.0 + num * d
            d = 1.0 / (d if abs(d) > tiny else tiny)
            c = 1.0 + num / c
            c = c if abs(c) > tiny else tiny
            h *= d * c
        if abs(d * c - 1.0) < 1e-15:
            break
    return h


def _betainc(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1.0 - x) / b


def t_two_sided_p(t: float, df: int) -> float:
    """Two-sided p-value of Student's t with df degrees of freedom."""
    if df < 1 or not math.isfinite(t):
        raise ValueError("finite t and df >= 1 required")
    return _betainc(df / 2.0, 0.5, df / (df + t * t))


def t_quantile_975(df: int) -> float:
    lo, hi = 0.0, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if t_two_sided_p(mid, df) > 0.05 else (lo, mid)
    return (lo + hi) / 2


def one_sample(values) -> dict:
    x = np.asarray(values, dtype=float)
    n = len(x)
    mean, se = float(x.mean()), float(x.std(ddof=1) / math.sqrt(n))
    if se == 0.0:
        return {"n": n, "mean": mean, "stderr": None, "t": None, "p": None, "ci95": None}
    t = mean / se
    q = t_quantile_975(n - 1)
    return {"n": n, "mean": mean, "stderr": se, "t": t, "p": t_two_sided_p(t, n - 1),
            "ci95": [mean - q * se, mean + q * se]}


def check_config(cfg: dict) -> None:
    for key, value in REQUIRED_CONFIG.items():
        if cfg.get(key) != value:
            raise ValueError(f"config deviates from preregistration: {key}")
    if type(cfg.get("batches")) is not int or cfg["batches"] < 20:
        raise ValueError("preregistration requires >= 20 batches")


def _values(report: dict, kind: str, temperature: float, observable: str, burn: int) -> list:
    if kind == "bias":
        arm = next(a for a in report["arms"] if a["burn_sweeps"] == burn)
        return [r["mean"] - r["reference"] for r in arm["batches"]
                if r["temperature"] == temperature and r["observable"] == observable]
    return [c["paired_mean_shift"] for c in report["paired_contrasts"]
            if c["burn_sweeps"] == burn and c["temperature"] == temperature and c["observable"] == observable]


def evaluate(report: dict) -> dict:
    """Apply the preregistered decision rules to a ``burnin_sensitivity`` report."""
    alpha = FAMILY_ALPHA / len(PRIMARY)
    primary = []
    for pid, kind, temp, obs, burn, sign, original in PRIMARY:
        s = one_sample(_values(report, kind, temp, obs, burn))
        significant = s["p"] is not None and s["p"] < alpha
        same_sign = s["t"] is not None and math.copysign(1, s["t"]) == sign
        if pid == "P7":
            if significant and same_sign:
                verdict = "persists"
            elif s["ci95"] is not None and not significant and s["ci95"][0] < original < s["ci95"][1]:
                verdict = "inconclusive"
            elif s["ci95"] is not None and not significant:
                verdict = "not replicated"
            else:
                verdict = "inconclusive"
        else:
            verdict = "replicated" if significant and same_sign else "not replicated"
        primary.append({"id": pid, "kind": kind, "temperature": temp, "observable": obs,
                        "burn_sweeps": burn, "expected_sign": sign, "original_estimate": original,
                        **s, "bonferroni_alpha": alpha, "verdict": verdict})
    exploratory = []
    for arm in report["arms"]:
        for temp in report["config"]["temperatures"]:
            for obs in (E, M):
                exploratory.append({"kind": "bias", "burn_sweeps": arm["burn_sweeps"], "temperature": temp,
                                    "observable": obs, **one_sample(_values(report, "bias", temp, obs,
                                                                            arm["burn_sweeps"]))})
                if arm["burn_sweeps"] != report["arms"][0]["burn_sweeps"]:
                    exploratory.append({"kind": "shift", "burn_sweeps": arm["burn_sweeps"], "temperature": temp,
                                        "observable": obs, **one_sample(_values(report, "shift", temp, obs,
                                                                                arm["burn_sweeps"]))})
    coverage = [{"burn_sweeps": arm["burn_sweeps"], **{k: a[k] for k in
                 ("temperature", "observable", "covered_batches", "batches", "wilson95_low", "wilson95_high")}}
                for arm in report["arms"] for a in arm["aggregates"]]
    return {"primary": primary, "exploratory_uncorrected": exploratory, "coverage_secondary": coverage}


def main() -> None:
    p = argparse.ArgumentParser(description="Preregistered 4x4 burn-in replication")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    cfg = json.loads(a.config.read_text())
    check_config(cfg)
    report = burnin_sensitivity(cfg)
    result = {"config": cfg, "environment": {"python": platform.python_version(), "numpy": np.__version__},
              "analysis": evaluate(report), "raw": report}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    for row in result["analysis"]["primary"]:
        print(f"{row['id']} {row['kind']} T={row['temperature']} {row['observable']} burn={row['burn_sweeps']}: "
              f"{row['mean']:+.5f} ± {row['stderr']:.5f} t={row['t']:+.2f} p={row['p']:.2e} -> {row['verdict']}")


if __name__ == "__main__":
    main()
