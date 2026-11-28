import random
from collections import Counter
from fractions import Fraction

import numpy as np
import pytest

import emergence_lab.uipt_peeling as uipt_peeling

from emergence_lab.dimension_d1 import _from_multiedges
from emergence_lab.spectral_dimension import graph_even_returns
from emergence_lab.uipt_peeling import (
    FreeTransition,
    UIPTSamplingLimitError,
    UIPTTransition,
    _CombinatorialMap,
    _draw_exact,
    free_transition_probabilities,
    sample_uipt_neighborhood,
    uipt_transition_probabilities,
)


def test_exact_uipt_transition_probabilities_sum_to_one():
    for m in range(8):
        outcomes = uipt_transition_probabilities(m)
        assert sum(outcome.probability for outcome in outcomes) == Fraction(1)

    m0 = uipt_transition_probabilities(0)
    assert [(outcome.kind, outcome.probability) for outcome in m0] == [
        ("new", Fraction(1, 1)),
    ]
    m1 = uipt_transition_probabilities(1)
    assert [outcome.probability for outcome in m1] == [
        Fraction(5, 6),
        Fraction(1, 12),
        Fraction(1, 12),
    ]

    m2 = uipt_transition_probabilities(2)
    assert [outcome.probability for outcome in m2] == [
        Fraction(7, 9),
        Fraction(1, 90),
        Fraction(1, 10),
        Fraction(1, 10),
        Fraction(1, 90),
    ]


def test_exact_free_boltzmann_digon_and_triangle_probabilities():
    m0 = free_transition_probabilities(0)
    assert [(outcome.kind, outcome.probability) for outcome in m0] == [
        ("new", Fraction(1, 9)),
        ("empty", Fraction(8, 9)),
    ]
    m1 = free_transition_probabilities(1)
    assert [(outcome.kind, outcome.probability) for outcome in m1] == [
        ("new", Fraction(1, 4)),
        ("split", Fraction(3, 4)),
    ]
    for m in range(8):
        assert sum(outcome.probability for outcome in free_transition_probabilities(m)) == 1


def test_local_sample_has_one_boundary_and_a_valid_rotation_system():
    sample = sample_uipt_neighborhood(radius=3, seed=0)

    assert sample.root == 0
    assert sample.root_edge == (0, 1)
    assert sample.dart_origin[sample.root_edge_dart] == 0
    assert sample.dart_target[sample.root_edge_dart] == 1
    assert sample.face_kinds.count("boundary") == 1
    assert sample.face_kinds[sample.boundary_face_index] == "boundary"
    assert sample.n_triangles == sample.face_kinds.count("triangle")
    assert sample.n_edges == len(sample.dart_origin) // 2
    assert sample.n_vertices - sample.n_edges + sample.n_faces == 2

    assert len(set(sample.boundary_vertices)) == len(sample.boundary_vertices)
    assert all(sample.distances[v] >= sample.radius for v in sample.boundary_vertices)
    assert not set(sample.boundary_vertices).intersection(
        np.flatnonzero(sample.distances < sample.radius)
    )

    n_darts = len(sample.dart_origin)
    assert len(sample.dart_target) == n_darts
    assert len(sample.dart_twin) == n_darts
    assert np.array_equal(sample.dart_twin[sample.dart_twin], np.arange(n_darts))
    assert np.array_equal(
        sample.dart_origin,
        sample.dart_target[sample.dart_twin],
    )
    assert np.array_equal(
        sample.dart_target,
        sample.dart_origin[sample.dart_twin],
    )

    face_darts = [dart for cycle in sample.face_cycles for dart in cycle]
    assert sorted(face_darts) == list(range(n_darts))
    for cycle in sample.face_cycles:
        for dart, next_dart in zip(cycle, cycle[1:] + cycle[:1]):
            assert sample.dart_target[dart] == sample.dart_origin[next_dart]

    rotation_darts = [dart for rotation in sample.rotation_system for dart in rotation]
    assert sorted(rotation_darts) == list(range(n_darts))
    for vertex, rotation in enumerate(sample.rotation_system):
        assert rotation
        assert all(sample.dart_origin[dart] == vertex for dart in rotation)

    assert sample.free_fill_steps > 0
    assert sample.stats["free_empty_digon_closures"] > 0


