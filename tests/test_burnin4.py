from emergence_lab.burnin4 import burnin_sensitivity

def test_determinism():
    cfg = dict(temperatures=[1.5], batches=2, chains_per_batch=4, base_seed=2099910000, sample_sweeps=30, sample_every=5, burn_sweeps_variants=[0, 10])
    assert burnin_sensitivity(cfg) == burnin_sensitivity(cfg)
