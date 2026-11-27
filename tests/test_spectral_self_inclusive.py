"""Exact deterministic controls for the self-inclusive disconnected walk kernel."""
import numpy as np
import pytest

from emergence_lab.dimension_d1 import Graph, MultiGraph, _from_edges, _from_multiedges
from emergence_lab.spectral_self_inclusive import SelfInclusiveKernel


def _graph(n, edges):
    if not edges:
        empty = np.array([], dtype=np.int32)
        return _from_edges(n, empty, empty)
    u, v = zip(*edges)
    return _from_edges(
        n, np.asarray(u, dtype=np.int32), np.asarray(v, dtype=np.int32)
    )


@pytest.mark.parametrize(
    "graph",
    [
        _graph(5, [(0, 1), (0, 2), (0, 3), (0, 4)]),
        _graph(6, [(0, 1), (1, 2), (3, 4)]),  # path, edge, isolated vertex
        _graph(1, []),  # one singleton component
        _graph(4, []),  # four singleton components
    ],
)
def test_self_inclusive_returns_match_dense_matrix_powers_for_every_root(graph):
    kernel = SelfInclusiveKernel(graph)
    adjacency = graph.csr().toarray()
    closed = adjacency + np.eye(graph.n)
    degree = closed.sum(axis=1)
    transition = closed / degree[:, None]

    for source in range(graph.n):
        actual = kernel.returns(source, [1, 2, 3, 4])
        for step, observed in actual.items():
            expected = float(
                np.linalg.matrix_power(transition, step)[source, source]
            )
            assert observed == pytest.approx(expected, abs=1e-13)


def test_self_inclusive_kernel_is_reversible_with_component_local_stationarity():
    graph = _graph(6, [(0, 1), (1, 2), (3, 4)])
    kernel = SelfInclusiveKernel(graph)
    adjacency = graph.csr().toarray()
    closed = adjacency + np.eye(graph.n)
    degree = closed.sum(axis=1)
    transition = closed / degree[:, None]

    # Detailed balance is checked without normalizing disconnected components
    # against one another; each component has its own stationary mass.
    flux = degree[:, None] * transition
    assert np.allclose(flux, flux.T, atol=0.0, rtol=0.0)
    assert kernel.n_components == 3
    assert kernel.stationary_floor(0) == pytest.approx(2 / 7)
    assert kernel.stationary_floor(1) == pytest.approx(3 / 7)
    assert kernel.stationary_floor(2) == pytest.approx(2 / 7)
    assert kernel.stationary_floor(3) == pytest.approx(1 / 2)
    assert kernel.stationary_floor(4) == pytest.approx(1 / 2)
    assert kernel.stationary_floor(5) == pytest.approx(1.0)


def test_singleton_is_trapped_with_return_and_stationary_floor_one():
    graph = _graph(3, [(0, 1)])
    kernel = SelfInclusiveKernel(graph)
    assert kernel.returns(2, [1, 2, 8]) == {
        1: 1.0, 2: 1.0, 8: 1.0
    }
    assert kernel.stationary_floor(2) == 1.0
    assert kernel.returns(0, [1])[1] == pytest.approx(0.5)


def test_disconnected_components_do_not_exchange_probability_mass():
    whole = _graph(5, [(0, 1), (1, 2), (3, 4)])
    component = _graph(3, [(0, 1), (1, 2)])
    q_whole = SelfInclusiveKernel(whole).returns(0, [1, 2, 4])
    q_component = SelfInclusiveKernel(component).returns(0, [1, 2, 4])
    assert q_whole == pytest.approx(q_component)


def test_input_graph_is_not_mutated_when_self_choices_are_added():
    graph = _graph(4, [(0, 1), (2, 3)])
    before = graph.csr().toarray().copy()
    SelfInclusiveKernel(graph)
    assert np.array_equal(graph.csr().toarray(), before)


def test_self_inclusive_operation_budget_counts_all_transition_entries():
    graph = _graph(4, [(0, 1), (2, 3)])
    kernel = SelfInclusiveKernel(graph)
    assert kernel.transition_nnz == 8
    with pytest.raises(ValueError, match="budget"):
        kernel.returns(0, [1], max_transition_ops=7)
    assert kernel.returns(0, [1], max_transition_ops=8)[1] == pytest.approx(0.5)


def test_self_inclusive_memory_estimate_is_checked_before_kernel_construction():
    graph = _graph(2, [(0, 1)])
    with pytest.raises(ValueError, match="memory"):
        SelfInclusiveKernel(graph, max_memory_bytes=1)


def test_self_inclusive_rejects_multigraph_and_malformed_adjacencies():
    multi = _from_multiedges(
        3, np.array([0, 0, 1], dtype=np.int32),
        np.array([1, 1, 2], dtype=np.int32),
    )
    with pytest.raises(TypeError, match="simple Graph"):
        SelfInclusiveKernel(multi)

    asymmetric = Graph(
        np.array([0, 1, 1], dtype=np.int64),
        np.array([1], dtype=np.int32),
    )
    with pytest.raises(ValueError, match="undirected"):
        SelfInclusiveKernel(asymmetric)

    looped = Graph(
        np.array([0, 1, 1], dtype=np.int64),
        np.array([0], dtype=np.int32),
    )
    with pytest.raises(ValueError, match="loop-free"):
        SelfInclusiveKernel(looped)

    duplicated = Graph(
        np.array([0, 2, 4], dtype=np.int64),
        np.array([1, 1, 0, 0], dtype=np.int32),
    )
    with pytest.raises(ValueError, match="simple and unweighted"):
        SelfInclusiveKernel(duplicated)


def test_self_inclusive_rejects_invalid_sources_times_and_budgets():
    kernel = SelfInclusiveKernel(_graph(3, [(0, 1)]))
    for source in (-1, 3, True, 1.5):
        with pytest.raises(ValueError, match="source"):
            kernel.returns(source, [1])
    for times in ([], [0], [-1], [1.5], [True]):
        with pytest.raises(ValueError, match="times"):
            kernel.returns(0, times)
    for budget in (-1, 1.5, True):
        with pytest.raises(ValueError, match="max_transition_ops"):
            kernel.returns(0, [1], max_transition_ops=budget)
