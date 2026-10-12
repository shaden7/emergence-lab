# Pilot B stage-2 blind run: result (prereg v1.0-r1), proposed

**Status:** one-shot blinded calibration result, **later-pass review PASS** (2026-10-12, see the review section at the end). This is methodology on stipulated linear ring dynamics, **not a physics result** and not a statement about signalling or causality in nature. The decision record is [PILOT_B_DECISION.md](../PILOT_B_DECISION.md).

## What ran

- Design: [Pilot B preregistration v1.0-r1](../PILOT_B_BLINDED_INTERVENTION_PREREGISTRATION.md), blob `dd5dbef`. The config `configs/pilot_b.json` has SHA-256 `3fc24afa…6d2e`. The frozen stage-1 code blobs are listed in `blind_archive_manifest.json`. The stage-1 merge was `7780fc1`, at 2026-10-10T21:09:59Z.
- Execution: GitHub Actions run [38181108016](https://github.com/shaden7/emergence-lab/actions/runs/38181108016). It was `workflow_dispatch` by the owner on `main` `0048198`, started 2026-10-11T22:36:42Z, and all 12 steps succeeded.
  - It is the **only** run of `pilot-b-blind-run.yml` (`total_count` = 1).
  - The run used Python 3.12.15, NumPy 2.5.3 and SciPy 1.18.1. Analysis CPU was 0.65 s.
- Beacon: drand quicknet round **R = 32983212** (2026-10-11T21:10:00Z), the first round ≥ 24 h after the stage-1 merge. The chain hash is `52db9ba7…e971`. The BLS signature was verified, and `randomness = SHA-256(signature)` was checked.
  - Blind key: `faa3949b…5c8d` = SHA-256(`pilot-b-v1|32983212|` ‖ randomness), as specified in §6.3.
- Steps in the workflow, in order:
  - A preflight checked the round pin, the frozen code, the prereg and config pins, and that the time was ≥ R plus margin.
  - The dev set reproduced the stage-1 decision digest `6da5c8e3…`, and two dev invocations were byte-identical (B-G6).
  - The blind evaluation ran exactly once.
  - The outputs were published as the release [`pilot-b-blind-v1`](https://github.com/shaden7/emergence-lab/releases/tag/pilot-b-blind-v1) and re-verified after download. *(Review correction: GitHub reports this release as `immutable: false`, so its assets are not platform-immutable; integrity rests on the SHA-256 digests pinned in Git, which all five assets match.)* Byte copies are committed in `2026-10-11-pilot-b-blind/`.
- Decision digest: `c9129efc…9bb1`.

## Director checks (this session, not the producer of the run; the same model family wrote the design and the code)

Script: `docs/experiments/pilot_b_blind_check.py`. Environment: Director sandbox, Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1.

- The SHA-256 of `rows.csv`, `result.json` and `manifest.json` match the archive manifest. The release assets were downloaded through the REST asset API.
- The blind key was recomputed from the beacon file and equals the logged key.
- **Decision reproduction:**
  - Locally, `pilot_b --phase dev` reproduces the dev digest `6da5c8e3…`.
  - `pilot_b_blind execute` with the same beacon reproduces the blind decision digest `c9129efc…` exactly.
  - The local `rows.csv` bytes differ from the CI bytes only in last-ulp values of D for N1 (max |ΔD| = 2.2·10⁻¹⁶; `expm` on a different platform). All 1320 detection flags and all verdicts are identical.
  - This reruns the frozen code; it is not an independent implementation.
- **Noise calibration:** on the 674 grid cells whose analytic response is exactly 0, z has mean 0.047 and sd 1.051, KS against N(0,1) gives p = 0.475, and 2 cells have |z| > z₂ against 1.02 expected (Poisson P(X ≥ 2) = 0.27). The largest |z| is 4.00. This is consistent with the stipulated Gaussian detector model. It says nothing about a real detector.

## Gates (prereg §8), numbers from `result.json`

| Gate | Result | Basis |
| --- | --- | --- |
| B-G0 exact references | **PASS** | Two-path max \|Δ\| = 1.1·10⁻¹⁴ ≤ 10⁻¹², and every exterior cell of every P instance is exactly 0. |
| B-G1 soundness | **PASS** | 1 of 24 P instances is `H0_REJECTED`, against a threshold of ≤ 3. The rejection is #37 (S1, k = 4): one exterior cell (t = 2, r = 16, true S = 0) has z = −4.00. |
| B-G2 speed soundness | **PASS** | 2 of 16 strict instances overestimate, against a threshold of ≤ 3. In #35 (S3, k = 2), r̂(2) = 8 > 4, from one cell at true S = 0 with z = −3.64. In #37, r̂(2) = 16 > 8, from the same cell as in B-G1. |
| B-G3 null controls | **PASS** | All C1 instances detect r = 0 at every t, and 0 of 8 C instances are spurious (≤ 2 allowed). |
| B-G4 power | **PASS, N2 only** | The 5 detectable N instances (analytic max exterior \|S\| ≥ 1.146·10⁻⁴) are all N2: #6, #15, #17, #18 and #20. All 5 are `H0_REJECTED` (≥ 90 % required). The pass is not vacuous. |
| B-G5 vocabulary | **PASS** | Only `NO_RESPONSE`, `CONSISTENT_WITH_H0` and `H0_REJECTED` are used. All 11 undetected N instances are listed below. |
| B-G6 provenance | **PASS** | The manifest has the prereg blob, config hash, code commit, beacon, key, versions, per-instance rows, CPU time and output hashes. The dev outputs were byte-identical in CI; the workflow `cmp` step succeeded. |

## Undetected non-strict instances (`CONSISTENT_WITH_H0`), reported as *undetected*, never as strict

The detection limit is |S| ≈ 5.73·10⁻⁵.

| # | Class | Parameters | Analytic max exterior \|S\| on the grid |
| --- | --- | --- | --- |
| 2 | N1 | γ = 0.424 | 3.5·10⁻⁶ |
| 11 | N1 | γ = 0.596 | 2.0·10⁻⁵ |
| 16 | N1 | γ = 0.204 | 6.7·10⁻⁸ |
| 26 | N1 | γ = 0.785 | **7.4·10⁻⁵** (1.29× the limit, below the 2× "detectable" bar) |
| 29 | N1 | γ = 0.205 | 6.9·10⁻⁸ |
| 8 | N3 | d = 88, k = 2 | 0 (shortcut site not on the grid) |
| 19 | N3 | d = 36, k = 1, ε = 2.1·10⁻³ | 0 (not on the grid) |
| 22 | N3 | d = 29, k = 1 | 1.2·10⁻⁷ |
| 24 | N3 | d = 91, k = 1, ε = 5.6·10⁻³ | 0 (not on the grid) |
| 27 | N3 | d = 93, k = 2, ε = 4·10⁻⁴ | 0 (not on the grid) |
| 30 | N3 | d = 63, k = 2, ε = 2·10⁻⁴ | 0 (not on the grid) |

Detection by class, with Wilson 95 % intervals (descriptive):

| Class | Detected | Wilson 95 % |
| --- | --- | --- |
| N1 | 0/5 | [0, 0.43] |
| N2 | 5/5 | [0.57, 1] |
| N3 | 0/6 | [0, 0.39] |

## Interpretation and limitations

- *Numerical observation:* on this one blinded draw, the frozen Bonferroni bounded-speed test kept its false rejections (1/24) and speed overestimates (2/16) within the preregistered tolerances. It caught every violation that was large relative to the noise, and it never asserted strictness.
  - Both errors come from single zero-signal cells at |z| = 3.6–4.0. The zero-cell calibration check shows no excess, so this is the expected Bonferroni behaviour, not a bias.
- **Power was exercised only on N2**, the power-law stencil, exactly as §10 anticipated.
  - Heat-type violations (N1) and sparse shortcuts (N3) went undetected. For 5 of the 6 N3 instances the shortcut does not reach any measured grid site, so it is *invisible by construction*.
  - The test therefore says little about weak or sparse non-locality. "No violation detected" is a statement about this grid and budget only.
- One draw of 40 instances gives wide intervals. B-G1 and B-G2 can only detect gross miscalibration.
- Known σ and Gaussian white noise are stipulated. Unknown-σ and correlated noise are untested.
- The blinding covers the specific instances, not the family design. Generator, analyst, workflow and this check were all written by the same AI model family (§6.5).

## Later-pass review (2026-10-12, `rd-claude-20261012T0205Z-64ccb703e8eb`)

This session produced neither the run, the result note nor the decision record. It is the same model family that designed, implemented and checked Pilot B, so this is an AI-mediated later-pass review, not independent peer review.

Script: [`pilot_b_review_independent.py`](pilot_b_review_independent.py). It does not import `emergence_lab`. Environment: Director sandbox, Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1, py_ecc 8.0.0.

- **Provenance.**
  - All five release assets' GitHub SHA-256 digests equal the committed copies.
  - `randomness` = SHA-256(`signature`), and the key is recomputed per §6.3.
  - Quicknet arithmetic (genesis 1692803367, period 3 s): round 32983212 is at 1791753000 = 2026-10-11T21:10:00Z. It is the first round at or after the stage-1 merge (`7780fc1`, 2026-10-10T21:09:59Z) plus 24 h.
  - The frozen blobs of prereg, config, `pilot_b.py`, `pilot_b_analyst.py` and `pilot_b_beacon.py` are identical at `7780fc1`, `0048198` and current `main`.
  - `pilot-b-blind-run.yml` has exactly one run (38181108016, `workflow_dispatch` by the owner, success).
- **Frozen-code rerun** (not independent):
  - The dev digest `6da5c8e3…` is reproduced.
  - `pilot_b_blind execute` with the committed beacon verifies the BLS signature locally (`signature_verified: true`) and reproduces the blind decision digest `c9129efc…`.
  - The gate blocks differ from CI only in last-ulp `max_abs_exterior_S` for four N1 instances (`expm`).
- **Own re-derivation from `rows.csv`:**
  - z = D/SE, z₁ = 2.8653 and z₂ = 3.1718 are recomputed.
  - All detection flags (0 mismatches), all 40 verdicts and all r̂(t) are reproduced.
  - The class counts match §3.
  - B-G1 gives {37}, B-G2 gives {35, 37}, B-G3 gives C1 r = 0 detected and 0 spurious, and B-G5 gives the same 11 undetected N instances.
- **Own propagators from the logged parameters:**
  - Direct circular convolution for S1/S3/C2, the leapfrog recursion for S2, the Fourier heat kernel for N1, the FFT power-law stencil for N2 and a dense matrix power for N3 reproduce every logged S_true (max |ΔS| 1.3·10⁻¹⁵).
  - Every exterior cell of every P instance is exactly 0.0.
  - The B-G4 detectable set is {6, 15, 17, 18, 20} with the prereg bar 2 × 5.73·10⁻⁵. The code's bar of 2 × 5.7306·10⁻⁵ gives the same set, since no instance lies between the two.
  - Limitation: the instance parameters themselves are re-derived from the key only by the frozen-code rerun, not by an independent generator.

**Findings:**
1. *Corrected in this note and in the decision record (wording only):* "immutable release" was replaced by a statement of the actual `immutable: false` status and the Git-pinned digests.
2. *Non-blocking:* B-G2 compares r̂(t) with k·t, as preregistered. For S3 this is the radius bound, not the true support, which interference zeros can make smaller. It is conservative for the overestimate gate, so it is not a problem.

**Decision: PASS.** The gates and decision rule were applied as preregistered. The GO is scoped exactly as in the decision record. There is no physics claim.

## Next

1. Possible follow-ups, *proposals only, not authorised by this result*: an unknown-σ or correlated-noise variant, and a grid-coverage design for sparse shortcuts. Each needs its own preregistration.
