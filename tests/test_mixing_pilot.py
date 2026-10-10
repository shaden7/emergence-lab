import pytest
from emergence_lab.mixing_pilot import run_chain, run_pilot, _block_tau
import numpy as np


def test_determinism_energy_range_and_ess():
    a = run_chain(8, 2.269185, 150, 3, 98, 'random')
    b = run_chain(8, 2.269185, 150, 3, 98, 'random')
    assert a == b
    assert len(a['raw_series']['energy']) == 50
    assert len(a['raw_series']['abs_magnetization']) == 50
    assert -2 <= a['observables']['energy']['last_mean'] <= 2
    assert 0 <= a['observables']['abs_magnetization']['last_mean'] <= 1
    assert _block_tau(np.ones(200),20) is None


def test_invalid_and_excessive_design():
    cfg={'sizes':[8],'temperatures':[2.269185],'repeats':8,'base_seed':1,'sample_sweeps':500,'sample_every':5}
    assert run_pilot(cfg)==run_pilot(cfg)
    with pytest.raises(ValueError):run_pilot({**cfg,'sizes':[31]})
    with pytest.raises(ValueError):run_pilot({**cfg,'sample_sweeps':100000})
    with pytest.raises(ValueError):run_pilot({**cfg,'repeats':99})
