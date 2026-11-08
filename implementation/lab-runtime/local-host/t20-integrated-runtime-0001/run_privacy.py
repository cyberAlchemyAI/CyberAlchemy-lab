"""Actual selected-runtime Session privacy; no fake clock or Service replacement.

Trusted CLI selects immutable API/hash/deps, not a public protocol field. The
original inherited fixture constructs real Source, Reader, Service and resource.
This is fixture qualification and never permission to read real protected data.
"""
import argparse
import base64
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[4]


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def run(api, source_sha, profile_sha, deps):
    need(sys.dont_write_bytecode, 'no-bytecode runtime required')
    api = Path(api).absolute()
    need(api.parent == ROOT / 'product/lab/release-candidates/v1/interface'
         and not api.is_symlink(), 'selected API caller fixture required')
    sys.path.insert(0, str(Path(deps).absolute()))
    sys.path.insert(0, str(api.parent))
    G = importlib.import_module(api.name + '.guard')
    manifest = G.verify(source_sha)
    need(manifest['profile_binding']['sha256'] == profile_sha, 'selected profile differs')
    M = importlib.import_module(api.name + '.test_custody_sessions')
    C = importlib.import_module(api.name + '.current_legacy_context_sessions')
    need(Path(M.__file__).resolve() == api / 'test_custody_sessions.py'
         and Path(C.__file__).resolve() == api / 'current_legacy_context_sessions.py', 'selected fixture origin differs')
    sentinel = ('private-runtime-privacy-' + uuid.uuid4().hex).encode()
    forbidden = (sentinel, base64.b64encode(sentinel), sentinel.hex().encode())
    checked = {'wire_replies': 0, 'durable_files': 0, 'captured_stream_bytes': 0}
    def scan(raw):
        need(type(raw) is bytes and not any(value in raw for value in forbidden),
             'private fixture sentinel reached a retained public surface')
    streams = io.StringIO(), io.StringIO()
    row = None
    with redirect_stdout(streams[0]), redirect_stderr(streams[1]):
        M.PROFILE = profile_sha
        case = None
        try:
            M.Sessions.setUpClass()
            case = M.Sessions('test_01_actual_private_memory_erased')
            M.Sessions.events = []
            case.setUp()
            opened, _ = case.opening_success()
            resource = case.service.sessions.live[opened['session_ref']]
            resource.note(sentinel)
            held = resource.memory[-1]
            need(bytes(held) == sentinel, 'actual private note was not held in RAM')
            # A successful metadata read and an actual refused caller input both
            # cross Service.call. Neither can serialize the separate note buffer.
            case.success(case.inspection(opened['session_ref']))
            wrong = case.inspection(opened['session_ref'])
            wrong['message']['actor']['principal_ref'] = 'principal:privacy-foreign'
            refused = case.invoke(wrong)
            need(refused.get('kind') == 'error', 'foreign metadata Actor was accepted')
            malformed = case.service.call(b'{not-json')
            scan(M.compact(malformed))
            checked['wire_replies'] += 1
            # Private typed memory must also fail the actual Vault write boundary.
            before = {p.name for p in (case.service.vault.root / 'objects').iterdir()}
            try:
                case.service.vault.object(M.compact({'session_memory': sentinel.decode()}))
            except ValueError:
                pass
            else:
                raise ValueError('private typed Session material entered the Vault')
            need(before == {p.name for p in (case.service.vault.root / 'objects').iterdir()},
                 'refused private Vault write left a completed object')
            case.success(case.closing(opened))
            need(resource.closed and resource.memory == [] and not any(held)
                 and opened['session_ref'] not in case.service.sessions.live,
                 'actual close did not erase held note bytes and resource')
            # Fresh custodian reads original closed metadata without live RAM.
            case.service.sessions.close()
            fresh = C.ContextSessions(case.view, case.channel, case.schemas, case.service.vault)
            case.service.sessions = fresh
            need(not fresh.live, 'restart reconstructed a live Session')
            restarted = case.success(case.inspection(opened['session_ref']))
            need(restarted['posture'] == 'closed' and not fresh.live,
                 'restart failed closed metadata read or revived the resource')
            for event in M.Sessions.events:
                scan(M.compact(event['reply']))
                checked['wire_replies'] += 1
            for folder in ('journal', 'objects'):
                for path in sorted((case.service.vault.root / folder).rglob('*')):
                    if path.is_file():
                        scan(path.read_bytes())
                        checked['durable_files'] += 1
            row = {'result': 'PASS-actual-Session-private-memory-boundaries',
                   'api_directory': str(api.relative_to(ROOT)), 'source_sha256': source_sha,
                   'profile_sha256': profile_sha, 'held_note_zeroed': True,
                   'fresh_custodian_live_resources': 0, 'private_vault_write_refused': True,
                   'source_fixture_only': True, 'actual_owner_outcome': None, 'authority_effect': 'none',
                   'claim_ceiling': 'Actual fixture Session success/refusal, Vault, closed metadata restart and named byte/base64/hex leak checks. Other Machine/workflow/export routes and final package privacy require their own selected evidence.'}
        finally:
            try:
                if case is not None and hasattr(case, 'service'):
                    case.tearDown()
            finally:
                if case is not None:
                    case.doCleanups()
                M.Sessions.doClassCleanups()
    for stream in streams:
        raw = stream.getvalue().encode()
        scan(raw)
        checked['captured_stream_bytes'] += len(raw)
    G.verify(source_sha)
    row['checked'] = checked
    return row


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--api', required=True)
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--profile-sha256', required=True)
    parser.add_argument('--deps', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        result = run(args.api, args.source_sha256, args.profile_sha256, args.deps)
        raw = (json.dumps(result, indent=2, sort_keys=True) + '\n').encode()
        fd = os.open(args.output, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception as error:
        # Never print exception values or hostile response bodies to public logs.
        print(json.dumps({'result': 'FAIL-selected-runtime-privacy', 'exception': type(error).__name__}))
        raise SystemExit(1)
    print(json.dumps({'result': result['result'], 'checked': result['checked']}, sort_keys=True))
