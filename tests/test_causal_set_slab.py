"""Deterministic engineering controls for the finite Minkowski slab sampler."""
import numpy as np
import pytest

from emergence_lab.causal_set_mm import check_partial_order
from emergence_lab.causal_set_spatial import (
    minimal_antichain,
    predistance_matrix,
    spatial_distance_matrix,
)
from emergence_lab.causal_set_slab import (
    PoissonDrawExceedsLimit,
    expected_poisson_count,
    minkowski_slab_causal_relation,
    minkowski_slab_volume,
    poisson_sprinkle_minkowski_slab,
)


def test_rectangular_slab_volume_and_poisson_mean_are_exact():
    assert minkowski_slab_volume(
        time_extent=4, x_extent=4, y_extent=4
    ) == 64.0
    assert expected_poisson_count(
        density=0.5, time_extent=4, x_extent=4, y_extent=4
    ) == 32.0


def test_poisson_mean_overflow_is_rejected():
    with pytest.raises(ValueError, match="Poisson mean"):
        expected_poisson_count(
            density=1e308, time_extent=1.0, x_extent=1.0, y_extent=1.0
        )


def test_slab_volume_overflow_is_rejected():
    with pytest.raises(ValueError, match="volume"):
        minkowski_slab_volume(
            time_extent=1e308, x_extent=1e308, y_extent=1.0
        )


def test_invalid_max_elements_is_rejected():
    for value in (-1, 1.5, True):
        with pytest.raises(ValueError, match="max_elements"):
            poisson_sprinkle_minkowski_slab(
                np.random.default_rng(0),
                density=1.0,
                time_extent=1.0,
                x_extent=1.0,
                y_extent=1.0,
                max_elements=value,
            )


def test_sampler_matches_one_unconditioned_poisson_draw_and_uniform_coordinates():
    seed = 1234
    expected_rng = np.random.default_rng(seed)
    expected_count = int(expected_rng.poisson(64.0))
    unit = expected_rng.random((expected_count, 3), dtype=np.float64)
    expected = unit * np.array([4.0, 4.0, 4.0]) + np.array([0.0, -2.0, -2.0])

    actual = poisson_sprinkle_minkowski_slab(
        np.random.default_rng(seed),
        density=1.0,
        time_extent=4.0,
        x_extent=4.0,
        y_extent=4.0,
    )
    assert np.array_equal(actual, expected)
    assert actual.shape == (expected_count, 3)
    assert np.all((actual[:, 0] >= 0.0) & (actual[:, 0] < 4.0))
    assert np.all((actual[:, 1] >= -2.0) & (actual[:, 1] < 2.0))
    assert np.all((actual[:, 2] >= -2.0) & (actual[:, 2] < 2.0))


def test_same_seed_reproduces_the_same_sprinkling():
    kwargs = dict(
        density=1.0,
        time_extent=4.0,
        x_extent=4.0,
        y_extent=4.0,
    )
    left = poisson_sprinkle_minkowski_slab(np.random.default_rng(42), **kwargs)
    right = poisson_sprinkle_minkowski_slab(np.random.default_rng(42), **kwargs)
    assert np.array_equal(left, right)


def test_empty_poisson_realisation_is_not_conditioned_away():
    points = poisson_sprinkle_minkowski_slab(
        np.random.default_rng(0),
        density=1e-6,
        time_extent=1.0,
        x_extent=1.0,
        y_extent=1.0,
    )
    assert points.shape == (0, 3)
    relation = minkowski_slab_causal_relation(points)
    assert relation.shape == (0, 0)
    with pytest.raises(ValueError, match="at least one element"):
        minimal_antichain(relation)


def test_resource_guard_reports_the_draw_without_truncating_or_redrawing():
    seed = 0
    expected_rng = np.random.default_rng(seed)
    expected_count = int(expected_rng.poisson(64.0))
    assert expected_count > 0
    expected_next = float(expected_rng.random())

    actual_rng = np.random.default_rng(seed)
    with pytest.raises(PoissonDrawExceedsLimit) as caught:
        poisson_sprinkle_minkowski_slab(
            actual_rng,
            density=1.0,
            time_extent=4.0,
            x_extent=4.0,
            y_extent=4.0,
            max_elements=expected_count - 1,
        )
    assert caught.value.sampled_count == expected_count
    assert caught.value.max_elements == expected_count - 1
    assert "no truncation or resampling" in str(caught.value)
    # The only random operation was the one Poisson count draw.
    assert float(actual_rng.random()) == expected_next


def test_slab_causal_relation_is_a_strict_partial_order():
    points = poisson_sprinkle_minkowski_slab(
        np.random.default_rng(7),
        density=1.0,
        time_extent=4.0,
        x_extent=4.0,
        y_extent=4.0,
    )
    relation = minkowski_slab_causal_relation(points)
    assert relation.dtype == np.bool_
    assert not np.any(np.diag(relation))
    check_partial_order(relation)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"density": 0.0, "time_extent": 1.0, "x_extent": 1.0, "y_extent": 1.0},
        {"density": 1.0, "time_extent": float("inf"), "x_extent": 1.0, "y_extent": 1.0},
        {"density": 1.0, "time_extent": 1.0, "x_extent": -1.0, "y_extent": 1.0},
        {"density": True, "time_extent": 1.0, "x_extent": 1.0, "y_extent": 1.0},
    ],
)
def test_invalid_region_or_density_is_rejected(kwargs):
    with pytest.raises(ValueError):
        poisson_sprinkle_minkowski_slab(np.random.default_rng(0), **kwargs)


def test_invalid_rng_and_bad_point_coordinates_are_rejected():
    with pytest.raises(TypeError, match="Generator"):
        poisson_sprinkle_minkowski_slab(
            np.random.RandomState(0),
            density=1.0,
            time_extent=1.0,
            x_extent=1.0,
            y_extent=1.0,
        )
    with pytest.raises(ValueError, match="shape"):
        minkowski_slab_causal_relation(np.zeros((3, 2)))
    with pytest.raises(ValueError, match="finite"):
        minkowski_slab_causal_relation(np.array([[0.0, np.nan, 0.0]]))



def test_poisson_slab_sample_runs_through_exact_spatial_geometry_oracle():
    points = poisson_sprinkle_minkowski_slab(
        np.random.default_rng(7),
        density=1.0,
        time_extent=4.0,
        x_extent=4.0,
        y_extent=4.0,
    )
    relation = minkowski_slab_causal_relation(points)
    antichain = minimal_antichain(relation)
    predistance = predistance_matrix(relation, antichain)
    distance = spatial_distance_matrix(
        relation, antichain, meso_cutoff=5.0
    )

    assert antichain.size > 0
    assert predistance.shape == (antichain.size, antichain.size)
    assert distance.shape == predistance.shape
    assert np.allclose(predistance, predistance.T)
    assert np.allclose(distance, distance.T)
    assert np.all(np.diag(predistance) == 0.0)
    assert np.all(np.diag(distance) == 0.0)
    assert np.all(predistance >= 0.0)
    assert np.all(distance >= 0.0)
