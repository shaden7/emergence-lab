import math
import pytest
from emergence_lab.ising_1d_control import exact_energy_per_spin,run_chain,run_pilot


def test_exact_energy_one_dimensional_limits():
    assert exact_energy_per_spin(32,1e9)==pytest.approx(0,abs=1e-8)
    assert exact_energy_per_spin(32,0.01)==pytest.approx(-1,abs=1e-7)
    t=2.269185
    assert exact_energy_per_spin(32,t)==pytest.approx(-math.tanh(1/t),abs=1e-8)


def test_simulator_determinism_and_analytic_energy():
    a=run_chain(8,2.269185,300,1000,5,42)
    assert a==run_chain(8,2.269185,300,1000,5,42)
    assert abs(a['energy_per_spin']-exact_energy_per_spin(8,2.269185))<0.15
    assert 0<=a['abs_magnetization']<=1


def test_config_guard():
    cfg=dict(sizes=[8],temperatures=[2.269185],repeats=4,base_seed=27,burn_sweeps=5,sample_sweeps=30,sample_every=5)
    assert len(run_pilot(cfg)['records'])==4
    with pytest.raises(ValueError):run_pilot({**cfg,'sizes':[31]})
    with pytest.raises(ValueError):run_pilot({**cfg,'sizes':[64],'sample_sweeps':999999})


def test_finite_one_dimensional_partition_formula_vs_bruteforce():
    import numpy as np
    size = 8
    states = 2 * ((np.arange(1 << size, dtype=np.uint32)[:, None] >> np.arange(size)) & 1).astype(int) - 1
    energies = -(states * np.roll(states, 1, axis=1)).sum(axis=1)
    for t in (1.5, 2.269185, 3.5):
        weights = np.exp(-(energies - energies.min())/t)
        enumeration = float(np.sum(weights*energies)/(size*np.sum(weights)))
        assert exact_energy_per_spin(size,t) == pytest.approx(enumeration, abs=1e-12)
