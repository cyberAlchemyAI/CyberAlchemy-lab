"""Read-only, bounded snapshots of explicitly named local recovery fixtures.

This process never drives faults or recovery. The driver waits for its response
before proceeding. Each store has a separate snapshot, never a cross-store one.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone

VERSION = 'domainspec.orodi.recovery-observer/v1-candidate'
MAX_ROWS = 10000

def utc():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def strict_json(text):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError('duplicate key: ' + key)
            value[key] = item
        return value
    return json.loads(text, object_pairs_hook=pairs, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))

def exact(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError('closed request shape mismatch')

def authorizer(action, arg1, arg2, database, trigger):
    if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_TRANSACTION):
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_PRAGMA and arg1 in ('user_version', 'journal_mode') and arg2 is None:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY

def capture_store(root, specification):
    exact(specification, ['role', 'path'])
    if specification['role'] not in ('coordination', 'operation') or not isinstance(specification['path'], str):
        raise ValueError('invalid store role/path')
    path = Path(specification['path']).resolve()
    if not path.is_relative_to(root) or path == root:
        raise ValueError('store outside explicit fixture root')
    result = {'role': specification['role'], 'path': str(path), 'capture_started_at_utc': utc(), 'state': 'unavailable'}
    db = None
    started = time.monotonic()
    try:
        # Avoid ro-WAL connection behavior which can create a missing -shm file.
        with path.open('rb') as stream:
            header = stream.read(100)
        if len(header) < 100 or header[:16] != b'SQLite format 3\x00':
            raise ValueError('not a supported SQLite database')
        if header[18:20] != b'\x01\x01':
            raise ValueError('WAL fixture is outside observer profile')
        db = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=0.1)
        db.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 1000000)
        db.execute('PRAGMA query_only=ON')
        db.set_authorizer(authorizer)
        db.set_progress_handler(lambda: int(time.monotonic() - started > 0.5), 1000)
        db.execute('BEGIN')
        definitions = db.execute("SELECT type,name,sql FROM sqlite_master ORDER BY type,name").fetchall()
        tables = {}
        remaining = MAX_ROWS
        bytes_remaining = 2000000
        for kind, name, sql in definitions:
            if kind != 'table' or name.startswith('sqlite_'):
                continue
            quoted = '"' + name.replace('"', '""') + '"'
            cursor = db.execute('SELECT * FROM ' + quoted + ' LIMIT ' + str(remaining + 1))
            rows = []
            for row in cursor:
                if len(rows) >= remaining:
                    raise ValueError('snapshot row budget exceeded')
                bytes_remaining -= len(json.dumps(row, sort_keys=True, allow_nan=False).encode('utf8'))
                if bytes_remaining < 0:
                    raise ValueError('snapshot byte budget exceeded')
                rows.append(row)
            remaining -= len(rows)
            # Stable ordering without requiring rowid or executing database functions.
            encoded = sorted(rows, key=lambda row: json.dumps(row, sort_keys=True, allow_nan=False))
            tables[name] = {'columns': [column[0] for column in cursor.description], 'rows': encoded}
        result.update(state='observed', schema_version=db.execute('PRAGMA user_version').fetchone()[0],
                      journal_mode=db.execute('PRAGMA journal_mode').fetchone()[0],
                      schema_sha256=hashlib.sha256(json.dumps(definitions, separators=(',', ':')).encode()).hexdigest(), tables=tables)
    except (OSError, sqlite3.Error, ValueError, TypeError) as error:
        result.update(state='unavailable', cause=type(error).__name__ + ': ' + str(error))
    finally:
        if db is not None:
            db.close()
        result.update(capture_finished_at_utc=utc(), connection_closed=True)
    return result

def observe(request):
    exact(request, ['schema_version', 'scenario_id', 'repetition', 'test_id', 'subject_digest', 'producer_pid', 'barrier_id', 'sequence', 'clock', 'fixture_root', 'stores'])
    if request['schema_version'] != VERSION or not re.fullmatch(r'R01-F(?:0[1-9]|[12][0-9]|30)', request['scenario_id']):
        raise ValueError('unsupported version or scenario')
    if type(request['repetition']) is not int or request['repetition'] not in (1, 2):
        raise ValueError('invalid repetition')
    if type(request['producer_pid']) is not int or request['producer_pid'] <= 0 or request['producer_pid'] == os.getpid():
        raise ValueError('observer must be separate from producer')
    if request['producer_pid'] != os.getppid():
        raise ValueError('producer must be the invoking parent process')
    if type(request['sequence']) is not int or request['sequence'] < 0:
        raise ValueError('invalid sequence')
    if not re.fullmatch('[0-9a-f]{64}', request['subject_digest']):
        raise ValueError('invalid subject digest')
    for key in ['test_id', 'barrier_id']:
        if not isinstance(request[key], str) or not request[key] or len(request[key]) > 256:
            raise ValueError('invalid label')
    exact(request['clock'], ['kind', 'boot_id', 'monotonic_value'])
    if request['clock']['kind'] not in ('injected', 'not-supplied'):
        raise ValueError('unsupported driver clock kind')
    if request['clock']['kind'] == 'injected':
        if not isinstance(request['clock']['boot_id'], str) or type(request['clock']['monotonic_value']) is not int:
            raise ValueError('invalid injected clock')
    elif request['clock']['boot_id'] is not None or request['clock']['monotonic_value'] is not None:
        raise ValueError('absent clock has no fabricated values')
    stores = request['stores']
    if not isinstance(stores, list) or len(stores) > 2:
        raise ValueError('store budget exceeded')
    if len({s.get('role') for s in stores if isinstance(s, dict)}) != len(stores):
        raise ValueError('duplicate store role')
    root = Path(request['fixture_root']).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('fixture root must be a directory')
    started = utc()
    captures = [capture_store(root, s) for s in stores]
    return {'schema_version': VERSION, 'scenario_id': request['scenario_id'], 'repetition': request['repetition'],
            'test_id': request['test_id'], 'subject_digest': request['subject_digest'],
            'observer_digest': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'producer_pid': request['producer_pid'], 'observer_pid': os.getpid(), 'parent_pid': os.getppid(),
            'barrier_id': request['barrier_id'], 'sequence': request['sequence'], 'driver_clock': request['clock'],
            'capture_started_at_utc': started, 'capture_finished_at_utc': utc(),
            'observer_environment': {'python': sys.version, 'sqlite': sqlite3.sqlite_version},
            'stores': captures, 'all_connections_closed': True, 'cross_store_atomic': False,
            'authority_effect': 'none'}

if __name__ == '__main__':
    try:
        raw = sys.stdin.read(65537)
        if len(raw) > 65536:
            raise ValueError('request too large')
        print(json.dumps(observe(strict_json(raw)), sort_keys=True, allow_nan=False))
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(json.dumps({'schema_version': VERSION, 'state': 'invalid', 'cause': str(error), 'authority_effect': 'none'}))
        sys.exit(2)
