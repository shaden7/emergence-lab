# Spectral SE audit — calibration of the tree-level delta SE for the annealed CAY slope (Issue #37), preregistration v0.1

**Status: PROPOSED design. No seed drawn, nothing implemented, no run authorized.**
- Before integration this design needs a later-pass review by a separately started session.
- After that, a separate implementation PR is needed, with its own review and exact-head CI, plus an explicit in-code seed unlock.
- This is **instrument diagnosis only**. It says nothing about dimensional reduction, emergent geometry or spacetime.

**Date:** 2026-10-25. **Author:** Director `rd-claude-20261025T0803Z-82350b8c`. **Base:** `main` `7281443`.
**Basis:** [S1 method/scope decision](S1_METHOD_SCOPE_DECISION.md) § 3 item 2 (merged via PR #54) and its [later-pass review](https://github.com/shaden7/emergence-lab/pull/54#issuecomment-6395192707). It reuses the observable and kernel of the [S1 prereg v0.2](SPECTRAL_S1_PREREGISTRATION.md) and the [S1b prereg v0.2](SPECTRAL_S1B_PREREGISTRATION.md).
**Operating characteristics script:** [`docs/experiments/se_audit_operating_characteristics.py`](experiments/se_audit_operating_characteristics.py). It needs no project seeds and no tree data.

## 0. Question and why it is asked

**Question.** At a single CAY size, does the tree-level delta-method SE (S1 P3) match the actual sampling spread of the annealed window slope d̂_W? The window is W = 128–1024 and each batch has 12 independently seeded trees.

**Motivation (post hoc, descriptive).**
- The CAY 2¹⁸−2¹⁶ contrast was +0.071 in the pilot and −0.043 in S1b. That is about 2.9 combined SE apart.
- The S1b SE was 1.64× its pilot-based plug-in value.
- The decision record lists four open readings: (a) a chance pilot SE underestimate, (b) winner's curse, (c) SE misstatement, (d) a run defect. Only (c) is directly testable at low cost, and this audit targets it.

**Prior information disclosed before design freeze.** These are numerical observations from the archived S1b release `s1b-run-v1` (tarball sha256 `0211d32d…`, CAY, 24 trees per size). They are not audit data.
- Per-tree annealed Q_i(128) and Q_i(1024) have a coefficient of variation of ≈ 0.11–0.15 at all three sizes.
- The correlation between ln Q_i(128) and ln Q_i(1024) is 0.65–0.81.
- At 2¹⁴, Q_i(1024) has skew −0.76 and excess kurtosis 1.06.

**Honest prior expectation (assumption, not result).**
- Trees are i.i.d., per-tree CV is ≈ 0.12 and the shape is near-normal. In the linear approximation, R (§ 2) is then distributed as √F(15, 176). The synthetic model in § 4 confirms a size of ≈ 0.05 at CV 0.125.
- So the audit is **expected not to reject** unless one of three things holds: the per-tree law is much heavier-tailed than S1b suggests; trees or sources are not independent (a seeding or generator defect); or the implementation's SE is wrong.
- Under that expectation, reading (a) is the most plausible explanation of the 1.64× ratio: under normal theory, P(s/σ < 1/1.64 | 7 df) ≈ 0.08.
- The audit is still worth its ≈ 53 CPU-min, about a quarter of option B's ≈ 220. It checks the independence and SE assumptions on fresh seeds at a new seed base. It also delivers a pooled per-tree SD with 176 df, a ±≈ 9 % 90 % CI factor of [0.92, 1.10]. Option B's power calculation would rest on that SD, instead of on 24 or 8 trees.

## 1. Observable (unchanged from S1 v0.2 § 3 / S1b v0.2 § 1)

- **Return probability:** simple random-walk even-time return q_v(t) = [P^(2t)]_vv, with sources sampled uniformly without replacement.
- **Per tree:** Q_i(t) is the mean over S = 32 sources.
- **Per batch:** an **annealed** batch mean Q̄_b(t) over its 12 trees is formed before taking logs. Then d̂_b = −2[ln Q̄_b(1024) − ln Q̄_b(128)]/ln 8.
- **Fixed settings:** T = 4096. Killed-ball certified bracket η = 10⁻⁴. R starts at 64 and doubles. Edge-step cap of 2×10⁹ per source.
- **Generator:** unchanged Prüfer uniform labelled tree (`cayley_uniform_tree`).
- **Batch SE:** SE_b is the tree-level delta SE within batch b, i.e. s_ψ,b/√12 with ψ_i as in S1 P3.

## 2. Design, statistic and decision rule

| Item | Fixed value |
| --- | --- |
| Family / size | CAY, N = 2¹⁴ only |
| Batches × trees | B = 16 disjoint batches × m = 12 independently seeded trees (192 trees) |
| Sources per tree | 32 |
| Graph seed base | **2036101901** (unused in the repo at `7281443`, checked by `git grep 20361019`) |
| Seed rule | SeedSequence([2036101901, 0, 0, i_tree]), PCG64, i_tree = 0…191. Batch b = trees 12b…12b+11. Sources from the same tree-seed child protocol as S1. |
| Engineering seed base | 2036101997, used for tests and smoke runs only |

**Primary statistic.** R = sd_b(d̂_b) ÷ √(mean_b SE_b²), using the sample sd with B−1 df.
- R² is the one-way ANOVA ratio MS_between / MS_within in the linear approximation.
- Its reference distribution is **F(15, 176)**, which accounts for the estimated denominator.
- The PR #54 sketch used the χ²₁₅/15 bound of 1.291, which treats the denominator as known. This version corrects it.

**Decision rule (nominal one-sided α = 0.05):**
- **SE-REJECTED** iff R > **1.313** = √F₀.₉₅(15, 176). Action: per the decision record, option C, a new estimator. A symmetric equivalence study with the current SE model is not defensible.
- **SE-NOT-REJECTED** iff R ≤ 1.313. The SE model is *not rejected at N = 2¹⁴*. Option B, a symmetric CAY equivalence study, may be **separately preregistered**. That prereg must use the pooled SD from this audit, inflated to its 90 % upper CI factor, and must disclose that 2¹⁶–2¹⁸ are uncertified.
- **BLOCKED** if any condition in § 3 fails. Then there is no classification and no automatic rerun.

**Descriptive outputs (not decision inputs):**
- the pooled per-tree SD s_ψ (176 df) with a 90 % CI;
- CV(SE_b) across batches. The normal-theory reference is ≈ 0.21; the synthetic heavy-tail scenarios give 0.33–0.62;
- d̂ over all 192 trees with its delta SE, and the jackknife/delta ratio;
- per-tree CV, skew and kurtosis of Q_i(128) and Q_i(1024);
- a QQ summary of the standardized batch deviations.

None of these changes the decision. The pooled d̂ is **not** compared with 4/3 as a calibration verdict.

## 3. Controls, eligibility and budget

- **Before the first audit seed:** run S1 P0a–P0d unchanged. Any STOP blocks the run.
- **Full sample only:** all 192 trees complete, with all 32 sources OK and certified. Any OVER_CAP, PARTIAL, non-finite or non-positive Q̄_b, or missing certification means BLOCKED.
- **No replacement:** no tree is replaced, and no batch is re-formed after seeing data. Batch membership is fixed by i_tree as above.
- **Budget:** one core, ≤ 2 GiB enforced externally, the hosted-runner containment path, **not Lightsail**, and no paid service.
  - Projection: 192 × ≈ 16 CPU-s ≈ 51 CPU-min plus controls, ≈ 53 CPU-min in total. The per-tree cost is derived from S1b's recorded 34.3 CPU-min for 24 × (2¹⁴, 2¹⁶, 2¹⁸) trees.
  - **Hard stop at 100 CPU-min.** Stopping early means BLOCKED, with no extension.
- **Once-only run:** a single run under an explicit in-code authorization, after implementation review. All attempts are logged. No selective omission.

## 4. Operating characteristics (assumptions, not observations)

From the script, analytic part:
- R_crit = 1.313.
- Power (P(SE-REJECTED) when the true ratio of actual to delta-SE sampling sd is ρ): **0.44** at ρ = 1.3, **0.81** at ρ = 1.6, **0.97** at ρ = 2.0.
- An undetected ρ ≈ 1.3 would make a nominal 90 % CI's actual coverage about 79 %. That is a **known blind spot** of this budget.

Synthetic Monte Carlo (seed 2036101991, 4000 replicates per scenario, correlated per-tree Q laws, nonlinear annealed slope):

| Per-tree law of Q | P(R > 1.313) | median R | median CV(SE_b) |
| --- | ---: | ---: | ---: |
| lognormal, CV 0.125 (≈ S1b) | 0.048 | 0.98 | 0.21 |
| lognormal, CV 0.3 | 0.057 | 0.99 | 0.23 |
| lognormal, CV 1.0 | 0.161 | 1.09 | 0.33 |
| log-t₃, scale as CV 0.3 | 0.355 | 1.19 | 0.53 |
| log-t₃, scale as CV 1.0 | 0.899 | 2.11 | 0.62 |

Reading:
- At S1b-like dispersion the rule holds its nominal size.
- It reacts to strong skew or nonlinearity and to infinite-moment tails, which is the case reading (c) worries about.
- The log-t₃ scenarios are deliberately extreme stress cases, not plausible models of tree returns.

## 5. Limitations

- A single size, 2¹⁴. A pass cannot certify the SE at 2¹⁶–2¹⁸, where the S1b contrast lives. Word any pass as "not rejected at 2¹⁴", never "SE validated".
- R pools all batches. It cannot detect a defect shared by every tree, such as a generator or kernel bias, because that would shift d̂ without changing its spread.
- Nominal F levels assume approximately normal batch estimates. The script checks only the synthetic laws listed.
- The audit cannot discriminate (a) from (b), and it does not test (d) for the archived S1b run.
- The threshold, batch split and seed base are engineering choices, frozen here before any draw.

## 6. Staged execution

1. Later-pass review of this design, then integration.
2. A separate implementation PR. It adds an `se_audit` mode reusing `spectral_s1` (kernel, influences, P0 controls), config `configs/spectral_se_audit.json`, a seed lock with an environment gate, a manifest, and synthetic-data tests of the R and F classification and of the batch indexing. It needs exact-head CI and its own review.
3. A run-authorization change, reviewed.
4. One contained run, then an archived evidence release and an independently rechecked result note.

No step unlocks S2. The frozen S1 NO-GO, S1b C-INCONCLUSIVE/U-EQUIVALENT and Phase-0 GO stay unchanged.
