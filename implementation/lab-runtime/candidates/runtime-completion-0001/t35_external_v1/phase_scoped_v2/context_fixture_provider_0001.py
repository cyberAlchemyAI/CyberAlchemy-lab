"""Pure fixture body selection, not original Context generation or permission.

Only deterministic bytes and references are implemented. The full runtime facade,
query, authenticated channel and transport bridge remain deliberately unavailable.
"""
import hashlib
import json
import re
from dataclasses import dataclass

__all__ = ('make_bodies', 'select_bodies', 'FixtureBodies', 'fixture_query', 'generate')

SCHEMA = 'lab-context-orchestration-body/v1-inert'
CARRIER = 'fixture:context-orchestration-body/v1'
BODY_KEYS = frozenset(('schema_version', 'fixture_id', 'ordinal', 'fixture_kind',
                       'mapper_manifest_sha256', 'mapping_sha256',
                       'authority_effect', 'actual_owner_outcome'))
MAX_BODY = 4096
MAX_TOTAL = 30 * MAX_BODY
KINDS = ('node-label',) * 15 + ('edge-label',) * 10 + (
    'ontology-label', 'cut-label', 'view-label', 'request-label', 'context-label')


class Refusal(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise Refusal(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _hash(value):
    need(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None,
         'FIXTURE_HASH')


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + '\n').encode('utf-8')


def _body(index, mapper_manifest_sha256, mapping_sha256):
    return {'schema_version': SCHEMA,
            'fixture_id': f'fixture:context:{index:02d}', 'ordinal': index,
            'fixture_kind': KINDS[index],
            'mapper_manifest_sha256': mapper_manifest_sha256,
            'mapping_sha256': mapping_sha256, 'authority_effect': 'none',
            'actual_owner_outcome': None}


def make_bodies(*, mapper_manifest_sha256, mapping_sha256):
    """Prepare bytes for subsequent independent selection; not a read receipt."""
    _hash(mapper_manifest_sha256)
    _hash(mapping_sha256)
    return tuple(encoded(_body(i, mapper_manifest_sha256, mapping_sha256))
                 for i in range(30))


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'FIXTURE_DUPLICATE_KEY')
        result[key] = value
    return result


def _decode(raw):
    need(type(raw) is bytes and 0 < len(raw) <= MAX_BODY, 'FIXTURE_BODY_BOUND')
    try:
        body = json.loads(raw, object_pairs_hook=_pairs)
    except (ValueError, UnicodeError, RecursionError):
        raise Refusal('FIXTURE_BODY_JSON') from None
    need(type(body) is dict and set(body) == BODY_KEYS, 'FIXTURE_BODY_FIELDS')
    need(type(body['ordinal']) is int and 0 <= body['ordinal'] < 30,
         'FIXTURE_ORDINAL')
    need(encoded(body) == raw, 'FIXTURE_CANONICAL_BYTES')
    return body


def select_bodies(raws, *, expected_rows, mapper_manifest_sha256, mapping_sha256):
    """Verify independently selected ordered byte bindings and complete values."""
    _hash(mapper_manifest_sha256)
    _hash(mapping_sha256)
    need(type(raws) is tuple and len(raws) == 30 and
         type(expected_rows) is list and len(expected_rows) == 30,
         'FIXTURE_BODY_COUNT')
    total = 0
    for i, (raw, row) in enumerate(zip(raws, expected_rows)):
        need(type(row) is dict and set(row) == {'fixture_id', 'sha256', 'size_bytes'},
             'FIXTURE_SELECTION_FIELDS')
        _hash(row['sha256'])
        need(type(row['size_bytes']) is int and 0 < row['size_bytes'] <= MAX_BODY,
             'FIXTURE_SELECTION_SIZE')
        body = _decode(raw)
        need(body == _body(i, mapper_manifest_sha256, mapping_sha256),
             'FIXTURE_BODY_MEANING')
        need(row == {'fixture_id': body['fixture_id'], 'sha256': digest(raw),
                     'size_bytes': len(raw)}, 'FIXTURE_SELECTED_BYTES')
        total += len(raw)
    need(total <= MAX_TOTAL, 'FIXTURE_TOTAL_BOUND')
    return FixtureBodies(raws, mapper_manifest_sha256, mapping_sha256)


@dataclass(frozen=True)
class FixtureBodies:
    """Immutable pure values; directly constructing this class grants nothing."""
    raw_bodies: tuple
    mapper_manifest_sha256: str
    mapping_sha256: str

    def values(self):
        _hash(self.mapper_manifest_sha256)
        _hash(self.mapping_sha256)
        need(type(self.raw_bodies) is tuple and len(self.raw_bodies) == 30,
             'FIXTURE_BODY_COUNT')
        bodies, refs = {}, {}
        for i, raw in enumerate(self.raw_bodies):
            body = _decode(raw)
            need(body == _body(i, self.mapper_manifest_sha256, self.mapping_sha256),
                 'FIXTURE_BODY_MEANING')
            identity = body['fixture_id']
            bodies[identity] = body
            refs[identity] = {'identity_ref': identity, 'version_ref': identity+'@1',
                              'carrier_ref': CARRIER, 'byte_sha256': digest(raw)}
        return bodies, refs


def fixture_query(*args, **kwargs):
    raise Refusal('FIXTURE_RUNTIME_FACADE_NOT_IMPLEMENTED')


def generate(*args, **kwargs):
    raise Refusal('FIXTURE_RUNTIME_FACADE_NOT_IMPLEMENTED')
