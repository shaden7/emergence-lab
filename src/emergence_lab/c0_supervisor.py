"""Linux resource-limited C0 execution and failure preservation."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

from emergence_lab.c0_report import validate_report

MODULES = ['emergence_lab', 'emergence_lab.c0_report', 'emergence_lab.dimension_c0',
           'emergence_lab.dimension_d1', 'emergence_lab.spectral_dimension']

def report_outcome(payload):
    """Require explicit gate evidence; failure takes precedence over omissions."""
    if not isinstance(payload, dict):
        return 'INCOMPLETE'
    gates = payload.get('gates')
    if payload.get('outcome') == 'FAIL':
        return 'FAIL'
    if isinstance(gates, dict) and any(value is False for value in gates.values()):
        return 'FAIL'
    if (payload.get('outcome') != 'PASS' or not isinstance(gates, dict)
            or set(gates) != {f'C0-G{i}' for i in range(4)}
            or any(value is not True for value in gates.values())):
        return 'INCOMPLETE'
    try:
        validate_report(payload)
    except (ValueError, KeyError, TypeError, AttributeError):
        return 'INCOMPLETE'
    return 'PASS'

def verify_sources(root, commit, files):
    resolved=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    if resolved != commit:
        raise ValueError('executing HEAD differs from requested commit')
    for path in files:
        relative=path.relative_to(root).as_posix()
        original=subprocess.check_output(['git','show',f'{commit}:{relative}'],cwd=root)
        if path.read_bytes()!=original:
            raise ValueError('uncommitted source bytes: '+relative)

def child_env(root):
    """Child environment: one BLAS thread, project sources resolved only from this checkout."""
    env = {**os.environ, **{k: '1' for k in ['OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS',
                                             'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']}}
    env['PYTHONPATH'] = str(Path(root) / 'src')
    env.pop('PYTHONHOME', None)
    return env

def verify_resolution(root, files):
    """Probe, in a child with the worker's environment, which files the project modules load from."""
    # find_spec resolves without executing the worker modules (only the package __init__).
    probe = ('import importlib.util,json,sys;print(json.dumps({m:importlib.util.find_spec(m).origin '
             'for m in sys.argv[1:]}))')
    out = subprocess.check_output([sys.executable, '-c', probe, *MODULES], cwd=root,
                                  env=child_env(root), text=True, timeout=60)
    resolved = {m: str(Path(f).resolve()) for m, f in json.loads(out).items()}
    expected = {str(Path(p).resolve()) for p in files}
    stray = {m: f for m, f in resolved.items() if f not in expected}
    if stray:
        raise ValueError('project module resolved outside verified sources: ' + json.dumps(stray))
    return resolved

