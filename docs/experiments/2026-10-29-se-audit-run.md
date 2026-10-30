# SE audit v0.1 once-only run: admissible; SE-NOT-REJECTED at N = 2¹⁴ (proposed record)

**Status: PROPOSED record, not yet integrated.** The run was executed by the dispatch-only
workflow. This file is the step-4 later-pass audit of its archived evidence by Director
`rd-claude-20261030T0804Z-54724eff`, a session separate from every producer of the SE-audit
design, code and authorization. It is AI-mediated, not external peer review. The interpretive
text below needs its own later-pass review before merge.
**Issue:** [#37](https://github.com/shaden7/emergence-lab/issues/37). **Protocol:**
[SPECTRAL_SE_AUDIT_PREREGISTRATION.md](../SPECTRAL_SE_AUDIT_PREREGISTRATION.md) v0.1, run record
[SE_AUDIT_RUN_AUTHORIZATION.md](../SE_AUDIT_RUN_AUTHORIZATION.md).
Instrument diagnosis only: no statement about dimensional reduction, emergent geometry or spacetime.

## Provenance (direct observations)

- **Dispatch:** [run 40945734466](https://github.com/shaden7/emergence-lab/actions/runs/40945734466),
  `workflow_dispatch` by the repository owner on `main`, attempt 1, 2026-10-29 20:04:23Z–21:36:21Z,
  conclusion **success**. Every step (guard, full pytest, image build, marker, contained run,
  package, artifact upload, release archive, admissibility) is `success`. It is the only run of
  `se-audit-run.yml`.
- **Commit:** `14659460d3ad613455be4bfb27c8061d5f95ce94` (= `main` at dispatch and at this audit).
  Image `sha256:4ffda72e…0ada15`. Host: GitHub-hosted `ubuntu24` image 20261026.354.1, AMD EPYC 7763,
  `nproc=1` inside the container; cgroup `cpu.max 100000/100000`, `memory.max` 2 GiB,
  `memory.swap.max 0`, interfaces `lo` only. Not Lightsail.
- **Once-only marker:** release [`se-audit-run-v1`](https://github.com/shaden7/emergence-lab/releases/tag/se-audit-run-v1),
  published 20:06:27Z; its body binds this run URL, commit and image. (The API `created_at`
  2026-10-28T08:11:30Z is the date of the tagged commit, not the release.)
- **Evidence asset:** `se_audit_run_evidence.tar.gz` (1,144,509 bytes), sha256
  `63d8b42a9c60861017c67317022e8a31b4d2119dfd0d770b07acc120354453de`. Re-downloaded over REST in
  this session; the hash equals the archived `.sha256` asset. Workflow artifact 12934114553 is also retained (90 days).
- **Hashes vs `main` `1465946`:** the manifest's `prereg_sha256` (`977275bf…`), `config_sha256`
  (`93f38904…`) and all six `source_sha256` entries equal the files on `main`. All five
  `outputs` hashes match the extracted files.

## Admissibility (record § 4), every item directly observed

Exit code 0; `clean_exit` true; `watchdog_failure` null; no `resource_stop.json`; `mode = se_audit`;
`run_status = FINISHED`; 192/192 seed tuples attempted = planned, all at base 2036101901;
`attempts.jsonl` has 192 STARTED and 192 COMPLETED entries; `s2_run_authorized` false;
P0a–P0d pass. `n_complete_trees` 192, no invalid or stray trees, all 6144 source rows `OK`
with 32 distinct sources per tree. **Result: admissible.**

**Budget (observation, flagged):** 5,383.5 CPU-s = **89.7 CPU-min** of the 100 CPU-min hard stop,
against a preregistered projection of ≈ 53. Mean per-tree cost was 27.8 CPU-s (max 39.2) vs the
projected ≈ 16. The margin to the stop was only 1.11×. The run did not hit the stop, so this
does not affect admissibility; it does affect any follow-up budget (see below).

## Result under the frozen rule (independently recomputed)

[`se_audit_run_recheck.py`](se_audit_run_recheck.py) (no `emergence_lab` import) reads only the
source-level `numeric.csv`, rebuilds the per-tree means, batches, annealed slopes and tree-level
delta SEs, and reproduces the report to ≤ 1.4 × 10⁻¹⁵ (Python 3.13.18, NumPy 2.5.3, SciPy 1.18.1).

| Quantity | Value |
| --- | ---: |
| sd_b(d̂_b), 16 batches | 0.01606 |
| RMS SE_b | 0.02289 |
| **R** | **0.7017** |
| frozen threshold (exact √F₀.₉₅(15,176) = 1.31284) | 1.313 |
| P(F(15,176) ≥ R²) | 0.942 |

**Classification: SE-NOT-REJECTED.** In the preregistered wording: *the tree-level delta SE model
of the annealed CAY W = 128–1024 slope is not rejected at N = 2¹⁴*. It is not "validated", and
2¹⁶–2¹⁸ are uncertified. R is far from the threshold, so the 1.313-vs-1.31284 literal is immaterial.

**Descriptive outputs (prereg § 2, not decision inputs; numerical observations):**
- Pooled per-tree ψ SD 0.07929 (176 df), 90 % CI [0.07295, 0.08696].
- CV(SE_b) 0.151 (normal-theory reference ≈ 0.21; synthetic heavy-tail scenarios 0.33–0.62).
- All-tree annealed slope 1.3056, delta SE 0.00564, jackknife/delta ratio 1.0002.
- Per-tree Q(128): CV 0.124, skew 0.33, excess kurtosis 0.08. Q(1024): CV 0.134, skew 0.52, excess kurtosis 0.11. corr(ln Q(128), ln Q(1024)) 0.81.
- QQ of standardized batch deviations: correlation 0.991 with normal quantiles.

## Interpretation (hypotheses, clearly separated from the above)

- The between-batch spread is, if anything, **smaller** than the delta SE predicts (R = 0.70).
  Post hoc and outside the one-sided rule: P(F ≤ R²) = 0.058. That is not significant at a
  two-sided 5 % level and is not a finding. Possible readings are chance, a mildly conservative
  SE, or an unmodelled negative between-batch dependence; this audit cannot tell them apart.
  It is recorded so that later work does not read the result as "SE exact".
- Together with the near-normal per-tree shape and CV ≈ 0.13, consistent with S1b, the result
  makes reading (c) "SE misstatement" of the S1 decision record **less likely at 2¹⁴**. It makes
  reading (a), a chance pilot SE underestimate, the leading but **unproved** explanation of the
  1.64× S1b/pilot SE ratio. It does not discriminate (a) from (b) and does not test (d).
- R is blind to defects shared by all trees (prereg § 5). The all-tree slope 1.3056 is
  **not** compared with 4/3 as a calibration verdict.

## Consequences fixed in advance (prereg § 2, decision record § 3)

- Option C (new estimator) is **not triggered** by this audit.
- **Option B**, a symmetric CAY equivalence study using this SE model, **may be separately
  preregistered**. It is not authorized by this record. Its prereg must:
  - use the pooled SD inflated to its 90 % upper CI factor (0.08696 for ψ at 2¹⁴);
  - state the 2¹⁴ → 2¹⁶–2¹⁸ SD transfer as an assumption and disclose that those sizes are uncertified;
  - **re-derive its CPU budget from this run's observed 27.8 CPU-s per 2¹⁴ tree on the hosted
    runner** (1.74× the projection), not from the S1b-derived figure. The ≈ 220 CPU-min
    projection for option B is therefore likely an underestimate.
- No outcome authorizes S2 or changes S1 NO-GO, S1b C-INCONCLUSIVE/U-EQUIVALENT or Phase-0 GO.
  No rerun.

## Evidence level and limitations

- Numerical observation at a nominal F level on one size; instrument diagnosis only.
- This audit is a separate-session, AI-mediated recheck. The recheck reuses the same observable
  definition, so it verifies the arithmetic from the raw source rows, not the kernel.
- No Lightsail, deployment, paid API, new seeds or rerun.
