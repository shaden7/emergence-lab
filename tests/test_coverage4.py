"""Negative controls for empirical interval coverage audit."""
import pytest

from emergence_lab.coverage4 import run_coverage, wilson_interval


def test_wilson_bounds_at_extremes():
    assert wilson_interval(0, 10)[0] == pytest.approx(0.0)
    assert wilson_interval(10, 10)[1] == pytest.approx(1.0)
    lo, hi = wilson_interval(5, 10)
    assert lo < 0.5 < hi
    for args in ((-1, 5), (6, 5), (0, 0)):
        with pytest.raises(ValueError):
            wilson_interval(*args)


def test_seeded_short_pilot_is_deterministic():
    cfg = dict(temperatures=[1.5], batches=2, chains_per_batch=4,
               base_seed=2099990000, burn_sweeps=10, sample_sweeps=35, sample_every=5)
    result = run_coverage(cfg)
    assert result == run_coverage(cfg)
    assert len(result["batches"]) == 4
    assert len(result["aggregates"]) == 2
    for row in result["aggregates"]:
        assert 0 <= row["wilson95_low"] <= row["wilson95_high"] <= 1
    for record in result["batches"]:
        assert isinstance(record["covered"], bool)


def test_rejects_excessive_or_invalid_plan():
    cfg = dict(temperatures=[1.5], batches=2, chains_per_batch=4,
               base_seed=2099990000, burn_sweeps=10, sample_sweeps=35, sample_every=5)
    for change in (dict(batches=1), dict(chains_per_batch=3), dict(sample_every=0),
                   dict(temperatures=[]), dict(temperatures=[1.5, 1.5]),
                   dict(batches=200), dict(sample_sweeps=0)):
        with pytest.raises(ValueError):
            run_coverage({**cfg, **change})
