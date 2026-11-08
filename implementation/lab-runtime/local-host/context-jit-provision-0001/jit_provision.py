"""Effect-disabled Context JIT construction and exact role projection.

All inputs to policy construction are synthetic/caller supplied. No private key,
authorization, private root, grant or Context role is created here.
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import importlib.util
import json
import os
import stat
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
LOCAL = REPO / 'implementation/lab-runtime/local-host'
HERE = Path(__file__).resolve().parent
STAGE_ROOT = Path('/tmp/cal-context-family-20261020-0001/root')
INTERFACE = Path('product/lab/release-candidates/v1/interface')
CONTEXT_FAMILY = STAGE_ROOT / INTERFACE / 'docker-context-20261020-0001'
SOURCE_FAMILY = STAGE_ROOT / INTERFACE / 'docker-source-20261020-0001'
PRIVATE_ROOT = Path('/tmp/cal-context-jit-private-20261020-0001')
SCOPE = 'scope:cyberalchemy-lab-first-agent-episode'
SOURCE_APPROVAL_SHA = '1dfa7d55643631d9669ea1e40bef329300a0a2939d736d36fd84f1a7a0453dfe'
SOURCE_MANIFEST = Path('/tmp/cal-mapper-only-dev-20261020-0001-release3/root/product/lab/release-candidates/v1/interface/docker-source-20261020-0001/packages/0001/manifest.json')
SOURCE_MANIFEST_SHA = 'f132b3e1908e9e116464ad29c3db7f56ca17d4dee080e60ffa62547dd9588a5b'
STAGE_FREEZE_SHA = '8e7194585a4a98ce4a6ed906ef349449457335aba2060229c1d105eac36021b8'
STAGE_SELECTION_SHA = '6721210d076da6462f904b2836a9e3ff5853be92f395a05ee2b141b517e078bf'
STAGE_BUILD_SHA = 'fdffe962bc6c745860d302f1911e094d6e6364403020e91d8cb6fbf93d58b48c'
STAGE_CONTROL_SHA = '1d0cf363ecd6a3b45e9abd278bc19be97a79f333a1128c5005b4b5060f92c06f'
JIT_FREEZE_SHA = 'e0286814e0e34770a0fa4b7fe0d9ab08161e5ea3264386c9f0b6cb76f201a391'
JIT_REVIEW_SHA = 'c974bf13f7a181ca1b3435c5cf2440258096d2f28155601b152936818c6b1c31'
JIT_CODE_SHA = 'f40ca49a9f9f72e1c8490d753633c1db4307736a1b2f41080ee8a5f684c33a7a'
PINS = {
    LOCAL / 'context-stage-0001/freeze.json': STAGE_FREEZE_SHA,
    LOCAL / 'context-stage-0001/selection.json': STAGE_SELECTION_SHA,
    LOCAL / 'context-stage-0001/generated/context/build.py': STAGE_BUILD_SHA,
    LOCAL / 'context-stage-0001/generated/context/control.py': STAGE_CONTROL_SHA,
    LOCAL / 'context-jit-policy-0002/freeze.json': JIT_FREEZE_SHA,
    LOCAL / 'CONTEXT-JIT-POLICY-INDEPENDENT-STATIC-REVIEW-0002.md': JIT_REVIEW_SHA,
    LOCAL / 'context-jit-policy-0002/jit_policy.py': JIT_CODE_SHA,
    HERE / 'source-approval.json': SOURCE_APPROVAL_SHA,
    SOURCE_MANIFEST: SOURCE_MANIFEST_SHA,
}

class Refused(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise Refused(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned_public(path, pin):
    """Bounded no-follow public preimage read; no archive body path is accepted."""
    require(path in PINS and pin == PINS[path], 'unselected public preimage')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                0 < before.st_size <= 2 * 1024 * 1024, 'bounded public file required')
        raw = os.read(fd, before.st_size + 1)
        after = os.fstat(fd)
        require(len(raw) == before.st_size and
                (before.st_dev, before.st_ino, before.st_mode, before.st_size) ==
                (after.st_dev, after.st_ino, after.st_mode, after.st_size) and
                sha(raw) == pin, 'public preimage changed')
        return raw
    finally:
        os.close(fd)


def reviewed_inputs():
    for path, pin in PINS.items():
        pinned_public(path, pin)
    approval = json.loads(pinned_public(HERE / 'source-approval.json', SOURCE_APPROVAL_SHA))
    require(approval['authorized_domain_scope_refs'] == [SCOPE],
            'selected public Source approval scope differs')
    manifest = json.loads(pinned_public(SOURCE_MANIFEST, SOURCE_MANIFEST_SHA))
    require(sum(row == {'path':
                'product/lab/release-candidates/v1/interface/docker-source-20261020-0001/packages/0001/approval.json',
                'sha256': SOURCE_APPROVAL_SHA} for row in manifest['files']) == 1,
            'Source package manifest does not bind selected approval')
    stage = json.loads(pinned_public(LOCAL / 'context-stage-0001/selection.json', STAGE_SELECTION_SHA))
    require(stage['future_exclusive_stage_root'] == str(STAGE_ROOT) and
            stage['effect'] == 'NOT_RUN' and stage['authorization_sha256'] == 'DUMMY_UNMINTED',
            'selected future Context stage differs')
    return {'source_approval_sha256': SOURCE_APPROVAL_SHA,
            'source_scope_ref': SCOPE, 'stage_root': str(STAGE_ROOT),
            'stage_effect': 'NOT_RUN', 'preimages': len(PINS)}


def jit_module():
    path = LOCAL / 'context-jit-policy-0002/jit_policy.py'
    pinned_public(path, JIT_CODE_SHA)
    spec = importlib.util.spec_from_file_location('_context_jit_policy_0002_inert', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(module.EFFECT_ENABLED is False, 'reviewed JIT policy must be inert')
    return module


def select_context(period_raw, now, signed_scope_ref):
    """Pin the expected scope; signed_scope_ref is an effect-time obligation.

    Caller values here cannot prove a protected signed Source view. The future
    adapter must obtain this field from Reader.open_signed and compare it.
    """
    reviewed_inputs()
    require(type(signed_scope_ref) is str and signed_scope_ref == SCOPE,
            'signed Source view scope differs from approved expected scope')
    jit = jit_module()
    spec = {'family_ref': str(CONTEXT_FAMILY), 'source_root': str(SOURCE_FAMILY),
            'private_root': str(PRIVATE_ROOT), 'uid': os.getuid(), 'gid': os.getgid(),
            'principal_ref': 'principal:R03-docker-source-20261020-0001',
            'scope_ref': SCOPE, 'reader_code_sha256': jit.READER_CODE_SHA,
            'reader_manifest_sha256': jit.READER_MANIFEST_SHA,
            'source_package_sha256': jit.SOURCE_PACKAGE_SHA,
            'mapper_package_sha256': jit.MAPPER_PACKAGE_SHA,
            'period_sha256': jit.PERIOD_SHA}
    selected = jit.select(spec, period_raw, now)
    require(selected['authorization_path'] == str(SOURCE_FAMILY / 'authorization/context-development.json') and
            selected['policy_path'] == str(PRIVATE_ROOT / 'permission.json') and
            selected['family_ref'] == str(CONTEXT_FAMILY),
            'Source, Context or private policy topology differs')
    return selected


def wire(value):
    return (json.dumps(value, indent=2, sort_keys=True,
                       ensure_ascii=False, allow_nan=False) + '\n').encode()


def stamp(value):
    require(type(value) is dt.datetime and value.tzinfo is not None and
            value.utcoffset() == dt.timedelta() and value.microsecond == 0,
            'whole-second UTC timestamp required')
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')


def construct_policy(selected, authorization_raw, authorization_sha256,
                     public_key_raw, now):
    """Construct original-format policy from supplied public key only.

    This function never generates or holds Ed25519 private material.
    """
    jit = jit_module()
    require(type(public_key_raw) is bytes and len(public_key_raw) == 32,
            '32-byte Ed25519 public key required')
    Ed25519PublicKey.from_public_bytes(public_key_raw)
    auth = jit.validate_authorization(authorization_raw, selected, now)
    require(auth['authorization_sha256'] == authorization_sha256,
            'held authorization digest differs')
    end = min(now + dt.timedelta(seconds=1200),
              jit.instant(auth['expires_at']), jit.instant(selected['period_end']))
    require(end > now, 'no current bounded policy interval')
    policy = {
        'schema_version': 'lab-context-host-policy/v1-candidate',
        'host_uid': selected['uid'], 'principal_ref': selected['principal_ref'],
        'scope_ref': selected['scope_ref'],
        'reader_public_key': base64.b64encode(public_key_raw).decode(),
        'not_before': stamp(now), 'expires_at': stamp(end),
        'max_input_bytes': 1048576, 'max_output_bytes': 2097152,
        'max_session_seconds': 900,
        'period_binding': {'path': jit.PERIOD_REL, 'sha256': jit.PERIOD_SHA},
        'allowed_operations': ['context.get', 'session.open'],
        'authority_effect': 'none', 'actual_owner_outcome': None,
    }
    raw = wire(policy)
    proof = jit.validate_policy(raw, selected, authorization_raw,
                                authorization_sha256, now)
    require(proof['authorization_sha256'] == authorization_sha256 and
            proof['policy_sha256'] == sha(raw), 'policy and authorization join differs')
    return raw, proof


def sub_once(raw, old, new, label):
    old, new = old.encode(), new.encode()
    require(raw.count(old) == 1, 'selected ' + label + ' site differs')
    result = raw.replace(old, new, 1)
    require(result.replace(new, old, 1) == raw, 'projection inverse differs: ' + label)
    return result


def project_roles():
    """Return inert build/control projection bytes; never import either role."""
    reviewed_inputs()
    build = pinned_public(LOCAL / 'context-stage-0001/generated/context/build.py', STAGE_BUILD_SHA)
    control = pinned_public(LOCAL / 'context-stage-0001/generated/context/control.py', STAGE_CONTROL_SHA)
    source_expr = "ROOT / 'product/lab/release-candidates/v1/interface/docker-source-20261020-0001'"
    control = sub_once(control,
                       "AUTH = ROOT / 'authorization/context-development.json'",
                       "AUTH = " + source_expr + " / 'authorization/context-development.json'",
                       'AUTH path')
    control = sub_once(control, 'read_auth_bytes(AUTH, ROOT, AUTH_SHA, os.geteuid())',
                       'read_auth_bytes(AUTH, ' + source_expr + ', AUTH_SHA, os.geteuid())',
                       'held AUTH root')
    control = sub_once(control, "value['family_ref'] == str(HERE.parent)",
                       "value['family_ref'] == str(HERE)", 'Context family')
    build = sub_once(build, 'def provision(path, source):\n',
                     'def provision(path, source):\n    _t35_effect_refused()\n',
                     'direct provision gate')
    build = sub_once(build,
                     'with reader.open_signed(SOURCE_PIN, SOURCE_PACKAGE) as source, _t35_effect_refused() as tmp:',
                     'with reader.open_signed(SOURCE_PIN, SOURCE_PACKAGE) as source, _jit_private_root() as tmp:',
                     'exact private root site')
    build = sub_once(build, '        root = Path(tmp)\n        _t35_effect_refused()\n',
                     '        root = Path(tmp)\n        require(root == JIT_PRIVATE_ROOT, "selected exclusive private root differs")\n        _t35_effect_refused()\n',
                     'private root equality')
    build = sub_once(build, 'return (key, sha(path.read_bytes()))',
                     'return (key, sha(read_policy_bytes(path, path.parent, ROOT, sha(encoded(policy)), os.geteuid(), os.getegid())))',
                     'held policy post-write read')
    build = sub_once(build, "emit(out / 'host-permission-public.json', load(policy_path))",
                     "emit(out / 'host-permission-public.json', EL.parse(read_policy_bytes(policy_path, policy_path.parent, ROOT, policy_pin, os.geteuid(), os.getegid())))",
                     'held public policy read')
    anchor = b"SOURCE_PACKAGE = 'f132b3e1908e9e116464ad29c3db7f56ca17d4dee080e60ffa62547dd9588a5b'\n"
    require(build.count(anchor) == 1, 'selected build anchor differs')
    private_definition = ("JIT_PRIVATE_ROOT = Path('" + str(PRIVATE_ROOT) + "')\n"
                          "def _jit_private_root():\n"
                          "    _t35_effect_refused()\n").encode()
    build = build.replace(anchor, anchor + private_definition, 1)
    require(b'path.read_bytes()' not in build and b'load(policy_path)' not in build and
            b'AUTH.read_bytes()' not in control and
            b'def read_auth_bytes(' in control and b'def read_policy_bytes(' in control,
            'path-based AUTH or policy read remains')
    compile(build, '<inert-projected-context-build>', 'exec')
    compile(control, '<inert-projected-context-control>', 'exec')
    return {'build.py': build, 'control.py': control}


LIFECYCLE = ('PIN_PUBLIC_PREIMAGES', 'OPEN_SIGNED_SOURCE_VIEW',
             'VALIDATE_CURRENT_SCOPE_PERIOD', 'HELD_AUTH_READ_AND_PIN',
             'CREATE_EXCLUSIVE_PRIVATE_ROOT_0700', 'GENERATE_ONE_USE_ED25519_KEY',
             'CONSTRUCT_POLICY_20MIN_MAX', 'WRITE_EXCLUSIVE_POLICY_0600_NOFOLLOW',
             'FSYNC_POLICY_AND_PARENT', 'HELD_POLICY_READBACK_AND_PIN',
             'OPEN_HOST_CHANNEL', 'AUTHENTICATE_ONCE', 'CLOSE_HOST_CHANNEL',
             'DROP_KEY_REFERENCE', 'REMOVE_EXACT_OWNED_PRIVATE_ROOT',
             'VERIFY_PRIVATE_ROOT_ABSENT', 'RECORD_ATTEMPT_CONSUMED')


def synthetic_lifecycle(events, failure_at=None, cleanup='clean'):
    """Pure rollback oracle. No actual filesystem, key or channel operation."""
    require(type(events) is list and all(type(x) is str for x in events),
            'synthetic lifecycle events required')
    require(cleanup in ('clean', 'uncertain'), 'closed cleanup outcome required')
    if failure_at is None:
        require(cleanup == 'clean' and tuple(events) == LIFECYCLE,
                'successful JIT lifecycle differs')
        return {'status': 'SYNTHETIC_SUCCESS_ORDER', 'effect': 'NOT_RUN',
                'attempt_reusable': False}
    require(failure_at in LIFECYCLE, 'selected failure point required')
    prefix = LIFECYCLE[:LIFECYCLE.index(failure_at)]
    if cleanup == 'clean':
        suffix = ('ROLLBACK_CLOSE_CHANNEL_IF_OPEN', 'ROLLBACK_DROP_KEY_IF_CREATED',
                  'ROLLBACK_REMOVE_ONLY_OWNED_PRIVATE_ROOT_IF_CREATED',
                  'ROLLBACK_VERIFY_OWNED_ROOT_ABSENT', 'RECORD_ATTEMPT_CONSUMED')
        status = 'SYNTHETIC_ROLLBACK_ORDER'
    else:
        suffix = ('ROLLBACK_CLOSE_CHANNEL_IF_OPEN', 'ROLLBACK_DROP_KEY_IF_CREATED',
                  'PRESERVE_UNKNOWN_EFFECT_EVIDENCE', 'RECORD_UNKNOWN_REFUSE_REUSE')
        status = 'SYNTHETIC_UNKNOWN_PRESERVED'
    require(tuple(events) == prefix + ('FAIL:' + failure_at,) + suffix,
            'failure rollback or ownership boundary differs')
    return {'status': status, 'effect': 'NOT_RUN', 'attempt_reusable': False}


def generate_private_key(*_args, **_kwargs):
    raise Refused('effect disabled: no Ed25519 private key generation')


def write_authorization_or_policy(*_args, **_kwargs):
    raise Refused('effect disabled: no authorization, private root or host policy write')


def launch_context(*_args, **_kwargs):
    raise Refused('effect disabled: no Context import or launch')
