"""Fresh local technical Session consuming a pinned API30 Project State view."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import stat
import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

ROOT = Path(__file__).resolve().parents[4]
TASK = Path(__file__).resolve().parent
API = 'product/lab/release-candidates/v1/interface/api-integration-v30/source-manifest.json'
LOOKUP = 'authority/project-state-transitions/current.json'
STATE = 'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances/project-state.json'
PINS = {
    API: 'cfd9a932d87c565c22b915234bbf2a18bfed23f163607b95b96f24b2533e3a16',
    LOOKUP: '12937950af2a00ef329deb1a922275250c61ad199b8f6216eab448e06bf49984',
    STATE: 'cccf18d2966cf0dd494f7d88b054243bb635a91bc84fdcbf5c70709b7b6f8793',
}
PROJECT = 'project:cyberalchemy-v2-to-lab-migration'
OLD_LOOKUP_SHA = '8ba8ee25ccbf12721d800c693120a3452ddf1ec4427c6fdf1e0655beae31bc12'
LEASE_SECONDS = 120


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def pretty(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def utc(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat().replace('+00:00', 'Z')


def read_exact(root, name, expected):
    rel = Path(name)
    if rel.is_absolute() or '..' in rel.parts or rel.as_posix() != name:
        raise ValueError('unsafe source path')
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('unsafe source root')
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in rel.parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd); fd = child
        leaf = os.open(rel.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            before = os.fstat(leaf)
            if not stat.S_ISREG(before.st_mode) or before.st_size > 8 * 1024 * 1024:
                raise ValueError('selected source is not bounded regular file')
            with os.fdopen(os.dup(leaf), 'rb') as stream:
                raw = stream.read(8 * 1024 * 1024 + 1)
            after = os.fstat(leaf)
            if (len(raw) != before.st_size or len(raw) > 8 * 1024 * 1024 or
                    (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) !=
                    (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) or
                    sha(raw) != expected):
                raise ValueError('selected source byte differs')
            return raw
        finally:
            os.close(leaf)
    except OSError as error:
        raise ValueError('unsafe selected source attachment') from error
    finally:
        os.close(fd)


def selection(root=ROOT):
    raw = {name: read_exact(root, name, pin) for name, pin in PINS.items()}
    manifest, lookup, state = [json.loads(raw[name]) for name in (API, LOOKUP, STATE)]
    rows = manifest['files']
    if len(rows) != len({row['path'] for row in rows}):
        raise ValueError('API30 manifest duplicate source row')
    indexed = {row['path']: row['sha256'] for row in rows}
    if indexed.get(LOOKUP) != OLD_LOOKUP_SHA or indexed.get(STATE) is not None:
        raise ValueError('API30 historical source-selection premise changed')
    if (lookup['current_project_state'] != {'path': STATE, 'sha256': PINS[STATE]} or
            lookup['identity_ref'] != state['node_id'] or lookup['authority_effect'] != 'none' or
            state['kind'] != 'project-state' or state['payload']['project_ref'] != PROJECT or
            state['lifecycle_state'] != 'active' or state['authority_effect'] != 'none'):
        raise ValueError('current Project State selection differs')
    if lookup['admission_bundle']['path'] != 'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/bundle.json':
        raise ValueError('current lookup producer differs')
    read_exact(root, lookup['admission_bundle']['path'], lookup['admission_bundle']['sha256'])
    return manifest, lookup, state


def bounded_view(selected, opened_at):
    manifest, lookup, state = selected
    payload = state['payload']
    if (set(payload) != {'artifact_refs', 'cursor', 'decision_refs', 'governance_history_ref',
                         'project_ref', 'semantic_history_ref', 'state_digest'} or
            len(payload['artifact_refs']) > 100 or len(payload['decision_refs']) > 40 or
            payload['project_ref'] != PROJECT):
        raise ValueError('selected Project State projection shape differs')
    projected = {'project_ref': payload['project_ref'], 'cursor': payload['cursor'],
                 'state_digest': payload['state_digest'],
                 'decision_refs': payload['decision_refs'],
                 'artifact_refs': payload['artifact_refs'],
                 'governance_history_ref': payload['governance_history_ref'],
                 'semantic_history_ref': payload['semantic_history_ref']}
    if len(compact(projected)) > 16 * 1024:
        raise ValueError('selected Project State projection exceeds bound')
    return {'schema_version': 'lab-T22-local-project-state-view/v2',
            'work': 'Inspect Lab interface API30 against current Project State for R03 episode 0005 rework',
            'project_ref': PROJECT, 'api30_source_sha256': PINS[API],
            'current_lookup': {'path': LOOKUP, 'sha256': PINS[LOOKUP]},
            'current_project_state': {'path': STATE, 'sha256': PINS[STATE],
                                      'node_id': state['node_id'],
                                      'lifecycle_state': state['lifecycle_state'],
                                      'scope_ref': state['scope_ref'],
                                      'owner_ref': state['owner_ref'],
                                      'payload_sha256': sha(compact(projected)),
                                      'payload': projected},
            'api30_declared_lookup_sha256': OLD_LOOKUP_SHA,
            'opened_at': utc(opened_at), 'expires_at': utc(opened_at + LEASE_SECONDS),
            'authority_effect': 'none', 'native_context_delivery': False}


def discrepancies(selected):
    manifest, lookup, state = selected
    return [{'code': 'api30-current-project-state-lookup-stale',
             'candidate': API, 'selected_path': LOOKUP,
             'candidate_sha256': OLD_LOOKUP_SHA, 'observed_sha256': PINS[LOOKUP],
             'implication': 'The frozen API30 source cut cannot represent this current Project State lookup.'},
            {'code': 'api30-current-project-state-body-unselected',
             'candidate': API, 'selected_path': STATE, 'observed_sha256': PINS[STATE],
             'implication': 'The successor Project State body is absent from the frozen API30 source inventory.'}]


def expected_report(selected, view, view_sha):
    payload = view['current_project_state']['payload']
    role_assignments = [ref for ref in payload['artifact_refs']
                        if ref.endswith('/role-assignment.json') or ref.endswith('-role-assignment.json')]
    return {'schema_version': 'lab-T22-local-api30-inspection-report/v2',
            'work_item': 'R03 episode 0005 rework: inspect Lab interface API30',
            'result_kind': 'observed-discrepancies', 'discrepancies': discrepancies(selected),
            'current_project_state_node_id': view['current_project_state']['node_id'],
            'observed_state_projection': {'project_ref': payload['project_ref'],
                                          'cursor': payload['cursor'],
                                          'state_digest': payload['state_digest'],
                                          'decision_count': len(payload['decision_refs']),
                                          'artifact_count': len(payload['artifact_refs']),
                                          'role_assignment_refs': role_assignments,
                                          'payload_sha256': view['current_project_state']['payload_sha256']},
            'view_sha256': view_sha, 'authority_effect': 'none',
            'native_lab_session': False, 'contest_outcome': None, 'lesson_outcome': None}


class FreshSession:
    """Disposable local technical Session; this is not Lab API session.open."""
    def __init__(self, *, clock=time.time, monotonic=time.monotonic, ttl=LEASE_SECONDS):
        if not 1 <= ttl <= LEASE_SECONDS:
            raise ValueError('Session lease out of bounds')
        self.clock, self.monotonic = clock, monotonic
        self.opened = clock(); self.deadline = monotonic() + ttl
        self.ttl = ttl; self.ref = 'session:local-T22-' + secrets.token_hex(16)
        self.nonce = secrets.token_bytes(32)
        self.memory = []; self.closed = False; self.consumed = False
        self.signer = Ed25519PrivateKey.generate()

    def consume(self, view):
        if self.closed or self.consumed or self.monotonic() >= self.deadline or self.clock() >= self.opened + self.ttl:
            raise ValueError('Session not fresh/current or already consumed')
        if view['expires_at'] != utc(self.opened + self.ttl) or view['opened_at'] != utc(self.opened):
            raise ValueError('view not bound to this Session lease')
        raw = compact(view)
        if len(raw) > 65536:
            raise ValueError('bounded view exceeded input budget')
        self.memory.append(bytearray(raw)); self.consumed = True
        return {'view_sha256': sha(raw), 'input_bytes': len(raw),
                'session_ref': self.ref, 'nonce_sha256': sha(self.nonce)}

    def close(self):
        if self.closed or not self.consumed:
            raise ValueError('Session not consumable/closable')
        for row in self.memory: row[:] = b'\x00' * len(row)
        zeroed = all(not any(row) for row in self.memory)
        self.memory.clear(); self.nonce = b'\x00' * len(self.nonce)
        self.closed = True
        return {'closed_at': utc(self.clock()), 'memory_zeroed': zeroed,
                'live_memory_entries': len(self.memory), 'nonce_zeroed': not any(self.nonce)}


def run(root=ROOT):
    selected = selection(root)
    session = FreshSession()
    view = bounded_view(selected, session.opened)
    consumption = session.consume(view)
    report = expected_report(selected, view, consumption['view_sha256'])
    closed = session.close()
    if not (closed['memory_zeroed'] and closed['nonce_zeroed'] and closed['live_memory_entries'] == 0):
        raise ValueError('technical Session did not clear live memory')
    public = session.signer.public_key().public_bytes(encoding=serialization.Encoding.Raw,
                                                     format=serialization.PublicFormat.Raw)
    result = {'schema_version': 'lab-T22-local-api30-episode-inspection/v2',
              'status': 'PASS', 'selected_inputs': PINS, 'project_ref': PROJECT,
              'runner_sha256': sha((TASK / 'episode.py').read_bytes()),
              'test_sha256': sha((TASK / 'test_episode.py').read_bytes()),
              'view': view, 'report': report, 'session': {
                  'session_ref': session.ref, 'opened_at': utc(session.opened),
                  'deadline_at': utc(session.opened + session.ttl),
                  'nonce_sha256': consumption['nonce_sha256'],
                  'consumed_view_sha256': consumption['view_sha256'],
                  'consumed_input_bytes': consumption['input_bytes'], **closed},
              'technical_session_public_key_base64': base64.b64encode(public).decode(),
              'authority_effect': 'none', 'original_t22_complete': False,
              'native_lab_session': False, 'native_contest_complete': False,
              'lesson_reuse_qualified': False}
    result['technical_session_signature_base64'] = base64.b64encode(session.signer.sign(compact(result))).decode()
    return result


def verify(result, root=ROOT):
    if result.get('selected_inputs') != PINS or result.get('status') != 'PASS':
        raise ValueError('selected inspection receipt differs')
    read_exact(TASK, 'episode.py', result['runner_sha256'])
    read_exact(TASK, 'test_episode.py', result['test_sha256'])
    signature = base64.b64decode(result['technical_session_signature_base64'], validate=True)
    body = {k: v for k, v in result.items() if k != 'technical_session_signature_base64'}
    key = base64.b64decode(body['technical_session_public_key_base64'], validate=True)
    Ed25519PublicKey.from_public_bytes(key).verify(signature, compact(body))
    selected = selection(root)
    session = result['session']
    opened = datetime.fromisoformat(session['opened_at'].replace('Z', '+00:00')).timestamp()
    expected_view = bounded_view(selected, opened)
    if (result['view'] != expected_view or result['project_ref'] != PROJECT or
            session['deadline_at'] != expected_view['expires_at'] or
            session['consumed_view_sha256'] != sha(compact(expected_view)) or
            session['consumed_input_bytes'] != len(compact(expected_view)) or
            session['closed_at'] < session['opened_at'] or session['closed_at'] > session['deadline_at'] or
            not session['memory_zeroed'] or not session['nonce_zeroed'] or session['live_memory_entries'] != 0):
        raise ValueError('technical Session consumption/closure differs')
    if (result['report'] != expected_report(selected, expected_view, session['consumed_view_sha256']) or
            result['native_lab_session'] is not False or
            result['original_t22_complete'] is not False or result['native_contest_complete'] is not False or
            result['lesson_reuse_qualified'] is not False or result['authority_effect'] != 'none'):
        raise ValueError('inspection report or claim ceiling differs')
    return True


def cold_receipt(path):
    parent = os.open(TASK, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_size > 1024 * 1024:
                raise ValueError('unsafe bounded receipt')
            with os.fdopen(os.dup(fd), 'rb') as stream:
                raw = stream.read(1024 * 1024 + 1)
            after = os.fstat(fd)
            if len(raw) != before.st_size or len(raw) > 1024 * 1024 or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise ValueError('receipt changed during read')
            return raw
        finally: os.close(fd)
    finally: os.close(parent)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.write == args.verify: raise ValueError('choose --write or --verify')
    path = TASK / 'RUN-0003.json'
    if args.write:
        value = run()
        verify(value)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(pretty(value)); stream.flush(); os.fsync(stream.fileno())
        parent = os.open(TASK, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try: os.fsync(parent)
        finally: os.close(parent)
    else:
        raw = cold_receipt('RUN-0003.json')
        verify(json.loads(raw))
    print('PASS: local technical API30 inspection Session')


if __name__ == '__main__': main()
