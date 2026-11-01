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

def execute(command, output, cpu, wall, memory, size):
    start=time.monotonic()
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu))
        resource.setrlimit(resource.RLIMIT_AS,(memory,memory))
        resource.setrlimit(resource.RLIMIT_FSIZE,(size,size))
    env={**os.environ,**{k:'1' for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']}}
    with open(output,'wb') as stdout, open(str(output)+'.stderr','wb') as stderr:
        p=subprocess.Popen(command,stdout=stdout,stderr=stderr,env=env,
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
    files=[root/'docs/DIMENSION_C0_PREREGISTRATION.md',Path(__file__),
           Path(__file__).with_name('dimension_c0.py'),Path(__file__).with_name('dimension_d1.py'),
           Path(__file__).with_name('spectral_dimension.py')]
    manifest['source_sha256']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    manifest['config_sha256']=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
    manifest['python']=sys.version
    import importlib.metadata
    manifest['versions']={k:importlib.metadata.version(k) for k in ['numpy','scipy']}
    manifest['platform']=sys.platform
    manifest['threads']=1
    mpath=a.output/'manifest.json'
    def save():
        mpath.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
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
                    left_cpu,left_wall,512*1024**2,available//2)
        cpu+=run['cpu_seconds']
        run['sha256']=hashlib.sha256(output.read_bytes()).hexdigest()
        manifest['runs'].append(run)
        save()
        if run['exit_code']!=0: break
        try: payload=json.loads(output.read_text())
        except (ValueError,UnicodeError): break
        observed_failure |= payload.get('outcome')=='FAIL'
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
