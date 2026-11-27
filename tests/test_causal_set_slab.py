"""Deterministic engineering controls for the finite Minkowski slab sampler."""
import numpy as np
import pytest

from emergence_lab.causal_set_mm import check_partial_order
from emergence_lab.causal_set_spatial import (
    minimal_antichain,
    minimum_common_future_witnesses,
    predistance_matrix,
    spatial_distance_matrix,
    suspended_volumes,
)
from emergence_lab.causal_set_slab import (
    MAX_SLAB_ELEMENTS,
    PoissonDrawExceedsLimit,
    expected_poisson_count,
    minkowski_slab_causal_relation,
    minkowski_slab_volume,
    poisson_sprinkle_minkowski_slab,
    side_boundary_censor_mask,
)


def test_rectangular_slab_volume_and_poisson_mean_are_exact():
    assert minkowski_slab_volume(
        time_extent=4, x_extent=4, y_extent=4
    ) == 64.0
    assert expected_poisson_count(
        density=0.5, time_extent=4, x_extent=4, y_extent=4
    ) == 32.0


def test_poisson_mean_underflow_is_rejected():
    with pytest.raises(ValueError, match="Poisson mean"):
        expected_poisson_count(
            density=1e-300, time_extent=1e-100, x_extent=1.0, y_extent=1.0
        )


def test_poisson_mean_overflow_is_rejected():
    with pytest.raises(ValueError, match="Poisson mean"):
        expected_poisson_count(
            density=1e308, time_extent=1.0, x_extent=1.0, y_extent=1.0
        )


def test_slab_volume_underflow_is_rejected():
    with pytest.raises(ValueError, match="volume"):
        minkowski_slab_volume(
            time_extent=1e-200, x_extent=1e-200, y_extent=1e-200
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



@pytest.mark.parametrize("limit", [MAX_SLAB_ELEMENTS + 1, 10**9])
def test_sampler_cannot_raise_the_dense_reference_allocation_cap(limit):
    rng = np.random.default_rng(20261127)
    state_before = rng.bit_generator.state
    with pytest.raises(ValueError, match="no greater than"):
        poisson_sprinkle_minkowski_slab(
            rng,
            density=1.0,
            time_extent=1.0,
            x_extent=1.0,
            y_extent=1.0,
            max_elements=limit,
        )
    # Invalid caps are rejected before consuming the Poisson draw.
    assert rng.bit_generator.state == state_before


def test_slab_relation_rejects_more_than_the_dense_reference_cap():
    points = np.zeros((MAX_SLAB_ELEMENTS + 1, 3), dtype=np.float64)
    with pytest.raises(ValueError, match="limited to N"):
        minkowski_slab_causal_relation(points)


def test_slab_relation_is_exact_for_large_finite_coordinates_and_overflowing_differences():
    squared_overflow = np.array(
        [[0.0, 0.0, 0.0], [1e200, 2.5e199, 0.0]], dtype=np.float64
    )
    assert minkowski_slab_causal_relation(squared_overflow)[0, 1]

    difference_overflow = np.array(
        [[-1e308, 0.0, 0.0], [1e308, 1e308, 0.0]], dtype=np.float64
    )
    assert minkowski_slab_causal_relation(difference_overflow)[0, 1]


def test_slab_relation_excludes_exact_null_pairs_and_keeps_strict_timelike_pairs():
    just_above_five = np.nextafter(5.0, np.inf)
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [5.0, 3.0, 4.0],
            [just_above_five, 3.0, 4.0],
        ],
        dtype=np.float64,
    )
    relation = minkowski_slab_causal_relation(points)
    assert not relation[0, 1]  # exactly null: 5^2 == 3^2 + 4^2
    assert relation[0, 2]  # strictly timelike by one binary64 step



def test_slab_volume_avoids_intermediate_overflow_and_underflow():
    assert minkowski_slab_volume(
        time_extent=1e308, x_extent=1e308, y_extent=1e-308
    ) == pytest.approx(1e308)
    assert minkowski_slab_volume(
        time_extent=1e-308, x_extent=1e-308, y_extent=1e308
    ) == pytest.approx(1e-308)


