# S1 preregistration later-pass review — design audit, 2026-10-14

**Decision:** REVISE v0.1; v0.2 corrects the identified methodological errors. This is an AI-mediated later-pass review by a different session from the producer, not external peer review. **No tree pilot data were generated or inspected.** CI on the amended head and any eventual merge must be checked independently of this review note.

## Exact checks and observations

1. **S0 killed-ball bound (mathematical check):** paths not leaving B contribute P_R^s(v,v); returning paths that exited B contribute at most killed mass m_R(s). Therefore q_R(s) ≤ q(s) ≤ q_R(s)+m_R(s). As a substochastic operator reversible under original graph-degree weights, P_R is similar to a symmetric matrix, and its even moments at a fixed source are non-increasing: q_R(2t)=Σ_k w_k λ_k^(2t) with w_k ≥ 0 and |λ_k| ≤ 1. Consequently m_R(2T) ≤ η q_R(2T) bounds relative truncation error at all earlier **even** times 2t. Numeric implementation and floating-point accuracy still require P0a–P0c.
2. **Source-of-mean vs mean-of-source slopes (deterministic counterexample):** take two tree-mean return profiles Q₁(lo)=0.08, Q₁(hi)=0.04, Q₂(lo)=0.02, Q₂(hi)=0.018, hi/lo=2. The annealed slope is 1.571750, while the average of separate slopes is 1.152003. Thus tree-specific slope variance is not the sampling variance of the declared log-of-mean estimator. This arithmetic example is **not** an observed tree simulation. v0.2 uses tree-level joint influences of Qᵢ(lo) and Qᵢ(hi).
3. **Headroom consistency:** at t=4096, t^(−2/3)=1/256 and the finite bipartite floor at N=65536, deg(v)=2 is 2/65535, giving ratio 128.00 (assuming unit amplitude). The v0.1 '≥10⁴ expected' statement was unsupported. Headroom is measured on each sampled source, not certified by this illustration.
4. **Size test logic:** a CI that contains 0 is a failed-difference test, not evidence of equality. v0.2 uses a 90% CI fully contained in a prospectively chosen ±0.03 margin (TOST interpretation), with disclosure that n=8 may lack power.
5. **Decision logic:** a two-family S2 GO must establish finite cost and prospective precision for **both** CAY and UST. A very precise CAY alone cannot qualify an unresolved UST. The reduced GO condition is therefore strengthened.
6. **Power method limitations:** the χ² upper variance factor assumes approximate independent, normal tree influences; it is not a distribution-free coverage guarantee with n=8. Whole-tree bootstrap and 3× variance sensitivity are diagnostics; dominating trees or gross skew force an UNRELIABLE/NO-GO finding. Future S2 tests must have fresh seeds and prespecified tolerances.
7. **Resource projection:** 8192×50000 ≈ 4.096×10⁸ edge-step updates **per source**, not a measured CPU duration. The 120 CPU-min / 2 GiB hard cap remains; pilot may correctly end BLOCKED or NO-GO.

## Scope and reproducibility

- Reviewed PR v0.1 head: `fc63e44dcce9f2142a7b9187998331b8a063353d`; review adjustments frozen as v0.2 before all pilot samples.
- Direct known reference: Barlow & Kumagai, *Random walk on the incipient infinite cluster on trees* (2006, https://arxiv.org/abs/math/0503118), and Barlow & Masson, *Spectral dimension and random walks on the two dimensional uniform spanning tree* (2011, https://arxiv.org/abs/0912.4765). Both are infinite-model results, not finite-N predictions. Their applicability and exact random-root conventions to CAY require careful limit matching.
- This note contains an analytic identity and arithmetic checks only; no formal Lean proof, stochastic confidence intervals, remote simulation, deployment, or empirical physics evidence.
- Remaining risk: high-order finite-size and source-degree effects; approximate n=8 variance upper bound; very low power of stringent size-equivalence test. These may yield an honest scoped NO-GO.
