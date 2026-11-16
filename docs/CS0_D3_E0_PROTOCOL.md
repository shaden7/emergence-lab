# D3-E0/M0 v1 — frozen protocol (PROPOSED freeze; pilot and target NOT executed)

Status: **frozen-protocol candidate v1, proposed in a PR.** It becomes binding
only after a later-pass review (separate session) and merge. Even then it
authorizes **only the engineering pilot**; the target requires a separate,
committed, pinned authorization (§7). No D=3 target-cell mean or SD exists.
Design history and the reviewed identities: [design r0 + implementation r1](CS0_D3_E0_CONTROL_PROPOSAL.md)
(PR #80, PR #81). Config: [`configs/d3_e0_v1.json`](../configs/d3_e0_v1.json).
Code: `src/emergence_lab/d3_e0.py` (tools), `src/emergence_lab/d3_e0_campaign.py`
(pilot/target runner). Tests: `tests/test_d3_e0_impl.py`, `tests/test_d3_e0_campaign.py`.

## 1. Question and scope (unchanged from design r0)

At fixed input D=3 in the unit-height Minkowski Alexandrov diamond, does the
sign of the finite-N Myrheim–Meyer bias depend on the point ensemble as it does
at D=2? Arm A (E0): two tips + N−2 uniform interior points. Arm B (M0): N
uniform points, estimate conditioned on R>0. Same total N, different ensembles.
This is an **estimator/instrument control in one prescribed flat geometry**. It
is not a model comparison, does not answer Issue #37, and no outcome licenses a
statement about physical dimensional reduction. Hypotheses H_A, H_B (design r0)
are hypotheses, not assumptions.

## 2. Fixed elements

- Grid N ∈ {2,3,4,5,6,8,12,16,24,32}; inverse d(r) of f on [1,10]; every
  positive r is invertible on this grid (1/496 > f(10) = 1/2002).
- Deterministic cells A2, A3, B2: d ≡ 1, classified **BELOW** analytically, not
  in the test family. The family is the **17 stochastic cells**; Bonferroni
  family-wise α = 0.01 ⇒ two-sided per-cell **z = 3.4370**.
- Classification of a stochastic D=3 cell with Δ = mean(d) − 3 (arm B over R>0
  replicates) and i.i.d. SE: ABOVE if Δ − z·SE > 0, BELOW if Δ + z·SE < 0,
  else UNRESOLVED. The sign-reversal set is the N with A BELOW and B ABOVE.
- Reported alongside, never substituted: d(E[r]) (arm A exact from
  E[r] = f(3) + (1 − f(3))(2N−3)/C; arm B d(f(3)/P̂(R>0))) and the Jensen gap.
- Seed roots (numpy `SeedSequence`, spawn key (arm∈{A:0,B:1}, D, N); root =
  first 8 bytes of SHA-256 of `emergence-lab/d3-e0-v1/<name>`, fixed before any
  run, not chosen by outcome): pilot `1200746945068229832`, gates
  `4350303129085650063`, target `2631650520979328321`. Chunk size 4096.

## 3. Sampling rule (fixed R>0 count)

Each cell draws chunks of i.i.d. replicates in order until exactly n_c
replicates with R>0 are reached (truncating the last chunk at the n_c-th
positive). The stopping rule depends only on the R>0 indicators, which are
independent of the d-values of positive replicates, so the positives are
i.i.d. draws from the conditional law. Arm A has R>0 always (drawn = n_c).
Mean and variance by streaming Welford/Chan merging (freeze item (c)).

## 4. Engineering pilot (authorized by this protocol once merged)

Seed root: pilot. 1,000 R>0 replicates per stochastic cell at D=3 and at D=2
(arm B at N=3 draws ≈2,060; within the ≤2,000-per-cell intent up to the R=0
draws). Pilot also executes the quadrature and sampler gates to time them.
Cap: **60 CPU s**, 512 MiB peak RSS. Output `pilot_record.json` with per-cell
SD̂(d), P̂(R=0) (D=3), CPU s per positive replicate (D=3 and D=2), gate CPU, the
derived n_c and the budget status. **Blinded:** no cell mean is written; pilot
numbers are never reported as results or pooled with target data. Pilot timing
on the executing host replaces the sandbox timings of r1 (freeze item (d)).

## 5. n_c rule (frozen)

n_c(cell) = max(**10^5**, ⌈(4·SD̂/0.01)²⌉), i.e. the 4-SE half-width ≤ **0.01**
in dimension units, counted in R>0 replicates. The matching D=2 control cell
uses the same n_c (≥10^5; detects a pipeline bias ≈0.011 with power ≥0.9 at
SD ≤ 0.68). Precision (4 SE) and decision (z = 3.4370) deliberately differ.
Budget projection = 1.25 × (Σ n_c·(cpu/positive at D=3 + at D=2) + gate CPU).
If > 600 CPU s, all n_c are scaled down by one common factor (never below
10^5) and the status is CAP_BINDS (achieved half-widths are reported). If even
the 10^5 floor does not fit: BUDGET_INFEASIBLE, no target run under v1.

## 6. Target gates and outcomes

One cap covers everything — quadrature, sampler gates, D=2 control and D=3
cells: **600 CPU s** (soft RLIMIT_CPU; exceeding it ⇒ INVALID) and
**512 MiB** peak RSS (checked from `getrusage`; exceeding ⇒ INVALID).

1. Quadrature (mpmath 1.3.0, 40 digits): q_pair = f(D)/2 and q_chain = χ_3 at
   D=2,3; D=2 q_chain = 1/36, q_down = 1/9; quadrature D=2 B3 and A5 cells vs
   the archived exact table; all within 1e−11.
2. Sampler agreement at D=3 (gates root): pair probability vs f(3) for the
   direct and rejection samplers, 20,000 pairs each, |z| ≤ 4; R-distribution
   chi-square between samplers at N=3,4,8, 6,000 replicates each, p > 10^−3.
3. D=3 MC vs quadrature: target cells B3 and A5 within 4 SE of the quadrature
   values (≈2.163007, ≈1.408768).
4. D=2 positive control: all 17 stochastic D=2 cells within 4 SE of
   `docs/experiments/d2-e0-v1-20261111/ensemble_comparison.csv`.

Outcome: **INVALID** if any gate, the CPU cap, RSS cap or provenance fails;
**UNDECIDABLE_AT_BUDGET** if any of the 17 stochastic D=3 cells is UNRESOLVED
(stricter than r0's "N ≥ 4": B3 is now included; it is the only stochastic
N=3 cell); else **COMPLETE** with the full table. All cells, failed gates and
negative outcomes are retained. No rerun with a larger budget or new seeds
without a new reviewed protocol version.

## 7. Target authorization (separate commit, not part of this freeze)

`run_target` refuses unless a committed JSON authorization exists with: mode
`target`, an id, a future `expires_utc`, SHA-256 of this file and of the config,
git blob ids at HEAD of the pinned paths (this file, config, `d3_e0.py`,
`d3_e0_campaign.py`, `causal_set_mm.py`, the archived D=2 table), a clean
worktree for those paths, and the path + SHA-256 of a committed
`PILOT_COMPLETE` pilot record whose status is not BUDGET_INFEASIBLE. The runner
then requires the pinned `.[reference]` extra (`mpmath==1.3.0`; freeze item
(a)) and writes `manifest.json`, `cells.csv` and `raw_counts.npz` (per-replicate
R as uint16) to a fresh output directory. Archive: manifest and cells in Git;
the raw NPZ in Git if ≤ 5 MB, otherwise as a release asset referenced by hash.

## 8. Freeze-item resolutions and open caveats

- (a) mpmath pin enforced at runtime (`require_reference_extra`), tested.
- (b) **Open:** the χ_k closed form (Meyer 1988 as reviewed in Surya 2019) is
  still **not checked against the primary text**; the 2026-11-16 attempt could
  not fetch arXiv:1903.11544. It is an extra anchor only: the quadrature (gate
  1) and its D=2 reproduction of the archived Mahonian-exact values do not
  depend on it, and χ_k was checked analytically at D=2 (1/(k!)²) and k=2
  (f(D)/2) in the 2026-11-15 review. A reviewer may accept or require it.
- (c) Welford/Chan accumulation in `estimate_cell` and `run_cell`, tested.
- (d) Host timing re-measured by the pilot (§4) before n_c is fixed.
- Resource enforcement is process-level (soft RLIMIT_CPU + post-hoc RSS
  check), weaker than the D2-E0 supervisor; acceptable because the work is
  pure in-process numerics with no subprocess, network or file input beyond
  the pinned table. No Lightsail, deployment or paid API is involved.
- Limits from design r0 stand: no D=4, no other estimator, no Poisson-N, no
  full-CS0 or Issue #37 claim.

## 9. Later-pass review checklist

Check: seed-root derivation; the fixed-positive stopping argument (§3);
n_c/budget arithmetic and the CAP_BINDS/INFEASIBLE branches; pilot blinding
(no mean written); authorization refusal paths; that gates 1–4 cannot pass a
known-wrong pipeline (wrong D and arm-A offset negative controls from the
2026-11-15 review); and caveat (b). Record PASS/REVISE in the PR.
