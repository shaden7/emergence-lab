"""SE-audit v0.1 engineering/synthetic checks. Never draw audit seeds (2036101901)."""
import copy
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pytest

from emergence_lab import spectral_s1 as s1
from emergence_lab import spectral_se_audit as sa
from emergence_lab.dimension_d2 import CAY

OC_SCRIPT = Path("docs/experiments/se_audit_operating_characteristics.py")


def config():
    return json.loads(sa.CONFIG.read_text())


def tiny():
    d = sa.design(config(), engineering=True)
    d.update(total_cpu_s=600.)  # generous; avoids timing-dependent tests
    return d


def synthetic_records(d, tree_q):
    """tree_q: (n_trees, T) per-tree return curves; every source of tree i gets row i."""
    rows = []
    for job in sa.schedule(d):
        for v in range(d["sources"]):
            q = np.asarray(tree_q[job["i_rep"]], dtype=float).copy()
            res = s1.KilledBallResult(v, 1, 64, d["T"], 10, 18, q, np.zeros(d["T"]))
            rows.append(dict(job, n=d["N"], res=res))
    return rows


def curves(d, exponents, scales):
    t = np.arange(1, d["T"] + 1, dtype=float)
    return [s * .8 * t ** (-e / 2) for e, s in zip(exponents, scales)]


def iid_curves(d, rng, sd=.02):
    n = d["batches"] * d["per_batch"]
    return curves(d, .85 + sd * rng.standard_normal(n), np.exp(.05 * rng.standard_normal(n)))


# ------------------------------------------------------------------ frozen design / seeds
def test_frozen_design_and_threshold():
    d = sa.design(config())
    assert (d["N"], d["batches"], d["per_batch"], d["sources"]) == (16384, 16, 12, 32)
    assert d["window"] == [128, 1024] and d["T"] == 4096 and d["total_cpu_s"] == 6000
    assert d["r_crit"] == 1.313
    assert abs(sa.r_critical(16, 12) - 1.3128) < 1e-4  # sqrt F_.95(15, 176)


@pytest.mark.parametrize("change", [
    lambda c: c.update(N=65536), lambda c: c.update(batches=8),
    lambda c: c.update(trees_per_batch=24), lambda c: c.update(seed_base=2036101701),
    lambda c: c["statistic"].update(R_crit=1.291), lambda c: c["primary_window"].__setitem__(0, 64),
    lambda c: c["budget"].update(hard_stop_total_cpu_min=200),
    lambda c: c["budget"].update(host="Lightsail"), lambda c: c["kernel"].update(eta=1e-3)])
def test_config_drift_rejected(change):
    c = copy.deepcopy(config())
    change(c)
    with pytest.raises(ValueError):
        sa.design(c)


def test_schedule_seed_rule_and_fixed_batch_membership():
    plan = sa.schedule(sa.design(config()))
    assert len(plan) == 192
    assert [j["seed"] for j in plan] == [[2036101901, 0, 0, i] for i in range(192)]
    assert s1.FAMILY_ORDER.index(CAY) == 0
    for b in range(16):
        assert [j["i_rep"] for j in plan if j["batch"] == b] == list(range(12 * b, 12 * b + 12))


def test_seed_bases_disjoint():
    used = {s1.PILOT_SEED_BASE, s1.BOOTSTRAP_SEED, s1.TEST_SEED_BASE, s1.S1B_SEED_BASE,
            2036101101, 2036101797, 2036101798, 2036101799}
    assert s1.SE_AUDIT_SEED_BASE == 2036101901 and sa.ENGINEERING_SEED == 2036101997
    assert not {s1.SE_AUDIT_SEED_BASE, sa.ENGINEERING_SEED, 2036101991} & used


