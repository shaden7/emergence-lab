# Phase-0 GO/NO-GO decision record (Ising calibration)

**Date:** 2026-10-10. **Director session:** `rd-claude-20261010T115647Z-4e5855`. This is a later-pass session; it did not produce gates 4–6. **Base:** `main` `6b4fc6e`.

**Decision: GO for Phase 1, scoped and conditional on the binding constraints C1–C5 below.** This replaces the NO-GO of [ISING_CALIBRATION_REPORT.md](ISING_CALIBRATION_REPORT.md) §D/§J as the *current* Phase-0 status. That report stays unchanged as the audit trail.

**What this decision is.** A *methodological decision* that the project's Monte Carlo, uncertainty, control and provenance tooling is calibrated well enough on the 2D Ising benchmark to start the next preregistered stage.

**What it is not.**
- It is not a physics result. Every target used (Tc, exponents, Kaufman finite-torus energy) is known theory.
- It is not independent external review. All reviews were AI-mediated, by sessions of the same model family.
- It does **not** authorize deployment, Lightsail runs or new spending.

## 1. Gate audit against the prospective gates G1–G6 (report §D)

| Gate (report §D) | Evidence | Verdict |
| --- | --- | --- |
| **G1** reviewed sequential integration, green main CI | Stack #1→#3→#7→#9→#10→#12 and #13–#20 merged with expected-head guards and a review record on each PR. `main` CI success on `6b4fc6e` ([run 38047588399](https://github.com/shaden7/emergence-lab/actions/runs/38047588399)). Second-session reviews: #13 by #15; gate 4 analysis re-run from released raw data by the gate-6 session; gate 5 exponents recomputed here (§2). | **Met** in the policy sense (AI-mediated later-pass review, not external) |
| **G2** equilibrium target from independent hot/cold starts, seed-disjoint holdout, numerical bias bound | L4: [equilibration pilot](ISING_CALIBRATION_REPORT.md) (random/ordered/exact-stationary starts) and the preregistered fresh-seed [burn-in replication](experiments/2026-10-10-burnin-replication.md) (#16: zero-burn bias replicated, burn ≥ 100 sweeps required at T ≤ 2.27). Stronger tests at larger L: [L32 gate](experiments/2026-10-10-l32-critical-gate.md) (#13), 16 hot + 16 cold, E vs exact z = −0.46, hot−cold z −0.76/0.64. [Finite-size gate](experiments/2026-10-10-finite-size-gate.md) (#18), L = 8…48, hot/cold \|z\| ≤ 0.90, E and C vs exact \|z\| ≤ 1.35. | **Met.** The L4 hot/cold part was a pilot, not a preregistered holdout. It is superseded by the preregistered hot/cold-vs-exact checks at L = 8…48. |
| **G3** robust τ/ESS window sensitivity, short chains flagged, incl. AR(1) φ ≥ 0.98 | L32 gate power control: the PR #12 window (1,800 sweeps) fails G1/G3 as prespecified; rank-normalized R̂ and bulk/tail ESS match ArviZ to ~1e-12. **New in this session:** preregistered [AR(1) addendum](experiments/2026-10-10-g3-ar1-stress.md) for `convergence.py` at φ = 0.98 and 0.995, **PASS 10/10**. τ is recovered to ≈ 2–3 % at n = 500 τ, and every chain at n = 20 τ is flagged (ESS ≤ 50 < 100). | **Met**, with the short-chain caveat in C1 |
| **G4** coverage on new seeds, Wilson half-width < 0.05 | [Coverage gate](experiments/2026-10-10-coverage-gate.md) (#17): 379/400 (L16), 381/400 (L32), Wilson half-width ≈ 0.02; power controls fail as required; runner reproduction byte-identical ([38042967864](https://github.com/shaden7/emergence-lab/actions/runs/38042967864)). | **Met** for E, this sampler, Tc, L16/32 |
| **G5** L = 8…32+ with long chains, hot/cold, fit-window stability | Finite-size gate (#18): 65/65 checks. β/ν, γ/ν within statistical error in all windows. **1/ν = 1.04–1.08 passes only through the preregistered tolerance δ = 0.08.** Non-critical controls (T = 2.6, J = 0) rejected. | **Met** at the preregistered accuracy, with the 1/ν caveat in C3 |
| **G6** durably findable raw artifacts with revision-bound manifests | Release [`phase0-evidence-2026-10-10-v1`](https://github.com/shaden7/emergence-lab/releases/tag/phase0-evidence-2026-10-10-v1) (#19/#20, run [38047147426](https://github.com/shaden7/emergence-lab/actions/runs/38047147426)). Pinned SHA-256 in Git; assets re-downloaded and verified by the gate-6 session and again here (`finite_size_gate.npz` `b18423a2…`). | **Met** for gates 4/5; other series see §3 |
| Adversarial null (report §D) | J = 0 and interacting 1D Ising (#12), and in the gate-5 rule: T = 2.6 and J = 0 both rejected | **Met** |
| Seeds not reused for tuning and confirmation | Seed bases are disjoint: L32 2028…, burn-in 2029…, coverage 2030…, AR(1) 2031…, FSS 2032–2034…. Sizing pilots used disjoint seeds and are disclosed in each preregistration. | **Met** |

## 2. Later-pass checks actually executed in this session

All runs were local (Python 3.13.16, NumPy 2.5.3) on `main` code. Nothing ran on Lightsail.

1. **AR(1) G3 addendum.** Preregistration committed and pushed before execution (`96e886b`). Result PASS 10/10, deterministic (two identical executions). The full table is in the [note](experiments/2026-10-10-g3-ar1-stress.md).
2. **Gate 5, independent re-analysis.** The released `finite_size_gate.npz` (SHA-256 `b18423a2…` verified after download) was re-analysed with `scripts/fss_gate_independent_crosscheck.py`. The script does not import `emergence_lab`; it uses unweighted OLS on window 12…48 with a chain bootstrap.
   - β/ν = 0.1261 ± 0.0023 (report 0.1256 ± 0.0021).
   - γ/ν = 1.7487 ± 0.0032 (report 1.7499 ± 0.0030).
   - Both agree with the report and with the exact 1/8 and 7/4. 1/ν was not recomputed.
3. **L32 critical-mixing gate re-run.** Raw `.npz` SHA-256 `57ae4ea037e7f16402d3f0f41645f8f357cd4b09ab11c76648338a9b75bf47a2`, byte-identical for the fourth time, with the same gate outcome: PASS, and the power control fails G1/G3.

## 3. Carry-over caveats: blocking or constraint?

None of the three caveats blocks Phase 1. Each is bounded, characterized and tied to a specific estimator, so each becomes a binding constraint:

- **L32 short-chain per-chain ESS intervals under-cover** (0.903 at 750 draws, gate 4). The AR(1) addendum shows the mechanism in a controlled setting. At ~20 τ, Geyer τ̂ is biased low by ≈ 15 % and single chains reach 0.4 τ. Such intervals are therefore anti-conservative. → **C1**.
- **1/ν passes only via tolerance.** The ∂ln⟨|m|⟩/∂K estimator without correction-to-scaling terms is biased at these L. The correction-to-scaling hypothesis is untested. → **C3**.
- **Unarchived raw series (L32 critical mixing, burn-in replication).** They are not added to the release:
  - The L32 raw data has been reproduced byte-identically four times (local and GitHub runner) from pinned code and seeds in 78 s.
  - The burn-in replication Monte Carlo output is identical between local runs and the runner.
  - Both summary reports are versioned in `docs/experiments/`.
  - Their claims are superseded or extended by the archived gate-4/5 data.
  - Regeneration depends on the NumPy `Generator`/PCG64 stream staying stable across versions; the recorded version is NumPy 2.5.3. Archiving them later, e.g. via an owner-dispatched extension of the archive workflow, is optional and non-blocking. → **C5**.

## 4. Binding constraints for Phase 1 (C1–C5)

- **C1 Uncertainty.** Primary intervals come from ≥ 4 independent replicates (chains or batches). An interval based on per-chain ESS may be primary only when every chain has n ≥ 100 τ̂. Otherwise it is labelled anti-conservative.
- **C2 Convergence.** Report rank-normalized R̂ (< 1.01) and bulk/tail ESS (≥ 400), plus dispersed-start checks. Include a prespecified short-window power control whenever a convergence gate is claimed. Compare against an exact or independent reference wherever one exists.
- **C3 Scaling and exponents.** Do not make an exponent or scaling-law claim from a single estimator without window stability and a correction-to-scaling assessment. Recovering known exponents is calibration, not discovery.
- **C4 Transfer.** Phase 0 calibrated *this* Ising sampler and analysis stack (checkerboard Metropolis, Wolff cross-check, T ≈ Tc, L ≤ 48). It does **not** validate the samplers, integrators or estimators of Phase-1 models. Each Phase-1 model needs its own analytic or null controls. Pilot A provides these: d'Alembert, heat kernel and quantum walk references, per [its preregistration](PILOT_A_CAUSAL_PROPAGATION_PREREGISTRATION.md).
- **C5 Provenance.** Before a gate is declared met, the raw arrays behind it are archived with pinned digests ([archive protocol](PHASE0_EVIDENCE_ARCHIVE.md)). Deterministic regeneration may substitute only when byte-identical reproduction in ≥ 2 environments is documented.

## 5. What GO authorizes, and what it does not

- **Authorizes:** implementing Pilot A per `docs/PILOT_A_CAUSAL_PROPAGATION_PREREGISTRATION.md`, as a **separate reviewed code PR** with its own preregistered gates, within the WIP limit.
- **Does not authorize:**
  - Lightsail deployment of merged code (still a separate reviewed decision with an EatSleepFeel impact check).
  - Any claim about emergent spacetime.
  - Skipping Pilot A's own controls.

## 6. Counterarguments and residual risk

- **Reviewer independence.** Every producer and reviewer was an AI session of the same family. An external statistical review could still find shared blind spots.
- **Narrow scope.** One temperature for coverage and mixing. The coverage reference is energy-only: no exact finite-L |m| exists, and |m| is checked only against the Wolff sampler.
- **Run lengths chosen by sizing pilots.** They used disjoint seeds and were disclosed, but the producing sessions designed their own gates.
- **Possible pressure toward GO.** This decision follows a run of six passing gates. To counter that, it re-ran an independent check (§2) and added a new falsifiable test (G3 addendum) before deciding, instead of relying only on the producers' reports.

A NO-GO remains the correct reading if C1–C5 cannot be honoured in a Phase-1 design. **Reverting to NO-GO** is required if a later pass finds a defect in any gate-4/5 analysis. **Reopening G3** is required if the AR(1) result fails to reproduce.
