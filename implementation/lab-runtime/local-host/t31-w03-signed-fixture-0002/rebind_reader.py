"""Derive a disjoint Reader selection after the signed W03 Source is frozen."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
INSTANCES = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances'
OLD = INSTANCES / 'legacy-local-ce4d53a6479188a5'
NEW = INSTANCES / 'legacy-local-62f4c217e8b9a30d'
SOURCE_SHA = '69967b19d3bb170885c28542f36b66a1a4ed8a3936abcd1850f64c44d19ac3b1'
OLD_READER_SHA = 'b3461a1e68a5da06ad6c47966eb4ed448e67f2318baf5e7e956937d15f007877'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row(path):
    if path.is_symlink() or not path.is_file() or not path.is_relative_to(ROOT):
        raise ValueError('unselected Reader closure member')
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def main():
    old = OLD / 'reader/source-manifest.json'
    source = NEW / 'source/source-manifest.json'
    package = NEW / 'source/packages/0001/manifest.json'
    output = NEW / 'reader-w03-0002/source-manifest.json'
    if output.exists():
        raise ValueError('Reader selection already exists')
    if sha(old) != OLD_READER_SHA or sha(source) != SOURCE_SHA:
        raise ValueError('selected predecessor or W03 Source bytes changed')
    prior = json.loads(old.read_bytes())
    selected = json.loads(source.read_bytes())
    package_value = json.loads(package.read_bytes())
    if package_value['source_manifest_binding'] != row(source):
        raise ValueError('signed Source package selects another W03 Source')
    package_files = {item['path']: item['sha256'] for item in package_value['files']}
    actual = {str(path.relative_to(ROOT)) for path in package.parent.rglob('*') if path.is_file()}
    if actual != set(package_files) | {str(package.relative_to(ROOT))}:
        raise ValueError('signed Source package file closure differs')
    rows = {}
    def add(item):
        path = ROOT / item['path']
        if row(path) != item:
            raise ValueError('Reader closure member digest differs: ' + item['path'])
        previous = rows.setdefault(item['path'], item)
        if previous != item:
            raise ValueError('Reader closure has conflicting path')
    for item in prior['files']:
        if 'legacy-local-ce4d53a6479188a5' not in item['path']:
            add(item)
    for item in selected['files']:
        add(item)
    add(row(source))
    for item in package_value['files']:
        add(item)
    add(row(package))
    for path in sorted((NEW / 'reader-w03-0002').glob('*.py')):
        add(row(path))
    result = copy.deepcopy(prior)
    result['files'] = [rows[name] for name in sorted(rows)]
    result['producer_source_binding'] = row(source)
    result['producer_package_binding'] = row(package)
    result['implementation_entrypoint_ref'] = str((NEW / 'reader-w03-0002/reader.py').relative_to(ROOT)) + '#SelectedReader.open_signed'
    result['construction_status'] = 'construction-bound-unqualified-w03-reader-v2-exact-entrypoint'
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'reader_manifest_sha256': sha(output), 'rows': len(rows),
                      'producer_package_sha256': sha(package)}, sort_keys=True))


if __name__ == '__main__':
    main()
