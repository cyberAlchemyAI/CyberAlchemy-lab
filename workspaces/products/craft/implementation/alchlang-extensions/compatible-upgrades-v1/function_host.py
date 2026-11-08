#!/usr/bin/env python3
"""Function-owned state host with a private, bounded drain protocol."""
import argparse
import fcntl
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import threading
import time
import tempfile
import sys
import sqlite3
from compatibility import fingerprint
local_worker = None

BUNDLE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    manifest = json.loads((BUNDLE / 'host-manifest.json').read_bytes())
    for name, expected in manifest['files'].items():
        path = BUNDLE / name
        if path.is_symlink() or path.resolve() != path.absolute() or not path.resolve().is_relative_to(BUNDLE) or digest(path) != expected:
            raise ValueError('BUNDLE_DRIFT')
    cfg = json.loads((BUNDLE / 'host.json').read_bytes())
    provisioner = Path(cfg['provisioner_root'])
    if digest(provisioner / 'host.py') != cfg['provisioner_host_sha256'] or digest(provisioner / 'source-manifest.json') != cfg['provisioner_manifest_sha256']:
        raise ValueError('PROVISIONER_DRIFT')
    return cfg, provisioner


def run(root_value, port, contract, state_key, crash_after_consume=False):
    cfg, provisioner = verify()
    if cfg["isolation"] != "bubblewrap" or fingerprint(BUNDLE) != contract:
        raise ValueError("COMPATIBILITY_MISMATCH")
    token = os.environ.get('ALCH_HOST_TOKEN', '')
    if not re.fullmatch(r'[A-Za-z0-9_-]{32,256}', token):
        raise ValueError('HOST_TOKEN_REQUIRED')
    policy = json.loads(os.environ.get('ALCH_HOST_POLICY', '{}'))
    if (policy.get('actor') not in cfg['actors'] or not isinstance(policy.get('grants'), list)
            or cfg['boundary'] not in policy['grants'] or policy.get('operations') != [cfg['operation']]):
        raise ValueError('HOST_POLICY_DENIED')
    context = {'actor': policy['actor'], 'grants': [cfg['boundary']], 'transport_grants': []}
    consumer_context = None
    if cfg['events'] == 'local':
        cp = policy.get('consumer', {})
        if (not isinstance(cp, dict) or not isinstance(cp.get('grants'), list)
                or not isinstance(policy.get('transport_grants'), list)
                or cp.get('actor') not in cfg['consumer']['actors'] or cp.get('operation') != cfg['consumer']['operation']
                or cfg['consumer']['boundary'] not in cp.get('grants', [])
                or cfg['transport'] not in policy.get('transport_grants', [])):
            raise ValueError('EVENT_POLICY_DENIED')
        consumer_context = {'actor':cp['actor'],'grants':[cfg['consumer']['boundary']], 'transport_grants':[]}
    if cfg['isolation'] == 'bubblewrap':
        if policy.get('isolation') != 'bubblewrap':
            raise ValueError('ISOLATION_POLICY_DENIED')
        try:
            with tempfile.TemporaryDirectory(prefix='alch-isolation-probe-') as temp:
                result = subprocess.run(local_worker.sandbox_command('/usr/bin/true', temp),
                                        env={'PATH':'/usr/bin:/bin'},capture_output=True,timeout=5)
                if result.returncode:
                    raise ValueError('ISOLATION_UNAVAILABLE')
        except (OSError, subprocess.TimeoutExpired):
            raise ValueError('ISOLATION_UNAVAILABLE')
    spec = importlib.util.spec_from_file_location('alch_provisioner', provisioner / 'host.py')
    host = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(host)
    if host.run(root_value)['status'] != 'Succeeded':
        raise ValueError('PROVISIONING_FAILED')
    root = host.open_root(root_value)
    with (root / 'owner.lock').open('rb') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if not host.configured(root, host.load(provisioner / 'domainspec.json')):
            raise ValueError('PROVISIONED_CONFIGURATION_DRIFT')
        binding = root / 'target/state/function-binding.json'
        identity = {'contract':contract, 'state_key':state_key, 'id':cfg['id']}
        if binding.exists():
            if json.loads(binding.read_bytes()) != identity:
                raise ValueError('FUNCTION_REVISION_CONFLICT')
        else:
            with binding.open('x') as stream:
                json.dump(identity, stream)
                stream.flush()
                os.fsync(stream.fileno())
        data = root / 'target/state/runtime' if cfg['isolation'] == 'bubblewrap' else root / 'target/state'
        data.mkdir(mode=0o700, exist_ok=True)
        database = data / 'function.sqlite'
        slot = threading.BoundedSemaphore(1)
        stopping = threading.Event()
        paused = threading.Event()
        delivery = {'state':'disabled' if consumer_context is None else 'running'}
        def call(request, caller):
            host.safe_tree(root)
            verify()
            return local_worker.invoke(BUNDLE,cfg,database,request,caller)

        # A real isolated inspect initializes/checks the storage protocol before readiness.
        code, _ = call({'command':'inspect'}, {'transport_grants':[cfg['transport']]})
        if code:
            raise ValueError('RUNTIME_NOT_READY')

        def drain():
            paused.set()
            deadline=time.monotonic()+35
            while time.monotonic()<deadline and not stopping.is_set():
                if slot.acquire(timeout=.1):
                    try:
                        with sqlite3.connect(database.as_uri()+'?mode=ro',uri=True) as db:
                            counts=dict(db.execute('SELECT status,COUNT(*) FROM outbox GROUP BY status'))
                        if counts.get('dead',0) or delivery['state']=='blocked':
                            return 409, {'error':'DRAIN_BLOCKED'}
                        if sum(count for status,count in counts.items() if status!='published')==0:
                            return 200, {'status':'drained'}
                    finally:
                        slot.release()
                time.sleep(.05)
            return 409, {'error':'DRAIN_TIMEOUT'}

        def deliver():
            while not stopping.wait(.2):
                if not slot.acquire(blocking=False):
                    continue
                try:
                    delivery['state'] = local_worker.dispatch_once(call,cfg,consumer_context,'local-delivery',crash_after_consume)
                except Exception:
                    delivery['state'] = 'blocked'
                    return
                finally:
                    slot.release()

        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'

            def log_message(self, *_args):
                pass

            def setup(self):
                super().setup()
                self.connection.settimeout(5)

            def respond(self, status, value):
                data = json.dumps(value).encode()
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Connection', 'close')
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.close_connection = True
                self.wfile.write(data)

            def authorized(self):
                supplied = self.headers.get_all('Authorization', [])
                return (not self.headers.get('Origin') and len(supplied) == 1
                        and hmac.compare_digest(supplied[0].encode(), ('Bearer ' + token).encode()))

            def do_GET(self):
                if not self.authorized():
                    return self.respond(401, {'error': 'UNAUTHORIZED'})
                if self.path != '/health':
                    return self.respond(404, {'error': 'NOT_FOUND'})
                self.respond(200, {'status': 'listening', 'scope': 'trusted-local-prototype', 'function': cfg['id'],
                                  'isolation':cfg['isolation'],'event_delivery':delivery['state']})

            def do_POST(self):
                if not self.authorized():
                    return self.respond(401, {'error': 'UNAUTHORIZED'})
                if self.path in ('/_host/drain','/_host/resume'):
                    if self.headers.get('Transfer-Encoding') or self.headers.get_all('Content-Length',[]) != ['0']:
                        return self.respond(400, {'error':'EMPTY_BODY_REQUIRED'})
                    if self.path == '/_host/resume':
                        paused.clear()
                        return self.respond(200, {'status':'resumed'})
                    status,value=drain()
                    return self.respond(status,value)
                if self.path != cfg['endpoint']:
                    return self.respond(404, {'error': 'NOT_FOUND'})
                lengths = self.headers.get_all('Content-Length', [])
                if self.headers.get('Transfer-Encoding') or len(lengths) != 1 or not re.fullmatch('[0-9]+', lengths[0]):
                    return self.respond(400, {'error': 'CONTENT_LENGTH_REQUIRED'})
                size = int(lengths[0])
                if size > cfg['max_request_bytes']:
                    return self.respond(413, {'error': 'REQUEST_TOO_LARGE'})
                if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                    return self.respond(415, {'error': 'JSON_REQUIRED'})
                if not slot.acquire(blocking=False):
                    return self.respond(503, {'error': 'FUNCTION_BUSY'})
                try:
                    if paused.is_set():
                        return self.respond(503, {'error':'FUNCTION_DRAINING'})
                    raw = self.rfile.read(size)
                    if len(raw) != size:
                        return self.respond(400, {'error': 'INCOMPLETE_BODY'})
                    body = json.loads(raw)
                    if not isinstance(body, dict) or set(body) != {'facts', 'expected_version'}:
                        return self.respond(400, {'error': 'REQUEST_FIELDS'})
                    try:
                        code, value = call({'command':'invoke','operation':cfg['operation'],**body},context)
                    except TimeoutError:
                        return self.respond(504, {'error':'OUTCOME_UNKNOWN','retry':'same-message-id-only'})
                    if code:
                        return self.respond(422, {'error':'FUNCTION_REJECTED'})
                    return self.respond(200,value)
                except (ValueError, UnicodeError):
                    self.respond(400, {'error': 'INVALID_REQUEST_OR_BINDING'})
                except TimeoutError:
                    self.respond(408, {'error': 'BODY_TIMEOUT'})
                except Exception:
                    self.respond(500, {'error': 'HOST_FAILURE'})
                finally:
                    slot.release()

        server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
        server.daemon_threads = False
        def stop(*_args):
            stopping.set()
            threading.Thread(target=server.shutdown, daemon=True).start()
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        print(json.dumps({'status': 'listening', 'url': f'http://127.0.0.1:{server.server_port}',
                          'endpoint': cfg['endpoint'], 'function': cfg['id']}), flush=True)
        worker = threading.Thread(target=deliver) if consumer_context is not None else None
        if worker:
            worker.start()
        try:
            server.serve_forever(poll_interval=.1)
        finally:
            stopping.set()
            if worker:
                worker.join()
            server.server_close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-root', required=True)
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--contract', required=True)
    parser.add_argument('--state-key', required=True)
    parser.add_argument('--port', type=int, default=0)
    parser.add_argument('--test-crash-after-consume', action='store_true')
    args = parser.parse_args()
    try:
        if not 0 <= args.port <= 65535:
            raise ValueError('PORT_INVALID')
        if not re.fullmatch('[a-f0-9]{64}',args.contract) or not re.fullmatch('[a-f0-9]{64}',args.state_key):
            raise ValueError('STATE_BINDING_INVALID')
        BUNDLE=Path(args.bundle).resolve()
        verify()
        spec=importlib.util.spec_from_file_location('upgrade_worker',BUNDLE/'local_worker.py')
        local_worker=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(local_worker)
        run(args.run_root, args.port, args.contract, args.state_key, args.test_crash_after_consume)
    except Exception as error:
        code = str(error)
        print(json.dumps({'status': 'blocked', 'error': code if re.fullmatch('[A-Z_]+', code) else 'LOCAL_HOST_START_FAILED'}), flush=True)
        raise SystemExit(1)
