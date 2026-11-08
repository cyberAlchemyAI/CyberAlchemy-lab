"""Exact public Context input inventory; never opens a protected archive."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import stat
from pathlib import Path, PurePosixPath

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
SELECTION_SHA = 'bf7597ed77ad71bbf45c9b6d5100805a60200139c9159e4321d8d5ebbb21c3e7'
HISTORICAL = REPO / 'implementation/lab-runtime/local-host/context-construction-0003/historical-closure-candidates.json'
HISTORICAL_SHA = 'e02c3061ee705d826f02d74887340ce85047ef989491dfddfdf1e3590aec350a'
INTEGRATION_FREEZE = REPO / 'implementation/lab-runtime/local-host/context-integration-0002/freeze.json'
INTEGRATION_SHA = '53e9b63a47ca889cf458ecdff3bc7c8a07297bdc6a46b54294029b016c296360'
INTEGRATION_REVIEW = REPO / 'implementation/lab-runtime/local-host/CONTEXT-INTEGRATION-INDEPENDENT-STATIC-REVIEW-0002.md'
REVIEW_SHA = 'c7106748446db781dcd5d57ef08c0cc297bdf637c85b118b5e2fff19c93ce9e1'
CONSTRUCTOR_FREEZE = REPO / 'implementation/lab-runtime/local-host/context-construction-0003/freeze.json'
CONSTRUCTOR_SHA = '33f253a6bb71c6f7188eb8f966d3d80ca414c3c2321e0d94c0e8efbde4a64d3a'
API = 'product/lab/release-candidates/v1/interface/api-v25/'
FACT = 'product/lab/release-candidates/v1/interface/fact-read-scope-v1/'
CARRIERS = {'ontology-node': 'v2', 'ontology-edge': 'v1', 'ontology': 'v1',
            'ontology-cut': 'v1', 'ontology-view': 'v1', 'context-request': 'v1',
            'context-view': 'v1'}
READER_CODE_SHA = 'f93a1f218238c05b18a7c355f9bc1363bbf42d2b1d442d03e191e121f8e9c9b9'
READER_MANIFEST_SHA = '4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251'
FAMILY = '/tmp/cal-context-construction-20261020-0003/family/legacy-context-dev-20261020-0003'
ENV = {'python': '3.14.4', 'jsonschema': '4.23.0', 'cryptography': '46.0.5'}
LIMIT = 4 * 1024 * 1024


class Refused(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise Refused(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_exact(path: Path, pin: str) -> bytes:
    require(type(pin) is str and len(pin) == 64 and all(c in '0123456789abcdef' for c in pin),
            'exact digest required')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and 0 <= before.st_size <= LIMIT,
                'public metadata must be bounded regular file')
        parts, total = [], 0
        while True:
            chunk = os.read(fd, min(1024 * 1024, before.st_size + 1 - total))
            if not chunk:
                break
            total += len(chunk)
            require(total <= before.st_size, 'public metadata grew during read')
            parts.append(chunk)
        after = os.fstat(fd)
        require((after.st_dev, after.st_ino, after.st_mode, after.st_nlink, after.st_size) ==
                (before.st_dev, before.st_ino, before.st_mode, before.st_nlink, before.st_size),
                'public metadata identity changed')
        raw = b''.join(parts)
        require(total == before.st_size and sha(raw) == pin, 'public metadata bytes differ')
        return raw
    finally:
        os.close(fd)


def carrier_paths():
    return {f'authority/artifact-types/{kind}/{version}/{name}'
            for kind, version in CARRIERS.items()
            for name in ('artifact.json', 'schema.json', 'fixtures/valid/record.json')}


def validate_selection(selected, historical):
    require(type(selected) is dict and set(selected) == {
        'schema_version', 'status', 'authority_effect', 'actual_owner_outcome',
        'integration_freeze_sha256', 'integration_review_sha256', 'constructor_freeze_sha256',
        'historical_inventory_sha256', 'environment', 'public_rows', 'counts',
        'reader_binding', 'development_authorization', 'mapper_package',
        'context_source_manifest', 'context_launch', 'protected_body_read',
    }, 'closed public selection shape differs')
    require(selected['schema_version'] == 'lab-context-public-closure-selection/v1' and
            selected['status'] == 'PUBLIC_CONSTRUCTION_ONLY' and
            selected['authority_effect'] == 'none' and selected['actual_owner_outcome'] is None and
            selected['integration_freeze_sha256'] == INTEGRATION_SHA and
            selected['integration_review_sha256'] == REVIEW_SHA and
            selected['constructor_freeze_sha256'] == CONSTRUCTOR_SHA and
            selected['historical_inventory_sha256'] == HISTORICAL_SHA and
            selected['environment'] == ENV and
            selected['reader_binding'] == 'MECHANISM_ONLY_NO_SAME_FAMILY_FILE' and
            selected['development_authorization'] == 'UNMINTED' and
            selected['mapper_package'] == 'UNSELECTED' and
            selected['context_source_manifest'] == 'REFUSED' and
            selected['context_launch'] == 'REFUSED' and
            selected['protected_body_read'] is False,
            'effect-disabled public selection differs')
    require(type(selected['counts']) is dict and selected['counts'] == {
        'api_v25': 34, 'fact_scope': 4, 'carrier_artifact': 7,
        'carrier_schema': 7, 'carrier_fixture': 7}, 'public role counts differ')
    require(type(historical) is dict and set(historical) == {'historical_manifest_sha256', 'rows'},
            'historical inventory shape differs')
    history = {r['path']: r for r in historical['rows']}
    require(len(history) == len(historical['rows']) == 1804 and
            sum(r['state'] == 'protected_archive_excluded' for r in historical['rows']) == 6,
            'historical closure inventory differs')
    expected = {p for p in history if p.startswith(API) or p.startswith(FACT)} | carrier_paths()
    rows = selected['public_rows']
    require(type(rows) is list and len(rows) == len(expected) == 59,
            'exact public role inventory differs')
    seen = set()
    for row in rows:
        require(type(row) is dict and set(row) == {'role', 'path', 'sha256', 'size', 'historical_row'},
                'closed public row differs')
        path = row['path']
        require(type(path) is str and path in expected and path not in seen and
                '..' not in PurePosixPath(path).parts and not path.startswith('/') and
                not path.endswith('branch.snapshot') and 'authorization' not in path,
                'historical protected or unselected input refused')
        seen.add(path)
        role = ('api_v25' if path.startswith(API) else 'fact_scope' if path.startswith(FACT)
                else 'carrier_fixture' if '/fixtures/' in path else
                'carrier_schema' if path.endswith('/schema.json') else 'carrier_artifact')
        require(row['role'] == role and type(row['size']) is int and 0 <= row['size'] <= LIMIT and
                type(row['sha256']) is str and len(row['sha256']) == 64 and
                all(c in '0123456789abcdef' for c in row['sha256']) and
                row['historical_row'] is (path in history), 'public row binding differs')
        if path in history:
            require(history[path]['state'] == 'unselected_candidate' and
                    row['sha256'] == history[path]['historical_sha256'],
                    'historical public pin differs')
    require(seen == expected, 'public role set differs')
    return rows


def verify_public():
    selected = json.loads(read_exact(HERE / 'public-selection.json', SELECTION_SHA))
    historical = json.loads(read_exact(HISTORICAL, HISTORICAL_SHA))
    rows = validate_selection(selected, historical)
    read_exact(INTEGRATION_FREEZE, INTEGRATION_SHA)
    read_exact(INTEGRATION_REVIEW, REVIEW_SHA)
    constructor = json.loads(read_exact(CONSTRUCTOR_FREEZE, CONSTRUCTOR_SHA))
    control = next(r for r in constructor['files'] if r['path'] == 'rendered/control.py')
    base = next(r for r in constructor['files'] if r['path'] == 'rendered/base.py')
    control_raw = read_exact(CONSTRUCTOR_FREEZE.parent / control['path'], control['sha256'])
    base_raw = read_exact(CONSTRUCTOR_FREEZE.parent / base['path'], base['sha256'])
    require(b"API_PROFILE_PIN = 'c9b9d88e37ff0e9514727bd71ac0091e0dd4dc59c707fb6b07e713503922d33d'" in base_raw,
            'selected API profile literal differs')
    require(control_raw.count(b'AUTH.read_bytes()') == 2 and
            control_raw.count(b"AUTH = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'") == 1,
            'historical AUTH sites differ')
    for row in rows:
        raw = read_exact(REPO / row['path'], row['sha256'])
        require(len(raw) == row['size'], 'public row length differs')
    require(next(r['sha256'] for r in rows if r['path'] == API + 'contract-profile.json') ==
            'c9b9d88e37ff0e9514727bd71ac0091e0dd4dc59c707fb6b07e713503922d33d',
            'API profile and rendered role diverge')
    return {'status': 'PUBLIC_59_EXACT_PASS', 'public_rows': len(rows),
            'api_v25': 34, 'fact_scope': 4, 'carrier_rows': 21,
            'historical_rows': 1804, 'protected_archives_excluded': 6,
            'reader_binding': 'MECHANISM_ONLY', 'development_authorization': 'UNMINTED',
            'mapper_package': 'UNSELECTED', 'context_source_manifest': 'REFUSED',
            'context_launch': 'REFUSED', 'protected_body_read': False, 'effect': 'NOT_RUN'}


def project_reader_binding(family: Path) -> bytes:
    """Pure candidate bytes only after actual same-family public Reader files exist."""
    name = PurePosixPath(str(family))
    require(name.is_absolute() and '..' not in name.parts and str(name) == FAMILY,
            'selected same-family Reader root required')
    code = family / 'reader/reader.py'
    manifest = family / 'reader/source-manifest.json'
    read_exact(code, READER_CODE_SHA)
    source = json.loads(read_exact(manifest, READER_MANIFEST_SHA))
    require(source['environment'] == ENV and source['authority_effect'] == 'none' and
            source['actual_owner_outcome'] is None, 'reviewed Reader posture differs')
    value = {
        'schema_version': 'lab-original-reader-implementation-evidence/v1-candidate',
        'code_binding': {'ref': str(code), 'sha256': READER_CODE_SHA},
        'entrypoint_ref': str(code) + '#SelectedReader.open_signed',
        'environment': ENV,
        'environment_contract_ref': 'protocol:R03-selected-R02-reader-environment',
        'authority_effect': 'none', 'actual_owner_outcome': None,
        'claim_ceiling': 'Same-family Reader code projection only; no issuer grant or Context delivery.',
    }
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def auth_projection_plan(relative_path: str, pin: str):
    """Inspect exact frozen AST; no authorization bytes or projected role are emitted."""
    require(relative_path == 'authorization/context-development.json' and
            type(pin) is str and len(pin) == 64 and all(c in '0123456789abcdef' for c in pin),
            'fresh development AUTH path and exact pin required')
    constructor = json.loads(read_exact(CONSTRUCTOR_FREEZE, CONSTRUCTOR_SHA))
    row = next(r for r in constructor['files'] if r['path'] == 'rendered/control.py')
    raw = read_exact(CONSTRUCTOR_FREEZE.parent / row['path'], row['sha256'])
    tree = ast.parse(raw)
    assignments = {name: [] for name in ('AUTH', 'AUTH_SHA')}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in assignments:
                    assignments[target.id].append(node)
    require(all(len(v) == 1 for v in assignments.values()) and
            raw.count(b'AUTH.read_bytes()') == 2 and raw.count(b'AUTH_SHA') == 1,
            'historical AUTH projection occurrence vector differs')
    require('authorization.json' not in relative_path and relative_path not in raw.decode(),
            'historical or reused grant refused')
    return {'status': 'AST_PROJECTION_MECHANISM_ONLY',
            'future_path': 'ROOT/' + relative_path, 'future_sha256': pin,
            'old_path_assignments': 1, 'old_pin_assignments': 1,
            'unguarded_auth_reads_to_replace': 2,
            'required_guard': 'exact selected AUTH byte hash and current period at each read',
            'authorization_file_created': False, 'policy_or_key_created': False,
            'final_projection': 'REFUSED_PENDING_FRESH_AUTH_BYTES'}


def project_auth_pure(relative_path: str, pin: str) -> bytes:
    """In-memory role projection only; a digest is not an issued authorization."""
    auth_projection_plan(relative_path, pin)
    constructor = json.loads(read_exact(CONSTRUCTOR_FREEZE, CONSTRUCTOR_SHA))
    row = next(r for r in constructor['files'] if r['path'] == 'rendered/control.py')
    original = read_exact(CONSTRUCTOR_FREEZE.parent / row['path'], row['sha256'])
    old_path = b"AUTH = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'"
    old_pin = b"AUTH_SHA = '4d3c34a7f19b4b47892b3fbf5673544b36b0517e516961adcc77722f5d08e906'"
    old_read = b'AUTH.read_bytes()'
    require(original.count(old_path) == original.count(old_pin) == 1 and
            original.count(old_read) == 2, 'AUTH preimage occurrence vector differs')
    new_path = ("AUTH = ROOT / '" + relative_path + "'").encode()
    new_pin = ("AUTH_SHA = '" + pin + "'").encode()
    new_read = b'_context_development_auth(self.source.sources.scope_ref)'
    helper = b'''\n\ndef _context_development_auth(scope_ref):
    raw = AUTH.read_bytes()
    require(sha(raw) == AUTH_SHA, 'development authorization bytes changed')
    value = EL.parse(raw)
    require(type(value) is dict and set(value) == {
        'schema_version', 'family_ref', 'episode_ref', 'scope_ref',
        'period_binding', 'not_before', 'expires_at', 'authority_effect',
        'actual_owner_outcome', 'claim_ceiling'}, 'closed development authorization required')
    period_path = reader.HERE / 'packages/0001/period.json'
    period = load(period_path)
    start, end = EL.instant(value['not_before']), EL.instant(value['expires_at'])
    require(value['schema_version'] == 'lab-context-development-authorization/v1-candidate' and
            value['family_ref'] == str(HERE.parent) and
            value['episode_ref'] == period['period_ref'] and
            value['scope_ref'] == scope_ref and
            value['period_binding'] == binding(period_path) and
            value['authority_effect'] == 'none' and
            value['actual_owner_outcome'] is None and
            value['claim_ceiling'] == 'Local disposable development episode only; no protected Source8 issuer grant or owner outcome.' and
            EL.instant(period['not_before']) <= start <= now() < end <= EL.instant(period['expires_at']) and
            (end - start).total_seconds() <= 1200,
            'development authorization period, scope or posture differs')
    return raw
'''
    projected = original.replace(old_path, new_path).replace(old_pin, new_pin)
    projected = projected.replace(old_read, new_read)
    projected = projected.replace(new_pin + b'\n', new_pin + helper + b'\n', 1)
    ast.parse(projected)
    require(projected.count(new_path) == projected.count(new_pin) == 1 and
            projected.count(new_read) == 2 and projected.count(old_read) == 1,
            'AUTH postimage occurrence vector differs')
    inverse = projected.replace(new_pin + helper + b'\n', new_pin + b'\n', 1)
    inverse = inverse.replace(new_read, old_read).replace(new_pin, old_pin).replace(new_path, old_path)
    require(inverse == original, 'AUTH projection byte inverse differs')
    return projected


def final_context_source_manifest(*_args, **_kwargs):
    raise Refused('fresh Mapper output, same-family Reader and development AUTH, and complete closure required')


def launch_context(*_args, **_kwargs):
    raise Refused('effect-disabled public closure construction')