def test_audit_seeds_locked_before_any_rng_or_files(monkeypatch, tmp_path):
    """The env gate is required even with the activated flag; the flag is required even
    with the env gate. Neither path reaches the RNG or creates the output directory."""
    monkeypatch.setattr(s1, "_seed_seq", lambda *a: pytest.fail("audit RNG reached"))
    monkeypatch.delenv("SE_AUDIT_ALLOW_SEEDS", raising=False)
    cases = [(True, None), (True, "0"), (False, None), (False, "1")]
    for flag, env in cases:
        monkeypatch.setattr(s1, "SE_AUDIT_RUN_AUTHORIZED", flag)
        if env is None:
            monkeypatch.delenv("SE_AUDIT_ALLOW_SEEDS", raising=False)
        else:
            monkeypatch.setenv("SE_AUDIT_ALLOW_SEEDS", env)
        with pytest.raises(PermissionError, match="locked"):
            s1.build_instance(CAY, 8, 0, 0, 1, s1.SE_AUDIT_SEED_BASE)
        out = tmp_path / f"locked{flag}{env}"
        with pytest.raises(PermissionError, match="locked"):
            sa.run(sa.design(config()), out)
        with pytest.raises(PermissionError):
            sa._run(sa.design(config()), out, Path("."))
        with pytest.raises(PermissionError):
            sa.main(["--mode", "se_audit", "--output", str(out)])
        assert not out.exists()


def test_activated_full_mode_still_refused_outside_containment(monkeypatch, tmp_path):
    """Run authorization (flag True) + env gate: an uncontained host is refused by the
    cgroup/network/host-attestation preflight before mkdir, P0 or any RNG."""
    assert s1.SE_AUDIT_RUN_AUTHORIZED is True
    monkeypatch.setattr(s1, "_seed_seq", lambda *a: pytest.fail("audit RNG reached"))
    monkeypatch.setattr(s1, "run_p0", lambda *a: pytest.fail("controls reached"))
    monkeypatch.setenv("SE_AUDIT_ALLOW_SEEDS", "1")
    monkeypatch.delenv("S1B_HOST_CLASS", raising=False)
    out = tmp_path / "uncontained"
    with pytest.raises((PermissionError, OSError)):
        sa.run(sa.design(config()), out)
    assert not out.exists()


def test_contained_engineering_flag_requires_engineering_mode(tmp_path):
    with pytest.raises(SystemExit):
        sa.main(["--mode", "se_audit", "--contained-engineering", "--output", str(tmp_path / "x")])
    assert not (tmp_path / "x").exists()


def test_engineering_cannot_borrow_audit_seed():
    d = tiny()
    d["seed_base"] = s1.SE_AUDIT_SEED_BASE
    with pytest.raises(PermissionError):
        sa.authorize(d)
    d = tiny()
    d["seed_base"] = 2036101797
    with pytest.raises(ValueError):
        sa.authorize(d)


# ------------------------------------------------------------------ statistic and classification
def test_statistic_uses_ddof1_and_mean_of_squared_se():
    rng = np.random.default_rng(1)  # test-only stream, not a project seed
    times = [1, 2, 4, 8]
    B, m = 4, 5
    Q = np.exp(.3 * rng.standard_normal((B * m, 4))) * np.array([1., .5, .25, .1])
    st = sa.batch_statistic(Q, B, m, 1, 8, times)
    c = -2 / math.log(8)
    d_b, se_b = [], []
    for b in range(B):
        q = Q[m * b:m * b + m]
        lo, hi = q[:, 0], q[:, 3]
        d_b.append(c * (math.log(hi.mean()) - math.log(lo.mean())))
        psi = c * ((hi - hi.mean()) / hi.mean() - (lo - lo.mean()) / lo.mean())
        se_b.append(psi.std(ddof=1) / math.sqrt(m))
    d_b, se_b = np.array(d_b), np.array(se_b)
    assert np.allclose(st["d_b"], d_b) and np.allclose(st["se_b"], se_b)
    expected = d_b.std(ddof=1) / math.sqrt(np.mean(se_b ** 2))
    assert st["R"] == pytest.approx(expected, rel=1e-12)
    # The two denominators differ for these data, so the test discriminates them.
    assert abs(math.sqrt(np.mean(se_b ** 2)) - se_b.mean()) > 1e-6
    assert st["R"] != pytest.approx(d_b.std(ddof=0) / math.sqrt(np.mean(se_b ** 2)))


