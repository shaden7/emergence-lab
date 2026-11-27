"""Bounded exact reference for causal-set spatial geometry (Issue #37).

This module implements the order-theoretic reference construction from
Eichhorn, Surya & Versteegen (2019), not a sprinkling generator or target
experiment.  It deliberately uses a dense strict-order matrix and is capped
at small fixtures; a scalable bitset/CSR implementation must be checked
against this oracle before use on target-sized antichains.
"""
from __future__ import annotations

import heapq
import math
from collections.abc import Iterable

import numpy as np

from .causal_set_mm import check_partial_order

MAX_REFERENCE_ELEMENTS = 256


def _validated_relation(prec: np.ndarray) -> np.ndarray:
    relation = np.asarray(prec)
    if relation.dtype != np.bool_:
        raise TypeError("prec must be a boolean strict-order matrix")
    if relation.ndim != 2 or relation.shape[0] != relation.shape[1]:
        raise ValueError("prec must be a square matrix")
    n = relation.shape[0]
    if n < 1:
        raise ValueError("causal set must contain at least one element")
    if n > MAX_REFERENCE_ELEMENTS:
        raise ValueError(
            f"exact reference is limited to N <= {MAX_REFERENCE_ELEMENTS}"
        )
    check_partial_order(relation)
    return relation


def _antichain_indices(
    relation: np.ndarray, antichain: Iterable[int] | None
) -> np.ndarray:
    n = relation.shape[0]
    if antichain is None:
        indices = np.flatnonzero(~np.any(relation, axis=0))
    else:
        try:
            raw = np.asarray(list(antichain))
        except TypeError as exc:
            raise ValueError("antichain must be a nonempty iterable of indices") from exc
        if (raw.ndim != 1 or raw.size == 0
                or not np.issubdtype(raw.dtype, np.integer)
                or np.issubdtype(raw.dtype, np.bool_)):
            raise ValueError("antichain must contain integer indices")
        indices = raw.astype(np.int64, copy=False)
        if np.any(indices < 0) or np.any(indices >= n):
            raise ValueError("antichain index out of range")
        if np.unique(indices).size != indices.size:
            raise ValueError("antichain indices must be unique")
        indices = np.sort(indices)

    if indices.size == 0:
        raise ValueError("causal set has no minimal elements")
    if np.any(relation[np.ix_(indices, indices)]):
        raise ValueError("selected elements are not an antichain")

    outside = np.setdiff1d(np.arange(n, dtype=np.int64), indices, assume_unique=True)
    if outside.size:
        future_of_a = np.any(relation[np.ix_(indices, outside)], axis=0)
        if not np.all(future_of_a):
            raise ValueError(
                "selected antichain is not initial: every outside element "
                "must be strictly to its future"
            )
    return indices


def minimal_antichain(prec: np.ndarray) -> np.ndarray:
    """Return all minimal elements, the paper's initial/past antichain.

    For a finite poset this is an inextendible antichain: every nonminimal
    element has a descending chain ending at a minimal element.  The returned
    indices are sorted only as stable labels; the construction is order-defined.
    """
    relation = _validated_relation(prec)
    return _antichain_indices(relation, None)


def validate_initial_antichain(
    prec: np.ndarray, antichain: Iterable[int]
) -> np.ndarray:
    """Validate an initial antichain: all other elements lie strictly to its future."""
    relation = _validated_relation(prec)
    return _antichain_indices(relation, antichain)


def suspended_volumes(
    prec: np.ndarray, antichain: Iterable[int] | None = None
) -> np.ndarray:
    """Return N(c)=|Fut(A) intersect Past(c)| for every element c.

    Fut and Past are the *exclusive* causal future/past.  Thus A and c are
    excluded from the count.  Values outside Fut(A) are zero.  Zero-volume
    common-future candidates are retained, not clipped: they can produce
    zero predistance on a sparse finite causal set and are a degeneracy to
    report, not a physical zero-dimensional regime.
    """
    relation = _validated_relation(prec)
    a = _antichain_indices(relation, antichain)
    future_of_a = np.any(relation[a, :], axis=0)
    return np.count_nonzero(relation[future_of_a, :], axis=0).astype(
        np.int64, copy=False
    )


