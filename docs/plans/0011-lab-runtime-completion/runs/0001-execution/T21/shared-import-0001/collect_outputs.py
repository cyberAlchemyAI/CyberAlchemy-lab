"""Collect exact importer writes in memory; do not mutate shared documentation."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import stat
import sys

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = Path(__file__).resolve().parent
DEST = ROOT / 'docs/lab'
SCRIPT = ROOT / 'tooling/docs/import_site_docs.py'
virtual = {}
modes = {}
original = {name: getattr(Path, name) for name in ('write_text', 'mkdir', 'read_bytes', 'read_text')}
copy2 = shutil.copy2

def owned(path):
    path = Path(os.path.abspath(path))
    if not path.is_relative_to(DEST):
        raise ValueError(f'Unexpected importer write outside docs/lab: {path}')
    if path.is_symlink():
        raise ValueError(f'Symlink output: {path}')
    return path

def write_text(path, data, encoding=None, errors=None, newline=None):
    path = owned(path)
    raw = data.encode(encoding or 'utf-8', errors or 'strict')
    virtual[path] = raw
    modes[path] = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    return len(data)

def mkdir(path, *args, **kwargs):
    owned(path)

def copy(source, target, *args, **kwargs):
    target = owned(target)
    virtual[target] = original['read_bytes'](Path(source))
    modes[target] = stat.S_IMODE(Path(source).stat().st_mode)
    return str(target)

def read_bytes(path):
    return virtual[path] if path in virtual else original['read_bytes'](path)

def read_text(path, encoding=None, errors=None):
    return virtual[path].decode(encoding or 'utf-8', errors or 'strict') if path in virtual else original['read_text'](path, encoding=encoding, errors=errors)

raw = SCRIPT.read_bytes()
namespace = {'__name__': 'passive_import_selection', '__file__': str(SCRIPT)}
exec(compile(raw, str(SCRIPT), 'exec'), namespace)
prior_argv = sys.argv
stdout = io.StringIO()
try:
    Path.write_text, Path.mkdir = write_text, mkdir
    Path.read_bytes, Path.read_text = read_bytes, read_text
    shutil.copy2 = copy
    sys.argv = [str(SCRIPT), '--site', str(ROOT / 'website/dist/governance-lab-series'), '--repo', str(ROOT), '--imported-on', '2026-10-14']
    with contextlib.redirect_stdout(stdout):
        namespace['main']()
finally:
    for name, method in original.items():
        setattr(Path, name, method)
    shutil.copy2 = copy2
    sys.argv = prior_argv

rows = []
for path, body in sorted(virtual.items()):
    existed = path.exists()
    before = path.read_bytes() if existed else None
    rows.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body), 'mode': modes[path], 'preimage_sha256': hashlib.sha256(before).hexdigest() if before is not None else None, 'preimage_mode': stat.S_IMODE(path.stat().st_mode) if existed else None})
manifest = json.loads(virtual[DEST / 'IMPORT-MANIFEST.json'])
selection = {'schema_version': 'lab-T21-exact-import-output-selection/v1-candidate', 'authority_effect': 'none', 'shared_writes': False, 'importer_sha256': hashlib.sha256(raw).hexdigest(), 'imported_on': '2026-10-14', 'files': rows, 'summary': json.loads(stdout.getvalue()), 'source_comparison_counts': manifest['source_comparison_counts']}
target = BASE / 'output-selection.json'
with target.open('x', encoding='utf-8') as stream:
    stream.write(json.dumps(selection, indent=2) + '\n')
print(json.dumps({'selection': str(target), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'files': len(rows), 'existing': sum(r['preimage_sha256'] is not None for r in rows), 'pages': len(manifest['pages']), 'assets': len(manifest['assets']), 'comparisons': manifest['source_comparison_counts'], 'shared_writes': False}))
