"""Capture local compiler/linker inputs; no installation or qualification claim."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

R = Path('/home/vlad_/projects/CyberAlchemy-lab')
S = R / 'implementation/lab-runtime/candidates/runtime-completion-0001'
E = R / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U02-01'
PREFIX = E.parent / 'LC-U01-02/python-bytecode-cache-disabled-0002'


def record(path):
    path = Path(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > 1024 ** 3:
            raise ValueError('tool input type/size')
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        after = os.fstat(stream.fileno())
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError('tool input drift')
        return {'path': str(path), 'sha256': digest, 'size_bytes': before.st_size}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.parent != E or not args.out.name.startswith('toolchain-inputs-'):
        raise ValueError('exclusive unit evidence path required')
    if record(PREFIX)['sha256'] != 'a5712f1655f68e6f8fe7cacbfb454dc0be0cd1ad8f22f1788fbad7b8adafae29':
        raise ValueError('cache prefix changed')
    if os.environ.get('PYTHONPYCACHEPREFIX') != str(PREFIX) or not sys.flags.no_site or not sys.dont_write_bytecode:
        raise ValueError('guarded Python required')
    baseline = S / 'control/baseline.json'
    fd = os.open(baseline, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        st = os.fstat(stream.fileno())
        if not stat.S_ISREG(st.st_mode) or st.st_size > 16 * 1024 * 1024:
            raise ValueError('baseline type/size')
        raw = stream.read(16 * 1024 * 1024 + 1)
        if hashlib.sha256(raw).hexdigest() != 'e3541b1f668375686b0c9e6c871acbeb1258830a1ac5ee84f025efd976343b3d':
            raise ValueError('baseline changed')
    b = json.loads(raw)['toolchain']
    tools = {name: Path(b[name]['actual_binary']['path']) for name in ('cargo', 'rustc')}
    tools['gcc'] = Path(b['gcc']['resolved_path'])
    for name in ('cargo', 'rustc'):
        if record(tools[name])['sha256'] != b[name]['actual_binary']['sha256']:
            raise ValueError('compiler changed')
    if record(tools['gcc'])['sha256'] != b['gcc']['sha256']:
        raise ValueError('linker wrapper changed')
    locators = {}
    def add(path):
        p = Path(path)
        resolved = p.resolve(strict=True)
        locators[str(p)] = str(resolved)
        return resolved
    for path in tools.values(): add(path)
    for name in ('sh', 'readlink', 'dirname', 'basename', 'ldd', 'x86_64-linux-gnu-ld'):
        add(Path('/usr/bin') / name)
    root = tools['gcc'].parent.parent
    add(root / 'sysroot/usr/bin/x86_64-linux-gnu-gcc-15')
    env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}
    observations = []
    def command(argv, selected_env):
        p = subprocess.run([str(a) for a in argv], env=selected_env, capture_output=True, timeout=10, check=True)
        if len(p.stdout) + len(p.stderr) > 1048576:
            raise ValueError('tool observation output bound')
        observations.append({'argv': [str(a) for a in argv], 'environment': selected_env,
                             'stdout': p.stdout.decode(), 'stderr': p.stderr.decode()})
        return p.stdout.decode()
    for name in ('cc1', 'collect2', 'ld', 'as'):
        output = command([tools['gcc'], '-print-prog-name=' + name], env).strip()
        add(output if output.startswith('/') else '/usr/bin/' + output)
    missing = []
    for name in ('crt1.o', 'Scrt1.o', 'crti.o', 'crtn.o', 'crtbeginS.o', 'crtendS.o',
                 'libgcc.a', 'libgcc_s.so', 'libc.so', 'libc_nonshared.a', 'libm.so',
                 'libmvec.so', 'libpthread.a', 'libdl.a', 'librt.a'):
        output = command([tools['gcc'], '-print-file-name=' + name], env).strip()
        if output.startswith('/'):
            add(output)
        else:
            missing.append(name)
    rustlib = tools['rustc'].parent.parent / 'lib'
    for p in sorted(rustlib.rglob('*')):
        if p.is_file() and (p.suffix in ('.so', '.rlib', '.rmeta', '.a', '.o') or '.so.' in p.name or p.name.startswith('libLLVM.so')):
            add(p)
    binaries = [tools['cargo'], tools['rustc'], root / 'sysroot/usr/bin/x86_64-linux-gnu-gcc-15',
                root / 'sysroot/usr/libexec/gcc/x86_64-linux-gnu/15/cc1',
                root / 'sysroot/usr/libexec/gcc/x86_64-linux-gnu/15/collect2', Path('/usr/bin/x86_64-linux-gnu-ld')]
    for p in binaries:
        selected_env = dict(env)
        if p.is_relative_to(root):
            selected_env['LD_LIBRARY_PATH'] = str(root / 'sysroot/usr/lib/x86_64-linux-gnu')
        output = command(['/usr/bin/ldd', p], selected_env)
        if 'not found' in output:
            raise ValueError('unresolved runtime library')
        for name in re.findall(r'(/[^\s()]+)', output): add(name)
    rows = [record(path) for path in sorted(set(locators.values()))]
    value = {'schema_version': 'lab-broker-local-toolchain-inputs/v1', 'files': rows,
        'locators': [{'path': p, 'resolved_path': r} for p, r in sorted(locators.items())],
        'observations': observations, 'unavailable_linker_names': missing,
        'platform': {'sysname': os.uname().sysname, 'release': os.uname().release, 'machine': os.uname().machine},
        'claim_ceiling': 'Selected local compiler, standard libraries, observed linker/runtime dependencies; no deployed host custody or reproducible cross-platform binary claim.',
        'authority_effect': 'none'}
    raw = (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()
    with args.out.open('xb') as out:
        out.write(raw);out.flush();os.fsync(out.fileno())
    print(json.dumps({'path': str(args.out), 'sha256': hashlib.sha256(raw).hexdigest(), 'files': len(rows)}))


if __name__ == '__main__': main()
