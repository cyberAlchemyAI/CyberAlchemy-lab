"""Fixture-only signed Agent challenge grant for a *live* current Source8 Session.

The selected API must supply actual in-process Session/Agent records and a live
guard. This module selects signed Source records and constrains a one-call
technical grant; it neither authenticates the host callback nor dispatches an
API operation. Private issuer material is never read from or written to Git.
"""
from __future__ import annotations

import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import jsonschema


ROOT = Path(__file__).absolute().parents[4]
FAMILY = ('implementation/lab-runtime/local-host/source8-current-fixture/'
          'instances/legacy-local-14aa76257d0ab568')
SOURCE_SHA = 'f8470ce8b4d5eabefbd6e127c4653b1d663b0596fb1fa73cf32e45b5930ced88'
PACKAGE_SHA = '5fa4f08513131810e21d6d04f3fed5c6fa27a4d034818166d8f3f8b216edb3ea'
INDEX_SHA = '4134ff50f90ae8ad89de0f969ac49dfe4429652f734052450ec74d54394b4108'
COLD_SHA = '95c08692d45fa0a123a725a93654fc76d4a6c6173041764fc1a64f46cbc7086e'
PERIOD_SHA = '06e89b3b96c1d0603ab3f86e49797dadca15a76ace8291929bc6ed98ee580e74'
WORK_SHA = 'ca7dd71c1249ff10c978566f6265bad2ab5b9930c44896833f3003c7ca14364c'
CONTRACT_SHA = 'f71a8628bfba94171e94af1ec8cf827d2452293390b04dba204fa6d3aefabb9d'
MAPPING_SHA = 'e5352b2d7d74a215138451fab6a8a0bb1c598caddf41d71a4fba69251a032a0b'
DELIVERY_SHA = '655497b69f22a3a6d4905be2789b6d84e4a4f24568d97fc32aaddf2b836e4126'
SCHEMAS = {
    'agent-instance': '0dc09d05ec9c932a6073c1cab41e6a81e9ea3a85116e21b1789923ad6915bf30',
    'agent-session': 'e05780ad1ee2f87cc4bc288a05cca24c6e0ac35e97771ff689de0ec64d14aae8',
    'agent-assignment': '39ae5be3a8242d414b6929efaa7516e56657f39d0d7731b53a13f4de43276812',
}
STORE = 'completion-legacy-local-14aa76257d0ab568'
SCOPE = 'project:cyberalchemy-v2-to-lab-migration'
GRANT_VERSION = 'lab-local-r03-0005-agent-challenge-grant/v1-fixture'
PAYLOAD_FIELDS = {
    'schema_version', 'grant_id', 'issuer_ref', 'issuer_public_sha256', 'operation',
    'host_uid', 'principal_ref', 'scope_ref', 'source_manifest_binding',
    'source_package_binding', 'source_cut', 'work_binding', 'work_ref',
    'contract_binding', 'contract_ref', 'assignment_binding', 'assignment_ref',
    'agent_instance_ref', 'session_ref', 'context_view_ref',
    'context_delivery_binding', 'allowed_grounds', 'allowed_response_modes',
    'required_evidence_kinds', 'not_before', 'expires_at', 'max_actions',
    'revoked', 'authority_effect', 'owner_decision', 'contest_outcome',
}


class Refused(ValueError):
    pass


def need(value, reason):
    if not value:
        raise Refused(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def exact(path, digest):
    """Capture exact regular-file bytes without following any path component."""
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts, 'selected path is not closed')
    directory = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in path.parts[1:-1]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
        try:
            info = os.fstat(fd)
            need(stat.S_ISREG(info.st_mode) and info.st_size <= 16 * 1024 * 1024,
                 'selected file is not bounded regular input')
            with os.fdopen(fd, 'rb', closefd=False) as stream:
                raw = stream.read()
        finally:
            os.close(fd)
    except OSError as error:
        raise Refused('selected path missing or linked') from error
    finally:
        os.close(directory)
    need(sha(raw) == digest, 'selected bytes changed')
    return raw


def selected(relative, digest):
    need(type(relative) is str and relative and not relative.startswith('/')
         and '..' not in Path(relative).parts and Path(relative).as_posix() == relative,
         'noncanonical repository locator')
    return exact(ROOT / relative, digest)


def utc(value):
    need(type(value) is str, 'UTC instant required')
    try:
        instant = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as error:
        raise Refused('invalid UTC instant') from error
    need(instant.tzinfo is not None and instant.utcoffset().total_seconds() == 0,
         'UTC instant required')
    return instant.astimezone(timezone.utc)


