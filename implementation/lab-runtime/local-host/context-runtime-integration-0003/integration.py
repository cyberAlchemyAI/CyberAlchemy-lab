"""One-based bridge-aligned pure Context contract; all real effects refused."""
from __future__ import annotations

import base64
import binascii
import ast
from datetime import datetime, timedelta
import hashlib
import importlib.util
import json
from pathlib import Path

LOCAL = Path(__file__).resolve().parents[1]
PREVIOUS = LOCAL / 'context-runtime-integration-0001/integration.py'
PREVIOUS_SHA = '0388b1e1b811ed24835e7c35f5156ca3ee01fca9acb6e7a4b5ade209d0d67415'
REJECTED_PREDECESSOR = LOCAL / 'context-runtime-integration-0002/freeze.json'
REJECTED_PREDECESSOR_SHA = '9a618a98101fceefbcac44dfb7338da17ee99bf47a64b60c1da361547b4460de'
BRIDGE = LOCAL / 'context-bridge-0002/bridge.py'
BRIDGE_SHA = '5bf35088d43f781453ee8f4e9397a033bd2acdd671142a5a7c05adad709bb52a'
PERIOD_SHA = 'f2633ba3d6c9868740749a3e7d8f288ea7abb461246f964e64c5dc9bf8b14bca'
PERIOD_REL = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0001/packages/0001/period.json'
SCOPE = 'scope:cyberalchemy-lab-first-agent-episode'
CLAIM = 'Local disposable development episode only; no protected Source8 issuer grant or owner outcome.'


