#!/usr/bin/env python3
"""Private loopback control-plane candidate. See README.md for its claim ceiling."""
import argparse
import ctypes
import fcntl
import hashlib
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import re
import resource
import secrets
import selectors
import signal
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time

HERE = Path(__file__).resolve().parent
BASE = HERE.parent.parent
REPO = BASE.parents[5]
IMPL = BASE / 'implementation'
DS = REPO / 'projects/domainspec-v2/impl/cli'
PROV = REPO / 'cyberAlchemy-v2/work-orchestration-implementation/extensions/alch-host-provisioning-v1'
NODE = Path('/home/vrondelli/.nvm/versions/node/v26.8.1/bin/node')
RUST = Path('/home/vrondelli/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu')
REGISTRY = Path('/home/vrondelli/.cargo/registry')
OUTBOX = BASE / 'extensions/generatable-operation-patterns-v1/bindings/sqlite-transactional-outbox.binding-set.json'
SLUG = r'[a-z][a-z0-9-]{0,63}'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


class Rejected(Exception):
    def __init__(self, code, status=400):
        self.code, self.status = code, status


def require(condition, code, status=400):
    if not condition:
        raise Rejected(code, status)


def inventory(root):
    result = {}
    for p in sorted(root.rglob('*')):
        require(not p.is_symlink(), 'SYMLINK_DENIED')
        if p.is_file():
            result[str(p.relative_to(root))] = sha(p.read_bytes())
    return result


def compiler_binding():
    return {'alch': inventory(IMPL / 'dist'), 'domainspec': inventory(DS / 'dist'),
            'outbox_binding': sha(OUTBOX.read_bytes()),
            'alch_package': sha((IMPL / 'package.json').read_bytes()),
            'domainspec_package': sha((DS / 'package.json').read_bytes()),
            'node': sha(NODE.read_bytes()), 'cargo': sha((RUST / 'bin/cargo').read_bytes()),
            'rustc': sha((RUST / 'bin/rustc').read_bytes()),
            'provisioner_host': sha((PROV / 'host.py').read_bytes()),
            'provisioner_manifest': sha((PROV / 'source-manifest.json').read_bytes())}


def build_command(job):
    # Only compiler inputs are mounted, never the repository root or tenant store.
    mounts = [OUTBOX, IMPL / 'dist', IMPL / 'package.json', DS / 'dist', DS / 'package.json',
              REPO / 'cyberAlchemy-v2/agent-routing/profile.json', PROV / 'host.py', PROV / 'source-manifest.json']
    args = ['/usr/bin/bwrap', '--unshare-all', '--die-with-parent', '--new-session',
            '--ro-bind', '/usr', '/usr', '--ro-bind', '/usr/bin', '/bin', '--ro-bind', '/lib', '/lib', '--ro-bind', '/lib64', '/lib64',
            '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp']
    for p in mounts:
        args += ['--ro-bind', str(p), str(p)]
    args += ['--ro-bind', str(NODE), '/tool/node', '--ro-bind', str(RUST), '/tool/rust',
             '--dir', '/cargo', '--ro-bind', str(REGISTRY), '/cargo/registry',
             '--bind', str(job), '/job', '--chdir', '/job', '--clearenv',
             '--setenv', 'PATH', '/tool/rust/bin:/usr/bin:/bin', '--setenv', 'CARGO_HOME', '/cargo',
             '--setenv', 'HOME', '/tmp', '--setenv', 'CARGO_BUILD_JOBS', '2', '--setenv', 'CC', '/usr/bin/gcc',
             '--setenv', 'RUSTFLAGS', '-C linker=/usr/bin/gcc',
             '--', '/tool/node', '--max-old-space-size=512', str(IMPL / 'dist/cli.js'),
             'build', '/job/source.alch', '--out', '/job/bundle']
    return args


def policy_check(cfg, policy):
    require(cfg['isolation'] == 'bubblewrap', 'ISOLATION_REQUIRED', 422)
    require(policy.get('isolation') == 'bubblewrap' and policy.get('actor') in cfg['actors']
            and isinstance(policy.get('grants'), list) and cfg['boundary'] in policy['grants']
            and policy.get('operations') == [cfg['operation']], 'POLICY_DENIED', 403)
    if cfg['events'] == 'local':
        cp = policy.get('consumer', {})
        require(isinstance(cp, dict) and isinstance(cp.get('grants'), list)
                and cp.get('actor') in cfg['consumer']['actors'] and cp.get('operation') == cfg['consumer']['operation']
                and cfg['consumer']['boundary'] in cp['grants'] and isinstance(policy.get('transport_grants'), list)
                and cfg['transport'] in policy['transport_grants'], 'POLICY_DENIED', 403)


