# Ising autocorrelation: first local benchmark (2026-10-09)

## Question and baseline
Does neglecting autocorrelation exaggerate the information content of sampled finite-size Metropolis Ising chains? Known 2D Ising reference critical temperature 2/log(1+sqrt(2)) ~= 2.269185; J=k_B=1. **No new physics is claimed.**

## Exact setup and budget
- Code base: main@9d541146556e32187812175ea99a41ddf5daaa51, with milestone-2 statistics patch from PR branch research/ising-statistics-m2-20261009. No server deployment.
- Config: configs/smoke.json, SHA-256 31d500fb653db1368d46364c561c825770faa289a6775529192e5b1cb7ae8b5b. Sizes 8,16; T=1.5,2.269185,3.5; repeats 2; burn 100; sample sweeps 200; every fifth sweep; base seed 1234.
- Budget: 12 chains, 300 sweeps each, L<=16; run locally with Python 3.13.5 / NumPy 2.3.5; no server CPU budget consumed. GIT_SHA was not set locally.
- Exact reproduction after checkout of PR head: run the CLI with --config configs/smoke.json --output results/smoke; inspect measurements.csv, summary.csv and manifest.json.

## Numerically observed
At L=16 and T=2.269185, two independent seed chains:
- seed 1828234: 40 measurements, integrated autocorrelation time for |M| ~4.39 sample intervals; effective samples ~4.56.
- seed 1828235: 40 measurements, autocorrelation time ~5.18; effective samples ~3.86.
- Across the two chains, average |M| ~0.68555, approximate 95% Student-t interval **[-0.00436, 1.37545]**. This enormous unconstrained interval is a warning about insufficient replicas, not a physically feasible parameter domain.
- Low T=1.5 versus high T=3.5 gives mean |M| ~0.98770 versus ~0.14326 for L=16, consistent qualitatively with the reference model, but short-run numerical checks are not quantitative phase-transition evidence.

## Controls and uncertainty
- Unit tests (10 passed) compare i.i.d. Gaussian noise to synthetic correlated AR(1) noise, reject nonfinite input, and do not assign zero uncertainty to a trapped/constant series.
- The approximate per-chain error uses a positive-lag integrated autocorrelation heuristic (minimum 20 samples; truncation at first nonpositive correlation or window 5*tau).
- Approximate between-chain 95% intervals use independent seeded chain means, with 2 repeats giving t critical ~12.706; they assume normality of chain means and ignore untested burn-in bias.
- The run does not establish calibrated coverage, asymptotic scaling, equilibrium, or exact infinite-volume behavior. Autocorrelation may be badly underestimated for chains slower than the measurement window.

## Planned falsification / holdout
Compare longer runs at fixed L,T with independent holdout seeds and increasing burn-in and autocorrelation windows; require interval stability and no systematic seed/burn-in shift before drawing thermodynamic conclusions. Add a noninteracting-spin baseline; only then start finite-size scaling.
