"""Pilot B stage 1: generator, oracle, analyst isolation, references, gates, beacon."""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from emergence_lab import pilot_b as pb
from emergence_lab import pilot_b_analyst as an
from emergence_lab import pilot_b_beacon as bc

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / pb.CONFIG_PATH).read_text())


def test_frozen_files_pinned():
    pins = pb.validate_frozen_files(ROOT)
    assert pins["prereg_blob_sha"].startswith("dd5dbefe")
    assert pins["config_sha256"].startswith("3fc24afa")


def test_z_values_and_detection_limit():
    from statistics import NormalDist
    nd = NormalDist()
    assert abs(nd.inv_cdf(1 - 0.05 / 24) - CFG["z_exterior"]) < 1e-4
    assert abs(nd.inv_cdf(1 - 0.05 / 66) - CFG["z_front"]) < 1e-4
    se = an.standard_error(CFG["sigma"], CFG["readouts_per_arm_per_cell"])
    assert abs(se - 2.0e-5) < 1e-12
    ext = [(t, r) for t in CFG["times"] for r in CFG["sites"] if r > CFG["v_max"] * t]
    assert len(ext) == CFG["exterior_tests"] == 12


def test_analyst_import_isolation_static():
    tree = ast.parse((ROOT / "src/emergence_lab/pilot_b_analyst.py").read_text())
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            mods.add(node.module or "")
    assert mods <= {"__future__", "math", "numpy"}, mods


def test_analyst_import_isolation_runtime():
    code = ("import sys; import emergence_lab.pilot_b_analyst; "
            "bad=[m for m in sys.modules if m.startswith('emergence_lab') and "
            "m not in ('emergence_lab','emergence_lab.pilot_b_analyst')]; print(bad); "
            "sys.exit(1 if bad else 0)")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr


def test_generator_counts_ranges_and_determinism():
    key = pb.dev_key(CFG)
    a, b = pb.instances(key, CFG), pb.instances(key, CFG)
    assert a == b
    assert [i["index"] for i in a] == list(range(40))
    counts = {}
    for inst in a:
        counts[inst["class"]] = counts.get(inst["class"], 0) + 1
    assert counts == CFG["class_counts"]
    other = pb.instances(hashlib.sha256(b"other").digest(), CFG)
    assert [i["class"] for i in other] != [i["class"] for i in a]


def test_keys():
    assert pb.dev_key(CFG) == hashlib.sha256(b"pilot-b-dev-2027101101").digest()
    rnd = "ab" * 32
    k = pb.blind_key(42, rnd)
    assert k == hashlib.sha256(b"pilot-b-v1|42|" + bytes.fromhex(rnd)).digest()
    with pytest.raises(ValueError):
        pb.blind_key(42, "ab" * 31)


@pytest.mark.parametrize("code", ["S1", "S2", "S3", "C1", "C2", "N1", "N2", "N3"])
def test_two_reference_paths_and_exact_exterior_zeros(code):
    insts = [i for i in pb.instances(pb.dev_key(CFG), CFG) if i["class"] == code]
    L, times = CFG["ring_L"], CFG["times"]
    for inst in insts:
        mp = pb.response_matrix_path(inst, L, times)
        sp = pb.response_spectral_path(inst, L, times)
        for t in times:
            assert np.max(np.abs(mp[t] - sp[t])) <= 1e-12
            if inst["group"] != "nonstrict":
                far = [r for r in range(L) if min(r, L - r) > CFG["v_max"] * t]
                assert np.all(mp[t][far] == 0.0)
            if inst["group"] == "nonstrict" and code in ("N1", "N2"):
                assert np.all(mp[t][[24, 32]] > 0.0)


def test_noise_free_oracle_returns_exact_response():
    inst = pb.instances(pb.dev_key(CFG), CFG)[0]
    mp = pb.response_matrix_path(inst, CFG["ring_L"], CFG["times"])
    truth = {(t, r): float(mp[t][r]) for t in CFG["times"] for r in CFG["sites"]}
    o = pb.Oracle(truth, 0, 1, CFG, sigma=0.0)
    for (t, r), s in truth.items():
        assert np.all(o.readouts(t, r, "do") == s)
        assert np.all(o.readouts(t, r, "control") == 0.0)


def test_oracle_budget_and_grid_enforced():
    o = pb.Oracle({(1, 0): 1.0}, 0, 1, CFG)
    o.readouts(1, 0, "do")
    with pytest.raises(RuntimeError):
        o.readouts(1, 0, "do")
    with pytest.raises(ValueError):
        o.readouts(1, 5, "do")
    with pytest.raises(ValueError):
        o.readouts(3, 0, "do")


