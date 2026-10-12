"""Later-pass review check of the Pilot B stage-2 blind result (PR #40).

Written by a session that did not produce the run or the result note
(rd-claude-20261012T0205Z-64ccb703e8eb); same model family, so this is an
AI-mediated later-pass review, not independent peer review.

Does NOT import emergence_lab. From the committed release copies it:
  1. checks file hashes, the blind key (prereg §6.3), randomness == SHA-256(signature),
     and drand quicknet round arithmetic (genesis 1692803367, period 3 s) against
     the stage-1 merge time + 24 h;
  2. recomputes z = D/SE, both Bonferroni thresholds, detections, verdicts and r_hat
     from the per-cell rows and re-derives B-G1..B-G3 and B-G5 counts;
  3. recomputes the analytic response S(r,t) for every instance from its logged
     parameters with its own propagators (direct circular convolution for S1/S3/C2/N2,
     leapfrog recursion for S2, Fourier heat kernel for N1, dense matrix power for N3),
     compares with the logged S_true, checks exterior zeros for all P instances, and
     re-derives the B-G4 detectable set.

Usage: python docs/experiments/pilot_b_review_independent.py docs/experiments/2026-10-11-pilot-b-blind <stage1-merge-unix>
"""
import csv
import hashlib
import json
import sys

import numpy as np
from scipy import stats

D = sys.argv[1]
MERGE_UNIX = int(sys.argv[2])
L, TS, RS = 256, (1, 2, 4), (0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32)
VMAX, ALPHA, N, SIGMA = 4, 0.05, 50, 1e-4
SE = SIGMA * np.sqrt(2 / N)
Z1 = stats.norm.ppf(1 - ALPHA / (2 * 12))
Z2 = stats.norm.ppf(1 - ALPHA / (2 * 33))
LIMIT = Z1 * SE
ok = True


def check(name, cond, extra=""):
    global ok
    ok &= bool(cond)
    print(f"[{'OK' if cond else 'FAIL'}] {name} {extra}")


# 1. provenance
m = json.load(open(f"{D}/blind_archive_manifest.json"))
for n, e in m["files_sha256"].items():
    check(f"sha256 {n}", hashlib.sha256(open(f"{D}/{n}", "rb").read()).hexdigest() == e)
b = json.load(open(f"{D}/beacon_R.json"))
check("randomness == SHA-256(signature)",
      hashlib.sha256(bytes.fromhex(b["signature"])).hexdigest() == b["randomness"])
key = hashlib.sha256(b"pilot-b-v1|" + str(b["round"]).encode() + b"|" + bytes.fromhex(b["randomness"])).hexdigest()
r = json.load(open(f"{D}/result.json"))
check("blind key recomputed", key == m["key_hex"] == r["key_hex"])
GEN, PER = 1692803367, 3
t_round = GEN + (b["round"] - 1) * PER
first = (MERGE_UNIX + 86400 - GEN + PER - 1) // PER + 1  # first round with time >= target
check("round is first >= merge+24h", b["round"] == first and t_round >= MERGE_UNIX + 86400 > t_round - PER,
      f"(round {b['round']}, t={t_round}, target {MERGE_UNIX + 86400})")
check("chain hash = quicknet", b["chain_hash"] == "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971")

# 2. decisions from rows
rows = list(csv.DictReader(open(f"{D}/rows.csv")))
check("1320 rows", len(rows) == 40 * 33)
cells = {}
for x in rows:
    i = int(x["instance"])
    z = float(x["D"]) / SE
    ext = int(x["r"]) > VMAX * int(x["t"])
    check_z = abs(z - float(x["z"])) < 1e-9 * max(1, abs(z))
    if not check_z:
        check(f"z instance {i}", False)
    cells.setdefault(i, []).append(dict(t=int(x["t"]), r=int(x["r"]), ext=ext, z=z,
                                        front=abs(z) > Z2, exter=ext and abs(z) > Z1,
                                        S=float(x["S_true"]), cls=x["class"], verdict=x["verdict"],
                                        flags=(int(x["detect_front"]), int(x["detect_exterior"]))))