class Plane:
    def __init__(self, root, config):
        self.root = Path(root).absolute()
        require(self.root.resolve() == self.root and not self.root.is_symlink(), 'ROOT_UNSAFE')
        self.root.mkdir(mode=0o700, parents=False, exist_ok=True)
        require(self.root.stat().st_uid == os.getuid() and self.root.stat().st_mode & 0o777 == 0o700, 'ROOT_UNSAFE')
        require(not any(p.is_symlink() for p in self.root.rglob('*')), 'ROOT_UNSAFE')
        self.lock = (self.root / 'owner.lock').open('a+b')
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.lock.close()
            raise Rejected('CONTROL_PLANE_BUSY', 409)
        self.children = {}
        self.db = None
        try:
            require(config.get('schema') == 'alch.local-control-plane/v1' and isinstance(config.get('users'), list), 'CONFIG_INVALID')
            self.users = {}
            identities = set()
            for user in config['users']:
                require(isinstance(user, dict) and re.fullmatch(SLUG, user.get('id', ''))
                        and re.fullmatch('[a-f0-9]{64}', user.get('token_sha256', ''))
                        and isinstance(user.get('scopes'), list) and set(user['scopes']) <= {'read','build','activate','invoke'}
                        and isinstance(user.get('projects'), list) and all(p == '*' or re.fullmatch(SLUG, p) for p in user['projects'])
                        and isinstance(user.get('policy'), dict), 'CONFIG_INVALID')
                require(user['token_sha256'] not in self.users and user['id'] not in identities, 'DUPLICATE_IDENTITY')
                identities.add(user['id'])
                self.users[user['token_sha256']] = user
            self.binding = compiler_binding()
            binding_file = self.root / 'compiler-binding.json'
            if binding_file.exists():
                require(json.loads(binding_file.read_bytes()) == self.binding, 'COMPILER_DRIFT', 409)
            else:
                binding_file.write_bytes(encoded(self.binding))
            self.db = sqlite3.connect(self.root / 'registry.sqlite')
            self.db.row_factory = sqlite3.Row
            self.db.executescript('''
                PRAGMA journal_mode=WAL;
                PRAGMA foreign_keys=ON;
                CREATE TABLE IF NOT EXISTS projects(tenant TEXT, project TEXT, PRIMARY KEY(tenant,project));
                CREATE TABLE IF NOT EXISTS revisions(tenant TEXT, project TEXT, id TEXT, source TEXT, status TEXT,
                    artifact TEXT, function TEXT, error TEXT, PRIMARY KEY(tenant,project,id),
                    FOREIGN KEY(tenant,project) REFERENCES projects(tenant,project));
                CREATE TABLE IF NOT EXISTS routes(tenant TEXT, project TEXT, function TEXT, revision TEXT,
                    PRIMARY KEY(tenant,project,function), FOREIGN KEY(tenant,project,revision) REFERENCES revisions(tenant,project,id));
                CREATE TABLE IF NOT EXISTS journal(seq INTEGER PRIMARY KEY, tenant TEXT, project TEXT, revision TEXT, stage TEXT);
            ''')
            with self.db:
                interrupted = self.db.execute("SELECT tenant,project,id FROM revisions WHERE status='building'").fetchall()
                for row in interrupted:
                    self.db.execute("UPDATE revisions SET status='failed',error='BUILD_INTERRUPTED' WHERE tenant=? AND project=? AND id=?", tuple(row))
                    self.event(*row, 'build-interrupted')
            (self.root / 'revisions').mkdir(mode=0o700, exist_ok=True)
        except Exception:
            self.close()
            raise

    def close(self):
        for proc, _, _ in self.children.values():
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
            if proc.stdout:
                proc.stdout.close()
        self.children.clear()
        if self.db is not None:
            self.db.close()
        self.lock.close()

    def auth(self, token):
        require(isinstance(token, str) and re.fullmatch(r'[A-Za-z0-9_-]{32,256}', token), 'UNAUTHORIZED', 401)
        user = self.users.get(sha(token.encode()))
        require(user is not None, 'UNAUTHORIZED', 401)
        return user

    def scope(self, user, project, action):
        require(re.fullmatch(SLUG, project) is not None, 'PATH_INVALID')
        require(action in user['scopes'] and ('*' in user['projects'] or project in user['projects']), 'FORBIDDEN', 403)

    def event(self, tenant, project, revision, stage):
        self.db.execute('INSERT INTO journal(tenant,project,revision,stage) VALUES(?,?,?,?)', (tenant, project, revision, stage))

    def project(self, user, name):
        self.scope(user, name, 'build')
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO projects VALUES(?,?)', (user['id'], name))
        return {'project': name}

    def revision(self, user, project, revision):
        row = self.db.execute('SELECT * FROM revisions WHERE tenant=? AND project=? AND id=?', (user['id'], project, revision)).fetchone()
        require(row is not None, 'NOT_FOUND', 404)
        return row

    def build(self, user, project, source):
        self.scope(user, project, 'build')
        require(self.db.execute('SELECT 1 FROM projects WHERE tenant=? AND project=?', (user['id'], project)).fetchone(), 'NOT_FOUND', 404)
        require(isinstance(source, str) and len(source.encode()) <= 131072, 'SOURCE_INVALID')
        require(compiler_binding() == self.binding, 'COMPILER_DRIFT', 409)
        revision = secrets.token_hex(16)
        dest = self.root / 'revisions' / revision
        dest.mkdir(mode=0o700)
        (dest / 'source.alch').write_text(source)
        with self.db:
            self.db.execute('INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?)', (user['id'], project, revision, sha(source.encode()), 'building', None, None, None))
            self.event(user['id'], project, revision, 'build-requested')
        try:
            with tempfile.TemporaryDirectory(prefix='alch-build-') as work:
                job = Path(work)
                (job / 'source.alch').write_text(source)
                with (dest / 'build.log').open('wb') as log:
                    proc = subprocess.Popen([sys.executable, str(HERE / 'control_plane.py'), '--build-launch', *build_command(job)],
                                            stdout=log, stderr=subprocess.STDOUT, env={'PATH':'/usr/bin:/bin'}, start_new_session=True)
                    try:
                        code = proc.wait(timeout=180)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, signal.SIGKILL)
                        proc.wait()
                        raise Rejected('BUILD_TIMEOUT', 422)
                require(code == 0, 'BUILD_FAILED', 422)
                require(compiler_binding() == self.binding, 'COMPILER_DRIFT', 409)
                bundle = job / 'bundle'
                cfg = json.loads((bundle / 'host.json').read_bytes())
                policy_check(cfg, user['policy'])
                require(cfg['source_sha256'] == sha(source.encode()), 'SOURCE_DRIFT', 409)
                files = inventory(bundle)
                import shutil
                shutil.copytree(bundle, dest / 'bundle')
                artifact = sha(encoded(files))
                (dest / 'artifact.json').write_bytes(encoded(files))
            with self.db:
                self.db.execute("UPDATE revisions SET status='ready',artifact=?,function=? WHERE tenant=? AND project=? AND id=?", (artifact,cfg['id'],user['id'],project,revision))
                self.event(user['id'],project,revision,'build-ready')
            return {'revision':revision,'status':'ready','source_sha256':sha(source.encode()),'artifact_sha256':artifact,'function':cfg['id']}
        except Exception as error:
            code = error.code if isinstance(error, Rejected) else 'BUILD_FAILED'
            with self.db:
                self.db.execute("UPDATE revisions SET status='failed',error=? WHERE tenant=? AND project=? AND id=?", (code,user['id'],project,revision))
                self.event(user['id'],project,revision,'build-failed')
            raise Rejected(code, 422)

    def verify(self, row, user):
        require(row['status'] == 'ready', 'REVISION_NOT_READY', 409)
        dest = self.root / 'revisions' / row['id']
        require(not dest.is_symlink() and dest.resolve().is_relative_to(self.root), 'ARTIFACT_DRIFT', 409)
        files = inventory(dest / 'bundle')
        require(sha(encoded(files)) == row['artifact'] and sha((dest / 'source.alch').read_bytes()) == row['source'], 'ARTIFACT_DRIFT', 409)
        cfg = json.loads((dest / 'bundle/host.json').read_bytes())
        policy_check(cfg, user['policy'])
        return dest / 'bundle', cfg

    def host(self, row, user):
        bundle, cfg = self.verify(row, user)
        key = row['id']
        if key in self.children:
            proc, port, token = self.children[key]
            if proc.poll() is None:
                return port, token, cfg
            if proc.stdout:
                proc.stdout.close()
            del self.children[key]
        require(len(self.children) < 8, 'HOST_CAPACITY', 503)
        # PROV owns and checks its /tmp root contract. Opaque identity prevents user path selection.
        run_root = '/tmp/alch-provision-cp-' + sha(str(self.root).encode())[:16] + '-' + key
        token = secrets.token_urlsafe(32)
        proc = subprocess.Popen([sys.executable, str(HERE / 'control_plane.py'), '--host-launch', str(bundle / 'serve.py'), '--run-root', run_root],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, start_new_session=True,
                                env={'PATH':'/usr/bin:/bin','PYTHONDONTWRITEBYTECODE':'1','ALCH_HOST_TOKEN':token,'ALCH_HOST_POLICY':json.dumps(user['policy'])})
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(proc.stdout, selectors.EVENT_READ)
                require(bool(selector.select(30)), 'HOST_TIMEOUT', 503)
                ready = json.loads(proc.stdout.readline())
            require(ready.get('status') == 'listening', 'HOST_START_FAILED', 503)
            port = int(ready['url'].rsplit(':',1)[1])
            self.children[key] = (proc, port, token)
            return port, token, cfg
        except Exception:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
            if proc.stdout:
                proc.stdout.close()
            raise Rejected('HOST_START_FAILED',503)

    def activate(self, user, project, revision):
        self.scope(user, project, 'activate')
        row = self.revision(user, project, revision)
        self.host(row, user)
        with self.db:
            self.db.execute('INSERT INTO routes VALUES(?,?,?,?) ON CONFLICT(tenant,project,function) DO UPDATE SET revision=excluded.revision', (user['id'],project,row['function'],revision))
            self.event(user['id'],project,revision,'route-selected')
        return {'function':row['function'],'revision':revision}

    def invoke(self, user, project, function, body):
        self.scope(user, project, 'invoke')
        require(isinstance(body, dict) and set(body) == {'facts','expected_version'}, 'REQUEST_FIELDS')
        route = self.db.execute('SELECT revision FROM routes WHERE tenant=? AND project=? AND function=?', (user['id'],project,function)).fetchone()
        require(route is not None, 'NOT_FOUND',404)
        row = self.revision(user,project,route['revision'])
        port, token, cfg = self.host(row,user)
        data = encoded(body)
        require(len(data) <= cfg['max_request_bytes'], 'REQUEST_TOO_LARGE',413)
        conn = http.client.HTTPConnection('127.0.0.1',port,timeout=cfg['timeout_ms']/1000+2)
        try:
            conn.request('POST',cfg['endpoint'],data,{'Authorization':'Bearer '+token,'Content-Type':'application/json'})
            response = conn.getresponse()
            return response.status, json.loads(response.read())
        except (TimeoutError, OSError, http.client.HTTPException):
            return 504, {'error':'OUTCOME_UNKNOWN','retry':'same-message-id-only'}
        finally:
            conn.close()

    def inspect(self,user,project):
        self.scope(user,project,'read')
        require(self.db.execute('SELECT 1 FROM projects WHERE tenant=? AND project=?',(user['id'],project)).fetchone(), 'NOT_FOUND',404)
        return {'revisions':[dict(r) for r in self.db.execute('SELECT id,status,source,artifact,function,error FROM revisions WHERE tenant=? AND project=?',(user['id'],project))],
                'routes':[dict(r) for r in self.db.execute('SELECT function,revision FROM routes WHERE tenant=? AND project=?',(user['id'],project))]}


