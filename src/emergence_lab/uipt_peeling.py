"""Exact local peeling sampler for the Type-II uniform infinite planar triangulation.

The sampler follows Angel (2003), Section 2, equations (2.3)-(2.4) and
Theorem 1.10. It returns a finite explored submap with one unfilled infinite
boundary, not a closed finite spherical triangulation.
"""
from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction
from threading import Lock
import random

import numpy as np

from emergence_lab.dimension_d1 import MultiGraph, _from_multiedges
from emergence_lab.spectral_dimension import MAX_TRANSITION_OPS, graph_even_returns


ALPHA = Fraction(27, 2)
_INF_DISTANCE = 10**18


@dataclass(frozen=True)
class UIPTTransition:
    """One exact Type-II UIPT peeling outcome."""

    kind: str
    index: int | None
    infinite_side: str | None
    probability: Fraction


@dataclass(frozen=True)
class FreeTransition:
    """One exact free Boltzmann polygon-filling outcome."""

    kind: str
    index: int | None
    probability: Fraction


@dataclass(frozen=True)
class UIPTSample:
    """A rooted local Type-II UIPT neighbourhood.

    The graph contains all exposed edges, including the current boundary.
    Vertices at distance less than radius are internal and have complete
    degree. The boundary vertices have distance at least radius.
    """

    graph: MultiGraph
    root: int
    root_edge: tuple[int, int]
    root_edge_dart: int
    radius: int
    seed: int
    distances: np.ndarray
    dart_origin: np.ndarray
    dart_target: np.ndarray
    dart_twin: np.ndarray
    face_cycles: tuple[tuple[int, ...], ...]
    face_kinds: tuple[str, ...]
    rotation_system: tuple[tuple[int, ...], ...]
    boundary_face_index: int
    boundary_vertices: tuple[int, ...]
    boundary_edges: tuple[tuple[int, int], ...]
    peel_steps: int
    free_fill_steps: int
    total_peel_steps: int
    vertices_added: int
    n_triangles: int
    stats: dict[str, int]

    @property
    def n_vertices(self) -> int:
        return self.graph.n

    @property
    def n_edges(self) -> int:
        return len(self.dart_origin) // 2

    @property
    def n_faces(self) -> int:
        return len(self.face_cycles)

    @property
    def complete_degree_radius(self) -> int:
        """Largest radius whose vertices are guaranteed to have full degree."""
        return self.radius - 1

    def ball_size(self, radius: int) -> int:
        """Return the complete graph-ball cardinality B(radius)."""
        radius = _checked_int(radius, "radius", minimum=0)
        if radius > self.radius:
            raise ValueError("ball radius exceeds the exposed neighbourhood radius")
        return int(np.count_nonzero(self.distances <= radius))

    def even_returns(
        self,
        half_times: Iterable[int],
        *,
        max_transition_ops: int = MAX_TRANSITION_OPS,
    ) -> dict[int, float]:
        """Return Q_t=P^(2t)(root,root) when all endpoint degrees are complete.

        The reversible half-kernel identity needs complete degrees for every
        endpoint within graph distance t. This sample guarantees that only
        when t < radius.
        """
        times = tuple(_checked_int(t, "half_time", minimum=1) for t in half_times)
        if not times:
            raise ValueError("half_times must be nonempty")
        if max(times) >= self.radius:
            raise ValueError(
                "local sample radius must be at least max(half_times)+1 "
                "for complete endpoint degrees"
            )
        return graph_even_returns(
            self.graph,
            self.root,
            times,
            max_transition_ops=max_transition_ops,
        )


def _checked_int(value: int, name: str, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"{name} must be an integer")
    result = int(value)
    if result < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return result


_PARTITION_LOCK = Lock()
_Z_VALUES = [Fraction(9, 8)]
_C_RATIO_VALUES = [Fraction(1)]


