"""Model-based (NOT a D2 result): effect of the PR #36 G1 implementation, which also requires 8/8
PLATEAU at 2^20, on the noise-only G1 pass probability of the prereg §5a model. Seed 828282."""
import sys, importlib.util
import numpy as np
spec = importlib.util.spec_from_file_location("r2p", "scripts/review_d2/r2_power_resolution.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
rng = np.random.default_rng(828282)
T = 40000
v20 = m.sim(20, 256, T, rng, m.DE0)
k20 = sum(v["verdict"] != "PLATEAU" for v in v20)
v22 = m.sim(22, 256, T, rng, m.DE0)
k22 = sum(v["verdict"] != "PLATEAU" for v in v22)
print(f"S=256 non-PLATEAU per replicate: 2^20 {k20}/{T} = {k20/T:.2e}; 2^22 {k22}/{T} = {k22/T:.2e}")
print(f"P(8/8 at 2^20) = {(1-k20/T)**8:.4f}; P(8/8 at 2^22) = {(1-k22/T)**8:.4f}")
ok20 = np.array([v["verdict"] == "PLATEAU" for v in v20]); ok22 = np.array([v["verdict"] == "PLATEAU" for v in v22])
d20 = np.array([v["d_hat"] if v["d_hat"] is not None else np.nan for v in v20])
d22 = np.array([v["d_hat"] if v["d_hat"] is not None else np.nan for v in v22])
trials = 200000; p_pre = p_impl = 0
for _ in range(trials):
    i = rng.integers(0, T, 8); j = rng.integers(0, T, 8)
    base = ok22[i].all() and abs(np.nanmean(d22[i]) - 2) <= 0.15 and abs(np.nanmean(d20[j]) - np.nanmean(d22[i])) <= 0.10
    p_pre += base; p_impl += base and ok20[j].all()
print(f"joint P(G1) prereg reading (nanmean at 2^20) = {p_pre/trials:.4f}; PR #36 reading (+8/8 at 2^20) = {p_impl/trials:.4f}")
