"""Exact energy of the periodic M x N square-lattice Ising model (J = k_B = 1).

Kaufman's (1949) closed form for the torus partition function, in the notation
of Beale (Phys. Rev. Lett. 76, 78, 1996):

    Z = 1/2 (2 sinh 2K)^(MN/2) (Z1 + Z2 + Z3 + Z4),  K = 1/T,
    Z1 = prod_{r<N} 2 cosh(M g_{2r+1}/2),  Z2 = prod_{r<N} 2 sinh(M g_{2r+1}/2),
    Z3 = prod_{r<N} 2 cosh(M g_{2r}/2),    Z4 = prod_{r<N} 2 sinh(M g_{2r}/2),
    cosh g_l = cosh 2K coth 2K - cos(l pi / N)   (l >= 1),
    g_0 = 2K + ln tanh K                         (sign matters; g_0 < 0 below Tc).

The energy per spin is -(1/MN) d ln Z / dK, evaluated analytically in log space
(float64, signed log-sum-exp). This is a known exact result, not a new theorem;
the module is cross-checked in tests against brute-force 4x4 enumeration and an
independent transfer-matrix computation, which share no code with it.
"""
import math

import numpy as np

T_CRITICAL = 2.0 / math.log(1.0 + math.sqrt(2.0))


def _gammas(K: float, N: int):
    """g_l and dg_l/dK for l = 0 .. 2N-1."""
    s2, c2 = math.sinh(2 * K), math.cosh(2 * K)
    c = c2 * c2 / s2
    dc = 2 * c2 * (1 - 1 / (s2 * s2))
    g = np.empty(2 * N)
    dg = np.empty(2 * N)
    g[0] = 2 * K + math.log(math.tanh(K))
    dg[0] = 2 + 2 / s2
    l = np.arange(1, 2 * N)
    arg = c - np.cos(np.pi * l / N)
    g[1:] = np.arccosh(arg)
    dg[1:] = dc / np.sinh(g[1:])
    return g, dg


def _log2cosh(x):
    x = np.abs(x)
    return x + np.log1p(np.exp(-2 * x))


def _log_abs_2sinh(x):
    x = np.abs(x)
    return x + np.log1p(-np.exp(-2 * x))


def exact_energy_per_spin(temperature: float, rows: int, cols: int | None = None) -> dict:
    """Exact mean energy per spin and ln Z of the periodic rows x cols lattice."""
    cols = rows if cols is None else cols
    if (type(rows) is not int or type(cols) is not int or rows < 2 or cols < 2
            or not math.isfinite(temperature) or temperature <= 0):
        raise ValueError("integer sizes >= 2 and finite T > 0 required")
    M, N = rows, cols
    K = 1.0 / temperature
    g, dg = _gammas(K, N)
    odd, even = slice(1, None, 2), slice(0, None, 2)
    h = 0.5 * M * g
    dh = 0.5 * M * dg
    # Z1, Z2 (odd l): all g_l > 0.
    a1 = float(np.sum(_log2cosh(h[odd])))
    d1 = float(np.sum(np.tanh(h[odd]) * dh[odd]))
    a2 = float(np.sum(_log_abs_2sinh(h[odd])))
    d2 = float(np.sum(dh[odd] / np.tanh(h[odd])))
    # Z3 (even l): cosh is even in g_0.
    a3 = float(np.sum(_log2cosh(h[even])))
    d3 = float(np.sum(np.tanh(h[even]) * dh[even]))
    # Z4 = 2 sinh(h_0) * rest; rest has g_l > 0.  dZ4/dK handled without coth(h_0).
    rest_h, rest_dh = h[2::2], dh[2::2]
    a4_rest = float(np.sum(_log_abs_2sinh(rest_h)))
    d4_rest = float(np.sum(rest_dh / np.tanh(rest_h)))
    sinh0, cosh0 = math.sinh(h[0]), math.cosh(h[0])
    # Signed log-sum-exp of Z1 + Z2 + Z3 + Z4 (Z4 = 2 sinh0 e^{a4_rest}).
    ref = max(a1, a2, a3, a4_rest + math.log(2 * cosh0))
    total = (math.exp(a1 - ref) + math.exp(a2 - ref) + math.exp(a3 - ref)
             + 2 * sinh0 * math.exp(a4_rest - ref))
    if total <= 0:
        raise ArithmeticError("non-positive partition sum")
    log_sum = ref + math.log(total)
    dsum = (math.exp(a1 - log_sum) * d1 + math.exp(a2 - log_sum) * d2 + math.exp(a3 - log_sum) * d3
            + math.exp(a4_rest - log_sum) * (2 * sinh0 * d4_rest + 2 * cosh0 * dh[0]))
    n_sites = M * N
    log_z = math.log(0.5) + 0.5 * n_sites * math.log(2 * math.sinh(2 * K)) + log_sum
    dlogz_dk = n_sites / math.tanh(2 * K) + dsum
    return {"temperature": temperature, "rows": M, "cols": N,
            "log_partition_function": log_z,
            "energy_per_spin": -dlogz_dk / n_sites}


def transfer_matrix_energy_per_spin(temperature: float, rows: int, cols: int) -> dict:
    """Independent check: Z = Tr T^rows with 2^cols x 2^cols row transfer matrix."""
    if cols > 12 or rows < 2 or cols < 2:
        raise ValueError("transfer matrix limited to 2 <= cols <= 12")
    K = 1.0 / temperature
    states = ((np.arange(1 << cols)[:, None] >> np.arange(cols)) & 1) * 2 - 1
    intra = np.sum(states * np.roll(states, -1, axis=1), axis=1).astype(float)
    inter = states @ states.T
    bonds = inter + 0.5 * (intra[:, None] + intra[None, :])
    T = np.exp(K * bonds)
    dT = T * bonds
    lam, U = np.linalg.eigh(T)
    top = lam.max()
    w = (lam / top) ** (rows - 1)
    z_scaled = float(np.sum(w * lam / top))
    proj = np.einsum("ij,ik,kj->j", U, dT, U) / top
    dz_over_z = rows * float(np.sum(w * proj)) / z_scaled
    return {"log_partition_function": rows * math.log(top) + math.log(z_scaled),
            "energy_per_spin": -dz_over_z / (rows * cols)}
