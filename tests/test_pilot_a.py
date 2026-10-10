"""Tests for Pilot A reference solvers and controls (development grid only; holdout untouched)."""
import json
import math
from pathlib import Path

import numpy as np
import pytest

from emergence_lab import pilot_a as pa

CFG = json.loads(Path("configs/pilot_a.json").read_text())


def test_protocol_pin_matches_preregistration():
    import hashlib
    data = Path(CFG["protocol"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == CFG["protocol_sha256"]


def test_config_grids_match_preregistration():
    dev, hold = CFG["development"], CFG["holdout"]
    assert dev["continuum_times"] == [0.5, 1.0, 2.0]
    assert dev["sites"] == [0, 1, 2, 4, 6, 8, 12] and dev["ring_sizes"] == [128, 256]
    assert dev["ca_steps"] == [0, 1, 2, 4, 8]
    assert hold["continuum_times"] == [0.75, 1.5, 3.0]
    assert hold["sites"] == [0, 3, 5, 7, 11, 15] and hold["ring_sizes"] == [512, 1024]
    assert hold["ca_steps"] == [3, 5, 12]
    assert CFG["tolerance"] == {"abs_floor": 1e-11, "rel": 1e-6, "censor_below": 1e-8}
    assert CFG["shortcut"]["epsilon"] == 0.05 and CFG["shortcut"]["ring_sizes"] == [128, 256, 512]
    assert CFG["thresholds"] == [1e-3, 1e-6, 1e-9]


# --- W ---------------------------------------------------------------------

def test_wave_strict_support_and_normalisation():
    assert pa.wave_reference(0, 0) == 1.0  # S(0,0) = 1
    for t in (0.5, 1.0, 2.0, 3.0):
        for r in np.linspace(-10, 10, 401):
            if abs(r) > 0.5 + t:
                assert pa.wave_reference(r, t) == 0.0
    assert pa.wave_reference(0, 1.0) == 0.0  # pulses have separated (t > a)
    assert pa.wave_reference(1.0, 1.0) == 0.5
    assert pa.wave_on_front(1.5, 1.0) and not pa.wave_on_front(1.4, 1.0)


# --- H ---------------------------------------------------------------------

@pytest.mark.parametrize("t", [0.5, 1.0, 2.0, 0.75, 3.0])
def test_heat_closed_form_matches_quadrature(t):
    for r in [0, 0.25, 1, 2, 4, 6, 8, 12]:
        ref = pa.heat_reference(r, t)
        num = pa.heat_quadrature(r, t)
        assert ref > 0.0
        assert abs(num - ref) <= max(1e-15, 1e-12 * ref)


def test_heat_is_positive_far_away_and_conserves_mass():
    assert pa.heat_reference(0, 0) == 1.0
    assert pa.heat_reference(20, 1.0) > 0.0  # analytic far witness, ~1e-42
    xs = np.linspace(-40, 40, 160001)
    mass = np.trapezoid([pa.heat_reference(x, 1.0) for x in xs], xs)
    assert abs(mass - 1.0) < 1e-6  # initial mass 2a = 1


def test_euler_stencil_has_artificial_hard_front():
    vals, support = pa.heat_explicit_euler([4, 6], 1.0)
    assert support == 5.5
    assert vals[6.0] == 0.0 and pa.heat_reference(6, 1.0) > 1e-5  # artifact vs continuum
    assert vals[4.0] > 0.0
    with pytest.raises(ValueError):
        pa.heat_explicit_euler([4], 1.0, dt=0.2)  # unstable


# --- CA --------------------------------------------------------------------

@pytest.mark.parametrize("L", [16, 17, 128])
def test_ca_simulation_matches_induction(L):
    for n in range(0, (L - 1) // 2 + 1):
        if not n < L / 2:
            continue
        z = pa.ca_simulate(L, n)
        for r in range(L):
            assert int(z[r]) == pa.ca_reference(r, n, L)


def test_ca_reference_refuses_wraparound():
    with pytest.raises(ValueError):
        pa.ca_reference(0, 64, 128)


# --- Q ---------------------------------------------------------------------

@pytest.mark.parametrize("L", [16, 31, 128])
def test_qwalk_numeric_matches_fourier_and_taylor(L):
    for t in (0.5, 1.0, 2.0):
        num = pa.qwalk_numeric(L, t)
        ref = pa.qwalk_fourier(L, t)
        tay = pa.qwalk_taylor(L, t)
        assert abs(math.fsum(num) - 1) < 1e-12 and abs(math.fsum(ref) - 1) < 1e-12
        assert np.max(np.abs(num - ref)) < 1e-13
        assert np.max(np.abs(tay - ref)) < 1e-13


def test_qwalk_initial_state_and_bessel_limit():
    p0 = pa.qwalk_fourier(64, 0.0)
    assert p0[0] == pytest.approx(1.0, abs=1e-15) and np.max(p0[1:]) < 1e-28
    # small ring: wrap-around makes the ring differ from the infinite line
    assert abs(pa.qwalk_fourier(8, 3.0)[2] - pa.qwalk_bessel_line(2, 3.0)) > 1e-3
    # large ring: identical to the Bessel limit at short times
    ref = pa.qwalk_fourier(256, 1.0)
    for r in range(0, 9):
        assert abs(ref[r] - pa.qwalk_bessel_line(r, 1.0)) < 1e-14


def test_bessel_series_known_values():
    # J0(1), J1(2), J5(4); constants from scipy.special.jv 1.18.1 (scipy is not a dependency)
    assert pa.bessel_j(0, 1.0) == pytest.approx(0.7651976865579666, abs=1e-14)
    assert pa.bessel_j(1, 2.0) == pytest.approx(0.5767248077568736, abs=1e-14)
    assert pa.bessel_j(5, 4.0) == pytest.approx(0.1320866560470983, abs=1e-14)
    assert pa.bessel_j(-3, 2.0) == pa.bessel_j(3, 2.0)


def test_shortcut_far_response_is_from_the_built_in_edge():
    L, rs = 128, 32
    num = pa.qwalk_numeric(L, 1.0, shortcut=(rs, 0.05))
    ref = pa.qwalk_taylor(L, 1.0, shortcut=(rs, 0.05))
    assert abs(num[rs] - ref[rs]) < 1e-14
    assert num[rs] > 1e-4 and pa.qwalk_fourier(L, 1.0)[rs] < 1e-25
    # leading short-time behaviour |eps t|^2 at tiny t
    t = 1e-3
    assert pa.qwalk_taylor(L, t, shortcut=(rs, 0.05))[rs] == pytest.approx((0.05 * t) ** 2, rel=1e-5)


# --- classification and fronts ---------------------------------------------

def test_precision_status_rules():
    s = pa.precision_status
    assert s("Q", 1e-3 * (1 + 5e-7), 1e-3) == "match"
    assert s("Q", 1e-3 * (1 + 5e-6), 1e-3) == "mismatch"
    assert s("Q", 0.0, 1e-9) == "censored"   # never "zero"
    assert s("Q", 5e-9, 1e-9) == "censored"
    assert s("W", 0.0, 0.0, analytic_zero=True) == "analytic_zero_ok"
    assert s("CA", 1.0, 0.0, analytic_zero=True) == "analytic_zero_violated"
    assert s("W", 0.5, 0.5, on_front=True) == "front_excluded"
    # absolute floor governs near 1e-8
    assert s("H", 1e-8 + 9e-12, 1e-8) == "match"
    assert s("H", 1e-8 + 2e-11, 1e-8) == "mismatch"


def test_detection_front_depends_on_threshold_not_support():
    sites = [0, 1, 2, 4, 6, 8, 12]
    vals = [pa.qwalk_fourier(256, 1.0)[r] for r in sites]
    fronts = [pa.detection_front(sites, vals, eta) for eta in (1e-3, 1e-6, 1e-9)]
    assert fronts == sorted(fronts) and fronts[0] < fronts[-1]
    assert pa.detection_front(sites, vals, 2.0) is None
    # every site beyond the coarsest front still has strictly positive reference
    assert all(v > 0 for r, v in zip(sites, vals) if r > fronts[0])


# --- N1 and full development run --------------------------------------------

def test_null_correlation_control():
    out = pa.null_correlation(2027050101, 4000)
    assert out["a1_pass"] and out["remote_delta_max_abs"] == 0.0
    assert out["observational_corr_ci95"][0] > 0.4
    # zero shift: no local manipulation, so A1 (which requires the local effect) must fail
    assert pa.null_correlation(2027050101, 4000, shift=0.0)["a1_pass"] is False


def test_development_run_gates_and_determinism():
    r1 = pa.run(CFG, "development")
    r2 = pa.run(CFG, "development")
    for k in ("a1_pass", "a2_pass", "a3_pass", "a4_pass", "a5_pass", "no_mismatch"):
        assert r1[k] is True, k
    strip = lambda r: [{k: v for k, v in x.items()} for x in r["rows"]]  # noqa: E731
    assert strip(r1) == strip(r2)
    assert r1["summary"].get("mismatch", 0) == 0
    # A3 far witnesses: W exactly zero by theorem, H and Q positive and matched
    fw = r1["far_witness_a3"]
    assert {x["model"] for x in fw} == {"W", "H", "Q"}
    assert all(x["S_ref"] == 0.0 for x in fw if x["model"] == "W")
    assert all(x["S_ref"] > 1e-8 for x in fw if x["model"] != "W")


def test_holdout_requires_explicit_flag(tmp_path):
    with pytest.raises(SystemExit):
        pa.main(["--phase", "holdout", "--output", str(tmp_path)])
    assert not (tmp_path / "result.json").exists()


def test_a2_detects_injected_support_violation(monkeypatch):
    orig = pa.ca_simulate

    def leaky(L, n):
        z = orig(L, n)
        z[n + 1] = True  # one bit outside the cone
        return z

    monkeypatch.setattr(pa, "ca_simulate", leaky)
    assert pa.run(CFG, "development")["a2_pass"] is False


def test_a4_detects_wrong_quantum_sign(monkeypatch):
    # mutation: a Fourier reference with a different dispersion must fail A4
    monkeypatch.setattr(pa, "qwalk_fourier", lambda L, t, J=1.0: pa.qwalk_numeric(L, 1.1 * t, J))
    r = pa.run(CFG, "development")
    assert r["a4_pass"] is False and r["no_mismatch"] is False


# --- later-pass review additions (2026-10-10) -------------------------------

@pytest.mark.parametrize("t", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0])
def test_wave_leapfrog_matches_dalembert_bit_for_bit(t):
    # quarter-integer sites, includes front points and the gap between separated pulses
    sites = [k / 4 for k in range(-64, 65)]
    num = pa.wave_leapfrog(sites, t)
    for s in sites:
        assert num[s] == pa.wave_reference(s, t), (s, t)
        if abs(s) > 0.5 + t:
            assert num[s] == 0.0


def test_wave_leapfrog_rejects_off_grid_input():
    with pytest.raises(ValueError):
        pa.wave_leapfrog([0.1], 1.0)
    with pytest.raises(ValueError):
        pa.wave_leapfrog([1.0], 0.3)


def test_a2_detects_injected_wave_violation(monkeypatch):
    orig = pa.wave_leapfrog

    def leaky(sites, t, a=0.5, c=1.0, h=0.25):
        out = orig(sites, t, a, c, h)
        out[12.0] = 1e-300  # tiny nonzero outside the cone
        return out

    monkeypatch.setattr(pa, "wave_leapfrog", leaky)
    assert pa.run(CFG, "development")["a2_pass"] is False


def test_registered_witnesses_are_not_on_holdout_grid():
    # Grid membership only; no holdout values are computed here.
    hold = CFG["holdout"]
    on_grid = [(t, r) for t, r in CFG["far_witnesses"]
               if t in hold["continuum_times"] and r in hold["sites"]]
    assert on_grid == []


def test_a3_decision_is_never_vacuous():
    m = {"model": "H", "precision_status": "match"}
    c = {"model": "Q", "precision_status": "censored"}
    bad = {"model": "Q", "precision_status": "mismatch"}
    assert pa.a3_decision([], [], "development") is False
    assert pa.a3_decision([m], [], "development") is True
    assert pa.a3_decision([m], [], "holdout") is False          # no exterior witness
    assert pa.a3_decision([m], [c], "holdout") is False         # censored only
    assert pa.a3_decision([m], [m, c], "holdout") is True
    assert pa.a3_decision([m], [m, bad], "holdout") is False
    assert pa.a3_decision([bad], [m], "holdout") is False


def test_registered_witnesses_evaluated_directly_on_development():
    reg = pa._far_witness_registered(CFG, "development")
    assert {(x["model"], x["L"]) for x in reg} == {("H", None), ("Q", 128), ("Q", 256)}
    assert all(x["precision_status"] == "match" and x["S_ref"] > 1e-8 for x in reg)
