"""Recheck retained C0-v2 bytes without executing a worker (standard library only)."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys


def cycle_walks(steps, side):
    # Exact count of +/-1 walks returning modulo side, including winding paths.
    return sum(math.comb(steps, (steps + winding * side) // 2)
               for winding in range(-steps // side - 1, steps // side + 2)
               if (steps + winding * side) % 2 == 0
               and 0 <= steps + winding * side <= 2 * steps)


def recheck(directory, root):
    manifest = json.loads((directory / 'manifest.json').read_text())
    authorization = json.loads((directory / 'authorization.json').read_text())
    assert manifest['commit'] == authorization['execution_commit']
    assert manifest['outcome'] == 'PASS' and manifest['setup'] == 'passed'
    assert manifest['threads'] == 1 and len(manifest['runs']) == 2
    for path, expected in manifest['source_sha256'].items():
        data = subprocess.check_output(['git', 'show', manifest['commit'] + ':' + path], cwd=root)
        assert hashlib.sha256(data).hexdigest() == expected, path
    auth = subprocess.check_output(['git', 'show', manifest['commit'] + ':docs/C0_V2_RUN_AUTHORIZATION.md'], cwd=root)
    assert hashlib.sha256(auth).hexdigest() == authorization['authorization_sha256']
    raw_files = authorization['raw_files']
    for name, evidence in raw_files.items():
        data = (directory / name).read_bytes()
        assert len(data) == evidence['bytes']
        assert hashlib.sha256(data).hexdigest() == evidence['sha256']
    actual_bytes = sum((directory / name).stat().st_size for name in raw_files)
    assert actual_bytes == authorization['actual_raw_output_bytes'] <= 5 * 1024**2
    assert (directory / 'run1.json').read_bytes() == (directory / 'run2.json').read_bytes()
    for i, run in enumerate(manifest['runs'], 1):
        assert run['exit_code'] == 0 and not run['timeout'] and run['report_outcome'] == 'PASS'
        assert run['sha256'] == raw_files[f'run{i}.json']['sha256']
        assert run['peak_rss_kib'] <= 512 * 1024
    assert manifest['total_child_cpu_seconds'] + manifest['supervisor_cpu_seconds'] <= 300
    assert manifest['wall_seconds'] <= 600
    report = json.loads((directory / 'run1.json').read_text())
    assert report['outcome'] == 'PASS' and all(report['gates'].values())
    assert report['return_half_times'] == [8, 16, 32, 64, 128, 256]
    assert report['radii'] == [4, 8, 16, 32] and report['rng'] == 'not used'
    definitions = [('C1024', 1, 1024, False), ('T256', 2, 256, False),
                   ('C8', 1, 8, True), ('K32', 0, 32, True)]
    assert len(report['graphs']) == len(definitions)
    checks = 0
    maximum = 0.0
    for row, (name, dimension, side, null) in zip(report['graphs'], definitions):
        assert (row['graph'], row['dimension_parameter'], row['side'], row['null']) == (name, dimension, side, null)
        assert all(row['topology'][k] for k in ['connected', 'simple', 'undirected', 'no_self_loops', 'no_duplicate_edges'])
        for half_time in report['return_half_times']:
            steps = 2 * half_time
            if dimension == 1:
                exact = cycle_walks(steps, side) / 2**steps
            elif dimension == 2:
                # Allocate horizontal steps first; each axis is counted independently.
                exact = sum(math.comb(steps, k) * cycle_walks(k, side) * cycle_walks(steps-k, side)
                            for k in range(steps+1)) / 4**steps
            else:
                exact = 1/32 + (31/32) * (1/31)**steps
            entry = row['returns'][str(half_time)]
            for key in ['observed', 'oracle']:
                error = abs(entry[key] - exact)
                assert error <= 1e-12 and error / exact <= 1e-9, (name, half_time, key)
            maximum = max(maximum, abs(entry['observed']-exact))
            checks += 1
        for slope in row['spectral_slopes']:
            t = slope['half_time']
            early, late = [row['returns'][str(x)]['observed'] for x in [t, 2*t]]
            assert abs(slope['observed'] + 2*math.log2(late/early)) <= 1e-12
            for ratio in [5, 10, 20]:
                assert slope['headroom'][str(ratio)] == (early > ratio*row['floor'] and late > ratio*row['floor'])
            if not null:
                assert slope['headroom']['10']
        for volume in row['volume']:
            for key, radius in [('ball', volume['radius']), ('double_ball', 2*volume['radius'])]:
                expected = 2*radius+1 if dimension == 1 else 1+2*radius*(radius+1)
                assert volume[key] == expected
                assert volume['oracle_'+key] == expected
                checks += 1
        if null:
            assert row['classification'] == 'SATURATED'
            assert row['volume_verdict']['verdict'] == 'INSUFFICIENT_RANGE'
            assert row['volume_verdict']['d_hat'] is None
            assert abs(row['spectral_slopes'][-1]['observed']) <= 0.02
            assert all(abs(row['returns'][str(t)]['observed']/row['floor']-1) <= 0.01 for t in [128, 256])
    return {'outcome': 'PASS', 'independent_integer_walk_and_ball_checks': checks,
            'maximum_return_absolute_error': maximum, 'actual_raw_output_bytes': actual_bytes,
            'raw_manifest_output_bytes': manifest['output_bytes'],
            'note': 'manifest byte count precedes its final save; actual bytes checked separately'}


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    directory = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('c0-v2')
    print(json.dumps(recheck(directory, root), indent=2, sort_keys=True))
