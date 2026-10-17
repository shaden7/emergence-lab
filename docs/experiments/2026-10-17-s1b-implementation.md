# S1b v0.2 implementation: locked, awaiting later-pass review

This implements the design integrated in PR #48 (`4614500`). **No S1b graph,
source or bootstrap seeds have been drawn. No S1b/S2 run is authorized.**
All engineering results are instrument tests, not spectral calibration results.

## Implemented behavior

- `spectral_s1b.design` validates the fixed allocation, sizes, kernel, window,
  thresholds and budget; `schedule` produces 168 unique seed tuples in
  replicate-major, then family/size-list order. It draws nothing.
- `spectral_s1.build_instance` rejects the S1b seed base before creating an RNG.
  `S1B_RUN_AUTHORIZED=False` cannot be overridden by environment flags. The S1b
  analysis entry also checks authorization before the frozen bootstrap seed.
  Activation requires a later reviewed code change and explicit run authorization.
- Engineering uses graph base `2036101797` and bootstrap base `2036101798` on
  small instances, separate from S1b `2036101701` / `2036101799` and S1 bases.
- S1 generators/kernel/source mapping are reused unchanged: graph RNG from the
  parent SeedSequence, source RNG from `ss.spawn(1)[0]`, sorted uniform sources
  without replacement. No ladder, seed replacement, pilot pooling or resume.
- Every attempt is fsynced **before** graph generation. Numeric source rows,
  source timing/bound records and completion/failure events are checkpointed.
  Existing output directories are refused. A STARTED attempt without a terminal
  event is consumed and incomplete, never permission to repeat that seed.
- All required trees and sources at every size are required. Duplicate/missing/
  censored source records block the family; the descriptive CAY 2^14 cohort is
  mandatory too. Failed P0 controls or global budget block both families;
  a family stop blocks that family. Completed other-family data remain descriptive.
- P3 influence skew/share and positive finite means, certification, monotonicity,
  per-source >=10x headroom and delete-one-tree jackknife/delta SE <=1.25 are
  checked **per size**. The larger-minus-smaller contrast uses the inherited
  tree-level delta/Welch interval and the strict disjoint v0.2 verdict rules.
  The independent-size whole-tree bootstrap reports a descriptive 90% percentile
  contrast interval, with the fixed stream restarted for each family; it never
  changes cutoffs. All S1-compatible windows, q(1) and leaf fraction are descriptive.
- The global CPU counter includes completed P0 subprocesses and analysis; family
  counters include generation, source work and analysis. Projection-based family
  ceilings are fixed at CAY 157.5 and UST 34.5 CPU-min, not refitted on new results.
  Final-tree and analysis overruns veto verdicts. Engineering cannot unlock S2.

## Resource boundary and run entry (still locked)

`scripts/run-s1b-contained.sh` requires an immutable image ID, clean reviewed
checkout and new absolute output directory. It mounts that checkout read-only,
uses its source and Git revision, removes network access/capabilities, sets a
one-core quota, 2 GiB memory with zero extra swap, bounded PIDs/tmpfs and one
thread per numerical library. It must be used on a verified **non-Lightsail**
host; the host-class environment value is an operator attestation, not remotely
verified hardware provenance. This PR does not build/deploy on Lightsail.

The Linux cgroup-v2 guard checks actual quota/memory/swap/interface settings and
rejects absent/unbounded accounting. An isolated process-group watchdog reads
cumulative cgroup CPU (including children and analysis), polling every 50 ms and
stopping at a two-CPU-second reserve before the 200-CPU-min total. The kernel
enforces CPU *rate* and memory; the cumulative CPU stop is a watchdog, **not a
mathematically exact kernel CPU-total limit**. Scheduling/GIL delays and forced
termination are risks to challenge in later review. The reserve is conservative,
not a proven worst-case latency bound. A separate native `timeout` process also
kills the worker after 11,998 wall seconds (118 for engineering), independent of
the Python GIL; the <=one-core quota makes this a conservative additional stop.
This can terminate an I/O-delayed run before its CPU budget, yielding partial
evidence only. There is no automatic budget extension.

A full result is invalid without `resource_evidence.json` with a clean exit,
within-budget accounting and no `resource_stop.json`; a killed run can leave an
earlier report/checkpoint and must never be accepted from that report alone.
The completion evidence is emitted after report/manifest writes. Loss of its
counter fails closed. Later review should validate the containment boundary and
its behavior on abnormal exits before activation, including OOM/forced stops.

## Validation and limits

The test suite covers config drift, scheduling, seed lock through public/lower
entry points, the no-seed reference interval grid, synthetic positive/negative/
equivalent/inconclusive contrasts, per-size reliability, incomplete/duplicate/
OVER_CAP rows, control failure before generation, durable attempted-seed logging,
final-tree budget stops, deterministic numeric CSV and cgroup refusal/watchdog
logic. CI additionally runs a real network-disabled, CPU/memory-capped Docker
**engineering** smoke; its outputs cannot authorize S1b or S2. The normal full
CI suite and inherited S1 P0 engineering steps remain required on the final head.

Local Windows development tests require an import-only stub for the pre-existing
Linux `resource` import in `dimension_d1`; the S1b numerical tests do not use that
stub for measurements. This is not Linux resource validation. Final test counts,
exact-head CI and review findings are recorded in the PR/research-state handoff.

Nominal Welch/TOST coverage remains uncalibrated for heavy tails and completion/
reliability selection; bootstrap agreement is not proof of coverage. No new
physical claim or theorem. The next action is a distinct later-pass implementation
review, including adversarial resource/provenance checks; keep seeds locked.
