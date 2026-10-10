import math

import pytest

from emergence_lab.exact4 import exact_observables
from emergence_lab.exact_finite import (T_CRITICAL, exact_energy_per_spin,
                                        transfer_matrix_energy_per_spin)


@pytest.mark.parametrize("temperature", [1.0, 1.5, 2.269185, T_CRITICAL, 3.5, 5.0])
def test_kaufman_matches_bruteforce_4x4_enumeration(temperature):
    exact = exact_energy_per_spin(temperature, 4)["energy_per_spin"]
    brute = exact_observables(temperature)["mean_energy_per_spin"]
    assert abs(exact - brute) < 1e-11


@pytest.mark.parametrize("rows,cols", [(6, 6), (8, 8), (6, 8), (8, 6), (5, 7), (7, 4), (32, 10)])
@pytest.mark.parametrize("temperature", [1.8, 2.269185, T_CRITICAL, 3.0])
def test_kaufman_matches_independent_transfer_matrix(rows, cols, temperature):
    k = exact_energy_per_spin(temperature, rows, cols)
    t = transfer_matrix_energy_per_spin(temperature, rows, cols)
    assert abs(k["energy_per_spin"] - t["energy_per_spin"]) < 1e-10
    assert abs(k["log_partition_function"] - t["log_partition_function"]) < 1e-9


def test_rows_cols_symmetry_of_asymmetric_formula():
    # Kaufman's expression is not manifestly symmetric in (M, N); Z must be.
    for temperature in (2.0, 2.269185, 2.6):
        a = exact_energy_per_spin(temperature, 32, 12)
        b = exact_energy_per_spin(temperature, 12, 32)
        assert abs(a["energy_per_spin"] - b["energy_per_spin"]) < 1e-11


def test_registered_l32_reference_and_thermodynamic_limit():
    e32 = exact_energy_per_spin(2.269185, 32)["energy_per_spin"]
    assert abs(e32 - (-1.4336590464244536)) < 1e-12
    # Known infinite-lattice value at Tc is -sqrt(2); finite-L values approach it.
    gaps = [exact_energy_per_spin(T_CRITICAL, L)["energy_per_spin"] + math.sqrt(2) for L in (32, 128, 512)]
    assert gaps[0] < gaps[1] < gaps[2] < 0
    assert abs(gaps[2]) < 2e-3


def test_limits_and_invalid_input():
    assert abs(exact_energy_per_spin(0.2, 16)["energy_per_spin"] + 2.0) < 1e-9
    assert abs(exact_energy_per_spin(500.0, 16)["energy_per_spin"]) < 1e-2
    for bad in ((0.0, 4), (float("nan"), 4), (2.0, 1)):
        with pytest.raises(ValueError):
            exact_energy_per_spin(*bad)