def test_oracle_noise_streams_distinct_and_calibrated():
    truth = {(t, r): 0.0 for t in CFG["times"] for r in CFG["sites"]}
    o = pb.Oracle(truth, 7, 123, CFG)
    ys = [o.readouts(t, r, arm) for t in CFG["times"] for r in CFG["sites"] for arm in an.ARMS]
    flat = np.concatenate(ys) / CFG["sigma"]
    assert len({y.tobytes() for y in ys}) == len(ys)
    assert abs(flat.mean()) < 0.1 and abs(flat.std() - 1) < 0.05


class _FakeOracle:
    def __init__(self, means):
        self.means = means

    def readouts(self, t, r, arm):
        return np.full(50, self.means.get((t, r), 0.0) if arm == "do" else 0.0)


def test_analyst_verdicts_on_noise_free_inputs():
    d = pb.design_from_config(CFG)
    assert an.analyse(_FakeOracle({}), d)["verdict"] == "NO_RESPONSE"
    res = an.analyse(_FakeOracle({(1, 0): 1.0, (1, 4): 1e-3}), d)
    assert res["verdict"] == "CONSISTENT_WITH_H0" and res["r_hat"]["1"] == 4
    # exterior cell (t=1, r=6) just above / below the Bonferroni limit z1*SE = 5.7306e-5
    assert an.analyse(_FakeOracle({(1, 6): 5.8e-5}), d)["verdict"] == "H0_REJECTED"
    assert an.analyse(_FakeOracle({(1, 6): 5.6e-5}), d)["verdict"] == "NO_RESPONSE"
    # r=6 is interior at t=2 (6 <= 8): a detection there must not reject H0
    assert an.analyse(_FakeOracle({(2, 6): 1.0}), d)["verdict"] == "CONSISTENT_WITH_H0"


def test_dev_run_gates_and_byte_identical(tmp_path):
    a = pb.run("dev", tmp_path / "a", root=ROOT)
    b = pb.run("dev", tmp_path / "b", root=ROOT)
    for name in ("rows.csv", "result.json"):
        assert (tmp_path / "a" / name).read_bytes() == (tmp_path / "b" / name).read_bytes()
    assert a["manifest"]["outputs"] == b["manifest"]["outputs"]
    gates = a["gates"]
    assert gates["B_G0"]["pass"] and gates["B_G0"]["max_abs_diff"] <= 1e-12
    for g in ("B_G1", "B_G2", "B_G3", "B_G4", "B_G5"):
        assert gates[g]["pass"], (g, gates[g])
    rows = (tmp_path / "a" / "rows.csv").read_text().splitlines()
    assert len(rows) == 1 + 40 * 33


def test_blind_phase_refuses_unverified_beacon(tmp_path):
    with pytest.raises(RuntimeError):
        pb.run("blind", tmp_path, beacon={"round": 5, "randomness": "00" * 32,
                                          "signature_verified": False}, root=ROOT)


def test_beacon_round_arithmetic():
    g, p = bc.QUICKNET["genesis_time"], bc.QUICKNET["period"]
    assert bc.round_time(1) == g and bc.round_time(2) == g + p
    assert bc.first_round_at_or_after(g) == 1
    assert bc.first_round_at_or_after(g + 1) == 2
    assert bc.first_round_at_or_after(g + p) == 2
    assert bc.first_round_at_or_after(g + p + 1) == 3
    rec = bc.blind_round_for_merge("2026-10-10T20:00:00Z")
    assert rec["round_unix"] >= rec["target_unix"] > rec["round_unix"] - p
    assert rec["round_utc"].startswith("2026-10-11T20:00")
    with pytest.raises(ValueError):
        bc.blind_round_for_merge("2026-10-10T20:00:00")


def test_beacon_bls_verification_selftest():
    pytest.importorskip("py_ecc")
    from py_ecc.bls.hash_to_curve import hash_to_G1
    from py_ecc.bls.point_compression import compress_G1, compress_G2
    from py_ecc.optimized_bls12_381 import G2, multiply

    sk = 0x1234567890ABCDEF1234567890ABCDEF
    pk = multiply(G2, sk)
    z1, z2 = compress_G2(pk)
    pkb = z1.to_bytes(48, "big") + z2.to_bytes(48, "big")
    R = 777
    sig = compress_G1(multiply(hash_to_G1(bc.round_message(R), bc.DST_G1, hashlib.sha256), sk))
    sig = sig.to_bytes(48, "big")
    rec = {"round": R, "signature": sig.hex(), "randomness": hashlib.sha256(sig).hexdigest()}
    assert bc.verify_round(rec, pkb.hex())["signature_verified"]
    assert not bc.verify_round(dict(rec, round=R + 1), pkb.hex())["signature_verified"]
    bad = dict(rec, randomness="00" * 32)
    assert not bc.verify_round(bad, pkb.hex())["signature_verified"]
