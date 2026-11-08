"""Select exact 40-event W03 Mapper package and 45-carrier Context code for a disjoint delivery."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
INSTANCES = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances'
OLD = INSTANCES / 'legacy-local-ce4d53a6479188a5'
NEW = INSTANCES / 'legacy-local-8d0312c813444f57'
OLD_CONTEXT_SHA = '07fd3184fc4d68c955886dca2f787e8bc8f82c46b6f892e2cebdc02a09e667ec'
MAPPED_SHA = 'a156b29511f7226762cb73e8390eada3b6951bf8e813a579f0d0fe7b00741a74'
MAPPED_PACKAGE_SHA = '27a923e4a6509dcb6d19d539da99d5be0731df43b43402852c7c348b9f7fe13e'


def row(path):
    if path.is_symlink() or not path.is_file() or not path.is_relative_to(ROOT):
        raise ValueError('unselected Context input')
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    prior_path = OLD / 'context/source-manifest.json'
    mapper = NEW / 'mapped-w03-0003/source-manifest.json'
    package = NEW / 'mapped-w03-0003/packages/0001/manifest.json'
    if [row(prior_path)['sha256'], row(mapper)['sha256'], row(package)['sha256']] != [OLD_CONTEXT_SHA, MAPPED_SHA, MAPPED_PACKAGE_SHA]:
        raise ValueError('selected Context predecessor or Mapper differs')
    prior = json.loads(prior_path.read_bytes())
    selected = json.loads(mapper.read_bytes())
    package_value = json.loads(package.read_bytes())
    if package_value['source_manifest_binding'] != row(mapper):
        raise ValueError('Mapper package selects another source')
    actual_package = {p.relative_to(ROOT).as_posix() for p in package.parent.rglob('*') if p.is_file()}
    if actual_package != {item['path'] for item in package_value['files']} | {row(package)['path']}:
        raise ValueError('Mapper package closure differs')
    rows = {}
    for item in prior['files']:
        if 'legacy-local-ce4d53a6479188a5' not in item['path']:
            rows[item['path']] = item
    def add(item):
        if row(ROOT / item['path']) != item:
            raise ValueError('Context input digest differs: ' + item['path'])
        if item['path'] in rows and rows[item['path']] != item:
            raise ValueError('Context input has conflicting bindings')
        rows[item['path']] = item
    for item in selected['files']:
        add(item)
    add(row(mapper))
    for item in package_value['files']:
        add(item)
    add(row(package))
    for path in sorted((NEW / 'context-w03-0003').rglob('*')):
        if path.is_file():
            add(row(path))
    output = NEW / 'context-w03-0003/source-manifest.json'
    if output.exists():
        raise ValueError('Context selection already exists')
    value = copy.deepcopy(prior)
    value['files'] = [rows[key] for key in sorted(rows)]
    value['qualified_mapper_source_binding'] = row(mapper)
    value['qualified_mapper_package_binding'] = row(package)
    value['construction_status'] = 'construction-bound-unqualified-w03-additive'
    output.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'context_manifest_sha256': row(output)['sha256'], 'rows': len(rows)}, sort_keys=True))


if __name__ == '__main__':
    main()
