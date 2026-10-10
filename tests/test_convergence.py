import numpy as np
import pytest

from emergence_lab import convergence as cv


def _ar1(rng, m, n, phi, mu=0.0, scale=1.0):
    x = np.empty((m, n))
    x[:, 0] = rng.normal(size=m) / np.sqrt(1 - phi * phi)
    e = rng.normal(size=(m, n))
    for t in range(1, n):
        x[:, t] = phi * x[:, t - 1] + e[:, t]
    return mu + scale * x


def test_iid_ess_close_to_draw_count_and_rhat_near_one():
    rng = np.random.default_rng(11)
    a = rng.normal(size=(8, 2000))
    assert 0.9 * a.size < cv.ess_bulk(a) < 1.1 * a.size
    assert cv.rhat_rank(a) < 1.005


@pytest.mark.parametrize("phi", [0.5, 0.9])
def test_ar1_tau_matches_analytic_value(phi):
    rng = np.random.default_rng(12)
    a = _ar1(rng, 8, 20000, phi)
    tau_true = (1 + phi) / (1 - phi)
    assert abs(cv.ess(a)["tau"] / tau_true - 1) < 0.15
    single = cv.chain_ess(a[0])
    assert abs(single["tau"] / tau_true - 1) < 0.35


def test_location_shift_detected_by_bulk_rhat():
    rng = np.random.default_rng(13)
    a = np.vstack([_ar1(rng, 7, 2000, 0.5), _ar1(rng, 1, 2000, 0.5, mu=1.0)])
    assert cv.rhat_bulk(a) > 1.02


def test_scale_mismatch_detected_by_tail_not_bulk():
    rng = np.random.default_rng(14)
    a = np.vstack([_ar1(rng, 4, 2000, 0.5), _ar1(rng, 4, 2000, 0.5, scale=3.0)])
    assert cv.rhat_bulk(a) < 1.01
    assert cv.rhat_tail(a) > 1.05
    assert cv.rhat_rank(a) == cv.rhat_tail(a)


def test_within_chain_trend_detected_by_split():
    rng = np.random.default_rng(15)
    a = rng.normal(size=(4, 2000)) + np.linspace(0, 2, 2000)
    assert cv.rhat_bulk(a) > 1.1


def test_ranks_average_ties_and_constant_input_undefined():
    assert list(cv.average_ranks([3.0, 1.0, 3.0, 2.0])) == [3.5, 1.0, 3.5, 2.0]
    const = np.ones((4, 100))
    assert cv.ess(const)["ess"] is None
    with pytest.raises(ValueError):
        cv.ess(np.ones((2, 3)))
    with pytest.raises(ValueError):
        cv.rhat_bulk([[0.0, np.nan] * 10])
