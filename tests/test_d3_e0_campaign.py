"""D3-E0/M0 v1 freeze: config, n_c rule, blinding, authorization refusal.

No D=3 target-cell mean is computed here: the end-to-end target test is
restricted to the two cells whose values are already known exactly from the
quadrature (arm B N=3, arm A N=5)."""

import copy
import hashlib
import json
import math

import numpy as np
import pytest

from emergence_lab import d3_e0 as m
from emergence_lab import d3_e0_campaign as c

CFG = c.load_config()


def test_seed_roots_derivation_and_distinct():
    roots = CFG["seed_roots"]
    for name in ("pilot", "gates", "target"):
        digest = hashlib.sha256(f"emergence-lab/d3-e0-v1/{name}".encode()).digest()
        assert roots[name] == int.from_bytes(digest[:8], "big")
    assert len({roots["pilot"], roots["gates"], roots["target"]}) == 3
    assert roots["pilot"] + 1 not in (roots["gates"], roots["target"])


def test_family_and_threshold():
    cells = c.stochastic_cells(CFG)
    assert len(cells) == CFG["decision"]["family"] == 17
    assert {tuple(x) for x in CFG["deterministic_cells"]} == set(m.DETERMINISTIC_CELLS)
    assert m.bonferroni_z(CFG["decision"]["alpha"], len(cells)) == pytest.approx(3.4370, abs=1e-4)


def test_protocol_mentions_frozen_constants():
    text = c.PROTOCOL.read_text()
    for token in ("3.4370", "600 CPU s", "512 MiB", "10^5", "0.01",
                  str(CFG["seed_roots"]["target"])):
        assert token in text


def test_welford_matches_numpy():
    x = np.random.default_rng(1).normal(2.0, 0.3, 10007)
    acc = m.Welford()
    for part in np.array_split(x, 13):
        acc.add_batch(part)
    assert acc.n == x.size
    assert acc.mean == pytest.approx(x.mean(), rel=1e-14)
    assert acc.var == pytest.approx(x.var(ddof=1), rel=1e-12)


def test_run_cell_exact_positive_count_and_deterministic():
    a = c.run_cell("B", 3, 3, 777, c.cell_rng(5, "B", 3, 3), 256)
    b = c.run_cell("B", 3, 3, 777, c.cell_rng(5, "B", 3, 3), 256)
    assert a["positives"] == 777 and a["drawn"] > 777
    assert a["mean_d"] == b["mean_d"] and a["drawn"] == b["drawn"]
    arm_a = c.run_cell("A", 6, 2, 300, c.cell_rng(5, "A", 2, 6), 128, keep_raw=True)
    assert arm_a["drawn"] == 300 and arm_a["raw"].min() >= 9


def test_d_of_mean_r_matches_design_values():
    assert c.arm_a_d_of_mean_r(8, 3) == pytest.approx(1.784, abs=1e-3)
    assert c.arm_a_d_of_mean_r(32, 3) == pytest.approx(2.565, abs=1e-3)
    assert c.arm_a_d_of_mean_r(3, 3) == 1.0
    # arm B with P(R>0)=1 gives d(f(3)) = 3.
    assert c.arm_b_d_of_mean_r(1.0, 3) == pytest.approx(3.0, abs=1e-10)


def _pilot_cells(sd, cpu):
    return {f"{a}|{n}": {"sd_d": sd, "cpu_per_positive_D3": cpu, "cpu_per_positive_D2": cpu}
            for a, n in c.stochastic_cells(CFG)}


def test_n_c_rule():
    s = c.target_sizes(CFG, _pilot_cells(0.8, 1e-6), 10.0)
    assert s["status"] == "OK"
    assert all(v == math.ceil((4 * 0.8 / 0.01) ** 2) for v in s["n_c"].values())
    s = c.target_sizes(CFG, _pilot_cells(0.2, 1e-6), 10.0)
    assert all(v == 100000 for v in s["n_c"].values())  # floor
    s = c.target_sizes(CFG, _pilot_cells(3.0, 1e-4), 10.0)
    assert s["status"] == "CAP_BINDS" and s["projected_cpu_s"] <= 600
    assert all(v >= 100000 for v in s["n_c"].values())
    s = c.target_sizes(CFG, _pilot_cells(0.5, 1e-3), 10.0)
    assert s["status"] == "BUDGET_INFEASIBLE"


