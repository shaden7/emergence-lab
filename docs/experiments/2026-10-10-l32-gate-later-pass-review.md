# Later-pass review of PR #13 — L32 critical-mixing gate

**Session:** Director lease `rd-claude-20261010T081233Z-2bca3d` (a different session from the producer `rd-claude-20261010T073142Z-d6f71d`). AI-mediated review by the same model family, **not independent external review**.
**Object:** merge commit `effba3e9d9ad68956623a6f21f9f14ca93f2bf23` (`exact_finite.py`, `convergence.py`, `critical_gate.py`, preregistration, report).
**Decision:** **PASS (confirmed)**. No defect found; one evidence gap closed (|m| had no reference), see below.

## What was checked

| Check | Method | Result |
| --- | --- | --- |
| Preregistration integrity | `git diff ab67cdc 06705ef` on config, preregistration, runner, diagnostics, exact energy | only four `print` lines added to `critical_gate.main()` after preregistration; no criterion, seed or config change |
| Raw-data reproduction | re-ran `python -m emergence_lab.critical_gate --config configs/l32_critical_gate.json --workers 2` (Python 3.13.16, NumPy 2.5.3, 91 s) | raw `.npz` SHA-256 `57ae4ea0…47a2`, **byte-identical** to producer and GitHub runner (third independent execution) |
| Reported numbers | recomputed from the fresh JSON | all handoff values match (pooled E, z = −0.455, 30/32 coverage, R̂, ESS, hot/cold z, τ medians 36/85 sweeps, power-control values) |
| Sampler logic | code reading | checkerboard sublattices have no internal bonds, so the half-sweep update is valid Metropolis; ΔE = 2 s Σnb; each bond counted once in E; int16 sums cannot overflow for L ≤ 64 (|E| ≤ 2L²) |
| Exact reference, M = 32 dimension | Kaufman vs independent transfer matrix on 32 × 6, 32 × 9, 32 × 10 tori at T = 1.5, 2.269185, 3.5 | max difference 1.8·10⁻¹² (odd width included; existing tests used only small square/even sizes) |
| Exact reference, self-consistency | Z(M,N) vs Z(N,M); analytic E vs central difference of ln Z at L = 32; L → ∞ at exact Tc | symmetry ≤ 2·10⁻¹⁴; derivative agrees to 3·10⁻⁹ (difference-step error); E + √2 = −0.01944, −0.00486, −0.00122, −0.00030 for L = 32, 128, 512, 2048, i.e. ∝ 1/L towards Onsager's −√2 |
| **Independent sampler** | single-cluster Wolff (`scripts/wolff_crosscheck.py`, no shared update code), 16 chains, seeds 2029050001–016, 1,000 warmup + 40,000 clusters, measure every 2nd; decision rule fixed before the run: \|z\| ≤ 3 for each comparison | see next table; 188 s |

**Wolff validation first:** on 4 × 4 at T = 2.269185 (8 chains × 20,000 clusters, seeds 2029040001–008) Wolff gives E −1.56544 ± 0.00167 (exact −1.56562, z = 0.11) and |m| 0.84379 ± 0.00075 (exact 0.84386).

## Independent-sampler cross-check at L = 32, T = 2.269185 (numerical observation)

| Observable | Wolff (16 chains, t-SE) | Checkerboard gate (32 chains) | z (Wolff − gate) | vs exact |
| --- | --- | --- | --- | --- |
| E | −1.433404 ± 0.000284 | −1.433862 ± 0.000446 | +0.87 | Wolff z = +0.90 |
| \|m\| | 0.653710 ± 0.000439 | 0.655549 ± 0.001235 | −1.40 | no exact reference |

Wolff raw-data SHA-256 (int32 E/M sums, all chains): `bdd170f642672ad69e78383f811e9da2545e7f11eb41d49efde9d16975054cbd`. Mean Wolff cluster ≈ 470 sites.

**Interpretation.** Two samplers with unrelated update rules agree on E (both consistent with the exact value) and on |m| within the stated uncertainties. This closes the gap that the gate's |m| result rested only on internal diagnostics (R̂, ESS, hot/cold). It is a *numerical observation*; it does not prove convergence, and both samplers share the same lattice/energy convention and PCG64 generator.

## Limitations

- Same model family as the producer; a human or differently built reviewer could still find what this pass missed.
- The Wolff |m| comparison has ≈ 0.0013 combined standard error; differences smaller than ≈ 0.004 are not resolvable.
- One size, one temperature. Nothing here extends the gate to other L, T or samplers.
- No GitHub-hosted run of the Wolff check was dispatched (dispatch is not available to this integration); it is cheap enough to rerun locally (≈ 3 min, single core).
