#!/usr/bin/env python3
"""Read-only exact delivery integrity check; no proof or admission effect."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check():
    manifest = json.loads((HERE / 'manifest.json').read_text())
    expected = {r['path']: r for r in manifest['files']}
    if len(expected) != len(manifest['files']):
        raise ValueError('Duplicate delivery path')
    actual = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != 'manifest.json'}
    if actual != set(expected):
        raise ValueError('Delivery inventory mismatch')
    for relative, row in expected.items():
        path = (HERE / relative).resolve()
        if not path.is_relative_to(HERE) or path.stat().st_size != row['size_bytes'] or sha(path) != row['sha256']:
            raise ValueError('Changed delivery file: ' + relative)
    receipt = json.loads((HERE / 'planning-validation.json').read_text())
    for filename, field in [('dag.json','dag_sha256'), ('swu-manifest.json','swu_manifest_sha256'), ('check_plan.py','validator_sha256')]:
        if sha(HERE / filename) != receipt[field]:
            raise ValueError('Validation binding mismatch: ' + filename)
    pilot = HERE.parent / 'd0-d2-v1'
    prior = json.loads((pilot / 'manifest.json').read_text())
    for row in prior['files']:
        path = pilot / row['path']
        if path.stat().st_size != row['size_bytes'] or sha(path) != row['sha256']:
            raise ValueError('Prior pilot changed: ' + row['path'])
    return {'result':'PASS', 'delivery_files':len(expected), 'prior_pilot_files_preserved':len(prior['files']), 'authority_effect':'none', 'meaning':'Exact delivery integrity and prior pilot preservation; no implementation or formal assurance claim.'}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
