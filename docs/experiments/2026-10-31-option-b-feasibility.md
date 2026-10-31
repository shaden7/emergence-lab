# Option B (S1c) feasibility inputs: cost and power from archived evidence (proposed note)

**Status: PROPOSED planning note, not a preregistration and not an authorization.** It draws no seeds and runs no kernel.
**Author:** Director `rd-claude-20261031T0803Z-` (2026-10-31). **Base:** `main` `a475ebf` (SE-audit run record merged via PR #58).
**Issue:** [#37](https://github.com/shaden7/emergence-lab/issues/37). **Inputs:**
- [S1 method/scope decision](../S1_METHOD_SCOPE_DECISION.md) § 2, option B: about 192 trees per size at 2¹⁶ and 2¹⁸, ≈ 220 CPU-min, nominal P(equivalence | D = 0) ≈ 0.85.
- The [SE-audit run record](2026-10-29-se-audit-run.md), which says an option-B prereg must:
  - use the pooled SD upper factor 0.08696;
  - state the 2¹⁴ → 2¹⁶–2¹⁸ transfer assumption;
  - re-derive its budget from the observed per-tree cost.

Instrument planning only. Nothing here concerns dimensional reduction, emergent geometry or spacetime.

## Reproduction

[`option_b_feasibility.py`](option_b_feasibility.py) does not import `emergence_lab`. It reads only archived release assets:
- `s1b-run-v1`, tarball sha256 `0211d32d…e66f`;
- `se-audit-run-v1`, tarball sha256 `63d8b42a…53de`.

Both were re-downloaded over REST on 2026-10-31, and both hashes match their `.sha256` assets. Run it as:

`python -I option_b_feasibility.py <s1b_run> <se_audit_run>`

Local run: Python 3.13, NumPy 2.5, SciPy 1.18, pandas.

## 1. Why the SE audit cost 1.7× its projection (numerical observation)

| Run | Host CPU (container `nproc=1`) | CAY 2¹⁴ edge steps / tree | source CPU / tree | throughput |
| --- | --- | ---: | ---: | ---: |
| S1b | AMD EPYC 9V74 | 7.472 × 10⁹ | 16.4 s | 4.56 × 10⁸ steps/s |
| SE audit | AMD EPYC 7763 | 7.490 × 10⁹ | 27.8 s | 2.70 × 10⁸ steps/s |

The work per tree is the same to 0.24 %. The whole 1.69× excess is host throughput. GitHub-hosted runners are assigned different CPU models, and the workflow cannot choose one. So the gap is **not** a kernel or design change. The conclusion is that **any budget for a hosted-runner run must assume the slower observed host**.

## 2. Option-B cost (projection; the assumptions are stated)

S1b per-tree source CPU on the fast host was 29.0 s at 2¹⁶ and 40.0 s at 2¹⁸. At 192 trees per size:

| Host | 2¹⁶ s/tree | 2¹⁸ s/tree | total source CPU |
| --- | ---: | ---: | ---: |
| fast (EPYC 9V74, observed per size) | 29.0 | 40.0 | **221 CPU-min** |
| slow (EPYC 7763, scaled by the 2¹⁴ throughput ratio 1.691) | 49.1 | 67.6 | **373 CPU-min** |

**Assumption:** the host ratio measured at 2¹⁴ transfers to 2¹⁶ and 2¹⁸. On the fast host, throughput at 2¹⁸ was already 14 % below 2¹⁴, so cache effects could make the slow-host figure worse, not better.

Overhead adds about 40–50 CPU-s per run.

**Consequence:** GitHub-hosted jobs have a 6 h (360 min) maximum. A single `nproc=1` contained job running the decision record's 192 + 192 trees would **exceed that limit on the slower host**, and it would need a hard CPU stop far above the record's 220 CPU-min. Option B as sketched is therefore not feasible as one contained single-CPU job.

Design choices for a prereg, listed here without selecting one:
- (i) **Two size-specific jobs**, each ≤ ≈ 220 CPU-min on the slow host, with one marker and one shared seed plan. This needs once-only guards that span two jobs.
- (ii) **Two contained worker processes**, one per size. Hosted runners expose more than one vCPU, but `nproc=1` containment is currently part of the reviewed design.
- (iii) **Fewer trees**, with the power cost shown in § 3.
- (iv) **Option A stays in force**, and option B is not pursued.

## 3. Power and the SD transfer assumption (normal-theory projection)

These are descriptive SD inputs, each the pooled per-tree ψ SD of the annealed W = 128–1024 CAY slope.

| Source | N | n trees | SD | 90 % CI |
| --- | --- | ---: | ---: | --- |
| SE audit (prereg-mandated basis) | 2¹⁴ | 192 | 0.07929 | [0.07295, **0.08696**] |
| S1b | 2¹⁴ | 24 | 0.0781 | [0.0632, 0.1036] |
| S1b | 2¹⁶ | 24 | 0.0986 | [0.0798, 0.1307] |
| S1b | 2¹⁸ | 24 | 0.0910 | [0.0736, 0.1206] |

**Observation:** both S1b point SDs at 2¹⁶ and 2¹⁸ lie *above* the mandated upper factor 0.08696, though inside their wide CIs. The 2¹⁴ → 2¹⁶–2¹⁸ transfer assumption is therefore **not conservative on the available evidence**. This was a post hoc look at 24 trees per size, so it is not a test.

Nominal TOST power for the 2¹⁸ − 2¹⁶ contrast: ±0.03, α = 0.05 per side, equal n per size, independent sizes.

| SD | n = 128 (D = 0 / 0.01 / 0.02) | n = 192 | n = 256 |
| --- | --- | --- | --- |
| 0.08696 (mandated) | 0.74 / 0.56 / 0.23 | 0.92 / 0.73 / 0.30 | 0.98 / 0.83 / 0.37 |
| 0.0986 (S1b 2¹⁶ point) | 0.57 / 0.44 / 0.19 | 0.82 / 0.62 / 0.26 | 0.93 / 0.74 / 0.31 |

At n = 192 the nominal power at D = 0 is 0.82–0.92, depending on which SD transfers. Even with a perfect SE model, the design has little power against a true |D| ≈ 0.02, which is two-thirds of the margin. Fewer trees (option iii) push the D = 0 power to about 0.6–0.75.

## 4. Implications for the next step (hypotheses and recommendations, not decisions)

- An option-B prereg is still *permissible* under the SE-audit outcome. But it must budget about **375–400 CPU-min**, split across jobs or workers, rather than ≈ 220. It should also either:
  - adopt the larger S1b-observed SD as a sensitivity case; or
  - justify the mandated 0.08696 and disclose this note's observation.
- The S1/S1b record already closes the two-family objective as *not established* (option A). Whether a ≈ 6.5 CPU-h, multi-job CAY-only study is worth it relative to option C or other Issue #37 work is a **judgment for the next Director**. This note supplies the inputs and does not pre-empt that choice.

## Evidence level and limitations

- Cost figures are observations for 2¹⁴. The figures for 2¹⁶–2¹⁸ on the slow host are projections under the stated transfer assumption, and only two host models have been observed.
- The power figures are nominal normal-theory projections. They inherit the SE model, which was not rejected at 2¹⁴ only, and they ignore SD estimation uncertainty.
- The 6 h job limit is a GitHub platform limit, not a project measurement.
- No Lightsail, deployment, paid API, seeds or run.
