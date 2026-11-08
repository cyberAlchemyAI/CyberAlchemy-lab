"""Build the disjoint Action v7 successor for API40's exact profile selection."""
import hashlib
import json
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = INTERFACE / 'api-action-integration-v6-current-t06-0001'
NEW = INTERFACE / 'api-action-integration-v7-current-t06-0001'
OLD_SOURCE = '59c87d33d5d762ea55a80ef941002fd2beace66ed233ecb917fdc5c829de3f1a'

def sha(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('missing or linked selected input: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rel(path):
    return path.relative_to(ROOT).as_posix()

def row(path):
    return {'path': rel(path), 'sha256': sha(path)}

def load(path):
    return json.loads(path.read_bytes())

def save(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n')

def main():
    if sha(OLD / 'source-manifest.json') != OLD_SOURCE:
        raise ValueError('selected Action predecessor differs')
    dependency = NEW / 'dependencies.py'
    raw = dependency.read_text()
    old = 'api-integration-v39-current-t06-0001/contract-profile.json'
    new = 'api-integration-v40-current-t06-0001/contract-profile.json'
    if raw.count(old) != 1:
        raise ValueError('Action integration profile rebind site differs')
    dependency.write_text(raw.replace(old, new))
    old_prefix = rel(OLD) + '/'
    selection_path = NEW / 'EXECUTION-DEPENDENCIES.json'
    selection = load(selection_path)
    # The retained dependency inventory is immutable in meaning. Its one
    # current-authority re-pin was already established in Action v4.
    for selected in selection['files']:
        if sha(ROOT / selected['path']) != selected['sha256']:
            raise ValueError('selected Action dependency drift: ' + selected['path'])
    source = load(NEW / 'source-manifest.json')
    source['schema_version'] = 'lab-action-integration-v7-current-t06-source/v1-candidate'
    source['predecessor_source_manifest_binding'] = {'path': rel(OLD / 'source-manifest.json'), 'sha256': OLD_SOURCE}
    source['execution_selection_sha256'] = sha(selection_path)
    source['profile_sha256'] = sha(NEW / 'contract-profile.json')
    rows = []
    for item in source['files']:
        if item['path'].startswith(old_prefix):
            path = NEW / item['path'][len(old_prefix):]
            rows.append(row(path))
        else:
            if sha(ROOT / item['path']) != item['sha256']:
                raise ValueError('retained Action source drift: ' + item['path'])
            rows.append(item)
    source['files'] = sorted(rows, key=lambda item: item['path'])
    save(NEW / 'source-manifest.json', source)
    print(json.dumps({'action_source_sha256': sha(NEW / 'source-manifest.json'),
                      'action_profile_sha256': source['profile_sha256'],
                      'action_selection_sha256': source['execution_selection_sha256'],
                      'action_source_rows': len(source['files'])}, sort_keys=True))

if __name__ == '__main__':
    main()
