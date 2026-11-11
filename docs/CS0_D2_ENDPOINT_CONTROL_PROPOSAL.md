# D2-E0 — endpoint-conditioned finite-occupancy MM control (reviewed design r3, NOT frozen)

**Current successor:** [frozen v1 contract](CS0_D2_E0_PROTOCOL.md) supersedes this historical design after integration of the freeze/target-gate PR. The dated sections below retain their original status. Execution still requires a separate committed authorization; no target has been evaluated in this change.
Related: [D2-M0 protocol](CS0_D2_M0_PROTOCOL.md), [D2-M0 observed reference](experiments/2026-11-07-d2-m0-run.md), [Issue #37](https://github.com/shaden7/emergence-lab/issues/37).
This is an exact estimator-control at fixed **input D=2**, not a model comparison, physical discovery, or full-CS0 authorization.

## Question and discriminating comparison

Does the small-N apparent MM dimension shift found in D2-M0 persist when two
causally ordered interval endpoints are included by construction, removing
the undefined R=0 selection event? Compare D2-E0 against the **same total N**
from D2-M0; report the different point-generation conventions prominently.
A difference between curves is a finite-occupancy / endpoint-convention
effect, **not** evidence of dynamical dimension change. Do not interpret
a positive or negative shift as a universal claim.

## Model and exact distribution (analytical derivation)

Take an ideal D=2 Minkowski Alexandrov diamond with its minimal and maximal
events included deterministically, and m=N-2 independent continuous uniform
interior events (N>=2). In null coordinates the inner events induce a uniform
permutation of size m. Let I_m be its inversion count, K_m=m(m-1)/2, and
R_inner=K_m-I_m. Every endpoint is related to all other points, and the
endpoints to each other, contributing (N-1)+(N-2)=2N-3 ordered pairs.
Therefore

    R = 2N-3 + R_inner = 2N-3 + K_m-I_m,
    C = N(N-1)/2,  r=R/C.

The exact multiplicity at R=2N-3+k is the Mahonian coefficient
M(m,k) (symmetry of the inversion distribution), k=0,...,K_m;
the sum of all weights is m!. For m=0 or 1 there is one weight.
The **exact** rational controls are

    min R=2N-3, max R=C;  P(R=0)=0;
    E[R]=2N-3 + (N-2)(N-3)/4;
    E[r]=(N^2+3N-6)/(2N(N-1))
        =1/2+(2N-3)/(N(N-1));
    Var(r) = Var(I_m)/C^2
           = m(m-1)(2m+5)/(72*C^2),  m>=0.

The inversion variance formula also covers m=0,1 by zero factors.
For every finite N, E[r]>1/2, so monotonicity of the usual
Myrheim-Meyer D2 relation implies d(E[r])<2. At N=2 and N=3,
r=1 deterministically, hence d(r)=1; there is no undefined estimate.
Unlike D2-M0, E[d(r)] is **unconditional** and always defined.

## Required proposed observables and controls

For each integer N=2,...,32 report full exact weights, m!, min/max R,
E[r], Var(r), d(E[r]), E[d(r)], and Jensen/nonlinearity gap
E[d(r)]-d(E[r]). Compare d(E[r]) and E[d(r)] with D2-M0's
d(E[r|R>0]) and E[d(r)|R>0], respectively, explicitly identifying
the **different ensembles**. No finite-N claim may be extrapolated to
the continuum or another dimension.

Exact controls: enumeration of all m! permutations for m<=7;
weight symmetry, integer sum, range, rational mean/variance for
every N; N=2,3 both dimensions exactly 1. For numerical checks,
compute an independent 80-digit inversion from exact rational r
(no binary64 intermediate), and check every N's mean-inverse and
full weighted dimension means at N=2,3,4,8,32. Record all
binary64/high-precision discrepancies, including negative outcomes.
The D2-M0 gamma relation, monotonicity and inverse domain must be
rechecked against endpoint fractions before freezing a runner.

## Numerical acceptance details (proposal; not yet a frozen runner)

Use the exact integer Mahonian weights and `fractions.Fraction` for all
fractions and moments. Evaluate the inverse D2 MM relation on **every distinct
support fraction** `r=(2N-3+k)/C`, for every `N=2..32` and
`k=0..(N-2)(N-3)/2`; cache equal rational fractions if desired but
retain an auditable per-N coverage count. In particular `r=1` must return
`d=1` exactly without iterative root finding. For every `r<1`, use
mpmath at 80 decimal digits, passing numerator and denominator as integers,
and the seeded-Newton inverse with numerical sign checks specified below; do not construct an mpmath input from a
binary64 float. Independently evaluate the forward MM relation at the
resulting dimension and record the absolute residual.

Proposed **predeclared** numerical gates: all high-precision forward
residuals <= 1e-60; all returned dimensions finite and >= 1; dimensions
nonincreasing in `r` across each support; for the production binary64
path, maximum absolute discrepancy from the 80-digit reference <= 1e-11
for every distinct support fraction, every `d(E[r])`, and every weighted
`E[d(r)]` at N=2..32. If a high-precision solver cannot certify the
1e-60 residual, classify NUMERICAL_CHECK_FAILED rather than silently
lowering precision. Record worst-case N, fraction, residual, and signed
discrepancy; report negative outcomes as well. These thresholds are
**proposed** and require measured feasibility before freeze.

Output serialization: write exact controls as integer numerators and
denominators (not decimal-rounded JSON numbers), numeric outputs as
17-significant-digit binary64 strings, and high-precision values as
80-digit decimal strings. Preserve an ordered per-N support/check table
and complete Mahonian weights, plus versioned manifest and SHA-256
digests. No selective omission of failed fractions.

## Fixed-writer byte decision r3 (2026-11-08; implementation requirement)

The total cap is **2,000,000 content bytes simultaneously present**, including
old and temporary copies, rather than the earlier 1 MB retained-only proposal.
This modest increase avoids relying on successful compression or ignoring
atomic replacement costs. The fixed writer may create only these slots:

| Slot | Count | Maximum bytes per slot |
| --- | ---: | ---: |
| `reference.json.gz` and its atomic temporary | 2 | 800,000 |
| `manifest.json` and its atomic temporary | 2 | 16,384 |
| Combined bounded diagnostic log | 1 | 131,072 |

The sum is **1,763,840 bytes**, leaving 236,160 bytes unused.
Serialize and compress in memory, check the byte limit **before opening** the
temporary file, then fsync and replace. Keep complete exact weights, fraction
coverage reconstruction, all numerical checks and failure flags in the
compressed payload; never discard unfavorable rows to fit. No extra archive,
uncompressed on-disk staging, separate error file or output spill is permitted.
The manifest is a fixed schema with bounded strings; on refusal preserve a
minimal INCOMPLETE record within the same slots. This is a trusted fixed-writer
content bound, not a filesystem allocation quota or protection from arbitrary
writers. The implementation must test all slots, compression failure and
interrupted replacement. Previously measured 536,491 raw / 219,159 compressed
bytes are feasibility observations, **not** a bound on the final richer payload.

## Exact combinatorial later-pass check

Reproduce with `python3 -I docs/experiments/d2_e0_exact_recheck.py`.
On 2026-11-08, Python 3.12.14: all **5,914 permutations** for N=2..9
passed direct coordinate-order pair counting, matching the full shifted
Mahonian law. Exact Fraction mean, variance, support and normalization checks
passed for every N=2..32 (0.082 process CPU s).
N=4 is an explicit control: R=5 or 6 with equal weights.
This separate implementation uses no repository simulation or inversion code.
It is a same-session AI-mediated computational check of model-level
mathematics, not formal verification or external scientific review.
No MM diagnostic curve or full-CS0 data were generated in this check.

## Containment and failure semantics (design only)

A future runner must reuse or extend the existing CS0/D2-M0 supervised
subprocess design, with a separately reviewed *actual implementation*:
single worker process group; wall-clock deadline measured by the parent;
process-group termination on timeout; conservative **aggregate** CPU
accounting across worker descendants and controller/finalization; peak
aggregate resident memory (not just one child); bounded stdout/stderr,
temporary files, atomic checkpoint copies, manifest and final archive.
Check controller overhead and post-termination finalization against the
same total caps. If the available supervisor cannot guarantee aggregate
CPU/RSS or bound its own archive writes, **do not run**: record the
containment gap as a blocker instead of treating observation as enforcement.

On failure, emit an atomic minimal INCOMPLETE manifest if safely possible,
including pinned commit, config, Python/mpmath versions, stage, reason,
elapsed CPU/wall, observed peak memory and retained bytes; include
partial data only with explicit incompleteness labels. If even that
manifest cannot be safely persisted, report a missing-artifact failure
and do not infer a completed result. Never rerun automatically after
failure. An implementation PR must test timeout, killed worker,
oversized output, nonfinite numeric result, interrupted finalization,
and exact-head provenance before any once-only run authorization.

## Feasibility probe r2 (2026-11-08; engineering measurement, NOT the D2-E0 diagnostic)

Prompted by the two later-pass REVISE findings on this PR (naive full-row JSON
1.72 MB > 1 MB cap; 210-step bisection extrapolated to ~44 CPU s > 30 s cap).
Script: [docs/experiments/d2_e0_feasibility_probe.py](experiments/d2_e0_feasibility_probe.py),
run twice with `python3 -I` in the cloud sandbox (not Lightsail; Python 3.13.18,
mpmath 1.3.0, SciPy 1.18.1, 2 vCPU), Director `rd-claude-20261108T0803Z-d84f4978`.
It computes real 80-digit inverses (no placeholders) but is **not** a frozen
runner, has no containment, and its values are **not** a reported D2-E0 result.

Measured (numerical engineering observations, single host, two runs; all
non-timing outputs byte-identical between runs):

- 4,526 per-N support rows reduce to **3,921 distinct reduced fractions**.
- Solver: binary64 `brentq` seed on [1,10], then 80-digit Newton with
  analytic derivative `f·(ψ(d+1)+ψ(d/2)/2−(3/2)ψ(3d/2))`, stop at step
  <1e-75; numerically sign-check each root by the sign change `f(d−1e−62)>r>f(d+1e−62)`
  (f is decreasing) from the exact rational `r` (the target is never
  constructed from binary64; only the starting point is). Max Newton
  iterations 4; max forward residual 5.3e−81 (gate 1e−60); all
  certifications passed; dimensions nonincreasing in r within every N.
- Binary64 discrepancy vs 80-digit: support max 2.98e−15, `d(E[r])` and
  `E[d(r)]` summaries max 1.33e−15 (proposed gate 1e−11). Exact
  `E[r]=(N²+3N−6)/(2N(N−1))` re-asserted from the weights for every N.
  N=32 minimum r=61/496 gives d≈3.75324363653865860, matching the earlier
  independent bisection value.
- Cost of the whole probe process: **10.3–11.6 CPU s**, 11.7 s wall,
  max RSS 85,064 KiB (inverse stage 10.9 CPU s).
- Bytes (compact UTF-8 JSON): distinct-fraction table (80-digit + binary64
  strings) + per-N coverage counts + 31 summaries + **complete** integer
  Mahonian weights = **536,491 bytes** (219,159 gzip-9); weights alone 82,002.

Consequences for the design (proposed, still not frozen):

1. Replace bisection by the seeded-Newton + numerical sign-check inverse; keep
   the independent bisection only as a spot cross-check (e.g. N=2,3,4,8,32
   extreme and mean fractions) so the 80-digit path is not solely seeded-
   derived.
2. Serialize one table keyed by **distinct** reduced fraction plus an
   auditable per-N coverage list (N → k-range → fraction index) and the
   complete weights; do not repeat 80-digit strings per (N,k) row.
3. The original 1 MB cap could not accommodate two uncompressed atomic
   copies. The r3 fixed-writer decision above replaces it with a 2 MB
   simultaneous-content cap and explicit slots; actual payload completeness,
   compression and failure behavior still require implementation tests.
4. CPU margin is host-dependent; the runner must measure on the target
   host before authorization rather than relying on this sandbox timing.

**Still blocking freeze:** aggregate process-tree/controller/finalization
containment and the fixed-writer byte rules are **not implemented or tested**.
The byte-accounting design choice is resolved; enforceability remains open.
Numerical sign checks at finite precision are not rigorous interval certificates.
No D2-E0 run is authorized.

## Implementation step 1 (2026-11-10): computation + fixed writer, NO runner

`src/emergence_lab/d2_e0_reference.py` implements, but does not execute for
the target N=2..32: shifted Mahonian weights; exact rational controls for every
N (support, normalization, symmetry, min/max R, mean, variance, E[r]>1/2);
distinct reduced-fraction table with per-N coverage indices; the seeded 80-digit
Newton inverse with numerical sign check (r=1 → d=1 without iteration, target
from the exact rational only); unseeded 80-digit bisection spot checks at
N=2,3,4,8,32 (min, max, mean fractions); binary64 production path with the
1e-11 gate; d(E[r]) in [1,2) and the N=2,3 exact-1 controls. The residual and
sign check are **recomputed by the caller** from the stored 80-digit text and
the exact rational, so a solver's self-reported flags are not trusted (added
after a later-pass REVISE counterexample in which returning the binary64 seed
with all flags set was accepted). Worst-case residual and summary
discrepancies are recorded. Every fraction and
occupancy is retained, including failures (outcome `NUMERICAL_CHECK_FAILED`).

