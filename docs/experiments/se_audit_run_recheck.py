"""Independent recheck of the archived SE-audit v0.1 run (release se-audit-run-v1).

No emergence_lab import. Usage:
    python -I se_audit_run_recheck.py <path/to/extracted/se_audit_run>
where the directory is the `se_audit_run/` folder inside se_audit_run_evidence.tar.gz.

Checks the record-section-4 admissibility fields and the manifest output hashes, then
recomputes from numeric.csv alone (source-level q values): per-tree mean Q_i(128),
Q_i(1024) over 32 sources; per-batch annealed slope d_b and tree-level delta SE_b
(batch b = trees 12b..12b+11); R = sd_b(d_b) / sqrt(mean SE_b^2) and the frozen rule
R > 1.313 -> SE-REJECTED. Also prints the post-hoc (non-decision) lower-tail F probability.
"""
import collections
import csv
import hashlib
import json
import math
import sys

import numpy as np
from scipy import stats

D = sys.argv[1].rstrip("/")
RUN = D + "/run"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


man = json.load(open(RUN + "/manifest.json"))
rep = json.load(open(RUN + "/report.json"))
res = json.load(open(RUN + "/resource_evidence.json"))
for name, h in man["outputs"].items():
    assert sha(RUN + "/" + name) == h, name
print("manifest output hashes: OK")

seeds = man["seed_tuples_attempted"]
adm = {
    "exit_code_0": open(D + "/run_exit_code").read().strip() == "0",
    "clean_exit": res["clean_exit"] is True,
    "no_watchdog_failure": res["watchdog_failure"] is None,
    "no_resource_stop": not __import__("os").path.exists(RUN + "/resource_stop.json"),
    "mode_se_audit": man["mode"] == "se_audit" and rep["mode"] == "se_audit",
    "run_status_terminal": man["run_status"] in ("FINISHED", "BLOCKED"),
    "all_seeds_base_2036101901": len(seeds) == 192 and all(s[0] == 2036101901 for s in seeds),
    "seeds_attempted_eq_planned": seeds == man["seed_tuples_planned"],
    "s2_not_authorized": rep["s2_run_authorized"] is False,
    "controls_P0_passed": rep["controls_passed"] is True,
}
print("admissibility:", adm, "->", "ADMISSIBLE" if all(adm.values()) else "NOT ADMISSIBLE")
print("cpu_s", man["cpu_s"], "cgroup_cpu_s", res["cgroup_cpu_s"], "limit", res["cpu_limit_s"])

rows = list(csv.DictReader(open(RUN + "/numeric.csv")))
assert len(rows) == 192 * 32
assert all(r["status"] == "OK" for r in rows)
assert all(r["family"] == "cayley_uniform_tree" and r["size"] == "16384" for r in rows)
by = collections.defaultdict(list)
for r in rows:
    by[int(r["i_rep"])].append((float(r["q_t128"]), float(r["q_t1024"]), int(r["source"])))
assert sorted(by) == list(range(192))
assert all(len(v) == 32 and len({s for *_, s in v}) == 32 for v in by.values())
Q = np.array([[np.mean([a for a, _, _ in by[i]]), np.mean([b for _, b, _ in by[i]])] for i in range(192)])

c = -2.0 / math.log(8.0)
d, se, resid = [], [], []
for b in range(16):
    q = Q[12 * b:12 * b + 12]
    m = q.mean(axis=0)
    d.append(c * (math.log(m[1]) - math.log(m[0])))
    psi = c * (q[:, 1] / m[1] - q[:, 0] / m[0])
    se.append(psi.std(ddof=1) / math.sqrt(12))
    resid.append(psi - psi.mean())
d, se = np.array(d), np.array(se)
R = d.std(ddof=1) / math.sqrt(np.mean(se ** 2))
r = rep["result"]
print("R recomputed %.12f  report %.12f  |diff| %.1e" % (R, r["R"], abs(R - r["R"])))
print("max|d_b diff| %.1e  max|SE_b diff| %.1e" % (np.abs(d - r["d_b"]).max(), np.abs(se - r["se_b"]).max()))
print("exact sqrt F_0.95(15,176) = %.5f; frozen literal 1.313" % math.sqrt(stats.f.ppf(0.95, 15, 176)))
print("VERDICT (frozen rule):", "SE-REJECTED" if R > 1.313 else "SE-NOT-REJECTED", "| report:", r["verdict"])
F = R * R
print("R^2 = %.4f; P(F>=R^2) = %.4f; post-hoc lower tail P(F<=R^2) = %.4f (descriptive only)"
      % (F, stats.f.sf(F, 15, 176), stats.f.cdf(F, 15, 176)))
s_pool = math.sqrt(sum((x ** 2).sum() for x in resid) / 176)
lo, hi = math.sqrt(176 / stats.chi2.ppf(0.95, 176)), math.sqrt(176 / stats.chi2.ppf(0.05, 176))
print("pooled psi sd %.5f (176 df), 90%% CI [%.5f, %.5f]" % (s_pool, s_pool * lo, s_pool * hi))
print("all-tree annealed slope %.5f; mean d_b %.5f; sd d_b %.5f; RMS SE_b %.5f; CV(SE_b) %.3f"
      % (c * (math.log(Q[:, 1].mean()) - math.log(Q[:, 0].mean())), d.mean(), d.std(ddof=1),
         math.sqrt(np.mean(se ** 2)), se.std(ddof=1) / se.mean()))
