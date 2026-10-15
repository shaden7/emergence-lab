"""S1 pilot orchestration tests (engineering seeds only; the pilot base is never drawn)."""
import copy
import json
import math

import numpy as np
import pytest
from scipy import stats

from emergence_lab import spectral_s1 as s1
from emergence_lab import spectral_s1_pilot as sp
from emergence_lab.dimension_d2 import CAY, RRT, UST
from emergence_lab.spectral_dimension import graph_even_returns


@pytest.fixture(scope="module")
def cfg():
    return json.loads(open("configs/spectral_s1_pilot.json").read())


def tiny(cfg, **kw):
    d = sp.engineering_design(cfg)
    d["families"] = {CAY: {"sizes": [256, 512], "trees": 8, "sources": 4},
                     UST: {"sizes": [16, 24], "trees": 8, "sources": 4},
                     RRT: {"sizes": [256], "trees": 2, "sources": 4}}
    d["T_ladder"] = [32, 16, 8]
    d["n_boot"] = 64
    d.update(kw)
    return d


def test_pilot_design_matches_frozen_config(cfg):
    d = sp.pilot_design(cfg)
    assert d["mode"] == "pilot" and d["seed_base"] == s1.PILOT_SEED_BASE == 2036101301
    assert d["families"][CAY] == {"sizes": [65536, 262144], "trees": 8, "sources": 32}
    assert d["families"][UST] == {"sizes": [128, 256], "trees": 8, "sources": 32}
    assert d["families"][RRT] == {"sizes": [65536], "trees": 4, "sources": 32}
    assert d["T_ladder"] == [4096, 2048, 1024]
    assert d["ladder_trigger_cpu_s"] == 45 * 60 and d["total_cpu_s"] == 120 * 60
    assert d["s2_budget_cpu_s"] == 180 * 60 and d["s2_sources"] == 32
    assert d["max_memory_bytes"] == 2 * 1024 ** 3 and d["hard_stop_factor"] == 1.5
    assert (d["go_full"], d["go_reduced"], d["margin"], d["level"]) == (0.03, 0.05, 0.03, 0.9)
    assert d["n_boot"] == 4096 and d["bootstrap_seed"] == 2036101499
    eng = sp.engineering_design(cfg)
    assert eng["seed_base"] == s1.TEST_SEED_BASE != s1.PILOT_SEED_BASE
    bad = copy.deepcopy(cfg)
    bad["seed_base"] = 1
    with pytest.raises(ValueError):
        sp.pilot_design(bad)


def test_pilot_mode_requires_explicit_flag_and_env(monkeypatch, tmp_path, cfg):
    with pytest.raises(SystemExit):
        sp.main(["--mode", "pilot", "--output", str(tmp_path)])
    monkeypatch.delenv("S1_ALLOW_PILOT_SEEDS", raising=False)
    with pytest.raises(PermissionError):
        sp.run_family(sp.pilot_design(cfg), CAY, sp.Budget(1.0))


def test_truncation_keeps_certified_bracket():
    g, srcs = s1.build_instance(CAY, 512, 0, 0, 4, s1.TEST_SEED_BASE)
    for v in srcs.tolist():
        res = s1.certified_returns(g, v, 32, r_start=4)
        rec = sp.SourceRecord(CAY, 512, 0, 0, 32, g.n, res, 0.0, 0.0, 0)
        tr = sp.truncate(rec, 8)
        exact = graph_even_returns(g, v, list(range(1, 9)))
        for t in range(1, 9):
            assert tr.res.q_lower[t - 1] <= exact[t] * (1 + 1e-12)
            assert exact[t] <= tr.res.q_lower[t - 1] * (1 + s1.ETA) + 1e-15
        assert tr.res.T == 8 and tr.res.q_lower.size == 8
    over = sp.SourceRecord(CAY, 512, 0, 0, 32, g.n, s1.KilledBallResult(
        0, 1, 4, 32, 1, 1, np.full(32, np.nan), np.full(32, np.nan), {}, "OVER_CAP"),
        0.0, 0.0, 0)
    with pytest.raises(ValueError):
        sp.truncate(over, 8)


def test_ladder_accepts_first_rung_when_cheap(cfg):
    d = tiny(cfg)
    fr = sp.run_family(d, CAY, sp.Budget(600))
    assert fr.status == "COMPLETE" and fr.T == 32
    assert [s["decision"] for s in fr.ladder] == ["accept"]
    assert len(fr.records) == 2 * 8 * 4
    assert len(fr.tree_cpu_s) == 16


