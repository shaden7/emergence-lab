import sys
import tempfile
import unittest
from pathlib import Path
from emergence_lab.dimension_c0 import validate_row,TIMES
from emergence_lab.c0_supervisor import execute

class C0Tests(unittest.TestCase):
    def test_supervisor_rejects_identical_incomplete_reports(self):
        import json
        import os
        import subprocess
        from emergence_lab import c0_supervisor
        from emergence_lab import c0_report
        from emergence_lab.dimension_c0 import run
        for payload, expected in [({}, 'INCOMPLETE'),
                                  ({'outcome': 'PASS', 'gates': {'C0-G0': False}}, 'FAIL'),
                                  ({'outcome': 'PASS', 'gates': {f'C0-G{i}': True for i in range(4)}}, 'INCOMPLETE'),
                                  (run(), 'PASS')]:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                package = root/'src/emergence_lab'
                package.mkdir(parents=True)
                (root/'docs').mkdir()
                (root/'docs/DIMENSION_C0_PREREGISTRATION.md').write_text('synthetic test fixture\n')
                (package/'__init__.py').write_text('')
                (package/'c0_report.py').write_bytes(Path(c0_report.__file__).read_bytes())
                for name in ['dimension_d1.py', 'spectral_dimension.py']:
                    (package/name).write_text('')
                (package/'dimension_c0.py').write_text('print('+repr(json.dumps(payload))+')\n')
                supervisor = package/'c0_supervisor.py'
                supervisor.write_bytes(Path(c0_supervisor.__file__).read_bytes())
                subprocess.run(['git','init','-q',directory],check=True)
                subprocess.run(['git','add','.'],cwd=root,check=True)
                subprocess.run(['git','-c','user.name=C0 Test','-c','user.email=test@example.invalid','commit','-qm','fixture'],cwd=root,check=True)
                sha = subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
                subprocess.run([sys.executable,str(supervisor),'--commit',sha,'--output',str(root/'output')],
                               cwd=root,env={**os.environ,'PYTHONPATH':str(root/'src')},
                               check=True,capture_output=True,timeout=10)
                manifest = json.loads((root/'output/manifest.json').read_text())
                self.assertEqual(manifest['outcome'],expected)
                self.assertEqual(len(manifest['runs']),2 if expected=='PASS' else 1)

    def test_report_outcome(self):
        from emergence_lab.c0_supervisor import report_outcome
        good = {f'C0-G{i}': True for i in range(4)}
        from emergence_lab.dimension_c0 import run
        cases = [
            (run(), 'PASS'),
            ({'outcome': 'PASS', 'gates': good}, 'INCOMPLETE'),  # gates alone are not a report
            ({}, 'INCOMPLETE'),
            ([], 'INCOMPLETE'),
            ({'outcome': 'INCOMPLETE', 'gates': good}, 'INCOMPLETE'),
            ({'outcome': 'PASS'}, 'INCOMPLETE'),
            ({'outcome': 'PASS', 'gates': {}}, 'INCOMPLETE'),
            ({'outcome': 'PASS', 'gates': {**good, 'C0-G0': 1}}, 'INCOMPLETE'),
            ({'outcome': 'PASS', 'gates': {**good, 'C0-G0': False}}, 'FAIL'),
            ({'outcome': 'INCOMPLETE', 'gates': {'C0-G0': False}}, 'FAIL'),
            ({'outcome': 'FAIL'}, 'FAIL'),
        ]
        for payload, expected in cases:
            with self.subTest(payload=payload):
                self.assertEqual(report_outcome(payload), expected)

    def test_payloads(self):
        import copy
        from emergence_lab.dimension_c0 import run
        from emergence_lab.c0_report import validate_report
        from emergence_lab.c0_supervisor import report_outcome
        report = run()
        self.assertEqual(report['outcome'], 'PASS')
        validate_report(report)
        def null_row(r): return r['graphs'][2]
        def pos_row(r): return r['graphs'][1]
        mutations = {
            'endpoint': lambda r: null_row(r)['returns'].pop('256'),
            'floor': lambda r: null_row(r).update(floor=.125),
            'oracle_only': lambda r: null_row(r).pop('kernel'),
            'label': lambda r: null_row(r).update(classification='POSITIVE_DIMENSION'),
            'empty_return': lambda r: pos_row(r)['returns'].update({'8': {}}),
            'nan_observed': lambda r: pos_row(r)['returns']['16'].update(observed=float('nan')),
            'missing_slope': lambda r: pos_row(r)['spectral_slopes'].pop(),
            'missing_headroom': lambda r: pos_row(r)['spectral_slopes'][0]['headroom'].pop('20'),
            'missing_volume': lambda r: pos_row(r)['volume'].pop(0),
            'volume_label': lambda r: pos_row(r)['volume'][0].update(classification='DIMENSIONAL_REDUCTION'),
            'missing_topology': lambda r: pos_row(r).pop('topology'),
            'wrong_source': lambda r: pos_row(r).update(source=1),
            'missing_graph': lambda r: r['graphs'].pop(),
            'null_verdict': lambda r: null_row(r)['volume_verdict'].update(verdict='PLATEAU'),
            'outcome_mismatch': lambda r: r['gates'].update({'C0-G3': False}),
            'grid': lambda r: r.update(radii=[4, 8, 16]),
            # Later-pass counterexamples (2026-11-02 review of 726e029): topology/G0 coherence.
            'topology_disconnected_under_g0': lambda r: r['graphs'][0]['topology'].update(connected=False),
            'topology_simple_with_loop': lambda r: r['graphs'][0]['topology'].update(no_self_loops=False),
            'topology_simple_with_duplicate': lambda r: r['graphs'][3]['topology'].update(no_duplicate_edges=False),
            'topology_not_simple_clean': lambda r: r['graphs'][3]['topology'].update(simple=False),
            'topology_directed_under_g0': lambda r: r['graphs'][2]['topology'].update(undirected=False),
            # Derived-field identities.
            'abs_error_identity': lambda r: pos_row(r)['returns']['8'].update(absolute_error=0.0),
            'rel_error_identity': lambda r: pos_row(r)['returns']['8'].update(relative_error=0.0),
            'finite_vs_infinite_identity': lambda r: pos_row(r)['returns']['8'].update(finite_relative_to_infinite=0.5),
            'slope_residual_identity': lambda r: pos_row(r)['spectral_slopes'][0].update(residual=0.0, observed=0.9),
            'volume_observed_identity': lambda r: pos_row(r)['volume'][0].update(observed=1.0),
            'volume_offset_identity': lambda r: pos_row(r)['volume'][0].update(finite_radius_offset=0.0),
            'volume_limiting_d': lambda r: pos_row(r)['volume'][0].update(limiting_d=3),
            # True gates contradicted by self-consistent row evidence.
            'g1_ball_mismatch': lambda r: pos_row(r)['volume'][0].update(
                ball=pos_row(r)['volume'][0]['ball'] + 1,
                observed=__import__('math').log2(pos_row(r)['volume'][0]['double_ball'] /
                                                 (pos_row(r)['volume'][0]['ball'] + 1)),
                residual=__import__('math').log2(pos_row(r)['volume'][0]['double_ball'] /
                                                 (pos_row(r)['volume'][0]['ball'] + 1))
                - pos_row(r)['volume'][0]['oracle']),
            'g2_error_over_tolerance': lambda r: pos_row(r)['returns']['8'].update(
                observed=pos_row(r)['returns']['8']['oracle'] + 1e-6,
                absolute_error=abs(pos_row(r)['returns']['8']['oracle'] + 1e-6
                                   - pos_row(r)['returns']['8']['oracle']),
                relative_error=abs(pos_row(r)['returns']['8']['oracle'] + 1e-6
                                   - pos_row(r)['returns']['8']['oracle'])
                / pos_row(r)['returns']['8']['oracle']),
            'g3_headroom_false': lambda r: pos_row(r)['spectral_slopes'][-1]['headroom'].update({'10': False}),
            'g3_null_unsaturated': lambda r: null_row(r)['spectral_slopes'][-1].update(
                observed=0.5, oracle=0.5, residual=0.0),
        }
        for name, mutate in mutations.items():
            with self.subTest(mutation=name):
                bad = copy.deepcopy(report)
                mutate(bad)
                with self.assertRaises(ValueError):
                    validate_report(bad)
                self.assertNotEqual(report_outcome(bad), 'PASS')
        # Prereg-required row-level rejections.
        for name in ['endpoint', 'floor', 'oracle_only', 'label']:
            with self.subTest(row=name):
                bad = copy.deepcopy(report)
                mutations[name](bad)
                with self.assertRaises(ValueError):
                    validate_row(null_row(bad))

    def test_topology_checks(self):
        import numpy as np
        from emergence_lab.dimension_d1 import Graph, torus_lattice
        from emergence_lab.dimension_c0 import check_topology
        good = check_topology(torus_lattice(2, 8))
        self.assertTrue(all(good[k] for k in ['connected', 'simple', 'undirected']))
        def csr(rows):
            indptr = np.cumsum([0] + [len(r) for r in rows])
            return Graph(indptr, np.array([x for r in rows for x in r], dtype=np.int32))
        cases = {'self_loop': ([[0, 1], [0]], 'no_self_loops'),
                 'duplicate': ([[1, 1], [0, 0]], 'no_duplicate_edges'),
                 'directed': ([[1], [0, 2], []], 'undirected'),
                 'disconnected': ([[1], [0], [3], [2]], 'connected')}
        for name, (rows, key) in cases.items():
            with self.subTest(case=name):
                self.assertFalse(check_topology(csr(rows))[key])

    def test_setup_failure_is_persisted(self):
        import json
        import os
        import subprocess
        from emergence_lab import c0_supervisor
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git','init','-q',directory],check=True)
            package = root/'src/emergence_lab'
            package.mkdir(parents=True)
            supervisor = package/'c0_supervisor.py'
            supervisor.write_bytes(Path(c0_supervisor.__file__).read_bytes())
            # Missing sources and no commit: preflight must fail with a durable manifest.
            result = subprocess.run([sys.executable,str(supervisor),'--commit','0'*40,
                                     '--output',str(root/'output')],cwd=root,
                                    env={**os.environ,'PYTHONPATH':str(Path(c0_supervisor.__file__).parents[1])},
                                    capture_output=True,timeout=30)
            self.assertEqual(result.returncode, 2)
            manifest = json.loads((root/'output/manifest.json').read_text())
            self.assertEqual(manifest['outcome'], 'INCOMPLETE')
            self.assertEqual(manifest['setup'], 'failed')
            self.assertIn('setup_error', manifest)
            self.assertEqual(manifest['runs'], [])

    def test_module_resolution_rejects_foreign_source(self):
        from emergence_lab.c0_supervisor import verify_resolution
        root = Path(__file__).resolve().parents[1]
        package = root/'src/emergence_lab'
        names = ['__init__.py','c0_report.py','dimension_c0.py','dimension_d1.py','spectral_dimension.py']
        verify_resolution(root, [package/n for n in names])
        with self.assertRaises(ValueError):
            verify_resolution(root, [package/n for n in names[:-1]])

    def test_supervisor(self):
        cases=[('import time; print("partial",flush=True); time.sleep(10)',.15,4096),
               ('while True: pass',4,4096),('print("x"*100000)',4,128),
               ('x=bytearray(200*1024**2)',4,4096),('print(42)',4,4096)]
        for i,(code,wall,size) in enumerate(cases):
            with self.subTest(case=i), tempfile.TemporaryDirectory() as directory:
                out=Path(directory)/'out'
                result=execute([sys.executable,'-c',code],out,1,wall,64*1024**2,size)
                self.assertEqual(result['exit_code']==0,i==4)
                self.assertTrue(out.exists())
                self.assertTrue(Path(str(out)+'.stderr').exists())
                self.assertLess(result['wall_seconds'],5)
                self.assertGreater(result['peak_rss_kib'],0)
                if i==0: self.assertIn('partial',out.read_text())
                if i==4: self.assertEqual(out.read_text(),'42\n')

    def test_exact_source_preflight(self):
        import subprocess
        from emergence_lab.c0_supervisor import verify_sources
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            subprocess.run(['git','init','-q',directory],check=True)
            path=root/'source.py'; path.write_text('x=1\n')
            subprocess.run(['git','add','source.py'],cwd=root,check=True)
            subprocess.run(['git','-c','user.name=C0 Test','-c','user.email=test@example.invalid','commit','-qm','test'],cwd=root,check=True)
            sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
            verify_sources(root,sha,[path])
            path.write_text('x=1\n\n')
            with self.assertRaises(ValueError): verify_sources(root,sha,[path])
            with self.assertRaises(ValueError): verify_sources(root,'0'*40,[path])

