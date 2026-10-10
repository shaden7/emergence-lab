import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from emergence_lab import coverage_gate as cg

PATH = Path(__file__).parents[1] / "configs" / "coverage_gate.json"
CFG = json.loads(PATH.read_text())


def _small():
    cfg = copy.deepcopy(CFG)
    cfg.update(sizes=[4, 8], batches=12, chains_per_batch=4, warmup_sweeps=40,
               sample_sweeps=200, power_control_sweeps=8, max_proposals=10_000_000)
    return cfg


def test_registered_config_is_frozen_and_within_budget():
    assert cg.validate_config(CFG) == 8_192_000_000
    seeds = [cg.seed_for(CFG, i, b, c) for i in range(2) for b in range(400) for c in range(4)]
    assert len(set(seeds)) == 3200
    assert min(seeds) == 2030010001 and max(seeds) == 2030010001 + 100_000 + 3993
    assert hashlib.sha256(PATH.read_bytes()).hexdigest() == (
        "a03e68c5c49e2cb93e4718fe33fd7d99d7820579347593860b661bd81594fc1b")


def test_pass_threshold_and_precision_follow_from_design():
    # 400 batches: worst-case Wilson half-width < 0.05; pass iff >= 372 covered.
    n = CFG["batches"]
    assert max((h - l) / 2 for l, h in (cg.wilson_interval(k, n) for k in range(n + 1))) < 0.05
    assert cg.wilson_interval(372, n)[0] >= 0.90 > cg.wilson_interval(371, n)[0]


@pytest.mark.parametrize("change", [{"batches": 5}, {"sizes": [7]}, {"sizes": [16, 16]},
                                    {"chains_per_batch": 2}, {"power_control_sweeps": 2000},
                                    {"sample_every": 7}, {"max_proposals": 20_000_000_000},
                                    {"sample_sweeps": 300_000}, {"extra": 1}])
def test_schema_and_budget_rejections(change):
    cfg = copy.deepcopy(CFG)
    cfg.update(change)
    with pytest.raises(ValueError):
        cg.validate_config(cfg)


def test_small_run_is_deterministic_and_complete():
    r1, raw1 = cg.run_gate(_small())
    r2, raw2 = cg.run_gate(_small(), workers=2)
    assert raw1 == raw2 and r1["raw_digests"] == r2["raw_digests"]
    for L in ("4", "8"):
        m = r1["sizes"][L]["main"]
        assert m["draws_per_chain"] == 50 and m["energy"]["batches"] == 12
        assert len(m["energy"]["covered_flags"]) == 12
        assert r1["sizes"][L]["power_control"]["draws_per_chain"] == 2
        assert m["per_chain_energy"]["chains"] == 48


def test_exact_l4_reference_is_covered_at_high_rate():
    # 4x4 has an independent brute-force reference; a correct sampler must cover it.
    cfg = _small()
    cfg.update(sizes=[4], batches=40, sample_sweeps=400)
    m = cg.run_gate(cfg)[0]["sizes"]["4"]["main"]
    assert m["energy"]["covered"] >= 34 and abs(m["bias_z"]) < 4


def test_coverage_detects_bias_and_undefined_intervals():
    rng = np.random.default_rng(1)
    ref = -1.4
    good = ref + 0.01 * rng.normal(size=(400, 4))
    ok = cg.batch_coverage(good, ref)
    assert 360 <= ok["covered"] <= 395 and 0.85 < ok["sd_batch_means_over_rms_stderr"] < 1.2
    biased = cg.batch_coverage(good + 0.015, ref)  # 3 x stderr of a 4-chain mean
    assert biased["wilson95"][0] < 0.90
    frozen = good.copy()
    frozen[:10] = ref  # zero spread -> undefined interval, counted as non-coverage
    f = cg.batch_coverage(frozen, ref)
    assert f["undefined_intervals"] == 10 and f["covered"] <= ok["covered"]


def test_gate_logic_on_synthetic_draws():
    rng = np.random.default_rng(2)
    ref = -1.45
    e = ref + 0.02 * rng.normal(size=(400, 4, 60))
    m = np.abs(0.6 + 0.05 * rng.normal(size=(400, 4, 60)))
    good = cg.evaluate_size(e, m, CFG, ref, 10, None)
    assert good["pass"] and not good["bias_flag"]
    bad = cg.evaluate_size(e + 0.01, m, CFG, ref, 10, None)
    assert not bad["pass"] and bad["bias_flag"]


def test_binomial_p_matches_scipy_rule():
    scipy_stats = pytest.importorskip("scipy.stats")
    for k, n, p in [(372, 400, 0.95), (380, 400, 0.95), (395, 400, 0.95), (0, 10, 0.3), (10, 10, 0.3), (7, 24, 0.5)]:
        assert cg.binomial_two_sided_p(k, n, p) == pytest.approx(scipy_stats.binomtest(k, n, p).pvalue, rel=1e-9)


def test_binomial_p_sanity_without_scipy():
    assert cg.binomial_two_sided_p(5, 10, 0.5) == pytest.approx(1.0)
    assert cg.binomial_two_sided_p(0, 10, 0.5) == pytest.approx(2 * 0.5 ** 10)


def test_report_is_json_serializable_and_reanalysis_reproduces_it():
    import io
    report, raw = cg.run_gate(_small())
    text = json.dumps(report)
    assert json.loads(text)["gate_pass"] in (True, False)
    with np.load(io.BytesIO(raw)) as z:
        arrays = {n: z[n] for n in z.files}
    again = cg.analyze(_small(), arrays, raw, {})
    assert again["sizes"] == json.loads(text)["sizes"] and again["raw_npz_sha256"] == report["raw_npz_sha256"]
    arrays["energy_sum_L4"] = arrays["energy_sum_L4"][:, :, :-1]
    with pytest.raises(ValueError):
        cg.analyze(_small(), arrays, raw, {})
