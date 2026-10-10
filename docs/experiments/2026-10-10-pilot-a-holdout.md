# Pilot A, holdout evaluation (one-shot, unchanged)

**Protocol:** [PILOT_A_CAUSAL_PROPAGATION_PREREGISTRATION.md](../PILOT_A_CAUSAL_PROPAGATION_PREREGISTRATION.md) v1.0, SHA-256 `c8061aed…` (re-verified before the run).
**Executing commit:** `c4f2793c3cb8fd4d93cd4d9ed69c9d5ae800bb11` (PR #23 merge). Config `configs/pilot_a.json`, SHA-256 `a55fcfa8…` (re-verified).
**Command:** `GIT_SHA=c4f2793… python -m emergence_lab.pilot_a --phase holdout --allow-holdout --output <dir>`
**Director session:** `rd-claude-20261010T145640Z-d84b0e`. Run at 2026-10-10T14:58:41Z, local cloud sandbox, Python 3.13.16 / NumPy 2.5.3, Linux x86_64. Nothing ran on Lightsail.
**Resources:** 4.3 s CPU, 2.7 s wall, 81 MB max RSS. This is well inside the registered budget (0.5 vCPU, 1.5 GiB, 30 min).
**Artifacts (in Git, small):**
- [`2026-10-10-pilot-a-holdout-result.json`](2026-10-10-pilot-a-holdout-result.json), SHA-256 `5530e17e…`. It contains the full manifest, all rows, fronts and controls.
- [`2026-10-10-pilot-a-holdout-rows.csv`](2026-10-10-pilot-a-holdout-rows.csv), SHA-256 `a99bdb4d…`. This matches `rows_csv_sha256` in the manifest.

## Pre-run checks (same session, before the holdout)

- `pytest -q` on `main` `a005277`: 207 passed. `a005277` differs from `c4f2793` only in `docs/RESEARCH_STATE.md`.
- Development grid reproduced: `rows.csv` `7a2ff47c…`, byte-identical to stages 1 and 2.
- The protocol and config hashes match the pins.
- The A3/A2/A4 decision code was reread. A3 cannot be vacuous: an empty registered or cone-exterior witness set fails. A2 requires a non-empty set of W cells outside the cone.
- **Launch incident, recorded for completeness:** the first launch attempt was wrapped in `/usr/bin/time -v`. That binary does not exist in this sandbox. The shell returned exit 127 before Python started, so no output directory was created and **no holdout cell was computed**. The single real evaluation followed 10 s later without the wrapper. The holdout was evaluated **once**. It was not re-run afterwards, not even for a determinism check.

## Result (numerical observation)

**Holdout grid:** t ∈ {0.75, 1.5, 3}; r ∈ {0, 3, 5, 7, 11, 15}; Q/CA on L ∈ {512, 1024}; CA n ∈ {3, 5, 12}. That gives 108 cells:
- 58 `match`
- 33 `analytic_zero_ok`
- 17 `censored` (S_ref < 1e-8, never reported as zero)
- 0 `front_excluded`
- **0 `mismatch`**
- 0 `analytic_zero_violated`

| Criterion | Holdout result | Evidence |
| --- | --- | --- |
| A1 (N1) | pass | Same seeded control as development (seed 2027050101; corr 0.497; remote Δ = 0 for all 4000 pairs; local Δ = 1). N1 does not depend on the grid, so this is **not new evidence**. |
| A2 strict support (W, CA) | pass | 14 W cells with \|r\| > a + t: all S = 0 from the Courant-1 leapfrog. 16 CA cells with d > n: all exactly 0. No theorem zero is violated. |
| A3 nonstrict witnesses | pass | Registered (t, r) = (1, 4), (1, 6), evaluated directly: H 5.932806e-3 / 4.815957e-5; Q (L = 512, 1024) 1.155709e-3 / 1.445835e-6. All are `match`. Cone-exterior H/Q cells: 25 `match` (smallest S_ref 5.5e-8) and 17 `censored`. None is mismatched and none is called zero. |
| A4 Q vs finite-ring Fourier | pass | All 36 Q cells are `match` or `censored`. Max normalisation error is 1.1e-15. Ring minus Bessel line is ≤ 5.6e-16 on this grid, so wrap-around is negligible at L ≥ 512 and t ≤ 3. |
| A6 threshold fronts | reported | 27 H/Q fronts, r_η for η ∈ {1e-3, 1e-6, 1e-9}. They are labelled threshold diagnostics of nonstrict models, never support boundaries. |
| **A7** (A1–A4 on the holdout without retuning) | **pass** | Deterministic error budget: the max relative error over matched cells is 2.1e-13, against a tolerance of 1e-6. No confidence interval was invented. |

**Not evaluated on the holdout, by design or as an open item:**
- A5 (N2 shortcut) is a development-only control in this code. Its development result passed.
- N5 (measurement noise) is not implemented, so the optional noise part of A7 is **not done**.
- N4 is the solver-artifact demo. It is unchanged and does not depend on the grid: forward Euler gives exactly 0 at r = 6, while the continuum value is 4.8e-5.

## Interpretation and limits

- **Evidence level:** numerical observation about a measurement and classification procedure. It is **not a physics result**. The support classes of W, H, CA and Q are mathematical inputs (`SUPPORT_CLASS`), not something measured here. The holdout shows that the pipeline's numerical paths and the A3 rule reproduce those known classes on unseen (t, r, L) without a mismatch.
- H1 (method hypothesis) **survived a preregistered holdout test**. That supports H1; it does not prove it. All four families are textbook cases with closed forms, so this test cannot discriminate between a good metric and one that only works where references exist.
- **Weak spots that I found and state rather than hide:**
  - Only 1 W cell on the holdout is non-zero (t = 3, r = 3, S = 0.5). The independent W solver therefore mostly checks zeros on this grid.
  - A1 reuses the development control.
  - The A3 rule for the cone exterior was clarified after the development run but **before** any holdout evaluation (PR #23). It was not tuned to holdout data.
  - All reviews, including this one, are AI-mediated by the same model family. This is a later-pass check, not independent peer review.
- Per the protocol's main decision rule: A1–A4 hold on the development grid and the holdout, so **the metric is validated as a reference calibration within this scope**. A5 passed on development. A7 is met without its optional noise part. Model-comparison capability for non-textbook models is **not** established by this run.

## Next single step

Either:
- implement N5 (measurement noise, 20 independent realisations per σ/threshold) to complete A7's optional part; or
- record a scoped Pilot A decision (reference calibration GO, with limits) before any exploratory model family is run with this metric.
