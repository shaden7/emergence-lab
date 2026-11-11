# D2-E0 protocol v1 — endpoint control

Frozen numerical contract, subject to the reviewed code PR being integrated.
This document alone does not authorize execution. A separate committed
`CS0_D2_E0_AUTHORIZATION.json` must pin one host, interpreter, exact reviewed
source hashes, protocol/config hashes, output path and expiry. No automatic
retry. Fixtures N<=10 are engineering tests, never target curves.

## Question and model

Does the D2-M0 small-occupancy MM shift change when the two ordered interval
endpoints are always present? Compare the same **total** N, disclosing that
the point-generation ensembles differ. Input is a fixed D=2 Minkowski diamond,
with m=N-2 independent uniform interior events and deterministic endpoints.
This validates a measurement instrument in one prescribed geometry. No model
comparison, emergent geometry, universal dimensional reduction or CS0 acceptance.

For N=2..32, let K=m(m-1)/2 and I be a uniform-permutation inversion count.
R=2N-3+K-I, C=N(N-1)/2, r=R/C. The weight of R=2N-3+k is M(m,k),
normalized by m!, including m=0,1. Record complete integer weights and exact
rational mean and variance:

- E[r]=(N²+3N-6)/(2N(N-1))=1/2+(2N-3)/(N(N-1)).
- Var(r)=m(m-1)(2m+5)/(72 C²).
- R>0 always; N=2,3 give r=1 and dimension 1 exactly.

The MM relation is f(d)=Gamma(d+1) Gamma(d/2)/(2 Gamma(3d/2)). Use its
decreasing inverse on [1,10]. The smallest support fraction is 61/496 at
N=32, inside the range; r=1 is handled exactly. These are established model
identities and numerical instrument controls, not newly proved physics.
The direct-coordinate combinatorial recheck in `experiments/d2_e0_exact_recheck.py`
checks all 5,914 permutations through N=9 and rational identities through 32.

## Observables, controls and failure rule

Record every support fraction and its per-N coverage index, E[r], Var(r),
d(E[r]), E[d(r)] and E[d(r)]-d(E[r]); E[d(r)] is unconditional here.
Compare to the archived D2-M0 conditional estimates, retaining their R>0
selection convention. Do not infer an N-to-physical-length conversion.

Use exact Fraction inputs, mpmath 1.3.0 at 80 digits, binary64 inverse as
Newton seed only, at most 12 iterations, step <1e-75, numerical sign check
f(d-1e-62)>r>f(d+1e-62), and independently recomputed forward residual
<=1e-60 from stored 80-digit text. No finite-precision sign check is a
rigorous interval certificate. Check monotonicity across the full support.
Binary64 support and both summary discrepancies must be <=1e-11. Independent
unseeded bisection to width 1e-65 at min/max/mean fractions for N=2,3,4,8,32
must agree within 1e-60. Keep all failed rows and negative outcomes.
Exact controls: support, integer positivity, symmetry, normalization,
endpoints, rational moments and N=2,3 dimensions exactly 1.

REFERENCE_COMPLETE requires all checks plus provenance and finished manifest.
NUMERICAL_CHECK_FAILED retains numerical failures. A resource/provenance,
serialization, classification or persistence failure is INCOMPLETE and takes
precedence. A reference beside a non-finished/missing manifest is INCOMPLETE.
`durability_unverified` prevents acceptance until archival verification; it
is surfaced by exit code 3. No selective row omission or threshold relaxation.
Deterministic exact weights imply no Monte Carlo sampling error; solver and
finite-occupancy/ensemble effects are the relevant limitations.

## Enforced budget and trust boundary

30 CPU s / 60 wall s / 512 MiB simultaneous user-process address space.
Partition: controller soft RLIMIT_CPU=4 s, AS=128 MiB; at most six sequential
git helpers at hard 1 CPU s / 384 MiB; one worker at hard 20 CPU s / 384 MiB.
Controller itimer covers process startup through finalization. Children have
PDEATHSIG, FSIZE=0, no core dumps, and seccomp denial of fork/vfork/clone/clone3.
Require CAP_SYS_RESOURCE verifiably absent; preflight actual host seccomp,
fork/thread denial and limit readback. RLIMIT_CPU has kernel tick granularity.
Trusted controller never raises its soft limits; it is not an adversarial
sandbox. Launcher/kernel/page-cache and third-party installation remain outside
the process resource accounting. No Lightsail, deployment, network or paid API.

Launch the controller with `python -I -B -X
pycache_prefix=/nonexistent-d2-e0-pycache`; the nonexisting cache path, trusted
interpreter/dependencies and no concurrent checkout modifications are explicit
preconditions. Verify clean exact HEAD and every src/protocol/authorization git
blob before and after worker execution. Never modify code after pinning.

Fixed-writer simultaneous content slots: reference gzip plus temporary at
800,000 B each; manifest plus temporary at 16,384 B each; one log at 131,072 B.
Sum 1,763,840 B <=2,000,000 B, including old+temporary copies. Compress/validate
in memory before opening. No other output/staging/archive is admitted. The
final full compressed size is deliberately unknown until the single authorized
attempt; exceeding 800,000 B means INCOMPLETE. This is a fixed-writer content
bound, not a filesystem quota. Retain failed/partial artifacts; no rerun.

## Review status

The design r3 and source history are in CS0_D2_ENDPOINT_CONTROL_PROPOSAL.md,
PRs #75–77. A later-session review must check this contract, exact code/tests,
host containment and failure cases before merging the target gate. A second
committed decision records the one-run authorization after integration. Neither
an implementation merge nor this freeze is an experimental result.
