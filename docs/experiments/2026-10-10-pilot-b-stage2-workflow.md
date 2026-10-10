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

## Later-pass review (2026-10-10, `rd-claude-20261010T225628Z-1ebe46`)

Different session from the producer; same AI model family, so this is not external review.

**Decision on the producer's head `fd6f284`: REVISE (two small workflow-only fixes, applied on this PR).** Nothing frozen was touched: `pilot_b.py`, the analyst, the beacon module, the config and the prereg keep their `7780fc1` blob SHAs (re-checked with `git rev-parse 7780fc1:<path>` against `git hash-object`).

*Checked and found sound:*
1. No step can fetch R before `preflight` passes. Steps run sequentially without `continue-on-error`. Only the artifact upload has `if: always()`, and it uploads nothing secret.
2. A failing B-gate still archives and publishes: `execute` exits 0 after a completed evaluation.
3. `fetch-round` writes only JSON to stdout (`tee` with `pipefail`), and its record carries every field `check_beacon` and the release notes read (`round`, `chain_hash`, `signature`, `randomness`, `signature_verified`, `source_url`). `pilot_b.run("blind")` derives the key from the locally re-verified randomness.
4. `permissions: contents: write` is the minimum for `gh release create`. The job has no other credentials.
5. A redispatch after a post-evaluation failure recomputes the same key from the same R and the same deterministic decisions, so it cannot select a favourable key. This is the "retry on the same R" that the prereg permits.
6. *Simulation:* a scratch script ran `execute` with the tests' throwaway BLS key (not Pilot B evidence). It then ran the workflow's two inline Python blocks, extracted from the YAML, on the outputs. Release notes rendered, and the hash verification passed.

*Findings fixed in this revision:*
- **Once-only guard failed open on API errors.** `gh release view … >/dev/null 2>&1` treats *any* error (403, rate limit, network, missing `gh`) as "release absent". Demonstrated in this sandbox: `gh release view` returns a 403 here, which the old guard would read as "no release". The guard now queries `GET /repos/{repo}/releases/tags/{tag}` and proceeds only on a definite `HTTP 404`. Exercised against the live API:
  - absent tag → proceed;
  - existing tag `phase0-evidence-2026-10-10-v1` → fail;
  - 403 → fail;
  - `gh` missing → fail.
- **B-G6 was not evaluable from the blind run itself.** The prereg requires "development outputs byte-identical on two invocations in the same environment". The workflow ran the dev set once, and in a different NumPy build from CI. It now runs the dev set twice and `cmp`s `rows.csv` and `result.json` before fetching R. Locally, two invocations are byte-identical.
- The static workflow test asserts both properties.

*Local checks (Python 3.13.16 / NumPy 2.5.3):* `pytest -q` 244 passed. `preflight` → FAIL CLOSED "too early" (exit 2).

*Not covered by this revision (stated):* once-only is still cooperative, and dispatch from a non-`main` branch is blocked only by the job condition in the file on that branch. These are unchanged from the producer's list.

Because this reviewer authored the revision, a different session should check this delta (workflow and test only), confirm green CI on the new head, and merge with an expected-head guard **before 2026-10-11T21:10Z**.