def serve(plane, port=0):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_): pass
        def setup(self):
            super().setup()
            self.connection.settimeout(5)
        def handle_request(self):
            try:
                auth = self.headers.get_all('Authorization',[])
                require(len(auth)==1 and auth[0].startswith('Bearer ') and not self.headers.get('Origin'), 'UNAUTHORIZED',401)
                user = plane.auth(auth[0][7:])
                body = None
                if self.command == 'POST':
                    lengths = self.headers.get_all('Content-Length',[])
                    require(not self.headers.get('Transfer-Encoding') and len(lengths)==1 and re.fullmatch('[0-9]{1,7}',lengths[0]), 'CONTENT_LENGTH_REQUIRED')
                    size = int(lengths[0])
                    require(size <= 262144, 'REQUEST_TOO_LARGE',413)
                    require(self.headers.get('Content-Type','').split(';')[0]=='application/json', 'JSON_REQUIRED',415)
                    raw = self.rfile.read(size)
                    require(len(raw)==size,'INCOMPLETE_BODY')
                    body=json.loads(raw)
                    require(isinstance(body,dict),'REQUEST_FIELDS')
                parts=self.path.split('/')
                require(len(parts)>=4 and parts[:3]==['','v1','projects'] and re.fullmatch(SLUG,parts[3]),'NOT_FOUND',404)
                project=parts[3]
                status=200
                if len(parts)==4 and self.command=='POST':
                    require(body=={},'REQUEST_FIELDS')
                    value=plane.project(user,project)
                elif len(parts)==4 and self.command=='GET': value=plane.inspect(user,project)
                elif len(parts)==5 and parts[4]=='revisions' and self.command=='POST':
                    require(set(body)=={'source'},'REQUEST_FIELDS')
                    value=plane.build(user,project,body['source']); status=201
                elif len(parts)==7 and parts[4]=='revisions' and re.fullmatch('[a-f0-9]{32}',parts[5]) and parts[6]=='activate' and self.command=='POST':
                    require(body=={},'REQUEST_FIELDS')
                    value=plane.activate(user,project,parts[5])
                elif len(parts)==7 and parts[4]=='functions' and re.fullmatch(SLUG,parts[5]) and parts[6]=='invoke' and self.command=='POST':
                    status,value=plane.invoke(user,project,parts[5],body)
                else: raise Rejected('NOT_FOUND',404)
            except Rejected as e: status,value=e.status,{'error':e.code}
            except (ValueError,UnicodeError): status,value=400,{'error':'INVALID_JSON'}
            except TimeoutError: status,value=408,{'error':'BODY_TIMEOUT'}
            except Exception: status,value=500,{'error':'CONTROL_PLANE_FAILURE'}
            data=encoded(value)
            self.send_response(status)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Connection','close')
            self.send_header('Cache-Control','no-store')
            self.end_headers()
            self.close_connection=True
            try: self.wfile.write(data)
            except OSError: pass
        do_GET=handle_request
        do_POST=handle_request
    # Serialized requests bound admission concurrency and make activation/invoke ordering explicit.
    return HTTPServer(('127.0.0.1',port),Handler)


