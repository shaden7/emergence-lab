"""Exact controls for the bounded causal-set spatial-geometry reference."""
import math

import numpy as np
import pytest

from emergence_lab import causal_set_spatial as spatial


def _closure(n, edges):
    relation = np.zeros((n, n), dtype=bool)
    for before, after in edges:
        relation[before, after] = True
    for middle in range(n):
        relation |= (
            relation[:, middle, None] & relation[middle, None, :]
        )
    return relation


def _path_minimization_fixture():
    """Three minimal elements; the 0->2 predistance is longer than 0->1->2."""
    n_padding = 8
    x = list(range(3, 3 + n_padding))          # future of A[0] only
    y = list(range(3 + n_padding, 3 + 2*n_padding))  # future of A[2] only
    u, v, common_02 = 3 + 2*n_padding, 4 + 2*n_padding, 5 + 2*n_padding
    n = common_02 + 1
    edges = [(0, z) for z in x] + [(2, z) for z in y]
    edges += [
        (0, u), (1, u), (x[0], u),  # common future of 0,1; one strict interior
        (1, v), (2, v), (y[0], v),  # common future of 1,2; one strict interior
        (0, common_02), (2, common_02),
    ]
    edges += [(z, common_02) for z in x + y]
    return _closure(n, edges)


def test_minimal_elements_form_the_initial_inextendible_antichain():
    relation = _closure(4, [(0, 1), (2, 3)])
    assert spatial.minimal_antichain(relation).tolist() == [0, 2]
    assert spatial.validate_initial_antichain(
        relation, [0, 2]
    ).tolist() == [0, 2]


def test_antichain_with_incomparable_outside_elements_is_rejected():
    relation = _closure(4, [(0, 1), (2, 3)])
    with pytest.raises(ValueError, match="not initial"):
        spatial.validate_initial_antichain(relation, [0])



def test_maximal_but_non_initial_antichain_is_rejected():
    # {1} is maximal by inclusion in this chain, but is not the initial/past
    # antichain because element 0 lies to its past.
    relation = _closure(3, [(0, 1), (1, 2)])
    with pytest.raises(ValueError, match="not initial"):
        spatial.validate_initial_antichain(relation, [1])

def test_non_antichain_is_rejected():
    relation = _closure(3, [(0, 1)])
    with pytest.raises(ValueError, match="not an antichain"):
        spatial.validate_initial_antichain(relation, [0, 1])


def test_exclusive_future_past_volume_and_minimum_common_future():
    relation = _path_minimization_fixture()
    antichain = spatial.minimal_antichain(relation)
    volumes = spatial.suspended_volumes(relation, antichain)
    u, v, common_02 = 19, 20, 21
    assert antichain.tolist() == [0, 1, 2]
    assert volumes[u] == 1
    assert volumes[v] == 1
    assert volumes[common_02] == 16

    pred = spatial.predistance_matrix(relation, antichain, spacetime_dimension=3)
    assert pred[0, 1] == pytest.approx(pred[1, 2])
    assert pred[0, 2] == pytest.approx(
        2.0 * (16.0 / (math.pi / 3.0)) ** (1.0 / 3.0)
    )
    assert np.array_equal(pred, pred.T)
    assert np.array_equal(np.diag(pred), np.zeros(3))


def test_full_path_minimization_can_be_shorter_than_direct_predistance():
    relation = _path_minimization_fixture()
    pred = spatial.predistance_matrix(relation)
    cutoff = 1.1 * pred[0, 1]
    distance = spatial.spatial_distance_matrix(
        relation, meso_cutoff=cutoff
    )
    assert pred[0, 2] > 2.0 * pred[0, 1]
    assert distance[0, 2] == pytest.approx(2.0 * pred[0, 1])
    assert distance[0, 2] < pred[0, 2]
    assert np.array_equal(distance, distance.T)


def test_meso_cutoff_is_strict():
    relation = _path_minimization_fixture()
    pred = spatial.predistance_matrix(relation)
    distance = spatial.spatial_distance_matrix(
        relation, meso_cutoff=float(pred[0, 1])
    )
    assert math.isinf(distance[0, 1])
    assert math.isinf(distance[1, 2])


def test_missing_common_future_is_censored_not_fabricated():
    relation = _closure(4, [(0, 1), (2, 3)])
    pred = spatial.predistance_matrix(relation)
    distance = spatial.spatial_distance_matrix(
        relation, meso_cutoff=10.0
    )
    assert math.isinf(pred[0, 1])
    assert math.isinf(distance[0, 1])


def test_zero_strict_suspended_volume_is_not_clipped():
    # The common-future element itself is excluded from Past(c), and A is
    # excluded from Fut(A); hence this sparse fixture has V(c)=0 and d~=0.
    relation = _closure(3, [(0, 2), (1, 2)])
    assert spatial.suspended_volumes(relation, [0, 1])[2] == 0
    pred = spatial.predistance_matrix(relation, [0, 1])
    assert pred[0, 1] == 0.0


