"""Deterministic S0 calibration tests; no random tree samples or held-out runs."""
import math

import numpy as np
import pytest

from emergence_lab.dimension_d1 import _from_edges, torus_lattice
from emergence_lab.spectral_dimension import (
    complete_graph_even_return,
    graph_even_returns,
    infinite_lattice_even_return,
    is_saturated,
    local_spectral_slope,
    torus_even_return_fourier,
)


def _graph(n, edges):
    u, v = zip(*edges)
    return _from_edges(n, np.array(u, dtype=np.int32), np.array(v, dtype=np.int32))


@pytest.mark.parametrize("graph", [
    torus_lattice(1, 8),  # even cycle; bipartite
    torus_lattice(1, 7),  # odd cycle; not bipartite
    torus_lattice(2, 6),
    _graph(5, [(0, 1), (0, 2), (0, 3), (0, 4)]),  # irregular star
    _graph(3, [(0, 1), (1, 2), (0, 2)]),  # triangle
    _graph(2, [(0, 1)]),  # bipartite K2
])
def test_s0_g0_reversible_kernel_vs_dense_powers(graph):
    degree = graph.degrees.astype(float)
    matrix = graph.csr().toarray() / degree[:, None]
    for source in range(graph.n):
        actual = graph_even_returns(graph, source, [1, 2, 4])
        for t in (1, 2, 4):
            direct = float(np.linalg.matrix_power(matrix, 2 * t)[source, source])
            assert abs(actual[t] - direct) <= 1e-12


def test_s0_g0_bipartite_parity_is_explicit():
    g = _graph(2, [(0, 1)])
    m = g.csr().toarray()
    assert (np.linalg.matrix_power(m, 2) == np.eye(2)).all()
    assert np.linalg.matrix_power(m, 3)[0, 0] == 0
    assert graph_even_returns(g, 0, [1, 2, 4]) == {1: 1.0, 2: 1.0, 4: 1.0}


@pytest.mark.parametrize("d,L", [(1, 7), (1, 8), (2, 6)])
def test_s0_g1_independent_fourier_matches_direct_matrix(d, L):
    graph = torus_lattice(d, L)
    actual = graph_even_returns(graph, 0, [1, 2, 4])
    for t in (1, 2, 4):
        assert abs(actual[t] - torus_even_return_fourier(d, L, t)) <= 1e-12


@pytest.mark.parametrize("d,L", [(1, 256), (2, 64)])
def test_s0_g1_lattice_asymptotic_control(d, L):
    for t in (32, 64, 128, 256):
        finite = torus_even_return_fourier(d, L, t)
        infinite = infinite_lattice_even_return(d, t)
        assert abs(finite / infinite - 1) <= 0.01
    for t in (32, 64, 128):
        ds = local_spectral_slope(torus_even_return_fourier(d, L, t),
                                  torus_even_return_fourier(d, L, 2 * t))
        assert abs(ds - d) <= 0.03


@pytest.mark.parametrize("d,L", [(1, 32), (2, 16)])
def test_s0_g2_bipartite_torus_is_saturated_not_zero_dimension(d, L):
    floor = 2.0 / L ** d  # even-time subsequence, bipartite torus
    q0 = torus_even_return_fourier(d, L, 4096)
    q1 = torus_even_return_fourier(d, L, 8192)
    assert abs(q0 / floor - 1) < 0.01
    assert abs(q1 / floor - 1) < 0.01
    assert is_saturated(q0, floor)
    assert abs(local_spectral_slope(q0, q1)) <= 0.02


def test_s0_g3_complete_graph_fast_mixing_null():
    n = 32
    q0 = complete_graph_even_return(n, 4)
    q1 = complete_graph_even_return(n, 8)
    floor = 1.0 / n  # K32 is nonbipartite
    assert abs(q0 / floor - 1) <= 0.01
    assert is_saturated(q0, floor)
    assert abs(local_spectral_slope(q0, q1)) <= 0.02


def test_star_root_weights_are_not_uniform_stationarity():
    g = _graph(5, [(0, 1), (0, 2), (0, 3), (0, 4)])
    # Every even step returns to center. A leaf returns with probability 1/4.
    assert graph_even_returns(g, 0, [1, 4])[4] == pytest.approx(1)
    assert graph_even_returns(g, 1, [1, 4])[4] == pytest.approx(.25)
    degree = g.degrees.astype(float)
    assert 2 * degree[0] / degree.sum() == 1
    assert 2 * degree[1] / degree.sum() == .25


def test_s0_g0_invalid_inputs_and_bounded_work():
    g = torus_lattice(1, 8)
    for times in ([], [0], [-1], [1.5]):
        with pytest.raises(ValueError):
            graph_even_returns(g, 0, times)
    with pytest.raises(ValueError):
        graph_even_returns(g, -1, [1])
    with pytest.raises(ValueError):
        graph_even_returns(g, 0, [4], max_transition_ops=2)
    with pytest.raises(ValueError):
        graph_even_returns(_graph(4, [(0, 1), (2, 3)]), 0, [1])
    with pytest.raises(ValueError):
        graph_even_returns(_from_edges(3, np.array([0]), np.array([1])), 0, [1])
    asymmetric = _graph(3, [(0, 1), (1, 2)])
    asymmetric.indices[asymmetric.indptr[2]] = 0  # corrupt source-2 neighbour (1 -> 0)
    with pytest.raises(ValueError):
        graph_even_returns(asymmetric, 0, [1])


def test_invalid_references_and_zero_probability_rejected():
    with pytest.raises(ValueError):
        torus_even_return_fourier(3, 10, 2)
    with pytest.raises(ValueError):
        torus_even_return_fourier(2, 2, 2)
    with pytest.raises(ValueError):
        infinite_lattice_even_return(3, 2)
    with pytest.raises(ValueError):
        complete_graph_even_return(2, 3)
    for first, second in [(0, 0.1), (0.2, -0.1), (math.nan, 0.2)]:
        with pytest.raises(ValueError):
            local_spectral_slope(first, second)
    with pytest.raises(ValueError):
        is_saturated(0.2, 0)


def test_s0_g4_numeric_output_byte_deterministic():
    # Exact deterministic arrays (no PRNG, no time field).
    g = torus_lattice(2, 6)
    a = np.array(list(graph_even_returns(g, 0, [1, 2, 4]).values()),
                 dtype=np.float64).tobytes()
    b = np.array(list(graph_even_returns(g, 0, [1, 2, 4]).values()),
                 dtype=np.float64).tobytes()
    assert a == b
