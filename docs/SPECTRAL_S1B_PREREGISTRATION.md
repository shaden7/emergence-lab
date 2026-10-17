# S1b — Replication of the S1 size difference with fresh seeds (Issue #37), preregistration v0.1

**Status: PROPOSED design, no seed drawn.** Requires a later-pass review by a different session before any implementation is merged, and before the S1b seed base is unlocked. Engineering/instrument question only: no statement about dimensional reduction, emergent geometry or spacetime.
**Date:** 2026-10-17. **Author:** Director `rd-claude-20261017T0846Z-21c3330dce46`. **Config:** [`configs/spectral_s1b.json`](../configs/spectral_s1b.json).
**Builds on:** [S1 prereg v0.2](SPECTRAL_S1_PREREGISTRATION.md) (frozen; its §7 NO-GO stands and is not revisited), [S1 pilot result](experiments/2026-10-17-s1-pilot.md), [post-hoc diagnostic](experiments/2026-10-17-s1-pilot-diagnostic.md).

## 0. Why this step (decision for Issue #37)

The S1 NO-GO had two different causes: (i) UST size equivalence was **undetermined** (eight trees per size give CIs ≈ ±0.07, far wider than ±0.03), and (ii) CAY showed a **resolved** larger-minus-smaller slope difference (+0.071, 90 % CI [+0.020, +0.122] at 128–1024). The post-hoc diagnostic found the local (t = 1) statistics correct at both sizes, a CAY difference of similar size already in the 8–64 window, and no change under source-degree post-stratification. Whether (ii) is a systematic N-dependence of the annealed estimator at t ≤ 4096 or a sampling fluctuation decides between two very different continuations:

- systematic → the annealed killed-ball estimator is not a size-stable instrument on CAY at these sizes; change method (quenched/per-source estimator, heat-kernel trace) or close the spectral track at this budget;
- fluctuation → a two-family S2 calibration design remains possible.

A direct replication at the pilot's sizes with fresh seeds and three times more trees is the smallest experiment that discriminates these, and the same run resolves (i) for UST at modest extra cost. Alternatives considered and **not** chosen now: a new estimator (larger change, does not explain the pilot), closing S1 (premature while (ii) is unexplained and cheap to test), more sources per tree instead of more trees (same CPU per unit variance reduction at S = 32, since source sampling dominates; trees are the independent units).

## 1. Questions

- **Q1 (primary, CAY):** does the larger-minus-smaller annealed window slope difference D_CAY = d̂_W(N = 2¹⁸) − d̂_W(N = 2¹⁶) at W = 128–1024 replicate on fresh trees?
- **Q2 (UST):** is D_UST = d̂_W(L = 256) − d̂_W(L = 128) at W = 128–1024 inside ±0.03 (90 % CI), as needed for any later S2?
- **Q3 (descriptive, CAY):** does the difference depend on N? Compare D(2¹⁶ − 2¹⁴) with D(2¹⁸ − 2¹⁶).

The window 128–1024 is fixed now. It was the pilot's headline window and one of its largest differences, so the pilot effect size is likely inflated (selection); this makes a positive replication *harder*, not easier.

## 2. Observable and method (unchanged from S1 v0.2 §3)

Same observable (annealed q̄(t) from q_v(t) = [P^(2t)]_vv, simple random walk, uniform sources without replacement, mean before logs), same killed-ball kernel with η = 10⁻⁴ certified bracket and radius rule, same per-source cap 2·10⁹ edge-steps (OVER_CAP recorded, never dropped), same window-slope formula, same tree-level delta-method influences ψᵢ and standard error as S1 P3/P5 (Welch–Satterthwaite t for the 90 % CI). **T = 4096 fixed** (the pilot measured cost at T = 4096 for every family; no ladder). Generators unchanged (CAY Prüfer, UST Wilson on the L×L torus, as D2/S1).

## 3. Design

| Family | Sizes | Trees × sources per size |
| --- | --- | --- |
| CAY | N ∈ {2¹⁴, 2¹⁶, 2¹⁸} | 24 × 32 |
| UST (torus) | L ∈ {128, 256} | 48 × 32 |

No RRT null (characterized in the S1 pilot). Engineering controls P0a–P0d of S1 v0.2 §5 are re-run unchanged as STOP gates before any S1b tree.

**Seeds:** `seed_base = 2036101701`, disjoint from every seed constant in `configs/`, `docs/`, `src/`, `tests/` (grep at `187349c`), in particular from S1 pilot 2036101301, S1 engineering 2036101397 and D2 2036101101. Rule: `np.random.SeedSequence([seed_base, i_family, i_size, i_rep])`, PCG64, family index CAY = 0, UST = 1, i_size indexes the S1b size list above; sources from a child of the same sequence (as S1). The S1b seed base is locked in code until this design and its implementation have passed review.

