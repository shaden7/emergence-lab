"""Pilot B stage 2: fail-closed guards around the once-only blind run (no blind key is used here)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from emergence_lab import pilot_b as pb
from emergence_lab import pilot_b_beacon as bc
from emergence_lab import pilot_b_blind as bb

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/pilot-b-blind-run.yml"


def test_round_pin_recomputed_from_merge_time():
    rec = bb.check_round_pin()
    assert rec["round"] == bb.BLIND_ROUND == 32983212
    assert rec["round_utc"] == "2026-10-11T21:10:00+00:00"
    assert bc.round_time(bb.BLIND_ROUND) == bb.BLIND_ROUND_UNIX
    # R is the *first* round at/after merge + 24 h.
    assert bc.round_time(bb.BLIND_ROUND - 1) < rec["target_unix"] <= bb.BLIND_ROUND_UNIX


def test_frozen_stage1_code_unchanged():
    observed = bb.check_frozen_code(ROOT)
    assert observed == bb.FROZEN_BLOBS
    assert bb.FROZEN_BLOBS["docs/PILOT_B_BLINDED_INTERVENTION_PREREGISTRATION.md"] == pb.PREREG_BLOB_SHA


def test_frozen_code_guard_detects_change(tmp_path):
    for p in bb.FROZEN_BLOBS:
        (tmp_path / p).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / p).write_bytes((ROOT / p).read_bytes())
    bb.check_frozen_code(tmp_path)
    f = tmp_path / "src/emergence_lab/pilot_b_analyst.py"
    f.write_bytes(f.read_bytes() + b"\n")
    with pytest.raises(bb.GuardError, match="pilot_b_analyst"):
        bb.check_frozen_code(tmp_path)


def test_time_guard():
    with pytest.raises(bb.GuardError, match="too early"):
        bb.check_time(bb.BLIND_ROUND_UNIX)
    with pytest.raises(bb.GuardError):
        bb.check_time(bb.BLIND_ROUND_UNIX + bb.SAFETY_MARGIN_SECONDS - 1)
    assert bb.check_time(bb.BLIND_ROUND_UNIX + bb.SAFETY_MARGIN_SECONDS) > 0


def test_dev_digest_guard(tmp_path):
    pb.run("dev", tmp_path / "dev", root=ROOT)
    assert bb.check_dev_result(tmp_path / "dev") == bb.DEV_DECISIONS_SHA256
    m = json.loads((tmp_path / "dev" / "manifest.json").read_text())
    m["decisions_sha256"] = "0" * 64
    (tmp_path / "dev" / "manifest.json").write_text(json.dumps(m))
    with pytest.raises(bb.GuardError):
        bb.check_dev_result(tmp_path / "dev")


def _test_signer(monkeypatch):
    """Self-signed records with a throwaway key; the real quicknet key is never mocked in CI runs."""
    pytest.importorskip("py_ecc")
    from py_ecc.bls.hash_to_curve import hash_to_G1
    from py_ecc.bls.point_compression import compress_G1, compress_G2
    from py_ecc.optimized_bls12_381 import G2, multiply

    sk = 0x5EED5EED5EED5EED5EED
    z1, z2 = compress_G2(multiply(G2, sk))
    pk_hex = (z1.to_bytes(48, "big") + z2.to_bytes(48, "big")).hex()
    real = bc.verify_round
    monkeypatch.setattr(bb.bc, "verify_round", lambda rec, public_key_hex=pk_hex: real(rec, pk_hex))

    def sign(r):
        sig = compress_G1(multiply(hash_to_G1(bc.round_message(r), bc.DST_G1, hashlib.sha256), sk))
        sig = sig.to_bytes(48, "big")
        return {"round": r, "signature": sig.hex(), "randomness": hashlib.sha256(sig).hexdigest(),
                "signature_verified": True, "chain_hash": bc.QUICKNET["hash"]}
    return sign


def test_beacon_guard(monkeypatch):
    sign = _test_signer(monkeypatch)
    good = sign(bb.BLIND_ROUND)
    assert bb.check_beacon(good)["signature_verified"]
    with pytest.raises(bb.GuardError, match="pinned R"):
        bb.check_beacon(sign(bb.BLIND_ROUND + 1))
    with pytest.raises(bb.GuardError, match="quicknet"):
        bb.check_beacon(dict(good, chain_hash="00" * 32))
    with pytest.raises(bb.GuardError, match="re-verification"):
        bb.check_beacon(dict(good, randomness="11" * 32))  # stored flag alone is not trusted


def test_real_quicknet_key_rejects_self_signed_record():
    pytest.importorskip("py_ecc")
    rec = {"round": bb.BLIND_ROUND, "signature": "a" * 96, "randomness": "00" * 32,
           "signature_verified": True, "chain_hash": bc.QUICKNET["hash"]}
    with pytest.raises(Exception):
        bb.check_beacon(rec)


def test_execute_end_to_end_with_test_key(monkeypatch, tmp_path):
    """Exercises the full blind path with a *test* beacon; the result is not Pilot B evidence."""
    sign = _test_signer(monkeypatch)
    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(bb.time, "time", lambda: bb.BLIND_ROUND_UNIX + 3600.0)
    pb.run("dev", tmp_path / "dev", root=ROOT)
    beacon = tmp_path / "beacon.json"
    beacon.write_text(json.dumps(sign(bb.BLIND_ROUND)))
    rec = bb.execute(beacon, tmp_path / "dev", tmp_path / "blind")
    assert rec["key_hex"] == pb.blind_key(bb.BLIND_ROUND, json.loads(beacon.read_text())["randomness"]).hex()
    assert set(rec["files_sha256"]) == {"rows.csv", "result.json", "manifest.json"}
    assert set(rec["gates"]) == {f"B_G{i}" for i in range(6)}
    stored = json.loads((tmp_path / "blind" / "blind_archive_manifest.json").read_text())
    assert stored["blind_decisions_sha256"] == rec["blind_decisions_sha256"] != bb.DEV_DECISIONS_SHA256
    for name, digest in rec["files_sha256"].items():
        assert hashlib.sha256((tmp_path / "blind" / name).read_bytes()).hexdigest() == digest


def test_workflow_is_dispatch_only_on_main_and_once_only():
    text = WORKFLOW.read_text()
    on_block = text.split("\non:", 1)[1].split("\npermissions:", 1)[0]
    assert "workflow_dispatch" in on_block
    for trigger in ("push", "pull_request", "schedule"):
        assert trigger not in on_block, trigger
    assert "github.ref == 'refs/heads/main'" in text
    assert bb.RELEASE_TAG in text and "already exists" in text
    assert str(bb.BLIND_ROUND) in text
    # The preflight (time + frozen code) precedes any beacon fetch.
    assert text.index("pilot_b_blind preflight") < text.index("fetch-round")