The fixed writer enforces the r3 slot table (sum 1,763,840 bytes): only the
five named entries may exist; each size is checked before the temporary is
opened (`O_EXCL`); gzip is in memory with a round-trip check; the log is a single
truncating file; a stale temporary from an interrupted replacement is a counted
slot and is removed before the next replacement. Failures preserve a minimal
INCOMPLETE manifest and delete any already written reference, so no
complete-looking payload survives without a finished manifest, and the finished
manifest is the last write (log first), so no finished manifest survives a
later failure without its reference (a failed directory fsync after the final
replace keeps the consistent pair and flags `durability_unverified`). The writer
refuses payloads whose outcome is not a reference outcome or is inconsistent
with its failure list. Manifest keys from the caller are not schema-bounded;
an oversized manifest is refused (never written beyond its slot). Tests (`tests/test_d2_e0_reference.py`, small-N fixtures
only) cover brute-force weights N=2..9, exact controls N=2..32, Newton vs
bisection, manufactured sign-check/nonfinite/discrepancy failures, oversized
payload refused before open, compression failure and non-round-trip,
nonserializable payload, interrupted `os.replace`, unexpected entries, log bound
and oversized manifest.

**Still missing before freeze:** (a) the supervised runner with aggregate
process-tree CPU/RSS/wall containment including controller/finalization
(`strict_aggregate_containment` must be demonstrated, not assumed);
(b) source/protocol/commit provenance pinning as in `d2_m0_runner`;
(c) runner-side classification of the payload contents (the writer only checks
outcome/failure-list consistency and is not a full classifier); (d) a measured bound on the
**full** compressed payload against the 800,000-byte slot (the step-1 layout
stores 80-digit d values but 6-digit residual/discrepancy strings; not measured
on the target because no evaluation is authorized). This step is engineering
only; it is not protocol freeze, run authorization, or a D2-E0 result.

