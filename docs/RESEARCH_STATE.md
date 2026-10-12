# Research State

Last handoff update: 2026-10-12. **D2 complete: all gates G0–G4 pass with reviewed outcomes**, so the first §6 branch of the D2 preregistration applies (instrument calibration only). The RRT result ([PR #41](https://github.com/shaden7/emergence-lab/pull/41)) was reviewed PASS by a later-pass session; see the integration line of the 06:06 session below for the merge status.
- D2: CAY (G0/G1, PR #38, `becfcdf`), UST (G0/G2, PR #39, `7db826e`) and RRT (G0/G3, PR #41) pass, and the per-family byte identity holds (G4). **§6 reading (reviewed):** the frozen D1 estimator at S = 256 is *calibrated for* uniform labelled trees (d = 2) and the 2D torus UST (8/5) at the reported sizes and windows, and it rejects the RRT null. Qualifications: the CAY §8 overrun, the CAY ε = 0.10 fragility, the ≈ 0.04 UST offset, S = 32 not re-tested, both positive families are trees, and the RRT tests only the saturation guard. This is not a statement about emergent geometry, spectral dimension or nature.
- D2 implementation was integrated via PR #36 (`e014319`). The Phase-0 scoped GO and the D1 instrument calibration are unchanged.
- **Pilot B:** the single blind run [38181108016](https://github.com/shaden7/emergence-lab/actions/runs/38181108016) on `main` `0048198` passes B-G0 to B-G6. The [decision record](PILOT_B_DECISION.md) gives a **scoped GO only as a noise-aware calibration instrument** on stipulated linear models with known σ. Power is shown only for dense power-law violations (N2 5/5); N1 0/5 and N3 0/6 went undetected. This is not a physics result.

## Director session: later-pass review of D2 RRT result, PASS (2026-10-12, `rd-claude-20261012T0606Z-6cad7dd175fb`)

**Recovery audit:**
- The previous lease (`rd-claude-20261012T0405Z-e359effb4040`) was released cleanly at lock commit `2462872`.
- Open PRs: #41 only, at head `ddab0da`, base `main` `ff4f121`, mergeable and clean. Its exact-head CI runs [38208969669](https://github.com/shaden7/emergence-lab/actions/runs/38208969669) and [38208966091](https://github.com/shaden7/emergence-lab/actions/runs/38208966091) are completed-success.
- Open issues: #4 and #37. Nothing was queued or in progress, and nothing was incomplete. WIP is 1 PR.

**Executed:** a later-pass review of PR #41, recorded in full in the review section of `docs/experiments/2026-10-12-d2-rrt.md`. The script is `docs/experiments/d2_rrt_review_independent.py`, which does not import `emergence_lab`. The reviewer is a different session from the producer, but the same model family.
- Both producer scripts were rerun. Their outputs are identical, and the artifact hashes match both manifests.
- An own D1 verdict reproduces 24/24 verdicts and admissible sets, plus the B̄(32)/N figures and the r_min = 2 sensitivity.
- Instances were rebuilt from the seed rule and checked with an own numpy BFS: 1792/1792 counts match at 2²⁰ (rep 5, all 256 sources) and 168/168 at 2²² (rep 3, 24 sources).
- An **independent RRT generator** (⌊U·i⌋, fresh seeds 20261012 and 20261013) gives no Bonferroni rejection of the B̄(r) replicate means against the CSV. The smallest p is 0.024 at 2¹⁸ (threshold 0.01) and 0.367 at 2²⁰. Its own verdicts are 16/16 `INSUFFICIENT_RANGE`.
- The r = 2 identity and the Geometric(1/2) limit were re-derived. The Na & Rapoport title and authors were confirmed.

**Decision:** PASS, with no findings that need correction. The §6 reading is confirmed: first branch, instrument statement only (see the header).

**Evidence level:** reviewed numerical observation for the D2 null family. It completes D2 as a methodological calibration. No physics claim.

**Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:** write the D2 decision record for Issue #4, scoped as with `PILOT_B_DECISION.md`. It should state what the calibration does and does not license for Phase 1, and that S for any Phase-1 application must be chosen by the §5a power argument. It should be docs-only and reviewed by a later session. Candidates after that, as proposals only: a D3 with a non-tree family (for example random planar maps), or a spectral-dimension cross-check on the same frozen instances.

## Director session: D2 RRT family executed, result proposed (2026-10-12, `rd-claude-20261012T0405Z-e359effb4040`)

**Recovery audit:** the previous lease (`rd-claude-20261012T0205Z-64ccb703e8eb`) was released cleanly at lock commit `0f52da5`. No open PRs; open issues #4 and #37. The latest runs, including `main` `ff4f121` push run [38194933603](https://github.com/shaden7/emergence-lab/actions/runs/38194933603), are completed-success; nothing was queued or in progress.

**Why this step:** the next step named in the previous handoff (D2 RRT, budget decision first).

**Budget decision (before any RRT output):** no r4. A timing-only check (non-D2 seed 4242, ball counts discarded) gave 1.23 s/BFS for RRT and 1.88 s/BFS for CAY at N = 2²². The RRT figure matches the §8 basis; CAY's deeper trees need more pointer-jumping passes, which explains its overrun. The 50-min projection and the binding `timeout 75m` stop stand.

**Actually executed (Director cloud sandbox, Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1; code `main` `ff4f121`):**
- `pytest -q`: 289 passed, 4 skipped (Pilot B tests needing `py_ecc`).
- `--families random_recursive_tree` twice, one after the other, each under `timeout 75m` on one pinned vCPU: 43.1 / 44.2 CPU-min (0.86× / 0.88× the projection), peak RSS ≤ 395 MiB. Outputs byte-identical: `ball_counts.csv` `4dd7c63c…`, `result.json` `23d6275f…`.

**Numerical observations (proposed; `docs/experiments/2026-10-12-d2-rrt.md` in PR #41):**
- D2-G0 (RRT structural) PASS; **D2-G3 PASS:** 24/24 `INSUFFICIENT_RANGE`, decided by the saturation guard (pooled B̄(32)/N 0.985 / 0.930 / 0.817). Under r_min = 2, 21/24 are `NO_PLATEAU`. No sensitivity setting gives a `PLATEAU`.
- Producer checks (not independent): re-verdict 0/24 mismatches; networkx BFS 112/112; mean |B(v, 2)| consistent with the exact asymptotic value 7 (|z| ≤ 0.35).

**Evidence level:** numerical observation for the D2 null family. Unreviewed. The §6 reading (all gates pass) is proposed in PR #41, not established. No physics claim.

**Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:** a later-pass review of PR #41 by a different session (rerun both check scripts, own RRT regeneration at 2¹⁸, re-check the Na & Rapoport reference, rule on §6), then merge with an expected-head guard if PASS. After that, the D2 decision record for Issue #4.

Director run rd-claude-20261012T0405Z-e359effb4040: start 2026-10-12T04:05:05Z, end 2026-10-12T05:40:15Z, duration 95 min

## Director session: PR #39 merge, later-pass review of Pilot B result PASS (2026-10-12, `rd-claude-20261012T0205Z-64ccb703e8eb`)

**Recovery audit:**
- The previous lease (`rd-claude-20261012T0005Z-915e474a3b7b`) was released cleanly at lock commit `9d9114a`. Its handoff was on the PR #39 branch, not on `main`.
- Open PRs: #39 (head `c774f6e`, docs-only on top of the reviewed `2b84a3a`) and #40 (head `fa01b33`). Both have completed-success CI on their exact heads: #39 [38187678413](https://github.com/shaden7/emergence-lab/actions/runs/38187678413) and [38187674772](https://github.com/shaden7/emergence-lab/actions/runs/38187674772); #40 [38187652455](https://github.com/shaden7/emergence-lab/actions/runs/38187652455) and [38187634094](https://github.com/shaden7/emergence-lab/actions/runs/38187634094).
- Nothing was queued or in progress. `pilot-b-blind-run.yml` has exactly one run. Nothing was incomplete.

**Integrated:** PR #39 was merged with the expected-head guard `c774f6e`, giving `7db826e`. The review was PASS by `rd-claude-20261012T0005Z-915e474a3b7b`.

**Executed:** a later-pass review of PR #40 by a session that produced none of it (same model family). The details are in the review section of `docs/experiments/2026-10-11-pilot-b-blind.md`. The script is `docs/experiments/pilot_b_review_independent.py`, which does not use `emergence_lab`.
- Release digests, beacon, key and round arithmetic all check out, and so do the frozen blobs and the single workflow run.
- A frozen-code rerun reproduces the dev and blind decision digests, with local BLS verification.
- An own re-derivation reproduces all flags, verdicts, r̂ and gate counts.
- Own propagators reproduce S_true for all 40 instances (max |ΔS| 1.3·10⁻¹⁵), exterior zeros for all P instances, and the B-G4 detectable set.

**Findings:** the claim "immutable release" was wrong, because GitHub reports `immutable: false`. It is corrected in the note and the decision record (wording only). The integrity of the release rests on the digests pinned in Git.

**Decision:** PASS. **Evidence level:** reviewed numerical observation of a methodological calibration on stipulated models; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:** D2 RRT. Decide the r4 budget before any RRT output exists. CAY took about 75 CPU-min against a projection of 50; the current stop is 75 min. Then make one invocation under the binding stop, then the repeat. Pilot B follow-ups (unknown σ, correlated noise, N3 grid coverage) are proposals only.

**Merge follow-up:** PR #40 was merged with the expected-head guard `4f28ff7`, after CI was green on that exact head ([38194734035](https://github.com/shaden7/emergence-lab/actions/runs/38194734035), [38194730448](https://github.com/shaden7/emergence-lab/actions/runs/38194730448)), giving `037606b`. WIP is now 0 PRs. RRT was not started this session, because the r4 budget decision should come first and two 75-min invocations would not fit within one lease without several heartbeats.

Director run rd-claude-20261012T0205Z-64ccb703e8eb: start 2026-10-12T02:04:39Z, end 2026-10-12T02:13:17Z, duration 9 min

## Director session: later-pass review of D2 UST result, PASS (2026-10-12, `rd-claude-20261012T0005Z-915e474a3b7b`)

**Recovery audit:**
- The previous lease (`rd-claude-20261011T2205Z-fa3ffc55355f`) was released cleanly at lock commit `4fc3400`.
- Open PRs: #39 only, head `85f81a8`, base `main` `0048198`, mergeable and clean. Its exact-head CI runs [38180822587](https://github.com/shaden7/emergence-lab/actions/runs/38180822587) and [38180825167](https://github.com/shaden7/emergence-lab/actions/runs/38180825167) are completed-success.
- Open issues: #4 and #37. Nothing was queued or in progress.
- New since the last handoff: the owner's Pilot B blind dispatch ran (see the header). It has not been evaluated yet.
- WIP is 1 PR.

**Executed:** a later-pass review of PR #39, recorded in full in the note's review section. The script is `docs/experiments/d2_ust_review_independent.py`. It was written by a different session from the producer, but by the same model family.
- Hashes match both manifests.
- An own verdict reproduces 24/24 replicate results and all G2 and pooled numbers from the CSV.
- The full L = 256 slice was regenerated and every ball count recomputed with scipy BFS: 26 368 / 26 368 match.
- An **independent Aldous–Broder sampler** was run with fresh seeds (16 trees at L = 256, 8 at L = 512). Its B̄(r) shows no Bonferroni rejection against the CSV replicates (smallest p 0.042 and 0.119). Its d̂ level is the same: 1.557 and 1.572, so the offset of about 0.04 below 8/5 is not a Wilson artifact.
- The leaf fraction is 0.2944–0.2946 against the exact Z² value 0.2945.
- The budget is within the §8 stop, so there is no deviation.

**Decision:** PASS, with no findings that need correction.

**Evidence level:** reviewed numerical observation for the second of three D2 families. There is no §6 decision and no physics claim. Volume-growth dimension is not spectral dimension.

**Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Merge blocker:** CI was green on the reviewed head `2b84a3a` (push [38187264874](https://github.com/shaden7/emergence-lab/actions/runs/38187264874), PR [38187267889](https://github.com/shaden7/emergence-lab/actions/runs/38187267889)). The expected-head merge (`PUT /pulls/39/merge`, sha `2b84a3a`) was then refused by this session's tool permission classifier, as happened with PR #38. It was not retried through another tool. This handoff commit is docs-only on top of `2b84a3a`. The next Director or the owner should merge PR #39 with an expected-head guard, after confirming that the head is this handoff commit and that its CI is green.

**Pilot B (also this session):**
- The blind release was downloaded through the REST asset API. Its hashes match the archive manifest.
- The key was recomputed from the beacon.
- A local rerun of the frozen code reproduces the dev digest `6da5c8e3…` and the blind decision digest `c9129efc…`.
- On zero-signal cells, z is consistent with N(0,1).
- The result note, the decision record and the check script are proposed in [PR #40](https://github.com/shaden7/emergence-lab/pull/40), head `fa01b33`. A different session must review them.
- WIP after this session: PRs #39 and #40.

**Next single step:**
1. Merge PR #39 once CI is green on its head; the review is PASS.
2. A later-pass review of PR #40 by a different session.
3. D2 RRT under `timeout 75m`, with the r4 budget decision before any RRT output exists.

Director run rd-claude-20261012T0005Z-915e474a3b7b: start 2026-10-12T00:05:17Z, end 2026-10-12T00:21:07Z, duration 15 min

## Director session: D2 UST family executed, result proposed (2026-10-11, `rd-claude-20261011T2205Z-fa3ffc55355f`)

**Recovery audit:**
- The previous lease (`rd-claude-20261011T2020Z-3f2bf2a82e36`) was released cleanly at lock commit `4fd3289`.
- There were no open PRs. Open issues: #4 and #37.
- The latest runs are all completed-success, including the `main` `0048198` push run [38171905106](https://github.com/shaden7/emergence-lab/actions/runs/38171905106). Nothing was queued and nothing was incomplete.
- The owner-triggered Pilot B dispatch has still not run. It is not this session's action.

**Why this step:** it is the next step named in the previous handoff.

**Actually executed (Director cloud sandbox, Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1; code `main` `0048198`):**
- `pytest -q`: 293 passed.
- `--families ust_2d_torus` ran twice, one after the other, each under `timeout 15m` on one pinned vCPU.
  - CPU: 10.7 / 11.1 min against a projection of 10. Peak RSS ≤ 488 MiB.
  - Outputs are byte-identical: `ball_counts.csv` `1ab481e8…`, `result.json` `6a77925b…`.

**Numerical observations (proposed; `docs/experiments/2026-10-11-d2-ust.md` in PR #39):**
- D2-G0 (UST structural) **PASS**.
- **D2-G2 PASS:** at L = 1024, 8/8 `PLATEAU`, mean d̂ 1.5668, 95 % CI [1.526, 1.608]. The L = 512 mean is 1.5595.
- No sensitivity flips.
- All means are 0.03–0.05 below 8/5. *Hypothesis:* a finite-size/torus correction; not tested.
- Producer checks (not independent): CSV re-verdict gives 0/24 mismatches; networkx BFS matches 208/208.

**Evidence level:** numerical observation for a second D2 family. Unreviewed. No §6 decision and no physics claim.

**Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. A later-pass review of PR #39 by a different session, including an independent regeneration of the L = 256 slice. Merge with an expected-head guard if PASS.
2. Then RRT under `timeout 75m`, with an r4 budget decision before any RRT output exists.

Director run rd-claude-20261011T2205Z-fa3ffc55355f: start 2026-10-11T22:05:05Z, end 2026-10-11T22:32:08Z, duration 27 min

## Director session: later-pass review of D2 CAY result, PASS, integration (2026-10-11, `rd-claude-20261011T2005Z-941a1e38c53a`)

**Recovery audit:**
- The previous lease (`rd-claude-20261011T1805Z-b1af89b4a6bb`) was released cleanly at lock commit `2b50be3`.
- Open PRs: #38 only, at head `29322bc`, base `main` `ecc4031`, mergeable. Its exact-head CI runs [38168112492](https://github.com/shaden7/emergence-lab/actions/runs/38168112492) and [38168092543](https://github.com/shaden7/emergence-lab/actions/runs/38168092543) are completed-success.
- Open issues: #4 and #37. Nothing was incomplete. WIP is 1 PR.

**Executed:** a later-pass review of PR #38 by a session that did not produce the run (same model family, so not independent peer review). The script is `docs/experiments/d2_cay_review_independent.py`. It does not use `emergence_lab` code; it has its own D1 verdict, its own exact CAY mean, a heap Prüfer decoder and scipy BFS.
- Hashes match both manifests.
- 24/24 verdicts and d̂ values are reproduced from the CSV, and so are all G0 and G1 numbers.
- Regenerating the whole 2¹⁸ slice gives 24 832 / 24 832 ball counts equal to the CSV.
- Spot checks at 2²⁰ and 2²² give 864 / 864.

**Findings:**
1. *Non-blocking, corrected in the note:* the column labelled "r_last per replicate" is really the largest admissible scale. d̂ is taken one scale earlier in 6/24 replicates, because of the finite-size turn-down predicted in §4.
2. *§8 ruling:* a recorded deviation, not BLOCKED.
   - The overrun was 0.5–0.8 %, with no output visible before completion. The run is deterministic and byte-identical, so an identical rerun would reproduce the same numbers.
   - This is a reviewer judgement; a stricter reading is disclosed in the note.
   - *Binding for the remaining families:* run them one after the other, each with a mechanical stop at 1.5× its projection (UST 15 min, RRT 75 min). A stop is BLOCKED (budget). Any change to the RRT budget needs r4 before RRT output exists.

**Evidence level:** numerical observation for one of the three D2 families (CAY), reviewed. No §6 decision and no physics claim.

**Deployment:** none. No Lightsail or EatSleepFeel interaction, and no spending.

**Merge blocker (resolved; see the merge follow-up):** after CI was green on `50d55c5`, the expected-head merge (`PUT /pulls/38/merge`, sha `50d55c5`) was refused by this session's tool permission classifier. It was not retried through another tool. The next Director, or the owner, should merge PR #38 with an expected-head guard once it has confirmed that the head is still the reviewed one and that CI is green.

**Merge follow-up (session `rd-claude-20261011T2020Z-3f2bf2a82e36`, owner-requested):**
- The session took a fresh lease and confirmed the head was `020c1f3`, which is docs-only on top of the reviewed `50d55c5`.
- CI on that head is green: [38171607549](https://github.com/shaden7/emergence-lab/actions/runs/38171607549) and [38171604310](https://github.com/shaden7/emergence-lab/actions/runs/38171604310).
- It merged PR #38 with the expected-head guard, giving `becfcdf`.

**Next single step:** run the UST family. Use two invocations, one after the other, each under `timeout 15m`. Then put the result PR through a later-pass review. RRT comes after that, under `timeout 75m`. Consider an r4 budget revision for RRT before any RRT output exists, given the CAY timing.

Director run rd-claude-20261011T2020Z-3f2bf2a82e36: start 2026-10-11T20:20:25Z, end 2026-10-11T20:21:59Z, duration 1 min
Director run rd-claude-20261011T2005Z-941a1e38c53a: start 2026-10-11T20:04:52Z, end 2026-10-11T20:17:48Z, duration 12 min

## Director session: D2 CAY family executed, result proposed (2026-10-11, `rd-claude-20261011T1805Z-b1af89b4a6bb`)

**Recovery audit:** the previous lease (`rd-gpt6-20261011T1645Z-1ard95ai`) was released cleanly at lock commit `e0fe61e`. Open PRs: none; open issues: #4. The latest runs are all completed-success, including `main` `ecc4031` push run [38157053037](https://github.com/shaden7/emergence-lab/actions/runs/38157053037). No queued runs. No release or branch held D2 output beforehand. Nothing was incomplete. WIP count before this session: 0.

**Why this step:** the previous handoff named the CAY family of the frozen D2 grid as the next step. The implementation review had passed, and prereg §8 requires only CI pytest plus a deterministic local run.

**Actually executed (Director cloud sandbox, Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1; code `ecc4031`, whose `src/` is identical to `e014319`):**
- `pytest -q`: 293 passed.
- `python -m emergence_lab.dimension_d2 --families cayley_uniform_tree` ran twice, in parallel, one vCPU each: wall 76.6 / 76.5 min, CPU 75.4 / 75.6 min, peak RSS 707 MiB.
- `ball_counts.csv` (`541e7ffb…1c2e`) and `result.json` (`a6a195b6…1e4a`) are byte-identical. The 3.79 MB total is committed in the PR, so no release asset is needed.
- Producer checks: CSV → frozen `verdict` agrees on 24/24 replicates; an independent networkx BFS matches 192/192 ball counts on two 2¹⁸ instances.

**Numerical observations (proposed; `docs/experiments/2026-10-11-d2-cay.md` in the PR):**
- **D2-G0 PASS:** largest |t| 1.89 over 21 pairs; Bonferroni critical value 6.13.
- **D2-G1 PASS:** at 2²², 8/8 `PLATEAU`, mean d̂ 1.9439, 95 % CI [1.873, 2.015]. The drift from 2²⁰ (mean 1.8981) is 0.046.
- **Not gated:**
  - Per-replicate sd(d̂) at 2²² is 0.085, about 1.7× the §5a model's 0.051. So P(G1) ≈ 0.997 is optimistic. *Hypothesis:* a larger design effect at 2²².
  - ε = 0.10 flips 2/8 replicates at 2²², so G1 is fragile under ε = 0.10.
  - The pooled d̂ at 2²² is 1.890, against the exact mean-curve value 1.929.

**Open for the reviewer:** §8 says to stop at 1.5× the projection, which is 75 CPU-min. Both invocations ended at 75.4–75.6 CPU-min without being stopped. No output was visible before completion. Whether this is BLOCKED (budget) is left to the reviewer; this session does not rule on it.

**Evidence level:** numerical observation for one of three D2 families. No §6 decision and no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **After 2026-10-11T21:11Z:** the owner dispatches `Pilot B stage-2 blind run (once only)` from `main`; this is unchanged.
2. A later-pass review of the CAY result PR by a different session, including the §8 ruling; merge with an expected-head guard if PASS.
3. Run UST (≈ 10 min projected), then RRT (≈ 50 min), two invocations each, one after the other.

Director run rd-claude-20261011T1805Z-b1af89b4a6bb: start 2026-10-11T18:04:43Z, end 2026-10-11T19:27:22Z, duration 83 min

## Director session: check of D2 fix, PASS and integration (2026-10-11, `rd-gpt6-20261011T1645Z-1ard95ai`)

**Objective:** Complete a distinct later-pass check of PR #36 after its previous reviewer changed the G1/G2 implementation and left a REVISE handoff. The lease was idle at entry (prior owner `rd-claude-20261011T160532Z-920cd8` clean release at 16:16:09Z); this session acquired and verified its own lease via expected-head CAS. Only one research PR was open.

**Evidence:** PR head `2d31a317133b7365c29b433a430fc48f62b2e57f`, initial base `505ab21480143ece0a4f4157332bb9e6b7d1a17a`. Inspected the fix diff `3af4ba6..2d31a31`, the actual `src/emergence_lab/dimension_d2.py` methods `_family_stats`/`evaluate_gates`, synthetic positive/negative tests, and prereg §5/§5a. Confirmed 8/8 `PLATEAU` is imposed only at the largest size; at the middle size the mean uses the available `PLATEAU` replicates as in the *preregistered model* (`nanmean`), and an empty set fails the drift gate. The UST CI separation and all top-size gates remain unchanged. The design/config pins, generator code and D1 estimator were not changed by the fix.

**Validation:** Two GitHub Actions runs on the **exact head** both concluded success: [PR 38154721280](https://github.com/shaden7/emergence-lab/actions/runs/38154721280), [push 38154717868](https://github.com/shaden7/emergence-lab/actions/runs/38154717868). The PR job includes `pytest -q`, smoke, exact holdout and D1 checks. The preceding reviewer reported 293 passing local tests and analytical/generator cross-checks; this session inspected those records and the source but **did not repeat the complete test suite locally**, because `git clone` failed due to DNS/network isolation. The uncertainty/noise figures (≈0.997 vs ≈0.973 probability of passing the correct-instrument G1 under alternative middle-size rules) remain **model-based**, not sampled D2 output. Conditioning the middle-size estimate on `PLATEAU` may cause selection bias and must be stated in the D2 result note.

**Decision and integration:** **PASS for the implementation, not for D2 experimental gates.** Review recorded in [PR #36 discussion](https://github.com/shaden7/emergence-lab/pull/36#issuecomment-6111338099). GitHub merge with `expected_head_sha=2d31a31...` succeeded; verified [merge `e014319`](https://github.com/shaden7/emergence-lab/commit/e014319fe2ca01b1ed7876686f2e063be9ce695a) as `main` HEAD. No D2 run or release created; no Lightsail/EatSleepFeel interaction, deployment or spending.

**Next discriminating step:** Execute the **CAY family** of the frozen D2 grid with the preregistered `seed_base` only now that implementation review passed. Use `GIT_SHA=e014319fe2ca01b1ed7876686f2e063be9ce695a`, single-core and ≤2 GiB RAM, per-family ≤90-minute stop rule and documented job provenance. Check D2-G0 (exact Cayley ball reference), G1, sensitivity, per-source CSV/manifest, and byte-identical second run; put outputs exceeding 5 MiB into an immutable release asset with SHA-256, not Git history. Without suitable bounded compute access this is a **pending run**, not a completed result. Later UST and RRT runs are separate family invocations. Pilot B's owner-triggered blind workflow remains a separate pending step after 21:11Z.

Review/integration start after lease acquisition 2026-10-11T16:45:54Z; state entry written 2026-10-11T16:49:18.450Z. No D2 measurement.


## Director session: later-pass review of the D2 implementation (PR #36), REVISE with fix applied (2026-10-11, `rd-claude-20261011T160532Z-920cd8`)

**Why this step:** PR #36 was the only open PR (WIP 1), and its handoff named a later-pass review by a different session as the next step. This session authored none of `8d2c05a` or `3af4ba6`. Same model family and software stack as the producer, so this is an AI-mediated later-pass review, not independent peer review.

**Recovery audit:** the lease was idle (released cleanly 14:20:52Z by `rd-claude-20261011T140555Z-`). That owner string has an empty random suffix, so owner uniqueness rested on the lease ID alone; process note, no conflicting writes found. PR #36 head `3af4ba6`: CI runs 38146673263 and 38146649583 completed-success on that SHA. No release, branch or CI artifact contains D2 output, and `seed_base` 2036101101 occurs only in the prereg, the config, the test pin and this file.

**Checks (Director sandbox; Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1, networkx 3.6.1; review seeds 818181 and 828282; non-grid sizes; no D2 seed):**
- **r3 delta:** only the two status lines, the version and the S256 reference figure change (`git diff 505ab21 8d2c05a`). PASS.
- **Prüfer:** the decoder re-derived (smallest-leaf pointer, the shortcut for a new leaf below the pointer, the last edge `(leaf, N−1)`). It agrees with networkx `from_prufer_sequence` on 1 865 random sequences (N = 3…39, 100, 1000, 5000) and round-trips through `to_prufer_sequence`: 0 mismatches (`scripts/review_d2/impl_generator_crosscheck.py`). PASS.
- **Wilson:** the last-exit pointer overwrite followed by a retrace from the start vertex is the loop-erased path (equivalent to cycle popping). On the 5 × 5 torus over 10⁶ draws, all 50 per-edge frequencies match the exact (n−1)/|E| = 0.48 (z: sd 1.08, max |z| 2.72; root-incident edges z = 1.68, −0.21, 0.01, 1.72; `impl_wilson_edge_marginals.py`). Over 2·10⁵ draws, four two-edge probabilities match the transfer-current determinant (|z| ≤ 2.14). At 4 × 4, Wilson and an independent Aldous–Broder sampler agree on the distributions of the degree of vertex 0, the tree distance 0 → (2, 2) and the diameter (χ² p = 0.48, 0.52, 0.69; 4·10⁴ trees each). PASS.
- **G0:** radii are the admissible scales of the pooled curve; the Bonferroni count is all (N, r) pairs; df = 7. PASS. Robustness note (non-blocking): if a replicate's radius list lacked a pooled-admissible r, the code would raise rather than misreport. This is not reachable at grid sizes.
- **Blocking finding (G1/G2 size comparison):** `two_size` also required 8/8 `PLATEAU` at 2²⁰ (UST: L = 512), following the D1 D-G3 note. The D2 prereg §5 requires 8/8 only at the largest size, and the §5a power model (`scripts/d2_g1_power.py`, `r2_power_resolution.py`) takes the 2²⁰ mean over `PLATEAU` replicates (nanmean). Under that model (40 000-replicate pools at S = 256, seed 828282; `impl_g1_middle_size_power.py`), the per-replicate non-`PLATEAU` rate is 3.1·10⁻³ at 2²⁰ and 3.5·10⁻⁴ at 2²². Joint P(G1 passes | correct instrument) is 0.997 under the prereg reading but 0.973 with the extra condition: about 9× the noise-only failure rate the design was justified by. **Model-based, not a D2 result.**
- **Fix applied in this session's commit on the PR branch:** the middle-size mean is over its `PLATEAU` replicates (it is undefined if none, and the gate then fails); 8/8 is required at the largest size only; `n_plateau` is reported; gate notes and the docstring are updated. New negative and positive tests: one non-`PLATEAU` at 2²⁰ passes, none at 2²⁰ fails, drift 0.11 fails; for UST, one non-`PLATEAU` at L = 512 passes and at L = 1024 fails. The new test fails on the old code (checked). `pytest -q`: 293 passed. Prereg and config are unchanged, and the pins still hold.
- **Run-time requirements (non-blocking):** set `GIT_SHA` to the executing commit, as for D1, or the manifest records `null`. `ball_counts.csv` will exceed 5 MiB, so D2-G4 needs a release asset with a pinned digest.

**Decision:** **REVISE**, fix applied. Not merged: the fix is by this reviewing session, so a further session must check it (diff `3af4ba6..` the new head) before merge. **Evidence level:** implementation review plus exact/independent generator checks; no D2 measurement; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **After 2026-10-11T21:11Z:** the owner dispatches `Pilot B stage-2 blind run (once only)` from `main` (unchanged).
2. A different session checks the G1/G2 fix commit on PR #36 against prereg §5/§5a and merges it with an expected-head guard if PASS.
3. Then run the grid per family (`GIT_SHA=<commit> python -m emergence_lab.dimension_d2 --families <f> --output …`, twice for D2-G4), within the §8 budget and lease heartbeats.

Director run rd-claude-20261011T160532Z-920cd8: start 2026-10-11T16:04:59Z, end 2026-10-11T16:15:33Z, duration 11 min

## Director session: D2 implementation and v1.0-r3 errata, proposed (2026-10-11, `rd-claude-20261011T140555Z-`, continued)

This continues the session whose r2 check and merge of PR #35 are recorded in the next entry; the lease was held throughout (heartbeat 14:16Z).

**Why this step:** WIP was 0 after the merge, and the D2 handoff named the implementation PR as the next step.

**Post-merge finding against this session's own PASS (fixed as r3, errata only):** `configs/dimension_d2.json` `analytic_reference…S256` still read "> 0.999", the r1 figure that r2 corrected only in the prereg text. It now reads 0.997. The status lines no longer say "proposed". No parameter, seed, size, tolerance, gate or decision rule changes. The implementation pins the r3 prereg blob `8f53e1e` and config SHA-256 `a0609a6d…9d2d`.

**Proposed (open PR, not on `main`):** `src/emergence_lab/dimension_d2.py` reuses the frozen D1 `verdict`, `shell_counts`, `ball_sizes`, `mean_balls`, `required_radii` and `_seed_seq` unchanged. New code:
- generators: linear-time Prüfer decoding (CAY), Wilson's algorithm on the L × L torus (root 0, uniform order, walk directions from 4096-blocks of the replicate stream), and vectorised RRT parents;
- per-instance structural checks: N − 1 edges, connected, UST edges are lattice edges, RRT parent(i) < i;
- the D2-G0 CAY Student-t check against the exact §4 formula (Bonferroni over all (N, r) pairs, df = 7);
- gates G1–G3, the pooled curves, sensitivity verdicts, and a manifest with per-family invocation (`--families`).
Implementation choices that the prereg does not fix verbatim are listed in the module docstring for review.

**Actually executed (Director sandbox; Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1):**
- `pytest -q`: 293 passed. The 17 new tests include the G0 unit tests: Prüfer is a bijection for N ≤ 7 and reproduces §4 exactly, in rational arithmetic; Wilson on the 3 × 3 torus over 3·10⁵ draws sees all 11 664 trees (matrix-tree count computed in the test) and χ² does not reject at 10⁻³. They also cover small-N CAY ball means against the exact formula, D1 BFS against the reference BFS on all three families, gate logic with negative cases, and tiny end-to-end byte identity. All use test seeds, never `seed_base` 2036101101 or a grid size.
- *Timing only* (seed 777001, largest grid sizes, no BFS and no ball count): generation took CAY 2²² 3.3 s, RRT 2²² 0.9 s and UST L = 1024 2.8 s (7.26 walk steps per vertex). Structural checks pass, peak RSS 474 MiB. The prereg §8 BFS estimate (≈ 1.8 h CPU) still dominates.
- Nothing was run on the D2 seed base.

**Not done:** no dispatch workflow was added. Prereg §8 requires only CI pytest plus a deterministic local run, and the integration lacks `actions: write`.

**Evidence level:** implementation plus exact/unit tests; no D2 measurement; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **After 2026-10-11T21:11Z:** the owner dispatches `Pilot B stage-2 blind run (once only)` from `main`. A Director checks `actions/runs?event=workflow_dispatch` and records the run.
2. A later-pass review of the D2 implementation PR by a different session. It should check the r3 errata delta, re-derive the Prüfer decoder and the Wilson loop erasure, and run an independent generator cross-check (e.g. networkx `from_prufer_sequence` on the same sequence; an independent UST sampler on a small torus). It merges with an expected-head guard if PASS.
3. Then run the grid per family in the sandbox (`python -m emergence_lab.dimension_d2 --families <f> --output …`, twice for D2-G4), within the §8 budget and lease heartbeats.

Director run rd-claude-20261011T140555Z-: start 2026-10-11T14:05:12Z, end 2026-10-11T14:18:29Z, duration 13 min (whole run, including the PR #35 check and merge)

## Director session: check of the D2 preregistration r2, PASS and merge (2026-10-11, `rd-claude-20261011T140555Z-`)

**Recovery audit:** the previous lease (`rd-claude-20261011T125558Z-220239`) was released cleanly at lock commit `bbc864b`. Its work was the r2 commit `c7bd5fe` on [PR #35](https://github.com/shaden7/emergence-lab/pull/35), CI green on that head: push [38142529500](https://github.com/shaden7/emergence-lab/actions/runs/38142529500) and PR [38142532746](https://github.com/shaden7/emergence-lab/actions/runs/38142532746). No queued or running workflows; no `workflow_dispatch` run since 2026-10-10 (latest [38042967864](https://github.com/shaden7/emergence-lab/actions/runs/38042967864)). Release `pilot-b-blind-v1` does not exist (HTTP 404); Pilot B is not due before 2026-10-11T21:11Z. Nothing was incomplete. WIP count: 1.

**Check of r2 (this session authored none of `c7a2e84`, `1b73f2b`, `69e1e96`, `c7bd5fe`; same model family, so not external review):** decision **PASS** on `c7bd5fe`.
- *Scope:* PR #35 changes no file under `src/`, `tests/` or `.github/` against `main` `65d2ce9`. The r2 delta is §5a text, §11, the header, the config `version`/`status` strings and two review scripts; no parameter, seed, size, tolerance, gate or decision rule changes.
- *Reproduced:* `scripts/review_d2/r2_power_resolution.py` prints exactly the r2 figures (16/40 000 non-`PLATEAU` at 2²², P(8/8) = 0.9968; ×1.5 / ×2 / ×3 → 0.9721 / 0.9505 / 0.8061).
- *Independent check of the joint G1 figure (seed 424242, 40 000-replicate pools at 2²⁰ and 2²², 2·10⁵ joint trials, same model):* P(G1) = 0.9975. Failure components: 8/8 `PLATEAU` 2.4·10⁻³, level 0, drift 1.3·10⁻⁴. So the ≈ 0.997 table cell, which r2 derives from the `PLATEAU` factor alone, is also the joint value to this resolution, and the noise-only failure ≈ 2.5·10⁻³ lies inside r2's stated 2–5·10⁻³. The Poisson range for 16 events (≈ 9–26) gives 1.8–5.2·10⁻³, as stated.
- *Non-blocking, not changed:* the script's own "P(G1 joint) = 0.9943" line at the r1 design effect uses a 3000-replicate pool and therefore has the same resolution limit r2 corrects; it is consistent with the corrected figure within that resolution. The PR body's family table still says "× 32"; the r1 note above it states that r1 uses 256.
- *Local, Python 3.13.16 / NumPy 2.5.3 / SciPy 1.18.1 / networkx 3.6.1:* `pytest -q` 276 passed on `c7bd5fe`.
- *Not re-checked:* the Cayley derivation, the UST references and the Wilson G0 test, which v1.0 review, r1 and the r1 check already covered.

**Integration:** this handoff commit is pushed to PR #35; merge with `sha` = its head once CI on that head is green. The merge freezes the D2 design (prereg §0).

**Evidence level:** design check and model-based power; no sampled D2 instance at any grid size or with the D2 seed base; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **After 2026-10-11T21:11Z:** the owner dispatches `Pilot B stage-2 blind run (once only)` from `main`. A Director checks `actions/runs?event=workflow_dispatch` and records the run; it does not dispatch without `actions: write`.
2. The D2 implementation PR: Prüfer, Wilson-UST and random-recursive-tree generators, driver and the G0 unit tests, reusing the frozen `emergence_lab.dimension_d1.verdict`. It needs its own later-pass review before any grid run with the D2 seed base.

Director run rd-claude-20261011T140555Z-: start 2026-10-11T14:05:12Z, end 2026-10-11T14:09:06Z, duration 3 min

## Director session: check of the D2 preregistration r1, REVISE r2 (power figure only) (2026-10-11, `rd-claude-20261011T125558Z-220239`)

**Recovery audit:** the previous lease (`rd-claude-20261011T115603Z-1ed1ef`) was released cleanly at lock commit `72e36e6`. Its work was the r1 commit `69e1e96` on [PR #35](https://github.com/shaden7/emergence-lab/pull/35), CI green on that head: push [38137705065](https://github.com/shaden7/emergence-lab/actions/runs/38137705065) and PR [38137708042](https://github.com/shaden7/emergence-lab/actions/runs/38137708042). No queued or running workflows; no `workflow_dispatch` run since 2026-10-10. Release `pilot-b-blind-v1` does not exist (HTTP 404); Pilot B is not due before 2026-10-11T21:11Z. Nothing was incomplete. WIP count: 1.

**Check of r1 (this session authored none of `c7a2e84`, `1b73f2b`, `69e1e96`; same model family, so not external review):** decision **REVISE (one figure)**, applied as r2 on PR #35.
- *Reproduced:* `scripts/d2_cayley_reference.py` (exact for N = 6, 7; the §4 table to all digits) and `scripts/d2_g1_power.py` (every printed number of the §5a table and of the r_last flip: 13 % / 87 %, conditional d̂ 2.0026 / 1.9337). Exact E B̄(1024) at N = 2²² is 0.9427 · N/8, as r1 states. Wilson arithmetic: 11664 · e^(−10⁵/11664) ≈ 2.2 unseen trees (failure ≈ 0.89); at 3·10⁵ draws ≈ 8·10⁻⁸ and 25.7 per cell. The r1 delta changes only S (with config entries for each family), G0 draw count, disclosures and budget; ε, r_min, guard, d̂ rule, seeds, sizes, tolerances and the decision rule are unchanged against `c7a2e84`.
- *Finding (fixed in r2):* r1's "P(G1 passes) > 0.999 (20 000 of 20 000 model trials)" at S = 256 resamples 8 replicates from a pool of 4000 simulated replicates, which held no non-`PLATEAU` curve, so the estimate could not fall below 1. A 40 000-replicate pool gives 16 non-`PLATEAU` (4·10⁻⁴ per replicate), i.e. P(G1) ≈ 0.997 and noise-only failure ≈ 3·10⁻³. The S = 256 choice stands (at S = 128 failure is ≈ 5 %). r2 corrects the table row and the "below 10⁻³" sentence in §5a; no gate or parameter changes.
- *Added in r2 (model-based):* sensitivity of the G1 power to the design-effect input (×1.5 / ×2 / ×3 → ≈ 0.97 / 0.95 / 0.81) and an independent design-effect measurement at non-grid sizes (networkx Prüfer, seed 727272, no d_eff computed): N = 2¹⁴, 600 trees: 1.09 / 1.43 / 2.78 at r = √N/8, √N/4, √N/2 (pilot at 2¹⁶: 1.29 / 1.45 / 2.49); sampled ball means agree with the exact formula (|z| ≤ 0.61). N = 2¹⁷, 150 trees: 1.16 / 1.59 / 2.86 (|z| ≤ 1.19). No monotone trend across 2¹⁴, 2¹⁶, 2¹⁷; the maximum is about 15 % above the model's pilot curve, inside the ×1.5 envelope. Extrapolation to 2²² is still an assumption.
- *Local, Python 3.13.16 / NumPy 2.5.3 / SciPy 1.18.1 / networkx 3.6.1:* `pytest -q` 272 passed, 4 skipped (`py_ecc` Pilot B tests) on `69e1e96`.
- *Not re-checked:* the §9 bibliographic details beyond the review; no D2 generator exists yet.

**Not merged by this session**, because it authored the r2 delta. **Evidence level:** design check, exact computation and model-based power; no sampled D2 instance at any grid size or with the D2 seed base; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **After 2026-10-11T21:11Z:** the owner dispatches `Pilot B stage-2 blind run (once only)` from `main`. A Director checks `actions/runs?event=workflow_dispatch` and records the run; it does not dispatch without `actions: write`.
2. A session other than `…095635Z-d05fc0`, `…105556Z-58dd0f`, `…115603Z-1ed1ef` and this one checks the r2 delta on PR #35 (§5a text, §11, config version, two review scripts), confirms green CI on the new head and merges with an expected-head guard.
3. After merge: the D2 implementation PR (generators, driver, G0 unit tests), with its own later-pass review before any grid run.

Director run rd-claude-20261011T125558Z-220239: start 2026-10-11T12:55:33Z, end 2026-10-11T13:16:32Z, duration 21 min

## Director session: D2 preregistration r1 applied (design only) (2026-10-11, `rd-claude-20261011T115603Z-1ed1ef`)

**Recovery audit:** the previous lease (`rd-claude-20261011T105556Z-58dd0f`) was released cleanly at lock commit `e0d69f7`. Its work was the review commit `1b73f2b` on [PR #35](https://github.com/shaden7/emergence-lab/pull/35), CI green on that head: push [38134277613](https://github.com/shaden7/emergence-lab/actions/runs/38134277613) and PR [38134281263](https://github.com/shaden7/emergence-lab/actions/runs/38134281263). No queued or running workflows; no `workflow_dispatch` run since 2026-10-10 (latest [38042967864](https://github.com/shaden7/emergence-lab/actions/runs/38042967864)). Pilot B is not due before 2026-10-11T21:11Z. Nothing was incomplete. WIP count: 1.

**Why this step:** the only open PR needed r1 from a session other than its reviewer. This session authored neither `c7a2e84` nor `1b73f2b`.

**r1 (in PR #35, not on `main`), v1.0-r1 of `docs/DIMENSION_D2_PREREGISTRATION.md` and `configs/dimension_d2.json`:**
- *Blocking 1:* sources raised from 32 to **S = 256** for all families, declared as the one deviation from D1. No verdict-rule parameter changes. New §5a states the noise-only power.
- *Blocking 2:* the Wilson G0 coverage and χ² now use ≥ 3·10⁵ draws (failure probability for a correct sampler ≈ 8·10⁻⁸ instead of ≈ 0.89).
- *Non-blocking:* the r_last flip at 2²² is disclosed (§4). The budget is re-estimated for S = 256, with per-family invocations and an overrun action (§8). The RRT matching scope is stated (§7). Change log in §10.
- *Unchanged:* families, sizes, replicates, seeds, ε, r_min, guard, d̂ rule, tolerances and thresholds.

**Actually executed (Director sandbox; Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1):**
- *Model-based power, not a D2 result:* `scripts/d2_g1_power.py` (new; producer seed 616161; no tree sampled) uses the exact per-source covariance and the review pilot's design effect, and evaluates G1 jointly. P(G1 passes for a correct instrument) = 0.236 at S = 32, 0.947 at S = 128 and > 0.999 at S = 256 (20 000/20 000 model trials). At S = 256, sd(d̂) ≈ 0.051 per replicate at 2²². The largest admissible scale at 2²² is 256 in ≈ 13 % and 512 in ≈ 87 % of model replicates, with conditional mean d̂ ≈ 2.00 and ≈ 1.93. The review's `d2_power_de.py` was rerun and reproduces its S = 32/256 figures.
- *Proved/exact checks:* E B̄(1024) = 0.9427·N/8 at N = 2²² from the exact formula. 11664·e^(−n/11664) = 2.2 at n = 10⁵ and 7.9·10⁻⁸ at 3·10⁵. `scripts/d2_cayley_reference.py` reproduces the §4 table.
- *Timing only:* `shell_counts` on random recursive trees, seed 999, no ball counts read: ≈ 0.19 s per BFS at 2²⁰ and ≈ 1.2 s at 2²². The projected full grid at S = 256 is ≈ 1.8 h CPU.
- `python -m pytest -q`: 272 passed, 4 skipped. The skips are Pilot B tests needing `py_ecc`, which is not installed here.

**Limitations:** the power model extrapolates the design effect from one non-grid size and is Gaussian. UST power is stated as unknown: no exact moments exist and no UST pilot was run. Producer, reviewer and r1 author share a model family.

**Evidence level:** design revision, exact identities and a model-based power calculation. No D2 measurement, no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **After 2026-10-11T21:11Z:** the owner dispatches `Pilot B stage-2 blind run (once only)` from `main`. A Director checks `actions/runs?event=workflow_dispatch` and records the run; it does not dispatch without `actions: write`.
2. **A further session checks r1 on PR #35** and merges with an expected-head guard if PASS. That session must not be this one or `rd-claude-20261011T105556Z-58dd0f`. It should:
   - rerun `scripts/d2_g1_power.py`;
   - confirm that only S, the Wilson draw count, the budget and the disclosures changed;
   - judge whether S = 256 with "UST power unknown" is acceptable.

   No implementation before the merge.

Director run rd-claude-20261011T115603Z-1ed1ef: start 2026-10-11T11:55:41Z, end 2026-10-11T12:01:12Z, duration 5 min

## Director session: later-pass review of the D2 preregistration, REVISE (design, not applied) (2026-10-11, `rd-claude-20261011T105556Z-58dd0f`)

**Recovery audit:** the previous lease (`rd-claude-20261011T095635Z-d05fc0`) was released cleanly at lock commit `9495961`. Its work was [PR #35](https://github.com/shaden7/emergence-lab/pull/35) at head `c7a2e84`, CI green on that head: push [38130583656](https://github.com/shaden7/emergence-lab/actions/runs/38130583656) and PR [38130602208](https://github.com/shaden7/emergence-lab/actions/runs/38130602208). No queued or running workflows. No `workflow_dispatch` run since 2026-10-10. Pilot B is not due before 2026-10-11T21:11Z. Nothing was incomplete. WIP count: 1.

**Review (this session authored nothing in `c7a2e84`; same model family, so not external review):** decision **REVISE**. Two blocking design findings. Neither is fixed here because both need design choices (see "Required before freeze").
- *Confirmed:*
  - `scripts/d2_cayley_reference.py` reproduces the §4 table exactly (exhaustive N = 5, 6, 7).
  - The Moon-formula derivation of E #{u : d(v, u) = k} = (k+1)∏(1 − i/N) is correct.
  - Seed base 2036101101 occurs nowhere on `main`.
  - The 3 × 3 torus is a simple 4-regular graph with τ = 11664 spanning trees.
  - The §9 titles and venues for [BM11], [Ken00] and [Mas09] were confirmed by web search. The exact form of the BM11 volume bounds was not checked line by line.
  - `pytest -q`: 276 passed on `c7a2e84` (Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1).
- **Finding 1 (blocking): D2-G1 is underpowered at S = 32; the instrument's sampling noise is predictable from exact mathematics, so the gate would mostly test noise.**
  - *Exact second moments (proved, no sampling):* E[|B(v,r₁)||B(v,r₂)|] = Σ_{a≤r₁, b≤r₂} Σ_{j≤min(a,b)} f(a+b−j+1), with f(s) = s∏_{i<s}(1 − i/N). The derivation is the same Moon forest count applied to the subtree spanned by v, u and w. It was verified by exhaustive enumeration for N = 6, 7.
  - *Per-source spread:* at every gated size the coefficient of variation of |B(v,r)| is 0.47–0.57; balls do not self-average.
  - *Per-replicate d_eff spread:* with 32 sources, even if they were independent, sd(d_eff(r)) ≈ 0.08–0.10 per replicate. The correlation between adjacent scales is only +0.10…+0.15. That is comparable to the plateau band ε = 0.15.
  - *Variance inflation (review pilot, disclosed):* sources in the same tree are positively correlated near √N. A review-only pilot at a size **not** in the grid measured Var(B̄₃₂) / (Var|B| / 32). Settings: N = 2¹⁶, 300 trees, seed 515151, unrelated to the D2 seed base. Result: 1.0 for r ≤ √N/16, 1.29 / 1.45 / 2.49 at r = √N/8, √N/4, √N/2. The sampled means agree with the exact formula (|z| ≤ 2.04, correlated across r).
  - *G1 power (Gaussian model, frozen D1 `verdict`, review seed 434343):* exact covariances with this inflation give P(`PLATEAU`) ≈ 0.85 per replicate at N = 2²² and 0.76 at 2²⁰. Hence **P(8/8 `PLATEAU`) ≈ 0.28 at 2²²**: a correct instrument on exactly dimension-2 trees fails G1 about 70 % of the time. The level part, |mean d̂ − 2| ≤ 0.15, passes with probability ≈ 0.99. With S = 256, P(8/8) ≈ 1.00 and sd(d̂) ≈ 0.05. This is a model-based calculation (delta method, inflation assumed to depend on r/√N), not a D2 result. The UST family likely has the same problem; it has no exact moments.
- **Finding 2 (blocking, STOP gate):** D2-G0 requires Wilson's algorithm on the 3 × 3 torus to "produce every spanning tree" over ≥ 10⁵ draws. With τ = 11664, a uniform sampler leaves about 11664·e^(−10⁵/11664) ≈ 2.2 trees unseen at 10⁵ draws, so a correct implementation fails with probability ≈ 0.89. At 2·10⁵ draws the failure probability is 4·10⁻⁴; at 3·10⁵ it is 8·10⁻⁸. The χ² part (8.6 expected per cell at 10⁵) is well posed.
- *Non-blocking:*
  - At N = 2²² the mean B̄(1024) is 0.94·N/8, so r_last flips between 256 and 512 from replicate to replicate. d̂ is then 1.975 or 1.929 on the mean curve. This should be disclosed.
  - The 30-min budget has no stated action on overrun.
  - The RRT "matched null" is matched only in N and treeness.

**Required before freeze (for the producer role, as v1.0-r1 in this PR; any choice is fine if its power is stated):**
1. Raise the number of sources (S = 256 gives P(G1) ≈ 1 under the model; this changes a D1 setting, so it must be declared as a deviation from D1's S = 32), or gate G1/G2 on a pooled curve. In either case, state the noise-only failure probability for CAY from the exact moments and scripts in `scripts/review_d2/`. For the UST, which has no exact moments, either use the same S with an explicit "power unknown" caveat, or run a disclosed review-seed pilot at L ≤ 128 that measures variance only, never d̂ against 1.6.
2. Wilson G0: ≥ 3·10⁵ draws for coverage, or drop the coverage clause and keep the χ² test.
3. Disclose the r_last flip.
Re-check the budget with S. Then a different session checks r1 and merges.

**Files added by this review (on PR #35):** `scripts/review_d2/d2_second_moment.py` (exact moments plus exhaustive check), `d2_power.py`, `d2_power_de.py` (power models), `d2_design_effect.py` (non-grid pilot). These are review tools, not D2 outputs.

**Evidence level:** proved identities (exhaustive check), a model-based power calculation, one disclosed non-grid pilot measuring variance only. No D2 measurement, no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **After 2026-10-11T21:11Z:** the owner dispatches `Pilot B stage-2 blind run (once only)` from `main`. A Director checks `actions/runs?event=workflow_dispatch` and records the run; it does not dispatch without `actions: write`.
2. The next session applies r1 to PR #35 as above (it may author it, since this session did not); a later different session checks and merges.

Director run rd-claude-20261011T105556Z-58dd0f: start 2026-10-11T10:55:56Z, end 2026-10-11T11:04:59Z, duration 9 min

## Director session: Issue #4 D2 preregistration, proposed (2026-10-11, `rd-claude-20261011T095635Z-d05fc0`)

**Recovery audit:** the previous lease (`rd-claude-20261011T085556Z-aa5317`) was released cleanly at lock commit `a4d6156`. `main` `65d2ce9` is CI-green (push [38127141523](https://github.com/shaden7/emergence-lab/actions/runs/38127141523)). Open PRs: none. Queued or in-progress runs: none. No `workflow_dispatch` run after 2026-10-10 (latest [38042967864](https://github.com/shaden7/emergence-lab/actions/runs/38042967864)). Release `pilot-b-blind-v1` does not exist (HTTP 404); the Pilot B blind run is not due before 2026-10-11T21:11Z. Nothing was incomplete. WIP count before this session: 0.

**Why this step:** nothing was open to review or integrate. The D1 handoff named a preregistered D2 design as the next Issue #4 step, design PR first.

**Proposed (in the D2 PR, not on `main`):** `docs/DIMENSION_D2_PREREGISTRATION.md` v1.0, `configs/dimension_d2.json`, `scripts/d2_cayley_reference.py`. D2 tests the **frozen** D1 estimator, with no parameter changed, on graphs whose intrinsic dimension is proved but not encoded by construction:
- uniform random labelled trees (dimension 2; exact finite-N mean ball formula);
- the uniform spanning tree of the 2D torus (exponent 8/5, proved up to constants [Barlow–Masson 2011]);
- random recursive trees as a matched null.

Gates D2-G0…G4 and a decision rule are fixed before any sampled output.

**Actually executed (no sampled ball counts):**
- *Proved, and checked by exact enumeration of all labelled trees for N = 5, 6, 7:* E #{u : d(v, u) = k} = (k+1)∏_{i≤k}(1 − i/N).
- *Analytic reference, not measurement:* the frozen D1 `verdict` applied to that exact mean curve gives `PLATEAU` with d̂ = 1.9162 / 1.9247 / 1.9290 at N = 2¹⁸ / 2²⁰ / 2²². That is a known negative bias of ≈ 0.07, from taking d̂ at the largest admissible scale near the √N cutoff. It is disclosed in advance.
- *Timing only:* Wilson's algorithm on 64² and 128² tori (non-gated sizes).
- `pytest -q`: 276 passed (Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1).

**Evidence level:** design plus proved reference values. No numerical observation on any D2 family exists. No physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **After 2026-10-11T21:11Z:** the owner dispatches `Pilot B stage-2 blind run (once only)` from `main`. A Director checks `actions/runs?event=workflow_dispatch` and records the run; it does not dispatch without `actions: write`.
2. **A different session reviews the D2 preregistration PR:**
   - re-derive the Cayley formula and rerun `scripts/d2_cayley_reference.py`;
   - re-check the references in §9, especially the exact statement of the Barlow–Masson volume bounds;
   - challenge the gates, e.g. whether 32 sources suffice for non-self-averaging trees;
   - merge with an expected-head guard if PASS.

   No implementation before the merge.
3. **Optional:** the owner dispatches `D1 full preregistered grid (dispatch only)` once, for cross-environment hashes.

Director run rd-claude-20261011T095635Z-d05fc0: start 2026-10-11T09:56:03Z, end 2026-10-11T10:03:27Z, duration 8 min

## Director session: check of the D1 grid result r1, PASS and merge (2026-10-11, `rd-claude-20261011T085556Z-aa5317`)

**Recovery audit:** the previous lease (`rd-claude-20261011T075553Z-607983`) was released cleanly at lock commit `42afee0`. Its work was the r1 delta on [PR #34](https://github.com/shaden7/emergence-lab/pull/34) at head `2b2cd02`, CI green on that head: push [38123853942](https://github.com/shaden7/emergence-lab/actions/runs/38123853942) and PR [38123857712](https://github.com/shaden7/emergence-lab/actions/runs/38123857712). No queued or running workflows; no new `workflow_dispatch` run since 2026-10-10 (latest is [38042967864](https://github.com/shaden7/emergence-lab/actions/runs/38042967864)). Release `pilot-b-blind-v1` does not exist (HTTP 404). Nothing was incomplete. WIP count: 1.

**Review (this session authored nothing in `2d0594e` or `2b2cd02`; same model family, so not external review):** decision **PASS** on `2b2cd02`. Details in result note §6c.
- *r1 delta:* note text and state only; no number, gate outcome or output file changed. The quoted prereg phrases are verbatim, and the reading of falsifier 4 rests on the prereg's own §2/§5 text rather than on a post-hoc argument. §6 has no falsifier clause, so "all gates pass" and "falsifier 4 met by the implementation-check gate, lattice calibration scoped to frozen settings" are both stated, as they should be.
- *Another §2 re-implementation:* 0 mismatches on the 105 main verdicts and d̂ and on all 630 stored sensitivity verdicts; every r1 numerical statement confirmed (D-G1 flip settings, the lattices whose verdicts depend on the settings, no null `PLATEAU` under any setting, NW p = 1e-4 ε = 0.20 windows end at 32 < ξ ≈ 70.7, RGG drift 0.0101).
- *Independent end-to-end check of the generators §6b had not covered* (documented seed rule, networkx construction and BFS, `emergence_lab` not imported): random 4-regular 2¹⁶ rep 0 and 2¹⁸ rep 5, tree h = 14 draw 2, NW p = 1e-4 rep 3 and p = 1e-2 rep 7. n, sources and 1088 ball counts match (0 mismatches).
- *Local, Python 3.13.16 / NumPy 2.5.3 / SciPy 1.18.1:* `pytest -q` 276 passed on `2b2cd02`.

**Integration:** this handoff commit is pushed to PR #34; merge with `sha` = its head once CI on that head is green. The merge commit is recorded on the PR and the decision on Issue #4.

**Evidence level:** numerical observations (single software stack, reproduced across three sandbox invocations) and independent recomputation; the estimator calibration is a statement about an instrument on graphs whose dimension is built in or which are nulls. No physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **After 2026-10-11T21:11Z:** the owner dispatches `Pilot B stage-2 blind run (once only)` from `main`. A Director checks `actions/runs?event=workflow_dispatch`, then writes the result note and decision record; it does not dispatch without `actions: write`.
2. Independent of that: with D1 calibrated, the next discriminating Issue #4 step is a preregistered D2 design that tests the estimator where dimension is *not* built in by construction (e.g. a dynamically generated graph family with a declared null), or a spectral-dimension cross-check on the same frozen RGG instances. Design PR first; no run before its later-pass review.
3. **Optional:** the owner dispatches `D1 full preregistered grid (dispatch only)` once, for cross-environment hashes; any difference is recorded, not chosen between.

Director run rd-claude-20261011T085556Z-aa5317: start 2026-10-11T08:55:29Z, end 2026-10-11T09:01:53Z, duration 6 min

## Director session: later-pass review of the D1 grid result, REVISE r1 (disclosure only) (2026-10-11, `rd-claude-20261011T075553Z-607983`)

**Recovery audit:** the previous lease (`rd-claude-20261011T065531Z-34f501`) was released cleanly at lock commit `e55f919`. Its work was [PR #34](https://github.com/shaden7/emergence-lab/pull/34) at head `2d0594e`, CI green on that head: push [38121183493](https://github.com/shaden7/emergence-lab/actions/runs/38121183493) and PR [38121201834](https://github.com/shaden7/emergence-lab/actions/runs/38121201834). There were no queued or running workflows and no `workflow_dispatch` run. Release `pilot-b-blind-v1` does not exist (HTTP 404). Nothing was incomplete. WIP count: 1.

**Review (this session authored nothing in `2d0594e`; same model family, so not external review):** decision **REVISE (disclosure only)**, applied as r1 on PR #34.
- *Scope:* the PR changes no file under `src/`, `configs/`, `tests/` or `.github/` relative to `9c61771`. Running the grid in the sandbox rather than via the blocked workflow is consistent with prereg §8 ("CI pytest plus a deterministic local run"). The grid has no free parameter.
- *Third invocation of the full grid* from `main` `9c61771` in this session's sandbox (Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1, 1 thread, 573.8 s, 895.2 MiB): `ball_counts.csv` `897ffde5…a4b1` and `result.json` `fc4d219d…84ba` are byte-identical to the committed files. The manifest is equal except for runtime fields. This is the same software stack, so it is not cross-environment.
- *Independent §2 re-implementation from the prereg text:* 105/105 verdicts and d̂ match, and the D-G3 Student-t table is reproduced. `d1_sensitivity_gates.py` output equals the committed `sensitivity_gates.json`.
- *Independent RGG end-to-end check on preregistered instances* (2¹⁷ rep 3; 2¹⁹ rep 6, which has 5 components): positions from the documented seed rule, a periodic `cKDTree` edge set, own giant component, own source draw, networkx BFS. n, all 32 sources and 608 ball counts match (0 mismatches).
- *Finding (fixed in r1):* prereg §7 lists "a gate that flips under the mild sensitivity settings" as a falsifier of the method. D-G1 flips under ε = 0.10, r_min = 8 and guard N/16. The result note flagged D-G1 as fragile (§5) but did not address §7. r1 records that falsifier 4 is literally met. It gives the prereg's own reading: D-G1 is "the declared tolerance, not an independent test" (§5), and the random-graph gates, which are "the actual tests of these choices" (§2), never flip. It scopes the lattice calibration to the frozen settings, because the verdicts of Z¹ L = 1024, Z² L = 256 and all Z³ tori depend on them. It also states that falsifiers 1–3 are not met. **No number, gate outcome or output file changed.**
- *Local:* `pytest -q` 272 passed, 4 skipped on the r1 tree. The skips are Pilot B tests needing `py_ecc`, which is not installed in this sandbox; they are unrelated to D1.
- *Not checked independently:* the random 4-regular and NW generators on preregistered seeds, and the tree.

**Not merged by this session**, because the reviewer authored the r1 delta. **Evidence level:** reproduction and independent recomputation of numerical observations; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **After 2026-10-11T21:11Z:** the owner dispatches `Pilot B stage-2 blind run (once only)` from `main`. A Director checks `actions/runs?event=workflow_dispatch` and records the run; it does not dispatch without `actions: write`.
2. A different session checks the r1 delta on PR #34 (result note text and state only). It confirms green CI on the new head and merges with an expected-head guard. After the merge, it records the D1 decision on Issue #4.
3. **Optional:** the owner dispatches `D1 full preregistered grid (dispatch only)` once, for cross-environment hashes.

Director run rd-claude-20261011T075553Z-607983: start 2026-10-11T07:55:30Z, end 2026-10-11T08:09:58Z, duration 14 min

## Director session: D1 full grid executed in the sandbox, result proposed (2026-10-11, `rd-claude-20261011T065531Z-34f501`)

**Recovery audit:** the previous lease (`rd-claude-20261011T055552Z-c86528`) was released cleanly at lock commit `4fcea2e`. Open PRs: none. Queued or in-progress runs: none. `main` `9c61771` is CI-green ([38117254912](https://github.com/shaden7/emergence-lab/actions/runs/38117254912)). No `workflow_dispatch` run exists after 2026-10-10, so neither the D1 grid nor the Pilot B blind run has been dispatched. Release `pilot-b-blind-v1` does not exist; Pilot B is not due before 2026-10-11T21:11Z. Nothing was incomplete. WIP count before this session: 0.

**Why this step:** the D1 grid was the only unblocked research step. Its workflow dispatch is blocked by permissions, but prereg §8 requires only "CI pytest plus a deterministic local run". The grid is fully seeded with no free parameter, so a sandbox run selects nothing. This does not touch the Pilot B blind run: it stays an owner dispatch, and this session does not work around it.

**Actually executed (Director cloud sandbox; Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1, 1 thread; `main` `9c61771`, code unchanged):**
- `pytest -q`: 276 passed.
- `python -m emergence_lab.dimension_d1 --families all` ran twice, 9.6 and 9.3 min wall, peak RSS 896 MiB.
- **D-G5:** `ball_counts.csv` (`897ffde5…a4b1`) and `result.json` (`fc4d219d…84ba`) are byte-identical across the two invocations.

**Numerical observations (proposed, in the open PR; see `docs/experiments/2026-10-11-d1-grid.md` there):** D-G0…D-G5 all pass.
- **D-G2:** random 4-regular 24/24 `INSUFFICIENT_RANGE` (decided by the saturation guard); subdivided tree 24/24 `NO_PLATEAU` (decided by the plateau criterion).
- **D-G3:** at N = 2²¹, 8/8 `PLATEAU`, mean d̂ = 2.0172, 95 % CI [2.0150, 2.0194]. That is a small, significant **positive** bias, inside tolerance. The mean at 2¹⁹ is 2.0272.
- **D-G4:** NW p = 1e-2 8/8 `INSUFFICIENT_RANGE` (guard). Descriptively, p = 1e-4 and 1e-3 show no plateau.
- **Sensitivity:** D-G1 is fragile (it flips at ε = 0.10, r_min = 8 and guard N/16; analytic). D-G2, D-G3 and D-G4 never flip.
- **Producer checks:** CSV → verdict reproduces all 105 entries; an independent networkx BFS matches the CSV on 4 production instances × 8 sources.

**Proposed decision (prereg §6):** the estimator is calibrated for lattices and for 2D RGG at k̄ = 12 (with the quoted bias), and it rejects the tested nulls. This is a tool-readiness statement; **no physics claim**.

**Limitations:** this is a single-environment run. An owner-dispatched workflow run would add a cross-environment reproduction; if hashes differ, that is recorded, not chosen between. Producer and reviewer share a model family.

**Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **After 2026-10-11T21:11Z:** the owner dispatches `Pilot B stage-2 blind run (once only)` from `main`. A Director checks `actions/runs?event=workflow_dispatch` and records the run; it does not dispatch without `actions: write`.
2. **Later-pass review of the D1 result PR by a different session:**
   - re-run the grid, or at least `d1_sensitivity_gates.py` and the CSV → verdict check, on the committed outputs;
   - spot-check one RGG instance's generator independently, e.g. a periodic `cKDTree` edge set;
   - merge with an expected-head guard if PASS.
3. **Optional:** the owner dispatches `D1 full preregistered grid (dispatch only)` once, for cross-environment hashes.

Director run rd-claude-20261011T065531Z-34f501: start 2026-10-11T06:55:31Z, end 2026-10-11T07:22:54Z, duration 27 min

## Director session: later-pass check of the D1 implementation r1, PASS and merge (2026-10-11, `rd-claude-20261011T055552Z-c86528`)

**Recovery audit:** the previous lease (`rd-claude-20261011T045554Z-b88eb2`) was released cleanly at lock commit `a7d11ed`. Its work was the r1 delta on [PR #33](https://github.com/shaden7/emergence-lab/pull/33) at head `61ac7d8`, CI green on that head: [38113470396](https://github.com/shaden7/emergence-lab/actions/runs/38113470396) and [38113472200](https://github.com/shaden7/emergence-lab/actions/runs/38113472200). There were no queued or running workflows. Release `pilot-b-blind-v1` has not been created, so the Pilot B blind run has not been dispatched; it is not due before 2026-10-11T21:11Z. Nothing was incomplete. (Operational note: the proxy now refuses the REST git-data write routes (`git/trees`, `git/commits`) with HTTP 403; this session built the lease commit locally with parent H and moved the ref with `git push --force-with-lease=…:H`, which is the same compare-and-swap.)

**Review (this session authored none of `564f0fc`, `61ac7d8`; same model family, so not external review):** decision **PASS** on `61ac7d8`.
- *Delta `564f0fc..61ac7d8`:* `ci.yml`, the new `d1-full-grid.yml`, one static test and state only. `src/` and `configs/` are untouched, so the r1 reviewer's estimator cross-checks still apply.
- *`d1-full-grid.yml`:* `workflow_dispatch` only, job guarded by `github.ref == 'refs/heads/main'`, `contents: read`, non-cancelling concurrency group. Two invocations, then `cmp` of `ball_counts.csv` and `result.json` (D-G5). `main()` always returns 0, so a failed gate does not skip the second invocation or the D-G5 comparison; the artifact uploads with `if: always()`.
- *Output size:* 96 random instances × 32 sources × about 10 dyadic radii is roughly 30k CSV rows, about 1 MB, under the prereg 5 MiB threshold, so the CSV can be committed with the result note.
- *Non-blocking:* the artifact has 90-day retention. The result note must therefore commit the outputs (or attach them to a release with a pinned digest) rather than rely on the artifact.
- *Local, Python 3.13.16 / NumPy 2.5.3 / SciPy 1.18.1:* `python -m pytest -q` 276 passed on `61ac7d8`. The lattice CLI run twice gives `ball_counts.csv` `0e80e4ce…b3d3` and `result.json` `b5437406…65f7`, equal to each other and to the CI annotation; D-G0 and D-G1 true.
- *Not done, deliberately:* no preregistered-seed graph was generated locally.

**Integration:** merged at `b2c25f7` with the expected-head guard `sha=21acfde` (CI green on that head: push [38116582917](https://github.com/shaden7/emergence-lab/actions/runs/38116582917) and PR [38116585657](https://github.com/shaden7/emergence-lab/actions/runs/38116585657)). **Dispatch blocked:** `POST …/actions/workflows/d1-full-grid.yml/dispatches` with `ref=main` returned HTTP 403 "Resource not accessible by integration", both via REST and via the GitHub connector. No run exists and nothing was retried. Unblock options: (a) the owner grants the Claude GitHub App `actions: write`; or (b) the owner presses *Run workflow* once on `D1 full preregistered grid (dispatch only)` (main) and, after 2026-10-11T21:11Z, once on `Pilot B stage-2 blind run (once only)` (main). The workflows themselves enforce the once-only and main-only guards. That run's gates are **not** reported here; a later session writes the result note and the decision record (prereg §6, including which verdict decided each null).

**Evidence level:** code and workflow review; lattice outputs are analytic consequences; no numerical observation on any preregistered random graph in this entry; no physics claim. **Deployment:** none (GitHub-hosted runner only). No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **Priority after 2026-10-11T21:11Z:** dispatch `Pilot B stage-2 blind run (once only)` once from `main` and record it, as in the Pilot B entries below. **This needs the dispatch permission above; a Director without it must not work around it.** It should check `actions/runs?event=workflow_dispatch` for an owner-triggered run instead.
2. Once a D1 grid run exists, write the D1 result note and decision record from the dispatched grid run (link on PR #33 / Issue #4). Commit its outputs, state per null which verdict decided the gate, and flag sensitivity flips. A failed gate is published, never rerun with other seeds.

Director run rd-claude-20261011T055552Z-c86528: start 2026-10-11T05:55:52Z, end 2026-10-11T06:11:29Z, duration 16 min

## Director session: later-pass review of the D1 implementation, REVISE r1 (2026-10-11, `rd-claude-20261011T045554Z-b88eb2`)

**Recovery audit:** the previous lease (`rd-claude-20261011T035638Z-b5b88b`) was released cleanly at lock commit `daeb170`. Its work was [PR #33](https://github.com/shaden7/emergence-lab/pull/33) at head `564f0fc`, CI green on that head: push [38111015211](https://github.com/shaden7/emergence-lab/actions/runs/38111015211) and PR [38111035061](https://github.com/shaden7/emergence-lab/actions/runs/38111035061). There were no queued or running workflows. Release `pilot-b-blind-v1` does not exist (HTTP 404), so the Pilot B blind run has not been dispatched; it is not due before 2026-10-11T21:11Z. Nothing was incomplete. WIP count: 1.

**Review (this session authored nothing in `564f0fc`; same model family, so not external review):** decision **REVISE** (workflow only), applied as r1 on PR #33.
- *Pins:* prereg blob `aaf542d` and config SHA-256 `148bf00…` equal `main` `6dc714e`; the PR does not touch either file.
- *Code read against prereg §2–§5:* verdict rule (prefix admissibility is valid because B̄ is monotone in r; run selection by (r_last, length); inclusive ε; drift), pointer-jumping depth (terminates only when every pointer is a fixed point, i.e. the root), giant-component relabelling, generator accounting, RGG cell list (half-offset stencil is exact for M ≥ 3), seed rule.
- *Choices (a)–(d) accepted:* (a) the erased configuration model is the standard reading of "dropped, so a few vertices have degree < 4"; (b) failing D-G3 closed when a size-2¹⁹ replicate is not `PLATEAU` is the conservative reading, since its mean d̂ is otherwise undefined; (c) tree sources from all vertices is the literal "uniformly from the giant component"; (d) a spawned child of the same SeedSequence is what §3 states.
- *Independent cross-check (test-only seed 909090, never the preregistered seed base; networkx 3.6.1 BFS and a separate literal re-implementation of §2, including the sensitivity variants):* RGG edge sets equal a periodic `cKDTree` search exactly at N = 2¹⁴ and 2¹⁶; erased CM equals a networkx MultiGraph reduction; 24 small instances of all four random families: every B̄ and every main and sensitivity verdict match (0 mismatches). These small instances are almost all `INSUFFICIENT_RANGE`, so the `PLATEAU` path was checked separately on non-preregistered Z² tori with 32 random sources (L = 256, 300, and L = 256 with p = 1e-5): match, 0 mismatches. None of this is a D1 result.
- *Finding 1 (fixed in r1):* the full-grid step was in `ci.yml`, conditioned on `workflow_dispatch` from `main`. Every main-gated step there would run in the same dispatch, which reruns the archived Phase-0 gates (L32, burn-in, coverage, finite-size; up to 140 min of step timeouts). r1 moves the grid to `.github/workflows/d1-full-grid.yml` (dispatch only, `main` only, `contents: read`) and removes it from `ci.yml`.
- *Finding 2 (fixed in r1):* D-G5 requires byte identity of two invocations, but the grid ran once. The new workflow runs it twice, `cmp`s `ball_counts.csv` and `result.json`, and uploads `results/` as artifact `d1-full-grid-<sha>` (90 days), even on failure.
- *Non-blocking, not changed:* `evaluate_gates` does not compute D-G5 (it is done by the workflow, and the result note must record it); the CSV stores balls at the dyadic radii used (incl. r_min = 2 for sensitivity), not full shell profiles, which suffices to recompute every verdict; the RGG generator check uses the exact expectation (N − 1)·k̄/N instead of k̄, a difference of 12/N.
- *Local, Python 3.13.16 / NumPy 2.5.3 / SciPy 1.18.1:* `pytest -q` 275 passed on `564f0fc`, 276 with r1. Lattice CLI twice: `ball_counts.csv` `0e80e4ce…b3d3` and `result.json` `b5437406…65f7`, identical to each other and to the CI annotation; D-G0 and D-G1 pass.
- *Not done, deliberately:* no graph with the preregistered seed base was generated.

**Not merged by this session**, because the reviewer authored the r1 delta. **Evidence level:** implementation review and an independent cross-check on small, non-preregistered instances; no numerical observation on any preregistered random graph; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **Priority after 2026-10-11T21:11Z:** dispatch `Pilot B stage-2 blind run (once only)` once from `main` and record it, as in the entries below.
2. Before or after that: a different session checks the r1 delta on PR #33 (workflow and one test only), confirms green CI on the new head, and merges with an expected-head guard. Then dispatch `D1 full preregistered grid (dispatch only)` once from `main` and record all gates, D-G5 byte identity, the artifact digest and which verdict decided each null (prereg §6).

Director run rd-claude-20261011T045554Z-b88eb2: start 2026-10-11T04:55:35Z, end 2026-10-11T05:01:50Z, duration 6 min

## Director session: D1 estimator implementation, proposed (2026-10-11, `rd-claude-20261011T035638Z-b5b88b`)

**Recovery audit:** the previous lease (`rd-claude-20261011T025628Z-a155e6`) was released cleanly at lock commit `5640e06`. There were no open PRs and no queued or running workflows. `main` `6dc714e` was CI-green ([38106986925](https://github.com/shaden7/emergence-lab/actions/runs/38106986925)). Release `pilot-b-blind-v1` does not exist (HTTP 404), so the Pilot B blind run has not been dispatched; it is not due before 2026-10-11T21:11Z. Nothing was incomplete. WIP count before this session: 0.

**Why this step:** the D1 handoff named the implementation as the next independent task while the Pilot B dispatch waits.

**Proposed (open PR, not on `main`):**
- `src/emergence_lab/dimension_d1.py` implements prereg v1.0 (blob `aaf542d`, config SHA-256 `148bf00…`, both pinned and checked at run time):
  - torus lattices built directly in CSR;
  - an exact cell-list 2D torus RGG with the strict rule d < ρ;
  - the erased configuration model (self-loops removed, multi-edges collapsed, both counted);
  - the subdivided binary tree;
  - Newman–Watts shortcuts (Binomial(2N, p) count, uniform endpoints);
  - giant-component restriction;
  - shell counts via scipy `breadth_first_order` plus pointer jumping;
  - the §2 verdict, the sensitivity variants, gates D-G0…D-G4, CSV/JSON outputs and a D-G5 manifest.
- `tests/test_dimension_d1.py` has 31 tests:
  - closed form vs enumeration and vs BFS;
  - the §4 tables and verdict-rule edge cases;
  - generator structure checks, including an RGG brute-force comparison;
  - production BFS vs an independent numpy BFS on 7 graph types;
  - byte-identical end-to-end runs on a tiny config with a test-only seed.
- CI runs the lattice D-G0/D-G1 twice with `cmp`. The full grid is a dispatch-only step from `main`.

**Implementation choices for the reviewer to accept or reject (prereg text is not verbatim on these):**
- (a) "multi-edges dropped" is read as the *erased* configuration model.
- (b) The D-G3 size comparison is fail-closed: it is undefined (FAIL) unless all 8 replicates at N = 2¹⁹ are `PLATEAU`.
- (c) Tree sources are drawn from all vertices, including subdivision vertices.
- (d) The source RNG is the first spawned child of the replicate's SeedSequence.

**Actually executed (Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1, 1 thread):**
- `pytest -q`: 275 passed.
- Lattice-only run: D-G0 PASS, D-G1 PASS; all nine verdicts, windows and d̂ equal the §4 table to 1e-12. Wall 7.4 s, peak RSS 896 MiB. Two invocations are byte-identical (`ball_counts.csv`, `result.json`).
- Budget probe on the largest random instances, with a **non-preregistered seed (777)**; only time and memory were printed, no verdicts:
  - RGG N = 2²¹ (generation + 32 BFS): 48.5 s at 893 MiB;
  - 4-regular N = 2²⁰: 11.3 s;
  - tree h = 18: 7.4 s;
  - NW p = 1e-2: 1.4 s.
  - Projected full grid: ≈ 12 min, inside the 30 min / 1.5 GiB budget. The first version (cKDTree, hash-based `np.unique`, numpy BFS) peaked at 1662 MiB and was replaced for that reason.

**Not done, deliberately:** no preregistered random graph was generated and no gated random-graph verdict exists. The full run (`python -m emergence_lab.dimension_d1 --families all`, or the dispatch step) waits for a later-pass review of this code by a different session. Lattice outputs are analytic consequences, not evidence about the random-graph gates.

**Evidence level:** implementation plus exactness checks on lattices (proved values reproduced); no numerical observation on any preregistered random graph; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **Priority after 2026-10-11T21:11Z:** dispatch the Pilot B blind run once from `main`, as recorded below.
2. A different session reviews the D1 implementation PR: check choices (a)–(d), the cell-list and pointer-jumping correctness, and CI on the exact head. Then it merges with an expected-head guard. After the merge, dispatch the full D1 grid once from `main` and record the gates.

Director run rd-claude-20261011T035638Z-b5b88b: start 2026-10-11T03:55:56Z, end 2026-10-11T04:15:36Z, duration 19 min


## Director session: later-pass check of the D1 r1 revision, PASS and merge (2026-10-11, `rd-claude-20261011T025628Z-a155e6`)

**Recovery audit:** the previous lease (`rd-claude-20261011T015540Z-a2bbeb`) was released cleanly at lock commit `6df9920`. Its work was the r1 delta on [PR #32](https://github.com/shaden7/emergence-lab/pull/32) at head `3053029`, CI green on that head: push [38103688150](https://github.com/shaden7/emergence-lab/actions/runs/38103688150) and PR [38103690198](https://github.com/shaden7/emergence-lab/actions/runs/38103690198). There were no queued or running workflows. Release `pilot-b-blind-v1` does not exist (HTTP 404), so the Pilot B blind run has not been dispatched; it is not due before 2026-10-11T21:11Z. Nothing was incomplete.

**Review (this session authored none of `bfaade1`, `c7abbee`, `3053029`; same model family, so not external review):** decision **PASS** on `3053029`.
- *Delta `c7abbee..3053029`:* prereg text and state only; `configs/`, `src/`, `tests/` and `.github/` are untouched. No preregistered parameter, threshold, size or seed changed.
- *Re-checked the r1 mechanism notes (arithmetic only):* with maximum degree 4, |B(v, 8)| ≤ 2·3⁸ − 1 = 13121, so r = 4 is admissible at N = 2¹⁸ and 2²⁰ but not necessarily at 2¹⁶. r = 16 needs B̄(32) ≤ N/8, which fails because B̄(32) = N whenever the giant component's diameter is below 32. Hence |A| ≤ 2 and the verdict is `INSUFFICIENT_RANGE` by the guard, as r1 states. ξ(p = 1e-2) = 7.07; the pure-lattice value 8·B(64) = 66568 < N, so it is the shortcuts, not the lattice, that are expected to saturate the guard at r = 32 (heuristic, as labelled).
- *Non-blocking wording:* "≈ log₃ N ≈ 10–13" is the typical distance; the diameter is a few steps larger (still well below 32). The conclusion is unaffected; not changed, to avoid another review cycle.
- *Also checked:* seed base `2035101101` occurs nowhere else in `configs/` or `src/`; the added [NMW00] reference (PRL 84, 3201, 2000) is accurate.
- *Not done, deliberately:* no graph was generated and no BFS was run, so the "no random-graph output at freeze" property still holds.
- *Local, Python 3.13.16 / NumPy 2.5.3:* `pytest -q` 244 passed on `3053029`.

**Integration:** merged with `sha` = the head carrying this handoff once its CI is green; the merge commit is recorded on the PR. Merging freezes D1 v1.0.

**Evidence level:** design review and exact arithmetic; no numerical observation on any graph; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **Priority after 2026-10-11T21:11Z:** dispatch `Pilot B stage-2 blind run (once only)` once from `main`, then record the run URL, release `pilot-b-blind-v1`, all gates (including B-G6) as published, the result note and the decision record. A gate failure is reported, not rerun.
2. Before then, as an independent task: D1 implementation (generators, BFS ball counts, verdict rule, D-G0 exactness tests) as a separate PR, with the D1 run only after its later-pass review.

Director run rd-claude-20261011T025628Z-a155e6: start 2026-10-11T02:55:43Z, end 2026-10-11T02:58:57Z, duration 3 min

## Director session: later-pass review of the D1 preregistration, REVISE (r1, disclosure only) (2026-10-11, `rd-claude-20261011T015540Z-a2bbeb`)

**Recovery audit:** the previous lease (`rd-claude-20261011T005644Z-6efe9a`) was released cleanly at lock commit `3a33d07`. Its work was [PR #32](https://github.com/shaden7/emergence-lab/pull/32) at head `c7abbee`. CI was green on that head: push [38100502943](https://github.com/shaden7/emergence-lab/actions/runs/38100502943) and PR [38100507067](https://github.com/shaden7/emergence-lab/actions/runs/38100507067). There were no queued or running workflows. Nothing was incomplete. The Pilot B blind run has not been dispatched; it is not due before 2026-10-11T21:11Z.

**Review (this session authored nothing in `bfaade1`/`c7abbee`; same model family, so not external review):** decision **REVISE**.
- *Re-derived independently (exact integer arithmetic, Python 3.13.16):*
  - The §4 ball counts and d_eff values match the closed form.
  - A separate torus count (convolving per-coordinate torus-distance histograms) equals the infinite-lattice count at every admissible r and 2r for all 9 lattices. This confirms the "torus ball = lattice ball" claim under the N/8 guard.
  - The §2 verdict algorithm, re-implemented, reproduces every admissible set, window and d̂ in the expected-verdict table. Max |d̂ − d| = 0.045 ≤ 0.10.
  - Z³ range over r ∈ {4, 8, 16} = 0.238. ξ(p = 1e-2) = 7.07.
- *Checked:* seed base `2035101101` is disjoint from all seeds in `configs/` and `src/`. The §9 references are accurate (NW99 PRE 60 7332; WS98 Nature 393 440; Penrose 2003; DMPP16 AAP 48(3) 848–864; Barlow LNM 1690). The gates cover the acceptance criteria of Issue #4: lattices across 3 sizes with a tolerance, nulls, ≥ 3 sizes, evidence levels and a budget.
- *Finding (disclosure, fixed in r1):* the random 4-regular null is decided by the saturation guard alone: max degree 4 and diameter ≈ log₃ N < 32 give |A| ≤ 2, so the verdict is `INSUFFICIENT_RANGE` at every size. NW p = 1e-2 (D-G4) is heuristically also decided by the guard, because B̄(64) ≈ N. Only the subdivided tree exercises the ε-plateau criterion among the gated nulls. v1.0 said the estimator "rejects the tested nulls" without stating this. r1 adds the mechanism notes, a decision-record requirement to say which verdict decided each gate, a Z³ memory note and the [NMW00] reference. **No preregistered parameter, gate threshold, size or seed changed**, and the config is unchanged.
- *Not done, deliberately:* no graph was generated and no BFS was run on any null or random graph, so the "no random-graph output at freeze" property holds. The guard arguments are analytic or heuristic, not measured.
- *Local:* `pytest -q` 244 passed on `c7abbee` (Python 3.13.16).

**Not merged by this session**, because the reviewer authored the r1 delta. **Evidence level:** design review and exact arithmetic; no numerical observation on any graph; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **Priority after 2026-10-11T21:11Z:** dispatch the Pilot B blind run once from `main`, as recorded in the Pilot B entries below.
2. Before or after that, a different session checks the r1 delta on PR #32 (prereg text only) and confirms green CI on the new head. Then it merges with an expected-head guard. D1 implementation is a separate PR after the merge.

Director run rd-claude-20261011T015540Z-a2bbeb: start 2026-10-11T01:55:20Z, end 2026-10-11T01:59:51Z, duration 4 min

## Director session: Issue #4 dimension-estimator preregistration D1, proposed (2026-10-11, `rd-claude-20261011T005644Z-6efe9a`)

**Recovery audit:** the previous lease (`rd-claude-20261010T235526Z-158381`) was released cleanly at lock commit `bede57c`. There were no open PRs and no queued or running workflows. `main` `798dd72` was CI-green ([38097017390](https://github.com/shaden7/emergence-lab/actions/runs/38097017390)). Release `pilot-b-blind-v1` did not exist (HTTP 404), so the Pilot B blind run has not been dispatched. Nothing was incomplete.

**Why this step:** the only Pilot B action left is the once-only dispatch, which must wait until after 2026-10-11T21:11Z. Issue #4 is independent of Pilot B, and its deliverable 1 (a preregistered design) was the oldest unblocked item. The WIP count was 0.

**Proposed, open (not on `main`):** a PR on branch `research/dimension-d1-prereg-20261011` adds [D1 preregistration v1.0](DIMENSION_ESTIMATOR_PREREGISTRATION.md) and `configs/dimension_d1.json`. Design only; it touches no Pilot B file.
- *Estimator:* dyadic volume-growth d_eff(r) = log₂(B̄(2r)/B̄(r)) with r_min = 4 and a saturation guard 8·B̄(2r) ≤ N. The verdict is PLATEAU only with ≥ 3 consecutive scales within ε = 0.15; otherwise NO_PLATEAU or INSUFFICIENT_RANGE.
- *Controls:* exact Z¹/Z²/Z³ lattices, with the analytic table included in the prereg, and a 2D random geometric graph at k̄ = 12.
- *Nulls and adversaries:* random 4-regular graphs, a subdivided binary tree and Newman–Watts shortcuts on Z².
- *Gates:* D-G0…D-G5. Seed base `2035101101`. Budget: 1 core, 1.5 GiB, 30 min, no Lightsail.

**Actually executed:** only the closed-form lattice ball counts and expected verdicts (exact arithmetic, Python 3.13). No graph was generated and no random-graph output exists.

**Review:** producer self-review only. **Not merged by this session.**

**Evidence level:** design only; the lattice table follows from a counting formula. No numerical observation and no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:**
1. **Priority after 2026-10-11T21:11Z:** dispatch the Pilot B blind run once from `main`, as recorded in the entry below.
2. Before then or afterwards: a later-pass review of the D1 PR in a different session. It should check the gates against Issue #4, the references in §9 and the analytic table (recompute it). If it passes, merge with an expected-head guard. Implementation is a separate PR.

PR: [#32](https://github.com/shaden7/emergence-lab/pull/32).

Director run rd-claude-20261011T005644Z-6efe9a: start 2026-10-11T00:56:09Z, end 2026-10-11T01:02:58Z, duration 6 min

## Director session: later-pass check of the Pilot B stage-2 revision, PASS and merge (2026-10-10, `rd-claude-20261010T235526Z-158381`)

**Recovery audit:** the previous lease (`rd-claude-20261010T225628Z-1ebe46`) was released cleanly at lock commit `52d8c7e`. Its work was the REVISE delta on [PR #31](https://github.com/shaden7/emergence-lab/pull/31) at head `1569b19`, CI green on that head: push [38093531708](https://github.com/shaden7/emergence-lab/actions/runs/38093531708) and PR [38093535371](https://github.com/shaden7/emergence-lab/actions/runs/38093535371). There were no queued or running workflows, and release `pilot-b-blind-v1` did not exist (live `GET releases/tags` → HTTP 404). Nothing was incomplete.

**Review (this session authored none of `a57d5ef`, `fd6f284`, `1569b19`; same model family, so not external review):** decision **PASS** on `1569b19`.
- *Delta `fd6f284..1569b19`:* workflow, test, note and state only. The once-only guard proceeds only when `gh api` fails and its output contains `HTTP 404`; the live response for the absent tag is `gh: Not Found (HTTP 404)`, so it proceeds now and fails closed on any other error. The B-G6 dev rerun and `cmp` precede `fetch-round`.
- *Re-checked independently:* R = 32983212 from the merge committer time `2026-10-10T21:09:59Z` (quicknet genesis 1692803367 + 32983211 × 3 s = 1791753000 = 2026-10-11T21:10:00Z). All five frozen blob SHAs at `1569b19` equal `7780fc1`.
- *Local, Python 3.13.16 / NumPy 2.5.3:* `pytest -q` 244 passed. Two dev invocations into *different* output directories: `rows.csv` and `result.json` byte-identical (so the `cmp` does not depend on the output path); decision digest `6da5c8e3…` as pinned. `preflight` → FAIL CLOSED "too early" (exit 2).
- *Non-blocking:* the step named "Development set must reproduce the stage-1 decision digest" runs the dev set but the digest itself is checked in `execute`, after `fetch-round`. Fetching the public round first cannot select a key (the key is deterministic in R), so ordering is cosmetic; not changed, to avoid another review cycle before R.

**Integration:** merged with `sha` = the head carrying this handoff once its CI is green; the merge commit is recorded on the PR. **Not dispatched.**

**Evidence level:** workflow infrastructure review; no Pilot B blind output; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:** after 2026-10-11T21:11Z, a Director holding the lease dispatches `Pilot B stage-2 blind run (once only)` once from `main`, then records the run URL, release `pilot-b-blind-v1`, all gates (including B-G6) as published, the result note and the decision record. A gate failure is reported, not rerun.

Director run rd-claude-20261010T235526Z-158381: start 2026-10-10T23:55:26Z, end 2026-10-10T23:59:11Z, duration 3 min

## Director session: later-pass review of Pilot B stage 2, REVISE (2026-10-10, `rd-claude-20261010T225628Z-1ebe46`)

**Recovery audit:** the previous lease (`rd-claude-20261010T215634Z-08323a`) was released cleanly at lock commit `17386ac`. Its work was [PR #31](https://github.com/shaden7/emergence-lab/pull/31) at head `fd6f284`, CI green on that head: push [38090055693](https://github.com/shaden7/emergence-lab/actions/runs/38090055693) and PR [38090059291](https://github.com/shaden7/emergence-lab/actions/runs/38090059291). There were no queued or running workflows, Issue #4 was unchanged, and release `pilot-b-blind-v1` did not exist. Nothing was incomplete.

**Review (this session did not author the producer's code; same model family, so not external review):** decision **REVISE**, applied on PR #31. Details are in the [stage-2 note](experiments/2026-10-10-pilot-b-stage2-workflow.md), section *Later-pass review*.
- *Sound:*
  - frozen blob SHAs equal `7780fc1`;
  - no beacon fetch before `preflight`;
  - gate failures publish;
  - the `fetch-round` record matches what the guards and the release notes read;
  - `contents: write` is minimal;
  - a retry on the same R cannot change the key.
  - The workflow's inline Python blocks were run on outputs from the tests' throwaway key; this is not Pilot B evidence.
- *Fixed:*
  - The once-only guard failed open on any `gh` error. It now proceeds only on a definite HTTP 404, checked live: absent tag → proceed; existing tag, 403 and missing `gh` → fail.
  - B-G6 dev byte-identity is now checked inside the blind run: the dev set runs twice and is `cmp`ed before R is fetched.
  - The static test covers both.
- *Local, Python 3.13.16 / NumPy 2.5.3:* `pytest -q` 244 passed; `preflight` → FAIL CLOSED "too early".

**Not merged by this session**, because the reviewer authored the delta. **Evidence level:** workflow infrastructure review; no Pilot B blind output; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:** a different session checks the delta (workflow and test only), confirms green CI on the new head, and merges with an expected-head guard **before 2026-10-11T21:10Z**. After 2026-10-11T21:11Z, dispatch once from `main`, then record the run, release, gates (including B-G6), the result note and the decision record.

Director run rd-claude-20261010T225628Z-1ebe46: start 2026-10-10T22:55:54Z, end 2026-10-10T23:00:55Z, duration 5 min

## Director session: Pilot B stage 2 workflow, proposed (2026-10-10, `rd-claude-20261010T215634Z-08323a`)

**Recovery audit:** the previous lease (`rd-claude-20261010T205622Z-908995`) was released cleanly at lock commit `93672f0`. There were no open PRs and no queued or running workflows; `main` `7780fc1` was CI-green ([38086569248](https://github.com/shaden7/emergence-lab/actions/runs/38086569248)). Issue #4 was unchanged. Nothing was incomplete. R = 32983212 was re-derived from the merge time and matches the record on PR #30.

**Implemented, open (not on `main`):** [PR #31](https://github.com/shaden7/emergence-lab/pull/31), branch `research/pilot-b-stage2-blind-workflow-20261010`, code head `a57d5ef`. [Stage-2 note](experiments/2026-10-10-pilot-b-stage2-workflow.md).
- *`pilot_b_blind.py` (guards only):* it pins R, the stage-1 merge, the frozen blob SHAs of the stage-1 code, config and prereg, and the dev decision digest. Before any beacon fetch it fails closed if wall clock < R + 60 s. It re-verifies the beacon (round, chain, SHA-256, BLS) locally. Gate failures are archived, not rerun.
- *`pilot-b-blind-run.yml`:* `workflow_dispatch` only, `main` only. Order: once-only release-tag guard → preflight → dev digest → fetch R → blind run → artifact → release → re-download hash check.

**Actually executed:**
- *Local, Python 3.13.16 / NumPy 2.5.3:* `pytest -q` 244 passed (9 new). `preflight` returned FAIL CLOSED "too early" (exit 2), as intended.
- *CI on `a57d5ef`:* push [38089825387](https://github.com/shaden7/emergence-lab/actions/runs/38089825387) and PR [38089846338](https://github.com/shaden7/emergence-lab/actions/runs/38089846338) both succeeded. Python 3.12.15 / NumPy 2.5.4; dev decision digest `6da5c8e3…` unchanged.
- *Not executed:* the blind workflow and any beacon fetch.

**Review:** producer self-review only. **Not merged by this session.**

**Evidence level:** workflow infrastructure; no Pilot B blind output; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:** a later-pass review of PR #31 in a different session, covering the guards, the frozen blob SHAs against `7780fc1`, and the workflow order and permissions. Then merge with an expected-head guard **before** 2026-10-11T21:10Z. After 2026-10-11T21:11Z, dispatch the workflow once from `main`, then record the run, the release, the gates, the result note and the decision record.

Director run rd-claude-20261010T215634Z-08323a: start 2026-10-10T21:56:12Z, end 2026-10-10T22:04:30Z, duration 8 min

## Director session: later-pass review and merge of Pilot B stage 1 (2026-10-10, `rd-claude-20261010T205622Z-908995`)

**Recovery audit:** the previous lease (`rd-claude-20261010T195637Z-0eea4a`) was released cleanly at lock commit `c38026f`. Its work was open [PR #30](https://github.com/shaden7/emergence-lab/pull/30) at head `7686584`, with all three workflows green on that head: push [38082783464](https://github.com/shaden7/emergence-lab/actions/runs/38082783464), PR [38082785677](https://github.com/shaden7/emergence-lab/actions/runs/38082785677) and beacon [38082785660](https://github.com/shaden7/emergence-lab/actions/runs/38082785660). There were no queued or running workflows and Issue #4 was unchanged. Nothing was incomplete. The PR's stage-1 note still described the beacon as unverified; this review corrected it.

**Review (this session did not author the code; same model family, so not external review):** decision **PASS**. Details are in the [stage-1 note](experiments/2026-10-10-pilot-b-stage1-dev.md), section *Later-pass review*.
- *Read against the prereg text:* generator, analyst and evaluator against §3/§5/§7/§8; beacon arithmetic against the drand round formula. The pins match 4/4 relays and three live rounds BLS-verify in CI.
- *Local checks:* `pytest -q` 235 passed. Dev run ×2 byte-identical. Decision digest `6da5c8e3…` equals the Python 3.12 CI value. An independent recomputation of all verdicts and r̂ found 0 mismatches.
- *Calibration Monte Carlo (400 non-blind review keys, a review check, not a Pilot B result):* exterior false-rejection rate 0.0518 (exact 0.0488, SE 0.0022); spurious C2 0.086 / C1 0.079 (prereg 0.079 / 0.075); speed overestimate 0.028; power 2,347/2,347. Gate failures: B-G1 13/400, B-G2 2/400, B-G3 10/400, all others 0. **A correct implementation therefore fails some gate in the blind run with probability ≈ 6 %.** Under §8 such a failure is published, not rerun.
- *Non-blocking:* B-G4 with fewer than 3 detectable instances is stricter than the prereg's "vacuous pass". It never occurred (min 5 detectable per key).

**Evidence level:** implementation review plus a stochastic calibration check of a stipulated detector model; no blind evaluation; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:** compute R from the merge commit (`python -m emergence_lab.pilot_b_beacon round-for-merge <merge-time>`; the value is recorded on PR #30). Stage 2 is a separate PR: a `workflow_dispatch` blind-run workflow on `main` that fails closed before R's timestamp, fetches and verifies round R, runs `--phase blind` once and archives the outputs durably as for N5. Dispatch it only after R is published.

Director run rd-claude-20261010T205622Z-908995: start 2026-10-10T20:55:52Z, end 2026-10-10T21:07:15Z, duration 11 min

## Director session: Pilot B stage 1 implementation (2026-10-10, `rd-claude-20261010T195637Z-0eea4a`)

**Recovery audit:** the previous lease (`rd-claude-20261010T185551Z-a8d493`) was released cleanly at lock commit `b5ee413`. There were no open PRs, and no queued or running workflows. `main` `c877d91` was CI-green ([38078085959](https://github.com/shaden7/emergence-lab/actions/runs/38078085959)). Nothing was incomplete.

**Implemented, open (not on `main`):** [PR #30](https://github.com/shaden7/emergence-lab/pull/30), branch `research/pilot-b-stage1-20261010`, code head `0fd1259`. [Stage-1 note](experiments/2026-10-10-pilot-b-stage1-dev.md).
- *Modules:* `pilot_b.py` (generator, oracle, two exact reference paths, evaluator, manifest), `pilot_b_analyst.py` (§5 rule; imports only `math` and NumPy) and `pilot_b_beacon.py` (quicknet pins, round arithmetic, SHA-256 and BLS verification).
- *Tests and CI:* 23 tests; CI runs the dev set twice; new `Pilot B drand quicknet check` workflow.
- *Unchanged:* prereg blob `dd5dbefe…` and config `3fc24afa…`. The note records the implementation choices the prereg left open (draw order, `key_int`, cell index, circulant convention).

**Actually executed:**
- *Local, Python 3.13.16 / NumPy 2.5.3:* `pytest -q` 235 passed. Dev run ×2 byte-identical (`rows.csv` `fa657d02…`); 0.6 s CPU, 68 MiB.
- *CI on `0fd1259`:* push [38082607401](https://github.com/shaden7/emergence-lab/actions/runs/38082607401) and PR [38082611224](https://github.com/shaden7/emergence-lab/actions/runs/38082611224), both success on Python 3.12.15. Decision digest `6da5c8e3…` equals the local one.
- *Beacon check [38082611228](https://github.com/shaden7/emergence-lab/actions/runs/38082611228):* 4/4 relays match the pinned chain hash `52db9ba7…`, public key, period and genesis. Live round 32953201 passes both the SHA-256(signature) and the BLS check. This resolves the stage-1 chain-hash blocker.

**Dev numerical observations (public key; correctness check, not the blind test):**
- B-G0: max path difference 1.1e-14; all P exterior sites exactly 0.
- B-G1: 0/24 false rejections.
- B-G2: 1/16 speed overestimates (an interior noise false positive at S = 0, z = 3.46).
- B-G3: C1 r = 0 always detected; 0/8 spurious.
- B-G4: 6/6 detectable N instances rejected.
- Undetected violations: all 5 N1 (max exterior |S| below the 5.73e-5 limit) and 5 of 6 N3 (shortcut site not on the grid). These are *undetected*, not evidence of bounded support.
- Separate `np.roll` time-stepping reproduces every `S_true` to 6e-14.

**Finding:** `rows.csv` bytes differ across CI runners because of last-bit BLAS rounding (|ΔS| ≤ 1.7e-15; reproduced with four OpenBLAS kernels; decisions identical). Fixed in reporting with a `decisions_sha256` digest and a forced-kernel test; no rule changed.

**Review:** producer self-review only ([record](https://github.com/shaden7/emergence-lab/pull/30#issuecomment-6101709782)). **Not merged by this session.** PR activity was not subscribed, because the repo's single-writer lease assigns follow-up to the next Director.

**Evidence level:** an implementation check on a public development key. No blind evaluation; no physics claim. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:** a later-pass review of PR #30 in a different session, covering the analyst code, the implementation choices against the prereg, and green CI on the final head. Then merge with an expected-head guard. The merge timestamp fixes R (`python -m emergence_lab.pilot_b_beacon round-for-merge <merge-time>`). Stage 2 (a once-only blind run workflow on `main`) is a separate PR after R is published.

Director run rd-claude-20261010T195637Z-0eea4a: start 2026-10-10T19:56:10Z, end 2026-10-10T20:11:43Z, duration 16 min

## Director session: later-pass check of Pilot B r1 and merge decision (2026-10-10, `rd-claude-20261010T185551Z-a8d493`)

**Recovery audit:** the previous lease (`rd-claude-20261010T175613Z-1698f5`) was released cleanly at lock commit `b74f14c`. One open PR ([#29](https://github.com/shaden7/emergence-lab/pull/29), head `c3ecb84`, CI green on push [38074046021](https://github.com/shaden7/emergence-lab/actions/runs/38074046021) and PR [38074049590](https://github.com/shaden7/emergence-lab/actions/runs/38074049590)), no queued or running workflows, Issue #4 unchanged. Nothing incomplete.

**Review (this session authored neither v1.0 nor r1; same model family, so not external review):** [record](https://github.com/shaden7/emergence-lab/pull/29#issuecomment-6101056236). B-G3 was re-derived from the §4–§5 grid in a separate script:
- 21 interior C2 cells and 18 interior C1 cells (r > 0) under z₂, plus 12 exterior cells under z₁.
- Per-instance spurious probability: C2 0.0787, C1 0.0745.
- P(≥ 3 of 8 spurious): 0.0202 (binomial bound), 0.0188 (exact 4+4), 0.0182 (Monte Carlo, 2×10⁵ replicates, seed 20261010).
- The v1.0 rule's failure probability is 0.2013, which confirms the r1 blocking finding.

Pins re-verified: prereg blob `dd5dbefe…`, config SHA-256 `3fc24afa…`. Key encodings are byte-exact. Local `pytest -q`: 212 passed (Python 3.13.16, NumPy 2.5.3). **Decision: PASS.** The merge uses an expected-head guard once CI on this handoff commit is green; the merge commit is recorded on the PR.

**Remaining stage-1 blockers (not merge blockers):** the drand quicknet chain hash is unverified, and without it the pilot is BLOCKED with no substitute seed. Blinding is instance-level only.

**Evidence level:** design review and arithmetic only; no Pilot B code or numerical output exists. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:** Pilot B stage 1 as a separate PR: `instances(key)` generator, noisy oracle, analyst module with an import-isolation test, evaluator, B-G0 two-path references, dev-key gates B-G1…B-G6. Verify the drand quicknet chain hash and round arithmetic in GitHub Actions before merge. The blind run happens only ≥ 24 h after the stage-1 merge.

Director run rd-claude-20261010T185551Z-a8d493: start 2026-10-10T18:55:29Z, end 2026-10-10T18:58:32Z, duration 3 min

## Director session: later-pass review of Pilot B preregistration, REVISE → r1 (2026-10-10, `rd-claude-20261010T175613Z-1698f5`)

**Recovery audit:** the previous lease (`rd-claude-20261010T165622Z-55e236`) was released cleanly at lock commit `a3bed8b`. One open PR ([#29](https://github.com/shaden7/emergence-lab/pull/29), head `11df5d0`, CI green on push [38070097242](https://github.com/shaden7/emergence-lab/actions/runs/38070097242) and PR [38070117822](https://github.com/shaden7/emergence-lab/actions/runs/38070117822)), explicitly awaiting a later-pass review. Nothing incomplete.

**Review (non-producer session, same model family; independent re-derivation, not independent external review):**
- *Verified:* z₁ = 2.8653, z₂ = 3.1718, SE = 2.0e-5, detection limit 5.73e-5, m = 12 exterior cells, binomial tails 0.0298 / 0.0070, boundary power 0.998. A separate script built S1/S3 (100 signed + 100 positive random stencils, k ≤ 4) and S2 (c² ∈ {0.25, 0.6, 1}) propagators: every exterior grid cell is exactly 0.0. N3: 300 random draws were non-negative, column-stochastic and symmetric; min diagonal bound 0.0244 > 0.01 holds.
- *Blocking finding:* B-G3 (all 8 C instances clean except B-G1 exterior rejections) fails with probability **0.201** analytically (0.202 in a 2×10⁵-replicate Monte Carlo) for a *perfectly calibrated* method, because interior false detections at the nominal z₂ rate were not excepted. 
- *Non-blocking:* blind/dev key byte encodings were unspecified; S2 has no L×L matrix power; B-G4 power is expected to rest mainly on N2 (all α detectable; N1 only for γ ≳ 0.89, N3 ≈ 4 % of draws — analytic probe, not a Pilot B run).

**Implemented on PR #29 (pre-merge revision r1, not on `main`):** B-G3 restated as `#spurious C instances ≤ 2 of 8` plus a C1 r=0 sanity check (P(fail | calibrated) ≤ 0.020); key encodings pinned; S2 companion-matrix path; §10 power-composition note. Config `1.0-r1`. Prereg blob `dd5dbefe…`, config SHA-256 `3fc24afa…`. Local `pytest -q`: 212 passed (Python 3.13, NumPy 2.5.3). **Not merged by this session**: the reviewer authored the gate change, so a different session should check the r1 delta (B-G3 arithmetic, encodings) and merge with an expected-head guard. drand quicknet chain hash remains unverified (stage-1 requirement; sandbox cannot reach drand).

**Evidence level:** design review and arithmetic; no Pilot B code or numerical output exists. **Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:** later-pass check of the r1 delta on PR #29, then merge; afterwards Stage 1 (generator, oracle, isolated analyst, evaluator, dev-set gates) as a separate PR.

Director run rd-claude-20261010T175613Z-1698f5: start 2026-10-10T17:55:51Z, end 2026-10-10T18:00:29Z, duration 5 min

## Director session: Pilot B preregistration (proposed) and N5 later-pass reproduction (2026-10-10, `rd-claude-20261010T165622Z-55e236`)

**Recovery audit:** the previous lease (`rd-gpt6-20261010T153936Z-6b85701b`) was released cleanly at lock commit `412c652`. There were no open PRs, no queued or running workflows, and `main` `8d6adac` was CI-green ([38066460739](https://github.com/shaden7/emergence-lab/actions/runs/38066460739)). Nothing was incomplete.

**Later-pass check of N5 (non-producer session; not an independent implementation):** on `main` `8d6adac`, local cloud sandbox, Python 3.13.16 / NumPy 2.5.3:
- `pytest -q`: 212 passed.
- `python -m emergence_lab.pilot_a_noise` run twice: `rows.csv` SHA-256 `af7ec754…` both times, **identical to the archived CI digest** produced on Python 3.12.15. This is a cross-environment byte match for this dataset; it is not a general guarantee.
- All N5-G1…G6 report PASS. A separate script recomputed `S_hat` and `detected` for all 5,040 rows (0 inconsistencies) and recounted the W/CA r=6 sentinels: W 9/20 and CA 8/20 at σ=η=1e-6 (analytic 0.4795), 0/20 at σ=1e-6, η=1e-3, and 20/20 at σ=1e-4, η=1e-9, matching the [N5 note](experiments/2026-10-10-pilot-a-n5.md).
- *Evidence level:* reproduction of a stipulated-detector numerical observation; the same code was rerun, so this checks determinism and reporting, not the implementation's correctness.

**Proposed, not on `main`:** [Pilot B preregistration v1.0](PILOT_B_BLINDED_INTERVENTION_PREREGISTRATION.md) and [config](../configs/pilot_b.json), design commit `427c4a4` (prereg blob `96146a68…`, config SHA-256 `4afa2ebc…`). It is a blinded black-box test of a declared bounded-speed null H0(v_max=4) on 40 stipulated ring dynamics (16 strict, 8 null, 16 non-strict). It uses a fixed budget (33 cells × 2 arms × 50 readouts, σ=1e-4), a Bonferroni exterior test (z=2.8653) and drand commit-reveal blinding. Gates B-G0…B-G6 are fixed. **No Pilot B code or numerical output exists.**
- *Design rationale (mathematical point, not a result):* finite data cannot establish strict support; it can only reject a declared bounded-speed null.
- *Arithmetic checked in this session:* z values, the 12 exterior cells, the detection limit 5.73e-5, and binomial tails P(X≥4 | 24, 0.05) = 0.030 and P(X≥4 | 16, 0.05) = 0.007.
- *Feasibility probe (analytic, not a Pilot B run):* N1 heat at t=1, r=6 has |S| = 6e-8 / 4.8e-6 / 2.2e-4 for γ = 0.2 / 0.45 / 1. Most N1 instances will therefore be undetectable, which is the intended lesson.

**Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:** a different Director session reviews the Pilot B PR: arithmetic, the zero-exterior claim for every strict/null class, the N3 non-negativity bound and the blinding procedure. It then merges or requests v1.1. Stage 1 (generator, oracle, isolated analyst, evaluator, dev-set gates) is a separate PR only after that merge.

Director run rd-claude-20261010T165622Z-55e236: start 2026-10-10T16:55:46Z, end 2026-10-10T17:02:15Z, duration 6 min

## Director session: Pilot A N5 noise stress (2026-10-10, `rd-gpt6-20261010T153936Z-6b85701b`)

**Question:** can finite independent readout noise create spurious threshold detections outside a mathematically strict model cone, and can these be accounted for by an independent analytic Gaussian-null formula?

**Prereviewed design:** [N5 preregistration](PILOT_A_N5_NOISE_PREREGISTRATION.md) and config were committed first as `8686ae276e6cb4892c8410874136ae2baf31c93e`, before results; implementation `afed534d`, CI runner `f336572`. The deterministic Pilot A holdout was not rerun. Tested only frozen development fixtures W/H/CA/Q (7 sites; 3 sigma × 3 thresholds × 20 independent replicates/model).

**Actually executed on GitHub CI:** [push 38065322982](https://github.com/shaden7/emergence-lab/actions/runs/38065322982) and [PR 38065354024](https://github.com/shaden7/emergence-lab/actions/runs/38065354024) completed successfully on exact code head `f336572`: 210 pytest passed and 1 skipped; N5-G1…G6 all PASS, 720 independent seed tuples and 5,040 site records. [Full note](experiments/2026-10-10-pilot-a-n5.md).

**Quantitative adversarial result:** at mathematically zero r=6, sigma=eta=1e-6, W false detections **9/20** (Wilson 95% [0.258, 0.658]) and CA **8/20** ([0.219, 0.613]); analytic Gaussian `p=erfc(0.5)=0.4795`. Strict W's measured farthest front incorrectly reached r=12 in 6/20 trials; strict CA's in 4/20. These are detector false positives and do not alter the strict support theorem. Same-random-stream finite observation sites are not statistically independent replicates.

**Archive independently verified:** the initial short-lived GitHub Actions [artifact 11674566926](https://github.com/shaden7/emergence-lab/actions/runs/38065322982/artifacts/11674566926) was downloaded/unpacked and CSV hash-checked (`af7ec754…`). After a first main-only [archive run 38065990548](https://github.com/shaden7/emergence-lab/actions/runs/38065990548) *failed closed* on a copied prereg blob SHA typo (data and G1–G6 matched), [fix PR #27](https://github.com/shaden7/emergence-lab/pull/27) and regression tests corrected that guard. On merged main `a4f021ea…`, the [successful archive run 38066230799](https://github.com/shaden7/emergence-lab/actions/runs/38066230799) regenerated all N5 raw records byte-identically, pinned the SHA-256, uploaded a versioned [GitHub Release](https://github.com/shaden7/emergence-lab/releases/tag/pilot-a-n5-evidence-2026-10-10-v1), **downloaded it again and checked manifest, CSV and JSON hashes**. Published: `n5_rows.csv` (645,027 B, `af7ec754…`), `n5_result.json` (`091a942d…`), `n5_archive_manifest.json` (`5f9f1e20…`). **Phase-0 C5 durable raw evidence achieved for this N5 dataset**. The original Actions artifact separately expires 2027-01-08. No Lightsail/production deployment or new paid usage.

**Evidence level:** computational methodology/stochastic observation in an assumed Gaussian detector model, not real-world experimental support or new physics. **Next single action:** preregister a genuinely blinded unknown-class interventional benchmark (finite measurement budget, negative controls, prespecified false-positive policy) **before** trying to infer causality from an unexplored model. Geometry issue #4 remains separate and requires its own preregistration.

## Director session: Pilot A scoped calibration decision (2026-10-10, `rd-gpt6-20261010T153936Z-6b85701b`)

**Question:** does the archived Pilot A development/holdout evidence justify moving from reference calibration to general causal inference?

**Artifact audit, not a rerun:** on `main` `b14c43d`, read the archived one-shot [holdout JSON](experiments/2026-10-10-pilot-a-holdout-result.json), recounted 108 cells by model/status (58 match, 33 theorem-consistent zero, 17 censored, 0 mismatch), checked A3 registered witnesses and all 27 threshold-front entries across nine (model, L, t) groups. The latest `main` [CI 38062057844](https://github.com/shaden7/emergence-lab/actions/runs/38062057844) passed. **No holdout was re-executed, no experiment was run, and no local pytest was executed in this session.**

**Decision:** [Pilot A scoped decision](PILOT_A_DECISION.md) — **GO only for deterministic reference calibration; NO-GO for inferred strict causal cones, universal speeds, or claims about emergent spacetime**. A1–A4 and deterministic A7 passed on the original one-shot holdout. A5 passed on development. A6 is threshold/site-grid dependent; N5 measurement noise is unimplemented. Only one W holdout cell is nonzero. Prior Phase-0 C1–C5 remain binding for applicable new models. No new authorisation to deploy or to run an exploratory model is implied.

**Evidence level:** data re-tabulation and methodological assessment of *known-model* numerical observations; no mathematical proof or new physics. **Deployment:** none. **Next single step:** separately preregister/implement N5 on development/reference fixtures with 20 independent noise realisations per sigma/threshold; do not retune or rerun the one-shot holdout. Geometry Issue #4 still requires its own preregistration.

## Director session: Pilot A holdout evaluation (2026-10-10, `rd-claude-20261010T145640Z-d84b0e`)

**Question:** do A1–A4 hold on the preregistered holdout grid, evaluated once without retuning (A7)?

**Recovery audit:** the previous lease (`rd-claude-20261010T141114Z-3b0788`, which recorded the PR #23 merge) was released cleanly. There were no open PRs, and no queued or running workflows. `main` `a005277` was CI-green ([38058950624](https://github.com/shaden7/emergence-lab/actions/runs/38058950624)). The holdout had not been run. Nothing was incomplete.

**Actually executed (local cloud sandbox, Python 3.13.16 / NumPy 2.5.3, not on Lightsail):**
- `pytest -q`: 207 passed.
- Development grid reproduced: `rows.csv` `7a2ff47c…`.
- Protocol and config pins re-verified.
- **Holdout, once**, on `c4f2793` (`--phase holdout --allow-holdout`, `GIT_SHA` set): 108 cells. 58 match, 33 analytic_zero_ok, 17 censored, **0 mismatch**. A1, A2, A3 and A4 pass, so **A7 passes**. Max relative error 2.1e-13. 4.3 s CPU.
- `rows.csv` `a99bdb4d…`, `result.json` `5530e17e…`. Both are committed in [the holdout note](experiments/2026-10-10-pilot-a-holdout.md).
- An earlier launch attempt failed at the shell (`/usr/bin/time` was missing, exit 127) before Python started. No cell was computed in that attempt. The note records it.

**Evidence level:** numerical observation about a measurement procedure on textbook models whose support classes are mathematical inputs. **No physics claim.** H1 survived its preregistered holdout; this is not proof.

**Limitations:**
- A1 reuses the grid-independent development control.
- Only one non-zero W cell lies on the holdout grid.
- N5 (noise) is not implemented, so the optional part of A7 is open.
- A5 was evaluated on development only.
- All review is AI-mediated by the same model family.

**Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:** a scoped Pilot A decision record (reference calibration within the stated limits). Alternatively, implement N5 first. Either one comes before any exploratory model family uses this metric.

Director run rd-claude-20261010T145640Z-d84b0e: start 2026-10-10T14:56:07Z, end 2026-10-10T15:00:16Z, duration 4 min

## Director session: Pilot A later-pass review before the holdout (2026-10-10, `rd-claude-20261010T135604Z-f9e889`)

**Question:** is the merged stage-1 code (`c8831af`) fit to evaluate the preregistered holdout once and unchanged?

**Recovery audit:** the previous lease (`rd-claude-20261010T133045Z-45f458`, which recorded the PR #22 merge) was released cleanly. There were no open PRs, and no queued or running workflows. `main` `449162e` was CI-green ([38056099886](https://github.com/shaden7/emergence-lab/actions/runs/38056099886)). Nothing was incomplete.

**Review finding (engineering, blocking for the holdout):** the registered A3 witnesses (t, r) = (1, 4), (1, 6) are not on the holdout grid. The stage-1 rule `all(...)` over the phase's witness rows was therefore **vacuously true on the holdout**. This was established from grid membership only. **No holdout cell was computed.**

**Implemented, open (not on `main`):** [PR #23](https://github.com/shaden7/emergence-lab/pull/23), head `1f22958`.
- *A3 clarification, fixed before any holdout evaluation:*
  - The registered witnesses are evaluated directly in every phase.
  - On the holdout, every non-censored H/Q cell with |r| > a + c t must also `match`.
  - Empty witness sets fail A3; A2 and A4 also fail on an empty set.
- *Independent W path:* Courant-1 leapfrog (h = 0.25), exact at grid points.
- *Unchanged:* tolerances, grids, seeds, config `a55fcfa8…` and protocol pin `c8061aed…`.

**Actually executed (local, Python 3.13.16 / NumPy 2.5.3):**
- `pytest -q`: 207 passed.
- Development grid: A1–A5 pass, and the summary is unchanged. `rows.csv` `7a2ff47c…` is byte-identical twice and identical to stage 1.
- PR CI on `1f22958`: push [38057875118](https://github.com/shaden7/emergence-lab/actions/runs/38057875118) and pull_request [38057878334](https://github.com/shaden7/emergence-lab/actions/runs/38057878334), both success.
- [Note](experiments/2026-10-10-pilot-a-references-dev.md#later-pass-review-before-the-holdout-2026-10-10-rd-claude-20261010t135604z-f9e889).

**Review:** [PASS for engineering merge](https://github.com/shaden7/emergence-lab/pull/23#issuecomment-6098282755). This is a producer self-review.

**Merge blocker:** `PUT …/pulls/23/merge` with the expected head was denied by the session permission classifier as self-approval. It was not retried by other means ([comment](https://github.com/shaden7/emergence-lab/pull/23#issuecomment-6098288590)). This handoff commit changes the PR head, so CI must be re-verified on the new head.

**Merged on explicit owner request:** under a fresh lease (`rd-claude-20261010T141114Z-3b0788`), with expected head `9c21807`, whose CI was green on both runs. The merge commit is `c4f2793c3cb8fd4d93cd4d9ed69c9d5ae800bb11`, and `main` CI [38058684785](https://github.com/shaden7/emergence-lab/actions/runs/38058684785) passed. The review is still a producer self-review. The merge does not accept Pilot A as validated.

**Evidence level:** engineering fix plus a numerical consistency observation. No physics claim. The holdout is unrun.

**Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:** a non-producer Director session:
- re-verifies the PR #23 head CI;
- merges with an expected-head guard;
- runs `python -m emergence_lab.pilot_a --phase holdout --allow-holdout` once on the merge commit (with `GIT_SHA` set);
- reports A1–A4/A7 with the manifest and the `rows.csv` digest, including any failure.

Director run rd-claude-20261010T135604Z-f9e889: start 2026-10-10T13:55:26Z, end 2026-10-10T14:03:31Z, duration 8 min

## Director session: Pilot A stage 1, reference solvers and null controls (2026-10-10, `rd-claude-20261010T125630Z-693e0a`)

**Question:** do Pilot A's reference solutions, independent numerical paths and null controls behave as preregistered on the development grid, before any holdout or exploratory run?

**Recovery audit:** the previous lease (`rd-claude-20261010T115647Z-4e5855`) was released cleanly. There were no open PRs, and no queued or running workflows. `main` `5da5d00` was CI-green ([38050894924](https://github.com/shaden7/emergence-lab/actions/runs/38050894924)). Nothing was incomplete.

**Implemented and integrated:** [PR #22](https://github.com/shaden7/emergence-lab/pull/22), head `fcbe14d`:
- `src/emergence_lab/pilot_a.py`, `tests/test_pilot_a.py` and `configs/pilot_a.json`. The config pins the preregistration SHA-256 `c8061aed…`.
- Paths compared: W (d'Alembert); H (erfc vs Gauss–Legendre kernel quadrature); CA (simulation vs induction); Q (eigh vs explicit Fourier sum vs Taylor, plus the Bessel limit).
- The A3 classifier, with censoring below 1e-8.
- Controls N1–N4.
- The holdout is refused without `--allow-holdout`.

**Actually executed (local, Python 3.13.16 / NumPy 2.5.3):**
- `pytest -q`: 194 passed. PR CI on the exact head: push [38054211314](https://github.com/shaden7/emergence-lab/actions/runs/38054211314) and pull_request [38054230687](https://github.com/shaden7/emergence-lab/actions/runs/38054230687), both success.
- Development grid (numerical observation): 81 match, 55 analytic_zero_ok, 16 censored, 2 front_excluded, 0 mismatch. A1–A5 pass. `rows.csv` `7a2ff47c…` byte-identical twice.
- Far witnesses at t = 1 (r = 4 / 6): H 5.93e-3 / 4.82e-5, Q 1.16e-3 / 1.45e-6, W 0 by theorem.
- N4: forward Euler gives exactly 0 at r = 6, where the continuum value is 4.8e-5. This is a solver artifact.
- [Note](experiments/2026-10-10-pilot-a-references-dev.md).

**Review:** [PASS for engineering merge](https://github.com/shaden7/emergence-lab/pull/22#issuecomment-6097810844). This is a self-review by the producer.

**Merged on explicit owner request:** the Director's own merge attempt (`PUT …/pulls/22/merge` with the expected head SHA) was first denied by the session's permission classifier and was not retried by other means. The owner then asked for the merge in the same session. It was merged under a fresh lease with expected head `3ce7357`, giving merge commit `c8831af0bc235a8818b15d34931dea220314e06b`. `main` CI [38056010852](https://github.com/shaden7/emergence-lab/actions/runs/38056010852) passed. The review is still a producer self-review; the merge does not accept Pilot A as validated.

**Limitations:**
- W has no independent solver, so its A2 check is tautological.
- The N2 times and N4 grid are development choices. N5 is not implemented.
- The development grid is not a holdout. No physics claim.

**Deployment:** none. No Lightsail or EatSleepFeel interaction, no spending.

**Next single step:** a later session reviews the merged stage-1 code (later-pass review), optionally adds an independent W solver, then runs the holdout once and unchanged (`--phase holdout --allow-holdout`) and reports A1–A4 and A7.

Director run rd-claude-20261010T125630Z-693e0a: start 2026-10-10T12:55:50Z, end 2026-10-10T13:07:39Z, duration 11 min

## Director session: Phase-0 GO/NO-GO decision record (2026-10-10, `rd-claude-20261010T115647Z-4e5855`)

**Question:** do gates G1–G6 of `ISING_CALIBRATION_REPORT.md` §D hold against their criteria, and do the carry-over caveats block Phase 1?

**Recovery audit:** the previous lease (`rd-claude-20261010T105555Z-c25439`) was released cleanly. No open PRs; only Issue #4 is open. No queued or running workflows. `main` `6b4fc6e` CI-green ([38047588399](https://github.com/shaden7/emergence-lab/actions/runs/38047588399)). Release `phase0-evidence-2026-10-10-v1` present with 7 assets. Nothing incomplete.

**Actually executed (local, Python 3.13.16 / NumPy 2.5.3, nothing on Lightsail):**
- *G3 addendum*, preregistered before execution (`96e886b`). The production `convergence.py` ESS was tested on stationary AR(1) at φ = 0.98 and 0.995 (exact τ = 99 / 399). **PASS 10/10.** τ recovered to ≈ 2–3 % at n = 500 τ; every chain at n = 20 τ is flagged (ESS ≤ 50 < 100). At n = 20 τ, τ̂ is biased low by ≈ 15 %, and bulk-ESS at φ = 0.995 is 13 % above nominal. [Note](experiments/2026-10-10-g3-ar1-stress.md).
- *Gate-5 independent re-analysis* of the released `finite_size_gate.npz` (digest `b18423a2…` verified), without project code: β/ν = 0.1261 ± 0.0023, γ/ν = 1.7487 ± 0.0032. This agrees with the report (0.1256 ± 0.0021, 1.7499 ± 0.0030).
- *L32 gate re-run*: raw `57ae4ea0…` byte-identical, for the fourth time.

**Decision (methodological, not physics): GO for Phase 1, scoped and conditional on C1–C5** in [PHASE0_DECISION.md](PHASE0_DECISION.md):
- C1: ≥ 4 independent replicates; per-chain ESS intervals only when n ≥ 100 τ̂.
- C2: R̂/ESS/dispersed starts plus a power control.
- C3: no exponent claim without window stability and a correction-to-scaling assessment.
- C4: Phase-0 calibration does not transfer to Phase-1 models; each needs its own controls.
- C5: raw arrays archived before a gate is met.

The carry-over caveats (L32 short-chain under-coverage, 1/ν via tolerance, unarchived L32/burn-in series) are constraints, not blockers. GO authorizes only Pilot A as a separate reviewed code PR. It does not authorize deployment.

**Limitations:** all reviews are AI-mediated by the same model family. Coverage is energy-only at one temperature. AR(1) has a single exponential mode, so that check is necessary rather than sufficient.

**Deployment:** none. No EatSleepFeel interaction, no spending.

**Next single step:** implement Pilot A per `docs/PILOT_A_CAUSAL_PROPAGATION_PREREGISTRATION.md` under C1–C5 as one reviewed code PR. Start with its analytic reference solutions and null controls before any exploratory model run.

Director run rd-claude-20261010T115647Z-4e5855: start 2026-10-10T11:56:09Z, end 2026-10-10T12:06:35Z, duration 10 min

## Director session: gate-6 archive repair and verification (2026-10-10, `rd-claude-20261010T105555Z-c25439`)

**Question:** why did archive run 38045856455 fail, is the registered gate-4/5 raw evidence intact, and can gate 6 (durable raw-data archival) be verified?

**Recovery audit:** the previous lease (`rd-gpt6-20261010T103425Z-a274c6dd`) was released cleanly. There were no open PRs; the only open issue is #4 (post-Ising). `main` `94d9841` was CI-green. The archive run [38045856455](https://github.com/shaden7/emergence-lab/actions/runs/38045856455) on `8d83d8e` had **completed with failure**. Status by step:
- Step 5 (gate-4 NPZ `97a81cb7…` retrieved from run 38042967864): passed.
- Step 6 (gate-5 raw draws reproduced on the runner, `b18423a2…`): passed. This is the first runner reproduction of gate 5.
- Step 7 (both re-analyses): passed.
- Step 8 failed: `ValueError: coverage: config or reported config differs from preregistration`.
- Steps 9–10 (release publication and download check): skipped. No release was created.

**Root cause:** an engineering bug in the verifier. The config pins in `archive_evidence.EXPECTED` are SHA-256 of the **file bytes**. The verifier compared them with SHA-256 of **canonical JSON** (`json.dumps(sort_keys=True)`, gate 4 `97d3bb6f…`, gate 5 `689f2a9d…`), which is the convention the gate reports record. Unit tests missed it: they injected their own pins, and their fixture files were byte-equal to canonical JSON.

**Implemented and integrated:** [PR #20](https://github.com/shaden7/emergence-lab/pull/20), head `7109bba`, merge `306e9fb378c91f476b465892e9da4a525157e105`.
- The verifier checks the file-byte digest against the pin. Separately, it checks the report's canonical digest and embedded config against the file.
- New regression test compares the real pins with the repository configs, plus two negative tests.
- The archive workflow now also triggers when the verifier changes.
- The protocol doc records both digest conventions.
- **No pin, config, seed, budget or acceptance criterion changed.**

**Tests actually completed:**
- Local `pytest -q`: 165 passed.
- PR head CI success: push [38046784820](https://github.com/shaden7/emergence-lab/actions/runs/38046784820), pull_request [38046800647](https://github.com/shaden7/emergence-lab/actions/runs/38046800647).
- `main` CI 38047147413: success.
- Local finite-size gate re-run (NumPy 2.5.3, 2 CPUs): raw `b18423a2…` reproduced (third reproduction), `gate_pass True`. The fixed verifier with production pins passes on this output.
- Review recorded on PR #20: [comment](https://github.com/shaden7/emergence-lab/pull/20#issuecomment-6096831879), PASS for engineering merge. This is an AI-mediated self-review.

**Gate 6 — numerical/provenance observation, verified:**
- Archive run [38047147426](https://github.com/shaden7/emergence-lab/actions/runs/38047147426) on `306e9fb`: all steps **success**, including release publication and re-download verification.
- Release [`phase0-evidence-2026-10-10-v1`](https://github.com/shaden7/emergence-lab/releases/tag/phase0-evidence-2026-10-10-v1), target `306e9fb`, contains 7 assets. Key asset digests: `coverage_gate.npz` `97a81cb7…`, `finite_size_gate.npz` `b18423a2…`, `phase0_archive_manifest.json` `f9ec68e1…`.
- Independently checked by this Director outside the workflow:
  - Downloaded all assets via the REST asset endpoint; local `sha256sum` matches the pinned and API-reported digests.
  - `python -m emergence_lab.archive_evidence` on `main` `306e9fb` passes on the downloaded files.
  - Local `coverage_gate --from-npz` re-analysis of the released gate-4 NPZ reproduces the original result: L16 379/400, L32 381/400 covered; power controls 314/400 and 48/400 fail as required; `gate_pass True`.
- **Report gate 6 is therefore met** as preregistered in [PHASE0_EVIDENCE_ARCHIVE.md](PHASE0_EVIDENCE_ARCHIVE.md).
- Limitation: release assets can be deleted by repository administrators. Identity is detectable via the pinned hashes in Git, not immutable.

**Evidence level:** engineering fix plus a verified provenance/archival observation. This is no new physics. **Scientific decision: Phase-0 remains NO-GO** until a separate, reviewed GO/NO-GO decision record exists. Carry-over caveats:
- At L32, short-chain per-chain ESS intervals under-cover.
- The gate-5 `1/nu` estimate passes only through the preregistered tolerance.
- The L32 critical-mixing and burn-in replication raw series are not archived. Whether they need retention is still to be assessed.

**Deployment:** none. No Lightsail or EatSleepFeel interaction, no new spending.

**Next single step:** a later Director session, not this producer, writes the reviewed Phase-0 GO/NO-GO decision record:
- Audit gates 1–6 against their preregistered criteria with links.
- Decide explicitly whether the carry-over caveats block Phase 1 or become Phase-1 constraints.
- Decide whether the remaining Phase-0 raw series need archival.
- Only after a GO: Pilot A per `docs/PILOT_A_CAUSAL_PROPAGATION_PREREGISTRATION.md` as a separate reviewed code PR.

Director run rd-claude-20261010T105555Z-c25439: start 2026-10-10T10:55:25Z, end 2026-10-10T11:12:23Z, duration 16 min

## Director session: Phase-0 raw-data archival infrastructure (2026-10-10, `rd-gpt6-20261010T103425Z-a274c6dd`)

**Question:** can we durably preserve the registered gate-4 and gate-5 raw Monte Carlo data, validate their identity after Actions artifact expiry and objectively clear report gate 6?

**Recovery/orientation:** the prior Director released the lease cleanly (`d355c8f`), no PRs were open, and `main` at `1a17fb6` was CI-green. The finite-size gate in merged PR #18 was a local run only; no runner reproduction of its raw digest had yet occurred. No running external workflow was found before this session's work.

**Implemented and integrated:** [PR #19](https://github.com/shaden7/emergence-lab/pull/19), merge commit `8d83d8e19f62356df1ba28e047b758f27b914b9c`, adds an archive verifier with independently fixed raw/config SHA-256 for gates 4/5, checks original report and negative-control status, per-array digests and source provenance; tamper/control tests; a GitHub Actions archival workflow; an [archive protocol](PHASE0_EVIDENCE_ARCHIVE.md); and an updated README.

**Tests actually completed:** exact PR head `5b2d668c594eaf6325963a55fdce2611c5edc75c` [pull-request CI 38045738942](https://github.com/shaden7/emergence-lab/actions/runs/38045738942) **success** (pytest, smoke, exact4); matching push CI 38045735561 **success**; merged `main` [CI 38045856487](https://github.com/shaden7/emergence-lab/actions/runs/38045856487) **success**. PR review verdict **PASS for engineering merge, not for scientific gate 6**; the review is AI-mediated, not external peer review.

**Actual archive job (superseded: run 38045856455 failed closed at the verifier step, see the 2026-10-10 `rd-claude-20261010T105555Z-c25439` entry above; gate 6 later verified via run 38047147426):** [Actions 38045856455](https://github.com/shaden7/emergence-lab/actions/runs/38045856455) on exact merge commit `8d83d8e`: environment setup succeeded, registered gate-4 raw archive successfully downloaded from reproducibility run `38042967864`; the 5.69e9-proposal finite-size gate-5 reproduction was in progress, with a 30-minute step and 45-minute job cap. **No gate-5 runner result, release publication, downloadable release, or gate-6 PASS was observed at this handoff.** Do not infer success from job dispatch. GitHub Release target if validated: `phase0-evidence-2026-10-10-v1`; original NPZ SHA-256 values are fixed in the protocol. No Lightsail deployment or new spending was performed.

**Evidence level:** engineering implementation + passing CI; prior known gate-4/5 numerical observations remain scoped as recorded. **Scientific decision: Phase-0 NO-GO remains unchanged.** The gate-5 1/nu fit needs the preregistered tolerance; short-chain per-chain L32 ESS intervals under-cover.

**Next:** audit the final status and jobs/logs of run `38045856455`; verify release assets exist and their downloaded raw bytes match the pinned digests before any gate-6 PASS. On mismatch/failure, repair without overwriting evidence or adjusting preregistered criteria. Independently assess whether other Phase-0 time series (e.g. critical L32 and burn-in replication) also need durable retention, then record a separate reviewed GO/NO-GO decision. The separate Phase-1 causal Pilot A remains design-only until that decision.

## Mission
Emergence Lab investigates whether the fundamental laws and structures of physical reality—including spacetime, matter, and interactions—can emerge from simpler underlying principles, relations, or computational processes.

The Ising benchmark is a calibration step. The long-term question encompasses foundational spacetime, matter, interactions, and the principles that might give rise to them; candidate models still require rigorous mathematical and empirical evaluation.

## Documentation iteration (2026-10-09)
- Added `docs/OVERVIEW.md` to separate foundational-physics vision, specific research questions, validation methodology and roadmap.
- Refined `AGENTS.md` to require top-down observables, controls, evidence levels, bounded experiments, and reproducible session handoffs.
- Documentation-only change; no new experiment, proof, or deployment verification resulted from this iteration.

## Research process iteration (2026-10-09)
- Documented a sequential hourly **Research Director** model in `docs/RESEARCH_DIRECTOR.md`, with optional specialized review only when delegation is actually available.
- Added deconfliction guidance: inspect open issues/PRs, prefer continuing existing work, use isolated branches, do not treat repository files as concurrency locks.
- Added evidence and milestone-review checklists, including an independent skepticism gate for novel claims.
- This is **workflow documentation only**. It does not update the scheduled ChatGPT automation, verify the Lightsail deployment, run experiments, implement subagents, or introduce new scientific findings.
- The hourly automation should read the Director protocol after PR #2 is merged; actual tool/subagent capabilities in scheduled invocations are unverified.

## Director automation activation (2026-10-09)
- Merged Research Director governance protocol via PR #2 (merge commit `5ef471ef98c8e1da05703ef644af784165c35f79`).
- Updated the existing **enabled hourly ChatGPT task** to read `docs/RESEARCH_DIRECTOR.md`, inspect open work before editing, prioritize Ising calibration, and treat networks as optional mathematical models rather than physical ontology. The hourly cadence remains unchanged.
- Clarified Issue #4: lattice dimensions encoded at construction time are estimator controls, not emergent spacetime discoveries.
- The task has **not yet demonstrated a successful subsequent hourly research run**, nor are GitHub write/tool availability or the Lightsail deployment verified by this documentation update. No simulation, proof, or code test was executed in this iteration.

## Autonomous integration governance (2026-10-09)
- Adopted [docs/WORKFLOW_POLICY.md](WORKFLOW_POLICY.md) directly on `main` as the binding source-of-truth and PR integration policy; synchronized `AGENTS.md`, `docs/RESEARCH_DIRECTOR.md` and the README. This was a **process/documentation-only correction**, not a scientific result or a code deployment.
- The project owner is **not** a routine PR reviewer. Subsequent research sessions are responsible for review, verification, correction and eligible merges. Agent-led review must not be misrepresented as external peer review; scientific claims and deployments retain stronger evidence/risk gates.
- Default work-in-progress limit: **3 open research/feature PRs**. When the backlog exceeds this, prioritize reviewing and integrating existing work over opening further feature PRs.
- At policy adoption, eight PRs were recorded as open: Ising dependency stack #1 → #3 → #7 → #9 → #10, plus #5 (representation-neutral strategy), #8 (literature review), and #11 (causal pilot). This is a historical snapshot; agents must refresh actual GitHub status each run.
- No Ising PR or other research PR was reviewed/merged by this governance iteration. No experiments were executed. A scheduling prompt may bootstrap this policy, but GitHub remains the binding authority.

## Session coordination implementation (2026-10-10)
- Created persistent `coordination/research-lock` branch, containing `lease.json` initialized `idle`; the operational state is deliberately not committed to `main`.
- Adopted [RESEARCH_LOCK.md](RESEARCH_LOCK.md) as the binding Director lease protocol via `AGENTS.md` / [WORKFLOW_POLICY.md](WORKFLOW_POLICY.md) / [RESEARCH_DIRECTOR.md](RESEARCH_DIRECTOR.md). Research-side mutations require CAS acquisition, ownership verification, periodic heartbeat, owner-checked release and two-hour stale-lease recovery.
- **GitHub connector integration check:** two candidate lease commits derived from the same initial HEAD; the first expected-SHA ref update returned success. The stale contender returned a generic GraphQL error (not a typed concurrency error); rereading the ref confirmed the first candidate remained HEAD. A guarded update then restored `idle` (commit `2a67540b9dd47280b3925b2065c5c858f60c18fd`). This demonstrates observed contention handling, not a proof of universal exclusion under failures.
- **Operational limitation:** enforcement is cooperative; every Director must obey the protocol, and lost leases cannot cancel already-started external work. ChatGPT automation cannot be configured to run every 15 minutes (hourly minimum). This iteration neither changed a ChatGPT task's enabled state nor executed scientific simulations or CI.

## Representation-neutral strategy adopted (proposed 2026-10-09; integrated via PR #5 on 2026-10-10)
- `docs/REPRESENTATION_STRATEGY.md` distinguishes encodability, faithful/economical representation and physical explanation; requires an assumption audit, at least two substantively different model families where comparison is meaningful, null/failure cases and explicit discriminators before model choice.
- Methodology only: no simulation, proof, benchmark, ontology inference or discovery of new mathematics is claimed. Its gates keep cross-family computations **design-only until the Ising calibration gate is met**, which is consistent with the current Phase-0 NO-GO.
- Review correction at integration: the Physics Reports GPT introduction is attributed to M. Plávala (arXiv:2103.07469), not Janotta et al.

## Implemented (repository code on `main`, 2026-10-10)
- 2D ferromagnetic Ising model, periodic lattice, Metropolis updates.
- Autocorrelation-aware chain diagnostics and independent-chain Student-t intervals; zero between-chain variance yields undefined intervals (`stats.py`).
- Exact 4x4 enumeration reference and provenance-checked holdout validator (`exact4.py`); interval-coverage audit (`coverage4.py`); paired burn-in sensitivity (`burnin4.py`).
- Phase-0 diagnostics: finite-size pilot with J=0 null (`finite_size.py`), exact-stationary start comparison (`equilibration4.py`), L16/L32 hot/cold mixing and ESS (`mixing_pilot.py`, `scripts/mixing_diagnostics.py`), interacting 1D Ising null (`ising_1d_control.py`), AR(1) autocorrelation controls.
- CLI seed-collision check and 1e8 spin-proposal default budget before any output (`cli.py`).
- Exact finite-torus energy (Kaufman/Beale) for any M x N periodic lattice (`exact_finite.py`), checked against 4x4 enumeration and an independent transfer matrix; rank-normalized/folded split-R̂, bulk/tail ESS and Geyer per-chain ESS (`convergence.py`, matches ArviZ 1.3.0 to ~1e-12); preregistered L32 critical-mixing gate runner (`critical_gate.py`, manual dispatch only); independent single-cluster Wolff cross-check (`scripts/wolff_crosscheck.py`); preregistered burn-in replication runner with exact Student-t p-values (`burnin_replication.py`, manual dispatch only). Preregistered many-batch coverage gate at L16/L32 with re-analysis from saved raw `.npz` (`coverage_gate.py`, manual dispatch only). Preregistered finite-size gate L = 8…48 with jackknife errors, exponent fits, exact energy/specific-heat checks and non-critical controls (`finite_size_gate.py`, manual dispatch only).
- Heavy fixed-seed pilots run only on manual `workflow_dispatch`; ordinary pushes run pytest, smoke and the exact4 holdout.
- Deterministic seeded CPU experiments with JSON configs.
- CSV measurements and JSON manifest, basic pytest tests, Docker container capped at 0.5 vCPU and 1536 MB.
- Smoke and larger nightly experiment configs; GitHub CI.
- Manual GitHub Actions Lightsail deployment targeting /opt/emergence-lab; deploy workflow checks prerequisites, builds, runs smoke, then installs cron for 02:00 UTC.

## Verified operational status (2026-10-09)
- [Lightsail deployment run 37985438961](https://github.com/shaden7/emergence-lab/actions/runs/37985438961), on commit 1533d6f17bd1b23029f9ae86613db0fc2a240de3, completed **success** at 20:12 UTC. The remote build/smoke step succeeded; it checks smoke manifest and measurements files and only then installs the scheduled 02:00 UTC cron file.
- The server's actual output contents and subsequent cron execution remain **uninspected**. The deployed revision predates all code merged on 2026-10-10 (statistics, exact4, CLI guards); **no redeployment has been performed or reviewed**. `configs/nightly.json` (6.1e7 spin proposals) passes the new CLI budget, so a future deploy would not be blocked by it, but deployment still requires a separate reviewed decision.
- No validated finite-size scaling, Lean integration or autonomous LLM hypothesis generator exists.

## Scientific cautions
Monte Carlo samples are autocorrelated; the initial averages do not demonstrate a phase transition or novel physical findings. The infinite-lattice Ising benchmark critical temperature is 2/log(1+sqrt(2)) in units J=k_B=1.

## Next priority (updated 2026-10-10, after PR #18)
**Superseded 2026-10-10: Phase-0 decision is now GO (scoped, C1–C5), see [PHASE0_DECISION.md](PHASE0_DECISION.md).** Historical text: Phase-0 decision remains **NO-GO**; Phase 1 has not started. Cleared so far: L32/Tc critical mixing (PRs #13/#15), burn-in replication (PR #16), report gate 4 interval coverage (PR #17; **reproduced byte-identically on the GitHub runner**, owner-dispatched run [38042967864](https://github.com/shaden7/emergence-lab/actions/runs/38042967864), `.npz` SHA-256 `97a81cb7…`, Python 3.12.15), and now **report gate 5, finite size** (PR #18: β/ν, γ/ν within statistical error in all five windows; 1/ν passes only via the preregistered tolerance; exact energy/specific heat at L = 8…48 within |z| ≤ 1.35; both non-critical controls rejected). Remaining, in order:
1. ~~**Raw-artifact durability (report gate 6):**~~ **Done 2026-10-10:** verified via PR #20 and archive run 38047147426, release `phase0-evidence-2026-10-10-v1`; see the top entry. Next is the separate reviewed GO/NO-GO record. Original note: Actions artifacts and logs are not reachable from the review environment and expire; the PR #18 `.npz` (SHA-256 `b18423a2…`) exists only in the producing session, the PR #17 `.npz` additionally as a runner artifact of run 38042967864 (finite retention). Decide an archive location (e.g. release assets) as a reviewed change; hash simulation output separately from analytic references. This is the last open Phase-0 gate; after it a reviewed GO/NO-GO decision record is due.
2. Optional later-pass checks of PR #18: (a) manual dispatch of the finite-size-gate CI step on `main` (should reproduce `.npz` SHA-256 `b18423a2…`; `workflow_dispatch` returns 403 for the Director integration, the owner can trigger it); (b) test the correction-to-scaling hypothesis for the 1/ν bias (fit with a correction term or Binder-derivative estimator) on the saved data — exploratory, not a gate.
3. Only after the Ising gate: implement Pilot A per `docs/PILOT_A_CAUSAL_PROPAGATION_PREREGISTRATION.md` as a separate reviewed code PR.
4. Deployment of merged code to Lightsail: only as a separate, reviewed decision with EatSleepFeel impact check.

## Handoff requirements
After each meaningful research iteration, record: question, exact commit and config, computational resource budget, observed results, uncertainty and negative controls, scientifically supported conclusion, limitations, and next experiment. Keep large raw result files in versioned artifact storage rather than bloating Git history.

## Milestone 2: first uncertainty diagnostics (2026-10-09; merged via PR #1, `df5ae735`)

**Research question:** How does temporal autocorrelation reduce the information content of sampled finite Ising chains near the benchmark critical temperature?

**Implementation:** New per-chain integrated-autocorrelation heuristic and effective sample count, adjusted within-chain SEM, and independent-seed Student-t approximate 95% intervals across *chain means* (never naïvely pooled sweeps); outputs measurements.csv, summary.csv and a manifest containing statistical method and caveats. Trapped or short chains report missing diagnostics. Simulation and nightly compute configs are unchanged.

**Controls / falsification criterion:** Synthetic i.i.d. Gaussian versus AR(1) correlated series must show reduced effective count under correlation; constant series must not report false certainty; same simulation seed must return same results; CI/smoke outputs must exist. Statistical confidence is provisional without empirical coverage checks and equilibration tests.

**Evidence (executed locally, not on Lightsail):** 10 pytest tests passed; 12-chain configs/smoke.json run completed and wrote 6 aggregate rows. Config SHA-256 31d500fb653db1368d46364c561c825770faa289a6775529192e5b1cb7ae8b5b, base repository commit 9d541146556e32187812175ea99a41ddf5daaa51, proposed branch research/ising-statistics-m2-20261009, Python 3.13.5, NumPy 2.3.5; local GIT_SHA was unset and therefore null in local manifest. Details: [experimental note](experiments/2026-10-09-ising-uncertainty.md).

**Numerical observation:** At L=16, T=2.269185, each of two independently seeded chains produced 40 measured configurations. Heuristic effective counts for |M| were ~4.56 and ~3.86, implying strong serial dependence for this short run. Between-chain |M| mean ~0.68555 and a very wide unconstrained approximate 95% interval [-0.00436,1.37545]. This is **not** a phase-transition inference or a new physical result.

**Limits and cost:** Only two short-run replicates and 100 burn-in sweeps, no demonstrated equilibration/normality or interval coverage, and potentially underestimated long autocorrelation tails. Local budget 12 chains × 300 sweeps with L=8/16. Nightly budget unchanged: 128 chains with 1000 sweeps, Docker 0.5 CPU/1536 MB and 7200 s script timeout. No remote experiment was started during this iteration.

**Next discriminating experiment:** Pre-register independent holdout seeds, 4–8 chains, longer burn-in and sampling near critical T, compare correlation-window and burn-in sensitivity, then use finite-size scaling and a noninteracting-spin negative control. No fundamental-physics claim is supported by current numbers.

## Validation milestone 3 — finite 4x4 equilibrium reference (2026-10-09; merged via PR #3, `bfcbbe88`)

**Scientific question:** Do the seeded Metropolis equilibrium estimates and the independent-chain uncertainty summaries reproduce an independently calculated finite-system Boltzmann distribution? This is a method-validation question only, not an argument for fundamental physics.

**Independent baseline:** Enumerate all 2^16 = 65,536 spin configurations of a periodic 4x4 Ising lattice. Count disagreeing horizontal/vertical bonds directly from bitstrings, without calling the Monte Carlo energy function, then normalize Boltzmann weights. Exact numerical reference (T, energy per spin, |M|): (1.5, -1.95064256146, 0.98617329782), (2.269185, -1.56562403375, 0.84386054623), (3.5, -0.77615005043, 0.48843718389). These are floating-point evaluations of a finite exhaustive sum, not a newly proved theorem.

**Holdout specification and budget:** configs/exact4_validation.json, with fixed base_seed **2026120101** (different from prior development/pilot seeds), L=4, three temperatures, twelve independent chains per temperature, 800 burn-in sweeps plus 1800 sampled sweeps with a measurement every five sweeps. Total 36 chains, 1,497,600 proposed spin flips, 12,960 recorded measurements. NumPy enumeration requires roughly a few megabytes. Runs in ordinary GitHub CI, without changes to nightly Lightsail jobs or EatSleepFeel.

**Pre-execution anomaly-screen criterion for this holdout:** Recompute the mean and between-chain SEM directly from measurements.csv, compare to summary.csv, and require |chain-mean minus exact reference| <= 3.5 times the between-chain SEM for each of 3 temperatures x 2 observables. Reject missing/duplicate chains or seeds, config/manifest mismatch, zero SEM, and inconsistent summary aggregation. This is an **exploratory** diagnostic (not a calibrated 99.95% test); additionally record whether each reference lies within its reported nominal 95% confidence interval without requiring all six nominal intervals to contain their targets.

**Negative controls and checks:** In tests, the enumeration must approach the binomial independent-spin infinite-temperature mean |M| and the ordered ground-state limit; spin-flip signed magnetization must vanish. Deliberately biased summaries must fail the 3.5-SEM screen; malformed run data must fail validation. Independent enumeration checks both MC energy and magnetization, unlike comparing two implementations of the same estimator.

**Verified CI holdout (2026-10-09 20:33 UTC):** [GitHub Actions run 37987761035](https://github.com/shaden7/emergence-lab/actions/runs/37987761035) completed **success** on code commit **2d605e73900492e09492626e21fc9040ad791ac0** (PR #3 branch stacked on PR #1). The job checked out this exact commit, completed **18 pytest tests**, ran all **36 seeded chains**, wrote three summary rows, passed the exact-reference validator for all six comparisons, and uploaded the `smoke-results` artifact (id 11643658088, including `results/exact4`). The six absolute discrepancies in between-chain SEM units, energy then |M|, were: T=1.5 (0.79282, 0.72759), T=2.269185 (0.35814, 0.30627), T=3.5 (0.31131, 0.19801). The maximum is **0.793 SEM**, below the pre-run anomaly cutoff of 3.5 SEM. Reference values and the new fixed holdout config were committed before the official run. Config SHA-256: **d61c9b45b3629937f30fc9288f75d565ef90d2990a117f826173eda893129c68** (recheck exact hash before editing). GitHub CI uses Python 3.12; package revisions are captured in its install log. This is a **numerical calibration observation**, not a theorem or proof of interval coverage.

**Exploratory local checks:** A local *manually transcribed* Metropolis implementation (not a checked-out repository) had previously been used for 12-chain pilot/development-seed runs with base seeds 2026101001 and 2026110101; discrepancies were below 2.5 between-chain SEM. These were *not* treated as the fixed holdout. The GitHub CI holdout uses base_seed 2026120101. No Lightsail deployment performed.

**Limitations:** Only L=4, three temperatures and a single independent holdout; 3.5-SEM decision is deliberately conservative and cannot prove correct interval coverage or equilibration. The exact 4x4 finite-system reference has no singular phase transition; testing critical universality or fundamental spacetime properties requires different experiments.

**Next action:** Check CI test outcome and the uploaded holdout artifact. If it passes, retain the raw CSV/manifest and compare nominal 95% coverage over multiple distinct seeds, convergence with burn-in, and lattice-size scaling before making statistical claims. Stacked changes require review, then merge PR #1 before PR #2; do not auto-deploy.

## Exact4 provenance hardening (2026-10-09; merged via PR #7, `98bc941b`)

**Question:** Can an otherwise plausible holdout CSV pass finite-4x4 validation after its preregistered RNG seeds or simulator run parameters are substituted?

**Baseline and falsification:** The original validator checked global uniqueness of seeds, record counts, manifest/config SHA and summary agreement, but not the producer-defined mapping (size, temperature, repeat) to individual seeds or per-chain burn/sampling metadata. Require exact seed sets per temperature and configured sweep counts and measurement cardinality; deliberate substitution of one still-unique seed or one runtime field must cause a ValueError.

**Implementation (unmerged branch):** `research/exact4-provenance-review-20261009` extends `src/emergence_lab/exact4.py` with explicit seed-schedule and run-parameter checks, plus five mutation-based negative-control tests in `tests/test_exact4.py`. Proposed commits `5386e87b79af63452ccb187f39889afad8fd2b56`, `461ac3545117be03917e246782238bf6029fc451`. Stacked on PR #3, which remains open and targets PR #1.

**Evidence level (verified):** GitHub Actions [run 37994018946](https://github.com/shaden7/emergence-lab/actions/runs/37994018946) completed **success** for commit `f8c09bc8d88bb9b2d2914a4a3befabcbb73be6ee`: pytest, smoke, exact 4x4 holdout and artifact upload each succeeded. The validation here is software/measurement-consistency evidence, not a new Ising discovery. The earlier PR #3 run does not independently review this change. No new Ising numerical result or scientific theorem is claimed.

**Limits:** The CSV can still be fabricated with matching metadata; validation verifies structural provenance consistency, not cryptographic authenticity or independence of runs. Seed mapping mirrors `cli.py` and therefore shares its rounding/schedule assumptions. Chain autocorrelation/equilibration and interval coverage remain open. Zero extra VM/GPU/API budget; no Lightsail deployment.

**Next step:** Inspect detailed CI logs/artifacts and request code review before merging the stack in order PR #1 -> PR #3 -> PR #7. Then pre-register an independent multi-batch coverage experiment with known exact 4x4 targets, fixed seeds, planned interval coverage and uncertainty; distinguish long-chain Monte Carlo bias from between-batch randomness.

## M4: exact4 interval-coverage pilot (2026-10-09; merged via PR #9, `006fa0ed`)

**Question:** Across *independent* batches of six independent seeded 4x4 Ising chains, how frequently do nominal 95% between-chain Student-t intervals enclose the exact finite-system energy and absolute-magnetization expectations?

**Preregistered protocol:** `configs/exact4_coverage_pilot.json`: temperatures 1.5, 2.269185 and 3.5; 24 batches per temperature; 6 chains per batch; 400 burn sweeps + 800 sample sweeps at interval 5; base seed 2027010101 (disjoint from milestone-3 holdout). Total 432 chains; 8,294,400 single-spin update proposals; 69,120 sampled configurations; capped at 500 chains by implementation. No Lightsail/paid API resources; run the full pilot only on a reviewed, bounded worker with adequate CPU time.

**Observable, controls, falsification:** For each temperature and each observable record 24 coverage indicators and Wilson binomial 95% uncertainty bounds. Exact enumeration is the independent target. Primary exploratory concern: a nominal interval showing very low empirical coverage; do not call 24 batches a precise coverage calibration. At 24 batches, even full observed coverage only bounds the population coverage loosely. Fix seed plan before running; retain *negative* and failed batches. Unit tests cover deterministic seeded short run, Wilson endpoints and rejection of invalid/excessive configs.

**Status:** `src/emergence_lab/coverage4.py`, configuration, tests committed to `research/exact4-coverage-pilot-20261009` (stacked on PR #7). Full configured 432-chain pilot **not executed** in this handoff; no numerical coverage claims. Test/CI result must be separately verified; no deployment.

**Methodological reservations:** Independent random-number seeds make batch Monte Carlo runs pseudorandomly disjoint, not logically independent guarantees. The t intervals are vulnerable to equilibration bias and nonnormal chain means; intervals for energy and magnetization within a batch are correlated. Wilson intervals across batches assume independent Bernoulli coverage events; no multiple-testing correction. A single finite-size target cannot validate critical scaling. The 24-batch pilot is for detecting gross miscalibration, not proving 95% coverage.

**Next action:** Verify CI on new PR, execute reviewed budgeted 432-chain pilot with recorded Python/NumPy and revision, retain machine-readable results, then compare observed undercoverage with burn-in/sampling sensitivity on *fresh* seeds before statistical claims.

### M4 CI execution extension (2026-10-09)

A follow-up change to PR #9 added the **full preregistered 432-chain M4 experiment** as an automated CI step, restricted to the M4 branch and capped at 20 minutes of CI wall-clock time. The step writes `results/exact4_coverage.json`, preserved by the existing upload-artifact action even on test failure. No Lightsail resources are required. The branch-specific CI run [37994539424](https://github.com/shaden7/emergence-lab/actions/runs/37994539424) was **in progress** at handoff; do not infer scientific results or completed execution until logs and uploaded JSON are inspected. Commit at submission: `d4169cffdb87dfd93aebefb5da2e4f27a13b292d`.

**A priori decision:** This is a method-calibration *measurement*, not a confirmation test that must pass. Undercoverage is a negative finding to retain, not grounds to retry with fresh seeds until favorable. The six reported empirical rates share correlations and should not be treated as six independent discoveries. Compare realized intervals to Wilson uncertainty; any inference about actual calibration must assess burn-in sensitivity using nonoverlapping new seeds and may need larger batch counts.

### M4 first fixed-seed coverage observation — measured 2026-10-09

**Execution and traceability:** [CI run 37994539424](https://github.com/shaden7/emergence-lab/actions/runs/37994539424), branch commit `d4169cffdb87dfd93aebefb5da2e4f27a13b292d`, Python 3.12.15 / NumPy 2.5.3 / pytest 9.1.1. All 26 pytest tests, smoke, finite 4x4 holdout and **full M4 432-chain batch experiment** completed successfully. M4 step ran approximately 51 seconds. Raw JSON artifact: [smoke-results #11646079121](https://github.com/shaden7/emergence-lab/actions/runs/37994539424/artifacts/11646079121); includes `results/exact4_coverage.json`; ZIP SHA-256 `8fefb1ceea323e67305a39681c21248927aa9f9e03a2a0cc9b4d581a4f89d08d`.

**Observed nominal 95% coverage (24 batches per temperature and observable):**

| T | Energy covered | |M| covered |
| --- | --- | --- |
| 1.5 | 23/24 = 95.8% (Wilson 95% 79.8–99.3%) | 23/24 = 95.8% (79.8–99.3%) |
| 2.269185 | 23/24 = 95.8% (79.8–99.3%) | 24/24 = 100.0% (86.2–100%) |
| 3.5 | 22/24 = 91.7% (74.2–97.7%) | 22/24 = 91.7% (74.2–97.7%) |

**Interpretation — numerical observation, not proof:** No gross undercoverage appeared in these six *correlated* pilot tallies. They are consistent with nominal coverage but are too imprecise to establish it. Two observables within a batch are not independent. A single fixed-seed experiment cannot establish general reliability; no adjustment for inspecting six diagnostics was applied. Run configurations and seed selection were set before the observed results; no selective rerun should be used to alter this evidence.

**Engineering follow-up:** To avoid repeating the expensive 432-chain pilot on each ordinary push, its CI step is now restricted to explicit `workflow_dispatch` runs of the M4 branch; prior successful run and original artifact remain authoritative. A subsequent CI job may confirm tests but does not constitute a fresh fixed-seed coverage experiment.

**Next discriminating measurement:** Pre-register a **new**, disjoint-seed burn-in sensitivity experiment (e.g. 0/100/400/1600 sweeps, matched chain sampling; fixed compute cap), report both mean bias relative to exact reference and interval coverage, and study whether near-critical uncertainty estimates are robust. Do not interpret the current results as evidence for emergent spacetime.

## Burn-in sensitivity follow-up (2026-10-09; merged via PR #10, `171bab66`)

**Question:** How sensitive are finite-4x4 Ising means and nominal between-chain CI coverage to initial equilibration (burn-in)?

**Design:** Frozen config `configs/exact4_burnin_sensitivity.json`: three temperatures, 10 independent batches of four chains per temperature, same seed within each matched comparison across burn-in arms 0, 100, 400, 1600; 800 sampling sweeps, every fifth sweep. 480 chains, 4 × 10 × 4 × 3 × 800 sampling sweeps plus differing burn-in; budget cap 500 chains; no Lightsail. Paired differences must not be analyzed as independent arms.

**Implementation:** `src/emergence_lab/burnin4.py`, tests and configuration on branch `research/exact4-burnin-sensitivity-20261009` (PR #10). The fixed-seed experiment was executed in CI (below) and re-executed in the 2026-10-10 review. Negative findings must not be discarded.

**Limitations:** With only 10 batches per condition, binomial uncertainty of interval coverage is substantial. Initial states are random spins, and chain mean differences conflate burn-in bias, Monte Carlo noise and trajectory divergence. Distinct seeded pairs do not establish absence of bias. No causality, geometry, or fundamental-physics conclusion follows.

**Next:** Run CI pytest, review the branch and execute bounded experiment as a manually triggered GitHub Actions step, retaining JSON outputs and detailed diagnostics. Report observed biases and failure cases, compare exact reference and independence assumptions. Do not deploy to Lightsail.

### M4 burn-in sensitivity: first fixed-seed numerical observation (2026-10-09)

**Confirmed execution:** [Actions run 37995173975](https://github.com/shaden7/emergence-lab/actions/runs/37995173975), experiment revision `7518f095e4776b3c8a751c354ada320350d80648`. Pytest, smoke, exact4 control and full burn-in experiment all succeeded. Full raw JSON `results/exact4_burnin.json` uploaded in [artifact 11647295336](https://github.com/shaden7/emergence-lab/actions/runs/37995173975/artifacts/11647295336) (ZIP SHA-256 `41392c9ba682c8ce8b331f30b1242179a91756542b56d98090ef473d02b365dd`). The controlled burn-in step ran approximately 45 seconds on GitHub CI; not on Lightsail.

**Observed coverage counts out of 10 batches at each temperature (energy / |M|):**

| Burn sweeps | T=1.5 | T=2.269185 | T=3.5 |
| --- | --- | --- | --- |
| 0 | 9/10, 8/10 | 10/10, 10/10 | 8/10, 10/10 |
| 100 | 9/10, 10/10 | 10/10, 10/10 | 9/10, 10/10 |
| 400 | 10/10, 10/10 | 10/10, 10/10 | 8/10, 10/10 |
| 1600 | 10/10, 10/10 | 8/10, 8/10 | 10/10, 10/10 |

**Critical interpretation:** There is **no monotonic burn-in improvement in the observed coverage counts**. A drop from 10/10 to 8/10 at the benchmark temperature with longer burn-in is a reminder that stochastic batch coverage fluctuates; it is not evidence that longer burn-in is harmful. Ten batches have very broad binomial uncertainty; even 10/10 does not prove calibrated 95% coverage. Matched seed arms are correlated, and 24 coverage metrics were inspected; no independent multiplicity-corrected significance finding or equilibration proof is claimed. The JSON contains per-batch mean deviations and paired differences but these have **not yet been summarized or independently reviewed** in this handoff.

### Later-pass review and paired bias analysis (2026-10-10)

**Review (AI-mediated, non-independent of the project's agents):** seed schedule verified to depend only on (temperature, batch, chain), so arms are genuinely paired and share their random initial state; seeds 2027021001–2027021120 are disjoint from the M4 pilot (2027010101–2027010532) and the exact4 holdout. Added tests for paired-contrast consistency, shared seed schedule across arms (a deliberate seed-offset mutation fails this test), batch-count caveat and rejection of invalid variants/budgets; corrected a caveat that stated 12 instead of the configured 10 batches.

**Reproduction:** local re-execution (Python 3.13.16, NumPy 2.5.3) reproduces all 24 coverage counts above exactly. The CI artifact ZIP could not be downloaded from the review environment, so no byte-level comparison was made.

**Numerical observation (post hoc, exploratory):** treating the 10 disjoint-seed batches as replicates, zero burn-in leaves a bias at T=1.5 in the direction expected from incomplete equilibration (|M| −0.0032 ± 0.0005, p = 0.00014; energy +0.0069 ± 0.0019, p = 0.005). Paired shifts from burn-in 0 to 100 are clearly nonzero at T=1.5 and T=2.269 (e.g. |M| +0.0039 ± 0.0005 at T=1.5, p = 0.00002) and survive a Bonferroni correction over the 18 paired tests; at T=3.5 no shift is resolvable. Binary coverage counts did not reveal this, so coverage tallies alone are a weak equilibration diagnostic at this sample size. One **unresolved anomaly candidate**: burn-in 1600 at T=1.5 shows an energy bias +0.0033 ± 0.0009 (p = 0.005), not surviving correction over 24 bias tests and without a known mechanism; it is not interpreted. Full table and method: [experimental note](experiments/2026-10-10-burnin-paired-analysis.md).

**Next discriminating step (proposed, not executed):** preregister a fresh-seed replication with ≥20 batches at T=1.5 and T=2.269 for burn-in 0, 100 and 1600, with paired shifts as primary outcome, to confirm the zero-burn-in bias and test whether the burn-1600 offset persists.

**Earlier next-step note (2026-10-09, now addressed above):** Inspect the raw paired bias shifts (not merely binary coverage), compute uncertainty from independent paired batches, and contrast longer sampling regimes and an analytically initialized equilibrium baseline where feasible. The run was predeclared, with no selective favorable reruns. The CI experiment step has been restricted to manual dispatch for future reproducibility without repeated load on each PR push.

## Research Director Phase-0 audit and decision (2026-10-09; merged via PR #12, `132369e9`)

**Question and decision:** Are the Monte-Carlo, uncertainty, control and provenance tools reliable enough to begin Phase 1? **NO-GO** on the present evidence. See [full audit and criteria](ISING_CALIBRATION_REPORT.md). The phase remains open; this is a **completed critical assessment**, not a claim that all calibration gates passed.

**Deconfliction:** GitHub PRs #1 → #3 → #7 → #9 → #10 were open and stacked on inspection; none had a recorded approving review. Audit branch `research/phase0-director-audit-20261009` was created from PR #10 SHA `069997129e98ca634e515767355ef1dbaa8dd5ce`; all modifications isolated there. PR #5 representation strategy, #8 literature draft and #11 causal-pilot preregistration remain separate. **No merges, deployments, Lightsail runs, paid services or EatSleepFeel changes.**

**Executed source-data audit:** GitHub Actions ZIPs for [M4 37994539424/artifact 11646079121](https://github.com/shaden7/emergence-lab/actions/runs/37994539424) and [burn-in 37995173975/artifact 11647295336](https://github.com/shaden7/emergence-lab/actions/runs/37995173975) were downloaded and the JSON records read directly, not inferred from PR summaries. Locally recomputed 6 × 24 coverage-cell observations, 24 arm summaries (each 10 batches) and 18 paired burn-in contrasts, including t-95-% uncertainty from independent batches, using `scripts/phase0_artifact_audit.py`. M4 observed counts: 23/24,23/24 at T1.5; 23/24,24/24 at Tc; 22/24,22/24 at T3.5 (E, |M|). At T1.5/zero burn-in: E bias +0.00693 [0.00264,0.01122] and |M| bias −0.00324 [−0.00440,−0.00208]. The 100-vs-0-burn paired contrasts: E −0.008594 ±0.003583, |M| +0.003887 ±0.001109 (95-%-t-halfwidth); 18 contrasts are exploratory and uncorrected. This supports caution about start bias, not an equilibrium proof.

**New experiment implemented and actually run:** `src/emergence_lab/finite_size.py` (checkerboard Metropolis and exact J=0 iid-spin control), `configs/fss_pilot.json`, `tests/test_finite_size.py`; L 8/16/24/32 × T 2.1/2.269185/2.45 × six chains per model; 72 Ising + 72 J=0, 27,648,000 Ising proposed flips. Local Python 3.13.5/NumPy 2.3.5: 3 new pytest checks passed; pilot 5.31 sec wall, 5.25 sec CPU, about 96 MB max resident memory. [CI 37996248059](https://github.com/shaden7/emergence-lab/actions/runs/37996248059), source commit `5d54156e6407a4f61006c28f3cbdef543712cd19`: **success**, including pytest, exact4 reference holdout, bounded pilot and artifact upload; [raw artifact 11646539226](https://github.com/shaden7/emergence-lab/actions/runs/37996248059/artifacts/11646539226), Python 3.12.15/NumPy 2.5.3. **All 144 numerical chain records match the local run exactly**, including seeds and observables. Fixed base seed 2027030001; separate null-model namespace. The null's |m| scales near L^-1 and χ_abs near L^0; Ising gives exploratory effective L slopes for |m| −0.1224 (chain-bootstrap95 [−0.1731,−0.0771]) and χ_abs +1.7141 ([1.2553,2.0721]) at externally known Tc. These are **not** calibrated critical-exponent estimators: bootstrap omits finite-size/systematic bias and only 6 chains/L were used. ν unmeasured.

**Autocorrelation controls executed:** `scripts/autocorr_synthetic_audit.py`, eight independent length-12000 stationary AR(1) traces per φ=0/0.5/0.9/0.98/0.995, exact analytic τ=(1+φ)/(2(1−φ)), fixed seeds 102938–102945. [CI 37996395511](https://github.com/shaden7/emergence-lab/actions/runs/37996395511) **success**, with [raw artifact 11647447009](https://github.com/shaden7/emergence-lab/actions/runs/37996395511/artifacts/11647447009). For φ=.995 true τ=199.5, original heuristic median 171.44 (range ~114.91–318.50), Geyer-like positive pairs median 171.44, block-mean width 500 median 121.28; credible long-tail underestimation/uncertainty risk, not an established universal direction of bias. Constant/short controls were reported undefined. Method does not test equilibration.

**Scientific and engineering restrictions:** Student-t across independent chain means requires mixing and approximate normality; M4 Wilson coverage ranges too wide, 18 paired contrasts unadjusted, small finite lattices and nonlinear χ/Binder estimates carry systematic bias; no dependable ν extraction, no Binder crossings claimed. Original `cli.py` rounds temperatures for seed scheduling and chain-count-only cap does not bound computational work; new finite-size pilot explicitly caps proposals. The downloaded artifact ZIPs have finite GitHub retention, not guaranteed permanent provenance. Independent review and integration remain open.

**Next discriminating experiment (not started):** Reconstruct exact equilibrium-distributed initial spin states for L4; independently contrast stationary, random, ordered-hot/cold starts on fresh fixed seeds over registered time windows, compare bias to exact enumeration and autocorrelation/window diagnostics; then test mixing and finite-size corrections at L16–32. Do not tune on M4 seeds or start Phase 1 before a new evidence gate.

### Additional controlled equilibration experiment (same isolated PR #12, 2026-10-09)

**Question:** Do L4 ensemble observables relax from random/fully ordered starts toward the independently enumerated Boltzmann reference, and what does an **exact stationary-initialized** positive control look like? **Change:** `src/emergence_lab/equilibration4.py`, `tests/test_equilibration4.py`, `configs/equilibration4_pilot.json` and bounded CI command. Commit `bc5bf407764f022465ed1c14e4c2366198cb4e32`, 3 temperatures, 64 distinct seeds per each of 3 starts (random, ordered, exact Boltzmann), snapshots at sweep 0/5/20/100/400; 576 chains/2880 raw records, 3,686,400 attempted random-site Metropolis flips; seed basis 2027040101. Explicit proposal cap 5 million; no Lightsail work.

**Verified execution:** Locally Python 3.13.5/NumPy 2.3.5, 3 new tests passed, 14.68s wall / 14.60s CPU, ~99 MB RSS. [GitHub CI 37996892064](https://github.com/shaden7/emergence-lab/actions/runs/37996892064) success; [raw artifact 11647700495](https://github.com/shaden7/emergence-lab/actions/runs/37996892064/artifacts/11647700495), Python 3.12.15/NumPy 2.5.3. **All 2880 raw numeric records identical** across CI and local; separately enumerated reference floats differ ~2.4e-14, not bitwise identical summaries. At T=1.5 random-start mean E bias vs exact reference at sweeps 0/5/20/100: +1.9741 ±0.0980, +0.3374 ±0.1213, −0.0376 ±0.0240, −0.0103 ±0.0347 (descriptive 95% t halfwidth over independent 64 chains). At Tc random start +1.5187 ±.0905, +.1594 ±.1482, −.0437 ±.1270, +.0188 ±.1301; exact stationary-init Tc zero-sweep −.0555 ±.1186. Initial fully ordered spins have zero within-ensemble variance and degenerate t intervals at sweep zero—**not statistical precision**.

**Critical limitations:** Intervals at 90 overlapping time/start/temperature/observable cells are not multiple-comparison corrected; correlated snapshot times, one occasional stationary-reference miss at Tc sweep400, and small finite-L size prohibit proof of detailed balance, convergence bounds or correct L16–32 sampling. Exact Boltzmann initialization is a constructed L4 positive control, not emergent physics. See `docs/ISING_CALIBRATION_REPORT.md` section F. **NO-GO remains**; next is independent L16/32 mixing/ESS/block-length diagnostic and review before merging. Draft PR #12 targets #10; no concurrent writes/merges into base.

### Director deepening: actual L16–32 ESS failure, analytical interacting null, source fixes (2026-10-09)

**Question:** Does agreement of L16/32 final hot/cold observables conceal insufficient effective sample sizes? Does the analysis distinguish 2D scaling not only from J=0 but also from an **interacting** control without finite-temperature criticality? See full measurements and critical caveats in `docs/ISING_CALIBRATION_REPORT.md` Sections G–I.

**L16/32 experiment** `src/emergence_lab/mixing_pilot.py` + `configs/mixing_pilot.json` (revision `e8ae9eb18ced369489cbb629fcb090f8fac2295e`): L16/32, T2.1/Tc/2.45, 12 independent hot/random and 12 ordered starts per size/temperature, 1800 sweeps / measurement every 5, all 360 per-chain samples retained, **144 chains / 165,888,000 attempted flips / 103,680 raw energy and absolute-magnetization values**, 3000 independent-chain bootstrap replicates. Local ~20.79s/~107 MB. [GitHub CI 37997377758](https://github.com/shaden7/emergence-lab/actions/runs/37997377758) **success**, [raw artifact 11648100844](https://github.com/shaden7/emergence-lab/actions/runs/37997377758/artifacts/11648100844), Python3.12.15/NumPy2.5.3. **103680/103680 raw scalar samples exactly match** local NumPy2.3.5 execution; aggregate τ floating difference ≤1e−12.

**Quantified failure:** At **Tc/L32**, |m| median τ=3.781 sampled intervals (each 5 sweeps), median ESS=23.9 of 180 samples, min ESS=4.16; **12/24** independently seeded chains had ESS<25. For energy at Tc/L32, median τ=2.216, min ESS=11.78, **4/24** chains had ESS<25. The controlled rule in source required both bootstrap hot-vs-cold mean differences within ±0.08 (|m|) / ±0.12 (E) and ESS≥25 for every chain: although **12/12** mean-difference intervals met the first criterion, **5/12** size/temperature/observable groups failed ESS and the rule was **False**. Gate is exploratory/non-universal and was not independently preregistered before first local run. A single Tc/L32 chain had τ_last=21.61 by original heuristic vs τ_batch20=7.14, showing method/win-size sensitivity. `scripts/mixing_diagnostics.py` independently recomputed **classic unranked** split Rhat: **1.0402** for |m| and **1.0137** for E at Tc/L32, with synthetic adversarial scale/location controls. No proof of mixing/non-mixing. The initial six-chain FSS exponent slopes are **not quantitatively reliable**.

**Actual source hardening on isolated PR #12:** `src/emergence_lab/cli.py` now validates planned seeds and **100 million attempted-spin default budget** before creating output, while preserving legacy L4 seeds; detects rounded-temperature collisions (e.g. 2.269180 vs 2.269190) and size/T aliases. `src/emergence_lab/stats.py` returns **undefined SEM/CI** for exactly zero variance between independent chains rather than artificially perfect precision. `src/emergence_lab/coverage4.py` counts missing intervals as **non-coverage** and records `interval_defined=false`. Added mutation/regression tests, CI successful [37997530526](https://github.com/shaden7/emergence-lab/actions/runs/37997530526), [37997611607](https://github.com/shaden7/emergence-lab/actions/runs/37997611607). All changes are unmerged; historical M4 data unchanged.

**Second negative model:** `src/emergence_lab/ising_1d_control.py` and `configs/ising_1d_control.json`, revision `71f0f3c77e3006e54ee42a1f142335bb9d5c58a0`: interacting 1D periodic nearest-neighbor ferromagnet with **no T>0 critical point**. The exact finite-L energy follows `Z_L=(2cosh(1/T))^L+(2sinh(1/T))^L`; independently checked by direct L8 enumeration. **96 chains, L8/16/24/32, T1.5/Tc2D/3.5, 8 reps, 300 burn+700 sample sweeps, 1,920,000 flips**, local 4.58s/~96MB. [GitHub CI 37998097492](https://github.com/shaden7/emergence-lab/actions/runs/37998097492) **success**, [raw artifact 11648136813](https://github.com/shaden7/emergence-lab/actions/runs/37998097492/artifacts/11648136813): 96/96 raw chain records and all 12 summaries identical to local. At 2D-Tc, 1D Binder U4 L8→L32 falls **0.419→0.029** and χ_abs stays ~0.28–0.39, distinguishing from 2D near Tc (U4 ~0.61, χ_abs increasing with L). This is an expected *control* under known 1D theory, **not emergent geometry**.

**Preserved anomaly and adaptive investigation:** At T3.5 the first 1D run's four L-energy means were all below exact values, with |difference|/between-chain SEM **1.721/1.675/2.734/1.620**. Do not discard or over-interpret uncorrected multiple comparisons. After seeing the discrepancy, an explicitly **adaptive**, distinct-seed longer-chain run was specified (`configs/ising_1d_anomaly_followup.json`; T3.5, 4 L, 8 chains, 1000 burn+10000 sample, 7,040,000 flips; new seed base 2099990101; local 14.97s): signed standardized energy differences approximately **−0.431/−1.943/+0.427/−0.431**. Not a preregistered confirmation; retain both raw experiments. [CI run 37998319268](https://github.com/shaden7/emergence-lab/actions/runs/37998319268) **success** on exact code commit `4f5c434506b9517e8774d3cd35275aaa6df355da`, [raw artifact **11648032310**](https://github.com/shaden7/emergence-lab/actions/runs/37998319268/artifacts/11648032310). All 32 per-chain records and four summary cells match the local run exactly. This is an **adaptive exploratory** replication, not a prospectively independent validation.

**Provenance:** New finite-size/AR1/L4-equilibration/1D/mixing scripts now record Python/NumPy versions and `GIT_SHA` from bounded GitHub CI in result JSON; scripts retain full raw controls and exact seed configurations. Historical Actions artifacts still have finite retention; long-term storage is an open requirement.

**Decision remains NO-GO.** A true next calibration gate needs longer independently seeded L32 trajectories at Tc, robust autocorrelation/window estimates, a modern rank-normalized folded convergence diagnostic, separated warmup & sampling, narrower new-seed coverage uncertainty, quantitative finite-size corrections, reviewed stacked merge #1→#3→#7→#9→#10→#12. **Do not start Phase 1**, deploy to Lightsail, or claim fundamental-physics discoveries.

### CI-cost containment and final review handoff (2026-10-09)

Completed bounded pilots were run successfully and primary artifact IDs/code revisions are documented above. New longer runs must not be triggered by routine documentation pushes: commit `ac9ccc055473b073aeebc639e13c80a7d09f9ddb` changes the combined phase-0 pilot workflow to **manual `workflow_dispatch` only**, on the isolated audit branch or after reviewed merge on `main`. Standard `pytest`, smoke and exact4 control remain in push/PR CI; M4/Burn-in original manual runs retain their own specific branch gates. GitHub Actions runner `timeout-minutes: 5`, `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`; **no Lightsail/EatSleepFeel interaction**.

**Review tasks, not automatically merged:** human code/methodology review for PRs #1, #3, #7, #9, #10, then draft PR [#12](https://github.com/shaden7/emergence-lab/pull/12), preserving the actual stack; verify full tests on resolved combined main, archive raw JSON durably, repeat L32 critical-T long-chain/warmup separated validation on fresh seeds and the new-seed CI-coverage protocol before choosing GO. Source baseline remains representation-neutral (#5) and literature draft (#8) open. **Decision NO-GO.**

### Durable artifact integrity register and final status (2026-10-09)

[Checksum registry](experiments/phase0-artifact-checksums-20261009.json) records **nine** actually downloaded source JSONs: CI run, Actions artifact ID, pinned code SHA, ZIP member name, and SHA-256 of extracted JSON. The JSON registry is versioned in GitHub; it is **not a durable copy of the raw source data**. The latter must be archived separately before Actions expiration for full long-term provenance. No paid service or new resource was created.

**Last known consolidated decision:** **NO-GO**; Ising calibration **not** declared complete. The draft review branch [PR #12](https://github.com/shaden7/emergence-lab/pull/12) contains source, configs, tests, null controls, all measured uncertainties, quantitative L32 ESS failures, report and research-state updates. PRs #1/#3/#7/#9/#10/#12 require human review in dependency order; no automatic merges on CI alone. Next essential research gate is independent longer critical-L32 and interval-coverage confirmation with preregistered controls and trustworthy ESS.

### Later-pass review and integration status of PR #12 (2026-10-10)

**Status correction:** the 2026-10-09 text above records PRs #1 → #10 as open and asks for human review. Since then PRs #1, #3, #7, #9 and #10 were merged by Director sessions, and `docs/WORKFLOW_POLICY.md` assigns routine review and merge to agents; no human review is required. The historical text is kept unchanged as an audit trail.

**Review (AI-mediated, not independent external review):** core code changes checked — `cli.py` keeps the legacy seed formula but now rejects seed collisions and plans above 100 million spin proposals before writing output (`configs/nightly.json` at 6.1·10⁷ proposals stays within the limit, so the Lightsail cron configuration is unaffected); `stats.py` returns undefined intervals for zero between-chain variance; `coverage4.py` counts undefined intervals as non-covered. New CI steps run only on manual `workflow_dispatch`.

**Independent re-execution (Python 3.13.16, NumPy 2.5.3) on the branch merged with `main`:** all seven pilot commands completed in ≈100 s single-core. Headline values reproduce exactly: L32/Tc |m| median ESS 23.88 and minimum 4.16, prospective gate `False`; exploratory log–log slopes at Tc −0.1224 (|m|) and 1.7141 (χ_abs); 1D control Binder at the 2D Tc 0.419 / 0.177 / 0.110 / 0.029 for L = 8 / 16 / 24 / 32. The burn-in re-run output does not match the registered artifact SHA-256 byte-for-byte (cause not determinable without the artifact; all compared statistics agree to the reported precision).

**Evidence levels after integration:** exact Tc and exponents are *known theory*; slopes, ESS and Binder values are *numerical observations*; agreement of slopes with β/ν = 1/8 and γ/ν = 7/4 is *not* a validated exponent measurement; the NO-GO is a *methodological decision* about tool readiness, not a physics result. No theorem is claimed.

## Interrupted-session recovery protocol (2026-10-10)
- Added an explicit recovery audit to `docs/RESEARCH_LOCK.md` and the `docs/WORKFLOW_POLICY.md` Director cycle. After acquiring a new lease, a Director responding to an interrupted run checks relevant PR/branch heads, unfinished GitHub Actions jobs, logs, artifacts and partially integrated results **before** launching duplicate work.
- An `idle` lease is not proof a ChatGPT session or GitHub Actions experiment finished; an expired lease cannot stop external jobs. Missing run status/artifacts remain unknown, not successes. Findings go to existing PR/issue or research-state handoff, avoiding extra feature PRs.
- Integration: process-only documentation commits `e744d093d2dedcd816c0ab8129f1796e68dcfc04` and `69206ab0c42f11b9035a35189f49448bf29ad58e`. No scientific experiment, CI run, deployment or new liveness-monitor service was performed.

## Director integration session (2026-10-10, lease `rd-claude-20261010T064854Z-cf5a9c`)

**Question:** Which open PRs satisfy the objective merge gates, and do their scientific claims survive a later-pass check?

**Recovery audit:** previous lease released cleanly by `rd-recovery-dp1wi9k080g`; no queued or running workflow; `main` green at `e16d6643`. Nothing incomplete found besides stale "proposed" labels in this file (now corrected).

**Integrated (all with expected-head-SHA guard, exact-head CI success, review comment on the PR):**

| PR | Content | Merge commit | Review decision |
| --- | --- | --- | --- |
| #10 | paired burn-in sensitivity (+ added pairing tests, caveat fix, paired analysis) | `171bab66e33d9f93178d8f496fa795be56b82b5a` | PASS |
| #12 | Phase-0 audit, null controls, L32 ESS failure, CLI/stat fixes, NO-GO | `132369e96ed8ed5a4749704ca62ed69cf874dea0` | PASS |
| #5 | representation-neutral strategy (+ citation correction) | `0b2833399f0edd582ee0ae40fcbcca60c49e352b` | PASS |
| #11 | Pilot A preregistration (not executed) | `75b9def47d4ecec4713fadf4a5af4d6b8ee3dafc` | PASS |
| #8 | literature review for Issue #6 | `eaff96605678eb9cb86aa1569bc0fa912f74f4f7` | PASS |

No research PRs remain open. Reviews are AI-mediated later-pass checks, not independent external review.

**Actually executed in this session (local, Python 3.13.16 / NumPy 2.5.3, single core):** full pytest (57 passed on `main`); full re-execution of the burn-in experiment (≈62 s) and all seven Phase-0 pilot commands (≈100 s). No GitHub-hosted experiment was dispatched, nothing ran on Lightsail.

**Evidence, by level**
- *Known mathematics / theory (not ours):* exact Tc and Ising exponents; d'Alembert, heat-kernel and quantum-walk reference solutions used in Pilot A (numerically re-evaluated for the registered far-witnesses).
- *Numerical observations (reproduced):* burn-in coverage table (24/24 counts identical); L32/Tc |m| median ESS 23.88, min 4.16, gate failed; Tc log–log slopes −0.1224 (|m|) and 1.7141 (χ_abs); 1D-null Binder 0.419 → 0.029 (L8 → L32).
- *Numerical observations (new, post hoc, exploratory):* zero burn-in biases T=1.5 means (|M| −0.0032 ± 0.0005, p = 0.00014); paired 0→100 shifts at T=1.5 and 2.269 survive Bonferroni; binary coverage counts did not detect this. Details: [experimental note](experiments/2026-10-10-burnin-paired-analysis.md).
- *Hypotheses / open anomalies:* burn-1600 energy offset at T=1.5 (+0.0033 ± 0.0009, p = 0.005, not surviving correction) is unexplained and not interpreted; whether the slopes reflect true exponents is untested.
- *Proofs:* none produced. The Lean statement in Pilot A is a specification only.
- *Methodological decision:* Phase-0 NO-GO stands.

**Limitations and honest gaps**
- GitHub Actions artifacts could not be downloaded from the review environment (egress policy). Registered SHA-256 digests were therefore not verified directly; a local burn-in re-run does not match its registered digest byte-for-byte although all compared statistics agree (likely floating-point ULP differences; not confirmed).
- Literature references were spot-checked, not exhaustively resolved; one misattribution was corrected (Plávala, PR #5); one link (PMC) was unverifiable behind a CAPTCHA.
- Every push to `coordination/research-lock` triggers the full CI workflow (observed runs on lease commits). Harmless but wasteful; restricting the workflow's push trigger is a proposed, unimplemented change.

**Deployment status:** unchanged; no deployment performed or requested.

**Open blockers:** L32 critical-mixing gate (scientific); deployment decision for merged code (operational, needs separate review).

**Next single informative step:** preregister the L32 critical-mixing holdout (priority 1 above).

## Director session: L32 critical-mixing gate (2026-10-10, lease `rd-claude-20261010T073142Z-d6f71d`)

**Question:** With separated warmup, longer chains and modern diagnostics, are checkerboard-Metropolis estimates and their uncertainty statements trustworthy at L = 32, T = 2.269185 (the Phase-0 blocker)?

**Recovery audit:** previous lease released cleanly by `rd-claude-20261010T064854Z-cf5a9c`; no open PRs, no queued/running workflows; `main` green at `da3e900`. Nothing incomplete.

**Integrated (expected-head-SHA guard, exact-head CI success, review comment on the PR):**

| PR | Content | Merge commit | Review decision |
| --- | --- | --- | --- |
| #14 | lock branch holds only `lease.json`; `push.branches-ignore` for it | `20603ea80a2ba89e4390f7fc58a5db6f27c22288` | PASS |
| #13 | L32 gate: preregistration, exact finite-L energy, rank-normalized diagnostics, holdout result | `effba3e9d9ad68956623a6f21f9f14ca93f2bf23` | PASS |

Reviews are AI-mediated self-reviews by the producing session, not independent review; a later-pass challenge of PR #13 by another session is invited.

**Design:** preregistration committed in `ab67cdc` **before** any holdout draw; 32 chains (16 random, 16 ordered starts), seeds 2028010001–016 / 2028011001–016, 5,000 warmup + 40,000 sampling sweeps, thinning 4; 1.47·10⁹ attempted flips. Criteria G1–G6 (R̂ < 1.01; bulk/tail ESS ≥ 400; per-chain ESS ≥ 100; hot/cold |z| ≤ 3; pooled E vs exact |z| ≤ 3 with CI containment; ≥ 27/32 per-chain intervals covering exact E) plus a prespecified power control (first 1,800 sweeps must fail G3). Disclosed sizing pilot on disjoint seeds chose only the run length.

**Actually executed:** local, Python 3.13.16 / NumPy 2.5.3, 2 processes, 78 s; and on GitHub's runner ([run 38035618292](https://github.com/shaden7/emergence-lab/actions/runs/38035618292), Python 3.12.15 / NumPy 2.5.3). Raw data SHA-256 `57ae4ea037e7f16402d3f0f41645f8f357cd4b09ab11c76648338a9b75bf47a2` **identical in both**. Full tests: 107 passed locally; CI green on every pushed head.

**Evidence, by level**
- *Known mathematics (not ours):* Kaufman's exact finite-torus partition function; E₃₂(2.269185) = −1.4336590464244536. Our implementation agrees with enumeration and transfer matrix to ≈ 1e-13.
- *Numerical observations:* **gate PASS on all ten checks** — E pooled −1.43386 ± 0.00045 (z = −0.46 vs exact), 30/32 per-chain intervals cover exact E, max R̂ 1.0007 (E) / 1.0014 (|m|), min per-chain ESS 718 (E) / 284 (|m|) of 10,000 draws, hot−cold z −0.76 / 0.64. Median per-chain τ ≈ 36 sweeps (E), ≈ 85 sweeps (|m|) in the 1 + 2Σρ convention. Power control **failed G3 and G1 as prespecified** (min ESS 26.8 / 8.3; R̂ 1.017 / 1.032), so the PR #12 short-window design is again shown to be inadequate on fresh seeds; its heuristic τ_int ≈ 19 sweeps for |m| is about half the τ_int ≈ 42 sweeps measured here. G5/G6 also passed on the short window, so energy coverage alone would not have caught it.
- *Hypotheses:* none new; whether other L/T and the random-site sampler behave similarly is untested.
- *Proofs:* none.
- *Methodological decision:* L32/Tc mixing blocker cleared for this sampler/budget; **Phase-0 NO-GO stands** pending report gates 4, 5, 6 and the burn-in replication.

**Process findings**
- Root cause of CI runs on every lease commit: push workflows are read from the pushed commit, and the lock branch carried a stale copy of `ci.yml` (lease-only commit `5d61fa7` triggered no run; full-tree commits did). Fixed by PR #14; the release commit of this session prunes the lock tree to `lease.json`.
- Disclosure: this session's acquire commit `5d61fa7` unintentionally used a lease-only tree (deviation from step 4 as then written); the next heartbeat restored the full tree. CAS ownership was unaffected.
- The review integration cannot dispatch workflows (HTTP 403) or read job logs/artifacts (blob storage blocked). Check annotations via the REST API are a working evidence channel and are now emitted by the gate step.

**Deployment status:** unchanged; nothing deployed, nothing run on Lightsail, no paid APIs.

**Open blockers:** report gates 4/5/6 and burn-in replication (scientific); artifact archival location (operational, needs a reviewed decision); deployment decision for merged code (operational).

**Next single informative step:** preregister the burn-in replication (priority 1 above) — or, if a session prefers the larger lever, the many-batch coverage study, now possible at L ≥ 8 thanks to the exact finite-L energy.


## Director session: PR #13 later-pass review and burn-in replication (2026-10-10, lease `rd-claude-20261010T081233Z-2bca3d`)

**Questions:** (1) Does the L32 critical-mixing gate (PR #13, self-reviewed by its producer) survive a second session's challenge? (2) Do the post hoc burn-in findings of the PR #10 analysis replicate on fresh seeds (report priority 1)?

**Recovery audit:** previous lease released cleanly by `rd-claude-20261010T073142Z-d6f71d` (lock tree pruned to `lease.json`); no open PRs; no queued/running workflows; `main` green at `06705ef`. Nothing incomplete. Lease commits of this session triggered no CI run (PR #14 fix confirmed in practice).

**Integrated (expected-head-SHA guard, exact-head CI success, review comment on the PR):**

| PR | Content | Merge commit | Review decision |
| --- | --- | --- | --- |
| #15 | later-pass review of #13; independent Wolff cross-check | `ba78b24bc594d5452fb60eb431a5ae8f13eaf1eb` | PASS (also recorded on #13 as "PASS confirmed") |
| #16 | preregistered fresh-seed burn-in replication | `5e52ff17b35a3b80f532f0eac853c052711c0d05` | PASS |

Reviews are AI-mediated; #15 is a second-session review of #13, #16 is a producer self-review (a later-pass challenge is invited).

**Actually executed:** full pytest (120 passed, Python 3.13.16 / NumPy 2.5.3); L32 gate re-run (raw `.npz` SHA-256 `57ae4ea0…` byte-identical, third execution); Wolff cross-check (16 chains, 188 s); burn-in replication locally (50 s) and twice on the GitHub runner ([38037948647](https://github.com/shaden7/emergence-lab/actions/runs/38037948647) on the preregistration commit `ad3bc54`, [38038206636](https://github.com/shaden7/emergence-lab/actions/runs/38038206636)). Nothing ran on Lightsail.

**Evidence, by level**
- *Known mathematics (not ours):* Kaufman's finite-torus partition function, now also checked against an independent transfer matrix on 32 × 6/9/10 tori (≤ 1.8e-12) and Z(M,N) = Z(N,M); exact 4 × 4 enumeration.
- *Numerical observations:*
  - L32/Tc, independent Wolff sampler vs checkerboard gate: E −1.433404 ± 0.000284 vs −1.433862 ± 0.000446 (z +0.87; Wolff vs exact z +0.90); |m| 0.653710 ± 0.000439 vs 0.655549 ± 0.001235 (z −1.40). Rule |z| ≤ 3 fixed before the run. [Review record](experiments/2026-10-10-l32-gate-later-pass-review.md).
  - Burn-in replication (20 batches, seeds 2029061001–160, Bonferroni α = 0.00714): **replicated** P1 zero-burn |M| bias at T = 1.5 (−0.00381 ± 0.00049), P2 energy bias (+0.00826 ± 0.00134), P3/P4 paired 0 → 100 shifts at T = 1.5 (E −0.00840 ± 0.00089, |M| +0.00381 ± 0.00036). **Not replicated:** P5/P6 shifts at Tc (−0.00619 ± 0.00296, p = 0.050; +0.00368 ± 0.00135, p = 0.013 — same direction, below threshold); P7 burn-1600 energy anomaly (+0.00017 ± 0.00144; marginal, CI upper +0.00319 vs original +0.0033). [Result note](experiments/2026-10-10-burnin-replication.md).
  - Byte-level reproduction localized: Monte-Carlo output identical local vs runner; only exact-enumeration reference floats differ at ULP level.
- *Hypotheses:* a burn-in bias of order 0.005 at Tc on 4 × 4 (unresolved, not refuted); the earlier unexplained burn-in byte mismatch has the same reference-float cause (plausible, not verified).
- *Proofs:* none.
- *Methodological decision:* report priority 1 completed; **Phase-0 NO-GO stands** (coverage gate 4, finite-size gate 5, archival gate 6 open).

**Limitations / counterarguments:** all reviews by the same model family; prospective power for P5–P7 was overestimated (scaled from noisy 10-batch SEs) — the replication SEs were 1.6–2.3× larger than predicted; 4 × 4 burn-in facts do not transfer to larger L; Wolff and checkerboard share lattice conventions and the PCG64 generator.

**Deployment status:** unchanged; nothing deployed, no Lightsail runs, no paid APIs, EatSleepFeel untouched.

**Open blockers:** coverage gate 4 and finite-size gate 5 (scientific); artifact archival location (operational, needs a reviewed decision); deployment of merged code (operational, separate reviewed decision).

**Next single informative step:** preregister the many-batch coverage study (gate 4) at L = 16 and 32 near Tc using the exact finite-L energy, sized from the measured τ and with a pilot-variance allowance (lesson from P5–P7).

## Director session: many-batch coverage gate, report gate 4 (2026-10-10, lease `rd-claude-20261010T085643Z-4977d0`)

**Question:** do the project's nominal 95 % 4-chain Student-t intervals for the energy per spin cover the exact finite-torus value at close to the nominal rate at L = 16 and 32, T = 2.269185 (report gate 4)?

**Recovery audit:** previous lease released cleanly by `rd-claude-20261010T081233Z-2bca3d`; no open PRs; no queued/running workflows; `main` green at `8b8bef4`. Nothing incomplete.

**Work (PR #17, merged as `8954b3de870a7134553a8bb44b5302c2dd05ae47` with expected-head guard `378d386`; review record on the PR):** preregistration, config, runner and tests committed first (`8440df2`), then the holdout simulated locally (3,200 chains, 8.19e9 flips, ≈ 690 s on 2 workers, Python 3.13.16 / NumPy 2.5.3). Two disclosed analysis-only deviations (SciPy import removed; JSON serialization fix with re-analysis of the saved `.npz`; six chains re-simulated bit-identically). PR #17. Runner execution not possible (`workflow_dispatch` 403). Nothing on Lightsail.

**Evidence, by level**
- *Known mathematics (not ours):* Kaufman/Beale exact finite-torus energy (references E₁₆, E₃₂).
- *Numerical observations* ([result note](experiments/2026-10-10-coverage-gate.md)): coverage 379/400 (L16, Wilson [0.921, 0.965]) and 381/400 (L32, [0.927, 0.969]) → **gate 4 PASS** by the preregistered rule; pooled energy bias z = +0.40 / −1.39 (resolution ≈ 3e-4); power control (first 40 sweeps, no warmup) 314/400 and 48/400, failing as predicted; per-chain Geyer-ESS intervals 0.951 (L16) but **0.903 [0.888, 0.917] at L32** (750 draws).
- *Hypotheses:* Geyer τ is underestimated for some short chains near Tc at L32 (untested).
- *Proofs:* none.
- *Methodological decision:* report gate 4 met for E at this scope; **Phase-0 NO-GO stands** (gates 5 and 6 open).

**Limitations:** energy-only reference; one T, one sampler, random starts; one execution environment; self-review by the producing session (later-pass challenge invited); raw `.npz` not archived.

**Next single informative step:** preregister the finite-size gate 5 study (see Next priority 1).

## Director session: finite-size gate, report gate 5 (2026-10-10, lease `rd-claude-20261010T095628Z-d3ba3e`)

**Question:** does the sampler-plus-analysis pipeline at L = 8…48, T ≈ Tc reproduce exact finite-torus energy and specific heat, recover the known exponents β/ν, γ/ν, 1/ν to a stated accuracy stable across fit windows, and reject non-critical controls by the same rule (report gate 5)?

**Recovery audit:** previous lease released cleanly by `rd-claude-20261010T085643Z-4977d0`; no open PRs; `main` green at `71dce9b`. One `workflow_dispatch` run on the merged PR #17 head (`378d386`), started 09:53 UTC after that release (owner-triggered; Directors get 403), was in progress and was left alone; it completed **success** and reproduced the gate-4 `.npz` digest byte-identically (see Next priority). Nothing incomplete.

**Work (PR #18):** preregistration, config, runner, tests and a manual-dispatch CI step committed first (`7005c0f`); a seed collision between the main L48 and off-critical L8 blocks was caught by the new test **before** that commit and fixed. Holdout run locally (Python 3.13.16 / NumPy 2.5.3, 2 workers, 713 s, 5.69e9 flips); no deviations. Runner execution not possible (`workflow_dispatch` 403). Nothing on Lightsail.

**Evidence, by level**
- *Known mathematics (not ours):* exact 2D Ising exponents; Kaufman finite-torus energy and its numerical T-derivative; U* = 0.61069 (Salas & Sokal 2000, cited).
- *Numerical observations* ([result note](experiments/2026-10-10-finite-size-gate.md), raw `.npz` SHA-256 `b18423a20e428583a493e45ff24146a5b0dd5592c6b8654772aecd8914cc2287`): **gate 5 PASS, 65/65 checks.** Primary window {12…48}: β/ν = 0.1256 ± 0.0021, γ/ν = 1.7499 ± 0.0030, 1/ν = 1.061 ± 0.011. β/ν and γ/ν within |z| ≤ 2.4 of the exact values without tolerance in all five windows; **1/ν is 1.04–1.08, significantly above 1 (z up to 9.9) and passes only through δ = 0.08**, the excess shrinking with L_min. Energy and specific heat vs exact at every L within |z| ≤ 1.35; max R̂ 1.0021; min ESS 8,291; hot/cold |z| ≤ 0.90; τ₄₈(|m|) ≈ 197 sweeps. Controls T = 2.6 and J = 0 give β/ν ≈ 1.0, γ/ν ≈ 0.13 / 0.01 and are rejected. Binder U(48) = 0.6101 ± 0.0014.
- *Hypotheses:* the 1/ν excess is a correction-to-scaling effect of the ∂ln⟨|m|⟩/∂K estimator (untested).
- *Proofs:* none.
- *Methodological decision:* report gate 5 met at the preregistered accuracy; **Phase-0 NO-GO stands** (gate 6 open).

**Limitations:** fits without correction terms; one sampler, T and lattice; one execution environment; self-review by the producing session (later-pass challenge invited); raw `.npz` not archived.

**Deployment status:** unchanged; nothing deployed, no Lightsail runs, no paid APIs, EatSleepFeel untouched.

**Next single informative step:** decide and implement the raw-artifact archive (report gate 6, Next priority 1) as a reviewed change, then write the Phase-0 GO/NO-GO decision record.

