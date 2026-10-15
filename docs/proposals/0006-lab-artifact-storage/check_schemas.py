#!/usr/bin/env python3
"""Validate proposed schema authoring only; create no persistent runtime database."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import sqlite3

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECEIPT = HERE / 'receipts/schema-authoring.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def check():
    schemas = {}
    for p in sorted((HERE / 'schemas').glob('*.schema.json')):
        s = json.loads(p.read_text())
        Draft202012Validator.check_schema(s)
        schemas[p.name] = s
    require(len(schemas) == 4, 'unexpected protocol schema count')
    content = json.loads((HERE / 'examples/content-entry.json').read_text())
    Draft202012Validator(schemas['artifact-content-entry.schema.json']).validate(content)
    decoded = base64.b64decode(content['data'], validate=True)
    original = ROOT / 'authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts/work.json'
    require(decoded == original.read_bytes(), 'content example lost original bytes')
    require(len(decoded) == content['size_bytes'] and sha(decoded) == content['byte_sha256'], 'content length/hash mismatch')
    with sqlite3.connect(':memory:') as db:
        db.executescript((HERE / 'schemas/sqlite-read-model.sql').read_text())
        require(db.execute('PRAGMA foreign_keys').fetchone()[0] == 1, 'foreign keys not enabled')
        tables = sorted(row[0] for row in db.execute("SELECT name FROM sqlite_schema WHERE type='table'"))
        require(len(tables) == 12, 'unexpected draft table count')
        require(not list(db.execute('PRAGMA foreign_key_check')), 'foreign key DDL inconsistency')
    baseline = json.loads((HERE / 'SOURCE-BASELINE.json').read_text())
    require(sha(json.dumps(baseline['sources'], sort_keys=True, separators=(',', ':')).encode()) == baseline['source_manifest_digest'], 'source manifest digest mismatch')
    for source in baseline['sources']:
        p = ROOT / source['path']
        require(p.is_file() and sha(p.read_bytes()) == source['sha256'] and p.stat().st_size == source['size_bytes'], 'source drift: ' + source['path'])
    preserved = []
    for v in ('v1', 'v2'):
        receipt = json.loads((ROOT / f'implementation/lab-runtime/{v}/receipts/validation.json').read_text())
        for item in receipt['source_manifest']:
            require(sha((ROOT / item['path']).read_bytes()) == item['sha256'], 'frozen runtime drift: ' + item['path'])
        preserved.append({'version': v, 'files': len(receipt['source_manifest']), 'unchanged': True})
    for p in HERE.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            name = target.split('#', 1)[0].strip('<>')
            target_path = p.parent / name
            if target_path.resolve() == RECEIPT.resolve():
                continue
            require(target_path.exists(), 'missing local link: ' + target)
    manifest = [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p.read_bytes())}
                for p in sorted(HERE.rglob('*')) if p.is_file() and p != RECEIPT and '__pycache__' not in p.parts]
    return {'schema_version': 'lab-artifact-storage-schema-authoring-receipt/v1',
            'result': 'PASS', 'authority_effect': 'none',
            'scope': 'Schema meta-validation, one exact-byte example, in-memory SQLite DDL creation, source/package hashes and local links. No complete package, replay, projector, materializer, failure recovery or workload conformance demonstrated.',
            'json_protocol_schemas': len(schemas), 'sqlite_tables': tables,
            'sqlite_authoring_version': sqlite3.sqlite_version,
            'exact_byte_round_trip': True, 'source_files': len(baseline['sources']),
            'source_manifest_digest': baseline['source_manifest_digest'],
            'preserved_lab_packages': preserved, 'runtime_suites_executed': False,
            'benchmarks_executed': False, 'persistent_databases_created': 0,
            'admissions_applied': 0, 'stores_migrated': 0, 'proposal_manifest': manifest}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write-receipt', action='store_true')
    args = p.parse_args()
    result = check()
    if args.write_receipt:
        RECEIPT.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    elif RECEIPT.exists():
        require(json.loads(RECEIPT.read_text()) == result, 'authoring receipt stale')
    print(json.dumps({k: v for k, v in result.items() if k != 'proposal_manifest'}, indent=2, sort_keys=True))