def cut_shape(value):
    if type(value) is not dict or set(value) != {'store_ref', 'branch_ref', 'commit_sequence',
                                                'commit_sha256', 'source_profile_sha256', 'streams'}:
        return False
    if (value['store_ref'] != STORE or value['branch_ref'] != 'branch:' + STORE
            or type(value['commit_sequence']) is not int or value['commit_sequence'] < 1
            or not all(type(value[k]) is str and re.fullmatch('[0-9a-f]{64}', value[k])
                       for k in ('commit_sha256', 'source_profile_sha256'))
            or type(value['streams']) is not list or len(value['streams']) != 2):
        return False
    refs = set()
    for row in value['streams']:
        if (type(row) is not dict or set(row) != {'stream_ref', 'cursor', 'head_sha256'}
                or type(row['stream_ref']) is not str or row['stream_ref'] in refs
                or type(row['cursor']) is not int or row['cursor'] < 0
                or type(row['head_sha256']) is not str
                or not re.fullmatch('[0-9a-f]{64}', row['head_sha256'])):
            return False
        refs.add(row['stream_ref'])
    return refs == {'project-semantic-event-history', 'project-governance-event-history'}


def native_cut():
    """Select one actual signed Source cut joined through Mapper and Context."""
    mapping = json.loads(selected(FAMILY + '/mapped/packages/0001/mapping.json', MAPPING_SHA))
    delivery = json.loads(selected(FAMILY + '/context/packages/0001/delivery.json', DELIVERY_SHA))
    cut = mapping['source_cut']
    need(cut_shape(cut) and delivery['source_cut'] == cut
         and mapping['source_package_binding'] == {
             'path': FAMILY + '/source/packages/0001/manifest.json', 'sha256': PACKAGE_SHA}
         and mapping['authority_effect'] == 'none'
         and delivery['authority_effect'] == 'none'
         and delivery['posture'] == 'ready' and delivery['scope_enforced'] is True,
         'native Source, Mapper or Context cut differs')
    return cut


def source_records():
    """Recheck the signed candidate family and return its exact original bodies."""
    base = FAMILY + '/source/'
    manifest = json.loads(selected(base + 'source-manifest.json', SOURCE_SHA))
    package = json.loads(selected(base + 'packages/0001/manifest.json', PACKAGE_SHA))
    cold = json.loads(selected(FAMILY + '/cold-result.json', COLD_SHA))
    period = json.loads(selected(base + 'packages/0001/period.json', PERIOD_SHA))
    index = json.loads(selected(base + 'packages/0001/record-index.json', INDEX_SHA))
    need(manifest['construction_status'] == 'construction-bound-unqualified' and manifest['authority_effect'] == 'none'
         and package['source_manifest_binding'] == {'path': base + 'source-manifest.json', 'sha256': SOURCE_SHA}
         and cold['result'] == 'PASS-native-cold' and cold['independent_cold_replays'] == 2
         and cold['original_byte_parity'] is True
         and cold['source_binding'] == {'path': base + 'source-manifest.json', 'sha256': SOURCE_SHA}
         and cold['package_binding'] == {'path': base + 'packages/0001/manifest.json', 'sha256': PACKAGE_SHA}
         and cold['period_binding'] == {'path': base + 'packages/0001/period.json', 'sha256': PERIOD_SHA},
         'signed Source or cold proof differs')
    need(type(index) is list and len(index) == 22, 'signed record index differs')
    by_kind = {}
    for row in index:
        if row['kind'] in ('principal', 'work', 'challenge-contract', 'agent-profile',
                           'agent-assignment', 'agent-capability', 'implementation'):
            need(row['kind'] not in by_kind, 'duplicate selected kind')
            pin = row['original_binding']
            raw = selected(pin['path'], pin['sha256'])
            body = json.loads(raw)
            need(body['kind'] == row['kind'] and body['node_id'] + '@1.0.0-candidate.1' == row['version_ref']
                 and body['scope_ref'] == SCOPE and body['authority_effect'] == 'none',
                 'signed original identity or scope differs')
            by_kind[row['kind']] = {'body': body, 'binding': pin, 'version_ref': row['version_ref']}
    need(set(by_kind) == {'principal', 'work', 'challenge-contract', 'agent-profile',
                          'agent-assignment', 'agent-capability', 'implementation'},
         'signed contest inputs incomplete')
    need(by_kind['work']['binding']['sha256'] == WORK_SHA
         and by_kind['challenge-contract']['binding']['sha256'] == CONTRACT_SHA
         and by_kind['agent-assignment']['body']['payload']['work_ref'] == by_kind['work']['version_ref']
         and by_kind['agent-assignment']['body']['payload']['eligible_agent_ref'] == by_kind['agent-profile']['version_ref']
         and by_kind['agent-profile']['body']['payload']['policy_refs'] != []
         and by_kind['challenge-contract']['body']['payload']['eligible_challenger_kinds'] == ['agent-instance']
         and by_kind['challenge-contract']['body']['payload']['required_evidence_kinds'] == ['source', 'validation-receipt']
         and by_kind['challenge-contract']['body']['lifecycle_state'] == 'candidate',
         'signed Work, Assignment or candidate Contract differs')
    schema = json.loads(selected('authority/artifact-types/agent-assignment/v1/schema.json',
                                 SCHEMAS['agent-assignment']))
    jsonschema.Draft202012Validator(schema).validate(by_kind['agent-assignment']['body'])
    need(utc(period['not_before']) < utc(period['expires_at']), 'signed Source period is empty')
    return by_kind, period


