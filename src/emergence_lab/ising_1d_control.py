"""Interacting 1D periodic Ising negative control: no critical point at T>0.

Exact finite-L energy derived from Z=(2cosh K)^L+(2sinh K)^L.  Energy,
|magnetization|, susceptibility_abs and Binder use same conventions as 2D.
This benchmark has genuine nearest-neighbor interactions but no finite-T
thermodynamic phase transition; it is a model assumption/control, not new physics.
"""
import argparse
import json
import math
import os
import platform
from pathlib import Path

import numpy as np
from .stats import independent_chain_interval


def exact_energy_per_spin(size, temperature):
    if type(size) is not int or size < 4 or type(temperature) not in (float, int) or not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("finite L>=4 and positive temperature required")
    t = math.tanh(1 / temperature)
    return -float((t+t**(size-1))/(1+t**size))


def run_chain(size, temperature, burn, samples, every, seed):
    if type(size) is not int or size < 4 or size % 2 or type(burn) is not int or burn < 0 or type(samples) is not int or samples < 1 or type(every) is not int or every < 1 or not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("invalid 1D configuration")
    rng = np.random.default_rng(seed)
    spins = 2 * rng.integers(0, 2, size=size, dtype=np.int8) - 1
    colors = np.arange(size) % 2
    e, a, sq, fourth = [], [], [], []
    for sweep in range(burn + samples):
        for color in (0, 1):
            nb = np.roll(spins, 1) + np.roll(spins, -1)
            de = 2 * spins * nb
            accept = (de <= 0) | (rng.random(size) < np.exp(-np.maximum(de, 0)/temperature))
            spins[(colors==color) & accept] *= -1
        if sweep >= burn and (sweep-burn)%every==0:
            signed = float(np.mean(spins))
            e.append(float(-np.mean(spins*np.roll(spins, 1))))
            a.append(abs(signed))
            sq.append(signed*signed)
            fourth.append(signed**4)
    mean_sq = float(np.mean(sq))
    return {"size":size,"temperature":temperature,"seed":seed,"measurements":len(e),
            "energy_per_spin":float(np.mean(e)),"abs_magnetization":float(np.mean(a)),
            "susceptibility_abs": float(size/temperature*(mean_sq-float(np.mean(a))**2)),
            "binder": float(1-np.mean(fourth)/(3*mean_sq*mean_sq)) if mean_sq>0 else None}


def run_pilot(cfg):
    sizes, temps, reps = cfg["sizes"],cfg["temperatures"],cfg["repeats"]
    burn, sample, every = cfg["burn_sweeps"],cfg["sample_sweeps"],cfg["sample_every"]
    if (not isinstance(sizes,list) or not sizes or len(set(sizes))!=len(sizes) or
            any(type(s) is not int or s<4 or s>64 or s%2 for s in sizes) or
            not isinstance(temps,list) or not temps or len(set(temps))!=len(temps) or
            any(type(t) not in (float,int) or not math.isfinite(t) or t<=0 for t in temps) or
            type(reps) is not int or not 4<=reps<=24 or type(cfg["base_seed"]) is not int or
            type(burn) is not int or type(sample) is not int or type(every) is not int or
            burn<0 or sample<1 or every<1):
        raise ValueError("invalid 1D plan")
    proposals=sum(sizes)*len(temps)*reps*(burn+sample)
    if proposals>10_000_000 or len(sizes)*len(temps)*reps>128 or burn+sample>12000:
        raise ValueError("1D budget exceeded")
    records=[]
    for ti,t in enumerate(temps):
        for si,L in enumerate(sizes):
            for rep in range(reps):
                seed=cfg["base_seed"]+100000*ti+1000*si+rep
                records.append(run_chain(L,float(t),burn,sample,every,seed))
    summaries=[]
    for t in temps:
        for L in sizes:
            group=[r for r in records if r["size"]==L and r["temperature"]==t]
            summary={"size":L,"temperature":t,"exact_energy_per_spin":exact_energy_per_spin(L,float(t))}
            for name in ("energy_per_spin","abs_magnetization","susceptibility_abs","binder"):
                data=[r[name] for r in group]
                mean,se,lo,hi=independent_chain_interval(data) if None not in data else (None,None,None,None)
                summary[name]={"mean":mean,"stderr":se,"ci95_low":lo,"ci95_high":hi}
            measured=summary["energy_per_spin"]
            if measured["stderr"] is None:
                summary["energy_z_vs_exact"]=None
            else:
                summary["energy_z_vs_exact"]=abs(measured["mean"]-summary["exact_energy_per_spin"])/measured["stderr"]
            summaries.append(summary)
    return {"model":"1d-nearest-neighbor-ferromagnetic-ising-periodic-J1", "config":cfg,
            "environment":{"python":platform.python_version(),"numpy":np.__version__,"commit":os.getenv("GIT_SHA")},
            "proposals":proposals,"records":records,"summaries":summaries,
            "caveats":["A 1D Ising model with J>0 has no finite-positive-temperature thermodynamic phase transition.",
                       "Finite L can have smooth crossovers or misleading apparent Binder intersections.",
                       "Our nominal t intervals need chain mixing and approximate normal chain means; energy z values are exploratory multiple diagnostics."]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    result=run_pilot(json.loads(args.config.read_text()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('1D control',len(result['records']),'chains,',result['proposals'],'proposals')


if __name__=='__main__':
    main()
