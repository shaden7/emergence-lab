"""S0 spectral-dimension reference kernels (Issue #37).

Preregistration: docs/SPECTRAL_S0_PREREGISTRATION.md.
Deterministic analytic/finite-graph instrument calibration only. The functions
do not classify emergent dimension or run stochastic tree-family experiments.
"""
from __future__ import annotations

import math
from collections.abc import Iterable

import numpy as np
from scipy.sparse.csgraph import connected_components

from emergence_lab.dimension_d1 import Graph


MAX_TRANSITION_OPS = 100_000_000


def graph_even_returns(
    graph: Graph,
    source: int,
    half_times: Iterable[int],
    *,
    max_transition_ops: int = MAX_TRANSITION_OPS,
) -> dict[int, float]:
    """Return P^(2t)[source,source] from the reversible half-kernel identity.

    The graph must be connected, undirected and simple with no isolated
    vertices. Operation limit is a conservative directed-edge-step proxy,
    not an exact CPU or peak-memory measurement. Uses one float64 CSR kernel.
    """
    times = list(half_times)
    if not times or any(not isinstance(t, (int, np.integer)) or t < 1 for t in times):
        raise ValueError("half_times must be nonempty positive integers")
    if not isinstance(source, (int, np.integer)) or not 0 <= source < graph.n:
        raise ValueError("invalid source vertex")
    if graph.n < 2:
        raise ValueError("at least two vertices are required")
    degree = graph.degrees
    if np.any(degree <= 0):
        raise ValueError("graph contains isolated vertices")
    a = graph.csr()
    if a.diagonal().any() or (a != a.T).nnz or np.any(a.data != 1):
        raise ValueError("graph must be undirected, loop-free and unweighted")
    if connected_components(a, directed=False, return_labels=False) != 1:
        raise ValueError("graph must be connected")
    max_t = max(times)
    if max_transition_ops < 0 or max_t * a.nnz > max_transition_ops:
        raise ValueError("transition operation budget exceeded")

    inverse_degree = 1.0 / degree.astype(np.float64)
    transition = a.multiply(inverse_degree[:, None]).tocsr()
    row = np.zeros(graph.n, dtype=np.float64)
    row[int(source)] = 1.0
    wanted = set(times)
    result: dict[int, float] = {}
    for t in range(1, max_t + 1):
        row = np.asarray(row @ transition).ravel()
        if t in wanted:
            # Detailed balance: P^(2t)_vv = deg(v) sum_x P^t_vx^2/deg(x).
            q = float(degree[source] * np.dot(row * row, inverse_degree))
            if not (0.0 < q <= 1.0 + 1e-10):
                raise ArithmeticError("invalid return probability")
            result[t] = q
    return result


def torus_even_return_fourier(d: int, L: int, half_time: int) -> float:
    """Independent finite-torus reference: average lambda_k^(2t)."""
    if d not in (1, 2) or not isinstance(L, int) or L < 3:
        raise ValueError("only d=1,2 and L>=3 are supported")
    if not isinstance(half_time, int) or half_time < 1:
        raise ValueError("positive integer half-time required")
    c = np.cos(2 * np.pi * np.arange(L, dtype=np.float64) / L)
    spectrum = c if d == 1 else (c[:, None] + c[None, :]) / 2.0
    return float(np.mean(np.power(spectrum, 2 * half_time)))


def infinite_lattice_even_return(d: int, half_time: int) -> float:
    """Combinatorial reference on Z or Z² at physical time 2t."""
    if d not in (1, 2) or not isinstance(half_time, int) or half_time < 1:
        raise ValueError("only d=1,2 and positive integer t are supported")
    t = half_time
    log_one_dim = math.lgamma(2 * t + 1) - 2 * math.lgamma(t + 1) - 2 * t * math.log(2)
    return math.exp(d * log_one_dim)


