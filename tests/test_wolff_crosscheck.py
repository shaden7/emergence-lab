import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from wolff_crosscheck import wolff_chain  # noqa: E402

# Exact 4x4 periodic references at T = 2.269185 (exhaustive enumeration, exact4.py).
E4, M4 = -1.56562403375, 0.84386054623


def test_wolff_is_deterministic():
    a = wolff_chain(8, 2.269185, 10, 50, 1, 7)
    b = wolff_chain(8, 2.269185, 10, 50, 1, 7)
    assert all(np.array_equal(x, y) for x, y in zip(a, b))


def test_wolff_matches_exact_4x4():
    e, m, _ = wolff_chain(4, 2.269185, 200, 6000, 1, 2029040099)
    assert abs(e.mean() / 16 - E4) < 0.02
    assert abs(np.abs(m).mean() / 16 - M4) < 0.01


def test_wolff_ordered_limit_and_null_cluster_rule():
    # Very low T: clusters span the lattice, |m| -> 1. Very high T: p_add -> 0, clusters are single sites.
    _, m, _ = wolff_chain(8, 0.5, 20, 50, 1, 3)
    assert np.all(np.abs(m) == 64)
    _, _, cs = wolff_chain(8, 1e6, 0, 200, 1, 4)
    assert np.all(cs == 1)
