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
        for payload, expected in [({}, 'INCOMPLETE'),
                                  ({'outcome': 'PASS', 'gates': {'C0-G0': False}}, 'FAIL'),
                                  ({'outcome': 'PASS', 'gates': {f'C0-G{i}': True for i in range(4)}}, 'PASS')]:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                package = root/'src/emergence_lab'
                package.mkdir(parents=True)
                (root/'docs').mkdir()
                (root/'docs/DIMENSION_C0_PREREGISTRATION.md').write_text('synthetic test fixture\n')
                (package/'__init__.py').write_text('')
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
        cases = [
            ({'outcome': 'PASS', 'gates': good}, 'PASS'),
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
        for mutation in ['none','endpoint','floor','oracle','label']:
            with self.subTest(mutation=mutation):
                r={'kernel':'graph_even_returns','bipartite':True,'n':8,'floor':.25,
                   'returns':{str(t):{} for t in TIMES},'null':True,'classification':'SATURATED'}
                if mutation=='endpoint': del r['returns']['256']
                if mutation=='floor': r['floor']=.125
                if mutation=='oracle': del r['kernel']
                if mutation=='label': r['classification']='POSITIVE_DIMENSION'
                if mutation=='none': validate_row(r)
                else:
                    with self.assertRaises(ValueError): validate_row(r)

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