def test_outcome_rules():
    assert c.outcome(False, True, ["BELOW"]) == "INVALID"
    assert c.outcome(True, False, ["BELOW"]) == "INVALID"
    assert c.outcome(True, True, ["BELOW", "UNRESOLVED"]) == "UNDECIDABLE_AT_BUDGET"
    assert c.outcome(True, True, ["BELOW", "ABOVE"]) == "COMPLETE"


def test_reference_extra_pin_enforced():
    bad = copy.deepcopy(CFG)
    bad["required_versions"] = {"mpmath": "0.0.1"}
    with pytest.raises(RuntimeError):
        c.require_reference_extra(bad)
    assert c.require_reference_extra(CFG)["mpmath"] == "1.3.0"


def test_cpu_cap_restores_limit():
    import resource
    before = resource.getrlimit(resource.RLIMIT_CPU)
    with c.cpu_cap(1000):
        assert resource.getrlimit(resource.RLIMIT_CPU)[0] != before[0] or before[0] != resource.RLIM_INFINITY
    assert resource.getrlimit(resource.RLIMIT_CPU) == before


def _small_cfg(tmp_path, **pilot):
    cfg = copy.deepcopy(CFG)
    cfg["seed_roots"] = {"pilot": 11, "gates": 12, "target": 13}
    cfg["pilot"].update(pilot)
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps(cfg))
    return p


def test_pilot_is_blinded(tmp_path, monkeypatch):
    # Engineering seeds, tiny sizes; restricted to cells already known exactly.
    monkeypatch.setattr(c, "stochastic_cells", lambda cfg: [("B", 3), ("A", 5)])
    man = c.run_pilot(tmp_path / "out", _small_cfg(tmp_path, positives_per_cell=200))
    assert man["status"] == "PILOT_COMPLETE"
    text = (tmp_path / "out" / "pilot_record.json").read_text()
    assert "mean_d" not in text and "mean" not in json.loads(text)["cells"]["B|3"]
    assert set(json.loads(text)["cells"]["B|3"]) == {
        "sd_d", "p_r0_D3", "cpu_per_positive_D3", "cpu_per_positive_D2"}
    with pytest.raises(FileExistsError):
        c.run_pilot(tmp_path / "out", _small_cfg(tmp_path, positives_per_cell=200))


def test_target_refuses_without_valid_authorization(tmp_path):
    auth = {"protocol": "D3-E0/M0 v1", "mode": "target", "expires_utc": "2000-01-01T00:00:00Z"}
    p = tmp_path / "auth.json"
    p.write_text(json.dumps(auth))
    with pytest.raises(PermissionError, match="expired"):
        c.run_target(tmp_path / "out", p)
    auth.update(expires_utc="2999-01-01T00:00:00Z", config_sha256="0" * 64)
    p.write_text(json.dumps(auth))
    with pytest.raises(PermissionError, match="config hash"):
        c.run_target(tmp_path / "out", p)
    assert not (tmp_path / "out").exists()


def test_target_pipeline_on_exactly_known_cells(tmp_path, monkeypatch):
    """End-to-end engineering check (not a result): only B3/A5, whose D=3 values
    are fixed by the quadrature, with engineering seeds and n_c=4000."""
    cfg_path = _small_cfg(tmp_path)
    cells = [("B", 3), ("A", 5)]
    monkeypatch.setattr(c, "stochastic_cells", lambda cfg: cells)
    fake = {"auth": {"authorization_id": "test"},
            "pilot": {"target_sizes": {"n_c": {"B|3": 4000, "A|5": 4000}}}}
    monkeypatch.setattr(c, "check_authorization", lambda a, b: fake)
    monkeypatch.setattr(c, "classify_cells",
                        lambda d3, cfg: {"z": 3.0, "cells": [dict(x, delta=x["mean_d"] - 3,
                                         z_bonf=3.0, label=m.classify(x["mean_d"] - 3, x["se_d"], 3.0))
                                         for x in d3]})
    man = c.run_target(tmp_path / "out", tmp_path / "unused.json", cfg_path)
    assert man["gates"]["quadrature"]["passed"] and man["gates"]["sampler"]["passed"]
    assert man["gates"]["d2_positive_control"]["passed"]
    assert man["gates"]["d3_mc_vs_quadrature"]["passed"]
    assert man["status"] == "COMPLETE"
    assert all(x["label"] == "BELOW" for x in man["cells"])  # both exact values < 3
    raw = np.load(tmp_path / "out" / "raw_counts.npz")
    assert set(raw.files) == {"D3_B_3", "D2_B_3", "D3_A_5", "D2_A_5"}
    assert (tmp_path / "out" / "cells.csv").exists()


