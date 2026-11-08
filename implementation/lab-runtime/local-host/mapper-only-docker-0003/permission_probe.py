"""One-shot synthetic Docker identity/mount observation; no project input is mounted."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess

import construct

PROBE = Path('/tmp/cal-mapper-permission-probe-20261020-0003')
NAME = 'cal-mapper-permission-probe-20261020-0003'
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'


def write(path: Path, content: bytes, mode: int) -> None:
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def run_once() -> dict:
    construct.require(not os.path.lexists(PROBE), 'synthetic probe already consumed')
    os.mkdir(PROBE, 0o700)
    root = PROBE / 'root'
    root.mkdir(mode=0o755)
    source = root / construct.SOURCE / 'packages/0001'
    reader = root / construct.READER
    mapper = root / construct.NEW / 'packages'
    for target, mode in ((source, 0o700), (reader, 0o755), (mapper, 0o700)):
        target.mkdir(parents=True, exist_ok=False)
        os.chmod(target, mode)
    write(source / 'branch.snapshot', b'SYNTHETIC-PERMISSION-PROBE\n', 0o600)
    write(reader / 'reader.py', b'# synthetic reader placeholder\n', 0o444)
    input_dir = PROBE / 'input'
    input_dir.mkdir(mode=0o700)
    write(input_dir / 'lab-context-native-reader', b'synthetic native placeholder\n', 0o444)
    code = '''import json,os,tempfile
from pathlib import Path
root=Path('/workspace')
archive=root/'product/lab/release-candidates/v1/interface/docker-source-20261020-0001/packages/0001/branch.snapshot'
reader=root/'product/lab/release-candidates/v1/interface/docker-reader-20261020-0001/reader.py'
out=root/'product/lab/release-candidates/v1/interface/docker-mapped-20261020-0001/packages/receipt.txt'
assert os.getuid()==os.getgid()==1000
assert archive.read_bytes()==b'SYNTHETIC-PERMISSION-PROBE\\n'
assert reader.read_bytes()==b'# synthetic reader placeholder\\n'
out.write_bytes(b'SYNTHETIC-OUTPUT\\n')
with tempfile.TemporaryDirectory(dir='/attempt/scratch') as name:
 p=Path(name)/'input.json';p.write_bytes(b'{}\\n');assert p.read_bytes()==b'{}\\n'
print(json.dumps({'uid':os.getuid(),'gid':os.getgid(),'archive_read':True,'reader_read':True,'package_write':True,'scratch_write':True,'tmpdir':os.environ.get('TMPDIR')},sort_keys=True))
'''
    argv = ['docker', 'run', '--rm', '--name', NAME, '--user', '1000:1000',
            '--userns', 'host', '--network', 'none', '--read-only',
            '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges:true',
            '--pids-limit', '16', '--memory', '1g', '-e', 'TMPDIR=/attempt/scratch',
            '--mount', f'type=bind,src={root},dst=/workspace,readonly',
            '--mount', f'type=bind,src={mapper},dst=/workspace/{construct.NEW}/packages',
            '--mount', f'type=bind,src={input_dir},dst=/attempt/input,readonly',
            '--tmpfs', '/attempt/scratch:rw,nosuid,nodev,size=512m,mode=0700,uid=1000,gid=1000',
            '--entrypoint', 'python', IMAGE, '-c', code]
    try:
        result = subprocess.run(argv, capture_output=True, timeout=25)
        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode
        timeout = False
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout or b''
        stderr = error.stderr or b''
        exit_code = None
        timeout = True
    ps = subprocess.run(['docker', 'ps', '-a', '--filter', f'name=^{NAME}$',
                         '--format', '{{.ID}}'], capture_output=True, timeout=10)
    observed = None
    if exit_code == 0 and not stderr and len(stdout.splitlines()) == 1:
        observed = json.loads(stdout)
    expected = {'uid': 1000, 'gid': 1000, 'archive_read': True,
                'reader_read': True, 'package_write': True, 'scratch_write': True,
                'tmpdir': '/attempt/scratch'}
    output = mapper / 'receipt.txt'
    overall = ('PASS_SYNTHETIC_ACCESS' if not timeout and exit_code == 0 and
               observed == expected and ps.returncode == 0 and not ps.stdout.strip() and
               output.is_file() and output.read_bytes() == b'SYNTHETIC-OUTPUT\n'
               else 'UNKNOWN_SYNTHETIC_ACCESS')
    receipt = {'schema_version': 'lab-mapper-synthetic-permission-probe/v1',
               'overall': overall, 'image': IMAGE, 'effective_user': '1000:1000',
               'userns': 'host', 'docker_exit': exit_code,
               'timeout': timeout, 'container_absent': ps.returncode == 0 and not ps.stdout.strip(),
               'observed': observed,
               'stdout_sha256': hashlib.sha256(stdout).hexdigest(),
               'stderr_sha256': hashlib.sha256(stderr).hexdigest(),
               'synthetic_only': True, 'no_private_archive_body': True,
               'no_mapper_or_reader_effect': True}
    write(PROBE / 'receipt.json', construct.canonical(receipt), 0o600)
    print(json.dumps(receipt, sort_keys=True))
    return receipt


if __name__ == '__main__':
    result = run_once()
    raise SystemExit(0 if result['overall'] == 'PASS_SYNTHETIC_ACCESS' else 2)
