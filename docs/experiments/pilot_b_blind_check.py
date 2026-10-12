"""Director check of the Pilot B stage-2 blind run (release pilot-b-blind-v1, run 38181108016).

Usage: python docs/experiments/pilot_b_blind_check.py docs/experiments/2026-10-11-pilot-b-blind
Checks: release-file SHA-256 vs blind_archive_manifest; blind key recomputed from the beacon per
prereg §6.3; decision digest vs result.json; calibration of z on all grid cells whose analytic
response is exactly 0 (Gaussian detector model); per-gate numbers from rows.csv.
Reproducing the decisions themselves needs the frozen code: run
`python -m emergence_lab.pilot_b --phase dev --output DEV` and
`python -m emergence_lab.pilot_b_blind execute --beacon D/beacon_R.json --dev-output DEV --output OUT`
and compare blind_decisions_sha256.
"""
import csv, hashlib, json, sys
import numpy as np
from scipy import stats

D = sys.argv[1]
m = json.load(open(f"{D}/blind_archive_manifest.json"))
for n, e in m["files_sha256"].items():
    print(n, "sha ok:", hashlib.sha256(open(f"{D}/{n}", "rb").read()).hexdigest() == e)
b = json.load(open(f"{D}/beacon_R.json"))
key = hashlib.sha256(b"pilot-b-v1|" + str(b["round"]).encode() + b"|" + bytes.fromhex(b["randomness"])).hexdigest()
r = json.load(open(f"{D}/result.json"))
print("key recomputed == manifest == result:", key == m["key_hex"] == r["key_hex"])
print("decisions digest matches:", r["decisions_sha256"] == m["blind_decisions_sha256"])
rows = list(csv.DictReader(open(f"{D}/rows.csv")))
z0 = np.array([float(x["z"]) for x in rows if float(x["S_true"]) == 0.0])
lam = len(z0) * 2 * stats.norm.sf(3.1718)
print(f"zero-signal cells {len(z0)}: mean z {z0.mean():.3f}, sd {z0.std(ddof=1):.3f}, KS p {stats.kstest(z0, 'norm').pvalue:.3f}; "
      f"|z|>z2 {int((abs(z0) > 3.1718).sum())} (expected {lam:.2f}), max |z| {abs(z0).max():.2f}")
P = {"S1", "S2", "S3", "C1", "C2"}
inst = {}
for x in rows:
    inst.setdefault(int(x["instance"]), (x["class"], x["verdict"]))
cls = {}
for i, (c, v) in sorted(inst.items()):
    cls.setdefault(c, []).append((i, v))
for c in sorted(cls):
    print(c, "H0_REJECTED", sum(v == "H0_REJECTED" for _, v in cls[c]), "of", len(cls[c]))
print("B-G1 false rejections (P):", [i for i, (c, v) in inst.items() if c in P and v == "H0_REJECTED"])
for g, v in sorted(r["summary"]["gates"].items()):
    print(g, "PASS" if v["pass"] else "FAIL")