def test_local_sample_preserves_parallel_edge_multiplicity():
    sample = sample_uipt_neighborhood(radius=3, seed=0)
    adjacency = sample.graph.csr()
    rows = np.repeat(np.arange(sample.graph.n), np.diff(adjacency.indptr))
    multiplicities = Counter(
        (int(row), int(column))
        for row, column in zip(rows, adjacency.indices)
        if row < column
    )
    assert max(multiplicities.values()) > 1
    assert np.all(adjacency.data == 1)


def test_local_sample_is_deterministic_for_a_fixed_seed():
    first = sample_uipt_neighborhood(radius=3, seed=123)
    second = sample_uipt_neighborhood(radius=3, seed=123)
    assert np.array_equal(first.dart_origin, second.dart_origin)
    assert np.array_equal(first.dart_target, second.dart_target)
    assert np.array_equal(first.dart_twin, second.dart_twin)
    assert np.array_equal(first.distances, second.distances)
    assert first.face_cycles == second.face_cycles
    assert first.rotation_system == second.rotation_system
    assert first.stats == second.stats


def test_ball_and_even_return_locality_contract():
    sample = sample_uipt_neighborhood(radius=3, seed=777)
    assert sample.ball_size(0) == 1
    assert sample.ball_size(1) >= 3
    assert sample.ball_size(3) >= sample.ball_size(2)
    with pytest.raises(ValueError, match="exceeds"):
        sample.ball_size(4)

    observed = sample.even_returns([1, 2])
    adjacency = sample.graph.csr().toarray().astype(float)
    transition = adjacency / sample.graph.degrees[:, None]
    for half_time in (1, 2):
        expected = np.linalg.matrix_power(transition, 2 * half_time)[
            sample.root, sample.root
        ]
        assert observed[half_time] == pytest.approx(expected, abs=1e-13)

    with pytest.raises(ValueError, match="complete endpoint degrees"):
        sample.even_returns([3])


def _is_bipartite(graph):
    adjacency = graph.csr()
    colors = [None] * graph.n
    for start in range(graph.n):
        if colors[start] is not None:
            continue
        colors[start] = 0
        pending = [start]
        while pending:
            u = pending.pop()
            for position in range(adjacency.indptr[u], adjacency.indptr[u + 1]):
                v = int(adjacency.indices[position])
                if colors[v] is None:
                    colors[v] = 1 - colors[u]
                    pending.append(v)
                elif colors[v] == colors[u]:
                    return False
    return True