def _zeta(spacetime_dimension: int) -> float:
    if (not isinstance(spacetime_dimension, (int, np.integer))
            or isinstance(spacetime_dimension, (bool, np.bool_))
            or spacetime_dimension < 2):
        raise ValueError("spacetime_dimension must be an integer >= 2")
    n = int(spacetime_dimension)
    return math.pi ** ((n - 1) / 2) / (n * math.gamma((n + 1) / 2))


def _predistance_matrix_validated(
    relation: np.ndarray, antichain: np.ndarray, spacetime_dimension: int
) -> np.ndarray:
    zeta = _zeta(spacetime_dimension)
    future_of_a = np.any(relation[antichain, :], axis=0)
    volumes = np.count_nonzero(relation[future_of_a, :], axis=0)

    m = antichain.size
    result = np.full((m, m), np.inf, dtype=np.float64)
    np.fill_diagonal(result, 0.0)
    exponent = 1.0 / int(spacetime_dimension)
    factor = 2.0 / (zeta ** exponent)
    for i in range(m):
        row = relation[antichain[i], :]
        for j in range(i + 1, m):
            common_future = row & relation[antichain[j], :]
            if not np.any(common_future):
                continue
            volume = int(np.min(volumes[common_future]))
            distance = factor * (volume ** exponent)
            result[i, j] = result[j, i] = distance
    return result


def predistance_matrix(
    prec: np.ndarray,
    antichain: Iterable[int] | None = None,
    *,
    spacetime_dimension: int = 3,
) -> np.ndarray:
    """Compute the symmetric minimum-common-future predistance on A.

    For distinct a,b, minimize the exclusive suspended volume
    |Fut(A) intersect Past(c)| over c in Fut(a) intersect Fut(b), then apply
    2 * (V/zeta_n)**(1/n).  A pair with no common future in the finite causal
    set is censored as +inf.  The diagonal is exactly zero.
    """
    relation = _validated_relation(prec)
    a = _antichain_indices(relation, antichain)
    return _predistance_matrix_validated(
        relation, a, spacetime_dimension
    )


def spatial_distance_matrix(
    prec: np.ndarray,
    antichain: Iterable[int] | None = None,
    *,
    meso_cutoff: float,
    spacetime_dimension: int = 3,
) -> np.ndarray:
    """Compute the full Eq. (31) path-minimized distance for small fixtures.

    Construct the undirected weighted graph whose edges have predistance
    strictly less than meso_cutoff, then run Dijkstra from each antichain
    element.  This is the unrestricted full-path reference, not the paper's
    SWB/SIL acceleration.  Unreachable pairs are +inf.  Zero predistances
    remain zero; they are not silently regularized.
    """
    if (isinstance(meso_cutoff, (bool, np.bool_))
            or not isinstance(meso_cutoff, (int, float, np.integer, np.floating))
            or not math.isfinite(float(meso_cutoff))
            or float(meso_cutoff) <= 0):
        raise ValueError("meso_cutoff must be a finite positive number")
    relation = _validated_relation(prec)
    a = _antichain_indices(relation, antichain)
    pred = _predistance_matrix_validated(
        relation, a, spacetime_dimension
    )
    m = a.size
    adjacency: list[list[tuple[int, float]]] = [[] for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            weight = float(pred[i, j])
            if math.isfinite(weight) and weight < float(meso_cutoff):
                adjacency[i].append((j, weight))
                adjacency[j].append((i, weight))

    result = np.full((m, m), np.inf, dtype=np.float64)
    np.fill_diagonal(result, 0.0)
    for source in range(m):
        distances = [math.inf] * m
        distances[source] = 0.0
        queue = [(0.0, source)]
        while queue:
            distance, vertex = heapq.heappop(queue)
            if distance != distances[vertex]:
                continue
            for neighbour, weight in adjacency[vertex]:
                candidate = distance + weight
                if candidate < distances[neighbour]:
                    distances[neighbour] = candidate
                    heapq.heappush(queue, (candidate, neighbour))
        for target in range(source + 1, m):
            result[source, target] = result[target, source] = distances[target]
    return result