def _ensure_partition_values(max_m: int) -> tuple[list[Fraction], list[Fraction]]:
    """Extend exact Z_m and C_m/C_0 tables using rational recurrences."""
    with _PARTITION_LOCK:
        while len(_Z_VALUES) <= max_m:
            m = len(_Z_VALUES) - 1
            _Z_VALUES.append(
                _Z_VALUES[-1] * Fraction(9 * (2 * m + 1), 2 * (m + 3))
            )
            _C_RATIO_VALUES.append(
                _C_RATIO_VALUES[-1] * Fraction(9 * (2 * m + 3), 2 * (m + 1))
            )
    return _Z_VALUES, _C_RATIO_VALUES


def uipt_transition_probabilities(m: int) -> tuple[UIPTTransition, ...]:
    """Exact Type-II UIPT transition probabilities for boundary length m+2.

    T1 has boundary length i+1; T2 has boundary length m-i+2.
    """
    m = _checked_int(m, "m", minimum=0)
    z_values, c_values = _ensure_partition_values(m + 1)
    outcomes = [
        UIPTTransition(
            kind="new",
            index=None,
            infinite_side=None,
            probability=c_values[m + 1] / (ALPHA * c_values[m]),
        )
    ]
    if m:
        # Seed the two closure sequences at i=1, then advance by exact
        # rational ratios. This avoids recomputing large factorials per i.
        p_t1 = z_values[m - 1] / c_values[m]
        p_t2 = c_values[m - 1] * z_values[0] / c_values[m]
        for i in range(1, m + 1):
            outcomes.append(
                UIPTTransition(
                    kind="closure",
                    index=i,
                    infinite_side="T1",
                    probability=p_t1,
                )
            )
            outcomes.append(
                UIPTTransition(
                    kind="closure",
                    index=i,
                    infinite_side="T2",
                    probability=p_t2,
                )
            )
            if i < m:
                k = m - i
                p_t1 *= Fraction((k + 2) * (2 * i + 1), i * (2 * k - 1))
                p_t2 *= Fraction(k * (2 * i - 1), (2 * k + 1) * (i + 2))
    if sum(outcome.probability for outcome in outcomes) != 1:
        raise ArithmeticError("UIPT peeling probabilities do not sum exactly to one")
    return tuple(outcomes)


def free_transition_probabilities(m: int) -> tuple[FreeTransition, ...]:
    """Exact free Boltzmann triangulation probabilities for boundary m+2."""
    m = _checked_int(m, "m", minimum=0)
    z_values, _ = _ensure_partition_values(m + 1)
    p_new = z_values[m + 1] / (ALPHA * z_values[m])
    if m == 0:
        outcomes = (
            FreeTransition("new", None, p_new),
            FreeTransition("empty", None, 1 / z_values[0]),
        )
    else:
        split_prob = z_values[0] * z_values[m - 1] / z_values[m]
        outcome_list = [FreeTransition("new", None, p_new)]
        for i in range(1, m + 1):
            outcome_list.append(FreeTransition("split", i, split_prob))
            if i < m:
                k = m - i
                split_prob *= Fraction(
                    (2 * i - 1) * (k + 2),
                    (i + 2) * (2 * k - 1),
                )
        outcomes = tuple(outcome_list)
    if sum(outcome.probability for outcome in outcomes) != 1:
        raise ArithmeticError("free triangulation probabilities do not sum exactly to one")
    return outcomes


def _draw_exact(rng: random.Random, outcomes: tuple) -> object:
    """Draw an exact rational categorical outcome without a common-denominator LCM.

    A prefix of random bits defines a dyadic interval in [0, 1). If that
    interval straddles a cumulative-probability boundary, append more bits.
    The interval is eventually contained in one category almost surely.
    No floating-point conversion or potentially enormous LCM is required.
    """
    cumulative = [Fraction(0)]
    for outcome in outcomes:
        cumulative.append(cumulative[-1] + outcome.probability)
    if cumulative[-1] != 1:
        raise ArithmeticError("categorical probabilities do not sum exactly to one")

    bits = 0
    prefix = 0
    while True:
        prefix = (prefix << 64) | rng.getrandbits(64)
        bits += 64
        denominator = 1 << bits
        lower = Fraction(prefix, denominator)
        upper = Fraction(prefix + 1, denominator)
        lower_index = bisect_right(cumulative, lower) - 1
        upper_index = bisect_left(cumulative, upper) - 1
        if lower_index == upper_index:
            return outcomes[lower_index]