def test_irregular_finite_type_ii_control_root_law_period_and_stationary_floor():
    edges = [
        (0, 1), (1, 2), (2, 0),
        (3, 0), (3, 1), (3, 2),
        (4, 0), (4, 1), (4, 2),
    ]
    edge_u = np.asarray([edge[0] for edge in edges], dtype=np.int32)
    edge_v = np.asarray([edge[1] for edge in edges], dtype=np.int32)
    graph = _from_multiedges(5, edge_u, edge_v)

    # Triangular bipyramid: six triangular faces, nine edges, five vertices.
    faces = [
        (3, 0, 1), (3, 1, 2), (3, 2, 0),
        (4, 0, 1), (4, 1, 2), (4, 2, 0),
    ]
    face_edge_counts = Counter(
        tuple(sorted((u, v)))
        for face in faces
        for u, v in zip(face, face[1:] + face[:1])
    )
    assert len(faces) == 6
    assert len(face_edge_counts) == 9
    assert set(face_edge_counts.values()) == {2}
    assert set(face_edge_counts) == {tuple(sorted(edge)) for edge in edges}
    assert 5 - 9 + 6 == 2
    assert graph.csr().nnz // 2 == 9
    assert graph.degrees.tolist() == [4, 4, 4, 3, 3]
    assert not _is_bipartite(graph)  # connected and non-bipartite implies period 1

    degrees = graph.degrees.tolist()
    edge_root_law = [Fraction(degree, 18) for degree in degrees]
    mean_degree = Fraction(18, 5)
    uniform_vertex_weights = [
        probability * mean_degree / degree
        for probability, degree in zip(edge_root_law, degrees)
    ]
    assert edge_root_law == [
        Fraction(2, 9), Fraction(2, 9), Fraction(2, 9),
        Fraction(1, 6), Fraction(1, 6),
    ]
    assert uniform_vertex_weights == [Fraction(1, 5)] * 5
    assert Fraction(degrees[0], 18) == Fraction(2, 9)
    assert Fraction(degrees[3], 18) == Fraction(1, 6)

    adjacency = graph.csr().toarray().astype(float)
    transition = adjacency / graph.degrees[:, None]
    stationary = graph.degrees.astype(float) / graph.degrees.sum()
    assert np.allclose(stationary @ transition, stationary, atol=1e-15)
    assert np.linalg.matrix_power(transition, 200)[3, 3] == pytest.approx(
        1 / 6, abs=1e-12
    )

    observed = graph_even_returns(graph, 3, [1, 2, 3])
    for half_time in (1, 2, 3):
        expected = np.linalg.matrix_power(transition, 2 * half_time)[3, 3]
        assert observed[half_time] == pytest.approx(expected, abs=1e-13)


def test_resource_limit_raises_instead_of_returning_a_partial_sample():
    with pytest.raises(UIPTSamplingLimitError, match="budget exceeded"):
        sample_uipt_neighborhood(
            radius=1,
            seed=0,
            max_total_peel_steps=0,
        )

def test_partition_recurrences_match_direct_factorial_probabilities():
    import math

    def z(m):
        return (
            Fraction(math.factorial(2 * m), math.factorial(m) * math.factorial(m + 2))
            * Fraction(9, 4) ** (m + 1)
        )

    def c(m):
        return (
            Fraction(math.factorial(2 * m + 1), math.factorial(m) ** 2)
            * Fraction(9, 4) ** m
        )

    alpha = Fraction(27, 2)
    for m in range(20):
        expected_uipt = [c(m + 1) / (alpha * c(m))]
        for i in range(1, m + 1):
            expected_uipt.extend((
                z(m - i) * c(i - 1) / c(m),
                c(m - i) * z(i - 1) / c(m),
            ))
        assert [x.probability for x in uipt_transition_probabilities(m)] == expected_uipt

        expected_free = [z(m + 1) / (alpha * z(m))]
        if m == 0:
            expected_free.append(1 / z(0))
        else:
            expected_free.extend(z(i - 1) * z(m - i) / z(m) for i in range(1, m + 1))
        assert [x.probability for x in free_transition_probabilities(m)] == expected_free


def test_exact_categorical_draw_refines_a_dyadic_interval_crossing_a_boundary():
    class ScriptedBits:
        def __init__(self, chunks):
            self.chunks = iter(chunks)

        def getrandbits(self, bit_count):
            assert bit_count == 64
            return next(self.chunks)

    outcomes = (
        FreeTransition("new", None, Fraction(1, 3)),
        FreeTransition("empty", None, Fraction(2, 3)),
    )
    first_prefix = (1 << 64) // 3
    assert _draw_exact(ScriptedBits([first_prefix, 0]), outcomes) == outcomes[0]
    assert _draw_exact(
        ScriptedBits([first_prefix, (1 << 64) - 1]),
        outcomes,
    ) == outcomes[1]


