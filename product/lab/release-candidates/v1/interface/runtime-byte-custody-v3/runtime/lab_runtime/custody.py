"""Retain reviewed JSON bytes, independently of the runtime structural encoding.

This is a candidate storage primitive. Transport permission, privacy, schema,
reference closure, complete export and canonical admission are separate gates.
"""
from __future__ import annotations

import base64
import binascii
import json
import math
import os
import sqlite3
from pathlib import Path

from .common import RuntimeFault, byte_digest, digest, encoded, load, pointer, require, under

CONTENT_SCHEMA = load(Path(__file__).resolve().parents[1] / 'schemas/artifact-content-entry.schema.json')
MAX_CONTENT_BYTES = 1024 * 1024
MAX_PROPOSAL_CONTENT_BYTES = 16 * MAX_CONTENT_BYTES
MAX_MATERIALS = 64
ENCODING = 'base64-original-json/v1-candidate'
PROPOSAL_VERSION = 'lab-runtime-original-json-proposal/v1-candidate'


def parse_original(raw):
    require(isinstance(raw, bytes) and len(raw) <= MAX_CONTENT_BYTES, 'original JSON content exceeds bound')
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate original JSON key')
            result[key] = value
        return result
    def walk(value, depth=0):
        require(depth <= 64, 'original JSON nesting exceeds bound')
        if isinstance(value, str):
            try:
                value.encode('utf-8')
            except UnicodeEncodeError as exc:
                raise RuntimeFault('original JSON has unpaired Unicode surrogate') from exc
        elif isinstance(value, float):
            require(math.isfinite(value), 'original JSON has nonfinite number')
        elif isinstance(value, dict):
            for key, child in value.items():
                walk(key, depth + 1); walk(child, depth + 1)
        elif isinstance(value, list):
            for child in value: walk(child, depth + 1)
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(RuntimeFault('nonfinite original JSON')))
        require(isinstance(value, dict), 'original JSON must be an object')
        walk(value)
        return value
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise RuntimeFault('invalid original UTF8 JSON') from exc


def content_entry(raw):
    """No reserialization: wrap precisely the bytes supplied by the caller."""
    parse_original(raw)
    sha = byte_digest(raw)
    return {'schema_version': 'lab-artifact-content-entry/v1-candidate',
        'content_ref': 'runtime-content:sha256:' + sha, 'media_type': 'application/json',
        'byte_sha256': sha, 'size_bytes': len(raw), 'encoding': 'base64',
        'data': base64.b64encode(raw).decode('ascii'), 'semantic_binding': None}


