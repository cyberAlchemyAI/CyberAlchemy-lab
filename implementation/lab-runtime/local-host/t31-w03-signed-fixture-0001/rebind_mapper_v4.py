"""Select exact signed W03 Source and Reader for the native mapper."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
INSTANCES = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances'
OLD = INSTANCES / 'legacy-local-ce4d53a6479188a5'
NEW = INSTANCES / 'legacy-local-8d0312c813444f57'
OLD_MAPPER_SHA = 'fa05a8638d49ba8f27df4b6ffdf2dae00868ff4d7ac3946d2785f5bbfe771b02'
SOURCE_SHA = '14639c94bd192ebbaf0f34524e588bf7b09ea75616e2b10bbe53df98695833d6'
READER_SHA = '0cd65a9e171dd5e41afe719b52ad61fef7c7365491df1b31f9d594c7b2824081'
PACKAGE_SHA = 'b78fe83c69e40457b891550540873c62a53294d671d7622807d2129600766d27'


def row(path):
    if path.is_symlink() or not path.is_file() or not path.is_relative_to(ROOT):
        raise ValueError('unselected mapper input')
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    prior_path = OLD / 'mapped/source-manifest.json'
    if row(prior_path)['sha256'] != OLD_MAPPER_SHA:
        raise ValueError('original mapper manifest differs')
    source = NEW / 'source/source-manifest.json'
    package = NEW / 'source/packages/0001/manifest.json'
    adapter = NEW / 'reader-w03-0002/source-manifest.json'
    if [row(source)['sha256'], row(package)['sha256'], row(adapter)['sha256']] != [SOURCE_SHA, PACKAGE_SHA, READER_SHA]:
        raise ValueError('signed W03 source, package or Reader differs')
    prior = json.loads(prior_path.read_bytes())
    reader = json.loads(adapter.read_bytes())
    if reader['producer_source_binding'] != row(source) or reader['producer_package_binding'] != row(package):
        raise ValueError('Reader selects another signed Source')
    rows = {}
    for item in prior['files']:
        if 'legacy-local-ce4d53a6479188a5' not in item['path']:
            rows[item['path']] = item
    for item in reader['files']:
        path = ROOT / item['path']
        if row(path) != item:
            raise ValueError('Reader manifest closure differs')
        rows[item['path']] = item
    rows[row(adapter)['path']] = row(adapter)
    for path in sorted((NEW / 'mapped-w03-0004').glob('*.py')) + [NEW / 'mapped-w03-0004/policy.json']:
        item = row(path)
        rows[item['path']] = item
    value = copy.deepcopy(prior)
    value['files'] = [rows[key] for key in sorted(rows)]
    value['original_source_binding'] = row(source)
    value['original_package_binding'] = row(package)
    value['adapter_source_binding'] = row(adapter)
    value['construction_status'] = 'construction-bound-unqualified-w03-additive'
    output = NEW / 'mapped-w03-0004/source-manifest.json'
    if output.exists():
        raise ValueError('mapper selection already exists')
    output.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'mapper_manifest_sha256': row(output)['sha256'], 'rows': len(rows)}, sort_keys=True))


if __name__ == '__main__':
    main()
