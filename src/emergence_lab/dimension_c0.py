"""Deterministic C0 worker; execute only through a bounded supervisor."""
import json
import math
import numpy as np
from emergence_lab.dimension_d1 import (torus_lattice, _from_edges, shell_counts,
    ball_sizes, required_radii, mean_balls, verdict)
from emergence_lab.spectral_dimension import (graph_even_returns,
    torus_even_return_fourier, complete_graph_even_return,
    infinite_lattice_even_return, local_spectral_slope, has_powerlaw_headroom)

from emergence_lab.c0_report import TIMES, RADII, validate_row, validate_report  # noqa: F401  (re-exported)


def check_topology(graph):
    """Independent CSR checks of the frozen C0-G0 topology properties.

    Performed here on the constructed graph; this does not rely on the builders' own
    loop/duplicate removal. Connectivity uses SciPy connected components, not BFS shells."""
    from scipy import sparse
    from scipy.sparse.csgraph import connected_components
    n = graph.n
    rows = np.repeat(np.arange(n, dtype=np.int64), graph.degrees)
    cols = graph.indices.astype(np.int64)
    key = rows * n + cols
    reverse = np.sort(cols * n + rows)
    forward = np.sort(key)
    no_loops = bool(np.all(rows != cols))
    no_dup = bool(forward.size == 0 or np.all(np.diff(forward) > 0))
    undirected = bool(np.array_equal(forward, reverse))
    matrix = sparse.csr_matrix((np.ones(cols.size, dtype=np.int8), cols, graph.indptr), shape=(n, n))
    connected = bool(connected_components(matrix, directed=False)[0] == 1)
    return {'connected': connected, 'simple': no_loops and no_dup, 'undirected': undirected,
            'no_self_loops': no_loops, 'no_duplicate_edges': no_dup,
            'checked_by': 'dimension_c0.check_topology (independent of graph builder)'}

def run():
    rows = []
    gates = {f'C0-G{i}': True for i in range(4)}
    for name, d, L, null in [('C1024',1,1024,False),('T256',2,256,False),
                              ('C8',1,8,True),('K32',0,32,True)]:
        if d:
            graph = torus_lattice(d,L)
        else:
            u,v = np.triu_indices(32,1)
            graph = _from_edges(32,u,v)
        n = graph.n
        floor = (2 if d else 1)/n
        degree = 2*d if d else 31
        topology = check_topology(graph)
        gates['C0-G0'] &= all(topology[k] for k in ['connected','simple','undirected'])
        gates['C0-G0'] &= bool(np.all(graph.degrees == degree) and
            graph.n_edges == n*degree//2 and max(TIMES)*graph.indices.size <= 100000000)
        q = graph_even_returns(graph,0,TIMES)
        ref = {t: torus_even_return_fourier(d,L,t) if d else
               complete_graph_even_return(32,t) for t in TIMES}
        returns = {}
        for t in TIMES:
            error = abs(q[t]-ref[t])
            gates['C0-G2'] &= error <= 1e-12 and error/ref[t] <= 1e-9
            returns[str(t)] = {'observed':q[t],'oracle':ref[t],
                'absolute_error':error,'relative_error':error/ref[t]}
            if d:
                inf = infinite_lattice_even_return(d,t)
                returns[str(t)].update(infinite=inf,finite_relative_to_infinite=(ref[t]-inf)/inf)
        slopes = []
        for t in TIMES[:-1]:
            observed = local_spectral_slope(q[t],q[2*t])
            oracle = local_spectral_slope(ref[t],ref[2*t])
            headroom = {str(k):all(has_powerlaw_headroom(q[x],floor,ratio=k)
                        for x in [t,2*t]) for k in [5,10,20]}
            gates['C0-G2'] &= abs(observed-oracle) <= 1e-9
            if not null:
                gates['C0-G3'] &= headroom['10']
            entry = {'half_time':t,'observed':observed,'oracle':oracle,
                     'residual':observed-oracle,'headroom':headroom}
            if d:
                entry['infinite_slope_offset'] = local_spectral_slope(
                    infinite_lattice_even_return(d,t),infinite_lattice_even_return(d,2*t))-d
            slopes.append(entry)
        shells = shell_counts(graph,0)
        volume = []
        if null:
            vv = verdict(mean_balls([shells],required_radii([shells],4)),n)
            gates['C0-G3'] &= vv['verdict']=='INSUFFICIENT_RANGE' and vv['d_hat'] is None
            gates['C0-G3'] &= all(abs(q[t]/floor-1)<=0.01 for t in [128,256])
            gates['C0-G3'] &= abs(slopes[-1]['observed'])<=0.02
        else:
            balls = dict(zip(RADII,map(int,ball_sizes(shells,RADII))))
            oracle = {r:2*r+1 if d==1 else 1+2*r*(r+1) for r in RADII}
            gates['C0-G1'] &= balls==oracle
            for r in RADII[:-1]:
                obs=math.log2(balls[2*r]/balls[r]); ex=math.log2(oracle[2*r]/oracle[r])
                gates['C0-G1'] &= 2*r<L/2 and abs(obs-ex)<=1e-12 and ex<d
                volume.append({'radius':r,'ball':balls[r],'double_ball':balls[2*r],
                    'oracle_ball':oracle[r],'oracle_double_ball':oracle[2*r],
                    'observed':obs,'oracle':ex,'residual':obs-ex,'limiting_d':d,
                    'finite_radius_offset':ex-d,'classification':'FINITE_RADIUS_CORRECTION'})
            vv={'verdict':'POINTWISE_CONTROL','d_hat':None}
        row={'graph':name,'n':n,'dimension_parameter':d,'side':L,'source':0,
             'null':null,'bipartite':bool(d),'floor':floor,'kernel':'graph_even_returns',
             'volume_kernel':'shell_counts','returns':returns,'spectral_slopes':slopes,
             'volume':volume,'volume_verdict':vv,'topology':topology,
             'classification':'SATURATED' if null else 'POINTWISE_CONTROL'}
        validate_row(row)
        rows.append(row)
    report = {'schema':1,'rng':'not used','time_units':'half_steps_2t','radii':RADII,
              'return_half_times':TIMES,'graphs':rows,'gates':gates,
              'outcome':'PASS' if all(gates.values()) else 'FAIL'}
    validate_report(report)
    return report

if __name__ == '__main__':
    print(json.dumps(run(),sort_keys=True,separators=(',',':'),allow_nan=False))
