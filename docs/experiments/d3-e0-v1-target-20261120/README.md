# D3-E0/M0 v1 target run — 2026-11-20 (PROPOSED archive; awaiting later-pass review)

- **What:** this is the single target run authorized by `docs/experiments/d3-e0-v1-target-auth-20261119/authorization.json`. That file was merged in PR #84 as `835eac2` after later-pass review r1 PASS.
- **How it ran:**
  - Executed once, on a clean worktree of `main` at `835eac22b0adbe49e5c4cb554fcc52c07dc6d2f8` (`git_dirty_pinned: false`).
  - Seed roots: gates `4350303129085650063`, target `2631650520979328321`.
  - Command: `python3 -m emergence_lab.d3_e0_campaign target --authorization docs/experiments/d3-e0-v1-target-auth-20261119/authorization.json --output <fresh dir>`. The outputs were copied here unchanged.
  - One earlier invocation wrapper (`/usr/bin/time`) did not exist on the host. That shell call exited 127 before Python started, so no output directory was created and no run took place.
- **Host:** Linux x86_64 cloud sandbox with 2 CPUs. Python 3.13.18, numpy 2.5.3, scipy 1.18.1, mpmath 1.3.0.
- **Files:**
  - `manifest.json`: SHA-256 `c913c808…23a0`.
  - `cells.csv`: SHA-256 `ba838064…5d14`.
  - `raw_counts.npz`: per-replicate R as uint16, 2.35 MB, SHA-256 `757b4f99…5954`. This matches `raw_counts_sha256` in the manifest.
- **Status `COMPLETE`:**
  - Resources: 20.97 CPU s (cap 600) and 271.8 MiB peak RSS (cap 512).
  - Gates 1–4 all passed:
    - Quadrature: every error is ≤ 7e-16, against a tolerance of 1e-11.
    - Sampler: pair |z| ≤ 1.31; the chi-square p-values are 0.073, 0.091 and 0.656.
    - D=3 MC vs quadrature: z(B3) = −0.78 and z(A5) = −1.38.
    - D=2 positive control: max |z| = 1.95 over the 17 cells.

## Numerical observation (scoped; Bonferroni z = 3.437; n_c = 10^5 R>0 replicates per cell)

| N | arm A mean d (Δ) | label | arm B mean d given R>0 (Δ) | label |
|---|---|---|---|---|
| 3 | 1 (deterministic) | BELOW | 2.1618 (−0.838) | BELOW |
| 4 | 1.2196 (−1.780) | BELOW | 2.6859 (−0.314) | BELOW |
| 5 | 1.4081 (−1.592) | BELOW | 2.9634 (−0.037) | BELOW |
| 6 | 1.5627 (−1.437) | BELOW | 3.0949 (+0.095) | ABOVE |
| 8 | 1.7941 (−1.206) | BELOW | 3.1694 (+0.169) | ABOVE |
| 12 | 2.0838 (−0.916) | BELOW | 3.1224 (+0.122) | ABOVE |
| 16 | 2.2608 (−0.739) | BELOW | 3.0849 (+0.085) | ABOVE |
| 24 | 2.4640 (−0.536) | BELOW | 3.0514 (+0.051) | ABOVE |
| 32 | 2.5792 (−0.421) | BELOW | 3.0347 (+0.035) | ABOVE |

The cells A2, A3 and B2 are deterministic, with d ≡ 1. All 17 stochastic cells resolved, so none is UNRESOLVED. Sign-reversal set: **N ∈ {6, 8, 12, 16, 24, 32}**. The SEs are in `cells.csv`; the largest is 0.0025. d(E[r]) and the Jensen gap are reported in `cells.csv` alongside these values, not substituted for them.

**Interpretation (hypothesis-level, not yet reviewed):**
- The design-r0 hypotheses H_A (arm A below 3 at every grid N) and H_B (arm B above 3 for N ≥ N_B) are consistent with this run, with N_B = 6 on this grid.
- At D=2 the archived table has the no-endpoint conditional mean above 2 from N = 4 onward. The qualitative ensemble dependence of the sign therefore recurs at D=3, with a later onset.
- This is an estimator/instrument control in one prescribed flat Alexandrov diamond. It is not a model comparison and does not answer Issue #37. It licenses no statement about physical dimensional reduction (protocol §1).

**Not done:**
- No later-pass review of this archive yet.
- No independent reimplementation.
- No rerun: v1 allows none.
