"""Disposable real-Docker engineering probes; never generate CS0 orders/seeds."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid


def run(image: str, output: Path):
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', image):
        raise ValueError('an immutable image ID is required')
    if os.environ.get('CS0_HOST_CLASS') != 'non-lightsail':
        raise ValueError('verified non-Lightsail host required')
    if output.exists():
        raise ValueError('refusing existing probe record')
    record = dict(outcome='INCOMPLETE', study_authorized=False, image=image, probes=[])
    def save():
        temporary = output.with_suffix('.tmp')
        with temporary.open('w') as stream:
            json.dump(record, stream, sort_keys=True, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
        fd = os.open(output.parent, os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    save()
    flags = ['--log-driver', 'none', '--network', 'none', '--cpus', '1',
             '--memory', '1g', '--memory-swap', '1g', '--read-only',
             '--pids-limit', '64', '--cap-drop', 'ALL',
             '--security-opt', 'no-new-privileges',
             '--user', f'{os.getuid()}:{os.getgid()}',
             '--tmpfs', '/tmp:rw,noexec,nosuid,size=64m']
    cases = [
        ('limits', '5s', 'import json,pathlib; p=pathlib.Path("/sys/fs/cgroup"); '
         'print(json.dumps({n:(p/n).read_text().strip() for n in '
         '["cpu.max","memory.max","memory.swap.max","pids.max"]}))'),
        ('timeout', '1s', 'import subprocess,sys,time; '
         'subprocess.Popen([sys.executable,"-c","import time; time.sleep(20)"]); time.sleep(20)'),
        ('oom', '20s', 'x=bytearray(2*1024**3)'),
    ]
    try:
        for label, deadline, code in cases:
            name = 'cs0-probe-' + uuid.uuid4().hex
            item = dict(name=label, container=name, outcome='INCOMPLETE')
            record['probes'].append(item)
            save()
            try:
                started = time.monotonic()
                process = subprocess.run(['docker', 'run', '--name', name, *flags,
                    '--entrypoint', 'timeout', image, '--signal=KILL', deadline,
                    'python', '-I', '-B', '-c', code], capture_output=True,
                    text=True, timeout=45)
                item['wall_seconds'] = time.monotonic() - started
                inspected = subprocess.run(['docker', 'inspect', name],
                    capture_output=True, text=True, timeout=10, check=True)
                state = json.loads(inspected.stdout)[0]['State']
                item.update(exit_code=process.returncode, oom_killed=state['OOMKilled'],
                            running=state['Running'])
                if state['Running']:
                    raise ValueError(f'{label}: container still running')
                if label == 'limits':
                    if process.returncode != 0:
                        raise ValueError('cgroup read failed: ' + process.stderr[:1000])
                    limits = json.loads(process.stdout)
                    item['limits'] = limits
                    quota, period = map(int, limits['cpu.max'].split())
                    if not (quota == period and quota > 0
                            and int(limits['memory.max']) == 1024**3
                            and int(limits['memory.swap.max']) == 0
                            and int(limits['pids.max']) == 64):
                        raise ValueError('unexpected cgroup v2 limits')
                elif label == 'timeout':
                    if (process.returncode != 137 or state['OOMKilled']
                            or item['wall_seconds'] >= 15):
                        raise ValueError('timeout did not kill the namespace as expected')
                elif process.returncode != 137 or not state['OOMKilled']:
                    raise ValueError('OOM was not confirmed by Docker state')
                item['outcome'] = 'PASS'
            finally:
                cleanup = subprocess.run(['docker', 'rm', '-f', name],
                    capture_output=True, text=True, timeout=10)
                item['removed'] = cleanup.returncode == 0
                save()
                if not item['removed']:
                    raise ValueError(f'probe container cleanup failed: {name}')
        record['outcome'] = 'ENGINEERING_COMPLETE'
    except Exception as error:
        record['error'] = f'{type(error).__name__}: {error}'
    finally:
        save()
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image')
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = run(args.image, args.output)
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result['outcome'] == 'ENGINEERING_COMPLETE' else 2)