def test_statistic_matches_operating_characteristics_script():
    spec = importlib.util.spec_from_file_location("oc", OC_SCRIPT)
    oc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oc)
    rng = np.random.default_rng(2)
    qlo = np.exp(.12 * rng.standard_normal(192))
    qhi = 1e-3 * np.exp(.12 * rng.standard_normal(192))
    times = [128, 1024]
    st = sa.batch_statistic(np.column_stack([qlo, qhi]), 16, 12, 128, 1024, times)
    ref = [oc.batch_stats(qlo[12 * b:12 * b + 12], qhi[12 * b:12 * b + 12]) for b in range(16)]
    assert np.allclose(st["d_b"], [r[0] for r in ref]) and np.allclose(st["se_b"], [r[1] for r in ref])
    assert oc.analytic()["R_crit"] == pytest.approx(sa.r_critical(16, 12))


@pytest.mark.parametrize("r,expected", [(0., sa.NOT_REJECTED), (1.313, sa.NOT_REJECTED),
                                        (1.3131, sa.REJECTED), (5., sa.REJECTED),
                                        (float("nan"), sa.BLOCKED), (float("inf"), sa.BLOCKED),
                                        (-1., sa.BLOCKED)])
def test_classification_boundary(r, expected):
    assert sa.classify(r, 1.313) == expected


def test_batch_indexing_is_contiguous():
    # Batch 2 alone is shifted: only a contiguous 12b..12b+11 split sees it as one batch.
    B, m = 16, 12
    Q = np.ones((B * m, 2))
    Q[:, 1] = .1
    Q[24:36, 1] = .2
    Q[np.arange(B * m) % 2 == 0, 1] *= 1.01  # within-batch spread so SE_b > 0
    st = sa.batch_statistic(Q, B, m, 1, 2, [1, 2])
    assert np.argmin(st["d_b"]) == 2 and np.sum(st["d_b"] < st["d_b"][0] - .1) == 1


# ------------------------------------------------------------------ synthetic end-to-end analysis
def test_iid_synthetic_not_rejected_and_batch_effect_rejected():
    d = sa.design(config(), engineering=True)
    d.update(batches=16, per_batch=12, r_crit=1.313)
    rng = np.random.default_rng(3)
    out = sa.analyze(d, synthetic_records(d, iid_curves(d, rng)))
    assert out["verdict"] == sa.NOT_REJECTED, out.get("R")
    desc = out["descriptive"]
    assert desc["pooled_psi_sd_df"] == 176
    lo, hi = desc["pooled_psi_sd_ci90"]
    assert lo < desc["pooled_psi_sd"] < hi
    assert hi / desc["pooled_psi_sd"] == pytest.approx(1.0967, abs=1e-3)
    # Shared within-batch component (e.g. a seeding defect): SE ignores it, spread grows.
    n = 192
    batch_shift = np.repeat(.05 * rng.standard_normal(16), 12)
    bad = curves(d, .85 + .02 * rng.standard_normal(n) + batch_shift, np.ones(n))
    out = sa.analyze(d, synthetic_records(d, bad))
    assert out["verdict"] == sa.REJECTED and out["R"] > 2


@pytest.mark.parametrize("fault", ["missing_source", "over_cap", "uncertified", "nan",
                                   "duplicate_source", "missing_tree", "non_monotone"])
def test_no_dropping_incomplete_or_uncertified_trees(fault):
    d = tiny()
    rows = synthetic_records(d, iid_curves(d, np.random.default_rng(4)))
    target = [r for r in rows if r["i_rep"] == 5]
    if fault == "missing_source":
        rows.remove(target[0])
    elif fault == "over_cap":
        target[0]["res"].status = "OVER_CAP"
    elif fault == "uncertified":
        target[0]["res"].killed[-1] = 1.
    elif fault == "nan":
        target[0]["res"].q_lower[-1] = np.nan
    elif fault == "duplicate_source":
        target[1]["res"].source = target[0]["res"].source
    elif fault == "missing_tree":
        for r in target:
            rows.remove(r)
    elif fault == "non_monotone":
        target[0]["res"].q_lower[3] = 10.
    out = sa.analyze(d, rows)
    assert out["verdict"] == sa.BLOCKED and 5 in out["invalid_trees"] and "R" not in out