def complete_graph_even_return(n: int, half_time: int) -> float:
    """Independent closed form for non-bipartite K_n, n>=3."""
    if not isinstance(n, int) or n < 3 or not isinstance(half_time, int) or half_time < 1:
        raise ValueError("K_n requires n>=3 and positive integer t")
    return 1.0 / n + (n - 1.0) / n * (1.0 / (n - 1)) ** (2 * half_time)


def local_spectral_slope(q_t: float, q_2t: float) -> float:
    """-2 log(q(2t)/q(t))/log(2), where q(t) means return at 2t steps."""
    if not (math.isfinite(q_t) and math.isfinite(q_2t) and
            0.0 < q_t <= 1.0 + 1e-10 and 0.0 < q_2t <= 1.0 + 1e-10):
        raise ValueError("finite positive return probabilities <= 1 required")
    return -2.0 * (math.log(q_2t) - math.log(q_t)) / math.log(2)


def is_saturated(q_t: float, stationary_even_floor: float, *, tolerance: float = 0.01) -> bool:
    """True if within relative tolerance above the supplied even-time mixing floor.

    Caller must establish bipartiteness and the correct vertex-specific floor.
    Do not silently use 1/N for an irregular tree or bipartite graph.
    """
    if not (0.0 < stationary_even_floor <= 1 and math.isfinite(stationary_even_floor)):
        raise ValueError("invalid stationary floor")
    if not (0.0 <= tolerance < 1 and math.isfinite(tolerance)):
        raise ValueError("invalid tolerance")
    if not (0.0 <= q_t <= 1.0 + 1e-10 and math.isfinite(q_t)):
        raise ValueError("invalid return probability")
    return q_t <= (1.0 + tolerance) * stationary_even_floor


def has_powerlaw_headroom(q_t: float, stationary_even_floor: float, *, ratio: float = 10.0) -> bool:
    """Censor q(t) when it is too close to its vertex-specific even-time floor.

    This is a necessary finite-size guard, not a positive scaling verdict.
    Callers must establish period and stationary vertex weight independently.
    """
    if not (math.isfinite(stationary_even_floor) and 0 < stationary_even_floor <= 1):
        raise ValueError("invalid stationary even-time floor")
    if not (math.isfinite(q_t) and 0 <= q_t <= 1 + 1e-10):
        raise ValueError("invalid return probability")
    if not (math.isfinite(ratio) and ratio >= 1):
        raise ValueError("invalid headroom ratio")
    return q_t > ratio * stationary_even_floor


def s0_reference_payload() -> dict:
    """Reproducible small exact reference output; no random samples or wall clock."""
    import hashlib
    import json
    import platform
    import subprocess
    from pathlib import Path

    import scipy

    root = Path(__file__).resolve().parents[2]
    design = root / "docs" / "SPECTRAL_S0_PREREGISTRATION.md"
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    lattice = {}
    for d, L in ((1, 256), (2, 64)):
        lattice[f"d{d}_L{L}"] = {
            str(t): {
                "finite": torus_even_return_fourier(d, L, t),
                "infinite": infinite_lattice_even_return(d, t),
            }
            for t in (32, 64, 128, 256)
        }
    return {
        "manifest": {
            "commit": commit,
            "prereg_sha256": hashlib.sha256(design.read_bytes()).hexdigest(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "time_units": "half_steps_2t",
            "thresholds": {"lattice_relative": 0.01, "slope_absolute": 0.03,
                           "saturation_relative": 0.01, "max_transitions": MAX_TRANSITION_OPS},
        },
        "numerical": {
            "lattice": lattice,
            "torus_saturation": {
                f"d{d}_L{L}": {
                    str(t): torus_even_return_fourier(d, L, t)
                    for t in (4096, 8192)
                } for d, L in ((1, 32), (2, 16))
            },
            "complete_K32": {str(t): complete_graph_even_return(32, t)
                             for t in (4, 8)},
        },
    }


if __name__ == "__main__":
    import json

    print(json.dumps(s0_reference_payload(), sort_keys=True, separators=(",", ":")))
