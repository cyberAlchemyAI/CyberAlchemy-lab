"""Independent inert causal checks against the frozen public probe."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys

SOURCE = Path(__file__).resolve().parent.parent / 'context-public-policy-namespace-probe-0003'
sys.path.insert(0, str(SOURCE))
import release as R
import probe_child as C
import observer as O

def good():
    return b''.join(
        f'{i} 1 0:{i} / {target} ro,relatime - ext4 /dev/root rw\n'.encode()
        for i, target in enumerate(R.MOUNT_TARGETS, 10)
    )

def refuses(call):
    try:
        call()
    except (R.Refused, RuntimeError):
        return
    raise AssertionError('unexpected acceptance')

baseline = good()
assert R.mountinfo_ro(baseline) == C.mountinfo_ro(baseline) == R.sha(baseline)
for parser in (R.mountinfo_ro, C.mountinfo_ro):
    for target in R.MOUNT_TARGETS:
        for mode in ('ro', 'rw'):
            nested = baseline + f'99 1 0:99 / {target}/hidden {mode} - tmpfs tmpfs {mode}\n'.encode()
            refuses(lambda: parser(nested))
        escaped = baseline + f'99 1 0:99 / {target}\\057hidden ro - tmpfs tmpfs rw\n'.encode()
        refuses(lambda: parser(escaped))

def spawn(_argv, **kwargs):
    return subprocess.Popen([sys.executable, '-I', '-B', '-c',
        'import os;os.write(1,b"x"*262144);os.write(2,b"y"*262144)'], **kwargs)

refuses(lambda: R.bounded_capture([R.DOCKER, 'synthetic'], spawn=spawn, env={}, timeout=2))
assert R.EFFECT_ENABLED is False and O.EFFECT_ENABLED is False
refuses(R.execute)
refuses(O.execute)
print('independent causal checks: six targets, escaped children, bounded dual streams, effect refusals PASS')
