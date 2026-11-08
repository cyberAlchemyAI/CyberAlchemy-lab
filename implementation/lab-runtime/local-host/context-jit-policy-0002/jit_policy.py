"""Effect-disabled local Context JIT authorization and host-policy contract.

This module validates *caller-supplied synthetic values* and models release
order. Policy validation revalidates exact supplied authorization bytes and
their digest. It never generates a key, issues a grant, creates a private root,
or imports Context. A future effect adapter must implement the frozen contract
in a disjoint candidate after the family/scope and issuer bytes are selected.
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import os
import stat
import ast
from pathlib import Path
from pathlib import PurePosixPath

EFFECT_ENABLED = False
CLAIM = 'Local disposable development episode only; no protected Source8 issuer grant or owner outcome.'
PERIOD_REF = 'protocol:R03-docker-source-20261020-0001-period/v1'
PERIOD_SHA = 'f2633ba3d6c9868740749a3e7d8f288ea7abb461246f964e64c5dc9bf8b14bca'
SOURCE_PACKAGE_SHA = 'f132b3e1908e9e116464ad29c3db7f56ca17d4dee080e60ffa62547dd9588a5b'
READER_MANIFEST_SHA = '4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251'
READER_CODE_SHA = 'f93a1f218238c05b18a7c355f9bc1363bbf42d2b1d442d03e191e121f8e9c9b9'
MAPPER_PACKAGE_SHA = '0b3635dc9896034203e9e318ad99d58f2c37ca5acd419841d338f6ec9e4a1aea'
MAX_POLICY_BYTES = 16 * 1024
MAX_AUTH_BYTES = 16 * 1024
PERIOD_REL = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0001/packages/0001/period.json'
REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
PREIMAGES = {
    'implementation/lab-runtime/local-host/context-auth-guard-0004/freeze.json':
        '40baf5d872fdd95ab34238311c26a21dfc12dbb44cd2160487a515b3dbaf473a',
    'implementation/lab-runtime/local-host/CONTEXT-AUTH-GUARD-INDEPENDENT-STATIC-REVIEW-0004.md':
        '01e818c8d17834b1eae7dec77fbaca16e23f3820b737c80d20b08a49ae6f6626',
    'implementation/lab-runtime/local-host/context-policy-0002/freeze.json':
        '9aedc04a6f25c2380330223da9a94453aee851a7affcf178f908ed2160aafed6',
    'implementation/lab-runtime/local-host/CONTEXT-POLICY-INDEPENDENT-STATIC-REVIEW-0002.md':
        '6959f5f5dd82addca8827d2a322e92554639a24fba0ca5ee99d886c6377b5416',
    'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0005/instances/optimized-0005/context/build.py':
        '593bb78e8834c7d09277b1e04fe7b9256015746a2ee405d4910b1d2124d80369',
    'implementation/lab-runtime/local-host/context-critical-path-audit-0001/AUDIT.md':
        '9722ccfb830dde13448883160da66172c59eb738a3bbffad53a26468a943db97',
}


class Refused(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise Refused(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def reviewed_preimages():
    """Read only exact public code/reviews; never any Source archive or key."""
    for relative, pin in PREIMAGES.items():
        path = REPO / relative
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_size <= 2 * 1024 * 1024,
                    'bounded public preimage required')
            raw = os.read(fd, before.st_size + 1)
            after = os.fstat(fd)
            require(len(raw) == before.st_size and
                    (before.st_dev, before.st_ino, before.st_mode, before.st_size) ==
                    (after.st_dev, after.st_ino, after.st_mode, after.st_size) and
                    digest(raw) == pin, 'reviewed public preimage changed')
        finally:
            os.close(fd)
    build = (REPO / next(k for k in PREIMAGES if k.endswith('/context/build.py'))).read_bytes()
    tree = ast.parse(build)
    functions = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    require({'provision', 'build', 'emit', 'query'} <= functions and
            build.count(b'Ed25519PrivateKey.generate()') == 1 and
            build.count(b'key=None') == 1 and
            build.count(b"policy_path=root/'permission.json'") == 1 and
            build.count(b"require(not root.exists()") == 1,
            'original Context JIT/key/root preimage differs')
    return {'status': 'EXACT_PUBLIC_PREIMAGES', 'files': len(PREIMAGES),
            'original_build_sha256': PREIMAGES[next(k for k in PREIMAGES if k.endswith('/context/build.py'))],
            'effect': 'NOT_RUN'}


def closed_json(raw, limit):
    require(type(raw) is bytes and 1 <= len(raw) <= limit, 'bounded JSON bytes required')
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise Refused('canonical closed JSON bytes required') from error
    require(type(value) is dict and
            (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                        allow_nan=False) + '\n').encode() == raw,
            'canonical closed JSON bytes required')
    return value


def instant(value):
    require(type(value) is str, 'timestamp required')
    result = dt.datetime.fromisoformat(value)
    require(result.tzinfo is not None and result.utcoffset() == dt.timedelta(),
            'UTC timestamp required')
    return result


def canonical_absolute(value):
    require(type(value) is str and value.startswith('/') and '//' not in value and
            not any(part in ('', '.', '..') for part in value.split('/')[1:]) and
            str(PurePosixPath(value)) == value,
            'canonical absolute path required')
    return PurePosixPath(value)


def exact_hash(value):
    require(type(value) is str and len(value) == 64 and
            all(ch in '0123456789abcdef' for ch in value), 'exact SHA-256 required')
    return value


def selected_identity(uid, gid):
    require(type(uid) is int and type(gid) is int and uid >= 1 and gid >= 1 and
            uid == os.getuid() == os.geteuid() and
            gid == os.getgid() == os.getegid(),
            'selected real/effective UID/GID differs')


def select(spec, period_raw, now):
    """Purely select scope, roles and paths. No grant/policy bytes are made."""
    require(type(now) is dt.datetime and now.tzinfo is not None and
            now.utcoffset() == dt.timedelta(), 'UTC selection time required')
    require(type(period_raw) is bytes and digest(period_raw) == PERIOD_SHA,
            'exact selected Source period bytes required')
    period = closed_json(period_raw, 16 * 1024)
    require(type(spec) is dict and set(spec) == {
        'family_ref', 'source_root', 'private_root', 'uid', 'gid',
        'principal_ref', 'scope_ref', 'reader_code_sha256',
        'reader_manifest_sha256', 'source_package_sha256',
        'mapper_package_sha256', 'period_sha256'},
        'closed JIT selection required')
    require(type(period) is dict and {'period_ref', 'principal_ref', 'not_before', 'expires_at',
                                      'authority_effect', 'actual_owner_outcome'} <= set(period),
            'selected Source period required')
    selected_identity(spec['uid'], spec['gid'])
    family = canonical_absolute(spec['family_ref'])
    source = canonical_absolute(spec['source_root'])
    private = canonical_absolute(spec['private_root'])
    tmp = PurePosixPath('/tmp')
    require(tmp in family.parents and tmp in source.parents and tmp in private.parents and
            family != source and family not in source.parents and
            source not in family.parents and private != source and
            private not in source.parents and source not in private.parents and
            private != family and private not in family.parents and family not in private.parents,
            'family, Source and private-root topology differs')
    require(spec['period_sha256'] == PERIOD_SHA and
            spec['source_package_sha256'] == SOURCE_PACKAGE_SHA and
            spec['reader_manifest_sha256'] == READER_MANIFEST_SHA and
            spec['mapper_package_sha256'] == MAPPER_PACKAGE_SHA and
            spec['reader_code_sha256'] == READER_CODE_SHA and
            type(spec['principal_ref']) is str and
            spec['principal_ref'] == period['principal_ref'] and
            type(spec['scope_ref']) is str and spec['scope_ref'].startswith('scope:'),
            'selected role pins or principal/scope differ')
    start, end = instant(period['not_before']), instant(period['expires_at'])
    require(period['period_ref'] == PERIOD_REF and period['authority_effect'] == 'none' and
            period['actual_owner_outcome'] is None and end - start == dt.timedelta(hours=24) and
            start <= now < end, 'selected Source period is not current local development')
    selected_identity(spec['uid'], spec['gid'])
    return {'schema_version': 'lab-context-jit-policy-selection/v1-inert',
            'effect': 'NOT_RUN', 'family_ref': str(family),
            'authorization_path': str(source / 'authorization/context-development.json'),
            'source_root': str(source), 'private_root': str(private),
            'policy_path': str(private / 'permission.json'),
            'period_ref': PERIOD_REF, 'period_sha256': PERIOD_SHA,
            'principal_ref': spec['principal_ref'], 'scope_ref': spec['scope_ref'],
            'uid': spec['uid'], 'gid': spec['gid'],
            'reader_code_sha256': spec['reader_code_sha256'],
            'reader_manifest_sha256': READER_MANIFEST_SHA,
            'source_package_sha256': SOURCE_PACKAGE_SHA,
            'mapper_package_sha256': MAPPER_PACKAGE_SHA,
            'period_start': period['not_before'], 'period_end': period['expires_at'],
            'authority_effect': 'none', 'actual_owner_outcome': None}


def validate_authorization(raw, selected, now):
    """Validate supplied dummy authorization bytes; never issue or sign them."""
    value = closed_json(raw, MAX_AUTH_BYTES)
    require(set(value) == {'schema_version', 'family_ref', 'episode_ref', 'scope_ref',
                           'period_binding', 'not_before', 'expires_at',
                           'authority_effect', 'actual_owner_outcome', 'claim_ceiling'},
            'closed Context development authorization required')
    require(type(selected) is dict and selected.get('schema_version') ==
            'lab-context-jit-policy-selection/v1-inert' and
            selected.get('effect') == 'NOT_RUN', 'exact inert selection required')
    selected_identity(selected['uid'], selected['gid'])
    start, end = instant(value['not_before']), instant(value['expires_at'])
    period_start, period_end = instant(selected['period_start']), instant(selected['period_end'])
    require(value['schema_version'] == 'lab-context-development-authorization/v1-candidate' and
            value['family_ref'] == selected['family_ref'] and
            value['episode_ref'] == selected['period_ref'] and
            value['scope_ref'] == selected['scope_ref'] and
            value['period_binding'] == {'path': PERIOD_REL, 'sha256': PERIOD_SHA} and
            value['authority_effect'] == 'none' and value['actual_owner_outcome'] is None and
            value['claim_ceiling'] == CLAIM and
            period_start <= start <= now < end <= period_end and
            end - start <= dt.timedelta(seconds=1200),
            'Context development authorization scope, period or posture differs')
    selected_identity(selected['uid'], selected['gid'])
    return {'authorization_sha256': digest(raw),
            'not_before': value['not_before'], 'expires_at': value['expires_at'],
            'family_ref': selected['family_ref'], 'scope_ref': selected['scope_ref'],
            'episode_ref': selected['period_ref'],
            'authority_effect': 'none', 'actual_owner_outcome': None}


def validate_policy(raw, selected, authorization_raw, expected_authorization_sha256, now):
    """Validate policy against the exact supplied authorization byte preimage.

    A future effect adapter must obtain these bytes from the reviewed held
    reader and supply its independently pinned digest. This inert validator
    neither opens the Source path nor treats a caller result dict as proof.
    """
    value = closed_json(raw, MAX_POLICY_BYTES)
    exact_hash(expected_authorization_sha256)
    require(type(authorization_raw) is bytes and
            digest(authorization_raw) == expected_authorization_sha256,
            'exact held authorization digest required')
    auth_result = validate_authorization(authorization_raw, selected, now)
    require(set(value) == {'schema_version', 'host_uid', 'principal_ref', 'scope_ref',
                           'reader_public_key', 'not_before', 'expires_at',
                           'max_input_bytes', 'max_output_bytes', 'max_session_seconds',
                           'period_binding', 'allowed_operations', 'authority_effect',
                           'actual_owner_outcome'}, 'closed host policy required')
    selected_identity(selected['uid'], selected['gid'])
    start, end = instant(value['not_before']), instant(value['expires_at'])
    require(value['schema_version'] == 'lab-context-host-policy/v1-candidate' and
            type(value['host_uid']) is int and value['host_uid'] == selected['uid'] and
            value['principal_ref'] == selected['principal_ref'] and
            value['scope_ref'] == selected['scope_ref'] and
            value['period_binding'] == {'path': PERIOD_REL, 'sha256': PERIOD_SHA} and
            value['allowed_operations'] == ['context.get', 'session.open'] and
            value['authority_effect'] == 'none' and value['actual_owner_outcome'] is None and
            instant(selected['period_start']) <= instant(auth_result['not_before']) <=
            start <= now < end <=
            min(instant(selected['period_end']), instant(auth_result['expires_at'])) and
            end - start <= dt.timedelta(seconds=1200),
            'host policy scope, period or posture differs')
    for key, maximum in (('max_input_bytes', 1048576),
                         ('max_output_bytes', 2097152),
                         ('max_session_seconds', 900)):
        require(type(value[key]) is int and 1 <= value[key] <= maximum,
                'host policy budget differs')
    key = value['reader_public_key']
    require(type(key) is str, 'public key text required')
    try:
        decoded = base64.b64decode(key, validate=True)
    except ValueError as error:
        raise Refused('canonical public key encoding required') from error
    require(len(decoded) == 32 and base64.b64encode(decoded).decode() == key,
            '32-byte canonical public key required')
    selected_identity(selected['uid'], selected['gid'])
    return {'policy_sha256': digest(raw),
            'authorization_sha256': auth_result['authorization_sha256'],
            'expires_at': value['expires_at'],
            'authority_effect': 'none', 'actual_owner_outcome': None}


ORDER = ('SELECT_CLOSED_FAMILY', 'VALIDATE_CURRENT_PERIOD_AND_SCOPE',
         'CREATE_EXCLUSIVE_PRIVATE_ROOT_0700', 'GENERATE_ONE_USE_KEY_IN_PRIVATE_ROOT',
         'WRITE_EXCLUSIVE_POLICY_0600_NOFOLLOW', 'FSYNC_POLICY_AND_PARENT',
         'HELD_POLICY_READBACK_AND_PIN', 'CONSTRUCT_HOST_CHANNEL',
         'AUTHENTICATE_ONCE', 'CLOSE_CHANNEL', 'DROP_KEY_REFERENCE',
         'REMOVE_EXACT_OWNED_PRIVATE_ROOT', 'VERIFY_ABSENCE')


def synthetic_lifecycle(events):
    """Pure order/cleanup oracle; no filesystem, key or policy effect."""
    require(type(events) is list and all(type(e) is str for e in events),
            'synthetic events required')
    completed = []
    for event in events:
        require(len(completed) < len(ORDER) and event == ORDER[len(completed)],
                'private-root lifecycle order differs')
        completed.append(event)
    require(tuple(completed) == ORDER, 'private-root lifecycle incomplete')
    return {'status': 'SYNTHETIC_ORDER_ONLY', 'effect': 'NOT_RUN',
            'key_generated': False, 'grant_created': False,
            'policy_created': False, 'private_root_created': False}


def provision_actual(*_args, **_kwargs):
    raise Refused('effect disabled: fresh authority, private root and key require a disjoint reviewed release')


def launch_context(*_args, **_kwargs):
    raise Refused('effect disabled: complete Context role and writer are unselected')
