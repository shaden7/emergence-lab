import pytest
from emergence_lab.finite_size import chain, run_pilot


def test_independent_spins_exact_energy_and_reproducibility():
    a = chain(8, 2.269185, 0, 400, 1, 103, False)
    assert a == chain(8, 2.269185, 0, 400, 1, 103, False)
    assert a['energy_per_spin'] == 0
    assert 0.07 < a['abs_magnetization'] < 0.17
    assert abs(a['binder']) < 0.20
    assert 0 <= a['susceptibility_abs'] < 1


def test_checkerboard_means_near_exact4():
    r = [chain(4, 2.269185, 400, 1400, 5, 177+i) for i in range(6)]
    assert abs(sum(x['energy_per_spin'] for x in r)/len(r) + 1.56562403375) < 0.10
    assert abs(sum(x['abs_magnetization'] for x in r)/len(r) - 0.84386054623) < 0.07


def test_budget_and_even_size_guards():
    cfg = {"sizes":[4],"temperatures":[2.2],"repeats":4,"base_seed":42,"burn_sweeps":2,"sample_sweeps":20,"sample_every":1}
    assert run_pilot(cfg) == run_pilot(cfg)
    assert len(run_pilot(cfg)['records']) == 8
    with pytest.raises(ValueError):
        run_pilot({**cfg, "sizes": [8, 31]})
    with pytest.raises(ValueError):
        run_pilot({**cfg, "sample_sweeps": 100_000})
