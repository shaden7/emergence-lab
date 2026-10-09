import numpy as np
import pytest
from emergence_lab.ising import energy, magnetization, run_chain


def test_all_up_energy_periodic():
    assert energy(np.ones((8, 8), dtype=np.int8)) == -128.0


def test_checkerboard_energy():
    spins = np.fromfunction(lambda x, y: (-1) ** (x + y), (8, 8), dtype=int)
    assert energy(spins) == 128.0


def test_magnetization():
    spins = np.ones((4, 4), dtype=np.int8)
    spins[:2] = -1
    assert magnetization(spins) == 0


def test_deterministic_and_bounded():
    a = run_chain(8, 2.2, 10, 20, 17)
    b = run_chain(8, 2.2, 10, 20, 17)
    assert a == b
    assert 0 <= a["mean_abs_magnetization"] <= 1
    assert -2 <= a["mean_energy_per_spin"] <= 2
    assert 0 <= a["acceptance_rate"] <= 1


def test_reject_invalid():
    with pytest.raises(ValueError):
        run_chain(3, 0, 10, 10, 1)
