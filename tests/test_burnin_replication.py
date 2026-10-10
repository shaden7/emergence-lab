import json
from pathlib import Path

import numpy as np
import pytest

from emergence_lab import burnin_replication as br

CFG = Path(__file__).resolve().parents[1] / "configs" / "exact4_burnin_replication.json"


@pytest.mark.parametrize("t,df,p", [(1.0, 1, 0.5), (2.093024054, 19, 0.05), (2.860934606, 19, 0.01),
                                    (2.262157163, 9, 0.05), (1.959963985, 10**8, 0.05), (0.0, 5, 1.0)])
def test_t_pvalue_against_tables(t, df, p):
    assert br.t_two_sided_p(t, df) == pytest.approx(p, rel=1e-6, abs=1e-9)


def test_t_quantile():
    assert br.t_quantile_975(19) == pytest.approx(2.093024054, abs=1e-8)
    assert br.t_quantile_975(9) == pytest.approx(2.262157163, abs=1e-8)


def test_config_matches_preregistration_and_rejects_edits():
    cfg = json.loads(CFG.read_text())
    br.check_config(cfg)
    for key, bad in (("batches", 10), ("temperatures", [1.5]), ("burn_sweeps_variants", [0, 100]),
                     ("sample_sweeps", 400)):
        with pytest.raises(ValueError):
            br.check_config({**cfg, key: bad})


def _fake_report(effects: dict, n: int = 20, noise: float = 1e-4, seed: int = 0) -> dict:
    """Synthetic burnin_sensitivity-shaped report with chosen mean biases per (burn, T, obs)."""
    rng = np.random.default_rng(seed)
    temps, burns = [1.5, 2.269185], [0, 100, 1600]
    arms = []
    for b in burns:
        batches = [{"temperature": t, "batch": k, "observable": o, "reference": 0.0,
                    "mean": effects.get((b, t, o), 0.0) + noise * rng.standard_normal()}
                   for t in temps for k in range(n) for o in (br.E, br.M)]
        arms.append({"burn_sweeps": b, "batches": batches,
                     "aggregates": [{"temperature": t, "observable": o, "covered_batches": n, "batches": n,
                                     "wilson95_low": 0.8, "wilson95_high": 1.0} for t in temps for o in (br.E, br.M)]})
    contrasts = [{"burn_sweeps": arm["burn_sweeps"], "temperature": r1["temperature"], "observable": r1["observable"],
                  "paired_mean_shift": r1["mean"] - r0["mean"]}
                 for arm in arms[1:] for r0, r1 in zip(arms[0]["batches"], arm["batches"])]
    return {"config": {"temperatures": temps}, "arms": arms, "paired_contrasts": contrasts}


def test_decision_rules_replicate_and_null():
    original = {(0, 1.5, br.M): -0.0032, (0, 1.5, br.E): 0.0069, (0, 2.269185, br.E): 0.0113,
                (0, 2.269185, br.M): -0.0050, (1600, 1.5, br.E): 0.0033}
    out = {r["id"]: r["verdict"] for r in br.evaluate(_fake_report(original))["primary"]}
    assert out == {"P1": "replicated", "P2": "replicated", "P3": "replicated", "P4": "replicated",
                   "P5": "replicated", "P6": "replicated", "P7": "persists"}
    null = {r["id"]: r["verdict"] for r in br.evaluate(_fake_report({}))["primary"]}
    assert null["P7"] == "not replicated"
    assert all(null[k] == "not replicated" for k in ("P1", "P2", "P3", "P4", "P5", "P6"))


def test_wrong_sign_is_not_replication_and_wide_p7_is_inconclusive():
    flipped = {(0, 1.5, br.M): +0.0032}
    assert br.evaluate(_fake_report(flipped))["primary"][0]["verdict"] == "not replicated"
    noisy = br.evaluate(_fake_report({(1600, 1.5, br.E): 0.002}, noise=0.01))["primary"][6]
    assert noisy["verdict"] == "inconclusive"