def test_empty_digon_gluing_merges_the_two_boundary_edges_and_preserves_map():
    state = _CombinatorialMap(
        max_vertices=10,
        max_total_peel_steps=10,
        max_boundary_parameter=10,
    )
    cycle = state.faces[state.boundary_face]
    state._set_face(state.boundary_face, cycle[1:] + cycle[:1], "boundary")
    face_t1, face_t2 = state._add_triangle(state.boundary_face, 1)
    state.boundary_face = face_t1

    digon = state.faces[face_t2]
    boundary_dart_0, boundary_dart_1 = digon
    interior_dart_0 = state.twin[boundary_dart_0]
    interior_dart_1 = state.twin[boundary_dart_1]
    edges_before = sum(
        1 for dart, active in enumerate(state.active)
        if active and dart < state.twin[dart]
    )
    faces_before = len(state.faces)

    state._close_empty_digon(face_t2)

    assert not state.active[boundary_dart_0]
    assert not state.active[boundary_dart_1]
    assert state.twin[interior_dart_0] == interior_dart_1
    assert state.twin[interior_dart_1] == interior_dart_0
    edges_after = sum(
        1 for dart, active in enumerate(state.active)
        if active and dart < state.twin[dart]
    )
    assert edges_before - edges_after == 1
    assert faces_before - len(state.faces) == 1
    state._validate(radius=0)


@pytest.mark.parametrize(("infinite_side", "expected_boundary_face"), [
    ("T1", 3),
    ("T2", 4),
])
def test_sample_assigns_the_named_infinite_closure_side(
    monkeypatch,
    infinite_side,
    expected_boundary_face,
):
    state = _CombinatorialMap(
        max_vertices=10,
        max_total_peel_steps=1,
        max_boundary_parameter=10,
    )

    def force_closure(_rng, _outcomes):
        return UIPTTransition(
            "closure",
            1,
            infinite_side,
            Fraction(1, 12),
        )

    monkeypatch.setattr(uipt_peeling, "_draw_exact", force_closure)
    with pytest.raises(UIPTSamplingLimitError, match="peeling-step budget"):
        state.sample(radius=1, seed=0)
    assert state.boundary_face == expected_boundary_face


def test_two_empty_digons_close_the_split_triangle_to_a_sphere(monkeypatch):
    state = _CombinatorialMap(
        max_vertices=10,
        max_total_peel_steps=10,
        max_boundary_parameter=10,
    )
    cycle = state.faces[state.boundary_face]
    state._set_face(state.boundary_face, cycle[1:] + cycle[:1], "boundary")
    face_t1, face_t2 = state._add_triangle(state.boundary_face, 1)

    def force_empty(_rng, _outcomes):
        return FreeTransition("empty", None, Fraction(8, 9))

    monkeypatch.setattr(uipt_peeling, "_draw_exact", force_empty)
    state._fill_free_component(face_t1, random.Random(0))
    state._fill_free_component(face_t2, random.Random(1))

    assert state.stats["free_empty_digon_closures"] == 2
    assert set(state.face_kind.values()) == {"triangle"}
    active_darts = [d for d, active in enumerate(state.active) if active]
    assert len(active_darts) == 6
    edges = len(active_darts) // 2
    assert state.n_vertices - edges + len(state.faces) == 2
    assert len(state.faces) == 2
    state._rotation_system()


def test_boundary_parameter_limit_fails_closed_before_transition_table():
    with pytest.raises(UIPTSamplingLimitError, match="boundary-parameter budget"):
        sample_uipt_neighborhood(
            radius=1,
            seed=0,
            max_boundary_parameter=0,
        )

def test_exact_categorical_draw_fails_closed_if_a_boundary_never_resolves():
    class RepeatingBoundaryBits:
        def getrandbits(self, bit_count):
            assert bit_count == 64
            return (1 << 64) // 3

    outcomes = (
        FreeTransition("new", None, Fraction(1, 3)),
        FreeTransition("empty", None, Fraction(2, 3)),
    )
    with pytest.raises(UIPTSamplingLimitError, match="categorical bit-refinement budget"):
        _draw_exact(RepeatingBoundaryBits(), outcomes)
