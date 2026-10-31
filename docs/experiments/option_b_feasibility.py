"""Option-B (S1c) feasibility inputs from archived evidence only (no emergence_lab import, no seeds).

Usage:
    python -I option_b_feasibility.py <extracted s1b_run dir> <extracted se_audit_run dir>
Inputs: release assets s1b-run-v1 (sha256 0211d32d...e66f) and se-audit-run-v1 (sha256 63d8b42a...53de).

Prints (1) per-size work (edge_steps) and CPU per tree and throughput per host, (2) a projected
option-B cost at 192 trees per size for N = 2^16 and 2^18 on each observed host, (3) S1b per-size
pooled psi SD of the annealed W=128-1024 CAY slope, and (4) nominal TOST power for the +-0.03
same-family size contrast under normal theory. Everything here is descriptive planning input.
"""
import collections
import json
import math
import sys

import numpy as np
import pandas as pd
from scipy import stats

S1B, AUD = (p.rstrip("/") for p in sys.argv[1:3])
C = -2.0 / math.log(8.0)


def cost(path):
    man = json.load(open(path + "/run/manifest.json"))
    by = collections.defaultdict(lambda: [0.0, 0.0, set()])
    for line in open(path + "/run/sources.jsonl"):
        r = json.loads(line)
        k = (r["family"], int(r["size"]))
        by[k][0] += r["cpu_s"]
        by[k][1] += r["edge_steps"]
        by[k][2].add(r["i_rep"])
    out = {}
    for k, (cpu, steps, reps) in sorted(by.items()):
        n = len(reps)
        out[k] = dict(trees=n, cpu_per_tree=cpu / n, steps_per_tree=steps / n, throughput=steps / cpu)
    return man["cpu_s"], out


def host(path):
    for line in open(path + "/host_provenance.txt"):
        if "model name" in line:
            return line.split(":", 1)[1].strip()
    return "?"


cay = ("cayley_uniform_tree",)
res = {}
for name, p in (("S1b", S1B), ("SE-audit", AUD)):
    tot, c = cost(p)
    res[name] = c
    print("%s on %s: manifest cpu_s %.0f" % (name, host(p), tot))
    for k, v in c.items():
        print("   %-22s N=%-7d trees %3d  src-cpu/tree %5.1f s  edge_steps/tree %.3g  throughput %.3g steps/s"
              % (k[0], k[1], v["trees"], v["cpu_per_tree"], v["steps_per_tree"], v["throughput"]))

a = res["S1b"][(cay[0], 16384)]
b = res["SE-audit"][(cay[0], 16384)]
ratio = a["throughput"] / b["throughput"]
print("same-work check at N=2^14: steps/tree S1b %.4g vs audit %.4g (ratio %.4f); host speed ratio %.3f"
      % (a["steps_per_tree"], b["steps_per_tree"], b["steps_per_tree"] / a["steps_per_tree"], ratio))

n_b = 192
fast = sum(n_b * res["S1b"][(cay[0], N)]["cpu_per_tree"] for N in (65536, 262144)) / 60
slow = fast * ratio
print("option B, %d trees/size at 2^16 + 2^18, source CPU only: fast host (S1b) %.0f CPU-min; "
      "slow host (audit, scaled by the 2^14 throughput ratio) %.0f CPU-min" % (n_b, fast, slow))
for N in (65536, 262144):
    v = res["S1b"][(cay[0], N)]
    print("   N=%d: %.1f s/tree fast, %.1f s/tree slow (assumed)" % (N, v["cpu_per_tree"], v["cpu_per_tree"] * ratio))

df = pd.read_csv(S1B + "/run/numeric.csv")
df = df[df.family == cay[0]]
for N, g in df.groupby("size"):
    Q = g.groupby("i_rep")[["q_t128", "q_t1024"]].mean().values
    m = Q.mean(axis=0)
    psi = C * (Q[:, 1] / m[1] - Q[:, 0] / m[0])
    s, n = psi.std(ddof=1), len(psi)
    lo = s * math.sqrt((n - 1) / stats.chi2.ppf(0.95, n - 1))
    hi = s * math.sqrt((n - 1) / stats.chi2.ppf(0.05, n - 1))
    print("S1b CAY N=%-6d n=%d pooled psi SD %.4f, 90%% CI [%.4f, %.4f]" % (N, n, s, lo, hi))


def tost(n, sd, D=0.0, delta=0.03, alpha=0.05):
    se = math.sqrt(2.0) * sd / math.sqrt(n)
    z = stats.norm.ppf(1 - alpha)
    return max(0.0, stats.norm.cdf((delta - D) / se - z) - stats.norm.cdf((-delta - D) / se + z))


print("nominal TOST power, +-0.03, alpha 0.05 per side, equal n per size, normal theory:")
for sd in (0.07929, 0.08696, 0.0910, 0.0986):
    print("   sd %.5f: " % sd + "  ".join(
        "n=%d: D=0 %.2f, D=.01 %.2f, D=.02 %.2f" % (n, tost(n, sd), tost(n, sd, 0.01), tost(n, sd, 0.02))
        for n in (128, 192, 256)))
