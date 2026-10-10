import json
import sys

import pytest
from emergence_lab.cli import plan_seeded_experiments, main


def _config():
    return {
        "sizes": [4], "temperatures": [1.5, 2.269185, 3.5], "repeats": 2,
        "base_seed": 2026120101, "burn_sweeps": 10,
        "sample_sweeps": 20, "sample_every": 5,
    }


def test_legacy_exact4_seed_schedule_preserved():
    plan = plan_seeded_experiments(_config())
    assert len(plan) == 6
    assert plan[0] == (4, 1.5, 2026120101 + 400000 + 150000)
    assert plan[1][2] == plan[0][2] + 1


def test_rounding_and_size_cross_collisions_are_rejected():
    cfg = _config()
    cfg["temperatures"] = [2.269180, 2.269190]
    with pytest.raises(ValueError, match="collision"):
        plan_seeded_experiments(cfg)
    # 8-size vs 9-size differs by 100000, exactly 1.0 temperature has same offset.
    cfg["sizes"], cfg["temperatures"] = [8, 9], [2.0, 3.0]
    with pytest.raises(ValueError, match="collision"):
        plan_seeded_experiments(cfg)


def test_spin_proposals_guard_prevents_unbounded_work():
    cfg = _config()
    cfg.update(sizes=[32], temperatures=[2.269185], repeats=1,
               sample_sweeps=100001, burn_sweeps=0)
    with pytest.raises(ValueError, match="exceeds budget"):
        plan_seeded_experiments(cfg)
    with pytest.raises(ValueError, match="invalid"):
        plan_seeded_experiments({**_config(), "temperatures": [float("nan")]})
    with pytest.raises(ValueError, match="invalid"):
        plan_seeded_experiments({**_config(), "repeats": True})


def test_cli_fails_closed_before_creating_outputs(tmp_path, monkeypatch):
    cfg = _config()
    cfg["temperatures"] = [2.269180, 2.269190]
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(cfg))
    output = tmp_path / "results"
    monkeypatch.setattr(sys, "argv", ["emergence-lab", "--config", str(path), "--output", str(output)])
    with pytest.raises(ValueError, match="collision"):
        main()
    assert not output.exists()
