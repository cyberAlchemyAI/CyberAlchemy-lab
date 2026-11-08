"""Pure receipt joins. Inputs are bounded original bytes, never private bodies."""
import hashlib
import json
import math

STAGE_SHA = '6721210d076da6462f904b2836a9e3ff5853be92f395a05ee2b141b517e078bf'
STAGE_REVIEW_SHA = 'c1c4389211c89a3ba291767a8a08f77898488eee9c1388292aa2599d7c47c45f'
ROOT = '/tmp/cal-context-family-20261020-0001/root'
ROLE = 'product/lab/release-candidates/v1/interface/docker-context-20261020-0001'
SOURCE = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0001'
AUTH = SOURCE + '/authorization/context-development.json'
REPLACEMENTS = (ROLE + '/build.py', ROLE + '/control.py')
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
NATIVE_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'


def need(ok, code):
    if not ok:
        raise RuntimeError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, 'DUPLICATE_KEY')
        result[key] = value
    return result


def parse(raw, limit=2 * 1024 * 1024):
    need(type(raw) is bytes and 0 < len(raw) <= limit, 'BYTE_BOUND')
    def constant(value):
        raise RuntimeError('NONFINITE')
    value = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    # All following comparisons operate on plain data produced by json.loads.
    return value


def digest(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def baseline(stage_raw):
    need(sha(stage_raw) == STAGE_SHA, 'ORIGINAL_STAGE_PIN')
    stage = parse(stage_raw)
    rows = []
    for key in ('existing_family_public', 'exact_public_checkout_additions',
                'projected_api_additions', 'projected_context_additions'):
        rows.extend({'path': r['path'], 'sha256': r['sha256']} for r in stage[key])
    rows.append({k: stage['protected_family_binding'][k] for k in ('path', 'sha256')})
    rows.sort(key=lambda r: r['path'])
    need(len(rows) == 1570 and len({r['path'] for r in rows}) == 1570, 'ORIGINAL_INVENTORY')
    return rows


def validate(stage_raw, selection_raw, selection_sha, receipt_raw, now):
    """selection_sha is an OUTSIDE independent pin, not taken from receipt.

    This validates receipt consistency only. It does not issue authority,
    establish honest provenance, inspect live files, or qualify issuer custody.
    """
    need(digest(selection_sha) and sha(selection_raw) == selection_sha, 'OUTSIDE_SELECTION_PIN')
    selection = parse(selection_raw)
    keys = {'schema', 'root', 'root_identity', 'stage_sha256', 'stage_review_sha256',
            'receipt_sha256', 'authorization_sha256', 'role_replacements',
            'constructor_review_sha256', 'issuer_enrollment_sha256',
            'private_root', 'not_before', 'expires', 'final_manifest_sha256'}
    need(type(selection) is dict and set(selection) == keys, 'SELECTION_FIELDS')
    need(selection['schema'] == 'context-finalization-selection/v1' and selection['root'] == ROOT
         and selection['stage_sha256'] == STAGE_SHA and
         selection['stage_review_sha256'] == STAGE_REVIEW_SHA, 'STAGE_JOIN')
    identity = selection['root_identity']
    need(type(identity) is list and len(identity) == 4 and
         all(type(v) is int and v >= 0 for v in identity) and identity[1] > 0, 'ROOT_IDENTITY')
    for key in ('receipt_sha256', 'authorization_sha256', 'constructor_review_sha256',
                'issuer_enrollment_sha256', 'final_manifest_sha256'):
        need(digest(selection[key]), 'MISSING_INDEPENDENT_INPUT')
    private = selection['private_root']
    need(type(private) is str and private.startswith('/tmp/') and '\\' not in private and
         '\0' not in private and all(p not in ('', '.', '..') for p in private[1:].split('/'))
         and private != ROOT and not private.startswith(ROOT + '/')
         and not ROOT.startswith(private + '/'), 'PRIVATE_ROOT_EXPOSURE')
    interval = [selection['not_before'], selection['expires'], now]
    need(all(type(v) in (int, float) and math.isfinite(v) for v in interval) and
         selection['not_before'] <= now < selection['expires'], 'CURRENT_INTERVAL')
    replacements = selection['role_replacements']
    need(type(replacements) is dict and set(replacements) == set(REPLACEMENTS) and
         all(digest(d) for d in replacements.values()), 'TWO_ROLE_SELECTION')
    need(sha(receipt_raw) == selection['receipt_sha256'], 'INDEPENDENT_RECEIPT_PIN')
    receipt = parse(receipt_raw)
    expected_keys = {'schema', 'root', 'root_identity', 'stage_sha256', 'files',
                     'source_mode', 'auth_directory_mode', 'auth_leaf_mode',
                     'mounts', 'image', 'native_sha256', 'constructor_review_sha256',
                     'issuer_enrollment_sha256', 'private_root', 'not_before', 'expires',
                     'status', 'retry_allowed'}
    need(type(receipt) is dict and set(receipt) == expected_keys, 'RECEIPT_FIELDS')
    need(receipt['schema'] == 'context-finalization-receipt/v1' and
         receipt['status'] == 'FINALIZATION_ONLY' and receipt['retry_allowed'] is False,
         'FINALIZATION_CEILING')
    for key in ('root', 'root_identity', 'stage_sha256', 'constructor_review_sha256',
                'issuer_enrollment_sha256', 'private_root', 'not_before', 'expires'):
        need(receipt[key] == selection[key], 'RECEIPT_SCOPE_JOIN')
    expected = baseline(stage_raw)
    for row in expected:
        if row['path'] in replacements:
            need(row['sha256'] != replacements[row['path']], 'UNCHANGED_ROLE')
            row['sha256'] = replacements[row['path']]
    expected.append({'path': AUTH, 'sha256': selection['authorization_sha256']})
    expected.sort(key=lambda r: r['path'])
    need(receipt['files'] == expected and len(expected) == 1571, 'EXACT_1571_INVENTORY')
    need(sha(encode(expected)) == selection['final_manifest_sha256'], 'FINAL_MANIFEST_PIN')
    need(receipt['source_mode'] == '0700' and receipt['auth_directory_mode'] == '0700'
         and receipt['auth_leaf_mode'] == '0600', 'AUTH_TOPOLOGY')
    need(receipt['mounts'] == {'root': 'ro', 'output': 'ro', 'native': 'ro', 'private': 'unmounted'}
         and receipt['image'] == IMAGE and receipt['native_sha256'] == NATIVE_SHA, 'RUNTIME_MOUNTS')
    return {'status': 'RECEIPT_CONSISTENT_ONLY', 'effect_enabled': False,
            'receipt_sha256': sha(receipt_raw), 'final_manifest_sha256': sha(encode(expected)),
            'files': 1571, 'live_custody': 'NOT_CHECKED', 'issuer_authority': 'NOT_ESTABLISHED'}