def execute(command, output, cpu, wall, memory, size, env=None, cwd=None):
    start=time.monotonic()
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu))
        resource.setrlimit(resource.RLIMIT_AS,(memory,memory))
        resource.setrlimit(resource.RLIMIT_FSIZE,(size,size))
    if env is None:
        env={**os.environ,**{k:'1' for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']}}
    with open(output,'wb') as stdout, open(str(output)+'.stderr','wb') as stderr:
        p=subprocess.Popen(command,stdout=stdout,stderr=stderr,env=env,cwd=cwd,
                           preexec_fn=limits,start_new_session=True)
        timed_out=False
        while True:
            pid,status,usage=os.wait4(p.pid,os.WNOHANG)
            if pid:
                p.returncode=os.waitstatus_to_exitcode(status)
                break
            if time.monotonic()-start>=wall:
                os.killpg(p.pid,signal.SIGKILL)
                timed_out=True
                _,status,usage=os.wait4(p.pid,0)
                p.returncode=os.waitstatus_to_exitcode(status)
                break
            time.sleep(0.02)
    return {'exit_code':p.returncode,'timeout':timed_out,
            'cpu_seconds':usage.ru_utime+usage.ru_stime,
            'wall_seconds':time.monotonic()-start,'peak_rss_kib':usage.ru_maxrss}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--commit',required=True); a=ap.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    root=Path(__file__).resolve().parents[2]
    config={'cpu_seconds':300,'wall_seconds':600,'address_space_bytes':512*1024**2,
            'output_bytes':5*1024**2,'repetitions':2}
    manifest={'commit':a.commit,'config':config,'runs':[],'outcome':'INCOMPLETE'}
    package=Path(__file__).resolve().parent
    files=[root/'docs/DIMENSION_C0_PREREGISTRATION.md',package/'__init__.py',package/'c0_report.py',
           Path(__file__).resolve(),package/'dimension_c0.py',package/'dimension_d1.py',
           package/'spectral_dimension.py']
    mpath=a.output/'manifest.json'
    def save():
        mpath.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    manifest['setup']='started'
    save()  # durable INCOMPLETE record exists before any preflight can fail
    try:
        verify_sources(root,a.commit,files)
        manifest['source_sha256']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        manifest['module_resolution']=verify_resolution(root,files)
        import emergence_lab.c0_report as own_report
        if Path(own_report.__file__).resolve()!=package/'c0_report.py':
            raise ValueError('supervisor validator not loaded from verified checkout')
        verified={str(Path(p).resolve()) for p in files}
        own={m:str(Path(mod.__file__).resolve()) for m,mod in list(sys.modules.items())
             if (m=='emergence_lab' or m.startswith('emergence_lab.')) and getattr(mod,'__file__',None)}
        if any(f not in verified for f in own.values()):
            raise ValueError('supervisor loaded project module outside verified sources: '+json.dumps(own))
        manifest['config_sha256']=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
        manifest['python']=sys.version
        import importlib.metadata
        manifest['versions']={k:importlib.metadata.version(k) for k in ['numpy','scipy']}
        manifest['platform']=sys.platform
        manifest['threads']=1
    except Exception as error:  # noqa: BLE001 - every setup failure must be persisted
        manifest.update(setup='failed',setup_error=f'{type(error).__name__}: {error}',outcome='INCOMPLETE')
        save()
        print(manifest['outcome'])
        sys.exit(2)
    manifest['setup']='passed'
    save(); start=time.monotonic(); cpu=0; hashes=[]; observed_failure=False
    for i in range(2):
        left_cpu=math.floor(300-cpu-(time.process_time()))
        left_wall=600-(time.monotonic()-start)
        used=sum(p.stat().st_size for p in a.output.iterdir())
        available=5*1024**2-used-65536
        if left_cpu<1 or left_wall<=0 or available<2:
            break
        output=a.output/f'run{i+1}.json'
        run=execute([sys.executable,'-m','emergence_lab.dimension_c0'],output,
                    left_cpu,left_wall,512*1024**2,available//2,env=child_env(root),cwd=root)
        cpu+=run['cpu_seconds']
        run['sha256']=hashlib.sha256(output.read_bytes()).hexdigest()
        manifest['runs'].append(run)
        save()
        if run['exit_code']!=0: break
        try: payload=json.loads(output.read_text())
        except (ValueError,UnicodeError): break
        outcome = report_outcome(payload)
        run['report_outcome'] = outcome
        observed_failure |= outcome == 'FAIL'
        save()
        if outcome != 'PASS': break
        hashes.append(run['sha256'])
        if observed_failure: break
    complete=len(hashes)==2
    equal=complete and hashes[0]==hashes[1]
    if complete and not equal: observed_failure=True
    manifest.update(outcome='FAIL' if observed_failure else ('PASS' if equal else 'INCOMPLETE'),
                    numerical_byte_identical=equal,total_child_cpu_seconds=cpu,
                    supervisor_cpu_seconds=time.process_time(),wall_seconds=time.monotonic()-start)
    if cpu+time.process_time()>300 or manifest['wall_seconds']>600:
        if manifest['outcome']!='FAIL': manifest['outcome']='INCOMPLETE'
    save()
    manifest['output_bytes']=sum(p.stat().st_size for p in a.output.iterdir())
    save()
    print(manifest['outcome'])

if __name__=='__main__': main()

