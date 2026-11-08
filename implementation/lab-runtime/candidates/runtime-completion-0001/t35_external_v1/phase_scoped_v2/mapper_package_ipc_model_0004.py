"""Inert IPC grammar/transition model; never a server or effect capability.

No sockets, file writes, native execution, durable ACK or credential proof.
`complete_synthetic` only advances this model and cannot authorize any effect.
Kernel transport, native basis checks and semantic validators remain separate.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re

FRAME_MAX = 65536
CHUNK_MAX = 32768
BLOB_MAX = 4 * 1024 * 1024
EVENT_MAX = 256 * 1024
PACKAGE_MAX = 32 * 1024 * 1024
TOTAL_MAX = 64 * 1024 * 1024
PACKETS_MAX = 8192
VERSION = 'lab-mapper-package-ipc/v1'
VERBS = frozenset(('BEGIN', 'BLOB_BEGIN', 'BLOB_CHUNK', 'BLOB_END',
                   'SEAL', 'EMIT', 'COLD_READ', 'FINISH'))


class Refusal(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def hexhash(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def integer(value, minimum=0, maximum=2**63-1):
    return type(value) is int and minimum <= value <= maximum


def closed(value, names):
    need(type(value) is dict and set(value) == set(names), 'CLOSED_FIELDS')


def _domain(value, depth=0):
    need(depth <= 64, 'DEPTH')
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        need(integer(value), 'INTEGER')
    elif type(value) is str:
        need(not any(0xD800 <= ord(c) <= 0xDFFF for c in value), 'UNICODE')
    elif type(value) is list:
        for child in value:
            _domain(child, depth+1)
    elif type(value) is dict:
        for key, child in value.items():
            need(type(key) is str, 'KEY_TYPE')
            _domain(key, depth+1)
            _domain(child, depth+1)
    else:
        raise Refusal('CONTROL_TYPE')


def encode(value):
    _domain(value)
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False,
                     separators=(',', ':'), allow_nan=False).encode('utf-8')
    need(0 < len(raw) <= FRAME_MAX, 'FRAME_BOUND')
    return raw


def decode(raw):
    need(type(raw) is bytes and 0 < len(raw) <= FRAME_MAX, 'FRAME_BOUND')
    # Bound container nesting before allocating the parsed tree.
    depth, quoted, escaped = 0, False, False
    for c in raw:
        if quoted:
            if escaped:
                escaped = False
            elif c == 92:
                escaped = True
            elif c == 34:
                quoted = False
        elif c == 34:
            quoted = True
        elif c in (91, 123):
            depth += 1
            need(depth <= 64, 'DEPTH')
        elif c in (93, 125):
            depth -= 1
            need(depth >= 0, 'JSON')
    def pairs(rows):
        result = {}
        for key, value in rows:
            need(key not in result, 'DUPLICATE_KEY')
            result[key] = value
        return result
    def invalid(_):
        raise Refusal('CONTROL_TYPE')
    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_float=invalid,
                           parse_constant=invalid)
    except (ValueError, UnicodeError, RecursionError):
        raise Refusal('CONTROL_JSON') from None
    _domain(value)
    need(encode(value) == raw, 'NONCANONICAL')
    return value


def envelope(attempt_id, selection_sha256, ordinal, verb, payload):
    return {'schema_version': VERSION, 'attempt_id': attempt_id,
            'selection_sha256': selection_sha256, 'ordinal': ordinal,
            'verb': verb, 'payload': payload}


def schedule():
    return ([('BEGIN', ''), ('SEAL', 'semantic'), ('SEAL', 'governance')]
            + [('EMIT', family + '/' + str(i).zfill(8) + '.json')
               for family in ('semantic', 'governance') for i in range(1, 26)]
            + [('EMIT', 'request.json'), ('COLD_READ', 2), ('COLD_READ', 3)]
            + [('EMIT', leaf) for leaf in ('native-output.json', 'mapping.json',
                                          'build-result.json', 'manifest.json')]
            + [('FINISH', '')])


class ProtocolModel:
    """Synthetic sequencing only. No result from this class is a durable ACK."""
    def __init__(self, *, attempt_id, selection_sha256, begin_pins, peer):
        need(type(attempt_id) is str and re.fullmatch('[a-z0-9-]{1,64}', attempt_id), 'ATTEMPT')
        need(hexhash(selection_sha256), 'SELECTION')
        closed(begin_pins, ('mapper', 'source', 'reader', 'adapter'))
        need(all(hexhash(x) for x in begin_pins.values()), 'BEGIN_PINS')
        need(type(peer) is tuple and len(peer) == 4
             and integer(peer[0], 1, 2**31-1) and integer(peer[1], 1)
             and all(integer(x, 0, 2**32-2) for x in peer[2:]), 'PEER_MODEL')
        self.attempt_id = attempt_id
        self.selection_sha256 = selection_sha256
        self.begin_pins = dict(begin_pins)
        self.peer = peer  # Synthetic PID/start/UID/GID; no kernel claim.
        self.ordinal = self.step = self.total = self.package_bytes = 0
        self.pending = self.upload = self.ready = None
        self.failed = False
        self.first_failure = None
        self.manifest_sha256 = None
        self.trace = []

    def _poison(self, code):
        self.failed = True
        if self.first_failure is None:
            self.first_failure = code

    def disconnect(self):
        self._poison('DISCONNECTED')

    def receive(self, raw, *, peer, truncated=False, ancillary_truncated=False,
                credential_count=1, rights_present=False, unknown_ancillary=False):
        """Validate synthetic transport observations; never owns real FDs."""
        need(not self.failed, 'POISONED')
        try:
            need(peer == self.peer and type(peer) is tuple and all(type(x) is int for x in peer)
                 and type(credential_count) is int and credential_count == 1
                 and truncated is False and ancillary_truncated is False
                 and rights_present is False and unknown_ancillary is False, 'TRANSPORT_MODEL')
            need(self.pending is None and self.step < len(schedule()), 'PENDING_OR_FINISHED')
            value = decode(raw)
            closed(value, ('schema_version', 'attempt_id', 'selection_sha256', 'ordinal', 'verb', 'payload'))
            need(value['schema_version'] == VERSION and value['attempt_id'] == self.attempt_id
                 and value['selection_sha256'] == self.selection_sha256, 'SUBJECT')
            need(integer(value['ordinal']) and value['ordinal'] == self.ordinal
                 and self.ordinal < PACKETS_MAX, 'ORDINAL')
            need(type(value['verb']) is str and value['verb'] in VERBS, 'VERB')
            need(self.total + len(raw) <= TOTAL_MAX, 'AGGREGATE')
            self.total += len(raw)
            action = self._request(value['verb'], value['payload'])
            self.ordinal += 1
            request_sha = sha(raw)
            if action is None:
                return {'schema_version': 'lab-mapper-model-transition/v1',
                        'request_sha256': request_sha, 'ordinal': value['ordinal'],
                        'effect_performed': False, 'durable_ack': False}
            action.update(request_sha256=request_sha, ordinal=value['ordinal'],
                          action_id=request_sha, effect_performed=False, durable_ack=False)
            self.pending = action
            return dict(action)
        except Refusal as e:
            self._poison(e.args[0])
            raise

    def _request(self, verb, p):
        expected_verb, target = schedule()[self.step]
        if verb == 'BLOB_BEGIN':
            closed(p, ('size_bytes', 'sha256', 'purpose', 'target'))
            need(expected_verb in ('SEAL', 'EMIT') and self.upload is None and self.ready is None
                 and p['purpose'] == expected_verb and p['target'] == target, 'BLOB_SCOPE')
            cap = EVENT_MAX if expected_verb == 'EMIT' and '/' in target else BLOB_MAX
            need(integer(p['size_bytes'], 1, cap) and hexhash(p['sha256']), 'BLOB_BOUND')
            need(self.total + p['size_bytes'] <= TOTAL_MAX, 'AGGREGATE')
            self.upload = {'id': self.ordinal, 'size': p['size_bytes'], 'sha256': p['sha256'],
                           'purpose': p['purpose'], 'target': target, 'data': bytearray()}
            return None
        if verb == 'BLOB_CHUNK':
            closed(p, ('blob_id', 'offset', 'data'))
            u = self.upload
            need(u is not None and integer(p['blob_id']) and p['blob_id'] == u['id']
                 and integer(p['offset']) and p['offset'] == len(u['data'])
                 and type(p['data']) is str and len(p['data']) <= 4*((CHUNK_MAX+2)//3), 'CHUNK_SCOPE')
            try:
                data = base64.b64decode(p['data'], validate=True)
            except (ValueError, UnicodeError):
                raise Refusal('CHUNK_ENCODING') from None
            need(base64.b64encode(data).decode('ascii') == p['data'], 'CHUNK_ENCODING')
            need(0 < len(data) <= CHUNK_MAX and len(u['data']) + len(data) <= u['size'], 'CHUNK_BOUND')
            u['data'].extend(data)
            return None
        if verb == 'BLOB_END':
            closed(p, ('blob_id',))
            u = self.upload
            need(u is not None and integer(p['blob_id']) and p['blob_id'] == u['id']
                 and len(u['data']) == u['size'] and sha(u['data']) == u['sha256'], 'BLOB_INTEGRITY')
            self.ready, self.upload = u, None
            return None
        need(verb == expected_verb and self.upload is None, 'PHASE')
        if verb in ('SEAL', 'EMIT'):
            closed(p, ('blob_id',) if verb == 'SEAL' else ('blob_id', 'leaf'))
            u = self.ready
            need(u is not None and integer(p['blob_id']) and p['blob_id'] == u['id']
                 and u['purpose'] == verb and u['target'] == target, 'BLOB_CONSUMPTION')
            if verb == 'EMIT':
                need(p['leaf'] == target and self.package_bytes + u['size'] <= PACKAGE_MAX, 'LEAF_OR_QUOTA')
            action = {'schema_version': 'lab-mapper-model-action/v1', 'verb': verb,
                      'target': target, 'blob_sha256': u['sha256'], 'size_bytes': u['size']}
            # The model deliberately does not represent these bytes as validated native events.
            self.ready = None
            return action
        need(self.ready is None, 'UNCONSUMED_BLOB')
        if verb == 'BEGIN':
            closed(p, ('mapper', 'source', 'reader', 'adapter'))
            need(p == self.begin_pins, 'BEGIN_BINDING')
        elif verb == 'COLD_READ':
            closed(p, ('index',))
            need(integer(p['index']) and p['index'] == target, 'COLD_INDEX')
        elif verb == 'FINISH':
            closed(p, ('manifest_sha256',))
            need(hexhash(p['manifest_sha256']) and p['manifest_sha256'] == self.manifest_sha256, 'MANIFEST')
        return {'schema_version': 'lab-mapper-model-action/v1', 'verb': verb, 'target': target}

    def complete_synthetic(self, action_id, *, success):
        """Fixture continuation only: no native or filesystem evidence accepted."""
        need(not self.failed, 'POISONED')
        try:
            need(self.pending is not None and hexhash(action_id)
                 and action_id == self.pending['action_id'] and success is True, 'MODEL_COMPLETION')
            action = self.pending
            if action['verb'] == 'EMIT':
                self.package_bytes += action['size_bytes']
                if action['target'] == 'manifest.json':
                    self.manifest_sha256 = action['blob_sha256']
            self.trace.append(dict(action))
            self.step += 1
            self.pending = None
        except Refusal as e:
            self._poison(e.args[0])
            raise