def test_controls_budget_and_stray_trees_block():
    d = tiny()
    rows = synthetic_records(d, iid_curves(d, np.random.default_rng(5)))
    assert sa.analyze(d, rows)["verdict"] in (sa.REJECTED, sa.NOT_REJECTED)
    assert sa.analyze(d, rows, controls_passed=False)["verdict"] == sa.BLOCKED
    assert sa.analyze(d, rows, budget_ok=False)["verdict"] == sa.BLOCKED
    extra = dict(rows[0], i_rep=99)
    assert sa.analyze(d, rows + [extra])["stray_trees"] == [99]


# ------------------------------------------------------------------ engineering pipeline
def test_engineering_pipeline_determinism_ledger_and_cpu_log(tmp_path):
    d = tiny()
    reps = [sa.run(d, tmp_path / name, controls=False) for name in ("a", "b")]
    for rep in reps:
        assert rep["result"]["verdict"] == sa.BLOCKED  # no controls -> never classified
        assert rep["result"]["blocked_reasons"] == ["controls"]
        assert not rep["s2_run_authorized"]
    assert (tmp_path / "a/numeric.csv").read_bytes() == (tmp_path / "b/numeric.csv").read_bytes()
    manifest = json.loads((tmp_path / "a/manifest.json").read_text())
    assert manifest["seed_tuples_attempted"] == [[sa.ENGINEERING_SEED, 0, 0, i] for i in range(12)]
    events = [json.loads(s) for s in (tmp_path / "a/attempts.jsonl").read_text().splitlines()]
    assert len(events) == 24 and all(e["status"] == "STARTED" for e in events[::2])
    assert all(e["status"] == "COMPLETED" and e["cpu_s"] >= 0 for e in events[1::2])
    assert [e["batch"] for e in events[1::2]] == [i // 3 for i in range(12)]
    with pytest.raises(FileExistsError):
        sa.run(d, tmp_path / "a", controls=False)


def test_engineering_records_classify_when_controls_treated_as_passed(tmp_path, monkeypatch):
    monkeypatch.setattr(s1, "run_p0", lambda root: {"pass": True, "stub": "test only"})
    rep = sa.run(tiny(), tmp_path / "eng")
    assert rep["controls_passed"] and rep["result"]["verdict"] in (sa.REJECTED, sa.NOT_REJECTED)
    assert math.isfinite(rep["result"]["R"]) and len(rep["result"]["d_b"]) == 4


def test_control_failure_precedes_generation(tmp_path, monkeypatch):
    monkeypatch.setattr(s1, "run_p0", lambda root: {"pass": False})
    monkeypatch.setattr(s1, "build_instance", lambda *a: pytest.fail("control STOP ignored"))
    rep = sa.run(tiny(), tmp_path / "stopped")
    assert rep["attempts"] == [] and rep["result"]["verdict"] == sa.BLOCKED


def test_first_failure_stops_and_is_never_replaced(tmp_path, monkeypatch):
    out = tmp_path / "failed"

    def fail(*args):
        first = json.loads((out / "attempts.jsonl").read_text().splitlines()[0])
        assert first["status"] == "STARTED"
        raise ValueError("synthetic generation failure")
    monkeypatch.setattr(s1, "build_instance", fail)
    rep = sa.run(tiny(), out, controls=False)
    assert len(rep["attempts"]) == 1 and rep["attempts"][0]["status"] == "FAILED"
    assert rep["result"]["verdict"] == sa.BLOCKED


def test_budget_overrun_blocks(tmp_path, monkeypatch):
    used = [0.]

    class Clock:
        def __init__(self, total): self.total = total
        @staticmethod
        def cpu(): return used[0]
        def used(self): return used[0]
        def exceeded(self): return used[0] >= self.total
    original = s1.certified_returns

    def compute(*a, **k):
        used[0] += 1
        return original(*a, **k)
    monkeypatch.setattr(sa, "Budget", Clock)
    monkeypatch.setattr(s1, "run_p0", lambda root: {"pass": True})
    monkeypatch.setattr(s1, "certified_returns", compute)
    d = tiny()
    d["total_cpu_s"] = 20  # 12 trees * 4 sources = 48 source units needed
    rep = sa.run(d, tmp_path / "budget")
    assert rep["budget_ok"] is False and rep["result"]["verdict"] == sa.BLOCKED
    assert len(rep["attempts"]) < 12