class Refused(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refused(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def previous():
    need(sha(PREVIOUS.read_bytes()) == PREVIOUS_SHA, 'PREVIOUS_DRIFT')
    spec = importlib.util.spec_from_file_location('context_runtime_integration_0001_frozen', PREVIOUS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def plan():
    need(sha(REJECTED_PREDECESSOR.read_bytes()) == REJECTED_PREDECESSOR_SHA,
         'REJECTED_PREDECESSOR_DRIFT')
    old = previous()
    value = old.proposed_topology()
    need(value['effect_enabled'] is False and value['context_source_manifest'] ==
         'REFUSED_PENDING_COMPLETE_INVERSE_AND_REAL_INPUTS', 'TOPOLOGY_CEILING')
    return value


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'DUPLICATE_KEY')
        result[key] = value
    return result


def parse(raw, limit, code):
    need(type(raw) is bytes and 0 < len(raw) <= limit, code)
    try:
        value = json.loads(raw, object_pairs_hook=_pairs)
    except (UnicodeError, ValueError, RecursionError):
        raise Refused(code) from None
    need(type(value) is dict, code)
    return value


def instant(value):
    need(type(value) is str and (value.endswith('Z') or value.endswith('+00:00')), 'TIME_FORMAT')
    try:
        time = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise Refused('TIME_FORMAT') from None
    need(time.tzinfo is not None and time.utcoffset() == timedelta(0), 'TIME_FORMAT')
    return time


def expected_leaves():
    first = ('request.json', 'authentication-proof.json', 'trusted-context.json',
             'host-permission-public.json')
    artifacts = tuple(f'artifacts/{i:02d}.json' for i in range(30))
    tail = ('artifact-index.json', 'delivery.json', 'lesson-selection.json',
            'delivery-provenance.json')
    result = first + artifacts + tail
    need(len(result) == 38, 'ORIGINAL_LEAF_MAP')
    return result


def bridge_wire_contract():
    """Extract the selected Client's ordinals from pinned public source, without import."""
    raw = BRIDGE.read_bytes()
    need(sha(raw) == BRIDGE_SHA, 'BRIDGE_DRIFT')
    tree = ast.parse(raw)
    clients = [node for node in tree.body if isinstance(node, ast.ClassDef) and
               node.name == 'Client']
    need(len(clients) == 1, 'BRIDGE_CLIENT_SHAPE')
    methods = {node.name: node for node in clients[0].body
               if isinstance(node, ast.FunctionDef)}

    def calls(name, op):
        found = [node for node in ast.walk(methods[name])
                 if isinstance(node, ast.Call) and
                 isinstance(node.func, ast.Attribute) and
                 isinstance(node.func.value, ast.Name) and
                 node.func.value.id == 'self' and node.func.attr == 'exchange' and
                 node.args and isinstance(node.args[0], ast.Constant) and
                 node.args[0].value == op]
        need(len(found) == 1, 'BRIDGE_CALL_SHAPE')
        return found[0]

    emit = calls('emit', 'EMIT')
    need(len(emit.args) == 4, 'BRIDGE_EMIT_SHAPE')
    ordinal = emit.args[1]
    rows = ast.parse('len(self.rows)', mode='eval').body
    need(isinstance(ordinal, ast.BinOp) and isinstance(ordinal.op, ast.Add) and
         ast.dump(ordinal.left) == ast.dump(rows) and
         isinstance(ordinal.right, ast.Constant) and
         type(ordinal.right.value) is int and ordinal.right.value == 1,
         'BRIDGE_EMIT_ORDINAL')
    release = calls('release_private', 'RELEASE_PRIVATE')
    finish = calls('emit', 'FINISH')
    need(len(release.args) == len(finish.args) == 2 and
         isinstance(release.args[1], ast.Constant) and release.args[1].value == 38 and
         isinstance(finish.args[1], ast.Constant) and finish.args[1].value == 41,
         'BRIDGE_TERMINAL_ORDINALS')
    return {'emit_offset': ordinal.right.value,
            'release_private_action_ordinal': release.args[1].value,
            'finish_ordinal': finish.args[1].value,
            'source_sha256': BRIDGE_SHA}


def expected_trace():
    """42 wire requests: EMIT1–38, separate release38, result39, manifest40, FINISH41."""
    contract = bridge_wire_contract()
    events = []
    for ordinal, leaf in enumerate(expected_leaves(), start=contract['emit_offset']):
        events += [f'send:{ordinal}:EMIT:{leaf}', f'ack:{ordinal}:EMIT:{leaf}']
    events += ['channel-closed', 'key-cleared',
               'send:38:RELEASE_PRIVATE', 'ack:38:RELEASE_PRIVATE',
               'private-root-absent']
    for ordinal, leaf in ((39, 'build-result.json'), (40, 'manifest.json')):
        events += [f'send:{ordinal}:EMIT:{leaf}', f'ack:{ordinal}:EMIT:{leaf}']
    events += ['send:41:FINISH', 'writer-validated-original-profile',
               'writer-closed', 'ack:41:FINISH', 'client-closed',
               'original-summary', 'child-exit-0', 'parent-closed']
    need(sum(value.startswith('send:') for value in events) == 42 and
         sum(value.startswith('ack:') for value in events) == 42, 'REQUEST_COUNT')
    return tuple(events)


def _held(method_owner, method, code):
    need(hasattr(method_owner, method), code)
    value = getattr(method_owner, method)()
    need(type(value) is dict, code)
    return value


def check_synthetic(held_source, held_auth, held_policy, receipt, observed_at):
    """Checks synthetic held-reader interfaces; never confers real authority."""
    topology = plan()
    receipt_keys = {'uid', 'gid', 'namespace_count', 'source_mode',
                    'auth_dir_mode', 'auth_leaf_mode', 'root_mount', 'native_mount',
                    'child_output_mount', 'private_root_outside_public',
                    'post_ack_readback', 'manifest_rows', 'leaves',
                    'finish_ordinal', 'trace'}
    need(type(receipt) is dict and set(receipt) == receipt_keys, 'RECEIPT_FIELDS')
    family = previous()._load('context-family-0001/selection.json')['family']
    source = _held(held_source, 'read_current_signed', 'SOURCE_ORACLE')
    need(set(source) == {'period_raw', 'scope_ref', 'family_ref', 'source_manifest_sha256',
                         'source_package_sha256', 'reader_open_signed', 'source_guarded',
                         'package_guarded', 'held_origin'} and
         source['held_origin'] == 'synthetic-held-reader' and
         source['reader_open_signed'] is True and source['source_guarded'] is True and
         source['package_guarded'] is True and source['scope_ref'] == SCOPE and
         source['source_manifest_sha256'] == family['source_manifest_sha256'] and
         source['source_package_sha256'] == family['source_package_sha256'] and
         source['family_ref'] == topology['stage_root'] + '/' + topology['source_role'],
         'SIGNED_SOURCE_MODEL')
    need(type(source['period_raw']) is bytes, 'SOURCE_PERIOD_BYTES')
    need(sha(source['period_raw']) == PERIOD_SHA, 'SOURCE_PERIOD_BINDING')
    period = parse(source['period_raw'], 16384, 'SOURCE_PERIOD_BYTES')
    need(period.get('schema_version') == 'lab-owned-absolute-participation-period/v1-candidate' and
         period.get('period_ref') == 'protocol:R03-docker-source-20261020-0001-period/v1' and
         period.get('authority_effect') == 'none' and period.get('actual_owner_outcome') is None,
         'SOURCE_PERIOD_PROFILE')
    start, end, now = instant(period['not_before']), instant(period['expires_at']), instant(observed_at)
    need(start <= now < end, 'SOURCE_PERIOD_CURRENT')

    auth = _held(held_auth, 'read_selected_authorization', 'AUTH_ORACLE')
    need(type(auth.get('raw')) is bytes, 'AUTH_BYTES')
    need(set(auth) == {'raw', 'sha256', 'path', 'uid', 'gid', 'mode', 'held_origin'} and
         auth['held_origin'] == 'synthetic-held-auth' and
         auth['path'] == topology['stage_root'] + '/' + topology['auth_path'] and
         auth['sha256'] == sha(auth['raw']) and auth['mode'] == '0600' and
         type(auth['uid']) is int and auth['uid'] > 0 and
         type(auth['gid']) is int and auth['gid'] >= 0, 'AUTH_HELD_MODEL')
    value = parse(auth['raw'], 16384, 'AUTH_BYTES')
    need(set(value) == {'schema_version', 'family_ref', 'episode_ref', 'scope_ref',
                        'period_binding', 'not_before', 'expires_at', 'authority_effect',
                        'actual_owner_outcome', 'claim_ceiling'} and
         value['schema_version'] == 'lab-context-development-authorization/v1-candidate' and
         value['family_ref'] == topology['stage_root'] + '/' +
         'product/lab/release-candidates/v1/interface/docker-context-20261020-0001' and
         value['episode_ref'] == period['period_ref'] and
         value['scope_ref'] == source['scope_ref'] and
         value['period_binding'] == {'path': PERIOD_REL, 'sha256': PERIOD_SHA} and
         value['authority_effect'] == 'none' and value['actual_owner_outcome'] is None and
         value['claim_ceiling'] == CLAIM, 'AUTH_PROFILE_JOIN')
    auth_start, auth_end = instant(value['not_before']), instant(value['expires_at'])
    need(start <= auth_start <= now < auth_end <= end, 'AUTH_WITHIN_SOURCE_PERIOD')

    policy = _held(held_policy, 'read_selected_policy', 'POLICY_ORACLE')
    need(type(policy.get('raw')) is bytes, 'POLICY_BYTES')
    need(set(policy) == {'raw', 'sha256', 'path', 'uid', 'gid', 'mode', 'held_origin'} and
         policy['held_origin'] == 'synthetic-held-policy' and
         policy['path'] == topology['private_policy_root'] + '/permission.json' and
         policy['sha256'] == sha(policy['raw']) and policy['mode'] == '0600' and
         type(policy['uid']) is int and policy['uid'] > 0 and
         type(policy['gid']) is int and policy['gid'] >= 0 and
         type(receipt['uid']) is int and receipt['uid'] > 0 and
         type(receipt['gid']) is int and receipt['gid'] >= 0 and
         policy['uid'] == auth['uid'] == receipt.get('uid') and
         policy['gid'] == auth['gid'] == receipt.get('gid'), 'POLICY_HELD_MODEL')
    p = parse(policy['raw'], 16384, 'POLICY_BYTES')
    need(set(p) == {'schema_version', 'host_uid', 'principal_ref', 'scope_ref',
                    'reader_public_key', 'not_before', 'expires_at',
                    'max_input_bytes', 'max_output_bytes', 'max_session_seconds',
                    'period_binding', 'allowed_operations', 'authority_effect',
                    'actual_owner_outcome'} and
         p['schema_version'] == 'lab-context-host-policy/v1-candidate' and
         p['authority_effect'] == 'none' and p['actual_owner_outcome'] is None and
         p['scope_ref'] == source['scope_ref'] and
         p['principal_ref'] == period['principal_ref'] and
         p['host_uid'] == policy['uid'] and
         p['period_binding'] == {'path': PERIOD_REL, 'sha256': PERIOD_SHA} and
         p['allowed_operations'] == ['context.get', 'session.open'] and
         type(p['max_input_bytes']) is int and p['max_input_bytes'] == 1048576 and
         type(p['max_output_bytes']) is int and p['max_output_bytes'] == 2097152 and
         type(p['max_session_seconds']) is int and p['max_session_seconds'] == 900 and
         type(p['reader_public_key']) is str, 'POLICY_JOIN')
    try:
        key = base64.b64decode(p['reader_public_key'], validate=True)
    except (ValueError, binascii.Error):
        raise Refused('POLICY_KEY_SHAPE') from None
    need(len(key) == 32, 'POLICY_KEY_SHAPE')
    policy_start, policy_end = instant(p['not_before']), instant(p['expires_at'])
    need(auth_start <= policy_start <= now < policy_end <= auth_end, 'POLICY_WITHIN_AUTH')
    need(receipt['namespace_count'] == 1571 and
         receipt['source_mode'] == receipt['auth_dir_mode'] == '0700' and
         receipt['auth_leaf_mode'] == '0600' and
         receipt['root_mount'] == receipt['native_mount'] == receipt['child_output_mount'] == 'ro' and
         receipt['private_root_outside_public'] is True and receipt['post_ack_readback'] is True and
         receipt['manifest_rows'] == 39 and receipt['leaves'] == 40 and
         receipt['finish_ordinal'] == 41 and type(receipt['trace']) is list and
         tuple(receipt['trace']) == expected_trace(), 'COMPLETE_42_REQUEST_TRACE')
    return {'status': 'SYNTHETIC_COMPLETE_TRACE_ONLY', 'effect_enabled': False,
            'source_scope_origin': 'synthetic-held-reader',
            'private_root_absence_origin': 'synthetic-receipt',
            'actual_source_read': False, 'real_context': 'NOT_RUN'}


def launch(*_args, **_kwargs):
    raise Refused('effect disabled: final staged body, source manifest, issuer and original Context remain unselected')
