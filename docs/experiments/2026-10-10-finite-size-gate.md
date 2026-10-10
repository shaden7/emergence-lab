# Finite-size gate (report gate 5) — result

**Preregistration:** [FINITE_SIZE_GATE_PREREGISTRATION.md](../FINITE_SIZE_GATE_PREREGISTRATION.md), committed in `7005c0fdbbbcebf880150259fb976b426a877a14` before any draw with the registered seeds. Config `configs/finite_size_gate.json` SHA-256 `2176235a66c7c437d008307ebe8129519b138c7ec62520b0afbda6b073fae6a2`, unchanged. **No deviations.**

**Execution:** local, Python 3.13.16 / NumPy 2.5.3, 2 worker processes, 713 s wall, 5.69 × 10⁹ attempted flips (main + controls). Command:
`python -m emergence_lab.finite_size_gate --config configs/finite_size_gate.json --output results/finite_size_gate.json --workers 2` with `GIT_SHA=7005c0f…`. Full JSON report: [2026-10-10-finite-size-gate-report.json](2026-10-10-finite-size-gate-report.json). Raw `.npz` SHA-256 **`b18423a20e428583a493e45ff24146a5b0dd5592c6b8654772aecd8914cc2287`** (not committed; ~MBs; regenerable deterministically; the GitHub-runner step exists but `workflow_dispatch` returns 403 for the Director integration). Nothing ran on Lightsail.

## Outcome: GATE 5 PASS (all 65 checks: 48 per-size, 15 exponent-window, 2 control)

### Exponent fits (known exact values 0.125, 1.75, 1; estimate ± scaled SE; χ²/dof; deviation; allowed = 3·SE + δ; z without δ)

| Window | β/ν | γ/ν | 1/ν |
| --- | --- | --- | --- |
| **primary {12…48}** | 0.1256 ± 0.0021 (0.68); +0.0006 ≤ 0.0112; z 0.3 | 1.7499 ± 0.0030 (0.63); −0.0001 ≤ 0.0391; z −0.0 | 1.0611 ± 0.0111 (0.94); +0.061 ≤ 0.113; **z 5.5** |
| {8…48} | 0.1236 ± 0.0013; z −1.1 | 1.7536 ± 0.0020; z 1.9 | 1.0747 ± 0.0089; **z 9.9** |
| {16…48} | 0.1246 ± 0.0032; z −0.1 | 1.7504 ± 0.0046; z 0.1 | 1.0420 ± 0.0183; z 2.3 |
| {8…32} | 0.1225 ± 0.0016; z −1.6 | 1.7554 ± 0.0022; z 2.4 | 1.0799 ± 0.0114; **z 8.7** |
| {12…32} | 0.1244 ± 0.0027; z −0.2 | 1.7522 ± 0.0039; z 0.6 | 1.0638 ± 0.0175; z 4.3 |

All fifteen X checks pass. **β/ν and γ/ν are recovered within statistical error alone** (|z| ≤ 2.4 without the tolerance) in every window. **1/ν passes only because of the preregistered allowance δ = 0.08**: the estimates 1.04–1.08 lie significantly above 1 without it, and the excess shrinks as L_min grows (1.075 → 1.061 → 1.042 for L_min = 8, 12, 16).

### Per-size checks

| L | E: z vs exact | c (jackknife) vs exact c | z | max R̂ (e / \|m\|) | min ESS (e / \|m\|) | hot−cold z (e / \|m\|) | median τ(\|m\|), sweeps | Binder U |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | 0.83 | 1.1443 ± 0.0040 vs 1.1456 | −0.31 | 1.0001 / 1.0002 | 68,365 / 61,928 | −0.90 / 0.27 | 6 | 0.6129 ± 0.0004 |
| 12 | −0.45 | 1.3487 ± 0.0046 vs 1.3530 | −0.92 | 1.0003 / 1.0004 | 43,191 / 33,810 | 0.13 / −0.02 | 12 | 0.6125 ± 0.0005 |
| 16 | −0.10 | 1.4982 ± 0.0079 vs 1.4987 | −0.06 | 1.0006 / 1.0008 | 27,149 / 19,406 | −0.09 / −0.65 | 22 | 0.6109 ± 0.0007 |
| 24 | −1.23 | 1.6928 ± 0.0073 vs 1.7027 | −1.35 | 1.0002 / 1.0005 | 29,709 / 16,992 | 0.10 / −0.28 | 48 | 0.6119 ± 0.0008 |
| 32 | 0.00 | 1.8489 ± 0.0105 vs 1.8468 | 0.21 | 1.0009 / 1.0016 | 17,582 / 8,770 | 0.61 / −0.05 | 89 | 0.6111 ± 0.0012 |
| 48 | 0.83 | 2.0540 ± 0.0119 vs 2.0491 | 0.42 | 1.0011 / 1.0021 | 17,101 / 8,291 | 0.28 / −0.06 | 197 | 0.6101 ± 0.0014 |

(τ in sweeps = 2 × draws, 1 + 2Σρ convention.) The measured τ₄₈(|m|) ≈ 197 sweeps matches the a-priori sizing estimate of ≈ 200 (z ≈ 2.17 from the L32 τ).

### Controls (primary window, same rule)

| Control | β/ν estimate | γ/ν estimate | Rejected | U(48) |
| --- | --- | --- | --- | --- |
| C1 Ising T = 2.6 | 0.996 | 0.127 | yes | 0.042 |
| C2 J = 0 i.i.d. | 0.994 | 0.010 | yes | −0.016 |

Both behave as expected for non-critical systems (\|m\| ~ L⁻¹; χ saturating or constant).

## Evidence levels

- **Known mathematics / established results (not ours):** exact 2D Ising exponents; Kaufman finite-torus energy (and its T-derivative); U* = 0.61069 (Salas & Sokal 2000, cited, not re-derived).
- **Numerical observations (this run, configuration and seeds above):** all items in the tables. Exact-reference checks: 12/12 within |z| ≤ 1.35. Binder U(L) decreases from 0.6129 (L8) to 0.6101 ± 0.0014 (L48), consistent with the cited U* at L ≥ 16 within ≈ 1 SE (secondary, not gating).
- **Hypotheses (untested):** the upward bias of the 1/ν estimate from D = ∂ln⟨|m|⟩/∂K is a correction-to-scaling effect (supported only by its decrease with L_min); a fit with a correction term, or the Binder-derivative estimator, would test this.
- **Proofs:** none.

## Interpretation and limitations

Report gate 5 is met **for this sampler, T and size range, at the preregistered accuracy**. The result calibrates the pipeline; it says nothing new about the Ising model or about emergent structure. The 1/ν pass depends on the tolerance; a stricter "statistical error only" rule would have failed for 1/ν in three of five windows, and that is the main caveat to carry forward to any later use of derivative-based ν estimates (e.g. in Phase-1 dimension or scaling analyses). Other limitations: fits without correction terms; one sampler and lattice; one execution environment (runner reproduction of the `.npz` digest pending a manual dispatch); self-review by the producing session (later-pass challenge invited). Phase 0 remains **NO-GO** until archival gate 6 is decided.
