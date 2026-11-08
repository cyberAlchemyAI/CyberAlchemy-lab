"""Inert Context IPC sequence/semantic model, never a socket or writer.

Receipts, peer IDs, path custody and absence here are synthetic values. This
model cannot prove kernel credentials, held FDs, mount visibility or fsync.
"""
from __future__ import annotations

import base64
import binascii
import datetime as dt
import hashlib
import json
import re
from pathlib import PurePosixPath

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

from . import mapper_package_ipc_model_0004 as codec

VERSION = 'lab-context-package-ipc/v1-inert'
PACKAGE_MAX = 8 * 1024 * 1024
LEAF_MAX = 4 * 1024 * 1024
REQUEST_MAX = 1024 * 1024
ARTIFACT_TOTAL_MAX = 2 * 1024 * 1024
POLICY_MAX = 16 * 1024
PACKETS_MAX = 4096
HEX = re.compile(r'[0-9a-f]{64}\Z')
NONCE = re.compile(r'[0-9a-f]{64}\Z')


class Refusal(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def hexhash(value):
    return type(value) is str and HEX.fullmatch(value) is not None


def closed(value, keys):
    need(type(value) is dict and set(value) == set(keys), 'CLOSED_FIELDS')


def integer(value, low=0, high=2**63 - 1):
    return type(value) is int and low <= value <= high


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True,
                       ensure_ascii=False, allow_nan=False) + '\n').encode()


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def instant(value):
    need(type(value) is str and value.endswith('Z'), 'PERIOD_FORMAT')
    try:
        parsed = dt.datetime.fromisoformat(value)
    except ValueError:
        raise Refusal('PERIOD_FORMAT') from None
    need(parsed.tzinfo is not None and parsed.utcoffset() == dt.timedelta(0),
         'PERIOD_FORMAT')
    return parsed


def schedule():
    first = ['request.json', 'authentication-proof.json',
             'trusted-context.json', 'host-permission-public.json']
    artifacts = ['artifacts/' + str(i).zfill(2) + '.json' for i in range(30)]
    tail = ['artifact-index.json', 'delivery.json', 'lesson-selection.json',
            'delivery-provenance.json']
    return ([('PREPARE', None), ('PRIVATE_ROOT', None), ('PROVISION', None)]
            + [('EMIT', leaf) for leaf in first]
            + [('NATIVE_READ', None)]
            + [('EMIT', leaf) for leaf in artifacts + tail]
            + [('RELEASE_PRIVATE', None)]
            + [('EMIT', 'build-result.json'), ('EMIT', 'manifest.json')]
            + [('FINISH', None)])


