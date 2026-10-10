"""Independent-sampler cross-check of the L32 critical-mixing gate (later-pass review of PR #13).

Single-cluster Wolff algorithm (Wolff, PRL 62, 361, 1989) on the periodic L x L
Ising model. It shares no update code with the checkerboard Metropolis sampler
used in ``critical_gate``; agreement of the two samplers on E and |m| is a
cross-check of the gate's |m| estimate, for which no exact finite-L reference
exists. Uncertainty: Student-t interval over independently seeded chain means.

This is a numerical method check, not a physics result.
"""
import argparse
import hashlib
import json
import math
import platform
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from emergence_lab.exact_finite import exact_energy_per_spin  # noqa: E402
from emergence_lab.stats import independent_chain_interval  # noqa: E402


def wolff_chain(size: int, temperature: float, warmup: int, clusters: int, every: int, seed: int):
    """Return per-measurement energy and magnetization sums (int arrays)."""
    if size < 4 or warmup < 0 or clusters < 1 or every < 1 or temperature <= 0:
        raise ValueError("invalid chain parameters")
    rng = np.random.default_rng(seed)
    n = size * size
    spins = (2 * rng.integers(0, 2, size=n) - 1).tolist()
    nbrs = [((i // size) * size + (i + 1) % size, (i // size) * size + (i - 1) % size,
             (i + size) % n, (i - size) % n) for i in range(n)]
    p_add = 1.0 - math.exp(-2.0 / temperature)
    e_out, m_out, sizes = [], [], []
    for step in range(warmup + clusters):
        seed_site = int(rng.integers(n))
        s0 = spins[seed_site]
        spins[seed_site] = -s0
        stack = [seed_site]
        csize = 1
        draws = iter(rng.random(4 * n).tolist())  # at most 4 bond tests per cluster site
        while stack:
            i = stack.pop()
            for j in nbrs[i]:
                if spins[j] == s0 and next(draws) < p_add:
                    spins[j] = -s0
                    stack.append(j)
                    csize += 1
        if step >= warmup and (step - warmup + 1) % every == 0:
            a = np.asarray(spins, dtype=np.int64).reshape(size, size)
            e_out.append(-int(np.sum(a * (np.roll(a, 1, 0) + np.roll(a, 1, 1)))))
            m_out.append(int(a.sum()))
            sizes.append(csize)
    return np.array(e_out), np.array(m_out), np.array(sizes)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--size", type=int, default=32)
    p.add_argument("--temperature", type=float, default=2.269185)
    p.add_argument("--chains", type=int, default=8)
    p.add_argument("--warmup", type=int, default=1000)
    p.add_argument("--clusters", type=int, default=20000)
    p.add_argument("--every", type=int, default=2)
    p.add_argument("--base-seed", type=int, default=2029050001)
    p.add_argument("--gate-report", type=Path, help="critical_gate JSON report to compare against")
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    t0 = time.time()
    n = a.size * a.size
    per_chain, raw = [], []
    for c in range(a.chains):
        e, m, cs = wolff_chain(a.size, a.temperature, a.warmup, a.clusters, a.every, a.base_seed + c)
        raw.append(np.stack([e, m]))
        per_chain.append({"seed": a.base_seed + c, "E": float(e.mean() / n),
                          "abs_m": float(np.abs(m).mean() / n), "mean_cluster": float(cs.mean())})
    out = {"method": "single-cluster Wolff, independent of checkerboard Metropolis",
           "size": a.size, "temperature": a.temperature, "chains": a.chains,
           "warmup_clusters": a.warmup, "clusters": a.clusters, "every": a.every,
           "seeds": [r["seed"] for r in per_chain],
           "environment": {"python": platform.python_version(), "numpy": np.__version__},
           "per_chain": per_chain,
           "raw_sha256": hashlib.sha256(np.stack(raw).astype(np.int32).tobytes()).hexdigest()}
    exact = exact_energy_per_spin(a.temperature, a.size)["energy_per_spin"]
    for key in ("E", "abs_m"):
        mean, se, lo, hi = independent_chain_interval([r[key] for r in per_chain])
        out[key] = {"mean": mean, "stderr": se, "ci95": [lo, hi]}
    out["E"]["exact"] = exact
    out["E"]["z_vs_exact"] = (out["E"]["mean"] - exact) / out["E"]["stderr"]
    if a.gate_report:
        g = json.loads(a.gate_report.read_text())["main"]["observables"]
        for key, gk in (("E", "energy"), ("abs_m", "abs_magnetization")):
            gm, gs = g[gk]["pooled_mean"], g[gk]["pooled_stderr"]
            d = out[key]["mean"] - gm
            out[key]["gate_mean"], out[key]["gate_stderr"] = gm, gs
            out[key]["z_wolff_minus_gate"] = d / math.hypot(out[key]["stderr"], gs)
    out["environment"]["wall_seconds"] = time.time() - t0
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("E", "abs_m", "raw_sha256")}, indent=2))


if __name__ == "__main__":
    main()