def test_ladder_steps_down_then_blocks_on_cost(cfg):
    d = tiny(cfg, ladder_trigger_cpu_s=0.0)
    fr = sp.run_family(d, CAY, sp.Budget(600))
    assert [s["T"] for s in fr.ladder] == [32, 16, 8]
    assert fr.ladder[-1]["decision"] == "BLOCKED (budget)" and fr.status == "BLOCKED"
    assert fr.T == 8 and len(fr.records) == 4      # tree 0 kept and reported
    an = sp.family_analysis(d, fr)
    assert an["status"] == "BLOCKED"
    dec = sp.decide_family(d, fr, an)
    assert dec["h"] is None and "family" in dec["failures"]


def test_over_cap_sources_are_recorded_never_dropped(cfg):
    d = tiny(cfg, edge_step_cap=10)
    fr = sp.run_family(d, CAY, sp.Budget(600))
    assert fr.status == "BLOCKED"
    assert all(s["over_cap_sources"] for s in fr.ladder)
    assert len(fr.records) == 4 and all(r.res.status == "OVER_CAP" for r in fr.records)
    csv = sp.numeric_csv([fr]).decode()
    assert csv.count("OVER_CAP") == 4


def test_over_cap_on_first_rung_recomputed_at_lower_T(cfg):
    g, srcs = s1.build_instance(CAY, 256, 0, 0, 4, s1.TEST_SEED_BASE)
    nnz = [s1.certified_returns(g, v, 8, r_start=16).nnz for v in srcs.tolist()]
    # cap admits every source at T=16 (R>=16 balls) but not at T=32 for the largest ball
    big = [s1.certified_returns(g, v, 32, r_start=16).nnz for v in srcs.tolist()]
    cap = 2 * 16 * max(max(big), max(nnz))
    if 2 * 32 * max(big) <= cap:
        pytest.skip("instance does not separate the rungs")
    d = tiny(cfg, edge_step_cap=cap)
    fr = sp.run_family(d, CAY, sp.Budget(600))
    assert fr.ladder[0]["over_cap_sources"] and fr.ladder[0]["decision"] == "reduce T to 16"
    assert fr.T == 16 and fr.status == "COMPLETE"
    tree0 = [r for r in fr.records if (r.i_size, r.i_rep) == (0, 0)]
    assert len(tree0) == 4 and all(r.res.status == "OK" and r.res.T == 16 for r in tree0)
    # later trees may still exceed the cap: they stay in the record and block the decision
    an = sp.family_analysis(d, fr)
    later_over = [(r.i_size, r.i_rep, r.res.source) for r in fr.records if r.res.status != "OK"]
    assert an["over_cap_records"] == later_over
    if later_over:
        assert sp.decide_family(d, fr, an)["failures"]["family"] == "OVER_CAP sources present"


def test_global_budget_marks_partial(cfg):
    d = tiny(cfg)
    fr = sp.run_family(d, CAY, sp.Budget(0.0))
    assert fr.status == "PARTIAL" and len(fr.records) == 4
    an = sp.family_analysis(d, fr)
    assert sp.decide_family(d, fr, an)["h"] is None


def test_run_pilot_end_to_end_is_deterministic(cfg, tmp_path):
    d = tiny(cfg)
    r1 = sp.run_pilot(d, tmp_path / "a", controls=False)
    r2 = sp.run_pilot(d, tmp_path / "b", controls=False)
    assert r1["numeric_csv_sha256"] == r2["numeric_csv_sha256"]
    assert (tmp_path / "a" / "s1_pilot_numeric.csv").read_bytes() == \
        (tmp_path / "b" / "s1_pilot_numeric.csv").read_bytes()
    rep = json.loads((tmp_path / "a" / "s1_pilot_report.json").read_text())
    assert rep["mode"] == "engineering" and rep["design"]["seed_base"] == s1.TEST_SEED_BASE
    assert rep["decision"]["verdict"] in ("GO (full S2)", "GO (reduced)", "NO-GO (scoped)")
    for fam in (CAY, UST):
        fa = rep["families"][fam]
        assert fa["status"] == "COMPLETE"
        for size in fa["sizes"].values():
            assert size["n_trees"] == 8 and size["certified"]
            for w in size["windows"].values():
                assert len(w["psi"]) == 8 and w["headroom_min"] > 0
                assert w["bootstrap"]["n_boot"] == 64
            lb = size["degree_bias"]["leaf_share"]
            assert all(0 <= x <= 1 for x in lb)
        assert rep["family_decisions"][fam]["tested_windows"] == len(
            s1.candidate_windows(32, 8, 3))
    assert rep["families"][RRT]["status"] == "COMPLETE"
    timing = (tmp_path / "a" / "s1_pilot_timing.csv").read_text().splitlines()
    assert len(timing) == 1 + 2 * 8 * 4 * 2 + 2 * 4


