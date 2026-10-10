# Pilot B stage 2: once-only blind-run workflow (implementation, not run)

**Status:** implemented on a PR branch; **not dispatched, and not dispatchable before 2026-10-11T21:10:00Z**. No blind key exists. No Pilot B blind output exists. Author session `rd-claude-20261010T215634Z-08323a` (producer self-review only).
**Prereg:** [v1.0-r1](../PILOT_B_BLINDED_INTERVENTION_PREREGISTRATION.md) §6.3–6.4, §8 B-G6, §11.3. Stage 1: [note](2026-10-10-pilot-b-stage1-dev.md), merge commit `7780fc1` (committer time 2026-10-10T21:09:59Z).

## What was added

- `src/emergence_lab/pilot_b_blind.py`: guards only, no analysis. It pins these values and checks them on the executing commit:
  - the stage-1 merge commit and time. R is **recomputed** from the merge time and must equal the pinned R = 32983212 (round time 1791753000 = 2026-10-11T21:10:00Z).
  - Git blob SHAs of `pilot_b.py`, `pilot_b_analyst.py`, `pilot_b_beacon.py`, `configs/pilot_b.json` and the prereg, all as of `7780fc1`. Any edit to the frozen rule blocks the run.
  - the development decision digest `6da5c8e3…`, recomputed in the workflow before the beacon is fetched.
  - wall clock ≥ R's timestamp + 60 s before any relay is asked for R.
  - the beacon: round = R, chain hash = quicknet, and SHA-256(signature) = randomness plus BLS **re-verified locally**. A stored `signature_verified` flag is not trusted.

  `execute` then calls the frozen `pilot_b.run("blind", …)` unchanged and writes `blind_archive_manifest.json` (beacon, key, commits, blobs, gate outcomes, file hashes). It exits 0 whenever the evaluation completed, **including when a B-gate fails**, because §8 requires a failure to be published, not rerun.
- `.github/workflows/pilot-b-blind-run.yml`: `workflow_dispatch` only, job restricted to `refs/heads/main`, NumPy pinned to 2.5.3. Step order:
  1. **Once-only guard:** fail if release `pilot-b-blind-v1` exists.
  2. Preflight.
  3. Dev digest.
  4. Fetch and verify R.
  5. Blind evaluation.
  6. 90-day run artifact.
  7. Release with all outputs.
  8. Re-download and hash check.
- `tests/test_pilot_b_blind.py` (9 tests). It covers the round pin, the frozen-blob guard and its negative case, the time guard boundary, the dev-digest guard, and the beacon guard (wrong round, wrong chain, tampered randomness). It also has an end-to-end `execute` with a **throwaway test BLS key** (not Pilot B evidence) and a static check of the workflow's triggers and step order.

## Actually executed (local sandbox, Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1)

- `pytest -q`: 244 passed (235 before + 9 new).
- `python -m emergence_lab.pilot_b_blind preflight` at 2026-10-10T21:59Z: **FAIL CLOSED: too early** (exit 2), as intended.
- `round-for-merge 2026-10-10T21:09:59Z` → R = 32983212, matching the value recorded on PR #30.
- Not executed: the workflow itself (it can only be dispatched from `main` after merge, and its preflight blocks until R); any beacon fetch (the sandbox cannot reach drand).

## Limitations and residual risks (stated, not hidden)

- **Once-only is enforced by the release tag, which is cooperative.** If the job fails *after* the evaluation but before the release is created, no tag exists. A redispatch then recomputes the same key from the same R. This is the permitted "retry on the same R": the decisions are deterministic, and `rows.csv` may differ only in last-bit BLAS rounding. The decision digest is the cross-run comparator. The 90-day run artifact of the first attempt is kept.
- A workflow file edited on another branch could be dispatched from that branch; the `refs/heads/main` job condition and the frozen-blob guard only cover the file on `main`. Directors must dispatch from `main`.
- The guards check code identity, not correctness. Correctness was the subject of the stage-1 later-pass review.
- Same AI model family for design, implementation and review (prereg §6.5).

## Next

A later-pass review of this PR by a different Director session, then merge with an expected-head guard. **After 2026-10-11T21:11Z**, dispatch the workflow once from `main` and record the run URL, the release and the gate outcomes, then write the result note and the decision record.
