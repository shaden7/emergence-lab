from math import comb
import json
import numpy as np
import pytest
from emergence_lab.exact4 import assess_difference, exact_observables, validate_results
from emergence_lab.ising import run_chain
from emergence_lab.stats import summarize_replicates


@pytest.mark.parametrize("temperature,expected_energy,expected_m", [
    (1.5, -1.9506425614594773, 0.9861732978163789),
    (2.269185, -1.5656240337509293, 0.843860546230359),
    (3.5, -0.7761500504348433, 0.48843718389136415),
])
def test_exact_enumeration_known_reference(temperature, expected_energy, expected_m):
    exact = exact_observables(temperature)
    assert exact["mean_energy_per_spin"] == pytest.approx(expected_energy, abs=1e-7)
    assert exact["mean_abs_magnetization"] == pytest.approx(expected_m, abs=1e-7)
    assert exact["mean_signed_magnetization"] == pytest.approx(0, abs=1e-12)


def test_infinite_temperature_binomial_null_control():
    exact = exact_observables(1e9)
    binomial_mean_abs_m = sum(abs(2*k-16) * comb(16, k) for k in range(17)) / (16 * 2**16)
    assert exact["mean_energy_per_spin"] == pytest.approx(0, abs=1e-7)
    assert exact["mean_abs_magnetization"] == pytest.approx(binomial_mean_abs_m, abs=1e-7)


def test_low_temperature_ground_state_limit():
    exact = exact_observables(0.01)
    assert exact["mean_energy_per_spin"] == pytest.approx(-2, abs=1e-9)
    assert exact["mean_abs_magnetization"] == pytest.approx(1, abs=1e-9)


def test_biased_estimate_fails_and_zero_sem_is_not_evidence():
    assert assess_difference(0.8, 0.01, 0.9)["passes_3p5_sem_diagnostic"] is False
    assert assess_difference(0.9, 0.01, 0.9)["passes_3p5_sem_diagnostic"] is True
    assert assess_difference(0.9, 0.0, 0.9)["passes_3p5_sem_diagnostic"] is False
    with pytest.raises(ValueError):
        exact_observables(-2)


def test_detects_missing_chains(tmp_path):
    config = tmp_path / "config.json"
    cfg = {"sizes": [4], "temperatures": [1.5], "repeats": 4}
    config.write_text(json.dumps(cfg))
    (tmp_path / "manifest.json").write_text(json.dumps({
        "config": cfg, "config_sha256": __import__("hashlib").sha256(config.read_bytes()).hexdigest()
    }))
    (tmp_path / "measurements.csv").write_text("size,temperature,seed\n")
    (tmp_path / "summary.csv").write_text("size,temperature,replicates\n")
    with pytest.raises(ValueError, match="wrong number"):
        validate_results(config, tmp_path)


def test_short_independent_smoke_has_correct_mean_scale():
    # Not a coverage assertion; simply exercises the unchanged simulator with exact reference.
    actual = summarize_replicates([
        run_chain(4, 2.269185, 30, 100, 100 + repeat, sample_every=5)
        for repeat in range(4)
    ])[0]
    assert actual["replicates"] == 4
    assert -2 <= actual["mean_energy_per_spin"] <= 2
    assert 0 <= actual["mean_abs_magnetization"] <= 1
