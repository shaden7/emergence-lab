# Pilot A, stage 1: reference solvers and null controls (development grid only)

**Protocol:** [PILOT_A_CAUSAL_PROPAGATION_PREREGISTRATION.md](../PILOT_A_CAUSAL_PROPAGATION_PREREGISTRATION.md) v1.0, SHA-256 `c8061aed…`, pinned in `configs/pilot_a.json` and checked at runtime.
**Code:** `src/emergence_lab/pilot_a.py`, `tests/test_pilot_a.py`, config SHA-256 `a55fcfa8…`.
**Scope:** this stage covers the analytic references, independent numerical evaluators, the A3 classification rule and controls N1–N4. **The holdout grid was not evaluated.** The runner refuses it without `--allow-holdout`.

## What is a theorem and what is numerical

- **Mathematical (inputs, not measured):**
  - W (d'Alembert) and CA (induction) have strict support.
  - H has a positive kernel, so S > 0 everywhere for t > 0.
  - Q is analytic in t and nonstrict.
  - These classes are hard-coded in `SUPPORT_CLASS`. No data can change them.
- **Numerical observation (this code, Python 3.13.16 / NumPy 2.5.3, local, 1.3 s CPU):**
  - H: closed form (erfc) compared with 96-node Gauss–Legendre quadrature of the kernel. These share no code. Max relative error 1.7e-14.
  - Q: dense `eigh` compared with explicit Fourier summation (`math.fsum`, no FFT, no eigensolver). A Taylor series is a third path, used in tests. Max relative error 1.6e-13 over the matched cells. Normalisation error < 1e-12.
  - CA: direct simulation compared with the induction formula. Exact agreement, including wrap-around tests at L = 16, 17.
  - W: no independent PDE solver in this stage. S_num *is* the closed form, so the W check is a consistency check, not a numerical validation.
- **Development grid result** (154 cells): 81 `match`, 55 `analytic_zero_ok`, 16 `censored` (S_ref < 1e-8, never reported as zero), 2 `front_excluded` (W top-hat discontinuities), 0 `mismatch`. `rows.csv` SHA-256 is `7a2ff47c…`, byte-identical across two runs.

## Preregistered criteria on the development grid

These are calibration results. The protocol says the development grid is **not** an independent holdout.

| Criterion | Result | Evidence |
| --- | --- | --- |
| A1 (N1 correlation ≠ causation) | pass | corr = 0.497, Fisher 95 % [0.473, 0.520]; remote Δ = 0 exactly for all 4000 paired samples; local Δ = 1. Seed 2027050101. |
| A2 strict support (W, CA) | pass | no theorem zero violated; every W site with \|r\| > a + t has S = 0 |
| A3 far witnesses (t, r) = (1, 4), (1, 6) | pass | H: 5.932806e-3, 4.815957e-5; Q (L = 128, 256): 1.155709e-3, 1.445835e-6; all within max(1e-11, 1e-6 S_ref); W = 0 by theorem |
| A4 Q against finite-ring Fourier | pass | all Q cells `match` or `censored`; ring vs Bessel line differ ≤ 1.1e-16 on this grid (wrap-around terms are negligible at L ≥ 128, t ≤ 2) |
| A5 N2 shortcut (ε = 0.05, r* = L/4) | pass | S(r*) = 4.4e-4 / 5.2e-4 / 3.6e-4 at t = 0.5 / 1 / 2, the same for L = 128, 256, 512. It agrees with the Taylor reference. The no-shortcut ring gives ≤ 2.3e-30. |
| A6 detection fronts | tabulated | Q at t = 1: r_η = 4 / 6 / 6 for η = 1e-3 / 1e-6 / 1e-9. H at t = 2: 6 / 8 / 12. The front moves with η and is capped by the sparse site grid. |
| N4 Euler artifact | shown | forward Euler (dx = 0.5, dt = 0.1, t = 1) is **exactly 0 at r = 6**, where the continuum value is 4.8e-5. It has a hard front at 5.5, which is a solver artifact. |

## Interpretation and limits

- The A5 far response is put in by the built-in edge (distance measured in the original ring metric). It is **not** emergent nonlocality.
- Detection fronts depend on η and the site grid. They say nothing about strict causality: every site beyond the coarsest front has a strictly positive analytic reference.
- No new physics. All four models have metric, clock and propagation constants as inputs.
- **Deviations from the protocol** (also listed in the run manifest):
  - W has no separate PDE solver yet.
  - The N2 times and the N4 grid are development choices; the protocol does not fix them.
  - N5 measurement noise (optional) is not implemented.
- Self-review only. Producer and reviewer are the same AI session.

## Next step

A later session reviews this stage independently, then runs the holdout once and unchanged (`--phase holdout --allow-holdout`; t = 0.75, 1.5, 3; r = 0, 3, 5, 7, 11, 15; L = 512, 1024). It reports A1–A4 and A7 there. Optional before that: add an independent W solver (e.g. characteristic leapfrog at Courant number 1 with a smooth bump) so A2 for W is numerical, not tautological.