**Execution order:** round-robin over i_rep (rep 0 of every size, then rep 1, …) so that a stop leaves balanced partial data.

## 4. Budget and stops

- 1 core, ≤ 2 GiB (external `taskset` / `ulimit -v`), no Lightsail, no network during the run, no paid service. Any later S2 must use yet another seed base.
- **Projection from measured S1 pilot cost** (CPU-s per tree with 32 sources): CAY 2¹⁶ 82, 2¹⁸ 98, 2¹⁴ ≤ 82 (not measured; the R = 256 ball covers the whole tree); UST L = 128 12.6, L = 256 16.5. CAY ≈ 24 × 262 s ≈ 105 CPU-min; UST ≈ 48 × 29 s ≈ 23 CPU-min; controls ≈ 2 CPU-min; **total ≈ 130 CPU-min** (≈ 2.2 h wall on one core).
- **Hard stops:** 200 CPU-min total; per family 1.5× its projection. A stop yields PARTIAL; the §5 outcomes are computed only if every size has ≥ 16 CAY or ≥ 32 UST complete trees, otherwise BLOCKED (budget).
- Expected precision (from pilot influences, scaled by √(8/n)): SE(D_CAY) ≈ 0.017, SE(D_UST) ≈ 0.017, 90 % CI half-width ≈ 0.028 each. Consequence stated in advance: an equivalence outcome (CI inside ±0.03) is reachable only if the point difference is within about ±0.002; the design is therefore mainly able to **confirm** a difference of the pilot's magnitude (P(lower bound > 0) ≈ 0.99 if D = 0.07, ≈ 0.66 if D = 0.035) and will otherwise often return "undetermined".

## 5. Outcomes (fixed now)

For CAY at W = 128–1024:
- **C-REPLICATED:** 90 % CI of D_CAY entirely above 0 (same sign as the pilot).
- **C-EQUIVALENT:** 90 % CI entirely inside [−0.03, +0.03].
- **C-UNDETERMINED:** otherwise (including a CI entirely below 0, reported as such).

For UST at W = 128–1024: **U-EQUIVALENT** (90 % CI inside ±0.03) or **U-NOT-SHOWN**.

**Consequence for Issue #37 (fixed now):**
- C-REPLICATED → record "annealed killed-ball slope on CAY is size-dependent at N ≤ 2¹⁸, t ≤ 4096 (numerical observation)"; no S2 with this estimator; decide between a method change and closing the spectral track at this budget.
- C-EQUIVALENT and U-EQUIVALENT → an S2 two-family calibration preregistration may be drafted (fresh seed base, its own review); pooled-size analysis allowed only if both equivalences hold.
- Anything else → close S1 as **undetermined at this budget**; no further replication without a method change.

Q3 and all other windows (every admissible window as in S1 §3, with headroom per source) are reported descriptively, with no multiplicity-free claims. The pilot data are **not pooled** with S1b for any outcome.

## 6. Threats

- **Same estimator, same generators:** a defect common to pilot and S1b would replicate; P0a–P0d and the post-hoc t = 1 local-limit check (2(e−1)/e² ≈ 0.4651) do not test large-t behaviour beyond N = 4096. S1b will additionally report the t = 1 check and P(deg = 1) per size.
- **Normal-theory CI with heavy-tailed annealed means:** report the delete-one-tree jackknife SE and a whole-tree bootstrap percentile interval (4096 resamples, bootstrap seed 2036101799) beside the primary CI; if the jackknife SE exceeds the delta-method SE by > 25 % for a family, the outcome for that family is reported as UNRELIABLE instead of REPLICATED/EQUIVALENT.
- **Cost:** 2¹⁴ cost is projected, not measured; the per-family stop limits overrun.
- **Reviewer independence:** later-pass review by a different session before implementation merges; a different-model-family review before any interpretation beyond instrument calibration (Issue #37).

## 7. Provenance and implementation (later PR)

An `s1b` mode in `src/emergence_lab/spectral_s1_pilot.py` (or a thin wrapper) reading this config, reusing the S1 kernel and statistics unchanged, with tests that the seed lock, the round-robin order and the outcome rule work on engineering seeds. Result note `docs/experiments/YYYY-MM-DD-s1b-replication.md` with numeric/timing CSVs, manifest and an independent CSV-only check script.
