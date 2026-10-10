import pytest

from emergence_lab.burnin4 import burnin_sensitivity

BASE = dict(temperatures=[1.5], batches=2, chains_per_batch=4, base_seed=2099910000,
            sample_sweeps=30, sample_every=5, burn_sweeps_variants=[0, 10])


def test_determinism():
    assert burnin_sensitivity(BASE) == burnin_sensitivity(BASE)


def test_paired_contrasts_align_and_are_internally_consistent():
    report = burnin_sensitivity({**BASE, "burn_sweeps_variants": [0, 10, 20]})
    contrasts = report["paired_contrasts"]
    # 2 non-baseline arms x 1 temperature x 2 batches x 2 observables
    assert len(contrasts) == 2 * 1 * 2 * 2
    for c in contrasts:
        # shift = variant mean - baseline mean = variant bias - baseline bias
        assert c["paired_mean_shift"] == pytest.approx(c["variant_bias"] - c["baseline_bias"], abs=1e-12)
    assert {c["burn_sweeps"] for c in contrasts} == {10, 20}


def test_every_arm_uses_the_shared_seed_schedule():
    # Each arm must equal a coverage run with the *same* base seed and that arm's
    # burn-in; this fails if arms silently draw fresh or offset seeds.
    from emergence_lab.coverage4 import run_coverage
    report = burnin_sensitivity(BASE)
    cfg = {k: v for k, v in BASE.items() if k != "burn_sweeps_variants"}
    for arm in report["arms"]:
        again = run_coverage({**cfg, "burn_sweeps": arm["burn_sweeps"]})["batches"]
        assert [r["mean"] for r in arm["batches"]] == [r["mean"] for r in again]


def test_caveat_reports_configured_batch_count():
    caveats = " ".join(burnin_sensitivity(BASE)["caveats"])
    assert "2 batches" in caveats


@pytest.mark.parametrize("variants", [[0], [0, 0], [0, -1], [0, 2001], [0, 1, 2, 3, 4], [0, 1.5]])
def test_rejects_invalid_burnin_variants(variants):
    with pytest.raises(ValueError):
        burnin_sensitivity({**BASE, "burn_sweeps_variants": variants})


def test_rejects_second_burnin_spec_and_excess_budget():
    with pytest.raises(ValueError):
        burnin_sensitivity({**BASE, "burn_sweeps": 5})
    with pytest.raises(ValueError):
        burnin_sensitivity({**BASE, "temperatures": [1.5, 2.0, 3.0], "batches": 21,
                            "burn_sweeps_variants": [0, 1]})  # 3*21*4*2 = 504 > 500
