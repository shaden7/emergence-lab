"""Archive gate verification must detect tampering, missing controls and missing arrays."""
import hashlib
import io
import json

import numpy as np
import pytest

from pathlib import Path

from emergence_lab.archive_evidence import EXPECTED, canonical_config_sha256, digest, verify_gate


def fixture_gate(tmp_path, kind="coverage"):
    cfg = ({"sizes": [4], "warmup_sweeps": 4, "sample_sweeps": 8,
            "sample_every": 2, "batches": 2, "chains_per_batch": 3} if kind == "coverage"
           else {"sizes": [4], "chains_per_start": 2,
                 "controls": {"off_critical": {"chains_per_start": 2},
                              "j0_iid": {"chains": 2}}})
    arrays = {}
    if kind == "coverage":
        for name in ("energy_sum_L4", "magnetization_sum_L4"):
            arrays[name] = np.arange(36, dtype=np.int16).reshape(2, 3, 6)
        extras = {"sizes": {"4": {"main": {"pass": True},
                                   "power_control": {"pass": False}}},
                  "raw_digests": {k: digest(np.ascontiguousarray(a).tobytes())
                                  for k, a in arrays.items()}}
    else:
        for part, n in (("main", 4), ("off_critical", 4), ("j0_iid", 2)):
            stem = f"{part}_L4_"
            arrays[stem + "energy_sum"] = np.zeros((n, 4), dtype=np.int16)
            arrays[stem + "magnetization_sum"] = np.ones((n, 4), dtype=np.int16)
            arrays[stem + "seeds"] = np.arange(1, n + 1, dtype=np.int64)
            arrays[stem + "starts"] = np.array(["random"] * n)
        extras = {"main": {"checks": {f"C{i}": True for i in range(65)}},
                  "controls": {"off_critical": {"rejected": True}, "j0_iid": {"rejected": True}}}
    buf = io.BytesIO()
    np.savez_compressed(buf, **arrays)
    raw_bytes = buf.getvalue()
    raw = tmp_path / "input.npz"
    raw.write_bytes(raw_bytes)
    config = tmp_path / "config.json"
    # Like the real configs: file bytes (indented, unsorted) differ from canonical JSON.
    config.write_text(json.dumps(cfg, indent=2) + "\n")
    cfg_hash = digest(json.dumps(cfg, sort_keys=True).encode())
    cfg_file_hash = digest(config.read_bytes())
    assert cfg_file_hash != cfg_hash
    report = {"gate_pass": True, "config": cfg, "config_sha256": cfg_hash,
              "raw_npz_sha256": digest(raw_bytes), **extras}
    report_file = tmp_path / "report.json"
    report_file.write_text(json.dumps(report))
    return raw, report_file, config, {"raw": digest(raw_bytes), "config": cfg_file_hash}


@pytest.mark.parametrize("kind", ["coverage", "finite_size"])
def test_valid_archive_and_manifest(tmp_path, kind):
    raw, rep, cfg, pins = fixture_gate(tmp_path, kind)
    entry = verify_gate(kind, raw, rep, cfg, expected=pins)
    assert entry["raw_npz_sha256"] == pins["raw"]
    assert len(entry["raw_array_sha256"]) == (2 if kind == "coverage" else 12)


@pytest.mark.parametrize("kind", ["coverage", "finite_size"])
def test_tampered_raw_rejected(tmp_path, kind):
    raw, rep, cfg, pins = fixture_gate(tmp_path, kind)
    raw.write_bytes(raw.read_bytes() + b"tampered")
    with pytest.raises(ValueError, match="raw bytes"):
        verify_gate(kind, raw, rep, cfg, expected=pins)


@pytest.mark.parametrize("kind", ["coverage", "finite_size"])
def test_negative_control_failure_rejected(tmp_path, kind):
    raw, rep, cfg, pins = fixture_gate(tmp_path, kind)
    report = json.loads(rep.read_text())
    if kind == "coverage":
        report["sizes"]["4"]["power_control"]["pass"] = True
    else:
        report["controls"]["j0_iid"]["rejected"] = False
    rep.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="control"):
        verify_gate(kind, raw, rep, cfg, expected=pins)


def test_wrong_config_rejected(tmp_path):
    raw, rep, cfg, pins = fixture_gate(tmp_path)
    report = json.loads(rep.read_text())
    report["config"]["temperature"] = 2.5
    rep.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="config"):
        verify_gate("coverage", raw, rep, cfg, expected=pins)


def test_report_array_digest_mismatch_rejected(tmp_path):
    raw, rep, cfg, pins = fixture_gate(tmp_path)
    report = json.loads(rep.read_text())
    report["raw_digests"]["energy_sum_L4"] = "0" * 64
    rep.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="arrays/digests"):
        verify_gate("coverage", raw, rep, cfg, expected=pins)


@pytest.mark.parametrize("kind,path", [("coverage", "configs/coverage_gate.json"),
                                       ("finite_size", "configs/finite_size_gate.json")])
def test_production_config_pins_match_repository_files(kind, path):
    """Regression (archive run 38045856455): pins are file-byte SHA-256, not canonical JSON."""
    data = (Path(__file__).resolve().parents[1] / path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == EXPECTED[kind]["config"]
    assert canonical_config_sha256(json.loads(data)) != EXPECTED[kind]["config"]


def test_reformatted_config_file_rejected(tmp_path):
    raw, rep, cfg, pins = fixture_gate(tmp_path)
    cfg.write_text(json.dumps(json.loads(cfg.read_text()), sort_keys=True))
    with pytest.raises(ValueError, match="config file differs"):
        verify_gate("coverage", raw, rep, cfg, expected=pins)


def test_wrong_reported_config_hash_rejected(tmp_path):
    raw, rep, cfg, pins = fixture_gate(tmp_path)
    report = json.loads(rep.read_text())
    report["config_sha256"] = digest(cfg.read_bytes())
    rep.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="reported config"):
        verify_gate("coverage", raw, rep, cfg, expected=pins)