def test_slab_relation_rejects_oversized_sized_input_before_array_conversion():
    class OversizedSequence:
        def __len__(self):
            return MAX_SLAB_ELEMENTS + 1

        def __array__(self, dtype=None):
            raise AssertionError("oversized input must be rejected before conversion")

    with pytest.raises(ValueError, match="limited to N"):
        minkowski_slab_causal_relation(OversizedSequence())



def _mixed_safe_unsafe_minimizer_fixture():
    # For antichain pair (0, 7), witnesses 2 and 6 tie at V=1.
    # Witness 2 is side-clipped; witness 6 is safe. The pair must be retained
    # without choosing a witness by its arbitrary vertex index.
    return np.array(
        [
            [0.41512569403879285, 3.347997377836343, 0.7167858080893694],
            [7.3397917361079745, -4.090912161765893, 1.8755478700098998],
            [11.958872634957238, 6.290149216477133, -6.958618907894124],
            [5.717426491438222, -7.039629366675912, -13.142902247407664],
            [10.64249926223192, -6.788792145618759, -9.46089575028697],
            [1.8223630624294436, 2.097147214375184, 0.8269351893954653],
            [7.81732640911207, 3.7510027118713722, 4.319114819943504],
            [0.7747522947481045, 7.311049218825975, -0.46177947442382816],
        ],
        dtype=np.float64,
    )


def _unsafe_minimum_safe_higher_volume_fixture():
    # For pair (5, 14), witness 2 is the unsafe global minimum (V=1).
    # Element 13 is safe but has V=2, so it must not rescue the pair.
    return np.array(
        [
            [8.302614569350215, 1.0020836258342634, 0.11589781566519619],
            [7.828567801773363, -8.909068639968124, -1.4527672380367935],
            [10.393171340501102, -3.895437190736663, 8.009697914295558],
            [9.05455136502443, -5.390736008512942, -3.117008701066746],
            [11.171410687623425, -10.875904224664968, 4.697105098908473],
            [1.8688531975013767, -5.554186256112281, 3.794166049721131],
            [2.1444969765136697, -14.494424424831235, 7.475025783743657],
            [8.91063589422582, 9.854012311721732, 8.811429682301963],
            [0.9887559627135776, -11.415516783808918, 13.578437911239835],
            [1.8986709241640791, 5.020040067942116, -14.127728152688729],
            [3.611807116163703, -2.806067927948847, -13.148209058708199],
            [4.663035743448916, 6.645292572334842, 9.843540184511586],
            [4.315609918838547, 0.4502184882108544, 4.16181143568334],
            [11.21899866069256, 3.212443601932467, 0.7606826334606751],
            [0.5471081168136003, 3.130920328106786, 3.517780824643328],
        ],
        dtype=np.float64,
    )





def _side_margin(point, x_extent=30.0, y_extent=30.0):
    t, x, y = point
    margin = min(
        x + x_extent / 2.0,
        x_extent / 2.0 - x,
        y + y_extent / 2.0,
        y_extent / 2.0 - y,
    )
    return t, margin


def test_side_boundary_censor_keeps_pair_with_one_safe_tied_minimizer():
    points = _mixed_safe_unsafe_minimizer_fixture()
    relation = minkowski_slab_causal_relation(points)
    antichain = minimal_antichain(relation)
    assert antichain.tolist() == [0, 1, 3, 7]

    witnesses = minimum_common_future_witnesses(relation, antichain)
    assert witnesses[(0, 7)] == (2, 6)
    volumes = suspended_volumes(relation, antichain)
    assert volumes[2] == volumes[6] == 1
    t_unsafe, margin_unsafe = _side_margin(points[2])
    t_safe, margin_safe = _side_margin(points[6])
    assert margin_unsafe < t_unsafe
    assert margin_safe >= t_safe

    mask = side_boundary_censor_mask(
        points, relation, antichain,
        time_extent=12.0, x_extent=30.0, y_extent=30.0,
    )
    # Antichain order is [0, 1, 3, 7], so pair (0, 7) is [0, 3].
    assert mask[0, 3]
    assert np.array_equal(mask, mask.T)
    assert np.all(np.diag(mask))


