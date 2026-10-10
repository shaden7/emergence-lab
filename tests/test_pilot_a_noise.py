"""N5 frozen design tests (development references only; never evaluate holdout)."""
import hashlib
import json
import math
from pathlib import Path

import pytest

from emergence_lab import pilot_a_noise as n5

CFG = json.loads(Path("configs/pilot_a_n5.json").read_text())


def test_frozen_pins_and_analytic_null():
    n5.check_frozen_config(CFG)
    pins = n5.validate_protocol_files(CFG)
    assert pins["n5_prereg_git_blob_sha"] == n5.PREREG_BLOB_SHA
    assert n5.PREREG_COMMIT == "8686ae276e6cb4892c8410874136ae2baf31c93e"
    assert n5.gaussian_false_detection_probability(0, 1e-9) == 0
    assert n5.gaussian_false_detection_probability(1e-6, 1e-6) == pytest.approx(
        math.erfc(0.5), abs=1e-15)
    assert n5.gaussian_false_detection_probability(1e-4, 1e-9) > 0.99999
    assert n5.gaussian_false_detection_probability(1e-6, 1e-3) == 0
    assert n5.wilson95(0, 20)[0] == 0
    assert n5.wilson95(20, 20)[1] == 1


def test_modified_prereg_or_config_fails(tmp_path, monkeypatch):
    altered = dict(CFG)
    altered["replicates"] = 21
    with pytest.raises(ValueError, match="preregistered"):
        n5.check_frozen_config(altered)
    wrong = tmp_path / "prereg.md"
    wrong.write_text("changed")
    c2 = dict(CFG, preregistration=str(wrong))
    with pytest.raises(ValueError, match="preregistration changed"):
        n5.validate_protocol_files(c2)


def test_n5_analytic_controls_and_reproducibility():
    refs = n5.reference_values(CFG)
    for m in ("W", "CA"):
        assert refs[m][6] == 0
        assert n5.is_exterior_theorem_zero(m, 6, CFG)
    for m in ("H", "Q"):
        assert refs[m][6] > 0
        assert not n5.is_exterior_theorem_zero(m, 6, CFG)

    a = n5.run(CFG)
    b = n5.run(CFG)
    assert all(a["gates"].values()), a["gates"]
    assert a["gates"] == b["gates"]
    assert a["rows"] == b["rows"]
    assert a["trials"] == b["trials"]
    assert a["conditions"] == b["conditions"]
    assert len(a["rows"]) == 5040 and len(a["trials"]) == 720
    assert len({tuple(trial["seed"]) for trial in a["trials"]}) == 720
    assert {row["support_class"] for row in a["rows"] if row["model"] == "Q"} == {"nonstrict"}
    assert all(not row["false_positive"] for row in a["rows"] if row["sigma"] == 0)
    # N5 is a noise accounting stress, not a theorem based on noisy measurement.
    assert any(row["false_positive"] for row in a["rows"] if row["sigma"] == 1e-4
               and row["eta"] == 1e-9 and row["r"] == 6)
    for condition in a["conditions"]:
        assert sum(condition["front_histogram"].values()) == 20
        if condition["model"] in ("W", "CA"):
            k = condition["sentinel_false_detection"]
            lo, hi = condition["sentinel_wilson95"]
            assert lo <= k / 20 <= hi
            assert 0 <= condition["analytic_gaussian_null_p"] <= 1


def test_cli_writes_complete_replayable_artifacts(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_SHA", "n5-ci-test-revision")
    assert n5.main(["--output", str(tmp_path)]) == 0
    output = json.loads((tmp_path / "result.json").read_text())
    assert output["manifest"]["executing_commit"] == "n5-ci-test-revision"
    assert output["manifest"]["preregistration_commit"] == n5.PREREG_COMMIT
    assert output["manifest"]["rows_csv_sha256"] == hashlib.sha256(
        (tmp_path / "rows.csv").read_bytes()).hexdigest()
    assert sum(output["gates"].values()) == 6
    assert len((tmp_path / "rows.csv").read_text().splitlines()) == 5041