## Implementation step 2 (2026-11-11): supervised runner, NO target run

`src/emergence_lab/d2_e0_runner.py` addresses items (a)–(c) above for review;
item (d) stays open because measuring the full payload requires the target
evaluation, which remains unauthorized. `main` refuses the target N=2..32 and
any N>10 unconditionally (exit 4, no output directory); only engineering
fixtures run.

**Containment model: partitioned kernel ceilings** (not cgroups; the cloud
sandbox has no cgroup v2 and runs as root, and Issue #37's audit notes that
`cpu.max` is a rate, not a total). The controller is the root of the
accountable process tree. Bounds are sums of per-process kernel limits of
processes that never overlap, not observations:

| process | CPU (RLIMIT_CPU) | address space (RLIMIT_AS) | other |
| --- | --- | --- | --- |
| controller | 4 s (soft) | 128 MiB (soft) | ITIMER_REAL at 60 s from process start (SIGALRM default kill) |
| ≤6 git helpers, sequential | 1 s each (hard) | 384 MiB (hard) | `--no-optional-locks`, FSIZE=0, seccomp, PDEATHSIG |
| 1 worker, after the helpers | 20 s (hard) | 384 MiB (hard) | FSIZE=0, seccomp, PDEATHSIG, own session, killpg |

Total CPU ≤ 4+6+20 = 30 s; simultaneous virtual memory (hence RSS) ≤ 128+384 =
512 MiB; wall ≤ 60 s. Children cannot create descendants or threads: a classic
BPF seccomp filter (with `PR_SET_NO_NEW_PRIVS`) returns EPERM for
fork/vfork/clone/clone3 (and x32 syscalls) and kills on a foreign
architecture; the worker runs a fork probe first and exits 3 if fork succeeds.
Controller limits are *soft* because a non-root child cannot be given a larger
allotment than a lowered hard limit; the kernel enforces soft limits and the
trusted controller never raises its own. Worker stdout (≤8,000,000 bytes) is
held only in controller memory; the only files are the fixed-writer slots.