def test_spacetime_dimension_and_cutoff_validation():
    relation = _closure(2, [])
    with pytest.raises(ValueError, match="spacetime_dimension"):
        spatial.predistance_matrix(relation, spacetime_dimension=1)
    with pytest.raises(ValueError, match="meso_cutoff"):
        spatial.spatial_distance_matrix(relation, meso_cutoff=0)
    with pytest.raises(ValueError, match="meso_cutoff"):
        spatial.spatial_distance_matrix(relation, meso_cutoff=float("inf"))


def test_relation_matrix_must_be_boolean_and_strict():
    with pytest.raises(TypeError, match="boolean"):
        spatial.minimal_antichain(np.zeros((2, 2), dtype=np.int8))
    loop = np.eye(2, dtype=bool)
    with pytest.raises(ValueError, match="irreflexive"):
        spatial.minimal_antichain(loop)



def test_nontransitive_relation_is_rejected():
    relation = np.zeros((3, 3), dtype=bool)
    relation[0, 1] = True
    relation[1, 2] = True
    with pytest.raises(ValueError, match="not transitive"):
        spatial.minimal_antichain(relation)

def test_exact_reference_resource_cap_is_enforced():
    relation = np.zeros((spatial.MAX_REFERENCE_ELEMENTS + 1,) * 2, dtype=bool)
    with pytest.raises(ValueError, match="limited"):
        spatial.minimal_antichain(relation)


def test_inputs_are_not_mutated():
    relation = _path_minimization_fixture()
    before = relation.copy()
    spatial.spatial_distance_matrix(relation, meso_cutoff=100.0)
    assert np.array_equal(relation, before)


def test_geometry_is_invariant_under_vertex_relabeling():
    relation = _path_minimization_fixture()
    original_a = spatial.minimal_antichain(relation)
    original_pred = spatial.predistance_matrix(relation, original_a)
    original_distance = spatial.spatial_distance_matrix(
        relation, original_a, meso_cutoff=1.1 * original_pred[0, 1]
    )

    permutation = np.roll(np.arange(relation.shape[0]), 7)
    inverse = np.empty_like(permutation)
    inverse[permutation] = np.arange(permutation.size)
    relabelled = relation[np.ix_(permutation, permutation)]
    relabelled_a = spatial.minimal_antichain(relabelled)
    mapped_a = inverse[original_a]
    order = np.argsort(mapped_a)

    relabelled_pred = spatial.predistance_matrix(relabelled, relabelled_a)
    relabelled_distance = spatial.spatial_distance_matrix(
        relabelled, relabelled_a,
        meso_cutoff=1.1 * original_pred[0, 1],
    )
    assert np.allclose(
        relabelled_pred, original_pred[np.ix_(order, order)],
        rtol=0.0, atol=1e-14,
    )
    assert np.allclose(
        relabelled_distance, original_distance[np.ix_(order, order)],
        rtol=0.0, atol=1e-14,
    )



def test_minimum_common_future_witnesses_returns_all_tied_minimizers():
    relation = _closure(
        5,
        [
            (0, 2),  # predecessor of both common-future candidates, but not common future
            (0, 3), (1, 3), (2, 3),
            (0, 4), (1, 4), (2, 4),
        ],
    )
    witnesses = spatial.minimum_common_future_witnesses(relation, [0, 1])
    assert witnesses[(0, 1)] == (3, 4)
    assert spatial.predistance_matrix(relation, [0, 1])[0, 1] > 0.0


def test_minimum_common_future_witnesses_reports_empty_common_future():
    relation = _closure(4, [(0, 1), (2, 3)])
    assert spatial.minimum_common_future_witnesses(relation, [0, 2])[(0, 2)] == ()


def test_spatial_distance_pair_mask_excludes_direct_edges_before_dijkstra():
    relation = _closure(3, [(0, 2), (1, 2)])
    allowed = np.eye(2, dtype=np.bool_)
    distance = spatial.spatial_distance_matrix(
        relation, meso_cutoff=1.0, pair_mask=allowed
    )
    assert distance[0, 1] == math.inf
    assert np.array_equal(np.diag(distance), np.zeros(2))


def test_spatial_distance_pair_mask_validation():
    relation = _closure(3, [(0, 2), (1, 2)])
    with pytest.raises(TypeError, match="boolean"):
        spatial.spatial_distance_matrix(
            relation, meso_cutoff=1.0, pair_mask=np.ones((2, 2), dtype=np.int8)
        )
    with pytest.raises(ValueError, match="symmetric"):
        spatial.spatial_distance_matrix(
            relation,
            meso_cutoff=1.0,
            pair_mask=np.array([[True, True], [False, True]], dtype=bool),
        )
    with pytest.raises(ValueError, match="diagonal"):
        spatial.spatial_distance_matrix(
            relation,
            meso_cutoff=1.0,
            pair_mask=np.array([[False, False], [False, True]], dtype=bool),
        )
