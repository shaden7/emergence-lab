# C0-v2 rerun authorization — 2026-11-04

Status: authorized only after integration of this record; one bounded supervisor invocation, containing two fresh sequential worker processes. This is deterministic instrument calibration, not a new physics hypothesis test.

## Question, baseline and prior outcome

Does the reviewed C0 tool pass the original deterministic controls, report-contract, exact-source provenance and repeatability requirements within the frozen resource envelope?

The governing design is [DIMENSION_C0_PREREGISTRATION.md](DIMENSION_C0_PREREGISTRATION.md). Tool PR #63 was reviewed at 45d5ed4821888b82365ef6b9986ca7adff4b21c5 and integrated at bec92847ba53fd5b1af13eba1a5cf7f8140e6007. All scientific kernels, thresholds, graphs, radii and times remain unchanged.

Preserve [c0-v1](experiments/c0-v1/manifest.json) and [its adjudication](experiments/2026-11-01-c0-first-run.md) without edits: **INCOMPLETE (provenance)**, regardless of its raw machine PASS. No retroactive acceptance. Development calls in tests and review are disclosed; this is not a blind holdout.

## Versioned changes

Compared with c0-v1, reports add explicit independently checked CSR topology fields; the worker/supervisor now enforce full required report shape, derived identities and gate/evidence coherence. Source preflight verifies exact HEAD and byte-identical committed files, pins child module resolution, checks supervisor project imports and persists setup failures. See [repair history](experiments/2026-11-02-c0-review.md) and [later-pass PASS](https://github.com/shaden7/emergence-lab/pull/63#issuecomment-6637652537).

This versioned amendment changes the reporting/provenance acceptance implementation, not numerical tolerances. Keep JSON schema field 1 for compatibility with the reviewed worker; identify this execution by c0-v2 artifact directory and this authorization's Git blob/SHA-256. Numerical bytes need only agree between the two v2 invocations, not with v1.

## Frozen experiment and falsification

Models: C1024 and 256-square torus are known-dimensional positive controls; C8 and K32 are saturation/insufficient-range nulls. Their geometry, locality, clock and dimension are inputs. No random trees, cross-family emergence inference or radius/time mapping.

Observables: actual BFS balls and volume log-ratios at radii 4/8/16 (doubled endpoint 32); graph return probabilities q(2t) at half-times 8/16/32/64/128/256; spectral log-ratios at half-times through 128. Compare with the preregistered explicit integer ball formulas and finite-graph return oracles. Infinite-lattice offsets remain descriptive.

All G0–G4 conditions of the original preregistration remain binding, including exact topology/budget checks, zero integer count discrepancy, volume slope tolerance 1e-12, return absolute/relative tolerances 1e-12/1e-9, spectral residual 1e-9, primary headroom 10 (sensitivity 5 and 20), null within-1% stationary floors and final slope magnitude <=0.02, and byte-identical v2 outputs. Saturated nulls cannot support a zero-dimensional claim.

There is no stochastic sampling error or fitted parameter here; RNG is unused. Numerical discrepancy, finite-radius/time offsets and saturation guards quantify the relevant limitations. Passing does not resolve finite-size stability of random-tree spectral estimates or Issue #37.

## Execution, provenance and budget

Execute only from a clean exact checkout of the integrated authorization revision, with all tracked blob hashes checked. Before launching, record exact execution commit and this document's SHA-256. Use:

`PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 python -m emergence_lab.c0_supervisor --commit <exact-HEAD> --output <new-c0-v2-directory>`

Linux local session only; no Lightsail, deployment, external service or paid API. Unchanged total envelope: 300 CPU seconds, 600 wall seconds, 512 MiB address space per process, 5 MiB combined output, one thread, two fresh sequential workers. Use the reviewed supervisor; do not raise limits on failure.

Store both output files, stderr (including empty files), raw manifest, and a separate authorization record with execution commit, authorization blob/SHA-256, reviewed tool commit and environment. Preserve all failed/partial output. Commit retrievable artifacts and final adjudication via a reviewed result PR.

FAIL takes precedence for an observed gate failure; otherwise missing provenance, incomplete output, a resource stop or absent repetition is INCOMPLETE. PASS requires all checks, provenance and resource observations plus both equal outputs. No automatic retry or in-place output overwrite. Any additional execution requires a new versioned authorization retaining this outcome.

## Review and remaining limits

AI-mediated nonindependent authorization review: PASS for a deterministic rerun with unchanged scientific decision rules and repaired provenance/reporting. The later-pass implementation review used 493 passing tests, 4 optional skips, 65 subtests and 36 separately calculated integer walk/ball checks. No claim of external peer review.

The report validator is not an authenticity verifier: a wholly fabricated internally consistent report can evade it. Exact-source checks and independently calculated references supply separate evidence. Third-party dependencies are version-recorded rather than fully byte-hashed. This authorization has no experimental result yet.