flag_mismatch = sum((c["front"], c["exter"]) != c["flags"] for cs in cells.values() for c in cs)
check("detection flags reproduced", flag_mismatch == 0, f"({flag_mismatch} mismatches)")
inst = {i["index"]: i for i in r["summary"]["instances"]}
verd, rhat = {}, {}
for i, cs in cells.items():
    if any(c["exter"] for c in cs):
        v = "H0_REJECTED"
    elif any(c["front"] for c in cs):
        v = "CONSISTENT_WITH_H0"
    else:
        v = "NO_RESPONSE"
    verd[i] = v
    rhat[i] = {t: max([c["r"] for c in cs if c["t"] == t and c["front"]], default=None) for t in TS}
check("verdicts reproduced", all(verd[i] == cells[i][0]["verdict"] == inst[i]["verdict"] for i in cells))
check("r_hat reproduced", all({int(k): v for k, v in inst[i]["r_hat"].items()} == rhat[i] for i in cells))
cls = {i: cells[i][0]["cls"] for i in cells}
counts = {c: sum(v == c for v in cls.values()) for c in sorted(set(cls.values()))}
check("class counts per prereg §3", counts == dict(C1=4, C2=4, N1=5, N2=5, N3=6, S1=6, S2=4, S3=6), str(counts))
P = [i for i in cells if cls[i] in ("S1", "S2", "S3", "C1", "C2")]
K = [i for i in cells if cls[i] in ("S1", "S2", "S3")]
NS = [i for i in cells if cls[i] in ("N1", "N2", "N3")]
g1 = sorted(i for i in P if verd[i] == "H0_REJECTED")
check("B-G1 <= 3", len(g1) <= 3, f"false rejections {g1}")
kk = {i: inst[i]["params"]["k"] for i in K}
g2 = sorted(i for i in K if any(rhat[i][t] is not None and rhat[i][t] > kk[i] * t for t in TS))
check("B-G2 <= 3", len(g2) <= 3, f"speed overestimates {g2}")
c1 = [i for i in cells if cls[i] == "C1"]
check("B-G3a C1 detects r=0 at all t", all(all(c["front"] for c in cells[i] if c["r"] == 0) for i in c1))
spur = sorted(i for i in cells if cls[i] == "C2" and any(c["front"] or c["exter"] for c in cells[i])) + \
    sorted(i for i in c1 if any((c["r"] > 0 and c["front"]) or c["exter"] for c in cells[i]))
check("B-G3b spurious C <= 2", len(spur) <= 2, f"spurious {spur}")
check("B-G5 vocabulary", set(verd.values()) <= {"NO_RESPONSE", "CONSISTENT_WITH_H0", "H0_REJECTED"})
undetected = sorted(i for i in NS if verd[i] != "H0_REJECTED")
check("B-G5 undetected N list complete",
      undetected == sorted(u["index"] for u in r["summary"]["gates"]["B_G5"]["undetected_nonstrict"]), str(undetected))


# 3. analytic S, own propagators
def circ_step(x, w, k):
    """x_{t+1}(i) = sum_j w[j+k] x_t(i - j) (spread), orientation tested both ways below."""
    y = np.zeros_like(x)
    for j in range(-k, k + 1):
        y += w[j + k] * np.roll(x, j)
    return y


