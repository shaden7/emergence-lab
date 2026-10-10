import pytest
from emergence_lab.equilibration4 import trace, run, sample_exact_state, observables
import numpy as np


def test_stationary_draw_support_and_control_means():
    rng=np.random.default_rng(402)
    samples=[observables(sample_exact_state(rng,2.269185)) for _ in range(300)]
    assert abs(np.mean([x['energy_per_spin'] for x in samples]) + 1.56562403375) < 0.12
    assert abs(np.mean([x['abs_magnetization'] for x in samples]) - 0.84386054623) < 0.07


def test_zero_sweep_starts_and_determinism():
    p=[0,5,20]
    a=trace(1.5,p,313,'ordered')
    assert a==trace(1.5,p,313,'ordered')
    assert a[0]['energy_per_spin']==-2
    assert a[0]['abs_magnetization']==1
    assert trace(2.269185,p,314,'random') != trace(2.269185,p,315,'random')


def test_budget_checks_and_numerics():
    cfg=dict(temperatures=[2.269185],probes=[0,2,10],repeats=4,base_seed=17)
    r=run(cfg)
    assert len(r['raw'])==3*4*3
    assert len(r['summary'])==3*3
    with pytest.raises(ValueError):run({**cfg,'probes':[0,10000,30000]})
    with pytest.raises(ValueError):run({**cfg,'temperatures':[2.2,2.2]})
