#!/usr/bin/env python3
"""Durable asynchronous build scheduling over the tested local Alch host."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = Path(__file__).resolve().parent
PREDECESSOR = HERE.parent / 'local-control-plane-v1'
spec = importlib.util.spec_from_file_location('alch_sync_control', PREDECESSOR / 'control_plane.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
require, Rejected, sha, encoded = base.require, base.Rejected, base.sha, base.encoded
GLOBAL_PENDING = 8
TENANT_PENDING = 2


class Plane(base.Plane):
    @property
    def db(self):
        return getattr(self.connections, 'db', None)

    @db.setter
    def db(self, value):
        self.connections.db = value

    def __init__(self, root, config):
        self.connections = threading.local()
        self.stopping = threading.Event()
        self.wakeup = threading.Event()
        self.process_lock = threading.Lock()
        self.active_build = None
        self.worker = None
        self.worker_failure = None
        profile = self.support_binding()
        self.support = profile
        marker = Path(root) / 'async-profile.json'
        require(not (Path(root) / 'registry.sqlite').exists() or marker.is_file(), 'NEW_ASYNC_ROOT_REQUIRED',409)
        if marker.exists():
            require(json.loads(marker.read_bytes()) == profile, 'ASYNC_PROFILE_DRIFT',409)
        super().__init__(root,config)
        try:
            if not marker.exists():
                with marker.open('xb') as stream:
                    stream.write(encoded(profile)); stream.flush(); os.fsync(stream.fileno())
        except Exception:
            self.close()
            raise

    @staticmethod
    def support_binding():
        return {'schema':'alch.async-control-plane/v1',
                'implementation':sha(Path(__file__).read_bytes()),
                'predecessor':sha((PREDECESSOR / 'control_plane.py').read_bytes())}

    def verify_support(self):
        require(self.support_binding() == self.support, 'SUPPORT_DRIFT',409)

    def host(self,row,user):
        self.verify_support()
        return super().host(row,user)

    def start_worker(self):
        require(self.worker is None and not self.stopping.is_set(), 'WORKER_ALREADY_STARTED',409)
        self.worker = threading.Thread(target=self.work, name='alch-build-worker')
        self.worker.start()

    def close(self):
        self.stopping.set()
        self.wakeup.set()
        with self.process_lock:
            if self.active_build is not None and self.active_build.poll() is None:
                try: os.killpg(self.active_build.pid, signal.SIGKILL)
                except ProcessLookupError: pass
        if self.worker is not None:
            self.worker.join()
        super().close()

    def build(self, user, project, source):
        """Durably accept a revision; compilation happens on the worker connection."""
        self.scope(user,project,'build')
        require(not self.stopping.is_set() and self.worker_failure is None, 'BUILD_WORKER_UNAVAILABLE',503)
        require(isinstance(source,str) and len(source.encode()) <= 131072, 'SOURCE_INVALID')
        revision = secrets.token_hex(16)
        dest = self.root / 'revisions' / revision
        try:
            with self.db:
                self.db.execute('BEGIN IMMEDIATE')
                require(self.db.execute('SELECT 1 FROM projects WHERE tenant=? AND project=?',(user['id'],project)).fetchone(), 'NOT_FOUND',404)
                pending = self.db.execute("SELECT COUNT(*) FROM revisions WHERE status IN ('queued','building')").fetchone()[0]
                own = self.db.execute("SELECT COUNT(*) FROM revisions WHERE tenant=? AND status IN ('queued','building')",(user['id'],)).fetchone()[0]
                require(pending < GLOBAL_PENDING and own < TENANT_PENDING, 'BUILD_QUEUE_FULL',429)
                dest.mkdir(mode=0o700)
                with (dest / 'source.alch').open('xb') as stream:
                    stream.write(source.encode()); stream.flush(); os.fsync(stream.fileno())
                for directory in (dest,dest.parent):
                    fd=os.open(directory,os.O_DIRECTORY)
                    try: os.fsync(fd)
                    finally: os.close(fd)
                self.db.execute('INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?)',(user['id'],project,revision,sha(source.encode()),'queued',None,None,None))
                self.event(user['id'],project,revision,'build-queued')
        except Exception:
            if dest.exists(): shutil.rmtree(dest)
            raise
        self.wakeup.set()
        return {'revision':revision,'status':'queued','source_sha256':sha(source.encode()),
                'status_url':f'/v1/projects/{project}/revisions/{revision}'}

    def claim(self):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row=self.db.execute("""SELECT r.* FROM revisions r WHERE status='queued'
                ORDER BY COALESCE((SELECT MAX(j.seq) FROM journal j
                    WHERE j.tenant=r.tenant AND j.stage='build-started'),0),r.rowid LIMIT 1""").fetchone()
            if row is None: return None
            self.db.execute("UPDATE revisions SET status='building' WHERE tenant=? AND project=? AND id=? AND status='queued'",(row['tenant'],row['project'],row['id']))
            self.event(row['tenant'],row['project'],row['id'],'build-started')
            return row

    def work(self):
        try:
            self.db=sqlite3.connect(self.root / 'registry.sqlite',timeout=5)
            self.db.row_factory=sqlite3.Row
            self.db.execute('PRAGMA foreign_keys=ON')
            while not self.stopping.is_set():
                self.wakeup.clear()
                row=self.claim()
                if row is None:
                    self.wakeup.wait(.2)
                    continue
                self.execute_build(row)
        except Exception:
            # A storage/control failure stops scheduling. Startup reconciles any
            # in-flight row; never fabricate a completed build or route.
            self.worker_failure='BUILD_WORKER_UNAVAILABLE'
        finally:
            if self.db is not None: self.db.close()
            self.db=None

    def execute_build(self,row):
        tenant,project,revision=row['tenant'],row['project'],row['id']
        dest=self.root / 'revisions' / revision
        try:
            self.verify_support()
            require(not self.stopping.is_set(), 'BUILD_INTERRUPTED',422)
            user=next((u for u in self.users.values() if u['id']==tenant),None)
            require(user is not None,'BUILD_PERMISSION_REVOKED',403)
            self.scope(user,project,'build')
            require(base.compiler_binding()==self.binding,'COMPILER_DRIFT',409)
            source=(dest / 'source.alch').read_bytes()
            require(sha(source)==row['source'],'SOURCE_DRIFT',409)
            with tempfile.TemporaryDirectory(prefix='alch-async-build-') as work:
                job=Path(work)
                (job / 'source.alch').write_bytes(source)
                with (dest / 'build.log').open('wb') as log:
                    with self.process_lock:
                        require(not self.stopping.is_set(),'BUILD_INTERRUPTED',422)
                        proc=subprocess.Popen([sys.executable,str(PREDECESSOR / 'control_plane.py'),'--build-launch',*base.build_command(job)],
                                              stdout=log,stderr=subprocess.STDOUT,env={'PATH':'/usr/bin:/bin'},start_new_session=True)
                        self.active_build=proc
                    try:
                        try: code=proc.wait(timeout=180)
                        except subprocess.TimeoutExpired:
                            os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                            raise Rejected('BUILD_TIMEOUT',422)
                    finally:
                        with self.process_lock: self.active_build=None
                    require(not self.stopping.is_set(),'BUILD_INTERRUPTED',422)
                    require(code==0,'BUILD_FAILED',422)
                self.verify_support()
                require(base.compiler_binding()==self.binding,'COMPILER_DRIFT',409)
                bundle=job / 'bundle'
                cfg=json.loads((bundle / 'host.json').read_bytes())
                base.policy_check(cfg,user['policy'])
                require(cfg['source_sha256']==row['source'] and sha((dest/'source.alch').read_bytes())==row['source'],'SOURCE_DRIFT',409)
                files=base.inventory(bundle)
                shutil.copytree(bundle,dest / 'bundle')
                artifact=sha(encoded(files))
                (dest / 'artifact.json').write_bytes(encoded(files))
            with self.db:
                self.db.execute("UPDATE revisions SET status='ready',artifact=?,function=? WHERE tenant=? AND project=? AND id=?",(artifact,cfg['id'],tenant,project,revision))
                self.event(tenant,project,revision,'build-ready')
        except Exception as error:
            code=error.code if isinstance(error,Rejected) else 'BUILD_FAILED'
            with self.db:
                self.db.execute("UPDATE revisions SET status='failed',error=? WHERE tenant=? AND project=? AND id=?",(code,tenant,project,revision))
                self.event(tenant,project,revision,'build-failed')

    def status(self,user,project,revision):
        self.scope(user,project,'read')
        row=self.revision(user,project,revision)
        result={k:row[k] for k in ('id','status','source','artifact','function','error')}
        result['scheduler']='unavailable' if self.worker_failure else 'running'
        return result


def serve(plane,port=0):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_): pass
        def setup(self):
            super().setup();self.connection.settimeout(5)
        def handle_request(self):
            try:
                auth=self.headers.get_all('Authorization',[])
                require(len(auth)==1 and auth[0].startswith('Bearer ') and not self.headers.get('Origin'),'UNAUTHORIZED',401)
                user=plane.auth(auth[0][7:]);body=None
                if self.command=='POST':
                    lengths=self.headers.get_all('Content-Length',[])
                    require(not self.headers.get('Transfer-Encoding') and len(lengths)==1 and re.fullmatch('[0-9]{1,7}',lengths[0]),'CONTENT_LENGTH_REQUIRED')
                    size=int(lengths[0]);require(size<=262144,'REQUEST_TOO_LARGE',413)
                    require(self.headers.get('Content-Type','').split(';')[0]=='application/json','JSON_REQUIRED',415)
                    raw=self.rfile.read(size);require(len(raw)==size,'INCOMPLETE_BODY')
                    body=json.loads(raw);require(isinstance(body,dict),'REQUEST_FIELDS')
                parts=self.path.split('/')
                require(len(parts)>=4 and parts[:3]==['','v1','projects'] and re.fullmatch(base.SLUG,parts[3]),'NOT_FOUND',404)
                project=parts[3];status=200
                if len(parts)==4 and self.command=='POST':
                    require(body=={},'REQUEST_FIELDS');value=plane.project(user,project)
                elif len(parts)==4 and self.command=='GET':value=plane.inspect(user,project)
                elif len(parts)==5 and parts[4]=='revisions' and self.command=='POST':
                    require(set(body)=={'source'},'REQUEST_FIELDS');value=plane.build(user,project,body['source']);status=202
                elif len(parts)==6 and parts[4]=='revisions' and re.fullmatch('[a-f0-9]{32}',parts[5]) and self.command=='GET':
                    value=plane.status(user,project,parts[5])
                elif len(parts)==7 and parts[4]=='revisions' and re.fullmatch('[a-f0-9]{32}',parts[5]) and parts[6]=='activate' and self.command=='POST':
                    require(body=={},'REQUEST_FIELDS');value=plane.activate(user,project,parts[5])
                elif len(parts)==7 and parts[4]=='functions' and re.fullmatch(base.SLUG,parts[5]) and parts[6]=='invoke' and self.command=='POST':
                    status,value=plane.invoke(user,project,parts[5],body)
                else:raise Rejected('NOT_FOUND',404)
            except Rejected as e:status,value=e.status,{'error':e.code}
            except (ValueError,UnicodeError):status,value=400,{'error':'INVALID_JSON'}
            except TimeoutError:status,value=408,{'error':'BODY_TIMEOUT'}
            except Exception:status,value=500,{'error':'CONTROL_PLANE_FAILURE'}
            data=encoded(value);self.send_response(status)
            self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)))
            self.send_header('Connection','close');self.send_header('Cache-Control','no-store');self.end_headers()
            self.close_connection=True
            try:self.wfile.write(data)
            except OSError:pass
        do_GET=handle_request
        do_POST=handle_request
    return HTTPServer(('127.0.0.1',port),Handler)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',required=True);parser.add_argument('--config',required=True)
    parser.add_argument('--port',type=int,default=0)
    args=parser.parse_args();require(0<=args.port<=65535,'PORT_INVALID');os.umask(0o077)
    plane=Plane(args.root,json.loads(Path(args.config).read_bytes()));server=None
    try:
        server=serve(plane,args.port);plane.start_worker()
        def stop(*_):threading.Thread(target=server.shutdown,daemon=True).start()
        signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
        print(json.dumps({'status':'listening','url':f'http://127.0.0.1:{server.server_port}'}),flush=True)
        server.serve_forever(poll_interval=.1)
    finally:
        if server:server.server_close()
        plane.close()


if __name__=='__main__':main()
