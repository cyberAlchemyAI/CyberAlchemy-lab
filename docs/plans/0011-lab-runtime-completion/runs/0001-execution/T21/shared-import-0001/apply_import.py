"""Preserve exact importer preimages, run reviewed importer, verify scope."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = Path(__file__).resolve().parent
DEST = ROOT / 'docs/lab'
SELECTION = BASE / 'output-selection.json'
digest = lambda raw: hashlib.sha256(raw).hexdigest()
if digest(SELECTION.read_bytes()) != 'a74e4a4d25138c7f29d6872f9cbd6475f489c2f66220aeddeaaf90604d1c2f36':
    raise ValueError('Output selection changed')
selected = json.loads(SELECTION.read_bytes())
script = ROOT / 'tooling/docs/import_site_docs.py'
if digest(script.read_bytes()) != selected['importer_sha256']:
    raise ValueError('Importer changed')

def snapshot():
    result = {}
    for path in sorted(DEST.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Symlink documentation input: {path}')
        if path.is_file():
            result[path.relative_to(ROOT).as_posix()] = {'sha256': digest(path.read_bytes()), 'mode': stat.S_IMODE(path.stat().st_mode)}
    return result

before = snapshot()
backup = BASE / 'preimages'
backup.mkdir(mode=0o700)
for row in selected['files']:
    path = ROOT / row['path']
    if not path.is_relative_to(DEST):
        raise ValueError('Output outside docs/lab')
    expected = None if row['preimage_sha256'] is None else {'sha256': row['preimage_sha256'], 'mode': row['preimage_mode']}
    if before.get(row['path']) != expected:
        raise ValueError(f'Preimage changed: {row["path"]}')
    if expected is not None:
        body = path.read_bytes()
        target = backup / row['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        target.chmod(row['preimage_mode'])
        if digest(target.read_bytes()) != row['preimage_sha256']:
            raise ValueError('Backup mismatch')
preserved = {'schema_version': 'lab-T21-import-preservation/v1-candidate', 'authority_effect': 'none', 'selection_sha256': digest(SELECTION.read_bytes()), 'existing_outputs': sum(r['preimage_sha256'] is not None for r in selected['files']), 'preimport_snapshot': before}
with (BASE / 'preservation-receipt.json').open('x') as stream:
    stream.write(json.dumps(preserved, indent=2) + '\n')
    stream.flush()
    os.fsync(stream.fileno())
with (BASE / 'terminal.log').open('x') as stream:
    process = subprocess.run([sys.executable, '-B', str(script), '--site', str(ROOT / 'website/dist/governance-lab-series'), '--repo', str(ROOT), '--imported-on', selected['imported_on']], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
if process.returncode != 0:
    raise ValueError(f'Importer failed: {process.returncode}; preserved partial writes for review')
after = snapshot()
outputs = {r['path']: {'sha256': r['sha256'], 'mode': r['mode']} for r in selected['files']}
for path, expected in outputs.items():
    if after.get(path) != expected:
        raise ValueError(f'Output mismatch: {path}')
for path, expected in before.items():
    if path not in outputs and after.get(path) != expected:
        raise ValueError(f'Unselected documentation changed: {path}')
if set(after) != set(before) | set(outputs):
    raise ValueError('Unselected new documentation output')
receipt = {'schema_version': 'lab-T21-actual-import/v1-candidate', 'result': 'PASS', 'authority_effect': 'none', 'selection_sha256': digest(SELECTION.read_bytes()), 'preservation_receipt_sha256': digest((BASE / 'preservation-receipt.json').read_bytes()), 'terminal_sha256': digest((BASE / 'terminal.log').read_bytes()), 'files_verified': len(outputs), 'unchanged_unselected_files': len(set(before)-set(outputs)), 'pages': selected['summary']['pages'], 'assets': selected['summary']['assets'], 'source_comparison_counts': selected['source_comparison_counts'], 'runtime_execution': False, 'deployment_performed': False}
target = BASE / 'application-receipt.json'
with target.open('x') as stream:
    stream.write(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'result': 'PASS', 'receipt': str(target), 'sha256': digest(target.read_bytes()), 'files': len(outputs), 'pages': receipt['pages'], 'assets': receipt['assets'], 'unselected_unchanged': receipt['unchanged_unselected_files']}))