def test_decision_rule_branches(cfg):
    d = sp.pilot_design(cfg)

    def dec(h_cay, h_ust):
        return sp.decision({CAY: {"h": h_cay}, UST: {"h": h_ust}}, d)

    assert dec(0.02, 0.03)["verdict"] == "GO (full S2)"
    assert dec(0.02, 0.04)["verdict"] == "GO (reduced)"
    assert dec(0.05, 0.05)["verdict"] == "GO (reduced)"
    r = dec(0.02, None)
    assert r["verdict"] == "NO-GO (scoped)" and r["single_family_feasible_descriptive"] == [CAY]
    assert dec(0.06, 0.01)["verdict"] == "NO-GO (scoped)"
    assert dec(float("nan"), 0.01)["verdict"] == "NO-GO (scoped)"


def test_s2_projection_minimal_n(cfg):
    d = sp.pilot_design(cfg)
    rng = np.random.default_rng(5)
    psi = rng.normal(0, 0.2, size=8)
    proj = sp.s2_projection(d, psi, cpu_per_tree_s=10.0)
    assert proj["n_max_in_budget"] == 1080
    m = proj["by_multiplier"]["1"]
    U = m["U"]
    assert U == pytest.approx(7 * psi.var(ddof=1) / stats.chi2.ppf(0.05, 7))

    def h(n):
        return stats.t.ppf(0.975, n - 1) * math.sqrt(U / n)

    for name, target in (("full", 0.03), ("reduced", 0.05)):
        n = m["n_needed"][name]
        assert n is not None and h(n) <= target and (n == 8 or h(n - 1) > target)
    assert proj["by_multiplier"]["3"]["U"] == pytest.approx(3 * U)
    poor = sp.s2_projection(d, psi, cpu_per_tree_s=10_000.0)
    assert poor["n_max_in_budget"] == 1
    assert math.isnan(poor["by_multiplier"]["1"]["h_at_n_max"])


def test_source_jackknife_zero_for_identical_sources():
    times = [1, 2, 4, 8]
    q = np.array([0.5, 0.3, 0.2, 0.12, 0.08, 0.06, 0.05, 0.04])

    def rec(rep, src, scale):
        r = s1.KilledBallResult(src, 2, 8, 8, 10, 10, q * scale, np.zeros(8))
        return sp.SourceRecord(CAY, 64, 0, rep, 8, 64, r, 0, 0, 0)

    per_tree = {k: [rec(k, j, 1 + 0.1 * k) for j in range(3)] for k in range(4)}
    assert sp.source_jackknife_sd(per_tree, 2, 8, times) == pytest.approx(0.0, abs=1e-12)
    per_tree[0][0] = rec(0, 0, 2.0)
    assert sp.source_jackknife_sd(per_tree, 2, 8, times) > 0


def test_p0d_replay_matches_in_run_tree_including_ladder(cfg):
    d = tiny(cfg)
    fr = sp.run_family(d, CAY, sp.Budget(600))
    assert sp.p0d_pilot_tree(d, fr)["pass"]
    d2 = tiny(cfg, ladder_trigger_cpu_s=0.0)
    d2["T_ladder"] = [32, 16, 8, 4]  # still blocked at the end, path of four rungs
    fr2 = sp.run_family(d2, CAY, sp.Budget(600))
    rep = sp.p0d_pilot_tree(d2, fr2)
    assert rep["T_path"] == [32, 16, 8, 4] and rep["pass"]


def test_exhausted_budget_before_families_is_no_go(cfg, tmp_path):
    rep = sp.run_pilot(tiny(cfg, total_cpu_s=0.0), tmp_path, controls=False)
    assert all(a["status"] == "PARTIAL" for a in rep["families"].values())
    assert rep["decision"]["verdict"] == "NO-GO (scoped)" and not rep["budget"]["within_total"]


