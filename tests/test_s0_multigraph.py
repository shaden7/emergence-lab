"""S0 checks for multiplicity-preserving, loop-free multigraphs."""
import numpy as np
import pytest

from emergence_lab.dimension_d1 import MultiGraph, _from_edges, _from_multiedges
from emergence_lab.spectral_dimension import graph_even_returns


def test_multigraph_builder_preserves_parallel_edges_and_degrees():
    graph = _from_multiedges(
        3,
        np.array([0, 0, 1], dtype=np.int32),
        np.array([1, 1, 2], dtype=np.int32),
    )
    assert isinstance(graph, MultiGraph)
    assert graph.degrees.tolist() == [2, 3, 1]
    assert graph.n_edges == 3
    assert graph.info["parallel_edge_copies_preserved"] == 1
    assert graph.info["duplicate_edges_removed"] == 0
    assert graph.csr().nnz == 6
    assert np.array_equal(
        graph.csr().toarray(),
        np.array([[0, 2, 0], [2, 0, 1], [0, 1, 0]], dtype=float),
    )


def test_multigraph_s0_returns_match_dense_matrix_powers_for_every_root():
    graph = _from_multiedges(
        3,
        np.array([0, 0, 1, 1, 2, 0], dtype=np.int32),
        np.array([1, 1, 2, 2, 0, 2], dtype=np.int32),
    )
    adjacency = graph.csr().toarray()
    transition = adjacency / graph.degrees[:, None]
    for source in range(graph.n):
        actual = graph_even_returns(graph, source, range(1, 5))
        for half_time, observed in actual.items():
            expected = float(np.linalg.matrix_power(transition, 2 * half_time)[source, source])
            assert observed == pytest.approx(expected, abs=1e-13)


def test_parallel_edges_change_the_walk_instead_of_being_deduplicated():
    u = np.array([0, 0, 1], dtype=np.int32)
    v = np.array([1, 1, 2], dtype=np.int32)
    multi = _from_multiedges(3, u, v)
    simple = _from_edges(3, u, v)
    assert graph_even_returns(multi, 0, [1])[1] == pytest.approx(2 / 3)
    assert graph_even_returns(simple, 0, [1])[1] == pytest.approx(1 / 2)


def test_s0_operation_budget_counts_parallel_half_edges():
    graph = _from_multiedges(
        3,
        np.array([0, 0, 1], dtype=np.int32),
        np.array([1, 1, 2], dtype=np.int32),
    )
    with pytest.raises(ValueError, match="budget"):
        graph_even_returns(graph, 0, [1], max_transition_ops=5)
    assert graph_even_returns(graph, 0, [1], max_transition_ops=6)[1] == pytest.approx(2 / 3)


def test_multigraph_builder_rejects_loops_and_invalid_endpoints():
    with pytest.raises(ValueError, match="self-loops"):
        _from_multiedges(2, np.array([0]), np.array([0]))
    with pytest.raises(ValueError, match="out of range"):
        _from_multiedges(2, np.array([0]), np.array([2]))
    with pytest.raises(ValueError, match="one-dimensional"):
        _from_multiedges(3, np.array([[0, 1]]), np.array([[1, 2]]))


def test_s0_rejects_asymmetric_parallel_edge_multiplicity():
    graph = MultiGraph(
        np.array([0, 2, 3, 4], dtype=np.int64),
        np.array([1, 1, 0, 1], dtype=np.int32),
    )
    with pytest.raises(ValueError, match="undirected"):
        graph_even_returns(graph, 0, [1])


def test_s0_rejects_self_loop_in_manually_constructed_multigraph():
    graph = MultiGraph(
        np.array([0, 2, 3], dtype=np.int64),
        np.array([0, 1, 0], dtype=np.int32),
    )
    with pytest.raises(ValueError, match="undirected"):
        graph_even_returns(graph, 0, [1])
