# Pilot B stage 1 — implementation and development-set check (2026-10-10)

**Status:** stage-1 code accepted in a later-pass review (PASS, session `rd-claude-20261010T205622Z-908995`, [record](https://github.com/shaden7/emergence-lab/pull/30)) and integrated via PR #30; the merge commit and the resulting blind round R are recorded on the PR. Development key only: **no blind evaluation has run.**
**Session:** `rd-claude-20261010T195637Z-0eea4a` (producer of this code; a different session must do the later-pass review).
**Frozen design:** [preregistration v1.0-r1](../PILOT_B_BLINDED_INTERVENTION_PREREGISTRATION.md) (Git blob `dd5dbefe950add3341366224b76ba179326282c8`), [config](../../configs/pilot_b.json) (SHA-256 `3fc24afa33c31c91eb0f96be8ac7b785a7abb13083725fd39d6df406640d6d2e`). Both are verified at run time; any change fails closed. Neither file is modified by this stage.
**Scope:** methodology only. Every instance is a stipulated linear dynamics on a ring. Nothing here concerns physical spacetime, signalling or causality in nature.

## What was implemented

| Path | Role |
| --- | --- |
| `src/emergence_lab/pilot_b.py` | `instances(key)` generator, noisy `Oracle`, two exact reference paths, evaluator for B-G0…B-G5, manifest (B-G6), CLI (`--phase dev`; `--phase blind --allow-blind --beacon` refuses unverified beacons) |
| `src/emergence_lab/pilot_b_analyst.py` | Frozen decision rule (§5). Imports only `math` and NumPy; it sees an instance only through `oracle.readouts(t, r, arm)` |
| `src/emergence_lab/pilot_b_beacon.py` | drand quicknet pins, round↔time arithmetic, `randomness == SHA-256(signature)` check, BLS (G1 signature / G2 key, RFC 9380 hash-to-G1) verification with `py_ecc`, relay comparison |
| `tests/test_pilot_b.py` | 23 tests: pins, z values, analyst import isolation (AST and subprocess), generator determinism/counts, both reference paths for every class with exact exterior zeros, noise-free oracle exactness, budget enforcement, analyst verdict boundaries at z₁·SE, dev gates + byte identity, decision digest invariant under a forced BLAS kernel, blind-phase refusal, beacon arithmetic, BLS self-test |
| `.github/workflows/ci.yml` | Dev run twice + `cmp` + notice annotation |
| `.github/workflows/pilot-b-beacon-check.yml` | PR / dispatch job: compares the pins with four relays' `/info` and BLS-verifies the latest round |

`scipy` was added as a runtime dependency (`expm` for the N1 matrix path, as §8 B-G0 names). `py_ecc` was added to the `test` and new `beacon` extras.

### Implementation choices the preregistration leaves open (fixed here, before any blind key exists)

- **Parameter stream:** one `default_rng(SeedSequence([key_int, 1]))`. Classes are drawn in config order S1, S2, S3, C1, C2, N1, N2, N3, with per-class draw order as coded in `_draw_params`. Then `perm = rng.permutation(40)`, and instance `i` is the `perm[i]`-th drawn instance.
- **Key integer:** `key_int = int.from_bytes(key[:16], "big")` for the parameter stream and the noise streams (§7 uses `key_int` for both).
- **Noise streams:** cell index `c = time_index·11 + site_index`; arm index control = 0, do = 1.
- **Circulant convention:** `x_{t+1}(i) = Σ_j a_j x_t(i−j)`. Ring Laplacian `(Δu)(i) = u(i+1) + u(i−1) − 2u(i)`. N3 symmetric stencil: draw `w_0…w_k`, mirror, normalise.
- **Control arm:** starts from 0, so its noise-free value is 0 for every linear member. For C2 the do arm equals the control arm, so S ≡ 0. The S1-type dynamics drawn for C2 is recorded but cannot affect any readout.
- **B-G2 for S2:** the true radius is `k = 1` per step.
- **B-G3 spurious definition:** exactly as in §8. C1 also counts an exterior detection under z₁, which implies `r > 0`.

## Development-set run (key `SHA-256(b"pilot-b-dev-2027101101")` = `266f9a9f…34c9f6`)

**Actually executed:** local cloud sandbox (Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1). Two invocations produced byte-identical `rows.csv` (SHA-256 `fa657d024027ce3e587472912e522da61f44f7806b9f662f21f9a72a8cd53404`, 1 + 1,320 rows) and `result.json` (`43d87373f13945512e049fc0b159da8cdbee8d76001a9eab8fd23afe5599398a`). The **decision digest** is `6da5c8e328ffad3be6172bebf9c0a7a016db88a9abc943e958636724a5fd9f50` (see below). CPU 0.6 s, max RSS 68 MiB, outputs 152 KiB. These are inside the §9 budget (120 s / 512 MiB / 5 MiB).

### Cross-machine reproducibility finding (raised by the first CI run, fixed in reporting)

The first PR head `f8af39b` ran green in CI ([push 38082297835](https://github.com/shaden7/emergence-lab/actions/runs/38082297835), [PR 38082317954](https://github.com/shaden7/emergence-lab/actions/runs/38082317954)). Inside each job the two invocations were byte-identical (`cmp` passed). Across jobs, however, the `rows.csv` digests differed: `db7482b5…` and `0f8f8f04…`, both on Python 3.12.15 / NumPy 2.5.4, versus `fa657d02…` locally. The artifacts could not be downloaded from the sandbox, so the cause was reproduced locally instead. Forcing different OpenBLAS kernels (`OPENBLAS_CORETYPE` = SkylakeX / Haswell / Sandybridge / Prescott) gives four different `rows.csv` digests. Across the four:
- max |ΔS| ≤ 1.7e-15, max |ΔD| ≤ 1.6e-15, max |Δz| ≤ 8e-11;
- identical per-cell detections, verdicts, r̂ and gate results;
- the closest |z| to either threshold is 0.027 away.

`rows.csv` records floats with `repr`, so its bytes depend on last-bit BLAS rounding, which follows the runner's CPU.

**Fix (reporting only; no rule, grid or threshold changed):** the manifest now carries `decisions_sha256`. It hashes per-cell detections, verdicts, r̂ and gate outcomes, and CI prints it. A test asserts it is unchanged under a forced Prescott kernel. B-G6's literal requirement (byte identity of two invocations *in the same environment*) holds. Cross-machine comparison should use the decision digest. For stage 2, the archived blind outputs are whatever the single blind run produced, and re-runs elsewhere are compared by decision digest. The CI annotation on the new head records whether the Python 3.12 decision digest equals `6da5c8e3…`.

| Gate | Dev outcome | Detail |
| --- | --- | --- |
| B-G0 | PASS | max \|matrix − spectral\| = 1.1e-14 over 40 instances × 3 t × 256 sites; every exterior site (ring distance > 4t) of all 24 P instances is exactly 0.0 in the matrix path; noise-free oracle exact (unit test) |
| B-G1 | PASS | 0 / 24 H0-satisfying instances rejected |
| B-G2 | PASS | 1 / 16 strict instances overestimated (instance 36, S2, c² = 0.427: cell t=4, r=12 has S = 0 exactly and z = 3.46 > z₂ = 3.1718; an interior false positive at the nominal rate, not an exterior rejection) |
| B-G3 | PASS | all 4 C1 detect r = 0 at every t; 0 / 8 spurious C instances |
| B-G4 | PASS | 6 detectable N instances (5 N2 and 1 N3 with d = 24, ε = 9.8e-3): 6 / 6 `H0_REJECTED` |
| B-G5 | PASS | verdicts ⊆ {NO_RESPONSE, CONSISTENT_WITH_H0, H0_REJECTED}; 10 undetected N instances listed with analytic max exterior \|S\| |
| B-G6 | dev part PASS | manifest with pins, versions, CPU, output hashes and decision digest; byte identity on two invocations in the same environment. The `code_commit` field is `null` locally and set from `GIT_SHA` in CI |

**Undetected non-strict dev instances (descriptive, the intended lesson, not a gate):** all five N1 (γ = 0.21…0.58; max exterior \|S\| 8e-8…1.7e-5, every one below the detection limit 5.73e-5) and five N3 whose shortcut site `d ∈ {20, 49, 73, 84, 94}` puts every grid exterior cell at exactly S = 0 within t ≤ 4. These are **undetected violations**, not evidence of bounded support. Rejection counts by class: N2 5/5, N3 1/6 (Wilson 95 % [0.03, 0.56]), N1 0/5 ([0, 0.43]).

**Independent cross-check (separate script, not the module's reference code):** direct time-stepping with `np.roll` (Taylor series with 80 terms for N1, the leapfrog recursion for S2, explicit shortcut update for N3) reproduced every `S_true` in `rows.csv` to 6.1e-14. It also re-checked all parameter ranges, the symmetry of the N3 stencils, ε < w₀, and the class counts. It shares the parameter draws, so it checks propagation and reporting, not the generator's sampling.

**Evidence level:** numerical check of an implementation on a public development key. It is not the blind test and not a physics result. Same model family wrote the design, code and this check (see prereg §6.5).

## Beacon (prereg §6.3) — status

- **Implemented and unit-tested locally:**
  - round arithmetic: round 1 at genesis, `round_time(R) = genesis + (R−1)·period`, and R is the first round with timestamp ≥ merge time + 24 h;
  - `randomness = SHA-256(signature)`;
  - BLS verification. A synthetic-keypair self-test accepts the valid signature and rejects a wrong round or wrong randomness.
- **Verified in CI (resolves the stage-1 chain-hash requirement of §6.3):** the `Pilot B drand quicknet check` workflow compared the pins (chain hash `52db9ba7…84e971`, public key `83cf0f28…ece45a`, period 3 s, genesis 1692803367, scheme `bls-unchained-g1-rfc9380`) with the `/info` served by four relays (api, api2, api3.drand.sh and drand.cloudflare.com): **4/4 match**. Live rounds verified with `randomness = SHA-256(signature)` and the BLS pairing check (py_ecc hash-to-G1): 32953113 (run [38082317982](https://github.com/shaden7/emergence-lab/actions/runs/38082317982)), 32953201 ([38082611228](https://github.com/shaden7/emergence-lab/actions/runs/38082611228)) and 32953256 ([38082785660](https://github.com/shaden7/emergence-lab/actions/runs/38082785660), final code head). Round 32953256 maps to 2026-10-10T20:12:12Z under `round_time`, consistent with that run's 20:11:49–20:12:20Z window (5 s behind). The pins were typed from model memory first; they are now relay-confirmed, not memory-based.
- **Stage 2 gap:** a workflow that runs the blind phase exactly once on `main`, fetches round R via `fetch-round` and archives the outputs is **not** part of this PR. It belongs to stage 2 and must not run before R is published.

## Later-pass review (session `rd-claude-20261010T205622Z-908995`; did not author the code; same model family, so not external review)

**Decision: PASS.** Checked against prereg v1.0-r1 text:
- §3 class definitions, parameter ranges and counts; S3 normalisation Σ|a_j| = 1; N3 symmetric base with w₀ ≥ 0.0244 > ε.
- §5 rule in the analyst (z₁/z₂ Bonferroni, exterior r > 4t, r̂, exhaustive verdicts).
- §7 seed streams; §8 gate logic in the evaluator; and the beacon arithmetic and BLS scheme.

**Actually executed (local sandbox, Python 3.13.16 / NumPy 2.5.3 / SciPy 1.18.1, `OPENBLAS_NUM_THREADS=1`):**
- `pytest -q`: 235 passed.
- Dev run ×2 byte-identical (`rows.csv` `fa657d02…`, `result.json` `43d87373…`).
- Decision digest `6da5c8e3…`, equal to the Python 3.12.15 CI value on head `7686584` ([38082785677](https://github.com/shaden7/emergence-lab/actions/runs/38082785677)).
- A separate review script recomputed every z, detection, verdict and r̂ from `rows.csv`: 0 mismatches over 40 instances.

**Calibration Monte Carlo (review check, not a Pilot B result):** the full pipeline ran on 400 non-blind review keys `SHA-256(b"pr30-review-mc-<i>")` (16,000 instances), with counts recomputed independently. Rates against expectations under exact calibration:

| Quantity | Observed | Expected |
| --- | --- | --- |
| Exterior false rejection, H0 instances | 497/9,600 = 0.0518 | 1 − (1 − 0.05/12)¹² = 0.0488; binomial SE 0.0022 |
| Speed overestimate, strict instances | 178/6,400 = 0.028 | bound 0.05 |
| Spurious C2 | 0.086 | prereg 0.079; SE 0.007 |
| Spurious C1 | 0.079 | prereg 0.075 |
| B-G1 failure | 13/400 | prereg 0.030 |
| B-G2 failure | 2/400 | prereg bound 0.007 |
| B-G3 failure | 10/400 | prereg ≤ 0.020 |
| B-G0, B-G4, B-G5 failure | 0/400 | — |
| Power on detectable N | 2,347/2,347 rejected | ≥ 90 % required |

Detectable N instances per key: min 5, mean 5.87. Per-instance rates agree with exact calibration within sampling error. Consequence to state before the blind run: **even a correct implementation fails some gate with probability ≈ 6 %** (sum of the B-G1/B-G2/B-G3 tails); a blind gate failure is then published as a failure per §8, not rerun.

**Non-blocking notes:**
- B-G4 with 1–2 detectable instances computes the fraction instead of the prereg's "vacuous pass". This is stricter than the text, but it never occurred in 400 keys (min 5 detectable, mostly N2).
- The stage-1 note's beacon section was stale ("not yet verified"); this review corrected it from the CI annotations.

## Limitations

- Analyst isolation is enforced at the import and interface level. Python cannot stop deliberate introspection of the oracle object, so a reviewer should read the 60-line analyst.
- The dev set is a single draw of 40 instances. Gate passes on it check correctness, not calibration rates (the expected B-G1 count is ≈ 1.2).
- The detector model (known σ, Gaussian white noise) is imposed, as in N5.

## Next step

A later-pass review by a different Director session. It should cover:
- the beacon workflow outcome, and correcting the pins if needed;
- the analyst code;
- the implementation choices above against the preregistration text;
- the Python 3.12 CI digests.

Then merge with an expected-head guard. The merge commit's timestamp fixes R; the blind run (stage 2) happens only after round R is published.