Provenance: three git helpers before and three after the worker pin HEAD =
commit, a clean tree (untracked included), and every tracked `src/` file plus
the protocol by git blob id; the loaded runner/reference modules must come
from the checkout. Runner-side classification recomputes exact weights,
exact controls, support fractions and coverage indices, and checks the
distinct-fraction table, flags (a passed row must have sign_check, converged,
independent_check true and no error), spot-check count, monotonicity, config
and outcome/failure consistency; any mismatch is INCOMPLETE. The 80-digit and
binary64 **values** are trusted from the pinned worker computation, not
re-derived by the controller. The worker never loads bytecode (`-X pycache_prefix`
to a nonexistent path); the controller's own launch is a **trust precondition**
the code cannot check before its modules load: it must be started as
`python3 -I -B -X pycache_prefix=/nonexistent-d2-e0-pycache -c <launcher>` (as
in the tests). A controller launched otherwise is outside the guarantee and any `.pyc`/`__pycache__` under `src` is a
provenance failure (added after a later-pass REVISE: a planted unchecked-hash
`.pyc` passed the blob-id check and produced a REFERENCE_COMPLETE with
tampered values). `run()` repeats the target refusal. `durability_unverified`
from the writer is surfaced in the result and exit code 3.

Tests (`tests/test_d2_e0_runner.py`, 36, fixtures N≤10 only): fork/thread/file
denial and limit readback in a restricted child; worker wall kill, CPU kill,
memory refusal and stdout overflow; git-helper budget; fixture
REFERENCE_COMPLETE from a pinned clean clone; target/oversized refusal; wrong
commit and untracked file → INCOMPLETE without reference; SIGKILL of the
controller in the worker stage leaves an INCOMPLETE manifest, no reference and
no surviving worker; planted bytecode → INCOMPLETE; direct `run()` with the
target refused; 17 payload tamperings and a wrong size list → INCOMPLETE;
manufactured nonfinite binary64 → NUMERICAL_CHECK_FAILED.

