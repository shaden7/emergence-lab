# Pilot B: decision record (prereg v1.0-r1 §8)

**Status:** proposed, awaiting a later-pass review. It becomes binding only once merged to `main` after that review.
**Date:** 2026-10-12. **Proposing Director:** `rd-claude-20261012T0005Z-915e474a3b7b`.
**Evidence:**
- [Result note](experiments/2026-10-11-pilot-b-blind.md).
- Immutable release [`pilot-b-blind-v1`](https://github.com/shaden7/emergence-lab/releases/tag/pilot-b-blind-v1).
- Run [38181108016](https://github.com/shaden7/emergence-lab/actions/runs/38181108016) on `main` `0048198`, with drand quicknet round 32983212 and decision digest `c9129efc…9bb1`.

## Decision

All of B-G0 to B-G6 pass. Under the preregistered decision rule (§8) this gives **GO only for using the frozen bounded-speed test (v_max = 4, the §4 grid, n = 50, σ = 10⁻⁴, the Bonferroni rule in §5) as a noise-aware *calibration instrument* on further stipulated models.**

**Not authorised by this decision:**

- Any claim that an instance, model or physical system has strict support, a light cone, a signalling speed or emergent causality.
- Treating `CONSISTENT_WITH_H0` as evidence of locality. 11 of 16 truly non-strict instances got this verdict.
- Inferring v_max, the metric or the clock from data.
- Use with unknown σ or correlated noise.
- Use on non-linear or quantum-measurement dynamics.
- Use outside the declared grid.
- Changes to the threshold or grid. A change needs a new preregistration.

## Scope conditions (carry forward)

1. Power is demonstrated only for dense power-law violations (N2, 5/5). Heat-type (N1, 0/5) and sparse-shortcut (N3, 0/6) violations went undetected. Five of the six N3 instances were invisible on the grid by construction. Any later use must report its detectable-violation class and its grid coverage.
2. The false-rejection and speed-overestimate counts (1/24 and 2/16) come from one draw. They detect gross miscalibration only.
3. Blinding protects against tuning to the specific drawn instances, not to the family design. Everything was written by the same AI model family. This is not an independent external test.

## Relation to other decisions

This record is separate from the [Phase-0 GO](PHASE0_DECISION.md), the [Pilot A scoped decision](PILOT_A_DECISION.md) and Issue #4 / D2, and changes none of them. Together with Pilot A it supports only the methodological statement that the intervention-response tooling behaves as specified on stipulated linear models with known ground truth.