def test_target_negative_control_offset_bug_is_invalid(tmp_path, monkeypatch):
    """Injected arm-A offset bug (2N-4 instead of 2N-3) must make the run INVALID."""
    cfg_path = _small_cfg(tmp_path)
    monkeypatch.setattr(c, "stochastic_cells", lambda cfg: [("A", 5)])
    fake = {"auth": {"authorization_id": "neg"},
            "pilot": {"target_sizes": {"n_c": {"A|5": 4000}}}}
    monkeypatch.setattr(c, "check_authorization", lambda a, b: fake)
    real = m.arm_counts

    def buggy(arm, n, d, batch, rng):
        r = real(arm, n, d, batch, rng)
        return r - 1 if arm == "A" else r
    monkeypatch.setattr(m, "arm_counts", buggy)
    man = c.run_target(tmp_path / "out", tmp_path / "unused.json", cfg_path)
    assert not man["gates"]["d2_positive_control"]["passed"]
    assert not man["gates"]["d3_mc_vs_quadrature"]["passed"]
    assert man["status"] == "INVALID"


def test_steady_cpu_per_positive_corrects_chunk_tail():
    """Review r1: pilot timing must not count the discarded chunk tail."""
    res = c.run_cell("A", 5, 3, 100, c.cell_rng(5, "A", 3, 5), 4096)
    assert res["computed"] == 4096 and res["drawn"] == 100
    assert c.steady_cpu_per_positive(res) == pytest.approx(res["cpu_s"] / 4096)
    res = c.run_cell("B", 3, 3, 500, c.cell_rng(5, "B", 3, 3), 256)
    assert res["computed"] >= res["drawn"] > res["positives"]
    assert c.steady_cpu_per_positive(res) == pytest.approx(
        res["cpu_s"] / res["computed"] / (res["positives"] / res["drawn"]))


def test_authorization_refuses_uncommitted_ignored_files():
    """Review r1 adversarial case: a well-formed authorization and a fabricated
    pilot record under the gitignored results/ directory must be refused."""
    import subprocess
    d = c.REPO / "results" / "_review_r1_adversarial"
    d.mkdir(parents=True, exist_ok=False)
    try:
        pilot = d / "pilot_record.json"
        pilot.write_text(json.dumps({"status": "PILOT_COMPLETE",
                                     "target_sizes": {"status": "OK", "n_c": {}}}))
        blobs = {p: subprocess.run(["git", "-C", str(c.REPO), "rev-parse", f"HEAD:{p}"],
                                   capture_output=True, text=True, check=True).stdout.strip()
                 for p in c.PINNED_PATHS}
        if subprocess.run(["git", "-C", str(c.REPO), "status", "--porcelain", "--", *c.PINNED_PATHS],
                          capture_output=True, text=True).stdout.strip():
            pytest.skip("pinned paths dirty in this checkout")
        auth = {"protocol": "D3-E0/M0 v1", "mode": "target", "authorization_id": "adv",
                "expires_utc": "2999-01-01T00:00:00Z",
                "config_sha256": c.sha256_file(c.CONFIG), "protocol_sha256": c.sha256_file(c.PROTOCOL),
                "blobs": blobs, "pilot_record": str(pilot.relative_to(c.REPO)),
                "pilot_record_sha256": c.sha256_file(pilot)}
        ap = d / "auth.json"
        ap.write_text(json.dumps(auth))
        with pytest.raises(PermissionError, match="authorization file is not committed"):
            c.check_authorization(ap, c.CONFIG)
    finally:
        for f in d.iterdir():
            f.unlink()
        d.rmdir()
