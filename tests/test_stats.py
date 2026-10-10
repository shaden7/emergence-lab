import numpy as np
import pytest
from emergence_lab.stats import autocorrelation_diagnostics, independent_chain_interval, summarize_replicates


def test_short_and_trapped_chains_are_not_false_precision():
    assert autocorrelation_diagnostics([1.0] * 100)["stderr"] is None
    assert autocorrelation_diagnostics(np.arange(10))["effective_samples"] is None
    with pytest.raises(ValueError):
        autocorrelation_diagnostics([0.0, np.nan])


def test_correlation_reduces_effective_sample_size():
    rng = np.random.default_rng(42)
    noise = rng.normal(size=4000)
    correlated = np.zeros_like(noise)
    for i in range(1, len(noise)):
        correlated[i] = 0.85 * correlated[i - 1] + noise[i]
    a = autocorrelation_diagnostics(noise)
    b = autocorrelation_diagnostics(correlated)
    assert 0.5 <= a["tau_int"] < 2.0
    assert b["tau_int"] > 2.5 * a["tau_int"]
    assert b["effective_samples"] < a["effective_samples"] / 2


def test_independent_chain_t_interval_and_single_chain():
    mean, se, low, high = independent_chain_interval([0, 2, 4, 6])
    assert mean == 3
    assert se == pytest.approx(np.sqrt(20 / 3) / 2)
    assert low == pytest.approx(3 - 3.182446305 * se)
    assert high == pytest.approx(3 + 3.182446305 * se)
    assert independent_chain_interval([2.0]) == (2.0, None, None, None)


def test_summarizes_independent_chains_not_sweeps():
    rows = [{"size": 8, "temperature": 2.2, "mean_abs_magnetization": v,
             "mean_energy_per_spin": -v, "magnetization_effective_samples": 25.0,
             "energy_effective_samples": 15.0} for v in (0.2, 0.4, 0.6, 0.8)]
    result = summarize_replicates(rows)[0]
    assert result["replicates"] == 4
    assert result["mean_abs_magnetization"] == pytest.approx(0.5)
    assert result["magnetization_stderr"] == pytest.approx(np.std([0.2, 0.4, 0.6, 0.8], ddof=1)/2)
    assert result["min_energy_effective_samples"] == 15.0


def test_cli_creates_auditable_summary_and_manifest(tmp_path, monkeypatch):
    import csv
    import json
    import sys
    from emergence_lab.cli import main

    config = tmp_path / "small.json"
    config.write_text(json.dumps({
        "sizes": [4], "temperatures": [2.2], "repeats": 2,
        "base_seed": 19, "burn_sweeps": 10, "sample_sweeps": 40,
        "sample_every": 2,
    }))
    output = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["emergence-lab", "--config", str(config), "--output", str(output)])
    main()
    with (output / "measurements.csv").open() as f:
        measurements = list(csv.DictReader(f))
    with (output / "summary.csv").open() as f:
        summary = list(csv.DictReader(f))
    manifest = json.loads((output / "manifest.json").read_text())
    assert len(measurements) == 2
    assert len(summary) == 1
    assert summary[0]["replicates"] == "2"
    assert "magnetization_tau_int" in measurements[0]
    assert manifest["result_rows"] == 2
    assert manifest["summary_rows"] == 1
    assert "uncertainty_method" in manifest