def decode_content(entry):
    from .operations import protocol_check
    protocol_check(entry, CONTENT_SCHEMA)
    require(entry['media_type'] == 'application/json' and entry['semantic_binding'] is None,
        'custody profile requires JSON and asserts no semantic hash')
    require(type(entry['size_bytes']) is int and entry['size_bytes'] <= MAX_CONTENT_BYTES,
        'original content size exceeds bound')
    require(len(entry['data']) <= ((MAX_CONTENT_BYTES + 2) // 3) * 4,
        'encoded original content exceeds bound')
    try:
        raw = base64.b64decode(entry['data'], validate=True)
    except (binascii.Error, ValueError) as exc:
        raise RuntimeFault('invalid original base64') from exc
    require(base64.b64encode(raw).decode('ascii') == entry['data'], 'noncanonical base64')
    require(len(raw) == entry['size_bytes'] and byte_digest(raw) == entry['byte_sha256'],
        'original content size or byte digest differs')
    require(entry['content_ref'] == 'runtime-content:sha256:' + entry['byte_sha256'],
        'original content reference differs')
    return raw


def equivalent(raw, record):
    # Structural algorithm is frozen common.digest. It is not a semantic hash.
    # Comparing digests also avoids Python's True == 1 and 1 == 1.0 collapse.
    require(digest(parse_original(raw)) == digest(record), 'original JSON value differs from parsed record')


def validate_proposal_content(proposal):
    if proposal['schema_version'] != PROPOSAL_VERSION:
        return
    require(len(proposal['targets']) <= MAX_MATERIALS and len(proposal['schemas']) <= MAX_MATERIALS,
        'original content material count exceeds bound')
    require(set(proposal['schema_contents']) == set(proposal['schemas']),
        'every proposed schema needs exactly one original content entry')
    total = 0
    for target in proposal['targets']:
        if target['operation'] == 'withdraw':
            require(target['content'] is None, 'withdrawal cannot replace original content')
        else:
            require(target['content'] is not None, 'admission/revision requires original content')
            raw = decode_content(target['content']); equivalent(raw, target['record']); total += len(raw)
    for path, schema in proposal['schemas'].items():
        raw = decode_content(proposal['schema_contents'][path]); equivalent(raw, schema); total += len(raw)
    require(total <= MAX_PROPOSAL_CONTENT_BYTES, 'total original content exceeds proposal bound')


def with_originals(proposal, target_bytes, schema_bytes):
    """Construct a new review proposal; prior cores/approvals must be regenerated.

    The caller must provide each original byte body. This never labels the
    inherited canonical encoder's output as a previously reviewed original.
    """
    import copy
    require(proposal['schema_version'] == 'lab-runtime-proposal/v1', 'explicit v1 proposal input required')
    result = copy.deepcopy(proposal)
    result['schema_version'] = PROPOSAL_VERSION
    require(set(target_bytes) == {t['version_ref'] for t in result['targets'] if t['operation'] != 'withdraw'},
        'original target byte map must be exact')
    require(set(schema_bytes) == set(result['schemas']), 'original schema byte map must be exact')
    result['schema_contents'] = {p: content_entry(raw) for p, raw in schema_bytes.items()}
    for target in result['targets']:
        target['content'] = None if target['operation'] == 'withdraw' else content_entry(target_bytes[target['version_ref']])
    validate_proposal_content(result)
    return result


def content_rows(data):
    """Verified committed transaction contents; derived from one replay cut."""
    rows = []
    for tx in data['transactions'][1:]:
        proposal = tx['proposal']; custody = proposal['schema_version'] == PROPOSAL_VERSION
        for target in proposal['targets']:
            if target['operation'] == 'withdraw': continue
            raw = decode_content(target['content']) if custody else encoded(target['record'])
            equivalent(raw, target['record'])
            rows.append({'content_key': 'target:' + target['version_ref'], 'version_ref': target['version_ref'],
                'role': 'authored-target', 'sequence': tx['sequence'], 'byte_sha256': byte_digest(raw),
                'structural_value_sha256': digest(target['record']), 'raw': raw,
                'encoding': ENCODING if custody else 'inherited-runtime-encoded-json/v1'})
        for path, schema in proposal['schemas'].items():
            raw = decode_content(proposal['schema_contents'][path]) if custody else encoded(schema)
            equivalent(raw, schema)
            rows.append({'content_key': 'schema:' + proposal['proposal_id'] + ':' + path,
                'version_ref': path, 'role': 'schema-input', 'sequence': tx['sequence'],
                'byte_sha256': byte_digest(raw), 'structural_value_sha256': digest(schema), 'raw': raw,
                'encoding': ENCODING if custody else 'inherited-runtime-encoded-json/v1'})
    return rows


def original_bytes(store, version_ref, expected_head):
    """Retrieve exact immutable revision bytes from verified canonical replay.

    Repository-file baseline bodies remain independently bound original files.
    The legacy selector convention keeps its declared inherited encoding.
    """
    data = store.replay()
    require(data['head']['transaction_digest'] == expected_head, 'content read HEAD differs')
    require(version_ref in data['projection']['subjects'], 'content read requires exact revision')
    subject = data['projection']['subjects'][version_ref]; binding = subject['source']
    if binding.get('store_id'):
        sequence = int(Path(binding['path']).stem)
        require(0 <= sequence < len(data['transactions']), 'content source transaction absent')
        tx = data['transactions'][sequence]
        if binding.get('encoding') == ENCODING:
            prefix = binding['selector'].removesuffix('/data')
            require(prefix + '/data' == binding['selector'], 'original content selector differs')
            entry = pointer(tx, prefix); raw = decode_content(entry)
            require(pointer(tx, binding['record_selector']) == subject['record'], 'parsed record selector differs')
        else:
            require('encoding' not in binding, 'unknown content encoding')
            raw = encoded(pointer(tx, binding['selector']))
    else:
        require('encoding' not in binding, 'unknown repository content encoding')
        path = under(store.repo, binding['path']); file_raw = path.read_bytes()
        require(byte_digest(file_raw) == data['baseline']['materials'][binding['path']], 'baseline original file drift')
        raw = encoded(pointer(parse_original(file_raw), binding['selector'])) if binding.get('selector') else file_raw
    require(byte_digest(raw) == binding['sha256'], 'retrieved original byte identity differs')
    equivalent(raw, subject['record'])
    return raw


def build_content_cache(store, path, expected_head):
    """Disposable SQLite BLOB projection. Never supplies replay input or authority.

    Requires a new caller-selected path. Full API path/grant/export governance
    remains a separate integration obligation.
    """
    data = store.replay()
    require(data['head']['transaction_digest'] == expected_head, 'cache source HEAD differs')
    rows = content_rows(data); path = Path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600); os.close(fd)
    db = None
    try:
        db = sqlite3.connect(path)
        db.executescript('CREATE TABLE cut(head TEXT NOT NULL); CREATE TABLE contents(content_key TEXT PRIMARY KEY, version_ref TEXT NOT NULL, role TEXT NOT NULL, sequence INTEGER NOT NULL, byte_sha256 TEXT NOT NULL, structural_value_sha256 TEXT NOT NULL, encoding TEXT NOT NULL, raw BLOB NOT NULL);')
        db.execute('INSERT INTO cut VALUES (?)', (expected_head,))
        for row in rows:
            db.execute('INSERT INTO contents VALUES (?,?,?,?,?,?,?,?)', tuple(row[k] for k in ('content_key','version_ref','role','sequence','byte_sha256','structural_value_sha256','encoding','raw')))
        db.commit()
        require(db.execute('PRAGMA integrity_check').fetchone() == ('ok',), 'content cache integrity failed')
        actual = db.execute('SELECT content_key,byte_sha256,raw FROM contents ORDER BY content_key').fetchall()
        wanted = sorted((r['content_key'],r['byte_sha256'],r['raw']) for r in rows)
        require(actual == wanted, 'content cache differs from canonical original bytes')
        db.close(); db = None
        with path.open('rb') as file: os.fsync(file.fileno())
        return {'source_head': expected_head, 'row_count': len(rows), 'file_sha256': byte_digest(path.read_bytes()),
            'authority_effect': 'none', 'replay_source': False}
    except BaseException:
        if db is not None: db.close()
        # This function created this exact path exclusively. Delete only its file.
        path.unlink(missing_ok=True)
        raise
