"""Reproducible static launcher over the independently selected native payload."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RECEIPT = ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/installation.json'
RECEIPT_SHA = '5821d37ce536e08c639493ceb8d165949e65cf5dd9771af5576a724082cca13b'
BOOTSTRAP = ROOT/'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/child_bootstrap.py'
FLAGS = ['-static','-std=c11','-Os','-s','-fno-ident','-Wl,--build-id=none','-Wl,-z,noexecstack','-Wall','-Wextra','-Werror']

def sha(raw): return hashlib.sha256(raw).hexdigest()

def header(bootstrap):
    raw = RECEIPT.read_bytes()
    if sha(raw) != RECEIPT_SHA: raise ValueError('selected original public installation receipt differs')
    members = json.loads(raw)['installed_files']
    if len(members) != 1010: raise ValueError('exact original1010 selected native files required')
    lines = ['/* Generated from exact independently pinned public native installation receipt. */',
             '#define NATIVE_MEMBER_COUNT 1010', '#define BOOTSTRAP_SHA256 '+json.dumps(sha(bootstrap)),
             '#define BOOTSTRAP_SIZE '+str(len(bootstrap)),
             'static const struct NativeMember { const char *name; const char *sha256; uint64_t size; int mode; } native_members[] = {']
    for name, row in sorted(members.items()):
        p = Path(name)
        if p.is_absolute() or '..' in p.parts or p.as_posix()!=name or '\\' in name or '\0' in name:
            raise ValueError('unsafe original native locator')
        lines.append('  {'+json.dumps(name)+','+json.dumps(row['sha256'])+','+str(row['size_bytes'])+','+str(row['mode'])+'},')
    return ('\n'.join([*lines, '};', ''])).encode()

def build(destination, bootstrap_raw):
    generated = header(bootstrap_raw)
    with tempfile.TemporaryDirectory(prefix='cal-static-launcher-build-') as folder:
        stage = Path(folder)
        (stage/'native_members.h').write_bytes(generated)
        (stage/'selected_python.c').write_bytes((HERE/'selected_python.c').read_bytes())
        child = subprocess.run(['cc', *FLAGS, 'selected_python.c', '-o', str(Path(destination).absolute())],
                               cwd=stage, env={**os.environ, 'SOURCE_DATE_EPOCH':'0'},capture_output=True,text=True)
        if child.returncode: raise ValueError('static compiler refused: '+child.stderr)
    return generated

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=HERE/'selected-python')
    parser.add_argument('--bootstrap', type=Path, default=BOOTSTRAP)
    args = parser.parse_args()
    generated = build(args.output, args.bootstrap.read_bytes())
    (args.output.parent/'native_members.h').write_bytes(generated)
    print(json.dumps({'result':'PASS-static-launcher-build','binary_sha256':sha(args.output.read_bytes()),
                      'generated_header_sha256':sha(generated),'native_files':1010,
                      'selected_bootstrap_sha256':sha(args.bootstrap.read_bytes()),'flags':FLAGS},sort_keys=True))