def test_side_boundary_censor_rejects_unsafe_minimum_even_with_safe_higher_candidate():
    points = _unsafe_minimum_safe_higher_volume_fixture()
    relation = minkowski_slab_causal_relation(points)
    antichain = minimal_antichain(relation)
    assert antichain.tolist() == [1, 5, 6, 8, 9, 10, 11, 14]

    witnesses = minimum_common_future_witnesses(relation, antichain)
    assert witnesses[(5, 14)] == (2,)
    volumes = suspended_volumes(relation, antichain)
    assert volumes[2] == 1
    assert volumes[13] == 2  # safe, but not a global minimizer
    t_unsafe, margin_unsafe = _side_margin(points[2])
    t_safe, margin_safe = _side_margin(points[13])
    assert margin_unsafe < t_unsafe
    assert margin_safe >= t_safe

    mask = side_boundary_censor_mask(
        points, relation, antichain,
        time_extent=12.0, x_extent=30.0, y_extent=30.0,
    )
    # Pair (5, 14) occupies antichain positions (1, 7).
    assert not mask[1, 7]


def test_side_boundary_censor_is_invariant_under_vertex_relabeling():
    points = _mixed_safe_unsafe_minimizer_fixture()
    relation = minkowski_slab_causal_relation(points)
    antichain = minimal_antichain(relation)
    original = side_boundary_censor_mask(
        points, relation, antichain,
        time_extent=12.0, x_extent=30.0, y_extent=30.0,
    )

    permutation = np.array([5, 2, 7, 0, 6, 3, 1, 4])
    inverse = np.empty_like(permutation)
    inverse[permutation] = np.arange(permutation.size)
    permuted_points = points[permutation]
    permuted_relation = minkowski_slab_causal_relation(permuted_points)
    permuted_antichain = minimal_antichain(permuted_relation)
    mapped_antichain = inverse[antichain]
    order = np.argsort(mapped_antichain)
    permuted = side_boundary_censor_mask(
        permuted_points, permuted_relation, permuted_antichain,
        time_extent=12.0, x_extent=30.0, y_extent=30.0,
    )
    assert np.array_equal(permuted, original[np.ix_(order, order)])


def test_side_boundary_censor_rejects_relation_not_matching_embedding():
    points = _mixed_safe_unsafe_minimizer_fixture()
    relation = minkowski_slab_causal_relation(points)
    wrong = relation.copy()
    wrong[0, 1] = True
    with pytest.raises(ValueError, match="Minkowski relation"):
        side_boundary_censor_mask(
            points, wrong, time_extent=12.0, x_extent=30.0, y_extent=30.0
        )


def test_side_boundary_censor_rejects_points_outside_declared_slab():
    points = _mixed_safe_unsafe_minimizer_fixture()
    relation = minkowski_slab_causal_relation(points)
    outside = points.copy()
    outside[0, 1] = 15.0  # upper x boundary is excluded
    with pytest.raises(ValueError, match="half-open slab"):
        side_boundary_censor_mask(
            outside, relation, time_extent=12.0, x_extent=30.0, y_extent=30.0
        )


def test_sampler_rejects_unrepresentable_half_extents_and_time_interior():
    smallest = np.nextafter(0.0, 1.0)
    base = dict(
        density=1.0, time_extent=1.0, x_extent=1.0, y_extent=1.0
    )
    for extent in (smallest, 3.0 * smallest):
        with pytest.raises(ValueError, match="half-extents"):
            poisson_sprinkle_minkowski_slab(
                np.random.default_rng(0), **{**base, "x_extent": extent}
            )
    with pytest.raises(ValueError, match="positive coordinate"):
        poisson_sprinkle_minkowski_slab(
            np.random.default_rng(0), **{**base, "time_extent": smallest}
        )



def test_side_boundary_censor_keeps_no_common_future_pair_censored():
    points = np.array([[0.0, -1.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float64)
    relation = minkowski_slab_causal_relation(points)
    antichain = minimal_antichain(relation)
    assert minimum_common_future_witnesses(relation, antichain)[(0, 1)] == ()
    mask = side_boundary_censor_mask(
        points, relation, antichain,
        time_extent=0.5, x_extent=4.0, y_extent=4.0,
    )
    assert not mask[0, 1]