def S_of(i, flip=False):
    c, p = cls[i], inst[i]["params"]
    out = {}
    e0 = np.zeros(L); e0[0] = 1.0
    if c == "C2":
        return {t: np.zeros(L) for t in TS}
    if c == "C1":
        return {t: e0.copy() for t in TS}
    if c in ("S1", "S3", "N3"):
        k, w = p["k"], np.array(p["weights"])
        if flip:
            w = w[::-1]
        if c == "N3":
            A = np.zeros((L, L))
            for j in range(-k, k + 1):
                for a in range(L):
                    A[a, (a + j) % L] += w[j + k]
            d, eps = p["d"], p["epsilon"]
            A[0, d] += eps; A[d, 0] += eps; A[0, 0] -= eps; A[d, d] -= eps
            x = e0.copy()
            for t in range(1, 5):
                x = A @ x
                if t in TS:
                    out[t] = x.copy()
            return out
        x = e0.copy()
        for t in range(1, 5):
            x = circ_step(x, w, k)
            if t in TS:
                out[t] = x.copy()
        return out
    if c == "S2":
        c2 = p["c2"]
        prev, u = e0.copy(), e0.copy()
        for t in range(1, 5):
            lap = np.roll(u, 1) + np.roll(u, -1) - 2 * u
            prev, u = u, 2 * u - prev + c2 * lap
            if t in TS:
                out[t] = u.copy()
        return out
    if c == "N1":
        q = 2 * np.pi * np.arange(L) / L
        lam = -(2 - 2 * np.cos(q)) * p["gamma"]
        return {t: np.real(np.fft.ifft(np.exp(t * lam))) for t in TS}
    if c == "N2":
        j = np.arange(-127, 129)
        w = (1.0 + np.abs(j)) ** (-p["alpha"]); w /= w.sum()
        kern = np.zeros(L)
        for jj, ww in zip(j, w):
            kern[jj % L] += ww
        if flip:
            kern = np.roll(kern[::-1], 1)
        fk = np.fft.fft(kern)
        return {t: np.real(np.fft.ifft(fk ** t)) for t in TS}
    raise ValueError(c)


maxdiff, orient, ext_nonzero, detectable = 0.0, {}, [], []
for i in sorted(cells):
    best = None
    for flip in (False, True):
        S = S_of(i, flip)
        dmax = max(abs(S[c["t"]][c["r"]] - c["S"]) for c in cells[i])
        if best is None or dmax < best[0]:
            best = (dmax, flip, S)
    dmax, flip, S = best
    orient[i] = flip
    maxdiff = max(maxdiff, dmax)
    if i in P and any(S[c["t"]][c["r"]] != 0.0 for c in cells[i] if c["ext"]):
        ext_nonzero.append(i)
    if i in NS:
        mx = max(abs(S[c["t"]][c["r"]]) for c in cells[i] if c["ext"])
        if abs(mx - inst[i]["max_abs_exterior_S"]) > 1e-12:
            check(f"max exterior S instance {i}", False, f"{mx} vs {inst[i]['max_abs_exterior_S']}")
        if mx >= 2 * 5.73e-5:
            detectable.append(i)
check("analytic S reproduced (own propagators)", maxdiff < 1e-12, f"(max |dS| {maxdiff:.2e})")
check("exterior S exactly 0 for all P instances", not ext_nonzero, str(ext_nonzero))
flips = sorted(i for i, f in orient.items() if f and cls[i] in ("S1", "S3"))
print(f"   orientation: logged S1/S3 weights match spread x_(t+1)(i)=sum_j w_j x_t(i-j) "
      f"{'for all' if not flips else 'except ' + str(flips)}")
check("B-G4 detectable set", sorted(detectable) == r["summary"]["gates"]["B_G4"]["detectable"], str(sorted(detectable)))
check("B-G4 >= 90% rejected", len(detectable) >= 3 and
      sum(verd[i] == "H0_REJECTED" for i in detectable) >= 0.9 * len(detectable))
z0 = np.array([c["z"] for cs in cells.values() for c in cs if c["S"] == 0.0])
print(f"   zero-signal cells {len(z0)}: mean {z0.mean():.3f} sd {z0.std(ddof=1):.3f} "
      f"KS p {stats.kstest(z0, 'norm').pvalue:.3f}, |z|>z2: {(abs(z0) > Z2).sum()} "
      f"(exp {len(z0) * 2 * stats.norm.sf(Z2):.2f})")
print(f"   z1 {Z1:.4f}, z2 {Z2:.4f}, limit {LIMIT:.4e}")
print("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED")
sys.exit(0 if ok else 1)
