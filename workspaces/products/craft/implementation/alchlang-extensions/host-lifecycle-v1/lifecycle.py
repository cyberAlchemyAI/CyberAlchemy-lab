"""Durable, tenant-bound lifecycle requests; native host adapter prototype."""
import copy
import hashlib
import http.client
import json
import re
import secrets
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path

class LifecycleError(ValueError):
    def __init__(self,code,status=409):
        super().__init__(code);self.code=code;self.status=status

def need(condition,code,status=409):
    if not condition:raise LifecycleError(code,status)

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def sha(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def now():return int(time.time()*1000)

ACTIVE="('queued','running','outcome_unknown')"

def delivery_snapshot(database):
    observed=now()
    try:
        path=Path(database)
        if path.is_symlink() or path.resolve()!=path.absolute():raise ValueError('UNSAFE_STORAGE')
        with sqlite3.connect(path.as_uri()+'?mode=ro',uri=True,timeout=.05) as db:
            deadline=time.monotonic()+.1
            db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
            db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
            counts=dict(db.execute('SELECT status,COUNT(*) FROM outbox GROUP BY status'))
            if not set(counts)<={'pending','leased','published','dead'}:raise ValueError('STORAGE_STATUS_UNKNOWN')
            dead=db.execute('SELECT COUNT(*) FROM dead_letters').fetchone()[0]
            if dead!=counts.get('dead',0):raise ValueError('STORAGE_SUMMARY_INCONSISTENT')
        return {'available':True,'observed_at':observed,'pending':counts.get('pending',0)+counts.get('leased',0),
                'leased':counts.get('leased',0),'published':counts.get('published',0),'dead':dead,'reason':None}
    except (OSError,sqlite3.Error,ValueError) as e:
        code=str(e) if str(e) in ('UNSAFE_STORAGE','STORAGE_STATUS_UNKNOWN','STORAGE_SUMMARY_INCONSISTENT') else 'STORAGE_UNAVAILABLE'
        return {'available':False,'observed_at':observed,'pending':None,'leased':None,'published':None,'dead':None,'reason':code}

class LifecycleMixin:
    def __init__(self,root,config):
        self.lifecycle_worker=None;self.lifecycle_failure=None
        self.function_guards={};self.guards_lock=threading.Lock();self.children_guard=threading.RLock()
        self.runtime_identities={}
        original=copy.deepcopy(config)
        need(original.get('schema')=='alch.host-lifecycle/v1','LIFECYCLE_CONFIG_REQUIRED',400)
        need(isinstance(original.get('users'),list),'CONFIG_INVALID',400)
        for user in original['users']:
            need(isinstance(user,dict) and isinstance(user.get('scopes'),list) and
                 all(isinstance(s,str) for s in user['scopes']) and
                 set(user['scopes'])<={'read','build','activate','invoke','lifecycle'},'CONFIG_INVALID',400)
        adapted=copy.deepcopy(original);adapted['schema']='alch.local-control-plane/v1'
        for user in adapted['users']:user['scopes']=[s for s in user['scopes'] if s!='lifecycle']
        super().__init__(root,adapted)
        for user in original['users']:self.users[user['token_sha256']]['scopes']=user['scopes']
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS lifecycle_modes(
            tenant TEXT,project TEXT,function TEXT,mode TEXT NOT NULL,version INTEGER NOT NULL,
            generation TEXT NOT NULL,PRIMARY KEY(tenant,project,function));
          CREATE TABLE IF NOT EXISTS lifecycle_requests(
            seq INTEGER PRIMARY KEY,tenant TEXT,project TEXT,function TEXT,id TEXT,payload TEXT,
            action TEXT,status TEXT,stage TEXT,revision TEXT,route_epoch INTEGER,version INTEGER,
            target_mode TEXT,reason TEXT,UNIQUE(tenant,project,function,id));
        ''')
        self.db.commit()

    def close(self):
        if hasattr(self,'stopping'):self.stopping.set()
        if self.lifecycle_worker is not None:self.lifecycle_worker.join(timeout=60)
        need(self.lifecycle_worker is None or not self.lifecycle_worker.is_alive(),'LIFECYCLE_SHUTDOWN_PENDING',503)
        super().close()

    @contextmanager
    def function_guard(self,tenant,project,function):
        with self.guards_lock:lock=self.function_guards.setdefault((tenant,project,function),threading.RLock())
        need(lock.acquire(blocking=False),'FUNCTION_CONTROL_BUSY')
        try:yield
        finally:lock.release()

    def mode(self,tenant,project,function):
        row=self.db.execute('SELECT * FROM lifecycle_modes WHERE tenant=? AND project=? AND function=?',(tenant,project,function)).fetchone()
        return dict(row) if row else {'mode':'accepting','version':0,'generation':'none'}

    def active_request(self,tenant,project,function):
        return self.db.execute(f'SELECT * FROM lifecycle_requests WHERE tenant=? AND project=? AND function=? AND status IN {ACTIVE}',(tenant,project,function)).fetchone()

    def selected(self,user,project,function):
        need(isinstance(function,str) and re.fullmatch('[a-z][a-z0-9-]{0,63}',function),'FUNCTION_ID',400)
        row=self.db.execute('SELECT revision FROM routes WHERE tenant=? AND project=? AND function=?',(user['id'],project,function)).fetchone()
        need(row is not None,'NOT_FOUND',404)
        baseline=self.baseline(user,project,function)
        need(baseline is not None,'STATE_BINDING_MISSING')
        return baseline

    def fence(self,baseline,mode):
        return sha({'revision':baseline['revision'],'route_epoch':baseline['route_epoch'],
                    'version':mode['version'],'generation':mode['generation']})

    def probe(self,key):
        with self.children_guard:
            child=self.children.get(key);identity=self.runtime_identities.get(key)
        if child is None:return {'state':'stopped','reason':'HOST_ABSENT','observed_at':now()}
        proc,port,token=child
        if proc.poll() is not None:return {'state':'failed','reason':'HOST_EXITED','observed_at':now()}
        conn=http.client.HTTPConnection('127.0.0.1',port,timeout=.3)
        try:
            conn.request('GET','/health',headers={'Authorization':'Bearer '+token})
            response=conn.getresponse();raw=response.read(8193)
            need(response.status==200 and len(raw)<=8192,'HOST_PROTOCOL')
            value=json.loads(raw)
            need(isinstance(value,dict) and identity is not None and value.get('identity')==identity,'HOST_IDENTITY_MISMATCH')
            return {'state':'live','observed_at':now(),'reason':None,'gate':value['gate'],
                    'event_delivery':value['event_delivery'],'active':value['active'],'identity':identity}
        except Exception:return {'state':'unknown','reason':'HOST_PROBE_UNAVAILABLE','observed_at':now()}
        finally:conn.close()

    def function_status(self,user,project,function):
        self.scope(user,project,'read')
        baseline=self.selected(user,project,function);mode=self.mode(user['id'],project,function)
        host=self.probe(baseline['state_key']);counts=delivery_snapshot(self.database(baseline['state_key']))
        health=host['state']
        if health=='live':
            if host['identity']!={'revision':baseline['revision'],'generation':mode['generation']}:health='unknown'
            elif host['event_delivery']=='blocked':health='failed'
            elif host['gate']=='draining':
                health='drained' if counts['available'] and counts['pending']==0 and counts['dead']==0 and not host['active'] else 'draining'
            elif mode['mode']=='accepting':health='ready'
            else:health='draining'
        # Observation may race a launch. An identity mismatch can never report ready.
        current=self.mode(user['id'],project,function)
        if current['generation']!=mode['generation']:health='starting'
        return {'project':project,'function':function,'revision':baseline['revision'],'route_epoch':baseline['route_epoch'],
                'desired_mode':mode['mode'],'generation':mode['generation'],'version':mode['version'],
                'expected':self.fence(baseline,mode),'health':health,'host':host,'delivery':counts}

    def request_status(self,user,project,function,request_id):
        self.scope(user,project,'read')
        row=self.db.execute('SELECT * FROM lifecycle_requests WHERE tenant=? AND project=? AND function=? AND id=?',(user['id'],project,function,request_id)).fetchone()
        need(row is not None,'NOT_FOUND',404)
        return self.request_view(row)

    @staticmethod
    def request_view(row):
        return {'request_id':row['id'],'action':row['action'],'status':row['status'],'stage':row['stage'],
                'reason':row['reason'],'status_url':f"/v1/projects/{row['project']}/functions/{row['function']}/requests/{row['id']}"}

    def submit_control(self,user,project,function,action,body):
        self.scope(user,project,'lifecycle')
        need(action in ('drain','resume','restart'),'ACTION_INVALID',400)
        need(isinstance(body,dict) and set(body)=={'request_id','expected'} and
             isinstance(body['request_id'],str) and re.fullmatch('[a-zA-Z0-9_-]{1,64}',body['request_id']) and
             isinstance(body['expected'],str) and re.fullmatch('[a-f0-9]{64}',body['expected']),'REQUEST_FIELDS',400)
        baseline=self.selected(user,project,function);payload=canonical({'action':action,**body})
        # Idempotent lookups do not wait for the function effect lock.
        old=self.db.execute('SELECT * FROM lifecycle_requests WHERE tenant=? AND project=? AND function=? AND id=?',(user['id'],project,function,body['request_id'])).fetchone()
        if old:
            need(old['payload']==payload,'REQUEST_ID_CONFLICT');return self.request_view(old)
        with self.function_guard(user['id'],project,function),self.db:
            self.db.execute('BEGIN IMMEDIATE')
            mode=self.mode(user['id'],project,function)
            need(self.active_request(user['id'],project,function) is None,'FUNCTION_CONTROL_BUSY')
            need(body['expected']==self.fence(baseline,mode),'STALE_FENCE')
            need(self.lifecycle_failure is None and not self.stopping.is_set(),'LIFECYCLE_UNAVAILABLE',503)
            count=self.db.execute(f'SELECT COUNT(*) FROM lifecycle_requests WHERE status IN {ACTIVE}').fetchone()[0]
            own=self.db.execute(f'SELECT COUNT(*) FROM lifecycle_requests WHERE tenant=? AND status IN {ACTIVE}',(user['id'],)).fetchone()[0]
            need(count<8 and own<2,'LIFECYCLE_QUEUE_FULL',429)
            target='accepting' if action=='resume' else 'draining' if action=='drain' else mode['mode']
            version=mode['version']+1
            self.db.execute('INSERT INTO lifecycle_modes VALUES(?,?,?,?,?,?) ON CONFLICT(tenant,project,function) DO UPDATE SET mode=excluded.mode,version=excluded.version',
                            (user['id'],project,function,'draining',version,mode['generation']))
            self.db.execute('INSERT INTO lifecycle_requests(tenant,project,function,id,payload,action,status,stage,revision,route_epoch,version,target_mode) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
                            (user['id'],project,function,body['request_id'],payload,action,'queued','accepted',baseline['revision'],baseline['route_epoch'],version,target))
        row=self.db.execute('SELECT * FROM lifecycle_requests WHERE tenant=? AND project=? AND function=? AND id=?',(user['id'],project,function,body['request_id'])).fetchone()
        return self.request_view(row)

    def start_lifecycle_worker(self):
        need(self.lifecycle_worker is None,'WORKER_ALREADY_STARTED')
        self.lifecycle_worker=threading.Thread(target=self.lifecycle_work,name='alch-lifecycle-worker');self.lifecycle_worker.start()

    def lifecycle_work(self):
        self.db=sqlite3.connect(self.root/'registry.sqlite',timeout=5);self.db.row_factory=sqlite3.Row
        try:
            while not self.stopping.wait(.05):
                row=self.db.execute("SELECT * FROM lifecycle_requests WHERE status='queued' ORDER BY seq LIMIT 1").fetchone()
                if row is not None:self.execute_control(row)
        except Exception:self.lifecycle_failure='LIFECYCLE_WORKER_FAILED'
        finally:self.db.close();self.db=None

    def step(self,seq,stage,status='running',reason=None):
        with self.db:self.db.execute('UPDATE lifecycle_requests SET stage=?,status=?,reason=? WHERE seq=?',(stage,status,reason,seq))
        self.failpoint(stage)

    def failpoint(self,stage):
        """Test seam; no environment or HTTP activation."""

    def execute_control(self,request):
        seq=request['seq'];tenant,project,function=request['tenant'],request['project'],request['function']
        try:
            with self.function_guard(tenant,project,function):
                user=next((u for u in self.users.values() if u['id']==tenant),None)
                need(user is not None,'OWNER_UNAVAILABLE',403);self.scope(user,project,'lifecycle')
                baseline=self.selected(user,project,function);mode=self.mode(tenant,project,function)
                need(baseline['revision']==request['revision'] and baseline['route_epoch']==request['route_epoch'] and mode['version']==request['version'],'STALE_FENCE')
                row=self.revision(user,project,baseline['revision']);key=baseline['state_key']
                self.step(seq,'controlling')
                if request['action']=='restart':
                    with self.children_guard:child=self.children.get(key)
                    if child and child[0].poll() is None:
                        self.host_control(key,'drain')
                    self.step(seq,'quiescent')
                    self.stop_host(key);self.step(seq,'stopped')
                self.host(row,user);self.step(seq,'launched')
                if request['action']=='drain' or request['target_mode']=='draining':self.host_control(key,'drain')
                else:
                    health=self.probe(key)
                    need(health['state']=='live' and health.get('event_delivery')!='blocked','HOST_NOT_READY',503)
                    self.host_control(key,'resume')
                self.step(seq,'controlled')
                with self.db:
                    self.db.execute('UPDATE lifecycle_modes SET mode=? WHERE tenant=? AND project=? AND function=?',(request['target_mode'],tenant,project,function))
                    self.db.execute("UPDATE lifecycle_requests SET status='succeeded',stage='completed',reason=NULL WHERE seq=?",(seq,))
                self.failpoint('completed')
        except Exception as error:
            code=getattr(error,'code','CONTROL_FAILED')
            if not isinstance(code,str) or not re.fullmatch('[A-Z_]+',code):code='CONTROL_FAILED'
            # If commit already succeeded, retain its result rather than inventing a failed action.
            saved=self.db.execute('SELECT status FROM lifecycle_requests WHERE seq=?',(seq,)).fetchone()
            if saved and saved[0]=='succeeded':return
            uncertain=code in ('HOST_CONTROL_UNKNOWN','CONTROL_FAILED')
            self.step(seq,'needs-reconciliation' if uncertain else 'blocked','outcome_unknown' if uncertain else 'blocked',code)

    def restore_selected(self):
        # A new controller cannot trust a prior effect's response. Reconcile the same
        # request with the old process gone (parent-death signal + storage owner lock).
        with self.db:self.db.execute("UPDATE lifecycle_requests SET status='queued',stage='reconciling' WHERE status IN ('running','outcome_unknown')")
        for route in self.db.execute('SELECT * FROM routes ORDER BY tenant,project,function').fetchall():
            if self.active_request(route['tenant'],route['project'],route['function']):continue
            user=next((u for u in self.users.values() if u['id']==route['tenant']),None)
            if user is None:continue
            try:self.host(self.revision(user,route['project'],route['revision']),user)
            except Exception:pass  # status exposes failed/absent; other tenants remain observable

    def invoke(self,user,project,function,body):
        self.scope(user,project,'invoke')
        with self.function_guard(user['id'],project,function):
            need(self.mode(user['id'],project,function)['mode']=='accepting','FUNCTION_DRAINING',503)
            need(self.active_request(user['id'],project,function) is None,'FUNCTION_CONTROL_BUSY',503)
            return super().invoke(user,project,function,body)

    def activate(self,user,project,revision):
        self.scope(user,project,'activate');row=self.revision(user,project,revision)
        _,cfg,_=self.runtime(row,user);function=cfg['id']
        with self.function_guard(user['id'],project,function):
            need(self.active_request(user['id'],project,function) is None,'FUNCTION_CONTROL_BUSY')
            need(self.mode(user['id'],project,function)['mode']=='accepting','FUNCTION_DRAINING')
            return super().activate(user,project,revision)
