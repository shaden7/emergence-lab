# S1 pilot orchestration: tree-0 ladder, accounting, P1–P6 report, §7 decision (2026-10-15)

**Status: proposed implementation, producer self-review only. No pilot seed drawn.** Preregistration: [SPECTRAL_S1_PREREGISTRATION.md](../SPECTRAL_S1_PREREGISTRATION.md) v0.2 (§4–§7). Issue [#37](https://github.com/shaden7/emergence-lab/issues/37). Builds on the merged kernel/P0 stage ([PR #45](https://github.com/shaden7/emergence-lab/pull/45), merge `4d1e838`). Director session `rd-claude-20261015T0717Z-1cadda8b713f`, base `main` `4edbc95`.

## What was implemented

`src/emergence_lab/spectral_s1_pilot.py`, `tests/test_spectral_s1_pilot.py` (14 tests), one CI step (engineering smoke run twice, numeric CSVs compared with `cmp`). The frozen config and preregistration are unchanged.

- **Modes.** `engineering` (default): engineering seed base 2036101397 and a scaled-down design (CAY N ∈ {1024, 4096}, UST L ∈ {32, 64}, RRT N = 1024, 8/8/4 trees × 8 sources, ladder T ∈ {128, 64, 32}, small budgets). `pilot`: the frozen config (checked: version 0.2, seed base 2036101301), refused unless both `S1_ALLOW_PILOT_SEEDS=1` (existing lock in `build_instance`) **and** `--i-understand-this-draws-pilot-seeds` are given.
- **Ladder (§6), cost only.** Tree 0 of the smallest size is computed at T = 2¹². Projected family CPU = tree-0 CPU (generation + all sources) × total trees of the family. If > 45 CPU-min or any tree-0 source is OVER_CAP, step to the next rung; after the last rung, the family is BLOCKED (budget) and tree 0 is still reported. On a step, tree 0's OK sources are **truncated** to the new T (valid: m_R(2t) ≤ m_R(2T) ≤ η q_R(2T) ≤ η q_R(2t)), OVER_CAP sources are recomputed at the new T; the next projection scales the OK sources' measured CPU linearly in T. q values never enter the ladder.
- **Stops.** Global CPU budget (process CPU, checked between trees; 120 CPU-min in pilot mode) and per-family hard stop at 1.5× the accepted projection → status PARTIAL, partial results retained. Peak RSS (`ru_maxrss`) recorded per source and checked against 2 GiB; the 2-GiB limit is checked, not enforced by `setrlimit`.
- **OVER_CAP** sources in later trees are kept in the numeric CSV and the report, and block that family's GO.
- **Outputs.** `s1_pilot_numeric.csv` (deterministic, no timings; S1 `rows_csv` format), `s1_pilot_timing.csv` (CPU/wall/peak RSS per source), `s1_pilot_report.json` (design, manifest, all results, SHA-256 of both CSVs).
- **Report contents.** P1 cost per tree and per source, R values, max ball, edge-steps; P2 q̄, dyadic slopes, per-tree slopes, all admissible window slopes; P3 tree influences ψ, reliability screen, whole-tree bootstrap (seeded), within-tree delete-one-source jackknife SD (descriptive), mean/SD of per-tree slopes, S2 projection at fixed S for multipliers 1 and 3 with the smallest n′ meeting 0.03 / 0.05 within 180 CPU-min; P4 degree classes and leaf share; P5 size equivalence (existing Welch/Satterthwaite 90 % CI) and per-source headroom quantiles; P6 RRT curves (not gated); controls P0a, P0c and **P0d on the run's own CAY tree 0** (separate-process replay along the ladder path actually taken, SHA-256 compared).
- **§7 decision.** GO (full) iff both CAY and UST have a W* with h ≤ 0.03; GO (reduced) iff both ≤ 0.05; else NO-GO (scoped), listing a single feasible family as descriptive only.

## Interpretations the preregistration leaves open (for the reviewer; fixed before any pilot draw)

1. **Projection method:** tree 0 of the smaller size × all trees. The larger size can cost more (see probe below); the 1.5× hard stop then decides. An alternative (time one tree of each size first) would deviate from "from tree 0 of the smallest size" and is not implemented.
2. **Both sizes required** for headroom ≥ 10, adjacent-slope ≤ 0.10, certification and the reliability screen (conservative). The S2 projection uses the **larger** size's ψ and CPU per tree, with S = 32 and one size in S2.
3. **Primary variance multiplier 1** for the decision; 3U is reported as sensitivity only.
4. Ties: smallest h, then earlier t_lo, then smaller t_hi (prereg §7).
5. Tree-0 cost entry after a ladder step is the scaled projection, not the CPU actually spent (which is kept in the ladder record).

## Executed (Director cloud sandbox, Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1, 2 vCPU; OPENBLAS/OMP threads = 1)

- `pytest -q`: **353 passed** (14 new). New tests cover: frozen-config mapping; pilot-mode refusal without flag/env; truncation keeps the certified bracket vs the S0 full kernel; ladder accept / step-down / BLOCKED; OVER_CAP recorded never dropped; OVER_CAP-on-tree-0 recompute at the lower rung; global budget → PARTIAL; end-to-end determinism of the numeric CSV; §7 branches; minimal n′ in the projection; jackknife zero for identical sources; P0d replay including a four-rung ladder path; exhausted global budget → all families PARTIAL → NO-GO.
- Engineering CLI with controls: completes in 31 CPU-s; numeric CSV SHA-256 `ecef25c5…587b` identical in two separate runs; P0a, P0c, P0d (pilot tree-0 replay) PASS. Its verdict (NO-GO at engineering sizes T = 128) is a smoke result about tiny engineering graphs, **not** pilot evidence.

## Engineering cost probe at full pilot scale (engineering seeds 2036101397, tree 0 only, T = 4096, 32 sources; not pilot data, not a benchmark)

| Family, size | tree CPU-s | R | max \|B\| | peak RSS | naive family projection |
| --- | --- | --- | --- | --- | --- |
| CAY N = 2¹⁶ | 61.7 | 256 | 39 235 | 107 MiB | 16.4 CPU-min (< 45) |
| CAY N = 2¹⁸ | 81.3 | 256 | 70 012 | 128 MiB | — |
| UST L = 128 | 12.4 | 256 | 7 844 | 107 MiB | 3.3 CPU-min |
| UST L = 256 | 13.8 | 256 | 13 681 | 104 MiB | — |
| RRT N = 2¹⁶ | 158.9 | 64 | 65 536 | 116 MiB | 10.6 CPU-min |

Implication (projection from single engineering trees, uncertain): T = 2¹² is expected to be accepted for all families; the CAY larger-size tree cost 1.32× the smaller, so actual CAY time ≈ 1.16× the naive projection, inside the 1.5× hard stop unless tree-to-tree variation is large. The whole pilot is expected around 35 CPU-min of 120. Per-source CPU varies 0.5–4 s for CAY (radius-doubling repeats included).

## Evidence level

Implementation and deterministic engineering checks; producer self-review only. No pilot sample, no d_s value, no physics claim. No Lightsail activity, deployment or spending.

## Next step

Later-pass review by a different session (the five interpretations above, ladder bookkeeping, OVER_CAP and partial handling, the P0d replay). If PASS and merged, run `S1_ALLOW_PILOT_SEEDS=1 python -m emergence_lab.spectral_s1_pilot --mode pilot --i-understand-this-draws-pilot-seeds --output …` once at the merge commit (1 core, ≤ 120 CPU-min, no Lightsail), publish CSVs/report with the manifest, and record the §7 outcome in a result note without changing the rule.

## 2026-10-15 later-pass reviewer correction (REVISE, no pilot data)

A separate GPT-6 Director reviewed the original producer head `ad6c53d` on PR #46. The previous green CI runs apply **only to that head**. The review detected five functional/data-provenance weaknesses and changed the existing PR branch, with six regression tests: (1) classify a final tree that exceeds CPU budget as PARTIAL; (2) aggregate subprocess CPU and veto §7 GO on budget/memory violations or P0 failures, including refusal of pilot mode with skipped controls; (3) produce a single-header numeric CSV with an explicit T and blank columns beyond shorter family horizons; (4) compound tree-0 cost estimates across multiple ladder steps instead of rescaling the same original measured CPU repeatedly; (5) enumerate actual executed tree SeedSequence tuples in the manifest. The reviewer did **not** sample any pilot seed. No deployment or Lightsail work.

Review status: **REVISE** pending exact-corrected-head CI and subsequent later-pass review before merge. Existing cost probes above belong to the original engineering implementation and are not freshly remeasured after the correction. Controls P0b were validated separately by the P0/CI stage but are not redundantly run in this orchestration's report. Resource checks are between trees (and after controls), not a kernel-interrupting OS-level CPU/memory limiter; overshoot retains data and explicitly denies GO. The calibrated 90% Welch equivalence CI with n=8 retains its statistical limitations. No physical inference.

## 2026-10-16 second later-pass review (PASS, engineering only)

A separate Claude Director (`rd-claude-20261016T0718Z-a56c5b176293`) reviewed the reviewer-authored corrections `ad6c53d..7b4c845` and found them correct. Its local full suite failed once in three runs in the end-to-end determinism test: the 1.5× family hard stop is timing-dependent and, at the millisecond tree costs of the tiny test design, the measured/projected CPU ratio ranged 0.79–1.42, so the stop occasionally truncated the record set. The tiny test design now disables the hard stop; production code is unchanged. For the real pilot this means byte identity holds only for an identical ladder/stop path, which the report records. No pilot seed drawn.