def main():
    if len(sys.argv)>1 and sys.argv[1] in ('--build-launch','--host-launch'):
        parent=os.getppid()
        require(ctypes.CDLL(None).prctl(1,signal.SIGTERM,0,0,0)==0,'PARENT_BINDING_FAILED')
        if os.getppid()!=parent: raise SystemExit(1)
        if sys.argv[1]=='--build-launch':
            resource.setrlimit(resource.RLIMIT_CPU,(120,120))
            resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3))
            resource.setrlimit(resource.RLIMIT_FSIZE,(256*1024**2,256*1024**2))
            resource.setrlimit(resource.RLIMIT_NOFILE,(256,256))
            os.execv(sys.argv[2],sys.argv[2:])
        os.execv(sys.executable,[sys.executable,*sys.argv[2:]])
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',required=True)
    parser.add_argument('--config',required=True)
    parser.add_argument('--port',type=int,default=0)
    args=parser.parse_args()
    require(0<=args.port<=65535,'PORT_INVALID')
    os.umask(0o077)
    plane=Plane(args.root,json.loads(Path(args.config).read_bytes()))
    server=None
    try:
        server=serve(plane,args.port)
        def stop(*_): threading.Thread(target=server.shutdown,daemon=True).start()
        signal.signal(signal.SIGTERM,stop)
        signal.signal(signal.SIGINT,stop)
        print(json.dumps({'status':'listening','url':f'http://127.0.0.1:{server.server_port}'}),flush=True)
        server.serve_forever(poll_interval=.1)
    finally:
        if server: server.server_close()
        plane.close()


if __name__=='__main__':
    main()