Engineering observation (cloud sandbox, Python 3.13.18, mpmath 1.3.0, root,
not Lightsail): fixture N=2..8 from a pinned clone gave REFERENCE_COMPLETE in
1.02 s wall, 0.77 s CPU for the whole process tree, max child RSS 78,688 KiB;
compressed reference 4,686 bytes. Not a D2-E0 result.

**Limits of the guarantee.** RLIMIT_CPU is enforced at scheduler-tick
granularity, so each process can overshoot slightly; the launching shell,
kernel memory and page cache, filesystem faults, a concurrent adversary
editing the checkout, and the trustworthiness of the interpreter and mpmath
are outside it. Hard child limits bind the child itself only without
CAP_SYS_RESOURCE (root in this sandbox lacks it; a normal root host has it);
the manifest records `cap_sys_resource`, and an authorized run should require
it false. A kill of the controller by its own limits leaves the last
INCOMPLETE checkpoint, not a finished manifest; a kill inside the final write
window can leave `reference.json.gz` beside a non-finished manifest, which is
INCOMPLETE by rule (the manifest is authoritative); this window is not
covered by a test. Containment must still be
re-checked on whichever host a once-only run would use (e.g. seccomp
availability) before any authorization.

**Still missing before freeze:** (d) above; later-pass review of this step;
then protocol freeze and a separately recorded once-only authorization that
adds the target path. No deployment, Lightsail action or target evaluation.

## Proposed resources and decision rule (not authorization)

Deterministic, no RNG or sampling error. Proposed limits:
30 CPU seconds, 60 wall seconds, 512 MiB total observed memory,
2,000,000 simultaneous output content bytes under the fixed-writer rules; include controller/finalization cost
and manifest, environment, exact code/config SHA, complete results,
error checks, and SHA-256 digests. Require verified aggregate process-tree and controller containment;
if budget/provenance fails record INCOMPLETE, not a selectively rerun
curve. Outcome vocabulary: REFERENCE_COMPLETE, NUMERICAL_CHECK_FAILED,
INCOMPLETE; never CS0 PASS.

**Freeze gate:** later-pass reviewer verifies the combinatorial law,
variance, inversion range, numerical precision, endpoint ensemble,
proposed tests and enforceable budget. Design integration does not require an already implemented runner and must
not be described as protocol freeze. Next implement the bounded runner in a
separate reviewed code change, verify its exact-head numerical/failure/resource
tests, and only then freeze the protocol and authorize at most one pinned
diagnostic in a separately recorded decision. No Lightsail deployment.
