import copy
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest

from emergence_lab import finite_size_gate as fg

PATH = Path(__file__).parents[1] / "configs" / "finite_size_gate.json"
CFG = json.loads(PATH.read_text())


def _small():
    cfg = copy.deepcopy(CFG)
    cfg.update(sizes=[4, 6, 8], chains_per_start=2, warmup_sweeps=50,
               sample_sweeps={"4": 200, "6": 200, "8": 400}, max_proposals=10_000_000,
               primary_window=[4, 6, 8], stability_windows=[[4, 6, 8]])
    cfg["controls"]["off_critical"].update(chains_per_start=2, warmup_sweeps=20, sample_sweeps=100)
    cfg["controls"]["j0_iid"].update(chains=3, draws=50)
    return cfg


def test_registered_config_frozen_budget_and_seeds():
    assert hashlib.sha256(PATH.read_bytes()).hexdigest() == (
        "2176235a66c7c437d008307ebe8129519b138c7ec62520b0afbda6b073fae6a2")
    proposals = fg.validate_config(CFG)
    assert proposals == 16 * (64 * 30000 + 144 * 30000 + 256 * 30000 + 576 * 50000
                              + 1024 * 50000 + 2304 * 90000) + 8 * 4368 * 25000
    seeds = [fg.seed_for(CFG["base_seed"], li, si, r) for li in range(6) for si in range(2) for r in range(8)]
    off = [fg.seed_for(2033010001, li, si, r) for li in range(6) for si in range(2) for r in range(4)]
    j0 = [fg.seed_for(2034010001, li, 0, r) for li in range(6) for r in range(8)]
    allseeds = seeds + off + j0
    assert len(set(allseeds)) == len(allseeds)
    assert min(allseeds) == 2032010001 and max(allseeds) < 2035000000


@pytest.mark.parametrize("change", [{"sizes": [8, 7]}, {"sizes": [12, 8]}, {"chains_per_start": 1},
                                    {"primary_window": [8, 12]}, {"primary_window": [8, 12, 64]},
                                    {"max_proposals": 7_000_000_000}, {"extra": 1}])
def test_config_rejections(change):
    cfg = copy.deepcopy(CFG)
    cfg.update(change)
    with pytest.raises(ValueError):
        fg.validate_config(cfg)


def test_budget_cap():
    cfg = copy.deepcopy(CFG)
    cfg["max_proposals"] = 1_000_000
    with pytest.raises(ValueError):
        fg.validate_config(cfg)


def test_wls_recovers_exact_power_law_and_scales_error():
    x = np.log([8, 12, 16, 24, 32])
    y = 0.3 + 1.75 * x
    f = fg.wls_slope(x, y, np.full(5, 0.01))
    assert f["slope"] == pytest.approx(1.75, abs=1e-12) and f["chi2_dof"] == pytest.approx(0, abs=1e-18)
    noisy = y + np.array([0.05, -0.05, 0.05, -0.05, 0.05])
    g = fg.wls_slope(x, noisy, np.full(5, 0.01))
    assert g["stderr"] > g["stderr_unscaled"] and g["stderr"] == pytest.approx(
        g["stderr_unscaled"] * math.sqrt(g["chi2_dof"]))
    assert fg.wls_slope(x, y, np.zeros(5))["slope"] is None


def test_jackknife_of_mean_matches_between_chain_se():
    rng = np.random.default_rng(1)
    e = rng.normal(-1.4, 0.05, size=(10, 30))
    m = rng.normal(0.0, 0.3, size=(10, 30))
    jk = fg.jackknife(e, m, 4, 2.0)
    means = e.mean(axis=1)
    assert jk["energy"]["value"] == pytest.approx(e.mean())
    assert jk["energy"]["stderr"] == pytest.approx(means.std(ddof=1) / math.sqrt(10))


def test_derived_quantities_on_known_distribution():
    # two-point |m| = 1 with e = -2 (ordered), equal weights with m = 0, e = 0
    e = np.array([[-2.0, 0.0]])
    m = np.array([[1.0, 0.0]])
    d = fg.derived(fg.moments(e, m), 2, 1.0)
    assert d["chi"] == pytest.approx(4 * 0.5)
    assert d["binder"] == pytest.approx(1 - 0.5 / (3 * 0.25))
    # <e> = -1, <|m| e>/<|m|> = -2 -> d ln<|m|>/dK = N(-1 + 2) = 4 > 0
    assert d["dlnm_dK"] == pytest.approx(4.0)


def test_fit_rule_accepts_exact_and_rejects_wrong_exponents():
    cfg = copy.deepcopy(CFG)
    per = {}
    for L in cfg["sizes"]:
        vals = {"abs_m": L ** -0.125, "chi": L ** 1.75, "dlnm_dK": L ** 1.0}
        per[str(L)] = {"jackknife": {"ln_" + k: {"value": math.log(v), "stderr": 0.002} for k, v in vals.items()}}
    fit = fg.fit_exponents(per, cfg["primary_window"], cfg)
    assert all(fit[k]["pass"] for k in fg.EXPONENTS)
    assert fit["beta_over_nu"]["estimate"] == pytest.approx(0.125)
    for L in cfg["sizes"]:  # J = 0-like: |m| ~ 1/L, chi constant
        per[str(L)]["jackknife"]["ln_abs_m"]["value"] = -math.log(L)
        per[str(L)]["jackknife"]["ln_chi"]["value"] = 0.0
    fit = fg.fit_exponents(per, cfg["primary_window"], cfg)
    assert not fit["beta_over_nu"]["pass"] and not fit["gamma_over_nu"]["pass"]


def test_small_run_deterministic_and_reanalysis_roundtrip():
    cfg = _small()
    fg.validate_config(cfg)
    a = fg.simulate(cfg, workers=1)
    b = fg.simulate(cfg, workers=2)
    ra, rb = fg.raw_npz(a), fg.raw_npz(b)
    assert hashlib.sha256(ra).hexdigest() == hashlib.sha256(rb).hexdigest()
    rep = fg.build_report(cfg, a, ra, {})
    again = fg.build_report(cfg, fg.load_npz(ra), ra, {})
    assert json.dumps(rep, sort_keys=True) == json.dumps(again, sort_keys=True)
    assert set(rep["controls"]) == {"off_critical", "j0_iid"}
    assert any(k.startswith("E1_energy_L") for k in rep["main"]["checks"])
    ps = rep["main"]["per_size"]["8"]
    assert ps["chains"] == 4 and ps["draws_per_chain"] == 200
    assert ps["exact_specific_heat"] > 0


def test_iid_control_is_uncorrelated():
    c = fg.iid_chain(8, 400, 5)
    m = c["magnetization_sum"] / 64
    assert abs(m.mean()) < 0.05 and np.mean(m * m) == pytest.approx(1 / 64, rel=0.25)
