import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from emergence_lab import critical_gate as cg

CFG = json.loads((Path(__file__).parents[1] / "configs" / "l32_critical_gate.json").read_text())


def _small():
    cfg = copy.deepcopy(CFG)
    cfg.update(size=8, chains_per_start=4, warmup_sweeps=50, sample_sweeps=400,
               sample_every=4, power_control_sweeps=200, max_proposals=10_000_000)
    return cfg


def test_registered_config_is_frozen_and_within_budget():
    assert cg.validate_config(CFG) == 1_474_560_000
    seeds = [CFG["base_seed"] + si * 1000 + r for si in range(2) for r in range(16)]
    assert len(set(seeds)) == 32 and min(seeds) == 2028010001 and max(seeds) == 2028011016
    raw = (Path(__file__).parents[1] / "configs" / "l32_critical_gate.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "8ba2f38b62c5af3c0faf63a5cce59f35f62a57a354b03bc2278400ecb49c46c0"


def test_budget_and_schema_rejections():
    for change in ({"sample_sweeps": 400_000}, {"size": 7}, {"chains_per_start": 2},
                   {"power_control_sweeps": 40_000}, {"sample_every": 7}):
        cfg = copy.deepcopy(CFG)
        cfg.update(change)
        with pytest.raises(ValueError):
            cg.validate_config(cfg)
    cfg = copy.deepcopy(CFG)
    cfg["extra"] = 1
    with pytest.raises(ValueError):
        cg.validate_config(cfg)


def test_small_run_is_deterministic_and_complete():
    r1, raw1 = cg.run_gate(_small())
    r2, raw2 = cg.run_gate(_small(), workers=2)
    assert raw1 == raw2 and r1["raw_npz_sha256"] == r2["raw_npz_sha256"]
    assert r1["draws_per_chain"] == 100 and len(set(r1["seeds"])) == 8
    assert set(r1["main"]["checks"]) == {
        "G1_rhat_energy", "G2_ess_energy", "G3_chain_ess_energy", "G4_hot_cold_energy",
        "G5_exact_energy", "G6_chain_coverage", "G1_rhat_abs_magnetization",
        "G2_ess_abs_magnetization", "G3_chain_ess_abs_magnetization", "G4_hot_cold_abs_magnetization"}


def _synthetic(rng, ref, shift=0.0, phi=0.0, n=4000, m=32):
    x = np.empty((m, n))
    x[:, 0] = rng.normal(size=m)
    for t in range(1, n):
        x[:, t] = phi * x[:, t - 1] + np.sqrt(1 - phi * phi) * rng.normal(size=m)
    e = ref + 0.01 * x
    e[:16] += shift
    return e, np.abs(0.6 + 0.05 * rng.normal(size=(m, n)))


def test_evaluate_passes_well_mixed_synthetic_data():
    rng = np.random.default_rng(21)
    ref = -1.43
    e, a = _synthetic(rng, ref)
    out = cg.evaluate(e, a, ["random"] * 16 + ["ordered"] * 16, CFG, ref)
    assert out["gate_pass"], out["checks"]


def test_evaluate_fails_hot_cold_disagreement_and_bias():
    rng = np.random.default_rng(22)
    ref = -1.43
    starts = ["random"] * 16 + ["ordered"] * 16
    # A 0.2-sd offset of half the chains: R-hat ~1.005 misses it, the hot/cold test does not.
    e, a = _synthetic(rng, ref, shift=0.002)
    out = cg.evaluate(e, a, starts, CFG, ref)
    assert out["checks"]["G1_rhat_energy"]
    assert not out["checks"]["G4_hot_cold_energy"]
    assert not out["gate_pass"]
    # A 0.6-sd offset also trips R-hat and the exact-reference test.
    e, a = _synthetic(rng, ref, shift=0.006)
    out = cg.evaluate(e, a, starts, CFG, ref)
    assert not out["checks"]["G1_rhat_energy"]
    assert not out["checks"]["G5_exact_energy"]


def test_evaluate_fails_low_per_chain_ess():
    rng = np.random.default_rng(23)
    ref = -1.43
    e, a = _synthetic(rng, ref, phi=0.98, n=2000)
    out = cg.evaluate(e, a, ["random"] * 16 + ["ordered"] * 16, CFG, ref)
    assert not out["checks"]["G3_chain_ess_energy"]
