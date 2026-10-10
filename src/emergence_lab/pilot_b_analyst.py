"""Pilot B frozen analyst: black-box bounded-speed test (preregistration v1.0-r1, section 5).

ISOLATION CONTRACT (enforced by tests/test_pilot_b.py): this module imports only the
standard library and NumPy. It must never import the Pilot B generator/evaluator
(`emergence_lab.pilot_b`) or any other project module. Its only access to an instance
is the oracle object passed in, through ``oracle.readouts(t, r, arm)``; the declared
design (grid, sigma, n, v_max, z thresholds) is a public input, not instance data.

Verdict vocabulary is exhaustive: NO_RESPONSE, CONSISTENT_WITH_H0, H0_REJECTED.
There is deliberately no verdict asserting proven or strict support.
"""
from __future__ import annotations

import math

import numpy as np

VERDICTS = ("NO_RESPONSE", "CONSISTENT_WITH_H0", "H0_REJECTED")
ARMS = ("control", "do")


def standard_error(sigma: float, n: int) -> float:
    """SE of D = mean(Y_do) - mean(Y_control) under the declared Gaussian detector."""
    return sigma * math.sqrt(2.0 / n)


def analyse(oracle, design: dict) -> dict:
    """Apply the frozen decision rule to one black-box instance.

    ``design`` keys: times, sites, sigma, n, v_max, z_exterior, z_front.
    Every grid cell is queried exactly once per arm (no adaptive querying).
    """
    times = list(design["times"])
    sites = list(design["sites"])
    v_max = design["v_max"]
    z1 = float(design["z_exterior"])
    z2 = float(design["z_front"])
    se = standard_error(float(design["sigma"]), int(design["n"]))

    cells = []
    for t in times:
        for r in sites:
            y_do = np.asarray(oracle.readouts(t, r, "do"), dtype=float)
            y_ctl = np.asarray(oracle.readouts(t, r, "control"), dtype=float)
            d = float(y_do.mean() - y_ctl.mean())
            z = d / se
            exterior = r > v_max * t
            cells.append({
                "t": t, "r": r, "D": d, "SE": se, "z": z,
                "exterior": exterior,
                "detect_front": abs(z) > z2,
                "detect_exterior": bool(exterior and abs(z) > z1),
            })

    r_hat = {}
    for t in times:
        hits = [c["r"] for c in cells if c["t"] == t and c["detect_front"]]
        r_hat[str(t)] = max(hits) if hits else None

    if any(c["detect_exterior"] for c in cells):
        verdict = "H0_REJECTED"
    elif any(c["detect_front"] for c in cells):
        verdict = "CONSISTENT_WITH_H0"
    else:
        verdict = "NO_RESPONSE"
    return {"verdict": verdict, "r_hat": r_hat, "cells": cells,
            "exterior_tests": sum(c["exterior"] for c in cells)}