def project_live(live, selected_cut, now, host_uid, host_policy_expires, grant_id,
                 issuer_public_raw, live_guard):
    """Constrain grant payload from API-supplied *actual live* records.

    The API must bind live_guard to its selected ContextSessions resource and
    recheck it at effect time; this module cannot authenticate a supplied
    callback or create an Agent Session.
    """
    need(callable(live_guard) and live_guard() is True, 'live Session guard refused')
    by_kind, period = source_records()
    need(type(live) is dict and set(live) == {'agent_record', 'session_record',
                                             'session_result', 'context_view_header',
                                             'context_delivery_binding'},
         'live Agent evidence shape differs')
    need(selected_cut == native_cut(), 'wrong current Source cut')
    need(type(now) is datetime and now.tzinfo is not None and type(host_uid) is int
         and host_uid == os.getuid() and type(grant_id) is str
         and re.fullmatch(r'grant:R03-0005:[a-f0-9]{32}', grant_id)
         and type(issuer_public_raw) is bytes and len(issuer_public_raw) == 32,
         'host identity or technical issuer differs')
    moment = now.astimezone(timezone.utc)
    end = min(utc(period['expires_at']), utc(host_policy_expires),
              utc(live['session_result']['expires_at']))
    need(utc(period['not_before']) <= moment < end, 'Source, host or Session lease expired')
    agent, session, result = (live[key] for key in ('agent_record', 'session_record', 'session_result'))
    header = live['context_view_header']
    delivery = live['context_delivery_binding']
    need(type(header) is dict and set(header) == {'identity_ref', 'version_ref',
                                                  'carrier_ref', 'scope_ref', 'byte_sha256'}
         and header['carrier_ref'] == 'cal.artifact-type.context-view/v1'
         and header['scope_ref'] == SCOPE
         and type(header['byte_sha256']) is str
         and re.fullmatch('[0-9a-f]{64}', header['byte_sha256'])
         and type(delivery) is dict and set(delivery) == {'ref', 'sha256'}
         and type(delivery['ref']) is str and delivery['ref']
         and type(delivery['sha256']) is str
         and re.fullmatch('[0-9a-f]{64}', delivery['sha256']),
         'live Context view or delivery binding differs')
    for kind, body in (('agent-instance', agent), ('agent-session', session)):
        schema = json.loads(selected('authority/artifact-types/' + kind + '/v1/schema.json', SCHEMAS[kind]))
        jsonschema.Draft202012Validator(schema).validate(body)
    need(result['schema_version'] == 'lab-agent-session-result/v1-candidate'
         and result['posture'] == 'active' and result['authority_effect'] == 'none'
         and result['source_cut'] == selected_cut
         and result['session_ref'] == session['node_id']
         and result['agent_instance_ref'] == agent['node_id']
         and session['payload']['agent_instance_ref'] == agent['node_id']
         and agent['payload']['session_ref'] == session['node_id']
         and session['payload']['termination_state'] == 'active'
         and session['payload']['assignment_ref'] == by_kind['agent-assignment']['version_ref']
         and agent['payload']['profile_ref'] == by_kind['agent-profile']['version_ref']
         and agent['payload']['implementation_ref'] == by_kind['implementation']['version_ref']
         and agent['payload']['capability_refs'] == [by_kind['agent-capability']['version_ref']]
         and agent['payload']['accountable_principal_ref'] == by_kind['principal']['body']['node_id']
         and result['assignment']['version_ref'] == by_kind['agent-assignment']['version_ref']
         and result['context_delivery_binding'] == live['context_delivery_binding']
         and live['context_view_header']['version_ref'] == session['payload']['context_view_ref']
         and session['payload']['session_memory']['expires_with_session'] is True,
         'live Agent, Session, Assignment or Context join differs')
    need(live_guard() is True, 'live Session changed during grant projection')
    return {
        'schema_version': GRANT_VERSION, 'grant_id': grant_id,
        'issuer_ref': 'fixture:local-technical-agent-challenge-issuer',
        'issuer_public_sha256': sha(issuer_public_raw),
        'operation': 'challenge.submit', 'host_uid': host_uid,
        'principal_ref': by_kind['principal']['body']['node_id'], 'scope_ref': SCOPE,
        'source_manifest_binding': {'path': FAMILY + '/source/source-manifest.json', 'sha256': SOURCE_SHA},
        'source_package_binding': {'path': FAMILY + '/source/packages/0001/manifest.json', 'sha256': PACKAGE_SHA},
        'source_cut': selected_cut,
        'work_binding': by_kind['work']['binding'], 'work_ref': by_kind['work']['version_ref'],
        'contract_binding': by_kind['challenge-contract']['binding'],
        'contract_ref': by_kind['challenge-contract']['version_ref'],
        'assignment_binding': by_kind['agent-assignment']['binding'],
        'assignment_ref': by_kind['agent-assignment']['version_ref'],
        'agent_instance_ref': agent['node_id'], 'session_ref': session['node_id'],
        'context_view_ref': live['context_view_header']['version_ref'],
        'context_delivery_binding': live['context_delivery_binding'],
        'allowed_grounds': by_kind['challenge-contract']['body']['payload']['grounds'],
        'allowed_response_modes': by_kind['challenge-contract']['body']['payload']['response_modes'],
        'required_evidence_kinds': ['source', 'validation-receipt'],
        'not_before': moment.isoformat().replace('+00:00', 'Z'),
        'expires_at': end.isoformat().replace('+00:00', 'Z'),
        'max_actions': 1, 'revoked': False,
        'authority_effect': 'none', 'owner_decision': None, 'contest_outcome': None,
    }


