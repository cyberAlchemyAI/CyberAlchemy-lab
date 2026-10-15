"""Review exact public code and protected original provenance without publishing.

This bounded audit is an R06 partial: final integrated Product release bytes
remain required. Findings carry selectors and hashes, never private values.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
SOURCE = HERE / 'source-manifest.json'
PACKAGE = ROOT / 'product/lab/release-candidates/v1/packaging/R02/packages/0003'
PRIVATE = ROOT / 'product/lab/release-candidates/v1/interface/current-participation-v3/packages/0001/branch.snapshot'
MIGRATION = ROOT / 'implementation/lab-ontology/candidates/v1/migration/source-selection.json'
SENSITIVE = {'private_key', 'private_key_bytes', 'session_memory', 'short_memory'}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def pairs(rows):
        value = {}
        for key, item in rows:
            need(key not in value, 'duplicate JSON field')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def read(path):
    path = Path(path)
    need(not path.is_symlink() and not any(p.is_symlink() for p in path.parents),
         'symlink custody refused')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        need(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), 'regular source required')
        return stream.read()


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': sha(read(path))}


def relative(name):
    need(type(name) is str and name and '\\' not in name and '\x00' not in name,
         'invalid relative path')
    path = PurePosixPath(name)
    need(not path.is_absolute() and '..' not in path.parts and path.as_posix() == name,
         'unsafe relative path')
    need(not any(p in {'.env', '.local', '__pycache__'} or p.startswith('.env.') for p in path.parts),
         'private environment/cache path')
    need(not name.endswith(('.key', '.pem', '.pyc', '.db', '.sqlite', '.sqlite3')),
         'key/cache/store path')
    return name


def scan(raw, label):
    """Inspect actual values and closed embedded byte formats; no value output."""
    findings = []
    need(len(raw) <= 128 * 1024 ** 2, 'inspection byte ceiling exceeded')
    if re.search(rb'-----BEGIN (?:[A-Z ]+)?PRIVATE KEY-----\r?\n', raw):
        findings.append({'source': label, 'selector': '#', 'reason': 'private-key-marker'})
    if not raw.lstrip().startswith((b'{', b'[')):
        return findings

    def walk(value, selector, declaration=False, depth=0):
        need(depth <= 64, 'inspection nesting ceiling exceeded')
        if isinstance(value, dict):
            if not declaration:
                for key in sorted(SENSITIVE & set(value)):
                    findings.append({'source': label, 'selector': selector + '/' + key,
                                     'reason': 'actual-private-or-session-field'})
            is_schema = '$schema' in value
            for key, item in value.items():
                schema_region = declaration or (is_schema and key in {'properties', '$defs', 'definitions'})
                walk(item, selector + '/' + key.replace('~', '~0').replace('/', '~1'),
                     schema_region, depth + 1)
            # Closed original-custody envelopes are decoded and hash verified.
            if set(value) == {'base64_original_bytes', 'sha256'}:
                body = base64.b64decode(value['base64_original_bytes'], validate=True)
                need(sha(body) == value['sha256'], 'embedded original digest differs')
                findings.extend(scan(body, label + ':' + selector))
            if value.get('schema_version') == 'lab-exact-public-byte-snapshot/v1-candidate':
                need(set(value) == {'schema_version', 'authority_effect', 'files', 'sha256s'},
                     'closed public snapshot shape required')
                need(set(value['files']) == set(value['sha256s']), 'public snapshot closure differs')
                for name, encoded in value['files'].items():
                    relative(name)
                    body = base64.b64decode(encoded, validate=True)
                    need(sha(body) == value['sha256s'][name], 'public embedded digest differs')
                    findings.extend(scan(body, label + ':' + name))
            for key in ('byte_contents', 'control_bytes', 'executable_byte_contents'):
                if key in value:
                    need(isinstance(value[key], dict), 'closed embedded byte dictionary required')
                    for name, encoded in value[key].items():
                        body = base64.b64decode(encoded, validate=True)
                        findings.extend(scan(body, label + ':' + key + ':' + name))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, selector + '/' + str(index), declaration, depth + 1)

    walk(parse(raw), '#')
    return findings


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser();parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args();need(sha(read(SOURCE)) == args.source_sha256, 'independent source pin differs')
    source = parse(read(SOURCE))
    for row in source['files']:
        need(bind(ROOT / row['path']) == row, 'frozen input changed: ' + row['path'])
    selection = parse(read(PACKAGE / 'selection.json'))
    snapshot_raw = read(PACKAGE / 'payload.snapshot')
    need(sha(snapshot_raw) == selection['snapshot_sha256'], 'package snapshot digest differs')
    snapshot = parse(snapshot_raw)
    need(snapshot['schema_version'] == 'lab-exact-public-byte-snapshot/v1-candidate', 'actual public package required')
    need(set(snapshot['files']) == set(snapshot['sha256s']), 'public code closure differs')
    need(not scan(snapshot_raw, 'R02-public-payload'), 'private values in selected public code')
    public = []
    for name, encoded in sorted(snapshot['files'].items()):
        relative(name);body = base64.b64decode(encoded, validate=True)
        need(sha(body) == snapshot['sha256s'][name], 'exact package code digest differs')
        public.append({'package_member': name, 'sha256': sha(body), 'size_bytes': len(body),
                       'disposition': 'public-code-candidate', 'public_body_export_allowed': True,
                       'source_provenance': bind(PACKAGE / 'payload.snapshot')})
    need(len(public) == 87, 'original87package code/control members required')
    package_files = []
    for path in sorted(PACKAGE.rglob('*')):
        if not path.is_file():continue
        relative(path.relative_to(PACKAGE).as_posix())
        package_files.append({**bind(path), 'size_bytes': path.stat().st_size,
                              'disposition': 'public-code-package-candidate',
                              'public_body_export_allowed': True})
    wheel_names = {row['filename'] for row in selection['wheels']}
    need(len(wheel_names) == 8, 'all8declareddependency wheels required')
    need({p.name for p in (PACKAGE / 'wheels').iterdir()} == wheel_names, 'closed wheel set required')
    for row in selection['wheels']:
        need(sha(read(PACKAGE / 'wheels' / row['filename'])) == row['sha256'], 'wheel digest differs')
    protected = parse(read(PRIVATE))
    need(protected['historical_provenance_protection'] == 'private-original-custody-not-public-package',
         'protected archive classification differs')
    findings = scan(read(PRIVATE), 'current-participation-v3-protected-archive')
    need(any(row['selector'].endswith('/session_memory') for row in findings),
         'actual historical Session field must be accounted')
    protected_row = {**bind(PRIVATE), 'size_bytes': PRIVATE.stat().st_size,
                     'disposition': 'retain-private-exclude-public',
                     'public_body_export_allowed': False,
                     'reason': 'Exact historical signed provenance includes Session fields; never copy into public payload.',
                     'findings': findings}
    migration = parse(read(MIGRATION));items = migration['items']
    need(len(items) == 140 and all(row['privacy'] == 'private' and
         row['public_body_export_allowed'] is False for row in items), 'all140private migration dispositions required')
    imported = [{'item_id': row['item_id'], 'source_binding': row['source_binding'],
                 'source_disposition': row['disposition'], 'public_body_export_allowed': False,
                 'disposition': 'retain-private-provenance-exclude-public-body',
                 'reason': row['reason']} for row in items]
    for row in source['files']:
        need(bind(ROOT / row['path']) == row, 'final frozen input changed: ' + row['path'])
    result = {'schema_version': 'lab-R06-boundary-inventory/v1-candidate',
              'result': 'PASS', 'task': 'R06', 'task_complete': False,
              'public_code_members': public, 'public_package_files': package_files,
              'protected_archives': [protected_row], 'private_migration_items': imported,
              'source_manifest_binding': bind(SOURCE), 'authority_effect': 'none',
              'actual_owner_outcome': None, 'publication_authorized': False,
              'private_or_live_state_removed': False,
              'remaining_obligations': [
                  'Select and inspect every final integrated API/workflow/ontology/schema/review/evidence release byte.',
                  'Verify complete integrated packaging closure and source permissions after R03 integration.',
                  'Bind S02/R07 to the exact complete release-selection successor; final public export is currently disallowed.',
                  'Keep protected provenance outside public packages and retain original/rollback dependencies.']}
    inventory = HERE / 'inventory.json';put(inventory, result)
    files = {row['path']: row for row in source['files']}
    for path in [SOURCE, inventory]:files[bind(path)['path']] = bind(path)
    receipt = {'schema_version': 'lab-R06-boundary-partial-proof/v1-candidate',
               'result': 'PASS', 'task': 'R06', 'task_complete': False,
               'files': [files[k] for k in sorted(files)], 'inventory_binding': bind(inventory),
               'public_code_members': len(public), 'public_package_files': len(package_files),
               'private_migration_items': len(imported), 'protected_archive_findings': len(findings),
               'remaining_obligations': result['remaining_obligations'],
               'authority_effect': 'none', 'actual_owner_outcome': None,
               'claim_ceiling': 'Exact current R02 code package and private Source3/O04 provenance only; full integrated R06 and final release remain incomplete.'}
    put(HERE / 'receipts/0001.json', receipt)
    print(json.dumps({k: receipt[k] for k in ['result','task_complete','public_code_members','public_package_files','private_migration_items','protected_archive_findings']}), flush=True)


if __name__ == '__main__':
    main()
