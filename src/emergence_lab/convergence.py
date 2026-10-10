"""Rank-normalized split-R-hat and Geyer effective sample sizes.

Implements the multi-chain diagnostics of Vehtari, Gelman, Simpson, Carpenter
and Buerkner, "Rank-normalization, folding, and localization: an improved
R-hat for assessing convergence of MCMC", Bayesian Analysis 16 (2021) 667-718:
bulk R-hat on rank-normalized split chains, tail R-hat on folded draws, and
ESS from the multi-chain autocorrelation with Geyer's initial positive/monotone
sequence truncation. These are diagnostics: passing them does not prove
convergence, and a mode never visited by any chain cannot be detected.

Convention: ``tau`` here is 1 + 2 sum rho_t (so ESS = n / tau); the older
``stats.autocorrelation_diagnostics`` reports tau_int = 1/2 + sum rho_t.
"""
from statistics import NormalDist

import numpy as np

_inv_cdf = np.vectorize(NormalDist().inv_cdf, otypes=[float])


def _check(chains) -> np.ndarray:
    a = np.asarray(chains, dtype=float)
    if a.ndim != 2 or a.shape[0] < 1 or a.shape[1] < 8 or not np.isfinite(a).all():
        raise ValueError("expected (chains, draws) array of finite values, >= 8 draws")
    return a


def split_chains(chains) -> np.ndarray:
    a = _check(chains)
    half = a.shape[1] // 2
    return np.concatenate((a[:, :half], a[:, a.shape[1] - half:]), axis=0)


def average_ranks(x) -> np.ndarray:
    flat = np.asarray(x, dtype=float).ravel()
    _, inverse, counts = np.unique(flat, return_inverse=True, return_counts=True)
    upper = np.cumsum(counts)
    avg = upper - (counts - 1) / 2.0
    return avg[inverse].reshape(np.shape(x))


def rank_normalize(chains) -> np.ndarray:
    a = np.asarray(chains, dtype=float)
    r = average_ranks(a)
    return _inv_cdf((r - 0.375) / (a.size + 0.25))


def _rhat(a: np.ndarray) -> float | None:
    n = a.shape[1]
    within = float(np.mean(np.var(a, axis=1, ddof=1)))
    if within <= 1e-300:
        return None
    between = float(n * np.var(a.mean(axis=1), ddof=1))
    return float(np.sqrt(((n - 1) / n * within + between / n) / within))


def rhat_bulk(chains) -> float | None:
    return _rhat(rank_normalize(split_chains(chains)))


def rhat_tail(chains) -> float | None:
    s = split_chains(chains)
    return _rhat(rank_normalize(np.abs(s - np.median(s))))


def rhat_rank(chains) -> float | None:
    """max(bulk, tail): the recommended single R-hat summary."""
    vals = [v for v in (rhat_bulk(chains), rhat_tail(chains)) if v is not None]
    return max(vals) if vals else None


def _autocov(x: np.ndarray) -> np.ndarray:
    """Biased (1/n) autocovariance of each row via FFT."""
    m, n = x.shape
    c = x - x.mean(axis=1, keepdims=True)
    size = 1 << int(np.ceil(np.log2(2 * n)))
    f = np.fft.rfft(c, size, axis=1)
    return np.fft.irfft(f * np.conj(f), size, axis=1)[:, :n] / n


def ess(chains) -> dict:
    """Multi-chain ESS (Geyer initial positive + monotone sequence)."""
    a = _check(chains)
    m, n = a.shape
    acov = _autocov(a)
    mean_var = float(np.mean(acov[:, 0])) * n / (n - 1)
    var_plus = mean_var * (n - 1) / n
    if m > 1:
        var_plus += float(np.var(a.mean(axis=1), ddof=1))
    if var_plus <= 1e-300:
        return {"ess": None, "tau": None, "max_lag": None}
    rho = np.zeros(n)
    rho[0] = 1.0
    even, odd = 1.0, 1.0 - (mean_var - float(np.mean(acov[:, 1]))) / var_plus
    rho[1] = odd
    t = 1
    while t < n - 3 and even + odd > 0:
        even = 1.0 - (mean_var - float(np.mean(acov[:, t + 1]))) / var_plus
        odd = 1.0 - (mean_var - float(np.mean(acov[:, t + 2]))) / var_plus
        if even + odd >= 0:
            rho[t + 1], rho[t + 2] = even, odd
        t += 2
    max_t = t - 2
    if even > 0:
        rho[max_t + 1] = even
    t = 1
    while t <= max_t - 2:
        if rho[t + 1] + rho[t + 2] > rho[t - 1] + rho[t]:
            rho[t + 1] = rho[t + 2] = (rho[t - 1] + rho[t]) / 2.0
        t += 2
    tau = -1.0 + 2.0 * float(np.sum(rho[:max_t + 1])) + float(rho[max_t + 1])
    tau = max(tau, 1.0 / np.log10(m * n))
    return {"ess": float(m * n / tau), "tau": float(tau), "max_lag": int(max_t)}


def ess_bulk(chains) -> float | None:
    return ess(rank_normalize(split_chains(chains)))["ess"]


def ess_tail(chains) -> float | None:
    s = split_chains(chains)
    out = []
    for q in (0.05, 0.95):
        ind = (s <= np.quantile(s, q)).astype(float)
        out.append(ess(ind)["ess"])
    return None if None in out else min(out)


def chain_ess(series) -> dict:
    """Single-chain Geyer ESS on the raw (not rank-normalized) series."""
    x = np.asarray(series, dtype=float)[None, :]
    return ess(x)
