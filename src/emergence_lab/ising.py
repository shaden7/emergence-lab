"""2D ferromagnetic Ising model, periodic boundaries, J=k_B=1."""
import numpy as np


def energy(spins: np.ndarray) -> float:
    """Total interaction energy; count right/down neighbors once."""
    return float(-np.sum(spins * (np.roll(spins, 1, axis=0) + np.roll(spins, 1, axis=1))))


def magnetization(spins: np.ndarray) -> float:
    return float(np.abs(np.mean(spins)))


def run_chain(size: int, temperature: float, burn_sweeps: int, sample_sweeps: int,
              seed: int, sample_every: int = 5) -> dict:
    if size < 4 or temperature <= 0 or burn_sweeps < 0 or sample_sweeps < 1 or sample_every < 1:
        raise ValueError("Invalid experiment parameters")
    rng = np.random.default_rng(seed)
    spins = rng.choice(np.array([-1, 1], dtype=np.int8), size=(size, size))
    n = size * size
    mags = []
    energies = []
    accepted = 0
    total = (burn_sweeps + sample_sweeps) * n
    for sweep in range(burn_sweeps + sample_sweeps):
        for _ in range(n):
            x = int(rng.integers(size)); y = int(rng.integers(size))
            s = int(spins[x, y])
            neighbors = (int(spins[(x - 1) % size, y]) + int(spins[(x + 1) % size, y])
                         + int(spins[x, (y - 1) % size]) + int(spins[x, (y + 1) % size]))
            delta_e = 2 * s * neighbors
            if delta_e <= 0 or rng.random() < np.exp(-delta_e / temperature):
                spins[x, y] = -s
                accepted += 1
        if sweep >= burn_sweeps and (sweep - burn_sweeps) % sample_every == 0:
            mags.append(magnetization(spins))
            energies.append(energy(spins) / n)
    return {
        "size": size, "temperature": temperature, "seed": seed,
        "burn_sweeps": burn_sweeps, "sample_sweeps": sample_sweeps,
        "sample_every": sample_every, "measurements": len(mags),
        "mean_abs_magnetization": float(np.mean(mags)),
        "mean_energy_per_spin": float(np.mean(energies)),
        "acceptance_rate": accepted / total,
    }
