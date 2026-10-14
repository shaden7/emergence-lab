# S1 implementation stage: killed-ball kernel, exact references, P0 gates (2026-10-14)

**Status: proposed implementation, producer self-review only. No pilot seed drawn.** Preregistration: [SPECTRAL_S1_PREREGISTRATION.md](../SPECTRAL_S1_PREREGISTRATION.md) v0.2 (§0 order of work, step 2). Issue [#37](https://github.com/shaden7/emergence-lab/issues/37). Director session `rd-claude-20261014T0717Z-1bae2f26dce7`.

## What was implemented

`src/emergence_lab/spectral_s1.py`, `tests/test_spectral_s1.py`, one CI step.

- **Killed-ball kernel** (prereg §3): BFS ball B(v, R); sub-stochastic kernel P_R with the full-graph degrees; 2T steps from δ_v; q read at every even step. Killed mass is accumulated as the exact outflow through boundary vertices (no `1 − Σ` cancellation). Reversibility identity deg(v) Σ_x P_R^t(v,x)²/deg(x) is evaluated at requested t ≤ T.
- **Radius rule:** R = 64, doubled until m_R(2T) ≤ η·q_R(2T) (η = 10⁻⁴) or R ≥ 2T. A source whose 2T·nnz(P_R) exceeds 2·10⁹ returns status `OVER_CAP` with NaN values and is written to the CSV (never dropped).
- **Exact reference (P0a):** all N^(N−2) labelled trees via all Prüfer sequences (bijection checked by counting distinct edge sets), integer matrix B = diag(M/deg)·A with M = lcm(1..N−1), so [P^(2t)]_vv = [B^(2t)]_vv/M^(2t) exactly; annealed mean as a `Fraction`. Independent of the float kernels except the shared D2 Prüfer decoder.
- **P0b–P0d gate functions**, CSV writer (`repr` floats, no wall time), manifest (commit, prereg/config SHA-256, versions, seeds).
- **Statistics for P3/P5/§7, not yet applied to any data:** annealed window slope, tree-level delta-method influences ψᵢ, U = (n−1)s²_ψ/χ²₀.₀₅,ₙ₋₁ and h(n′), 3U sensitivity, frozen reliability screen (|g₁| > 1.5, max share > 0.5, Q̄ ≤ 0, s² = 0), seeded whole-tree bootstrap (seed 2036101499), size-equivalence CI, admissible dyadic windows, adjacent-slope check, per-source headroom against deg(v)/(N−1).
- **Seed lock:** `build_instance` refuses the pilot base 2036101301 unless `S1_ALLOW_PILOT_SEEDS=1`. All tests and P0b/P0d use the engineering base **2036101397** (distinct from pilot, bootstrap and D2 bases; grep at base `b67ee30` found no other use).

**Not implemented yet:** the pilot orchestration (ladder from tree 0, CPU accounting, peak memory, P1–P6 report assembly, release-asset handling). That belongs in a follow-up commit or PR after review of this kernel.

## Executed (Director cloud sandbox, Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1; base `main` `b67ee30`)

- `pytest -q`: 339 passed (25 new S1 tests), 102 s.
- `python -m emergence_lab.spectral_s1 --output …` (P0 CLI), 62 s wall: **P0a, P0b, P0c, P0d all PASS.**
  - P0a: max |pipeline − exact| = 1.9·10⁻¹⁵ (N = 5), 9.7·10⁻¹⁵ (N = 6), 1.5·10⁻¹³ (N = 7), t = 1…4, all trees, all vertices. Exact annealed values for N = 7: q(1) = 8866/16807, q(2) = 1275013/3025260, q(3) = 403465807/1089093600, q(4) = 133810589683/392073696000. Hand checks in tests: N = 3 gives 2/3; N = 4 gives 19/32 at t = 1.
  - P0b: 3 instances × 3 families (CAY N = 4096, UST L = 64, RRT N = 4096), 4 sources each, T = 256: killed ball with R = 2T vs S0 `graph_even_returns` max abs difference 1.1·10⁻¹⁶; identity check 1.1·10⁻¹⁶; killed mass exactly 0; even-time monotone; brackets with forced R ∈ {2, 4, 8, 16} contain the exact value in every case.
  - P0c: Z² torus L = 64, 32 evenly spaced sources, t ≤ 256: max |q − Fourier| = 1.4·10⁻¹⁷.
  - P0d: CSV SHA-256 `dd030399…d93cb` identical across two separate interpreter processes (engineering CAY tree N = 4096, T = 256, 8 sources).
- These are **instrument checks**, not measurements of any spectral dimension.

## Engineering cost observation (engineering seeds, one source each, not a benchmark)

T = 4096, single process: CAY N = 65536 settled at R = 256 (|B| = 23781, 3.9·10⁸ edge-steps), 4.8 CPU-s including the discarded R = 64 and 128 attempts; UST L = 128 at R = 256 (|B| = 4381), 0.4 CPU-s; RRT N = 65536 at R = 64 with the ball already the whole tree (|B| = 65536, 1.07·10⁹ edge-steps), 11.3 CPU-s. One source per family is not a cost model. Naively, 512 CAY sources at ~5 s would be ~43 CPU-min, close to the 45 CPU-min ladder trigger, and the N = 2¹⁸ trees may need a larger R. The pilot's tree-0 ladder rule (§6) decides; these numbers do not.

## Points for the later-pass reviewer

1. **P5 CI quantile:** the prereg fixes a 90 % two-sided CI from tree-level delta-method SEs but not the reference distribution. Implemented: Welch t with Satterthwaite df (wider than z for n = 8). Confirm or change before pilot data exist.
2. **P0c is weak as specified:** at L = 64 the R = 64 ball is the whole torus, so killing never acts. A supplementary test uses L = 256 with r_start = 16 (killing active, rule must double) and checks the Fourier value inside the bracket.
3. **P0d** is run on an engineering tree. Repeating it on pilot tree 0 belongs to the pilot run.
4. **Radius doubling repeats the whole iteration** for each R; acceptable for correctness, wasteful for cost (included in the timings above).
5. The forced-small-R brackets in P0b are trivially wide at R = 2; R = 16 is the informative case.

## Evidence level

Implementation plus deterministic exactness checks (known-answer and exact-rational). No pilot sample, no d_s value, no physics claim. No Lightsail activity, deployment or spending.