class _CombinatorialMap:
    """Mutable oriented combinatorial map with explicit darts and face cycles."""

    def __init__(
        self,
        *,
        max_vertices: int,
        max_total_peel_steps: int,
        max_boundary_parameter: int,
    ) -> None:
        self.max_vertices = max_vertices
        self.max_total_peel_steps = max_total_peel_steps
        self.max_boundary_parameter = max_boundary_parameter
        self.n_vertices = 0
        self.origin: list[int] = []
        self.target: list[int] = []
        self.twin: list[int] = []
        self.face_of: list[int] = []
        self.active: list[bool] = []
        self.adjacency: list[list[int]] = []
        self.distances: list[int] | None = None
        self.faces: dict[int, list[int]] = {}
        self.face_kind: dict[int, str] = {}
        self.next_face_id = 0
        self.total_peel_steps = 0
        self.uipt_peel_steps = 0
        self.free_fill_steps = 0
        self.triangles = 0
        self.stats = {
            "uipt_new_vertex_steps": 0,
            "uipt_T1_infinite_closures": 0,
            "uipt_T2_infinite_closures": 0,
            "free_new_vertex_steps": 0,
            "free_splits": 0,
            "free_empty_digon_closures": 0,
        }
        self.root = 0
        self.root_edge = (0, 1)
        self._init_root_triangle()

    def _new_vertex(self) -> int:
        if self.n_vertices >= self.max_vertices:
            raise UIPTSamplingLimitError("vertex budget exceeded; sample discarded")
        vertex = self.n_vertices
        self.n_vertices += 1
        self.adjacency.append([])
        if self.distances is not None:
            self.distances.append(_INF_DISTANCE)
        return vertex

    def _relax_edges(self, edges: tuple[tuple[int, int], ...]) -> None:
        if self.distances is None:
            return
        queue: deque[int] = deque()
        for u, v in edges:
            if self.distances[u] + 1 < self.distances[v]:
                self.distances[v] = self.distances[u] + 1
                queue.append(v)
            if self.distances[v] + 1 < self.distances[u]:
                self.distances[u] = self.distances[v] + 1
                queue.append(u)
        while queue:
            u = queue.popleft()
            next_distance = self.distances[u] + 1
            for v in self.adjacency[u]:
                if next_distance < self.distances[v]:
                    self.distances[v] = next_distance
                    queue.append(v)

    def _add_edge(self, u: int, v: int) -> tuple[int, int]:
        if u == v:
            raise ValueError("Type-II triangulations forbid self-loops")
        if not (0 <= u < self.n_vertices and 0 <= v < self.n_vertices):
            raise ValueError("edge endpoint is outside the vertex set")
        dart = len(self.origin)
        self.origin.extend((u, v))
        self.target.extend((v, u))
        self.twin.extend((dart + 1, dart))
        self.face_of.extend((-1, -1))
        self.active.extend((True, True))
        self.adjacency[u].append(v)
        self.adjacency[v].append(u)
        self._relax_edges(((u, v),))
        return dart, dart + 1

    def _set_face(self, face_id: int, cycle: list[int], kind: str) -> None:
        cycle = list(cycle)
        if len(cycle) < 2:
            raise ValueError("face cycle must contain at least two darts")
        self.faces[face_id] = cycle
        self.face_kind[face_id] = kind
        for dart in cycle:
            if not self.active[dart]:
                raise ValueError("inactive dart cannot belong to a face")
            self.face_of[dart] = face_id

    def _new_face(self, cycle: list[int], kind: str) -> int:
        face_id = self.next_face_id
        self.next_face_id += 1
        self._set_face(face_id, cycle, kind)
        return face_id

    def _remove_face(self, face_id: int) -> None:
        self.faces.pop(face_id)
        self.face_kind.pop(face_id)

    def _init_root_triangle(self) -> None:
        for _ in range(3):
            self._new_vertex()
        d01, d10 = self._add_edge(0, 1)
        d12, d21 = self._add_edge(1, 2)
        d20, d02 = self._add_edge(2, 0)
        self.root_edge_dart = d01
        self._new_face([d01, d12, d20], "triangle")
        self.triangles = 1
        self.boundary_face = self._new_face([d10, d02, d21], "boundary")
        self.distances = self._full_distances()

    def _count_step(self, kind: str) -> None:
        if self.total_peel_steps >= self.max_total_peel_steps:
            raise UIPTSamplingLimitError("total peeling-step budget exceeded; sample discarded")
        self.total_peel_steps += 1
        if kind == "uipt":
            self.uipt_peel_steps += 1
        else:
            self.free_fill_steps += 1

    def _add_triangle(
        self,
        face_id: int,
        third_index: int | None = None,
    ) -> int | tuple[int, int]:
        if self.face_kind.get(face_id) != "boundary":
            raise ValueError("triangles can only be peeled from a boundary face")
        cycle = self.faces[face_id]
        m = len(cycle) - 2
        if m < 0:
            raise ValueError("invalid boundary length")
        peeled_dart = cycle[-1]
        u = self.origin[peeled_dart]
        v = self.target[peeled_dart]

        if third_index is None:
            third_vertex = self._new_vertex()
        else:
            third_index = _checked_int(third_index, "third_index", minimum=1)
            if third_index > m:
                raise ValueError("closure index exceeds the current boundary")
            rest = cycle[:-1]
            third_vertex = self.target[rest[third_index - 1]]

        triangle_dart_1, boundary_dart_1 = self._add_edge(v, third_vertex)
        triangle_dart_2, boundary_dart_2 = self._add_edge(third_vertex, u)
        self._new_face(
            [peeled_dart, triangle_dart_1, triangle_dart_2],
            "triangle",
        )
        self.triangles += 1

        if third_index is None:
            self._set_face(
                face_id,
                cycle[:-1] + [boundary_dart_2, boundary_dart_1],
                "boundary",
            )
            return face_id

        rest = cycle[:-1]
        arc_t1 = rest[:third_index]
        arc_t2 = rest[third_index:]
        face_t1 = self._new_face(arc_t1 + [boundary_dart_1], "boundary")
        face_t2 = self._new_face(arc_t2 + [boundary_dart_2], "boundary")
        self._remove_face(face_id)
        return face_t1, face_t2

    def _close_empty_digon(self, face_id: int) -> None:
        if self.face_kind.get(face_id) != "boundary":
            raise ValueError("only a boundary digon can close")
        cycle = self.faces[face_id]
        if len(cycle) != 2:
            raise ValueError("empty free component must be a 2-gon")
        boundary_dart_0, boundary_dart_1 = cycle
        interior_dart_0 = self.twin[boundary_dart_0]
        interior_dart_1 = self.twin[boundary_dart_1]
        if interior_dart_0 == interior_dart_1:
            raise ValueError("digon boundary darts cannot share one twin")
        if not (self.active[interior_dart_0] and self.active[interior_dart_1]):
            raise ValueError("digon twins must be active")
        if (
            self.origin[interior_dart_0] != self.target[interior_dart_1]
            or self.target[interior_dart_0] != self.origin[interior_dart_1]
        ):
            raise ValueError("digon edges do not have opposite orientations")
        self.twin[interior_dart_0] = interior_dart_1
        self.twin[interior_dart_1] = interior_dart_0
        for dart in (boundary_dart_0, boundary_dart_1):
            self.active[dart] = False
            self.face_of[dart] = -1
        self._remove_face(face_id)

    def _fill_free_component(self, face_id: int, rng: random.Random) -> None:
        pending = [face_id]
        while pending:
            current_face = pending.pop()
            if current_face not in self.faces:
                continue
            m = len(self.faces[current_face]) - 2
            if m > self.max_boundary_parameter:
                raise UIPTSamplingLimitError(
                    "boundary-parameter budget exceeded; sample discarded"
                )
            self._count_step("free")
            outcome = _draw_exact(rng, free_transition_probabilities(m))
            if outcome.kind == "empty":
                self.stats["free_empty_digon_closures"] += 1
                self._close_empty_digon(current_face)
            elif outcome.kind == "new":
                self.stats["free_new_vertex_steps"] += 1
                self._add_triangle(current_face)
                pending.append(current_face)
            else:
                self.stats["free_splits"] += 1
                face_t1, face_t2 = self._add_triangle(current_face, outcome.index)
                pending.extend((face_t1, face_t2))

    def _active_edges(self) -> list[tuple[int, int]]:
        return [
            (self.origin[dart], self.target[dart])
            for dart, is_active in enumerate(self.active)
            if is_active and dart < self.twin[dart]
        ]

    def _full_distances(self) -> list[int]:
        adjacency = [[] for _ in range(self.n_vertices)]
        for u, v in self._active_edges():
            adjacency[u].append(v)
            adjacency[v].append(u)
        distances = [_INF_DISTANCE] * self.n_vertices
        distances[self.root] = 0
        queue: deque[int] = deque([self.root])
        while queue:
            u = queue.popleft()
            next_distance = distances[u] + 1
            for v in adjacency[u]:
                if next_distance < distances[v]:
                    distances[v] = next_distance
                    queue.append(v)
        if any(distance >= _INF_DISTANCE for distance in distances):
            raise ValueError("sampled combinatorial map is disconnected")
        return distances

    def _rotation_system(self) -> tuple[tuple[int, ...], ...]:
        previous = [-1] * len(self.origin)
        for cycle in self.faces.values():
            for index, dart in enumerate(cycle):
                previous[dart] = cycle[index - 1]
        active_darts = [
            dart for dart, is_active in enumerate(self.active) if is_active
        ]
        sigma = [-1] * len(self.origin)
        for dart in active_darts:
            previous_dart = previous[dart]
            if previous_dart < 0:
                raise ValueError("active dart is absent from every face cycle")
            sigma[dart] = self.twin[previous_dart]
        if {sigma[dart] for dart in active_darts} != set(active_darts):
            raise ValueError("rotation successor is not a permutation of active darts")

        outgoing = [[] for _ in range(self.n_vertices)]
        for dart in active_darts:
            outgoing[self.origin[dart]].append(dart)
        visited: set[int] = set()
        rotations = []
        for vertex, darts in enumerate(outgoing):
            if not darts:
                raise ValueError("combinatorial map contains an isolated vertex")
            start = min(darts)
            orbit = []
            dart = start
            while dart not in visited:
                if self.origin[dart] != vertex:
                    raise ValueError("rotation successor changed its origin vertex")
                orbit.append(dart)
                visited.add(dart)
                dart = sigma[dart]
            if dart != start or len(orbit) != len(darts):
                raise ValueError("darts at a vertex do not form one rotation cycle")
            rotations.append(tuple(orbit))
        if visited != set(active_darts):
            raise ValueError("rotation system omitted active darts")
        return tuple(rotations)

    def _validate(self, radius: int) -> None:
        seen_darts = []
        for face_id, cycle in self.faces.items():
            kind = self.face_kind[face_id]
            if kind == "triangle" and len(cycle) != 3:
                raise ValueError("interior face is not triangular")
            if kind == "boundary" and len(cycle) < 2:
                raise ValueError("boundary face has fewer than two edges")
            if kind not in {"triangle", "boundary"}:
                raise ValueError("unknown face kind")
            for index, dart in enumerate(cycle):
                if not self.active[dart] or self.face_of[dart] != face_id:
                    raise ValueError("face/dart ownership mismatch")
                next_dart = cycle[(index + 1) % len(cycle)]
                if self.target[dart] != self.origin[next_dart]:
                    raise ValueError("face cycle is not contiguous")
                seen_darts.append(dart)

        active_darts = [
            dart for dart, is_active in enumerate(self.active) if is_active
        ]
        if sorted(seen_darts) != active_darts:
            raise ValueError("active darts are not partitioned by face cycles")
        for dart in active_darts:
            twin = self.twin[dart]
            if not self.active[twin] or self.twin[twin] != dart:
                raise ValueError("twin relation is not an involution")
            if (
                self.origin[dart] != self.target[twin]
                or self.target[dart] != self.origin[twin]
            ):
                raise ValueError("twin darts have inconsistent endpoints")
            if self.origin[dart] == self.target[dart]:
                raise ValueError("self-loop found in Type-II map")
        if len(active_darts) % 2:
            raise ValueError("combinatorial map has an odd number of active darts")
        edge_count = len(active_darts) // 2
        if self.n_vertices - edge_count + len(self.faces) != 2:
            raise ValueError("Euler characteristic is not that of the sphere map")

        boundary_faces = [
            face_id for face_id, kind in self.face_kind.items() if kind == "boundary"
        ]
        if boundary_faces != [self.boundary_face]:
            raise ValueError("sample must finish with exactly one infinite boundary")
        boundary_cycle = self.faces[self.boundary_face]
        boundary_vertices = [self.origin[dart] for dart in boundary_cycle]
        if len(set(boundary_vertices)) != len(boundary_vertices):
            raise ValueError("infinite boundary repeats a vertex")
        if any(self.distances[vertex] < radius for vertex in boundary_vertices):
            raise ValueError("boundary contains a vertex inside the requested radius")
        if self.root_edge_dart not in active_darts:
            raise ValueError("root edge dart is inactive")
        if (
            self.origin[self.root_edge_dart] != self.root_edge[0]
            or self.target[self.root_edge_dart] != self.root_edge[1]
        ):
            raise ValueError("root-edge orientation changed")
        if self.distances != self._full_distances():
            raise ValueError("incremental distances disagree with a full BFS")
        if self.triangles != sum(kind == "triangle" for kind in self.face_kind.values()):
            raise ValueError("triangle counter disagrees with face inventory")
        self._rotation_system()

    def _compact_sample(self, radius: int, seed: int) -> UIPTSample:
        active_darts = [
            dart for dart, is_active in enumerate(self.active) if is_active
        ]
        dart_map = {old: new for new, old in enumerate(active_darts)}
        face_ids = sorted(self.faces)
        face_map = {old: new for new, old in enumerate(face_ids)}

        dart_origin = np.asarray(
            [self.origin[dart] for dart in active_darts], dtype=np.int32
        )
        dart_target = np.asarray(
            [self.target[dart] for dart in active_darts], dtype=np.int32
        )
        dart_twin = np.asarray(
            [dart_map[self.twin[dart]] for dart in active_darts], dtype=np.int32
        )
        face_cycles = tuple(
            tuple(dart_map[dart] for dart in self.faces[face_id])
            for face_id in face_ids
        )
        face_kinds = tuple(self.face_kind[face_id] for face_id in face_ids)
        rotation_system = tuple(
            tuple(dart_map[dart] for dart in rotation)
            for rotation in self._rotation_system()
        )
        boundary_face_index = face_map[self.boundary_face]
        boundary_cycle = face_cycles[boundary_face_index]
        boundary_vertices = tuple(int(dart_origin[dart]) for dart in boundary_cycle)
        boundary_edges = tuple(
            (int(dart_origin[dart]), int(dart_target[dart]))
            for dart in boundary_cycle
        )

        edge_darts = [
            dart for dart in range(len(active_darts)) if dart < dart_twin[dart]
        ]
        edge_u = np.asarray([dart_origin[dart] for dart in edge_darts], dtype=np.int32)
        edge_v = np.asarray([dart_target[dart] for dart in edge_darts], dtype=np.int32)
        graph = _from_multiedges(
            self.n_vertices,
            edge_u,
            edge_v,
            info={
                "family": "UIPT_type_II",
                "sampler": "Angel_2003_local_peeling",
                "root_law": "oriented_root_edge_tail",
                "seed": seed,
                "exposure_radius": radius,
                "boundary_faces": 1,
            },
        )

        distances = np.asarray(self.distances, dtype=np.int64)
        for array in (distances, dart_origin, dart_target, dart_twin):
            array.setflags(write=False)
        stats = dict(self.stats)
        return UIPTSample(
            graph=graph,
            root=self.root,
            root_edge=self.root_edge,
            root_edge_dart=dart_map[self.root_edge_dart],
            radius=radius,
            seed=seed,
            distances=distances,
            dart_origin=dart_origin,
            dart_target=dart_target,
            dart_twin=dart_twin,
            face_cycles=face_cycles,
            face_kinds=face_kinds,
            rotation_system=rotation_system,
            boundary_face_index=boundary_face_index,
            boundary_vertices=boundary_vertices,
            boundary_edges=boundary_edges,
            peel_steps=self.uipt_peel_steps,
            free_fill_steps=self.free_fill_steps,
            total_peel_steps=self.total_peel_steps,
            vertices_added=self.n_vertices - 3,
            n_triangles=self.triangles,
            stats=stats,
        )

    def sample(self, radius: int, seed: int) -> UIPTSample:
        rng = random.Random(seed)
        while True:
            cycle = self.faces[self.boundary_face]
            chosen = next(
                (
                    index
                    for index, dart in enumerate(cycle)
                    if (
                        self.distances[self.origin[dart]] < radius
                        or self.distances[self.target[dart]] < radius
                    )
                ),
                None,
            )
            if chosen is None:
                break

            m = len(cycle) - 2
            if m > self.max_boundary_parameter:
                raise UIPTSamplingLimitError(
                    "boundary-parameter budget exceeded; sample discarded"
                )
            self._count_step("uipt")
            rotated = cycle[chosen + 1 :] + cycle[: chosen + 1]
            self._set_face(self.boundary_face, rotated, "boundary")
            outcome = _draw_exact(rng, uipt_transition_probabilities(m))
            if outcome.kind == "new":
                self.stats["uipt_new_vertex_steps"] += 1
                self._add_triangle(self.boundary_face)
                continue

            face_t1, face_t2 = self._add_triangle(
                self.boundary_face,
                outcome.index,
            )
            if outcome.infinite_side == "T1":
                self.stats["uipt_T1_infinite_closures"] += 1
                self.boundary_face = face_t1
                finite_face = face_t2
            else:
                self.stats["uipt_T2_infinite_closures"] += 1
                self.boundary_face = face_t2
                finite_face = face_t1
            self._fill_free_component(finite_face, rng)

        self._validate(radius)
        return self._compact_sample(radius, seed)


