"""No-seed S1b v0.2 decision tests for the design PR."""
import json
import math
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = runpy.run_path(str(ROOT / "docs/experiments/s1b_outcome_reference.py"))
classify_ci = REFERENCE["classify_ci"]
classify_family = REFERENCE["classify_family"]


@pytest.mark.parametrize(("lower", "upper", "expected"), [
    (0.010, 0.020, "EQUIVALENT"),  # sign-positive and equivalent, formerly overlapping
    (0.031, 0.050, "MATERIAL-POSITIVE"),
    (-0.060, -0.031, "MATERIAL-NEGATIVE"),
    (0.015, 0.045, "INCONCLUSIVE"),  # positive but not demonstrated > margin
    (0.030, 0.050, "INCONCLUSIVE"),  # touching margin
    (-0.050, -0.030, "INCONCLUSIVE"),
    (-0.030, 0.030, "INCONCLUSIVE"),
    (-0.029, 0.029, "EQUIVALENT"),
    (-0.070, -0.050, "MATERIAL-NEGATIVE"),
    (0.000, 0.060, "INCONCLUSIVE"),
])
def test_ci_cases_disjoint(lower, upper, expected):
    assert classify_ci(lower, upper) == expected


@pytest.mark.parametrize(("lower", "upper"), [
    (math.nan, 0.05), (0.0, math.inf), (0.03, 0.01),
])
def test_ci_invalid(lower, upper):
    with pytest.raises(ValueError):
        classify_ci(lower, upper)


def family(**overrides):
    settings = dict(
        counts=(24, 24, 24), expected_trees=24, expected_sizes=3, controls_passed=True,
        budget_ok=True, certified=True, headroom_ok=True,
        annealed_q_positive=True, ci=(0.035, 0.055),
        delta_se=0.015, jackknife_se=0.015,
        influence_skew=0.3, max_squared_share=0.2, margin=0.03,
    )
    settings.update(overrides)
    return classify_family(**settings)


def test_complete_valid_primary_is_material():
    assert family() == "MATERIAL-POSITIVE"


@pytest.mark.parametrize("changes", [
    {"counts": (24, 24, 23)},    # unused third size still mandatory
    {"counts": (24, 24)},         # missing a size is also incomplete
    {"controls_passed": False},
    {"budget_ok": False},
])
def test_partial_and_stops_always_block(changes):
    assert family(**changes) == "BLOCKED"


@pytest.mark.parametrize("changes", [
    {"certified": False}, {"headroom_ok": False},
    {"annealed_q_positive": False}, {"ci": (math.nan, 0.05)},
    {"delta_se": 0.0}, {"jackknife_se": 0.02},
    {"influence_skew": -1.51}, {"max_squared_share": 0.51},
])
def test_unreliable_screens_block_material_verdict(changes):
    assert family(**changes) == "UNRELIABLE"


def test_ust_complete_48_and_underpowered_is_classified_normally():
    assert family(counts=(48, 48), expected_trees=48, expected_sizes=2, ci=(-0.02, 0.02)) == "EQUIVALENT"
    assert family(counts=(47, 48), expected_trees=48, expected_sizes=2) == "BLOCKED"


def test_reference_thresholds_match_config():
    cfg = json.loads((ROOT / "configs/spectral_s1b.json").read_text())
    assert cfg["version"] == "0.2"
    assert cfg["outcomes"]["margin"] == 0.03
    assert cfg["outcomes"]["confidence_level"] == 0.90
    for family_name, values in cfg["families"].items():
        assert values["trees"] == cfg["outcomes"]["exact_trees_per_size"][family_name]
    reliability = cfg["outcomes"]["reliability"]
    assert reliability["max_abs_influence_skew"] == 1.5
    assert reliability["max_squared_influence_share"] == 0.5
    assert reliability["max_jackknife_to_delta_se_ratio"] == 1.25
    assert reliability["min_headroom_per_source"] == 10
    assert cfg["outcomes"]["full_samples_required"] is True
