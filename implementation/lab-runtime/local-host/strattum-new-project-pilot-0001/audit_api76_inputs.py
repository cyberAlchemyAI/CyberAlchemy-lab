"""Read-only exact preflight of the selected API76 archive input closure."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
ARCHIVE = ROOT / 'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/archive.py'
spec = importlib.util.spec_from_file_location('cal_static_archive_audit', ARCHIVE)
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def audit(view):
    view = Path(view).resolve()
    raw = (view / 'PACKAGE-MANIFEST.json').read_bytes()
    manifest = json.loads(raw)
    inputs_raw = (view / 'BUILD-INPUTS.json').read_bytes()
    inputs = json.loads(inputs_raw)
    if sha(raw) != inputs['package_manifest_sha256']:
        raise ValueError('selected package manifest differs')
    rows = A.entries(manifest)
    counts = {'repository': 0, 'host': 0, 'native': 0}
    bytes_read = 0
    for name, row in rows.items():
        if name == 'PACKAGE-MANIFEST.json':
            continue
        if name.startswith('repository/'):
            source = inputs['repository_inputs'][name[len('repository/'):]]['input_path']
            kind = 'repository'
        elif name.startswith('host-inputs/'):
            source = inputs['host_inputs']['/' + name[len('host-inputs/'):]]['input_path']
            kind = 'host'
        else:
            source = str(Path(inputs['native_payload_root']) / name[len('native-payload/'):])
            kind = 'native'
        body = A.M.exact(source, row)
        counts[kind] += 1
        bytes_read += len(body)
    if sha((view / 'PACKAGE-MANIFEST.json').read_bytes()) != sha(raw) or sha((view / 'BUILD-INPUTS.json').read_bytes()) != sha(inputs_raw):
        raise ValueError('selected build inputs changed during audit')
    return {'schema_version': 'lab-api76-static-archive-input-audit/v1',
            'result': 'PASS-exact-inputs-before-archive',
            'package_manifest_sha256': sha(raw), 'build_inputs_sha256': sha(inputs_raw),
            'file_counts': counts, 'selected_bytes_read': bytes_read,
            'archive_written': False, 'installed_API_qualified': False,
            'authority_effect': 'none'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('view', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.view), sort_keys=True), flush=True)