class ProtocolModel:
    """Closed synthetic message schedule with sticky retained failure."""

    def __init__(self, *, attempt_id, selection_sha256, predecessor,
                 package_path, private_root_path, uid, source_period,
                 source_scope_ref, principal_ref, mapped_output_sha256,
                 peer, now):
        need(type(attempt_id) is str and re.fullmatch(r'[a-z0-9-]{1,64}', attempt_id),
             'ATTEMPT')
        need(hexhash(selection_sha256) and hexhash(mapped_output_sha256),
             'SELECTION')
        closed(predecessor, ('source', 'source_package', 'mapped', 'mapped_package'))
        need(all(hexhash(value) for value in predecessor.values()), 'PREDECESSOR')
        need(type(package_path) is str and package_path.startswith('/') and
             package_path.endswith('/context/packages/0001') and
             PurePosixPath(package_path).as_posix() == package_path and
             all(part not in ('.', '..') for part in package_path.split('/')[1:])
             and type(private_root_path) is str and
             re.fullmatch(r'/tmp/[a-z0-9-]{1,80}', private_root_path)
             and integer(uid, 1, 2**32 - 2), 'PATH_SELECTION')
        closed(source_period, ('not_before', 'expires_at', 'binding'))
        closed(source_period['binding'], ('path', 'sha256'))
        need(hexhash(source_period['binding']['sha256']) and
             type(source_period['binding']['path']) is str, 'PERIOD_BINDING')
        need(type(now) is dt.datetime and now.tzinfo is not None and
             now.utcoffset() == dt.timedelta(0), 'CLOCK_MODEL')
        need(instant(source_period['not_before']) <= now <
             instant(source_period['expires_at']), 'SOURCE_PERIOD_STALE')
        need(type(source_scope_ref) is str and bool(source_scope_ref) and
             type(principal_ref) is str and bool(principal_ref), 'SOURCE_SCOPE')
        need(type(peer) is tuple and len(peer) == 4 and
             integer(peer[0], 1, 2**31 - 1) and integer(peer[1], 1) and
             integer(peer[2], 0, 2**32 - 2) and
             integer(peer[3], 0, 2**32 - 2), 'PEER_MODEL')
        self.attempt_id = attempt_id
        self.selection_sha256 = selection_sha256
        self.predecessor = dict(predecessor)
        self.package_path = package_path
        self.private_root_path = private_root_path
        self.uid = uid
        self.source_period = dict(source_period)
        self.source_scope_ref = source_scope_ref
        self.principal_ref = principal_ref
        self.mapped_output_sha256 = mapped_output_sha256
        self.peer = peer
        self.now = now
        self.step = self.ordinal = self.package_bytes = self.artifact_bytes = 0
        self.bindings = {}
        self.policy = self.policy_sha256 = None
        self.package_identity = self.private_identity = None
        self.failed = self.finished = self.retain_attempt = False
        self.first_failure = None
        self.trace = []

    def _fail(self, code):
        self.failed = True
        self.retain_attempt = True
        if self.first_failure is None:
            self.first_failure = code
        raise Refusal(code)

    def disconnect(self):
        if not self.finished:
            self.failed = self.retain_attempt = True
            if self.first_failure is None:
                self.first_failure = 'DISCONNECTED'

    def receive(self, raw, *, peer, truncated=False, ancillary_truncated=False,
                credential_count=1, rights_present=False):
        need(not self.failed, 'POISONED')
        need(not self.finished, 'FINISHED')
        try:
            need(peer == self.peer and type(peer) is tuple and
                 len(peer) == 4 and all(type(value) is int for value in peer) and
                 truncated is False and ancillary_truncated is False and
                 type(credential_count) is int and credential_count == 1 and
                 rights_present is False,
                 'TRANSPORT_MODEL')
            try:
                event = codec.decode(raw)
            except codec.Refusal:
                raise Refusal('FRAME_REFUSED') from None
            closed(event, ('schema_version', 'attempt_id', 'selection_sha256',
                           'ordinal', 'verb', 'payload'))
            need(event['schema_version'] == VERSION and
                 event['attempt_id'] == self.attempt_id and
                 event['selection_sha256'] == self.selection_sha256,
                 'ENVELOPE')
            need(integer(event['ordinal']) and event['ordinal'] == self.ordinal and
                 self.ordinal < PACKETS_MAX, 'ORDINAL')
            expected_verb, expected_leaf = schedule()[self.step]
            need(event['verb'] == expected_verb, 'ORDER')
            payload = event['payload']
            if expected_verb in ('PREPARE', 'PRIVATE_ROOT'):
                self._receipt(payload, private=expected_verb == 'PRIVATE_ROOT')
            elif expected_verb == 'PROVISION':
                self._provision(payload)
            elif expected_verb == 'EMIT':
                self._emit(payload, expected_leaf)
            elif expected_verb == 'NATIVE_READ':
                self._native(payload)
            elif expected_verb == 'RELEASE_PRIVATE':
                self._release(payload)
            else:
                self._finish(payload)
            receipt = {'schema_version': VERSION, 'ordinal': self.ordinal,
                       'request_sha256': sha(raw), 'step': self.step,
                       'status': 'synthetic-accepted'}
            self.trace.append((event['verb'], expected_leaf, sha(raw)))
            self.ordinal += 1
            self.step += 1
            if expected_verb == 'FINISH':
                self.finished = True
            return receipt
        except Refusal as error:
            self._fail(str(error))

    def _receipt(self, payload, *, private):
        closed(payload, ('path', 'absent_before', 'empty_after',
                         'readonly_visible', 'nonsymlink', 'uid', 'mode',
                         'identity_sha256'))
        need(payload['path'] == (self.private_root_path if private else
                                self.package_path) and
             payload['absent_before'] is True and
             payload['empty_after'] is True and
             payload['readonly_visible'] is True and
             payload['nonsymlink'] is True and
             payload['uid'] == self.uid and
             payload['mode'] == 0o700 and
             hexhash(payload['identity_sha256']),
             'PRIVATE_ROOT_RECEIPT' if private else 'PACKAGE_PREEXISTS')
        if private:
            self.private_identity = payload['identity_sha256']
        else:
            self.package_identity = payload['identity_sha256']

    def _provision(self, payload):
        closed(payload, ('path', 'policy', 'policy_sha256'))
        need(payload['path'] == self.private_root_path + '/permission.json' and
             self.private_identity is not None, 'POLICY_PATH')
        policy = payload['policy']
        closed(policy, ('schema_version', 'host_uid', 'principal_ref', 'scope_ref',
                        'reader_public_key', 'not_before', 'expires_at',
                        'max_input_bytes', 'max_output_bytes', 'max_session_seconds',
                        'period_binding', 'allowed_operations', 'authority_effect',
                        'actual_owner_outcome'))
        raw = encoded(policy)
        need(len(raw) <= POLICY_MAX and sha(raw) == payload['policy_sha256'] and
             policy['schema_version'] == 'lab-context-host-policy/v1-candidate' and
             policy['host_uid'] == self.uid and
             policy['principal_ref'] == self.principal_ref and
             policy['scope_ref'] == self.source_scope_ref and
             policy['period_binding'] == self.source_period['binding'] and
             policy['allowed_operations'] == ['context.get', 'session.open'] and
             policy['authority_effect'] == 'none' and
             policy['actual_owner_outcome'] is None and
             policy['max_input_bytes'] == REQUEST_MAX and
             policy['max_output_bytes'] == ARTIFACT_TOTAL_MAX and
             policy['max_session_seconds'] == 900,
             'POLICY_FIELDS')
        need(instant(self.source_period['not_before']) <=
             instant(policy['not_before']) <= self.now <
             instant(policy['expires_at']) <=
             instant(self.source_period['expires_at']) and
             instant(policy['expires_at']) <= self.now + dt.timedelta(minutes=20),
             'POLICY_STALE')
        try:
            public = base64.b64decode(policy['reader_public_key'], validate=True)
            Ed25519PublicKey.from_public_bytes(public)
        except (ValueError, TypeError):
            raise Refusal('PUBLIC_KEY') from None
        need(len(public) == 32, 'PUBLIC_KEY')
        self.policy = policy
        self.policy_sha256 = payload['policy_sha256']

    def _proof(self, proof, leaf_sha, leaf_size):
        closed(proof, ('challenge', 'signature'))
        challenge = proof['challenge']
        closed(challenge, ('schema_version', 'host_instance_ref', 'connection_ref',
                           'nonce', 'policy_sha256', 'expires_at',
                           'authority_effect'))
        need(challenge['schema_version'] == 'lab-context-host-challenge/v1-candidate'
             and type(challenge['host_instance_ref']) is str and
             bool(challenge['host_instance_ref']) and
             type(challenge['connection_ref']) is str and
             bool(challenge['connection_ref']) and
             type(challenge['nonce']) is str and NONCE.fullmatch(challenge['nonce'])
             and challenge['policy_sha256'] == self.policy_sha256 and
             challenge['expires_at'] == self.policy['expires_at'] and
             challenge['authority_effect'] == 'none', 'CHALLENGE')
        raw = compact(proof)
        need(sha(raw) == leaf_sha and len(raw) == leaf_size, 'PROOF_BINDING')
        try:
            signature = base64.b64decode(proof['signature'], validate=True)
            Ed25519PublicKey.from_public_bytes(base64.b64decode(
                self.policy['reader_public_key'], validate=True)).verify(
                    signature, compact(challenge))
        except (ValueError, TypeError, binascii.Error, InvalidSignature):
            # Never put the crypto exception or proof bytes in a public refusal.
            raise Refusal('NONCE_PROOF') from None

    def _emit(self, payload, leaf):
        if leaf == 'authentication-proof.json':
            closed(payload, ('leaf', 'sha256', 'size_bytes', 'proof'))
        else:
            closed(payload, ('leaf', 'sha256', 'size_bytes'))
        need(payload['leaf'] == leaf and hexhash(payload['sha256']) and
             integer(payload['size_bytes'], 1, LEAF_MAX) and
             leaf not in self.bindings and
             self.package_bytes + payload['size_bytes'] <= PACKAGE_MAX,
             'LEAF_BINDING')
        if leaf == 'request.json':
            need(payload['size_bytes'] <= REQUEST_MAX, 'REQUEST_BOUND')
        elif leaf == 'authentication-proof.json':
            self._proof(payload['proof'], payload['sha256'], payload['size_bytes'])
        elif leaf == 'host-permission-public.json':
            need(self.policy is not None and
                 payload['sha256'] == self.policy_sha256 and
                 payload['size_bytes'] == len(encoded(self.policy)),
                 'PUBLIC_POLICY_BINDING')
        elif leaf.startswith('artifacts/'):
            self.artifact_bytes += payload['size_bytes']
            need(self.artifact_bytes <= ARTIFACT_TOTAL_MAX, 'ARTIFACT_BOUND')
        self.bindings[leaf] = (payload['sha256'], payload['size_bytes'])
        self.package_bytes += payload['size_bytes']

    def _native(self, payload):
        closed(payload, ('mapped_package_sha256', 'output_sha256', 'size_bytes'))
        need(payload['mapped_package_sha256'] == self.predecessor['mapped_package']
             and payload['output_sha256'] == self.mapped_output_sha256 and
             integer(payload['size_bytes'], 1, LEAF_MAX), 'NATIVE_PARITY')

    def _release(self, payload):
        closed(payload, ('path', 'identity_sha256', 'policy_absent',
                         'root_absent', 'owner_uid'))
        need(payload['path'] == self.private_root_path and
             payload['identity_sha256'] == self.private_identity and
             payload['policy_absent'] is True and
             payload['root_absent'] is True and
             payload['owner_uid'] == self.uid, 'PRIVATE_RETAINED')
        self.private_identity = None

    def _finish(self, payload):
        closed(payload, ('manifest_rows', 'package_closed'))
        need(payload['package_closed'] is True and
             self.private_identity is None and len(self.bindings) == 40 and
             'manifest.json' in self.bindings, 'PACKAGE_CLOSURE')
        rows = payload['manifest_rows']
        need(type(rows) is list and len(rows) == 39 and
             all(type(row) is dict and set(row) == {'path', 'sha256'}
                 for row in rows), 'MANIFEST_ROWS')
        expected = [(self.package_path + '/' + name, self.bindings[name][0])
                    for name in sorted(self.bindings) if name != 'manifest.json']
        need([(row['path'], row['sha256']) for row in rows] == expected,
             'MANIFEST_BINDINGS')


def message(model, verb, payload, *, ordinal=None):
    """Canonical synthetic request bytes for tests; no transport sends them."""
    return codec.encode({'schema_version': VERSION, 'attempt_id': model.attempt_id,
                         'selection_sha256': model.selection_sha256,
                         'ordinal': model.ordinal if ordinal is None else ordinal,
                         'verb': verb, 'payload': payload})