def sign(payload, private_key):
    need(isinstance(private_key, Ed25519PrivateKey), 'technical Ed25519 issuer required')
    public = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    need(payload['issuer_public_sha256'] == sha(public), 'issuer key selection differs')
    return {'payload': payload,
            'signature': base64.b64encode(private_key.sign(compact(payload))).decode('ascii')}


def verify(envelope, public_raw, expected_payload, at):
    need(type(envelope) is dict and set(envelope) == {'payload', 'signature'}
         and type(public_raw) is bytes and len(public_raw) == 32
         and type(expected_payload) is dict and set(expected_payload) == PAYLOAD_FIELDS
         and envelope['payload'] == expected_payload
         and expected_payload['schema_version'] == GRANT_VERSION
         and expected_payload['operation'] == 'challenge.submit'
         and expected_payload['issuer_public_sha256'] == sha(public_raw)
         and expected_payload['host_uid'] == os.getuid()
         and expected_payload['max_actions'] == 1
         and expected_payload['revoked'] is False
         and expected_payload['authority_effect'] == 'none'
         and expected_payload['owner_decision'] is None
         and expected_payload['contest_outcome'] is None,
         'selected technical grant differs')
    by_kind, period = source_records()
    need(expected_payload['source_cut'] == native_cut()
         and expected_payload['scope_ref'] == SCOPE
         and expected_payload['principal_ref'] == by_kind['principal']['body']['node_id']
         and expected_payload['source_manifest_binding'] == {'path': FAMILY + '/source/source-manifest.json', 'sha256': SOURCE_SHA}
         and expected_payload['source_package_binding'] == {'path': FAMILY + '/source/packages/0001/manifest.json', 'sha256': PACKAGE_SHA}
         and expected_payload['work_binding'] == by_kind['work']['binding']
         and expected_payload['work_ref'] == by_kind['work']['version_ref']
         and expected_payload['contract_binding'] == by_kind['challenge-contract']['binding']
         and expected_payload['contract_ref'] == by_kind['challenge-contract']['version_ref']
         and expected_payload['assignment_binding'] == by_kind['agent-assignment']['binding']
         and expected_payload['assignment_ref'] == by_kind['agent-assignment']['version_ref']
         and expected_payload['required_evidence_kinds'] == ['source', 'validation-receipt']
         and expected_payload['allowed_grounds'] == by_kind['challenge-contract']['body']['payload']['grounds']
         and expected_payload['allowed_response_modes'] == by_kind['challenge-contract']['body']['payload']['response_modes']
         and utc(expected_payload['not_before']) >= utc(period['not_before'])
         and utc(expected_payload['expires_at']) <= utc(period['expires_at']),
         'technical grant source, Work or Contract binding differs')
    need(type(at) is datetime and at.tzinfo is not None
         and utc(expected_payload['not_before']) <= at.astimezone(timezone.utc)
         < utc(expected_payload['expires_at']), 'technical grant expired')
    try:
        signature = base64.b64decode(envelope['signature'], validate=True)
        Ed25519PublicKey.from_public_bytes(public_raw).verify(signature, compact(expected_payload))
    except Exception as error:
        raise Refused('technical grant signature differs') from error
    return True