class UIPTSamplingLimitError(RuntimeError):
    """Raised when a local sample exceeds an explicit resource cap."""


def sample_uipt_neighborhood(
    radius: int,
    seed: int,
    *,
    max_vertices: int = 20_000,
    max_total_peel_steps: int = 100_000,
    max_boundary_parameter: int = 5_000,
) -> UIPTSample:
    """Sample an exact local Type-II UIPT neighbourhood through graph radius.

    The root is the tail of the canonical oriented root edge. Parallel edges
    are retained as distinct darts and as MultiGraph half-edge multiplicities.
    The finite components cut off by peeling are filled independently from
    the exact free Boltzmann polygon law.

    Resource limits are fail-closed: exceeding any vertex, step or boundary
    parameter cap raises UIPTSamplingLimitError and returns no partial sample.
    """
    radius = _checked_int(radius, "radius", minimum=1)
    seed = _checked_int(seed, "seed", minimum=0)
    max_vertices = _checked_int(max_vertices, "max_vertices", minimum=3)
    max_total_peel_steps = _checked_int(
        max_total_peel_steps,
        "max_total_peel_steps",
        minimum=0,
    )
    max_boundary_parameter = _checked_int(
        max_boundary_parameter,
        "max_boundary_parameter",
        minimum=0,
    )
    if max_vertices > np.iinfo(np.int32).max:
        raise ValueError("max_vertices exceeds the supported int32 vertex range")
    state = _CombinatorialMap(
        max_vertices=max_vertices,
        max_total_peel_steps=max_total_peel_steps,
        max_boundary_parameter=max_boundary_parameter,
    )
    return state.sample(radius, seed)
