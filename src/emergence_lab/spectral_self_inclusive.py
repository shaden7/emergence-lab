"""Self-inclusive reversible walk kernel for spatial-neighbour graphs (Issue #37).

This is deliberately separate from the loop-free S0 kernel.  It accepts a
simple, undirected, unweighted Graph, adds exactly one self-choice per vertex,
and supports disconnected components (including isolated singleton vertices).
It is a deterministic finite-graph instrument; it does not generate causal sets
or authorize Issue #37 target measurements.
"""
from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from scipy.sparse.csgraph import connected_components

from emergence_lab.dimension_d1 import Graph, MultiGraph


MAX_TRANSITION_OPS = 100_000_000
MAX_KERNEL_MEMORY_BYTES = 512 * 1024 * 1024


class SelfInclusiveKernel:
    """Sparse reversible kernel with one self-choice and component-local floors.

    For a simple adjacency matrix A, the transition matrix is
    P = (A + I) D^{-1}, where D[v,v] = deg_A(v) + 1.  Each component is
    therefore aperiodic.  Its stationary law is proportional to the closed
    degree k_v = deg_A(v) + 1, and its source-specific return floor is
    k_source / sum_{x in C(source)} k_x.

    The memory guard is a conservative estimate for the graph copy, closed
    adjacency, transition CSR and O(n) work vectors.  It is not an OS-enforced
    RSS limit.  The operation guard counts transition nonzeros per half-step.
    """

    def __init__(
        self,
        graph: Graph,
        *,
        max_memory_bytes: int = MAX_KERNEL_MEMORY_BYTES,
    ) -> None:
        if not isinstance(graph, Graph) or isinstance(graph, MultiGraph):
            raise TypeError("self-inclusive spatial kernel requires a simple Graph, not MultiGraph")
        if graph.n < 1:
            raise ValueError("graph must contain at least one vertex")
        if (not isinstance(max_memory_bytes, (int, np.integer))
                or isinstance(max_memory_bytes, (bool, np.bool_))
                or max_memory_bytes < 1):
            raise ValueError("max_memory_bytes must be a positive integer")

        base = graph.csr()
        n = graph.n
        if base.shape != (n, n):
            raise ValueError("graph adjacency must be square and match graph.n")

        # Check the estimated peak before making the working CSR copies.
        base_bytes = int(base.data.nbytes + base.indices.nbytes + base.indptr.nbytes)
        closed_nnz_upper = int(base.nnz + n)
        index_bytes = max(base.indices.dtype.itemsize, np.dtype(np.int32).itemsize)
        indptr_bytes = max(base.indptr.dtype.itemsize, np.dtype(np.int32).itemsize)
        closed_csr_bytes = (
            closed_nnz_upper * (np.dtype(np.float64).itemsize + index_bytes)
            + (n + 1) * indptr_bytes
        )
        vector_bytes = n * (6 * np.dtype(np.float64).itemsize + 2 * index_bytes)
        vector_bytes += (n + 1) * indptr_bytes
        estimated_peak_bytes = base_bytes + 2 * closed_csr_bytes + vector_bytes
        if estimated_peak_bytes > int(max_memory_bytes):
            raise ValueError("estimated kernel memory budget exceeded")

        adjacency = base.copy().tocsr()
        adjacency.sum_duplicates()
        adjacency.eliminate_zeros()
        adjacency.sort_indices()
        adjacency.check_format(full_check=True)

        if adjacency.diagonal().any():
            raise ValueError("input adjacency must be loop-free; the kernel adds one self-choice")
        if (adjacency != adjacency.T).nnz:
            raise ValueError("input adjacency must be undirected")
        if (not np.all(np.isfinite(adjacency.data))
                or np.any(adjacency.data != 1.0)):
            raise ValueError("input adjacency must be simple and unweighted")

        degree = np.diff(adjacency.indptr).astype(np.float64) + 1.0
        n_components, labels = connected_components(
            adjacency, directed=False, return_labels=True
        )
        component_mass = np.bincount(
            labels, weights=degree, minlength=n_components
        ).astype(np.float64, copy=False)

        # The input diagonal was checked above, so setdiag adds exactly one
        # self-choice to every vertex, including isolated singleton vertices.
        adjacency.setdiag(1.0)
        adjacency.sum_duplicates()
        adjacency.sort_indices()
        inverse_degree = 1.0 / degree
        transition = adjacency.multiply(inverse_degree[:, None]).tocsr()
        transition.sum_duplicates()
        transition.sort_indices()

        self._n = n
        self._transition = transition
        self._degree = degree
        self._inverse_degree = inverse_degree
        self._component_labels = labels
        self._component_mass = component_mass
        self._estimated_peak_bytes = int(estimated_peak_bytes)

    @property
    def n_components(self) -> int:
        """Number of connected components in the input graph."""
        return int(self._component_mass.size)

    @property
    def transition_nnz(self) -> int:
        """Number of nonzero transition entries, including one self-choice per vertex."""
        return int(self._transition.nnz)

    @property
    def estimated_peak_bytes(self) -> int:
        """Conservative CSR/work-vector memory estimate; not measured RSS."""
        return self._estimated_peak_bytes

    def _source(self, source: int) -> int:
        if (not isinstance(source, (int, np.integer))
                or isinstance(source, (bool, np.bool_))
                or not 0 <= source < self._n):
            raise ValueError("invalid source vertex")
        return int(source)

    def stationary_floor(self, source: int) -> float:
        """Return the aperiodic stationary return floor in source's component."""
        v = self._source(source)
        component = int(self._component_labels[v])
        return float(self._degree[v] / self._component_mass[component])

    def even_returns(
        self,
        source: int,
        half_times: Iterable[int],
        *,
        max_transition_ops: int = MAX_TRANSITION_OPS,
    ) -> dict[int, float]:
        """Return P^(2t)[source,source] using the reversible half-kernel identity."""
        v = self._source(source)
        times = list(half_times)
        if not times or any(
            not isinstance(t, (int, np.integer))
            or isinstance(t, (bool, np.bool_))
            or t < 1
            for t in times
        ):
            raise ValueError("half_times must be nonempty positive integers")
        if (not isinstance(max_transition_ops, (int, np.integer))
                or isinstance(max_transition_ops, (bool, np.bool_))
                or max_transition_ops < 0):
            raise ValueError("max_transition_ops must be a nonnegative integer")

        requested = {int(t) for t in times}
        max_t = max(requested)
        if max_t * self._transition.nnz > int(max_transition_ops):
            raise ValueError("transition operation budget exceeded")

        row = np.zeros(self._n, dtype=np.float64)
        row[v] = 1.0
        result: dict[int, float] = {}
        for t in range(1, max_t + 1):
            row = np.asarray(row @ self._transition).ravel()
            if t in requested:
                # Detailed balance: P^(2t)_vv = k_v sum_x P^t_vx^2 / k_x.
                q = float(
                    self._degree[v]
                    * np.dot(row * row, self._inverse_degree)
                )
                if not (np.isfinite(q) and 0.0 < q <= 1.0 + 1e-10):
                    raise ArithmeticError("invalid return probability")
                result[t] = q
        return result