def test_numeric_csv_is_rectangular_across_ladder_horizons():
    import csv
    import io

    def family(fam, T, size):
        res = s1.KilledBallResult(0, 1, 4, T, 3, 4, np.full(T, 0.25), np.zeros(T))
        rec = sp.SourceRecord(fam, size, 0, 0, T, 10, res, 0, 0, 0)
        return sp.FamilyRun(fam, T=T, records=[rec])

    rows = list(csv.reader(io.StringIO(sp.numeric_csv([
        family(CAY, 8, 256), family(UST, 4, 16), family(RRT, 2, 256)
    ]).decode())))
    header = rows[0]
    assert len(rows) == 4 and sum(row[0] == "family" for row in rows) == 1
    assert len({len(row) for row in rows}) == 1
    assert header[-4:] == ["q_t1", "q_t2", "q_t4", "q_t8"]
    assert [row[header.index("T")] for row in rows[1:]] == ["8", "4", "2"]
    assert rows[2][-1] == "" and rows[3][-2:] == ["", ""]
    assert rows[1][-1] == "0.25"


def test_exceeding_budget_on_final_tree_marks_partial(cfg, monkeypatch):
    d = tiny(cfg)
    original = sp._run_tree
    calls = {"n": 0}

    def counted(*args, **kwargs):
        result = original(*args, **kwargs)
        calls["n"] += 1
        return result

    monkeypatch.setattr(sp, "_run_tree", counted)
    budget = sp.Budget(1000.0)
    monkeypatch.setattr(budget, "exceeded", lambda: calls["n"] >= 16)
    fr = sp.run_family(d, CAY, budget)
    assert calls["n"] == 16 and fr.status == "PARTIAL"
    assert any("final tree" in reason for reason in fr.notes)


def test_control_stop_vetoes_positive_decision(cfg, tmp_path, monkeypatch):
    d = tiny(cfg)
    monkeypatch.setattr(sp.s1, "p0a", lambda: {"pass": False})
    monkeypatch.setattr(sp.s1, "p0c", lambda: {"pass": True})
    monkeypatch.setattr(sp, "p0d_pilot_tree", lambda *args, **kwargs: {"pass": True})
    monkeypatch.setattr(sp, "decision", lambda *args, **kwargs: {"verdict": "GO (full S2)"})
    report = sp.run_pilot(d, tmp_path, controls=True)
    assert report["decision"]["verdict"] == "FAIL (P0 STOP)"
    assert "P0_STOP:P0a" in report["decision"]["stop_reasons"]


def test_excess_total_budget_vetoes_positive_decision(cfg, tmp_path, monkeypatch):
    d = tiny(cfg, total_cpu_s=0.0)
    monkeypatch.setattr(sp, "decision", lambda *args, **kwargs: {"verdict": "GO (full S2)"})
    report = sp.run_pilot(d, tmp_path, controls=False)
    assert report["decision"]["verdict"] == "NO-GO (scoped)"
    assert "total_cpu_budget_exceeded" in report["decision"]["stop_reasons"]


def test_pilot_mode_does_not_allow_skipping_stop_controls(cfg, tmp_path):
    with pytest.raises(ValueError, match="P0 STOP"):
        sp.run_pilot(sp.pilot_design(cfg), tmp_path, controls=False)


def test_ladder_cost_compounds_across_two_reductions(cfg, monkeypatch):
    d = tiny(cfg, ladder_trigger_cpu_s=0.0)
    # Fixed source costs independent of T intentionally expose bookkeeping errors.
    # Projections after two 1/2 horizon reductions must be 1+4*(2/4) = 3, not 5.
    def fake_tree(design, fam, i_size, size, i_rep, T, recompute_only=None):
        records = []
        for v in range(4):
            res = s1.KilledBallResult(v, 1, 4, T, 4, 6,
                                      np.full(T, 0.25), np.zeros(T))
            records.append(sp.SourceRecord(fam, size, i_size, i_rep, T, size,
                                           res, 2.0, 2.0, 0))
        return records, 1.0, 9.0, 9.0

    monkeypatch.setattr(sp, "_run_tree", fake_tree)
    fr = sp.run_family(d, CAY, sp.Budget(1000.0))
    assert fr.status == "BLOCKED"
    assert [x["T"] for x in fr.ladder] == [32, 16, 8]
    assert [x["tree0_cpu_s"] for x in fr.ladder] == pytest.approx([9.0, 5.0, 3.0])
