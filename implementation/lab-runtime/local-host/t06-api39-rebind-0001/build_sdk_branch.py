"""Rebind exact disjoint SDK and branch constructor bytes to API39."""
import hashlib
import json
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD_SDK = INTERFACE / 'composite-operator-v1-current-api38-0001/revision-0001'
SDK = INTERFACE / 'composite-operator-v1-current-api39-0001/revision-0001'
OLD_BRANCH = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api38-0001/revision-0001'
BRANCH = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api39-0001/revision-0001'
OLD_SDK_SHA = '4da6dc3db086ffb4d74abaa8f364c3579c7acdbf72afbb7f7e54b4e5c169847b'
OLD_BRANCH_SHA = 'bfdc80f119d415ba243ff1fe72c0870f33d3406eb3446a39f86a1bb408a73967'

def sha(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('missing or linked selected path: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rel(path):
    return path.relative_to(ROOT).as_posix()

def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n')

def rebind(root, originals, replacements):
    for path in sorted(root.glob('*.py')):
        raw = path.read_text()
        for old, new in replacements:
            raw = raw.replace(old, new)
        path.write_text(raw)

def manifest(new, old, filename, old_sha, schema):
    if sha(old / filename) != old_sha:
        raise ValueError('selected predecessor manifest drift')
    path = new / filename
    value = json.loads(path.read_bytes())
    value['schema_version'] = schema
    key = 'historical_sdk_binding' if filename == 'source-manifest.json' else 'predecessor_binding'
    value[key] = {'path': rel(old / filename), 'sha256': old_sha}
    old_prefix = rel(old) + '/'
    new_prefix = rel(new) + '/'
    rows = []
    for item in value['files']:
        if item['path'].startswith(old_prefix):
            selected = new / item['path'][len(old_prefix):]
            updated = {'path': rel(selected), 'sha256': sha(selected)}
            if 'size_bytes' in item:
                updated['size_bytes'] = selected.stat().st_size
            rows.append(updated)
        elif item['path'].startswith(new_prefix):
            selected = ROOT / item['path']
            updated = {'path': item['path'], 'sha256': sha(selected)}
            if filename == 'source-manifest.json' or 'size_bytes' in item:
                updated['size_bytes'] = selected.stat().st_size
            rows.append(updated)
        else:
            if sha(ROOT / item['path']) != item['sha256']:
                raise ValueError('retained external source drift: ' + item['path'])
            rows.append(item)
    value['files'] = sorted(rows, key=lambda item: item['path'])
    write(path, value)
    return sha(path)

def main():
    rebind(SDK, OLD_SDK, [
        ('api-integration-v38-current-t06-0001', 'api-integration-v39-current-t06-0001'),
        ('branch-fixtures-current-api38-0001', 'branch-fixtures-current-api39-0001'),
        ('lab-T06-current-api38-sdk-source/v1-candidate', 'lab-T06-current-api39-sdk-source/v1-candidate'),
        ('API38', 'API39')])
    rebind(BRANCH, OLD_BRANCH, [
        ('api-integration-v38-current-t06-0001', 'api-integration-v39-current-t06-0001'),
        ('composite-operator-v1-current-api38-0001', 'composite-operator-v1-current-api39-0001'),
        ('API38', 'API39')])
    sdk_sha = manifest(SDK, OLD_SDK, 'source-manifest.json', OLD_SDK_SHA,
                       'lab-T06-current-api39-sdk-source/v1-candidate')
    branch_sha = manifest(BRANCH, OLD_BRANCH, 'driver-selection.json', OLD_BRANCH_SHA,
                          'lab-T06-current-api39-branch-driver-selection/v1-candidate')
    print(json.dumps({'sdk_manifest_sha256': sdk_sha,
                      'branch_selection_sha256': branch_sha}, sort_keys=True))

if __name__ == '__main__':
    main()
