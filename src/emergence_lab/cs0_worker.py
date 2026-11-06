"""Trusted, no-fork CS0 row producer; not a study run authorization.

The launcher must validate a committed full-run authorization before calling
full mode, and must enforce resource/provenance limits. Engineering mode is a
small fixture on a fixed, disjoint development entropy. This module writes no
files, starts no processes, and evaluates no scientific PASS/FAIL gate.

The JSONL protocol is one ``type=metadata`` object followed by ``type=row``
objects. Row order is size, family/parameter, replicate; deterministic chain
and antichain each occur once per size. The fixed family indices below are
part of seed derivation, not dynamically assigned enumeration indices.
"""
from __future__ import annotations

import argparse
import json
import math
import platform
from pathlib import Path
from typing import Iterator

import numpy as np
import scipy
import emergence_lab

from emergence_lab import causal_set_mm as mm


ENGINEERING_ENTROPY = 2036110697
FAMILY_INDICES = {
    'diamond': 0, 'two_layer': 1, 'k_order': 2, 'chain': 3, 'antichain': 4,
}


def design(mode: str = 'full') -> dict:
    """Return the frozen grid without drawing any random numbers.

    Full mode contains 720 stochastic realizations and 8 exact controls.
    Engineering mode contains 36 stochastic fixtures and 4 exact controls;
    neither its size nor its replication supports CS0 gate conclusions.
    """
    if mode not in ('full', 'engineering'):
        raise ValueError('mode must be full or engineering')
    return {
        'mode': mode,
        'sizes': [128, 256, 512, 1024] if mode == 'full' else [8, 12],
        'replicates': 30 if mode == 'full' else 3,
        'diamond_dimensions': [2, 3, 4],
        'k_orders': [3, 4],
        'two_layer_p': 0.5,
        'family_indices': FAMILY_INDICES.copy(),
    }


def _validate_entropy(entropy: int, mode: str) -> None:
    design(mode)
    if type(entropy) is not int or entropy < 0:
        raise ValueError('entropy must be an explicit nonnegative integer')
    if mode == 'engineering' and entropy != ENGINEERING_ENTROPY:
        raise ValueError('engineering mode requires its fixed development entropy')


def _row(family: str, parameter: int, n: int, rep: int, entropy: int) -> dict:
    key = [FAMILY_INDICES[family], parameter, n, rep]
    # Exact controls retain their unambiguous identifiers but consume no RNG.
    if family == 'chain':
        prec = mm.chain(n)
    elif family == 'antichain':
        prec = mm.antichain(n)
    else:
        rng = np.random.default_rng(np.random.SeedSequence(entropy, spawn_key=key))
        if family == 'diamond':
            points = mm.sprinkle_diamond(n, parameter, rng)
            if (points.shape != (n, parameter) or not np.all(np.isfinite(points))
                    or not np.all(np.abs(points[:, 0])
                                  + np.sqrt(np.sum(points[:, 1:] ** 2, axis=1)) <= .5)):
                raise ValueError('sprinkled point outside the causal diamond')
            prec = mm.causal_matrix(points)
        elif family == 'two_layer':
            prec = mm.two_layer_order(n, .5, rng)
        elif family == 'k_order':
            prec = mm.random_k_order(n, parameter, rng)
        else:
            raise ValueError(f'unknown family {family}')
    if prec.shape != (n, n):
        raise ValueError('order shape differs from design')
    mm.check_partial_order(prec)
    result = mm.measure(prec)
    return {
        'family': family, 'D_or_k': parameter, 'N': n, 'rep': rep,
        'spawn_key': key, 'R': result.related_pairs, 'r': result.r,
        'd_mm': None if math.isnan(result.d_mm) else result.d_mm,
        'classification': result.classification,
    }


def generate_rows(entropy: int, mode: str = 'full') -> Iterator[dict]:
    """Yield checked rows; full entropy is supplied only by an authorized caller.

    Merely importing this module or inspecting ``design`` never constructs an
    RNG. Errors propagate without emitting a success or scientific gate verdict.
    """
    _validate_entropy(entropy, mode)
    grid = design(mode)
    for n in grid['sizes']:
        for dimension in grid['diamond_dimensions']:
            for rep in range(grid['replicates']):
                yield _row('diamond', dimension, n, rep, entropy)
        for rep in range(grid['replicates']):
            yield _row('two_layer', 0, n, rep, entropy)
        for k in grid['k_orders']:
            for rep in range(grid['replicates']):
                yield _row('k_order', k, n, rep, entropy)
        yield _row('chain', 0, n, 0, entropy)
        yield _row('antichain', 0, n, 0, entropy)


def metadata(entropy: int, mode: str) -> dict:
    _validate_entropy(entropy, mode)
    return {
        'type': 'metadata', 'schema': 1, 'mode': mode, 'design': design(mode),
        'entropy': entropy,
        'versions': {'python': platform.python_version(), 'numpy': np.__version__,
                     'scipy': scipy.__version__},
        'modules': {'package': str(Path(emergence_lab.__file__).resolve()),
                    'cs0_worker': str(Path(__file__).resolve()),
                    'causal_set_mm': str(Path(mm.__file__).resolve()),
                    'numpy': str(Path(np.__file__).resolve()),
                    'scipy': str(Path(scipy.__file__).resolve())},
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', required=True, choices=['full', 'engineering'])
    parser.add_argument('--entropy', required=True, type=int)
    args = parser.parse_args(argv)
    print(json.dumps(metadata(args.entropy, args.mode), allow_nan=False), flush=True)
    for row in generate_rows(args.entropy, args.mode):
        print(json.dumps({'type': 'row', **row}, allow_nan=False), flush=True)


if __name__ == '__main__':
    main()
